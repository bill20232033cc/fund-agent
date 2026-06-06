# MVP Provider Endpoint/Path Diagnostic Gate — Plan Review (AgentDS, Revised)

## 1. Review Metadata

- Role: AgentDS
- Focus: same-source path logic, outcome taxonomy, Gate1/Gate2/Gate3 gating clarity, Chapter calibration blocked, residual owner routing, dirty workspace isolation
- Verdict format: `PASS`, `PASS_WITH_NON_BLOCKING_OBSERVATIONS`, or `BLOCKED_WITH_REQUIRED_FIXES`
- Reviewed artifact: `docs/reviews/mvp-provider-endpoint-path-diagnostic-gate-plan-20260606.md` (revised)
- Revision note: 本 review 针对修订版 plan。修订版将原 Check A/Check B 重构为 Gate 2 (local-only evidence) / Gate 3 (same-process adapter minimal check)，Gate 1 现在只允许 plan/review/controller judgment，不执行任何 evidence 或 control sync。

---

## 2. Verdict

**PASS**

---

## 3. Same-Source Path Logic

### 3.1 Config 加载路径

Plan §5 使用 `load_llm_provider_config_from_env()` — 对应 `fund_agent/config/llm.py:79`，是生产代码中唯一的 typed config 构造入口。

`_load_base_url()` (llm.py:171-177) 已做 `scheme ∈ {http,https}` 校验、禁止 query/fragment、`rstrip("/")`。`load_llm_provider_config_from_env()` 返回的 `LLMProviderConfig.base_url` 已经是 stripped 形式。

**验证通过。** Gate 2 消费的 config 与生产路径中的 `build_chapter_llm_clients()` → `OpenAICompatibleChapterLLMClient(config=config)` 使用完全相同的 `LLMProviderConfig` 对象。✓

### 3.2 URL Derivation 逻辑

Plan §5 描述的 URL derivation:

- base URL ending `/chat/completions` → 保持不变
- base URL ending `/v1` → 追加 `/chat/completions`
- otherwise → 追加 `/v1/chat/completions`

与 `fund_agent/services/llm_provider.py:444-462` `_chat_completions_url()` 逐行一致:

```python
normalized = base_url.rstrip("/")
if normalized.endswith("/chat/completions"):
    return normalized
if normalized.endswith("/v1"):
    return f"{normalized}/chat/completions"
return f"{normalized}/v1/chat/completions"
```

注意 double-strip: `_load_base_url()` 已做 `rstrip("/")`（llm.py:177），`_chat_completions_url()` 再做 `rstrip("/")`（llm_provider.py:457）。Gate 2 使用 `load_llm_provider_config_from_env()` 返回的 config 后自动继承此行为。

**验证通过。** ✓

### 3.3 Gate 3 Adapter 调用

Plan §6 使用 `OpenAICompatibleChapterLLMClient.generate_chapter()` — 对应 `fund_agent/services/llm_provider.py:167`，是生产 adapter 的同一公开方法。

构造路径: `OpenAICompatibleChapterLLMClient(config=config)` → `self._url = _chat_completions_url(config.base_url)` → `self._http_client = httpx.Client(timeout=config.timeout_seconds)` → `generate_chapter()` → `_complete()` → `http_client.post(self._url, ...)`

与生产路径 `build_chapter_llm_clients()` → `OpenAICompatibleChapterLLMClient(config=config)` 完全一致。

**验证通过。** ✓

### 3.4 小结

Same-source 链条完整: `load_llm_provider_config_from_env()` → `LLMProviderConfig` → `_chat_completions_url(base_url)` → `OpenAICompatibleChapterLLMClient` → `generate_chapter()` → `_complete()` → `httpx.Client.post(url, ...)`

三个环节均直接复用生产代码，零重新实现。无 blocking finding。

---

## 4. Outcome Taxonomy

### 4.1 Gate 2 Outcomes

| Outcome | 触发条件 | Owner |
|---------|---------|-------|
| `local_config_path_blocked` | `load_llm_provider_config_from_env()` 抛出 `LLMProviderConfigError` | operator/environment |
| `repo_adapter_path_mismatch` | config 有效但 derived path suffix 为 `unexpected` | repo controller → implementation gate |
| (internal consistency, insufficient) | config/path 一致但不足以解释 prior `ConnectError` | → request Gate 3 controller judgment |

### 4.2 Gate 3 Outcomes

