# MVP Future Live Provider Calibration Evidence Gate Plan — AgentMiMo Independent Plan Review

## 1. Reviewed Target And Scope

- **Target artifact**: `docs/reviews/mvp-future-live-provider-calibration-evidence-gate-plan-20260604.md`
- **Reviewer**: AgentMiMo
- **Role**: independent plan reviewer (not controller, not evidence executor)
- **Review focus**: forbidden-scope containment, secret-safety and redaction rules, command singularity, fail-closed / no deterministic fallback / stdout-empty-on-incomplete semantics, provider default preservation, historical/current evidence separation, taxonomy and residual owner completeness after DS fixes, handoff readiness for evidence executor
- **Sources consulted**: `AGENTS.md`, `docs/implementation-control.md` (front control/current gate section), `docs/current-startup-packet.md` (sections 2, 5, 6, 7, 8), `docs/design.md` (Route C, typed template truth-source replacement, provider runtime budget, internalized Agent future design), target plan artifact, DS review (`docs/reviews/mvp-future-live-provider-calibration-evidence-gate-plan-review-ds-20260604.md`), DS re-review (`docs/reviews/mvp-future-live-provider-calibration-evidence-gate-plan-rereview-ds-20260604.md`)

## 2. Review Focus — Systematic Assessment

### 2.1 Forbidden-Scope Containment

Plan Section 4 (Non-Goals) explicitly forbids:

- Running live provider commands in the plan step
- Changing provider endpoint/model/API key/timeout/writer timeout/auditor timeout/repair timeout/retry attempts/backoff/max output defaults
- Adding env overrides to make the run pass
- PASS-only timing probe, split-audit probe, endpoint reachability probe, curl, handwritten HTTP, private provider client calls
- Entering Chapter acceptance calibration
- Implementing Agent runtime, tool loop, ToolRegistry, ToolTrace, multi-year annual evidence runtime, score-loop
- Changing source, tests, config, runtime default, README, template, design doc, control doc, startup packet, quality gate, golden/readiness, snapshot, fixtures
- Pushing, opening PR, changing release state, touching external state beyond the one authorized live command
- Using historical retained artifacts as substitute for current direct evidence
- Pasting secrets/raw prompts/raw provider responses into artifacts

Section 8 (Acceptance Criteria) A8 adds a boundary guardrails checklist covering source/test/config/runtime/quality/golden/Agent/score-loop drift.

**Verdict**: Forbidden scope is comprehensive and correctly aligned with `docs/current-startup-packet.md` Section 7 (Prohibited Actions) and `docs/implementation-control.md` current gate next entry point. No containment gap found.

### 2.2 Secret-Safety And Redaction Rules

- Section 4 Non-Goals explicitly forbids pasting API key, Authorization header, bearer token, provider base URL value, model value, raw prompt, writer draft, raw provider response, raw audit response, or full env dump.
- Section 5.2 readiness command prints only presence booleans (`present|absent`, `set|unset`) and safe field names; never prints actual env values.
- Section 5.3 live command evidence requirements list safe fields only (exit code, stdout byte count, stderr safe summary, retained artifact path, orchestration_status, final_assembly_status, per-chapter matrix, safe runtime diagnostics allowlist fields).
- Section 7 provides minimum redaction scan patterns and instructs the evidence executor to adapt to known configured provider key format without printing the key or key prefix.
- Section 6.6 Safety Blocker classifies any secret/raw prompt/raw provider response leak as a safety blocker with immediate stop.

**Verdict**: Secret-safety is correctly enforced at all layers: readiness command, live command evidence, redaction scan, and safety blocker classification. No gap found.

### 2.3 Command Singularity

- Section 5.3 states "exactly one live command" with explicit command string `uv run fund-analysis analyze 006597 --report-year 2024 --use-llm`.
- Command constraints explicitly forbid `--llm-progress` (unless controller wants), timeout/attempt/backoff/max-output/model/endpoint/prompt/repair-budget/provider override, second live command, deterministic fallback command, endpoint reachability check before/after, PASS-only or chapter-only live probe.
- Section 8 A3 requires "exactly one live command" as a blocking failure criterion.
- Section 10 requires controller judgment explicitly authorizing "exactly one live command... only if readiness passes".
- Section 6.6 Safety Blocker classifies "live command count exceeds one" as safety blocker.

**Verdict**: Command singularity is correctly enforced through plan specification, acceptance criteria, controller judgment requirements, and safety blocker classification. No gap found.

### 2.4 Fail-Closed / No Deterministic Fallback / Stdout-Empty-On-Incomplete

