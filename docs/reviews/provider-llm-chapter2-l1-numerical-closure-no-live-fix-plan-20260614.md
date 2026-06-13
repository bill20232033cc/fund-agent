# Provider/LLM Chapter 2 L1 Numerical Closure No-live Fix Plan

Date: 2026-06-14

## 1. Scope

Gate: `Provider/LLM Chapter 2 L1 Numerical Closure No-live Fix Planning Gate`.

Role: AgentCodex planning worker, not controller.

Objective: produce a code-generation-ready no-live fix plan for the accepted H3 root cause only.

This plan does not implement the fix, change source code, change tests, update control/design/README files, run live/provider/network/source/PDF/readiness/release/PR commands, stage, commit, push or open a PR.

In scope for the future implementation gate:

- Strengthen the Chapter 2 L1 repair attempt prompt so a `patch` repair hint that is currently executed as whole-chapter regenerate receives local, structured and unambiguous anchor-placement instructions.
- Preserve the current fail-closed L1 blocker: concrete R/A/B/C/A-C numerical closure assertions remain invalid unless an allowed anchor marker is in the same sentence or within two surrounding lines.
- Preserve current one-regenerate content repair budget.

Out of scope:

- Weakening, deleting or downgrading L1.
- Changing `max_content_repair_attempts`, `max_repair_attempts` or any repair budget default.
- Implementing typed patch API.
- Changing source policy, EID single-source/no-fallback, fallback eligibility, Docling, provider defaults, provider runtime budget, annual-period LLM route, readiness/release/PR state or default deterministic routes.
- Running live/provider/network/source/PDF/readiness/release/PR commands.

Release/readiness remains `NOT_READY`.

## 2. Evidence Inputs

Primary control inputs:

- `AGENTS.md`
- `docs/implementation-control.md`
- `docs/current-startup-packet.md`
- `docs/design.md` relevant Route C, CHAPTER_CONTRACT, L1 numerical closure and repair-budget sections

Accepted root-cause inputs:

- `docs/reviews/provider-llm-chapter2-l1-numerical-closure-root-cause-evidence-20260614.md`
- `docs/reviews/provider-llm-chapter2-l1-numerical-closure-root-cause-evidence-controller-judgment-20260614.md`

Narrow code context read:

- `fund_agent/fund/chapter_writer.py`: `ChapterRepairContext`, `build_chapter_prompt()`, `_chapter_prompt_fragments()`, `_ch2_numerical_closure_contract_prompt()`, `_repair_context_prompt()`
- `fund_agent/services/chapter_orchestrator.py`: `_repair_context_from_audit()`, `_required_correction_from_issue()`
- `fund_agent/agent/repair.py`: `repair_context_from_audit()`, L1 correction mapping
- Existing focused tests in `tests/fund/test_chapter_writer.py`, `tests/fund/test_chapter_auditor.py`, `tests/services/test_chapter_orchestrator.py`, `tests/agent/test_repair_policy.py`

Workspace note: `git status --short` showed pre-existing modified/untracked residue before this artifact, including `AGENTS.md`, `README.md`, `docs/design.md`, multiple review artifacts, reports, scripts and local data. This is scope evidence only and is not readiness evidence.

## 3. Accepted Root Cause Restatement

Accepted H3 root cause:

- Chapter 2 attempt 0 produced a valid `programmatic:L1` blocker: a concrete R/A/B/C/A-C numerical closure assertion lacked a nearby allowed anchor marker.
- The auditor returned `repair_hint=patch`.
- Current repair behavior maps both `patch` and `regenerate` to whole-chapter regenerate while budget remains.
- Chapter 2 attempt 1 again produced an L1 unanchored numerical closure.
- The one-regenerate budget was exhausted, yielding `repair_budget_exhausted` / `prompt_contract` / `l1_numerical_closure`.

Rejected or residual hypotheses:

- H1 required-output omission is rejected.
- H2 L1 strictness/contract mismatch is rejected.
- H4 evidence/fact/anchor availability insufficiency remains residual, not accepted as the root cause.
- H5 diagnostic serialization incompleteness is a contributing diagnostic gap, not the runtime cause.

## 4. Design Constraints

- `docs/fund-analysis-template-draft.md` canonical `TEMPLATE_CONTRACT_MANIFEST_JSON` remains the authored template truth source.
- Route C `--use-llm` remains explicit opt-in, provider-backed and fail-closed.
- `fund-analysis analyze-annual-period` remains deterministic and is not an LLM body-chapter route.
- The current Route C body-chapter repair path may still regenerate the whole chapter; this gate must not introduce typed patch API.
- L1 remains a blocking programmatic audit rule.
- The fix must not hide L1 by moving the failure to a warning, skipping audit, changing failure category, or weakening anchor proximity.
- Business parameters must remain typed and explicit; no `extra_payload`.
- The implementation must stay within Fund writer prompt behavior and the existing Service/Agent repair context path. Host, provider construction, source acquisition and document repository behavior are not in scope.

