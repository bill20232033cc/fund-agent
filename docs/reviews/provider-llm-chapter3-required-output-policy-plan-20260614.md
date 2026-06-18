# Provider/LLM Chapter 3 Required-output Policy Plan

Date: 2026-06-14

## 1. Scope

Gate: `Provider/LLM Chapter 3 Required-output Policy Planning Gate`.

Role: AgentCodex planning worker only. This artifact is a code-generation-ready plan for the current Chapter 3 item 01 fact-gap blocker. It does not implement code, change tests, update control docs, run live/provider/network/source/PDF/FDR/analyze/checklist/readiness/release/PR commands, or change EID source policy.

Decision target:

- `ch3.required_output.item_01` currently blocks when fund manager basic information lacks reviewed evidence.
- The planning question is whether this should remain hard block, degrade to evidence-gap rendering, or emit a minimum verification question.
- Release/readiness remains `NOT_READY`.
- EID remains single-source/no-fallback.

Preflight:

- Branch observed: `feat/mvp-llm-incomplete-run-artifacts`.
- Worktree already had unrelated modified/untracked files before this artifact. This plan writes only `docs/reviews/provider-llm-chapter3-required-output-policy-plan-20260614.md`.

## 2. Evidence Reviewed

Truth and control:

- `AGENTS.md`: module boundary, EID single-source/no-fallback, Route C fail-closed, no direct PDF/source helper access, and `NOT_READY` conservatism.
- `docs/current-startup-packet.md`: active gate is `Provider/LLM Chapter 3 Required-output Policy Planning Gate`; planning must decide hard block vs evidence-gap rendering vs minimum verification question while preserving `NOT_READY`.
- `docs/implementation-control.md`: current gate and accepted checkpoint chain:
  - Chapter 3 item 01 no-live fix checkpoint `6cd5ac5`.
  - Chapter 3 item 01 post-fix live evidence checkpoint `6fc7f2b`.
  - Chapter 2 L1 post-fix bounded live evidence checkpoint `765c616`.
  - Chapter 3 item 01 fact-gap disposition checkpoint `62c7a2e`.
- `docs/design.md` relevant Route C / typed template / final assembly sections:
  - `docs/fund-analysis-template-draft.md` canonical JSON is the authored template contract truth source.
  - `RequiredOutputItem.when_evidence_missing` drives typed writer behavior.
  - Fund writer/auditor primitives do not read source/PDF/provider env directly.
  - Service final assembly only consumes accepted chapters/conclusions and does not backfill blocked body chapters.
- `docs/fund-analysis-template-draft.md` Chapter 3 `required_output_items`:
  - `item_01` = `基金经理基本信息`, currently `when_evidence_missing="block"`.
  - `item_02` to `item_05` already use `render_evidence_gap`.
  - `item_06` uses `render_minimum_verification_question`.
- `docs/reviews/provider-llm-chapter3-item01-fact-gap-disposition-controller-judgment-20260614.md`:
  - current Chapter 3 issue is `3:missing_required_facts:writer:required_output_block:ch3.required_output.item_01`;
  - `stop_reason=missing_required_facts`;
  - `failure_category=fact_gap`;
  - Chapter 3 is the first failed chapter after Chapter 2 L1 was accepted;
  - `final_assembly_status=incomplete`;
  - this is accepted intentional fail-closed residual, not a current code bug.

Narrow code/test evidence reviewed for code-generation readiness:

- `fund_agent/fund/chapter_writer.py`
  - `RequiredOutputEvidencePlan.action` supports `render`, `render_evidence_gap`, `render_minimum_verification_question`, `delete`, `block`.
  - `_required_output_action()` maps missing evidence to the template `when_evidence_missing` behavior.
  - `_required_output_preflight_issues()` only blocks items whose computed action is `block`.
  - `_required_output_degrade_issues()` checks post-writer output for required evidence-gap or minimum-verification wording.
- `fund_agent/fund/evidence_availability.py`
  - `ch3.required_output.item_01` is mapped to `structured.basic_identity` and `structured.portfolio_managers`.
