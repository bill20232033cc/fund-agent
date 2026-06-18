# Fixture Promotion Content / Promotion-state Manifest Plan

Date: 2026-06-13

Gate: `Fixture Promotion Content / Promotion-state Manifest Planning Gate`

Role: planning worker, not controller

verdict: `IMPLEMENTATION_RECOMMENDED`

Release/readiness state: `NOT_READY`

Allowed write for this gate: this plan artifact only.

## goal

Decide whether the next local gate should create a reviewed, year-aware fixture
promotion state manifest/content path for `004393 / 2025`, or defer the
remaining blocker to release/readiness residual handling.

Decision: implementation is recommended, but only as a narrow manifest/content
artifact gate. The implementation gate may create an accepted year-aware
promotion-state manifest for the already accepted `004393 / 2025` tracked
golden content. It must first re-validate that the tracked JSON still contains
exactly the seven accepted `004393 / 2025` row identities, zero skipped fields
and no fee rows, `turnover_rate`, skipped/deferred rows, other funds or other
years inside the promotion scope. It must not edit golden-answer content,
fixture content, source/tests/runtime behavior, control/design truth,
release/readiness state or external PR/release state.

This recommendation depends on a bounded source of authority:

- accepted tracked golden content write for exactly seven `004393 / 2025` rows;
- accepted strict-golden coverage evidence for the current tracked JSON surface;
- accepted year-aware fixture promotion parser/schema implementation;
- accepted downstream parser evidence showing exact `(fund_code, report_year)`
  consumption and fail-closed wrong-year/legacy behavior;
- controller judgments for the above gates.

If any implementation or review path needs arbitrary workspace residue, old
fund-code-only manifests, unreviewed fixture content, live/provider/LLM access,
or a broader readiness claim, the implementation must stop and defer instead.
Downstream parser evidence may be cited only as parser/consumption compatibility
evidence. The next implementation gate's manifest JSON, implementation evidence,
reviews and controller judgment are the fixture promotion content proof.

## non-goals

- Do not implement anything in this planning gate.
- Do not edit `fund_agent/`, `tests/`, `reports/golden-answers/`, fixture
  directories, runtime outputs, `docs/design.md`, `docs/implementation-control.md`
  or `docs/current-startup-packet.md`.
- Do not create fixture promotion content/manifest in this planning gate.
- Do not add fee rows, `turnover_rate`, skipped rows or deferred rows to
  `004393 / 2025`.
- Do not use `docs/reviews/fixture-promotion-state-manifest-20260529.json` as
  current proof; it is legacy/fund-code-oriented historical evidence.
- Do not run live, provider, LLM, `analyze`, `checklist`, readiness, release,
  PR, push, merge, cleanup, archive or external-state commands.
- Do not claim release/readiness. Release/readiness remains `NOT_READY`.

## accepted facts

| Fact | Disposition | Basis |
|---|---|---|
| Current active gate is planning-only and allowed writes are plan/review/controller artifacts under `docs/reviews/`. | ACCEPT | `docs/current-startup-packet.md`; `docs/implementation-control.md` |
| `004393 / 2025` tracked golden content already exists with exactly seven active rows in reviewed Markdown and generated JSON. | ACCEPT | `reports/golden-answers/golden-answer-prefill-reviewed.md`; `reports/golden-answers/golden-answer.json`; `docs/reviews/mvp-004393-2025-tracked-golden-content-write-implementation-controller-judgment-20260613.md` |
| The seven rows are `basic_identity.fund_name`, `basic_identity.fund_code`, `basic_identity.management_company`, `basic_identity.custodian`, `basic_identity.inception_date`, `product_profile.investment_objective`, and `benchmark.benchmark_name`. | ACCEPT | same tracked golden content write judgment |
| `fee_schedule.management_fee`, `fee_schedule.custody_fee`, `turnover_rate`, skipped rows and deferred rows are excluded from `004393 / 2025` tracked golden content. | ACCEPT | same tracked golden content write judgment; `docs/reviews/mvp-004393-2025-fixture-promotion-strict-golden-coverage-evidence-controller-judgment-20260613.md` |
| Strict golden coverage is accepted as year-aware for the current tracked JSON surface. | ACCEPT | `docs/reviews/mvp-004393-2025-fixture-promotion-strict-golden-coverage-evidence-controller-judgment-20260613.md` |
| Fixture promotion content/manifest for current `004393 / 2025` has not been created. | ACCEPT | `docs/current-startup-packet.md`; `docs/implementation-control.md`; downstream evidence controller judgment |
| Downstream parser evidence is accepted for exact year-aware consumption, wrong-year non-cross-application and legacy fund-code-only diagnostic routing. | ACCEPT | `docs/reviews/mvp-fixture-promotion-year-aware-parser-downstream-evidence-controller-judgment-20260613.md` |
| Downstream parser evidence is not content proof and does not create accepted fixture promotion content/manifest. | ACCEPT_AS_BOUNDARY | same downstream evidence controller judgment |
| Release/readiness remains `NOT_READY`. | ACCEPT | current startup packet, control doc and accepted controller judgments |

