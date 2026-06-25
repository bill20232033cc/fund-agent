# RR-09 Product Provenance Scope Decision

Final token:

`ACCEPT_RR_09_PRODUCT_PROVENANCE_SCOPE_SECTION_FLOOR_READY_FOR_CONTRACT_PLAN_NOT_READY`

## Gate

Gate: `RR-09 Product Provenance Scope Decision Gate`.

Authorization: `授权 RR-09 Product Provenance Scope Decision Gate: evaluate Dayu-style pragmatic provenance release scope`.

Classification: `heavy`, because this gate changes the proposed release-scope interpretation for Evidence Confirm residuals. This artifact is a decision artifact only. It does not change source code, tests, product runtime behavior, quality-gate semantics, checklist support, report-body rendering, provider/LLM defaults, PR state, tag, release or readiness. It does not run live/PDF, repository/source-helper/parser, product CLI or provider/LLM commands.

## Inputs

- `AGENTS.md`: evidence must be traceable; production annual PDF access must go through `FundDocumentRepository`; structured field extraction must stay behind Fund Processor/Extractor boundaries; Dayu is architecture reference and capability source, not production runtime dependency.
- `docs/design.md`: default product `analyze` runs repository-bounded Evidence Confirm with `warn` policy; CLI/UI expose safe summary and ECQ; report body does not render Evidence Confirm; checklist support and provider-backed semantic default-on remain future gates; release/readiness remains `NOT_READY`.
- `docs/reviews/evidence-confirm-productionization-release-boundary-residual-routing-20260623.md`: RR-09 may accept a reviewed disposition that product CLI EC `fail` under `warn` is release-acceptable with explicit user-facing semantics and owner, but must not bypass repository, add checklist/report-body support, switch provider default-on, tag/release or claim readiness.
- `docs/reviews/evidence-confirm-productionization-current-objective-gap-audit-after-a6-precheck-20260624.md`: default `analyze` / ECQ / repository pathway are partially proven; strict R1-R4 deterministic V2 precision remains open; B1 `017641 / 2024`, checklist/report-body/provider default and release/readiness remain open.
- Dayu-style research input is used only as product philosophy: audit should be the natural result of a stable data pipeline, not the product goal itself. It is not accepted as current runtime dependency or source of production behavior.

## Problem Reframing

The previous RR-09 execution path treated strict deterministic V2 row/value-match success as the practical release blocker for all R1-R4 samples. That path produced useful diagnostics, but it also coupled release scope to the hardest precision tier:

- section/source pathway provenance;
- table/row/cell locator adoption;
- value-token materialization;
- composite-field subvalue narrowing;
- V2 exact match classification.

Those are not the same product promise.

For the current product, the minimum promise is: user-visible claims must not be unsupported; every material numeric or factual claim must have repository-bounded disclosure provenance at an explicitly labeled tier. Strict row-level value-match is a stronger precision claim. It should remain visible and owned, but it should not be silently conflated with the minimum provenance claim unless the product surface claims row-level verification.

## Decision

RR-09 accepts a Dayu-style pragmatic provenance route as the next release-scope candidate:

1. Product release floor may be defined as repository-bounded provenance coverage, with `section` as the minimum accepted tier for this release, and `table`, `row`, `cell` as stronger tiers when available.
2. Deterministic V2 remains the main strict diagnostic path. It is not disabled, hidden, or replaced.
3. Under current `warn` policy, deterministic V2 value-match failure may be routed as `strict_precision_residual` with explicit owner and user-facing safe summary, instead of automatically blocking release scope.
4. Repository/source/pathway failure remains material. ECQ1-style pathway failure is still a blocker because it means the system cannot prove the claim is tied to the approved document boundary.
5. Claim-level missing provenance remains material. A report claim without at least section-level repository-bounded provenance is `provenance_missing`, not an acceptable pragmatic residual.
6. Report body still must not render Evidence Confirm or imply row-level verification. Evidence Confirm remains visible through CLI/UI safe summary and ECQ unless a later report-body gate changes that.
7. Checklist Evidence Confirm, provider-backed semantic default-on, FDD default-on parsing, direct parser/PDF/cache consumption, tag/release/readiness, and public row-level verification claims remain out of scope.

This route changes the release-scope question from:

> Do all strict V2 value-match checks pass at row/value precision?

to:

> Does the product give users a traceable report whose material claims have repository-bounded provenance at a clearly labeled tier, while strict precision failures remain visible as residual diagnostics?

## Accepted Product Contract For The Next Plan

The next planning gate must specify a no-live implementation contract for provenance tiers and residual disposition. It must preserve these semantics:

| Condition | Release-scope disposition | Required visibility |
|---|---|---|
| Repository/source/pathway unavailable or failed | blocker | ECQ/pathway issue |
| Material product claim has no repository-bounded provenance | blocker | `provenance_missing` or equivalent |
| Claim has section-level provenance only | acceptable floor for this release | provenance tier must be visible as `section`, not row proof |
| Claim has table/row/cell provenance | stronger accepted tier | provenance tier must be visible |
| Strict deterministic V2 value-match fails but section-or-better provenance exists | `strict_precision_residual` under `warn`; block under `block` | safe summary + ECQ/residual owner |
| Provider-backed semantic result is absent | non-blocking for current deterministic release floor | provider default remains off |
| Checklist/report-body Evidence Confirm is absent | non-blocking by accepted deferral | no report-body EC claim |

## Rejected Alternatives

- Disabling deterministic V2 to make release easier.
- Treating section-level provenance as proof of row-level value match.
- Treating Dayu as a production runtime dependency.
- Reading raw PDF/cache/source-helper/parser artifacts outside the Fund documents / Processor boundary.
- Adding report-body Evidence Confirm rendering in this gate.
- Adding checklist Evidence Confirm support in this gate.
- Changing quality-gate block/warn semantics without a separate implementation gate.
- Claiming release/readiness from this decision.

## Impact On A6

A6 remains useful and accepted as a strict precision improvement route: top-level `source_field_path=<field>` locator adoption may still reduce coarse-reference failures if later live/PDF evidence is authorized.

But after this decision, A6 live/PDF re-evidence is no longer the only mainline next step for RR-09. It becomes an optional strict-precision evidence path. The next mainline gate should first define the product provenance tier contract and how strict V2 failures are classified under the current `warn` policy.

## Next Gate

`RR-09 Product Provenance Tier Contract Planning Gate`

Minimum requirements for the next plan:

- define provenance tier names and public-safe summary wording;
- define how ECQ maps `provenance_missing`, pathway failure and `strict_precision_residual`;
- preserve `block` policy behavior for strict V2 failure if policy is explicitly `block`;
- add no-live tests for section-floor acceptance, missing-provenance block, pathway block and strict-precision residual under `warn`;
- avoid live/PDF, product CLI, provider/LLM, checklist, report-body, FDD default-on, tag, release and readiness unless separately authorized.

## Validation

Static review only:

- Read current startup/control state.
- Read release-boundary RR-09 acceptance criteria.
- Read current A6 objective gap audit.
- Cross-checked design boundaries for default `warn`, ECQ, report-body non-rendering, checklist deferral and provider semantic deferral.

No runtime command beyond repository text inspection was used. No source behavior changed.

Completion token:

`ACCEPT_RR_09_PRODUCT_PROVENANCE_SCOPE_SECTION_FLOOR_READY_FOR_CONTRACT_PLAN_NOT_READY`
