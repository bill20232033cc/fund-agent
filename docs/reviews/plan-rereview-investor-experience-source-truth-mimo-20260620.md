# Targeted Plan Re-review: FundDisclosureDocument investor_experience.v1 Source-truth Direct Extraction

## Re-review Metadata

- **Reviewer**: AgentMiMo targeted planning reviewer
- **Gate**: Plan Re-review Gate
- **Reviewed plan**: `docs/reviews/funddisclosuredocument-investor-experience-source-truth-extraction-plan-20260620.md`
- **Prior DS review**: `docs/reviews/plan-review-investor-experience-source-truth-ds-20260620.md`
- **Prior MiMo review**: `docs/reviews/plan-review-investor-experience-source-truth-mimo-20260620-114946.md`
- **Branch**: `funddisclosure-investor-experience-source-truth`, HEAD `57c992f`
- **Verdict**: `TARGETED_PLAN_REREVIEW_PASS`

## Scope

Verify that the six accepted plan-review findings were addressed in the plan artifact. Do not expand into full plan review except to identify a new blocker introduced by the fix.

## Accepted Findings Verification

### DS Finding 1: share_change FDD column selection specificity

**Plan fix location**: Section 5.3 `share_change` Selection (lines 216-224)

**What was added**:
- Column header text construction from `column_header_path`: group cells by `column_index`, collect non-empty strings from `cell.column_header_path`, trim whitespace, deduplicate, join with ` / `.
- Label column identification: aggregated header text or stable row-label-like cells dominated by label tokens (`项目`, `项目名称`, `份额类别`, `类别`, `基金份额`, `基金份额项目`, `变动项目`, `期初`, `期末`, `申购`, `赎回`, or allowed row labels).
- Value column validation: must contain at least one stable beginning/ending/net row value after label-column exclusion.
- `fund_code_header_match` requires exact match against `context.fund_code` after trimming whitespace and removing internal whitespace from both sides. Substring, prefix, suffix, fuzzy, fund-name, or share-class-name matches are not allowed.

**Code fact cross-check**:
- `contracts.py:404-405`: each cell has `column_header_path: tuple[str, ...]` — the plan's aggregation strategy correctly operates at cell level.
- `holdings_share_change.py:824-873`: existing `_select_share_change_value_column()` uses `table.headers` and `_ShareClassEvidence` — the plan defines FDD-specific equivalents without importing the ParsedTable dependency.

**Verdict**: ADDRESSED. The column selection rules are now specific enough for implementation agent to code directly from the plan.

### DS Finding 2: holder_structure placeholder filtering

**Plan fix location**: Section 5.2 `holder_structure` Selection (lines 192-194)

**What was added**:
- "Reject empty or placeholder values before conflict resolution. Invalid holder side values include empty string, whitespace-only text, `无`, `不适用`, `-`, `—`, and `未披露`."
- "A rejected placeholder side remains `None`; it must not be emitted as a public value and must not by itself make `holder_structure` present."
- Test `test_investor_experience_source_truth_holder_structure_filters_placeholder_values` (line 338).

**Code fact cross-check**:
- `manager_ownership.py:922`: existing `_build_holder_structure()` uses `_extract_field()` which has token match + value extraction — the FDD direct route cannot reuse `_extract_field()` because it operates on FDD intermediate protocol, so explicit placeholder rejection is the correct approach.

**Verdict**: ADDRESSED. Placeholder token set is explicit and test coverage is specified.

### DS Finding 3: investor_return paragraph label/value and unavailable wording

**Plan fix location**: Section 5.1 `investor_return` Selection (lines 165-167)

**What was added**:
- "Paragraph extraction requires a label token plus a valid percent value in the same paragraph block. The value must appear after the label or within the immediate label/value phrase around the label; a label-only paragraph is not enough."
- "If the paragraph contains negated or unavailable wording near the matched label, including `未披露`, `未提供`, `无法取得`, `不适用`, or `无`, omit `investor_return` for that paragraph even if the label token matches."
- Test `test_investor_experience_source_truth_investor_return_paragraph_requires_label_value_pattern` (line 335).

**Code fact cross-check**:
- `performance.py:1113`: existing `_build_investor_return()` uses `_extract_field(report, "investor_return_rate")` which has internal token match + value extraction — the FDD direct route paragraph pattern is an explicit equivalent.
- The unavailable wording list (`未披露`, `未提供`, `无法取得`, `不适用`, `无`) covers the common Chinese negation/absence patterns.

