# MVP provider runtime timeout hardening code review (GLM)

日期：2026-05-31

Gate：`MVP provider runtime timeout hardening implementation gate`

角色：Code review worker（GLM），不是 implementation worker。本文只做 review，不改文件、不 push、不 merge。

## Findings

无 blocking findings。下文按 severity 排序。

### F1 — Non-blocking / Low：orchestrator `_sanitize_text` 敏感词列表短于 provider 层

- **文件**：`fund_agent/services/chapter_orchestrator.py:1526`
- **对比**：`fund_agent/services/llm_provider.py:585-594`
- **详情**：orchestrator 的 `_sanitize_text` 红脱敏列表为 `("Authorization", "Bearer", "FUND_AGENT_LLM_API_KEY", "api_key", "sk-", "prompt")`，缺少 provider 层的 `"writer user"` 和 `"draft markdown"`。
- **风险评估**：
  - Provider 层异常在进入 orchestrator 前已由 provider 的 `_sanitize_text` 处理，消息文本已是安全短句（如 `"LLM provider request timed out"`）。
  - Orchestrator 处理的 Fund 层 writer/auditor issue 消息来自 `ChapterWriteResult.stop_reason` 和 `ChapterAuditIssue.message`，这些是结构化短文本，不含 `"writer user"` 或 `"draft markdown"`。
  - 理论上若 Fund 层未来在 issue message 中嵌入 `"draft markdown"` 文本，orchestrator 不会脱敏。
- **结论**：当前不构成泄漏风险。建议后续统一 `_sanitize_text` 或提取为共享 helper 时合并列表。

### F2 — Info：异常类型匹配使用字符串比较而非 isinstance

- **文件**：`fund_agent/services/chapter_orchestrator.py:960-968`、`chapter_orchestrator.py:1179-1190`
- **详情**：`_provider_runtime_stop_reason()` 和 `_provider_runtime_category_from_exception()` 使用 `type(exc).__name__` 字符串匹配而非 `isinstance()`。
- **优点**：避免 orchestrator 导入 provider error types，保持 Service 层模块边界清晰。
- **风险**：若有人子类化 `LLMProviderTimeoutError`，匹配会失败并 fallback 到 `llm_exception`/`code_bug`。当前代码中所有 error 类都是叶子类，无子类化。fallback 也是 fail-closed 行为。
- **结论**：合理的设计权衡，不是 bug。

### F3 — Info：`_exception_result` 中 diagnostics 放置位置的不对称

- **文件**：`fund_agent/services/chapter_orchestrator.py:885-943`
- **详情**：writer 异常时 diagnostics 放在 `ChapterRunResult.runtime_diagnostics`；auditor 异常时 diagnostics 放在最后一个 `ChapterAttemptRecord.runtime_diagnostics`。这是因为 writer 异常时当前 attempt 未被追加到 attempts 列表，而 auditor 异常时已有 writer 成功的 attempt 记录。
- **影响**：下游消费者需检查 `result.runtime_diagnostics` 和 `attempt.runtime_diagnostics` 两处。当前唯一下游是 CLI stderr 和 diagnostic JSON，两者都正确处理了这两个位置。
- **结论**：正确实现，仅标注不对称性供后续维护参考。

## Scope guard verification

| 检查项 | 结果 |
|--------|------|
| `fund_agent/fund/chapter_writer.py` 未被本 gate 修改 | PASS — git diff 显示为之前 gate 的新增文件，本 gate 无增量改动 |
| `fund_agent/fund/chapter_auditor.py` 未被本 gate 修改 | PASS — 同上 |
| Fund Protocol request/response dataclass 签名不变 | PASS — `ChapterLLMRequest`、`ChapterLLMResponse`、`ChapterAuditLLMRequest`、`ChapterAuditLLMResponse` 无字段变更 |
| `ChapterLLMClient` / `ChapterAuditLLMClient` Protocol 签名不变 | PASS — `generate_chapter()` 和 `audit_chapter()` 签名不变 |
| golden/fixtures/score/quality gate 不变 | PASS — 无相关文件 diff |
| 默认 deterministic analyze/checklist 不读 LLM config | PASS — `test_analyze_cli_default_product_request` 验证 `_forbid_llm_config` |

## 必查项逐条核验

### 1. timeout-only retry/backoff 是否只在 provider timeout 生效

