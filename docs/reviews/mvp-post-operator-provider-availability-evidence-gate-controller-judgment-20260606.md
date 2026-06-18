# MVP Post-Operator Provider Availability Evidence Gate Controller Judgment

## 1. Scope

- Phase: `MVP typed-template-to-agent report generation stabilization phase`
- Gate: `post-operator provider availability evidence gate`
- Classification: `heavy`
- Role: controller judgment after plan review; not evidence execution, implementation, PR, push, release, provider default change, endpoint diagnostic, or Chapter calibration
- Plan artifact: `docs/reviews/mvp-post-operator-provider-availability-evidence-gate-plan-20260606.md`
- MiMo review artifact: `docs/reviews/mvp-post-operator-provider-availability-evidence-gate-plan-review-mimo-20260606.md`
- DS review artifact: `docs/reviews/mvp-post-operator-provider-availability-evidence-gate-plan-review-ds-20260606.md`

This judgment decides whether the reviewed plan may proceed to a bounded evidence step. It does not execute that step.

## 2. Current Preflight

- Branch: `feat/mvp-llm-incomplete-run-artifacts`
- Dirty workspace at controller judgment time includes unrelated tracked `pyproject.toml` and multiple unrelated untracked files.
- Gate-related untracked artifacts now include the plan, MiMo review, DS review, and this controller judgment.

Dirty workspace containment remains mandatory:

- do not clean, delete, stage, or commit unrelated files for this gate;
- do not use unrelated dirty files as evidence for this gate;
- if later evidence execution creates an evidence artifact, keep it scoped to this gate and record it explicitly.

## 3. Review Summary

AgentMiMo verdict: `PASS`

- No blocking findings.
- MiMo confirmed no live command before controller judgment, no endpoint probe, no PASS-only probe, no retry, no default override, singular unchanged-default command semantics, fail-closed evidence capture, secret-safety scan coverage, and dirty workspace containment.

AgentDS verdict: `PASS`

- No blocking findings.
- DS confirmed first-principles routing from operator availability signal to one same-source evidence command, same-source root-cause discipline, outcome taxonomy coverage, separation from out-of-scope gates, dirty workspace containment, and controller judgment requirements.
- DS non-blocking observation: mixed per-chapter failure scenarios may overlap taxonomy rows unless controller judgment defines priority.

Controller treatment of DS observation:

- Accepted as non-blocking.
- Mixed outcome classification must preserve per-chapter detail from retained artifacts.
- If `secret_safety_blocker` appears, it has highest priority and stops all further inspection.
- If non-zero failure emits report-like stdout, classify as `unexpected_stdout_on_failure` even if another failure category is also present.
- If provider-runtime failures and content/contract failures coexist, classify the gate outcome as provider-runtime blocked first, while noting any reached content/contract evidence as secondary detail. Provider availability must be reliable before content calibration can be accepted.
- If the command exits `0` and accepted report output is produced through the current fail-closed path without secret-safety or stdout regression findings, classify as `accepted_report`.

## 4. Controller Decision

Decision: `AUTHORIZED_WITH_BOUNDARIES`

The reviewed plan is accepted for evidence execution under the exact boundaries below.

Authorized:

1. One secret-safe presence-only readiness check using the accepted typed config loading path.
2. If and only if the readiness check passes, exactly one live unchanged-default command:

```bash
uv run fund-analysis analyze 006597 --report-year 2024 --use-llm
```

Not authorized:

- no live command before the presence-only readiness check passes;
- no second live command;
- no retry;
- no fallback command;
- no endpoint, DNS, socket, curl, private provider API, account metadata, or PASS-only probe;
- no timeout, attempt, backoff, max-output, endpoint, model, provider, API-key, runtime budget, or default override;
- no source, test, config, README, design, control, startup packet, template, quality gate, golden/readiness, Host/Agent, score-loop, PR, push, or release change;
- no Chapter acceptance calibration inside this gate.

This judgment authorizes the bounded evidence procedure only. It does not claim provider health and does not mark any later calibration or release gate accepted.

## 5. Evidence Artifact Requirement

If execution proceeds, write the evidence report to:

`docs/reviews/mvp-post-operator-provider-availability-evidence-gate-live-evidence-20260606.md`

The evidence report must include:

- branch and `git status --short` preflight;
- E1 presence-only readiness output using only `present`, `absent`, `unset`, and coarse validation labels;
- whether E1 passed or stopped the gate;
- if E1 passed, the single live command string exactly as authorized above;
- live command exit code, elapsed time, stdout byte count, safe stderr summary, retained artifact path if emitted, and whether fallback was absent;
- safe retained artifact inspection limited to structured status fields named in the plan;
- redaction/scope scan result;
- final outcome taxonomy row and residual owner.

Forbidden in the evidence report:

- raw prompt;
- writer draft;
- raw provider response;
- raw audit response;
- provider message body;
- API key;
- Authorization header;
- bearer token;
- full environment dump;
- model value;
- base URL value.

## 6. Stop Conditions And Residual Owners

| Outcome | Stop condition | Residual owner |
|---|---|---|
| `environment_blocked` | E1 config validation fails or required config presence is absent/unset | operator/environment owner |
| `provider_runtime_error_non_timeout` | live command reaches provider path but provider runtime non-timeout errors remain primary | provider runtime operator or separate reviewed diagnostic gate |
| `provider_runtime_timeout` | live command fails under timeout categories with unchanged defaults | provider runtime budget/calibration controller |
| `chapter_content_or_contract_blocked` | provider path reaches draft/audit semantics and primary failure is prompt contract, audit rule, missing evidence, unknown anchor, or code-bug taxonomy | later Chapter acceptance calibration or contract diagnostic gate |
| `accepted_report` | command exits `0` and accepted report output is produced through current fail-closed path | controller decides whether Real LLM smoke re-baseline evidence is sufficient |
| `unexpected_stdout_on_failure` | non-zero exit emits report-like stdout | fail-closed regression investigation gate |
| `secret_safety_blocker` | any output or artifact leaks forbidden secret/raw values | remediation gate; stop immediately |

Mixed outcomes must be recorded with per-chapter detail and classified using the priority rules in Section 3.

## 7. Final Judgment

The gate has completed plan and independent plan review requirements.

Controller authorizes E1 and, if E1 passes, exactly one unchanged-default live evidence command. No live command has been executed by this judgment.
