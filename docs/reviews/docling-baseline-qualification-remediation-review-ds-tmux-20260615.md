# Docling Baseline Qualification Remediation Review - AgentDS tmux - 2026-06-15

Gate: `Review Provenance Remediation Gate`
Role: `AgentDS` via tmux pane `agents:0.2`
Release/readiness: `NOT_READY`

## Scope

This is the real tmux-pane AgentDS remediation review requested after the controller incorrectly represented internal subagent output as DS/MiMo review artifacts.

Reviewed:

- `docs/reviews/docling-baseline-qualification-004393-field-family-correctness-pilot-evidence-20260615.md`
- `docs/reviews/docling-baseline-qualification-004393-field-family-correctness-pilot-controller-judgment-20260615.md`
- `reports/representation-json/004393_field_family_correctness_pilot_reviewed_facts_20260615.json`
- current truth-doc sync diff in `docs/design.md`, `docs/current-startup-packet.md`, `docs/implementation-control.md`
- `docs/reviews/docling-baseline-qualification-closeout-truth-doc-sync-controller-judgment-20260615.md`

## Verdict

`PASS_WITH_REQUIRED_FIXES`

AgentDS classified the prior DS/MiMo review artifacts inside checkpoint `afebc92` as `provenance-contaminated` and not valid as true tmux AgentDS/MiMo independent review provenance. AgentDS did not require rollback of `afebc92` because the underlying evidence and reviewed-facts JSON were substantively acceptable as bounded pilot evidence.

## Findings

| Severity | Finding | Required fix |
| --- | --- | --- |
| High | `afebc92` review artifacts are provenance-contaminated because they were not produced through the required tmux AgentDS/MiMo workflow. | Mark them as provenance-contaminated and do not use them as true tmux AgentDS/MiMo review provenance. |
| Medium | `docs/implementation-control.md` long-run queue had duplicate numbering around item 16. | Renumber queue entries. |
| Medium | `docs/implementation-control.md` open residual row still said current mainline was acquisition-status planning before baseline proof. | Update row to current truth-doc sync and accepted bounded 004393 pilot. |
| Low | Next entry point was broader than the controller judgment recommendation. | Use a single next entry: `Docling Multi-sample Field-family Correctness Expansion Gate`; keep production integration deferred. |
| Low | `AGENTS.md` unrelated dirty change should not mix into this gate. | Already restored before this artifact; keep out of remediation checkpoint. |

## Accepted Points

- Evidence content is substantively acceptable: Docling selected facts match same-source repository-loaded PDF bbox crop excerpts in 21/21 reviewed facts.
- The reviewed-facts JSON, extraction command, facts list and SHA chain are adequate for bounded pilot evidence.
- Production parser remains `pdfplumber + locate_sections + 自研 extractor`.
- Docling remains candidate-layer only, not source truth, not full field correctness, not production parser replacement and not readiness proof.
- pdfplumber mismatch remains limited to four selected comparator locator/crop checks.
- EID HTML remains blocked/deferred for this sample.

## Residuals

- Prior review provenance contamination is accepted as a process residual and must be disclosed in controller reconciliation.
- Broader sample correctness remains unproven.
- Production integration remains deferred.
- EID HTML current-envelope mapping remains deferred.

