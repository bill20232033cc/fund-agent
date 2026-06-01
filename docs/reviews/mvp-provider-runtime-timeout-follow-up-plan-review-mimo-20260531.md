# MVP provider runtime timeout follow-up plan review - MiMo

日期：2026-05-31

Reviewer：Gateflow plan reviewer（MiMo 角色），不是 implementation worker。

Reviewed target：`docs/reviews/mvp-provider-runtime-timeout-follow-up-plan-20260531.md`

Allowed edit scope：仅本 review artifact。未改代码，未运行真实 provider，未 push / PR / merge / release。

## Conclusion

**FAIL - blocking finding present.**

计划总体方向正确：它聚焦 authoritative CLI blocker chapter 1 `llm_timeout`，不回到 provider config/auth，不扩大 retry 到非 timeout，不引入并发或 fallback，也明确把 C2 作为 timeout-free 后的次级诊断。但当前 handoff 还不能交给 implementation worker，因为 runtime diagnostic serializer 的输出字段允许 `message`，而现有 Service 层 runtime diagnostic 的 `message` 并不总是 provider-safe scalar；它可能来自 writer/auditor issue message 或 LLM audit line message。若 implementation worker 按计划直接序列化，会违反本 gate “不记录完整 prompt/draft/provider response/raw audit response”和“只记录安全标量”的证据边界。

修正后建议 re-review。

## Sources Read

- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/reviews/mvp-programmatic-audit-l1-calibration-controller-judgment-20260531.md`
- `docs/reviews/mvp-provider-runtime-timeout-follow-up-plan-20260531.md`
- 必要代码事实：
  - `fund_agent/services/chapter_orchestrator.py`
  - `fund_agent/services/llm_provider.py`
  - `fund_agent/config/llm.py`
  - `fund_agent/ui/cli.py`
  - `tests/services/test_chapter_orchestrator.py`
  - `tests/services/test_llm_provider.py`
  - `tests/config/test_llm_config.py`
  - `tests/ui/test_cli.py`

## Assumptions Tested

- 当前主 blocker 是否仍是 chapter 1 `llm_timeout`，不是 provider config/auth。
- 计划是否能安全区分 writer/auditor、chapter repair attempt、provider attempt budget 和 elapsed budget。
- retry 是否保持 timeout-only、有界、顺序执行。
- 诊断证据是否不泄露 prompt、draft、provider body、raw audit response、key/header。
- 是否避免放松 writer/auditor/evidence/C2/L1/candidate facet/ITEM_RULE/quality/golden/default deterministic。

## Findings

### MIMO-P1-未修复-高-runtime serializer 计划允许输出非安全 message 文本

- **位置**: Plan §5.1 “Runtime diagnostic serialization”；Plan §4 “Root Cause Evidence To Gather”；Plan §9 “Smoke Evidence Requirements”
- **问题类型**: 契约缺失 / 测试缺口 / 证据泄漏风险
- **当前写法**: 新 serializer 的 `chapter_runtime_matrix` 允许输出每条 runtime diagnostic 的 `message` 字段，同时要求“只记录安全标量”。§4 还把“HTTP/provider scalar context”限定为 status code、safe request id、finish reason、response char count 等安全标量。
- **反例/失败场景**: `serialize_chapter_runtime_diagnostics()` 若直接遍历 `ChapterRunResult.runtime_diagnostics` 和 `ChapterAttemptRecord.runtime_diagnostics` 并输出 `message`，会把 writer/auditor diagnostic message 一并写入 report JSON。现有 `_writer_runtime_diagnostic()` 使用 `"; ".join(_writer_issue_messages(writer_result))`，`_audit_runtime_diagnostic()` 使用 `"; ".join(_audit_issue_messages(audit_result))`。writer issue message 可包含 required output item、unknown anchor id、missing reason 等章节 contract 文本；auditor issue message 可来自 LLM audit line protocol 的自由文本 message，也可能包含模型摘录或对草稿内容的转述。它们不是 provider attempt budget / elapsed / status code 这类 runtime 标量。
- **为什么有问题**: 本 gate 的用户硬约束和 plan 自身都禁止记录完整 prompt、完整 draft、完整 provider response、raw audit response，并要求 smoke evidence 只保存脱敏章节矩阵和失败定位。`message` 字段没有被 plan 限定为 provider-local safe message；将 writer/auditor issue message 序列化会把证据边界从“runtime diagnostic”扩大到“模型/审计文本摘要”，implementation worker 容易按 plan 生成泄漏或过宽 evidence。
- **直接证据**:
  - Plan §5.1 要求 serializer 输出 `message`。
  - `fund_agent/services/chapter_orchestrator.py` 中 `ChapterLLMRuntimeDiagnostic.message` 的 docstring 是“已脱敏、限长的安全摘要”，但 `_writer_runtime_diagnostic()` 以 writer issue messages 构造 message，`_audit_runtime_diagnostic()` 以 audit issue messages 构造 message。
  - `_audit_issue_messages()` 返回 `_all_audit_issues(audit_result)` 的 `issue.message`；LLM audit issues 由 line protocol message 构造，属于模型输出文本，不是 provider scalar。
  - `fund_agent/services/llm_provider.py` 的 provider-local message 相对安全，使用固定 timeout/network/malformed 文案或 status/request-id 摘要；风险主要来自 Service 层 writer/auditor diagnostic 复用同一个 `message` 字段。
- **影响**: 实施 Agent 可能直接输出非标量文本到 reports，导致 secret/prompt/draft/raw audit response 边界不可审计；code review 也难以判断哪些 `message` 来源安全。即使没有实际 secret，也会违背当前 gate 的证据最小化目标，并可能迫使后续 gate 清理 artifacts。
- **建议改法和验证点**:
  - Plan §5.1 明确禁止 runtime serializer 输出通用 `message` 字段；默认只输出枚举/计数/数值标量：operation、repair_attempt_index、provider_attempt_index、provider_max_attempts、provider_runtime_category、chapter_failure_category、elapsed_ms、status_code、request_id、finish_reason、response_chars、error_type。
  - 如果确实需要 message，只允许输出 provider-local allowlist message，并且必须满足 `provider_runtime_category is not None` 且 message 属于固定枚举文案或 `_safe_http_error_message()` 生成的 status/request-id 摘要；writer/auditor issue messages 不得进入 runtime serializer。
  - CLI summary 也不得输出 message，只输出 plan 已列出的 operation / attempts / runtime category / elapsed max。
  - 测试必须新增断言：writer issue message、auditor LLM issue message、required output item、unknown anchor id、raw audit line、prompt/draft/body/key/header 均不出现在 serializer payload 和 CLI stderr。
  - Evidence secret scan pattern 应覆盖 `raw_response`、`draft_markdown`、`system_prompt`、`user_prompt`、`Authorization`、`Bearer`、`FUND_AGENT_LLM_API_KEY`，并增加对测试注入的 canary text（例如 fake prompt / fake draft / fake audit raw message）的负断言。
- **修复风险（低/中/高）**: 低。只需收紧计划和后续实现字段 allowlist，不改变 runtime 行为或 retry 语义。
- **严重程度（低/中/高/严重）**: 高

## Positive Checks

- 计划聚焦 current authoritative CLI blocker：chapter `1` / `llm_timeout`，并明确 C2 只作为 timeout-free 后的 secondary diagnostic。
- 计划没有把问题回滚到 provider config/auth；只在 env load 失败时要求同源证据说明 preflight issue。
- retry 决策保持 timeout-only、有界 `1..3`，不重试 rate limit / malformed / network / non-2xx，不引入无限重试。
- 计划拒绝并发章节生成和 provider fallback，避免放大 provider pressure 或掩盖失败来源。
- 计划明确不改 golden / fixtures / score / quality gate / final judgment / Host / Agent / dayu / deterministic default。
- 计划明确不修 C2、不放松 C2/L1/candidate facet/ITEM_RULE/evidence 边界。

## Open Questions

- 无 blocking open question；blocking finding 可通过收紧 plan 字段 allowlist 和测试断言解决。

## Residual Risks

- 即使 runtime diagnostic 变安全，真实 provider 仍可能在 bounded smoke 下继续 timeout；这是 Gate B acceptance 风险，不是本 plan review blocker。controller judgment 需要按计划输出唯一主 blocker和最小下一入口。
- 若 timeout-free rerun 到达 chapter 3 C2，后续应按 `MVP programmatic audit C2 calibration gate` 单独处理，不能把 C2 修复混入 timeout gate。

## Reviewer Self-Check

- 当前角色：Gateflow plan reviewer（MiMo），不是 implementation worker。
- 本 review 只新增指定 review artifact；未修改 plan 或代码。
- finding 绑定到 plan §5.1 与现有代码事实，不是风格意见。
- conclusion 使用 `FAIL`，因为存在 implementation 前必须修正的 evidence safety contract 缺口。
