"""P1 结构化数据样本矩阵测试。"""

from __future__ import annotations

from dataclasses import fields

import pytest

from fund_agent.fund.data.nav_data import NavDataResult
from fund_agent.fund.data_extractor import FundDataExtractor, StructuredFundDataBundle
from fund_agent.fund.documents.models import DocumentKey, ParsedAnnualReport, ParsedTable, ReportSection

_SAMPLE_FUNDS: tuple[tuple[str, str], ...] = (
    ("110011", "主动权益"),
    ("510300", "宽基指数"),
    ("000171", "偏债混合"),
)

_MATRIX_FIELD_NAMES: tuple[str, ...] = (
    "basic_identity",
    "product_profile",
    "benchmark",
    "index_profile",
    "fee_schedule",
    "turnover_rate",
    "nav_benchmark_performance",
    "investor_return",
    "tracking_error",
    "share_change",
    "manager_alignment",
    "manager_strategy_text",
    "holdings_snapshot",
    "holder_structure",
)


class _FakeRepository:
    """集成测试用年报仓库。"""

    def __init__(self, reports: dict[str, ParsedAnnualReport]) -> None:
        """初始化 fake repository。

        Args:
            reports: 基金代码到年报对象的映射。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self.reports = reports
        self.calls: list[tuple[str, int, bool]] = []

    async def load_annual_report(
        self,
        fund_code: str,
        year: int,
        *,
        force_refresh: bool = False,
    ) -> ParsedAnnualReport:
        """加载 fake 年报。

        Args:
            fund_code: 基金代码。
            year: 年报年份。
            force_refresh: 是否强制刷新。

        Returns:
            fake 年报对象。

        Raises:
            KeyError: 基金代码不存在时抛出。
        """

        self.calls.append((fund_code, year, force_refresh))
        return self.reports[fund_code]


class _FakeNavProvider:
    """集成测试用净值数据提供者。"""

    def __init__(self) -> None:
        """初始化 fake nav provider。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self.calls: list[tuple[str, bool]] = []

    async def load_nav_data(self, fund_code: str, *, force_refresh: bool = False) -> NavDataResult:
        """加载 fake 净值数据。

        Args:
            fund_code: 基金代码。
            force_refresh: 是否强制刷新。

        Returns:
            fake 净值数据。

        Raises:
            无显式抛出。
        """

        self.calls.append((fund_code, force_refresh))
        return NavDataResult(
            fund_code=fund_code,
            records=[{"date": "2024-12-31", "nav": "1.2345"}],
            source="fake",
            cached=False,
        )


