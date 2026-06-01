# MVP provider runtime timeout hardening plan

日期：2026-05-31

Gate：`MVP provider runtime timeout hardening plan gate`

角色：Gateflow planning worker。本文只提供 code-generation-ready plan，不实现代码、不提交、不 push、不创建或更新 PR。

## plan review fix log

本节记录 controller accepted reviewer findings 的修订结果。

| Finding | Controller decision | Plan revision |
|---|---|---|
| MiMo B-1 | accepted | `ChapterLLMRuntimeDiagnostic` 改为 Service-layer only；只允许定义在 `fund_agent/services/chapter_orchestrator.py` 或 `fund_agent/services/llm_provider.py`；从 diagnostic allowed files 中移除 `fund_agent/fund/chapter_writer.py` 和 `fund_agent/fund/chapter_auditor.py`。 |
| MiMo B-2 / GLM F1 | accepted | 不扩展 `ChapterLLMRequest` / `ChapterAuditLLMRequest` / `ChapterLLMResponse` / `ChapterAuditLLMResponse` / Protocol 签名来传递 diagnostics。Provider 层只记录 provider request attempt 诊断；章节 identity 由 orchestrator 在捕获异常或构造 `ChapterAttemptRecord` 诊断时补齐。 |
| GLM F2 | accepted | provider-level diagnostic 的 `repair_attempt_index` 为 `None`；orchestrator 聚合到 chapter attempt 时填入当前 `attempt_index`。 |
| GLM F4 | accepted | CLI failure message 从 “may append” 改为 “must append” first failed chapter `chapter_id/status/stop_reason`；provider attempt counts 留在 diagnostic JSON，除非后续确认不会造成耦合或泄漏。 |
| Non-blocking clarifications | accepted | 明确 sleep injection 默认 `time.sleep`、测试注入 no-op；diagnostic message 必须使用 `_sanitize_text()` 或等价 helper；writer/auditor 共享同一 client，但 retry 计数按每次 `_complete()` 调用独立。 |
| GLM F3 | accepted clarification | 拆分 `provider_runtime_category` 和 `chapter_failure_category`：provider 层只知道 provider runtime category；orchestrator 从 provider/runtime、writer/auditor result、repair decision 映射为 chapter failure category。 |

## goal and direct evidence

目标：在保持 `fund-analysis analyze --use-llm` fail-closed、无 deterministic fallback 的前提下，为真实 provider runtime timeout 增加有界、可诊断、不会放大成无限 repair loop 的 hardening。完成后，`006597 / 2024 --use-llm` 必须重新跑真实 provider validation，并把结果分类为 accepted full report、provider_runtime、prompt_contract、audit_parse、fact_gap、code_bug 或 unknown 中的一个。

直接证据：

- `docs/reviews/mvp-provider-auth-config-verification-controller-judgment-20260531.md` 已证明当前 MiMo-compatible provider auth/config 可用；本 gate 不把 blocker 重新归因为 missing provider config。
- `docs/reviews/mvp-llm-writer-auditor-contract-hardening-controller-judgment-20260531.md`：Gate A accepted；writer/auditor contract 已硬化；真实 provider diagnostic 中 chapter 1 accepted，chapter 2 failed `llm_timeout`。
- `docs/reviews/mvp-real-provider-smoke-acceptance-controller-judgment-20260531.md`：Gate B blocked，分类 `provider_runtime / timeout`，底层 `stop_reason=llm_timeout`；CLI exit code `1`，stdout empty，无 deterministic fallback。
- `docs/reviews/mvp-real-provider-smoke-timeout-rerun-controller-judgment-20260531.md`：timeout reproduced；rerun 中 chapter 1 regenerate 路径 failed `llm_timeout`，chapters 2-6 skipped `dependency_missing`。timeout 位置可变，说明问题不是单一章节事实缺口，也不是 provider/auth。
- Diagnostic JSON：
  - `reports/mvp-local-acceptance/20260531-writer-auditor-contract-hardening/real-provider-006597-2024-diagnostic.json`
  - `reports/mvp-local-acceptance/20260531-provider-timeout-rerun/real-provider-rerun-diagnostic.json`
- 当前代码事实：
  - `fund_agent/config/llm.py` 已有 typed `FUND_AGENT_LLM_TIMEOUT_SECONDS` 和 `FUND_AGENT_LLM_MAX_OUTPUT_CHARS`。
  - `fund_agent/services/llm_provider.py` 对 `httpx.TimeoutException` 映射为 `LLMProviderTimeoutError`，但没有 retry/backoff，也没有请求级 runtime diagnostics。
  - `fund_agent/services/chapter_orchestrator.py` 捕获 provider 异常并映射 `LLMProviderTimeoutError -> llm_timeout`；`ChapterOrchestrationPolicy.max_repair_attempts` 只控制 audit-driven regenerate，不控制 provider request retry。
  - `fund_agent/ui/cli.py` `--use-llm` 已从 typed config 传入 `max_output_chars`，默认 deterministic `analyze/checklist` 不读 LLM config。

