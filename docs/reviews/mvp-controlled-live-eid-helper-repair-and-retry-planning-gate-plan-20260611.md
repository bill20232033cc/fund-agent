# Controlled Live EID Helper Repair And Retry Planning Gate Plan - 2026-06-11
Status: DRAFT_FOR_REVIEW

## Goal

Plan the minimum repair path for the gate-local controlled live EID observation helper after the previous live evidence gate ended as `blocked_helper_serialization_error_after_acquisition`.

The implementation target is narrow: make `scripts/controlled_live_eid_failure_branch_observation.py` serialize only fields that exist in the current repository model, so a later separately authorized live retry can produce either safe success JSON or a safe acquisition-error JSON without crashing in the helper.

The plan preserves:

- EID single-source MVP as the current source policy.
- No-live checkpoint `ac6bbe9` as accepted code-behavior proof for the five failure categories: `not_found`, `unavailable`, `schema_drift`, `identity_mismatch`, and `integrity_error`.
- The prior controlled live command as consumed exactly once.
- The rule that no further live EID/FDR/PDF/network acquisition occurs until after plan review, controller judgment, implementation/review, and a separate explicit live authorization.

## Non-Goals

- Do not run live EID, network, PDF acquisition, FDR acquisition, fallback, curl, DNS, socket, provider, LLM, `analyze`, `checklist`, extractor, golden/readiness, score-loop, release, PR, push or merge actions during Stage A.
- Do not add `identity_status` or `integrity_status` to `AnnualReportSourceMetadata`.
- Do not change production source policy, fallback eligibility, EID single-source semantics, cache semantics, parser behavior, extractor behavior, Service/Host/Agent runtime, provider/runtime defaults, score-loop, quality gate, renderer, snapshot, fixture projection, golden/readiness or release state.
- Do not use Eastmoney, CNINFO, fund-company website/CDN or any non-EID source.
- Do not treat the prior live attempt as accepted live success evidence or live failure-branch proof.
- Do not claim Stage A proves live behavior; Stage A only proves the helper no longer statically references non-existent metadata fields and remains import/compile/lint safe.

## Current Facts

- Current branch at planning preflight: `feat/mvp-llm-incomplete-run-artifacts`.
- Worktree has unrelated untracked residue; this gate must only touch its allowed files.
- Previous plan checkpoint `7ebd06d` authorized exactly one live command: `uv run python scripts/controlled_live_eid_failure_branch_observation.py`.
- Previous live command target was exactly `006597 / 2024`.
- Previous live command was consumed once.
- Previous live command exited `1`.
- Previous live command stdout was empty.
- Previous stderr ended in `AttributeError: 'AnnualReportSourceMetadata' object has no attribute 'identity_status'`.
- The traceback reached `_safe_report_payload(report)` after `repository.load_annual_report()` returned a `report` object, so the accepted controller inference is post-acquisition helper serialization failure.
- This is not accepted live success evidence.
- This is not live failure-branch proof.
- `scripts/controlled_live_eid_failure_branch_observation.py` currently reads:
  - `source_metadata.identity_status`
  - `source_metadata.integrity_status`
- `fund_agent/fund/documents/models.py` currently defines `AnnualReportSourceMetadata` fields including `source`, `source_url`, `fund_code`, `fund_id`, `report_year`, `report_code`, `report_desp`, `report_name`, `upload_info_id`, `upload_info_detail_id`, `table_name`, `report_send_date`, `operation_upload_type`, `corrections_num`, `fallback_used`, `primary_failure_category`, `selected_source`, `source_mode`, `fallback_enabled`, and `discovery_contract_version`.
- `AnnualReportSourceMetadata` does not define `identity_status` or `integrity_status`.
- Accepted no-live checkpoint `ac6bbe9` remains accepted proof for the five modeled EID failure categories.
- Control truth states the next entry point is this planning/control gate and forbids any new live/PDF/FDR/network command before a reviewed plan, controller judgment and separate explicit live authorization.

## Proposed Helper Repair

Repair only the gate-local helper success serializer.

Required implementation decision:

- Remove the two non-existent metadata reads from `_safe_report_payload()`:
  - `"identity_status": source_metadata.identity_status if source_metadata else None`
  - `"integrity_status": source_metadata.integrity_status if source_metadata else None`
