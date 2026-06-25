# Evidence Confirm Anchor Auditability Score PR 39 Review Fix Evidence - 2026-06-21

## Gate

- Work unit: `Evidence Confirm / anchor auditability scoring phase 1`
- PR: 39
- Branch: `evidence-confirm-anchor-audit-score`
- Fix scope: PR review findings from `docs/reviews/pr-39-review-20260621-193835.md`

## Finding Decisions

### PR review finding 1 - `_flatten_material_values` unknown type silently returns empty tuple

- Decision: rejected-with-reason
- Final status: evidence does not prove a current defect
- Reason:
  - Accepted plan explicitly allows oversized or complex object values with no material scalar token to become `not_applicable` unless the fact is required/critical, where E3 applies.
  - Current `ChapterFactProjection` values are shallow scalar/dict/list/dataclass values produced by existing Fund projection paths.
  - No current producer emits `set`, `bytes` or arbitrary custom object values.
  - This remains a future contract hardening topic if a new value producer expands the value domain.

### PR review finding 2 - empty projection path lacks independent test

- Decision: accepted
- Final status: fixed
- Fix:
  - Added `test_empty_projection_returns_not_applicable`.
  - The test constructs an empty `ChapterFactProjection` and verifies:
    - `overall_status == "not_applicable"`
    - `auditability_score is None`
    - `fact_results == ()`
    - `issues == ()`

## Validation

```bash
uv run pytest tests/fund/test_evidence_confirm.py -q
uv run pytest tests/fund/test_chapter_auditor.py tests/fund/test_evidence_availability.py -q
uv run ruff check fund_agent/fund/evidence_confirm.py tests/fund/test_evidence_confirm.py
```

Results:

- `21 passed in 0.80s`
- `60 passed in 0.92s`
- `All checks passed!`

## Residual Risks

- Unknown value-type hardening remains assigned to a future value-domain expansion gate.
- Phase 1 still verifies caller-supplied excerpts only; live source/PDF proof remains assigned to a later full Evidence Confirm gate.

## Verdict

PR_REVIEW_FIX_READY_FOR_RE_REVIEW_NOT_READY
