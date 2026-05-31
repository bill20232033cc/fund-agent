# MVP provider runtime timeout follow-up code review

日期：2026-05-31

Reviewer：mimo（code review worker，不是 implementation worker）

Gate：`MVP provider runtime timeout follow-up gate`

Review scope：当前未提交改动中与本 gate 相关的 6 个文件。

## Verdict

**PASS**

## Review Basis

- `docs/reviews/mvp-provider-runtime-timeout-follow-up-plan-20260531.md`（accepted plan）
- `docs/reviews/mvp-provider-runtime-timeout-follow-up-implementation-evidence-20260531.md`
- `AGENTS.md`
- 当前未提交 diff（`git diff`）和完整文件读取

## Review Findings

### 1. Provider timeout retry 是否只针对 timeout 且 bounded

**PASS**

- `llm_provider.py:257`：只有 `httpx.TimeoutException` 进入 retry loop，`provider_attempt_index` 从 1 到 `max_attempts`（config 范围 1..3）。
- `llm_provider.py:278`：`httpx.TransportError`（网络错误）立即 raise `LLMProviderNetworkError`，不 retry。
- `llm_provider.py:294`：`status_code == 429` 立即 raise `LLMProviderRateLimitError`，不 retry。
- `llm_provider.py:309`：非 2xx 立即 raise `LLMProviderRuntimeError`，不 retry。
- `llm_provider.py:325-376`：malformed response 立即 raise `LLMProviderMalformedResponseError`，不 retry。
- `test_llm_provider.py:285-298`：`test_http_errors_do_not_retry` 参数化验证 400/429/500 只发送 1 次请求。
- `test_llm_provider.py:301-323`：`test_network_error_does_not_retry_and_carries_single_diagnostic` 验证网络错误只发送 1 次请求。
- `test_llm_provider.py:326-340`：`test_malformed_response_does_not_retry_and_carries_single_diagnostic` 验证 malformed 只发送 1 次请求。
- `test_llm_provider.py:153-184`：`test_timeout_only_retry_succeeds_on_later_attempt` 验证 timeout retry 在后续 attempt 成功。
- `test_llm_provider.py:187-231`：`test_timeout_retry_exhausted_carries_provider_diagnostics` 验证 timeout 耗尽后携带 3 条诊断且 `provider_max_attempts=3`。

非 timeout 错误不被无限/长时间 retry。PASS。

### 2. Runtime-cost diagnostics 是否只记录安全标量

**PASS**

- `llm_provider.py:49-67`：`_ProviderCostContext` 只存储 `system_prompt_chars`、`user_prompt_chars`、`approx_prompt_tokens`、`allowed_fact_count`、`allowed_anchor_count`、`max_output_chars`。不含 prompt 文本、draft、API key。
- `llm_provider.py:486-498`：`_writer_cost_context` 从 `request.system_prompt` 和 `request.user_prompt` 取 `len()`，不存储原文。
- `llm_provider.py:517-530`：`_auditor_cost_context` 从 `provider_user_prompt`（实际发送文本）取 `len()`，不存储原文。
- `llm_provider.py:533-547`：`_approx_prompt_tokens` 使用 `ceil((system + user) / 4)` 固定 heuristic。
- `llm_provider.py:587-644`：`_provider_diagnostic` 构造诊断时只写入 cost context 标量，`model_name=None`（provider 层不返回 model 信息到诊断中）。
- `llm_provider.py:637-638`：`system_prompt_chars=cost_context.system_prompt_chars` 等只赋值标量。
- `chapter_orchestrator.py:156-209`：`ChapterLLMRuntimeDiagnostic` dataclass 定义了 cost 标量字段（`system_prompt_chars` 等），均为 `int | None`。
- `chapter_orchestrator.py:2549-2583`：`_runtime_diagnostic_payload` 序列化时不输出 `model_name` 和 `message`。
- `test_llm_provider.py:218-231`：timeout exhausted 测试验证 `system_prompt_chars == len("writer system")`、`user_prompt_chars == len("writer user")`、`approx_prompt_tokens == ceil_div4(sum)`，且 `diagnostic_text` 不含 `Authorization`、`Bearer`、`writer user`、`test-secret`。
- `test_llm_provider.py:234-274`：auditor timeout 测试验证 cost 基于实际 provider-bound prompt（`user_prompt_chars > len(audit_request.user_prompt)`），且 `diagnostic_text` 不含 `draft markdown`、`按 SEVERITY|LOCATION|MESSAGE 返回。`、`test-secret`。

