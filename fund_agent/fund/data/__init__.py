"""基金数据适配器。"""

from fund_agent.fund.data.nav_data import FundNavDataAdapter, NavDataResult
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
    ThermometerReading,
    ThermometerUnavailable,
)

__all__ = [
    "FundNavDataAdapter",
    "FundThermometerAdapter",
    "IndexTemperature",
    "MacroTemperature",
    "MarketTemperature",
    "NavDataResult",
    "PePbHistory",
    "PePbPoint",
    "ThermometerReading",
    "ThermometerSnapshot",
    "ThermometerUnavailable",
    "parse_thermometer_pages",
]
