# Provider/LLM Chapter 5 Forbidden-phrase No-live Diagnostic Evidence — DS Review

Date: 2026-06-14

Role: AgentDS evidence reviewer

Gate: `Provider/LLM Chapter 5 Forbidden-phrase No-live Diagnostic Evidence Gate`

Verdict: `PASS_WITH_FINDINGS`

## Review Scope

This review verifies whether the no-live diagnostic evidence artifact `docs/reviews/provider-llm-chapter5-forbidden-phrase-no-live-diagnostic-evidence-20260614.md` supports its conclusion for the next no-live fix planning gate. No live/provider/LLM/network/PDF/FDR/source commands were run. No source was modified.

## Evidence Verified

| Check | Method | Result |
|---|---|---|
| `git diff --check` | Direct run | Passed (no output) |
| `git status --short` | Direct run | Confirmed pre-existing dirty worktree; not used as evidence |
| summary.json safe scalars | jq | Confirmed: `schema_version=llm_incomplete_run_summary.v1`, `run_id=host_run_8c795cd1469b44d3`, `orchestration_status=partial`, `final_assembly_status=incomplete`, `redaction_applied=true`, `redaction_count=1` |
| summary.json first_failed | jq | Confirmed: `chapter_id=5`, `status=blocked`, `stop_reason=llm_contract_violation`, `failure_category=audit_parse`, `failure_subcategory=forbidden_phrase`, `attempt_count=2` |
| chapter-05.json attempt scalars | jq | Confirmed: attempt 0 `writer_status=drafted`, `audit_status=blocked`, `repair_hint=regenerate`, `repair_action=regenerate`; attempt 1 `writer_status=blocked` |
| chapter-05.json issues | jq | Confirmed: `["5:llm_contract_violation:writer:forbidden_phrase:7"]` |
| chapter-05.json prompt contract diagnostic | jq | Confirmed: `phase=writer_parse`, `attempt_index=1`, `forbidden_phrase_count=1`, `issue_id_prefix_counts={"writer:forbidden_phrase":1}`, `issue_reason_counts={"llm_contract_violation":1}`, `max_output_chars=12000`, `response_chars=2322`, `primary_subcategory=forbidden_phrase` |
| chapter-05.json runtime diagnostic rows | jq | Confirmed: row 1 `operation=auditor`, `chapter_failure_category=audit_parse`, `repair_attempt_index=0`, `response_chars=17`; row 2 `operation=writer`, `chapter_failure_category=prompt_contract`, `repair_attempt_index=1` |
| chapter-05.json terminal fields | jq | Confirmed: `terminal_failure_category=audit_parse`, `diagnostic_consistency_status=consistent` |
| Source: `_FORBIDDEN_PHRASES` (writer) | nl/sed | Confirmed at `chapter_writer.py:97-110`; 12 phrases including buy/sell/position/return/motive |
| Source: `_forbidden_phrase_issues()` | nl/sed | Confirmed at `chapter_writer.py:1939-1960`; emits `writer:forbidden_phrase:<index>` with `llm_contract_violation` |
| Source: writer validation chain | nl/sed | Confirmed at `chapter_writer.py:1612-1645`; `_forbidden_phrase_issues(text)` is in blocking chain at line 1643 |
| Source: writer system prompt | nl/sed | Confirmed at `chapter_writer.py:617-620`; broad prohibition on buy/sell/position/return |
| Source: writer main protocol | nl/sed | Confirmed at `chapter_writer.py:682-708`; no Chapter 5-specific forbidden-phrase correction |
| Source: `_repair_context_prompt()` | nl/sed | Confirmed at `chapter_writer.py:1458-1480`; renders issue ids, messages, corrections only; no hard-coded forbidden-phrase instruction |
| Source: auditor forbidden phrases | nl/sed | Confirmed at `chapter_auditor.py:66-76`; aligned list, 12 phrases |
| Source: auditor C1 forbidden phrase | nl/sed | Confirmed at `chapter_auditor.py:1277-1280`; emits C1 with `repair_hint=regenerate` |
| Source: `_aggregate_repair_hint()` | nl/sed | Confirmed at `chapter_auditor.py:1630-1649`; chooses highest-priority hint |
| Source: `decide_repair()` (agent) | nl/sed | Confirmed at `repair.py:61-145`; budget-exhausted stops with `repair_budget_exhausted`; `repair_hint in (patch, regenerate)` → `action=regenerate` only when `remaining_budget > 0` |
| Source: `repair_context_from_audit()` | nl/sed | Confirmed at `repair.py:151-175`; carries issue ids, sanitized messages, required corrections |
| Source: `_required_correction_from_issue()` | nl/sed | Confirmed at `repair.py:300-340`; explicit branches for structure, required output, candidate facet, L1, anchor, `llm:parse_failure` (line 338-339); no forbidden-phrase-specific branch |
| Source: writer-block terminal (agent runner) | nl/sed | Confirmed at `runner.py:380-420`; `_should_retry_writer_invalid_marker()` is the only writer-block retry path (lines 389-409); forbidden phrase is not in that path |
| Source: audit failure repair (agent runner) | nl/sed | Confirmed at `runner.py:580-607`; consumes budget, constructs next writer input via `repair_context_from_audit()` |
| Source: `_terminal_from_writer_stop_reason()` | nl/sed | Confirmed at `runner.py:1348-1369`; `llm_contract_violation` → `blocked_prompt_contract` |
| Source: `_failure_category_from_audit_result()` | nl/sed | Confirmed at `runner.py:1579-1599`; `llm:parse_failure` → `audit_parse`; blocked/fail → `prompt_contract` |
| Source: Service orchestrator policy | nl/sed | Confirmed at `chapter_orchestrator.py:336-350`; `max_repair_attempts=1` default |
| Source: Service writer failure mapping | nl/sed | Confirmed at `chapter_orchestrator.py:1360-1392`; `llm_contract_violation` → `prompt_contract` |
| Source: Service audit failure mapping | nl/sed | Confirmed at `chapter_orchestrator.py:1395-1419`; `llm:parse_failure` → `audit_parse` |
| Source: `_writer_prompt_contract_diagnostic()` | nl/sed | Confirmed at `chapter_orchestrator.py:1422-1483`; counts `writer:forbidden_phrase`, sets subcategory precedence |
| Source: Service `_decide_repair()` | nl/sed | Confirmed at `chapter_orchestrator.py:1821-1907`; same budget semantics |
| Test function line numbers | rg | All 11 test function names and start lines match artifact claims |

