# Code Review: MVP Provider Runtime Budget and Prompt-Cost Root-Cause Calibration — MiMo

- Gate: `MVP provider runtime budget and prompt-cost root-cause calibration gate`
- Role: Gateflow code review worker MiMo, not implementation worker
- Date: 2026-05-31
- Verdict: **PASS**

## Review Scope

Read:
- `AGENTS.md`
- `docs/reviews/mvp-provider-runtime-budget-prompt-cost-root-cause-calibration-plan-20260531.md`
- `docs/reviews/mvp-provider-runtime-budget-prompt-cost-root-cause-calibration-plan-review-mimo-20260531.md`
- `docs/reviews/mvp-provider-runtime-budget-prompt-cost-root-cause-calibration-plan-review-ds-20260531.md`
- `docs/reviews/mvp-provider-runtime-budget-prompt-cost-root-cause-calibration-implementation-evidence-20260531.md`
- `fund_agent/fund/chapter_writer.py`
- `fund_agent/services/llm_provider.py`
- `fund_agent/services/chapter_orchestrator.py`
- `fund_agent/config/llm.py`
- `fund_agent/ui/cli.py`
- `fund_agent/config/README.md`
- `fund_agent/fund/README.md`
- `tests/README.md`
- `tests/fund/test_chapter_writer.py`
- `tests/services/test_llm_provider.py`
- `tests/services/test_chapter_orchestrator.py`
- `tests/config/test_llm_config.py`
- `tests/ui/test_cli.py`

## Blocking Findings

None.

## Findings by Criterion

### 1. Safe prompt-cost diagnostic — PASS

`ChapterPromptCostDiagnostic` (`chapter_writer.py:224-243`) stores only char counts, scalar metadata, and id-typed rows. `ChapterPromptFactCostRow` (`chapter_writer.py:176-199`) stores `fact_id`, `source_field_id`, `status`, `missing_reason`, `value_chars`, `serialized_fact_chars`, counts — no fact value text. `ChapterPromptAnchorCostRow` (`chapter_writer.py:201-221`) stores `anchor_id`, `source_kind`, `document_year`, `section_id`, `table_id`, `row_locator_present`, `serialized_anchor_chars` — no anchor note text.

The allowlisted serializer in `chapter_orchestrator.py:2898-3008` (`_prompt_cost_diagnostic_payload`, `_prompt_component_cost_payload`, `_prompt_fact_cost_payload`, `_prompt_anchor_cost_payload`) uses explicit `getattr` field extraction, not `__dict__` serialization. No prompt text, draft markdown, provider response, raw audit response, API key, or Authorization header enters the diagnostic payload.

`llm_provider.py:816-846` (`_sanitize_text`) redacts `Authorization`, `Bearer`, `FUND_AGENT_LLM_API_KEY`, `api_key`, `sk-`, `prompt`, `writer user`, `draft markdown` from diagnostic messages. Tests at `test_llm_provider.py:231-235` and `test_chapter_writer.py:329-333` verify secret/prompt absence in `repr(diagnostic)`.

### 2. Compact payload preserves required semantics — PASS

`_prompt_fact_row` (`chapter_writer.py:1623-1654`) in compact mode replaces large values with `_compact_value_payload` but preserves `fact_id`, `source_field_id`, `source_field_name`, `status`, `evidence_anchor_ids`, `missing_reason`, `required_by`. The `_compact_payload_protocol` (`chapter_writer.py:1039-1057`) explicitly instructs the LLM: "不得引用、复述或推断被省略的 raw detail" when `value_available_but_detail_compacted=true`.

`_prompt_anchor_row` (`chapter_writer.py:1681-1709`) in compact mode omits `note` but preserves `anchor_id`, `source_kind`, `document_year`, `section_id`, `table_id`, `row_locator`. Test `test_compact_prompt_payload_preserves_fact_and_anchor_contract` (`test_chapter_writer.py:258-301`) verifies: fact_id, source_field_id, status, evidence_anchor_ids, value_available_but_detail_compacted, prompt_budget_compaction, section_id, table_id, row_locator, L1 rule, required_output markers, and candidate facet boundary all remain present.

No anchors/ITEM_RULE/candidate facet/audit relaxation detected. `_preflight_issues` and all marker/structure/forbidden-phrase checks remain unchanged.

### 3. value_summary deterministic, no inference — PASS

`_value_summary` (`chapter_writer.py:1844-1883`) extracts only: top-level scalar field names/values, list lengths, nested dict key names. No natural language inference, no semantic summarization, no truncation heuristics. For non-dict/list/scalar values, returns `{"summary_available": False}`. This matches plan review DS advisory N2 recommendation exactly.

### 4. Timeout budget bounded, timeout-only retry, diagnostics recorded — PASS

`llm_provider.py:617-666` (`_effective_timeout_seconds`, `_timeout_budget_kind`) selects effective timeout by operation: auditor → `auditor_timeout_seconds`, repair attempt > 0 → `repair_timeout_seconds`, else → `writer_timeout_seconds`. Budget kind: `"auditor"`, `"writer_repair"`, `"writer_initial"`.

