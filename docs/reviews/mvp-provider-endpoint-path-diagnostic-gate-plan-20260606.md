# MVP Provider Endpoint/Path Diagnostic Gate Plan

## 1. Scope And Classification

- Phase: `MVP typed-template-to-agent report generation stabilization phase`
- Gate: `provider endpoint/path diagnostic gate`
- Classification: `heavy`
- Role: planning/controller gate only. Define the diagnostic sequence for typed provider config, derived adapter URL path, and a future same-process adapter call, but do not execute any diagnostic command in this gate.

Classification rationale: this gate may affect the accepted routing of the active `provider_runtime_error_non_timeout` residual. It does not change code, provider defaults, runtime budget, environment, Chapter calibration, Agent runtime, score-loop, PR, or release state, but it decides whether repo adapter path semantics are internally consistent with the configured provider endpoint. Under `AGENTS.md`, choose `heavy`.

## 2. Authoritative Inputs

- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `fund_agent/config/llm.py`
- `fund_agent/services/llm_provider.py`
- `fund_agent/fund/chapter_writer.py`
- Prior accepted provider-runtime control truth: `provider_runtime_error_non_timeout` remains active and Chapter calibration remains blocked because no body chapter has accepted draft/conclusion evidence.

Preflight at plan time:

- Branch: `feat/mvp-llm-incomplete-run-artifacts`
- Dirty workspace contains unrelated tracked `pyproject.toml` and unrelated untracked files. They are not evidence for this gate and must not be staged, committed, cleaned, deleted, or used to infer this gate outcome.

## 3. Gate Question

Does the current repo have a same-source endpoint/path mismatch among typed config, provider adapter URL derivation, and the minimal provider runtime failure path?

This planning gate answers only what exact checks will be used by later evidence/disposition gates. It does not execute local evidence, does not retry a full analyze run, does not probe endpoint reachability outside the production adapter, does not change provider/runtime defaults, and does not open Chapter calibration.

## 4. Non-Goals And Forbidden Actions

Forbidden:

- no `fund-analysis analyze` rerun;
- no retry command or loop;
- no curl, DNS, socket, PASS-only probe, private provider metadata call, direct handwritten HTTP probe, or endpoint fallback;
- no provider, model, base URL, API key, timeout, attempt, backoff, max-output, runtime budget, default, config file, env var, Host, Agent, score-loop, template, README, source, test, PR, push, or release change;
- no deterministic fallback;
- no Chapter acceptance calibration or same-source chapter evidence claim;
- no staging or committing unrelated dirty files;
- no prompt text, raw provider response, API key, Authorization header, bearer token, model value, base URL value, full host value, or full environment dump in artifacts.

Allowed in Gate 1:

- inspect source files and prior safe docs evidence needed to define checks;
- write only this plan, plan reviews, and controller judgment;
- record the queued Gate 2-6 sequence and exact stop conditions.

Allowed only in later gates:

- Gate 2 may run local-only config/path evidence after Gate 1 controller judgment authorizes it;
- Gate 3 may run one same-process adapter minimal check only after Gate 2 is insufficient and a separate Gate 3 controller judgment explicitly authorizes external state;
- later gates may sync control docs only after diagnostic disposition is accepted.

## 5. Check A: Local-Only Config/Path Reconciliation

Gate 2 will run a secret-safe Python inspection using existing repo code only:

- load `load_llm_provider_config_from_env()`;
- print only presence/coarse labels:
  - provider present and supported;
  - model present, without model value;
  - base URL present and shape category only: `absolute_http_url`, `has_no_query_fragment`;
  - API key env var label: `default` or `explicit_custom`, without printing custom env var name;
  - effective API key present, without value;
  - timeout, operation timeout, max attempts, backoff, max output numeric values;
- derive the adapter URL using current adapter semantics:
  - base URL ending `/chat/completions` stays unchanged;
  - base URL ending `/v1` appends `/chat/completions`;
  - otherwise appends `/v1/chat/completions`;
- print derived URL shape only:
  - scheme category;
  - host present yes/no;
  - path suffix category: `chat_completions`, `v1_chat_completions`, or `unexpected`;
  - no full base URL or host value.

Gate 2 acceptance:

- config validation failure => outcome `local_config_path_blocked`, owner operator/environment;
- derived path suffix `unexpected` => outcome `repo_adapter_path_mismatch`, owner repo controller for a later implementation gate;
- internally consistent config/path but insufficient to explain prior `ConnectError` => outcome `local_config_path_consistent_insufficient`, then request Gate 3 planning/controller judgment for one same-process adapter minimal check.

## 6. Check B: One Same-Process Provider Adapter Minimal Check

Check B is not authorized by Gate 1. It is only a planned future Gate 3 check. Gate 3 may open only if Gate 2 local-only evidence does not produce a sufficient blocking outcome and the controller explicitly authorizes external state.

Gate 3, if opened, will execute exactly one Python process that uses the current production adapter class:

- `OpenAICompatibleChapterLLMClient.generate_chapter()`;
- a minimal `ChapterLLMRequest`;
- short diagnostic system prompt and short diagnostic user prompt requesting a tiny plain response;
- `required_anchor_ids=()`;
- `forbidden_phrases=()`;
- `max_output_chars=128`;
- no fund document access;
- no `fund-analysis analyze`;
- no orchestration;
- no Host;
- no retry command;
- no curl/DNS/socket/PASS-only probe;
- no provider/default/runtime/budget overrides.

