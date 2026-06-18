# MVP Small Golden Set Portfolio Manager Tenure List Additive Extractor Fix Gate Plan

## Gate

- Gate: `portfolio_manager_tenure_list.v1 additive extractor fix gate`
- Classification: `standard`
- Date: 2026-06-10
- Role: planning worker
- Status: proposed for review

## Goal

Make the accepted same-source manager roster test pass for `portfolio_manager_tenure_list.v1` by adding a narrow, additive manager roster extraction surface to the existing manager ownership extractor.

The direct failing evidence is `tests/fund/test_small_golden_set_extractor_correctness.py::test_manager_extractor_exposes_same_source_portfolio_manager_tenure_list`: the accepted xfail currently fails because `ManagerOwnershipExtractionResult` has no `portfolio_managers` output field. The target is to parse the accepted `§4.1.2 基金经理简介` table shape and return same-source rows for all five accepted small-golden rows.

## Source Truth And Evidence

- Control truth: `docs/implementation-control.md`
- Startup packet: `docs/current-startup-packet.md`
- Accepted previous gate judgment: `docs/reviews/mvp-small-golden-set-same-source-manager-failing-test-gate-controller-judgment-20260610.md`
- Accepted retained excerpt oracle: `docs/reviews/mvp-small-golden-set-retained-excerpt-fixture-pdf-only-20260609.json`
- Current failing test: `tests/fund/test_small_golden_set_extractor_correctness.py`
- Current extractor: `fund_agent/fund/extractors/manager_ownership.py`
- Current model: `fund_agent/fund/extractors/models.py`

## Scope

Allowed files:

- `fund_agent/fund/extractors/models.py`
- `fund_agent/fund/extractors/manager_ownership.py`
- `tests/fund/extractors/test_manager_ownership.py`
- `tests/fund/test_small_golden_set_extractor_correctness.py`
- `tests/README.md`
- this gate's evidence/review artifacts under `docs/reviews/`

Optional only if implementation proves unavoidable:

- `fund_agent/fund/README.md`, only if reviewer decides the new extractor output surface must be documented immediately.

## Non-goals

- No PDF read, network, live EID/FDR acquisition, fallback invocation, provider probe or live LLM run.
- No source orchestration, cache, repository, parser, provider, runtime budget or config change.
- No fixture projection and no mutation of `tests/fixtures/fund/small_golden_set/`.
- No golden/readiness promotion and no score-loop or quality gate semantics change.
- No `StructuredFundDataBundle`, report renderer, chapter facts, evidence availability, report evidence, checklist or Service integration in this gate.
- No inference of manager tenure from prose; only parse explicit table rows.
- No expansion to `risk_characteristic_text.v1`, `bond_top_holding_row.v1` or `target_fund_holding_row.v1`.

## Implementation Decisions

1. Add `portfolio_managers` to `ManagerOwnershipExtractionResult` as an `ExtractedField[dict[str, object]]`.
2. Define the emitted value as:
   - `schema_version`: exactly `portfolio_manager_tenure_list.v1`
   - `fund_code`: `report.key.fund_code`
   - `report_year`: `report.key.year`
   - `portfolio_managers`: ordered list of row dictionaries.
3. Each manager row must contain:
   - `name`
   - `role`
   - `start_date`
   - optional `end_date` only when disclosed and non-empty
   - `source_anchor` containing `section_id`, `section_title`, `page_number`, `table_id`, and `row_locator`
4. The extractor must identify a manager roster table by header semantics, not by fixed `table_index`.
5. Required header groups:
   - name header: contains `姓名`
   - role header: contains one of `职务`, `职责`, `岗位`
   - start date header: contains one of `任职日期`, `任职时间`, `起始日期`, `聘任日期`
   - end date header is optional: contains one of `离任日期`, `离任时间`, `终止日期`
6. Candidate tables must be tied to `§4` fail-closed:
   - If a future `ParsedTable` model exposes section metadata, use that metadata and require `§4`.
   - In the current model, `ParsedTable` has no section metadata, so direct extraction also requires current `§4` section text to contain a manager-roster heading such as `4.1.2 基金经理简介` or an accepted equivalent heading containing both `基金经理` and `简介`.
   - If the report has a manager-shaped table but no `§4` manager-roster heading, return `missing` rather than inventing a `§4` anchor.
   - Do not inspect external source text, PDF, repository, cache or source helper.
