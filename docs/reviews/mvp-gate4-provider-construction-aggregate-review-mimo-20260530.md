# MVP Gate 4 Slice 4D Provider Construction Aggregate Review

日期：2026-05-30
角色：aggregate review agent（MiMo）
Gate：`MVP Gate 4 Slice 4D provider-backed CLI path` aggregate review
分类：`heavy`
范围：commits b688d30, 26203d3, ab0590a, 4d0c19f 及其 artifacts

---

## Verdict

**PASS**

所有 8 个审查 lens 通过。无 blocking finding。3 个 non-blocking residual 已由先前 controller 4D1/4D2 接受。

---

## 1. End-to-End `--use-llm` Path

**审查结论：PASS**

完整路径：

```text
CLI analyze --use-llm
  -> _build_llm_clients_or_fail()                       # cli.py:784-804
    -> load_llm_provider_config_from_env()              # config/llm.py:59-92
    -> build_chapter_llm_clients(config)                # services/llm_provider.py:197-216
    -> ChapterOrchestrationPolicy(max_output_chars=...)  # from config
  -> FundAnalysisService().analyze_with_llm(request, llm_clients, chapter_policy)
  -> Gate 3 ChapterOrchestrator -> Gate 4 FinalChapterAssembler
  -> stdout or exit 1
```

验证点：

- `cli.py:243-251`：`use_llm` 分支调用 `_build_llm_clients_or_fail()` 返回 `(ChapterOrchestratorLLMClients, ChapterOrchestrationPolicy)`，然后调用 `analyze_with_llm()`。
- `cli.py:253`：`else` 分支走确定性 `analyze()`。
- `cli.py:269-271`：LLM 结果 `report_markdown is None` 时 exit 1，无 deterministic fallback。
- `cli.py:254-259`：`LLMProviderConfigError` 和 `LLMProviderConstructionError` 在 Service 调用前被捕获，exit 1，stdout 为空。
- `cli.py:260-265`：Quality gate `block/not_run` 在 LLM path 中仍 exit 2，语义不变。

CLI 测试覆盖：

| 场景 | 测试 | 断言 |
|------|------|------|
| missing config | `test_analyze_cli_use_llm_missing_config_fails_before_service` | exit 1, stdout 空, 不调用 Service |
| configured path | `test_analyze_cli_use_llm_configured_calls_llm_service_and_prints_report` | 调用 `analyze_with_llm` 不调用 `analyze`, 传递 typed policy |
| construction error | `test_analyze_cli_use_llm_construction_error_fails_before_service` | exit 1, stdout 空, 不调用 Service |
| incomplete result | `test_analyze_cli_use_llm_incomplete_result_exits_without_fallback` | exit 1, stdout 空, 不回退 deterministic |
| gate block (LLM) | `test_analyze_cli_use_llm_structured_quality_gate_block` | exit 2 |
| gate not-run (LLM) | `test_analyze_cli_use_llm_structured_quality_gate_not_run_block` | exit 2 |
| default analyze 不读 LLM | `test_analyze_cli_default_product_request` | monkeypatch `_forbid_llm_config` / `_forbid_llm_clients` 断言不被调用 |

无 deterministic fallback：所有 LLM failure path 均 exit 1/2，stdout 为空。

---

## 2. Default analyze/checklist Remain Deterministic

**审查结论：PASS**

- `cli.py:243`：`if use_llm:` 分支只在显式 `--use-llm` flag 时进入。
- `cli.py:253`：`else` 分支走确定性 `FundAnalysisService().analyze(request)`。
- `checklist` 命令（`cli.py:276-351`）无 `--use-llm` 参数。
- 测试 `test_checklist_cli_rejects_use_llm_option` 验证 `checklist --use-llm` 被 Typer 拒绝。
- 测试 `test_analyze_cli_default_product_request` 通过 monkeypatch `_forbid_llm_config` / `_forbid_llm_clients` 确保默认 path 不读 LLM env、不构造 provider。
- `config/llm.py` 不被默认 analyze/checklist 导入——CLI 中 `load_llm_provider_config_from_env` 和 `build_chapter_llm_clients` 只在 `if use_llm:` 块内调用。

---

## 3. Security: API Key / Prompt / Body Leak

**审查结论：PASS**

API key 处理：

