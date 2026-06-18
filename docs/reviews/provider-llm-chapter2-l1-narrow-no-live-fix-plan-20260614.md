# Provider/LLM Chapter 2 L1 Numerical Closure Narrow No-live Fix Plan

Date: 2026-06-14

Role: AgentCodex/procodex planning worker

Gate: `Provider/LLM Chapter 2 L1 Numerical Closure Narrow No-live Fix Planning Gate`

## Scope / Non-goals

Plan scope:

- Produce a code-generation-ready narrow no-live fix plan for Chapter 2 L1 numerical-closure repair effectiveness.
- Treat repair-context propagation as working.
- Preserve L1 as fail-closed.
- Preserve current repair budget defaults, including one regenerate attempt per chapter in the current body-chapter path.
- Keep the fix deterministic and no-live, with fake-client/unit/integration tests only.
- Preserve EID single-source/no-fallback and release/readiness `NOT_READY`.

Non-goals:

- No implementation in this planning gate.
- No live/provider/LLM/network/source/PDF/FDR/analyze/checklist/readiness/release/PR commands.
- No writer Markdown, auditor feedback Markdown, repair Markdown, raw prompts, provider payloads, source/PDF/cache body or final report body reads.
- No L1 weakening, downgrade, warning-only conversion, allowlist bypass or audit suppression.
- No repair budget calibration or default changes.
- No source policy, fallback, annual-period LLM route, provider default or runtime config change.
- No Chapter 5 forbidden-phrase disposition.

## Inputs And Accepted Facts

Accepted control facts:

- Current active gate is this planning gate; classification is `standard`.
- Current path is explicit opt-in Provider/LLM and fail-closed; deterministic mainline and EID single-source/no-fallback remain unchanged.
- Release/readiness remains `NOT_READY`.
- Current default body-chapter repair budget remains one regenerate attempt per chapter and is not calibrated as a product default.

Accepted diagnostic facts from `docs/reviews/provider-llm-chapter2-l1-no-live-diagnostic-evidence-controller-judgment-20260614.md`:

- Prior live metadata checkpoint `765c616` had Chapter 2 accepted after repair, with first failed Chapter 3 fact-gap.
- Current live metadata checkpoint `2f8dce9` has Chapter 2 failed with `repair_budget_exhausted` / `prompt_contract` / `l1_numerical_closure`.
- Both runs used two Chapter 2 attempts, so the issue is repair effectiveness, not missing initial L1 detection.
- Chapter 2 L1 repair checklist reaches writer prompt assembly in current no-live code.
- Current Chapter 3 required-output policy path does not route through the Chapter 2 L1 checklist condition.
- L1 fail-closed behavior and one-repair-budget exhaustion semantics are preserved.
- Metadata-only evidence cannot prove whether the model ignored the checklist or whether the checklist wording is too weak.

Accepted DS review residual:

- `1b9cd00` diff verification had not been performed in the diagnostic gate and had to be closed in this planning gate or carried as an explicit assumption.
- This plan closes it with the bounded diff result below.

Current implementation facts from must-read code/tests:

- `fund_agent/fund/chapter_writer.py` assembles prompt fragments in `_chapter_prompt_fragments()` and appends repair context through `_repair_context_prompt()` plus `_ch2_l1_repair_guidance_prompt()`.
- `_ch2_numerical_closure_contract_prompt()` injects the initial Chapter 2 R=A+B-C numerical-closure anchor rule for Chapter 2 only.
- `_has_l1_numerical_closure_repair_issue()` triggers only when previous issue ids start with `programmatic:L1`.
- `_ch2_l1_repair_guidance_prompt()` currently renders a Chapter 2 L1 repair checklist only for Chapter 2 plus prior `programmatic:L1`.
- `tests/fund/test_chapter_writer.py` already proves initial Chapter 2 L1 guidance, repair checklist rendering, absence outside target scope and typed repair context propagation.
- `tests/services/test_chapter_orchestrator.py` already proves L1 repair context reaches the second writer request, anchored repair can pass, ignored/unanchored repair fails closed with `repair_budget_exhausted` / `prompt_contract` / `l1_numerical_closure`, and repair budget semantics remain unchanged.
- `tests/fund/test_chapter_auditor.py` already proves concrete unanchored R=A+B-C / A=R-B / A-C percentages fail L1, nearby anchors pass, formula-framework-only text passes, and source-section unanchored numeric closure still fails.

## Bounded Diff Result

Command run:

```bash
git diff 842362d..1b9cd00 -- fund_agent/fund/chapter_writer.py
```

Result:

- Exit code `0`.
- No output.
- Interpretation: checkpoint `1b9cd00` did not modify `fund_agent/fund/chapter_writer.py`; DS F1 bounded-diff residual is closed for this file. Current Chapter 2 repair prompt assembly in `chapter_writer.py` is byte-identical to checkpoint `842362d` across this bounded range.

This does not prove the model read a live prompt or followed a checklist. It only proves the Chapter 3 required-output policy checkpoint did not alter `chapter_writer.py`.

## Chosen Fix Strategy

Implement a narrow Fund writer prompt-contract strengthening in `fund_agent/fund/chapter_writer.py`, without changing Service orchestration, L1 auditor semantics, repair budget, provider behavior, source policy or fallback.

Primary decision:

- Strengthen Chapter 2 L1 instructions where they already belong: the Fund writer prompt contract.
- Make the initial Chapter 2 numerical-closure contract and repair-specific checklist more deterministic by giving the writer an explicit safe-output decision rule:
  - If a concrete R/A/B/C/A-C / Alpha / Beta / Cost / percentage-closure statement is used, an allowed anchor marker must be in the same sentence or immediately adjacent local context.
  - If the writer is unsure that an allowed anchor supports the exact numeric closure, it must remove the concrete percentage and write an approved gap / minimum verification question instead.
  - `### 结论要点` and `### 证据与出处` must not repeat concrete R/A/B/C/A-C percentages unless the local anchor condition is met.
  - Source labels or prose references to annual-report sections do not substitute for `<!-- anchor:<anchor_id> -->`.
  - The repair prompt must include a final local self-check before output: any line containing concrete closure terms plus a percentage without nearby allowed anchor must be rewritten to a gap / verification sentence.

Implementation shape:

1. Update `_ch2_numerical_closure_contract_prompt(chapter)` to add an explicit `第2章 L1 数字闭环安全输出契约` block for all Chapter 2 attempts.
2. Update `_ch2_l1_repair_guidance_prompt(chapter, repair_context)` to add an explicit repair-only `第2章 L1 repair 必须改写规则` block.
3. Keep `_has_l1_numerical_closure_repair_issue()` unchanged.
4. Keep `_repair_context_prompt()` unchanged except if minor wording is strictly needed to avoid duplicated/contradictory repair instructions; no behavior or schema change.
5. Do not add post-processing that silently edits model output.
6. Do not alter `_draft_from_llm_response()`, `_required_output_*()`, `ChapterRepairContext`, `ChapterLLMRequest`, or Service orchestration.
7. Do not alter auditor L1 detection except for adding tests that prove the safe gap rewrite remains allowed and concrete unanchored percentages still fail.

Why this is robust to both interpretations:

- If the previous checklist was ignored, implementation must prove that ignored/unanchored repair output still fails closed under the existing L1 path.
- If the previous checklist wording was too weak, implementation strengthens the prompt contract and tests the exact prompt text that fake writers receive on repair.
- The plan does not rely on metadata-only proof of model behavior and does not claim deterministic live success. It only creates a stronger no-live prompt contract plus fail-closed guard evidence.

## Rejected Alternatives

- Weaken L1, downgrade it to warning, or allow concrete percentages without nearby anchor: rejected because accepted facts require L1 fail-closed semantics.
- Increase `max_repair_attempts` or change repair budget defaults: rejected because repair budget calibration is a separate gate.
- Repeat live/provider evidence before a narrow no-live fix: rejected because the accepted diagnostic already identifies no-live repair-effectiveness planning as the next gate, and live sampling would not distinguish ignored checklist from weak wording.
- Read writer Markdown, repair Markdown, raw prompts, provider payloads or final report bodies: rejected by scope.
- Change Service orchestration, Host/Agent runtime, provider adapter or typed template required-output policy: rejected as broader than the root-cause surface.
- Add deterministic post-processing that deletes or rewrites LLM text after generation: rejected because it can silently change evidence-bearing content and would require a separate design gate for report text mutation.
- Disable concrete R=A+B-C discussion entirely for Chapter 2: rejected because Chapter 2 remains the收益归因 chapter; the fix should constrain unsupported numeric closure, not remove the chapter's analytical lens.

## Exact Allowed Implementation Write Set

Allowed source/test writes for the next implementation gate:

- `fund_agent/fund/chapter_writer.py`
- `tests/fund/test_chapter_writer.py`
- `tests/services/test_chapter_orchestrator.py`
- `tests/fund/test_chapter_auditor.py`

Allowed conditional documentation writes only if implementation makes existing docs stale:

- `fund_agent/fund/README.md`
- `tests/README.md`

Documentation rule:

- If the implementation changes only internal prompt wording and existing READMEs do not describe that wording, record `README no-change; checked not stale` in the implementation artifact.
- If either README currently documents the affected Chapter 2 L1 writer/auditor/test contract and becomes stale, update only the stale lines.

Forbidden implementation writes:

- Any source/test/runtime file outside the write set above.
- Any report, prompt payload, source/PDF/cache, provider artifact, final report body, readiness/release/PR artifact or control/design truth document.

## Exact Implementation Steps

1. In `fund_agent/fund/chapter_writer.py`, strengthen `_ch2_numerical_closure_contract_prompt()`:
   - Keep Chapter 2-only gating.
   - Preserve current rule that concrete formula/percentage closure requires an allowed anchor marker in the same sentence or nearby local context.
   - Add explicit safe-output alternatives:
     - anchored numeric closure, or
     - no concrete percentage plus `数据不足` / `下一步最小验证问题`.
   - State that prose source labels, section names and `### 证据与出处` lists do not replace local anchor markers.
   - State that unsupported R/A/B/C/A-C / Alpha / Beta / Cost percentages must be omitted, not approximated.

2. In `fund_agent/fund/chapter_writer.py`, strengthen `_ch2_l1_repair_guidance_prompt()`:
   - Keep the same trigger: Chapter 2 plus prior `programmatic:L1`.
   - Add a short, explicit repair-only contract with stable wording suitable for tests:
     - `第2章 L1 repair 必须改写规则`
     - `先删除上一轮无邻近 anchor 的具体数字闭环断言`
     - `只有确认 allowed anchor 支撑该具体数值时才重新写入百分比`
     - `不确定时写数据不足或下一步最小验证问题，且不写具体百分比`
     - `输出前逐行自查 R/A/B/C/A-C/Alpha/Beta/Cost/%`
   - Keep instructions concise enough not to inflate prompt materially.

3. Do not modify `ChapterRepairContext`, `ChapterLLMRequest`, prompt diagnostics schema, required-output plan/action logic, writer parser stop reasons, auditor L1 regex/nearby-anchor logic, or Service repair decisions.

4. Check conditional README/doc staleness under the exact write set. Do not update control/design docs.

## Exact Test Additions / Updates

`tests/fund/test_chapter_writer.py`:

- Update `test_writer_prompt_contains_l1_numerical_closure_anchor_rule` to assert the initial Chapter 2 prompt contains the new safe-output contract:
  - the stable header `第2章 L1 数字闭环安全输出契约`;
  - the same-sentence / nearby allowed-anchor requirement;
  - the no-concrete-percentage gap / minimum-verification alternative;
  - the rule that source labels do not replace local anchor markers.
- Update `test_ch2_l1_repair_context_renders_local_anchor_placement_checklist` to assert the repair prompt contains:
  - `第2章 L1 repair 必须改写规则`;
  - delete first, reintroduce only with allowed anchor support;
  - uncertainty routes to gap / minimum verification without concrete percentage;
  - final local self-check for R/A/B/C/A-C/Alpha/Beta/Cost/%.
- Keep `test_ch2_l1_repair_checklist_absent_outside_ch2_l1_repair_context` and extend it to assert the repair-only header remains absent outside Chapter 2 L1 repair.
- Keep `test_non_ch2_writer_prompt_omits_l1_numerical_closure_anchor_rule` and extend it to assert the new Chapter 2-only header is absent outside Chapter 2.
- Keep compact-payload coverage by asserting the strengthened Chapter 2 contract survives compact prompt mode.

`tests/services/test_chapter_orchestrator.py`:

- Update `test_l1_repair_context_guides_anchored_correction_and_accepts_after_repair` to assert the second writer request contains the strengthened repair-only contract and still accepts an anchored repair.
- Update `test_l1_failure_after_repair_budget_exhausted_keeps_l1_subcategory` to assert a writer that ignores the strengthened checklist still fails closed with:
  - `status == "failed"`;
  - `stop_reason == "repair_budget_exhausted"`;
  - `failure_category == "prompt_contract"`;
  - `failure_subcategory == "l1_numerical_closure"`.
- Update `test_required_corrections_are_deterministic_for_known_issue_patterns` only if wording in Service-derived correction assertions must align with the strengthened writer contract. Do not broaden Service behavior.

`tests/fund/test_chapter_auditor.py`:

- Add or update one no-live L1 test proving a safe gap / minimum-verification rewrite without concrete percentage is allowed for Chapter 2:
  - Example suffix: `数据不足，不能完成具体 R=A+B-C 百分比闭环。下一步最小验证问题：复核年报中基金收益、基准收益和费用口径是否同源可比。`
  - Assertion: no `L1` issue.
