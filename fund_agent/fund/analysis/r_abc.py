"""R=A+B-C 收益归因计算模块。

本模块属于 Agent 层基金能力，只消费 P1 已形成的结构化数据，不直接读取年报文件。
计算逻辑对应模板第 2 章“R=A+B-C 收益归因”。
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Final, Literal

from fund_agent.fund.analysis._ratios import parse_ratio
from fund_agent.fund.data_extractor import StructuredFundDataBundle
from fund_agent.fund.extractors.models import EvidenceAnchor, ExtractedField

AttributionStatus = Literal["computed", "missing"]

_TURNOVER_COST_RATE: Final[Decimal] = Decimal("0.003")


@dataclass(frozen=True, slots=True)
class RabcInput:
    """R=A+B-C 单期计算输入。

    Attributes:
        period: 归因周期标识，例如 `1y`、`3y`、`5y` 或年报年度。
        nav_growth_rate: 基金净值增长率，小数比例。
        benchmark_return_rate: 业绩比较基准收益率，小数比例。
        equity_position: 股票仓位，小数比例。
        management_fee_rate: 管理费率，小数比例。
        custody_fee_rate: 托管费率，小数比例。
        turnover_rate: 换手率，小数比例。
    """

    period: str
    nav_growth_rate: Decimal
    benchmark_return_rate: Decimal
    equity_position: Decimal
    management_fee_rate: Decimal
    custody_fee_rate: Decimal
    turnover_rate: Decimal


@dataclass(frozen=True, slots=True)
class RabcAttribution:
    """R=A+B-C 单期归因结果。

    Attributes:
        period: 归因周期标识。
        status: 计算状态。
        total_return_r: R，基金净值增长率。
        beta_return_b: B，业绩比较基准收益率乘以股票仓位。
        alpha_return_a: A，R 减 B。
        explicit_cost_c: C，管理费、托管费和换手交易成本之和。
        net_excess_return: 净超额收益，A 减 C。
        turnover_cost: 换手交易成本估算，换手率乘以 0.3%。
        anchors: 参与计算字段的证据锚点。
        note: 缺失或计算口径说明。
    """

    period: str
    status: AttributionStatus
    total_return_r: Decimal | None
    beta_return_b: Decimal | None
    alpha_return_a: Decimal | None
    explicit_cost_c: Decimal | None
    net_excess_return: Decimal | None
    turnover_cost: Decimal | None
    anchors: tuple[EvidenceAnchor, ...]
    note: str | None = None


def calculate_r_abc(input_data: RabcInput) -> RabcAttribution:
    """计算单期 R=A+B-C 收益归因，见模板第 2 章。

    Args:
        input_data: 单期收益归因输入，所有比例均使用小数口径。

    Returns:
        单期收益归因结果。

    Raises:
        ValueError: 当周期为空，或任一比例无法落在合理区间时抛出。
    """

    if not input_data.period.strip():
        raise ValueError("period 不能为空")
    _validate_ratio("nav_growth_rate", input_data.nav_growth_rate, allow_negative=True)
    _validate_ratio("benchmark_return_rate", input_data.benchmark_return_rate, allow_negative=True)
    _validate_ratio("equity_position", input_data.equity_position, allow_negative=False)
    _validate_ratio("management_fee_rate", input_data.management_fee_rate, allow_negative=False)
    _validate_ratio("custody_fee_rate", input_data.custody_fee_rate, allow_negative=False)
    _validate_ratio("turnover_rate", input_data.turnover_rate, allow_negative=False)

    beta_return = input_data.benchmark_return_rate * input_data.equity_position
    alpha_return = input_data.nav_growth_rate - beta_return
    turnover_cost = input_data.turnover_rate * _TURNOVER_COST_RATE
    explicit_cost = input_data.management_fee_rate + input_data.custody_fee_rate + turnover_cost
    net_excess_return = alpha_return - explicit_cost

    return RabcAttribution(
        period=input_data.period.strip(),
        status="computed",
        total_return_r=input_data.nav_growth_rate,
        beta_return_b=beta_return,
        alpha_return_a=alpha_return,
        explicit_cost_c=explicit_cost,
        net_excess_return=net_excess_return,
        turnover_cost=turnover_cost,
        anchors=(),
        note="B=业绩比较基准收益率×股票仓位；C=管理费+托管费+换手率×0.3%。",
    )


def calculate_r_abc_series(input_series: tuple[RabcInput, ...]) -> tuple[RabcAttribution, ...]:
    """批量计算多周期 R=A+B-C 收益归因，见模板第 2 章。

    Args:
        input_series: 多个周期的收益归因输入，典型周期为 `1y`、`3y`、`5y`。

    Returns:
        与输入顺序一致的多周期归因结果。

    Raises:
        ValueError: 当输入为空，或任一单期输入非法时抛出。
    """

    if not input_series:
        raise ValueError("input_series 不能为空")
    return tuple(calculate_r_abc(input_data) for input_data in input_series)


def calculate_r_abc_from_bundle(
    bundle: StructuredFundDataBundle,
    *,
    period: str | None = None,
    equity_position: Decimal | str | float | int | None = None,
) -> RabcAttribution:
    """从 P1 结构化数据包计算 R=A+B-C，见模板第 2 章。

    Args:
        bundle: P1 结构化基金数据包。
        period: 归因周期；未提供时使用年报年份。
        equity_position: 股票仓位。P1 当前尚未稳定抽取股票仓位，因此该参数必须显式提供。

    Returns:
        归因计算结果；关键输入缺失时返回 `missing` 状态。

    Raises:
        ValueError: 当显式股票仓位格式非法时抛出。
    """

    anchors = _merge_anchors(
        bundle.nav_benchmark_performance,
        bundle.fee_schedule,
        bundle.turnover_rate,
    )
    missing_reasons = _missing_input_reasons(bundle, equity_position)
    attribution_period = period or str(bundle.report_year)
    if missing_reasons:
        return RabcAttribution(
            period=attribution_period,
            status="missing",
            total_return_r=None,
            beta_return_b=None,
            alpha_return_a=None,
            explicit_cost_c=None,
            net_excess_return=None,
            turnover_cost=None,
            anchors=anchors,
            note="；".join(missing_reasons),
        )

    assert bundle.nav_benchmark_performance.value is not None
    assert bundle.fee_schedule.value is not None
    assert bundle.turnover_rate.value is not None
    assert equity_position is not None

    input_data = RabcInput(
        period=attribution_period,
        nav_growth_rate=_parse_ratio(
            bundle.nav_benchmark_performance.value["nav_growth_rate"],
            field_name="nav_growth_rate",
        ),
        benchmark_return_rate=_parse_ratio(
            bundle.nav_benchmark_performance.value["benchmark_return_rate"],
            field_name="benchmark_return_rate",
        ),
        equity_position=_parse_ratio(equity_position, field_name="equity_position"),
        management_fee_rate=_parse_ratio(
            bundle.fee_schedule.value["management_fee"],
            field_name="management_fee",
        ),
        custody_fee_rate=_parse_ratio(bundle.fee_schedule.value["custody_fee"], field_name="custody_fee"),
        turnover_rate=_parse_ratio(
            bundle.turnover_rate.value["turnover_rate"],
            field_name="turnover_rate",
        ),
    )
    computed = calculate_r_abc(input_data)
    return RabcAttribution(
        period=computed.period,
        status=computed.status,
        total_return_r=computed.total_return_r,
        beta_return_b=computed.beta_return_b,
        alpha_return_a=computed.alpha_return_a,
        explicit_cost_c=computed.explicit_cost_c,
        net_excess_return=computed.net_excess_return,
        turnover_cost=computed.turnover_cost,
        anchors=anchors,
        note=computed.note,
    )


def _validate_ratio(field_name: str, value: Decimal, *, allow_negative: bool) -> None:
    """校验比例字段是否处在合理区间。

    Args:
        field_name: 字段名。
        value: 待校验比例。
        allow_negative: 是否允许负值。

    Returns:
        无返回值。

    Raises:
        ValueError: 当比例不在合理区间时抛出。
    """

    if not allow_negative and value < Decimal("0"):
        raise ValueError(f"{field_name} 不能为负数")
    if abs(value) > Decimal("10"):
        raise ValueError(f"{field_name} 超出合理比例区间")


def _parse_ratio(value: object, *, field_name: str) -> Decimal:
    """调用分析模块公共比例解析工具。

    Args:
        value: 原始比例值。
        field_name: 字段名。

    Returns:
        Decimal 小数比例。

    Raises:
        ValueError: 当输入为空或无法解析为比例时抛出。
    """

    return parse_ratio(value, field_name=field_name)


def _merge_anchors(*fields: ExtractedField[dict[str, object]]) -> tuple[EvidenceAnchor, ...]:
    """合并参与计算字段的证据锚点。

    Args:
        fields: 参与计算的抽取字段。

    Returns:
        去重后的证据锚点元组。

    Raises:
        无显式抛出。
    """

    anchors: list[EvidenceAnchor] = []
    seen: set[EvidenceAnchor] = set()
    for field in fields:
        for anchor in field.anchors:
            if anchor in seen:
                continue
            anchors.append(anchor)
            seen.add(anchor)
    return tuple(anchors)


def _missing_input_reasons(
    bundle: StructuredFundDataBundle,
    equity_position: Decimal | str | float | int | None,
) -> list[str]:
    """检查从 P1 数据包计算 R=A+B-C 所需的缺失输入。

    Args:
        bundle: P1 结构化基金数据包。
        equity_position: 显式股票仓位输入。

    Returns:
        缺失原因列表；为空表示输入齐备。

    Raises:
        无显式抛出。
    """

    reasons: list[str] = []
    if bundle.nav_benchmark_performance.extraction_mode == "missing":
        reasons.append("缺少 §3 净值增长率/业绩比较基准收益率")
    elif _field_value_missing(bundle.nav_benchmark_performance, "nav_growth_rate"):
        reasons.append("缺少 §3 净值增长率")
    elif _field_value_missing(bundle.nav_benchmark_performance, "benchmark_return_rate"):
        reasons.append("缺少 §3 业绩比较基准收益率")

    if bundle.fee_schedule.extraction_mode == "missing":
        reasons.append("缺少 §2 管理费/托管费")
    elif _field_value_missing(bundle.fee_schedule, "management_fee"):
        reasons.append("缺少 §2 管理费")
    elif _field_value_missing(bundle.fee_schedule, "custody_fee"):
        reasons.append("缺少 §2 托管费")

    if bundle.turnover_rate.extraction_mode == "missing":
        reasons.append("缺少 §8 换手率")
    elif _field_value_missing(bundle.turnover_rate, "turnover_rate"):
        reasons.append("缺少 §8 换手率")

    if equity_position is None:
        reasons.append("缺少显式股票仓位，不能计算 B=业绩比较基准收益率×股票仓位")
    return reasons


def _field_value_missing(field: ExtractedField[dict[str, object]], key: str) -> bool:
    """检查抽取字段中的指定子值是否缺失。

    Args:
        field: 抽取字段。
        key: 子字段名。

    Returns:
        子值缺失时返回 `True`。

    Raises:
        无显式抛出。
    """

    if field.value is None:
        return True
    value = field.value.get(key)
    return value is None or str(value).strip() == ""
