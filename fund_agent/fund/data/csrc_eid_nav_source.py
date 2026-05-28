"""CSRC EID 累计净值 source adapter。

本模块只负责通过证监会资本市场统一信息披露平台公开页面读取 A/C/E/F 份额
分类净值表，并返回 repository 内部 `_RawNavSourceResult`。它不计算模板第 6 章
回撤指标，也不把累计净值解释为 dividend-adjusted 或 total-return basis。
"""

from __future__ import annotations

import asyncio
import json
import re
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime, timezone
from html import unescape
from html.parser import HTMLParser
from typing import Final
from urllib.parse import parse_qs, urlencode, urlparse

import httpx

from fund_agent.fund.data.nav_models import NavDataContractError, NavFailureCategory
from fund_agent.fund.data.nav_source_contract import _RawNavSourceResult

_SOURCE_NAME: Final[str] = "csrc_eid"
_BASE_URL: Final[str] = "http://eid.csrc.gov.cn"
_SEARCH_PATH: Final[str] = "/fund/disclose/validate_fund.do"
_DETAIL_PATH: Final[str] = "/fund/disclose/fund_detail_search.do"
_CLASSIFICATION_PATH: Final[str] = "/fund/disclose/list_net_classification.do"
_PRODUCT_FUND_CODE: Final[str] = "006597"
_VERIFIED_FUND_ID: Final[str] = "5755"
_DEFAULT_LIMIT: Final[int] = 20
_MAX_ATTEMPTS: Final[int] = 3
_HTTP_TIMEOUT: Final[httpx.Timeout] = httpx.Timeout(
    connect=10.0,
    read=30.0,
    write=10.0,
    pool=10.0,
)
_EXPECTED_SHARE_CLASSES: Final[dict[str, tuple[str, str]]] = {
    "006597": ("A", "2030-1010"),
    "006598": ("C", "2030-1020"),
    "014217": ("E", "2030-1040"),
    "022176": ("F", "2030-1050"),
}
_SHARE_CLASS_TO_CODE: Final[dict[str, str]] = {
    share_class: fund_code for fund_code, (share_class, _) in _EXPECTED_SHARE_CLASSES.items()
}
_DATE_RE: Final[re.Pattern[str]] = re.compile(r"\d{4}-\d{2}-\d{2}")
_TOTAL_RE: Final[re.Pattern[str]] = re.compile(r"记录：\s*(\d+)\s*-\s*(\d+)\s*/\s*共\s*(\d+)条")
_PAGE_RE: Final[re.Pattern[str]] = re.compile(r"共\s*(\d+)页")


@dataclass(frozen=True, slots=True)
class _CsrcShareClass:
    """CSRC EID detail 页解析出的份额类别。

    Args:
        share_class: 份额类别字母。
        fund_code: 份额基金代码。
        fund_name: 份额名称。
        product_fund_code: 分类列表使用的产品基金代码。
        classification: EID 分类 ID。
        href: detail 页中的分类链接。

    Returns:
        dataclass 实例。

    Raises:
        无显式抛出。
    """

    share_class: str
    fund_code: str
    fund_name: str
    product_fund_code: str
    classification: str
    href: str


@dataclass(frozen=True, slots=True)
class _CsrcNetPage:
    """CSRC EID 分类净值分页解析结果。

    Args:
        rows: 当前页原始 rows。
        total_records: 分页声明的总记录数。
        range_start: 当前页首条 1-based 序号；无数据时为 0。
        range_end: 当前页末条 1-based 序号；无数据时为 0。
        total_pages: 分页声明页数。

    Returns:
        dataclass 实例。

    Raises:
        无显式抛出。
    """

    rows: list[dict[str, object]]
    total_records: int
    range_start: int
    range_end: int
    total_pages: int


