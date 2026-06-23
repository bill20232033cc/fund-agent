"""Service 层 Evidence Confirm semantic provider adapter 测试。"""

from __future__ import annotations

import json

import httpx
import pytest

from fund_agent.config.llm import LLMProviderConfig
from fund_agent.fund.evidence_confirm_semantic import (
    EvidenceEntailmentRequest,
    EvidenceSemanticClaim,
)
from fund_agent.services.evidence_confirm_semantic_provider import (
    EvidenceSemanticProviderError,
    OpenAICompatibleEvidenceEntailmentClient,
    build_evidence_entailment_client,
)


def test_build_evidence_entailment_client_returns_openai_compatible_adapter() -> None:
    """验证 factory 返回 OpenAI-compatible semantic adapter。"""

    client = build_evidence_entailment_client(_config())

    assert isinstance(client, OpenAICompatibleEvidenceEntailmentClient)


def test_judge_sends_authorization_and_maps_entailed_response() -> None:
    """验证 provider 请求与 entailed 响应映射。"""

    records: list[httpx.Request] = []
    client = _semantic_client(records=records, provider_content={"status": "entailed"})

    judgment = client.judge(_request())

    assert judgment.status == "entailed"
    assert judgment.reason_code == "entailed_by_excerpt"
    assert judgment.message == "provider semantic status: entailed"
    assert len(records) == 1
    request = records[0]
    assert str(request.url) == "https://llm.example.com/v1/chat/completions"
    assert request.headers["Authorization"] == "Bearer test-secret"
    body = _json_body(request)
    assert body["model"] == "unit-model"
    messages = body["messages"]
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
    assert "claim: 换手率披露为 120%。" in messages[1]["content"]
    assert "年报披露换手率为 120%。" in messages[1]["content"]


@pytest.mark.parametrize(
    ("status", "reason_code"),
    (
        ("entailed", "entailed_by_excerpt"),
        ("contradicted", "contradicted_by_excerpt"),
        ("insufficient", "insufficient_excerpt_support"),
        ("not_applicable", "not_applicable"),
    ),
)
def test_judge_maps_closed_status_reason_pairs(status: str, reason_code: str) -> None:
    """验证 provider closed status/reason pair 映射。"""

    client = _semantic_client(
        provider_content={"status": status, "reason_code": reason_code},
    )

    judgment = client.judge(_request())

    assert judgment.status == status
    assert judgment.reason_code == reason_code


def test_malformed_provider_content_fails_closed_without_excerpt_or_key() -> None:
    """验证畸形 provider content fail-closed 且不泄漏 claim/excerpt/key。"""

    client = _semantic_client(provider_text="not json with 年报披露换手率为 120%。 test-secret")

    with pytest.raises(EvidenceSemanticProviderError) as exc_info:
        client.judge(_request())

    message = str(exc_info.value)
    assert "semantic provider content must be JSON" in message
    assert "年报披露" not in message
    assert "test-secret" not in message


def test_http_error_fails_closed_without_body_prompt_or_key() -> None:
    """验证 HTTP error fail-closed 且不泄漏 body/prompt/key。"""

    client = _semantic_client(
        status_code=500,
        response_text="provider body has 换手率披露为 120%。 and test-secret",
    )

    with pytest.raises(EvidenceSemanticProviderError) as exc_info:
        client.judge(_request())

    message = str(exc_info.value)
    assert "status_code=500" in message
    assert "request_id=req-123" in message
    assert "provider body" not in message
    assert "换手率披露" not in message
    assert "test-secret" not in message


def test_transport_error_fails_closed_without_prompt_or_key() -> None:
    """验证 transport error fail-closed 且不泄漏底层异常文本。"""

    def handler(request: httpx.Request) -> httpx.Response:
        """固定抛出 transport error。"""

        raise httpx.TransportError("network down with 换手率披露 and test-secret", request=request)

    client = OpenAICompatibleEvidenceEntailmentClient(
        config=_config(),
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    with pytest.raises(EvidenceSemanticProviderError) as exc_info:
        client.judge(_request())

    message = str(exc_info.value)
    assert message == "semantic provider network error"
    assert "换手率披露" not in message
    assert "test-secret" not in message


def test_invalid_status_reason_pair_fails_closed() -> None:
    """验证 provider status/reason 自相矛盾时 fail-closed。"""

    client = _semantic_client(
        provider_content={"status": "entailed", "reason_code": "contradicted_by_excerpt"},
    )

    with pytest.raises(EvidenceSemanticProviderError, match="reason_code is invalid"):
        client.judge(_request())


def _semantic_client(
    *,
    records: list[httpx.Request] | None = None,
    provider_content: dict[str, str] | None = None,
    provider_text: str | None = None,
    status_code: int = 200,
    response_text: str | None = None,
) -> OpenAICompatibleEvidenceEntailmentClient:
    """构造测试用 semantic provider client。

    Args:
        records: 请求记录列表。
        provider_content: provider message content JSON object。
        provider_text: provider message content 原始字符串。
        status_code: HTTP status code。
        response_text: 非 JSON HTTP body。

    Returns:
        semantic provider client。

    Raises:
        无显式抛出。
    """

    def handler(request: httpx.Request) -> httpx.Response:
        """记录请求并返回 fake provider response。"""

        if records is not None:
            records.append(request)
        if response_text is not None:
            return httpx.Response(
                status_code,
                text=response_text,
                headers={"x-request-id": "req-123"},
                request=request,
            )
        content = provider_text
        if content is None:
            content = json.dumps(provider_content or {"status": "entailed"})
        payload = {
            "model": "unit-response-model",
            "choices": [{"message": {"content": content}, "finish_reason": "stop"}],
        }
        return httpx.Response(
            status_code,
            json=payload,
            headers={"x-request-id": "req-123"},
            request=request,
        )

    return OpenAICompatibleEvidenceEntailmentClient(
        config=_config(),
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )


def _config() -> LLMProviderConfig:
    """构造测试用 provider config。"""

    return LLMProviderConfig(
        provider_name="openai_compatible",
        model="unit-model",
        base_url="https://llm.example.com/v1",
        api_key_env_var="UNIT_TEST_KEY",
        api_key="test-secret",
        timeout_seconds=10,
        writer_timeout_seconds=10,
        auditor_timeout_seconds=10,
        repair_timeout_seconds=10,
        timeout_max_attempts=1,
        timeout_backoff_seconds=0,
        max_output_chars=12000,
    )


def _request() -> EvidenceEntailmentRequest:
    """构造 semantic entailment request fixture。"""

    return EvidenceEntailmentRequest(
        claim=EvidenceSemanticClaim(
            claim_id="claim-1",
            fact_id="fact-1",
            source_field_id="structured.turnover_rate",
            claim_text="换手率披露为 120%。",
            anchor_ids=("anchor-1",),
        ),
        excerpt_texts=("年报披露换手率为 120%。",),
    )


def _json_body(request: httpx.Request) -> dict[str, object]:
    """读取 MockTransport 记录的 JSON body。"""

    return json.loads(request.content.decode("utf-8"))
