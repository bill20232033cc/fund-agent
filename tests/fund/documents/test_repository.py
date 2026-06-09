"""文档仓库测试。"""

import asyncio
from dataclasses import replace
from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest

import fund_agent.fund.documents.adapters.annual_report_pdf as annual_report_pdf_module
import fund_agent.fund.documents.repository as repository_module
from fund_agent.fund.documents.adapters.annual_report_pdf import AnnualReportPdfAdapter
from fund_agent.fund.documents.cache import AnnualReportDocumentCache
from fund_agent.fund.documents.models import (
    AnnualReportPdfFetchResult,
    AnnualReportSourceMetadata,
    DocumentKey,
    ParsedAnnualReport,
    ReportSection,
)
from fund_agent.fund.documents.repository import FundDocumentRepository
from fund_agent.fund.documents.sources import AnnualReportSourceResult


class _FakeSourceOrchestrator:
    """PDF 适配器测试使用的假来源编排器。"""

    def __init__(self, pdf_path: Path) -> None:
        """初始化假来源编排器。

        Args:
            pdf_path: 伪造的 PDF 路径。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self.fetch_annual_report_pdf = AsyncMock(
            return_value=AnnualReportSourceResult(
                pdf_path=pdf_path,
                metadata=AnnualReportSourceMetadata(source="eastmoney"),
            )
        )


@pytest.mark.asyncio
async def test_repository_returns_parsed_annual_report_without_path_exposure() -> None:
    """验证仓库对外返回统一年报对象而不是本地路径。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当仓库返回结果仍暴露本地路径时抛出。
    """

    raw_text = "§1 基金简介\n第一章正文\n§3 基金净值表现\n第三章正文"
    section_three_offset = raw_text.index("§3")
    source_orchestrator = _FakeSourceOrchestrator(Path("/tmp/mock-report.pdf"))
    text_extractor = Mock(return_value=raw_text)
    table_extractor = Mock(
        return_value=[
            {
                "page_number": 2,
                "headers": ["字段", "数值"],
                "rows": [["累计净值", "1.23"]],
            }
        ]
    )
    section_locator = Mock(
        return_value={
            "§1": (0, section_three_offset),
            "§3": (section_three_offset, len(raw_text)),
        }
    )
    adapter = AnnualReportPdfAdapter(
        source_orchestrator=source_orchestrator,
        text_extractor=text_extractor,
        table_extractor=table_extractor,
        section_locator=section_locator,
    )
    repository = FundDocumentRepository(adapter)

    report = await repository.load_annual_report("110011", 2024, force_refresh=True)

    assert isinstance(report, ParsedAnnualReport)
    assert not isinstance(report, Path)
    assert not hasattr(report, "path")
    assert report.key.fund_code == "110011"
    assert report.key.year == 2024
    assert report.key.document_kind == "annual_report"
    assert report.sections["§3"].title == "§3 基金净值表现"
    assert report.get_section_text("§3") == "§3 基金净值表现\n第三章正文"
    assert report.tables[0].page_number == 2
    assert report.tables[0].headers == ("字段", "数值")
    assert report.tables[0].rows == (("累计净值", "1.23"),)
    source_orchestrator.fetch_annual_report_pdf.assert_awaited_once_with(
        "110011", 2024, force_refresh=True
    )
    text_extractor.assert_called_once()
    table_extractor.assert_called_once()
    section_locator.assert_called_once_with(raw_text)


def _build_stub_report(fund_code: str, year: int, marker: str = "仓库样本基金") -> ParsedAnnualReport:
    """构造仓库测试使用的可缓存年报对象。

    Args:
        fund_code: 基金代码。
        year: 年报年份。
        marker: 用于区分不同解析结果的正文标记。

    Returns:
        满足 parsed report 缓存质量门槛的 ``ParsedAnnualReport`` 对象。

    Raises:
        无显式抛出。
    """

    raw_text = "\n".join(
        (
            "§2 基金简介",
            f"基金名称：{marker}",
            "§3 主要财务指标、基金净值表现及利润分配情况",
            "净值表现正文",
            "§4 管理人报告",
            "管理人报告正文",
            "§8 投资组合报告",
            "投资组合正文",
            "§9 基金份额持有人信息",
            "持有人正文",
            "§10 基金份额变动",
            "份额变动正文",
            "仓库缓存正文" * 160,
        )
    )
    section_ids = ("§2", "§3", "§4", "§8", "§9", "§10")
    sections = {
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
    return ParsedAnnualReport(
        key=DocumentKey(fund_code=fund_code, year=year),
        raw_text=raw_text,
        sections=sections,
        tables=(),
    )


def _eid_metadata(fund_code: str = "110011", year: int = 2024) -> AnnualReportSourceMetadata:
    """构造仓库测试使用的 EID 来源元数据。

    Args:
        fund_code: 基金代码。
        year: 年报年份。

    Returns:
        EID 来源元数据。

    Raises:
        无显式抛出。
    """

    return AnnualReportSourceMetadata(
        source="eid",
        source_url=f"http://eid.test/{fund_code}/{year}.pdf",
        fund_code=fund_code,
        fund_id=f"fund-{fund_code}",
        report_year=year,
        report_code="FB010010",
        report_desp="年度报告",
        report_name=f"{fund_code} {year} 年年度报告",
        upload_info_id=f"upload-{fund_code}-{year}",
        upload_info_detail_id=f"detail-{fund_code}-{year}",
        table_name="PDF",
        fallback_used=False,
        selected_source="eid",
        source_mode="single_source_only",
        fallback_enabled=False,
        discovery_contract_version="eid_annual_report_discovery.v1",
    )


def _eastmoney_fallback_metadata(
    fund_code: str = "110011",
    year: int = 2024,
) -> AnnualReportSourceMetadata:
    """构造仓库测试使用的 Eastmoney fallback 元数据。

    Args:
        fund_code: 基金代码。
        year: 年报年份。

    Returns:
        Eastmoney fallback 来源元数据。

    Raises:
        无显式抛出。
    """

    return AnnualReportSourceMetadata(
        source="eastmoney",
        fund_code=fund_code,
        report_year=year,
        fallback_used=True,
        primary_failure_category="not_found",
    )


def _assert_same_report_content(
    actual: ParsedAnnualReport,
    expected: ParsedAnnualReport,
) -> None:
    """断言两个 parsed report 的业务内容一致，忽略 metadata。

    Args:
        actual: 实际报告。
        expected: 预期报告。

    Returns:
        无返回值。

    Raises:
        AssertionError: 业务内容不一致时抛出。
    """

    assert actual.key == expected.key
    assert actual.raw_text == expected.raw_text
    assert actual.sections == expected.sections
    assert actual.tables == expected.tables


@pytest.mark.asyncio
async def test_repository_normalizes_fund_code_before_delegating_to_loader() -> None:
    """验证仓库会在委派前标准化基金代码。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当仓库未去除基金代码首尾空白时抛出。
    """

    loader = Mock()
    loader.load_annual_report = AsyncMock(return_value=_build_stub_report("110011", 2024))
    repository = FundDocumentRepository(loader)

    report = await repository.load_annual_report(" 110011 ", 2024)

    assert report.key.fund_code == "110011"
    loader.load_annual_report.assert_awaited_once_with("110011", 2024, force_refresh=False)


@pytest.mark.asyncio
async def test_repository_rejects_invalid_inputs() -> None:
    """验证仓库会拒绝空基金代码和非法年份。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当非法输入未触发 ``ValueError`` 时抛出。
    """

    loader = Mock()
    loader.load_annual_report = AsyncMock()
    repository = FundDocumentRepository(loader)

    with pytest.raises(ValueError, match="fund_code 不能为空"):
        await repository.load_annual_report("   ", 2024)

    with pytest.raises(ValueError, match="year 必须为正整数"):
        await repository.load_annual_report("110011", 0)


@pytest.mark.asyncio
async def test_annual_report_pdf_adapter_happy_path_builds_sections_and_tables() -> None:
    """验证 PDF 适配器会把底层 helper 结果适配为统一年报模型。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当适配结果不符合仓库公共契约时抛出。
    """

    pdf_path = Path("/tmp/annual-report.pdf")
    raw_text = "§1 基金简介\n第一章\n§4 管理人报告\n第四章"
    section_four_offset = raw_text.index("§4")
    adapter = AnnualReportPdfAdapter(
        source_orchestrator=_FakeSourceOrchestrator(pdf_path),
        text_extractor=Mock(return_value=raw_text),
        table_extractor=Mock(
            return_value=[
                {
                    "page_number": 5,
                    "headers": ["项目", "内容"],
                    "rows": [["策略", "长期持有"]],
                },
                {
                    "page_number": 5,
                    "headers": ["项目", "内容"],
                    "rows": [["风格", "偏价值"]],
                },
                {
                    "page_number": 7,
                    "headers": ["项目", "内容"],
                    "rows": [["行业", "制造业"]],
                }
            ]
        ),
        section_locator=Mock(
            return_value={
                "§1": (0, section_four_offset),
                "§4": (section_four_offset, len(raw_text)),
            }
        ),
    )

    report = await adapter.load_annual_report("000001", 2023)

    assert report.key.fund_code == "000001"
    assert report.key.year == 2023
    assert tuple(report.sections) == ("§1", "§4")
    assert report.sections["§4"].matched_rule == "fund_agent.fund.pdf.parser.locate_sections"
    assert report.sections["§4"].confidence == 1.0
    assert report.get_section_text("§4") == "§4 管理人报告\n第四章"
    assert report.tables[0].table_index == 0
    assert report.tables[1].table_index == 1
    assert report.tables[2].table_index == 0
    assert report.tables[0].headers == ("项目", "内容")
    assert report.tables[0].rows == (("策略", "长期持有"),)


@pytest.mark.asyncio
async def test_annual_report_pdf_adapter_runs_sync_helpers_via_to_thread(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """验证 PDF 适配器会通过 `asyncio.to_thread()` 隔离同步 helper。

    Args:
        monkeypatch: pytest 提供的运行时打补丁工具。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当同步 helper 未通过 `to_thread()` 调用时抛出。
    """

    pdf_path = Path("/tmp/annual-report.pdf")
    call_sequence: list[tuple[object, tuple[object, ...]]] = []
    raw_text = "§1 基金简介\n第一章"
    text_extractor = Mock(return_value=raw_text)
    table_extractor = Mock(return_value=[])
    section_locator = Mock(return_value={"§1": (0, len(raw_text))})

    async def _fake_to_thread(function: object, /, *args: object, **kwargs: object) -> object:
        """在测试内同步执行被代理函数，并记录调用顺序。

        Args:
            function: 被 `to_thread()` 代理的同步函数。
            *args: 传给目标函数的位置参数。
            **kwargs: 传给目标函数的关键字参数。

        Returns:
            目标函数的返回值。

        Raises:
            无显式抛出。
        """

        call_sequence.append((function, args))
        return function(*args, **kwargs)

    monkeypatch.setattr(annual_report_pdf_module.asyncio, "to_thread", _fake_to_thread)
    adapter = AnnualReportPdfAdapter(
        source_orchestrator=_FakeSourceOrchestrator(pdf_path),
        text_extractor=text_extractor,
        table_extractor=table_extractor,
        section_locator=section_locator,
    )

    report = await adapter.load_annual_report("110011", 2024)

    assert report.raw_text == raw_text
    assert call_sequence == [
        (text_extractor, (pdf_path,)),
        (table_extractor, (pdf_path,)),
        (section_locator, (raw_text,)),
    ]


class _FakeCacheAwareLoader:
    """仓库缓存测试使用的假加载器。"""

    def __init__(self, pdf_path: Path, reports: list[ParsedAnnualReport]) -> None:
        """初始化假加载器。

        Args:
            pdf_path: 伪造的原始 PDF 路径。
            reports: 顺序返回的解析结果。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self.fetch_pdf_path = AsyncMock(return_value=pdf_path)
        self.parse_pdf = AsyncMock(side_effect=reports)
        self.load_annual_report = AsyncMock(side_effect=AssertionError("不应走直接加载路径"))


