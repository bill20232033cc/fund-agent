# Gate C First Report-Quality Improvement Slice Plan Re-Review — AgentGLM

> Date: 2026-05-26
> Reviewer: AgentGLM
> Review type: Targeted re-review (read-only, no source/test/README/control-doc modification, no commit/push/PR)
> Target: `docs/reviews/release-maintenance-first-report-quality-improvement-slice-plan-20260526.md` (patched version)
> Prior GLM review: `docs/reviews/release-maintenance-first-report-quality-improvement-slice-plan-review-glm-20260526.md`
> MiMo review: `docs/reviews/release-maintenance-first-report-quality-improvement-slice-plan-review-mimo-20260526.md`

## Verdict

**PASS_WITH_FINDINGS**

All MiMo material findings (F1-F4) are closed by the patched plan's new "Exact Wording And Route Decisions" section. One new informational finding (F6) identified. No blocker or material issues remain.

## MiMo Material Finding Closure Table

| MiMo Finding | Severity | Issue | Patched plan change | Closure |
|---|---|---|---|---|
| F1 | Material | Plan specifies intent but not exact contract wording strings | New section "Exact Wording And Route Decisions" provides exact Chinese strings for 2 modified `must_answer`, 1 new `must_not_cover`, 1 new `required_output_items`, plus exact data-gap wording extending the validated anchor `当前 slice 未复核换手率，不能据此判断风格稳定` | **CLOSED** |
| F2 | Material | Audit coverage route for new must_not_cover is underspecified ("likely narrative_guidance" but not committed) | Plan now commits: "Add one `ContractMustNotCoverCoverageRule` to `_MUST_NOT_COVER_COVERAGE_RULES` with `coverage_kind='narrative_guidance'`" and explicitly says "Do not use `ContractForbiddenContentRule`" with rationale | **CLOSED** |
| F3 | Material | must_answer / required_output_items coverage route update is vague (modify vs add unclear) | Plan now specifies: modify 2 existing `must_answer` (with exact old/new strings), add 1 new `must_not_cover`, add 1 new `required_output_items`. Coverage route updates explicitly list which `ContractMustAnswerCoverageRule.question_text` values change and how the routes expand. | **CLOSED** |
| F4 | Minor | Dual truth-source sync protocol not operationalized (which is authoritative?) | Plan now specifies mandatory update order: (1) `docs/fund-analysis-template-draft.md` first as human truth, (2) mirror into `contracts.py` as machine truth, (3) update `contract_rules.py` coverage routes to match. Step 2 in Code-Generation-Ready Steps also reflects this order. | **CLOSED** |
| F5 | Minor | `docs/design.md` update decision is ambiguous | Unchanged. Plan still says "Only update if the implementation changes template structure or accepted design truth." MiMo recommended recording justification in implementation artifact if skipped, which is acceptable. | **ACCEPTED AS-IS** |

## Prior GLM Findings Status

| GLM Finding | Severity | Status in patched plan |
|---|---|---|
| F1 (ReportDataGapOverride no structured next-validation-question field) | Informational | Plan now provides exact composed wording string that embeds both insufficiency and next-validation-question in `required_report_wording`. Explicitly says: "Do not add a separate next-validation-question field unless the existing `required_report_wording` path demonstrably cannot carry the wording." **Tracked and closed.** |
| F2 (Existing data-gap test does not assert projected required_report_wording) | Informational | Plan Step 5 says: "Use the exact required wording from `Exact Wording And Route Decisions`" and "assert it is preserved in the projected data-gap output." **Tracked and closed.** |
| F3 (English contract intent, Chinese wording delegated) | Informational | Patched plan provides exact Chinese strings. **Resolved by MiMo F1 closure.** |
| F4 (Provenance wording for quasi-real evidence) | Informational | Unchanged. Non-blocking for contract-wording gate. **No action needed.** |

## New Finding

### F6 — Informational: Adding `ContractRequiredItemRule` may cause runtime audit failure against current renderer output

**Observation:** The plan adds a new `ContractRequiredItemRule` for Chapter 3 with markers `("换手率/风格变化证据缺口说明：", "下一步最小验证问题：")`. This rule is loaded by `load_programmatic_contract_rules()` and checked against rendered chapter text by `run_programmatic_audit()`. The current renderer does not emit these markers.

If the `covered_by_required_item` coverage route for the modified `must_answer` entries uses AND semantics (both "言行一致性判断" AND "换手率/风格变化证据缺口说明与下一步最小验证问题" must be present), then the runtime audit would detect a missing required item for Chapter 3 in current renderer output. This would cause `fund-analysis analyze` to fail with a P2 audit error after this change is merged, which would be a product behavior change.

The plan says "Explicitly out of scope: default `fund-analysis analyze` / `fund-analysis checklist` behavior" and "Renderer still may not emit the new wording in current product reports until a later renderer/report-writing gate." But adding a `ContractRequiredItemRule` that the current renderer cannot satisfy would affect the default analyze audit behavior.

Additionally, the `ContractRequiredItemRule` does not have a fund-type filter. If applied to Chapter 3 unconditionally, it would affect all fund types, not just `active_fund`. For non-active funds where the data-gap override doesn't apply, the audit would still check for the new markers.

**Assessment:** The plan's stop condition ("The implementation needs to change renderer output to make the contract meaningful") would likely catch this during implementation. However, the plan does not explicitly acknowledge this potential side effect.

**Recommendation:** The implementation agent should verify the `covered_by_required_item` route semantics (AND vs OR for multiple referenced items) and the `ContractRequiredItemRule` runtime audit behavior before adding the rule. If AND semantics apply:

