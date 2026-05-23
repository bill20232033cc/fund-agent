"""估值状态解析与温度计证据模型。

本模块属于 Fund Capability analysis 层，服务模板第 7 章检查清单第 6 问。
它只负责基金类型门禁、业绩基准到支持指数的精确映射，以及把显式输入或
自建温度计读数转换为结构化 `ValuationStateResolution`，不访问外部数据源。
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal
from typing import Literal

from fund_agent.fund.data.thermometer_types import ThermometerReading
from fund_agent.fund.extractors.models import EvidenceAnchor, ExtractedField, IndexProfileValue
from fund_agent.fund.fund_type import FundType

ValuationState = Literal["low", "fair", "high", "unavailable"]
ValuationStateSource = Literal[
    "explicit_user_input",
    "self_owned_thermometer",
    "unavailable_mapping",
    "unavailable_thermometer",
]
ValuationIndexTargetStatus = Literal[
    "mapped",
    "unsupported_fund_type",
    "missing_benchmark",
    "ambiguous_benchmark",
    "unsupported_index",
]

THERMOMETER_REPORT_DISCLAIMER = (
    "本温度计基于有知有行公开方法论独立计算，非有知有行官方数据。"
    "计算方法：等权 PE/PB 中位数历史分位数综合。"
    "与有知有行官方温度计可能存在合理偏差，仅供投资前风险检查参考。"
)

_SUPPORTED_AUTO_FUND_TYPES: frozenset[FundType] = frozenset(("index_fund", "enhanced_index"))
_CASH_OR_BOND_MARKERS: tuple[str, ...] = (
    "活期存款",
    "存款利率",
    "中债",
    "全债",
    "国债",
    "债券",
    "央票",
    "银行间",
)
_COMPONENT_SPLIT_PATTERN = re.compile(r"[+＋、,，;；]")
_WEIGHT_SUFFIX_PATTERN = re.compile(r"[*＊×xX]\s*\d+(?:\.\d+)?\s*%?$")
_RETURN_SUFFIXES: tuple[str, ...] = (
    "价格指数收益率",
    "全收益指数收益率",
    "指数收益率",
    "收益率",
)


@dataclass(frozen=True, slots=True)
class ValuationIndexMappingRule:
    """估值温度计支持指数映射规则。

    Attributes:
        index_code: 支持的指数代码。
        index_name: 支持的指数名称。
        aliases: 允许 exact identity 匹配的别名集合。
        supported_fund_types: 允许自动映射的基金类型。
    """

    index_code: str
    index_name: str
    aliases: tuple[str, ...]
    supported_fund_types: tuple[FundType, ...]


@dataclass(frozen=True, slots=True)
class ValuationIndexTarget:
    """基金业绩基准解析出的估值温度计目标。

    Attributes:
        status: 解析状态；仅 `mapped` 允许调用温度计。
        index_code: 命中的支持指数代码。
        index_name: 命中的支持指数名称。
        reason: 状态说明，用于灰灯原因。
        anchors: 支撑映射判断的证据锚点。
    """

    status: ValuationIndexTargetStatus
    index_code: str | None
    index_name: str | None
    reason: str
    anchors: tuple[EvidenceAnchor, ...]


@dataclass(frozen=True, slots=True)
class ValuationStateResolution:
    """估值状态解析的单一结构化真源。

    Attributes:
        state: 检查清单第 6 问估值状态，见模板第 7 章。
        source: 估值状态来源。
        reason: 面向检查清单和报告的简要原因。
        anchors: 估值状态证据锚点；ChecklistItem 只能投影这些锚点。
        disclaimer_required: 是否要求报告正文显示自建温度计免责声明。
        index_code: 温度计或映射目标指数代码。
        index_name: 温度计或映射目标指数名称。
        temperature: 综合温度。
        pe_percentile: PE 历史分位。
        pb_percentile: PB 历史分位。
        data_date: 温度计数据日期。
        lookback_start: 回溯窗口开始日期。
        lookback_end: 回溯窗口结束日期。
        thermometer_source: 温度计数据来源。
        cached: 是否使用缓存。
        stale: 是否使用 stale 缓存。
        unavailable_reason: 不可用原因。
        disclaimer: 报告中应展示的免责声明。
    """

    state: ValuationState
    source: ValuationStateSource
    reason: str
    anchors: tuple[EvidenceAnchor, ...]
    disclaimer_required: bool = False
    index_code: str | None = None
    index_name: str | None = None
    temperature: Decimal | None = None
    pe_percentile: Decimal | None = None
    pb_percentile: Decimal | None = None
    data_date: str | None = None
    lookback_start: str | None = None
    lookback_end: str | None = None
    thermometer_source: str | None = None
    cached: bool | None = None
    stale: bool | None = None
    unavailable_reason: str | None = None
    disclaimer: str | None = None


VALUATION_INDEX_MAPPING_RULES: tuple[ValuationIndexMappingRule, ...] = (
    ValuationIndexMappingRule(
        index_code="000300",
        index_name="沪深300",
        aliases=("沪深300", "沪深300指数", "CSI300", "CSI 300"),
        supported_fund_types=("index_fund", "enhanced_index"),
    ),
    ValuationIndexMappingRule(
        index_code="000905",
        index_name="中证500",
        aliases=("中证500", "中证500指数", "CSI500", "CSI 500"),
        supported_fund_types=("index_fund", "enhanced_index"),
    ),
)


def resolve_valuation_index_target(
    *,
    fund_type: FundType,
    index_profile: ExtractedField[IndexProfileValue],
    benchmark: ExtractedField[dict[str, object]],
) -> ValuationIndexTarget:
    """解析自动估值可调用的自建温度计指数目标，见模板第 7 章第 6 问。

    Args:
        fund_type: P1 已识别的基金类型。
        index_profile: 指数画像结构化字段。
        benchmark: 业绩比较基准字段。

    Returns:
        指数目标解析结果；非 `mapped` 状态不得调用温度计。

    Raises:
        无显式抛出。
    """

    anchors = _dedupe_anchors((*index_profile.anchors, *benchmark.anchors))
    if fund_type not in _SUPPORTED_AUTO_FUND_TYPES:
        return ValuationIndexTarget(
            status="unsupported_fund_type",
            index_code=None,
            index_name=None,
            reason=f"基金类型 {fund_type} 不适用 A 股宽基指数温度计自动估值。",
            anchors=anchors,
        )

    profile_value = index_profile.value
    if profile_value is not None and profile_value.benchmark_index_code:
        code_rule = _rule_for_supported_code(profile_value.benchmark_index_code)
        if code_rule is not None:
            compatibility = _validate_code_text_compatibility(
                rule=code_rule,
                index_profile=index_profile,
                benchmark=benchmark,
                anchors=anchors,
            )
            if compatibility is not None:
                return compatibility
            return _target_from_rule(code_rule, anchors=anchors)
        return ValuationIndexTarget(
            status="unsupported_index",
            index_code=None,
            index_name=None,
            reason=f"基准指数代码 {profile_value.benchmark_index_code} 不在 P19-S3 支持范围。",
            anchors=anchors,
        )

    components = _benchmark_components(index_profile=index_profile, benchmark=benchmark)
    if not components:
        return ValuationIndexTarget(
            status="missing_benchmark",
            index_code=None,
            index_name=None,
            reason="缺少可解析的业绩基准或指数画像，自动估值不可用。",
            anchors=anchors,
        )

    matched_rules: list[ValuationIndexMappingRule] = []
    unsupported_equity_seen = False
    uncertain_component_seen = False
    for component in components:
        normalized = _normalize_component_identity(component)
        if not normalized:
            continue
        rule = _rule_for_exact_alias(normalized)
        if rule is not None:
            matched_rules.append(rule)
            continue
        if _is_cash_or_bond_component(normalized):
            continue
        if _looks_like_supported_derived_index(normalized) or _looks_like_equity_index(normalized):
            unsupported_equity_seen = True
            continue
        uncertain_component_seen = True

    distinct_rules = tuple({rule.index_code: rule for rule in matched_rules}.values())
    if len(distinct_rules) > 1:
        return ValuationIndexTarget(
            status="ambiguous_benchmark",
            index_code=None,
            index_name=None,
            reason="业绩基准包含多个支持的权益指数，无法选择单一温度计。",
            anchors=anchors,
        )
    if distinct_rules and (unsupported_equity_seen or uncertain_component_seen):
        return ValuationIndexTarget(
            status="ambiguous_benchmark",
            index_code=None,
            index_name=None,
            reason="业绩基准同时包含支持指数和无法精确归类的权益成分。",
            anchors=anchors,
        )
    if distinct_rules:
        rule = distinct_rules[0]
        return ValuationIndexTarget(
            status="mapped",
            index_code=rule.index_code,
            index_name=rule.index_name,
            reason=f"业绩基准精确映射到 {rule.index_name}（{rule.index_code}）。",
            anchors=anchors,
        )
    status: ValuationIndexTargetStatus = "unsupported_index"
    reason = "业绩基准未精确匹配 P19-S3 支持的沪深300或中证500。"
    if uncertain_component_seen:
        status = "ambiguous_benchmark"
        reason = "业绩基准成分无法精确归类，自动估值不可用。"
    return ValuationIndexTarget(
        status=status,
        index_code=None,
        index_name=None,
        reason=reason,
        anchors=anchors,
    )


def build_explicit_valuation_resolution(state: ValuationState) -> ValuationStateResolution:
    """构造用户显式输入的估值状态解析结果，见模板第 7 章第 6 问。

    Args:
        state: 用户显式提供的估值状态。

    Returns:
        显式输入来源的估值状态解析结果。

    Raises:
        ValueError: 当估值状态不在允许集合内时抛出。
    """

    if state not in {"low", "fair", "high", "unavailable"}:
        raise ValueError("valuation_state 必须是 low / fair / high / unavailable")
    reason = "用户显式输入当前估值状态为 unavailable，保留手动灰灯。" if state == "unavailable" else (
        f"用户显式输入当前估值状态为 {state}。"
    )
    return ValuationStateResolution(
        state=state,
        source="explicit_user_input",
        reason=reason,
        anchors=(_explicit_user_input_anchor(state),),
        disclaimer_required=False,
    )


def build_unavailable_valuation_resolution(
    target: ValuationIndexTarget | None = None,
    *,
    reason: str | None = None,
) -> ValuationStateResolution:
    """构造未调用温度计的灰灯估值解析结果，见模板第 7 章第 6 问。

    Args:
        target: 基准映射目标。
        reason: 显式灰灯原因；提供时优先于 target reason。

    Returns:
        映射不可用来源的估值状态解析结果。

    Raises:
        无显式抛出。
    """

    unavailable_reason = reason or (target.reason if target is not None else "自动估值不可用。")
    anchors = target.anchors if target is not None else (_unavailable_anchor(unavailable_reason),)
    if not anchors:
        anchors = (_unavailable_anchor(unavailable_reason),)
    return ValuationStateResolution(
        state="unavailable",
        source="unavailable_mapping",
        reason=f"自动估值不可用：{unavailable_reason}",
        anchors=anchors,
        unavailable_reason=unavailable_reason,
        index_code=target.index_code if target is not None else None,
        index_name=target.index_name if target is not None else None,
    )


def build_thermometer_valuation_resolution(
    reading: ThermometerReading,
) -> ValuationStateResolution:
    """把自建温度计读数转换为估值状态解析结果，见模板第 7 章第 6 问。

    Args:
        reading: 自建温度计单指数读数。

    Returns:
        温度计来源的估值状态解析结果。

    Raises:
        ValueError: 当读数候选状态或可用读数字段不满足契约时抛出。
    """

    if reading.valuation_state_candidate not in {"low", "fair", "high", "unavailable"}:
        raise ValueError("温度计返回了非法 valuation_state_candidate")
    if reading.unavailable:
        reason = reading.unavailable_reason or "自建温度计数据不可用。"
        return ValuationStateResolution(
            state="unavailable",
            source="unavailable_thermometer",
            reason=f"自动估值不可用：{reason}",
            anchors=(_thermometer_anchor(reading, state="unavailable", unavailable_reason=reason),),
            disclaimer_required=True,
            index_code=reading.index_code,
            index_name=reading.index_name,
            thermometer_source=reading.source,
            cached=reading.cached,
            stale=reading.stale,
            unavailable_reason=reason,
            disclaimer=THERMOMETER_REPORT_DISCLAIMER,
        )

    _validate_available_reading(reading)
    state = reading.valuation_state_candidate
    return ValuationStateResolution(
        state=state,
        source="self_owned_thermometer",
        reason=(
            f"自建温度计显示 {reading.index_name}（{reading.index_code}）估值状态为 {state}，"
            f"温度 {reading.temperature}，数据日 {reading.data_date}。"
        ),
        anchors=(_thermometer_anchor(reading, state=state, unavailable_reason=None),),
        disclaimer_required=True,
        index_code=reading.index_code,
        index_name=reading.index_name,
        temperature=reading.temperature,
        pe_percentile=reading.pe_percentile,
        pb_percentile=reading.pb_percentile,
        data_date=reading.data_date,
        lookback_start=reading.lookback_start,
        lookback_end=reading.lookback_end,
        thermometer_source=reading.source,
        cached=reading.cached,
        stale=reading.stale,
        unavailable_reason=reading.unavailable_reason,
        disclaimer=THERMOMETER_REPORT_DISCLAIMER,
    )


def build_thermometer_failure_anchor(
    *,
    index_code: str,
    index_name: str,
    unavailable_reason: str,
) -> EvidenceAnchor:
    """构造自建温度计失败派生锚点，见模板第 7 章第 6 问。

    Args:
        index_code: 目标指数代码。
        index_name: 目标指数名称。
        unavailable_reason: 温度计不可用原因。

    Returns:
        记录温度计失败 provenance 的 derived 锚点。

    Raises:
        无显式抛出。
    """

    return EvidenceAnchor(
        source_kind="derived",
        document_year=None,
        section_id="thermometer",
        page_number=None,
        table_id="self_owned_thermometer",
        row_locator=f"{index_code}:calculation_error",
        note=(
            f"self_owned_thermometer failure；index_code={index_code}；"
            f"index_name={index_name}；unavailable_reason={unavailable_reason}；"
            f"{THERMOMETER_REPORT_DISCLAIMER}"
        ),
    )


def _rule_for_supported_code(index_code: str) -> ValuationIndexMappingRule | None:
    """按支持指数代码查找映射规则。

    Args:
        index_code: 指数代码。

    Returns:
        支持时返回映射规则，否则返回 `None`。

    Raises:
        无显式抛出。
    """

    stripped = index_code.strip()
    for rule in VALUATION_INDEX_MAPPING_RULES:
        if stripped == rule.index_code:
            return rule
    return None


def _target_from_rule(
    rule: ValuationIndexMappingRule,
    *,
    anchors: tuple[EvidenceAnchor, ...],
) -> ValuationIndexTarget:
    """按支持指数规则构造映射目标。

    Args:
        rule: 指数映射规则。
        anchors: 业绩基准证据锚点。

    Returns:
        映射目标。

    Raises:
        无显式抛出。
    """

    return ValuationIndexTarget(
        status="mapped",
        index_code=rule.index_code,
        index_name=rule.index_name,
        reason=f"指数画像已精确识别为 {rule.index_name}（{rule.index_code}）。",
        anchors=anchors,
    )


def _validate_code_text_compatibility(
    *,
    rule: ValuationIndexMappingRule,
    index_profile: ExtractedField[IndexProfileValue],
    benchmark: ExtractedField[dict[str, object]],
    anchors: tuple[EvidenceAnchor, ...],
) -> ValuationIndexTarget | None:
    """校验 benchmark_index_code 与同源基准文本是否兼容。

    Args:
        rule: benchmark_index_code 命中的支持指数规则。
        index_profile: 指数画像字段。
        benchmark: 业绩基准字段。
        anchors: 基准证据锚点。

    Returns:
        不兼容时返回 fail-closed target；兼容或无文本时返回 `None`。

    Raises:
        无显式抛出。
    """

    components = _benchmark_components(index_profile=index_profile, benchmark=benchmark)
    if not components:
        return None

    exact_rule_seen = False
    unsupported_equity_seen = False
    uncertain_component_seen = False
    other_supported_rule_seen = False
    for component in components:
        normalized = _normalize_component_identity(component)
        if not normalized:
            continue
        component_rule = _rule_for_exact_alias(normalized)
        if component_rule is not None:
            if component_rule.index_code == rule.index_code:
                exact_rule_seen = True
            else:
                other_supported_rule_seen = True
            continue
        if _is_cash_or_bond_component(normalized):
            continue
        if _looks_like_supported_derived_index(normalized) or _looks_like_equity_index(normalized):
            unsupported_equity_seen = True
            continue
        uncertain_component_seen = True

    if other_supported_rule_seen or (exact_rule_seen and (unsupported_equity_seen or uncertain_component_seen)):
        return ValuationIndexTarget(
            status="ambiguous_benchmark",
            index_code=None,
            index_name=None,
            reason="基准指数代码与同源基准文本存在歧义，自动估值不可用。",
            anchors=anchors,
        )
    if unsupported_equity_seen:
        return ValuationIndexTarget(
            status="unsupported_index",
            index_code=None,
            index_name=None,
            reason="基准指数代码对应文本包含派生、策略、行业或未支持权益指数，自动估值不可用。",
            anchors=anchors,
        )
    if uncertain_component_seen:
        return ValuationIndexTarget(
            status="ambiguous_benchmark",
            index_code=None,
            index_name=None,
            reason="基准指数代码对应文本包含无法精确归类的基准成分，自动估值不可用。",
            anchors=anchors,
        )
    return None


def _benchmark_components(
    *,
    index_profile: ExtractedField[IndexProfileValue],
    benchmark: ExtractedField[dict[str, object]],
) -> tuple[str, ...]:
    """读取并拆分业绩基准候选成分。

    Args:
        index_profile: 指数画像字段。
        benchmark: 业绩比较基准字段。

    Returns:
        候选成分文本元组。

    Raises:
        无显式抛出。
    """

    profile_value = index_profile.value
    raw_values: list[str] = []
    if profile_value is not None:
        raw_values.extend(component for component in profile_value.benchmark_component_text)
        raw_values.extend(
            value
            for value in (profile_value.benchmark_index_name, profile_value.benchmark_text)
            if value
        )
    benchmark_value = benchmark.value or {}
    for key in ("benchmark_text", "benchmark", "performance_benchmark"):
        value = benchmark_value.get(key)
        if isinstance(value, str) and value.strip():
            raw_values.append(value)

    components: list[str] = []
    for raw_value in raw_values:
        components.extend(_split_benchmark_components(raw_value))
    return tuple(component for component in components if component.strip())


def _split_benchmark_components(text: str) -> tuple[str, ...]:
    """把复合基准文本拆成组件。

    Args:
        text: 原始基准文本。

    Returns:
        基准组件元组。

    Raises:
        无显式抛出。
    """

    normalized = text.replace("（", "(").replace("）", ")")
    return tuple(part.strip(" ()") for part in _COMPONENT_SPLIT_PATTERN.split(normalized))


def _normalize_component_identity(component: str) -> str:
    """规范化组件身份文本但不删除风格、行业或策略修饰语。

    Args:
        component: 原始组件文本。

    Returns:
        规范化后的组件身份。

    Raises:
        无显式抛出。
    """

    text = component.strip()
    text = text.replace("　", " ").replace("（", "(").replace("）", ")")
    text = re.sub(r"\s+", " ", text)
    text = _WEIGHT_SUFFIX_PATTERN.sub("", text).strip()
    text = re.sub(r"^\d+(?:\.\d+)?\s*%\s*[*＊×xX]?\s*", "", text).strip()
    for suffix in _RETURN_SUFFIXES:
        if text.endswith(suffix):
            text = text[: -len(suffix)].strip()
            if suffix == "指数收益率" and not text.endswith("指数"):
                text = f"{text}指数"
            break
    # 中文指数名中的空格不构成身份差异；CSI 300 同时保留空格版本用于 exact alias。
    if not text.upper().startswith("CSI "):
        text = text.replace(" ", "")
    return text


def _rule_for_exact_alias(normalized_component: str) -> ValuationIndexMappingRule | None:
    """按 exact identity 查找支持指数规则。

    Args:
        normalized_component: 规范化组件身份。

    Returns:
        命中的支持指数规则；未命中返回 `None`。

    Raises:
        无显式抛出。
    """

    upper_component = normalized_component.upper()
    for rule in VALUATION_INDEX_MAPPING_RULES:
        normalized_aliases = {_normalize_alias(alias) for alias in rule.aliases}
        if _normalize_alias(upper_component) in normalized_aliases:
            return rule
    return None


def _normalize_alias(alias: str) -> str:
    """规范化支持指数别名。

    Args:
        alias: 指数别名。

    Returns:
        规范化别名。

    Raises:
        无显式抛出。
    """

    return alias.upper().replace(" ", "")


def _is_cash_or_bond_component(normalized_component: str) -> bool:
    """判断组件是否属于可忽略的现金或债券基准。

    Args:
        normalized_component: 规范化组件身份。

    Returns:
        属于现金或债券成分时返回 `True`。

    Raises:
        无显式抛出。
    """

    return any(marker in normalized_component for marker in _CASH_OR_BOND_MARKERS)


def _looks_like_supported_derived_index(normalized_component: str) -> bool:
    """判断组件是否是含支持别名的派生指数。

    Args:
        normalized_component: 规范化组件身份。

    Returns:
        含沪深300或中证500但不是 exact identity 时返回 `True`。

    Raises:
        无显式抛出。
    """

    compact = _normalize_alias(normalized_component)
    return (
        ("沪深300" in compact or "CSI300" in compact or "中证500" in compact or "CSI500" in compact)
        and _rule_for_exact_alias(normalized_component) is None
    )


def _looks_like_equity_index(normalized_component: str) -> bool:
    """粗粒度识别权益指数成分，用于 fail-closed ambiguity。

    Args:
        normalized_component: 规范化组件身份。

    Returns:
        看起来像权益指数时返回 `True`。

    Raises:
        无显式抛出。
    """

    if "指数" not in normalized_component and not normalized_component.upper().startswith("CSI"):
        return False
    return not _is_cash_or_bond_component(normalized_component)


def _validate_available_reading(reading: ThermometerReading) -> None:
    """校验可用温度计读数字段完整性。

    Args:
        reading: 自建温度计读数。

    Returns:
        无返回值。

    Raises:
        ValueError: 当必要字段缺失时抛出。
    """

    required_values = (
        reading.index_code,
        reading.index_name,
        reading.temperature,
        reading.pe_percentile,
        reading.pb_percentile,
        reading.data_date,
        reading.lookback_start,
        reading.lookback_end,
        reading.source,
    )
    if any(value is None or value == "" for value in required_values):
        raise ValueError("可用温度计读数缺少必要字段")


def _explicit_user_input_anchor(state: ValuationState) -> EvidenceAnchor:
    """构造用户显式估值输入锚点。

    Args:
        state: 用户显式估值状态。

    Returns:
        派生锚点。

    Raises:
        无显式抛出。
    """

    return EvidenceAnchor(
        source_kind="derived",
        document_year=None,
        section_id="user_input",
        page_number=None,
        table_id=None,
        row_locator="valuation_state",
        note=f"用户显式输入 valuation_state={state}",
    )


def _unavailable_anchor(reason: str) -> EvidenceAnchor:
    """构造自动估值不可用派生锚点。

    Args:
        reason: 不可用原因。

    Returns:
        派生锚点。

    Raises:
        无显式抛出。
    """

    return EvidenceAnchor(
        source_kind="derived",
        document_year=None,
        section_id="valuation_state",
        page_number=None,
        table_id=None,
        row_locator="unavailable_mapping",
        note=reason,
    )


def _thermometer_anchor(
    reading: ThermometerReading,
    *,
    state: ValuationState,
    unavailable_reason: str | None,
) -> EvidenceAnchor:
    """构造自建温度计证据锚点。

    Args:
        reading: 自建温度计读数。
        state: 投影后的估值状态。
        unavailable_reason: 温度计不可用原因。

    Returns:
        外部数据锚点。

    Raises:
        无显式抛出。
    """

    note_parts = [
        f"index={reading.index_code}",
        f"state={state}",
        f"temperature={reading.temperature}",
        f"pe_percentile={reading.pe_percentile}",
        f"pb_percentile={reading.pb_percentile}",
        f"lookback={reading.lookback_start}..{reading.lookback_end}",
        f"cached={reading.cached}",
        f"stale={reading.stale}",
        THERMOMETER_REPORT_DISCLAIMER,
    ]
    if unavailable_reason:
        note_parts.append(f"unavailable_reason={unavailable_reason}")
    return EvidenceAnchor(
        source_kind="external_api",
        document_year=None,
        section_id="thermometer",
        page_number=None,
        table_id=reading.source,
        row_locator=f"{reading.index_code}:{reading.data_date}",
        note="；".join(note_parts),
    )


def _dedupe_anchors(anchors: tuple[EvidenceAnchor, ...]) -> tuple[EvidenceAnchor, ...]:
    """按值去重证据锚点。

    Args:
        anchors: 原始锚点。

    Returns:
        稳定顺序去重锚点。

    Raises:
        无显式抛出。
    """

    deduped: list[EvidenceAnchor] = []
    seen: set[EvidenceAnchor] = set()
    for anchor in anchors:
        if anchor in seen:
            continue
        deduped.append(anchor)
        seen.add(anchor)
    return tuple(deduped)
