"""Service 层 Evidence Confirm provider-backed 语义蕴含 adapter。

本模块只把 typed provider config 适配成 Fund 层
``EvidenceEntailmentClient`` 协议。它不读取基金文档、repository、PDF/cache/source
helper，不修改 provider 默认值、runtime budget 或 Evidence Confirm 确定性策略。
见基金分析模板第 0-7 章 Evidence Confirm 语义复核路径。
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Final

import httpx

from fund_agent.config.llm import LLMProviderConfig
from fund_agent.fund.evidence_confirm_semantic import (
    EvidenceEntailmentJudgment,
    EvidenceEntailmentRequest,
)

_CHAT_COMPLETIONS_SUFFIX: Final[str] = "/chat/completions"
_AUTHORIZATION_HEADER: Final[str] = "Authorization"
_REQUEST_ID_HEADERS: Final[tuple[str, ...]] = (
    "x-request-id",
    "x-correlation-id",
    "request-id",
)
_SUPPORTED_PROVIDER_NAME: Final[str] = "openai_compatible"
_DEFAULT_REASON_BY_STATUS: Final[dict[str, str]] = {
    "entailed": "entailed_by_excerpt",
    "contradicted": "contradicted_by_excerpt",
    "insufficient": "insufficient_excerpt_support",
    "not_applicable": "not_applicable",
}
_VALID_REASON_BY_STATUS: Final[dict[str, frozenset[str]]] = {
    "entailed": frozenset(("entailed_by_excerpt",)),
    "contradicted": frozenset(("contradicted_by_excerpt",)),
    "insufficient": frozenset(("insufficient_excerpt_support",)),
    "not_applicable": frozenset(("not_applicable",)),
}


class EvidenceSemanticProviderError(RuntimeError):
    """provider-backed semantic adapter 安全错误。"""


@dataclass(frozen=True, slots=True)
class EvidenceSemanticProviderResponse:
    """provider-backed semantic adapter 的安全响应摘要。

    Attributes:
        status: closed semantic status。
        reason_code: closed reason code。
    """

    status: str
    reason_code: str


class OpenAICompatibleEvidenceEntailmentClient:
    """OpenAI-compatible Evidence Confirm semantic entailment client。"""

    def __init__(
        self,
        *,
        config: LLMProviderConfig,
        http_client: httpx.Client | None = None,
    ) -> None:
        """初始化 provider-backed semantic adapter。

        Args:
            config: typed LLM provider 配置。
            http_client: 可选 HTTP client；测试可注入 mock transport。

        Raises:
            EvidenceSemanticProviderError: provider 协议不支持时抛出。
        """

        if config.provider_name != _SUPPORTED_PROVIDER_NAME:
            raise EvidenceSemanticProviderError("unsupported semantic provider")
        self._config = config
        self._url = _chat_completions_url(config.base_url)
        self._http_client = http_client or httpx.Client(timeout=config.timeout_seconds)

    def judge(self, request: EvidenceEntailmentRequest) -> EvidenceEntailmentJudgment:
        """调用 provider 判断 claim 是否被 bounded excerpts 蕴含。

        Args:
            request: Fund 层传入的 semantic entailment 请求。

        Returns:
            Fund 层 closed judgment。

        Raises:
            EvidenceSemanticProviderError: provider 调用或响应不符合契约时抛出安全错误。
        """

        response = self._complete(request)
        return EvidenceEntailmentJudgment(
            status=response.status,  # type: ignore[arg-type]
            reason_code=response.reason_code,  # type: ignore[arg-type]
            message=f"provider semantic status: {response.status}",
        )

    def _complete(self, request: EvidenceEntailmentRequest) -> EvidenceSemanticProviderResponse:
        """执行一次 provider semantic 判断。

        Args:
            request: semantic entailment 请求。

        Returns:
            安全响应摘要。

        Raises:
            EvidenceSemanticProviderError: HTTP 或响应结构失败时抛出。
        """

        try:
            response = self._http_client.post(
                self._url,
                headers={
                    _AUTHORIZATION_HEADER: f"Bearer {self._config.api_key}",
                    "Content-Type": "application/json",
                },
                json=_chat_payload(self._config.model, request),
                timeout=self._config.timeout_seconds,
            )
        except httpx.TimeoutException as exc:
            raise EvidenceSemanticProviderError("semantic provider timeout") from exc
        except httpx.TransportError as exc:
            raise EvidenceSemanticProviderError("semantic provider network error") from exc

        if response.status_code < 200 or response.status_code >= 300:
            message = _safe_http_error_message("semantic provider request failed", response)
            raise EvidenceSemanticProviderError(message)

        try:
            payload = response.json()
        except ValueError as exc:
            raise EvidenceSemanticProviderError("semantic provider returned invalid JSON") from exc
        if not isinstance(payload, Mapping):
            raise EvidenceSemanticProviderError("semantic provider response must be a JSON object")
        content = _extract_text(payload)
        return _parse_semantic_content(content)


def build_evidence_entailment_client(
    config: LLMProviderConfig,
) -> OpenAICompatibleEvidenceEntailmentClient:
    """构造 provider-backed Evidence Confirm semantic client。

    Args:
        config: typed LLM provider 配置。

    Returns:
        OpenAI-compatible semantic entailment client。

    Raises:
        EvidenceSemanticProviderError: provider 协议不支持时抛出。
    """

    return OpenAICompatibleEvidenceEntailmentClient(config=config)


def _chat_completions_url(base_url: str) -> str:
    """从 base URL 派生 chat completions URL。

    Args:
        base_url: 已校验的 provider base URL。

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


