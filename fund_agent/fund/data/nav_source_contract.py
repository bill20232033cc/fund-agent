"""NAV source adapter 内部契约。

本模块定义 Fund data 层 repository 依赖的 source adapter Protocol 和 raw DTO。
它只服务模板第 2 章「R=A+B-C」与第 6 章「核心风险」后续路径型 NAV 证据
进入 typed contract 前的内部边界，不作为 `fund_agent.fund.data` 包级公共 API
导出。
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Protocol

from fund_agent.fund.data.nav_models import AdjustmentBasis, NavType


@dataclass(frozen=True, slots=True)
class _RawNavSourceResult:
    """NAV source adapter 原始结果。

    Args:
        fund_code: source adapter 解析后的基金代码。
        records: 原始 NAV rows；字段名保留 source 原始语义。
        source: 本次返回的直接来源名称。
        origin_source: 缓存命中或包装来源背后的原始来源名称。
        source_id: 来源内部 ID；无法证明时为空。
        source_url: 来源详情或列表 URL；无法证明时为空。
        source_query_params: 来源查询参数，必须显式列出，不得放入 extra_payload。
        source_nav_type: source 声称的 NAV 数学形态。
        source_adjustment_basis: source 声称并由 adapter 证明的调整基础。
        cached: 是否命中缓存。
        retrieved_at: 实际抓取时间；缓存命中且未重新抓取时为空。
        cache_updated_at: 缓存更新时间；非缓存命中时为空。

    Returns:
        dataclass 实例。

    Raises:
        无显式抛出。
    """

    fund_code: str
    records: list[dict[str, object]]
    source: str
    origin_source: str
    source_id: str | None
    source_url: str | None
    source_query_params: tuple[tuple[str, str], ...]
    source_nav_type: NavType
    source_adjustment_basis: AdjustmentBasis
    cached: bool
    retrieved_at: str | None
    cache_updated_at: str | None

    def __post_init__(self) -> None:
        """规范化来源查询参数为不可变 tuple。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        object.__setattr__(
            self,
            "source_query_params",
            tuple((str(key), str(value)) for key, value in self.source_query_params),
        )


class _NavSourceAdapter(Protocol):
    """NAV source adapter Protocol。

    Repository 只依赖该显式签名传递基金代码、份额、日期窗口和刷新策略；禁止
    `extra_payload`、`**kwargs` 或自由 dict 透传业务参数。
    """

    async def load_raw_nav_source(
        self,
        fund_code: str,
        *,
        share_class: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        force_refresh: bool = False,
    ) -> _RawNavSourceResult:
        """读取 source 原始 NAV 结果。

        Args:
            fund_code: 请求基金代码。
            share_class: 请求份额类别；source 不支持时可显式忽略。
            start_date: 请求日期窗口起点；source 不支持时可显式忽略。
            end_date: 请求日期窗口终点；source 不支持时可显式忽略。
            force_refresh: 是否强制刷新来源缓存。

        Returns:
            source 原始 NAV DTO。

        Raises:
            Exception: 具体 source adapter 可按 typed failure taxonomy 抛出异常。
        """

        ...


__all__ = ["_NavSourceAdapter", "_RawNavSourceResult"]
