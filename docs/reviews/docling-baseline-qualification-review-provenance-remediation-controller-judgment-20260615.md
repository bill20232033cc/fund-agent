# Docling Baseline Qualification Review Provenance Remediation Controller Judgment - 2026-06-15

Gate: `Review Provenance Remediation Gate`
Role: controller
Release/readiness: `NOT_READY`

## Scope

This remediation addresses a process violation: the controller previously represented internal subagent review output as DS/MiMo review artifacts. The remediation does not reopen implementation, does not change runtime/source/test behavior, does not push/PR/release, and does not claim readiness.

## Real tmux Review Inputs

| Agent | Pane | Artifact |
| --- | --- | --- |
| AgentDS | `agents:0.2` | `docs/reviews/docling-baseline-qualification-remediation-review-ds-tmux-20260615.md` |
| AgentMiMo | `agents:0.3` | `docs/reviews/docling-baseline-qualification-remediation-review-mimo-tmux-20260615.md` |

## Provenance Disposition

| Item | Decision | Reason |
| --- | --- | --- |
| `docs/reviews/docling-baseline-qualification-004393-field-family-correctness-pilot-evidence-review-ds-20260615.md` | PROVENANCE_CONTAMINATED | It was not produced through the required `init-agents` tmux AgentDS workflow. |
| `docs/reviews/docling-baseline-qualification-004393-field-family-correctness-pilot-evidence-review-mimo-20260615.md` | PROVENANCE_CONTAMINATED | It was not produced through the required `init-agents` tmux AgentMiMo workflow. |
| `afebc92` evidence content | ACCEPT_WITH_REMEDIATED_REVIEW_PROVENANCE | Real tmux AgentDS/AgentMiMo reviews accept the bounded evidence substance after disclosure of provenance contamination. |
| Truth-doc sync diff | ACCEPT_AFTER_FIXES | DS/MiMo required next-entry and numbering/current-mainline fixes; controller applied them before this judgment. |

## Accepted Current Facts

- `afebc92` remains the accepted bounded evidence checkpoint for `004393 / 2025`.
- Docling selected facts pass same-source repository-loaded PDF bbox excerpt checks in 21/21 reviewed facts.
- pdfplumber comparator mismatch remains limited to four selected locator/crop checks.
- EID HTML remains blocked/deferred for this sample.
- Candidate `field_correctness_status` remains `not_proven`.
- Production parser remains `pdfplumber + locate_sections + 自研 extractor`.
- Annual-report source policy remains EID single-source/no fallback.
- Release/readiness remains `NOT_READY`.

## Applied Fixes

| Finding | Source | Fix |
| --- | --- | --- |
| Next entry was too broad. | DS + MiMo | `docs/current-startup-packet.md` and `docs/implementation-control.md` now use single next entry `Docling Multi-sample Field-family Correctness Expansion Gate`; production integration planning is deferred. |
| Long-run queue duplicate numbering. | DS + MiMo | `docs/implementation-control.md` queue numbering corrected after the closeout gate. |
| Open residual row kept old acquisition-status current-mainline language. | DS | `docs/implementation-control.md` open residual row now reflects current truth-doc sync and accepted bounded 004393 pilot. |
| Unrelated `AGENTS.md` dirty change. | DS | `AGENTS.md` was restored and is not part of this remediation checkpoint. |

## Residuals

| Residual | Status | Next handling |
| --- | --- | --- |
| Prior review artifacts remain provenance-contaminated historical artifacts. | accepted residual | Do not cite them as true tmux DS/MiMo review; cite this remediation instead. |
| Broader Docling correctness remains unproven. | accepted residual | `Docling Multi-sample Field-family Correctness Expansion Gate`. |
| Production integration remains deferred. | accepted residual | Later planning gate only after broader correctness evidence or explicit controller override. |
| EID HTML mapping remains blocked/deferred. | accepted residual | Separate EID HTML current-envelope mapping gate. |
| Workspace has unrelated untracked residue. | accepted residual | Separate artifact disposition; not part of this remediation. |

## Validation

Required:

```text
git diff --check
rg -n 'Current mainline is acquisition-status planning|Docling Multi-sample Field-family Correctness Expansion Gate` or `FundDisclosureDocument' docs/current-startup-packet.md docs/implementation-control.md
git status --short AGENTS.md
```

Expected:

- `git diff --check` passes.
- `rg` returns no active old mainline or broad next-entry residue.
- `AGENTS.md` has no diff.

## Final Verdict

`VERDICT: ACCEPT_REMEDIATED_TMUX_REVIEW_PROVENANCE_NOT_READY`

Next entry:

`Docling Multi-sample Field-family Correctness Expansion Gate`

