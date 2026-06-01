"""Service 层 OpenAI-compatible LLM provider factory。

本模块负责把 typed LLM provider config 适配成 Gate 3 `ChapterOrchestrator`
需要的 writer/auditor Protocol clients，见模板第 1-6 章写作与审计路径。
它不解析基金文档、不修改 Fund writer/auditor 协议、不接入 CLI、Host、
Agent/dayu，也不引入 vendor SDK。
"""

from __future__ import annotations

import time
from collections.abc import Callable
from collections.abc import Mapping
from dataclasses import dataclass
from math import ceil
from typing import Any, Final

import httpx

from fund_agent.config.llm import LLMProviderConfig
from fund_agent.fund.chapter_auditor import (
    ChapterAuditLLMClient,
    ChapterAuditLLMRequest,
    ChapterAuditLLMResponse,
)
from fund_agent.fund.chapter_writer import (
    ChapterLLMClient,
    ChapterLLMRequest,
    ChapterLLMResponse,
)
from fund_agent.services.chapter_orchestrator import (
    ChapterLLMRuntimeDiagnostic,
    ChapterOrchestratorLLMClients,
    ProviderOperation,
    ProviderRuntimeCategory,
)

_CHAT_COMPLETIONS_SUFFIX: Final[str] = "/chat/completions"
_AUTHORIZATION_HEADER: Final[str] = "Authorization"
_REQUEST_ID_HEADERS: Final[tuple[str, ...]] = (
    "x-request-id",
    "x-correlation-id",
    "request-id",
)
_MAX_DIAGNOSTIC_MESSAGE_CHARS: Final[int] = 180


@dataclass(frozen=True, slots=True, kw_only=True)
class _ProviderCostContext:
    """provider-bound prompt/runtime cost 标量上下文。

    Attributes:
        system_prompt_chars: 实际发送的 system prompt 字符数。
        user_prompt_chars: 实际发送的 user prompt 字符数。
        approx_prompt_tokens: 以固定 heuristic 估算的 prompt token 数。
        allowed_fact_count: 允许 fact 数；writer 当前不可得。
        allowed_anchor_count: 允许 anchor 数。
        max_output_chars: writer 输出字符上限；auditor 不适用。
        prompt_cost_diagnostic: writer prompt-cost 安全诊断。
        repair_attempt_index: writer repair attempt index；auditor 为 0。
    """

    system_prompt_chars: int
    user_prompt_chars: int
    approx_prompt_tokens: int
    allowed_fact_count: int | None
    allowed_anchor_count: int | None
    max_output_chars: int | None
    prompt_cost_diagnostic: object | None = None
    repair_attempt_index: int = 0



@dataclass(frozen=True, slots=True, kw_only=True)
class LLMProviderResponse:
    """OpenAI-compatible provider 响应投影。

    Attributes:
        text: `choices[0].message.content` 文本。
        model_name: provider 返回的模型名；缺失时为 `None`。
        finish_reason: `choices[0].finish_reason`；缺失时为 `None`。
    """

    text: str
    model_name: str | None
    finish_reason: str | None


class LLMProviderConstructionError(RuntimeError):
    """provider client 构造失败。"""


class LLMProviderRuntimeError(RuntimeError):
    """provider 调用失败。"""

    def __init__(
        self,
        message: str,
        *,
        diagnostics: tuple[ChapterLLMRuntimeDiagnostic, ...] = (),
    ) -> None:
        """初始化 provider runtime error。

        Args:
            message: 安全错误摘要。
            diagnostics: provider attempt 安全诊断。

        Raises:
            无显式抛出。
        """

        super().__init__(message)
        self.diagnostics = diagnostics


class LLMProviderTimeoutError(LLMProviderRuntimeError):
    """provider timeout。"""


class LLMProviderNetworkError(LLMProviderRuntimeError):
    """provider network error。"""


