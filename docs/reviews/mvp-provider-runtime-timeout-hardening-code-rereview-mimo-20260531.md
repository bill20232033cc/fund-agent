# MVP provider runtime timeout hardening code re-review

日期：2026-05-31

Gate：`MVP provider runtime timeout hardening gate`

角色：review worker，不是 implementation worker。

Re-review 原因：前次 review 将 pre-existing Gate A dirty worktree 变更误判为本 gate scope violation。Controller 澄清后，本轮只 review allowed files。

## Review scope — allowed files only

- `fund_agent/config/llm.py`
- `fund_agent/services/llm_provider.py`
- `fund_agent/services/chapter_orchestrator.py`
- `fund_agent/ui/cli.py`
- `tests/config/test_llm_config.py`
- `tests/services/test_llm_provider.py`
- `tests/services/test_chapter_orchestrator.py`
- `tests/services/test_fund_analysis_service_llm.py`
- `tests/ui/test_cli.py`
- `fund_agent/config/README.md`

## Verification commands run

| Command | Result |
|---|---|
| `uv run ruff check .` | PASS |
| `uv run pytest tests/config/test_llm_config.py tests/services/test_llm_provider.py tests/services/test_chapter_orchestrator.py tests/services/test_fund_analysis_service_llm.py tests/ui/test_cli.py -q` | PASS, 157 passed |
| `uv run pytest tests/services/test_fund_analysis_service_llm.py -q` | PASS, 7 passed |

## Review criteria checklist

### 1. Timeout-only bounded retry, deterministic default unchanged

**llm_provider.py:219-249** — `_complete()` loops `for provider_attempt_index in range(1, max_attempts + 1)`，只 catch `httpx.TimeoutException` 执行 retry。以下立即 raise 不 retry：
- `httpx.TimeoutException` → retry (line 230-249)
- `httpx.TransportError` (非 timeout) → `LLMProviderNetworkError` (line 250-263)
- HTTP 429 → `LLMProviderRateLimitError` (line 265-278)
- 非 2xx 非 429 → `LLMProviderRuntimeError` (line 279-292)
- JSON parse failure / malformed shape → `LLMProviderMalformedResponseError` (line 294-341)

Timeout exhausted 后抛 `LLMProviderTimeoutError` 携带 `diagnostics=tuple(diagnostics)` (line 246-249)。Backoff 只在 `provider_attempt_index < max_attempts` 时执行 (line 242-244)，且通过 `self._sleep()` 注入，测试用 `lambda _: None` 或 `sleeps.append`。

**llm.py:20-21, 64-65** — `timeout_max_attempts` 默认 2，边界 [1,3]；`timeout_backoff_seconds` 默认 1.0，边界 [0,30]。

**cli.py:252-253** — 默认 `analyze` 不读 LLM config；`checklist` 无 `--use-llm` 选项。

✅ PASS

### 2. Provider diagnostics not entering Fund writer/auditor protocol

- `ChapterLLMRuntimeDiagnostic` 定义在 `chapter_orchestrator.py:116-158`（Service 层）。
- `llm_provider.py:30-35` 从 orchestrator import `ChapterLLMRuntimeDiagnostic`、`ProviderOperation`、`ProviderRuntimeCategory`。
- `generate_chapter()` / `audit_chapter()` 签名未变，返回 `ChapterLLMResponse` / `ChapterAuditLLMResponse`，不含 diagnostics。
- Provider exception 通过 `.diagnostics` 属性携带诊断，由 orchestrator 在 `_exception_result()` 中提取。

✅ PASS

### 3. Service layer enriches chapter identity, diagnostics contain no secrets

**Provider 层** (`llm_provider.py:476-525`) — `_provider_diagnostic()` 构造诊断时：
- `chapter_id=None`, `fund_code=None`, `report_year=None`, `repair_attempt_index=None`, `chapter_failure_category=None`
- 只填 provider-safe 字段：`operation`, `provider_attempt_index`, `provider_max_attempts`, `provider_runtime_category`, `elapsed_ms`, `status_code`, `request_id`, `error_type`, `message`
- `message` 通过 `_sanitize_text()` 脱敏 (line 524)

