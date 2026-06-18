# Provider/LLM Chapter 2 L1 Deterministic Gap Rendering Plan

Date: 2026-06-14

Role: AgentCodex planning worker, not controller

Gate: `Provider/LLM Chapter 2 L1 Deterministic Gap Rendering Planning Gate`

Recommended next gate: `Provider/LLM Chapter 2 L1 Deterministic Gap Rendering No-live Implementation Gate`

Release/readiness: `NOT_READY`

## 1. Scope and Non-goals

This plan defines a code-generation-ready, no-live implementation route for Chapter 2 `l1_numerical_closure` when same-source typed evidence is absent or insufficient: render explicit evidence-gap / minimum-verification wording instead of unsupported R/A/B/C/A-C percentages or opaque `repair_budget_exhausted`.

Scope is limited to template 第 2 章 `R=A+B-C 收益归因` required-output behavior backed by existing `EvidenceAvailability` statuses and existing writer/auditor/orchestrator mechanics. The behavior is not generalized to all L1 subcategories.

In-scope product decision:

- If Chapter 2 required-output facts are `missing`, `unavailable`, `unreviewed` or `not_applicable`, the writer may emit an explicit evidence gap or minimum verification question under the exact required-output marker.
- If Chapter 2 facts are `available` with same-source fact/anchor ids and the LLM ignores them or emits unanchored numeric closure, keep current L1 fail-closed behavior. Do not convert that case into a product evidence gap.

Non-goals:

- No implementation in this planning gate.
- Do not weaken L1, downgrade it to warn, or accept unsupported concrete percentages.
- Do not change `max_repair_attempts`; repair budget interaction is out of scope for implementation except for proving the current one-repair behavior is preserved.
- Do not change provider defaults, model selection, timeout, output budget, prompt payload mode, annual-period LLM route, Docling/parser policy, source policy or fallback policy.
- Do not introduce Eastmoney, fund-company, CNINFO or any non-EID fallback.
- Do not run live/provider/LLM/network/PDF/FDR/source/analyze/checklist/readiness/release commands.
- Do not read report bodies, prompt bodies, provider request/response payloads, PDF/source/cache bodies, source bodies or final report body.
- Do not update `docs/design.md`, `docs/current-startup-packet.md`, `docs/implementation-control.md`, root README, release/readiness state, PR state, staging, commit, push or merge.

## 2. Evidence Reviewed

| Evidence | Use |
|---|---|
| `AGENTS.md` | Execution truth, fail-closed posture, EID single-source/no-fallback, module boundaries and template/audit constraints. |
| `docs/current-startup-packet.md` | Confirms active gate, binding amendments and `NOT_READY`. |
| `docs/implementation-control.md` | Confirms standard planning-only gate, Route C fail-closed boundaries, current one-repair default and no source/provider/readiness authorization. |
| `docs/design.md` relevant Route C / Host-Agent / LLM fail-closed sections | Confirms `--use-llm` is explicit opt-in, Service -> Host -> Agent boundary, no deterministic full-report fallback, and repair budget/runtime expansion remain future gates. |
| `docs/reviews/provider-llm-chapter2-l1-live-persistent-failure-disposition-plan-controller-judgment-20260614.md` | Binding controller amendments for this gate. |
| `docs/reviews/provider-llm-chapter2-l1-live-persistent-failure-disposition-plan-20260614.md` | Accepted disposition basis and rejected/deferred alternatives. |
| `docs/reviews/provider-llm-chapter2-l1-live-persistent-failure-disposition-plan-review-ds-20260614.md` | DS findings on fact-absence vs ignored facts, mock/stub specificity and auditor/repair alignment. |
| `docs/reviews/provider-llm-chapter2-l1-live-persistent-failure-disposition-plan-review-mimo-20260614.md` | MiMo findings on validation concreteness, repair budget scope, product direction and L1 subcategory scope. |
| `docs/fund-analysis-template-draft.md` Ch2 required-output block | Current canonical Ch2 required-output items all use `when_evidence_missing="block"`. |
| `fund_agent/fund/evidence_availability.py` | Ch2 required-output facts are already mapped to `structured.nav_benchmark_performance` and `structured.fee_schedule`; statuses are `available`, `missing`, `unavailable`, `not_applicable`, `unreviewed`. |
| `fund_agent/fund/chapter_writer.py` | Existing typed writer supports `render_evidence_gap` and `render_minimum_verification_question`; missing `EvidenceAvailability` envelope remains fail-closed. |
| `fund_agent/fund/chapter_auditor.py` | Existing L1 numerical closure audit blocks concrete unanchored R/A/B/C/A-C percentages and permits safe no-percentage gap/minimum-verification wording. |
| `fund_agent/services/chapter_orchestrator.py` and `fund_agent/agent/runner.py` | Existing Service and Agent paths preserve attempt ledgers, repair context, `repair_budget_exhausted`, `prompt_contract`, and `l1_numerical_closure` diagnostics. |
| Existing no-live tests under `tests/fund/`, `tests/services/`, `tests/agent/` | Determine exact implementation validation targets and fixture/stub layers. |

