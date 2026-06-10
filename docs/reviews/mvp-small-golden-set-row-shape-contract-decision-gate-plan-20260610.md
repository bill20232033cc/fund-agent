# MVP Small Golden Set Row-shape Contract Decision Gate Plan

## Gate

- Gate: `row-shape contract decision gate for retained manager / risk / non-equity holdings residuals`
- Classification: `heavy`
- Date: 2026-06-10
- Role: planning worker
- Artifact: `docs/reviews/mvp-small-golden-set-row-shape-contract-decision-gate-plan-20260610.md`

## Verdict Target

This plan is verdict-ready for controller review if reviewers can confirm:

1. It keeps current code facts separate from accepted future row-shape contracts.
2. It defines exact future contracts before any implementation or tests.
3. It preserves no-live, no-source-acquisition, no-fixture-projection and no-golden-promotion boundaries.

## Review Requirements

This heavy contract gate requires all of the following before any implementation or test gate may open:

1. Two independent plan reviews, one from AgentDS and one from AgentMiMo or equivalent independent reviewers.
2. Controller judgment that explicitly accepts, rejects or defers each review finding.
3. Controller confirmation that the accepted plan remains planning/contract-only and does not authorize source acquisition, tests, extractor implementation, fixture projection, golden/readiness promotion or provider/runtime/config work.

## Current Code And Control Facts

### Accepted Facts

- Five small-golden rows `004393`, `004194`, `006597`, `110020`, `017641` / `2024` have accepted same-source source identity, live EID/FDR acquisition proof and retained PDF-only excerpts.
- Current retained excerpt oracle is `docs/reviews/mvp-small-golden-set-retained-excerpt-fixture-pdf-only-20260609.json`.
- Current row-field extractor correctness tests pass for the current extractor-consumable subset:
  - identity: `fund_code`, `fund_name`
  - scale: `fund_scale`
  - benchmark: `benchmark_text`
  - fee: `management_fee`, `custody_fee`
  - return: one-year target-share NAV growth and benchmark return
  - `110020` tracking error
  - equity-like holdings rows: `004393` top stock, `004194` top index stock, `017641` top equity
- Latest accepted validation for the row-field test family: `37 passed, 4 xfailed`.
- Residuals remain:
  - `manager`
  - retained `risk`
  - `006597` bond top holding
  - `110020` target ETF holding

### Current Extractor Surface Facts

- `extract_manager_ownership()` currently returns `manager_strategy_text`, `turnover_rate`, `manager_alignment` and `holder_structure`; it does not expose a portfolio-manager identity and tenure list.
- `extract_profile()` currently exposes `basic_identity`, `product_profile`, `benchmark`, `index_profile` and `fee_schedule`.
- `product_profile.style_positioning` may be populated from `风险收益特征`, but the accepted gap decision rejected mapping retained `risk` to `style_positioning`.
- `extract_holdings_share_change()` currently exposes `holdings_snapshot.value.top_holdings`, `top_holdings_status`, `top_holdings_source`, `industry_distribution` and `share_change`.
- The accepted equity-like holdings extension uses a test-local raw-header adapter only; no production normalization or new production schema was accepted.

### Not Current Facts

- The contracts below are not implemented.
- No source/test/fixture/golden/readiness artifact currently proves the residual contracts as passing extractor correctness.
- The retained excerpt oracle is not a projected production fixture and is not a golden/readiness promotion artifact.

## Decision Summary

Accept four future row-shape contracts for later gates:

| Residual | Contract name / version | First next action | Current surface decision |
|---|---|---|---|
| `manager` | `portfolio_manager_tenure_list.v1` | same-source failing tests first | insufficient |
| retained `risk` | `risk_characteristic_text.v1` | same-source failing tests first | insufficient; do not use `style_positioning` |
| `006597` bond top holding | `bond_top_holding_row.v1` | same-source failing test first | insufficient |
| `110020` target ETF holding | `target_fund_holding_row.v1` | same-source failing test first | insufficient |

All four contracts are additive future extractor output contracts. They must not replace current accepted identity, performance, fee, tracking-error or equity-like holdings assertions.

## Contract 1: Portfolio-manager Identity And Tenure

### Contract

- Name/version: `portfolio_manager_tenure_list.v1`
- Scope: year-specific portfolio-manager identity and tenure list from annual report `§4.1.2 基金经理简介`.
- Public shape target: additive field under Fund-layer structured extraction, preferably `portfolio_managers` rather than overloading `manager_alignment` or `basic_identity.fund_manager`.

