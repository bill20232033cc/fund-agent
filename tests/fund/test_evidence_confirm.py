"""Evidence Confirm no-live 锚点可审计性评分测试。"""

from __future__ import annotations

from dataclasses import replace

from fund_agent.fund.chapter_facts import (
    ChapterFactEntry,
    ChapterFactInput,
    ChapterFactProjection,
    project_chapter_facts,
)
from fund_agent.fund.evidence_confirm import (
    EVIDENCE_CONFIRM_SCHEMA_VERSION,
    EVIDENCE_CONFIRM_V2_SCHEMA_VERSION,
    EvidenceConfirmReference,
    confirm_chapter_evidence,
    confirm_chapter_evidence_v2,
    confirm_projection_evidence,
    confirm_projection_evidence_v2,
)
from tests.fund.test_chapter_facts import _bundle


def test_precise_anchor_and_matching_excerpt_passes() -> None:
    """验证精确 anchor 加同源摘录命中时 E1/E2/E3 通过。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 同源摘录未通过时抛出。
    """

    chapter, fact = _chapter_and_fact("structured.turnover_rate")
    result = confirm_chapter_evidence(
        chapter,
        (_reference(fact.evidence_anchor_ids[0], excerpt_text="年报披露换手率为 120%。"),),
    )
    fact_result = result.fact_results[0]

    assert result.schema_version == EVIDENCE_CONFIRM_SCHEMA_VERSION
    assert result.overall_status == "pass"
    assert result.auditability_score == 100
    assert result.issues == ()
    assert fact_result.status == "pass"
    assert fact_result.auditability_score == 100
    assert fact_result.matched_anchor_ids == fact.evidence_anchor_ids


def test_imprecise_anchor_warns_but_keeps_value_match() -> None:
    """验证锚点缺少页码/表格/行级定位时触发 E1 reviewable。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: E1 未触发或分数错误时抛出。
    """

    chapter, fact = _chapter_and_fact("structured.turnover_rate")
    result = confirm_chapter_evidence(
        chapter,
        (
            _reference(
                fact.evidence_anchor_ids[0],
                excerpt_text="年报披露换手率为 120%。",
                page_number=None,
                row_locator=None,
            ),
        ),
    )

    assert result.overall_status == "warn"
    assert result.auditability_score == 70
    assert result.fact_results[0].status == "warn"
    assert result.fact_results[0].auditability_score == 70
    assert {issue.rule_code for issue in result.issues} == {"E1"}


def test_value_absent_from_same_anchor_excerpt_fails_e2() -> None:
    """验证 fact value 未出现在同 anchor 摘录时触发 E2。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: E2 未触发时抛出。
    """

    chapter, fact = _chapter_and_fact("structured.turnover_rate")
    result = confirm_chapter_evidence(
        chapter,
        (_reference(fact.evidence_anchor_ids[0], excerpt_text="年报只披露管理费率 1.20%。"),),
    )

    assert result.overall_status == "fail"
    assert result.fact_results[0].status == "fail"
    assert result.fact_results[0].auditability_score == 40
    assert result.fact_results[0].matched_anchor_ids == ()
    assert {issue.rule_code for issue in result.issues} == {"E2"}


def test_numeric_token_does_not_match_inside_larger_decimal() -> None:
    """验证短数字 token 不跨数值边界误命中。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 数字 token 跨边界误匹配时抛出。
    """

    chapter, fact = _chapter_and_fact("structured.turnover_rate")
    chapter = replace(chapter, facts=(replace(fact, value={"turnover_rate": "12"}),))
    result = confirm_chapter_evidence(
        chapter,
        (_reference(fact.evidence_anchor_ids[0], excerpt_text="年报披露管理费率为 1.20%。"),),
    )

    assert result.overall_status == "fail"
    assert result.fact_results[0].auditability_score == 40
    assert {issue.rule_code for issue in result.issues} == {"E2"}


def test_numeric_percent_token_matches_equivalent_decimal_format() -> None:
    """验证百分比 token 支持小数尾零等价匹配。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 等价百分比格式未匹配时抛出。
    """

    chapter, fact = _chapter_and_fact("structured.turnover_rate")
    chapter = replace(chapter, facts=(replace(fact, value={"turnover_rate": "1.20%"}),))
    result = confirm_chapter_evidence(
        chapter,
        (_reference(fact.evidence_anchor_ids[0], excerpt_text="年报披露管理费率为 1.2%。"),),
    )

    assert result.overall_status == "pass"
    assert result.fact_results[0].auditability_score == 100
    assert result.issues == ()


def test_empty_excerpt_emits_e1_and_e2() -> None:
    """验证空摘录同时触发定位可复核性与值不匹配问题。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 空摘录 issue 组合错误时抛出。
    """

    chapter, fact = _chapter_and_fact("structured.turnover_rate")
    result = confirm_chapter_evidence(
        chapter,
        (_reference(fact.evidence_anchor_ids[0], excerpt_text="   "),),
    )

    assert result.overall_status == "fail"
    assert result.fact_results[0].status == "fail"
    assert result.fact_results[0].auditability_score == 40
    assert {issue.rule_code for issue in result.issues} == {"E1", "E2"}


