# P19-S4 Source Feasibility Controller Judgment - 2026-05-23

## Inputs

- P19-S4 plan: `docs/reviews/p19-s4-expanded-index-coverage-plan-20260523.md`
- Plan reviews:
  - `docs/reviews/p19-s4-plan-review-mimo-20260523.md`
  - `docs/reviews/p19-s4-plan-review-glm-20260523.md`
  - `docs/reviews/p19-s4-plan-review-controller-judgment-20260523.md`
- Source feasibility: `docs/reviews/p19-s4-source-feasibility-20260523.md`
- Design truth: `docs/design.md` v2.2 §11

## Judgment

Verdict: P19-S4 BLOCKED_DEFERRED

P19-S4 cannot be implemented under the current thermometer design because no verified source provides exact target-index PE+PB historical series for the five P19-S4 indexes.

The feasibility pass went beyond the initially blocked Legulegu `stock_index_pe_lg` / `stock_index_pb_lg` path. It checked the relevant akshare index valuation candidates and minimally probed official 中证 / 国证 routes. The best available official source proves exact identity and PE for several targets but lacks PB; the 国证 path proves 创业板指 identity and current PE but lacks PE+PB history. This does not satisfy `docs/design.md` §11.2, which defines the thermometer as PE percentile plus PB percentile.

## Per-Target Decision

| Code | Index | Decision | Reason |
|---|---|---|---|
| `399006` | 创业板指 | deferred | 国证 proves identity/current PE only; no PE+PB history |
| `000688` | 科创50 | deferred | 中证 indicator proves identity and PE-only recent rows; no PB |
| `000922` | 中证红利 | deferred | 中证 indicator proves identity and PE-only recent rows; no PB |
| `000932` | 中证消费 | deferred | 中证 indicator proves identity and PE-only recent rows; no PB |
| `000933` | 中证医药 | deferred | 中证 indicator proves identity and PE-only recent rows; no PB |

## Controller Decisions

- Do not change `fund_agent/fund/data/thermometer_source.py` supported mappings for these targets.
- Do not use PE-only, dividend yield, current-only valuation, constituents, weights, or adjacent indexes as substitutes.
- Do not change `fund-analysis thermometer` no-index behavior.
- Do not broaden `fund-analysis analyze` automatic `ValuationStateResolution` mapping.
- Do not change the PE+PB algorithm inside P19-S4.

## Residual Owners

- Future source-acquisition gate: find exact target-index PB history plus PE history for these indexes, or record a paid/licensed/manual data-source decision.
- Future design gate, if desired: redefine a separate PE-only official-index indicator. That would not be the current P19 thermometer and must update `docs/design.md` before implementation.

## Validation

- `git diff --check` passed in the source feasibility pass.

## Next Gate

P19-S5 / all-A PE source gate, unless the controller chooses a separate post-P19 source-acquisition planning lane first.

