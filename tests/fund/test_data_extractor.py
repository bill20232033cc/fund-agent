"""P1 结构化数据 façade 测试。"""

from __future__ import annotations

import pytest

from fund_agent.fund.data.nav_data import NavDataResult
from fund_agent.fund.data_extractor import FundDataExtractor, StructuredFundDataBundle
from fund_agent.fund.documents.models import (
    AnnualReportMetadata,
    AnnualReportSourceMetadata,
    DocumentKey,
    ParsedAnnualReport,
)
from fund_agent.fund.extractors import ExtractedField
from fund_agent.fund.extractors import bond_risk_evidence as bond_risk_module


class _FakeRepository:
    """测试用年报仓库。"""

    def __init__(self, result: ParsedAnnualReport | Exception) -> None:
        """初始化测试仓库。

        Args:
            result: 预置年报或待抛异常。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self.result = result
        self.calls: list[tuple[str, int, bool]] = []

    async def load_annual_report(
        self,
        fund_code: str,
        year: int,
        *,
        force_refresh: bool = False,
    ) -> ParsedAnnualReport:
        """返回预置年报或抛出预置异常。

        Args:
            fund_code: 基金代码。
            year: 年报年份。
            force_refresh: 是否强制刷新。

        Returns:
            预置年报。

        Raises:
            Exception: 当初始化传入异常时抛出。
        """

        self.calls.append((fund_code, year, force_refresh))
        if isinstance(self.result, Exception):
            raise self.result
        return self.result


class _FailingNavProvider:
    """测试用失败净值 provider。"""

    def __init__(self) -> None:
        """初始化测试 provider。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self.calls: list[tuple[str, bool]] = []

    async def load_nav_data(self, fund_code: str, *, force_refresh: bool = False) -> NavDataResult:
        """记录调用并模拟外部净值失败。

        Args:
            fund_code: 基金代码。
            force_refresh: 是否强制刷新。

        Returns:
            无返回值。

        Raises:
            RuntimeError: 始终抛出网络失败。
        """

        self.calls.append((fund_code, force_refresh))
        raise RuntimeError("network down")


