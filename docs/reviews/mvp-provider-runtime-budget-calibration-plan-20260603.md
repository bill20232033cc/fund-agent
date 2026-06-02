# MVP provider runtime budget calibration design/plan

## Scope And Role

- Role: planning/design specialist only, not phaseflow/gateflow controller.
- Gate: `MVP provider runtime budget calibration gate`.
- Classification: `heavy`.
- Output: handoff-ready design/plan only.
- Current action: no implementation, no source/test/config/runtime edit, no provider budget default change, no auditor/template/quality/golden/readiness/score-loop change, no retained report mutation, no PR/push/commit, no live provider call.

## Source Truth And Evidence

Required input status:

| Input | Status |
|---|---|
| `AGENTS.md` | read |
| `docs/design.md` | read |
| `docs/implementation-control.md` | read |
| `docs/current-startup-packet.md` | read |
| `docs/reviews/mvp-provider-runtime-timeout-follow-up-implementation-evidence-20260602.md` | missing |
| closest substitute | `docs/reviews/mvp-provider-runtime-timeout-follow-up-implementation-evidence-20260531.md` |
| `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-slice1-controller-judgment-after-provider-restore-20260602.md` | read |
| `docs/reviews/mvp-internalized-agent-engine-tool-loop-contract-execution-controller-judgment-20260603.md` | read |
| `docs/reviews/mvp-multi-year-annual-evidence-scope-controller-judgment-20260603.md` | read |
| retained run | `reports/llm-runs/006597-2024-20260602T121553Z-host_run_1f8d428509c5431` read |

Substitute evidence caveat: the requested 2026-06-02 timeout follow-up implementation evidence is absent, so this plan treats the 2026-05-31 follow-up as historical implementation evidence only. It does not infer a 2026-06-02 artifact.

## First-Principles Problem Frame

The problem is not "make the LLM pass." The problem is to determine whether Ch2/Ch4/Ch6 fail because the provider endpoint/runtime budget is too small for safe chapter generation, or because another layer is correctly blocking incomplete or unsafe output.

Same-source retained evidence must separate these causes:

| Cause class | Direct evidence required | Current retained evidence |
|---|---|---|
| Provider endpoint/runtime timeout | `operation`, `provider_runtime_category=timeout`, `elapsed_ms`, `timeout_seconds`, `provider_attempt_index/max`, `timeout_budget_kind`, prompt scalar fields | present for Ch2/Ch4/Ch6 auditor calls |
| Prompt contract failure | writer parser issue, marker issue, response incomplete/too long, required-output marker issue, `failure_category=prompt_contract` | present for Ch3 only |
| Audit parse or audit rule block | auditor status/issue ids without provider timeout; programmatic/LLM issue identity | present for Ch3, Ch6 attempt 0, not terminal for Ch2/Ch4 |
| Fact gap | same-source `writer_declared_missing_reasons`, missing fact ids, data gap identities causing safe downgrade or block | present as metadata, not terminal for Ch2/Ch4/Ch6 timeout rows |
| Code bug | exception/traceback, deterministic regression, test failure, malformed retained artifact, impossible state | no current direct evidence |
| Large prompt cost | prompt scalar fields above accepted large threshold or historical before/after prompt-cost evidence | rejected for current retained Ch2/Ch4/Ch6; all timeout prompts are under 800 tokens |

Important correction: the 2026-05-31 validation evidence recorded all body chapters timing out at the writer operation after compact mode, with Ch2/Ch4/Ch6 writer prompt tokens `1590` / `1274` / `2110`. The 2026-06-02 retained run records Ch2/Ch4/Ch6 writer drafts as produced and terminal failures at the auditor operation with prompt tokens `743` / `584` / `731`. Therefore the next gate must evaluate writer-timeout and auditor-timeout hypotheses separately. The latest retained run disproves "Ch2/Ch4/Ch6 writer timeout" for that run, but not for all future provider reruns.