- Section 2 Current Facts states: "Incomplete LLM runs must not print partial reports to stdout", "Incomplete LLM runs must not fall back to deterministic report generation".
- Section 5.3 live command constraints: "no deterministic fallback command".
- Section 6.5 Smoke Accepted requires exit code 0, stdout contains complete report, all chapters present — otherwise not classified as accepted.
- Section 6.6 Safety Blocker classifies: "incomplete run prints partial report to stdout", "incomplete run exits 0", "deterministic fallback appears" as safety blockers.
- Section 8 A5 requires: "Exit code, stdout byte count, stderr safe summary, retained artifact" with blocking failure on "Partial stdout, exit 0, deterministic fallback".

**Verdict**: Fail-closed, no-fallback, and stdout-empty-on-incomplete semantics are correctly preserved and enforced through multiple layers. No gap found.

### 2.5 Provider Default Preservation

- Section 2 Current Facts: "Provider runtime defaults are unchanged: timeout/budget/attempt/backoff/model/endpoint are not changed by this plan."
- Section 4 Non-Goals: "Do not change provider endpoint, model, API key, timeout, writer timeout, auditor timeout, repair timeout, retry attempts, backoff or max output defaults."
- Section 5.3 live command constraints: "no timeout, attempt, backoff, max-output, model, endpoint, prompt, repair-budget or provider override".
- Section 8 A4: "Defaults unchanged — Command has no overrides; git diff has no config/runtime change — Timeout/attempt/backoff/model/endpoint/default changed" is a blocking failure.
- Section 10 controller judgment requirements: "no provider/default/runtime/budget change is authorized".

**Verdict**: Provider default preservation is correctly enforced at all layers. No gap found.

### 2.6 Historical/Current Evidence Separation

- Section 4 Non-Goals: "Do not use historical retained artifacts as a substitute for current direct evidence."
- Section 3 Goal: fund/year fixed to `006597 / 2024` with explicit rationale for comparability.
- Section 5.2 stop condition: "Do not run live smoke, do not set ad hoc env values, and do not reuse historical artifacts as current evidence."
- Section 6.6 Safety Blocker: "historical artifact substituted" is a blocking failure.
- Section 8 A6: "Same-run direct evidence — New command output plus retained artifact from that run — Historical artifact substituted" is a blocking failure.

**Verdict**: Historical/current evidence separation is correctly enforced. No gap found.

### 2.7 Taxonomy Completeness After DS Fixes

DS original review identified four findings. The plan was revised to address all four. My independent assessment of the fixes:

**Finding 1 (Non-timeout provider errors) — FIXED**: Section 6.4 `provider_runtime_error_non_timeout` now covers `llm_rate_limited`, `llm_malformed_response`, `llm_network_error`, HTTP error, malformed response, and rate limiting. Evidence requirements are secret-safe. Next action is clear (stop, hand controller, do not retry). Boundary with Section 6.2 (timeout) is explicit.

**Finding 2 (Presence-check implementation path) — FIXED**: Section 5.2 now includes an exact inline Python command with structured output, config validation with per-field error classification, and a stop condition if the shell cannot safely run the exact command.

**Finding 3 (Fund/year rationale) — FIXED**: Section 3 now explains that reusing the same fund/year keeps the live sample comparable to current same-run endpoint residual evidence and avoids adding fund-selection variance.

**Finding 4 (Redaction pattern adaptation) — FIXED**: Section 7 now instructs the evidence executor to adapt the scan to the known configured provider key format without printing the key or prefix.

**Verdict**: All four DS findings appear resolved from my independent review lens. The taxonomy now covers all six current provider failure categories (`llm_timeout`, `llm_rate_limited`, `llm_malformed_response`, `llm_network_error` plus generic HTTP/malformed). No new taxonomy gap found.

### 2.8 Residual Owner Completeness

Section 11 Residual Owners table lists:

| Residual | Owner |
|---|---|
| `environment_blocked` | provider config/operator shell owner |
| `endpoint_availability_residual_active` | provider endpoint operator / future calibration controller |
| `provider_runtime_residual_narrowed` | future provider-runtime calibration owner |
| content contract or audit-rule blocker | future chapter/content calibration owner |
| safety blocker | controller |

**Gap identified**: `provider_runtime_error_non_timeout` (Section 6.4) is not listed as a row in the residual owners table. Section 6.4 does specify a clear next action ("stop and hand controller a same-run non-timeout provider residual"), but the table — which is the authoritative residual-to-owner mapping — is missing this entry. This is a documentation consistency gap, not a logic or safety gap, but it could cause the evidence executor to lack a clear owner assignment for this outcome.

