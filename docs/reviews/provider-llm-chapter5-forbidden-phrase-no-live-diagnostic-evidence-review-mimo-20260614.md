# Provider/LLM Chapter 5 Forbidden-phrase No-live Diagnostic Evidence Review (MiMo)

Date: 2026-06-14

Reviewer: AgentMiMo

Gate: `Provider/LLM Chapter 5 Forbidden-phrase No-live Diagnostic Evidence Gate`

Artifact under review: `docs/reviews/provider-llm-chapter5-forbidden-phrase-no-live-diagnostic-evidence-20260614.md`

Verdict: `PASS_WITH_FINDINGS`

## 1. Review Questions

### Q1. Are H1-H5 dispositions supported by direct no-live evidence and safe metadata?

**PASS.**

| Hypothesis | Disposition | Evidence check |
|---|---|---|
| H1 prompt contract omission | `DEFER_AS_PARTIAL` | Writer system prompt at `chapter_writer.py:617-620` shows broad global prohibition. No Chapter 5-specific forbidden-phrase remediation found in prompt assembly at `chapter_writer.py:682-708` and `1458-1480`. Worker correctly notes raw prompt bodies were intentionally not read, so the label `DEFER_AS_PARTIAL` is precise: the evidence gap is acknowledged, not hidden. |
| H2 LLM noncompliance caught by writer | `ACCEPT` | Runtime attempt 1 has `writer_status=blocked`, `writer_stop_reason=llm_contract_violation`, `writer:forbidden_phrase=1`, provider attempt count `0`. Writer code blocks `_FORBIDDEN_PHRASES` match at `chapter_writer.py:1939-1960`. No-live test `test_writer_rejects_forbidden_trading_advice` (line 1120) confirms `建议买入。` blocks. Direct evidence supports acceptance. |
| H3 audit repair context gap | `ACCEPT` | Attempt 0 repair decision issue id is `llm:parse_failure` (controller judgment accepted facts). Repair context mapping at `repair.py:277-340` maps to auditor line-protocol correction, not forbidden-phrase removal. No forbidden-phrase-specific branch exists. Writer renders supplied issue ids/messages/corrections only at `chapter_writer.py:1458-1480`. Direct code evidence supports acceptance. |
| H4 taxonomy mismatch | `ACCEPT_AS_DIAGNOSTIC_LAYERING` | Runtime first failed category `audit_parse` vs prompt diagnostic `writer_parse`/`forbidden_phrase`. Service mapping at `chapter_orchestrator.py:1395-1412` and `1360-1392`, `1422-1483` confirmed. Chapter 5 runtime rows show attempt 0 auditor `audit_parse` and attempt 1 writer `prompt_contract`. Direct code and metadata evidence supports acceptance as layering issue. |
| H5 repair budget makes second attempt terminal | `ACCEPT_CURRENT_BEHAVIOR` | Default `max_repair_attempts=1` at `chapter_orchestrator.py:336-350`. Writer-block terminal at `runner.py:380-420` excludes forbidden phrase from special retry path. Tests `test_repair_budget_exhausted_stops_without_hidden_retry` (line 84) and `test_repair_budget_exhausted_records_each_regenerate_attempt` (line 489) confirm behavior. Direct code and test evidence supports acceptance. |

All five dispositions are anchored to direct no-live source code evidence, safe runtime metadata, and targeted test results. No disposition relies on indirect evidence or live/provider claims.

### Q2. Is the conclusion ready for no-live fix planning, not immediate implementation?

**PASS.**

The verdict is `VERDICT: DIAGNOSTIC_EVIDENCE_READY_FOR_NO_LIVE_FIX_PLANNING_NOT_READY`. Section 7 conclusion explicitly says "Recommended next entry: narrow no-live fix planning gate" and lists three possible fix directions (forbidden-phrase-specific repair context/prompt guidance, diagnostic lineage normalization, or both) while preserving `NOT_READY`. No implementation is authorized.

### Q3. Did the worker stay inside no-live/no-source-change/no-live-command boundaries?

**PASS.**

- No live/provider/LLM/network/PDF/FDR/source/analyze/checklist/golden/readiness/release commands were executed.
- No source/test/runtime behavior changes were made.
- No staging, commit, push, PR actions.
- No raw bodies, raw prompts, provider payloads, source/PDF/cache bodies, final report bodies or report Markdown were read.
- `docs/design.md` was not read (explicitly documented as constrained by handoff).
- Only allowed commands: `sed`/`grep` over cited source/test paths, `jq` safe scalar extraction from summary/chapter-05 JSON, `git diff --check`, `git status --short`, and targeted pytest.
- Section 8 verification records confirm `git diff --check` passed and targeted pytest `11 passed in 0.46s`.

