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
    env["FUND_AGENT_LLM_MAX_OUTPUT_CHARS"] = "34000"

    config = load_llm_provider_config_from_env(env)

    assert config.api_key_env_var == "CUSTOM_LLM_KEY"
    assert config.api_key == "custom-secret"
    assert config.timeout_seconds == 12.5
    assert config.max_output_chars == 34000
    assert "custom-secret" not in repr(config)
