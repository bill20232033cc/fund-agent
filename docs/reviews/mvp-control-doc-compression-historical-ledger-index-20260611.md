# Control-doc Compression Historical Ledger Index

日期：2026-06-11

状态：implementation artifact；historical/evidence-chain index；pending review/controller acceptance.

Purpose: identify historical or superseded ledger families that should not remain in the active startup/control surface. This file is evidence chain only.

## Authority Boundary

- Does not override `AGENTS.md`.
- Does not override `docs/design.md`.
- Does not override current phase/gate/next entry in `docs/current-startup-packet.md` or `docs/implementation-control.md`.
- Does not convert historical live evidence, untracked residue or review notes into current source, fixture, release or readiness proof.

## Historical Ledger Families

| Ledger family | Historical status | Evidence entry points | Why it is not active control surface | Current routing |
|---|---|---|---|---|
| Release-maintenance long ledger | Historical evidence | `docs/archive/implementation-control-release-maintenance-ledger-20260527.md`; `docs/reviews/release-maintenance-*`; repo review artifacts | Earlier release-maintenance/readiness context; current phase has moved to typed-template-to-agent stabilization | Use only for provenance; release/readiness requires separate current gate |
| Retrospective independent reviews and provenance corrections | Historical evidence | `docs/reviews/*retrospective*`; checkpoints `f590cae`, `525f9e4`, `671e967`, `3af9e63` | Accepted as evidence-chain corrections, not active next-entry drivers | Use when reconstructing provenance only |
| Earlier provider endpoint/path diagnostics | Superseded or historical evidence | `docs/reviews/mvp-provider-endpoint-path-*`; checkpoints `a96a724`, `764ca00`, `dd0a074`; provider residual artifacts | Later post-config and chapter-calibration evidence changed current residual routing; old retained artifacts cannot prove current live acceptance | Provider/runtime work needs separate reviewed gate and explicit authorization |
| Future live provider calibration evidence | Historical live evidence with residual | Future live provider calibration artifacts; environment-blocked checkpoint `79fd068`; live rerun controller judgment | Evidence classified provider/runtime/network residuals, not repo acceptance or runtime default changes | Operator/environment owner or new diagnostic gate |
| Real LLM smoke re-baseline | Not accepted as full smoke success | Plan `4fd5b5b`; provider residual artifacts; post-config smoke disposition artifacts | Fail-closed smoke evidence did not produce accepted full report; active blockers moved into chapter content/contract/audit calibration | Live acceptance remains deferred |
| Real LLM chapter acceptance Slice 1A-1G | Accepted no-live local calibration evidence | Slice artifacts under `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-*`; no-live closeout checkpoint `13a8c19` | Covers deterministic/no-live residual routes, but does not prove live accepted report generation | Future live evidence gate only with explicit authorization |
| Agent engine design refresh and Slice A-D | Historical/future-design evidence feeding Slice E | Design refresh artifacts and checkpoints `b862381`, `8d50b40`, `1c3c031`, `bc45778`, `9f6d360` | Future architecture and prerequisites; current implemented mechanics are summarized through Slice E | Use design truth labels in `docs/design.md`; do not infer full tool-loop runtime |
| Typed template implementation slice ledger | Accepted evidence, too verbose for active surface | Slice checkpoints and review artifacts listed in accepted artifact index | Full slice-by-slice ledger is recoverable from index and `docs/reviews/`; active surface only needs current template truth-source fact | Use accepted artifact index for reconstruction |
| Small golden manual source identity and retained excerpt intake | Accepted evidence, not current active startup material | Manual evidence artifacts under `docs/reviews/mvp-small-golden-set-*`; checkpoints `2706f91`, `7cc0479` | Supports current extractor evidence baseline but not release/readiness by itself | Use accepted artifact index; fixture projection/promotion deferred |
| Old PR/release closeout notes | Historical evidence | Draft PR #22 checkpoint `2b1c804`; PR/release artifacts under `docs/reviews/` | Does not set current PR external state or release readiness | New PR/release action requires separate gate |
| Workspace ownership and artifact disposition attempts | Historical/context evidence | `docs/reviews/workspace-ownership-reconciliation-20260531.md`; post-EID artifact disposition untracked files if later accepted | Existing untracked files remain unclassified unless accepted by exact artifact/gate | Use current residue disposition index; no cleanup here |

## Compression Decision

The active control docs should retain:

- current phase
- current gate
- next entry
- control/design/template truth
- current accepted checkpoint summary
- open residuals and owners
- links to this index and the accepted artifact index

The active control docs should not retain:

- full accepted checkpoint/path tables
- old release-maintenance long ledgers
- superseded provider diagnostic narratives
- old PR/release state details
- untracked residue as proof

## Residuals

| Residual | Owner | Next handling |
|---|---|---|
| Need exact chronological reconstruction | Controller/reviewer | Use git history plus `docs/reviews/` artifacts; do not re-inline into active control surface |
| Historical artifact acceptance ambiguity | Controller | Create artifact-specific disposition or provenance gate |
| Release/readiness cleanliness | Release owner | Separate release-readiness gate after accepted residue disposition |
