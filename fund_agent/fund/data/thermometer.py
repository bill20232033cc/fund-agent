"""有知有行温度计数据适配器。

本模块属于 Agent 层基金能力的 data 层，负责读取有知有行公开数据页、
解析市场温度计数据并维护自身缓存。它不依赖 UI、Service 或 Engine，
也不把温度计结果直接写入分析结论。
"""

from __future__ import annotations

import asyncio
import html
import json
import re
from collections.abc import Awaitable, Callable
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Final

from fund_agent.config.paths import DEFAULT_THERMOMETER_CACHE_ROOT

THERMOMETER_CACHE_ROOT: Final[Path] = DEFAULT_THERMOMETER_CACHE_ROOT
THERMOMETER_CACHE_FILENAME: Final[str] = "thermometer.json"
THERMOMETER_DATA_URL: Final[str] = "https://youzhiyouxing.cn/data"
THERMOMETER_MACRO_URL: Final[str] = "https://youzhiyouxing.cn/data/macro"
THERMOMETER_FRESH_TTL: Final[timedelta] = timedelta(hours=24)
THERMOMETER_STALE_TTL: Final[timedelta] = timedelta(days=7)

ThermometerFetcher = Callable[[str], Awaitable[str] | str]

_TAG_PATTERN: Final[re.Pattern[str]] = re.compile(r"<[^>]+>")
_SCRIPT_STYLE_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"<(script|style)\b[^>]*>.*?</\1>",
    re.IGNORECASE | re.DOTALL,
)
_TABLE_ROW_PATTERN: Final[re.Pattern[str]] = re.compile(r"<tr\b[^>]*>(.*?)</tr>", re.IGNORECASE | re.DOTALL)
_TABLE_CELL_PATTERN: Final[re.Pattern[str]] = re.compile(r"<t[dh]\b[^>]*>(.*?)</t[dh]>", re.IGNORECASE | re.DOTALL)
_NUMBER_PATTERN: Final[re.Pattern[str]] = re.compile(r"[-+]?\d+(?:\.\d+)?")
_DATE_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"\d{4}(?:[-/.年]\d{1,2}(?:[-/.月]\d{1,2}日?)?)(?:\s+\d{1,2}:\d{2})?"
)
_INDEX_CODE_PATTERN: Final[re.Pattern[str]] = re.compile(r"\b\d{6}\b")
_MARKET_LABELS: Final[tuple[str, ...]] = ("全市场温度", "全市场估值温度", "A股温度", "市场温度")
_BOND_LABELS: Final[tuple[str, ...]] = ("债券温度", "债市温度", "债券市场温度")
_TREASURY_YIELD_LABELS: Final[tuple[str, ...]] = (
    "10年期国债收益率",
    "10年期国债到期收益率",
    "十年期国债收益率",
    "十年期国债到期收益率",
    "10Y国债收益率",
)


@dataclass(frozen=True, slots=True)
class MarketTemperature:
    """全市场温度计数据。

    Attributes:
        value: 全市场温度数值。
        valuation_band: 估值区间或估值标签。
        trend_text: 页面披露的趋势文本。
    """

    value: Decimal | None
    valuation_band: str | None
    trend_text: str | None


@dataclass(frozen=True, slots=True)
class IndexTemperature:
    """指数温度计行数据。

    Attributes:
        name: 指数名称。
        code: 指数代码。
        temperature: 指数温度。
        intrinsic_return: 内在收益率。
        dividend_yield: 股息率。
    """

    name: str
    code: str
    temperature: Decimal | None
    intrinsic_return: Decimal | None
    dividend_yield: Decimal | None


@dataclass(frozen=True, slots=True)
class MacroTemperature:
    """宏观温度计数据。

    Attributes:
        bond_temperature: 债券温度。
        ten_year_treasury_yield: 10 年期国债收益率。
    """

    bond_temperature: Decimal | None
    ten_year_treasury_yield: Decimal | None


