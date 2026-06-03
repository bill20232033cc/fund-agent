"""基金分析模板 typed CHAPTER_CONTRACT 投影。

本模块属于 Agent 层 Fund 包，只把 `docs/fund-analysis-template-draft.md`
中的 `TEMPLATE_CONTRACT_MANIFEST_JSON` 真源投影为 typed dataclasses。
见模板第 2 章 R=A+B-C：Ch2 的 performance / attribution / cost 只能作为
第 2 章内部 typed subcontract，不能成为公开章节。
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final, Literal, Mapping, TypeAlias, cast, get_args

from fund_agent.fund.fund_type import FundType
from fund_agent.fund.template import contracts as contracts_module
from fund_agent.fund.template.contracts import (
    TemplateContractManifest,
    load_template_contract_manifest,
)

TYPED_TEMPLATE_CONTRACT_SCHEMA_VERSION: Final[str] = "typed_chapter_contract.v1"
TYPED_TEMPLATE_CONTRACT_TEMPLATE_ID: Final[str] = "fund-analysis-template-typed-v1"
EXPECTED_PUBLIC_CHAPTER_IDS: Final[tuple[int, ...]] = tuple(range(8))

MissingEvidenceBehavior: TypeAlias = Literal[
    "render_evidence_gap",
    "render_minimum_verification_question",
    "delete_if_not_applicable",
    "block",
]
EvidenceAvailabilityStatus: TypeAlias = Literal[
    "available",
    "missing",
    "unavailable",
    "not_applicable",
    "unreviewed",
]
AllowedContextLiteral: TypeAlias = Literal[
    "required_label",
    "evidence_gap_statement",
    "quote",
    "anchor_caption",
]
AuditFocusLiteral: TypeAlias = Literal[
    "chapter_structure",
    "evidence_anchors",
    "r_abc",
    "manager_consistency",
    "investor_experience",
    "current_stage",
    "risk",
    "final_judgment",
]
LensKey: TypeAlias = FundType | Literal["default"]

SUPPORTED_AUDIT_FOCUS: Final[tuple[AuditFocusLiteral, ...]] = get_args(AuditFocusLiteral)
SUPPORTED_MISSING_EVIDENCE_BEHAVIORS: Final[tuple[MissingEvidenceBehavior, ...]] = get_args(
    MissingEvidenceBehavior
)
SUPPORTED_EVIDENCE_STATUSES: Final[tuple[EvidenceAvailabilityStatus, ...]] = get_args(
    EvidenceAvailabilityStatus
)
SUPPORTED_ALLOWED_CONTEXTS: Final[tuple[AllowedContextLiteral, ...]] = get_args(
    AllowedContextLiteral
)
AUDIT_FOCUS_IS_SEMANTIC_ONLY: Final[bool] = True


@dataclass(frozen=True, slots=True)
class EvidencePredicate:
    """证据谓词描述。

    Attributes:
        predicate_id: 稳定谓词编号。
        requirement_ids: 谓词依赖的 requirement id。
        required_statuses: 触发谓词所需的证据状态闭集。
        description: 面向 review 的中文说明。
    """

    predicate_id: str
    requirement_ids: tuple[str, ...]
    required_statuses: tuple[EvidenceAvailabilityStatus, ...]
    description: str


@dataclass(frozen=True, slots=True)
class MustAnswerClause:
    """typed must_answer 条款。

    Attributes:
        clause_id: 稳定条款编号。
        text: 模板 JSON 中的原始条款文本。
    """

    clause_id: str
    text: str


@dataclass(frozen=True, slots=True)
class MustNotCoverClause:
    """typed must_not_cover 条款。

    Attributes:
        clause_id: 稳定条款编号。
        text: 模板 JSON 中的原始禁写文本。
        applies_when: 证据条件；为空表示无条件禁写。
        allowed_contexts: 条件禁写允许出现的上下文闭集。
    """

    clause_id: str
    text: str
    applies_when: EvidencePredicate | None = None
    allowed_contexts: tuple[AllowedContextLiteral, ...] = ()


@dataclass(frozen=True, slots=True)
class RequiredOutputItem:
    """typed required_output_items 条目。

    Attributes:
        item_id: 稳定输出条目编号。
        text: 模板 JSON 中的原始 required output 文本。
        when_evidence_missing: 缺证处理行为。
        missing_evidence_reason: 缺证行为的 reviewed typed reason。
    """

    item_id: str
    text: str
    when_evidence_missing: MissingEvidenceBehavior | None = None
    missing_evidence_reason: str | None = None


@dataclass(frozen=True, slots=True)
class TemplateLensRule:
    """typed preferred_lens 规则。

    Attributes:
        fund_type: 当前 lens 对应的标准基金类型或 default。
        statements: 当前 preferred_lens 的说明文本。
        facets_any: 当前 preferred_lens 的细分标签。
        priority: 当前 preferred_lens 的优先级。
    """

    fund_type: LensKey
    statements: tuple[str, ...]
    facets_any: tuple[str, ...] = ()
    priority: str | None = None


@dataclass(frozen=True, slots=True)
class ChapterInternalSubcontract:
    """章节内部 typed subcontract。

    Attributes:
        subcontract_id: 章节内部稳定编号，例如第 2 章的 performance / attribution / cost。
        title: 内部子契约标题。
        requirement_ids: 子契约覆盖的条款或 required output id。
        public_chapter_id: 必须为 `None`，防止 Ch2 子契约变成公开章节。
    """

    subcontract_id: str
    title: str
    requirement_ids: tuple[str, ...]
    public_chapter_id: int | None = None


@dataclass(frozen=True, slots=True)
class TypedChapterContract:
    """typed 单章 CHAPTER_CONTRACT。

    Attributes:
        schema_version: typed schema 版本。
        chapter_id: 公开章节编号，必须保持 0-7。
        title: 章节标题。
        narrative_mode: 当前叙事模式。
        must_answer: typed must_answer 条款。
        must_not_cover: typed must_not_cover 条款。
        required_output_items: typed required output 条目。
        preferred_lens: typed preferred_lens 规则。
        audit_focus: bounded semantic audit 的关注点数据，只作语义强调。
        consumes_chapter_conclusions: 本章消费的其它章节结论编号。
        independent_action_source: 是否允许本章独立派生动作判断。
        internal_subcontracts: 章节内部子契约；当前仅第 2 章允许。
    """

    schema_version: str
    chapter_id: int
    title: str
    narrative_mode: str
    must_answer: tuple[MustAnswerClause, ...]
    must_not_cover: tuple[MustNotCoverClause, ...]
    required_output_items: tuple[RequiredOutputItem, ...]
    preferred_lens: Mapping[str, TemplateLensRule]
    audit_focus: tuple[AuditFocusLiteral, ...]
    consumes_chapter_conclusions: tuple[int, ...] = ()
    independent_action_source: bool = False
    internal_subcontracts: tuple[ChapterInternalSubcontract, ...] = ()


@dataclass(frozen=True, slots=True)
class TypedTemplateContractManifest:
    """typed 模板契约清单。

    Attributes:
        schema_version: typed schema 版本。
        template_id: typed 模板 id。
        source_template_id: 当前 untyped manifest 的 id。
        source_path: 当前模板真源路径。
        chapters: 第 0-7 章 typed contract。
    """

    schema_version: str
    template_id: str
    source_template_id: str
    source_path: str
    chapters: tuple[TypedChapterContract, ...]


def load_typed_template_contract_manifest(
    source_manifest: TemplateContractManifest | None = None,
) -> TypedTemplateContractManifest:
    """读取 typed 模板契约清单。

    Args:
        source_manifest: 可选兼容参数，只用于校验调用方传入的 untyped manifest
            与当前模板文档投影一致；不得用于生成 typed 字段。

    Returns:
        覆盖公开章节 0-7 的 `TypedTemplateContractManifest`。

    Raises:
        ValueError: 传入的 `source_manifest` stale/different，模板 JSON 结构无效，
            或 typed 校验失败时抛出。
    """

    current_manifest = load_template_contract_manifest()
    if source_manifest is not None and source_manifest != current_manifest:
        raise ValueError("source_manifest 与当前模板文档投影不一致")

    raw_manifest = _load_raw_template_contract_manifest()
    chapters = raw_manifest["chapters"]
    if not isinstance(chapters, list):
        raise ValueError("typed manifest.chapters 必须是 array")
    typed_manifest = TypedTemplateContractManifest(
        schema_version=_read_required_string(raw_manifest, "schema_version", "manifest.schema_version"),
        template_id=_read_required_string(raw_manifest, "template_id", "manifest.template_id"),
        source_template_id=_read_required_string(
            raw_manifest,
            "source_template_id",
            "manifest.source_template_id",
        ),
        source_path=_read_required_string(raw_manifest, "source_path", "manifest.source_path"),
        chapters=tuple(_project_typed_chapter(raw_chapter) for raw_chapter in chapters),
    )
    validate_typed_template_contract_manifest(typed_manifest)
    return typed_manifest


def validate_typed_template_contract_manifest(manifest: TypedTemplateContractManifest) -> None:
    """校验 typed 模板契约清单。

    Args:
        manifest: 待校验的 typed manifest。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: schema、章节 id、依赖、Ch2 内部子契约、required output id、
            clause id、`audit_focus` 闭集或 evidence requirement guard 不满足
            fail-closed 约束时抛出。
    """

    if manifest.schema_version != TYPED_TEMPLATE_CONTRACT_SCHEMA_VERSION:
        raise ValueError(f"typed schema_version 不受支持：{manifest.schema_version}")
    if manifest.template_id != TYPED_TEMPLATE_CONTRACT_TEMPLATE_ID:
        raise ValueError(f"typed template_id 不受支持：{manifest.template_id}")
    if not manifest.source_template_id.strip():
        raise ValueError("typed source_template_id 不能为空")
    if not manifest.source_path.strip():
        raise ValueError("typed source_path 不能为空")

    chapter_ids = tuple(chapter.chapter_id for chapter in manifest.chapters)
    if chapter_ids != EXPECTED_PUBLIC_CHAPTER_IDS:
        raise ValueError("typed 公开章节 id 必须精确覆盖 0..7")
    if len(set(chapter_ids)) != len(chapter_ids):
        raise ValueError("typed 公开章节 id 存在重复")

    known_ids = frozenset(chapter_ids)
    all_clause_ids: list[str] = []
    for chapter in manifest.chapters:
        _validate_typed_chapter_contract(chapter, known_ids)
        all_clause_ids.extend(clause.clause_id for clause in chapter.must_answer)
        all_clause_ids.extend(clause.clause_id for clause in chapter.must_not_cover)
    if len(all_clause_ids) != len(set(all_clause_ids)):
        raise ValueError("typed clause_id 存在重复")


def get_typed_chapter_contract(chapter_id: int) -> TypedChapterContract:
    """按公开章节编号读取 typed CHAPTER_CONTRACT。

    Args:
        chapter_id: 公开章节编号，必须为 0-7。

    Returns:
        对应章节的 `TypedChapterContract`。

    Raises:
        ValueError: 章节编号不存在或 typed manifest 校验失败时抛出。
    """

    manifest = load_typed_template_contract_manifest()
    for chapter in manifest.chapters:
        if chapter.chapter_id == chapter_id:
            return chapter
    raise ValueError(f"未找到 typed 模板章节契约：chapter_id={chapter_id}")


def _load_raw_template_contract_manifest(path: str | Path | None = None) -> Mapping[str, Any]:
    """读取并返回模板文档中的 canonical JSON object。

    Args:
        path: 可选模板 Markdown 路径；为空时使用 `contracts.py` 当前默认路径。

    Returns:
        已由 Slice 2 parser 解析出的 raw JSON object。

    Raises:
        ValueError: 模板文档读取失败、JSON 区块非法或 untyped 投影校验失败时抛出。
    """

    template_path = Path(path) if path is not None else contracts_module._DEFAULT_TEMPLATE_PATH
    # 先走 Slice 2 的严格 untyped parser/validator，确保 typed 投影与同一文档真源共享校验入口。
    contracts_module._load_template_contract_manifest_from_path(template_path)
    try:
        template_text = template_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"读取 typed 模板契约文档失败：{template_path}") from exc
    return contracts_module._parse_template_contract_manifest_json(template_text)


def _project_typed_chapter(raw_chapter: Mapping[str, Any]) -> TypedChapterContract:
    """把单章模板 JSON 投影为 typed 章节契约。

    Args:
        raw_chapter: 单章 canonical JSON object。

    Returns:
        typed 单章契约。

    Raises:
        ValueError: typed 字段类型不符合 dataclass 投影要求时抛出。
    """

    chapter_id = _read_required_int(raw_chapter, "chapter_id", "chapter.chapter_id")
    return TypedChapterContract(
        schema_version=TYPED_TEMPLATE_CONTRACT_SCHEMA_VERSION,
        chapter_id=chapter_id,
        title=_read_required_string(raw_chapter, "title", f"chapter[{chapter_id}].title"),
        narrative_mode=_read_required_string(
            raw_chapter,
            "narrative_mode",
            f"chapter[{chapter_id}].narrative_mode",
        ),
        must_answer=_project_must_answer_entries(
            raw_chapter["must_answer"],
            f"chapter[{chapter_id}].must_answer",
        ),
        must_not_cover=_project_must_not_cover_entries(
            raw_chapter["must_not_cover"],
            f"chapter[{chapter_id}].must_not_cover",
        ),
        required_output_items=_project_required_output_entries(
            raw_chapter["required_output_items"],
            f"chapter[{chapter_id}].required_output_items",
        ),
        preferred_lens=_project_typed_lens_rules(
            raw_chapter["preferred_lens"],
            f"chapter[{chapter_id}].preferred_lens",
        ),
        audit_focus=tuple(
            cast(AuditFocusLiteral, value)
            for value in _read_string_array(
                raw_chapter["audit_focus"],
                f"chapter[{chapter_id}].audit_focus",
                allow_empty=False,
            )
        ),
        consumes_chapter_conclusions=tuple(
            _read_int_array(
                raw_chapter["consumes_chapter_conclusions"],
                f"chapter[{chapter_id}].consumes_chapter_conclusions",
            )
        ),
        independent_action_source=_read_required_bool(
            raw_chapter,
            "independent_action_source",
            f"chapter[{chapter_id}].independent_action_source",
        ),
        internal_subcontracts=_project_internal_subcontracts(
            raw_chapter["internal_subcontracts"],
            f"chapter[{chapter_id}].internal_subcontracts",
        ),
    )


def _project_must_answer_entries(raw_entries: Any, path: str) -> tuple[MustAnswerClause, ...]:
    """投影 must_answer 条目。

    Args:
        raw_entries: 模板 JSON 中的 must_answer array。
        path: 错误路径。

    Returns:
        typed must_answer 条款元组。

    Raises:
        ValueError: 条目不是 object 或字段不是非空字符串时抛出。
    """

    return tuple(
        MustAnswerClause(
            clause_id=_read_required_string(entry, "id", f"{path}[{index}].id"),
            text=_read_required_string(entry, "text", f"{path}[{index}].text"),
        )
        for index, entry in enumerate(_read_mapping_array(raw_entries, path, allow_empty=False))
    )


def _project_must_not_cover_entries(raw_entries: Any, path: str) -> tuple[MustNotCoverClause, ...]:
    """投影 must_not_cover 条目。

    Args:
        raw_entries: 模板 JSON 中的 must_not_cover array。
        path: 错误路径。

    Returns:
        typed must_not_cover 条款元组。

    Raises:
        ValueError: 条目、predicate 或 allowed_contexts 类型无效时抛出。
    """

    clauses: list[MustNotCoverClause] = []
    for index, entry in enumerate(_read_mapping_array(raw_entries, path, allow_empty=False)):
        entry_path = f"{path}[{index}]"
        applies_when = entry["applies_when"]
        clauses.append(
            MustNotCoverClause(
                clause_id=_read_required_string(entry, "id", f"{entry_path}.id"),
                text=_read_required_string(entry, "text", f"{entry_path}.text"),
                applies_when=(
                    None
                    if applies_when is None
                    else _project_evidence_predicate(applies_when, f"{entry_path}.applies_when")
                ),
                allowed_contexts=tuple(
                    cast(AllowedContextLiteral, value)
                    for value in _read_string_array(
                        entry["allowed_contexts"],
                        f"{entry_path}.allowed_contexts",
                        allow_empty=True,
                    )
                ),
            )
        )
    return tuple(clauses)


def _project_required_output_entries(raw_entries: Any, path: str) -> tuple[RequiredOutputItem, ...]:
    """投影 required_output_items 条目。

    Args:
        raw_entries: 模板 JSON 中的 required_output_items array。
        path: 错误路径。

    Returns:
        typed required output 条目元组。

    Raises:
        ValueError: 缺证行为或原因字段类型无效时抛出。
    """

    items: list[RequiredOutputItem] = []
    for index, entry in enumerate(_read_mapping_array(raw_entries, path, allow_empty=False)):
        entry_path = f"{path}[{index}]"
        behavior = _read_optional_string(
            entry,
            "when_evidence_missing",
            f"{entry_path}.when_evidence_missing",
        )
        items.append(
            RequiredOutputItem(
                item_id=_read_required_string(entry, "id", f"{entry_path}.id"),
                text=_read_required_string(entry, "text", f"{entry_path}.text"),
                when_evidence_missing=cast(MissingEvidenceBehavior | None, behavior),
                missing_evidence_reason=_read_optional_string(
                    entry,
                    "missing_evidence_reason",
                    f"{entry_path}.missing_evidence_reason",
                ),
            )
        )
    return tuple(items)


def _project_typed_lens_rules(raw_lens: Any, path: str) -> Mapping[str, TemplateLensRule]:
    """投影 preferred_lens 规则。

    Args:
        raw_lens: 模板 JSON 中的 preferred_lens object。
        path: 错误路径。

    Returns:
        typed preferred_lens 映射。

    Raises:
        ValueError: lens object 或字段类型无效时抛出。
    """

    if not isinstance(raw_lens, dict):
        raise ValueError(f"{path} 必须是 object")
    projected: dict[str, TemplateLensRule] = {}
    for lens_key, raw_rule in raw_lens.items():
        rule_path = f"{path}.{lens_key}"
        if not isinstance(lens_key, str) or not isinstance(raw_rule, dict):
            raise ValueError(f"{rule_path} 必须是 object")
        projected[lens_key] = TemplateLensRule(
            fund_type=cast(
                LensKey,
                _read_required_string(raw_rule, "fund_type", f"{rule_path}.fund_type"),
            ),
            statements=tuple(
                _read_string_array(raw_rule["statements"], f"{rule_path}.statements", allow_empty=False)
            ),
            facets_any=tuple(
                _read_string_array(raw_rule["facets_any"], f"{rule_path}.facets_any", allow_empty=True)
            ),
            priority=_read_optional_string(raw_rule, "priority", f"{rule_path}.priority"),
        )
    return projected


def _project_internal_subcontracts(raw_subcontracts: Any, path: str) -> tuple[ChapterInternalSubcontract, ...]:
    """投影章节内部 subcontract。

    Args:
        raw_subcontracts: 模板 JSON 中的 internal_subcontracts array。
        path: 错误路径。

    Returns:
        typed internal subcontract 元组。

    Raises:
        ValueError: subcontract array 或字段类型无效时抛出。
    """

    subcontracts: list[ChapterInternalSubcontract] = []
    for index, entry in enumerate(_read_mapping_array(raw_subcontracts, path, allow_empty=True)):
        entry_path = f"{path}[{index}]"
        subcontracts.append(
            ChapterInternalSubcontract(
                subcontract_id=_read_required_string(entry, "subcontract_id", f"{entry_path}.subcontract_id"),
                title=_read_required_string(entry, "title", f"{entry_path}.title"),
                requirement_ids=tuple(
                    _read_string_array(
                        entry["requirement_ids"],
                        f"{entry_path}.requirement_ids",
                        allow_empty=False,
                    )
                ),
                public_chapter_id=_read_optional_int(
                    entry,
                    "public_chapter_id",
                    f"{entry_path}.public_chapter_id",
                ),
            )
        )
    return tuple(subcontracts)


def _project_evidence_predicate(raw_predicate: Any, path: str) -> EvidencePredicate:
    """投影 evidence predicate。

    Args:
        raw_predicate: 模板 JSON 中的 applies_when object。
        path: 错误路径。

    Returns:
        typed evidence predicate。

    Raises:
        ValueError: predicate 不是 object 或字段类型无效时抛出。
    """

    if not isinstance(raw_predicate, dict):
        raise ValueError(f"{path} 必须是 object")
    return EvidencePredicate(
        predicate_id=_read_required_string(raw_predicate, "predicate_id", f"{path}.predicate_id"),
        requirement_ids=tuple(
            _read_string_array(
                raw_predicate["requirement_ids"],
                f"{path}.requirement_ids",
                allow_empty=False,
            )
        ),
        required_statuses=tuple(
            cast(EvidenceAvailabilityStatus, value)
            for value in _read_string_array(
                raw_predicate["required_statuses"],
                f"{path}.required_statuses",
                allow_empty=False,
            )
        ),
        description=_read_required_string(raw_predicate, "description", f"{path}.description"),
    )


def _validate_typed_chapter_contract(
    chapter: TypedChapterContract,
    known_chapter_ids: frozenset[int],
) -> None:
    """校验 typed 单章契约。

    Args:
        chapter: 待校验的 typed 章节契约。
        known_chapter_ids: manifest 中已知公开章节 id 集合。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: 单章 schema、依赖、条款、required output、audit_focus 或内部子契约无效时抛出。
    """

    if chapter.schema_version != TYPED_TEMPLATE_CONTRACT_SCHEMA_VERSION:
        raise ValueError(f"章节 {chapter.chapter_id} typed schema_version 不受支持")
    if chapter.chapter_id not in EXPECTED_PUBLIC_CHAPTER_IDS:
        raise ValueError(f"不支持的 typed 公开章节 id：{chapter.chapter_id}")
    if not chapter.title.strip():
        raise ValueError(f"typed 章节 {chapter.chapter_id} 标题不能为空")
    if not chapter.narrative_mode.strip():
        raise ValueError(f"typed 章节 {chapter.chapter_id} narrative_mode 不能为空")
    _validate_non_empty_unique_clause_ids(chapter.must_answer, "must_answer", chapter.chapter_id)
    _validate_non_empty_unique_clause_ids(chapter.must_not_cover, "must_not_cover", chapter.chapter_id)
    _validate_required_output_items(chapter)
    _validate_preferred_lens(chapter)
    _validate_dependencies(chapter, known_chapter_ids)
    _validate_audit_focus(chapter)
    _validate_internal_subcontracts(chapter)


def _validate_non_empty_unique_clause_ids(
    clauses: tuple[MustAnswerClause, ...] | tuple[MustNotCoverClause, ...],
    field_name: str,
    chapter_id: int,
) -> None:
    """校验 clause id 非空且局部唯一。

    Args:
        clauses: 待校验的 clause 序列。
        field_name: 字段名。
        chapter_id: 当前章节编号。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: clause 为空、id 为空、文本为空或 id 重复时抛出。
    """

    if not clauses:
        raise ValueError(f"typed 章节 {chapter_id} {field_name} 不能为空")
    clause_ids = tuple(clause.clause_id for clause in clauses)
    if len(set(clause_ids)) != len(clause_ids):
        raise ValueError(f"typed 章节 {chapter_id} {field_name} clause_id 存在重复")
    for clause in clauses:
        if not clause.clause_id.strip():
            raise ValueError(f"typed 章节 {chapter_id} {field_name} clause_id 不能为空")
        if not clause.clause_id.startswith(f"ch{chapter_id}.{field_name}."):
            raise ValueError(f"typed 章节 {chapter_id} {field_name} clause_id 前缀不稳定")
        if not clause.text.strip():
            raise ValueError(f"typed 章节 {chapter_id} {field_name} text 不能为空")
        if isinstance(clause, MustNotCoverClause):
            _validate_must_not_cover_clause(chapter_id, clause)


def _validate_must_not_cover_clause(chapter_id: int, clause: MustNotCoverClause) -> None:
    """校验 typed must_not_cover clause。

    Args:
        chapter_id: 当前章节编号。
        clause: 待校验的 must_not_cover clause。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: evidence predicate 或 allowed_contexts 不满足闭集约束时抛出。
    """

    if clause.applies_when is not None:
        _validate_evidence_predicate(chapter_id, clause.applies_when)
        if not clause.allowed_contexts:
            raise ValueError(f"typed 章节 {chapter_id} conditional must_not_cover 缺少 allowed_contexts")
    elif clause.allowed_contexts:
        raise ValueError(f"typed 章节 {chapter_id} allowed_contexts 必须有 applies_when")
    for context in clause.allowed_contexts:
        if context not in SUPPORTED_ALLOWED_CONTEXTS:
            raise ValueError(f"typed 章节 {chapter_id} allowed_context 不受支持：{context}")


def _validate_evidence_predicate(chapter_id: int, predicate: EvidencePredicate) -> None:
    """校验证据谓词数据。

    Args:
        chapter_id: 当前章节编号。
        predicate: 待校验的证据谓词。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: 谓词 id、requirement id、证据状态或说明无效时抛出。
    """

    if not predicate.predicate_id.strip():
        raise ValueError(f"typed 章节 {chapter_id} evidence predicate id 不能为空")
    if not predicate.requirement_ids:
        raise ValueError(f"typed 章节 {chapter_id} evidence predicate requirement_ids 不能为空")
    known_requirement_ids = _known_evidence_requirement_ids()
    for requirement_id in predicate.requirement_ids:
        if not requirement_id.strip():
            raise ValueError(f"typed 章节 {chapter_id} evidence predicate requirement_id 不能为空")
        if requirement_id not in known_requirement_ids:
            raise ValueError(
                f"typed 章节 {chapter_id} evidence predicate requirement_id 不受支持：{requirement_id}"
            )
    if not predicate.required_statuses:
        raise ValueError(f"typed 章节 {chapter_id} evidence predicate statuses 不能为空")
    for status in predicate.required_statuses:
        if status not in SUPPORTED_EVIDENCE_STATUSES:
            raise ValueError(f"typed 章节 {chapter_id} evidence status 不受支持：{status}")
    if not predicate.description.strip():
        raise ValueError(f"typed 章节 {chapter_id} evidence predicate description 不能为空")


def _validate_required_output_items(chapter: TypedChapterContract) -> None:
    """校验 required output 条目。

    Args:
        chapter: 当前 typed 章节契约。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: required output 条目为空、id 重复、文本为空或缺证行为不在闭集中时抛出。
    """

    if not chapter.required_output_items:
        raise ValueError(f"typed 章节 {chapter.chapter_id} required_output_items 不能为空")
    item_ids = tuple(item.item_id for item in chapter.required_output_items)
    if len(set(item_ids)) != len(item_ids):
        raise ValueError(f"typed 章节 {chapter.chapter_id} required_output item_id 存在重复")
    for item in chapter.required_output_items:
        if not item.item_id.strip():
            raise ValueError(f"typed 章节 {chapter.chapter_id} required_output item_id 不能为空")
        if not item.item_id.startswith(f"ch{chapter.chapter_id}.required_output."):
            raise ValueError(f"typed 章节 {chapter.chapter_id} required_output item_id 前缀不稳定")
        if not item.text.strip():
            raise ValueError(f"typed 章节 {chapter.chapter_id} required_output text 不能为空")
        if (
            item.when_evidence_missing is not None
            and item.when_evidence_missing not in SUPPORTED_MISSING_EVIDENCE_BEHAVIORS
        ):
            raise ValueError(
                f"typed 章节 {chapter.chapter_id} missing evidence behavior 不受支持："
                f"{item.when_evidence_missing}"
            )
        if item.when_evidence_missing is not None and item.missing_evidence_reason is None:
            raise ValueError(f"typed 章节 {chapter.chapter_id} missing evidence behavior 缺少 typed reason")
        if item.missing_evidence_reason is not None and not item.missing_evidence_reason.strip():
            raise ValueError(f"typed 章节 {chapter.chapter_id} missing evidence reason 不能为空")


def _validate_preferred_lens(chapter: TypedChapterContract) -> None:
    """校验 typed preferred_lens 规则。

    Args:
        chapter: 当前 typed 章节契约。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: preferred_lens 为空、key 与 fund_type 不一致或 lens 内容为空时抛出。
    """

    if not chapter.preferred_lens:
        raise ValueError(f"typed 章节 {chapter.chapter_id} preferred_lens 不能为空")
    for key, rule in chapter.preferred_lens.items():
        if key != rule.fund_type:
            raise ValueError(f"typed 章节 {chapter.chapter_id} lens key 与 fund_type 不一致：{key}")
        if not rule.statements:
            raise ValueError(f"typed 章节 {chapter.chapter_id} preferred_lens statements 不能为空")
        if any(not statement.strip() for statement in rule.statements):
            raise ValueError(f"typed 章节 {chapter.chapter_id} preferred_lens statements 存在空值")
        if any(not facet.strip() for facet in rule.facets_any):
            raise ValueError(f"typed 章节 {chapter.chapter_id} preferred_lens facets_any 存在空值")
        if rule.priority is not None and not rule.priority.strip():
            raise ValueError(f"typed 章节 {chapter.chapter_id} preferred_lens priority 不能为空")


def _validate_dependencies(
    chapter: TypedChapterContract,
    known_chapter_ids: frozenset[int],
) -> None:
    """校验章节依赖。

    Args:
        chapter: 当前 typed 章节契约。
        known_chapter_ids: manifest 中已知公开章节 id。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: dependency id 未知、重复，或第 0 章未消费第 7 章时抛出。
    """

    dependencies = chapter.consumes_chapter_conclusions
    if len(set(dependencies)) != len(dependencies):
        raise ValueError(f"typed 章节 {chapter.chapter_id} consumes_chapter_conclusions 存在重复")
    unknown = tuple(chapter_id for chapter_id in dependencies if chapter_id not in known_chapter_ids)
    if unknown:
        raise ValueError(f"typed 章节 {chapter.chapter_id} 存在未知 dependency id：{unknown}")
    if chapter.chapter_id == 0 and dependencies != (7,):
        raise ValueError("typed 第 0 章必须消费第 7 章最终判断结论")
    if chapter.chapter_id == 0 and chapter.independent_action_source:
        raise ValueError("typed 第 0 章不得独立派生动作判断")


def _validate_audit_focus(chapter: TypedChapterContract) -> None:
    """校验 audit_focus 闭集。

    Args:
        chapter: 当前 typed 章节契约。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: audit_focus 为空或包含闭集外值时抛出。
    """

    if not chapter.audit_focus:
        raise ValueError(f"typed 章节 {chapter.chapter_id} audit_focus 不能为空")
    for focus in chapter.audit_focus:
        if focus not in SUPPORTED_AUDIT_FOCUS:
            raise ValueError(f"typed 章节 {chapter.chapter_id} audit_focus 不受支持：{focus}")


def _validate_internal_subcontracts(chapter: TypedChapterContract) -> None:
    """校验章节内部子契约。

    Args:
        chapter: 当前 typed 章节契约。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: 非第 2 章存在子契约、第 2 章缺子契约、子契约携带公开章节 id、
            子契约编号无效或 requirement id 不在 strict guard 时抛出。
    """

    if chapter.chapter_id != 2:
        if chapter.internal_subcontracts:
            raise ValueError(f"typed 章节 {chapter.chapter_id} 不允许内部子契约")
        return

    subcontract_ids = tuple(item.subcontract_id for item in chapter.internal_subcontracts)
    if subcontract_ids != ("performance", "attribution", "cost"):
        raise ValueError("typed 第 2 章内部子契约必须为 performance / attribution / cost")
    known_chapter_requirement_ids = {
        *(clause.clause_id for clause in chapter.must_answer),
        *(item.item_id for item in chapter.required_output_items),
    }
    known_evidence_requirement_ids = _known_evidence_requirement_ids()
    for subcontract in chapter.internal_subcontracts:
        if subcontract.public_chapter_id is not None:
            raise ValueError("typed 第 2 章内部子契约不得携带公开 chapter_id")
        if not subcontract.title.strip():
            raise ValueError(f"typed 第 2 章内部子契约 {subcontract.subcontract_id} 标题不能为空")
        if not subcontract.requirement_ids:
            raise ValueError(
                f"typed 第 2 章内部子契约 {subcontract.subcontract_id} requirement_ids 不能为空"
            )
        if any(not requirement_id.strip() for requirement_id in subcontract.requirement_ids):
            raise ValueError(
                f"typed 第 2 章内部子契约 {subcontract.subcontract_id} requirement_id 不能为空"
            )
        unknown_chapter_ids = tuple(
            requirement_id
            for requirement_id in subcontract.requirement_ids
            if requirement_id not in known_chapter_requirement_ids
        )
        if unknown_chapter_ids:
            raise ValueError(
                f"typed 第 2 章内部子契约 {subcontract.subcontract_id} 存在未知 requirement_id："
                f"{unknown_chapter_ids}"
            )
        unknown_evidence_ids = tuple(
            requirement_id
            for requirement_id in subcontract.requirement_ids
            if requirement_id not in known_evidence_requirement_ids
        )
        if unknown_evidence_ids:
            raise ValueError(
                f"typed 第 2 章内部子契约 {subcontract.subcontract_id} requirement_id 不受支持："
                f"{unknown_evidence_ids}"
            )


def _known_evidence_requirement_ids() -> frozenset[str]:
    """读取证据 availability 的 strict requirement id guard。

    Returns:
        `EvidenceRequirementId` 当前闭集。

    Raises:
        ValueError: guard 不存在或不是 frozenset 时抛出。
    """

    from fund_agent.fund.evidence_availability import _KNOWN_REQUIREMENT_IDS

    if not isinstance(_KNOWN_REQUIREMENT_IDS, frozenset):
        raise ValueError("EvidenceRequirementId guard 不是 frozenset")
    return _KNOWN_REQUIREMENT_IDS


def _read_mapping_array(value: Any, path: str, *, allow_empty: bool) -> tuple[Mapping[str, Any], ...]:
    """读取 JSON object array。

    Args:
        value: 待读取的 JSON value。
        path: 错误路径。
        allow_empty: 是否允许空数组。

    Returns:
        object 元组。

    Raises:
        ValueError: 值不是 array、空数组不被允许或成员不是 object 时抛出。
    """

    if not isinstance(value, list):
        raise ValueError(f"{path} 必须是 array")
    if not allow_empty and not value:
        raise ValueError(f"{path} 不能为空")
    entries: list[Mapping[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise ValueError(f"{path}[{index}] 必须是 object")
        entries.append(item)
    return tuple(entries)


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


def _read_int_array(value: Any, path: str) -> tuple[int, ...]:
    """读取整数数组。

    Args:
        value: 待读取的 JSON value。
        path: 错误路径。

    Returns:
        整数元组。

    Raises:
        ValueError: 值不是 array 或成员不是 integer 时抛出。
    """

    if not isinstance(value, list):
        raise ValueError(f"{path} 必须是 array")
    for index, item in enumerate(value):
        if not isinstance(item, int) or isinstance(item, bool):
            raise ValueError(f"{path}[{index}] 必须是 integer")
    return tuple(value)


def _read_required_string(data: Mapping[str, Any], key: str, path: str) -> str:
    """读取必需非空字符串字段。

    Args:
        data: JSON object。
        key: 字段名。
        path: 错误路径。

    Returns:
        原始字符串值。

    Raises:
        ValueError: 字段不是非空字符串时抛出。
    """

    value = data[key]
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{path} 必须是非空字符串")
    return value


def _read_optional_string(data: Mapping[str, Any], key: str, path: str) -> str | None:
    """读取可空字符串字段。

    Args:
        data: JSON object。
        key: 字段名。
        path: 错误路径。

    Returns:
        `None` 或非空字符串。

    Raises:
        ValueError: 字段不是 `None` 或非空字符串时抛出。
    """

    value = data[key]
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{path} 必须是非空字符串或 null")
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


def _read_optional_int(data: Mapping[str, Any], key: str, path: str) -> int | None:
    """读取可空整数字段。

    Args:
        data: JSON object。
        key: 字段名。
        path: 错误路径。

    Returns:
        `None` 或整数字段值。

    Raises:
        ValueError: 字段不是 `None`、整数或是 boolean 时抛出。
    """

    value = data[key]
    if value is None:
        return None
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"{path} 必须是 integer 或 null")
    return value


def _read_required_bool(data: Mapping[str, Any], key: str, path: str) -> bool:
    """读取必需布尔字段。

    Args:
        data: JSON object。
        key: 字段名。
        path: 错误路径。

    Returns:
        布尔字段值。

    Raises:
        ValueError: 字段不是 boolean 时抛出。
    """

    value = data[key]
    if not isinstance(value, bool):
        raise ValueError(f"{path} 必须是 boolean")
    return value


__all__ = [
    "AUDIT_FOCUS_IS_SEMANTIC_ONLY",
    "EXPECTED_PUBLIC_CHAPTER_IDS",
    "TYPED_TEMPLATE_CONTRACT_SCHEMA_VERSION",
    "TYPED_TEMPLATE_CONTRACT_TEMPLATE_ID",
    "AllowedContextLiteral",
    "AuditFocusLiteral",
    "ChapterInternalSubcontract",
    "EvidenceAvailabilityStatus",
    "EvidencePredicate",
    "MissingEvidenceBehavior",
    "MustAnswerClause",
    "MustNotCoverClause",
    "RequiredOutputItem",
    "SUPPORTED_AUDIT_FOCUS",
    "SUPPORTED_MISSING_EVIDENCE_BEHAVIORS",
    "TemplateLensRule",
    "TypedChapterContract",
    "TypedTemplateContractManifest",
    "get_typed_chapter_contract",
    "load_typed_template_contract_manifest",
    "validate_typed_template_contract_manifest",
]
