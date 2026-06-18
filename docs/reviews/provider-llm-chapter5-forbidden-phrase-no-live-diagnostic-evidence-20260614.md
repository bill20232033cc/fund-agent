# Provider/LLM Chapter 5 Forbidden-phrase No-live Diagnostic Evidence

Date: 2026-06-14

Role: AgentCodex no-live diagnostic evidence worker, not controller, not implementation.

Gate: `Provider/LLM Chapter 5 Forbidden-phrase No-live Diagnostic Evidence Gate`

Verdict: `VERDICT: DIAGNOSTIC_EVIDENCE_READY_FOR_NO_LIVE_FIX_PLANNING_NOT_READY`

Release/readiness: `NOT_READY`

## 1. Scope And Boundaries

This artifact collects deterministic no-live evidence for Chapter 5 `forbidden_phrase` after the accepted disposition checkpoint `746ff7e`.

It does not authorize implementation, live/provider/LLM/network/PDF/FDR/source/acquisition/analyze/checklist/golden/readiness/release/PR commands, source-policy changes, provider-default changes, annual-period LLM route changes, or repair-budget changes.

No source, test, runtime, prompt, report, Markdown body, provider payload, source/PDF/cache body, final report body, staging, commit, push, PR or readiness action was performed.

`docs/design.md` was not read in this worker run because the handoff constrained required reads and source/test reads for a no-live evidence artifact; no design or control state is changed here.

## 2. Required Control Evidence

| Evidence | Direct finding |
|---|---|
| `AGENTS.md:13-21` | LLM path is explicit opt-in and fail-closed; audit mechanism status is controlled by design/control docs. |
| `AGENTS.md:67-93` | Root cause must use direct same-source logic/data; source/FDR/live boundaries and evidence traceability remain hard constraints. |
| `AGENTS.md:95-145` | Service/Host/Agent/Fund boundaries: prompt/contract assembly belongs to Service, agent run lifecycle/tool loop to Agent, audit/evidence rules to Fund. |
| `docs/current-startup-packet.md:22-24` | Current active gate is exactly `Provider/LLM Chapter 5 Forbidden-phrase No-live Diagnostic Evidence Gate`; required purpose is to distinguish prompt, LLM noncompliance, repair-context, taxonomy and budget hypotheses while preserving `NOT_READY`. |
| `docs/current-startup-packet.md:48-49` | Chapter 6 post-fix bounded live evidence found Chapter 5 `audit_parse` / `forbidden_phrase`; Chapter 5 disposition checkpoint `746ff7e` routes to this no-live evidence gate. |
| `docs/current-startup-packet.md:207-213` | Resume checklist repeats no-live-only scope and prohibits live/provider/source-policy/provider-default/repair-budget/readiness/release/PR changes. |
| `docs/implementation-control.md:24-38` | Current truth guardrails keep deterministic production path, explicit opt-in LLM, default `max_repair_attempts=1`, EID single-source policy and FDR boundary. |
| `docs/implementation-control.md:40-47` | Current gate objective is no-live diagnostic evidence only for Chapter 5 `forbidden_phrase`. |
| `docs/reviews/provider-llm-chapter5-forbidden-phrase-live-blocker-disposition-controller-judgment-20260614.md:30-41` | Accepted runtime facts: Chapter 5 is first failed; failure is `llm_contract_violation` / `audit_parse` / `forbidden_phrase`; attempt 0 drafted then auditor blocked; attempt 1 writer blocked with `writer:forbidden_phrase`; provider attempt count is 0. |
| `docs/reviews/provider-llm-chapter5-forbidden-phrase-live-blocker-disposition-controller-judgment-20260614.md:54-70` | Current classification is `LLM_OUTPUT_POLICY_NONCOMPLIANCE_AFTER_REPAIR_ATTEMPT`; H1-H5 remain open for no-live evidence. |

## 3. Safe Runtime Metadata Evidence

Only safe scalar fields were read from:

- `reports/llm-runs/004393-2025-20260614T002657Z-host_run_8c795cd1469b44d/summary.json`
- `reports/llm-runs/004393-2025-20260614T002657Z-host_run_8c795cd1469b44d/chapters/chapter-05.json`

