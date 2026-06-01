# MVP Gate 1: ChapterFactProvider typed projection plan

日期：2026-05-30

角色：Gateflow planning specialist。本文只写 implementation-ready plan，不实现、不提交、不 push、不开 PR。

## 1. Gate 定位

Gate：`MVP Gate 1: ChapterFactProvider typed projection`

分类：`heavy`。理由：本 gate 新增未来章节写作输入的 typed public contract，涉及 Fund 层公共契约、证据/缺口语义、CHAPTER_CONTRACT / preferred_lens / ITEM_RULE 组合边界。分类不确定时按 `AGENTS.md` 选择更重一级。

目标：把现有 `StructuredFundDataBundle` 投影为章节级 typed input，供后续 Route C chapter writer/auditor 使用。输出必须覆盖：

- `chapter_id` / `title` / `ChapterContract`
- `fund_type` 与分类依据
- deterministic facets
- `preferred_lens` resolution
- `ITEM_RULE` decisions
- fact entries
- evidence anchors
- missing / unavailable / not applicable / unknown semantics
- source field ids

本 gate 是 Fund 层 typed projection，不是 writer、auditor、orchestrator、CLI 或 dayu gate。

## 2. 已读真源与直接证据

本计划基于以下文件，不读取 release maintenance 长账本：

- `docs/current-startup-packet.md`
  - 当前生产路径仍是确定性 `fund-analysis analyze/checklist`。
  - Route C Gate 1 是 `facet_recognizer` + `ChapterFactProvider` / `FundToolService` contract and implementation。
  - 当前没有 LLM writer/audit、write-audit-repair、chapter orchestrator、final assembler、CLI `--use-llm`、Host/Agent/dayu。
- `docs/design.md` §5.4 / §5.4.1 / §5.4.3
  - Future chapter writing input 必须是 structured facts、derived calculations、EvidenceAnchor、data gaps、quality context。
  - Gate 1 消费现有 8 章模板、CHAPTER_CONTRACT、preferred_lens、ITEM_RULE 和 facet catalog。
  - 基金类型 / facet / fact / evidence 语义属于 Agent/Fund；Service 只做 typed invocation 和用例编排。
- `AGENTS.md`
  - 目标边界固定为 `UI -> Service -> Host -> Agent`。
  - `fund_agent/fund` 是当前 Agent 层基金领域能力包，拥有基金类型、CHAPTER_CONTRACT、preferred_lens、ITEM_RULE、证据审计。
  - 年报生产访问必须经过 `FundDocumentRepository`；本 gate 的 projection 不得直接读取 PDF/cache/source/downloader。
  - 禁止把显式业务参数藏入 `extra_payload`。
- `docs/fund-analysis-template-draft.md`
  - 当前模板是 0-7 共 8 章。
  - `CHAPTER_CONTRACT` 给出每章 `must_answer` / `must_not_cover` / `required_output_items` / `preferred_lens`。
  - 当前 `ITEM_RULE` 只覆盖第 1/2 章四条条件规则。
- `fund_agent/fund/fund_type.py`
  - `FundType` 闭集为 `index_fund`、`active_fund`、`bond_fund`、`enhanced_index`、`qdii_fund`、`fof_fund`。
  - `classify_fund_type(report)` 面向原始年报；本 gate 应消费 `StructuredFundDataBundle.basic_identity.value["classified_fund_type"]`，不得重新加载年报。
- `fund_agent/fund/data_extractor.py`
  - `StructuredFundDataBundle` 已包含 identity/profile/benchmark/index/fee/performance/tracking/share/manager/holder/holdings/bond/nav/source provenance。
  - 除 `nav_data` / `source_provenance` 外，多数字段是 `ExtractedField[T]`，带 `value`、`anchors`、`extraction_mode`、`note`。
- `fund_agent/fund/template/contracts.py`
  - `load_template_contract_manifest()`、`get_chapter_contract()`、`resolve_preferred_lens()` 是当前 CHAPTER_CONTRACT / lens 真源。
