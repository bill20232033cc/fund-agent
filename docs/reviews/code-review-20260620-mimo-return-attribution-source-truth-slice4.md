# Code Review: FundDisclosureDocument return_attribution.v1 Source-truth Direct Extraction — Slice 4 Facade/Test/Docs Sync

- **Reviewer**: AgentMiMo (review-only)
- **Date**: 2026-06-20
- **Gate**: FundDisclosureDocument return_attribution.v1 Source-truth Direct Extraction Implementation Gate - Slice 4 Facade/Test/Docs Sync
- **Checkpoint**: `ca05704`
- **Implementation evidence**: `docs/reviews/funddisclosuredocument-return-attribution-source-truth-extraction-slice4-implementation-evidence-20260620.md`
- **Verdict**: `CODE_REVIEW_PASS_NOT_READY`

---

## 1. Facade Regression — Default Processor Proof-Positive Projection

**Target**: 验证 `test_explicit_disclosure_source_truth_return_attribution_projects_to_bundle` 是否真实验证 default `FundDisclosureDocumentProcessor` proof-positive `return_attribution.v1` 到 `StructuredFundDataBundle` 的显式 opt-in 投影。

**Finding: PASS**

- 测试使用 `FundProcessorRegistry.create_default()`（line 1176），注册的是真实 `FundDisclosureDocumentProcessor`（priority=50），而非 marker stub。
- `_source_truth_disclosure_intermediate()` 构造了 proof-positive stub：`FundDisclosureSourceTruthAdmissionProof` 满足 `__post_init__` 全部校验（proof_kind、source_boundary、four boolean flags、producer），`candidate_boundary=None`、`failure_class=None`、`source_provenance` 非空。
- stub 提供 `table_blocks` 含 5 个 `_DisclosureCell`（nav-growth、benchmark-return、management-fee、custody-fee、tracking-error），`column_header_path` / `row_label_path` 匹配 processor 选择器。
- 测试断言覆盖 `fee_schedule`、`nav_benchmark_performance`、`tracking_error` 三个 bundle 字段的值、extraction_mode、anchors 来源和 row_locator 格式。
- 与已有 marker test（`test_explicit_disclosure_intermediate_routes_to_registry`，line 1132）的关键区别：marker test 验证 registry 路由；新测试验证真实 processor 的 source-truth extraction 到 bundle projection 全路径。

**Trace**: `extract()` → `_extract_active_fund_disclosure_via_processor()` → `FundDisclosureDocumentProcessor.extract()` → `_validate_source_truth_admission()` → `_field_families_for_intermediate(source_truth_extraction_allowed=True)` → `_extract_return_attribution_source_truth()` → `_active_processor_result_to_bundle()` → `_field_from_family()` / `_tracking_error_for_fund_type()`。

---

## 2. tracking_error — Active Fund Facade Non-Index Rule

**Target**: 验证测试是否误导 tracking_error：当前 active_fund facade 应保持非指数 tracking_error missing，而不是当成 blocker。

**Finding: PASS**

- 测试 stub 含 tracking_error cell（"1.23%"），processor 的 `_collect_return_attribution_tracking_error_candidates()` 会提取该值。
- `_active_processor_result_to_bundle()` 调用 `_tracking_error_for_fund_type(raw_tracking_error, classified_fund_type)`（`data_extractor.py:759`）。
- `classified_fund_type` 在测试中为 `"active_fund"`，不在 `_TRACKING_ERROR_APPLICABLE_FUND_TYPES`（`("index_fund", "enhanced_index")`，line 48-50）中。
- `_tracking_error_for_fund_type()` 返回 `ExtractedField(value=None, anchors=(), extraction_mode="missing", note="非指数基金不适用跟踪误差")`（line 932-939）。
- 测试正确断言 `tracking_error.value is None`、`extraction_mode == "missing"`、`note == "非指数基金不适用跟踪误差"`。
- 这是 active_fund 的预期行为，不是测试缺陷。tracking_error 在 bundle 层被 fund_type 语义覆盖，与 processor 是否提取到 source value 无关。

---

## 3. Docs Sync — design.md 与 README.md

**Target**: 验证 `docs/design.md` 与 `fund_agent/fund/README.md` 是否准确同步：`product_essence.v1` + `return_attribution.v1` 已 direct source-truth；其它四个仍 missing；candidate evidence candidate_only/not_proven/NOT_READY；无 parser replacement/readiness。

**Finding: PASS**

### docs/design.md

