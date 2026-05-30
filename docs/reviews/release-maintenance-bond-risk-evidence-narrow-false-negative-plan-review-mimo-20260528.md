# Bond Risk Evidence Narrow False-Negative Plan Review (MiMo)

> Date: 2026-05-28
> Role: plan review worker MiMo
> Gate: `bond risk evidence narrow false-negative gate`
> Work unit: `bond risk evidence narrow false-negative`
> Review type: adversarial plan review — semantic correctness and implementability
> Status: complete

---

## Worker Self-Check

### Before Start

- Role confirmed: plan review worker only; not controller, not implementer.
- Truth sources read: `AGENTS.md`, `docs/design.md`, `docs/implementation-control.md`, plan artifact (`release-maintenance-bond-risk-evidence-narrow-false-negative-plan-20260528.md`), Slice 6 root-cause review (DS), Slice 6 investigation (GLM), aggregate deepreview (MiMo), current `bond_risk_evidence.py` source, current `test_bond_risk_evidence.py` tests, `extractors/models.py` type definitions.
- Branch: `codex/local-reconciliation`; no source modifications by this worker.

### Before Completion

- All focus areas checked: fund-own-rating boundary, rating distribution anchors, A/C/E/F aggregation, Decimal arithmetic, drawdown boundary, scope creep, validation commands, slice implementability, test coverage.

---

## Review Summary

**Verdict: PASS_WITH_CONDITIONAL_FIXES**

The plan is well-structured, correctly scoped, and preserves all hard constraints. The root-cause analysis from DS/GLM investigations is accurate and the slice decomposition is implementable. However, I found **7 findings** requiring concrete fixes before implementation should proceed. Two are P0 (could cause incorrect acceptance or semantic violation), five are P1 (precision/completeness gaps).

---

## Focus Area 1: fund-own-rating vs portfolio_credit_exposure Hard Boundary

### Check: Does the plan enforce the distinction?

**PASS.** The plan explicitly forbids `fund_rating`, `ratings`, `fund_own_rating`, `基金评级`, `本基金评级`, `评级为 AAA 的基金` in Contract Decisions section (lines 117-120). The metric wording `年报表格披露持有债券/证券的信用评级分布` correctly scopes to portfolio exposure.

### F1 [P0]: Plan does not specify how to handle tables with fund-level rating headers

**Severity**: P0 — could cause false positive acceptance of fund-own-rating evidence.

**Problem**: The plan's detection rules (lines 133-136) specify `table_keywords` containing `信用` and `评级`, and recognized row labels include `A-1`, `AAA`, etc. However, some annual reports contain tables with headers like `本基金评级` or `基金评级信息` that also have `信用`/`评级` in table text and `AAA`-family row labels. The plan's current detection rules would match such tables, violating the hard boundary.

**Fix**: Add explicit rejection rules:
- If table header text contains `本基金` or `基金评级` (without `持仓`/`持有`/`证券`), reject the table.
- The helper `_credit_rating_distribution_anchor_drafts` must verify the table is about **held bond/security ratings**, not fund ratings. A safe heuristic: table must be in §8 (portfolio) context, OR header must contain `持有`/`持仓`/`证券` combined with `信用评级`.

**Concrete plan amendment**: Add to "Detection rules" section:
> Candidate table must NOT contain `本基金评级` or `基金评级信息` in header text. If the table header contains `信用评级` without `持有`/`持仓`/`证券` qualifier, it must be located in §8 portfolio context to be accepted.

---

## Focus Area 2: Rating Distribution Evidence Strength and Anchors

### Check: Are anchors sufficient and metric_value meaningful?

**PARTIAL PASS.** The plan requires row-level anchors (line 140), `page_number`, `table_id`, `row_locator` (line 142), and `metric_value` summarizing table evidence (line 144). This is correct.

### F2 [P1]: Plan does not specify which table to prefer when multiple rating tables exist

**Severity**: P1 — could cause non-deterministic behavior.

