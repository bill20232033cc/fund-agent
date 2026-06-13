# Provider/LLM Chapter 3 Fund-writer Missing-availability No-live Patch Implementation Review DS - 2026-06-14

Reviewer: AgentDS (role-scoped implementation review)

Gate: `Provider/LLM Chapter 3 Fund-writer Missing-availability No-live Patch Gate`

Release/readiness: `NOT_READY`

## 1. Scope

This is a role-scoped implementation review per the deepreview discipline. Review authority: verify correctness of the implementation diff against the 6 review questions. Non-goal: live/provider/network/analyze/checklist/readiness/release/PR commands. Do not read chapter bodies, raw prompts, provider payloads, reports runtime bodies, source/PDF/cache bodies. Do not modify source/tests/control/design. Do not stage/commit/push/open PR.

Sources read:
- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/reviews/provider-llm-chapter3-fund-writer-missing-availability-no-live-patch-implementation-evidence-procodex-20260614.md`
- `docs/reviews/provider-llm-chapter3-no-live-code-bug-root-cause-fix-verification-controller-judgment-20260614.md`
- `fund_agent/fund/chapter_writer.py`
- `tests/agent/test_runner.py`

## 2. Implementation Trace

The fix is contained in `fund_agent/fund/chapter_writer.py`, affecting two functions:

### 2.1 `_availability_for_required_output()` (line 971-991)

**Before**: `evidence_availability.require(...)` raised `ValueError` when the item requirement was not found. This propagated up through `_required_output_plan_item()` → `_required_output_evidence_plan()` → `build_chapter_prompt()` → `write_chapter()`, eventually surfacing in the Agent runner as `llm_exception` / `code_bug`.

**After**: `except ValueError: return None`. Missing requirement now returns `None` instead of raising.

### 2.2 `_required_output_plan_item()` (line 931-968)

New gating logic:
```python
requirement = _availability_for_required_output(item, evidence_availability)
status = requirement.status if requirement is not None else None
missing_availability = requirement is None and item.when_evidence_missing is not None
action = "block" if missing_availability else _required_output_action(item, status)
```

When `requirement is None` AND `item.when_evidence_missing is not None` → `action = "block"`.

### 2.3 Downstream blocking chain (unchanged)

- `_required_output_preflight_issues()` (line 1090-1113): generates `ChapterWriteIssue` for items with `action == "block"`, using `stop_reason="missing_required_facts"`.
- `_preflight_issues()` (line 830-886): collects all preflight issues including `_required_output_preflight_issues()`.
- `write_chapter()` (line 760-762): returns `_blocked_result()` when preflight issues exist, BEFORE any LLM client call.

### 2.4 Envelope-missing guard (line 921-922, unchanged)

```python
if input_data.evidence_availability is None:
    raise ValueError("typed required output 写作路径必须显式传入 EvidenceAvailability")
