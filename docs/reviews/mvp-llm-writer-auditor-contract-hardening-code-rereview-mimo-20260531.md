# MVP LLM writer/auditor contract hardening code re-review

日期：2026-05-31

角色：AgentMiMo independent code reviewer。

Review target：post-review validation fix diff + controller validation evidence。

Prior review：`docs/reviews/mvp-llm-writer-auditor-contract-hardening-code-review-mimo-20260531.md`（PASS）

## Scope

- Mode：re-review follow-up，仅检查 post-review diff
- 变更文件：`tests/ui/test_cli.py`
- 变更内容：`test_analyze_cli_use_llm_missing_config_fails_before_service` 增加 `monkeypatch.delenv` 显式删除 4 个 LLM env vars；新增 `_TimeoutLLMService` 和 `test_analyze_cli_use_llm_timeout_fail_closed_without_fallback`

## Findings

未发现实质性问题。

### 变更分析

1. **missing config test fix**（`test_cli.py:1249-1255`）：原测试依赖 shell 环境不含 LLM env vars，改为 `monkeypatch.delenv(env_name, raising=False)` 显式删除 `FUND_AGENT_LLM_PROVIDER`、`FUND_AGENT_LLM_BASE_URL`、`FUND_AGENT_LLM_API_KEY`、`FUND_AGENT_LLM_MODEL`。`raising=False` 确保 env 不存在时不报错。修复正确，使测试在有真实 provider env 的 shell 中也能通过。

2. **timeout fail-closed test**（`test_cli.py:1374-1415`）：新增 `_TimeoutLLMService` 返回 `status="blocked"` + `blocked_reasons=("llm_timeout",)` 的 fake 结果，断言 exit code 1、stdout empty、stderr 含 `llm_timeout`、不含 `Authorization`/`Bearer`、不含 deterministic report。覆盖了 timeout 分类在 CLI 层的 fail-closed 路径。

3. **`_FakeLLMOrchestrationResult.blocked_reasons`**（`test_cli.py:50`）：新增 `blocked_reasons: tuple[str, ...] = ()` 字段，支持 timeout test 的 orchestration 结果构造。向后兼容，默认空元组不影响现有测试。

## Controller validation evidence

- `uv run pytest ... -q`：155 passed
- `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q`：1127 passed, coverage 91.77%
- `uv run ruff check .`：PASS
- missing-config smoke：exit 1 fail-closed
- real provider CLI smoke：exit 1, no deterministic fallback; Service diagnostic 显示 chapter 1 accepted, chapter 2 failed stop_reason `llm_timeout`, chapters 3-6 skipped `dependency_missing`

real provider smoke 结果与 contract hardening 目标一致：timeout 被精确分类为 `llm_timeout`（不再是泛化 `llm_exception`），fail-closed 无 deterministic fallback。

## Verdict

**PASS** — prior PASS stands，无新 blocking finding。

post-review diff 仅增强测试健壮性（missing config test 在有 env shell 中通过）和补充 timeout CLI 覆盖。实现代码无变更。controller validation evidence 确认 contract hardening 在真实 provider 下生效。
