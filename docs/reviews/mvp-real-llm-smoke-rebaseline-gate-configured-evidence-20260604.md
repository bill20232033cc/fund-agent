# MVP Real LLM Smoke Re-baseline Gate Configured Evidence

## 1. Scope

- Role: AgentCodex evidence execution.
- Phase: `MVP typed-template-to-agent report generation stabilization phase`.
- Gate: `Gate 2 Real LLM smoke re-baseline gate`.
- Plan accepted checkpoint: `4fd5b5b`.
- Prior environment-blocked evidence: `docs/reviews/mvp-real-llm-smoke-rebaseline-gate-evidence-20260604.md`.
- This artifact records the resumed evidence attempt after the environment owner configured required LLM env/config.
- Allowed write path for this resumed attempt: this artifact only.
- Allowed runtime output path: local ignored `reports/llm-runs/` retained artifact only if the reviewed smoke reaches typed incomplete/fail-closed artifact retention.

Scope boundary: evidence collection only. No source, test, config, runtime behavior, provider default, provider budget, timeout, attempt/backoff, model, endpoint, Agent runtime, multi-year runtime, score-loop, golden/readiness, PR/push/release or external release state was changed.

## 2. Source Of Truth Read

Context read before execution:

- `AGENTS.md`
- `docs/implementation-control.md`
- `docs/design.md`
- `docs/reviews/mvp-real-llm-smoke-rebaseline-gate-plan-20260604.md`
- `docs/reviews/mvp-real-llm-smoke-rebaseline-gate-evidence-20260604.md`

Key confirmed constraints:

- The current gate remains `Real LLM smoke re-baseline gate` evidence stage.
- Required env/config presence must be checked secret-safely before any live provider command.
- If preflight passes, exactly one reviewed live smoke command is allowed: `uv run fund-analysis analyze 006597 --report-year 2024 --use-llm`.
- No provider/runtime/default override is allowed.
- Incomplete or blocked `--use-llm` runs must fail closed, must not fall back to deterministic report generation and must not print partial reports to stdout.
- Historical retained artifacts may provide context only; they cannot substitute for current direct evidence.

## 3. Pre Git Integrity

- Command: `git branch --show-current`
  - Exit code: `0`
  - Result: `feat/mvp-llm-incomplete-run-artifacts`
- Command: `git status --short`
  - Exit code: `0`
  - Result: pre-existing untracked files only; no tracked modifications before this artifact.
- Command: `git diff --name-only`
  - Exit code: `0`
  - Result: empty before this artifact.

## 4. Secret-safe Env/Config Presence Preflight

Command run:

```bash
uv run python -c '<presence-only env preflight>'
```

Exit code: `0`.

Presence-only results:

| Field | Result |
|---|---|
| `FUND_AGENT_LLM_PROVIDER` present | `true` |
| `FUND_AGENT_LLM_MODEL` present | `true` |
| `FUND_AGENT_LLM_BASE_URL` present | `true` |
| `FUND_AGENT_LLM_API_KEY_ENV_VAR` override present | `false` |
| API key env var name checked | `FUND_AGENT_LLM_API_KEY` |
| API key present | `true` |
| Required env/config all present | `true` |

Optional runtime env explicitly set:

| Env var | explicitly_set |
|---|---|
| `FUND_AGENT_LLM_TIMEOUT_SECONDS` | `false` |
| `FUND_AGENT_LLM_WRITER_TIMEOUT_SECONDS` | `false` |
| `FUND_AGENT_LLM_AUDITOR_TIMEOUT_SECONDS` | `false` |
| `FUND_AGENT_LLM_REPAIR_TIMEOUT_SECONDS` | `false` |
| `FUND_AGENT_LLM_TIMEOUT_MAX_ATTEMPTS` | `false` |
| `FUND_AGENT_LLM_TIMEOUT_BACKOFF_SECONDS` | `false` |
| `FUND_AGENT_LLM_MAX_OUTPUT_CHARS` | `false` |

Secret-safe statement:

- No API key value was printed.
- No base URL value was printed.
- No provider/model value was printed.
- No Authorization header, raw config dump, shell environment dump, raw prompt, draft, raw provider response, raw audit response or request headers were printed by the preflight.
- No endpoint reachability check, HTTP request or provider call was performed by the preflight.

Preflight classification: `PASS`.

## 5. Local Non-live Safety Validation

