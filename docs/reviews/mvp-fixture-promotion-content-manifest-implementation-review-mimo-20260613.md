# Fixture Promotion Content / Promotion-state Manifest Implementation Review - MiMo

Date: 2026-06-13

Role: MiMo-role implementation review worker, not controller

Gate: `Fixture Promotion Content / Promotion-state Manifest Implementation Gate`

Verdict: `PASS_WITH_RESIDUALS`

## Scope

This review covers only the implementation artifacts:

- `docs/reviews/mvp-fixture-promotion-state-manifest-20260613.json`
- `docs/reviews/mvp-fixture-promotion-content-manifest-implementation-evidence-20260613.md`
- accepted plan/controller judgment:
  `docs/reviews/mvp-fixture-promotion-content-manifest-plan-controller-judgment-20260613.md`

This review did not edit source, tests, runtime, golden-answer content, fixture
content, control/design/startup docs, README files, readiness/release state, PR
state or external state.

Release/readiness remains `NOT_READY`.

## Review Basis

- Rule truth: `AGENTS.md`
- Control truth:
  - `docs/current-startup-packet.md`
  - `docs/implementation-control.md`
- Accepted plan/controller judgment:
  `docs/reviews/mvp-fixture-promotion-content-manifest-plan-controller-judgment-20260613.md`
- Accepted tracked golden content judgment:
  `docs/reviews/mvp-004393-2025-tracked-golden-content-write-implementation-controller-judgment-20260613.md`
- Accepted strict coverage evidence judgment:
  `docs/reviews/mvp-004393-2025-fixture-promotion-strict-golden-coverage-evidence-controller-judgment-20260613.md`
- Accepted parser/downstream judgments:
  - `docs/reviews/mvp-fixture-promotion-state-year-aware-schema-parser-implementation-controller-judgment-20260613.md`
  - `docs/reviews/mvp-fixture-promotion-year-aware-parser-downstream-evidence-controller-judgment-20260613.md`
- Parser code:
  `fund_agent/fund/golden_readiness_preflight.py`
- Targeted tests:
  `tests/fund/test_golden_readiness_preflight.py`

## Findings

| Severity | Evidence | Recommended disposition |
|---|---|---|
| none | Manifest body has schema version `fund-agent.fixture-promotion-state.year-aware.v1`, one entry only, `fund_code="004393"`, `report_year=2025`, `promotion_state="promoted_fixture"`, `promotion_identity="fund_year"` and entry-level evidence artifacts. Parser code rejects unknown year-aware top-level keys except the accepted `schema_version`, `accepted_as_of`, `source_artifacts`, `entries`, rejects unknown entry keys except the accepted five keys, rejects duplicate `(fund_code, report_year)`, and returns `fund_year_states` without legacy states. | Accept. No implementation fix required. |
| none | Row-scope assertion against `reports/golden-answers/golden-answer.json` confirms exactly one `004393 / 2025` fund entry, exactly seven active rows, zero skipped fields, and no `fee_schedule` or `turnover_rate` active rows. The seven identities are `basic_identity.fund_name`, `basic_identity.fund_code`, `basic_identity.management_company`, `basic_identity.custodian`, `basic_identity.inception_date`, `product_profile.investment_objective`, and `benchmark.benchmark_name`. | Accept. This is sufficient for the narrow manifest-only promotion-state proof. |
| none | Content proof is not delegated to downstream parser evidence alone. The implementation evidence states that downstream/parser artifacts are accepted inputs and that this evidence only closes fixture promotion content/manifest absence if review and controller judgment accept it. The new manifest plus implementation evidence/review/controller path remains the content-proof route. | Accept. Controller judgment should preserve this wording. |
| residual | Fee rows, `turnover_rate`, skipped/deferred rows, other funds and other years remain outside the manifest. This matches the accepted tracked golden content judgment and plan stop conditions. | Preserve as explicit residual, not a blocker for this gate. |
| residual | Release/readiness remains unproven. No readiness, release, PR, live/provider/LLM, `analyze` or `checklist` command was run in this review. | Preserve `NOT_READY`; route readiness/release only to a future authorized gate. |
| residual | Workspace still has unrelated untracked residue in `git status --branch --short`; forbidden-path guards for source/tests/golden/control/design/README paths were empty, and path-scoped status for the two implementation artifacts showed only those two files before this review artifact was written. | Treat unrelated residue as outside this gate. Do not use it as proof and do not clean it up here. |

