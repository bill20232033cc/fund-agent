"""P3 CLI 端到端样本矩阵测试。"""

from __future__ import annotations

from dataclasses import dataclass

from typer.testing import CliRunner

from fund_agent.fund.data.nav_data import NavDataResult
from fund_agent.fund.data_extractor import FundDataExtractor
from fund_agent.fund.documents.models import DocumentKey, ParsedAnnualReport, ParsedTable, ReportSection
from fund_agent.services import FundAnalysisRequest, FundAnalysisResult, FundAnalysisService
from fund_agent.ui import cli


@dataclass(frozen=True, slots=True)
class _SampleFundCase:
    """P3 样本基金测试用例。

    Attributes:
        fund_code: 基金代码。
        fund_name: 基金全称。
        short_name: 基金简称。
        expected_type: 期望识别出的基金类型。
        objective: 投资目标。
        scope: 投资范围。
        strategy: 投资策略。
        benchmark: 业绩比较基准。
        management_fee: 管理费率。
        custody_fee: 托管费率。
        category: 可选基金类别。
        cli_args: 除基金代码外的 CLI 显式参数。
    """

    fund_code: str
    fund_name: str
    short_name: str
    expected_type: str
    objective: str
    scope: str
    strategy: str
    benchmark: str
    management_fee: str
    custody_fee: str
    category: str | None
    cli_args: tuple[str, ...]


class _FakeRepository:
    """P3 CLI 测试用统一年报仓库。"""

    def __init__(self, reports: dict[str, ParsedAnnualReport]) -> None:
        """初始化 fake repository。

        Args:
            reports: 基金代码到 fake 年报的映射。

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
    """P3 CLI 测试用净值数据提供者。"""

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
            source="p3-cli-fixture",
            cached=False,
        )


class _RecordingService:
    """P3 CLI 测试用 Service 代理，记录真实 Service 返回值。"""

    def __init__(self, service: FundAnalysisService) -> None:
        """初始化记录代理。

        Args:
            service: 真实基金分析 Service。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self._service = service
        self.results: list[FundAnalysisResult] = []

    async def analyze(self, request: FundAnalysisRequest) -> FundAnalysisResult:
        """调用真实 Service 并记录结果。

        Args:
            request: CLI 组装出的显式分析请求。

        Returns:
            真实 Service 返回值。

        Raises:
            Exception: 允许真实 Service 传播分析或审计异常。
        """

        result = await self._service.analyze(request)
        self.results.append(result)
        return result


_SAMPLE_CASES: tuple[_SampleFundCase, ...] = (
    _SampleFundCase(
        fund_code="110011",
        fund_name="易方达优质精选混合型证券投资基金",
        short_name="易方达优质精选混合（QDII）",
        expected_type="qdii_fund",
        objective="精选内地与境外市场优质企业，追求长期资本增值。",
        scope="本基金可投资于境内和境外证券市场。",
        strategy="保持均衡配置，重点关注消费、制造和港股优质企业。",
        benchmark="沪深300指数收益率×50%+中证香港300指数收益率×30%+中债总指数收益率×20%",
        management_fee="1.50%",
        custody_fee="0.25%",
        category=None,
        cli_args=(
            "--report-year",
            "2024",
            "--dev-override",
            "--equity-position",
            "80%",
            "--actual-style",
            "均衡",
            "--actual-equity-position",
            "70%",
            "--manager-tenure-months",
            "24",
            "--peer-fee-median",
            "1.00%",
            "--investment-amount",
            "10000",
            "--max-tolerable-loss-rate",
            "50%",
            "--valuation-state",
            "low",
            "--user-money-horizon-years",
            "4",
            "--current-stage",
            "估值较低但需继续跟踪境外市场波动。",
            "--quality-gate-policy",
            "off",
            "--force-refresh",
        ),
    ),
    _SampleFundCase(
        fund_code="510300",
        fund_name="华泰柏瑞沪深300交易型开放式指数证券投资基金",
        short_name="华泰柏瑞沪深300ETF",
        expected_type="index_fund",
        objective="紧密跟踪标的指数表现，追求跟踪偏离度和跟踪误差最小化。",
        scope="主要投资于沪深300指数成份股和备选成份股。",
        strategy="采用完全复制法跟踪沪深300指数。",
        benchmark="沪深300指数",
        management_fee="0.50%",
        custody_fee="0.10%",
        category=None,
        cli_args=(
            "--report-year",
            "2024",
            "--dev-override",
            "--equity-position",
            "100%",
            "--actual-style",
            "指数复制",
            "--actual-equity-position",
            "95%",
            "--manager-tenure-months",
            "24",
            "--peer-fee-median",
            "0.60%",
            "--tracking-error",
            "1.00%",
            "--investment-amount",
            "10000",
            "--max-tolerable-loss-rate",
            "40%",
            "--valuation-state",
            "fair",
            "--user-money-horizon-years",
            "4",
            "--current-stage",
            "宽基指数处于可持续跟踪阶段。",
            "--quality-gate-policy",
            "off",
            "--force-refresh",
        ),
    ),
    _SampleFundCase(
        fund_code="000171",
        fund_name="易方达裕丰回报债券型证券投资基金",
        short_name="易方达裕丰回报债券A",
        expected_type="bond_fund",
        objective="主要投资于债券资产，力争获得稳健回报。",
        scope="本基金主要投资于债券资产，可少量投资股票。",
        strategy="以债券配置为主，适度参与权益资产增强收益。",
        benchmark="中债新综合财富指数收益率*90%+沪深300指数收益率*10%",
        management_fee="0.70%",
        custody_fee="0.20%",
        category=None,
        cli_args=(
            "--report-year",
            "2024",
            "--dev-override",
            "--equity-position",
            "20%",
            "--actual-style",
            "偏债稳健",
            "--actual-equity-position",
            "20%",
            "--manager-tenure-months",
            "24",
            "--peer-fee-median",
            "0.80%",
            "--investment-amount",
            "10000",
            "--max-tolerable-loss-rate",
            "20%",
            "--valuation-state",
            "fair",
            "--user-money-horizon-years",
            "3",
            "--current-stage",
            "债券底仓稳定，权益增强贡献需持续验证。",
            "--quality-gate-policy",
            "off",
            "--force-refresh",
        ),
    ),
)

