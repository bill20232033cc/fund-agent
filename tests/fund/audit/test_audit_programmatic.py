"""程序审计测试。"""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal

import pytest

from fund_agent.fund.analysis import ChecklistItem, ChecklistResult, RabcAttribution
from fund_agent.fund.audit.contract_rules import (
    ContractAuditCoverageManifest,
    ContractMustAnswerCoverageRule,
    ContractRequiredItemRule,
    ProgrammaticContractRules,
    load_contract_audit_coverage_manifest,
    load_programmatic_contract_rules,
    validate_contract_audit_coverage_manifest,
    validate_programmatic_contract_rules,
)
from fund_agent.fund.template.contracts import load_template_contract_manifest
from fund_agent.fund.audit import ProgrammaticAuditInput, run_programmatic_audit
from fund_agent.fund.template import render_template_report, split_rendered_chapter_blocks
from tests.fund.template.test_renderer import _render_input


def _complete_report() -> str:
    """构造完整报告 Markdown。

    Args:
        无。

    Returns:
        包含 8 章和证据锚点的报告。

    Raises:
        无显式抛出。
    """

    return "\n\n".join(
        [
            "# 投资要点概览\n这是一段超过十个字符的内容。",
            "# 这只基金到底是什么产品\n这是一段超过十个字符的内容。",
            "# R=A+B-C 收益归因\n这是一段超过十个字符的内容。",
            "# 基金经理画像与言行一致性\n这是一段超过十个字符的内容。",
            "# 投资者获得感\n这是一段超过十个字符的内容。",
            "# 当前阶段与关键变化\n这是一段超过十个字符的内容。",
            "# 核心风险与否决项\n这是一段超过十个字符的内容。",
            "# 是否值得持有\n这是一段超过十个字符的内容。",
            "## 证据与出处\n年报2024§3表2行5。",
        ],
    )


def _rabc() -> RabcAttribution:
    """构造闭合的 R=A+B-C 归因结果。

    Args:
        无。

    Returns:
        R=A+B-C 归因结果。

    Raises:
        无显式抛出。
    """

    return RabcAttribution(
        period="2024",
        status="computed",
        total_return_r=Decimal("0.10"),
        beta_return_b=Decimal("0.04"),
        alpha_return_a=Decimal("0.06"),
        explicit_cost_c=Decimal("0.02"),
        net_excess_return=Decimal("0.04"),
        turnover_cost=Decimal("0.003"),
        anchors=(),
        note=None,
    )


def _checklist(signal: str = "green") -> ChecklistResult:
    """构造检查清单结果。

    Args:
        signal: 单题和汇总信号。

    Returns:
        检查清单结果。

    Raises:
        无显式抛出。
    """

    status_by_signal = {
        "green": "pass",
        "yellow": "watch",
        "red": "block",
        "gray": "insufficient_data",
    }
    items = tuple(
        ChecklistItem(
            code=code,  # type: ignore[arg-type]
            question=code,
            signal=signal,  # type: ignore[arg-type]
            status=status_by_signal[signal],  # type: ignore[arg-type]
            anchors=(),
            reason="fixture",
        )
        for code in (
            "net_excess_covers_cost",
            "manager_alignment",
            "investor_return",
            "consistency",
            "survival",
            "valuation",
            "money_horizon",
        )
    )
    return ChecklistResult(
        items=items,
        overall_signal=signal,  # type: ignore[arg-type]
        overall_status=status_by_signal[signal],  # type: ignore[arg-type]
        red_items=items if signal == "red" else (),
        yellow_items=items if signal == "yellow" else (),
        gray_items=items if signal == "gray" else (),
        next_minimum_verification="fixture",
    )


def _rendered_audit_input(
    *,
    report_markdown: str | None = None,
    use_explicit_blocks: bool = True,
) -> ProgrammaticAuditInput:
    """构造基于真实模板渲染结果的审计输入。

    Args:
        report_markdown: 覆盖使用的报告 Markdown。
        use_explicit_blocks: 是否显式传入渲染章节块。

    Returns:
        程序审计输入。

    Raises:
        ValueError: 覆盖报告无法切分章节时由 splitter 抛出。
    """

    render_result = render_template_report(_render_input())
    markdown = report_markdown if report_markdown is not None else render_result.report_markdown
    chapter_blocks = (
        split_rendered_chapter_blocks(markdown)
        if report_markdown is not None and use_explicit_blocks
        else render_result.chapter_blocks
        if use_explicit_blocks
        else ()
    )
    return ProgrammaticAuditInput(
        report_markdown=markdown,
        rabc_attributions=render_result.audit_input.rabc_attributions,
        checklist_result=render_result.audit_input.checklist_result,
        final_judgment=render_result.audit_input.final_judgment,
        chapter_blocks=chapter_blocks,
    )


