# Provider/LLM Chapter 6 Invalid-marker Narrow No-live Fix Plan

Date: 2026-06-14

Role: AgentCodex planning worker, not controller.

Gate: `Provider/LLM Chapter 6 Invalid-marker Narrow No-live Fix Planning Gate`

Target: Chapter 6 `invalid_marker` output-format guardrails only.

Release/readiness: `NOT_READY`

## 1. Scope

This is a code-generation-ready no-live fix plan. It does not implement the fix, modify source/tests/runtime/prompts/README/design/control docs, run live/provider/network/PDF/FDR/source/acquisition/analyze/checklist/golden/readiness/release/PR commands, or change external state.

The implementation gate must preserve:

- Exact marker contract: `<!-- anchor:<anchor_id> -->`.
- EID single-source/no-fallback policy.
- Provider defaults, repair budget defaults, annual-period LLM route, Docling/source policy, release/readiness state and PR state.
- Current fail-closed Route C semantics: no deterministic fallback for `--use-llm`.

Out of scope:

- Parser relaxation or accepting alternative marker syntax.
- Eastmoney, fund-company, CNINFO, fallback, FDR/source/acquisition/PDF work.
- Provider runtime/default/budget changes.
- Chapter repair budget calibration.
- Annual-period LLM route or multi-period disclosure route.
- Golden/readiness/release/PR movement.

## 2. Evidence Basis

Accepted inputs:

- `docs/reviews/provider-llm-chapter6-invalid-marker-no-live-diagnostic-evidence-controller-judgment-20260614.md`
- `docs/reviews/provider-llm-chapter6-invalid-marker-no-live-diagnostic-evidence-20260614.md`
- `docs/reviews/provider-llm-chapter6-invalid-marker-no-live-diagnostic-evidence-review-ds-20260614.md`
- `docs/reviews/provider-llm-chapter6-invalid-marker-no-live-diagnostic-evidence-review-mimo-20260614.md`
- checkpoint `10d9373`

Accepted diagnostic facts used by this plan:

- D1 proves current Chapter 6 prompt rendering already includes the exact anchor syntax, allowed-anchor boundary, no synthesized anchor IDs, and bond-risk internal/组级 anchor prohibition.
- D2 proves parser taxonomy is working: malformed anchor comments route to `invalid_marker` / `llm_contract_violation`; syntactically valid but unauthorized anchors route to `unknown_anchor`.
- D3 proves diagnostics are safe and count `writer:invalid_anchor_marker` into `invalid_marker_count` without leaking raw malformed marker suffixes.
- D4 proves the current gap: `invalid_marker` writer blocks return before audit/repair, so no invalid-marker repair context exists today.
- Both reviews accepted D1-D4 and supported proceeding to a narrow no-live fix planning gate.

Current code facts checked for planning:

- `fund_agent/fund/chapter_writer.py` renders `<!-- anchor:<anchor_id> -->` in the initial protocol and validates malformed markers through `writer:invalid_anchor_marker`.
- `fund_agent/agent/runner.py` currently returns immediately when `writer_result.status == "blocked"`, before `decide_repair()` or `repair_context_from_audit()`.
- `fund_agent/agent/repair.py` currently builds repair context only from audit issues; the generic anchor correction does not include the exact marker syntax.
- `fund_agent/services/chapter_orchestrator.py` delegates current orchestration through the Agent bridge, so the behavioral fix should live in the Agent runner/repair path rather than a parallel Service retry loop.

## 3. Fix Strategy Decision

Decision: add a writer-block repair/retry path for Chapter 6 `invalid_marker` only, consuming the existing per-chapter content repair attempt budget.

Do not strengthen the initial Chapter 6 writer prompt in this gate.

Rationale:

- The accepted D1 evidence shows the initial prompt already contains the exact marker contract and Chapter 6 bond-risk anchor boundary. A salience-only change would mostly duplicate existing contract text and would not address the D4-proven terminal writer-block gap.
- The strongest proven missing mechanism is D4: an `invalid_marker` parse block never reaches audit-derived repair context. A narrow writer-block retry directly closes that gap.
- The retry must be budget-consuming. With current default `max_content_repair_attempts=1`, a Chapter 6 invalid-anchor marker may receive at most one regenerate attempt. With budget `0`, it must not retry. If the retry also returns `invalid_marker`, it must fail closed without hidden third attempt.
- The retry context must carry exact syntax guidance: `<!-- anchor:<anchor_id> -->`, use only allowed anchor IDs, delete malformed or synthesized anchors, and do not cite `bond_risk_evidence` internal/组级 anchors unless they are present in the allowed anchor set.

Implementation shape:

- Add a narrow helper in `fund_agent/agent/repair.py`, for example `repair_context_from_writer_invalid_marker(writer_result, attempt_index=...)`.
- The helper must only be used when all are true:
  - current `chapter_id == 6`;
  - `writer_result.status == "blocked"`;
  - `writer_result.stop_reason == "llm_contract_violation"`;
  - at least one writer issue id starts with `writer:invalid_anchor_marker`;
  - remaining content repair budget is greater than `0`.
