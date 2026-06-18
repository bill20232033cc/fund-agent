# Provider/LLM Chapter 6 Invalid-marker Live-blocker Disposition Plan Review (MiMo)

Date: 2026-06-14

Role: AgentMiMo independent plan reviewer

Gate: `Provider/LLM Chapter 6 Invalid-marker Live-blocker Disposition Gate`

Review target: `docs/reviews/provider-llm-chapter6-invalid-marker-live-blocker-disposition-plan-20260614.md`

Verdict: `ACCEPT`

## 1. Scope

This is an independent plan review for the Chapter 6 `invalid_marker` live-blocker disposition artifact. The review checks boundary adherence, root-cause calibration, next-gate recommendation strength, hypothesis/residual/non-goal separation, and validation-check readiness.

No source, test, runtime, prompt, README, design, startup packet or implementation-control changes were made. No live/provider/LLM/network/PDF/FDR/source/analyze/checklist/readiness/release/PR commands were run. No writer/auditor/repair markdown bodies, prompt bodies, provider payloads, PDF/source/cache bodies, source bodies or final report body were read.

## 2. Evidence Reviewed

| Evidence | Use |
|---|---|
| `AGENTS.md` | Execution truth, role boundary, EID single-source/no-fallback policy and `NOT_READY` preservation. |
| `docs/current-startup-packet.md` | Current active gate and accepted checkpoint context. |
| `docs/implementation-control.md` | Current control truth: Chapter 6 invalid-marker disposition is the active no-code planning gate. |
| `docs/reviews/provider-llm-chapter2-l1-deterministic-gap-rendering-post-fix-bounded-live-re-evidence-controller-judgment-20260614.md` | Controller-accepted live fact: Chapter 6 `invalid_marker` is the new current blocker. |
| `docs/reviews/provider-llm-chapter2-l1-deterministic-gap-rendering-post-fix-bounded-live-re-evidence-20260614.md` | Live evidence artifact: exact run path, safe metadata boundary and final assembly blocker summary. |
| `docs/reviews/provider-llm-chapter6-invalid-marker-live-blocker-disposition-plan-20260614.md` | Plan under review. |
| `reports/llm-runs/004393-2025-20260613T231426Z-host_run_8bbf668bcf7644e/manifest.json` | Safe metadata cross-check: run identity and partial/incomplete status. |
| `reports/llm-runs/004393-2025-20260613T231426Z-host_run_8bbf668bcf7644e/summary.json` | Safe metadata cross-check: chapter matrix, prompt-contract diagnostics and runtime diagnostics. |
| `reports/llm-runs/004393-2025-20260613T231426Z-host_run_8bbf668bcf7644e/chapters/chapter-06.json` | Safe metadata cross-check: Chapter 6 issue IDs, diagnostic counters and issue offsets. |

## 3. Findings

### Review Question 1: Safe metadata and no-code disposition boundary

The plan reads the following source files: `fund_agent/fund/chapter_writer.py` (marker validation and prompt-contract mechanics only), `tests/fund/test_chapter_writer.py` and `tests/services/test_chapter_orchestrator.py` (existing invalid-marker / unknown-anchor taxonomy coverage only).

The gate description says "no-code disposition/root-cause planning gate" — meaning no code changes, not no code reading. The plan explicitly scopes these reads to mechanics understanding only and does not modify any file. The plan also explicitly states "Not read: writer/auditor/repair markdown bodies, prompt bodies, provider payloads, PDF/source/cache bodies, source bodies or final report body."

Safe metadata cross-check confirms all facts in Section 3 "Accepted Facts" match the actual manifest.json, summary.json and chapter-06.json:
- `orchestration_status=partial`, `final_assembly_status=incomplete` ✓
- Chapter 6 `status=blocked`, `stop_reason=llm_contract_violation`, `failure_category=prompt_contract`, `failure_subcategory=invalid_marker` ✓
- `phase=writer_parse`, `invalid_marker_count=4`, `issue_id_prefix_counts={"writer:invalid_anchor_marker": 4}` ✓
- `unknown_anchor_count=0`, `required_output_missing_count=0`, `required_structure_missing_count=0`, `forbidden_phrase_count=0`, `response_length_incomplete_count=0` ✓
- `finish_reason=stop`, `max_output_chars=12000`, `response_chars=3120` ✓
- Four `writer:invalid_anchor_marker` issues at offsets 63, 711, 1095, 1521 with empty `anchor_ids` and `fact_ids` ✓
- `provider_attempt_count=0` in runtime diagnostics ✓