| Outcome | 对应代码异常 |
|---------|------------|
| `minimal_adapter_success` | `_complete()` 正常返回 `LLMProviderResponse` |
| `provider_runtime_error_non_timeout` | `LLMProviderNetworkError` (含 `httpx.TransportError` / `ConnectError`) |
| `provider_runtime_timeout` | `LLMProviderTimeoutError` (含 `httpx.TimeoutException`) |
| `provider_http_error` | `LLMProviderRuntimeError` (non-2xx, non-429) |
| `provider_rate_limited` | `LLMProviderRateLimitError` (429) |
| `provider_malformed_response` | `LLMProviderMalformedResponseError` (JSON parse / schema) |

### 4.3 评估

Gate 3 的 6 个 outcomes 与 `llm_provider.py:218-419` `_complete()` 方法的所有异常分支一一对应。Gate 2 的 3 个 outcomes 覆盖了配置加载的全部可能结果。

`provider_runtime_error_non_timeout` outcome 直接保留了当前 active residual 的名称，确保 Gate 3 的 outcome 可以直接与 `implementation-control.md` 的 residual 对齐，不需要中间翻译层。✓

**唯一的轻微不对齐**: Gate 2 第三个结果 "internally consistent but insufficient" 没有正式的 typed outcome label（`local_config_path_blocked` 和 `repo_adapter_path_mismatch` 有）。这不影响正确性——它是 transition 状态而非 terminal outcome——但 Gate 4 的 disposition 需要引用 Gate 2 结果时，建议有一个明确的 label（如 `local_config_path_consistent`）以便精确引用。这是 cosmetic 问题，不阻塞。

---

## 5. Gate1 / Gate2 / Gate3 Gating Clarity

### 5.1 权限边界矩阵

| 操作 | Gate 1 | Gate 2 | Gate 3 |
|------|--------|--------|--------|
| 读取源码/prior docs | ✓ | ✓ | ✓ |
| 写 plan/review/judgment | ✓ | — | — |
| 加载 config 并输出 redacted evidence | — | ✓ | — |
| 调用 adapter 发起 HTTP | — | — | ✓ |
| 写 evidence artifact | — | ✓ | ✓ |
| 写 control sync | — | — | — (Gate 4+) |

Gate 1 的权限边界在 §4 明确定义: Allowed in Gate 1 只有 "inspect source files and prior safe docs evidence needed to define checks; write only this plan, plan reviews, and controller judgment; record the queued Gate 2-6 sequence and exact stop conditions."

### 5.2 门控触发条件

- **Gate 1 → Gate 2**: §8 "Gate 2 local-only config/path evidence is the next gate if the plan is accepted" — 隐性授权，Gate 1 controller judgment 接受 plan 后自动进入 Gate 2
- **Gate 2 → Gate 3**: §6 "Gate 3 may open only if Gate 2 local-only evidence does not produce a sufficient blocking outcome and the controller explicitly authorizes external state" — 显性授权，需要独立 controller judgment
- **Gate 3 → Gate 4**: §9 "Gate 4 diagnostic disposition gate" — 自然序列

### 5.3 Stop Conditions

Gate 2 有两个 terminal blocking outcomes (`local_config_path_blocked`, `repo_adapter_path_mismatch`)，任一个触发即停止，不进入 Gate 3。Gate 3 的任意 outcome 均终止 diagnostic sequence，进入 Gate 4 disposition。

**验证通过。** 门控序列无歧义，无循环，无跳跃。Gate 3 需要独立 controller 授权的设计防止了 external state 被未经审查地访问。✓

---

## 6. Chapter Calibration Blocked

Plan 在 5 处显式声明 Chapter calibration 阻断:

1. **§2 authoritative inputs**: "Chapter calibration remains blocked because no body chapter has accepted draft/conclusion evidence"
2. **§4 forbidden**: "no Chapter acceptance calibration or same-source chapter evidence claim"
3. **§6 Gate 3 acceptance**: "minimal_adapter_success: ... Chapter calibration still remains blocked until a separate authorized report-generation gate produces accepted same-source draft/conclusion evidence"
4. **§8 controller judgment**: "Chapter calibration remains blocked unless a separate authorized report-generation gate produces same-source accepted draft/conclusion evidence"
5. **§9 Gate 6**: "Chapter acceptance calibration gate. Open only if at least one body chapter has accepted draft/conclusion evidence"

与 `implementation-control.md` line 71 当前事实一致: 所有六章 body chapters 在 writer 操作阶段即失败 (`llm_network_error` / `ConnectError`)，无任何一章有 accepted draft 或 accepted conclusion。

关键设计点: Gate 3 `minimal_adapter_success` 明确不构成 Chapter calibration 证据。这阻止了 "diagnostic ping 成功 → provider 可用 → 可以跑 Chapter calibration" 的错误推论链。✓

