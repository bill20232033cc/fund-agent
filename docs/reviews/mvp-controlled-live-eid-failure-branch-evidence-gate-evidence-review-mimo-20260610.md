# Controlled Live EID Failure-Branch Evidence Gate Evidence Review MiMo - 2026-06-10

## Verdict

PASS_WITH_FINDINGS

## Review Scope

Evidence artifact: `docs/reviews/mvp-controlled-live-eid-failure-branch-evidence-gate-evidence-20260610.md`
Helper script: `scripts/controlled_live_eid_failure_branch_observation.py`
Plan: `docs/reviews/mvp-controlled-live-eid-failure-branch-evidence-gate-plan-20260610.md`
Controller judgment: `docs/reviews/mvp-controlled-live-eid-failure-branch-evidence-gate-plan-controller-judgment-20260610.md`
No-live checkpoint: `ac6bbe9` (`docs/reviews/mvp-eid-failure-branch-evidence-20260610.md`)

Role: evidence reviewer for AgentMiMo. Review only. No live execution, no source/test/runtime modification, no stage/commit/push/PR.

## Must-Check Results

### 1. One live command consumed, no retry allowed

**PASS.** Evidence states: "The command was executed exactly once. It was not retried, expanded to additional rows, or replaced with an inline command." Controller judgment authorized exactly one command (`uv run python scripts/controlled_live_eid_failure_branch_observation.py`) for `006597 / 2024`. Evidence "Non-Events" section confirms no retry or second live EID attempt occurred.

### 2. stdout empty and exit_code 1 treated as no accepted safe JSON evidence

**PASS.** Evidence records `exit_code=1` and `stdout=empty`. Classification is `blocked_helper_serialization_error_after_acquisition`, correctly identifying this as a helper defect rather than an accepted live outcome. Evidence explicitly states: "This is direct evidence of a gate-local helper serialization defect, not accepted live success evidence and not live failure-branch proof."

### 3. Post-acquisition inference phrased as inference from traceback, not accepted success proof

**PASS.** Evidence states: "The live command reached the post-acquisition serialization path: `_run_observation()` returned from `repository.load_annual_report('006597', 2024, force_refresh=True)` with a `report` object and then failed while converting repo metadata to safe JSON scalars." The phrasing "reached the post-acquisition serialization path" is qualified as inference from the traceback structure. The script's `_safe_report_payload()` is called after the `try/except` block around `load_annual_report()`, so the `AttributeError` escaping the `try` block confirms `load_annual_report()` returned before the crash. However, see Finding F1 below.

### 4. No-live checkpoint ac6bbe9 remains accepted proof for five failure categories

**PASS.** Evidence states: "Accepted no-live checkpoint `ac6bbe9` remains the accepted code-behavior proof for all five EID failure categories: `not_found`, `unavailable`, `schema_drift`, `identity_mismatch`, and `integrity_error`." Verified against `ac6bbe9` artifact: it proves all five categories using `httpx.MockTransport` and `_FakeAnnualReportSource` with zero live network/PDF/repository calls.

### 5. Future helper repair and retry require new reviewed plan and separate live authorization

**PASS.** Evidence states: "Any helper repair and live retry requires a new reviewed plan and separate explicit authorization." Residual section states: "`controlled_live_eid_helper_repair_and_retry` remains deferred. The minimum future scope is to remove or replace the two non-existent metadata reads in the gate-local helper, re-review the repair, and request a separate controlled live retry authorization before another network/FDR acquisition command is run."

### 6. No forbidden fallback/provider/LLM/non-EID/source-policy action endorsed

**PASS.** Evidence "Non-Events" section comprehensively lists all forbidden actions that did not occur: retry, additional rows, non-EID sources, fallback invocation, provider/LLM/endpoint/DNS/curl/socket probe, extractor/deterministic analyze/checklist/renderer/quality gate, Service/Host/Agent runtime expansion, fixture projection, golden/readiness promotion, score-loop, release/PR action/push/merge. The classification and residual sections do not endorse any forbidden action.

## Findings

### F1 - Low - Inference precision for post-acquisition claim

**Severity:** low
**File/path:** `docs/reviews/mvp-controlled-live-eid-failure-branch-evidence-gate-evidence-20260610.md`, "Execution Result" and "Classification" sections
**Issue:** The evidence infers "reached the post-acquisition serialization path" from the traceback structure. The inference is technically correct because `_safe_report_payload()` is called after the `try/except` block around `load_annual_report()`, so the `AttributeError` escaping the `try` block proves `load_annual_report()` returned a `report` object. However, the evidence does not explicitly state this inference chain (that the exception escaping the `try/except` is the proof of successful return). A reader unfamiliar with the script structure might not immediately see why the inference is sound.
**Required disposition:** Acceptable as-is for a gate-local helper serialization defect classification. The inference is correct and the classification is appropriately cautious. No mandatory change required, but adding one sentence explaining the inference basis ("The `AttributeError` escaped the `try/except` around `load_annual_report()`, proving the repository call returned before the serialization helper crashed") would improve clarity.

### F2 - Low - Helper script self-identifies metadata shape mismatch

**Severity:** low
**File/path:** `scripts/controlled_live_eid_failure_branch_observation.py`, lines 97-98
**Issue:** The helper script reads `source_metadata.identity_status` and `source_metadata.integrity_status` (lines 97-98), but `AnnualReportSourceMetadata` does not define these fields. The evidence correctly identifies this: "Repo models currently define `AnnualReportSourceMetadata` without `identity_status` or `integrity_status` fields." This is a gate-local helper defect, not a production code defect. The residual correctly routes this to `controlled_live_eid_helper_repair_and_retry`.
**Required disposition:** No change to production code or evidence artifact required. The residual correctly defers helper repair to a future reviewed plan.

### F3 - Informational - Evidence artifact completeness check

**Severity:** informational
**File/path:** `docs/reviews/mvp-controlled-live-eid-failure-branch-evidence-gate-evidence-20260610.md`
**Issue:** The evidence artifact covers all required elements from the plan: exact command, exit code, safe stderr summary, exception type and mapped category, explicit no-fallback/no-non-EID/no-provider/no-LLM statement, explicit statement that this is not live failure-branch proof, no-live checkpoint preservation, residual wording, and post-run validation. The plan's "Evidence Artifact" section listed `identity_status` and `integrity_status` as expected scalar fields for a success outcome; since the outcome was a failure, these fields are not applicable and their absence is correct.
**Required disposition:** None.

## Residuals

- `controlled_live_eid_helper_repair_and_retry` remains deferred: remove or replace `identity_status` and `integrity_status` reads in gate-local helper, re-review repair, request separate controlled live retry authorization.
- No-live checkpoint `ac6bbe9` remains accepted proof for `not_found`, `unavailable`, `schema_drift`, `identity_mismatch`, `integrity_error`.
- Live `schema_drift`, `identity_mismatch`, `integrity_error`, `not_found` and `unavailable` are not guaranteed to occur under controlled conditions.
- Eastmoney, CNINFO, fund-company official website/CDN and other non-EID routes remain forbidden in this gate.
- This gate consumed its single authorized live attempt; no additional live command is authorized without a new reviewed plan and controller judgment.

## No live execution performed

yes