def test_available_fact_without_anchor_fails_e3() -> None:
    """验证可用 annual-report fact 缺 anchor 时触发 E3。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: E3 未触发时抛出。
    """

    chapter, fact = _chapter_and_fact("structured.turnover_rate")
    chapter = replace(chapter, facts=(replace(fact, evidence_anchor_ids=()),), evidence_anchors=())

    result = confirm_chapter_evidence(chapter, ())

    assert result.overall_status == "fail"
    assert result.fund_code == "110011"
    assert result.report_year == 2024
    assert result.auditability_score == 0
    assert result.fact_results[0].auditability_score == 0
    assert {issue.rule_code for issue in result.issues} == {"E3"}


def test_available_fact_with_anchor_but_empty_references_fails_e3() -> None:
    """验证有 anchor 但调用方未传 reference 时触发 E3。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 空 references 未 fail-closed 时抛出。
    """

    chapter, fact = _chapter_and_fact("structured.turnover_rate")
    result = confirm_chapter_evidence(chapter, ())

    assert fact.evidence_anchor_ids
    assert result.overall_status == "fail"
    assert result.auditability_score == 0
    assert result.fact_results[0].auditability_score == 0
    assert {issue.rule_code for issue in result.issues} == {"E3"}


def test_partial_dangling_anchor_fails_closed_even_with_valid_v1_proof() -> None:
    """验证 V1 有效 proof 不能掩盖同 fact 的悬挂 anchor。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 悬挂 anchor 被有效 proof 掩盖时抛出。
    """

    chapter, fact = _chapter_and_fact("structured.turnover_rate")
    valid_anchor_id = fact.evidence_anchor_ids[0]
    dangling_anchor_id = "missing-anchor"
    mixed_fact = replace(fact, evidence_anchor_ids=(valid_anchor_id, dangling_anchor_id))
    chapter = replace(chapter, facts=(mixed_fact,))

    result = confirm_chapter_evidence(
        chapter,
        (_reference(valid_anchor_id, excerpt_text="年报披露换手率为 120%。"),),
    )
    fact_result = result.fact_results[0]

    assert result.overall_status == "fail"
    assert result.auditability_score == 0
    assert fact_result.status == "fail"
    assert fact_result.auditability_score == 0
    assert fact_result.matched_anchor_ids == ()
    assert {issue.rule_code for issue in result.issues} == {"E3"}
    assert tuple(issue.anchor_id for issue in result.issues) == (dangling_anchor_id,)


def test_projection_partial_dangling_anchor_fails_closed_with_v1_issue_anchor() -> None:
    """验证 V1 projection 级复核保留悬挂 anchor issue 定位。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: projection 级悬挂 anchor 未 fail-closed 时抛出。
    """

    projection = project_chapter_facts(_bundle(), chapter_ids=(3,))
    chapter = projection.chapters[0]
    fact = next(item for item in chapter.facts if item.source_field_id == "structured.turnover_rate")
    valid_anchor_id = fact.evidence_anchor_ids[0]
    dangling_anchor_id = "missing-anchor"
    mixed_fact = replace(fact, evidence_anchor_ids=(valid_anchor_id, dangling_anchor_id))
    anchor_ids = set(fact.evidence_anchor_ids)
    anchors = tuple(anchor for anchor in chapter.evidence_anchors if anchor.anchor_id in anchor_ids)
    projection = replace(
        projection,
        chapters=(replace(chapter, facts=(mixed_fact,), evidence_anchors=anchors),),
    )

    result = confirm_projection_evidence(
        projection,
        (_reference(valid_anchor_id, excerpt_text="年报披露换手率为 120%。"),),
    )

    assert result.overall_status == "fail"
    assert result.auditability_score == 0
    assert result.fact_results[0].auditability_score == 0
    assert tuple(issue.anchor_id for issue in result.issues) == (dangling_anchor_id,)


def test_candidate_or_not_proven_reference_cannot_satisfy_source_support() -> None:
    """验证 candidate-only / not_proven reference 不能满足 E2/E3。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: candidate reference 被错误当作 proof 时抛出。
    """

    chapter, fact = _chapter_and_fact("structured.turnover_rate")
    references = (
        _reference(
            fact.evidence_anchor_ids[0],
            excerpt_text="年报披露换手率为 120%。",
            source_kind="docling_pdf_candidate",
            candidate_only=True,
            source_truth_status="not_proven",
        ),
    )

    result = confirm_chapter_evidence(chapter, references)

    assert result.overall_status == "fail"
    assert result.fact_results[0].status == "fail"
    assert result.fact_results[0].auditability_score == 0
    assert {issue.rule_code for issue in result.issues} == {"E3"}


def test_candidate_only_reference_cannot_satisfy_source_support() -> None:
    """验证仅 candidate_only 非法时不能满足 proof predicate。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: candidate_only 被错误接受时抛出。
    """

    chapter, fact = _chapter_and_fact("structured.turnover_rate")
    result = confirm_chapter_evidence(
        chapter,
        (
            _reference(
                fact.evidence_anchor_ids[0],
                excerpt_text="年报披露换手率为 120%。",
                candidate_only=True,
            ),
        ),
    )

    assert result.overall_status == "fail"
    assert result.fact_results[0].auditability_score == 0
    assert {issue.rule_code for issue in result.issues} == {"E3"}


def test_not_proven_reference_cannot_satisfy_source_support() -> None:
    """验证仅 not_proven 非法时不能满足 proof predicate。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: not_proven 被错误接受时抛出。
    """

    chapter, fact = _chapter_and_fact("structured.turnover_rate")
    result = confirm_chapter_evidence(
        chapter,
        (
            _reference(
                fact.evidence_anchor_ids[0],
                excerpt_text="年报披露换手率为 120%。",
                source_truth_status="not_proven",
            ),
        ),
    )

    assert result.overall_status == "fail"
    assert result.fact_results[0].auditability_score == 0
    assert {issue.rule_code for issue in result.issues} == {"E3"}