class _FakeMetadataAwareLoader:
    """仓库 metadata 测试使用的显式 PDF 获取结果加载器。"""

    def __init__(
        self,
        fetch_results: dict[tuple[str, int], AnnualReportPdfFetchResult],
        reports: dict[tuple[str, int], ParsedAnnualReport],
    ) -> None:
        """初始化 metadata-aware 假加载器。

        Args:
            fetch_results: 按基金代码和年份索引的 PDF 获取结果。
            reports: 按基金代码和年份索引的 parsed report。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self.fetch_results = fetch_results
        self.reports = reports
        self.fetch_pdf_calls: list[tuple[str, int, bool]] = []
        self.fetch_pdf_path = AsyncMock(side_effect=AssertionError("不应调用 legacy fetch_pdf_path"))
        self.load_annual_report = AsyncMock(side_effect=AssertionError("不应走直接加载路径"))

    async def fetch_pdf(
        self,
        fund_code: str,
        year: int,
        *,
        force_refresh: bool = False,
    ) -> AnnualReportPdfFetchResult:
        """返回预设 PDF 获取结果。

        Args:
            fund_code: 基金代码。
            year: 年报年份。
            force_refresh: 是否强制刷新。

        Returns:
            PDF 获取结果。

        Raises:
            KeyError: 未配置对应结果时抛出。
        """

        self.fetch_pdf_calls.append((fund_code, year, force_refresh))
        return self.fetch_results[(fund_code, year)]

    async def parse_pdf(
        self,
        pdf_path: Path,
        fund_code: str,
        year: int,
    ) -> ParsedAnnualReport:
        """返回预设 parsed report。

        Args:
            pdf_path: PDF 路径。
            fund_code: 基金代码。
            year: 年报年份。

        Returns:
            parsed report。

        Raises:
            KeyError: 未配置对应报告时抛出。
        """

        return self.reports[(fund_code, year)]


class _ConcurrentMetadataAwareLoader(_FakeMetadataAwareLoader):
    """用于并发串扰回归的 metadata-aware 假加载器。"""

    def __init__(
        self,
        fetch_results: dict[tuple[str, int], AnnualReportPdfFetchResult],
        reports: dict[tuple[str, int], ParsedAnnualReport],
    ) -> None:
        """初始化并发假加载器。

        Args:
            fetch_results: 按基金代码和年份索引的 PDF 获取结果。
            reports: 按基金代码和年份索引的 parsed report。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        super().__init__(fetch_results, reports)
        self._first_fetch_started = asyncio.Event()
        self._second_fetch_started = asyncio.Event()

    async def fetch_pdf(
        self,
        fund_code: str,
        year: int,
        *,
        force_refresh: bool = False,
    ) -> AnnualReportPdfFetchResult:
        """用事件强制两个 fetch 调用交错。

        Args:
            fund_code: 基金代码。
            year: 年报年份。
            force_refresh: 是否强制刷新。

        Returns:
            PDF 获取结果。

        Raises:
            KeyError: 未配置对应结果时抛出。
        """

        self.fetch_pdf_calls.append((fund_code, year, force_refresh))
        if fund_code == "110011":
            self._first_fetch_started.set()
            await self._second_fetch_started.wait()
        else:
            await self._first_fetch_started.wait()
            self._second_fetch_started.set()
        return self.fetch_results[(fund_code, year)]


