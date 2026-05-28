"""基金数据适配器公共入口。

本模块是 Agent 层基金能力 data 层对外暴露的稳定入口。上层 Service 可以
通过这里获取数据适配器、结构化类型和默认工厂，不直接穿透具体实现模块。
"""

from pathlib import Path

from fund_agent.fund.data.nav_data import FundNavDataAdapter, NavDataResult
from fund_agent.fund.data.nav_models import (
    AdjustmentBasis,
    DividendAdjustmentStatus,
    FundNavRecord,
    FundNavSeries,
    NavCompletenessStatus,
    NavContractError,
    NavDataContractError,
    NavFailureCategory,
    NavIdentityStatus,
    NavSourceMetadata,
    NavType,
    ShareClassMapping,
)
from fund_agent.fund.data.thermometer import (
    FundThermometerAdapter,
    IndexTemperature,
    MacroTemperature,
    MarketTemperature,
    ThermometerSnapshot,
    parse_thermometer_pages,
)
from fund_agent.fund.data.thermometer_types import (
    PePbHistory,
    PePbPoint,
    ThermometerBatchResult,
    ThermometerReading,
    ThermometerUnavailable,
)
from fund_agent.fund.data.thermometer_cache import ThermometerHistoryCache
from fund_agent.fund.data.thermometer_source import (
    ALL_A_MARKET_CODE,
    AkshareThermometerSource,
    ThermometerSourceError,
    classify_thermometer_code,
    thermometer_display_name,
)


def create_default_thermometer_history_cache(
    cache_dir: Path | None = None,
) -> ThermometerHistoryCache:
    """创建默认自建温度计历史缓存。

    Args:
        cache_dir: 温度计缓存目录；为空时使用基金领域能力默认目录。

    Returns:
        默认温度计历史缓存。

    Raises:
        无显式抛出。
    """

    return ThermometerHistoryCache(root_dir=cache_dir)


def create_default_thermometer_source() -> AkshareThermometerSource:
    """创建默认自建温度计数据源。

    Args:
        无。

    Returns:
        默认 akshare 复合温度计数据源。

    Raises:
        无显式抛出。
    """

    return AkshareThermometerSource()

__all__ = [
    "ALL_A_MARKET_CODE",
    "AdjustmentBasis",
    "DividendAdjustmentStatus",
    "FundNavDataAdapter",
    "FundNavRecord",
    "FundNavSeries",
    "FundThermometerAdapter",
    "IndexTemperature",
    "MacroTemperature",
    "MarketTemperature",
    "NavCompletenessStatus",
    "NavContractError",
    "NavDataResult",
    "NavDataContractError",
    "NavFailureCategory",
    "NavIdentityStatus",
    "NavSourceMetadata",
    "NavType",
    "PePbHistory",
    "PePbPoint",
    "ShareClassMapping",
    "ThermometerBatchResult",
    "ThermometerReading",
    "ThermometerSnapshot",
    "ThermometerSourceError",
    "ThermometerUnavailable",
    "classify_thermometer_code",
    "create_default_thermometer_history_cache",
    "create_default_thermometer_source",
    "parse_thermometer_pages",
    "thermometer_display_name",
]
