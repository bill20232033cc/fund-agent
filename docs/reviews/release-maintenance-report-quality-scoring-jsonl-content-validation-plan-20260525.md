# Release Maintenance Report-Quality Scoring JSONL Content Validation Plan

> Gate: `report-quality scoring JSONL content validation plan`
> Role: AgentCodex planning specialist
> Date: 2026-05-25
> Truth sources: `AGENTS.md`, `docs/implementation-control.md`, `docs/design.md` §5.4 / §5.4.1 / §5.4.2 / §7.1-§7.6, current `fund_agent/fund/report_evidence.py`, `fund_agent/fund/extraction_score.py`, `fund_agent/fund/quality_gate.py`, and adjacent tests.

## 1. 当前事实与非目标

### 当前事实

1. `docs/design.md` §5.4 已接受的方向是先让报告质量“可评分、可复盘”，再决定数据源、抽取、模板或写作迭代；当前 `fund-analysis analyze` 仍是 v0 确定性 8 章 renderer，不声明章节级 LLM 写作、修复闭环或 Dayu Host/Agent runtime 已实现。
2. `docs/design.md` §5.4.1 定义 report-quality scoring 维度：`fact_coverage`、`extraction_correctness`、`evidence_traceability`、`chapter_contract_completeness`、`final_judgment_consistency`、`investment_advice_boundary`、`readability_actionability`，现有 `ReportScoreIssueLink` 还包含 `chapter_summary` 作为跳过章节汇总语义。
3. `docs/design.md` §5.4.2 定义 Fact / Evidence 输入契约：`facts`、`derived_calculations`、`evidence_anchors`、`data_gaps`、`quality_context`。写作、审计和评分只能读取结构化 bundle，不得直接读取 PDF、cache、下载 helper 或来源适配器。
4. 当前已接受实现 `fund_agent/fund/report_evidence.py` 提供 frozen slotted typed model：`ReportEvidenceBundle`、`ReportFact`、`ReportEvidenceAnchor`、`ReportDataGap`、`ReportScoreIssueLink`、`ReportQualityContext`、`ReportEvidenceProjectionContext` 等，并从 `StructuredFundDataBundle` 投影生成 typed bundle。
5. 当前 `ReportEvidenceBundle` 已有投影期局部校验：
   - context guard：`run_id` / `corpus_id`、`fallback_used`、fail-closed source failure、`external_official`、`accepted_baseline` 强制等；
   - score issue link：missing gap refs、missing anchor refs、`issue/blocked` 必须有 severity、`pass` 不得引用 blocking gap、`N/A` 必须有 `na_reason` 或 `reviewer_note`、`chapter_summary` 只能 `skipped`；
   - review status 派生：`rejected > expired > deferred > scoring_ready > fact_prefill_reviewed > fact_prefill_generated > repository_verified > candidate`。
6. 当前 `extraction_score.py` 只消费 P4-S1 `snapshot.jsonl` 并输出 `score.json` / `score.md` / `golden_set.json`；它是字段级 extraction scoring，不是 report-quality issue JSONL content validation。
7. 当前 `quality_gate.py` 只消费 `score.json` 并执行 FQ0-FQ6 gate；它不读取 PDF/cache，不做 LLM 审计，也不验证 `ReportEvidenceBundle` serialization 或 report-quality JSONL。
8. 当前相邻测试覆盖 typed projection、extraction score、FQ0-FQ6 gate；尚无独立 `ReportEvidenceBundle` serialization / report-quality issue JSONL content validator。

### 非目标

本 gate 不替代、不削弱、不重写 FQ0-FQ6；不改变 `quality_gate.py` 的既有 gate semantics。

本 gate 不改 renderer、不改当前 8 章 Markdown 输出、不改 Service 默认行为、不新增 CLI 命令，也不让 `FundAnalysisService` 默认调用新 validator。

本 gate 不创建 `fund_agent/host`、`fund_agent/agent` 包，不引入 `dayu.host` / `dayu.engine`，不实现 session/run/cancel/resume/outbox、tool loop、runner 或 ToolRegistry。

本 gate 不投影 `nav_data`；`nav_data` 仍等待独立 source contract slice。

本 gate 不推广 durable baseline，不创建 curated JSON fixture，不把 `reports/scoring-runs/` scratch 输出纳入长期基准。

本 gate 不读取 PDF/cache/source helper，不调用 `FundDocumentRepository`，不触发任何年报下载、解析或 fallback 编排。

