# MVP Gate 4 Slice 4D1 typed LLM config and provider factory implementation review — MiMo

日期：2026-05-30
角色：implementation review worker
Review target：`fund_agent/config/llm.py`、`fund_agent/services/llm_provider.py`、`fund_agent/services/__init__.py`、`tests/config/test_llm_config.py`、`tests/services/test_llm_provider.py`、`tests/README.md`
Gate：`MVP Gate 4 Slice 4D1: typed LLM config and provider factory implementation gate`
分类：`heavy`

## Verdict

**PASS_WITH_NON_BLOCKING**

实现严格遵循 4D plan 和 controller amendments A1-A8。env contract 是 typed、fail-closed 的，无默认 vendor/model/base_url；空白 API key 视为 missing；secret 不会出现在 repr/error/log。provider 仅使用 openai_compatible HTTP chat-completions 和现有 httpx；无新增 vendor SDK/dependency；无 live network tests。审计 adapter 没有重建或弱化 Gate 2 的 SEVERITY|LOCATION|MESSAGE 协议。没有触碰 CLI wiring、Fund/Service analyze/orchestrator runtime、Host/dayu、extra_payload、golden/readiness、score/quality gate。测试覆盖主要 failure path 和安全边界。有 2 个 non-blocking findings 和若干 residual risk。

---

## Non-blocking Findings

### N1. `_audit_user_prompt()` 协议唯一性断言可加强

**文件**：`tests/services/test_llm_provider.py:73`

**现状**：测试断言 `user_message.count("SEVERITY|LOCATION|MESSAGE") == 1`，验证协议文本在 provider user message 中恰好出现一次。

**分析**：当前实现中该文本来自 `request.user_prompt`（Gate 2 冻结的审计协议真源），adapter 没有重复构造。断言已充分证明协议没有被额外重复。但可以进一步断言 `request.user_prompt` 本身恰好包含一次协议文本，作为 adapter 行为的前置不变量。

**Why non-blocking**：当前断言已验证 adapter 不重复构造协议文本；加强断言属于防御性改进，不改变实现正确性。

**建议**：可选——在 `_audit_user_prompt()` 或其测试中增加 `assert request.user_prompt.count("SEVERITY|LOCATION|MESSAGE") == 1` 前置断言。

### N2. `build_chapter_llm_clients()` 的 `except Exception` catch 范围较宽

**文件**：`fund_agent/services/llm_provider.py:210-215`

**现状**：

```python
try:
    client = OpenAICompatibleChapterLLMClient(config=config)
except LLMProviderConstructionError:
    raise
except Exception as exc:
    raise LLMProviderConstructionError("failed to construct LLM provider client") from exc
```

**分析**：`LLMProviderConstructionError` 已被显式 re-raise。外层 `except Exception` 捕获所有非 `LLMProviderConstructionError` 异常并包装为 `LLMProviderConstructionError`。当前 `OpenAICompatibleChapterLLMClient.__init__()` 内部只在 `provider_name != "openai_compatible"` 时抛出 `LLMProviderConstructionError`，其余逻辑（`_chat_completions_url()`、`httpx.Client()` 构造）理论上不应抛出其他异常。外层 catch 作为防御性兜底是合理的，但包装消息 `"failed to construct LLM provider client"` 丢失了原始异常类型信息。

**Why non-blocking**：当前 `__init__()` 的实际执行路径不太可能触发非 `LLMProviderConstructionError` 异常；`from exc` 保留了 exception chain，用户仍可从 `__cause__` 获取原始异常。这是防御性编码风格问题，不是功能缺陷。

**建议**：可选——将 catch 消息改为 `f"failed to construct LLM provider client: {exc}"` 以在顶层消息中包含原始异常摘要。

---

## Blocking Findings

**无。**

---

## 逐 Lens 审查

### Lens 1: 是否严格实现 4D plan 和 controller amendments A1-A8

