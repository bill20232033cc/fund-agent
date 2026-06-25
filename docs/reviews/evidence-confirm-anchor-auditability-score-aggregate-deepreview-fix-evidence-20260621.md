# Evidence Confirm Anchor Auditability Score Aggregate Deepreview Fix Evidence - 2026-06-21

## Gate

- Work unit: `Evidence Confirm / anchor auditability scoring phase 1`
- Branch: `evidence-confirm-anchor-audit-score`
- Fix scope: aggregate deepreview findings after slice commit `50fd162`
- Aggregate review artifacts:
  - `docs/reviews/code-review-20260621-153037.md`
  - `docs/reviews/code-review-20260621-153217.md`
  - `docs/reviews/code-review-20260621-153307.md`

## Finding Decisions

### AgentMiMo 1 - token substring matching false positive / false negative

- Decision: accepted
- Status: fixed
- Fix:
  - `_matched_anchor_ids()` now delegates each token to `_token_matches_excerpt()`.
  - Numeric tokens use `_numeric_token_matches_excerpt()` instead of raw substring matching.
  - Numeric matching extracts numeric candidates with boundary-aware regex and compares Decimal values.
  - Percent unit compatibility is preserved: percent tokens only match percent candidates.
- Regression tests:
  - `test_numeric_token_does_not_match_inside_larger_decimal`
  - `test_numeric_percent_token_matches_equivalent_decimal_format`

### AgentMiMo 2 - `reviewed_note` proof kind is currently unreachable

- Decision: deferred-with-owner
- Owner: future reviewed-note anchor production gate
- Reason: accepted plan explicitly included `reviewed_note` in the phase 1 reference contract. Current `ChapterEvidenceAnchor.source_kind` cannot produce it, so it is contract surface for a later producer, not current runtime behavior.

### AgentMiMo 3 - `derived_calculation` precision check is skipped

- Decision: deferred-with-owner
- Owner: future derived-calculation Evidence Confirm gate
- Reason: current `_fact_is_derived()` returns not_applicable before annual-report style E1/E2/E3 matching. Derived proof production and precision policy remain future scope.

### AgentMiMo 4 - mixed status aggregation untested

- Decision: accepted
- Status: fixed
- Regression test:
  - `test_chapter_aggregation_uses_strictest_status_and_average_score`

### AgentMiMo 5 - `report_year=0` skips report-year check

- Decision: deferred-with-owner
- Owner: future downstream adoption gate
- Reason: current `ChapterFactProjection` emits `chapter-fact:<fund_code>:<year>:...` ids. Malformed external or hand-built fact ids remain outside current phase 1 producer contract.

## Validation

Commands executed after aggregate fixes:

```bash
uv run pytest tests/fund/test_evidence_confirm.py -q
uv run pytest tests/fund/test_chapter_auditor.py tests/fund/test_evidence_availability.py -q
uv run ruff check fund_agent/fund/evidence_confirm.py tests/fund/test_evidence_confirm.py
```

Results:

- `20 passed in 0.88s`
- `60 passed in 0.99s`
- `All checks passed!`

## Residual Risks

- Phase 1 still verifies only caller-supplied excerpts; live source/PDF proof remains assigned to a later full Evidence Confirm gate.
- Numeric token matching is now boundary-aware and Decimal-equivalent, but remains syntactic support rather than semantic entailment.
- Reviewed-note and derived-calculation proof production are still future gates.
- Report-level adoption, quality gate impact and review workflow consumption remain assigned to a later work unit.

## Verdict

AGGREGATE_DEEPREVIEW_FIX_READY_FOR_RE_REVIEW_NOT_READY
