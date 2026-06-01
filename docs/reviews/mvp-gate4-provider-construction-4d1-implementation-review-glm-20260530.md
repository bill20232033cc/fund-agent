# MVP Gate 4 Slice 4D1 Implementation Review (GLM)

日期：2026-05-30
角色：review worker (GLM)
Review target：`fund_agent/config/llm.py`, `fund_agent/services/llm_provider.py`, `fund_agent/services/__init__.py`, `tests/config/test_llm_config.py`, `tests/services/test_llm_provider.py`, `tests/README.md`
Gate：`MVP Gate 4 Slice 4D1: typed LLM config and provider factory implementation gate`
分类：`heavy`

## Verdict

**PASS**

实现严格遵循 4D plan 和 controller amendments A1-A8，无阻断发现。以下是逐 lens 验证结果。

---

## Blocking Findings

**无。**

---

## Controller Amendments A1-A8 Compliance

### A1. Provider Choice Signed Off ✓

- `LLMProviderName = Literal["openai_compatible"]`，硬编码唯一受支持值。
- Config loader 在 `_load_provider_name()` 中校验 `value != "openai_compatible"` 即抛 `LLMProviderConfigError`。
- 无默认 model、base_url、vendor 或 fallback provider。
- Provider adapter 构造函数再次校验 `config.provider_name != "openai_compatible"` 抛 `LLMProviderConstructionError`。
- 测试覆盖 unsupported provider 拒绝路径（`test_load_llm_provider_config_unsupported_provider_fails`）。

### A2. Audit Prompt Boundary ✓

- `_audit_user_prompt()`（`llm_provider.py:264-287`）首段完整保留 `request.user_prompt`，随后附加 `draft_markdown`、`allowed_fact_ids`、`allowed_anchor_ids`、`audit_focus`。
- 不重复构造 `SEVERITY|LOCATION|MESSAGE` 协议。
- 测试 `test_audit_chapter_uses_existing_user_prompt_protocol_and_maps_raw_text()` 显式断言 `user_message.count("SEVERITY|LOCATION|MESSAGE") == 1`，证明协议只出现一次且来自 `request.user_prompt`。
- 与 `ChapterAuditLLMRequest` 实际字段完全一致：`user_prompt`、`draft_markdown`、`allowed_fact_ids`（`tuple[str, ...]`）、`allowed_anchor_ids`（`tuple[str, ...]`）、`audit_focus`（`tuple[str, ...]`）全部被消费，`system_prompt` 通过 `_complete(system_prompt=request.system_prompt, ...)` 单独传递。

### A3. `ChapterOrchestrationPolicy.max_output_chars` Confirmed ✓

- `ChapterOrchestrationPolicy` 已有 `max_output_chars: int = 12000`（`chapter_orchestrator.py:112`）。
- `LLMProviderConfig` 默认值同为 12000（`llm.py:20`），4D2 可直接传递 `config.max_output_chars`。
- 无需修改 orchestrator。

### A4. API Key Empty String Is Missing ✓

- `_load_api_key()`（`llm.py:138-155`）：`api_key is None or not api_key.strip()` 时抛 `LLMProviderConfigError(f"missing API key value in {api_key_env_var}")`。
- 空字符串 `""` 和纯空白 `"   "` 均视为缺失。
- 测试 `test_load_llm_provider_config_empty_api_key_fails` 覆盖两种边界。
- 错误消息只命名 env var，不打印 key 值。

### A5. CLI Temporary Unavailable Error Removal — Deferred to 4D2 ✓

- 本 slice 未修改 `fund_agent/ui/cli.py`，未触碰 `LLMProviderUnavailableError`。
- 符合 4D1 scope：CLI wiring 是 4D2 的职责。

### A6. Config Import Path ✓

- `fund_agent/config/__init__.py` 未修改（git diff 无输出），新 config 类型不 re-export。
- 导入路径 `fund_agent.config.llm` 与现有 `fund_agent.config.paths` 直接导入风格一致。
- Provider adapter 使用 `from fund_agent.config.llm import LLMProviderConfig`。
- 测试使用 `from fund_agent.config.llm import LLMProviderConfigError, load_llm_provider_config_from_env`。