def test_unknown_source_kind_reference_cannot_satisfy_source_support() -> None:
    """验证仅 source_kind 非闭集时不能满足 proof predicate。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 非闭集 source_kind 被错误接受时抛出。
    """

    chapter, fact = _chapter_and_fact("structured.turnover_rate")
    result = confirm_chapter_evidence(
        chapter,
        (
            _reference(
                fact.evidence_anchor_ids[0],
                excerpt_text="年报披露换手率为 120%。",
                source_kind="docling_pdf_candidate",
            ),
        ),
    )

    assert result.overall_status == "fail"
    assert result.fact_results[0].auditability_score == 0
    assert {issue.rule_code for issue in result.issues} == {"E3"}


def test_invalid_reference_kind_source_kind_pair_is_non_proof() -> None:
    """验证 reference_kind/source_kind 非法组合不能满足 proof predicate。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 非法组合被错误接受时抛出。
    """

    chapter, fact = _chapter_and_fact("structured.turnover_rate")
    result = confirm_chapter_evidence(
        chapter,
        (
            _reference(
                fact.evidence_anchor_ids[0],
                excerpt_text="年报披露换手率为 120%。",
                reference_kind="reviewed_note",
                source_kind="annual_report",
            ),
        ),
    )

    assert result.overall_status == "fail"
    assert result.fact_results[0].auditability_score == 0
    assert {issue.rule_code for issue in result.issues} == {"E3"}


def test_reference_source_kind_must_match_chapter_anchor_source_kind() -> None:
    """验证合法 reference kind/source kind 仍必须匹配章节 anchor 来源身份。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: derived reference 错误关闭 annual-report fact 时抛出。
    """

    chapter, fact = _chapter_and_fact("structured.turnover_rate")
    result = confirm_chapter_evidence(
        chapter,
        (
            _reference(
                fact.evidence_anchor_ids[0],
                excerpt_text="年报披露换手率为 120%。",
                reference_kind="derived_calculation",
                source_kind="derived",
            ),
        ),
    )

    assert result.overall_status == "fail"
    assert result.fact_results[0].auditability_score == 0
    assert {issue.rule_code for issue in result.issues} == {"E3"}


def test_reference_document_year_must_match_report_year() -> None:
    """验证同 anchor 但年份不匹配的 reference 不能关闭 E2/E3。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 错误年份 reference 被接受时抛出。
    """

    chapter, fact = _chapter_and_fact("structured.turnover_rate")
    result = confirm_chapter_evidence(
        chapter,
        (
            _reference(
                fact.evidence_anchor_ids[0],
                excerpt_text="年报披露换手率为 120%。",
                document_year=2023,
            ),
        ),
    )

    assert result.overall_status == "fail"
    assert result.fact_results[0].auditability_score == 0
    assert {issue.rule_code for issue in result.issues} == {"E3"}


def test_unknown_reference_kind_is_non_proof_without_exception() -> None:
    """验证未知 reference_kind fail-closed 为 non-proof。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 未知 reference_kind 抛异常或被接受时抛出。
    """

    chapter, fact = _chapter_and_fact("structured.turnover_rate")
    result = confirm_chapter_evidence(
        chapter,
        (
            _reference(
                fact.evidence_anchor_ids[0],
                excerpt_text="年报披露换手率为 120%。",
                reference_kind="unknown_reference_kind",
            ),
        ),
    )

    assert result.overall_status == "fail"
    assert result.fact_results[0].auditability_score == 0
    assert {issue.rule_code for issue in result.issues} == {"E3"}


def test_unrelated_anchor_excerpt_does_not_close_e2() -> None:
    """验证其它 anchor 的摘录不能关闭当前 fact 的 E2。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 跨 anchor 值匹配被错误接受时抛出。
    """

    chapter, fact = _chapter_and_fact("structured.turnover_rate")
    result = confirm_chapter_evidence(
        chapter,
        (
            _reference("anchor:unrelated", excerpt_text="年报披露换手率为 120%。"),
            _reference(fact.evidence_anchor_ids[0], excerpt_text="年报披露管理费率 1.20%。"),
        ),
    )

    assert result.overall_status == "fail"
    assert result.fact_results[0].matched_anchor_ids == ()
    assert {issue.rule_code for issue in result.issues} == {"E2"}


def test_derived_and_not_applicable_facts_are_not_scored() -> None:
    """验证 derived/not_applicable fact 不强制走年报摘录匹配。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 不适用 fact 被错误计分时抛出。
    """

    chapter, fact = _chapter_and_fact("structured.turnover_rate")
    derived_fact = replace(
        fact,
        source_field_id="synthetic.cross_period_comparison",
        extraction_mode="derived",
        evidence_anchor_ids=(),
    )
    not_applicable_fact = replace(
        fact,
        fact_id=f"{fact.fact_id}:na",
        source_field_id="structured.bond_risk_evidence",
        status="not_applicable",
        evidence_anchor_ids=(),
    )
    chapter = replace(chapter, facts=(derived_fact, not_applicable_fact), evidence_anchors=())

    result = confirm_chapter_evidence(chapter, ())

    assert result.overall_status == "not_applicable"
    assert result.auditability_score is None
    assert {item.status for item in result.fact_results} == {"not_applicable"}
    assert all(item.auditability_score is None for item in result.fact_results)
    assert result.issues == ()


