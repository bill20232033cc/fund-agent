# Provider/LLM Route Stabilization Closeout Controller Judgment

Date: 2026-06-14

Role: AgentController

Gate: `Route C post-live stabilization closeout / annual-report document representation route realignment`

Release/readiness: `NOT_READY`

## 1. Scope

This judgment closes the current Route C post-live stabilization loop at the control-plane level.

It accepts the existing Chapter 3 missing-required-marker no-live diagnostic evidence as diagnostic input, but rejects continuing the next Chapter 3 no-live fix planning gate as the default mainline.

No source, tests, runtime behavior, provider defaults, repair budget, source policy, fallback, production parser, Docling dependency, readiness, release, PR, stage, commit or push state is changed by this judgment.

## 2. Evidence Reviewed

- `AGENTS.md`
- `docs/design.md`
- `docs/implementation-control.md`
- `docs/current-startup-packet.md`
- `docs/reviews/provider-llm-chapter3-missing-required-marker-no-live-diagnostic-evidence-20260614.md`
- `docs/reviews/provider-llm-chapter3-missing-required-marker-no-live-diagnostic-evidence-review-ds-20260614.md`
- `docs/reviews/provider-llm-chapter3-missing-required-marker-no-live-diagnostic-evidence-review-mimo-20260614.md`
- Recent accepted Route C checkpoints listed in `docs/implementation-control.md` and `docs/current-startup-packet.md`

No live/provider/LLM/network/PDF/FDR/source/analyze/checklist/readiness/release/PR command was run for this closeout.

## 3. Accepted Current Facts

| Fact | Disposition | Basis |
|---|---|---|
| Current operational annual-report source remains EID single-source. | ACCEPT | `AGENTS.md`, `docs/design.md`, `docs/implementation-control.md` |
| Eastmoney, fund-company/CDN, CNINFO and other fallback routes are not current production fallback. | ACCEPT | `AGENTS.md`, `docs/design.md`, `docs/implementation-control.md` |
| `fund-analysis analyze-annual-period` is deterministic and does not accept `--use-llm`. | ACCEPT | `docs/design.md`, `docs/current-startup-packet.md` |
| Route C `--use-llm` is explicit opt-in, provider-backed and fail-closed. | ACCEPT | `docs/design.md`, `docs/implementation-control.md` |
| Current repair budget remains one regenerate attempt per body chapter and is not product-calibrated. | ACCEPT | `docs/design.md`, `docs/implementation-control.md` |
| Release/readiness remains `NOT_READY`. | ACCEPT | `docs/implementation-control.md`, `docs/current-startup-packet.md` |

## 4. Diagnostic Closeout

The Chapter 3 diagnostic evidence is accepted for the narrow question it answered:

- prompt payload and typed policy exist for the affected required-output items;
- existing fake-writer/no-live code paths reproduce the `missing_required_output_marker` / `prompt_contract` class;
- current writer-block retry routing is not wired for Chapter 3 required-output gap marker issues;
- provider runtime diagnostics should not be used to classify this blocker.

DS and MiMo both returned PASS. Their residuals are accepted as nonblocking diagnostic residuals:

- item 05 lacks a dedicated paired fake-writer test;
- repair context construction also needs explicit planning coverage, not only runner retry routing;
- some inspection command text in the evidence artifact is less reproducible than ideal.

These residuals would matter if the project chose to enter a Chapter 3 no-live fix planning gate. They do not require that gate to remain the product mainline.

## 5. Route Diagnosis

The accepted post-live sequence shows a repeated pattern:

| Step | Accepted outcome | Controller interpretation |
|---|---|---|
| Chapter 2 L1 fixes | Local no-live fixes and live fail-closed evidence identified new blockers. | Useful local stabilization, not comprehensive report understanding. |
| Chapter 6 invalid marker fix | Chapter 6 became accepted in bounded live metadata, then Chapter 5 became first blocker. | Writer marker repair can move the first blocker but does not prove route readiness. |
| Chapter 5 forbidden phrase fix | Chapter 5 became accepted in bounded live metadata, then Chapter 3 became first blocker. | Prompt/repair guidance remains chapter-specific churn. |
| Chapter 3 missing-required-marker evidence | Diagnostic evidence supports a possible no-live fix plan. | The next local fix is plausible, but continuing this sequence is no longer the best mainline. |

