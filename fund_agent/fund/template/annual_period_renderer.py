"""多年年报期间报告渲染器，见模板第 5 章“当前阶段”。

本模块属于 Agent 层 Fund 领域能力，只消费内存中的 `AnnualEvidenceBundle`
和显式传入的当前年份报告 Markdown，不读取 repository、PDF/cache、来源 helper、
provider、LLM 或文件系统文档语料。
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Final, Mapping

from fund_agent.fund.annual_evidence import AnnualEvidenceAnchor, AnnualEvidenceBundle

ANNUAL_PERIOD_REPORT_SCHEMA_VERSION: Final[str] = "annual_period_report.v1"
QUALITY_GATE_STATUS_NOT_AVAILABLE: Final[str] = "not_available"
_FORBIDDEN_ANNUAL_PERIOD_PHRASES: Final[tuple[str, ...]] = (
    "买入金额",
    "卖出时机",
    "买入信号",
    "卖出信号",
    "仓位比例",
    "收益预测",
)
_DIRECT_TRADING_ADVICE_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"(建议|推荐|应当|应该|直接|立即|马上)"
    r"[\s，,。；;：:、]{0,4}"
    r"(买入|卖出|加仓|减仓)"
)
_UNSUPPORTED_CAUSAL_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"(必然|一定会|保证|确保|导致收益|带来收益|决定收益)"
)
_CURRENT_YEAR_REPORT_MARKER: Final[str] = "<!-- current_year_report:start -->"


@dataclass(frozen=True, slots=True)
class AnnualPeriodReportRenderInput:
    """多年年报期间报告渲染输入。

    Attributes:
        annual_evidence_bundle: Fund 层多年年报证据 bundle。
        current_year_report_markdown: 当前必需年份 8 章报告 Markdown。
        quality_gate_status: 显式 quality gate 状态；缺失时渲染为 `not_available`。
        quality_gate_not_run_reason: quality gate 未运行原因；只作为安全短说明。
    """

    annual_evidence_bundle: AnnualEvidenceBundle
    current_year_report_markdown: str
    quality_gate_status: str | None = None
    quality_gate_not_run_reason: str | None = None


@dataclass(frozen=True, slots=True)
class AnnualPeriodReportRenderResult:
    """多年年报期间报告渲染结果。

    Attributes:
        schema_version: 报告 schema 版本。
        report_markdown: 完整多年年报期间报告 Markdown。
        period_summary_markdown: 不含当前年份 8 章报告的期间摘要 Markdown。
        current_year_report_markdown: 原样保留的当前年份报告 Markdown。
        available_years: 可用年份。
        gap_years: 可降级缺口年份。
        fail_closed_years: fail-closed 年份。
        cross_year_fact_count: 跨年事实数量。
    """

    schema_version: str
    report_markdown: str
    period_summary_markdown: str
    current_year_report_markdown: str
    available_years: tuple[int, ...]
    gap_years: tuple[int, ...]
    fail_closed_years: tuple[int, ...]
    cross_year_fact_count: int


def render_annual_period_report(
    input_data: AnnualPeriodReportRenderInput,
) -> AnnualPeriodReportRenderResult:
    """渲染确定性多年年报期间报告。

    Args:
        input_data: 多年年报期间报告渲染输入。

    Returns:
        多年年报期间报告渲染结果。

    Raises:
        ValueError: 当输入 bundle 身份或当前年份报告非法，或摘要包含禁用措辞时抛出。
    """

    bundle = input_data.annual_evidence_bundle
    current_year_report = input_data.current_year_report_markdown.strip()
    _validate_render_input(bundle, current_year_report)
    quality_gate_status = input_data.quality_gate_status or QUALITY_GATE_STATUS_NOT_AVAILABLE
    period_summary = "\n\n".join(
        (
            _render_title(bundle),
            _render_coverage_section(bundle, quality_gate_status, input_data.quality_gate_not_run_reason),
            _render_cross_year_fact_section(bundle),
            _render_impact_section(bundle),
            _render_gap_section(bundle),
        )
    )
    validate_annual_period_report_wording(period_summary)
    report_markdown = (
        f"{period_summary}\n\n"
        "## 当前年份报告\n\n"
        f"{_CURRENT_YEAR_REPORT_MARKER}\n\n"
        f"{current_year_report}\n"
    )
    return AnnualPeriodReportRenderResult(
        schema_version=ANNUAL_PERIOD_REPORT_SCHEMA_VERSION,
        report_markdown=report_markdown,
        period_summary_markdown=period_summary,
        current_year_report_markdown=current_year_report,
        available_years=bundle.available_years,
        gap_years=bundle.gap_years,
        fail_closed_years=bundle.fail_closed_years,
        cross_year_fact_count=len(bundle.cross_year_facts),
    )


def validate_annual_period_report_wording(report_markdown: str) -> None:
    """校验多年年报期间摘要不含禁用交易、收益预测或强因果措辞。

    Args:
        report_markdown: 待校验的多年期间摘要 Markdown。

    Returns:
        无返回值。

    Raises:
        ValueError: 当摘要包含禁用措辞时抛出。
    """

    forbidden_hits = tuple(
        phrase for phrase in _FORBIDDEN_ANNUAL_PERIOD_PHRASES if phrase in report_markdown
    )
    forbidden_hits += tuple(
        match.group(0).strip()
        for match in _DIRECT_TRADING_ADVICE_PATTERN.finditer(report_markdown)
    )
    forbidden_hits += tuple(
        match.group(0).strip()
        for match in _UNSUPPORTED_CAUSAL_PATTERN.finditer(_impact_section(report_markdown))
    )
    if forbidden_hits:
        raise ValueError(f"多年年报期间报告包含禁用措辞：{'、'.join(forbidden_hits)}")


def _validate_render_input(bundle: AnnualEvidenceBundle, current_year_report: str) -> None:
    """校验 renderer 输入身份和当前年份报告。

    Args:
        bundle: 多年年报证据 bundle。
        current_year_report: 当前年份报告 Markdown。

    Returns:
        无返回值。

    Raises:
        ValueError: 当输入不满足渲染前置条件时抛出。
    """

    if not current_year_report:
        raise ValueError("current_year_report_markdown 不能为空")
    if not bundle.fund_code or len(bundle.fund_code) != 6 or not bundle.fund_code.isdigit():
        raise ValueError("annual_evidence_bundle.fund_code 必须是 6 位数字")
    if bundle.target_year <= 0:
        raise ValueError("annual_evidence_bundle.target_year 必须为正整数")
    if not bundle.canonical_years or bundle.canonical_years[0] != bundle.target_year:
        raise ValueError("annual_evidence_bundle.canonical_years 必须以 target_year 开头")
    if bundle.current_year_bundle.fund_code != bundle.fund_code:
        raise ValueError("annual_evidence_bundle.current_year_bundle.fund_code 不一致")
    if bundle.current_year_bundle.report_year != bundle.target_year:
        raise ValueError("annual_evidence_bundle.current_year_bundle.report_year 不一致")


def _render_title(bundle: AnnualEvidenceBundle) -> str:
    """渲染多年期间报告标题。

    Args:
        bundle: 多年年报证据 bundle。

    Returns:
        标题 Markdown。

    Raises:
        无显式抛出。
    """

    start_year = min(bundle.canonical_years)
    end_year = max(bundle.canonical_years)
    return f"# 多年年报分析（{start_year}-{end_year}）"


def _render_coverage_section(
    bundle: AnnualEvidenceBundle,
    quality_gate_status: str,
    quality_gate_not_run_reason: str | None,
) -> str:
    """渲染年度覆盖与来源章节。

    Args:
        bundle: 多年年报证据 bundle。
        quality_gate_status: quality gate 状态。
        quality_gate_not_run_reason: quality gate 未运行原因。

    Returns:
        年度覆盖与来源 Markdown。

    Raises:
        无显式抛出。
    """

    lines = [
        "## 年度覆盖与来源",
        "",
        f"- canonical_years: {_format_years(bundle.canonical_years)}",
        f"- available_years: {_format_years(bundle.available_years)}",
        f"- gap_years: {_format_years(bundle.gap_years)}",
        f"- fail_closed_years: {_format_years(bundle.fail_closed_years)}",
        f"- fallback_year_count: {_safe_value(bundle.fallback_summary.get('fallback_year_count'))}",
        f"- quality_gate_status={_safe_value(quality_gate_status)}",
    ]
    if quality_gate_status == QUALITY_GATE_STATUS_NOT_AVAILABLE:
        lines.append("- quality_gate_note: 未提供质量门控状态，本报告不据此声明通过或 readiness。")
    elif quality_gate_not_run_reason:
        lines.append(f"- quality_gate_note: {_safe_text(quality_gate_not_run_reason)}")
    lines.extend(("", "| 年份 | 可用性 | 来源 | fallback |", "|---|---|---|---|"))
    for year in bundle.canonical_years:
        lines.append(_render_source_row(bundle, year))
    return "\n".join(lines)


def _render_source_row(bundle: AnnualEvidenceBundle, year: int) -> str:
    """渲染单个年份的来源行。

    Args:
        bundle: 多年年报证据 bundle。
        year: 年份。

    Returns:
        Markdown 表格行。

    Raises:
        无显式抛出。
    """

    provenance = bundle.source_provenance_by_year.get(year)
    status = _year_status(bundle, year)
    if provenance is None:
        return f"| {year} | {status} | unavailable | unavailable |"
    source_text = (
        f"selected_source={_safe_value(provenance.selected_source)}; "
        f"source_mode={_safe_value(provenance.source_mode)}"
    )
    fallback_text = (
        f"enabled={_safe_value(provenance.fallback_enabled)}; "
        f"used={_safe_value(provenance.fallback_used)}"
    )
    return f"| {year} | {status} | {source_text} | {fallback_text} |"


def _render_cross_year_fact_section(bundle: AnnualEvidenceBundle) -> str:
    """渲染跨年关键变化章节。

    Args:
        bundle: 多年年报证据 bundle。

    Returns:
        跨年关键变化 Markdown。

    Raises:
        无显式抛出。
    """

    lines = ["## 跨年关键变化", ""]
    if not bundle.cross_year_facts:
        lines.append("- 跨年事实：insufficient_evidence，当前 bundle 未产出可渲染跨年事实。")
        lines.append("- 下一步最小验证问题：补齐 prior 年份可用字段后再比较第 5 章关键变化。")
        return "\n".join(lines)
    for fact in bundle.cross_year_facts:
        anchors = _format_fact_anchors(bundle, fact.source_year_anchor_ids)
        lines.extend(
            (
                f"- fact_id={_safe_text(fact.fact_id)}",
                f"  - fact_type={_safe_text(fact.fact_type)}",
                f"  - source_field_id={_safe_text(fact.source_field_id)}",
                f"  - source_years={_format_years(fact.source_years)}",
                f"  - values_by_year={_safe_value(fact.values_by_year)}",
                f"  - evidence_anchors={anchors}",
            )
        )
        if fact.caveats:
            lines.append(f"  - caveats={_safe_value(fact.caveats)}")
    return "\n".join(lines)


def _render_impact_section(bundle: AnnualEvidenceBundle) -> str:
    """渲染对当前判断的影响章节。

    Args:
        bundle: 多年年报证据 bundle。

    Returns:
        对当前判断的影响 Markdown。

    Raises:
        无显式抛出。
    """

    lines = ["## 对当前判断的影响", ""]
    if not bundle.cross_year_facts:
        lines.append("- impact_status=insufficient_evidence")
        lines.append("- 说明：当前期间证据不足，只保留目标年份报告结论，不扩展跨年判断。")
        return "\n".join(lines)
    lines.append("- impact_status=evidence_context_only")
    lines.append("- 说明：跨年事实仅作为第 5 章期间证据补充；当前结论仍以目标年份报告和质量门控为准。")
    lines.append("- 边界：不预测未来收益，不给出交易或配置指令，不把跨年事实升级为更强结论。")
    return "\n".join(lines)


def _render_gap_section(bundle: AnnualEvidenceBundle) -> str:
    """渲染缺口与降级章节。

    Args:
        bundle: 多年年报证据 bundle。

    Returns:
        缺口与降级 Markdown。

    Raises:
        无显式抛出。
    """

    lines = [
        "## 缺口与降级",
        "",
        f"- gap_years: {_format_years(bundle.gap_years)}",
        f"- fail_closed_years: {_format_years(bundle.fail_closed_years)}",
    ]
    if bundle.gap_years:
        lines.append("- gap_note: 这些年份未进入跨年正向判断，只记录为可降级证据缺口。")
    if bundle.fail_closed_years:
        lines.append("- fail_closed_note: 这些年份阻断依赖该年份的跨年 claims。")
    if not bundle.gap_years and not bundle.fail_closed_years:
        lines.append("- degradation_note: 未记录 prior 年份缺口或 fail-closed 年份。")
    for gap in bundle.data_gaps:
        lines.append(
            f"- data_gap: year={gap.year}; status={gap.status}; "
            f"category={_safe_value(gap.source_failure_category)}; message={_safe_text(gap.message)}"
        )
    return "\n".join(lines)


def _year_status(bundle: AnnualEvidenceBundle, year: int) -> str:
    """返回年份可用性状态。

    Args:
        bundle: 多年年报证据 bundle。
        year: 年份。

    Returns:
        年份状态。

    Raises:
        无显式抛出。
    """

    if year in bundle.available_years:
        return "available"
    if year in bundle.gap_years:
        return "gap"
    if year in bundle.fail_closed_years:
        return "failed_closed"
    return "unknown"


def _format_fact_anchors(bundle: AnnualEvidenceBundle, anchor_ids: tuple[str, ...]) -> str:
    """格式化跨年事实锚点。

    Args:
        bundle: 多年年报证据 bundle。
        anchor_ids: 跨年事实引用的锚点 ID。

    Returns:
        安全锚点摘要。

    Raises:
        无显式抛出。
    """

    if not anchor_ids:
        return "anchor not emitted"
    rendered = []
    for anchor_id in anchor_ids:
        anchor = bundle.anchor_by_id(anchor_id)
        rendered.append(_format_anchor(anchor_id, anchor))
    return "; ".join(rendered)


def _format_anchor(anchor_id: str, anchor: AnnualEvidenceAnchor | None) -> str:
    """格式化单个年度锚点。

    Args:
        anchor_id: 锚点 ID。
        anchor: 命中的年度锚点；缺失时为空。

    Returns:
        锚点摘要。

    Raises:
        无显式抛出。
    """

    if anchor is None:
        return f"anchor not emitted: {_safe_text(anchor_id)}"
    return (
        f"{_safe_text(anchor.anchor_id)}("
        f"year={anchor.source_year}, "
        f"field={_safe_text(anchor.source_field_id)}, "
        f"section={_safe_value(anchor.section_id)}, "
        f"row={_safe_value(anchor.row_locator)}"
        ")"
    )


def _format_years(years: tuple[int, ...]) -> str:
    """格式化年份元组。

    Args:
        years: 年份元组。

    Returns:
        逗号分隔年份；空元组返回 `none`。

    Raises:
        无显式抛出。
    """

    if not years:
        return "none"
    return ",".join(str(year) for year in years)


def _safe_value(value: object) -> str:
    """把值格式化为安全短文本。

    Args:
        value: 任意值。

    Returns:
        可渲染文本。

    Raises:
        无显式抛出。
    """

    if value is None:
        return "none"
    if isinstance(value, str):
        return _safe_text(value)
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int | float):
        return str(value)
    try:
        return _safe_text(json.dumps(_sanitize_value(value), ensure_ascii=False, sort_keys=True))
    except TypeError:
        return _safe_text(str(value))


def _sanitize_value(value: object) -> object:
    """递归清洗可能包含路径的结构化值。

    Args:
        value: 任意结构化值。

    Returns:
        JSON 兼容的清洗后值。

    Raises:
        无显式抛出。
    """

    if isinstance(value, str):
        return _safe_text(value)
    if isinstance(value, Mapping):
        return {str(key): _sanitize_value(item) for key, item in value.items()}
    if isinstance(value, tuple | list):
        return [_sanitize_value(item) for item in value]
    return value


def _safe_text(text: str) -> str:
    """清洗单个文本值，避免输出 raw PDF/cache/path 形态。

    Args:
        text: 原始文本。

    Returns:
        清洗后的单行文本。

    Raises:
        无显式抛出。
    """

    normalized = " ".join(text.split())
    lowered = normalized.lower()
    if ".pdf" in lowered or "cache/" in lowered or "\\cache\\" in lowered:
        return "redacted_path"
    if normalized.startswith("/") or normalized.startswith("~"):
        return "redacted_path"
    return normalized or "none"


def _impact_section(report_markdown: str) -> str:
    """提取 `对当前判断的影响` 章节用于 section-specific wording guard。

    Args:
        report_markdown: 多年期间摘要 Markdown。

    Returns:
        命中的影响章节；未命中时返回空字符串。

    Raises:
        无显式抛出。
    """

    marker = "## 对当前判断的影响"
    start = report_markdown.find(marker)
    if start < 0:
        return ""
    next_start = report_markdown.find("\n## ", start + len(marker))
    if next_start < 0:
        return report_markdown[start:]
    return report_markdown[start:next_start]