| 位置 | 机制 | 验证 |
|------|------|------|
| `config/llm.py:54` | `api_key: str = field(repr=False)` | 测试 `test_load_llm_provider_config_from_env_success_and_hides_api_key` 断言 `"secret-value" not in repr(config)` |
| `config/llm.py:152-154` | 空白 key 视为 missing | 测试 `test_load_llm_provider_config_empty_api_key_fails` |
| `config/llm.py:154` | 错误消息只含 env var 名，不含 key 值 | 测试断言 `"secret-value" not in str(exc_info.value)` |
| `services/llm_provider.py:327-344` | `_safe_http_error_message()` 只含 status_code 和 request_id | 测试断言 `"test-secret" not in message` 和 `"full error body" not in message` |
| `services/llm_provider.py:179-181` | TransportError/Timeout 消息不泄漏 prompt/key | 测试断言 `"writer user" not in message` 和 `"test-secret" not in message` |
| `services/llm_provider.py:191` | JSON parse error 不泄漏 key | 测试覆盖 |
| `cli.py:255-258` | Config/construction error 使用 typed exception 消息 | 不含 key |
| `tests/README.md:244` | 文档化 "不需要真实 API key" | — |

Prompt body 不泄漏：

- `services/llm_provider.py:179-181`：TransportError/Timeout 异常消息固定为 `"LLM provider request timed out"` / `"LLM provider network error"`，不包含 `system_prompt` 或 `user_prompt`。
- `_safe_http_error_message()` 不包含 response body。
- 测试显式断言 `"writer user" not in message`。

Authorization header 不泄漏：

- 错误消息中不含 `Authorization` 或 `Bearer`。
- 测试覆盖 429/4xx/5xx/network/timeout/malformed 六类错误路径。

---

## 4. Architecture Boundary

**审查结论：PASS**

UI -> config/Service 公共 API：

- `cli.py:17-18`：只导入 `fund_agent.config.llm`（直接导入，符合 plan A6）。
- `cli.py:25-56`：只从 `fund_agent.services` 导入公共类型。
- 测试 `test_cli_module_imports_service_but_not_agent_internals` 断言 CLI 源码不含 `fund_agent.fund.`。
- 测试 `test_cli_module_llm_boundary_has_no_forbidden_runtime_imports` 断言不含 `dayu`, `extra_payload`, `openai`, `anthropic`, `httpx`, `provider_sdk`, `pdf_cache` 等。

Service owns provider factory：

- `services/llm_provider.py`：Service 层 adapter，导入 Fund Protocol types（`ChapterLLMClient` 等）构造 `ChapterOrchestratorLLMClients`。
- `build_chapter_llm_clients()` 返回 `ChapterOrchestratorLLMClients(writer=client, auditor=client)`。
- CLI 不直接构造 provider adapter，通过 `build_chapter_llm_clients(config)` 间接获取。

Fund writer/auditor only Protocol：

- `services/llm_provider.py:18-28`：导入 Fund Protocol types 用于 adapter 实现。
- Fund writer/auditor 不导入 provider SDK、httpx、env/config 或 CLI。
- `chapter_writer.py` 和 `chapter_auditor.py` 未被 4D 修改。

No Host/dayu, no extra_payload：

- `cli.py` 源码不含 `dayu`, `extra_payload`, `host`, `agent`（除 target 架构注释外）。
- 4D 未创建 `fund_agent/host` 或 `fund_agent/agent`。
- 所有 provider 参数通过 typed `LLMProviderConfig` 显式声明，无 `extra_payload`。

---

## 5. Failure Semantics

**审查结论：PASS**

Config/construction fail before Service：

| Failure | Location | CLI behavior | Test |
|---------|----------|-------------|------|
| missing provider | config/llm.py | exit 1, stderr `LLM provider 配置错误：missing FUND_AGENT_LLM_PROVIDER`, stdout 空 | `test_analyze_cli_use_llm_missing_config_fails_before_service` |
| unsupported provider | config/llm.py:110-112 | exit 1, stderr config error | `test_load_llm_provider_config_unsupported_provider_fails` |
| missing model | config/llm.py:77 | exit 1, stderr config error | parametrized `test_load_llm_provider_config_missing_required_values_fail` |
| missing/invalid base_url | config/llm.py:116-135 | exit 1, stderr config error | parametrized `test_load_llm_provider_config_invalid_base_url_fails` |
| missing API key | config/llm.py:138-154 | exit 1, stderr names env var, stdout 空 | `test_load_llm_provider_config_empty_api_key_fails` |
| invalid timeout | config/llm.py:158-182 | exit 1, stderr config error | parametrized `test_load_llm_provider_config_timeout_bounds_fail` |
| construction failure | services/llm_provider.py:210-215 | exit 1, stderr `LLM provider 构造失败：...`, stdout 空 | `test_analyze_cli_use_llm_construction_error_fails_before_service` |

