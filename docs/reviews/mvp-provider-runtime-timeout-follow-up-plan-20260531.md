# MVP provider runtime timeout follow-up plan

日期：2026-05-31

Gate：`MVP provider runtime timeout follow-up gate`

角色：Gateflow planning worker，不是 implementation worker。

## 1. Goal

在 provider config/auth 已验证可用、writer/auditor contract 与 L1 calibration 已本地接受的前提下，处理当前 Gate B authoritative CLI blocker：

- 命令：`fund-analysis analyze 006597 --report-year 2024 --use-llm`
- 当前结果：exit `1`，stdout empty，无 deterministic fallback。
- 主 blocker：chapter `1` / `llm_timeout` / subcategory `unknown`。
- 不是 provider config/auth；不得回退到 provider_config / provider_auth。

本 gate 的目标不是放松 writer/auditor contract，也不是简单把 timeout 拉满，而是让 provider runtime timeout 的发生点、prompt/runtime cost、预算耗尽形态和下一最小入口可审计。如果 timeout 稳定后真实 provider 能跑出完整 `0-7` 章，则 Gate B 可进入 smoke acceptance；若仍失败，必须输出唯一主 blocker、chapter/phase/operation 定位、prompt/cost 标量、attempt/budget 摘要和下一最小入口。

## 2. Direct Evidence Read

- `docs/current-startup-packet.md`：当前 authoritative CLI blocker 是 chapter `1` / `llm_timeout`；补充 service diagnostic 在另一轮调用中接受 chapters 1-2 后卡在 chapter 3 `programmatic_audit` / `programmatic:C2`。
- `docs/implementation-control.md`：下一入口为 `MVP provider runtime timeout follow-up gate`，分类 `heavy`；Gate C score-loop 只是 design-only，不能作为 readiness/golden/quality pass。
- `docs/reviews/mvp-programmatic-audit-l1-calibration-controller-judgment-20260531.md`：L1 calibration local accepted；真实 CLI smoke 仍以 chapter 1 `llm_timeout` 为唯一主 blocker；C2 是 timeout-free 后的 secondary diagnostic。
- `fund_agent/config/llm.py`：已有 typed env knobs：`FUND_AGENT_LLM_TIMEOUT_SECONDS` 默认 `60`、最大 `300`；`FUND_AGENT_LLM_TIMEOUT_MAX_ATTEMPTS` 默认 `2`、范围 `1..3`；`FUND_AGENT_LLM_TIMEOUT_BACKOFF_SECONDS` 默认 `1.0`、范围 `0..30`；`FUND_AGENT_LLM_MAX_OUTPUT_CHARS` 默认 `12000`。
- `fund_agent/services/llm_provider.py`：OpenAI-compatible adapter 已只对 `httpx.TimeoutException` 做有界 retry；rate limit / malformed / network / non-2xx 不重试；provider-local diagnostic 不含 chapter identity、prompt、draft、body 或 secret。
- `fund_agent/services/chapter_orchestrator.py`：Service 已把 provider diagnostics enrich 到 chapter/fund/year/attempt，并把 timeout 映射到 stop_reason `llm_timeout`、failure_category `llm_timeout`；但当前 `serialize_chapter_prompt_contract_diagnostics()` 只输出 prompt-contract matrix，不输出 runtime attempt/budget matrix，也不输出脱敏 prompt/runtime cost 标量。
- `fund_agent/ui/cli.py`：CLI incomplete message 已输出 first failed chapter/status/stop_reason/category/subcategory；但 timeout 场景无法从 stderr 判断失败 operation、provider attempts、configured budget 或 elapsed summary。
- 相关 tests 已覆盖 typed config bounds、timeout-only retry、timeout diagnostic enrich、CLI fail-closed/no fallback；缺口是 provider runtime diagnostic serialization / CLI safe timeout summary / smoke evidence shape。

## 3. Non-goals And Hard Constraints

