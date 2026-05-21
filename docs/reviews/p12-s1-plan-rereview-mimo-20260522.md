# P12-S1 Plan Re-Review — AgentMiMo (targeted)

- **Reviewer**: AgentMiMo (independent plan reviewer)
- **Gate**: `P12-S1 ITEM_RULE renderer/audit compliance plan/review`
- **Initial review**: `docs/reviews/p12-s1-plan-review-mimo-20260522.md`
- **Revised plan**: `docs/reviews/p12-s1-item-rule-renderer-audit-compliance-plan-20260522.md`
- **Scope**: Targeted re-review of 4 findings from initial review against revised plan

---

## Verdict: PASS

All 4 findings are resolved or substantially addressed. No blocking issues remain.

---

## Finding-by-Finding Assessment

### Finding 1: Fail-closed check scope contradiction — RESOLVED

**Was**: HIGH — internal contradiction between absolute fail-closed rule and soft compatibility note, with ~9 existing C2 tests at risk.

**Now**: The revised plan introduces `TemplateItemRuleAuditContext = Literal["identity_missing", "identity_present"]` as a new field in both `TemplateRenderResult` and `ProgrammaticAuditInput` (section 4.1, Slice 1 step 3-6). The fail-closed check is now conditional on audit context:

- `identity_missing` + empty decisions → skip ITEM_RULE missing-decision C2 issue (P/L/R checks still run)
- `identity_present` + empty decisions + chapter_blocks exist → C2 issue
- `identity_present` + non-empty decisions → run presence/delete compliance

The compatibility note (Slice 3) now explicitly categorizes test update impact:

- Helpers like `_valid_audit_input()` should use `render_template_report().audit_input` so decisions/context come from renderer.
- Tests rebuilding `ProgrammaticAuditInput` from rendered output should copy both fields from `render_result.audit_input`.
- Tests isolating P/L/R failures with partial inputs keep the default `identity_missing` context.
- New C2 tests explicitly set `identity_present` when simulating missing decisions.

This resolves the contradiction: the check is deterministic and conditional on a well-defined context field, not on an undefined "enough input" threshold. The default `item_rule_audit_context="identity_missing"` on `ProgrammaticAuditInput` means existing L1/R1/R2 tests that don't provide chapter_blocks continue to work without changes. C2 tests that provide chapter_blocks will need the context field, but the compatibility note now identifies exactly which patterns need updating and how.

**Assessment**: Fully resolved. The audit context approach is cleaner than either of my suggested fixes (explicit enumeration or boolean flag) because it carries semantic meaning and integrates with the renderer's existing missing-data path.

---

### Finding 2: Missing test coverage for enhanced_index, bond_fund, qdii_fund, fof_fund — RESOLVED

**Was**: MEDIUM — only `active_fund` and `index_fund` required in Slice 1 step 5 tests.

**Now**: Revised plan adds coverage requirements across multiple locations:

- Slice 1 step 7: "enhanced index renders index constituents, alpha breakdown and tracking error, deletes manager philosophy" + "at least one non-triggering fund type such as `bond_fund` deletes all four" + "preferably table-driven checks for all six standard fund types"
- Slice 3 step 4: "enhanced index render/delete matrix passes through audit" + "at least one non-triggering fund type, preferably `bond_fund`, verifies all built-in markers are absent"
- Acceptance criterion 4: "Bond/QDII/FOF, or at least a table-driven all-six-fund-type test matrix, verifies non-triggering fund types delete all current built-in conditional segments"

Coverage now requires: active, index, enhanced_index, and at least one of bond/qdii/fof. Since bond/qdii/fof share identical behavior (all 4 rules delete), testing one is sufficient to verify the pattern. The "preferably table-driven" language encourages full coverage without mandating it.

**Assessment**: Substantially resolved. The minimum required coverage (4 types) covers all distinct behavioral patterns: active (2 render, 2 delete), index (2 render, 2 delete), enhanced (3 render, 1 delete), and non-triggering (0 render, 4 delete). The recommendation for table-driven all-six-type tests is good practice but not a blocking requirement.

---

### Finding 3: Evidence anchoring ambiguity for new segments — RESOLVED

**Was**: MEDIUM — only 2 of 4 segments had clear evidence anchor sources; index constituents and tracking error were ambiguous.