## non-goals and hard constraints

- 不实现 deterministic fallback；provider runtime failure、partial orchestration、incomplete final assembly 仍 exit code `1` 且 stdout empty。
- 不放松 writer/auditor contract、required_output marker、anchor、missing marker、candidate facet、LLM audit line protocol 或 fail-closed 审计规则。
- 不进入 Gate 5；不新增 `fund_agent/host`、`fund_agent/agent`，不接入 `dayu.host` / `dayu.engine`。
- 不修改 golden、fixtures、score、quality gate、snapshot、manifest、promotion state、final judgment、基金分析模板或 `AGENTS.md`。
- 不改变默认 deterministic `fund-analysis analyze` 和 `fund-analysis checklist` 行为；它们仍不得读取 LLM env 或构造 provider client。
- 不把显式参数塞进 `extra_payload`。
- 不记录 API key、Authorization header、完整 provider response、完整 writer draft、完整 audit response、完整 prompt、完整 env var value。
- 不对 rate limit、malformed response、network error、prompt_contract、audit_parse、fact_gap 或 code_bug 做 retry；本 gate 只 retry provider timeout。
- 不把 timeout 成功重试包装成 quality/golden/readiness pass；真实 provider validation 只能证明本 gate runtime blocker 的当前分类。

## affected files / allowed files

本 planning worker 只允许写入：

- `docs/reviews/mvp-provider-runtime-timeout-hardening-plan-20260531.md`

后续 implementation worker 允许修改的代码/测试文件：

- `fund_agent/config/llm.py`
- `fund_agent/services/llm_provider.py`
- `fund_agent/services/chapter_orchestrator.py`
- `fund_agent/services/__init__.py`，仅当新增 public diagnostic type 需要导出时使用。
- `fund_agent/ui/cli.py`，仅允许改进 `--use-llm` incomplete/failure stderr 的安全分类摘要，默认 analyze/checklist 不得受影响。
- `tests/config/test_llm_config.py`
- `tests/services/test_llm_provider.py`
- `tests/services/test_chapter_orchestrator.py`
- `tests/services/test_fund_analysis_service_llm.py`
- `tests/ui/test_cli.py`
- `fund_agent/config/README.md`、`fund_agent/README.md`、根 `README.md`，仅当新增 typed env 或 CLI failure wording 需要同步当前用法时更新。
- `tests/README.md`，仅当新增测试运行约定需要同步时更新。

后续 validation 可生成但不得作为代码修改提交的运行证据目录：

- `reports/mvp-local-acceptance/20260531-provider-timeout-hardening/`

显式禁止修改：

- runtime 代码以外的 golden / fixture / score / quality gate / snapshot / promotion / manifest 文件。
- `fund_agent/fund/chapter_writer.py` 和 `fund_agent/fund/chapter_auditor.py`，本 gate 不扩展 Fund-layer Protocol request/response，不把 provider diagnostics 放入 Fund primitive。
- `docs/implementation-control.md`、`docs/current-startup-packet.md`、`docs/design.md`，除非 controller 在后续 gate 单独授权 docs/control sync。
- `docs/fund-analysis-template-draft.md`、`AGENTS.md`。

## proposed contract changes

### Typed env config

在 `LLMProviderConfig` 上新增两个显式字段：

- `timeout_max_attempts: int`
  - env：`FUND_AGENT_LLM_TIMEOUT_MAX_ATTEMPTS`
  - 默认：`2`，含首次请求，即最多一次 timeout retry。
  - 边界：`1 <= value <= 3`。
- `timeout_backoff_seconds: float`
  - env：`FUND_AGENT_LLM_TIMEOUT_BACKOFF_SECONDS`
  - 默认：`1.0`。
  - 边界：`0 <= value <= 30`。

保留现有 `timeout_seconds` 语义：单次 HTTP request timeout，不是整章、整报告或 CLI 总 timeout。

### Provider retry contract

`OpenAICompatibleChapterLLMClient` 在 `_complete()` 内对 `httpx.TimeoutException` 执行有界 retry：

