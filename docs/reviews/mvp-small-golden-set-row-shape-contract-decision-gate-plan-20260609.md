# MVP Small Golden Set Row-shape Contract Decision Gate Plan

## Gate

| Item | Value |
|---|---|
| Gate | `row-shape contract decision gate for retained manager / risk / non-equity holdings residuals` |
| Role | planning worker only |
| Classification | `heavy` |
| Date | 2026-06-09 |
| Baseline checkpoint | `d61071a gateflow: accept equity-like holdings row-field tests` |
| Deliverable | `docs/reviews/mvp-small-golden-set-row-shape-contract-decision-gate-plan-20260609.md` |

## Source Evidence Read

- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/design.md`
- `docs/reviews/mvp-small-golden-set-row-field-equity-like-holdings-test-extension-controller-judgment-20260609.md`
- `docs/reviews/mvp-small-golden-set-row-field-extractor-gap-decision-gate-controller-judgment-20260609.md`
- `docs/reviews/mvp-small-golden-set-retained-excerpt-fixture-pdf-only-20260609.json`
- `tests/fund/test_small_golden_set_extractor_correctness.py`
- Read-only code surface: `fund_agent/fund/extractors/profile.py`, `fund_agent/fund/extractors/manager_ownership.py`, `fund_agent/fund/extractors/holdings_share_change.py`, `fund_agent/fund/extractors/bond_risk_evidence.py`, `fund_agent/fund/extractors/models.py`
- Git evidence: current `HEAD` is `d61071a gateflow: accept equity-like holdings row-field tests`; current branch is `feat/mvp-llm-incomplete-run-artifacts`; unrelated untracked workspace residue exists and must remain untouched.

## Current Accepted Facts

1. The current accepted checkpoint is `d61071a`, and it accepts only equity-like holdings row-field tests.
2. Current control truth routes the next extractor-facing entry to `row-shape contract decision gate for retained manager / risk / non-equity holdings residuals`.
3. The only correctness oracle for this gate family is `docs/reviews/mvp-small-golden-set-retained-excerpt-fixture-pdf-only-20260609.json`.
4. The retained excerpt JSON has accepted short field-scoped excerpts for all five rows, but explicitly does not accept fixture projection, exact/numeric correctness promotion, golden/readiness promotion, extractor modification, fallback, network, or live acquisition.
5. Existing row-field correctness tests already pass for current extractor-consumable fields: identity, share-unit scale, benchmark, management/custody fee, one-year return, `110020` tracking error, and equity-like holdings rows for `004393`, `004194`, `017641`.
6. Existing tests preserve strict xfail residuals for `manager`, `risk`, `006597` bond top holding, and `110020` target ETF holding.
7. Current `profile.py` exposes `basic_identity`, `product_profile`, `benchmark`, `index_profile`, and `fee_schedule`; its `fund_manager` label is a scalar profile field and is not a portfolio-manager identity/tenure list contract.
8. Current `manager_ownership.py` extracts manager strategy text, turnover, manager/employee holding, and holder structure; it does not expose portfolio-manager identity and tenure from `§4.1.2`.
9. Current `profile.py` can read `style_positioning` from "风险收益特征", but the prior controller judgment accepted that retained `risk` must not be mapped to style positioning because the retained values include risk-characteristic clauses such as Hong Kong Stock Connect risk, credit/liquidity control, and QDII FX risk.
10. Current `holdings_share_change.py` only identifies top-ten/equity stock detail shapes and emits them under `holdings_snapshot.value["top_holdings"]` with raw table headers. It has no bond top-holding route and no target ETF/fund holding route.
11. Current `bond_risk_evidence.py` and `BondRiskEvidenceValue` are seven-group template chapter 6 risk evidence contracts. They are not a bond top-holding row contract.

## Non-goals

- Do not read local PDFs.
- Do not use network, `FundDocumentRepository` live acquisition, fallback, live LLM, endpoint/DNS/curl/socket/provider probes, or source acquisition.
- Do not modify extractor/provider/default/runtime/budget/config files in this planning gate.
- Do not project fixtures or use synthetic/unmatched fixtures as truth.
- Do not accept exact/numeric correctness for residual fields in this planning artifact.
- Do not enter golden/readiness promotion, Chapter calibration, Agent runtime expansion, multi-year runtime, score-loop, release, merge, PR creation, mark-ready, or external PR state changes.
- Do not treat search results, LLM summaries, fallback traces, historical outputs, or unrelated untracked files as source truth.
- Do not touch unrelated dirty/untracked files.

## Why This Gate Is Heavy

This gate is `heavy` because the residuals cannot be safely unlocked by adding more row-field assertions over existing public output shapes. Each residual either changes extractor output schema semantics or requires an additive field contract before tests can mean anything:

- `manager` would require a portfolio-manager identity/tenure list with row-level anchors, not a scalar "基金经理" profile string and not manager ownership.
- `risk` would require a risk-characteristic disclosure contract, not `style_positioning`.
- `006597` would require a bond top-holding row shape, not equity `top_holdings`.
- `110020` would require a target ETF/fund holding row shape, not stock holdings.

Because these choices affect public extractor contracts, snapshot comparability, downstream score/golden semantics, and fail-closed correctness rules, the gate must receive plan review by two independent reviewers, controller judgment, and an accepted local checkpoint before any implementation or passing tests.

## Contract Decisions By Residual

| Residual | Current oracle shape | Current extractor surface | Semantic mismatch | Decision | Recommended contract route | Allowed next gate | Stop conditions |
|---|---|---|---|---|---|---|---|
| `manager` portfolio-manager identity and tenure | `fields.manager.expected` is a list of managers: `name`, `role`, `start_date`, optional `end_date`; anchor is `§4.1.2 基金经理简介` | `ProfileExtractionResult.basic_identity` has no portfolio manager list; `profile.py` has only scalar `fund_manager`; `manager_ownership.py` covers strategy/turnover/holding/holder structure, not identity/tenure | A scalar manager label cannot preserve multiple managers, departed manager roles, start/end dates, or row-level tenure evidence | Needs new additive output contract before tests | Add Fund extractor contract such as `portfolio_manager_tenure` as `ExtractedField[PortfolioManagerTenureValue]`, or an equivalent explicitly named additive field. It must preserve ordered records, `name`, `role`, `start_date`, optional `end_date`, source section, row locator, and missing/partial mode. Do not overload `fund_manager` or `manager_alignment` | Heavy implementation plan for additive manager contract, then same-source failing tests, then extractor implementation/fix | Stop if implementation tries to compare only names, drops dates, silently ignores departed managers, reuses `manager_ownership`, reads PDFs, or turns retained JSON into projected fixtures |
| retained `risk` characteristic text | `fields.risk.expected` is a disclosure text string combining fund category/risk-return level and special risks/control clauses; anchors are `§2.2` and sometimes `§4.4.1` | `profile.py` has `style_positioning`; `bond_risk_evidence.py` has chapter 6 seven-group bond risk evidence for bond funds | `style_positioning` is product style/risk-positioning text and does not guarantee the same semantic coverage as retained risk characteristics; `bond_risk_evidence` is a different chapter 6 evidence contract | Needs new additive output contract before tests | Add `risk_characteristics` or equivalent explicit `ExtractedField[RiskCharacteristicValue]` with raw disclosure text, normalized category/risk-return summary only if directly present, optional special risk clauses, anchors, and source sections. Do not map it to `style_positioning`; do not reuse `bond_risk_evidence` | Heavy implementation plan for additive risk-characteristic contract, then same-source failing tests, then extractor implementation/fix | Stop if the route collapses risk to fund type, benchmark, style positioning, or bond-risk group status; stop if exact/numeric correctness is claimed for free-text residuals |
| `006597` bond top holding | `fields.holdings.expected.top_bond_table_row`: `code`, `name`, `fair_value_cny`, `net_asset_ratio`; anchor is `§8.6 前五名债券投资明细` | `holdings_share_change.py` emits `holdings_snapshot.value["top_holdings"]` only from equity top-ten/all-stock detail routes; `bond_risk_evidence` can use bond allocation/risk evidence but not top bond row | Bond top holding is a portfolio holding row, not a risk-evidence group and not an equity stock row | Needs new additive output contract before tests | Extend holdings output additively with a bond-specific row shape, e.g. `bond_top_holdings` plus `bond_top_holdings_status` and `bond_top_holdings_source="top_bond_investment_details"`. Canonical row keys should be `code`, `name`, `fair_value_cny`, `net_asset_ratio`; source anchor must point to `§8.6` | Holdings row-shape implementation plan; then same-source failing test for a minimal `§8.6` table; then extractor implementation/fix | Stop if implementation reuses equity `top_holdings` without a distinct source/status, routes through `bond_risk_evidence`, normalizes by production parser without review, or claims quantity/rating fields not in retained oracle |
| `110020` target ETF holding | `fields.holdings.expected.target_etf_holding`: `name`, `fair_value_cny`, `net_asset_ratio`; no code in oracle; anchor is `§8.2 期末投资目标基金明细` | `holdings_share_change.py` has no target-fund/ETF holding route; current equity-like holdings tests deliberately exclude this row shape | Target ETF/fund holding is a fund-holding row with no security code in the accepted oracle; it is not stock top holding and must not fabricate code | Needs new additive output contract before tests | Extend holdings output additively with target-fund/ETF row shape, e.g. `target_fund_holdings` plus `target_fund_holdings_status` and `target_fund_holdings_source="target_fund_investment_details"`. Canonical row keys should be `name`, `fair_value_cny`, `net_asset_ratio`, with optional `code` only when directly disclosed and accepted by a later oracle | Holdings row-shape implementation plan; then same-source failing test for a minimal `§8.2` target fund table; then extractor implementation/fix | Stop if implementation fabricates ETF code from fund name, maps target ETF into stock `top_holdings`, requires code for this row, or treats the accepted `annual_tracking_error` as unlocking target holding correctness |

## Row-field Gated Unlock Rules

### Shared Rules

| Gate action | Required evidence | Allowed result | Stop condition |
|---|---|---|---|
| Passing tests | Accepted output contract exists, same-source oracle expected shape maps 1:1 to contract keys, test constructs only minimal parsed annual report data from retained oracle, and extractor currently emits the contract values | Passing assertion may be added only for the exact accepted row/field shape | Stop if test needs PDF, network, FDR, fallback, fixture projection, synthetic fixture, LLM summary, unrelated output, or production normalization not yet accepted |
| Failing tests | Accepted output contract exists, same-source oracle expected shape maps 1:1 to contract keys, and current extractor does not yet emit the contract | Add strict failing/xfail or explicit failing test as directed by the implementation plan | Stop if the contract is still undecided or expected fields exceed retained oracle scope |
| Extractor fixes | A reviewed implementation plan names allowed files, exact contract, parser surface, missing/partial behavior, and tests that currently fail for same-source rows | Implement only the named additive route and make the named tests pass | Stop if fix touches provider/runtime/config/source acquisition, changes default behavior beyond extractor contract, or modifies unrelated fixtures |
| Defer | Existing surface mismatch remains material or contract cannot be safely reviewed without PDF/network/code changes | Preserve xfail residual and owner | Stop if deferral silently removes residual visibility |

### Per-residual Unlock

| Residual | May pass now? | May add failing tests next? | May fix extractor next? | Defer rule |
|---|---:|---:|---:|---|
| `manager` | No | Yes, only after additive manager tenure contract is accepted | Yes, only after contract + failing same-source tests | Defer if multi-manager/departed-manager semantics are not represented |
| `risk` | No | Yes, only after additive risk-characteristic contract is accepted | Yes, only after contract + failing same-source tests | Defer if route maps to `style_positioning`, fund type, or bond-risk evidence |
| `006597` | No | Yes, only after additive bond top-holding contract is accepted | Yes, only after contract + failing same-source test | Defer if route reuses equity `top_holdings` without distinct source/status |
| `110020` | No | Yes, only after additive target fund/ETF holding contract is accepted | Yes, only after contract + failing same-source test | Defer if route requires/fabricates a code or maps into stock holdings |

## Acceptance Matrix

| Row | Accepted fact | Contract route | Same-source test target | Expected first implementation signal | Promotion status |
|---|---|---|---|---|---|
| Manager | Retained oracle has `fields.manager.expected` list for all five rows | New additive `portfolio_manager_tenure` contract | Start with all five rows only if implementation can represent optional `end_date`; otherwise start with `004393` single-manager and one multi-manager row as a smaller slice | Tests assert record count, names, roles, dates, anchors, and missing/partial mode | No golden/readiness promotion |
| Risk | Retained oracle has `fields.risk.expected` text for all five rows | New additive `risk_characteristics` contract | Start with all five rows as text/disclosure assertions, not numeric correctness | Tests assert raw retained disclosure text or exact accepted characteristic clauses, anchors, and source sections | No golden/readiness promotion |
| `006597` | Retained oracle has `top_bond_table_row` under holdings | Additive `bond_top_holdings` route in holdings output | One minimal `§8.6` bond table for `006597` | Test first fails until extractor recognizes bond holding table; then passes on canonical row keys | No golden/readiness promotion |
| `110020` | Retained oracle has `target_etf_holding` under holdings without `code` | Additive `target_fund_holdings` route in holdings output | One minimal `§8.2` target-fund table for `110020` | Test first fails until extractor recognizes target fund table; then passes without requiring code | No golden/readiness promotion |

## Implementation Slicing Plan After This Planning Gate

### Slice A: Contract Review And Model Surface Plan

- Type: planning/review only.
- Objective: freeze exact additive field names, value dataclasses or dict schemas, missing/partial semantics, and public output ownership for `portfolio_manager_tenure`, `risk_characteristics`, `bond_top_holdings`, and `target_fund_holdings`.
- Allowed files in future gate: planning/review artifacts only unless controller explicitly opens implementation.
- Expected outcome: controller-approved contract names and schemas.
- Stop condition: any reviewer says an existing field can be reused without preserving retained semantics.

### Slice B: Test-only Same-source Contract Guards

- Type: test-only after Slice A.
- Objective: update `tests/fund/test_small_golden_set_extractor_correctness.py` to assert the accepted additive contract shapes using only retained JSON and minimal `ParsedAnnualReport` construction.
- Allowed files: `tests/fund/test_small_golden_set_extractor_correctness.py`, `tests/README.md`, implementation evidence/review artifacts.
- Exact allowed changes:
  - Add helpers only for minimal `§4.1.2`, `§2.2`, `§4.4.1`, `§8.6`, and `§8.2` synthetic parsed report sections/tables built from oracle values.
  - Preserve existing xfails until each contract is implemented or intentionally convert to strict failing tests under the approved gate.
  - Do not modify retained JSON or synthetic fixtures.
- Expected outcome: failing/xfail tests document the accepted row shapes without extractor fixes.
- Stop condition: test needs non-oracle values, full PDF text, parser cache, network, FDR, fallback, or production normalization.

### Slice C: Manager Additive Extractor Contract

- Type: extractor/schema behavior change.
- Objective: implement portfolio-manager identity and tenure extraction from `§4.1.2` table/text shape after failing same-source tests exist.
- Allowed files in future implementation: exact extractor/model files approved by controller, likely `fund_agent/fund/extractors/models.py`, `fund_agent/fund/extractors/profile.py` or a narrow new extractor module, `fund_agent/fund/data_extractor.py` only if bundle wiring is explicitly required, tests/README, evidence artifacts.
- Required invariants:
  - Multiple managers are preserved.
  - Optional departed-manager `end_date` is preserved when present.
  - `role` is preserved as disclosed text and not normalized into active-only status unless explicitly reviewed.
  - Empty/ambiguous manager table returns `missing` or `partial`, not a fabricated list.
- Stop condition: implementation collapses records to a single scalar or derives tenure from non-oracle context.

### Slice D: Risk-characteristic Additive Extractor Contract

- Type: extractor/schema behavior change.
- Objective: implement risk-characteristic disclosure extraction without reusing `style_positioning` as correctness target.
- Allowed files in future implementation: exact extractor/model files approved by controller, likely `fund_agent/fund/extractors/models.py`, `fund_agent/fund/extractors/profile.py` or a narrow new profile/risk extractor, `fund_agent/fund/data_extractor.py` only if bundle wiring is explicitly required, tests/README, evidence artifacts.
- Required invariants:
  - Raw disclosure text or exact retained clauses are preserved.
  - Special risks/control clauses remain in output when directly present.
  - Fund type recognition may consume the text separately, but fund type is not the correctness output.
  - `bond_risk_evidence` remains separate chapter 6 evidence.
- Stop condition: implementation accepts a fund category label alone as matching the retained risk expected string.

### Slice E: Non-equity Holdings Additive Row-shape Contract

- Type: extractor/schema behavior change.
- Objective: implement additive `bond_top_holdings` and `target_fund_holdings` routes in holdings output.
- Allowed files in future implementation: exact extractor/model files approved by controller, likely `fund_agent/fund/extractors/holdings_share_change.py`, `fund_agent/fund/extractors/models.py` if typed value classes are added, tests/README, evidence artifacts.
- Required invariants:
  - Existing equity-like `top_holdings` behavior and accepted tests remain unchanged.
  - Bond rows have a distinct status/source and do not route through `bond_risk_evidence`.
  - Target fund rows do not require `code`; optional `code` is allowed only if directly disclosed and accepted by oracle in a later gate.
  - Output preserves anchors for each matched table.
- Stop condition: implementation mutates existing equity `top_holdings` semantics, fabricates code, or treats parser-specific raw headers as canonical production schema without review.

### Slice F: Aggregate Review And Control Sync

- Type: review/control after implementation slices.
- Objective: run aggregate review, classify residuals, and update control docs only after controller acceptance.
- Allowed files: review/control artifacts named by controller; source/test docs only if already changed by accepted implementation slices.
- Stop condition: any residual lacks owner/destination.

## Verification Commands For Future Gates

Do not run these in this planning gate. Future controller may choose the exact subset after approving slice scope.

```text
uv run pytest tests/fund/test_small_golden_set_extractor_correctness.py -q
```

```text
uv run pytest tests/fund/test_small_golden_set_manifest.py tests/fund/test_small_golden_set_fixture_shape.py tests/fund/test_small_golden_set_source_identity.py tests/fund/test_small_golden_set_parser_mechanics.py tests/fund/test_small_golden_set_extractor_correctness.py -q
```

```text
uv run pytest tests/fund/extractors/test_manager_ownership.py tests/fund/test_data_extractor.py -q
```

```text
uv run ruff check fund_agent/fund/extractors/profile.py fund_agent/fund/extractors/manager_ownership.py fund_agent/fund/extractors/holdings_share_change.py fund_agent/fund/extractors/bond_risk_evidence.py fund_agent/fund/extractors/models.py tests/fund/test_small_golden_set_extractor_correctness.py
```

```text
git diff --check -- fund_agent/fund/extractors/profile.py fund_agent/fund/extractors/manager_ownership.py fund_agent/fund/extractors/holdings_share_change.py fund_agent/fund/extractors/bond_risk_evidence.py fund_agent/fund/extractors/models.py tests/fund/test_small_golden_set_extractor_correctness.py tests/README.md
```

## Review Plan

1. Send this plan to AgentDS for independent plan review.
2. Send this plan to AgentMiMo for independent plan review.
3. Fix only controller-accepted plan findings in the plan artifact.
4. Run targeted plan re-review if any accepted findings are fixed.
5. Controller writes a row-shape contract decision judgment.
6. If reviews pass and no blocking questions remain, controller creates accepted local checkpoint for this planning gate.
7. Only after accepted checkpoint may controller open the first implementation/test gate.

## Residual Owners

| Residual | Owner | Destination |
|---|---|---|
| Manager portfolio-manager identity/tenure | Future manager contract implementation gate owner | Additive contract + same-source tests before extractor fixes |
| Risk-characteristic text | Future risk contract implementation gate owner | Additive contract + same-source tests before extractor fixes |
| `006597` bond top holding | Future holdings row-shape implementation gate owner | Additive holdings contract + same-source tests before extractor fixes |
| `110020` target ETF holding | Future holdings row-shape implementation gate owner | Additive holdings contract + same-source tests before extractor fixes |
| Real parser/PDF fidelity | Separately authorized parser/FDR/PDF evidence gate owner | Not part of this row-shape contract gate |
| Golden/readiness promotion | Future golden/readiness controller | Remains blocked until separate promotion gate |

## Blocking Questions For Controller

None. The safe route is determinable from accepted control truth, retained excerpt JSON, existing tests, and current extractor/model surfaces without reading PDFs or using network/provider/runtime access.

## Next Entry Point

Next entry point: `row-shape additive output contract implementation planning gate for retained manager / risk / non-equity holdings residuals`.

Minimum controller handoff summary:

```text
Gateflow-governed handoff. You are not controller. Do not start $gateflow. Current gate: row-shape additive output contract implementation planning, classification heavy. Baseline: d61071a. Source truth: AGENTS.md, current-startup-packet, implementation-control, design, retained excerpt JSON, current row-field judgments, this plan. Objective: freeze additive output contracts before any passing tests or extractor fixes. Required decisions: manager -> new portfolio-manager tenure contract; risk -> new risk-characteristic contract; 006597 -> additive bond_top_holdings; 110020 -> additive target_fund_holdings. Non-goals: no PDFs/network/FDR/fallback/live/provider/config/fixture projection/golden promotion/PR state. Stop if existing surfaces are reused in a way that loses row-shape semantics.
```
