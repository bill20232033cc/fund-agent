# Docling Reference Bundle Producer Row-hierarchy and Benchmark Semantic-label No-live Re-evidence Review (AgentDS) — 2026-06-17

Gate: `Docling Reference Bundle Producer Row-hierarchy and Benchmark Semantic-label No-live Re-evidence Gate`
Role: AgentDS evidence review worker only
Verdict: `PASS` — artifact is internally consistent and honestly self-declares REGRESSION/BLOCKED; this evidence cannot be accepted as successful re-evidence
Blocking findings: 0
Non-blocking findings: 3

## Reviewed Artifacts

- `reports/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-reevidence/20260617/residual_closure_matrix.json`
- `docs/reviews/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-no-live-reevidence-20260617.md`

Prior checkpoint: `reports/docling-reference-bundle-enrichment-residual-closure/20260617/residual_closure_matrix.json` (13 closed / 4 residual)

---

## Findings

### F-DS-E1 (Medium) — F015 出现回退：disambiguated_source_body_match → semantic_assignment_residual

**事实**: Prior matrix 中 F015（`sales_service_fee_C_current_year`, S1）为 `disambiguated_source_body_match`。当前 matrix 中为 `semantic_assignment_residual`（`fund_layer_status=semantic_rule_rejected`）。

**影响**: F015 是 target seven 之一，在 prior 中由 C 类/本期/费用表的 enriched predicate 组合闭合。当前 run 中同一 predicate 组合不再满足。可能原因：evidence wrapper 的 bundle 构造在两次 run 之间发生了变化——S1 的 `§7` section inference count 从 5 变为 8，说明费用表被重新解析/分类，匹配的 cell 上下文可能已改变。

**Severity**: Medium — target seven 内直接回退。

### F-DS-E2 (Medium) — S5-F023 出现回退：disambiguated_source_body_match → source_body_mismatch

**事实**: Prior matrix 中 S5-F023（`investment_objective`, S5）为 `disambiguated_source_body_match`。当前 matrix 中为 `source_body_mismatch`（`source_layer_status=same_source_text_absent`）。

**影响**: Candidate 文本在本次 run 的 reference bundle 中完全未被找到。S5 的 `text_span_count` 从 prior 的 8 降为当前的 6，投资目标对应的 text span 可能在此次 bundle 构造中缺失。虽非 target seven 行，但直接贡献了闭合数下降。

**Severity**: Medium — 闭合数直接下降。

### F-DS-E3 (Medium) — S6-F035 出现回退：disambiguated_source_body_match → semantic_assignment_residual

**事实**: Prior matrix 中 S6-F035（`fund_name`, S6）为 `disambiguated_source_body_match`。当前 matrix 中为 `semantic_assignment_residual`（`fund_layer_status=semantic_rule_rejected`）。

**影响**: S6 的 `text_span_count` 同样从 8 降为 6，基金名称文本对应的 span 可能在 bundle 中缺失或上下文已变，导致 `fund_name` 规则的语义检查不再通过。

**Severity**: Medium — 虽非 target seven，但与 F-DS-E1/E2 同为 evidence wrapper bundle 构造变化导致的回退。

### F-DS-E4 (Info) — Target seven 中 hierarchy-dependent 三行和 benchmark 一行均未闭合

**事实**: Target seven 中仅 F020 和 S4-F015 闭合（不依赖 hierarchy/benchmark label）。其余 5 行 residual：
- `F015`: `semantic_assignment_residual`（见 F-DS-E1）
- `S5-F032`: `semantic_assignment_residual`（hierarchy 未证明）
- `S6-F041`: `source_body_mismatch`（benchmark 候选文本未在 bundle 中找到）
- `S6-F049`: `semantic_assignment_residual`（hierarchy 未证明）
- `S6-F050`: `semantic_assignment_residual`（hierarchy 未证明）

**分析**: Hierarchy-dependent 三行在真实年报数据中未能闭合——真实 ParsedTable 的 label structure 可能不满足 helper 要求的显式 `权益投资` → `其中：股票` pattern。S6-F041 的 `source_body_mismatch` 是 text_span_count 下降的直接后果。Helper 在 fixture 测试中已验证正确（80 passed），但真实数据与 test fixture 存在差距。

**Severity**: Info — plan 明确声明不要求 4/4 闭合，此结果在预期范围内。

---

## Matrix Consistency Verification

