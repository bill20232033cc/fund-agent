# MVP Future Live Provider Calibration Evidence Gate Plan

## 1. Scope And Classification

- Phase: `MVP typed-template-to-agent report generation stabilization phase`
- Gate: `Future live provider calibration evidence gate`
- Classification: `heavy`
- Role: planning worker; not controller and not evidence executor
- Allowed write in this step: this plan artifact only
- Preceding accepted gate: `Provider runtime residual disposition / calibration gate`
- Preceding accepted plan checkpoint: `75150ce`
- Preceding accepted evidence checkpoint: `3f72786`
- Current residual: `provider_runtime_residual_all_chapters_llm_timeout`
- Current residual classification: `endpoint_availability_residual`

This plan does not run a live provider command. It only defines the reviewed evidence protocol for the next gate.

## 2. Current Facts

Current control truth states:

- `Real LLM smoke re-baseline gate` remains not accepted.
- Required provider/model/base-url/API-key presence was previously confirmed in the configured evidence shell.
- The replacement `006597 / 2024 --use-llm` smoke failed closed with exit `1`, stdout empty, safe stderr summary and retained artifact.
- Retained artifact `reports/llm-runs/006597-2024-20260604T091239Z-host_run_b52b779e7e9a43c/` showed `orchestration_status=blocked`, `final_assembly_status=incomplete`, and all six body chapters failed with provider `ReadTimeout` / `llm_timeout`.
- Static D1-D4 disposition verified all six chapter JSON files and all twelve provider call diagnostics, and accepted the system as `READY_FOR_FUTURE_LIVE_PROVIDER_CALIBRATION_GATE`.
- The accepted next entry is a new scoped future live provider calibration evidence gate plan before any live command.

Current implementation facts remain unchanged:

- Default `fund-analysis analyze` and `fund-analysis checklist` stay deterministic.
- `fund-analysis analyze --use-llm` is explicit opt-in and fail-closed.
- Incomplete LLM runs must not print partial reports to stdout.
- Incomplete LLM runs must not fall back to deterministic report generation.
- Provider runtime defaults are unchanged: timeout/budget/attempt/backoff/model/endpoint are not changed by this plan.
- Host remains lifecycle-only and business-agnostic; current `--use-llm` execution is still Service-owned provider construction plus Fund writer/auditor primitives, not Agent tool-loop runtime.

## 3. Goal

Collect exactly one current live-provider evidence sample under unchanged defaults, after a presence-only readiness preflight, so the controller can decide whether the endpoint availability residual is still active or whether the system can return to the Real LLM smoke re-baseline sequence.

This gate answers only:

1. Does the current execution shell have valid typed provider config presence without printing secrets?
2. If presence passes, what happens on exactly one default-budget `006597 / 2024 --use-llm` command?
3. Does the run preserve fail-closed, stdout-empty-on-incomplete, no-fallback and secret-safe artifact semantics?
4. Does the retained artifact produce enough same-run evidence to classify the next blocker?

The fund/year is fixed to `006597 / 2024` because the current accepted blocker and retained artifact use the same fund/year. Reusing it keeps the next live sample comparable to the current same-run endpoint residual evidence and avoids adding fund-selection variance to a provider-availability gate.

## 4. Non-Goals

- Do not run any live provider command in the plan step.
- Do not change provider endpoint, model, API key, timeout, writer timeout, auditor timeout, repair timeout, retry attempts, backoff or max output defaults.
- Do not add env overrides to make the run pass.
- Do not run PASS-only timing probe, split-audit probe, endpoint reachability probe, curl, handwritten HTTP, or private provider client calls.
- Do not enter Chapter acceptance calibration; no body chapter currently has accepted conclusion in the latest retained artifact.
- Do not implement Agent runtime, tool loop, ToolRegistry, ToolTrace, multi-year annual evidence runtime or score-loop.
- Do not change source, tests, config, README, template, design doc, control doc, startup packet, quality gate, golden/readiness, snapshot or fixtures in this gate.
- Do not push, open PR, change release state, or touch external state beyond the one authorized live command in the later evidence step.
- Do not use historical retained artifacts as a substitute for current direct evidence.
- Do not paste API key, Authorization header, bearer token, provider base URL value, model value, raw prompt, writer draft, raw provider response, raw audit response or full env dump into any artifact.

## 5. Evidence Protocol

### 5.1 Preflight: Git And Scope

The evidence executor must record:

```bash
git branch --show-current
git status --short
git diff --name-only
```

