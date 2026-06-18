# Docling Baseline Runtime Containment Evidence Controller Judgment - 2026-06-16

Gate: `Docling Baseline Runtime Containment Evidence Gate`
Controller role: evidence disposition and closeout
Release/readiness: `NOT_READY`

## 1. Scope

This judgment closes the current runtime containment evidence pass for Docling baseline qualification.

It does not authorize code changes, Docling conversion, live/source acquisition, EID/FDR/PDF download, pdfplumber export, provider/LLM, analyze/checklist/golden/readiness/release/PR commands, production parser replacement, source policy change, `FundDocumentRepository` behavior change, `EvidenceAnchor` schema change, CHAPTER_CONTRACT change, Service/Host/UI/renderer/quality gate integration, push, merge or PR.

## 2. Evidence Reviewed

| Artifact | Role |
| --- | --- |
| `AGENTS.md` | Rule truth source |
| `docs/current-startup-packet.md` | Current active gate and guardrails |
| `docs/implementation-control.md` | Control truth and current gate scope |
| `docs/design.md` Docling candidate sections | Candidate-layer design boundary |
| `docs/reviews/docling-baseline-qualification-plan-20260615.md` | Accepted baseline qualification plan |
| `docs/reviews/docling-baseline-qualification-plan-controller-judgment-20260615.md` | Accepted Gate A threshold source |
| `docs/reviews/docling-runtime-local-artifact-no-model-download-containment-proof-controller-judgment-20260614.md` | Prior blocked state |
| `docs/reviews/docling-route-a-local-artifact-conversion-quality-evidence-20260615.md` | Route A single-sample runtime evidence |
| `docs/reviews/docling-baseline-runtime-containment-evidence-20260616.md` | Current evidence artifact |
| `docs/reviews/docling-baseline-runtime-containment-evidence-review-local-20260616.md` | Initial local fallback review |
| `docs/reviews/docling-baseline-runtime-containment-evidence-review-ds-20260616.md` | AgentDS scoped review via tmux |
| `docs/reviews/docling-baseline-runtime-containment-evidence-review-mimo-20260616.md` | AgentMiMo scoped review via tmux |

Initial subagent spawn was attempted and failed with `agent thread limit reached`. After user correction, real tmux handoffs were sent to AgentDS and AgentMiMo, and both returned scoped reviews. This judgment does not claim ProCodex review.

## 3. Accepted Facts

| Fact | Classification | Controller disposition |
| --- | --- | --- |
| Prior `20260614` containment evidence correctly blocked Docling conversion when `artifacts_path=None` because the layout stage could call remote model download. | accepted historical fact | `ACCEPT` |
| Route A later supplied repo-local artifacts under `cache/docling-artifacts` and completed S1 `004393 / 2025` conversion with explicit artifacts path and socket blocking. | accepted single-sample runtime fact | `ACCEPT` |
| Route A artifact inventory is about `505M` and includes layout/table model artifacts with recorded file hashes. | candidate cache fact | `ACCEPT_WITH_BOUNDARY` |
| S1 conversion cost is measured as `63.483s` for a `65` page / `832089` byte PDF with `do_ocr=false` and `do_table_structure=true`. | single-sample runtime cost fact | `ACCEPT_WITH_BOUNDARY` |
| S4/S5/S6 Docling representation JSON files exist and carry page/bbox/table-cell locator structure. | representation artifact fact | `ACCEPT` |
| S4/S5/S6 do not have accepted per-sample runtime logs proving socket-blocked conversion, explicit local artifacts path, no hidden model download and elapsed-time cost. | blocker fact | `ACCEPT_BLOCKER` |
| Multi-sample selected-fact correctness expansion remains accepted from the prior gate, but it is not runtime containment proof. | boundary fact | `ACCEPT` |

## 4. Review Finding Disposition

| Finding | Source | Disposition | Reason |
| --- | --- | --- | --- |
| Do not infer runtime containment from S4/S5/S6 JSON existence. | Local R1 | `ACCEPT_CLOSED` | Evidence artifact separates representation availability from runtime proof. |
| Preserve Gate A active-sample runtime threshold. | Local R2 | `ACCEPT_CLOSED` | Full-matrix pass is blocked. |
| Local artifacts are candidate evidence, not production model provenance. | Local R3 | `ACCEPT_RESIDUAL` | Production model provenance requires separate gate. |
| Multi-sample runtime/cost threshold remains uncalibrated. | Local R4 | `ACCEPT_RESIDUAL` | Needs bounded runtime re-evidence. |
| Worker-channel history must be recorded. | Local R5 | `ACCEPT_RESIDUAL_HISTORY` | Initial `agent thread limit reached` recorded; later DS/MiMo tmux reviews completed. |
| Control sync files are modified and need checkpoint. | DS-F1 | `ACCEPT_NONBLOCKING` | Local accepted commit is required before closeout; does not block gate acceptance. |
| Heavy gate independent review requirement must be handled. | DS-F2 | `ACCEPT_CLOSED` | DS and MiMo reviews were obtained through real tmux panes after initial spawn failure. |
| S4/S5/S6 JSONs exist but do not prove original containment posture. | DS-F3 | `ACCEPT_RESIDUAL` | The next re-evidence planning gate must explicitly state this causal gap. |
| Evidence/control sync pass with no required action. | MiMo-F1-F6 | `ACCEPT` | MiMo returned PASS and recommended local checkpoint. |

