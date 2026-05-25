# Implementation Review: Report-Quality Scoring JSONL Content Validation

> Gate: `report-quality scoring JSONL content validation implementation`
> Role: AgentMiMo independent code reviewer
> Date: 2026-05-25
> Truth sources: `AGENTS.md`, `docs/design.md` §5.4 / §5.4.1 / §5.4.2 / §7.1-§7.6, `docs/implementation-control.md` Startup Packet / Next Entry Point, `docs/reviews/release-maintenance-report-quality-scoring-jsonl-content-validation-plan-20260525.md`, controller judgment

## 结论

**PASS_WITH_FINDINGS**

## Review Scope

| File | Status |
|---|---|
| `fund_agent/fund/report_quality_validation.py` | 新增，2392 行 |
| `tests/fund/test_report_quality_validation.py` | 新增，851 行 |
| `fund_agent/fund/README.md` | 最小同步，新增 validator 模块导读（第 99-105 行） |

## Controller 本地验证确认

| Check | Result |
|---|---|
| validator tests | 19 passed |
| adjacent tests | 81 passed |
| coverage | 91% (≥80% target) |
| ruff | All checks passed |
| boundary rg (forbidden imports) | no matches |
| nav_data rg | no matches |
| git diff --check | clean |

## Correctness 审查

### 复用 report_evidence.py typed domains

**PASS** — 实现从 `report_evidence.py` 导入全部 27 个 Literal domain（`ClassifiedFundType`、`TypeSlotMembershipStatus`、`DocumentType`、`DocumentIdentityStatus`、`SourceBoundary`、`SourceFailureCategory`、`ReportAnchorSourceKind`、`SourceStrength`、`FactCategory`、`ReportExtractionMode`、`FactUnit`、`GapKind`、`GapFailureCategory`、`DataGapReasonCode`、`ChapterRef`、`ReviewStatus`、`FactReviewStatus`、`SchemaRevisionStatus`、`FQGateStatus`、`ProgrammaticAuditStatus`、`JudgmentConstraint`、`ScoreDimension`、`ScoreRecordStatus`、`ScoreIssueSeverity`、`NextGateRecommendation`、`CalculationFormulaName`、`CalculationStatus`）和 `REPORT_EVIDENCE_SCHEMA_VERSION`。`_ENUM_FIELDS` 字典完整覆盖，使用 `typing.get_args()` 递归展开，无 parallel schema。

### API 契约

**PASS** — `validate_report_quality_bundle()` 和 `validate_report_quality_jsonl()` 签名与 plan §3 推荐 API 完全一致。参数显式声明，无 `extra_payload`、`**kwargs` 或 passthrough dict。

### JSONL record_type / pointer / run_id / schema_version / summary

**PASS** — JSONL 支持 `record_type="bundle"` 和 `record_type="score_issue"`。pointer 稳定：行级 `line:{n}`，bundle 内 `/bundle/...`，issue 行 `line:{n}/score_issue`。`run_id` 从显式参数或 `score_run_id` 推断，多值冲突为 material。`schema_version` 校验 `REPORT_EVIDENCE_SCHEMA_VERSION`。summary 包含 `total_records`、`blocking_count`、`material_count`、`minor_count`、`error_code_counts`、`scoring_ready_record_count`、`failed_closed`。

### scoring_ready canonical preconditions

**PASS** — 实现在 `_validate_scoring_ready_preconditions()` 统一输出 `RQV_SCORING_READY_PRECONDITION/blocking`，覆盖 plan §4.H 全部 11 项。不在 §4.C 重复 emit。违反时 `failed_closed=True`。

### fallback consistency canonical §4.G

**PASS** — 实现在 `_validate_source_documents()` 统一处理 `fallback_allowed` / `fallback_used` 与 `source_failure_category` 一致性，输出 `RQV_FALLBACK_CONFLICT/blocking`。fail-closed 类别输出 `RQV_FAIL_CLOSED_SOURCE/blocking`。不在 §4.C 重复 emit。

### N/A 与 chapter_summary canonical issue 去重