### A7. Runtime Error Detail ✓

- `_safe_http_error_message()`（`llm_provider.py:327-344`）只包含 `status_code` 和可选 `request_id`。
- 读取 `_REQUEST_ID_HEADERS = ("x-request-id", "x-correlation-id", "request-id")`。
- 不包含 API key、Authorization header、prompt body、full response body。
- 测试逐一验证：429/error/network/timeout/malformed 路径的错误文本不包含 `test-secret`、`writer user`、`full error body` 或 `provider body`。

### A8. Design/Control Timing ✓

- 本 slice 未修改 `docs/design.md`、`docs/current-startup-packet.md` 或 `docs/implementation-control.md`。
- Implementation evidence 明确标注 "未 commit、未 push、未 PR、未 merge、未 release"。

---

## Review Lens Verification

### Lens 1: 严格实现 4D Plan 和 Controller Amendments

**通过。** 逐条验证见上方 A1-A8。

额外验证 plan §7 env contract 表与实际实现对照：

| Env var | Plan Required | Implementation | 验证 |
|---|---|---|---|
| `FUND_AGENT_LLM_PROVIDER` | yes | `_required_non_empty(env, _ENV_PROVIDER)` + 值校验 | ✓ |
| `FUND_AGENT_LLM_MODEL` | yes | `_required_non_empty(env, _ENV_MODEL)` | ✓ |
| `FUND_AGENT_LLM_BASE_URL` | yes | `_load_base_url(env)` 校验 scheme/host/query/fragment | ✓ |
| `FUND_AGENT_LLM_API_KEY_ENV_VAR` | no, default `FUND_AGENT_LLM_API_KEY` | `_optional_non_empty(env, _ENV_API_KEY_ENV_VAR, _DEFAULT_API_KEY_ENV_VAR)` | ✓ |
| api_key value | yes, non-empty | `_load_api_key()` strip 校验 | ✓ |
| `FUND_AGENT_LLM_TIMEOUT_SECONDS` | no, default 60 | `_load_timeout_seconds()` range (0, 300] | ✓ |
| `FUND_AGENT_LLM_MAX_OUTPUT_CHARS` | no, default 12000 | `_load_max_output_chars()` range (0, 50000] | ✓ |

### Lens 2: Env Contract — typed, fail-closed, no default vendor/model/base_url, empty key = missing, secret not in repr/error/body/log

**通过。**

- `LLMProviderConfig` 是 `frozen=True, slots=True, kw_only=True` dataclass。
- `api_key: str = field(repr=False)` — repr 不泄漏。
- `_load_provider_name`、`_required_non_empty`、`_load_base_url`、`_load_api_key` 均在值缺失/非法时抛 `LLMProviderConfigError`。
- 无任何默认 model/base_url/vendor。
- 测试 `test_load_llm_provider_config_success_and_hides_api_key()` 断言 `"secret-value" not in repr(config)`。
- 测试 `test_load_llm_provider_config_missing_required_values_fail()` 断言 `"secret-value" not in str(exc_info.value)`。

### Lens 3: Provider — openai_compatible HTTP chat-completions + existing httpx, no new SDK, no live network tests

**通过。**

- `OpenAICompatibleChapterLLMClient` 只使用 `httpx.Client.post()`。
- Request body 构造在 `_chat_payload()`：`{"model": ..., "messages": [...]}`。
- Response 解析在 `_extract_text()`：要求 `choices[0].message.content` 为 string。
- 无 vendor SDK import。
- `pyproject.toml` 未修改。
- 测试使用 `httpx.Client(transport=httpx.MockTransport(handler))`。

### Lens 4: URL/payload/header/response parsing robustness, error classification

**通过。**

URL 构造：
- `_chat_completions_url()` 处理三种输入：已含 `/chat/completions` 后缀、`/v1` 后缀、其他。base_url 的 scheme/host/query/fragment 由 config 层先行校验。