**No finding.** The plan stays inside the safe metadata and no-code disposition boundary.

### Review Question 2: Root-cause classification calibration

The plan classifies the strongest current root-cause category as `LLM output-format noncompliance with existing anchor marker contract`, with `missing no-live reproducer/diagnostic evidence` as the accepted evidence gap.

Calibration is well-supported:
- The live metadata strongly indicates marker-format rejection (4 invalid markers, zero unknown anchors, zero missing structure/output, zero forbidden phrases, zero truncation, finish_reason=stop).
- The plan correctly distinguishes invalid-marker from unknown-anchor: the existing parser separates syntactically invalid markers (`invalid_marker`) from valid-but-unauthorized anchor IDs (`unknown_anchor`), and the live metadata confirms `unknown_anchor_count=0`.
- The plan correctly acknowledges the evidence gap: the actual malformed marker strings, rendered Chapter 6 prompt body, allowed anchor list, and provider output body were not read.
- The plan does not over-claim: it says "not yet enough to authorize a concrete fix."

**No finding.** The root-cause classification is properly calibrated.

### Review Question 3: Next-gate recommendation strength

The plan recommends `no-live diagnostic evidence gate` as the next gate. The alternatives considered and rejected:
- No-live fix planning: rejected because the exact malformed marker pattern is unknown and direct fix-surface attribution remains under-proven.
- Another bounded live command: rejected because a live sample already exposed the blocker; another run would likely spend provider budget without isolating root cause.
- Blocked: rejected because current policy already says exact marker contract is fail-closed; no product decision is needed to collect no-live diagnostics.

The recommendation is well-supported: the live metadata is strong enough to route away from source/provider/fallback/readiness/live repetition and toward marker-contract mechanics, but not strong enough to choose a fix surface.

**No finding.** The recommended next gate is better supported than the alternatives.

### Review Question 4: Hypothesis/residual/non-goal separation

The plan has clean separation:
- Section 4 "Hypothesis Disposition Table": six hypotheses with explicit dispositions (`STRONGEST_CURRENT_ROOT_CAUSE_CATEGORY`, `POSSIBLE_CONTRIBUTOR_UNPROVEN`, `WEAK_UNPROVEN`, `ACCEPTED_EVIDENCE_GAP`, `REJECTED_FOR_NEXT_GATE`).
- Section 6 "Non-goals and Deferred Gates": explicit list of what is out of scope.
- Residuals are implicitly carried through the hypothesis dispositions and the recommended next gate.

Each hypothesis has "Evidence for" and "Evidence against / gap" columns, providing balanced analysis.

**No finding.** The separation is clean enough for controller acceptance.

### Review Question 5: D1-D5 validation check readiness

| Check | Assessment |
|---|---|
| D1 Chapter 6 prompt contract rendering | Specific: inspect no-live rendered Chapter 6 writer prompt from fixture/fake typed inputs; record whether exact marker format, allowed-anchor set language and Chapter 6 bond-risk internal-anchor prohibition are present. |
| D2 Validator taxonomy | Specific: use fake LLM/no-live writer inputs to show malformed anchor comments route to `invalid_marker` and valid syntax with unauthorized IDs routes to `unknown_anchor`. |
| D3 Diagnostic payload mapping | Specific: verify orchestrator diagnostics count `writer:invalid_anchor_marker` as `invalid_marker_count` and do not leak raw marker suffixes. |
| D4 Repair-context specificity | Specific: inspect no-live repair-context text for `invalid_marker` and determine whether it tells the next writer attempt to use exact marker syntax. |
| D5 Boundary preservation | Specific: confirm no live/provider/PDF/source/fallback/readiness/release commands and no body reads outside the next gate's explicit authorization. |

D1-D4 are concrete enough for the next gate's validation worker to execute. D5 is a standard boundary guard. Acceptance criteria in Section 7 provide routing rules for different D1-D4 outcomes.

**No finding.** D1-D5 are specific and code-generation/evidence-generation ready.

## 4. Verdict

NO BLOCKING FINDINGS.

`VERDICT: ACCEPT`

The plan correctly classifies the Chapter 6 `invalid_marker` first-failed blocker, stays within the safe metadata and no-code disposition boundary, calibrates the root-cause classification appropriately, recommends the best-supported next gate, separates hypotheses/residuals/non-goals cleanly, and provides D1-D5 validation checks that are specific enough for the next gate.

Release/readiness remains: `NOT_READY`
