# MVP provider runtime timeout hardening plan review — MiMo

日期：2026-05-31

Reviewer: AgentMiMo independent plan reviewer, not controller, not implementation worker.

Review target: `docs/reviews/mvp-provider-runtime-timeout-hardening-plan-20260531.md`

## conclusion

Plan is **code-generation-ready with 2 blocking and 3 non-blocking findings**. Core retry/backoff/bounded-loop design is correct. Blocking issues are: (1) `ChapterLLMRuntimeDiagnostic` placement in Fund-layer `chapter_writer.py` violates existing layering; (2) Slice B `_complete()` signature change lacks explicit contract for how `generate_chapter()` / `audit_chapter()` obtain identity fields. Both are fixable without redesign.

## review focus results

### 1. Code-generation-ready?

**YES, with 2 blocking fixes needed.** Slices A→D are properly sequenced (config → provider → orchestrator → CLI). Each slice has allowed files, exact field/env names, completion signals, and stop conditions. The implementation worker can execute without redesign.

### 2. Timeout retry bounded, no unbounded loops?

**YES.** The plan correctly separates two orthogonal dimensions:

- `timeout_max_attempts` (per-provider-request HTTP retry, default 2)
- `max_repair_attempts` (audit-driven regenerate, default 1)

Per-chapter HTTP upper bound `<= (max_repair_attempts + 1) * 2 * timeout_max_attempts = 8` is correct. The plan explicitly states timeout exhausted → `failed/llm_timeout` → no regenerate trigger. This is sound.

### 3. Typed env config minimal and compatible?

**YES.** Two new fields on `LLMProviderConfig` follow existing `_load_timeout_seconds()` / `_load_max_output_chars()` pattern exactly. Boundaries `1..3` and `0..30` are reasonable. Existing `timeout_seconds` semantics preserved.

### 4. Runtime diagnostics safe?

**YES, with one non-blocking concern.** The diagnostic field list is well-curated: counts, status code, request id, model, elapsed, attempt indexes, safe category. Forbidden list explicitly covers all leakage vectors. The `message` field must be "短安全摘要" — implementation must enforce max length.

### 5. Non-timeout categories not retried?

**YES.** 429 → `LLMProviderRateLimitError`, non-2xx → `LLMProviderRuntimeError`, malformed → `LLMProviderMalformedResponseError`, transport non-timeout → `LLMProviderNetworkError`. All fail immediately. Fail-closed preserved. No deterministic fallback.

### 6. Scope guard (golden/fixtures/score/quality/dayu/Agent)?

**YES.** Explicitly listed in non-goals and forbidden scope. Default deterministic `analyze`/`checklist` unchanged.

### 7. Scope too broad (diagnostic propagation)?