不暴露 API key、Authorization、完整 prompt、draft、provider response、raw audit response。PASS。

### 3. Serializer/CLI 是否只输出 allowlisted fields

**PASS**

- `chapter_orchestrator.py:2549-2583`：`_runtime_diagnostic_payload` 输出白名单字段：`operation`、`repair_attempt_index`、`provider_attempt_index`、`provider_max_attempts`、`provider_runtime_category`、`chapter_failure_category`、`elapsed_ms`、`status_code`、`request_id`、`finish_reason`、`response_chars`、`error_type`、`system_prompt_chars`、`user_prompt_chars`、`approx_prompt_tokens`、`allowed_fact_count`、`allowed_anchor_count`、`max_output_chars`。不含 `model_name`、`message`、`parse`、`model`、`base_url`、`key`、`header`。
- `chapter_orchestrator.py:2441-2470`：`_first_failed_runtime_diagnostic` 输出 `chapter_id`、`status`、`stop_reason`、`category`、`subcategory`、`runtime_operation`、`repair_attempt_index`、`provider_attempt_count`、`provider_max_attempts`、`provider_runtime_categories`、`system_prompt_chars`、`user_prompt_chars`、`approx_prompt_tokens`、`allowed_fact_count`、`allowed_anchor_count`、`max_output_chars`。不含 `message`。
- `cli.py:873-901`：`_first_failed_runtime_summary` 输出 `first_failed_runtime_operation`、`first_failed_provider_attempts`、`first_failed_provider_runtime_category`、`first_failed_elapsed_ms_max`、`first_failed_prompt_chars`、`first_failed_approx_prompt_tokens`。不含 `message`。
- `test_chapter_orchestrator.py:956-1077`：`test_runtime_diagnostic_serialization_exposes_only_safe_scalars` 使用包含 canary 字符串（`USER_PROMPT_CANARY`、`DRAFT_MARKDOWN_CANARY`、`RAW_RESPONSE_CANARY`、`RAW_AUDIT_RESPONSE_CANARY`、`SYSTEM_PROMPT_CANARY`、`PROVIDER_RESPONSE_CANARY`、`secret-deployment-model`、`Authorization`、`Bearer`、`sk-secret`、`header`、`key`）的 `message` 字段，验证 `str(payload)` 不含任何 forbidden 字符串。验证 `model_name` 不在序列化输出中。
- `test_cli.py:1541-1598`：`test_analyze_cli_use_llm_timeout_fail_closed_without_fallback` 验证 stderr 不含 `message`、`Authorization`、`Bearer`、`sk-`、`header`、`key`、`auditor`、`programmatic`、`raw audit`、`system_prompt`、`user_prompt`、`draft_markdown`、`provider_response`、`provider body`。

parse/message/model/base_url/key/header 不泄漏。PASS。

### 4. Default deterministic analyze/checklist 行为是否不变

**PASS**

- `cli.py:243`：`if use_llm:` 分支与 `else:` 分支互斥。默认 `use_llm=False` 走 `FundAnalysisService().analyze(request)`。
- `cli.py:276-351`：`checklist` 命令无 `--use-llm` 选项，完全不触碰 LLM 路径。
- `test_cli.py:1261-1353`：`test_analyze_cli_calls_service_and_prints_report` 验证默认 analyze 调用 `analyze`（非 `analyze_with_llm`），`analyze_with_llm_called=False`。
- `test_cli.py:1709-1740`：`test_analyze_cli_default_product_request` 验证默认请求 `mode="product"`、`developer_overrides=None`。
- `test_cli.py:2072-2102`：`test_checklist_cli_rejects_use_llm_option` 验证 checklist 不接受 `--use-llm`。

默认 deterministic 行为不变。PASS。

### 5. 是否未触碰 golden/fixtures/score/quality gate/Host/Agent/dayu/PR 状态

**PASS**

- diff 中不包含 `golden`、`fixtures`、`score`、`quality_gate`、`host`、`agent`、`dayu` 相关文件。
- 不包含 `docs/design.md`、`docs/fund-analysis-template-draft.md` 修改。
- 不包含 PR/push/merge 操作。
- `test_chapter_orchestrator.py:1828-1854`：`test_chapter_orchestrator_imports_do_not_cross_forbidden_boundaries` 验证 orchestrator 不导入 `documents`、`repository`、`cache`、`pdf`、`source`、`downloader`、`parser`、`dayu`、`openai`、`httpx`。

PASS。

### 6. Tests 是否覆盖 plan 要求的关键场景

**PASS**

