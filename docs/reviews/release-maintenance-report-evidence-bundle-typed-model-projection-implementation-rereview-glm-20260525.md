# Release Maintenance ReportEvidenceBundle Typed Model / Projection Implementation Re-Review (GLM)

> Date: 2026-05-25
> Reviewer: AgentGLM (independent re-review of F1 fix)
> Gate: `typed ReportEvidenceBundle model/projection implementation`
> Scope: F1 fix regression review — `_deduplicate_gaps` merge logic + `test_missing_classified_fund_type_derives_unknown_and_gap` update
> Truth sources: original review `docs/reviews/release-maintenance-report-evidence-bundle-typed-model-projection-implementation-review-glm-20260525.md`, implementation plan

## Conclusion: PASS

**F1 is closed.** No new blocker exists. F2–F4 from the original review remain open as previously classified (all LOW); no regression introduced by the fix.

---

## F1 Fix Analysis

### What changed

**`fund_agent/fund/report_evidence.py`**:

1. **`_deduplicate_gaps()` (lines 1777–1800)**: Replaced simple "keep first, skip rest" dedup with merge-aware dedup. When a duplicate `gap_id` is encountered, the existing gap is updated via `_merge_duplicate_gap_references()` instead of silently discarded.

2. **`_merge_duplicate_gap_references()` (lines 1803–1831)**: New private helper. Uses `or` semantics to fill `related_fact_id` and `related_claim_id` on the first gap from the incoming duplicate — first-wins for existing values, second-fills for `None` fields. Only creates a new frozen instance via `replace()` when a value actually changes; returns the original object otherwise.

**`tests/fund/test_report_evidence.py`**:

3. **`test_missing_classified_fund_type_derives_unknown_and_gap` (lines 85–113)**: Updated to assert:
   - Exactly 1 gap with `reason_code="classified_fund_type_missing"` and `gap_kind="missing_fact"` (dedup working)
   - That single gap carries `related_fact_id="fact:fund_type.classified_fund_type"` (merge working)
   - The classified fund type fact references the gap's `gap_id` in its `data_gap_refs` (bidirectional link verified)

### Correctness of the fix

The duplicate scenario for `classified_fund_type` missing:

| Source | `gap_id` | `related_fact_id` |
|---|---|---|
| `_read_classified_fund_type` (line 1082) | `gap:{code}:{year}:missing_fact:classified_fund_type:classified_fund_type_missing` | `None` |
| `_project_classified_fund_type_fact` (line 1522) | same | `"fact:fund_type.classified_fund_type"` |

Merge result: `None or "fact:fund_type.classified_fund_type"` → the merged gap carries the explicit fact reference. ✓

The `or` merge semantics are safe for all four cases:
- Both `None`: no change. ✓
- Existing has value, incoming `None`: keeps existing. ✓
- Existing `None`, incoming has value: fills from incoming. ✓
- Both non-`None`: keeps existing (first-wins). ✓

In the current codebase, `classified_fund_type_missing` is the only duplicate `gap_id` scenario. The `blocks_claim_ids`, `blocks_scoring_dimensions`, and `score_issue_ids` fields are not merged — both gaps in the known duplicate carry empty tuples, so no information is lost.

### Regression risk assessment

| Risk | Assessment |
|---|---|
| Other gap dedup paths broken | No — `_deduplicate_gaps` still deduplicates by `gap_id`. Non-duplicate gaps pass through unchanged. The merge only fires when `gap_id` matches. |
| Object identity mutation | No — `_merge_duplicate_gap_references` uses `replace()` (frozen dataclass) or returns the original object unchanged. No in-place mutation. |
| Performance regression | Negligible — `index_by_gap_id` dict replaces the previous `seen` set; still O(n). One extra `replace()` call per duplicate gap, which is rare (only classified_fund_type missing in current code). |
| No-change path uncovered (line 1831) | The `return existing_gap` fast path when no merge is needed is uncovered. This is the optimization branch for non-duplicate or identical-reference gaps. No correctness risk — the covered merge path is the one that matters. |
| Coverage change | 93% (623 stmts, 45 miss) — same percentage as pre-fix. New function adds 8 stmts; the no-change return (line 1831) is the only new uncovered line. |

---

## Verification Results

| Check | Result |
|---|---|
| pytest (23 tests) | 23 passed |
| Line coverage | 93% (623 stmts, 45 miss) |
| Adjacent regression (controller ran) | 40 passed |
| ruff | Passed |
| Boundary rg | Clean — only negative-test assertions |
| git diff --check | Clean |

---

## Previous Findings Status

| Finding | Original severity | Status |
|---|---|---|
| F1: Duplicate gap loses fact reference | MEDIUM | **Closed** — merge logic fills `related_fact_id` from incoming duplicate |
| F2: Uncovered validation branches | LOW | Open — unchanged, not in fix scope |
| F3: Uncovered review status fallback states | LOW | Open — unchanged, not in fix scope |
| F4: Uncovered extraction mode fallback | LOW | Open — unchanged, not in fix scope |

---

*GLM independent re-review completed 2026-05-25. No files modified, no commits made.*