- 不改 golden / fixtures / existing score / quality gate / final judgment / snapshot / promotion state。
- 不进入 Gate 5，不创建 Host/Agent，不引入 `dayu.host` 或 `dayu.engine`。
- 不修改 writer/auditor 安全边界：证据锚点、ITEM_RULE、candidate facet、交易建议、E2 deferred、missing semantics、L1 anchor proximity 都不得放松。
- 不把 weak evidence、missing evidence、candidate facet 或 provider timeout 包装成 pass。
- 不记录 API key、Authorization header、Bearer token、完整 prompt、完整 draft、完整 provider response、raw audit response。
- 不改变默认 deterministic `fund-analysis analyze` / `fund-analysis checklist` 行为。
- 不改 PR 状态，不 push，不 merge，不 release。
- 不修改 provider config/auth 结论；除非 env load 本身失败，否则不得把当前问题归类回 provider_config/provider_auth。
- 不做 provider fallback、多供应商 fallback、writer/auditor 分开模型、非 timeout retry 或并发章节生成；这些都需要单独 gate。

## 4. Root Cause Evidence To Gather

Implementation must add safe observability so controller can answer these questions from local artifacts without raw prompt/response:

1. Timeout operation：chapter 1 timeout 发生在 `writer` 还是 `auditor`。
2. Chapter repair attempt：发生在 chapter repair attempt `0` 还是 regenerate attempt。
3. Provider attempt budget：`provider_attempt_index` 序列、`provider_max_attempts`、是否每次都是 `timeout`。
4. Elapsed budget：每次 attempt 的 `elapsed_ms`，以及本章 timeout diagnostics 的 safe total/maximum elapsed summary。
5. Prompt/runtime cost：记录脱敏规模而非文本：
   - writer/auditor provider-bound `system_prompt_chars`
   - writer/auditor provider-bound `user_prompt_chars`
   - approximate token count, derived locally from char length by a fixed conservative heuristic such as `ceil(chars / 4)` and clearly labeled approximate
   - `allowed_fact_count`
   - `allowed_anchor_count`
   - `max_output_chars`
6. Configured runtime budget：记录本次 smoke 使用的 `timeout_seconds`、`timeout_max_attempts`、`timeout_backoff_seconds`、`max_output_chars`，只记录数值，不记录 base URL、model、key。
7. HTTP/provider scalar context：只允许 status code、safe request id、finish reason、response char count 等既有安全标量；timeout 通常为空。
8. Orchestration effect：stdout empty、no deterministic fallback、final assembly incomplete、chapters accepted/failed/skipped matrix。

Do not gather:

- system/user prompt、chapter draft、provider response body、raw audit text、Authorization header、API key、base URL、model permission details。

## 5. Implementation Decisions

### 5.1 Runtime diagnostic serialization

Add a Service-owned safe serializer for provider runtime diagnostics.

Preferred approach:

- Add `serialize_chapter_runtime_diagnostics(orchestration_result)` in `fund_agent/services/chapter_orchestrator.py`.
- Keep `serialize_chapter_prompt_contract_diagnostics()` behavior compatible for existing prompt-contract evidence.
- The new serializer returns only safe scalar fields:
- `schema_version`
- `fund_code`, `report_year`, `orchestration_status`
- `first_failed`: `chapter_id`, `status`, `stop_reason`, `category`, `subcategory`, `runtime_operation`, `repair_attempt_index`, `provider_attempt_count`, `provider_max_attempts`, `provider_runtime_categories`, `system_prompt_chars`, `user_prompt_chars`, `approx_prompt_tokens`, `allowed_fact_count`, `allowed_anchor_count`, `max_output_chars`
- `chapter_runtime_matrix`: per chapter `chapter_id`, `status`, `stop_reason`, `failure_category`, `failure_subcategory`, `attempt_count`, and per runtime diagnostic `operation`, `repair_attempt_index`, `provider_attempt_index`, `provider_max_attempts`, `provider_runtime_category`, `chapter_failure_category`, `elapsed_ms`, `status_code`, `request_id`, `finish_reason`, `response_chars`, `error_type`, `system_prompt_chars`, `user_prompt_chars`, `approx_prompt_tokens`, `allowed_fact_count`, `allowed_anchor_count`, `max_output_chars`
- Include runtime diagnostics stored both on `ChapterRunResult.runtime_diagnostics` and `ChapterAttemptRecord.runtime_diagnostics`.
- Do not include `model_name` unless controller explicitly needs it and review confirms it cannot leak a configured secret-like deployment name. Default plan decision: omit `model_name` from serialized evidence.
- Do not include the generic `message` field in the runtime serializer. Existing `ChapterLLMRuntimeDiagnostic.message` can be provider-local safe text in some cases, but it can also be built from writer/auditor/programmatic issue text or LLM audit line messages. For this gate, precise timeout classification must rely on allowlisted scalar fields only.
- If a future gate needs a textual provider runtime summary, it must add a separate allowlisted enum/fixed-summary field with tests proving writer/auditor/programmatic issue messages cannot flow into it. This gate must not serialize `message`.

