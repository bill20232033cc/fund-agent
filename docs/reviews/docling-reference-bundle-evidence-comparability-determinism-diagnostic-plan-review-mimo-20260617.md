# Docling Reference Bundle Evidence Comparability and Producer Determinism Diagnostic Plan Review (AgentMiMo) - 2026-06-17

Verdict: PASS
Blocking findings: 0
Non-blocking findings: 0

## Review Target

`docs/reviews/docling-reference-bundle-evidence-comparability-determinism-diagnostic-plan-20260617.md`

## Verification Against Committed Matrices

All factual claims in the plan were verified against the two committed matrix JSON files via `jq` extraction.

### Count Drift Claims

Plan states prior/current cell_reference_count and text_span_count per sample. Verified:

| Sample | Prior cells | Current cells | Prior spans | Current spans | Plan claims |
|---|---|---|---|---|---|
| S1 | 3201 | 3247 | 8 | 6 | ✓ |
| S4 | 2529 | 2561 | 8 | 6 | ✓ |
| S5 | 6739 | 6805 | 6 | 6 | ✓ |
| S6 | 5665 | 5633 | 8 | 6 | ✓ |

### Regression Row Matched Context Claims

Plan states prior matched context for F015, S5-F023, S6-F035 and current empty context. Verified against both matrices:

- F015: prior `matched_row_label_path=["当期发生的基金应支付的销售服务费","安信基金"]`; current `[]`. ✓
- S5-F023: prior `matched_row_label_path=["投资目标"]`, `matched_column_header_path=["table_header"]`; current `[]`. ✓
- S6-F035: prior `matched_row_label_path=["基金名称"]`, `matched_column_header_path=["table_header"]`; current `[]`. ✓

### Summary Facts

- Prior: 17 rows, 13 closed, 4 residual. ✓
- Current: 17 rows, 10 closed, 7 residual. ✓
- Delta: -3. ✓
- Regression rows: F015, S5-F023, S6-F035. ✓
- Target seven: prior 3/7 closed, current 2/7 closed. ✓
- Both matrices have `rows_total=17`. ✓ (`jq '.rows | length'` = 17 for both)

### Boundary Flags

- `candidate_only=true` and `source_truth_status=not_proven` asserted. ✓
- `NOT_READY` preserved. ✓
- Non-goals list covers baseline/source truth/parser/readiness. ✓
- No live/network/provider/LLM/analyze/checklist/golden/readiness commands. ✓
- No direct PDF/cache/source-helper access. ✓

## Assessment

1. **Handoff-ready**: The plan is complete and actionable. Diagnostic questions are specific, schema is defined, implementation steps are numbered, stop conditions are enumerated, and output paths are exact. A future evidence worker can execute without ambiguity.

2. **Code-generation-ready**: The `comparability_matrix.json` schema is specified with exact field names, verdict tokens, and validation commands. The 15-step implementation sequence is deterministic.

3. **Boundary preservation**: The plan preserves all required boundaries. Repository-mediated access is gated behind explicit authorization. The plan explicitly states comparison uses committed JSON artifacts first.

4. **Fact accuracy**: All count drift, matched context, summary, and regression row claims match the committed matrices.

5. **Repository reload guard**: The plan correctly gates repository-mediated access behind a separate authorized gate, with socket guard requirements specified.

6. **Drift classification logic**: The plan's three-class classification (wrapper drift, helper drift, insufficient JSON evidence) is sound and aligns with the diagnostic questions.

## Self-check

- Read plan artifact and both committed matrices.
- Verified count drift claims via `jq` extraction on `repository_loads` per sample.
- Verified regression row matched context via `jq` extraction on `rows[]` for F015, S5-F023, S6-F035 in both matrices.
- Verified row counts (17) for both matrices.
- Verified `git diff --check` clean.
- No blocking findings identified.
- Artifact written to allowed path only.
