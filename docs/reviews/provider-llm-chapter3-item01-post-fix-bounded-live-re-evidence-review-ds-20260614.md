# Provider/LLM Chapter 3 Item 01 Post-fix Bounded Live Re-evidence — DS Review

Date: 2026-06-14
Reviewer: AgentDS
Role: Evidence reviewer
Gate: `Provider/LLM Chapter 3 Item 01 Post-fix Bounded Live Re-evidence Gate`

## Input Artifacts Reviewed

- Evidence: `docs/reviews/provider-llm-chapter3-item01-post-fix-bounded-live-re-evidence-20260614.md`
- Implementation checkpoint: `6cd5ac5`
- Controller judgment: `docs/reviews/provider-llm-chapter3-required-output-item01-missing-evidence-no-live-fix-implementation-controller-judgment-20260614.md`
- Runtime metadata: `manifest.json`, `summary.json`, `chapters/chapter-02.json`, `chapters/chapter-03.json`

## Allowed Checks Executed

- `git diff --check` — passed, no output
- `git status --short` — unrelated tracked diffs (AGENTS.md, README.md, docs/design.md) and untracked residue visible; no new changes from this gate
- `jq` metadata extraction from all four allowed JSON files

## Cross-check: Evidence Claims vs Runtime Metadata

### Claim 1: Chapter 3 is now blocked/missing_required_facts/fact_gap, not ValueError/code_bug

| Field | Evidence Claim | Runtime Truth | Match? |
|---|---|---|---|
| `status` | `blocked` | `blocked` | YES |
| `stop_reason` | `missing_required_facts` | `missing_required_facts` | YES |
| `failure_category` | `fact_gap` | `fact_gap` | YES |
| `terminal_issue_class` | `null` | `null` | YES |
| issue | `required_output_block:ch3.required_output.item_01` | `3:missing_required_facts:writer:required_output_block:ch3.required_output.item_01` | YES |
| `writer_status` | (implied blocked) | `blocked` | YES |
| `writer_stop_reason` | (implied missing_required_facts) | `missing_required_facts` | YES |
| provider attempt | (implied 0) | `provider_attempt_index: null`, `writer_max_output_chars: null`, `writer_response_chars: null` | YES |

**Finding**: The Chapter 3 writer now correctly blocks at fact-gap with explicit `required_output_block:ch3.required_output.item_01`, reason `missing_required_facts`. Zero provider attempt — the writer preflight correctly applies the template `when_evidence_missing="block"` rule and stops before any writer/provider call. The prior `ValueError` / `code_bug` path is not reproduced. This is confirmed live.

### Claim 2: Full LLM completion NOT accepted — exit 1, orchestration partial, final assembly incomplete

| Field | Evidence Claim | Runtime Truth | Match? |
|---|---|---|---|
| exit code | `1` | (from evidence CLI output) | YES |
| `orchestration_status` | `partial` | `partial` | YES |
| `final_assembly_status` | `incomplete` | `incomplete` | YES |
| Chapter 2 status | `failed` | `failed` | YES |
| Chapter 3 status | `blocked` | `blocked` | YES |
| Chapter 7 | blocked | `readiness_blocked` (8 blocking final assembly issues) | YES |

**Finding**: `summary.json` confirms 8 blocking final assembly issues including `orchestration_not_accepted`, `chapter_2:not_accepted`, `chapter_3:not_accepted`, and `chapter_7:readiness_blocked`. Routes C full completion remains unproven.

### Claim 3: Strongest next blocker is Chapter 2 prompt_contract/l1_numerical_closure repair_budget_exhausted

| Field | Evidence Claim | Runtime Truth | Match? |
|---|---|---|---|
| `first_failed.chapter_id` | `2` | `2` | YES |
| `first_failed.status` | `failed` | `failed` | YES |
| `first_failed.stop_reason` | `repair_budget_exhausted` | `repair_budget_exhausted` | YES |
| `first_failed.failure_category` | `prompt_contract` | `prompt_contract` | YES |
| `first_failed.failure_subcategory` | `l1_numerical_closure` | `l1_numerical_closure` | YES |
| `first_failed.attempt_count` | `2` | `2` | YES |

**Finding**: `first_failed` is consistent across `summary.json.first_failed`, `summary.json.runtime_diagnostics.first_failed`, and `summary.json.prompt_contract_diagnostics.first_failed`. All three sources agree Chapter 2 is the first/strongest blocker.

