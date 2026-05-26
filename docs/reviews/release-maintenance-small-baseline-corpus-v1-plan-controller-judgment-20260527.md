# Controller Judgment: Small Baseline Corpus v1 Plan

> Date: 2026-05-27
> Controller: Codex
> Gate: `small baseline corpus v1 plan/review`
> Plan: `docs/reviews/release-maintenance-small-baseline-corpus-v1-plan-20260527.md`
> Plan reviews:
> - `docs/reviews/release-maintenance-small-baseline-corpus-v1-plan-review-mimo-20260527.md`
> - `docs/reviews/release-maintenance-small-baseline-corpus-v1-plan-review-glm-20260527.md`
> Targeted re-reviews:
> - `docs/reviews/release-maintenance-small-baseline-corpus-v1-plan-rereview-mimo-20260527.md`
> - `docs/reviews/release-maintenance-small-baseline-corpus-v1-plan-rereview-glm-20260527.md`
> Verdict: **ACCEPTED FOR EVALUATION RUN**

## Startup Reconciliation

The current Startup Packet says the phase is `release maintenance`, the current gate is `core analyze/checklist reliability hardening accepted locally`, and the next entry point is `small baseline corpus v1 plan/review`. The latest accepted checkpoint is local commit `1aca29b`.

The accepted artifacts already include active-fund Chapter 3 renderer minimal integration, so this gate does not repeat renderer implementation. The next executable work is the small baseline corpus v1 evaluation run.

## Controller Findings Judgment

| Reviewer finding | Judgment | Controller rationale |
|---|---|---|
| MiMo M1: plan-only gate should mandate `git diff --check` | Accepted; resolved | The revised plan adds `git diff --check` to the verifier matrix and validation section. This is the minimal hygiene check for a tracked documentation artifact. |
| MiMo M2: clarify `selected_funds_smoke.py` dry-run scope | Accepted; resolved | The revised plan states the dry-run validates argument parsing and command construction only, with no availability confidence and no network/cache expectation. |
| MiMo I3: control doc current-gate update timing | Accepted for closeout | The control doc should be updated at Gate 4 closeout after the run/review result is known, not during plan-only review. |
| GLM F1: clean denominator only covers three fund-type slots | Accepted; resolved | The revised plan records the 3-clean-candidate / 3-slot coverage as a residual and routes coverage at or below three clean candidates, or fewer than half target slots, to more probing/source recovery/taxonomy rather than golden promotion. |
| GLM F2: golden coverage expectation missing | Accepted; resolved | The revised plan separates golden-covered from golden-missing observations and states that `004194` / 2024 and `006597` / 2024 are expected to produce `year_not_covered` / `FQ0/info`, not correctness signal. |
| GLM F3: seven-row vs eight-row mismatch | Accepted; resolved | The revised plan now uses eight candidate rows across seven unique fund codes, because `004393` appears for 2024 and 2025. |
| GLM F4: `--dev-override` final-judgment semantics unclear | Accepted; resolved | The revised plan states that `004393` / 2025 `--dev-override` smoke records only exit, quality-gate summary, availability, and report-year scope, not final-judgment semantics. |

## Accepted Implementation Scope

Proceed to a bounded evaluation run that creates a tracked summary artifact under `docs/reviews/` and leaves bulk outputs in ignored scratch paths.

Allowed:

- run the explicit product smoke and candidate probing commands from the accepted plan;
- use ignored scratch paths under `/tmp/...` or `reports/...`;
- write a tracked summary artifact with candidate status, evidence paths, issue taxonomy, false-positive suspicion, suitability for future golden, and next gate recommendation;
- run `git diff --check` before handoff.

Forbidden:

- modifying renderer, FQ0-FQ6, Service/CLI defaults, Host/Agent/dayu, `FundDocumentRepository`, concrete source fallback, extractors, tests, source code, package config, durable fixtures, golden corpus, or default product behavior;
- committing large run outputs;
- treating fallback-blocked or FOF data-gap rows as clean baseline coverage;
- treating missing same-year golden coverage as extraction failure;
- using `--dev-override` output to judge final report quality;
- GitHub mutation.

## Gate Acceptance Criteria For The Run

- At least the three clean candidates are evaluated or have explicit, directly evidenced failure categories.
- Index/QDII fallback-blocked and FOF data-gap rows remain visible but excluded from the clean denominator unless source recovery is independently proven.
- The tracked summary artifact records annual-report availability, extraction gaps, quality-gate status, report-quality categories, false-positive suspicion, required next action, and future-golden suitability per row.
- Bulk outputs remain in scratch/ignored paths.
- `git diff --check` passes.

## Verdict

The revised plan is code-generation-ready for the small baseline corpus v1 evaluation run. All material findings are resolved, no scope drift was introduced, and the gate may proceed to bounded evaluation.
