"""年报来源编排测试。"""

import asyncio
import json
from pathlib import Path
from urllib.parse import parse_qs

import httpx
import pytest

from fund_agent.fund.documents.adapters.annual_report_pdf import AnnualReportPdfAdapter
from fund_agent.fund.documents.models import AnnualReportSourceMetadata
from fund_agent.fund.documents.sources import (
    AnnualReportSourceAggregateError,
    AnnualReportSourceConfig,
    EastmoneyAnnualReportSource,
    EidAnnualReportSource,
    AnnualReportSourceMismatchError,
    AnnualReportSourceNotFoundError,
    AnnualReportSourceOrchestrator,
    AnnualReportSourceResult,
    AnnualReportSourceSchemaError,
    AnnualReportSourceUnavailableError,
)

_EID_BASE_URL = "http://eid.test/fund"
_EID_PDF_BYTES = b"%PDF-1.7\nfixture"


def _eid_validate_payload(
    *,
    is_success: bool = True,
    fund_id: int | str | None = 1618,
) -> dict[str, object]:
    """构造 EID validate_fund.do 响应。

    Args:
        is_success: 是否校验成功。
        fund_id: EID 基金 ID。

    Returns:
        JSON payload。

    Raises:
        无显式抛出。
    """

    payload: dict[str, object] = {"isSuccess": is_success}
    if fund_id is not None:
        payload["fundId"] = fund_id
    return payload


def _eid_candidate_row(**overrides: object) -> dict[str, object]:
    """构造 004393 的 EID 年报候选行。

    Args:
        overrides: 覆盖字段。

    Returns:
        EID 候选行。

    Raises:
        无显式抛出。
    """

    row: dict[str, object] = {
        "fundCode": "004393",
        "fundId": 1618,
        "reportYear": "2024",
        "reportDesp": "年度报告",
        "reportCode": "FB010010",
        "uploadInfoId": 1248088,
        "uploadInfoDetailId": 1285356,
        "tableName": "PDF",
    }
    row.update(overrides)
    return row


def _eid_search_payload(rows: list[dict[str, object]]) -> dict[str, object]:
    """构造 EID advanced_search_report.do 响应。

    Args:
        rows: 候选行列表。

    Returns:
        JSON payload。

    Raises:
        无显式抛出。
    """

    return {"iTotalRecords": len(rows), "aaData": rows}