All local non-live validation commands passed before the live smoke command.

| Command | Exit code | Result |
|---|---:|---|
| `uv run pytest tests/services/test_llm_run_artifacts.py -q` | `0` | `7 passed` |
| `uv run pytest tests/ui/test_cli.py -q` | `0` | `74 passed` |
| `uv run pytest tests/services/test_fund_analysis_service_llm.py tests/services/test_execution_contract.py -q` | `0` | `47 passed` |
| `uv run pytest tests/services/test_chapter_orchestrator.py -q` | `0` | `77 passed` |
| `uv run pytest tests/fund/test_chapter_writer.py tests/fund/test_chapter_auditor.py -q` | `0` | `81 passed` |
| `uv run pytest tests/services/test_llm_provider.py -q` | `0` | `25 passed` |

Aggregate local validation: `306 passed`.

Validation classification: `PASS`.

## 6. Host Timeout Derivation Check

Current code facts checked after the operator-terminated live smoke to avoid over-classifying the result:

- `fund_agent/config/llm.py` defaults `FUND_AGENT_LLM_TIMEOUT_SECONDS` to `60.0`.
- Writer, auditor and repair timeout env vars were not explicitly set, so the configured presence-only preflight implies each operation-specific timeout used its default/fallback value.
- `FUND_AGENT_LLM_TIMEOUT_MAX_ATTEMPTS` was not explicitly set, so the default max attempts is `2`.
- `fund_agent/services/execution_contract.py` derives Host timeout as `(writer_timeout_seconds + auditor_timeout_seconds + repair_timeout_seconds) * timeout_max_attempts * chapter_count`.
- `fund_agent/services/fund_analysis_service.py` sets `LLM_REPORT_HOST_TIMEOUT_CHAPTER_COUNT = 6`.

Derived default Host timeout for this configured attempt: `(60 + 60 + 60) * 2 * 6 = 2160s`.

Implication: the observed approximately `900s` wait was shorter than the derived Host deadline. Therefore this evidence attempt cannot prove Host/CLI timeout enforcement failure, provider runtime residual, content contract residual or accepted fail-closed behavior. It only proves that the current evidence owner interrupted the single reviewed live smoke before the derived Host deadline.

## 7. Exactly-one Reviewed Live Smoke

Reviewed command run:

```bash
uv run fund-analysis analyze 006597 --report-year 2024 --use-llm
```

Execution facts:

| Field | Result |
|---|---|
| Live smoke command count | `1` |
| Provider/runtime/default overrides added | `false` |
| Natural terminal result observed | `false` |
| Observed wall-clock wait before operator termination | approximately `900s` |
| Derived Host timeout for default runtime plan | approximately `2160s` |
| Operator termination reason | command remained running without terminal stdout/stderr output in the observable window |
| Final exit code after termination | `143` |
| Stdout | empty |
| Stderr | empty |
| New retained artifact in `reports/llm-runs/` | none observed |
| Deterministic fallback command run | `false` |
| Accepted full report produced | `false` |

Process cleanup:

- The hanging `uv run fund-analysis analyze 006597 --report-year 2024 --use-llm` parent process and its Python child process were terminated.
- Follow-up process check showed no remaining current `fund-analysis analyze 006597 --report-year 2024 --use-llm` process.
- A stale unrelated process record containing historical prompt text matched the narrow process pattern; it was not this smoke process and was not terminated.

Operational hygiene note:

- A broad process listing command was used while diagnosing the hung process. Its output was not promoted into this artifact because it included unrelated process command lines from the local machine. This artifact only records the narrow target-process facts needed for the smoke evidence.

Smoke classification: `INCONCLUSIVE_BLOCKED`.

Blocking finding: `B2 operator_interrupted_before_derived_host_deadline`.

Direct-evidence basis:

- Required env/config presence passed.
- Local non-live safety validation passed.
- The only allowed live smoke command did not naturally return within the observed 900 second window.
- The observed 900 second wait was shorter than the current default derived Host timeout of approximately 2160 seconds.
- The command produced no stdout, no stderr and no retained incomplete artifact before operator termination.
- Because the command was operator-terminated, the result cannot be used as accepted smoke baseline, accepted fail-closed incomplete baseline or provider/content residual baseline.
- This attempt also cannot be used to claim a Host/CLI terminal timeout bug because the operator termination happened before the derived Host deadline.