- `fund_agent/fund/template/item_rules.py`
  - `load_template_item_rule_manifest()`、`evaluate_template_item_rules()` 已实现 deterministic ITEM_RULE，且对 fund type / facet 冲突 fail closed。
- `fund_agent/services/fund_analysis_service.py`
  - 当前 Service 编排 deterministic analyze/checklist，直接调用 Fund public capabilities 是过渡路径。
  - `_extract_fund_type` 当前对缺失分类更硬；本 gate projection 应提供 typed unknown/missing 语义，由后续 Service gate 决定是否阻断。
- `tests/fund/template/*`、`tests/fund/test_data_extractor.py`
  - 现有测试已经覆盖模板 contract、ITEM_RULE、data extractor repository/NAV 降级边界；新测试应复用这些约束，不改现有语义。

## 3. Non-goals

本 gate 明确不做：

- 不做 `chapter_writer`。
- 不做 `chapter_auditor`。
- 不做 `chapter_orchestrator`。
- 不做 write-audit-repair policy。
- 不做 final chapter assembler。
- 不做 CLI `--use-llm`。
- 不做 Host/Agent/dayu 接入。
- 不做 ToolRegistry、ToolTrace、runner、session/run lifecycle、并发、取消、恢复、outbox。
- 不改 deterministic `fund-analysis analyze/checklist` 行为。
- 不改 renderer 输出、programmatic audit、FQ0-FQ6、quality gate 语义、final judgment 语义。
- 不改 golden fixtures、golden answers、snapshots、score、promotion state、release readiness。
- 不读取 raw PDF、cache、download helper、annual-report concrete sources 或外部网站。
- 不调用 LLM，不要求 LLM key/API。
- 不修改 `docs/fund-analysis-template-draft.md`。
- 不把当前 8 章模板改写成未来 0-10 章体系。
- 不落完整 `FundToolService`；除非后续 gate 需要，只可在计划中保留 Protocol/未来边界说明。

## 4. 推荐总体方案

新增 Fund 层模块：

- `fund_agent/fund/chapter_facts.py`

该模块只消费：

- `StructuredFundDataBundle`
- `fund_agent.fund.template.contracts`
- `fund_agent.fund.template.item_rules`
- `fund_agent.fund.fund_type.FundType`
- `fund_agent.fund.extractors.models.EvidenceAnchor` / `ExtractedField` 类型

不要导入：

- `FundDocumentRepository`
- `AnnualReportDocumentCache`
- PDF parser/downloader/adapter
- annual-report concrete sources
- Service/UI/Host/dayu

推荐 public API：

```python
DEFAULT_CHAPTER_FACT_IDS: tuple[int, ...] = tuple(range(8))
CHAPTER_FACT_SCHEMA_VERSION: Literal["chapter_fact_projection.v1"] = "chapter_fact_projection.v1"

def project_chapter_facts(
    bundle: StructuredFundDataBundle,
    *,
    chapter_ids: tuple[int, ...] = DEFAULT_CHAPTER_FACT_IDS,
) -> ChapterFactProjection:
    ...

class ChapterFactProvider:
    def project(
        self,
        bundle: StructuredFundDataBundle,
        *,
        chapter_ids: tuple[int, ...] = DEFAULT_CHAPTER_FACT_IDS,
    ) -> ChapterFactProjection:
        ...
```

`ChapterFactProvider` 只是 typed provider façade，不是 `FundToolService`，不承担 tool routing、runtime lifecycle 或 Service orchestration。

## 5. Typed contract

所有类型使用 frozen/slotted dataclass。所有类、函数、复杂 helper 必须写完整中文 docstring，且涉及基金模板的 docstring 引用模板章节编号。

### 5.1 Literal aliases

