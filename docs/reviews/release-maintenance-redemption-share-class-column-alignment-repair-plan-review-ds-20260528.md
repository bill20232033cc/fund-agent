# Redemption Share Class Column Alignment Repair Plan — DS Review

> Date: 2026-05-28
> Reviewer: DS (plan review worker)
> Gate: `redemption share class column alignment repair gate`
> Conclusion: **PASS_WITH_FINDINGS**

## Review Scope

This is a strict plan review. No code modification, no gateflow, no implementation.

Reviewed artifacts:
- `docs/reviews/release-maintenance-redemption-share-class-column-alignment-repair-plan-20260528.md` (the plan)
- `docs/reviews/release-maintenance-bond-risk-evidence-narrow-false-negative-validation-failure-controller-judgment-20260528.md` (controller stop)
- `AGENTS.md` (rules)
- Current dirty diff: `fund_agent/fund/extractors/bond_risk_evidence.py` and `tests/fund/extractors/test_bond_risk_evidence.py`
- Full source: `bond_risk_evidence.py` (2254 lines), `test_bond_risk_evidence.py` (1330 lines)

## Summary Assessment

The plan correctly identifies the root cause (label-based false negative in `_align_share_change_columns` for unlabeled §10 headers), proposes a conservative fail-closed positional alignment with layered guardrails, and respects all boundary constraints. The six-slice structure is logical and each slice has clear acceptance criteria.

However, the §2 ending cross-check (Slice 4) has a material implementation risk: `ParsedTable` carries no `section_id`, so the cross-check must scan all tables and could inadvertently compare §10 ending shares against §10 itself (circular proof). The plan partially mitigates this with a stop-if-not-found instruction, but lacks explicit table-disambiguation logic. Three other findings are high-severity and should be addressed before implementation begins.

## Findings

### F1 [CRITICAL] §2 Ending Cross-Check Circularity Risk — Table Scoping Missing

**What**: The plan proposes searching all parsed tables for rows like `报告期末基金份额总额` / `期末基金份额总额` / `下属分级基金的份额总额` to cross-check §10 ending shares. But `ParsedTable` (models.py:475) has no `section_id` field — only `page_number`, `table_index`, `headers`, `rows`. Without section-aware filtering, the cross-check helper will scan ALL tables including §10 itself.

