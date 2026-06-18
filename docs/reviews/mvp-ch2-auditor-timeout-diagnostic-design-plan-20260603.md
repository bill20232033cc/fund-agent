# MVP Ch2 auditor timeout diagnostic design/plan

## Scope And Role

- Role: planning/design specialist only, not controller.
- Gate: `MVP Ch2 auditor timeout diagnostic design gate`.
- Classification: `heavy`.
- Output: handoff-ready diagnostic design/plan only.
- Actions intentionally not taken: no source, test, config, runtime behavior, provider timeout default, auditor rule, template truth, quality/golden/readiness, score-loop, retained report, PR, staging, commit, push, or live provider call change.

## Required Input Disposition

| Input | Disposition |
|---|---|
| `AGENTS.md` | reviewed from prompt and local file for language, heavy gate, first-principles, same-source evidence and boundary constraints |
| `docs/design.md` | reviewed for current Route C, Service-owned provider runtime ceiling, Host/Agent boundary and future Agent ownership |
| `docs/implementation-control.md` | reviewed for current gate, accepted provider evidence and prohibited changes |
| `docs/current-startup-packet.md` | reviewed for short resume state and current residuals |
| `docs/reviews/mvp-provider-runtime-budget-calibration-plan-20260603.md` | reviewed for prior diagnostic hypotheses and safe evidence shape |
| `docs/reviews/mvp-provider-runtime-budget-calibration-evidence-resume-20260603.md` | reviewed for resumed default live evidence |
| `docs/reviews/mvp-provider-runtime-budget-calibration-evidence-resume-controller-judgment-20260603.md` | reviewed for accepted narrowing and next entry point |
| `reports/llm-runs/006597-2024-20260602T220325Z-host_run_c83e8c1adcc846a/summary.json` | inspected with `jq` for same-source chapter/runtime facts |

Supplemental same-source code/config checks:

- `fund_agent/config/llm.py` defines explicit `FUND_AGENT_LLM_AUDITOR_TIMEOUT_SECONDS`, falling back to `FUND_AGENT_LLM_TIMEOUT_SECONDS`, with range `(0, 300]`.
- `fund_agent/config/README.md` documents writer/auditor/repair operation-specific timeout env vars.
- `fund_agent/services/execution_contract.py` carries `ProviderRuntimeBudget.auditor_timeout_seconds` and derives Host timeout from writer + auditor + repair budgets.
- `fund_agent/services/fund_analysis_service.py` copies typed config into the Service-owned runtime plan.
- `fund_agent/services/llm_provider.py` selects `config.auditor_timeout_seconds` when `operation == "auditor"` and records `timeout_budget_kind="auditor"`.

Observed documentation drift, not part of this gate: root `README.md` only lists `FUND_AGENT_LLM_TIMEOUT_SECONDS`, while config README and code already expose operation-specific timeout vars. This plan does not edit README; controller may route a later doc-sync fast/standard gate if desired.

## First-Principles Problem Frame

The problem is not to make the report pass by any available means. The problem is to determine, using same-source runtime evidence, whether the current blocker for template Chapter 2 `R=A+B-C 收益归因` is a provider small-prompt auditor runtime budget issue or a different fail-closed content/contract issue.

Current accepted evidence from the resumed default live run:

| Chapter | Current status | Same-source disposition |
|---:|---|---|
| 1 | accepted | not a current blocker |
| 2 | failed | `llm_timeout`, `runtime_operation=auditor`, approx prompt tokens `758`, `timeout_seconds=60.0`, `timeout_max_attempts=2`, `timeout_budget_kind=auditor`, root hint `small_prompt_provider_timeout` |
| 3 | failed | separate `prompt_contract` / `code_bug_other`, `programmatic:C2`, `repair_budget_exhausted` |
| 4 | accepted | no longer a current default-run blocker |
| 5 | accepted | no longer a current default-run blocker |
| 6 | accepted | no longer a current default-run blocker |

