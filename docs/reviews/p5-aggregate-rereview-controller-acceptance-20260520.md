# P5 Aggregate Re-review Controller Acceptance - 2026-05-20

## Verdict

P5 aggregate re-review PASS.

Both targeted reviewers confirmed their accepted findings were fixed. P5 can move to acceptance / ready-to-open-draft-PR reconciliation.

Next gate: `P5 acceptance / ready-to-open-draft-PR reconciliation`.

## Re-review Inputs

- Original aggregate finding judgment: `docs/reviews/p5-aggregate-deepreview-controller-judgment-20260520.md`
- AgentCodex targeted re-review: P5-S1~S4 fixes
- AgentDS targeted re-review: P5-S5~S7 fixes
- Controller verification after fixes

## Re-review Results

### AgentCodex

Status: PASS.

Confirmed closed:

- `block` quality gate policy no longer succeeds when gate does not run.
- Explicit non-default golden answer path typo no longer silently disables correctness.
- New snapshot `comparable_values` missing whitelisted subfield now enters mismatch.

Reviewer note:

- The not-run failure under block policy is currently a normal `ValueError`, not `QualityGateBlockedError`. Controller accepts this for P5 because the core contract is “must not successfully output report when block gate did not run.” A structured not-run exception can be a future UX refinement.

Reviewer targeted verification:

- `4 passed`

### AgentDS

Status: PASS.

Confirmed closed:

- `share_change` no longer uses A-class fallback; A/D table with `fund_code=019264` now returns missing.
- `selected_funds_smoke` now records `quality_gate_status` separately from process status and exposes it in JSONL/summary.

Reviewer targeted verification:

- `16 passed`

## Controller Verification

- `.venv/bin/python -m pytest tests/fund/extractors/test_holdings_share_change.py tests/services/test_fund_analysis_service.py tests/fund/test_extraction_score.py tests/scripts/test_selected_funds_smoke.py tests/ui/test_cli.py -q` -> `53 passed`
- `.venv/bin/python -m pytest tests/ -q` -> `206 passed`
- `.venv/bin/python -m ruff check .` -> passed
- `git diff --check` -> passed

## Remaining Risks / Owners

| Risk | Status | Owner |
|---|---|---|
| `016492` duplicate in `docs/code_20260519.csv` | still open | human/user App source confirmation |
| Live PDF/network smoke | opt-in only | operator/controller when explicitly run |
| Thermometer-to-valuation mapping | intentionally not implemented | future Capability/checklist design |
| Not-run block UX uses `ValueError` rather than structured blocked error | accepted residual UX issue | future Service/CLI polish if needed |

## Gate Decision

P5 aggregate re-review is accepted.

Current gate advances to `P5 acceptance / ready-to-open-draft-PR reconciliation`.