```python
ChapterFactSchemaVersion = Literal["chapter_fact_projection.v1"]
ChapterFactFundType = FundType | Literal["unknown"]

ChapterFactStatus = Literal[
    "available",
    "missing",
    "not_applicable",
    "unavailable",
    "unknown",
]

ChapterFactMissingReason = Literal[
    "classified_fund_type_missing",
    "classified_fund_type_invalid",
    "field_missing",
    "field_not_applicable",
    "field_unavailable",
    "evidence_missing",
    "accepted_chapter_conclusions_missing",
    "cross_period_comparison_missing",
    "unsupported_facet_inference",
]

ChapterFacetStatus = Literal["resolved", "empty", "unknown"]
ChapterFacetSource = Literal["preferred_lens", "item_rule_manifest", "empty", "unknown"]
ChapterEvidenceSourceKind = Literal["annual_report", "external_api", "derived", "unknown"]
```

### 5.2 Dataclasses

`ChapterEvidenceAnchor`

- `anchor_id: str`
- `source_kind: ChapterEvidenceSourceKind`
- `document_year: int | None`
- `section_id: str | None`
- `page_number: int | None`
- `table_id: str | None`
- `row_locator: str | None`
- `note: str | None`

`ChapterFactEntry`

- `fact_id: str`
- `chapter_id: int`
- `field_path: str`
- `source_field_id: str`
- `source_field_name: str`
- `status: ChapterFactStatus`
- `value: object | None`
- `extraction_mode: str | None`
- `evidence_anchor_ids: tuple[str, ...]`
- `missing_reason: ChapterFactMissingReason | None`
- `missing_detail: str | None`
- `required_by: tuple[str, ...]`

`ChapterFacetResolution`

- `chapter_id: int`
- `fund_type: ChapterFactFundType`
- `facets: tuple[str, ...]`
- `status: ChapterFacetStatus`
- `reason: str`
- `source: ChapterFacetSource`
- `non_asserted_facets: tuple[str, ...]`

说明：`facets` 只放当前已确定断言的细分 facet；当前 bundle 没有稳定字段可断言价值/成长/宽基/行业/纯债等 subtype 时，放空。`non_asserted_facets` 可保存 lens/catalog 中兼容的候选标签，供审计解释“为什么没有猜 subtype”。

`ChapterLensResolution`

- `chapter_id: int`
- `fund_type: ChapterFactFundType`
- `lens_key: LensKey | Literal["unknown"]`
- `used_default: bool`
- `statements: tuple[str, ...]`
- `facets_any: tuple[str, ...]`
- `priority: str | None`
- `missing_reason: ChapterFactMissingReason | None`

`ChapterItemRuleProjection`

- `chapter_id: int`
- `decisions: tuple[TemplateItemRuleDecision, ...]`

`ChapterFactInput`

- `chapter_id: int`
- `title: str`
- `contract: ChapterContract`
- `fund_type: ChapterFactFundType`
- `classification_basis: tuple[str, ...]`
- `facet_resolution: ChapterFacetResolution`
- `lens_resolution: ChapterLensResolution`
- `item_rule_projection: ChapterItemRuleProjection`
- `facts: tuple[ChapterFactEntry, ...]`
- `evidence_anchors: tuple[ChapterEvidenceAnchor, ...]`
- `missing_reasons: tuple[ChapterFactMissingReason, ...]`
- `source_field_ids: tuple[str, ...]`

`ChapterFactProjection`

- `schema_version: ChapterFactSchemaVersion`
- `fund_code: str`
- `report_year: int`
- `fund_type: ChapterFactFundType`
- `classification_basis: tuple[str, ...]`
- `chapters: tuple[ChapterFactInput, ...]`
- `global_missing_reasons: tuple[ChapterFactMissingReason, ...]`

## 6. Source field ids

新增模块内显式维护当前 bundle 字段 id，id 稳定、可测试、不可从 `repr` 或字典 key 临时拼接：