Allowed changes after the evidence step:

- the evidence artifact under `docs/reviews/`
- local ignored retained artifact under `reports/llm-runs/`, if an incomplete typed LLM run reaches retention

Any source, test, config, runtime default, README, template, design, control, startup, quality gate, golden/readiness or release-state diff is a blocker unless separately authorized by a later controller judgment.

### 5.2 Preflight: Presence-Only Provider Readiness

The evidence executor must run one presence-only readiness check before live execution. The command must:

- load typed config through `load_llm_provider_config_from_env()`;
- print only presence booleans and safe field names;
- not print env values, base URL value, model value, API key value, Authorization header, provider account metadata, endpoint path or full config repr;
- not call provider or perform HTTP reachability.

Required outputs:

- `FUND_AGENT_LLM_PROVIDER: present|absent`
- `FUND_AGENT_LLM_MODEL: present|absent`
- `FUND_AGENT_LLM_BASE_URL: present|absent`
- `FUND_AGENT_LLM_API_KEY_ENV_VAR: present|absent`
- `effective_api_key_value: present|absent`
- `config_validation: pass|fail`
- if failed: `config_error_class: LLMProviderConfigError` and a coarse `config_error_field`
- optional runtime variables as set/unset booleans only:
  - `FUND_AGENT_LLM_TIMEOUT_SECONDS`
  - `FUND_AGENT_LLM_WRITER_TIMEOUT_SECONDS`
  - `FUND_AGENT_LLM_AUDITOR_TIMEOUT_SECONDS`
  - `FUND_AGENT_LLM_REPAIR_TIMEOUT_SECONDS`
  - `FUND_AGENT_LLM_TIMEOUT_MAX_ATTEMPTS`
  - `FUND_AGENT_LLM_TIMEOUT_BACKOFF_SECONDS`
  - `FUND_AGENT_LLM_MAX_OUTPUT_CHARS`

Stop condition:

- If config validation fails, stop the gate as `environment_blocked`. Do not run live smoke, do not set ad hoc env values, and do not reuse historical artifacts as current evidence.

Recommended readiness command for the evidence executor:

```bash
python -c 'import os
from fund_agent.config.llm import LLMProviderConfigError, load_llm_provider_config_from_env
required = ("FUND_AGENT_LLM_PROVIDER", "FUND_AGENT_LLM_MODEL", "FUND_AGENT_LLM_BASE_URL")
for name in required:
    print(name + ": " + ("present" if os.environ.get(name, "").strip() else "absent"))
custom_key_var = bool(os.environ.get("FUND_AGENT_LLM_API_KEY_ENV_VAR", "").strip())
api_var = os.environ.get("FUND_AGENT_LLM_API_KEY_ENV_VAR", "FUND_AGENT_LLM_API_KEY")
print("FUND_AGENT_LLM_API_KEY_ENV_VAR: " + ("present" if custom_key_var else "absent"))
print("effective_api_key_value: " + ("present" if os.environ.get(api_var, "").strip() else "absent"))
for name in ("FUND_AGENT_LLM_TIMEOUT_SECONDS", "FUND_AGENT_LLM_WRITER_TIMEOUT_SECONDS", "FUND_AGENT_LLM_AUDITOR_TIMEOUT_SECONDS", "FUND_AGENT_LLM_REPAIR_TIMEOUT_SECONDS", "FUND_AGENT_LLM_TIMEOUT_MAX_ATTEMPTS", "FUND_AGENT_LLM_TIMEOUT_BACKOFF_SECONDS", "FUND_AGENT_LLM_MAX_OUTPUT_CHARS"):
    print(name + ": " + ("set" if os.environ.get(name, "").strip() else "unset"))
try:
    load_llm_provider_config_from_env()
except LLMProviderConfigError as exc:
    text = str(exc)
    if "FUND_AGENT_LLM_PROVIDER" in text:
        field = "missing FUND_AGENT_LLM_PROVIDER"
    elif "FUND_AGENT_LLM_MODEL" in text:
        field = "missing FUND_AGENT_LLM_MODEL"
    elif "FUND_AGENT_LLM_BASE_URL" in text:
        field = "missing FUND_AGENT_LLM_BASE_URL"
    elif "API key" in text:
        field = "missing API key value"
    elif "unsupported provider" in text:
        field = "unsupported provider"
    elif "URL" in text:
        field = "invalid base URL shape"
    else:
        field = "invalid typed config"
    print("config_validation: fail")
    print("config_error_class: LLMProviderConfigError")
    print("config_error_field: " + field)
else:
    print("config_validation: pass")'
```

