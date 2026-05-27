# Bond Risk Evidence Extractor / Anchor Hardening Slice 1 Fix

> Date: 2026-05-27
> Role: fix worker
> Gate: Slice 1 fix for `bond risk evidence extractor / anchor hardening design gate`
> Scope: controller-accepted Slice 1 findings only

## Scope Guard

- Workflow/skill command: not run.
- Review: not performed.
- Git staging/commit/push/PR/merge/golden promotion: not performed.
- Deferred Slice 5 item `extraction_score.py` constant drift: not changed.

## Per-Finding Status

| Finding | Controller Decision | Status | Fix |
|---|---|---|---|
| DS Finding 2 / MiMo F-4 equivalent: `_validate_bond_risk_group_anchor_refs` reparses anchor IDs with direct `split(":")[3]` | Accepted for Slice 1 | Fixed | `_validate_bond_risk_group_anchor_refs` now receives `fund_code` and `report_year` and reuses `_parse_bond_risk_anchor_id()` for referenced anchors. |
| Focused validator edge-path tests | Accepted for Slice 1 | Fixed | Added tests for `weak_group_ids` mismatch, `ambiguous_group_ids` mismatch, cross-group anchor rejection, malformed/wrong anchor IDs, duplicate group ID, invalid status, and invalid strength. |
| Constant drift between `models.py` and `extraction_score.py` | Deferred to Slice 5 | Deferred | No edit made to `fund_agent/fund/extraction_score.py`. |
| Cosmetic final redundant return | Optional only if touched naturally | Not changed | Left unchanged to avoid style churn. |

## Changed Files

- `fund_agent/fund/extractors/models.py`
- `tests/fund/extractors/test_bond_risk_evidence.py`
- `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-slice1-fix-20260527.md`

## Validation Results

| Command | Result |
|---|---|
| `uv run pytest tests/fund/extractors/test_bond_risk_evidence.py -q` | Pass: `15 passed in 0.71s` |
| `uv run ruff check fund_agent/fund/extractors/models.py tests/fund/extractors/test_bond_risk_evidence.py` | Pass: `All checks passed!` |

## Residual Risk Classification

- Classification: Low.
- Remaining risk: Slice 5 still owns constant drift between `models.py` and `extraction_score.py`.
- Behavioral note: duplicate group IDs now produce the more specific duplicate-ID error before the required-set mismatch error; this keeps validation fail-closed and improves error specificity.
- No extractor, snapshot, score, README, design, control-doc, baseline, or golden promotion surface was changed.

## Self-Check

- Self-check: pass.
