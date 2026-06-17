# Docling Reference Bundle Residual Closure Re-evidence Plan Controller Judgment - 2026-06-17

Gate: `Docling Reference Bundle Residual Closure Re-evidence Planning Gate`
Role: controller
Status: `PLAN_ACCEPTED_READY_FOR_EVIDENCE_NOT_READY`
Verdict: `ACCEPT_PLAN_READY_FOR_RESIDUAL_CLOSURE_REEVIDENCE_NOT_READY`
Release/readiness: `NOT_READY`

## Inputs

- Plan: `docs/reviews/docling-reference-bundle-residual-closure-reevidence-plan-20260617.md`
- DS plan review: `docs/reviews/docling-reference-bundle-residual-closure-reevidence-plan-review-ds-20260617.md`
- MiMo plan review: `docs/reviews/docling-reference-bundle-residual-closure-reevidence-plan-review-mimo-20260617.md`
- Accepted producer determinism evidence judgment: `docs/reviews/docling-reference-bundle-producer-determinism-evidence-controller-judgment-20260617.md`
- Accepted producer determinism implementation judgment: `docs/reviews/docling-reference-bundle-producer-determinism-no-live-implementation-controller-judgment-20260617.md`

## Decision

Accept the plan for the next no-live evidence gate.

Controller basis:

- DS review verdict: `PLAN_REVIEW_PASS_NOT_READY`.
- MiMo review verdict: `PLAN_REVIEW_PASS_NOT_READY`.
- No material blocking findings were reported by either reviewer.
- Advisory findings are non-blocking and are covered by the plan's non-goals, stop conditions, comparability rules, verdict taxonomy, and explicit `NOT_READY` boundary.
- `git diff --check` passed for the plan and review artifacts.

Accepted plan facts:

- The next gate is a no-live evidence gate, not implementation and not source-truth adjudication.
- The future evidence gate may write only:
  - `reports/docling-reference-bundle-residual-closure-reevidence/20260617/residual_closure_matrix.json`
  - `docs/reviews/docling-reference-bundle-residual-closure-reevidence-20260617.md`
- The future evidence scope is exactly the existing 17 residual-closure rows.
- The future evidence must explicitly cover residual seven rows, regression rows `F015`, `S5-F023`, `S6-F035`, and fail-closed locks `S6-F041`, `S6-F049`, `S6-F050`.
- The future evidence must compare sample identity, row identity, repository metadata, producer diagnostics availability, counts, `bundle_content_fingerprint`, and `producer_contract_version` before interpreting closure-count movement.
- If comparability fails, the future evidence must emit a blocked `NOT_READY` verdict and must not claim helper improvement or regression.

## Boundary Decision

This accepted plan does not authorize:

- live/network/provider/LLM/analyze/checklist/golden/readiness/release/PR commands;
- direct PDF/cache/source-helper access;
- fresh fetch or repository reload;
- code, test, README, design, control-doc, or production behavior changes;
- source truth acceptance;
- Docling baseline promotion;
- parser replacement;
- full field correctness;
- golden readiness, release readiness, or PR readiness.

The following remain binding:

- `candidate_only=true`;
- `source_truth_status=not_proven`;
- release/readiness remains `NOT_READY`.

## Review Advisory Disposition

- DS advisory on making `force_refresh=false` explicit is not blocking. The plan already forbids fresh fetch and repository reload; the future evidence worker should still include or assert `force_refresh=false` if the sample diagnostics expose that field.
- DS advisory on diagnostic payload sub-schema is not blocking. The accepted implementation defines row diagnostic payload structures, and the future evidence worker is expected to consume those implemented helper payloads without inventing new schema.
- MiMo advisory on prior-matrix missing fingerprints is not blocking. The accepted plan already states old matrices cannot be retroactively fingerprinted and requires blocked non-comparable handling before any delta interpretation.
- MiMo advisory on `PLAN_NOT_READY` wording is not blocking because the controller acceptance status here is explicitly `PLAN_ACCEPTED_READY_FOR_EVIDENCE_NOT_READY`, while release/readiness remains `NOT_READY`.

## Validation

Controller validation:

```text
git diff --check -- docs/reviews/docling-reference-bundle-residual-closure-reevidence-plan-20260617.md docs/reviews/docling-reference-bundle-residual-closure-reevidence-plan-review-ds-20260617.md docs/reviews/docling-reference-bundle-residual-closure-reevidence-plan-review-mimo-20260617.md docs/reviews/docling-reference-bundle-residual-closure-reevidence-plan-controller-judgment-20260617.md
```

Result: pass.

## Next Gate

Enter:

`Docling Reference Bundle Residual Closure Re-evidence Gate`

Future evidence worker stop condition:

- stop after writing exactly the two accepted evidence artifacts and reporting validation/verdict;
- do not proceed to evidence review, implementation, readiness, release, PR, source-truth, baseline, parser replacement, or golden gates.

## Controller Self-check

- Current role: controller acceptance after plan and two independent plan reviews.
- Source of truth: accepted producer determinism implementation/evidence judgments, current plan artifact, DS review, MiMo review.
- Scope boundary: controller judgment artifact only; no implementation, no evidence execution, no source access, no design/control sync, no readiness/release/PR action.
- Validation: diff check passed.
- Stop conditions: no material blocking finding, no unresolved open question, no unclassified residual risk for plan acceptance.
- Next action: create local accepted plan checkpoint.

VERDICT: `ACCEPT_PLAN_READY_FOR_RESIDUAL_CLOSURE_REEVIDENCE_NOT_READY`
