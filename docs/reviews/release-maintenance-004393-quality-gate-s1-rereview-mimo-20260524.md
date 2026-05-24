# Release Maintenance 004393 Quality Gate S1 Targeted Re-Review - MiMo - 2026-05-24

## Scope

- Review role: Gateflow targeted re-review agent
- Work unit: `004393/2024 quality gate block root-cause investigation`
- Slice: `S1 - P0 Extraction And Comparable Fields`
- Controller judgment reviewed: `docs/reviews/release-maintenance-004393-quality-gate-s1-code-review-controller-judgment-20260524.md`
- Fix artifact reviewed: `docs/reviews/release-maintenance-004393-quality-gate-s1-code-review-fix-20260524.md`
- Changed source/test paths reviewed:
  - `fund_agent/fund/extractors/profile.py`
  - `tests/fund/extractors/test_profile.py`
  - `tests/fund/test_extraction_snapshot.py`

## Conclusion

`PASS`

The S1 fix closes both controller-accepted findings. I found no blocking correctness, boundary, or test-coverage issue in the targeted scope.

## Finding Closure

| Finding | Status | Evidence |
|---|---|---|
| `004393-S1-C1` | Closed | Table fallback now requires explicit target subsection context before extracting a rate. `_extract_fee_from_fallback_tables()` tracks `in_target_context`, `_fee_row_context()` only opens the context on the exact `7.4.10.2.x` target, and `_row_matches_fee_semantics()` rejects rows outside that context. See `fund_agent/fund/extractors/profile.py:290`, `fund_agent/fund/extractors/profile.py:362`, and `fund_agent/fund/extractors/profile.py:422`. |
| `004393-S1-C2` | Closed | Table fallback no longer guesses a parser section from unrelated existing sections. Table-derived matches call `_section_id_for_fee_table()`, which returns the conservative target subsection semantic anchor `§7.4.10.2.x`. See `fund_agent/fund/extractors/profile.py:305` and `fund_agent/fund/extractors/profile.py:480`. |

## Tests Reviewed

The added adversarial tests cover the required failure modes:

- Unbounded earlier broad labels do not win over target subsection disclosure: `tests/fund/extractors/test_profile.py:782`
- Cross-subsection label collision does not let custody fee match inside management-fee context: `tests/fund/extractors/test_profile.py:846`
- Table fallback uses target subsection anchor instead of parser-section guessing: `tests/fund/extractors/test_profile.py:904`

The tests also preserve direct `§2` precedence and partial direct/fallback combination in the same file.

## Validation

```text
uv run pytest tests/fund/extractors/test_profile.py tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py -q
66 passed in 0.71s

uv run ruff check fund_agent/fund/extractors/profile.py tests/fund/extractors/test_profile.py tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py
All checks passed!

git diff --check
passed
```

## Residual Risk

- `ParsedTable` still has no physical parser-section metadata. The current fix handles that conservatively by using target subsection semantic anchors for table fallback evidence. This is acceptable for S1 and does not block acceptance.
