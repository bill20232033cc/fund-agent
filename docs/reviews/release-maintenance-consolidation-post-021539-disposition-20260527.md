# Release-Maintenance Consolidation Closeout / QDII Post-021539 Disposition

> Date: 2026-05-27
> Controller: Codex
> Gate: `release-maintenance consolidation closeout / QDII post-021539 disposition gate`
> Gate classification: `standard`
> Scope: docs/control/disposition only; no production code, renderer, quality gate, extractor, baseline/golden promotion, or new QDII probing.

## Startup Packet Replay

| Item | State |
|---|---|
| Current phase | `release maintenance` |
| Current gate | `QDII replacement fallback 021539 evidence accepted locally` |
| Startup Packet next entry point | `QDII replacement post-021539 disposition decision gate; must use init-agents / tmux multi-agent flow` |
| Current HEAD before this gate | `7ab5656 docs: accept qdii fallback 021539 evidence` |
| Gate transition | Authorized transition from the accepted `021539` evidence gate to the Startup Packet next entry point; no unauthorized cursor switch. |

Current allowed work is controller disposition, source-document reconciliation, coverage matrix update, artifact disposition, review dispatch, controller judgment, control-doc update, validation, and local accepted commit.

Current forbidden work remains production code implementation, renderer changes, FQ0-FQ6 changes, extractor changes, Service/CLI changes, new QDII candidate probing, baseline/golden promotion, Host/Agent package creation, `dayu.host` / `dayu.engine` integration, GitHub mutation, or deleting untracked files without explicit authorization.

## Source-Document Standards Check

`docs/implementation-control.md` has been compressed to a control-plane entrypoint and `docs/archive/implementation-control-release-maintenance-ledger-20260527.md` preserves the release-maintenance long ledger as evidence chain.

| Check | Disposition | Evidence |
|---|---|---|
| Startup Packet sufficient to resume | pass | It states truth guardrails, branch, current phase, current gate, next entry point, latest checkpoint, design/control truth, and historical archive paths. |
| Current gate / next entry point clear | pass | It names the current gate as `QDII replacement fallback 021539 evidence accepted locally` and next entry point as `QDII replacement post-021539 disposition decision gate`. |
| Open Residuals centralized | pass with current-gate update required | Residuals are in one table; this gate updates QDII hard stop, coverage blockers, and artifact disposition owner rows. |
| Historical Evidence Index evidence-only | pass | It points to archive files and explicitly says archive entries cannot override Startup Packet or `docs/design.md`. |
| Stale misleading next entry point | pass after this gate update | Old next-entry values remain only in recent ledger rows as evidence chain; the Startup Packet and `Next Entry Point` section will be updated to the accepted next cursor. |

The compressed control document should be accepted as the current control surface after this gate, together with the archived release-maintenance ledger.

## QDII Post-021539 Disposition

Automatic QDII replacement probing is stopped. The four accepted attempts have the same promotion terminal state: source-provenance eligible, quality blocked, and not promoted.

| Candidate | Report year | Provenance disposition | Quality disposition | Promotion disposition | Accepted blocker summary |
|---|---:|---|---|---|---|
| `096001` | 2024 | complete eligible fallback | `block` | `not_promoted` | P0 `nav_benchmark_performance`, FQ4 missing-field-rate `42.9%`, P1 gaps including `turnover_rate`, `holder_structure`, `holdings_snapshot`, `share_change`. |
| `040046` | 2024 | complete eligible fallback | `block` | `not_promoted` | P0 pass, FQ4 missing-field-rate `35.7%`, P1 gaps `turnover_rate`, `holder_structure`, `holdings_snapshot`, `share_change`. |
| `019172` | 2024 | complete eligible fallback | `block` | `not_promoted` | P0 `manager_strategy_text` coverage / traceability `0.0% / 0.0%`, FQ4 missing-field-rate `35.7%`, P1 gaps `turnover_rate`, `holdings_snapshot`, `share_change`. |
| `021539` | 2024 | complete eligible fallback | `block` | `not_promoted` | P0 pass and `manager_strategy_text` pass, but FQ4 missing-field-rate `35.7%` and P1 gaps `turnover_rate`, `holder_structure`, `holdings_snapshot`, `share_change`. |