- In `fund_agent/agent/runner.py`, before returning the current writer-block terminal task, branch to this helper only for that eligible case. Append the current failed attempt to the ledger, increment `attempt_index`, build a new writer input with the writer-block repair context, and continue the existing writer loop.
- Reuse the existing repair phase event convention if phase events are recorded, but do not introduce new provider/runtime budget knobs.
- Keep parser behavior unchanged. The first malformed output still fails validation; the only change is whether a budgeted retry is attempted.

## 4. Rejected Alternatives

Prompt salience only: rejected for this gate. D1 proves the initial prompt already renders the exact syntax and Chapter 6-specific anchor boundary, while D4 proves the missing repair-context path. Salience-only does not close the proven terminal writer-block gap.

Both prompt salience and writer-block retry: rejected as unnecessarily broad under current evidence. The behavioral gap can be closed by a budgeted writer-block retry that injects exact syntax in repair context. Initial prompt edits can be reconsidered only if no-live or later bounded evidence shows retry context is insufficient.

Parser relaxation: rejected. D2 proves strict taxonomy is correct under the accepted contract. Any alternate syntax acceptance is a future product/contract gate.

Budget increase: rejected. The retry consumes existing per-chapter content repair budget. It must not change `AgentRepairPolicy(max_content_repair_attempts=1)`, `ChapterOrchestrationPolicy(max_repair_attempts=1)`, provider attempts, timeout defaults or runtime plan defaults.

Source/fallback/provider work: rejected. The blocker is writer output-format noncompliance, not annual-report acquisition or provider configuration.

## 5. Allowed Write Set for Implementation Gate

Implementation gate may modify only:

- `fund_agent/agent/repair.py`
- `fund_agent/agent/runner.py`
- `tests/agent/test_repair_policy.py`
- `tests/agent/test_runner.py`
- `tests/services/test_chapter_orchestrator.py`
- `tests/fund/test_chapter_writer.py`

Conditional write:

- `tests/services/test_fund_analysis_service_llm.py` only if the implementation changes Service-level incomplete-run or final-assembly diagnostics. It should not be touched for a pure Agent runner/repair implementation.

Not allowed:

- `fund_agent/fund/chapter_writer.py`, unless implementation proves the existing repair-context renderer cannot render the exact correction text from `ChapterRepairContext`. The current preferred plan does not require modifying it.
- Any writer/auditor/repair markdown body.
- Provider config, runtime defaults, source/FDR/cache/PDF code, README, `docs/design.md`, `docs/implementation-control.md`, release/readiness/PR artifacts.

## 6. Red-test-first Validation Plan

Implementation must start with fake-input no-live red tests and record that they fail before source changes.

Required red tests:

1. `tests/agent/test_runner.py`
   - Given Chapter 6 writer first returns malformed `<!-- ANCHOR:... -->` and second returns valid exact marker output.
   - With `AgentRepairPolicy(max_content_repair_attempts=1)`, current code should red-fail because it returns after one writer-block attempt.
   - After implementation, it must call writer twice, set second request `repair_context.attempt_index == 1`, include exact marker correction in `required_corrections`, and accept the chapter if the second output is valid.

2. `tests/agent/test_runner.py`
   - Given Chapter 6 writer returns malformed anchor marker twice.
   - With `max_content_repair_attempts=1`, after implementation it must call writer exactly twice, record attempts `[0, 1]`, fail closed, and perform no hidden third retry.

3. `tests/agent/test_runner.py`
   - Given Chapter 6 writer returns malformed anchor marker.
   - With `max_content_repair_attempts=0`, it must call writer once and preserve current writer-block failure classification.

4. `tests/agent/test_runner.py`
   - Given non-Chapter-6 writer returns malformed anchor marker.
   - With `max_content_repair_attempts=1`, it must not retry. This keeps the gate Chapter 6-scoped.

5. `tests/agent/test_repair_policy.py`
   - New helper builds a sanitized `ChapterRepairContext` from writer invalid-anchor issues:
     - previous issue IDs keep safe issue IDs;
     - previous messages are sanitized;
     - required corrections include exact `<!-- anchor:<anchor_id> -->`;
     - raw malformed marker text is not introduced by the helper.

6. `tests/services/test_chapter_orchestrator.py`
   - Through `orchestrate_chapters()`, fake Chapter 6 first invalid marker then valid retry should accept with `max_repair_attempts=1`.
   - With `max_repair_attempts=0`, fake Chapter 6 invalid marker should not retry.

7. `tests/fund/test_chapter_writer.py`
   - Existing repair-context renderer must render the exact correction text from `ChapterRepairContext` without using `extra_payload`.

