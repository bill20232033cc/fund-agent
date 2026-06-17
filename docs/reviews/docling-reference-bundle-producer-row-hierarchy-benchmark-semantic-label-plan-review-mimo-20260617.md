# Docling Reference Bundle Producer Row-hierarchy and Benchmark Semantic-label Plan Review - AgentMiMo - 2026-06-17

Gate: `Docling Reference Bundle Producer Row-hierarchy and Benchmark Semantic-label Planning Gate`
Role: AgentMiMo plan review worker only.
Verdict: `PASS_WITH_FINDINGS`
Release/readiness: `NOT_READY`

## Reviewed Artifact

- `docs/reviews/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-plan-20260617.md`

## Accepted Inputs Cross-checked

- `docs/reviews/docling-reference-bundle-enrichment-residual-closure-no-live-reevidence-controller-judgment-20260617.md`
- `docs/reviews/docling-reference-bundle-enrichment-residual-closure-no-live-reevidence-review-ds-20260617.md`
- `docs/reviews/docling-reference-bundle-enrichment-residual-closure-no-live-reevidence-review-mimo-20260617.md`
- `reports/docling-reference-bundle-enrichment-residual-closure/20260617/residual_closure_matrix.json`
- `fund_agent/fund/documents/candidates/source_truth_residual_closure.py`
- `tests/fund/documents/test_docling_source_truth_residual_closure.py`

## Findings

### F1 - Medium - Test case 1 (`其中：普通股`) does not match current `stock_investment_amount` FIELD_RULES `required_row_label_any`

**Location:** Plan "Row Hierarchy Positive Tests" test 1 and test 2.

**Issue:** The plan uses `其中：普通股` as a stock child marker in test 1 and test 2. The explicit child marker definition (lines 189-196) lists `其中：普通股` as accepted. However, the current `FIELD_RULES["stock_investment_amount"]` has `required_row_label_any=("其中：股票", "其中:股票", "股票")`. The label `其中：普通股` does not contain the substring `股票`, so `_contains_any()` would not match it against any of the three required labels. The `_has_share_class_context` pattern is unrelated here — the stock rule uses `required_row_label_any`, not share-class context.

**Evidence:** `source_truth_residual_closure.py:655-656` defines `required_row_label_any=("其中：股票", "其中:股票", "股票")`. The `_contains_any()` helper (line 1665) normalizes and checks substring containment. After normalization, `其中：普通股` does not contain `其中：股票`, `其中:股票`, or `股票`.

**Impact:** If the implementation derives `row_hierarchy_role="child"` for a `其中：普通股` row, the row label still fails `required_row_label_any`, so the row remains residual. The plan's "Expected after implementation" table claims S6-F050 "may close", but with `其中：普通股` as the child label, it would not close under current rules.

**Risk:** The plan's positive test 1 expects `disambiguated_source_body_match` for stock with `其中：普通股`, which would fail against current FIELD_RULES. This could lead the implementation worker to either (a) incorrectly broaden the stock rule, or (b) write a test that cannot pass without rule changes the plan says should not happen.

**Suggested fix:** Either (a) use `其中：股票` instead of `其中：普通股` in tests 1-3, or (b) add `其中：普通股` / `其中:普通股` / `普通股` to `FIELD_RULES["stock_investment_amount"].required_row_label_any` if that is the intended scope. The plan's Step 5 says "Do not change FIELD_RULES unless required by tests" — this is exactly such a case. The child marker definition should align with the rule's accepted labels.

### F2 - Low - Parent scope boundary "top-level asset row" list may be incomplete for real documents

**Location:** Plan "Top-level Row Boundary" section, `_is_explicit_top_level_asset_row()`.

**Issue:** The plan lists six top-level asset labels that close parent scope: `权益投资`, `基金投资`, `固定收益投资`, `贵金属投资`, `金融衍生品投资`, `买入返售金融资产`. Real annual report portfolio composition tables may include additional top-level rows such as `银行存款和结算备付金`, `其他资产`, `应收利息`, `应收股利`, etc. If such a row appears between `权益投资` and `其中：股票`, the plan's boundary check would not detect it, potentially allowing a child to incorrectly adopt a distant parent.

**Evidence:** The plan does not claim this list is exhaustive, but the `_is_explicit_top_level_asset_row()` function signature implies a closed set. The ambiguity-fail-closed rule says "top-level asset rows make parent scope ambiguous" should keep role `unknown`, but the implementation must enumerate those rows.

**Impact:** If a real document has `权益投资` followed by `银行存款和结算备付金` then `其中：股票`, the child might incorrectly attach to `权益投资` because the boundary function doesn't recognize `银行存款和结算备付金` as a scope closer. The fail-closed fallback (keep `unknown`) would still prevent false closure, but only if the boundary function is triggered.

