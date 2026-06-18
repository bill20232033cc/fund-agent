# Docling Reference Bundle Producer Row-hierarchy and Benchmark Semantic-label Plan Re-review - AgentMiMo - 2026-06-17

Gate: `Docling Reference Bundle Producer Row-hierarchy and Benchmark Semantic-label Planning Gate`
Role: AgentMiMo plan re-review worker only.
Verdict: `PASS`
Release/readiness: `NOT_READY`

## Reviewed Artifacts

- `docs/reviews/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-plan-20260617.md`
- `docs/reviews/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-plan-fix2-evidence-20260617.md`

## Prior MiMo Review

- `docs/reviews/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-plan-review-mimo-20260617.md`

## Prior Finding Disposition

### F1 (Medium) - `其中：普通股` test/rule mismatch - FIXED

The plan has been corrected in all relevant locations:

1. **Explicit positive stock marker** (line 197): Now states "current row label must contain `其中` plus `股票`" — no `普通股`.
2. **Accepted examples** (lines 199-201): Only `其中：股票` and `其中:股票`.
3. **Not-accepted examples** (lines 206-212): Explicitly lists `其中：普通股` as not accepted for positive `stock_investment_amount` closure, with rationale: "Current `FIELD_RULES["stock_investment_amount"].required_row_label_any` does not include `普通股`, so this plan does not authorize a stock FIELD_RULES expansion for it."
4. **Test 1** (line 510): Changed from `其中：普通股` to `其中：股票`.
5. **Test 2** (line 519): Changed from `其中：普通股` to `其中：股票`.
6. **New negative test 6** (lines 541-544): `test_raw_legacy_stock_child_plain_common_share_label_remains_residual_under_current_rules` — confirms `其中：普通股` under a `权益投资` parent remains residual for `stock_investment_amount`.
7. **Step 5** (lines 490-498): Explicitly states "No FIELD_RULES expansion is authorized for this gate. In particular, do not add `其中：普通股`, `其中:普通股`, or `普通股` to `FIELD_RULES["stock_investment_amount"].required_row_label_any`."
8. **Expected behavior table** (line 627): "`其中：普通股` remains residual under current stock row-label rules".
9. **Stop Conditions** (line 691): "child marker lacks explicit `其中` plus `股票` for positive `stock_investment_amount` closure".

**Verification:** No positive `stock_investment_amount` closure test or example depends on `其中：普通股`. No FIELD_RULES expansion is authorized. Positive stock closure is aligned to current FIELD_RULES (`其中：股票` / `其中:股票` / `股票`).

### F2 (Low) - Top-level asset row boundary list - CLARIFIED (non-blocking)

The plan retains the conservative six-row boundary list. The ambiguity-fail-closed rules (lines 261-274) already handle the case: "top-level asset rows make parent scope ambiguous" keeps role `unknown`. The plan does not expand the list, which is conservative and correct for this gate. If real documents produce unexpected scope leakage, the fail-closed fallback prevents false closure. This is acceptable as a residual.

### F3 (Low) - `_enrich_share_period_contexts()` ambiguity - CLARIFIED (non-blocking)

Step 3 (lines 466-478) now states: "Do not introduce `_enrich_share_period_contexts()` unless the implementation worker explicitly chooses a small local refactor. If introduced, it must preserve the existing share/period behavior exactly and stay private to this module." This resolves the ambiguity — the default is to keep the existing inline logic.

### F4 (Info) - S5-F032 closure depends on actual table structure - UNCHANGED

No action needed. The plan uses hedging language ("may close") which is correct.

## New Findings

No new blocking findings identified.

### NF1 - Info - Test count increased from 17 to 20

The fix added 3 new tests: test 6 (`其中：普通股` negative), test 13 (heading_path benchmark positive), and test 17 (context/objective heading/benchmark conflict negative). This improves coverage. Not blocking.

### NF2 - Info - `_row_primary_label()` definition is now precise

The plan now includes exact code for `_row_primary_label()` (lines 415-424) and specifies that all parent/child/top-level predicates consume this primary label. The rationale (last element is most specific) is sound. Not blocking.

## Validation

| Check | Result |
|---|---|
| F1: no positive stock test depends on `其中：普通股` | confirmed — tests 1-3 use `其中：股票`; negative test 6 covers `其中：普通股` |
| F1: no FIELD_RULES expansion authorized | confirmed — Step 5 explicitly prohibits expansion |
| F1: positive stock closure aligned to current FIELD_RULES | confirmed — `其中：股票` / `其中:股票` / `股票` only |
| F2: conservative boundary retained, fail-closed | confirmed |
| F3: `_enrich_share_period_contexts()` default clarified | confirmed — optional refactor only |
| No new blocking issue | confirmed |
| Test count adequate | confirmed — 20 tests (10 hierarchy + 5 benchmark + 5 regression) |
| git diff --check on plan + fix2 evidence | passed, no output |
| NOT_READY preserved | confirmed |
| source_truth_status=not_proven preserved | confirmed |
| No source truth/baseline/parser/readiness claims | confirmed |

## Boundary Check

| Boundary | Status |
|---|---|
| `NOT_READY` preserved | confirmed |
| `source_truth_status=not_proven` preserved | confirmed |
| No source truth acceptance | confirmed |
| No baseline promotion | confirmed |
| No parser replacement | confirmed |
| No full correctness/readiness claim | confirmed |
| No direct PDF/cache/source-helper access | confirmed |
| No live/network/provider/LLM commands | confirmed |
| No FIELD_RULES expansion | confirmed |

## Final Verdict

**PASS**

All prior findings are resolved. F1 (medium) is fixed: the plan no longer uses `其中：普通股` for positive stock closure tests, explicitly prohibits FIELD_RULES expansion, and adds a negative test confirming `其中：普通股` remains residual. F2/F3 are clarified as non-blocking residuals. No new blocking issues. Boundaries are preserved.

Blocking findings count: 0

## Self-check

pass - verified F1 fix against all plan locations (marker definition, examples, tests 1-3, Step 5, expected behavior, stop conditions), confirmed no FIELD_RULES expansion authorized, confirmed F2/F3 are non-blocking clarifications, and verified all boundary conditions remain intact.