### Q4. Are repair context, taxonomy and budget findings precise enough for a code-generation-ready fix plan gate?

**PASS.**

| Finding | Precision |
|---|---|
| Repair context gap | Exact code path: `repair.py:277-340` has no forbidden-phrase-specific branch; `repair.py:338-340` maps `llm:parse_failure` to auditor line-protocol correction. `chapter_writer.py:1458-1480` renders only supplied issue ids/messages/corrections. |
| Taxonomy mismatch | Exact mapping chain: `chapter_orchestrator.py:1395-1412` maps `llm:parse_failure` to `audit_parse`; `chapter_orchestrator.py:1360-1392` maps writer `llm_contract_violation` to `prompt_contract`; `chapter_orchestrator.py:1422-1483` counts `writer:forbidden_phrase` as `forbidden_phrase` subcategory. |
| Budget semantics | Exact default: `chapter_orchestrator.py:336-350` declares `max_repair_attempts=1`. Runner terminal: `runner.py:380-420` returns writer-block unless special invalid-anchor retry path. Budget exhaustion: `repair.py:61-145` stops when `remaining_budget <= 0`. |
| Writer validation | Exact validation chain: `chapter_writer.py:1612-1645` includes `_forbidden_phrase_issues` in blocking chain; `chapter_writer.py:1939-1960` emits `writer:forbidden_phrase:<index>` with `llm_contract_violation`. |

All findings include exact file paths and line ranges. A fix-plan gate has sufficient precision to scope code changes.

### Q5. Are any claims overread from raw bodies, provider, source policy, readiness or live stability?

**PASS.**

- H1 is correctly labeled `DEFER_AS_PARTIAL` with explicit acknowledgment that raw prompt bodies were not read.
- No provider response classification claims are made; provider attempt count `0` is correctly cited.
- No readiness, release, or live stability claims are made.
- The diagnostic consistency finding is presented as "taxonomy lineage mismatch requiring planning, not readiness evidence."
- The conclusion explicitly states "not evidence of source acquisition, provider runtime, or readiness state."

## 2. Safe Metadata Cross-check

Verified all section 3 safe scalar values against actual JSON:

| Claim in artifact | Actual JSON value | Match |
|---|---|---|
| `summary schema_version` = `llm_incomplete_run_summary.v1` | `.schema_version` = `llm_incomplete_run_summary.v1` | OK |
| `run_id` = `host_run_8c795cd1469b44d3` | `.run_id` = `host_run_8c795cd1469b44d3` | OK |
| `orchestration` = `partial` | `.orchestration_status` = `partial` | OK |
| `final_assembly` = `incomplete` | `.final_assembly_status` = `incomplete` | OK |
| `redaction_applied` = `true`, count `1` | `.redaction_applied` = `true`, `.redaction_count` = `1` | OK |
| Chapter 5 `status=blocked` | `.first_failed.status` = `blocked` | OK |
| Chapter 5 `stop_reason=llm_contract_violation` | `.first_failed.stop_reason` = `llm_contract_violation` | OK |
| Chapter 5 `failure_category=audit_parse` | `.first_failed.failure_category` = `audit_parse` | OK |
| Chapter 5 `failure_subcategory=forbidden_phrase` | `.first_failed.failure_subcategory` = `forbidden_phrase` | OK |
| Chapter 5 `attempt_count=2` | `.first_failed.attempt_count` = `2` | OK |
| Prompt diagnostic `phase=writer_parse`, `attempt_index=1` | `.prompt_contract_diagnostics.first_failed.phase` = `writer_parse`, `.attempt_index` = `1` | OK |
| `forbidden_phrase_count=1`, `issue_reason_counts.llm_contract_violation=1` | Chapter 5 phase entry: `forbidden_phrase_count=1`, `issue_reason_counts.llm_contract_violation=1` | OK |
| `max_output_chars=12000`, `response_chars=2322` | Chapter 5 phase entry: `max_output_chars=12000`, `response_chars=2322` | OK |
| `provider_attempt_count=0`, `provider_runtime_categories=[]` | `.runtime_diagnostics.first_failed.provider_attempt_count` = `0`, `.provider_runtime_categories` = `[]` | OK |
| `diagnostic_consistency=consistent` | `.diagnostic_consistency_status` = `consistent` (chapter-level) | OK |
| Chapter 5 top-level issue `5:llm_contract_violation:writer:forbidden_phrase:7` | `.issues` = `["5:llm_contract_violation:writer:forbidden_phrase:7"]` | OK |