def test_run_programmatic_audit_passes_complete_inputs() -> None:
    """验证完整输入通过 P1/P2/P3/C2/L1/R1/R2 审计。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当完整输入未通过审计时抛出。
    """

    render_result = render_template_report(_render_input())
    result = run_programmatic_audit(
        ProgrammaticAuditInput(
            report_markdown=render_result.report_markdown,
            rabc_attributions=(_rabc(),),
            checklist_result=_checklist("green"),
            final_judgment="worth_holding",
            chapter_blocks=render_result.chapter_blocks,
        ),
    )

    assert result.passed
    assert not result.issues
    assert result.checked_rules == ("P1", "P2", "P3", "C2", "L1", "R1", "R2")


def test_run_programmatic_audit_splits_report_when_chapter_blocks_absent() -> None:
    """验证未显式传入章节块时审计可从 Markdown fallback 切分。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 fallback 切分未通过完整审计时抛出。
    """

    result = run_programmatic_audit(_rendered_audit_input(use_explicit_blocks=False))

    assert result.passed
    assert result.issues == ()


def test_run_programmatic_audit_reports_p1_when_splitter_fallback_fails() -> None:
    """验证 fallback 切分失败时审计记录 P1 而不是抛异常。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当非法 Markdown 未触发 P1 时抛出。
    """

    render_result = render_template_report(_render_input())
    chapter_2 = render_result.chapter_blocks[2].markdown
    broken_markdown = render_result.report_markdown.replace(
        f"\n\n{chapter_2}",
        f"\n\n# 非法标题\n\nbody\n\n{chapter_2}",
        1,
    )

    result = run_programmatic_audit(
        _rendered_audit_input(report_markdown=broken_markdown, use_explicit_blocks=False)
    )

    assert not result.passed
    assert any(issue.code == "P1" and "无法按 CHAPTER_CONTRACT 切分" in issue.message for issue in result.issues)


def test_run_programmatic_audit_detects_missing_required_output_item_marker() -> None:
    """验证 C2 能检测 required_output_items marker 缺失。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当缺失 required item 未触发 C2 时抛出。
    """

    render_result = render_template_report(_render_input())
    broken_markdown = render_result.report_markdown.replace(
        "- 盈利投资者占比：数据不足，当前公开输入未提供该字段。\n",
        "",
        1,
    )

    result = run_programmatic_audit(_rendered_audit_input(report_markdown=broken_markdown))

    assert not result.passed
    assert any(
        issue.code == "C2" and "盈利投资者占比" in issue.message
        for issue in result.issues
    )


def test_run_programmatic_audit_detects_forbidden_contract_marker() -> None:
    """验证 C2 能检测 must_not_cover 确定性禁止 marker。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当禁止 marker 未触发 C2 时抛出。
    """

    render_result = render_template_report(_render_input())
    chapter_7 = render_result.chapter_blocks[7].markdown
    broken_chapter_7 = chapter_7.replace(
        "- 最终判断：值得持有。",
        "- 最终判断：值得持有。\n- 买入金额：fixture。",
        1,
    )
    broken_markdown = render_result.report_markdown.replace(chapter_7, broken_chapter_7, 1)

    result = run_programmatic_audit(_rendered_audit_input(report_markdown=broken_markdown))

    assert not result.passed
    assert any(issue.code == "C2" and "买入金额" in issue.message for issue in result.issues)