**PASS** — `_validate_single_score_issue()` 中 `dimension=="chapter_summary"` 优先走 `_validate_chapter_summary_issue()`，`status=="N/A"` 走 `_validate_na_issue()`。当同一 record 同时违反时，只输出 canonical `RQV_CHAPTER_SUMMARY_SEMANTICS`，不输出 `RQV_NA_SEMANTICS`。test 验证无 duplicate。

### id refs / anchor.document_id / preferred_lens required fields / fact/gap/issue link completeness

**PASS** — bundle-local id 索引覆盖 `anchor_ids`、`gap_ids`、`fact_ids`、`issue_ids`、`document_ids`、`calculation_ids`。重复 id 为 blocking。`_validate_ref()` 校验全部 plan §4.D 引用关系。`evidence_anchor[].document_id` 校验指向 `source_documents`，severity 按 scoring_ready 区分。preferred_lens chapters 必填字段 `chapter_id`、`lens_key`、`used_default`、`primary_focus` 校验完整。fact/gap/issue 双向链接完整性由 `_validate_link_completeness()` 覆盖。

### 边界约束

**PASS** — 不改/不导入 renderer、Service、CLI、quality_gate.py FQ0-FQ6、extraction_score semantics、repository/PDF/cache/source helper、Host/Agent/dayu、nav_data。boundary rg 确认无匹配。

## Findings

### F1 [minor] chapter_summary report_level 校验重复输出

**文件**: `fund_agent/fund/report_quality_validation.py`
**行号**: 1512-1525, 1630-1643

**描述**: 当 `scoring_ready=True` 且 `chapter_summary` 的 `chapter_id=="report_level"` 时，校验输出 **两条** `RQV_CHAPTER_SUMMARY_SEMANTICS/blocking` issue：

1. `_validate_chapter_summary_issue()` 第 1630-1643 行：无条件检查 `chapter_id=="report_level"`。
2. `_validate_single_score_issue()` 第 1512-1525 行：`scoring_ready` 条件下再次检查同一语义。

两条 issue pointer 相同（`/bundle/score_issue_links/0/chapter_id`），severity 相同（blocking），message 近似。违反 plan §4.F.5 原则："chapter_summary status 唯一性由本节作为 canonical location；同一 dimension/status 语义错误不得同时输出 RQV_CHAPTER_SUMMARY_SEMANTICS 和 RQV_NA_SEMANTICS"——同理，同一语义不应在两处各输出一条 canonical issue。

**影响**: `blocking_count` 被重复计入 1，`error_code_counts` 中 `RQV_CHAPTER_SUMMARY_SEMANTICS` 计数偏高。不影响 fail-closed 判断（已 blocking），但影响 summary 统计准确性。

**复现**:
```python
bundle = _valid_bundle_dict()  # scoring_ready
bundle['score_issue_links'] = [chapter_summary_issue_with_chapter_id_report_level]
result = validate_report_quality_bundle(bundle)
# → 2 条 RQV_CHAPTER_SUMMARY_SEMANTICS/blocking
```

**建议**: 从 `_validate_single_score_issue()` 第 1512-1525 行移除 `report_level` 检查，保留 `_validate_chapter_summary_issue()` 作为 canonical location。

### F2 [minor] _validate_chapter_summary_issue 对非 scoring_ready bundle 也阻断 report_level

**文件**: `fund_agent/fund/report_quality_validation.py`
**行号**: 1630-1643

**描述**: `_validate_chapter_summary_issue()` 无条件检查 `chapter_id=="report_level"`，对 `scoring_ready=False` 的 bundle 也输出 blocking。plan §4.F.2 原文："chapter_summary 必须有 chapter_id，不得是 report_level，因为它总结具体章节"——未显式要求 gating on scoring_ready，但 plan §4.H.7 将 preferred_lens 覆盖检查限定为 scoring_ready 前置条件，暗示非 scoring_ready bundle 的 chapter_id 约束更宽松。

**影响**: 非 scoring_ready bundle 的 `chapter_summary + report_level` 被 blocking，比 plan 要求更严格。当前无测试覆盖此路径（`test_chapter_summary_requires_skipped_chapter_scope_and_canonical_issue` 使用 scoring_ready bundle）。