## Validation Re-run

Allowed local validation was re-run in this review.

```text
uv run python -m json.tool docs/reviews/mvp-fixture-promotion-state-manifest-20260613.json
```

Result: passed.

```text
uv run python -c "from pathlib import Path; from fund_agent.fund.golden_readiness_preflight import _load_fixture_promotion_states; states=_load_fixture_promotion_states(Path('docs/reviews/mvp-fixture-promotion-state-manifest-20260613.json')); assert states is not None; assert states.fund_year_states == {('004393', 2025): 'promoted_fixture'}; assert states.legacy_fund_states == {}; print('fixture_promotion_manifest_year_aware_ok')"
```

Result:

```text
fixture_promotion_manifest_year_aware_ok
```

```text
uv run python -c "import json; from pathlib import Path; payload=json.loads(Path('reports/golden-answers/golden-answer.json').read_text(encoding='utf-8')); funds=[f for f in payload['funds'] if f.get('fund_code')=='004393' and f.get('report_year')==2025]; assert len(funds)==1; records=funds[0]['records']; identities={(r.get('field_name'), r.get('sub_field')) for r in records}; expected={('basic_identity','fund_name'),('basic_identity','fund_code'),('basic_identity','management_company'),('basic_identity','custodian'),('basic_identity','inception_date'),('product_profile','investment_objective'),('benchmark','benchmark_name')}; assert identities==expected; assert not funds[0].get('skipped_fields'); forbidden={'fee_schedule','turnover_rate'}; assert not any(r.get('field_name') in forbidden for r in records); print('004393_2025_row_scope_ok')"
```

Result:

```text
004393_2025_row_scope_ok
```

```text
uv run pytest tests/fund/test_golden_readiness_preflight.py::test_preflight_accepts_year_aware_fixture_promotion_matching_year tests/fund/test_golden_readiness_preflight.py::test_preflight_rejects_fixture_promotion_wrong_year tests/fund/test_golden_readiness_preflight.py::test_preflight_blocks_legacy_fund_code_only_fixture_promotion tests/fund/test_golden_readiness_preflight.py::test_preflight_rejects_duplicate_year_aware_fixture_promotion_entry tests/fund/test_golden_readiness_preflight.py::test_preflight_rejects_year_aware_fixture_promotion_unknown_field tests/fund/test_golden_readiness_preflight.py::test_preflight_rejects_year_aware_fixture_promotion_wrong_identity -q
```

Result:

```text
6 passed in 0.39s
```

```text
git diff --name-only -- fund_agent tests reports/golden-answers docs/design.md docs/implementation-control.md docs/current-startup-packet.md README.md fund_agent/README.md tests/README.md
git status --short -- fund_agent tests reports/golden-answers docs/design.md docs/implementation-control.md docs/current-startup-packet.md README.md fund_agent/README.md tests/README.md
```

Result: both commands emitted empty output.

```text
git diff --check --no-index -- /dev/null docs/reviews/mvp-fixture-promotion-state-manifest-20260613.json
git diff --check --no-index -- /dev/null docs/reviews/mvp-fixture-promotion-content-manifest-implementation-evidence-20260613.md
```

Result: both commands emitted no whitespace diagnostics. The non-zero exit code
is expected for `--no-index` comparison against `/dev/null`.

```text
git status --short docs/reviews/mvp-fixture-promotion-state-manifest-20260613.json docs/reviews/mvp-fixture-promotion-content-manifest-implementation-evidence-20260613.md
```

Result before this review artifact was written:

```text
?? docs/reviews/mvp-fixture-promotion-content-manifest-implementation-evidence-20260613.md
?? docs/reviews/mvp-fixture-promotion-state-manifest-20260613.json
```

## Conclusion

The implementation matches the accepted narrow contract. It creates a
year-aware promotion-state proof only for the accepted `004393 / 2025` tracked
golden content surface and does not promote fee rows, `turnover_rate`,
skipped/deferred rows, other funds or other years.

This review does not make a controller decision. Recommended controller
disposition: accept the implementation with explicit residuals and keep
release/readiness `NOT_READY`.
