# MVP provider runtime timeout hardening plan re-review (GLM)

日期：2026-05-31

角色：AgentGLM independent plan re-reviewer，非 controller，非 implementation worker。

Re-reviewed target：`docs/reviews/mvp-provider-runtime-timeout-hardening-plan-20260531.md`（修订版）

Prior review：`docs/reviews/mvp-provider-runtime-timeout-hardening-plan-review-glm-20260531.md`

Re-review scope：验证 controller accepted findings 的修订结果，检查是否残留 blocking findings。

## fix verification

### MiMo B-1：diagnostic type Service-layer only — VERIFIED ✅

Plan 修订后：
- Line 116-121：明确 "只能定义在 Service 层：`fund_agent/services/chapter_orchestrator.py` 或 `fund_agent/services/llm_provider.py`。不得定义在 `fund_agent/fund/chapter_writer.py` 或 `fund_agent/fund/chapter_auditor.py`。"
- Line 81：显式禁止修改 `fund_agent/fund/chapter_writer.py` 和 `fund_agent/fund/chapter_auditor.py`。
- Allowed files（lines 60-72）：已从 allowed files 中移除 writer/auditor。

### MiMo B-2 / GLM F1：不扩展 Fund Protocol — VERIFIED ✅

Plan 修订后：
- Line 121：显式声明 "不得扩展 Fund-layer Protocol request/response：不修改 `ChapterLLMRequest`、`ChapterAuditLLMRequest`、`ChapterLLMResponse`、`ChapterAuditLLMResponse` 或 `ChapterLLMClient` / `ChapterAuditLLMClient` 签名来传递 diagnostics。"
- Line 122：失败路径 — "Provider 层可以在 `LLMProviderRuntimeError` 子类上携带 provider attempt diagnostics；orchestrator 捕获异常后把 diagnostics enrichment 到 chapter attempt context。"
- Line 123：成功/非 runtime 路径 — "orchestrator 从已有安全 result 字段、`stop_reason`、`attempt_index` 和 repair decision 构造 chapter-level diagnostics；不要求 provider success diagnostics 穿越 Fund Protocol。"
- Line 239：`_complete()` 只接收 `operation="writer" | "auditor"`，不接收 chapter identity。
- Line 240：`generate_chapter()` / `audit_chapter()` 继续使用现有 Fund Protocol 签名，不得新增 kwargs。
- Line 245：成功响应仍返回现有 `LLMProviderResponse`，success diagnostics 不穿越 Fund Protocol。
- Line 274-275：diagnostics 只加在 `ChapterAttemptRecord`，不修改 `write_chapter()` / `audit_chapter_llm()` 或 Fund request/response。
- Line 291：Tests prove "existing Fund fake writer/auditor tests with old response constructors still work"。

Propagation mechanism 已明确：failure 通过 exception 对象 → orchestrator 提取并 enrich；success 不穿越 Protocol，orchestrator 从现有 result 字段构造。

### GLM F2：audit repair_attempt_index 显式处理 — VERIFIED ✅

Plan 修订后：
- Line 131：`repair_attempt_index: int | None` — nullable。
- Line 147：provider 层所有 identity 字段（`chapter_id`、`fund_code`、`report_year`、`repair_attempt_index`、`chapter_failure_category`）必须为 `None`。
- Line 149：显式说明 "audit provider-level diagnostic 的 `repair_attempt_index` 在 provider 层必须为 `None`；orchestrator 聚合时填入当前 `ChapterAttemptRecord.attempt_index`。"
- Line 348：Slice B completion signal 要求 "diagnostics 中 chapter identity 和 repair attempt 均为 `None`"。

### GLM F4：CLI must append safe first failed chapter — VERIFIED ✅