### 5.2 Runtime-cost diagnostic source

Add prompt/runtime cost scalar fields at provider-call diagnostic creation time without storing prompt text.

Preferred approach:

- Extend `ChapterLLMRuntimeDiagnostic` with optional scalar fields:
  - `system_prompt_chars`
  - `user_prompt_chars`
  - `approx_prompt_tokens`
  - `allowed_fact_count`
  - `allowed_anchor_count`
  - `max_output_chars`
- In `OpenAICompatibleChapterLLMClient.generate_chapter()`, pass a provider cost context into `_complete()`:
  - `system_prompt_chars=len(request.system_prompt)`
  - `user_prompt_chars=len(request.user_prompt)`
  - `approx_prompt_tokens=ceil((system_prompt_chars + user_prompt_chars) / 4)`
  - `allowed_fact_count=None` unless the request type exposes it; writer request has `required_anchor_ids` but not allowed fact ids, so do not infer facts from prompt text
  - `allowed_anchor_count=len(request.required_anchor_ids)`
  - `max_output_chars=request.max_output_chars`
- In `OpenAICompatibleChapterLLMClient.audit_chapter()`, compute cost on the actual provider-bound user prompt returned by `_audit_user_prompt(request)`, not just `request.user_prompt`:
  - `system_prompt_chars=len(request.system_prompt)`
  - `user_prompt_chars=len(provider_user_prompt)`
  - `approx_prompt_tokens=ceil((system_prompt_chars + user_prompt_chars) / 4)`
  - `allowed_fact_count=len(request.allowed_fact_ids)`
  - `allowed_anchor_count=len(request.allowed_anchor_ids)`
  - `max_output_chars=None`
- Do not expose raw prompt, draft, raw audit response, provider response body, model, base URL or key in any diagnostic.
- Keep char/token values as diagnostic-only evidence. They must not change provider payload, retry decisions, audit pass/fail or deterministic output.
- Tests must prove the char counts match fake prompt lengths while prompt sentinel text is absent from diagnostics and CLI stderr.

### 5.3 CLI safe timeout summary

Extend `_llm_incomplete_message()` / `_first_failed_chapter_summary()` in `fund_agent/ui/cli.py` only for safe scalar timeout summary.

Required stderr additions when first failed chapter has runtime diagnostics:

- `first_failed_runtime_operation=<writer|auditor|unknown>`
- `first_failed_provider_attempts=<observed>/<max|unknown>`
- `first_failed_provider_runtime_category=<timeout|...|unknown>`
- `first_failed_elapsed_ms_max=<number|unknown>`
- `first_failed_prompt_chars=<system+user|unknown>`
- `first_failed_approx_prompt_tokens=<number|unknown>`

Keep existing fields unchanged:

- `first_failed_chapter_id`
- `first_failed_status`
- `first_failed_stop_reason`
- `first_failed_category`
- `first_failed_subcategory`

The CLI must still exit `1` with stdout empty for incomplete `--use-llm`; no deterministic fallback.
The CLI summary must not print runtime diagnostic `message` or any writer/auditor/programmatic issue text.

### 5.4 Timeout budget and retry

Use existing config bounds first. Do not add new provider config variables in this gate unless implementation discovers the existing knobs cannot represent the required bounded smoke.

Decisions:

- Keep chapters sequential and `fail_fast=True`; no concurrency. Parallel provider calls would make timeout/rate behavior harder to attribute and may increase provider pressure.
- Keep timeout retry timeout-only. Do not retry rate limit, malformed response, network error, non-2xx or audit/programmatic failures.
- Keep max provider attempts bounded by existing config range `1..3`; no infinite retry.
- Do not change deterministic defaults.
- Do not change `max_repair_attempts` as a timeout mitigation; repair/regenerate is for contract/audit failures, not provider transport timeout.
- Controller validation may run one current-config smoke and one explicitly bounded smoke using existing env knobs. Do not start by maxing out every knob. Recommended first bounded smoke:
  - `FUND_AGENT_LLM_TIMEOUT_SECONDS=120`
  - `FUND_AGENT_LLM_TIMEOUT_MAX_ATTEMPTS=2`
  - `FUND_AGENT_LLM_TIMEOUT_BACKOFF_SECONDS=2`
  These values are validation-time inputs, not new code defaults.

