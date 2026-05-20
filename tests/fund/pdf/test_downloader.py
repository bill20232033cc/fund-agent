"""PDF 下载 helper 测试。"""

from pathlib import Path
from unittest.mock import AsyncMock

import pandas as pd
import pytest

from fund_agent.fund.pdf import downloader


class _FailingAsyncClient:
    """用于断言缓存命中时不会创建 HTTP 客户端。"""

    def __init__(self, *_args: object, **_kwargs: object) -> None:
        """初始化一个一旦实例化就失败的客户端。

        Args:
            *_args: 位置参数占位。
            **_kwargs: 关键字参数占位。

        Returns:
            无返回值。

        Raises:
            AssertionError: 总是抛出，用于证明缓存命中未触网。
        """

        raise AssertionError("缓存命中时不应访问网络")


class _FakeResponse:
    """模拟 HTTP 响应对象。"""

    def __init__(self, content: bytes) -> None:
        """保存响应内容。

        Args:
            content: 模拟的 PDF 二进制内容。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self.content = content

    def raise_for_status(self) -> None:
        """模拟成功响应，不抛出异常。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """


class _RecordingAsyncClient:
    """记录请求参数的假 HTTP 客户端。"""

    captured: dict[str, object] = {}

    def __init__(self, **kwargs: object) -> None:
        """记录客户端初始化参数。

        Args:
            **kwargs: 透传的客户端参数。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self.__class__.captured["client_kwargs"] = kwargs

    async def __aenter__(self) -> "_RecordingAsyncClient":
        """进入异步上下文。

        Args:
            无。

        Returns:
            当前客户端实例。

        Raises:
            无显式抛出。
        """

        return self

    async def __aexit__(
        self,
        _exc_type: object,
        _exc: object,
        _tb: object,
    ) -> None:
        """退出异步上下文。

        Args:
            _exc_type: 异常类型占位。
            _exc: 异常对象占位。
            _tb: 异常回溯占位。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

    async def get(self, url: str, headers: dict[str, str]) -> _FakeResponse:
        """记录请求参数并返回固定响应。

        Args:
            url: 请求地址。
            headers: 请求头。

        Returns:
            模拟的 PDF 响应对象。

        Raises:
            无显式抛出。
        """

        self.__class__.captured["url"] = url
        self.__class__.captured["headers"] = headers
        return _FakeResponse(b"%PDF-1.7\nfresh-pdf")


@pytest.mark.asyncio
async def test_download_pdf_returns_cached_file_without_network(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """验证缓存命中时不会发起网络请求。

    Args:
        tmp_path: pytest 提供的临时目录。
        monkeypatch: pytest 提供的运行时打补丁工具。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当缓存命中仍触发网络请求时抛出。
    """

    cached_path = tmp_path / "cached.pdf"
    cached_path.write_bytes(b"%PDF-1.7\ncached-pdf")
    monkeypatch.setattr(downloader.httpx, "AsyncClient", _FailingAsyncClient)

    result = await downloader._download_pdf("https://example.com/cached.pdf", tmp_path)

    assert result == cached_path
    assert result.read_bytes() == b"%PDF-1.7\ncached-pdf"


@pytest.mark.asyncio
async def test_download_pdf_downloads_file_when_force_refresh_enabled(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """验证强制刷新时会重新下载并覆盖本地缓存。

    Args:
        tmp_path: pytest 提供的临时目录。
        monkeypatch: pytest 提供的运行时打补丁工具。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当强制刷新未重新下载或未覆盖缓存时抛出。
    """

    _RecordingAsyncClient.captured = {}
    monkeypatch.setattr(downloader.httpx, "AsyncClient", _RecordingAsyncClient)
    cached_path = tmp_path / "report.pdf"
    cached_path.write_bytes(b"%PDF-1.7\nstale-pdf")

    result = await downloader._download_pdf(
        "https://example.com/report.pdf",
        tmp_path,
        filename="report.pdf",
        force_refresh=True,
    )

    assert result == cached_path
    assert result.read_bytes() == b"%PDF-1.7\nfresh-pdf"
    assert _RecordingAsyncClient.captured["url"] == "https://example.com/report.pdf"
    assert "User-Agent" in _RecordingAsyncClient.captured["headers"]
    assert _RecordingAsyncClient.captured["client_kwargs"] == {
        "timeout": 60.0,
        "follow_redirects": True,
    }


@pytest.mark.asyncio
async def test_download_pdf_refreshes_invalid_cached_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """验证损坏 PDF 缓存不会被当作有效缓存复用。

    Args:
        tmp_path: pytest 提供的临时目录。
        monkeypatch: pytest 提供的运行时打补丁工具。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当损坏缓存未触发重新下载时抛出。
    """

    _RecordingAsyncClient.captured = {}
    monkeypatch.setattr(downloader.httpx, "AsyncClient", _RecordingAsyncClient)
    cached_path = tmp_path / "cached.pdf"
    cached_path.write_bytes(b"<html>error</html>")

    result = await downloader._download_pdf("https://example.com/cached.pdf", tmp_path)

    assert result == cached_path
    assert result.read_bytes() == b"%PDF-1.7\nfresh-pdf"
    assert _RecordingAsyncClient.captured["url"] == "https://example.com/cached.pdf"


@pytest.mark.asyncio
async def test_download_pdf_rejects_non_pdf_response(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """验证 Eastmoney 返回 HTML 时不会写入 PDF 缓存。

    Args:
        tmp_path: pytest 提供的临时目录。
        monkeypatch: pytest 提供的运行时打补丁工具。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当非 PDF 响应被写入缓存时抛出。
    """

    class _HtmlAsyncClient(_RecordingAsyncClient):
        """返回 HTML 正文的假客户端。"""

        async def get(self, url: str, headers: dict[str, str]) -> _FakeResponse:
            """返回非 PDF 响应。

            Args:
                url: 请求地址。
                headers: 请求头。

            Returns:
                HTML 响应。

            Raises:
                无显式抛出。
            """

            self.__class__.captured["url"] = url
            self.__class__.captured["headers"] = headers
            return _FakeResponse(b"<html>error</html>")

    monkeypatch.setattr(downloader.httpx, "AsyncClient", _HtmlAsyncClient)

    with pytest.raises(ValueError, match="PDF 响应缺少"):
        await downloader._download_pdf(
            "https://example.com/report.pdf",
            tmp_path,
            filename="report.pdf",
        )

    assert not (tmp_path / "report.pdf").exists()


@pytest.mark.asyncio
async def test_download_annual_report_delegates_to_download_pdf(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """验证年报下载 helper 会正确拼装 URL 和文件名。

    Args:
        tmp_path: pytest 提供的临时目录。
        monkeypatch: pytest 提供的运行时打补丁工具。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 URL、文件名或刷新参数拼装错误时抛出。
    """

    expected_path = tmp_path / "110011_2024_annual_report.pdf"
    download_pdf_mock = AsyncMock(return_value=expected_path)
    monkeypatch.setattr(downloader, "_find_annual_report_id", lambda fund_code, year: "RID123")
    monkeypatch.setattr(downloader, "_download_pdf", download_pdf_mock)

    result = await downloader._download_annual_report_pdf(
        "110011",
        2024,
        dest_dir=tmp_path,
        force_refresh=True,
    )

    assert result == expected_path
    download_pdf_mock.assert_awaited_once_with(
        "https://pdf.dfcfw.com/pdf/H2_RID123_1.pdf",
        tmp_path,
        filename="110011_2024_annual_report.pdf",
        force_refresh=True,
    )


def test_find_annual_report_id_returns_none_when_target_year_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """验证未命中目标年份时不会静默回退到其它年份年报。

    Args:
        monkeypatch: pytest 提供的运行时打补丁工具。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当函数错误回退到其它年份年报时抛出。
    """

    records = pd.DataFrame(
        [
            {"公告标题": "2023年年度报告", "报告ID": "RID2023"},
            {"公告标题": "2022年年度报告", "报告ID": "RID2022"},
            {"公告标题": "2024年年度报告摘要", "报告ID": "RID2024SUMMARY"},
        ]
    )
    monkeypatch.setattr(
        downloader.ak,
        "fund_announcement_report_em",
        lambda symbol: records,
    )

    result = downloader._find_annual_report_id("110011", 2024)

    assert result is None


@pytest.mark.asyncio
async def test_download_annual_report_uses_to_thread_for_lookup(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """验证年报下载 helper 会通过 `asyncio.to_thread()` 隔离同步公告查询。

    Args:
        tmp_path: pytest 提供的临时目录。
        monkeypatch: pytest 提供的运行时打补丁工具。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当同步公告查询未通过 `to_thread()` 调用时抛出。
    """

    expected_path = tmp_path / "110011_2024_annual_report.pdf"
    download_pdf_mock = AsyncMock(return_value=expected_path)
    call_payload: dict[str, object] = {}

    def _fake_find_annual_report_id(fund_code: str, year: int) -> str:
        """返回固定公告 ID，供 `to_thread()` 包装测试使用。

        Args:
            fund_code: 基金代码。
            year: 报告年份。

        Returns:
            固定公告 ID。

        Raises:
            无显式抛出。
        """

        return "RID123"

    async def _fake_to_thread(function: object, /, *args: object, **kwargs: object) -> object:
        """在测试内同步执行被代理函数，并记录调用参数。

        Args:
            function: 被 `to_thread()` 代理的同步函数。
            *args: 传给目标函数的位置参数。
            **kwargs: 传给目标函数的关键字参数。

        Returns:
            目标函数的返回值。

        Raises:
            无显式抛出。
        """

        call_payload["function"] = function
        call_payload["args"] = args
        call_payload["kwargs"] = kwargs
        return function(*args, **kwargs)

    monkeypatch.setattr(downloader, "_find_annual_report_id", _fake_find_annual_report_id)
    monkeypatch.setattr(downloader, "_download_pdf", download_pdf_mock)
    monkeypatch.setattr(downloader.asyncio, "to_thread", _fake_to_thread)

    result = await downloader._download_annual_report_pdf("110011", 2024, dest_dir=tmp_path)

    assert result == expected_path
    assert call_payload == {
        "function": _fake_find_annual_report_id,
        "args": ("110011", 2024),
        "kwargs": {},
    }


@pytest.mark.asyncio
async def test_download_annual_report_raises_when_target_year_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """验证未命中目标年份时由上层抛出 `FileNotFoundError`。

    Args:
        monkeypatch: pytest 提供的运行时打补丁工具。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当未命中目标年份却未抛出异常时抛出。
    """

    monkeypatch.setattr(downloader, "_find_annual_report_id", lambda fund_code, year: None)

    with pytest.raises(FileNotFoundError, match="未找到基金 110011 的 2024 年年报"):
        await downloader._download_annual_report_pdf("110011", 2024)
