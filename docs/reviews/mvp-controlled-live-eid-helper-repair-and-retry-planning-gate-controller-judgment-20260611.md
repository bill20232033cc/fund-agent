# Controlled Live EID Helper Repair And Retry Planning Gate Controller Judgment - 2026-06-11

## Judgment

ACCEPT_WITH_CONTROLLER_AMENDMENT.

The plan is accepted for Stage A no-live helper repair only. Stage B controlled live retry is not authorized by this judgment.

Controller amendment: the optional no-live regression test is accepted and becomes required for Stage A implementation. The implementation gate must add exactly one narrow test file, `tests/scripts/test_controlled_live_eid_failure_branch_observation.py`, unless implementation discovers the path cannot be collected by pytest and records a controller-approved equivalent no-live test path before coding.

## Basis

- `AGENTS.md`: production annual-report access must go through `FundDocumentRepository`; fallback/source policy must remain explicit and fail-closed; non-EID routes must not silently re-enter current policy.
- `docs/current-startup-packet.md` and `docs/implementation-control.md`: current next entry is `Controlled live EID helper repair and retry planning gate`; no additional PDF/FDR/network/`FundDocumentRepository` live acquisition is authorized before reviewed plan, controller judgment and separate explicit live authorization.
- Prior controller judgment `docs/reviews/mvp-controlled-live-eid-failure-branch-evidence-gate-controller-judgment-20260610.md`: previous command was consumed once and ended as `blocked_helper_serialization_error_after_acquisition`; this is not accepted live success evidence and not live failure-branch proof.
- Plan artifact `docs/reviews/mvp-controlled-live-eid-helper-repair-and-retry-planning-gate-plan-20260611.md`.
- DS plan review `docs/reviews/mvp-controlled-live-eid-helper-repair-and-retry-planning-gate-plan-review-ds-20260611.md`: `PASS`.
- MiMo plan review `docs/reviews/mvp-controlled-live-eid-helper-repair-and-retry-planning-gate-plan-review-mimo-20260611.md`: `PASS_WITH_FINDINGS`.

## Accepted Scope

Stage A may touch only:

- `scripts/controlled_live_eid_failure_branch_observation.py`
- `tests/scripts/test_controlled_live_eid_failure_branch_observation.py`
- `docs/reviews/mvp-controlled-live-eid-helper-repair-and-retry-implementation-evidence-20260611.md`
- `docs/reviews/mvp-controlled-live-eid-helper-repair-and-retry-code-review-ds-20260611.md`
- `docs/reviews/mvp-controlled-live-eid-helper-repair-and-retry-code-review-mimo-20260611.md`
- `docs/reviews/mvp-controlled-live-eid-helper-repair-and-retry-controller-judgment-20260611.md`

The test file must be no-live. It may call `_safe_report_payload()` with fake in-memory report, metadata and cache objects. It must not call `main()`, `_run_observation()`, `FundDocumentRepository`, `AnnualReportPdfAdapter`, `AnnualReportSourceOrchestrator`, `EidAnnualReportSource`, live network/FDR/PDF paths, fallback, provider, LLM, extractor, `analyze`, `checklist`, score-loop or golden/readiness code.

## Accepted Implementation Decisions

- Remove the two non-existent helper success-payload reads:
  - `source_metadata.identity_status`
  - `source_metadata.integrity_status`
- Do not add `identity_status` or `integrity_status` to `AnnualReportSourceMetadata`.
- Preserve current EID single-source helper wiring and target constants:
  - `FUND_CODE = "006597"`
  - `REPORT_YEAR = 2024`
- Preserve `FundDocumentRepository.load_annual_report(FUND_CODE, REPORT_YEAR, force_refresh=True)` for the later Stage B command only.
- Preserve gate-local temporary cache isolation.
- Optional `discovery_contract_version` success-payload field is accepted because it exists on current `AnnualReportSourceMetadata` and is a safe scalar; implementation may add it but is not required to.

## Required No-Live Validation

Stage A implementation must run:

```bash
uv run ruff check scripts/controlled_live_eid_failure_branch_observation.py tests/scripts/test_controlled_live_eid_failure_branch_observation.py
uv run python -m py_compile scripts/controlled_live_eid_failure_branch_observation.py
uv run pytest tests/scripts/test_controlled_live_eid_failure_branch_observation.py
git diff --check -- scripts/controlled_live_eid_failure_branch_observation.py tests/scripts/test_controlled_live_eid_failure_branch_observation.py docs/reviews/mvp-controlled-live-eid-helper-repair-and-retry-implementation-evidence-20260611.md
```

Forbidden in Stage A:

```bash
uv run python scripts/controlled_live_eid_failure_branch_observation.py
```

That command performs live acquisition and remains Stage B only after separate explicit live authorization.

## Finding Disposition

| Finding | Source | Disposition | Controller rationale |
|---|---|---|---|
| `docs/design.md` contains stale wording implying identity/integrity status fields exist. | DS F1 / MiMo F2 | DEFER | This planning gate must not resolve stale design wording by adding production fields. Defer to a future docs-sync gate. |
| Optional no-live regression test would add meaningful coverage. | DS F2 / MiMo F1 | ACCEPT_WITH_REWRITE | The optional test becomes required for Stage A. This is still no-live and directly covers the previous helper failure class. |
| Core safety checks pass: no Stage A live rerun, no production metadata expansion, EID single-source preserved, `ac6bbe9` preserved. | DS F3 / MiMo checklist | ACCEPT | The plan is handoff-ready once amended by this judgment. |

## Stage B Boundary

Stage B is not authorized.

If the user later explicitly authorizes Stage B after accepted Stage A implementation/review/judgment, the only candidate command remains:

```bash
uv run python scripts/controlled_live_eid_failure_branch_observation.py
```

It may run at most once for `006597 / 2024`; no retry, additional row, fallback, non-EID source, provider/LLM probe, extractor/analyze/checklist, fixture projection, golden/readiness, score-loop, release, PR action, push or merge is authorized by this judgment.

## Next Entry

Recommended next entry:

```text
controlled live EID helper repair Stage A no-live implementation gate
```

This next gate is implementation/review only and remains no-live.
