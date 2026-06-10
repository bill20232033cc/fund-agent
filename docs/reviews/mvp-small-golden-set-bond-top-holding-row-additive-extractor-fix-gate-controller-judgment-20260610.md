# MVP Small Golden Set Bond Top Holding Row Additive Extractor Fix Gate Controller Judgment - 2026-06-10

## Judgment

Accepted for implementation.

## Basis

- The current control truth lists `bond_top_holding_row.v1` additive extractor fix as the next valid entry.
- The plan is code-generation-ready and uses the accepted same-source strict xfail as its contract.
- Plan review reports no blocking findings.

## Approved Scope

- Add a dedicated bond top holding table detector and extractor in `fund_agent/fund/extractors/holdings_share_change.py`.
- Convert the dedicated bond strict xfail into a passing correctness test.
- Update package/test README only for current behavior.
- Produce implementation evidence and code review artifacts before accepted implementation commit.

## Preserved Boundaries

- No source acquisition, fallback, PDF/FDR/network/live LLM, provider/runtime/config, fixture projection, golden/readiness promotion or downstream bundle/report integration.
- `target_fund_holding_row.v1` remains a separate next gate.