class _TableParser(HTMLParser):
    """小型 HTML table/link parser。

    该 parser 只收集 `tr` 中的 `td` 文本和 `a[href]`，避免依赖 BeautifulSoup/lxml。
    """

    def __init__(self) -> None:
        """初始化 parser 状态。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        super().__init__()
        self.rows: list[list[str]] = []
        self.links: list[tuple[str, str, str]] = []
        self._in_tr = False
        self._in_td = False
        self._in_a = False
        self._current_row: list[str] = []
        self._current_cell_parts: list[str] = []
        self._current_link_parts: list[str] = []
        self._current_href: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """处理 HTML 起始标签。

        Args:
            tag: 标签名。
            attrs: 标签属性。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        attrs_dict = dict(attrs)
        if tag == "tr":
            self._in_tr = True
            self._current_row = []
        elif tag == "td" and self._in_tr:
            self._in_td = True
            self._current_cell_parts = []
        elif tag == "a":
            self._in_a = True
            self._current_href = attrs_dict.get("href")
            self._current_link_parts = []

    def handle_data(self, data: str) -> None:
        """收集文本节点。

        Args:
            data: 文本内容。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        if self._in_td:
            self._current_cell_parts.append(data)
        if self._in_a:
            self._current_link_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        """处理 HTML 结束标签。

        Args:
            tag: 标签名。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        if tag == "td" and self._in_td:
            self._current_row.append(_clean_text("".join(self._current_cell_parts)))
            self._in_td = False
        elif tag == "tr" and self._in_tr:
            if self._current_row:
                self.rows.append(self._current_row)
            self._in_tr = False
        elif tag == "a" and self._in_a:
            if self._current_href:
                link_text = _clean_text("".join(self._current_link_parts))
                row_context = _clean_text(
                    " ".join((*self._current_row, "".join(self._current_cell_parts), link_text))
                )
                self.links.append((link_text, self._current_href, row_context))
            self._in_a = False
            self._current_href = None


