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
    LLMProviderNetworkError,
    LLMProviderRateLimitError,
    LLMProviderRuntimeError,
    LLMProviderTimeoutError,
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


def test_network_error_maps_to_typed_error_without_prompt_or_key() -> None:
    """验证网络错误映射为 typed error 且不泄漏 prompt/key。"""

    def handler(request: httpx.Request) -> httpx.Response:
        """固定抛出 transport error。"""

        raise httpx.TransportError("network down with writer user and test-secret", request=request)

    client = OpenAICompatibleChapterLLMClient(
        config=_config(),
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    with pytest.raises(LLMProviderNetworkError) as exc_info:
        client.generate_chapter(_writer_request())

    message = str(exc_info.value)
    assert "network error" in message
    assert "writer user" not in message
    assert "test-secret" not in message


def test_timeout_maps_to_typed_error_without_prompt_or_key() -> None:
    """验证 timeout 映射为 typed error 且不泄漏 prompt/key。"""

    def handler(request: httpx.Request) -> httpx.Response:
        """固定抛出 timeout。"""

        raise httpx.TimeoutException("timeout with writer user and test-secret", request=request)

    client = OpenAICompatibleChapterLLMClient(
        config=_config(),
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    with pytest.raises(LLMProviderTimeoutError) as exc_info:
        client.generate_chapter(_writer_request())

    message = str(exc_info.value)
    assert "timed out" in message
    assert "writer user" not in message
    assert "test-secret" not in message


def test_timeout_only_retry_succeeds_on_later_attempt() -> None:
    """验证 timeout-only retry 在后续 attempt 成功时返回响应。"""

    records: list[httpx.Request] = []
    sleeps: list[float] = []

    def handler(request: httpx.Request) -> httpx.Response:
        """前两次 timeout，第三次返回合法响应。"""

        records.append(request)
        if len(records) < 3:
            raise httpx.TimeoutException("timeout with writer user and test-secret", request=request)
        return httpx.Response(
            200,
            json={
                "model": "unit-response-model",
                "choices": [{"message": {"content": "writer markdown"}, "finish_reason": "stop"}],
            },
            request=request,
        )

    client = OpenAICompatibleChapterLLMClient(
        config=_config(timeout_max_attempts=3, timeout_backoff_seconds=0.25),
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
        sleep=sleeps.append,
    )

    response = client.generate_chapter(_writer_request())

    assert response.text == "writer markdown"
    assert len(records) == 3
    assert sleeps == [0.25, 0.25]


def test_timeout_retry_exhausted_carries_provider_diagnostics() -> None:
    """验证 timeout 耗尽后异常携带 provider-local 安全诊断。"""

    records: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        """每次固定 timeout。"""

        records.append(request)
        raise httpx.TimeoutException("timeout with writer user and test-secret", request=request)

    client = OpenAICompatibleChapterLLMClient(
        config=_config(timeout_max_attempts=3, timeout_backoff_seconds=0),
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
        sleep=lambda _: None,
    )

    with pytest.raises(LLMProviderTimeoutError) as exc_info:
        client.generate_chapter(_writer_request())

    assert len(records) == 3
    diagnostics = exc_info.value.diagnostics
    assert len(diagnostics) == 3
    assert tuple(item.provider_attempt_index for item in diagnostics) == (1, 2, 3)
    assert all(item.provider_max_attempts == 3 for item in diagnostics)
    assert all(item.provider_runtime_category == "timeout" for item in diagnostics)
    assert all(item.chapter_id is None for item in diagnostics)
    assert all(item.fund_code is None for item in diagnostics)
    assert all(item.report_year is None for item in diagnostics)
    assert all(item.repair_attempt_index is None for item in diagnostics)
    assert all(item.chapter_failure_category is None for item in diagnostics)
    assert all(item.system_prompt_chars == len("writer system") for item in diagnostics)
    assert all(item.user_prompt_chars == len("writer user") for item in diagnostics)
    assert all(
        item.approx_prompt_tokens == _ceil_div4(len("writer system") + len("writer user"))
        for item in diagnostics
    )
    assert all(item.allowed_fact_count is None for item in diagnostics)
    assert all(item.allowed_anchor_count == 1 for item in diagnostics)
    assert all(item.max_output_chars == 12000 for item in diagnostics)
    assert all(item.timeout_seconds == 10 for item in diagnostics)
    assert all(item.timeout_max_attempts == 3 for item in diagnostics)
    assert all(item.timeout_backoff_seconds == 0 for item in diagnostics)
    assert all(item.timeout_budget_kind == "writer_initial" for item in diagnostics)
    diagnostic_text = repr(diagnostics)
    assert "Authorization" not in diagnostic_text
    assert "Bearer" not in diagnostic_text
    assert "writer user" not in diagnostic_text
    assert "test-secret" not in diagnostic_text


def test_auditor_timeout_diagnostic_uses_provider_bound_prompt_cost() -> None:
    """验证 auditor timeout cost 基于实际 provider-bound user prompt。"""

    records: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        """固定 timeout 并记录 provider request。"""

        records.append(request)
        raise httpx.TimeoutException("timeout with draft markdown and test-secret", request=request)

    client = OpenAICompatibleChapterLLMClient(
        config=_config(timeout_max_attempts=1, timeout_backoff_seconds=0),
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
        sleep=lambda _: None,
    )
    audit_request = _audit_request()

    with pytest.raises(LLMProviderTimeoutError) as exc_info:
        client.audit_chapter(audit_request)

    body = _json_body(records[0])
    provider_user_prompt = body["messages"][1]["content"]
    diagnostic = exc_info.value.diagnostics[0]
    assert diagnostic.operation == "auditor"
    assert diagnostic.system_prompt_chars == len(audit_request.system_prompt)
    assert diagnostic.user_prompt_chars == len(provider_user_prompt)
    assert diagnostic.user_prompt_chars > len(audit_request.user_prompt)
    assert diagnostic.approx_prompt_tokens == _ceil_div4(
        diagnostic.system_prompt_chars + diagnostic.user_prompt_chars
    )
    assert diagnostic.allowed_fact_count == len(audit_request.allowed_fact_ids)
    assert diagnostic.allowed_anchor_count == len(audit_request.allowed_anchor_ids)
    assert diagnostic.max_output_chars is None
    assert diagnostic.timeout_seconds == 10
    assert diagnostic.timeout_budget_kind == "auditor"
    diagnostic_text = repr(exc_info.value.diagnostics)
    assert "draft markdown" not in diagnostic_text
    assert "按 SEVERITY|LOCATION|MESSAGE 返回。" not in diagnostic_text
    assert "test-secret" not in diagnostic_text
    assert "Authorization" not in diagnostic_text
    assert "Bearer" not in diagnostic_text
    assert "provider body" not in diagnostic_text


@pytest.mark.parametrize(
    ("status_code", "error_type"),
    (
        (400, LLMProviderRuntimeError),
        (429, LLMProviderRateLimitError),
        (500, LLMProviderRuntimeError),
    ),
)
def test_http_errors_do_not_retry(status_code: int, error_type: type[Exception]) -> None:
    """验证非 timeout HTTP 错误不 retry。"""

    records: list[httpx.Request] = []
    client = _provider_client(
        records=records,
        status_code=status_code,
        response_text="provider body with writer user",
    )

    with pytest.raises(error_type):
        client.generate_chapter(_writer_request())

    assert len(records) == 1


def test_network_error_does_not_retry_and_carries_single_diagnostic() -> None:
    """验证非 timeout transport error 不 retry。"""

    records: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        """固定抛出 network error。"""

        records.append(request)
        raise httpx.TransportError("network down with writer user", request=request)

    client = OpenAICompatibleChapterLLMClient(
        config=_config(timeout_max_attempts=3),
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
        sleep=lambda _: None,
    )

    with pytest.raises(LLMProviderNetworkError) as exc_info:
        client.generate_chapter(_writer_request())

    assert len(records) == 1
    assert len(exc_info.value.diagnostics) == 1
    assert exc_info.value.diagnostics[0].provider_runtime_category == "network"


def test_malformed_response_does_not_retry_and_carries_single_diagnostic() -> None:
    """验证 malformed response 不 retry。"""

    records: list[httpx.Request] = []
    client = _provider_client(
        records=records,
        payload={"choices": []},
    )

    with pytest.raises(LLMProviderMalformedResponseError) as exc_info:
        client.generate_chapter(_writer_request())

    assert len(records) == 1
    assert len(exc_info.value.diagnostics) == 1
    assert exc_info.value.diagnostics[0].provider_runtime_category == "malformed"


def test_operation_specific_timeout_is_passed_to_httpx() -> None:
    """验证 writer/auditor/repair 使用各自 effective timeout。"""

    timeouts: list[object] = []

    def handler(request: httpx.Request) -> httpx.Response:
        """记录 httpx request timeout extension 并返回合法响应。"""

        timeouts.append(request.extensions.get("timeout"))
        return httpx.Response(
            200,
            json={
                "model": "unit-response-model",
                "choices": [{"message": {"content": "writer markdown"}, "finish_reason": "stop"}],
            },
            request=request,
        )

    client = OpenAICompatibleChapterLLMClient(
        config=_config(
            writer_timeout_seconds=11,
            auditor_timeout_seconds=22,
            repair_timeout_seconds=33,
        ),
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    client.generate_chapter(_writer_request())
    client.audit_chapter(_audit_request())
    client.generate_chapter(_writer_request(repair_attempt_index=1))

    assert _timeout_read_values(timeouts) == [11, 22, 33]


def test_repair_timeout_fallback_is_recorded_in_timeout_diagnostic() -> None:
    """验证 repair timeout fallback 决策进入安全 diagnostic。"""

    def handler(request: httpx.Request) -> httpx.Response:
        """固定 timeout。"""

        raise httpx.TimeoutException("timeout", request=request)

    client = OpenAICompatibleChapterLLMClient(
        config=_config(
            writer_timeout_seconds=11,
            repair_timeout_seconds=11,
            repair_timeout_fallback_used=True,
            timeout_max_attempts=1,
        ),
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
        sleep=lambda _: None,
    )

    with pytest.raises(LLMProviderTimeoutError) as exc_info:
        client.generate_chapter(_writer_request(repair_attempt_index=1))

    diagnostic = exc_info.value.diagnostics[0]
    assert diagnostic.timeout_budget_kind == "writer_repair"
    assert diagnostic.timeout_seconds == 11
    assert diagnostic.repair_timeout_fallback_used is True


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


def _config(
    *,
    writer_timeout_seconds: float = 10,
    auditor_timeout_seconds: float = 10,
    repair_timeout_seconds: float = 10,
    repair_timeout_fallback_used: bool = False,
    timeout_max_attempts: int = 2,
    timeout_backoff_seconds: float = 0.0,
) -> LLMProviderConfig:
    """构造测试用 provider config。

    Args:
        timeout_max_attempts: timeout 最大尝试次数。
        timeout_backoff_seconds: timeout retry backoff 秒数。

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
        writer_timeout_seconds=writer_timeout_seconds,
        auditor_timeout_seconds=auditor_timeout_seconds,
        repair_timeout_seconds=repair_timeout_seconds,
        repair_timeout_fallback_used=repair_timeout_fallback_used,
        timeout_max_attempts=timeout_max_attempts,
        timeout_backoff_seconds=timeout_backoff_seconds,
        max_output_chars=12000,
    )


def _writer_request(*, repair_attempt_index: int = 0) -> ChapterLLMRequest:
    """构造 writer request fixture。"""

    repair_context = None
    if repair_attempt_index > 0:
        from fund_agent.fund.chapter_writer import ChapterRepairContext

        repair_context = ChapterRepairContext(
            attempt_index=repair_attempt_index,
            previous_issue_ids=("issue-1",),
            previous_messages=("message",),
            required_corrections=("fix",),
        )
    return ChapterLLMRequest(
        chapter_id=1,
        fund_code="000001",
        report_year=2024,
        system_prompt="writer system",
        user_prompt="writer user",
        required_anchor_ids=("anchor-1",),
        forbidden_phrases=("建议买入",),
        max_output_chars=12000,
        repair_context=repair_context,
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


def _ceil_div4(value: int) -> int:
    """返回测试用固定 approximate token heuristic。"""

    return (value + 3) // 4


def _timeout_read_values(timeouts: list[object]) -> list[float]:
    """从 httpx timeout extension 提取 read timeout。"""

    values: list[float] = []
    for timeout in timeouts:
        if isinstance(timeout, dict):
            values.append(float(timeout["read"]))
        else:
            values.append(float(timeout))
    return values
