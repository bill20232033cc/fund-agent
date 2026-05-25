# Release Maintenance ReportEvidenceBundle Typed Model / Projection Implementation Re-Review — MiMo

> Date: 2026-05-25
> Reviewer: AgentMiMo (re-review of GLM F1 fix only)
> Gate: `typed ReportEvidenceBundle model/projection implementation`
> Prior review: `docs/reviews/release-maintenance-report-evidence-bundle-typed-model-projection-implementation-review-mimo-20260525.md`
> Fix scope: `_deduplicate_gaps` gap-reference merging + `test_missing_classified_fund_type_derives_unknown_and_gap` assertion update

## Conclusion

**PASS**

GLM F1 fix is correct. No new blockers or regression risk introduced.

## Fix Analysis

### What changed

**`fund_agent/fund/report_evidence.py`**:

1. `_deduplicate_gaps()` (line 1777): Previously discarded duplicate gaps entirely. Now calls `_merge_duplicate_gap_references()` to preserve back-references (`related_fact_id`, `related_claim_id`) from duplicate occurrences before discarding.

2. New `_merge_duplicate_gap_references()` (line 1803): Merges two same-`gap_id` records by taking the first non-None `related_fact_id` and `related_claim_id` via `or`. Returns the existing gap unchanged if no new references are contributed.

**`tests/fund/test_report_evidence.py`**:

1. `test_missing_classified_fund_type_derives_unknown_and_gap` (line 85): Now asserts:
   - Exactly 1 gap with `reason_code == "classified_fund_type_missing"` (deduplication works)
   - The gap has `related_fact_id == "fact:fund_type.classified_fund_type"` (merge preserved back-ref)
   - The classified fact's `data_gap_refs` contains the gap id (bidirectional reference)

### Correctness

- The merge logic is sound: `or` picks the first non-None value, which is correct because the first occurrence's `related_fact_id` is set by `_read_classified_fund_type` (line 1083) and the duplicate's is set by `_project_classified_fund_type_fact` (line 1527). Both carry the same fact id; the merge ensures neither is lost.
- `replace()` on frozen dataclass is the correct idiom for creating a new immutable instance with updated fields.
- The merge only touches `related_fact_id` and `related_claim_id`; other fields (gap_kind, failure_category, wording, etc.) are kept from the first occurrence, which is correct since duplicates carry the same business description.

### Regression risk

None. The change only affects the deduplication path for gaps with identical `gap_id`. Non-duplicate gaps are unaffected. The existing 22 tests that don't produce duplicate gaps continue to pass unchanged.

## Verification

| Command | Result |
|---------|--------|
| `pytest tests/fund/test_report_evidence.py::test_missing_classified_fund_type_derives_unknown_and_gap -v` | PASSED |
| `pytest tests/fund/test_report_evidence.py -q` | 23/23 passed |

## GLM F1 Status

**Closed.** The duplicate gap deduplication now correctly merges back-references, and the test explicitly validates the bidirectional fact-gap linkage.

## Remaining MiMo Findings

MiMo F1 (`expired` schema revision branch untested) and F2 (`turnover_rate` field path normalization asymmetry) from the initial review remain unchanged. Both are minor and non-blocking.