The adapter may perform its current timeout-only internal attempts if configured defaults already do so. This gate must not modify attempts, backoff, timeout, or any provider default.

Capture:

- stdout file: `reports/llm-runs/provider-endpoint-path-diagnostic-20260606/stdout.txt`
- stderr file: `reports/llm-runs/provider-endpoint-path-diagnostic-20260606/stderr.txt`
- evidence artifact records only safe summary:
  - exit code;
  - elapsed seconds;
  - stdout/stderr byte counts;
  - typed outcome: `minimal_adapter_success`, `provider_runtime_error_non_timeout`, `provider_runtime_timeout`, `provider_http_error`, `provider_rate_limited`, or `provider_malformed_response`;
  - diagnostic fields only: operation, provider_runtime_category, provider_attempt_index/max_attempts, timeout_seconds, timeout_root_cause_hint if present, status_code if present.

Forbidden in captured evidence artifact:

- prompt text;
- raw response body;
- API key;
- Authorization header;
- bearer token;
- model value;
- base URL value;
- full host value;
- full environment dump.

Acceptance:

- `minimal_adapter_success`: endpoint/path and adapter can complete a minimal same-process call; Chapter calibration still remains blocked until a separate authorized report-generation gate produces accepted same-source draft/conclusion evidence.
- `provider_runtime_error_non_timeout`: preserve operator/provider endpoint-path ownership.
- `provider_runtime_timeout`, `provider_http_error`, `provider_rate_limited`, `provider_malformed_response`: route by typed category only; do not infer exact DNS/TLS/proxy/account root cause from adapter exceptions alone.

## 7. Review Requirements

Before controller judgment, obtain two independent plan reviews:

- AgentDS focus: same-source path logic, outcome taxonomy, Check A gating before Check B, Chapter calibration separation, and owner routing.
- AgentMiMo focus: scope boundaries, secret-safety, no retry/probe/default change, dirty workspace isolation, and capture redaction.

Reviewer verdict format: `PASS`, `PASS_WITH_NON_BLOCKING_OBSERVATIONS`, or `BLOCKED_WITH_REQUIRED_FIXES`.

If a reviewer pane/tool is unavailable, record the pane/tool failure in the corresponding review artifact and use a local fallback review only for that unavailable reviewer path. The controller judgment must state the deviation explicitly.

## 8. Controller Judgment Requirements For Gate 1

Controller judgment must explicitly state:

- gate classification is `heavy`;
- checks are exact and bounded;
- Gate 1 authorizes no diagnostic evidence execution;
- Gate 2 local-only config/path evidence is the next gate if the plan is accepted;
- Gate 3 same-process adapter minimal check is not authorized until Gate 2 is insufficient and a separate controller judgment authorizes external state;
- no full analyze rerun, retry command, curl/DNS/PASS-only probe, fallback, config/default/runtime/budget change, Chapter calibration, Agent runtime, score-loop, PR, or release;
- Chapter calibration remains blocked unless a separate authorized report-generation gate produces same-source accepted draft/conclusion evidence;
- dirty workspace isolation remains mandatory;
- this gate may write only plan, plan reviews, and controller judgment.

## 9. Queued Phaseflow Sequence

After Gate 1 is accepted, phaseflow queues:

- Gate 2: `local-only config/path evidence gate`. Confirm the repo's actual provider factory, adapter, httpx/proxy/config source path and output only boolean/hash/redacted evidence.
- Gate 3: `same-process adapter minimal check gate`. Open only if Gate 2 is insufficient and external state is explicitly authorized. Run exactly one minimal provider adapter call; save no raw response.
- Gate 4: `diagnostic disposition gate`. Decide repo implementation, operator defer, or later request-shape/long-running provider path diagnostic.
- Gate 5: `controlled live rerun evidence gate`. Open only if path diagnostic shows environment and repo provider path are available; run exactly one unchanged-default `006597 / 2024 --use-llm`.
- Gate 6: `Chapter acceptance calibration gate`. Open only if at least one body chapter has accepted draft/conclusion evidence.

Long-line order after this blocker: Chapter calibration before Agent runtime planning; Agent runtime before multi-year; multi-year before score-loop. PR/release remain out of scope until separately authorized.

## 10. Validation

Before Gate 1 accepted checkpoint:

- run `git diff --check`;
- run secret scan over Gate 1 plan/review/controller artifacts for API key patterns, `Authorization`, `Bearer`, raw provider response markers, base URL leakage, model value leakage, and full host leakage;
- confirm staging area before accepted checkpoint with `git diff --cached --name-only`;
- confirm `git diff --cached --name-only` includes only this gate's plan/review/controller artifacts;
- confirm no runtime code, tests, config, README, provider defaults, control docs, or report captures are staged in Gate 1.

## 11. Expected Artifact Sequence

1. Plan: `docs/reviews/mvp-provider-endpoint-path-diagnostic-gate-plan-20260606.md`
2. Plan reviews:
   - `docs/reviews/mvp-provider-endpoint-path-diagnostic-gate-plan-review-ds-20260606.md`
   - `docs/reviews/mvp-provider-endpoint-path-diagnostic-gate-plan-review-mimo-20260606.md`
3. Controller judgment:
   - `docs/reviews/mvp-provider-endpoint-path-diagnostic-gate-controller-judgment-20260606.md`

Gate 1 does not write evidence or control sync artifacts. Those belong to later gates.
