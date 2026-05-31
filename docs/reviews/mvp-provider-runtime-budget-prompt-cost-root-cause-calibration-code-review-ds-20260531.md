# Code Review: MVP Provider Runtime Budget and Prompt-Cost Root-Cause Calibration — AgentDS

- Gate: `MVP provider runtime budget and prompt-cost root-cause calibration gate`
- Role: Gateflow code review worker AgentDS, not implementation worker, not controller
- Date: 2026-05-31
- Verdict: **PASS**

## Review Scope

Read all scope files:
- Plan and plan reviews (DS, MiMo)
- Implementation evidence
- MiMo code review (`code-review-mimo-20260531.md`)
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
- `AGENTS.md`

## Blocking Findings

None.

## Findings by Criterion

### 1. Safe prompt-cost diagnostic (no full prompt/draft/provider response/secret) — PASS

`ChapterPromptCostDiagnostic` (`chapter_writer.py:224-243`) stores only char counts, scalar metadata, and id-typed rows. `ChapterPromptFactCostRow` (`chapter_writer.py:176-199`) stores `fact_id`, `source_field_id`, `status`, `missing_reason`, `value_chars`, `serialized_fact_chars`, counts — no fact value text. `ChapterPromptAnchorCostRow` (`chapter_writer.py:201-221`) stores `anchor_id`, `source_kind`, `document_year`, `section_id`, `table_id`, `row_locator_present`, `serialized_anchor_chars` — no anchor note text.

The allowlisted serializer in `chapter_orchestrator.py:2898-3008` uses explicit `getattr` field extraction, not `__dict__` serialization. No prompt text, draft markdown, provider response, raw audit response, API key, or Authorization header enters diagnostic payload.

`_sanitize_text` in `llm_provider.py:816-846` redacts `Authorization`, `Bearer`, `FUND_AGENT_LLM_API_KEY`, `api_key`, `sk-`, `prompt`, `writer user`, `draft markdown` from diagnostic messages. Tests at `test_llm_provider.py:231-235` and `test_chapter_writer.py:329-333` verify secret/prompt absence in `repr(diagnostic)`.

**Minor observation:** `_sanitize_text` in `chapter_orchestrator.py:2185-2204` has a smaller sensitive-word list than `llm_provider.py:816-846` — lacks `"writer user"` and `"draft markdown"`. The orchestrator version is used for repair context messages only, not for prompt-bearing diagnostics, so no actual leak risk. Still worth noting as a consistency gap for future maintenance.

### 2. Compact payload preserves required semantics (no relaxation of anchors/ITEM_RULE/candidate/audit) — PASS

`_prompt_fact_row` (`chapter_writer.py:1623-1654`) in compact mode replaces large values with `_compact_value_payload` but preserves `fact_id`, `source_field_id`, `source_field_name`, `status`, `evidence_anchor_ids`, `missing_reason`, `required_by`. `_prompt_anchor_row` (`chapter_writer.py:1681-1709`) in compact mode omits `note` but preserves `anchor_id`, `source_kind`, `document_year`, `section_id`, `table_id`, `row_locator`.

`_compact_payload_protocol` (`chapter_writer.py:1039-1057`) explicitly instructs LLM: "不得引用、复述或推断被省略的 raw detail" when `value_available_but_detail_compacted=true`.

Test `test_compact_prompt_payload_preserves_fact_and_anchor_contract` (`test_chapter_writer.py:258-301`) verifies all required identifiers and constraints remain present.

No anchor/ITEM_RULE/candidate facet/audit relaxation detected. All existing `_preflight_issues`, marker parsing, structure checks, and forbidden phrase checks remain unchanged.

### 3. value_summary deterministic and without inference — PASS

`_value_summary` (`chapter_writer.py:1844-1883`) extracts only: top-level scalar field names/values, list lengths, nested dict key names. No natural language inference, no semantic summarization, no truncation heuristics. For non-dict/list/scalar values, returns `{"summary_available": False}`.

This matches plan review DS advisory finding N2 recommendation exactly.

### 4. Timeout budget bounded, timeout-only retry, diagnostics recorded — PASS

`_effective_timeout_seconds` (`llm_provider.py:617-666`) selects effective timeout: auditor → `auditor_timeout_seconds`, repair attempt > 0 → `repair_timeout_seconds`, else → `writer_timeout_seconds`. Budget kind: `"auditor"`, `"writer_repair"`, `"writer_initial"`.

Retry loop (`llm_provider.py:259-419`) only retries on `httpx.TimeoutException`. Non-timeout errors (`httpx.TransportError`, 429, non-2xx, malformed) raise immediately without retry. Tests `test_http_errors_do_not_retry` (line 283), `test_network_error_does_not_retry` (line 307), `test_malformed_response_does_not_retry` (line 332) confirm.

Every diagnostic records `timeout_seconds`, `timeout_max_attempts`, `timeout_backoff_seconds`, `timeout_budget_kind`, `repair_timeout_fallback_used`. Config validates bounds: timeout `(0, 300]`, max_attempts `[1, 3]`, backoff `[0, 30]`.

### 5. Root-cause hint classification correct (auditor never produces large) — PASS