- 只 retry timeout。
- HTTP 429 仍立即 `LLMProviderRateLimitError`，不 retry。
- malformed JSON/shape 仍立即 `LLMProviderMalformedResponseError`，不 retry。
- `httpx.TransportError` 非 timeout 仍立即 `LLMProviderNetworkError`，不 retry。
- 非 2xx 非 429 仍 `LLMProviderRuntimeError`，不 retry。
- 第 `timeout_max_attempts` 次仍 timeout 时抛出 `LLMProviderTimeoutError`。
- backoff 只发生在下一次 timeout retry 前；测试必须可注入 no-op sleep 或配置 `0`，不得让单元测试真实等待。

### Runtime diagnostic contract

新增安全 Service-layer runtime diagnostic，推荐命名：

- `ChapterLLMRuntimeDiagnostic`，schema `chapter_llm_runtime_diagnostic.v1`。
- 只能定义在 Service 层：`fund_agent/services/chapter_orchestrator.py` 或 `fund_agent/services/llm_provider.py`。
- 不得定义在 `fund_agent/fund/chapter_writer.py` 或 `fund_agent/fund/chapter_auditor.py`。
- 不得扩展 Fund-layer Protocol request/response：不修改 `ChapterLLMRequest`、`ChapterAuditLLMRequest`、`ChapterLLMResponse`、`ChapterAuditLLMResponse` 或 `ChapterLLMClient` / `ChapterAuditLLMClient` 签名来传递 diagnostics。
- Provider 层可以在 `LLMProviderRuntimeError` 子类上携带 provider attempt diagnostics；orchestrator 捕获异常后把 diagnostics enrichment 到 chapter attempt context。
- 对 writer/auditor 成功或 prompt/audit/fact failure，orchestrator 从已有安全 result 字段、`stop_reason`、`attempt_index` 和 repair decision 构造 chapter-level diagnostics；不要求 provider success diagnostics 穿越 Fund Protocol。

必须包含的安全字段：

- `operation`: `writer` / `auditor`
- `chapter_id: int | None`
- `fund_code: str | None`
- `report_year: int | None`
- `repair_attempt_index: int | None`
- `provider_attempt_index`
- `provider_max_attempts`
- `provider_runtime_category: "success" | "timeout" | "rate_limit" | "malformed" | "network" | "http_error" | None`
- `chapter_failure_category: "provider_runtime" | "prompt_contract" | "audit_parse" | "fact_gap" | "code_bug" | None`
- `elapsed_ms`
- `status_code: int | None`
- `request_id: str | None`
- `model_name: str | None`
- `finish_reason: str | None`
- `response_chars: int | None`
- `error_type: str | None`
- `message: str | None`，必须通过 `_sanitize_text()` 或等价 helper 生成短安全摘要，不能包含 prompt/draft/provider body/env value/header。

字段填充规则：

- Provider 层只填 `operation`、`provider_attempt_index`、`provider_max_attempts`、`provider_runtime_category`、HTTP/status/request/model/finish/elapsed/response length/error 安全字段；`chapter_id`、`fund_code`、`report_year`、`repair_attempt_index` 和 `chapter_failure_category` 在 provider 层必须为 `None`。
- Orchestrator 捕获 provider exception 时，用当前 `chapter_id`、`projection.fund_code`、`projection.report_year`、当前 orchestration `attempt_index` enrich provider diagnostics，并映射 `chapter_failure_category="provider_runtime"`。
- Audit provider-level diagnostic 的 `repair_attempt_index` 在 provider 层必须为 `None`；orchestrator 聚合时填入当前 `ChapterAttemptRecord.attempt_index`。
- Writer/auditor 共享同一个 `OpenAICompatibleChapterLLMClient` 实例，但 retry 计数按每次 `_complete()` 调用独立；writer 的 `_complete()` timeout retry 不影响 auditor 的 `_complete()` retry 计数，反之亦然。

禁止字段：

- `system_prompt`、`user_prompt`、`draft_markdown`、`raw_response`、provider response body、request JSON body、headers、API key、完整 base URL query/fragment、env var value。

### Error taxonomy mapping

后续实现必须分两层分类：provider 层只产出 `provider_runtime_category`；orchestrator 层把 provider/runtime、writer/auditor result、repair decision 映射为 `chapter_failure_category` 和现有 `ChapterRunResult.stop_reason`。

Provider runtime taxonomy：

