# MVP LLM acceptance volatility and diagnostic evidence reconciliation design/plan

## Scope And Role

- Role: planning/design specialist only, not controller.
- Gate: `MVP LLM acceptance volatility and diagnostic evidence reconciliation design gate`.
- Classification: `heavy`.
- Output: code-generation-ready design/plan artifact.
- Actions intentionally not taken: no source, test, config, runtime behavior, provider timeout default, provider endpoint, auditor rule, template truth, quality/golden/readiness, score-loop, retained report, staging, commit, push, PR or live provider call changes.
- Explicit non-goals: do not continue Ch3 calibration implementation; do not implement PASS-only, split-audit, `audit_focus`, diagnostic serializer, endpoint disposition or provider budget changes in this gate.

## Required Input Disposition

| Input | Disposition |
|---|---|
| `AGENTS.md` | reviewed for Chinese response, heavy gate, first-principles, same-source root cause and fail-closed constraints |
| `docs/design.md` | reviewed for current Route C, Service/Host/Agent boundary, future typed template/audit/Agent design and non-goals |
| `docs/implementation-control.md` | reviewed for current gate, accepted evidence and prohibited changes |
| `docs/current-startup-packet.md` | reviewed for short startup state and residuals |
| `docs/reviews/mvp-ch2-auditor-timeout-120s-evidence-20260603.md` | reviewed as direct 120s diagnostic evidence |
| `docs/reviews/mvp-ch2-auditor-timeout-120s-evidence-controller-judgment-20260603.md` | reviewed for accepted/rejected conclusions |
| `docs/reviews/mvp-ch2-auditor-timeout-diagnostic-design-plan-20260603.md` | reviewed for prior diagnostic design and safe evidence contract |
| `docs/reviews/mvp-provider-runtime-budget-calibration-evidence-resume-20260603.md` | reviewed for default resumed live evidence |
| Default retained run `reports/llm-runs/006597-2024-20260602T220325Z-host_run_c83e8c1adcc846a/summary.json` | inspected only through safe scalar fields |
| 120s retained run `reports/llm-runs/006597-2024-20260602T224137Z-host_run_4b7dddc60d084e7/summary.json` | inspected only through safe scalar fields |
| 120s `chapter-01/02/04/05/06.json` | inspected only for status, stop reason, issue ids/reasons, repair decisions and scalar diagnostics; writer/auditor markdown files were not opened |

Supplemental read-only code inspection for implementation readiness:

- `fund_agent/services/chapter_orchestrator.py`: `ChapterRunResult`, `_exception_result()`, `serialize_chapter_runtime_diagnostics()`, `_runtime_diagnostics_for_run()` and runtime diagnostic payload fields.
- `fund_agent/services/llm_run_artifacts.py`: current retained artifact serializer references.
- `tests/services/test_chapter_orchestrator.py` and `tests/services/test_llm_run_artifacts.py`: existing coverage anchors for runtime/prompt diagnostics.

## Same-Source Evidence Summary

Default resumed run:

- Artifact: `reports/llm-runs/006597-2024-20260602T220325Z-host_run_c83e8c1adcc846a`.
- Summary fields: `orchestration_status=partial`, `final_assembly_status=incomplete`.
- Chapter matrix: Ch1 accepted, Ch2 failed `llm_timeout`, Ch3 failed `repair_budget_exhausted` / `prompt_contract` / `code_bug_other`, Ch4 accepted, Ch5 accepted, Ch6 accepted.
- Ch2 runtime fields: `runtime_operation=auditor`, `provider_attempt_count=2`, `provider_max_attempts=2`, `timeout_seconds=60.0`, `timeout_budget_kind=auditor`, `approx_prompt_tokens=758`, `timeout_root_cause_hint=small_prompt_provider_timeout`.
- Ch3 prompt fields: `issue_id_prefix_counts={"programmatic:C2": 1}`, `phase=programmatic_audit`.

120s auditor-only diagnostic run:

- Artifact: `reports/llm-runs/006597-2024-20260602T224137Z-host_run_4b7dddc60d084e7`.
- Summary fields: `orchestration_status=blocked`, `final_assembly_status=incomplete`.
- Chapter matrix: Ch1 failed `repair_budget_exhausted` / `audit_rule_too_strict`; Ch2 failed `llm_timeout`; Ch3 failed `repair_budget_exhausted` / `prompt_contract` / `code_bug_other`; Ch4 failed `repair_budget_exhausted` / `audit_rule_too_strict`; Ch5 failed `llm_timeout`; Ch6 blocked `unknown_anchor` / `prompt_contract` / `unknown_anchor`.
- Ch2 chapter JSON has top-level `stop_reason=llm_timeout` and issue text class `LLMProviderTimeoutError`, but `chapter_runtime_diagnostics` contains only an auditor row with `finish_reason=stop`, `response_chars=22`, no timeout scalar fields and `chapter_failure_category=prompt_contract`; its attempt repair decision references `programmatic:L1`.
- Ch1 issue classes are unsupported anchor/fact and unsupported `non_asserted_facet_boundary`; Ch4 issue classes are unsupported pure-bond facet and unsupported investor-behavior inference.
- Ch5 has writer timeout rows: `operation=writer`, `timeout_budget_kind=writer_initial`, `timeout_seconds=60.0`, `provider_attempt_index=1/2` and `2/2`, `approx_prompt_tokens=2518`, `max_output_chars=12000`, `timeout_root_cause_hint=small_prompt_provider_timeout`.
- Ch6 prompt diagnostic fields: `phase=writer_parse`, `issue_id_prefix_counts={"writer:unknown_anchor": 1}`, `issue_reason_counts={"unknown_anchor": 1}`, `unknown_anchor_count=1`, `response_chars=2633`.

Inference label: the Ch2 discrepancy is a diagnostic attribution gap, not a proven provider-budget root cause. The same retained chapter file simultaneously exposes a terminal timeout classification and a non-timeout diagnostic row. Until serialization/lineage is repaired, future budget probes can produce misleading first-failed evidence.

## Problem Decomposition

### 1. Ch2 Diagnostic Attribution Gap

Observed same-source contradiction:

- Chapter-level result says `status=failed`, `stop_reason=llm_timeout`, `failure_category=llm_timeout`.
- Chapter issues mention `LLMProviderTimeoutError`.
- The exposed runtime diagnostic row for Ch2 is auditor `finish_reason=stop`, `response_chars=22`, no `timeout_seconds`, no `timeout_budget_kind`, no provider attempt scalar, and `chapter_failure_category=prompt_contract`.
- The same chapter attempt has a `programmatic:L1` repair decision before the terminal timeout classification.

Design conclusion:

- Do not use current Ch2 120s artifact to tune provider timeout defaults.
- Treat the artifact as evidence that retained diagnostics can conflate prior audit/repair diagnostics with terminal runtime failure.
- The next implementation must make terminal failure lineage explicit and machine-checkable before any further live provider probe.

Required invariant:

```text
If ChapterRunResult.stop_reason is a provider/runtime stop reason,
then serialized diagnostics must expose either:
1. at least one terminal runtime diagnostic with matching category/operation/attempt, or
2. an explicit diagnostic_consistency_status explaining why terminal runtime fields are unavailable.
```

### 2. Ch1/Ch4 Cross-Run Acceptance Volatility

Observed same-source contrast:

- Default resumed run accepted Ch1 and Ch4.
- 120s auditor-only diagnostic failed Ch1 and Ch4 with `audit_rule_too_strict` / `repair_budget_exhausted`.
- Ch1/Ch4 issue texts point to unsupported facet/inference classes, not provider timeout.

Design conclusion:

- This is acceptance volatility under live LLM nondeterminism and strict evidence boundaries.
- It is not evidence that the auditor should be relaxed.
- It is evidence that semantic audit failures need typed issue taxonomy and repeatable diagnostics before release or score-loop work.

Required invariant:

```text
An accepted chapter in one live run does not invalidate a later fail-closed audit issue.
Cross-run volatility must be recorded as evidence volatility, not resolved by weakening blockers.
```

### 3. Ch5 Writer Timeout Boundary

Observed same-source fields:

- 120s run Ch5 failed before accepted draft/conclusion.
- Runtime rows show writer `60s x2`, `timeout_budget_kind=writer_initial`, `approx_prompt_tokens=2518`, `max_output_chars=12000`.
- Default resumed run accepted Ch5.

Design conclusion:

- Ch5 is writer endpoint/runtime evidence under unchanged writer budget.
- It is not evidence for changing writer default timeout because it appears in a volatility run whose other chapters also changed status.
- It must be carried as provider endpoint/runtime disposition evidence, separate from Ch2 auditor budget.

### 4. Ch6 Unknown Anchor

Observed same-source fields:

- Ch6 `status=blocked`, `stop_reason=unknown_anchor`, `failure_category=prompt_contract`, `failure_subcategory=unknown_anchor`.
- Prompt diagnostic fields show `phase=writer_parse`, `writer:unknown_anchor=1`, `unknown_anchor_count=1`.
- Chapter issue text says `bond_risk_evidence` group anchor was not expanded into `ChapterEvidenceAnchor`.

Design conclusion:

- Ch6 belongs to typed anchor/evidence contract, not provider runtime.
- Future fix must be in Fund/Agent evidence-anchor conversion and writer parse diagnostics, not auditor relaxation or provider timeout tuning.

## Design Decision

Decision: the next accepted path should first repair local typed diagnostic serialization/lineage, then run or design further provider endpoint disposition evidence. Do not run more live provider probes on top of the current attribution gap.

Rationale:

- Same-source root cause requires a trustworthy diagnostic contract.
- Current Ch2 evidence cannot distinguish terminal provider timeout from prior programmatic/audit repair state.
- Cross-run volatility makes single-run acceptance insufficient for default changes.
- Ch5 and Ch6 show at least two other failure classes that budget-only probes cannot reconcile.

## Code-Generation-Ready Implementation Plan

### Slice 1: Typed Diagnostic Serialization Repair

Classification: heavy or standard at controller discretion; choose heavy if this changes public CLI diagnostic semantics or retained artifact schema semantics.

Allowed files:

- `fund_agent/services/chapter_orchestrator.py`
- `fund_agent/services/llm_run_artifacts.py`
- `tests/services/test_chapter_orchestrator.py`
- `tests/services/test_llm_run_artifacts.py`
- `tests/README.md` only if test conventions change; otherwise no README update.

Non-goals:

- No provider call.
- No timeout default change.
- No auditor rule change.
- No prompt/body/raw response persistence.
- No deterministic fallback.
- No complete-report stdout change.

Implementation decisions:

1. Add a safe diagnostic consistency layer, not a new business outcome.
   - Suggested enum strings:
     - `consistent`
     - `missing_terminal_runtime_diagnostic`
     - `terminal_category_conflict`
     - `non_runtime_terminal_without_scalar`
   - Suggested serialized fields:
     - `diagnostic_consistency_status`
     - `terminal_stop_reason`
     - `terminal_failure_category`
     - `terminal_runtime_operation`
     - `terminal_repair_attempt_index`
     - `terminal_runtime_diagnostic_present`
     - `terminal_issue_class`
   - These fields must be scalar allowlisted values only.

2. Preserve current safe runtime rows, but make terminal lineage visible.
   - Do not delete prior audit/runtime rows.
   - Add terminal summary that is computed from `ChapterRunResult.stop_reason`, `failure_category`, `issues`, `runtime_diagnostics` and attempt diagnostics.
   - If a timeout/error issue exists but no timeout scalar exists, set `terminal_runtime_diagnostic_present=false` and `diagnostic_consistency_status=missing_terminal_runtime_diagnostic`.

3. Prefer matching terminal diagnostics in first-failed summaries.
   - `_first_failed_runtime_diagnostic()` should not blindly use the first collected row when it conflicts with chapter terminal status.
   - For `stop_reason=llm_timeout`, prefer runtime rows with `provider_runtime_category=timeout` or `timeout_budget_kind != None`.
   - If none exists, preserve existing fields as nullable and set consistency status.

4. Ensure exception diagnostics are not lost when a prior attempt already has non-timeout audit diagnostics.
   - Implementation agent must write a regression test that creates an attempt with prior audit diagnostic, then terminal `LLMProviderTimeoutError`, and verifies terminal timeout is serialized or explicitly marked missing.
   - If current control flow cannot represent both rows without behavior change, do not change chapter acceptance behavior; only expose the inconsistency.

5. Keep prompt-contract diagnostics separate.
   - `programmatic:L1`, `writer:unknown_anchor` and `llm:0:*` counts remain prompt/audit/anchor diagnostics.
   - Runtime serializer must not reinterpret these as provider runtime.

Expected tests:

- A failed chapter with `stop_reason=llm_timeout` and real timeout diagnostic serializes `diagnostic_consistency_status=consistent`, `timeout_budget_kind` and provider attempts.
- A failed chapter with `stop_reason=llm_timeout` but only auditor `finish_reason=stop` diagnostic serializes `missing_terminal_runtime_diagnostic` and does not claim a timeout scalar.
- A failed chapter with `audit_rule_too_strict` serializes no timeout scalar and does not become provider runtime.
- A blocked `unknown_anchor` chapter remains `prompt_contract` / `unknown_anchor` and surfaces `writer_parse` counts only in prompt-contract diagnostics.
- Retained artifact serializer includes new safe fields without prompt, draft, raw provider response, raw audit response, API key, provider base URL or model value.

