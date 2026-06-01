# MVP LLM writer/auditor contract hardening code re-review (GLM)

日期：2026-05-31
角色：AgentGLM 独立 code reviewer，非 controller、非 implementation worker。
Gate：`MVP LLM writer/auditor contract hardening gate`
前置 review：`docs/reviews/mvp-llm-writer-auditor-contract-hardening-code-review-glm-20260531.md`
Review scope：post-review validation fix only

## Re-review scope

本次 re-review 仅覆盖首轮 PASS 之后的 post-review validation fix：

1. `tests/ui/test_cli.py`：三处变更
   - `test_analyze_cli_use_llm_missing_config_fails_before_service` 增加 `monkeypatch.delenv` 清除四个 LLM 环境变量
   - 新增 `_TimeoutLLMService` fake service
   - 新增 `test_analyze_cli_use_llm_timeout_fail_closed_without_fallback` 测试
2. Implementation evidence 更新（validation-fix note）
3. Controller validation 结果：155 passed / 1127 passed / ruff PASS / missing-config smoke fail-closed / real provider smoke exit 1（chapter 1 accepted, chapter 2 llm_timeout, chapters 3-6 skipped）

不变更的部分：所有 Fund 层和 Service 层源码、所有 Fund 层和 Service 层测试。首轮 review 的 7 项审查结论不受影响。

## Post-review diff analysis

### Change 1：`monkeypatch.delenv` for missing-config test

- 文件：`tests/ui/test_cli.py:1252-1258`
- 变更：在 `test_analyze_cli_use_llm_missing_config_fails_before_service` 中，调用 `CliRunner.invoke` 前增加循环 `monkeypatch.delenv` 删除 `FUND_AGENT_LLM_PROVIDER`、`FUND_AGENT_LLM_BASE_URL`、`FUND_AGENT_LLM_API_KEY`、`FUND_AGENT_LLM_MODEL`。
- 判断：正确。原测试在已有真实 provider env 的 shell 中会跳过 missing-config 路径，因为 `load_llm_provider_config_from_env` 读到真实 env 后不报错。`monkeypatch.delenv(rasing=False)` 确保无论 shell env 状态如何，测试都进入 missing-config 分支。`rasing=False` 防止 env 不存在时报错。
- 安全性：不引入 secret、不修改运行时代码、不改变 fail-closed 语义。测试断言不变（exit 1、stdout 空、stderr 含 missing config 消息）。

### Change 2：`_TimeoutLLMService` fake service

- 文件：`tests/ui/test_cli.py:471-510`
- 变更：新增 `_FakeLLMOrchestrationResult.blocked_reasons` 字段和 `_TimeoutLLMService` 类，返回 `status="blocked"`、`issues=("llm_timeout",)`、`blocked_reasons=("llm_timeout",)` 的 fake LLM 结果。
- 判断：正确。`blocked_reasons` 字段为新增的带默认值 `()` 的 dataclass field，不影响已有 `_FakeLLMOrchestrationResult` 的使用者。`_TimeoutLLMService` 继承 `_FakeService`，只覆盖 `analyze_with_llm`，不触及 deterministic `analyze` 方法。fake service 不连接真实 provider。
- 安全性：无 secret、无真实 provider 调用。

### Change 3：`test_analyze_cli_use_llm_timeout_fail_closed_without_fallback`

- 文件：`tests/ui/test_cli.py:1370-1410`
- 变更：新增测试验证 `--use-llm` 当 Service 返回 llm_timeout 阻断结果时，CLI exit 1、stdout 空、stderr 含 "LLM 分析未完成：" 和 "llm_timeout"、stderr 不含 "Authorization"/"Bearer"、不输出 deterministic 报告。
- 判断：正确。该测试是 plan Slice C 要求的 CLI 层 timeout fail-closed 测试（plan section 10 Slice C: "增加或更新 `--use-llm` provider runtime timeout fail-closed 测试"）。首轮 review 时该测试尚未存在；post-review fix 补齐了此 gap。
- 断言完整性：
  - `exit_code == 1`：fail-closed ✓
  - `stdout == ""`：无 deterministic fallback ✓
  - `"llm_timeout" in stderr`：精确 stop reason 可见 ✓
  - `"Authorization" not in stderr`：无 secret 泄漏 ✓
  - `"Bearer" not in stderr`：无 secret 泄漏 ✓
  - `"# 0. 投资要点概览" not in output`：无 deterministic 报告 ✓
  - `analyze_called is False`：deterministic path 未被调用 ✓
  - `analyze_with_llm_called is True`：LLM path 被调用 ✓

### Controller validation results assessment

- 155 passed（targeted tests）：首轮 review 已验证通过的 Fund/Service 测试不受影响。
- 1127 passed（full suite with coverage 91.77%）：无回归。
- ruff check PASS：无 lint 问题。
- Missing-config smoke exit 1 fail-closed：与测试预期一致。
- Real provider smoke exit 1：chapter 1 accepted（writer/auditor contract hardening 生效），chapter 2 llm_timeout（provider 运行时分类生效，stop reason 精确），chapters 3-6 skipped dependency_missing（fail_fast 策略生效）。无 deterministic fallback。这属于 `MVP real provider smoke acceptance gate` 的 acceptance 范围，不阻塞当前 contract hardening gate。

## Verdict

**PASS confirmed** — 首轮 PASS 结论维持不变。

Post-review fix 仅补充了 CLI 层 timeout fail-closed 测试和 missing-config 测试环境隔离。两处变更均为测试代码，不修改运行时行为，不放松安全边界，不引入 secret 泄漏。首轮 review 的 4 条 info 级观察（N-1 至 N-4）不受影响。

Controller validation 结果与 contract hardening 目标一致：writer/auditor 协议强化使 chapter 1 通过，provider 运行时分类使 chapter 2 的 timeout 被精确报告为 `llm_timeout`。

## New findings

无新增 finding。

## Self-check

Self-check: pass

- 只执行了读取操作（diff、文件内容），未修改任何源文件。
- 未运行破坏性命令、未 commit/push/PR。
- Review artifact 未包含 API key、Authorization header、完整 provider response 或完整 writer draft。