The root issue is not a single remaining extractor or writer bug. The current architecture is field/extractor-driven and prompt-contract-driven. It lacks a durable Fund documents-layer annual-report document representation that can preserve section hierarchy, table structure, provenance, bbox/page spans, field candidates, failure taxonomy and EvidenceAnchor mapping across reports.

Therefore, continuing Route C as an indefinite series of chapter-specific prompt/repair fixes would not prove comprehensive fund-report coverage, long-term extractor viability, readiness or release quality.

## 6. Disposition Table

| Item | Decision | Rationale |
|---|---|---|
| Chapter 3 missing-required-marker no-live diagnostic evidence | ACCEPT | It answers the assigned no-live diagnostic questions and was independently reviewed by DS/MiMo. |
| Chapter 3 no-live fix planning as immediate default next gate | DEFER | It may be useful stabilization work, but the current product mainline must first address annual-report document representation and coverage. |
| Continue Route C chapter-by-chapter live blocker patching as mainline | REJECT | The sequence shows blocker churn and does not solve comprehensive document coverage. |
| Annual-report document representation / Docling benchmark planning as next mainline | ACCEPT | It directly addresses the architecture gap identified by current failures while preserving parser/source boundaries. |
| Direct Docling production parser replacement | REJECT | `docs/design.md` allows Docling only as benchmark/candidate under Fund documents; not as fact truth or direct Service/UI/Host dependency. |
| Annual-period LLM route design | DEFER | It depends on clearer document representation and evidence coverage; current `analyze-annual-period` remains deterministic. |
| Repair budget calibration | DEFER | Current budget is an implementation fact, not product-calibrated; this is separate from document representation. |
| Readiness/release/PR state change | REJECT | Evidence remains insufficient; `NOT_READY` is preserved. |

## 7. Truth-doc Updates

This closeout is paired with truth-doc sync in:

- `docs/design.md`: records that Route C post-live repair churn is not the current product mainline and that document representation is the next architecture question.
- `docs/implementation-control.md`: sets current gate to `Annual-report Document Representation / Docling Benchmark Planning Gate`.
- `docs/current-startup-packet.md`: updates resume entry and next entry point to the same gate.

These updates do not change source behavior, runtime behavior, parser implementation, source policy or readiness state.

## 8. Next Gate Recommendation

Proceed to:

```text
Annual-report Document Representation / Docling Benchmark Planning Gate
```

Required planning boundaries:

- plan only;
- no source/test/runtime implementation;
- no live/provider/network/PDF/FDR commands;
- no production Docling replacement;
- no direct Service/UI/Host/renderer/quality-gate parser calls;
- preserve EID single-source/no-fallback;
- preserve `NOT_READY`;
- define a benchmark matrix for current pdfplumber parser vs Docling candidate on section hierarchy, cross-page tables, merged headers/cells, provenance/bbox to EvidenceAnchor mapping, parser failure taxonomy, cache shape, latency and reproducibility;
- define a future `FundDisclosureDocument`-like schema only as candidate design, not current code fact.

Deferred entries:

- `Provider/LLM Chapter 3 Missing-required-marker No-live Fix Planning Gate`
- Provider/LLM Chapter 2 / Chapter 5 / Chapter 6 further stabilization
- chapter repair budget calibration
- annual-period / multi-period disclosure LLM route design
- controlled live provider/LLM acceptance
- release/readiness/PR gate

## 9. Final Verdict

VERDICT: ACCEPT_ROUTE_REALIGNMENT_NOT_READY

The current Route C diagnostic route is closed as accepted diagnostic input, but the mainline moves to annual-report document representation / Docling benchmark planning. Release/readiness remains `NOT_READY`.
