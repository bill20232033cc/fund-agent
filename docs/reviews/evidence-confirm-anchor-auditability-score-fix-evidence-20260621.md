# Evidence Confirm Anchor Auditability Score Fix Evidence - 2026-06-21

## Gate

- Work unit: `Evidence Confirm / anchor auditability scoring phase 1`
- Branch: `evidence-confirm-anchor-audit-score`
- Fix scope: accepted findings from multi-agent code review
- Review artifacts:
  - `docs/reviews/code-review-20260621-150809.md` (AgentCodex)
  - `docs/reviews/code-review-20260621-150938.md` (AgentDS)
  - `docs/reviews/code-review-20260621-151953.md` (AgentMiMo)

## Finding Decisions

### AgentCodex 001 - reference proof not bound to chapter anchor/source identity

- Decision: accepted
- Status: fixed
- Fix:
  - `confirm_chapter_evidence()` now builds `anchor_id -> ChapterEvidenceAnchor` map from the current chapter.
  - `confirm_projection_evidence()` now passes per-chapter anchor maps and projection report year into fact confirmation.
  - `_reference_is_proof()` now requires `_reference_matches_anchor()`.
  - `_reference_matches_anchor()` fail-closes source kind, report year, anchor document year and explicit locator contradictions.
  - Known anchors with only phase-1 unsupported source kinds, such as `external_api`, are `not_applicable` instead of E3.
- Regression tests:
  - `test_reference_source_kind_must_match_chapter_anchor_source_kind`
  - `test_reference_document_year_must_match_report_year`
  - projection aggregation asserts `structured.nav_data` is `not_applicable` and unscored.

### AgentDS 001 - anchors-present-zero-references path untested

- Decision: accepted
- Status: fixed
- Regression test:
  - `test_available_fact_with_anchor_but_empty_references_fails_e3`

### AgentDS 002 - empty excerpt combined E1/E2 untested

- Decision: accepted
- Status: fixed
- Regression test:
  - `test_empty_excerpt_emits_e1_and_e2`

### AgentDS 003 - proof predicate checks tested together

- Decision: accepted
- Status: fixed
- Regression tests:
  - `test_candidate_only_reference_cannot_satisfy_source_support`
  - `test_not_proven_reference_cannot_satisfy_source_support`
  - `test_unknown_source_kind_reference_cannot_satisfy_source_support`

### AgentMiMo observation 1 - numeric normalization may conflate `1.20%` and `120%`

- Decision: rejected-with-reason
- Status: evidence invalid
- Reason: current `_PUNCTUATION_RE` does not remove ASCII `.` or `%`; `unicodedata.normalize("NFKC", ...)` also preserves their semantic distinction. The cited direct evidence was incorrect.

### AgentMiMo observation 2 - malformed fact id can still produce report year `0`

- Decision: deferred-with-owner
- Owner: future downstream adoption gate
- Reason: current phase 1 now reads normal `chapter-fact:<fund_code>:<year>:...` ids before references. Malformed external fact ids remain out of current `ChapterFactProjection` contract.

### AgentMiMo observation 3 - test module imports private `_bundle`

- Decision: deferred-with-owner
- Owner: future test fixture cleanup
- Reason: existing fund tests already share local helper fixtures. This is maintainability cleanup, not a correctness blocker for this slice.

## Validation

Commands executed after fixes:

```bash
uv run pytest tests/fund/test_evidence_confirm.py -q
uv run pytest tests/fund/test_chapter_auditor.py tests/fund/test_evidence_availability.py -q
uv run ruff check fund_agent/fund/evidence_confirm.py tests/fund/test_evidence_confirm.py
git diff --check -- fund_agent/fund/evidence_confirm.py tests/fund/test_evidence_confirm.py fund_agent/fund/README.md docs/design.md tests/README.md docs/reviews/evidence-confirm-anchor-auditability-score-implementation-evidence-20260621.md docs/reviews/code-review-20260621-150809.md docs/reviews/code-review-20260621-150938.md docs/reviews/code-review-20260621-151953.md
```

Results:

- `17 passed in 0.40s`
- `60 passed in 0.51s`
- `All checks passed!`
- `git diff --check`: clean

## Residual Risks

- Phase 1 still verifies only caller-supplied excerpts; live source/PDF proof remains assigned to a later full Evidence Confirm gate.
- Material token matching remains conservative substring matching and is not semantic entailment.
- Report-level adoption, quality gate impact and review workflow consumption remain assigned to a later work unit.

## Verdict

FIX_READY_FOR_RE_REVIEW_NOT_READY