PASS。

- `llm_provider.py:230-249`：只有 `httpx.TimeoutException` 进入 retry 循环。
- `llm_provider.py:265-278`：429 立即抛 `LLMProviderRateLimitError`。
- `llm_provider.py:279-292`：非 2xx 立即抛 `LLMProviderRuntimeError`。
- `llm_provider.py:250-263`：`httpx.TransportError`（非 timeout）立即抛 `LLMProviderNetworkError`。
- `llm_provider.py:294-341`：malformed JSON/shape 立即抛 `LLMProviderMalformedResponseError`。
- 最大轮次 `timeout_max_attempts` 有界 [1,3]，默认 2。
- 默认 deterministic analyze/checklist 不构造 provider client。

### 2. provider runtime diagnostics 不进入 Fund writer/auditor protocol

PASS。

- `ChapterLLMRuntimeDiagnostic` 只定义在 `fund_agent/services/chapter_orchestrator.py:117`，Service 层。
- `fund_agent/fund/chapter_writer.py` 和 `chapter_auditor.py` 无任何 diagnostic 相关变更。
- `ChapterLLMRequest`、`ChapterLLMResponse`、`ChapterAuditLLMRequest`、`ChapterAuditLLMResponse` 无新增字段。
- `generate_chapter()` 和 `audit_chapter()` 签名不变。

### 3. Service 层补齐 chapter_id/fund_code/report_year/repair_attempt_index

PASS。

- Provider 层 `_provider_diagnostic()` (`llm_provider.py:506-525`)：`chapter_id=None`、`fund_code=None`、`report_year=None`、`repair_attempt_index=None`。
- Orchestrator `_enrich_provider_diagnostic()` (`chapter_orchestrator.py:1029-1069`)：填入 `chapter_id=chapter_id`、`fund_code=projection.fund_code`、`report_year=projection.report_year`、`repair_attempt_index=attempt_index`。
- Provider diagnostics 无 API key、Authorization、prompt、draft、完整 response。

### 4. CLI incomplete message fail-closed 且只输出安全 first failed summary

PASS。

- `cli.py:269-271`：`use_llm and result.final_assembly_result.report_markdown is None` 时输出 stderr 并 exit 1。
- `_llm_incomplete_message()` (`cli.py:807-832`)：遍历 `chapter_results` 找第一个 `status != "accepted"` 的章节。
- `_first_failed_chapter_summary()` (`cli.py:835-860`)：只输出 `chapter_id`、`status`、`stop_reason`。
- 无 `first_failed_chapter=none` fallback 分支 (`cli.py:860`)。
- `test_analyze_cli_use_llm_timeout_fail_closed_without_fallback` 验证 stderr 包含 `first_failed_chapter_id=2, first_failed_status=failed, first_failed_stop_reason=llm_timeout` 且 stdout 为空。

### 5. 分类精确

PASS。

Provider runtime taxonomy (`llm_provider.py`):
| category | 来源 | 处理 |
|----------|------|------|
| timeout | `httpx.TimeoutException` after bounded retry | `llm_timeout` |
| rate_limit | HTTP 429 | `llm_rate_limited` |
| malformed | JSON parse failure / invalid structure | `llm_malformed_response` |
| network | `httpx.TransportError` (non-timeout) | `llm_network_error` |
| http_error | non-2xx / non-429 | `llm_exception` |

Chapter failure taxonomy (`chapter_orchestrator.py`):
| category | 来源 | 映射函数 |
|----------|------|----------|
| provider_runtime | LLMProvider*Error 子类 | `_chapter_failure_category_from_exception()` |
| prompt_contract | writer stop reasons: `llm_empty_response`, `llm_contract_violation`, `missing_required_structure`, `missing_required_output_marker`, `unknown_anchor`, `response_too_long`, `response_incomplete` | `_chapter_failure_category_from_writer_result()` |
| audit_parse | LLM audit `llm:parse_failure` issue | `_chapter_failure_category_from_audit_result()` |
| fact_gap | `missing_required_facts`, `evidence_anchor_missing`, `item_rule_deleted_required_content`, `fund_type_unknown`, `needs_more_facts` | 同上 |
| code_bug | unexpected exception | fallback |

