# Plan Review: target_fund_holding_row.v1 additive extractor fix gate

## Verdict

Pass. No blocking findings.

## Review Notes

- The plan is code-generation-ready: it names the exact extractor file, test files, output keys, source-anchor shape and validation commands.
- Scope is correctly additive. `target_fund_holdings` is a dedicated sub-shape and does not reuse stock `top_holdings` or bond `bond_top_holdings`.
- The plan preserves the accepted oracle boundary: no PDF, repository, source helper, fallback, provider, network, fixture projection or golden/readiness promotion.
- The no-code rule is explicit and matches the accepted oracle, which only contains `name`, `fair_value_cny` and `net_asset_ratio`.
- Downstream bundle/snapshot/report/quality integration remains out of scope and must stay a later separately authorized gate.

## Residual Risk

The implementation must avoid broad table matching that could classify ordinary fund identity tables as target-fund holdings. The planned required headers `基金名称`, `公允价值`, and `占基金资产净值比例` are sufficient for this narrow gate.