@dataclass(frozen=True, slots=True)
class ThermometerSnapshot:
    """温度计快照。

    Attributes:
        as_of_text: 页面披露的更新时间原文。
        as_of_date: 从更新时间中解析出的日期文本。
        market: 全市场温度计数据。
        indexes: 指数温度计行。
        macro: 宏观温度计数据。
        source: 数据来源。
        cached: 是否来自缓存。
        stale: 是否超过 24h fresh TTL。
        unavailable: 当前数据是否不可用。
        unavailable_reason: 不可用原因。
        fetched_at: 抓取或缓存写入的 UTC 时间。
    """

    as_of_text: str | None
    as_of_date: str | None
    market: MarketTemperature | None
    indexes: tuple[IndexTemperature, ...]
    macro: MacroTemperature | None
    source: str
    cached: bool
    stale: bool
    unavailable: bool
    unavailable_reason: str | None
    fetched_at: str | None


async def _default_fetcher(url: str) -> str:
    """默认 HTTP 抓取函数。

    Args:
        url: 待抓取的公开页面 URL。

    Returns:
        页面 HTML 文本。

    Raises:
        ImportError: httpx 不可用时抛出。
        httpx.HTTPError: 请求失败时抛出。
    """

    import httpx

    headers = {"User-Agent": "FundAgent/0.1 (+https://youzhiyouxing.cn/data)"}
    async with httpx.AsyncClient(headers=headers, timeout=10.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.text


class FundThermometerAdapter:
    """有知有行温度计数据适配器。

    该适配器维护 24h fresh cache，并在抓取失败时使用 7 天内 stale cache。
    无可用缓存时返回 `unavailable=True` 的快照，而不是向上抛出抓取或解析异常。
    """

    def __init__(
        self,
        root_dir: Path | None = None,
        fetcher: ThermometerFetcher | None = None,
        data_url: str = THERMOMETER_DATA_URL,
        macro_url: str = THERMOMETER_MACRO_URL,
    ) -> None:
        """初始化温度计适配器。

        Args:
            root_dir: 缓存目录；未提供时使用 `cache/thermometer`。
            fetcher: 可注入页面抓取函数；未提供时使用 httpx。
            data_url: 有知有行数据页 URL。
            macro_url: 有知有行宏观数据页 URL。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self.root_dir = root_dir or THERMOMETER_CACHE_ROOT
        self.cache_path = self.root_dir / THERMOMETER_CACHE_FILENAME
        self._fetcher = fetcher or _default_fetcher
        self._data_url = data_url
        self._macro_url = macro_url

    async def load_thermometer(self, *, force_refresh: bool = False) -> ThermometerSnapshot:
        """读取温度计快照。

        Args:
            force_refresh: 是否绕过 fresh cache 强制抓取。

        Returns:
            温度计快照；抓取或解析失败且无缓存时返回 unavailable 快照。

        Raises:
            OSError: 缓存目录创建失败时抛出。
        """

        self.root_dir.mkdir(parents=True, exist_ok=True)
        cached_payload = await asyncio.to_thread(self._load_cache_payload)
        if not force_refresh and cached_payload is not None and _cache_age(cached_payload) <= THERMOMETER_FRESH_TTL:
            return _snapshot_from_cache(cached_payload, stale=False)

        try:
            data_html = await self._call_fetcher(self._data_url)
            macro_html = await self._call_fetcher(self._macro_url)
            snapshot = parse_thermometer_pages(data_html, macro_html, fetched_at=_utc_timestamp())
            if snapshot.unavailable:
                raise ValueError(snapshot.unavailable_reason or "温度计页面解析失败")
            try:
                await asyncio.to_thread(self._save_snapshot, snapshot)
            except OSError:
                pass
            return snapshot
        except Exception as exc:
            if cached_payload is not None and _cache_age(cached_payload) <= THERMOMETER_STALE_TTL:
                stale = _cache_age(cached_payload) > THERMOMETER_FRESH_TTL
                return _snapshot_from_cache(cached_payload, stale=stale)
            return _unavailable_snapshot(f"温度计数据不可用：{exc}")

    async def _call_fetcher(self, url: str) -> str:
        """调用页面抓取函数。

        Args:
            url: 待抓取 URL。

        Returns:
            页面 HTML 文本。

        Raises:
            TypeError: 抓取结果不是字符串时抛出。
            Exception: 允许注入抓取函数传播异常。
        """

        payload = self._fetcher(url)
        if asyncio.iscoroutine(payload):
            payload = await payload
        if not isinstance(payload, str):
            raise TypeError("温度计抓取结果必须是 HTML 字符串")
        return payload

    def _load_cache_payload(self) -> dict[str, object] | None:
        """读取缓存 JSON。

        Args:
            无。

        Returns:
            缓存 payload；不存在或格式非法时返回 `None`。

        Raises:
            无显式抛出。
        """

        if not self.cache_path.exists():
            return None
        try:
            payload = json.loads(self.cache_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None
        return payload if isinstance(payload, dict) else None

    def _save_snapshot(self, snapshot: ThermometerSnapshot) -> None:
        """写入温度计快照缓存。

        Args:
            snapshot: 温度计快照。

        Returns:
            无返回值。

        Raises:
            OSError: 写入缓存失败时抛出。
        """

        self.cache_path.write_text(json.dumps(_snapshot_to_cache_payload(snapshot), ensure_ascii=False, indent=2), encoding="utf-8")


def parse_thermometer_pages(
    data_html: str,
    macro_html: str | None = None,
    *,
    fetched_at: str | None = None,
) -> ThermometerSnapshot:
    """解析有知有行温度计页面。

    Args:
        data_html: `https://youzhiyouxing.cn/data` 页面 HTML。
        macro_html: `https://youzhiyouxing.cn/data/macro` 页面 HTML。
        fetched_at: 抓取时间。

    Returns:
        温度计快照；无法解析关键数据时返回 unavailable 快照。

    Raises:
        无显式抛出。
    """

    normalized_data_text = _normalize_html_text(data_html)
    normalized_macro_text = _normalize_html_text(macro_html or "")
    as_of_text = _extract_as_of_text(normalized_data_text) or _extract_as_of_text(normalized_macro_text)
    market = _parse_market_temperature(normalized_data_text)
    indexes = _parse_index_temperatures(data_html)
    macro = _parse_macro_temperature(normalized_macro_text)
    if market is None and not indexes and macro is None:
        return _unavailable_snapshot("解析失败：温度计页面缺少可解析的市场、指数或宏观数据", fetched_at=fetched_at)
    return ThermometerSnapshot(
        as_of_text=as_of_text,
        as_of_date=_extract_date_text(as_of_text),
        market=market,
        indexes=indexes,
        macro=macro,
        source="youzhiyouxing",
        cached=False,
        stale=False,
        unavailable=False,
        unavailable_reason=None,
        fetched_at=fetched_at or _utc_timestamp(),
    )


def _parse_market_temperature(text: str) -> MarketTemperature | None:
    """解析全市场温度计数据。

    Args:
        text: 归一化页面文本。

    Returns:
        全市场温度计数据；无法解析温度时返回 `None`。

    Raises:
        无显式抛出。
    """

    value = _degree_after_heading(text, _MARKET_LABELS) or _decimal_after_labels(text, _MARKET_LABELS)
    if value is None:
        return None
    return MarketTemperature(
        value=value,
        valuation_band=_extract_valuation_band(text),
        trend_text=_extract_market_trend_text(text),
    )


def _parse_index_temperatures(html_text: str) -> tuple[IndexTemperature, ...]:
    """解析指数温度表。

    Args:
        html_text: 页面 HTML。

    Returns:
        指数温度行元组。

    Raises:
        无显式抛出。
    """

    rows = _extract_table_rows(html_text)
    if not rows:
        return ()
    header_index = _find_index_table_header(rows)
    if header_index is None:
        return ()
    header = rows[header_index]
    header_positions = _header_positions(header)
    index_rows: list[IndexTemperature] = []
    for row in rows[header_index + 1 :]:
        parsed_row = _parse_index_row(row, header_positions)
        if parsed_row is not None:
            index_rows.append(parsed_row)
    return tuple(index_rows)


def _find_index_table_header(rows: tuple[tuple[str, ...], ...]) -> int | None:
    """定位指数温度表头。

    Args:
        rows: 页面中提取出的所有表格行。

    Returns:
        指数温度表头行位置；无法定位时返回 `None`。

    Raises:
        无显式抛出。
    """

    for row_index, row in enumerate(rows):
        joined = " ".join(row)
        if ("指数名称" in joined or "指数" in joined) and "温度" in joined and ("内在" in joined or "股息" in joined):
            return row_index
    return None


def _parse_index_row(row: tuple[str, ...], header_positions: dict[str, int]) -> IndexTemperature | None:
    """解析单个指数温度表行。

    Args:
        row: HTML 表格单行单元格文本。
        header_positions: 表头字段位置。

    Returns:
        指数温度行；无法识别指数代码时返回 `None`。

    Raises:
        无显式抛出。
    """

    code_index = header_positions.get("code", header_positions.get("name", 0))
    if len(row) <= code_index:
        return None
    code_match = _INDEX_CODE_PATTERN.search(row[code_index]) or _INDEX_CODE_PATTERN.search(" ".join(row))
    if code_match is None:
        return None
    name = _cell_at(row, header_positions.get("name", 0))
    if not name:
        return None
    return IndexTemperature(
        name=_remove_index_code(name),
        code=code_match.group(0),
        temperature=_decimal_from_cell(row, header_positions.get("temperature", 2)),
        intrinsic_return=_decimal_from_cell(row, header_positions.get("intrinsic_return", 3)),
        dividend_yield=_decimal_from_cell(row, header_positions.get("dividend_yield", 4)),
    )


def _parse_macro_temperature(text: str) -> MacroTemperature | None:
    """解析宏观页面温度计数据。

    Args:
        text: 归一化宏观页面文本。

    Returns:
        宏观温度数据；无法解析任何字段时返回 `None`。

    Raises:
        无显式抛出。
    """

    bond_temperature = _decimal_after_labels(text, _BOND_LABELS)
    ten_year_yield = _decimal_after_labels(text, _TREASURY_YIELD_LABELS)
    if bond_temperature is None and ten_year_yield is None:
        return None
    return MacroTemperature(
        bond_temperature=bond_temperature,
        ten_year_treasury_yield=ten_year_yield,
    )


def _extract_table_rows(html_text: str) -> tuple[tuple[str, ...], ...]:
    """从 HTML 中提取表格行。

    Args:
        html_text: 页面 HTML。

    Returns:
        表格行元组。

    Raises:
        无显式抛出。
    """

    rows: list[tuple[str, ...]] = []
    for row_match in _TABLE_ROW_PATTERN.finditer(html_text):
        cells = tuple(
            _normalize_plain_text(cell_match.group(1))
            for cell_match in _TABLE_CELL_PATTERN.finditer(row_match.group(1))
        )
        if cells:
            rows.append(cells)
    return tuple(rows)


def _header_positions(header: tuple[str, ...]) -> dict[str, int]:
    """识别指数表头字段位置。

    Args:
        header: 表头单元格文本。

    Returns:
        字段名到列位置的映射。

    Raises:
        无显式抛出。
    """

    positions: dict[str, int] = {}
    for index, cell in enumerate(header):
        if "指数" in cell or "名称" in cell:
            positions.setdefault("name", index)
        if "代码" in cell:
            positions["code"] = index
        if "温度" in cell:
            positions["temperature"] = index
        if "内在" in cell and "收益" in cell:
            positions["intrinsic_return"] = index
        if "股息" in cell or "股息率" in cell:
            positions["dividend_yield"] = index
    return positions


def _normalize_html_text(html_text: str) -> str:
    """把 HTML 归一化为适合正则解析的文本。

    Args:
        html_text: 原始 HTML。

    Returns:
        归一化文本。

    Raises:
        无显式抛出。
    """

    without_scripts = _SCRIPT_STYLE_PATTERN.sub(" ", html_text)
    text = _TAG_PATTERN.sub(" ", without_scripts)
    return _normalize_plain_text(text)


def _normalize_plain_text(text: str) -> str:
    """归一化普通文本。

    Args:
        text: 原始文本。

    Returns:
        去标签、解实体、压缩空白后的文本。

    Raises:
        无显式抛出。
    """

    unescaped = html.unescape(_TAG_PATTERN.sub(" ", text))
    return re.sub(r"\s+", " ", unescaped).strip()


def _extract_as_of_text(text: str) -> str | None:
    """提取更新时间文本。

    Args:
        text: 归一化页面文本。

    Returns:
        更新时间文本。

    Raises:
        无显式抛出。
    """

    for label in ("更新时间", "更新日期", "数据日期", "日期"):
        pattern = re.compile(rf"{label}\s*[:：]?\s*({_DATE_PATTERN.pattern})")
        match = pattern.search(text)
        if match:
            return match.group(0)
    date_match = _DATE_PATTERN.search(text)
    return date_match.group(0) if date_match else None


def _extract_date_text(text: str | None) -> str | None:
    """从更新时间文本中提取日期。

    Args:
        text: 更新时间文本。

    Returns:
        日期文本。

    Raises:
        无显式抛出。
    """

    if not text:
        return None
    match = _DATE_PATTERN.search(text)
    return match.group(0) if match else None


def _decimal_after_labels(text: str, labels: tuple[str, ...]) -> Decimal | None:
    """提取标签后的第一个数值。

    Args:
        text: 归一化文本。
        labels: 候选标签。

    Returns:
        Decimal 数值；无法解析时返回 `None`。

    Raises:
        无显式抛出。
    """

    for label in labels:
        match = re.search(rf"{re.escape(label)}\s*[:：]?\s*([-+]?\d+(?:\.\d+)?)", text)
        if match:
            return _parse_decimal(match.group(1))
    return None


def _degree_after_heading(text: str, labels: tuple[str, ...]) -> Decimal | None:
    """提取标题后近距离披露的温度数值。

    Args:
        text: 归一化文本。
        labels: 候选标题。

    Returns:
        Decimal 温度值；无法解析时返回 `None`。

    Raises:
        无显式抛出。
    """

    for label in labels:
        for match in re.finditer(re.escape(label), text):
            tail = text[match.end() : match.end() + 120]
            degree_match = re.search(r"([-+]?\d+(?:\.\d+)?)\s*(?:°|℃)", tail)
            if degree_match:
                return _parse_decimal(degree_match.group(1))
    return None


def _decimal_from_cell(row: tuple[str, ...], index: int | None) -> Decimal | None:
    """从表格单元格中解析数值。

    Args:
        row: 表格行。
        index: 单元格位置。

    Returns:
        Decimal 数值；无法解析时返回 `None`。

    Raises:
        无显式抛出。
    """

    if index is None or index >= len(row):
        return None
    match = _NUMBER_PATTERN.search(row[index].replace(",", ""))
    if match is None:
        return None
    return _parse_decimal(match.group(0))


def _parse_decimal(value: str) -> Decimal | None:
    """把字符串解析为 Decimal。

    Args:
        value: 数值字符串。

    Returns:
        Decimal 数值；解析失败时返回 `None`。

    Raises:
        无显式抛出。
    """

    try:
        return Decimal(value)
    except InvalidOperation:
        return None


def _cell_at(row: tuple[str, ...], index: int) -> str | None:
    """读取表格单元格。

    Args:
        row: 表格行。
        index: 单元格位置。

    Returns:
        单元格文本；越界或空字符串时返回 `None`。

    Raises:
        无显式抛出。
    """

    if index >= len(row):
        return None
    value = row[index].strip()
    return value or None


def _remove_index_code(name: str) -> str:
    """从指数名称单元格中移除代码。

    Args:
        name: 原始指数名称单元格。

    Returns:
        去除指数代码后的名称。

    Raises:
        无显式抛出。
    """

    cleaned = re.sub(r"\b\d{6}(?:\.[A-Z]{2})?\b", "", name).strip()
    return re.sub(r"\s+", " ", cleaned)


def _extract_valuation_band(text: str) -> str | None:
    """提取估值区间标签。

    Args:
        text: 归一化页面文本。

    Returns:
        估值区间标签。

    Raises:
        无显式抛出。
    """

    explicit = _extract_label_text(text, ("估值状态", "估值区间", "估值标签"))
    if explicit:
        return explicit
    match = re.search(r"(低估|偏低|适中|合理|偏高|高估|便宜|昂贵)", text)
    return match.group(1) if match else None


def _extract_market_trend_text(text: str) -> str | None:
    """提取全市场温度趋势文本。

    Args:
        text: 归一化页面文本。

    Returns:
        趋势文本。

    Raises:
        无显式抛出。
    """

    explicit = _extract_label_text(text, ("趋势", "温度趋势", "最近变化"))
    if explicit:
        return explicit
    match = re.search(r"\d+(?:\.\d+)?\s*°\s*(?:低估|偏低|适中|合理|偏高|高估|便宜|昂贵)?\s*(温度(?:不变|上升|下降))", text)
    return match.group(1) if match else None


def _extract_label_text(text: str, labels: tuple[str, ...]) -> str | None:
    """提取短标签后的文本。

    Args:
        text: 归一化页面文本。
        labels: 候选标签。

    Returns:
        标签后的短文本。

    Raises:
        无显式抛出。
    """

    for label in labels:
        match = re.search(rf"{re.escape(label)}\s*[:：]?\s*([^\s，。；;|]+)", text)
        if match:
            return match.group(1)
    return None


def _snapshot_to_cache_payload(snapshot: ThermometerSnapshot) -> dict[str, object]:
    """把快照转换为 JSON 缓存 payload。

    Args:
        snapshot: 温度计快照。

    Returns:
        JSON 兼容 payload。

    Raises:
        无显式抛出。
    """

    payload = _json_safe(asdict(snapshot))
    assert isinstance(payload, dict)
    payload["cache_updated_at"] = snapshot.fetched_at or _utc_timestamp()
    return payload


def _snapshot_from_cache(payload: dict[str, object], *, stale: bool) -> ThermometerSnapshot:
    """从缓存 payload 还原快照。

    Args:
        payload: 缓存 JSON payload。
        stale: 是否标记为 stale cache。

    Returns:
        温度计快照。

    Raises:
        无显式抛出。
    """

    market_payload = payload.get("market")
    macro_payload = payload.get("macro")
    indexes_payload = payload.get("indexes")
    indexes = indexes_payload if isinstance(indexes_payload, list) else []
    return ThermometerSnapshot(
        as_of_text=_optional_str(payload.get("as_of_text")),
        as_of_date=_optional_str(payload.get("as_of_date")),
        market=_market_from_payload(market_payload),
        indexes=tuple(_index_from_payload(index) for index in indexes if isinstance(index, dict)),
        macro=_macro_from_payload(macro_payload),
        source="thermometer_cache",
        cached=True,
        stale=stale,
        unavailable=bool(payload.get("unavailable", False)),
        unavailable_reason=_optional_str(payload.get("unavailable_reason")),
        fetched_at=_optional_str(payload.get("fetched_at")),
    )


def _market_from_payload(payload: object) -> MarketTemperature | None:
    """从缓存 payload 还原全市场温度。

    Args:
        payload: 缓存字段。

    Returns:
        全市场温度或 `None`。

    Raises:
        无显式抛出。
    """

    if not isinstance(payload, dict):
        return None
    return MarketTemperature(
        value=_optional_decimal(payload.get("value")),
        valuation_band=_optional_str(payload.get("valuation_band")),
        trend_text=_optional_str(payload.get("trend_text")),
    )


def _index_from_payload(payload: dict[str, object]) -> IndexTemperature:
    """从缓存 payload 还原指数温度。

    Args:
        payload: 指数缓存字段。

    Returns:
        指数温度。

    Raises:
        无显式抛出。
    """

    return IndexTemperature(
        name=str(payload.get("name") or ""),
        code=str(payload.get("code") or ""),
        temperature=_optional_decimal(payload.get("temperature")),
        intrinsic_return=_optional_decimal(payload.get("intrinsic_return")),
        dividend_yield=_optional_decimal(payload.get("dividend_yield")),
    )


def _macro_from_payload(payload: object) -> MacroTemperature | None:
    """从缓存 payload 还原宏观温度。

    Args:
        payload: 宏观缓存字段。

    Returns:
        宏观温度或 `None`。

    Raises:
        无显式抛出。
    """

    if not isinstance(payload, dict):
        return None
    return MacroTemperature(
        bond_temperature=_optional_decimal(payload.get("bond_temperature")),
        ten_year_treasury_yield=_optional_decimal(payload.get("ten_year_treasury_yield")),
    )


def _json_safe(value: object) -> object:
    """把 dataclass payload 转换为 JSON 兼容值。

    Args:
        value: 原始值。

    Returns:
        JSON 兼容值。

    Raises:
        无显式抛出。
    """

    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, tuple):
        return [_json_safe(item) for item in value]
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    return value


def _cache_age(payload: dict[str, object]) -> timedelta:
    """计算缓存年龄。

    Args:
        payload: 缓存 payload。

    Returns:
        缓存年龄；时间戳非法时返回超长年龄。

    Raises:
        无显式抛出。
    """

    updated_at = _optional_str(payload.get("cache_updated_at")) or _optional_str(payload.get("fetched_at"))
    if not updated_at:
        return THERMOMETER_STALE_TTL + timedelta(seconds=1)
    try:
        parsed = datetime.fromisoformat(updated_at)
    except ValueError:
        return THERMOMETER_STALE_TTL + timedelta(seconds=1)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) - parsed.astimezone(timezone.utc)


def _optional_str(value: object) -> str | None:
    """把可选字段转换为字符串。

    Args:
        value: 原始字段。

    Returns:
        字符串或 `None`。

    Raises:
        无显式抛出。
    """

    return value if isinstance(value, str) else None


def _optional_decimal(value: object) -> Decimal | None:
    """把可选字段转换为 Decimal。

    Args:
        value: 原始字段。

    Returns:
        Decimal 或 `None`。

    Raises:
        无显式抛出。
    """

    if value is None:
        return None
    return _parse_decimal(str(value))


def _unavailable_snapshot(reason: str, *, fetched_at: str | None = None) -> ThermometerSnapshot:
    """构造不可用温度计快照。

    Args:
        reason: 不可用原因。
        fetched_at: 抓取时间。

    Returns:
        不可用快照。

    Raises:
        无显式抛出。
    """

    return ThermometerSnapshot(
        as_of_text=None,
        as_of_date=None,
        market=None,
        indexes=(),
        macro=None,
        source="youzhiyouxing",
        cached=False,
        stale=False,
        unavailable=True,
        unavailable_reason=reason,
        fetched_at=fetched_at or _utc_timestamp(),
    )


def _utc_timestamp() -> str:
    """生成 UTC 时间戳。

    Args:
        无。

    Returns:
        ISO 8601 UTC 时间戳。

    Raises:
        无显式抛出。
    """

    return datetime.now(timezone.utc).isoformat()
