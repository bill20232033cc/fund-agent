"""基金模板 CHAPTER_CONTRACT manifest 测试。"""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path
from typing import Any

import pytest

from fund_agent.fund.fund_type import FundType
from fund_agent.fund.template import contracts as contracts_module
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


def test_current_untyped_manifest_projects_slice1_template_json_values() -> None:
    """验证当前未类型化 manifest 逐项投影 Slice 1 模板 JSON。

    Args:
        无。

    Returns:
        无。

    Raises:
        AssertionError: 当前 manifest 未精确投影模板 JSON 中的章节文本或 lens 值。
    """

    raw_manifest = _current_template_json()
    manifest = load_template_contract_manifest()

    assert manifest.template_id == raw_manifest["source_template_id"]
    assert manifest.source_path == raw_manifest["source_path"]
    assert tuple(chapter.chapter_id for chapter in manifest.chapters) == tuple(
        raw_manifest["public_chapter_ids"]
    )

    for chapter, raw_chapter in zip(manifest.chapters, raw_manifest["chapters"], strict=True):
        assert chapter.chapter_id == raw_chapter["chapter_id"]
        assert chapter.title == raw_chapter["title"]
        assert chapter.narrative_mode == raw_chapter["narrative_mode"]
        assert chapter.must_answer == tuple(item["text"] for item in raw_chapter["must_answer"])
        assert chapter.must_not_cover == tuple(
            item["text"] for item in raw_chapter["must_not_cover"]
        )
        assert chapter.required_output_items == tuple(
            item["text"] for item in raw_chapter["required_output_items"]
        )
        assert tuple(chapter.preferred_lens) == tuple(raw_chapter["preferred_lens"])
        for lens_key, raw_rule in raw_chapter["preferred_lens"].items():
            projected_rule = chapter.preferred_lens[lens_key]
            assert projected_rule.fund_type == raw_rule["fund_type"]
            assert projected_rule.statements == tuple(raw_rule["statements"])
            assert projected_rule.facets_any == tuple(raw_rule["facets_any"])
            assert projected_rule.priority == raw_rule["priority"]


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


@pytest.mark.parametrize(
    ("markdown_text", "expected_message"),
    (
        ("# no block\n", "缺少 TEMPLATE_CONTRACT_MANIFEST_JSON"),
        ("TEMPLATE_CONTRACT_MANIFEST_JSON\n\nEND_TEMPLATE_CONTRACT_MANIFEST_JSON\n", "不能为空"),
        (
            "TEMPLATE_CONTRACT_MANIFEST_JSON\n{}\nEND_TEMPLATE_CONTRACT_MANIFEST_JSON\n"
            "TEMPLATE_CONTRACT_MANIFEST_JSON\n{}\nEND_TEMPLATE_CONTRACT_MANIFEST_JSON\n",
            "exactly one",
        ),
        (
            "TEMPLATE_CONTRACT_MANIFEST_JSON\n{not-json}\nEND_TEMPLATE_CONTRACT_MANIFEST_JSON\n",
            "不是合法 JSON",
        ),
    ),
)
def test_template_doc_parser_fails_closed_for_missing_empty_duplicate_or_malformed_json(
    tmp_path: Path,
    markdown_text: str,
    expected_message: str,
) -> None:
    """验证模板 JSON block 缺失、重复、空值或非法 JSON 时 fail closed。

    Args:
        tmp_path: pytest 临时目录。
        markdown_text: 待写入临时模板的 Markdown 内容。
        expected_message: 期望错误信息片段。

    Returns:
        无。

    Raises:
        AssertionError: 非法模板未抛出 `ValueError`。
    """

    template_path = _write_template_markdown(tmp_path, markdown_text)

    with pytest.raises(ValueError, match=expected_message):
        contracts_module._load_template_contract_manifest_from_path(template_path)