- `fund_agent/agent/runner.py`
  - `_final_readiness()` marks final assembly readiness false for any non-accepted body chapter.
- `fund_agent/services/final_chapter_assembler.py`
  - `_validate_orchestration()` and `_build_final_assembly_readiness()` require chapters 1-6 to be accepted with accepted draft/conclusion before full final assembly.
- Current tests:
  - `tests/fund/template/test_typed_contracts.py::test_chapter_3_basic_manager_info_missing_behavior_blocks`
  - `tests/fund/test_evidence_availability.py::test_ch3_basic_manager_info_required_output_uses_basic_identity_availability`
  - `tests/agent/test_runner.py::test_chapter_3_missing_basic_manager_info_blocks_before_provider`
  - `tests/services/test_fund_analysis_service_llm.py::test_partial_llm_result_does_not_fallback_to_deterministic_after_typed_readiness`

No writer markdown, auditor markdown, raw prompts, provider payload/response, source/cache/PDF body, final report body, live/provider/network/FDR/analyze/checklist/readiness/release/PR command was read or run.

## 3. Current Accepted Facts

- The current blocker is not the old provider-before `ValueError` / `code_bug`; that path was fixed and dispositioned as historical.
- Current Chapter 3 item 01 behavior is policy-driven: the canonical template declares `when_evidence_missing="block"`.
- Current safe runtime metadata shows Chapter 3 fails as `missing_required_facts` / `fact_gap`, with the explicit issue `required_output_block:ch3.required_output.item_01`.
- Chapter 2 L1 is accepted in the relevant post-fix bounded live metadata; the first failed chapter is now Chapter 3 item 01 fact-gap.
- Current Route C remains explicit opt-in, provider-backed, and fail-closed.
- Current deterministic `analyze/checklist` and deterministic `analyze-annual-period` are not changed by this gate.
- Current `analyze-annual-period` is not an LLM chapter-writing route.
- Current repair budget remains one regenerate attempt per chapter and is not product-calibrated.
- Final assembly remains incomplete unless every required body chapter 1-6 is accepted and has accepted draft/conclusion.
- EID annual-report source policy remains single-source/no-fallback.
- Release/readiness remains `NOT_READY`.

## 4. Policy Options Considered

### Option A: Keep `block`

Meaning:

- Keep `ch3.required_output.item_01` as hard fail-closed when basic manager information lacks reviewed evidence.

Pros:

- Maximum conservatism.
- No policy/code/test update required beyond accepting the residual.
- Avoids any chance of a weak manager profile being rendered from incomplete evidence.

Cons:

- It treats absence of manager basic info as a complete Chapter 3 report-generation blocker, even though a visible evidence-gap statement would be safer and more informative.
- It is stricter than nearby Chapter 3 policy: `item_02` to `item_05` already render evidence gaps for missing reviewed evidence.
- It prevents final assembly progress for a known data gap rather than requiring the report to expose the gap.

Decision:

- Not recommended. Keeping hard block is acceptable only if the product policy is "no manager profile chapter without basic manager identity evidence." Current CHAPTER_CONTRACT goal is lower-risk stable next action under limited context, and a visible gap is a better next action than stopping the entire LLM report.

### Option B: Change to `render_evidence_gap`

Meaning:

- Change `ch3.required_output.item_01` so missing/unreviewed manager basic information must still emit the item marker, but only with explicit evidence-gap wording. No positive manager-profile claim is allowed.

Pros:

- Aligns item 01 with Chapter 3 items 02-05, which already degrade to evidence-gap rendering.
- Keeps the required output visible in the report instead of silently deleting it or blocking the whole run.
- Preserves fail-closed safety through existing writer output validation: a writer draft that omits the gap phrase remains blocked.
- Allows final assembly only after Chapter 3 produces an accepted draft/conclusion with approved gap wording and all other required body chapters are accepted.

Cons:

- Requires updating template truth and tests.
- A live/provider completion claim still cannot be made from no-live tests; bounded live re-evidence would remain a later explicitly authorized gate.
- It may expose "fund manager basic information unavailable" in a Chapter 3 profile chapter, which is product-safe but less complete.