**建议**: 如确认 plan 意图是无条件阻断，保持现状并在 plan 中补充说明。如确认仅 scoring_ready 阻断，需在 `_validate_chapter_summary_issue()` 中传入 `scoring_ready` 参数并条件化。

### F3 [minor] scoring_ready preconditions 测试未验证 unknown_upstream_failure 消息内容

**文件**: `tests/fund/test_report_quality_validation.py`
**行号**: 271-298

**描述**: `test_scoring_ready_blocks_ad_hoc_unknown_type_probe_boundary_unreviewed_facts_and_fail_closed_source` 构造了 `source_failure_category="unknown_upstream_failure_category"` 的 bundle，但 test 只断言 `"all facts must have review_status=reviewed" in scoring_issues[0].actual`。未验证 consolidated message 是否包含 `"unknown upstream failure category must be recovered"`。

**影响**: 实现正确包含该消息（第 1919-1920 行），但 test 不覆盖。若未来重构遗漏该条件，test 不会捕获回归。

**建议**: 补充断言：
```python
assert "unknown upstream failure" in scoring_issues[0].actual
```

## 规则遗漏检查

| Plan Rule | Status |
|---|---|
| §4.A Field presence | PASS — 17 个 bundle 必填字段、8 个 score_issue 必填字段、6 个 preferred_lens chapter 必填字段 |
| §4.B Enum domain | PASS — 27 个 Literal domain 全部从 report_evidence.py 导入并校验 |
| §4.C Invalid combinations | PASS — accepted_baseline、external_official、extraction_mode=missing+value、pass+blocking gap、skipped+non-chapter_summary、chapter_summary+non-skipped、N/A+severity |
| §4.D ID references | PASS — 6 类 id 索引、11 类引用校验、重复 id blocking |
| §4.E N/A semantics | PASS — na_reason/reviewer_note required、severity material、blocking gap ref blocking |
| §4.F chapter_summary semantics | PASS — skipped only、specific chapter_id、reviewer_note/problem required、no severity (F1 为重复输出，非遗漏) |
| §4.G Source boundary / failure category | PASS — fail-closed blocking、fallback consistency、unknown_upstream material |
| §4.H scoring_ready preconditions | PASS — 11 项前置条件统一输出 RQV_SCORING_READY_PRECONDITION |
| §4.I data_gap_refs / evidence_anchor_refs completeness | PASS — bidirectional link completeness with scoring_ready escalation |

## 过度实现检查

**PASS** — 无过度实现。未新增 CLI、Service 接口、renderer 修改、quality_gate.py 修改、Host/Agent/dayu 引入、nav_data 投影、durable fixture 或第三方 JSON Schema 依赖。

## 测试盲点

| 场景 | 覆盖状态 |
|---|---|
| 非 scoring_ready + chapter_summary + report_level | 未覆盖（F2） |
| scoring_ready + chapter_summary + report_level 重复计数 | 未覆盖（F1） |
| unknown_upstream_failure 消息内容 | 未覆盖（F3） |
| 多 bundle record JSONL | 未覆盖（当前只处理首个 bundle） |
| score_issue record without bundle in JSONL | PASS — test 覆盖 |
| dataclass bundle 输入 | PASS — test 覆盖 |
| 负例矩阵 plan §6 | PASS — 18/18 核心测试 + 1 个额外 dataclass 测试 |

## 边界检查

| Check | Result |
|---|---|
| 不读取 PDF/cache/download helper | PASS — rg 无匹配 |
| 不调用 FundDocumentRepository | PASS — rg 无匹配 |
| 不导入 documents.* / AnnualReportDocumentCache / AnnualReportPdfAdapter | PASS — rg 无匹配 |
| 不导入 dayu.host / dayu.engine | PASS — rg 无匹配 |
| 不使用 extra_payload / **kwargs | PASS — 代码审查确认 |
| 不修改 quality_gate.py FQ0-FQ6 | PASS — 未触及 |
| 不修改 renderer / Service | PASS — 未触及 |
| 不投影 nav_data | PASS — rg 无匹配 |
| 不创建 durable fixture | PASS — 未触及 |