```

Complete absence of `EvidenceAvailability` still raises `ValueError`. This was not changed.

### 2.5 Tests added

`tests/agent/test_runner.py`:

1. `test_chapter_3_missing_typed_availability_blocks_before_provider` (line 253-298): monkeypatches `derive_evidence_availability` to return same-identity `EvidenceAvailability` with `requirements=()`. Asserts `writer.requests == []`, `run.status == "blocked"`, `task.terminal_state == "blocked_fact_gap"`, `task.stop_reason == "missing_required_facts"`, `task.failure_category == "fact_gap"`, and that `required_output_evidence_plan` contains a block-action item for `ch3.required_output.item_03`.

2. `test_chapter_3_missing_evidence_availability_envelope_remains_value_error` (line 301-318): passes `evidence_availability=None`, asserts `ValueError` with message `"EvidenceAvailability"`, asserts `writer.requests == []`.

## 3. Review Question Answers

### Q1: Does the implementation correctly convert provided-but-missing typed required-output availability with declared `when_evidence_missing` into writer-preflight fact-gap blocking?

**YES.** The implementation trace confirms:

1. `_availability_for_required_output()` returns `None` when an item is not found in availability (was `ValueError`).
2. `_required_output_plan_item()` detects `requirement is None and item.when_evidence_missing is not None` and sets `action="block"`.
3. `_required_output_preflight_issues()` emits a `missing_required_facts` issue for every block-action plan item.
4. `write_chapter()` returns blocked before reaching `llm_client.generate_chapter()`.

Test evidence: `test_chapter_3_missing_typed_availability_blocks_before_provider` passes with exact assertions on `terminal_state`, `stop_reason`, `failure_category`, and the presence of a block-action plan item.

### Q2: Does it preserve true missing EvidenceAvailability envelope as ValueError / code_bug?

**YES.** `_required_output_evidence_plan()` at line 921-922 still raises `ValueError` when `evidence_availability is None` and typed items are enabled. The code path was not edited.

Test evidence: `test_chapter_3_missing_evidence_availability_envelope_remains_value_error` passes, confirming `ValueError` is raised and `writer.requests == []`.

### Q3: Does it avoid provider calls on the fixed path?

**YES.** The blocking path in `write_chapter()` returns at line 762 before reaching the LLM client call at line 773. Both new tests assert `writer.requests == []`. The evidence reports the red-test-first run already confirmed `writer.requests == []` before the fix, and the post-fix tests reconfirm it.

### Q4: Does it avoid masking errors in Agent runner, Service bridge or orchestrator?

**YES.** No runner, Service bridge, or orchestrator source was edited. The fix is entirely within `fund_agent/fund/chapter_writer.py` (Agent/Fund layer). Three Service/orchestrator no-masking guard tests from authorized test files all pass:
- `test_typed_contract_path_preserves_independent_body_execution`
- `test_chapter_3_writer_input_value_error_serializes_safe_runtime_cap_before_writer_tool`
- `test_analyze_with_llm_execution_projects_chapter_3_value_error_as_code_bug_safe_diagnostic`

The existing runner-layer test `test_chapter_3_writer_input_value_error_is_internal_code_bug_before_writer_tool` also continues to pass, confirming the runner still correctly classifies upstream `ValueError` as `code_bug`.

### Q5: Are tests sufficient and no-live boundaries respected?

**Mostly sufficient, no-live boundaries fully respected.**

Test coverage confirmed:
- Covered missing availability with `when_evidence_missing` → blocks as fact_gap, zero provider calls.
- Envelope-missing (None) → ValueError, zero provider calls.
- Legacy contract path untouched → `test_legacy_contract_does_not_derive_typed_evidence_availability` still passes.
- Runner/Service/orchestrator no-masking → existing tests pass.
- All tests use fake/mock writers; no live/provider/network calls.

**Finding 1 (non-blocking, test coverage gap)**: No test covers `requirement is None AND when_evidence_missing is None`. In the new code this silently renders (action="render") instead of fail-closing. In the old code this would have raised `ValueError`. While the typed contract should always declare `when_evidence_missing` for items that need evidence availability, and items without it that do have a requirement in availability would still fail in `_required_output_action()`, this is a behavioral change worth noting. Recommendation: if a future typed contract update introduces an item without `when_evidence_missing` and without an availability mapping, the writer would silently render it with no evidence rather than failing. This residual should be recorded in the next gate's risk register.

### Q6: Is no fund_agent/fund/README.md update acceptable for this internal fail-closed routing fix?

**Acceptable for this gate.**

AGENTS.md line 210 triggers: `fund_agent/fund/` 修改 → 更新 `fund_agent/fund/README.md`.

But AGENTS.md line 192-193 says: "仅更新 README 中没对齐到代码的部分" and "以代码为准".

Analysis:
- The fix is entirely internal to `chapter_writer.py`. No public API, exported type, documented interface, or documented behavior changed.
- `write_chapter()` still returns `ChapterWriteResult` with `status="blocked"` for problems; the only change is WHICH code path does the blocking (writer preflight instead of `ValueError` propagation). A README reader would see the same documented behavior.
- The implementation evidence states README was inspected and no stale content was found.

**Finding 2 (non-blocking, procedural)**: The strict trigger rule in AGENTS.md line 210 says any `fund_agent/fund/` change → README update. While no update is substantively needed (no public contract changed), the gate's implementation evidence could more explicitly record: "Verified `fund_agent/fund/README.md` — no documented interface affected by this internal routing change." This would strengthen the evidence chain against the strict-trigger challenge. Recommended for the next gate's evidence standard, not a blocker here.

## 4. Cross-check Summary

| Review question | Verdict |
|---|---|
| Q1: Covered missing availability → fact-gap blocking | PASS |
| Q2: Envelope-missing → ValueError preserved | PASS |
| Q3: Zero provider calls on fixed path | PASS |
| Q4: No runner/Service/orchestrator masking | PASS |
| Q5: Test sufficiency and no-live boundaries | PASS_WITH_FINDING |
| Q6: README non-update acceptable | PASS_WITH_FINDING |

## 5. Rejected Claims

| Claim | Disposition | Reason |
|---|---|---|
| Provider readiness is proven | REJECT | No provider call was made. Tests prove zero fake writer calls. |
| LLM content quality is accepted | REJECT | No chapter/report body was read. |
| Release/readiness can advance | REJECT | `NOT_READY` unchanged. This is not a readiness gate. |
| Source policy or fallback changed | REJECT | No source/FDR/fallback file touched. |
| Conditional write-set files need editing | REJECT | `evidence_availability.py` and typed sidecar files were inspected, not changed. The fix in `chapter_writer.py` correctly handles the boundary without modifying the availability module. |

## 6. Accepted Claims

| Claim | Disposition |
|---|---|
| Covered missing typed required-output availability now blocks as writer-preflight fact gap | ACCEPT |
| Missing availability path makes zero provider calls | ACCEPT |
| True missing EvidenceAvailability envelope remains fail-closed ValueError | ACCEPT |
| Runner/Service/orchestrator were not patched to mask Fund semantics | ACCEPT |
| EID single-source/no-fallback and `NOT_READY` are preserved | ACCEPT |
| No-live boundaries respected | ACCEPT |

## 7. Residuals

| Residual | Severity | Owner | Next handling |
|---|---|---|---|
| Untested edge case: `requirement is None AND when_evidence_missing is None` silently renders instead of fail-closing | Low; typed contract design mitigates | Fund writer / typed contract owner | Record in next gate risk register; add defensive test if typed contract surface expands |
| `fund_agent/fund/README.md` not updated despite AGENTS.md line 210 trigger | Non-blocking procedural; README inspected and no stale content found | Implementation evidence owner | Strengthen evidence language in next gate: explicitly state README was checked and no public interface affected |

## 8. Final Verdict

**PASS_WITH_FINDINGS**

The implementation correctly converts provided-but-missing typed required-output availability with declared `when_evidence_missing` into deterministic writer-preflight fact-gap blocking. True missing `EvidenceAvailability` envelope is preserved as `ValueError` / `code_bug`. Zero provider calls occur on the fixed path. No runner, Service bridge, or orchestrator masking was introduced. Tests are sufficient for the gate scope and no-live boundaries are fully respected. Two non-blocking findings: one test coverage gap for an edge case mitigated by typed contract design, and one procedural observation about README update evidence language.