**Non-blocking.** Slice C diagnostic propagation into `ChapterAttemptRecord` is minimal — one new tuple field. CLI stderr in Slice D is additive, not restructured. Writer/auditor modules touched only for type definition (see blocking finding #1 below).

---

## blocking findings

### B-1: `ChapterLLMRuntimeDiagnostic` placement violates Fund-layer boundary

**Evidence:** Plan Slice C, lines 107-109: "若需要 writer/auditor result 直接携带，则定义在 `fund_agent/fund/chapter_writer.py`，`chapter_auditor.py` 复用该类型。"

**Problem:** `fund_agent/fund/chapter_writer.py` and `chapter_auditor.py` are Fund-layer primitives. Their docstrings explicitly state: "不读取年报仓库、PDF、cache、source helper、下载器、parser、Service、Host 或 dayu" and "不直接依赖任何真实 LLM provider SDK". The diagnostic type includes Service-layer concepts (`provider_attempt_index`, `provider_max_attempts`, `status_code`, `request_id`, `model_name`, `finish_reason`) that are provider-adapter concerns, not Fund primitive concerns. Placing it in `chapter_writer.py` imports provider transport semantics into the Fund layer.

**Fix:** Define `ChapterLLMRuntimeDiagnostic` in `fund_agent/services/chapter_orchestrator.py` (option 2 in the plan's own priority list). The diagnostic is a Service-layer aggregation concern. `ChapterAttemptRecord` already lives in `chapter_orchestrator.py` — adding `runtime_diagnostics: tuple[ChapterLLMRuntimeDiagnostic, ...]` there is natural. Writer/audit results do not need to carry diagnostics; the orchestrator already catches exceptions and can attach diagnostics at the `ChapterAttemptRecord` level. This eliminates the need to touch `chapter_writer.py` or `chapter_auditor.py` at all for Slice C.

**Impact:** Removes `fund_agent/fund/chapter_writer.py` and `fund_agent/fund/chapter_auditor.py` from Slice C allowed files. Simplifies implementation.

### B-2: `_complete()` identity parameter contract underspecified

**Evidence:** Plan Slice B, line 206: "`_complete()` 接收 operation/chapter identity，例如从 `generate_chapter()` / `audit_chapter()` 传入 `operation`、`chapter_id`、`fund_code`、`report_year`、`repair_attempt_index`。"

**Problem:** Currently `generate_chapter(request: ChapterLLMRequest)` and `audit_chapter(request: ChapterAuditLLMRequest)` only receive the existing request types. Neither `ChapterLLMRequest` nor `ChapterAuditLLMRequest` contains `chapter_id`, `fund_code`, `report_year`, or `repair_attempt_index`. The plan says "例如从 ... 传入" but does not specify:

1. Are these added as new fields on `ChapterLLMRequest` / `ChapterAuditLLMRequest`? That touches Fund-layer Protocol types.
2. Are they passed as separate parameters to `generate_chapter()` / `audit_chapter()`? That changes the `ChapterLLMClient` / `ChapterAuditLLMClient` Protocol signatures.
3. Are they passed only to `_complete()` as private implementation detail? Then `generate_chapter()` / `audit_chapter()` must obtain them from somewhere.

The implementation worker cannot proceed without knowing which approach. If option 1 or 2, the Fund-layer Protocol changes must be explicitly listed in Slice B allowed files.

**Fix:** Specify one of:
- **Option A (recommended):** Pass identity as keyword-only parameters to `_complete()` only. `generate_chapter()` / `audit_chapter()` accept optional `operation`, `chapter_id`, `fund_code`, `report_year`, `repair_attempt_index` kwargs (defaulting to sentinel values for tests). The Protocol types `ChapterLLMClient` / `ChapterAuditLLMClient` get `**kwargs` or explicit optional params. Document that the orchestrator is responsible for passing these from `ChapterOrchestrationInput`.
- **Option B:** Add identity fields to `ChapterLLMRequest` / `ChapterAuditLLMRequest`. This requires listing those Fund-layer files in Slice B allowed files.

Either way, add the chosen Fund-layer request/Protocol files to Slice B allowed files if they need modification.

---

## non-blocking findings

### NB-1: Backoff sleep injection should default to `time.sleep`, not `None`

**Evidence:** Plan Slice B, line 205: "增加可测试 sleep 注入，例如 `sleep: Callable[[float], None] | None = None`，默认使用 `time.sleep`。"

The `| None` default + "默认使用 `time.sleep`" is slightly ambiguous. If `sleep=None`, does the constructor use `time.sleep`? Or does `None` mean "no sleep" (which would break the backoff contract)?

**Recommendation:** Make the default explicit: `sleep: Callable[[float], None] = time.sleep`. Tests inject `lambda _: None`. This removes the ambiguity.

### NB-2: `_safe_exception_message` already redacts `prompt` — diagnostic `message` field contract should reference it

**Evidence:** `chapter_orchestrator.py:1101` already redacts `Authorization`, `Bearer`, `FUND_AGENT_LLM_API_KEY`, `api_key`, `sk-`, `prompt` in `_sanitize_text()`. The plan's diagnostic `message` field (line 128) says "必须为短安全摘要，不能包含 prompt/draft/provider body/env value/header" but does not reference the existing `_sanitize_text()` helper.

**Recommendation:** Add a note that diagnostic `message` should be produced via `_sanitize_text()` or equivalent, to reuse existing redaction rather than inventing a parallel mechanism.

### NB-3: Per-chapter HTTP bound formula comment could clarify writer+auditor share same client

**Evidence:** Plan line 159: "每章理论 HTTP 上限：`<= (max_repair_attempts + 1) * 2 * timeout_max_attempts`". The `* 2` accounts for writer + auditor per attempt. Since `build_chapter_llm_clients()` returns `ChapterOrchestratorLLMClients(writer=client, auditor=client)` with the **same** client instance, the retry state (attempt counters) is shared. This is fine because each `_complete()` call is independent, but the formula's `* 2` could be misread as "two separate retry budgets."

**Recommendation:** Add a one-line note: "writer 和 auditor 共享同一 `OpenAICompatibleChapterLLMClient` 实例，但每次 `_complete()` 调用的 retry 计数独立。"

---

## scope guard verification

| Check | Result |
|---|---|
| Default deterministic `analyze`/`checklist` unchanged | PASS — plan explicitly preserves |
| Golden/fixtures/score/quality gate unchanged | PASS — explicitly forbidden |
| Host/Agent/dayu untouched | PASS — explicitly forbidden |
| `docs/implementation-control.md` / `docs/current-startup-packet.md` / `docs/design.md` untouched | PASS — explicitly forbidden |
| `AGENTS.md` untouched | PASS — explicitly forbidden |
| No deterministic fallback introduced | PASS — explicitly stated in non-goals |
| No non-timeout retry | PASS — taxonomy table and Slice B contract |
| Secret hygiene plan present | PASS — lines 366-378 |

## self-check

- 未修改代码文件。
- 未记录 API key、Authorization header、完整 provider response 或完整 writer draft。
- 未修改 golden / fixtures / score / quality gate。
- 未修改 PR 状态。
