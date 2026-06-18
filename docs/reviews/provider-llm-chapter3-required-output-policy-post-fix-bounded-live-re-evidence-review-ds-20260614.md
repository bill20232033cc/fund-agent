# Provider/LLM Chapter 3 Required-output Policy Post-fix Bounded Live Re-evidence — DS Review

Date: 2026-06-14
Role: AgentDS — independent evidence review
Gate: `Provider/LLM Chapter 3 Required-output Policy Post-fix Bounded Live Re-evidence Gate`

## Scope

This review assesses the bounded live re-evidence at `docs/reviews/provider-llm-chapter3-required-output-policy-post-fix-bounded-live-re-evidence-20260614.md` for correctness, boundary compliance, and overclaim. It does not re-run live/provider/LLM/network/source/PDF commands, does not read forbidden files, and does not change source policy, provider defaults, repair budget, readiness, release or PR state.

## Evidence Reviewed

- Primary evidence: `docs/reviews/provider-llm-chapter3-required-output-policy-post-fix-bounded-live-re-evidence-20260614.md`
- Required inputs: `AGENTS.md`, `docs/current-startup-packet.md`, `docs/implementation-control.md`, `docs/reviews/provider-llm-chapter3-required-output-policy-no-live-implementation-controller-judgment-20260614.md`
- Safe metadata cross-validation:
  - `reports/llm-runs/004393-2025-20260613T211325Z-host_run_605e381de24f4ab/manifest.json`
  - `reports/llm-runs/004393-2025-20260613T211325Z-host_run_605e381de24f4ab/summary.json`
  - `reports/llm-runs/004393-2025-20260613T211325Z-host_run_605e381de24f4ab/chapters/chapter-02.json`
  - `reports/llm-runs/004393-2025-20260613T211325Z-host_run_605e381de24f4ab/chapters/chapter-03.json`
  - `reports/llm-runs/004393-2025-20260613T211325Z-host_run_605e381de24f4ab/chapters/chapter-05.json`

No writer Markdown, auditor feedback, repair Markdown, raw prompts, provider payloads, source/PDF/cache body, or final report body were read.

## Findings

### F1 (PASS) Chapter 3 accepted — item 01 no longer blocks

The evidence claims Chapter 3 `status=accepted`, no provider-before `ValueError`/`code_bug`, item 01 now degrades to an evidence gap. Cross-validation against `chapter-03.json` confirms:

- `status: "accepted"`, `accepted: true`, `issues: []`, `stop_reason: "none"`
- `failure_category: null`, `failure_subcategory: null`
- Writer completed: `writer_finish_reason: "stop"`, `writer_response_chars: 2739`, `writer_max_output_chars: 12000`
- Auditor passed: `audit_status: "pass"`, `audit_accepted: true`
- Zero `programmatic_issues`, zero `llm_issues`

The `writer_max_output_chars: 12000` (not `null`) confirms the env var fix from checkpoint `1b9cd00` propagated. The prior `item_01` provider-before `ValueError` is not reproduced. This is a single bounded live sample — not general proof, and the evidence does not claim otherwise.

**Verdict: CONFIRMED.** The safe metadata directly supports the claim.

### F2 (PASS) Chapter 2 L1 regression correctly identified as current blocker

The evidence claims first failed chapter is Chapter 2 with `prompt_contract/l1_numerical_closure`. Cross-validation confirms:

- `summary.json.first_failed.chapter_id: 2`, `failure_category: "prompt_contract"`, `failure_subcategory: "l1_numerical_closure"`
- `chapter-02.json`: `status: "failed"`, `stop_reason: "repair_budget_exhausted"`
- Both attempts (index 0 and 1) show 2× `programmatic:L1` issues each — R=A+B-C numerical closure assertions missing adjacent anchor markers
- `provider_attempt_count: 0` — failure is pre-provider (programmatic audit), confirming fail-closed

**Verdict: CONFIRMED.** However, see F5 regarding prior accepted Chapter 2 evidence.

### F3 (PASS) Chapter 5 forbidden_phrase correctly identified as additional blocked chapter

The evidence claims Chapter 5 is blocked with `audit_parse/forbidden_phrase`. Cross-validation confirms:

- `chapter-05.json`: `status: "blocked"`, `stop_reason: "llm_contract_violation"`, `failure_category: "audit_parse"`, `failure_subcategory: "forbidden_phrase"`
- Attempt 0: auditor parse failure (`llm:parse_failure` / `C1`)
- Attempt 1: writer blocked with `writer:forbidden_phrase:7` (禁用措辞：减仓), `writer_max_output_chars: 12000`

**Verdict: CONFIRMED.**

### F4 (PASS) Final assembly correctly blocked, redaction applied

Evidence claims `orchestration_status=partial`, `final_assembly_status=incomplete`, `redaction_applied=true`. Cross-validation confirms:

- `manifest.json`: `orchestration_status: "partial"`, `final_assembly_status: "incomplete"`, `redaction_applied: true`, `redaction_count: 1`
- `summary.json`: 8 `final_assembly_issues`, all severity `blocking`, covering Chapter 2 missing draft/conclusion, Chapter 5 missing draft/conclusion, Chapter 7 readiness blocked, and orchestration not accepted

**Verdict: CONFIRMED.**

### F5 (INFO) Chapter 2 L1 regression vs prior accepted live evidence

Chapter 2 L1 was previously accepted in bounded live evidence at checkpoint `765c616` (controller judgment `docs/reviews/provider-llm-chapter2-l1-post-fix-bounded-live-re-evidence-controller-judgment-20260614.md`, verdict `ACCEPT_LIVE_CHAPTER2_L1_FIX_CONFIRMED_CHAPTER3_FACT_GAP_NOT_READY`). In that run, Chapter 2 was `accepted`. In this run, Chapter 2 again fails with the same `programmatic:L1` root cause.

This does not invalidate the current evidence — the evidence correctly reports what happened. But it means the Chapter 2 L1 fix may be fragile or sensitive to LLM output variation in the writer phase. The next gate recommendation (`Provider/LLM Chapter 2 L1 Numerical Closure Live-regression Disposition Gate`) should explicitly require reconciliation with the prior accepted live evidence at `765c616` to determine whether:

- The fix at `842362d` needs strengthening (the L1 check is on writer output, which varies per LLM run)
- The prior passing run was a lucky draw
- A different Chapter 2 failure mode has emerged under the same L1 classification

This is an informational finding for the controller, not a blocker for this gate's acceptance.

### F6 (PASS) Safe-read boundaries respected

The evidence document explicitly enumerates which files were read (manifest, summary, chapter-02/03/05 JSONs) and which were not read (writer Markdown, auditor feedback, repair Markdown, raw prompts, provider payloads, source/PDF/cache body, final report body). My independent cross-validation used only the same allowed safe metadata files and confirms the evidence claims without needing any forbidden reads.

**Verdict: CONFIRMED.** No boundary violation observed.

### F7 (PASS) No overclaim of provider/LLM readiness or release readiness

The evidence explicitly states:
- Exit code `1`, final assembly incomplete
- `REJECT_AS_UNPROVEN` for provider/LLM full completion
- `NOT_READY` for release/readiness
- `UNCHANGED` for source/fallback policy
- Verdict `LIVE_FAIL_CLOSED_CHAPTER3_ACCEPTED_NEW_BLOCKERS_NOT_READY`

No claim of MVP-ready, LLM-path-ready, or release-ready is made. EID single-source/no-fallback is explicitly preserved.

**Verdict: CONFIRMED.**

### F8 (PASS) Chapter matrix accurately reported

The evidence document's chapter matrix (6 chapters, each with status/stop_reason/category/subcategory/attempts) was cross-validated against `summary.json.chapter_matrix` and individual chapter JSONs. All 6 × 5 = 30 cells match the source data exactly.

**Verdict: CONFIRMED.**

### F9 (INFO) Acceptable scope limitation — other chapters not inspected

Chapters 1, 4, 6 were not read as individual JSON files. The `summary.json` chapter_matrix shows all three as `accepted` with `stop_reason: "none"` and `failure_category: null`. The evidence document correctly reports them as accepted in its chapter matrix. Reading their individual JSONs would be redundant for the current gate's purpose (determining whether Chapter 3 item 01 no longer blocks). This is not a boundary violation — it is reasonable scope management.

**Verdict: ACCEPTABLE.** Not a finding against the evidence.

## Residuals

| Residual | Severity | Notes |
|---|---|---|
| Chapter 2 L1 regression vs prior accepted evidence at `765c616` | Medium — needs controller attention in next gate | The L1 fix may need hardening; the next disposition gate should reconcile with prior live evidence |
| Chapter 5 forbidden_phrase (`减仓`) | Low — correctly deferred | Separate residual; does not affect current gate's Chapter 3 question |
| Provider/LLM full completion unproven | Accepted residual | Exit code `1`, incomplete assembly; expected and correctly reported |
| Single-sample limitation | Inherent | One bounded `004393 / 2025` run is not general proof; evidence correctly scopes this |

## Verdict

**PASS**

The evidence directly and accurately supports that Chapter 3 item 01 no longer blocks and Chapter 3 is accepted in this bounded live sample. All claims are verified against safe runtime metadata. No overclaim, no boundary violation, and no readiness/release claim is made. The Chapter 2 L1 regression (F5) is an informational finding for the controller's next gate, not a blocker for accepting this evidence.

Recommended controller action: ACCEPT the live evidence with the Chapter 2 L1 regression noted as a residual requiring reconciliation with prior accepted evidence at `765c616` in the next disposition gate.