def test_projection_aggregates_multiple_chapters_deterministically() -> None:
    """验证 projection 级聚合保留稳定排序和平均分。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: projection 聚合状态或分数错误时抛出。
    """

    projection = project_chapter_facts(_bundle(), chapter_ids=(2, 3))
    facts = _available_facts(projection)
    references = tuple(
        _reference(anchor_id, excerpt_text=_excerpt_for_fact(fact))
        for fact in facts
        for anchor_id in fact.evidence_anchor_ids
    )

    result = confirm_projection_evidence(projection, references)

    assert result.overall_status == "pass"
    assert result.auditability_score == 100
    assert result.fact_results == tuple(
        sorted(result.fact_results, key=lambda item: (item.source_field_id, item.fact_id))
    )
    nav_data_result = next(item for item in result.fact_results if item.source_field_id == "structured.nav_data")
    assert nav_data_result.status == "not_applicable"
    assert nav_data_result.auditability_score is None
    assert result.issues == ()


def test_empty_projection_returns_not_applicable() -> None:
    """验证空 projection 不伪造通过或失败状态。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 空 projection 聚合状态错误时抛出。
    """

    base_projection = project_chapter_facts(_bundle(), chapter_ids=(3,))
    projection = ChapterFactProjection(
        schema_version=base_projection.schema_version,
        fund_code=base_projection.fund_code,
        report_year=base_projection.report_year,
        fund_type=base_projection.fund_type,
        classification_basis=base_projection.classification_basis,
        chapters=(),
        global_missing_reasons=(),
    )

    result = confirm_projection_evidence(projection, ())

    assert result.overall_status == "not_applicable"
    assert result.auditability_score is None
    assert result.fact_results == ()
    assert result.issues == ()


def test_chapter_aggregation_uses_strictest_status_and_average_score() -> None:
    """验证混合 fact 状态按最严格状态聚合并平均可计分 fact。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 聚合状态或分数错误时抛出。
    """

    chapter, fact = _chapter_and_fact("structured.turnover_rate")
    failed_fact = replace(
        fact,
        fact_id=f"{fact.fact_id}:failed",
        source_field_id="structured.aaa_failed_turnover_rate",
        value={"turnover_rate": "121%"},
    )
    chapter = replace(chapter, facts=(fact, failed_fact))
    result = confirm_chapter_evidence(
        chapter,
        (_reference(fact.evidence_anchor_ids[0], excerpt_text="年报披露换手率为 120%。"),),
    )

    assert result.overall_status == "fail"
    assert result.auditability_score == 70
    assert [item.auditability_score for item in result.fact_results] == [40, 100]
    assert {issue.rule_code for issue in result.issues} == {"E2"}


# ─── V2 测试 ───────────────────────────────────────────────────────────────────


def test_v2_result_uses_v2_schema_version() -> None:
    """验证 V2 结果使用 evidence_confirm.v2 schema version。"""

    chapter, fact = _chapter_and_fact("structured.turnover_rate")
    result = confirm_chapter_evidence_v2(
        chapter,
        (_reference(fact.evidence_anchor_ids[0], excerpt_text="年报披露换手率为 120%。"),),
    )

    assert result.schema_version == EVIDENCE_CONFIRM_V2_SCHEMA_VERSION
    assert result.schema_version == "evidence_confirm.v2"


def test_v2_fact_result_includes_five_dimensions_in_order() -> None:
    """验证 V2 fact result 包含五个维度且按确定性顺序。"""

    chapter, fact = _chapter_and_fact("structured.turnover_rate")
    result = confirm_chapter_evidence_v2(
        chapter,
        (_reference(fact.evidence_anchor_ids[0], excerpt_text="年报披露换手率为 120%。"),),
    )

    fact_result = result.fact_results[0]
    assert len(fact_result.dimension_results) == 5
    expected_dims = (
        "anchor_precision",
        "source_support",
        "missing_evidence",
        "proof_boundary",
        "value_match",
    )
    actual_dims = tuple(d.dimension for d in fact_result.dimension_results)
    assert actual_dims == expected_dims


def test_v2_blocking_e3_produces_hard_gate_fail() -> None:
    """验证 E3 阻塞产生 hard gate fail。"""

    chapter, fact = _chapter_and_fact("structured.turnover_rate")
    chapter = replace(chapter, facts=(replace(fact, evidence_anchor_ids=()),), evidence_anchors=())
    result = confirm_chapter_evidence_v2(chapter, ())

    assert result.overall_status == "fail"
    assert result.fact_results[0].status == "fail"
    assert result.fact_results[0].hard_gate.status == "fail"
    assert len(result.hard_gate.blocking_issue_ids) > 0


def test_v2_e1_only_imprecision_produces_hard_gate_warn() -> None:
    """验证 E1 定位不精确产生 hard gate warn。"""

    chapter, fact = _chapter_and_fact("structured.turnover_rate")
    result = confirm_chapter_evidence_v2(
        chapter,
        (
            _reference(
                fact.evidence_anchor_ids[0],
                excerpt_text="年报披露换手率为 120%。",
                page_number=None,
                row_locator=None,
            ),
        ),
    )

    assert result.overall_status == "warn"
    assert result.fact_results[0].status == "warn"
    assert result.fact_results[0].hard_gate.status == "warn"
    assert result.fact_results[0].auditability_score == 94
    assert result.auditability_score == 94


