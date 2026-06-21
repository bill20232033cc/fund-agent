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


def _fund_disclosure_dispatch_key(fund_type: str = "active_fund") -> FundProcessorDispatchKey:
    """构造 FundDisclosureDocument 中间态 dispatch key。

    Args:
        无。

    Returns:
        指定基金类型的年报 FundDisclosureDocument processor 路由键。

    Raises:
        无显式抛出。
    """

    return FundProcessorDispatchKey(
        fund_type=fund_type,
        report_type="annual_report",
        intermediate_kind="fund_disclosure_document.v1",
        source_kind="annual_report",
        document_year=2024,
        fund_code="110011",
    )


def _parsed_annual_dispatch_key(fund_type: str) -> FundProcessorDispatchKey:
    """构造指定基金类型的 ParsedAnnualReport dispatch key。

    Args:
        fund_type: 标准基金类型。

    Returns:
        对应基金类型的年报 ParsedAnnualReport processor 路由键。

    Raises:
        无显式抛出。
    """

    return FundProcessorDispatchKey(
        fund_type=fund_type,  # type: ignore[arg-type]
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


def test_registry_create_default_resolves_non_active_parsed_annual_processors() -> None:
    """验证默认 registry 按基金类型解析五类非 active ParsedAnnualReport processor。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当任一非 active 类型缺少默认 processor 时抛出。
    """

    registry = FundProcessorRegistry.create_default()

    expected_processor_ids = {
        "index_fund": "index_fund_annual.parsed_annual_report.v1",
        "enhanced_index": "enhanced_index_annual.parsed_annual_report.v1",
        "bond_fund": "bond_fund_annual.parsed_annual_report.v1",
        "qdii_fund": "qdii_fund_annual.parsed_annual_report.v1",
        "fof_fund": "fof_fund_annual.parsed_annual_report.v1",
    }
    for fund_type, expected_processor_id in expected_processor_ids.items():
        processor = registry.resolve(_parsed_annual_dispatch_key(fund_type))

        assert processor.processor_id == expected_processor_id


def test_registry_default_supports_fund_disclosure_document_intermediate() -> None:
    """验证默认 registry 已注册 active FundDisclosureDocumentProcessor。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当默认 registry 未注册 S4 processor 时抛出。
    """

    registry = FundProcessorRegistry.create_default()

    processor = registry.resolve(_fund_disclosure_dispatch_key())

    assert processor.processor_id == "active_fund_disclosure.fund_disclosure_document.v1"


def test_registry_create_default_resolves_non_active_fund_disclosure_processors() -> None:
    """验证默认 registry 按基金类型解析五类非 active FDD processor。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当任一非 active FDD processor 缺失时抛出。
    """

    registry = FundProcessorRegistry.create_default()

    expected_processor_ids = {
        "index_fund": "index_fund_disclosure.fund_disclosure_document.v1",
        "enhanced_index": "enhanced_index_disclosure.fund_disclosure_document.v1",
        "bond_fund": "bond_fund_disclosure.fund_disclosure_document.v1",
        "qdii_fund": "qdii_fund_disclosure.fund_disclosure_document.v1",
        "fof_fund": "fof_fund_disclosure.fund_disclosure_document.v1",
    }
    for fund_type, expected_processor_id in expected_processor_ids.items():
        processor = registry.resolve(_fund_disclosure_dispatch_key(fund_type))

        assert processor.processor_id == expected_processor_id


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
