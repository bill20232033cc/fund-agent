# Provider/LLM Chapter 3 No-live Code-bug Root-cause/Fix Verification Review - MiMo - 2026-06-14

Date: 2026-06-14

Reviewer: AgentMiMo

Gate: `Provider/LLM Chapter 3 No-live Code-bug Root-cause/Fix Verification Gate`

Target artifact: `docs/reviews/provider-llm-chapter3-no-live-code-bug-root-cause-fix-verification-evidence-procodex-20260614.md`

Release/readiness: `NOT_READY`

## 1. Review Scope

Per the deepreview prompt:

- Determine whether the `BLOCKED_NEEDS_CONTROLLER_DECISION` verdict is supported.
- Check whether the root-cause classification is coherent: typed required-output / availability gap can still surface as pre-provider `ValueError` / `code_bug`, provider attempt count 0.
- Check whether proposed next write-set expansion to `fund_agent/fund/chapter_writer.py` and maybe `evidence_availability` / typed sidecar is justified, or whether the worker should have fixed inside existing allowed files.
- Verify no-live boundary, no source/fallback expansion, no readiness/provider/content-quality overclaim.

## 2. Evidence Reviewed

Truth/control:

- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`

Target artifact:

- `docs/reviews/provider-llm-chapter3-no-live-code-bug-root-cause-fix-verification-evidence-procodex-20260614.md`

Prior retry/fix judgments:

- `docs/reviews/provider-llm-chapter3-bounded-live-re-evidence-retry-controller-judgment-20260614.md`
- `docs/reviews/provider-llm-chapter3-provider-before-code-bug-no-live-fix-implementation-controller-judgment-20260614.md`

Scoped code inspection (read-only, no modification):

- `fund_agent/fund/chapter_writer.py` (lines 905-928, 970-992, 1091-1114, 616, 741-762)
- `fund_agent/agent/runner.py` (lines 277-356, 595-629, 907-962, 1399-1481)
- `fund_agent/services/agent_bridge.py` (lines 533-534)
- `fund_agent/services/chapter_orchestrator.py` (lines 1284-1301, 2691-2714)

## 3. Verdict Support Assessment

### 3.1 Is `BLOCKED_NEEDS_CONTROLLER_DECISION` supported?

**YES.** The evidence artifact correctly identifies:

1. The remaining Chapter 3 failure is a pre-provider `ValueError` / `code_bug` with `provider_attempt_count=0`.
2. The semantic fix belongs in `fund_agent/fund/chapter_writer.py`, outside the worker's allowed write set.
3. No production code change was made; the worker correctly deferred the fix.
4. A controller decision is required to authorize write-set expansion.

The verdict is well-formed: the worker completed its scoped investigation, identified the root cause, proved it with a temporary red reproducer, and correctly escalated rather than patching in the wrong layer.

### 3.2 Is the root-cause classification coherent?

**YES.** Independent code inspection confirms the evidence artifact's classification.

The error flow is:

1. `_typed_required_output_items()` in `runner.py` returns items with `when_evidence_missing` for Chapter 3.
2. `_writer_input()` constructs `ChapterWriterInput` with these typed items but `evidence_availability` is `None` or missing the corresponding requirement.
3. `write_chapter_tool()` -> `write_chapter()` -> `build_chapter_prompt()` calls `_required_output_evidence_plan()` at `chapter_writer.py:616`.
4. `_required_output_evidence_plan()` at line 922 raises `ValueError("typed required output 写作路径必须显式传入 EvidenceAvailability")` because `evidence_availability is None`.
5. A second site at line 992 (`_availability_for_required_output`) raises `ValueError` when an item has `when_evidence_missing` but no matching requirement in the `EvidenceAvailability` object.
6. The `ValueError` escapes `write_chapter_tool` (which catches it internally as `ToolExecution.exception`), reaches `_exception_task()` in `runner.py`, and is classified as `blocked_internal_code_bug` / `code_bug` / `llm_exception`.

The critical insight is that `_required_output_preflight_issues()` (line 1091-1114) is designed to catch items with `action == "block"` and return them as `"missing_required_facts"` issues, which `write_chapter()` would convert to a `_blocked_result` with `fact_gap` classification. But the `ValueError` from `_required_output_evidence_plan()` fires **before** the preflight can complete, so the fail-closed fact-gap path is never reached.

The H3 classification (within worker scope) with H1 at product/runtime level is accurate. This is not a diagnostic projection gap (H2 rejected correctly); the metadata is now complete (`max_output_chars=12000`, `provider_attempt_count=0`), but the code path itself converts a typed availability gap into a `ValueError` instead of a writer-preflight `fact_gap` block.

### 3.3 Is the proposed write-set expansion justified?

**YES.** The fix must be in `fund_agent/fund/chapter_writer.py`:

- `_required_output_evidence_plan()` (line 922) should not raise `ValueError` when typed items have `when_evidence_missing` set and availability is missing. Instead, it should return plan items with `action == "block"`.
- `_availability_for_required_output()` (line 992) should similarly route to `action == "block"` rather than raising when `when_evidence_missing` is set.
- `_required_output_preflight_issues()` (line 1091-1114) would then convert these to `"missing_required_facts"` issues, causing `write_chapter()` to return a blocked result.

The worker correctly rejected in-scope workarounds:

- Patching `runner.py` to reclassify would mask the typed mapping failure and weaken fail-closed evidence.
- Patching `agent_bridge.py` or `chapter_orchestrator.py` to fabricate availability would inject Fund-domain semantics at the wrong layer.

The proposed companion files (`evidence_availability.py` or typed sidecar) are correctly flagged as conditional: they are needed only if the mapping is incomplete rather than the writer behavior too strict. This is a controller-level investigation decision.

### 3.4 No-live boundary verification

**PASS.** No violations detected:

- No live/provider/network/analyze/checklist/readiness/release/PR commands were run.
- No source/FDR/provider/live path was used.
- EID single-source/no-fallback remains unchanged.
- The temporary red reproducer was removed after failure capture; no test change was retained.
- No production code change was made.
- `NOT_READY` is preserved throughout.

### 3.5 Overclaim check

**PASS.** The evidence artifact correctly rejects:

| Claim | Disposition | Correct? |
|---|---|---|
| Provider readiness is proven | REJECT | YES. `provider_attempt_count=0`. |
| LLM content quality is accepted | REJECT | YES. No body read. |
| EID source policy or fallback changed | REJECT | YES. No source path used. |
| A narrow fix can be safely made inside this worker's write set | REJECT | YES. Fix belongs in `chapter_writer.py`. |
| Release/readiness can advance | REJECT | YES. `NOT_READY` preserved. |

## 4. Red-reproducer Assessment

The temporary red reproducer was correctly designed:

- Monkeypatched `derive_evidence_availability` to return empty `EvidenceAvailability`.
- Executed Chapter 3 only with `typed_template_path`.
- Used fake writer/auditor clients (no provider/network).
- Expected writer-preflight fact-gap block with one writer attempt and zero provider calls.
- Observed: `task.status == "failed"` instead of `"blocked"`, with `writer.requests == []` passing before the failed assertion.

The `writer.requests == []` fact proves the failure is pre-provider. The reproducer was removed because the semantic fix requires editing outside the allowed write set. This is correct gate discipline.

## 5. Residual Assessment

The evidence artifact's residuals are well-formed:

| Residual | Owner | Assessment |
|---|---|---|
| Chapter 3 typed required-output availability gap surfaces as pre-provider ValueError / code_bug | Controller + Fund writer/typed availability owner | Correct. Fix requires `chapter_writer.py` edit. |
| Provider readiness and provider-response classification remain unproven | Provider/runtime owner | Correct. No live retry until no-live root cause is fixed. |
| LLM content quality remains unaccepted | Provider/runtime + chapter owners | Correct. Future gate only after complete accepted run. |
| Release/readiness remains NOT_READY | Release owner/controller | Correct. |

## 6. Observations (non-blocking)

1. **Routing gap.** The evidence artifact does not explain how typed required-output items reach Chapter 3 without corresponding evidence availability. The Explore agent confirmed that `_typed_required_output_items()` returns items with `when_evidence_missing` for Chapter 3, but the mechanism by which `evidence_availability` ends up `None` or missing the requirement is not traced. This is a legitimate residual for the controller's write-set authorization decision: the fix may need to be in the availability mapping rather than (or in addition to) the writer's error handling.

2. **Scope of `when_evidence_missing`.** The fix should distinguish between "availability genuinely not provided" (which should remain a ValueError / code_bug indicating a configuration error) and "availability provided but item not covered" (which should route to `action == "block"` / `fact_gap`). The evidence artifact's patch plan step 2 correctly notes this distinction ("items with declared `when_evidence_missing`"), but the controller should confirm this boundary when authorizing the write set.

## 7. Final Verdict

**VERDICT: PASS_BLOCKED**

The `BLOCKED_NEEDS_CONTROLLER_DECISION` verdict is correctly supported. The root-cause classification is coherent and independently verified by code inspection. The proposed write-set expansion to `fund_agent/fund/chapter_writer.py` is justified. The no-live boundary was maintained with no overclaims. The red reproducer was properly temporary. `NOT_READY` is preserved.