本 gate 不把显式参数塞进 `extra_payload`、`kwargs` 或任意扩展 dict；所有 validator API 参数必须显式声明。

## 2. 推荐实现 Slice

### 推荐文件范围

允许新增：

1. `fund_agent/fund/report_quality_validation.py`
   - Fund capability 内部 validator 模块。
   - 只依赖 `report_evidence.py` 的 typed domains 和 Python 标准库。
   - 提供 JSONL / bundle serialization content validation，不执行 extraction、scoring 计算、quality gate、renderer 或 repository 操作。
2. `tests/fund/test_report_quality_validation.py`
   - 使用 fixture-free fake dictionaries / dataclass records。
   - 覆盖正例、负例矩阵、fail-closed、边界导入检查。

允许最小修改：

1. `fund_agent/fund/report_evidence.py`
   - 仅当实现需要复用 enum domains 或 dataclass serialization helper 时，新增稳定公开 helper，例如 `report_evidence_bundle_to_dict(bundle: ReportEvidenceBundle) -> dict[str, object]`。
   - 不改变 projection behavior，不改变 review_status 派生，不新增 `nav_data` 投影。
2. `tests/fund/test_report_evidence.py`
   - 仅当新增 serialization helper 时增加相邻回归测试。

不建议本 slice 修改：

1. `fund_agent/fund/extraction_score.py`：它属于 P4-S2 snapshot scoring，不应混入 report-quality bundle validation。
2. `fund_agent/fund/quality_gate.py`：FQ0-FQ6 gate 行为保持不变。
3. `fund_agent/cli/`、Service、renderer、config、runtime、Host/Agent/dayu 相关文件：当前没有消费路径，过早接入会扩大 blast radius。
4. README：本计划 artifact 本身不修改 README。若后续 implementation gate 要求 source README 同步，应由 controller 明确授权并只做当前模块导读级同步。

### 为什么暂不做 CLI / Service

第一性原理：当前问题不是“用户如何触发 validator”，而是“评分输入本身是否可验证、可复盘、可驱动后续迭代”。在没有 durable baseline / curated fixture / Service 默认流程裁决前，CLI 或 Service 接入会把实验性 validator 误当生产 gate。正确顺序是先提供纯函数 validator 和完整负例矩阵，让后续 gate 再决定是否接入 CLI、Service 或 scoring-run writer。

## 3. 输入 / 输出契约

### 输入优先级

实现应支持两个等价入口，但以 typed domain 为真源：

1. `ReportEvidenceBundle` 或 `Mapping[str, object]` 形式的 bundle serialization。
2. JSONL artifact：每行一个 JSON object，推荐 `record_type` 区分：
   - `record_type="bundle"`：整包 serialization，包含 `facts`、`evidence_anchors`、`data_gaps`、`score_issue_links`、`quality_context`。
   - `record_type="score_issue"`：单条 `ReportScoreIssueLink` serialization。只有在同一 JSONL artifact 内存在一个 `bundle` record 或调用方显式传入 `bundle` 时才允许，因为 issue refs 必须回到同 bundle 校验。

不允许创建与 `ReportEvidenceBundle` / `ReportScoreIssueLink` 平行的 report-quality schema。所有字段名、enum domain、id reference 语义必须复用 `report_evidence.py` 中已有 dataclass 和 `Literal` domain。

### 推荐公开 API

```python
@dataclass(frozen=True, slots=True)
class ReportQualityValidationIssue:
    """单条 report-quality content validation issue。"""

    error_code: str
    severity: Literal["blocking", "material", "minor"]
    record_pointer: str
    message: str
    source_path: str | None = None
    record_type: str | None = None
    record_id: str | None = None
    field_name: str | None = None
    expected: str | None = None
    actual: str | None = None


@dataclass(frozen=True, slots=True)
class ReportQualityValidationSummary:
    """report-quality content validation 汇总。"""

    total_records: int
    blocking_count: int
    material_count: int
    minor_count: int
    error_code_counts: tuple[tuple[str, int], ...]
    scoring_ready_record_count: int
    failed_closed: bool


@dataclass(frozen=True, slots=True)
class ReportQualityValidationResult:
    """report-quality content validation 结果。"""

    source_path: str | None
    run_id: str | None
    schema_version: str | None
    issues: tuple[ReportQualityValidationIssue, ...]
    summary: ReportQualityValidationSummary


def validate_report_quality_bundle(
    bundle: ReportEvidenceBundle | Mapping[str, object],
    *,
    source_path: str | None = None,
    run_id: str | None = None,
) -> ReportQualityValidationResult: ...


def validate_report_quality_jsonl(
    jsonl_path: Path,
    *,
    run_id: str | None = None,
) -> ReportQualityValidationResult: ...
```

