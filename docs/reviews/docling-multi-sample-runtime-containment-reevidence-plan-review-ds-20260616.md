# Docling Multi-sample Runtime Containment Re-evidence Plan Review - DS - 2026-06-16

Gate: `Docling Multi-sample Runtime Containment Re-evidence Planning Gate`
Reviewer: AgentDS via tmux pane `agents:0.2`
Review type: scoped plan review
Release/readiness: `NOT_READY`

## Verdict

```text
PASS_WITH_FINDINGS
```

## Scope

AgentDS reviewed:

- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/reviews/docling-baseline-runtime-containment-evidence-controller-judgment-20260616.md`
- `docs/reviews/docling-multi-sample-runtime-containment-reevidence-plan-20260616.md`
- `fund_agent/fund/documents/candidates/representation_export.py`
- `fund_agent/fund/documents/candidates/representation_handlers.py`

The review was plan-only. AgentDS did not run Docling conversion, live/network/EID/FDR/PDF/source acquisition/provider/LLM/analyze/checklist/golden/readiness/release/PR commands, and did not modify files.

## Findings

| ID | Severity | Finding | Required action |
| --- | --- | --- | --- |
| P1 | low | Section 3 listed `reports/representation-json/full-representation-export-manifest-20260615.json` as a direct evidence input without explicitly warning that it is metadata-only and must not be passed to `--manifest`. If the full manifest were passed to the harness, the worker could accidentally target existing accepted `reports/representation-json/*` outputs or S1. | Add an explicit warning that this manifest is metadata input only and that Section 7 single-sample manifests are mandatory. |
| P2 | info | `/usr/bin/time -p` output can mix with stderr when stdout/stderr are redirected. | No required plan fix; worker can parse `real <seconds>` from stderr or a timing log. |
| P3 | info | Section 13 correctly requires real tmux DS/MiMo handoffs and records the fallback condition if panes are unavailable. | No action. |

## Focus Assessment

| Focus | Result |
| --- | --- |
| Restricts scope to S4/S5/S6 runtime/cache/cost containment re-evidence | PASS |
| Avoids treating existing representation JSON as runtime proof | PASS |
| Uses existing candidate export harness without crossing production repository/parser/Service/Host/UI boundaries | PASS |
| Forbids overwriting accepted `reports/representation-json/*` outputs | PASS |
| Manifest, commands and pass/block criteria are execution-ready | PASS_WITH_LOW_FINDING |
| Preserves candidate-only non-proof claims and `NOT_READY` | PASS |
| Contains blocker requiring plan rejection | NO |

## Residuals

| Residual | Owner | Disposition |
| --- | --- | --- |
| Worker-channel reliability for future DS/MiMo handoffs | Controller / agent setup owner | Retained process residual; current review completed through real tmux pane. |
| S4/S5/S6 runtime containment evidence remains unproven until the next evidence gate runs | Evidence worker / controller | Expected next-gate residual. |

## Final Recommendation

AgentDS recommends accepting the plan after the low clarity finding P1 is amended. P2 and P3 are nonblocking execution-detail notes. Release/readiness must remain `NOT_READY`.
