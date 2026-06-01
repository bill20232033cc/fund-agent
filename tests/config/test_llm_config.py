"""LLM provider typed env config 测试。"""

import pytest

from fund_agent.config.llm import (
    LLMProviderConfigError,
    load_llm_provider_config_from_env,
)

_BASE_ENV = {
    "FUND_AGENT_LLM_PROVIDER": "openai_compatible",
    "FUND_AGENT_LLM_MODEL": "unit-model",
    "FUND_AGENT_LLM_BASE_URL": "https://llm.example.com/v1",
    "FUND_AGENT_LLM_API_KEY": "secret-value",
}


def test_load_llm_provider_config_from_env_success_and_hides_api_key() -> None:
    """验证完整 fake env 可构造配置且 repr 不泄漏 API key。"""

    config = load_llm_provider_config_from_env(dict(_BASE_ENV))

    assert config.provider_name == "openai_compatible"
    assert config.model == "unit-model"
    assert config.base_url == "https://llm.example.com/v1"
    assert config.api_key_env_var == "FUND_AGENT_LLM_API_KEY"
    assert config.api_key == "secret-value"
    assert config.timeout_seconds == 60
    assert config.writer_timeout_seconds == 60
    assert config.auditor_timeout_seconds == 60
    assert config.repair_timeout_seconds == 60
    assert config.repair_timeout_fallback_used is True
    assert config.timeout_max_attempts == 2
    assert config.timeout_backoff_seconds == 1.0
    assert config.max_output_chars == 12000
    assert "secret-value" not in repr(config)


@pytest.mark.parametrize(
    "missing_name",
    (
        "FUND_AGENT_LLM_PROVIDER",
        "FUND_AGENT_LLM_MODEL",
        "FUND_AGENT_LLM_BASE_URL",
        "FUND_AGENT_LLM_API_KEY",
    ),
)
def test_load_llm_provider_config_missing_required_values_fail(missing_name: str) -> None:
    """验证 provider/model/base_url/key 缺失时 fail-closed。"""

    env = dict(_BASE_ENV)
    env.pop(missing_name)

    with pytest.raises(LLMProviderConfigError) as exc_info:
        load_llm_provider_config_from_env(env)

    assert missing_name in str(exc_info.value)
    assert "secret-value" not in str(exc_info.value)


def test_load_llm_provider_config_unsupported_provider_fails() -> None:
    """验证非 OpenAI-compatible provider 被拒绝。"""

    env = dict(_BASE_ENV, FUND_AGENT_LLM_PROVIDER="vendor_sdk")

    with pytest.raises(LLMProviderConfigError, match="unsupported provider"):
        load_llm_provider_config_from_env(env)


@pytest.mark.parametrize(
    "base_url",
    (
        "ftp://llm.example.com/v1",
        "llm.example.com/v1",
        "https://llm.example.com/v1?tenant=abc",
        "https://llm.example.com/v1#chat",
    ),
)
def test_load_llm_provider_config_invalid_base_url_fails(base_url: str) -> None:
    """验证 base_url 必须是无 query/fragment 的绝对 HTTP(S) URL。"""

    env = dict(_BASE_ENV, FUND_AGENT_LLM_BASE_URL=base_url)

    with pytest.raises(LLMProviderConfigError):
        load_llm_provider_config_from_env(env)


@pytest.mark.parametrize("timeout", ("0", "-1", "301", "not-a-number"))
def test_load_llm_provider_config_timeout_bounds_fail(timeout: str) -> None:
    """验证 timeout 必须满足 0 < timeout <= 300。"""

    env = dict(_BASE_ENV, FUND_AGENT_LLM_TIMEOUT_SECONDS=timeout)

    with pytest.raises(LLMProviderConfigError):
        load_llm_provider_config_from_env(env)


def test_load_llm_provider_config_operation_specific_timeout_overrides() -> None:
    """验证 writer/auditor/repair timeout 可显式覆盖 legacy timeout。"""

    env = dict(
        _BASE_ENV,
        FUND_AGENT_LLM_TIMEOUT_SECONDS="50",
        FUND_AGENT_LLM_WRITER_TIMEOUT_SECONDS="90",
        FUND_AGENT_LLM_AUDITOR_TIMEOUT_SECONDS="80",
        FUND_AGENT_LLM_REPAIR_TIMEOUT_SECONDS="70",
    )

    config = load_llm_provider_config_from_env(env)

    assert config.timeout_seconds == 50
    assert config.writer_timeout_seconds == 90
    assert config.auditor_timeout_seconds == 80
    assert config.repair_timeout_seconds == 70
    assert config.repair_timeout_fallback_used is False


def test_load_llm_provider_config_repair_timeout_falls_back_to_writer_timeout() -> None:
    """验证 repair timeout 缺省时显式回落到 writer timeout。"""

    env = dict(
        _BASE_ENV,
        FUND_AGENT_LLM_TIMEOUT_SECONDS="50",
        FUND_AGENT_LLM_WRITER_TIMEOUT_SECONDS="90",
    )

    config = load_llm_provider_config_from_env(env)

    assert config.repair_timeout_seconds == 90
    assert config.repair_timeout_fallback_used is True


