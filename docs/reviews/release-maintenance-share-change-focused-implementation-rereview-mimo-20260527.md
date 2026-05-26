# Targeted Re-Review: share_change Implementation M1 Fix

> Date: 2026-05-27
> Reviewer: AgentMiMo
> Review target: `fund_agent/fund/extractors/holdings_share_change.py` and `tests/fund/extractors/test_holdings_share_change.py` (current diff)
> Prior review: `docs/reviews/release-maintenance-share-change-focused-implementation-review-mimo-20260527.md`
> Verdict: **PASS**

---

## M1 Resolution: A-Z suffix false-positive risk

**Status: RESOLVED**

The fix introduces `_endswith_bare_share_class_label` (new function at ~line 941-957):

```python
def _endswith_bare_share_class_label(text: str, class_label: str) -> bool:
    if not text.endswith(class_label):
        return False
    prefix = text[: -len(class_label)]
    if not prefix:
        return False
    return not prefix[-1].isascii() or not prefix[-1].isalpha()
```

Logic: the `endswith` match is only accepted when the character immediately preceding the label is NOT a Latin letter. This correctly handles:

| Text | Label | `endswith` | Prefix last char | Result | Correct? |
|------|-------|-----------|-----------------|--------|----------|
| "目标ETF" | F | True | "T" (ASCII alpha) | False | Yes — ETF is not an F-class |
| "场内LOF" | F | True | "O" (ASCII alpha) | False | Yes — LOF is not an F-class |
| "累计NAV" | V | True | "A" (ASCII alpha) | False | Yes — NAV is not a V-class |
| "国泰利享中短债债券A" | A | True | "券" (non-ASCII) | True | Yes — Chinese fund name suffix |
| "A类" | A | True (via "A类" pattern, not endswith) | — | True | Yes — explicit class marker |
| "DATA" | A | True | "T" (ASCII alpha) | False | Yes — English word not a class |

The `X类` and `X份额` patterns in `_contains_share_class_label` are unaffected by this change — they continue to match explicit class markers regardless of preceding character.

---

## New Tests

Two new tests added:

1. `test_extract_holdings_share_change_does_not_treat_etf_lof_nav_suffixes_as_share_classes`: Uses `_english_suffix_header_table()` with headers `("项目", "目标ETF", "场内LOF", "累计NAV")`. Asserts `extraction_mode == "missing"` — proves English suffixes do not trigger false positive share-class detection.

2. `test_extract_holdings_share_change_ignores_etf_suffix_but_keeps_chinese_fund_name_suffix`: Uses `_share_change_table_with_etf_and_bond_a_headers()` with headers `("项目", "目标ETF", "国泰利享中短债债券A")` plus §2 mapping. Asserts `extraction_mode == "direct"` with `share_class_column == "国泰利享中短债债券A"` — proves ETF suffix is ignored while Chinese fund name A-suffix is correctly matched.

Both tests cover the exact false-positive scenarios identified in M1. No scope drift — only the authorized files changed.

---

## Verdict

**PASS**

M1 is fully resolved. The `_endswith_bare_share_class_label` function correctly rejects Latin-letter-adjacent suffixes (ETF, LOF, NAV, DATA) while accepting Chinese-character-adjacent suffixes (基金名A). New tests explicitly cover both rejection and acceptance paths. No scope drift.
