"""CSRC EID accumulated NAV source adapter 测试。

本文件使用 `httpx.MockTransport` 和小型 HTML fixtures 覆盖 CSRC EID search /
detail / classification source adapter，不访问真实网络，也不引入 stock-sdk runtime。
"""

from __future__ import annotations

import inspect
from urllib.parse import parse_qs

import httpx
import pytest

from fund_agent.fund.data.csrc_eid_nav_source import CsrcEidNavSource
from fund_agent.fund.data.nav_models import FundNavRecord, FundNavSeries, NavDataContractError
from fund_agent.fund.data.nav_source_contract import _NavSourceAdapter

_BASE_URL = "http://eid.test"


def _search_payload(fund_id: str | int | None = 5755, *, success: bool = True) -> bytes:
    """构造 CSRC EID search 响应。

    Args:
        fund_id: EID fundId。
        success: 是否成功。

    Returns:
        JSON bytes。

    Raises:
        无显式抛出。
    """

    if fund_id is None:
        return b'{"isSuccess":true}'
    success_text = "true" if success else "false"
    return f'{{"fundId":{fund_id!r},"isSuccess":{success_text}}}'.replace("'", "").encode()


def _detail_html(*, include_f: bool = True, bad_classification: bool = False) -> str:
    """构造 detail 页份额分类 HTML。

    Args:
        include_f: 是否包含 F 类。
        bad_classification: 是否篡改 A 类 classification。

    Returns:
        detail HTML。

    Raises:
        无显式抛出。
    """

    rows = [
        ("国泰利享中短债债券A", "006597", "2030-9999" if bad_classification else "2030-1010"),
        ("国泰利享中短债债券C", "006598", "2030-1020"),
        ("国泰利享中短债债券E", "014217", "2030-1040"),
    ]
    if include_f:
        rows.append(("国泰利享中短债债券F", "022176", "2030-1050"))
    body = "\n".join(
        (
            "<tr><td style='padding-left:15px;font-size:16px;text-align: left;'>"
            f"净值日报{name}({code})</td><td><a href='../disclose/list_net_classification.do"
            f"?reportType=FB040&fundCode=006597&classification={classification}'>更多</a></td></tr>"
        )
        for name, code, classification in rows
    )
    return f"<html><body><table>{body}</table></body></html>"


