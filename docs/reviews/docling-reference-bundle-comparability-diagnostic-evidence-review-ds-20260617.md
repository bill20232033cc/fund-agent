# Docling Reference Bundle Comparability Diagnostic Evidence Review (AgentDS) — 2026-06-17

Gate: `Docling Reference Bundle Comparability Diagnostic Evidence Review Gate`
Role: AgentDS evidence review worker only
Verdict: `PASS`
Blocking findings: 0
Non-blocking findings: 1

## Reviewed Artifacts

- `reports/docling-reference-bundle-comparability-diagnostic/20260617/comparability_matrix.json`
- `docs/reviews/docling-reference-bundle-comparability-diagnostic-evidence-20260617.md`

## Context

- Plan: `docs/reviews/docling-reference-bundle-evidence-comparability-determinism-diagnostic-plan-20260617.md`
- Controller judgment: `docs/reviews/docling-reference-bundle-evidence-comparability-determinism-diagnostic-plan-controller-judgment-20260617.md`
- Current re-evidence matrix: `reports/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-reevidence/20260617/residual_closure_matrix.json`
- Prior checkpoint: `reports/docling-reference-bundle-enrichment-residual-closure/20260617/residual_closure_matrix.json`

## Schema Invariant Verification (jq)

| Invariant | Expected | jq Result |
|---|---|---|
| `candidate_only == true` | true | ✅ |
| `not_source_truth == true` | true | ✅ |
| `not_ready == true` | true | ✅ |
| `row_comparison \| length` | 17 | ✅ |
| `regression_rows \| length` | 3 | ✅ |
| `summary.rows_total` | 17 | ✅ |
| `summary.prior_closed_rows_total` | 13 | ✅ |
| `summary.current_closed_rows_total` | 10 | ✅ |
| `summary.delta_closed_rows` | -3 | ✅ |
| `summary.prior_residual_rows_total` | 4 | ✅ |
| `summary.current_residual_rows_total` | 7 | ✅ |
| `summary.regression_fact_ids` | `["F015","S5-F023","S6-F035"]` | ✅ |
| `summary.target_seven_prior_closed` | 3 | ✅ |
| `summary.target_seven_current_closed` | 2 | ✅ |

## Report ↔ Matrix Consistency

| Report Claim | Matrix Field | Match |
|---|---|---|
| Prior 13/4, current 10/7, delta -3 | `summary.prior/current_closed_rows_total`, `summary.delta_closed_rows` | ✅ |
| Regression rows: F015, S5-F023, S6-F035 | `regression_rows[].fact_id`, `summary.regression_fact_ids` | ✅ |
| Target seven prior 3/7, current 2/7 | `summary.target_seven_prior/current_closed` | ✅ |
| All 4 samples: count drift | `repository_load_comparison[].has_count_drift` all `true` | ✅ |
| All 4 samples: section inference drift | `repository_load_comparison[].has_section_inference_drift` all `true` | ✅ |
| Text span drift: S1/S4/S6, not S5 | S1 δ=-2, S4 δ=-2, S5 δ=0, S6 δ=-2 | ✅ |
| S1 §7: 5→8 | `section_inference_counts_comparison.§7` prior=5, current=8, δ=3 | ✅ |
| S1 §8: 21→12 | `section_inference_counts_comparison.§8` prior=21, current=12, δ=-9 | ✅ |
| S6 §2: 9→14 | `section_inference_counts_comparison.§2` prior=9, current=14, δ=5 | ✅ |
| S5 text_span_count stable at 6 | `count_comparison.text_span_count.delta` = 0 | ✅ |
| S5 §8: 14→10 | `section_inference_counts_comparison.§8` prior=14, current=10, δ=-4 | ✅ |
| Primary class: wrapper drift | `classification.primary_class` = `wrapper_or_reference_bundle_construction_drift` | ✅ |
| json insufficient for exact producer line | `classification.json_artifacts_insufficient_for_exact_producer_line` = true | ✅ |
| Repository object access: false | `repository_object_access` = false | ✅ |
| Helper semantics NOT isolated as root cause | `classification.helper_semantics_not_isolated_as_root_cause` = true | ✅ |
| F015 prior matched context | prior row `["当期发生的基金应支付的销售服务费","安信基金"]`, column `["本期 2025年...",...,"安信企业价值优选混 合C"]` | ✅ exact match with prior matrix |
| S5-F023 prior matched context | prior row `["投资目标"]`, column `["table_header"]`, table with §2 + full text | ✅ exact match with prior matrix |
| S6-F035 prior matched context | prior row `["基金名称"]`, column `["table_header"]`, table with §2 + fund name | ✅ exact match with prior matrix |
| S6-F041: SAR→SBM, regression_flag=false | `row_comparison` shows `closure_disposition_changed=true`, `regression_flag=false`, class=`status_drift_only` | ✅ (was residual in both runs, correctly not counted as regression) |
| F015: DSBM→SAR, regression_flag=true | `row_comparison` confirms `closure_disposition_changed=true`, `regression_flag=true` | ✅ |

