# Provider/LLM Chapter 3 Item 01 Fact-gap Disposition - MiMo Review

Date: 2026-06-14

Reviewer: AgentMiMo

## 1. Scope

Review target: `docs/reviews/provider-llm-chapter3-item01-fact-gap-disposition-20260614.md`

Review question: Does the target artifact correctly classify Chapter 3 item 01 fact_gap as accepted fail-closed residual and route to required-output policy planning, without overclaiming readiness or implementation authorization?

This review reads only truth/control docs, accepted prior judgments, and safe runtime metadata. Forbidden reads (writer Markdown, auditor feedback, raw prompts, provider payloads/responses, source/cache/PDF bodies, final report body) were not used.

## 2. Evidence Reviewed

Truth/control:

- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/design.md` (Route C and template sections)
- `docs/fund-analysis-template-draft.md` (Chapter 3 item 01 section)

Accepted prior judgments:

- `docs/reviews/provider-llm-chapter3-post-fix-provider-before-valueerror-no-live-root-cause-evidence-controller-judgment-20260614.md`
- `docs/reviews/provider-llm-chapter3-required-output-item01-missing-evidence-no-live-fix-implementation-controller-judgment-20260614.md`
- `docs/reviews/provider-llm-chapter3-item01-post-fix-bounded-live-re-evidence-controller-judgment-20260614.md`
- `docs/reviews/provider-llm-chapter2-l1-post-fix-bounded-live-re-evidence-controller-judgment-20260614.md`

Safe runtime metadata:

- `reports/llm-runs/004393-2025-20260613T201900Z-host_run_4a531cbe94604e4/manifest.json`
- `reports/llm-runs/004393-2025-20260613T201900Z-host_run_4a531cbe94604e4/summary.json`
- `reports/llm-runs/004393-2025-20260613T201900Z-host_run_4a531cbe94604e4/chapters/chapter-03.json`

## 3. Findings

### F1 [LOW] Verdict format non-standard

The artifact's final verdict is `ACCEPT_AS_FAIL_CLOSED_RESIDUAL_READY_FOR_REQUIRED_OUTPUT_POLICY_PLANNING_GATE_NOT_READY`. The gate classification in `docs/current-startup-packet.md` is `standard`, and prior gates in this chain use verdicts like `ACCEPT_LIVE_CHAPTER2_L1_FIX_CONFIRMED_CHAPTER3_FACT_GAP_NOT_READY` or `ACCEPT_ROOT_CAUSE_PROVEN_READY_FOR_NO_LIVE_FIX_IMPLEMENTATION_GATE_NOT_READY`. The disposition verdict is readable and internally consistent, but deviates from the `PASS` / `PASS_WITH_FINDINGS` / `FAIL` structure specified in the review instructions. This is a presentation-level deviation, not a correctness issue; the verdict's semantic content is accurate.

### F2 [LOW] Scope statement slightly over-broad

Section 1 scope says "does not... change source policy, provider defaults, repair budget, annual-period LLM route, Docling/parser policy, fallback policy or release state." The annual-period LLM route and Docling/parser policy are not in scope for this gate at all (they are future design gates), so mentioning them in the "does not change" list is technically correct but could be read as implying they were considered. Minor clarity issue only.

### F3 [INFO] Broader ch3 required-output items not explicitly scoped

The disposition correctly focuses on item 01 as the current proven blocker. However, the template declares five other ch3 required_output items (item_02 through item_06) with `when_evidence_missing` set to `render_evidence_gap` or `render_minimum_verification_question`. The disposition defers "broader typed required-output null/missing behavior audit" to a residual, which is the correct scoping decision. No finding against the artifact; this is noted for the policy planning gate's awareness.

## 4. Accepted Points

1. **Classification as fail-closed residual**: Correct. The five-point rationale in section 4 is logically sound and directly supported by the accepted evidence chain. The old `ValueError`/`code_bug` path is fixed; the current `missing_required_facts`/`fact_gap` is the explicit template policy for `ch3.required_output.item_01` with `when_evidence_missing="block"`.

2. **Template truth fact**: Verified against `docs/fund-analysis-template-draft.md`. Chapter 3 item 01 currently declares `when_evidence_missing: "block"` and `missing_evidence_reason: "第 3 章基金经理基本信息缺少已复核证据时不能进入基金经理画像写作。"`.

3. **Runtime metadata facts**: All metadata claims verified against `summary.json` and `chapters/chapter-03.json`:
   - `status=blocked` (chapter-03.json line 118: `"status": "blocked"`)
   - `stop_reason=missing_required_facts` (chapter-03.json line 119: `"stop_reason": "missing_required_facts"`)
   - `failure_category=fact_gap` (chapter-03.json line 107: `"failure_category": "fact_gap"`)
   - Issue string `3:missing_required_facts:writer:required_output_block:ch3.required_output.item_01` (chapter-03.json line 111)
   - `orchestration_status=partial` (manifest.json line 17: `"orchestration_status": "partial"`)
   - `final_assembly_status=incomplete` (manifest.json line 14: `"final_assembly_status": "incomplete"`)
   - `accepted_conclusion_present=false` (chapter-03.json line 4)

4. **Chapter 2 accepted claim**: Verified. `summary.json` chapter_matrix shows Chapter 2 with `status: "accepted"` and `stop_reason: "none"`. First failed chapter is Chapter 3 (`first_failed.chapter_id: 3`).

5. **Rejection of source fallback**: Correctly rejects Eastmoney/fund-company/CNINFO expansion based on AGENTS.md EID single-source/no-fallback constraint.

6. **Rejection of readiness/release claims**: Correctly preserves `NOT_READY` throughout. No overclaiming observed.

7. **Routing to policy planning**: The `Provider/LLM Chapter 3 Required-output Policy Planning Gate` routing is appropriate. The item 01 fact-gap is a product policy question (should it remain hard block, degrade to evidence-gap rendering, or produce minimum verification question), not a code bug.

8. **Residuals table**: Accurately identifies six residuals with correct owners and next gates. The policy question about evidence-gap degradation is properly scoped as a policy candidate, not an implementation directive.

9. **Forbidden reads respected**: The artifact and this review did not read writer Markdown, auditor feedback, raw prompts, provider payloads/responses, source/cache/PDF bodies, or final report body.

## 5. Residuals

| Residual | Severity | Note |
| --- | --- | --- |
| Verdict format non-standard for gate classification | LOW | Does not affect correctness; semantic content is accurate |
| Scope statement mentions future design items not in gate scope | LOW | Correct but slightly over-broad; no behavioral impact |

## 6. Verdict

**PASS_WITH_FINDINGS**

The target artifact correctly classifies Chapter 3 item 01 fact_gap as accepted fail-closed residual and routes to required-output policy planning. All runtime metadata claims are verified against safe metadata. No readiness or implementation authorization overclaiming detected. The two low-severity findings are presentation-level only and do not affect the disposition's correctness or safety.

The disposition decision `ACCEPT_AS_FAIL_CLOSED_RESIDUAL_AND_ROUTE_TO_POLICY_PLANNING` is accepted. Release/readiness remains `NOT_READY`.