def test_run_programmatic_audit_detects_malformed_explicit_chapter_blocks() -> None:
    """验证 C2 能检测显式传入的畸形章节块元数据。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当畸形章节块未触发 C2 时抛出。
    """

    render_result = render_template_report(_render_input())
    broken_heading_block = replace(render_result.chapter_blocks[0], heading="# 0. 错误标题")
    result = run_programmatic_audit(
        ProgrammaticAuditInput(
            report_markdown=render_result.report_markdown,
            rabc_attributions=render_result.audit_input.rabc_attributions,
            checklist_result=render_result.audit_input.checklist_result,
            final_judgment=render_result.audit_input.final_judgment,
            chapter_blocks=(broken_heading_block, *render_result.chapter_blocks[1:]),
        )
    )

    assert not result.passed
    assert any(issue.code == "C2" and "Markdown 标题" in issue.message for issue in result.issues)

    incomplete_result = run_programmatic_audit(
        ProgrammaticAuditInput(
            report_markdown=render_result.report_markdown,
            rabc_attributions=render_result.audit_input.rabc_attributions,
            checklist_result=render_result.audit_input.checklist_result,
            final_judgment=render_result.audit_input.final_judgment,
            chapter_blocks=render_result.chapter_blocks[:-1],
        )
    )

    assert not incomplete_result.passed
    assert any(issue.code == "C2" and "0..7" in issue.message for issue in incomplete_result.issues)


def test_run_programmatic_audit_detects_missing_chapter_evidence_line() -> None:
    """验证 P3 能检测单章证据行缺失。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当单章证据行缺失未触发 P3 时抛出。
    """

    render_result = render_template_report(_render_input())
    broken_markdown = render_result.report_markdown.replace(
        "> 📎 证据：年报2024§3 nav_benchmark_performance\n\n# 6.",
        "\n\n# 6.",
        1,
    )

    result = run_programmatic_audit(_rendered_audit_input(report_markdown=broken_markdown))

    assert not result.passed
    assert any(issue.code == "P3" and "第5章" in issue.message for issue in result.issues)


def test_programmatic_contract_rules_cover_manifest_and_fail_closed_for_invalid_rule() -> None:
    """验证程序化契约规则覆盖 manifest 并对非法条目 fail closed。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当规则覆盖不完整或非法规则未被拒绝时抛出。
    """

    rules = load_programmatic_contract_rules()
    validate_programmatic_contract_rules(rules)

    broken_rules = ProgrammaticContractRules(
        required_items=(
            *rules.required_items,
            ContractRequiredItemRule(0, "不存在的 required item", ("fixture",)),
        ),
        forbidden_contents=rules.forbidden_contents,
    )
    with pytest.raises(ValueError, match="未匹配 manifest"):
        validate_programmatic_contract_rules(broken_rules)


def test_contract_audit_coverage_manifest_covers_every_must_answer() -> None:
    """验证 must_answer 审计覆盖清单完整覆盖模板问题。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当覆盖清单缺失、重复或分类错误时抛出。
    """

    coverage_manifest = load_contract_audit_coverage_manifest()
    template_manifest = load_template_contract_manifest()
    manifest_questions = {
        (chapter.chapter_id, question)
        for chapter in template_manifest.chapters
        for question in chapter.must_answer
    }
    coverage_questions = {
        (rule.chapter_id, rule.question_text)
        for rule in coverage_manifest.must_answer_coverages
    }

    assert coverage_questions == manifest_questions
    assert len(coverage_manifest.must_answer_coverages) == 47
    assert sum(
        1
        for rule in coverage_manifest.must_answer_coverages
        if rule.coverage_kind == "narrative_guidance"
    ) == 2
    assert any(
        rule.chapter_id == 6
        and rule.question_text == "压力测试结论是什么。"
        and rule.coverage_kind == "structured_data_availability"
        for rule in coverage_manifest.must_answer_coverages
    )


def test_contract_audit_coverage_manifest_fails_closed_for_missing_rule() -> None:
    """验证缺失 must_answer 覆盖规则会 fail closed。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当缺失覆盖未被拒绝时抛出。
    """

    coverage_manifest = load_contract_audit_coverage_manifest()
    broken_manifest = ContractAuditCoverageManifest(
        must_answer_coverages=coverage_manifest.must_answer_coverages[:-1],
    )

    with pytest.raises(ValueError, match="must_answer 未被覆盖规则覆盖"):
        validate_contract_audit_coverage_manifest(broken_manifest)


