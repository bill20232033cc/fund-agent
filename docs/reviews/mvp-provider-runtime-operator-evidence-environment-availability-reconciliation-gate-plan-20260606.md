# MVP Provider Runtime Operator Evidence / Environment Availability Reconciliation Gate Plan

## 1. Scope And Classification

- Phase: `MVP typed-template-to-agent report generation stabilization phase`
- Gate: `provider runtime operator evidence / environment availability reconciliation gate`
- Classification: `heavy`
- Role: plan only; not evidence execution, implementation, live provider retry, endpoint diagnostic, provider default change, PR, push, release, or Chapter calibration
- Accepted checkpoint before this gate: `508071c gateflow: accept post-operator availability closeout`

Classification rationale: this gate may change accepted control truth for provider-runtime evidence routing by deciding whether the 2026-06-06 actual live evidence can be accepted as `provider_runtime_error_non_timeout`. It does not change code or provider behavior, but it affects whether the current residual remains operator-owned, whether Chapter calibration stays blocked, and how future diagnostic gates may be opened. Under `AGENTS.md`, use `heavy`.

## 2. Authoritative Inputs

- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/reviews/mvp-provider-runtime-non-timeout-residual-disposition-diagnostic-plan-controller-judgment-20260605.md`
- `docs/reviews/mvp-post-operator-provider-availability-evidence-gate-closeout-disposition-20260606.md`
- `docs/reviews/mvp-post-operator-provider-availability-evidence-gate-live-evidence-20260606.md`
- `reports/llm-runs/006597-2024-20260606T090435Z-host_run_f00dc5dcf8b249c/summary.json`

Preflight at plan time:

- Branch: `feat/mvp-llm-incomplete-run-artifacts`
- Dirty workspace includes unrelated tracked `pyproject.toml` and unrelated untracked files, including `fund_agent/tools/`, `reports/manual-llm-smoke/`, `reviews/`, `scripts/claude_mimo_simple.py`, and historical review artifacts. They are not evidence for this gate and must not be staged, committed, cleaned, deleted, or used as current gate evidence.

## 3. Gate Question

Can the repository accept the 2026-06-06 actual live evidence outcome as `provider_runtime_error_non_timeout`, while explicitly preserving the stdout/stderr capture limitation and keeping the 2026-06-06 artifacts not accepted as `environment_blocked` evidence?

This gate answers only that diagnostic-entry reconciliation question. It does not prove provider health, does not retry provider calls, does not probe endpoints, does not tune budgets, and does not open Chapter calibration.

## 4. Non-Goals And Forbidden Actions

Forbidden:

- no live `--use-llm` command;
- no retry or second live command;
- no endpoint, DNS, socket, curl, private provider API, account metadata, or PASS-only probe;
- no fallback command;
- no provider, model, base URL, API key, timeout, attempt, backoff, max-output, runtime budget, or provider default change;
- no source, test, config, README, template, design doc, Host/Agent, multi-year runtime, score-loop, golden/readiness, PR, push, or release change;
- no Chapter acceptance calibration;
- no staging or committing unrelated dirty files.

Allowed:

- inspect existing safe structured artifacts under `docs/reviews/` and `reports/llm-runs/.../summary.json`;
- produce this plan, two independent plan reviews, and controller judgment under `docs/reviews/`;
- if controller accepts, sync only `docs/current-startup-packet.md` and `docs/implementation-control.md`;
- create one local accepted checkpoint that stages only this gate's review artifacts and the two control documents.

## 5. Evidence Matrix

| Evidence item | Direct source | Acceptance use |
|---|---|---|
| 2026-06-06 was not `environment_blocked` | `docs/reviews/mvp-post-operator-provider-availability-evidence-gate-live-evidence-20260606.md` records E1 `passed` and `executed_once` | Blocks any control sync that would treat the artifacts as `environment_blocked` |
| Actual outcome is `provider_runtime_error_non_timeout` | live evidence Section 7 and retained `summary.json` | Candidate accepted outcome for reconciliation |
| Runtime category is provider network/non-timeout | `summary.json` has all body chapters `failed`, `stop_reason=llm_network_error`, `failure_category=provider_runtime`, runtime `error_type=ConnectError`, `provider_runtime_category=network`, `timeout_root_cause_hint=non_timeout_provider_runtime` | Supports residual owner provider runtime operator / environment owner |
| No chapter content calibration evidence exists | `summary.json` has `accepted_draft_present=false` and `accepted_conclusion_present=false` for chapters 1-6 | Keeps Chapter calibration blocked |
| stdout/stderr capture limitation exists | live evidence records `stdout byte count=not_independently_measured` and capture note | Controller must preserve limitation instead of claiming strict stdout proof |
| Secret/scope safety is acceptable for docs-only reconciliation | live evidence redaction/scope scan and retained artifact redaction fields | Allows control sync if limitation is explicit |

## 6. Acceptance Criteria

| ID | Criterion | Blocking failure |
|---|---|---|
| A1 | Gate is classified `heavy` and scoped to reconciliation only | classification omitted or scope allows runtime/provider behavior change |
| A2 | 2026-06-06 artifacts remain not accepted as `environment_blocked` | any artifact/control text treats them as environment-blocked accepted evidence |
| A3 | Actual 2026-06-06 outcome may be accepted only as `provider_runtime_error_non_timeout` | outcome conflated with timeout, content, accepted report, or environment block |
| A4 | stdout/stderr capture limitation is explicitly preserved | control sync claims independently measured stdout byte count or stdout empty proof |
| A5 | No new live/provider/probe/fallback/default-change action is performed or authorized | any new command/probe/retry/default change appears |
| A6 | Chapter calibration remains blocked | sync opens calibration despite no accepted drafts/conclusions |
| A7 | Residual owner remains provider runtime operator / environment owner | owner shifts to repo code, template, budget, or calibration without evidence |
| A8 | Dirty workspace stays isolated | `pyproject.toml`, `fund_agent/tools/`, or unrelated untracked files are staged/committed/used as evidence |
| A9 | Control sync is limited to `docs/current-startup-packet.md` and `docs/implementation-control.md` | source/config/design/template/README/runtime files are edited |
| A10 | Next entry is gated by operator evidence, environment availability, or new controller-authorized diagnostic request | next entry authorizes direct retry or broader phase work |

## 7. Review Requirements

Before controller judgment, obtain two independent plan reviews:

- AgentMiMo focus: scope boundaries, no live retry/probe/default change, capture limitation handling, dirty workspace isolation, and accepted outcome wording.
- AgentDS focus: same-source evidence discipline, outcome taxonomy, residual owner, separation from Chapter calibration/Agent runtime/score-loop/release, and control sync criteria.

Reviewer verdict format: `PASS`, `PASS_WITH_NON_BLOCKING_OBSERVATIONS`, or `BLOCKED_WITH_REQUIRED_FIXES`.

## 8. Controller Judgment Requirements

Controller judgment must explicitly decide:

- whether both reviews pass or require plan fixes;
- whether 2026-06-06 actual live evidence outcome is accepted as `provider_runtime_error_non_timeout`;
- whether stdout/stderr capture limitation is acceptable for control truth, and exactly how it must be preserved;
- whether the 2026-06-06 artifacts remain unaccepted as `environment_blocked`;
- whether control sync is authorized and which files may be edited;
- residual owner and next entry point;
- exact staging boundary for local accepted checkpoint.

Until that judgment exists, do not sync control documents and do not create an accepted checkpoint for this gate.