def _install_temp_cache(monkeypatch: pytest.MonkeyPatch, cache_root: Path) -> None:
    """把仓库默认缓存替换为测试临时目录。

    Args:
        monkeypatch: pytest 提供的运行时打补丁工具。
        cache_root: 测试缓存根目录。

    Returns:
        无返回值。

    Raises:
        无显式抛出。
    """

    monkeypatch.setattr(
        repository_module,
        "_create_default_cache",
        lambda: AnnualReportDocumentCache(cache_root),
    )


@pytest.mark.asyncio
async def test_repository_reuses_parsed_report_cache_without_reparsing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """验证仓库命中 parsed report 缓存后不会重复下载或重复解析。

    Args:
        tmp_path: pytest 提供的临时目录。
        monkeypatch: pytest 提供的运行时打补丁工具。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当缓存命中后仍重复下载或解析时抛出。
    """

    cache_root = tmp_path / "documents-cache"
    pdf_path = tmp_path / "110011_2024_annual_report.pdf"
    pdf_path.write_bytes(b"pdf")
    report = _build_stub_report("110011", 2024)
    metadata = _eid_metadata()
    loader = _FakeMetadataAwareLoader(
        {("110011", 2024): AnnualReportPdfFetchResult(pdf_path, metadata)},
        {("110011", 2024): report},
    )
    _install_temp_cache(monkeypatch, cache_root)
    repository = FundDocumentRepository(loader)

    first_report = await repository.load_annual_report("110011", 2024)
    second_report = await repository.load_annual_report("110011", 2024)

    _assert_same_report_content(first_report, report)
    _assert_same_report_content(second_report, report)
    assert loader.fetch_pdf_calls == [("110011", 2024, False)]
    assert first_report.metadata.cache.parsed_cache_hit is False
    assert second_report.metadata.cache.parsed_cache_hit is True


