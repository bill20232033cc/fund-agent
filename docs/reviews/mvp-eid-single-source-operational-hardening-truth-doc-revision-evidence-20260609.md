# EID Single Source Operational Hardening Truth-Doc Revision Evidence

## Gate

| Item | Value |
|---|---|
| Gate | `EID Single Source Operational Hardening Gate` |
| Classification | `heavy` |
| Role | truth-doc revision worker, not controller |
| Scope | truth-doc-only revision |
| Date | 2026-06-09 |

## Source Artifacts Read

- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/design.md`
- `docs/reviews/repo-review-20260609-165959.md`
- `docs/reviews/mvp-eid-single-source-operational-hardening-steering-judgment-20260609.md`
- `docs/reviews/mvp-eid-single-source-operational-hardening-truth-doc-revision-plan-20260609.md`
- `docs/reviews/mvp-eid-single-source-operational-hardening-truth-doc-revision-plan-acceptance-controller-judgment-20260609.md`

## Modified Sections

### `docs/design.md`

- Header status and change summary now record EID single-source as accepted gate target, not implemented code fact.
- §6.1 document repository layer now separates current code fact from accepted source policy target.
- §6.1 source failure table now states `not_found` and `unavailable` are terminal EID source failures under `single_source_only`; `schema_drift`, `identity_mismatch` and `integrity_error` remain fail-closed.
- §6.1 cache and metadata wording now records future implementation expectations for EID source identity, no hidden fallback metadata, parsed cache source identity and schema version.
- §6.3 external data table now records annual-report PDF source target as EID single-source only.
- §6.6 error/degradation table now removes current fallback authorization from PDF download failure wording.
- Directory overview and decision table now avoid current production fallback wording and keep Eastmoney / fund-company website/CDN / CNINFO as deferred candidates or historical evidence routes.

### `docs/implementation-control.md`

- Top status and current gate closeout now route the active gate to `EID Single Source Operational Hardening Gate`.
- Current Truth Guardrails now record `selected_source=eid`, `mode=single_source_only`, `fallback_enabled=false`.
- Current gate table now marks the gate as `heavy`, truth-doc-only, and future implementation direction only.
- Current accepted evidence list now includes the steering judgment, accepted truth-doc revision plan and plan acceptance judgment.
- Open residuals now include EID implementation residual, deferred Eastmoney risk, queued row-shape gate and unauthorized live EID proof.

### `docs/current-startup-packet.md`

- Current Mainline now records the active gate as EID single-source operational hardening truth-doc revision.
- Startup packet now includes all exact policy values: `selected_source=eid`, `mode=single_source_only`, `fallback_enabled=false`.
- Startup packet now records Eastmoney / fund-company website/CDN / CNINFO as deferred or historical evidence routes only.
- Startup packet now preserves row-shape residuals as queued / paused by steering.
- Current residuals now include the EID implementation residual and no-live/no-source/no-test/no-README boundary.

## Boundaries Preserved

- Current code fact and accepted gate target remain separate; EID single-source is not written as already implemented.
- `FundDocumentRepository` remains the only production annual-report access boundary.
- UI, Service, Host, renderer and quality gate remain prohibited from direct concrete source, PDF cache, downloader or parser access.
- Eastmoney, fund-company website/CDN and CNINFO are deferred source candidates or historical evidence routes only in this gate.
- Row-shape contract decision gate remains queued / paused by steering; it was not deleted or rejected.
- `not_found` and `unavailable` do not authorize fallback under `mode=single_source_only`.
- `schema_drift`, `identity_mismatch` and `integrity_error` remain fail-closed.
- Dayu remains strategy/reference only; no `dayu-agent`, `dayu.host` or `dayu.engine` runtime authorization was added.
- Explicit source/business parameters remain prohibited from `extra_payload`.

## No-Live Validation Results

All validation commands were no-live text checks. No live EID/network/PDF/FDR/fallback/provider/curl/DNS/socket/smoke command was run.

| Command | Result |
|---|---|
| `rg -n "selected_source=eid" docs/design.md` | PASS, hits include lines 5, 650, 657, 676, 711, 1096 |
| `rg -n "mode=single_source_only" docs/design.md` | PASS, hits include lines 5, 650, 657, 711, 1096 |
| `rg -n "fallback_enabled=false" docs/design.md` | PASS, hits include lines 5, 650, 657, 676, 711, 1096 |
| `rg -n "selected_source=eid" docs/implementation-control.md` | PASS, hits include lines 9, 63, 71, 595 |
| `rg -n "mode=single_source_only" docs/implementation-control.md` | PASS, hits include lines 9, 63, 71, 595 |
| `rg -n "fallback_enabled=false" docs/implementation-control.md` | PASS, hits include lines 9, 63, 71, 595 |
| `rg -n "selected_source=eid" docs/current-startup-packet.md` | PASS, hits include lines 20, 332 |
| `rg -n "mode=single_source_only" docs/current-startup-packet.md` | PASS, hits include lines 20, 21, 332 |
| `rg -n "fallback_enabled=false" docs/current-startup-packet.md` | PASS, hits include lines 20, 332 |
| `rg -n "row-shape\|paused by steering\|queued" docs/implementation-control.md docs/current-startup-packet.md` | PASS, hits include startup lines 21, 22, 334 and implementation-control lines 9, 10, 72, 73, 597 |
| `rg -n "FundDocumentRepository" docs/design.md docs/implementation-control.md docs/current-startup-packet.md` | PASS, boundary hits present in all three truth docs |
| `rg -n "extra_payload\|dayu-agent\|dayu.host\|dayu.engine" docs/design.md docs/implementation-control.md docs/current-startup-packet.md` | PASS, hits are prohibition/boundary/reference-only wording |
| `git diff --check -- docs/design.md docs/implementation-control.md docs/current-startup-packet.md docs/reviews` | PASS, no output |

## Prohibited Actions Audit

- Source code modified: no.
- Tests modified: no.
- README modified: no.
- Config/provider/runtime/budget modified: no.
- Live EID/network/PDF/FDR acquisition/fallback/provider/curl/DNS/socket/smoke run: no.
- Commit/push/PR/merge/release/mark-ready run: no.

## Completion Status

Truth-doc revision completed within the accepted plan scope.