| provider_runtime_category | 直接来源 | 处理 |
|---|---|---|
| `timeout` | `LLMProviderTimeoutError` after bounded attempts | `ChapterRunResult.stop_reason=llm_timeout`，fail-closed |
| `rate_limit` | `LLMProviderRateLimitError` | `llm_rate_limited`，fail-closed，不 retry |
| `malformed` | `LLMProviderMalformedResponseError` | `llm_malformed_response`，fail-closed，不 retry |
| `network` | `LLMProviderNetworkError` | `llm_network_error`，fail-closed，不 retry |
| `http_error` | non-2xx/non-429 `LLMProviderRuntimeError` | `llm_exception` 或保持现有 runtime error mapping，fail-closed，不 retry |
| `success` | provider 返回可解析 response | 不作为 failure；不穿越 Fund Protocol，只可在 provider-local test 中断言 |

Chapter failure taxonomy：

| chapter_failure_category | 直接来源 | 处理 |
|---|---|---|
| `provider_runtime` | provider runtime exception after mapping | 对应 `llm_timeout` / `llm_rate_limited` / `llm_malformed_response` / `llm_network_error` / `llm_exception` |
| `prompt_contract` | writer stop reasons: `llm_empty_response`、`llm_contract_violation`、`missing_required_structure`、`missing_required_output_marker`、`unknown_anchor`、`response_too_long`、`response_incomplete` | fail-closed；仍按现有 writer/auditor policy 决定是否 repair |
| `audit_parse` | LLM audit `llm:parse_failure` / C1 line protocol parse failure | fail-closed；可按现有 `max_repair_attempts` regenerate |
| `fact_gap` | `missing_required_facts`、`needs_more_facts`、`fund_type_unknown`、critical evidence gap | fail-closed，不 source probing |
| `code_bug` | unexpected exception / `llm_exception` / invariant `ValueError` | fail-closed；safe message only |

### Interaction with max_repair_attempts and regenerate

Provider timeout retry 是“单次 writer/auditor provider request 内部”的 transport hardening；`ChapterOrchestrationPolicy.max_repair_attempts` 仍只控制 audit-driven regenerate。

硬边界：

- `max_provider_http_attempts_per_request = timeout_max_attempts`
- `max_orchestration_attempts_per_chapter = max_repair_attempts + 1`
- 每章理论 HTTP 上限：
  - `<= (max_repair_attempts + 1) * 2 * timeout_max_attempts`
  - 默认 `max_repair_attempts=1`、`timeout_max_attempts=2` 时，每章最多 `8` 次 HTTP attempt。
  - `* 2` 表示每个 orchestration attempt 最多 writer + auditor 两次 `_complete()` 调用；即使 writer/auditor 共享同一 client 实例，每次 `_complete()` 的 retry 计数仍独立。
- timeout retry exhausted 后，本章立即 `failed/llm_timeout`；不得把 timeout 当成 audit failure 再触发 regenerate。
- prompt/audit/fact/code 类问题不得使用 provider timeout retry。

## implementation slices

### Slice A：typed timeout budget config

Objective：扩展现有 typed env config，新增 timeout retry attempts/backoff，不构造 provider、不改 CLI 默认路径。

Allowed files：

- `fund_agent/config/llm.py`
- `tests/config/test_llm_config.py`
- `fund_agent/config/README.md`，仅同步新增 env。

Exact changes：

- 新增 env 常量 `FUND_AGENT_LLM_TIMEOUT_MAX_ATTEMPTS`、`FUND_AGENT_LLM_TIMEOUT_BACKOFF_SECONDS`。
- 在 `LLMProviderConfig` 新增字段 `timeout_max_attempts`、`timeout_backoff_seconds`。
- 新增 `_load_timeout_max_attempts()` 和 `_load_timeout_backoff_seconds()`。
- 默认值分别为 `2` 和 `1.0`。
- 边界校验分别为 `1..3`、`0..30`。
- `repr(config)` 继续隐藏 API key；错误消息只能出现 env var 名和边界，不出现 env value 中的 secret。

Completion signal：

- Config tests 覆盖默认值、自定义合法值、非法边界、非数字、repr 不泄密。

Stop condition：

- 如果必须改变现有 env 名语义或降低 `timeout_seconds` 边界，停止交回 controller。

### Slice B：provider timeout retry/backoff and safe diagnostics

Objective：在 Service provider adapter 内实现 timeout-only bounded retry，并把每次 provider attempt 记录为安全 diagnostic。

Allowed files：

- `fund_agent/services/llm_provider.py`
- `tests/services/test_llm_provider.py`
- `fund_agent/services/__init__.py`，仅当导出 diagnostic/error type 必需。

Exact changes：

