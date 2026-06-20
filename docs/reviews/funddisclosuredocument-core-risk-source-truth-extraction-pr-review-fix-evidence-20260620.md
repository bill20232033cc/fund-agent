# FundDisclosureDocument core_risk.v1 Source-truth Direct Extraction PR Review Fix Evidence

## Scope

- Gate: `FundDisclosureDocument core_risk.v1 Source-truth Direct Extraction PR Review Fix Gate`
- Accepted finding fixed: Codex F1 from `docs/reviews/pr-34-review-codex-20260620.md`
- Secondary input reviewed: `docs/reviews/pr-34-review-ds-20260620.md`
- Artifact path: `docs/reviews/funddisclosuredocument-core-risk-source-truth-extraction-pr-review-fix-evidence-20260620.md`

## PR 34 Facts Recorded

- PR URL: `https://github.com/bill20232033cc/fund-agent/pull/34`
- Base: `funddisclosure-current-stage-source-truth`
- Head: `funddisclosure-core-risk-source-truth`
- Reviewed head: `24c6761f9da81110cc303a187680c952a2c98354`
- mergeState: `CLEAN`
- CI: `test` `SUCCESS`

## Changed Files

- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/reviews/funddisclosuredocument-core-risk-source-truth-extraction-pr-review-fix-evidence-20260620.md`

## Fix Summary

- Updated active current gate from stale implementation/code-review wording to `FundDisclosureDocument core_risk.v1 Source-truth Direct Extraction PR Review Fix Gate Completed Locally`.
- Updated current next entry to `FundDisclosureDocument core_risk.v1 Source-truth Direct Extraction PR Review Re-review Gate`.
- Recorded PR 34 URL, base/head, reviewed head, mergeState and CI in both current control surfaces.
- Removed active/current contradictions that said no push/PR after PR 34 already existed.
- Removed active/current resume residue that routed to `current_stage.v1` follow-up push or stated `core_risk.v1` remained unimplemented.
- Preserved the scope boundary: only `core_risk.v1.risk_characteristic_text` is implemented; `liquidation_or_scale_risk`, `tracking_error_or_deviation_risk`, `turnover_or_style_drift_risk` and `concentration_risk` remain candidate-only/deferred; no parser replacement, readiness, release, mark-ready or merge is authorized.

## Verification

Command:

```bash
rg -n "Implementation Gate Completed Locally|pending code review|Code Review Gate|No commit/stage/push/PR|current_stage\\.v1 Source-truth Direct Extraction Follow-up Push Gate|core_risk\\.v1 remains unimplemented|PR Review Re-review Gate|PR 34" docs/current-startup-packet.md docs/implementation-control.md
```

Result summary:

- Active/current surfaces now route to `FundDisclosureDocument core_risk.v1 Source-truth Direct Extraction PR Review Re-review Gate`.
- Active/current surfaces record PR 34 metadata in `docs/current-startup-packet.md` and `docs/implementation-control.md`.
- No active/current hit remains for `Implementation Gate Completed Locally`, `pending code review`, `No commit/stage/push/PR`, or `core_risk.v1 remains unimplemented`.
- Remaining `Code Review Gate` and `current_stage.v1 Source-truth Direct Extraction Follow-up Push Gate` hits are historical ledger entries under the accepted artifact list, not active/current control or resume checklist entries.

Command:

```bash
git diff --check -- docs/current-startup-packet.md docs/implementation-control.md docs/reviews/funddisclosuredocument-core-risk-source-truth-extraction-pr-review-fix-evidence-20260620.md
```

Observed result after writing this artifact: no output, exit code 0.

## Non-goals Preserved

- No code, tests, PR review artifacts, plan artifacts, README or design doc edits.
- No staging, commit, push, PR mutation, mark-ready, merge or re-review execution.
