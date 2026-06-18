# Controlled Live EID Failure-Branch Evidence Gate Plan Controller Judgment - 2026-06-10

## Judgment

ACCEPT.

The plan is accepted for one bounded live EID/FDR acquisition observation, using `FundDocumentRepository.load_annual_report()` and EID single-source wiring only. This judgment authorizes the next evidence step inside this gate, not any recurring live run, fallback source, source-policy change, provider/LLM action, fixture projection, golden/readiness promotion, score-loop, release or PR action.

## Basis

- User explicitly authorized entering `controlled live EID failure-branch evidence gate`.
- Current control truth names this gate as the next entry after downstream integration implementation checkpoint `c3b9061` and control sync `d65a7b7`.
- Boundary reviews from AgentDS and AgentMiMo both concluded `BLOCKED_FOR_PLAN`, requiring a reviewed controller plan before live execution.
- Plan reviews from AgentDS and AgentMiMo both returned `PASS_WITH_FINDINGS`.
- Targeted re-reviews from AgentDS and AgentMiMo both returned `PASS`, confirming all plan findings are resolved.

## Accepted Plan Artifacts

- Plan: `docs/reviews/mvp-controlled-live-eid-failure-branch-evidence-gate-plan-20260610.md`
- Boundary review DS: `docs/reviews/mvp-controlled-live-eid-failure-branch-evidence-gate-boundary-review-ds-20260610.md`
- Boundary review MiMo: `docs/reviews/mvp-controlled-live-eid-failure-branch-evidence-gate-boundary-review-mimo-20260610.md`
- Plan review DS: `docs/reviews/mvp-controlled-live-eid-failure-branch-evidence-gate-plan-review-ds-20260610.md`
- Plan review MiMo: `docs/reviews/mvp-controlled-live-eid-failure-branch-evidence-gate-plan-review-mimo-20260610.md`
- Plan re-review DS: `docs/reviews/mvp-controlled-live-eid-failure-branch-evidence-gate-plan-rereview-ds-20260610.md`
- Plan re-review MiMo: `docs/reviews/mvp-controlled-live-eid-failure-branch-evidence-gate-plan-rereview-mimo-20260610.md`
- Gate-local helper: `scripts/controlled_live_eid_failure_branch_observation.py`

## Finding Disposition

| Finding | Disposition | Basis |
|---|---|---|
| Direct live execution before plan/review is unsafe for this heavy gate. | ACCEPT_FIXED | A controller plan artifact, two boundary reviews, two plan reviews and two re-reviews now exist before live execution. |
| Live command was not fully pinned and helper script was absent. | ACCEPT_FIXED | The plan pins `uv run python scripts/controlled_live_eid_failure_branch_observation.py`; helper script is present and reviewed. |
| EID config/env readiness was unstated. | ACCEPT_FIXED | The plan states EID single-source acquisition has no API key, env var or typed config dependency; E1 provider readiness is not applicable. |
| Success label risked implying live failure-branch proof. | ACCEPT_FIXED | Outcome label is now `accepted_live_window_no_failure_observed` and explicitly states it is not live failure-branch proof. |
| No-live proof at `ac6bbe9` needed explicit preservation. | ACCEPT_FIXED | The plan states no-live evidence remains accepted proof for all five failure categories and cannot be replaced/upgraded by this live gate. |
| Parsed-document cache isolation was not feasible as originally written. | ACCEPT_FIXED | The helper uses a temporary EID PDF cache and replaces the repository instance `_cache` with `AnnualReportDocumentCache(root_dir=...)` under the same temporary root. |
| Constructor and helper/inline command ambiguity. | ACCEPT_FIXED | The helper explicitly wires EID source, single-source orchestrator, PDF adapter and repository; no inline fallback command is authorized. |
| Stop condition wording could imply stopping before recording failure. | ACCEPT_FIXED | The plan now requires recording classification per the outcome matrix, then stopping. |

## Accepted Live Execution Boundary

Authorized next step:

```bash
uv run python scripts/controlled_live_eid_failure_branch_observation.py
```

Pre-checks:

```bash
git status --short
git status --branch --short
```

Post-checks:

```bash
git status --short
git status --branch --short
git diff --check
```

The command is authorized exactly once for `006597 / 2024`. It must not be retried or expanded to additional rows without a new controller decision and user authorization.

## Evidence Rules

Evidence must be written to:

- `docs/reviews/mvp-controlled-live-eid-failure-branch-evidence-gate-evidence-20260610.md`

The evidence artifact must retain only safe scalars. It must not retain raw PDF bytes, full parsed text, full table contents, API secrets or any provider/LLM payload.

If the live command succeeds, final classification is `accepted_live_window_no_failure_observed`: the EID/FDR path worked during the observation window, and no natural live failure branch was observed. This must not be worded as live proof for the five failure categories.

If the live command fails, preserve the natural failure category or environment category, stop, and route to evidence review. Do not retry.

## Residuals

- Live `schema_drift`, `identity_mismatch`, `integrity_error`, `not_found` and `unavailable` are not guaranteed to occur under controlled conditions.
- No-live evidence at checkpoint `ac6bbe9` remains the accepted code-behavior proof for all five failure categories.
- Eastmoney, CNINFO, fund-company official website/CDN and other non-EID routes remain forbidden in this gate.
