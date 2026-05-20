"""基金 8 章模板渲染器。

本模块属于基金 Capability 层，服务 `docs/design.md` 第 3.1 节 8 章模板。
它只消费 P1/P2 已形成的结构化结果，不直接读取年报、PDF、缓存或文档仓库。
当前实现是 MVP 模板填充，不做 LLM 写作。
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from decimal import Decimal
from typing import Final, Literal

from fund_agent.fund.analysis.alpha_judge import AlphaJudgment
from fund_agent.fund.analysis.checklist import ChecklistResult
from fund_agent.fund.analysis.consistency_check import ConsistencyCheckResult
from fund_agent.fund.analysis.investor_return import InvestorExperienceResult
from fund_agent.fund.analysis.r_abc import RabcAttribution
from fund_agent.fund.analysis.risk_check import RiskCheckResult, StressTestResult
from fund_agent.fund.audit import ProgrammaticAuditInput
from fund_agent.fund.data_extractor import StructuredFundDataBundle
from fund_agent.fund.extractors.models import EvidenceAnchor, ExtractedField
from fund_agent.fund.template.chapter_blocks import (
    RenderedChapterBlock,
    get_template_chapter_heading,
    split_rendered_chapter_blocks,
)
from fund_agent.fund.template.contracts import get_chapter_contract

TemplateFinalJudgment = Literal["worth_holding", "needs_attention", "suggest_replace"]

_FINAL_JUDGMENT_TEXT: Final[dict[TemplateFinalJudgment, str]] = {
    "worth_holding": "值得持有",
    "needs_attention": "需要关注",
    "suggest_replace": "建议替换",
}
_FORBIDDEN_TERMS: Final[tuple[str, ...]] = ("买入", "卖出", "仓位比例", "收益预测")
_MISSING_TEXT: Final[str] = "未披露"
_INSUFFICIENT_TEXT: Final[str] = "数据不足"
_UNLOCATED_TEXT: Final[str] = "未定位"
_SOURCE_KIND_LABELS: Final[dict[str, str]] = {
    "annual_report": "年报",
    "external_api": "外部数据(external_api)",
    "derived": "计算(derived)",
}


@dataclass(frozen=True, slots=True)
class TemplateRenderInput:
    """8 章模板渲染输入。

    Attributes:
        structured_data: P1 结构化基金数据包。
        rabc_attributions: R=A+B-C 归因结果，用于模板第 2 章和 L1 审计。
        alpha_judgment: 超额收益性质判断，用于模板第 2 章。
        consistency_result: 言行一致性结果，用于模板第 3 章。
        investor_experience: 投资者获得感结果，用于模板第 4 章。
        risk_check_result: 否决项检查结果，用于模板第 6 章。
        stress_test_result: 压力测试结果，用于模板第 6 章。
        checklist_result: 7 问题检查清单结果，用于模板第 7 章和 R1/R2 审计。
        final_judgment: 显式最终判断，只允许值得持有、需要关注、建议替换三类。
        current_stage: 当前阶段与关键变化说明；缺失时模板第 5 章显式写数据不足。
    """

    structured_data: StructuredFundDataBundle
    rabc_attributions: tuple[RabcAttribution, ...]
    alpha_judgment: AlphaJudgment
    consistency_result: ConsistencyCheckResult
    investor_experience: InvestorExperienceResult
    risk_check_result: RiskCheckResult
    stress_test_result: StressTestResult
    checklist_result: ChecklistResult
    final_judgment: TemplateFinalJudgment
    current_stage: str | None = None


@dataclass(frozen=True, slots=True)
class TemplateRenderResult:
    """8 章模板渲染结果。

    Attributes:
        report_markdown: 已渲染的完整 Markdown 报告。
        audit_input: 可直接传给 `run_programmatic_audit` 的程序审计输入。
        evidence_anchors: 报告引用到的去重证据锚点。
        chapter_blocks: 按模板第 0-7 章切分的渲染章节块。
    """

    report_markdown: str
    audit_input: ProgrammaticAuditInput
    evidence_anchors: tuple[EvidenceAnchor, ...]
    chapter_blocks: tuple[RenderedChapterBlock, ...]


def render_template_report(input_data: TemplateRenderInput) -> TemplateRenderResult:
    """渲染基金 8 章 Markdown 报告。

    Args:
        input_data: 模板渲染输入，聚合 P1/P2 结构化结果。

    Returns:
        模板渲染结果，包含 Markdown、程序审计输入和证据锚点。

    Raises:
        ValueError: 当最终判断不在允许集合内，或渲染文本包含禁用投资建议词时抛出。
    """

    _validate_final_judgment(input_data.final_judgment)
    evidence_anchors = _collect_evidence_anchors(input_data)
    chapter_evidence_groups = _collect_chapter_evidence_groups(input_data)
    sections = (
        _render_chapter_0(input_data),
        _render_chapter_1(input_data),
        _render_chapter_2(input_data),
        _render_chapter_3(input_data),
        _render_chapter_4(input_data),
        _render_chapter_5(input_data),
        _render_chapter_6(input_data),
        _render_chapter_7(input_data),
        _render_evidence_section(
            evidence_anchors, input_data.structured_data.report_year, chapter_evidence_groups
        ),
    )
    report_markdown = "\n\n".join(sections).strip() + "\n"
    _validate_report_wording(report_markdown)
    chapter_blocks = split_rendered_chapter_blocks(report_markdown)
    return TemplateRenderResult(
        report_markdown=report_markdown,
        audit_input=ProgrammaticAuditInput(
            report_markdown=report_markdown,
            rabc_attributions=input_data.rabc_attributions,
            checklist_result=input_data.checklist_result,
            final_judgment=input_data.final_judgment,
            chapter_blocks=chapter_blocks,
        ),
        evidence_anchors=evidence_anchors,
        chapter_blocks=chapter_blocks,
    )


def build_programmatic_audit_input(render_result: TemplateRenderResult) -> ProgrammaticAuditInput:
    """从渲染结果提取程序审计输入。

    Args:
        render_result: 模板渲染结果。

    Returns:
        可直接传给 `run_programmatic_audit` 的输入。

    Raises:
        无显式抛出。
    """

    return render_result.audit_input


def _render_chapter_0(input_data: TemplateRenderInput) -> str:
    """渲染模板第 0 章“投资要点概览”。

    Args:
        input_data: 模板渲染输入。

    Returns:
        第 0 章 Markdown。

    Raises:
        无显式抛出。
    """

    identity = input_data.structured_data.basic_identity.value or {}
    fund_name = _value_text(identity, "fund_name")
    fund_code = _value_text(identity, "fund_code", fallback=input_data.structured_data.fund_code)
    fund_type = _value_text(identity, "classified_fund_type")
    judgment_text = _FINAL_JUDGMENT_TEXT[input_data.final_judgment]
    primary_rabc = _primary_rabc(input_data.rabc_attributions)
    net_excess = _ratio_text(primary_rabc.net_excess_return) if primary_rabc else _INSUFFICIENT_TEXT
    content = [
        get_template_chapter_heading(0),
        f"- 基金：{fund_name}（{fund_code}）。",
        f"- 基金类型：{fund_type}，本报告先识别基金类型，再应用对应 preferred_lens。",
        f"- 最终判断：{judgment_text}；检查清单汇总为 {input_data.checklist_result.overall_signal} / {input_data.checklist_result.overall_status}。",
        f"- 当前业绩与运作状态：R=A+B-C 净超额 {net_excess}；超额性质 {input_data.alpha_judgment.nature}。",
        f"- 支撑当前动作的最主要理由：检查清单汇总为 {input_data.checklist_result.overall_signal} / {input_data.checklist_result.overall_status}。",
        f"- 当前最值得盯住的变量：{_INSUFFICIENT_TEXT}，当前未提供独立变量识别输入。",
        f"- 当前最大的风险：{_INSUFFICIENT_TEXT}，当前未提供独立最大风险排序输入。",
        f"- R=A+B-C 净超额：{net_excess}；超额性质：{input_data.alpha_judgment.nature}。",
        f"- 下一步最小验证问题：{input_data.checklist_result.next_minimum_verification}",
        f"- 什么变化会升级、降级或终止当前动作：{_INSUFFICIENT_TEXT}，需要后续跨期证据确认。",
        _evidence_line(input_data.structured_data.basic_identity.anchors),
    ]
    return "\n".join(content)


def _render_chapter_1(input_data: TemplateRenderInput) -> str:
    """渲染模板第 1 章“这只基金到底是什么产品”。

    Args:
        input_data: 模板渲染输入。

    Returns:
        第 1 章 Markdown。

    Raises:
        无显式抛出。
    """

    identity = input_data.structured_data.basic_identity.value or {}
    profile = input_data.structured_data.product_profile.value or {}
    benchmark = input_data.structured_data.benchmark.value or {}
    fee = input_data.structured_data.fee_schedule.value or {}
    anchors = _merge_anchors(
        input_data.structured_data.basic_identity,
        input_data.structured_data.product_profile,
        input_data.structured_data.benchmark,
        input_data.structured_data.fee_schedule,
    )
    content = [
        get_template_chapter_heading(1),
        f"- 基金类型与分类标签：{_value_text(identity, 'classified_fund_type')}；分类依据：{_join_values(identity.get('classification_basis'))}。",
        f"- 投资目标（一句话）：{_value_text(profile, 'investment_objective')}。",
        f"- 投资策略概述：{_value_text(profile, 'investment_strategy')}；投资范围：{_value_text(profile, 'investment_scope')}。",
        f"- 业绩基准及合理性：{_value_text(benchmark, 'benchmark_text')}；合理性当前为 {_INSUFFICIENT_TEXT}。",
        "- 看这类基金最先看什么：先看基金类型、业绩基准、成本底座和 preferred_lens。",
        f"- 会改变产品理解的特别情况：{_INSUFFICIENT_TEXT}，当前输入未提供额外特别情况。",
        f"- 产品本质：{_value_text(profile, 'investment_objective')}；投资范围：{_value_text(profile, 'investment_scope')}。",
        f"- 收益来源假设：围绕基金类别 {_value_text(identity, 'fund_category')} 和业绩基准 {_value_text(benchmark, 'benchmark_text')} 观察。",
        f"- 成本底座：管理费 {_value_text(fee, 'management_fee')}，托管费 {_value_text(fee, 'custody_fee')}。",
        f"- 基金类型识别依据：{_join_values(identity.get('classification_basis'))}。",
        _evidence_line(anchors),
    ]
    return "\n".join(content)


def _render_chapter_2(input_data: TemplateRenderInput) -> str:
    """渲染模板第 2 章“R=A+B-C 收益归因”。

    Args:
        input_data: 模板渲染输入。

    Returns:
        第 2 章 Markdown。

    Raises:
        无显式抛出。
    """

    lines = [
        get_template_chapter_heading(2),
        "- 公式口径：R=基金净值增长率，B=业绩比较基准收益率×股票仓位，A=R-B，C=管理费+托管费+换手率×0.3%。",
    ]
    for attribution in input_data.rabc_attributions:
        lines.append(
            "- "
            f"{attribution.period}：状态 {attribution.status}，"
            f"R {_ratio_text(attribution.total_return_r)}，"
            f"B {_ratio_text(attribution.beta_return_b)}，"
            f"A {_ratio_text(attribution.alpha_return_a)}，"
            f"C {_ratio_text(attribution.explicit_cost_c)}，"
            f"净超额 {_ratio_text(attribution.net_excess_return)}。"
        )
    if not input_data.rabc_attributions:
        lines.append(f"- 归因结果：{_INSUFFICIENT_TEXT}，缺少可审计的 R=A+B-C 输入。")
    primary_rabc = _primary_rabc(input_data.rabc_attributions)
    lines.extend(
        [
            f"- 近 1/3/5 年净值增长率：{_ratio_text(primary_rabc.total_return_r) if primary_rabc else _INSUFFICIENT_TEXT}。",
            f"- 近 1/3/5 年业绩基准收益率：{_ratio_text(primary_rabc.beta_return_b) if primary_rabc else _INSUFFICIENT_TEXT}。",
            f"- 超额收益（A = R - B）及稳定性：{_ratio_text(primary_rabc.alpha_return_a) if primary_rabc else _INSUFFICIENT_TEXT}；稳定性需多期归因确认。",
            f"- 超额收益性质：{input_data.alpha_judgment.nature}；正 Alpha 周期 {input_data.alpha_judgment.positive_alpha_count}/{input_data.alpha_judgment.observation_count}。",
            f"- 成本拆解：管理费、托管费和交易成本合计 {_ratio_text(primary_rabc.explicit_cost_c) if primary_rabc else _INSUFFICIENT_TEXT}。",
            f"- 成本合理性判断：{_INSUFFICIENT_TEXT}，当前未提供同类成本中位数输入。",
            f"- R=A+B-C 综合评估：净超额 {_ratio_text(primary_rabc.net_excess_return) if primary_rabc else _INSUFFICIENT_TEXT}。",
            f"- 判断依据：{_join_values(input_data.alpha_judgment.reasons)}；风险提示：{_join_values(input_data.alpha_judgment.risks)}。",
            _evidence_line(_collect_rabc_anchors(input_data.rabc_attributions)),
        ],
    )
    return "\n".join(lines)


def _render_chapter_3(input_data: TemplateRenderInput) -> str:
    """渲染模板第 3 章“基金经理画像与言行一致性”。

    Args:
        input_data: 模板渲染输入。

    Returns:
        第 3 章 Markdown。

    Raises:
        无显式抛出。
    """

    profile = input_data.structured_data.product_profile.value or {}
    strategy = input_data.structured_data.manager_strategy_text.value or {}
    manager_alignment = input_data.structured_data.manager_alignment.value or {}
    lines = [
        get_template_chapter_heading(3),
        f"- 基金经理基本信息：{_value_text(input_data.structured_data.basic_identity.value or {}, 'fund_manager')}。",
        f"- 宣称的投资策略（§4）：{_value_text(strategy, 'strategy_summary')}。",
        f"- 实际投资行为（§8）：{_value_text(input_data.structured_data.holdings_snapshot.value or {}, 'top_holdings')}。",
        f"- 言行一致性判断：{input_data.consistency_result.overall_signal} / {input_data.consistency_result.overall_status}。",
        f"- 风格稳定性判断：{_INSUFFICIENT_TEXT}，当前需要多期持仓继续验证。",
        f"- 利益一致性判断：{_join_values(manager_alignment.values()) if manager_alignment else _MISSING_TEXT}。",
        f"- 管理人表述：{_value_text(strategy, 'strategy_summary')}；产品风格定位：{_value_text(profile, 'style_positioning')}。",
        f"- 利益一致性原始披露：{_join_values(manager_alignment.values()) if manager_alignment else _MISSING_TEXT}。",
        f"- 言行一致性汇总：{input_data.consistency_result.overall_signal} / {input_data.consistency_result.overall_status}。",
    ]
    for dimension in input_data.consistency_result.dimensions:
        lines.append(
            "- "
            f"{dimension.dimension}：{dimension.signal} / {dimension.status}，"
            f"宣称={_nullable_text(dimension.declared)}，实际={_nullable_text(dimension.actual)}，原因={dimension.reason}"
        )
    lines.append(_evidence_line(_collect_consistency_anchors(input_data)))
    return "\n".join(lines)


def _render_chapter_4(input_data: TemplateRenderInput) -> str:
    """渲染模板第 4 章“投资者获得感”。

    Args:
        input_data: 模板渲染输入。

    Returns:
        第 4 章 Markdown。

    Raises:
        无显式抛出。
    """

    behavior_gap = input_data.investor_experience.behavior_gap
    fund_flow = input_data.investor_experience.fund_flow
    lines = [
        get_template_chapter_heading(4),
        f"- 基金产品收益 vs 投资者实际收益：产品收益 {_ratio_text(behavior_gap.product_return)}，投资者实际收益 {_ratio_text(behavior_gap.investor_return)}。",
        f"- 盈利投资者占比：{_INSUFFICIENT_TEXT}，当前公开输入未提供该字段。",
        f"- 行为损益估算：{_ratio_text(behavior_gap.behavior_gap)}。",
        f"- 份额变动趋势：期初份额 {_decimal_text(fund_flow.beginning_share)}，期末份额 {_decimal_text(fund_flow.ending_share)}，净变动 {_decimal_text(fund_flow.net_change)}。",
        f"- 获得感状态：{input_data.investor_experience.status}。",
        f"- 行为损益：产品收益 {_ratio_text(behavior_gap.product_return)}，投资者实际收益 {_ratio_text(behavior_gap.investor_return)}，差额 {_ratio_text(behavior_gap.behavior_gap)}。",
        f"- 资金流向：{fund_flow.signal}；期初份额 {_decimal_text(fund_flow.beginning_share)}，期末份额 {_decimal_text(fund_flow.ending_share)}，净变动 {_decimal_text(fund_flow.net_change)}。",
        f"- 依据说明：{_sentence_body(_join_values(input_data.investor_experience.reasons))}。",
        _evidence_line((*behavior_gap.anchors, *fund_flow.anchors)),
    ]
    return "\n".join(lines)


def _render_chapter_5(input_data: TemplateRenderInput) -> str:
    """渲染模板第 5 章“当前阶段与关键变化”。

    Args:
        input_data: 模板渲染输入。

    Returns:
        第 5 章 Markdown。

    Raises:
        无显式抛出。
    """

    nav_count = len(input_data.structured_data.nav_data.records)
    stage_text = (
        input_data.current_stage.strip()
        if input_data.current_stage and input_data.current_stage.strip()
        else _INSUFFICIENT_TEXT
    )
    lines = [
        get_template_chapter_heading(5),
        f"- 过去一年最关键的变化：{stage_text}。",
        f"- 基金当前所处阶段：{stage_text}。",
        f"- 变化是否改变前文判断：{_INSUFFICIENT_TEXT}，当前需要跨期年报对比确认。",
        "- 接下来最该跟踪的变量：继续补充多期年报与同口径净值序列。",
        f"- 当前阶段：{stage_text}。",
        f"- 关键变化输入：净值记录 {nav_count} 条；跨期年报对比结论当前为 {_INSUFFICIENT_TEXT}。",
        "- 需要补证：若要判断阶段变化，应继续补充多期年报与同口径净值序列。",
        _evidence_line(_merge_anchors(input_data.structured_data.nav_benchmark_performance)),
    ]
    return "\n".join(lines)


def _render_chapter_6(input_data: TemplateRenderInput) -> str:
    """渲染模板第 6 章“核心风险与否决项”。

    Args:
        input_data: 模板渲染输入。

    Returns:
        第 6 章 Markdown。

    Raises:
        无显式抛出。
    """

    lines = [
        get_template_chapter_heading(6),
        f"- 最关键的风险或否决项：{input_data.risk_check_result.overall_status}。",
        f"- 为什么足以改变结论：红灯否决 {len(input_data.risk_check_result.veto_items)} 项，跟踪/补证 {len(input_data.risk_check_result.watch_items)} 项。",
        f"- 否决 vs 跟踪判断：{input_data.risk_check_result.overall_status}。",
        f"- 下一轮先验证什么：{input_data.risk_check_result.next_minimum_verification}",
        f"- 否决项汇总：{input_data.risk_check_result.overall_status}；红灯否决 {len(input_data.risk_check_result.veto_items)} 项，跟踪/补证 {len(input_data.risk_check_result.watch_items)} 项。",
    ]
    for item in input_data.risk_check_result.items:
        lines.append(
            "- "
            f"{item.code}：{item.status}，当前值={_nullable_text(item.current_value)}，阈值={item.threshold}，原因={item.reason}"
        )
    lines.extend(
        [
            f"- 压力测试：基金类型 {input_data.stress_test_result.fund_type}，投入金额 {_decimal_text(input_data.stress_test_result.investment_amount)}，最大可承受亏损 {_ratio_text(input_data.stress_test_result.max_tolerable_loss_rate)}。",
            f"- 最差场景：{input_data.stress_test_result.worst_scenario.code}，浮亏 {_decimal_text(input_data.stress_test_result.worst_scenario.floating_loss_amount)}，承受状态 {input_data.stress_test_result.worst_scenario.capacity_status}。",
            f"- 下一步最小验证问题：{input_data.risk_check_result.next_minimum_verification}",
            _evidence_line(_collect_risk_anchors(input_data)),
        ],
    )
    return "\n".join(lines)


def _render_chapter_7(input_data: TemplateRenderInput) -> str:
    """渲染模板第 7 章“是否值得持有——最终判断”。

    Args:
        input_data: 模板渲染输入。

    Returns:
        第 7 章 Markdown。

    Raises:
        无显式抛出。
    """

    lines = [
        get_template_chapter_heading(7),
        f"- 最终判断：{_FINAL_JUDGMENT_TEXT[input_data.final_judgment]}。",
        f"- 支撑判断的核心依据：检查清单汇总为 {input_data.checklist_result.overall_signal} / {input_data.checklist_result.overall_status}。",
        f"- 当前最容易看错的地方：{_INSUFFICIENT_TEXT}，需要继续核对证据锚点和缺失字段。",
        f"- 下一轮最小验证计划：{input_data.checklist_result.next_minimum_verification}",
        f"- 危级/降级阈值：{_INSUFFICIENT_TEXT}，当前模板保留该阈值字段待后续补证。",
        "- 判断边界：本结论只在公开披露信息和显式输入范围内成立，不预测未来收益，不给出交易或配置指令。",
        f"- 检查清单汇总：{input_data.checklist_result.overall_signal} / {input_data.checklist_result.overall_status}。",
    ]
    for item in input_data.checklist_result.items:
        lines.append(f"- {item.question} {item.signal} / {item.status}：{item.reason}")
    lines.append(f"- 下一步最小验证问题：{input_data.checklist_result.next_minimum_verification}")
    lines.append(_evidence_line(_collect_checklist_anchors(input_data.checklist_result)))
    return "\n".join(lines)


def _render_evidence_section(
    anchors: tuple[EvidenceAnchor, ...],
    report_year: int,
    chapter_evidence_groups: tuple[tuple[EvidenceAnchor, ...], ...],
) -> str:
    """渲染证据与出处附录。

    Args:
        anchors: 去重证据锚点。
        report_year: 报告年份，用于无锚点时仍输出可审计年份。
        chapter_evidence_groups: 按模板第 0-7 章分组的证据锚点，用于显式标注缺证章节。

    Returns:
        证据与出处 Markdown。

    Raises:
        无显式抛出。
    """

    lines = ["## 证据与出处"]
    for index, anchor in enumerate(anchors, start=1):
        lines.append(f"- [{index}] {_anchor_reference(anchor)}")
    for chapter_index, chapter_anchors in enumerate(chapter_evidence_groups):
        if chapter_anchors:
            continue
        lines.append(
            f"- [M{chapter_index}] {_missing_anchor_reference(report_year, chapter_index)}"
        )
    return "\n".join(lines)


def _evidence_line(anchors: tuple[EvidenceAnchor, ...]) -> str:
    """渲染章节内证据行。

    Args:
        anchors: 章节关联证据锚点。

    Returns:
        项目统一格式的证据行。

    Raises:
        无显式抛出。
    """

    if not anchors:
        return f"> 📎 证据：{_INSUFFICIENT_TEXT}，当前章节未携带证据锚点"
    return f"> 📎 证据：{_body_anchor_reference(anchors[0])}"


def _body_anchor_reference(anchor: EvidenceAnchor) -> str:
    """渲染正文证据锚点引用。

    Args:
        anchor: 证据锚点。

    Returns:
        正文证据锚点文本；年报来源必须包含年份和章节，非年报来源必须显式标注来源类型。

    Raises:
        无显式抛出。
    """

    description = _anchor_description(anchor)
    page_part = _page_metadata_text(anchor.page_number)
    if anchor.source_kind == "annual_report":
        year = anchor.document_year if anchor.document_year is not None else "未知年份"
        return f"年报{year}§{_section_text(anchor.section_id)}{page_part} {description}"
    source_label = _source_kind_label(anchor.source_kind)
    location = _non_annual_location_text(anchor)
    return f"{source_label}{location}{page_part} {description}"


def _anchor_reference(anchor: EvidenceAnchor) -> str:
    """渲染附录证据锚点引用。

    Args:
        anchor: 证据锚点。

    Returns:
        附录格式证据引用；缺行定位时仍保留年份和章节。

    Raises:
        无显式抛出。
    """

    if anchor.source_kind != "annual_report":
        return _non_annual_anchor_reference(anchor)
    year = anchor.document_year if anchor.document_year is not None else "未知年份"
    section = _section_text(anchor.section_id)
    table_part = f"表{anchor.table_id or _UNLOCATED_TEXT}"
    row_part = f"行{anchor.row_locator or _UNLOCATED_TEXT}"
    page_part = _page_metadata_text(anchor.page_number)
    note_part = f"：{anchor.note}" if anchor.note else ""
    return f"年报{year}§{section}{table_part}{row_part}{page_part}{note_part}"


def _non_annual_anchor_reference(anchor: EvidenceAnchor) -> str:
    """渲染非年报证据锚点引用。

    Args:
        anchor: 非年报证据锚点。

    Returns:
        附录格式的非年报证据引用，显式保留来源类型。

    Raises:
        无显式抛出。
    """

    source_label = _source_kind_label(anchor.source_kind)
    location = _non_annual_location_text(anchor)
    page_part = _page_metadata_text(anchor.page_number)
    note_part = f"：{anchor.note}" if anchor.note else ""
    return f"{source_label}{location}{page_part}{note_part}"


def _missing_anchor_reference(report_year: int, chapter_index: int) -> str:
    """渲染缺失证据锚点的附录条目。

    Args:
        report_year: 报告年份。
        chapter_index: 模板章节编号。

    Returns:
        附录中的显式缺证条目。

    Raises:
        无显式抛出。
    """

    chapter_title = get_chapter_contract(chapter_index).title
    return (
        f"年报{report_year}§{_UNLOCATED_TEXT}表{_UNLOCATED_TEXT}行{_UNLOCATED_TEXT}："
        f"{_INSUFFICIENT_TEXT}，模板第{chapter_index}章《{chapter_title}》当前输入未携带证据锚点。"
    )


def _source_kind_label(source_kind: str) -> str:
    """渲染证据来源类型标签。

    Args:
        source_kind: 证据来源类型。

    Returns:
        人类可读且保留原始枚举的来源标签。

    Raises:
        无显式抛出。
    """

    return _SOURCE_KIND_LABELS.get(source_kind, f"未知来源({source_kind})")


def _non_annual_location_text(anchor: EvidenceAnchor) -> str:
    """渲染非年报锚点位置文本。

    Args:
        anchor: 非年报证据锚点。

    Returns:
        非年报位置文本，优先保留年份、章节、表格和行定位。

    Raises:
        无显式抛出。
    """

    parts: list[str] = []
    if anchor.document_year is not None:
        parts.append(f"年份{anchor.document_year}")
    if anchor.section_id:
        parts.append(f"§{_section_text(anchor.section_id)}")
    if anchor.table_id:
        parts.append(f"表{anchor.table_id}")
    if anchor.row_locator:
        parts.append(f"行{anchor.row_locator}")
    if not parts:
        return f"位置{_UNLOCATED_TEXT}"
    return "".join(parts)


def _page_metadata_text(page_number: int | None) -> str:
    """渲染页码位置元数据。

    Args:
        page_number: 页码。

    Returns:
        页码元数据文本；缺失时返回空字符串。

    Raises:
        无显式抛出。
    """

    if page_number is None:
        return ""
    return f"（第{page_number}页）"


def _anchor_description(anchor: EvidenceAnchor) -> str:
    """选择正文证据描述文本。

    Args:
        anchor: 证据锚点。

    Returns:
        正文证据描述，优先使用行定位，其次使用附注。

    Raises:
        无显式抛出。
    """

    return anchor.row_locator or anchor.note or "结构化字段"


def _section_text(section_id: str | None) -> str:
    """标准化章节编号文本。

    Args:
        section_id: 年报章节编号，可能为空。

    Returns:
        不重复 `§` 的章节文本。

    Raises:
        无显式抛出。
    """

    if not section_id:
        return "未定位"
    return section_id[1:] if section_id.startswith("§") else section_id


def _collect_evidence_anchors(input_data: TemplateRenderInput) -> tuple[EvidenceAnchor, ...]:
    """汇总报告中所有证据锚点。

    Args:
        input_data: 模板渲染输入。

    Returns:
        去重后的证据锚点。

    Raises:
        无显式抛出。
    """

    return _dedupe_anchors(
        (
            *_merge_anchors(
                input_data.structured_data.basic_identity,
                input_data.structured_data.product_profile,
                input_data.structured_data.benchmark,
                input_data.structured_data.fee_schedule,
                input_data.structured_data.turnover_rate,
                input_data.structured_data.nav_benchmark_performance,
                input_data.structured_data.investor_return,
                input_data.structured_data.share_change,
                input_data.structured_data.manager_alignment,
                input_data.structured_data.manager_strategy_text,
                input_data.structured_data.holdings_snapshot,
                input_data.structured_data.holder_structure,
            ),
            *_collect_rabc_anchors(input_data.rabc_attributions),
            *_collect_consistency_anchors(input_data),
            *_collect_risk_anchors(input_data),
            *_collect_checklist_anchors(input_data.checklist_result),
            *input_data.stress_test_result.anchors,
        ),
    )


def _collect_chapter_evidence_groups(
    input_data: TemplateRenderInput,
) -> tuple[tuple[EvidenceAnchor, ...], ...]:
    """按模板章节收集证据锚点。

    Args:
        input_data: 模板渲染输入。

    Returns:
        第 0-7 章各自使用的证据锚点分组。

    Raises:
        无显式抛出。
    """

    behavior_gap = input_data.investor_experience.behavior_gap
    fund_flow = input_data.investor_experience.fund_flow
    return (
        _dedupe_anchors(input_data.structured_data.basic_identity.anchors),
        _merge_anchors(
            input_data.structured_data.basic_identity,
            input_data.structured_data.product_profile,
            input_data.structured_data.benchmark,
            input_data.structured_data.fee_schedule,
        ),
        _collect_rabc_anchors(input_data.rabc_attributions),
        _collect_consistency_anchors(input_data),
        _dedupe_anchors((*behavior_gap.anchors, *fund_flow.anchors)),
        _merge_anchors(input_data.structured_data.nav_benchmark_performance),
        _collect_risk_anchors(input_data),
        _collect_checklist_anchors(input_data.checklist_result),
    )


def _collect_rabc_anchors(attributions: tuple[RabcAttribution, ...]) -> tuple[EvidenceAnchor, ...]:
    """汇总 R=A+B-C 证据锚点。

    Args:
        attributions: R=A+B-C 归因结果。

    Returns:
        去重证据锚点。

    Raises:
        无显式抛出。
    """

    return _dedupe_anchors(tuple(anchor for item in attributions for anchor in item.anchors))


def _collect_consistency_anchors(input_data: TemplateRenderInput) -> tuple[EvidenceAnchor, ...]:
    """汇总言行一致性证据锚点。

    Args:
        input_data: 模板渲染输入。

    Returns:
        去重证据锚点。

    Raises:
        无显式抛出。
    """

    anchors = tuple(
        anchor for item in input_data.consistency_result.dimensions for anchor in item.anchors
    )
    return _dedupe_anchors((*anchors, *input_data.structured_data.manager_alignment.anchors))


def _collect_risk_anchors(input_data: TemplateRenderInput) -> tuple[EvidenceAnchor, ...]:
    """汇总风险与压力测试证据锚点。

    Args:
        input_data: 模板渲染输入。

    Returns:
        去重证据锚点。

    Raises:
        无显式抛出。
    """

    risk_anchors = tuple(
        anchor for item in input_data.risk_check_result.items for anchor in item.anchors
    )
    return _dedupe_anchors((*risk_anchors, *input_data.stress_test_result.anchors))


def _collect_checklist_anchors(checklist_result: ChecklistResult) -> tuple[EvidenceAnchor, ...]:
    """汇总检查清单证据锚点。

    Args:
        checklist_result: 检查清单结果。

    Returns:
        去重证据锚点。

    Raises:
        无显式抛出。
    """

    return _dedupe_anchors(
        tuple(anchor for item in checklist_result.items for anchor in item.anchors)
    )


def _merge_anchors(*fields: ExtractedField[dict[str, object]]) -> tuple[EvidenceAnchor, ...]:
    """合并抽取字段证据锚点。

    Args:
        fields: P1 抽取字段。

    Returns:
        去重证据锚点。

    Raises:
        无显式抛出。
    """

    return _dedupe_anchors(tuple(anchor for field in fields for anchor in field.anchors))


def _dedupe_anchors(anchors: tuple[EvidenceAnchor, ...]) -> tuple[EvidenceAnchor, ...]:
    """按 dataclass 值去重证据锚点。

    Args:
        anchors: 原始证据锚点。

    Returns:
        稳定顺序去重后的证据锚点。

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


