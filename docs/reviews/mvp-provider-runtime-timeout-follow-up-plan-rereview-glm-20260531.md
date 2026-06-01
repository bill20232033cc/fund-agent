# MVP provider runtime timeout follow-up plan re-review - GLM

生成时间：20260531-081442

Reviewer：Gateflow plan re-reviewer（GLM 角色），不是 implementation worker。

Reviewed target：`docs/reviews/mvp-provider-runtime-timeout-follow-up-plan-20260531.md`

上一份 review：`docs/reviews/mvp-provider-runtime-timeout-follow-up-plan-review-glm-20260531.md`

Allowed edit scope：仅本 re-review artifact。

## Re-review Scope

本次审查只读：

- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/reviews/mvp-programmatic-audit-l1-calibration-controller-judgment-20260531.md`
- `docs/reviews/mvp-provider-runtime-timeout-follow-up-plan-20260531.md`
- `docs/reviews/mvp-provider-runtime-timeout-follow-up-plan-review-glm-20260531.md`
- 必要代码事实：`fund_agent/services/chapter_orchestrator.py`、`fund_agent/services/llm_provider.py`、`fund_agent/config/llm.py`、`fund_agent/ui/cli.py`、相关测试入口

未运行真实 provider，未改代码，未 push / PR / merge / release。

## 上轮阻塞点验证

### 001-已修复-[高]-runtime serializer 计划包含 `message` 字段，可能把 LLM audit/provider 派生文本写入 evidence

**修复验证**：逐条对照上轮建议与当前 plan 文本。

**建议 1：runtime serializer 默认不要输出 `message`**

- Plan §5.1 行 76-77 现在写明："Do not include the generic `message` field in the runtime serializer... This gate must not serialize `message`."
- Plan §5.1 行 69-74 的 serializer 输出字段清单不包含 `message`；列出的是 `operation`, `repair_attempt_index`, `provider_attempt_index`, `provider_max_attempts`, `provider_runtime_category`, `chapter_failure_category`, `elapsed_ms`, `status_code`, `request_id`, `finish_reason`, `response_chars`, `error_type`。
- 对 code fact `ChapterLLMRuntimeDiagnostic.message` 可能承载 writer/auditor/programmatic issue text 的风险有明确认知，且选择不输出而非白名单过滤。
- **结论：已修复。**

**建议 2：CLI timeout summary 不应包含 `message`**

- Plan §5.2 行 99 写明："The CLI summary must not print runtime diagnostic `message` or any writer/auditor/programmatic issue text."
- 新增的 CLI stderr 字段（行 85-88）全部是安全标量：`runtime_operation`, `provider_attempts`, `provider_runtime_category`, `elapsed_ms_max`。
- **结论：已修复。**

**建议 3：service diagnostic JSON 测试应显式构造含 sentinel 文本的 diagnostic，断言 serializer 输出不含这些字符串**

- Plan §7 Slice 1 行 186 写明："Omits generic diagnostic `message` even when a diagnostic carries text that contains writer issue text, auditor LLM line text, programmatic issue text, raw audit sentinel text, prompt/draft/body-like strings or secret-like strings."
- Plan §10 Review Gates 行 287 写明："Runtime serializer and CLI summary do not output diagnostic `message`; tests include negative canary strings for writer/auditor/programmatic/raw audit text."
- **结论：已修复。**

**建议 4：content-level negative assertions 覆盖 system_prompt、user_prompt、draft_markdown、raw_response 等 sentinel 文本**

- Plan §8 行 240 写明："content-level negative assertion over diagnostic JSON/stderr: injected sentinel strings representing `system_prompt`, `user_prompt`, `draft_markdown`, `raw_response`, raw audit text, provider body, writer/auditor issue text, Authorization/Bearer/key-like values must be absent."
- **结论：已修复。**

## Focus Area 验证

### Runtime serializer 是否已禁止输出通用 message

**已禁止。** §5.1 行 76 明确排除 `message`；serializer 字段清单（行 73-74）不包含 `message`。§9 行 272 evidence 禁止记录清单也包含 "generic runtime diagnostic `message`"。

### CLI summary 是否不输出 message

**不输出。** §5.2 行 99 明确禁止。新增 stderr 字段全部是安全标量，不含任何 message 或 issue text。

### 测试要求是否覆盖 writer/auditor/programmatic/raw audit canary 负断言

**已覆盖。** 三处独立要求：
- §7 Slice 1 行 186：serializer 不输出含 writer issue text、auditor LLM line text、programmatic issue text、raw audit sentinel text 的 message。
- §8 行 240：content-level negative assertion 覆盖 `system_prompt`、`user_prompt`、`draft_markdown`、`raw_response`、raw audit text、provider body、writer/auditor issue text、Authorization/Bearer/key-like values。
- §10 行 287：code review 必须验证 tests include negative canary strings for writer/auditor/programmatic/raw audit text。

### 是否仍聚焦 chapter 1 llm_timeout

**聚焦。** §1 Goal 行 15-16 明确主 blocker 为 "chapter `1` / `llm_timeout` / subcategory `unknown`"。§3 Non-goals 行 40 明确 "不修改 provider config/auth 结论；除非 env load 本身失败，否则不得把当前问题归类回 provider_config/provider_auth"。

### 不回到 provider config/auth

**未回到。** §5.3 行 103 写明 "Use existing config bounds first. Do not add new provider config variables in this gate unless implementation discovers the existing knobs cannot represent the required bounded smoke." §11 Stop Criteria 行 314 保持 "Provider config unexpectedly fails to load; report as environment preflight issue, but do not rewrite history as provider_auth/config unless same-source evidence proves it."

### 不扩大 retry

**未扩大。** §5.3 行 107-111 写明 "Keep timeout retry timeout-only. Do not retry rate limit, malformed response, network error, non-2xx or audit/programmatic failures" 和 "Keep max provider attempts bounded by existing config range `1..3`; no infinite retry"。

### 不混修 C2

**未混修。** §5.5 行 134-142 写明 "Do not fix C2 in this gate. Carry it only as a secondary diagnostic after timeout is no longer first blocker" 和 "Do not weaken C2, evidence support, ITEM_RULE or candidate facet boundaries in this gate"。

### 不放松 evidence/ITEM_RULE/candidate facet/L1/default deterministic

**未放松。** §3 行 35 写明 "不修改 writer/auditor 安全边界：证据锚点、ITEM_RULE、candidate facet、交易建议、E2 deferred、missing semantics、L1 anchor proximity 都不得放松"。§3 行 38 写明 "不改变默认 deterministic `fund-analysis analyze` / `fund-analysis checklist` 行为"。§3 行 36 写明 "不把 weak evidence、missing evidence、candidate facet 或 provider timeout 包装成 pass"。

## Open Questions

上轮 open questions 仍成立但不阻塞：

- Configured runtime budget 的记录方式：plan §4 行 51 已明确由 evidence 记录 timeout/backoff/output-ch 数值，§5.1 serializer 不读 provider config 对象。此问题已有足够约束。
- `request_id` 是否可能包含 provider 侧租户/部署信息：plan §4 行 52 将其视为 "safe request id"，与现有 provider helper 一致。若 code review 发现异常，可在实现阶段标记。

## Residual Risks

与上轮相同，不因 plan 修复而改变：

- 真实 provider runtime latency 波动性仍存在；controller judgment 必须以 authoritative CLI rerun 为主。
- 若 bounded smoke 越过 timeout 后到达 chapter 3 C2，应按 §5.5 停止并进入 C2 calibration gate。

## Lens Review Summary

- **Architecture boundary review**: PASS. Serializer 位于 Service 层，CLI 只展示安全标量，未引入 Host/Agent/dayu。
- **Best-practice review**: PASS. Serializer 默认最小化输出，`message` 字段已排除，测试要求覆盖负断言。
- **Optimal-solution review**: PASS. 增加安全 runtime serializer 和 CLI scalar summary 仍是最小路径。
- **Overengineering review**: PASS. 未引入新 provider SDK、多模型、并发、fallback 或新配置。
- **Overcoupling review**: PASS. 新增 serialization/summary helper 不要求改 provider retry 状态机；C2 明确后置。

## Conclusion

**PASS**

上轮唯一阻塞点（001：runtime serializer 包含 `message` 字段）已在 plan 的四个位置（§5.1、§5.2、§7 Slice 1、§8/§10）得到完整修复。Serializer 字段清单不包含 `message`；CLI summary 不输出 `message`；测试要求覆盖 writer/auditor/programmatic/raw audit canary 负断言；scope 仍聚焦 chapter 1 `llm_timeout`，不回到 provider config/auth，不扩大 retry，不混修 C2，不放松 evidence/ITEM_RULE/candidate facet/L1/default deterministic。

该 plan 可以安全交给 implementation worker。
