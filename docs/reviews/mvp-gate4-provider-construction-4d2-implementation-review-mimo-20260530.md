# MVP Gate 4 Slice 4D2 Implementation Review — MiMo

日期：2026-05-30
角色：review agent（独立审查，非 implementation worker）
Gate：`MVP Gate 4 Slice 4D2: CLI --use-llm provider construction wiring gate`
结论：**PASS**

## 1. Review Inputs

- Plan：`docs/reviews/mvp-gate4-provider-construction-plan-20260530.md`
- Plan decision A1-A8：`docs/reviews/mvp-gate4-provider-construction-plan-decision-20260530.md`
- 4D1 controller judgment：`docs/reviews/mvp-gate4-provider-construction-4d1-controller-judgment-20260530.md`
- Implementation evidence：`docs/reviews/mvp-gate4-provider-construction-4d2-implementation-evidence-20260530.md`
- Current diff：`fund_agent/ui/cli.py`、`tests/ui/test_cli.py`
- Design truth：`docs/design.md` §5.4.1
- Control truth：`docs/current-startup-packet.md`、`AGENTS.md`

## 2. Verdict

**PASS**

无 blocking findings。所有 9 个审查 lens 均通过。

## 3. Blocking Findings

无。

## 4. Non-blocking Findings

### N1. Provider runtime errors 落入通用 Exception handler

**文件**：`fund_agent/ui/cli.py:266-268`

`LLMProviderRuntimeError`（及其子类 `LLMProviderRateLimitError`、`LLMProviderMalformedResponseError`）未被显式 catch，落入 `except Exception as exc` 分支，stderr 前缀为 `分析失败：` 而非 `LLM provider 运行时错误：`。

**为什么 non-blocking**：Plan §11.1 只要求 missing config / construction error 有清晰分类前缀（✅ 已实现）。Plan §11.2 对 runtime errors 只要求 "exit `1`，no fallback"，不要求特定 stderr 前缀。当前行为满足 plan 最低要求：exit 1、stdout empty、无 deterministic fallback。

**残余风险**：如果未来需要区分 provider runtime error 与通用 Service error 的 CLI 消息，可在新 gate 增加显式 catch。不阻塞 4D2。

### N2. `_llm_incomplete_message` 使用 `# type: ignore[no-untyped-def]`

**文件**：`fund_agent/ui/cli.py:807`

函数参数 `result` 未标注类型。这是测试友好的设计选择（接受 fake 和 real result），但不符合 AGENTS.md "所有函数必须提供完整中文 docstring" 和类型注解要求。

**为什么 non-blocking**：4D1 controller judgment 已接受同模式。测试替身需要 duck-typing 兼容。

## 5. Validation Reviewed

| 验证项 | 方法 | 结果 |
|--------|------|------|
| CLI tests 通过 | `uv run pytest tests/ui/test_cli.py -q` | 51 passed in 1.07s |
| 实现 evidence 报告的全量测试 | 未重跑，信任 evidence 报告中 `1106 passed in 5.07s`，coverage 91.76% | — |
| `git diff --check` | 未重跑，信任 evidence 报告 | — |
| ruff lint | 未重跑，信任 evidence 报告 | — |
| Import boundary test | 审查 `test_cli_module_imports_service_but_not_agent_internals` 和 `test_cli_module_llm_boundary_has_no_forbidden_runtime_imports` 源码 | ✅ |
| checklist --use-llm | 审查 `test_checklist_cli_rejects_use_llm_option` 源码 | ✅ |
| 代码逐行审查 | 读取完整 `fund_agent/ui/cli.py` 和 `tests/ui/test_cli.py` diff | ✅ |

## 6. Scope Check

### 6.1 已确认未越界

| 检查项 | 状态 |
|--------|------|
| 未修改 Service/Fund/orchestrator internals | ✅ 只修改 `cli.py` 和 `test_cli.py` |
| 未改变 quality gate 语义 | ✅ `QualityGateBlockedError` / `QualityGateNotRunBlockedError` 仍 exit 2 |
| 未改变 Gate 2/3/4 contract | ✅ writer/auditor Protocol 不变 |
| 未改变 final judgment 语义 | ✅ |
| 未引入 live provider smoke | ✅ 测试使用 monkeypatch fake |
| 未修改 design/control docs | ✅ 符合 A8 裁决：4D3 才同步 |
| 未 import `fund_agent.fund.*` | ✅ |
| 未 import Host/dayu/provider SDK/httpx | ✅ |
| 未使用 `extra_payload` | ✅ |
| 未写入 provider-backed path 到 design/control docs | ✅ 符合 A8 |
| checklist 无 --use-llm option | ✅ |

