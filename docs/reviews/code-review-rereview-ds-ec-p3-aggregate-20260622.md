# Targeted Re-Review — EC-P3 Aggregate Finding 001

## Metadata

- **Date**: 2026-06-22
- **Source**: aggregate deepreview `docs/reviews/code-review-20260622-172254.md` finding 001
- **Finding**: missing_bounded_excerpt fail-closed branch is untested
- **Fix under review**: `tests/fund/test_evidence_confirm_semantic.py` — `test_semantic_missing_bounded_excerpt_does_not_call_client`
- **Re-review scope**: accepted finding 001 only; no full code review, no code changes, no stage/commit/push

## Checks

### 1. Coverage: passing V2 result + unmatched claim anchor

**PASS** — Test creates a passing V2 result via `confirm_chapter_evidence_v2`, then sets `claim.anchor_ids = ("anchor:unmatched",)`. This exercises the exact production path where `_bounded_excerpts_for_claim()` finds no intersection between claim anchors and deterministic `matched_anchor_ids`.

### 2. Assertions: overall_status fail, reason_code missing_bounded_excerpt, matched_anchor_ids empty

**PASS** — Lines 276–280 assert:
- `result.overall_status == "fail"`
- `result.claim_results[0].reason_code == "missing_bounded_excerpt"`
- `result.claim_results[0].matched_anchor_ids == ()`

Also asserts `status == "insufficient"` and `severity == "block"`, consistent with the finding's suggested verification points.

### 3. Assertion: semantic client not called

**PASS** — Line 281 asserts `client.requests == []`. `_FakeEntailmentClient.judge()` appends to `self.requests` on every call, so an empty list confirms the client was never invoked.

### 4. No production behavior boundary violation

**PASS** — Only a test function is added. The exercised production code path (`_confirm_single_claim` → `_bounded_excerpts_for_claim` → return `missing_bounded_excerpt` without client call, lines 244–257) is unchanged. No cross-module imports, no new production logic, no boundary crossing.

## Conclusion

**pass**
