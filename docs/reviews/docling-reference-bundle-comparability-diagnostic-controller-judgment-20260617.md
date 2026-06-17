# Docling Reference Bundle Comparability Diagnostic Controller Judgment - 2026-06-17

Gate: `Docling Reference Bundle Comparability Diagnostic No-live Evidence Gate`
Role: controller
Status: `ACCEPTED_DIAGNOSTIC_EVIDENCE_NOT_READY`
Verdict: `ACCEPT_COMPARABILITY_DIAGNOSTIC_WRAPPER_DRIFT_IDENTIFIED_NOT_READY`

## Inputs

- Diagnostic matrix: `reports/docling-reference-bundle-comparability-diagnostic/20260617/comparability_matrix.json`
- Diagnostic evidence report: `docs/reviews/docling-reference-bundle-comparability-diagnostic-evidence-20260617.md`
- AgentDS review: `docs/reviews/docling-reference-bundle-comparability-diagnostic-evidence-review-ds-20260617.md`
- AgentMiMo review: `docs/reviews/docling-reference-bundle-comparability-diagnostic-evidence-review-mimo-20260617.md`
- Accepted plan commit: `625b8c8`
- Blocked re-evidence checkpoint commit: `7b757d1`

## Decision

The no-live comparability diagnostic evidence is accepted.

Controller conclusion:

1. The prior `13/4` matrix and current `10/7` matrix are not comparable enough for another residual-closure interpretation.
2. The committed JSON artifacts identify wrapper/reference-bundle construction drift before helper semantics.
3. The diagnostic does not identify the exact producer code line because committed JSON lacks raw cell/text-span payloads.
4. The current Docling evidence remains `NOT_READY`; there is no Docling baseline promotion.

## Accepted Diagnostic Facts

- Prior accepted checkpoint: `13 closed / 4 residual`.
- Current blocked re-evidence: `10 closed / 7 residual`.
- Delta: `-3` closed rows.
- Regression rows: `F015`, `S5-F023`, `S6-F035`.
- Target seven: prior `3/7` closed; current `2/7` closed.
- All four samples show repository load count drift and section inference drift.
- Text span counts drift in `S1`, `S4`, and `S6`; `S5` shows content/context drift despite stable text span count.
- Row-level matched context drift is present across multiple rows.
- `S5-F023` and `S6-F041` show source layer status drift to `same_source_text_absent`.

Accepted verdict token:

`COMPARABILITY_DIAGNOSTIC_WRAPPER_DRIFT_IDENTIFIED_NOT_READY`

## Review Results

- AgentDS verdict: `PASS`, blocking findings `0`, non-blocking findings `1`.
- AgentMiMo verdict: `PASS`, blocking findings `0`, non-blocking findings `2`.

Controller disposition:

| Review finding | Disposition |
| --- | --- |
| `S6-F041` status drift is not a regression but should remain visible | Accepted as non-blocking follow-up attention item. |
| Current regression rows have empty matched paths, limiting exact root-cause diagnosis | Accepted as inherent committed-JSON limitation and already covered by `json_artifacts_insufficient_for_exact_producer_line`. |

No evidence fix is required before accepting this diagnostic gate.

## Boundary Decision

The diagnostic is accepted only as no-live comparability evidence.

It does not support:

- source truth acceptance;
- Docling baseline promotion;
- parser replacement;
- full field correctness;
- golden readiness;
- release readiness;
- PR readiness.

The following remain binding:

- `candidate_only=true`;
- `source_truth_status=not_proven`;
- `NOT_READY`;
- no direct PDF/cache/source-helper access;
- no repository object reload without a later explicit gate;
- no live/network/provider/LLM/analyze/checklist/golden/readiness/release command.

## Next Gate

Next gate should be a no-live wrapper/reference-bundle determinism implementation planning gate, not another residual-closure re-evidence retry.

Minimum objective:

- define a stable, reproducible reference-bundle producer contract for committed-matrix evidence;
- decide whether to persist enough raw cell/text-span payload or producer diagnostics to make future re-evidence comparable;
- preserve current `source_truth_status=not_proven` and candidate-only boundaries;
- avoid direct PDF/cache/source-helper access and avoid live acquisition unless separately authorized.

If exact producer-line root cause is required before implementation, create a separately scoped repository-mediated diagnostic gate using `FundDocumentRepository.load_annual_report(..., force_refresh=False)` with socket guard. That is not authorized by this judgment.

## Controller Self-check

- Current role: controller judgment only.
- Source of truth: diagnostic evidence matrix/report plus DS/MiMo evidence reviews.
- Scope boundary: judgment artifact only; no code, tests, runtime, control, design, README, baseline, source truth, release, PR, or live action.
- Validation observed: `python -m json.tool`, required `jq` invariants, and `git diff --check` passed.
- Stop conditions: do not run residual-closure re-evidence again until wrapper/reference-bundle determinism has a plan and accepted evidence path.
- Final decision: accept diagnostic evidence; proceed to planning for deterministic reference-bundle producer instrumentation/contract.
