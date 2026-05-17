"""程序审计测试。"""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal

from fund_agent.fund.analysis import ChecklistItem, ChecklistResult, RabcAttribution
from fund_agent.fund.audit import ProgrammaticAuditInput, run_programmatic_audit


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


def test_run_programmatic_audit_passes_complete_inputs() -> None:
    """验证完整输入通过 P1/P2/P3/L1/R1/R2 审计。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当完整输入未通过审计时抛出。
    """

    result = run_programmatic_audit(
        ProgrammaticAuditInput(
            report_markdown=_complete_report(),
            rabc_attributions=(_rabc(),),
            checklist_result=_checklist("green"),
            final_judgment="worth_holding",
        ),
    )

    assert result.passed
    assert not result.issues
    assert result.checked_rules == ("P1", "P2", "P3", "L1", "R1", "R2")


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