| Amendment | 实现状态 | 证据 |
|-----------|---------|------|
| A1 Provider Choice Signed Off | ✅ | `LLMProviderName = Literal["openai_compatible"]`；无默认 model/base_url/key；`_SUPPORTED_PROVIDER_NAME` 常量单一值 |
| A2 Audit Prompt Boundary | ✅ | `_audit_user_prompt()` 首段完整保留 `request.user_prompt`（Gate 2 冻结协议真源），附加 draft/ids/focus 但不重复构造 SEVERITY\|LOCATION\|MESSAGE 协议；`test_audit_chapter_uses_existing_user_prompt_protocol_and_maps_raw_text` 断言协议文本恰好出现 1 次 |
| A3 `ChapterOrchestrationPolicy.max_output_chars` Confirmed | ✅ | plan 说明无需 pre-work；4D1 不触碰 orchestrator；`config.max_output_chars` 可在 4D2 传入 |
| A4 API Key Empty String Is Missing | ✅ | `_load_api_key()` L152-154：`if api_key is None or not api_key.strip()` → raise；`test_load_llm_provider_config_empty_api_key_fails` 覆盖 `""` 和 `"   "` |
| A5 CLI Temporary Unavailable Error Removal | ✅ | 4D1 不触碰 CLI；4D2 负责删除 |
| A6 Config Import Path | ✅ | `config/__init__.py` 未被修改（`git diff` 确认无 tracked change）；`llm_provider.py` 使用 `from fund_agent.config.llm import LLMProviderConfig` 直接导入 |
| A7 Runtime Error Detail | ✅ | `_safe_http_error_message()` 只包含 status_code 和 request_id；`_request_id()` 只读 `x-request-id`/`x-correlation-id`/`request-id`；测试断言错误消息不包含 key/prompt/body |
| A8 Design/Control Timing | ✅ | 4D1 未修改 `docs/design.md`、`docs/current-startup-packet.md`、`docs/implementation-control.md` |

### Lens 2: env contract 是否 typed、fail-closed，无默认 vendor/model/base_url；空白 API key 视为 missing；secret 不出现在 repr/error/body/log

**结论：完全合规。**

| 要求 | 验证 |
|------|------|
| Typed config | `LLMProviderConfig` frozen dataclass with `kw_only=True, slots=True` |
| Fail-closed | 所有 required 字段缺失 → `LLMProviderConfigError`；provider 不支持 → `LLMProviderConfigError` |
| 无默认 vendor/model/base_url | `_ENV_PROVIDER`/`_ENV_MODEL`/`_ENV_BASE_URL` 全部通过 `_required_non_empty()` 读取，无 default |
| 空白 API key 视为 missing | `_load_api_key()` L152-154：`None` 或 `not strip()` → raise |
| Secret 不在 repr | `api_key: str = field(repr=False)`；`test_..._hides_api_key` 断言 `"secret-value" not in repr(config)` |
| Secret 不在 error | `test_..._missing_required_values_fail` 断言 `"secret-value" not in str(exc_info.value)`；error 只命名 env var name |
| Secret 不在 body/header 泄漏 | `_chat_payload()` 只含 model/messages；Authorization header 在 HTTP request 中（必须），但错误消息/日志不含 key |
| `environ: Mapping[str, str] \| None` 参数 | ✅ 支持显式 dict 注入，测试不 monkeypatch `os.environ` |

### Lens 3: provider 是否仅使用 openai_compatible HTTP chat-completions 和现有 httpx；无新增 vendor SDK/dependency；无 live network tests

**结论：完全合规。**

| 要求 | 验证 |
|------|------|
| 仅用 openai_compatible HTTP | `_complete()` 通过 `httpx.Client.post()` 发送 chat completions 请求 |
| 仅用现有 httpx | `pyproject.toml` 已有 `httpx>=0.28.0`；未修改 `pyproject.toml` |
| 无新增 vendor SDK | `grep` 确认无 `import anthropic/openai/...`；无新 dependency |
| 无 live network tests | 所有 provider tests 使用 `httpx.MockTransport`；config tests 使用 fake env dict |
| HTTP body shape | 只含 `model` 和 `messages`（system + user）；无 stream/tools/function_call |