## proposed write set

For the next implementation gate only:

1. Create one reviewed manifest/content artifact:
   `docs/reviews/mvp-fixture-promotion-state-manifest-20260613.json`.
2. Create one implementation evidence artifact:
   `docs/reviews/mvp-fixture-promotion-content-manifest-implementation-evidence-20260613.md`.
3. Review artifacts after implementation:
   `docs/reviews/mvp-fixture-promotion-content-manifest-implementation-review-ds-20260613.md`
   and
   `docs/reviews/mvp-fixture-promotion-content-manifest-implementation-review-mimo-20260613.md`.
4. Controller judgment after reviews:
   `docs/reviews/mvp-fixture-promotion-content-manifest-implementation-controller-judgment-20260613.md`.

Do not edit:

- `reports/golden-answers/golden-answer-prefill-reviewed.md`
- `reports/golden-answers/golden-answer.json`
- `docs/reviews/fixture-promotion-state-manifest-20260529.json`
- source, tests, fixtures, runtime outputs, README files, control docs or design
  docs.

## schema contract

The implementation gate must use the already implemented parser schema:

```json
{
  "schema_version": "fund-agent.fixture-promotion-state.year-aware.v1",
  "accepted_as_of": "2026-06-13",
  "source_artifacts": [
    "reports/golden-answers/golden-answer-prefill-reviewed.md",
    "reports/golden-answers/golden-answer.json",
    "docs/reviews/mvp-004393-2025-tracked-golden-content-write-implementation-controller-judgment-20260613.md",
    "docs/reviews/mvp-004393-2025-fixture-promotion-strict-golden-coverage-evidence-controller-judgment-20260613.md",
    "docs/reviews/mvp-fixture-promotion-state-year-aware-schema-parser-implementation-controller-judgment-20260613.md",
    "docs/reviews/mvp-fixture-promotion-year-aware-parser-downstream-evidence-controller-judgment-20260613.md"
  ],
  "entries": [
    {
      "fund_code": "004393",
      "report_year": 2025,
      "promotion_state": "promoted_fixture",
      "promotion_identity": "fund_year",
      "evidence_artifacts": [
        "docs/reviews/mvp-004393-2025-tracked-golden-content-write-implementation-controller-judgment-20260613.md",
        "docs/reviews/mvp-004393-2025-fixture-promotion-strict-golden-coverage-evidence-controller-judgment-20260613.md",
        "docs/reviews/mvp-fixture-promotion-year-aware-parser-downstream-evidence-controller-judgment-20260613.md"
      ]
    }
  ]
}
```

Required invariants:

- top-level keys are exactly `schema_version`, `accepted_as_of`,
  `source_artifacts`, `entries`;
- `schema_version` is exactly
  `fund-agent.fixture-promotion-state.year-aware.v1`;
- every `source_artifacts` and `evidence_artifacts` item is a string path to
  tracked accepted content or accepted review/controller evidence;
- entry keys are exactly `fund_code`, `report_year`, `promotion_state`,
  `promotion_identity`, `evidence_artifacts`;