## Hard Constraints

- No deterministic fallback for incomplete LLM result.
- No partial accepted report from a partial chapter matrix.
- No auditor relaxation, no programmatic blocker weakening, no fail-open parsing.
- No provider budget change without a later implementation gate, plan review, controller judgment, and validation.
- No mutation of `chapter_generation_score`, golden fixtures, quality gate, release readiness, retained reports, score-loop, or PR state.
- No raw prompt, draft body, provider response, raw audit response, API key, Authorization header, cookie, password, base URL value, model secret, or provider request body in artifacts.
- Provider experiments must write only allowlisted scalar/id diagnostics and safe summaries.

## Same-Source Retained Run Facts

Retained run:

`reports/llm-runs/006597-2024-20260602T121553Z-host_run_1f8d428509c5431`

Top-level facts:

- `cli_command=analyze --use-llm`
- `orchestration_status=partial`
- `final_assembly_status=incomplete`
- `stdout` remained empty per controller judgment.
- `chapter_count=6`
- `redaction_applied=false`, `redaction_count=0`

Chapter matrix from `summary.json`:

| Chapter | Status | Stop reason | Failure category | Terminal timeout operation | Approx tokens | Budget |
|---:|---|---|---|---|---:|---|
| 1 | accepted | `none` | n/a | n/a | n/a | n/a |
| 2 | failed | `llm_timeout` | `llm_timeout` | auditor | `743` | `60s x2` |
| 3 | failed | `repair_budget_exhausted` | `prompt_contract` / `code_bug_other` | n/a | n/a | n/a |
| 4 | failed | `llm_timeout` | `llm_timeout` | auditor | `584` | `60s x2` |
| 5 | accepted | `none` | n/a | n/a | n/a | n/a |
| 6 | failed | `llm_timeout` | `llm_timeout` | auditor after repair | `731` | `60s x2` |

Exact retained fields needed for future diagnosis:

- `summary.json`: `schema_version`, `orchestration_status`, `final_assembly_status`, `chapter_matrix`, `first_failed`, `runtime_diagnostics.chapter_runtime_matrix`, `prompt_contract_diagnostics.chapter_phase_matrix`.
- `manifest.json`: `artifact_kind`, `cli_command`, `created_at`, `run_id`, `redaction_policy`, `redaction_applied`, `redaction_count`.
- `chapters/chapter-0N.json`: `status`, `stop_reason`, `failure_category`, `failure_subcategory`, `attempts[].writer_status`, `attempts[].writer_stop_reason`, `attempts[].writer_response_chars`, `attempts[].writer_finish_reason`, `attempts[].audit_status`, `attempts[].audit_accepted`, `attempts[].programmatic_issues[].issue_id`, `attempts[].llm_issues[].issue_id`, `attempts[].runtime_diagnostics[]`.
- Runtime diagnostic fields: `operation`, `repair_attempt_index`, `provider_attempt_index`, `provider_max_attempts`, `provider_runtime_category`, `elapsed_ms`, `error_type`, `status_code`, `request_id`, `finish_reason`, `response_chars`, `system_prompt_chars`, `user_prompt_chars`, `approx_prompt_tokens`, `allowed_fact_count`, `allowed_anchor_count`, `max_output_chars`, `timeout_seconds`, `timeout_max_attempts`, `timeout_backoff_seconds`, `timeout_budget_kind`, `repair_timeout_fallback_used`, `timeout_root_cause_hint`.

## Root-Cause Hypotheses And Disproof Criteria