The latest same-source facts therefore support only this scoped runtime question:

Can Ch2 auditor complete under a bounded higher auditor timeout while preserving the exact same fail-closed pipeline, auditor rules, writer behavior, repair budget, default timeout semantics and retained-artifact safety?

They do not support:

- broad Ch2/Ch4/Ch6 timeout default changes;
- writer timeout tuning for the current run;
- Ch3 fixes through provider runtime tuning;
- auditor relaxation;
- score-loop or readiness changes.

## Design Decision

Decision: a bounded higher auditor-timeout diagnostic is possible with existing explicit config. No diagnostic-only timeout override implementation is needed for the next evidence slice.

Reasoning:

- The current code already has an explicit operation-specific env var: `FUND_AGENT_LLM_AUDITOR_TIMEOUT_SECONDS`.
- The value is typed, bounded and validated by `LLMProviderConfig`.
- The Service-owned runtime plan keeps provider runtime ceilings outside `FundLLMExecutionContract`, preserving current boundary discipline.
- The provider adapter already applies the auditor timeout only to `operation="auditor"`.
- Host deadline is derived from the runtime budget, so a higher auditor timeout should be reflected in `runtime_plan.host_timeout_seconds` without Host inspecting business fields.

Default-preserving diagnostic budget:

- Set only `FUND_AGENT_LLM_AUDITOR_TIMEOUT_SECONDS=120`.
- Do not set `FUND_AGENT_LLM_TIMEOUT_SECONDS`, `FUND_AGENT_LLM_WRITER_TIMEOUT_SECONDS`, or `FUND_AGENT_LLM_REPAIR_TIMEOUT_SECONDS` for the primary diagnostic.
- Keep `FUND_AGENT_LLM_TIMEOUT_MAX_ATTEMPTS` at the existing default unless the controller explicitly wants a presence-only assertion; current accepted evidence is `60s x2`, so the direct comparison is `120s x2`.
- Keep backoff/default output limits unchanged.
- Do not change code defaults.

Why `120` seconds:

- It is bounded and below the existing config maximum of `300`.
- It doubles the current single-attempt auditor budget while preserving the same attempt count.
- It is large enough to test "budget too low" without turning the diagnostic into an unbounded provider wait.

## Next Evidence Slice Plan

### Slice A: read-only preflight

Purpose: prove the current workspace still supports explicit auditor-only timeout override before live provider evidence.

Allowed commands:

```bash
git status --short
git branch --show-current
python -m json.tool reports/llm-runs/006597-2024-20260602T220325Z-host_run_c83e8c1adcc846a/summary.json >/tmp/ch2-timeout-summary-json-check.txt
rg -n "FUND_AGENT_LLM_AUDITOR_TIMEOUT_SECONDS|auditor_timeout_seconds|timeout_budget_kind" fund_agent/config fund_agent/services tests README.md fund_agent/README.md fund_agent/config/README.md
```

Expected safe outputs:

- Worktree status may contain unrelated existing changes; do not clean them.
- Branch should remain the current MVP branch.
- JSON validation succeeds.
- `rg` shows explicit config, runtime plan and provider adapter support for auditor timeout.

Stop conditions:

- If `FUND_AGENT_LLM_AUDITOR_TIMEOUT_SECONDS` is not present in code, stop and use conditional Slice I below instead.
- If JSON validation fails, stop; retained artifact is not valid evidence.
- If worktree has conflicting changes in the specific modules needed by a later implementation slice, stop for controller disposition.

### Slice B: default retained baseline extraction

Purpose: record the exact same-source baseline to compare against the bounded diagnostic.

Allowed command:

```bash
jq -r '
  .chapter_matrix[] as $c
  | [
      $c.chapter_id,
      $c.status,
      $c.stop_reason,
      ($c.failure_category // ""),
      ($c.failure_subcategory // "")
    ] | @tsv
' reports/llm-runs/006597-2024-20260602T220325Z-host_run_c83e8c1adcc846a/summary.json
```