Decision:

- Record QDII coverage as blocked for baseline/golden v1 until a separate QDII extraction/applicability diagnosis or taxonomy / asset-class fitness gate is accepted.
- Do not run more automatic QDII candidates, including `020712`, active QDII, QDII-FOF, `013308`, bond QDII, or later fallback candidates.
- Preserve `013308` as excluded from evidence until the QDII-name vs `国内股票类` conflict is resolved by a future taxonomy/controller gate.
- Preserve QDII-FOF as excluded from QDII coverage unless a separate taxonomy gate accepts it for the QDII slot.

## Coverage Disposition Matrix

| Slot | Current state | Golden corpus eligibility | Blocker reason | Owner | Revisit condition |
|---|---|---|---|---|---|
| active / `004393` / 2024 | evaluated carry-forward candidate | not yet eligible | Needs durable baseline/golden preflight and fixture-promotion gate; no row promoted by this disposition. | future baseline/golden preflight owner | After coverage blockers are dispositioned and reviewed fact/golden promotion rules are accepted. |
| index / `110020` / 2024 | terminal `reviewed_coverage_candidate_input_accepted`; quality `warn`; `not_promoted` | not yet eligible | Methodology / constituents evidence, reviewed-fact freeze, strict golden absence disposition still unresolved; accepted only as reviewed coverage input, not baseline-ready. | future index evidence sufficiency owner | After accepted index reviewed-fact / evidence sufficiency gate. |
| enhanced-index / `004194` / 2024 | evaluated carry-forward candidate | not yet eligible | Needs durable baseline/golden preflight and fixture-promotion gate; no row promoted by this disposition. | future baseline/golden preflight owner | After coverage blockers are dispositioned and reviewed fact/golden promotion rules are accepted. |
| bond / `006597` / 2024 | quality improved to `warn`, but remains baseline-blocked | blocked | `bond_risk_evidence_missing.baseline_blocking=true` and residual P1 gaps require positive bond-risk evidence or explicit deferral. | bond positive-risk evidence owner | After accepted positive bond-risk evidence contract/evidence, or accepted bond exclusion/deferral decision. |
| QDII / `096001`, `040046`, `019172`, `021539` / 2024 | four attempts provenance eligible but quality `block`; automatic probing stopped | blocked | Repeated FQ4/P1 QDII missing-field blocks after eligible provenance; current evidence does not distinguish extractor gap vs applicability/taxonomy gap enough for promotion. | future QDII diagnosis or taxonomy owner | After separate QDII extraction/applicability diagnosis or QDII taxonomy / asset-class fitness gate. |
| FOF | `data_gap` / `taxonomy_pending` | blocked | No accepted pure `fof_fund` repository-verified candidate; QDII-FOF rows cannot count as pure FOF without taxonomy gate. | future FOF taxonomy owner | After pure FOF entry contract/candidate path, or explicit FOF deferred-from-v1 decision with owner and revisit trigger. |

Golden answer corpus v1 remains blocked. This gate does not promote any sample to durable baseline, clean denominator, fixture, report-quality corpus, scoring-ready state, or golden answer corpus.

## Artifact Disposition

