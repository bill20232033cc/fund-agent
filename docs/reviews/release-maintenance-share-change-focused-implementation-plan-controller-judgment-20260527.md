# Controller Judgment: share_change Focused Implementation Plan

> Date: 2026-05-27
> Controller: Codex
> Gate: `share_change focused implementation plan + bond-lens contract design choice`
> Plan: `docs/reviews/release-maintenance-share-change-focused-implementation-plan-20260527.md`
> Reviews:
> - `docs/reviews/release-maintenance-share-change-focused-implementation-plan-review-mimo-20260527.md`
> - `docs/reviews/release-maintenance-share-change-focused-implementation-plan-review-glm-20260527.md`
> Verdict: **ACCEPTED FOR NARROW IMPLEMENTATION**

## Startup Reconciliation

The current Startup Packet says the phase is `release maintenance`, the current gate is `baseline coverage / source recovery / taxonomy + bond triage accepted locally`, and the next entry point is `share_change focused implementation plan + bond-lens contract design choice plan/review`.

The latest accepted checkpoint before this plan is `cd176d0`.

## Findings Judgment

| Finding | Judgment | Controller rationale |
|---|---|---|
| MiMo review: no findings; implementation should be authorized | Accepted | The plan is scoped to one same-source extractor gap and preserves fail-closed behavior. |
| GLM F3: `share_class_selection_reason` may require model scope | Accepted with boundary | Implementation should first use existing note/metadata shape if sufficient. `fund_agent/fund/extractors/models.py` is conditionally allowed only if existing result types cannot carry `share_class_column` / `share_class_selection_reason`; if changing that model expands downstream contracts, stop and return to controller. |
| GLM info findings: reconciliation, root cause, fail-closed semantics, tests, holdings deferral, verifier | Accepted | These findings confirm the plan aligns with current truth and supports narrow implementation. |

## Authorized Implementation Scope

Authorize implementation only for the `share_change` ambiguity slice.

Allowed production files:

- `fund_agent/fund/extractors/holdings_share_change.py`
- `fund_agent/fund/extractors/models.py` only if required to represent `share_class_column` / `share_class_selection_reason` and only if the change does not broaden public contracts beyond the extractor result shape

Allowed tests:

- `tests/fund/extractors/test_holdings_share_change.py`
- focused regression tests in `tests/fund/test_extraction_snapshot.py`, `tests/fund/test_extraction_score.py`, and `tests/fund/test_quality_gate.py` only if needed to prove observations or unchanged FQ behavior

Allowed docs:

- `fund_agent/fund/README.md` only if implementation changes documented Fund package behavior. It is not expected for a private extractor fix.

Forbidden:

- renderer, FQ0-FQ6 weakening, Service/CLI defaults, Host/Agent/dayu, `FundDocumentRepository`, source fallback, direct PDF/cache/source helpers, golden corpus, durable fixtures, package config, GitHub mutation;
- `turnover_rate`, `holder_structure`, `investor_return`, `nav_data`, or `holdings_snapshot` implementation;
- silently choosing A class, first non-empty column, total-share column, or a different fund-code column when share class cannot be proven.

## Required Behavior

The implementation must:

- choose a share-change value column only with deterministic evidence tied to the requested `fund_code`;
- preserve explicit missing/ambiguity when deterministic selection cannot be proven;
- keep quality-gate strictness unchanged;
- keep `holdings_snapshot` deferred to a future bond-lens evidence-contract gate;
- keep golden corpus v1 ineligible.

## Required Validation

Minimum validation:

- `uv run pytest tests/fund/extractors/test_holdings_share_change.py`
- `uv run ruff check fund_agent/fund/extractors/holdings_share_change.py tests/fund/extractors/test_holdings_share_change.py`
- `uv run fund-analysis extraction-snapshot --run-id share-change-focused-006597-2024 --fund-code 006597 --report-year 2024`
- `uv run fund-analysis extraction-score --snapshot-path reports/extraction-snapshots/share-change-focused-006597-2024/snapshot.jsonl --errors-path reports/extraction-snapshots/share-change-focused-006597-2024/errors.jsonl --golden-answer-path reports/golden-answers/golden-answer.json`
- `uv run fund-analysis quality-gate --score-path reports/extraction-snapshots/share-change-focused-006597-2024/score.json`
- `git diff --check`

Run focused snapshot/score/quality tests if those files or behaviors are touched. Run full `uv run pytest` if shared models, snapshot, score, quality gate, parsed report models, or any broader surface changes.

## Verdict

Proceed to narrow implementation. Stop and return to controller if deterministic selection cannot be proven from parsed report sections/tables, if model changes broaden downstream contracts, or if any forbidden boundary is needed.
