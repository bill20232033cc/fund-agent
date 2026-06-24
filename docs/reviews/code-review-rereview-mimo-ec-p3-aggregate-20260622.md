# Targeted Re-Review: EC-P3 Aggregate Finding 001

## Reviewed Target

Finding 001 from `docs/reviews/code-review-20260622-172254.md`:
"missing_bounded_excerpt fail-closed branch is untested"

## Scope

Verify that the fix — `test_semantic_missing_bounded_excerpt_does_not_call_client()` in `tests/fund/test_evidence_confirm_semantic.py` — fully covers the identified gap. No full code review. No code modification. No stage/commit/push.

## Evidence

- Fix: `tests/fund/test_evidence_confirm_semantic.py:257-281`
- Production branch: `fund_agent/fund/evidence_confirm_semantic.py:244-257`
- Aggregate status logic: `fund_agent/fund/evidence_confirm_semantic.py:500-521`

## Verification Checklist

### 1. New test covers passing V2 result + unmatched claim anchor

- Test at line 260-262: builds V2 result via `confirm_chapter_evidence_v2(chapter, references)` where reference excerpt "年报披露换手率为 120%。" matches the fact's value. The V2 result's `overall_status` is `pass` (deterministic value match succeeds).
- Test at line 266-267: creates claim then overrides `anchor_ids` to `("anchor:unmatched",)` via `replace(claim, anchor_ids=("anchor:unmatched",))`. This anchor id does not appear in `fact_result.matched_anchor_ids`.
- **Pass**: The test correctly constructs a passing V2 result with a claim referencing an unmatched anchor.

### 2. Assertions for overall_status fail, reason_code missing_bounded_excerpt, matched_anchor_ids empty

- Line 276: `assert result.overall_status == "fail"` — correct. `_overall_status()` at line 515 returns `"fail"` when any claim has `severity == "block"`.
- Line 279: `assert result.claim_results[0].reason_code == "missing_bounded_excerpt"` — matches production code at line 254.
- Line 280: `assert result.claim_results[0].matched_anchor_ids == ()` — matches production code at line 255.
- **Pass**: All three assertions are present and correct.

### 3. Semantic client not called

- Line 281: `assert client.requests == []` — verifies `client.judge()` was never invoked.
- Production code at line 249 returns before reaching `client.judge(request)` at line 261.
- **Pass**: Client non-invocation is asserted.

### 4. No production behavior boundary violations

- The test uses only existing test helpers (`_chapter_and_fact`, `_reference`, `_claim`, `_FakeEntailmentClient`).
- No production code was modified.
- No imports from Service, Host, UI, renderer, or quality gate layers.
- **Pass**: No boundary violation.

## Conclusion

`pass`

Finding 001 is fully fixed. The new test `test_semantic_missing_bounded_excerpt_does_not_call_client()` covers all four required dimensions: passing V2 + unmatched anchor, correct status/reason/anchor assertions, and client non-invocation.