### Required Fields

For each row:

- `fund_code`: string
- `report_year`: integer
- `schema_version`: fixed `portfolio_manager_tenure_list.v1`
- `portfolio_managers`: non-empty list

For each manager entry:

- `name`: string
- `role`: normalized retained role string such as `基金经理` or `基金经理（已离任）`
- `start_date`: ISO `YYYY-MM-DD`
- `source_anchor`: anchor object linking the entry to the retained source

### Optional Fields

- `end_date`: ISO `YYYY-MM-DD`, present only when annual report discloses离任日期
- `role_status`: enum-like derived helper such as `current` / `departed`, only if derived from explicit role or end date; not required for first test gate

### Normalization Rules

- `role` is not a verbatim phrase dump. It is normalized from the retained oracle expected entry, with leading context such as `本基金的` removed.
- Departure semantics must not be dropped: if the retained oracle role contains `已离任`, the normalized role remains `基金经理（已离任）`.
- First manager failing-test gate should assert the retained oracle `role` string exactly, including `基金经理（已离任）` for `004194` 王平.
- `end_date` remains optional at the contract level, but when the retained oracle entry includes `end_date`, the first manager test gate should assert it for that entry.

### Source Anchor Requirements

Each manager entry must anchor to:

- document kind: `annual_report`
- fund code and report year
- section: `§4.1.2 基金经理简介`
- retained PDF page range from oracle anchor
- row-level locator that distinguishes each manager on a shared page

For multi-manager sections, the row-level locator must include at least:

- manager name
- disclosure order within `§4.1.2` for that fund
- a stable section-relative row/paragraph locator or table-row locator when parser output exposes one

The anchor cannot be a manager strategy paragraph, holder structure table, `§9` manager holding table, source payload, LLM summary, synthetic fixture or external search result.

### Expected Oracle Mapping

Use only `fields.manager.expected` and `fields.manager.anchor` in the retained oracle:

| Fund | Expected entries |
|---|---|
| `004393` | 张明, 基金经理, start `2022-08-08` |
| `004194` | 蔡振, 基金经理, start `2021-11-05`; 王平, 基金经理（已离任）, start `2017-03-03`, end `2024-12-31` |
| `006597` | 陶然, 基金经理, start `2020-07-07`; 丁士恒, 基金经理, start `2020-05-15` |
| `110020` | 余海燕, 基金经理, start `2016-04-16`; 庞亚平, 基金经理, start `2022-12-15` |
| `017641` | 张军, 基金经理, start `2023-04-06` |

### Sufficiency Decision

Existing extractor surfaces are insufficient. `manager_strategy_text` is strategy narrative, `manager_alignment` is manager/employee holding disclosure, and `basic_identity.fund_manager` is at most a flat field and not a year-specific manager roster with tenure. A future implementation must add a dedicated roster contract rather than reusing these fields.

## Contract 2: Retained Risk-characteristic Text

### Contract

- Name/version: `risk_characteristic_text.v1`
- Scope: annual-report risk-return characteristic text from the retained oracle risk anchor. Most rows are anchored in `§2.2 基金产品说明`; `006597` is dual-source and also uses `§4.4.1`.
- Public shape target: additive field under product/profile extraction, preferably `risk_characteristics`, not `style_positioning`.

### Required Fields

- `fund_code`: string
- `report_year`: integer
- `schema_version`: fixed `risk_characteristic_text.v1`
- `risk_characteristic_text`: string, exactly matching retained oracle `fields.risk.expected`
- `source_anchor`: anchor object linking the value to every section named by retained oracle `fields.risk.anchor`

### Optional Fields

- `fund_type_risk_label`: short extracted label such as `混合型基金`, `债券型基金`, `沪深300ETF联接基金`
- `special_risk_clauses`: list of explicitly disclosed special risk phrases, for example 港股通、信用风险、流动性风险、汇率风险

Optional fields must be derived only from the same retained risk text or the same anchored sections named by `fields.risk.anchor`. They cannot be inferred from fund code, fund type classifier, market knowledge or unanchored manager narrative.

First test gate asserts only `schema_version`, `risk_characteristic_text` and source anchors. It must not assert `fund_type_risk_label` or `special_risk_clauses` unless a later reviewed contract revision enumerates their per-fund expected values.

### Source Anchor Requirements

The value must anchor to:

- primary section: `§2.2 基金产品说明`
- additional sections when the retained oracle anchor names them; for `006597`, include `§4.4.1`
- retained oracle `fields.risk.anchor`
- retained oracle excerpt or same row-level table locator

