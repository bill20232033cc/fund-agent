# EID Single Source Operational Hardening Truth-Doc Revision Plan

## Findings / Open Questions

Blocking questions: none

Non-blocking findings:

1. Current control truth still points the next entry to `row-shape contract decision gate for retained manager / risk / non-equity holdings residuals`; the accepted steering judgment supersedes this only for sequencing and must be written as `queued / paused by steering`, not deleted.
2. Current design truth still describes production annual-report sourcing as EID / CSRC centralized disclosure primary source plus Eastmoney fallback. That conflicts with this gate target: `selected_source=eid`, `mode=single_source_only`, `fallback_enabled=false`.
3. `docs/reviews/repo-review-20260609-165959.md` records a blocked Eastmoney integrity-classification risk. In this gate it is only deferred source-risk evidence, not an implementation target and not a reason to repair Eastmoney fallback.

## Worker Self-Check

- Current gate / role: planning worker for `EID Single Source Operational Hardening Gate`; not controller.
- Source of truth read: `AGENTS.md`, `docs/current-startup-packet.md`, `docs/implementation-control.md`, `docs/design.md`, `docs/reviews/repo-review-20260609-165959.md`, `docs/reviews/mvp-eid-single-source-operational-hardening-steering-judgment-20260609.md`.
- Scope boundary: write this plan artifact only; plan future truth-doc revision only.
- Stop conditions: no blocking question; stop if asked to change code/tests/live acquisition/fallback/commit/PR.
- Evidence and validation: no-live text validation only; direct evidence matrix below.

## Goal

Produce a code-generation-ready plan for a truth-document revision that aligns `docs/design.md`, `docs/implementation-control.md`, and `docs/current-startup-packet.md` with the accepted steering decision for EID single-source operational hardening.

The revision must make source-policy truth unambiguous while preserving current implementation facts:

- current code may still contain historical multi-source / fallback mechanics until a separate implementation gate changes it;
- this gate target is EID-only production annual-report source policy;
- Eastmoney and fund-company-site sources are deferred candidates only;
- no live EID/network/PDF/fallback/source acquisition is authorized by this plan.

## Non-Goals

- Do not modify source code.
- Do not modify tests.
- Do not modify README files.
- Do not run live EID, network, PDF, provider, curl, DNS, or smoke commands.
- Do not call `FundDocumentRepository` live acquisition.
- Do not enable, invoke, or validate fallback.
- Do not submit commit, push, PR, merge, mark-ready, release, or external state change.
- Do not write EID single source as already implemented.
- Do not write Eastmoney as current production fallback.
- Do not remove the row-shape residual gate.
- Do not authorize live / network / PDF / fallback / implementation.
- Do not introduce `dayu-agent`, `dayu.host`, or `dayu.engine` runtime dependency.
- Do not use or authorize `extra_payload` for explicit business/source parameters.

## Current Control Truth vs Target Conflict Inventory

