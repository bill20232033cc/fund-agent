"""Service 层 OpenAI-compatible LLM provider factory。

本模块负责把 typed LLM provider config 适配成 Gate 3 `ChapterOrchestrator`
需要的 writer/auditor Protocol clients，见模板第 1-6 章写作与审计路径。
它不解析基金文档、不修改 Fund writer/auditor 协议、不接入 CLI、Host、
Agent/dayu，也不引入 vendor SDK。
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
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
from fund_agent.services.chapter_orchestrator import ChapterOrchestratorLLMClients

_CHAT_COMPLETIONS_SUFFIX: Final[str] = "/chat/completions"
_AUTHORIZATION_HEADER: Final[str] = "Authorization"
_REQUEST_ID_HEADERS: Final[tuple[str, ...]] = (
    "x-request-id",
    "x-correlation-id",
    "request-id",
)


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
    ) -> None:
        """初始化 provider adapter。

        Args:
            config: typed LLM provider 配置。
            http_client: 可选 HTTP client；测试使用 `httpx.MockTransport` 注入。

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
            system_prompt=request.system_prompt,
            user_prompt=request.user_prompt,
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

        provider_response = self._complete(
            system_prompt=request.system_prompt,
            user_prompt=_audit_user_prompt(request),
        )
        return ChapterAuditLLMResponse(
            raw_text=provider_response.text,
            model_name=provider_response.model_name,
            finish_reason=provider_response.finish_reason,
        )

    def _complete(self, *, system_prompt: str, user_prompt: str) -> LLMProviderResponse:
        """调用 OpenAI-compatible chat completions endpoint。

        Args:
            system_prompt: system message 内容。
            user_prompt: user message 内容。

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
        try:
            response = self._http_client.post(
                self._url,
                headers={
                    _AUTHORIZATION_HEADER: f"Bearer {self._config.api_key}",
                    "Content-Type": "application/json",
                },
                json=request_body,
            )
        except httpx.TimeoutException as exc:
            raise LLMProviderRuntimeError("LLM provider request timed out") from exc
        except httpx.TransportError as exc:
            raise LLMProviderRuntimeError("LLM provider network error") from exc

        if response.status_code == 429:
            raise LLMProviderRateLimitError(_safe_http_error_message("rate limited", response))
        if response.status_code < 200 or response.status_code >= 300:
            raise LLMProviderRuntimeError(_safe_http_error_message("request failed", response))

        try:
            payload = response.json()
        except ValueError as exc:
            raise LLMProviderMalformedResponseError("LLM provider returned invalid JSON") from exc
        if not isinstance(payload, Mapping):
            raise LLMProviderMalformedResponseError("LLM provider response must be a JSON object")
        return _extract_text(payload)


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