```python
_SOURCE_FIELD_IDS: Final[dict[str, str]] = {
    "basic_identity": "structured.basic_identity",
    "product_profile": "structured.product_profile",
    "benchmark": "structured.benchmark",
    "index_profile": "structured.index_profile",
    "fee_schedule": "structured.fee_schedule",
    "turnover_rate": "structured.turnover_rate",
    "nav_benchmark_performance": "structured.nav_benchmark_performance",
    "investor_return": "structured.investor_return",
    "tracking_error": "structured.tracking_error",
    "share_change": "structured.share_change",
    "manager_alignment": "structured.manager_alignment",
    "manager_strategy_text": "structured.manager_strategy_text",
    "holdings_snapshot": "structured.holdings_snapshot",
    "holder_structure": "structured.holder_structure",
    "bond_risk_evidence": "structured.bond_risk_evidence",
    "nav_data": "structured.nav_data",
}
```

`source_provenance` 默认不作为 chapter fact；只有后续 gate 需要 fallback reporting 时再纳入。不能用 `source_provenance` 替代 evidence anchors。

## 7. Chapter field mapping

新增 `_CHAPTER_FIELD_SPECS`，每个 spec 至少包含：

- `chapter_id`
- `field_name`
- `source_field_id`
- `required_by`
- `not_applicable_when`
- `item_rule_ids`

推荐初始映射：

| Chapter | Source fields |
|---|---|
| 0 投资要点概览 | `basic_identity`, `nav_benchmark_performance`, `tracking_error`, `fee_schedule`, `bond_risk_evidence` |
| 1 产品本质 | `basic_identity`, `product_profile`, `benchmark`, `index_profile`, `fee_schedule` |
| 2 R=A+B-C | `nav_benchmark_performance`, `benchmark`, `tracking_error`, `fee_schedule`, `nav_data` |
| 3 基金经理画像 | `basic_identity`, `manager_strategy_text`, `holdings_snapshot`, `turnover_rate`, `manager_alignment`, `holder_structure` |
| 4 投资者获得感 | `nav_benchmark_performance`, `investor_return`, `share_change`, `holder_structure`, `fee_schedule` |
| 5 当前阶段 | `basic_identity`, `share_change`, `holdings_snapshot`, `turnover_rate`, `fee_schedule`, `manager_strategy_text` |
| 6 核心风险 | `basic_identity`, `fee_schedule`, `tracking_error`, `turnover_rate`, `holdings_snapshot`, `share_change`, `bond_risk_evidence`, `nav_data` |
| 7 最终判断 | `basic_identity`, `nav_benchmark_performance`, `tracking_error`, `fee_schedule`, `manager_alignment`, `bond_risk_evidence` |

特殊缺口：

- 第 0 章：`accepted_chapter_conclusions_missing`，因为 Gate 1 没有 accepted chapters，不能伪造封面总结。
- 第 5 章：`cross_period_comparison_missing`，因为当前 bundle 是单期输入，不能伪造跨期变化。
- 第 7 章：`accepted_chapter_conclusions_missing`，因为最终判断未来应消费前章 accepted conclusions，本 gate 不能伪造。

`required_by` 规则：

- 每个 mapped fact 至少包含 `CHAPTER_CONTRACT.chapter_{chapter_id}`。
- 只有映射明确时才加 `CHAPTER_CONTRACT.chapter_{chapter_id}.must_answer[{index}]`。
- 若字段支撑当前章 ITEM_RULE，添加 `ITEM_RULE.{rule_id}`。
- 不要声称某字段已满足整条 `must_answer`，除非该字段就是该问题的直接来源。

## 8. Evidence anchor 规则

Extractor anchor 输入来自 `ExtractedField.anchors`。Projection 必须：

- 对同一 chapter 内 anchors deterministic dedupe，保持首次出现顺序。
- 对同一 locator 生成稳定 `anchor_id`。
- `anchor_id` 推荐格式：
  - `chapter-anchor:{fund_code}:{report_year}:ch{chapter_id}:{source_kind}:{section_or_unknown}:{hash8}`