No forbidden body/payload/live/source reads were used.

## 3. Accepted Facts and Residual Ambiguity

Accepted facts:

- Exact `004393 / 2025` post-strengthening live evidence still first-fails Chapter 2 with `repair_budget_exhausted` / `prompt_contract` / `l1_numerical_closure`.
- No-live evidence proves checklist propagation and current L1 fail-closed behavior.
- Narrow prompt strengthening was accepted; `_repair_context_prompt()` and repair budget were unchanged.
- The post-strengthening live failure is not an implementation acceptance failure for the accepted no-live prompt contract.
- Ch2 required-output availability is already modeled through same-source `EvidenceAvailability`.
- Ch2 current template policy blocks all seven required-output items when evidence is missing.
- Ch3 already uses the accepted pattern where typed missing evidence can render an evidence gap while unsafe wording still blocks final assembly.

Residual ambiguity:

- Under current no-live/read-boundary constraints, this plan cannot prove whether the live sample had absent/insufficient Ch2 facts or present facts ignored by the LLM.
- The implementation must therefore use only typed availability as the deterministic discriminator. `available` facts with anchors mean present-but-ignored or unsupported writer output remains a prompt-contract failure. Missing or insufficient availability can render a constrained evidence gap / minimum verification question.
- Product wording must not say "the annual report lacks the fact" unless the typed availability status and safe gap metadata prove that specific absence. Default wording should say "当前同源已复核证据不足/未复核/不可用，不能完成具体 R=A+B-C 数字闭环".

## 4. Proposed Product Semantics

For Chapter 2 only:

| Item group | Required-output ids | Proposed missing-evidence behavior | User-visible semantics |
|---|---|---|---|
| Direct performance evidence | `ch2.required_output.item_01`, `ch2.required_output.item_02` | `render_evidence_gap` | Keep exact marker; state reviewed same-source performance/benchmark evidence is insufficient; do not invent 1/3/5-year values. |
| Derived excess-return judgment | `ch2.required_output.item_03`, `ch2.required_output.item_04` | `render_minimum_verification_question` | Keep exact marker; ask the minimum verification question needed to compare R and B before Alpha/stability/structural-vs-stage judgment. |
| Cost evidence and judgment | `ch2.required_output.item_05`, `ch2.required_output.item_06` | `render_evidence_gap` | Keep exact marker; state reviewed same-source fee/cost evidence is insufficient; do not invent fee or cost reasonableness. |
| R=A+B-C synthesis | `ch2.required_output.item_07` | `render_minimum_verification_question` | Keep exact marker; ask the minimum verification question for same-source R/B/cost support; do not output concrete Alpha/Beta/Cost closure. |

Auditor semantics:

- Safe gap/minimum-verification output without concrete percentages should pass L1.
- Any concrete unanchored `R=A+B-C`, `A=R-B`, `A-C`, Alpha/Beta/Cost/% closure still triggers L1, including inside "数据不足" wording.
- If same-source facts are `available`, the implementation must not auto-gap-render the chapter to hide writer noncompliance.

Repair budget semantics:

- `max_repair_attempts` remains unchanged.
- Tests must prove no implementation path increases writer request count beyond the existing policy for the tested scenario.
- Repair budget calibration remains a separate future standard gate.

## 5. Implementation Boundary and Allowed File Set

Allowed write set for the next implementation gate:

| Path | Allowed change |
|---|---|
| `docs/fund-analysis-template-draft.md` | Change only the seven Chapter 2 required-output `when_evidence_missing` values and missing-evidence reasons per Section 4. Do not change item ids, order, text, must-answer, must-not-cover, preferred lens, chapter ids or other chapters. |
| `tests/fund/template/test_typed_contracts.py` | Add/adjust assertions that canonical typed Ch2 required-output missing behavior matches Section 4 and Ch3 behavior remains unchanged. |
| `tests/fund/test_chapter_writer.py` | Replace the current Ch2 hard-block expectation with positive gap/minimum-verification writer tests and a negative missing-envelope fail-closed test. |
| `tests/fund/test_chapter_auditor.py` | Add/keep L1 positive and negative assertions for Ch2 safe gap/minimum-verification wording and concrete unanchored percentages. |
| `tests/services/test_chapter_orchestrator.py` | Add Service orchestrator tests for Ch2 missing-evidence accepted gap path, present-but-ignored facts still failing as `l1_numerical_closure`, and repair budget unchanged. |
| `tests/agent/test_runner.py` | Add Agent runner tests for Ch2 positive gap rendering and unsafe Ch2 output blocking with no final assembly readiness. |
| `tests/services/test_fund_analysis_service_llm.py` | Add Service hosted/final-assembly positive and negative no-live tests for Chapter 2 gap behavior under fake provider clients. |
| `tests/README.md` | Conditional only if current test-surface descriptions become false after the test changes. No broad documentation update. |

Conditional source write set:

- No production Python source change is expected. Existing writer/auditor/orchestrator/Agent mechanics already support the needed enum behavior and L1 audit. If an implementation worker proves a source gap, it must stop and return to controller unless the gap is a narrow defect in `fund_agent/fund/chapter_writer.py`, `fund_agent/fund/chapter_auditor.py`, `fund_agent/services/chapter_orchestrator.py`, `fund_agent/agent/runner.py` or `fund_agent/agent/repair.py` directly required by this plan.

Forbidden write set:

- `docs/design.md`, `docs/current-startup-packet.md`, `docs/implementation-control.md`, root `README.md`, source acquisition, provider config/defaults, Host lifecycle, source/FDR/PDF/cache, annual-period LLM route, Docling/parser policy, release/readiness/PR artifacts.

## 6. Concrete Validation Matrix with exact test files, fixture or stub approach, and expected assertions