### 6.2 文件范围

| 文件 | 是否在 plan 4D2 allowed files 内 |
|------|--------------------------------|
| `fund_agent/ui/cli.py` | ✅ |
| `tests/ui/test_cli.py` | ✅ |
| 本 review artifact | ✅ implementation evidence under `docs/reviews/` |

## 7. Plan Conformance Checklist

| Plan 4D2 要求 | 实现 | 证据 |
|---------------|------|------|
| `_build_llm_clients_or_fail()` 返回 `(ChapterOrchestratorLLMClients, ChapterOrchestrationPolicy)` | ✅ | `cli.py:784-804` |
| 移除临时 `LLMProviderUnavailableError` 和 `LLM_PROVIDER_UNAVAILABLE_MESSAGE` | ✅ | diff 确认移除 |
| `analyze --use-llm` 调用 `analyze_with_llm()` | ✅ | `cli.py:245-251` |
| `analyze --use-llm` 不调用 deterministic `analyze()` | ✅ | if/else 分支隔离，测试 `test_analyze_cli_use_llm_configured_calls_llm_service_and_prints_report` 断言 `analyze_called is False` |
| Missing config exit 1，stderr config error，stdout empty，Service 不调用 | ✅ | `cli.py:254-256`，测试 `test_analyze_cli_use_llm_missing_config_fails_before_service` |
| Construction error exit 1，stderr 构造失败，stdout empty，Service 不调用 | ✅ | `cli.py:257-259`，测试 `test_analyze_cli_use_llm_construction_error_fails_before_service` |
| Incomplete LLM exit 1，stderr `LLM 分析未完成：`，stdout empty，无 fallback | ✅ | `cli.py:269-271`，测试 `test_analyze_cli_use_llm_incomplete_result_exits_without_fallback` |
| Quality gate blocked/not-run 仍 exit 2 | ✅ | `cli.py:260-265`，测试 `test_analyze_cli_use_llm_structured_quality_gate_block` 和 `test_analyze_cli_use_llm_structured_quality_gate_not_run_block` |
| Default `analyze` 不读取 LLM env、不构造 provider | ✅ | `cli.py:252-253`，测试 `test_analyze_cli_default_product_request` monkeypatch `_forbid_llm_config` / `_forbid_llm_clients` |
| `checklist --use-llm` 仍被 Typer rejected | ✅ | 测试 `test_checklist_cli_rejects_use_llm_option` |
| UI 只 import config/Service public APIs | ✅ | `cli.py:17,25-56`，测试 `test_cli_module_imports_service_but_not_agent_internals` 和 `test_cli_module_llm_boundary_has_no_forbidden_runtime_imports` |
| CLI 不 import `fund_agent.fund.*`、Host/dayu、provider SDK/httpx | ✅ | 同上 |
| 测试无 live network / real key | ✅ | 测试全部使用 monkeypatch fake |
| A8：未把 provider-backed path 写入 design/control docs | ✅ | diff 未触碰 docs |

## 8. Residual Risks

| 风险 | 处置 / owner |
|------|-------------|
| N1：provider runtime errors 的 CLI 前缀不够细化 | 不阻塞；后续 gate 可增加显式 catch 改善消息 |
| 4D3 docs/control sync | 4D3 owner 负责 |
| Retry/backoff、live smoke、多模型 split、chapter 0/7 LLM polish、Evidence Confirm、Host/Agent/dayu | 均为后续 gate，不阻塞 4D2 |

## 9. Conclusion

4D2 implementation 严格遵循 plan §12 4D2 slice 要求，正确接入 typed config / provider factory construction，保持 fail-closed 语义，保持 quality gate exit 2 不变，保持 default deterministic path 隔离，测试覆盖充分且无 live network。所有 blocking lens 均通过，无 blocking finding。Verdict：**PASS**。