| Area | Current truth observed | Steering target | Required revision stance |
|---|---|---|---|
| Current gate | Startup/control docs say `row-field correctness test extension gate for retained equity-like holdings subset` is accepted locally | Open `EID Single Source Operational Hardening Gate`, `classification=heavy` | Keep accepted row-field closeout as historical/current closeout; set active next gate to EID truth-doc revision gate |
| Next entry | Startup/control docs route to row-shape contract decision gate or separately authorized non-extractor phase | EID truth-doc gate temporarily supersedes row-shape entry | Mark row-shape residual gate `queued / paused by steering`; do not delete or reject it |
| Source policy | Design says EID / CSRC centralized disclosure primary source plus Eastmoney fallback | `selected_source=eid`, `mode=single_source_only`, `fallback_enabled=false` | Rewrite future/current gate target to EID-only; keep current code fact separate if code still contains fallback mechanics |
| Control doc source-truth policy | `docs/implementation-control.md` currently says EID is a preferred official registry locator but not a mandatory automatic extraction source or exclusive source truth, and says `official_document_url` may come from EID, fund-company website/CDN PDF, CNINFO PDF, or another official/first-party disclosure platform | EID is the accepted single-source gate target; fund-company website/CDN, CNINFO, and other first-party routes are not production sources in this gate | Rewrite to `selected_source=eid`, `mode=single_source_only`, `fallback_enabled=false`; relabel non-EID routes as deferred candidates or historical evidence-intake routes only |
| Control doc fallback eligibility | `docs/implementation-control.md` currently says `not_found` / `unavailable` remain fallback-eligible while `schema_drift` / `identity_mismatch` / `integrity_error` fail closed | `fallback_enabled=false`; all EID source outcomes are terminal under `single_source_only` unless a later gate re-authorizes fallback | Rewrite `not_found` / `unavailable` as terminal EID source failures that do not authorize fallback in this gate; preserve fail-closed semantics for `schema_drift`, `identity_mismatch`, and `integrity_error` |
| Eastmoney | Design/control still allow fallback on eligible categories; repo review found Eastmoney integrity failure can be misclassified as `unavailable` | Eastmoney production fallback prohibited in this gate | Record Eastmoney finding as deferred/future source risk only, owner `future source-candidate gate`; no repair target here |
| Fund company official site / CNINFO | Prior source identity evidence allowed official/first-party disclosure platforms under anchor rules | This gate prohibits fund-company-site production fallback | Rewrite as deferred candidates or historical evidence-intake routes, not current production fallback |
| Live/source acquisition | Current docs repeatedly forbid PDF/network/FDR/fallback live actions without authorization | Same | Preserve prohibition; this truth-doc gate is no-live |
| Boundary | Production annual report access must go through `FundDocumentRepository`; Service/UI/Host/renderer/quality gate cannot call concrete sources | Same | Keep boundary; source selection belongs to Fund documents internals |

## Truth-Doc Revision Objective

The revision must leave a later implementation worker with a single stable source-policy truth:

```text
selected_source = eid
mode = single_source_only
fallback_enabled = false
```

The truth-doc revision must define EID single-source operational hardening as the accepted target for the current heavy gate, while explicitly saying it is not yet implemented until a separate implementation gate changes code and passes review.

## Current Code Fact vs Accepted Target Separation Rules

Use these labels consistently:

- `Current code fact`: what the repository currently implements or accepted prior code gates already landed.
- `Accepted current gate target`: what this heavy truth-doc gate now plans and later truth-doc revision may authorize as the next implementation direction.
- `Deferred candidate`: source or behavior retained only for future research/implementation gate.
- `Historical evidence`: prior review/source-identity/manual-intake data that informs decisions but does not unlock current implementation.

Required wording discipline:

- If code still contains EID primary + Eastmoney fallback, describe it as `current code fact pending separate implementation revision`, not as desired policy.
- If describing EID single-source, write `accepted target for the EID single-source operational hardening gate`, not `already implemented`.
- If describing Eastmoney/fund-company-site/CNINFO, write `deferred candidate / historical evidence route`, not `production fallback`.
- If describing row-shape residuals, write `queued / paused by steering`, not `closed`, `superseded forever`, or `deleted`.

## EID Selected Source Policy Wording

Recommended wording for truth docs:

```text
EID single-source annual-report policy is the accepted target for the current heavy operational hardening gate:
selected_source=eid, mode=single_source_only, fallback_enabled=false.
Production annual-report acquisition must resolve operational annual reports through the EID source path only after a separate implementation gate lands the code change.
Eastmoney, fund-company official-site/CDN, CNINFO or other first-party disclosure routes are deferred source candidates and must not be used as production fallback in this gate.
Failure categories remain fail-closed for schema_drift, identity_mismatch and integrity_error; not_found/unavailable may be reported as EID source failures but do not authorize fallback under single_source_only mode.
```

Forbidden wording:

- `EID single source is implemented`
- `Eastmoney remains current production fallback`
- `fallback eligible categories allow Eastmoney fallback in this gate`
- `source acquisition/live smoke is authorized`
- `row-shape residual gate is removed`

## Document Update Scope