def test_v2_all_applicable_pass_produces_hard_gate_pass() -> None:
    """验证全部通过产生 hard gate pass。"""

    chapter, fact = _chapter_and_fact("structured.turnover_rate")
    result = confirm_chapter_evidence_v2(
        chapter,
        (_reference(fact.evidence_anchor_ids[0], excerpt_text="年报披露换手率为 120%。"),),
    )

    assert result.overall_status == "pass"
    assert result.fact_results[0].status == "pass"
    assert result.fact_results[0].hard_gate.status == "pass"
    assert result.fact_results[0].hard_gate.failed_dimension_count == 0
    assert result.fact_results[0].auditability_score == 100
    assert result.auditability_score == 100


def test_v2_dangling_anchor_fails_missing_evidence_even_with_valid_proof() -> None:
    """验证有效 proof 不能掩盖同 fact 的 dangling anchor。"""

    chapter, fact = _chapter_and_fact("structured.turnover_rate")
    valid_anchor_id = fact.evidence_anchor_ids[0]
    mixed_fact = replace(fact, evidence_anchor_ids=(valid_anchor_id, "missing-anchor"))
    chapter = replace(chapter, facts=(mixed_fact,))

    result = confirm_chapter_evidence_v2(
        chapter,
        (_reference(valid_anchor_id, excerpt_text="年报披露换手率为 120%。"),),
    )
    fact_result = result.fact_results[0]
    missing_dim = next(d for d in fact_result.dimension_results if d.dimension == "missing_evidence")
    source_dim = next(d for d in fact_result.dimension_results if d.dimension == "source_support")

    assert result.overall_status == "fail"
    assert result.auditability_score == 0
    assert fact_result.status == "fail"
    assert fact_result.auditability_score == 0
    assert missing_dim.status == "fail"
    assert missing_dim.score == 0
    assert source_dim.status == "pass"
    assert any(issue.anchor_id == "missing-anchor" for issue in result.issues)


def test_v2_all_dangling_anchor_reports_concrete_anchor_ids() -> None:
    """验证 V2 全悬挂 anchor 路径也报告具体 anchor ids。"""

    chapter, fact = _chapter_and_fact("structured.turnover_rate")
    dangling_anchor_ids = ("missing-anchor-a", "missing-anchor-b")
    dangling_fact = replace(fact, evidence_anchor_ids=dangling_anchor_ids)
    chapter = replace(chapter, facts=(dangling_fact,), evidence_anchors=())

    result = confirm_chapter_evidence_v2(chapter, ())
    fact_result = result.fact_results[0]
    missing_dim = next(d for d in fact_result.dimension_results if d.dimension == "missing_evidence")

    assert result.overall_status == "fail"
    assert result.auditability_score == 0
    assert fact_result.status == "fail"
    assert fact_result.auditability_score == 0
    assert missing_dim.status == "fail"
    assert missing_dim.score == 0
    assert {issue.anchor_id for issue in result.issues} == set(dangling_anchor_ids)


def test_v2_derived_not_applicable_produces_hard_gate_not_applicable() -> None:
    """验证 derived/not_applicable fact 产生 hard gate not_applicable。"""

    chapter, fact = _chapter_and_fact("structured.turnover_rate")
    derived_fact = replace(
        fact,
        source_field_id="synthetic.cross_period_comparison",
        extraction_mode="derived",
        evidence_anchor_ids=(),
    )
    not_applicable_fact = replace(
        fact,
        fact_id=f"{fact.fact_id}:na",
        source_field_id="structured.bond_risk_evidence",
        status="not_applicable",
        evidence_anchor_ids=(),
    )
    chapter = replace(chapter, facts=(derived_fact, not_applicable_fact), evidence_anchors=())

    result = confirm_chapter_evidence_v2(chapter, ())

    assert result.overall_status == "not_applicable"
    assert result.auditability_score is None
    assert all(fr.status == "not_applicable" for fr in result.fact_results)


def test_v2_candidate_only_reference_fails_proof_boundary_and_source_support() -> None:
    """验证 candidate-only reference 同时 fail proof_boundary 和 source_support。"""

    chapter, fact = _chapter_and_fact("structured.turnover_rate")
    references = (
        _reference(
            fact.evidence_anchor_ids[0],
            excerpt_text="年报披露换手率为 120%。",
            candidate_only=True,
        ),
    )

    result = confirm_chapter_evidence_v2(chapter, references)
    fact_result = result.fact_results[0]

    proof_dim = next(d for d in fact_result.dimension_results if d.dimension == "proof_boundary")
    source_dim = next(d for d in fact_result.dimension_results if d.dimension == "source_support")

    assert proof_dim.status == "fail"
    assert source_dim.status == "fail"
    messages_by_issue_id = {issue.issue_id: issue.message for issue in result.issues}
    source_messages = tuple(messages_by_issue_id[issue_id] for issue_id in source_dim.issue_ids)
    missing_dim = next(d for d in fact_result.dimension_results if d.dimension == "missing_evidence")
    missing_messages = tuple(messages_by_issue_id[issue_id] for issue_id in missing_dim.issue_ids)

    assert any("source_support" in message for message in source_messages)
    assert any("missing_evidence" in message for message in missing_messages)
    assert set(source_messages).isdisjoint(missing_messages)


