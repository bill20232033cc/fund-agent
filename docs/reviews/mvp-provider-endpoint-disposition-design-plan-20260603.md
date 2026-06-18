# MVP provider endpoint disposition design/evidence plan

## 1. Scope

- Role: AgentCodex planning/design specialist, not controller.
- Gate: `MVP provider endpoint disposition design/evidence gate`.
- Classification: heavy.
- Date: 2026-06-03.
- This artifact is design/evidence planning only.

No live provider was called for this artifact. No source code, tests, provider timeout defaults, provider config, endpoint value, prompt, auditor rule, template truth, quality gate, score-loop, golden/readiness, PR/release state or runtime behavior was changed.

## 2. Current Evidence Baseline

The active problem is not "make the report pass"; it is to decide what evidence is needed before any provider endpoint/config/default/runtime disposition.

Accepted facts from current control documents and evidence:

- Current production default remains deterministic `fund-analysis analyze/checklist`.
- Route C `fund-analysis analyze --use-llm` is explicit opt-in and fail-closed.
- `--use-llm` now runs through the local Host runtime governance wrapper, but Agent tool-loop migration remains future design.
- Provider runtime budget calibration is accepted as evidence only. No default timeout/budget/runtime behavior change is authorized.
- Typed diagnostic serialization repair is accepted locally: future retained artifacts should expose terminal runtime lineage and consistency fields.

Retained pre-repair evidence:

| Artifact | Evidence status | Main safe observation |
|---|---|---|
| `reports/llm-runs/006597-2024-20260602T220325Z-host_run_c83e8c1adcc846a/summary.json` | pre-repair schema | default run: Ch2 failed with `llm_timeout` in `auditor`; Ch3 failed with `prompt_contract` / `code_bug_other`; Ch1/Ch4/Ch5/Ch6 accepted |
| `reports/llm-runs/006597-2024-20260602T224137Z-host_run_4b7dddc60d084e7/summary.json` | pre-repair schema | auditor-only `120s` diagnostic: Ch1/Ch4 `audit_rule_too_strict`, Ch2 `llm_timeout`, Ch3 `prompt_contract` / `code_bug_other`, Ch5 writer timeout, Ch6 `unknown_anchor` |

Important limitation: both retained run summaries above were produced before the typed diagnostic serialization repair. They must not be expected to contain:

- `diagnostic_consistency_status`
- `terminal_runtime_diagnostic_present`
- `terminal_stop_reason`
- `terminal_failure_category`
- `terminal_runtime_operation`
- `terminal_repair_attempt_index`
- `terminal_issue_class`

Therefore, old retained artifacts can support historical volatility and operation/prompt-size hypotheses, but they cannot settle terminal lineage consistency. Any endpoint/config disposition must be based on at least one post-repair retained live artifact if the controller authorizes a live evidence slice.

## 3. Provider Config Readiness Without Secret Disclosure

Presence-only readiness must answer only whether the configured provider path is runnable enough to collect evidence. It must not print provider base URL, model value, API key value, custom API key env var value if that value itself is secret-like, Authorization header, or any endpoint-derived URL.

Allowed readiness outputs:

- `FUND_AGENT_LLM_PROVIDER: present|absent`
- `FUND_AGENT_LLM_MODEL: present|absent`
- `FUND_AGENT_LLM_BASE_URL: present|absent`
- `FUND_AGENT_LLM_API_KEY_ENV_VAR: present|absent`
- `effective_api_key_value: present|absent`
- `config_validation: pass|fail`
- `config_error_class: LLMProviderConfigError` when validation fails
- `config_error_field`: env var name or coarse reason only, such as `missing FUND_AGENT_LLM_PROVIDER`, `missing API key value`, `unsupported provider`, or `invalid base URL shape`

Forbidden readiness outputs:

- the provider base URL value
- the model value
- the API key value
- the API key env var target value if it is not one of the public variable names
- HTTP headers
- provider account, region, organization, deployment or endpoint path

Recommended presence-only command for a future evidence gate:

```bash
python -c 'import os; from fund_agent.config.llm import load_llm_provider_config_from_env, LLMProviderConfigError; required=("FUND_AGENT_LLM_PROVIDER","FUND_AGENT_LLM_MODEL","FUND_AGENT_LLM_BASE_URL"); print("required_env_presence"); [print(k + ": " + ("present" if os.environ.get(k, "").strip() else "absent")) for k in required]; custom=bool(os.environ.get("FUND_AGENT_LLM_API_KEY_ENV_VAR", "").strip()); api_var=os.environ.get("FUND_AGENT_LLM_API_KEY_ENV_VAR", "FUND_AGENT_LLM_API_KEY"); print("FUND_AGENT_LLM_API_KEY_ENV_VAR: " + ("present" if custom else "absent")); print("effective_api_key_value: " + ("present" if os.environ.get(api_var, "").strip() else "absent"));
try:
    load_llm_provider_config_from_env()
except LLMProviderConfigError as exc:
    text=str(exc)
    safe=("missing FUND_AGENT_LLM_PROVIDER" if "FUND_AGENT_LLM_PROVIDER" in text else "missing FUND_AGENT_LLM_MODEL" if "FUND_AGENT_LLM_MODEL" in text else "missing FUND_AGENT_LLM_BASE_URL" if "FUND_AGENT_LLM_BASE_URL" in text else "missing API key value" if "API key" in text else "unsupported provider" if "unsupported provider" in text else "invalid base URL shape" if "URL" in text else "invalid typed config")
    print("config_validation: fail")
    print("config_error_class: LLMProviderConfigError")
    print("config_error_field: " + safe)
else:
    print("config_validation: pass")'
```

The future evidence artifact should paste only this presence-only output. It should not paste shell `export` lines, `.env` contents or command wrappers that reveal values.

## 4. Safe Evidence Fields From Existing Artifacts

Use only same-source retained artifact fields. Do not infer root cause from stderr anecdotes or from copied report bodies.

Allowed `summary.json` fields:

- root: `schema_version`, `fund_code`, `report_year`, `run_id`, `orchestration_status`, `final_assembly_status`, `redaction_applied`, `redaction_count`
- `chapter_matrix[]`: `chapter_id`, `status`, `stop_reason`, `failure_category`, `failure_subcategory`, `attempt_count`, `accepted_draft_present`, `accepted_conclusion_present`
- `first_failed`: same scalar fields as `chapter_matrix`
- `runtime_diagnostics.first_failed`: `chapter_id`, `status`, `stop_reason`, `category`, `subcategory`, `runtime_operation`, `provider_runtime_categories`, `provider_attempt_count`, `provider_max_attempts`, `repair_attempt_index`, `approx_prompt_tokens`, `system_prompt_chars`, `user_prompt_chars`, `max_output_chars`, `allowed_anchor_count`, `allowed_fact_count`, `timeout_seconds`, `timeout_budget_kind`, `timeout_max_attempts`, `timeout_backoff_seconds`, `timeout_root_cause_hint`
- `runtime_diagnostics.chapter_runtime_matrix[].runtime_diagnostics[]`: same scalar runtime fields plus `operation`, `provider_attempt_index`, `elapsed_ms`, `finish_reason`, `response_chars`, `error_type`, standard integer `status_code`
- `prompt_contract_diagnostics.chapter_phase_matrix[]`: `chapter_id`, `status`, `stop_reason`, `failure_category`, `failure_subcategory`, `attempt_count`, `phase`, `attempt_index`, `primary_subcategory`, `issue_id_prefix_counts`, `issue_reason_counts`, `required_structure_missing_count`, `required_output_missing_count`, `invalid_marker_count`, `unknown_anchor_count`, `response_length_incomplete_count`, `candidate_facet_assertion_count`, `forbidden_phrase_count`, `l1_numerical_closure_count`, `finish_reason`, `response_chars`, `max_output_chars`
- `final_assembly_issues[]`: `issue_id`, `reason`, `severity`, `chapter_ids`

Conditionally allowed only when needed for prompt/output-size correlation:

- `prompt_cost_diagnostic.component_costs`
- aggregate `anchor_cost_rows` / `fact_cost_rows` counts and character sizes
- fact status/missing reason counts

Do not use full anchor IDs or full fact IDs unless a later controller explicitly accepts them as safe. Aggregate them into counts and character-size totals.

Allowed per-chapter JSON fields:

- same scalar keys as above
- attempt indexes and file presence metadata
- post-repair terminal consistency fields once present

Forbidden evidence:

- `chapters/*-writer.md`
- `chapters/*-repair.md`
- `chapters/*-auditor-feedback.md`
- raw prompt body
- raw provider response
- raw audit response
- writer draft body
- repair draft body
- report markdown body
- raw PDF text
- raw parsed annual-report text
- provider base URL value
- model value
- API key value
- Authorization header
- Bearer token
- cookies, account IDs, organization IDs, deployment IDs or endpoint path values
- any direct quote of provider error messages if it embeds endpoint/account/request payload values

`request_id` is currently a safe opaque scalar in the serializer contract, but this gate should not use it for attribution because provider-specific request IDs may encode deployment or routing details in future providers. It may be retained in artifacts but should be omitted from human evidence unless needed for provider support escalation under a separate security review.

## 5. Need For Post-Repair Live Provider Evidence

Yes, a post-repair live provider evidence slice is needed before endpoint/config/default/runtime disposition.

Reasoning:

- The latest accepted implementation changed diagnostic retention and terminal lineage serialization, but no live retained artifact has yet proved those fields under the real provider path.
- The two most relevant retained live artifacts are pre-repair schema and showed cross-run volatility.
- Endpoint/config disposition requires distinguishing endpoint-wide provider instability from operation-specific timeout, budget insufficiency and content/audit failures. That classification depends on terminal consistency fields that old artifacts lack.

This gate does not run the slice. A controller must open/accept the evidence slice first.

### 5.1 Primary Post-Repair Evidence Slice

Purpose: collect one default-budget post-repair retained artifact under unchanged defaults.

Command:

```bash
uv run fund-analysis analyze 006597 --report-year 2024 --use-llm --llm-progress
```

Environment:

- Provider env must already be present and validated by the presence-only readiness command.
- Do not set `FUND_AGENT_LLM_TIMEOUT_SECONDS`.
- Do not set `FUND_AGENT_LLM_WRITER_TIMEOUT_SECONDS`.
- Do not set `FUND_AGENT_LLM_AUDITOR_TIMEOUT_SECONDS`.
- Do not set `FUND_AGENT_LLM_REPAIR_TIMEOUT_SECONDS`.
- Do not set `FUND_AGENT_LLM_TIMEOUT_MAX_ATTEMPTS` unless the controller explicitly wants to prove it is default; default is the comparison baseline.
- Do not change provider endpoint, model or key between readiness and live run.

Stop conditions:

- Stop after exactly one retained artifact is produced.
- Stop immediately if config validation fails; record presence-only failure and do not retry with ad hoc env changes.
- Stop if CLI exits before orchestration with missing/invalid provider config.
- Stop if no retained artifact is produced; record stdout byte count, exit code, safe stderr first line, and do not rerun until controller disposition.
- Stop if secret scan finds a real secret or raw payload in the retained artifact; quarantine evidence and do not paste matching value into docs.

Required artifact validation:

```bash
python -m json.tool NEW_ARTIFACT/summary.json
python -m json.tool NEW_ARTIFACT/manifest.json
rg -n "Authorization|Bearer |FUND_AGENT_LLM_API_KEY|api_key|sk-|raw_response|provider response|draft_markdown|system_prompt[^_]|user_prompt[^_]" NEW_ARTIFACT
```

Expected validation result:

- both JSON commands pass
- secret scan returns no matches, or only safe variable-name references that are explained without copying values
- `summary.json` contains post-repair terminal consistency fields in chapter-level or runtime summaries when a runtime failure occurs

Required evidence extraction:

- retained artifact path
- exit code
- stdout byte count only
- `orchestration_status`
- `final_assembly_status`
- chapter matrix
- first failed summary
- runtime first failed summary
- post-repair terminal consistency fields for every failed/blocked chapter
- prompt-contract diagnostic summary for non-runtime failures
- redaction status

### 5.2 Primary Slice Interpretation

PASS for diagnostic adequacy, not report acceptance, requires:

- retained artifact exists for incomplete live result, or accepted result is explicitly recorded as no incomplete artifact expected
- fail-closed stdout semantics preserved on incomplete run
- secret scan clean
- post-repair terminal consistency fields present when runtime failure occurs
- first-failed runtime summary matches terminal chapter lineage, or reports an explicit `missing_terminal_runtime_diagnostic` consistency status without inventing timeout scalars

The run can still exit `1`; diagnostic adequacy does not mean provider/report acceptance.

## 6. Root-Cause Classification Matrix

Root cause must be classified from same-source retained fields.

| Hypothesis | Supporting evidence | Refuting or limiting evidence | Disposition |
|---|---|---|---|
| Endpoint-wide latency/instability | Multiple operations or chapters show timeout with small or moderate prompts in the same run; timeout rows include `provider_runtime_category=timeout`, elapsed near budget, repeated attempts exhausted, and no content/audit blocker precedes them | Only one operation/chapter times out while other similar-cost calls accept; failures are prompt-contract/audit/anchor rather than timeout | Consider provider endpoint/config disposition only after at least two post-repair default runs or one default run plus a PASS-only timing probe show broad latency |
| Provider-specific latency | Same endpoint/model shows small-prompt timeout volatility across adjacent runs; timeout_root_cause_hint remains `small_prompt_provider_timeout`; no code/content change explains failure | Another provider/model is not tested in this gate; old artifacts cannot prove provider-specific root cause alone | Requires a separate endpoint/config comparison gate before changing provider config |
| Operation-specific latency | Timeouts cluster on `runtime_operation=auditor` or `writer` while other operation types accept under similar or larger prompt sizes | Mixed writer/auditor timeout in same run weakens operation-specific claim | Prefer split-audit or operation-specific timing probe before changing defaults |
| Budget insufficiency | Timeout rows are stable for one operation, all attempts reach configured timeout, no prompt-contract/audit blocker appears before terminal runtime failure, and a bounded operation-specific override later clears the same operation without causing new volatility | `120s` auditor-only run did not clear the report and introduced other failures; old artifact has Ch2 attribution gap | Do not change defaults until post-repair evidence plus targeted probe supports sufficiency |
| Prompt/output-size correlation | Timeout probability rises with `approx_prompt_tokens`, `user_prompt_chars`, `max_output_chars`, component cost totals or `response_chars`; failures cluster in high-cost chapters | Ch2 default timeout occurred at small prompt size; accepted chapters may have larger prompts | If supported, plan prompt-cost reduction or max-output tuning in a separate design gate |
| Audit/content failure | `failure_category=audit_rule_too_strict`, `repair_budget_exhausted`, `finish_reason=stop`, `response_chars` present, no provider runtime timeout, programmatic/LLM audit issue counts explain block | Runtime timeout is terminal and consistency fields show it is the final failure | Route to audit contract/calibration design, not endpoint disposition |
| Anchor/contract failure | `failure_category=prompt_contract`, `failure_subcategory=unknown_anchor` or marker/structure counters; writer parse phase identifies issue | No unknown-anchor/marker/structure counters and runtime timeout is terminal | Route to anchor/contract calibration, not provider endpoint |
| Ch3 C2/content failure | `programmatic:C2` under `prompt_contract` / `code_bug_other`, `phase=programmatic_audit`, repair budget exhausted | Ch3 not involved or runtime timeout terminal | Separate Ch3 calibration gate; do not solve via provider runtime tuning |

Classification rule: if terminal consistency is missing in a post-repair artifact, classify the artifact as diagnostic-defective for endpoint disposition rather than picking a root cause from incomplete fields.

## 7. Probe Ordering And Preconditions

Recommended order:

1. Presence-only provider config readiness.
2. One default-budget post-repair live evidence slice.
3. Decide whether evidence is diagnostic-adequate. If not, fix diagnostics before more provider probes.
4. If default post-repair evidence shows runtime latency but not broad endpoint failure, run PASS-only timing probe design gate.
5. If runtime latency clusters by operation, run split-audit probe design gate.
6. Only after PASS-only and/or split-audit evidence supports a specific runtime bottleneck, consider timeout default change design.
7. Only after endpoint-wide or provider-specific evidence survives targeted probes, consider provider endpoint/config change design.

PASS-only timing probe preconditions:

- post-repair default artifact exists or accepted no-artifact result is recorded
- terminal consistency fields validate runtime lineage
- no secret-scan failure
- probe uses a minimal provider call path that cannot produce report content artifacts
- probe records only timing, status class, timeout category and coarse operation label
- separate design/controller judgment accepts exact command and artifact destination

Split-audit probe preconditions:

- default post-repair evidence shows auditor-specific failure or ambiguity
- PASS-only probe does not show endpoint-wide timeout on minimal requests
- split-audit does not relax programmatic blockers or final fail-closed behavior
- split-audit records writer and auditor operation timing separately without raw prompts/responses

Timeout default change preconditions:

- at least one post-repair default artifact and one targeted probe show stable budget insufficiency for a specific operation
- raising an operation-specific timeout clears the targeted runtime blocker without introducing broader audit/anchor/content volatility
- no report acceptance is inferred solely from a single partial or accepted run
- controller opens a heavy implementation gate for default behavior change

Provider endpoint/config change preconditions:

- presence-only readiness passes
- post-repair default artifact shows endpoint-wide or provider-specific instability, not just one chapter/auditor timeout
- PASS-only timing or equivalent endpoint health evidence supports endpoint-level latency
- config change candidate is defined without printing secret values
- controller opens a heavy provider disposition implementation/config gate

## 8. No-Goals

- Do not change provider default timeout.
- Do not change writer, auditor, prompt contract, CHAPTER_CONTRACT or audit rules.
- Do not implement Ch3 calibration.
- Do not implement Ch3, Ch2 or any body chapter logic change.
- Do not connect `chapter_generation_score` or score-loop.
- Do not change FQ0-FQ6 quality gate, golden/readiness, fixture promotion or release state.
- Do not relax fail-closed behavior.
- Do not turn live incomplete result into deterministic fallback.
- Do not emit stdout partial reports from incomplete `--use-llm` runs.
- Do not add provider fallback or multi-provider selection.
- Do not print provider base URL, model value or API key value.
- Do not use old pre-repair artifacts as proof of post-repair terminal consistency.

## 9. Acceptance Matrix For The Future Evidence Gate

| Check | Accept | Reject / block |
|---|---|---|
| Readiness | presence-only config validation recorded without secret values | any base URL/model/key value printed |
| Scope | no code/config/default/runtime changes | any default timeout/provider/auditor/prompt change |
| Live command | exactly one controller-approved live command | ad hoc reruns after seeing failures |
| Retained artifact | valid `summary.json` and `manifest.json`, or accepted complete run with no incomplete artifact expected | missing artifact for incomplete run without explanation |
| Secret scan | clean or explained safe variable-name hits only | secret, endpoint value, model value, raw prompt/response/draft/report body present |
| Post-repair schema | terminal consistency fields present for runtime failures | pre-repair-only field set used for new disposition |
| Fail-closed semantics | incomplete run exits nonzero with stdout empty | incomplete run emits deterministic fallback or partial report |
| Root-cause classification | uses retained scalar fields and terminal consistency | uses indirect logs, anecdotes, provider guesses or copied bodies |
| Disposition | recommends next gate only | directly changes provider endpoint/config/default/runtime |

## 10. Next Gate Recommendation

Recommended next gate: `MVP post-repair provider endpoint disposition evidence slice`.

Classification: heavy, evidence-only.

Purpose:

- run presence-only provider config readiness
- run exactly one default-budget `006597 / 2024 --use-llm` live evidence slice if readiness passes
- validate retained artifact and secret safety
- verify post-repair terminal lineage fields under real provider behavior
- classify whether the next design gate should be PASS-only timing probe, split-audit probe, diagnostics repair, Ch3 calibration, or endpoint/config disposition

The next gate should still not change defaults, endpoint config, provider selection, prompt/auditor behavior, final assembly, score-loop or fail-closed semantics.

## 11. Blocking Open Questions

1. Does the controller want the next evidence gate to permit exactly one live default-budget run, or require an additional reviewer plan before any provider call?
2. If the post-repair default run accepts all body chapters, should the next gate stop at recording acceptance volatility evidence, or still run PASS-only timing to characterize endpoint health?
3. What is the minimum evidence threshold for provider endpoint/config disposition: two post-repair default runs with broad runtime failures, or one default run plus a PASS-only timing probe?