## 3. Source Code Reference Cross-check

Verified all cited source code line references:

| Cited reference | Verified |
|---|---|
| `chapter_writer.py:97-110` `_FORBIDDEN_PHRASES` | OK - contains `建议买入`, `可以买入`, `立即买入`, `建议卖出` etc. |
| `chapter_writer.py:617-620` system prompt broad policy | OK - `不得输出买入/卖出/仓位/收益预测` |
| `chapter_writer.py:1939-1960` `_forbidden_phrase_issues` | OK - function exists at line 1939 |
| `chapter_auditor.py:66-76` auditor `_FORBIDDEN_PHRASES` | OK - same forbidden phrases |
| `chapter_auditor.py:1277-1280` programmatic audit C1 | OK - `_program_issue("C1", ...)` with `repair_hint="regenerate"` |
| `repair.py:61-145` repair decision | OK - `decide_repair()` function at line 61 |
| `repair.py:277-340` correction mapping, no forbidden-phrase branch | OK - `llm:parse_failure` branch at line 62, no `forbidden_phrase` branch found |
| `chapter_orchestrator.py:336-350` `max_repair_attempts=1` | OK - docstring confirms default |
| `runner.py:380-420` writer-block terminal | OK |

## 4. Test Node ID Cross-check

All 11 test node IDs verified against actual test file definitions:

| Test node ID | File line | OK |
|---|---|---|
| `test_writer_rejects_forbidden_trading_advice` | `test_chapter_writer.py:1120` | OK |
| `test_programmatic_audit_fails_forbidden_trading_advice` | `test_chapter_auditor.py:207` | OK |
| `test_llm_audit_parse_failure_is_blocked` | `test_chapter_auditor.py:1071` | OK |
| `test_repair_budget_exhausted_stops_without_hidden_retry` | `test_repair_policy.py:84` | OK |
| `test_repair_context_records_issue_ids_and_sanitized_messages` | `test_repair_policy.py:118` | OK |
| `test_repair_budget_exhausted_records_each_regenerate_attempt` | `test_runner.py:489` | OK |
| `test_chapter_6_invalid_anchor_marker_twice_fails_closed_after_one_retry` | `test_runner.py:553` | OK |
| `test_writer_forbidden_phrase_subcategory_remains_blocked` | `test_chapter_orchestrator.py:745` | OK |
| `test_programmatic_forbidden_phrase_is_counted_not_accepted` | `test_chapter_orchestrator.py:833` | OK |
| `test_audit_parse_failure_records_audit_parse_diagnostic` | `test_chapter_orchestrator.py:1488` | OK |
| `test_repair_budget_exhausted_returns_failed_stop_reason` | `test_chapter_orchestrator.py:1946` | OK |

## 5. Findings

### F1. First pytest command had incorrect test node IDs (acceptable)

The artifact documents that the first attempted command used two incorrect test node IDs and exited with pytest collection error. The worker correctly excluded this from behavioral evidence and re-ran with correct nodes. This is transparent and appropriate.

### F2. Section 3 table uses descriptive labels, not literal JSON paths (acceptable)

The section 3 safe metadata table uses descriptive labels like "prompt diagnostic first failed" and "runtime diagnostic first failed" rather than literal `jq` paths. All scalar values were verified correct against actual JSON. The descriptive format is acceptable for a diagnostic evidence artifact.

### F3. `diagnostic_consistency` label (acceptable)

The artifact uses `diagnostic consistency consistent` while the actual JSON key is `diagnostic_consistency_status`. The value `consistent` is correct. This is a label abbreviation, not a factual error.

## 6. Overall Verdict

```text
VERDICT: PASS_WITH_FINDINGS
```

All five review questions pass. H1-H5 dispositions are supported by direct no-live evidence and safe metadata. The conclusion correctly routes to no-live fix planning without authorizing implementation. The worker stayed inside all no-live/no-source-change boundaries. Repair context, taxonomy and budget findings are precise enough for a code-generation-ready fix plan gate. No claims are overread from raw bodies, provider, source policy, readiness or live stability.

Three non-blocking findings are noted: first pytest command node ID error (transparently documented), descriptive labels in safe metadata table (values verified correct), and `diagnostic_consistency` label abbreviation (value correct).

The artifact is accepted for controller judgment routing to the next gate.
