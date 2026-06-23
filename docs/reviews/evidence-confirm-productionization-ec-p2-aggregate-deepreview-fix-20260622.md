# EC-P2 Aggregate Deepreview Fix

- Gate: aggregate deepreview fix
- Work unit: Evidence Confirm productionization / EC-P2 repository-bounded live source/PDF pathway
- Date: 2026-06-22
- Accepted finding: `docs/reviews/code-review-20260622-164847.md` finding `001`

## Fix

- Added generic `FileNotFoundError -> not_found` classification in `_classify_repository_failure()`.
- Added no-live regression coverage for plain `FileNotFoundError("missing")` in repository failure classification tests.

## Files Changed

- `fund_agent/fund/evidence_confirm_sources.py`
- `tests/fund/test_evidence_confirm_sources.py`

## Validation

```text
uv run pytest tests/fund/test_evidence_confirm_sources.py -q
39 passed in 0.91s
```

```text
uv run pytest tests/fund/test_evidence_confirm.py tests/fund/test_evidence_confirm_sources.py -q
86 passed in 0.93s
```

```text
uv run ruff check fund_agent/fund/evidence_confirm_sources.py tests/fund/test_evidence_confirm_sources.py
All checks passed!
```

```text
git diff --check -- fund_agent/fund/evidence_confirm_sources.py tests/fund/test_evidence_confirm_sources.py docs/reviews/code-review-20260622-164847.md
PASS
```

## Non-Goals Preserved

- No live/PDF command was run.
- No source fallback behavior was changed.
- No Service/UI/Host/renderer/quality-gate integration was added.
- No release/readiness or PR state was changed.