| 区域 | 变更 | 验证 |
|------|------|------|
| S2 概述段（line 674） | "其它五个" → "其它四个"；增加 `return_attribution.v1` 显式 FDD facade route 描述 | 准确：6 族 - 2 已实现 = 4 个 missing |
| S2 概述段（line 678） | "仅 proof-positive `product_essence.v1`" → "`product_essence.v1` 与 `return_attribution.v1`"；"其它五个" → "其它四个" | 准确 |
| 矩阵表（line ~1147） | "仅 proof-positive `product_essence.v1`" → "`product_essence.v1` 与 `return_attribution.v1`"；"其它五个" → "其它四个" | 准确 |

### fund_agent/fund/README.md

| 区域 | 变更 | 验证 |
|------|------|------|
| Source-truth 段（line ~100） | "当前仅 `product_essence.v1`" → "`product_essence.v1` 与 `return_attribution.v1`"；增加 FDD facade route 描述 | 准确 |
| Extractor 段（line 115） | "其它五个" → "其它四个"；增加 "当前例外是 proof-positive `product_essence.v1` 与 `return_attribution.v1`" | 准确 |
| 默认路径段（line 119） | "当前仅覆盖 proof-positive `product_essence.v1`" → "覆盖 proof-positive `product_essence.v1` 与 `return_attribution.v1`"；"其它五个" → "其它四个" | 准确 |

**计数一致性**: 6 个 FDD source-truth 字段族 = 2 已实现（`product_essence.v1`、`return_attribution.v1`）+ 4 个 missing（`manager_profile.v1`、`investor_experience.v1`、`current_stage.v1`、`core_risk.v1`）。所有文档一致。

**NOT_READY 声明**: 两份文档均保留 candidate evidence 的 `candidate_only / not_proven / NOT_READY` 声明，无 parser replacement 或 readiness 声明。

---

## 4. Boundary — 越界检查

**Target**: 是否越界改 source/repository/schema/public contract/其它 family/upper-layer consumption。

**Finding: PASS**

- `git diff --name-only` 仅含 `tests/fund/test_data_extractor.py`、`docs/design.md`、`fund_agent/fund/README.md`。
- 无 `fund_agent/` 内生产源文件变更（`fund_agent/fund/README.md` 是文档）。
- 无 `EvidenceAnchor`、`EvidenceSourceKind`、processor contract 或 public schema 扩展。
- 无其它 source-truth field family 实现。
- 无 source/repository/fallback/cache/PDF/live/network/provider/LLM/manual-reference 行为变更。
- 无 Service/UI/Host/renderer/quality-gate/LLM prompt consumption 新增。
- `FundDisclosureSourceTruthAdmissionProof` 已在 Slice 1-3 落地（`contracts.py:188-261`），本 slice 仅在 test 中 import 使用。
- `_DisclosureCell`、`_DisclosureTable` 为测试内部 dataclass（非导出），不影响生产协议。

---

## 5. Verification Commands

**Finding: PASS**

| 命令 | 预期 | 实际 |
|------|------|------|
| `uv run pytest tests/fund/test_data_extractor.py tests/fund/processors/test_fund_disclosure_processor.py` | 170 passed | 170 passed in 0.89s |
| `uv run ruff check tests/fund/test_data_extractor.py` | All checks passed | All checks passed |
| `git diff --check -- tests/fund/test_data_extractor.py docs/design.md fund_agent/fund/README.md` | PASS (no output) | exit 0, no output |

所有验证命令可信。

---

## Residual Risks（与 implementation evidence 一致）

1. Real-report field correctness 未证明；owner: later evidence gate。
2. `tracking_error` source-truth 存在于 processor 输出，但 active-fund bundle 投影保持 non-index not-applicable 规则；owner: future facade semantics gate（仅当 product contract 变更时）。
3. 同值 duplicate disclosures 仍接受第一个 locator；owner: future field-specific refinement gate。
4. 其余四个 FDD source-truth 字段族仍 missing；owner: separate future gates。
5. Aggregate deepreview / controller acceptance 仍 pending。

---

## Verdict

`CODE_REVIEW_PASS_NOT_READY`

Slice 4 facade regression 测试真实验证了 default `FundDisclosureDocumentProcessor` proof-positive `return_attribution.v1` 到 `StructuredFundDataBundle` 的显式 opt-in 投影。tracking_error 断言正确反映 active_fund 非指数基金语义。文档同步准确，计数一致。无越界变更。验证命令全部通过。NOT_READY 状态有意保留，real-report correctness 仍需后续 evidence gate。
