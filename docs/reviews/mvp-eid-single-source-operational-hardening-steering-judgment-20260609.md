# EID Single Source Operational Hardening Gate — Steering Judgment

## Gate

| Item | Value |
|---|---|
| Gate | `EID Single Source Operational Hardening Gate` |
| Classification | `heavy` |
| Date | 2026-06-09 |
| Controller role | phaseflow controller |
| Design truth | `docs/design.md` |
| Control truth | `docs/implementation-control.md` |

## Source Evidence Read

- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/design.md`
- `docs/reviews/repo-review-20260609-165959.md`

## Current Control Truth

- Current phase is `MVP typed-template-to-agent report generation stabilization phase`.
- Current accepted gate is `row-field correctness test extension gate for retained equity-like holdings subset`.
- Current control next entry is `row-shape contract decision gate for retained manager / risk / non-equity holdings residuals`, or a separately authorized non-extractor phase.
- Current design truth still describes annual-report production source as EID / CSRC centralized disclosure primary source plus Eastmoney fallback.
- `docs/reviews/repo-review-20260609-165959.md` is a repository-level review artifact with `BLOCKED` verdict. Its Eastmoney finding is accepted as risk input for this steering decision only; it is not the current implementation target.

## Steering Decision

The controller accepts the user's steering decision to pause the row-shape residual entry and open a heavy truth-document gate for EID single-source operational hardening.

Current source policy target for this gate:

- `selected_source = eid`
- `mode = single_source_only`
- `fallback_enabled = false`
- Eastmoney production fallback is prohibited in this gate.
- Fund-company-site production fallback is prohibited in this gate.
- Eastmoney and fund-company-site sources remain deferred candidates only.
- Live EID/network/PDF smoke remains unauthorized unless the user separately approves a future live gate.

## Conflict Judgment

This steering decision does not hard-conflict with control truth because the current startup packet allows a separately authorized non-extractor phase. It does supersede the currently queued row-shape residual entry for sequencing purposes.

The row-shape contract decision gate is not rejected or deleted. It is queued and paused by steering until the EID single-source truth-doc gate finishes or the user redirects.

## Why Heavy

This gate is `heavy` because it changes source policy and implementation planning boundaries for production annual-report acquisition. It affects:

- annual-report source strategy;
- `FundDocumentRepository` / Fund documents ownership;
- fallback semantics;
- failure classification (`not_found`, `unavailable`, `schema_drift`, `identity_mismatch`, `integrity_error`);
- source metadata expectations;
- UI / Service / Host / renderer / quality-gate boundary constraints.

Under `AGENTS.md`, source policy, public contract, architecture boundary, and quality gate semantics require heavy classification.

## Authorization Boundary

Authorized now:

- truth-document upgrade planning;
- plan review;
- plan revision;
- targeted re-review;
- controller judgments;
- final truth-document revision of `docs/design.md`, `docs/implementation-control.md`, and `docs/current-startup-packet.md` only after plan acceptance.

Not authorized now:

- source code changes;
- test changes;
- README changes;
- live EID/network/PDF smoke;
- `FundDocumentRepository` live acquisition;
- fallback invocation;
- provider/runtime/config changes;
- PR, push, merge, mark-ready, release;
- local accepted commit.

## Truth-Doc Revision Principles

- Strictly separate current code fact from accepted future/current gate target.
- Do not write EID single source as already implemented.
- Do not write Eastmoney as current production fallback.
- Keep row-shape residual gate queued, not removed.
- Do not authorize live/network/PDF/fallback/implementation.
- Keep `FundDocumentRepository` as the only production annual-report access boundary.
- Keep `UI -> Service -> Host -> Agent` boundaries.
- Treat Dayu only as a single-source engineering strategy reference; do not introduce Dayu runtime dependency.

## Next Entry

Open planning worker handoff:

`EID single-source truth-doc revision plan gate`

The plan must be code-generation-ready for truth-doc revision only. It must not plan source/test implementation in this gate except as future implementation scope after separate authorization.

## Blocking Open Questions

None.
