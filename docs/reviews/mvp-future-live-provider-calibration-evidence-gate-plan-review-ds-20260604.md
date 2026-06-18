# MVP Future Live Provider Calibration Evidence Gate Plan — AgentDS Independent Plan Review

## 1. Reviewed Target And Scope

- **Target artifact**: `docs/reviews/mvp-future-live-provider-calibration-evidence-gate-plan-20260604.md`
- **Reviewer**: AgentDS
- **Role**: independent plan reviewer (not controller, not evidence executor)
- **Review focus**: first-principles evidence logic, environment_blocked stop rule, same-run direct evidence requirements, outcome taxonomy correctness, historical/current evidence separation, heavy gate sequencing
- **Sources consulted**: `AGENTS.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md`, preceding controller judgment `docs/reviews/mvp-provider-runtime-residual-disposition-calibration-evidence-controller-judgment-20260604.md`

## 2. Assumptions Tested

| # | Plan assumption | Test | Result |
|---|---|---|---|
| H1 | Config presence check can be done without a pre-existing CLI command | Section 5.2 specifies outputs but no implementation path | **Gap** — see Finding 2 |
| H2 | The only non-env-blocked failure mode is provider timeout | Section 6 taxonomy centers on timeout vs success | **Gap** — see Finding 1 |
| H3 | Reusing the same fund/year (006597/2024) as the historical retained run is the correct choice | Plan gives no rationale for fund/year selection | **Gap** — see Finding 3 |
| H4 | A single live command provides sufficient evidence to reclassify the residual | Plan explicitly scopes to one command; this is consistent with the preceding controller judgment's authorized next entry | **Holds** |
| H5 | Heavy gate sequencing (plan → review ×2 → controller judgment → evidence) is correctly enforced | Sections 9 and 10 require reviews before execution and controller authorization before any live command | **Holds** |
| H6 | Historical retained artifacts won't be confused with current evidence | Section 4 Non-Goals explicitly forbids this; A6 makes it a blocking failure | **Holds** |

## 3. Findings

### Finding 1 — Outcome taxonomy incomplete for non-timeout provider errors (Material)

**Location**: Plan Section 6, Outcome Classification.

**What the plan does**: Defines five outcome categories:
- 6.1 `environment_blocked` — config/construction failure
- 6.2 `endpoint_availability_residual_active` — broad ReadTimeout / zero response bytes
- 6.3 `provider_runtime_residual_narrowed` — partial timeouts
- 6.4 `real_llm_smoke_accepted_candidate` — complete success
- 6.5 `safety_blocker` — safety violations

**What's missing**: The current codebase has four provider runtime failure categories: `llm_timeout`, `llm_rate_limited`, `llm_malformed_response`, `llm_network_error` (per `docs/implementation-control.md` line 37 and `docs/current-startup-packet.md` line 101). The plan's taxonomy only explicitly addresses `llm_timeout`. If the live run encounters `llm_rate_limited` (HTTP 429), `llm_malformed_response`, or `llm_network_error`, none of the five categories cleanly classify the result:

- It's not `environment_blocked` (config passed, provider constructed)
- It's not `endpoint_availability_residual_active` (not a timeout)
- It's not `provider_runtime_residual_narrowed` (assumes timeout split)
- It's not `smoke_accepted_candidate` (not successful)
- It's not `safety_blocker` (no safety violation)

**Why this matters**: The evidence executor, when faced with a non-timeout provider error, has no clear classification instruction. This could lead to an ad-hoc classification or a misclassification that muddies the residual chain. The preceding controller judgment's residual chain is specifically about `endpoint_availability_residual` driven by `ReadTimeout` evidence; introducing a new error category without taxonomy support would break the residual lineage.

**Recommendation**: Add a sixth outcome category (e.g., `provider_runtime_error_unclassified`) for non-timeout provider failures, with explicit evidence requirements (error category, HTTP status if available, per-chapter breakdown) and a clear next action (stop and hand controller the new error category for separate classification). Alternatively, broaden 6.2 to cover all provider-runtime-level blocks, not just timeouts.

### Finding 2 — Presence-only readiness check has no implementation path (Material)

**Location**: Plan Section 5.2.

**What the plan specifies**: The evidence executor must run a presence-only readiness check that:
- loads typed config through `load_llm_provider_config_from_env()`
- prints only presence booleans and safe field names
- does not print values, call provider, or perform HTTP

**What's missing**: The plan names a Python function (`load_llm_provider_config_from_env()`) but does not specify what CLI command, script, or code path the evidence executor should use to invoke it. The evidence executor is told *what* to produce but not *how*.

