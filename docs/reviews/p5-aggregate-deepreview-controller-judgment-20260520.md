# P5 Aggregate Deepreview Controller Judgment - 2026-05-20

## Verdict

P5 aggregate deepreview initially found blocking issues. Controller accepted the substantive findings and applied fixes.

Current status: PASS after fix.

Next gate: `P5 aggregate re-review / acceptance`.

## Review Inputs

- AgentCodex review scope: P5-S1~S4 quality gate integration, score schema, failed_funds, comparable_values, Service/CLI parameter chain.
- AgentDS review scope: P5-S5~S7 share_change, thermometer Service/CLI, selected_funds_smoke, docs/tests.
- Controller local review: same aggregate surface plus test and documentation reconciliation.

## Accepted Findings And Fixes

### F1 - `block` quality gate policy could succeed when gate did not run

Source: AgentCodex.

Status: accepted / fixed.

Evidence:

- `FundAnalysisService._run_quality_gate_if_enabled()` can return `(None, not_run_reason)` when the quality source CSV is missing, invalid, or does not contain the fund.
- Before fix, `analyze()` only raised on `quality_gate_result.status == block`, so default `block` policy could still output a report when gate was not run.

Fix:

- `FundAnalysisService.analyze()` now treats `quality_gate_policy="block"` plus `quality_gate_result is None` as a failure: `ValueError("质量 gate 未运行：...")`.
- Added/updated tests:
  - block policy fails when fund is absent from quality CSV;
  - warn policy can still keep the report and not-run reason.
- P3 CLI matrix now explicitly uses `--quality-gate-policy off`, because that matrix verifies report rendering and audit path, not P5 gate behavior.

### F2 - Explicit golden answer path typo silently disabled correctness

Source: AgentCodex.

Status: accepted / fixed.

Evidence:

- `_resolve_golden_answer_path()` returned `None` for any missing path.
- This made an explicitly wrong `--quality-gate-golden-answer-path` behave like “correctness unavailable”.

Fix:

- Missing default golden answer path still degrades to unavailable for fresh/local setups.
- Missing non-default explicit path now raises `FileNotFoundError`.
- Added Service test for explicit missing golden answer path.

### F3 - Whitelisted subfield missing under present parent field became unavailable

Source: AgentCodex.

Status: accepted / fixed.

Evidence:

- New snapshot records with `comparable_values` could omit a whitelisted child field while parent `value_present=True`.
- Before fix, `_snapshot_actual_index()` only wrote `None` for all whitelist children when the entire parent record had `value_present=False`.

Fix:

- For any new snapshot record containing `comparable_values`, `_snapshot_actual_index()` now initializes all whitelisted subfields for that field as `None`, then overwrites present comparable values.
- Added correctness test: parent field present, whitelisted `basic_identity.fund_name` missing, golden expects value -> mismatch.

### F4 - `share_change` A-class fallback could misread non-A share classes

Source: AgentDS.

Status: accepted / fixed.

Evidence:

- Existing fallback selected the only `A类` column when no exact fund-code header existed.
- The selected pool contains non-A classes such as B/D/E. A/D table for a D-code fund would misselect A.

Fix:

- Removed A-class fallback.
- `share_change` now selects only:
  - a single value column; or
  - a value column whose header contains the exact current fund code.
- Ambiguous multi-share-class tables return `missing`.
- Added non-A regression test using fund code `019264` and A/D table.
- Updated Fund README and tests README.

### F5 - Smoke PASS could hide quality gate block under warn policy

Source: AgentDS.

Status: accepted / fixed.

Evidence:

- `selected_funds_smoke.py` intentionally passes `--quality-gate-policy warn` to observe real PDF/network/rendering path.
- Before fix, `SmokeRecord.status` only reflected process return code, so a report with `quality_gate_status: block` could appear as PASS.

Fix:

- Smoke records now include `quality_gate_status` parsed from stderr.
- Summary table now separates process status from Quality Gate status.
- README documents this distinction.
- Added smoke record/status extraction tests.

## Rejected / Deferred Findings

None.

## Verification After Fix

- `.venv/bin/python -m pytest tests/fund/extractors/test_holdings_share_change.py tests/services/test_fund_analysis_service.py tests/fund/test_extraction_score.py tests/scripts/test_selected_funds_smoke.py tests/ui/test_cli.py -q` -> `53 passed`
- `.venv/bin/python -m pytest tests/ -q` -> `206 passed`
- `.venv/bin/python -m ruff check .` -> passed
- `git diff --check` -> passed

## Residual Risks

- P5-S6 duplicate `016492` remains human-owned. It is not auto-fixed.
- Live PDF/network smoke remains opt-in and environment-sensitive.
- Thermometer-to-`valuation_state` mapping remains intentionally unimplemented until Capability/checklist defines a same-source rule.

## Gate Decision

P5 aggregate deepreview findings are fixed.

Current gate advances to `P5 aggregate re-review / acceptance`.
