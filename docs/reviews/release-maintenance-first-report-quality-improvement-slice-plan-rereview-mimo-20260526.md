# Gate C Plan Re-Review: First Report-Quality Improvement Slice Plan (Patch Verification)

> Date: 2026-05-26
> Reviewer: AgentMiMo
> Review type: targeted re-review of MiMo F1-F4 closure after plan patch
> Review target: `docs/reviews/release-maintenance-first-report-quality-improvement-slice-plan-20260526.md` (patched)
> Prior review: `docs/reviews/release-maintenance-first-report-quality-improvement-slice-plan-review-mimo-20260526.md`
> GLM review: `docs/reviews/release-maintenance-first-report-quality-improvement-slice-plan-review-glm-20260526.md`
> Scope: only verify MiMo F1-F4 closure; report any new blocker introduced by the patch.

---

## Verdict

**PASS**

All four findings are closed by the plan patch. No new blocker introduced.

---

## Closure Table

| Finding | Severity | Closure status | Evidence in patched plan |
|---------|----------|----------------|--------------------------|
| F1 — Exact Chinese strings not specified | Material | **Closed** | New section "Exact Wording And Route Decisions" (lines 46-91) provides: (1) exact old/new strings table for 2 `must_answer` modifications, 1 `must_not_cover` addition, 1 `required_output_items` addition; (2) exact `ContractRequiredItemRule` markers; (3) exact `required_report_wording` sentence anchored to validated test precedent at `test_report_evidence.py:277`. |
| F2 — Audit route for new must_not_cover underspecified | Material | **Closed** | Lines 85-86: "The new semantic `must_not_cover` entry must be covered by adding one `ContractMustNotCoverCoverageRule` to `_MUST_NOT_COVER_COVERAGE_RULES` with `coverage_kind='narrative_guidance'`." and "Do not use `ContractForbiddenContentRule` for this entry." No ambiguity remains. |
| F3 — Modify/add decision and coverage route details vague | Material | **Closed** | Lines 48-51 explicitly state: "Modify two existing `must_answer` entries. Add one new semantic `must_not_cover` entry. Add one new `required_output_items` entry." Lines 87-91 specify exact coverage route changes: update two `ContractMustAnswerCoverageRule.question_text` values, keep `covered_by_required_item`, route each to existing judgment item plus new data-gap item, add one `ContractRequiredItemRule`, add one `ContractMustNotCoverCoverageRule`. |
| F4 — Update order not specified | Minor | **Closed** | Lines 54-58: "Update order is mandatory: 1. Update `docs/fund-analysis-template-draft.md` Chapter 3 `CHAPTER_CONTRACT` first as the human template truth. 2. Mirror the same wording into `fund_agent/fund/template/contracts.py` as the machine truth. 3. Update `fund_agent/fund/audit/contract_rules.py` coverage routes to match the machine-truth strings." |

---

## GLM Informational Findings Cross-Check

GLM's four informational findings were reviewed against the patched plan:

| GLM Finding | Patch coverage |
|-------------|---------------|
| F1 — `ReportDataGapOverride` has no structured next-validation-question field | Patched plan line 81: "Do not add a separate next-validation-question field unless the existing `required_report_wording` path demonstrably cannot carry the wording." Aligns with GLM recommendation. |
| F2 — Existing data-gap test does not assert projected `required_report_wording` content | Patched plan line 206-210: "Extend `test_extraction_mode_missing_produces_data_gap_ref()` ... to assert `ReportDataGapOverride.required_report_wording` ... preserves: insufficiency wording; no unsupported style-stability/style-consistency claim; next minimum validation question." Aligns with GLM recommendation. |
| F3 — Plan's suggested contract intent is English; implementation agent will produce Chinese wording | Patched plan now provides exact Chinese strings in the wording table (lines 62-67). This concern is fully resolved. |
| F4 — Provenance wording for quasi-real evidence identity status | Non-blocking; out of scope for a contract-wording gate. No action needed. |

---

## New Blocker Check

No new blocker introduced by the patch. Specific checks:

1. **Exact strings consistency**: The new `must_answer` strings in the wording table (lines 64-65) are consistent with each other — both reference "已复核的换手率或风格变化证据" as the evidence precondition. The `must_not_cover` addition (line 66) uses compatible terminology ("换手率或风格变化证据缺失、不可用、未复核时"). No internal contradiction.

2. **Audit route completeness**: The patch specifies updating 2 `ContractMustAnswerCoverageRule` entries, adding 1 `ContractRequiredItemRule`, and adding 1 `ContractMustNotCoverCoverageRule`. This accounts for all changes: 2 modified `must_answer` + 1 new `must_not_cover` + 1 new `required_output_items`. The `_validate_must_not_cover_coverage_rules()` completeness check will pass because the new `must_not_cover` item will be covered by the new `ContractMustNotCoverCoverageRule`.

3. **Marker uniqueness**: The new markers `("换手率/风格变化证据缺口说明：", "下一步最小验证问题：")` do not conflict with existing Chapter 3 markers in `_REQUIRED_ITEM_RULES` (lines 160-165 of `contract_rules.py`). The existing markers are `("基金经理基本信息：",)`, `("宣称的投资策略（§4）：",)`, `("实际投资行为（§8）：",)`, `("言行一致性判断：",)`, `("风格稳定性判断：",)`, `("利益一致性判断：",)`.

4. **`required_report_wording` compatibility**: The exact wording sentence (lines 77-79) is a narrow extension of the validated anchor at `test_report_evidence.py:277`. The existing `ReportDataGapOverride.required_report_wording: str` field can carry this string without schema changes.

5. **Coverage route for modified must_answer**: The patch specifies routing the two modified `must_answer` entries to *two* required items each (existing judgment item + new data-gap item). This is a valid `covered_by_required_item` routing — the `_validate_required_item_coverage_rule()` check at lines 753-781 of `contract_rules.py` validates that each `required_item_text` exists in both the manifest and the `_REQUIRED_ITEM_RULES` set. As long as the new `ContractRequiredItemRule` for `换手率/风格变化证据缺口说明与下一步最小验证问题` is added before the coverage rules are validated, this will pass.

---

## Residual Risks

| Residual | Severity | Notes |
|----------|----------|-------|
| Contract wording becomes too broad and blocks legitimate Chapter 3 judgments | Low | Patched plan constrains scope to active-fund stability/style-consistency claims only; manager holding traceability remains separate. Wording is narrow. |
| Renderer still may not emit the new wording | Low | Expected residual; correctly identified in plan's "Residuals After This Slice" section. |
| `docs/design.md` update decision | Low | Plan's approach (update only if template structure changes) is acceptable. Adding must_answer/must_not_cover/required_output_items items is a narrow structural change; the implementation artifact should record the decision either way. MiMo F5 from prior review remains informational. |
| `docs/fund-analysis-template-draft.md` and `contracts.py` drift | Low | Patched plan mandates template-draft-first update order, reducing drift risk. |

---

## Controller Recommendation

Accept the patched plan. All four MiMo findings (3 material, 1 minor) are closed. GLM's informational findings are either addressed by the patch or correctly scoped as non-blocking. No new blocker was introduced. The plan is now code-generation-ready.