Chapter 2 detail from `chapter-02.json`:
- Attempt 0: `programmatic:L1:line:10:7d718f9164` → repair action `regenerate`
- Attempt 1: `programmatic:L1:line:26:02ea024a63` → repair action `stop`, reason "章节修复预算耗尽。"
- Both attempts: `l1_numerical_closure_count=1`, `response_chars=22` (auditor programmatic only)
- Both attempts: `writer_deleted_item_rule_ids: ["chapter_2_tracking_error_analysis"]`

### Claim 4: Release/readiness remains NOT_READY

This is a disposition claim consistent with exit code 1, partial orchestration, incomplete final assembly, and 2 of 6 chapters not accepted.

## Disposition Accuracy

| Disposition Question | Evidence Verdict | Reviewer Assessment |
|---|---|---|
| Did item 01 fix remove provider-before ValueError? | ACCEPTED | **Confirmed.** Chapter 3 writer now blocks at fact-gap with zero provider attempts. The template `when_evidence_missing="block"` is working in live execution. |
| Did Chapter 3 become accepted? | NOT ACCEPTED | **Correct.** Chapter 3 remains blocked with no accepted draft/conclusion. This is expected fail-closed behavior, not content acceptance. |
| Did whole LLM run complete? | NOT ACCEPTED | **Correct.** Exit 1, orchestration partial, final assembly incomplete. |
| Strongest current blocker? | ACCEPTED as Chapter 2 l1_numerical_closure | **Correct.** First failed chapter is 2, consistent across all three diagnostic sources. |
| Does this prove release/readiness? | REJECT | **Correct.** Readiness claim is unsupported by this evidence. |

## Guardrail Verification

| Guardrail | Status |
|---|---|
| EID single-source only | Preserved — no source/PDF/cache body read |
| No fallback introduced | Confirmed — no fallback invocation in runtime metadata |
| No source/PDF/cache body reads | Confirmed — only safe metadata from 4 JSON files |
| No chapter writer Markdown, auditor feedback, raw prompt, provider payload read | Confirmed |
| Release/readiness NOT_READY | Preserved |
| Gate scope bounded to exact 004393/2025 Route C | Respected |

## Findings

### F1: Item 01 fix confirmed live — no regression

The live evidence independently confirms the template fix at `6cd5ac5` works as designed. Chapter 3 writer correctly blocks at `required_output_block:ch3.required_output.item_01` with reason `missing_required_facts` and zero provider attempts. No `ValueError`, no `code_bug`, no `llm_exception`. The fail-closed behavior matches the no-live test expectation.

### F2: Chapter 2 writer deletes item rule in both attempts

`chapter-02.json` shows `writer_deleted_item_rule_ids: ["chapter_2_tracking_error_analysis"]` in both attempt 0 and attempt 1. This is outside the Chapter 3 item 01 gate scope, but the pattern of writers deleting contractually required item rules to pass the prompt contract may be relevant when investigating why the L1 numerical closure assertion keeps failing. The deleted rule relates to tracking error analysis — a quantitative item that could directly affect numerical closure assertions. Recommend the next Chapter 2 root-cause gate investigate whether this deletion pattern contributes to the l1_numerical_closure failures.

### F3: Chapter 2 attempt regression in evidence usage

Attempt 0 used 5 anchor IDs and 3 fact IDs. Attempt 1 (repair) used 4 anchor IDs and 2 fact IDs — dropping `annual_report:§2:50b9f3c4` anchor and `structured.benchmark` fact. The repair attempt produced fewer evidence citations while still failing the same L1 numerical closure check. This suggests the current repair strategy (full chapter regenerate) may not be producing incrementally better drafts for L1 closure purposes. Deferred to Chapter 2 root-cause gate.

### F4: Runtime diagnostic metadata incompleteness

The evidence artifact correctly flags `max_output_chars=null` for programmatic/auditor phases and several `null` provider runtime metadata fields. This is a known deferred diagnostic-quality residual and does not affect the item 01 disposition. Noted for completeness.

## Verdict

VERDICT: **PASS_WITH_FINDINGS**

The review input artifact faithfully reports runtime metadata from the allowed JSON sources. All four disposition questions are correctly answered against the evidence. Guardrails are respected. The item 01 template fix is confirmed working in live execution: Chapter 3 now blocks at fact-gap (not ValueError/code_bug) with zero provider attempts.

Findings F2 and F3 are observations about Chapter 2 behavior that may assist the next root-cause gate but do not weaken the current evidence or its dispositions. Finding F4 is a known deferred residual.

Recommended next gate: `Provider/LLM Chapter 2 L1 Numerical Closure Root-cause Planning Gate`, with explicit attention to the `writer_deleted_item_rule_ids` pattern and the repair strategy's evidence-usage regression.