class CsrcEidNavSource:
    """CSRC EID 累计净值 source adapter。

    默认无缓存、无 fallback。任何 CSRC EID 已分类失败直接以
    `NavDataContractError` 向 repository 传播。
    """

    def __init__(
        self,
        *,
        base_url: str = _BASE_URL,
        client_factory: Callable[[], httpx.AsyncClient] | None = None,
        limit: int = _DEFAULT_LIMIT,
    ) -> None:
        """初始化 CSRC EID source adapter。

        Args:
            base_url: EID 站点根 URL。
            client_factory: 可注入 HTTP client factory；测试可传入 MockTransport。
            limit: 分类净值列表分页大小。

        Returns:
            无返回值。

        Raises:
            ValueError: limit 非正时抛出。
        """

        if limit < 1:
            raise ValueError("limit 必须为正整数")
        self._base_url = base_url.rstrip("/")
        self._client_factory = client_factory or self._default_client_factory
        self._limit = limit

    async def load_raw_nav_source(
        self,
        fund_code: str,
        *,
        share_class: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        force_refresh: bool = False,
    ) -> _RawNavSourceResult:
        """读取 CSRC EID 分类累计净值 raw rows。

        Args:
            fund_code: 请求基金代码。
            share_class: 请求份额类别；为空时按基金代码解析。
            start_date: 请求日期窗口起点；adapter 记录显式参数，窗口完整性由 repository 校验。
            end_date: 请求日期窗口终点；adapter 记录显式参数，窗口完整性由 repository 校验。
            force_refresh: 是否强制刷新；当前 CSRC adapter 无缓存，参数仅显式记录兼容。

        Returns:
            `_RawNavSourceResult`，其中 `source_nav_type="accumulated_nav"`。

        Raises:
            NavDataContractError: 当 search/detail/list 失败或身份、schema、完整性不满足时抛出。
        """

        normalized_fund_code = _normalize_fund_code(fund_code)
        normalized_share_class = _normalize_optional_share_class(share_class)
        async with self._client_factory() as client:
            fund_id = await self._resolve_fund_id(client, normalized_fund_code)
            detail_html = await self._request_text(
                client,
                "GET",
                self._url(_DETAIL_PATH),
                params={"cFundCode": fund_id},
            )
            share_classes = _parse_detail_share_classes(detail_html)
            selected = _select_share_class(
                requested_fund_code=normalized_fund_code,
                requested_share_class=normalized_share_class,
                fund_id=fund_id,
                share_classes=share_classes,
            )
            rows, query_params, source_url = await self._load_all_pages(
                client=client,
                selected=selected,
                start_date=start_date,
                end_date=end_date,
                force_refresh=force_refresh,
            )
        return _RawNavSourceResult(
            fund_code=selected.fund_code,
            records=rows,
            source=_SOURCE_NAME,
            origin_source=_SOURCE_NAME,
            source_id=f"{fund_id}:{selected.classification}",
            source_url=source_url,
            source_query_params=query_params,
            source_nav_type="accumulated_nav",
            source_adjustment_basis="accumulated_nav",
            cached=False,
            retrieved_at=datetime.now(timezone.utc).isoformat(),
            cache_updated_at=None,
        )

    def _default_client_factory(self) -> httpx.AsyncClient:
        """创建默认 HTTP client。

        Args:
            无。

        Returns:
            配置 timeout、headers 和重定向的 `httpx.AsyncClient`。

        Raises:
            无显式抛出。
        """

        return httpx.AsyncClient(
            timeout=_HTTP_TIMEOUT,
            follow_redirects=True,
            headers={
                "User-Agent": "fund-agent/0 CSRC-EID NAV adapter",
                "Accept": "text/html,application/json;q=0.9,*/*;q=0.8",
            },
        )

    def _url(self, path: str) -> str:
        """构造 EID endpoint URL。

        Args:
            path: endpoint path。

        Returns:
            完整 URL。

        Raises:
            无显式抛出。
        """

        return f"{self._base_url}{path}"

    async def _resolve_fund_id(self, client: httpx.AsyncClient, fund_code: str) -> str:
        """通过 public search 解析 EID internal fundId。

        Args:
            client: HTTP client。
            fund_code: 请求基金代码。

        Returns:
            EID internal fundId。

        Raises:
            NavDataContractError: search 不可用、schema 漂移或身份不匹配时抛出。
        """

        try:
            text = await self._request_text(
                client,
                "POST",
                self._url(_SEARCH_PATH),
                data={"cFundCode": fund_code},
            )
            fund_id = _parse_search_fund_id(text)
        except NavDataContractError as exc:
            if fund_code != "022176":
                raise
            if exc.category not in {"not_found", "schema_drift"}:
                raise
            # F 类 direct-search 缺口是已接受来源限制；回退到产品锚点后仍必须由 detail 验证 F。
            text = await self._request_text(
                client,
                "POST",
                self._url(_SEARCH_PATH),
                data={"cFundCode": _PRODUCT_FUND_CODE},
            )
            fund_id = _parse_search_fund_id(text)
        if fund_id != _VERIFIED_FUND_ID:
            _raise_contract_error(
                category="identity_mismatch",
                message=f"CSRC EID fundId 与 accepted identity 不匹配: {fund_id!r}。",
                fund_code=fund_code,
            )
        return fund_id

    async def _load_all_pages(
        self,
        *,
        client: httpx.AsyncClient,
        selected: _CsrcShareClass,
        start_date: date | None,
        end_date: date | None,
        force_refresh: bool,
    ) -> tuple[list[dict[str, object]], tuple[tuple[str, str], ...], str]:
        """读取并校验全部分页。

        Args:
            client: HTTP client。
            selected: 已验证份额分类。
            start_date: 显式日期窗口起点。
            end_date: 显式日期窗口终点。
            force_refresh: 当前无缓存，仅记录显式参数。

        Returns:
            `(rows, source_query_params, source_url)`。

        Raises:
            NavDataContractError: 分页 schema 或完整性不满足时抛出。
        """

        rows: list[dict[str, object]] = []
        expected_total: int | None = None
        total_pages: int | None = None
        start = 0
        base_params = {
            "fundCode": selected.product_fund_code,
            "classification": selected.classification,
            "limit": str(self._limit),
        }
        source_url = f"{self._url(_CLASSIFICATION_PATH)}?{urlencode(base_params)}"
        while True:
            params = {**base_params, "start": str(start)}
            html = await self._request_text(client, "GET", self._url(_CLASSIFICATION_PATH), params=params)
            page = _parse_net_page(
                html,
                source=_SOURCE_NAME,
                fund_code=selected.fund_code,
                share_class=selected.share_class,
                classification=selected.classification,
            )
            if expected_total is None:
                expected_total = page.total_records
                total_pages = page.total_pages
                if expected_total == 0:
                    _raise_contract_error(
                        category="not_found",
                        message="CSRC EID verified identity 后分类净值表为空。",
                        fund_code=selected.fund_code,
                    )
            elif page.total_records != expected_total or page.total_pages != total_pages:
                _raise_contract_error(
                    category="integrity_error",
                    message="CSRC EID pagination total 在翻页过程中变化。",
                    fund_code=selected.fund_code,
                )
            expected_start = start + 1
            expected_end = min(start + self._limit, expected_total)
            expected_count = expected_end - start
            if page.range_start != expected_start or page.range_end != expected_end:
                _raise_contract_error(
                    category="integrity_error",
                    message="CSRC EID pagination 当前页范围与 start/limit 不一致。",
                    fund_code=selected.fund_code,
                )
            if len(page.rows) != expected_count:
                _raise_contract_error(
                    category="integrity_error",
                    message="CSRC EID pagination 当前页 row 数与声明范围不一致。",
                    fund_code=selected.fund_code,
                )
            rows.extend(page.rows)
            if len(rows) >= expected_total:
                break
            start += self._limit
            await asyncio.sleep(0)
        if len(rows) != expected_total:
            _raise_contract_error(
                category="integrity_error",
                message="CSRC EID pagination 总 row 数与声明 total 不一致。",
                fund_code=selected.fund_code,
            )
        query_params = (
            ("fundCode", selected.product_fund_code),
            ("classification", selected.classification),
            ("limit", str(self._limit)),
            ("start", "0"),
            ("requested_fund_code", selected.fund_code),
            ("share_class", selected.share_class),
            ("force_refresh", str(force_refresh)),
        )
        if start_date is not None:
            query_params += (("start_date", start_date.isoformat()),)
        if end_date is not None:
            query_params += (("end_date", end_date.isoformat()),)
        return rows, query_params, source_url

    async def _request_text(
        self,
        client: httpx.AsyncClient,
        method: str,
        url: str,
        *,
        params: dict[str, str] | None = None,
        data: dict[str, str] | None = None,
    ) -> str:
        """执行 HTTP 请求并按 CSRC EID taxonomy 分类失败。

        Args:
            client: HTTP client。
            method: `GET` 或 `POST`。
            url: 请求 URL。
            params: GET 查询参数。
            data: POST 表单参数。

        Returns:
            响应文本。

        Raises:
            NavDataContractError: 网络、HTTP 或空响应失败。
        """

        last_error: Exception | None = None
        for attempt_index in range(_MAX_ATTEMPTS):
            try:
                response = await _send_request(client, method, url, params=params, data=data)
                if response.status_code >= 500:
                    raise _TransientHttpError(f"CSRC EID 服务端错误 {response.status_code}: {url}")
                if response.status_code != 200:
                    _raise_contract_error(
                        category="unavailable",
                        message=f"CSRC EID 请求失败 {response.status_code}: {url}",
                        fund_code=None,
                    )
                if not response.text.strip():
                    _raise_contract_error(
                        category="schema_drift",
                        message=f"CSRC EID 空响应: {url}",
                        fund_code=None,
                    )
                return response.text
            except _TransientHttpError as exc:
                last_error = exc
            except (httpx.TimeoutException, httpx.TransportError) as exc:
                last_error = exc
            if attempt_index < _MAX_ATTEMPTS - 1:
                await asyncio.sleep(0)
        raise NavDataContractError(
            category="unavailable",
            message=f"CSRC EID HTTP/network 不可用: {last_error}",
            source=_SOURCE_NAME,
            fund_code=None,
            cause=last_error,
        ) from last_error