Additional runtime command:

```bash
jq '.runtime_diagnostics.first_failed' reports/llm-runs/006597-2024-20260602T220325Z-host_run_c83e8c1adcc846a/summary.json
```

Expected baseline:

- Ch2 is first failed.
- Ch2 has `category=llm_timeout`, `runtime_operation=auditor`, `approx_prompt_tokens=758`, `timeout_seconds=60.0`, `timeout_max_attempts=2`, `timeout_budget_kind=auditor`.
- Ch3 remains `prompt_contract` / `code_bug_other`.
- Ch4/Ch5/Ch6 accepted.

### Slice C: bounded higher auditor-timeout diagnostic

Purpose: test whether Ch2 auditor timeout is resolved by a higher operation-specific auditor budget.

Live provider command for the next controller-authorized evidence slice:

```bash
FUND_AGENT_LLM_AUDITOR_TIMEOUT_SECONDS=120 \
uv run fund-analysis analyze 006597 --report-year 2024 --use-llm --llm-progress
```

Command constraints:

- Do not set `FUND_AGENT_LLM_TIMEOUT_SECONDS`.
- Do not set `FUND_AGENT_LLM_WRITER_TIMEOUT_SECONDS`.
- Do not set `FUND_AGENT_LLM_REPAIR_TIMEOUT_SECONDS`.
- Do not run PASS-only probe.
- Do not run split-audit probe.
- Do not alter provider model/base URL/API key values or print them.
- Do not mutate the prior retained artifact path.

Expected safe terminal behavior:

- If Ch2 still times out, CLI exit remains `1`, stdout remains empty, and a new retained artifact is written.
- If Ch2 passes but Ch3 remains failed, CLI exit remains `1`, stdout remains empty, and the new artifact should show Ch2 accepted plus Ch3 `prompt_contract` / `programmatic:C2`.
- If all body chapters pass and final assembly accepts, stdout may contain the normal accepted report; this would be a normal production-path complete result, not a partial stdout report. Evidence artifact may not be retained for a complete accepted run under current artifact-retention semantics, so terminal/stderr and any normal output handling must be recorded without leaking report body into the review artifact.

Artifact path handling:

- Capture the new `reports/llm-runs/...` path from CLI safe summary if the run remains incomplete.
- Never overwrite, edit or delete `reports/llm-runs/006597-2024-20260602T220325Z-host_run_c83e8c1adcc846a`.
- If no new retained artifact is written because the run fully accepts, record that explicitly and keep the evidence to command, exit code, stdout/stderr safety summary and controller judgment.
- If artifact writing emits only a safe warning, preserve fail-closed command result and route artifact-write issue separately.

### Slice D: post-run safe extraction

Run only against a newly retained incomplete artifact path.

```bash
python -m json.tool NEW_ARTIFACT/summary.json >/tmp/ch2-auditor-120-summary-json-check.txt
python -m json.tool NEW_ARTIFACT/manifest.json >/tmp/ch2-auditor-120-manifest-json-check.txt
jq '.runtime_diagnostics.first_failed, .chapter_matrix' NEW_ARTIFACT/summary.json
```

Expected safe evidence fields:

- `orchestration_status`
- `final_assembly_status`
- `first_failed`
- per-chapter `status`, `stop_reason`, `failure_category`, `failure_subcategory`, `attempt_count`
- Ch2 runtime diagnostics if still failed:
  - `operation`
  - `provider_runtime_category`
  - `provider_attempt_index`
  - `provider_max_attempts`
  - `elapsed_ms`
  - `timeout_seconds`
  - `timeout_max_attempts`
  - `timeout_budget_kind`
  - `approx_prompt_tokens`
  - `system_prompt_chars`
  - `user_prompt_chars`
  - `allowed_fact_count`
  - `allowed_anchor_count`
  - `response_chars`
  - `finish_reason`
  - `timeout_root_cause_hint`