### `docs/design.md`

Update only source-policy and architecture-truth sections needed to align with steering:

- Header / status summary: add EID single-source operational hardening as accepted current gate target, not implemented code fact.
- §2 architecture boundary: preserve `FundDocumentRepository` as only annual-report access boundary; state source selection remains Fund documents internal, not Service/UI/Host/renderer/quality gate.
- §6.1 document repository layer:
  - change desired policy from EID primary + Eastmoney fallback to EID single-source target;
  - keep current code fact caveat if existing code still contains fallback implementation;
  - describe Eastmoney as deferred candidate and risk input.
- §6.3 external data table:
  - annual-report PDF source should show EID-only as accepted target/current gate direction;
  - Eastmoney/fund-company-site/CNINFO must not appear as current production fallback.
- §6.6 error/degradation strategy:
  - single-source mode reports EID failures without fallback;
  - `schema_drift`, `identity_mismatch`, `integrity_error` remain fail-closed;
  - `not_found` / `unavailable` no longer imply fallback in this gate.
- Decision comparison / review checklist sections:
  - align source policy row and review criterion with EID single-source target;
  - keep no `extra_payload`, no dayu runtime, no direct source/PDF/cache access by upper layers.

### `docs/implementation-control.md`

Update only current control surface:

- Top status block: add steering result and current heavy truth-doc gate.
- Startup Packet / Current Truth Guardrails:
  - mark current active entry as `EID single-source truth-doc revision gate`;
  - keep row-field closeout as accepted;
  - mark row-shape residual gate `queued / paused by steering`.
- Current control-doc source-truth policy:
  - replace the statement that EID is only a preferred locator and not exclusive source truth;
  - replace the statement that `official_document_url` may come from EID, fund-company website/CDN PDF, CNINFO PDF, or other official/first-party platforms as current source truth;
  - rewrite non-EID routes as deferred candidates or historical evidence-intake routes, not current production source routes.
- Current control-doc fallback policy:
  - replace the statement that `not_found` / `unavailable` remain fallback-eligible;
  - state that under `single_source_only`, `not_found` and `unavailable` are terminal EID source failures and do not authorize fallback;
  - preserve `schema_drift`, `identity_mismatch`, and `integrity_error` as fail-closed.
- Current Gate:
  - replace row-field gate as active gate with EID truth-doc revision gate, while preserving row-field as latest accepted closeout evidence.
- Current Accepted Artifacts:
  - add steering judgment artifact and this plan artifact after it exists;
  - do not remove existing row-field/source-identity artifacts.
- Open residuals:
  - Eastmoney integrity-classification finding -> `deferred-with-owner: future source-candidate/fallback implementation gate`;
  - row-shape residuals -> `queued / paused by steering`;
  - live EID proof -> unauthorized/future live evidence gate.
- Non-goal reminder:
  - no source/test/README/live/FDR/fallback/commit/PR.

### `docs/current-startup-packet.md`

Keep short and resumable:

- `Current gate`: `EID Single Source Operational Hardening Gate` / truth-doc revision planning path / `heavy`.
- `Current gate status`: truth-doc-only steering accepted; implementation not authorized.
- `Next entry point`: plan review -> plan revision -> targeted re-review -> controller judgment for truth-doc revision; after acceptance, only then truth-doc revision of the three docs.
- Preserve row-field closeout and row-shape residual facts in concise form.
- Repeat no-live/no-fallback/no-FDR/no-implementation/no-commit/no-PR boundaries.

### Review / Controller Artifacts

Allowed only under `docs/reviews/`:

- plan review artifacts;
- plan revision artifact if required;
- targeted re-review artifacts;
- controller judgment artifacts;
- final truth-doc revision evidence artifact if later authorized.

## EID Operational Topics to Document

The truth-doc revision must mention each topic at policy/contract level only. It must not claim code implementation.

