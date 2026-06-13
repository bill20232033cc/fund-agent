# Provider/LLM Chapter 6 Invalid-marker Live-blocker Disposition Plan

Date: 2026-06-14

Role: AgentCodex disposition/planning worker

Gate: `Provider/LLM Chapter 6 Invalid-marker Live-blocker Disposition Gate`

Verdict: `RECOMMEND_NO_LIVE_DIAGNOSTIC_EVIDENCE_GATE_NOT_READY`

Release/readiness: `NOT_READY`

## 1. Scope

This artifact classifies the current strongest root-cause category for the Chapter 6 `invalid_marker` first-failed live blocker after the accepted Chapter 2 deterministic gap rendering post-fix bounded live evidence.

This is a disposition/planning artifact only. It does not implement fixes, change tests, change runtime behavior, change prompts, change provider configuration, run live/provider commands, or claim release/readiness.

EID source policy remains single-source/no-fallback. Eastmoney, fund-company, CNINFO and all other fallback routes remain out of scope.

## 2. Evidence Reviewed

| Evidence | Use |
|---|---|
| `AGENTS.md` | Execution truth, role boundary, EID single-source/no-fallback policy and `NOT_READY` preservation. |
| `docs/current-startup-packet.md` | Current active gate and accepted checkpoint context. |
| `docs/implementation-control.md` | Current control truth: Chapter 6 invalid-marker disposition is the active no-code planning gate. |
| `docs/reviews/provider-llm-chapter2-l1-deterministic-gap-rendering-post-fix-bounded-live-re-evidence-controller-judgment-20260614.md` | Controller-accepted live fact: Chapter 6 `invalid_marker` is the new current blocker. |
| `docs/reviews/provider-llm-chapter2-l1-deterministic-gap-rendering-post-fix-bounded-live-re-evidence-20260614.md` | Live evidence artifact: exact run path, safe metadata boundary and final assembly blocker summary. |
| `reports/llm-runs/004393-2025-20260613T231426Z-host_run_8bbf668bcf7644e/manifest.json` | Safe metadata only: run identity and partial/incomplete status. |
| `reports/llm-runs/004393-2025-20260613T231426Z-host_run_8bbf668bcf7644e/summary.json` | Safe metadata only: first failed chapter, chapter matrix, prompt-contract diagnostics and runtime diagnostics. |
| `reports/llm-runs/004393-2025-20260613T231426Z-host_run_8bbf668bcf7644e/chapters/chapter-06.json` | Safe metadata only: Chapter 6 issue IDs and diagnostic counters. |
| `fund_agent/fund/chapter_writer.py` | Marker validation and prompt-contract mechanics only. |
| `tests/fund/test_chapter_writer.py` and `tests/services/test_chapter_orchestrator.py` | Existing invalid-marker / unknown-anchor taxonomy coverage only. |

Not read: writer/auditor/repair markdown bodies, prompt bodies, provider payloads, PDF/source/cache bodies, source bodies or final report body.

No live/provider/LLM/network/PDF/FDR/source/analyze/checklist/readiness/release commands were run.

## 3. Accepted Facts