Decision:

- Recommended.

### Option C: Change to `render_minimum_verification_question`

Meaning:

- Missing manager basic information would emit a next minimum verification question instead of a gap statement.

Pros:

- Conservative and action-oriented.
- Reuses an existing typed behavior already used by `ch3.required_output.item_06`.

Cons:

- It does not satisfy the nature of item 01 as a visible "基金经理基本信息" required output. The report should show the missing information as an evidence gap before asking a follow-up question.
- It risks making a required descriptive field look like a process-only todo.
- It is less consistent with item 02-05, which use evidence-gap rendering for missing reviewed evidence.

Decision:

- Not recommended for item 01. It remains valid for item 06 and similar follow-up-verification items.

## 5. Recommended Policy Decision

Change `ch3.required_output.item_01` from hard block to `render_evidence_gap`.

Exact policy:

- When the same-source `EvidenceAvailability` for `ch3.required_output.item_01` is `missing`, `unavailable`, or `unreviewed`, the writer must:
  - emit exact marker `<!-- required_output:ch3.required_output.item_01 -->`;
  - state that fund manager basic information lacks reviewed evidence;
  - include one approved gap phrase such as `证据不足`, `数据不足`, `未披露`, `未复核`, or `不能据此判断`;
  - avoid positive manager-profile claims, inferred tenure/ability/style conclusions, or external-source speculation.
- When the writer omits the marker or does not include approved gap wording for the degraded item, the run must remain blocked before acceptance/final assembly.
- `EvidenceAvailability` envelope absence remains fail-closed. Missing availability mapping is not the same as a reviewed missing fact and must not degrade silently.

Rationale:

- The blocker is accepted policy behavior, not a code bug.
- A report can safely include "基金经理基本信息证据不足" without inventing facts.
- Final assembly safety is preserved because incomplete or unsafe Chapter 3 output remains non-accepted and therefore blocks final assembly.

## 6. Code-generation-ready Implementation Plan

### Slice 1: Template policy change

Objective:

- Make the canonical Chapter 3 item 01 policy render an evidence gap instead of blocking on missing reviewed manager basic information.

Allowed files:

- `docs/fund-analysis-template-draft.md`
- `tests/fund/template/test_typed_contracts.py`

Exact changes:

1. In `docs/fund-analysis-template-draft.md`, update the canonical JSON object:

```json
{
  "id": "ch3.required_output.item_01",
  "text": "基金经理基本信息",
  "when_evidence_missing": "render_evidence_gap",
  "missing_evidence_reason": "第 3 章基金经理基本信息缺少已复核证据时只能输出证据缺口，不得进入未经证据支持的基金经理画像判断。"
}
```

2. Do not change item ids, item order, Chapter 3 chapter id, `must_answer`, `must_not_cover`, preferred lens, or any other Chapter 3 item policy.
3. Rename/update `tests/fund/template/test_typed_contracts.py::test_chapter_3_basic_manager_info_missing_behavior_blocks` to assert:
   - `item.item_id == "ch3.required_output.item_01"`;
   - `item.text == "基金经理基本信息"`;
   - `item.when_evidence_missing == "render_evidence_gap"`;
   - `item.missing_evidence_reason` contains both `缺少已复核证据` and `只能输出证据缺口`.

Expected result:

- Typed template projection consumes the new canonical policy without code-authored parallel truth.

Non-goals:

- Do not change `fund_agent/fund/template/contracts.py` or `typed_contracts.py` unless tests prove parser validation rejects the already-supported enum.
- Do not change Chapter 2, Chapter 4-7, Ch0/Ch7 dependency metadata, or public chapter ids.

### Slice 2: No-live Agent writer behavior tests

Objective:

- Prove the policy change degrades item 01 to safe evidence-gap rendering, not a zero-provider hard block.

Allowed files:

- `tests/agent/test_runner.py`

Exact changes:

1. Update `test_chapter_3_missing_basic_manager_info_blocks_before_provider` into a positive degradation test, for example:
   - name: `test_chapter_3_missing_basic_manager_info_renders_evidence_gap_and_accepts`;
   - input: `project_chapter_facts(replace(_bundle(), portfolio_managers=missing_portfolio_managers), chapter_ids=(3,))`;
   - policy: `AgentRunPolicy(target_chapter_ids=(3,), max_output_chars=12000, typed_template_path="typed_template_contract")`;
   - writer: fake writer returns valid Chapter 3 markdown where the segment after `<!-- required_output:ch3.required_output.item_01 -->` contains approved gap wording, for example `证据不足，不能据此判断基金经理基本信息。`;
   - auditor: `_FakeAuditor()` pass.

2. Assertions for the positive degradation test:
   - writer is called once for Chapter 3, proving no pre-provider hard block;
   - run status is `accepted`;
   - task status is `accepted`;
   - task accepted draft and accepted conclusion are present;
   - `writer_result.prompt.required_output_evidence_plan` contains item 01 with:
     - `availability_status == "missing"`;
     - `action == "render_evidence_gap"`;
     - non-empty `requirement_fact_ids`;
   - final assembly readiness for this single-target run is ready for the accepted target set. If the test uses only Chapter 3, assert Agent readiness is ready for accepted source chapter ids `(3,)`; do not claim Service full report readiness from a single body chapter.

3. Add a negative degradation test, for example:
   - name: `test_chapter_3_missing_basic_manager_info_without_gap_phrase_blocks_after_writer`;
   - same missing portfolio-manager projection;
   - writer returns the required item 01 marker but does not include approved gap wording in that segment;
   - assert writer is called once, but the task blocks because `_required_output_degrade_issues()` rejects the unsafe output;
   - expected stop/failure classification should follow the current writer-output validation mapping, not `required_output_block:ch3.required_output.item_01`.

4. Keep `test_chapter_3_missing_typed_availability_blocks_before_provider` as a fail-closed envelope test:
   - absence of the availability envelope/mapping still blocks before provider;
   - this proves the policy only degrades reviewed missing evidence, not missing contract plumbing.

Expected result:

- Missing reviewed manager basic facts degrade to evidence-gap output when the writer complies.
- Unsafe or non-compliant output remains blocked.
- Missing `EvidenceAvailability` remains fail-closed.

Non-goals:

- Do not touch provider clients, env config, runtime budget, repair budget, source acquisition, FDR, cache, PDF, or live fixtures.

### Slice 3: Service final assembly readiness tests

Objective:

- Prove final assembly behavior after Chapter 3 item 01 degrades: accepted gap-rendered Chapter 3 may participate in final assembly, but incomplete/blocked body chapters still block full report assembly.

Allowed files:

- `tests/services/test_fund_analysis_service_llm.py`

Exact changes:

1. Add a no-live service test, for example:
   - name: `test_analyze_with_llm_accepts_final_assembly_when_ch3_item01_degrades_to_gap`;
   - fake extractor returns a structured bundle with missing `portfolio_managers`;
   - fake writer emits approved evidence-gap wording for `ch3.required_output.item_01` and valid output for all other required items/chapters;
   - fake auditor passes;
   - use current explicit LLM test path with fake clients, no provider/network.

2. Assertions:
   - `result.llm_orchestration_result.status == "accepted"`;
   - Chapter 3 result is accepted;
   - `result.final_assembly_result.status == "accepted"`;
   - `result.final_assembly_result.assembled_chapter_ids == (0, 1, 2, 3, 4, 5, 6, 7)`;
   - `result.final_assembly_result.report_markdown is not None`;
   - no deterministic fallback is used as a substitute for LLM final assembly.

3. Preserve or extend existing incomplete-readiness assertions:
   - `test_partial_llm_result_does_not_fallback_to_deterministic_after_typed_readiness` must still pass;
   - if Chapter 3 writer output is unsafe, Service final assembly must remain `incomplete` with no report markdown.

Expected result:

- Final assembly readiness is based on accepted body chapters, not on raw fact completeness.
- A Chapter 3 accepted draft that explicitly renders an evidence gap can be assembled.
- A blocked or unsafe Chapter 3 cannot be assembled.