All 20 consistency checks passed. No report-matrix discrepancy found.

## Diagnostic Findings Verification

| Diagnostic Finding | Matrix `diagnostic_findings[]` | Evidence Support |
|---|---|---|
| `repository_load_count_drift` | ✅ present | All 4 samples: cell counts changed (S1 +46, S4 +32, S5 +66, S6 -32) |
| `section_inference_drift` | ✅ present | All 4 samples: section inference counts shifted (e.g. S1 §7 5→8, §8 21→12) |
| `text_span_count_drift` | ✅ present | 3 of 4 samples: S1 8→6, S4 8→6, S6 8→6; S5 stable at 6 |
| `matched_context_drift` | ✅ present | Multiple rows show context changes even with stable closure (F002, F020, S4-F001, etc.) |
| `source_layer_status_drift` | ✅ present | S5-F023: same_source_reference_loaded→same_source_text_absent; S6-F041: same_source_reference_loaded→same_source_text_absent |
| `json_artifacts_insufficient_for_exact_producer_line` | ✅ present | Honest admission: committed JSON can show non-comparability but can't trace the exact producer code line |
| `current_10_7_artifact_remains_valid_blocked_regression_evidence` | ✅ present | Correctly preserves prior verdict |

## Classification Rationale Assessment

The diagnostic classifies the drift as `wrapper_or_reference_bundle_construction_drift` based on:

1. **Helper hash stability**: Helper SHA256 `f2a4f87a...` unchanged between runs ✅
2. **Count drift before helper**: All 4 samples show cell/text_span count changes, which occur at the wrapper/bundle-construction layer, before the helper is invoked ✅
3. **Section inference drift**: Section assignment changed across all samples (e.g. S1 §7:5→8, §8:21→12), which is a ParsedTable/wrapper-level operation ✅
4. **Text span loss**: S1/S4/S6 all lost 2 text spans; S5-F023 text went from found→absent despite S5 text_span_count staying at 6 (content composition drift) ✅
5. **Non-comparability established**: With different input bundles, the same helper produces different closure results by construction—the drift is at the input layer, not the computation layer ✅

The `json_artifacts_insufficient_for_exact_producer_line` finding is appropriately honest: the diagnostic can prove wrapper drift but cannot pinpoint which producer code line caused the specific cell/span/section changes without repository object access.

## Boundary Verification