No raw prompt, draft body, provider payload, source body, final report body or report Markdown was read.

| Runtime scalar | Value |
|---|---|
| summary schema/run | `llm_incomplete_run_summary.v1`; `host_run_8c795cd1469b44d3`; `004393 / 2025` |
| orchestration/final assembly | `partial` / `incomplete`; redaction applied `true`, redaction count `1` |
| first failed | chapter `5`; `status=blocked`; `stop_reason=llm_contract_violation`; `failure_category=audit_parse`; `failure_subcategory=forbidden_phrase`; `attempt_count=2` |
| prompt diagnostic first failed | `phase=writer_parse`; `attempt_index=1`; prompt diagnostic has no persisted `category` field; `primary_subcategory=forbidden_phrase` |
| Chapter 5 prompt diagnostic | `writer_parse`; `writer:forbidden_phrase=1`; `forbidden_phrase_count=1`; `issue_reason_counts.llm_contract_violation=1`; `max_output_chars=12000`; `response_chars=2322` |
| runtime diagnostic first failed | `runtime_operation=auditor`; `repair_attempt_index=0`; `provider_attempt_count=0`; provider runtime categories `[]`; diagnostic consistency `consistent` |
| Chapter 5 runtime rows | row 1: `operation=auditor`, `chapter_failure_category=audit_parse`, `repair_attempt_index=0`, `response_chars=17`; row 2: `operation=writer`, `chapter_failure_category=prompt_contract`, `repair_attempt_index=1` |
| Chapter 5 attempt scalars | attempt 0: `writer_status=drafted`, `audit_status=blocked`, `audit_repair_hint=regenerate`, `repair_decision.action=regenerate`; serialized attempt `issue_ids` arrays are empty; attempt 1: `writer_status=blocked`, `writer_stop_reason=llm_contract_violation`, no second audit/repair decision |
| Chapter 5 top-level issue scalar | `5:llm_contract_violation:writer:forbidden_phrase:7` |

Disposition: runtime metadata directly proves a two-attempt no-live-diagnosable path: attempt 0 reached auditor and repair decision; attempt 1 stopped at writer forbidden-phrase validation; provider response classification remains unproven because provider attempt count is 0. The `audit_parse` / `llm:parse_failure` relationship is a code-path inference from chapter-level failure-category mapping, not a direct persisted attempt `issue_ids` scalar in the serialized runtime JSON.

## 4. Source Evidence

### 4.1 Writer Forbidden-phrase Contract And Validation

| File/function | Evidence |
|---|---|
| `fund_agent/fund/chapter_writer.py:97-110` | Writer maintains `_FORBIDDEN_PHRASES`, including buy/sell/trading-position/return-prediction/manager-motive phrases. |
| `fund_agent/fund/chapter_writer.py:617-620` | Writer system prompt has broad policy text: do not output buy/sell/position/return prediction. |
| `fund_agent/fund/chapter_writer.py:682-708` | Main protocol emphasizes required output, markers, anchors, missing facts and no fabricated facts; no Chapter 5-specific forbidden-phrase correction exists in this prompt block. |
| `fund_agent/fund/chapter_writer.py:1458-1480` | Repair context renders previous issue ids/messages and required corrections only; no hard-coded forbidden-phrase-specific repair instruction is added by the writer. |
| `fund_agent/fund/chapter_writer.py:1612-1645` | Writer validates LLM response deterministically before accepting a draft; `_forbidden_phrase_issues(text)` is part of the blocking validation chain. |
| `fund_agent/fund/chapter_writer.py:1939-1960` | Forbidden phrase validation emits `writer:forbidden_phrase:<index>` with reason `llm_contract_violation`; any matching phrase blocks draft acceptance. |

Finding: writer forbidden-phrase validation is deterministic, provider-independent after a supplied response, and fail-closed. The prompt contains broad policy language, but evidence does not show a Chapter 5-specific forbidden-phrase remediation contract.

### 4.2 Programmatic Auditor Forbidden-phrase Path