All tests must use fake snippets/clients only. No live/provider/network/PDF/FDR/source/acquisition/analyze/checklist/golden/readiness/release/PR commands.

## 7. Implementation Steps

1. Add repair-policy helper.
   - In `fund_agent/agent/repair.py`, add a narrow function such as `repair_context_from_writer_invalid_marker(writer_result, attempt_index=...)`.
   - Import or type against `ChapterWriteResult` only if needed.
   - Use existing `_sanitize_text()` mechanics for messages.
   - Produce `ChapterRepairContext` with required corrections that explicitly say:
     - use exact `<!-- anchor:<anchor_id> -->`;
     - use only allowed anchor IDs from the prompt;
     - delete malformed `ANCHOR`, extra-space, synthesized, or free-form anchor comments;
     - do not use `bond_risk_evidence` internal/组级 anchors unless they are listed as allowed `ChapterEvidenceAnchor` IDs.
   - Do not add source probing, provider calls, config fields, or budget defaults.

2. Add Agent runner branch.
   - In `fund_agent/agent/runner.py`, before the existing writer-block return, compute whether the writer block is eligible for retry.
   - Eligibility must require Chapter 6, `llm_contract_violation`, `writer:invalid_anchor_marker`, and remaining content repair budget > 0.
   - For eligible failures:
     - append the current attempt with terminal state `blocked_prompt_contract`;
     - record repair phase start/completion consistently with existing regenerate flow if phase recorder is used;
     - increment `attempt_index`;
     - rebuild `writer_input` with `repair_context_from_writer_invalid_marker(...)`;
     - continue the existing loop.
   - For ineligible failures, keep current behavior exactly.

3. Preserve diagnostics.
   - Do not change `_terminal_from_writer_stop_reason()`, `_failure_category_from_writer_result()` or parser taxonomy unless tests prove a minimal diagnostic addition is required.
   - Do not leak raw malformed marker text into serialized diagnostics.
   - Attempt ledger must make budget consumption visible through attempt indexes and writer request count.

4. Update tests in the red-test-first sequence from Section 6.

5. Run focused no-live verification only after implementation.

## 8. Verification Matrix

Minimum implementation-gate commands:

```text
uv run pytest -q tests/agent/test_repair_policy.py tests/agent/test_runner.py tests/services/test_chapter_orchestrator.py tests/fund/test_chapter_writer.py
uv run ruff check fund_agent/agent/repair.py fund_agent/agent/runner.py tests/agent/test_repair_policy.py tests/agent/test_runner.py tests/services/test_chapter_orchestrator.py tests/fund/test_chapter_writer.py
git diff --check
```

Expected evidence:

| Check | Expected result |
|---|---|
| Red tests before implementation | Fail for the new writer-block retry behavior |
| Chapter 6 invalid-anchor first fail then valid retry | Accepted after exactly one budgeted retry |
| Chapter 6 invalid-anchor repeated failure | Fail closed after exactly two writer calls with default budget 1 |
| Budget 0 | No writer-block retry |
| Non-Chapter-6 invalid-anchor marker | No retry |
| Repair context | Exact `<!-- anchor:<anchor_id> -->` guidance present; no `extra_payload` |
| Parser taxonomy | Malformed marker remains `invalid_marker`; unauthorized valid anchor remains `unknown_anchor` |
| Diagnostics | Safe counts/prefixes only; no raw provider or malformed marker body leakage |
| Source policy | No source/FDR/PDF/fallback code touched |
| Release/readiness | Remains `NOT_READY` |

No live/provider/network/PDF/FDR/source/acquisition/analyze/checklist/golden/readiness/release/PR commands are part of this matrix.

## 9. Residuals and Non-goals

Residuals:

- This plan does not prove that a future provider sample will pass; it only defines the no-live narrow fix and fake-input acceptance criteria.
- If the retry also fails, Chapter 6 remains fail-closed.
- Current one-repair default remains uncalibrated product policy; calibration is still a future standard gate.
- Actual malformed live marker body remains unread and unnecessary for this no-live fix plan.

Non-goals:

- No parser relaxation.
- No prompt-body markdown edits.
- No source, fallback, Docling, annual-period LLM, provider default or runtime budget changes.
- No final assembly, golden, readiness, release or PR claim.

## 10. Next Gate Recommendation

Proceed to:

```text
Provider/LLM Chapter 6 Invalid-marker Narrow No-live Fix Implementation Gate
```

Required implementation-gate constraints:

- Apply the writer-block retry only for Chapter 6 `writer:invalid_anchor_marker`.
- Consume existing per-chapter content repair budget; do not increase defaults.
- Start with red/fake-input no-live tests.
- Preserve exact marker contract and fail-closed behavior.
- Preserve EID single-source/no-fallback and `NOT_READY`.

## 11. Final Verdict

VERDICT: PROCEED_TO_NARROW_NO_LIVE_FIX_IMPLEMENTATION_GATE_NOT_READY