- hash 输入必须包含 `document_year`、`section_id`、`page_number`、`table_id`、`row_locator`、`note` 的规范化 JSON。
- 若 hash 碰撞，用 `-2`、`-3` 后缀 deterministic 处理。
- `ChapterFactEntry.evidence_anchor_ids` 必须只引用本章 `evidence_anchors` 中存在的 id。
- `direct` / `derived` / `estimated` 字段有 value 但 anchors 为空时：
  - fact `status="available"`
  - `missing_reason="evidence_missing"`
  - `missing_detail` 写明字段有值但缺锚点
- `extraction_mode="missing"` 或 `value is None`：
  - `status="missing"` 或 `not_applicable` / `unavailable`
  - 不创建正向证据 anchor
  - 保留 `ExtractedField.note` 到 `missing_detail`

`bond_risk_evidence.value.anchors` 是组级 anchor ref，不同于普通 `EvidenceAnchor`。本 gate 可先把 `bond_risk_evidence` 作为一个 fact value 投影，并保留其内部 anchor ids 在 value 内；不要强行拆成普通 `ChapterEvidenceAnchor`，除非实现能完整校验引用。

## 9. Missing / unavailable semantics

分类语义：

- `classified_fund_type_missing`
  - `basic_identity.value is None`，或没有 `classified_fund_type`。
- `classified_fund_type_invalid`
  - `classified_fund_type` 不在 `FundType` 闭集。
- `field_missing`
  - `ExtractedField.extraction_mode == "missing"` 且不是明确不适用或不可用。
- `field_not_applicable`
  - 字段按 fund type 明确不适用，例如非指数基金 `tracking_error` note 为非指数不适用，非债券基金 `bond_risk_evidence` note 为 not applicable。
- `field_unavailable`
  - 外部源或 NAV 不可用，例如 `nav_data.unavailable is True`。
- `evidence_missing`
  - 字段有可用值但没有 anchor。
- `accepted_chapter_conclusions_missing`
  - 第 0/7 章需要未来 accepted chapter conclusions，但 Gate 1 尚未有 writer/auditor/orchestrator。
- `cross_period_comparison_missing`
  - 第 5 章需要跨期比较，但当前 bundle 是单期。
- `unsupported_facet_inference`
  - 模板 catalog 有候选 facet，但当前 structured fields 不能 deterministic 断言 subtype。

失败策略：

- fund type unknown 时，不调用 `resolve_preferred_lens()` / `evaluate_template_item_rules()`。
- invalid chapter ids、重复 chapter ids、空 chapter ids：`ValueError` fail closed。
- unknown facet 不得 fail open；必须为空/unknown 并记录原因。
- 不把 `unavailable` 误报为 `not_found` 或普通 missing。

## 10. Deterministic facet inference

允许输入：

- `basic_identity.value["classified_fund_type"]`
- `basic_identity.value["classification_basis"]`
- `basic_identity` / `product_profile` / `benchmark` / `index_profile` / `tracking_error` / `bond_risk_evidence` / `nav_data` / `manager_alignment` / `holder_structure` / `share_change` 等 structured fields
- `ChapterContract.preferred_lens[fund_type].facets_any`
- `TemplateItemRule.facets_any`

禁止输入：

- LLM
- raw PDF text
- cache / source helper
- 外部网站
- 任意 ad hoc NLP over 年报正文

具体规则：

1. fund type missing/invalid：
   - projection fund type 为 `unknown`
   - `facets=()`
   - `non_asserted_facets=()`
   - lens unknown
   - item rule decisions 为空
2. fund type valid：
   - 读取本章 resolved lens 的 `facets_any`。
   - 当前没有稳定 subtype 字段时，`facets=()`，`non_asserted_facets=lens.facets_any`，`status="empty"`，reason 包含 `unsupported_facet_inference`。
   - 若未来某个 structured field 明确存储 exact facet，才允许把该 exact facet 放入 `facets`。
