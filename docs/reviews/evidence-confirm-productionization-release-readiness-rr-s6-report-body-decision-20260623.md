# Evidence Confirm Productionization Release/readiness RR-S6 Report-body Decision

## Verdict

`RR_S6_REPORT_BODY_EVIDENCE_CONFIRM_OPTION_A_OUTSIDE_BODY_NOT_READY`

Release/readiness remains `NOT_READY`.

## Decision

RR-S6 accepts Option A for this release: keep Evidence Confirm outside the investment report body.

Evidence Confirm remains visible through CLI safe summary output and quality gate ECQ issue projection. The renderer must not add an Evidence Confirm section, per-chapter Evidence Confirm labels, raw semantic status text, source excerpt, PDF/cache path, parser JSON, provider payload, or source adapter object to the report body in this release.

## Basis

The accepted release/readiness plan recommends Option A unless a later explicit product-owner/controller decision overrides it.

Current behavior already exposes the product surface needed for this release:

- product `fund-analysis analyze` runs repository-bounded Evidence Confirm with `warn` policy
- product `fund-analysis analyze-annual-period` inherits the current-year Evidence Confirm summary and now prints safe summary lines
- quality gate can project Evidence Confirm summary into ECQ issues
- current renderer intentionally does not render Evidence Confirm in Markdown

Putting Evidence Confirm into report Markdown would require a separate UX/audit-contract review because report-body wording must not mix source-support metadata with investment conclusion language.

## Required Assertions

- Report body must not mix audit state with buy/sell advice, final judgment, or investment action wording.
- No raw excerpts, PDF/cache paths, provider payloads, parser JSON, source adapter objects, provider bodies, prompts, claims, or API keys may render.
- Any future report-body Evidence Confirm support must be covered by wording tests and audit tests.
- Any future per-chapter Evidence Confirm labels require separate wording review and audit contract review.
- Any implementation requiring public `EvidenceAnchor` or `EvidenceSourceKind` expansion must enter a separate reviewed design/implementation gate.

## Non-goals

- No renderer implementation was added.
- No Service request/result contract was changed.
- No annual-period report Markdown behavior was changed.
- No checklist Evidence Confirm support was added.
- No provider/live/PDF/source command was run.
- No push, PR mutation, mark-ready, merge, request-reviewer action, or release transition was performed.

## Residual Disposition

RR-08 is explicitly dispositioned for this release as `deferred_with_owner`.

- Owner: product-owner/controller decision gate for future report-body Evidence Confirm UX.
- Destination: future report-body Evidence Confirm rendering design gate, only if product owner wants audit metadata in report Markdown.
- Current release scope: Evidence Confirm remains outside report body.

## Next Gate

Proceed to `RR-S7 - Docs / Control / Hygiene Readiness Gate`.

RR-S7 must sync current behavior only and classify local artifacts/residue that could be mistaken for source truth, PR readiness, release evidence, or current implementation truth. It must not introduce new Evidence Confirm product behavior.