**Now**: Revised plan addresses this in three places:

Section 4.2 (Renderer segment behavior table): Each segment now has explicit evidence constraints in the renderer behavior column:
- Index constituents: "Benchmark anchor only proves benchmark/index reference, not constituents or methodology; therefore methodology and constituents must render as `数据不足` until an extractor exists."
- Tracking error: "deterministic data-insufficient placeholder until a tracking-error extractor exists; do not calculate or infer tracking error."

Section 4.2 (Evidence strategy subsection): Per-segment evidence rules:
- Index constituents: "benchmark anchors cannot be used as evidence for index constituents or methodology"
- Manager philosophy: "uses `manager_strategy_text` anchors when available"
- Alpha breakdown: "uses `RabcAttribution.anchors`; no multi-year stability claim unless multiple periods exist"
- Tracking error: "may cite benchmark/RABC anchors only to identify relevant index context, not to prove tracking error"

Section 4.2 (Fixed Markdown formats): Concrete bullet templates showing exactly what renders for each segment, with `数据不足` for unavailable data.

Slice 2 step 6: "benchmark anchors cannot be used as evidence for index constituents or methodology" + "tracking error remains `数据不足` until a dedicated extractor or calculation input exists"

Acceptance criterion 12: "benchmark anchors do not prove constituents/methodology, and tracking error remains `数据不足` until data exists"

**Assessment**: Fully resolved. The evidence strategy is now unambiguous for all 4 segments. The fixed Markdown formats in section 4.2 leave no room for implementor interpretation.

---

### Finding 4: docs/implementation-control.md update scope — RESOLVED

**Was**: LOW — non-goal "不改 `docs/implementation-control.md`" conflicted with phaseflow status tracking needs.

**Now**: Stop conditions (section 9) adds: "`docs/implementation-control.md` remains outside implementation scope for this specialist slice; it may only be updated later by the controller as phaseflow bookkeeping after plan/code acceptance, not by the implementation agent."

**Assessment**: Fully resolved. The revised wording clarifies that the non-goal applies to the implementation agent, not to the controller's phaseflow bookkeeping. This is the correct separation of concerns.

---

## New Elements in Revised Plan

The revised plan introduces several elements not in the original:

1. **`TemplateItemRuleAuditContext`**: A new `Literal["identity_missing", "identity_present"]` type shared between renderer and audit. This is a clean addition that resolves Finding 1 and improves the audit's ability to distinguish between "no identity" and "identity present but decisions missing."

2. **Fixed Markdown formats**: Section 4.2 now includes concrete `#### heading` + `- key：value。` bullet templates for all 4 segments. This removes implementor ambiguity about segment structure.

3. **Deterministic segment constraint**: "Segment Markdown must be deterministic: each segment is a heading followed by a fixed ordered set of `- key：value。` bullets, with no free prose paragraphs." This is a good constraint that prevents the renderer from introducing non-deterministic content.

4. **Per-chapter block audit**: "Audit must match `decision.chapter_id` to the corresponding `RenderedChapterBlock` and inspect only that block's `body_markdown`" — this is more precise than the original plan's global markdown scan approach.

5. **Edge case for identity-present-decisions-missing**: Section 6 now explicitly lists "Identity present but decisions missing" as a separate edge case with C2 fail behavior.

All new elements are architecturally sound and consistent with the deterministic MVP boundaries.

---

## Severity Matrix (updated)

| # | Finding | Initial severity | Resolution | Current status |
|---|---|---|---|---|
| 1 | Fail-closed check scope contradiction | HIGH | `TemplateItemRuleAuditContext` field | RESOLVED |
| 2 | Missing fund type test coverage | MEDIUM | enhanced_index + bond_fund required | RESOLVED |
| 3 | Evidence anchoring ambiguity | MEDIUM | Per-segment evidence strategy + fixed formats | RESOLVED |
| 4 | Control doc update scope | LOW | Stop conditions clarification | RESOLVED |

---

## Recommendation

**PASS**. All 4 findings from the initial review are resolved. The revised plan is ready for implementation.

The `TemplateItemRuleAuditContext` approach is a better solution than either of my suggested fixes for Finding 1 — it carries semantic meaning, integrates cleanly with the existing missing-data path, and provides a clear default that avoids mass fixture churn.
