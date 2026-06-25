# Evidence Confirm Anchor Auditability Score Re-review - 2026-06-21

## Gate

- Work unit: `Evidence Confirm / anchor auditability scoring phase 1`
- Branch: `evidence-confirm-anchor-audit-score`
- Scope: targeted re-review after `docs/reviews/evidence-confirm-anchor-auditability-score-fix-evidence-20260621.md`

## Inputs

- Original reviews:
  - `docs/reviews/code-review-20260621-150809.md`
  - `docs/reviews/code-review-20260621-150938.md`
  - `docs/reviews/code-review-20260621-151953.md`
- Fix evidence:
  - `docs/reviews/evidence-confirm-anchor-auditability-score-fix-evidence-20260621.md`
- Implementation files:
  - `fund_agent/fund/evidence_confirm.py`
  - `tests/fund/test_evidence_confirm.py`
  - `fund_agent/fund/README.md`
  - `docs/design.md`
  - `tests/README.md`

## Multi-agent Re-review Summary

### AgentCodex

- Target: original finding 001 from `code-review-20260621-150809.md`
- Evidence observed:
  - Re-read `evidence_confirm.py` and `test_evidence_confirm.py`.
  - Verified proof predicate now receives current chapter anchor map and report year.
  - Verified `_reference_matches_anchor()` checks source kind, report year, anchor document year and explicit locator conflicts.
  - Verified unsupported anchor source kinds are handled at `_confirm_fact()`.
  - Ran `uv run ruff check fund_agent/fund/evidence_confirm.py tests/fund/test_evidence_confirm.py`.
  - Ran `git diff --check -- fund_agent/fund/evidence_confirm.py tests/fund/test_evidence_confirm.py docs/reviews/evidence-confirm-anchor-auditability-score-fix-evidence-20260621.md`.
  - Ran `uv run pytest tests/fund/test_evidence_confirm.py -q` with 17 passing tests.
- Final chat line: missing; AgentCodex pane did not emit the requested three-line final conclusion after follow-up.
- Controller judgment: evidence is sufficient to mark finding 001 fixed.

### AgentDS

- Target: original findings 001-003 from `code-review-20260621-150938.md`
- Result:
  - `test_available_fact_with_anchor_but_empty_references_fails_e3` covers anchors-present plus empty references E3.
  - `test_empty_excerpt_emits_e1_and_e2` covers empty excerpt E1 + E2.
  - `test_candidate_only_reference_cannot_satisfy_source_support`, `test_not_proven_reference_cannot_satisfy_source_support` and `test_unknown_source_kind_reference_cannot_satisfy_source_support` independently cover proof predicate conditions.
  - AgentDS reported all three accepted findings fixed and no new defect or regression.

### AgentMiMo

- Target: observations from `code-review-20260621-151953.md`
- Result:
  - Observation 1 rejection accepted: `_PUNCTUATION_RE` does not remove ASCII `.` or `%`; the original finding evidence was invalid.
  - Observation 2 deferred accepted: malformed external fact ids are outside current `ChapterFactProjection` contract and assigned to a future downstream adoption gate.
  - Observation 3 deferred accepted: private `_bundle` fixture reuse is maintainability cleanup assigned to future test fixture cleanup.
  - AgentMiMo found no documentation overclaim.

## Final Finding Status

| Finding | Decision | Final status |
| --- | --- | --- |
| AgentCodex 001 reference proof not bound to chapter anchor/source identity | accepted | 已修复 |
| AgentDS 001 anchors-present-zero-references path untested | accepted | 已修复 |
| AgentDS 002 empty excerpt combined E1/E2 untested | accepted | 已修复 |
| AgentDS 003 proof predicate checks tested together | accepted | 已修复 |
| AgentMiMo observation 1 numeric normalization may conflate values | rejected-with-reason | 证据失效 |
| AgentMiMo observation 2 malformed fact id can report year 0 | deferred-with-owner | 已分类 |
| AgentMiMo observation 3 private test fixture helper dependency | deferred-with-owner | 已分类 |

## Validation

Latest controller validation:

```bash
uv run pytest tests/fund/test_evidence_confirm.py -q
uv run pytest tests/fund/test_chapter_auditor.py tests/fund/test_evidence_availability.py -q
uv run ruff check fund_agent/fund/evidence_confirm.py tests/fund/test_evidence_confirm.py
git diff --check -- fund_agent/fund/evidence_confirm.py tests/fund/test_evidence_confirm.py fund_agent/fund/README.md docs/design.md tests/README.md docs/reviews/evidence-confirm-anchor-auditability-score-implementation-evidence-20260621.md docs/reviews/evidence-confirm-anchor-auditability-score-fix-evidence-20260621.md docs/reviews/code-review-20260621-150809.md docs/reviews/code-review-20260621-150938.md docs/reviews/code-review-20260621-151953.md
```

Results:

- `17 passed in 0.66s`
- `60 passed in 0.74s`
- `All checks passed!`
- `git diff --check`: clean

## Residual Risks

- Phase 1 still verifies only caller-supplied excerpts; live source/PDF proof remains assigned to a later full Evidence Confirm gate.
- Material token matching remains conservative substring matching and is not semantic entailment.
- Report-level adoption, quality gate impact and review workflow consumption remain assigned to a later work unit.
- Malformed external fact id behavior and shared test fixture cleanup are classified deferred residuals.

## Verdict

CODE_REVIEW_ACCEPTED_READY_FOR_SLICE_COMMIT_NOT_READY