def _build_report(fund_code: str, fund_category: str) -> ParsedAnnualReport:
    """构造覆盖 12 项结构化数据的 fake 年报。

    Args:
        fund_code: 基金代码。
        fund_category: 基金类型文本。

    Returns:
        fake 年报对象。

    Raises:
        ValueError: 章节标题缺失时抛出。
    """

    raw_text = "\n".join(
        (
            "§1 基金简介",
            f"基金名称：样本基金{fund_code}",
            f"基金代码：{fund_code}",
            f"基金类别：{fund_category}",
            "基金规模：10.00亿元",
            "基金经理：测试经理",
            "§2 基金简介",
            "投资目标：追求长期稳健回报。",
            "投资范围：依法投资于基金合同允许的资产。",
            "投资策略：坚持分散配置。",
            "业绩比较基准：沪深300指数收益率×80%＋中债综合指数收益率×20%",
            "管理费率：1.20%/年",
            "托管费率：0.20%/年",
            "§3 主要财务指标、基金净值表现及利润分配情况",
            "基金份额净值增长率：12.34%",
            "业绩比较基准收益率：10.01%",
            "加权平均投资者收益率：8.88%",
            "报告期年化跟踪误差：1.23%",
            "§4 管理人报告",
            "投资策略：本基金报告期内保持均衡配置。",
            "风格定位：均衡偏价值。",
            "后市展望：继续关注基本面质量。",
            "§8 投资组合报告",
            "股票换手率：123.45%",
            "换手率口径：买卖股票成交总额除以期初期末平均股票资产。",
            "§9 基金份额持有人信息",
            "基金经理持有本基金：1.00万份",
            "从业人员持有本基金：2.00万份",
            "机构投资者持有比例：30.00%",
            "个人投资者持有比例：70.00%",
            "§10 基金份额变动",
            "份额变动表见下表。",
        )
    )
    section_ids = ("§1", "§2", "§3", "§4", "§8", "§9", "§10")
    sections: dict[str, ReportSection] = {}
    for index, section_id in enumerate(section_ids):
        start_offset = raw_text.index(section_id)
        end_offset = raw_text.index(section_ids[index + 1]) if index + 1 < len(section_ids) else len(raw_text)
        sections[section_id] = ReportSection(
            section_id=section_id,
            title=raw_text[start_offset: raw_text.index("\n", start_offset)],
            start_offset=start_offset,
            end_offset=end_offset,
            matched_rule="fixture",
            confidence=1.0,
        )

    return ParsedAnnualReport(
        key=DocumentKey(fund_code=fund_code, year=2024),
        raw_text=raw_text,
        sections=sections,
        tables=(
            ParsedTable(
                page_number=42,
                table_index=0,
                headers=("序号", "股票名称", "占基金资产净值比例", "前十大重仓"),
                rows=(("1", "贵州茅台", "8.00%", "前十大重仓"),),
            ),
            ParsedTable(
                page_number=43,
                table_index=1,
                headers=("行业", "占比"),
                rows=(("制造业", "55.00%"),),
            ),
            ParsedTable(
                page_number=58,
                table_index=0,
                headers=("项目", "份额"),
                rows=(
                    ("期初基金份额总额", "1,000,000.00"),
                    ("期末基金份额总额", "900,000.00"),
                    ("本期申购赎回净额", "-100,000.00"),
                ),
            ),
        ),
    )


def _assert_bundle_shape(bundle: StructuredFundDataBundle) -> None:
    """验证 bundle 字段集合保持稳定。

    Args:
        bundle: P1 结构化数据包。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当字段集合不符合契约时抛出。
    """

    field_names = {field.name for field in fields(bundle)}
    assert {
        "fund_code",
        "report_year",
        "nav_data",
        *_MATRIX_FIELD_NAMES,
    } <= field_names


@pytest.mark.asyncio
async def test_p1_sample_matrix_outputs_applicable_fields_without_source_leakage() -> None:
    """验证 3 只样本基金的结构化矩阵保持可用且不越过注入边界。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当矩阵通过数不足或 façade 越过注入边界时抛出。
    """

    reports = {
        fund_code: _build_report(fund_code, fund_category)
        for fund_code, fund_category in _SAMPLE_FUNDS
    }
    repository = _FakeRepository(reports)
    nav_provider = _FakeNavProvider()
    extractor = FundDataExtractor(repository=repository, nav_provider=nav_provider)

    bundles = [
        await extractor.extract(fund_code, 2024, force_refresh=True)
        for fund_code, _fund_category in _SAMPLE_FUNDS
    ]

    passed_cells = 0
    for bundle in bundles:
        _assert_bundle_shape(bundle)
        for field_name in _MATRIX_FIELD_NAMES:
            extracted_field = getattr(bundle, field_name)
            if extracted_field.extraction_mode in {"direct", "estimated", "derived"}:
                passed_cells += 1

    assert passed_cells == 38
    bundles_by_code = {bundle.fund_code: bundle for bundle in bundles}
    assert bundles_by_code["510300"].tracking_error.extraction_mode == "direct"
    assert bundles_by_code["110011"].tracking_error.extraction_mode == "missing"
    assert bundles_by_code["000171"].tracking_error.extraction_mode == "missing"
    assert repository.calls == [
        ("110011", 2024, True),
        ("510300", 2024, True),
        ("000171", 2024, True),
    ]
    assert nav_provider.calls == [
        ("110011", True),
        ("510300", True),
        ("000171", True),
    ]