API 参数必须显式声明；不得用 `extra_payload`、`**kwargs` 或任意 passthrough dict。

### JSON Pointer / record pointer

`record_pointer` 必须稳定、可定位：

1. JSONL 行级：`line:{line_number}`。
2. bundle 内字段：`line:1/bundle/facts/3/source_anchor_ids/0` 或 `/bundle/facts/3/source_anchor_ids/0`。
3. issue line：`line:7/score_issue/data_gap_refs/0`。

实现可以用轻量 pointer builder，不需要引入 JSON Schema 依赖。

### Serialization 规则

若输入是 dataclass，validator 内部可使用 `dataclasses.asdict()` 转成 JSON-like mapping；tuple/list 在 validation 中统一按 array 处理。不要为了 validator 改变现有 dataclass frozen / tuple 设计。

## 4. 规则集合

### A. Field presence

`bundle` record 必须包含：

`bundle_id`、`schema_version`、`corpus_id`、`fund_code`、`report_year`、`classified_fund_type`、`type_slot_membership_status`、`preferred_lens`、`quality_context`、`review_status`、`source_documents`、`facts`、`derived_calculations`、`evidence_anchors`、`data_gaps`、`score_issue_links`、`validation_messages`。

每个 `ReportScoreIssueLink` 必须包含：

`issue_id`、`score_run_id`、`chapter_id`、`dimension`、`status`、`next_gate_recommendation`、`evidence_anchor_refs`、`data_gap_refs`。

条件必填：

1. `status in {"issue", "blocked"}` 必须有 `severity`。
2. `status == "N/A"` 必须有 `na_reason` 或 `reviewer_note`。
3. `status in {"issue", "blocked"}` 至少应有 `field_path`、`claim_id` 或 `contract_item_id` 之一，用于定位。
4. fact `value is None` 或 `extraction_mode in {"missing", "estimated"}` 时，应有 `failure_category` 或 `data_gap_refs`，否则 material。
5. fact `extraction_mode in {"direct", "derived", "manual_reviewed"}` 且 `value is not None` 时，应有 `source_anchor_ids` 或 `source_boundary=="manual_review"`，否则 material；若该 fact 支撑 scoring_ready，则 blocking。
6. `preferred_lens.chapters[]` 每条记录必须包含 `chapter_id`、`lens_key`、`used_default`、`primary_focus`；缺失为 material，若 bundle 声明 `scoring_ready` 则 blocking。

### B. Enum domain

必须从 `report_evidence.py` 复用以下 Literal domain：

`ClassifiedFundType`、`TypeSlotMembershipStatus`、`DocumentType`、`DocumentIdentityStatus`、`SourceBoundary`、`SourceFailureCategory`、`ReportAnchorSourceKind`、`SourceStrength`、`FactCategory`、`ReportExtractionMode`、`FactUnit`、`GapKind`、`GapFailureCategory`、`DataGapReasonCode`、`ChapterRef`、`ReviewStatus`、`FactReviewStatus`、`SchemaRevisionStatus`、`FQGateStatus`、`ProgrammaticAuditStatus`、`JudgmentConstraint`、`ScoreDimension`、`ScoreRecordStatus`、`ScoreIssueSeverity`、`NextGateRecommendation`、`CalculationFormulaName`、`CalculationStatus`。

实现建议用 `typing.get_args()` 和小型 `_enum_values()` helper 生成 allowlist，避免复制硬编码枚举。

### C. Invalid combinations

必须 fail-closed 的组合：

1. `review_status=="accepted_baseline"`：当前 slice 不允许，blocking。
2. 所有 `review_status=="scoring_ready"` 的前置条件只在 §4.H 实现一次；§4.C 不重复列出 C2-C8。任何 scoring_ready 前置条件违反都统一输出 `RQV_SCORING_READY_PRECONDITION/blocking`，避免同一语义被重复计入 summary。
3. `ReportSourceDocument` fallback consistency 只在 §4.G 实现一次；§4.C 不重复实现 `fallback_allowed` / `fallback_used` 规则，避免同一语义重复输出 `RQV_FALLBACK_CONFLICT`。
4. `fallback_used=True` 且 `source_failure_category` 为 fallback-ineligible 类别时按下列 fail-closed / fallback conflict 规则处理。
5. `fallback_used=True` 且 `source_failure_category in {"schema_drift", "identity_mismatch", "integrity_error"}`：`RQV_FAIL_CLOSED_SOURCE/blocking`。
6. `fallback_used=True` 且 `source_failure_category=="none"`：`RQV_FALLBACK_CONFLICT/blocking`。
7. `source_boundary=="external_official"` 作为年报事实唯一来源边界：blocking。该值当前只能作为未来官方引用 metadata，不授权外部调用。
8. `extraction_mode=="missing"` 且 fact `value is not None`：blocking。
9. `status=="pass"` 且 issue 引用 blocking data gap：blocking。
10. `status=="skipped"` 且 `dimension!="chapter_summary"`：blocking。
11. `dimension=="chapter_summary"` 且 `status!="skipped"`：blocking。
12. `status=="N/A"` 同时存在 `severity`：material；`N/A` 不进入分母，不应携带 issue severity。