class _TransientHttpError(Exception):
    """CSRC EID 可重试 HTTP 5xx 错误。"""


async def _send_request(
    client: httpx.AsyncClient,
    method: str,
    url: str,
    *,
    params: dict[str, str] | None,
    data: dict[str, str] | None,
) -> httpx.Response:
    """发送单次 HTTP 请求。

    Args:
        client: HTTP client。
        method: 请求方法。
        url: 请求 URL。
        params: GET 查询参数。
        data: POST 表单参数。

    Returns:
        HTTP 响应。

    Raises:
        httpx.HTTPError: httpx 底层请求异常。
        NavDataContractError: method 非法时抛出。
    """

    if method == "POST":
        return await client.post(url, data=data)
    if method == "GET":
        return await client.get(url, params=params)
    _raise_contract_error(
        category="schema_drift",
        message=f"CSRC EID adapter HTTP method 非法: {method!r}",
        fund_code=None,
    )


def _parse_search_fund_id(text: str) -> str:
    """解析 search endpoint fundId。

    Args:
        text: search endpoint 响应文本。

    Returns:
        fundId 字符串。

    Raises:
        NavDataContractError: JSON schema 或业务结果不满足时抛出。
    """

    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise NavDataContractError(
            category="schema_drift",
            message="CSRC EID search 响应不是合法 JSON。",
            source=_SOURCE_NAME,
            fund_code=None,
            cause=exc,
        ) from exc
    if not isinstance(payload, dict):
        _raise_contract_error(
            category="schema_drift",
            message="CSRC EID search JSON 不是对象。",
            fund_code=None,
        )
    if payload.get("isSuccess") is not True:
        _raise_contract_error(
            category="not_found",
            message="CSRC EID search 未找到匹配基金。",
            fund_code=None,
        )
    fund_id = payload.get("fundId")
    if fund_id is None or str(fund_id).strip() == "":
        _raise_contract_error(
            category="schema_drift",
            message="CSRC EID search 缺少 fundId。",
            fund_code=None,
        )
    return str(fund_id).strip()