HTTP 错误分类：

| 场景 | 代码位置 | 异常类型 | 验证 |
|---|---|---|---|
| 429 rate limit | `:183-184` | `LLMProviderRateLimitError` | ✓ 测试覆盖 |
| 非 2xx | `:185-186` | `LLMProviderRuntimeError` | ✓ 400/500/503 参数化测试 |
| timeout | `:178-179` | `LLMProviderRuntimeError` | ✓ 专用测试 |
| transport/network | `:180-181` | `LLMProviderRuntimeError` | ✓ 专用测试 |
| invalid JSON | `:188-191` | `LLMProviderMalformedResponseError` | ✓ 专用测试 |
| response not object | `:192-193` | `LLMProviderMalformedResponseError` | ✓ `{}` payload 测试 |
| missing choices | `:303-305` | `LLMProviderMalformedResponseError` | ✓ `{"choices": []}` 测试 |
| message not object | `:309-310` | `LLMProviderMalformedResponseError` | ✓ `{"choices": [None]}` 测试 |
| content not string | `:311-316` | `LLMProviderMalformedResponseError` | ✓ None/123 参数化测试 |

所有错误消息不包含 API key、prompt 或完整 response body。

### Lens 5: Audit adapter — 不重建/弱化 Gate 2 SEVERITY|LOCATION|MESSAGE 协议

**通过。**

- `_audit_user_prompt()` 把 `request.user_prompt` 完整放在 user message 首段，不修改。
- 额外附加 `draft_markdown`、`allowed_fact_ids`、`allowed_anchor_ids`、`audit_focus`，这些是 `ChapterAuditLLMRequest` 的显式字段，为 provider 审计提供上下文但不改变审计协议。
- 测试断言 `SEVERITY|LOCATION|MESSAGE` 出现恰好一次。
- `system_prompt` 通过 `_complete(system_prompt=request.system_prompt, ...)` 独立传递，不做任何修改。

### Lens 6: 未触碰 CLI wiring、Fund analyze/orchestrator runtime、Host/dayu、extra_payload、golden/readiness、score/quality gate

**通过。** Scope 检查：

| 文件/模块 | 是否触碰 | 预期 |
|---|---|---|
| `fund_agent/ui/cli.py` | 否 | 4D2 scope ✓ |
| `fund_agent/fund/**` | 否 | ✓ |
| `fund_agent/services/fund_analysis_service.py` | 否 | ✓ |
| `fund_agent/services/chapter_orchestrator.py` | 否 | ✓ |
| `fund_agent/config/__init__.py` | 否 | A6 ✓ |
| `pyproject.toml` | 否 | ✓ |
| `docs/design.md` | 否 | A8 ✓ |
| `docs/current-startup-packet.md` | 否 | A8 ✓ |
| `docs/implementation-control.md` | 否 | A8 ✓ |

- Provider/model/base_url/key/timeout/max_output_chars 均为 typed config 字段，无 extra_payload。
- 无 Host/Agent/dayu 引用。

### Lens 7: Tests 覆盖主要 failure path 和安全边界

**通过。**

Config tests（`test_llm_config.py`）：7 个测试函数，覆盖：
- 完整 env 成功构造 + repr 不泄漏 key
- 4 个必填字段缺失 fail-closed（参数化）
- unsupported provider 拒绝
- 4 种非法 base_url（参数化）
- 4 种非法 timeout（参数化）
- 5 种非法 max_output_chars（参数化）
- 空白 API key 视为缺失（2 个参数化值）
- 自定义 API key env var + 非 int timeout/max_output 正常解析

Provider tests（`test_llm_provider.py`）：10 个测试函数，覆盖：
- factory 返回同一 adapter 实例
- writer Authorization header + JSON body 映射
- auditor user_prompt 协议透传 + raw_text 映射
- 429 rate limit typed error + 安全消息
- 400/500/503 HTTP error（参数化） + 安全消息
- network error + 安全消息
- timeout error + 安全消息
- 6 种 malformed response（参数化）+ 安全消息

