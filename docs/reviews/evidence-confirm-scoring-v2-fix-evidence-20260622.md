# Evidence Confirm Scoring V2 Fix Evidence

## Scope

- Gate: fix
- Branch: `evidence-confirm-anchor-audit-score`
- Accepted review artifacts:
  - `docs/reviews/code-review-20260622-053343.md`
  - `docs/reviews/code-review-20260622-053647.md`
- Fixed files:
  - `fund_agent/fund/evidence_confirm.py`
  - `tests/fund/test_evidence_confirm.py`

## Accepted Findings Fixed

1. `001`: `_proof_failure_reason` now reports concrete anchor identity mismatch fields for `anchor.document_year`, `section_id`, `page_number`, `table_id`, and `row_locator`.
2. `002`: `_fact_score_v2` no longer keeps the currently unreachable non-blocking fail-score fallback branch.
3. `003`: `source_support` and `missing_evidence` now emit dimension-specific E3 failure messages.
4. `004`: V2 tests now lock E1 warn and all-pass auditability scores.
5. `code-review-20260622-053647.md/001`: `confirm_projection_evidence_v2()` now preserves the accepted plan ordering by `chapter_id`, `source_field_id`, and `fact_id` without changing the public V2 fact-result schema.

## Validation

- `uv run pytest tests/fund/test_evidence_confirm.py -q`
  - Result: `42 passed in 0.54s`
- `uv run pytest tests/fund/test_chapter_auditor.py tests/fund/test_evidence_availability.py -q`
  - Result: `60 passed in 0.65s`
- `uv run ruff check fund_agent/fund/evidence_confirm.py tests/fund/test_evidence_confirm.py`
  - Result: `All checks passed!`
- `git diff --check -- fund_agent/fund/evidence_confirm.py tests/fund/test_evidence_confirm.py docs/reviews/evidence-confirm-scoring-v2-fix-evidence-20260622.md`
  - Result: clean

## Verdict

`FIX_COMPLETE_VALIDATED_NOT_READY`