class _RecordingNavProvider:
    """测试用记录调用的净值 provider。"""

    def __init__(self) -> None:
        """初始化测试 provider。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self.calls: list[tuple[str, bool]] = []

    async def load_nav_data(self, fund_code: str, *, force_refresh: bool = False) -> NavDataResult:
        """记录调用并返回空净值数据。

        Args:
            fund_code: 基金代码。
            force_refresh: 是否强制刷新。

        Returns:
            空净值数据。

        Raises:
            无显式抛出。
        """

        self.calls.append((fund_code, force_refresh))
        return NavDataResult(fund_code=fund_code, records=[], source="fixture", cached=False)


@pytest.mark.asyncio
async def test_data_extractor_degrades_nav_failure_without_blocking_annual_report() -> None:
    """验证 NAV 外部失败不会阻断年报结构化抽取。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 NAV 失败阻断年报抽取或原因丢失时抛出。
    """

    repository = _FakeRepository(_annual_report())
    nav_provider = _FailingNavProvider()
    extractor = FundDataExtractor(repository=repository, nav_provider=nav_provider)

    bundle = await extractor.extract("110011", 2024, force_refresh=True)

    assert repository.calls == [("110011", 2024, True)]
    assert nav_provider.calls == [("110011", True)]
    assert bundle.fund_code == "110011"
    assert bundle.basic_identity.value is not None
    assert bundle.nav_data.records == []
    assert bundle.nav_data.source == "nav_unavailable"
    assert bundle.nav_data.cached is False
    assert bundle.nav_data.unavailable is True
    assert bundle.nav_data.unavailable_reason == "RuntimeError: network down"
    assert bundle.source_provenance.fallback_eligibility == "not_applicable"
    assert bundle.source_provenance.source_provenance_status == "not_applicable"
    assert bundle.bond_risk_evidence.value is None
    assert bundle.bond_risk_evidence.extraction_mode == "missing"
    assert bundle.bond_risk_evidence.note == "not_applicable_non_bond_fund"


@pytest.mark.asyncio
async def test_data_extractor_does_not_mask_repository_failure() -> None:
    """验证年报仓库失败不会被 NAV 降级吞掉。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当仓库异常被误吞或 NAV 被误调用时抛出。
    """

    repository = _FakeRepository(RuntimeError("identity_mismatch fixture"))
    nav_provider = _RecordingNavProvider()
    extractor = FundDataExtractor(repository=repository, nav_provider=nav_provider)

    with pytest.raises(RuntimeError, match="identity_mismatch fixture"):
        await extractor.extract("110011", 2024, force_refresh=True)

    assert repository.calls == [("110011", 2024, True)]
    assert nav_provider.calls == []


def test_structured_bundle_default_source_provenance_is_not_none() -> None:
    """验证 fake bundle 未显式传 provenance 时使用安全默认值。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 bundle provenance 为 `None` 或非 not_applicable 时抛出。
    """

    report = _annual_report()
    bundle = StructuredFundDataBundle(
        fund_code=report.key.fund_code,
        report_year=report.key.year,
        basic_identity=_fake_field(),
        product_profile=_fake_field(),
        benchmark=_fake_field(),
        index_profile=_fake_field(),
        fee_schedule=_fake_field(),
        turnover_rate=_fake_field(),
        nav_benchmark_performance=_fake_field(),
        investor_return=_fake_field(),
        tracking_error=_fake_field(),
        share_change=_fake_field(),
        manager_alignment=_fake_field(),
        manager_strategy_text=_fake_field(),
        holdings_snapshot=_fake_field(),
        holder_structure=_fake_field(),
        nav_data=NavDataResult(fund_code="110011", records=[], source="fixture", cached=False),
    )

    assert bundle.source_provenance is not None
    assert bundle.source_provenance.fallback_used is False
    assert bundle.source_provenance.fallback_eligibility == "not_applicable"
    assert bundle.source_provenance.source_provenance_status == "not_applicable"
    assert bundle.bond_risk_evidence.value is None
    assert bundle.bond_risk_evidence.note == "bond_risk_evidence_not_extracted"


@pytest.mark.asyncio
async def test_data_extractor_returns_bundle_with_bond_risk_evidence() -> None:
    """验证 fake 仓库抽取结果显式携带债券风险证据字段。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 bundle 未携带债券风险证据字段或 provenance 行为改变时抛出。
    """

    repository = _FakeRepository(_annual_report())
    nav_provider = _RecordingNavProvider()
    extractor = FundDataExtractor(repository=repository, nav_provider=nav_provider)

    bundle = await extractor.extract("110011", 2024)

    assert repository.calls == [("110011", 2024, False)]
    assert nav_provider.calls == [("110011", False)]
    assert bundle.bond_risk_evidence.value is None
    assert bundle.bond_risk_evidence.anchors == ()
    assert bundle.bond_risk_evidence.extraction_mode == "missing"
    assert bundle.bond_risk_evidence.note == "not_applicable_non_bond_fund"
    assert bundle.source_provenance.fallback_used is False
    assert bundle.source_provenance.fallback_eligibility == "not_applicable"
    assert bundle.source_provenance.source_provenance_status == "not_applicable"


@pytest.mark.asyncio
async def test_data_extractor_non_bond_bond_risk_evidence_does_not_scan_groups(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """验证非债券基金通过显式分类早退，不扫描模板第 6 章七组债券风险证据。

    Args:
        monkeypatch: pytest 局部 monkeypatch 工具。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当非债券路径扫描七组 extractor 或产生满足组时抛出。
    """

    def _fail_group_scan(_report: ParsedAnnualReport) -> object:
        """非债券路径若触发七组扫描则使测试失败。

        Args:
            _report: 已解析年报。

        Returns:
            无返回值。

        Raises:
            AssertionError: 始终抛出，表示不应扫描七组债券风险证据。
        """

        raise AssertionError("non-bond path must not scan bond evidence groups")

    monkeypatch.setattr(bond_risk_module, "_extract_duration_rate_risk", _fail_group_scan)
    extractor = FundDataExtractor(
        repository=_FakeRepository(_annual_report()),
        nav_provider=_RecordingNavProvider(),
    )

    bundle = await extractor.extract("110011", 2024)

    assert bundle.basic_identity.value is not None
    assert bundle.basic_identity.value["classified_fund_type"] == "active_fund"
    assert bundle.bond_risk_evidence.value is None
    assert bundle.bond_risk_evidence.anchors == ()
    assert bundle.bond_risk_evidence.extraction_mode == "missing"
    assert bundle.bond_risk_evidence.note == "not_applicable_non_bond_fund"


@pytest.mark.asyncio
async def test_data_extractor_projects_primary_source_metadata() -> None:
    """验证生产 extractor 从年报元数据投影主源 provenance。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当生产路径没有读取 `ParsedAnnualReport.metadata.source` 时抛出。
    """

    repository = _FakeRepository(
        _annual_report(
            source_metadata=AnnualReportSourceMetadata(source="eid", fallback_used=False)
        )
    )
    extractor = FundDataExtractor(repository=repository, nav_provider=_RecordingNavProvider())

    bundle = await extractor.extract("110011", 2024)

    assert bundle.source_provenance.resolved_source_name == "eid"
    assert bundle.source_provenance.fallback_used is False
    assert bundle.source_provenance.fallback_eligibility == "not_applicable"
    assert bundle.source_provenance.source_provenance_status == "not_applicable"


@pytest.mark.asyncio
async def test_data_extractor_projects_fallback_metadata_as_unknown_when_category_absent() -> None:
    """验证生产 extractor 对缺少失败分类的 fallback 保持 unknown。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当缺少失败分类的 fallback 被推断为 eligible 时抛出。
    """

    repository = _FakeRepository(
        _annual_report(
            source_metadata=AnnualReportSourceMetadata(source="eastmoney", fallback_used=True)
        )
    )
    extractor = FundDataExtractor(repository=repository, nav_provider=_RecordingNavProvider())

    bundle = await extractor.extract("110011", 2024)

    assert bundle.source_provenance.resolved_source_name == "eastmoney"
    assert bundle.source_provenance.fallback_used is True
    assert bundle.source_provenance.primary_failure_category is None
    assert bundle.source_provenance.fallback_eligibility == "unknown_public_metadata_absent"
    assert bundle.source_provenance.source_provenance_status == "incomplete"


@pytest.mark.asyncio
async def test_data_extractor_projects_metadata_primary_failure_category() -> None:
    """验证生产 extractor 使用年报来源元数据中的主源失败分类。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当生产投影没有消费 metadata 分类时抛出。
    """

    repository = _FakeRepository(
        _annual_report(
            source_metadata=AnnualReportSourceMetadata(
                source="eastmoney",
                fallback_used=True,
                primary_failure_category="not_found",
            )
        )
    )
    extractor = FundDataExtractor(repository=repository, nav_provider=_RecordingNavProvider())

    bundle = await extractor.extract("110011", 2024)

    assert bundle.source_provenance.resolved_source_name == "eastmoney"
    assert bundle.source_provenance.fallback_used is True
    assert bundle.source_provenance.primary_failure_category == "not_found"
    assert bundle.source_provenance.fallback_eligibility == "eligible"
    assert bundle.source_provenance.source_provenance_status == "complete"


def _annual_report(
    *,
    source_metadata: AnnualReportSourceMetadata | None = None,
) -> ParsedAnnualReport:
    """构造可被当前 extractor 解析的最小年报。

    Args:
        source_metadata: 可选年报来源元数据。

    Returns:
        最小年报解析结果。

    Raises:
        无显式抛出。
    """

    raw_text = "\n".join(
        [
            "基金名称：测试成长基金",
            "基金代码：110011",
            "基金类别：混合型",
            "管理人：测试基金管理有限公司",
            "托管人：中国银行股份有限公司",
            "基金合同生效日：2020年1月1日",
            "投资目标：追求长期资本增值",
            "投资范围：主要投资股票和债券",
            "业绩比较基准：沪深300指数收益率",
            "管理费率：1.20%",
            "托管费率：0.20%",
            "基金净值增长率：10.00%",
            "业绩比较基准收益率：5.00%",
            "投资者收益率：12.00%",
            "4.4 报告期内基金投资策略和运作分析",
            "长期均衡配置消费和制造行业。",
            "4.5 管理人对宏观经济、证券市场及行业走势的简要展望",
            "保持审慎。",
            "换手率：80.00%",
            "基金经理持有本基金：0份",
            "从业人员持有本基金：100份",
            "机构投资者持有比例：30%",
            "个人投资者持有比例：70%",
            "期初份额：100",
            "期末份额：110",
            "净变动：10",
        ]
    )
    return ParsedAnnualReport(
        key=DocumentKey(fund_code="110011", year=2024),
        raw_text=raw_text,
        sections={},
        tables=(),
        metadata=AnnualReportMetadata(source=source_metadata),
    )


def _fake_field() -> ExtractedField[dict[str, object]]:
    """构造 bundle 默认 provenance 测试用最小字段。

    Args:
        无。

    Returns:
        当前测试不读取内容的字段对象。

    Raises:
        无显式抛出。
    """

    return ExtractedField(value={}, anchors=(), extraction_mode="missing")
