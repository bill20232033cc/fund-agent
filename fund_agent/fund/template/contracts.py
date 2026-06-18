"""基金分析模板 CHAPTER_CONTRACT 机器契约。

本模块在 Agent 层基金能力维护可机器消费的模板章节契约，覆盖模板第 0-7 章。
契约内容来自 `docs/fund-analysis-template-draft.md` 中唯一的
`TEMPLATE_CONTRACT_MANIFEST_JSON` 区块。本模块只负责严格解析、校验并投影为
当前未类型化的 `TemplateContractManifest`，不再以 Python 常量维护章节契约正文。
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Final, Literal, Mapping, get_args

from fund_agent.fund.fund_type import FundType

LensKey = FundType | Literal["default"]

_TEMPLATE_ID: Final[str] = "fund-analysis-template-v1"
_TYPED_TEMPLATE_ID: Final[str] = "fund-analysis-template-typed-v1"
_SCHEMA_VERSION: Final[str] = "typed_chapter_contract.v1"
_SOURCE_PATH: Final[str] = "docs/fund-analysis-template-draft.md"
_REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[3]
_DEFAULT_TEMPLATE_PATH: Final[Path] = _REPO_ROOT / _SOURCE_PATH
_EXPECTED_CHAPTER_IDS: Final[tuple[int, ...]] = tuple(range(8))
_EXPECTED_PUBLIC_CHAPTER_IDS: Final[list[int]] = list(_EXPECTED_CHAPTER_IDS)
_SUPPORTED_FUND_TYPES: Final[tuple[FundType, ...]] = get_args(FundType)
_SUPPORTED_LENS_KEYS: Final[frozenset[str]] = frozenset((*_SUPPORTED_FUND_TYPES, "default"))
_SUPPORTED_LENS_PRIORITIES: Final[frozenset[str]] = frozenset(
    ("core", "high", "medium", "low")
)
_TEMPLATE_BLOCK_START: Final[str] = "TEMPLATE_CONTRACT_MANIFEST_JSON"
_TEMPLATE_BLOCK_END: Final[str] = "END_TEMPLATE_CONTRACT_MANIFEST_JSON"
_REQUIRED_OUTPUT_MISSING_BEHAVIORS: Final[frozenset[str]] = frozenset(
    (
        "render_evidence_gap",
        "render_minimum_verification_question",
        "delete_if_not_applicable",
        "block",
    )
)
_EVIDENCE_STATUSES: Final[frozenset[str]] = frozenset(
    ("available", "missing", "unavailable", "not_applicable", "unreviewed")
)
_ALLOWED_CONTEXTS: Final[frozenset[str]] = frozenset(
    ("required_label", "evidence_gap_statement", "quote", "anchor_caption")
)
_TOP_LEVEL_KEYS: Final[frozenset[str]] = frozenset(
    (
        "schema_version",
        "template_id",
        "source_template_id",
        "source_path",
        "public_chapter_ids",
        "chapters",
    )
)
_CHAPTER_KEYS: Final[frozenset[str]] = frozenset(
    (
        "chapter_id",
        "title",
        "narrative_mode",
        "must_answer",
        "must_not_cover",
        "required_output_items",
        "preferred_lens",
        "audit_focus",
        "consumes_chapter_conclusions",
        "independent_action_source",
        "internal_subcontracts",
    )
)
_CLAUSE_KEYS: Final[frozenset[str]] = frozenset(("id", "text"))
_MUST_NOT_COVER_KEYS: Final[frozenset[str]] = frozenset(
    ("id", "text", "applies_when", "allowed_contexts")
)
_REQUIRED_OUTPUT_ITEM_KEYS: Final[frozenset[str]] = frozenset(
    ("id", "text", "when_evidence_missing", "missing_evidence_reason")
)
_LENS_RULE_KEYS: Final[frozenset[str]] = frozenset(
    ("fund_type", "statements", "facets_any", "priority")
)
_EVIDENCE_PREDICATE_KEYS: Final[frozenset[str]] = frozenset(
    ("predicate_id", "requirement_ids", "required_statuses", "description")
)
_INTERNAL_SUBCONTRACT_KEYS: Final[frozenset[str]] = frozenset(
    ("subcontract_id", "title", "requirement_ids", "public_chapter_id")
)
_FIELD_ID_SEGMENTS: Final[Mapping[str, str]] = {
    "must_answer": "must_answer",
    "must_not_cover": "must_not_cover",
    "required_output_items": "required_output",
}


@dataclass(frozen=True, slots=True)
class TemplateLensRule:
    """模板章节的基金类型视角规则。

    Attributes:
        fund_type: 当前 lens 对应的标准基金类型，或 `default` fallback。
        statements: 当前基金类型下的分析视角说明，见模板第 0-7 章 preferred_lens。
        facets_any: 模板草稿中声明的适用细分标签；没有声明时为空元组。
        priority: 模板草稿中声明的优先级；没有声明时为 `None`。
    """

    fund_type: LensKey
    statements: tuple[str, ...]
    facets_any: tuple[str, ...] = ()
    priority: str | None = None


@dataclass(frozen=True, slots=True)
class ChapterContract:
    """模板单章 CHAPTER_CONTRACT。

    Attributes:
        chapter_id: 模板章节编号，必须为 0-7。
        title: 章节标题，见模板第 0-7 章。
        narrative_mode: 叙事模式。
        must_answer: 本章必须回答的问题列表。
        must_not_cover: 本章禁止覆盖的内容。
        required_output_items: 本章必须输出的条目。
        preferred_lens: 按基金类型组织的分析视角规则。
    """

    chapter_id: int
    title: str
    narrative_mode: str
    must_answer: tuple[str, ...]
    must_not_cover: tuple[str, ...]
    required_output_items: tuple[str, ...]
    preferred_lens: Mapping[str, TemplateLensRule]


@dataclass(frozen=True, slots=True)
class TemplateContractManifest:
    """基金分析模板契约清单。

    Attributes:
        template_id: 模板契约标识。
        source_path: 人工维护契约文本的来源文档路径。
        chapters: 模板第 0-7 章的机器契约。
    """

    template_id: str
    source_path: str
    chapters: tuple[ChapterContract, ...]


def load_template_contract_manifest() -> TemplateContractManifest:
    """读取基金分析模板契约清单。

    Returns:
        覆盖模板第 0-7 章的 `TemplateContractManifest`。

    Raises:
        ValueError: 模板文档缺失、JSON 区块不唯一、JSON 非法、结构漂移或
            manifest 不满足章节数量、字段完整性、lens 可解析性时抛出。
    """

    return _load_template_contract_manifest_from_path(_DEFAULT_TEMPLATE_PATH)


def get_chapter_contract(chapter_id: int) -> ChapterContract:
    """按章节编号读取 CHAPTER_CONTRACT。

    Args:
        chapter_id: 模板章节编号，必须为 0-7。

    Returns:
        对应章节的 `ChapterContract`。

    Raises:
        ValueError: 章节编号不存在或 manifest 校验失败时抛出。
    """

    manifest = load_template_contract_manifest()
    for chapter in manifest.chapters:
        if chapter.chapter_id == chapter_id:
            return chapter
    raise ValueError(f"未找到模板章节契约：chapter_id={chapter_id}")


def resolve_preferred_lens(chapter_id: int, fund_type: FundType) -> TemplateLensRule:
    """解析指定章节与基金类型对应的 preferred_lens。

    Args:
        chapter_id: 模板章节编号，必须为 0-7。
        fund_type: 标准基金类型。

    Returns:
        精确命中基金类型的 `TemplateLensRule`；没有精确命中时返回 `default` 规则。

    Raises:
        ValueError: 章节不存在、基金类型不受支持，或没有精确 lens 且没有 default fallback 时抛出。
    """

    if fund_type not in _SUPPORTED_FUND_TYPES:
        raise ValueError(f"不支持的基金类型：{fund_type}")

    chapter = get_chapter_contract(chapter_id)
    if fund_type in chapter.preferred_lens:
        return chapter.preferred_lens[fund_type]
    if "default" in chapter.preferred_lens:
        return chapter.preferred_lens["default"]
    raise ValueError(f"章节 {chapter_id} 缺少基金类型 {fund_type} 的 preferred_lens fallback")


def validate_template_contract_manifest(manifest: TemplateContractManifest) -> None:
    """校验模板契约清单是否满足 fail-closed 约束。

    Args:
        manifest: 待校验的模板契约清单。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: 章节数量、id 连续性、重复 id、空字段、unsupported lens key、
            lens 对象不一致或基金类型无 lens fallback 时抛出。
    """

    if not manifest.template_id.strip():
        raise ValueError("template_id 不能为空")
    if not manifest.source_path.strip():
        raise ValueError("source_path 不能为空")
    if len(manifest.chapters) != len(_EXPECTED_CHAPTER_IDS):
        raise ValueError("模板章节数量必须等于 8")

    chapter_ids = tuple(chapter.chapter_id for chapter in manifest.chapters)
    if len(set(chapter_ids)) != len(chapter_ids):
        raise ValueError("模板章节 id 存在重复")
    if chapter_ids != _EXPECTED_CHAPTER_IDS:
        raise ValueError("模板章节 id 必须连续覆盖 0..7")

    for chapter in manifest.chapters:
        _validate_chapter_contract(chapter)
        # 每个支持基金类型都必须能精确命中或回退 default，避免后续推理器无 lens 可用。
        for fund_type in _SUPPORTED_FUND_TYPES:
            if fund_type not in chapter.preferred_lens and "default" not in chapter.preferred_lens:
                raise ValueError(
                    f"章节 {chapter.chapter_id} 缺少基金类型 {fund_type} 的 preferred_lens fallback"
                )


def _load_template_contract_manifest_from_path(path: str | Path) -> TemplateContractManifest:
    """从指定模板文档路径读取未类型化章节契约。

    Args:
        path: 包含唯一 `TEMPLATE_CONTRACT_MANIFEST_JSON` 区块的 Markdown 文件路径。

    Returns:
        从模板 JSON 投影得到的 `TemplateContractManifest`。

    Raises:
        ValueError: 文件读取失败、JSON 区块或 manifest 结构不满足 fail-closed 约束时抛出。
    """

    path_key = str(Path(path).resolve())
    return _load_template_contract_manifest_from_path_cached(path_key)


@lru_cache(maxsize=16)
def _load_template_contract_manifest_from_path_cached(path_key: str) -> TemplateContractManifest:
    """带路径键缓存地读取模板契约。

    Args:
        path_key: 已解析为绝对路径字符串的模板文件路径。

    Returns:
        从模板 JSON 投影得到的 `TemplateContractManifest`。

    Raises:
        ValueError: 文件读取失败、JSON 区块或 manifest 结构不满足 fail-closed 约束时抛出。
    """

    template_path = Path(path_key)
    try:
        template_text = template_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"读取模板契约文档失败：{template_path}") from exc

    raw_manifest = _parse_template_contract_manifest_json(template_text)
    manifest = _project_untyped_manifest(raw_manifest)
    validate_template_contract_manifest(manifest)
    return manifest


def _clear_template_contract_manifest_cache() -> None:
    """清理模板契约路径缓存，供测试隔离临时模板文件。

    Returns:
        无。

    Raises:
        无显式抛出。
    """

    _load_template_contract_manifest_from_path_cached.cache_clear()


def _parse_template_contract_manifest_json(template_text: str) -> Mapping[str, Any]:
    """从 Markdown 文本中提取并解析唯一模板契约 JSON 区块。

    Args:
        template_text: 模板 Markdown 完整文本。

    Returns:
        解析后的 JSON object。

    Raises:
        ValueError: 区块缺失、重复、为空、非 JSON object 或包含未知顶层字段时抛出。
    """

    blocks = _extract_template_manifest_blocks(template_text)
    if not blocks:
        raise ValueError("缺少 TEMPLATE_CONTRACT_MANIFEST_JSON 区块")
    if len(blocks) > 1:
        raise ValueError("TEMPLATE_CONTRACT_MANIFEST_JSON 区块必须 exactly one")

    block = blocks[0].strip()
    if not block:
        raise ValueError("TEMPLATE_CONTRACT_MANIFEST_JSON 区块不能为空")

    try:
        parsed = json.loads(block)
    except json.JSONDecodeError as exc:
        raise ValueError(f"TEMPLATE_CONTRACT_MANIFEST_JSON 不是合法 JSON：{exc.msg}") from exc

    if not isinstance(parsed, dict):
        raise ValueError("TEMPLATE_CONTRACT_MANIFEST_JSON 顶层必须是 JSON object")
    _reject_unknown_keys(parsed, _TOP_LEVEL_KEYS, "manifest")
    return parsed


def _extract_template_manifest_blocks(template_text: str) -> tuple[str, ...]:
    """提取所有模板契约 JSON 区块正文。

    Args:
        template_text: 模板 Markdown 完整文本。

    Returns:
        所有匹配区块正文组成的元组。

    Raises:
        ValueError: 起止 marker 不配对时抛出。
    """

    blocks: list[str] = []
    current_block_lines: list[str] | None = None
    for line_number, line in enumerate(template_text.splitlines(), start=1):
        stripped_line = line.strip()
        if stripped_line == _TEMPLATE_BLOCK_START:
            if current_block_lines is not None:
                raise ValueError("TEMPLATE_CONTRACT_MANIFEST_JSON 区块嵌套或重复开始")
            current_block_lines = []
            continue
        if stripped_line == _TEMPLATE_BLOCK_END:
            if current_block_lines is None:
                raise ValueError(
                    f"TEMPLATE_CONTRACT_MANIFEST_JSON 区块 END marker 没有开始：line={line_number}"
                )
            blocks.append("\n".join(current_block_lines))
            current_block_lines = None
            continue
        if current_block_lines is not None:
            current_block_lines.append(line)
    if current_block_lines is not None:
        raise ValueError("TEMPLATE_CONTRACT_MANIFEST_JSON 区块缺少 END marker")
    return tuple(blocks)


def _project_untyped_manifest(raw_manifest: Mapping[str, Any]) -> TemplateContractManifest:
    """把模板 JSON object 投影为当前未类型化 manifest。

    Args:
        raw_manifest: 已通过 JSON 解析的模板契约 object。

    Returns:
        `TemplateContractManifest` 未类型化投影。

    Raises:
        ValueError: 顶层字段、章节字段或嵌套契约字段漂移时抛出。
    """

    _validate_top_level_manifest(raw_manifest)
    chapters_value = raw_manifest["chapters"]
    if not isinstance(chapters_value, list):
        raise ValueError("manifest.chapters 必须是 array")

    chapters = tuple(
        _project_chapter_contract(chapter_value, index)
        for index, chapter_value in enumerate(chapters_value)
    )
    manifest = TemplateContractManifest(
        template_id=_read_required_string(raw_manifest, "source_template_id", "manifest.source_template_id"),
        source_path=_read_required_string(raw_manifest, "source_path", "manifest.source_path"),
        chapters=chapters,
    )
    return manifest


def _validate_top_level_manifest(raw_manifest: Mapping[str, Any]) -> None:
    """校验模板 JSON 顶层字段。

    Args:
        raw_manifest: 已通过 JSON 解析的模板契约 object。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: 顶层字段缺失、空值或固定值漂移时抛出。
    """

    _require_exact_keys(raw_manifest, _TOP_LEVEL_KEYS, "manifest")
    _require_exact_string(raw_manifest, "schema_version", _SCHEMA_VERSION, "manifest.schema_version")
    _require_exact_string(raw_manifest, "template_id", _TYPED_TEMPLATE_ID, "manifest.template_id")
    _require_exact_string(
        raw_manifest,
        "source_template_id",
        _TEMPLATE_ID,
        "manifest.source_template_id",
    )
    _require_exact_string(raw_manifest, "source_path", _SOURCE_PATH, "manifest.source_path")
    public_chapter_ids = raw_manifest["public_chapter_ids"]
    if public_chapter_ids != _EXPECTED_PUBLIC_CHAPTER_IDS:
        raise ValueError("manifest.public_chapter_ids 必须 exactly [0,1,2,3,4,5,6,7]")


def _project_chapter_contract(raw_chapter: Any, index: int) -> ChapterContract:
    """把单个章节 JSON object 投影为 `ChapterContract`。

    Args:
        raw_chapter: 单章 JSON object。
        index: 当前章节在 chapters array 中的位置，用于错误路径。

    Returns:
        投影后的 `ChapterContract`。

    Raises:
        ValueError: 单章字段缺失、未知或嵌套字段结构不满足契约时抛出。
    """

    path = f"chapters[{index}]"
    if not isinstance(raw_chapter, dict):
        raise ValueError(f"{path} 必须是 object")
    _require_exact_keys(raw_chapter, _CHAPTER_KEYS, path)

    chapter_id = _read_required_int(raw_chapter, "chapter_id", f"{path}.chapter_id")
    if chapter_id != index:
        raise ValueError(f"{path}.chapter_id 必须等于当前位置 {index}")

    must_answer = _project_text_entries(
        raw_chapter["must_answer"],
        chapter_id,
        "must_answer",
        f"{path}.must_answer",
        _CLAUSE_KEYS,
    )
    must_not_cover = _project_must_not_cover_entries(
        raw_chapter["must_not_cover"],
        chapter_id,
        f"{path}.must_not_cover",
    )
    required_output_items = _project_required_output_items(
        raw_chapter["required_output_items"],
        chapter_id,
        f"{path}.required_output_items",
    )
    preferred_lens = _project_preferred_lens(
        raw_chapter["preferred_lens"],
        chapter_id,
        f"{path}.preferred_lens",
    )
    _validate_chapter_sidecar_fields(raw_chapter, chapter_id, path)

    return ChapterContract(
        chapter_id=chapter_id,
        title=_read_required_string(raw_chapter, "title", f"{path}.title"),
        narrative_mode=_read_required_string(
            raw_chapter,
            "narrative_mode",
            f"{path}.narrative_mode",
        ),
        must_answer=must_answer,
        must_not_cover=must_not_cover,
        required_output_items=required_output_items,
        preferred_lens=preferred_lens,
    )


def _project_text_entries(
    raw_entries: Any,
    chapter_id: int,
    field_name: str,
    path: str,
    expected_keys: frozenset[str],
) -> tuple[str, ...]:
    """投影带 stable id 和 text 的条目数组。

    Args:
        raw_entries: JSON array。
        chapter_id: 当前章节编号。
        field_name: 当前字段名。
        path: 错误路径。
        expected_keys: 当前条目允许出现的字段集合。

    Returns:
        按原顺序投影得到的文本元组。

    Raises:
        ValueError: 条目数组为空、条目不是 object、unknown keys、stable id 或 text 无效时抛出。
    """

    entries = _read_non_empty_array(raw_entries, path)
    texts: list[str] = []
    for index, raw_entry in enumerate(entries):
        entry_path = f"{path}[{index}]"
        if not isinstance(raw_entry, dict):
            raise ValueError(f"{entry_path} 必须是 object")
        _require_exact_keys(raw_entry, expected_keys, entry_path)
        _validate_entry_id(
            _read_required_string(raw_entry, "id", f"{entry_path}.id"),
            chapter_id,
            field_name,
            index,
            f"{entry_path}.id",
        )
        texts.append(_read_required_string(raw_entry, "text", f"{entry_path}.text"))
    return tuple(texts)


def _project_must_not_cover_entries(
    raw_entries: Any,
    chapter_id: int,
    path: str,
) -> tuple[str, ...]:
    """投影 must_not_cover 条目并校验条件谓词结构。

    Args:
        raw_entries: `must_not_cover` JSON array。
        chapter_id: 当前章节编号。
        path: 错误路径。

    Returns:
        按原顺序投影得到的 must_not_cover 文本元组。

    Raises:
        ValueError: 条目、`applies_when` 或 `allowed_contexts` 结构无效时抛出。
    """

    entries = _read_non_empty_array(raw_entries, path)
    texts: list[str] = []
    for index, raw_entry in enumerate(entries):
        entry_path = f"{path}[{index}]"
        if not isinstance(raw_entry, dict):
            raise ValueError(f"{entry_path} 必须是 object")
        _require_exact_keys(raw_entry, _MUST_NOT_COVER_KEYS, entry_path)
        _validate_entry_id(
            _read_required_string(raw_entry, "id", f"{entry_path}.id"),
            chapter_id,
            "must_not_cover",
            index,
            f"{entry_path}.id",
        )
        _validate_applies_when(raw_entry["applies_when"], f"{entry_path}.applies_when")
        allowed_contexts = _read_string_array(
            raw_entry["allowed_contexts"],
            f"{entry_path}.allowed_contexts",
            allow_empty=True,
        )
        if raw_entry["applies_when"] is None and allowed_contexts:
            raise ValueError(f"{entry_path}.allowed_contexts 在 applies_when 为 null 时必须为空")
        if raw_entry["applies_when"] is not None and not allowed_contexts:
            raise ValueError(f"{entry_path}.allowed_contexts 在 applies_when 非空时不能为空")
        for allowed_context in allowed_contexts:
            if allowed_context not in _ALLOWED_CONTEXTS:
                raise ValueError(f"{entry_path}.allowed_contexts 存在不支持的上下文：{allowed_context}")
        texts.append(_read_required_string(raw_entry, "text", f"{entry_path}.text"))
    return tuple(texts)


def _project_required_output_items(
    raw_entries: Any,
    chapter_id: int,
    path: str,
) -> tuple[str, ...]:
    """投影 required_output_items 条目并校验缺证处理策略。

    Args:
        raw_entries: `required_output_items` JSON array。
        chapter_id: 当前章节编号。
        path: 错误路径。

    Returns:
        按原顺序投影得到的 required output 文本元组。

    Raises:
        ValueError: 条目 stable id、text、缺证策略或缺证原因无效时抛出。
    """

    entries = _read_non_empty_array(raw_entries, path)
    texts: list[str] = []
    for index, raw_entry in enumerate(entries):
        entry_path = f"{path}[{index}]"
        if not isinstance(raw_entry, dict):
            raise ValueError(f"{entry_path} 必须是 object")
        _require_exact_keys(raw_entry, _REQUIRED_OUTPUT_ITEM_KEYS, entry_path)
        _validate_entry_id(
            _read_required_string(raw_entry, "id", f"{entry_path}.id"),
            chapter_id,
            "required_output_items",
            index,
            f"{entry_path}.id",
        )
        behavior = raw_entry["when_evidence_missing"]
        if behavior is not None:
            if not isinstance(behavior, str) or not behavior.strip():
                raise ValueError(f"{entry_path}.when_evidence_missing 必须是非空字符串或 null")
            if behavior not in _REQUIRED_OUTPUT_MISSING_BEHAVIORS:
                raise ValueError(f"{entry_path}.when_evidence_missing 不受支持：{behavior}")
            _read_required_string(
                raw_entry,
                "missing_evidence_reason",
                f"{entry_path}.missing_evidence_reason",
            )
        elif raw_entry["missing_evidence_reason"] is not None:
            raise ValueError(f"{entry_path}.missing_evidence_reason 在策略为 null 时必须为 null")
        texts.append(_read_required_string(raw_entry, "text", f"{entry_path}.text"))
    return tuple(texts)


def _project_preferred_lens(
    raw_lens: Any,
    chapter_id: int,
    path: str,
) -> Mapping[str, TemplateLensRule]:
    """投影 preferred_lens object。

    Args:
        raw_lens: `preferred_lens` JSON object。
        chapter_id: 当前章节编号。
        path: 错误路径。

    Returns:
        以 lens key 为键的 `TemplateLensRule` 映射。

    Raises:
        ValueError: lens 不是 object、为空、key 不受支持、fund_type 不一致或字段无效时抛出。
    """

    if not isinstance(raw_lens, dict):
        raise ValueError(f"{path} 必须是 object")
    if not raw_lens:
        raise ValueError(f"{path} 不能为空")

    projected: dict[str, TemplateLensRule] = {}
    for lens_key, raw_rule in raw_lens.items():
        rule_path = f"{path}.{lens_key}"
        if lens_key not in _SUPPORTED_LENS_KEYS:
            raise ValueError(f"{path} 存在不支持的 lens key：{lens_key}")
        if not isinstance(raw_rule, dict):
            raise ValueError(f"{rule_path} 必须是 object")
        _require_exact_keys(raw_rule, _LENS_RULE_KEYS, rule_path)
        fund_type = _read_required_string(raw_rule, "fund_type", f"{rule_path}.fund_type")
        if fund_type != lens_key:
            raise ValueError(f"{rule_path}.fund_type 必须等于 lens key")
        statements = tuple(
            _read_string_array(raw_rule["statements"], f"{rule_path}.statements", allow_empty=False)
        )
        facets_any = tuple(
            _read_string_array(raw_rule["facets_any"], f"{rule_path}.facets_any", allow_empty=True)
        )
        priority = _read_optional_priority(raw_rule["priority"], f"{rule_path}.priority")
        projected[lens_key] = TemplateLensRule(
            fund_type=fund_type,
            statements=statements,
            facets_any=facets_any,
            priority=priority,
        )

    return projected


def _validate_chapter_sidecar_fields(raw_chapter: Mapping[str, Any], chapter_id: int, path: str) -> None:
    """校验当前 untyped 投影不消费但属于 canonical JSON 的章节侧字段。

    Args:
        raw_chapter: 单章 JSON object。
        chapter_id: 当前章节编号。
        path: 错误路径。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: 侧字段类型、空值或章节引用无效时抛出。
    """

    _read_string_array(raw_chapter["audit_focus"], f"{path}.audit_focus", allow_empty=False)
    consumes = raw_chapter["consumes_chapter_conclusions"]
    if not isinstance(consumes, list):
        raise ValueError(f"{path}.consumes_chapter_conclusions 必须是 array")
    for index, consumed_chapter_id in enumerate(consumes):
        if consumed_chapter_id not in _EXPECTED_CHAPTER_IDS:
            raise ValueError(
                f"{path}.consumes_chapter_conclusions[{index}] 必须是 0..7 的章节 id"
            )
    if not isinstance(raw_chapter["independent_action_source"], bool):
        raise ValueError(f"{path}.independent_action_source 必须是 boolean")
    _validate_internal_subcontracts(
        raw_chapter["internal_subcontracts"],
        chapter_id,
        f"{path}.internal_subcontracts",
    )


def _validate_internal_subcontracts(raw_subcontracts: Any, chapter_id: int, path: str) -> None:
    """校验内部 subcontract 数组结构。

    Args:
        raw_subcontracts: `internal_subcontracts` JSON array。
        chapter_id: 当前章节编号。
        path: 错误路径。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: subcontract 不是 object、含 unknown keys、空字段或 public chapter 泄漏时抛出。
    """

    if not isinstance(raw_subcontracts, list):
        raise ValueError(f"{path} 必须是 array")
    for index, raw_subcontract in enumerate(raw_subcontracts):
        subcontract_path = f"{path}[{index}]"
        if not isinstance(raw_subcontract, dict):
            raise ValueError(f"{subcontract_path} 必须是 object")
        _require_exact_keys(raw_subcontract, _INTERNAL_SUBCONTRACT_KEYS, subcontract_path)
        _read_required_string(raw_subcontract, "subcontract_id", f"{subcontract_path}.subcontract_id")
        _read_required_string(raw_subcontract, "title", f"{subcontract_path}.title")
        _read_string_array(
            raw_subcontract["requirement_ids"],
            f"{subcontract_path}.requirement_ids",
            allow_empty=False,
        )
        if raw_subcontract["public_chapter_id"] is not None:
            raise ValueError(f"{subcontract_path}.public_chapter_id 必须为 null")
    if chapter_id != 2 and raw_subcontracts:
        raise ValueError(f"{path} 仅允许第 2 章声明内部 subcontract")


def _validate_applies_when(raw_predicate: Any, path: str) -> None:
    """校验 evidence predicate 结构。

    Args:
        raw_predicate: `applies_when` JSON value。
        path: 错误路径。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: predicate 字段缺失、unknown keys、数组为空或状态值不受支持时抛出。
    """

    if raw_predicate is None:
        return
    if not isinstance(raw_predicate, dict):
        raise ValueError(f"{path} 必须是 object 或 null")
    _require_exact_keys(raw_predicate, _EVIDENCE_PREDICATE_KEYS, path)
    _read_required_string(raw_predicate, "predicate_id", f"{path}.predicate_id")
    _read_string_array(raw_predicate["requirement_ids"], f"{path}.requirement_ids", allow_empty=False)
    statuses = _read_string_array(
        raw_predicate["required_statuses"],
        f"{path}.required_statuses",
        allow_empty=False,
    )
    for status in statuses:
        if status not in _EVIDENCE_STATUSES:
            raise ValueError(f"{path}.required_statuses 存在不支持的状态：{status}")
    _read_required_string(raw_predicate, "description", f"{path}.description")


def _validate_chapter_contract(chapter: ChapterContract) -> None:
    """校验单章契约字段。

    Args:
        chapter: 待校验的章节契约。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: 章节字段为空、lens key 不受支持或 lens 内容无效时抛出。
    """

    if chapter.chapter_id not in _EXPECTED_CHAPTER_IDS:
        raise ValueError(f"不支持的章节 id：{chapter.chapter_id}")
    if not chapter.title.strip():
        raise ValueError(f"章节 {chapter.chapter_id} 标题不能为空")
    if not chapter.narrative_mode.strip():
        raise ValueError(f"章节 {chapter.chapter_id} narrative_mode 不能为空")
    _validate_non_empty_text_tuple(chapter.must_answer, "must_answer", chapter.chapter_id)
    _validate_non_empty_text_tuple(chapter.must_not_cover, "must_not_cover", chapter.chapter_id)
    _validate_non_empty_text_tuple(
        chapter.required_output_items,
        "required_output_items",
        chapter.chapter_id,
    )
    if not chapter.preferred_lens:
        raise ValueError(f"章节 {chapter.chapter_id} preferred_lens 不能为空")

    for key, lens_rule in chapter.preferred_lens.items():
        if key not in _SUPPORTED_LENS_KEYS:
            raise ValueError(f"章节 {chapter.chapter_id} 存在不支持的 lens key：{key}")
        if key != lens_rule.fund_type:
            raise ValueError(f"章节 {chapter.chapter_id} lens key 与 fund_type 不一致：{key}")
        _validate_lens_rule(chapter.chapter_id, lens_rule)


def _validate_lens_rule(chapter_id: int, lens_rule: TemplateLensRule) -> None:
    """校验单条 preferred_lens 规则。

    Args:
        chapter_id: 当前章节编号。
        lens_rule: 待校验的 lens 规则。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: lens 类型、说明文本、facets 或 priority 无效时抛出。
    """

    if lens_rule.fund_type not in _SUPPORTED_LENS_KEYS:
        raise ValueError(f"章节 {chapter_id} 存在不支持的 lens fund_type：{lens_rule.fund_type}")
    _validate_non_empty_text_tuple(lens_rule.statements, "preferred_lens.statements", chapter_id)
    if any(not facet.strip() for facet in lens_rule.facets_any):
        raise ValueError(f"章节 {chapter_id} preferred_lens.facets_any 存在空值")
    if lens_rule.priority is not None and not lens_rule.priority.strip():
        raise ValueError(f"章节 {chapter_id} preferred_lens.priority 不能为空字符串")
    if lens_rule.priority is not None and lens_rule.priority not in _SUPPORTED_LENS_PRIORITIES:
        raise ValueError(f"章节 {chapter_id} preferred_lens.priority 不受支持：{lens_rule.priority}")


def _validate_non_empty_text_tuple(values: tuple[str, ...], field_name: str, chapter_id: int) -> None:
    """校验非空文本元组。

    Args:
        values: 待校验的文本元组。
        field_name: 字段名，用于错误信息。
        chapter_id: 当前章节编号。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: 元组为空或包含空白文本时抛出。
    """

    if not values:
        raise ValueError(f"章节 {chapter_id} {field_name} 不能为空")
    if any(not value.strip() for value in values):
        raise ValueError(f"章节 {chapter_id} {field_name} 存在空值")


def _validate_entry_id(
    entry_id: str,
    chapter_id: int,
    field_name: str,
    index: int,
    path: str,
) -> None:
    """校验 stable id 是否匹配章节、字段和顺序。

    Args:
        entry_id: 条目 stable id。
        chapter_id: 当前章节编号。
        field_name: 当前字段名。
        index: 条目位置，从 0 开始。
        path: 错误路径。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: stable id 与 `chN.<field>.item_XX` 形状不一致时抛出。
    """

    field_segment = _FIELD_ID_SEGMENTS[field_name]
    expected_id = f"ch{chapter_id}.{field_segment}.item_{index + 1:02d}"
    if entry_id != expected_id:
        raise ValueError(f"{path} stable id 必须为 {expected_id}，实际为 {entry_id}")


def _read_required_string(data: Mapping[str, Any], key: str, path: str) -> str:
    """读取必需非空字符串字段。

    Args:
        data: JSON object。
        key: 字段名。
        path: 错误路径。

    Returns:
        去除首尾空白后的原字符串值。

    Raises:
        ValueError: 字段不是非空字符串时抛出。
    """

    value = data[key]
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{path} 必须是非空字符串")
    return value


def _read_required_int(data: Mapping[str, Any], key: str, path: str) -> int:
    """读取必需整数字段。

    Args:
        data: JSON object。
        key: 字段名。
        path: 错误路径。

    Returns:
        整数字段值。

    Raises:
        ValueError: 字段不是整数或是 boolean 时抛出。
    """

    value = data[key]
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"{path} 必须是 integer")
    return value


def _read_non_empty_array(value: Any, path: str) -> list[Any]:
    """读取非空 JSON array。

    Args:
        value: 待检查 JSON value。
        path: 错误路径。

    Returns:
        原始 list 值。

    Raises:
        ValueError: 值不是 array 或为空时抛出。
    """

    if not isinstance(value, list):
        raise ValueError(f"{path} 必须是 array")
    if not value:
        raise ValueError(f"{path} 不能为空")
    return value


def _read_string_array(value: Any, path: str, *, allow_empty: bool) -> tuple[str, ...]:
    """读取字符串数组。

    Args:
        value: 待检查 JSON value。
        path: 错误路径。
        allow_empty: 是否允许空数组。

    Returns:
        字符串元组。

    Raises:
        ValueError: 值不是 array、空数组不被允许或成员不是非空字符串时抛出。
    """

    if not isinstance(value, list):
        raise ValueError(f"{path} 必须是 array")
    if not allow_empty and not value:
        raise ValueError(f"{path} 不能为空")
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            raise ValueError(f"{path}[{index}] 必须是非空字符串")
    return tuple(value)


def _read_optional_priority(value: Any, path: str) -> str | None:
    """读取 preferred_lens priority 字段。

    Args:
        value: JSON priority value。
        path: 错误路径。

    Returns:
        `None` 或闭集内 priority 字符串。

    Raises:
        ValueError: priority 类型错误、空字符串或不在闭集内时抛出。
    """

    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{path} 必须是非空字符串或 null")
    if value not in _SUPPORTED_LENS_PRIORITIES:
        raise ValueError(f"{path} 不受支持：{value}")
    return value


def _require_exact_string(
    data: Mapping[str, Any],
    key: str,
    expected: str,
    path: str,
) -> None:
    """校验字符串字段等于固定值。

    Args:
        data: JSON object。
        key: 字段名。
        expected: 期望值。
        path: 错误路径。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: 字段不是非空字符串或不等于期望值时抛出。
    """

    actual = _read_required_string(data, key, path)
    if actual != expected:
        raise ValueError(f"{path} 必须为 {expected}，实际为 {actual}")


def _require_exact_keys(data: Mapping[str, Any], expected_keys: frozenset[str], path: str) -> None:
    """校验 JSON object 的 key 集合与契约完全一致。

    Args:
        data: JSON object。
        expected_keys: 允许且必需的 key 集合。
        path: 错误路径。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: 字段缺失或存在未知字段时抛出。
    """

    _reject_unknown_keys(data, expected_keys, path)
    missing_keys = expected_keys - data.keys()
    if missing_keys:
        raise ValueError(f"{path} 缺少必需字段：{sorted(missing_keys)}")


def _reject_unknown_keys(data: Mapping[str, Any], expected_keys: frozenset[str], path: str) -> None:
    """拒绝 JSON object 中的未知字段。

    Args:
        data: JSON object。
        expected_keys: 允许的 key 集合。
        path: 错误路径。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: 存在未知字段时抛出。
    """

    unknown_keys = data.keys() - expected_keys
    if unknown_keys:
        raise ValueError(f"{path} 存在未知字段：{sorted(unknown_keys)}")


def _main(argv: list[str] | None = None) -> int:
    """执行本地模板契约校验命令。

    Args:
        argv: 命令行参数；为 `None` 时读取进程参数。

    Returns:
        校验成功返回 `0`。

    Raises:
        ValueError: 模板解析或校验失败时抛出。
    """

    parser = argparse.ArgumentParser(description="校验基金分析模板契约 JSON block")
    parser.add_argument(
        "--validate-template-doc",
        action="store_true",
        help="校验 docs/fund-analysis-template-draft.md 中的 TEMPLATE_CONTRACT_MANIFEST_JSON",
    )
    parser.add_argument(
        "--template-path",
        default=str(_DEFAULT_TEMPLATE_PATH),
        help="待校验的模板 Markdown 路径",
    )
    args = parser.parse_args(argv)
    if not args.validate_template_doc:
        parser.error("必须传入 --validate-template-doc")
    manifest = _load_template_contract_manifest_from_path(args.template_path)
    print(
        "template_contract_manifest=valid "
        f"template_id={manifest.template_id} chapters={len(manifest.chapters)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