| Topic | Required doc stance |
|---|---|
| EID discovery | The accepted target is to discover operational annual reports through EID only; no fund-company-site, CNINFO, Eastmoney, search result, LLM summary, or synthetic source unlocks production acquisition in this gate |
| Identity | EID result must be checked against fund code / fund identity / report year / annual report type; mismatch is `identity_mismatch` and fail-closed |
| PDF integrity | Content-Type, `%PDF-` magic, write integrity, and parser viability failures are `integrity_error` and fail-closed |
| Metadata | Metadata must support `selected_source=eid`, `resolved_source_name=eid`, `fallback_enabled=false`, `fallback_used=false`, EID URL/identifier, source failure category, and identity/integrity status; no hidden fallback metadata |
| Repository cache | Repository/cache policy must not reuse fallback-origin PDFs as EID-selected production source; any future cache key/source metadata change requires implementation gate |
| Parsed cache | Parsed annual-report cache must remain tied to schema version and source identity; source mismatch/schema drift invalidates or blocks reuse rather than being silently accepted |
| Failure reporting | `not_found` and `unavailable` are EID terminal source failures in single-source mode; they do not authorize fallback |
| Boundary | UI, Service, Host, renderer and quality gate still cannot call concrete sources, PDF cache or downloader directly |

## Eastmoney Finding Disposition

`docs/reviews/repo-review-20260609-165959.md` finding:

- Status for this gate: `deferred-with-owner`.
- Owner/destination: future source-candidate or fallback implementation gate, if the user later re-authorizes Eastmoney as a production candidate.
- Current gate use: risk evidence explaining why Eastmoney must not remain in production fallback wording.
- Current gate non-use: do not repair Eastmoney code, do not add tests, do not validate live fallback, do not write Eastmoney as current fallback.

Truth-doc wording:

```text
Eastmoney remains a deferred source candidate only. The 2026-06-09 repository review recorded an integrity-classification risk in the Eastmoney wrapper; that finding is retained as future source-candidate risk and is not a current implementation target under the EID single-source gate.
```

## Row-Shape Residual Gate Disposition

Required wording:

```text
The row-shape contract decision gate for retained manager / risk / non-equity holdings residuals remains queued. It is paused by steering while the EID single-source truth-doc gate runs. It is not rejected, deleted, or converted into this source-policy gate.
```

Residuals to preserve:

- `manager`
- retained `risk`
- `006597` bond top holding
- `110020` target ETF holding

## Allowed Files

For this planning gate:

- `docs/reviews/mvp-eid-single-source-operational-hardening-truth-doc-revision-plan-20260609.md`

For later truth-doc revision only after plan acceptance and controller authorization:

- `docs/design.md`
- `docs/implementation-control.md`
- `docs/current-startup-packet.md`
- `docs/reviews/*eid-single-source-operational-hardening*`
- `docs/reviews/*truth-doc-revision*`
- `docs/reviews/*plan-review*` only if explicitly tied to this gate

## Forbidden Files

- `fund_agent/**`
- `tests/**`
- `README.md`
- `fund_agent/README.md`
- `fund_agent/host/README.md`
- `fund_agent/agent/README.md`
- `fund_agent/fund/README.md`
- `fund_agent/config/README.md`
- `tests/README.md`
- `pyproject.toml`
- `uv.lock`
- `reports/**`
- `reviews/**`
- any PDF/cache/source payload
- any file outside the allowed list unless controller explicitly opens a new gate

## Revision Slices

### Slice 0 — Baseline Evidence and Scope Guard

Objective: preserve exact gate boundaries before any truth-doc edit.

Allowed files: review artifacts only.

Steps:

1. Re-read branch/status and the six required files.
2. Confirm no tracked truth docs are already dirty from another owner.
3. Record that this gate is heavy, no-live, truth-doc-only.
4. Stop if source/test/README edits or live commands are requested.

Completion signal: plan/review artifacts agree on allowed/forbidden files and no-live scope.

### Slice 1 — Design Truth Source-Policy Revision

Objective: make `docs/design.md` distinguish current code fact from EID single-source target.

Allowed files: `docs/design.md`, gate review artifacts.

Exact changes:

1. Add EID single-source gate target to status/decision summary.
2. Rewrite document repository source-policy section to EID-only target with code-fact caveat.
3. Remove or relabel Eastmoney production fallback wording.
4. Preserve `FundDocumentRepository` boundary and failure category semantics.
5. Add metadata/cache/parsed-cache policy language at design level only.
6. Keep Dayu runtime and `extra_payload` prohibitions.

Stop condition: any change would imply code already implements EID-only source selection.

### Slice 2 — Control Truth Revision

Objective: update `docs/implementation-control.md` current gate and residual ownership.

Allowed files: `docs/implementation-control.md`, gate review artifacts.

Exact changes:

1. Set active gate to `EID Single Source Operational Hardening Gate`, `classification=heavy`.
2. Add steering judgment and plan artifacts to accepted/current evidence once accepted.
3. Mark row-shape gate `queued / paused by steering`.
4. Replace the current control-doc statement that EID is a preferred locator but not exclusive source truth; the revised target must state `selected_source=eid`, `mode=single_source_only`, `fallback_enabled=false`.
5. Replace the current control-doc statement that `official_document_url` may come from EID, fund-company website/CDN PDF, CNINFO PDF, or other official/first-party platforms; the revised target must make non-EID routes deferred candidates or historical evidence-intake routes only.
6. Replace the current control-doc statement that `not_found` / `unavailable` are fallback-eligible; the revised target must state they are terminal EID source failures under `single_source_only` and do not authorize fallback.
7. Move Eastmoney finding to deferred/future source risk.
8. Preserve no-live/no-FDR/no-fallback/no-code/no-test/no-PR boundaries.

Stop condition: control doc starts authorizing implementation, live source acquisition, fallback, commit, or PR.

### Slice 3 — Startup Packet Revision

Objective: make resume entry short and aligned with the new gate.

Allowed files: `docs/current-startup-packet.md`, gate review artifacts.

Exact changes:

1. Update `Current gate`, `classification`, `status`, and `next entry point`.
2. Preserve latest row-field closeout and row-shape residual list.
3. Add one concise source-policy paragraph for EID-only target that includes all three exact values: `selected_source=eid`, `mode=single_source_only`, `fallback_enabled=false`.
4. If the startup packet mirrors or summarizes the old control-doc policy, replace any statement that EID is non-exclusive or that `official_document_url` may currently come from fund-company website/CDN, CNINFO, or other first-party routes; these routes must be deferred/historical evidence only.
5. If the startup packet mirrors or summarizes fallback eligibility, replace any statement that `not_found` / `unavailable` authorize fallback; under `single_source_only` they are terminal EID source failures.
6. Repeat unauthorized actions.

Stop condition: packet becomes a long historical ledger or drops required row-shape residual context.

### Slice 4 — Consistency and Evidence Closeout

Objective: no-live verification and review readiness.

Allowed files: review/controller artifacts only, plus the three truth docs if already edited in prior slices.

Exact checks:

1. `rg -n "Eastmoney fallback|fallback 到 Eastmoney|Eastmoney production|fund-company-site production fallback|CNINFO.*fallback" docs/design.md docs/implementation-control.md docs/current-startup-packet.md`
2. `rg -n "selected_source=eid" docs/design.md docs/implementation-control.md docs/current-startup-packet.md`
3. `rg -n "mode=single_source_only" docs/design.md docs/implementation-control.md docs/current-startup-packet.md`
4. `rg -n "fallback_enabled=false" docs/design.md docs/implementation-control.md docs/current-startup-packet.md`
5. `rg -n "paused by steering|queued" docs/implementation-control.md docs/current-startup-packet.md`
6. `rg -n "FundDocumentRepository" docs/design.md docs/implementation-control.md docs/current-startup-packet.md`
7. `rg -n "extra_payload|dayu-agent|dayu.host|dayu.engine" docs/design.md docs/implementation-control.md docs/current-startup-packet.md`
8. `git diff --check -- docs/design.md docs/implementation-control.md docs/current-startup-packet.md docs/reviews`

Expected result:

- no current-production Eastmoney fallback wording remains;
- each target doc has all three exact policy values: `selected_source=eid`, `mode=single_source_only`, `fallback_enabled=false`;
- EID single-source policy is present as accepted target, not implemented fact;
- row-shape gate appears as queued/paused;
- `FundDocumentRepository` boundary remains present;
- no `dayu` runtime or `extra_payload` authorization is introduced.

## No-Live Validation Matrix

| Check | Command | Expected |
|---|---|---|
| `docs/design.md` selected source | `rg -n "selected_source=eid" docs/design.md` | At least one hit in `docs/design.md`; wording must describe accepted gate target, not implemented fact |
| `docs/design.md` mode | `rg -n "mode=single_source_only" docs/design.md` | At least one hit in `docs/design.md`; no multi-source production mode claim may remain |
| `docs/design.md` fallback disabled | `rg -n "fallback_enabled=false" docs/design.md` | At least one hit in `docs/design.md`; `not_found` / `unavailable` must not authorize fallback |
| `docs/implementation-control.md` selected source | `rg -n "selected_source=eid" docs/implementation-control.md` | At least one hit in `docs/implementation-control.md`; replaces old EID-not-exclusive control wording |
| `docs/implementation-control.md` mode | `rg -n "mode=single_source_only" docs/implementation-control.md` | At least one hit in `docs/implementation-control.md`; non-EID official routes must be deferred/historical evidence only |
| `docs/implementation-control.md` fallback disabled | `rg -n "fallback_enabled=false" docs/implementation-control.md` | At least one hit in `docs/implementation-control.md`; `not_found` / `unavailable` are terminal EID source failures |
| `docs/current-startup-packet.md` selected source | `rg -n "selected_source=eid" docs/current-startup-packet.md` | At least one hit in `docs/current-startup-packet.md`; resume packet mirrors control truth |
| `docs/current-startup-packet.md` mode | `rg -n "mode=single_source_only" docs/current-startup-packet.md` | At least one hit in `docs/current-startup-packet.md`; resume packet does not re-open non-EID production routes |
| `docs/current-startup-packet.md` fallback disabled | `rg -n "fallback_enabled=false" docs/current-startup-packet.md` | At least one hit in `docs/current-startup-packet.md`; resume packet does not authorize fallback |
| No production Eastmoney fallback wording | `rg -n "Eastmoney fallback|fallback 到 Eastmoney|production fallback" docs/design.md docs/implementation-control.md docs/current-startup-packet.md` | No current-production fallback claim; any hit must be deferred/future risk wording |
| Row-shape retained | `rg -n "row-shape|paused by steering|queued" docs/implementation-control.md docs/current-startup-packet.md` | Row-shape residual gate remains queued/paused |
| FDR boundary retained | `rg -n "FundDocumentRepository" docs/design.md docs/implementation-control.md docs/current-startup-packet.md` | FDR remains the only production annual-report access boundary |
| No dayu runtime / `extra_payload` authorization | `rg -n "extra_payload|dayu-agent|dayu.host|dayu.engine" docs/design.md docs/implementation-control.md docs/current-startup-packet.md` | Any hit must be a prohibition or boundary statement, not authorization |
| Formatting | `git diff --check -- docs/design.md docs/implementation-control.md docs/current-startup-packet.md docs/reviews` | Pass |

Forbidden validation:

- no `pytest` required for truth-doc-only plan unless controller later asks;
- no live EID/network/PDF/FDR/fallback/provider command;
- no curl/DNS/socket/browser acquisition;
- no cache inspection or PDF parsing.

## Direct Evidence Matrix