def _primary_rabc(attributions: tuple[RabcAttribution, ...]) -> RabcAttribution | None:
    """选择概览展示用 R=A+B-C 归因结果。

    Args:
        attributions: R=A+B-C 归因结果。

    Returns:
        优先返回首个已计算结果，否则返回首个结果或 `None`。

    Raises:
        无显式抛出。
    """

    for attribution in attributions:
        if attribution.status == "computed":
            return attribution
    return attributions[0] if attributions else None


def _ratio_text(value: Decimal | None) -> str:
    """把小数比例渲染为百分比文本。

    Args:
        value: 小数比例。

    Returns:
        百分比文本；缺失时返回“数据不足”。

    Raises:
        无显式抛出。
    """

    if value is None:
        return _INSUFFICIENT_TEXT
    return f"{(value * Decimal('100')).quantize(Decimal('0.01'))}%"


def _decimal_text(value: Decimal | None) -> str:
    """把 Decimal 数值渲染为文本。

    Args:
        value: Decimal 数值。

    Returns:
        数值文本；缺失时返回“数据不足”。

    Raises:
        无显式抛出。
    """

    if value is None:
        return _INSUFFICIENT_TEXT
    return str(value)


def _value_text(values: dict[str, object], key: str, *, fallback: object | None = None) -> str:
    """读取字典字段并处理缺失。

    Args:
        values: 字段字典。
        key: 字段名。
        fallback: 缺失时的备用值。

    Returns:
        字段文本；缺失时返回“未披露”。

    Raises:
        无显式抛出。
    """

    value = values.get(key, fallback)
    if value is None or str(value).strip() == "":
        return _MISSING_TEXT
    return str(value)