| Hypothesis | Current status | Evidence that would support it | Evidence that would disprove it |
|---|---|---|---|
| H1: provider endpoint small-prompt timeout | supported for Ch2/Ch4/Ch6 auditor rows | repeated `provider_runtime_category=timeout` at small prompt sizes under bounded budgets, no parser/audit/fact/code issue before timeout | same command succeeds under default budget or fails with content/audit/parser issue instead |
| H2: current timeout budget too low | unresolved | same prompts succeed with a bounded higher budget and identical fail-closed semantics | timeouts persist at bounded higher budget, or latency grows without response |
| H3: writer timeout remains primary for Ch2/Ch4/Ch6 | not supported by 2026-06-02 retained run; historically seen 2026-05-31 | future same-source rerun shows terminal `operation=writer` for these chapters | retained/future row has writer draft and terminal `operation=auditor`, as on 2026-06-02 |
| H4: auditor prompt format induces endpoint hang | unresolved | PASS-only or minimal auditor probe returns quickly while full audit prompt times out, with same draft/facts scalar profile | both PASS-only/minimal and full auditor prompt time out similarly |
| H5: audit rules are too strict | not supported for Ch2/Ch4; mixed historical for Ch6 attempt 0 | timeout-free audit returns programmatic/LLM blockers that repeat under same-source data | provider timeout occurs before audit result, or PASS-only probe also times out |
| H6: prompt contract/fact gap/code bug | not supported for Ch2/Ch4/Ch6 terminal rows | same-source parser, fact-gap, exception or deterministic regression evidence | timeout rows contain no such issue and validation remains green |

## Design Options

### Option A: Writer/Auditor Timeout Budget Calibration

Design-only decision: evaluate as a later controlled evidence gate before any default change.

Plan:

- Use operation-specific env overrides only in future live diagnostics: writer, auditor, repair timeout seconds.
- Keep attempts bounded; do not add unbounded retry.
- Compare default `60s x2` against one bounded higher budget such as `120s x2`.
- Record only scalar elapsed/attempt/category fields.

Pros: directly tests H2 without touching audit semantics.

Cons: live provider behavior may vary; a pass under higher timeout does not prove the budget should become default without latency/cost review.

Recommendation: accept as the primary next evidence path, not as immediate implementation.

### Option B: Split Writer/Auditor Timing

Design-only decision: required for diagnosis.

Plan:

- Treat writer and auditor as separate budget classes in evidence.
- For Ch2/Ch4/Ch6, the next gate must report whether timeout happened before writer draft, during auditor of initial draft, or during auditor after repair.
- Do not summarize all rows as "chapter timeout" without operation and repair attempt.

Pros: prevents wrong fixes such as slimming writer prompts when the terminal blocker is auditor runtime.

Cons: may require a small later diagnostic serializer improvement if current artifacts cannot expose enough fields in a future branch.

Recommendation: required handoff criterion.

### Option C: PASS-Only Audit Experiment

Design-only decision: allowed only as a future diagnostic experiment, not as production behavior.

Purpose: distinguish endpoint latency on the auditor endpoint from latency induced by full audit prompt/task complexity.

Safe shape:

- Use retained accepted writer draft metadata or a future same-run draft, but do not store or print the draft text in new evidence.
- Run an auditor client with a minimal request that asks only for the valid line protocol success shape.
- The output must never be accepted as chapter audit; it is a timing probe only.
- If it returns `PASS`, production still must run the full auditor.

Expected outputs:

- `pass_only_audit_elapsed_ms`
- `pass_only_audit_provider_runtime_category`
- `pass_only_audit_finish_reason`
- no prompt/draft/provider body

Stop condition:

- If PASS-only times out, classify as provider endpoint/runtime and do not tune audit rules.
- If PASS-only succeeds but full audit times out, consider split-audit or audit prompt budget design.

### Option D: Split-Audit

Design-only decision: candidate future design only; no implementation until evidence supports H4.

Possible split:

- Programmatic audit remains first and authoritative.
- Bounded semantic LLM audit may be split into smaller checks by issue family or required output item.
- Final audit result is fail-closed aggregation: any blocked, malformed, timeout or missing split blocks the chapter.

Pros: may reduce auditor prompt latency while preserving fail-closed.