If the explicitly bounded smoke still times out at chapter 1 writer attempt 0 after all provider attempts, classify the remaining blocker as provider runtime capacity/latency only after runtime-cost diagnostics are present. Do not infer prompt token size or provider throughput without those diagnostics.

### 5.5 Failure taxonomy

Use existing top-level categories:

- `llm_timeout`: timeout exhausted, including chapter 1 authoritative blocker.
- `provider_runtime`: rate limit, malformed, network, HTTP/non-2xx runtime failures.
- `prompt_contract`: writer/auditor output contract failures, including C2 after timeout-free runs if applicable.
- `audit_parse`: auditor line protocol parse failure.
- `audit_rule_too_strict`: calibrated audit rule false positive only when same-source evidence proves the output is acceptable.
- `fact_gap`: missing structured facts / dependency skips / unsupported evidence gaps.
- `code_bug`: unexpected exceptions or impossible state.

Do not overload prompt-contract `failure_subcategory` for timeout. Runtime precision should come from `runtime_operation`, provider attempt counts and runtime categories. If reviewers require a subcategory, add a separate runtime-only safe field such as `runtime_subcategory=timeout_budget_exhausted`, not prompt-contract subcategory reuse.

### 5.6 C2 secondary diagnostic handling

Do not fix C2 in this gate. Carry it only as a secondary diagnostic after timeout is no longer first blocker.

If validation reaches chapter 3 `programmatic_audit` / `programmatic:C2`, stop provider-runtime work and write controller judgment with next entry:

- `MVP programmatic audit C2 calibration gate`

Do not weaken C2, evidence support, ITEM_RULE or candidate facet boundaries in this gate.

### 5.7 Prompt slimming

Do not perform prompt slimming in this gate. Runtime-cost diagnostics may later justify a separate prompt slimming gate. That future gate must preserve all safety rules, evidence constraints and fail-closed semantics.

## 6. Affected Files For Implementation

Expected implementation files:

- `fund_agent/services/chapter_orchestrator.py`
  - Add runtime diagnostic serializer and helper extraction functions.
  - Preserve existing dataclass contracts unless a typed helper is strictly needed.
- `fund_agent/services/llm_provider.py`
  - Add provider-bound prompt/runtime cost scalar diagnostics without changing provider payload or retry behavior.
- `fund_agent/ui/cli.py`
  - Add safe runtime summary fields to incomplete LLM stderr.
- `tests/services/test_chapter_orchestrator.py`
  - Cover runtime serializer for chapter-level diagnostics and attempt-level diagnostics.
  - Assert no prompt/draft/raw response/key/header fields appear.
- `tests/ui/test_cli.py`
  - Cover timeout incomplete stderr includes operation/attempt/runtime category and excludes secrets/prompts/body.
- `tests/services/test_llm_provider.py`
  - Cover writer/auditor prompt/runtime cost scalar diagnostics and negative prompt/body/key/header leakage assertions.
- `tests/config/test_llm_config.py`
  - Add or adjust tests only if implementation changes timeout config bounds/defaults; default plan expects no config change.

Conditional docs:

- If code changes CLI-visible stderr fields or LLM env behavior materially, update `README.md`, `fund_agent/config/README.md` and `tests/README.md` in the implementation gate.
- If only internal diagnostic serializer/test evidence changes and user-facing commands/env remain unchanged, no README update is required; record this decision in implementation evidence.

Files explicitly out of scope:

- golden / fixtures / score / quality gate files
- `docs/design.md` unless a controller later requires design-truth update
- `docs/fund-analysis-template-draft.md`
- `fund_agent/host`, `fund_agent/agent`, dayu integration

## 7. Implementation Slices

### Slice 1: Safe runtime diagnostic serializer

Implement `serialize_chapter_runtime_diagnostics()` and helper functions.