总计 37 个测试，全部通过（evidence 记录 `37 passed in 0.61s`）。

未覆盖但风险可控的路径：

| 路径 | 风险评估 |
|---|---|
| `build_chapter_llm_clients` 意外异常包装 | 防御性代码；构造函数失败已由 `LLMProviderConstructionError` 覆盖 |
| `_chat_completions_url` 直接测试 | 间接通过 provider 请求 URL 验证 |
| provider 返回空字符串 content | `_extract_text` 允许 `isinstance(content, str)` 通过空串；Fund writer 的 `llm_empty_response` 合约处理此情况 |

---

## Non-blocking Findings / Residual Risk

### N1. `OpenAICompatibleChapterLLMClient` 在 `__all__` 中导出

`fund_agent/services/__init__.py` 将 `OpenAICompatibleChapterLLMClient` 加入 `__all__`。CLI 4D2 只需 `build_chapter_llm_clients()` 返回的 `ChapterOrchestratorLLMClients`，不需要具体类。导出具体类的好处是测试可直接构造，且未来扩展时不需要改 `__init__.py`。当前导出合理但非必需。

### N2. `_chat_completions_url` 间接测试

URL 构造的三种分支通过 provider 请求 URL 断言间接覆盖。如后续 URL 构造逻辑变复杂，建议补充直接单元测试。

### N3. 无 retry/backoff

Controller accepted residual。`LLMProviderRuntimeError` 和 `LLMProviderRateLimitError` 均为 fail-closed。未来 retry policy 需独立 gate。

### N4. 单一模型 writer/auditor

Controller accepted MVP simplification。`LLMProviderConfig` 的 `model: str` 单字段设计不阻碍未来拆分 `writer_model` / `auditor_model`。

### N5. 无 live provider smoke

Intentional。CI 只运行 MockTransport 测试。真实 endpoint 验证需手工或独立授权 gate。

---

## Validation Reviewed

以下核验基于读取代码和 implementation evidence 中的命令结果，未重新执行命令：

| 验证项 | 结果 |
|---|---|
| `ruff check` 新文件 | evidence: `All checks passed!` ✓ |
| `ruff check .` 全量 | evidence: `All checks passed!` ✓ |
| 新测试 `37 passed` | evidence: `37 passed in 0.61s` ✓ |
| 已有 writer/auditor/orchestrator 测试 `75 passed` | evidence: `75 passed in 0.54s` ✓ |
| 全量 `--cov-fail-under=50` | evidence: `1101 passed, Total coverage: 91.75%` ✓ |
| `git diff --check` | evidence: 无输出 ✓ |
| `git status --short` | evidence: 无 tracked dirty；新文件均为 untracked ✓ |
| `config/__init__.py` 未修改 | `git diff HEAD` 无输出 ✓ |

---

## Scope Check

**未发现越界项。** 具体确认：

- ✅ 只新增 `fund_agent/config/llm.py`、`fund_agent/services/llm_provider.py` 和对应测试
- ✅ `fund_agent/services/__init__.py` 只增加 provider 相关 import/export
- ✅ `tests/README.md` 只追加 4D1 测试说明和运行命令
- ✅ 未修改 CLI、Fund、orchestrator、config `__init__`、pyproject、design/control/startup 文档
- ✅ 未引入 Host/Agent/dayu、vendor SDK、live network、golden/score/snapshot/quality/final judgment/promotion

---

## Summary

Slice 4D1 实现严格对齐 4D plan 和 controller amendments A1-A8。typed env config 是 frozen dataclass，fail-closed 且无默认 vendor/model/base_url。provider adapter 使用现有 httpx 发送 OpenAI-compatible chat completions，response 解析保守，error 分类完整且安全。audit adapter 透传 Gate 2 审计协议不重建。测试覆盖配置校验、Protocol 映射和所有 runtime error path，使用 MockTransport 无 live network。无阻断发现。
