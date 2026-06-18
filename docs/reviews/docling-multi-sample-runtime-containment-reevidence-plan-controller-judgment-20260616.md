# Docling Multi-sample Runtime Containment Re-evidence Plan Controller Judgment - 2026-06-16

Gate: `Docling Multi-sample Runtime Containment Re-evidence Planning Gate`
Controller role: plan disposition and closeout
Release/readiness: `NOT_READY`

## 1. Scope

This judgment closes the planning gate for bounded S4/S5/S6 Docling runtime/cache/cost re-evidence.

It does not authorize Docling conversion in this planning gate, live/network/EID/FDR/PDF/source acquisition, pdfplumber export, provider/LLM, analyze/checklist/golden/readiness/release/PR commands, production parser replacement, `FundDocumentRepository` behavior change, source policy change, `EvidenceAnchor` schema change, CHAPTER_CONTRACT change, Service/Host/UI/renderer/quality gate integration, push, merge or PR.

## 2. Evidence Reviewed

| Artifact | Role |
| --- | --- |
| `AGENTS.md` | Rule truth source |
| `docs/current-startup-packet.md` | Current active gate and guardrails |
| `docs/implementation-control.md` | Control truth and current gate scope |
| `docs/reviews/docling-baseline-runtime-containment-evidence-controller-judgment-20260616.md` | Accepted source of the S4/S5/S6 runtime containment blocker |
| `docs/reviews/docling-multi-sample-runtime-containment-reevidence-plan-20260616.md` | Plan under review |
| `docs/reviews/docling-multi-sample-runtime-containment-reevidence-plan-review-ds-20260616.md` | AgentDS scoped plan review |
| `docs/reviews/docling-multi-sample-runtime-containment-reevidence-plan-review-mimo-20260616.md` | AgentMiMo scoped plan review |
| `fund_agent/fund/documents/candidates/representation_export.py` | Candidate export harness checked by reviewers |
| `fund_agent/fund/documents/candidates/representation_handlers.py` | Candidate Docling handler checked by reviewers |

## 3. Accepted Plan Facts

| Fact | Classification | Controller disposition |
| --- | --- | --- |
| S4/S5/S6 are the only samples in scope for the next re-evidence gate. | scope fact | `ACCEPT` |
| S1 `004393 / 2025` already has accepted single-sample socket-blocked runtime containment evidence and must not be re-run by this plan. | accepted prior fact | `ACCEPT` |
| Existing S4/S5/S6 representation JSONs are useful artifacts but are not runtime containment proof because their original conversion posture lacks accepted socket-block/offline/artifacts-path/timing logs. | causal-gap fact | `ACCEPT` |
| The next evidence gate should use the existing `fund_agent.fund.documents.candidates.representation_export` candidate harness with single-sample manifests and `--run-built-in-handlers`. | route fact | `ACCEPT` |
| Evidence outputs must be isolated under `reports/docling-runtime-containment/20260616/` and must not overwrite accepted `reports/representation-json/*` artifacts. | write-boundary fact | `ACCEPT` |
| The plan preserves `not_source_truth`, `not_full_field_correctness`, `not_production_parser_replacement`, `not_readiness_proof`, and `NOT_READY`. | guardrail fact | `ACCEPT` |

## 4. Review Finding Disposition

| Finding | Source | Disposition | Reason |
| --- | --- | --- | --- |
| Full representation manifest was listed as input without explicitly saying it is metadata-only and must not be passed to the harness. | DS-P1 | `ACCEPT_CLOSED` | Plan Section 3 now states that `reports/representation-json/full-representation-export-manifest-20260615.json` is metadata input only and that evidence worker must create Section 7 single-sample manifests. |
| `/usr/bin/time -p` output parsing could be ambiguous when stderr is redirected. | DS-P2 / MiMo-F2 | `ACCEPT_CLOSED` | Plan Section 8 now requires parsing `real <seconds>` from the timing stderr stream or combined stderr log and blocking when the timing line is absent. |
| The plan should explicitly mark `--output-root reports/docling-runtime-containment/20260616/outputs` as mandatory. | MiMo-F1 | `ACCEPT_CLOSED` | Plan Section 8 now states that `--output-root` is mandatory for every `representation_export` command. |
| `has_table_cell_locator=true` could block no-table PDFs. | MiMo-F3 | `ACCEPT_WITH_BOUNDARY` | S4/S5/S6 are annual-report samples expected to contain tables. Plan Section 11 now requires recording metrics and blocking the sample if table-cell locator structure is absent, rather than weakening criteria. |
| Real tmux DS/MiMo review requirement is compatible with heavy gate discipline. | DS-P3 | `ACCEPT` | Reviews were completed through real tmux panes `agents:0.2` and `agents:0.3`. |