**Severity**: Minor. The handling path is already specified in Section 6.4.

### 2.9 Handoff Readiness For Evidence Executor

The plan provides:

- Exact presence-only readiness command (Section 5.2 inline Python)
- Exact live command (Section 5.3)
- Six outcome classifications with evidence requirements and next actions (Sections 6.1-6.6)
- Redaction scan patterns and adaptation guidance (Section 7)
- Nine acceptance criteria with blocking failure definitions (Section 8)
- Review handoff requirements (Section 9)
- Controller judgment requirements (Section 10)

The evidence executor does not need to redesign any step. The only action needed is to add the missing `provider_runtime_error_non_timeout` row to the residual owners table for completeness.

**Verdict**: Handoff-ready with one minor table completeness gap.

## 3. Cross-Check Against Control Truth

- Plan classification `heavy` matches `docs/implementation-control.md` next gate classification.
- Plan scope matches `docs/current-startup-packet.md` Section 2 next entry point: "Start a new scoped future live provider calibration evidence gate plan; do not run live provider smoke/probe or endpoint reachability checks before plan/review/controller judgment/accepted checkpoint".
- Plan preserves all current implementation facts (deterministic default, fail-closed `--use-llm`, no Agent runtime, no Chapter acceptance calibration, no provider default changes).
- Plan correctly references the preceding accepted gate (`Provider runtime residual disposition / calibration gate` at checkpoint `3f72786`) and the current residual classification (`endpoint_availability_residual`).
- Plan does not authorize a live command by itself — only the controller judgment after accepted reviews can do so.

## 4. DS Findings Resolution Summary

| DS Finding | Severity | Resolution Status (My Assessment) |
|---|---|---|
| 1. Outcome taxonomy incomplete for non-timeout errors | Material | **FIXED** — Section 6.4 added with full classification |
| 2. Presence-check has no implementation path | Material | **FIXED** — Section 5.2 inline Python command added |
| 3. Fund/year selection lacks rationale | Minor | **FIXED** — Section 3 rationale added |
| 4. Redaction pattern may miss non-OpenAI keys | Minor | **FIXED** — Section 7 adaptation guidance added |

DS re-review findings are confirmed correct from my independent lens.

## 5. Findings

### Finding 1 — Residual owners table missing `provider_runtime_error_non_timeout` (Minor)

**Location**: Plan Section 11, Residual Owners table.

**Observation**: Section 6.4 defines outcome classification `provider_runtime_error_non_timeout` with a clear next action (stop and hand controller), but Section 11's residual owners table does not include this as a row. All other outcome classifications (6.1, 6.2, 6.3, 6.5, 6.6) have corresponding rows in the table.

**Why this matters**: The residual owners table is the authoritative mapping for the evidence executor to assign ownership. A missing row could cause ambiguity about who owns the follow-up for a non-timeout provider runtime error.

**Recommendation**: Add a row to Section 11: `| provider_runtime_error_non_timeout | provider runtime operator / future calibration controller | Stop with same-run evidence; do not retry or reclassify as endpoint availability |`.

## 6. Residual Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Residual owners table incomplete for non-timeout error | Low | Minor — handling path exists in Section 6.4 | Add table row (Finding 1) |
| Evidence executor environment cannot run inline Python command | Low | High — gate stalls at first step | Plan already specifies stop condition and controller judgment escalation |
| Single fund/year evidence may not generalize to other funds | Low | Medium — wrong residual classification | Plan already justifies fund/year selection for comparability |

## 7. Conclusion

The plan correctly enforces all hard boundaries from my review focus: forbidden-scope containment is comprehensive, secret-safety is enforced at all layers, command singularity is preserved through multiple mechanisms, fail-closed/no-fallback/stdout-empty-on-incomplete semantics are intact, provider defaults are immutable, historical/current evidence separation is explicit, and the taxonomy now covers all current provider failure categories after DS fixes.

One minor finding: the residual owners table is missing a row for `provider_runtime_error_non_timeout`. This is a documentation consistency gap, not a logic or safety issue, and does not block handoff to the evidence executor.

The plan is handoff-ready for the evidence executor without requiring redesign.

**REVIEWER VERDICT: PASS**

---

*Reviewer: AgentMiMo*
*Date: 2026-06-04*
*Target: `docs/reviews/mvp-future-live-provider-calibration-evidence-gate-plan-20260604.md`*