It must not anchor to `product_profile.style_positioning` as a semantic substitute unless the future extractor exposes the same `risk_characteristic_text.v1` contract with a retained-risk anchor. The contract is explicitly not `style_positioning`.

### Expected Oracle Mapping

Use only `fields.risk.expected` as the exact assertion string. This is the retained oracle's normalized expected value, not a verbatim excerpt assertion. The normalization rule is:

- preserve the retained oracle `expected` string exactly in tests;
- treat the retained oracle `excerpt` as source-clause evidence, not as the assertion string;
- combine multiple source clauses only when `fields.risk.anchor` names multiple sections;
- normalize punctuation and clause framing according to the retained oracle `expected` value rather than letting implementation invent new paraphrases.

| Fund | Exact expected string | Source anchor requirement |
|---|---|---|
| `004393` | 混合型基金；高于债券型和货币市场基金，低于股票型基金；含港股通特有风险 | `PDF p5 §2.2 基金产品说明` |
| `004194` | 股票指数增强型基金；较高风险、较高预期收益 | `PDF p5 §2.2 基金产品说明` |
| `006597` | 债券型基金；较低预期风险和预期收益；操作中强调信用风险和流动性风险控制 | `PDF p5 §2.2 and p21 §4.4.1`; clause 1 from `§2.2` risk-return type, clause 2 from `§4.4.1` credit/liquidity risk control wording |
| `110020` | 沪深300ETF联接基金；高于混合型、债券基金和货币市场基金；风险收益与业绩比较基准相似 | `PDF p6 §2.2 基金产品说明` |
| `017641` | 股票型被动指数基金；境外证券市场投资；含汇率风险等特别投资风险 | `PDF p7 §2.2 基金产品说明` |

### Sufficiency Decision

Existing extractor surfaces are insufficient. Current `product_profile.style_positioning` can capture risk-return wording, but prior accepted review found that mapping retained `risk` to `style_positioning` is conceptually unsafe. The future contract must preserve risk-characteristic semantics separately and must include source anchors.

## Contract 3: `006597` Bond Top Holding

### Contract

- Name/version: `bond_top_holding_row.v1`
- Scope: first row of annual-report bond investment detail table for a bond fund.
- Public shape target: additive holding sub-shape, preferably `holdings_snapshot.value.bond_top_holdings`, not stock `top_holdings`.

### Required Fields

- `fund_code`: string, fixed `006597` for first same-source test
- `report_year`: integer, fixed `2024` for first same-source test
- `schema_version`: fixed `bond_top_holding_row.v1`
- `bond_top_holdings`: non-empty list

For the first holding row:

- `code`: string
- `name`: string
- `fair_value_cny`: retained numeric string
- `net_asset_ratio`: retained percentage string
- `source_anchor`: anchor object

### Optional Fields

- `rank`: integer or string, only if the bond table explicitly discloses row order. The first same-source test must not assert rank because the retained oracle has no `rank` value.
- `quantity`: string, only if same row explicitly discloses it and parser surface preserves it
- `bond_type`: string, only if disclosed in same row/table

### Source Anchor Requirements

The value must anchor to:

- section: `§8.6 前五名债券投资明细`
- retained oracle anchor `PDF p61 §8.6 前五名债券投资明细`
- row-level locator for `230214 23国开14`

It must not use NAV data, bond risk evidence groups, manager strategy text, synthetic expected fields or any external source.

### Expected Oracle Mapping

Use only `fields.holdings.expected.top_bond_table_row` for `006597`:

- `code`: `230214`
- `name`: `23国开14`
- `fair_value_cny`: `1,133,300,622.22`
- `net_asset_ratio`: `9.00%`

### Sufficiency Decision

Existing extractor surfaces are insufficient. Current `holdings_snapshot.top_holdings` is designed around stock/equity-like table headers and accepted only for `top_ten` or `all_stock_investment_details` equity-like rows. A bond top holding must be a separate additive holding sub-shape so that stock rows, bond rows and target-fund rows do not share misleading status/source semantics.

## Contract 4: `110020` Target ETF Holding

### Contract

- Name/version: `target_fund_holding_row.v1`
- Scope: annual-report target-fund holding row for an ETF feeder fund.
- Public shape target: additive holding sub-shape, preferably `holdings_snapshot.value.target_fund_holdings`, not stock `top_holdings`.

### Required Fields