3. ITEM_RULE：
   - 默认调用 `evaluate_template_item_rules(fund_type=fund_type, facets=())`，让 fund type 作为主触发条件。
   - 不把 `non_asserted_facets` 传给 ITEM_RULE，避免把“候选 facet catalog”误当“已识别 subtype”。

## 11. Preferred lens / ITEM_RULE 规则

每章：

- 用 `get_chapter_contract(chapter_id)` 取 contract。
- fund type valid 时用 `resolve_preferred_lens(chapter_id, fund_type)`。
- 保存：
  - `lens_key`
  - `used_default`
  - `statements`
  - `facets_any`
  - `priority`
- fund type unknown 时：
  - `lens_key="unknown"`
  - `statements=()`
  - `facets_any=()`
  - `missing_reason=classified_fund_type_missing|classified_fund_type_invalid`
- projection 级别先调用一次 `evaluate_template_item_rules(fund_type=fund_type, facets=())`。
- 每章只保留 `decision.chapter_id == chapter_id` 的 decisions。
- 不复制/重写 ITEM_RULE manifest 或 CHAPTER_CONTRACT 文案。

## 12. Slice 计划

### Slice 1：新增 contract module

Allowed files：

- `fund_agent/fund/chapter_facts.py`
- `tests/fund/test_chapter_facts.py`

Exact changes：

- 新增 `chapter_facts.py` 模块概览 docstring，说明这是 Fund/Agent 层 typed projection，见模板第 0-7 章。
- 定义 §5 中全部 Literal aliases 与 dataclasses。
- 定义 constants：
  - `CHAPTER_FACT_SCHEMA_VERSION`
  - `DEFAULT_CHAPTER_FACT_IDS`
  - `_SOURCE_FIELD_IDS`
  - `_CHAPTER_FIELD_SPECS`
- 定义 private dataclass `_ChapterFieldSpec`：
  - `chapter_id: int`
  - `field_name: str`
  - `source_field_id: str`
  - `required_by: tuple[str, ...]`
  - `item_rule_ids: tuple[str, ...] = ()`
- 定义 helper stubs 并完成纯校验逻辑：
  - `_validate_chapter_ids(chapter_ids: tuple[int, ...]) -> tuple[int, ...]`
  - `_read_classified_fund_type(bundle: StructuredFundDataBundle) -> tuple[ChapterFactFundType, tuple[str, ...], ChapterFactMissingReason | None]`
  - `_chapter_field_specs(chapter_id: int) -> tuple[_ChapterFieldSpec, ...]`

Tests：

- `test_chapter_id_validation_fails_closed`
- `test_missing_or_invalid_fund_type_yields_unknown_without_lens_or_item_rules` 中的分类读取部分可先覆盖。

Stop condition：

- 如果需要修改 `StructuredFundDataBundle` schema 或 extractor 输出，停止。

### Slice 2：实现 projection 行为

Allowed files：

- `fund_agent/fund/chapter_facts.py`
- `tests/fund/test_chapter_facts.py`

Exact changes：

- 实现 public API：
  - `project_chapter_facts(...)`
  - `ChapterFactProvider.project(...)`
- 实现 helpers：
  - `_project_chapter(...) -> ChapterFactInput`
  - `_resolve_chapter_facets(...) -> ChapterFacetResolution`
  - `_resolve_chapter_lens(...) -> ChapterLensResolution`
  - `_evaluate_item_rule_decisions(...) -> tuple[TemplateItemRuleDecision, ...]`
  - `_item_rule_decisions_for_chapter(...) -> ChapterItemRuleProjection`
  - `_project_field_fact(...) -> tuple[ChapterFactEntry, tuple[ChapterEvidenceAnchor, ...]]`
  - `_project_extracted_field_fact(...)`
  - `_project_nav_data_fact(...)`
  - `_project_synthetic_missing_fact(...)`
  - `_dedupe_chapter_anchors(...)`
  - `_anchor_id_for(...)`