def test_v2_not_proven_reference_fails_proof_boundary() -> None:
    """验证 not_proven reference fail proof_boundary。"""

    chapter, fact = _chapter_and_fact("structured.turnover_rate")
    references = (
        _reference(
            fact.evidence_anchor_ids[0],
            excerpt_text="年报披露换手率为 120%。",
            source_truth_status="not_proven",
        ),
    )

    result = confirm_chapter_evidence_v2(chapter, references)
    fact_result = result.fact_results[0]
    proof_dim = next(d for d in fact_result.dimension_results if d.dimension == "proof_boundary")

    assert proof_dim.status == "fail"


def test_v2_invalid_kind_source_kind_pair_fails_proof_boundary() -> None:
    """验证非法 kind/source_kind 组合 fail proof_boundary。"""

    chapter, fact = _chapter_and_fact("structured.turnover_rate")
    references = (
        _reference(
            fact.evidence_anchor_ids[0],
            excerpt_text="年报披露换手率为 120%。",
            reference_kind="reviewed_note",
            source_kind="annual_report",
        ),
    )

    result = confirm_chapter_evidence_v2(chapter, references)
    fact_result = result.fact_results[0]
    proof_dim = next(d for d in fact_result.dimension_results if d.dimension == "proof_boundary")

    assert proof_dim.status == "fail"


def test_v2_wrong_document_year_fails_proof_boundary() -> None:
    """验证错误年份 fail proof_boundary。"""

    chapter, fact = _chapter_and_fact("structured.turnover_rate")
    references = (
        _reference(
            fact.evidence_anchor_ids[0],
            excerpt_text="年报披露换手率为 120%。",
            document_year=2023,
        ),
    )

    result = confirm_chapter_evidence_v2(chapter, references)
    fact_result = result.fact_results[0]
    proof_dim = next(d for d in fact_result.dimension_results if d.dimension == "proof_boundary")

    assert proof_dim.status == "fail"


def test_v2_anchor_locator_mismatches_explain_failed_field() -> None:
    """验证 anchor 身份字段不匹配时 proof issue 指明具体字段。"""

    chapter, fact = _chapter_and_fact("structured.turnover_rate")
    anchor = chapter.evidence_anchors[0]
    scenarios = (
        (
            replace(anchor, document_year=2025),
            _reference(fact.evidence_anchor_ids[0], excerpt_text="年报披露换手率为 120%。"),
            "anchor document_year",
        ),
        (
            anchor,
            _reference(
                fact.evidence_anchor_ids[0],
                excerpt_text="年报披露换手率为 120%。",
                section_id="§9",
            ),
            "section_id",
        ),
        (
            replace(anchor, page_number=12),
            _reference(
                fact.evidence_anchor_ids[0],
                excerpt_text="年报披露换手率为 120%。",
                page_number=13,
            ),
            "page_number",
        ),
        (
            replace(anchor, table_id="table-1"),
            _reference(
                fact.evidence_anchor_ids[0],
                excerpt_text="年报披露换手率为 120%。",
                table_id="table-2",
            ),
            "table_id",
        ),
        (
            anchor,
            _reference(
                fact.evidence_anchor_ids[0],
                excerpt_text="年报披露换手率为 120%。",
                row_locator="other-row",
            ),
            "row_locator",
        ),
    )

    for mismatch_anchor, reference, expected_message_part in scenarios:
        scenario_chapter = replace(chapter, evidence_anchors=(mismatch_anchor,))
        result = confirm_chapter_evidence_v2(scenario_chapter, (reference,))
        fact_result = result.fact_results[0]
        proof_dim = next(d for d in fact_result.dimension_results if d.dimension == "proof_boundary")
        proof_messages = tuple(
            issue.message for issue in result.issues if issue.issue_id in proof_dim.issue_ids
        )

        assert proof_dim.status == "fail"
        assert any(expected_message_part in message for message in proof_messages)


def test_v2_mixed_references_fail_proof_boundary_even_with_valid_proof() -> None:
    """验证混合引用（valid proven + invalid same-anchor）fail proof_boundary。"""

    chapter, fact = _chapter_and_fact("structured.turnover_rate")
    references = (
        _reference(fact.evidence_anchor_ids[0], excerpt_text="年报披露换手率为 120%。"),
        _reference(
            fact.evidence_anchor_ids[0],
            excerpt_text="另一条摘录。",
            candidate_only=True,
        ),
    )

    result = confirm_chapter_evidence_v2(chapter, references)
    fact_result = result.fact_results[0]
    proof_dim = next(d for d in fact_result.dimension_results if d.dimension == "proof_boundary")
    source_dim = next(d for d in fact_result.dimension_results if d.dimension == "source_support")

    assert proof_dim.status == "fail"
    # valid references can independently satisfy source_support
    assert source_dim.status == "pass"


def test_v2_value_mismatch_fails_value_match_while_source_support_passes() -> None:
    """验证同 anchor 值不匹配 fail value_match 而 source_support 可以 pass。"""

    chapter, fact = _chapter_and_fact("structured.turnover_rate")
    references = (
        _reference(fact.evidence_anchor_ids[0], excerpt_text="年报只披露管理费率 1.20%。"),
    )

    result = confirm_chapter_evidence_v2(chapter, references)
    fact_result = result.fact_results[0]
    value_dim = next(d for d in fact_result.dimension_results if d.dimension == "value_match")
    source_dim = next(d for d in fact_result.dimension_results if d.dimension == "source_support")

    assert value_dim.status == "fail"
    assert value_dim.score == 40
    assert source_dim.status == "pass"


