# FundDisclosureDocument core_risk.v1 Source-truth Direct Extraction PR Review Controller Judgment

## Metadata

- Work unit: `FundDisclosureDocument core_risk.v1 risk_characteristic_text Source-truth Direct Extraction`
- Gate: PR Review / Fix / Re-review Gate
- Draft PR: `https://github.com/bill20232033cc/fund-agent/pull/34`
- Base: `funddisclosure-current-stage-source-truth`
- Head: `funddisclosure-core-risk-source-truth`
- Reviewed head before fix commit: `24c6761f9da81110cc303a187680c952a2c98354`
- PR review artifacts:
  - `docs/reviews/pr-34-review-ds-20260620.md`
  - `docs/reviews/pr-34-review-codex-20260620.md`
- Fix evidence: `docs/reviews/funddisclosuredocument-core-risk-source-truth-extraction-pr-review-fix-evidence-20260620.md`
- Targeted re-reviews:
  - `docs/reviews/pr-34-rereview-ds-20260620.md`
  - `docs/reviews/pr-34-rereview-mimo-20260620.md`
- Artifact path: `docs/reviews/funddisclosuredocument-core-risk-source-truth-extraction-pr-review-controller-judgment-20260620.md`

## Verdict

`ACCEPT_PR_REVIEW_READY_FOR_COMMIT_NOT_READY`

PR 34 review is accepted after targeted fix and re-review. Codex F1 is closed. DS and MiMo targeted re-reviews both returned `PR_REREVIEW_PASS`.

## Finding Disposition

| Source | Finding | Controller disposition | Outcome |
|---|---|---|---|
| Codex F1 | Active/current control docs still pointed to stale implementation/code-review/current-stage next-entry surfaces after PR 34 existed | accepted | Fixed in `docs/current-startup-packet.md` and `docs/implementation-control.md`; targeted re-reviews confirmed active/current surfaces now route to PR review re-review gate and contain PR 34 metadata |
| DS low finding 1 | Shared risk-characteristic label config lacks explicit future decoupling guard | deferred-with-owner | No current behavior bug; product_essence focused tests pass. Owner: future risk-characteristic label divergence gate if product_essence and core_risk semantics diverge |
| DS low finding 2 | Binary `_core_risk_status()` may confuse consumers that ignore `deferred_role` gaps | deferred-with-owner | Accepted single-subvalue design for this gate; no current production consumer reads complete `core_risk.v1`. Owner: future multi-subvalue core-risk public contract gate |

## Accepted PR Scope

PR 34 remains limited to proof-positive `FundDisclosureDocument` source-truth direct extraction for:

- `core_risk.v1.risk_characteristic_text`

The following roles remain candidate-only/deferred and are not public values or anchors:

- `liquidation_or_scale_risk`
- `tracking_error_or_deviation_risk`
- `turnover_or_style_drift_risk`
- `concentration_risk`

No complete `core_risk.v1` source truth, parser replacement, `EvidenceSourceKind` / public `EvidenceAnchor` expansion, `StructuredFundDataBundle.core_risk`, Service/UI/Host/renderer/quality-gate consumption, real-report correctness, golden/readiness, release, mark-ready, or merge is accepted.

## Validation Evidence

- PR 34 merge state at review: `CLEAN`
- PR 34 CI `test`: `SUCCESS`
- Fix validation:
  - `rg -n "Implementation Gate Completed Locally|pending code review|Code Review Gate|No commit/stage/push/PR|current_stage\\.v1 Source-truth Direct Extraction Follow-up Push Gate|core_risk\\.v1 remains unimplemented|PR Review Re-review Gate|PR 34" docs/current-startup-packet.md docs/implementation-control.md`
  - `git diff --check -- docs/current-startup-packet.md docs/implementation-control.md docs/reviews/funddisclosuredocument-core-risk-source-truth-extraction-pr-review-fix-evidence-20260620.md`
- Targeted re-review:
  - DS: `PR_REREVIEW_PASS`
  - MiMo: `PR_REREVIEW_PASS`

## Next Gate

After this accepted PR review commit is created, the next entry point is:

`FundDisclosureDocument core_risk.v1 Source-truth Direct Extraction Push Gate`

Release/readiness remains `NOT_READY`.
