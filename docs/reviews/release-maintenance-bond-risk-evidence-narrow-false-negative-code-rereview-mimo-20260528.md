# Bond Risk Evidence Narrow False-Negative — Code Re-Review (MiMo)

> Date: 2026-05-28
> Role: code re-review worker (MiMo), not controller, not fix worker
> Gate: `bond risk evidence narrow false-negative gate`
> Reviewed artifacts:
>   - `fund_agent/fund/extractors/bond_risk_evidence.py` (unstaged diff)
>   - `tests/fund/extractors/test_bond_risk_evidence.py` (unstaged diff)
>   - `docs/reviews/release-maintenance-bond-risk-evidence-narrow-false-negative-code-fix-20260528.md`
>   - `docs/reviews/release-maintenance-bond-risk-evidence-narrow-false-negative-code-review-mimo-20260528.md`
>   - `docs/reviews/release-maintenance-bond-risk-evidence-narrow-false-negative-code-review-ds-20260528.md`

## Verdict

**PASS**

## Summary

Code fix correctly closes all 3 MiMo findings (F1/F2/F3) and all 5 DS findings (M1/M2/M3/L1/L2). No new false positives or false negatives introduced. Core behaviors (A/C/E/F aggregation fail-closed, drawdown boundary, no schema/score/gate changes) remain intact.

---

## 1. MiMo Findings Closure

### F1 — Current-period column detection (Medium) — CLOSED

**Original issue**: `_current_period_value_column_index` used first non-percentage numeric column without header semantics.

**Fix**: New header-based detection with three tiers:
1. `_CURRENT_PERIOD_HEADER_KEYWORDS` (`本期`, `本期末`, `期末`, `报告期末`) → prefer if exactly 1 match
2. `_PRIOR_PERIOD_HEADER_KEYWORDS` (`上年度`, `上年`, `上期`, `期初`, `年初`) → exclude
3. Single non-prior numeric column fallback → return if only 1 numeric column exists
4. Multiple unresolvable columns → `None` (fail closed)

**Verification**:
- `_is_current_period_amount_header` requires current-period keyword AND NOT percentage AND NOT prior-period. Correct.
- `_is_prior_period_header` checks against `_PRIOR_PERIOD_HEADER_KEYWORDS`. Correct.
- "上年度末" triggers prior-period (`上年度` substring). "上期末" triggers prior-period (`上期` substring). Both excluded. Correct.
- Fallback: single non-prior numeric column → accepted. Common case for simple tables. Correct.
- Multiple numeric columns with no reliable header → `None` → table rejected. Fail-closed. Correct.

**Test**: `test_credit_risk_uses_current_period_column_when_prior_period_appears_first` — headers `("长期信用评级", "上年度末公允价值", "本期末公允价值")` → asserts `AAA=10000000` (current-period) not `AAA=9000000` (prior-period). Anchor note verified. Correct.

### F2 — Rating label substring matching (Low) — CLOSED

**Original issue**: `label.upper() in row_label` is loose substring; `A` could match inside `AAA`.

**Fix**: Two-pass matching in `_rating_label_from_row`:
1. Exact match: `row_label == label.upper()` — primary
2. Compound match: `_is_compound_rating_label` — boundary-checked substring

**`_is_compound_rating_label` logic**: After `partition`, checks that the character before/after the matched label is NOT in `rating_token_chars` (A-Z, 0-9, +, -). This prevents:
- `AAAA` matching `AAA` (after-char `A` is in token chars → rejected)
- `A+` matching `A` (before-char is empty, but `+` after `A` is in token chars → rejected; `A+` matches `A+` exactly first)
- `AAA以下` matching `AAA` (after-char `下` is NOT in token chars → accepted as compound)

**Verification**: `_CREDIT_RATING_LABELS` order is long-first (`A-1`, `AAA以下`, `未评级`, `AAA`, `AA+`, ...). Exact match runs first, so `AAA` in `AAA` hits exact before compound. Compound only activates for non-exact labels. Correct.

**Test**: `test_compound_rating_labels_are_matched_without_loose_substring_false_positive` — rows `("AAA 债券", ...)` and `("AAAA 说明行", ...)` → only AAA=1000 in metric, not 9999. Correct.

### F3 — Missing test for prior-period-first column ordering (Low) — CLOSED

**Test added**: `test_credit_risk_uses_current_period_column_when_prior_period_appears_first` — same test as F1 fix. Correct.

---

## 2. DS Findings Closure

### M1 — `_current_period_value_column_index` not distinguishing current/prior (Medium) — CLOSED

Same as MiMo F1. Header-based detection with fail-closed fallback. Verified above.

### M2 — `_find_share_change_row` single keyword match too broad (Medium) — CLOSED

**Original issue**: `("申购",)` / `("赎回",)` would match `净申购` / `累计申购` rows before `本期基金总申购份额`.

**Fix**: `_find_share_change_row` now accepts `preferred_keyword_groups` and `excluded_keywords`:
- Subscription: `preferred_keyword_groups=(("总申购",), ("申购份额",))`, `excluded_keywords=("净申购", "累计申购")`
- Redemption: `preferred_keyword_groups=(("总赎回",), ("赎回份额",))`, `excluded_keywords=("净赎回", "累计赎回")`

**Logic**: When `preferred_keyword_groups` is non-empty, only rows matching at least one preferred group are returned. If no preferred match → `None` (fail closed). Excluded keywords filter rows before matching.

**Verification**: A row with only `净申购` is excluded. A row with `本期基金总申购份额` contains `总申购` → matches preferred group `("总申购",)`. Correct.

