# Release Maintenance ReportEvidenceBundle Typed Model / Projection — Implementation Plan Re-Review (AgentDS)

> Date: 2026-05-25
> Reviewer: AgentDS (targeted re-review)
> Gate: `typed ReportEvidenceBundle model/projection implementation plan review`
> Original review: `docs/reviews/release-maintenance-report-evidence-bundle-typed-model-projection-implementation-plan-review-ds-20260525.md`
> Patched plan: `docs/reviews/release-maintenance-report-evidence-bundle-typed-model-projection-implementation-plan-20260525.md`
> Verdict: **PASS**

## Re-Review Scope

Targeted re-review limited to: whether original 7 findings are resolved, and whether the patch introduced any new blocker.

## Finding Resolution

### F-01 (中) — Incomplete Dataclass Field Specifications → RESOLVED

Patch adds a full "Dataclass Field Specifications" subsection with complete field tables for all 12 dataclasses. Each table includes field name, required/default annotation, type, and notes. Fields are specified down to the tuple/list immutability constraint. The implementer no longer needs to cross-reference the S2 bundle plan to know what fields each dataclass carries.

### F-02 (低) — ReportEvidenceProjectionContext Field Optionality → RESOLVED

Patch adds an explicit field table with Required/default column. Four fields are required (`run_id`, `corpus_id`, `source_boundary`, `source_failure_category`); the remaining 10 have explicit defaults (`None`, `False`, `()`, `"not_reviewed"`, `"current"`, `"verified_annual_report"`, or default factory for `ReportQualityContext`). Constructor contract is unambiguous.

### F-03 (低) — chapter_id int→string Conversion → RESOLVED

Patch adds an explicit conversion rule in Step 4: `f"chapter_{chapter_id}"` with validation that the integer is in `0..7`. Out-of-range values derive `review_status="rejected"`. The `ReportPreferredLensChapter` field table confirms `chapter_id: ChapterRef` with note "Only `chapter_0` to `chapter_7`; not `report_level`."

### F-04 (低) — Test 10 ValueError vs rejected Bundle Ambiguity → RESOLVED

Patch removes the ambiguity from both the algorithm and the test spec:

- Step 7 table: "Return a constructed `ReportEvidenceBundle` with `review_status="rejected"` and a validation message / data gap explaining the contradiction; do not raise unless the underlying `ExtractedField` object itself cannot be inspected."
- Test 10: "Assert projection returns a `ReportEvidenceBundle` with `review_status=="rejected"`. … Do not accept `ValueError` for this case unless the object construction is impossible before projection can inspect the field."

The rejected-bundle path is now the mandated behavior.

### F-05 (低) — Anchor Dedup Two-Pass Normalization → RESOLVED

Patch fixes the sequencing in both Step 6 and Step 9:

- Step 6: "Normalize each locator object using the Step 9 locator normalization rules before any deduplication. Deduplicate anchors by normalized locator object … After deduplication, assign anchor ids, compute sha256 locator hashes, and apply deterministic collision suffixes."
- Step 9: "Normalize locator objects first, deduplicate identical normalized locator objects second, and assign ids / hashes / collision suffixes third."

Implementer has a clear three-phase pipeline.

### F-06 (低) — ReportDataGapOverride Field Specification → RESOLVED

Patch adds a complete 10-field table: `field_path`, `gap_kind`, `failure_category`, `reason_code`, `chapter_ids`, `required_report_wording` (all required); `related_claim_id`, `blocks_claim_ids`, `blocks_scoring_dimensions`, `score_issue_ids` (all defaulted). The S1 turnover gap example in Step 8 maps directly to these fields.

### F-07 (信息) — DerivedCalculation Deferral / Coverage → RESOLVED

Patch makes three changes:

1. Domain section: "The minimal slice should define the `DerivedCalculation` record shape only, with `ReportEvidenceBundle.derived_calculations` defaulting to an empty tuple. Do not populate calculations and do not add calculation-specific validation branches in the first slice."
2. Non-goals: "`DerivedCalculation` population or calculation-specific validation beyond storing an explicitly supplied empty/default tuple"
3. Residual risks table: new row documenting that `DerivedCalculation` population is deferred to a later calculation-source gate, with explicit coverage residual owner.

No uncovered-branch surprise for the implementer.

## New Content Audit

Patch adds the following new content not present in the original plan. Each item checked for regressions:

| Addition | Assessment |
|---|---|
| `ReportEvidenceProjectionContext.attempted_review_status` field (default `None`) | Safe. Ties into `accepted_baseline` rejection in Step 1 and test 21. Type is `ReviewStatus \| None`. |
| Step 1 validation: `attempted_review_status == "accepted_baseline"` → `ValueError` | Safe. Enforces the first-slice constraint at the earliest validation point. |
| `fund_code` / `report_year` must come from bundle, not context | Safe. Prevents identity drift between extraction bundle and projection metadata. Inline with S2 contract. |
| `ReportEvidenceBundle.validation_messages` (default `()`) | Safe. Provides a non-fatal warning channel for hash collision suffixing and similar diagnostics. |
| `ReportEvidenceBundle.fund_type_slot` (default `None`) | Safe. Separates classification from baseline slot membership, consistent with S1 design. |
| `ReportPreferredLensProjection.fund_type` typed as `ClassifiedFundType` with `unknown`-allowed note | Safe. Empty chapters when unknown, consistent with Step 4. |
| Test 21: `test_accepted_baseline_cannot_be_derived_or_forced` | Safe. Verifies both the derivation path (scoring_ready, not accepted_baseline) and the forced-attempt path (rejected or ValueError during context validation). |
| `source_failure_category == "none"` for scoring_ready (was `in {"none", "not_applicable"}`) | Safe. `SourceFailureCategory` domain explicitly excludes `not_applicable`, so the old `in` check was a no-op on the second value. This is a correction. |

No new blockers, no regressions, no contradictions introduced.

## Boundary Re-Check

Re-verified all stop conditions and boundaries from original review:

- No `FundDocumentRepository` / PDF / cache / source helper access: CONFIRMED
- No `extra_payload` / `**kwargs` / free dict: CONFIRMED
- No renderer / FQ0-FQ6 changes: CONFIRMED
- No Host/Agent package or `dayu.host` / `dayu.engine`: CONFIRMED
- No fixture promotion: CONFIRMED
- No parallel extraction path: CONFIRMED

## Validation

```text
rg -n "extra_payload|dayu\\.host|dayu\\.engine" docs/reviews/release-maintenance-report-evidence-bundle-typed-model-projection-implementation-plan-20260525.md
```

Result: zero matches (terms appear only in stop-condition / boundary statements).

```text
git diff --check
```

Result: passes.

## Conclusion

**PASS**

All 7 original findings are resolved. The patch adds complete dataclass field specifications, explicit required/default annotations, chapter_id conversion rule, rejected-bundle mandate for mode/value contradictions, anchor normalization/dedup/ID sequencing, `ReportDataGapOverride` fields, and `DerivedCalculation` deferral with coverage residual. No new blockers, regressions, or boundary violations. The plan is code-generation-ready.
