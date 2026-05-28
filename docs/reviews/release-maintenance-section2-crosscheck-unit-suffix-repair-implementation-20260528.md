# Section2 Crosscheck Unit Suffix Repair Implementation

> Date: 2026-05-28
> Gate: implementation
> Work unit: section2 crosscheck unit suffix repair gate
> Role: implementation worker, not controller
> Status: implementation complete; awaiting code review/controller disposition

## Approved Plan

- Plan: `docs/reviews/release-maintenance-section2-crosscheck-unit-suffix-repair-plan-20260528.md`
- Scope followed: only repair terminal `份` unit suffix parsing for §2 profile ending-share cells, with fail-closed behavior preserved.

## Dirty Baseline Note

Before implementation:

- Branch: `codex/local-reconciliation`
- Dirty baseline already contained uncommitted modifications in:
  - `fund_agent/fund/extractors/bond_risk_evidence.py`
  - `tests/fund/extractors/test_bond_risk_evidence.py`
- Untracked prior review/control artifacts were present under `docs/reviews/`, plus `--help` and `docs/tmux-agent-memory-store.md`.
- I did not revert, stage, commit, push, create PR, merge, or close out any gate.

## Changed Files

- `fund_agent/fund/extractors/bond_risk_evidence.py`
- `tests/fund/extractors/test_bond_risk_evidence.py`
- `docs/reviews/release-maintenance-section2-crosscheck-unit-suffix-repair-implementation-20260528.md`

## Code Changes

- Added `_DECIMAL_UNIT_SUFFIXES: Final[tuple[str, ...]] = ("份",)` near decimal parsing constants.
- Updated `_parse_plain_decimal()` so that, after compacting text and removing commas, it strips only a known terminal suffix from `_DECIMAL_UNIT_SUFFIXES` before `Decimal(normalized)`.
- Kept fail-closed parsing semantics:
  - No arbitrary non-numeric character deletion.
  - `%` remains rejected.
  - dash-as-zero behavior remains unchanged.
  - values such as `N/A份` still return `None`.

## Test Changes

- Added `test_redemption_share_pressure_aligns_real_profile_unit_suffix_newline_values`.
  - Uses real-shaped §2 profile ending-share cells such as `5,711,224,267\n.09份`.
  - Verifies unlabeled §10 alignment passes §2 cross-check and `redemption_share_pressure` is accepted.
- Added `test_redemption_share_pressure_keeps_invalid_unit_suffix_value_fail_closed`.
  - Directly verifies `_parse_share_decimal("N/A份") is None`.
  - Verifies invalid §2 cross-check values still fail closed with `share_class_ending_cross_check_missing`.
- Existing clean numeric fixture test still passes:
  - `test_redemption_share_pressure_aligns_real_unlabeled_section_ten_by_section_two_order`.
- Existing mismatch and missing fail-closed tests remain unchanged and passed:
  - `test_redemption_share_pressure_fails_closed_when_unlabeled_cross_check_missing`
  - `test_redemption_share_pressure_fails_closed_when_unlabeled_cross_check_mismatch`

## Validation Results

```bash
uv run ruff check fund_agent/fund/extractors/bond_risk_evidence.py tests/fund/extractors/test_bond_risk_evidence.py
```

Result: passed (`All checks passed!`)

```bash
uv run pytest tests/fund/extractors/test_bond_risk_evidence.py -q
```

Result: passed (`58 passed in 0.76s`)

## Docs Decision

- No README or design/control doc update made.
- Reason: this implementation only broadens an internal parser to accept the existing disclosed unit suffix `份` in §2 profile ending-share cells. It does not change public contract, schema, quality gate semantics, score policy, CLI usage, architecture boundaries, or template chapter structure.

## Residual Risks

- Real 006597/2024 end-to-end extraction snapshot was outside this worker's required validation commands and was not run in this pass.
- Only `份` is whitelisted. Other unit suffixes remain fail-closed until separately investigated and approved.
- The workspace still contains unrelated pre-existing dirty/untracked files from prior gates; this implementation did not classify or dispose of them.

## Stop Status

- Implementation scope complete.
- Required validation passed.
- No commit/push/PR/merge/closeout performed.
- Ready to return to controller for code review gate.
