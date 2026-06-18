# MVP Real LLM Chapter Acceptance Live Evidence Gate Plan

## 1. Scope And Classification

- Phase: `MVP typed-template-to-agent report generation stabilization phase`
- Gate: `Real LLM chapter acceptance live evidence gate`
- Classification: `heavy`
- Role of this artifact: plan only; not live execution, implementation, code review, commit, PR, push, release, provider default change, runtime-budget change, endpoint diagnostic, score-loop, golden/readiness or Agent runtime work.

Classification rationale under `AGENTS.md`: this gate may authorize a provider-backed `--use-llm` report generation command and can affect whether the `Real LLM smoke re-baseline gate` remains blocked by chapter content/contract/audit behavior or reaches a complete fail-closed accepted report. Use the conservative `heavy` classification.

This plan itself authorizes no live LLM command. Live execution requires plan review, controller judgment, and explicit user authorization for the exact command boundary.

## 2. Goal / Motivation

Slice 1A-1G and the no-live closeout accepted local fixes/evidence for all known deterministic residual routes from the retained post-config live artifact. The remaining question is live-only:

Can exactly one unchanged-default `006597 / 2024 --use-llm` command, after secret-safe readiness, show that the prior chapter blockers are resolved or produce a new same-source chapter/provider residual without weakening fail-closed behavior?

This gate must separate three facts:

- local deterministic coverage of known residuals;
- live body chapter acceptance status for chapters 1-6;
- complete fail-closed 0-7 report acceptance status.

## 3. Authoritative Inputs

- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/reviews/mvp-post-config-live-smoke-evidence-disposition-20260607.md`
- `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-slice1a-1g-no-live-closeout-controller-judgment-20260607.md`

Workspace preflight at plan time:

- Branch: `feat/mvp-llm-incomplete-run-artifacts`
- Known unrelated tracked dirty file: `pyproject.toml`; this gate must not touch, stage, commit or use it as evidence.
- Existing untracked review artifacts are local evidence chain only; do not delete, clean, stage or reclassify them in this gate.

## 4. Allowed Artifacts

Allowed plan/review/controller artifacts:

- `docs/reviews/mvp-real-llm-chapter-acceptance-live-evidence-gate-plan-20260607.md`
- `docs/reviews/mvp-real-llm-chapter-acceptance-live-evidence-gate-plan-review-ds-20260607.md`
- `docs/reviews/mvp-real-llm-chapter-acceptance-live-evidence-gate-plan-review-mimo-20260607.md`
- `docs/reviews/mvp-real-llm-chapter-acceptance-live-evidence-gate-plan-controller-judgment-20260607.md`

Allowed later evidence artifacts only after accepted plan judgment and explicit live authorization:

- `docs/reviews/mvp-real-llm-chapter-acceptance-live-evidence-gate-evidence-20260607.md`
- retained local `reports/llm-runs/...` artifact emitted by the unchanged-default command if the command fails closed.

Allowed control sync only after accepted evidence review/judgment:

- `docs/current-startup-packet.md`
- `docs/implementation-control.md`

## 5. Non-Goals And Forbidden Actions

Forbidden:

- no live LLM command before plan review, controller judgment and explicit user authorization;
- no more than one live `analyze --use-llm` command in this gate;
- no retry command if the command fails or times out;
- no endpoint probe, curl, DNS/socket probe, private provider API call, account metadata query, PASS-only timing probe or handwritten HTTP request;
- no CLI/env overrides for timeout, attempts, backoff, max output, provider, endpoint, model, API key, prompt mode, budget or runtime;
- no provider/default/runtime/budget/config/source/test/template/README/design-code/schema/quality gate/golden/readiness/score-loop/Host/Agent/multi-year/PR/push/release change;
- no deterministic fallback command;
- no claim that local deterministic coverage equals live acceptance;
- no raw prompt, writer draft, raw provider response, raw audit response, provider message body, API key, Authorization header, bearer token, full environment dump, model value or base URL value in artifacts.

## 6. Evidence Procedure After Authorization

### E0. Preflight

- Run `git branch --show-current`.
- Run `git status --short`.
- Re-read `docs/current-startup-packet.md` and `docs/implementation-control.md`.
- Confirm current gate still says Slice 1A-1G and no-live closeout are accepted locally and live acceptance remains unproven.
- Stop if another gate has changed the next entry point or if workspace ownership becomes unclear.

### E1. Presence-Only Readiness

Run a secret-safe typed config presence check:

- print only `present` / `absent` / `unset` booleans and coarse validation labels;
- invoke `load_llm_provider_config_from_env()` to validate typed config;
- perform no HTTP call or endpoint reachability check;
- do not print model, base URL, API key env value or any secret-bearing value.

Stop if config validation fails. Classification: `environment_blocked`.

### E2. Single Live Evidence Command

Only if E1 passes and explicit live authorization covers the command, run exactly once:

```bash
uv run fund-analysis analyze 006597 --report-year 2024 --use-llm
```

Constraints:

- unchanged defaults only;
- no environment overrides;
- no retry and no second command;
- no fallback command;
- capture exit code, elapsed time, stdout byte count, stderr safe summary and retained artifact path if emitted.

### E3. Result Inspection

If the command exits `0`:

- treat stdout as candidate accepted report output;
- verify report-like stdout is present;
- record whether chapters `0-7` are present in render order;
- do not claim final gate acceptance until evidence review confirms fail-closed acceptance shape.

If the command exits non-zero:

- stdout must be empty or non-report-like;
- retained artifact path should be captured if emitted;
- inspect only safe structured artifact fields: manifest kind/schema, fund/year, orchestration status, final assembly status, chapter matrix status, stop reason, failure category, failure subcategory, operation, attempts, elapsed scalar, prompt-cost scalar, timeout root-cause hint, accepted draft/conclusion flags and Host terminal status.

Do not read or record raw prompts, raw provider bodies, raw audit responses, headers or secret-bearing values.

### E4. Comparison Matrix

Produce a matrix comparing the new live result against the accepted post-config baseline:

| Chapter | Baseline category/subcategory | New status | New category/subcategory | Accepted draft? | Accepted conclusion? | Routing |
|---|---|---|---|---|---|---|

Required routing values:

- `live_accepted`
- `known_residual_resolved_live`
- `new_chapter_content_or_contract_residual`
- `provider_runtime_timeout`
- `provider_runtime_error_non_timeout`
- `environment_blocked`
- `unexpected_stdout_on_failure`
- `secret_safety_blocker`
- `artifact_shape_blocker`

### E5. Secret And Scope Scans

Run local scans over the new evidence artifact and any retained artifact path:

- fail on API key values, Authorization header, bearer token, raw prompt, raw provider response, raw audit response, provider body, model value, base URL value or full env dump;
- fail if unrelated source/config/default/runtime/golden/score/Agent/PR/release diffs are attributed to this gate.

## 7. Outcome Taxonomy

| Outcome | Evidence shape | Next routing |
|---|---|---|
| `environment_blocked` | E1 config validation fails | Stop; operator/environment owner |
| `accepted_report_candidate` | command exits `0`, report-like stdout exists, chapters `0-7` appear in order | Stop; evidence review decides whether Real LLM smoke re-baseline can be accepted or needs further review |
| `partial_chapter_acceptance` | some chapters accept live but final assembly remains incomplete | Stop; route remaining chapter rows to same-source chapter residual gate |
| `chapter_content_or_contract_blocked` | live artifact shows prompt contract, audit rule, missing evidence, unknown anchor, code-bug or parse blocker | Stop; open deterministic residual evidence gate for only new rows |
| `provider_runtime_timeout` | live command fails with timeout category under unchanged defaults | Stop; provider runtime budget/calibration owner |
| `provider_runtime_error_non_timeout` | live command reaches provider path but fails with network/non-timeout provider runtime category | Stop; provider runtime operator or separately reviewed diagnostic gate |
| `unexpected_stdout_on_failure` | non-zero exit emits report-like stdout | Stop; fail-closed regression gate |
| `artifact_shape_blocker` | retained artifact is missing, malformed or lacks required safe fields | Stop; artifact retention/diagnostic gate |
| `secret_safety_blocker` | any artifact/output leaks forbidden values | Stop immediately; remediation gate |

## 8. Acceptance Criteria

| ID | Criterion | Blocking failure |
|---|---|---|
| A1 | Plan is `heavy` and explains live evidence risk | classified lighter without rationale |
| A2 | Plan separates plan review/controller judgment/user authorization from live execution | plan authorizes immediate live command |
| A3 | Live procedure is singular and unchanged-default | retry, override, second command or default change allowed |
| A4 | Readiness check is presence-only and secret-safe | prints secrets/model/base URL or performs HTTP |
| A5 | Fail-closed behavior is measurable | exit code, stdout byte count, fallback absence or artifact path omitted |
| A6 | Local deterministic coverage is not conflated with live acceptance | evidence may mark live acceptance from local tests only |
| A7 | Outcome taxonomy distinguishes accepted report, partial live chapter acceptance, content/contract blockers, provider timeout and non-timeout runtime errors | categories are conflated |
| A8 | Evidence inspection forbids raw prompt/provider/audit bodies and secret-bearing values | artifact plan can leak forbidden data |
| A9 | Dirty workspace containment is explicit | unrelated `pyproject.toml` or untracked artifacts are used/staged/committed |
| A10 | Next routing remains gated | plan enters implementation, provider tuning, Agent runtime, score-loop, golden/readiness or PR/release directly |

## 9. Required Reviews

Before controller judgment, obtain two independent plan reviews where available.

AgentDS focus:

- first-principles route from no-live closeout to one live acceptance evidence command;
- same-source root-cause discipline;
- separation of local deterministic coverage, live chapter acceptance and complete report acceptance;
- outcome taxonomy and stop conditions.

AgentMiMo focus:

- no live command before authorization;
- command singularity and unchanged-default guarantees;
- secret-safety boundaries;
- fail-closed stdout/artifact evidence;
- dirty workspace containment.

Reviewer verdict format: `PASS`, `PASS_WITH_NON_BLOCKING_OBSERVATIONS`, or `BLOCKED_WITH_REQUIRED_FIXES`.

If a reviewer is unavailable due CLI/provider/tooling failure, controller judgment must record the unavailable reviewer, the exact observed blocker, and whether one independent review is sufficient for this plan gate. It must not use reviewer unavailability as live execution authorization.

## 10. Controller Judgment Requirements

Controller judgment must explicitly decide:

- whether plan reviews pass or require fixes;
- whether the plan is accepted;
- whether E1 presence-only readiness is authorized;
- whether exactly one unchanged-default live command is authorized, or whether explicit user authorization is still required before E2;
- evidence artifact path to write after execution;
- stop conditions and owner for every outcome taxonomy row.

Until that judgment exists and explicit user authorization covers E2, no live provider command is authorized.

## 11. Validation Before Review

Plan validation is local and no-live:

```bash
git diff --check -- docs/reviews/mvp-real-llm-chapter-acceptance-live-evidence-gate-plan-20260607.md
rg -n -- '--use-llm|curl|DNS|retry|timeout|provider/default/runtime/budget|Agent runtime|score-loop|golden/readiness|PR/push/release' docs/reviews/mvp-real-llm-chapter-acceptance-live-evidence-gate-plan-20260607.md
```

Expected:

- `git diff --check` exits `0`;
- `rg` output is reviewed manually to confirm forbidden items are only present in forbidden/non-goal/guardrail text, not as authorized actions.

## 12. Completion Report Format

The planning closeout report must include:

- plan artifact path;
- review artifact paths or reviewer-unavailable evidence;
- controller judgment path;
- explicit statement whether live execution is still blocked pending user authorization;
- confirmation that no live LLM/provider/runtime command ran during planning/review.