| Fact | Accepted disposition |
|---|---|
| The accepted live command exited `1`; `orchestration_status=partial`; `final_assembly_status=incomplete`. | Accepted live blocker fact only; not readiness evidence. |
| The first failed chapter is Chapter 6 with `status=blocked`, `stop_reason=llm_contract_violation`, `failure_category=prompt_contract`, `failure_subcategory=invalid_marker`. | Accepted current blocker. |
| Chapter 6 prompt-contract diagnostics show `phase=writer_parse`, `invalid_marker_count=4`, `issue_id_prefix_counts={"writer:invalid_anchor_marker": 4}`, `unknown_anchor_count=0`, `required_output_missing_count=0`, `required_structure_missing_count=0`, `forbidden_phrase_count=0`, `response_length_incomplete_count=0`, `finish_reason=stop`, `max_output_chars=12000`, `response_chars=3120`. | Strongly indicates marker-format rejection, not unknown anchor, missing structure, missing required output, forbidden phrase or truncation. |
| Chapter 6 issues are position-only safe metadata: `writer:invalid_anchor_marker` at four offsets. | Confirms invalid marker class without exposing body text. |
| Existing writer prompt protocol states evidence assertions must use `<!-- anchor:<anchor_id> -->`; allowed anchors are an allow-set, not a required full-use list. | Existing contract has an explicit marker format. |
| Existing validator detects HTML comments whose payload contains `anchor` but does not exactly match `<!-- anchor:<anchor_id> -->` as `writer:invalid_anchor_marker`. | Existing validation mechanics match the live diagnostic class. |
| Existing parser separately handles syntactically valid but unauthorized anchor IDs as `unknown_anchor`. | The live `unknown_anchor_count=0` makes unauthorized-anchor-ID the weaker category for this failure. |
| Existing tests cover invalid anchor marker syntax/case, Chapter 6 synthesized bond-risk anchors, and orchestrator taxonomy mapping. | There is some no-live coverage for mechanics, but not yet a current-run Chapter 6 diagnostic evidence artifact. |
| Safe metadata does not include the actual malformed marker strings, rendered Chapter 6 prompt body, allowed anchor list, or provider output body under this gate. | Direct fix-surface attribution remains under-proven. |

## 4. Hypothesis Disposition Table

| Hypothesis | Evidence for | Evidence against / gap | Disposition |
|---|---|---|---|
| LLM output-format noncompliance with existing anchor marker contract | Live metadata reports writer-parse `invalid_marker_count=4`, `writer:invalid_anchor_marker=4`, `finish_reason=stop`, no truncation, no structure/output missing; code contract requires exact `<!-- anchor:<anchor_id> -->`; validator and tests already distinguish invalid syntax from unknown anchor. | Body was not read, so the exact malformed marker pattern is unknown. | `STRONGEST_CURRENT_ROOT_CAUSE_CATEGORY`, but not yet enough to authorize a concrete fix. |
| Prompt/contract ambiguity for Chapter 6 allowed anchors or marker format | Chapter 6 has special bond-risk anchor constraints; prompt language includes both general allowed-anchor rules and Chapter 6 internal/组级 anchor warnings. | Static prompt code explicitly states exact anchor marker format and forbids synthesized/internal bond-risk anchors; existing tests assert Chapter 6 prompt contains that warning. No current evidence shows ambiguity rather than noncompliance. | `POSSIBLE_CONTRIBUTOR_UNPROVEN`; should be checked in no-live diagnostics before any fix plan. |
| Parser/validator over-strictness or bug | Validator is exact-format and fail-closed; strictness might be product-calibration relevant if LLM commonly varies marker case/spacing. | Existing contract explicitly requires exact format; tests cover invalid format fail-closed; live metadata has `unknown_anchor_count=0`, so parser did not confuse valid-but-unauthorized IDs with malformed syntax. No contradictory evidence. | `WEAK_UNPROVEN`; do not plan parser relaxation from current evidence. |
| Missing no-live reproducer/diagnostic evidence | Current proof is live-only safe metadata; actual malformed markers and rendered prompt body were not read; no Chapter 6-specific current-run no-live diagnostic artifact ties allowed-anchor rendering, validator taxonomy and repair/fix surface together. | Existing unit tests cover parts of the mechanics, but they are not this gate's current diagnostic evidence. | `ACCEPTED_EVIDENCE_GAP`; drives the recommended next gate. |
| Need for another bounded live command | A live sample already exposed the blocker and safe metadata gives enough routing signal. | Another live run would likely spend provider budget without isolating root cause; current gap is no-live reproducibility/diagnostic detail, not lack of another live occurrence. | `REJECTED_FOR_NEXT_GATE`. |
| Blocked pending user/product decision | Current policy already says exact marker contract is fail-closed; no product decision is needed to collect no-live diagnostics. | If a later gate wants to relax marker syntax, that would become a product/contract decision, but it is premature now. | `REJECTED_FOR_NEXT_GATE`. |