Runtime fail closed：

| Failure | Provider adapter | CLI |
|---------|-----------------|-----|
| timeout | `LLMProviderRuntimeError("LLM provider request timed out")` | generic catch, exit 1 |
| network | `LLMProviderRuntimeError("LLM provider network error")` | generic catch, exit 1 |
| 429 | `LLMProviderRateLimitError` | generic catch, exit 1 |
| 4xx/5xx | `LLMProviderRuntimeError` with status only | generic catch, exit 1 |
| malformed JSON | `LLMProviderMalformedResponseError` | generic catch, exit 1 |
| empty text | returns empty `text` in protocol response | writer/auditor existing fail-closed |
| incomplete assembly | `report_markdown is None` | exit 1, no fallback |

Quality gate exit 2 unchanged：

- LLM path 的 `QualityGateBlockedError` 和 `QualityGateNotRunBlockedError` 仍被 `cli.py:260-265` 捕获并 exit 2。
- 测试 `test_analyze_cli_use_llm_structured_quality_gate_block` 和 `test_analyze_cli_use_llm_structured_quality_gate_not_run_block` 验证。

---

## 6. Test Isolation

**审查结论：PASS**

| 测试文件 | 隔离机制 | 无 live network |
|---------|---------|----------------|
| `tests/config/test_llm_config.py` | fake env mapping（`dict(_BASE_ENV)`） | ✅ 不读真实环境变量 |
| `tests/services/test_llm_provider.py` | `httpx.MockTransport` + fake config | ✅ 不访问真实 HTTP |
| `tests/ui/test_cli.py` | monkeypatch `cli.FundAnalysisService` / `cli.load_llm_provider_config_from_env` / `cli.build_chapter_llm_clients` | ✅ 不访问真实 provider |

验证点：

- `test_llm_provider.py` 的 `_config()` 使用 `api_key="test-secret"`，不读真实 env。
- `test_llm_provider.py` 的 `_provider_client()` 构造 `httpx.Client(transport=httpx.MockTransport(handler))`，handler 返回 fake JSON。
- `test_cli.py` 的 `_fake_load_llm_config()` 返回 `_FakeLLMConfig()`，不读真实 env。
- `test_cli.py` 的 `_fake_build_llm_clients()` 返回 `_FakeLLMClients()`，不构造真实 HTTP client。
- `test_cli.py` 的 `_forbid_llm_config()` 和 `_forbid_llm_clients()` 断言默认 path 不调用 LLM config/factory。
- `tests/README.md:244` 文档化 "不需要真实 API key，不做 live provider smoke"。

---

## 7. Docs/Control Consistency After B1 Fix

**审查结论：PASS**

4D3 controller judgment 记录了 B1 blocking finding：`docs/implementation-control.md` 仍称 deterministic `analyze/checklist` 是 `only production report/checklist mainline`，与已接受的 `--use-llm` 路径矛盾。

B1 fix 后措辞：

```text
Current deterministic `fund-analysis analyze/checklist` remains the default production
report/checklist mainline; `fund-analysis analyze --use-llm` is the explicit provider-backed
opt-in path.
```

验证点（controller 4D3 judgment 记录）：

- `rg -n "only production report/checklist mainline|LLM provider 未配置/未实现|provider construction 未接受|尚未接受|provider 未配置/未实现" docs/implementation-control.md docs/current-startup-packet.md docs/design.md README.md fund_agent/README.md fund_agent/config/README.md tests/README.md` — no matches，expected。
- MiMo re-review verdict：`pass`。
- GLM re-review verdict：`pass`。

docs/control sync 一致性：

| 文档 | 当前事实 | 未来设计 |
|------|---------|---------|
| `docs/design.md` | Route C Gate 4 Slice 4D accepted locally | Host/Agent/dayu Gate 5 future |
| `docs/current-startup-packet.md` | `--use-llm` is explicit opt-in, deterministic default | retry/backoff, live smoke, multi-model future |
| `docs/implementation-control.md` | 4D1/4D2/4D3 accepted, next = aggregate review | residuals future-only |
| `README.md` | `--use-llm` env contract, fail-closed behavior | — |
| `fund_agent/README.md` | Service-owned provider construction, Fund Protocol boundary | — |
| `fund_agent/config/README.md` | typed LLM env config, secret handling | — |
| `tests/README.md` | fake env, MockTransport, monkeypatch, no live smoke | — |