| Requirement | jq Evidence |
|---|---|
| `candidate_only=true` | ✅ Matrix + report |
| `source_truth_status_preserved=not_proven` | ✅ Matrix + report |
| `not_source_truth=true` | ✅ Matrix |
| `not_baseline_promotion=true` | ✅ Matrix |
| `not_parser_replacement=true` | ✅ Matrix |
| `not_full_field_correctness=true` | ✅ Matrix |
| `not_release_readiness=true` | ✅ Matrix |
| `not_ready=true` | ✅ Matrix |
| `NOT_READY` verdict token | ✅ Matrix `summary.verdict` includes `NOT_READY` |
| `repository_object_access=false` | ✅ Matrix + report |
| `comparison_basis=committed_json_artifacts_only` | ✅ Matrix |
| No live/network/provider/LLM | ✅ Report line 36 |
| No direct PDF/cache/source-helper | ✅ Report line 35 |
| No code/test/runtime/control/design/README changes | ✅ Report line 37 |
| No stage/commit/push/PR | ✅ Implicit (evidence gate only) |
| Validation: `python -m json.tool` | ✅ pass |
| Validation: `jq -e` candidate/row count | ✅ pass |
| Validation: `jq -e` regression count | ✅ pass |
| Validation: `git diff --check` | ✅ pass |
| Plan compliance: output artifacts limited to 2 files | ✅ comparability_matrix.json + evidence.md |

---

## Finding

### F-DS-D1 (Info) — S6-F041 `status_drift_only` 分类可能模糊：benchmark 从 SAR→SBM

**Matrix evidence**: S6-F041 的 `row_comparison` 显示 `closure_disposition_changed=true`（SAR→SBM），`source_status_changed=true`（same_source_reference_loaded→same_source_text_absent），但 `regression_flag=false`。

**分析**: 这是正确的分类——S6-F041 在 prior 中就是 residual（SAR），当前仍是 non-closed（SBM）。它不是"闭合→非闭合"的回退，只是 residual 子类型的漂移。但 benchmark 候选文本从"存在但语义不匹配"变为"完全缺失"，这一变化与 S6 的 text_span_count 从 8→6 一致。分类为 `status_drift_only` 准确但不显眼——如果未来要追溯 benchmark 文本丢失的根本原因，可能需要显式关注此行的 source_layer 变化。

**Severity**: Info — 分类正确（regression_flag=false 合理），仅建议在 evidence 报告的 regression 讨论附近加一句解释，避免读者误以为 S6-F041 的 disposition change 被遗漏。

---

## Assessment

**Artifact quality**: 矩阵与报告完全一致。20 项一致性检查全部通过。Schema invariants 全部满足。诊断分类有坚实的 committed-JSON 证据支撑：helper hash 稳定 + 所有 4 个 sample 的 repository load counts 和 section inference 均漂移 = wrapper 层无疑是输入端变化的来源。

**Classification correctness**: `wrapper_or_reference_bundle_construction_drift` 是正确的首要分类。`json_artifacts_insufficient_for_exact_producer_line` 和 `repository_mediated_followup_needed` 是诚实的承认——诊断可以证明"无法比较"但不能精确指出 producer 中的哪一行代码导致了差异。这完全符合 plan 的设计意图。

**Gate utility**: 此 artifact 成功回答了 plan 中的 6 个 diagnostic questions：
1. ✅ 两个矩阵在 repository load aggregate 层面不可比
2. ✅ Section inference 在所有 4 个 sample 漂移
3. ✅ 三行回退均伴随 matched context 消失
4. ✅ Text span 内容漂移（不仅是 count）
5. ✅ Bundle schema 一致（均为 v1 legacy），无 v2 prefill
6. ✅ Drift 根因分类为 wrapper 构造层，非 helper 逻辑

**本 artifact 不**：闭合任何 residual 行、接受 source truth、promote baseline、替换 parser、或 claim readiness。它是一个纯诊断 artifact。

## Self-Check

pass — 审查基于 jq 直接从 matrix JSON 提取的数据。20 项报告↔矩阵一致性检查全部通过，所有 schema invariants 满足。诊断分类有坚实的计数/推断漂移证据支撑。1 项 Info finding（S6-F041 status_drift_only 可见性）为展示建议，不影响 artifact 正确性。所有 NOT_READY / candidate-only / no-live / no-source-truth 边界完整。

Verdict: `PASS`。Blocking findings: 0。