| ID | File | Fixture or stub layer | Test intent | Expected assertions |
|---|---|---|---|---|
| V1 | `tests/fund/template/test_typed_contracts.py` | Canonical template JSON projection only | Prove Ch2 policy changed exactly as planned. | `item_01`, `item_02`, `item_05`, `item_06` have `when_evidence_missing == "render_evidence_gap"`; `item_03`, `item_04`, `item_07` have `when_evidence_missing == "render_minimum_verification_question"`; ids/text/order unchanged; Ch3 assertions unchanged. |
| V2 | `tests/fund/test_chapter_writer.py` | `_bundle()` with `nav_benchmark_performance=ExtractedField(value=None, anchors=(), extraction_mode="missing", note="fixture missing")`; `_FakeChapterLLMClient` returns exact required marker plus safe gap wording | Direct Ch2 performance fact absence renders an accepted evidence gap instead of pre-provider block. | `write_chapter()` returns `status == "drafted"`, `stop_reason == "none"`, draft includes `<!-- required_output:ch2.required_output.item_01 -->`, includes `证据不足` or `数据不足`, and client was called once. |
| V3 | `tests/fund/test_chapter_writer.py` | `_bundle()` with missing `fee_schedule`; `_FakeChapterLLMClient` returns exact item 07 marker plus "下一步最小验证问题" and no concrete percentages | Ch2 composite R=A+B-C synthesis missing evidence renders minimum-verification wording. | Draft includes `<!-- required_output:ch2.required_output.item_07 -->`, includes `下一步最小验证问题`, contains no unsupported concrete percent closure, `stop_reason == "none"`. |
| V4 | `tests/fund/test_chapter_writer.py` | Typed required-output items passed but `evidence_availability=None` | Missing availability envelope remains contract failure, not evidence gap. | `build_chapter_prompt()` or `write_chapter()` raises `ValueError` matching `EvidenceAvailability`; provider client not used. |
| V5 | `tests/fund/test_chapter_writer.py` | Missing Ch2 evidence with fake writer omitting required gap/min-verification phrase | Unsafe gap output blocks after writer-output validation. | `result.status == "blocked"`, `stop_reason == "missing_required_output_marker"`, issue id starts with `writer:required_output_gap_missing:` or `writer:required_output_verification_missing:`, and not old `writer:required_output_block:`. |
| V6 | `tests/fund/test_chapter_auditor.py` | Existing `_audit_input()` helper with Ch2 suffix | Safe Ch2 gap/minimum-verification wording without concrete percentages passes L1. | No issue with `rule_code == "L1"`. |
| V7 | `tests/fund/test_chapter_auditor.py` | Existing `_audit_input()` helper with "数据不足，但 A=R-B 因此 Alpha 为 2.10%" | Gap wording cannot wrap unsupported concrete numeric closure. | `result.status == "fail"` and at least one `rule_code == "L1"`. |
| V8 | `tests/services/test_chapter_orchestrator.py` | `_orchestrate()` with typed template path, Ch2 projection missing `nav_benchmark_performance`; `_FakeChapterLLMClient` returns safe Ch2 required-output gap/min-verification text; `_FakeAuditLLMClient` default pass | Service orchestrator accepts Ch2 fact-absence gap path without changing repair budget. | Chapter 2 `run.status == "accepted"`, `stop_reason == "none"`, `failure_subcategory is None`, writer request count is `1` for no-repair accepted path, policy still uses `max_repair_attempts=1`. |
| V9 | `tests/services/test_chapter_orchestrator.py` | Existing available-facts Ch2 projection; fake writer returns unanchored "A=R-B，因此 Alpha 为 2.10%" on initial and repair attempts | Present-but-ignored facts remain fail-closed and scoped to `l1_numerical_closure`. | Existing or updated test keeps `status == "failed"`, `stop_reason == "repair_budget_exhausted"`, `failure_category == "prompt_contract"`, `failure_subcategory == "l1_numerical_closure"`, and two attempts only. |
| V10 | `tests/services/test_chapter_orchestrator.py` | Repair context fake auditor emitting L1 issue, existing `_FakeChapterLLMClient` two-attempt path | Auditor/repair alignment still tells repair to delete unsupported numeric closure and permits safe gap/min-verification wording. | Repair request has non-null `repair_context`; required corrections mention `第2章 R=A+B-C 数字闭环`, no-anchor concrete percentages, and data-insufficient/minimum verification; no `extra_payload`. |
| V11 | `tests/agent/test_runner.py` | Agent runner with typed template path, projection missing Ch2 nav/cost facts, `_FakeWriter` returns safe gap/min-verification Chapter 2, `_FakeAuditor` pass | Agent layer accepts Ch2 evidence gap under current one-repair policy. | `run.status` accepted or partial only according to targeted chapters; task chapter 2 accepted; `final_assembly_readiness.ready is True` for scoped accepted body; required-output plan action matches Section 4. |
| V12 | `tests/agent/test_runner.py` | Agent runner with missing Ch2 facts but fake writer emits required marker without approved gap phrase or emits concrete unanchored percentage | Unsafe Ch2 gap output remains blocked before final assembly. | `task.status in ("blocked", "failed")`, terminal is prompt-contract blocked/repair exhausted according to current runner mapping, no accepted conclusion, no final assembly readiness. |
| V13 | `tests/services/test_fund_analysis_service_llm.py` | Full fake Route C body run with deterministic fake writer returning safe Ch2 gap/min-verification and accepted other body chapters | Service final assembly can include safe Ch2 gap output without claiming readiness. | Final assembly result includes chapters `0..7` only in fake no-live path; report markdown exists for fake accepted run; no live/provider/network/source command. |
| V14 | `tests/services/test_fund_analysis_service_llm.py` | Same fake Service path but Ch2 unsafe output misses gap/min-verification phrase or emits concrete unanchored percentage | Unsafe Ch2 output keeps final assembly incomplete. | Hosted result is incomplete/fail-closed; report markdown absent; first failed chapter is 2 with `prompt_contract`; no deterministic full-report fallback. |
| V15 | `tests/fund/test_evidence_availability.py` | Existing `_bundle()` replacements only if needed | Prove Ch2 requirement ids remain mapped to same-source structured fields; no fallback/source expansion. | Ch2 required-output requirements still point only to `structured.nav_benchmark_performance` and/or `structured.fee_schedule`; status closed set remains unchanged. |