- 新增 Service-layer provider attempt diagnostic dataclass，或复用 Slice C 的 Service-layer `ChapterLLMRuntimeDiagnostic`，但 provider 层只能填 `provider_runtime_category` 和 provider-safe 字段。
- `OpenAICompatibleChapterLLMClient.__init__()` 增加可测试 sleep 注入：`sleep: Callable[[float], None] = time.sleep`；测试注入 `lambda _: None`。
- `_complete()` 只接收 `operation="writer" | "auditor"` 作为 provider-local 语义；不接收 `chapter_id`、`fund_code`、`report_year` 或 `repair_attempt_index`。
- `generate_chapter()` / `audit_chapter()` 继续使用现有 Fund Protocol 签名；不得新增 kwargs，不得修改 request/response dataclass。
- 对 `httpx.TimeoutException` 循环直到 `timeout_max_attempts`：
  - 每次 timeout 追加 diagnostic：`provider_runtime_category=timeout`、attempt index、elapsed、error_type。
  - 非最后一次执行 backoff。
  - 最后一次抛 `LLMProviderTimeoutError`，异常对象携带 diagnostics。
- 成功响应仍返回现有 `LLMProviderResponse`；provider-local tests 可检查 success attempt count，但 success diagnostics 不穿越 Fund Protocol。
- 429 / 非 2xx / malformed / network error 追加单次 diagnostic 并抛对应 typed error，不 retry。
- `_safe_http_error_message()` 继续只含 status code 和 request id；timeout/network message 不拼接 underlying exception text。
- 所有 diagnostic `message` 必须使用 `_sanitize_text()` 或等价 helper。

Completion signal：

- Tests prove two initial timeout then success returns response and performs three `_complete()` attempts when configured `timeout_max_attempts=3` and no-op sleep。
- Tests prove timeout exhausted raises `LLMProviderTimeoutError` with carried provider diagnostics count exactly equal config，且 diagnostics 中 chapter identity 和 repair attempt 均为 `None`，不包含 key/prompt/body。
- Tests prove 429/network/malformed/non-2xx do not retry。
- Existing authorization/body mapping tests仍通过。

Stop condition：

- 如果 implementation 需要 logging provider body、request body、prompt 或 draft 才能 debug，停止。

### Slice C：orchestrator diagnostic propagation and taxonomy

Objective：把 provider diagnostics 和 prompt/audit/fact/code 分类聚合进章节结果，让 diagnostic JSON 不靠间接证据判断 root cause。

Allowed files：

- `fund_agent/services/chapter_orchestrator.py`
- `tests/services/test_chapter_orchestrator.py`
- `tests/services/test_fund_analysis_service_llm.py`

Exact changes：

- 在 `ChapterAttemptRecord` 增加 Service-layer safe diagnostics 字段：
  - `runtime_diagnostics: tuple[ChapterLLMRuntimeDiagnostic, ...] = ()`
- 不修改 `write_chapter()`、`audit_chapter_llm()`、Fund request/response 或 Fund Protocol。
- `_run_single_chapter()` 在 writer/auditor provider exception 路径中调用 `_exception_result()` 时传入当前 `attempt_index` 和 `operation`。
- `_exception_result()` 从 typed provider exception 提取 provider diagnostics，并用当前 chapter identity、fund/report year、`attempt_index` enrich；未知异常生成 `chapter_failure_category=code_bug` 的短安全 diagnostic。
- Writer result blocked 时，orchestrator 基于 `writer_result.stop_reason` 构造 `chapter_failure_category`：prompt contract / fact gap / code bug。
- Audit result failed/blocked 时，orchestrator 基于 LLM parse failure issue、repair decision、`needs_more_facts` 构造 `chapter_failure_category`：audit_parse / fact_gap / code_bug。
- 新增分类 helper，例如 `_provider_runtime_category_from_exception()`、`_chapter_failure_category_from_writer_result()`、`_chapter_failure_category_from_audit_result()`、`_chapter_failure_category_from_exception()`。
- `ChapterOrchestrationResult.blocked_reasons` 可继续保持现状；不要把 diagnostics 塞入 blocked reason 文本。

Completion signal：

- Tests prove timeout exception maps to `llm_timeout` and enriched diagnostics contain chapter id/fund/year/current `attempt_index` plus provider attempts。
- Tests prove writer missing required structure / required output marker classify as `prompt_contract`。
- Tests prove LLM audit parse failure classify as `audit_parse` and still respects `max_repair_attempts`。
- Tests prove `needs_more_facts` / missing facts classify as `fact_gap`。
- Tests prove unexpected exception classify as `code_bug` with safe `error_type` and no prompt/key。
- Tests prove retry exhausted does not trigger regenerate and does not increase `ChapterOrchestrationPolicy.max_repair_attempts` loop.
- Tests prove no Fund-layer request/response/protocol diagnostics field was required; existing fake writer/auditor tests with old response constructors still work.