**Problem**: GLM investigation found 4 rating distribution tables (Tables #59-#62, pages 53-54): two for short-term ratings and two for long-term ratings, across different instrument categories. The plan says "at least one valid rating distribution table" (line 148) but doesn't specify preference when multiple valid tables exist. Should the helper:
- Accept the first match? (current implicit behavior)
- Accept all matches and aggregate? (most informative)
- Prefer long-term over short-term? (more common analysis focus)

**Fix**: Specify in the plan:
> When multiple valid rating distribution tables are found, emit anchors for ALL matching tables. The `metric_value` should summarize the first (or most representative) table. Multiple table anchors increase evidence strength and do not require aggregation — each table is independent evidence of portfolio credit exposure.

### F3 [P1]: metric_value format is underspecified for rating distribution

**Severity**: P1 — could cause inconsistent output across implementations.

**Problem**: The plan says `metric_value` should summarize as `长期信用评级: AAA=..., AAA以下=..., 未评级=..., 合计=...` (line 144) but doesn't specify:
- Which columns to include (current period only? or both current and prior period?)
- How to handle short-term vs long-term ratings in the same metric_value
- Whether `合计` row is mandatory for acceptance

**Fix**: Add to plan:
> `metric_value` should include current-period values from the first matching table. Format: `{rating_header}: {row_label}={value}, ...`. Include `合计` row if present. Prior-period values are supplementary and may be omitted from `metric_value` but should appear in anchor `note`.

---

## Focus Area 3: A/C/E/F Aggregation, Class Breakdown, Decimal Arithmetic, Fail-Closed

### Check: Is the aggregation contract complete and fail-safe?

**PARTIAL PASS.** The plan is detailed on required rows, calculations, and fail-closed conditions. However, several implementation details need tightening.

### F4 [P0]: Plan specifies Decimal arithmetic but current codebase uses string parsing — gap in contract

**Severity**: P0 — could cause arithmetic precision failures in implementation.

**Problem**: The plan requires `Decimal` for share values (line 262) and arithmetic reconciliation with "small Decimal tolerance" (line 181). However, looking at the current `bond_risk_evidence.py`, all value handling is string-based (`_format_row_note`, `_normalize_cell`). The plan does not specify:
- How to parse comma-separated values like `27,623,952,157.07` into `Decimal`
- What the "small Decimal tolerance" should be (absolute? relative? how many decimal places?)
- How to handle Chinese negative notation (rare but possible)
- How dash `-` and `－` (full-width) map to `Decimal(0)`

**Fix**: Add explicit parsing contract to Slice 3:
> Share value parsing:
> - Strip commas and whitespace before `Decimal()` conversion
> - `-`, `－`, `—`, `--` all map to `Decimal(0)`
> - Tolerance: `abs(computed - stated) <= Decimal("0.01")` (one cent)
> - If `Decimal()` conversion raises `InvalidOperation`, fail closed as `ambiguous` with `na_reason="non_parseable_share_value"`
> - Use `decimal.Decimal` with default precision; do not set `getcontext().prec` explicitly

### F5 [P1]: All-class aggregation position-based column alignment is fragile

**Severity**: P1 — could cause silent misalignment in real data.

**Problem**: The plan says "Require value columns to align with all mapped classes A/C/E/F by position or recognizable class headers" (line 170). The GLM investigation found that Table #78 headers contain share class names (e.g., `国泰利享中短债债券A`) rather than fund codes. The plan relies on position-based mapping from §2 table to §10 table, but:
- What if §2 table order is A, C, E, F but §10 table order is A, E, C, F? (column mismatch)
- What if §10 table has an extra "合计" column that §2 doesn't have?

**Fix**: Add to Slice 2/3 contract:
> Column alignment must verify that the number of value columns in the §10 share-change table (excluding row label and total columns) equals the number of mapped share classes from §2. If counts differ, fail closed as `ambiguous` with `na_reason="share_class_column_count_mismatch"`. When §10 table headers contain share class names (not fund codes), match by class label position in §2 mapping rather than absolute column index.

### F6 [P1]: Plan does not specify aggregate arithmetic reconciliation edge case — net change ratio when beginning is dash

**Severity**: P1 — could cause division by zero or incorrect acceptance.

**Problem**: The plan says "if aggregate beginning is zero or missing, fail closed" (line 184). But for F share class, GLM found beginning is `-` (dash). After parsing dash as zero:
- F class beginning = `Decimal(0)`
- F class net change = subscription - redemption + split
- F class net change ratio = `net_change / Decimal(0)` → division by zero

The plan mentions "Do not silently ignore F share because it has beginning `-`" (line 270) but doesn't address the per-class division by zero.

**Fix**: Add to Slice 3 contract:
> Per-class net change ratio: if class beginning is zero, set class net change ratio to `None` and note `"class_beginning_zero"`. Do not fail closed for individual class zero-beginning; only fail closed if **aggregate** beginning is zero. Include per-class ratio as `None` in class breakdown rather than omitting the class.

---

## Focus Area 4: drawdown_stress Remains Weak

### Check: Does the plan correctly preserve the drawdown boundary?

**PASS.** The plan explicitly states "No implementation changes should upgrade `drawdown_stress`" (line 207), "Only disclosed max drawdown, volatility, direct stress metric, or a future reviewed NAV-derived metric contract can satisfy `drawdown_stress`" (line 218), and "This gate must not calculate drawdown from NAV" (line 219). The test `test_drawdown_control_text_alone_remains_weak_after_false_negative_fix` (line 336) confirms the boundary.

No findings in this area.

---

## Focus Area 5: No Hidden Schema/Score/Gate Scope Creep

### Check: Does the plan stay within allowed scope?

**PASS.** The plan's Scope section (lines 84-101) correctly limits changes to `bond_risk_evidence.py` and `test_bond_risk_evidence.py`. It explicitly says no changes to `models.py`, `extraction_snapshot.py`, `extraction_score.py`, `quality_gate.py`, or Service/UI/Host/Agent/dayu modules. The "Docs decision" (lines 98-101) correctly states no README or design.md update is expected.

No findings in this area.

---

## Focus Area 6: Validation Command Correctness

### Check: Are the validation commands correct and complete?

**PARTIAL PASS.**

### F7 [P1]: Validation commands do not include a targeted bond_risk_evidence import test

**Severity**: P1 — could miss import-time errors in the new helper.

**Problem**: The validation commands (lines 362-368) include `ruff check`, `pytest`, and the full extraction-snapshot → extraction-score → quality-gate pipeline. However, there is no quick smoke test that specifically imports and calls the new `_credit_rating_distribution_anchor_drafts` helper or the modified `_extract_redemption_share_pressure`. If the new helper has a syntax error or import issue, it would only be caught by the full pipeline run, which is slow.

**Fix**: Add a targeted validation command:
```bash
uv run python -c "from fund_agent.fund.extractors.bond_risk_evidence import extract_bond_risk_evidence; print('import OK')"
```
This catches syntax/import errors immediately before running the full pipeline.

---

## Focus Area 7: Slice Implementability and Test Coverage

### Check: Are slices small, independent, and code-generation-ready?

**PASS with notes.** The four slices are well-decomposed:
- Slice 1 (credit rating helper): self-contained, one new helper + modification to `_extract_credit_risk`
- Slice 2 (share mapping + table selection): modifies §2 parsing and table selection
- Slice 3 (aggregation + reconciliation): adds Decimal arithmetic and fail-closed logic
- Slice 4 (tests): all required tests specified

### Test Coverage Assessment

**Strengths:**
- Tests cover both positive cases (accepted evidence) and negative cases (weak/ambiguous remain)
- Tests explicitly check forbidden fund-own-rating wording
- Tests verify fail-closed on column mismatch and arithmetic mismatch
- Tests verify drawdown remains weak after fix

**Gaps (minor, not blocking):**
- No test for multiple rating distribution tables (F2 above)
- No test for Chinese full-width dash `－` parsing in Decimal (F4 above)
- No test for §10 table with extra "合计" column (F5 above)

---

## Findings Summary

| ID | Severity | Focus Area | Description | Fix Required |
|---|---|---|---|---|
| F1 | P0 | fund-own-rating boundary | Detection rules could match fund-level rating tables | Add explicit rejection for `本基金评级`/`基金评级信息` headers |
| F2 | P1 | rating distribution anchors | No preference when multiple rating tables exist | Emit anchors for all matching tables |
| F3 | P1 | rating distribution metric_value | metric_value format underspecified | Specify current-period format and 合计 requirement |
| F4 | P0 | Decimal arithmetic | Parsing contract gap for comma-separated values and dash | Add explicit parsing rules and tolerance |
| F5 | P1 | A/C/E/F column alignment | Position-based alignment fragile when column order differs | Verify column count and match by class label |
| F6 | P1 | net change ratio edge case | Per-class division by zero when beginning is dash | Allow per-class zero beginning, fail only on aggregate zero |
| F7 | P1 | validation commands | No targeted import smoke test | Add quick import validation command |

---

## Conclusion

The plan is sound and implementable. The two P0 findings (F1, F4) must be addressed before implementation begins — F1 prevents potential false-positive acceptance of fund-level ratings, and F4 prevents arithmetic failures in the Decimal-heavy Slice 3. The five P1 findings improve robustness but are not blocking.

**Recommended action**: Controller should accept this plan with the 7 findings as required amendments. Implementation worker should incorporate F1 and F4 fixes into Slice 1 and Slice 3 respectively before writing code, and address P1 findings during implementation or as explicit residuals.

---

## Review Signature

- Reviewer: MiMo (Gateflow plan review worker)
- Review type: adversarial plan review
- Artifact: `docs/reviews/release-maintenance-bond-risk-evidence-narrow-false-negative-plan-review-mimo-20260528.md`
- Verdict: **PASS_WITH_CONDITIONAL_FIXES** — 2 P0 findings require plan amendment before implementation; 5 P1 findings improve robustness.
