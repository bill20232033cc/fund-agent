# Provider/LLM Chapter 3 Item 01 Fact-gap Disposition — DS Review

Date: 2026-06-14

## 1. Scope

Review target: `docs/reviews/provider-llm-chapter3-item01-fact-gap-disposition-20260614.md`

Review question: Does the target artifact correctly classify Chapter 3 item 01 `fact_gap` as accepted fail-closed residual and route to required-output policy planning, without overclaiming readiness or implementation authorization?

## 2. Evidence Reviewed

Truth/control:
- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/design.md` (Route C, fail-closed, EID single-source, annual-period sections)
- `docs/fund-analysis-template-draft.md` (ch3.required_output.item_01 section)

Accepted input artifacts:
- `docs/reviews/provider-llm-chapter3-post-fix-provider-before-valueerror-no-live-root-cause-evidence-controller-judgment-20260614.md`
- `docs/reviews/provider-llm-chapter3-required-output-item01-missing-evidence-no-live-fix-implementation-controller-judgment-20260614.md`
- `docs/reviews/provider-llm-chapter3-item01-post-fix-bounded-live-re-evidence-controller-judgment-20260614.md`
- `docs/reviews/provider-llm-chapter2-l1-post-fix-bounded-live-re-evidence-controller-judgment-20260614.md`

Safe runtime metadata:
- `reports/llm-runs/004393-2025-20260613T201900Z-host_run_4a531cbe94604e4/manifest.json`
- `reports/llm-runs/004393-2025-20260613T201900Z-host_run_4a531cbe94604e4/summary.json`
- `reports/llm-runs/004393-2025-20260613T201900Z-host_run_4a531cbe94604e4/chapters/chapter-02.json`
- `reports/llm-runs/004393-2025-20260613T201900Z-host_run_4a531cbe94604e4/chapters/chapter-03.json`

Forbidden reads not used: writer Markdown, auditor feedback Markdown, raw prompts, provider payloads/responses, source/cache/PDF bodies, final report body.

## 3. Findings

### F1 — Final verdict string is unusually verbose (presentation)

The target verdict (Section 8) reads:

`ACCEPT_AS_FAIL_CLOSED_RESIDUAL_READY_FOR_REQUIRED_OUTPUT_POLICY_PLANNING_GATE_NOT_READY`

This combines four distinct concepts (classification, readiness-for-next-gate, next-gate name, NOT_READY suffix) into a single identifier. Prior controller verdict conventions in this evidence chain separate the semantic verdict from the gate-routing suffix more cleanly (e.g., `ACCEPT_ROOT_CAUSE_PROVEN_READY_FOR_NO_LIVE_FIX_IMPLEMENTATION_GATE_NOT_READY` already pushes length limits, but this adds "FAIL_CLOSED_RESIDUAL" as an additional segment).

The verdict is not factually wrong, and every embedded concept is supported by the body. But the string is a presentation outlier that may complicate grep/search in future evidence chain reconstruction.

Severity: **Low**. Does not affect correctness, classification, or routing.

### F2 — Chapter 2 historical failure_subcategory vs terminal state distinction is elided (presentation)

The accepted facts table (Section 3) states for the Chapter 2 L1 evidence:

> Chapter 2 accepted and first failed chapter equal to Chapter 3.

This is correct for terminal state. However, `chapter-02.json` records `failure_subcategory: l1_numerical_closure` as a persistent field even though the chapter is now `accepted` with zero issues. This subcategory is a historical diagnostic (attempt 0 had a programmatic:L1 issue, repaired in attempt 1), not a current blocker. The target's phrasing is accurate for the disposition's purpose (the current first failed chapter IS Chapter 3), but a reader cross-referencing `chapter-02.json` might momentarily wonder why `failure_subcategory` is non-null on an accepted chapter.

The disposition's own evidence table (Section 4, row 5) correctly notes that Chapter 3 has no accepted draft/conclusion and that full LLM completion is not proven, which implicitly covers this distinction. No factual error.

Severity: **Low**. The target does not misrepresent the evidence; the summary is correct for disposition purposes.

## 4. Accepted Points

The following target claims were independently reproduced and confirmed:

### 4.1 Template truth fact: item_01 declares `block`

`docs/fund-analysis-template-draft.md` line 667: `"when_evidence_missing": "block"` for `ch3.required_output.item_01`. Confirmed against source. The target's Section 3 fact table correctly records this.

### 4.2 Evidence chain: old code_bug path is fixed, current behavior is fact_gap

Reproduced from the full accepted judgment chain:
- Root cause was `when_evidence_missing=null` causing provider-before `ValueError` (accepted at root-cause evidence judgment)
- Template fix at `6cd5ac5` changed to `when_evidence_missing="block"` (accepted at item 01 no-live fix judgment)
- Post-fix live evidence confirms Chapter 3 now blocks as `fact_gap` instead of `ValueError`/`code_bug` (accepted at item 01 post-fix live judgment)
- Chapter 2 L1 fix confirmed, Chapter 2 now accepted, first failed = Chapter 3 (accepted at Chapter 2 L1 post-fix live judgment)

The target correctly distinguishes old root cause (code_bug, now fixed) from current state (fact_gap, intentional policy).

### 4.3 Runtime metadata matches claimed state

Cross-verified against safe metadata:

| Target claim | Source | Match |
|---|---|---|
| Chapter 3 `status=blocked` | `summary.json` line 52, `chapter-03.json` line 118 | Exact |
| `stop_reason=missing_required_facts` | `summary.json` line 53, `chapter-03.json` line 119 | Exact |
| `failure_category=fact_gap` | `summary.json` line 51, `chapter-03.json` line 108 | Exact |
| Issue `3:missing_required_facts:writer:required_output_block:ch3.required_output.item_01` | `chapter-03.json` line 111 | Exact |
| `orchestration_status=partial` | `manifest.json` line 16, `summary.json` line 151 | Exact |
| `final_assembly_status=incomplete` | `manifest.json` line 14, `summary.json` line 142 | Exact |
| Chapter 3 no accepted draft/conclusion | `summary.json` chapter_matrix ch3: `accepted_draft_present: false`, `accepted_conclusion_present: false` | Exact |
| Chapter 2 accepted | `summary.json` chapter_matrix ch2: `status=accepted` | Exact |

### 4.4 Disposition classification is correct

The target's core classification — accept current fact_gap as intentional fail-closed residual, not a code bug — is the only classification consistent with the evidence:

- The old `ValueError`/`code_bug` path was caused by `when_evidence_missing=null` and has been fixed.
- The current `fact_gap`/`missing_required_facts` is the template's explicit `block` policy operating as designed.
- Treating this as a code bug would be incorrect (nothing is broken).
- Treating this as completion would be incorrect (Chapter 3 is blocked, no draft/conclusion, final assembly incomplete).

The routing to required-output policy planning (not implementation) is correct: the remaining question is a product policy decision (hard block vs evidence-gap paragraph vs minimum verification question), not a code fix.

### 4.5 No overclaiming detected

The target's Section 5 (Accepted/Rejected/Deferred Table) explicitly rejects:
- Release/readiness claim → REJECT ✓
- Immediate no-live code fix → REJECT ✓
- Bounded live re-evidence → REJECT ✓
- Source fallback / Eastmoney / CNINFO → REJECT ✓
- MVP-ready / LLM path ready → REJECT ✓

The target's Section 1 explicitly preserves EID single-source/no-fallback and `NOT_READY`.

The target's Section 7 (control-doc update recommendation) explicitly preserves these constraints in the next gate boundaries.

### 4.6 Residual routing is appropriate

The residuals table (Section 6) correctly assigns owners and distinguishes:
- Current blocker (Chapter 3 item 01 blocks completion) → policy planning gate
- Policy open question (hard block vs degrade) → same policy planning gate
- Deferred items (broader audit, multi-period LLM, release/readiness) → separate future gates

### 4.7 Design/control facts are correctly referenced

- Route C explicit opt-in and fail-closed: confirmed in `docs/design.md` lines 514, 517, 522
- `analyze-annual-period` is deterministic, not LLM route: confirmed in `docs/design.md` line 517
- Repair budget = 1 regenerate per chapter: confirmed in `docs/design.md` line 536, `docs/current-startup-packet.md` line 47
- EID single-source/no-fallback: confirmed in `AGENTS.md` fallback table, `docs/design.md` lines 654, 667-681

## 5. Residuals

| Residual | Severity | Handling |
|---|---|---|
| F1 verbose verdict string | Low | Accept as-is; does not affect correctness. Future dispositions may prefer shorter verdicts for grep/search consistency. |
| F2 elided historical subcategory distinction | Low | Accept as-is; the terminal-state summary is correct for disposition purposes. |

No blocking findings. No correctness issues. No scope-boundary violations.

## 6. Verdict

**PASS_WITH_FINDINGS**

The target artifact correctly classifies Chapter 3 item 01 `fact_gap` as an accepted fail-closed residual and correctly routes to required-output policy planning. It does not overclaim readiness, implementation authorization, live re-run authority, source fallback, or release state. The two findings are low-severity presentation observations that do not affect the correctness of the classification, routing, or boundary preservation.