- `promotion_identity` is exactly `fund_year`;
- identity is exact `(fund_code, report_year)`;
- duplicate `(fund_code, report_year)` entries are invalid;
- no field may be added to carry arbitrary notes, raw body text, live evidence
  payload, extra payload or readiness disposition;
- `promoted_fixture` applies only to the accepted seven-row tracked golden
  content for `004393 / 2025`; it does not promote fee rows, `turnover_rate`,
  skipped rows, deferred rows, other funds or other years.

## validation matrix

Plan artifact validation for this gate:

```bash
git diff --check --no-index -- /dev/null docs/reviews/mvp-fixture-promotion-content-manifest-plan-20260613.md
```

Expected result: no whitespace error output. With `--no-index` against
`/dev/null`, Git may still return non-zero because the new file differs from
`/dev/null`; treat emitted whitespace diagnostics as the failure signal.

Recommended validation for the next implementation gate:

```bash
uv run python -m json.tool docs/reviews/mvp-fixture-promotion-state-manifest-20260613.json
uv run python -c "from pathlib import Path; from fund_agent.fund.golden_readiness_preflight import _load_fixture_promotion_states; states=_load_fixture_promotion_states(Path('docs/reviews/mvp-fixture-promotion-state-manifest-20260613.json')); assert states is not None; assert states.fund_year_states == {('004393', 2025): 'promoted_fixture'}; assert states.legacy_fund_states == {}; print('fixture_promotion_manifest_year_aware_ok')"
uv run python -c "import json; from pathlib import Path; payload=json.loads(Path('reports/golden-answers/golden-answer.json').read_text(encoding='utf-8')); funds=[f for f in payload['funds'] if f.get('fund_code')=='004393' and f.get('report_year')==2025]; assert len(funds)==1; records=funds[0]['records']; identities={(r.get('field_name'), r.get('sub_field')) for r in records}; expected={('basic_identity','fund_name'),('basic_identity','fund_code'),('basic_identity','management_company'),('basic_identity','custodian'),('basic_identity','inception_date'),('product_profile','investment_objective'),('benchmark','benchmark_name')}; assert identities==expected; assert not funds[0].get('skipped_fields'); forbidden={'fee_schedule','turnover_rate'}; assert not any(r.get('field_name') in forbidden for r in records); print('004393_2025_row_scope_ok')"
uv run pytest tests/fund/test_golden_readiness_preflight.py::test_preflight_accepts_year_aware_fixture_promotion_matching_year tests/fund/test_golden_readiness_preflight.py::test_preflight_rejects_fixture_promotion_wrong_year tests/fund/test_golden_readiness_preflight.py::test_preflight_blocks_legacy_fund_code_only_fixture_promotion tests/fund/test_golden_readiness_preflight.py::test_preflight_rejects_duplicate_year_aware_fixture_promotion_entry tests/fund/test_golden_readiness_preflight.py::test_preflight_rejects_year_aware_fixture_promotion_unknown_field tests/fund/test_golden_readiness_preflight.py::test_preflight_rejects_year_aware_fixture_promotion_wrong_identity -q
git diff --name-only -- fund_agent tests reports/golden-answers docs/design.md docs/implementation-control.md docs/current-startup-packet.md README.md fund_agent/README.md tests/README.md
git status --short -- fund_agent tests reports/golden-answers docs/design.md docs/implementation-control.md docs/current-startup-packet.md README.md fund_agent/README.md tests/README.md
git diff --check --no-index -- /dev/null docs/reviews/mvp-fixture-promotion-state-manifest-20260613.json
git diff --check --no-index -- /dev/null docs/reviews/mvp-fixture-promotion-content-manifest-implementation-evidence-20260613.md
git status --short docs/reviews/mvp-fixture-promotion-state-manifest-20260613.json docs/reviews/mvp-fixture-promotion-content-manifest-implementation-evidence-20260613.md
```

Expected results:

- JSON parses.
- Parser loads one exact year-aware entry:
  `{("004393", 2025): "promoted_fixture"}`.