@pytest.mark.parametrize(
    "env_name",
    (
        "FUND_AGENT_LLM_WRITER_TIMEOUT_SECONDS",
        "FUND_AGENT_LLM_AUDITOR_TIMEOUT_SECONDS",
        "FUND_AGENT_LLM_REPAIR_TIMEOUT_SECONDS",
    ),
)
def test_load_llm_provider_config_operation_specific_timeout_bounds_fail(env_name: str) -> None:
    """验证 operation-specific timeout 继承 0 < timeout <= 300 边界。"""

    env = dict(_BASE_ENV, **{env_name: "301"})

    with pytest.raises(LLMProviderConfigError) as exc_info:
        load_llm_provider_config_from_env(env)

    assert env_name in str(exc_info.value)


@pytest.mark.parametrize("timeout_max_attempts", ("1", "3"))
def test_load_llm_provider_config_timeout_max_attempts_bounds_pass(
    timeout_max_attempts: str,
) -> None:
    """验证 timeout 最大尝试次数允许边界值。"""

    env = dict(_BASE_ENV, FUND_AGENT_LLM_TIMEOUT_MAX_ATTEMPTS=timeout_max_attempts)

    config = load_llm_provider_config_from_env(env)

    assert config.timeout_max_attempts == int(timeout_max_attempts)


@pytest.mark.parametrize("timeout_max_attempts", ("0", "4", "1.5", "not-an-int"))
def test_load_llm_provider_config_timeout_max_attempts_bounds_fail(
    timeout_max_attempts: str,
) -> None:
    """验证 timeout 最大尝试次数必须满足 1 <= attempts <= 3。"""

    env = dict(_BASE_ENV, FUND_AGENT_LLM_TIMEOUT_MAX_ATTEMPTS=timeout_max_attempts)

    with pytest.raises(LLMProviderConfigError) as exc_info:
        load_llm_provider_config_from_env(env)

    assert "FUND_AGENT_LLM_TIMEOUT_MAX_ATTEMPTS" in str(exc_info.value)
    assert "secret-value" not in str(exc_info.value)


@pytest.mark.parametrize("timeout_backoff_seconds", ("0", "30", "2.5"))
def test_load_llm_provider_config_timeout_backoff_bounds_pass(
    timeout_backoff_seconds: str,
) -> None:
    """验证 timeout backoff 允许边界值和小数。"""

    env = dict(_BASE_ENV, FUND_AGENT_LLM_TIMEOUT_BACKOFF_SECONDS=timeout_backoff_seconds)

    config = load_llm_provider_config_from_env(env)

    assert config.timeout_backoff_seconds == float(timeout_backoff_seconds)


@pytest.mark.parametrize("timeout_backoff_seconds", ("-0.1", "31", "not-a-number"))
def test_load_llm_provider_config_timeout_backoff_bounds_fail(
    timeout_backoff_seconds: str,
) -> None:
    """验证 timeout backoff 必须满足 0 <= seconds <= 30。"""

    env = dict(_BASE_ENV, FUND_AGENT_LLM_TIMEOUT_BACKOFF_SECONDS=timeout_backoff_seconds)

    with pytest.raises(LLMProviderConfigError) as exc_info:
        load_llm_provider_config_from_env(env)

    assert "FUND_AGENT_LLM_TIMEOUT_BACKOFF_SECONDS" in str(exc_info.value)
    assert "secret-value" not in str(exc_info.value)


@pytest.mark.parametrize("max_output_chars", ("0", "-1", "50001", "12.5", "not-an-int"))
def test_load_llm_provider_config_max_output_bounds_fail(max_output_chars: str) -> None:
    """验证 max_output_chars 必须满足 0 < max <= 50000。"""

    env = dict(_BASE_ENV, FUND_AGENT_LLM_MAX_OUTPUT_CHARS=max_output_chars)

    with pytest.raises(LLMProviderConfigError):
        load_llm_provider_config_from_env(env)


@pytest.mark.parametrize("api_key", ("", "   "))
def test_load_llm_provider_config_empty_api_key_fails(api_key: str) -> None:
    """验证 API key 空字符串或纯空白值视为缺失。"""

    env = dict(_BASE_ENV, FUND_AGENT_LLM_API_KEY=api_key)

    with pytest.raises(LLMProviderConfigError) as exc_info:
        load_llm_provider_config_from_env(env)

    assert "FUND_AGENT_LLM_API_KEY" in str(exc_info.value)
    assert "secret-value" not in str(exc_info.value)


def test_load_llm_provider_config_custom_api_key_env_var() -> None:
    """验证 API key env var 名可显式配置。"""

    env = dict(_BASE_ENV)
    env.pop("FUND_AGENT_LLM_API_KEY")
    env["FUND_AGENT_LLM_API_KEY_ENV_VAR"] = "CUSTOM_LLM_KEY"
    env["CUSTOM_LLM_KEY"] = "custom-secret"
    env["FUND_AGENT_LLM_TIMEOUT_SECONDS"] = "12.5"
    env["FUND_AGENT_LLM_TIMEOUT_MAX_ATTEMPTS"] = "3"
    env["FUND_AGENT_LLM_TIMEOUT_BACKOFF_SECONDS"] = "0"
    env["FUND_AGENT_LLM_MAX_OUTPUT_CHARS"] = "34000"

    config = load_llm_provider_config_from_env(env)

    assert config.api_key_env_var == "CUSTOM_LLM_KEY"
    assert config.api_key == "custom-secret"
    assert config.timeout_seconds == 12.5
    assert config.timeout_max_attempts == 3
    assert config.timeout_backoff_seconds == 0
    assert config.max_output_chars == 34000
    assert "custom-secret" not in repr(config)
