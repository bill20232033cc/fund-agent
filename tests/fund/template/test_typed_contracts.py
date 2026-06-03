"""基金模板 typed CHAPTER_CONTRACT sidecar 测试。"""

from __future__ import annotations

from dataclasses import replace

import pytest

from fund_agent.fund.template import (
    AUDIT_FOCUS_IS_SEMANTIC_ONLY,
    EXPECTED_PUBLIC_CHAPTER_IDS,
    TYPED_TEMPLATE_CONTRACT_SCHEMA_VERSION,
    load_template_contract_manifest,
    load_typed_template_contract_manifest,
    validate_typed_template_contract_manifest,
)
from fund_agent.fund.template.typed_contracts import (
    ChapterInternalSubcontract,
    RequiredOutputItem,
)


def test_typed_manifest_preserves_public_chapter_ids_0_to_7() -> None:
    """验证 typed manifest 保持模板第 0-7 章公开编号。

    Args:
        无。

    Returns:
        无。

    Raises:
        AssertionError: typed manifest 公开章节编号、schema 或 Ch2 子契约边界不符合预期。
    """

    manifest = load_typed_template_contract_manifest()

    assert manifest.schema_version == TYPED_TEMPLATE_CONTRACT_SCHEMA_VERSION
    assert tuple(chapter.chapter_id for chapter in manifest.chapters) == EXPECTED_PUBLIC_CHAPTER_IDS
    assert len(manifest.chapters) == 8
    assert {sub.subcontract_id for sub in manifest.chapters[2].internal_subcontracts} == {
        "performance",
        "attribution",
        "cost",
    }
    assert all(not chapter.internal_subcontracts for chapter in manifest.chapters if chapter.chapter_id != 2)


def test_typed_manifest_rejects_ch2_public_subchapter_ids() -> None:
    """验证 Ch2 子契约不得携带公开 chapter_id。

    Args:
        无。

    Returns:
        无。

    Raises:
        AssertionError: 非法 Ch2 public subchapter id 未被 fail-closed 拒绝。
    """

    manifest = load_typed_template_contract_manifest()
    chapter_2 = manifest.chapters[2]
    illegal_subcontract = replace(chapter_2.internal_subcontracts[0], public_chapter_id=20)
    illegal_chapter_2 = replace(
        chapter_2,
        internal_subcontracts=(illegal_subcontract, *chapter_2.internal_subcontracts[1:]),
    )
    illegal_manifest = _replace_typed_chapter(manifest, 2, illegal_chapter_2)

    with pytest.raises(ValueError, match="内部子契约不得携带公开 chapter_id"):
        validate_typed_template_contract_manifest(illegal_manifest)

    public_split_chapter = replace(chapter_2, chapter_id=20, internal_subcontracts=())
    illegal_public_split = replace(manifest, chapters=(*manifest.chapters, public_split_chapter))
    with pytest.raises(ValueError, match="公开章节 id 必须精确覆盖 0..7"):
        validate_typed_template_contract_manifest(illegal_public_split)


def test_ch0_consumes_ch7_and_has_no_independent_action_source() -> None:
    """验证第 0 章只消费第 7 章最终判断，不独立派生动作。

    Args:
        无。

    Returns:
        无。

    Raises:
        AssertionError: 第 0 章依赖或独立动作来源字段不符合预期。
    """

    manifest = load_typed_template_contract_manifest()
    chapter_0 = manifest.chapters[0]

    assert chapter_0.consumes_chapter_conclusions == (7,)
    assert chapter_0.independent_action_source is False

    missing_ch7 = _replace_typed_chapter(
        manifest,
        0,
        replace(chapter_0, consumes_chapter_conclusions=()),
    )
    with pytest.raises(ValueError, match="第 0 章必须消费第 7 章"):
        validate_typed_template_contract_manifest(missing_ch7)

    independent_action = _replace_typed_chapter(
        manifest,
        0,
        replace(chapter_0, independent_action_source=True),
    )
    with pytest.raises(ValueError, match="第 0 章不得独立派生动作判断"):
        validate_typed_template_contract_manifest(independent_action)


def test_required_output_item_ids_are_unique() -> None:
    """验证 required output item id 必须唯一。

    Args:
        无。

    Returns:
        无。

    Raises:
        AssertionError: 重复 required output item id 未被拒绝。
    """

    manifest = load_typed_template_contract_manifest()
    chapter_1 = manifest.chapters[1]
    duplicate = RequiredOutputItem(
        item_id=chapter_1.required_output_items[0].item_id,
        text="duplicate fixture",
    )
    illegal_chapter = replace(
        chapter_1,
        required_output_items=(duplicate, *chapter_1.required_output_items),
    )
    illegal_manifest = _replace_typed_chapter(manifest, 1, illegal_chapter)

    with pytest.raises(ValueError, match="required_output item_id 存在重复"):
        validate_typed_template_contract_manifest(illegal_manifest)


