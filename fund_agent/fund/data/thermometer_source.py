"""自建温度计 akshare 数据源。

本模块属于 Agent 层基金能力 data 层，负责把外部指数估值数据规整为
`PePbHistory`。它不计算温度，不处理 CLI 输出，也不依赖 Service。
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
import re
from typing import Literal, Protocol

from fund_agent.fund.data.thermometer_types import PePbHistory, PePbPoint

SUPPORTED_INDEX_SYMBOLS: dict[str, str] = {"000300": "沪深300", "000905": "中证500"}
INDEX_NAMES: dict[str, str] = {"000300": "沪深300", "000905": "中证500"}
ALL_A_MARKET_CODE = "wind_all_a"
ALL_A_MARKET_NAME = "万得全 A / 全 A 市场"
ALL_A_DATE_COLUMN = "date"
ALL_A_PE_COLUMN = "middlePETTM"
ALL_A_PB_COLUMN = "middlePB"
ALL_A_SOURCE_NAME = "akshare_legulegu_all_a_pe_pb"
PE_COLUMN = "滚动市盈率中位数"
PB_COLUMN = "市净率中位数"
DATE_COLUMN = "日期"
SOURCE_NAME = "akshare_legulegu_index_pe_pb"
ALL_A_FETCH_MAX_ATTEMPTS = 2
ISO_DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ThermometerCodeKind = Literal["index", "market", "unsupported"]


def is_supported_index_code(index_code: str) -> bool:
    """判断自建指数温度计是否支持指定指数代码。

    Args:
        index_code: 已完成格式规范化的 6 位指数代码。

    Returns:
        支持返回 True，否则返回 False。

    Raises:
        无显式抛出。
    """

    return classify_thermometer_code(index_code) == "index"


def classify_thermometer_code(code: str) -> ThermometerCodeKind:
    """分类温度计代码。

    Args:
        code: 温度计代码；支持六位指数代码和显式全 A 市场代码。

    Returns:
        `index` 表示已支持的六位指数，`market` 表示全 A 市场，
        `unsupported` 表示当前基金领域能力未支持。

    Raises:
        无显式抛出。
    """

    if code in SUPPORTED_INDEX_SYMBOLS:
        return "index"
    if code == ALL_A_MARKET_CODE:
        return "market"
    return "unsupported"


def is_supported_thermometer_code(code: str) -> bool:
    """判断温度计代码是否受当前基金领域能力支持。

    Args:
        code: 温度计代码。

    Returns:
        支持的指数或全 A 市场返回 True，否则返回 False。

    Raises:
        无显式抛出。
    """

    return classify_thermometer_code(code) != "unsupported"


def thermometer_display_name(code: str) -> str:
    """返回温度计代码的人类可读名称。

    Args:
        code: 温度计代码。

    Returns:
        支持代码返回对应展示名，未知代码返回原始代码。

    Raises:
        无显式抛出。
    """

    code_kind = classify_thermometer_code(code)
    if code_kind == "market":
        return ALL_A_MARKET_NAME
    if code_kind == "index":
        return INDEX_NAMES[code]
    return code


class ThermometerDataSource(Protocol):
    """温度计 PE/PB 历史数据源协议。"""

    async def load_index_history(self, index_code: str) -> PePbHistory:
        """读取指定指数 PE/PB 历史。

        Args:
            index_code: 指数代码。

        Returns:
            PE/PB 历史序列。

        Raises:
            ThermometerSourceError: 数据不可用或结构不符合契约时抛出。
        """


class ThermometerSourceError(RuntimeError):
    """温度计数据源不可用或结构漂移。"""


PeFetcher = Callable[[str], object]
PbFetcher = Callable[[str], object]
AllAFetcher = Callable[[], object]


@dataclass(frozen=True, slots=True)
class AkshareThermometerSource:
    """akshare 复合温度计数据源。

    Attributes:
        index_source: 六位指数数据源。
        all_a_source: 全 A 市场数据源。
    """

    index_source: ThermometerDataSource | None = None
    all_a_source: ThermometerDataSource | None = None

    async def load_index_history(self, index_code: str) -> PePbHistory:
        """按代码类型分派读取 PE/PB 历史。

        Args:
            index_code: 指数或市场代码。

        Returns:
            规整后的 PE/PB 历史序列。

        Raises:
            ThermometerSourceError: 代码不支持或底层数据源失败时抛出。
        """

        code_kind = classify_thermometer_code(index_code)
        if code_kind == "index":
            source = self.index_source or AkshareIndexThermometerSource()
            return await source.load_index_history(index_code)
        if code_kind == "market":
            source = self.all_a_source or AkshareAllAMarketThermometerSource()
            return await source.load_index_history(index_code)
        raise ThermometerSourceError(f"暂不支持温度计代码：{index_code}")


@dataclass(frozen=True, slots=True)
class AkshareIndexThermometerSource:
    """akshare 指数温度计数据源。

    Attributes:
        pe_fetcher: PE 表抓取函数；测试可注入 fake。
        pb_fetcher: PB 表抓取函数；测试可注入 fake。
    """

    pe_fetcher: PeFetcher | None = None
    pb_fetcher: PbFetcher | None = None

    async def load_index_history(self, index_code: str) -> PePbHistory:
        """读取指数 PE/PB 历史。

        Args:
            index_code: 指数代码；P19-S2 支持 `000300` 和 `000905`。

        Returns:
            规整后的 PE/PB 历史序列。

        Raises:
            ThermometerSourceError: 指数不支持、外部调用失败或 schema 漂移时抛出。
        """

        symbol = SUPPORTED_INDEX_SYMBOLS.get(index_code)
        if symbol is None:
            raise ThermometerSourceError(f"暂不支持指数：{index_code}")

        try:
            pe_frame = await asyncio.to_thread(self._load_pe_frame, symbol)
            pb_frame = await asyncio.to_thread(self._load_pb_frame, symbol)
        except Exception as exc:
            raise ThermometerSourceError(f"指数估值数据获取失败：{exc}") from exc

        points = _merge_pe_pb_rows(pe_frame, pb_frame)
        if not points:
            raise ThermometerSourceError("指数 PE/PB 历史合并后为空")

        return PePbHistory(
            index_code=index_code,
            index_name=INDEX_NAMES[index_code],
            points=points,
            source=SOURCE_NAME,
            fetched_at=None,
        )

    def _load_pe_frame(self, symbol: str) -> object:
        """同步读取 PE 表。

        Args:
            symbol: akshare 指数名称。

        Returns:
            akshare DataFrame 或测试 fake 对象。

        Raises:
            ImportError: akshare 不可用时抛出。
            Exception: 外部接口异常向上抛出。
        """

        if self.pe_fetcher is not None:
            return self.pe_fetcher(symbol)

        import akshare as ak

        return ak.stock_index_pe_lg(symbol=symbol)

    def _load_pb_frame(self, symbol: str) -> object:
        """同步读取 PB 表。

        Args:
            symbol: akshare 指数名称。

        Returns:
            akshare DataFrame 或测试 fake 对象。

        Raises:
            ImportError: akshare 不可用时抛出。
            Exception: 外部接口异常向上抛出。
        """

        if self.pb_fetcher is not None:
            return self.pb_fetcher(symbol)

        import akshare as ak

        return ak.stock_index_pb_lg(symbol=symbol)


@dataclass(frozen=True, slots=True)
class AkshareAllAMarketThermometerSource:
    """akshare 全 A 市场温度计数据源。

    Attributes:
        pe_fetcher: 全 A PE 表抓取函数；测试可注入 fake。
        pb_fetcher: 全 A PB 表抓取函数；测试可注入 fake。
    """

    pe_fetcher: AllAFetcher | None = None
    pb_fetcher: AllAFetcher | None = None

    async def load_index_history(self, index_code: str) -> PePbHistory:
        """读取全 A 市场 PE/PB 历史。

        Args:
            index_code: 市场代码；S5-1 仅支持 `wind_all_a`。

        Returns:
            规整后的 PE/PB 历史序列。

        Raises:
            ThermometerSourceError: 代码不支持、外部调用失败或 schema 漂移时抛出。
        """

        if classify_thermometer_code(index_code) != "market":
            raise ThermometerSourceError(f"暂不支持全 A 市场代码：{index_code}")

        pe_frame = await asyncio.to_thread(self._load_pe_frame)
        pb_frame = await asyncio.to_thread(self._load_pb_frame)
        points = _merge_all_a_pe_pb_rows(pe_frame, pb_frame)
        if not points:
            raise ThermometerSourceError("全 A PE/PB 历史合并后为空")

        return PePbHistory(
            index_code=ALL_A_MARKET_CODE,
            index_name=ALL_A_MARKET_NAME,
            points=points,
            source=ALL_A_SOURCE_NAME,
            fetched_at=None,
        )

    def _load_pe_frame(self) -> object:
        """同步读取全 A PE 表。

        Args:
            无。

        Returns:
            akshare DataFrame 或测试 fake 对象。

        Raises:
            ThermometerSourceError: 重试耗尽后抛出。
        """

        return _fetch_all_a_with_retry(self._fetch_pe_frame_once, label="PE")

    def _load_pb_frame(self) -> object:
        """同步读取全 A PB 表。

        Args:
            无。

        Returns:
            akshare DataFrame 或测试 fake 对象。

        Raises:
            ThermometerSourceError: 重试耗尽后抛出。
        """

        return _fetch_all_a_with_retry(self._fetch_pb_frame_once, label="PB")

    def _fetch_pe_frame_once(self) -> object:
        """执行一次全 A PE 表抓取。

        Args:
            无。

        Returns:
            akshare DataFrame 或测试 fake 对象。

        Raises:
            ImportError: akshare 不可用时抛出。
            Exception: 外部接口异常向上抛出。
        """

        if self.pe_fetcher is not None:
            return self.pe_fetcher()

        import akshare as ak

        return ak.stock_a_ttm_lyr()

    def _fetch_pb_frame_once(self) -> object:
        """执行一次全 A PB 表抓取。

        Args:
            无。

        Returns:
            akshare DataFrame 或测试 fake 对象。

        Raises:
            ImportError: akshare 不可用时抛出。
            Exception: 外部接口异常向上抛出。
        """

        if self.pb_fetcher is not None:
            return self.pb_fetcher()

        import akshare as ak

        return ak.stock_a_all_pb()


def _merge_pe_pb_rows(pe_frame: object, pb_frame: object) -> tuple[PePbPoint, ...]:
    """合并 PE/PB 表。

    Args:
        pe_frame: 包含日期和 PE 列的表。
        pb_frame: 包含日期和 PB 列的表。

    Returns:
        按日期升序排列的 PE/PB 点。

    Raises:
        ThermometerSourceError: 表结构缺列或无法读取时抛出。
    """

    pe_rows = _records_by_date(pe_frame, value_column=PE_COLUMN)
    pb_rows = _records_by_date(pb_frame, value_column=PB_COLUMN)
    common_dates = sorted(set(pe_rows) & set(pb_rows))
    return tuple(PePbPoint(date=date, pe=pe_rows[date], pb=pb_rows[date]) for date in common_dates)


def _merge_all_a_pe_pb_rows(pe_frame: object, pb_frame: object) -> tuple[PePbPoint, ...]:
    """合并全 A PE/PB 表。

    Args:
        pe_frame: 包含 `date` 和 `middlePETTM` 的表。
        pb_frame: 包含 `date` 和 `middlePB` 的表。

    Returns:
        按日期升序排列的 PE/PB 点。

    Raises:
        ThermometerSourceError: 表结构缺列或有效共同日期为空时抛出。
    """

    pe_rows = _strict_positive_records_by_date(
        pe_frame,
        date_column=ALL_A_DATE_COLUMN,
        value_column=ALL_A_PE_COLUMN,
    )
    pb_rows = _strict_positive_records_by_date(
        pb_frame,
        date_column=ALL_A_DATE_COLUMN,
        value_column=ALL_A_PB_COLUMN,
    )
    common_dates = sorted(set(pe_rows) & set(pb_rows))
    if not common_dates:
        raise ThermometerSourceError("全 A PE/PB 历史没有有效共同日期")
    return tuple(PePbPoint(date=date, pe=pe_rows[date], pb=pb_rows[date]) for date in common_dates)


def _fetch_all_a_with_retry(fetcher: AllAFetcher, *, label: str) -> object:
    """带有界重试地抓取全 A Legulegu 数据。

    Args:
        fetcher: 单次抓取函数。
        label: 数据类型标签，用于错误信息。

    Returns:
        抓取到的 DataFrame-like 对象。

    Raises:
        ThermometerSourceError: 连续失败达到上限时抛出。
    """

    last_error: Exception | None = None
    for _attempt in range(ALL_A_FETCH_MAX_ATTEMPTS):
        try:
            return fetcher()
        except Exception as exc:  # noqa: BLE001 - 外部数据源异常类型不稳定，需统一包裹。
            last_error = exc
    raise ThermometerSourceError(f"全 A 估值数据获取失败：{label}：{last_error}") from last_error


def _records_by_date(frame: object, *, value_column: str) -> dict[str, Decimal]:
    """把 DataFrame-like 表转换为日期到估值值的映射。

    Args:
        frame: akshare DataFrame 或具备 `to_dict(orient=\"records\")` 的对象。
        value_column: 估值列名。

    Returns:
        日期到估值值的映射。

    Raises:
        ThermometerSourceError: schema 缺失或值不可解析时抛出。
    """

    if not hasattr(frame, "to_dict"):
        raise ThermometerSourceError("指数估值数据不是 DataFrame-like 对象")

    try:
        records = frame.to_dict(orient="records")
    except TypeError as exc:
        raise ThermometerSourceError("指数估值数据无法转换为 records") from exc

    values: dict[str, Decimal] = {}
    for record in records:
        if not isinstance(record, dict):
            continue
        if DATE_COLUMN not in record or value_column not in record:
            raise ThermometerSourceError(f"指数估值数据缺少字段：{DATE_COLUMN} / {value_column}")
        date_text = _normalize_date(record[DATE_COLUMN])
        value = _to_decimal(record[value_column], field_name=value_column)
        if value > 0:
            values[date_text] = value
    return values


def _strict_positive_records_by_date(
    frame: object,
    *,
    date_column: str,
    value_column: str,
) -> dict[str, Decimal]:
    """把全 A DataFrame-like 表转换为严格日期到正估值值的映射。

    同一来源响应内如果同一日期出现多条正数记录，按输入顺序保留最后
    一条。该规则只在同源表内部做确定性折叠，用于处理来源返回的重复
    修正行；不跨来源推断、不做插补，也不放宽 schema 和数值校验。

    Args:
        frame: akshare DataFrame 或具备 `to_dict(orient=\"records\")` 的对象。
        date_column: 日期列名，必须是全 A source contract 的 `date`。
        value_column: 估值列名。

    Returns:
        日期到正估值值的映射。

    Raises:
        ThermometerSourceError: schema 缺失或值不可解析时抛出。
    """

    if not hasattr(frame, "to_dict"):
        raise ThermometerSourceError("全 A 估值数据不是 DataFrame-like 对象")

    try:
        records = frame.to_dict(orient="records")
    except TypeError as exc:
        raise ThermometerSourceError("全 A 估值数据无法转换为 records") from exc

    values: dict[str, Decimal] = {}
    saw_structured_row = False
    for record in records:
        if not isinstance(record, dict):
            continue
        if date_column not in record or value_column not in record:
            raise ThermometerSourceError(f"全 A 估值数据缺少字段：{date_column} / {value_column}")

        saw_structured_row = True
        date_text = _normalize_date(record[date_column])
        value = _to_optional_positive_decimal(record[value_column], field_name=value_column)
        if value is None:
            continue
        # 同源响应内重复日期视为来源重复修正行，按响应输入顺序保留最后一条正数值。
        values[date_text] = value

    if not saw_structured_row or not values:
        raise ThermometerSourceError(f"全 A 估值数据没有有效正数记录：{value_column}")
    return values


def _normalize_date(value: object) -> str:
    """标准化日期值。

    Args:
        value: 原始日期对象或字符串。

    Returns:
        ISO 日期字符串。

    Raises:
        ThermometerSourceError: 日期为空时抛出。
    """

    if value is None:
        raise ThermometerSourceError("指数估值数据日期为空")
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    text = str(value)
    if not text:
        raise ThermometerSourceError("指数估值数据日期为空")
    if not ISO_DATE_PATTERN.fullmatch(text):
        raise ThermometerSourceError(f"指数估值数据日期不是 ISO 格式：{value}")
    try:
        datetime.strptime(text, "%Y-%m-%d")
    except ValueError as exc:
        raise ThermometerSourceError(f"指数估值数据日期非法：{value}") from exc
    return text


def _to_decimal(value: object, *, field_name: str) -> Decimal:
    """转换估值字段为 Decimal。

    Args:
        value: 原始字段值。
        field_name: 字段名，用于错误信息。

    Returns:
        Decimal 值。

    Raises:
        ThermometerSourceError: 值为空或不可解析时抛出。
    """

    if value is None:
        raise ThermometerSourceError(f"{field_name} 为空")
    if isinstance(value, bool):
        raise ThermometerSourceError(f"{field_name} 不能为布尔值")
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ThermometerSourceError(f"{field_name} 不是有效数值：{value}") from exc


def _to_optional_positive_decimal(value: object, *, field_name: str) -> Decimal | None:
    """转换全 A 估值字段为正 Decimal。

    Args:
        value: 原始字段值。
        field_name: 字段名，用于错误信息。

    Returns:
        正 Decimal；空值或非正数返回 None，供全 A 缺失行丢弃。

    Raises:
        ThermometerSourceError: bool、非数值、NaN 或 Infinity 时抛出。
    """

    if value is None:
        return None
    if isinstance(value, bool):
        raise ThermometerSourceError(f"{field_name} 不能为布尔值")
    try:
        parsed_value = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ThermometerSourceError(f"{field_name} 不是有效数值：{value}") from exc
    if not parsed_value.is_finite():
        raise ThermometerSourceError(f"{field_name} 不是有限数值：{value}")
    if parsed_value <= 0:
        return None
    return parsed_value