The command is intentionally local and non-live: it reads `os.environ`, invokes typed config validation, and performs no HTTP request. If the shell cannot safely run this exact command, the evidence executor must stop and ask controller judgment before substituting another readiness implementation.

### 5.3 Exactly One Live Evidence Command

If presence-only readiness passes, the evidence executor is authorized to run exactly one live command:

```bash
uv run fund-analysis analyze 006597 --report-year 2024 --use-llm
```

Command constraints:

- no `--llm-progress` unless controller explicitly wants progress evidence;
- no timeout, attempt, backoff, max-output, model, endpoint, prompt, repair-budget or provider override;
- no second live command;
- no deterministic fallback command;
- no endpoint reachability check before or after the command;
- no PASS-only or chapter-only live probe in this gate.

The evidence artifact must record:

- command string;
- exit code;
- stdout byte count and whether stdout is empty;
- stderr safe summary only;
- retained artifact path if one is produced;
- whether the run reached orchestration;
- `orchestration_status`;
- `final_assembly_status`;
- per-chapter matrix with `chapter_id`, status, stop reason, failure category and failure subcategory;
- safe runtime diagnostics allowlist fields, if present.

## 6. Outcome Classification

### 6.1 Environment Blocked

Classify as `environment_blocked` when:

- required provider/model/base-url/API-key presence fails;
- typed config validation fails;
- provider construction fails before orchestration;
- this Codex/evidence shell does not inherit the configured env.

Evidence requirements:

- presence-only output;
- no live command;
- no secret values.

Next action:

- fix environment inheritance outside the repo or provide a correctly inherited execution shell, then rerun this gate from presence-only readiness after controller authorization.

### 6.2 Endpoint Availability Residual Still Active

Classify as `endpoint_availability_residual_active` when:

- readiness passes;
- the single live command reaches provider calls;
- retained artifact shows broad `ReadTimeout` / zero response bytes under small prompts again;
- fail-closed semantics remain intact.

Evidence requirements:

- live command exit code and stdout-empty evidence;
- retained artifact manifest/summary path;
- per-chapter matrix;
- runtime diagnostics showing timeout category and elapsed/time-budget fields.

Next action:

- stop and hand controller a same-run endpoint residual. Do not change runtime defaults in this gate.

### 6.3 Provider Runtime Residual Narrowed

Classify as `provider_runtime_residual_narrowed` when:

- readiness passes;
- only a subset of chapters or operations times out;
- other chapters produce accepted conclusions or non-timeout blockers.

Evidence requirements:

- same-run chapter matrix;
- accepted/failed split;
- operation-specific runtime diagnostics;
- explicit blocker taxonomy separating timeout, prompt contract, audit rule and code-contract blockers.

Next action:

- controller decides whether to return to Real LLM smoke re-baseline evidence, open a narrower provider-runtime calibration gate, or defer to content-contract calibration. No automatic Chapter acceptance calibration.

### 6.4 Non-Timeout Provider Runtime Error

Classify as `provider_runtime_error_non_timeout` when:

- readiness passes;
- the single live command reaches provider calls or provider response parsing;
- the retained artifact or stderr safe summary reports provider runtime failures other than timeout, including `llm_rate_limited`, `llm_malformed_response`, `llm_network_error`, HTTP error, malformed response or rate limiting;
- fail-closed semantics remain intact.

Evidence requirements:

- live command exit code and stdout-empty evidence;
- retained artifact manifest/summary path if one is produced;
- per-chapter matrix;
- provider runtime category, safe HTTP status scalar if present, response character count scalar if present, and operation labels;
- no raw provider response, request body, headers, endpoint URL or provider message body.

Next action:

- stop and hand controller a same-run non-timeout provider residual. Do not classify it as endpoint availability, do not retry, and do not change provider/default/runtime/budget in this gate.

### 6.5 Smoke Accepted

Classify as `real_llm_smoke_accepted_candidate` only when:

- exit code is `0`;
- stdout contains a complete final report;
- all public chapters `0-7` are present and ordered;
- quality/final assembly status is accepted;
- stderr and artifacts are secret-safe;
- no deterministic fallback was used.

Next action:

- evidence review and controller judgment for Real LLM smoke re-baseline acceptance. Do not proceed directly to golden/readiness, score-loop, PR or release.

### 6.6 Safety Blocker