def test_contract_audit_coverage_manifest_fails_closed_for_duplicate_rule() -> None:
    """验证重复 must_answer 覆盖规则会 fail closed。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当重复覆盖未被拒绝时抛出。
    """

    coverage_manifest = load_contract_audit_coverage_manifest()
    first_rule = coverage_manifest.must_answer_coverages[0]
    broken_manifest = ContractAuditCoverageManifest(
        must_answer_coverages=(
            first_rule,
            *coverage_manifest.must_answer_coverages,
        ),
    )

    with pytest.raises(ValueError, match="must_answer 覆盖规则重复"):
        validate_contract_audit_coverage_manifest(broken_manifest)


def test_contract_audit_coverage_manifest_fails_closed_for_unknown_required_item() -> None:
    """验证 must_answer 覆盖引用未知 required item 会 fail closed。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当未知 required item 未被拒绝时抛出。
    """

    coverage_manifest = load_contract_audit_coverage_manifest()
    first_rule = coverage_manifest.must_answer_coverages[0]
    broken_rule = replace(first_rule, required_item_texts=("不存在的 required item",))
    broken_manifest = ContractAuditCoverageManifest(
        must_answer_coverages=(
            broken_rule,
            *coverage_manifest.must_answer_coverages[1:],
        ),
    )

    with pytest.raises(ValueError, match="引用未知 required item"):
        validate_contract_audit_coverage_manifest(broken_manifest)


def test_contract_audit_coverage_manifest_fails_closed_for_empty_programmatic_marker() -> None:
    """验证 programmatic_marker 覆盖类型必须声明 marker。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当空 marker 未被拒绝时抛出。
    """

    coverage_manifest = load_contract_audit_coverage_manifest()
    first_rule = coverage_manifest.must_answer_coverages[0]
    broken_rule = replace(
        first_rule,
        coverage_kind="programmatic_marker",
        required_item_texts=(),
        markers_any=(),
    )
    broken_manifest = ContractAuditCoverageManifest(
        must_answer_coverages=(
            broken_rule,
            *coverage_manifest.must_answer_coverages[1:],
        ),
    )

    with pytest.raises(ValueError, match="programmatic_marker 必须声明 marker"):
        validate_contract_audit_coverage_manifest(broken_manifest)


def test_contract_audit_coverage_manifest_fails_closed_for_non_programmatic_markers() -> None:
    """验证非程序化 must_answer 覆盖不能声明 marker。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当非程序化 marker 未被拒绝时抛出。
    """

    coverage_manifest = load_contract_audit_coverage_manifest()
    narrative_rule_index, narrative_rule = next(
        (index, rule)
        for index, rule in enumerate(coverage_manifest.must_answer_coverages)
        if rule.coverage_kind == "narrative_guidance"
    )
    broken_rule = replace(narrative_rule, markers_any=("为什么偏偏是现在：",))
    broken_rules = (
        *coverage_manifest.must_answer_coverages[:narrative_rule_index],
        broken_rule,
        *coverage_manifest.must_answer_coverages[narrative_rule_index + 1 :],
    )
    broken_manifest = ContractAuditCoverageManifest(must_answer_coverages=broken_rules)

    with pytest.raises(ValueError, match="非程序化 must_answer 覆盖不应声明 marker"):
        validate_contract_audit_coverage_manifest(broken_manifest)


def test_run_programmatic_audit_detects_missing_must_answer_programmatic_marker(monkeypatch: pytest.MonkeyPatch) -> None:
    """验证 programmatic_marker 覆盖规则缺失 marker 时触发 C2。

    Args:
        monkeypatch: pytest monkeypatch fixture，用于替换 coverage manifest loader。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当缺失 must_answer marker 未触发 C2 时抛出。
    """

    marker_rule = ContractMustAnswerCoverageRule(
        chapter_id=0,
        question_text="用一句话定义这只基金到底是什么产品。",
        coverage_kind="programmatic_marker",
        markers_any=("不存在的独立 must_answer marker：",),
    )
    fixture_manifest = ContractAuditCoverageManifest(must_answer_coverages=(marker_rule,))
    monkeypatch.setattr(
        "fund_agent.fund.audit.audit_programmatic.load_contract_audit_coverage_manifest",
        lambda: fixture_manifest,
    )

    result = run_programmatic_audit(_rendered_audit_input())

    assert not result.passed
    assert any(
        issue.code == "C2" and "缺少 must_answer marker" in issue.message
        for issue in result.issues
    )


