"""自建温度计 akshare 数据源。

本模块属于 Fund Capability data 层，负责把外部指数估值数据规整为
`PePbHistory`。它不计算温度，不处理 CLI 输出，也不依赖 Service。
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
import re
from typing import Protocol

from fund_agent.fund.data.thermometer_types import PePbHistory, PePbPoint

SUPPORTED_INDEX_SYMBOLS: dict[str, str] = {"000300": "沪深300"}
INDEX_NAMES: dict[str, str] = {"000300": "沪深300"}
PE_COLUMN = "滚动市盈率中位数"
PB_COLUMN = "市净率中位数"
DATE_COLUMN = "日期"
SOURCE_NAME = "akshare_legulegu_index_pe_pb"
ISO_DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


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
            index_code: 指数代码；P19-S1 仅支持 `000300`。

        Returns:
            规整后的 PE/PB 历史序列。

        Raises:
            ThermometerSourceError: 指数不支持、外部调用失败或 schema 漂移时抛出。
        """

        symbol = SUPPORTED_INDEX_SYMBOLS.get(index_code)
        if symbol is None:
            raise ThermometerSourceError(f"暂不支持指数：{index_code}")

        try:
            pe_frame, pb_frame = await asyncio.gather(
                asyncio.to_thread(self._load_pe_frame, symbol),
                asyncio.to_thread(self._load_pb_frame, symbol),
            )
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
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ThermometerSourceError(f"{field_name} 不是有效数值：{value}") from exc