### Lens 4: URL/payload/header/response parsing 是否稳健；rate limit、HTTP error、timeout/network、malformed response 分类正确且安全

**结论：完全合规。**

| 场景 | 实现 | 测试覆盖 |
|------|------|---------|
| URL 组装 | `_chat_completions_url()` 处理 `/v1` suffix、已有 `/chat/completions`、无 suffix 三种情况；`base_url.rstrip("/")` | `test_generate_chapter_...` 验证完整 URL |
| Authorization header | `Bearer {api_key}` | `test_generate_chapter_...` 断言 `Authorization` header |
| JSON body | 只含 `model` + `messages` | `test_generate_chapter_...` 断言完整 body |
| 429 rate limit | `LLMProviderRateLimitError`；安全消息含 status_code + request_id | `test_rate_limit_...` |
| 4xx/5xx | `LLMProviderRuntimeError`；安全消息不含 body | `test_http_error_...` 覆盖 400/500/503 |
| Timeout | `LLMProviderRuntimeError("LLM provider request timed out")`；不含 prompt/key | `test_timeout_...` |
| Network/DNS | `LLMProviderRuntimeError("LLM provider network error")`；不含 prompt/key | `test_network_error_...` |
| Invalid JSON | `LLMProviderMalformedResponseError` | `test_malformed_response_...` 覆盖空/None/非字符串 |
| Missing choices | `LLMProviderMalformedResponseError` | `test_malformed_response_...` 覆盖 6 种 malformed shape |
| Request-id 提取 | `_request_id()` 检查 3 种 header name；缺失返回 None | 多个测试验证 `request_id=req-123` |

### Lens 5: audit adapter 是否没有重建或弱化 Gate 2 的 SEVERITY|LOCATION|MESSAGE 协议；是否只把 ChapterAuditLLMRequest 安全打包给 provider

**结论：完全合规。**

| 要求 | 验证 |
|------|------|
| 不重建/弱化协议 | `_audit_user_prompt()` 首段完整保留 `request.user_prompt`（Gate 2 冻结协议），不修改其内容 |
| 不重复构造协议文本 | `test_audit_chapter_...` 断言 `user_message.count("SEVERITY|LOCATION|MESSAGE") == 1` |
| 安全打包 | 附加 `draft_markdown`、`allowed_fact_ids`、`allowed_anchor_ids`、`audit_focus` 作为上下文 |
| 不读取 PDF/外部 facts | `_audit_user_prompt()` 只消费 `request` 字段，无 IO |
| `ChapterAuditLLMRequest` 字段匹配 | 实际字段（L136-161）：`system_prompt`/`user_prompt`/`draft_markdown`/`allowed_fact_ids`/`allowed_anchor_ids`/`audit_focus` — 与 adapter 使用的字段完全一致 |

### Lens 6: 是否没有触碰 CLI wiring、Fund/Service analyze/orchestrator runtime path、Host/dayu、extra_payload、golden/readiness、score/quality gate

**结论：完全合规。**

| 边界 | 验证 |
|------|------|
| CLI wiring | 未修改 `fund_agent/ui/cli.py`；`git status` 确认无 tracked change |
| Fund writer/auditor | 未修改 `fund_agent/fund/chapter_writer.py` 或 `chapter_auditor.py` |
| Service analyze/orchestrator | 未修改 `fund_analysis_service.py` 或 `chapter_orchestrator.py` |
| Host/dayu | `grep` 确认无 `import host/dayu/agent` in 4D1 files |
| extra_payload | `grep` 确认无 `extra_payload` usage |
| golden/readiness/score/quality gate | 未修改相关文件 |
| `config/__init__.py` | 未修改（A6 compliance） |
| `pyproject.toml` | 未修改 |

### Lens 7: tests 是否覆盖主要 failure path 和安全边界；是否存在未覆盖但应 blocker 的风险

**结论：覆盖充分，无 blocker 缺口。**