Retry loop (`llm_provider.py:259-419`) only retries on `httpx.TimeoutException`. Non-timeout errors (`httpx.TransportError`, 429, non-2xx, malformed) raise immediately without retry — verified by tests `test_http_errors_do_not_retry` (line 283), `test_network_error_does_not_retry` (line 307), `test_malformed_response_does_not_retry` (line 332).

Every diagnostic records `timeout_seconds`, `timeout_max_attempts`, `timeout_backoff_seconds`, `timeout_budget_kind`, `repair_timeout_fallback_used` — see `_provider_diagnostic` (`llm_provider.py:706-773`). Test `test_timeout_retry_exhausted_carries_provider_diagnostics` (line 187) verifies all fields. Test `test_operation_specific_timeout_is_passed_to_httpx` (line 349) verifies per-operation timeout reaches httpx. Test `test_repair_timeout_fallback_is_recorded_in_timeout_diagnostic` (line 383) verifies fallback decision.

Config (`llm.py:45-77`) validates bounds: timeout `(0, 300]`, max_attempts `[1, 3]`, backoff `[0, 30]`. Tests `test_llm_config.py:88-205` cover all bounds and fallback chains.

### 5. Root-cause hint classification correct — PASS

`_timeout_root_cause_hint` (`chapter_orchestrator.py:2694-2730`):
- `operation == "writer"` and `approx_tokens >= 8000` → `large_writer_prompt_cost`
- `approx_tokens <= 3000` → `small_prompt_provider_timeout`
- else → `provider_runtime_timeout_uncalibrated`
- Non-timeout → `non_timeout_provider_runtime`
- No provider category → `None`

Auditor can only produce `small_prompt_provider_timeout` (when tokens ≤ 3000) or `provider_runtime_timeout_uncalibrated` (when tokens in 3000-8000 gap). Auditor never produces `large_writer_prompt_cost` because the first branch requires `operation == "writer"`. This correctly addresses plan review DS advisory N1.

### 6. Deterministic analyze/checklist default unchanged — PASS

Compact mode is only activated via `--use-llm` path in CLI (`cli.py:803-806`: `prompt_payload_mode="compact"`). `build_chapter_writer_input` defaults to `prompt_payload_mode="full"` (`chapter_writer.py:487`). Deterministic `analyze` and `checklist` paths do not call writer at all. No behavioral change to deterministic paths detected.

### 7. Final assembly fail-closed unchanged — PASS

`_llm_incomplete_message` (`cli.py:810-836`) still triggers on `report_markdown is None`, prints safe scalar diagnostics, and exits 1. No partial report acceptance, no deterministic fallback introduced. `orchestration_status=partial` remains partial; `final_assembly_status=incomplete` remains fail-closed.

### 8. Tests sufficient — PASS

- `test_chapter_writer.py`: compact payload contract, prompt-cost diagnostic safety, all existing writer tests unchanged
- `test_llm_provider.py`: operation-specific timeout passthrough, timeout-only retry, non-timeout no-retry, repair timeout fallback, auditor prompt cost
- `test_chapter_orchestrator.py`: (partial read) covers runtime diagnostic serialization, timeout root-cause hint, prompt_payload_mode plumbing
- `test_llm_config.py`: operation-specific timeout env parsing, fallback chain, bounds, repair timeout fallback
- `test_cli.py`: (partial read) covers `_llm_incomplete_message`, `_first_failed_runtime_summary`, `_chapter_matrix_summary`, use-llm config flow

Implementation evidence reports 225 tests passing.

### 9. Prohibited scope not touched — PASS

- No Host/Agent/dayu code introduced
- No golden/fixtures/extraction score/quality gate changes
- No PR/push/merge/release action
- No deterministic fallback added
- No `docs/design.md` or `AGENTS.md` modified
- No `chapter_auditor.py` modified (plan allowed conditional; not needed)

## Non-blocking Residuals

1. **Real chapter 2/6 prompt size after compact mode.** Implementation evidence notes this needs live provider smoke to confirm whether compact tokens fall below `large_writer_prompt_cost` threshold. Local tests verify structural compaction but not actual production fact volumes.

2. **3000-8000 token gap.** No current chapter falls in the `provider_runtime_timeout_uncalibrated` range. If a future chapter lands there, controller should re-evaluate thresholds.

3. **Compact value threshold.** `_COMPACT_VALUE_CHAR_THRESHOLD` is 1200 chars. For facts with values between 1200-8000 chars that are required, the compact representation is used. If the LLM cannot work with the compact summary for a specific required fact, the next gate should stop for semantic compaction or tool-based lookup rather than relaxing evidence rules. This is correctly documented as a residual risk in the implementation evidence.

## Review Scope

Files read: all scope files listed above plus plan, plan reviews (MiMo/DS), implementation evidence, and `AGENTS.md`. Cross-referenced: prompt-cost diagnostic schema against plan contract, timeout budget config against plan env vars, root-cause hint classification against plan threshold rules, compact payload fields against plan safety invariants, allowlisted serializer output against plan diagnostic schema.