| Plan 要求 | 测试覆盖 | 文件:行号 |
|---|---|---|
| writer/auditor provider-bound prompt cost | `test_timeout_retry_exhausted_carries_provider_diagnostics` + `test_auditor_timeout_diagnostic_uses_provider_bound_prompt_cost` | `test_llm_provider.py:187` + `test_llm_provider.py:234` |
| timeout exhausted diagnostics | `test_timeout_retry_exhausted_carries_provider_diagnostics` | `test_llm_provider.py:187` |
| serializer canary negative leak (message/model_name/prompt/draft/body/key/header) | `test_runtime_diagnostic_serialization_exposes_only_safe_scalars` | `test_chapter_orchestrator.py:956` |
| attempt-level diagnostics included | `test_runtime_diagnostic_serialization_includes_attempt_level_diagnostics` | `test_chapter_orchestrator.py:1080` |
| CLI fail-closed timeout summary with safe fields | `test_analyze_cli_use_llm_timeout_fail_closed_without_fallback` | `test_cli.py:1541` |
| CLI no deterministic fallback on incomplete | `test_analyze_cli_use_llm_incomplete_result_exits_without_fallback` | `test_cli.py:1468` |
| prompt-contract diagnostic serialization excludes raw payloads | `test_sanitized_prompt_contract_serialization_excludes_raw_payloads` | `test_chapter_orchestrator.py:931` |
| provider runtime exceptions map to precise stop reason | `test_provider_runtime_exceptions_map_to_precise_stop_reason` | `test_chapter_orchestrator.py:515` |
| timeout enrich carries chapter identity | `test_provider_timeout_diagnostic_is_enriched_and_does_not_regenerate` | `test_chapter_orchestrator.py:553` |

PASS。

## Residual Risks

### R1. `_first_failed_runtime_diagnostic` 字典缩进不一致（cosmetic）

`chapter_orchestrator.py:2441-2470`：`_first_failed_runtime_diagnostic` 返回的字典中，前 6 个 key（`chapter_id` 到 `repair_attempt_index`）使用 12 空格缩进，后续 10 个 key（`provider_attempt_count` 到 `max_output_chars`）使用 8 空格缩进。Python 语法合法，运行时行为正确（测试全部通过），但不符合项目统一 4 空格对齐惯例。

建议：后续清理时统一为一致的字典缩进。

### R2. `_audit_runtime_diagnostic` 在 dataclass 层存储 `model_name`，serializer 层排除

`chapter_orchestrator.py:1356`：`_audit_runtime_diagnostic` 将 `audit_result.llm.model_name` 存入 `ChapterLLMRuntimeDiagnostic.model_name` 字段。serializer `_runtime_diagnostic_payload`（line 2564）不输出 `model_name`，因此序列化产物安全。但如果未来有人直接序列化 dataclass（如 `dataclasses.asdict`），`model_name` 会泄漏。

当前 gate 正确：serializer 控制了输出边界。后续 gate 若引入通用序列化路径，需确认 `model_name` 排除策略。

### R3. `_sanitize_text` 在 orchestrator 和 provider 中有两份实现

`chapter_orchestrator.py:2158-2177` 和 `llm_provider.py:687-717` 各有一份 `_sanitize_text`，逻辑基本相同但 provider 版本多了 `"writer user"` 和 `"draft markdown"` 两个 redaction pattern。这不是本 gate 引入的问题（provider 版本是本次新增），但如果未来需要统一 redaction 规则，需注意两处维护。

建议：后续 gate 可考虑抽取为共享 utility，但不在本 gate scope 内。

### R4. Real provider smoke 未执行

implementation evidence 记录 "Real provider smoke was not run, per implementation-worker handoff constraint"。controller 仍需在后续 validation gate 中运行真实 provider smoke 以验证 timeout 分类在实际环境中成立。

## Summary

实现与 plan delta 一致：
- Runtime-cost diagnostics 只记录安全标量（char counts、approx tokens、fact/anchor counts）。
- Serializer 只输出 allowlisted fields，排除 `model_name`、`message`、prompt、draft、body、key、header。
- CLI fail-closed summary 只输出 safe scalar timeout fields。
- Timeout retry 仅针对 `httpx.TimeoutException`，bounded by config 1..3。
- Non-timeout 错误不 retry。
- Default deterministic 行为不变。
- 未触碰 golden/fixtures/score/quality gate/Host/Agent/dayu/PR。
- C2 prompt contract 修复未混入本 gate。
- Tests 覆盖 writer/auditor prompt cost、timeout exhausted diagnostics、serializer canary negative leak、CLI fail-closed summary。