**Suggested fix:** Consider either (a) expanding the list to include common portfolio top-level rows, or (b) defining the boundary function as a "known top-level" check plus a fallback: any row that is NOT an explicit child marker (`其中` + asset name) and NOT the current parent resets scope. This is more conservative but safer.

### F3 - Low - `_enrich_share_period_contexts()` reference is ambiguous

**Location:** Plan "Step 3 - Wire helpers into v1 enrichment", line 428.

**Issue:** The plan shows `context_enriched = _enrich_share_period_contexts(hierarchy_enriched)` in the proposed call chain, but immediately follows with "If implementation does not introduce `_enrich_share_period_contexts()`, keep the existing loop." The current `_enrich_reference_bundle_contexts()` has the share/period derivation inline (lines 1922-1934), not in a separate function. The plan does not specify whether extracting this into `_enrich_share_period_contexts()` is required or optional.

**Impact:** Minor ambiguity for the implementation worker. Either approach (extract or inline) would produce the same result, but the plan should be definitive to avoid implementation drift.

**Suggested fix:** State explicitly: "Extracting `_enrich_share_period_contexts()` is optional. The implementation may keep the existing inline loop and insert `_enrich_row_hierarchy_contexts()` before it and `_enrich_text_span_semantic_contexts()` after it."

### F4 - Info - S5-F032 (equity) expected closure depends on S5's actual table structure

**Location:** Plan "Expected Row-level Behavior After Implementation", S5-F032 row.

**Issue:** The plan says S5-F032 "may close" with proof: `portfolio_asset_composition_table`; explicit aggregate `权益投资`; explicit stock child under it proves aggregate role. However, S5 is fund 017641 (摩根标普500 QDII index fund). The matrix shows S5-F032's value is `1818456375.25`. Whether S5's portfolio table actually has an explicit `权益投资` row followed by an explicit `其中：股票` child is not verified in this review — it depends on the actual ParsedTable structure from S5's repository load.

**Impact:** The plan correctly uses "may close" rather than "should close", so this is not a false promise. But the implementation worker should verify against the actual bundle data, not assume closure.

**Severity:** Info — the plan's hedging language is correct.

## Validation

| Check | Result |
|---|---|
| Plan references correct accepted inputs | confirmed — controller judgment, DS review, MiMo review, matrix all cited |
| Plan residual rows match matrix residual rows | confirmed — S5-F032, S6-F041, S6-F049, S6-F050 |
| Plan residual reasons match matrix/accepted inputs | confirmed — hierarchy not proven (3 rows), benchmark label not proven (1 row) |
| Plan preserves NOT_READY boundary | confirmed — "First-principles Boundary" section, no source truth/baseline/readiness claims |
| Plan specifies exact affected files | confirmed — 2 implementation files + 1 evidence artifact |
| Plan specifies exact function signatures | confirmed — 8 helper functions with type annotations |
| Plan specifies test count and coverage | confirmed — 17 test cases (9 hierarchy + 4 benchmark + 4 regression) |
| Plan does not redesign FIELD_RULES | confirmed — Step 5 says keep existing rules unless tests require |
| Plan avoids value-equality proof | confirmed — "must not use: value equality alone" |
| Plan avoids neighbor-label proof | confirmed — "must not use: bounded neighbor labels as positive proof" |
| Plan rejects investment-objective-mentioning-benchmark | confirmed — explicit rule with example |
| Plan preserves v2 non-overwrite guard | confirmed — Step 4 |
| git diff --check on plan artifact | passed, no output |

## Boundary Check

| Boundary | Status |
|---|---|
| `NOT_READY` preserved | confirmed |
| `source_truth_status=not_proven` preserved | confirmed — plan says "All rows retain `source_truth_status=not_proven`" |
| No source truth acceptance | confirmed |
| No baseline promotion | confirmed |
| No parser replacement | confirmed |
| No full correctness/readiness claim | confirmed — "do not force 17/17 or 4/4 closure" |
| No direct PDF/cache/source-helper access | confirmed — "The accepted helper remains pure" |
| No live/network/provider/LLM commands | confirmed |

## Final Verdict

**PASS_WITH_FINDINGS**

The plan is substantially code-generation-ready with precise function signatures, explicit evidence rules, comprehensive test cases, and correct boundary preservation. One medium-severity finding (F1) identifies a concrete mismatch between the plan's test case child marker (`其中：普通股`) and the current `FIELD_RULES["stock_investment_amount"].required_row_label_any` — this must be resolved before implementation to avoid test failures or unintended rule broadening. Two low-severity findings (F2, F3) are implementation ambiguities that can be resolved during implementation without blocking. One info finding (F4) notes a verification dependency on actual bundle data.

Blocking findings count: 1 (F1 — test/rule mismatch must be resolved)

## Self-check

pass — reviewed plan against accepted inputs and current source code, verified function signatures and FIELD_RULES, checked boundary preservation, identified concrete test/rule mismatch in F1, and confirmed all other plan claims are consistent with accepted evidence and code.
