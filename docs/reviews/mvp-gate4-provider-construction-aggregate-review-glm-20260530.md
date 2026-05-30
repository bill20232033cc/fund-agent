# MVP Gate 4 Slice 4D Provider Construction Aggregate Review (GLM)

日期：2026-05-30
角色：aggregate review agent (GLM)
Gate：`MVP Gate 4 Slice 4D provider-backed CLI path`
分类：`heavy`
Verdict：**pass**

---

## 1. Review Scope

本聚合审查覆盖 commits `b688d30` (plan accept)、`26203d3` (4D1 provider factory)、`ab0590a` (4D2 CLI wiring)、`4d0c19f` (4D3 docs sync) 及其全部 artifacts。

审查范围限于上述四个 commit 引入的变更；不审查无关的 release-maintenance untracked files。

---

## 2. Review Lens Findings

### Lens 1: End-to-end `--use-llm` path

**结论：满足。**

端到端路径 `CLI typed config → Service provider factory → analyze_with_llm → Gate 3/4` 已完整实现：

1. `cli.py:784-804` `_build_llm_clients_or_fail()` 调用 `load_llm_provider_config_from_env()` 然后 `build_chapter_llm_clients(config)` 并构造 `ChapterOrchestrationPolicy(max_output_chars=config.max_output_chars)`。
2. `cli.py:243-251` `use_llm=True` 分支调用 `FundAnalysisService().analyze_with_llm(request, llm_clients, chapter_policy)`。
3. `cli.py:269-271` `result.final_assembly_result.report_markdown is None` 时 exit 1、stderr 以 `LLM 分析未完成：` 开头、stdout 为空。
4. 无 deterministic fallback。测试 `test_analyze_cli_use_llm_incomplete_result_exits_without_fallback` 断言 `analyze_called=False`、`stdout==""`、`"# 0. 投资要点概览" not in result.output`。

### Lens 2: Default analyze/checklist remain deterministic

**结论：满足。**

1. `cli.py:252-253` `else` 分支调用 `FundAnalysisService().analyze(request)`，不读取 LLM env、不构造 provider。
2. `checklist` 命令（`cli.py:277-351`）没有 `--use-llm` 参数。
3. 测试 `test_checklist_cli_rejects_use_llm_option` 断言 exit code 非 0 且 Service 未被调用。

### Lens 3: Security — API key protection

**结论：满足。**

1. `llm.py:54` `api_key: str = field(repr=False)` — API key 不出现在 `repr(config)`。
2. `llm.py:152-155` `_load_api_key()` 空白值视为 missing，错误消息只包含 env var 名，不含 key 值。
3. `llm_provider.py:327-344` `_safe_http_error_message()` 只输出 status code 和 request-id header，不输出 Authorization header、prompt body 或 response body。
4. 配置测试 `test_load_llm_provider_config_from_env_success_and_hides_api_key` 断言 `"secret-value" not in repr(config)`。
5. 缺失配置测试断言 `"secret-value" not in str(exc_info.value)`。
6. Provider 错误测试（429/5xx/network/timeout/malformed）均断言 key 和 prompt 不泄漏。
7. 文档（`fund_agent/config/README.md`）显式声明 API key repr 隐藏和安全处理策略。

### Lens 4: Architecture boundary

**结论：满足。**

1. UI 只导入 `fund_agent.config.llm` 和 `fund_agent.services` 公共 API（`cli.py:17,25-56`）。
2. `grep` 确认 CLI 无 `fund_agent.fund` 导入。
3. Service 拥有 provider factory（`llm_provider.py`）。
4. Fund writer/auditor 只依赖 Protocol，不导入 `httpx`、env/config 或 Service provider factory。
5. 无 Host/dayu 运行时依赖。
6. 无 `extra_payload` 使用。
7. `fund_agent/services/__init__.py` 将 `LLMProviderConstructionError`、`LLMProviderRuntimeError` 等类型 re-export 到 Service 公共命名空间，CLI 通过 Service `__init__` 获取。
8. 两个导入边界测试强制执行：
   - `test_cli_module_imports_service_but_not_agent_internals` — 禁止 `fund_agent.fund` 和 `fund_agent.application`。
   - `test_cli_module_llm_boundary_has_no_forbidden_runtime_imports` — 禁止 `dayu`、`extra_payload`、`openai`、`anthropic`、`httpx` 等。

### Lens 5: Failure semantics

**结论：满足。**