**Why this matters**: Without a specified command, the evidence executor must either:
1. Find an existing CLI command that already does this (risk: none may exist)
2. Write a one-off script (risk: ad-hoc code outside gate scope, potential secret leak)
3. Use a Python one-liner (risk: inconsistent with the plan's structured output requirements)

Any of these paths introduces implementation ambiguity at the first step of evidence collection, which is exactly where a heavy gate should be most prescriptive.

**Recommendation**: Either specify the exact CLI command (if one exists), or add a brief specification of the script/command the evidence executor should use, with the constraint that it must not write new files outside the allowed paths.

### Finding 3 — Fund/year selection lacks rationale (Minor)

**Location**: Plan Section 5.3, the live command uses `006597 --report-year 2024`.

**Observation**: This is the same fund and year as the historical retained artifact (`reports/llm-runs/006597-2024-20260604T091239Z-host_run_b52b779e7e9a43c/`). The plan does not explain why this choice was made. Two interpretations are possible:
1. **Continuity**: same fund/year allows direct comparison with the historical retained run, making timeout pattern changes visible — this is a valid reason.
2. **Arbitrary**: any fund/year would work for an endpoint availability test, and the choice is incidental.

**Why this matters**: If the endpoint issue has any fund-specific or year-specific dimension (e.g., different prompt sizes for different funds), reusing the same fund/year is the correct choice for comparability. If not, a different fund could provide orthogonal evidence. Either way, the reasoning should be explicit so the controller can judge whether the evidence answers the right question.

**Recommendation**: Add a one-sentence rationale for the fund/year selection.

### Finding 4 — Redaction scan pattern may miss non-OpenAI key formats (Minor)

**Location**: Plan Section 7, redaction scan pattern.

**Observation**: The scan pattern includes `sk-[A-Za-z0-9]` which matches OpenAI-style keys. If the configured provider uses a different key format (e.g., Anthropic's `sk-ant-`, Google's, or a custom proxy key), the pattern would not match. The broader pattern `api_key.*=` would still catch most leaks in config-like contexts, but a raw key value appearing without the `api_key=` prefix could be missed.

**Recommendation**: Broaden the key pattern or add a note that the evidence executor should adapt the scan pattern to the configured provider's known key format.

## 4. What The Plan Gets Right

The plan correctly enforces several critical properties:

- **Fail-closed preservation** (A5): exit code 1, stdout empty, no fallback, no partial report — all correctly required as blocking failures.
- **Command singularity** (A3): exactly one live command, explicitly counted — prevents exploratory retry loops.
- **Default immutability** (A4): no timeout/attempt/backoff/model/endpoint overrides — correctly scoped as evidence collection, not tuning.
- **Historical/current separation** (A6 and Section 4): explicitly forbids substituting historical artifacts for current evidence.
- **Heavy gate sequencing** (Sections 9-10): requires two independent plan reviews, then controller judgment explicitly authorizing the live command, before any execution.
- **Secret safety** (A7 and Section 7): structured redaction scan, allowlist-only diagnostic fields, explicit safety_blocker classification.
- **Boundary guardrails** (A8): forbidden-scope checklist covers source, test, config, runtime, quality gate, golden, Agent runtime, score-loop, and external state.
- **Stop-before-live** (Section 12): the plan itself states it does not authorize a live command — only the controller judgment after accepted reviews can do so.

The `environment_blocked` stop rule (Section 5.2) is correctly designed: config validation failure stops the gate before any live command, with no ad-hoc env fixing and no historical artifact substitution.

## 5. Open Questions

1. Does a CLI command or script already exist that implements the presence-only readiness check specified in Section 5.2? If not, should the plan specify its creation as part of the evidence step?
2. Should the outcome taxonomy include explicit categories for `llm_rate_limited` and `llm_network_error`, or should the plan defer these to controller judgment on a case-by-case basis?
3. Is there a reason to prefer `006597 / 2024` over another fund/year, or is any fund/year acceptable for endpoint availability testing?

## 6. Residual Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Evidence executor encounters non-timeout provider error and misclassifies it | Low-Medium | Medium — muddies residual chain | Add taxonomy category (Finding 1) |
| Evidence executor cannot implement presence check from plan alone | Medium | High — gate stalls at first step | Specify implementation path (Finding 2) |
| Endpoint behavior is fund-specific and single-fund evidence overfits | Low | Medium — wrong residual classification | Justify fund selection (Finding 3) |
| Provider key format differs from scan pattern and raw key leaks into artifact | Low | High — secret exposure | Broaden pattern (Finding 4) |

## 7. Conclusion

**Verdict: PASS_WITH_FINDINGS**

The plan correctly enforces first-principles evidence logic, environment_blocked stop rules, same-run direct evidence requirements, historical/current separation, and heavy gate sequencing. No blocking findings were identified.

Finding 1 (outcome taxonomy gap for non-timeout errors) and Finding 2 (missing presence-check implementation path) are material and should be addressed before controller judgment. Finding 3 (fund/year rationale) and Finding 4 (redaction pattern) are minor and can be addressed at the plan author's discretion.

The plan's core safety properties — fail-closed, no fallback, secret-safe, single command, defaults unchanged, no live command before controller authorization — are correctly specified and meet the heavy gate classification requirements.

**REVIEWER VERDICT: PASS**

---

*Reviewer: AgentDS*
*Date: 2026-06-04*
*Target: `docs/reviews/mvp-future-live-provider-calibration-evidence-gate-plan-20260604.md`*
