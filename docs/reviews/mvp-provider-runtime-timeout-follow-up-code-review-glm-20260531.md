# MVP provider runtime timeout follow-up code review (GLM)

日期：2026-05-31

角色：Gateflow review worker（GLM），不是 implementation worker。

审查范围：当前未提交改动中与本 gate 相关的实现文件和测试。

Source of truth：
- `docs/reviews/mvp-provider-runtime-timeout-follow-up-plan-20260531.md`
- `docs/reviews/mvp-provider-runtime-timeout-follow-up-implementation-evidence-20260531.md`

审查文件：
- `fund_agent/services/llm_provider.py`
- `fund_agent/services/chapter_orchestrator.py`
- `fund_agent/ui/cli.py`
- `tests/services/test_llm_provider.py`
- `tests/services/test_chapter_orchestrator.py`
- `tests/ui/test_cli.py`

## Verdict: PASS

实现严格遵守 plan 的六项审查重点，未发现 blocking finding。以下是逐项审查结论和 residual risks。

---

## 1. Provider timeout retry 是否只针对 timeout 且 bounded

**结论：合规。**

- `llm_provider.py:246-277`：retry 循环仅 catch `httpx.TimeoutException`，在 `provider_attempt_index < max_attempts` 时 `continue`，耗尽后 raise `LLMProviderTimeoutError`。
- `llm_provider.py:278-292`：`httpx.TransportError`（非 timeout 的网络错误）立即 raise，不重试。
- `llm_provider.py:294-323`：429 rate limit 和非 2xx HTTP error 也立即 raise，不重试。
- `llm_provider.py:325-376`：malformed response 不重试。
- `max_attempts` 由 `self._config.timeout_max_attempts` 控制，config 层已校验范围 `1..3`。
- 无无限重试、无并发引入、无 retry broadening。

测试覆盖：
- `test_timeout_only_retry_succeeds_on_later_attempt`：验证 timeout retry 在第三次成功。
- `test_timeout_retry_exhausted_carries_provider_diagnostics`：验证三次 timeout 后耗尽。
- `test_http_errors_do_not_retry`：参数化验证 400/429/500 不重试。
- `test_network_error_does_not_retry_and_carries_single_diagnostic`：验证网络错误不重试。
- `test_malformed_response_does_not_retry_and_carries_single_diagnostic`：验证 malformed 不重试。

## 2. Runtime-cost diagnostics 是否只记录安全标量

**结论：合规。**

Provider 层新增的 `_ProviderCostContext` dataclass（`llm_provider.py:48-66`）只包含 6 个整型/可选整型字段：

| 字段 | Writer 来源 | Auditor 来源 |
|------|------------|-------------|
| `system_prompt_chars` | `len(request.system_prompt)` | `len(request.system_prompt)` |
| `user_prompt_chars` | `len(request.user_prompt)` | `len(provider_user_prompt)` |
| `approx_prompt_tokens` | `ceil((system + user) / 4)` | `ceil((system + user) / 4)` |
| `allowed_fact_count` | `None`（writer 无 allowed facts） | `len(request.allowed_fact_ids)` |
| `allowed_anchor_count` | `len(request.required_anchor_ids)` | `len(request.allowed_anchor_ids)` |
| `max_output_chars` | `request.max_output_chars` | `None`（auditor 不适用） |

关键安全点：
- Writer cost context（`_writer_cost_context`，行 473-498）直接从 request 对象读取 `len()`，不存储文本。
- Auditor cost context（`_auditor_cost_context`，行 501-530）使用 `_audit_user_prompt(request)` 返回的 provider-bound 文本计算 `len()`，但不存储该文本。`provider_user_prompt` 局部变量在函数返回后即被 GC。
- `_provider_diagnostic()`（行 587-644）将 cost context 的 6 个标量写入 `ChapterLLMRuntimeDiagnostic`，不写入原始 prompt 文本、draft、response body 或 secret。

不暴露的内容（已验证代码路径中不存在赋值或传递）：
- API key、Authorization、Bearer token
- 完整 system/user prompt 文本
- draft markdown 文本
- provider response body
- raw audit response 文本
- model name（diagnostic 中 `model_name=None`）
- base URL

测试覆盖：
- `test_timeout_retry_exhausted_carries_provider_diagnostics`（行 187-231）：验证 writer timeout diagnostics 携带正确的 prompt char/token 标量，且 negative canary 断言 `Authorization`/`Bearer`/`writer user`/`test-secret` 不在 `repr(diagnostics)` 中。
- `test_auditor_timeout_diagnostic_uses_provider_bound_prompt_cost`（行 234-274）：验证 auditor diagnostics 的 `user_prompt_chars` 基于 provider-bound prompt 长度（大于原始 `request.user_prompt`），且 negative canary 断言 `draft markdown`/`按 SEVERITY|LOCATION|MESSAGE`/`test-secret`/`Authorization`/`Bearer`/`provider body` 不在 diagnostics repr 中。