Stop condition：

- If a diagnostic field would require storing full writer draft, full audit raw response, full prompt, provider body or env value, omit the field; if classification then becomes impossible, stop for controller decision.

### Slice D：CLI safe classification surface and validation report

Objective：让 `--use-llm` failure stderr and diagnostic artifact expose the root classification safely enough for Gate B rerun, while preserving fail-closed behavior.

Allowed files：

- `fund_agent/ui/cli.py`
- `tests/ui/test_cli.py`
- Optional README updates listed above if CLI wording or env docs changed.
- Generated validation reports under `reports/mvp-local-acceptance/20260531-provider-timeout-hardening/` after implementation.

Exact changes：

- `_build_llm_clients_or_fail()` continues to build config -> clients -> `ChapterOrchestrationPolicy(max_output_chars=config.max_output_chars)`; retry config stays inside provider config/client, not `extra_payload`。
- `_llm_incomplete_message()` must append a safe first failed chapter summary by traversing `result.llm_orchestration_result.chapter_results` and selecting the first `ChapterRunResult` whose `status != "accepted"`:
  - `first_failed_chapter_id=<chapter_id>`
  - `first_failed_status=<status>`
  - `first_failed_stop_reason=<stop_reason>`
- `_llm_incomplete_message()` may continue to include existing final assembly issue reasons and orchestration/final assembly statuses.
- Runtime provider attempt counts should remain only in diagnostic JSON by default; expose them in CLI stderr only if implementation can prove no coupling/leakage risk.
- The safe classification summary must not require reading prompt/draft/raw provider response.
- If there is no failed chapter result, output `first_failed_chapter=none` rather than traversing attempts.
- CLI stderr must not include prompt/draft/provider response/API key/Authorization。
- Do not change `checklist` options; `checklist --use-llm` remains rejected。

Completion signal：

- CLI tests prove timeout failure stderr includes first failed chapter id/status/stop_reason and `llm_timeout` where applicable, stdout empty, no deterministic report。
- CLI tests prove missing config still fails before Service and still does not call LLM Service。
- CLI tests prove default analyze/checklist do not read LLM config or construct clients。

Stop condition：

- If adding CLI detail risks leaking full draft/prompt/provider body, keep CLI terse and rely on safe diagnostic JSON.

## tests per slice

Slice A:

- `uv run pytest tests/config/test_llm_config.py -q`
- Expected assertions:
  - default attempts/backoff are populated。
  - `FUND_AGENT_LLM_TIMEOUT_MAX_ATTEMPTS=1` and `3` accepted；`0`、`4`、non-int rejected。
  - `FUND_AGENT_LLM_TIMEOUT_BACKOFF_SECONDS=0` and `30` accepted；negative、`31`、non-number rejected。
  - API key value absent from repr/error strings。

Slice B:

- `uv run pytest tests/services/test_llm_provider.py -q`
- Expected assertions:
  - timeout-only retry succeeds when later attempt returns valid payload。
  - timeout exhausted raises `LLMProviderTimeoutError` after exact max attempts and carries provider-level diagnostics with `chapter_id=None`、`fund_code=None`、`report_year=None`、`repair_attempt_index=None`。
  - rate limit / malformed / network / http error attempt count is `1`。
  - no error message or diagnostic contains `Authorization`、`Bearer`、test secret、writer user prompt、provider body。

Slice C:

- `uv run pytest tests/services/test_chapter_orchestrator.py tests/services/test_fund_analysis_service_llm.py -q`
- Expected assertions:
  - provider timeout retry exhausted produces `ChapterRunResult(status="failed", stop_reason="llm_timeout")` with diagnostics `provider_runtime_category=timeout` and `chapter_failure_category=provider_runtime`。
  - orchestrator enriches provider diagnostics with `chapter_id`、`fund_code`、`report_year` and current `attempt_index`。
  - timeout does not create additional repair attempt beyond current orchestration attempt。
  - audit parse failure remains audit-driven and respects `max_repair_attempts`。
  - prompt_contract/fact_gap/code_bug categories are distinguishable without full prompt/draft/response。
  - existing Fund fake clients and response constructors do not need diagnostic fields。

Slice D:

- `uv run pytest tests/ui/test_cli.py -q`
- Expected assertions:
  - `analyze --use-llm` timeout failure exit `1`、stdout empty、stderr includes `first_failed_chapter_id`、`first_failed_status`、`first_failed_stop_reason=llm_timeout`。
  - default `analyze` and `checklist` do not touch LLM config。
  - `checklist --use-llm` remains invalid。

Full local validation before real provider:

- `uv run ruff check .`
- `uv run pytest tests/config/test_llm_config.py tests/services/test_llm_provider.py tests/services/test_chapter_orchestrator.py tests/services/test_fund_analysis_service_llm.py tests/ui/test_cli.py -q`
- `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q`

## validation matrix

| Validation | Command / method | Expected result |
|---|---|---|
| Static style | `uv run ruff check .` | PASS |
| Targeted config/provider/orchestration/CLI tests | `uv run pytest tests/config/test_llm_config.py tests/services/test_llm_provider.py tests/services/test_chapter_orchestrator.py tests/services/test_fund_analysis_service_llm.py tests/ui/test_cli.py -q` | PASS |
| Full regression | `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q` | PASS；coverage gate unchanged |
| Missing config smoke | Temporarily remove required fake/provider env and run `uv run fund-analysis analyze 006597 --report-year 2024 --use-llm` | exit `1`；stdout empty；config error；no deterministic fallback |
| Deterministic default smoke | `uv run fund-analysis analyze 006597 --report-year 2024` | exit `0`；完整 deterministic report；does not read LLM env |
| Checklist default smoke | `uv run fund-analysis checklist 006597 --report-year 2024` | deterministic behavior unchanged |
| Real provider validation | `uv run fund-analysis analyze 006597 --report-year 2024 --use-llm` with existing secret env in shell | classify result；if success, stdout has full 0-7 report；if failure, stdout empty and stderr/diagnostic safe |
| Real provider diagnostic JSON | Controller/worker diagnostic script over `FundAnalysisService.analyze_with_llm()` writing to `reports/mvp-local-acceptance/20260531-provider-timeout-hardening/real-provider-006597-2024-diagnostic.json` | Contains chapter statuses, stop reasons, Service-layer diagnostics with `provider_runtime_category` / `chapter_failure_category`, enriched chapter identity, provider attempt counts for runtime exceptions; contains no prompt/draft/raw provider response/key/header |
| CLI failure summary | Failed `--use-llm` run stderr | Must include first failed chapter id/status/stop_reason; provider attempt counts may remain diagnostic JSON only |
| Secret scan | `rg -n "Authorization|Bearer|FUND_AGENT_LLM_API_KEY|sk-|full provider|writer user|draft markdown" docs/reviews reports/mvp-local-acceptance/20260531-provider-timeout-hardening` plus manual review of any hits | Only safe variable names/test labels/explicit hygiene statements; no secret values or full content |
| Forbidden scope check | `git diff --name-only` | Only allowed implementation/test/doc files plus generated ignored validation reports |
| Golden/quality unchanged | `git diff --name-only -- reports/golden-answers tests/fixtures fund_agent/fund/extraction_score.py fund_agent/services/extraction_score_service.py fund_agent/fund/quality_gate.py` | Empty unless controller explicitly authorized unrelated future gate |

Real provider classification rules:

- `accepted_full_report`: CLI exit `0`, chapters `0-7` present, Service diagnostic `orchestration_status=accepted` and `final_assembly_status=accepted`。
- `provider_runtime_timeout`: any chapter final `stop_reason=llm_timeout` after bounded attempts。
- `provider_runtime_rate_limit`: any chapter final `stop_reason=llm_rate_limited`。
- `provider_runtime_malformed`: any chapter final `stop_reason=llm_malformed_response`。
- `provider_runtime_network`: any chapter final `stop_reason=llm_network_error`。
- `prompt_contract`: writer contract stop reason without provider runtime error。
- `audit_parse`: LLM audit parse failure diagnostic or repair exhausted after parse failure。
- `fact_gap`: `missing_required_facts` / `needs_more_facts` / `fund_type_unknown`。
- `code_bug`: `llm_exception` or unexpected invariant error。
- `unknown`: only if no safe direct evidence maps to the above; must stop for controller decision。

## secret hygiene plan

- Config object keeps `api_key=field(repr=False)`。
- Provider request diagnostics include only counts, status code, request id, model, finish reason, elapsed time, attempt indexes and safe provider runtime category。
- Chapter diagnostics add only chapter id/fund code/report year/attempt index and safe chapter failure category。
- Provider errors never concatenate `response.text`、request JSON、headers、prompt、draft 或 env values。
- CLI stderr includes first failed chapter id/status/stop_reason and existing high-level statuses/issues only; provider attempt counts stay in diagnostic JSON unless proven safe。
- Diagnostic `message` values must use `_sanitize_text()` or equivalent redaction/length cap。
- Tests must include negative assertions for:
  - `Authorization`
  - `Bearer`
  - fake secret values
  - writer user prompt text
  - provider response body text
  - draft markdown text