def _chat_payload(model: str, request: EvidenceEntailmentRequest) -> dict[str, object]:
    """构造 semantic provider chat payload。

    Args:
        model: provider model 名称。
        request: semantic entailment 请求。

    Returns:
        OpenAI-compatible chat payload。

    Raises:
        无显式抛出。
    """

    return {
        "model": model,
        "messages": (
            {"role": "system", "content": _system_prompt()},
            {"role": "user", "content": _user_prompt(request)},
        ),
    }


def _system_prompt() -> str:
    """返回 provider semantic system prompt。

    Args:
        无。

    Returns:
        provider system prompt。

    Raises:
        无显式抛出。
    """

    return (
        "你是 Evidence Confirm 语义蕴含判定器。只判断 claim 是否被给定 excerpts 明确支持。"
        "只能返回 JSON object，不要返回 Markdown。"
        "status 只能是 entailed、contradicted、insufficient、not_applicable。"
        "reason_code 必须分别对应 entailed_by_excerpt、contradicted_by_excerpt、"
        "insufficient_excerpt_support、not_applicable。"
        "如果 excerpts 不足以证明 claim，返回 insufficient。"
    )


def _user_prompt(request: EvidenceEntailmentRequest) -> str:
    """构造 provider semantic user prompt。

    Args:
        request: semantic entailment 请求。

    Returns:
        provider user prompt。这里包含 bounded excerpt 文本；调用方不得把该 prompt 写入诊断。

    Raises:
        无显式抛出。
    """

    excerpt_lines = "\n".join(
        f"[excerpt_{index}] {text}" for index, text in enumerate(request.excerpt_texts, start=1)
    )
    return "\n".join(
        (
            'Return exactly: {"status":"...","reason_code":"..."}',
            f"claim_id: {request.claim.claim_id}",
            f"fact_id: {request.claim.fact_id}",
            f"source_field_id: {request.claim.source_field_id}",
            f"claim: {request.claim.claim_text}",
            "excerpts:",
            excerpt_lines,
        )
    )


def _extract_text(payload: Mapping[str, Any]) -> str:
    """从 OpenAI-compatible response 中提取 message content。

    Args:
        payload: provider JSON object。

    Returns:
        provider message content。

    Raises:
        EvidenceSemanticProviderError: 响应结构不符合 contract 时抛出。
    """

    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        raise EvidenceSemanticProviderError("semantic provider response missing choices[0]")
    first_choice = choices[0]
    if not isinstance(first_choice, Mapping):
        raise EvidenceSemanticProviderError("semantic provider choices[0] must be an object")
    message = first_choice.get("message")
    if not isinstance(message, Mapping):
        raise EvidenceSemanticProviderError("semantic provider choices[0].message must be an object")
    content = message.get("content")
    if not isinstance(content, str):
        raise EvidenceSemanticProviderError(
            "semantic provider choices[0].message.content must be a string"
        )
    return content


def _parse_semantic_content(content: str) -> EvidenceSemanticProviderResponse:
    """解析 provider semantic JSON content。

    Args:
        content: provider message content。

    Returns:
        closed semantic status/reason。

    Raises:
        EvidenceSemanticProviderError: JSON 或 closed-set 字段非法时抛出。
    """

    try:
        payload = json.loads(content)
    except ValueError as exc:
        raise EvidenceSemanticProviderError("semantic provider content must be JSON") from exc
    if not isinstance(payload, Mapping):
        raise EvidenceSemanticProviderError("semantic provider content must be a JSON object")
    status = payload.get("status")
    if not isinstance(status, str) or status not in _DEFAULT_REASON_BY_STATUS:
        raise EvidenceSemanticProviderError("semantic provider status is not closed-set")
    reason = payload.get("reason_code", _DEFAULT_REASON_BY_STATUS[status])
    if not isinstance(reason, str) or reason not in _VALID_REASON_BY_STATUS[status]:
        raise EvidenceSemanticProviderError("semantic provider reason_code is invalid")
    return EvidenceSemanticProviderResponse(status=status, reason_code=reason)


def _safe_http_error_message(prefix: str, response: httpx.Response) -> str:
    """构造不含 response body、prompt 或 secret 的 HTTP 错误摘要。

    Args:
        prefix: 错误前缀。
        response: HTTP response。

    Returns:
        安全错误摘要。

    Raises:
        无显式抛出。
    """

    request_id = _request_id(response.headers)
    suffix = f" request_id={request_id}" if request_id else ""
    return f"{prefix}: status_code={response.status_code}{suffix}"


def _request_id(headers: Mapping[str, str]) -> str | None:
    """从响应 header 中读取安全 request id。

    Args:
        headers: HTTP response headers。

    Returns:
        request id；没有时返回 `None`。

    Raises:
        无显式抛出。
    """

    for header in _REQUEST_ID_HEADERS:
        value = headers.get(header)
        if value:
            return value[:80]
    return None


__all__ = [
    "EvidenceSemanticProviderError",
    "OpenAICompatibleEvidenceEntailmentClient",
    "build_evidence_entailment_client",
]