### D. ID references

validator 必须构建 bundle-local id 索引：

1. `anchor_ids = {evidence_anchors[].anchor_id}`。
2. `gap_ids = {data_gaps[].gap_id}`。
3. `fact_ids = {facts[].fact_id}`。
4. `issue_ids = {score_issue_links[].issue_id}`。
5. `document_ids = {source_documents[].document_id}`。
6. `calculation_ids = {derived_calculations[].calculation_id}`。

必须校验：

1. fact `source_anchor_ids` 全部存在于 `anchor_ids`。
2. fact `source_document_ids` 全部存在于 `document_ids`。
3. fact `data_gap_refs` 全部存在于 `gap_ids`。
4. fact `score_issue_ids` 全部存在于 `issue_ids`。
5. data gap `related_fact_id` 如果非空，必须存在于 `fact_ids`。
6. data gap `score_issue_ids` 全部存在于 `issue_ids`。
7. score issue `data_gap_refs` 全部存在于 `gap_ids`。
8. score issue `evidence_anchor_refs` 中以 `anchor:` 开头的 ref 必须存在于 `anchor_ids`；非 `anchor:` 的 Markdown review artifact ref 可以保留为字符串，但不能为空白。
9. evidence anchor `document_id` 非空时必须存在于 `document_ids`；缺失为 material，若 bundle 声明 `scoring_ready` 则 blocking。
10. derived calculation `input_fact_ids` 全部存在于 `fact_ids`，`input_anchor_ids` 全部存在于 `anchor_ids`，`data_gap_refs` / `score_issue_ids` 同理。
11. 所有 id 集合不得重复；重复 id 是 blocking，因为会破坏复盘和跨 run diff。

### E. N/A semantics

`N/A` 是“该维度不适用”，不是“缺证据”。规则：

1. `status=="N/A"` 必须提供 `na_reason` 或 `reviewer_note`。
2. `N/A` issue 不应携带 `severity`；携带 severity 时输出 `RQV_NA_SEMANTICS/material`。
3. `N/A` issue 不应引用 blocking `data_gap_refs`；如果是缺证据，应使用 `issue` / `blocked` 和 data gap。
4. `N/A` 不应出现在 `chapter_summary` 维度；章节汇总不可评分应使用 `chapter_summary + skipped`。若同一 record 同时违反 N/A 与 chapter_summary 唯一性，implementation 应只输出一条 canonical issue，优先使用 `RQV_CHAPTER_SUMMARY_SEMANTICS`，避免 summary counts 重复。

### F. chapter_summary semantics

1. `dimension=="chapter_summary"` 必须且只能使用 `status=="skipped"`。
2. `chapter_summary` 必须有 `chapter_id`，不得是 `report_level`，因为它总结具体章节。
3. `chapter_summary` 必须有 `reviewer_note` 或 `problem` 解释为什么 skipped。
4. `chapter_summary` 不得携带 `severity`，除非后续 gate 明确把 skipped summary 变成阻断规则；本 slice 不做。
5. `chapter_summary` status 唯一性由本节作为 canonical location；同一 `dimension/status` 语义错误不得同时输出 `RQV_CHAPTER_SUMMARY_SEMANTICS` 和 `RQV_NA_SEMANTICS`。

### G. Source boundary / failure category

本节是 `ReportSourceDocument` fallback consistency 的唯一 canonical implementation location；所有 `fallback_allowed` / `fallback_used` 与 `source_failure_category` 的一致性违反统一输出 `RQV_FALLBACK_CONFLICT/blocking`，不得在 §4.C 重复 emit。

