# Provider/LLM Chapter 6 Invalid-marker Live-blocker Disposition Plan Review — AgentDS

Date: 2026-06-14

Role: AgentDS independent plan reviewer

Gate: `Provider/LLM Chapter 6 Invalid-marker Live-blocker Disposition Gate`

Review target: `docs/reviews/provider-llm-chapter6-invalid-marker-live-blocker-disposition-plan-20260614.md`

Verdict: `ACCEPT`

## NO BLOCKING FINDINGS

## Findings

### F1. Plan stays inside safe metadata and no-code disposition boundary (Q1: PASS)

The plan reads only safe metadata files (manifest.json, summary.json, chapter-06.json) from the accepted live run, plus existing source code (`chapter_writer.py`) and test files for contract/coverage understanding. It explicitly declares all unread body categories (writer/auditor/repair markdown, prompt bodies, provider payloads, PDF/source/cache bodies, final report body). No live/provider/LLM/network commands were run. No source, test, runtime, prompt, or config changes were made. EID single-source/no-fallback is preserved. `NOT_READY` is preserved. The plan stays within the no-code disposition boundary declared by the controller judgment at `bcbbfd3`.

Safe metadata cross-check confirms all plan claims:

- `manifest.json`: `orchestration_status=partial`, `final_assembly_status=incomplete`, `fund_code=004393`, `report_year=2025`
- `summary.json`: Chapter 6 `status=blocked`, `failure_category=prompt_contract`, `failure_subcategory=invalid_marker`, `first_failed.chapter_id=6`; Chapters 1-5 `status=accepted`; `prompt_contract_diagnostics` confirms `invalid_marker_count=4`, `unknown_anchor_count=0`, `phase=writer_parse`, `finish_reason=stop`, `response_chars=3120`
- `chapter-06.json`: 4 issues at character offsets 63/711/1095/1521, all `writer:invalid_anchor_marker`, message is generic format violation description without exposing malformed marker text; `writer_used_anchor_ids=[]`, `unknown_anchor_count=0`, `provider_attempt_count=0` in runtime diagnostics

### F2. Root-cause classification is well-calibrated (Q2: PASS)

The plan classifies the strongest root-cause category as `LLM output-format noncompliance with existing anchor marker contract`. The classification is supported by convergent safe-metadata evidence:

- `invalid_marker_count=4` with `unknown_anchor_count=0` — format rejection, not unauthorized-ID rejection
- `finish_reason=stop`, `response_chars=3120` < `max_output_chars=12000` — no truncation confound
- `required_output_missing_count=0`, `required_structure_missing_count=0`, `forbidden_phrase_count=0` — no competing failure categories
- `writer_used_anchor_ids=[]` — zero valid anchors parsed, consistent with format-level rejection of all markers
- `provider_attempt_count=0` — pre-provider writer-parse failure, not a provider response issue

The plan correctly labels this as `STRONGEST_CURRENT_ROOT_CAUSE_CATEGORY` rather than proven root cause, and explicitly identifies the `ACCEPTED_EVIDENCE_GAP` of missing no-live diagnostic evidence as the binding constraint on proceeding to a fix.

Alternative hypotheses are properly dispositioned: prompt/contract ambiguity is `POSSIBLE_CONTRIBUTOR_UNPROVEN` (to be checked in diagnostics before fix planning), parser over-strictness is `WEAK_UNPROVEN` (contract explicitly requires exact format, no contradictory evidence), another live command is `REJECTED` (would spend budget without isolating root cause), and blocked-pending-decision is `REJECTED` (fail-closed policy already in place).

### F3. Recommended next gate is better supported than alternatives (Q3: PASS)

The plan recommends a `no-live diagnostic evidence gate` and explicitly rejects three alternatives:

- **Additional bounded live evidence**: correctly rejected — a live sample already exposed the blocker; another live run would spend provider budget without isolating root cause; the gap is no-live reproducibility/diagnostic detail
- **Immediate no-live fix planning**: correctly deferred — diagnostic evidence must first identify whether the fix surface is prompt clarification, repair instruction, or validator adjustment
- **Blocked**: correctly rejected — the path forward is clear enough; no product decision is needed to collect diagnostics under current fail-closed policy

