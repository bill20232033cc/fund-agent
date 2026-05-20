"""基金模板 CHAPTER_CONTRACT manifest 测试。"""

from __future__ import annotations

from dataclasses import replace

import pytest

from fund_agent.fund.fund_type import FundType
from fund_agent.fund.template import (
    ChapterContract,
    TemplateContractManifest,
    TemplateLensRule,
    get_chapter_contract,
    load_template_contract_manifest,
    resolve_preferred_lens,
    validate_template_contract_manifest,
)

_SUPPORTED_FUND_TYPES: tuple[FundType, ...] = (
    "index_fund",
    "active_fund",
    "bond_fund",
    "enhanced_index",
    "qdii_fund",
    "fof_fund",
)

_EXPECTED_TITLES: tuple[str, ...] = (
    "投资要点概览",
    "这只基金到底是什么产品",
    "R=A+B-C 收益归因",
    "基金经理画像与言行一致性",
    "投资者获得感",
    "当前阶段与关键变化",
    "核心风险与否决项",
    "是否值得持有——最终判断",
)


def test_load_template_contract_manifest_returns_eight_contiguous_chapters() -> None:
    """验证 manifest 覆盖模板第 0-7 章。

    Args:
        无。

    Returns:
        无。

    Raises:
        AssertionError: manifest 章节数量或编号不符合预期。
    """

    manifest = load_template_contract_manifest()

    assert len(manifest.chapters) == 8
    assert tuple(chapter.chapter_id for chapter in manifest.chapters) == tuple(range(8))


def test_chapter_titles_match_design_and_not_renderer_private_constant() -> None:
    """验证章节标题来自公开设计预期，不耦合渲染器私有常量。

    Args:
        无。

    Returns:
        无。

    Raises:
        AssertionError: 标题不符合 `docs/design.md` 第 3.1 节预期。
    """

    manifest = load_template_contract_manifest()

    assert tuple(chapter.title for chapter in manifest.chapters) == _EXPECTED_TITLES


def test_every_chapter_has_non_empty_contract_fields() -> None:
    """验证每章 CHAPTER_CONTRACT 必需字段非空。

    Args:
        无。

    Returns:
        无。

    Raises:
        AssertionError: 任一章节字段为空。
    """

    manifest = load_template_contract_manifest()

    for chapter in manifest.chapters:
        assert chapter.narrative_mode
        assert chapter.must_answer
        assert chapter.must_not_cover
        assert chapter.required_output_items
        assert chapter.preferred_lens


def test_every_supported_fund_type_resolves_lens_for_every_chapter() -> None:
    """验证所有标准基金类型在每章都能解析 preferred_lens。

    Args:
        无。

    Returns:
        无。

    Raises:
        AssertionError: 任一基金类型无法解析 lens。
    """

    for chapter_id in range(8):
        for fund_type in _SUPPORTED_FUND_TYPES:
            lens = resolve_preferred_lens(chapter_id, fund_type)
            assert lens.fund_type in (fund_type, "default")
            assert lens.statements