Non-goals:

- Do not weaken `FinalAssemblyPolicy.require_orchestration_accepted`.
- Do not change `_validate_orchestration()` or `_build_final_assembly_readiness()` unless tests reveal a mismatch with current accepted contract. The expected implementation should not need final assembler changes.

### Slice 4: Documentation sync decision

Objective:

- Avoid stale hard-block documentation without broad control-doc churn.

Allowed files:

- `docs/fund-analysis-template-draft.md`
- Conditionally `fund_agent/fund/README.md` only if it contains an item 01 hard-block statement.
- Conditionally `docs/design.md` only if it contains an item 01-specific hard-block statement.

Exact checks:

```bash
rg -n "ch3.required_output.item_01|基金经理基本信息|required_output_block|hard block|阻断" docs README.md fund_agent tests
```

Rules:

- Do not update `docs/current-startup-packet.md` or `docs/implementation-control.md` in the implementation gate unless the controller explicitly opens a control-doc sync gate.
- Do not rewrite general design text that only says `when_evidence_missing` supports `block / render_evidence_gap / render_minimum_verification_question`.
- If README/design prose specifically says Chapter 3 item 01 must hard-block, update it narrowly to evidence-gap behavior.

Expected result:

- Canonical template and directly relevant docs do not contradict the new policy.

## 7. Validation Matrix

All validation is no-live. No provider/network/source/PDF/FDR/analyze/checklist/readiness/release/PR commands are authorized by this plan.

### Static/template contract

Command:

```bash
uv run pytest tests/fund/template/test_typed_contracts.py::test_chapter_3_basic_manager_info_missing_behavior_renders_evidence_gap
```

Expected assertions:

- item 01 projects as `render_evidence_gap`;
- missing reason is explicit and safe;
- no other Chapter 3 item policy changes.

### Evidence availability mapping

Command:

```bash
uv run pytest tests/fund/test_evidence_availability.py::test_ch3_basic_manager_info_required_output_uses_basic_identity_availability
```

Expected assertions:

- item 01 still maps to `structured.basic_identity` and `structured.portfolio_managers`;
- policy change does not remove the same-source requirement.

### Agent runner policy behavior

Command:

```bash
uv run pytest \
  tests/agent/test_runner.py::test_chapter_3_missing_typed_availability_blocks_before_provider \
  tests/agent/test_runner.py::test_chapter_3_missing_basic_manager_info_renders_evidence_gap_and_accepts \
  tests/agent/test_runner.py::test_chapter_3_missing_basic_manager_info_without_gap_phrase_blocks_after_writer
```

Expected assertions:

- missing availability envelope remains zero-provider fail-closed;
- missing manager basic info with approved gap wording calls writer and accepts Chapter 3;
- missing manager basic info without approved gap wording blocks after writer validation;
- new blocker is not `required_output_block:ch3.required_output.item_01`.

### Service final assembly behavior

Command:

```bash
uv run pytest \
  tests/services/test_fund_analysis_service_llm.py::test_analyze_with_llm_accepts_final_assembly_when_ch3_item01_degrades_to_gap \
  tests/services/test_fund_analysis_service_llm.py::test_partial_llm_result_does_not_fallback_to_deterministic_after_typed_readiness
```

Expected assertions:

- if all body chapters including gap-rendered Chapter 3 are accepted, final assembly is accepted and report markdown exists;
- if any body chapter remains blocked/partial, final assembly remains incomplete and report markdown remains `None`;
- no deterministic fallback masks incomplete LLM assembly.

### Focused regression bundle

Command:

```bash
uv run pytest tests/agent/test_runner.py tests/services/test_fund_analysis_service_llm.py tests/fund/template/test_typed_contracts.py tests/fund/test_evidence_availability.py
```

Expected assertions:

- all focused no-live tests pass.

### Formatting/static checks

Commands:

```bash
uv run ruff check docs/fund-analysis-template-draft.md tests/agent/test_runner.py tests/services/test_fund_analysis_service_llm.py tests/fund/template/test_typed_contracts.py tests/fund/test_evidence_availability.py
git diff --check
```

