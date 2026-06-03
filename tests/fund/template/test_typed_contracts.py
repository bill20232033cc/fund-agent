"""基金模板 typed CHAPTER_CONTRACT sidecar 测试。"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from typing import Any, Mapping

import pytest

from fund_agent.fund.template import (
    AUDIT_FOCUS_IS_SEMANTIC_ONLY,
    EXPECTED_PUBLIC_CHAPTER_IDS,
    TYPED_TEMPLATE_CONTRACT_SCHEMA_VERSION,
    load_template_contract_manifest,
    load_typed_template_contract_manifest,
    validate_typed_template_contract_manifest,
)
from fund_agent.fund.template import typed_contracts
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


def test_typed_contracts_has_no_code_authored_text_mapping_truth() -> None:
    """验证 typed_contracts.py 不再保留代码 authored stable id/text 真源。

    Args:
        无。

    Returns:
        无。

    Raises:
        AssertionError: 旧 authored truth symbol 仍残留在 typed_contracts.py。
    """

    source = Path(typed_contracts.__file__).read_text(encoding="utf-8")

    assert "_CURRENT_TEXT_MAPPING" not in source
    assert "_TextIdMapping" not in source
    assert "_ChapterTextMapping" not in source
    assert "_AUDIT_FOCUS_BY_CHAPTER" not in source
    assert "_CH3_STYLE_EVIDENCE_UNREVIEWED" not in source


def test_current_typed_projection_matches_template_json_exact_fields() -> None:
    """验证 typed manifest 精确投影模板 JSON 中的 id、文本和 typed 侧字段。

    Args:
        无。

    Returns:
        无。

    Raises:
        AssertionError: typed manifest 与 canonical JSON 不一致。
    """

    raw_manifest = typed_contracts._load_raw_template_contract_manifest()
    typed_manifest = load_typed_template_contract_manifest()

    assert typed_manifest.schema_version == raw_manifest["schema_version"]
    assert typed_manifest.template_id == raw_manifest["template_id"]
    assert typed_manifest.source_template_id == raw_manifest["source_template_id"]
    assert typed_manifest.source_path == raw_manifest["source_path"]

    for typed_chapter, raw_chapter in zip(typed_manifest.chapters, raw_manifest["chapters"], strict=True):
        assert typed_chapter.chapter_id == raw_chapter["chapter_id"]
        assert typed_chapter.title == raw_chapter["title"]
        assert typed_chapter.narrative_mode == raw_chapter["narrative_mode"]
        assert tuple((item.clause_id, item.text) for item in typed_chapter.must_answer) == tuple(
            (item["id"], item["text"]) for item in raw_chapter["must_answer"]
        )
        assert tuple((item.item_id, item.text) for item in typed_chapter.required_output_items) == tuple(
            (item["id"], item["text"]) for item in raw_chapter["required_output_items"]
        )
        assert tuple(
            (item.when_evidence_missing, item.missing_evidence_reason)
            for item in typed_chapter.required_output_items
        ) == tuple(
            (item["when_evidence_missing"], item["missing_evidence_reason"])
            for item in raw_chapter["required_output_items"]
        )
        assert typed_chapter.audit_focus == tuple(raw_chapter["audit_focus"])
        assert typed_chapter.consumes_chapter_conclusions == tuple(
            raw_chapter["consumes_chapter_conclusions"]
        )
        assert typed_chapter.independent_action_source == raw_chapter["independent_action_source"]
        assert tuple(
            (item.subcontract_id, item.title, item.requirement_ids, item.public_chapter_id)
            for item in typed_chapter.internal_subcontracts
        ) == tuple(
            (
                item["subcontract_id"],
                item["title"],
                tuple(item["requirement_ids"]),
                item["public_chapter_id"],
            )
            for item in raw_chapter["internal_subcontracts"]
        )

    raw_ch3_predicate = raw_manifest["chapters"][3]["must_not_cover"][3]["applies_when"]
    typed_ch3_predicate = typed_manifest.chapters[3].must_not_cover[3].applies_when
    assert typed_ch3_predicate is not None
    assert typed_ch3_predicate.predicate_id == raw_ch3_predicate["predicate_id"]
    assert typed_ch3_predicate.requirement_ids == tuple(raw_ch3_predicate["requirement_ids"])
    assert typed_ch3_predicate.required_statuses == tuple(raw_ch3_predicate["required_statuses"])
    assert typed_ch3_predicate.description == raw_ch3_predicate["description"]


def test_stale_source_manifest_raises_value_error() -> None:
    """验证 source_manifest 只做 compatibility validation，stale 输入 fail-closed。

    Args:
        无。

    Returns:
        无。

    Raises:
        AssertionError: stale source_manifest 未触发 ValueError。
    """

    current_manifest = load_template_contract_manifest()
    stale_chapter = replace(current_manifest.chapters[0], title="stale title")
    stale_manifest = replace(
        current_manifest,
        chapters=(stale_chapter, *current_manifest.chapters[1:]),
    )

    with pytest.raises(ValueError, match="source_manifest 与当前模板文档投影不一致"):
        load_typed_template_contract_manifest(stale_manifest)


def test_changing_template_json_changes_projected_typed_manifest(monkeypatch: pytest.MonkeyPatch) -> None:
    """验证 typed manifest 来自模板 JSON，而不是 source_manifest 或代码 mapping。

    Args:
        monkeypatch: pytest monkeypatch fixture。

    Returns:
        无。

    Raises:
        AssertionError: raw JSON 合法变化未反映到 typed manifest。
    """

    raw_manifest = _mutable_raw_manifest()
    raw_manifest["chapters"][0]["must_answer"][0]["text"] = "测试用模板 JSON 改写后的第一条"
    monkeypatch.setattr(typed_contracts, "_load_raw_template_contract_manifest", lambda: raw_manifest)

    typed_manifest = load_typed_template_contract_manifest()

    assert typed_manifest.chapters[0].must_answer[0].text == "测试用模板 JSON 改写后的第一条"


def test_unknown_template_requirement_id_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    """验证模板 JSON 中未知 EvidenceRequirementId 会 fail-closed。

    Args:
        monkeypatch: pytest monkeypatch fixture。

    Returns:
        无。

    Raises:
        AssertionError: 未知 evidence requirement id 未被拒绝。
    """

    raw_manifest = _mutable_raw_manifest()
    raw_manifest["chapters"][3]["must_not_cover"][3]["applies_when"]["requirement_ids"] = [
        "ch3.requirement.unknown_reviewed"
    ]
    monkeypatch.setattr(typed_contracts, "_load_raw_template_contract_manifest", lambda: raw_manifest)

    with pytest.raises(ValueError, match="evidence predicate requirement_id 不受支持"):
        load_typed_template_contract_manifest()


def test_malformed_typed_values_fail_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    """验证 malformed typed-only JSON 值会在 typed validation 中 fail-closed。

    Args:
        monkeypatch: pytest monkeypatch fixture。

    Returns:
        无。

    Raises:
        AssertionError: 非法 typed 值未被拒绝。
    """

    raw_manifest = _mutable_raw_manifest()
    raw_manifest["chapters"][3]["required_output_items"][1]["when_evidence_missing"] = "silent_skip"
    monkeypatch.setattr(typed_contracts, "_load_raw_template_contract_manifest", lambda: raw_manifest)

    with pytest.raises(ValueError, match="missing evidence behavior 不受支持"):
        load_typed_template_contract_manifest()


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


def _mutable_raw_manifest() -> dict[str, Any]:
    """读取当前模板 JSON，并返回可修改副本。

    Args:
        无。

    Returns:
        当前 raw template manifest 的深拷贝。

    Raises:
        AssertionError: raw manifest 不是 dict 时抛出。
    """

    raw_manifest: Mapping[str, Any] = typed_contracts._load_raw_template_contract_manifest()
    mutable = deepcopy(raw_manifest)
    assert isinstance(mutable, dict)
    return mutable


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
