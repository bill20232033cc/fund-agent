# P19-S5 Source Feasibility Controller Judgment — 2026-05-23

## Scope

- Phase: P19 thermometer independent development
- Gate: P19-S5 source feasibility execution
- Design truth: `docs/design.md` v2.2 §11
- Control truth: `docs/implementation-control.md`
- Worker artifact: `docs/reviews/p19-s5-source-feasibility-20260523.md`

## Controller Verdict

Verdict: `ACCEPT_IMPLEMENTATION_PLAN`

AgentDS independently validated a design-compatible all-A PE+PB historical source contract:

- all-A PE history: `akshare.stock_a_ttm_lyr()` / Legulegu `market-ttm-lyr?marketId=5`
- all-A PB history: `akshare.stock_a_all_pb()` / Legulegu `market-index-pb?marketId=ALL`
- selected PE field: `middlePETTM` (median trailing PE)
- selected PB field: `middlePB` (median PB)
- common usable dates: 4828 days, 2005-01-05 to 2026-05-22
- access: public Legulegu pages through akshare 1.18.60, no login, paid source, or Youzhiyouxing production scrape

Based on `docs/design.md` §11 and first principles, this satisfies the source gate because the source contract provides exact all-A identity, PE and PB history, equal-weight / median-oriented semantics, TTM PE basis compatible with the existing index thermometer direction, sufficient historical coverage, and documented negative controls for PB-only, PE-only, board-level, index-level, stock-level, and current-only substitutes.

## Accepted Findings

### F1 — All-A PE Candidate Validated

- Status: accepted.
- Evidence: `stock_a_ttm_lyr()` returns 5186 raw rows / 5182 unique dates, 2005-01-05 to 2026-05-22, with `middlePETTM`, `averagePETTM`, `middlePELYR`, and `averagePELYR`.
- Controller reasoning: `middlePETTM` is the best current implementation field because §11 defines PE as historical PE median percentile and the existing index thermometer already uses trailing PE median semantics.

### F2 — All-A PB Contract Remains Compatible

- Status: accepted.
- Evidence: `stock_a_all_pb()` returns 5184 unique dates, 2005-01-04 to 2026-05-22, with `middlePB` and `equalWeightAveragePB`.
- Controller reasoning: `middlePB` matches §11's PB median percentile requirement and avoids PB-only thermometer scope creep.

### F3 — Negative Controls Close Substitute Risk

- Status: accepted.
- Evidence: board/market wrappers, index wrappers, Eastmoney spot, CSIndex valuation, dividend-yield, congestion, and guessed direct endpoints were classified and rejected where not exact all-A PE+PB history.
- Controller reasoning: this protects the design boundary by preventing board-level, index-level, current-only, PE-only, or PB-only data from masquerading as the P19 all-A thermometer.

## Implementation Plan Constraints

The next gate is an implementation plan/review, not coding. The plan must explicitly include:

- source adapter ownership under the existing Thermometer data-source boundary, with no UI or Service direct akshare calls;
- explicit `wind_all_a` or equivalent all-A market code, without overloading index code semantics;
- source-shaped fixtures for both PE and PB responses;
- strict date parsing, positive numeric validation, duplicate-date handling, and common-date merge semantics;
- retry/unavailable behavior for observed Legulegu SSL EOF and Eastmoney-style connection failures;
- field freezing to `middlePETTM` and `middlePB` unless the plan deliberately proposes a design change;
- cache and CLI behavior that does not regress P19-S1/S2 index thermometer behavior;
- no new `fund-analysis analyze` behavior beyond the already accepted P19-S3 exact-identity integration boundaries.

## Residual Risks

- Legulegu public token and SSL EOF behavior are source-operational risks, not source-identity blockers; implementation must fail closed to `unavailable` and rely on cache/fixtures in tests.
- Legulegu does not publish a full per-security all-A inclusion rule; this is acceptable for current design because §11 targets methodologically consistent public all-A valuation series, not precise reproduction of Youzhiyouxing.
- P19-S4 expanded-index source coverage remains deferred and is not reopened by this all-A acceptance.

## Next Gate

Proceed to `P19-S5 all-A market thermometer implementation plan/review`.

Do not implement until a code-generation-ready plan is independently reviewed and accepted.
