# Provider/LLM Chapter 3 Provider-before Code-bug No-live Fix Plan — Independent Plan Review

Date: 2026-06-14

Reviewer: AgentDS (independent plan reviewer, role-scoped worker handoff)

Gate: `Provider/LLM Chapter 3 Provider-before Code-bug No-live Fix Gate`

Target: `docs/reviews/provider-llm-chapter3-provider-before-code-bug-no-live-fix-plan-procodex-20260613.md`

Release/readiness: `NOT_READY`

## 1. Scope

This is an independent adversarial plan review only. The review assesses whether the proposed plan is safe to hand to an implementation worker.

In scope:

- Verify the candidate code path is supported by current repo code/test facts.
- Assess whether the red-test-first stop condition is sufficient to avoid speculative fix.
- Check that the minimal write set is properly constrained.
- Confirm preservation of EID single-source/no-fallback, `NOT_READY`, and all non-goal guardrails.
- Evaluate whether proposed tests prove the no-live pre-tool ValueError path and safe diagnostic projection.

Out of scope:

- Source/test/runtime/control-doc/design-doc edits.
- Live/provider/LLM/network/PDF/FDR/source/analyze/checklist/readiness/release/PR commands.
- Stage, commit, push, delete, archive, cleanup, or ignore actions.
- Implementation or controller judgment.

## 2. Evidence Reviewed

Truth sources:

- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/reviews/provider-llm-chapter3-diagnostic-disposition-20260613.md`
- `docs/reviews/workspace-scope-artifact-disposition-closeout-20260613.md`

Code evidence (read to verify plan claims):

- `fund_agent/agent/runner.py` — `_run_single_chapter()` (L290-385), `_writer_input()` (L585-619), `_exception_task()` (L897-952), `_typed_required_output_items()` (L1102-1123), `_typed_chapter_contract()` (L1079-1099), `_terminal_from_exception()` (L1389-1404), `_stop_reason_from_exception()` (L1407-1429), `_failure_category_from_exception()` (L1454-1471)
- `fund_agent/fund/chapter_writer.py` — `build_chapter_writer_input()` (L544-596), `_required_output_evidence_plan()` (L905-928), `_required_output_plan_item()` (L931-967), `_required_output_action()` (L995-1025)
- `fund_agent/fund/template/typed_contracts.py` — `get_typed_chapter_contract()` (L305-322)
- `tests/agent/test_runner.py` — existing Chapter 3 reproducer (L167-194)
- `tests/services/test_chapter_orchestrator.py` — existing serialization test (L1606-1646)
- `tests/services/test_fund_analysis_service_llm.py` — existing Service execution test (L1024-1065)

## 3. Findings

### 3.1 Plan Soundness Assessment

The plan identifies a real, code-supported pre-tool boundary. Below is the code-path verification with direct evidence.

**Path verified.** `_run_single_chapter()` at `runner.py:305-313`:

```python
title = _chapter_title(projection, chapter_id)
attempts: list[ChapterAttempt] = []
writer_input = _writer_input(           # L307 — can raise ValueError
    projection, chapter_id=chapter_id,
    policy=policy, evidence_availability=evidence_availability,
    repair_context=None,
)
attempt_index = 0                       # L314 — NOT YET DEFINED if L307 raises
```

`_writer_input()` calls `build_chapter_writer_input()` (chapter_writer.py:544-596) which raises `ValueError` at L577 (invalid mode), L579 (invalid citation_style), L581 (`max_output_chars <= 0`), L583 (invalid prompt_payload_mode). It also calls `_typed_required_output_items()` (runner.py:1102-1123) → `_typed_chapter_contract()` (runner.py:1079-1099) → `get_typed_chapter_contract()` (typed_contracts.py:305-322) which raises `ValueError` at L322 for unknown chapter_id. Additionally, `_required_output_evidence_plan()` (chapter_writer.py:905-928) raises `ValueError` at L922 when `typed_required_output_items` are present but `evidence_availability` is `None`, and at L951 when an item doesn't belong to the current chapter.

All of these are pre-tool, pre-provider, and before `attempt_index` initialization at L314. If any `ValueError` escapes `_run_single_chapter()`, neither the Agent runner's fail-closed conversion at L338-346 (which handles writer tool exceptions) nor the Service bridge diagnostics can project it through the accepted `llm_exception`/`code_bug`/provider attempt count `0` diagnostic path.

**Existing tests do not cover this pre-tool boundary.** The existing reproducer at `test_runner.py:167-194` injects `ValueError` through `_FakeWriter(actions={3: ValueError(...)})`, which triggers at the `write_chapter_tool()` call (runner.py:326-330) — AFTER the writer request is built. The existing orchestrator test at `test_chapter_orchestrator.py:1606-1646` and Service test at `test_fund_analysis_service_llm.py:1024-1065` use `_FakeChapterLLMClient(exception=exception)`, which similarly injects at the tool-call boundary, not at input construction. The plan correctly distinguishes these as post-request, not pre-tool, and the gap is genuine.

**Proposed fix is minimal and correctly scoped.** The fix touches only `_run_single_chapter()` in `fund_agent/agent/runner.py`:

1. Move `attempt_index = 0` before `_writer_input()`.
2. Wrap initial `_writer_input()` in try/except.
3. On exception, return `_exception_task()` with `traces=()`.
4. Adjust `_exception_task()` to not create a synthetic `ChapterAttempt` when `traces == ()`.

No other source file is modified. Provider defaults, source policy, fallback, repair budget, config, annual-period LLM route, and deterministic path are untouched.

**Red-test-first stop condition is sufficient.** The plan specifies that if Test A does not reproduce an escaped `ValueError` before the source fix, the implementation worker must stop and return `NEED_MORE_NO_LIVE_EVIDENCE`. This prevents speculative fix when the assumed failure path is not confirmed.

### 3.2 Findings Detail

#### Finding 1 — accepted-candidate — 中 — `_exception_task` Modification Ambiguity

- **位置**: §5 Proposed Minimal Fix, lines 129-131
- **问题类型**: 不可直接实施
- **当前写法**: "Adjust `_exception_task(...)` so zero-trace pre-tool exceptions do not create a synthetic attempt record unless the existing dataclass contract requires it. Preferred minimal behavior is: keep `attempts == previous_attempts` when `traces == ()`; keep existing behavior unchanged for writer tool exceptions and auditor/programmatic exceptions."
- **反例/失败场景**: Implementation worker reads `_exception_task()` at runner.py:897-952 and encounters the existing condition at L929: `if len(traces) == 1 and traces[0].request.tool_name == "fund.write_chapter"`. For `traces=()`, `len(traces) == 1` is `False`, so the `else` branch creates a synthetic `ChapterAttempt(tool_traces=(), ...)`. The plan's phrasing "preferred minimal behavior" and "unless the existing dataclass contract requires it" creates ambiguity — the worker must decide whether the dataclass contract permits zero-trace attempts. The correct change (add `len(traces) == 0` to the guard) is inferable but not explicit.
- **为什么有问题**: The implementation worker is asked to interpret intent rather than follow a precise specification. The existing `ChapterAttempt` dataclass does not forbid `tool_traces=()`, so "dataclass contract" is not a clear constraint.
- **直接证据**: `_exception_task()` L927-940 in runner.py shows the current guard condition is `len(traces) == 1 and traces[0].request.tool_name == "fund.write_chapter"`. Adding `or len(traces) == 0` achieves the plan's stated goal. No other caller passes `traces=()` so this change is safe. The plan's "preferred" qualifier and dataclass-contract caveat are unnecessary indirection.
- **影响**: 实施 Agent 跑偏 — the worker might skip the `_exception_task` change entirely (relying on the fact that `traces=()` with a synthetic attempt still works mechanically) or might over-modify the function.
- **建议改法和验证点**: Replace the "preferred minimal behavior" phrasing with: "Change the guard at runner.py:929 from `if len(traces) == 1 and traces[0].request.tool_name == 'fund.write_chapter'` to `if len(traces) == 0 or (len(traces) == 1 and traces[0].request.tool_name == 'fund.write_chapter')`." Verify that existing tests for writer tool exceptions (which pass `traces=(writer_trace,)`) continue to pass.
- **修复风险（低）**: One-line condition change; no other caller passes empty traces.
- **严重程度（中）**: Not a blocker — the intended behavior is clear — but the ambiguity invites implementation drift.

#### Finding 2 — accepted-candidate — 低 — Test A Injection Point is One of Several Valid Paths

- **位置**: §6 Proposed Tests, Test A
- **问题类型**: 测试缺口
- **当前写法**: Test A uses `monkeypatch` to patch `fund_agent.agent.runner._typed_required_output_items` to raise `ValueError`.
- **反例/失败场景**: The `_writer_input()` function calls both `build_chapter_writer_input()` (which has its own ValueError branches for invalid mode/citation_style/max_output_chars/prompt_payload_mode) and `_typed_required_output_items()`. If the fix is implemented correctly, any ValueError from either sub-call is caught. But Test A only exercises one specific injection point. A future regression that breaks the try/except location (e.g., someone moves the try/except to wrap only `_typed_required_output_items` instead of the whole `_writer_input()`) would not be caught if `build_chapter_writer_input()`'s ValueError branches remain uncovered.
- **为什么有问题**: The fix wraps the entire `_writer_input()` call, which is correct, but the single-injection-point test doesn't prove the try/except covers all ValueError sources within `_writer_input()`.
- **直接证据**: `_writer_input()` at runner.py:607-618 calls both `build_chapter_writer_input()` (chapter_writer.py:544-596, with ValueError at L577/579/581/583) and `_typed_required_output_items()` (runner.py:1102-1123, with ValueError via `_typed_chapter_contract()`). Two independent ValueError sources exist within the wrapped call.
- **影响**: 后续返工 — a narrow refactor could expose one ValueError path while the test continues to pass via the other injection point.
- **建议改法和验证点**: Not blocking. The fix wrapping the whole `_writer_input()` call is structurally correct, and a second injection point is desirable but not strictly necessary for this narrow gate. Record as residual for future pre-provider diagnostic coverage.
- **修复风险（低）**:
- **严重程度（低）**:

#### Finding 3 — accepted-candidate — 低 — `_chapter_title()` Remains Unprotected Before Try/Except

- **位置**: §5 Proposed Minimal Fix
- **问题类型**: 切片过粗
- **当前写法**: The plan wraps `_writer_input()` in try/except, but `title = _chapter_title(projection, chapter_id)` at runner.py:305 remains outside the protection boundary.
- **反例/失败场景**: If `_chapter_title()` were to raise for an unexpected chapter_id or malformed projection, the exception would still escape `_run_single_chapter()`. However, `_chapter_title()` is a simple dict-lookup function operating on inputs already validated upstream, making this path extremely unlikely in practice.
- **为什么有问题**: The plan claims to cover "pre-tool" failures but `_chapter_title()` is also pre-tool. In practice this is negligible because `_chapter_title()` does not have the same ValueError risk surface as `_writer_input()`.
- **直接证据**: runner.py:305 — `title = _chapter_title(projection, chapter_id)` precedes the proposed try/except boundary.
- **影响**: 风险后移 — a Chapter 3 title lookup failure would still escape. Probability is very low given the function's simplicity.
- **建议改法和验证点**: Accept as residual. If the controller wants full pre-tool coverage, a future gate could expand the try/except boundary to include `_chapter_title()`. Not worth complicating this narrow fix.
- **修复风险（低）**:
- **严重程度（低）**:

## 4. Verdict Table

| Criterion | Assessment | Evidence |
|---|---|---|
| Candidate code path supported by repo facts | **PASS** | `_run_single_chapter()` L305-313 in runner.py: `_writer_input()` called before `attempt_index` init; `build_chapter_writer_input()` has 4× ValueError branches (L577/579/581/583); `get_typed_chapter_contract()` raises ValueError at L322; `_required_output_evidence_plan()` raises ValueError at L922/951. |
| Red-test-first stop condition sufficient | **PASS** | Test A must reproduce escaped ValueError pre-fix; if not, stop and report `NEED_MORE_NO_LIVE_EVIDENCE`. This gate prevents speculative fix. |
| Minimal write set properly constrained | **PASS** | Source: `fund_agent/agent/runner.py` only (two localized changes). Tests: two new tests in two files. No other source/test/doc/config touched. |
| EID single-source/no-fallback preserved | **PASS** | §8 Non-goals explicitly preserves EID single-source policy, no Eastmoney/CDN/CNINFO/fallback re-entry. Fix is purely internal fail-closed conversion. |
| NOT_READY preserved | **PASS** | Plan explicitly states release/readiness remains `NOT_READY` and does not claim readiness improvement. |
| Annual-period LLM route avoided | **PASS** | §8 Non-goals: "Do not design annual-period LLM route or inject multi-year annual evidence into Route C." |
| Repair budget calibration avoided | **PASS** | §8 Non-goals: "Do not change repair budget." Repair policy untouched. |
| Provider default changes avoided | **PASS** | §5: "Do not change provider defaults, model, base URL, runtime budget, repair budget, source policy, fallback, annual-period LLM route or config." |
| Docling/source fallback avoided | **PASS** | §8 Non-goals: "Do not touch `FundDocumentRepository`, source helpers, PDF/cache/parser/Docling paths." |
| Live/provider commands avoided | **PASS** | §7 Validation Matrix: "No `fund-analysis analyze`...provider, LLM, network...command is authorized." All V1-V6 are no-live pytest/ruff/git commands. |
| Tests prove no-live pre-tool ValueError path | **PASS with minor gap** | Test A covers Agent runner pre-tool boundary with one injection point; Test B covers orchestrator projection with same. Both verify secret-free diagnostics, `max_output_chars=12000`, provider attempt count 0. See Finding 2 for single-injection-point residual. |
| Safe diagnostic projection proved | **PASS** | Test B asserts `provider_runtime_categories == ()`, `error_type == "ValueError"`, `provider_runtime_category is None`, `max_output_chars == 12000`, and no `Authorization`/`Bearer`/`sk-secret`/`prompt raw` in serialized payload. |

## 5. Required Amendments

**Amendment 1 (recommended, not blocking)**: Replace the "preferred minimal behavior" language in §5 with an exact code specification for the `_exception_task()` guard change. Current phrasing introduces unnecessary ambiguity. The exact change is:

> Change the guard at `runner.py:927-929` from:
> ```python
> if len(traces) == 1 and traces[0].request.tool_name == "fund.write_chapter"
> ```
> to:
> ```python
> if len(traces) == 0 or (len(traces) == 1 and traces[0].request.tool_name == "fund.write_chapter")
> ```

This amendment is optional — the plan's intent is clear — but it removes a decision point from the implementation worker and reduces risk of implementation drift.

## 6. Residuals

| Residual | Severity | Owner / tracking |
|---|---|---|
| `_exception_task()` modification spec ambiguity (Finding 1) | 低 — intent clear, minimal risk of wrong implementation | Implementation worker + controller review |
| Single injection point in Test A doesn't prove coverage of all `_writer_input()` ValueError branches (Finding 2) | 低 — fix structure is correct; second injection point is nice-to-have | Future pre-provider diagnostic coverage gate |
| `_chapter_title()` at runner.py:305 remains outside try/except boundary (Finding 3) | 低 — function is simple dict lookup, extremely unlikely to raise for validated inputs | Accept as is; expand boundary in future gate only if evidence warrants |
| Broader pre-run global ValueError paths before any target chapter task remain outside this narrow fix | Accepted residual per plan §9 | Separate no-live evidence/planning gate |
| Live `004393 / 2025` Route C full completion, LLM content quality, 401/403 classification remain unproven | Accepted residual per plan §9 | Separately authorized gates |
| Release/readiness remains `NOT_READY` | Accepted residual per plan §9 | Release/readiness gate only |

## 7. Final Verdict

**PASS**

The plan identifies a genuine, code-supported pre-tool ValueError boundary in `_run_single_chapter()` that existing tests do not cover. The proposed fix is minimal (two localized changes in one source file), correctly preserves fail-closed behavior, and does not alter any provider/source/fallback/config/route policy. The red-test-first stop condition is well-designed and prevents speculative implementation. The non-goal guardrails are comprehensive and correctly enumerate all forbidden paths. The proposed tests prove the pre-tool ValueError → `llm_exception`/`code_bug` → safe diagnostic projection chain with appropriate assertions.

One recommended amendment (see §5) would tighten the `_exception_task()` modification spec, but the plan is safe to hand to an implementation worker as-is.