| File/function | Evidence |
|---|---|
| `fund_agent/fund/chapter_auditor.py:66-76` | Auditor maintains its own forbidden-phrase list aligned with trading/position/return-prediction phrases. |
| `fund_agent/fund/chapter_auditor.py:1277-1280` | Programmatic audit creates `C1` issue `章节包含禁用措辞：<phrase>` with `repair_hint=regenerate`. |
| `fund_agent/fund/chapter_auditor.py:1630-1649` | Aggregate repair hint chooses the highest-priority hint; forbidden phrase therefore contributes `regenerate` when present. |

Finding: programmatic auditor can independently block forbidden phrases and request regenerate. This is separate from writer parse validation.

### 4.3 Repair Decision And Repair Context

| File/function | Evidence |
|---|---|
| `fund_agent/agent/repair.py:61-145` | Agent repair decision maps failed/blocked audit with `patch`/`regenerate` to `action=regenerate` only if `remaining_budget > 0`; when budget is exhausted, it stops with `repair_budget_exhausted`. |
| `fund_agent/agent/repair.py:151-175` | Agent repair context from audit carries only issue ids, sanitized messages, and deterministic required corrections. |
| `fund_agent/agent/repair.py:277-340` | Required correction mapping has explicit branches for structure, required output, candidate facet, L1, anchor and `llm:parse_failure`; no forbidden-phrase-specific correction branch exists. Default fallback is sanitized issue message. |
| `fund_agent/agent/runner.py:380-420` | Writer-block terminal returns immediately unless it is the special writer invalid-anchor retry path; forbidden phrase is not in that retry path. |
| `fund_agent/agent/runner.py:580-607` | Audit failure repair consumes current budget and constructs next writer input through `repair_context_from_audit`. |
| `fund_agent/agent/runner.py:1348-1369` | Writer `llm_contract_violation` maps to `blocked_prompt_contract`. |
| `fund_agent/agent/runner.py:1579-1599` | Audit `llm:parse_failure` maps to `audit_parse`; blocked/fail audit otherwise maps to `prompt_contract` unless other special cases apply. |

Finding: audit repair context after `llm:parse_failure` carries an auditor-line-protocol correction, not a specific forbidden-phrase removal instruction. If the regenerated writer response still contains a forbidden phrase, writer validation blocks before audit repair can run again.

### 4.4 Service Orchestration Mapping

| File/function | Evidence |
|---|---|
| `fund_agent/services/chapter_orchestrator.py:336-350` | Default Service chapter orchestration policy has `max_repair_attempts=1`. |
| `fund_agent/services/chapter_orchestrator.py:1360-1392` | Writer `llm_contract_violation` maps to `prompt_contract`. |
| `fund_agent/services/chapter_orchestrator.py:1395-1419` | Audit `llm:parse_failure` maps to `audit_parse`; blocked/fail audit otherwise maps to `prompt_contract` unless audit rule too strict or needs more facts. |
| `fund_agent/services/chapter_orchestrator.py:1422-1483` | Writer prompt-contract diagnostic counts `writer:forbidden_phrase` and sets primary subcategory through common subcategory precedence. |
| `fund_agent/services/chapter_orchestrator.py:1486-1538` | Audit prompt-contract diagnostic counts programmatic forbidden phrase via `_is_forbidden_phrase_issue()` and records `phase=programmatic_audit`. |
| `fund_agent/services/chapter_orchestrator.py:1555-1590` | `forbidden_phrase` is an explicit prompt-contract subcategory in fixed precedence. |
| `fund_agent/services/chapter_orchestrator.py:1821-1905` | Service repair decision has the same budget semantics: `remaining_budget <= 0` stops with `repair_budget_exhausted`; `patch`/`regenerate` maps to regenerate only inside budget. |
| `fund_agent/services/chapter_orchestrator.py:1928-1952` | Service repair context from audit carries issue ids, sanitized messages and mapped required corrections. |

Finding: Service diagnostic mapping can count/subcategorize forbidden phrase without provider. Runtime category mismatch is real at lineage level: attempt 0 terminal category is `audit_parse`, while attempt 1 writer diagnostic is `prompt_contract/forbidden_phrase`. This is diagnostic taxonomy layering, not readiness evidence.

