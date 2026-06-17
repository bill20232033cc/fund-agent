"""Fund processor registry 测试。"""

from __future__ import annotations

from dataclasses import fields

import pytest

from fund_agent.fund.processors.contracts import (
    FundProcessorDispatchKey,
    FundProcessorInput,
    FundProcessorResult,
)
from fund_agent.fund.processors.registry import (
    FundProcessorRegistry,
    UnsupportedFundProcessorError,
)


class _NeverProcessor:
    """测试用永不支持 processor。"""

    processor_id = "never"
    priority = 0
    output_schema_version = "test.v1"

    def supports(self, context: FundProcessorDispatchKey) -> bool:
        """返回不支持。

        Args:
            context: Processor 路由键。

        Returns:
            固定返回 `False`。

        Raises:
            无显式抛出。
        """

        return False

    def extract(self, input_data: FundProcessorInput) -> FundProcessorResult:
        """测试占位方法。

        Args:
            input_data: Processor 输入。

        Returns:
            不会被调用。

        Raises:
            AssertionError: 被调用时抛出。
        """

        raise AssertionError("never processor must not extract")


class _FirstProcessor(_NeverProcessor):
    """测试用第一 processor。"""

    processor_id = "first"

    def supports(self, context: FundProcessorDispatchKey) -> bool:
        """返回支持。

        Args:
            context: Processor 路由键。

        Returns:
            固定返回 `True`。

        Raises:
            无显式抛出。
        """

        return True


class _SecondProcessor(_FirstProcessor):
    """测试用第二 processor。"""

    processor_id = "second"


class _HighPriorityProcessor(_FirstProcessor):
    """测试用高优先级 processor。"""

    processor_id = "high"
    priority = 50


def _dispatch_key() -> FundProcessorDispatchKey:
    """构造默认 dispatch key。

    Args:
        无。

    Returns:
        主动基金年报 ParsedAnnualReport processor 路由键。

    Raises:
        无显式抛出。
    """

    return FundProcessorDispatchKey(
        fund_type="active_fund",
        report_type="annual_report",
        intermediate_kind="parsed_annual_report.v1",
        source_kind="annual_report",
        document_year=2024,
        fund_code="110011",
    )


def test_registry_resolves_priority_descending() -> None:
    """验证 registry 按 priority 降序解析。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当高优先级 processor 未优先返回时抛出。
    """

    registry = FundProcessorRegistry()
    registry.register(_FirstProcessor, priority=10)
    registry.register(_HighPriorityProcessor, priority=100)

    processor = registry.resolve(_dispatch_key())

    assert processor.processor_id == "high"


def test_registry_keeps_stable_tie_order() -> None:
    """验证同优先级按注册顺序稳定解析。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当同优先级排序不稳定时抛出。
    """

    registry = FundProcessorRegistry()
    registry.register(_FirstProcessor, priority=10)
    registry.register(_SecondProcessor, priority=10)

    processor = registry.resolve(_dispatch_key())

    assert processor.processor_id == "first"


def test_registry_first_supported_wins() -> None:
    """验证 registry 跳过不支持 processor 后返回第一个支持项。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 registry 没有选择第一个支持 processor 时抛出。
    """

    registry = FundProcessorRegistry()
    registry.register(_NeverProcessor, priority=100)
    registry.register(_FirstProcessor, priority=10)
    registry.register(_SecondProcessor, priority=1)

    processor = registry.resolve(_dispatch_key())

    assert processor.processor_id == "first"


def test_registry_unsupported_context_fail_closed() -> None:
    """验证没有 processor 支持时 fail-closed。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 registry 静默 fallback 时抛出。
    """

    registry = FundProcessorRegistry()
    registry.register(_NeverProcessor)

    with pytest.raises(UnsupportedFundProcessorError, match="unsupported_processor"):
        registry.resolve(_dispatch_key())


def test_registry_create_default_resolves_active_annual_processor() -> None:
    """验证默认 registry 只做纯注册并可解析主动基金年报 processor。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当默认 registry 未注册 S1 processor 时抛出。
    """

    registry = FundProcessorRegistry.create_default()

    processor = registry.resolve(_dispatch_key())

    assert processor.processor_id == "active_fund_annual.parsed_annual_report.v1"


def test_dispatch_key_rejects_invalid_values_and_has_no_extra_payload() -> None:
    """验证 dispatch key 显式参数和 no extra_payload 约束。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当非法字段未被拒绝或出现 extra_payload 时抛出。
    """

    key = _dispatch_key()

    assert "extra_payload" not in {field.name for field in fields(FundProcessorDispatchKey)}
    assert "extra_payload" not in {field.name for field in fields(FundProcessorInput)}
    assert not hasattr(key, "extra_payload")
    with pytest.raises(ValueError, match="fund_code"):
        FundProcessorDispatchKey(
            fund_type="active_fund",
            report_type="annual_report",
            intermediate_kind="parsed_annual_report.v1",
            source_kind="annual_report",
            document_year=2024,
            fund_code="11001",
        )
    with pytest.raises(ValueError, match="document_year"):
        FundProcessorDispatchKey(
            fund_type="active_fund",
            report_type="annual_report",
            intermediate_kind="parsed_annual_report.v1",
            source_kind="annual_report",
            document_year=0,
            fund_code="110011",
        )