1. `source_boundary in {"unknown", "probe_only"}` 永远不能进入 `scoring_ready`。
2. `source_failure_category in {"schema_drift", "identity_mismatch", "integrity_error"}` 必须 fail-closed 为 blocking。
3. `source_failure_category=="unknown_upstream_failure_category"` 至少 material；如果 bundle 试图 `scoring_ready`，blocking。
4. `not_found` / `unavailable` 允许 fallback，但 fallback 后仍必须记录 `fallback_used=True` 和原始 failure category；缺失任一为 material。
5. `ReportSourceDocument.fallback_allowed` 必须与 failure category 一致：仅 `not_found` / `unavailable` 为 true；`none`、fail-closed、unknown upstream 均为 false。
6. `ReportSourceDocument.fallback_used=True` 必须同时满足 `fallback_allowed=True`；否则输出 `RQV_FALLBACK_CONFLICT/blocking`。

### H. review_status / scoring_ready preconditions

validator 不重新派生业务状态，但必须验证声明状态与内容不矛盾。本节是 `scoring_ready` 前置条件的唯一 canonical implementation location；implementation 不应在 §4.C 另行实现重复规则。所有 `scoring_ready` 前置条件违反统一输出 `RQV_SCORING_READY_PRECONDITION/blocking`。

`scoring_ready` 前置条件：

1. 非 `ad_hoc` corpus。
2. verified annual report document identity。
3. source boundary 不是 `unknown` / `probe_only` / `external_official` 年报唯一来源。
4. source failure category 为 `none`。
5. classified fund type 不为 `unknown`。
6. slot membership 为 `matches_slot`。
7. preferred_lens 覆盖当前模板第 0-7 章。
8. 不存在 blocking data gap。
9. 不存在 `severity=="blocking"` 的 score issue。
10. `quality_context.fq_gate_status!="block"` 且 `programmatic_audit_status!="block"`。
11. 所有 facts 的 `review_status=="reviewed"`；存在 `not_reviewed` 或 `partially_reviewed` fact 时，bundle-level `scoring_ready` 声明与内容矛盾，blocking。

违反这些条件时 validator 输出 blocking issue，`failed_closed=True`。

### I. data_gap_refs / evidence_anchor_refs 完整性

1. 所有 `data_gap_refs` 必须存在且双向关系尽量闭合：如果 issue 引用 gap，gap 的 `score_issue_ids` 应包含 issue id；缺失是 material，若 scoring_ready 则 blocking。
2. fact 因缺口阻断时，fact 的 `data_gap_refs` 应包含相关 gap；缺失是 material。
3. 关键评分 issue 如果有 `field_path` 且同 bundle 存在对应 fact，fact 的 `score_issue_ids` 应包含 issue id；缺失是 material。
4. anchor ref 只检查存在性和非空，不尝试读取原始文档。

## 5. 错误模型

### Severity

1. `blocking`：输入不可信，必须 fail-closed；不得进入 scoring_ready / durable baseline / downstream scoring consumption。
2. `material`：输入可解析但复盘性不足或链路不闭合；不应晋级 durable baseline，后续迭代必须修复。
3. `minor`：不影响阻断性判断，但影响 hygiene、可读性或统计一致性。

### Error code

建议 error code 使用稳定前缀 `RQV`：

| Code | Severity | 含义 |
|---|---|---|
| `RQV_FIELD_MISSING` | blocking/material | 必填字段缺失或条件必填缺失 |
| `RQV_ENUM_INVALID` | blocking | enum 值不在 `report_evidence.py` domain |
| `RQV_ID_DUPLICATE` | blocking | bundle-local id 重复 |
| `RQV_REF_MISSING` | blocking/material | id reference 指向不存在的 anchor/gap/fact/issue/document |
| `RQV_SCORING_READY_PRECONDITION` | blocking | `scoring_ready` 前置条件不满足 |
| `RQV_FAIL_CLOSED_SOURCE` | blocking | fail-closed source failure 被继续使用或 fallback |
| `RQV_FALLBACK_CONFLICT` | blocking | fallback flag / fallback_allowed 与 failure category 矛盾 |
| `RQV_EXTRACTION_MODE_CONFLICT` | blocking | `missing` 携带非空 value 等矛盾 |
| `RQV_NA_SEMANTICS` | blocking/material | `N/A` 原因、severity、gap ref 语义错误 |
| `RQV_CHAPTER_SUMMARY_SEMANTICS` | blocking/material | `chapter_summary` 与 `skipped` 约束冲突 |
| `RQV_GAP_LINK_INCOMPLETE` | material/blocking | data gap / score issue / fact 双向链接不完整 |
| `RQV_TRACEABILITY_GAP` | material/blocking | 有值事实缺锚点或人工 review 边界 |
| `RQV_JSONL_INVALID` | blocking | JSONL 行不是 JSON object 或解析失败 |
| `RQV_RECORD_TYPE_INVALID` | blocking | `record_type` 缺失或非法 |

