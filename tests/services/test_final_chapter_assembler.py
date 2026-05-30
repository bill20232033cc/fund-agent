"""Gate 4 Slice 4A Service 最终章节总装器测试，覆盖模板第 0 章和第 7 章。"""

from __future__ import annotations

import ast
from dataclasses import replace
from pathlib import Path

import pytest

import fund_agent.services.final_chapter_assembler as final_chapter_assembler
from fund_agent.fund.analysis.final_judgment import FinalJudgmentDecision
from fund_agent.fund.chapter_writer import ChapterDraft
from fund_agent.services.chapter_orchestrator import (
    AcceptedChapterConclusion,
    ChapterOrchestrationResult,
    ChapterRunResult,
)
from fund_agent.services.final_chapter_assembler import (
    FinalAssemblyIssue,
    FinalAssemblyPolicy,
    FinalChapterAssemblyInput,
    FinalChapter7Summary,
    assemble_final_chapters,
)


def test_assembles_report_in_render_order_while_chapter0_uses_chapter7_summary() -> None:
    """验证生成顺序为第 7 章再第 0 章，最终渲染顺序为 0 -> 1-6 -> 7。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当总装状态、typed action 或渲染顺序错误时抛出。
    """

    result = assemble_final_chapters(_assembly_input())

    assert result.status == "accepted"
    assert result.assembled_chapter_ids == (0, 1, 2, 3, 4, 5, 6, 7)
    assert result.chapter7_summary is not None
    assert result.chapter7_summary.selected_judgment_label == "🟡 需要关注"
    assert result.chapter0_markdown is not None
    assert "- **当前动作**：🟡 需要关注" in result.chapter0_markdown
    assert "证据与出处" not in result.chapter0_markdown
    assert "> 📎 证据" not in result.chapter0_markdown
    assert "<!-- anchor:" not in result.chapter0_markdown
    assert result.chapter7_markdown is not None
    assert "规则依据：检查清单存在黄灯或灰灯问题，需要最小验证。" in result.chapter7_markdown
    assert "章节结论语境：第 1 章：" in result.chapter7_markdown
    assert result.report_markdown is not None
    assert _index(result.report_markdown, "## 第 0 章：投资要点概览") < _index(
        result.report_markdown, "## 第 1 章：产品画像"
    )
    assert _index(result.report_markdown, "## 第 6 章：核心风险") < _index(
        result.report_markdown, "## 第 7 章：是否值得持有--最终判断"
    )


@pytest.mark.parametrize("orchestration_status", ["partial", "blocked"])
def test_incomplete_when_orchestration_not_accepted(orchestration_status: str) -> None:
    """验证 Gate 3 非 accepted 不能被当作完整报告输出。

    Args:
        orchestration_status: Gate 3 非 accepted 状态。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当非 accepted 状态被 accepted 或输出完整 markdown 时抛出。
    """

    orchestration = replace(_orchestration_result(), status=orchestration_status)

    result = assemble_final_chapters(_assembly_input(orchestration_result=orchestration))

    assert result.status == "incomplete"
    assert result.report_markdown is None
    assert result.chapter0_markdown is None
    assert result.chapter7_markdown is None
    assert [issue.reason for issue in result.issues] == ["orchestration_not_accepted"]


def test_incomplete_when_required_chapter_lacks_accepted_conclusion() -> None:
    """验证必需章节缺少 accepted conclusion 会 fail-closed。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当缺失结论未阻断总装时抛出。
    """

    orchestration = _orchestration_result()
    broken = replace(orchestration.chapter_results[2], accepted_conclusion=None)
    chapter_results = (
        orchestration.chapter_results[0],
        orchestration.chapter_results[1],
        broken,
        *orchestration.chapter_results[3:],
    )
    orchestration = replace(orchestration, chapter_results=chapter_results)

    result = assemble_final_chapters(_assembly_input(orchestration_result=orchestration))

    assert result.status == "incomplete"
    assert "missing_accepted_conclusion" in {issue.reason for issue in result.issues}
    assert result.report_markdown is None


def test_incomplete_when_orchestration_has_duplicate_chapter() -> None:
    """验证 Gate 3 重复章节会 fail-closed。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当重复章节未阻断总装时抛出。
    """

    orchestration = _orchestration_result()
    duplicated = replace(
        orchestration,
        chapter_results=(*orchestration.chapter_results, orchestration.chapter_results[0]),
    )

    result = assemble_final_chapters(_assembly_input(orchestration_result=duplicated))

    assert result.status == "incomplete"
    assert "duplicate_chapter" in {issue.reason for issue in result.issues}
    assert result.report_markdown is None