**Orchestrator 层** (`chapter_orchestrator.py:1029-1069`) — `_enrich_provider_diagnostic()` 补齐：
- `chapter_id`, `fund_code=projection.fund_code`, `report_year=projection.report_year`, `repair_attempt_index=attempt_index`
- `chapter_failure_category="provider_runtime"`

**脱敏** (`llm_provider.py:568-598`) — `_sanitize_text()` redact 列表包含 `Authorization`, `Bearer`, `FUND_AGENT_LLM_API_KEY`, `api_key`, `sk-`, `prompt`, `writer user`, `draft markdown`。单行化、限长 180 字符。

**Provider error** — `_safe_http_error_message()` 只含 status_code 和 request_id，不拼接 response.text (line 528-545)。

**Unknown exception** (`chapter_orchestrator.py:1006-1026`) — 当 provider exception 无 `.diagnostics` 时，构造单条 `code_bug` diagnostic，message 通过 `_safe_exception_message()` → `_sanitize_text()` 脱敏。

✅ PASS

### 4. CLI fail-closed, first_failed summary safe

**cli.py:269-271** — `if use_llm and result.final_assembly_result.report_markdown is None:` → 输出 incomplete message 并 `raise typer.Exit(code=1)`。Stdout 为空，无 deterministic fallback。

**cli.py:835-860** — `_first_failed_chapter_summary()` 遍历 `chapter_results`，找到第一个 `status != "accepted"` 的章节，输出：
- `first_failed_chapter_id=<chapter_id>`
- `first_failed_status=<status>`
- `first_failed_stop_reason=<stop_reason>`
- 无章节结果时输出 `first_failed_chapter=none`
- 不包含 prompt/draft/provider response/API key/Authorization

✅ PASS

### 5. Taxonomy precise, no cross-contamination

**Provider runtime categories** (`chapter_orchestrator.py:71-78`)：
- `success`, `timeout`, `rate_limit`, `malformed`, `network`, `http_error`

**Chapter failure categories** (`chapter_orchestrator.py:79-85`)：
- `provider_runtime`, `prompt_contract`, `audit_parse`, `fact_gap`, `code_bug`

**映射函数**：
- `_provider_runtime_category_from_exception()` (line 1164-1190): 按异常类型精确映射 provider category
- `_chapter_failure_category_from_exception()` (line 1193-1208): provider exception → `provider_runtime`，其他 → `code_bug`
- `_chapter_failure_category_from_writer_result()` (line 1211-1243): `missing_required_facts`/`evidence_anchor_missing`/`item_rule_deleted_required_content`/`fund_type_unknown` → `fact_gap`；`llm_empty_response`/`llm_contract_violation`/`missing_required_structure`/`missing_required_output_marker`/`unknown_anchor`/`response_too_long`/`response_incomplete` → `prompt_contract`；其他 → `code_bug`
- `_chapter_failure_category_from_audit_result()` (line 1246-1268): `llm:parse_failure` → `audit_parse`；`needs_more_facts` → `fact_gap`；`fail`/`blocked` → `prompt_contract`；其他 → `code_bug`

Timeout exhausted → `provider_runtime`，不触发额外 regenerate（orchestrator 在 exception 路径直接 return `_exception_result()`，不进入 audit/regenerate 循环）。

✅ PASS

### 6. Test coverage

**tests/config/test_llm_config.py**:
- 默认值 `timeout_max_attempts=2`, `timeout_backoff_seconds=1.0` (line 29-30)
- 合法边界 `1`, `3` / `0`, `30` (line 94-132)
- 非法边界 `0`, `4`, `1.5`, `not-an-int` / `-0.1`, `31`, `not-a-number` (line 107-147)
- `repr(config)` 不含 `secret-value` (line 32)

**tests/services/test_llm_provider.py**:
- `test_timeout_only_retry_succeeds_on_later_attempt`: 3 attempts, 2 timeouts then success, sleep 注入验证 (line 153-184)
- `test_timeout_retry_exhausted_carries_provider_diagnostics`: 3 attempts 全 timeout，diagnostics count=3，`chapter_id=None`/`fund_code=None`/`report_year=None`/`repair_attempt_index=None`/`chapter_failure_category=None`，不含 secret (line 187-222)
- `test_http_errors_do_not_retry`: 400/429/500 各只 1 次 request (line 225-246)
- `test_network_error_does_not_retry_and_carries_single_diagnostic`: TransportError 只 1 次 request (line 249-271)
- `test_malformed_response_does_not_retry_and_carries_single_diagnostic`: 空 choices 只 1 次 request (line 274-288)