- Do not replace them with new production model fields.
- Do not add `identity_status` or `integrity_status` to `AnnualReportSourceMetadata`.
- Keep existing safe scalar fields that exist on the current model:
  - `source`
  - `selected_source`
  - `source_mode`
  - `fallback_enabled`
  - `fallback_used`
  - `primary_failure_category`
  - cache booleans already read from `report.metadata.cache`
- Optionally add `discovery_contract_version` to the helper success payload because it exists on current `AnnualReportSourceMetadata`, is a safe scalar, and can help identify source contract shape. This optional addition must not be used to infer identity or integrity status.
- Keep the helper target constants unchanged:
  - `FUND_CODE = "006597"`
  - `REPORT_YEAR = 2024`
- Keep the repository path unchanged:
  - `FundDocumentRepository.load_annual_report(FUND_CODE, REPORT_YEAR, force_refresh=True)`
- Keep gate-local temporary cache isolation unchanged.
- Keep failure serialization unchanged except for any lint-required mechanical cleanup.

The repair is deliberately not a production metadata/schema repair. Root cause is a helper overclaim of the current model shape, not missing production identity/integrity fields.

## Stage A - No-Live Helper Repair Implementation And Deterministic Validation

### Objective

Repair and validate the helper without live acquisition.

### Required Allowed Files

- `scripts/controlled_live_eid_failure_branch_observation.py`
- `docs/reviews/mvp-controlled-live-eid-helper-repair-and-retry-implementation-evidence-20260611.md`
- `docs/reviews/mvp-controlled-live-eid-helper-repair-and-retry-code-review-ds-20260611.md`
- `docs/reviews/mvp-controlled-live-eid-helper-repair-and-retry-code-review-mimo-20260611.md`
- `docs/reviews/mvp-controlled-live-eid-helper-repair-and-retry-controller-judgment-20260611.md`

### Optional Controller-Decision File

Only if plan review or controller judgment decides a no-live regression test is worth the extra file, allow exactly one narrow test file:

- `tests/scripts/test_controlled_live_eid_failure_branch_observation.py`

The optional test must construct fake report/metadata objects in memory and call `_safe_report_payload()` directly. It must not call `main()`, `_run_observation()`, `FundDocumentRepository`, `AnnualReportPdfAdapter`, `AnnualReportSourceOrchestrator`, `EidAnnualReportSource`, filesystem PDF cache, network, FDR, PDF parsing, fallback, provider, LLM, extractor, `analyze`, `checklist`, score-loop or golden/readiness code.

If the controller does not explicitly accept this optional test file, Stage A remains a one-source-file repair plus evidence/review/judgment artifacts.

### Exact Allowed Source Change

In `scripts/controlled_live_eid_failure_branch_observation.py`:

1. Edit `_safe_report_payload(report)`.
2. Delete the `identity_status` output field.
3. Delete the `integrity_status` output field.
4. Preserve all existing success payload safe scalar fields that refer to current model attributes.
5. Optionally add `"discovery_contract_version": source_metadata.discovery_contract_version if source_metadata else None`.
6. Do not change `_run_observation()` control flow.
7. Do not change the live target row.
8. Do not change exception category mapping.
9. Do not broaden caught exceptions beyond the current helper behavior.
10. Do not add source-policy, fallback-policy or production metadata logic.

### Deterministic Validation Commands

Stage A validation must be no-live only. Allowed commands:

```bash
uv run ruff check scripts/controlled_live_eid_failure_branch_observation.py
uv run python -m py_compile scripts/controlled_live_eid_failure_branch_observation.py
git diff --check -- scripts/controlled_live_eid_failure_branch_observation.py docs/reviews/mvp-controlled-live-eid-helper-repair-and-retry-implementation-evidence-20260611.md
```

If the optional no-live test file is accepted:

```bash
uv run pytest tests/scripts/test_controlled_live_eid_failure_branch_observation.py
git diff --check -- scripts/controlled_live_eid_failure_branch_observation.py tests/scripts/test_controlled_live_eid_failure_branch_observation.py docs/reviews/mvp-controlled-live-eid-helper-repair-and-retry-implementation-evidence-20260611.md
```

Explicitly forbidden in Stage A:

```bash
uv run python scripts/controlled_live_eid_failure_branch_observation.py
```

