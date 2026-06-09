# MVP Small Golden Set Row-field Extractor Gap Decision Gate

## Gate

- Gate: `row-field extractor gap decision gate for retained manager / holdings / risk fields`
- Classification: `standard`
- Date: 2026-06-09
- Controller: AgentController
- Prior accepted checkpoint: `4f28306 gateflow: accept row-field extractor correctness tests`

## Objective

Decide the next safe extractor-facing route for retained `manager`, `holdings` and `risk` fields after accepted same-source retained excerpts, without modifying extractor code, adding tests, reading PDFs, invoking `FundDocumentRepository`, running network/fallback/live/provider probes, changing config/runtime, projecting fixtures or promoting golden/readiness.

## Inputs

- Control truth: `docs/implementation-control.md`
- Startup packet: `docs/current-startup-packet.md`
- Design truth: `docs/design.md`
- Accepted retained excerpt oracle: `docs/reviews/mvp-small-golden-set-retained-excerpt-fixture-pdf-only-20260609.json`
- Accepted row-field correctness tests: `tests/fund/test_small_golden_set_extractor_correctness.py`

## Current Facts

- The accepted row-field correctness test gate already proves same-source extractor correctness for identity, share-unit scale, benchmark, management/custody fee, one-year return and `110020` tracking error.
- `manager`, `holdings` and `risk` remain strict xfail markers in the accepted test. Those xfails are blocked-gap records, not accepted passing correctness.
- The current decision gate is docs-only and does not change product behavior.

## Field Decisions

| Field | Retained expected shape | Current extractor surface | Decision | Reason |
|---|---|---|---|---|
| `risk` | Single retained risk-characteristic string for each row, including fund-type risk, relative risk ranking and special risk clauses | `extract_profile(report).product_profile.value["style_positioning"]` can consume some `风险收益特征` / `风格定位` / `产品定位` labels, but its output contract is product style positioning, not the retained risk-characteristic contract | Defer to row-shape contract decision before tests | Review found that mapping retained `risk` to `style_positioning` is conceptually unsafe: retained values include clauses such as 港股通风险、信用/流动性控制 and QDII 汇率风险. These may come from different annual-report sections and are not guaranteed to equal a single §2 style-positioning label. Writing passing tests now would risk accepting the wrong output contract |
| `holdings` | Heterogeneous first-row holdings shapes: stock/index stock/bond/target ETF/QDII equity | `extract_holdings_share_change(report).holdings_snapshot` consumes stock-like §8 top holdings and all-stock details tables; it is not a generic bond/ETF-target holding extractor | Split by row shape before implementation | Equity-like rows (`004393`, `004194`, `017641`) may enter a test-only extension gate using current `holdings_snapshot.top_holdings`. Bond row `006597` and ETF-linked target holding `110020` need row-shape decision before tests because the current extractor name and status vocabulary are stock-oriented |
| `manager` | Portfolio manager list with name, role and start/end dates | `profile.basic_identity.value["fund_manager"]` is a simple profile string; `extract_manager_ownership()` handles strategy/turnover/manager holding/holder structure, not portfolio-manager tenure identity | Defer to row-shape contract decision before tests | Existing surfaces are not the same output contract as retained `manager` expected values. Writing a failing test now would test an undefined target and risk confusing management company/profile string, manager ownership, and portfolio manager tenure |

## Accepted Next Route

Open a `row-field correctness test extension gate for retained equity-like holdings subset`.

Allowed in that next gate:

- Use only `docs/reviews/mvp-small-golden-set-retained-excerpt-fixture-pdf-only-20260609.json`.
- Add holdings tests only for equity-like row shapes that map to current `holdings_snapshot.top_holdings`:
  - `004393`: `top_stock_table_row`
  - `004194`: `top_index_stock_table_row`
  - `017641`: `top_equity_table_row`
- Decide in that test gate whether to assert raw extractor header keys or a test-local comparison adapter for canonical oracle keys (`code`, `name`, `fair_value_cny`, `net_asset_ratio`). Do not add production normalization in this gate.
- Keep `006597` `top_bond_table_row` and `110020` `target_etf_holding` out of default passing correctness until a row-shape design gate decides whether they belong to `holdings_snapshot`, bond risk evidence, a target-fund holding field, or a new output contract.
- Keep `manager` out of default passing correctness until a portfolio-manager identity/tenure output contract is explicitly accepted.
- Keep `risk` out of default passing correctness until a risk-characteristic output contract is explicitly accepted.

Forbidden in that next gate:

- Extractor modification.
- PDF read, `FundDocumentRepository` live acquisition, network, fallback, live LLM, endpoint/provider probe.
- Provider/default/runtime/budget/config changes.
- Fixture projection, full golden/readiness promotion, release, merge or mark-ready.

## Deferred Residuals

| Residual | Owner | Required next decision |
|---|---|---|
| Portfolio manager list/tenure | Future manager row-shape contract gate | Decide canonical output field, list ordering, current/left manager treatment, date normalization and relationship to existing `profile.fund_manager` |
| Retained risk-characteristic text | Future risk row-shape contract gate | Decide whether retained risk belongs to product profile, bond/QDII risk evidence, risk disclosure summary, or a new output contract; define exact-vs-contains semantics and source-section eligibility |
| Bond top holding (`006597`) | Future holdings row-shape contract gate | Decide whether bond top holding belongs to generic holdings snapshot, bond risk evidence, or a new fixed-income holding field |
| ETF target holding (`110020`) | Future holdings row-shape contract gate | Decide whether target ETF holding belongs to holdings snapshot, target-fund exposure, or a new linked-fund holding field |
| Production parser fidelity | Future parser/FDR evidence gate | Prove real PDF parser table shape through authorized repository/PDF gate, not through this docs-only decision gate |

## Verification Matrix

| Check | Evidence |
|---|---|
| Branch/status reviewed | `git branch --show-current`; `git status --short` |
| Rule/control/design truth reviewed | `AGENTS.md`; `docs/current-startup-packet.md`; `docs/implementation-control.md`; `docs/design.md` |
| Retained expected shapes reviewed | `jq` over accepted retained excerpt oracle |
| Extractor surfaces reviewed | `profile.py`, `holdings_share_change.py`, `manager_ownership.py`, `bond_risk_evidence.py`, extractor model/tests |
| No implementation performed | This artifact only; no source/test/config/runtime changes |

## Stop Conditions

- If review finds current holdings extractor cannot reliably represent any retained holdings row without changing extractor behavior, do not open holdings tests; move all holdings rows to row-shape contract decision.
- If the next holdings test gate cannot compare oracle canonical keys to raw extractor table keys without production normalization, stop and return to row-shape decision.
- If any route requires PDF/FDR/network/fallback/live/provider/config/golden promotion, stop and require a separately authorized gate.