def test_v2_unrelated_anchor_excerpt_cannot_pass_value_match() -> None:
    """验证其它 anchor 的摘录不能通过当前 fact 的 value_match。"""

    chapter, fact = _chapter_and_fact("structured.turnover_rate")
    references = (
        _reference("anchor:unrelated", excerpt_text="年报披露换手率为 120%。"),
        _reference(fact.evidence_anchor_ids[0], excerpt_text="年报披露管理费率 1.20%。"),
    )

    result = confirm_chapter_evidence_v2(chapter, references)
    fact_result = result.fact_results[0]
    value_dim = next(d for d in fact_result.dimension_results if d.dimension == "value_match")

    assert value_dim.status == "fail"
    assert value_dim.matched_anchor_ids == ()


def test_v2_projection_aggregation_deterministic_averages_numeric_scores() -> None:
    """验证 projection 级聚合确定性排序且只平均 numeric fact scores。"""

    projection = project_chapter_facts(_bundle(), chapter_ids=(2, 3))
    facts = _available_facts(projection)
    references = tuple(
        _reference(anchor_id, excerpt_text=_excerpt_for_fact(fact))
        for fact in facts
        for anchor_id in fact.evidence_anchor_ids
    )

    result = confirm_projection_evidence_v2(projection, references)
    expected_source_field_ids = tuple(
        fact.source_field_id
        for chapter in sorted(projection.chapters, key=lambda item: item.chapter_id)
        for fact in sorted(chapter.facts, key=lambda item: (item.source_field_id, item.fact_id))
    )

    assert result.schema_version == EVIDENCE_CONFIRM_V2_SCHEMA_VERSION
    assert tuple(item.source_field_id for item in result.fact_results) == expected_source_field_ids
    nav_data_result = next(item for item in result.fact_results if item.source_field_id == "structured.nav_data")
    assert nav_data_result.status == "not_applicable"
    assert nav_data_result.auditability_score is None


def test_v2_projection_order_uses_chapter_id_before_source_field_id() -> None:
    """验证 V2 projection 排序以 chapter_id 为第一排序键。"""

    base_projection = project_chapter_facts(_bundle(), chapter_ids=(2, 3))
    chapter_2, chapter_3 = base_projection.chapters
    fact_2 = next(
        fact for fact in chapter_2.facts if fact.status == "available" and fact.evidence_anchor_ids
    )
    fact_3 = next(
        fact for fact in chapter_3.facts if fact.status == "available" and fact.evidence_anchor_ids
    )
    chapter_2_fact = replace(fact_2, source_field_id="structured.zzz_chapter_2")
    chapter_3_fact = replace(fact_3, source_field_id="structured.aaa_chapter_3")
    chapter_2_anchor_ids = set(chapter_2_fact.evidence_anchor_ids)
    chapter_3_anchor_ids = set(chapter_3_fact.evidence_anchor_ids)
    projection = replace(
        base_projection,
        chapters=(
            replace(
                chapter_2,
                facts=(chapter_2_fact,),
                evidence_anchors=tuple(
                    anchor for anchor in chapter_2.evidence_anchors if anchor.anchor_id in chapter_2_anchor_ids
                ),
            ),
            replace(
                chapter_3,
                facts=(chapter_3_fact,),
                evidence_anchors=tuple(
                    anchor for anchor in chapter_3.evidence_anchors if anchor.anchor_id in chapter_3_anchor_ids
                ),
            ),
        ),
    )
    references = tuple(
        _reference(anchor_id, excerpt_text=_excerpt_for_fact(fact))
        for fact in (chapter_2_fact, chapter_3_fact)
        for anchor_id in fact.evidence_anchor_ids
    )

    result = confirm_projection_evidence_v2(projection, references)

    assert tuple(item.source_field_id for item in result.fact_results) == (
        "structured.zzz_chapter_2",
        "structured.aaa_chapter_3",
    )


def test_v2_value_mismatch_hard_gate_fail_score_cap() -> None:
    """验证值不匹配 hard-gate fail 时 fact auditability_score <= 40。"""

    chapter, fact = _chapter_and_fact("structured.turnover_rate")
    references = (
        _reference(fact.evidence_anchor_ids[0], excerpt_text="年报只披露管理费率 1.20%。"),
    )

    result = confirm_chapter_evidence_v2(chapter, references)
    fact_result = result.fact_results[0]

    assert fact_result.status == "fail"
    assert fact_result.auditability_score <= 40


def test_v2_candidate_only_proof_failure_score_zero() -> None:
    """验证 candidate-only proof failure 时 fact auditability_score = 0。"""

    chapter, fact = _chapter_and_fact("structured.turnover_rate")
    references = (
        _reference(
            fact.evidence_anchor_ids[0],
            excerpt_text="年报披露换手率为 120%。",
            candidate_only=True,
        ),
    )

    result = confirm_chapter_evidence_v2(chapter, references)
    fact_result = result.fact_results[0]

    assert fact_result.status == "fail"
    assert fact_result.auditability_score == 0


def test_v2_aggregate_score_one_blocking_fact_cannot_report_pass_like_score() -> None:
    """验证一个阻塞 fact 时聚合分数不能报告 pass-like >= 70。"""

    chapter, fact = _chapter_and_fact("structured.turnover_rate")
    passing_fact = replace(
        fact,
        fact_id=f"{fact.fact_id}:pass",
        source_field_id="structured.aaa_pass_rate",
    )
    failing_fact = replace(
        fact,
        fact_id=f"{fact.fact_id}:fail",
        source_field_id="structured.bbb_fail_rate",
        value={"turnover_rate": "999%"},
    )
    chapter = replace(chapter, facts=(passing_fact, failing_fact))
    references = (
        _reference(fact.evidence_anchor_ids[0], excerpt_text="年报披露换手率为 120%。"),
    )

    result = confirm_chapter_evidence_v2(chapter, references)

    assert result.overall_status == "fail"
    assert result.auditability_score is not None
    assert result.auditability_score == 40