- Option A: Defer the `ContractRequiredItemRule` until the renderer can emit the new markers. In this slice, only add the contract wording, the `narrative_guidance` coverage route for the new `must_not_cover`, and the `ContractMustAnswerCoverageRule` updates that keep the existing route references. Add the `ContractRequiredItemRule` in the future renderer gate.

- Option B: Accept that `fund-analysis analyze` will produce an audit P2 finding for Chapter 3 after this change, explicitly document this as a known product behavior change, and remove "default analyze behavior" from the out-of-scope list.

- Option C: If the audit framework supports fund-type-conditional rules, scope the `ContractRequiredItemRule` to `active_fund` only.

Option A is the safest path and aligns with the plan's stated intent of contract hardening before renderer changes.

## Scope Compliance Verification

| Boundary | Patched plan status | New expansion? |
|---|---|---|
| Renderer (`renderer.py`) | Explicitly out of scope | No |
| FQ0-FQ6 (`quality_gate.py`, `extraction_score.py`) | Explicitly out of scope | No |
| Service/CLI defaults | Explicitly out of scope | No (but see F6) |
| Host/Agent/dayu | Explicitly out of scope | No |
| Durable baseline / fixtures | Explicitly out of scope | No |
| Production extraction / `FundDocumentRepository` | Explicitly out of scope | No |
| PDF/cache/source helpers | Explicitly out of scope | No |
| Default analyze/checklist behavior | Explicitly out of scope | No (but see F6) |

The patched plan does not introduce new files to the allowed list, does not expand the implementation scope beyond the original plan, and does not remove any items from the out-of-scope list. The boundary check commands and stop conditions are unchanged. No new scope expansion detected.

## Exact Wording Quality Check

The patched plan's exact Chinese strings are internally consistent:

| String | Preserves validated anchor? | Scopes to active_fund? | Internally consistent? |
|---|---|---|---|
| `must_answer` modify 1: `言行一致性判断：说的和做的一样吗？主动基金如缺少已复核的换手率或风格变化证据，不得据此判断言行一致。` | Extends anchor pattern | Yes — "主动基金" | Yes — conditional clause correctly scoped |
| `must_answer` modify 2: `风格稳定性判断：跨期风格是否漂移？主动基金必须基于已复核的换手率或风格变化证据。` | Consistent with anchor | Yes — "主动基金" | Yes — evidence precondition correctly scoped |
| `must_not_cover` add: `不在换手率或风格变化证据缺失、不可用、未复核时，推断主动基金风格稳定、风格一致或言行一致。` | Consistent | Yes — "主动基金" | Yes — prohibition covers all three claim types |
| `required_output_items` add: `换手率/风格变化证据缺口说明与下一步最小验证问题` | Consistent | Implicit — only triggered when evidence gap exists | Yes |
| Data-gap wording: `当前 slice 未复核换手率，不能据此判断风格稳定、风格一致或言行一致；下一步最小验证问题：复核年报§8换手率及跨期行业配置/持仓集中度变化后，风格稳定性和言行一致性判断是否仍成立？` | Extends anchor `当前 slice 未复核换手率，不能据此判断风格稳定` | N/A — runtime wording | Yes — extends anchor to cover style-consistency and next-validation-question |

The wording correctly:
1. Preserves the validated anchor from `test_report_evidence.py:277`
2. Extends it narrowly to cover style-consistency and speech-act consistency (言行一致)
3. Adds a concrete next-validation-question referencing annual report §8
4. Scopes conditional clauses to "主动基金" in the `must_answer` entries

## Residual Risks

| Risk | Severity | Status | Assessment |
|---|---|---|---|
| Wording-only contract does not change real report output | Informational | Unchanged from original plan | Adequate — correct sequencing |
| `ContractRequiredItemRule` may cause runtime audit failure (F6) | Informational | New finding | Implementation agent should verify AND/OR semantics and adjust if needed |
| Exact Chinese string changes break audit coverage counts | Informational | Unchanged | Adequate — same-gate alignment |
| `ReportDataGapOverride` may need schema extension | Informational | Resolved by composed wording string | Adequate |
| Contract wording becomes too broad | Informational | Unchanged | Adequate — scope constrained |

## Controller Recommendation

Accept the patched plan. All MiMo material findings (F1-F4) are closed. The patched plan's "Exact Wording And Route Decisions" section provides:

1. **Exact Chinese strings** for all contract modifications (MiMo F1 closed)
2. **Committed audit route** (`narrative_guidance` in `_MUST_NOT_COVER_COVERAGE_RULES`) (MiMo F2 closed)
3. **Explicit modify/add decisions** with old/new string mapping (MiMo F3 closed)
4. **Mandatory template-draft-first update order** (MiMo F4 closed)

One new informational finding (F6) should be tracked by the implementation agent: verify `covered_by_required_item` AND/OR semantics and `ContractRequiredItemRule` runtime audit behavior before adding the new required item rule. If AND semantics apply, defer the `ContractRequiredItemRule` to the future renderer gate (Option A).

## Validation

Read-only documents reviewed:

```text
docs/reviews/release-maintenance-first-report-quality-improvement-slice-plan-20260526.md (patched)
docs/reviews/release-maintenance-first-report-quality-improvement-slice-plan-review-glm-20260526.md
docs/reviews/release-maintenance-first-report-quality-improvement-slice-plan-review-mimo-20260526.md
```

No source, test, README, control-doc, renderer, FQ0-FQ6, Service/CLI, Host/Agent/dayu, fixture, tracked report, commit, push, PR, or destructive git operation was performed.