- `fund_code`: string, fixed `110020` for first same-source test
- `report_year`: integer, fixed `2024` for first same-source test
- `schema_version`: fixed `target_fund_holding_row.v1`
- `target_fund_holdings`: non-empty list

For the retained target ETF row:

- `name`: string
- `fair_value_cny`: retained numeric string
- `net_asset_ratio`: retained percentage string
- `source_anchor`: anchor object

### Optional Fields

- `target_fund_code`: string, only if same table explicitly discloses it
- `holding_kind`: fixed helper value `target_etf_holding`
- `rank`: integer or string, only if same table explicitly discloses row order

### Source Anchor Requirements

The value must anchor to:

- section: `§8.2 期末投资目标基金明细`
- retained oracle anchor `PDF p64 §8.2 期末投资目标基金明细`
- row-level locator for `易方达沪深300交易型开放式指数发起式证券投资基金`

It must not be inferred from fund name, benchmark, tracking error, index profile or external ETF metadata.

### Expected Oracle Mapping

Use only `fields.holdings.expected.target_etf_holding` for `110020`:

- `name`: `易方达沪深300交易型开放式指数发起式证券投资基金`
- `fair_value_cny`: `19,085,355,845.40`
- `net_asset_ratio`: `93.19%`

### Sufficiency Decision

Existing extractor surfaces are insufficient. `110020` tracking error is already current extractor-consumable and accepted, but tracking error does not prove target ETF holding extraction. Current holdings extractor stock-table semantics are not enough for target-fund holdings because the table shape lacks stock code/name headers and expresses a target fund rather than a stock or ordinary equity row.

## Residual Owners And Next Gates

| Residual | Controller-owned next gate | Owner role | Acceptance destination |
|---|---|---|---|
| `portfolio_manager_tenure_list.v1` | same-source failing manager test gate | controller assigns test worker after this plan is accepted | reviewed failing tests before implementation |
| `risk_characteristic_text.v1` | same-source failing risk test gate | controller assigns test worker after this plan is accepted | reviewed failing tests before implementation |
| `bond_top_holding_row.v1` | same-source failing `006597` bond holding test gate | controller assigns test worker after this plan is accepted | reviewed failing tests before implementation |
| `target_fund_holding_row.v1` | same-source failing `110020` target ETF holding test gate | controller assigns test worker after this plan is accepted | reviewed failing tests before implementation |
| additive extractor implementation for any accepted contract | one-contract implementation gate | controller assigns implementation worker only after accepted failing tests | reviewed additive fix and local validation |

## Next Gate File Scope

### Next Same-source Failing Test Gate

Allowed files:

- `tests/fund/test_small_golden_set_extractor_correctness.py`
- `tests/README.md`, only if test coverage documentation changes
- `docs/reviews/mvp-small-golden-set-row-shape-contract-decision-gate-*-implementation-evidence-20260610.md`
- `docs/reviews/mvp-small-golden-set-row-shape-contract-decision-gate-*-code-review-*.md`
- `docs/reviews/mvp-small-golden-set-row-shape-contract-decision-gate-*-controller-judgment-*.md`

Forbidden files:

- `fund_agent/**`
- `tests/fixtures/**`
- `reports/**`
- `README.md`
- `fund_agent/**/README.md`
- `docs/design.md`
- `docs/implementation-control.md`
- `docs/current-startup-packet.md`
- `docs/fund-analysis-template-draft.md`
- `configs/**`
- provider/runtime/budget/config files
- golden/readiness files

### Later Additive Extractor Fix Gate

Allowed only after reviewed same-source failing tests prove a current extractor failure:

- `fund_agent/fund/extractors/models.py`, only for additive typed/dataclass surface if needed
- `fund_agent/fund/extractors/manager_ownership.py`, only for `portfolio_manager_tenure_list.v1`
- `fund_agent/fund/extractors/profile.py`, only for `risk_characteristic_text.v1`
- `fund_agent/fund/extractors/holdings_share_change.py`, only for `bond_top_holding_row.v1` or `target_fund_holding_row.v1`
- `fund_agent/fund/data_extractor.py`, only if the additive field must be surfaced through `StructuredFundDataBundle`
- `tests/fund/test_small_golden_set_extractor_correctness.py`
- `tests/README.md`, only if test coverage documentation changes
- matching implementation evidence/review/controller artifacts under `docs/reviews/`

Forbidden files for the additive fix gate:

- `tests/fixtures/**`
- `reports/**`
- `docs/design.md`, unless a separate controller authorizes post-acceptance design sync
- `docs/implementation-control.md`, unless a separate controller authorizes control sync
- `docs/current-startup-packet.md`
- `docs/fund-analysis-template-draft.md`
- root or package README files other than `tests/README.md` unless the implementation changes documented public usage
- any source acquisition, provider/runtime/budget/config, fallback, fixture projection, golden/readiness or PR/release state file

## Implementation Sequencing

1. Same-source failing test gate for `portfolio_manager_tenure_list.v1`.
   - Highest priority because manager identity/tenure is a public report semantic and current extractor has no equivalent surface.
   - Add strict xfail-to-fail or explicit failing assertions from retained oracle only; do not implement.
2. Additive extractor fix for `portfolio_manager_tenure_list.v1`, only if the failing test gate is accepted.
3. Same-source failing test gate for `risk_characteristic_text.v1`.
   - Keep separate because it rejects the tempting but unsafe `style_positioning` shortcut.
4. Additive extractor fix for `risk_characteristic_text.v1`, only if failing tests are accepted.
5. Same-source failing test gate for `bond_top_holding_row.v1`.
   - Then additive holdings fix if proven.
6. Same-source failing test gate for `target_fund_holding_row.v1`.
   - Then additive holdings fix if proven.

Recommended slice order is manager -> risk -> `006597` bond top holding -> `110020` target ETF holding. Do not combine all four implementation fixes in one slice; each contract can change public extractor schema semantics and must remain reviewable.

## No-live Validation Matrix

| Gate | Validation | Expected result |
|---|---|---|
| This plan gate | `git diff --check -- docs/reviews/mvp-small-golden-set-row-shape-contract-decision-gate-plan-20260610.md` | no output |
| This plan gate | manual review against required inputs | reviewers confirm no implementation claim and no scope leak |
| Same-source failing test gate | `uv run pytest tests/fund/test_small_golden_set_extractor_correctness.py -q` | existing passing subset remains pass; newly accepted residual assertions fail or strict xfail exactly as planned |
| Same-source failing test gate | `uv run pytest tests/fund/test_small_golden_set_manifest.py tests/fund/test_small_golden_set_fixture_shape.py tests/fund/test_small_golden_set_source_identity.py tests/fund/test_small_golden_set_parser_mechanics.py tests/fund/test_small_golden_set_extractor_correctness.py -q` | no regression outside planned residual failures |
| Same-source failing test gate | `uv run ruff check tests/fund/test_small_golden_set_extractor_correctness.py` | pass |
| Additive fix gate | same pytest family plus ruff on touched files | residual-specific tests pass; existing current subset still passes |
| Additive fix gate | `git diff --check -- <touched files>` | no output |

No validation step may call network, PDF reading, `FundDocumentRepository.load_annual_report()`, fallback, live LLM, provider probes, fixture projection, golden/readiness promotion, PR, push or release commands.

## Stop Conditions

Stop before implementation or test expansion if any of these occur:

- A reviewer cannot confirm that a contract is additive and separate from existing current surfaces.
- A proposed test needs any source other than `docs/reviews/mvp-small-golden-set-retained-excerpt-fixture-pdf-only-20260609.json`.
- A proposed test requires live PDF parsing, network, FDR acquisition, fallback or fixture projection.
- A proposed assertion would use `style_positioning` as the retained `risk` oracle.
- A proposed holdings assertion would force stock, bond and target-fund rows into one ambiguous `top_holdings` schema without explicit kind/source status.
- A proposed manager assertion would use manager holding/alignment as a proxy for portfolio-manager tenure.
- A future implementation slice would wire more than one additive contract into `StructuredFundDataBundle`.
- Any fix needs provider/default/runtime/budget/config changes.
- Any change would promote fixture, golden, readiness, release, PR or external state.
- Any unrelated dirty or untracked workspace residue becomes necessary as proof.

## Explicit Non-goals

- No source acquisition.
- No PDF read.
- No network.
- No `FundDocumentRepository` live use.
- No fallback invocation.
- No extractor implementation in this gate.
- No test implementation in this gate.
- No fixture projection.
- No golden/readiness promotion.
- No live LLM.
- No provider/default/runtime/budget/config changes.
- No docs/design sync in this planning-worker artifact.
- No docs/implementation-control or current-startup-packet sync in this planning-worker artifact.
- No PR, push, release, merge or mark-ready action.

## Completion Report Format

When this planning worker completes, report only:

- artifact path
- verdict-ready status
- blockers