Next entry point 正确指向 `MVP Gate 4 Slice 4D aggregate review gate`。

---

## 8. Hidden Regressions / Missing Tests

**审查结论：PASS — 无 blocking missing test**

单文件覆盖率：

| 文件 | 覆盖率 | 评估 |
|------|--------|------|
| `fund_agent/config/llm.py` | 100% | ✅ |
| `fund_agent/services/llm_provider.py` | 88% | ⚠️ 低于 80% 目标但已知 non-blocking |
| `fund_agent/ui/cli.py` | 87% | ⚠️ 已有大量测试，未覆盖路径为 thermometer/extraction-score/golden 等非 4D scope |

`llm_provider.py` 未覆盖行：

- Line 95：`OpenAICompatibleChapterLLMClient.__init__` 中 `provider_name != "openai_compatible"` 分支。此路径在 `build_chapter_llm_clients` 的 `except LLMProviderConstructionError: raise` 中已覆盖（config 层已过滤不支持的 provider），属于 defense-in-depth。
- Lines 212-215：`build_chapter_llm_clients` 的 broad `except Exception`。4D1 controller 已裁决为 non-blocking。
- Line 234/237：`_chat_completions_url` 的 `/v1` suffix 和 `/chat/completions` suffix 识别。已有 URL 形态测试间接覆盖。
- Lines 343/364：`_safe_http_error_message` / `_request_id` 的 request-id header 读取。已有 429 测试覆盖 `x-request-id`。

全部未覆盖行均属于 defense-in-depth 或间接覆盖路径，不构成 blocking gap。

回归验证：

```text
uv run ruff check .                           — passed
uv run pytest (targeted 125 tests)            — 125 passed in 1.20s
uv run pytest (full 1106 tests)               — 1106 passed in 5.14s, coverage 91.76%
```

---

## Findings Summary

### Non-blocking Findings (已由 4D1/4D2 controller 接受)

| ID | Severity | Description | Controller Disposition |
|----|----------|-------------|----------------------|
| N1 | non-blocking | `_llm_incomplete_message()` 使用 duck typing 无显式 result annotation | 4D2 controller accepted：CLI display helper，兼容 real result 与测试替身 |
| N2 | non-blocking | `build_chapter_llm_clients()` broad `except Exception` 可进一步收窄 | 4D1 controller accepted：`from exc` 保留 cause，顶层消息不泄漏 prompt/key/body |
| N3 | non-blocking | provider runtime error 可能通过 generic `分析失败：` handler 暴露（如果 leaked past Service） | 4D2 controller accepted：正常 orchestration path 将 provider runtime error 收敛为 incomplete final assembly |

### Blocking Findings

无。

---

## Validation Reviewed

| 验证项 | 结果 |
|--------|------|
| `uv run ruff check .` | passed |
| targeted regression (config + provider + CLI + LLM service + orchestrator) | 125 passed in 1.20s |
| full coverage regression | 1106 passed in 5.14s, 91.76% |
| `git diff --check` | passed（由 4D3 controller 记录） |
| stale/conflicting phrase scan | no matches（由 4D3 controller 记录） |
| path existence check | all required files exist（由 4D3 controller 记录） |

---

## Residual Risks

| Risk | Disposition | Owner |
|------|------------|-------|
| `openai_compatible` HTTP shape may not fit eventual production vendor | Stop condition: controller/user chooses another provider contract before implementation | Future provider-specific gate |
| Single model for writer and auditor | Accepted MVP simplification | Future multi-model gate |
| No retry/backoff | Accepted fail-closed behavior | Future reliability gate |
| No live smoke in pytest | Intentional; live smoke must be manual/explicit | Future evidence gate |
| `max_output_chars` is local acceptance cap, not provider token cap | Documented | Future provider token budget gate |
| Provider runtime exceptions surface as `llm_exception` unless Service mapping accepted | 4D2 controller accepted current behavior | Future polish gate |
| `_llm_incomplete_message()` duck typing | Non-blocking; compatible with real result and test doubles | — |

---

## Decision

**PASS**

Gate 4 Slice 4D provider construction 整体通过 aggregate review。所有 8 个 lens 均通过，无 blocking finding。3 个 non-blocking residual 已由先前 4D1/4D2 controller 接受。实现满足 plan 和 controller amendments 的所有要求。

建议下一步：关闭 Gate 4 Slice 4D，进入 Route C Gate 5 planning 或其他后续 gate。
