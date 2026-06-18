# MVP Small Golden Set Row-shape Contract Decision Gate Controller Judgment

## Gate

- Gate: `row-shape contract decision gate for retained manager / risk / non-equity holdings residuals`
- Classification: `heavy`
- Date: 2026-06-10
- Controller: AgentController
- Plan: `docs/reviews/mvp-small-golden-set-row-shape-contract-decision-gate-plan-20260610.md`

## Scope Judgment

Accepted as a planning and contract decision gate only. This gate defines accepted future row-shape contracts for later same-source failing test gates and later additive extractor fixes. It does not implement those contracts, does not add tests, does not project fixtures, does not read PDF/source/network/FDR, does not enable fallback, and does not change golden/readiness semantics.

The retained oracle remains `docs/reviews/mvp-small-golden-set-retained-excerpt-fixture-pdf-only-20260609.json`.

## Accepted Future Contracts

| Residual | Accepted future contract | First allowed next action |
|---|---|---|
| Portfolio-manager identity and tenure | `portfolio_manager_tenure_list.v1` | Same-source failing manager test gate |
| Retained risk-characteristic text | `risk_characteristic_text.v1` | Same-source failing risk test gate |
| `006597` bond top holding | `bond_top_holding_row.v1` | Same-source failing bond holding test gate |
| `110020` target ETF holding | `target_fund_holding_row.v1` | Same-source failing target ETF holding test gate |

These contracts are accepted future design. They are not current code facts.

## Review Inputs

| Reviewer | Artifact | Verdict |
|---|---|---|
| AgentDS | `docs/reviews/mvp-small-golden-set-row-shape-contract-decision-gate-plan-review-ds-20260610.md` | PASS_WITH_FINDINGS; 0 blockers |
| AgentMiMo | `docs/reviews/mvp-small-golden-set-row-shape-contract-decision-gate-plan-review-mimo-20260610.md` | PASS_WITH_FINDINGS; 0 blockers; requested F1 fix before judgment |
| AgentDS targeted re-review | `docs/reviews/mvp-small-golden-set-row-shape-contract-decision-gate-plan-rereview-ds-20260610.md` | PASS; all 4 DS findings resolved |
| AgentMiMo targeted re-review | `docs/reviews/mvp-small-golden-set-row-shape-contract-decision-gate-plan-rereview-mimo-20260610.md` | PASS; all 7 MiMo findings resolved |

## Controller Finding Decisions

| Finding | Decision | Rationale |
|---|---|---|
| DS F1 / MiMo F5: bond `rank` was required despite no oracle value | Accepted and resolved | Plan now makes `rank` optional and forbids first-test assertion unless retained oracle has it. |
| DS F2 / MiMo F3: manager role/status normalization needed precision | Accepted and resolved | Plan now defines normalized retained role, preserves `基金经理（已离任）`, and requires asserting `end_date` when oracle provides it. |
| DS F3 / MiMo F1: `006597` risk text and anchor needed dual-source semantics | Accepted and resolved | Plan now distinguishes oracle `expected` from `excerpt`, requires exact `fields.risk.expected`, and records `006597` as `§2.2 + §4.4.1` dual-source. |
| DS F4: multi-manager row-level locator was underspecified | Accepted and resolved | Plan now requires name, disclosure order and stable section-relative row/paragraph/table locator when parser output exposes one. |
| MiMo F2: heavy gate needed explicit two-reviewer requirement | Accepted and resolved | Plan now requires two independent plan reviews and controller finding-by-finding judgment before implementation/test gates. |
| MiMo F4: optional risk fields lacked first-test guidance | Accepted and resolved | Plan now limits first risk test gate to `schema_version`, exact `risk_characteristic_text` and source anchors unless a later contract revision enumerates optional expectations. |
| MiMo F6: `StructuredFundDataBundle` wiring could become too broad | Accepted and resolved | Plan now stops any future implementation slice that wires more than one additive contract into the bundle. |
| MiMo F7: residual owners were not explicit | Accepted and resolved | Plan now has controller-owned next gates and acceptance destinations for each residual. |

## Validation

Controller validation:

```text
git diff --check -- docs/reviews/mvp-small-golden-set-row-shape-contract-decision-gate-plan-20260610.md docs/reviews/mvp-small-golden-set-row-shape-contract-decision-gate-plan-review-ds-20260610.md docs/reviews/mvp-small-golden-set-row-shape-contract-decision-gate-plan-review-mimo-20260610.md docs/reviews/mvp-small-golden-set-row-shape-contract-decision-gate-plan-rereview-ds-20260610.md docs/reviews/mvp-small-golden-set-row-shape-contract-decision-gate-plan-rereview-mimo-20260610.md docs/reviews/mvp-small-golden-set-row-shape-contract-decision-gate-controller-judgment-20260610.md
```

Result: PASS after final validation.

No pytest, ruff, live EID/network/PDF/FDR, fallback, provider or LLM commands were authorized or run for this planning gate.

## Residuals And Next Entry

Next entry is the same-source failing manager test gate for `portfolio_manager_tenure_list.v1`, unless the controller/user deliberately chooses a different accepted contract slice. The next gate may add tests only; it must not implement extractor fixes until same-source failing tests are accepted.

Valid queued alternatives:

- same-source failing risk test gate for `risk_characteristic_text.v1`;
- same-source failing `006597` bond holding test gate for `bond_top_holding_row.v1`;
- same-source failing `110020` target ETF holding test gate for `target_fund_holding_row.v1`;
- a separately authorized non-extractor phase.

Still unauthorized: source acquisition, PDF read, network, `FundDocumentRepository` live use, fallback, extractor implementation, fixture projection, golden/readiness promotion, provider/default/runtime/budget/config changes, Chapter calibration, Agent runtime expansion, multi-year, score-loop, PR, push, release, merge or mark-ready.

## Final Judgment

Accepted locally. Next recommended entry is the same-source failing manager test gate for `portfolio_manager_tenure_list.v1`.
