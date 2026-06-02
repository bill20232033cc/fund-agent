# MVP Ch2 auditor timeout diagnostic design plan review — MiMo

## Reviewed Target

- **Plan**: `docs/reviews/mvp-ch2-auditor-timeout-diagnostic-design-plan-20260603.md`
- **Gate**: `MVP Ch2 auditor timeout diagnostic design gate`
- **Classification**: `heavy`
- **Scope**: design/review only; no implementation, no live provider calls

## Assumptions Tested

1. Same-source evidence: Ch2 is the only current default-run auditor timeout blocker; Ch4/Ch5/Ch6 accepted; Ch3 is separate `prompt_contract` / `programmatic:C2`.
2. Existing code/config supports explicit auditor-only timeout override via `FUND_AGENT_LLM_AUDITOR_TIMEOUT_SECONDS` without implementation.
3. 120s auditor-only diagnostic is bounded, default-preserving, and safe.
4. Service/Host/Agent/Fund ownership boundaries are preserved.
5. Stop conditions, interpretation matrix, artifact handling and secret-safety are sufficient.

## Findings

### 001-unfixed-low-host-timeout-doubling-not-quantified

- **位置**: Slice C command constraints; Design Decision; Residual Risks
- **问题类型**: 最佳实践偏离
- **当前写法**: Plan says "Keep backoff/default output limits unchanged" and acknowledges "Higher auditor timeout can increase wall-clock time and provider cost" as a residual risk, but does not quantify the actual host timeout impact.
- **反例/失败场景**: Implementation agent or controller may not realize the host timeout doubles from ~1440s to ~2880s (48 minutes) for a single diagnostic run.
- **为什么有问题**: `derive_host_timeout_seconds()` in `execution_contract.py:406-434` computes `max(1, (writer + auditor + repair) * attempts * chapter_count)`. With auditor=120, writer=60, repair=60 (fallback), attempts=2, chapters=6: `(60+120+60)*2*6 = 2880s`. Current default: `(60+60+60)*2*6 = 1440s`. This is a meaningful wall-clock increase for a diagnostic run.
- **直接证据**: `execution_contract.py:428-433` — formula `(writer + auditor + repair) * attempts * chapter_count`. `llm.py:107-111` — auditor falls back to `timeout_seconds` (60), writer stays at `timeout_seconds` (60).
- **影响**: Not a safety issue (bounded under 300s per-request cap and 2880s host cap), but controller should be aware of wall-clock cost when authorizing.
- **建议改法和验证点**: Add a note in Slice C or Residual Risks: "Host timeout increases from ~1440s to ~2880s for this diagnostic run; per-request timeout remains bounded at 120s."
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

### 002-unfixed-low-repair-timeout-implicit-behavior

