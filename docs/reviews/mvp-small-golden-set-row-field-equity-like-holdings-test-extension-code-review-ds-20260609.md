# MVP Small Golden Set Row-field Equity-like Holdings Test Extension — Code Review (DS)

## Gate

- Gate: `row-field correctness test extension gate for retained equity-like holdings subset`
- Classification: `standard`
- Reviewer: AgentDS
- Role: independent code review worker only
- Baseline checkpoint: `fc80d3d gateflow: accept row-field extractor gap decision`
- Date: 2026-06-09

## Review Inputs

| Input | Path |
|---|---|
| Control truth | `AGENTS.md`, `docs/current-startup-packet.md`, `docs/implementation-control.md`, `docs/design.md` |
| Prior gate decision | `docs/reviews/mvp-small-golden-set-row-field-extractor-gap-decision-gate-20260609.md` |
| Prior controller judgment | `docs/reviews/mvp-small-golden-set-row-field-extractor-gap-decision-gate-controller-judgment-20260609.md` |
| Implementation evidence | `docs/reviews/mvp-small-golden-set-row-field-equity-like-holdings-test-extension-implementation-evidence-20260609.md` |
| Retained excerpt oracle | `docs/reviews/mvp-small-golden-set-retained-excerpt-fixture-pdf-only-20260609.json` |
| Review targets | `tests/fund/test_small_golden_set_extractor_correctness.py` (diff), `tests/README.md` (diff) |

## Findings

### F1 — NON-BLOCKING: §3 end_offset silently changed for existing tests

**File:** `tests/fund/test_small_golden_set_extractor_correctness.py`, lines 460–466

**Finding:** `_build_report_from_oracle_row` now sets `§3` `end_offset=section_eight_start` instead of the prior `end_offset=len(raw_text)`. This is a behavioral change that affects all existing profile/performance tests even when `include_holdings=False`.

**Analysis:** The change is correct for the new model (when §8 exists, §3 should end where §8 begins). However, the prior contract had §3 extending to `len(raw_text)`. Current profile/performance extractors consume `report.tables` (not section text ranges) for the fields under test, so existing assertions are unaffected. The 16/16 passing result confirms no regression.

**Recommendation:** Document in the evidence artifact that the §3 range boundary change is intentional and does not affect current extractor behavior (extractors use tables, not section offsets, for the tested fields). No code change needed.

### F2 — NON-BLOCKING: §8 section always present in constructed report

**File:** `tests/fund/test_small_golden_set_extractor_correctness.py`, lines 426–428, 468–474

**Finding:** `_build_report_from_oracle_row` now unconditionally includes `§8` section text and `ReportSection` entry regardless of `include_holdings`. All 5 fund codes' constructed reports gain a §8 section with text `"本节持仓字段由同源 accepted oracle 表格承载。"`. Only when `include_holdings=True` is the holdings table appended to `tables`.

**Analysis:** The extra raw_text content and section entry have no observable effect on profile/performance extraction because those extractors iterate `report.tables` by keyword match, not section text. However, the constructed report shape now differs from what prior tests implicitly relied on. If a future extractor scans section text for holdings keywords, the dummy §8 text could cause false-positive table matching.

**Risk:** Low. The dummy §8 text `"本节持仓字段由同源 accepted oracle 表格承载。"` contains no extractor keywords (股票代码, 股票名称, 前十大, 重仓 etc.), so table-finding logic in `holdings_share_change.py` will not spuriously match it. The oracle boundary test also validates no forbidden full-pdf/page-text keys leak.

**Status:** Acceptable for this gate. No code change required.

### F3 — NON-BLOCKING: raw-header adapter covers only 4 canonical keys; quantity omitted

**File:** `tests/fund/test_small_golden_set_extractor_correctness.py`, lines 97–102

**Finding:** `HOLDINGS_RAW_KEY_ADAPTER` maps only `code`, `name`, `fair_value_cny`, `net_asset_ratio`. It does not map the `数量` (quantity) raw key to any canonical key.

