"""Service 层 LLM provider adapter 测试，见模板第 1-6 章。"""

from __future__ import annotations

import json

import httpx
import pytest

from fund_agent.config.llm import LLMProviderConfig
from fund_agent.fund.chapter_auditor import ChapterAuditLLMRequest
from fund_agent.fund.chapter_writer import ChapterLLMRequest
from fund_agent.services.llm_provider import (
    LLMProviderMalformedResponseError,
    LLMProviderRateLimitError,
    LLMProviderRuntimeError,
    OpenAICompatibleChapterLLMClient,
    build_chapter_llm_clients,
)


def test_build_chapter_llm_clients_returns_same_adapter_for_writer_and_auditor() -> None:
    """验证 Service factory 返回 Gate 3 所需 writer/auditor clients。"""

    clients = build_chapter_llm_clients(_config())

    assert isinstance(clients.writer, OpenAICompatibleChapterLLMClient)
    assert clients.writer is clients.auditor


def test_generate_chapter_sends_authorization_and_maps_response() -> None:
    """验证 writer 请求 header/body 与 `ChapterLLMResponse` 映射。"""

    records: list[httpx.Request] = []
    client = _provider_client(records=records)

    response = client.generate_chapter(_writer_request())

    assert response.text == "writer markdown"
    assert response.model_name == "unit-response-model"
    assert response.finish_reason == "stop"
    assert len(records) == 1
    request = records[0]
    assert str(request.url) == "https://llm.example.com/v1/chat/completions"
    assert request.headers["Authorization"] == "Bearer test-secret"
    body = _json_body(request)
    assert body == {
        "model": "unit-model",
        "messages": [
            {"role": "system", "content": "writer system"},
            {"role": "user", "content": "writer user"},
        ],
    }


def test_audit_chapter_uses_existing_user_prompt_protocol_and_maps_raw_text() -> None:
    """验证 auditor 透传既有 user_prompt 协议并映射 raw_text。"""

    records: list[httpx.Request] = []
    client = _provider_client(records=records, text="PASS|chapter|ok")

    response = client.audit_chapter(_audit_request())

    assert response.raw_text == "PASS|chapter|ok"
    assert response.model_name == "unit-response-model"
    assert response.finish_reason == "stop"
    body = _json_body(records[0])
    user_message = body["messages"][1]["content"]
    assert user_message.startswith("按 SEVERITY|LOCATION|MESSAGE 返回。")
    assert "draft markdown" in user_message
    assert "fact-1" in user_message
    assert "anchor-1" in user_message
    assert user_message.count("SEVERITY|LOCATION|MESSAGE") == 1


def test_rate_limit_maps_to_typed_error_without_secret_prompt_or_body() -> None:
    """验证 429 映射为 typed rate-limit error 且错误文本安全。"""

    client = _provider_client(status_code=429, response_text="full error body with writer user")

    with pytest.raises(LLMProviderRateLimitError) as exc_info:
        client.generate_chapter(_writer_request())

    message = str(exc_info.value)
    assert "status_code=429" in message
    assert "request_id=req-123" in message
    assert "test-secret" not in message
    assert "writer user" not in message
    assert "full error body" not in message


@pytest.mark.parametrize("status_code", (400, 500, 503))
def test_http_error_maps_to_runtime_error_without_full_body(status_code: int) -> None:
    """验证非 2xx HTTP 状态映射为 runtime error 且不包含响应正文。"""

    client = _provider_client(status_code=status_code, response_text="provider body")

    with pytest.raises(LLMProviderRuntimeError) as exc_info:
        client.generate_chapter(_writer_request())

    message = str(exc_info.value)
    assert f"status_code={status_code}" in message
    assert "provider body" not in message
    assert "test-secret" not in message