## Findings

### F1: `issue_ids` overread from runtime metadata

**Location**: Target artifact §3 line 56.

**Claim**: `attempt 0: ... issue_ids=[llm:parse_failure]`

**Direct evidence**: The actual `chapter-05.json` shows `"issue_ids": []` for attempt 0 and `"issue_ids": []` for attempt 1. The `llm:parse_failure` value is not present in the runtime JSON scalars.

**Analysis**: The artifact infers `llm:parse_failure` from the code path analysis — `failure_category=audit_parse` in both the agent runner (`runner.py:1593`: `if "llm:parse_failure" in issue_ids: return "audit_parse"`) and the Service orchestrator (`chapter_orchestrator.py:1411`: `if "llm:parse_failure" in issue_ids: return "audit_parse"`). This inference is logically sound, but the artifact presents it as a direct runtime metadata scalar rather than as a code-path inference. The `issue_ids` arrays were not persisted in the serialized chapter artifact, so the actual runtime issue IDs are not directly available as claimed.

**Severity**: Non-blocking. The H3 conclusion (repair context lacks specific forbidden-phrase correction) remains fully supported by code evidence alone: `_required_correction_from_issue()` has no forbidden-phrase branch, and `failure_category=audit_parse` reliably indicates the auditor found `llm:parse_failure` at runtime.

**Recommendation**: Amend the artifact to note that `issue_ids` arrays are empty in the serialized JSON and that the `llm:parse_failure` classification is derived from the `failure_category=audit_parse` code-path mapping, not from a direct runtime scalar.

### F2: Prompt diagnostic `category` field misattribution

**Location**: Target artifact §3 line 52.

**Claim**: `prompt diagnostic first failed: ... category=audit_parse`

**Direct evidence**: The actual `chapter_prompt_contract_diagnostics[0]` has `category: null`. The `chapter_prompt_contract_diagnostics` schema (`ChapterPromptContractDiagnostic` dataclass in `chapter_orchestrator.py`) does not include a `category` field — only `phase`, `attempt_index`, `primary_subcategory`, `issue_reason_counts`, `issue_id_prefix_counts`, and counted fields.

