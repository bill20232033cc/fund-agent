# Docling Baseline Qualification Remediation Review - AgentMiMo tmux - 2026-06-15

Gate: `Review Provenance Remediation Gate`
Role: `AgentMiMo` via tmux pane `agents:0.3`
Release/readiness: `NOT_READY`

## Scope

This is the real tmux-pane AgentMiMo remediation review requested after the controller incorrectly represented internal subagent output as DS/MiMo review artifacts.

Reviewed:

- `docs/reviews/docling-baseline-qualification-004393-field-family-correctness-pilot-evidence-20260615.md`
- `docs/reviews/docling-baseline-qualification-004393-field-family-correctness-pilot-controller-judgment-20260615.md`
- `reports/representation-json/004393_field_family_correctness_pilot_reviewed_facts_20260615.json`
- current truth-doc sync diff in `docs/design.md`, `docs/current-startup-packet.md`, `docs/implementation-control.md`
- `docs/reviews/docling-baseline-qualification-closeout-truth-doc-sync-controller-judgment-20260615.md`

## Verdict

`PASS_WITH_RESIDUALS`

AgentMiMo accepted the current truth-doc sync content and bounded pilot evidence, with residuals for queue numbering, prior provenance risk and broader future gates.

## Findings

| Severity | Finding | Required fix |
| --- | --- | --- |
| Low | `docs/implementation-control.md` long-run queue had duplicate item 16. | Renumber queue entries. |
| Info | Prior controller claim that DS/MiMo review came from internal subagent output creates provenance risk. | Treat as remediation residual; current tmux review can close the process gap without rolling back bounded evidence. |
| Info | `docs/design.md` now describes `FundDisclosureDocument` as a current candidate rather than only future candidate. | No fix required; aligns with accepted candidate-layer status. |

## Accepted Points

- Evidence remains acceptable as bounded `004393 / 2025` Docling pilot: 21 selected Docling facts pass same-source PDF bbox excerpt checks.
- pdfplumber comparator mismatch is limited to four selected locator/crop checks.
- EID HTML remains blocked/deferred.
- Truth-doc sync has no active old current-mainline residue after the controller fix.
- Docling is not upgraded to production parser, source truth, full field correctness or readiness.
- Production parser and source policy remain unchanged: `pdfplumber + locate_sections + 自研 extractor`; EID single-source/no fallback.

## Residuals

- Broader sample correctness remains unproven.
- Production integration remains unplanned and deferred.
- EID HTML current-envelope mapping remains blocked/deferred.
- Workspace residue remains separate from this gate.