---

## 7. Residual Owner Routing

Routing 链:

```
Config 加载失败 → operator/environment
Config 有效 + path 异常 → repo controller → implementation gate
Config/path 一致 + adapter 失败 → 按 typed outcome 分类:
  ├─ provider_runtime_error_non_timeout → operator/provider endpoint-path (保持当前 residual owner)
  ├─ provider_runtime_timeout → typed category, 不推断 root cause
  ├─ provider_http_error → typed category
  ├─ provider_rate_limited → typed category
  └─ provider_malformed_response → typed category
Config/path 一致 + adapter 成功 → residual 仍在 operator/environment, repo 无代码问题
```

与 `implementation-control.md` 的当前 residual owner 一致: "Defer the same-run non-timeout provider runtime residual to the provider runtime operator / environment owner"。

**验证通过。** Operator 问题和 repo 代码问题的 ownership 边界清晰，不交叉。`provider_runtime_error_non_timeout` 保持 operator owner，符合 AGENTS.md "找问题的 root cause 一定要逻辑/数据同源"原则——adapter 的单一异常类型不能作为 DNS/TLS/proxy/account 的 root cause 证据。✓

---

## 8. Dirty Workspace Isolation

Plan 的隔离声明覆盖了全部误操作路径:

| 声明位置 | 内容 |
|---------|------|
| §2 preflight | 识别 dirty `pyproject.toml` + untracked files; "must not be staged, committed, cleaned, deleted, or used to infer this gate outcome" |
| §4 forbidden | "no staging or committing unrelated dirty files" |
| §8 controller judgment | "dirty workspace isolation remains mandatory" |
| §10 validation | `git diff --cached --name-only` 只包含本 gate 的 docs/control artifacts |

**验证通过。** 五个操作维度（read / stage / commit / clean / delete）全部覆盖。✓

---

## 9. Cross-Cutting Checks

### 9.1 Gate Classification

Plan 自分类 `heavy`，rationale: 可能影响 `provider_runtime_error_non_timeout` residual 的 accepted routing。按 AGENTS.md gate 分类规则 "不确定时选择更重一级"，即使有人主张 `standard` 也可成立，`heavy` 是安全选择。不构成问题。✓

### 9.2 Secret-Safety

Gate 2: 只输出 presence/coarse labels；API key env var label 只输出 `default` 或 `explicit_custom`（不输出自定义 env var name）；不输出 full base URL 或 host value。✓

Gate 3: §6 forbidden 列表覆盖 prompt text, raw response body, API key, Authorization header, bearer token, model value, base URL value, full host value, full environment dump。Capture 只记录 safe summary fields。✓

### 9.3 No Retry / No Fallback / No Default Change

§4 forbidden 完整覆盖: no retry command, no curl/DNS/PASS-only probe, no fallback, no provider/default/runtime/budget change。与 `implementation-control.md` 禁止项一致。✓

### 9.4 Adversarial Failure Pass

| 场景 | 防御 |
|------|------|
| Gate 1 阶段试图执行 evidence | §8 显式禁止 "Gate 1 authorizes no diagnostic evidence execution" |
| 跳过 Gate 2 直接跑 Gate 3 | §4/§6/§8 三级声明 Gate 3 需要独立 controller 授权 |
| Gate 2 evidence 被当作 Chapter calibration | §4/§6/§8 多处禁止 |
| 误 stage dirty `pyproject.toml` | §2/§4/§8/§10 四处禁止 |
| Gate 3 success 被解读为 provider ready | §6 显式 block Chapter calibration |
| stdout/stderr 泄露 secret | §6 forbidden 列表 + artifact safe summary only |

无未覆盖的 adversarial path。✓

---

## 10. Summary

修订版 plan 将原 Check A/Check B 正确重构为 Gate1(plan-only) / Gate2(local-only) / Gate3(controlled external) 三层门控。Same-source path logic 完整追溯到 `load_llm_provider_config_from_env()` → `_chat_completions_url()` → `OpenAICompatibleChapterLLMClient.generate_chapter()` 生产调用链。Outcome taxonomy 与 adapter 异常类一一对应。Gate 门控条件明确，Gate 3 的独立 controller 授权机制防止了 external state 的越权访问。Chapter calibration 阻断在 5 处显式声明且条件明确。Residual owner routing 保持 operator 与 repo controller 的 ownership 边界。Dirty workspace isolation 覆盖 read/stage/commit/clean/delete 全路径。

无阻塞性问题。

Verdict: **PASS**
