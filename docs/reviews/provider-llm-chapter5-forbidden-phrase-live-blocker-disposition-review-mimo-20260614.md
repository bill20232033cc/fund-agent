# Provider/LLM Chapter 5 Forbidden-phrase Live-blocker Disposition Review (MiMo)

Date: 2026-06-14

Reviewer: AgentMiMo

Gate: `Provider/LLM Chapter 5 Forbidden-phrase Live-blocker Disposition Gate`

Target artifact: `docs/reviews/provider-llm-chapter5-forbidden-phrase-live-blocker-disposition-20260614.md`

Verdict: `PASS_WITH_FINDINGS`

## 1. Review Scope

Findings-first review of the disposition artifact against accepted live evidence, safe metadata, control docs and hard boundaries. No source/test/runtime change, no live/provider command, no raw body read.

## 2. Safe Metadata Cross-check

Reviewer independently extracted safe metadata from the accepted runtime artifact.

### 2.1 Summary first_failed

```text
$ jq '.runtime_diagnostics.first_failed' .../summary.json
chapter_id=5
status=blocked
stop_reason=llm_contract_violation
category=audit_parse
subcategory=forbidden_phrase
runtime_operation=auditor
provider_attempt_count=0
diagnostic_consistency_status=consistent
```

Disposition Section 3 summary facts match exactly.

### 2.2 Chapter-05 top-level

```text
$ jq '{chapter_id, status, stop_reason, failure_category, failure_subcategory, attempts_count}' .../chapter-05.json
chapter_id=5
status=blocked
stop_reason=llm_contract_violation
failure_category=audit_parse
failure_subcategory=forbidden_phrase
attempts_count=2
```

Disposition Section 3 top-level facts match exactly.

### 2.3 Attempt-level detail

Attempt 0:

| Field | Safe metadata value | Disposition claim |
|---|---|---|
| `writer_status` | `drafted` | `drafted` |
| `writer_stop_reason` | `none` | `none` |
| `audit_status` | `blocked` | `blocked` |
| `runtime_diagnostics[0].operation` | `auditor` | `auditor` |
| `writer_issues` | `[]` (empty) | (not explicitly listed) |
| `programmatic_issues` | 1 entry: `llm:parse_failure`, rule `C1`, severity `blocking` | (not explicitly listed; audit_parse implied) |
| `repair_decision.action` | `regenerate` | (not explicitly listed) |

Attempt 1:

| Field | Safe metadata value | Disposition claim |
|---|---|---|
| `writer_status` | `blocked` | `blocked` |
| `writer_stop_reason` | `llm_contract_violation` | `llm_contract_violation` |
| `audit_status` | `null` | `null` |
| `runtime_diagnostics[0].operation` | `writer` | `writer` |
| `writer_issues` | 1 entry: `writer:forbidden_phrase:7`, message "章节草稿包含禁用措辞：减仓" | (not explicitly listed) |

### 2.4 Issue list

```text
$ jq '.issues' .../chapter-05.json
["5:llm_contract_violation:writer:forbidden_phrase:7"]
```

Disposition Section 3 issue list matches exactly.

## 3. Findings

### F1: Attempt 1 runtime_category column value not directly extractable from safe metadata — NON-BLOCKING

The disposition table (Section 3) lists `Runtime category` for attempt 1 as `prompt_contract`. The safe metadata `chapter-05.json` stores `runtime_diagnostics` as an array; for attempt 1, `runtime_diagnostics[0].category` is `null`. The summary-level `first_failed.subcategory` is `forbidden_phrase` (not `prompt_contract`). The value `prompt_contract` may be derived from the writer stop reason `llm_contract_violation` or from the writer issue reason field, but the extraction path from safe metadata is not self-evident.

This does not affect the root-cause classification or routing because:
- The summary-level `failure_subcategory=forbidden_phrase` is the controlling fact.
- The writer issue `writer:forbidden_phrase:7` confirms the writer validation caught the forbidden phrase.
- The conclusion that attempt 1 was writer-blocked (not audit-blocked) is correct regardless of the category label.

**Disposition**: FINDING_ACCEPTED_AS_NONBLOCKING. The `prompt_contract` label should be traceable to its exact safe-metadata extraction path in a future evidence gate if needed, but it does not block routing.

## 4. Review Questions

### Q1: Is the root-cause classification supported by accepted live evidence and safe metadata?

**PASS.** Classification `LLM_OUTPUT_POLICY_NONCOMPLIANCE_AFTER_REPAIR_ATTEMPT` is supported:

- Attempt 0: writer drafted, audit blocked with `audit_parse` / `forbidden_phrase` (C1 parse failure), repair triggered.
- Attempt 1: writer blocked with `writer:forbidden_phrase:7` ("减仓"), no audit reached.
- Provider attempt count is `0`; no provider interaction occurred.
- The blocker is writer/auditor forbidden-phrase policy, not provider/source.

### Q2: Is direct implementation correctly rejected for this gate?

**PASS.** Root cause is not specific enough for implementation. Five hypotheses (H1-H5) are open and require no-live diagnostic evidence to distinguish. Direct implementation without knowing whether the fix is prompt, repair context, taxonomy, writer validation or budget behavior would be premature.

### Q3: Is the recommended next gate appropriate?

**PASS.** `Provider/LLM Chapter 5 Forbidden-phrase No-live Diagnostic Evidence Gate` is the correct next gate. The disposition correctly specifies:
- Source/test paths for diagnostic evidence (chapter_writer, chapter_auditor, repair, runner, chapter_orchestrator and their tests).
- Five hypotheses to distinguish (prompt omission, LLM noncompliance, repair context gap, taxonomy mismatch, budget fail-closed).
- Forbidden paths (no live/provider/source/PR commands).

### Q4: Does the artifact avoid overclaim?

**PASS.** No overclaim detected:
- No provider readiness claim (provider attempt count correctly noted as `0`).
- No source policy change.
- No readiness/release/PR claim.
- No fallback design implied.
- `NOT_READY` preserved throughout.

### Q5: Are residuals and hypotheses complete enough for the next evidence gate?

**PASS.** Five hypotheses (H1-H5) cover the plausible root-cause space:
- H1: Prompt omission (forbidden phrase not in prompt).
- H2: LLM noncompliance caught by writer validation.
- H3: Repair context missing specific correction.
- H4: Audit/writer taxonomy mismatch.
- H5: Repair budget of 1 makes second-attempt writer failure terminal.

Residuals are correctly listed: Chapter 5 forbidden phrase blocks final assembly, Chapter 2 L1 metadata is a monitoring residual, provider response classification is unproven, `NOT_READY` preserved.

## 5. Boundary Compliance

| Boundary | Status |
|---|---|
| No live/provider/LLM/network/PDF/FDR/source/analyze/checklist/golden/readiness/release commands | PASS |
| No raw body, raw prompt, provider payload, source/PDF/cache body, final report body read | PASS |
| No source/test/runtime behavior change | PASS |
| No source policy, provider default, repair budget, fallback change | PASS |
| No readiness/release/PR claim | PASS |
| `NOT_READY` preserved | PASS |

## 6. Final Verdict

`VERDICT: PASS_WITH_FINDINGS`

The disposition artifact correctly classifies the Chapter 5 forbidden-phrase root cause, rejects direct implementation, routes to the correct next gate (no-live diagnostic evidence), avoids overclaim, and preserves `NOT_READY`. One non-blocking finding (attempt 1 `runtime_category` extraction traceability) does not affect routing or classification.