**Test**: `test_redemption_share_pressure_uses_total_subscription_and_redemption_rows` — rows include `净申购份额`, `累计申购份额` before `本期基金总申购份额`. Asserts subscription anchor `row_locator` starts with `row:4:本期基金总申购份额` and redemption with `row:7:本期基金总赎回份额`. Correct.

### M3 — `_next_profile_code_row` scan window only 3 rows (Medium) — CLOSED

**Original issue**: `enumerate(rows[start_row_number : start_row_number + 4])` only scans 3 rows.

**Fix**: Changed to `enumerate(rows[start_row_number:], start=start_row_number + 1)` — scans all remaining rows.

**Verification**: No artificial window limit. Comment/blank rows between `基金简称` and `交易代码` no longer cause missed matches. Correct.

**Test**: `test_share_class_evidence_from_section_two_table_with_intervening_rows` — 2 intervening rows (`注：本表披露...` and empty row) between name and code rows. A/C/E/F mapping still resolved. Correct.

### L1 — Test name "anchor_missing" misleading (Low) — CLOSED

**Fix**: Renamed to `test_credit_risk_percentage_only_table_not_accepted`. Correct.

### L2 — Default fixture negative ending shares (Low) — CLOSED

**Fix**: `_share_change_table_ac_ef` default F-class ending changed from `"-200,000.00"` to `"-"` (dash-as-zero). Arithmetic mismatch test uses explicit `("期末基金份额总额", "901,000.00", ...)` to create inconsistency. Correct.

---

## 3. New False Positive / False Negative Check

### 3.1 No new false positives introduced

- **Credit risk accepted**: Requires `_is_holding_rating_distribution_table` (3-layer rejection) + at least 2 rating rows with recognized labels + parseable current-period numeric values + non-zero rows. All gates intact.
- **Redemption accepted**: Requires §2 mapping + §10 table selection (scoring, financial-statement rejection) + column alignment (exact count match) + row matching (preferred keywords + exclusion) + per-class arithmetic reconciliation + aggregate reconciliation. All gates intact.
- **Drawdown**: No changes. Weak qualitative remains.

### 3.2 No new false negatives introduced

- **Credit risk**: `_current_period_value_column_index` fallback accepts single non-prior numeric column (common case). Compound rating labels handled. `_FUND_OWN_RATING_KEYWORDS` includes new `基金信用评级` keyword — tighter rejection of fund-own tables is intentional and correct.
- **Redemption**: Preferred keyword groups require `总申购`/`申购份额` or `总赎回`/`赎回份额`. If a §10 table uses non-standard row labels without these keywords, `_find_share_change_row` returns `None` → `incomplete_share_change_rows` → ambiguous. This is correct fail-closed behavior; such tables should not produce accepted evidence.
- **Profile code row**: Extended scan window reduces false negatives from intervening rows. Correct.

### 3.3 Edge case: "期末" ambiguity

"期末" appears in both `_CURRENT_PERIOD_HEADER_KEYWORDS` and could conceptually be prior-period in some contexts (e.g., "上期末"). Verified: `_is_current_period_amount_header` checks `_is_prior_period_header` first; "上期末" contains `上期` → excluded. Standalone "期末" → accepted as current-period. Correct.

---

## 4. Core Behavior Verification

### 4.1 A/C/E/F aggregation and share row selection — accepted/fail-closed correct

- `_aggregate_share_change`: column alignment → row finding → per-class calculation → per-class arithmetic check → aggregate sum → aggregate arithmetic check. Any failure → `na_reason` → ambiguous. Correct.
- `_find_share_change_rows`: beginning/subscription/redemption/ending all required; split optional. Missing any → `None`. Correct.
- `_calculate_share_class_changes`: `beginning + net_change ≈ ending` per class (tolerance 0.01). Mismatch → `share_change_arithmetic_mismatch`. Correct.
- Aggregate: `aggregate_beginning == 0` → fail closed. Arithmetic mismatch → fail closed. Correct.

### 4.2 Drawdown boundary — no changes

`_extract_drawdown_stress` not modified. `test_drawdown_control_text_alone_is_weak` unchanged. Correct.

### 4.3 No schema/score/gate changes

- `models.py`: not modified
- `extraction_snapshot.py`: not modified
- `extraction_score.py`: not modified
- `quality_gate.py`: not modified
- Service/UI/Host/Agent/dayu: not modified

Only `_FUND_OWN_RATING_KEYWORDS` expanded with `基金信用评级` — this is a rejection keyword addition, not a schema/semantic change. Correct.

---

## 5. Fix Artifact Verification

Code-fix artifact (`docs/reviews/release-maintenance-bond-risk-evidence-narrow-false-negative-code-fix-20260528.md`) accurately describes all 5 fixes. Residual risks documented (no real 006597/2024 validation by fix worker, credit-risk conservative detection, drawdown remains weak). All consistent with observed diff.

---

## 6. Findings

No new findings. All prior findings closed.

| Prior ID | Source | Status |
|----------|--------|--------|
| F1 | MiMo | CLOSED — header-based detection + fail-closed + test |
| F2 | MiMo | CLOSED — exact-first + boundary-checked compound + test |
| F3 | MiMo | CLOSED — test added |
| M1 | DS | CLOSED — same as F1 |
| M2 | DS | CLOSED — preferred keywords + exclusion + test |
| M3 | DS | CLOSED — full-row scan + test |
| L1 | DS | CLOSED — test renamed |
| L2 | DS | CLOSED — fixture corrected |

---

## 7. Recommendation

Gate passes. Code fix is complete and correct. Ready for controller validation (real 006597/2024 path recommended but not required for gate pass).