## 5. Accepted / Rejected / Residual Table

| Claim | Decision | Reason |
| --- | --- | --- |
| Plan is ready to hand off to a bounded S4/S5/S6 runtime containment evidence worker. | `ACCEPT` | DS and MiMo both returned `PASS_WITH_FINDINGS`; low findings were applied or dispositioned. |
| The next gate may run bounded no-live Docling conversion for S4/S5/S6 using the accepted plan. | `ACCEPT_WITH_BOUNDARY` | Authorized only for the next evidence gate, with official source acquisition/live/network/provider/readiness/release/PR still forbidden. |
| Existing S4/S5/S6 JSONs prove runtime containment. | `REJECT` | The accepted blocker is missing per-sample runtime logs. |
| Docling is now a production baseline or parser replacement. | `REJECT` | Production integration remains deferred. |
| Docling output is source truth or full field correctness proof. | `REJECT` | Candidate-only evidence; full correctness/source truth remains unproven. |
| Release/readiness may move from `NOT_READY`. | `REJECT` | This is a planning closeout, not readiness proof. |

## 6. Validation

Commands run for this planning closeout:

```text
git branch --show-current
git status --short
git status --branch --short
git diff --check
tmux-cli status
tmux list-panes -a -F '#{session_name}:#{window_index}.#{pane_index} #{window_name} #{pane_current_command} #{pane_title}'
tmux-cli send -p agents:0.2 /clear
tmux-cli send -p agents:0.3 /clear
tmux-cli wait_idle -p agents:0.2 --timeout 30
tmux-cli wait_idle -p agents:0.3 --timeout 30
tmux-cli send -p agents:0.2 <DS scoped planreview prompt>
tmux-cli send -p agents:0.3 <MiMo scoped planreview prompt>
tmux-cli wait_idle -p agents:0.2 --timeout 180
tmux-cli wait_idle -p agents:0.3 --timeout 180
tmux capture-pane -p -t agents:0.2 -S -500
tmux capture-pane -p -t agents:0.3 -S -500
```

No Docling conversion, live/source acquisition, provider/LLM, readiness, release, PR, push or merge command was run in this planning gate.

## 7. Residuals

| Residual | Status | Owner | Next handling |
| --- | --- | --- | --- |
| S4/S5/S6 socket-blocked runtime logs are still missing | blocking for Gate A full-matrix runtime pass | evidence worker / controller | Run the next bounded no-live evidence gate using this accepted plan |
| Runtime cost threshold is not calibrated | retained | baseline qualification owner | Next evidence gate records elapsed seconds and metrics; threshold calibration remains separate |
| Production model artifact provenance is not accepted | retained | future production integration owner | Separate provenance gate before production dependency |
| Docling baseline status remains candidate-only | retained | controller / future baseline disposition owner | Full-document coverage, EvidenceAnchor mapping, comparative quality and performance evidence remain future gates |

## 8. Next Gate Recommendation

Recommended next gate:

```text
Docling Multi-sample Runtime Containment Re-evidence Gate
```

Purpose:

- create isolated single-sample manifests for S4/S5/S6;
- verify accepted input PDF hashes before conversion;
- run only bounded no-live candidate Docling conversion through the existing export harness;
- preserve socket blocking, offline flags, explicit `cache/docling-artifacts`, `do_ocr=false` and `do_table_structure=true`;
- write isolated outputs/logs/summary under `reports/docling-runtime-containment/20260616/`;
- produce `docs/reviews/docling-multi-sample-runtime-containment-reevidence-20260616.md`;
- keep all claims candidate-only and `NOT_READY`.

Do not proceed automatically to full-document coverage or baseline disposition before the evidence gate is completed, reviewed and accepted.

## 9. Final Verdict

```text
VERDICT: ACCEPT_PLAN_READY_FOR_MULTI_SAMPLE_RUNTIME_CONTAINMENT_REEVIDENCE_GATE_NOT_READY
```
