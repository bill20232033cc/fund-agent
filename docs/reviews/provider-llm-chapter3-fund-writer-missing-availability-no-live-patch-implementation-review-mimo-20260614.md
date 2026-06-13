# Provider/LLM Chapter 3 Fund-writer Missing-availability No-live Patch Implementation Review - MiMo - 2026-06-14

Status: `REVIEW_COMPLETE`

Gate: `Provider/LLM Chapter 3 Fund-writer Missing-availability No-live Patch Gate`

Reviewer: MiMo

Review scope:
- `fund_agent/fund/chapter_writer.py`
- `tests/agent/test_runner.py`
- Implementation evidence: `docs/reviews/provider-llm-chapter3-fund-writer-missing-availability-no-live-patch-implementation-evidence-procodex-20260614.md`

Forbidden actions: no live/provider/network/analyze/checklist/readiness/release/PR commands; no source/PDF/cache/FDR access; no chapter body/raw prompt/provider payload reads; no source test/control/design modification; no stage/commit/push/open PR.

---

## 1. Diff Summary

### `fund_agent/fund/chapter_writer.py`

Three targeted changes at the typed required-output availability boundary:

1. **`_availability_for_required_output()` (line 971-990)**: Previously re-raised `ValueError` when `evidence_availability.require()` failed AND `item.when_evidence_missing` was declared. Now catches `ValueError` unconditionally and returns `None`. Docstring updated to reflect "no explicit raises".

2. **`_required_output_plan_item()` (line 931-968)**: Added `missing_availability = requirement is None and item.when_evidence_missing is not None`. Changed action assignment from unconditional `_required_output_action(item, status)` to `"block" if missing_availability else _required_output_action(item, status)`.

3. **`_required_output_evidence_plan()` (line 905-928)**: Docstring only — clarified "完全缺少 availability" vs "缺少 availability" to distinguish envelope-missing from requirement-missing.

### `tests/agent/test_runner.py`

Two new regression tests added:

1. `test_chapter_3_missing_typed_availability_blocks_before_provider` (line 253-299): Monkeypatches `derive_evidence_availability` to return `EvidenceAvailability` with empty `requirements=()`. Asserts: `writer.requests == []`, `task.status == "blocked"`, `task.terminal_state == "blocked_fact_gap"`, `task.stop_reason == "missing_required_facts"`, `task.failure_category == "fact_gap"`, evidence plan contains `action="block"` for `ch3.required_output.item_03`.

2. `test_chapter_3_missing_evidence_availability_envelope_remains_value_error` (line 301-318): Calls `build_chapter_writer_input` with `evidence_availability=None` and typed items, then asserts `write_chapter` raises `ValueError` matching `"EvidenceAvailability"` and `writer.requests == []`.

---

## 2. Review Questions

### Q1: Does the implementation correctly convert provided-but-missing typed required-output availability with declared `when_evidence_missing` into writer-preflight fact-gap blocking?

**VERDICT: YES**

Execution trace for the covered missing case:

1. `EvidenceAvailability` is provided (not `None`) → `_required_output_evidence_plan()` does NOT raise `ValueError` (line 921 guard passes).
2. For a typed item whose `item_id` has no matching requirement in `evidence_availability.requirements`, `evidence_availability.require()` raises `ValueError` → `_availability_for_required_output()` catches it, returns `None` (line 988-990).
3. Back in `_required_output_plan_item()`: `requirement = None`, so `status = None`, `missing = False` (since `None not in _MISSING_EVIDENCE_STATUSES`), `missing_availability = True` (since `requirement is None and item.when_evidence_missing is not None`), `action = "block"` (line 956).
4. `_required_output_preflight_issues()` iterates plan items with `action == "block"` → emits `ChapterWriteIssue` with `reason="missing_required_facts"` (line 1103-1113).
5. `_preflight_issues()` collects these issues → `write_chapter()` returns `_blocked_result()` with `stop_reason="missing_required_facts"` (line 761-762).
6. LLM client is never called — confirmed by test assertion `writer.requests == []`.

The boundary conversion is correct and deterministic.

### Q2: Does it preserve true missing EvidenceAvailability envelope as ValueError / code_bug?

**VERDICT: YES**

When `evidence_availability is None` AND typed items are enabled, `_required_output_evidence_plan()` raises `ValueError("typed required output 写作路径必须显式传入 EvidenceAvailability")` at line 922. This happens BEFORE `_required_output_plan_item()` is reached.

Test `test_chapter_3_missing_evidence_availability_envelope_remains_value_error` confirms:
- `write_chapter()` raises `ValueError` matching `"EvidenceAvailability"`.
- `writer.requests == []` — no provider call attempted.

The two paths are cleanly separated:
- Envelope missing (`evidence_availability is None`) → `ValueError` (fail-closed configuration error).
- Envelope present, requirement missing (`requirement is None`, `when_evidence_missing` declared) → `action="block"` (deterministic preflight fact-gap).

