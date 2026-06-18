# Provider/LLM Chapter 3 Item 01 Post-fix Bounded Live Re-evidence — MiMo Review

Date: 2026-06-14

## Gate

`Provider/LLM Chapter 3 Item 01 Post-fix Bounded Live Re-evidence Gate`

## Review Input

- Evidence artifact: `docs/reviews/provider-llm-chapter3-item01-post-fix-bounded-live-re-evidence-20260614.md`
- Accepted implementation judgment: `docs/reviews/provider-llm-chapter3-required-output-item01-missing-evidence-no-live-fix-implementation-controller-judgment-20260614.md`
- Accepted implementation checkpoint: `6cd5ac5`
- Runtime artifact: `reports/llm-runs/004393-2025-20260613T190605Z-host_run_3870105453bd4f2/`

## Findings

### Finding 1 (Minor — Presentation): Chapter 3 Disposition Table "Evidence" Column Conflates failure_category with terminal_issue_class

**Location**: Evidence artifact, Disposition table, row 1 "Did the item 01 fix remove the provider-before ValueError / code_bug failure for Chapter 3?"

**Observation**: The Evidence column states:

> Chapter 3 is now `blocked/missing_required_facts/fact_gap`, terminal issue class is `null`, issue is `required_output_block:ch3.required_output.item_01`.

The notation `blocked/missing_required_facts/fact_gap` is a shorthand for `status/stop_reason/failure_category`. This is internally consistent with the source metadata, but the subsequent phrase "terminal issue class is `null`" may create a reading that `fact_gap` is the terminal issue class. Source metadata (`chapter-03.json`) shows:

- `failure_category`: `"fact_gap"`
- `terminal_failure_category`: `"fact_gap"`
- `terminal_issue_class`: `null`

The shorthand is accurate; the finding is only that a reader unfamiliar with the schema could misread `fact_gap` as the terminal issue class value. No factual error.

**Disposition**: Presentation-only. No correction required for this gate.

### Finding 2 (Minor — Pre-flight): Preflight `pgrep` Results Not Individually Itemized

**Location**: Evidence artifact, Preflight facts section.

**Observation**: The Preflight section documents two `pgrep` commands (`pgrep -x fund-analysis`, `pgrep -x uv`) and states "No active `fund-analysis` process was found" and "No active `uv` process was found." These are correct conclusions, but the individual command exit codes (expected: `1` for no match) are not explicitly stated. The guardrail is satisfied by the combined statement.

**Disposition**: Pre-flight guardrail is met. No correction required.

### Finding 3 (Observation): Chapter 2 Runtime Diagnostic `max_output_chars=null` for Auditor Phase

**Location**: `chapters/chapter-02.json`, `runtime_diagnostics` array, both attempts.

**Observation**: Both Chapter 2 auditor-phase runtime diagnostics show `max_output_chars: null` and `response_chars: 22`. The writer phase was configured with `writer_max_output_chars: 12000` and produced `writer_response_chars: 2484` (attempt 0) / `1799` (attempt 1). The auditor-phase `max_output_chars: null` is a separate diagnostic field — it does not mean the writer lacked an output budget. The evidence artifact correctly identifies this as a diagnostic-quality residual ("`max_output_chars=null` / provider runtime metadata unknown fields for auditor/programmatic phases").

**Disposition**: Correctly classified as residual. No finding correction required.

## Cross-Check: Evidence vs Source Metadata

| Claim in Evidence Artifact | Source Metadata | Status |
|---|---|---|
| Chapter 3 `status=blocked`, `stop_reason=missing_required_facts`, `failure_category=fact_gap` | `chapter-03.json`: `status: "blocked"`, `stop_reason: "missing_required_facts"`, `failure_category: "fact_gap"` | CONFIRMED |
| Chapter 3 `terminal_issue_class=null` | `chapter-03.json`: `terminal_issue_class: null` | CONFIRMED |
| Chapter 3 issue: `required_output_block:ch3.required_output.item_01` | `chapter-03.json` `writer_issues[0].issue_id: "writer:required_output_block:ch3.required_output.item_01"` — issues array: `"3:missing_required_facts:writer:required_output_block:ch3.required_output.item_01"` | CONFIRMED |
| Chapter 3 runtime diagnostic: writer operation, `finish_reason=null`, `response_chars=null` | `chapter-03.json` `runtime_diagnostics[0]`: `operation: "writer"`, `finish_reason: null`, `response_chars: null` | CONFIRMED (no provider call) |
| Exit code 1, orchestration partial, final assembly incomplete | CLI output and `manifest.json`: `orchestration_status: "partial"`, `final_assembly_status: "incomplete"` | CONFIRMED |
| First failed chapter: Chapter 2, `repair_budget_exhausted`, `prompt_contract`, `l1_numerical_closure` | `summary.json` `first_failed`: `chapter_id: 2`, `stop_reason: "repair_budget_exhausted"`, `failure_category: "prompt_contract"`, `failure_subcategory: "l1_numerical_closure"` | CONFIRMED |
| Chapter 2 attempt count 2, both with `programmatic:L1` issue | `chapter-02.json`: 2 attempts, each with `programmatic_issues` containing `programmatic:L1:line:*`, `l1_numerical_closure_count: 1` | CONFIRMED |
| Chapters 1, 4, 5, 6 accepted | `summary.json` `chapter_matrix`: ch1 accepted, ch4-6 accepted | CONFIRMED |
| 8 blocking final assembly issues | `summary.json` `final_assembly_issues`: 8 entries, all `severity: "blocking"` | CONFIRMED |
| Runtime artifact schema: `llm_incomplete_run_artifact_manifest.v1` | `manifest.json`: `schema_version: "llm_incomplete_run_artifact_manifest.v1"` | CONFIRMED |
| `diagnostic_consistency_status: "consistent"` for ch2 and ch3 | Both `chapter-02.json` and `chapter-03.json`: `diagnostic_consistency_status: "consistent"` | CONFIRMED |
| EID single-source/no-fallback preserved | No source/fallback/provider change in evidence; consistent with gate guardrails | CONFIRMED |
| Release/readiness remains NOT_READY | Evidence artifact verdict: `NOT_READY`; no readiness claim made | CONFIRMED |

## Verdict

**PASS_WITH_FINDINGS**

All five disposition answers in the evidence artifact are correctly supported by the source metadata. The item 01 live fix is confirmed: Chapter 3 now blocks at the template level (`missing_required_facts` / `fact_gap`) with no provider call, rather than raising a provider-before `ValueError` / `code_bug`. Full LLM completion remains unproven (exit 1, partial, incomplete). The strongest next blocker is correctly identified as Chapter 2 `prompt_contract/l1_numerical_closure` with `repair_budget_exhausted`. Release/readiness remains `NOT_READY`.

Three minor findings are noted: one presentation ambiguity in the Chapter 3 disposition table shorthand (Finding 1), one pre-flight itemization gap (Finding 2), and one observation confirming the existing diagnostic-quality residual classification (Finding 3). None affect the correctness of the disposition or the verdict.
