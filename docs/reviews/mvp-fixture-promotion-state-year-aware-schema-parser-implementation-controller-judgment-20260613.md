# Controller Judgment: Fixture Promotion State Year-aware Schema / Parser Implementation

Date: 2026-06-13

Gate: `Fixture Promotion State Year-aware Schema / Parser Implementation Gate`

Implementation evidence:

- `docs/reviews/mvp-fixture-promotion-state-year-aware-schema-parser-implementation-evidence-20260613.md`

Review inputs:

- `docs/reviews/mvp-fixture-promotion-state-year-aware-schema-parser-implementation-review-ds-20260613.md`
- `docs/reviews/mvp-fixture-promotion-state-year-aware-schema-parser-implementation-review-mimo-20260613.md`

Verdict: `ACCEPT_WITH_RESIDUALS_NOT_READY`

## 1. Controller Scope

This judgment accepts the implementation of the year-aware fixture promotion
schema/parser contract.

This judgment does not create or promote fixture content, does not edit
golden-answer content, does not run readiness/release commands, and does not
claim release/readiness.

Release/readiness remains `NOT_READY`.

## 2. Accepted Implementation Facts

| Fact | Disposition | Basis |
|---|---|---|
| Parser supports schema version `fund-agent.fixture-promotion-state.year-aware.v1`. | `ACCEPT` | Evidence §2; DS §1; MiMo §2.1 |
| Year-aware promotion identity is exact `(fund_code, report_year)`. | `ACCEPT` | `FixturePromotionStates.fund_year_states`; DS §1; MiMo §2.2 |
| `promotion_identity == "fund_year"` is required and wrong identity fails closed. | `ACCEPT` | DS §1; MiMo §2.3; wrong-identity test |
| Duplicate `(fund_code, report_year)` entries fail closed. | `ACCEPT` | DS §1; MiMo §2.4; duplicate test |
| Unknown top-level and year-aware entry fields fail closed. | `ACCEPT` | DS §1; MiMo §2.5; unknown-field test |
| Legacy fund-code-only manifests are diagnostic-only and cannot satisfy year-specific proof. | `ACCEPT` | DS §1/§3; MiMo §2.6; legacy test |
| Exact-year state/blocker mapping matches the accepted plan. | `ACCEPT` | DS state/blocker table; MiMo §2.7 |
| No `DEFAULT_REPORT_YEAR` mapping is used to promote legacy fixture state. | `ACCEPT` | DS §1; MiMo §2.8 |
| Strict golden coverage behavior was not changed. | `ACCEPT_CONFIRMED` | DS §2; MiMo §3.1 |
| README updates describe current implementation only. | `ACCEPT` | DS §4; MiMo §5 |

## 3. Review Finding Disposition

| Finding | Source | Controller disposition | Follow-up |
|---|---|---|---|
| DS review verdict is PASS. | DS | `ACCEPT` | No fix required. |
| MiMo review verdict is PASS. | MiMo | `ACCEPT` | No fix required. |
| Legacy `entries` format still does not reject unknown entry fields. | DS F1 | `ACCEPT_AS_NONBLOCKING_LEGACY_RESIDUAL` | Legacy formats are diagnostic-only and pre-existing; strict unknown-field validation is required and implemented only for year-aware schema. Revisit only if a future gate expands legacy format semantics. |
| `_run_single_artifact()` default `fixture_promotion_state_path=None` preserves existing callers. | DS F2 | `ACCEPT_AS_COMPATIBILITY_CONFIRMATION` | No action. |
| `FixturePromotionStates` is internal; exposing it later requires a separate contract gate. | MiMo residual | `ACCEPT_AS_FUTURE_CONTRACT_RESIDUAL` | No action in this gate. |

## 4. Validation

Accepted validation results:

```text
uv run pytest tests/fund/test_golden_readiness_preflight.py -q
22 passed in 0.90s

uv run ruff check fund_agent/fund/golden_readiness_preflight.py tests/fund/test_golden_readiness_preflight.py
All checks passed!

git diff --check
<no output>
```

The test count is consistent with the implementation: 16 existing tests plus
6 new value-level tests.

## 5. Accepted / Rejected / Deferred

| Item | Disposition | Reason |
|---|---|---|
| Year-aware fixture promotion parser/schema implementation. | `ACCEPT` | Meets accepted contract and both reviews passed. |
| Value-level tests for matching year, wrong year, legacy, duplicate, unknown field and wrong identity. | `ACCEPT` | Required scenarios covered. |
| Fund/tests README sync. | `ACCEPT` | Triggered by source/test changes and current-state accurate. |
| Strict golden coverage implementation. | `REJECT_AS_UNCHANGED` | Not needed and not changed. |
| Golden-answer content edits. | `REJECT` | Out of scope and not performed. |
| Fixture content creation or promotion action. | `REJECT` | Out of scope and not performed. |
| Readiness/release/PR claim. | `DEFER` | Release/readiness remains `NOT_READY`; external state requires separate authorization. |

## 6. Residuals

| Residual | Owner | Destination |
|---|---|---|
| No fixture promotion content was created or promoted. | Golden/readiness owner | Future fixture promotion/content gate only if authorized |
| No readiness/release command was run. | Release owner | Future readiness rollup |
| Legacy `entries` format remains permissive for unknown fields but diagnostic-only. | Future schema owner | Only revisit if legacy format gets new semantics |
| `FixturePromotionStates` is internal. | Fund API owner | Future public contract gate if exposed |

## 7. Accepted Checkpoint

This implementation gate is accepted as a local checkpoint once these files are
committed together:

- `fund_agent/fund/golden_readiness_preflight.py`
- `tests/fund/test_golden_readiness_preflight.py`
- `fund_agent/fund/README.md`
- `tests/README.md`
- `docs/reviews/mvp-fixture-promotion-state-year-aware-schema-parser-implementation-evidence-20260613.md`
- `docs/reviews/mvp-fixture-promotion-state-year-aware-schema-parser-implementation-review-ds-20260613.md`
- `docs/reviews/mvp-fixture-promotion-state-year-aware-schema-parser-implementation-review-mimo-20260613.md`
- `docs/reviews/mvp-fixture-promotion-state-year-aware-schema-parser-implementation-controller-judgment-20260613.md`

Expected checkpoint message:

```text
gateflow: accept fixture promotion year-aware parser implementation
```

## 8. Next Entry

Recommended next mainline entry:

```text
Fixture Promotion Year-aware Parser Downstream Evidence Gate
```

Purpose:

- collect non-live evidence that downstream preflight/readiness rows can consume
  exact year-aware fixture promotion state;
- confirm legacy fund-code-only state no longer satisfies `004393 / 2025`;
- preserve `NOT_READY` unless a later readiness rollup gate explicitly accepts
  enough evidence.

Do not enter fixture promotion content creation, readiness/release, live,
provider, LLM, PR, push or merge from this judgment.

## 9. Boundary Confirmation

This judgment did not perform or authorize:

- golden-answer, fixture or promotion-state content edits;
- fixture promotion;
- live EID, network, PDF, FDR, provider, LLM, analyze, checklist, readiness,
  release or PR commands;
- cleanup, deletion, archive, push, merge or external-state actions.
