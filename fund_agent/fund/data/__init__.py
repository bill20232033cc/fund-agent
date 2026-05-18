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

__all__ = [
    "FundNavDataAdapter",
    "FundThermometerAdapter",
    "IndexTemperature",
    "MacroTemperature",
    "MarketTemperature",
    "NavDataResult",
    "ThermometerSnapshot",
    "parse_thermometer_pages",
]