**Analysis**: The artifact conflates the chapter-level `failure_category` (`audit_parse`, from `chapter-05.json`) with a non-existent prompt-diagnostic `category` field. The prompt diagnostic correctly reports `phase=writer_parse` and `primary_subcategory=forbidden_phrase`, which is the correct taxonomy for the attempt 1 writer-level diagnostic. The chapter-level terminal category is `audit_parse` from attempt 0, and the prompt diagnostic represents the attempt 1 writer phase. These are at different layers of the diagnostic taxonomy, which is precisely the taxonomy layering issue that H4 addresses.

**Severity**: Non-blocking. The conflation does not create false evidence — it mislabels the source of the `audit_parse` value. The core facts (attempt 0 auditor `audit_parse`, attempt 1 writer `forbidden_phrase`) are correctly captured elsewhere in the artifact.

**Recommendation**: Amend the artifact to remove the `category=audit_parse` claim from the prompt diagnostic row and instead note that the prompt diagnostic has no `category` field; the `audit_parse` value belongs to the chapter-level terminal failure category from attempt 0.

### F3: Artifact line 53 references `prompt diagnostic first failed` with composite summary-level label

**Location**: Target artifact §3 line 53.

**Claim**: `Chapter 5 prompt diagnostic: writer_parse; writer:forbidden_phrase=1; forbidden_phrase_count=1; issue_reason_counts.llm_contract_violation=1; max_output_chars=12000; response_chars=2322`

**Direct evidence**: All individual scalar values in this row are verified correct against the actual JSON. The row composition is faithful.

**Severity**: Informational. All values are correct. The artifact's label `Chapter 5 prompt diagnostic` is imprecise (the data comes from `chapter_prompt_contract_diagnostics[0]`), but the data mapping is accurate.

## H1-H5 Disposition Cross-check

| Hypothesis | Artifact verdict | DS verification |
|---|---|---|
| H1: Chapter 5 prompt contract omission | `DEFER_AS_PARTIAL` | Supported. Writer prompt has broad policy but no Chapter 5-specific forbidden-phrase remediation in visible prompt assembly. |
| H2: LLM policy noncompliance caught by writer validation | `ACCEPT` | Supported. Runtime metadata confirms writer blocked at attempt 1 with `writer:forbidden_phrase` and provider attempt count 0. Writer code path confirmed. |
| H3: Audit repair context lacks specific forbidden-phrase correction | `ACCEPT` | Supported. Code evidence confirms no forbidden-phrase branch in `_required_correction_from_issue()`. F1 overread does not undermine this — the inference path (`audit_parse` → `llm:parse_failure` → line-protocol correction) is correct. |
| H4: Audit/writer diagnostic taxonomy mismatch | `ACCEPT_AS_DIAGNOSTIC_LAYERING` | Supported. Terminal category `audit_parse` from attempt 0 vs prompt diagnostic `writer_parse`/`forbidden_phrase` from attempt 1 are different layers. F2 imprecision does not invalidate the core layering observation. |
| H5: Existing repair budget makes second-attempt writer forbidden phrase terminal | `ACCEPT_CURRENT_BEHAVIOR` | Supported. Default `max_repair_attempts=1`, attempt 0 consumed it, attempt 1 writer block has no second chance. |

## Boundary Compliance

| Boundary | Status |
|---|---|
| No live/provider/LLM/network/PDF/FDR commands | PASS |
| No source modification | PASS |
| No design/control/README modification | PASS |
| No staging, commit, push, PR | PASS |
| Source code reads within allowed scope | PASS |
| jq safe scalar extraction only | PASS |
| git diff/status only | PASS |
| Targeted no-live pytest within allowed scope | PASS (artifact reports `11 passed`, test names match code) |

## Consolidated Conclusion

The artifact correctly distinguishes prompt contract omission (H1), LLM policy noncompliance caught by writer (H2), audit repair context gap (H3), taxonomy layering (H4), and intended budget terminal behavior (H5) using no-live code evidence and safe runtime metadata. The recommended next entry (narrow no-live fix planning gate) is appropriate — the evidence is sufficient for planning, not for direct implementation.

Two non-blocking imprecisions are noted: F1 overreads `issue_ids=[llm:parse_failure]` from metadata where the actual arrays are empty, and F2 misattributes `category=audit_parse` to a prompt diagnostic field that is actually null. Neither undermines the core diagnostic conclusions.

## Verdict

```text
VERDICT: PASS_WITH_FINDINGS
```

F1 and F2 are non-blocking. The diagnostic evidence is ready for no-live fix planning gate after the artifact is amended to correct the two metadata representation imprecisions.