## 5. Accepted / Rejected / Residual Table

| Claim | Decision | Reason |
| --- | --- | --- |
| Accept S1 runtime containment evidence as candidate input. | `ACCEPT` | Route A records explicit local artifacts path, socket-blocked conversion, no OCR, table structure enabled, output hashes and elapsed time. |
| Treat runtime containment as proven for S4/S5/S6. | `REJECT` | No accepted per-sample runtime logs found. |
| Treat full active sample matrix Gate A as passed. | `REJECT` | Accepted plan requires active samples to prove runtime containment; only S1 does. |
| Treat S4/S5/S6 representation JSONs as useful for later gates. | `ACCEPT_WITH_BOUNDARY` | They are parseable representation artifacts, not runtime logs or source truth. |
| Treat Docling as production baseline or parser replacement. | `REJECT` | Production integration remains deferred. |
| Treat Docling output as source truth or full field correctness proof. | `REJECT` | Candidate-only evidence; field correctness status remains bounded/not proven. |
| Move release/readiness from `NOT_READY`. | `REJECT` | This gate is not readiness proof. |

## 6. Validation

Commands run:

```text
git branch --show-current
git status --short
git diff --check
python -m json.tool reports/docling-route-a/artifact-manifest.json
python -m json.tool reports/docling-route-a/004393_2025_docling_summary.json
python -m json.tool reports/representation-json/004393_2025_docling_full.json
python -m json.tool reports/representation-json/006597_2024_docling_full.json
python -m json.tool reports/representation-json/017641_2024_docling_full.json
python -m json.tool reports/representation-json/110020_2024_docling_full.json
jq -e '.socket_blocked == true and .artifacts_path != null and .status == "success"' reports/docling-route-a/004393_2025_docling_summary.json
jq -e 'all(inputs; (.summary_metrics.has_bbox == true and .summary_metrics.has_page_number == true and .summary_metrics.has_table_cell_locator == true))' reports/representation-json/004393_2025_docling_full.json reports/representation-json/006597_2024_docling_full.json reports/representation-json/017641_2024_docling_full.json reports/representation-json/110020_2024_docling_full.json
```

At judgment-writing time, these commands are the required validation set for the scoped files. No production parser, source acquisition, Docling conversion or readiness command is part of this validation.

## 7. Residuals

| Residual | Status | Owner | Next handling |
| --- | --- | --- | --- |
| S4/S5/S6 socket-blocked runtime logs missing | blocking for Gate A pass | evidence worker / controller | Bounded no-live multi-sample runtime containment re-evidence gate |
| Multi-sample runtime cost threshold uncalibrated | blocking for performance/cost disposition | baseline qualification owner | Measure elapsed seconds, pages, tables, cells and output bytes per sample |
| Production model artifact provenance not accepted | retained | future production integration owner | Separate provenance gate before production dependency |
| Initial subagent spawn unavailable | accepted channel-history residual | controller / agent channel owner | Real tmux AgentDS and AgentMiMo reviews completed for this closeout; continue using pane handoffs when required |

## 8. Next Gate Recommendation

Recommended next gate:

```text
Docling Multi-sample Runtime Containment Re-evidence Planning Gate
```

Purpose:

- write a bounded, no-live, no-source-acquisition plan for re-running only S4/S5/S6 Docling conversion with:
  - `HF_HUB_OFFLINE=1`;
  - `TRANSFORMERS_OFFLINE=1`;
  - explicit `cache/docling-artifacts`;
  - socket-blocked subprocess;
  - `do_ocr=false`;
  - `do_table_structure=true`;
  - per-sample elapsed time, page/table/cell/output-byte metrics;
  - output hashes and manifest;
  - fail-closed logging for any attempted network/model download.
- keep all outputs candidate-only and `NOT_READY`.

Do not proceed to `Docling Full-document Coverage Evidence Gate` until the full active matrix runtime containment blocker is accepted or explicitly deferred by a controller judgment.

## 9. Final Verdict

```text
VERDICT: ACCEPT_PARTIAL_RUNTIME_EVIDENCE_BLOCKED_FOR_FULL_MATRIX_READY_FOR_REEVIDENCE_PLANNING_NOT_READY
```