## 5. Proposed No-live Fix Strategy

Chosen strategy: add a deterministic Chapter 2 + L1 repair checklist to the writer prompt when the repair context contains a previous `programmatic:L1` issue.

Rationale:

- It directly targets the accepted H3 failure mode without changing audit strictness or repair budget.
- It keeps current whole-chapter regenerate behavior, but makes the repair attempt behave like a localized correction for L1 anchor placement.
- It avoids implementing typed patch API or changing orchestration semantics.
- It preserves fail-closed behavior: if the writer still emits unanchored concrete numerical closure, the existing L1 auditor blocks it.

Implementation steps for the future gate:

1. In `fund_agent/fund/chapter_writer.py`, add a private helper such as `_has_l1_numerical_closure_repair_issue(repair_context: ChapterRepairContext | None) -> bool`.

   Detection should be deterministic and narrow:
   - true when any `previous_issue_ids` entry starts with `programmatic:L1`;
   - false for non-repair attempts, non-Chapter 2 prompts and non-L1 issues.

2. Add a private helper such as `_ch2_l1_repair_guidance_prompt(chapter: ChapterFactInput, repair_context: ChapterRepairContext | None) -> str`.

   It should return an empty string unless `chapter.chapter_id == 2` and the repair context has an L1 issue.

   The returned prompt must be a short checklist with these exact semantics:

   - scan `### 结论要点`, `### 详细情况` and `### 证据与出处` before output;
   - for every concrete R/A/B/C/A-C formula, A-C, Alpha/Beta/Cost or percentage closure assertion, choose exactly one valid path:
     - place an existing allowed `<!-- anchor:<anchor_id> -->` marker in the same sentence or within two surrounding lines; or
     - delete the concrete numerical closure assertion and write an approved data-gap / minimum-verification sentence without concrete percentages;
   - do not put the anchor only in a detached source list if the concrete closure sentence is elsewhere;
   - do not repeat concrete R/A/B/C/A-C percentages in conclusion or source sections without nearby anchor;
   - if unsure which allowed anchor supports the closure, omit the concrete percentage rather than inventing or repeating it.

3. Render that helper in `_chapter_prompt_fragments()` adjacent to the current `repair_context` fragment.

   Preferred minimal code shape:

   - keep `ChapterRepairContext` fields unchanged;
   - keep `_repair_context_prompt()` generic;
   - add the new Ch2/L1 checklist either by appending it to `repair_context` fragment or by inserting it immediately after the generic repair context in `user_prompt`;
   - do not modify `ChapterLLMRequest` schema and do not add `extra_payload`.

4. Do not change `fund_agent/services/chapter_orchestrator.py::_decide_repair()`, `fund_agent/agent/repair.py::decide_repair()`, budget defaults, or `_audit_numerical_closure()`.

5. Verify Service and Agent L1 correction text before changing it. The future implementation worker must add or extend a no-live assertion that exposes the existing L1 correction text in the Service repair path and, if the Agent duplicate path is touched, the Agent repair path. Edit `chapter_orchestrator.py` and `repair.py` only when that red assertion proves the emitted L1 correction text lacks the new anchor-placement semantics. Record the verified branch in implementation evidence. This must not change repair action, stop reason or budget behavior.

Rejected alternatives:

- Increase repair budget: rejected for this gate; calibration is separate.
- Weaken L1 proximity or allow detached source-section anchors: rejected because it would dilute accepted L1.
- Implement typed patch API: too broad for this gate.
- Add H4/H5 diagnostics as part of the main fix: useful later, but not required to address accepted H3.

## 6. Exact Allowed Write Set for future implementation gate

Closed write set:

- `fund_agent/fund/chapter_writer.py`
- `tests/fund/test_chapter_writer.py`
- `tests/services/test_chapter_orchestrator.py`
- `fund_agent/services/chapter_orchestrator.py` only if aligning the existing L1 `required_corrections` text is necessary
- `fund_agent/agent/repair.py` only if `fund_agent/services/chapter_orchestrator.py` L1 correction text is changed, to prevent Service/Agent divergence
- `tests/agent/test_repair_policy.py` only if `fund_agent/agent/repair.py` is changed
- `tests/README.md` only if the implementation changes test commands, test layout or documented testing conventions

Explicitly disallowed write targets:

- `docs/design.md`
- `docs/implementation-control.md`
- `docs/current-startup-packet.md`
- root `README.md`
- provider config/defaults
- source policy, fallback, Docling or annual-report repository code
- CLI live/provider command behavior
- release/readiness/PR artifacts
- runtime report artifacts under `reports/`

## 7. Test Plan

Future implementation should be red-test-first.

Required tests:

1. Writer prompt unit test in `tests/fund/test_chapter_writer.py`.

   Add a test such as `test_ch2_l1_repair_context_renders_local_anchor_placement_checklist`.

   Construct Chapter 2 writer input with:

   - `repair_context.attempt_index=1`
   - `previous_issue_ids=("programmatic:L1:line:10:fixture",)`
   - a sanitized previous message about missing nearby anchor
   - an existing `required_corrections` tuple

   Assert `build_chapter_prompt(input_data).user_prompt` contains the new checklist semantics:

   - L1 numerical closure repair checklist title;
   - same sentence or two surrounding lines;
   - concrete R/A/B/C/A-C percentage closure assertions;
   - delete/replace with data gap when no same-source anchor is known;
   - do not place anchor only in detached `### 证据与出处` source list;
   - no `extra_payload` field is introduced.

2. Writer negative/leakage test in `tests/fund/test_chapter_writer.py`.

   Assert the checklist is absent for:

   - Chapter 2 initial attempt with no repair context;
   - non-Chapter 2 repair context;
   - Chapter 2 repair context whose previous issue is not L1.

3. Orchestrator path test in `tests/services/test_chapter_orchestrator.py`.

   Extend or add a focused test around the existing L1 repair scenario to assert the second writer request contains the new checklist in `user_prompt`, while:

   - `repair_context.previous_issue_ids` still carries `programmatic:L1`;
   - the run can still be accepted when the repair draft places an allowed anchor near the numerical closure;
   - the existing failure test still returns `repair_budget_exhausted` / `prompt_contract` / `l1_numerical_closure` if the repair draft repeats the unanchored assertion.

4. If Service/Agent L1 correction text is changed, add or update tests in `tests/agent/test_repair_policy.py` and the relevant Service repair-context tests to prove both mappings keep the same L1 semantics and still sanitize previous messages. If those files are not changed, implementation evidence must state which Service-side assertion proved no correction-text alignment edit was needed.

Regression expectations:

- Existing L1 auditor tests must continue to pass unchanged.
- Existing repair-budget-exhausted tests must continue to pass unchanged.
- No test may require provider, network, live source, PDF, readiness or release state.

## 8. Validation Commands

Future implementation gate may run only no-live/local commands:

```bash
uv run pytest tests/fund/test_chapter_writer.py -k "ch2_l1_repair or l1_numerical_closure or repair_context" -q
uv run pytest tests/services/test_chapter_orchestrator.py -k "l1_repair_context or l1_failure_after_repair_budget_exhausted or repair_budget_exhausted" -q
uv run pytest tests/fund/test_chapter_auditor.py -k "programmatic_audit_fails_l1 or programmatic_audit_allows_l1 or a_minus_c or formula_framework or ch2_source_section" -q
uv run pytest tests/agent/test_repair_policy.py -k "repair_context or repair_budget_exhausted" -q
uv run ruff check fund_agent/fund/chapter_writer.py fund_agent/services/chapter_orchestrator.py fund_agent/agent/repair.py tests/fund/test_chapter_writer.py tests/services/test_chapter_orchestrator.py tests/agent/test_repair_policy.py
git diff --check
```

If `fund_agent/services/chapter_orchestrator.py`, `fund_agent/agent/repair.py` or `tests/agent/test_repair_policy.py` are not changed, their focused tests and ruff targets may be omitted by the implementation worker with that omission recorded in completion evidence.

Forbidden validation:

- live/provider/network commands
- `fund-analysis analyze --use-llm`
- `fund-analysis analyze-annual-period`
- source/PDF/FDR/FundDocumentRepository acquisition commands
- readiness/release/PR/push/merge commands

## 9. Risks and Residuals

- The fix improves repair instruction quality but cannot guarantee a live provider will obey it. If a future bounded live run still repeats L1 after this no-live fix, the next gate should classify whether the remaining issue is prompt adherence, insufficient safe diagnostics, or budget calibration.
- H4 remains residual: safe metadata still may not prove full allowed fact/anchor availability or required-output linkage.
- H5 remains residual: diagnostic serialization may still lack allowed fact/anchor counts unless a separate diagnostic gate adds them.
- Repair budget remains uncalibrated. This gate must not treat one-regenerate success/failure as product-level optimality.
- The `tests/README.md` trigger should be handled conservatively: if only focused tests are added under existing conventions, no README change is expected; if the implementation changes testing commands or conventions, update `tests/README.md` within the allowed set above.

## 10. Next Gate Recommendation

Proceed to:

`Provider/LLM Chapter 2 L1 Numerical Closure No-live Fix Implementation Gate`

Required implementation-gate conditions:

- Red-test-first for the Ch2/L1 repair checklist.
- Stay within the allowed write set.
- Preserve L1 blocker, repair budget defaults, EID single-source/no-fallback and `NOT_READY`.
- Run only the no-live validation commands listed above.
- Produce implementation evidence and independent review before any controller acceptance.

Future separate gates after this implementation, if needed:

- H4/H5 safe diagnostic serialization/projection evidence gate.
- Chapter repair budget calibration gate.
- Controlled bounded live re-evidence gate, only after explicit live authorization.

## 11. Final Verdict

VERDICT: READY_FOR_NO_LIVE_FIX_IMPLEMENTATION_GATE_NOT_READY