## 8. Retained Artifact Check

Command:

```bash
find reports/llm-runs -maxdepth 1 -type d -mmin -120 -print
```

Exit code: `0`.

Result: no recently created retained artifact directory was observed for this configured evidence attempt.

Historical retained artifact files from 2026-06-02 and 2026-06-03 remain present under `reports/llm-runs/`, but were not used as current direct smoke evidence.

## 9. Secret / Redaction Scan

This artifact intentionally avoids:

- API key values.
- Base URL values.
- Provider/model values.
- Authorization header values.
- Bearer token values.
- Raw env dumps.
- Raw prompt, draft, raw provider response, raw audit response, message body or full request headers.

Scan commands:

- `rg` scan for secret-like token, Authorization value, Bearer value and URL value patterns.
- `rg` scan for policy terms: API key, base URL, raw prompt, raw provider response, raw audit response, message body and request headers.

Scan results:

- Secret-like values / URL values / Authorization value patterns: no matches.
- Policy terms such as `base URL`, `raw prompt`, `raw provider response`, `raw audit response`, `message body` and `request headers` appear only as forbidden-scope or scan checklist labels.
- No real secret, base URL value, raw provider payload or raw prompt was found in this artifact.

Scan classification: `PASS`.

## 10. A1-A9 Acceptance Criteria Mapping

| Criterion | Status | Evidence / reason |
|---|---|---|
| A1. Plan scope and forbidden-scope safety | `PASS` | Evidence stayed within configured evidence attempt. No source/test/config/runtime behavior was changed. |
| A2. Env/config presence preflight is secret-safe | `PASS` | Required env/config presence passed with presence-only output and no secret/base URL/provider/model value printed. |
| A3. Reviewed real-smoke command is singular and scoped | `PASS` | Exactly one reviewed command was run, with no provider/runtime/default overrides. |
| A4. Incomplete fail-closed and stdout safety | `BLOCKED` | The command did not naturally reach incomplete terminal state before operator interruption. Stdout remained empty, but the interruption occurred before the derived Host deadline, so fail-closed terminal behavior was not evaluated. |
| A5. Accepted report safety if smoke succeeds | `BLOCKED` | No accepted report was produced. |
| A6. Safe diagnostic matrix and no secret leakage | `BLOCKED` | No runtime diagnostic matrix was available because the command did not naturally terminate. Artifact redaction scan passed with no secret-like value hit. |
| A7. Direct evidence integrity | `PASS` | Branch/status/diff, command list, validation results and retained artifact check were recorded. |
| A8. Provider timeout/block classification preserves current semantics | `BLOCKED` | No provider timeout/block terminal classification was produced before operator interruption; interruption occurred before the derived Host deadline and no runtime/default/budget changes were made. |
| A9. Boundary guardrails | `PASS` | No Dayu runtime dependency, Agent runtime, multi-year runtime, direct PDF/cache/source-helper read, `extra_payload` business parameter, public id, provider default, quality gate, golden/readiness, PR/push/release or deterministic fallback action was introduced. |

## 11. Forbidden-scope Checklist

| Forbidden scope | Result |
|---|---|
| No provider default/runtime/budget change | `PASS` |
| No timeout/attempt/backoff/model/endpoint/provider/max-output/repair-budget override | `PASS` |
| No Agent runtime implementation | `PASS` |
| No multi-year runtime | `PASS` |
| No score-loop | `PASS` |
| No golden/readiness | `PASS` |
| No snapshot refresh | `PASS` |
| No strict correctness rerun | `PASS` |
| No release readiness | `PASS` |
| No PR/push/release | `PASS` |
| No deterministic fallback | `PASS` |
| No public chapter id change | `PASS` |
| No direct PDF/cache/source helper read introduced | `PASS` |
| No `extra_payload` business parameter introduced | `PASS` |
| No production dependency on `dayu-agent` / `dayu.host` / `dayu.engine` introduced | `PASS` |

## 12. Findings And Next Entry

### B1 `environment_blocked`

Status: `RESOLVED`.

Required provider/model/base-url/API-key presence is now present in the current shell, and optional runtime env overrides are absent.

### B2 `operator_interrupted_before_derived_host_deadline`

Status: `BLOCKING`.

