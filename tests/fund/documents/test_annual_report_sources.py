"""年报来源编排测试。"""

from pathlib import Path

import httpx
import pytest

from fund_agent.fund.documents.adapters.annual_report_pdf import AnnualReportPdfAdapter
from fund_agent.fund.documents.sources import (
    AnnualReportSourceAggregateError,
    EastmoneyAnnualReportSource,
    AnnualReportSourceMetadata,
    AnnualReportSourceMismatchError,
    AnnualReportSourceNotFoundError,
    AnnualReportSourceOrchestrator,
    AnnualReportSourceResult,
    AnnualReportSourceSchemaError,
    AnnualReportSourceUnavailableError,
)


class _FakeAnnualReportSource:
    """年报来源编排测试使用的假来源。"""

    def __init__(
        self,
        name: str,
        *,
        result: AnnualReportSourceResult | None = None,
        error: Exception | None = None,
    ) -> None:
        """初始化假来源。

        Args:
            name: 来源名称。
            result: 成功时返回的来源结果。
            error: 失败时抛出的异常。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self.name = name
        self._result = result
        self._error = error
        self.calls: list[tuple[str, int, bool]] = []

    async def fetch_annual_report_pdf(
        self,
        fund_code: str,
        year: int,
        *,
        force_refresh: bool = False,
    ) -> AnnualReportSourceResult:
        """返回预设结果或抛出预设异常。

        Args:
            fund_code: 基金代码。
            year: 年报年份。
            force_refresh: 是否强制刷新。

        Returns:
            预设来源结果。

        Raises:
            Exception: 预设异常。
            AssertionError: 未配置结果且未配置异常时抛出。
        """

        self.calls.append((fund_code, year, force_refresh))
        if self._error is not None:
            raise self._error
        if self._result is None:
            raise AssertionError("fake source 未配置 result 或 error")
        return self._result


def _source_result(tmp_path: Path, source: str = "eastmoney") -> AnnualReportSourceResult:
    """构造来源成功结果。

    Args:
        tmp_path: pytest 临时目录。
        source: 来源名称。

    Returns:
        来源成功结果。

    Raises:
        OSError: 写入临时 PDF 失败时抛出。
    """

    pdf_path = tmp_path / f"{source}_annual_report.pdf"
    pdf_path.write_bytes(b"%PDF-fixture")
    return AnnualReportSourceResult(
        pdf_path=pdf_path,
        metadata=AnnualReportSourceMetadata(source=source),
    )


def test_orchestrator_rejects_empty_sources_but_none_uses_default() -> None:
    """验证空来源列表会被拒绝，`None` 仍使用默认来源。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当空来源未抛错或默认来源未创建时抛出。
    """

    with pytest.raises(ValueError, match="sources 不能为空"):
        AnnualReportSourceOrchestrator(())

    orchestrator = AnnualReportSourceOrchestrator(None)

    assert len(orchestrator.sources) == 1
    assert isinstance(orchestrator.sources[0], EastmoneyAnnualReportSource)


@pytest.mark.asyncio
async def test_orchestrator_returns_first_successful_source(tmp_path: Path) -> None:
    """验证编排器返回第一个成功来源且不调用 fallback。

    Args:
        tmp_path: pytest 临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 fallback 被错误调用时抛出。
    """

    primary = _FakeAnnualReportSource("eid", result=_source_result(tmp_path, "eid"))
    fallback = _FakeAnnualReportSource("eastmoney", result=_source_result(tmp_path, "eastmoney"))
    orchestrator = AnnualReportSourceOrchestrator((primary, fallback))

    result = await orchestrator.fetch_annual_report_pdf("004393", 2024)

    assert result.metadata.source == "eid"
    assert result.metadata.fallback_used is False
    assert primary.calls == [("004393", 2024, False)]
    assert fallback.calls == []


@pytest.mark.asyncio
async def test_orchestrator_falls_back_after_unavailable_error(tmp_path: Path) -> None:
    """验证来源临时不可用时会进入 fallback 并标记 metadata。

    Args:
        tmp_path: pytest 临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 fallback 未执行或未标记时抛出。
    """

    primary = _FakeAnnualReportSource(
        "eid",
        error=AnnualReportSourceUnavailableError("timeout"),
    )
    fallback = _FakeAnnualReportSource("eastmoney", result=_source_result(tmp_path))
    orchestrator = AnnualReportSourceOrchestrator((primary, fallback))

    result = await orchestrator.fetch_annual_report_pdf("004393", 2024)

    assert result.metadata.source == "eastmoney"
    assert result.metadata.fallback_used is True
    assert primary.calls == [("004393", 2024, False)]
    assert fallback.calls == [("004393", 2024, False)]


@pytest.mark.asyncio
async def test_orchestrator_falls_back_after_not_found_error(tmp_path: Path) -> None:
    """验证来源未找到时会进入 fallback。

    Args:
        tmp_path: pytest 临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 fallback 未执行时抛出。
    """

    primary = _FakeAnnualReportSource(
        "eid",
        error=AnnualReportSourceNotFoundError("not found"),
    )
    fallback = _FakeAnnualReportSource("eastmoney", result=_source_result(tmp_path))
    orchestrator = AnnualReportSourceOrchestrator((primary, fallback))

    result = await orchestrator.fetch_annual_report_pdf("004393", 2024)

    assert result.metadata.source == "eastmoney"
    assert result.metadata.fallback_used is True


@pytest.mark.asyncio
async def test_orchestrator_stops_on_mismatch_error(tmp_path: Path) -> None:
    """验证来源矛盾错误会 fail closed，不进入 fallback。

    Args:
        tmp_path: pytest 临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 fallback 被调用或异常类别错误时抛出。
    """

    primary = _FakeAnnualReportSource("eid", error=AnnualReportSourceMismatchError("wrong year"))
    fallback = _FakeAnnualReportSource("eastmoney", result=_source_result(tmp_path))
    orchestrator = AnnualReportSourceOrchestrator((primary, fallback))

    with pytest.raises(AnnualReportSourceMismatchError, match="wrong year"):
        await orchestrator.fetch_annual_report_pdf("004393", 2024)

    assert fallback.calls == []


@pytest.mark.asyncio
async def test_orchestrator_stops_on_schema_error(tmp_path: Path) -> None:
    """验证来源 schema 错误会 fail closed，不进入 fallback。

    Args:
        tmp_path: pytest 临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 fallback 被调用或异常类别错误时抛出。
    """

    primary = _FakeAnnualReportSource("eid", error=AnnualReportSourceSchemaError("missing field"))
    fallback = _FakeAnnualReportSource("eastmoney", result=_source_result(tmp_path))
    orchestrator = AnnualReportSourceOrchestrator((primary, fallback))

    with pytest.raises(AnnualReportSourceSchemaError, match="missing field"):
        await orchestrator.fetch_annual_report_pdf("004393", 2024)

    assert fallback.calls == []


@pytest.mark.asyncio
async def test_orchestrator_raises_file_not_found_when_all_sources_are_not_found() -> None:
    """验证所有来源均为 not-found 时最终抛出 FileNotFoundError。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当最终异常不是 not-found 时抛出。
    """

    primary = _FakeAnnualReportSource("eid", error=AnnualReportSourceNotFoundError("eid none"))
    fallback = _FakeAnnualReportSource(
        "eastmoney",
        error=AnnualReportSourceNotFoundError("eastmoney none"),
    )
    orchestrator = AnnualReportSourceOrchestrator((primary, fallback))

    with pytest.raises(FileNotFoundError) as exc_info:
        await orchestrator.fetch_annual_report_pdf("004393", 2024)

    assert isinstance(exc_info.value, AnnualReportSourceNotFoundError)
    assert "eid:not_found" in str(exc_info.value)
    assert "eastmoney:not_found" in str(exc_info.value)


@pytest.mark.asyncio
async def test_orchestrator_unavailable_exhaustion_is_not_file_not_found() -> None:
    """验证所有来源不可用时不会被折叠为 FileNotFoundError。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 unavailable 被误报为 not-found 时抛出。
    """

    primary = _FakeAnnualReportSource("eid", error=AnnualReportSourceUnavailableError("timeout"))
    fallback = _FakeAnnualReportSource(
        "eastmoney",
        error=AnnualReportSourceUnavailableError("http 503"),
    )
    orchestrator = AnnualReportSourceOrchestrator((primary, fallback))

    with pytest.raises(AnnualReportSourceAggregateError) as exc_info:
        await orchestrator.fetch_annual_report_pdf("004393", 2024)

    assert not isinstance(exc_info.value, FileNotFoundError)
    assert {failure.category for failure in exc_info.value.failures} == {"unavailable"}


@pytest.mark.asyncio
async def test_orchestrator_mixed_not_found_and_unavailable_preserves_unavailable_category() -> None:
    """验证 not-found 与 unavailable 混合时保留 unavailable 类别。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当混合失败被误报为纯 not-found 时抛出。
    """

    primary = _FakeAnnualReportSource("eid", error=AnnualReportSourceNotFoundError("none"))
    fallback = _FakeAnnualReportSource(
        "eastmoney",
        error=AnnualReportSourceUnavailableError("timeout"),
    )
    orchestrator = AnnualReportSourceOrchestrator((primary, fallback))

    with pytest.raises(AnnualReportSourceAggregateError) as exc_info:
        await orchestrator.fetch_annual_report_pdf("004393", 2024)

    assert not isinstance(exc_info.value, FileNotFoundError)
    assert {failure.category for failure in exc_info.value.failures} == {
        "not_found",
        "unavailable",
    }


@pytest.mark.asyncio
async def test_orchestrator_passes_force_refresh_to_source(tmp_path: Path) -> None:
    """验证 `force_refresh` 会显式传给来源。

    Args:
        tmp_path: pytest 临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当来源未收到强制刷新参数时抛出。
    """

    source = _FakeAnnualReportSource("eastmoney", result=_source_result(tmp_path))
    orchestrator = AnnualReportSourceOrchestrator((source,))

    await orchestrator.fetch_annual_report_pdf("004393", 2024, force_refresh=True)

    assert source.calls == [("004393", 2024, True)]


@pytest.mark.asyncio
async def test_annual_report_pdf_adapter_fetch_pdf_path_uses_source_orchestrator(
    tmp_path: Path,
) -> None:
    """验证 PDF 适配器通过来源编排器获取 PDF 路径。

    Args:
        tmp_path: pytest 临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当适配器未调用来源编排器时抛出。
    """

    source = _FakeAnnualReportSource("eastmoney", result=_source_result(tmp_path))
    orchestrator = AnnualReportSourceOrchestrator((source,))
    adapter = AnnualReportPdfAdapter(source_orchestrator=orchestrator)

    pdf_path = await adapter.fetch_pdf_path("004393", 2024, force_refresh=True)

    assert pdf_path == source._result.pdf_path
    assert source.calls == [("004393", 2024, True)]


@pytest.mark.asyncio
async def test_eastmoney_source_maps_http_error_to_unavailable() -> None:
    """验证 Eastmoney 包装器会把 HTTP 错误归类为来源不可用。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 HTTP 错误未被归类为 unavailable 时抛出。
    """

    async def failing_downloader(
        fund_code: str,
        year: int,
        *,
        force_refresh: bool = False,
    ) -> Path:
        """抛出 HTTP 错误的假下载器。

        Args:
            fund_code: 基金代码。
            year: 年报年份。
            force_refresh: 是否强制刷新。

        Returns:
            不返回。

        Raises:
            httpx.TimeoutException: 固定抛出。
        """

        raise httpx.TimeoutException(f"{fund_code}-{year}-{force_refresh}")

    source = EastmoneyAnnualReportSource(downloader=failing_downloader)

    with pytest.raises(AnnualReportSourceUnavailableError, match="004393-2024-True"):
        await source.fetch_annual_report_pdf("004393", 2024, force_refresh=True)
