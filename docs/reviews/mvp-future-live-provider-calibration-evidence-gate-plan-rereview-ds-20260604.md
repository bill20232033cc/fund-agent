# MVP Future Live Provider Calibration Evidence Gate Plan — AgentDS Re-Review

## 1. Scope

- **Target**: `docs/reviews/mvp-future-live-provider-calibration-evidence-gate-plan-20260604.md` (revised per DS finding)
- **Reviewer**: AgentDS
- **Role**: independent plan re-reviewer
- **Prior review**: `docs/reviews/mvp-future-live-provider-calibration-evidence-gate-plan-review-ds-20260604.md`

## 2. Prior Findings — Resolution Status

| # | Prior finding | Severity | Resolution | Status |
|---|---|---|---|---|
| 1 | Outcome taxonomy missing non-timeout provider errors | Material | New Section 6.4 `Non-Timeout Provider Runtime Error` with classification `provider_runtime_error_non_timeout`, covering `llm_rate_limited`, `llm_malformed_response`, `llm_network_error`, HTTP error, malformed response, rate limiting. Evidence requirements and next action specified. | **FIXED** |
| 2 | Presence-only readiness check has no implementation path | Material | New inline Python command in Section 5.2: reads env vars, runs `load_llm_provider_config_from_env()`, catches `LLMProviderConfigError` with per-field classification, prints only presence booleans and `config_validation: pass\|fail`. No HTTP, no values. Stop rule if shell can't run the exact command. | **FIXED** |
| 3 | Fund/year selection lacks rationale | Minor | Section 3 now states: same fund/year keeps the live sample comparable to current same-run endpoint residual evidence and avoids adding fund-selection variance to a provider-availability gate. | **FIXED** |
| 4 | Redaction scan pattern may miss non-OpenAI key formats | Minor | Section 7 now instructs evidence executor to adapt scan to known configured provider key format if not OpenAI-style, without printing key or prefix. | **FIXED** |

## 3. New Revisions — Correctness Check

### 3.1 Inline presence-only readiness command

The new Python command in Section 5.2 correctly:

- Lists required env vars (`FUND_AGENT_LLM_PROVIDER`, `FUND_AGENT_LLM_MODEL`, `FUND_AGENT_LLM_BASE_URL`) and prints `present|absent` booleans.
- Handles custom API key env var name via `FUND_AGENT_LLM_API_KEY_ENV_VAR` with correct fallback to `FUND_AGENT_LLM_API_KEY`.
- Prints `effective_api_key_value: present|absent` without revealing the value.
- Lists optional runtime vars as `set|unset` booleans.
- Attempts `load_llm_provider_config_from_env()` and catches `LLMProviderConfigError` with coarse field classification (missing provider/model/base-url/API-key, unsupported provider, invalid URL, fallthrough).
- Performs no HTTP call — `load_llm_provider_config_from_env()` is a typed config constructor, not a provider client.

**Verdict**: The command is safe and fit for purpose. It does not leak values and correctly gates live execution on config validity.

### 3.2 Non-timeout error taxonomy (Section 6.4)

The new category `provider_runtime_error_non_timeout`:

- Correctly excludes timeout (boundary with 6.2 is explicit).
- Covers all four current failure categories (`llm_rate_limited`, `llm_malformed_response`, `llm_network_error`) plus generic HTTP error and malformed response.
- Evidence requirements are secret-safe: no raw provider response, request body, headers, endpoint URL, or message body.
- Next action is clear: stop, hand controller, do not retry, do not reclassify as endpoint availability.

**Minor observation**: Section 11 Residual Owners table does not list `provider_runtime_error_non_timeout` as a residual row. This is a documentation consistency gap, not a logic or safety issue. The next action in 6.4 already specifies the handling path.

### 3.3 Fund/year rationale (Section 3)

The added sentence is clear and logically sound: reusing the same fund/year avoids introducing fund-selection as a confounding variable when the gate's purpose is provider availability classification.

### 3.4 Redaction scan adaptation (Section 7)

The added guidance is appropriate: the evidence executor is told to adapt without printing the key format or prefix. This is guidance-level and sufficient for an evidence protocol.

## 4. No New Blocking Findings

All four prior findings are resolved. The revisions introduce no new safety, logic, boundary, or sequencing issues. The plan continues to correctly enforce:

- Fail-closed, no-fallback, stdout-empty-on-incomplete semantics (A5)
- Command singularity (A3)
- Default immutability (A4)
- Historical/current evidence separation (A6)
- Secret-safe diagnostics (A7)
- Heavy gate sequencing: plan → review ×2 → controller judgment → evidence (Sections 9-10)
- Stop-before-live: the plan itself does not authorize a live command (Section 12)

## 5. Conclusion

**Verdict: PASS**

All four prior findings are confirmed fixed. No new blocking or material findings identified. The plan is ready for MiMo review and controller judgment.

**REVIEWER VERDICT: PASS**

---

*Reviewer: AgentDS*
*Date: 2026-06-04*
*Re-review of: `docs/reviews/mvp-future-live-provider-calibration-evidence-gate-plan-20260604.md`*
