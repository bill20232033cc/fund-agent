# Provider/LLM Chapter 2 L1 Post-fix Bounded Live Re-evidence — MiMo Review

Date: 2026-06-14
Reviewer: AgentMiMo (evidence reviewer role)
Target: `docs/reviews/provider-llm-chapter2-l1-post-fix-bounded-live-re-evidence-20260614.md`
Gate: `Provider/LLM Chapter 2 L1 Post-fix Bounded Live Re-evidence Gate`

## Review Checklist

### 1. Does evidence accurately report the live command and exit code?

**PASS_WITH_FINDINGS.**

The evidence reports the command string with all environment variables and the `004393 / 2025` Route C arguments. The manifest safe metadata confirms `cli_command="analyze --use-llm"`, `fund_code=004393`, `report_year=2025`, `orchestration_status=partial`, `final_assembly_status=incomplete`, `trigger=use_llm_incomplete` — consistent with an incomplete LLM run.

The evidence states exit code `1`. The safe metadata files (`manifest.json`, `summary.json`) do not contain an explicit `exit_code` field. However, the manifest's `trigger=use_llm_incomplete` and `final_assembly_status=incomplete` are consistent with a non-zero exit. The exit code claim is a live command observation, not a safe metadata fact; this is standard for bounded live evidence gates and does not constitute a metadata fabrication.

### 2. Does safe metadata support that Chapter 2 is now accepted in this run?

**PASS.**

Summary `chapter_matrix` entry for chapter 2:
- `status=accepted`
- `stop_reason=none`
- `failure_category=null`
- `failure_subcategory=l1_numerical_closure`
- `attempt_count=2`

Chapter 2 safe metadata (`chapter-02.json`):
- `status=accepted`
- `stop_reason=none`
- `failure_category=null`
- `failure_subcategory=l1_numerical_closure`
- `diagnostic_consistency_status=consistent`
- `issues=[]` (empty)

The evidence correctly reports Chapter 2 as `accepted` with `l1_numerical_closure` residual subcategory and 2 attempts. This confirms the L1 fix is effective in this run — Chapter 2 no longer blocks as `repair_budget_exhausted`.

### 3. Does evidence avoid claiming Chapter 2 content correctness/readiness?

**PASS.**

The disposition table explicitly states:
- `Chapter 2 full content correctness | NOT_CLAIMED | This gate read only safe metadata, not accepted draft/report body.`
- `Release/readiness | NOT_READY | Single live evidence does not prove readiness.`

No content quality, draft body, or readiness claim is made.

### 4. Does safe metadata support that first failed chapter is Chapter 3 fact_gap/missing_required_facts?

**PASS.**

Summary `first_failed`:
- `chapter_id=3`
- `status=blocked`
- `stop_reason=missing_required_facts`
- `failure_category=fact_gap`
- `failure_subcategory=null`

Chapter 3 safe metadata (`chapter-03.json`):
- `status=blocked`
- `stop_reason=missing_required_facts`
- `failure_category=fact_gap`
- `failure_subcategory=null`
- `diagnostic_consistency_status=consistent`
- `issues=["3:missing_required_facts:writer:required_output_block:ch3.required_output.item_01"]`
- `chapter_runtime_diagnostics[0].operation="writer"`
- `chapter_runtime_diagnostics[0].provider_attempt_index=null`

The evidence correctly identifies Chapter 3 `missing_required_facts` / `fact_gap` as the first failed chapter and the specific issue `ch3.required_output.item_01`.

### 5. Does evidence preserve EID single-source/no-fallback and NOT_READY?

**PASS.**

The evidence states in Scope: "Release/readiness remains `NOT_READY`. Annual-report access remains EID single-source/no-fallback."

The disposition table confirms:
- `Release/readiness | NOT_READY`
- `Provider/LLM full completion | REJECT_AS_NOT_PROVEN`

No fallback, source expansion, readiness claim or readiness change is made.

### 6. Did it avoid forbidden body reads and provider payload reads?

**PASS.**

The "Safe Metadata Read" section explicitly lists which files were read (manifest, summary, chapter-02.json, chapter-03.json) and which were not (writer draft, repair Markdown, auditor feedback, raw prompts, provider payloads/responses, source/cache/PDF bodies, final report body).