未混淆的分类边界：
- `prompt_contract` / `audit_parse`：writer blocked 为 `prompt_contract`，auditor `llm:parse_failure` 为 `audit_parse`，互不交叉。
- `fact_gap` / `code_bug`：`needs_more_facts` 为 `fact_gap`，`RuntimeError` 为 `code_bug`。

### 6. 测试覆盖

PASS。

| 测试场景 | 测试文件:行 | 断言 |
|----------|-------------|------|
| Bounded retry 后成功 | `test_llm_provider.py:153-185` | 3 次请求、2 次 sleep、返回正确响应 |
| Timeout exhausted diagnostics | `test_llm_provider.py:187-222` | 3 条 diagnostics、`chapter_id=None`、无 secret |
| Non-timeout 不 retry | `test_llm_provider.py:225-288` | 429/400/500/网络/malformed 均 1 次请求 |
| Diagnostic propagation + enrich | `test_chapter_orchestrator.py:544-613` | enriched `chapter_id=1`、`fund_code`、`provider_runtime_category=timeout`、不 regenerate |
| prompt_contract 分类 | `test_chapter_orchestrator.py:616-625` | `missing_required_output_marker` → `prompt_contract` |
| audit_parse 分类 | `test_chapter_orchestrator.py:628-641` | `llm:parse_failure` → `audit_parse` |
| fact_gap 分类 | `test_chapter_orchestrator.py:644-660` | `needs_more_facts` → `fact_gap` |
| code_bug 分类 | `test_chapter_orchestrator.py:663-681` | `RuntimeError` → `code_bug`，无 Authorization/Bearer/sk- |
| Missing config fail-closed | `test_cli.py:1248-1286` | exit 1、stdout 空、无 Service 调用 |
| Deterministic default | `test_cli.py:1541-1571` | `_forbid_llm_config` 验证不读 LLM |
| Timeout fail-closed | `test_cli.py:1394-1430` | exit 1、stdout 空、stderr 含 `first_failed_chapter_id=2, llm_timeout` |
| checklist 拒绝 `--use-llm` | `test_cli.py:1904-1934` | exit ≠ 0、无 Service 调用 |
| Config 边界 | `test_llm_config.py:94-119` | `1,3` pass; `0,4,1.5,not-int` fail |
| Backoff 边界 | `test_llm_config.py:122-147` | `0,30,2.5` pass; `-0.1,31,not-number` fail |
| Repr 不泄密 | `test_llm_config.py:32,193` | `"secret-value" not in repr(config)` |

## 验证命令

本 reviewer 未亲自运行验证命令。以下基于 implementation evidence 报告和代码阅读：

| 命令 | Evidence 报告结果 |
|------|-------------------|
| `uv run ruff check .` | PASS |
| `uv run pytest tests/config/test_llm_config.py tests/services/test_llm_provider.py tests/services/test_chapter_orchestrator.py tests/services/test_fund_analysis_service_llm.py tests/ui/test_cli.py -q` | 157 passed |
| `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q` | 1151 passed, 91.82% |
| missing-config smoke | PASS |
| deterministic analyze smoke | PASS |
| deterministic checklist smoke | PASS |
| real provider rerun | blocked (missing env) |

## Secret hygiene

- `api_key=field(repr=False)` 保留。 ✓
- Provider diagnostic 无 API key、Authorization、prompt、draft、provider body。 ✓
- CLI stderr 无 prompt/draft/response/key。 ✓
- 测试包含否定断言：`"Authorization" not in`、`"Bearer" not in`、`"test-secret" not in`、`"writer user" not in`、`"full error body" not in`。 ✓
- Orchestrator `_sanitize_text` 覆盖 "Authorization", "Bearer", "sk-", "FUND_AGENT_LLM_API_KEY", "api_key", "prompt"。 ✓
- Provider `_sanitize_text` 额外覆盖 "writer user", "draft markdown"。 ✓

## 结论

**PASS**。无 blocking findings。

实现严格遵守了 accepted plan 的所有约束：
- Timeout-only bounded retry，非 timeout 不 retry
- Provider diagnostics 不进入 Fund Protocol
- Service 层正确补齐章节身份
- CLI fail-closed、无 deterministic fallback
- 错误分类精确且两层分离
- 测试覆盖所有 plan 指定场景
- Secret hygiene 完整

3 个 non-blocking/info findings 已记录，不阻碍 gate 推进。