- Keep existing tests proving concrete unanchored R=A+B-C / A=R-B / A-C percentages still fail and nearby anchored percentages still pass.

## Validation Commands

Implementation gate should run only no-live local validation:

```bash
uv run pytest tests/fund/test_chapter_writer.py -k "ch2_l1 or l1_numerical_closure or repair_context or compact_prompt_payload" -q
uv run pytest tests/services/test_chapter_orchestrator.py -k "l1_repair_context or l1_failure_after_repair_budget_exhausted or required_corrections_are_deterministic" -q
uv run pytest tests/fund/test_chapter_auditor.py -k "programmatic_audit_fails_l1 or programmatic_audit_allows_l1 or a_minus_c or formula_framework or ch2_source_section or l1_gap" -q
uv run pytest tests/fund/test_chapter_writer.py tests/services/test_chapter_orchestrator.py tests/fund/test_chapter_auditor.py -q
uv run ruff check fund_agent/fund/chapter_writer.py tests/fund/test_chapter_writer.py tests/services/test_chapter_orchestrator.py tests/fund/test_chapter_auditor.py
git diff --check
git status --short
```

Forbidden validation:

- Any live/provider/LLM/network/source/PDF/FDR/analyze/checklist/readiness/release/PR/push/merge command.
- Any command that reads forbidden body artifacts.

## Review Checklist For DS / MiMo

Reviewers should check:

- The implementation touches only the allowed write set.
- `fund_agent/fund/chapter_writer.py` remains inside Fund/Agent boundary and imports no Service, Host, provider SDK, source, PDF, cache, repository, parser, dayu or network modules.
- Chapter 2 L1 prompt changes are scoped to Chapter 2 and repair-only text is scoped to prior `programmatic:L1`.
- L1 auditor behavior remains fail-closed; no tests were changed to accept concrete unanchored percentages.
- Repair budget defaults and `ChapterOrchestrationPolicy` defaults are unchanged.
- No deterministic report fallback, provider fallback, source fallback or EID policy change was introduced.
- The tests prove both:
  - strengthened prompt contract reaches the second writer request; and
  - ignored/unanchored repair output still fails closed.
- No forbidden bodies, raw prompts, payloads, source/PDF/cache content or final report bodies were read or added as fixtures.
- README/doc decision is recorded and, if docs were edited, edits are limited to stale current behavior only.
- Final implementation report preserves `NOT_READY` and does not claim live/provider completion.

## Stop Conditions

Implementation worker must stop and return control if any of these occur:

- A fix appears to require L1 weakening, L1 warning-only behavior, issue suppression or expanded allowlists.
- A fix appears to require changing repair budget defaults.
- A fix appears to require Service/Host/Agent runtime behavior beyond the allowed write set.
- A fix appears to require live/provider/network/source/PDF/FDR/analyze/checklist/readiness/release/PR commands.
- A fix appears to require reading writer Markdown, auditor feedback Markdown, repair Markdown, raw prompts, provider payloads, source/PDF/cache bodies or final report bodies.
- A fix appears to require modifying control/design truth docs.
- Focused validation fails and the failure cannot be resolved inside the allowed write set without broadening scope.
- Existing dirty workspace changes create file ownership ambiguity in any allowed write file.

## Residuals

| Residual | Status | Owner / next handling |
|---|---|---|
| Whether the live model ignored the checklist or the checklist wording was too weak | Unproven | This plan covers both with stronger prompt contract plus ignored-output fail-closed tests; live behavior remains unproven. |
| Provider/LLM full completion and content quality | Unproven | Future bounded live evidence gate only after no-live implementation/review acceptance. |
| Repair budget calibration | Deferred | Separate standard gate; do not change defaults here. |
| Chapter 5 forbidden phrase blocker | Deferred | Separate disposition/fix gate after Chapter 2 path is accepted. |
| Release/readiness/PR state | `NOT_READY` | Future readiness/release/PR gates only; no claim here. |
| Workspace residue and unrelated dirty files | Observed via status only | No disposition in this gate; not readiness proof. |

## Next Gate Recommendation

Proceed to:

```text
Provider/LLM Chapter 2 L1 Numerical Closure Narrow No-live Fix Implementation Gate
```

The implementation gate should follow this plan exactly, produce a durable implementation artifact, run only the no-live validation commands above, then go to DS/MiMo code review. Do not proceed to live/provider evidence until no-live implementation and review are accepted by controller judgment.

## Final Verdict

READY_FOR_NARROW_NO_LIVE_FIX_IMPLEMENTATION_GATE_NOT_READY