### Q3: Does it avoid provider calls on the fixed path?

**VERDICT: YES**

Both new tests assert `writer.requests == []`. The `write_chapter()` function's control flow (line 759-762) checks `_preflight_issues()` BEFORE reaching `llm_client.generate_chapter()` (line 773). When preflight issues exist, the function returns early with `_blocked_result()`.

### Q4: Does it avoid masking errors in Agent runner, Service bridge or orchestrator?

**VERDICT: YES**

- No source code in `fund_agent/agent/`, `fund_agent/services/`, or `fund_agent/host/` was modified.
- No runner/Service/orchestrator logic was changed to catch or reinterpret `ValueError` or `ChapterWriteResult` status.
- Implementation evidence confirms targeted no-masking tests passed:
  - `test_typed_contract_path_preserves_independent_body_execution`
  - `test_chapter_3_writer_input_value_error_serializes_safe_runtime_cap_before_writer_tool`
  - `test_analyze_with_llm_execution_projects_chapter_3_value_error_as_code_bug_safe_diagnostic`

### Q5: Are tests sufficient and no-live boundaries respected?

**VERDICT: YES, with minor observation**

Test coverage:

| Scenario | Test | Status |
|---|---|---|
| Covered missing availability → block before provider | `test_chapter_3_missing_typed_availability_blocks_before_provider` | PASS |
| True envelope missing → ValueError | `test_chapter_3_missing_evidence_availability_envelope_remains_value_error` | PASS |
| Writer input ValueError before writer tool | `test_chapter_3_writer_input_value_error_is_internal_code_bug_before_writer_tool` | PASS |
| Full test_runner.py suite | 15 tests | PASS |
| Service/orchestrator no-masking guards | 3 tests | PASS |
| Ruff | PASS |
| Whitespace check | PASS |

Red-test-first discipline: evidence shows the new regression test failed before implementation (`AssertionError: assert 'failed' == 'blocked'`) and passed after.

No-live boundaries: No live/provider/network/analyze/checklist/readiness/release/PR commands were run. Source policy, fallback, repair budget, Docling, annual-period LLM route and provider defaults were not changed.

**Minor observation**: The regression test asserts one specific item (`ch3.required_output.item_03`) has `action="block"`, but does not assert the total count of blocked items or that ALL typed items in the plan are blocked. With `requirements=()`, ALL typed items for chapter 3 would have `requirement is None`, so all with `when_evidence_missing` would be `"block"`. This is a non-blocking observation — the test captures the core regression path, and the zero-provider-call assertion (`writer.requests == []`) covers the critical invariant regardless of item count.

### Q6: Is no fund_agent/fund/README.md update acceptable for this internal fail-closed routing fix, or is README sync required by AGENTS.md?

**VERDICT: No README sync required**

AGENTS.md `fund_agent/fund/` 修改 → 更新 `fund_agent/fund/README.md` trigger rule applies. However:

- The change is to internal routing logic within `_availability_for_required_output()` and `_required_output_plan_item()` — private functions, not public API.
- No public interface, export, class, or documented behavior changed.
- The `fund_agent/fund/README.md` documents Fund package architecture, CHAPTER_CONTRACT mechanism, audit rules, and public interfaces — none of which are affected by this internal boundary adjustment.
- The fix converts a previously-unhandled edge case (ValueError surfacing as code_bug) into deterministic preflight blocking, which is closer to the documented fail-closed contract, not a deviation from it.

No README update is needed.

---

## 3. Correctness Analysis

### Boundary separation is clean

The two failure modes are correctly separated:

| Condition | `evidence_availability` | `requirement` | `when_evidence_missing` | Result |
|---|---|---|---|---|
| True envelope missing | `None` | N/A | N/A | `ValueError` in `_required_output_evidence_plan()` |
| Envelope present, requirement missing | provided | `None` | declared | `action="block"` in `_required_output_plan_item()` |
| Envelope present, requirement missing | provided | `None` | `None` | Falls through to `_required_output_action()` which raises `ValueError` (existing behavior) |
| Envelope present, requirement present | provided | found | N/A | Normal `_required_output_action()` routing |

The third row (requirement missing, no `when_evidence_missing`) is correctly preserved — the existing `_required_output_action()` raises `ValueError("typed required output 缺证但未声明 when_evidence_missing")` at line 1015. This path was NOT changed by the fix.

### `status=None` propagation is correct

When `requirement is None`:
- `status = requirement.status if requirement is not None else None` → `status = None`
- `missing = None in _MISSING_EVIDENCE_STATUSES` → `False` (correct; `None` is not in the frozenset)
- `missing_availability = None is None and item.when_evidence_missing is not None` → depends on item

