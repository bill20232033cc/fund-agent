"""CHAPTER_CONTRACT 可执行 sidecar 测试。"""

from __future__ import annotations

from fund_agent.fund.template.chapter_contract_constraints import (
    ACTIVE_CHAPTER_3_TURNOVER_REQUIREMENT_ID,
    BOND_CHAPTER_6_REQUIREMENT_ID,
    ENHANCED_INDEX_CHAPTER_2_REQUIREMENT_ID,
    TURNOVER_STYLE_GAP_REASON_CODES,
    TURNOVER_STYLE_REQUIRED_WORDING_FRAGMENTS,
    constraints_for_chapter,
    load_chapter_contract_constraint_manifest,
    map_requirement_severity_to_issue_severity,
)
from fund_agent.fund.template.contracts import load_template_contract_manifest
from fund_agent.fund.template.typed_contracts import load_typed_template_contract_manifest


def test_sidecar_covers_all_chapter_ids_0_to_7() -> None:
    """验证 sidecar 覆盖模板第 0-7 章。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: sidecar 章节覆盖与模板 manifest 不一致时抛出。
    """

    source_manifest = load_template_contract_manifest()
    sidecar_manifest = load_chapter_contract_constraint_manifest()

    assert {constraint.chapter_id for constraint in sidecar_manifest.constraints} == set(range(8))
    assert {chapter.chapter_id for chapter in source_manifest.chapters} == set(range(8))


def test_sidecar_wraps_existing_chapter_contract_without_parallel_truth() -> None:
    """验证 sidecar 默认约束只包裹既有 CHAPTER_CONTRACT。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 默认 wrapper 与模板真源字段不一致时抛出。
    """

    source_by_id = {
        chapter.chapter_id: chapter
        for chapter in load_template_contract_manifest().chapters
    }
    typed_by_id = {
        chapter.chapter_id: chapter
        for chapter in load_typed_template_contract_manifest().chapters
    }
    sidecar_manifest = load_chapter_contract_constraint_manifest()
    default_constraints = {
        constraint.chapter_id: constraint
        for constraint in sidecar_manifest.constraints
        if constraint.fund_type_slot == "default"
    }

    assert tuple(sorted(default_constraints)) == tuple(range(8))
    for chapter_id, constraint in default_constraints.items():
        assert constraint.must_answer == source_by_id[chapter_id].must_answer
        assert constraint.must_not_cover == source_by_id[chapter_id].must_not_cover
        assert constraint.must_answer == tuple(item.text for item in typed_by_id[chapter_id].must_answer)
        assert constraint.must_not_cover == tuple(item.text for item in typed_by_id[chapter_id].must_not_cover)

    active_constraints = constraints_for_chapter(3, "active_fund")
    assert tuple(constraint.fund_type_slot for constraint in active_constraints) == (
        "default",
        "active_fund",
    )
    assert active_constraints[0].must_answer == source_by_id[3].must_answer
    assert active_constraints[1].must_answer == source_by_id[3].must_answer


def test_active_chapter_3_turnover_requirement_is_material() -> None:
    """验证主动基金第 3 章换手率/风格一致性证据约束为 material。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: material 约束字段不完整时抛出。
    """

    constraints = constraints_for_chapter(3, "active_fund")
    active_constraint = next(
        constraint for constraint in constraints if constraint.fund_type_slot == "active_fund"
    )
    requirement = next(
        item
        for item in active_constraint.required_evidence
        if item.requirement_id == ACTIVE_CHAPTER_3_TURNOVER_REQUIREMENT_ID
    )

    assert requirement.severity == "material"
    assert requirement.deferred is False
    assert requirement.accepted_fact_ids
    assert requirement.accepted_gap_reason_codes == TURNOVER_STYLE_GAP_REASON_CODES
    assert requirement.required_wording_fragments == TURNOVER_STYLE_REQUIRED_WORDING_FRAGMENTS
    assert active_constraint.failure_behavior == "material"


def test_chapter_2_and_6_deferred_requirements_are_config_only() -> None:
    """验证增强指数第 2 章与债券第 6 章要求只作为 deferred config。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: deferred 要求错误升级为 material/blocking 时抛出。
    """

    chapter_2 = constraints_for_chapter(2, "enhanced_index")
    chapter_6 = constraints_for_chapter(6, "bond_fund")
    enhanced_requirement = next(
        requirement
        for constraint in chapter_2
        for requirement in constraint.required_evidence
        if requirement.requirement_id == ENHANCED_INDEX_CHAPTER_2_REQUIREMENT_ID
    )
    bond_requirement = next(
        requirement
        for constraint in chapter_6
        for requirement in constraint.required_evidence
        if requirement.requirement_id == BOND_CHAPTER_6_REQUIREMENT_ID
    )

    assert enhanced_requirement.deferred is True
    assert enhanced_requirement.severity == "config_only"
    assert map_requirement_severity_to_issue_severity(enhanced_requirement.severity) == "informational"
    assert bond_requirement.deferred is True
    assert bond_requirement.severity == "config_only"
    assert map_requirement_severity_to_issue_severity(bond_requirement.severity) == "informational"