The decision to route through no-live diagnostics before any fix planning follows the same pattern successfully used for Chapter 2 L1 (root-cause evidence → fix plan → implementation → live evidence) and Chapter 3 (diagnostic disposition → root-cause evidence → fix implementation → live evidence). This sequencing discipline is consistent with the established gateflow.

### F4. Hypotheses, residuals, and non-goals are cleanly separated (Q4: PASS)

The hypothesis disposition table (Section 4) uses a consistent six-column format with explicit evidence-for/evidence-against/disposition, and clear disposition labels (STRONGEST, POSSIBLE_CONTRIBUTOR_UNPROVEN, WEAK_UNPROVEN, ACCEPTED_EVIDENCE_GAP, REJECTED). Each hypothesis has a distinct evidential basis and a clear routing decision.

Non-goals (Section 6) are comprehensive: all prohibited actions are listed, and all deferred gates are explicitly named with their deferral rationale.

One observation: the plan embeds residual information in the hypothesis dispositions and scope statement rather than in a standalone residuals table. This is a format choice, not a deficiency — all residual information is present and clearly attributed. The `ACCEPTED_EVIDENCE_GAP` disposition in particular serves as the primary residual driving the next gate.

### F5. Next-gate validation checks D1-D5 are specific and actionable (Q5: PASS)

Each check has a clear input, method, and expected output:

| Check | Assessment |
|---|---|
| D1 (prompt contract rendering) | Specific: inspect no-live rendered Chapter 6 writer prompt; record presence/absence of marker format, allowed-anchor language, and bond-risk internal-anchor prohibition. Actionable without production code changes. |
| D2 (validator taxonomy) | Specific: use fake LLM/no-live inputs; demonstrate routing of malformed markers → `invalid_marker` vs unauthorized IDs → `unknown_anchor`. Directly testable. |
| D3 (diagnostic payload mapping) | Specific: verify orchestrator diagnostics count `writer:invalid_anchor_marker` as `invalid_marker_count` and do not leak raw marker suffixes. The safe metadata already confirms position-only issue IDs; D3 formalizes this as a verification step. |
| D4 (repair-context specificity) | Specific: inspect repair-context text for `invalid_marker`; determine whether it instructs exact marker syntax. Actionable by reading generated repair context. |
| D5 (boundary preservation) | Specific: confirm no live/provider/PDF/source/fallback/readiness/release commands and no unauthorized body reads. Standard gate-boundary check. |

The acceptance criteria routing matrix (prompt ambiguity → prompt fix, validator bug → parser fix, repair insufficiency → repair-context fix) provides clear decision branches for the controller.

## Cross-check Summary

| Plan claim | Safe metadata verification | Match? |
|---|---|---|
| Chapter 6 first failed, `invalid_marker`, `prompt_contract` | `summary.json` first_failed and chapter_matrix[5] | Yes |
| `invalid_marker_count=4`, `unknown_anchor_count=0` | `summary.json` prompt_contract_diagnostics, `chapter-06.json` issues array | Yes |
| `finish_reason=stop`, `response_chars=3120`, no truncation | `chapter-06.json` writer_finish_reason, writer_response_chars, chapter_prompt_contract_diagnostics | Yes |
| `provider_attempt_count=0` (pre-provider failure) | `summary.json` runtime_diagnostics.first_failed.provider_attempt_count=0 | Yes |
| Position-only issue IDs | `chapter-06.json` issue IDs use numeric position suffixes (63/711/1095/1521), messages are generic | Yes |
| `writer_used_anchor_ids=[]` | `chapter-06.json` attempts[0].writer_used_anchor_ids is empty array | Yes |
| Chapters 1-5 accepted | `summary.json` chapter_matrix[0]-[4] all `status=accepted` | Yes |

## Verdict

`VERDICT: ACCEPT`

No blocking findings. The plan is well-calibrated on root-cause classification, correctly identifies the evidence gap, recommends the appropriate next gate, separates hypotheses/residuals/non-goals cleanly, and provides specific actionable validation checks for the next gate. The plan stays within the no-code disposition boundary and preserves all required constraints (EID single-source/no-fallback, `NOT_READY`, no live/provider by default).