class LLMProviderRateLimitError(LLMProviderRuntimeError):
    """provider rate limit。"""


class LLMProviderMalformedResponseError(LLMProviderRuntimeError):
    """provider 响应结构不符合 contract。"""


class OpenAICompatibleChapterLLMClient(ChapterLLMClient, ChapterAuditLLMClient):
    """OpenAI-compatible HTTP chat-completions 章节 LLM client。

    同一个 adapter 同时实现章节 writer 与 auditor Protocol。audit 路径以
    `ChapterAuditLLMRequest.user_prompt` 为 Gate 2 审计协议真源，不在 provider
    层重复构造 `SEVERITY|LOCATION|MESSAGE` 协议。
    """

    def __init__(
        self,
        *,
        config: LLMProviderConfig,
        http_client: httpx.Client | None = None,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        """初始化 provider adapter。

        Args:
            config: typed LLM provider 配置。
            http_client: 可选 HTTP client；测试使用 `httpx.MockTransport` 注入。
            sleep: timeout retry 前等待函数；测试可注入 no-op。

        Raises:
            LLMProviderConstructionError: 当 provider 协议不受支持时抛出。
        """

        if config.provider_name != "openai_compatible":
            raise LLMProviderConstructionError(
                f"unsupported provider {config.provider_name!r} for OpenAI-compatible client"
            )
        self._config = config
        self._url = _chat_completions_url(config.base_url)
        self._http_client = http_client or httpx.Client(timeout=config.timeout_seconds)
        self._sleep = sleep

    def generate_chapter(self, request: ChapterLLMRequest) -> ChapterLLMResponse:
        """生成单章草稿。

        Args:
            request: Gate 2 章节写作请求。

        Returns:
            Gate 2 章节写作响应。

        Raises:
            LLMProviderRuntimeError: 当 HTTP 调用、状态码或响应结构失败时抛出。
        """

        provider_response = self._complete(
            operation="writer",
            system_prompt=request.system_prompt,
            user_prompt=request.user_prompt,
            cost_context=_writer_cost_context(request),
        )
        return ChapterLLMResponse(
            text=provider_response.text,
            model_name=provider_response.model_name,
            finish_reason=provider_response.finish_reason,
        )

    def audit_chapter(self, request: ChapterAuditLLMRequest) -> ChapterAuditLLMResponse:
        """审计单章草稿。

        Args:
            request: Gate 2 章节审计请求。

        Returns:
            Gate 2 章节审计响应，`raw_text` 保留 provider 返回文本。

        Raises:
            LLMProviderRuntimeError: 当 HTTP 调用、状态码或响应结构失败时抛出。
        """

        provider_user_prompt = _audit_user_prompt(request)
        provider_response = self._complete(
            operation="auditor",
            system_prompt=request.system_prompt,
            user_prompt=provider_user_prompt,
            cost_context=_auditor_cost_context(request, provider_user_prompt),
        )
        return ChapterAuditLLMResponse(
            raw_text=provider_response.text,
            model_name=provider_response.model_name,
            finish_reason=provider_response.finish_reason,
        )

    def _complete(
        self,
        *,
        operation: ProviderOperation,
        system_prompt: str,
        user_prompt: str,
        cost_context: _ProviderCostContext,
    ) -> LLMProviderResponse:
        """调用 OpenAI-compatible chat completions endpoint。

        Args:
            operation: writer 或 auditor，仅用于 provider-local 安全诊断。
            system_prompt: system message 内容。
            user_prompt: user message 内容。
            cost_context: provider-bound prompt/runtime cost 标量。

        Returns:
            provider 响应投影。

        Raises:
            LLMProviderRateLimitError: 当 provider 返回 429 时抛出。
            LLMProviderRuntimeError: 当网络、timeout 或非 2xx 状态失败时抛出。
            LLMProviderMalformedResponseError: 当 JSON 或响应结构不符合 contract 时抛出。
        """

        request_body = _chat_payload(
            model=self._config.model,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )
        diagnostics: list[ChapterLLMRuntimeDiagnostic] = []
        max_attempts = self._config.timeout_max_attempts
        effective_timeout = _effective_timeout_seconds(
            self._config,
            operation=operation,
            repair_attempt_index=cost_context.repair_attempt_index,
        )
        timeout_budget_kind = _timeout_budget_kind(
            operation=operation,
            repair_attempt_index=cost_context.repair_attempt_index,
        )
        for provider_attempt_index in range(1, max_attempts + 1):
            started_at = time.monotonic()
            try:
                response = self._http_client.post(
                    self._url,
                    headers={
                        _AUTHORIZATION_HEADER: f"Bearer {self._config.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=request_body,
                    timeout=effective_timeout,
                )
            except httpx.TimeoutException as exc:
                diagnostics.append(
                    _provider_diagnostic(
                        operation=operation,
                        provider_attempt_index=provider_attempt_index,
                        provider_max_attempts=max_attempts,
                        provider_runtime_category="timeout",
                        started_at=started_at,
                        cost_context=cost_context,
                        timeout_seconds=effective_timeout,
                        timeout_budget_kind=timeout_budget_kind,
                        timeout_backoff_seconds=self._config.timeout_backoff_seconds,
                        repair_timeout_fallback_used=self._config.repair_timeout_fallback_used,
                        error_type=type(exc).__name__,
                        message="LLM provider request timed out",
                    )
                )
                if provider_attempt_index < max_attempts:
                    if self._config.timeout_backoff_seconds > 0:
                        self._sleep(self._config.timeout_backoff_seconds)
                    continue
                raise LLMProviderTimeoutError(
                    "LLM provider request timed out",
                    diagnostics=tuple(diagnostics),
                ) from exc
            except httpx.TransportError as exc:
                diagnostic = _provider_diagnostic(
                    operation=operation,
                    provider_attempt_index=provider_attempt_index,
                    provider_max_attempts=max_attempts,
                    provider_runtime_category="network",
                    started_at=started_at,
                    cost_context=cost_context,
                    timeout_seconds=effective_timeout,
                    timeout_budget_kind=timeout_budget_kind,
                    timeout_backoff_seconds=self._config.timeout_backoff_seconds,
                    repair_timeout_fallback_used=self._config.repair_timeout_fallback_used,
                    error_type=type(exc).__name__,
                    message="LLM provider network error",
                )
                raise LLMProviderNetworkError(
                    "LLM provider network error",
                    diagnostics=(*diagnostics, diagnostic),
                ) from exc

            if response.status_code == 429:
                diagnostic = _provider_diagnostic(
                    operation=operation,
                    provider_attempt_index=provider_attempt_index,
                    provider_max_attempts=max_attempts,
                    provider_runtime_category="rate_limit",
                    started_at=started_at,
                    cost_context=cost_context,
                    timeout_seconds=effective_timeout,
                    timeout_budget_kind=timeout_budget_kind,
                    timeout_backoff_seconds=self._config.timeout_backoff_seconds,
                    repair_timeout_fallback_used=self._config.repair_timeout_fallback_used,
                    response=response,
                    message=_safe_http_error_message("rate limited", response),
                )
                raise LLMProviderRateLimitError(
                    _safe_http_error_message("rate limited", response),
                    diagnostics=(*diagnostics, diagnostic),
                )
            if response.status_code < 200 or response.status_code >= 300:
                diagnostic = _provider_diagnostic(
                    operation=operation,
                    provider_attempt_index=provider_attempt_index,
                    provider_max_attempts=max_attempts,
                    provider_runtime_category="http_error",
                    started_at=started_at,
                    cost_context=cost_context,
                    timeout_seconds=effective_timeout,
                    timeout_budget_kind=timeout_budget_kind,
                    timeout_backoff_seconds=self._config.timeout_backoff_seconds,
                    repair_timeout_fallback_used=self._config.repair_timeout_fallback_used,
                    response=response,
                    message=_safe_http_error_message("request failed", response),
                )
                raise LLMProviderRuntimeError(
                    _safe_http_error_message("request failed", response),
                    diagnostics=(*diagnostics, diagnostic),
                )

            try:
                payload = response.json()
            except ValueError as exc:
                diagnostic = _provider_diagnostic(
                    operation=operation,
                    provider_attempt_index=provider_attempt_index,
                    provider_max_attempts=max_attempts,
                    provider_runtime_category="malformed",
                    started_at=started_at,
                    cost_context=cost_context,
                    timeout_seconds=effective_timeout,
                    timeout_budget_kind=timeout_budget_kind,
                    timeout_backoff_seconds=self._config.timeout_backoff_seconds,
                    repair_timeout_fallback_used=self._config.repair_timeout_fallback_used,
                    response=response,
                    error_type=type(exc).__name__,
                    message="LLM provider returned invalid JSON",
                )
                raise LLMProviderMalformedResponseError(
                    "LLM provider returned invalid JSON",
                    diagnostics=(*diagnostics, diagnostic),
                ) from exc
            if not isinstance(payload, Mapping):
                diagnostic = _provider_diagnostic(
                    operation=operation,
                    provider_attempt_index=provider_attempt_index,
                    provider_max_attempts=max_attempts,
                    provider_runtime_category="malformed",
                    started_at=started_at,
                    cost_context=cost_context,
                    timeout_seconds=effective_timeout,
                    timeout_budget_kind=timeout_budget_kind,
                    timeout_backoff_seconds=self._config.timeout_backoff_seconds,
                    repair_timeout_fallback_used=self._config.repair_timeout_fallback_used,
                    response=response,
                    message="LLM provider response must be a JSON object",
                )
                raise LLMProviderMalformedResponseError(
                    "LLM provider response must be a JSON object",
                    diagnostics=(*diagnostics, diagnostic),
                )
            try:
                provider_response = _extract_text(payload)
            except LLMProviderMalformedResponseError as exc:
                diagnostic = _provider_diagnostic(
                    operation=operation,
                    provider_attempt_index=provider_attempt_index,
                    provider_max_attempts=max_attempts,
                    provider_runtime_category="malformed",
                    started_at=started_at,
                    cost_context=cost_context,
                    timeout_seconds=effective_timeout,
                    timeout_budget_kind=timeout_budget_kind,
                    timeout_backoff_seconds=self._config.timeout_backoff_seconds,
                    repair_timeout_fallback_used=self._config.repair_timeout_fallback_used,
                    response=response,
                    error_type=type(exc).__name__,
                    message=str(exc),
                )
                raise LLMProviderMalformedResponseError(
                    str(exc),
                    diagnostics=(*diagnostics, diagnostic),
                ) from exc
            return provider_response
        raise LLMProviderRuntimeError("LLM provider retry loop ended unexpectedly")


def build_chapter_llm_clients(config: LLMProviderConfig) -> ChapterOrchestratorLLMClients:
    """构造 Route C Gate 3 所需 writer/auditor LLM clients。

    Args:
        config: typed LLM provider 配置。

    Returns:
        使用同一个 OpenAI-compatible adapter 的 writer/auditor client 包。

    Raises:
        LLMProviderConstructionError: 当 provider 协议不受支持或构造失败时抛出。
    """

    try:
        client = OpenAICompatibleChapterLLMClient(config=config)
    except LLMProviderConstructionError:
        raise
    except Exception as exc:
        raise LLMProviderConstructionError("failed to construct LLM provider client") from exc
    return ChapterOrchestratorLLMClients(writer=client, auditor=client)


def _chat_completions_url(base_url: str) -> str:
    """从 base URL 派生 chat completions URL。

    Args:
        base_url: 已由 config 层校验的 base URL。

    Returns:
        OpenAI-compatible chat completions URL。

    Raises:
        无显式抛出。
    """

    normalized = base_url.rstrip("/")
    if normalized.endswith(_CHAT_COMPLETIONS_SUFFIX):
        return normalized
    if normalized.endswith("/v1"):
        return f"{normalized}{_CHAT_COMPLETIONS_SUFFIX}"
    return f"{normalized}/v1{_CHAT_COMPLETIONS_SUFFIX}"


def _chat_payload(*, model: str, system_prompt: str, user_prompt: str) -> dict[str, object]:
    """构造 OpenAI-compatible chat completions JSON body。

    Args:
        model: 模型名。
        system_prompt: system message 内容。
        user_prompt: user message 内容。

    Returns:
        请求 JSON body。

    Raises:
        无显式抛出。
    """

    return {
        "model": model,
        "messages": (
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ),
    }


def _audit_user_prompt(request: ChapterAuditLLMRequest) -> str:
    """构造 provider user message，保持 Gate 2 审计 prompt 语义不变。

    Args:
        request: Gate 2 章节审计请求。

    Returns:
        provider user message。首段完整保留 `request.user_prompt`；随后附加草稿和
        显式上下文，方便 provider 审计，但不重复构造审计行协议。

    Raises:
        无显式抛出。
    """

    return "\n\n".join(
        (
            request.user_prompt,
            "待审计章节 Markdown：",
            request.draft_markdown,
            f"允许 fact ids：{', '.join(request.allowed_fact_ids)}",
            f"允许 anchor ids：{', '.join(request.allowed_anchor_ids)}",
            f"审计关注点：{', '.join(request.audit_focus)}",
        )
    )


def _writer_cost_context(request: ChapterLLMRequest) -> _ProviderCostContext:
    """构造 writer provider-bound prompt/runtime cost 标量。

    Args:
        request: Gate 2 章节写作请求。

    Returns:
        不含 prompt 文本的 cost context。

    Raises:
        无显式抛出。
    """

    system_prompt_chars = len(request.system_prompt)
    user_prompt_chars = len(request.user_prompt)
    return _ProviderCostContext(
        system_prompt_chars=system_prompt_chars,
        user_prompt_chars=user_prompt_chars,
        approx_prompt_tokens=_approx_prompt_tokens(
            system_prompt_chars,
            user_prompt_chars,
        ),
        allowed_fact_count=None,
        allowed_anchor_count=len(request.required_anchor_ids),
        max_output_chars=request.max_output_chars,
        prompt_cost_diagnostic=request.prompt_cost_diagnostic,
        repair_attempt_index=request.repair_context.attempt_index
        if request.repair_context is not None
        else 0,
    )


def _auditor_cost_context(
    request: ChapterAuditLLMRequest,
    provider_user_prompt: str,
) -> _ProviderCostContext:
    """构造 auditor provider-bound prompt/runtime cost 标量。

    Args:
        request: Gate 2 章节审计请求。
        provider_user_prompt: 实际发送给 provider 的 user message。

    Returns:
        不含 prompt、draft 或 raw audit 文本的 cost context。

    Raises:
        无显式抛出。
    """

    system_prompt_chars = len(request.system_prompt)
    user_prompt_chars = len(provider_user_prompt)
    return _ProviderCostContext(
        system_prompt_chars=system_prompt_chars,
        user_prompt_chars=user_prompt_chars,
        approx_prompt_tokens=_approx_prompt_tokens(
            system_prompt_chars,
            user_prompt_chars,
        ),
        allowed_fact_count=len(request.allowed_fact_ids),
        allowed_anchor_count=len(request.allowed_anchor_ids),
        max_output_chars=None,
        prompt_cost_diagnostic=None,
        repair_attempt_index=0,
    )


def _approx_prompt_tokens(system_prompt_chars: int, user_prompt_chars: int) -> int:
    """按固定保守 heuristic 估算 prompt token 数。

    Args:
        system_prompt_chars: system prompt 字符数。
        user_prompt_chars: user prompt 字符数。

    Returns:
        `ceil((system + user) / 4)` 的近似 token 数。

    Raises:
        无显式抛出。
    """

    return ceil((system_prompt_chars + user_prompt_chars) / 4)


def _repair_attempt_index(prompt_cost_diagnostic: object | None) -> int:
    """从 writer prompt-cost 诊断读取 repair attempt。

    Args:
        prompt_cost_diagnostic: writer prompt-cost 诊断。

    Returns:
        当前 provider request 所属 repair attempt；缺省为 0。

    Raises:
        无显式抛出。
    """

    repair_attempt_index = getattr(prompt_cost_diagnostic, "repair_attempt_index", None)
    if isinstance(repair_attempt_index, int):
        return repair_attempt_index
    return 0


def _effective_timeout_seconds(
    config: LLMProviderConfig,
    *,
    operation: ProviderOperation,
    repair_attempt_index: int,
) -> float:
    """读取单次 provider request 的 effective timeout。

    Args:
        config: typed provider 配置。
        operation: writer 或 auditor。
        repair_attempt_index: 当前章节 attempt index。

    Returns:
        effective timeout 秒数。

    Raises:
        无显式抛出。
    """

    if operation == "auditor":
        return config.auditor_timeout_seconds
    if repair_attempt_index > 0:
        return config.repair_timeout_seconds
    return config.writer_timeout_seconds


def _timeout_budget_kind(
    *,
    operation: ProviderOperation,
    repair_attempt_index: int,
) -> str:
    """读取 timeout budget kind。

    Args:
        operation: writer 或 auditor。
        repair_attempt_index: 当前章节 attempt index。

    Returns:
        timeout budget kind。

    Raises:
        无显式抛出。
    """

    if operation == "auditor":
        return "auditor"
    if repair_attempt_index > 0:
        return "writer_repair"
    return "writer_initial"


def _extract_text(payload: Mapping[str, Any]) -> LLMProviderResponse:
    """从 OpenAI-compatible JSON 响应提取文本。

    Args:
        payload: provider JSON object。

    Returns:
        provider 响应投影。

    Raises:
        LLMProviderMalformedResponseError: 当 `choices[0].message.content` 不是字符串时抛出。
    """

    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        raise LLMProviderMalformedResponseError("LLM provider response missing choices[0]")
    first_choice = choices[0]
    if not isinstance(first_choice, Mapping):
        raise LLMProviderMalformedResponseError("LLM provider choices[0] must be an object")
    message = first_choice.get("message")
    if not isinstance(message, Mapping):
        raise LLMProviderMalformedResponseError("LLM provider choices[0].message must be an object")
    content = message.get("content")
    if not isinstance(content, str):
        raise LLMProviderMalformedResponseError(
            "LLM provider choices[0].message.content must be a string"
        )

    model = payload.get("model")
    finish_reason = first_choice.get("finish_reason")
    return LLMProviderResponse(
        text=content,
        model_name=model if isinstance(model, str) else None,
        finish_reason=finish_reason if isinstance(finish_reason, str) else None,
    )


def _provider_diagnostic(
    *,
    operation: ProviderOperation,
    provider_attempt_index: int,
    provider_max_attempts: int,
    provider_runtime_category: ProviderRuntimeCategory,
    started_at: float,
    cost_context: _ProviderCostContext,
    timeout_seconds: float,
    timeout_budget_kind: str,
    timeout_backoff_seconds: float,
    repair_timeout_fallback_used: bool,
    response: httpx.Response | None = None,
    error_type: str | None = None,
    message: str | None = None,
) -> ChapterLLMRuntimeDiagnostic:
    """构造 provider-local 安全 runtime diagnostic。

    Args:
        operation: writer 或 auditor。
        provider_attempt_index: provider `_complete()` 内从 1 开始的尝试序号。
        provider_max_attempts: provider `_complete()` 最大尝试次数。
        provider_runtime_category: provider runtime 分类。
        started_at: attempt 开始时间戳。
        cost_context: provider-bound prompt/runtime cost 标量。
        response: 可选 HTTP 响应，只读取 status/header。
        error_type: 安全异常类型名。
        message: 安全摘要候选。

    Returns:
        不含章节身份、prompt、draft、provider body 或 secret 的诊断记录。

    Raises:
        无显式抛出。
    """

    elapsed_ms = int((time.monotonic() - started_at) * 1000)
    return ChapterLLMRuntimeDiagnostic(
        operation=operation,
        chapter_id=None,
        fund_code=None,
        report_year=None,
        repair_attempt_index=None,
        provider_attempt_index=provider_attempt_index,
        provider_max_attempts=provider_max_attempts,
        provider_runtime_category=provider_runtime_category,
        chapter_failure_category=None,
        elapsed_ms=elapsed_ms,
        status_code=response.status_code if response is not None else None,
        request_id=_request_id(response.headers) if response is not None else None,
        model_name=None,
        finish_reason=None,
        response_chars=None,
        error_type=error_type,
        system_prompt_chars=cost_context.system_prompt_chars,
        user_prompt_chars=cost_context.user_prompt_chars,
        approx_prompt_tokens=cost_context.approx_prompt_tokens,
        allowed_fact_count=cost_context.allowed_fact_count,
        allowed_anchor_count=cost_context.allowed_anchor_count,
        max_output_chars=cost_context.max_output_chars,
        timeout_seconds=timeout_seconds,
        timeout_max_attempts=provider_max_attempts,
        timeout_backoff_seconds=timeout_backoff_seconds,
        timeout_budget_kind=timeout_budget_kind,  # type: ignore[arg-type]
        repair_timeout_fallback_used=repair_timeout_fallback_used,
        prompt_cost_diagnostic=cost_context.prompt_cost_diagnostic,
        message=_sanitize_text(message) if message else None,
    )


def _safe_http_error_message(category: str, response: httpx.Response) -> str:
    """构造不包含 secret、prompt 或响应正文的 HTTP 错误消息。

    Args:
        category: 错误类别。
        response: HTTP 响应对象。

    Returns:
        只包含 status code 与可用 request id 的错误消息。

    Raises:
        无显式抛出。
    """

    request_id = _request_id(response.headers)
    if request_id is None:
        return f"LLM provider {category}: status_code={response.status_code}"
    return f"LLM provider {category}: status_code={response.status_code}, request_id={request_id}"


def _request_id(headers: httpx.Headers) -> str | None:
    """读取 provider 响应中的安全 request id。

    Args:
        headers: HTTP 响应 headers。

    Returns:
        request id；缺失时为 `None`。

    Raises:
        无显式抛出。
    """

    for header_name in _REQUEST_ID_HEADERS:
        value = headers.get(header_name)
        if value:
            return value
    return None


def _sanitize_text(text: str | None, *, max_chars: int = _MAX_DIAGNOSTIC_MESSAGE_CHARS) -> str:
    """清理 provider runtime diagnostic 文本。

    Args:
        text: 原始文本。
        max_chars: 最大保留字符数。

    Returns:
        单行、脱敏、限长文本。

    Raises:
        无显式抛出。
    """

    if text is None:
        return ""
    redacted = " ".join(text.replace("\r", " ").replace("\n", " ").split())
    for sensitive in (
        "Authorization",
        "Bearer",
        "FUND_AGENT_LLM_API_KEY",
        "api_key",
        "sk-",
        "prompt",
        "writer user",
        "draft markdown",
    ):
        redacted = redacted.replace(sensitive, "[redacted]")
    if len(redacted) <= max_chars:
        return redacted
    return redacted[:max_chars].rstrip() + "..."