## 3. Serializer/CLI 是否只输出 allowlisted fields

**结论：合规。**

Service serializer（`chapter_orchestrator.py:653-682`）`serialize_chapter_runtime_diagnostics()`：
- 输出字段通过 `_runtime_diagnostic_payload()`（行 2549-2583）严格 allowlisted：`operation`/`repair_attempt_index`/`provider_attempt_index`/`provider_max_attempts`/`provider_runtime_category`/`chapter_failure_category`/`elapsed_ms`/`status_code`/`request_id`/`finish_reason`/`response_chars`/`error_type`/`system_prompt_chars`/`user_prompt_chars`/`approx_prompt_tokens`/`allowed_fact_count`/`allowed_anchor_count`/`max_output_chars`。
- **刻意不输出 `model_name` 和 `message`**。代码中无任何路径将这两个字段写入 serializer 输出。

CLI stderr（`cli.py:873-901`）`_first_failed_runtime_summary()`：
- 输出 6 个 runtime 标量：`first_failed_runtime_operation`/`first_failed_provider_attempts`/`first_failed_provider_runtime_category`/`first_failed_elapsed_ms_max`/`first_failed_prompt_chars`/`first_failed_approx_prompt_tokens`。
- 所有标量通过 `_runtime_*` helper 函数从 diagnostics 中提取，使用 `getattr` + 类型检查，不直接访问 `message`/`model_name`/原始 prompt。

`_runtime_prompt_chars()`（行 1027-1048）只读取 `system_prompt_chars` 和 `user_prompt_chars` 整型值并求和，不拼接或输出原始文本。

测试覆盖：
- Service serializer test `test_runtime_diagnostic_serialization_exposes_only_safe_scalars`（行 956-1077）：构造含 canary 值 `message` 的 diagnostics（含 `USER_PROMPT_CANARY`/`DRAFT_MARKDOWN_CANARY`/`RAW_RESPONSE_CANARY`/`RAW_AUDIT_RESPONSE_CANARY`/`SYSTEM_PROMPT_CANARY`/`PROVIDER_RESPONSE_CANARY`/`secret-deployment-model`/`Authorization`/`Bearer`/`sk-secret`/`header`/`key` 等），验证序列化后文本不含这些 canary 值，且不含 `model_name`/`message` 字段名。
- CLI test `test_analyze_cli_use_llm_timeout_fail_closed_without_fallback`（行 1541-1598）：验证 stderr 包含 runtime 标量且不含 `message`/`Authorization`/`Bearer`/`sk-`/`header`/`key`/`auditor`/`programmatic`/`raw audit`/`system_prompt`/`user_prompt`/`draft_markdown`/`provider_response`/`provider body`。

## 4. Default deterministic analyze/checklist 行为是否不变

**结论：合规。**

- CLI `analyze` 命令默认 `use_llm=False`（行 169-171），只有显式传 `--use-llm` 才进入 LLM 路径。
- 不传 `--use-llm` 时，`load_llm_provider_config_from_env` 和 `build_chapter_llm_clients` 不会被调用（行 243-253 的 if 分支）。
- `checklist` 命令不接受 `--use-llm` 参数（测试 `test_checklist_cli_rejects_use_llm_option` 已验证）。
- Provider/serializer/runtime cost 字段的添加不影响 deterministic 路径——这些字段仅在 LLM 调用路径中填充。

测试覆盖：
- `test_analyze_cli_default_product_request`：验证默认不调用 `load_llm_provider_config_from_env`。
- `test_checklist_cli_rejects_use_llm_option`：验证 checklist 不接受 `--use-llm`。

## 5. 是否未触碰 golden/fixtures/score/quality gate/Host/Agent/dayu/PR 状态

**结论：合规。**

Implementation evidence 列出 allowed files 限于：
- `fund_agent/services/chapter_orchestrator.py`
- `fund_agent/services/llm_provider.py`
- `fund_agent/ui/cli.py`
- `tests/services/test_llm_provider.py`
- `tests/services/test_chapter_orchestrator.py`
- `tests/ui/test_cli.py`

审查代码确认：
- 无 golden/fixtures 文件修改。
- 无 score/quality gate 逻辑修改。
- 无 Host/Agent/dayu 模块引入。
- 无 PR/push/merge/release 状态操作。
- Provider config/auth 结论未被回退。

## 6. Tests 覆盖

**结论：合规。**

### Writer provider-bound prompt cost
- `test_timeout_retry_exhausted_carries_provider_diagnostics`（`test_llm_provider.py:187-231`）：覆盖 writer timeout diagnostics 的 `system_prompt_chars`/`user_prompt_chars`/`approx_prompt_tokens`/`allowed_fact_count=None`/`allowed_anchor_count`/`max_output_chars`。