def _parse_detail_share_classes(html: str) -> dict[str, _CsrcShareClass]:
    """解析 detail 页 A/C/E/F 份额分类链接。

    Args:
        html: detail 页 HTML。

    Returns:
        以 fund code 为 key 的份额分类映射。

    Raises:
        NavDataContractError: detail schema 漂移或缺少已接受份额分类时抛出。
    """

    parser = _TableParser()
    parser.feed(html)
    share_classes: dict[str, _CsrcShareClass] = {}
    for link_text, href, row_context in parser.links:
        if _CLASSIFICATION_PATH.rsplit("/", 1)[-1] not in href:
            continue
        query = parse_qs(urlparse(unescape(href)).query)
        classification = _single_query_value(query, "classification")
        product_fund_code = _single_query_value(query, "fundCode")
        if classification is None or product_fund_code is None:
            continue
        parsed = _parse_share_class_from_text(f"{row_context} {link_text}")
        if parsed is None:
            continue
        fund_name, fund_code, share_class = parsed
        share_classes[fund_code] = _CsrcShareClass(
            share_class=share_class,
            fund_code=fund_code,
            fund_name=fund_name,
            product_fund_code=product_fund_code,
            classification=classification,
            href=href,
        )
    missing = sorted(set(_EXPECTED_SHARE_CLASSES) - set(share_classes))
    if missing:
        _raise_contract_error(
            category="identity_mismatch",
            message=f"CSRC EID detail 缺少已接受份额分类: {', '.join(missing)}。",
            fund_code=None,
        )
    return share_classes


def _parse_share_class_from_text(text: str) -> tuple[str, str, str] | None:
    """从 detail 文本解析份额名称、代码和类别。

    Args:
        text: detail 上下文文本。

    Returns:
        `(fund_name, fund_code, share_class)`；无法解析时返回 `None`。

    Raises:
        无显式抛出。
    """

    match = re.search(r"净值日报\s*([^()（）]+)[(（](\d{6})[)）]", text)
    if match is None:
        match = re.search(r"([^()（）\s]+)[(（](\d{6})[)）]", text)
    if match is None:
        return None
    fund_name = _clean_text(match.group(1))
    fund_code = match.group(2)
    expected = _EXPECTED_SHARE_CLASSES.get(fund_code)
    if expected is None:
        return None
    share_class = expected[0]
    if not fund_name.endswith(share_class):
        return None
    return fund_name, fund_code, share_class