- Real validation artifact must be reviewed with `rg` before acceptance；any hit that is not a safe variable name or test label blocks the gate。

## stop conditions

- Provider auth/config is missing or invalid in the validation shell：stop and report environment issue separately; do not implement config fallback。
- Timeout retry would require unbounded loops, global sleeps without test injection, or retries for non-timeout categories：stop。
- `ChapterOrchestrationPolicy.max_repair_attempts` and provider retry cannot be bounded by a simple formula：stop。
- Any implementation needs to store prompt/full draft/full provider response/API key/header for diagnostics：stop。
- Real provider validation produces a new category not covered by taxonomy：stop with `unknown` classification and direct evidence。
- Any change touches golden/fixtures/score/quality gate/Host/Agent/dayu/final judgment/template without explicit controller authorization：stop。
- Default deterministic analyze/checklist starts reading LLM env or constructing provider clients：stop。
- Unit tests pass but real validation still exits with `llm_timeout` after bounded attempts：do not broaden scope; report residual provider_runtime_timeout with attempt counts and elapsed budget。

## residual risks

- Bounded retry may reduce transient timeouts but cannot guarantee real provider completion if model latency routinely exceeds configured per-request timeout。
- Default `timeout_max_attempts=2` increases worst-case explicit `--use-llm` runtime. This is acceptable only because `--use-llm` is opt-in and bounded。
- Successful retry after a timeout may still be followed by prompt_contract or audit_parse failure; this gate must classify that next blocker, not solve all downstream LLM quality issues。
- Provider-specific rate-limit headers are intentionally not consumed in this gate; retrying 429 is deferred because it needs separate quota/backoff policy。
- Runtime diagnostics improve root-cause classification but are not a score-loop implementation and must not be consumed by golden/readiness/quality gates。
- Real provider smoke remains network/external-service dependent；failure classification is evidence for next gate, not release readiness。

## completion report format

Implementation worker final report must use this format:

```markdown
Self-check: pass | blocked - <reason>

Gate: MVP provider runtime timeout hardening implementation gate
Role: implementation worker, not controller

Changed files:
- <path>: <short purpose>

Implemented slices:
- Slice A: complete | blocked - <reason>
- Slice B: complete | blocked - <reason>
- Slice C: complete | blocked - <reason>
- Slice D: complete | blocked - <reason>

Validation:
- `uv run ruff check .`: PASS/FAIL
- `uv run pytest tests/config/test_llm_config.py tests/services/test_llm_provider.py tests/services/test_chapter_orchestrator.py tests/services/test_fund_analysis_service_llm.py tests/ui/test_cli.py -q`: PASS/FAIL
- `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q`: PASS/FAIL
- deterministic analyze/checklist smoke: PASS/FAIL/not run with reason
- missing-config `--use-llm` smoke: PASS/FAIL/not run with reason
- real provider `006597 / 2024 --use-llm`: accepted_full_report | provider_runtime_timeout | provider_runtime_rate_limit | provider_runtime_malformed | provider_runtime_network | prompt_contract | audit_parse | fact_gap | code_bug | unknown | not run with reason

Real provider evidence:
- CLI stdout path:
- CLI stderr path:
- diagnostic JSON path:
- safe classification:

Secret hygiene:
- API key/header/full prompt/full draft/full provider response leaked: no | yes - <path/reason>
- secret scan command/result:

Scope guard:
- default deterministic analyze/checklist unchanged: yes/no
- golden/fixtures/score/quality gate unchanged: yes/no
- Host/Agent/dayu untouched: yes/no

Residual risks:
- <classified residual with owner/next gate>

Stop status:
- complete | blocked - <reason>
```

## worker self-check

- Current gate / role：当前是 `MVP provider runtime timeout hardening plan gate`；本文作者是 planning worker，不是 controller，不进入 implementation。
- Source of truth：已读取 `AGENTS.md`、startup/control docs、Gate A/Gate B/rerun judgments、两份 diagnostic JSON、provider/config/orchestrator/CLI/tests 当前代码。
- Scope boundary：本轮只修订本 plan artifact；后续 implementation allowed files 已列出；不触碰现有 dirty runtime code、control docs、golden/fixtures/score/quality gate。
- Stop conditions：当前无 blocking open question；provider/auth 不作为 blocker；实现前必须由 controller 进入后续 gate。
- Evidence and validation：本 plan 已给出 direct evidence、contract、slices、tests、validation matrix、secret hygiene 和 completion report format。
- Next action：交回 controller 做 plan review / judgment；不得 commit、push、PR 或自行实现。