Required validation commands for the implementation gate:

```bash
uv run pytest tests/fund/template/test_typed_contracts.py tests/fund/test_chapter_writer.py tests/fund/test_chapter_auditor.py tests/services/test_chapter_orchestrator.py tests/agent/test_runner.py tests/services/test_fund_analysis_service_llm.py tests/fund/test_evidence_availability.py -q
uv run ruff check tests/fund/template/test_typed_contracts.py tests/fund/test_chapter_writer.py tests/fund/test_chapter_auditor.py tests/services/test_chapter_orchestrator.py tests/agent/test_runner.py tests/services/test_fund_analysis_service_llm.py tests/fund/test_evidence_availability.py
git diff --check
```

If production source becomes necessary under the conditional source rule, extend ruff to the touched source files and add the exact touched source tests before implementation review.

## 7. Risk and Residual Table

| Risk / residual | Disposition | Owner / next handling |
|---|---|---|
| Gap rendering may mask model noncompliance when facts are present but ignored | Mitigated by scope | Implementation must gate gap rendering on non-`available` typed availability; available-fact L1 failures remain fail-closed. |
| No-live evidence cannot prove the exact live sample's fact availability without forbidden body/source/payload reads | Accepted ambiguity | Product wording must say "current reviewed same-source evidence is insufficient/unreviewed/unavailable" rather than claiming source absence. Future live/body evidence gate may refine. |
| Ch2 template policy change could be broader than `l1_numerical_closure` | Controlled | Limit to Ch2 R=A+B-C required-output ids and tests proving concrete unanchored numeric closure still triggers L1. |
| Auditor accepts unsafe gap wording | Must be tested | V6/V7/V14 require safe wording pass and unsafe percentage block. |
| Repair budget accidentally changes | Out of scope | V8/V9/V10 require request-count and current one-repair semantics; do not change `max_repair_attempts`. |
| Missing `EvidenceAvailability` envelope is degraded to product gap | Forbidden | V4 requires fail-closed `ValueError`; this is contract plumbing failure, not fact absence. |
| Source/fallback policy drift | Forbidden | No FDR/PDF/source/fallback code in write set; V15 and diff review verify same-source requirement ids only. |
| Release/readiness overclaim | Forbidden | Implementation evidence and controller judgment must preserve `NOT_READY`; no readiness/release/PR command. |

## 8. Next Gate Recommendation

Proceed to exactly one next gate:

```text
Provider/LLM Chapter 2 L1 Deterministic Gap Rendering No-live Implementation Gate
```

Gate classification: `standard`.

Allowed write set is Section 5. Required validation commands are Section 6. The implementation worker must stop and return to controller if production source changes are needed beyond the conditional source rule, if a live/source/provider command appears necessary, or if tests show the gap route cannot be scoped to typed fact absence/insufficiency.

## 9. Stop Condition

Stop after writing this artifact.

This planning artifact does not implement code, run tests, run live/provider/source commands, update control/design/startup docs, change readiness/release/PR state, stage, commit, push or merge.

Final planning verdict:

```text
VERDICT: READY_FOR_NO_LIVE_IMPLEMENTATION_GATE_NOT_READY
```