- `project_chapter_facts()` data flow：
  1. validate `chapter_ids`
  2. read fund type from bundle
  3. if valid, evaluate ITEM_RULE once with `facets=()`
  4. for each chapter, get contract, lens, facet resolution, scoped item rule decisions
  5. project mapped fields to facts
  6. append synthetic missing facts for chapter 0/5/7 special缺口
  7. dedupe anchors and ensure all fact anchor refs exist
  8. aggregate chapter/global missing reasons

Tests：

- `test_projects_eight_chapter_inputs_from_structured_bundle`
- `test_preferred_lens_resolution_preserves_default_and_exact_lens`
- `test_item_rule_decisions_are_chapter_scoped_and_fund_type_deterministic`
- `test_facet_resolution_does_not_semantically_guess_subtype`
- `test_missing_field_semantics_and_anchor_traceability`
- `test_projection_does_not_call_repository_or_source_helpers`

Stop condition：

- 如果实现需要调用 repository/source/PDF/cache/downloader/parser 或 LLM，停止。

### Slice 3：public export 与文档最小同步

Allowed files：

- `fund_agent/fund/__init__.py`，仅当仓库当前模式需要 Fund package-level export。
- `fund_agent/fund/README.md`，仅当新增 public Fund capability 后需要同步。
- `tests/README.md`，仅当新增测试分类或命令入口。
- `docs/design.md` / `docs/implementation-control.md`，仅在 controller 明确把 doc sync 纳入 accepted implementation scope 时做最小更新。

Recommended decision：

- 默认不改 Service。
- 默认不改 root README。
- 默认不新增完整 `FundToolService`。
- `fund_agent/fund/README.md` 若更新，只写当前事实：`ChapterFactProvider` 是 Fund 层 typed projection，从 `StructuredFundDataBundle` 生成 chapter facts；不写 writer/auditor/orchestrator/dayu 已实现。

Tests：

- 若只改 README，不需额外测试。
- 若改 `__init__.py` export，`tests/fund/test_chapter_facts.py` 增加 public import smoke test。

Stop condition：

- 如果需要改变 CLI 或 Service result schema，停止并交回 controller。

## 13. Test plan

新增：

- `tests/fund/test_chapter_facts.py`

Required cases：

- `test_projects_eight_chapter_inputs_from_structured_bundle`
  - 构造 fake `StructuredFundDataBundle`。
  - 断言章节 `0..7` 均存在，标题来自 `ChapterContract`。
  - 断言第 1 章包含 `basic_identity` / `product_profile` / `benchmark` / `index_profile`。
  - 断言第 3 章包含 `manager_strategy_text` / `holdings_snapshot` / `turnover_rate` / `manager_alignment`。
- `test_missing_or_invalid_fund_type_yields_unknown_without_lens_or_item_rules`
  - missing 与 invalid fund type 都返回 `fund_type="unknown"`。
  - lens 为 unknown，ITEM_RULE decisions 为空。
  - 不触发 `resolve_preferred_lens()` invalid input。
- `test_preferred_lens_resolution_preserves_default_and_exact_lens`
  - active fund 第 3 章 lens key 为 `active_fund`，priority 为 `core`。
  - 选择一个 fallback default 章节，断言 `used_default=True`。
- `test_item_rule_decisions_are_chapter_scoped_and_fund_type_deterministic`
  - active fund 第 1 章 render manager philosophy，第 2 章 render alpha breakdown。
  - index fund 第 1 章 render index constituents，第 2 章 render tracking error。
  - bond/QDII/FOF 不渲染当前四条 conditional ITEM_RULE。
- `test_facet_resolution_does_not_semantically_guess_subtype`
  - active fund 不猜 value/growth/balanced。
  - compatible catalog labels 出现在 `non_asserted_facets` 或 reason 中，不进入 asserted `facets`。