Validation commands:

```bash
uv run pytest tests/services/test_chapter_orchestrator.py tests/services/test_llm_run_artifacts.py
uv run pytest tests/ui/test_cli.py -k "llm and diagnostic"
```

Completion evidence:

- Test output.
- A short before/after serializer fixture summary using fake clients only.
- No live provider run.
- Secret-safety scan over generated test artifacts if any are written.

### Slice 2: Provider Endpoint Disposition Design/Evidence Gate

Run only after Slice 1 has been reviewed and accepted.

Purpose:

- Decide whether observed small-prompt writer/auditor timeouts are endpoint/runtime instability, provider-specific latency, or budget insufficiency.
- Keep this as evidence/disposition before any default timeout change.

Allowed evidence:

- Presence-only provider config readiness.
- Safe run metadata from retained artifacts.
- Optional live provider command only under a separate controller-authorized evidence gate.
- No raw prompt/body/response/base URL/model/API key.

Minimum design questions:

- Does the current endpoint routinely exceed 60s for small prompts across writer and auditor?
- Are timeouts operation-specific or endpoint-wide?
- Is the failure correlated with prompt size, output cap, attempt index, or live volatility?
- Is a provider endpoint switch/config disposition needed before changing code defaults?

Stop conditions:

- Any config/auth failure routes to provider config/auth, not runtime budget.
- Any secret-bearing output stops the gate.
- Any complete accepted run does not by itself authorize defaults; repeatability/cost still needs controller judgment.

### Slice 3: Volatility Matrix Evidence Gate

Run only after diagnostic repair.

Purpose:

- Compare default and diagnostic runs with a stable safe schema.
- Classify chapter outcomes by failure family:
  - provider runtime
  - prompt/anchor contract
  - audit semantic blocker
  - programmatic audit blocker
  - final assembly dependency

Expected artifact:

- A review/evidence markdown table that cites only safe summary fields and new diagnostic consistency fields.
- No report body or raw LLM content.

### Slice 4: Bounded Semantic `audit_focus` Design Gate

Run only after Slice 1 and volatility matrix are accepted.

Purpose:

- Design future bounded semantic audit emphasis without disabling programmatic blockers.
- Address Ch1/Ch4 audit-rule volatility by narrowing what LLM auditor is asked to judge, not by relaxing evidence requirements.

Required constraints:

- Programmatic blockers remain authoritative.
- `audit_focus` is a typed per-chapter semantic emphasis, not an auditor bypass.
- It must not accept unsupported facets, unsupported causal/behavior inferences or unknown anchors.
- It must not change current chapter ids `0-7` or implement Ch2 split.

### Deferred Probes: PASS-only Timing And Split-Audit

PASS-only timing probe:

- Do not run now.
- It may be designed later only if endpoint disposition still cannot distinguish auditor endpoint latency from audit-content latency.
- It must be clearly labeled synthetic timing evidence and cannot prove report acceptance.
- It must not persist prompt/raw response and must not be wired into production auditor behavior.

Split-audit probe:

- Do not run now.
- It changes audit shape and could mask programmatic-first semantics if rushed.
- It requires a separate design gate after `audit_focus` design clarifies bounded semantic responsibilities.

## Ordering Recommendation

1. Typed diagnostic serialization repair implementation gate.
2. Re-review of diagnostic repair with fake-client tests only.
3. Provider endpoint disposition design/evidence gate.
4. Volatility matrix evidence gate using repaired diagnostics.
5. Bounded semantic `audit_focus` design gate.
6. Only then consider PASS-only timing probe design.
7. Split-audit probe remains later than PASS-only and `audit_focus`; do not implement from this gate.

Do not start Ch3 calibration implementation until steps 1-4 have made runtime/audit/anchor volatility legible.

## Safe Evidence Fields

Allowed:

- `schema_version`
- `run_id`
- `fund_code`
- `report_year`
- `orchestration_status`
- `final_assembly_status`
- `redaction_applied`
- `redaction_count`
- `chapter_id`
- `title`
- `status`
- `stop_reason`
- `failure_category`
- `failure_subcategory`
- `attempt_count`
- `accepted_draft_present`
- `accepted_conclusion_present`
- `issue_id_prefix_counts`
- `issue_reason_counts`
- `phase`
- `primary_subcategory`
- `finish_reason`
- `response_chars`
- `operation`
- `provider_attempt_index`
- `provider_max_attempts`
- `provider_runtime_category`
- `elapsed_ms`
- `status_code`
- `request_id`
- `system_prompt_chars`
- `user_prompt_chars`
- `approx_prompt_tokens`
- `allowed_fact_count`
- `allowed_anchor_count`
- `max_output_chars`
- `timeout_seconds`
- `timeout_max_attempts`
- `timeout_backoff_seconds`
- `timeout_budget_kind`
- `repair_timeout_fallback_used`
- `timeout_root_cause_hint`
- `diagnostic_consistency_status`
- `terminal_runtime_diagnostic_present`
- `terminal_stop_reason`
- `terminal_failure_category`
- `terminal_runtime_operation`
- `terminal_repair_attempt_index`
- safe issue ids/reasons that do not include report prose, prompt text or provider payloads

Forbidden:

- API key
- Authorization header
- Bearer token
- cookie
- password
- provider base URL value
- model value
- raw prompt body
- system prompt body
- user prompt body
- writer draft body
- repair draft body
- raw provider response
- raw audit response
- full report body
- markdown chapter body
- raw PDF text
- raw parsed annual-report text
- any copied provider request/response JSON payload

## Acceptance Matrix

| Requirement | Acceptance signal | Reject/stop signal |
|---|---|---|
| Ch2 attribution gap reconciled | Terminal timeout either has matching timeout diagnostics or explicit `missing_terminal_runtime_diagnostic` | `llm_timeout` terminal row still exposes only non-timeout scalar fields with no consistency status |
| Ch1/Ch4 volatility preserved fail-closed | Plan records `audit_rule_too_strict` as volatility evidence and keeps blockers strict | Auditor relaxation, ignored unsupported facet/inference issue, or accepted-by-default rule |
| Ch5 evidence bounded | Writer timeout kept as provider/runtime evidence under unchanged writer budget | Writer default changed from this gate |
| Ch6 typed anchor issue classified | `unknown_anchor` remains prompt/anchor contract issue with writer-parse counts | Reclassified as provider timeout or auditor strictness |
| Safe evidence contract maintained | Serializer/tests exclude forbidden fields | Any prompt/body/raw response/key/base URL/model leaks |
| Default deterministic behavior untouched | No changes to deterministic `analyze/checklist` | Any deterministic fallback or partial report stdout |
| Incomplete LLM behavior untouched | Incomplete `--use-llm` remains fail-closed | Partial LLM result falls back to deterministic report |
| Future probes ordered | Serializer repair and endpoint disposition precede PASS-only/split-audit | Live PASS-only/split-audit runs before diagnostic repair |

## Stop Conditions

- Stop if any required artifact JSON is invalid.
- Stop if any evidence requires raw prompt, raw draft, raw provider response, raw audit response, API key, provider base URL or report body.
- Stop if implementation would change deterministic `analyze/checklist`.
- Stop if implementation would let incomplete LLM results fall back to deterministic output.
- Stop if a proposed fix relaxes auditor, anchor validation, programmatic blockers, repair budget or fail-closed semantics.
- Stop if Ch2 split, `0+9`, `0+10`, Agent runner/tool-loop, multi-year runtime, score-loop or provider default behavior is being written as current fact.
- Stop if provider endpoint/base/model/key disposition requires printing secrets.
- Stop if unrelated dirty files are needed for the slice and ownership is unclear.

## Review Handoff

Reviewers should challenge:

- Whether the plan keeps root-cause claims same-source and labels inference.
- Whether diagnostic repair is narrowly scoped to serialization/lineage, not behavior.
- Whether Ch1/Ch4 volatility is preserved without weakening audit.
- Whether Ch5 and Ch6 are classified into separate failure families.
- Whether PASS-only and split-audit are correctly deferred.
- Whether safe/forbidden evidence fields are complete enough for retained artifacts.

## Next Gate Recommendation

Recommended next gate:

`MVP typed diagnostic serialization repair implementation gate`

Gate objective:

- Implement safe terminal diagnostic lineage and consistency fields for retained incomplete LLM artifacts.
- Use fake-client/unit tests only.
- Do not run live provider.
- Do not change timeout defaults, auditor rules, prompt contracts, deterministic mainline, final assembly, score-loop or provider endpoint config.

Blocking open questions:

- None for the design/plan artifact.
- Controller must still decide reviewer assignment and whether the next implementation gate is classified as `standard` or `heavy`; given public fail-closed diagnostics and retained artifact semantics, this plan recommends `heavy` when uncertain.
