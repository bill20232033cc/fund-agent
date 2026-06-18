# Controller Judgment: target_fund_holding_row.v1 additive extractor fix gate plan

## Judgment

Accepted for implementation.

## Basis

- Current control truth lists `target_fund_holding_row.v1` additive extractor fix as a valid next entry.
- The accepted same-source failing test proves a dedicated target-fund holding surface is absent.
- The plan keeps the fix inside Fund holdings extraction and does not alter source, fallback, fixture, golden/readiness, provider/runtime/config or downstream integration boundaries.
- Plan review reports no blocking findings.

## Approved Scope

- Add `target_fund_holdings` under `extract_holdings_share_change().holdings_snapshot.value`.
- Parse only explicit `§8.2 期末投资目标基金明细`-style tables with `基金名称`, `公允价值`, and `占基金资产净值比例`.
- Return row fields `name`, `fair_value_cny`, `net_asset_ratio`, and serializable `source_anchor`.
- Remove only the dedicated target-fund strict xfail after the implementation makes it pass.
- Update focused tests and README text as needed.

## Preserved Boundaries

- No PDF/source/repository/FDR/fallback/network/live LLM/provider/runtime/config behavior.
- No fixture projection, golden/readiness promotion, bundle/snapshot/report/renderer/quality/checklist/Service/Host/Agent integration.
- No target ETF code assertion or inference.