### Result metadata

`ReportQualityValidationResult` 必须包含：

1. `source_path`：输入 JSONL 路径或调用方传入路径。
2. `run_id`：调用方显式传入或从 bundle / issue `score_run_id` 推断；多值冲突时 material。
3. `schema_version`：bundle `schema_version`；缺失或不等于 `REPORT_EVIDENCE_SCHEMA_VERSION` 时 blocking。
4. `summary`：
   - `total_records`
   - `blocking_count`
   - `material_count`
   - `minor_count`
   - `error_code_counts`
   - `scoring_ready_record_count`
   - `failed_closed`
5. 每条 issue 必须有 `record_pointer`、`error_code`、`severity`、`message`，并尽量带 `record_id` / `field_name` / `expected` / `actual`。

### Fail-closed

只要存在 `blocking`，`summary.failed_closed=True`。调用方后续可以据此拒绝进入 scoring 或 baseline promotion。validator 自身不抛出业务 validation 异常；只有文件不存在、JSON 解码失败等无法构造结果的技术错误可以抛出，或转换成 `RQV_JSONL_INVALID` 后继续返回，二者在实现中择一但测试必须固定。

推荐：`validate_report_quality_jsonl()` 对单行 JSON decode error 返回 `RQV_JSONL_INVALID` blocking result，不让坏行掩盖其他行；文件不存在仍抛 `FileNotFoundError`。

## 6. 测试计划

### 单测结构

新增 `tests/fund/test_report_quality_validation.py`，全部使用本地 fake records，不读取真实 PDF、cache、repository、reports run 输出或 curated fixtures。

核心测试：

1. `test_valid_scoring_ready_bundle_passes_without_issues`
   - 用 `_valid_bundle_dict()` 构造最小 bundle serialization。
   - 断言 no issues、`failed_closed=False`、summary counts 正确。
2. `test_jsonl_accepts_bundle_record_and_score_issue_records`
   - `tmp_path` 写 JSONL：一行 bundle，一行 score_issue。
   - 断言 refs 回到同 bundle 校验。
3. `test_missing_required_bundle_field_is_blocking`
4. `test_invalid_enum_value_is_blocking`
   - 必须覆盖嵌套 enum，例如 `source_documents[0].source_boundary="invalid_value"` 输出 `RQV_ENUM_INVALID/blocking`。
5. `test_duplicate_ids_are_blocking`
6. `test_missing_anchor_gap_fact_issue_document_refs_are_reported`
7. `test_scoring_ready_blocks_ad_hoc_unknown_type_probe_boundary_unreviewed_facts_and_fail_closed_source`
8. `test_fallback_flags_must_match_failure_category`
9. `test_missing_extraction_mode_with_value_is_blocking`
10. `test_na_requires_reason_uses_material_for_severity_and_does_not_allow_blocking_gap`
11. `test_chapter_summary_requires_skipped_chapter_scope_and_canonical_issue`
12. `test_gap_issue_fact_bidirectional_links_are_material`
13. `test_source_boundary_external_official_cannot_be_annual_report_only_source`
14. `test_jsonl_bad_line_returns_blocking_pointer`
15. `test_validator_does_not_import_repository_source_helpers_dayu_or_quality_gate`
16. `test_no_nav_data_projection_requirement_is_introduced`
17. `test_preferred_lens_chapter_required_fields_are_validated`
18. `test_anchor_document_id_must_exist_in_source_documents`

若 `report_evidence.py` 增加 serialization helper，再补：

19. `tests/fund/test_report_evidence.py::test_report_evidence_bundle_to_dict_preserves_score_issue_and_tuple_arrays`

### 负例矩阵

最少覆盖以下 bad cases：

