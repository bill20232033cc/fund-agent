# Code Review: share_change Focused Implementation

> Date: 2026-05-27
> Reviewer: AgentMiMo
> Changed files: `fund_agent/fund/extractors/holdings_share_change.py`, `tests/fund/extractors/test_holdings_share_change.py`
> Evidence: `docs/reviews/release-maintenance-share-change-focused-implementation-evidence-20260527.md`
> Verdict: **PASS_WITH_FINDINGS**

---

## Criterion 1: Correctness of A-Z label detection; false positive risk

**Finding M1: `_contains_share_class_label` `endswith` check matches any text ending in a single uppercase letter**

Evidence: `holdings_share_change.py:937` — `compact_text.endswith(normalized_class_label)`.

The three match patterns are:
1. `f"{label}类" in compact_text` — specific pattern like "A类"
2. `f"{label}份额" in compact_text` — specific pattern like "A份额"
3. `compact_text.endswith(normalized_class_label)` — any text ending in the letter

Pattern 3 is overly broad. For A/C (original scope), this was unlikely to cause false positives because §10 fund names end in "A" or "C". But with A-Z generalization, any cell text ending in B, D, E, F, G, etc. would match. Examples:
- "ETF" → matches F
- "MOMENTA" → matches A (if no other A-Z letter also matches, `_share_class_label_from_text` returns "A")
- "NAV" → matches V

The uniqueness guard in `_share_class_label_from_text` (line 963: `len(unique_matches) != 1 → None`) provides partial mitigation: if "NAV" is the only text and only V matches, it returns "V". But this means a table containing "NAV" in a cell would be counted as having a V-class label by `_table_share_class_label_count`.

Risk: In practice, §10 tables contain Chinese fund names ending in class letters, so real false positives are unlikely. But the `endswith` pattern is semantically wrong for A-Z generalization — it should require a word boundary or a Chinese-character prefix.

Recommendation: Either (a) restrict `endswith` to require a non-ASCII character before the letter (e.g., `compact_text[-2:-1]` is Chinese), or (b) remove the `endswith` pattern and rely only on `X类` / `X份额` patterns plus explicit §2 evidence. If `endswith` is kept, add a test proving that "ETF" in a table header does not produce an F-class match.

Severity: **MATERIAL**

---

**Finding M2: Case inconsistency in `_contains_share_class_label` `endswith` check**

Evidence: `holdings_share_change.py:932-937`.

```python
compact_text = _compact_text(text).upper()      # uppercased
normalized_class_label = class_label.upper()      # uppercased
return (
    f"{normalized_class_label}类" in compact_text   # checks uppercased
    or f"{normalized_class_label}份额" in compact_text  # checks uppercased
    or compact_text.endswith(normalized_class_label)   # checks uppercased vs uppercased — OK
)
```

Actually, on closer inspection: `compact_text` IS uppercased on line 932, and `normalized_class_label` is uppercased on line 933. The `endswith` check compares uppercased to uppercased. This is consistent. My initial concern was misplaced.

**Withdrawn — no finding.**

---

## Criterion 2: Fail-closed behavior

**Verdict: PASS**

- No default A-class, first-column, total-share, or other-code fallback (confirmed by code structure and 006597 rerun).
- `_share_class_label_from_text` returns `None` for 0 or multiple matches.
- `_select_share_change_value_column` falls back to `extraction_mode="missing"` when no deterministic column is found.
- 006597 post-rerun: `share_change` remains `missing` with explicit ambiguity note (evidence lines 60-61).

No finding.

---

## Criterion 3: §2 subordinate mapping logic

**Verdict: PASS**

- `_class_matches_from_rows` maps fund_code → class_label via §2 subordinate rows; returns only unique matches.
- `_table_likely_belongs_to_section_two` now accepts tables with subordinate mapping rows even without profile identity rows (`基金名称` / `基金主代码`).
- Multiple matches from §2 tables are deduplicated; if not unique, returns `None`.

No finding.

---

## Criterion 4: Split table behavior regression risk

**Verdict: PASS**

- `_is_split_share_header_table` changed from "contains A and C" to "≥2 share class labels" (line 267).
- `_is_split_share_data_table` changed from "not A and not C" to "0 share class labels" (line 290).
- This broadens split-table detection to non-A/C classes, which is correct for the A-Z generalization.
- The actual column selection still requires deterministic evidence, so broader detection does not introduce wrong-column selection risk.

No finding.

---

## Criterion 5: Test coverage

**Verdict: PASS**

New tests added:
1. `test_extract_holdings_share_change_selects_bond_a_class_from_section_two_mapping` — A/C/E/F multi-class with §2 mapping selects A for fund_code 006597.
2. `test_extract_holdings_share_change_selects_bond_class_from_subordinate_rows_only` — §2 subordinate rows without profile identity header still provide evidence.
3. `test_extract_holdings_share_change_fails_closed_for_duplicate_bond_class_columns` — duplicate A-class columns fail closed.

Existing tests preserved: 21 total passed (evidence line 42). Existing A/C, A/D, split-table, single-value, total-column, and fail-closed tests all pass.

No finding.

---

## Criterion 6: 006597 remaining missing is acceptable

**Verdict: PASS**

Evidence lines 60-68: `share_change` remains `missing` with the same ambiguity note. Quality gate remains `block` with 7 issues. The implementation correctly preserves ambiguity when deterministic evidence is not available from the parsed public extraction output. Per the acceptance criteria (plan lines 234-236), "preserves explicit missing/ambiguity with no wrong-column selection and records why implementation cannot safely choose" is a valid outcome.

No finding.

---

## Criterion 7: No forbidden boundary changes

**Verdict: PASS**

Only two files changed: `holdings_share_change.py` and `test_holdings_share_change.py`. No changes to renderer, FQ0-FQ6, Service/CLI, Host/Agent/dayu, repository, source fallback, models, snapshot, score, quality gate, or any other module. Import reordering (line 5-6) is cosmetic only.

No finding.

---

## Summary

| Finding | Severity | Description |
|---------|----------|-------------|
| M1 | MATERIAL | `_contains_share_class_label` `endswith` check matches any text ending in a single uppercase letter; needs boundary constraint or explicit test for false positive like "ETF" |
| M2 | WITHDRAWN | Case inconsistency — on re-inspection, `compact_text` is uppercased before `endswith` check |

---

## Verdict

**PASS_WITH_FINDINGS**

The implementation is correct, fail-closed, well-tested, and within authorized scope. The 006597 rerun correctly preserves ambiguity. The one material finding (M1) is about the `endswith` pattern in `_contains_share_class_label` being overly broad for A-Z generalization — any text ending in a single uppercase letter matches. In practice this is unlikely to cause issues with Chinese annual report §10 tables, but the pattern should be tightened or a false-positive test added. This finding does not block closeout but should be addressed as a follow-up hardening item.