The single reviewed live smoke command did not naturally produce a CLI terminal state, fail-closed diagnostic summary or retained incomplete artifact within the observed 900 second window. However, the observed wait was shorter than the current derived Host timeout of approximately 2160 seconds. Because the process was operator-terminated before the derived Host deadline, this run cannot be accepted as either a successful smoke baseline or a valid fail-closed provider/content residual baseline, and it cannot prove a Host/CLI terminal timeout defect.

Owner: controller / evidence owner.

Minimum next entry:

1. Independent evidence review of this artifact should confirm whether the configured evidence attempt is correctly classified as blocked and whether redaction requirements are met.
2. Controller should decide whether a new reviewed evidence attempt is authorized to wait through the full derived Host deadline, or whether the evidence protocol should be revised first with an explicit external observation window and capture/termination policy.
3. Do not enter Chapter acceptance calibration until a natural terminal smoke result exists and is independently reviewed.

## 13. Post Evidence Git Integrity

Post-evidence expected file addition:

- `docs/reviews/mvp-real-llm-smoke-rebaseline-gate-configured-evidence-20260604.md`

Initial configured-attempt runtime artifact result:

- No new `reports/llm-runs/` directory from this configured attempt.

Replacement attempt runtime artifact result:

- The later controller-authorized replacement attempt produced `reports/llm-runs/006597-2024-20260604T091239Z-host_run_b52b779e7e9a43c/manifest.json`; see sections 14-20.

No accepted checkpoint should be created solely from this artifact unless independent reviews and controller judgment classify the gate state and explicitly accept the blocked evidence artifact correctness.

## 14. Replacement Attempt Controller Authorization

Controller decision artifact:

- `docs/reviews/mvp-real-llm-smoke-rebaseline-gate-configured-evidence-controller-decision-20260604.md`

Decision summary:

- The first configured attempt was not accepted because it was operator-interrupted before the derived Host deadline.
- One replacement attempt was authorized for the same reviewed command.
- Replacement attempt constraints preserved the accepted plan's core scope: same fund/year/command, no provider/runtime/default override, no deterministic fallback, no provider probe and no Chapter acceptance calibration.
- External observation window was set to `2400s`, exceeding the current derived Host timeout of approximately `2160s`.

## 15. Replacement Preflight

Command run:

```bash
uv run python -c '<presence-only env preflight>'
```

Exit code: `0`.

Presence-only results:

| Field | Result |
|---|---|
| `FUND_AGENT_LLM_PROVIDER` present | `true` |
| `FUND_AGENT_LLM_MODEL` present | `true` |
| `FUND_AGENT_LLM_BASE_URL` present | `true` |
| `FUND_AGENT_LLM_API_KEY_ENV_VAR` override present | `false` |
| API key env var name checked | `FUND_AGENT_LLM_API_KEY` |
| API key present | `true` |
| Required env/config all present | `true` |

Optional runtime env explicitly set:

| Env var | explicitly_set |
|---|---|
| `FUND_AGENT_LLM_TIMEOUT_SECONDS` | `false` |
| `FUND_AGENT_LLM_WRITER_TIMEOUT_SECONDS` | `false` |
| `FUND_AGENT_LLM_AUDITOR_TIMEOUT_SECONDS` | `false` |
| `FUND_AGENT_LLM_REPAIR_TIMEOUT_SECONDS` | `false` |
| `FUND_AGENT_LLM_TIMEOUT_MAX_ATTEMPTS` | `false` |
| `FUND_AGENT_LLM_TIMEOUT_BACKOFF_SECONDS` | `false` |
| `FUND_AGENT_LLM_MAX_OUTPUT_CHARS` | `false` |

Secret-safe statement:

- No API key value was printed.
- No base URL value was printed.
- No provider/model value was printed.
- No Authorization header, raw config dump, shell environment dump, raw prompt, draft, raw provider response, raw audit response or request headers were printed by the preflight.
- No endpoint reachability check, HTTP request or provider call was performed by the preflight.

Replacement preflight classification: `PASS`.

## 16. Replacement Live Smoke Result

Reviewed command run:

```bash
uv run fund-analysis analyze 006597 --report-year 2024 --use-llm
```

Execution facts:

| Field | Result |
|---|---|
| Replacement live smoke command count | `1` |
| Provider/runtime/default overrides added | `false` |
| Natural terminal result observed | `true` |
| Exit code | `1` |
| Stdout | empty |
| Stderr | safe fail-closed summary present |
| Deterministic fallback command run | `false` |
| Accepted full report produced | `false` |
| Orchestration status | `blocked` |
| Final assembly status | `incomplete` |
| Host run status | `failed` |
| Host timeout classification | `none` |
| Host cancel reason | `none` |
| CLI elapsed max observed | `923547ms` |
| New retained artifact manifest | `reports/llm-runs/006597-2024-20260604T091239Z-host_run_b52b779e7e9a43c/manifest.json` |

CLI safe summary:

- `orchestration_status=blocked`
- `final_assembly_status=incomplete`
- `first_failed_chapter_id=1`
- `first_failed_status=failed`
- `first_failed_stop_reason=llm_timeout`
- `first_failed_category=llm_timeout`
- `first_failed_runtime_operation=auditor`
- `first_failed_provider_attempts=2/2`
- `first_failed_provider_runtime_category=timeout`
- `first_failed_elapsed_ms_max=60224`
- `first_failed_prompt_chars=4295`
- `first_failed_approx_prompt_tokens=1074`
- `first_failed_timeout_root_cause_hint=small_prompt_provider_timeout`
- `chapter_matrix=1:failed/llm_timeout/llm_timeout/unknown;2:failed/llm_timeout/llm_timeout/unknown;3:failed/llm_timeout/llm_timeout/unknown;4:failed/llm_timeout/llm_timeout/unknown;5:failed/llm_timeout/llm_timeout/unknown;6:failed/llm_timeout/llm_timeout/unknown`

Replacement smoke classification: `FAIL_CLOSED_PROVIDER_RUNTIME_RESIDUAL`.

Direct-evidence basis:

- Required env/config presence passed.
- Local non-live safety validation already passed earlier in this configured evidence run.
- Replacement command naturally returned exit `1`.
- Stdout was empty; no half report was printed.
- CLI emitted a safe fail-closed stderr summary and retained artifact path.
- No deterministic fallback was run.
- Retained artifact was created under local ignored `reports/llm-runs/`.
- Failure is same-run provider runtime timeout evidence, not environment blocked and not operator interruption.

## 17. Replacement Retained Artifact Summary

Retained artifact directory:

- `reports/llm-runs/006597-2024-20260604T091239Z-host_run_b52b779e7e9a43c`

Manifest summary:

| Field | Result |
|---|---|
| `artifact_kind` | `llm_incomplete_run_diagnostic` |
| `run_id` | `host_run_b52b779e7e9a43cd` |
| `fund_code` | `006597` |
| `report_year` | `2024` |
| `orchestration_status` | `blocked` |
| `final_assembly_status` | `incomplete` |
| `chapter_count` | `6` |
| `cli_command` | `analyze --use-llm` |
| `redaction_applied` | `false` |
| `redaction_count` | `0` |

Chapter matrix:

| Chapter | Status | Stop reason | Failure category | Attempt count | Terminal operation |
|---:|---|---|---|---:|---|
| 1 | `failed` | `llm_timeout` | `llm_timeout` | 1 | `auditor` |
| 2 | `failed` | `llm_timeout` | `llm_timeout` | 0 | `writer` |
| 3 | `failed` | `llm_timeout` | `llm_timeout` | 0 | `writer` |
| 4 | `failed` | `llm_timeout` | `llm_timeout` | 0 | `writer` |
| 5 | `failed` | `llm_timeout` | `llm_timeout` | 0 | `writer` |
| 6 | `failed` | `llm_timeout` | `llm_timeout` | 1 | `auditor` |

Runtime first failed:

| Field | Result |
|---|---|
| Chapter | `1` |
| Operation | `auditor` |
| Issue class | `ReadTimeout` |
| Provider runtime categories | `timeout` |
| Provider attempts | `2/2` |
| Timeout seconds | `60.0` |
| Timeout max attempts | `2` |
| Timeout backoff seconds | `1.0` |
| Approx prompt tokens | `1074` |
| System prompt chars | `54` |
| User prompt chars | `4241` |
| Timeout root cause hint | `small_prompt_provider_timeout` |
| Diagnostic consistency | `consistent` |

Retained files:

- `summary.json`
- `manifest.json`
- `chapters/chapter-01.json` through `chapters/chapter-06.json`
- `chapters/chapter-01-attempt-00-writer.md`
- `chapters/chapter-06-attempt-00-writer.md`