**Why it matters**: The row text `期末基金份额总额` appears in §10 rows (the plan's own real-table evidence shows row 4: `本报告期期末基金份额总额`). If the cross-check picks up §10 rows, it compares §10 ending against §10 ending — a vacuous proof that would silently pass and create false confidence. This would defeat the entire purpose of the cross-check as an independent verification.

**Evidence**: The plan itself lists `期末基金份额总额` as a row text candidate (Slice 4 line 3). The real §10 table rows include `本报告期期末基金份额总额`. The `_first_row_anchor_draft` / `_row_anchor_draft` existing pattern scans `report.tables` (all tables) without section filtering.

**Fix required**:
1. Remove `期末基金份额总额` from the candidate row texts for §2 cross-check — it's the §10 wording.
2. Require the cross-check table to be **provably different** from the §10 table, by at minimum `(page_number, table_index) != §10_table`.
3. Prefer §2-specific wording: `报告期末基金份额总额` (with `报告` prefix), `下属分级基金的份额总额`, or `基金份额总额` in a table whose rows also contain `基金简称` / `交易代码` (linking it to §2 profile semantics).
4. Add an explicit assertion in the plan: the implementation must log which table was used for the cross-check, so reviewers can verify it's not the §10 table.

### F2 [HIGH] Real §2 Table Shape Not Verified in Plan

**What**: The plan's §2 ending cross-check design is based on **hypothetical** row patterns (`报告期末基金份额总额`, `下属分级基金的份额总额`), not on the actual parsed §2 table structure for 006597/2024. The plan's "Truth And Evidence Read" section lists extensive artifacts but does not include the real §2 parsed table rows.

**Why it matters**: If the real §2 table for 006597/2024 doesn't expose per-class ending shares in a clean row format, the entire unlabeled positional path will fail closed and `redemption_share_pressure` remains ambiguous. This means the plan may be unimplementable as designed, and the implementation worker would stop at Slice 4.

**Mitigation in plan**: Slice 4 includes "If current parsed §2 table structure does not expose ending shares in a clean row, the implementation worker should stop and report the exact parsed §2 table shape rather than guessing." This is correct behavior but means the plan is **conditionally implementable** — acceptable for a narrow repair gate, but the plan should have front-loaded this verification.

**Fix required**:
1. Before implementation starts, read the real §2 parsed tables for 006597/2024 and confirm whether per-class ending shares exist in a scannable row.
2. If they don't exist, the plan must either: (a) accept that the unlabeled path can't be independently verified and document the residual risk, or (b) find an alternative cross-check source (e.g., §9 holder structure table).
3. Update the plan's "Truth And Evidence Read" to include the actual §2 table dump.

### F3 [HIGH] headers[0] Row-Label Identification Too Permissive

**What**: Slice 1 says `_share_change_value_columns(table) -> tuple[int, ...]` should "Treat `headers[0]` as the row-label/current item column even when it contains inception-date wording. Do not require `headers[0]` to literally be `项目`."

**Why it matters**: For the real 006597 table, `headers[0]` is `基金合同生效日（2018年12月3日）基金份额总额` — which is indeed the row-label column despite not being `项目`. However, unconditionally treating `headers[0]` as row-label for all tables is over-fitted to this one case. A genuinely malformed parsed table where `headers[0]` is not a row-label column would pass through undetected, and the subsequent value column selection would be offset by one.

**Mitigation**: The plan does add downstream guardrails (row presence, value parsing, arithmetic) that would catch most misalignments. But a one-column-offset error could still produce parseable values that happen to pass arithmetic if the table is internally consistent — the §2 cross-check would then be the only defense.

**Fix required**:
1. Add a lightweight verification: check that at least one row's `row[0]` text contains a recognizable row-label pattern (e.g., `期初`, `申购`, `赎回`, `期末`, `变动`, `份额`, `项目`). If not, fail closed.
2. Or: verify that `headers[0]` compact text does NOT look like a numeric value (if `_parse_plain_decimal(headers[0])` succeeds, it's likely NOT a row-label column).
3. Document this verification as a precondition in `_share_change_value_columns`.

### F4 [MEDIUM] `_share_change_value_columns` Semantics Underspecified

**What**: The plan says `_share_change_value_columns` should return candidate value column indexes "excluding row-label and total columns." But the mechanism for excluding the row-label column is underspecified — the plan says to treat `headers[0]` as row-label, but doesn't specify what `_share_change_value_columns` does if `headers[0]` genuinely can't be identified as a row-label.

**Fix required**: Specify the return contract precisely:
- Return indexes of columns that are NEITHER row-label NOR total/aggregate.
- Row-label column identification: default to index 0, verify via F3's lightweight check.
- Total column identification: reuse `_is_total_share_header`.
- If row-label column can't be confirmed, return empty tuple (caller fails closed).

### F5 [MEDIUM] Missing Test: Non-Standard headers[0]

**What**: Test 1 uses the real inception-date header as `headers[0]`. But there's no test for a genuinely unrecognizable `headers[0]` (e.g., empty string, purely numeric, or a random text label).

**Fix required**: Add a test where `headers[0]` is something like `"期末基金份额总额"` (which could be confused with a data row label rather than a column header). Assert that the extraction either handles it correctly or fails closed with a precise reason.

### F6 [MEDIUM] Missing Test: All-Zero (Dash) Value Columns Under Unlabeled Path

**What**: The real table has two columns where header is `-` (indicating inception-date class totals of zero). The plan's arithmetic guard handles this (F beginning is zero → `class_beginning_zero`). But there's no test for a table where ALL class value columns are dash/zero in ALL rows.

**Fix required**: Add a test where all four class columns have only `-` values in all rows. Assert fail-closed (likely `aggregate_beginning_zero`).

### F7 [INFO] Explicit Header Path — Label Matching Could Miss Split-Line Class Names

**What**: Slice 1 proposes `_header_has_explicit_share_class` that "Must support class names split by line breaks through normalization." This is a forward-looking requirement — the current real table has no labels at all. But the plan doesn't specify HOW line-break-split class names should be handled.

**Note for implementation**: `_compact_text` removes all whitespace including newlines. So `"易方达安悦\nA"` becomes `"易方达安悦A"`, and `_contains_share_class_label("易方达安悦A", "A")` would match via `compact_text.endswith("A")`. This is already handled by existing code. No plan change needed, but implementation should verify this case.

### F8 [INFO] Missing Explicit Assertion: Per-Class Zero Beginning vs Aggregate Zero Beginning

**What**: The plan correctly states: "per-class beginning zero is allowed with `class_beginning_zero`; aggregate beginning zero fails closed." But the test plan (Test 1) asserts `class_beginning_zero` for F but doesn't have a dedicated test for `aggregate_beginning_zero`.

**Note for implementation**: The existing `_aggregate_share_change` (line 1581-1582) already checks `aggregate_beginning == Decimal("0")` and returns `aggregate_beginning_zero`. This guard exists in the dirty diff. No plan change needed.

## Positive Findings

1. **Root cause is correctly identified and evidence-based**: The plan uses real parsed table data (page 65, table 0) to demonstrate the header mismatch, not indirect inference. This satisfies AGENTS.md "找问题的 root cause 一定要逻辑/数据同源，禁止使用间接证据。"

2. **Fail-closed layering is well-designed**: The guardrail sequence (count match → explicit headers first → fully unlabeled check → row presence → value parsing → per-class arithmetic → aggregate arithmetic → §2 cross-check) means each layer independently blocks false positives. If any layer fails, the result is `ambiguous` — never a guessed acceptance.

3. **Mixed-signal handling is correct**: Slice 2 step 6 explicitly fails closed when some but not all headers contain class/fund-code signals. This is the right conservative posture for parsed header drift.

4. **No A-only regression**: The old code's single-column fallback (`if len(value_columns) == 1: return value_columns[0][0]`) was removed in the current dirty diff and the plan explicitly forbids its reintroduction.

5. **Boundary discipline**: The plan correctly constrains scope to Agent-layer extractor code only. No drawdown/credit/score/gate/schema/golden/Service/UI/Host/Agent/dayu changes. The non-goals section is explicit and comprehensive.

6. **Implementation stop condition**: Slice 4's instruction to stop and report if §2 table structure doesn't support the cross-check is the correct engineering decision — it prevents the implementation worker from guessing or silently degrading the requirement.

7. **Test coverage is substantially complete**: 8 test cases cover the golden path, regression (explicit headers), mixed signals, cross-check missing/mismatch, arithmetic failure, count mismatch, and non-regression for drawdown/credit. The gaps identified in F5/F6 are edge cases.

8. **Dirty scope reuse is correctly judged**: The plan correctly classifies the current diff into reusable (credit_risk, mapping dataclasses, table selection, row identification, share parsing) and out-of-scope (drawdown repair, generic share_change, score/gate changes).

## Residual Risks After Plan Acceptance

1. **§2 cross-check may be unimplementable**: If real §2 tables lack per-class ending shares, the unlabeled positional path cannot be independently verified. The plan's stop condition handles this correctly, but the consequence is that `redemption_share_pressure` stays ambiguous for 006597. This is acceptable (fail-closed is correct) but means the gate may not achieve its primary goal.

2. **Positional alignment assumes §2 column order matches §10 column order**: For 006597, the real §2 table (A/C/E/F) matches the §10 column order. But this is an assumption about fund disclosure conventions, not a verified invariant. The §2 cross-check is the defense against this assumption being wrong — if the cross-check is unavailable, the positional alignment is unverified.

3. **`ParsedTable` model may evolve**: If `ParsedTable` gains a `section_id` field in the future, the cross-check implementation should be updated to use it. This is a forward-compatibility note, not a current defect.

## Verdict

**PASS_WITH_FINDINGS** — The plan is code-generation-ready after F1, F2, and F3 are addressed. F4–F6 should be resolved during implementation. The core repair logic (unlabeled positional alignment with layered fail-closed guardrails) is sound, and the root cause is evidence-based.

F1 is the only finding that could cause a silent false positive in production — all other gaps lead to fail-closed behavior, which is safe.

Recommended action: plan author addresses F1–F3, then implementation proceeds with F4–F6 resolved inline.