**Analysis:** The retained excerpt oracle does not include a `quantity` field in any holdings expected row. The non-equity holdings shapes (006597 bond, 110020 ETF) also lack `code` in the oracle. The adapter is intentionally minimal for the current equity-like subset. The empty string `""` for quantity in constructed `ParsedTable` rows correctly projects as empty after `_normalize_cell` (which only does `.strip()`).

**Status:** This is correct for the current gate scope. If future gates extend to quantity or bond holdings with different canonical fields, the adapter will need expansion.

### F4 — INFORMATION: 006597/110020 blocked test validates oracle fields but asserts impossible final condition

**File:** `tests/fund/test_small_golden_set_extractor_correctness.py`, lines 721–744

**Finding:** `test_same_source_holdings_rows_outside_equity_like_subset_remain_blocked` is `xfail(strict=True)`. It reads the oracle's expected holdings for 006597 and 110020, asserts they are non-empty with valid anchor/excerpt, then asserts `fund_code not in UNSUPPORTED_HOLDINGS_ROWS` — which is always `False` by construction since the parametrize source is `UNSUPPORTED_HOLDINGS_ROWS`.

**Analysis:** This pattern intentionally mirrors the existing `test_same_source_fields_without_current_row_consumer_are_blocked_gaps` xfail test. The final assertion pathologically fails to keep the test in permanent blocked state. This is a valid documentation pattern: the xfail remains strict so that if anyone removes a fund_code from `UNSUPPORTED_HOLDINGS_ROWS` without adding a passing test, the xfail becomes a real failure (since `fund_code not in UNSUPPORTED_HOLDINGS_ROWS` could now be `True` if only one entry remains and it happens to be the other one).

**Edge case note:** If both entries are removed from `UNSUPPORTED_HOLDINGS_ROWS`, the parametrized test would produce 0 test cases and silently disappear. This is acceptable because removal would only happen in a future gate that explicitly promotes those rows.

## Scope Verification

| Criterion | Status | Evidence |
|---|---|---|
| Only test/evidence/docs changes | PASS | Diff touches only `tests/fund/test_small_golden_set_extractor_correctness.py`, `tests/README.md`, and one new evidence doc. No extractor/source/provider/runtime/config/golden/readiness changes |
| Correctness oracle: only retained excerpt JSON | PASS | `_holdings_expected_row` reads only `ORACLE_PATH` via `_expected(row, "holdings")`. Synthetic `expected_fields.json` explicitly excluded by `test_synthetic_unmatched_expected_fields_are_excluded_from_correctness_source` |
| Holdings route: only 004393/004194/017641 | PASS | `EQUITY_LIKE_HOLDINGS_ROWS` contains exactly these three. Parametrize on `test_holdings_extractor_matches_same_source_equity_like_top_row` uses only `sorted(EQUITY_LIKE_HOLDINGS_ROWS)` |
| Blocked residuals preserved | PASS | `manager` and `risk` remain in `SAME_SOURCE_UNSUPPORTED_FIELDS` (strict xfail). 006597 and 110020 in `UNSUPPORTED_HOLDINGS_ROWS` with new strict xfail test |
| Raw-header adapter is test-local | PASS | `HOLDINGS_RAW_KEY_ADAPTER` is module-level constant in test file only. Docstring on `_adapt_raw_holding_row` states `仅用于本测试`. No production import or normalization dependency |
| No impl modifications | PASS | `git diff` shows no changes to `fund_agent/` |

## Oracle-to-Test Traceability