def _nullable_text(value: object | None) -> str:
    """渲染可空文本。

    Args:
        value: 任意可空值。

    Returns:
        字符串；缺失时返回“数据不足”。

    Raises:
        无显式抛出。
    """

    if value is None or str(value).strip() == "":
        return _INSUFFICIENT_TEXT
    return str(value)


def _join_values(values: object) -> str:
    """把多值字段渲染为中文分号连接文本。

    Args:
        values: 任意值。

    Returns:
        文本；空值返回“数据不足”。

    Raises:
        无显式抛出。
    """

    if values is None:
        return _INSUFFICIENT_TEXT
    if isinstance(values, str):
        return values if values.strip() else _INSUFFICIENT_TEXT
    if isinstance(values, Mapping):
        values = values.values()
    if isinstance(values, Iterable):
        non_empty = tuple(str(value) for value in values if str(value).strip())
        return "；".join(non_empty) if non_empty else _INSUFFICIENT_TEXT
    return str(values)


def _sentence_body(text: str) -> str:
    """渲染可追加中文句号的句身文本。

    Args:
        text: 已渲染的文本。

    Returns:
        去除尾部句末标点后的文本；空值返回“数据不足”。

    Raises:
        无显式抛出。
    """

    stripped_text = text.strip()
    if not stripped_text:
        return _INSUFFICIENT_TEXT
    return stripped_text.rstrip("。！？；;,.，")


def _validate_final_judgment(final_judgment: TemplateFinalJudgment) -> None:
    """校验最终判断是否落在允许集合内。

    Args:
        final_judgment: 最终判断。

    Returns:
        无返回值。

    Raises:
        ValueError: 当最终判断不在允许集合内时抛出。
    """

    if final_judgment not in _FINAL_JUDGMENT_TEXT:
        raise ValueError("final_judgment 只能是 worth_holding / needs_attention / suggest_replace")


def _validate_report_wording(report_markdown: str) -> None:
    """校验报告未包含禁用交易建议措辞。

    Args:
        report_markdown: 已渲染 Markdown。

    Returns:
        无返回值。

    Raises:
        ValueError: 当报告包含禁用措辞时抛出。
    """

    forbidden_hits = tuple(term for term in _FORBIDDEN_TERMS if term in report_markdown)
    if forbidden_hits:
        raise ValueError(f"报告包含禁用投资建议措辞：{'、'.join(forbidden_hits)}")