@pytest.mark.parametrize(
    ("mutator", "expected_message"),
    (
        (
            lambda manifest: manifest.update({"unexpected": "value"}),
            "manifest 存在未知字段",
        ),
        (
            lambda manifest: manifest["chapters"][0].update({"unexpected": "value"}),
            r"chapters\[0\] 存在未知字段",
        ),
        (
            lambda manifest: manifest["chapters"][0]["preferred_lens"]["default"].update(
                {"unexpected": "value"}
            ),
            r"preferred_lens.default 存在未知字段",
        ),
        (
            lambda manifest: manifest["chapters"][0]["must_answer"][0].update(
                {"unexpected": "value"}
            ),
            r"must_answer\[0\] 存在未知字段",
        ),
        (
            lambda manifest: manifest["chapters"][0]["must_not_cover"][0].update(
                {"unexpected": "value"}
            ),
            r"must_not_cover\[0\] 存在未知字段",
        ),
        (
            lambda manifest: manifest["chapters"][0]["required_output_items"][0].update(
                {"unexpected": "value"}
            ),
            r"required_output_items\[0\] 存在未知字段",
        ),
    ),
)
def test_template_doc_parser_rejects_unknown_keys_at_nested_levels(
    tmp_path: Path,
    mutator: Any,
    expected_message: str,
) -> None:
    """验证顶层、章节、lens 和 item 层 unknown keys 均 fail closed。

    Args:
        tmp_path: pytest 临时目录。
        mutator: 修改模板 JSON 的测试函数。
        expected_message: 期望错误信息片段。

    Returns:
        无。

    Raises:
        AssertionError: unknown key 未触发 `ValueError`。
    """

    manifest = _current_template_json()
    mutator(manifest)
    template_path = _write_manifest_template(tmp_path, manifest)

    with pytest.raises(ValueError, match=expected_message):
        contracts_module._load_template_contract_manifest_from_path(template_path)


@pytest.mark.parametrize(
    ("mutator", "expected_message"),
    (
        (
            lambda manifest: manifest.__setitem__("public_chapter_ids", [0, 1, 2]),
            "public_chapter_ids",
        ),
        (
            lambda manifest: manifest["chapters"][1].__setitem__("chapter_id", 7),
            r"chapters\[1\].chapter_id",
        ),
        (
            lambda manifest: manifest["chapters"][0]["must_answer"][0].__setitem__(
                "id",
                "ch0.must_answer.item_99",
            ),
            "stable id",
        ),
        (
            lambda manifest: manifest["chapters"][0]["must_answer"][0].__setitem__(
                "text",
                "",
            ),
            r"must_answer\[0\].text",
        ),
        (
            lambda manifest: manifest["chapters"][0]["preferred_lens"].__setitem__(
                "money_market_fund",
                {
                    "fund_type": "money_market_fund",
                    "statements": ["非法基金类型"],
                    "facets_any": [],
                    "priority": "core",
                },
            ),
            "不支持的 lens key",
        ),
        (
            lambda manifest: manifest["chapters"][0]["preferred_lens"]["index_fund"].__setitem__(
                "fund_type",
                "default",
            ),
            "fund_type 必须等于 lens key",
        ),
        (
            lambda manifest: manifest["chapters"][0]["preferred_lens"]["default"].__setitem__(
                "priority",
                "urgent",
            ),
            "priority.*不受支持",
        ),
        (
            lambda manifest: manifest["chapters"][0]["required_output_items"][0].__setitem__(
                "when_evidence_missing",
                "invent",
            ),
            "when_evidence_missing 不受支持",
        ),
    ),
)
def test_template_doc_parser_rejects_chapter_id_id_text_and_lens_drift(
    tmp_path: Path,
    mutator: Any,
    expected_message: str,
) -> None:
    """验证章节 id、stable id、text shape、lens key/priority 漂移均 fail closed。

    Args:
        tmp_path: pytest 临时目录。
        mutator: 修改模板 JSON 的测试函数。
        expected_message: 期望错误信息片段。

    Returns:
        无。

    Raises:
        AssertionError: 非法模板未触发 `ValueError`。
    """

    manifest = _current_template_json()
    mutator(manifest)
    template_path = _write_manifest_template(tmp_path, manifest)

    with pytest.raises(ValueError, match=expected_message):
        contracts_module._load_template_contract_manifest_from_path(template_path)


