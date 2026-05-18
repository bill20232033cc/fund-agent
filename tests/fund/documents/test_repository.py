"""文档仓库测试。"""

from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest

import fund_agent.fund.documents.adapters.annual_report_pdf as annual_report_pdf_module
import fund_agent.fund.documents.repository as repository_module
from fund_agent.fund.documents.adapters.annual_report_pdf import AnnualReportPdfAdapter
from fund_agent.fund.documents.cache import AnnualReportDocumentCache
from fund_agent.fund.documents.models import DocumentKey, ParsedAnnualReport, ReportSection
from fund_agent.fund.documents.repository import FundDocumentRepository


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
    downloader = AsyncMock(return_value=Path("/tmp/mock-report.pdf"))
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
        downloader=downloader,
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
    downloader.assert_awaited_once_with("110011", 2024, force_refresh=True)
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
        downloader=AsyncMock(return_value=pdf_path),
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
        downloader=AsyncMock(return_value=pdf_path),
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
    loader = _FakeCacheAwareLoader(pdf_path, [report])
    _install_temp_cache(monkeypatch, cache_root)
    repository = FundDocumentRepository(loader)

    first_report = await repository.load_annual_report("110011", 2024)
    second_report = await repository.load_annual_report("110011", 2024)

    assert first_report == report
    assert second_report == report
    loader.fetch_pdf_path.assert_awaited_once_with("110011", 2024, force_refresh=False)
    loader.parse_pdf.assert_awaited_once_with(pdf_path, "110011", 2024)


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
    loader = _FakeCacheAwareLoader(pdf_path, [stale_report, fresh_report])
    _install_temp_cache(monkeypatch, cache_root)
    repository = FundDocumentRepository(loader)

    first_report = await repository.load_annual_report("110011", 2024)
    refreshed_report = await repository.load_annual_report("110011", 2024, force_refresh=True)

    assert first_report == stale_report
    assert refreshed_report == fresh_report
    assert loader.fetch_pdf_path.await_count == 2
    assert loader.parse_pdf.await_count == 2
    loader.fetch_pdf_path.assert_any_await("110011", 2024, force_refresh=False)
    loader.fetch_pdf_path.assert_any_await("110011", 2024, force_refresh=True)


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

    await repository._cache.record_pdf_path(document_key, pdf_path)
    loaded_report = await repository.load_annual_report("110011", 2024)

    assert loaded_report == report
    loader.fetch_pdf_path.assert_not_awaited()
    loader.parse_pdf.assert_awaited_once_with(pdf_path, "110011", 2024)
