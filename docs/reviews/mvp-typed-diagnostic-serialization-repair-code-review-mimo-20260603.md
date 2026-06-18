# MVP typed diagnostic serialization repair code review — MiMo

## Gate

`MVP typed diagnostic serialization repair implementation gate`

## Role

Independent adversarial code reviewer. No source/test/config/runtime/provider modification.

## Scope Reviewed

- `fund_agent/services/chapter_orchestrator.py`
- `fund_agent/services/llm_run_artifacts.py`
- `fund_agent/config/paths.py`
- `fund_agent/config/README.md`
- `tests/services/test_chapter_orchestrator.py`
- `tests/services/test_llm_run_artifacts.py`
- `docs/reviews/mvp-typed-diagnostic-serialization-repair-implementation-evidence-20260603.md`

## Inputs

- `docs/reviews/mvp-llm-acceptance-volatility-diagnostic-evidence-reconciliation-design-plan-controller-judgment-20260603.md`
- `docs/reviews/mvp-typed-diagnostic-serialization-repair-implementation-evidence-20260603.md`
- `git diff` (uncommitted)

---

## Findings

### F-1 [minor] `_safe_status_code` duplicated across two modules

`chapter_orchestrator.py` 和 `llm_run_artifacts.py` 各自定义了一份完全相同的 `_safe_status_code` 函数。这不是 bug，但如果未来安全范围规则变更（例如排除 1xx informational），需要同步修改两处。

**Why it's not blocking:** 两份副本行为一致，且各模块保持自包含。这是代码卫生问题，不是正确性问题。

### F-2 [advisory] first-failed summary timeout fields 在 missing terminal diagnostic 时变为空值

旧代码直接用全量 diagnostics 填充 `timeout_seconds`、`timeout_budget_kind` 等字段；新代码在 `_representative_runtime_diagnostics` 返回空元组时，这些字段变为 `None`/`0`。

**分析:** 这是正确的语义变更。旧代码在 `llm_timeout` 但没有匹配 timeout runtime row 时，可能从非 timeout 的 diagnostic（例如 prompt_contract row）中取到误导性的 timeout 值。新代码通过 `missing_terminal_runtime_diagnostic` 状态明确标识这种情况，不伪造 timeout 标量。

**对旧 consumer 的影响:** 如果有旧 consumer 依赖这些字段总是非空，它们在 missing terminal case 下会收到 `None`。但这是预期行为——缺失就是缺失。`test_timeout_terminal_without_matching_runtime_row_marks_missing` 显式覆盖了这个场景。

### F-3 [advisory] `attempt_runtime_diagnostic_consistency_payload` 使用 chapter-level stop_reason 套到每个 attempt

`attempt_runtime_diagnostic_consistency_payload(result, attempt)` 中，`_terminal_runtime_diagnostic(result, attempt.runtime_diagnostics)` 用 chapter 的 `result.stop_reason` 来搜索 attempt 级 diagnostics。

**分析:** 这是正确设计。chapter 的 terminal status 是事实真源；attempt 级 payload 的 `terminal_runtime_diagnostic_present: False` 表示"这个 attempt 不持有 terminal diagnostic"，而不是"chapter 没有 terminal failure"。当 terminal exception 发生在没有 attempt record 的阶段时，chapter-level diagnostics 持有 terminal row，attempt rows 正确报告缺失。这不是误导——它是分层事实的正确表达。

### F-4 [advisory] `terminal_issue_class` 从 issue text 硬编码解析异常类名

`_terminal_issue_class` 在 fallback 路径中用 `"LLMProviderTimeoutError" in issue_text` 等子串匹配来推断异常类名。

**分析:** 这是安全的。硬编码的类名是已知的 provider 异常类型，不包含用户数据。匹配方向是"从安全 issue 文本推断已知类名"，不是从类名生成 issue 文本。`_first_safe_issue_prefix` 进一步用 allowlist 过滤。如果未来异常类名变更，这段代码会退化为返回 `_first_safe_issue_prefix` 结果，不会泄露信息。

### F-5 [positive] `_exception_result` attached_to_attempt 逻辑正确修复了诊断遮蔽 bug

旧逻辑 `runtime_diagnostics=runtime_diagnostics if not attempts else ()` 在 attempts 非空时无条件丢弃 chapter-level terminal diagnostics。新逻辑 `runtime_diagnostics=() if attached_to_attempt else runtime_diagnostics` 只在成功附加到 attempt 时才清空 chapter-level，否则保留。

**关键场景验证:**
- attempts 为空 → diagnostics 保留 chapter-level ✓
- 最后 attempt 无 diagnostics → 附加到 attempt，chapter-level 清空 ✓
- 最后 attempt 已有 diagnostics（prior audit row）→ 不附加，保留 chapter-level ✓（这就是修复的核心场景）

### F-6 [positive] test fixture fake client 优先级调整合理

`_FakeChapterLLMClient` 和 `_FakeAuditLLMClient` 的 `texts`/`raw_responses` 优先级从 `exception > raises > texts` 改为 `raises > texts > exception`。这允许测试通过 `texts` 参数注入成功响应后再抛异常，精确控制第 N 次调用的行为。全量 pytest 1292 passed 验证了无回归。

### F-7 [positive] config path import 依赖方向正确

`llm_run_artifacts.py` 从 `fund_agent.config.paths` 导入 `DEFAULT_LLM_RUN_ARTIFACT_ROOT`，方向是 Service → Config，与现有 `paths.py` 的职责（"默认路径常量的唯一入口"）一致。无循环依赖。`paths.py` 不导入任何 Service 或 Fund 模块。

---

## Checklist Against Design/Plan Gate Requirements

| Requirement | Status |
|---|---|
| Root cause framed as serializer/lineage bug, not provider-budget | ✓ |
| Scalar consistency fields added (`diagnostic_consistency_status`, etc.) | ✓ |
| Chapter-level and `attempts[]` runtime diagnostic lineage covered | ✓ |
| Prompt-contract diagnostics kept separate from provider runtime | ✓ |
| CLI first-failed regression coverage if representative selection changes | ✓ (3 new tests) |
| Full `uv run pytest` in evidence | ✓ (1292 passed) |
| `status_code` scoped to 100..599 | ✓ |
| `request_id` remains opaque | ✓ |
| `prompt_cost_diagnostic` not serialized by `llm_run_artifacts` | ✓ |
| No live provider called | ✓ |
| No timeout/auditor/prompt/final-assembly/score-loop/provider-config changes | ✓ |

---

## Verdict

**PASS. No blocking findings.**

Seven findings: 0 blocking, 0 major, 1 minor (code duplication), 3 advisory (all analyzed as correct design), 3 positive confirmations. The implementation correctly repairs the diagnostic shadowing bug, adds terminal lineage fields without breaking existing schema consumers, and maintains fail-closed behavior.

---

## Secret Safety

This review contains no API key, Authorization header, Bearer token, cookie, password, provider base URL, model value, raw prompt body, raw provider response, raw audit response, writer draft body, repair draft body, markdown report body, raw PDF text, or raw parsed annual-report text.