| Metric | Value | Verified |
|---|---|---|
| `rows_total` | 17 | ✅ |
| `closed_rows_total` | 10 | ✅ |
| `residual_rows_total` | 7 | ✅ |
| `disambiguated_source_body_match` | 10 | ✅ |
| `semantic_assignment_residual` | 5 | ✅ |
| `source_body_mismatch` | 2 | ✅ |
| Dispositions sum | 10 + 5 + 2 = 17 | ✅ |
| `delta_vs_previous_closed_rows` | -3 (13 → 10) | ✅ |
| Regression rows vs prior | F015, S5-F023, S6-F035 | ✅ |
| Target seven: closed / residual | 2 / 5 | ✅ |
| `verdict` | `REG_BLOCKED_NOT_READY` | ✅ |

### By-Sample Summary

| Sample | Closed | SAR | SBM | Total |
|---|---|---|---|---|
| S1 | F002, F020 (2) | F015 (1) | — | 3 |
| S4 | S4-F001, S4-F002, S4-F015 (3) | — | — | 3 |
| S5 | S5-F018, S5-F019 (2) | S5-F032 (1) | S5-F023 (1) | 4 |
| S6 | S6-F036, S6-F037, S6-F038 (3) | S6-F035, S6-F049, S6-F050 (3) | S6-F041 (1) | 7 |

### Regression Detail

| Fact ID | Field | Prior | Current | Root Cause |
|---|---|---|---|---|
| F015 | sales_service_fee_C_current_year | disambiguated | semantic_assignment_residual | Bundle: S1 §7 count 5→8, fee cell context changed |
| S5-F023 | investment_objective | disambiguated | source_body_mismatch | Bundle: S5 text_span_count 8→6, span missing |
| S6-F035 | fund_name | disambiguated | semantic_assignment_residual | Bundle: S6 text_span_count 8→6, span missing or context changed |

---

## Boundary Verification

| Requirement | Status |
|---|---|
| `candidate_only=true` preserved (top-level + all rows) | ✅ |
| All rows `source_truth_status=not_proven` | ✅ |
| `NOT_READY` preserved | ✅ |
| `not_baseline_promotion=true` | ✅ |
| `not_source_truth=true` | ✅ |
| `not_parser_replacement=true` | ✅ |
| `not_full_field_correctness=true` | ✅ |
| `not_release_readiness=true` | ✅ |
| Evidence wrapper: raw legacy v1 bundle, no v2 hierarchy/semantic prefill | ✅ |
| Repository access: `FundDocumentRepository.load_annual_report(..., force_refresh=False)` | ✅ |
| Socket guard recorded during repository loads | ✅ |
| No live/network/provider/LLM commands | ✅ |
| Evidence report self-declares `REG_BLOCKED_NOT_READY` | ✅ |

---

## Assessment

**Artifact quality**: Matrix 与 evidence 报告内部一致。17 行、10 闭合、7 residual（5 SAR + 2 SBM）、delta -3 的数据自洽。报告正确地自我声明为 `RESIDUAL_CLOSURE_REEVIDENCE_REGRESSION_BLOCKED_NOT_READY`——这是对回归证据的诚实记录。

**Gate disposition**: 此 evidence **不能**作为 hierarchy/benchmark 实现成功的 re-evidence。Delta -3 的三行回退均与 evidence wrapper 的 bundle 构造变化相关（text_span_count 8→6、section inference 分布变化），与 helper 的 hierarchy/benchmark enrichment 逻辑无直接因果关系。Helper 的 80 个单元测试在 prior code review gate 中全部通过，fixture 级别的 hierarchy/benchmark 闭合已验证——但真实年报的 ParsedTable 结构与测试 fixture 存在差距，且 bundle 构造在两次 run 之间不稳定。

**回退归因**: 三次回退的共性因子是 bundle 构造变化：所有 4 个 sample 的 `text_span_count` 从 8 降为 6，cell counts 和 section inference counts 均发生了系统性偏移。在 bundle 构造稳定之前，任何 re-evidence 结果的闭合数都不具可比性。

## Residual Risks

1. **Bundle 构造稳定性**: text_span_count 和 section inference 在两次 run 之间变化，evidence wrapper 对 ParsedTable 解析细节敏感。在构造参数统一之前，re-evidence 结果不可比。
2. **Real-document hierarchy gap**: S5-F032, S6-F049, S6-F050 在真实数据中保持 residual。Helper 的 label-pattern 推导是 conservative 的，依赖 table-local explicit structure。
3. **No source truth**: 所有行 `source_truth_status=not_proven`。此 artifact 不提供任何 source truth、baseline 或 readiness 证明。

## Self-Check

pass — 审查基于当前 disk artifact 的事实。Matrix 内部一致（17 rows, 10 closed, 7 residual, 3 regression rows）。Evidence 报告诚实地自我声明 REGRESSION/BLOCKED，所有 NOT_READY / candidate-only / no-live / no-source-truth 边界完整。Artifact 是一份正确的回归证据记录，但不能作为成功的 re-evidence 被接受。
