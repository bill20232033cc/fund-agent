# MVP provider runtime timeout hardening plan re-review — MiMo

日期：2026-05-31

Reviewer: AgentMiMo independent plan reviewer, not controller, not implementation worker.

Re-review target: `docs/reviews/mvp-provider-runtime-timeout-hardening-plan-20260531.md`（post-revision）

Previous review: `docs/reviews/mvp-provider-runtime-timeout-hardening-plan-review-mimo-20260531.md`

## re-review scope

Revised plan 已按 controller accepted findings 修订。逐项验证 5 个 fix 点，并对修订后 plan 施加 adversarial review lenses。

## fix verification

### Fix 1: MiMo B-1 — diagnostic type Service-layer only

**PASS.**

Plan lines 119-120 明确："只能定义在 Service 层：`fund_agent/services/chapter_orchestrator.py` 或 `fund_agent/services/llm_provider.py`。不得定义在 `fund_agent/fund/chapter_writer.py` 或 `fund_agent/fund/chapter_auditor.py`。"

Forbidden files (line 81-82) 已将 `chapter_writer.py` 和 `chapter_auditor.py` 列入显式禁止。

Slice C exact changes (line 275): "不修改 `write_chapter()`、`audit_chapter_llm()`、Fund request/response 或 Fund Protocol。"

Fund-layer boundary已恢复。

### Fix 2: MiMo B-2 / GLM F1 — no Fund Protocol extension

**PASS.**

Plan lines 121-122: "不得扩展 Fund-layer Protocol request/response：不修改 `ChapterLLMRequest`、`ChapterAuditLLMRequest`、`ChapterLLMResponse`、`ChapterAuditLLMResponse` 或 `ChapterLLMClient` / `ChapterAuditLLMClient` 签名来传递 diagnostics。"

Slice B lines 239-240: "`generate_chapter()` / `audit_chapter()` 继续使用现有 Fund Protocol 签名；不得新增 kwargs，不得修改 request/response dataclass。"

Lines 147-148: "Provider 层只填 `operation`、`provider_attempt_index`、`provider_max_attempts`、`provider_runtime_category`、HTTP/status/request/model/finish/elapsed/response length/error 安全字段；`chapter_id`、`fund_code`、`report_year`、`repair_attempt_index` 和 `chapter_failure_category` 在 provider 层必须为 `None`。"

Lines 122-123: "Provider 层可以在 `LLMProviderRuntimeError` 子类上携带 provider attempt diagnostics；orchestrator 捕获异常后把 diagnostics enrichment 到 chapter attempt context。"

Provider diagnostics 不穿越 Fund Protocol，由 orchestrator 在 exception catch 路径中 enrich。清晰。

### Fix 3: GLM F2 — audit repair_attempt_index handling

**PASS.**

Line 149: "Audit provider-level diagnostic 的 `repair_attempt_index` 在 provider 层必须为 `None`；orchestrator 聚合时填入当前 `ChapterAttemptRecord.attempt_index`。"

Field definition (line 131): `repair_attempt_index: int | None`，nullable 明确。

Provider 层和 orchestrator 层的填充规则已分开。

### Fix 4: GLM F4 — CLI must append first failed chapter id/status/stop_reason

**PASS.**

Lines 311-314: "`_llm_incomplete_message()` must append a safe first failed chapter summary by traversing `result.llm_orchestration_result.chapter_results` and selecting the first `ChapterRunResult` whose `status != "accepted"`: `first_failed_chapter_id=<chapter_id>`, `first_failed_status=<status>`, `first_failed_stop_reason=<stop_reason>`。"

从 "may append" 改为 "must append"。Line 318: "If there is no failed chapter result, output `first_failed_chapter=none` rather than traversing attempts." — edge case 覆盖。

Slice D completion signal (line 324): "CLI tests prove timeout failure stderr includes first failed chapter id/status/stop_reason and `llm_timeout` where applicable"。

### Fix 5: Non-blocking clarifications

**PASS.**

- Sleep injection (line 238): "`sleep: Callable[[float], None] = time.sleep`；测试注入 `lambda _: None`。" — 明确默认值，无 `None` 歧义。
- `_sanitize_text` (line 143): "必须通过 `_sanitize_text()` 或等价 helper 生成短安全摘要"。
- Shared client retry independence (line 150 + line 192): "writer/auditor 共享同一个 client 实例，但 retry 计数按每次 `_complete()` 调用独立"。
- `provider_runtime_category` vs `chapter_failure_category` split (lines 134-135, 158-179): 两层分类表已拆分，provider 层只产出 `provider_runtime_category`，orchestrator 映射 `chapter_failure_category`。

## adversarial lens results

### Architecture boundary review

**No findings.** Diagnostic type 定义在 Service 层，Fund-layer Protocol 未被修改。Provider 层只填 provider-safe 字段，orchestrator enrich chapter identity。分层清晰。

### Best-practice review

**No findings.** Sleep injection testable、`_sanitize_text` 复用、两层分类 taxonomy 都符合 project-local conventions。

### Optimal-solution review

**No findings.** Bounded retry + diagnostic enrichment 是 timeout hardening 最实际的路径。没有更简单的替代方案能同时满足 bounded loop 和 diagnostic 需求。

### Overengineering review

**No findings.** Plan 只新增两个 env config 字段、一个 diagnostic dataclass、retry loop 和 CLI classification summary。没有无需求支撑的 abstraction。

### Overcoupling review

**No findings.** Diagnostic type 定义在 Service 层，不穿透 Fund Protocol。Writer/auditor 共享 client 但 retry 独立。Orchestrator enrichment 是单向的（provider → orchestrator），无双向依赖。

## residual observations (non-blocking, not findings)

### O-1: `LLMProviderTimeoutError` 携带 diagnostics 的实现细节

Plan 要求 provider exception 携带 diagnostics (line 244: "最后一次抛 `LLMProviderTimeoutError`，异常对象携带 diagnostics")，但未指定具体方式。Python 中可在 `LLMProviderTimeoutError` 上新增 `diagnostics` 属性（如 `__init__` 加 `diagnostics` 参数，或 `self.diagnostics = [...]`）。这是实现细节，implementation worker 可自行决定。不构成 blocker。

### O-2: Diagnostic type 定义位置二选一

Plan (line 119) 允许定义在 `chapter_orchestrator.py` 或 `llm_provider.py`。两者都可行，但建议 implementation worker 优先选择 `llm_provider.py`（provider attempt diagnostic 的自然归属），然后由 orchestrator import。这不影响 plan 可实施性。

### O-3: 成功路径无 diagnostic

Plan 只求失败路径 diagnostic；成功路径不产出 `ChapterLLMRuntimeDiagnostic`。这意味着 `ChapterAttemptRecord.runtime_diagnostics` 在 accepted 章节上为空 tuple。这对当前 gate（诊断 timeout blocker）足够。后续 gate 若需成功 attempt 统计，可作为新 slice 扩展。

## conclusion

**PASS.** 所有 5 个 controller accepted findings 已正确修订到 plan 中。修订后 plan 无 remaining blocking findings。Adversarial review lenses 未发现新的 material issues。

Plan code-generation-ready，可交 implementation worker 执行。

## self-check

- reviewed target、scope、fix verification 均已写清。
- 无 blocking findings；residual observations 为非 blocking 实现细节。
- conclusion 为 `pass`。
- 未修改任何代码文件。