Plan 修订后：
- Line 311：从 "may append" 改为 "must append a safe first failed chapter summary by traversing `result.llm_orchestration_result.chapter_results`"。
- Lines 312-314：显式输出格式 `first_failed_chapter_id=<chapter_id>`, `first_failed_status=<status>`, `first_failed_stop_reason=<stop_reason>`。
- Line 318：edge case 处理 — "If there is no failed chapter result, output `first_failed_chapter=none`"。
- Line 316：provider attempt counts 默认留在 diagnostic JSON，不暴露到 CLI stderr。
- Line 324：completion signal 要求 stderr 含 first failed chapter id/status/stop_reason。
- Line 367：test assertions 显式要求 `first_failed_chapter_id`、`first_failed_status`、`first_failed_stop_reason=llm_timeout`。
- Line 389：validation matrix 新增 "CLI failure summary" 行。

### Non-blocking clarifications — VERIFIED ✅

1. **Sleep injection**：Line 238 — "`sleep: Callable[[float], None] = time.sleep`；测试注入 `lambda _: None`"。显式默认值和注入方式。

2. **_sanitize_text / equivalent**：Line 143 — "必须通过 `_sanitize_text()` 或等价 helper"；Line 248 — "所有 diagnostic `message` 必须使用 `_sanitize_text()` 或等价 helper"；Line 414 — "Diagnostic `message` values must use `_sanitize_text()` or equivalent redaction/length cap"。三处覆盖。

3. **Shared client but per _complete retry independent**：Line 150 — "Writer/auditor 共享同一个 `OpenAICompatibleChapterLLMClient` 实例，但 retry 计数按每次 `_complete()` 调用独立"；Line 192 — "即使 writer/auditor 共享同一 client 实例，每次 `_complete()` 的 retry 计数仍独立"。bounded formula 的 `* 2` 解释清晰。

4. **provider_runtime_category vs chapter_failure_category split**：Lines 133-135 — 两个独立字段；Lines 156-179 — 两个独立 taxonomy 表，provider 层只产出 `provider_runtime_category`，orchestrator 映射为 `chapter_failure_category`。解决了 GLM F3 layering concern。

## findings

无 blocking findings。

无新增 non-blocking findings。

修订版 plan 完整解决了 prior review 的 4 个 findings（F1-F4）和 MiMo 的 B-1/B-2 findings，以及 5 项 non-blocking clarifications。每项修复有具体 plan 文本、allowed files 变更和 test assertion 支撑。

## re-review lenses applied

- **Architecture boundary**：diagnostic type 限定 Service 层，Fund Protocol 不变，provider 只通过 exception 携带 diagnostics，orchestrator enrich。层次清晰。✅
- **Overcoupling**：provider 和 domain 分类拆为 `provider_runtime_category` 和 `chapter_failure_category` 两个独立字段，不再共享 enum。✅
- **Overengineering**：success diagnostics 不穿越 Protocol，orchestrator 从已有字段构造。最小改动。✅
- **Code-generation-readiness**：每个 Slice 有 allowed files、exact changes、completion signal、stop condition。CLI 遍历路径已指定。Sleep 注入和 _sanitize_text 使用已明确。✅
- **Bounded retry**：公式不变，默认每章最多 8 次 HTTP attempt，timeout retry 和 repair loop 独立。✅

## residual risks

与 prior review 一致，plan 已在 residual risks section 覆盖：
1. Provider 真实延迟可能持续超过 budget。
2. 成功 retry 后仍可能遇到 prompt_contract / audit_parse。
3. 429 retry 不在本 gate。

无新增 residual risks。

## conclusion

**PASS**

修订版 plan 完整解决了全部 prior findings。Diagnostic propagation mechanism 已明确选择不修改 Fund Protocol 的路径（exception-carried failure diagnostics + orchestrator-constructed success/classification diagnostics）。Bounded retry 有界、typed env 最小兼容、secret hygiene 充分、CLI 遍历路径 code-generation-ready。Plan 可以安全交给 implementation worker。

## reviewer self-check

- reviewed target、scope、fix verification 和 re-review lenses：已写清。✅
- findings 为空，无 style/nit/speculation。✅
- residual risks 与 findings 分开。✅
- conclusion 只能是 pass / pass-with-risks / fail：**pass**。✅
- 未修改 plan、未实施 fix、未 commit/push/PR。✅