_EXPECTED_APPENDIX_EVIDENCE_FRAGMENTS: tuple[str, ...] = (
    "年报2024§2表page-5-table-0行fund_name",
    "年报2024§2表page-5-table-1行investment_objective",
    "年报2024§2表page-5-table-1行investment_scope",
    "年报2024§2表page-5-table-1行benchmark",
    "年报2024§3表未定位行nav_growth_rate",
    "年报2024§3表未定位行investor_return_rate",
    "年报2024§4表未定位行strategy_summary",
    "年报2024§8表page-42-table-0行top_holdings",
    "年报2024§8表page-43-table-1行industry_distribution",
    "年报2024§9表未定位行manager_holding",
    "年报2024§10表page-58-table-0行share_change",
)


def _build_report(case: _SampleFundCase) -> ParsedAnnualReport:
    """构造覆盖 P3 CLI 端到端路径的 fake 年报。

    Args:
        case: 样本基金用例。

    Returns:
        fake 年报对象。

    Raises:
        ValueError: 当章节标题未找到时抛出。
    """

    raw_text = "\n".join(
        (
            "§1 基金简介",
            f"基金代码：{case.fund_code}",
            "§2 基金简介",
            "本章真实字段主要位于表格。",
            "§3 主要财务指标、基金净值表现及利润分配情况",
            "基金份额净值增长率：12.34%",
            "业绩比较基准收益率：10.01%",
            "加权平均投资者收益率：13.88%",
            "§4 管理人报告",
            "投资策略：本基金报告期内保持均衡配置，长期关注消费和制造行业。",
            "风格定位：均衡优质。",
            "后市展望：继续关注基本面质量。",
            "§8 投资组合报告",
            "股票换手率：80.00%",
            "换手率口径：买卖股票成交总额除以期初期末平均股票资产。",
            "§9 基金份额持有人信息",
            "基金经理持有本基金：1.00万份",
            "从业人员持有本基金：2.00万份",
            "机构投资者持有比例：30.00%",
            "个人投资者持有比例：70.00%",
            "§10 基金份额变动",
            "份额变动表见下表。",
            "P3 CLI 样本正文" * 100,
        )
    )
    return ParsedAnnualReport(
        key=DocumentKey(fund_code=case.fund_code, year=2024),
        raw_text=raw_text,
        sections=_build_sections(raw_text),
        tables=(
            _profile_table(case),
            _product_table(case),
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
                rows=(("消费", "35.00%"), ("制造业", "30.00%")),
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


def _build_sections(raw_text: str) -> dict[str, ReportSection]:
    """根据固定章节标题构造章节索引。

    Args:
        raw_text: fake 年报全文。

    Returns:
        章节编号到章节索引的映射。

    Raises:
        ValueError: 章节标题不存在时抛出。
    """

    section_ids = ("§1", "§2", "§3", "§4", "§8", "§9", "§10")
    return {
        section_id: ReportSection(
            section_id=section_id,
            title=section_id,
            start_offset=raw_text.index(section_id),
            end_offset=raw_text.index(section_ids[index + 1]) if index + 1 < len(section_ids) else len(raw_text),
            matched_rule="fixture",
            confidence=1.0,
        )
        for index, section_id in enumerate(section_ids)
    }


def _profile_table(case: _SampleFundCase) -> ParsedTable:
    """构造 `§2` 基金身份键值表。

    Args:
        case: 样本基金用例。

    Returns:
        基金身份表。

    Raises:
        无显式抛出。
    """

    rows = [
        ("基金简称", case.short_name),
        ("基金主代码", case.fund_code),
        ("报告期末基金份额总额", "10.00亿元"),
        ("基金管理人", "样本基金管理有限公司"),
    ]
    if case.category is not None:
        rows.append(("基金类别", case.category))
    return ParsedTable(
        page_number=5,
        table_index=0,
        headers=("基金名称", case.fund_name),
        rows=tuple(rows),
    )


def _product_table(case: _SampleFundCase) -> ParsedTable:
    """构造 `§2` 产品本质键值表。

    Args:
        case: 样本基金用例。

    Returns:
        产品本质表。

    Raises:
        无显式抛出。
    """

    return ParsedTable(
        page_number=5,
        table_index=1,
        headers=("投资目标", case.objective),
        rows=(
            ("投资范围", case.scope),
            ("投资策略", case.strategy),
            ("业绩比较基准", case.benchmark),
            ("管理费率", case.management_fee),
            ("托管费率", case.custody_fee),
        ),
    )


def _body_evidence_lines(report_markdown: str) -> tuple[str, ...]:
    """提取报告正文证据行。

    Args:
        report_markdown: CLI 输出的 Markdown 报告。

    Returns:
        正文中以统一证据标记开头的行。

    Raises:
        无显式抛出。
    """

    return tuple(line for line in report_markdown.splitlines() if line.startswith("> 📎 证据："))


def _appendix_evidence_lines(report_markdown: str) -> tuple[str, ...]:
    """提取证据附录条目。

    Args:
        report_markdown: CLI 输出的 Markdown 报告。

    Returns:
        `## 证据与出处` 之后的附录证据条目。

    Raises:
        AssertionError: 当报告缺少证据附录标题时抛出。
    """

    lines = report_markdown.splitlines()
    evidence_heading_index = lines.index("## 证据与出处")
    return tuple(line for line in lines[evidence_heading_index + 1 :] if line.startswith("- ["))


def _assert_complete_evidence_contract(report_markdown: str) -> None:
    """断言 P3-S5 端到端证据锚点契约。

    Args:
        report_markdown: CLI 输出的 Markdown 报告。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当正文章节证据或附录来源定位不完整时抛出。
    """

    body_evidence_lines = _body_evidence_lines(report_markdown)
    appendix_evidence_lines = _appendix_evidence_lines(report_markdown)
    appendix_text = "\n".join(appendix_evidence_lines)

    assert len(body_evidence_lines) == 8
    assert all("年报2024§" in line for line in body_evidence_lines)
    assert all("当前章节未携带证据锚点" not in line for line in body_evidence_lines)
    assert len(appendix_evidence_lines) >= len(_EXPECTED_APPENDIX_EVIDENCE_FRAGMENTS)
    assert not any(line.startswith("- [M") for line in appendix_evidence_lines)
    for fragment in _EXPECTED_APPENDIX_EVIDENCE_FRAGMENTS:
        assert fragment in appendix_text


def test_p3_cli_outputs_complete_reports_for_three_sample_funds(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """验证 3 只样本基金可经 CLI 跑通完整 8 章报告。

    Args:
        monkeypatch: pytest 提供的运行时打补丁工具。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 CLI 端到端输出不符合 P3-S3 gate 时抛出。
    """

    reports = {case.fund_code: _build_report(case) for case in _SAMPLE_CASES}
    repository = _FakeRepository(reports)
    nav_provider = _FakeNavProvider()
    service = FundAnalysisService(
        extractor=FundDataExtractor(repository=repository, nav_provider=nav_provider),
    )
    recording_service = _RecordingService(service)
    monkeypatch.setattr(cli, "FundAnalysisService", lambda: recording_service)
    runner = CliRunner()

    outputs: dict[str, str] = {}
    for case in _SAMPLE_CASES:
        result = runner.invoke(cli.app, ("analyze", case.fund_code, *case.cli_args))

        assert result.exit_code == 0, result.output
        outputs[case.fund_code] = result.output
        for chapter_index in range(8):
            assert f"# {chapter_index}." in result.output
        assert "## 证据与出处" in result.output
        assert f"这是什么基金：{case.fund_name}（{case.fund_code}），{case.expected_type}" in result.output
        assert "基金简介：" in result.output
        assert "产品本质：未披露" not in result.output
        assert "业绩基准 未披露" not in result.output
        assert "表page-5-table-0" in result.output
        assert "表page-5-table-1" in result.output
        _assert_complete_evidence_contract(result.output)

    assert set(outputs) == {"110011", "510300", "000171"}
    assert len(recording_service.results) == 3
    for result in recording_service.results:
        assert result.audit_result.passed
        assert result.audit_result.checked_rules == ("P1", "P2", "P3", "C2", "L1", "R1", "R2")
        assert result.audit_result.issues == ()
    assert repository.calls == [(case.fund_code, 2024, True) for case in _SAMPLE_CASES]
    assert nav_provider.calls == [(case.fund_code, True) for case in _SAMPLE_CASES]