class _EidMockServer:
    """基于 httpx.MockTransport 的 EID 假服务器。"""

    def __init__(
        self,
        *,
        validate_payload: dict[str, object] | None = None,
        search_payload: dict[str, object] | None = None,
        pdf_content_type: str = "application/pdf",
        pdf_bytes: bytes = _EID_PDF_BYTES,
        status_code: int = 200,
        raise_timeout_on: str | None = None,
    ) -> None:
        """初始化 EID 假服务器。

        Args:
            validate_payload: validate_fund.do 响应。
            search_payload: advanced_search_report.do 响应。
            pdf_content_type: PDF 响应 Content-Type。
            pdf_bytes: PDF 响应 body。
            status_code: PDF 响应状态码。
            raise_timeout_on: 指定路径片段触发 timeout。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self.validate_payload = validate_payload or _eid_validate_payload()
        self.search_payload = search_payload or _eid_search_payload([_eid_candidate_row()])
        self.pdf_content_type = pdf_content_type
        self.pdf_bytes = pdf_bytes
        self.status_code = status_code
        self.raise_timeout_on = raise_timeout_on
        self.requests: list[httpx.Request] = []

    def handler(self, request: httpx.Request) -> httpx.Response:
        """处理 fake EID HTTP 请求。

        Args:
            request: HTTP 请求。

        Returns:
            HTTP 响应。

        Raises:
            httpx.TimeoutException: 请求命中 timeout 配置时抛出。
            AssertionError: 请求路径不符合 EID 预期时抛出。
        """

        self.requests.append(request)
        path = request.url.path
        if self.raise_timeout_on and self.raise_timeout_on in path:
            raise httpx.TimeoutException("timeout", request=request)
        if path == "/fund/disclose/validate_fund.do":
            assert request.method == "POST"
            return httpx.Response(200, json=self.validate_payload)
        if path == "/fund/disclose/advanced_search_report.do":
            assert request.method == "GET"
            return httpx.Response(200, json=self.search_payload)
        if path == "/fund/disclose/instance_show_pdf_id.do":
            assert request.method == "GET"
            return httpx.Response(
                self.status_code,
                headers={"Content-Type": self.pdf_content_type},
                content=self.pdf_bytes,
            )
        raise AssertionError(f"unexpected EID path: {path}")

    def client_factory(self) -> httpx.AsyncClient:
        """创建绑定 fake transport 的异步客户端。

        Args:
            无。

        Returns:
            异步 HTTP 客户端。

        Raises:
            无显式抛出。
        """

        return httpx.AsyncClient(transport=httpx.MockTransport(self.handler))


class _RecordingEidClient:
    """记录请求级 timeout 的 EID fake 客户端。"""

    def __init__(self) -> None:
        """初始化 fake 客户端。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self.calls: list[tuple[str, str, float | None]] = []

    async def __aenter__(self) -> "_RecordingEidClient":
        """进入异步上下文。

        Args:
            无。

        Returns:
            当前客户端。

        Raises:
            无显式抛出。
        """

        return self

    async def __aexit__(self, exc_type: object, exc: object, tb: object) -> None:
        """退出异步上下文。

        Args:
            exc_type: 异常类型。
            exc: 异常对象。
            tb: traceback。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

    async def post(
        self,
        url: str,
        *,
        data: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> httpx.Response:
        """记录 POST timeout 并返回 EID 校验响应。

        Args:
            url: 请求 URL。
            data: 表单数据。
            timeout: 请求级 timeout。

        Returns:
            HTTP 响应。

        Raises:
            无显式抛出。
        """

        self.calls.append(("POST", url, timeout))
        return httpx.Response(200, json=_eid_validate_payload())

    async def get(
        self,
        url: str,
        *,
        params: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> httpx.Response:
        """记录 GET timeout 并返回 EID 检索或 PDF 响应。

        Args:
            url: 请求 URL。
            params: 查询参数。
            timeout: 请求级 timeout。

        Returns:
            HTTP 响应。

        Raises:
            无显式抛出。
        """

        self.calls.append(("GET", url, timeout))
        if "advanced_search_report.do" in url:
            return httpx.Response(200, json=_eid_search_payload([_eid_candidate_row()]))
        return httpx.Response(200, headers={"Content-Type": "application/pdf"}, content=_EID_PDF_BYTES)


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
    """验证空来源列表会被拒绝，`None` 使用 EID 主源和 Eastmoney fallback。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当空来源未抛错或默认来源顺序错误时抛出。
    """

    with pytest.raises(ValueError, match="sources 不能为空"):
        AnnualReportSourceOrchestrator(())

    orchestrator = AnnualReportSourceOrchestrator(None)

    assert len(orchestrator.sources) == 2
    assert isinstance(orchestrator.sources[0], EidAnnualReportSource)
    assert isinstance(orchestrator.sources[1], EastmoneyAnnualReportSource)


@pytest.mark.asyncio
async def test_eid_source_fetches_004393_annual_report_with_validated_metadata(
    tmp_path: Path,
) -> None:
    """验证 EID source 按 004393 fixture 获取年报并返回元数据。

    Args:
        tmp_path: pytest 临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 EID 请求链路、aoData、PDF 或元数据错误时抛出。
    """

    server = _EidMockServer()
    source = EidAnnualReportSource(
        base_url=_EID_BASE_URL,
        cache_dir=tmp_path,
        client_factory=server.client_factory,
    )

    result = await source.fetch_annual_report_pdf("004393", 2024)

    assert result.pdf_path == tmp_path / "004393_2024_annual_report_eid.pdf"
    assert result.pdf_path.read_bytes() == _EID_PDF_BYTES
    assert result.metadata.source == "eid"
    assert result.metadata.fund_code == "004393"
    assert result.metadata.fund_id == "1618"
    assert result.metadata.report_year == 2024
    assert result.metadata.report_code == "FB010010"
    assert result.metadata.report_desp == "年度报告"
    assert result.metadata.upload_info_id == "1248088"
    assert result.metadata.upload_info_detail_id == "1285356"
    assert result.metadata.table_name == "PDF"
    assert result.metadata.source_url == (
        "http://eid.test/fund/disclose/instance_show_pdf_id.do?instanceid=1248088"
    )
    assert [request.url.path for request in server.requests] == [
        "/fund/disclose/validate_fund.do",
        "/fund/disclose/advanced_search_report.do",
        "/fund/disclose/instance_show_pdf_id.do",
    ]
    search_request = server.requests[1]
    ao_data = json.loads(parse_qs(search_request.url.query.decode())["aoData"][0])
    assert {"name": "reportType", "value": "FB010"} in ao_data
    assert {"name": "reportYear", "value": "2024"} in ao_data
    assert {"name": "fundCode", "value": "004393"} in ao_data


@pytest.mark.asyncio
async def test_eid_source_validate_fund_false_is_not_found(tmp_path: Path) -> None:
    """验证 EID validate_fund.do 返回 false 时归类为 not-found。

    Args:
        tmp_path: pytest 临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当异常类别错误时抛出。
    """

    server = _EidMockServer(validate_payload=_eid_validate_payload(is_success=False))
    source = EidAnnualReportSource(
        base_url=_EID_BASE_URL,
        cache_dir=tmp_path,
        client_factory=server.client_factory,
    )

    with pytest.raises(AnnualReportSourceNotFoundError, match="EID 未找到基金代码"):
        await source.fetch_annual_report_pdf("004393", 2024)


@pytest.mark.asyncio
async def test_eid_source_validate_schema_error_fails_closed(tmp_path: Path) -> None:
    """验证 EID validate_fund.do 缺必需字段时 fail closed。

    Args:
        tmp_path: pytest 临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当异常类别错误时抛出。
    """

    server = _EidMockServer(validate_payload=_eid_validate_payload(fund_id=None))
    source = EidAnnualReportSource(
        base_url=_EID_BASE_URL,
        cache_dir=tmp_path,
        client_factory=server.client_factory,
    )

    with pytest.raises(AnnualReportSourceSchemaError, match="缺少 fundId"):
        await source.fetch_annual_report_pdf("004393", 2024)


@pytest.mark.asyncio
async def test_eid_source_search_empty_is_not_found(tmp_path: Path) -> None:
    """验证 EID exact query 无候选时归类为 not-found。

    Args:
        tmp_path: pytest 临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当异常类别错误时抛出。
    """

    server = _EidMockServer(search_payload=_eid_search_payload([]))
    source = EidAnnualReportSource(
        base_url=_EID_BASE_URL,
        cache_dir=tmp_path,
        client_factory=server.client_factory,
    )

    with pytest.raises(AnnualReportSourceNotFoundError, match="未找到 004393 2024 年年报"):
        await source.fetch_annual_report_pdf("004393", 2024)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("row_override", "error_match"),
    [
        ({"reportYear": "2023"}, "reportYear"),
        ({"reportCode": "FB030010", "reportDesp": "第一季度报告"}, "reportCode"),
        ({"tableName": "HTML"}, "tableName"),
        ({"reportName": "中欧时代先锋股票型发起式证券投资基金2024年年度报告摘要"}, "reportName"),
    ],
)
async def test_eid_source_rejects_mismatched_candidates(
    tmp_path: Path,
    row_override: dict[str, object],
    error_match: str,
) -> None:
    """验证 EID 候选与年度 PDF 条件矛盾时 fail closed。

    Args:
        tmp_path: pytest 临时目录。
        row_override: 候选字段覆盖值。
        error_match: 异常匹配文本。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当异常类别错误时抛出。
    """

    server = _EidMockServer(search_payload=_eid_search_payload([_eid_candidate_row(**row_override)]))
    source = EidAnnualReportSource(
        base_url=_EID_BASE_URL,
        cache_dir=tmp_path,
        client_factory=server.client_factory,
    )

    with pytest.raises(AnnualReportSourceMismatchError, match=error_match):
        await source.fetch_annual_report_pdf("004393", 2024)


@pytest.mark.asyncio
async def test_eid_source_rejects_duplicate_candidates(tmp_path: Path) -> None:
    """验证 EID 多个有效候选时拒绝静默选择。

    Args:
        tmp_path: pytest 临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当未抛 schema 错误时抛出。
    """

    server = _EidMockServer(
        search_payload=_eid_search_payload([_eid_candidate_row(), _eid_candidate_row()])
    )
    source = EidAnnualReportSource(
        base_url=_EID_BASE_URL,
        cache_dir=tmp_path,
        client_factory=server.client_factory,
    )

    with pytest.raises(AnnualReportSourceSchemaError, match="多个年度 PDF 候选"):
        await source.fetch_annual_report_pdf("004393", 2024)


@pytest.mark.asyncio
async def test_eid_source_rejects_attachment_candidate(tmp_path: Path) -> None:
    """验证 EID 附件链路在 P7-S3 中 fail closed。

    Args:
        tmp_path: pytest 临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当未抛 schema 错误时抛出。
    """

    server = _EidMockServer(
        search_payload=_eid_search_payload([_eid_candidate_row(attachFileName="annual.pdf")])
    )
    source = EidAnnualReportSource(
        base_url=_EID_BASE_URL,
        cache_dir=tmp_path,
        client_factory=server.client_factory,
    )

    with pytest.raises(AnnualReportSourceSchemaError, match="不支持的附件链路"):
        await source.fetch_annual_report_pdf("004393", 2024)


@pytest.mark.asyncio
async def test_eid_source_pdf_content_type_must_be_pdf(tmp_path: Path) -> None:
    """验证 EID PDF 响应 Content-Type 必须是 application/pdf。

    Args:
        tmp_path: pytest 临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当非 PDF Content-Type 被接受时抛出。
    """

    server = _EidMockServer(pdf_content_type="text/html", pdf_bytes=b"<html></html>")
    source = EidAnnualReportSource(
        base_url=_EID_BASE_URL,
        cache_dir=tmp_path,
        client_factory=server.client_factory,
    )

    with pytest.raises(AnnualReportSourceSchemaError, match="Content-Type"):
        await source.fetch_annual_report_pdf("004393", 2024)


@pytest.mark.asyncio
async def test_eid_source_pdf_magic_bytes_must_be_pdf(tmp_path: Path) -> None:
    """验证 EID PDF 响应必须包含 %PDF- 文件头。

    Args:
        tmp_path: pytest 临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当非 PDF body 被接受时抛出。
    """

    server = _EidMockServer(pdf_bytes=b"<html></html>")
    source = EidAnnualReportSource(
        base_url=_EID_BASE_URL,
        cache_dir=tmp_path,
        client_factory=server.client_factory,
    )

    with pytest.raises(AnnualReportSourceSchemaError, match="%PDF-"):
        await source.fetch_annual_report_pdf("004393", 2024)


@pytest.mark.asyncio
async def test_eid_source_transient_http_error_is_unavailable(tmp_path: Path) -> None:
    """验证 EID timeout 会归类为 unavailable。

    Args:
        tmp_path: pytest 临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当异常类别错误时抛出。
    """

    server = _EidMockServer(raise_timeout_on="advanced_search_report.do")
    source = EidAnnualReportSource(
        base_url=_EID_BASE_URL,
        cache_dir=tmp_path,
        config=AnnualReportSourceConfig(retry_attempts=1),
        client_factory=server.client_factory,
    )

    with pytest.raises(AnnualReportSourceUnavailableError, match="timeout"):
        await source.fetch_annual_report_pdf("004393", 2024)


@pytest.mark.asyncio
async def test_orchestrator_falls_back_to_eastmoney_after_eid_not_found(tmp_path: Path) -> None:
    """验证 EID not-found 后会进入 Eastmoney fallback。

    Args:
        tmp_path: pytest 临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 fallback 未执行或 metadata 未标记时抛出。
    """

    eid = _FakeAnnualReportSource("eid", error=AnnualReportSourceNotFoundError("eid none"))
    eastmoney = _FakeAnnualReportSource("eastmoney", result=_source_result(tmp_path))
    orchestrator = AnnualReportSourceOrchestrator((eid, eastmoney))

    result = await orchestrator.fetch_annual_report_pdf("004393", 2024)

    assert result.metadata.source == "eastmoney"
    assert result.metadata.fallback_used is True


@pytest.mark.asyncio
async def test_orchestrator_does_not_fallback_after_eid_mismatch(tmp_path: Path) -> None:
    """验证 EID mismatch 后不进入 Eastmoney fallback。

    Args:
        tmp_path: pytest 临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 fallback 被错误调用时抛出。
    """

    eid = _FakeAnnualReportSource("eid", error=AnnualReportSourceMismatchError("wrong year"))
    eastmoney = _FakeAnnualReportSource("eastmoney", result=_source_result(tmp_path))
    orchestrator = AnnualReportSourceOrchestrator((eid, eastmoney))

    with pytest.raises(AnnualReportSourceMismatchError, match="wrong year"):
        await orchestrator.fetch_annual_report_pdf("004393", 2024)

    assert eastmoney.calls == []


@pytest.mark.asyncio
async def test_eid_source_force_refresh_overwrites_cached_pdf(tmp_path: Path) -> None:
    """验证 EID force_refresh 会覆盖既有 PDF 缓存。

    Args:
        tmp_path: pytest 临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当缓存未被覆盖时抛出。
    """

    cached_pdf = tmp_path / "004393_2024_annual_report_eid.pdf"
    cached_pdf.write_bytes(b"%PDF-old")
    server = _EidMockServer(pdf_bytes=b"%PDF-new")
    source = EidAnnualReportSource(
        base_url=_EID_BASE_URL,
        cache_dir=tmp_path,
        client_factory=server.client_factory,
    )

    result = await source.fetch_annual_report_pdf("004393", 2024, force_refresh=True)

    assert result.pdf_path.read_bytes() == b"%PDF-new"
    assert "/fund/disclose/instance_show_pdf_id.do" in [
        request.url.path for request in server.requests
    ]


@pytest.mark.asyncio
async def test_eid_source_without_force_refresh_reuses_existing_pdf_after_metadata_validation(
    tmp_path: Path,
) -> None:
    """验证 EID 非强刷时元数据校验后复用既有 PDF。

    Args:
        tmp_path: pytest 临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 PDF 端点被错误调用或缓存未复用时抛出。
    """

    cached_pdf = tmp_path / "004393_2024_annual_report_eid.pdf"
    cached_pdf.write_bytes(b"%PDF-cached")
    server = _EidMockServer(pdf_bytes=b"%PDF-new")
    source = EidAnnualReportSource(
        base_url=_EID_BASE_URL,
        cache_dir=tmp_path,
        client_factory=server.client_factory,
    )

    result = await source.fetch_annual_report_pdf("004393", 2024)

    assert result.pdf_path == cached_pdf
    assert result.pdf_path.read_bytes() == b"%PDF-cached"
    assert [request.url.path for request in server.requests] == [
        "/fund/disclose/validate_fund.do",
        "/fund/disclose/advanced_search_report.do",
    ]


@pytest.mark.asyncio
async def test_eid_source_serializes_same_document_downloads(tmp_path: Path) -> None:
    """验证同一基金年份的 EID 并发请求只下载一次 PDF。

    Args:
        tmp_path: pytest 临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当同 key 并发请求重复下载 PDF 时抛出。
    """

    server = _EidMockServer(pdf_bytes=b"%PDF-concurrent")
    source = EidAnnualReportSource(
        base_url=_EID_BASE_URL,
        cache_dir=tmp_path,
        client_factory=server.client_factory,
    )

    results = await asyncio.gather(
        source.fetch_annual_report_pdf("004393", 2024),
        source.fetch_annual_report_pdf("004393", 2024),
    )

    assert {result.pdf_path for result in results} == {
        tmp_path / "004393_2024_annual_report_eid.pdf"
    }
    assert results[0].pdf_path.read_bytes() == b"%PDF-concurrent"
    assert [
        request.url.path
        for request in server.requests
        if request.url.path == "/fund/disclose/instance_show_pdf_id.do"
    ] == ["/fund/disclose/instance_show_pdf_id.do"]


@pytest.mark.asyncio
async def test_eid_source_uses_distinct_request_level_timeouts(tmp_path: Path) -> None:
    """验证 EID 元数据请求和 PDF 请求使用不同 request-level timeout。

    Args:
        tmp_path: pytest 临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 timeout 未按请求类型传递时抛出。
    """

    client = _RecordingEidClient()
    config = AnnualReportSourceConfig(
        metadata_timeout_seconds=3.5,
        pdf_timeout_seconds=77.0,
        retry_attempts=1,
    )
    source = EidAnnualReportSource(
        base_url=_EID_BASE_URL,
        cache_dir=tmp_path,
        config=config,
        client_factory=lambda: client,
    )

    await source.fetch_annual_report_pdf("004393", 2024)

    assert [call[2] for call in client.calls] == [3.5, 3.5, 77.0]
    assert [call[0] for call in client.calls] == ["POST", "GET", "GET"]


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


@pytest.mark.asyncio
async def test_eastmoney_source_maps_os_error_to_unavailable() -> None:
    """验证 Eastmoney 包装器会把缓存写入错误归类为来源不可用。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 OSError 未被归类为 unavailable 时抛出。
    """

    async def failing_downloader(
        fund_code: str,
        year: int,
        *,
        force_refresh: bool = False,
    ) -> Path:
        """抛出文件系统错误的假下载器。

        Args:
            fund_code: 基金代码。
            year: 年报年份。
            force_refresh: 是否强制刷新。

        Returns:
            不返回。

        Raises:
            OSError: 固定抛出。
        """

        raise OSError(f"{fund_code}-{year}-{force_refresh}")

    source = EastmoneyAnnualReportSource(downloader=failing_downloader)

    with pytest.raises(AnnualReportSourceUnavailableError, match="004393-2024-True"):
        await source.fetch_annual_report_pdf("004393", 2024, force_refresh=True)