- `legacy_fund_states` is empty.
- Tracked golden JSON still has exactly one `004393 / 2025` fund entry with the
  seven accepted row identities and zero skipped fields; fee rows,
  `turnover_rate`, skipped/deferred rows, other funds and other years are not
  included in the promotion scope.
- Targeted parser tests pass.
- Forbidden-path guards emit empty output, proving no tracked or untracked
  changes exist in source, tests, golden-answer content, control/design or README
  paths.
- Diff whitespace checks emit no whitespace error output.
- Status shows only the manifest JSON and implementation evidence as new or
  modified implementation-gate files before reviews.

Do not run:

- `fund-analysis analyze`
- `fund-analysis checklist`
- live/provider/LLM/network/PDF/FDR commands
- readiness, release, PR, push or merge commands
- cleanup/archive/delete commands

## review gates

Plan review:

- DS-role plan review must verify that the proposed manifest source of
  authority is limited to accepted tracked golden content, strict coverage
  evidence, parser implementation/downstream evidence and controller judgments.
- MiMo-role plan review must verify that the plan does not turn downstream
  parser evidence into content proof and does not change readiness state.
- Controller judgment must either accept this plan for a narrow implementation
  gate or explicitly defer the blocker to release/readiness residual handling.

Implementation review:

- DS-role implementation review must inspect the manifest JSON body and confirm
  schema compatibility, exact `(004393, 2025)` identity, no duplicate identity,
  no unknown keys and no legacy fund-code-only shape.
- MiMo-role implementation review must verify source authority, row scope and
  validation outputs, including that only the seven accepted rows are promoted.
- Controller judgment must state that the accepted implementation creates only
  fixture promotion state manifest/content proof for `004393 / 2025`; it must
  preserve release/readiness `NOT_READY`.

## stop conditions

Stop and route back to controller if any of the following occurs:

- The tracked golden content no longer has exactly one `004393 / 2025` fund
  entry with exactly seven active rows and zero skipped rows.
- Any proposed manifest source depends on arbitrary untracked residue, old
  fund-code-only manifest state, local PDF/body files, reports outside accepted
  evidence, or undocumented manual inspection.
- The implementation requires editing source, tests, golden-answer content,
  fixtures, runtime outputs, design docs, control docs or README files.
- The implementation needs live/provider/LLM/network/PDF/FDR access, `analyze`,
  `checklist`, readiness/release/PR commands, cleanup or external state.
- Reviewers dispute that the accepted tracked golden content write plus parser
  downstream evidence is sufficient source authority for a manifest-only
  promotion-state artifact.
- The manifest needs fields not accepted by
  `fund-agent.fixture-promotion-state.year-aware.v1`.
- The implementation attempts to promote fee rows, `turnover_rate`, skipped
  rows, deferred rows, another year or another fund.
- Any artifact states or implies release/readiness is ready.

If a stop condition triggers, recommended fallback verdict for the controller is
`DEFER_RECOMMENDED`, with the residual routed to release/readiness rollup as
`fixture_promotion_content_manifest_absent`.

## next gate recommendation

Recommended next gate:

```text
Fixture Promotion Content / Promotion-state Manifest Implementation Gate
```

Recommended gate classification: `standard`.

Allowed implementation scope:

- write exactly one year-aware manifest JSON under `docs/reviews/`;
- write implementation evidence under `docs/reviews/`;
- run only JSON/parser/test/diff/status validations listed above;
- obtain DS and MiMo reviews;
- controller may accept a local checkpoint only after review pass.

Expected controller closeout if accepted:

- `004393 / 2025` has accepted year-aware fixture promotion state manifest
  content for exactly the seven tracked golden rows;
- downstream parser evidence remains evidence of consumption semantics, not the
  manifest content proof itself;
- fixture promotion content/manifest absence residual is closed only for
  `004393 / 2025`;
- broader readiness, release, PR, fixture/golden expansion, fee rows,
  `turnover_rate`, other funds and other years remain deferred;
- release/readiness remains `NOT_READY`.
