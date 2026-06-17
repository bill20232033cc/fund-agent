# Docling Reference Bundle Producer Row-hierarchy and Benchmark Semantic-label No-live Re-evidence Controller Judgment - 2026-06-17

Gate: `Docling Reference Bundle Producer Row-hierarchy and Benchmark Semantic-label No-live Re-evidence Gate`
Role: controller
Status: `BLOCKED_NOT_READY`
Verdict: `ACCEPT_BLOCKED_REEVIDENCE_REGRESSION_EVIDENCE_NOT_READY`

## Inputs

- Evidence matrix: `reports/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-reevidence/20260617/residual_closure_matrix.json`
- Evidence report: `docs/reviews/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-no-live-reevidence-20260617.md`
- AgentDS review: `docs/reviews/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-no-live-reevidence-review-ds-20260617.md`
- AgentMiMo review: `docs/reviews/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-no-live-reevidence-review-mimo-20260617.md`
- Prior accepted checkpoint: `reports/docling-reference-bundle-enrichment-residual-closure/20260617/residual_closure_matrix.json`
- Accepted implementation commit: `7f1d0f6`

## Controller Findings

1. The current re-evidence artifact is internally consistent and valid as a blocked/regression evidence record.
2. It is not successful re-evidence for the row-hierarchy / benchmark semantic-label implementation.
3. It does not support Docling baseline promotion, source truth acceptance, parser replacement, full field correctness, golden readiness, release readiness, or PR readiness.

## Current Matrix

- rows_total: `17`
- closed_rows_total: `10`
- residual_rows_total: `7`
- closure_dispositions:
  - `disambiguated_source_body_match`: `10`
  - `semantic_assignment_residual`: `5`
  - `source_body_mismatch`: `2`
- prior accepted checkpoint: `13 closed / 4 residual`
- delta_vs_previous_closed_rows: `-3`
- verdict: `RESIDUAL_CLOSURE_REEVIDENCE_REGRESSION_BLOCKED_NOT_READY`

Regression rows versus the prior checkpoint:

| Sample | Fact | Field | Current Disposition |
| --- | --- | --- | --- |
| `S1` | `F015` | `sales_service_fee_C_current_year` | `semantic_assignment_residual` |
| `S5` | `S5-F023` | `investment_objective` | `source_body_mismatch` |
| `S6` | `S6-F035` | `fund_name` | `semantic_assignment_residual` |

Target seven status:

- closed: `2` (`F020`, `S4-F015`)
- residual: `5` (`F015`, `S5-F032`, `S6-F041`, `S6-F049`, `S6-F050`)

## Review Results

- AgentDS verdict: `PASS`, blocking findings `0`; artifact is valid blocked/regression evidence and cannot be accepted as successful re-evidence.
- AgentMiMo verdict: `PASS_WITH_FINDINGS`, blocking findings `0`; artifact is valid blocked/regression evidence and cannot be accepted as successful re-evidence.

The review loop required correction because an intermediate controller read saw an earlier `11/6` matrix state while the final disk artifact had been overwritten to `10/7`. The accepted review artifacts now match the current disk evidence artifact.

## Boundary Decision

The following boundaries remain binding:

- `candidate_only=true`
- `source_truth_status=not_proven`
- `NOT_READY`
- no source truth acceptance
- no Docling baseline promotion
- no parser replacement
- no full field correctness claim
- no release readiness, PR readiness, or golden readiness claim
- no code/tests/control/design/README changes in this gate

## Residual Owner

Owner: next planning gate.

Required next gate: design a no-live evidence comparability / reference-bundle determinism diagnostic before any further residual-closure re-evidence. The next gate must determine why the wrapper output changed between checkpoints, including cell counts, text span counts, section inference counts, and row/text context construction. It must not promote Docling to baseline and must not run live acquisition without explicit authorization.

## Controller Self-check

- Current role: controller judgment only.
- Source of truth: current disk evidence matrix/report and DS/MiMo review artifacts.
- Scope boundary: judgment artifact only; no code, tests, design, control, README, source truth, baseline, release, PR, or live actions.
- Stop condition: current gate is blocked by regression; proceed only to a follow-up diagnostic planning gate, not baseline promotion.
- Validation observed: `python -m json.tool` and `git diff --check` passed for current evidence and review artifacts.
- Final decision: accept this as blocked/regression evidence; do not accept as successful re-evidence.