## 5. Test Evidence

Command:

```text
uv run pytest -q tests/fund/test_chapter_writer.py::test_writer_rejects_forbidden_trading_advice tests/fund/test_chapter_auditor.py::test_programmatic_audit_fails_forbidden_trading_advice tests/fund/test_chapter_auditor.py::test_llm_audit_parse_failure_is_blocked tests/agent/test_repair_policy.py::test_repair_budget_exhausted_stops_without_hidden_retry tests/agent/test_repair_policy.py::test_repair_context_records_issue_ids_and_sanitized_messages tests/agent/test_runner.py::test_repair_budget_exhausted_records_each_regenerate_attempt tests/agent/test_runner.py::test_chapter_6_invalid_anchor_marker_twice_fails_closed_after_one_retry tests/services/test_chapter_orchestrator.py::test_writer_forbidden_phrase_subcategory_remains_blocked tests/services/test_chapter_orchestrator.py::test_programmatic_forbidden_phrase_is_counted_not_accepted tests/services/test_chapter_orchestrator.py::test_audit_parse_failure_records_audit_parse_diagnostic tests/services/test_chapter_orchestrator.py::test_repair_budget_exhausted_returns_failed_stop_reason
```

Result:

```text
11 passed in 0.46s
```

First attempted command used two incorrect test node ids and exited with pytest collection error before running tests; it provided no behavioral evidence and is not counted as validation.

| Test | Evidence |
|---|---|
| `tests/fund/test_chapter_writer.py:1120-1140` | Writer blocks a valid chapter body appended with `建议买入。` as `llm_contract_violation`. |
| `tests/fund/test_chapter_auditor.py:207-225` | Programmatic audit fails forbidden trading advice with rule `C1`. |
| `tests/fund/test_chapter_auditor.py:1071-1088` | LLM audit line-protocol parse failure is blocked, not silently accepted. |
| `tests/agent/test_repair_policy.py:84-98` | Exhausted repair budget stops without hidden retry. |
| `tests/agent/test_repair_policy.py:118-131` | Repair context records issue ids and sanitized messages, excluding raw prompt/secret text. |
| `tests/agent/test_runner.py:489-513` | Default one content repair attempt yields two writer requests/attempts and then `blocked_repair_budget_exhausted` after repeated regenerate-triggering audit failure. |
| `tests/agent/test_runner.py:553-576` | Writer invalid anchor has a special one-retry path; second failure blocks as `prompt_contract` with no third retry. This proves special writer retry is narrow and budget-bound. |
| `tests/services/test_chapter_orchestrator.py:745-762` | Writer forbidden phrase is blocked and diagnosed as `forbidden_phrase` with `writer:forbidden_phrase` count, without leaking phrase text into prefix counts. |
| `tests/services/test_chapter_orchestrator.py:833-860` | Programmatic forbidden phrase is counted as `forbidden_phrase` and not accepted. |
| `tests/services/test_chapter_orchestrator.py:1488-1502` | Audit parse failure records `audit_parse` at repair attempt 1. |
| `tests/services/test_chapter_orchestrator.py:1946-1977` | Service repair budget exhaustion returns `repair_budget_exhausted`. |

## 6. Hypothesis Disposition