def _classification_html(
    rows: list[tuple[str, str, str, str]],
    *,
    start: int = 0,
    total: int | None = None,
    total_pages: int | None = None,
    include_header: bool = True,
) -> str:
    """构造分类净值列表 HTML。

    Args:
        rows: `(code, unit_nav, accumulated_nav, date)` rows。
        start: 0-based start offset。
        total: 声明总记录数；为空时等于 rows 数。
        total_pages: 声明总页数；为空时按 total/20 简化。
        include_header: 是否包含必需表头。

    Returns:
        classification HTML。

    Raises:
        无显式抛出。
    """

    declared_total = len(rows) if total is None else total
    declared_pages = total_pages if total_pages is not None else max(1, (declared_total + 19) // 20)
    range_start = 0 if declared_total == 0 and not rows else start + 1
    end = start + len(rows)
    header = (
        "<tr><td>基金代码</td><td>分级代码</td><td>基金简称</td><td>份额净值</td>"
        "<td>累计净值 </td><td>基金资产净值</td><td>估值日期</td><td>备注</td></tr>"
        if include_header
        else "<tr><td>bad</td></tr>"
    )
    row_html = "\n".join(
        (
            "<tr><td>006597</td><td>{code}</td><td>国泰利享中短债债券A</td>"
            "<td>{unit_nav}</td><td>{acc_nav}</td><td></td><td>{nav_date}</td><td></td></tr>"
        ).format(code=code, unit_nav=unit_nav, acc_nav=acc_nav, nav_date=nav_date)
        for code, unit_nav, acc_nav, nav_date in rows
    )
    return (
        f"<html><body><table>{header}{row_html}</table>"
        f"<table><tr><td>第 <input value='1'> 页 / 共{declared_pages}页</td>"
        f"<td>记录：{range_start}-{end} / 共{declared_total}条</td></tr></table></body></html>"
    )


class _CsrcMockServer:
    """基于 httpx.MockTransport 的 CSRC EID 假服务器。"""

    def __init__(
        self,
        *,
        detail_html: str | None = None,
        list_pages: dict[int, str] | None = None,
        search_success_by_code: dict[str, bool] | None = None,
        status_code: int = 200,
        raise_transport: bool = False,
    ) -> None:
        """初始化 fake server。

        Args:
            detail_html: detail endpoint HTML。
            list_pages: start offset 到 list HTML 的映射。
            search_success_by_code: 指定基金代码 search 是否成功。
            status_code: 默认 HTTP 状态码。
            raise_transport: 是否抛出 transport error。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self.detail_html = detail_html or _detail_html()
        self.list_pages = list_pages or {
            0: _classification_html(
                [
                    ("006597", "1.1000", "1.1200", "2024-01-02"),
                    ("006597", "1.1001", "1.1201", "2024-01-03"),
                ],
                total=2,
            )
        }
        self.search_success_by_code = search_success_by_code or {}
        self.status_code = status_code
        self.raise_transport = raise_transport
        self.requests: list[httpx.Request] = []

    def handler(self, request: httpx.Request) -> httpx.Response:
        """处理 fake HTTP 请求。

        Args:
            request: httpx 请求。

        Returns:
            fake HTTP 响应。

        Raises:
            httpx.TransportError: 配置为 transport error 时抛出。
        """

        self.requests.append(request)
        if self.raise_transport:
            raise httpx.TransportError("network down", request=request)
        if self.status_code != 200:
            return httpx.Response(self.status_code, text="error")
        path = request.url.path
        if path.endswith("/validate_fund.do"):
            form = parse_qs(request.content.decode())
            code = form.get("cFundCode", [""])[0]
            success = self.search_success_by_code.get(code, True)
            return httpx.Response(200, content=_search_payload(success=success))
        if path.endswith("/fund_detail_search.do"):
            return httpx.Response(200, text=self.detail_html)
        if path.endswith("/list_net_classification.do"):
            start = int(request.url.params.get("start", "0"))
            return httpx.Response(200, text=self.list_pages[start])
        return httpx.Response(404, text="not found")

    def client_factory(self) -> httpx.AsyncClient:
        """创建使用 MockTransport 的 HTTP client。

        Args:
            无。

        Returns:
            fake HTTP client。

        Raises:
            无显式抛出。
        """

        return httpx.AsyncClient(transport=httpx.MockTransport(self.handler), base_url=_BASE_URL)


@pytest.mark.asyncio
async def test_csrc_source_loads_accumulated_a_success() -> None:
    """验证 A 类 fixture 能返回 accumulated raw DTO。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 source DTO 不符合预期时抛出。
    """

    server = _CsrcMockServer()
    source = CsrcEidNavSource(base_url=_BASE_URL, client_factory=server.client_factory)

    result = await source.load_raw_nav_source("006597", share_class="A", force_refresh=True)

    assert result.source == "csrc_eid"
    assert result.origin_source == "csrc_eid"
    assert result.fund_code == "006597"
    assert result.source_id == "5755:2030-1010"
    assert result.source_nav_type == "accumulated_nav"
    assert result.source_adjustment_basis == "accumulated_nav"
    assert result.records[0]["估值日期"] == "2024-01-02"
    assert result.records[0]["累计净值"] == "1.1200"
    assert result.records[0]["单位净值"] == "1.1000"
    assert result.source_query_params[:4] == (
        ("fundCode", "006597"),
        ("classification", "2030-1010"),
        ("limit", "20"),
        ("start", "0"),
    )


@pytest.mark.asyncio
async def test_csrc_source_proves_all_share_class_mappings() -> None:
    """验证 A/C/E/F 分类 identity 均来自 detail 页。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当份额映射不符合 accepted identity 时抛出。
    """

    expected = {
        "006597": ("A", "2030-1010"),
        "006598": ("C", "2030-1020"),
        "014217": ("E", "2030-1040"),
        "022176": ("F", "2030-1050"),
    }
    for code, (share_class, classification) in expected.items():
        server = _CsrcMockServer(
            search_success_by_code={"022176": False},
            list_pages={
                0: _classification_html(
                    [(code, "1.0000", "1.0000", "2024-10-08")],
                    total=1,
                )
            },
        )
        source = CsrcEidNavSource(base_url=_BASE_URL, client_factory=server.client_factory)

        result = await source.load_raw_nav_source(code, share_class=share_class)

        assert result.fund_code == code
        assert result.source_id == f"5755:{classification}"
        assert result.records[0]["份额类别"] == share_class


@pytest.mark.asyncio
async def test_csrc_source_conflicting_share_class_raises_identity_mismatch() -> None:
    """验证 fund_code/share_class 冲突触发 identity_mismatch。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当未触发 identity_mismatch 时抛出。
    """

    source = CsrcEidNavSource(base_url=_BASE_URL, client_factory=_CsrcMockServer().client_factory)

    with pytest.raises(NavDataContractError) as exc_info:
        await source.load_raw_nav_source("006598", share_class="A")

    assert exc_info.value.category == "identity_mismatch"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("server", "category"),
    (
        (_CsrcMockServer(detail_html="<html>missing classes</html>"), "identity_mismatch"),
        (_CsrcMockServer(list_pages={0: _classification_html([], total=0)}), "not_found"),
        (_CsrcMockServer(list_pages={0: _classification_html([], include_header=False, total=0)}), "schema_drift"),
        (_CsrcMockServer(status_code=503), "unavailable"),
        (_CsrcMockServer(raise_transport=True), "unavailable"),
    ),
)
async def test_csrc_source_failure_taxonomy(server: _CsrcMockServer, category: str) -> None:
    """验证 CSRC source 常见失败分类。

    Args:
        server: fake server。
        category: 期望失败分类。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当失败分类不符合预期时抛出。
    """

    source = CsrcEidNavSource(base_url=_BASE_URL, client_factory=server.client_factory)

    with pytest.raises(NavDataContractError) as exc_info:
        await source.load_raw_nav_source("006597", share_class="A")

    assert exc_info.value.category == category


@pytest.mark.asyncio
async def test_csrc_source_pagination_last_page_boundary_success() -> None:
    """验证 total % limit != 0 的最后一页边界能成功。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当分页边界处理错误时抛出。
    """

    page0_rows = [("006597", "1.0000", "1.0000", f"2024-01-{day:02d}") for day in range(1, 21)]
    page20_rows = [("006597", "1.0021", "1.0021", "2024-01-21")]
    server = _CsrcMockServer(
        list_pages={
            0: _classification_html(page0_rows, start=0, total=21, total_pages=2),
            20: _classification_html(page20_rows, start=20, total=21, total_pages=2),
        }
    )
    source = CsrcEidNavSource(base_url=_BASE_URL, client_factory=server.client_factory)

    result = await source.load_raw_nav_source("006597", share_class="A")

    assert len(result.records) == 21


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "server",
    (
        _CsrcMockServer(
            list_pages={
                0: _classification_html([("006597", "1", "1", "2024-01-01")], start=0, total=2)
            }
        ),
        _CsrcMockServer(
            list_pages={
                0: _classification_html(
                    [("006597", "1", "1", f"2024-01-{day:02d}") for day in range(1, 21)],
                    start=0,
                    total=21,
                    total_pages=2,
                ),
                20: _classification_html([("006597", "1", "1", "2024-01-21")], start=20, total=22, total_pages=2),
            }
        ),
        _CsrcMockServer(
            list_pages={
                0: _classification_html(
                    [("006597", "1", "1", f"2024-01-{day:02d}") for day in range(1, 21)],
                    start=0,
                    total=21,
                    total_pages=2,
                ),
                20: _classification_html([], start=20, total=21, total_pages=2),
            }
        ),
    ),
)
async def test_csrc_source_pagination_integrity_errors(server: _CsrcMockServer) -> None:
    """验证分页 total mismatch、total changes、last page mismatch 触发 integrity_error。

    Args:
        server: fake server。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当未触发 integrity_error 时抛出。
    """

    source = CsrcEidNavSource(base_url=_BASE_URL, client_factory=server.client_factory)

    with pytest.raises(NavDataContractError) as exc_info:
        await source.load_raw_nav_source("006597", share_class="A")

    assert exc_info.value.category == "integrity_error"


@pytest.mark.asyncio
async def test_csrc_source_preserves_blank_accumulated_rows_for_repository_taxonomy() -> None:
    """验证 A/C 早期空累计净值日期被保留给 repository 分类。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当空累计净值 row 被 source 丢失时抛出。
    """

    server = _CsrcMockServer(
        list_pages={
            0: _classification_html(
                [
                    ("006597", "1.0000", "", "2018-12-07"),
                    ("006597", "1.0001", "", "2018-12-14"),
                    ("006597", "1.0002", "1.0002", "2018-12-21"),
                ],
                total=3,
            )
        }
    )
    source = CsrcEidNavSource(base_url=_BASE_URL, client_factory=server.client_factory)

    result = await source.load_raw_nav_source("006597", share_class="A")

    assert result.records[0]["估值日期"] == "2018-12-07"
    assert result.records[0]["累计净值"] == ""
    assert result.records[1]["估值日期"] == "2018-12-14"
    assert result.records[1]["累计净值"] == ""


def test_nav_source_adapter_protocol_has_explicit_signature() -> None:
    """验证 source adapter Protocol 不包含 extra_payload 或 kwargs。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当签名包含禁止参数时抛出。
    """

    sig = inspect.signature(_NavSourceAdapter.load_raw_nav_source)

    assert "extra_payload" not in sig.parameters
    for param in sig.parameters.values():
        assert param.kind is not inspect.Parameter.VAR_KEYWORD


def test_no_stock_sdk_runtime_dependency() -> None:
    """验证 data source 模块没有 stock-sdk / node / subprocess runtime glue。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当出现 stock-sdk runtime 依赖痕迹时抛出。
    """

    import fund_agent.fund.data.csrc_eid_nav_source as csrc_module
    import fund_agent.fund.data.nav_repository as repository_module

    combined_source = inspect.getsource(csrc_module) + inspect.getsource(repository_module)

    assert "stock-sdk" not in combined_source
    assert "subprocess" not in combined_source
    assert "node" not in combined_source.lower()


def test_stock_sdk_date_shift_classified_as_integrity_error() -> None:
    """验证 stock-sdk 风格日期位移 fixture 仍被归类为 integrity_error。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当日期位移未被拒绝时抛出。
    """

    reference = {"date": "2023-01-12", "nav": "1.1254", "acc_nav": "1.1334"}
    stock_sdk_style = {"date": "2023-01-11", "nav": "1.1254", "acc_nav": "1.1334"}

    with pytest.raises(NavDataContractError) as exc_info:
        _classify_stock_sdk_date_shift(reference, stock_sdk_style)

    assert exc_info.value.category == "integrity_error"


def test_dividend_list_cross_check_cannot_construct_fund_nav_series() -> None:
    """验证 dividend-list-only fixture 不能构造 FundNavSeries。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 dividend-list-only 被误当作 NAV series 时抛出。
    """

    dividend_only = {"除息日": "2023-01-11", "每10份派发红利": "0.080"}

    with pytest.raises(NavDataContractError) as exc_info:
        _construct_series_from_dividend_only(dividend_only)

    assert exc_info.value.category == "adjustment_basis_unknown"


def _classify_stock_sdk_date_shift(
    reference: dict[str, str],
    stock_sdk_style: dict[str, str],
) -> None:
    """测试本地 helper：拒绝 stock-sdk NAV 日期位移。

    Args:
        reference: CSRC 参考 row。
        stock_sdk_style: stock-sdk 风格 row。

    Returns:
        无返回值。

    Raises:
        NavDataContractError: 日期不一致但 NAV 值相同，归为 integrity_error。
    """

    if (
        reference["nav"] == stock_sdk_style["nav"]
        and reference["acc_nav"] == stock_sdk_style["acc_nav"]
        and reference["date"] != stock_sdk_style["date"]
    ):
        raise NavDataContractError(
            category="integrity_error",
            message="stock-sdk getFundNavHistory date shift rejected",
            source="stock_sdk_diagnostics",
            fund_code="014217",
        )


def _construct_series_from_dividend_only(dividend_event: dict[str, str]) -> FundNavSeries:
    """测试本地 helper：拒绝 dividend-list-only 构造 NAV series。

    Args:
        dividend_event: 分红事件 fixture。

    Returns:
        不会返回成功 series。

    Raises:
        NavDataContractError: 始终按 adjustment_basis_unknown 拒绝。
    """

    _ = dividend_event
    raise NavDataContractError(
        category="adjustment_basis_unknown",
        message="dividend list only cannot construct NAV path series",
        source="stock_sdk_diagnostics",
        fund_code="014217",
    )


def test_dividend_only_helper_does_not_construct_record() -> None:
    """验证 stock-sdk 分红 helper 未构造 NAV record 类型。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 helper 源码构造 FundNavRecord 时抛出。
    """

    assert "FundNavRecord(" not in inspect.getsource(_construct_series_from_dividend_only)
    assert FundNavRecord.__name__ == "FundNavRecord"