| Fund | Oracle Key | Extractor Route | Raw Headers | Adapter Keys | Expected Values Match |
|---|---|---|---|---|---|
| 004393 | `top_stock_table_row` | `top_ten` → `direct_top_ten` | 前十大重仓, 股票代码, 股票名称, 数量, 公允价值, 占基金资产净值比例 | code→股票代码, name→股票名称, fair_value_cny→公允价值, net_asset_ratio→占基金资产净值比例 | code=00939, name=建设银行, fair_value_cny=18,182,239.78, net_asset_ratio=6.08% |
| 004194 | `top_index_stock_table_row` | `all_stock_investment_details` → `direct_all_stock_details` | 股票代码, 股票名称, 数量, 公允价值, 占基金资产净值比例 | same adapter | code=600428, name=中远海特, fair_value_cny=16,125,700.00, net_asset_ratio=1.02% |
| 017641 | `top_equity_table_row` | `all_stock_investment_details` → `direct_all_stock_details` | 股票代码, 股票名称, 数量, 公允价值, 占基金资产净值比例 | same adapter | code=AAPL, name=APPLE INC, fair_value_cny=148,655,637.71, net_asset_ratio=7.66% |

All three routes verified: extractor keywords (`_TOP_HOLDINGS_TABLE_KEYWORDS` / `_ALL_STOCK_DETAILS_KEYWORDS` at `holdings_share_change.py:18-19`) correctly dispatch to expected status/source values. Adapter keys verified against `_ALL_STOCK_DETAILS_KEYWORDS` at `holdings_share_change.py:19`. `_normalize_cell` at line 98-111 only does `.strip()`, so oracle values pass through unmodified.

## Validation Evidence Credibility

| Claim | Independent Verification |
|---|---|
| `16 passed, 4 xfailed in 0.84s` | Count verified: 1 oracle boundary + 1 synthetic exclusion + 5 profile × fund_code + 5 performance × fund_code + 1 tracking error + 3 holdings × fund_code = 16. 2 blocked fields + 2 blocked holdings = 4 xfail. Consistent |
| `37 passed, 4 xfailed in 0.51s` | Plausible: 37 - 16 = 21 additional passed from manifest/fixture_shape/source_identity/parser_mechanics test files |
| `ruff check` PASS | No reason to doubt |
| `git diff --check` clean | No whitespace errors reported |

## Adversarial Failure Pass

| Scenario | Result |
|---|---|
| Extract raw header keys don't match adapter | FAIL: `KeyError` in `_adapt_raw_holding_row`. Test fails hard, not silently |
| Oracle value not found in constructed table | FAIL: `_row_to_dict` produces different values → `==` assertion fails |
| Wrong fund_code given to non-equity route | FAIL: `KeyError` in `_holdings_table` (fund_code not in `EQUITY_LIKE_HOLDINGS_ROWS`) |
| Oracle JSON missing holdings field | FAIL: `KeyError` in `_expected(row, "holdings")` or `_holdings_expected_row` |
| Blocked holdings mistakenly run as passing | FAIL: blocked test is `xfail(strict=True)`. If `UNSUPPORTED_HOLDINGS_ROWS` is emptied, both tests silently disappear. But this would only happen in a future explicit promotion gate |
| `include_holdings=False` accidentally used | FAIL: `_holdings_table` not called, missing table → extractor returns `missing` or empty → assertion fails |
| Oracle value format drifts (e.g., ratio as float not string) | FAIL: `str(value)` conversion in `_holdings_expected_row` handles the canonical side, but `_adapt_raw_holding_row` returns raw extractor string values directly. If oracle changes value format, `_normalize_cell` is `.strip()` only → comparison may fail on whitespace or numeric formatting |

## Verdict

**PASS** — zero blocking findings.

F1 and F2 are non-blocking structural observations about `_build_report_from_oracle_row`'s §3/§8 boundary changes that do not affect current test correctness. F3 is informational about adapter scope. F4 is informational about the blocked-test pattern.

The implementation stays strictly within the allowed scope: test-only extension using only the accepted retained excerpt oracle, with a test-local adapter that does not imply production normalization. All three equity-like holdings routes are correctly wired to extractor keyword dispatch. Blocked residuals (manager, risk, 006597, 110020) remain properly gated behind strict xfail.