| Evidence | Direct fact used | Plan consequence |
|---|---|---|
| `AGENTS.md` | Heavy gates cover source policy, public contract, architecture boundary and quality semantics; production annual-report access must go through `FundDocumentRepository`; fallback fail-closed categories are mandatory | Classify gate as heavy; preserve FDR boundary and failure taxonomy |
| `docs/current-startup-packet.md` | Current next entry is row-shape residual gate; PDF/network/FDR/fallback/source acquisition remain unauthorized | Mark row-shape queued/paused; keep no-live boundary |
| `docs/implementation-control.md` | Current control truth still allows eligible annual-report fallback and records EID as preferred but not exclusive in source identity context | Truth-doc revision must update active control surface |
| `docs/design.md` | Document repository section says EID/CSRC primary source plus Eastmoney fallback; external data table repeats that source model | Design revision must relabel or replace fallback wording |
| `docs/reviews/repo-review-20260609-165959.md` | Repo-level review is BLOCKED on Eastmoney integrity failure being downgraded to unavailable/fallback-eligible | Treat Eastmoney as deferred risk; do not keep as production fallback target |
| `docs/reviews/mvp-eid-single-source-operational-hardening-steering-judgment-20260609.md` | Steering target is `selected_source=eid`, `mode=single_source_only`, `fallback_enabled=false`; row-shape paused, not deleted; only truth-doc planning/review/revision authorized | This plan scopes only truth docs and review/controller artifacts |

## Review Criteria

Plan review must fail if:

- the plan authorizes source/test/README implementation;
- the plan authorizes live EID/network/PDF/FDR/fallback;
- the plan leaves implementation agents to decide source policy;
- the plan lets Eastmoney remain current production fallback;
- the plan deletes row-shape residual gate;
- the plan lacks direct evidence mapping;
- the plan does not separate current code fact from accepted target;
- the plan omits metadata/cache/parsed-cache wording scope;
- the plan introduces dayu runtime or `extra_payload`.

## Targeted Re-Review Criteria

Targeted re-review should inspect only accepted findings from plan review and must confirm:

- all accepted findings are fixed or explicitly deferred with owner;
- no new authorization was introduced;
- allowed/forbidden files remain intact;
- EID selected source wording is exact enough for a later truth-doc revision worker;
- Eastmoney and row-shape dispositions match steering.

## Stop Conditions

Stop and return to controller/user if any of these occurs:

- tracked dirty changes exist in `docs/design.md`, `docs/implementation-control.md`, or `docs/current-startup-packet.md` and ownership is unclear;
- reviewer identifies a blocking scope or source-policy ambiguity;
- any required truth-doc wording would contradict current code facts unless clearly labeled as target/future;
- implementation, tests, live source acquisition, fallback, commit, push, PR, or external state is requested;
- an agent attempts to use `FundDocumentRepository` live acquisition or inspect/download PDFs;
- a change would introduce dayu runtime dependency or `extra_payload` business/source parameters.

## Residual Risks

| Risk | Classification | Owner / destination |
|---|---|---|
| Current code may still implement EID primary + Eastmoney fallback after truth-doc revision | accepted current-code/target gap | Future EID single-source implementation gate |
| Eastmoney integrity-classification bug remains open | deferred source-candidate risk | Future Eastmoney/fallback candidate gate only if user re-authorizes fallback |
| No live EID proof under this gate | unauthorized evidence gap | Future live EID evidence gate with explicit network/PDF/FDR authorization |
| Row-shape residuals remain unresolved | queued / paused by steering | Future row-shape contract decision gate |
| Cache/source metadata changes are not implemented | accepted implementation residual | Future implementation gate with tests |

## Final Controller Judgment Criteria

Controller may accept the truth-doc revision plan only if:

- Blocking questions remain `none`;
- plan review and targeted re-review, if needed, pass;
- allowed files and forbidden files are explicit;
- EID policy wording is `selected_source=eid`, `mode=single_source_only`, `fallback_enabled=false`;
- current code fact vs accepted target is clearly separated;
- Eastmoney is deferred/future risk, not production fallback;
- row-shape residual gate is queued/paused, not removed;
- no live/network/PDF/FDR/fallback/implementation/commit/PR is authorized;
- final no-live validation matrix is executable without external access.

After controller acceptance, the next authorized worker should revise only `docs/design.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md`, and gate-specific review/controller artifacts under this plan. Any source code, test, README, live source acquisition, fallback, commit, push, or PR action requires a separate explicit gate and authorization.