Acceptance assertions:

- Includes first failed chapter runtime operation and provider attempts for timeout.
- Includes diagnostics from both `run.runtime_diagnostics` and `attempt.runtime_diagnostics`.
- Omits prompt, draft, raw response, raw audit response, API key, Authorization, Bearer and provider body.
- Omits generic diagnostic `message` even when a diagnostic carries text that contains writer issue text, auditor LLM line text, programmatic issue text, raw audit sentinel text, prompt/draft/body-like strings or secret-like strings.
- Includes prompt/runtime cost scalars when available and degrades to `None`/`unknown` when absent.
- Does not change orchestration status or accepted/failed decisions.

### Slice 2: Provider-bound runtime-cost diagnostics

Extend provider diagnostics with prompt/runtime cost scalars.

Acceptance assertions:

- Writer timeout diagnostics include system/user prompt char counts, approximate prompt tokens, allowed anchor count and max_output_chars.
- Auditor timeout diagnostics compute user prompt chars from the actual provider-bound audit prompt including draft/context, but do not store the text.
- Diagnostics do not include raw prompt, draft, provider body, raw audit text, model name, base URL, API key, Authorization or Bearer.
- Timeout retry behavior stays timeout-only and bounded by existing config.

### Slice 3: CLI first-failed runtime summary

Extend CLI incomplete message to append safe runtime scalar fields.

Acceptance assertions:

- Timeout fake service exits `1`, stdout empty.
- Existing first failed fields remain present.
- Runtime fields are present when diagnostics exist.
- Runtime fields degrade to `unknown` when diagnostics are absent.
- Prompt char/token fields are present when diagnostics exist and degrade to `unknown` when absent.
- No deterministic fallback and no secret/prompt/body/raw audit/draft-derived message leakage.

### Slice 4: Evidence script shape

No production script is required. Implementation evidence should include the exact safe diagnostic capture snippets that controller can run later, using the new serializer. Snippets must write only redacted JSON/stderr/exitcode under a gate-specific reports directory.

Acceptance assertions:

- The snippet imports only public Service/CLI helpers needed for configured provider clients and safe serializers.
- The snippet does not print env values, base URL, model, prompts, drafts or raw responses.
- The report JSON can produce a per-chapter accepted/failed/skipped matrix and first-failed runtime summary.
- Evidence snippets may record configured timeout/backoff/output-char knob values as controller-owned scalar metadata, but serializer should not read or expose provider config objects, base URL, model name, API key or full headers.

## 8. Test Plan

Targeted tests:

- `uv run pytest tests/services/test_chapter_orchestrator.py -q`
- `uv run pytest tests/services/test_llm_provider.py tests/config/test_llm_config.py -q`
- `uv run pytest tests/ui/test_cli.py -q`

Required full validation for controller after implementation:

- `uv run ruff check .`
- `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q`
- deterministic analyze smoke:
  - `uv run fund-analysis analyze 006597 --report-year 2024`
- deterministic checklist smoke:
  - `uv run fund-analysis checklist 006597 --report-year 2024`
- missing-config `--use-llm` fail-closed smoke with LLM env unset:
  - exit `1`
  - stdout empty
  - no deterministic fallback
- real provider current-config smoke:
  - `uv run fund-analysis analyze 006597 --report-year 2024 --use-llm`
- if current-config smoke still times out, one bounded runtime smoke using existing env knobs:
  - `FUND_AGENT_LLM_TIMEOUT_SECONDS=120`
  - `FUND_AGENT_LLM_TIMEOUT_MAX_ATTEMPTS=2`
  - `FUND_AGENT_LLM_TIMEOUT_BACKOFF_SECONDS=2`
- service-level safe diagnostic rerun using `serialize_chapter_runtime_diagnostics()` and, when relevant, `serialize_chapter_prompt_contract_diagnostics()`.
- secret leak scan over current gate docs/reports/control snippets.
- content-level negative assertion over diagnostic JSON/stderr: injected sentinel strings representing `system_prompt`, `user_prompt`, `draft_markdown`, `raw_response`, raw audit text, provider body, writer/auditor issue text, Authorization/Bearer/key-like values must be absent.

Do not run real provider in pytest. Live provider commands are controller validation only.

## 9. Smoke Evidence Requirements