| 失败类别 | 检测位置 | CLI 行为 | 测试覆盖 |
|---|---|---|---|
| Missing provider/model/base_url/key | `llm.py` config loader | exit 1, stderr 配置错误, stdout 空 | `test_load_llm_provider_config_missing_required_values_fail` + CLI `test_analyze_cli_use_llm_missing_config_fails_before_service` |
| Unsupported provider | `llm.py` `_load_provider_name` | exit 1, stderr "unsupported provider" | `test_load_llm_provider_config_unsupported_provider_fails` |
| Empty API key | `llm.py` `_load_api_key` | exit 1, stderr "missing API key value" | `test_load_llm_provider_config_empty_api_key_fails` |
| Provider construction failure | `llm_provider.py` `build_chapter_llm_clients` | exit 1, stderr "构造失败" | CLI `test_analyze_cli_use_llm_construction_error_fails_before_service` |
| HTTP 429 | `llm_provider.py` `_complete` | `LLMProviderRateLimitError` | `test_rate_limit_maps_to_typed_error_without_secret_prompt_or_body` |
| HTTP 5xx/4xx | `llm_provider.py` `_complete` | `LLMProviderRuntimeError` | `test_http_error_maps_to_runtime_error_without_full_body` |
| Network/timeout | `llm_provider.py` `_complete` | `LLMProviderRuntimeError` | `test_network_error_maps_to_runtime_error...` + `test_timeout_maps_to_runtime_error...` |
| Malformed JSON | `llm_provider.py` `_extract_text` | `LLMProviderMalformedResponseError` | `test_malformed_response_maps_to_typed_error` |
| Incomplete final assembly | `cli.py:269-271` | exit 1, stderr "LLM 分析未完成", stdout 空 | `test_analyze_cli_use_llm_incomplete_result_exits_without_fallback` |
| Quality gate block | `cli.py:263-265` | exit 2 | `test_analyze_cli_use_llm_structured_quality_gate_block` |
| Quality gate not-run | `cli.py:260-262` | exit 2 | `test_analyze_cli_use_llm_structured_quality_gate_not_run_block` |

所有 config/construction 失败都在 Service 调用前发生（`cli.py:254-258`）。Runtime provider 失败经过 Service orchestrator 收敛为 `llm_exception` → incomplete final assembly → exit 1。无 deterministic fallback。

### Lens 6: Test isolation

**结论：满足。**

1. Config tests（`tests/config/test_llm_config.py`，14 个测试）：使用 `dict(_BASE_ENV)` fake env mapping，不读取 `os.environ` 或真实网络。
2. Provider tests（`tests/services/test_llm_provider.py`，11 个测试）：使用 `httpx.MockTransport` 注入 fake HTTP response，不需要真实 key。
3. CLI LLM tests（`tests/ui/test_cli.py`，8 个 LLM 相关测试）：使用 `monkeypatch` 替换 `load_llm_provider_config_from_env`、`build_chapter_llm_clients` 和 `FundAnalysisService`。
4. 全量回归 `1106 passed`，总 coverage `91.76%`。
5. 无 live provider smoke、无真实 API key、无网络测试。

### Lens 7: Docs/control consistency after B1 fix

**结论：满足。**

1. 4D3 controller judgment 记录了 B1 blocking finding：`docs/implementation-control.md` 原文 "only production report/checklist mainline" 与 accepted `analyze --use-llm` opt-in path 冲突。
2. B1 已修复为 "Current deterministic `fund-analysis analyze/checklist` remains the default production report/checklist mainline; `fund-analysis analyze --use-llm` is the explicit provider-backed opt-in path."。
3. MiMo re-review `pass`，GLM re-review `pass`。
4. Controller 执行了 stale phrase scan：`rg -n "only production report/checklist mainline|LLM provider 未配置/未实现|provider construction 未接受|尚未接受|provider 未配置/未实现"` — no matches。
5. `docs/design.md` §5.4.1 记录 Route C Gate 4 Slice 4D 为 current accepted code fact，保持 Host/Agent/dayu 为 future-only。
6. `README.md` 记录 `--use-llm` 为显式 opt-in，默认 deterministic 路径为主。
7. `docs/current-startup-packet.md` 和 `docs/implementation-control.md` 指向 `MVP Gate 4 Slice 4D aggregate review gate`，commits `26203d3` 和 `ab0590a` 已记录。
8. Next entry 是 aggregate review gate。

### Lens 8: Hidden regressions or missing tests

**结论：无阻塞性发现。**

逐项检查：

