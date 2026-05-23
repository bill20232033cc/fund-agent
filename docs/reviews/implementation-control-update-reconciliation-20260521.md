# Implementation Control Update Reconciliation（2026-05-21）

## Reviewed Inputs

- Current control truth: `docs/implementation-control.md`
- Candidate update: `docs/implementation-control-update.md`
- Current design truth: `docs/design.md`
- Related design reconciliation: `docs/reviews/design-update-reconciliation-20260521.md`

## Controller Judgment

`docs/implementation-control-update.md` is useful as a readable executive summary, but it cannot replace `docs/implementation-control.md`. The current control document is the durable phase ledger used by phaseflow: it records gate state, artifacts, review decisions, commits, validation results, residual risks, and next entry points. Replacing it with the update file would lose review evidence and break phase recovery.

The right fusion strategy is:

1. Keep the detailed gate log in `docs/implementation-control.md`.
2. Add a short top-level Current Snapshot and capability summary for readability.
3. Treat `docs/implementation-control-update.md` as an input, not as the new control truth.

## Accepted For Fusion

| Topic | Decision | Reason |
|---|---|---|
| Current project snapshot | accepted | A short dashboard helps readers understand phase, gate, next entry point, recent artifacts, and active risks without scanning the full ledger. |
| Implemented capability summary | accepted | A compact capability table is useful as navigation, as long as it avoids line counts and stale service-count claims. |
| Technical debt summary | accepted with correction | Repo-audit follow-ups should be tracked, but exact file references and severity must reflect current code facts. |
| Residual risk summary | accepted with correction | A short risk table is useful, but it must retain current P8/post-P8 risks and not mark unresolved supply-chain or product-contract issues as closed. |
| Future direction | accepted as direction only | v2/v3 ideas may be listed as non-committed planning directions; concrete phases require separate planning gates. |

## Rejected Or Corrected

| Topic | Decision | Reason |
|---|---|---|
| Wholesale replacement of `implementation-control.md` | rejected | It would discard phase evidence, artifact paths, review decisions, commits, and gate history. |
| “MVP completed / stable period” as current state | corrected | Current control truth includes P8 and post-P8 planning; the active state must reflect the latest gate, not stop at P7. |
| PR mapping in update file | corrected | Candidate PR mapping is inconsistent with the existing control ledger. Historical PR/phase mapping should not be rewritten without source evidence. |
| Phase renaming | rejected | P2/P3/P4 names in the current control ledger are accepted history and should not be redefined by a summary file. |
| “Dayu-Agent risk closed because zero imports” | corrected | Main path is not using Dayu runtime, but dependency availability/supply-chain risk remains until the dependency is removed, mirrored, or made optional. |
| “EID 巨潮” terminology | rejected | Accepted wording is EID/CSRC unified disclosure platform primary source, Eastmoney/akshare fallback. |
| “Investor return new-rule issue closed by estimation” | rejected | Current design requires explicit direct/estimated/missing distinction and evidence anchors. Estimation cannot be generalized as a closed data problem. |
| Unverified stale-file debt claims | needs more evidence | Claims about unused audit files or helpers must be checked against the current codebase before being accepted. |

## Applied Update Scope

The current control document should only receive a concise top-level snapshot and summary. Detailed historical records remain intact.

## Residual Follow-Ups

- Product contract: decide user-facing `analyze` minimal inputs versus dev/override parameters.
- Repo hygiene: LICENSE, CI, `.gitignore`, path configuration, and dependency strategy.
- Control document hygiene: consider phase-log archival/indexing only after phaseflow recovery requirements are preserved.
