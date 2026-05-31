# MVP Provider Runtime Budget and Prompt-Cost Root-Cause Calibration Plan

## Gate / Role

- Gate: `MVP provider runtime budget and prompt-cost root-cause calibration gate`
- Classification: `heavy`
- Role: Gateflow planning agent only; not controller, not implementation worker.
- Date: 2026-05-31.
- Output status: handoff-ready / code-generation-ready.
- Allowed outcome: a local implementation plan for safe diagnostics, prompt-cost compaction, bounded runtime budget calibration, and real-provider smoke rerun.

## Goal / Motivation

Calibrate the real-provider timeout root cause with same-source, safe diagnostics, then apply the smallest safe runtime-budget and prompt-cost fixes needed for the explicit `--use-llm` path.

The gate must distinguish:

- `large_writer_prompt_cost`: writer timeouts where prompt size is itself a likely root-cause contributor, currently chapter 2 and chapter 6.
- `small_prompt_provider_timeout`: writer/auditor timeouts where prompt size is not large enough to explain the timeout alone, currently chapter 1 writer and chapter 3/5 auditor.
- `provider_runtime / endpoint blocker`: if small prompts still time out after bounded budget calibration, classify the blocker as provider/runtime endpoint reliability rather than hiding it behind prompt changes.

The fix must preserve fail-closed behavior: no deterministic fallback, no partial report accepted as complete, no relaxation of writer/auditor/programmatic/LLM audit boundaries, and no secret or full-prompt leakage.

## Direct Evidence

Source files read for this plan:

- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/reviews/mvp-real-provider-smoke-independent-body-matrix-evidence-20260531.md`
- `docs/reviews/mvp-real-provider-smoke-independent-body-matrix-controller-judgment-20260531.md`
- `reports/mvp-real-provider-smoke-rerun/20260531-independent-body-matrix/service-diagnostic.json`
- Minimal writer/auditor/provider runtime code needed to identify file ownership and schemas.

Current real-provider smoke result for `006597 / 2024 --use-llm`:

- CLI exit `1`, stdout empty, no deterministic fallback.
- `orchestration_status=partial`, `final_assembly_status=incomplete`, `report_markdown_present=false`.
- `generated_chapter_ids=[1,2,3,4,5,6]`, `skipped_chapter_ids=[]`, `accepted_chapter_ids=[4]`.
- Failed rows are provider runtime timeout rows; no provider config/auth, prompt contract, audit parse, fact gap, deterministic fallback, or code-exception evidence is primary.

Safe service diagnostic timeout matrix:

| Chapter | Operation | Attempts | Max elapsed ms | System chars | User chars | Approx tokens | Max output chars | Current classification |
|---:|---|---:|---:|---:|---:|---:|---:|---|
| 1 | writer | `2/2` | `60081` | `87` | `8719` | `2202` | `12000` | `small_prompt_provider_timeout` candidate |
| 2 | writer | `2/2` | `60080` | `87` | `104256` | `26086` | `12000` | `large_writer_prompt_cost` candidate |
| 3 | auditor | `2/2` | `60060` | `54` | `4131` | `1047` | n/a | `small_prompt_provider_timeout` candidate |
| 5 | auditor | `2/2` | `60030` | `54` | `3878` | `983` | n/a | `small_prompt_provider_timeout` candidate |
| 6 | writer | `2/2` | `60087` | `87` | `116223` | `29078` | `12000` | `large_writer_prompt_cost` candidate |

Direct code facts:

- `fund_agent/fund/chapter_writer.py` builds writer prompts and currently serializes full fact values and anchors into `允许 facts` / `允许 anchors`.
- `fund_agent/fund/chapter_auditor.py` builds a small LLM audit request; provider adapter appends draft markdown, fact ids, anchor ids, and audit focus.
- `fund_agent/services/llm_provider.py` records provider-bound total prompt chars/tokens, attempts and elapsed time, but not component-level writer prompt cost.
- `fund_agent/services/chapter_orchestrator.py` serializes safe runtime diagnostics and preserves fail-closed partial orchestration.
- `fund_agent/config/llm.py` currently has one request timeout, one timeout max-attempts, one backoff, and one writer `max_output_chars`.
- CLI builds `ChapterOrchestrationPolicy(max_output_chars=config.max_output_chars)` only for explicit `--use-llm`.

## Scope

Implement only the minimum code and tests required to:

1. Add prompt-cost diagnostics that are safe enough to store in service diagnostic JSON.
2. Identify writer component cost by chapter and source field without storing prompt text.
3. Compact extreme writer prompt payloads for chapter 2 and chapter 6 without deleting required fact semantics or weakening evidence rules.
4. Calibrate bounded timeout budget by operation and repair attempt while keeping timeout-only retry finite.
5. Rerun deterministic, missing-config, and real-provider smoke validations.

## Non-Goals

- Do not enter Gate 5 Dayu / Host / Agent runtime.
- Do not implement fact lookup tools, tool loops, `dayu.host`, `dayu.engine`, `FundToolService`, provider fallback, multi-model routing, or chapter 0/7 LLM polish.
- Do not change golden, fixtures, extraction score, score-loop implementation, quality gate semantics, final judgment semantics, snapshots, manifests, promotion state, release readiness, PR state, push, merge, or release.
- Do not record API keys, Authorization headers, full prompt, full draft, full provider response, raw audit response, model request body, or provider response body.
- Do not make deterministic `fund-analysis analyze` or `fund-analysis checklist` depend on provider-backed behavior.
- Do not treat a partial chapter matrix as a complete accepted report.

## Safety Invariants

- Compress expression only; do not remove chapter-mandated fact semantics.
- Do not fake missing facts or imply that omitted prompt detail is available to the LLM.
- Do not relax evidence anchors, `ITEM_RULE`, candidate facet handling, forbidden trading advice, E2 deferral, programmatic audit, LLM audit parsing, or writer marker parsing.
- The LLM may cite only facts and anchor ids actually present in the compact payload.
- Compact payloads must preserve `fact_id`, `source_field_id`, fact `status`, `missing_reason`, `evidence_anchor_ids`, `anchor_id`, and anchor source section metadata.
- If a required fact cannot be safely represented inside the compact budget, fail closed before provider call or preserve an explicit compacted representation that says the raw detail is not available in prompt. Do not let the writer invent the omitted detail.
- Timeout handling remains bounded: no infinite retry, no retry for non-timeout errors unless a future gate explicitly accepts it, no swallowed timeout, no deterministic fallback.

## Affected Files / Modules

Implementation should be limited to these files unless tests reveal a necessary adjacent update:

- `fund_agent/fund/chapter_writer.py`
- `fund_agent/fund/chapter_auditor.py` only if audit request must carry attempt/budget metadata.
- `fund_agent/services/llm_provider.py`
- `fund_agent/services/chapter_orchestrator.py`
- `fund_agent/config/llm.py`
- `fund_agent/ui/cli.py` only for safe diagnostic summary fields or typed config plumbing.
- `fund_agent/services/__init__.py` only if new public Service diagnostic helpers are exported.
- Tests:
  - `tests/fund/test_chapter_writer.py`
  - `tests/fund/test_chapter_auditor.py` only if audit request schema changes.
  - `tests/services/test_llm_provider.py`
  - `tests/services/test_chapter_orchestrator.py`
  - `tests/config/test_llm_config.py`
  - `tests/ui/test_cli.py`
- Docs after implementation:
  - `fund_agent/fund/README.md` if writer prompt payload/compaction contract changes.
  - `fund_agent/config/README.md` if new env vars or budget semantics are added.
  - `fund_agent/README.md` only if Service/Fund boundary wording changes.
  - `docs/design.md` only for accepted current design facts after code/review acceptance.
  - `tests/README.md` only if test commands or conventions change.

Do not modify `AGENTS.md` or `docs/fund-analysis-template-draft.md`.

## Contract / Schema / State-Machine Changes

### Prompt-Cost Diagnostic Contract

Add a safe writer prompt-cost diagnostic contract. The implementation may choose dataclasses or typed dicts, but the serialized shape must include:

- `schema_version`: e.g. `chapter_prompt_cost_diagnostic_payload.v1`.
- Per chapter and operation:
  - `chapter_id`
  - `operation`: `writer` or `auditor`
  - `repair_attempt_index`
  - `provider_attempt_index`
  - `system_prompt_chars`
  - `user_prompt_chars`
  - `approx_prompt_tokens`
  - `max_output_chars`
  - `timeout_root_cause_hint`
- Writer component cost breakdown:
  - `protocol_chars`
  - `contract_chars`
  - `must_answer_chars`
  - `must_not_cover_chars`
  - `required_output_chars`
  - `facts_chars`
  - `anchors_chars`
  - `repair_context_chars`
- Fact cost rows:
  - `fact_id`
  - `source_field_id`
  - `status`
  - `missing_reason`
  - `value_chars`
  - `serialized_fact_chars`
  - `evidence_anchor_count`
  - `required_by_count`
  - no fact value text
- Anchor cost rows:
  - `anchor_id`
  - `source_kind`
  - `document_year`
  - `section_id`
  - `table_id`
  - `row_locator_present`
  - `serialized_anchor_chars`
  - no full anchor note if it can contain source text

Do not serialize complete prompt text, complete draft markdown, provider request JSON, provider response JSON, raw audit response, API key, Authorization header, or model secret-bearing config.

### Runtime Diagnostic Contract

Bump or extend runtime diagnostic payload safely. Existing v1 fields should remain present for compatibility with current evidence scripts. Add:

- `timeout_seconds`: effective timeout used for the provider attempt.
- `timeout_max_attempts`: effective max attempts.
- `timeout_backoff_seconds`: effective backoff.
- `timeout_budget_kind`: `writer_initial`, `auditor`, or `writer_repair`.
- `timeout_root_cause_hint`: one of:
  - `large_writer_prompt_cost`
  - `small_prompt_provider_timeout`
  - `provider_runtime_timeout_uncalibrated`
  - `non_timeout_provider_runtime`
  - `not_provider_runtime`
- Optional nested or referenced writer prompt-cost diagnostic, still safe and scalar-only.

Classification rule for this gate:

- `large_writer_prompt_cost`: `operation=writer`, `provider_runtime_category=timeout`, and `approx_prompt_tokens >= 8000`.
- `small_prompt_provider_timeout`: `provider_runtime_category=timeout` and `approx_prompt_tokens <= 3000`.
- `provider_runtime_timeout_uncalibrated`: timeout outside the two thresholds.
- Do not classify timeout as pass or as audit rule failure.

### Runtime Budget Config

Keep existing env vars working:

- `FUND_AGENT_LLM_TIMEOUT_SECONDS`
- `FUND_AGENT_LLM_TIMEOUT_MAX_ATTEMPTS`
- `FUND_AGENT_LLM_TIMEOUT_BACKOFF_SECONDS`
- `FUND_AGENT_LLM_MAX_OUTPUT_CHARS`

Add operation-specific optional env vars:

- `FUND_AGENT_LLM_WRITER_TIMEOUT_SECONDS`
- `FUND_AGENT_LLM_AUDITOR_TIMEOUT_SECONDS`
- `FUND_AGENT_LLM_REPAIR_TIMEOUT_SECONDS`

Rules:

- If operation-specific env var is absent, fall back to `FUND_AGENT_LLM_TIMEOUT_SECONDS`.
- Validation bounds remain `>0` and `<=300`.
- Timeout max attempts remains bounded by the current `1..3`.
- Backoff remains bounded by the current `0..30`.
- Provider adapter must pass the effective per-request timeout into `httpx.Client.post(..., timeout=effective_timeout)`.
- The adapter must record effective timeout, max attempts, backoff and budget kind in diagnostics.

Do not add provider fallback or non-timeout retry.

### Prompt Payload Compaction Contract

Add an explicit compact writer prompt payload mode for provider-backed LLM writing. The compact mode must:

- Preserve all ids and statuses needed by writer/auditor safety checks.
- Preserve every available anchor id and source location metadata.
- Preserve every fact `missing_reason`; do not convert a real missing fact into an available fact.
- Use minified JSON and compact field names only where the prompt still remains understandable.
- For large `value` payloads, replace raw value with a deterministic safe representation:
  - `value_kind`
  - `value_chars`
  - `value_summary` only if derived directly from the structured value without external inference.
  - `value_available_but_detail_compacted=true` when raw detail is omitted.
  - `compact_reason="prompt_budget_compaction"` when applicable.
- If no safe summary can be derived for a required fact, fail closed or keep exact value; do not silently drop it.
- Writer instructions must explicitly say: do not cite or infer omitted raw detail; only use provided compact summary fields and provided anchors.

Implementation should use compact mode only for the explicit `--use-llm` path unless tests and review accept making it the universal writer prompt mode. Deterministic analyze/checklist remain unchanged either way because they do not call provider-backed writer.

### State Machine

No accepted-report state changes:

- `orchestration_status=partial` remains partial.
- `final_assembly_status=incomplete` remains fail-closed.
- Missing config still exits `1` with empty stdout.
- Provider timeout still exits `1` unless all required chapters are accepted and final assembly succeeds.

Allowed diagnostic state additions:

- Chapter runtime rows may include `timeout_root_cause_hint`.
- CLI incomplete summary may include safe root-cause counts, but must not print full prompt/draft/response.

## Implementation Slices

### Slice 1: Safe Prompt-Cost Diagnostics

Goal: produce root-cause evidence before changing prompt shape.

Tasks:

1. Refactor writer prompt construction into named render fragments matching the required component buckets:
   - protocol
   - contract
   - must_answer
   - must_not_cover
   - required_output
   - facts
   - anchors
   - repair_context
2. Add safe cost calculation using the actual rendered fragment strings, not a second approximate representation.
3. Add fact and anchor cost rows using ids and char counts only.
4. Attach writer prompt-cost diagnostic to the writer LLM request so provider timeout exceptions can carry it even when no `ChapterWriteResult` exists.
5. Extend provider/runtime diagnostics and serializer to include safe cost breakdown for timeout rows.
6. Add tests proving diagnostics include chapter/operation, prompt chars, approx tokens, max output chars, component costs, fact rows and anchor rows.
7. Add tests proving diagnostics do not include prompt text, draft markdown, provider response body, raw audit response, API key, Authorization header, or provider request JSON.

Expected implementation details:

- Approx token heuristic remains `ceil((system_prompt_chars + user_prompt_chars) / 4)`.
- Existing total prompt char fields remain present.
- For auditor operations, record total prompt chars/tokens and operation/budget fields; writer component breakdown can be `null` or absent.
- Serializer output should be allowlisted. Do not serialize dataclass `__dict__` blindly.

### Slice 2: Chapter 2/6 Prompt-Cost Compaction

Goal: reduce extreme writer prompt cost while preserving chapter facts and safety semantics.

Tasks:

1. Add compact writer fact/anchor payload rendering behind an explicit prompt payload mode.
2. Route explicit `--use-llm` writer prompts through compact mode.
3. Keep prompt-only and unit tests able to inspect contract semantics without depending on huge raw values.
4. Add tests with oversized chapter 2 and chapter 6 fact values that assert:
   - total writer `user_prompt_chars` decreases materially.
   - `fact_id`, `source_field_id`, `status`, `missing_reason`, and `evidence_anchor_ids` remain present.
   - `anchor_id`, `section_id`, `table_id`, and row-locator presence remain present.
   - no compact payload asks the LLM to cite omitted raw detail.
   - required output markers and missing marker contracts are unchanged.
   - candidate facet boundary text remains present.
   - L1 / R=A+B-C evidence-nearby guidance remains present.
5. Add a fail-closed test for a required large fact that cannot be safely represented: implementation must either keep exact value or block before provider; it must not silently omit the value.

Expected acceptance target:

- Chapter 2 and chapter 6 writer prompt approx tokens should drop below the `large_writer_prompt_cost` threshold in local diagnostic tests using representative oversized values.
- If real chapter 2/6 still exceed the threshold after compaction, the implementation evidence must list the top fact/anchor cost rows from the safe diagnostic and stop for controller decision before additional semantic compaction.

### Slice 3: Operation-Specific Runtime Budget Calibration

Goal: distinguish writer, auditor and repair timeout budgets without adding unbounded retry or provider fallback.

Tasks:

1. Extend typed config with optional writer/auditor/repair timeout seconds.
2. Keep legacy timeout env var as the fallback.
3. Pass effective timeout per provider request:
   - initial writer: writer timeout.
   - regenerate writer with `ChapterRepairContext`: repair timeout.
   - auditor: auditor timeout.
4. Keep timeout retry count bounded by existing max attempts.
5. Keep retry limited to timeout exceptions only.
6. Record effective timeout seconds, max attempts, backoff, operation and budget kind in every provider attempt diagnostic.
7. Add tests for env parsing, fallback behavior, invalid bounds, and per-operation timeout passed to `httpx`.
8. Add tests proving non-timeout errors are not retried.

Initial recommended runtime-budget defaults:

- Keep `FUND_AGENT_LLM_TIMEOUT_SECONDS` default at `60.0` for backward compatibility.
- Keep `FUND_AGENT_LLM_TIMEOUT_MAX_ATTEMPTS` default at `2`.
- Keep `FUND_AGENT_LLM_TIMEOUT_BACKOFF_SECONDS` default at `1.0`.
- Do not change default `FUND_AGENT_LLM_MAX_OUTPUT_CHARS=12000` in the code in this slice. Treat it as a diagnostic variable first so prompt compaction and timeout budget effects can be separated.

Real-provider rerun matrix may use explicit env overrides in evidence, without printing values containing secrets:

- First rerun: compact prompt + existing timeout defaults to isolate prompt-cost effect.
- Second rerun only if first still small-prompt timeouts: set bounded operation-specific timeouts, e.g. writer/auditor/repair `120s`, max attempts still `2`, backoff `1s`.
- Optional controlled check: run with `FUND_AGENT_LLM_MAX_OUTPUT_CHARS=6000` only to test whether the `12000` instruction induces long writer latency. Do not change default based on this check unless evidence shows writer outputs stay safely under the smaller cap and audits still pass.

### Slice 4: Safe CLI / Service Diagnostic Evidence

Goal: make the real-provider smoke evidence self-contained and safe.

Tasks:

1. Extend service diagnostic JSON generation to include:
   - runtime diagnostic payload.
   - prompt-cost diagnostic payload.
   - chapter summary matrix.
   - final assembly status.
2. CLI incomplete message may include only compact scalar summaries:
   - first failed chapter.
   - operation.
   - timeout root-cause hint.
   - attempts.
   - elapsed max.
   - prompt chars/tokens.
   - max output chars.
3. Do not print prompt, draft, provider response, raw audit response, model request body, API key, Authorization header, or env values.
4. Add tests asserting stdout remains empty on incomplete `--use-llm` and stderr includes only safe scalar fields.

### Slice 5: Real Provider Smoke Rerun and Disposition

Goal: classify remaining blocker with same-source evidence.

Tasks:

1. Run the required local deterministic and missing-config validations.
2. Run real-provider smoke with configured provider without echoing secrets.
3. Emit service diagnostic JSON under a new reports directory.
4. Run secret leak scan over new report/evidence files.
5. Classify outcome:
   - PASS only if complete 0-7 report is produced, final assembly accepted, stdout contains report, and no deterministic fallback occurred.
   - If chapter 2/6 writer no longer timeout but chapter 1/3/5 small prompts still timeout, classify as `provider_runtime / endpoint blocker`.
   - If chapter 2/6 still timeout and safe cost rows show prompt remains large, keep blocker as `large_writer_prompt_cost` and stop for controller decision.
   - If timeout is gone but programmatic audit C2/L1 appears, stop and route to the relevant audit calibration gate; do not mix it into this runtime gate.

## Tests / Validation Commands and Expected Assertions

Required commands:

```bash
uv run ruff check .
uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q
uv run fund-analysis analyze 006597 --report-year 2024
uv run fund-analysis checklist 006597 --report-year 2024
uv run fund-analysis analyze 006597 --report-year 2024 --use-llm
```

Missing-config fail-closed check:

- Run `fund-analysis analyze 006597 --report-year 2024 --use-llm` with provider env intentionally absent.
- Expected: exit `1`, stdout empty, Service not called, clear missing provider config error, no deterministic fallback.

Real-provider smoke:

- Run only with configured provider env already present or supplied by controller.
- Do not echo env or command-expanded secrets.
- Expected for pass: exit `0`, complete report chapters `0-7`, final assembly accepted, no deterministic fallback.
- Expected for still-blocked: exit `1`, stdout empty, diagnostic JSON emitted, blocker classified by safe runtime/prompt-cost fields.

Service diagnostic JSON assertions:

- Contains `chapter_summary_matrix`, `runtime_diagnostics`, and prompt-cost diagnostic payload.
- Contains per chapter/operation `system_prompt_chars`, `user_prompt_chars`, `approx_prompt_tokens`, `max_output_chars`.
- Contains writer component costs and fact/anchor char rows.
- Contains provider attempts, elapsed ms, timeout seconds, max attempts, backoff, runtime category, and timeout root-cause hint.
- Does not contain keys or values for full prompt, draft markdown, raw provider response, raw audit response, provider request body, API key, Authorization header, or secret env values.

Secret leak scan:

- Scan new docs/reviews and reports artifacts.
- Findings containing words like `API key` only pass if they are constraint text, not secret values.
- Any actual `Bearer`, Authorization header, full prompt, full draft, raw provider response, or real key value is blocking.

Max output chars check:

- Verify diagnostics continue to record `max_output_chars`.
- If an optional `FUND_AGENT_LLM_MAX_OUTPUT_CHARS=6000` smoke is run, compare only safe scalar outcomes:
  - writer response chars if present.
  - timeout rate.
  - response incomplete / too long failures.
  - audit pass/fail.
- Do not change default `12000` unless the implementation evidence and reviews accept the lower cap as safe.

## Docs Decision

For the plan artifact only, no README or design update is required.

For implementation acceptance:

- Update `fund_agent/config/README.md` if new timeout env vars are added.
- Update `fund_agent/fund/README.md` if writer prompt payload compaction or prompt-cost diagnostic contracts become accepted current behavior.
- Update `docs/design.md` only after code/review acceptance, and label the behavior as current implementation facts.
- Update `docs/implementation-control.md` / `docs/current-startup-packet.md` only by controller after gate disposition.
- Do not update root `README.md` unless user-facing CLI behavior or configuration examples change.

## Review Gates

Plan review:

- At least two independent reviews unless controller records reviewer unavailability.
- Review must check safety boundaries, schema completeness, prompt-cost root-cause logic, and non-goals.

Implementation review:

- At least two independent code reviews.
- Review must verify:
  - no full prompt/draft/provider response/secret serialization.
  - no safety rule relaxation.
  - no deterministic fallback.
  - no Host/Agent/dayu introduction.
  - no golden/fixture/score/quality gate mutation.
  - retry remains bounded and timeout-only.
  - compact payload does not permit citing omitted facts.

Controller judgment:

- Must classify remaining real-provider blocker using same-source runtime/prompt-cost evidence.
- Must not mark PR #21 ready, push, merge, or release from this gate.

## Stop Conditions

Stop for controller decision if any of these occur:

- A blocking question emerges that affects schema, safety contract, file ownership, runtime budget defaults, or user-visible CLI behavior.
- Implementation requires full prompt, full draft, raw provider response, or secret logging to debug.
- Prompt compaction cannot preserve required fact semantics for chapter 2/6.
- A real-provider run exposes a non-timeout first blocker after timeout is handled, such as programmatic C2/L1 calibration.
- Small-prompt rows still time out after bounded operation-specific timeout calibration.
- Secret leak scan finds actual secret or raw prompt/draft/provider/audit content.
- Deterministic analyze/checklist behavior changes.
- Any change would enter Host/Agent/dayu, score-loop implementation, golden/fixture promotion, quality gate semantics, PR state, push, merge, or release.

## Risks / Open Questions

Non-blocking risks:

- Live provider outcomes may vary between runs; use service diagnostic JSON from the same run as the root-cause source, not cross-run inference.
- Compact summaries can accidentally become lossy. Mitigation: tests must prove ids, statuses, missing reasons and anchor ids remain present, and no omitted raw detail can be cited.
- Increasing timeout budget may turn a fast fail into a long fail. Mitigation: max attempts remains bounded, no infinite retry, and small-prompt persistent timeout is classified as endpoint blocker.
- Lowering `max_output_chars` could induce `response_too_long` or incomplete outputs. Mitigation: do not change the default in code until controlled evidence supports it.
- Existing workspace is dirty with many unrelated accepted/untracked artifacts. Implementation must stage only this gate's files and must not clean unrelated files.

Blocking Questions For Controller:

- None. The plan is handoff-ready under the working assumptions above.

## Completion Report Format

Implementation evidence must report:

- Changed files grouped by slice.
- New/changed diagnostic schema versions.
- Prompt-cost before/after table for chapters 1-6, including component costs for writer rows.
- Runtime budget table by operation: timeout seconds, max attempts, backoff, observed attempts, max elapsed ms.
- Real-provider outcome:
  - exit code.
  - stdout empty/non-empty.
  - orchestration status.
  - final assembly status.
  - generated/skipped/accepted chapter ids.
  - first failed chapter/operation/category/subcategory/root-cause hint.
- Validation command results for all required commands.
- Secret leak scan result and any allowlisted wording matches.
- Explicit non-goal confirmation:
  - no Host/Agent/dayu.
  - no deterministic fallback.
  - no golden/fixtures/score/quality/final judgment/promotion changes.
  - no PR/push/merge/release action.

## Handoff Status

Handoff-ready: yes.