The retained writer markdown files were not promoted into this evidence artifact. Only safe scalar summaries from manifest/summary JSON were recorded.

## 18. Replacement Redaction Scan

Scan scope:

- `docs/reviews/mvp-real-llm-smoke-rebaseline-gate-configured-evidence-20260604.md`
- `docs/reviews/mvp-real-llm-smoke-rebaseline-gate-configured-evidence-controller-decision-20260604.md`
- `reports/llm-runs/006597-2024-20260604T091239Z-host_run_b52b779e7e9a43c`

Scan commands:

- `rg` scan for secret-like token, Authorization value, Bearer value and URL value patterns.
- `rg` scan for policy terms: API key, base URL, Authorization, Bearer, raw prompt, raw provider response, raw audit response, message body and request headers.

Scan results:

- Secret-like values / URL values / Authorization value patterns: no matches.
- Policy terms appear only as forbidden-scope or scan checklist labels in review artifacts.
- No retained artifact match was found for the policy-term scan.
- No real secret, base URL value, raw provider payload or raw prompt was found in the scan scope.

Scan classification: `PASS`.

## 19. Replacement A1-A9 Acceptance Criteria Mapping

| Criterion | Status | Evidence / reason |
|---|---|---|
| A1. Plan scope and forbidden-scope safety | `PASS` | Replacement execution stayed within controller-authorized configured evidence attempt. No source/test/config/runtime behavior changed. |
| A2. Env/config presence preflight is secret-safe | `PASS` | Replacement presence preflight passed with booleans and env var names only. |
| A3. Reviewed real-smoke command is singular and scoped | `PASS` | Exactly one replacement command was run, same reviewed fund/year/command, no provider/runtime/default overrides. |
| A4. Incomplete fail-closed and stdout safety | `PASS` | Replacement smoke exited `1`, stdout empty, safe stderr summary present, retained artifact path present, no deterministic fallback. |
| A5. Accepted report safety if smoke succeeds | `NOT_APPLICABLE` | Smoke did not succeed; no accepted report was produced. |
| A6. Safe diagnostic matrix and no secret leakage | `PASS` | CLI and retained artifact provide safe chapter/runtime matrix; redaction scan passed. |
| A7. Direct evidence integrity | `PASS` | Branch/status/diff, command list, retained artifact path and same-run manifest/summary were recorded. |
| A8. Provider timeout/block classification preserves current semantics | `PASS_WITH_RESIDUAL` | Same-run direct evidence classifies all chapters as `llm_timeout` with provider `ReadTimeout`; no runtime/default/budget changes were made. |
| A9. Boundary guardrails | `PASS` | No Dayu runtime dependency, Agent runtime, multi-year runtime, direct PDF/cache/source-helper read, `extra_payload` business parameter, public id, provider default, quality gate, golden/readiness, PR/push/release or deterministic fallback action was introduced. |

## 20. Final Configured Evidence Classification

Final configured evidence classification: `BLOCKED_WITH_DIRECT_PROVIDER_RUNTIME_RESIDUAL`.

Resolved blocker:

- `B1 environment_blocked`: resolved. Required provider/model/base-url/API-key presence is present.

Superseded inconclusive blocker:

- `B2 operator_interrupted_before_derived_host_deadline`: superseded by controller-authorized replacement attempt. The first configured attempt remains recorded as inconclusive and is not used as the final smoke result.

Current blocking residual:

- `B3 provider_runtime_residual_all_chapters_llm_timeout`.

Residual details:

- Replacement smoke naturally failed closed.
- `orchestration_status=blocked`.
- `final_assembly_status=incomplete`.
- First failed chapter is chapter 1 auditor timeout, `2/2` attempts, `60s` timeout, approx `1074` prompt tokens, `small_prompt_provider_timeout`.
- Chapters 1 and 6 reached auditor timeout after one writer draft attempt.
- Chapters 2, 3, 4 and 5 failed at writer timeout.
- No chapter was accepted; no final report was assembled.

Minimum next entry:

1. Independent evidence review should verify this artifact and the retained artifact summary.
2. Controller judgment should accept the evidence artifact correctness while keeping the gate outcome blocked by `provider_runtime_residual`.
3. Do not enter Chapter acceptance calibration yet. The next scoped work should be provider runtime residual disposition/calibration or provider endpoint/runtime policy decision, not content acceptance calibration.
