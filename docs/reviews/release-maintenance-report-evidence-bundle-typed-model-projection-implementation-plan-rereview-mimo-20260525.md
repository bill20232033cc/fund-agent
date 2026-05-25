# Re-Review: Typed ReportEvidenceBundle Model / Projection Implementation Plan

> Date: 2026-05-25
> Reviewer: AgentMiMo
> Reviewed artifact: `docs/reviews/release-maintenance-report-evidence-bundle-typed-model-projection-implementation-plan-20260525.md` (patched)
> Original review: `docs/reviews/release-maintenance-report-evidence-bundle-typed-model-projection-implementation-plan-review-mimo-20260525.md`
> Gate: `typed ReportEvidenceBundle model/projection implementation plan review`
> Scope: re-review of 4 original findings only; no new adversarial pass.

## Step Self-Check

- Reviewed target: patched implementation plan artifact.
- Focus: whether 4 original findings are resolved and whether patches introduced new blockers.
- Original findings: (1) `SourceFailureCategory` domain mismatch, (2) missing `accepted_baseline` test, (3) `ReportDataGapOverride` fields underspecified, (4) `fund_code`/`report_year` source not explicit.

## Finding Disposition

### Finding 1: SourceFailureCategory domain 包含 S2 未接受的值 — RESOLVED

- **Original**: `SourceFailureCategory` included `data_gap` and `not_applicable`, not in S2 accepted contract.
- **Patch**: Lines 123-131 now show exactly the 7 S2-accepted values: `none`, `not_found`, `unavailable`, `schema_drift`, `identity_mismatch`, `integrity_error`, `unknown_upstream_failure_category`. Lines 136-137 add explicit guard: "Do not add `data_gap` or `not_applicable` here. Fact-level data gaps and applicability gaps belong only to `GapKind`, `GapFailureCategory`, `DataGapReasonCode`, score records, or `ReportDataGap` records."
- **Verdict**: Fully resolved. Domain is now aligned with S2.

### Finding 2: 缺少 accepted_baseline 不可派生的显式测试 — RESOLVED

- **Original**: No test for `accepted_baseline` rejection in the 20-test plan.
- **Patch**: Test 21 `test_accepted_baseline_cannot_be_derived_or_forced` added (lines 1047-1051). Tests both that derivation never produces `accepted_baseline` and that explicit `attempted_review_status="accepted_baseline"` is rejected.
- **Supporting changes**:
  - `ReportEvidenceProjectionContext` now includes `attempted_review_status: ReviewStatus | None` field (line 535).
  - Step 1 validation (line 619) explicitly rejects `context.attempted_review_status == "accepted_baseline"`.
  - Step 11 (line 877) adds `accepted_baseline is attempted before a curated-fixture gate` as a `rejected` derivation condition.
- **Verdict**: Fully resolved. The test, context field, and validation rules are internally consistent.

### Finding 3: ReportDataGapOverride 字段未完全指定 — RESOLVED

- **Original**: Only dataclass name listed, no field specifications.
- **Patch**: Lines 560-573 now provide a complete field table with 10 fields: `field_path` (required), `gap_kind` (required), `failure_category` (required), `reason_code` (required), `chapter_ids` (required), `required_report_wording` (required), `related_claim_id` (default `None`), `blocks_claim_ids` (default `()`), `blocks_scoring_dimensions` (default `()`), `score_issue_ids` (default `()`).
- **Verdict**: Fully resolved. Sufficient for implementation without redesign.

### Finding 4: fund_code/report_year 来源未显式说明 — RESOLVED

- **Original**: Bundle id format requires `fund_code`/`report_year` but plan didn't say where they come from.
- **Patch**: Line 379: "`fund_code` and `report_year` always come from the input `StructuredFundDataBundle`, not from `ReportEvidenceProjectionContext`." Line 606: "Do not duplicate them in `ReportEvidenceProjectionContext`; duplicating identity fields creates mismatch risk." `ReportEvidenceBundle` table (lines 544-545) explicitly notes "From `StructuredFundDataBundle.fund_code`" and "From `StructuredFundDataBundle.report_year`".
- **Verdict**: Fully resolved. Source is explicit and rationale for not duplicating is stated.

## New Blocker Check

The patches added the following changes beyond finding fixes. None are blockers:

- `attempted_review_status` field on context: clean design, prevents silent baseline promotion, tested.
- `ReportDataGapOverride` full field table: consistent with Step 8 examples and `ReportDataGap` field names.
- `DerivedCalculation` clarified as shape-only in first slice (line 356, line 948): avoids coverage churn.
- Test 10 clarified to prefer rejected bundle over `ValueError` (lines 1001-1005): consistent with bundle-as-validation-artifact pattern.
- `validation_messages` field on `ReportEvidenceBundle` (line 558): useful for non-fatal warnings like hash collisions.
- Scoring-ready condition changed from `source_failure_category in {"none", "not_applicable"}` to `source_failure_category == "none"` (line 897): consistent with removing `not_applicable` from `SourceFailureCategory`.

No new overdesign, contradictions, or boundary violations found.

## Conclusion

**PASS**

All 4 original findings are resolved. Patches are internally consistent, do not introduce new blockers, and do not widen scope beyond the accepted S2 contract. The plan is code-generation-ready for the narrow implementation slice.

## Validation Commands

```text
rg -n "data_gap|not_applicable" docs/reviews/release-maintenance-report-evidence-bundle-typed-model-projection-implementation-plan-20260525.md | grep -i "SourceFailureCategory"
rg -n "accepted_baseline|attempted_review_status" docs/reviews/release-maintenance-report-evidence-bundle-typed-model-projection-implementation-plan-20260525.md
rg -n "ReportDataGapOverride" docs/reviews/release-maintenance-report-evidence-bundle-typed-model-projection-implementation-plan-20260525.md
rg -n "fund_code.*report_year.*bundle\|bundle\.fund_code\|bundle\.report_year\|StructuredFundDataBundle" docs/reviews/release-maintenance-report-evidence-bundle-typed-model-projection-implementation-plan-20260525.md | head -5
git diff --check
```

Expected: all pass. This is an artifact-only re-review gate.