def test_v2_aggregate_score_e3_blocking_fact_caps_score_at_zero() -> None:
    """验证 E3 blocking fact 将聚合分数 cap 到 0。"""

    chapter, fact = _chapter_and_fact("structured.turnover_rate")
    passing_fact = replace(
        fact,
        fact_id=f"{fact.fact_id}:pass",
        source_field_id="structured.aaa_pass_rate",
    )
    failing_fact = replace(
        fact,
        fact_id=f"{fact.fact_id}:fail",
        source_field_id="structured.bbb_fail_rate",
        evidence_anchor_ids=("missing-anchor",),
    )
    chapter = replace(chapter, facts=(passing_fact, failing_fact))
    references = (
        _reference(fact.evidence_anchor_ids[0], excerpt_text="年报披露换手率为 120%。"),
    )

    result = confirm_chapter_evidence_v2(chapter, references)

    assert result.overall_status == "fail"
    assert result.auditability_score == 0


def test_v2_aggregate_score_all_passing_uses_uncapped_average() -> None:
    """验证全部通过时聚合分数使用 uncapped average。"""

    chapter, fact = _chapter_and_fact("structured.turnover_rate")
    fact2 = replace(
        fact,
        fact_id=f"{fact.fact_id}:b",
        source_field_id="structured.bbb_turnover_rate",
    )
    chapter = replace(chapter, facts=(fact, fact2))
    references = (
        _reference(fact.evidence_anchor_ids[0], excerpt_text="年报披露换手率为 120%。"),
    )

    result = confirm_chapter_evidence_v2(chapter, references)

    assert result.overall_status == "pass"
    assert result.auditability_score == 100


def test_v1_tests_still_pass() -> None:
    """验证 V1 公共行为不变。"""

    chapter, fact = _chapter_and_fact("structured.turnover_rate")
    result = confirm_chapter_evidence(
        chapter,
        (_reference(fact.evidence_anchor_ids[0], excerpt_text="年报披露换手率为 120%。"),),
    )

    assert result.schema_version == EVIDENCE_CONFIRM_SCHEMA_VERSION
    assert result.overall_status == "pass"
    assert result.auditability_score == 100


def _chapter_and_fact(source_field_id: str) -> tuple[ChapterFactInput, ChapterFactEntry]:
    """读取只含目标 fact 的测试章节。

    Args:
        source_field_id: 目标 source field id。

    Returns:
        只含目标 fact 的章节和 fact。

    Raises:
        AssertionError: 测试 fixture 未包含目标 fact 时抛出。
    """

    projection = project_chapter_facts(_bundle(), chapter_ids=(3,))
    chapter = projection.chapters[0]
    fact = next(item for item in chapter.facts if item.source_field_id == source_field_id)
    anchor_ids = set(fact.evidence_anchor_ids)
    anchors = tuple(anchor for anchor in chapter.evidence_anchors if anchor.anchor_id in anchor_ids)
    return replace(chapter, facts=(fact,), evidence_anchors=anchors), fact


def _available_facts(projection: object) -> tuple[ChapterFactEntry, ...]:
    """读取 projection 中有 anchor 的可用 fact。

    Args:
        projection: 章节事实投影。

    Returns:
        可用于聚合测试的 fact 元组。

    Raises:
        无显式抛出。
    """

    return tuple(
        fact
        for chapter in projection.chapters  # type: ignore[attr-defined]
        for fact in chapter.facts
        if fact.status == "available" and fact.evidence_anchor_ids
    )


def _reference(
    anchor_id: str,
    *,
    excerpt_text: str,
    reference_kind: str = "annual_report_excerpt",
    source_kind: str = "annual_report",
    document_year: int | None = 2024,
    page_number: int | None = 12,
    section_id: str | None = "§2",
    table_id: str | None = None,
    row_locator: str | None = None,
    candidate_only: bool = False,
    source_truth_status: str = "proven",
) -> EvidenceConfirmReference:
    """构造测试 reference。

    Args:
        anchor_id: anchor id。
        excerpt_text: 同源摘录。
        reference_kind: reference kind。
        source_kind: source kind。
        page_number: 页码。
        section_id: 章节。
        table_id: 表格 id。
        row_locator: 行定位。
        candidate_only: 是否 candidate-only。
        source_truth_status: proof 状态。

    Returns:
        测试 reference。

    Raises:
        无显式抛出。
    """

    return EvidenceConfirmReference(
        anchor_id=anchor_id,
        reference_kind=reference_kind,  # type: ignore[arg-type]
        source_kind=source_kind,
        document_year=document_year,
        section_id=section_id,
        page_number=page_number,
        table_id=table_id,
        row_locator=row_locator,
        excerpt_text=excerpt_text,
        source_truth_status=source_truth_status,  # type: ignore[arg-type]
        candidate_only=candidate_only,
    )


def _excerpt_for_fact(fact: ChapterFactEntry) -> str:
    """按测试 fact 构造包含 material token 的摘录。

    Args:
        fact: 章节事实。

    Returns:
        摘录文本。

    Raises:
        AssertionError: 测试 fact 没有 value 时抛出。
    """

    assert fact.value is not None
    return f"同源摘录：{fact.value}"