The chapter-02.json and chapter-03.json files contain only safe scalar/null metadata and diagnostics — no provider response content, no writer/auditor draft bodies, no prompt bodies.

### 7. Is next gate recommendation reasonable and not over-broad?

**PASS.**

The evidence recommends `Provider/LLM Chapter 3 Item 01 Fact-gap Disposition Gate` with clear scope: "decide whether Chapter 3 item 01 fact-gap remains an accepted residual, needs no-live data/projection diagnostics, or requires a narrow template/required-output policy adjustment. It must not reintroduce provider/source fallback or claim readiness."

This is a reasonable next step given the current blocker is Chapter 3 fact_gap, and the recommendation correctly scopes the gate boundary.

## Findings

### Finding 1: Factual inaccuracy in prompt_contract_diagnostics description

**Severity: Minor (factual error, does not invalidate evidence)**

Section "Chapter 2 safe metadata" states:

> Prompt-contract diagnostics still record an earlier `programmatic:L1` phase with `l1_numerical_closure_count=1`

Actual safe metadata (`chapter-02.json`, `chapter_prompt_contract_diagnostics[0]`):
- `phase = "programmatic_audit"` (not "programmatic:L1")
- `issue_id_prefix_counts = {"programmatic:L1": 1}` — this is the issue ID prefix, not the phase
- `l1_numerical_closure_count = 1` — this is correct
- `primary_subcategory = "l1_numerical_closure"` — this is correct

The "programmatic:L1" is an issue ID prefix within `issue_id_prefix_counts`, not the diagnostic phase. The phase is `"programmatic_audit"`. The evidence conflates the issue ID prefix with the phase name.

**Impact:** Low. The factual conclusion (Chapter 2 accepted with l1_numerical_closure residual, 2 attempts) is correct. The inaccuracy is in the descriptive detail of which diagnostic phase recorded the finding, not in the outcome.

**Recommendation:** Correct the description to: "Prompt-contract diagnostics (`phase=programmatic_audit`) still record `l1_numerical_closure_count=1` in `issue_id_prefix_counts['programmatic:L1']`."

### Finding 2: Minor imprecision in "provider attempt fields are null" statements

**Severity: Cosmetic**

The evidence states "provider attempt fields are null" for both Chapter 2 and Chapter 3. Actual safe metadata:

- Chapter 2 `chapter_runtime_diagnostics[0]`: `provider_attempt_index=null`, `provider_max_attempts=null` (correct), but `finish_reason="stop"`, `response_chars=22` are non-null.
- Chapter 3 `chapter_runtime_diagnostics[0]`: `provider_attempt_index=null`, `provider_max_attempts=null` (correct), but `operation="writer"` is non-null.

The phrase "provider attempt fields are null" is technically accurate for the specific provider-attempt fields, but could be read as implying all runtime diagnostic fields are null.

**Impact:** Cosmetic. Does not affect evidence validity.

## Verification Summary

| Review Focus | Verdict |
|---|---|
| Live command and exit code accuracy | PASS_WITH_FINDINGS (exit code not in safe metadata, consistent with incomplete status) |
| Chapter 2 accepted in this run | PASS |
| No Chapter 2 content correctness claim | PASS |
| Chapter 3 first failed as fact_gap | PASS |
| EID single-source/no-fallback and NOT_READY preserved | PASS |
| No forbidden body/payload reads | PASS |
| Next gate recommendation reasonable | PASS |

## Final Verdict

**VERDICT: PASS_WITH_FINDINGS**

The evidence artifact accurately captures the live command result and safe metadata facts. Chapter 2 is confirmed as `accepted` (2 attempts, `l1_numerical_closure` residual) and Chapter 3 is confirmed as the first failed chapter (`missing_required_facts` / `fact_gap`). EID single-source/no-fallback and `NOT_READY` are preserved. No forbidden reads occurred. One minor factual inaccuracy in the prompt_contract_diagnostics description (phase name vs issue ID prefix) should be corrected but does not invalidate the evidence.
