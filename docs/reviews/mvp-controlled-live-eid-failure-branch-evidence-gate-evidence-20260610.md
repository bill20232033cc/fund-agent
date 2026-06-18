# Controlled Live EID Failure-Branch Evidence Gate Evidence - 2026-06-10

## Scope

This artifact records the one live command authorized by `docs/reviews/mvp-controlled-live-eid-failure-branch-evidence-gate-plan-controller-judgment-20260610.md`.

The command was executed exactly once. It was not retried, expanded to additional rows, or replaced with an inline command.

## Authorized Command

```bash
uv run python scripts/controlled_live_eid_failure_branch_observation.py
```

Target row:

| Field | Value |
|---|---|
| fund_code | `006597` |
| report_year | `2024` |
| source route | EID single-source via `FundDocumentRepository.load_annual_report()` |

## Pre-Run State

Pre-checks showed no tracked workspace modifications. Existing untracked files were historical residue outside this gate.

## Execution Result

| Field | Value |
|---|---|
| exit_code | `1` |
| stdout | empty |
| stderr | Python traceback |
| final observed exception | `AttributeError: 'AnnualReportSourceMetadata' object has no attribute 'identity_status'` |
| script location | `scripts/controlled_live_eid_failure_branch_observation.py` |
| failing statement | `_safe_report_payload()` attempted to read `source_metadata.identity_status` |

Relevant traceback summary:

```text
asyncio.run(_run_observation())
...
return _safe_report_payload(report)
...
"identity_status": source_metadata.identity_status if source_metadata else None
AttributeError: 'AnnualReportSourceMetadata' object has no attribute 'identity_status'
```

## Classification

`blocked_helper_serialization_error_after_acquisition`.

The live command reached the post-acquisition serialization path: `_run_observation()` returned from `repository.load_annual_report("006597", 2024, force_refresh=True)` with a `report` object and then failed while converting repo metadata to safe JSON scalars.

This is direct evidence of a gate-local helper serialization defect, not accepted live success evidence and not live failure-branch proof.

## Repository Fact Check

Repo models currently define `AnnualReportSourceMetadata` without `identity_status` or `integrity_status` fields. The helper script overclaimed the metadata shape by attempting to serialize those two non-existent attributes.

The accepted EID single-source source-policy metadata fields remain `source`, `selected_source`, `source_mode`, `fallback_enabled`, `fallback_used`, and `primary_failure_category` plus related cache metadata.

## Non-Events

The gate did not run:

- retry or second live EID attempt
- additional fund/year rows
- Eastmoney, CNINFO, fund-company official website/CDN or any other non-EID source
- fallback invocation
- provider, LLM, endpoint, DNS, curl, socket or API-key probe
- `FundDataExtractor`, deterministic `analyze`, `checklist`, renderer or quality gate
- Service, Host, Agent runtime expansion
- fixture projection, golden/readiness promotion, score-loop, release, PR action, push or merge

## Evidence Disposition

Accepted no-live checkpoint `ac6bbe9` remains the accepted code-behavior proof for all five EID failure categories: `not_found`, `unavailable`, `schema_drift`, `identity_mismatch`, and `integrity_error`.

This live gate consumed its single authorized live attempt and did not produce accepted safe JSON stdout. Therefore:

- Do not word this gate as `accepted_live_window_no_failure_observed`.
- Do not word this gate as live proof that EID failure branches occur naturally.
- Do not rerun the live command inside this authorization.
- Any helper repair and live retry requires a new reviewed plan and separate explicit authorization.

## Post-Run Validation

Post-checks:

```bash
git status --short
git status --branch --short
git diff --check
```

Observed result: no tracked workspace modifications from the live command; `git diff --check` passed.

## Residual

`controlled_live_eid_helper_repair_and_retry` remains deferred. The minimum future scope is to remove or replace the two non-existent metadata reads in the gate-local helper, re-review the repair, and request a separate controlled live retry authorization before another network/FDR acquisition command is run.