### Auditor provider-bound prompt cost
- `test_auditor_timeout_diagnostic_uses_provider_bound_prompt_cost`（`test_llm_provider.py:234-274`）：覆盖 auditor diagnostics 基于 provider-bound user prompt 计算长度，验证 `user_prompt_chars > len(request.user_prompt)`，验证 `allowed_fact_count`/`allowed_anchor_count`/`max_output_chars=None`。

### Timeout exhausted diagnostics
- `test_timeout_retry_exhausted_carries_provider_diagnostics`：验证 3 次尝试全部 timeout 后 diagnostic 数量、attempt index 序列、category、cost 标量。
- `test_provider_timeout_diagnostic_is_enriched_and_does_not_regenerate`（`test_chapter_orchestrator.py:553-623`）：验证 provider diagnostics 经 orchestrator enrich 后补齐 chapter_id/fund_code/report_year/repair_attempt_index/chapter_failure_category。

### Serializer canary negative leak
- `test_runtime_diagnostic_serialization_exposes_only_safe_scalars`（`test_chapter_orchestrator.py:956-1077`）：注入 18 种 canary 敏感字符串，验证全部不出现在序列化输出中。同时验证 `model_name`/`message` 不作为字段名出现在 payload 中。
- `test_runtime_diagnostic_serialization_includes_attempt_level_diagnostics`（`test_chapter_orchestrator.py:1080-1097`）：验证 attempt 级 diagnostics 被包含且不含 `message`。

### CLI fail-closed summary
- `test_analyze_cli_use_llm_timeout_fail_closed_without_fallback`（`test_cli.py:1541-1598`）：验证 timeout 场景 exit 1、stdout 空、stderr 含完整 runtime 标量、negative leak 断言覆盖 13 种敏感字符串。

---

## Residual Risks

1. **`_sanitize_text` 敏感词列表不完全**（`llm_provider.py:704-714` 和 `chapter_orchestrator.py:2173`）：
   - Provider 层 `_sanitize_text` 包含 `"prompt"` 替换为 `[redacted]`，但 Service 层 `chapter_orchestrator.py` 的同名函数不包含 `"prompt"` 替换。当前无路径将 Service 层 `_sanitize_text` 的输出用于 runtime serializer（serializer 刻意不输出 `message`），所以这不是 blocking issue。但如果未来 gate 允许 serializer 输出 `message`，两处 `_sanitize_text` 的不一致可能导致泄漏。建议未来统一为单一 sanitize 函数。

2. **`_writer_runtime_diagnostic` 和 `_audit_runtime_diagnostic` 中的 `message` 字段**（`chapter_orchestrator.py:1296-1314` 和 `1342-1361`）：
   - 这些函数将 writer/auditor issue messages 拼接后经 `_sanitize_text` 处理写入 `message`。当前 serializer 和 CLI 刻意不输出 `message`，但 `ChapterLLMRuntimeDiagnostic` dataclass 仍保留该字段。如果未来 serializer 变更不慎包含了 `message`，可能泄漏 writer/auditor issue 文本。这是一个结构性的防御纵深风险，当前已被 serializer allowlist 机制覆盖。

3. **`model_name` 在 diagnostic dataclass 中保留但 serializer 不输出**：
   - `_enrich_provider_diagnostic`（行 1243-1269）传递 `diagnostic.model_name`（provider 返回的模型名）到 enriched diagnostic。当前 serializer 不输出 `model_name`。如果未来需要输出 `model_name`，plan 要求 review 确认不会泄漏配置的 secret-like 部署名。当前无风险。

4. **Real provider smoke 仍需 controller 验证**：
   - 本 review 仅覆盖代码和测试逻辑。Plan §8 明确要求 controller 运行真实 provider smoke 和 secret leak scan。Implementation evidence 也记录了这一 residual。

5. **README 未同步**：
   - Implementation evidence 记录了 README 未更新的决策，因为用户约束了 allowed files。Controller 需决定是否单独开 documentation synchronization gate。这不是代码质量问题。

---

## 审查结论

实现严格遵循 plan 的六项审查重点：
1. Timeout retry 只针对 `httpx.TimeoutException`，bounded by `timeout_max_attempts`（1..3），非 timeout 错误不重试。
2. Runtime-cost diagnostics 只记录 `len()`-derived 标量，不存储或传递任何文本。
3. Serializer/CLI 只输出 allowlisted 标量字段，刻意排除 `message`/`model_name`，测试用 canary 字符串验证了 18+ 种敏感模式均不存在。
4. Default deterministic 行为完全未变。
5. 未触碰 golden/fixtures/score/quality gate/Host/Agent/dayu/PR 状态。
6. 测试覆盖了 plan 要求的全部六项场景。

**Verdict: PASS。** Residual risks 均为非 blocking 的防御纵深事项，已被当前 allowlist 机制覆盖。Controller 应继续执行 real provider smoke 和 secret leak scan 验证。