Reason: executing the helper script calls `_run_observation()`, which constructs `EidAnnualReportSource` and calls `FundDocumentRepository.load_annual_report()` for live acquisition. That belongs only to Stage B after separate explicit live authorization.

### Stage A Review Gates

1. DS plan review of this plan.
2. MiMo plan review of this plan.
3. Controller judgment on plan review findings.
4. Implementation worker applies only the accepted Stage A file changes.
5. Implementation worker writes the Stage A implementation evidence artifact.
6. DS code review of the Stage A diff and evidence.
7. MiMo code review of the Stage A diff and evidence.
8. Controller judgment on code review findings.
9. If accepted and no blocking residual remains, controller may create a local accepted checkpoint for Stage A. No push/PR/release action is authorized by Stage A.

### Stage A Completion Signal

Stage A is complete only when:

- `_safe_report_payload()` no longer reads `identity_status` or `integrity_status`.
- No production model/schema/source-policy/fallback/runtime behavior changed.
- No live helper execution occurred.
- No forbidden commands/actions occurred.
- Required no-live validation commands have recorded results.
- DS and MiMo code reviews are complete.
- Controller judgment accepts or classifies all findings and residuals.

## Stage B - Optional Controlled Live Retry After Separate Authorization

### Entry Criteria

Stage B is not authorized by this plan.

Stage B may begin only after all of the following are true:

- Stage A plan reviews are complete.
- Controller judgment accepts the reviewed plan.
- Stage A implementation and no-live validation are complete.
- Stage A code reviews are complete.
- Controller judgment accepts the Stage A repair and records any residuals.
- The user gives a new explicit live authorization for exactly the Stage B command below.

### Exact Live Command

If later authorized, run exactly one bounded command:

```bash
uv run python scripts/controlled_live_eid_failure_branch_observation.py
```

The command remains bounded by the script constants:

- `FUND_CODE = "006597"`
- `REPORT_YEAR = 2024`

No retry is allowed. If the command exits non-zero, prints empty stdout, times out, or produces helper/runtime/acquisition failure, record that outcome and stop.

### Stage B Non-Expansion Rules

Stage B must not:

- Retry the command.
- Change the target row.
- Add another fund/year.
- Use fallback.
- Use non-EID sources.
- Run `analyze`, `checklist`, extractor, renderer or quality gate.
- Run provider/LLM/endpoint/DNS/curl/socket probes.
- Project fixtures.
- Promote golden/readiness.
- Enter score-loop, release or PR gate.

### Stage B Evidence Expectations

If Stage B is authorized and executed once, the evidence artifact must classify exactly one of:

- `accepted_live_window_no_failure_observed` only if exit code is `0`, stdout contains parseable safe JSON, target is `006597 / 2024`, source policy fields remain EID single-source, and no forbidden action occurred.
- A safe EID/FDR acquisition failure category if the helper returns safe JSON with `status="error"` and a current modeled category.
- A blocked helper/runtime outcome if the command fails before producing safe JSON or fails outside modeled acquisition categories.

Any Stage B result must still preserve `ac6bbe9` as no-live proof for all five modeled failure categories unless a later reviewed controller judgment explicitly changes that evidence status.

## Review Gates

Plan review required before any implementation:

- DS plan review.
- MiMo plan review.
- Controller judgment on all plan findings.

Implementation review required before any live retry authorization:

- DS code review of Stage A helper repair and evidence.
- MiMo code review of Stage A helper repair and evidence.
- Controller judgment on all code review findings.

Live retry authorization required after implementation review:

- Separate explicit user authorization for Stage B.
- Controller self-check that the command is exactly the single bounded command for `006597 / 2024`.
- Controller self-check that no retry/additional row/fallback/non-EID/provider/LLM/extractor/analyze/checklist/golden/readiness/score-loop/release/PR action is included.

## Stop Conditions

Stop before implementation if:

- DS or MiMo plan review finds a blocking issue.
- The plan attempts to change production metadata, fallback policy, source policy, runtime behavior, or any file outside Stage A allowed files.
- The controller cannot classify unrelated dirty workspace files safely.

Stop during Stage A implementation if:

- A required change would touch `fund_agent/fund/documents/models.py` or any production source/test/runtime file outside the allowed list.
- The helper repair cannot be made by removing/replacing non-existent metadata reads.
- Validation requires executing `scripts/controlled_live_eid_failure_branch_observation.py`.
- Validation attempts live/network/FDR/PDF/provider/LLM/extractor/analyze/checklist/golden/readiness/score-loop behavior.
- No-live validation fails and the failure is not purely artifact formatting.

Stop before Stage B if:

- Stage A implementation is not accepted by controller judgment.
- Any accepted code review finding remains unresolved.
- The user has not given a new explicit live authorization.
- The proposed live command differs from `uv run python scripts/controlled_live_eid_failure_branch_observation.py`.

Stop during Stage B if:

- The one live command completes with any result.
- The command exits non-zero.
- stdout is empty or unparsable.
- The helper crashes.
- Any fallback/non-EID/provider/LLM/extractor/analyze/checklist/golden/readiness/score-loop/release/PR action is requested or observed.

## Residuals

- Live natural occurrence of the five modeled EID failure categories remains unproven until a separately authorized live observation produces safe evidence.
- `ac6bbe9` remains the accepted code-behavior proof for the five modeled categories regardless of Stage A.
- The previous live attempt remains consumed and cannot be reused as authorization.
- If Stage B produces success JSON, it proves only that the controlled window did not observe a failure for `006597 / 2024`; it still does not prove natural occurrence of failure branches.
- If Stage B produces another helper/runtime blocker, future work must classify that blocker in a new reviewed gate before any retry.
- Non-EID routes remain deferred candidates/historical evidence routes only.
- Any design/control wording that implies current `AnnualReportSourceMetadata` has `identity_status` or `integrity_status` should be treated as stale relative to code and reviewed evidence unless a separate docs-sync gate explicitly reconciles it; this helper repair must not resolve that inconsistency by adding production fields.

## Completion Report Format

Stage A implementation worker completion report:

```text
Gate: controlled live EID helper repair and retry - Stage A no-live helper repair
Role: implementation worker
Self-check: pass | blocked - <reason>
Changed files:
- <path>
Implemented changes:
- Removed non-existent metadata reads: identity_status / integrity_status
- Preserved current EID single-source safe scalar fields
- Optional discovery_contract_version: yes | no
Validation:
- <command>: pass | fail | not run - <reason>
Live execution:
- none; helper script was not executed
Forbidden actions check:
- no live EID/FDR/PDF/network/fallback/non-EID/provider/LLM/analyze/checklist/extractor/golden/readiness/score-loop/release/PR actions
Residuals:
- <classified residuals or none>
Artifact:
- docs/reviews/mvp-controlled-live-eid-helper-repair-and-retry-implementation-evidence-20260611.md
```

Stage A reviewer completion report:

```text
Gate: controlled live EID helper repair and retry - Stage A code review
Role: DS | MiMo reviewer
Reviewed target:
- scripts/controlled_live_eid_failure_branch_observation.py
- implementation evidence artifact
Conclusion: PASS | PASS_WITH_FINDINGS | BLOCKED
Findings:
- <finding id/status/severity/summary or none>
No-live verification:
- no helper execution observed
Residuals:
- <classified residuals or none>
Artifact:
- <review artifact path>
```

Stage B live evidence worker completion report, only if separately authorized:

```text
Gate: controlled live EID helper repair and retry - Stage B controlled live retry
Role: evidence worker
Self-check: pass | blocked - <reason>
Authorization:
- explicit live authorization source: <message/artifact>
Command executed:
- uv run python scripts/controlled_live_eid_failure_branch_observation.py
Execution count:
- 1
Target:
- 006597 / 2024
Result:
- exit_code=<code>
- stdout=<safe summary: parseable JSON | empty | unparsable>
- classification=<accepted_live_window_no_failure_observed | safe_acquisition_error | blocked_helper_or_runtime_outcome>
Forbidden actions check:
- no retry/additional row/fallback/non-EID/provider/LLM/analyze/checklist/extractor/golden/readiness/score-loop/release/PR actions
Residuals:
- <classified residuals>
Artifact:
- <Stage B evidence artifact path>
```

## Blocking Questions For Controller

None for Stage A default scope.

The optional no-live regression test file is a controller decision, not a blocking question. Default route is no test file and validation by ruff, py_compile and diff check only.