| Case | Expected |
|---|---|
| `review_status=scoring_ready`, `corpus_id=ad_hoc` | `RQV_SCORING_READY_PRECONDITION/blocking` |
| `review_status=scoring_ready`, `source_boundary=probe_only` | `RQV_SCORING_READY_PRECONDITION/blocking` |
| `review_status=scoring_ready`, any fact `review_status=not_reviewed` or `partially_reviewed` | `RQV_SCORING_READY_PRECONDITION/blocking` |
| `source_failure_category=schema_drift`, `fallback_used=True` | `RQV_FAIL_CLOSED_SOURCE/blocking` |
| `source_failure_category=unknown_upstream_failure_category`, `review_status=scoring_ready` | `RQV_SCORING_READY_PRECONDITION/blocking` |
| `source_documents[0].fallback_allowed=True`, `source_failure_category=none` | `RQV_FALLBACK_CONFLICT/blocking` |
| `source_documents[0].fallback_used=True`, `fallback_allowed=False` | `RQV_FALLBACK_CONFLICT/blocking` |
| `source_documents[0].source_boundary=invalid_value` | `RQV_ENUM_INVALID/blocking` |
| issue `status=N/A` without reason | `RQV_NA_SEMANTICS/material or blocking` |
| issue `status=N/A` with `severity=minor` | `RQV_NA_SEMANTICS/material` |
| issue `dimension=chapter_summary`, `status=pass` | `RQV_CHAPTER_SUMMARY_SEMANTICS/blocking` |
| issue `dimension=chapter_summary`, `status=N/A` | one canonical `RQV_CHAPTER_SUMMARY_SEMANTICS/blocking`, no duplicate `RQV_NA_SEMANTICS` for the same semantic violation |
| issue references missing `gap_id` | `RQV_REF_MISSING/blocking` |
| fact references missing `anchor_id` | `RQV_REF_MISSING/blocking` |
| evidence anchor `document_id=doc:missing` | `RQV_REF_MISSING/material` or blocking if scoring_ready |
| duplicate `fact_id` | `RQV_ID_DUPLICATE/blocking` |
| fact `extraction_mode=missing`, `value` non-null | `RQV_EXTRACTION_MODE_CONFLICT/blocking` |
| `preferred_lens.chapters[0]` missing `primary_focus` | `RQV_FIELD_MISSING/material` or blocking if scoring_ready |

### 验证命令

实现完成后执行：

```bash
python -m pytest tests/fund/test_report_quality_validation.py -q
python -m pytest tests/fund/test_report_evidence.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py -q
python -m pytest tests/fund/test_report_quality_validation.py --cov=fund_agent.fund.report_quality_validation --cov-report=term-missing --cov-fail-under=80
ruff check fund_agent/fund/report_quality_validation.py tests/fund/test_report_quality_validation.py
rg -n "FundDocumentRepository|AnnualReportDocumentCache|AnnualReportPdfAdapter|documents\\.sources|annual_report_pdf|extra_payload|dayu\\.host|dayu\\.engine" fund_agent/fund/report_quality_validation.py tests/fund/test_report_quality_validation.py
rg -n "nav_data" fund_agent/fund/report_quality_validation.py tests/fund/test_report_quality_validation.py
git diff --check
```

如修改了 `report_evidence.py`，扩大命令：

```bash
ruff check fund_agent/fund/report_quality_validation.py fund_agent/fund/report_evidence.py tests/fund/test_report_quality_validation.py tests/fund/test_report_evidence.py
python -m pytest tests/fund/test_report_quality_validation.py tests/fund/test_report_evidence.py -q
```

## 7. 边界检查

实现 Agent 必须逐项确认：

1. 不读取 PDF、cache、下载 helper、source helper。
2. 不调用 `FundDocumentRepository`。
3. 不导入 `fund_agent.fund.documents.*`、`AnnualReportDocumentCache`、`AnnualReportPdfAdapter`。
4. 不导入或触碰 `dayu.host` / `dayu.engine`。
5. 不使用 `extra_payload`、`**kwargs`、任意 passthrough 参数。
6. 不修改 `quality_gate.py` FQ0-FQ6 行为。
7. 不修改 renderer 或 Service 默认行为。
8. 不投影 `nav_data`，不要求 `nav_data` refs。
9. 不创建 durable fixture，不读取 `reports/scoring-runs/` 作为测试 fixture。
10. 不把 validator issue 当作投资建议或最终判断。

## 8. 残留与后续 Gate

1. `nav_data source contract`
   - Owner: future `nav_data` source-contract slice。
   - 本 gate 只验证现有 bundle refs，不新增 `nav_data` fact。
2. `derived_calculations`
   - Owner: future derived-calculation source slice。
   - 本 gate 可校验已存在 calculation record 的 refs 和 enum，但不生成 R=A+B-C、成本估算、温度计或压力测试计算。
3. `durable baseline / curated fixtures`
   - Owner: future baseline-promotion gate。
   - 本 gate 输出 validator，不把任何 local JSONL / scoring run 晋级 fixture。