def test_audit_focus_literals_are_closed_and_do_not_imply_programmatic_disable() -> None:
    """验证 audit_focus 是闭集语义数据，不暗示关闭程序审计。

    Args:
        无。

    Returns:
        无。

    Raises:
        AssertionError: audit_focus 闭集或语义边界不符合预期。
    """

    manifest = load_typed_template_contract_manifest()

    assert AUDIT_FOCUS_IS_SEMANTIC_ONLY is True
    assert manifest.chapters[3].audit_focus == ("manager_consistency", "evidence_anchors")
    assert manifest.chapters[3].must_not_cover[3].applies_when is not None
    assert manifest.chapters[3].must_not_cover[3].allowed_contexts == (
        "required_label",
        "evidence_gap_statement",
        "quote",
        "anchor_caption",
    )

    illegal_chapter = replace(manifest.chapters[3], audit_focus=("disable_programmatic",))  # type: ignore[arg-type]
    illegal_manifest = _replace_typed_chapter(manifest, 3, illegal_chapter)
    with pytest.raises(ValueError, match="audit_focus 不受支持"):
        validate_typed_template_contract_manifest(illegal_manifest)


def test_typed_contract_loader_does_not_mutate_current_manifest() -> None:
    """验证 typed loader 不改变当前 `contracts.py` manifest。

    Args:
        无。

    Returns:
        无。

    Raises:
        AssertionError: typed loader 改变当前 manifest 对象或章节内容。
    """

    current_manifest = load_template_contract_manifest()
    before = tuple(
        (
            chapter.chapter_id,
            chapter.title,
            chapter.must_answer,
            chapter.must_not_cover,
            chapter.required_output_items,
        )
        for chapter in current_manifest.chapters
    )

    typed_manifest = load_typed_template_contract_manifest()

    after_manifest = load_template_contract_manifest()
    after = tuple(
        (
            chapter.chapter_id,
            chapter.title,
            chapter.must_answer,
            chapter.must_not_cover,
            chapter.required_output_items,
        )
        for chapter in after_manifest.chapters
    )
    assert after_manifest is current_manifest
    assert before == after
    assert typed_manifest.chapters[0].must_answer[0].text == current_manifest.chapters[0].must_answer[0]


def test_unknown_dependency_ids_fail_closed() -> None:
    """验证未知章节依赖 id fail-closed。

    Args:
        无。

    Returns:
        无。

    Raises:
        AssertionError: 未知 dependency id 未被拒绝。
    """

    manifest = load_typed_template_contract_manifest()
    illegal_manifest = _replace_typed_chapter(
        manifest,
        0,
        replace(manifest.chapters[0], consumes_chapter_conclusions=(7, 99)),
    )

    with pytest.raises(ValueError, match="未知 dependency id"):
        validate_typed_template_contract_manifest(illegal_manifest)


def test_non_ch2_internal_subcontracts_fail_closed() -> None:
    """验证非第 2 章不得出现内部子契约。

    Args:
        无。

    Returns:
        无。

    Raises:
        AssertionError: 非 Ch2 内部子契约未被拒绝。
    """

    manifest = load_typed_template_contract_manifest()
    illegal_chapter = replace(
        manifest.chapters[1],
        internal_subcontracts=(
            ChapterInternalSubcontract(
                subcontract_id="illegal",
                title="非法子契约",
                requirement_ids=("ch1.must_answer.item_01",),
            ),
        ),
    )
    illegal_manifest = _replace_typed_chapter(manifest, 1, illegal_chapter)

    with pytest.raises(ValueError, match="不允许内部子契约"):
        validate_typed_template_contract_manifest(illegal_manifest)


def _replace_typed_chapter(manifest, chapter_id, replacement):
    """替换 typed manifest 中的单章契约。

    Args:
        manifest: 原 typed manifest。
        chapter_id: 待替换章节编号。
        replacement: 替换后的章节契约。

    Returns:
        替换后的 typed manifest。

    Raises:
        无。
    """

    return replace(
        manifest,
        chapters=tuple(
            replacement if chapter.chapter_id == chapter_id else chapter
            for chapter in manifest.chapters
        ),
    )
