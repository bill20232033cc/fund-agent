# MVP provider runtime timeout follow-up plan review - GLM

生成时间：20260531-075912

Reviewer：Gateflow plan reviewer（GLM 角色），不是 implementation worker。

Reviewed target：`docs/reviews/mvp-provider-runtime-timeout-follow-up-plan-20260531.md`

Allowed edit scope：仅本 review artifact。

## Review Scope

本次审查只读：

- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/reviews/mvp-programmatic-audit-l1-calibration-controller-judgment-20260531.md`
- `docs/reviews/mvp-provider-runtime-timeout-follow-up-plan-20260531.md`
- 必要代码事实：`fund_agent/services/chapter_orchestrator.py`、`fund_agent/services/llm_provider.py`、`fund_agent/config/llm.py`、`fund_agent/ui/cli.py`、相关测试入口

未运行真实 provider，未改代码，未 push / PR / merge / release。

## Assumptions Tested

- 当前 authoritative CLI blocker 是 chapter `1` / `llm_timeout`，不是 provider config/auth。
- 计划必须 code-generation-ready，并能让 implementation worker 在不重新设计的情况下实现安全 timeout 诊断。
- 新 serializer / CLI summary 只能输出安全标量，不能泄漏 API key、Authorization header、Bearer、完整 prompt、完整 draft、完整 provider response 或 raw audit response。
- retry 语义必须保持 timeout-only、有界、无并发、无 provider fallback。
- C2 只能作为 timeout 稳定后的 secondary diagnostic，不得在本 gate 混修。
- 默认 deterministic analyze/checklist、golden、fixtures、score、quality gate、Host/Agent/dayu 不能受影响。

## Findings

### 001-未修复-[高]-runtime serializer 计划包含 `message` 字段，可能把 LLM audit/provider 派生文本写入 evidence

- **位置**: plan §5.1 Runtime diagnostic serialization，行 69-75；§9 Smoke Evidence Requirements，行 262-266
- **问题类型**: 契约缺失 / secret 与 raw-output 泄漏风险 / 测试缺口
- **当前写法**: 新 serializer 的 per runtime diagnostic 字段包括 `message`；同时 plan 禁止记录 full provider response、full prompt、full draft、raw audit response。
- **反例/失败场景**: implementation worker 按字段清单直接序列化 `ChapterLLMRuntimeDiagnostic.message`。当前 Service 的 `_audit_runtime_diagnostic()` 会把 `_audit_issue_messages(audit_result)` 汇总进 `message`，其中 LLM audit issue 来自 provider 返回的审计行文本；programmatic C2 / writer issue message 也可能包含 facet、phrase、item title 等 draft-derived 片段。这样 service-level diagnostic JSON 或 CLI summary 很容易存入 raw audit 派生文本、章节输出片段或不必要的业务文本，虽然没有存完整响应。
- **为什么有问题**: 用户和 plan 明确要求“不记录完整 prompt、完整 draft、完整 provider response、raw audit response”。对 timeout gate 来说，精确分类只需要 operation、repair attempt、provider attempt、runtime category、elapsed、status/request id 等安全标量；`message` 对判断 timeout budget exhaustion 不是必要字段，反而扩大泄漏面。
- **直接证据**:
  - plan 行 73 把 `message` 列入 serializer 输出字段。
  - `fund_agent/services/chapter_orchestrator.py` 中 `ChapterLLMRuntimeDiagnostic.message` 是通用字段；`_audit_runtime_diagnostic()` 使用 `"; ".join(_audit_issue_messages(audit_result))`，而 `_audit_issue_messages()` 返回 audit issue `message`。
  - `fund_agent/fund/chapter_auditor.py` 的 `_llm_issue()` 把 LLM 行协议 `message` 存入 issue；programmatic C2 issue 也会把 facet / phrase / item rule 等文本写入 message。
  - plan 行 262-266 禁止 evidence 记录 raw audit response / full draft / provider response，但没有要求 serializer 排除或强裁剪 `message`。
- **影响**: 实施 Agent 可能生成“功能正确但证据不合规”的 serializer；真实 provider diagnostic artifact 可能泄漏 raw audit-derived 内容，导致 gate 必须返工，且 secret scan 仅搜 key/header/prompt/body pattern 不一定能发现。
- **建议改法和验证点**:
  - 修改 plan：runtime serializer 默认不要输出 `message`。若必须输出，只允许 provider-local timeout/http/network 的固定白名单摘要，例如 `LLM provider request timed out`、`status_code/request_id`，且必须排除 writer/auditor/programmatic issue messages。
  - CLI timeout summary 不应包含 `message`。
  - service diagnostic JSON 测试应显式构造含有 `raw audit leaked text`、draft-like marker、facet 文本、Authorization/Bearer/key/prompt/body 的 diagnostic/message，并断言 serializer 输出不含这些字符串。
  - evidence script secret scan 之外，应增加 content-level negative assertions：不含 `system_prompt`、`user_prompt`、`draft_markdown`、`raw_response`、`raw audit` 以及测试注入的 sentinel 文本。
- **修复风险（低/中/高）**: 低。删除 serializer 字段或白名单固定 provider message 不影响 timeout 分类所需字段。
- **严重程度（低/中/高/严重）**: 高

## Open Questions

- 如果 controller 需要记录“configured runtime budget”，plan 目前把它放在 evidence requirement 中，但没有明确是否由 serializer 输出还是由 controller artifact 手工记录 env knob 数值。建议在实现 handoff 中固定为 controller evidence 记录高层 env knob，不让 serializer读取或暴露 provider config 对象。
- `request_id` 是否可能包含 provider 侧租户或部署信息需要 code review 复核；当前 plan 将其视为 safe scalar，与现有 provider helper一致，可接受，但真实 provider evidence 仍应只记录短字段、不记录响应 headers 全量。

## Residual Risks

- 即使本 plan 修正 `message` 泄漏风险，当前 gate 仍主要是 observability / bounded-smoke gate，不保证真实 provider 一定通过 0-7 章。若 bounded smoke 越过 timeout 后到达 chapter 3 C2，应按 plan 停止并进入 `MVP programmatic audit C2 calibration gate`。
- 真实 provider runtime latency 可能具有波动性；controller judgment 必须以 authoritative CLI rerun 为主，同时把 service diagnostic 作为补充，不应用一次 timeout-free service run 覆盖 CLI blocker。

## Lens Review Summary

- **Architecture boundary review**: PASS with finding above. Serializer 位于 Service 层，CLI 只展示 Service 结果，未引入 Host/Agent/dayu，符合当前过渡路径。
- **Best-practice review**: FAIL until finding fixed. 诊断 schema 应默认最小化输出，避免把通用 message 作为证据字段。
- **Optimal-solution review**: PASS with finding above. 增加安全 runtime serializer 和 CLI scalar summary 是比改 retry 或放宽 prompt contract 更小的路径。
- **Overengineering review**: PASS. 未引入新 provider SDK、多模型、并发、fallback 或新配置。
- **Overcoupling review**: PASS. 计划主要新增 serialization/summary helper，不要求改 provider retry 状态机；C2 明确后置。

## Conclusion

**FAIL**

该 plan 方向正确，范围基本受控，retry、C2、deterministic、golden/score/quality gate 边界清楚；但在当前形式下还不应交给 implementation worker。阻塞点是 runtime serializer 字段清单包含 `message`，而当前代码事实显示该字段可能承载 LLM audit line / programmatic issue / draft-derived 文本。请先收窄 serializer 输出字段或对白名单 message 做强约束，并补充相应 negative tests 后再进入实现。