@pytest.mark.asyncio
async def test_repository_force_refresh_bypasses_cached_pdf_and_parsed_report(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """验证 `force_refresh=True` 会穿透 raw PDF 与 parsed report 缓存。

    Args:
        tmp_path: pytest 提供的临时目录。
        monkeypatch: pytest 提供的运行时打补丁工具。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当强制刷新仍命中旧缓存时抛出。
    """

    cache_root = tmp_path / "documents-cache"
    pdf_path = tmp_path / "110011_2024_annual_report.pdf"
    pdf_path.write_bytes(b"pdf")
    stale_report = _build_stub_report("110011", 2024)
    fresh_report = _build_stub_report("110011", 2024, marker="刷新后的仓库样本基金")
    metadata_a = _eid_metadata()
    metadata_b = replace(metadata_a, upload_info_id="new-upload", upload_info_detail_id="new-detail")
    loader = _FakeMetadataAwareLoader(
        {("110011", 2024): AnnualReportPdfFetchResult(pdf_path, metadata_a)},
        {("110011", 2024): stale_report},
    )
    _install_temp_cache(monkeypatch, cache_root)
    repository = FundDocumentRepository(loader)

    first_report = await repository.load_annual_report("110011", 2024)
    loader.fetch_results[("110011", 2024)] = AnnualReportPdfFetchResult(pdf_path, metadata_b)
    loader.reports[("110011", 2024)] = fresh_report
    refreshed_report = await repository.load_annual_report("110011", 2024, force_refresh=True)

    _assert_same_report_content(first_report, stale_report)
    _assert_same_report_content(refreshed_report, fresh_report)
    assert loader.fetch_pdf_calls == [
        ("110011", 2024, False),
        ("110011", 2024, True),
    ]


@pytest.mark.asyncio
async def test_repository_reuses_cached_pdf_metadata_when_parsed_cache_missing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """验证 parsed report 缓存缺失时，仓库会复用 documents 中记录的 PDF 路径。

    Args:
        tmp_path: pytest 提供的临时目录。
        monkeypatch: pytest 提供的运行时打补丁工具。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当仓库未复用缓存 PDF 路径时抛出。
    """

    cache_root = tmp_path / "documents-cache"
    pdf_path = tmp_path / "110011_2024_annual_report.pdf"
    pdf_path.write_bytes(b"pdf")
    report = _build_stub_report("110011", 2024)
    loader = _FakeCacheAwareLoader(pdf_path, [report])
    _install_temp_cache(monkeypatch, cache_root)
    repository = FundDocumentRepository(loader)
    document_key = DocumentKey(fund_code="110011", year=2024)
    metadata = _eid_metadata()

    await repository._cache.record_pdf_path(document_key, pdf_path, source_metadata=metadata)
    loaded_report = await repository.load_annual_report("110011", 2024)

    _assert_same_report_content(loaded_report, report)
    assert loaded_report.metadata.source == metadata
    loader.fetch_pdf_path.assert_not_awaited()
    loader.parse_pdf.assert_awaited_once_with(pdf_path, "110011", 2024)
    assert loaded_report.metadata.cache.pdf_cache_hit is True


@pytest.mark.asyncio
async def test_repository_attaches_eid_source_metadata_on_fresh_fetch(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """验证仓库 fresh fetch 会附加并持久化 EID 来源元数据。

    Args:
        tmp_path: pytest 提供的临时目录。
        monkeypatch: pytest 提供的运行时打补丁工具。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 EID 元数据未正确附加或持久化时抛出。
    """

    cache_root = tmp_path / "documents-cache"
    pdf_path = tmp_path / "110011_2024_annual_report.pdf"
    pdf_path.write_bytes(b"pdf")
    metadata = _eid_metadata()
    report = _build_stub_report("110011", 2024)
    loader = _FakeMetadataAwareLoader(
        {("110011", 2024): AnnualReportPdfFetchResult(pdf_path, metadata)},
        {("110011", 2024): report},
    )
    _install_temp_cache(monkeypatch, cache_root)
    repository = FundDocumentRepository(loader)

    loaded_report = await repository.load_annual_report("110011", 2024)
    cache_entry = await repository._cache.get_pdf_entry(DocumentKey("110011", 2024))

    assert loaded_report.metadata.source == metadata
    assert loaded_report.metadata.cache.pdf_cache_hit is False
    assert loaded_report.metadata.cache.parsed_cache_hit is False
    assert loaded_report.metadata.cache.source_metadata_present is True
    assert cache_entry is not None
    assert cache_entry.source_metadata == metadata
    assert loader.fetch_pdf_calls == [("110011", 2024, False)]
    loader.fetch_pdf_path.assert_not_awaited()


@pytest.mark.asyncio
async def test_repository_attaches_eastmoney_fallback_metadata_on_fresh_fetch(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """验证仓库会持久化 Eastmoney fallback 元数据且不伪造 EID ID。

    Args:
        tmp_path: pytest 提供的临时目录。
        monkeypatch: pytest 提供的运行时打补丁工具。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 fallback 元数据错误时抛出。
    """

    cache_root = tmp_path / "documents-cache"
    pdf_path = tmp_path / "110011_2024_annual_report.pdf"
    pdf_path.write_bytes(b"pdf")
    metadata = _eastmoney_fallback_metadata()
    loader = _FakeMetadataAwareLoader(
        {("110011", 2024): AnnualReportPdfFetchResult(pdf_path, metadata)},
        {("110011", 2024): _build_stub_report("110011", 2024)},
    )
    _install_temp_cache(monkeypatch, cache_root)
    repository = FundDocumentRepository(loader)

    loaded_report = await repository.load_annual_report("110011", 2024)

    assert loaded_report.metadata.source == metadata
    assert loaded_report.metadata.source is not None
    assert loaded_report.metadata.source.source == "eastmoney"
    assert loaded_report.metadata.source.fallback_used is True
    assert loaded_report.metadata.source.primary_failure_category == "not_found"
    assert loaded_report.metadata.source.fund_id is None
    assert loaded_report.metadata.source.upload_info_id is None
    assert loaded_report.metadata.source.upload_info_detail_id is None


@pytest.mark.asyncio
async def test_repository_parsed_cache_hit_retains_metadata(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """验证 parsed cache hit 会保留来源元数据并标记 cache provenance。

    Args:
        tmp_path: pytest 提供的临时目录。
        monkeypatch: pytest 提供的运行时打补丁工具。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 parsed cache hit 丢失元数据时抛出。
    """

    cache_root = tmp_path / "documents-cache"
    pdf_path = tmp_path / "110011_2024_annual_report.pdf"
    pdf_path.write_bytes(b"pdf")
    metadata = _eid_metadata()
    loader = _FakeMetadataAwareLoader(
        {("110011", 2024): AnnualReportPdfFetchResult(pdf_path, metadata)},
        {("110011", 2024): _build_stub_report("110011", 2024)},
    )
    _install_temp_cache(monkeypatch, cache_root)
    repository = FundDocumentRepository(loader)

    first_report = await repository.load_annual_report("110011", 2024)
    second_report = await repository.load_annual_report("110011", 2024)

    assert first_report.metadata.source == metadata
    assert second_report.metadata.source == metadata
    assert second_report.metadata.cache.parsed_cache_hit is True
    assert loader.fetch_pdf_calls == [("110011", 2024, False)]


@pytest.mark.asyncio
async def test_repository_pdf_cache_hit_uses_cached_source_metadata(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """验证 PDF cache hit 会使用 documents 行中的来源元数据。

    Args:
        tmp_path: pytest 提供的临时目录。
        monkeypatch: pytest 提供的运行时打补丁工具。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 PDF cache hit 丢失来源元数据时抛出。
    """

    cache_root = tmp_path / "documents-cache"
    pdf_path = tmp_path / "110011_2024_annual_report.pdf"
    pdf_path.write_bytes(b"pdf")
    metadata = _eid_metadata()
    loader = _FakeCacheAwareLoader(pdf_path, [_build_stub_report("110011", 2024)])
    _install_temp_cache(monkeypatch, cache_root)
    repository = FundDocumentRepository(loader)
    document_key = DocumentKey("110011", 2024)

    await repository._cache.record_pdf_path(document_key, pdf_path, source_metadata=metadata)
    loaded_report = await repository.load_annual_report("110011", 2024)
    cached_report = await repository._cache.load_parsed_report(document_key)

    assert loaded_report.metadata.source == metadata
    assert loaded_report.metadata.cache.pdf_cache_hit is True
    assert cached_report is not None
    assert cached_report.metadata.source == metadata
    loader.fetch_pdf_path.assert_not_awaited()


@pytest.mark.asyncio
async def test_repository_legacy_pdf_cache_without_metadata_is_ignored(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """验证 PDF cache legacy 元数据缺失时会被 EID policy 忽略。

    Args:
        tmp_path: pytest 提供的临时目录。
        monkeypatch: pytest 提供的运行时打补丁工具。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 legacy cache 被错误复用时抛出。
    """

    cache_root = tmp_path / "documents-cache"
    legacy_pdf_path = tmp_path / "legacy_110011_2024_annual_report.pdf"
    legacy_pdf_path.write_bytes(b"legacy pdf")
    fresh_pdf_path = tmp_path / "fresh_110011_2024_annual_report.pdf"
    fresh_pdf_path.write_bytes(b"fresh pdf")
    metadata = _eid_metadata()
    loader = _FakeMetadataAwareLoader(
        {("110011", 2024): AnnualReportPdfFetchResult(fresh_pdf_path, metadata)},
        {("110011", 2024): _build_stub_report("110011", 2024)},
    )
    _install_temp_cache(monkeypatch, cache_root)
    repository = FundDocumentRepository(loader)

    await repository._cache.record_pdf_path(DocumentKey("110011", 2024), legacy_pdf_path)
    loaded_report = await repository.load_annual_report("110011", 2024)

    assert loaded_report.metadata.source == metadata
    assert loaded_report.metadata.cache.pdf_cache_hit is False
    assert loader.fetch_pdf_calls == [("110011", 2024, False)]


@pytest.mark.asyncio
async def test_repository_rejects_parsed_cache_without_current_eid_policy(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """验证 parsed cache 缺少当前 EID policy metadata 时会被忽略。

    Args:
        tmp_path: pytest 提供的临时目录。
        monkeypatch: pytest 提供的运行时打补丁工具。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 stale parsed cache 被错误复用时抛出。
    """

    cache_root = tmp_path / "documents-cache"
    stale_pdf_path = tmp_path / "stale_110011_2024_annual_report.pdf"
    stale_pdf_path.write_bytes(b"stale pdf")
    fresh_pdf_path = tmp_path / "fresh_110011_2024_annual_report.pdf"
    fresh_pdf_path.write_bytes(b"fresh pdf")
    stale_report = _build_stub_report("110011", 2024, marker="stale")
    fresh_report = _build_stub_report("110011", 2024, marker="fresh")
    metadata = _eid_metadata()
    loader = _FakeMetadataAwareLoader(
        {("110011", 2024): AnnualReportPdfFetchResult(fresh_pdf_path, metadata)},
        {("110011", 2024): fresh_report},
    )
    _install_temp_cache(monkeypatch, cache_root)
    repository = FundDocumentRepository(loader)

    await repository._cache.save_parsed_report(
        stale_report,
        pdf_path=stale_pdf_path,
        source_metadata=None,
    )
    loaded_report = await repository.load_annual_report("110011", 2024)

    _assert_same_report_content(loaded_report, fresh_report)
    assert loaded_report.metadata.source == metadata
    assert loaded_report.metadata.cache.parsed_cache_hit is False
    assert loader.fetch_pdf_calls == [("110011", 2024, False)]


@pytest.mark.asyncio
async def test_repository_rejects_eastmoney_fallback_pdf_cache(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """验证 Eastmoney fallback PDF cache 不满足当前 EID policy。

    Args:
        tmp_path: pytest 提供的临时目录。
        monkeypatch: pytest 提供的运行时打补丁工具。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 Eastmoney cache 被错误复用时抛出。
    """

    cache_root = tmp_path / "documents-cache"
    stale_pdf_path = tmp_path / "eastmoney_110011_2024_annual_report.pdf"
    stale_pdf_path.write_bytes(b"stale pdf")
    fresh_pdf_path = tmp_path / "eid_110011_2024_annual_report.pdf"
    fresh_pdf_path.write_bytes(b"fresh pdf")
    metadata = _eid_metadata()
    loader = _FakeMetadataAwareLoader(
        {("110011", 2024): AnnualReportPdfFetchResult(fresh_pdf_path, metadata)},
        {("110011", 2024): _build_stub_report("110011", 2024)},
    )
    _install_temp_cache(monkeypatch, cache_root)
    repository = FundDocumentRepository(loader)

    await repository._cache.record_pdf_path(
        DocumentKey("110011", 2024),
        stale_pdf_path,
        source_metadata=_eastmoney_fallback_metadata(),
    )
    loaded_report = await repository.load_annual_report("110011", 2024)

    assert loaded_report.metadata.source == metadata
    assert loaded_report.metadata.cache.pdf_cache_hit is False
    assert loader.fetch_pdf_calls == [("110011", 2024, False)]


@pytest.mark.asyncio
async def test_repository_force_refresh_overwrites_source_metadata(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """验证 force_refresh 会覆盖旧来源元数据。

    Args:
        tmp_path: pytest 提供的临时目录。
        monkeypatch: pytest 提供的运行时打补丁工具。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当旧元数据未被覆盖时抛出。
    """

    cache_root = tmp_path / "documents-cache"
    pdf_path = tmp_path / "110011_2024_annual_report.pdf"
    pdf_path.write_bytes(b"pdf")
    metadata_a = _eid_metadata()
    metadata_b = replace(metadata_a, upload_info_id="new-upload", upload_info_detail_id="new-detail")
    loader = _FakeMetadataAwareLoader(
        {
            ("110011", 2024): AnnualReportPdfFetchResult(pdf_path, metadata_a),
        },
        {
            ("110011", 2024): _build_stub_report("110011", 2024),
        },
    )
    _install_temp_cache(monkeypatch, cache_root)
    repository = FundDocumentRepository(loader)

    first_report = await repository.load_annual_report("110011", 2024)
    loader.fetch_results[("110011", 2024)] = AnnualReportPdfFetchResult(pdf_path, metadata_b)
    loader.reports[("110011", 2024)] = _build_stub_report("110011", 2024, marker="fresh")
    refreshed_report = await repository.load_annual_report("110011", 2024, force_refresh=True)
    cache_entry = await repository._cache.get_pdf_entry(DocumentKey("110011", 2024))

    assert first_report.metadata.source == metadata_a
    assert refreshed_report.metadata.source == metadata_b
    assert cache_entry is not None
    assert cache_entry.source_metadata == metadata_b


@pytest.mark.asyncio
async def test_repository_metadata_aware_loader_preferred_over_legacy_fetch_pdf_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """验证同时存在两种 fetch 方法时仓库优先使用 metadata-aware contract。

    Args:
        tmp_path: pytest 提供的临时目录。
        monkeypatch: pytest 提供的运行时打补丁工具。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当仓库错误调用 legacy 方法时抛出。
    """

    cache_root = tmp_path / "documents-cache"
    pdf_path = tmp_path / "110011_2024_annual_report.pdf"
    pdf_path.write_bytes(b"pdf")
    metadata = _eid_metadata()
    loader = _FakeMetadataAwareLoader(
        {("110011", 2024): AnnualReportPdfFetchResult(pdf_path, metadata)},
        {("110011", 2024): _build_stub_report("110011", 2024)},
    )
    _install_temp_cache(monkeypatch, cache_root)
    repository = FundDocumentRepository(loader)

    loaded_report = await repository.load_annual_report("110011", 2024)

    assert loaded_report.metadata.source == metadata
    assert loader.fetch_pdf_calls == [("110011", 2024, False)]
    loader.fetch_pdf_path.assert_not_awaited()


@pytest.mark.asyncio
async def test_repository_legacy_fetch_pdf_path_loader_gets_empty_source_metadata(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """验证只支持 legacy fetch_pdf_path 的 loader 仍可工作且来源元数据为空。

    Args:
        tmp_path: pytest 提供的临时目录。
        monkeypatch: pytest 提供的运行时打补丁工具。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 legacy loader 失效时抛出。
    """

    cache_root = tmp_path / "documents-cache"
    pdf_path = tmp_path / "110011_2024_annual_report.pdf"
    pdf_path.write_bytes(b"pdf")
    loader = _FakeCacheAwareLoader(pdf_path, [_build_stub_report("110011", 2024)])
    _install_temp_cache(monkeypatch, cache_root)
    repository = FundDocumentRepository(loader)

    loaded_report = await repository.load_annual_report("110011", 2024)

    assert loaded_report.metadata.source is None
    assert loaded_report.metadata.cache.source_metadata_present is False


@pytest.mark.asyncio
async def test_repository_concurrent_loads_do_not_cross_attach_source_metadata(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """验证并发加载不会把不同调用的来源元数据串接到错误报告。

    Args:
        tmp_path: pytest 提供的临时目录。
        monkeypatch: pytest 提供的运行时打补丁工具。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当并发调用发生元数据串扰时抛出。
    """

    cache_root = tmp_path / "documents-cache"
    pdf_path_a = tmp_path / "110011_2024_annual_report.pdf"
    pdf_path_b = tmp_path / "004393_2024_annual_report.pdf"
    pdf_path_a.write_bytes(b"pdf-a")
    pdf_path_b.write_bytes(b"pdf-b")
    metadata_a = _eid_metadata("110011", 2024)
    metadata_b = _eid_metadata("004393", 2024)
    loader = _ConcurrentMetadataAwareLoader(
        {
            ("110011", 2024): AnnualReportPdfFetchResult(pdf_path_a, metadata_a),
            ("004393", 2024): AnnualReportPdfFetchResult(pdf_path_b, metadata_b),
        },
        {
            ("110011", 2024): _build_stub_report("110011", 2024),
            ("004393", 2024): _build_stub_report("004393", 2024),
        },
    )
    _install_temp_cache(monkeypatch, cache_root)
    repository = FundDocumentRepository(loader)

    report_a, report_b = await asyncio.gather(
        repository.load_annual_report("110011", 2024),
        repository.load_annual_report("004393", 2024),
    )
    entry_a = await repository._cache.get_pdf_entry(DocumentKey("110011", 2024))
    entry_b = await repository._cache.get_pdf_entry(DocumentKey("004393", 2024))

    assert report_a.metadata.source == metadata_a
    assert report_b.metadata.source == metadata_b
    assert entry_a is not None
    assert entry_b is not None
    assert entry_a.source_metadata == metadata_a
    assert entry_b.source_metadata == metadata_b
