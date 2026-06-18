# MVP Post-Operator Provider Availability Evidence Gate Plan

## 1. Scope And Classification

- Phase: `MVP typed-template-to-agent report generation stabilization phase`
- Gate: `post-operator provider availability evidence gate`
- Classification: `heavy`
- Role of this artifact: plan only; not evidence execution, implementation, review, PR, push, release, provider default change, or endpoint diagnostic.
- User/operator signal: current shell LLM configuration is reported complete and a secret-safe local presence check passed on 2026-06-06.

Classification rationale under `AGENTS.md`: this gate may authorize exactly one live provider-backed `--use-llm` evidence command after a prior same-run `provider_runtime_error_non_timeout` residual. Even though no code/config/default change is planned, live provider evidence can affect Real LLM smoke re-baseline sequencing, Chapter acceptance calibration eligibility, and future provider/runtime-budget routing. Use the conservative `heavy` classification.

This plan itself authorizes no live command until independent plan review and controller judgment accept it.

## 2. Authoritative Inputs

- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/reviews/mvp-future-live-provider-calibration-evidence-gate-live-rerun-controller-judgment-20260605.md`
- `docs/reviews/mvp-provider-runtime-non-timeout-residual-disposition-diagnostic-plan-controller-judgment-20260605.md`
- Current secret-safe config presence check output:
  - `FUND_AGENT_LLM_PROVIDER: present`
  - `FUND_AGENT_LLM_MODEL: present`
  - `FUND_AGENT_LLM_BASE_URL: present`
  - `FUND_AGENT_LLM_API_KEY_ENV_VAR: absent`
  - `effective_api_key_value: present`
  - `config_validation: pass`

Workspace preflight at plan time:

- Branch: `feat/mvp-llm-incomplete-run-artifacts`
- Dirty workspace includes unrelated tracked `pyproject.toml` and multiple unrelated untracked files. They are not evidence for this gate and must not be staged or committed by this gate.

## 3. Gate Question

After operator/environment availability is reported restored, can exactly one unchanged-default live `006597 / 2024 --use-llm` command produce decision-useful evidence without violating fail-closed, stdout, fallback, provider-default, or secret-safety boundaries?

This gate answers only the current availability/evidence question. It does not prove permanent provider health, does not tune budgets, does not change defaults, and does not enter Chapter acceptance calibration unless a later controller judgment uses accepted evidence to open that separate gate.

## 4. Non-Goals And Forbidden Actions

Forbidden:

- no endpoint reachability probe, curl, handwritten HTTP, socket/DNS probe, account metadata query, or private provider API call;
- no PASS-only timing probe;
- no retry command or second live `analyze --use-llm` command in this gate;
- no timeout, attempt, backoff, max-output, endpoint, model, provider, API-key, runtime budget, or provider default override;
- no deterministic fallback command;
- no source, tests, config, README, design doc, control doc, startup packet, template, quality gate, golden/readiness, Host/Agent, multi-year runtime, score-loop, PR/push/release change;
- no Chapter acceptance calibration in this gate;
- no raw prompt, writer draft, raw provider response, raw audit response, provider message body, API key, Authorization header, bearer token, full environment dump, model value, or base URL value in artifacts.

Allowed after review and controller judgment:

- one secret-safe presence-only readiness check with no HTTP call;
- if readiness passes, exactly one unchanged-default live command:

```bash
uv run fund-analysis analyze 006597 --report-year 2024 --use-llm
```

## 5. Evidence Procedure

### E0. Preflight

- Record branch and `git status --short`.
- Confirm the only accepted gate input is the new operator/environment availability signal plus the existing accepted residual disposition.
- Do not clean, delete, stage, or commit unrelated dirty files.

### E1. Presence-Only Readiness

Run the same secret-safe typed config presence check shape used by prior accepted evidence gates:

- print only `present` / `absent` / `unset` booleans and coarse validation labels;
- invoke `load_llm_provider_config_from_env()` to validate typed config;
- perform no HTTP call or endpoint reachability check.

Stop if config validation fails.

### E2. Single Live Evidence Command

Only if E1 passes, run exactly once:

```bash
uv run fund-analysis analyze 006597 --report-year 2024 --use-llm
```

Constraints:

- no CLI overrides;
- no environment overrides;
- no retry;
- no second command if the first exits non-zero;
- no fallback command;
- capture exit code, stdout byte count, safe stderr summary, retained artifact path if emitted, and elapsed time.

### E3. Retained Artifact Inspection

If a retained artifact path is emitted, inspect only safe structured files and fields:

- manifest kind/schema;
- fund/year;
- orchestration and final assembly status;
- chapter matrix status, stop reason, failure category, failure subcategory, operation, attempts, elapsed scalar, prompt-cost scalar, timeout root-cause hint, and accepted draft/conclusion flags;
- Host terminal status and timeout/cancel classification.

Do not read or record raw prompts, raw provider bodies, raw audit responses, headers, or secret-bearing values.

### E4. Secret And Scope Scans

Run redaction/scope checks over the new evidence artifact and retained artifact path:

- fail on API key value, Authorization header, bearer token, raw prompt, raw provider response, raw audit response, provider body, model value, base URL value, or full env dump;
- fail on unrelated source/config/default/runtime/golden/score/Agent/PR/release diffs being attributed to this gate.

## 6. Outcome Taxonomy

| Outcome | Evidence shape | Next routing |
|---|---|---|
| `environment_blocked` | E1 config validation fails | Stop; no live command; operator/environment owner |
| `provider_runtime_error_non_timeout` | live command reaches provider path but all/multiple chapters fail with network/non-timeout provider runtime error | Stop; no retry; provider runtime operator or separate reviewed diagnostic gate |
| `provider_runtime_timeout` | live command fails with timeout categories under unchanged defaults | Stop; route to provider runtime budget/calibration controller |
| `chapter_content_or_contract_blocked` | at least one chapter reaches draft/audit semantics and fails on prompt contract, audit rule, missing evidence, unknown anchor, or code-bug taxonomy | Stop; evidence may support a later Chapter acceptance calibration or contract diagnostic gate |
| `accepted_report` | command exits `0` and report output is accepted through current fail-closed path | Stop; controller decides whether Real LLM smoke re-baseline can be accepted or whether further review is required |
| `unexpected_stdout_on_failure` | non-zero exit emits report-like stdout | Stop; fail-closed regression investigation gate required |
| `secret_safety_blocker` | artifact/output leaks forbidden values | Stop immediately; remediation gate required |

## 7. Acceptance Criteria

| ID | Criterion | Blocking failure |
|---|---|---|
| A1 | Gate is classified `heavy` with provider/runtime evidence rationale | classified as `fast_path` or unreasoned `standard` |
| A2 | Plan separates review/controller judgment from live execution | plan authorizes immediate live command without judgment |
| A3 | Procedure is singular and unchanged-default | more than one live command, retry, override, or default change allowed |
| A4 | Presence readiness is secret-safe and non-live | prints env values, model/base URL values, API key, or performs HTTP |
| A5 | Fail-closed semantics are measurable | stdout byte count, exit code, fallback absence, retained artifact are not captured |
| A6 | Outcome taxonomy preserves current residual distinctions | network, timeout, content/contract, accepted, and regression outcomes are conflated |
| A7 | Chapter calibration remains separate | plan enters calibration directly |
| A8 | Endpoint/network probing remains separate | plan authorizes curl, DNS/socket, private API call, or PASS-only probe |
| A9 | Secret safety is enforceable | artifacts may include raw prompt/provider/audit body or secret-bearing values |
| A10 | Dirty workspace is contained | unrelated `pyproject.toml` or untracked artifacts are staged/committed/used as gate evidence |

## 8. Required Reviews

Before controller judgment, obtain two independent plan reviews.

AgentMiMo focus:

- no live command before controller judgment;
- no endpoint probe/PASS-only/retry/default change;
- command singularity and unchanged-default guarantees;
- fail-closed stdout/fallback/retained-artifact evidence;
- secret-safety scan sufficiency.

AgentDS focus:

- first-principles routing from operator availability signal to exactly one evidence command;
- same-source root-cause discipline;
- outcome taxonomy correctness;
- separation from Chapter calibration, provider budget changes, Agent runtime, score-loop, golden/readiness and PR/release;
- dirty workspace containment.

Reviewer verdict format: `PASS`, `PASS_WITH_NON_BLOCKING_OBSERVATIONS`, or `BLOCKED_WITH_REQUIRED_FIXES`.

## 9. Controller Judgment Requirements

Controller judgment must explicitly decide:

- whether reviews pass or require plan fixes;
- whether E1 presence-only readiness is authorized;
- whether exactly one unchanged-default live command is authorized if E1 passes;
- evidence artifact path to write after execution;
- stop conditions and residual owner for each outcome taxonomy row.

Until that judgment exists, no live provider command is authorized.