**Verdict**: ADDRESSED. Paragraph extraction semantics are now specified with label+value requirement and negation guard.

### MiMo Finding 004: net_change Decimal semantics

**Plan fix location**: Section 5.3 `share_change` Selection (line 226)

**What was added**:
- "calculate `ending - beginning` with `Decimal` arithmetic aligned with the existing `_calculate_net_change` semantics in `holdings_share_change.py`; preserve stable text formatting by using a deterministic decimal string derived from the computed `Decimal` without scientific notation and without adding presentation units"
- Test `test_investor_experience_source_truth_share_change_calculates_net_change` (line 352).

**Code fact cross-check**:
- `holdings_share_change.py:1274-1296`: `_calculate_net_change()` uses `Decimal`, strips commas via `.replace(",", "")`, computes `ending_value - beginning_value`, formats as `f"{net_change:,.2f}"`.
- The plan says "aligned with the existing `_calculate_net_change` semantics" — this correctly delegates format alignment to the implementation agent while specifying the Decimal arithmetic contract.

**Verdict**: ADDRESSED. The Decimal semantics contract is explicit. The implementation agent should match `f"{net_change:,.2f}"` format from the existing helper.

### MiMo Finding 005: estimated investor_return conflict rule and tests

**Plan fix location**: Section 5.1 `investor_return` Selection (lines 171); Slice 2 test (line 333)

**What was added**:
- "If multiple estimated values exist and their normalized values conflict, apply the same ambiguity rule as direct conflicts: omit `investor_return` and add `ambiguous_table_or_locator` with `source_field_path="investor_return"`."
- Test `test_investor_experience_source_truth_estimated_investor_return_conflict_omits_value` (line 333).

**Code fact cross-check**:
- The ambiguity rule is consistent with the general conflict rule at line 148: "Same output path + conflicting normalized values: omit that output path and add `ambiguous_table_or_locator`."
- The estimated-specific rule at line 171 correctly applies the same logic.

**Verdict**: ADDRESSED. Estimated conflict resolution is now explicit with test coverage.

### MiMo Finding 006: current_stage/core_risk candidate evidence unaffected by investor direct-route suppression

**Plan fix location**: Section 6 Remaining families (lines 252-253); Slice 2 test (line 355)

**What was added**:
- "Their existing candidate selectors may still populate candidate evidence when matching candidate content exists; `investor_experience.v1` direct-route suppression must not clear, suppress, or otherwise alter their candidate evidence. They must not enter source-truth direct extraction."
- Test `test_investor_experience_source_truth_does_not_populate_stage_or_risk` (line 355).

**Code fact cross-check**:
- `_field_families_for_intermediate()` (line 848): the existing suppression pattern for `product_essence` only affects `product_essence_evidence`; it does not touch other family evidence. The same local-variable pattern for `investor_experience` will similarly not affect `current_stage` or `core_risk` evidence.

**Verdict**: ADDRESSED. The isolation boundary is explicit with test verification.

## New Blocker Check

No new blocker was introduced by the fixes. All changes are additive clarifications within existing plan sections. The plan structure, scope, non-goals, implementation slices, allowed files, and validation commands remain unchanged.

## Open Questions (from prior reviews, still applicable)

None that block code generation. The prior open questions (MiMo review) around holder_structure partial test, estimated-only test, and net_change test are now addressed by the added test specifications.

## Residual Risks (unchanged from prior reviews)

1. FDD source-truth direct extraction remains no-live fixture-backed.
2. `investor_return` source labels may differ across reports; fail-closed is intentional.
3. `share_change` column selection is intentionally narrower (no §2 evidence).
4. `subscription_redemption` and `income_distribution` remain candidate-only.

**Tracking destination**: `docs/implementation-control.md` residuals section.

## Conclusion

`TARGETED_PLAN_REREVIEW_PASS`

All six accepted findings (DS 1/2/3, MiMo 004/005/006) have been addressed in the plan artifact with sufficient specificity for code generation. The fixes are additive clarifications that do not introduce new blockers, change scope, or alter the plan's implementation structure. The plan remains code-generation-ready.

---

**Reviewer**: AgentMiMo targeted planning reviewer
**Re-review timestamp**: 20260620-115758
**Artifact path**: `docs/reviews/plan-rereview-investor-experience-source-truth-mimo-20260620.md`