Cons: increases provider calls and state accounting; belongs naturally in future Agent ToolTrace/attempt ledger.

Recommendation: do not implement unless PASS-only/minimal/full audit timing proves full auditor prompt complexity is the timeout trigger.

### Option E: Per-Chapter Budget Policy

Design-only decision: possible but not recommended as first change.

Rationale:

- Same-source Ch2/Ch4/Ch6 auditor prompts are all small.
- Per-chapter differences are currently weaker than operation differences.
- A chapter-specific budget risks encoding provider quirks into domain semantics.

Recommendation: defer. Prefer operation-specific budget first. Revisit only if repeated same-provider evidence shows stable chapter-specific latency after operation split.

### Option F: Endpoint/Model/Provider Diagnostics

Design-only decision: allowed as safe diagnostics only.

Allowed evidence:

- provider category label already in config, not secret value
- HTTP status code if present
- request id if provider returns one and it is not secret-bearing
- elapsed ms and timeout category
- tiny health-check result as separate diagnostic, clearly not proof that full chapter calls will pass

Forbidden:

- base URL value, model name if project policy treats it as unsafe, API key, Authorization header, request/response body, raw prompt.

Recommendation: use only to separate config/auth from runtime. Current evidence already rejects config/auth as primary.

### Option G: Timeout PoC

Design-only decision: future PoC may run only after controller authorization.

PoC matrix:

| Run | Budget | Purpose | Expected safe output |
|---|---|---|---|
| default rerun | current env/defaults | confirm whether 2026-06-02 auditor timeout reproduces | same scalar matrix |
| bounded higher auditor timeout | auditor timeout override only, attempts unchanged | test H2 for Ch2/Ch4/Ch6 | Ch2/Ch4/Ch6 accepted, content-blocked, or still timeout |
| bounded higher writer timeout | writer timeout override only | test historical 2026-05-31 writer timeout recurrence | writer timeout disappears or persists |
| PASS-only auditor probe | diagnostic-only | test H4 | timing/category only |

No PoC result may produce an accepted report unless the normal production path accepts every required chapter and final assembly.

## Future Evidence Commands

Do not run these in this planning gate. They are handoff commands for a later authorized evidence gate.

Read-only retained artifact checks:

```bash
python -m json.tool reports/llm-runs/006597-2024-20260602T121553Z-host_run_1f8d428509c5431/summary.json >/dev/null
jq -r '.runtime_diagnostics.chapter_runtime_matrix[] | [.chapter_id,.status,.stop_reason,.failure_category,([.runtime_diagnostics[]? | select(.provider_runtime_category=="timeout") | .operation] | unique | join("+")),([.runtime_diagnostics[]? | select(.provider_runtime_category=="timeout") | .approx_prompt_tokens] | max // ""),([.runtime_diagnostics[]? | select(.provider_runtime_category=="timeout") | .timeout_seconds] | max // ""),([.runtime_diagnostics[]? | select(.provider_runtime_category=="timeout") | .provider_max_attempts] | max // ""),([.runtime_diagnostics[]? | select(.provider_runtime_category=="timeout") | .elapsed_ms] | max // "")] | @tsv' reports/llm-runs/006597-2024-20260602T121553Z-host_run_1f8d428509c5431/summary.json
```

Expected retained output shape:

- Ch2/Ch4/Ch6 show `failed`, `llm_timeout`, terminal timeout `operation=auditor`, prompt tokens below `1000`, timeout `60.0`, max attempts `2`.
- Ch3 remains `prompt_contract`, not provider runtime.

Future live provider evidence commands, controller-authorized only:

```bash
uv run fund-analysis analyze 006597 --report-year 2024 --use-llm --llm-progress
```

Optional env-override matrix for later gate only:

```bash
FUND_AGENT_LLM_AUDITOR_TIMEOUT_SECONDS=120 uv run fund-analysis analyze 006597 --report-year 2024 --use-llm --llm-progress
FUND_AGENT_LLM_WRITER_TIMEOUT_SECONDS=120 uv run fund-analysis analyze 006597 --report-year 2024 --use-llm --llm-progress
```

