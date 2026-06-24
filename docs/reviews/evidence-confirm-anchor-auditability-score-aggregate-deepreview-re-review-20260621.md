# Evidence Confirm Anchor Auditability Score Aggregate Deepreview Re-review - 2026-06-21

## Gate

- Work unit: `Evidence Confirm / anchor auditability scoring phase 1`
- Branch: `evidence-confirm-anchor-audit-score`
- Scope: targeted re-review after `docs/reviews/evidence-confirm-anchor-auditability-score-aggregate-deepreview-fix-evidence-20260621.md`

## Inputs

- Aggregate reviews:
  - `docs/reviews/code-review-20260621-153037.md`
  - `docs/reviews/code-review-20260621-153217.md`
  - `docs/reviews/code-review-20260621-153307.md`
- Aggregate fix evidence:
  - `docs/reviews/evidence-confirm-anchor-auditability-score-aggregate-deepreview-fix-evidence-20260621.md`
- Modified files after slice commit:
  - `fund_agent/fund/evidence_confirm.py`
  - `tests/fund/test_evidence_confirm.py`
  - `tests/README.md`

## Re-review Summary

### AgentMiMo

- Target: five findings from `docs/reviews/code-review-20260621-153307.md`
- Result:
  - Finding 1 numeric substring FP/FN: fixed.
  - Finding 2 reviewed_note current dead code: deferred with future reviewed-note anchor production owner.
  - Finding 3 derived_calculation precision skip: deferred with future derived-calculation Evidence Confirm owner.
  - Finding 4 mixed aggregation untested: fixed.
  - Finding 5 report_year=0 silent skip: deferred with future downstream adoption owner.
  - No new blocker.

### AgentDS

- Target: artifact completeness, validation evidence and residual classification after aggregate fix.
- Result:
  - Numeric token fix verified.
  - Mixed aggregation test verified.
  - Deferred items have owner and reason.
  - Fix evidence artifact structure complete.
  - 20 focused tests, ruff and adjacent tests verified.
  - No new defect or regression.

### AgentCodex

- Target: architecture boundary and docs overclaim after numeric token fix and tests README update.
- Result:
  - PASS.
  - Numeric token fix is local to `fund_agent/fund/evidence_confirm.py`.
  - No Service/UI/Host/renderer/quality-gate/readiness integration introduced.
  - `tests/README.md` only describes numeric token and mixed status coverage.
  - Aggregate fix evidence matches code and tests.
  - No edit/stage/commit/push performed by reviewer.

## Final Finding Status

| Finding | Decision | Final status |
| --- | --- | --- |
| AgentMiMo 1 token substring matching false positive / false negative | accepted | 已修复 |
| AgentMiMo 2 reviewed_note proof kind currently unreachable | deferred-with-owner | 已分类 |
| AgentMiMo 3 derived_calculation precision check skipped | deferred-with-owner | 已分类 |
| AgentMiMo 4 mixed status aggregation untested | accepted | 已修复 |
| AgentMiMo 5 report_year=0 skips report-year check | deferred-with-owner | 已分类 |

## Validation

Latest controller validation before accepted deepreview commit:

```bash
uv run pytest tests/fund/test_evidence_confirm.py -q
uv run pytest tests/fund/test_chapter_auditor.py tests/fund/test_evidence_availability.py -q
uv run ruff check fund_agent/fund/evidence_confirm.py tests/fund/test_evidence_confirm.py
git diff --check -- fund_agent/fund/evidence_confirm.py tests/fund/test_evidence_confirm.py tests/README.md docs/reviews/evidence-confirm-anchor-auditability-score-aggregate-deepreview-fix-evidence-20260621.md docs/reviews/evidence-confirm-anchor-auditability-score-aggregate-deepreview-re-review-20260621.md docs/reviews/code-review-20260621-153037.md docs/reviews/code-review-20260621-153217.md docs/reviews/code-review-20260621-153307.md
```

Results:

- `20 passed in 0.79s`
- `60 passed in 0.90s`
- `All checks passed!`
- `git diff --check`: clean

## Residual Risks

- Phase 1 still verifies only caller-supplied excerpts; live source/PDF proof remains assigned to a later full Evidence Confirm gate.
- Numeric token matching is boundary-aware and Decimal-equivalent but still syntactic, not semantic entailment.
- Reviewed-note and derived-calculation proof production remain future gates.
- Malformed external fact id handling remains assigned to the future downstream adoption gate.

## Verdict

AGGREGATE_DEEPREVIEW_ACCEPTED_READY_FOR_COMMIT_NOT_READY