Forbidden evidence:

- API key
- Authorization header
- Bearer token
- cookie
- password
- provider base URL value
- raw prompt body
- writer draft body
- repair draft body
- raw provider response
- raw audit response
- full report body
- raw PDF text
- raw parsed annual-report text

### Slice E: secret scan

Run only against the new retained artifact if one exists:

```bash
rg -n "Authorization|Bearer |FUND_AGENT_LLM_API_KEY|api_key|sk-|raw_response|provider response|draft_markdown|system_prompt[^_]|user_prompt[^_]" NEW_ARTIFACT
```

Expected result:

- No matches.

If matches appear:

- Stop.
- Do not paste matched secret-bearing content into the review artifact.
- Record only the file path, redacted pattern class and controller escalation need.

## Interpretation Matrix

| Diagnostic outcome | Interpretation | Next route |
|---|---|---|
| Ch2 accepted; Ch3 remains `prompt_contract` / `programmatic:C2`; final assembly incomplete | Supports H2: current Ch2 auditor budget is too low for this provider/run; no evidence for auditor relaxation | Route Ch3 to separate contract/audit calibration before any score-loop |
| Ch2 still times out at `auditor`, `timeout_seconds=120`, `timeout_max_attempts=2`, small prompt | Disproves simple `120s x2` budget sufficiency; supports provider endpoint/runtime instability or auditor prompt/task latency beyond bounded budget | Controller decides between provider endpoint disposition, PASS-only timing probe design, or split-audit design gate |
| Ch2 fails with audit issue instead of timeout | Disproves "timeout is the only Ch2 blocker"; reveals content/audit issue now observable after budget increase | Route Ch2 content/audit issue to separate audit calibration; do not change timeout default yet |
| Ch2 accepted and full report accepted | Shows current normal path can complete under auditor-only diagnostic budget | Still does not authorize default change; controller must judge repeatability, cost/latency and release readiness separately |
| Writer or repair timeout appears | Disproves current Ch2-only auditor hypothesis for that run | Route back to provider runtime budget evidence with operation split |
| Config/construction/auth failure appears | Not evidence about Ch2 auditor timeout | Stop and route provider config/auth separately |
| Artifact missing for incomplete run | Evidence retention issue, not Ch2 runtime evidence | Stop and route artifact retention separately |

## Conditional Implementation Slice If Current Config Is Not Available

Current decision: not needed, because same-source code shows explicit auditor timeout config already exists.

Use this slice only if a future branch/controller check finds that operation-specific auditor timeout support is absent or unusable.

Allowed files/modules:

- `fund_agent/config/llm.py`
- `fund_agent/services/execution_contract.py`
- `fund_agent/services/fund_analysis_service.py`
- `fund_agent/services/llm_provider.py`
- focused tests under `tests/services/` and `tests/ui/`
- `fund_agent/config/README.md` only if config docs change
- root `README.md` only if the user-facing env table must be synchronized

Implementation constraints:

- Add an explicit typed env/config field for auditor timeout only.
- Keep `FUND_AGENT_LLM_TIMEOUT_SECONDS` default unchanged at `60`.
- Keep timeout attempts/backoff defaults unchanged.
- Do not change writer/repair defaults.
- Do not change auditor rules, parser, prompt contract, template truth or repair budget.
- Do not place explicit parameters in `extra_payload`.
- Keep provider runtime ceilings Service-owned until the future Agent implementation gate.
- Host may receive only the derived generic `host_timeout_seconds` scalar.

Validation commands:

```bash
uv run pytest tests/services/test_llm_provider.py tests/services/test_fund_analysis_service_llm.py tests/services/test_execution_contract.py tests/ui/test_cli.py -q
git diff --check
```

Acceptance criteria:

