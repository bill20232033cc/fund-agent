# Release Maintenance 004393 Quality Gate S1 Code Review Fix - 2026-05-24

## Scope

- Gate: `release-maintenance 004393 S1 code review`
- Controller judgment: `docs/reviews/release-maintenance-004393-quality-gate-s1-code-review-controller-judgment-20260524.md`
- Worker role: S1 fix worker

## Finding Closure

| Finding | Status | Fix |
|---|---|---|
| `004393-S1-C1` | Closed | Table fallback now requires bounded target subsection context. A row can only produce `management_fee` after `7.4.10.2.1` is observed in the same table context, and can only produce `custody_fee` after `7.4.10.2.2` is observed. Broad `管理费` / `托管费` labels alone no longer trigger fallback extraction. |
| `004393-S1-C2` | Closed | Table fallback anchors no longer guess from unrelated parser sections. Because `ParsedTable` does not carry section metadata, table-derived fallback anchors use conservative target subsection anchors `§7.4.10.2.1` / `§7.4.10.2.2`. Text fallback keeps parser section anchoring when the target subsection heading is located in `raw_text`. |

## Tests Added

- Unbounded earlier `管理费` / `托管费` percentage rows do not win over target `7.4.10.2.x` fee disclosure.
- Cross-subsection label collision does not let custody fee match a row still bounded by `7.4.10.2.1 基金管理费`.
- Table fallback `section_id` is the target subsection semantic anchor, not the first non-empty parser section.
- Existing direct precedence, partial direct/fallback combination, and no-fee missing behavior remain covered.

## Validation

```bash
uv run pytest tests/fund/extractors/test_profile.py tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py -q
uv run ruff check fund_agent/fund/extractors/profile.py tests/fund/extractors/test_profile.py tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py
git diff --check
```

## Residual Risk

- `ParsedTable` has no explicit parser-section metadata, so table fallback intentionally uses semantic subsection anchors instead of attempting a weaker section inference.
