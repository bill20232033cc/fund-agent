# MVP Small Golden Set Row-field Extractor Gap Decision Gate Controller Judgment

## Gate

- Gate: `row-field extractor gap decision gate for retained manager / holdings / risk fields`
- Classification: `standard`
- Date: 2026-06-09
- Controller: AgentController
- Prior accepted checkpoint: `4f28306 gateflow: accept row-field extractor correctness tests`
- Decision artifact: `docs/reviews/mvp-small-golden-set-row-field-extractor-gap-decision-gate-20260609.md`

## Scope Judgment

This gate is accepted as a docs-only row-field route decision. It did not change extractor code, tests, fixtures, provider/default/runtime/budget/config, PDF access, `FundDocumentRepository`, fallback behavior, live LLM behavior, golden/readiness semantics, release state or PR state.

The gate objective was to decide the next safe extractor-facing route for the retained `manager`, `holdings` and `risk` gaps after accepted same-source retained excerpts and accepted row-field extractor correctness tests.

## Review Inputs

| Reviewer | Artifact | Final result |
|---|---|---|
| AgentDS | `docs/reviews/mvp-small-golden-set-row-field-extractor-gap-decision-gate-review-ds-20260609.md` | PASS after targeted re-review; no blocking findings |
| AgentMiMo | `docs/reviews/mvp-small-golden-set-row-field-extractor-gap-decision-gate-review-mimo-20260609.md` | PASS after targeted re-review; original blocking `risk` finding fixed |

## Controller Finding Decisions

| Finding | Decision | Rationale |
|---|---|---|
| MiMo F1: `risk` mapped to `style_positioning` is conceptually unsafe | Accepted and fixed in the decision artifact | Retained `risk` values include risk-characteristic clauses such as 港股通风险、信用/流动性控制 and QDII 汇率风险. These are not guaranteed to equal a single product style-positioning label, so passing tests would accept the wrong output contract |
| DS F1 / MiMo F2: equity-like holdings need raw-header versus canonical-key comparison decision | Accepted as next-gate stop condition, not current blocker | The next test gate may decide raw extractor header assertions or a test-local comparison adapter. It must stop if comparison requires production normalization |
| DS F3 / MiMo F3: manager deferral rationale could be more specific | Accepted as non-blocking residual | Existing extractor surfaces do not expose a portfolio-manager list/tenure contract. This remains deferred to a row-shape contract gate |

## Accepted Decision

The next extractor-facing gate is:

`row-field correctness test extension gate for retained equity-like holdings subset`

That next gate may only use `docs/reviews/mvp-small-golden-set-retained-excerpt-fixture-pdf-only-20260609.json` and may only add tests for the retained equity-like holdings rows:

- `004393`: `top_stock_table_row`
- `004194`: `top_index_stock_table_row`
- `017641`: `top_equity_table_row`

It must not add production normalization, extractor fixes, PDF reads, `FundDocumentRepository` access, network access, fallback, live LLM, provider/default/runtime/budget/config changes, fixture projection or golden/readiness promotion.

## Deferred Residuals

| Residual | Required next gate |
|---|---|
| `manager` portfolio-manager identity and tenure | Portfolio-manager row-shape contract decision |
| `risk` retained risk-characteristic text | Risk row-shape contract decision |
| `006597` bond top holding | Holdings row-shape contract decision |
| `110020` target ETF holding | Holdings row-shape contract decision |
| Production PDF parser fidelity | Separately authorized parser/FDR/PDF evidence gate |

## Validation

- Branch checked: `feat/mvp-llm-incomplete-run-artifacts`
- Status checked: unrelated untracked workspace residue remains unstaged and unmodified by this gate.
- Review loop completed: DS and MiMo final targeted re-reviews report no blocking findings.
- Code/test validation not rerun because this gate is docs-only and no source/test/config files were modified.

## Final Judgment

Accepted locally.

The gate reduces the next extractor-facing step to a narrow same-source test extension for equity-like holdings only. It preserves fail-closed semantics for all still-undefined row shapes and keeps exact/numeric correctness blocked for `manager`, `risk`, bond holdings and target ETF holdings until their output contracts are reviewed and accepted.