Classify as `safety_blocker` when any of these occur:

- incomplete run prints partial report to stdout;
- incomplete run exits `0`;
- deterministic fallback appears;
- retained artifact or evidence leaks secret/raw prompt/raw provider response;
- source/test/config/runtime default diff appears;
- live command count exceeds one;
- endpoint/model/timeout/default is changed.

Next action:

- stop immediately; do not run more live commands.

## 7. Secret And Redaction Checks

The evidence executor must scan only the new evidence artifact and safe retained artifact summaries. Do not paste matching secret values into the evidence artifact.

Minimum scan patterns:

```bash
rg -n "Authorization|Bearer |sk-[A-Za-z0-9]|FUND_AGENT_LLM_API_KEY=|api_key.*=|raw_provider|raw_response|raw_audit|prompt=" docs/reviews reports/llm-runs
```

The evidence executor must also adapt the scan to the known configured provider key format if it is not OpenAI-style `sk-...`, without printing the key or key prefix value into the artifact. If the scan finds only policy text in review artifacts, document it as safe policy-text matches. If it finds a value-like secret, raw prompt, raw provider response, raw audit response, base URL value or Authorization header in the new evidence output, classify as `safety_blocker`.

## 8. Acceptance Criteria

| ID | Criterion | Required evidence | Blocking failure |
|---|---|---|---|
| A1 | Plan preserves current gate order | This artifact, plan reviews, controller judgment | Live command before plan review/judgment |
| A2 | Provider readiness is presence-only | Safe boolean output and config validation result | Any provider value, full env or HTTP call in readiness |
| A3 | Exactly one live command | Command log and execution count | More than one live provider/probe command |
| A4 | Defaults unchanged | Command has no overrides; git diff has no config/runtime change | Timeout/attempt/backoff/model/endpoint/default changed |
| A5 | Incomplete fail-closed remains intact | Exit code, stdout byte count, stderr safe summary, retained artifact | Partial stdout, exit 0, deterministic fallback |
| A6 | Same-run direct evidence | New command output plus retained artifact from that run | Historical artifact substituted |
| A7 | Secret-safe diagnostics | Redaction scan and allowlist fields | Secret/raw prompt/raw response leak |
| A8 | Boundary guardrails preserved | Forbidden-scope checklist and git integrity | Source/test/config/runtime/quality/golden/Agent/score-loop drift |
| A9 | Clear next residual classification | One of Section 6 classifications with evidence | Mixed historical/current root cause inference |

## 9. Review Handoff

Required plan reviews before evidence execution:

- AgentDS review: focus on first-principles evidence logic, environment-blocked stop rule, same-run direct evidence requirements and taxonomy correctness.
- AgentMiMo review: focus on forbidden-scope containment, secret-safety, command singularity, fail-closed/no-fallback/stdout semantics and provider default preservation.

Each review must return `PASS`, `NEEDS_FIX` or `BLOCKED`. Blocking findings must be fixed in the plan and re-reviewed before controller judgment.

## 10. Controller Judgment Requirements

Before the evidence executor runs any live command, controller judgment must explicitly state:

- this plan is accepted;
- the exact presence-only readiness check is authorized;
- the exact single live command is authorized only if readiness passes;
- no provider/default/runtime/budget change is authorized;
- no Chapter acceptance calibration is authorized;
- no Agent runtime, multi-year runtime, score-loop, golden/readiness, PR/push/release work is authorized;
- the evidence executor must stop after the one live command or earlier stop condition.

## 11. Residual Owners

| Residual | Owner | Handling |
|---|---|---|
| `environment_blocked` | provider config/operator shell owner | Fix env inheritance outside repo; no code change implied |
| `endpoint_availability_residual_active` | provider endpoint operator / future calibration controller | Stop with same-run evidence; do not tune defaults in this gate |
| `provider_runtime_error_non_timeout` | provider runtime operator / future calibration controller | Stop with same-run evidence; do not retry or reclassify as endpoint availability |
| `provider_runtime_residual_narrowed` | future provider-runtime calibration owner | New scoped gate if controller accepts |
| content contract or audit-rule blocker | future chapter/content calibration owner | Only after provider timeout is no longer first blocker |
| safety blocker | controller | Stop immediately and open separate remediation gate |

## 12. Final Plan Verdict

This plan is ready for independent plan review. It intentionally does not authorize a live provider command by itself. The next valid step is DS/MiMo plan review, then controller judgment, then evidence execution only if accepted.
