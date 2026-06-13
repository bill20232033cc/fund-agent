# Fixture Promotion Content / Promotion-state Manifest Implementation Evidence

Date: 2026-06-13

Gate: `Fixture Promotion Content / Promotion-state Manifest Implementation Gate`

Verdict: `IMPLEMENTED_PENDING_REVIEW_NOT_READY`

## Scope

This implementation creates one year-aware fixture promotion state manifest for
the already accepted `004393 / 2025` tracked golden content. It does not edit
golden-answer content, fixture content, source, tests, runtime behavior, README
files, design/control/startup docs, release/readiness state, PR state or external
state.

Release/readiness remains `NOT_READY`.

## Accepted Inputs

- Plan/controller judgment:
  `docs/reviews/mvp-fixture-promotion-content-manifest-plan-controller-judgment-20260613.md`
- Accepted tracked golden content judgment:
  `docs/reviews/mvp-004393-2025-tracked-golden-content-write-implementation-controller-judgment-20260613.md`
- Accepted strict coverage evidence judgment:
  `docs/reviews/mvp-004393-2025-fixture-promotion-strict-golden-coverage-evidence-controller-judgment-20260613.md`
- Accepted parser implementation judgment:
  `docs/reviews/mvp-fixture-promotion-state-year-aware-schema-parser-implementation-controller-judgment-20260613.md`
- Accepted downstream evidence judgment:
  `docs/reviews/mvp-fixture-promotion-year-aware-parser-downstream-evidence-controller-judgment-20260613.md`

## Files Written

- `docs/reviews/mvp-fixture-promotion-state-manifest-20260613.json`
- `docs/reviews/mvp-fixture-promotion-content-manifest-implementation-evidence-20260613.md`

No other project source, test, golden-answer, fixture, runtime, README,
design/control/startup or external-state file was intentionally changed.

## Manifest Content

The manifest uses the accepted year-aware schema:

```json
{
  "schema_version": "fund-agent.fixture-promotion-state.year-aware.v1",
  "accepted_as_of": "2026-06-13",
  "entries": [
    {
      "fund_code": "004393",
      "report_year": 2025,
      "promotion_state": "promoted_fixture",
      "promotion_identity": "fund_year"
    }
  ]
}
```

The actual manifest also lists accepted source/evidence artifacts. It has one
entry only, no legacy fund-code-only shape and no unknown fields.

Scope of the promotion state:

- applies only to `004393 / 2025`;
- applies only to the seven accepted tracked golden rows already accepted by the
  tracked golden content write controller judgment;
- does not promote `fee_schedule.management_fee`,
  `fee_schedule.custody_fee`, `turnover_rate`, skipped rows, deferred rows,
  other funds or other years.

## Validation

Command:

```text
uv run python -m json.tool docs/reviews/mvp-fixture-promotion-state-manifest-20260613.json
```

Result: passed. JSON parsed and was printed by `json.tool`.

Command:

```text
uv run python -c "from pathlib import Path; from fund_agent.fund.golden_readiness_preflight import _load_fixture_promotion_states; states=_load_fixture_promotion_states(Path('docs/reviews/mvp-fixture-promotion-state-manifest-20260613.json')); assert states is not None; assert states.fund_year_states == {('004393', 2025): 'promoted_fixture'}; assert states.legacy_fund_states == {}; print('fixture_promotion_manifest_year_aware_ok')"
```

Output:

```text
fixture_promotion_manifest_year_aware_ok
```

Command:

```text
uv run python -c "import json; from pathlib import Path; payload=json.loads(Path('reports/golden-answers/golden-answer.json').read_text(encoding='utf-8')); funds=[f for f in payload['funds'] if f.get('fund_code')=='004393' and f.get('report_year')==2025]; assert len(funds)==1; records=funds[0]['records']; identities={(r.get('field_name'), r.get('sub_field')) for r in records}; expected={('basic_identity','fund_name'),('basic_identity','fund_code'),('basic_identity','management_company'),('basic_identity','custodian'),('basic_identity','inception_date'),('product_profile','investment_objective'),('benchmark','benchmark_name')}; assert identities==expected; assert not funds[0].get('skipped_fields'); forbidden={'fee_schedule','turnover_rate'}; assert not any(r.get('field_name') in forbidden for r in records); print('004393_2025_row_scope_ok')"
```

Output:

```text
004393_2025_row_scope_ok
```

Command:

```text
uv run pytest tests/fund/test_golden_readiness_preflight.py::test_preflight_accepts_year_aware_fixture_promotion_matching_year tests/fund/test_golden_readiness_preflight.py::test_preflight_rejects_fixture_promotion_wrong_year tests/fund/test_golden_readiness_preflight.py::test_preflight_blocks_legacy_fund_code_only_fixture_promotion tests/fund/test_golden_readiness_preflight.py::test_preflight_rejects_duplicate_year_aware_fixture_promotion_entry tests/fund/test_golden_readiness_preflight.py::test_preflight_rejects_year_aware_fixture_promotion_unknown_field tests/fund/test_golden_readiness_preflight.py::test_preflight_rejects_year_aware_fixture_promotion_wrong_identity -q
```

Output:

```text
......                                                                   [100%]
6 passed in 0.58s
```

Command:

```text
git diff --name-only -- fund_agent tests reports/golden-answers docs/design.md docs/implementation-control.md docs/current-startup-packet.md README.md fund_agent/README.md tests/README.md
```

Output: empty.

Command:

```text
git status --short -- fund_agent tests reports/golden-answers docs/design.md docs/implementation-control.md docs/current-startup-packet.md README.md fund_agent/README.md tests/README.md
```

Output: empty.

## Evidence Conclusion

The implementation created the accepted manifest-only content artifact for
`004393 / 2025`. The parser loads it as exactly:

```text
{('004393', 2025): 'promoted_fixture'}
```

with no legacy fund-code-only states. Row-scope validation confirms the tracked
golden JSON still has the seven accepted `004393 / 2025` row identities and no
skipped fields, fee rows or `turnover_rate` inside the promotion scope.

This evidence does not prove release/readiness. It only closes the fixture
promotion content/manifest absence residual for `004393 / 2025` if review and
controller judgment accept it.

## Residuals

| Residual | Owner | Next handling |
|---|---|---|
| Release/readiness remains unproven. | Release owner / controller | Future readiness/release gate only. |
| Fee rows, `turnover_rate`, skipped/deferred rows, other funds and other years are outside this manifest. | Golden/fixture owner | Separate reviewed gates if ever needed. |
| Existing untracked residue remains outside this gate. | Controller / artifact owners | Artifact-specific disposition gates only. |