def test_chapter7_preserves_developer_override_source_and_conflict_reasons() -> None:
    """验证第 7 章保留 developer_override 来源和冲突原因。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 override 来源被隐藏或判断被重派生时抛出。
    """

    decision = FinalJudgmentDecision(
        selected_judgment="worth_holding",
        derived_judgment="suggest_replace",
        source="developer_override",
        override_judgment="worth_holding",
        reasons=("检查清单存在红灯问题，最终判断应建议替换。",),
        conflict_reasons=("开发覆盖判断 worth_holding 与系统派生判断 suggest_replace 不一致。",),
    )

    result = assemble_final_chapters(_assembly_input(final_judgment_decision=decision))

    assert result.status == "accepted"
    assert result.final_judgment_selected == "worth_holding"
    assert result.chapter7_markdown is not None
    assert "- **最终判断**：🟢 值得持有" in result.chapter7_markdown
    assert "- **判断来源**：developer_override" in result.chapter7_markdown
    assert "开发覆盖判断 worth_holding 与系统派生判断 suggest_replace 不一致。" in result.chapter7_markdown


def test_chapter0_sparse_and_truncated_sources_do_not_invent_absent_numbers() -> None:
    """验证第 0 章面对稀疏/截断结论只输出回看提示，不编造数字。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当第 0 章新增 absent 数值或未记录 informational issue 时抛出。
    """

    sparse_conclusions = tuple(
        _accepted_conclusion(
            chapter_id=chapter_id,
            title=_title(chapter_id),
            markdown="" if chapter_id in (2, 4, 5) else f"- 第 {chapter_id} 章只披露定性结论",
            truncated=chapter_id == 1,
        )
        for chapter_id in range(1, 7)
    )
    orchestration = _orchestration_result(conclusions=sparse_conclusions)

    result = assemble_final_chapters(_assembly_input(orchestration_result=orchestration))

    assert result.status == "accepted"
    assert result.chapter0_markdown is not None
    assert "见第 2/4/5 章 accepted conclusion，当前缺少可压缩为封面项的结论。" in result.chapter0_markdown
    assert "9.99%" not in result.chapter0_markdown
    assert "2亿" not in result.chapter0_markdown
    assert "低于1%" not in result.chapter0_markdown
    reasons = {issue.reason for issue in result.issues}
    assert "chapter0_source_sparse" in reasons
    assert all(issue.severity == "informational" for issue in result.issues)


def test_chapter0_output_can_be_capped_without_new_facts() -> None:
    """验证第 0 章输出上限只截断，不补写新事实。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当截断未记录 issue 或输出超过上限时抛出。
    """

    result = assemble_final_chapters(
        _assembly_input(policy=FinalAssemblyPolicy(max_chapter0_chars=160))
    )

    assert result.status == "accepted"
    assert result.chapter0_markdown is not None
    assert len(result.chapter0_markdown) <= 160
    assert "chapter0_contract_violation" in {issue.reason for issue in result.issues}