- Tests prove auditor timeout override affects only `operation=auditor`.
- Writer initial and writer repair timeouts remain unchanged unless their own explicit env vars are set.
- Diagnostics record `timeout_budget_kind=auditor` and the overridden timeout scalar.
- Host timeout is derived from Service runtime plan and Host does not inspect fund business fields.
- No live provider call is required for implementation validation.

## Boundary And Non-Goal Checks

- Service keeps first-MVP provider config parsing, provider construction and runtime ceilings for this diagnostic.
- Host remains lifecycle-only and sees only generic operation/deadline/session fields.
- Future Agent ToolTrace/budget ownership remains accepted future design; do not implement Agent runner/tool-loop/budget migration in this gate.
- Fund remains owner of CHAPTER_CONTRACT, preferred_lens, ITEM_RULE and audit semantics; do not change them here.
- No deterministic fallback is allowed.
- No partial stdout report is allowed.
- No auditor relaxation is allowed.
- No provider default timeout change is allowed.
- No score/golden/quality/readiness changes are allowed.
- No template truth changes are allowed.
- No retained artifact mutation is allowed.

## Explicit Routing

- Ch2 auditor timeout: next evidence slice is bounded higher auditor timeout using existing explicit config.
- Ch3 `prompt_contract` / `code_bug_other` / `programmatic:C2`: route to a separate Ch3 contract/audit calibration gate. That gate must first determine whether the root cause is the C2 rule, writer boundary, typed contract clause mapping, or a true code bug.
- Score-loop / `chapter_generation_score`: route to a later gate after provider runtime and Ch3 contract blockers have accepted dispositions.
- PASS-only auditor probe and split-audit: not authorized as the immediate next step. They become candidates only if the `120s x2` auditor-only diagnostic times out or otherwise indicates full auditor prompt/task latency as the blocker.

## Residual Risks

| Risk | Status | Owner / destination |
|---|---|---|
| Provider latency variance may make one `120s x2` result non-repeatable | accepted residual for evidence slice | controller judgment decides whether repeat evidence is required |
| Higher auditor timeout can increase wall-clock time and provider cost | known tradeoff, not a default change | provider runtime budget controller gate |
| Ch2 may reveal content/audit blockers only after timeout is removed | unresolved | Ch2 content/audit calibration gate if observed |
| Ch3 remains independently blocking final assembly | active residual | Ch3 contract/audit calibration gate |
| Root README env table omits operation-specific timeout vars | doc drift, not runtime blocker | later doc-sync gate if controller chooses |
| Future Agent should own budget/ToolTrace, but current MVP keeps Service runtime ceilings | intentional current boundary | future Agent implementation gate |
| Score-loop still lacks accepted runtime/content blocker disposition | deferred | later score-loop gate |

## Validation For This Design Artifact

Planned local validation after writing this artifact:

```bash
git diff --check -- docs/reviews/mvp-ch2-auditor-timeout-diagnostic-design-plan-20260603.md
rg -n "Bearer [A-Za-z0-9._-]{20,}|sk-[A-Za-z0-9._-]{20,}|Authorization:|FUND_AGENT_LLM_API_KEY=|api_key[=:][A-Za-z0-9._-]+" docs/reviews/mvp-ch2-auditor-timeout-diagnostic-design-plan-20260603.md | rg -v "rg -n"
```

Expected result:

- `git diff --check` passes.
- Secret-value scan has no matches after excluding the documented scan command itself. Policy terms such as `Authorization header` and `raw provider response` may appear in this design artifact as forbidden-output labels; those are not secret values.

## Handoff Summary

The next action should be an evidence-only, controller-authorized live diagnostic using existing explicit config:

```bash
FUND_AGENT_LLM_AUDITOR_TIMEOUT_SECONDS=120 \
uv run fund-analysis analyze 006597 --report-year 2024 --use-llm --llm-progress
```

This tests only whether Ch2's current small-prompt auditor timeout under `60s x2` resolves under `120s x2`. It does not authorize any default change, auditor relaxation, Ch3 fix, score-loop work, retained artifact mutation, PR action, or production readiness decision.