Expected assertions:

- ruff passes for touched Python files; if ruff does not accept Markdown path arguments in this repo, rerun on the touched Python files only and record the Markdown-path exclusion.
- `git diff --check` passes.

## 8. Deferred / Non-goals

Explicitly deferred:

- Any live/provider/network/source/PDF/FDR/analyze/checklist command.
- Any provider payload/response, writer markdown, auditor markdown, raw prompt, final report body, source/cache/PDF body read.
- Bounded live re-evidence after implementation.
- Release/readiness, MVP-ready, LLM path ready, PR/push/merge/mark-ready claims.
- EID source policy changes, fallback, Eastmoney, fund-company website, CNINFO, multi-source routing.
- Provider defaults, model/base URL defaults, API key behavior, provider timeout/budget changes.
- Chapter repair budget calibration.
- Annual-period LLM route or multi-period disclosure route.
- Docling/parser policy or parser benchmark.
- Score-loop, golden promotion/readiness, snapshot or final judgment policy changes.
- Host/Agent runtime expansion, durable session/resume/memory/outbox, full tool-loop/ToolRegistry work.
- Broad required-output policy audit across all chapters beyond item 01 and directly affected no-live tests.
- Control-doc updates unless a later controller gate opens control sync.

## 9. Risks and Residuals

- Risk: changing item 01 to evidence-gap rendering may allow a Chapter 3 draft with less complete manager profile content. Mitigation: require explicit gap wording and keep unsafe output blocked.
- Risk: no-live fake writer tests can overfit to local helper output. Mitigation: include one positive compliant writer case and one negative non-compliant writer case.
- Risk: final assembly acceptance could be misread as release readiness. Mitigation: artifact and tests must state that no-live final assembly behavior is not live/provider completion, content quality, readiness, release, or PR proof.
- Risk: item 01 basic manager info may be missing because upstream extraction is weak rather than source disclosure absence. Mitigation: this policy does not change extraction/source behavior; extraction/source evidence remains separate future work.
- Residual: post-implementation bounded live re-evidence remains separate and requires explicit authorization.
- Residual: broader Chapter 3 required-output policy calibration remains future scope if reviewers want item 02-06 re-evaluated together.
- Residual: release/readiness remains `NOT_READY` even if this policy implementation passes all no-live tests.

No blocking open questions are required for implementation. The policy choice is explicit: `render_evidence_gap`.

## 10. Exact Next Gate Recommendation

Next gate:

`Provider/LLM Chapter 3 Required-output Policy No-live Implementation Gate`

Recommended gate classification:

- `standard`

Implementation worker scope:

- Apply Slices 1-3.
- Run the validation matrix above.
- Record any conditional docs decision from Slice 4.
- Produce an implementation artifact under `docs/reviews/`.

Implementation worker must not:

- run live/provider/network/source/PDF/FDR/analyze/checklist/readiness/release/PR commands;
- read forbidden bodies or payloads;
- update control docs;
- stage, commit, push, create PR, or merge;
- change EID source policy, provider defaults, repair budget, annual-period LLM route, Docling/parser policy, fallback policy, or readiness state.

Completion signal:

- Template item 01 projects as `render_evidence_gap`.
- Missing item 01 reviewed evidence can produce accepted Chapter 3 only when approved evidence-gap wording is present.
- Unsafe item 01 output still blocks and cannot reach final assembly.
- Service final assembly accepts a full fake no-live LLM run only when all required body chapters, including gap-rendered Chapter 3, are accepted.
- Release/readiness remains `NOT_READY`.

## 11. Final Verdict

VERDICT: READY_FOR_NO_LIVE_POLICY_IMPLEMENTATION_GATE_NOT_READY

`ch3.required_output.item_01` should degrade to `render_evidence_gap`, not remain hard block and not switch to `render_minimum_verification_question`. The implementation should be a narrow canonical template policy change plus focused no-live tests proving writer gap enforcement and final assembly readiness behavior. No live/provider/source/FDR/readiness/release/PR work is authorized, and release/readiness remains `NOT_READY`.
