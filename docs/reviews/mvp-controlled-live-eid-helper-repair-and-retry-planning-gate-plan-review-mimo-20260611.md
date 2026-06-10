# Controlled Live EID Helper Repair And Retry Planning Gate Plan Review MiMo - 2026-06-11

Verdict: PASS_WITH_FINDINGS

## Review Scope

Plan file: `docs/reviews/mvp-controlled-live-eid-helper-repair-and-retry-planning-gate-plan-20260611.md`

Review question: Is the plan safe, handoff-ready and code-generation-ready for Stage A no-live helper repair, while preserving separate explicit authorization for Stage B live retry?

## Checked Items

### 1. Does it forbid direct live rerun in Stage A?

PASS. The plan explicitly lists `uv run python scripts/controlled_live_eid_failure_branch_observation.py` as forbidden in Stage A validation commands (line 136-138). The rationale is sound: the helper script constructs `EidAnnualReportSource` and calls `FundDocumentRepository.load_annual_report()` for live acquisition, which belongs only to Stage B. Stage A validation is limited to `ruff check`, `py_compile` and `git diff --check`.

### 2. Does it keep repair limited to removing/replacing non-existent helper metadata reads?

PASS. The plan specifies exactly two deletions from `_safe_report_payload()`:
- `"identity_status": source_metadata.identity_status if source_metadata else None`
- `"integrity_status": source_metadata.integrity_status if source_metadata else None`

One optional addition (`discovery_contract_version`) is safe: the field exists on current `AnnualReportSourceMetadata` at `models.py:71` and is a scalar. The plan explicitly prohibits adding `identity_status` or `integrity_status` to the production model, which is the correct root-cause disposition: the helper overclaimed the model shape, not the model missing fields.

### 3. Does it avoid adding identity_status/integrity_status to production metadata?

PASS. The plan's Non-Goals section (line 21) and Stage A rules (line 57) both explicitly forbid adding these fields to `AnnualReportSourceMetadata`. This preserves the current model contract.

### 4. Does it preserve EID single-source MVP and ac6bbe9 no-live proof?

PASS. Multiple plan sections (lines 13, 44, 218, 276) explicitly preserve `ac6bbe9` as accepted code-behavior proof for the five modeled failure categories. EID single-source MVP is preserved by not changing source policy, fallback eligibility, or production behavior. Stage B non-expansion rules (lines 197-209) forbid non-EID sources and fallback.

### 5. Are validation commands no-live and sufficient?

PASS. The three validation commands are:
- `uv run ruff check scripts/controlled_live_eid_failure_branch_observation.py` — lint
- `uv run python -m py_compile scripts/controlled_live_eid_failure_branch_observation.py` — compile
- `git diff --check -- scripts/...` — whitespace/formatting

These are sufficient to confirm the repair is syntactically valid, lint-clean and does not introduce diff artifacts. The plan correctly reasons that ruff + py_compile catch the exact class of error that caused the prior failure (accessing non-existent attributes). A live execution is not needed to validate removal of non-existent field reads.

### 6. Are allowed files and stop conditions precise enough?

PASS. Allowed files are enumerated as exactly 5 paths (1 source + 4 artifacts). Stop conditions are enumerated in three stages (before implementation, during Stage A, before Stage B, during Stage B) with explicit trigger conditions. The stop condition "A required change would touch `fund_agent/fund/documents/models.py` or any production source/test/runtime file outside the allowed list" (line 251) is the critical guardrail.

### 7. Is optional test scope acceptable or should it be required/rejected?

FINDING F1 (low/informational). See below.

## Findings

| ID | Severity | Issue | Required Disposition |
|----|----------|-------|---------------------|
| F1 | low | Optional test scope is acceptable but the default "no test" route is weaker than necessary. The helper was broken once by referencing non-existent fields; a narrow unit test calling `_safe_report_payload()` with a fake `AnnualReportSourceMetadata` would catch similar regressions without any live dependency. The plan makes this a controller decision (line 99), which is fine, but the reviewer recommends accepting the optional test file. | Controller decision; recommendation is to accept the optional test. |
| F2 | low/informational | The plan's Residuals section (line 279) correctly notes that `docs/design.md` line 678 claims `AnnualReportSourceMetadata` supports "identity status 和 integrity status" while `models.py` does not define these fields. This is a docs/code inconsistency that predates this gate. The plan correctly scopes it out and defers it to a docs-sync gate. No action required in this gate. | Acknowledged; deferred to future docs-sync gate. |

## Residuals

| Residual | Next handling |
|----------|---------------|
| `docs/design.md` line 678 claims `AnnualReportSourceMetadata` supports `identity_status` / `integrity_status` but `models.py` does not define them. | Future docs-sync gate should reconcile design.md to match current model or, if a future gate adds the fields, update both. |
| Live natural occurrence of the five modeled EID failure categories remains unobserved. | After Stage B (if separately authorized), classify result; until then, `ac6bbe9` remains accepted code-behavior proof. |
| Non-EID routes remain deferred candidates. | Not in scope for this gate. |

## No live execution performed

yes

## Evidence

- Plan: `docs/reviews/mvp-controlled-live-eid-helper-repair-and-retry-planning-gate-plan-20260611.md`
- Prior controller judgment: `docs/reviews/mvp-controlled-live-eid-failure-branch-evidence-gate-controller-judgment-20260610.md`
- Prior observation script: `scripts/controlled_live_eid_failure_branch_observation.py` (lines 97-98 read `identity_status` / `integrity_status`)
- Production model: `fund_agent/fund/documents/models.py` (lines 26-71, `AnnualReportSourceMetadata` without `identity_status` / `integrity_status`)
- Design doc claim: `docs/design.md` line 678 (claims fields exist)