def _select_share_class(
    *,
    requested_fund_code: str,
    requested_share_class: str | None,
    fund_id: str,
    share_classes: dict[str, _CsrcShareClass],
) -> _CsrcShareClass:
    """验证并选择请求的份额分类。

    Args:
        requested_fund_code: 请求基金代码。
        requested_share_class: 请求份额类别；为空时按代码映射。
        fund_id: EID internal fundId。
        share_classes: detail 页解析出的份额映射。

    Returns:
        选中的份额分类。

    Raises:
        NavDataContractError: 代码/份额冲突或分类 identity 不匹配时抛出。
    """

    if fund_id != _VERIFIED_FUND_ID:
        _raise_contract_error(
            category="identity_mismatch",
            message=f"CSRC EID detail fundId 非 accepted 5755: {fund_id!r}。",
            fund_code=requested_fund_code,
        )
    expected = _EXPECTED_SHARE_CLASSES.get(requested_fund_code)
    if expected is None:
        _raise_contract_error(
            category="not_found",
            message=f"CSRC EID adapter 当前未验证该 fund_code: {requested_fund_code}。",
            fund_code=requested_fund_code,
        )
    expected_share_class, expected_classification = expected
    if requested_share_class is not None and requested_share_class != expected_share_class:
        _raise_contract_error(
            category="identity_mismatch",
            message=(
                "请求基金代码与 share_class 冲突: "
                f"{requested_fund_code} 应为 {expected_share_class}，收到 {requested_share_class}。"
            ),
            fund_code=requested_fund_code,
        )
    selected = share_classes.get(requested_fund_code)
    if selected is None:
        _raise_contract_error(
            category="identity_mismatch",
            message=f"CSRC EID detail 未返回请求份额代码 {requested_fund_code}。",
            fund_code=requested_fund_code,
        )
    if (
        selected.share_class != expected_share_class
        or selected.classification != expected_classification
        or selected.product_fund_code != _PRODUCT_FUND_CODE
    ):
        _raise_contract_error(
            category="identity_mismatch",
            message=(
                "CSRC EID detail 分类与 accepted identity 不匹配: "
                f"{selected.fund_code}/{selected.share_class}/{selected.classification}。"
            ),
            fund_code=requested_fund_code,
        )
    return selected


def _parse_net_page(
    html: str,
    *,
    source: str,
    fund_code: str,
    share_class: str,
    classification: str,
) -> _CsrcNetPage:
    """解析 CSRC EID 分类净值页面。

    Args:
        html: 分类净值 HTML。
        source: 来源名称。
        fund_code: 份额基金代码。
        share_class: 份额类别。
        classification: EID 分类 ID。

    Returns:
        当前分页记录与分页声明。

    Raises:
        NavDataContractError: 表头、行、分页 schema 不满足时抛出。
    """

    parser = _TableParser()
    parser.feed(html)
    header_index = _find_header_index(parser.rows)
    header = tuple(_normalize_header_cell(cell) for cell in parser.rows[header_index])
    rows: list[dict[str, object]] = []
    for row in parser.rows[header_index + 1 :]:
        if len(row) != len(header):
            continue
        row_dict = dict(zip(header, row, strict=True))
        if not _row_looks_like_nav_record(row_dict):
            continue
        if row_dict.get("基金代码") != _PRODUCT_FUND_CODE or row_dict.get("分级代码") != fund_code:
            _raise_contract_error(
                category="identity_mismatch",
                message="CSRC EID 分类净值 row 基金代码与请求份额不匹配。",
                fund_code=fund_code,
            )
        row_dict["基金代码"] = fund_code
        row_dict["产品基金代码"] = _PRODUCT_FUND_CODE
        row_dict["基金名称"] = row_dict.get("基金简称", "")
        row_dict["份额类别"] = share_class
        row_dict["classification"] = classification
        rows.append(row_dict)
    total_match = _TOTAL_RE.search(html)
    page_match = _PAGE_RE.search(_clean_text(html))
    if total_match is None or page_match is None:
        _raise_contract_error(
            category="schema_drift",
            message="CSRC EID 分类净值页缺少分页 total 声明。",
            fund_code=fund_code,
        )
    range_start, range_end, total_records = (int(total_match.group(i)) for i in (1, 2, 3))
    total_pages = int(page_match.group(1))
    if total_records < 0 or range_start < 0 or range_end < range_start:
        _raise_contract_error(
            category="integrity_error",
            message="CSRC EID 分类净值分页数字非法。",
            fund_code=fund_code,
        )
    return _CsrcNetPage(
        rows=rows,
        total_records=total_records,
        range_start=range_start,
        range_end=range_end,
        total_pages=total_pages,
    )