| Path | Category | Evidence | Decision | Owner | Next gate | Blocker? |
|---|---|---|---|---|---|---|
| `docs/archive/implementation-control-release-maintenance-ledger-20260527.md` | evidence-chain artifact | Referenced by compressed control doc as archived release-maintenance ledger. | stage current-gate archive evidence | controller | this gate | no |
| `docs/implementation-control.md` | current-gate artifact | Compressed control surface and next-entry update. | stage current-gate control update | controller | this gate | no |
| `docs/reviews/release-maintenance-consolidation-post-021539-disposition-20260527.md` | current-gate artifact | This disposition / matrix / artifact-disposition artifact. | stage current-gate artifact after review | controller | this gate | no |
| `docs/reviews/release-maintenance-comprehensive-audit-report-20260526.md` | evidence-chain / research input | Historical audit report, not current truth. | leave-untracked | future release-readiness owner | release readiness reconciliation if needed | no |
| `docs/reviews/release-maintenance-comprehensive-audit-report-20260527.md` | evidence-chain / research input | Historical audit report, not current truth. | leave-untracked | future release-readiness owner | release readiness reconciliation if needed | no |
| `docs/reviews/repo-review-20260526-231040.md` | evidence-chain artifact | Historical repo review, not current truth for this gate. | leave-untracked | future review owner | only if separately accepted | no |
| `docs/tmux-agent-memory-store.md` | user-owned / coordination scratch | Agent memory coordination note, not current gate evidence. | leave-untracked | user/controller | none | no |
| `--help` | scratch/runtime stray | Zero-byte stray file from prior shell quoting issue. | ask-before-delete; do not stage | user authorization required | cleanup only if authorized | no |

No tracked scratch artifact is introduced by this gate. No `.gitignore` change is required because the untracked files are discrete review/research/coordination artifacts or a one-off stray file.

Tracked historical review artifacts that are not shown in `git status --short`, such as `docs/reviews/repo-review-20260527-065237.md`, remain evidence-chain material only and are not part of this gate's staging decision.

## Next Cursor Recommendation

Recommended next cursor: `bond positive-risk evidence gate`.

Reason:

- QDII has reached the accepted hard stop; more candidate probing would violate the current gate and repeat the same evidence pattern.
- `006597` is the narrowest known coverage blocker with an accepted concrete residual: `bond_risk_evidence_missing.baseline_blocking=true`.
- A bond positive-risk evidence gate can make progress without changing renderer, FQ0-FQ6, Host/Agent/dayu, source strategy, or baseline/golden promotion.

Why not the other cursors now:

- `QDII extractor/applicability diagnosis`: valid future cursor, but broader and should start from a separate diagnosis plan after this disposition, not by extending probing.
- `FOF taxonomy gate`: still required for FOF coverage, but it is a taxonomy/product coverage decision and does not address the currently narrow bond blocker.
- `golden corpus preflight`: premature because bond, QDII, FOF, and index reviewed-fact residuals remain unresolved or not explicitly deferred.
- `release readiness reconciliation`: premature because coverage and golden-preflight blockers are still open.

## Verifier Matrix

| Requirement | Evidence |
|---|---|
| Consolidation / post-021539 disposition artifact | this file |
| QDII hard stop recorded | QDII disposition section |
| Coverage disposition matrix | coverage matrix section |
| Golden corpus status | explicitly remains blocked |
| Residual owner / revisit condition | coverage matrix and next cursor sections |
| Untracked artifact disposition | artifact disposition section |
| No code/product changes | non-goal scope and git diff review |
| Independent reviews | pending DS / MiMo review artifacts |
| Controller judgment | pending controller judgment artifact |
| Validation | `git diff --check` after final docs update |

## Post-Acceptance Control Update

If controller judgment accepts this disposition, update `docs/implementation-control.md` as follows:

- Set Current gate to `release-maintenance consolidation / QDII post-021539 disposition accepted locally`.
- Set Next entry point to `bond positive-risk evidence gate; must use init-agents / tmux multi-agent flow`.
- Record this disposition artifact, DS review, MiMo review, and controller judgment in Current Accepted Artifacts.
- Resolve the QDII automatic probing hard-stop residual into `coverage blocked pending QDII diagnosis/taxonomy`.
- Preserve golden answer corpus v1 as blocked until coverage, source, quality, fund-type, and fixture-promotion blockers are resolved or explicitly deferred.
- Add a Recent Active Gate Ledger row for this disposition gate.