def test_run_programmatic_audit_detects_missing_chapter_short_content_and_evidence() -> None:
    """验证 P1/P2/P3 能检测章节缺失、内容过短和证据缺失。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当结构错误未被检测时抛出。
    """

    broken_report = "# 投资要点概览\n短"

    result = run_programmatic_audit(ProgrammaticAuditInput(report_markdown=broken_report))

    issue_codes = {issue.code for issue in result.issues}
    assert not result.passed
    assert {"P1", "P2", "P3"}.issubset(issue_codes)


def test_run_programmatic_audit_rejects_empty_input() -> None:
    """验证空输入不会伪装为已通过全部程序审计。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当空输入通过审计时抛出。
    """

    result = run_programmatic_audit(ProgrammaticAuditInput())

    issue_codes = {issue.code for issue in result.issues}
    assert not result.passed
    assert {"P1", "L1", "R1", "R2"}.issubset(issue_codes)


def test_run_programmatic_audit_requires_final_judgment_for_r2() -> None:
    """验证缺少最终判断会触发 R2 输入缺失问题。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当缺少最终判断未触发 R2 时抛出。
    """

    result = run_programmatic_audit(
        ProgrammaticAuditInput(
            report_markdown=_complete_report(),
            rabc_attributions=(_rabc(),),
            checklist_result=_checklist("green"),
        ),
    )

    assert not result.passed
    assert any(issue.code == "R2" and issue.location == "final_judgment" for issue in result.issues)


def test_run_programmatic_audit_detects_rabc_closure_error() -> None:
    """验证 L1 能检测 R=A+B-C 不闭合。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当不闭合计算未触发 L1 时抛出。
    """

    broken_rabc = replace(_rabc(), alpha_return_a=Decimal("0.05"))

    result = run_programmatic_audit(ProgrammaticAuditInput(rabc_attributions=(broken_rabc,)))

    assert not result.passed
    assert any(issue.code == "L1" for issue in result.issues)


def test_run_programmatic_audit_detects_checklist_rule_mismatch() -> None:
    """验证 R1 能检测检查清单信号与规则不一致。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当错误汇总信号未触发 R1 时抛出。
    """

    checklist = replace(_checklist("red"), overall_signal="green", overall_status="pass")

    result = run_programmatic_audit(ProgrammaticAuditInput(checklist_result=checklist))

    assert not result.passed
    assert any(issue.code == "R1" for issue in result.issues)


def test_run_programmatic_audit_detects_item_status_mismatch() -> None:
    """验证 R1 能检测单题信号与状态不一致。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当单题状态错误未触发 R1 时抛出。
    """

    checklist = _checklist("yellow")
    first_item = replace(checklist.items[0], status="pass")
    broken_checklist = replace(checklist, items=(first_item, *checklist.items[1:]))

    result = run_programmatic_audit(ProgrammaticAuditInput(checklist_result=broken_checklist))

    assert not result.passed
    assert any(issue.code == "R1" and issue.location == "net_excess_covers_cost" for issue in result.issues)


def test_run_programmatic_audit_reports_unknown_checklist_signal_without_crashing() -> None:
    """验证未知检查清单信号触发 R1 而不是抛异常。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当未知信号未触发 R1 时抛出。
    """

    checklist = _checklist("green")
    broken_item = replace(checklist.items[0], signal="blue")  # type: ignore[arg-type]
    broken_checklist = replace(checklist, items=(broken_item, *checklist.items[1:]))

    result = run_programmatic_audit(ProgrammaticAuditInput(checklist_result=broken_checklist))

    assert not result.passed
    assert any(issue.code == "R1" and "信号未知" in issue.message for issue in result.issues)


def test_run_programmatic_audit_detects_final_judgment_conflict() -> None:
    """验证 R2 能检测最终判断与检查清单信号矛盾。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当最终判断矛盾未触发 R2 时抛出。
    """

    result = run_programmatic_audit(
        ProgrammaticAuditInput(
            checklist_result=_checklist("red"),
            final_judgment="worth_holding",
        ),
    )

    assert not result.passed
    assert any(issue.code == "R2" for issue in result.issues)