def test_incomplete_debug_markdown_can_be_retained_for_late_blocking_issue(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """验证 late blocking issue 可按 policy 保留 debug markdown。

    Args:
        monkeypatch: pytest monkeypatch fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 debug markdown 分支未保留报告时抛出。
    """

    def _blocked_chapter0(
        _conclusions: tuple[AcceptedChapterConclusion, ...],
        _chapter7_summary: FinalChapter7Summary,
        *,
        max_chars: int,
    ) -> tuple[str, tuple[FinalAssemblyIssue, ...]]:
        """构造测试用 late blocking 第 0 章结果。

        Args:
            _conclusions: 未使用的 accepted conclusions。
            _chapter7_summary: 未使用的第 7 章摘要。
            max_chars: 未使用的输出上限。

        Returns:
            带 blocking issue 的第 0 章结果。

        Raises:
            无显式抛出。
        """

        _ = max_chars
        return (
            "## 第 0 章：投资要点概览\n\n### 一眼看懂\n- debug",
            (
                FinalAssemblyIssue(
                    issue_id="final_assembly:chapter_0:test_block",
                    severity="blocking",
                    reason="chapter0_contract_violation",
                    message="测试用第 0 章阻断问题。",
                    chapter_ids=(0,),
                ),
            ),
        )

    monkeypatch.setattr(final_chapter_assembler, "_render_chapter0_markdown", _blocked_chapter0)

    result = assemble_final_chapters(
        _assembly_input(policy=FinalAssemblyPolicy(allow_incomplete_debug_markdown=True))
    )

    assert result.status == "incomplete"
    assert result.report_markdown is not None
    assert "## 第 0 章：投资要点概览" in result.report_markdown
    assert "chapter0_contract_violation" in {issue.reason for issue in result.issues}


def test_policy_rejects_chapter0_lens_style_reconfiguration() -> None:
    """验证 Slice 4A 固定消费第 1-6 章，不开放 lens/基金类型重配置入口。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当非法策略未抛出 `ValueError` 时抛出。
    """

    with pytest.raises(ValueError):
        FinalAssemblyPolicy(required_body_chapter_ids=())
    with pytest.raises(ValueError):
        FinalAssemblyPolicy(required_body_chapter_ids=(1, 2, 3, 4, 5))
    with pytest.raises(ValueError):
        FinalAssemblyPolicy(required_body_chapter_ids=(1, 2, 3, 4, 5, 6, 7))
    with pytest.raises(ValueError):
        FinalAssemblyPolicy(required_body_chapter_ids=(2, 1, 3, 4, 5, 6))


def test_rejects_identity_mismatch_at_input_boundary() -> None:
    """验证总装输入 fund identity 必须同源。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 identity mismatch 未抛出 `ValueError` 时抛出。
    """

    with pytest.raises(ValueError):
        _assembly_input(fund_code="000001")


def test_rejects_invalid_final_judgment_at_input_boundary() -> None:
    """验证总装输入拒绝非法最终判断枚举值。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当非法最终判断未抛出 `ValueError` 时抛出。
    """

    decision = FinalJudgmentDecision(
        selected_judgment="buy",
        derived_judgment="needs_attention",
        source="derived",
        override_judgment=None,
        reasons=(),
        conflict_reasons=(),
    )

    with pytest.raises(ValueError):
        _assembly_input(final_judgment_decision=decision)


def test_service_public_exports_final_assembler_contract() -> None:
    """验证 Service 包公共入口导出 Gate 4 typed contract。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当公共导出缺失时抛出。
    """

    from fund_agent import services

    assert services.FinalAssemblyPolicy is FinalAssemblyPolicy
    assert services.assemble_final_chapters is assemble_final_chapters


def test_final_assembler_imports_stay_above_fact_and_source_boundaries() -> None:
    """验证 final assembler 不导入事实投影或来源仓库 helper。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当导入边界越过 Slice 4A 契约时抛出。
    """

    module_path = Path("fund_agent/services/final_chapter_assembler.py")
    tree = ast.parse(module_path.read_text(encoding="utf-8"))
    imported_modules: set[str] = set()
    imported_names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_modules.add(alias.name)
                imported_names.add(alias.name.rsplit(".", maxsplit=1)[-1])
        elif isinstance(node, ast.ImportFrom):
            if node.module is not None:
                imported_modules.add(node.module)
            imported_names.update(alias.name for alias in node.names)

    assert "StructuredFundDataBundle" not in imported_names
    assert "ChapterFactProjection" not in imported_names
    forbidden_module_fragments = (
        "data_extractor",
        "chapter_facts",
        "documents",
        "repository",
        "pdf",
        "cache",
        "source",
    )
    assert not any(
        fragment in module
        for module in imported_modules
        for fragment in forbidden_module_fragments
    )


def _assembly_input(
    *,
    fund_code: str = "110011",
    orchestration_result: ChapterOrchestrationResult | None = None,
    final_judgment_decision: FinalJudgmentDecision | None = None,
    policy: FinalAssemblyPolicy | None = None,
) -> FinalChapterAssemblyInput:
    """构造最终章节总装测试输入。

    Args:
        fund_code: 请求基金代码。
        orchestration_result: 可选 Gate 3 测试结果。
        final_judgment_decision: 可选最终判断决策。
        policy: 可选总装策略。

    Returns:
        最终章节总装输入。

    Raises:
        ValueError: 当输入同源性非法时抛出。
    """

    return FinalChapterAssemblyInput(
        fund_code=fund_code,
        report_year=2024,
        orchestration_result=orchestration_result or _orchestration_result(),
        final_judgment_decision=final_judgment_decision or _decision(),
        policy=policy or FinalAssemblyPolicy(),
    )


def _orchestration_result(
    conclusions: tuple[AcceptedChapterConclusion, ...] | None = None,
) -> ChapterOrchestrationResult:
    """构造 accepted Gate 3 测试结果。

    Args:
        conclusions: 可选 accepted conclusions。

    Returns:
        Gate 3 编排结果。

    Raises:
        无显式抛出。
    """

    accepted_conclusions = conclusions or tuple(
        _accepted_conclusion(
            chapter_id=chapter_id,
            title=_title(chapter_id),
            markdown=f"- 第 {chapter_id} 章已接受结论，包含当前报告需要保留的既有短句。",
        )
        for chapter_id in range(1, 7)
    )
    return ChapterOrchestrationResult(
        status="accepted",
        fund_code="110011",
        report_year=2024,
        projection=object(),
        chapter_results=tuple(_chapter_result(conclusion) for conclusion in accepted_conclusions),
        accepted_conclusions=accepted_conclusions,
        blocked_reasons=(),
        generated_chapter_ids=tuple(conclusion.chapter_id for conclusion in accepted_conclusions),
        skipped_chapter_ids=(),
    )


def _chapter_result(conclusion: AcceptedChapterConclusion) -> ChapterRunResult:
    """构造 accepted 单章结果。

    Args:
        conclusion: accepted conclusion。

    Returns:
        单章编排结果。

    Raises:
        无显式抛出。
    """

    return ChapterRunResult(
        chapter_id=conclusion.chapter_id,
        title=conclusion.title,
        status="accepted",
        stop_reason="none",
        accepted_draft=ChapterDraft(
            chapter_id=conclusion.chapter_id,
            title=conclusion.title,
            markdown=f"## 第 {conclusion.chapter_id} 章：{conclusion.title}\n\n{conclusion.conclusion_markdown}",
            used_fact_ids=conclusion.used_fact_ids,
            used_anchor_ids=conclusion.used_anchor_ids,
            declared_missing_reasons=conclusion.declared_missing_reasons,
            deleted_item_rule_ids=(),
            model_name="fake-writer",
            finish_reason="stop",
        ),
        accepted_conclusion=conclusion,
        attempts=(),
        issues=(),
    )


def _accepted_conclusion(
    *,
    chapter_id: int,
    title: str,
    markdown: str,
    truncated: bool = False,
) -> AcceptedChapterConclusion:
    """构造 accepted conclusion。

    Args:
        chapter_id: 章节编号。
        title: 章节标题。
        markdown: 结论 markdown。
        truncated: 是否模拟 Gate 3 截断。

    Returns:
        accepted conclusion。

    Raises:
        无显式抛出。
    """

    return AcceptedChapterConclusion(
        chapter_id=chapter_id,
        title=title,
        conclusion_markdown=markdown,
        conclusion_truncated=truncated,
        conclusion_source="heading",
        used_fact_ids=(f"fact.{chapter_id}",),
        used_anchor_ids=(f"anchor.{chapter_id}",),
        declared_missing_reasons=(),
        audit_checked_rules=(),
    )


def _decision() -> FinalJudgmentDecision:
    """构造默认最终判断决策。

    Args:
        无。

    Returns:
        最终判断决策。

    Raises:
        无显式抛出。
    """

    return FinalJudgmentDecision(
        selected_judgment="needs_attention",
        derived_judgment="needs_attention",
        source="derived",
        override_judgment=None,
        reasons=("检查清单存在黄灯或灰灯问题，需要最小验证。",),
        conflict_reasons=(),
    )


def _title(chapter_id: int) -> str:
    """返回测试章节标题。

    Args:
        chapter_id: 章节编号。

    Returns:
        章节标题。

    Raises:
        无显式抛出。
    """

    titles = {
        1: "产品画像",
        2: "收益归因",
        3: "基金经理画像",
        4: "投资者获得感",
        5: "当前阶段",
        6: "核心风险",
    }
    return titles[chapter_id]


def _index(text: str, needle: str) -> int:
    """返回子串位置，提供更清楚的断言错误。

    Args:
        text: 被搜索文本。
        needle: 目标子串。

    Returns:
        子串起始位置。

    Raises:
        AssertionError: 当子串缺失时抛出。
    """

    index = text.find(needle)
    assert index >= 0, needle
    return index