4. `Host/Agent/dayu`
   - Owner: future explicit Host/Agent gate。
   - 若未来需要 session/run/cancel/resume 或章节 agent 调度，Host 必须用 `dayu.host`，Agent execution 必须用 `dayu.engine`。
5. `guard/fallback hardening`
   - Owner: robustness or scoring-validation follow-up。
   - 当前 plan 覆盖 content validation；projection-context guard tests、review-status fallback-state tests、unknown extraction-mode fallback test 可在本 slice 补一部分，但不要求重构 projection。
6. `fallback upstream failure category for 110020 / 017641 / 017970`
   - Owner: source reliability evidence gate。
   - Validator 只检查 category 是否显式、是否 fail-closed，不恢复历史来源失败原因。
7. `FOF corpus coverage / QDII-FOF taxonomy`
   - Owner: fund-type taxonomy or corpus selection follow-up。
   - Validator 只检查 `type_slot_membership_status` 与 scoring_ready precondition，不裁决 taxonomy。

## 9. Implementation Handoff

给下一位 implementation agent 的步骤：

1. 先重新读取 `AGENTS.md`、`docs/implementation-control.md` Startup Packet / Next Entry Point、`docs/design.md` §5.4 / §5.4.1 / §5.4.2 / §7.1-§7.6、`fund_agent/fund/report_evidence.py` 和本 plan。
2. 确认当前 gate 仍是 `report-quality scoring JSONL content validation`，且 controller 没有新增 CLI/Service/FQ0-FQ6 scope。
3. 新增 `fund_agent/fund/report_quality_validation.py`，定义 validation dataclasses、enum helper、pointer helper、bundle validator、JSONL validator。
4. 从 `report_evidence.py` 导入 typed domain 和 `REPORT_EVIDENCE_SCHEMA_VERSION`；不要复制一套 parallel schema。
5. 先实现 pure Mapping validator，再实现 JSONL wrapper；JSONL wrapper 只负责解析、record_type 分派和 source_path / line pointer。
6. 实现 field presence、enum domain、id index / refs、invalid combinations、`N/A`、`chapter_summary`、source boundary / failure category、scoring_ready preconditions、gap / issue / fact link completeness。
7. 新增 `tests/fund/test_report_quality_validation.py`，用 fake dict/dataclass records 覆盖正例和负例矩阵。
8. 如发现必须新增 serialization helper，最小修改 `report_evidence.py` 并补相邻测试；否则不动现有 projection。
9. 运行本 plan 第 6 节验证命令。
10. 输出 completion report：列出新增/修改文件、validator API、测试命令结果、coverage、边界 `rg` 结果、未覆盖 residual。

### Stop conditions

遇到以下情况立即停止并交回 controller：

1. 需要修改 renderer、Service 默认行为、CLI、`quality_gate.py` FQ0-FQ6 或 `extraction_score.py` scoring semantics。
2. 需要读取真实 PDF/cache/repository/source helper 才能完成测试。
3. 需要新增 `nav_data` projection 或 derived calculation 生成逻辑。
4. 需要创建 durable fixture、baseline 或修改 `reports/` tracked output。
5. 发现 `ReportEvidenceBundle` typed domain 不足以表达 required validation，且必须引入新 schema。
6. 需要引入第三方 JSON Schema dependency。
7. 需要 Host/Agent/dayu runtime。

### Success signals

实现成功的信号：

1. `validate_report_quality_bundle()` 能对 typed bundle serialization 给出结构化 issues 和 summary。
2. `validate_report_quality_jsonl()` 能定位到 JSONL 行和字段 pointer。
3. 所有 blocking invalid combinations fail-closed。
4. `ReportScoreIssueLink` / `data_gap_refs` / `evidence_anchor_refs` 完整性可验证。
5. 新模块单文件 coverage ≥80%。
6. 相邻 `test_report_evidence.py`、`test_extraction_score.py`、`test_quality_gate.py` 回归通过。
7. boundary `rg` 未发现 repository/source helper、`extra_payload`、Dayu 或 accidental `nav_data` projection。
8. 没有修改 renderer、Service 默认行为、FQ0-FQ6、durable fixtures 或 Host/Agent runtime。

## Blocking Open Questions

当前没有阻断 implementation 的 open question。唯一需要 controller 后续裁决的是：implementation gate 是否允许按 AGENTS 文档同步 `fund_agent/fund/README.md` 的模块导读；若不授权，本 slice 仍可先以 source/test 和本 plan artifact 完成。