| Hypothesis | Disposition | Direct evidence basis |
|---|---|---|
| H1. Chapter 5 prompt contract omission. | `DEFER_AS_PARTIAL` | Writer prompt has broad global prohibition (`chapter_writer.py:617-620`) and no Chapter 5-specific forbidden-phrase remediation in the visible prompt assembly (`chapter_writer.py:682-708`, `1458-1480`). This supports a repair/prompt specificity gap, but does not prove the initial Chapter 5 prompt omitted all relevant policy because raw prompt bodies were intentionally not read. |
| H2. LLM policy noncompliance correctly caught by writer validation. | `ACCEPT` | Runtime attempt 1 has `writer_status=blocked`, `writer_stop_reason=llm_contract_violation`, `writer:forbidden_phrase` count 1 and provider attempt count 0. Writer code blocks any `_FORBIDDEN_PHRASES` match with `writer:forbidden_phrase:<index>` / `llm_contract_violation` (`chapter_writer.py:1939-1960`), and no-live test confirms `建议买入。` blocks (`test_chapter_writer.py:1120-1140`). |
| H3. Audit repair context lacks specific forbidden-phrase correction. | `ACCEPT` | The serialized runtime attempt `issue_ids` arrays are empty, so `llm:parse_failure` is not claimed as a direct runtime scalar here. The accepted chapter-level `audit_parse` classification maps through code to the audit parse-failure path (`runner.py:1579-1599`, `chapter_orchestrator.py:1395-1419`), whose required correction is auditor line protocol (`repair.py:338-340`) rather than forbidden-phrase removal. The repair correction mapping has no forbidden-phrase-specific branch (`repair.py:277-340`), and writer only renders supplied issue ids/messages/corrections (`chapter_writer.py:1458-1480`). |
| H4. Audit/writer diagnostic taxonomy mismatch. | `ACCEPT_AS_DIAGNOSTIC_LAYERING` | Runtime first failed category is `audit_parse` while prompt diagnostic first failed phase is `writer_parse` / `forbidden_phrase`; Chapter 5 runtime rows include attempt 0 auditor `audit_parse` and attempt 1 writer `prompt_contract`. Service code maps `llm:parse_failure` to `audit_parse` (`chapter_orchestrator.py:1395-1412`) and writer `llm_contract_violation` to `prompt_contract` with forbidden-phrase subcategory (`chapter_orchestrator.py:1360-1392`, `1422-1483`). This is a taxonomy lineage mismatch requiring planning, not readiness evidence. |
| H5. Existing repair budget intentionally makes second-attempt writer forbidden phrase terminal. | `ACCEPT_CURRENT_BEHAVIOR` | Default policy is `max_repair_attempts=1` (`chapter_orchestrator.py:336-350`). Attempt 0 consumes the single regenerate budget; attempt 1 writer block has no second audit/repair decision. Runner returns writer-block terminal unless it is the special invalid-anchor retry path (`runner.py:380-420`), and tests prove one repair means no hidden retry (`test_runner.py:489-513`, `test_repair_policy.py:84-98`). |

## 7. Consolidated Diagnostic Conclusion

The direct no-live evidence supports the following current-state explanation:

1. Attempt 0 produced a draft and failed in auditor parsing as `llm:parse_failure`, which generated a generic regenerate repair context focused on auditor line protocol.
2. That repair context did not carry a specific forbidden-phrase removal correction.
3. Attempt 1 generated a writer response containing a forbidden phrase; writer validation correctly blocked it as `writer:forbidden_phrase` / `llm_contract_violation` before any second audit/repair.
4. Service/runtime summary reports the terminal lineage as `audit_parse` while the attempt-level prompt diagnostic reports writer `forbidden_phrase`; both are explainable from current taxonomy but need no-live fix planning if the next gate wants clearer terminal categorization or targeted repair context.
5. With current default repair budget `1`, the second-attempt writer forbidden-phrase block is terminal by design in current code, not evidence of source acquisition, provider runtime, or readiness state.

Recommended next entry: narrow no-live fix planning gate, scoped to deciding whether to add forbidden-phrase-specific repair context/prompt guidance, diagnostic lineage normalization, or both, while preserving repair budget and `NOT_READY` unless separately authorized.

## 8. Verification And Workspace Notes

| Check | Result |
|---|---|
| `git diff --check` | Passed with no output before writing this artifact. |
| `git status --short` | Worktree was already dirty before this artifact: modified `AGENTS.md`, `README.md`, `docs/design.md`, plus many untracked docs/reports/scripts/data paths. This status is not used as readiness, source truth, or content correctness evidence. |
| Targeted no-live pytest | `11 passed in 0.46s`. |

Final verdict:

```text
VERDICT: DIAGNOSTIC_EVIDENCE_READY_FOR_NO_LIVE_FIX_PLANNING_NOT_READY
```