**tests/services/test_chapter_orchestrator.py**:
- `test_provider_timeout_diagnostic_is_enriched_and_does_not_regenerate`: timeout exception → `llm_timeout`，diagnostics 含 `chapter_id=1`/`fund_code="110011"`/`report_year=2024`/`repair_attempt_index=0`/`chapter_failure_category="provider_runtime"`，不触发额外 regenerate (line 544-613)
- `test_writer_prompt_contract_blocked_records_diagnostic_category`: `missing_required_output_marker` → `prompt_contract` (line 616-625)
- `test_audit_parse_failure_records_audit_parse_diagnostic`: parse failure → `audit_parse`，respect `max_repair_attempts` (line 628-641)
- `test_needs_more_facts_records_fact_gap_diagnostic`: `needs_more_facts` → `fact_gap` (line 644-660)
- `test_unexpected_exception_records_code_bug_diagnostic_without_secret`: RuntimeError → `code_bug`，message 不含 `Authorization`/`Bearer`/`sk-` (line 663-681)
- `test_required_corrections_sanitize_unknown_issue_message`: 敏感文本脱敏 (line 807-835)

**tests/ui/test_cli.py**:
- `test_analyze_cli_use_llm_missing_config_fails_before_service`: exit 1, stdout empty, stderr 含 config error, Service 未调用 (line 1248-1286)
- `test_analyze_cli_use_llm_timeout_fail_closed_without_fallback`: exit 1, stdout empty, stderr 含 `first_failed_chapter_id=2`/`first_failed_status=failed`/`first_failed_stop_reason=llm_timeout`, 不含 `Authorization`/`Bearer` (line 1394-1430)
- `test_analyze_cli_use_llm_incomplete_result_exits_without_fallback`: exit 1, stdout empty, 无 deterministic fallback (line 1360-1391)
- `test_checklist_cli_rejects_use_llm_option`: checklist `--use-llm` 被拒绝 (line 1904)

**tests/services/test_fund_analysis_service_llm.py**: 7 passed，覆盖 LLM 分析 Service 路径。

✅ PASS

## Secret hygiene

- `_sanitize_text()` 两个实例（`llm_provider.py:568-598`, `chapter_orchestrator.py:1511-1530`）均 redact `Authorization`/`Bearer`/`FUND_AGENT_LLM_API_KEY`/`api_key`/`sk-`/`prompt`
- Provider `_safe_http_error_message()` 只含 status_code 和 request_id
- Provider error 不拼接 `response.text`、request JSON 或 headers
- Test negative assertions 覆盖 `Authorization`/`Bearer`/`test-secret`/`writer user`/`sk-`
- Config `api_key=field(repr=False)` 隐藏 key

✅ PASS

## Deterministic default unchanged

- `cli.py:253`: 默认 `analyze` 调用 `FundAnalysisService().analyze(request)`，不读 LLM config
- `cli.py:340`: `checklist` 调用 `FundAnalysisService().checklist(request)`，无 LLM 路径
- `checklist --use-llm` 被 typer 拒绝 (`test_checklist_cli_rejects_use_llm_option`)
- `_forbid_llm_config()` / `_forbid_llm_clients()` 在默认路径被注入时会 raise AssertionError

✅ PASS

## Conclusion

**PASS — no blocking finding in allowed-file scope.**

本 gate 的 timeout hardening 实现在 allowed files 范围内完全正确：

1. Timeout-only bounded retry 有界、可注入、不 retry 非 timeout 错误
2. Provider diagnostics 不进入 Fund Protocol，由 orchestrator enrich 章节身份
3. 所有 diagnostic message 通过 `_sanitize_text()` 脱敏，无 secret/prompt/draft/body 泄漏
4. CLI fail-closed，`first_failed_chapter_id/status/stop_reason` 安全输出
5. Taxonomy 两层分类精确，prompt_contract/audit_parse/fact_gap/code_bug 不被混淆
6. 测试覆盖 bounded retry、non-timeout no retry、diagnostic enrichment、missing config、deterministic default
