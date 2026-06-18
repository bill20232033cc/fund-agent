# Docling Reference Bundle Evidence Comparability and Producer Determinism Diagnostic Plan Controller Judgment - 2026-06-17

Gate: `Docling Reference Bundle Evidence Comparability and Producer Determinism Diagnostic Planning Gate`
Role: controller
Status: `ACCEPTED_PLAN`
Verdict: `ACCEPT_PLAN_READY_FOR_NO_LIVE_DIAGNOSTIC_EVIDENCE_NOT_READY`

## Inputs

- Plan: `docs/reviews/docling-reference-bundle-evidence-comparability-determinism-diagnostic-plan-20260617.md`
- AgentDS plan review: `docs/reviews/docling-reference-bundle-evidence-comparability-determinism-diagnostic-plan-review-ds-20260617.md`
- AgentMiMo plan review: `docs/reviews/docling-reference-bundle-evidence-comparability-determinism-diagnostic-plan-review-mimo-20260617.md`
- Blocked re-evidence checkpoint commit: `7b757d1`

## Decision

The plan is accepted for the next no-live diagnostic evidence gate.

It is handoff-ready because it defines:

- current facts: prior `13/4`, current `10/7`, delta `-3`;
- exact regression rows: `F015`, `S5-F023`, `S6-F035`;
- exact input artifacts and output artifacts;
- JSON-first comparability workflow;
- machine-readable `comparability_matrix.json` schema;
- validation commands and stop conditions;
- review and controller judgment gates.

## Review Findings

- AgentDS verdict: `PASS`, blocking findings `0`, non-blocking findings `3`.
- AgentMiMo verdict: `PASS`, blocking findings `0`, non-blocking findings `0`.

Controller disposition for AgentDS non-blocking findings:

| Finding | Disposition |
| --- | --- |
| Regression rows with empty current matched paths may only support prior-vs-empty comparison | Accepted as expected limitation; no plan change required because `json_artifacts_insufficient_for_root_cause` already covers this. |
| S5 text_span_count stayed `6 -> 6` while span content may have drifted | Accepted as evidence-worker attention item; no plan change required because matched-context and section-inference comparison already cover this. |
| F015 row path shown with `>` notation though JSON stores an array | Accepted as presentation-only note; plan already requires exact array comparison. |

## Boundary Decision

The next gate remains no-live and candidate-only:

- no Docling baseline promotion;
- no source truth acceptance;
- no parser replacement;
- no full field correctness claim;
- no golden/readiness/release/PR claim;
- no direct PDF/cache/source-helper access;
- no repository reload unless a later separately authorized gate explicitly allows `FundDocumentRepository.load_annual_report(..., force_refresh=False)` with socket guard.

## Next Gate

Proceed to `Docling Reference Bundle Comparability Diagnostic No-live Evidence Gate`.

Allowed future evidence write set:

- `reports/docling-reference-bundle-comparability-diagnostic/20260617/comparability_matrix.json`
- `docs/reviews/docling-reference-bundle-comparability-diagnostic-evidence-20260617.md`

Expected final verdict token is one of:

- `COMPARABILITY_DIAGNOSTIC_WRAPPER_DRIFT_IDENTIFIED_NOT_READY`
- `COMPARABILITY_DIAGNOSTIC_HELPER_DRIFT_SUSPECTED_NOT_READY`
- `COMPARABILITY_DIAGNOSTIC_INSUFFICIENT_JSON_EVIDENCE_BLOCKED_NOT_READY`
- `COMPARABILITY_DIAGNOSTIC_NO_DRIFT_FOUND_BLOCKED_NOT_READY`

## Controller Self-check

- Current role: controller plan judgment.
- Source of truth: plan artifact, DS/MiMo plan reviews, blocked re-evidence checkpoint.
- Scope boundary: judgment artifact only; no code, tests, runtime, control, design, README, source truth, baseline, release, PR, or live action.
- Stop conditions: none blocking plan acceptance.
- Evidence and validation: DS/MiMo reviews have zero blocking findings; `git diff --check` passed for plan and review artifacts.
- Next action: create local accepted plan checkpoint, then start the no-live diagnostic evidence gate.
