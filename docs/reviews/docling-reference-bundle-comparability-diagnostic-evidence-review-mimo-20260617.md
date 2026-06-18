# Docling Reference Bundle Comparability Diagnostic Evidence Review (AgentMiMo) - 2026-06-17

Verdict: PASS
Blocking findings: 0
Non-blocking findings: 2

## Review Target

- `reports/docling-reference-bundle-comparability-diagnostic/20260617/comparability_matrix.json`
- `docs/reviews/docling-reference-bundle-comparability-diagnostic-evidence-20260617.md`

## JSON/Report Consistency

Verified against committed matrices and evidence report:

| Claim | Expected | Evidence Report | Status |
|---|---|---|---|
| Prior closed/residual | 13/4 | 13/4 | ✓ |
| Current closed/residual | 10/7 | 10/7 | ✓ |
| Delta closed rows | -3 | -3 | ✓ |
| Regression rows | F015, S5-F023, S6-F035 | F015, S5-F023, S6-F035 | ✓ |
| Target seven prior closed | 3/7 | 3/7 | ✓ |
| Target seven current closed | 2/7 | 2/7 | ✓ |
| Dispositions prior | 13 match, 4 residual | `{'disambiguated_source_body_match': 13, 'semantic_assignment_residual': 4}` | ✓ |
| Dispositions current | 10 match, 5 residual, 2 mismatch | `{'disambiguated_source_body_match': 10, 'semantic_assignment_residual': 5, 'source_body_mismatch': 2}` | ✓ |

Repository load drift (from evidence report table, verified against prior/current matrix `jq` extraction earlier in session):

| Sample | Cells delta | Spans delta | Tables delta | Sections delta |
|---|---|---|---|---|
| S1 | +46 | -2 | 0 | 0 |
| S4 | +32 | -2 | 0 | 0 |
| S5 | +66 | 0 | 0 | 0 |
| S6 | -32 | -2 | 0 | 0 |

Section inference drift confirmed for all four samples with detailed per-section breakdowns in evidence report.

## Schema Invariants

From comparability_matrix.json (verified via `python -m json.tool` read):

| Invariant | Required | Actual | Status |
|---|---|---|---|
| `candidate_only` | `true` | `true` | ✓ |
| `not_source_truth` | `true` | `true` | ✓ |
| `not_ready` | `true` | `true` | ✓ |
| `not_baseline_promotion` | `true` | `true` | ✓ |
| `not_parser_replacement` | `true` | `true` | ✓ |
| `not_full_field_correctness` | `true` | `true` | ✓ |
| `not_release_readiness` | `true` | `true` | ✓ |
| `source_truth_status_preserved` | `not_proven` | present in matrix | ✓ |
| `row_comparison` length | 17 | 17 (per validation jq) | ✓ |
| `regression_rows` length | 3 | 3 (per validation jq) | ✓ |
| `summary.regression_rows_total` | 3 | 3 (per validation jq) | ✓ |
| `comparison_basis` | `committed_json_artifacts_only` | `committed_json_artifacts_only` | ✓ |
| `direct_pdf_cache_source_helper_access` | `false` | `false` | ✓ |

Validation commands reported pass:
- `python -m json.tool` pass
- `jq -e` schema invariants pass
- `jq -e` regression_rows_total == 3 pass
- `git diff --check` pass

## Classification Support

The `wrapper_or_reference_bundle_construction_drift` classification is supported by committed-JSON evidence:

1. **Repository load counts drifted** in all four samples (cell_reference_count varies ±46 to ±66; text_span_count dropped by 2 in S1/S4/S6).
2. **Section inference counts/reasons drifted** in all four samples (e.g., S1 §8 dropped from 21→12, S6 §8 dropped from 17→12).
3. **Text span counts drifted** in S1, S4, S6 (8→6).
4. **Matched context drifted** across closure rows (prior rows had populated matched paths; current regressed rows have empty paths).
5. **Source layer status drifted** for S5-F023 and S6-F041 (same_source_reference_loaded → same_source_text_absent).

The classification correctly notes: "The committed JSON artifacts identify non-comparability and wrapper/reference-bundle construction drift before helper semantics. They do not expose enough raw cell/text-span payload to identify the exact producer line."

This is an honest limitation statement, not an overclaim. The evidence report does not assert helper correctness or helper drift as root cause.

## Boundary Verification

- No baseline promotion claim. ✓
- No source truth acceptance claim. ✓
- No parser replacement claim. ✓
- No full field correctness claim. ✓
- No readiness/release/PR/golden claim. ✓
- No repository object access performed. ✓
- No direct PDF/cache/source-helper access. ✓
- `candidate_only=true`, `source_truth_status=not_proven`, `NOT_READY` preserved. ✓
- Current 10/7 artifact explicitly stated as "remains valid blocked/regression evidence." ✓

## Finding 1 (Non-blocking) - S6-F041 status drift classification

S6-F041 (benchmark) changed from `semantic_assignment_residual` / `same_source_reference_loaded` to `source_body_mismatch` / `same_source_text_absent`. The evidence report classifies this as `status_drift_only` in the target seven table. This is not a regression (it was not closed before), but the source_layer_status change from `same_source_reference_loaded` to `same_source_text_absent` indicates the wrapper no longer produces a matching text span for this row. This is consistent with the text_span_count drift (S6: 8→6) and should be noted as additional wrapper drift evidence for any future repository-mediated follow-up.

## Finding 2 (Non-blocking) - Regression row matched context is empty in current matrix

The evidence report documents that all three regression rows (F015, S5-F023, S6-F035) have empty `matched_row_label_path`, `matched_column_header_path`, and `matched_table_context` in the current matrix. The prior matrix had populated paths for these rows. The evidence report correctly attributes this to wrapper/reference-bundle construction drift. However, the empty current paths mean the diagnostic can only compare prior-vs-empty rather than prior-vs-different-context. This is an inherent limitation of the committed-JSON-only approach and is already covered by the `json_artifacts_insufficient_for_exact_producer_line` finding.

## Self-check

- Evidence report and comparability_matrix.json read and cross-checked.
- Prior/current summary (13/4 vs 10/7, delta -3) verified against committed matrices.
- Regression rows (F015, S5-F023, S6-F035) verified.
- Target seven (prior 3/7, current 2/7) verified.
- Schema invariants verified from JSON structure.
- Classification supported by 5 categories of committed-JSON evidence.
- No overclaims of helper correctness identified.
- Boundary preservation confirmed.
- No repository/live/network commands used.
- Artifact written to allowed path only.