**Config tests（22 cases）**：
- ✅ 正常构造 + repr 隐藏 key
- ✅ 4 个 required 字段逐一缺失
- ✅ unsupported provider
- ✅ 4 种非法 base_url（ftp/relative/query/fragment）
- ✅ 4 种 timeout 边界（0/-1/301/NaN）
- ✅ 5 种 max_output_chars 边界（0/-1/50001/float/NaN）
- ✅ API key 空字符串 + 纯空白
- ✅ 自定义 API key env var + timeout + max_output

**Provider tests（15 cases）**：
- ✅ factory 返回同一 adapter
- ✅ writer 请求 header/body + response 映射
- ✅ auditor 请求透传协议 + raw_text 映射
- ✅ 429 → typed rate limit error（安全消息）
- ✅ 400/500/503 → runtime error（安全消息）
- ✅ network error → runtime error（安全消息）
- ✅ timeout → runtime error（安全消息）
- ✅ 6 种 malformed response shape

**未覆盖但非 blocker 的场景**：
- `base_url` 末尾带 `/v1/` 多余斜杠的 edge case — `_chat_completions_url()` 的 `rstrip("/")` 处理了此情况，但无显式测试
- `build_chapter_llm_clients()` 传入非 `openai_compatible` provider 的 `LLMProviderConstructionError` 路径 — 由 config 层先拦截，但 factory 测试未直接覆盖

---

## Validation Reviewed

| 命令 | 结果 |
|------|------|
| `uv run ruff check fund_agent/config/llm.py fund_agent/services/llm_provider.py fund_agent/services/__init__.py tests/config/test_llm_config.py tests/services/test_llm_provider.py` | All checks passed! |
| `uv run pytest tests/config/test_llm_config.py tests/services/test_llm_provider.py -v` | 37 passed in 0.75s |
| `uv run pytest tests/services/test_fund_analysis_service_llm.py tests/services/test_chapter_orchestrator.py tests/fund/test_chapter_writer.py tests/fund/test_chapter_auditor.py -q` | 75 passed in 0.47s |
| `git diff --stat HEAD` | Only `fund_agent/services/__init__.py` (re-export) and `tests/README.md` (doc update) as tracked changes |
| `git status fund_agent/config/llm.py fund_agent/services/llm_provider.py` | Both `??` (untracked new files) |
| `git diff fund_agent/config/__init__.py` | No change (A6 compliance) |
| `grep host/dayu/agent in 4D1 files` | None found |
| `grep extra_payload in 4D1 files` | None found |
| `fund_agent.config` dir() | No LLM types re-exported |

## Scope Check

| 检查项 | 结果 |
|--------|------|
| 未修改 CLI wiring | ✅ `cli.py` 无 tracked change |
| 未修改 Fund writer/auditor | ✅ |
| 未修改 Service analyze/orchestrator | ✅ |
| 未修改 config/__init__.py | ✅ A6 compliance |
| 未修改 pyproject.toml | ✅ |
| 未修改 design.md / startup-packet / implementation-control | ✅ A8 compliance |
| 未修改 golden/score/quality/final judgment | ✅ |
| 未创建 host/agent 包 | ✅ |
| 未引入 dayu 依赖 | ✅ |
| 未引入 vendor SDK | ✅ |
| 未做 live network tests | ✅ all MockTransport/fake env |
| 未做 deterministic fallback | ✅ |
| 未通过 extra_payload 传递参数 | ✅ |
| Service __init__.py 只新增 provider public API re-export | ✅ |
| tests/README.md 只新增 4D1 测试描述 | ✅ |

## Residual Risks

| Risk | Disposition |
|------|------------|
| 单一 adapter 同时用于 writer/auditor | Controller-accepted MVP simplification（plan §15）；未来分模型需独立 gate |
| 无 retry/backoff | Accepted MVP fail-closed；retry policy 是 future reliability gate |
| 无 live provider smoke | Intentional；live smoke 必须是后续显式授权 gate |
| `max_output_chars` 是本地字符上限不是 provider token cap | Plan §7 已文档化 |
| 4D2 将修改 CLI `_build_llm_clients_or_fail()` 签名并删除 `LLMProviderUnavailableError` | Plan §10 + controller amendment A5 已明确；本 slice 不涉及 |