- **位置**: Design Decision — "Default-preserving diagnostic budget"; Slice C command constraints
- **问题类型**: 契约缺失
- **当前写法**: "Set only `FUND_AGENT_LLM_AUDITOR_TIMEOUT_SECONDS=120`. Do not set `FUND_AGENT_LLM_REPAIR_TIMEOUT_SECONDS`."
- **反例/失败场景**: Implementation agent may not realize that repair timeout for auditor operations is determined by the `_effective_timeout_seconds()` fallback chain, not by the auditor timeout.
- **为什么有问题**: In `llm_provider.py:637-641`, `operation == "auditor"` always returns `config.auditor_timeout_seconds`. But repair timeout falls back to writer timeout (`llm.py:112-113`: `_load_repair_timeout_seconds(env, fallback=writer_timeout_seconds)`), which in turn falls back to `timeout_seconds=60`. So `repair_timeout_seconds=60` in the runtime budget, even though auditor is 120. This is correct behavior (we're only testing auditor), but the plan doesn't clarify the implicit fallback chain.
- **直接证据**: `llm.py:102-113` — writer→timeout_seconds fallback, auditor→timeout_seconds fallback, repair→writer fallback. `llm_provider.py:637-641` — `_effective_timeout_seconds` returns `config.auditor_timeout_seconds` for auditor operation.
- **影响**: No safety issue; behavior is correct. But the implicit chain could confuse a reviewer verifying that only auditor timeout changes.
- **建议改法和验证点**: Add one sentence: "Repair timeout remains at writer fallback (60s) since `FUND_AGENT_LLM_REPAIR_TIMEOUT_SECONDS` is not set; this is correct as the diagnostic only targets auditor."
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

### 003-unfixed-low-timeout-root-cause-hint-unspecified

- **位置**: Slice D expected safe evidence fields; Interpretation matrix
- **问题类型**: 契约缺失
- **当前写法**: Slice D lists `timeout_root_cause_hint` as an expected field. Interpretation matrix covers "Ch2 accepted" and "Ch2 still times out" but doesn't specify expected hint values.
- **反例/失败场景**: Current baseline shows `timeout_root_cause_hint: "small_prompt_provider_timeout"` at 60s. If Ch2 accepts at 120s, the hint field may be absent or changed. If Ch2 still times out at 120s, the hint behavior is unspecified.
- **为什么有问题**: The hint is diagnostic-only and doesn't affect safety, but specifying expected values would make the interpretation matrix more precise for controller judgment.
- **直接证据**: `summary.json` runtime_diagnostics.first_failed — `timeout_root_cause_hint: "small_prompt_provider_timeout"`.
- **影响**: No safety or implementation risk. Minor clarity gap for post-run evidence extraction.
- **建议改法和验证点**: In Interpretation matrix, note: "If Ch2 accepts, `timeout_root_cause_hint` may be absent. If Ch2 still times out at 120s, hint may change from `small_prompt_provider_timeout`."
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

## Open Questions

None. All review focus areas have sufficient evidence.

## Residual Risks

| Risk | Status | Tracking |
|---|---|---|
| Provider latency variance may make one `120s x2` result non-repeatable | accepted; already in plan Residual Risks | controller judgment |
| Higher auditor timeout doubles host wall-clock from ~1440s to ~2880s | accepted; bounded and safe | controller awareness |
| Ch2 may reveal content/audit blockers only after timeout is removed | accepted; already in plan Residual Risks | Ch2 content/audit calibration gate |
| Ch3 remains independently blocking final assembly | accepted; already in plan Residual Risks | Ch3 contract/audit calibration gate |

## Architecture Boundary Check

- **Service/Host boundary**: Preserved. Host receives only `host_timeout_seconds` scalar derived from Service runtime plan. Host does not inspect auditor timeout directly. `execution_contract.py:284` — `host_timeout_seconds: int` is the only Host-visible deadline field.
- **Service/Agent boundary**: Preserved. No Agent layer changes. Plan does not touch `fund_agent/agent` or `fund_agent/fund` audit rules.
- **Provider construction boundary**: Preserved. `build_fund_llm_execution_request()` in `fund_analysis_service.py:919-990` reads typed config and constructs runtime budget; env var override flows through existing `LLMProviderConfig` → `ProviderRuntimeBudget` → provider adapter.
- **Host business-agnostic boundary**: Preserved. `fund_analysis_service.py:974` — `derive_host_timeout_seconds()` produces a scalar; Host does not receive `auditor_timeout_seconds` directly.
- **No extra_payload leakage**: Preserved. All timeout values flow through typed `ProviderRuntimeBudget` fields.

## Command Safety Check

- **Bounded**: 120s is within `(0, 300]` config range (`llm.py:24`, `_MAX_TIMEOUT_SECONDS = 300.0`).
- **Default-preserving**: Only `FUND_AGENT_LLM_AUDITOR_TIMEOUT_SECONDS` is set; `FUND_AGENT_LLM_TIMEOUT_SECONDS`, `FUND_AGENT_LLM_WRITER_TIMEOUT_SECONDS`, `FUND_AGENT_LLM_REPAIR_TIMEOUT_SECONDS` are not set. Code defaults remain unchanged.
- **No PASS-only/split-audit**: Plan explicitly prohibits these (`llm.py` lines 161-163).
- **No auditor relaxation**: Auditor rules, parser, prompt contract unchanged.
- **No score/golden/quality/readiness changes**: Plan explicitly prohibits these.
- **No provider model/URL/key changes**: Plan explicitly prohibits these.

## Secret Safety

This review artifact contains no API key, Authorization header, Bearer token, cookie, password, provider base URL, model name, raw prompt, raw response, or report body. Environment variable names (`FUND_AGENT_LLM_AUDITOR_TIMEOUT_SECONDS`) are policy identifiers, not secret values.

## Reviewer Self-Check

- [x] Reviewed target, scope, source of truth and assumptions tested are written.
- [x] Findings are evidence-based, adversarial, actionable, and have no style/nit/speculation.
- [x] Open questions, residual risks and tracking destination are separated from findings.
- [x] Conclusion is one of `pass` / `pass-with-risks` / `fail`.
- [x] Output path matches user-specified artifact name.

## Conclusion

**PASS.**

The plan is well-scoped, evidence-based, and correctly identifies that no implementation is needed for the next evidence slice. The existing `FUND_AGENT_LLM_AUDITOR_TIMEOUT_SECONDS` env var flows through `LLMProviderConfig` → `ProviderRuntimeBudget` → `OpenAICompatibleChapterLLMClient._effective_timeout_seconds()` without code changes. Same-source evidence from `summary.json` correctly identifies Ch2 as the sole current default-run auditor timeout blocker. Three low-severity findings were identified (host timeout quantification, repair timeout fallback chain clarity, timeout root cause hint behavior), none of which block implementation. The plan preserves all Service/Host/Agent/Fund boundaries, maintains fail-closed semantics, and does not authorize any default, auditor, score, golden, or readiness changes.