Expected safe outcomes:

- Exit `0` only if all required body chapters are accepted and final assembly completes through the normal fail-closed path.
- Exit `1` with empty stdout remains acceptable evidence if the retained artifact shows precise blocker classification.
- Any timeout-free Ch3/Ch6 programmatic C2 or audit block must stop runtime-budget tuning and route to the appropriate audit/contract calibration gate.

Secret-safety scan for future report directory:

```bash
rg -n "Authorization|Bearer |FUND_AGENT_LLM_API_KEY|api_key|sk-|raw_response|provider response|draft_markdown|system_prompt[^_]|user_prompt[^_]" reports/<future-runtime-budget-dir>
```

Expected result:

- No actual secret, raw prompt, draft markdown, raw provider response or raw audit response.
- Field names like `system_prompt_chars` and `user_prompt_chars` are acceptable.

## Stop Conditions

Stop the later gate and ask controller for disposition if any of these occur:

- Missing provider env prevents the live evidence run.
- Any artifact contains secret-bearing text or raw prompt/draft/provider/audit body.
- Runtime rows cannot identify `operation`, attempt budget, elapsed ms and timeout category.
- Ch2/Ch4/Ch6 no longer fail by timeout and instead show programmatic, LLM audit, prompt contract, fact gap or code issue.
- A bounded higher timeout still times out for small prompts; classify as provider endpoint/runtime residual instead of increasing budgets again.
- A proposed fix requires auditor relaxation, deterministic fallback, score/golden/quality/readiness mutation, or template truth replacement.

## Future Implementation Slices

These slices are conditional. Do not implement unless the evidence gate supports the named condition and controller accepts the plan/review.

### Slice 1: Evidence-Only Runtime Matrix Artifact

Condition: current serializers are insufficient for operation split or PASS-only timing evidence.

Allowed files, to be confirmed by controller:

- `fund_agent/services/chapter_orchestrator.py`
- `fund_agent/services/llm_provider.py`
- `fund_agent/services/llm_run_artifacts.py`
- targeted tests under `tests/services/`
- evidence artifact under `docs/reviews/`

Implementation decision:

- Add only allowlisted scalar fields if missing.
- Do not serialize prompts, drafts, raw provider/audit payloads, model request bodies or secrets.

Validation:

- targeted service/provider/artifact tests
- leak canary tests
- `git diff --check`
- no live provider call by implementation worker unless separately authorized

### Slice 2: Operation-Specific Budget Policy

Condition: same-source live evidence shows Ch2/Ch4/Ch6 small auditor prompts pass under one bounded higher auditor timeout and no content/audit regression appears.

Allowed files, to be confirmed by controller:

- `fund_agent/config/llm.py`
- `fund_agent/services/llm_provider.py`
- `fund_agent/services/fund_analysis_service.py` only if runtime plan plumbing is missing
- `fund_agent/config/README.md`
- targeted tests under `tests/config/` and `tests/services/`

Implementation decision:

- Prefer explicit operation-specific env override or typed runtime plan value.
- Keep max attempts bounded.
- Do not change defaults in the same slice unless controller accepts latency/cost evidence. If a default change is proposed, make it a separate heavy implementation gate.

Validation:

- config bounds/default tests
- provider timeout selection tests
- CLI fail-closed tests
- no deterministic fallback

### Slice 3: Diagnostic PASS-Only Audit Probe

Condition: controller accepts a diagnostic-only PoC after default/higher-budget evidence remains ambiguous.

Allowed files, to be confirmed by controller:

- a diagnostic script or test-only helper under an approved diagnostics path
- `docs/reviews/` evidence artifact

Implementation decision:

- Must be impossible to feed PASS-only result into production acceptance.
- Output only timing/category scalars.

Validation:

- proof the probe is not imported by production path
- secret scan
- retained artifact comparison

### Slice 4: Split-Audit Design Gate

Condition: PASS-only succeeds but full auditor repeatedly times out under bounded budget.

Allowed output:

- design artifact only at first.

Implementation must wait for a separate Agent-aware plan because split-audit belongs to attempt ledger, ToolTrace and fail-closed aggregation.

## Ownership Boundary

Current first-MVP provider construction and runtime ceilings remain Service-owned:

- Service builds `FundLLMExecutionRequest`, runtime plan and openai-compatible writer/auditor clients.
- CLI passes only generic Host operation/deadline/session fields.
- Host is lifecycle-only and does not inspect fund code, chapter policy, provider clients or ExecutionContract business fields.
- Fund owns domain writer/auditor semantics and programmatic-first audit.

Accepted future Agent/tool-loop boundary changes eventual ownership:

- Future Agent owns runner, tool loop, retry/repair attempt ledger, budget spending, stop/retry decision and `ToolTrace`.
- Provider clients remain Service-constructed explicit per-run typed fields for the first Agent MVP; they are not ToolRegistry tools and must not be passed through `extra_payload`.
- Future runtime budget evidence should map naturally into `ToolTrace` attempt rows, while Service keeps use-case policy, provider construction and final product fail-closed mapping until an Agent implementation gate migrates them.
- Split-audit, per-attempt budget spending and final assembly readiness should be designed for Agent ownership, not expanded ad hoc inside Service beyond the first-MVP diagnostic need.

## Non-Goals

- No Ch3 calibration implementation.
- No Ch2 public split, `0+9`, `0+10`, or chapter count change.
- No multi-year annual evidence implementation.
- No raw five-year PDF/text prompt injection.
- No score-loop, `chapter_generation_score`, golden fixture, quality gate, readiness, release or PR mutation.
- No provider SDK replacement, provider fallback, model selection policy, or endpoint migration.
- No default provider budget change in this design/plan artifact.
- No deterministic fallback or partial stdout report.

## Residual Risks And Owners

| Risk | Owner / destination |
|---|---|
| Provider endpoint may remain unreliable even under bounded higher budgets | controller decision after evidence gate; possible provider endpoint/model diagnostics gate |
| Ch6 has non-terminal C2/C1 evidence before terminal timeout | separate Ch6 audit/contract calibration only after timeout no longer blocks |
| Ch3 remains `programmatic:C2` / `code_bug_other` | Ch3-only calibration gate, not runtime budget gate |
| Split-audit increases calls and state complexity | future Agent/tool-loop design or implementation gate |
| Budget default change affects cost/latency/user expectations | separate heavy implementation gate with explicit controller judgment |
| Current Service ownership is transitional | future Agent implementation gate owns ToolTrace/budget/retry migration |

## Review Handoff Criteria

Reviewers should verify:

- The plan distinguishes 2026-05-31 writer timeout evidence from 2026-06-02 auditor timeout retained evidence.
- Every root-cause claim uses same-source retained fields or explicitly labels historical evidence.
- Fail-closed, no-fallback, no-auditor-relaxation and no-secret constraints are preserved.
- Future live commands are diagnostics only and cannot change provider defaults by themselves.
- Implementation slices are conditional, small and do not require the implementation worker to redesign ownership.

## Validation Performed For This Artifact

- `python -m json.tool reports/llm-runs/006597-2024-20260602T121553Z-host_run_1f8d428509c5431/summary.json >/dev/null` — pass.
- `jq` retained runtime matrix consistency check — pass; Ch2/Ch4/Ch6 are auditor timeout rows in the 2026-06-02 retained run.
- `rg` consistency checks over control/design/review artifacts for timeout/fail-closed/provider-runtime wording — pass.
- `git diff --check -- docs/reviews/mvp-provider-runtime-budget-calibration-plan-20260603.md` — to be run after write.
