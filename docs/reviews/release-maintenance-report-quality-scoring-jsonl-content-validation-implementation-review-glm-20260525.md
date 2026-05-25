# Release Maintenance Report-Quality Scoring JSONL Content Validation Implementation Review (GLM)

> Date: 2026-05-25
> Gate: `report-quality scoring JSONL content validation implementation`
> Reviewer: AgentGLM
> Truth sources: `AGENTS.md`, `docs/design.md` §5.4 / §5.4.1 / §5.4.2 / §7.1-§7.6, `docs/implementation-control.md` Startup Packet / Next Entry Point, `docs/reviews/release-maintenance-report-quality-scoring-jsonl-content-validation-plan-20260525.md`, controller judgment.

## Verdict

**PASS_WITH_FINDINGS**

实现忠实对齐已接受 plan，正确复用 `report_evidence.py` 全部 27 个 Literal domain（零遗漏、零平行 schema），API 签名、JSONL record_type/pointer、scoring_ready canonical preconditions、N/A vs chapter_summary 去重、fallback consistency canonical location 均与 plan 一致。19 条测试覆盖 plan §6 全部 18 个必须场景加 1 个额外 dataclass 输入场景。Controller 验证已过（90.62% coverage、81 adjacent tests、ruff、boundary rg、nav_data rg、git diff --check）。

发现的 Material finding 为 `_validate_source_documents` 中 fallback 规则在同一文档上可能产生重复 issue；Minor finding 为三个测试覆盖缺口。无 correctness 或边界违规。

## Scope Verified

| 检查项 | 结果 |
|---|---|
| 复用 `report_evidence.py` typed domains，无 parallel schema | ✅ 全部 27 个 Literal domain 精确映射 |
| `validate_report_quality_bundle` / `validate_report_quality_jsonl` API | ✅ 签名与 plan 完全一致 |
| JSONL `record_type=bundle/score_issue` | ✅ |
| Pointer、run_id、schema_version、summary | ✅ |
| scoring_ready canonical preconditions 完整不重复 | ✅ 11 项前置条件在 §4.H 唯一位置 |
| fallback consistency canonical §4.G | ✅ 唯一位置，但有 F1 重复 issue |
| N/A vs chapter_summary 去重 | ✅ if/elif 正确优先 RQV_CHAPTER_SUMMARY_SEMANTICS |
| id refs、anchor.document_id、preferred_lens required fields、link completeness | ✅ |
| 不改/不导入 renderer/Service/CLI/quality_gate.py FQ0-FQ6 | ✅ boundary rg no matches |
| 不导入 FundDocumentRepository/PDF/cache/source helper | ✅ |
| 不导入 dayu.host/dayu.engine | ✅ |
| 不导入 nav_data | ✅ nav_data rg no matches |
| 无 extra_payload / **kwargs | ✅ 所有 API 参数显式声明 |
| README 最小同步 | ✅ 描述了 validator 模块定位和边界 |

## Findings

### Material

#### F1: `_validate_source_documents` 对同一文档可能产生重复 `RQV_FALLBACK_CONFLICT` issue

**严重度**: material
**位置**: `fund_agent/fund/report_quality_validation.py:1088-1131`

当 `source_failure_category` 属于 `_FALLBACK_ALLOWED_SOURCE_FAILURES`（`not_found` / `unavailable`）且 `fallback_allowed` 和 `fallback_used` 均不正确时，代码会对同一文档依次发出两条 `RQV_FALLBACK_CONFLICT/blocking`：一条针对 `fallback_allowed` 与 failure category 不一致（line 1088-1101），另一条针对允许 fallback 但 `fallback_used` 未显式记录为 True（line 1118-1131）。

Plan §4.G 规定 fallback consistency 的 canonical implementation 应避免同一语义被重复计入 summary。两条 issue 虽然指向不同字段，但属于同一语义违反（文档 fallback 状态与 failure category 不一致），会产生不必要的 summary counts 膨胀。

**影响**: 不影响 correctness（两条 issue 均为 blocking），但增加下游消费方的复盘噪音。

**建议**: 在 `failure_category in _FALLBACK_ALLOWED_SOURCE_FAILURES` 分支内，先短路判定 `fallback_allowed` 和 `fallback_used` 的一致性，合并为单条 issue；或在第三处检查前增加 `fallback_allowed is True` 前提，使得 `fallback_allowed=False` 的文档不再触发 `fallback_used` 检查。

#### F2: fail-closed failure 后继续发出 cascading `RQV_FALLBACK_CONFLICT`

**严重度**: material
**位置**: `fund_agent/fund/report_quality_validation.py:1073-1101`

当 `source_failure_category` 属于 `_FAIL_CLOSED_SOURCE_FAILURES`（`schema_drift` / `identity_mismatch` / `integrity_error`）且 `fallback_allowed=True` 时，代码先发出 `RQV_FAIL_CLOSED_SOURCE/blocking`（line 1073-1086），然后继续判定 `fallback_allowed` 是否匹配 `expected_fallback_allowed`（此时为 False），再发出一条 `RQV_FALLBACK_CONFLICT/blocking`（line 1088-1101）。