1. **`build_chapter_llm_clients()` broad `except Exception`**：`llm_provider.py:214` 捕获非 `LLMProviderConstructionError` 异常并包装为 `LLMProviderConstructionError("failed to construct LLM provider client") from exc`。4D1 controller 已裁决为 non-blocking residual，`from exc` 保留 cause chain，顶层消息不泄漏 prompt/key/body。
2. **Provider runtime error CLI message prefix**：`LLMProviderRuntimeError` 会落入 `cli.py:266-268` 的通用 `except Exception` handler，输出 `分析失败：...` 而非 provider-specific prefix。4D2 controller 已裁决为 non-blocking residual，行为仍为 fail-closed exit 1。未来 polish gate 可增加 typed catch。
3. **`_llm_incomplete_message()` duck typing**：`cli.py:807` 使用 `type: ignore[no-untyped-def]`。4D2 controller 已裁决为 non-blocking。
4. **`_chat_completions_url` base URL 派生**：`llm_provider.py:232-237` 正确处理 trailing `/v1`、已有 `/chat/completions` suffix 和默认追加。无测试直接覆盖此函数的 edge case，但 provider 整体测试通过 MockTransport 间接验证了 URL 构造。
5. **No test for provider returning empty string `content`**：`_extract_text` 对空字符串 content 不拒绝（只检查 `isinstance(content, str)`）。这符合 plan §11.2："provider returns empty text → return protocol response with empty text → existing writer `llm_empty_response`"。行为正确。
6. **`LLMProviderResponse` 不是 frozen dataclass**：与 `LLMProviderConfig` 的 frozen 不一致，但 `LLMProviderResponse` 是内部构造类型，只在 `_extract_text` 内创建。不构成问题。
7. **`services/__init__.py` re-export 具体类**：`OpenAICompatibleChapterLLMClient` 和所有 error types 被导出。4D1 GLM review 已 noted 为 non-blocking。当前 CLI 通过 Service `__init__` 导入 `build_chapter_llm_clients` 和 `LLMProviderConstructionError`，符合 plan §8.2 边界规则。未来如需收敛公共 API surface，可由独立 consistency gate 处理。

---

## 3. Validation Reviewed

Controller 在 4D1、4D2、4D3 三个 controller judgment 中分别重新执行了：

- `ruff check` — 全部 passed
- Targeted pytest（4D1: 37 passed; 4D2: 51 passed; 4D3: 125 passed）
- Full regression（4D1: 1101 passed, 91.75%; 4D2: 1106 passed, 91.76%; 4D3: 1106 passed, 91.76%）
- `git diff --check` — 全部 passed
- Stale phrase scan（4D3）— no matches
- Path existence checks（4D3）— passed

Aggregate review 确认所有 controller validation 命令覆盖了：
- 变更代码 lint
- 变更测试 + 下游依赖测试
- 全量 regression + coverage gate
- 文档残留检测

---

## 4. Residual Risks

| Residual | Disposition | Owner / next gate |
|---|---|---|
| `build_chapter_llm_clients()` broad except | Non-blocking; `from exc` preserves cause chain | Future provider polish gate |
| Provider runtime error CLI message classification | Non-blocking; fail-closed exit 1 语义正确 | Future CLI polish gate |
| `_llm_incomplete_message()` duck typing | Non-blocking; helper 不改变 public contract | Future CLI polish gate |
| No retry/backoff | Accepted MVP simplification | Future reliability gate |
| Single model for writer/auditor | Accepted MVP simplification | Future multi-model gate |
| No live provider smoke in pytest | Intentional; live smoke is manual/explicit | Future live smoke gate |
| `services/__init__.py` re-exports concrete classes | Non-blocking; current import style matches existing pattern | Future API surface consistency gate |
| Chapter 0/7 LLM polish, Evidence Confirm | Not in 4D scope | Future LLM polish / Evidence Confirm gate |
| Host/Agent/dayu integration | Deferred to Gate 5 | Future architecture gate |

---

## 5. Verdict

**pass**

理由：

1. 端到端 `--use-llm` 路径完整：typed env config → Service provider factory → `analyze_with_llm()` → Gate 3/4，无 deterministic fallback。
2. 默认 `analyze` 和 `checklist` 不读取 LLM env、不构造 provider，确定性路径完全未变。
3. API key 在 `repr`、错误消息、HTTP 错误文本中均不泄漏。
4. UI 只依赖 config/Service 公共 API，无 `fund_agent.fund`、无 Host/dayu、无 `extra_payload`、无 vendor SDK。
5. 所有失败语义均为 fail-closed：config/construction 失败在 Service 前退出 1；runtime/malformed/rate-limit 经 orchestrator 收敛后退出 1；quality gate 阻断退出 2 不变。
6. 全部测试使用 fake env、`httpx.MockTransport` 和 monkeypatch，无 live network/key。
7. 4D3 B1 docs contradiction 已修复并经两份独立 re-review 确认 pass；stale phrase scan 无残留。
8. 无阻塞性遗漏测试或隐藏回归。

4D1/4D2/4D3 三个 slice 的 controller judgment、MiMo review、GLM review 证据链完整，全量 regression `1106 passed, 91.76% coverage` 稳定。Non-blocking residuals 已由各 controller 裁决并记录 owner。
