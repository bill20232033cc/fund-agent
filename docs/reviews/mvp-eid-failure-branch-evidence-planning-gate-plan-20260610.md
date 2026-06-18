# MVP EID Failure-Branch Evidence Planning Gate Plan - 2026-06-10

## Goal

Plan a no-live evidence gate for EID annual-report failure branches.

The future evidence gate must prove how current EID single-source annual-report acquisition classifies and propagates failures without invoking live EID, fallback, provider, LLM, PDF repository acquisition or network.

## Direct Evidence

- Current production source policy is EID single-source only:
  - `selected_source = eid`
  - `source_mode = single_source_only`
  - `fallback_enabled = false`
- Current code defines five annual-report source failure categories:
  - `not_found`
  - `unavailable`
  - `schema_drift`
  - `identity_mismatch`
  - `integrity_error`
- `_FALLBACK_ELIGIBLE_CATEGORIES` still names `not_found` and `unavailable`, but current single-source orchestration has only EID and therefore terminates after the EID failure rather than invoking fallback.
- `schema_drift`, `identity_mismatch` and `integrity_error` are fail-closed categories that must be represented by `AnnualReportSourceFallbackBlockedError` at orchestration boundary.
- Existing tests in `tests/fund/documents/test_annual_report_sources.py` already use `httpx.MockTransport`, fake sources and small PDF bytes to cover many EID failure paths without live network.

## Scope

Allowed planning scope:

- Define a future no-live evidence matrix for each EID failure category.
- Define evidence artifact shape and test commands.
- Define missing evidence gaps that a future implementation/evidence gate may add.
- Define stop conditions and preserved boundaries.

Allowed files for this planning gate:

- `docs/reviews/mvp-eid-failure-branch-evidence-planning-gate-*.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`

## Non-Goals

- No live EID calls.
- No PDF read from local annual-report directory.
- No `FundDocumentRepository` live acquisition.
- No fallback invocation, Eastmoney/CNINFO/fund-company source activation or source-policy change.
- No provider, live LLM, endpoint probe, config/default/runtime/budget change.
- No fixture projection, golden/readiness promotion, score-loop, renderer/checklist/quality change, downstream integration implementation or release/PR action.
- No production code change in this planning gate.

## Future Evidence Matrix

The later evidence gate should produce a Markdown evidence artifact and, if useful, a small JSON sidecar with this matrix:

| Category | EID branch to prove | Expected boundary behavior | Existing evidence source |
|---|---|---|---|
| `not_found` | `validate_fund.do` returns `isSuccess=false`; exact annual-report query returns empty `aaData` | EID source raises `AnnualReportSourceNotFoundError`; single-source orchestrator raises terminal not-found; no fallback source is invoked | `test_eid_source_validate_fund_false_is_not_found`; `test_eid_source_search_empty_is_not_found`; `test_orchestrator_terminal_not_found_does_not_fallback`; `test_orchestrator_not_found_terminal_in_single_source` |
| `unavailable` | transient HTTP timeout or EID service unavailable response | EID source raises `AnnualReportSourceUnavailableError`; single-source orchestrator raises terminal unavailable; no fallback source is invoked | `test_eid_source_transient_http_error_is_unavailable`; `test_orchestrator_terminal_unavailable_does_not_fallback` |
| `schema_drift` | invalid JSON shape, missing required EID fields, duplicate valid candidates, unsupported attachment path | EID source raises `AnnualReportSourceSchemaError`; orchestration boundary should classify as `schema_drift` and fail closed | `test_eid_source_validate_schema_error_fails_closed`; `test_eid_source_rejects_duplicate_candidates`; `test_eid_source_rejects_attachment_candidate` |
| `identity_mismatch` | candidate fund/year/report identity contradicts request | EID source raises `AnnualReportSourceMismatchError`; orchestration boundary classifies as `identity_mismatch` and fails closed | `test_eid_source_rejects_mismatched_candidates`; `test_orchestrator_does_not_fallback_after_eid_mismatch`; `test_orchestrator_stops_on_mismatch_error` |
| `integrity_error` | PDF Content-Type or magic bytes invalid; atomic write rejects non-PDF bytes | EID source raises `AnnualReportSourceIntegrityError`; orchestration boundary classifies as `integrity_error` and fails closed | `test_eid_source_pdf_content_type_must_be_pdf`; `test_eid_source_pdf_magic_bytes_must_be_pdf`; `test_write_pdf_bytes_atomic_rejects_invalid_pdf_bytes` |

## Evidence Gaps To Resolve Later

The future evidence gate should add or verify focused no-live tests if current tests do not already assert them:

1. Orchestrator boundary classification for `schema_drift` from an EID source error includes `blocking_failure.category == "schema_drift"`.
2. Orchestrator boundary classification for `integrity_error` from an EID source error includes `blocking_failure.category == "integrity_error"`.
3. Single-source terminal `not_found` and `unavailable` evidence explicitly states that eligible categories do not imply fallback because there is no second source in current production mode.
4. Evidence artifact records that all branches use fake source / MockTransport only and do not read local annual-report PDFs.

## Proposed Future Slices

Slice A: no-live test gap closure.

- Add only missing boundary tests in `tests/fund/documents/test_annual_report_sources.py`.
- Do not change `fund_agent/fund/documents/sources.py` unless a test exposes a current bug.
- Expected validation:

```bash
uv run pytest tests/fund/documents/test_annual_report_sources.py -q
uv run ruff check tests/fund/documents/test_annual_report_sources.py
git diff --check -- tests/fund/documents/test_annual_report_sources.py docs/reviews/mvp-eid-failure-branch-evidence-*.md
```

Slice B: evidence artifact.

- Write `docs/reviews/mvp-eid-failure-branch-evidence-20260610.md`.
- Include the five-category matrix, exact tests used as proof, and residual gaps if any remain.
- Explicitly state:
  - `not_found` / `unavailable` are fallback-eligible in abstract but terminal in current single-source mode.
  - `schema_drift` / `identity_mismatch` / `integrity_error` are fail-closed.
  - no live EID, repository live acquisition, fallback, provider or network ran.

Slice C: control sync.

- Update `docs/current-startup-packet.md` and `docs/implementation-control.md` after evidence is accepted.
- Next entry after evidence should remain user-directed: downstream implementation or another separately authorized phase.

## Stop Conditions

- Stop if evidence would require live EID, network, local PDF reads, repository live acquisition, fallback or source-policy changes.
- Stop if a category cannot be proven no-live with existing public test seams.
- Stop if a test reveals production behavior that contradicts accepted single-source policy.
- Stop if evidence tries to promote golden/readiness or authorize fallback.
- Stop if downstream integration implementation is requested before this evidence planning is accepted.

## Completion Report Format

Future evidence closeout must report:

- evidence artifact path;
- tests used for each failure category;
- exact validation commands and results;
- any accepted code/test changes;
- explicit no-live/no-fallback boundary;
- residual risks and next recommended gate.