Write evidence under:

- `reports/mvp-local-acceptance/20260531-provider-runtime-timeout-follow-up/`

Required files:

- CLI current-config stdout/stderr/exitcode.
- CLI bounded-runtime stdout/stderr/exitcode if current-config still times out.
- Service safe runtime diagnostic JSON/stderr/exitcode for the authoritative or most informative rerun.
- Optional prompt-contract diagnostic JSON only if timeout-free run reaches prompt/audit blocker.
- Implementation evidence artifact.
- Code review and deepreview artifacts.
- Controller judgment artifact.

Evidence must record:

- command name and high-level env knob values used for timeout/backoff/output chars; no key/base URL/model secret-like values.
- stdout byte count and stderr first-failed summary.
- chapter matrix for chapters 1-6; final assembly state; report present/absent.
- for runtime failures: operation, repair attempt, provider attempts observed/max, runtime categories, elapsed ms summary.
- for runtime-cost evidence: system/user prompt chars, approximate prompt tokens, allowed fact count, allowed anchor count, max_output_chars.
- secret scan command and result.

Evidence must not record:

- API key, Authorization header, Bearer token.
- full provider response, full prompt, full draft, raw audit response.
- generic runtime diagnostic `message`, writer issue message, auditor LLM issue message, programmatic issue message, provider body text or draft-derived snippets.
- weak evidence repackaged as pass.

## 10. Review Gates

Plan review must verify:

- The plan stays on chapter 1 `llm_timeout` and does not revisit provider config/auth.
- Runtime diagnostics are safe and sufficient to identify writer vs auditor and provider attempt budget exhaustion.
- The plan does not loosen writer/auditor/audit/evidence safety boundaries.
- Existing deterministic behavior and quality/golden/score boundaries remain untouched.

Code review must verify:

- No secret/prompt/body leakage in new serializer, CLI stderr, tests or artifacts.
- Runtime serializer and CLI summary do not output diagnostic `message`; tests include negative canary strings for writer/auditor/programmatic/raw audit text.
- Provider diagnostics include prompt/runtime cost scalars without storing prompt text, draft text, model/base URL/key/header or provider body.
- No retry broadening beyond timeout-only.
- No concurrency introduction.
- No changes to deterministic analyze/checklist outputs.
- No C2 or audit-rule relaxation hidden inside timeout work.

## 11. Pass / Blocked / Stop Criteria

Pass for Gate B smoke acceptance:

- `fund-analysis analyze 006597 --report-year 2024 --use-llm` exits `0`.
- stdout contains complete chapters `0-7`.
- generated body contains evidence anchors and chapter audit status according to current Route C contracts.
- no deterministic fallback.
- secret scan passes.

Local accepted but Gate B still blocked:

- Implementation validation passes and diagnostics safely classify the blocker.
- Authoritative real provider smoke still exits `1`.
- Controller judgment names exactly one primary blocker with chapter/phase/operation/attempt budget:
  - e.g. `chapter 1 writer timeout_budget_exhausted after 3/3 provider attempts`.
- Next smallest entry is provider-runtime-specific if timeout remains first blocker, or `MVP programmatic audit C2 calibration gate` if timeout-free run reaches chapter 3 C2.

Stop immediately and write blocked judgment if:

- Dirty scope changes outside approved implementation files cannot be separated.
- Provider config unexpectedly fails to load; report as environment preflight issue, but do not rewrite history as provider_auth/config unless same-source evidence proves it.
- Any validation leaks secret/prompt/draft/provider body.
- Any implementation requires modifying golden/fixtures/score/quality gate/Host/Agent/dayu/default deterministic behavior.
- Real provider validation reaches C2; stop timeout gate and hand off to narrow C2 calibration rather than mixing fixes.

## 12. Completion Report Format

Implementation worker should report:

- Files changed.
- Runtime diagnostic fields added.
- Local validation commands and results.
- Whether README/docs were updated or why not.
- Any residual risk.

Controller judgment should report:

- Branch and dirty-scope summary.
- Plan/review/implementation/review artifact paths.
- Validation table.
- Authoritative CLI smoke result.
- Safe runtime diagnostic summary.
- Secret scan result.
- Final decision: Gate B pass, local accepted but blocked by timeout, or blocked by next precise category.
