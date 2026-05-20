# P7 Aggregate Targeted Re-review — Controller Acceptance

## Scope

- Gate: P7 aggregate targeted re-review
- Acceptance time: 2026-05-20
- Reviewed artifacts:
  - `docs/reviews/p7-aggregate-deepreview-mimo-20260520.md`
  - `docs/reviews/p7-aggregate-deepreview-glm-20260520.md`
  - `docs/reviews/p7-aggregate-fix-20260520.md`
  - `docs/reviews/p7-aggregate-rereview-mimo-20260520.md`
  - `docs/reviews/p7-aggregate-rereview-glm-20260520.md`

## Judgment

P7 aggregate targeted re-review is accepted.

MiMo and GLM both verified that the accepted aggregate finding is closed:

- malformed `source_metadata_json` now degrades to `None`;
- non-object JSON now degrades to `None`;
- invalid `source` name now degrades to `None` inside the cache read tolerance layer;
- `get_pdf_entry()` and `get_pdf_path()` keep returning usable PDF cache hits when the PDF file exists;
- `AnnualReportSourceMetadata.from_dict(...)` and `_normalize_source_name(...)` remain fail-closed outside cache read tolerance;
- no Service/UI/Engine/CLI source-awareness leakage was introduced;
- README/test documentation matches code facts.

The two low aggregate findings remain accepted residual risks and do not block P7:

- fallback success does not retain prior failure chain;
- legacy parsed report cache does not auto-refresh source metadata without `force_refresh=True`.

## Verification

Controller and reviewers observed:

```bash
.venv/bin/python -m pytest tests/fund/documents/test_cache.py -q
# 11 passed

.venv/bin/python -m pytest tests/ -q
# 293 passed

.venv/bin/python -m ruff check fund_agent/fund/documents/cache.py tests/fund/documents/test_cache.py
# All checks passed

git diff --check
# passed
```

## Result

P7 aggregate review/fix/rereview is accepted.

Next gate: `P7 acceptance / ready-to-open-draft-PR reconciliation`.
