# Evidence Confirm Scoring V2 PR Review Fix Evidence

## Scope

- Gate: Evidence Confirm Scoring V2 PR Review Fix Gate
- Role: AgentCodex fix worker
- Branch: `evidence-confirm-anchor-audit-score`
- Accepted findings fixed:
  - `docs/reviews/pr-39-review-20260622-104743.md` finding 001
  - `docs/reviews/pr-39-review-20260622-104015.md` findings 001/002/003
- Changed files:
  - `fund_agent/fund/evidence_confirm.py`
  - `tests/fund/test_evidence_confirm.py`
  - `tests/README.md`
  - `docs/reviews/evidence-confirm-scoring-v2-pr-review-fix-evidence-20260622.md`

## Fix Summary

- V1 `confirm_chapter_evidence()` / `confirm_projection_evidence()` now fail closed when an available non-derived fact declares any dangling `evidence_anchor_id`, even if another same-fact anchor has valid proven reference support.
- V1 dangling-anchor failure returns E3 blocking, score `0`, no matched anchors, and issue `anchor_id` set to the dangling id.
- V2 all-dangling path now emits concrete dangling-anchor E3 issue(s) instead of the previous generic missing-anchor issue with `anchor_id=None`.
- V2 mixed dangling behavior remains fail/score `0`; all-dangling and mixed paths now share concrete anchor-id reporting semantics.
- Aggregate score tests now lock exact value-match cap `40` and E3 blocking aggregate cap `0`.

## Test Coverage Added

- `test_partial_dangling_anchor_fails_closed_even_with_valid_v1_proof`
- `test_projection_partial_dangling_anchor_fails_closed_with_v1_issue_anchor`
- `test_v2_all_dangling_anchor_reports_concrete_anchor_ids`
- `test_v2_aggregate_score_e3_blocking_fact_caps_score_at_zero`
- Strengthened `test_v2_aggregate_score_one_blocking_fact_cannot_report_pass_like_score` from `< 70` to `== 40`.

## Validation

- `uv run pytest tests/fund/test_evidence_confirm.py -q`
  - Result: `47 passed in 0.52s`
- `uv run ruff check fund_agent/fund/evidence_confirm.py tests/fund/test_evidence_confirm.py`
  - Result: `All checks passed!`
- `git diff --check -- fund_agent/fund/evidence_confirm.py tests/fund/test_evidence_confirm.py tests/README.md`
  - Result: passed with no output
- `git diff --check --no-index /dev/null docs/reviews/evidence-confirm-scoring-v2-pr-review-fix-evidence-20260622.md`
  - Result: no whitespace-error output; command exits non-zero because the new file differs from `/dev/null`

## Finding Status

- `pr-39-review-20260622-104743.md` finding 001: fixed in current gate.
- `pr-39-review-20260622-104015.md` finding 001: fixed in current gate.
- `pr-39-review-20260622-104015.md` finding 002: fixed in current gate.
- `pr-39-review-20260622-104015.md` finding 003: fixed in current gate.

## Residual Risks

- Non-accepted PR title finding: deferred by user instruction; no PR metadata mutation performed.
- `implementation-control` / `current-startup-packet` scope finding: deferred by user instruction; no control-doc mutation performed.
- DS future-only hard_gate/score coupling: deferred by user instruction; no refactor performed.
- Whole-repo behavior outside Evidence Confirm V1/V2 no-live helper paths: not reviewed in this fix gate.

## Completion Status

- Implementation, tests, docs sync, and fix evidence artifact are complete for the accepted findings above.
- No `git add`, commit, push, PR mutation, or review artifact edit was performed.