The `status=None` is correctly handled downstream in `_required_output_prompt_instruction()` which returns a block instruction string including `状态=None` — this is safe diagnostic text, not user-facing.

### Docstring accuracy

The `_required_output_evidence_plan()` docstring change from "缺少 availability" to "完全缺少 availability" correctly distinguishes the envelope-missing case (which raises) from the requirement-missing case (which now blocks). The `_availability_for_required_output()` docstring correctly removes the `ValueError` from the Raises section since it now catches and returns `None`.

---

## 4. Adversarial Failure Analysis

### Edge case: typed item with `when_evidence_missing=None` and missing requirement

If a typed item has `when_evidence_missing=None` and the requirement is missing, the fix's `missing_availability` check evaluates to `False` (since `item.when_evidence_missing is not None` is `False`). Control falls through to `_required_output_action(item, status=None)` which returns `"render"` (line 1011: `if status == "available" or status is None: return "render"`). This means the item would be rendered without availability data — but this is the existing pre-fix behavior and is outside the scope of this gate (items without `when_evidence_missing` are expected to have requirements mapped).

### Edge case: multiple typed items, some blocked, some not

If a mix of items exist where some have requirements and some don't, only the missing-requirement items with `when_evidence_missing` declared would get `action="block"`. The `_required_output_preflight_issues()` would emit blocking issues for those items. `write_chapter()` would return blocked. This is correct — partial availability with declared missing behaviors should block the chapter rather than generate incomplete content.

### Edge case: test isolation

`test_chapter_3_missing_typed_availability_blocks_before_provider` monkeypatches `derive_evidence_availability` at the runner module level. This is scoped to the test function via `monkeypatch` fixture and does not leak to other tests. Verified by the full suite passing (15/15).

---

## 5. Module Boundary Compliance

- Fix is entirely within `fund_agent/fund/chapter_writer.py` (Agent layer, Fund capability package).
- No Host, Service, or UI boundary violations.
- No new imports from `fund_agent.host` or `fund_agent.services`.
- `fund_agent/fund/evidence_availability.py` was inspected but NOT changed — the fix is in the consumer, not the provider, of availability data.
- Test file imports only from `fund_agent.fund` and `tests` — boundary-clean.

---

## 6. AGENTS.md Compliance Check

| Rule | Status | Notes |
|---|---|---|
| 用中文回答 | N/A | Review artifact is in English per gate convention |
| 真源文档规范 | COMPLIANT | No design/control doc changes |
| 模块边界 | COMPLIANT | Fix within Agent layer Fund package |
| 硬约束 - 第一性原理 | COMPLIANT | Fix addresses confirmed root cause, not symptom |
| 硬约束 - 证据必须可溯源 | COMPLIANT | Red-test-first evidence documented |
| 设计和代码编写原则 - 注释与文档 | COMPLIANT | Docstrings updated |
| 设计和代码编写原则 - 代码结构 | COMPLIANT | No nested functions/classes added |
| 设计和代码编写原则 - 测试策略 | COMPLIANT | Red-test-first, regression tests added |
| 文档同步 - README | COMPLIANT | Internal routing fix, no public contract change |
| 年报来源 fallback 策略 | COMPLIANT | No source/fallback changes |
| 禁止事项 | COMPLIANT | No buy/sell advice, no predictions |

---

## 7. Findings

### F1 (Non-blocking): Regression test does not assert total blocked item count

The test `test_chapter_3_missing_typed_availability_blocks_before_provider` asserts that at least one plan item has `action="block"` for `ch3.required_output.item_03`, but does not assert the total number of blocked items or that the entire plan is blocked. With `requirements=()`, all typed items with `when_evidence_missing` would be blocked. The `writer.requests == []` assertion covers the critical invariant (no provider calls), so this is non-blocking.

**Severity**: Informational
**Recommendation**: Consider adding `assert all(plan.action == "block" for plan in writer_result.prompt.required_output_evidence_plan)` for completeness in a follow-up.

---

## 8. Final Verdict

**PASS_WITH_FINDINGS**

The implementation correctly:
1. Converts provided-but-missing typed required-output availability with declared `when_evidence_missing` into deterministic writer-preflight fact-gap blocking (Q1: YES).
2. Preserves true missing `EvidenceAvailability` envelope as `ValueError` / code_bug (Q2: YES).
3. Avoids provider calls on the fixed path (Q3: YES).
4. Avoids masking errors in Agent runner, Service bridge or orchestrator (Q4: YES).
5. Has sufficient tests with no-live boundaries respected (Q5: YES).
6. Does not require `fund_agent/fund/README.md` update for this internal fix (Q6: No sync needed).

One non-blocking informational finding (F1): regression test does not assert total blocked item count.

Residuals from implementation evidence remain valid:
- Provider readiness and provider-response classification remain unproven.
- LLM content quality remains unaccepted.
- Release/readiness remains `NOT_READY`.