def _find_header_index(rows: list[list[str]]) -> int:
    """定位分类净值表头。

    Args:
        rows: HTML table rows。

    Returns:
        表头 row index。

    Raises:
        NavDataContractError: 找不到必需表头时抛出。
    """

    required = {"基金代码", "分级代码", "基金简称", "单位净值", "累计净值", "估值日期"}
    for index, row in enumerate(rows):
        normalized = {_normalize_header_cell(cell) for cell in row}
        if required.issubset(normalized):
            return index
    _raise_contract_error(
        category="schema_drift",
        message="CSRC EID 分类净值页缺少必需表头。",
        fund_code=None,
    )


def _normalize_header_cell(cell: str) -> str:
    """规范化表头字段名。

    Args:
        cell: 原始表头。

    Returns:
        规范化表头。

    Raises:
        无显式抛出。
    """

    normalized = _clean_text(cell).replace(" ", "")
    if normalized == "份额净值":
        return "单位净值"
    return normalized


def _row_looks_like_nav_record(row: dict[str, str]) -> bool:
    """判断 row 是否是净值数据行。

    Args:
        row: 表格 row dict。

    Returns:
        是净值行时返回 True。

    Raises:
        无显式抛出。
    """

    value = row.get("估值日期", "")
    return bool(_DATE_RE.fullmatch(value.strip()))


def _single_query_value(query: dict[str, list[str]], key: str) -> str | None:
    """读取单值 query 参数。

    Args:
        query: `parse_qs` 输出。
        key: 参数名。

    Returns:
        单个参数值；不存在或空时返回 `None`。

    Raises:
        无显式抛出。
    """

    values = query.get(key)
    if not values:
        return None
    value = values[0].strip()
    return value or None


def _normalize_fund_code(fund_code: str) -> str:
    """规范化基金代码。

    Args:
        fund_code: 原始基金代码。

    Returns:
        6 位基金代码。

    Raises:
        NavDataContractError: 基金代码非法时抛出。
    """

    normalized = str(fund_code).strip()
    if not normalized or not normalized.isdigit() or len(normalized) != 6:
        _raise_contract_error(
            category="identity_mismatch",
            message=f"基金代码非法: {fund_code!r}",
            fund_code=normalized or None,
        )
    return normalized


def _normalize_optional_share_class(share_class: str | None) -> str | None:
    """规范化可选份额类别。

    Args:
        share_class: 原始份额类别。

    Returns:
        大写份额类别或 `None`。

    Raises:
        NavDataContractError: 份额类别非法时抛出。
    """

    if share_class is None:
        return None
    normalized = share_class.strip().upper()
    if normalized not in _SHARE_CLASS_TO_CODE:
        _raise_contract_error(
            category="identity_mismatch",
            message=f"CSRC EID 未验证份额类别: {share_class!r}",
            fund_code=None,
        )
    return normalized


def _clean_text(value: str) -> str:
    """清理 HTML 文本空白。

    Args:
        value: 原始文本。

    Returns:
        空白压缩后的文本。

    Raises:
        无显式抛出。
    """

    return " ".join(unescape(value).split())


def _raise_contract_error(
    *,
    category: NavFailureCategory,
    message: str,
    fund_code: str | None,
) -> None:
    """抛出 CSRC EID NAV 数据契约错误。

    Args:
        category: 失败分类。
        message: 错误说明。
        fund_code: 相关基金代码。

    Returns:
        无返回值。

    Raises:
        NavDataContractError: 始终抛出。
    """

    raise NavDataContractError(
        category=category,
        message=message,
        source=_SOURCE_NAME,
        fund_code=fund_code,
    )


__all__ = ["CsrcEidNavSource"]