`RQV_FAIL_CLOSED_SOURCE` 已完整表达"来源失败分类必须 fail-closed，不能进入评分消费"的语义，后续 `RQV_FALLBACK_CONFLICT` 是 cascading 噪音。

**影响**: 不影响 correctness，但增加 issue 数量。

**建议**: 在 `failure_category in _FAIL_CLOSED_SOURCE_FAILURES` 分支结束后 `continue`，跳过该文档的后续 fallback consistency 检查。

### Minor

#### F3: 无 `accepted_baseline` 阻断的独立测试

**严重度**: minor
**位置**: `tests/fund/test_report_quality_validation.py`（缺失测试）

实现正确处理 `review_status=="accepted_baseline"` 的阻断逻辑（`report_quality_validation.py:1868-1882`），但测试文件中没有设置 `review_status="accepted_baseline"` 的独立测试用例。现有 `test_scoring_ready_blocks_*` 使用默认 `review_status="scoring_ready"`，不覆盖此分支。

**建议**: 新增 `test_accepted_baseline_review_status_is_blocking` 测试。

#### F4: 无 `skipped` 状态配合非 `chapter_summary` 维度的独立测试

**严重度**: minor
**位置**: `tests/fund/test_report_quality_validation.py`（缺失测试）

Plan §4.C.9 要求 `status=="skipped"` 且 `dimension!="chapter_summary"` 时为 blocking。实现正确处理此逻辑（`report_quality_validation.py:1462-1475`），但测试中没有构造 `status="skipped"` + `dimension="fact_coverage"` 的场景来验证。

**建议**: 新增 `test_skipped_status_outside_chapter_summary_dimension_is_blocking` 测试。

#### F5: 无 JSONL 无效 `record_type` 的独立测试

**严重度**: minor
**位置**: `tests/fund/test_report_quality_validation.py`（缺失测试）

实现正确处理 `RQV_RECORD_TYPE_INVALID`（`report_quality_validation.py:374-389`），但测试中没有构造 `record_type="invalid"` 或缺少 `record_type` 的 JSONL 记录来验证此路径。

**建议**: 新增 `test_jsonl_invalid_record_type_returns_blocking` 测试。

#### F6: `_validator_source()` 测试 helper 未关闭文件句柄

**严重度**: minor
**位置**: `tests/fund/test_report_quality_validation.py:849-850`

`_validator_source()` 使用 `open()` 读取源码但未使用 `with` 语句或 `.close()`。CPython GC 会处理，但不符合最佳实践。

**建议**: 改为 `with open(...) as f: return f.read()`。

## Positive Observations

1. **Domain 复用精确**: `_ENUM_FIELDS` 映射了 `report_evidence.py` 全部 27 个 Literal type alias（包括 `ClassifiedFundType` 这种 Union 形式），通过 `get_args()` 递归展开，零遗漏、零硬编码枚举值。
2. **Scoring ready preconditions 完整且不重复**: `_validate_scoring_ready_preconditions` 收集全部 11 项前置条件失败后合并为单条 `RQV_SCORING_READY_PRECONDITION/blocking`，不会与 §4.C 或 §4.G 重复输出同一语义的 issue。
3. **N/A vs chapter_summary 去重正确**: `_validate_single_score_issue` 使用 `if dimension == "chapter_summary": ... elif status == "N/A": ...` 确保 chapter_summary canonical 语义优先。
4. **`_validate_source_documents` 作为 §4.G canonical location**: 所有 `fallback_allowed` / `fallback_used` / `source_failure_category` 一致性检查在此函数内，`_validate_scoring_ready_preconditions` 只引用 source boundary/failure category 是否满足前置条件，不重复实现 fallback 规则。
5. **Link completeness 双向检查**: gap.issue → issue.gap 回链、fact.gap → gap.fact 回链、issue.field_path → fact.issue 回链均已实现。
6. **JSONL wrapper 设计干净**: JSONL 解析、record_type 分派、行号 pointer 与 bundle 校验逻辑完全解耦。
7. **`_normalize_record` 支持 dataclass 和 Mapping 双入口**: 测试覆盖了两种输入形式。

## Validation Results (Controller Reported)

| 检查项 | 结果 |
|---|---|
| validator tests | 19 passed |
| coverage | 90.62% (≥80% target met) |
| adjacent tests | 81 passed |
| ruff check | passed |
| boundary rg (repository/source/extra_payload/dayu) | no matches |
| nav_data rg | no matches |
| git diff --check | clean |

## Residual Risk

| 风险 | 说明 | Owner |
|---|---|---|
| F1/F2 fallback issue 去重 | Material findings，不影响 correctness，后续 robustness gate 可修 | future robustness gate |
| F3/F4/F5 测试缺口 | Minor findings，实现路径正确，仅缺少独立负例测试 | future test hardening |
| `nav_data` projection | 不在本 gate scope | future nav_data source-contract slice |
| Derived calculations generation | 当前只校验已有 calculation refs | future calculation-source gate |
| Durable baseline / fixtures | 不在本 gate scope | future baseline-promotion gate |
| Host/Agent/Dayu runtime | 不在本 gate scope | future explicit Host/Agent gate |