`_timeout_root_cause_hint` (`chapter_orchestrator.py:2694-2730`):
- `operation == "writer"` and `approx_tokens >= 8000` → `large_writer_prompt_cost`
- `approx_tokens <= 3000` → `small_prompt_provider_timeout`
- else → `provider_runtime_timeout_uncalibrated`
- Non-timeout → `non_timeout_provider_runtime`
- No provider category → `None`

Auditor can only produce `small_prompt_provider_timeout` (tokens ≤ 3000) or `provider_runtime_timeout_uncalibrated` (tokens in 3000–8000 gap). Auditor never produces `large_writer_prompt_cost` because the first branch requires `operation == "writer"`.

Test `test_runtime_root_cause_hint_never_marks_auditor_as_large_prompt_cost` (`test_chapter_orchestrator.py:1161-1205`) verifies auditor with ~10003 tokens at timeout → `provider_runtime_timeout_uncalibrated`, not `large_writer_prompt_cost`.

### 6. Deterministic analyze/checklist default unchanged; explicit --use-llm only compact — PASS

Compact mode is only activated via `--use-llm` path in CLI (`cli.py:803-806`: `prompt_payload_mode="compact"`). `build_chapter_writer_input` defaults to `prompt_payload_mode="full"` (`chapter_writer.py:487`). Deterministic `analyze` and `checklist` paths do not call writer at all. No behavioral change to deterministic paths.

### 7. Final assembly fail-closed unchanged — PASS

`_llm_incomplete_message` (`cli.py:810-836`) triggers on `report_markdown is None`, prints safe scalar diagnostics, exits 1. No partial report acceptance, no deterministic fallback introduced. `orchestration_status=partial` remains partial; `final_assembly_status=incomplete` remains fail-closed.

### 8. Tests sufficient — PASS

All 5 test files have targeted tests for the new behavior:
- `test_chapter_writer.py`: compact payload contract preservation, prompt-cost diagnostic safety and component structure, all existing writer tests unchanged
- `test_llm_provider.py`: operation-specific timeout passthrough (`test_operation_specific_timeout_is_passed_to_httpx`), timeout-only retry (`test_timeout_only_retry_succeeds_on_later_attempt`), non-timeout no-retry, repair timeout fallback (`test_repair_timeout_fallback_is_recorded_in_timeout_diagnostic`), auditor prompt cost diagnostic safety
- `test_chapter_orchestrator.py`: runtime diagnostic serialization safety, timeout root-cause hint classification, auditor never large, prompt_payload_mode plumbing, L1 repair context
- `test_llm_config.py`: operation-specific timeout env parsing, fallback chain, bounds, repair timeout fallback with `repair_timeout_fallback_used` flag
- `test_cli.py`: `_llm_incomplete_message` fail-closed, `_first_failed_runtime_summary` safe scalars, `_chapter_matrix_summary`, use-llm config flow (`prompt_payload_mode="compact"` plumbing)

Implementation evidence reports 225 tests passing, ruff `All checks passed!`.

### 9. Prohibited scope not touched — PASS

- No Host/Agent/dayu code introduced
- No golden/fixtures/extraction score/quality gate changes
- No PR/push/merge/release action
- No deterministic fallback added
- No `docs/design.md` or `AGENTS.md` modified
- No `chapter_auditor.py` modified (plan allowed conditional; not needed — implementation evidence correctly reports this)
- No `FundDocumentRepository`, PDF cache, source helper, or downloader touched

## Non-blocking Residuals

1. **`_sanitize_text` inconsistency between `llm_provider.py` and `chapter_orchestrator.py`.** The provider version (`llm_provider.py:816-846`) redacts `"writer user"` and `"draft markdown"`; the orchestrator version (`chapter_orchestrator.py:2185-2204`) does not. The orchestrator version is only used for repair context messages (audit issue messages, not prompt-bearing text), so no actual leak risk. However, if a future maintainer reuses the orchestrator `_sanitize_text` for diagnostic messages that may contain prompt components, the narrower list would miss these two patterns. Recommended to align the two lists in a follow-up pass.

2. **Real chapter 2/6 prompt size after compact mode unconfirmed.** Local tests verify structural compaction but actual production fact volumes may differ. This needs a live provider smoke with service diagnostic JSON — correctly documented as a residual risk in implementation evidence.

3. **3000–8000 token classification gap.** No current chapter falls in the `provider_runtime_timeout_uncalibrated` range. If a future chapter lands there, controlled re-evaluation of thresholds is needed.

4. **`_COMPACT_VALUE_CHAR_THRESHOLD` = 1200.** For required facts with values between 1200–~8000 chars that are compacted, the LLM must work with compact summaries only. If the LLM cannot produce adequate chapters for a specific required fact under compact representation, the next gate should stop for tool-based fact lookup, not relax evidence rules. Correctly documented as a risk.

## Review Scope

All 13 review scope files listed above, plus AGENTS.md, plan, plan reviews, MiMo code review. Cross-referenced: prompt-cost diagnostic schema against plan contract, timeout budget config against plan env vars, root-cause hint classification against plan threshold rules, compact payload fields against plan safety invariants, allowlisted serializer output against plan diagnostic schema.