7. Row filtering must skip blank rows and header-repeat rows. It must not fabricate missing dates or roles.
8. Anchors must be annual-report anchors with `section_id="§4"` and row-level locators including the manager name.
9. If no valid row is extracted, return `missing` with a safe note; do not return partial schema values.
10. Keep existing `manager_strategy_text`, `turnover_rate`, `manager_alignment` and `holder_structure` behavior unchanged.

## Test Plan

Update or add focused tests in `tests/fund/extractors/test_manager_ownership.py`:

- direct table extraction returns `portfolio_manager_tenure_list.v1`, fund code, report year and ordered managers;
- optional blank `end_date` is omitted from the corresponding manager row;
- anchors are annual-report anchors, use `§4`, carry page/table identity and include the manager name in `row_locator`;
- manager-shaped tables return `missing` when `§4` lacks a manager-roster heading, because current `ParsedTable` has no section ownership metadata;
- non-manager tables and malformed rows do not produce a direct field;
- existing manager ownership tests still pass unchanged.

Update the accepted same-source test:

- remove the strict xfail marker only for `test_manager_extractor_exposes_same_source_portfolio_manager_tenure_list`;
- preserve five-row parameterization and accepted oracle input;
- do not relax schema or row assertions.

Required validation commands:

```bash
uv run pytest tests/fund/extractors/test_manager_ownership.py -q
uv run pytest tests/fund/test_small_golden_set_extractor_correctness.py -q
uv run pytest tests/fund/test_small_golden_set_manifest.py tests/fund/test_small_golden_set_fixture_shape.py tests/fund/test_small_golden_set_source_identity.py tests/fund/test_small_golden_set_parser_mechanics.py tests/fund/test_small_golden_set_extractor_correctness.py -q
uv run ruff check fund_agent/fund/extractors/models.py fund_agent/fund/extractors/manager_ownership.py tests/fund/extractors/test_manager_ownership.py tests/fund/test_small_golden_set_extractor_correctness.py
git diff --check -- fund_agent/fund/extractors/models.py fund_agent/fund/extractors/manager_ownership.py tests/fund/extractors/test_manager_ownership.py tests/fund/test_small_golden_set_extractor_correctness.py tests/README.md
```

Expected results:

- manager ownership unit tests pass;
- small-golden extractor correctness changes from `16 passed, 8 xfailed` to `21 passed, 3 xfailed`;
- small-golden family changes from `37 passed, 8 xfailed` to `42 passed, 3 xfailed`;
- remaining xfails must still correspond only to the other not-yet-implemented future contracts.

## Documentation Decision

Update `tests/README.md` only if the xfail count or small-golden extractor correctness state is documented there.

Do not update control docs during implementation. Control/startup truth sync belongs after implementation evidence, code review, controller judgment and accepted checkpoint.

`fund_agent/fund/README.md` is optional in this gate. If updated, it must describe only the current extractor output surface and must not claim report/scoring/quality gate integration.

## Stop Conditions

Stop and return to controller if any of these occur:

- making the test pass requires PDF, repository, source, fallback, network, live provider, fixture projection, score-loop or report pipeline changes;
- the implementation needs to modify `StructuredFundDataBundle` or downstream report/chapter/quality surfaces;
- manager roster table recognition cannot be kept header-based without hard-coding current fixture table indexes;
- direct extraction would require marking a table as `§4` without either parser section metadata or the `§4` manager-roster heading guard;
- the accepted same-source test must be relaxed to pass;
- validation result changes unrelated passing behavior outside the manager roster output surface;
- dirty unrelated workspace files would need staging or mutation.

## Completion Report Format

Implementation evidence must report:

- changed files;
- exact behavior added;
- confirmation that no forbidden source/provider/runtime/fallback/golden/readiness action occurred;
- validation command outputs;
- remaining xfails and their owner contracts;
- any residual risk, especially table shape ambiguity.
