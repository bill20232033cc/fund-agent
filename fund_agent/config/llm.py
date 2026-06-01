"""生产 LLM provider typed env 配置。

本模块只负责把显式环境变量解析为不可变配置对象。它不构造 HTTP client，
不读取基金文档，不接入 Service、Host、Agent/dayu，也不提供默认供应商、
默认模型或默认 endpoint。
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Final, Literal, Mapping
from urllib.parse import urlparse

LLMProviderName = Literal["openai_compatible"]

_SUPPORTED_PROVIDER_NAME: Final[LLMProviderName] = "openai_compatible"
_DEFAULT_API_KEY_ENV_VAR: Final[str] = "FUND_AGENT_LLM_API_KEY"
_DEFAULT_TIMEOUT_SECONDS: Final[float] = 60.0
_DEFAULT_TIMEOUT_MAX_ATTEMPTS: Final[int] = 2
_DEFAULT_TIMEOUT_BACKOFF_SECONDS: Final[float] = 1.0
_DEFAULT_MAX_OUTPUT_CHARS: Final[int] = 12000
_MAX_TIMEOUT_SECONDS: Final[float] = 300.0
_MAX_TIMEOUT_MAX_ATTEMPTS: Final[int] = 3
_MAX_TIMEOUT_BACKOFF_SECONDS: Final[float] = 30.0
_MAX_OUTPUT_CHARS: Final[int] = 50000

_ENV_PROVIDER: Final[str] = "FUND_AGENT_LLM_PROVIDER"
_ENV_MODEL: Final[str] = "FUND_AGENT_LLM_MODEL"
_ENV_BASE_URL: Final[str] = "FUND_AGENT_LLM_BASE_URL"
_ENV_API_KEY_ENV_VAR: Final[str] = "FUND_AGENT_LLM_API_KEY_ENV_VAR"
_ENV_TIMEOUT_SECONDS: Final[str] = "FUND_AGENT_LLM_TIMEOUT_SECONDS"
_ENV_WRITER_TIMEOUT_SECONDS: Final[str] = "FUND_AGENT_LLM_WRITER_TIMEOUT_SECONDS"
_ENV_AUDITOR_TIMEOUT_SECONDS: Final[str] = "FUND_AGENT_LLM_AUDITOR_TIMEOUT_SECONDS"
_ENV_REPAIR_TIMEOUT_SECONDS: Final[str] = "FUND_AGENT_LLM_REPAIR_TIMEOUT_SECONDS"
_ENV_TIMEOUT_MAX_ATTEMPTS: Final[str] = "FUND_AGENT_LLM_TIMEOUT_MAX_ATTEMPTS"
_ENV_TIMEOUT_BACKOFF_SECONDS: Final[str] = "FUND_AGENT_LLM_TIMEOUT_BACKOFF_SECONDS"
_ENV_MAX_OUTPUT_CHARS: Final[str] = "FUND_AGENT_LLM_MAX_OUTPUT_CHARS"


class LLMProviderConfigError(ValueError):
    """LLM provider 配置错误。"""


@dataclass(frozen=True, slots=True, kw_only=True)
class LLMProviderConfig:
    """生产 LLM provider 配置，见模板第 1-6 章 LLM 写作/审计路径。

    Attributes:
        provider_name: provider 协议名，当前仅支持 `openai_compatible`。
        model: 部署方显式配置的模型名。
        base_url: OpenAI-compatible chat completions endpoint base URL。
        api_key_env_var: API key 所在环境变量名。
        api_key: API key 值；repr 中隐藏。
        timeout_seconds: 单次 HTTP 请求 timeout。
        writer_timeout_seconds: writer 初次请求 timeout；缺省回落到 `timeout_seconds`。
        auditor_timeout_seconds: auditor 请求 timeout；缺省回落到 `timeout_seconds`。
        repair_timeout_seconds: writer repair 请求 timeout；缺省回落到 writer timeout 并显式记录。
        timeout_max_attempts: 单次 provider 请求 timeout 后的最大总尝试次数，含首次请求。
        timeout_backoff_seconds: timeout retry 前等待秒数。
        max_output_chars: 本地章节输出字符上限，不是 provider token budget。
    """

    provider_name: LLMProviderName
    model: str
    base_url: str
    api_key_env_var: str
    api_key: str = field(repr=False)
    timeout_seconds: float = _DEFAULT_TIMEOUT_SECONDS
    writer_timeout_seconds: float = _DEFAULT_TIMEOUT_SECONDS
    auditor_timeout_seconds: float = _DEFAULT_TIMEOUT_SECONDS
    repair_timeout_seconds: float = _DEFAULT_TIMEOUT_SECONDS
    repair_timeout_fallback_used: bool = False
    timeout_max_attempts: int = _DEFAULT_TIMEOUT_MAX_ATTEMPTS
    timeout_backoff_seconds: float = _DEFAULT_TIMEOUT_BACKOFF_SECONDS
    max_output_chars: int = _DEFAULT_MAX_OUTPUT_CHARS


def load_llm_provider_config_from_env(
    environ: Mapping[str, str] | None = None,
) -> LLMProviderConfig:
    """从显式环境变量构造 provider config。

    Args:
        environ: 环境变量映射；`None` 时读取 `os.environ`。

    Returns:
        通过校验的 LLM provider 配置。

    Raises:
        LLMProviderConfigError: 当必需配置缺失、provider 不支持、URL 非法、
            API key 缺失或数值边界非法时抛出。
    """

    env = os.environ if environ is None else environ
    provider_name = _load_provider_name(env)
    model = _required_non_empty(env, _ENV_MODEL)
    base_url = _load_base_url(env)
    api_key_env_var = _optional_non_empty(env, _ENV_API_KEY_ENV_VAR, _DEFAULT_API_KEY_ENV_VAR)
    api_key = _load_api_key(env, api_key_env_var)
    timeout_seconds = _load_timeout_seconds(env)
    writer_timeout_seconds = _load_optional_timeout_seconds(
        env,
        _ENV_WRITER_TIMEOUT_SECONDS,
        fallback=timeout_seconds,
    )
    auditor_timeout_seconds = _load_optional_timeout_seconds(
        env,
        _ENV_AUDITOR_TIMEOUT_SECONDS,
        fallback=timeout_seconds,
    )
    repair_timeout_seconds, repair_timeout_fallback_used = _load_repair_timeout_seconds(
        env,
        fallback=writer_timeout_seconds,
    )
    timeout_max_attempts = _load_timeout_max_attempts(env)
    timeout_backoff_seconds = _load_timeout_backoff_seconds(env)
    max_output_chars = _load_max_output_chars(env)

    return LLMProviderConfig(
        provider_name=provider_name,
        model=model,
        base_url=base_url,
        api_key_env_var=api_key_env_var,
        api_key=api_key,
        timeout_seconds=timeout_seconds,
        writer_timeout_seconds=writer_timeout_seconds,
        auditor_timeout_seconds=auditor_timeout_seconds,
        repair_timeout_seconds=repair_timeout_seconds,
        repair_timeout_fallback_used=repair_timeout_fallback_used,
        timeout_max_attempts=timeout_max_attempts,
        timeout_backoff_seconds=timeout_backoff_seconds,
        max_output_chars=max_output_chars,
    )


def _load_provider_name(env: Mapping[str, str]) -> LLMProviderName:
    """读取并校验 provider 名称。

    Args:
        env: 环境变量映射。

    Returns:
        支持的 provider 名称。

    Raises:
        LLMProviderConfigError: 当 provider 缺失或不支持时抛出。
    """

    value = _required_non_empty(env, _ENV_PROVIDER)
    if value != _SUPPORTED_PROVIDER_NAME:
        raise LLMProviderConfigError(
            f"unsupported provider {value!r}; only {_SUPPORTED_PROVIDER_NAME!r} is supported"
        )
    return _SUPPORTED_PROVIDER_NAME


def _load_base_url(env: Mapping[str, str]) -> str:
    """读取并校验 provider base URL。

    Args:
        env: 环境变量映射。

    Returns:
        合法的绝对 HTTP(S) base URL。

    Raises:
        LLMProviderConfigError: 当 URL 缺失、非 HTTP(S)、缺少 host 或带 query/fragment 时抛出。
    """

    value = _required_non_empty(env, _ENV_BASE_URL)
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise LLMProviderConfigError(f"{_ENV_BASE_URL} must be an absolute http(s) URL")
    if parsed.query or parsed.fragment:
        raise LLMProviderConfigError(f"{_ENV_BASE_URL} must not include query or fragment")
    return value.rstrip("/")


def _load_api_key(env: Mapping[str, str], api_key_env_var: str) -> str:
    """读取 API key，空白值视为缺失。

    Args:
        env: 环境变量映射。
        api_key_env_var: API key 所在环境变量名。

    Returns:
        非空 API key。

    Raises:
        LLMProviderConfigError: 当 API key 缺失或为空白时抛出。
    """

    api_key = env.get(api_key_env_var)
    if api_key is None or not api_key.strip():
        raise LLMProviderConfigError(f"missing API key value in {api_key_env_var}")
    return api_key


def _load_timeout_seconds(env: Mapping[str, str]) -> float:
    """读取并校验 timeout 秒数。

    Args:
        env: 环境变量映射。

    Returns:
        合法 timeout 秒数。

    Raises:
        LLMProviderConfigError: 当 timeout 不是数字或越界时抛出。
    """

    raw_value = env.get(_ENV_TIMEOUT_SECONDS)
    if raw_value is None or not raw_value.strip():
        return _DEFAULT_TIMEOUT_SECONDS
    try:
        value = float(raw_value)
    except ValueError as exc:
        raise LLMProviderConfigError(f"{_ENV_TIMEOUT_SECONDS} must be a number") from exc
    if value <= 0 or value > _MAX_TIMEOUT_SECONDS:
        raise LLMProviderConfigError(
            f"{_ENV_TIMEOUT_SECONDS} must be greater than 0 and no more than 300"
        )
    return value


def _load_optional_timeout_seconds(
    env: Mapping[str, str],
    name: str,
    *,
    fallback: float,
) -> float:
    """读取 operation-specific timeout 秒数。

    Args:
        env: 环境变量映射。
        name: 环境变量名。
        fallback: 变量缺失时使用的 fallback timeout。

    Returns:
        合法 timeout 秒数。

    Raises:
        LLMProviderConfigError: 当 timeout 不是数字或越界时抛出。
    """

    raw_value = env.get(name)
    if raw_value is None or not raw_value.strip():
        return fallback
    try:
        value = float(raw_value)
    except ValueError as exc:
        raise LLMProviderConfigError(f"{name} must be a number") from exc
    if value <= 0 or value > _MAX_TIMEOUT_SECONDS:
        raise LLMProviderConfigError(f"{name} must be greater than 0 and no more than 300")
    return value


def _load_repair_timeout_seconds(
    env: Mapping[str, str],
    *,
    fallback: float,
) -> tuple[float, bool]:
    """读取 repair timeout，并显式返回 fallback 使用状态。

    Args:
        env: 环境变量映射。
        fallback: repair timeout 缺省时使用的 writer timeout。

    Returns:
        `(timeout_seconds, fallback_used)`。

    Raises:
        LLMProviderConfigError: 当 timeout 不是数字或越界时抛出。
    """

    raw_value = env.get(_ENV_REPAIR_TIMEOUT_SECONDS)
    if raw_value is None or not raw_value.strip():
        return fallback, True
    return (
        _load_optional_timeout_seconds(env, _ENV_REPAIR_TIMEOUT_SECONDS, fallback=fallback),
        False,
    )


def _load_timeout_max_attempts(env: Mapping[str, str]) -> int:
    """读取并校验 timeout 最大尝试次数。

    Args:
        env: 环境变量映射。

    Returns:
        合法最大尝试次数，含首次请求。

    Raises:
        LLMProviderConfigError: 当尝试次数不是整数或越界时抛出。
    """

    raw_value = env.get(_ENV_TIMEOUT_MAX_ATTEMPTS)
    if raw_value is None or not raw_value.strip():
        return _DEFAULT_TIMEOUT_MAX_ATTEMPTS
    try:
        value = int(raw_value)
    except ValueError as exc:
        raise LLMProviderConfigError(f"{_ENV_TIMEOUT_MAX_ATTEMPTS} must be an integer") from exc
    if value < 1 or value > _MAX_TIMEOUT_MAX_ATTEMPTS:
        raise LLMProviderConfigError(
            f"{_ENV_TIMEOUT_MAX_ATTEMPTS} must be at least 1 and no more than 3"
        )
    return value


def _load_timeout_backoff_seconds(env: Mapping[str, str]) -> float:
    """读取并校验 timeout retry backoff 秒数。

    Args:
        env: 环境变量映射。

    Returns:
        合法 backoff 秒数。

    Raises:
        LLMProviderConfigError: 当 backoff 不是数字或越界时抛出。
    """

    raw_value = env.get(_ENV_TIMEOUT_BACKOFF_SECONDS)
    if raw_value is None or not raw_value.strip():
        return _DEFAULT_TIMEOUT_BACKOFF_SECONDS
    try:
        value = float(raw_value)
    except ValueError as exc:
        raise LLMProviderConfigError(f"{_ENV_TIMEOUT_BACKOFF_SECONDS} must be a number") from exc
    if value < 0 or value > _MAX_TIMEOUT_BACKOFF_SECONDS:
        raise LLMProviderConfigError(
            f"{_ENV_TIMEOUT_BACKOFF_SECONDS} must be at least 0 and no more than 30"
        )
    return value


def _load_max_output_chars(env: Mapping[str, str]) -> int:
    """读取并校验本地输出字符上限。

    Args:
        env: 环境变量映射。

    Returns:
        合法字符上限。

    Raises:
        LLMProviderConfigError: 当字符上限不是整数或越界时抛出。
    """

    raw_value = env.get(_ENV_MAX_OUTPUT_CHARS)
    if raw_value is None or not raw_value.strip():
        return _DEFAULT_MAX_OUTPUT_CHARS
    try:
        value = int(raw_value)
    except ValueError as exc:
        raise LLMProviderConfigError(f"{_ENV_MAX_OUTPUT_CHARS} must be an integer") from exc
    if value <= 0 or value > _MAX_OUTPUT_CHARS:
        raise LLMProviderConfigError(
            f"{_ENV_MAX_OUTPUT_CHARS} must be greater than 0 and no more than 50000"
        )
    return value


def _required_non_empty(env: Mapping[str, str], name: str) -> str:
    """读取必需非空环境变量。

    Args:
        env: 环境变量映射。
        name: 环境变量名。

    Returns:
        去除首尾空白后的环境变量值。

    Raises:
        LLMProviderConfigError: 当环境变量缺失或为空白时抛出。
    """

    value = env.get(name)
    if value is None or not value.strip():
        raise LLMProviderConfigError(f"missing {name}")
    return value.strip()


def _optional_non_empty(env: Mapping[str, str], name: str, default: str) -> str:
    """读取可选非空环境变量。

    Args:
        env: 环境变量映射。
        name: 环境变量名。
        default: 变量缺失时使用的默认值。

    Returns:
        去除首尾空白后的配置值或默认值。

    Raises:
        LLMProviderConfigError: 当变量存在但为空白时抛出。
    """

    value = env.get(name)
    if value is None:
        return default
    if not value.strip():
        raise LLMProviderConfigError(f"{name} must not be empty")
    return value.strip()