def test_validate_template_contract_manifest_fails_closed_for_invalid_cases() -> None:
    """验证 manifest 校验对典型漂移场景 fail closed。

    Args:
        无。

    Returns:
        无。

    Raises:
        AssertionError: 非法 manifest 未抛出 `ValueError`。
    """

    manifest = load_template_contract_manifest()

    duplicate_id = replace(
        manifest,
        chapters=(replace(manifest.chapters[0], chapter_id=1), *manifest.chapters[1:]),
    )
    with pytest.raises(ValueError, match="重复|连续"):
        validate_template_contract_manifest(duplicate_id)

    missing_id = replace(manifest, chapters=manifest.chapters[:-1])
    with pytest.raises(ValueError, match="章节数量"):
        validate_template_contract_manifest(missing_id)

    empty_must_answer = _replace_chapter(
        manifest,
        0,
        replace(manifest.chapters[0], must_answer=()),
    )
    with pytest.raises(ValueError, match="must_answer"):
        validate_template_contract_manifest(empty_must_answer)

    unsupported_lens_key = _replace_chapter(
        manifest,
        0,
        replace(
            manifest.chapters[0],
            preferred_lens={
                **dict(manifest.chapters[0].preferred_lens),
                "money_market_fund": TemplateLensRule(
                    fund_type="default",
                    statements=("非法 lens key fixture",),
                ),
            },
        ),
    )
    with pytest.raises(ValueError, match="不支持的 lens key"):
        validate_template_contract_manifest(unsupported_lens_key)

    lens_key_fund_type_mismatch = _replace_chapter(
        manifest,
        0,
        replace(
            manifest.chapters[0],
            preferred_lens={
                **dict(manifest.chapters[0].preferred_lens),
                "index_fund": TemplateLensRule(
                    fund_type="default",
                    statements=("lens key 与 fund_type 不一致 fixture",),
                ),
            },
        ),
    )
    with pytest.raises(ValueError, match="不一致"):
        validate_template_contract_manifest(lens_key_fund_type_mismatch)

    unsupported_priority = _replace_chapter(
        manifest,
        0,
        replace(
            manifest.chapters[0],
            preferred_lens={
                **dict(manifest.chapters[0].preferred_lens),
                "default": TemplateLensRule(
                    fund_type="default",
                    statements=("priority 闭集校验 fixture",),
                    priority="urgent",
                ),
            },
        ),
    )
    with pytest.raises(ValueError, match="priority 不受支持"):
        validate_template_contract_manifest(unsupported_priority)


def test_get_chapter_contract_zero_returns_cover_contract() -> None:
    """验证第 0 章契约可按编号读取。

    Args:
        无。

    Returns:
        无。

    Raises:
        AssertionError: 第 0 章契约内容不符合预期。
    """

    chapter = get_chapter_contract(0)

    assert chapter.chapter_id == 0
    assert chapter.title == "投资要点概览"
    assert "下一步最小验证问题" in chapter.required_output_items


def test_resolve_preferred_lens_fails_without_exact_or_default_fallback() -> None:
    """验证缺少 exact/default lens fallback 时抛出异常。

    Args:
        无。

    Returns:
        无。

    Raises:
        AssertionError: 缺少 lens fallback 的章节未抛出 `ValueError`。
    """

    chapter = ChapterContract(
        chapter_id=0,
        title="投资要点概览",
        narrative_mode="封面→动作→验证",
        must_answer=("fixture",),
        must_not_cover=("fixture",),
        required_output_items=("fixture",),
        preferred_lens={
            "index_fund": TemplateLensRule(
                fund_type="index_fund",
                statements=("fixture",),
            ),
        },
    )
    manifest = TemplateContractManifest(
        template_id="fixture",
        source_path="fixture.md",
        chapters=(chapter, *_shift_chapters(load_template_contract_manifest().chapters[1:])),
    )

    with pytest.raises(ValueError, match="fallback"):
        validate_template_contract_manifest(manifest)


def _replace_chapter(
    manifest: TemplateContractManifest,
    chapter_id: int,
    replacement: ChapterContract,
) -> TemplateContractManifest:
    """替换 manifest 中的单个章节契约。

    Args:
        manifest: 原始 manifest。
        chapter_id: 待替换章节编号。
        replacement: 替换后的章节契约。

    Returns:
        替换单章后的 manifest。

    Raises:
        无显式抛出。
    """

    chapters = tuple(
        replacement if chapter.chapter_id == chapter_id else chapter for chapter in manifest.chapters
    )
    return replace(manifest, chapters=chapters)


def _shift_chapters(chapters: tuple[ChapterContract, ...]) -> tuple[ChapterContract, ...]:
    """保留章节夹具元组。

    Args:
        chapters: 原始章节元组。

    Returns:
        原样返回的章节元组。

    Raises:
        无显式抛出。
    """

    return chapters
