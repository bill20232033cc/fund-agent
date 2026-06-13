# Fixture Promotion Content / Promotion-state Manifest Plan Controller Judgment

Date: 2026-06-13

Gate: `Fixture Promotion Content / Promotion-state Manifest Planning Gate`

Controller verdict: `ACCEPT_WITH_AMENDMENTS_NOT_READY`

## Scope

This judgment accepts a plan only. It does not create or edit fixture promotion
content, fixture promotion manifests, golden-answer content, fixtures, source,
tests, runtime behavior, design/control truth, release/readiness state, PR state
or external state.

Release/readiness remains `NOT_READY`.

## Inputs Reviewed

- Rule truth: `AGENTS.md`
- Design truth: `docs/design.md`
- Control truth: `docs/implementation-control.md`
- Startup truth: `docs/current-startup-packet.md`
- Accepted downstream evidence judgment:
  `docs/reviews/mvp-fixture-promotion-year-aware-parser-downstream-evidence-controller-judgment-20260613.md`
- Plan:
  `docs/reviews/mvp-fixture-promotion-content-manifest-plan-20260613.md`
- DS plan review:
  `docs/reviews/mvp-fixture-promotion-content-manifest-plan-review-ds-20260613.md`
- MiMo plan review:
  `docs/reviews/mvp-fixture-promotion-content-manifest-plan-review-mimo-20260613.md`
- DS targeted re-review:
  `docs/reviews/mvp-fixture-promotion-content-manifest-plan-rereview-ds-20260613.md`
- MiMo targeted re-review:
  `docs/reviews/mvp-fixture-promotion-content-manifest-plan-rereview-mimo-20260613.md`

## Review Disposition

| Reviewer | Verdict | Controller disposition |
|---|---|---|
| DS plan review | `PASS_WITH_AMENDMENTS` | ACCEPT_WITH_AMENDMENTS. The required forbidden-path guard is accepted and has been added to the plan. |
| MiMo plan review | `PASS_WITH_AMENDMENTS` | ACCEPT_WITH_AMENDMENTS. The required row-scope validation and content-proof wording amendments are accepted and have been added to the plan. |
| DS targeted re-review | `PASS` | ACCEPT. The forbidden-path guard amendment is closed. |
| MiMo targeted re-review | `PASS` | ACCEPT. The row-scope and content-proof wording amendments are closed. |

## Accepted Plan Facts

| Fact | Disposition | Basis |
|---|---|---|
| A narrow implementation gate is justified before residual rollup. | ACCEPT | Current control truth identifies fixture promotion content/manifest absence as the next decision point; parser schema and downstream consumption semantics are already accepted. |
| The implementation source authority must be bounded to accepted tracked golden content, strict coverage evidence, parser implementation/downstream evidence and controller judgments. | ACCEPT | Plan and DS/MiMo reviews. |
| Downstream parser evidence is not fixture promotion content proof. | ACCEPT_AS_BOUNDARY | Plan amendment and MiMo targeted re-review. |
| Fixture promotion content proof can only come from the new manifest JSON plus implementation evidence/reviews/controller judgment. | ACCEPT | Plan amendment and MiMo targeted re-review. |
| The implementation gate must re-validate row scope before accepting the manifest. | ACCEPT | MiMo finding accepted; amended plan includes row-scope validation for exactly seven accepted `004393 / 2025` row identities and zero skipped fields. |
| The implementation gate must prove forbidden paths are unchanged. | ACCEPT | DS finding accepted; amended plan includes `git diff --name-only` and `git status --short` guards for source/tests/golden/control/design/README paths. |
| Release/readiness is ready. | REJECT | Planning gate is not readiness/release proof; `NOT_READY` remains current truth. |

## Accepted Implementation Contract For Next Gate

Next implementation gate may write only:

- `docs/reviews/mvp-fixture-promotion-state-manifest-20260613.json`
- `docs/reviews/mvp-fixture-promotion-content-manifest-implementation-evidence-20260613.md`
- subsequent DS/MiMo implementation review artifacts under `docs/reviews/`
- subsequent implementation controller judgment under `docs/reviews/`

It must not edit:

- `reports/golden-answers/golden-answer-prefill-reviewed.md`
- `reports/golden-answers/golden-answer.json`
- `docs/reviews/fixture-promotion-state-manifest-20260529.json`
- `fund_agent/`
- `tests/`
- fixtures
- runtime outputs
- README files
- `docs/design.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`

Accepted manifest schema:

- `schema_version`: `fund-agent.fixture-promotion-state.year-aware.v1`
- one entry only:
  `(fund_code="004393", report_year=2025, promotion_state="promoted_fixture",
  promotion_identity="fund_year")`
- no unknown top-level or entry fields
- no duplicate identity
- no legacy fund-code-only shape
- no fee rows, `turnover_rate`, skipped/deferred rows, other funds or other
  years inside the promotion scope

Required implementation validation includes:

- `uv run python -m json.tool docs/reviews/mvp-fixture-promotion-state-manifest-20260613.json`
- parser-load assertion that `fund_year_states == {("004393", 2025): "promoted_fixture"}` and `legacy_fund_states == {}`
- row-scope assertion against `reports/golden-answers/golden-answer.json`
- six targeted fixture-promotion parser tests listed in the plan
- forbidden-path guard for source/tests/golden/control/design/README paths
- whitespace checks for the new manifest and implementation evidence
- path-scoped status for the two allowed implementation artifacts

## Stop Conditions

The next gate must stop and return to controller if:

- tracked golden content no longer has exactly the seven accepted `004393 / 2025`
  row identities and zero skipped fields;
- implementation requires arbitrary workspace residue, old fund-code-only
  manifests, local PDFs/body files, unreviewed reports, live/provider/LLM access,
  `analyze`, `checklist`, readiness/release/PR commands or cleanup;
- any forbidden path is changed;
- any artifact implies release/readiness is ready;
- any implementation tries to promote fee rows, `turnover_rate`, skipped or
  deferred rows, another fund or another year.

## Next Entry

Accepted next mainline entry:

`Fixture Promotion Content / Promotion-state Manifest Implementation Gate`

Classification: `standard`.

The next gate remains local and non-live. It may implement only the accepted
manifest/content artifact and evidence path above. Release/readiness remains
`NOT_READY` after planning acceptance.