def test_template_doc_parser_cache_is_path_keyed_and_clearable(tmp_path: Path) -> None:
    """验证模板 manifest cache 按路径隔离且可清理。

    Args:
        tmp_path: pytest 临时目录。

    Returns:
        无。

    Raises:
        AssertionError: cache 未按路径隔离或清理后未重新读取文件。
    """

    first_manifest = _current_template_json()
    second_manifest = _current_template_json()
    first_manifest["chapters"][0]["title"] = "缓存路径 A"
    second_manifest["chapters"][0]["title"] = "缓存路径 B"
    first_path = _write_manifest_template(tmp_path / "a", first_manifest)
    second_path = _write_manifest_template(tmp_path / "b", second_manifest)

    first_projection = contracts_module._load_template_contract_manifest_from_path(first_path)
    second_projection = contracts_module._load_template_contract_manifest_from_path(second_path)

    assert first_projection.chapters[0].title == "缓存路径 A"
    assert second_projection.chapters[0].title == "缓存路径 B"

    first_manifest["chapters"][0]["title"] = "缓存路径 A 已更新"
    first_path.write_text(_manifest_markdown(first_manifest), encoding="utf-8")

    cached_projection = contracts_module._load_template_contract_manifest_from_path(first_path)
    assert cached_projection.chapters[0].title == "缓存路径 A"

    contracts_module._clear_template_contract_manifest_cache()
    refreshed_projection = contracts_module._load_template_contract_manifest_from_path(first_path)
    assert refreshed_projection.chapters[0].title == "缓存路径 A 已更新"


def test_template_contracts_module_cli_validate_template_doc() -> None:
    """验证 no-provider 本地模板校验路径可用。

    Args:
        无。

    Returns:
        无。

    Raises:
        AssertionError: 模块 CLI 校验入口返回非 0。
    """

    assert contracts_module._main(["--validate-template-doc"]) == 0


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


def test_current_stage_contract_separates_change_facts_from_risk_and_final_judgment() -> None:
    """验证第 5 章只承载当前阶段与变化事实边界。

    Args:
        无。

    Returns:
        无。

    Raises:
        AssertionError: 第 5 章契约缺少阶段/变化边界或禁止项。
    """

    chapter = get_chapter_contract(5)

    assert chapter.title == "当前阶段与关键变化"
    assert "当前阶段是什么（建仓期/稳定期/膨胀期/萎缩期/转型期）。" in chapter.must_answer
    assert any("过去一年最关键的 1-3 个变化" in item for item in chapter.must_answer)
    assert "这些变化是否影响原始投资假设或第 1-4 章判断。" in chapter.must_answer
    assert "下一步最小验证问题是什么。" in chapter.must_answer
    assert "不给最终持有/替换结论。" in chapter.must_not_cover
    assert "不展开风险清单；变化事实只有转译为风险或否决项时才进入第 6 章。" in chapter.must_not_cover
    assert "不重复基金经理长期画像或成本收益总评。" in chapter.must_not_cover