def test_network_error_maps_to_runtime_error_without_prompt_or_key() -> None:
    """验证网络错误映射为 runtime error 且不泄漏 prompt/key。"""

    def handler(request: httpx.Request) -> httpx.Response:
        """固定抛出 transport error。"""

        raise httpx.TransportError("network down with writer user and test-secret", request=request)

    client = OpenAICompatibleChapterLLMClient(
        config=_config(),
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    with pytest.raises(LLMProviderRuntimeError) as exc_info:
        client.generate_chapter(_writer_request())

    message = str(exc_info.value)
    assert "network error" in message
    assert "writer user" not in message
    assert "test-secret" not in message


def test_timeout_maps_to_runtime_error_without_prompt_or_key() -> None:
    """验证 timeout 映射为 runtime error 且不泄漏 prompt/key。"""

    def handler(request: httpx.Request) -> httpx.Response:
        """固定抛出 timeout。"""

        raise httpx.TimeoutException("timeout with writer user and test-secret", request=request)

    client = OpenAICompatibleChapterLLMClient(
        config=_config(),
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    with pytest.raises(LLMProviderRuntimeError) as exc_info:
        client.generate_chapter(_writer_request())

    message = str(exc_info.value)
    assert "timed out" in message
    assert "writer user" not in message
    assert "test-secret" not in message


@pytest.mark.parametrize(
    "payload",
    (
        {},
        {"choices": []},
        {"choices": [None]},
        {"choices": [{"message": None}]},
        {"choices": [{"message": {"content": None}}]},
        {"choices": [{"message": {"content": 123}}]},
    ),
)
def test_malformed_response_maps_to_typed_error(payload: dict[str, object]) -> None:
    """验证 malformed provider response 映射为 typed malformed error。"""

    client = _provider_client(payload=payload)

    with pytest.raises(LLMProviderMalformedResponseError) as exc_info:
        client.generate_chapter(_writer_request())

    message = str(exc_info.value)
    assert "LLM provider" in message
    assert "test-secret" not in message
    assert "writer user" not in message


def _provider_client(
    *,
    records: list[httpx.Request] | None = None,
    text: str = "writer markdown",
    status_code: int = 200,
    response_text: str | None = None,
    payload: dict[str, object] | None = None,
) -> OpenAICompatibleChapterLLMClient:
    """构造使用 MockTransport 的 provider client。

    Args:
        records: 可选请求记录列表。
        text: 默认响应文本。
        status_code: HTTP 状态码。
        response_text: 非 JSON 响应正文。
        payload: 自定义 JSON payload。

    Returns:
        测试用 provider client。

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
        response_payload = (
            payload
            if payload is not None
            else {
                "model": "unit-response-model",
                "choices": [
                    {
                        "message": {"content": text},
                        "finish_reason": "stop",
                    }
                ],
            }
        )
        return httpx.Response(
            status_code,
            json=response_payload,
            headers={"x-request-id": "req-123"},
            request=request,
        )

    return OpenAICompatibleChapterLLMClient(
        config=_config(),
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )


def _config() -> LLMProviderConfig:
    """构造测试用 provider config。

    Args:
        无。

    Returns:
        fake provider config。

    Raises:
        无显式抛出。
    """

    return LLMProviderConfig(
        provider_name="openai_compatible",
        model="unit-model",
        base_url="https://llm.example.com/v1",
        api_key_env_var="UNIT_TEST_KEY",
        api_key="test-secret",
        timeout_seconds=10,
        max_output_chars=12000,
    )


def _writer_request() -> ChapterLLMRequest:
    """构造 writer request fixture。"""

    return ChapterLLMRequest(
        chapter_id=1,
        fund_code="000001",
        report_year=2024,
        system_prompt="writer system",
        user_prompt="writer user",
        required_anchor_ids=("anchor-1",),
        forbidden_phrases=("建议买入",),
        max_output_chars=12000,
    )


def _audit_request() -> ChapterAuditLLMRequest:
    """构造 auditor request fixture。"""

    return ChapterAuditLLMRequest(
        chapter_id=1,
        fund_code="000001",
        report_year=2024,
        system_prompt="audit system",
        user_prompt="按 SEVERITY|LOCATION|MESSAGE 返回。",
        draft_markdown="draft markdown",
        allowed_fact_ids=("fact-1",),
        allowed_anchor_ids=("anchor-1",),
        audit_focus=("evidence_support",),
    )


def _json_body(request: httpx.Request) -> dict[str, object]:
    """读取 MockTransport 记录的 JSON body。"""

    return json.loads(request.content.decode("utf-8"))