- `test_missing_field_semantics_and_anchor_traceability`
  - missing `turnover_rate` 在第 3 章产生 `field_missing`。
  - direct value without anchors 产生 `evidence_missing`，但 fact 仍可用。
  - fact anchor refs 均能在本章 anchors 中找到。
- `test_nav_data_unavailable_is_not_plain_missing`
  - `nav_data.unavailable=True` 时相关章节 fact status 为 `unavailable`，reason 为 `field_unavailable`。
- `test_projection_does_not_call_repository_or_source_helpers`
  - 静态断言 `chapter_facts` 模块未暴露/导入 `FundDocumentRepository`、`AnnualReportDocumentCache`、PDF adapter、concrete sources、downloader、parser。
- `test_chapter_id_validation_fails_closed`
  - `()`、重复、负数、`8` 均 `ValueError`。

现有测试：

- 不应修改 `tests/fund/template/test_item_rules.py`、`tests/fund/template/test_contracts.py` 的现有断言。
- 不应修改 `tests/fund/test_data_extractor.py` 的 repository/NAV 降级语义。

Coverage：

- 新增 `chapter_facts.py` 单文件目标 ≥80%。
- 若无法达到，implementation evidence 必须说明未覆盖行、原因和补测计划；项目 CI gate 仍按全局 coverage 命令。

## 14. Validation commands

Targeted：

```bash
uv run pytest tests/fund/test_chapter_facts.py -q
uv run pytest tests/fund/template/test_item_rules.py tests/fund/template/test_contracts.py tests/fund/test_data_extractor.py -q
```

Full required：

```bash
uv run ruff check .
uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q
```

若 implementation 触碰 Service：

```bash
uv run pytest tests/fund/integration/test_p3_cli_e2e_matrix.py tests/fund/test_data_extractor.py -q
```

## 15. Review checklist

Plan review / implementation review 重点：

- 是否只在 Fund 层新增 typed projection。
- 是否没有 writer/auditor/orchestrator/CLI/dayu scope creep。
- 是否没有完整 `FundToolService` 过度设计。
- 是否只消费 `StructuredFundDataBundle` 与 template manifests。
- 是否没有直接读取 PDF/cache/source/downloader/parser。
- 是否 fund type missing/invalid fail closed。
- 是否 facet inference deterministic 且不语义猜 subtype。
- 是否 `preferred_lens` / `ITEM_RULE` 来自现有 truth，不复制规则真源。
- 是否 anchors、missing、unavailable、not applicable、source field ids 可追溯。
- 是否 tests 覆盖 happy path、missing path、invalid input、no-source boundary。

## 16. Stop conditions

发现以下任一需求，停止并交回 controller/user：

- 需要修改模板真源、CHAPTER_CONTRACT、ITEM_RULE 或 facet catalog。
- 需要 LLM key/API、prompt execution、LLM facet classification。
- 需要 Host/Agent/dayu、ToolRegistry、ToolTrace、runner、session/run lifecycle、并发、取消、恢复。
- 需要 golden/quality semantics、strict correctness、snapshot、score、final judgment、promotion、release readiness。
- 需要 push、PR、release、promotion。
- 需要 raw PDF/cache/source helper/downloader/parser 访问。
- 需要修改 CLI `--use-llm` 或当前 deterministic analyze/checklist 行为。
- 需要把未来 0-10 章设计写成当前代码事实。

## 17. Completion report format

Implementation worker 完成后报告：

- Files changed。
- Public contract names and schema version。
- Fund type、facets、preferred_lens、ITEM_RULE、facts、anchors、missing semantics 的实现摘要。
- 确认没有 repository/source/PDF/cache/downloader/parser/LLM/dayu import 或调用。
- Validation commands and results。
- Coverage result，尤其是 `chapter_facts.py` 单文件覆盖率。
- Residual risks and owners。