def test_active_fund_chapter_3_contract_requires_reviewed_turnover_or_style_change_before_stability_claim() -> None:
    """验证主动基金第 3 章稳定性判断必须先具备已复核换手率或风格变化证据。

    Args:
        无。

    Returns:
        无。

    Raises:
        AssertionError: 第 3 章契约未声明证据前提或主动基金 lens 漂移。
    """

    chapter = get_chapter_contract(3)
    lens = resolve_preferred_lens(3, "active_fund")
    manifest = load_template_contract_manifest()
    lens_keys = set(manifest.chapters[3].preferred_lens)

    assert (
        "言行一致性判断：说的和做的一样吗？主动基金如缺少已复核的换手率或风格变化证据，不得据此判断言行一致。"
        in chapter.must_answer
    )
    assert (
        "风格稳定性判断：跨期风格是否漂移？主动基金必须基于已复核的换手率或风格变化证据。"
        in chapter.must_answer
    )
    assert (
        "不在换手率或风格变化证据缺失、不可用、未复核时，推断主动基金风格稳定、风格一致或言行一致。"
        in chapter.must_not_cover
    )
    assert "换手率/风格变化证据缺口说明与下一步最小验证问题" not in chapter.required_output_items
    assert lens.priority == "core"
    assert set(_SUPPORTED_FUND_TYPES) <= lens_keys


def test_core_risk_contract_translates_changes_into_risk_veto_and_stress_test() -> None:
    """验证第 6 章承载风险、否决项和压力测试边界。

    Args:
        无。

    Returns:
        无。

    Raises:
        AssertionError: 第 6 章契约缺少风险转译或禁止项。
    """

    chapter = get_chapter_contract(6)

    assert chapter.title == "核心风险与否决项"
    assert "核心风险是什么，其中哪些是结构性风险、哪些是阶段性风险。" in chapter.must_answer
    assert "是否触发一票否决，还是仍可跟踪。" in chapter.must_answer
    assert "压力测试结论是什么。" in chapter.must_answer
    assert "哪个信息缺口最可能改变最终判断，下一轮先验证什么。" in chapter.must_answer
    assert "不复述当前阶段事实，除非明确转译为风险、压力测试或否决项。" in chapter.must_not_cover
    assert "不给最终持有/替换结论。" in chapter.must_not_cover
    assert "不预测收益或市场走势。" in chapter.must_not_cover


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


def _current_template_json() -> dict[str, Any]:
    """读取当前模板文档中的 canonical JSON。

    Args:
        无。

    Returns:
        当前模板契约 JSON 的深拷贝字典。

    Raises:
        AssertionError: 当前模板 JSON 无法解析时由测试失败体现。
    """

    template_text = Path("docs/fund-analysis-template-draft.md").read_text(encoding="utf-8")
    raw_manifest = contracts_module._parse_template_contract_manifest_json(template_text)
    return json.loads(json.dumps(raw_manifest, ensure_ascii=False))


def _write_manifest_template(tmp_path: Path, manifest: dict[str, Any]) -> Path:
    """把 manifest JSON 写入临时模板 Markdown。

    Args:
        tmp_path: pytest 临时目录。
        manifest: 待写入的 manifest JSON。

    Returns:
        临时模板路径。

    Raises:
        无显式抛出。
    """

    return _write_template_markdown(tmp_path, _manifest_markdown(manifest))


def _write_template_markdown(tmp_path: Path, markdown_text: str) -> Path:
    """写入临时模板 Markdown 文本。

    Args:
        tmp_path: pytest 临时目录。
        markdown_text: 待写入的 Markdown 文本。

    Returns:
        临时模板路径。

    Raises:
        无显式抛出。
    """

    tmp_path.mkdir(parents=True, exist_ok=True)
    template_path = tmp_path / "template.md"
    template_path.write_text(markdown_text, encoding="utf-8")
    contracts_module._clear_template_contract_manifest_cache()
    return template_path


def _manifest_markdown(manifest: dict[str, Any]) -> str:
    """构造包含 canonical JSON block 的临时 Markdown。

    Args:
        manifest: 待写入的 manifest JSON。

    Returns:
        Markdown 文本。

    Raises:
        无显式抛出。
    """

    manifest_json = json.dumps(manifest, ensure_ascii=False, indent=2)
    return (
        "# 临时模板\n\n"
        "<!--\n"
        "TEMPLATE_CONTRACT_MANIFEST_JSON\n"
        f"{manifest_json}\n"
        "END_TEMPLATE_CONTRACT_MANIFEST_JSON\n"
        "-->\n"
    )