Current strongest root-cause category: `LLM output-format noncompliance with existing anchor marker contract`.

Current strongest disposition gap: `missing no-live reproducer/diagnostic evidence`.

## 5. Recommended Next Gate

Primary next gate: `no-live diagnostic evidence gate`.

Recommended gate name:

```text
Provider/LLM Chapter 6 Invalid-marker No-live Diagnostic Evidence Gate
```

Rationale:

The live metadata is strong enough to route away from source/provider/fallback/readiness/live repetition and toward marker-contract mechanics. It is not yet strong enough to choose a fix surface, because this gate did not read the Chapter 6 writer body, prompt body or provider payload and did not produce a current no-live diagnostic artifact.

The next gate should produce no-live evidence that answers exactly:

- whether Chapter 6 prompt rendering for the relevant fund type exposes the exact allowed marker format and allowed-anchor boundary clearly enough;
- whether synthetic malformed markers matching likely LLM deviations are classified as `invalid_marker` while valid-but-unauthorized marker IDs are classified as `unknown_anchor`;
- whether Chapter 6 bond-risk internal/组级 anchor guidance can plausibly cause marker-format confusion or only unauthorized-anchor confusion;
- whether repair-context routing for `invalid_marker` is specific enough to tell the next fix-planning gate what to change.

## 6. Non-goals and Deferred Gates

- No source, test, runtime, prompt, README, design, startup packet or implementation-control changes in this disposition gate.
- No live/provider/LLM/network/PDF/FDR/source/analyze/checklist/readiness/release commands.
- No provider default, repair budget, annual-period LLM route, Docling, EID source policy or fallback change.
- No Eastmoney, fund-company, CNINFO or other source fallback.
- No readiness, MVP-ready, LLM-path-ready, PR, push, merge or release claim.
- Parser relaxation, prompt rewrite, repair-budget change, marker-contract product change and additional bounded live evidence are deferred until after no-live diagnostics identify the narrow fix surface.

## 7. Validation Plan for Next Gate

The next no-live diagnostic evidence gate should remain read/evidence-only unless separately authorized. It should not modify production code or tests.

Minimum validation matrix:

| Check | Required evidence |
|---|---|
| D1 Chapter 6 prompt contract rendering | Inspect no-live rendered Chapter 6 writer prompt from fixture/fake typed inputs only; record whether exact `<!-- anchor:<anchor_id> -->`, allowed-anchor set language and Chapter 6 bond-risk internal-anchor prohibition are present. |
| D2 Validator taxonomy | Use fake LLM/no-live writer inputs to show malformed anchor comments route to `llm_contract_violation` / `invalid_marker`, and valid syntax with unauthorized IDs routes to `unknown_anchor`. |
| D3 Diagnostic payload mapping | Verify orchestrator/run-artifact diagnostics count `writer:invalid_anchor_marker` as `invalid_marker_count` and do not leak raw marker suffixes. |
| D4 Repair-context specificity | Inspect no-live repair-context text for `invalid_marker` and determine whether it tells the next writer attempt to use exact marker syntax, not merely "allowed anchor". |
| D5 Boundary preservation | Confirm no live/provider/PDF/source/fallback/readiness/release commands and no body reads outside the next gate's explicit authorization. |

Acceptance criteria for the next gate:

- If D1-D4 pass and no parser contradiction appears, route to a narrow no-live fix planning gate for prompt/repair instruction strengthening or output-format guardrail only.
- If D1 shows Chapter 6 prompt ambiguity specific to bond-risk anchors, route to no-live fix planning for prompt-contract clarification.
- If D2 shows accepted syntax is being rejected, route to parser/validator bug fix planning.
- If D4 shows repair instruction cannot correct invalid marker recurrence, route to repair-context fix planning.
- Do not route to additional bounded live evidence until a no-live fix is implemented and accepted.

## 8. Stop Condition

Stop after writing this artifact.

Final recommendation:

```text
no-live diagnostic evidence gate
```

Release/readiness remains:

```text
NOT_READY
```
