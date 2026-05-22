"""自建温度计结构化类型。

本模块属于 Fund Capability data 层，只定义 P19 自建温度计的数据契约。
它不访问外部数据源，不执行温度计算，也不参与 UI 输出。
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Literal

THERMOMETER_DISCLAIMER = "本温度计基于有知有行公开方法论独立计算，非有知有行官方数据。"

ValuationStateCandidate = Literal["low", "fair", "high", "unavailable"]


@dataclass(frozen=True, slots=True)
class PePbPoint:
    """单日 PE/PB 估值点。

    Attributes:
        date: 数据日期，使用 ISO `YYYY-MM-DD` 字符串。
        pe: PE 指标值。
        pb: PB 指标值。
    """

    date: str
    pe: Decimal
    pb: Decimal


@dataclass(frozen=True, slots=True)
class PePbHistory:
    """指数或市场 PE/PB 历史序列。

    Attributes:
        index_code: 指数代码，例如 `000300`。
        index_name: 指数名称，例如 `沪深300`。
        points: 按日期升序排列的 PE/PB 历史点。
        source: 数据来源标识。
        fetched_at: 抓取或缓存写入的 UTC 时间。
    """

    index_code: str
    index_name: str
    points: tuple[PePbPoint, ...]
    source: str
    fetched_at: str | None = None


@dataclass(frozen=True, slots=True)
class ThermometerReading:
    """自建温度计读数。

    Attributes:
        index_code: 指数代码。
        index_name: 指数名称。
        temperature: 综合温度，0 到 100；不可用时为空。
        pe_percentile: PE 历史分位，0 到 100；不可用时为空。
        pb_percentile: PB 历史分位，0 到 100；不可用时为空。
        valuation_state_candidate: 估值状态候选。
        data_date: 本次读数使用的数据日期。
        lookback_start: 历史窗口起始日期。
        lookback_end: 历史窗口结束日期。
        source: 数据来源。
        cached: 是否来自缓存。
        stale: 是否为 stale cache。
        unavailable: 是否不可用。
        unavailable_reason: 不可用原因。
        fetched_at: 抓取或缓存写入的 UTC 时间。
        disclaimer: 非官方独立计算免责说明。
    """

    index_code: str
    index_name: str
    temperature: Decimal | None
    pe_percentile: Decimal | None
    pb_percentile: Decimal | None
    valuation_state_candidate: ValuationStateCandidate
    data_date: str | None
    lookback_start: str | None
    lookback_end: str | None
    source: str
    cached: bool
    stale: bool
    unavailable: bool
    unavailable_reason: str | None
    fetched_at: str | None
    disclaimer: str = THERMOMETER_DISCLAIMER


@dataclass(frozen=True, slots=True)
class ThermometerBatchResult:
    """自建温度计批量读数。

    Attributes:
        readings: 按规范化请求顺序返回的指数温度计读数。
        requested_index_codes: preserve-order de-duplication 后的指数代码序列。
        generated_at: 批量结果生成时间。
        source: 批量温度计来源标识。
        unavailable: 是否全部指数不可用。
        partial_unavailable: 是否存在部分指数不可用。
        unavailable_count: 不可用指数数量。
        disclaimer: 非官方独立计算免责说明。
    """

    readings: tuple[ThermometerReading, ...]
    requested_index_codes: tuple[str, ...]
    generated_at: str | None
    source: str = "self_owned_index_thermometer_batch"
    unavailable: bool = False
    partial_unavailable: bool = False
    unavailable_count: int = 0
    disclaimer: str = THERMOMETER_DISCLAIMER


@dataclass(frozen=True, slots=True)
class ThermometerUnavailable:
    """自建温度计不可用结果。

    Attributes:
        index_code: 指数代码。
        index_name: 指数名称。
        reason: 不可用原因。
        source: 数据来源。
        cached: 是否来自缓存。
        stale: 是否为 stale cache。
        fetched_at: 抓取或缓存写入的 UTC 时间。
    """

    index_code: str
    index_name: str
    reason: str
    source: str = "self_owned_thermometer"
    cached: bool = False
    stale: bool = False
    fetched_at: str | None = None

    def to_reading(self) -> ThermometerReading:
        """转换为统一的温度计读数。

        Args:
            无。

        Returns:
            不可用状态的温度计读数。

        Raises:
            无显式抛出。
        """

        return ThermometerReading(
            index_code=self.index_code,
            index_name=self.index_name,
            temperature=None,
            pe_percentile=None,
            pb_percentile=None,
            valuation_state_candidate="unavailable",
            data_date=None,
            lookback_start=None,
            lookback_end=None,
            source=self.source,
            cached=self.cached,
            stale=self.stale,
            unavailable=True,
            unavailable_reason=self.reason,
            fetched_at=self.fetched_at,
        )
