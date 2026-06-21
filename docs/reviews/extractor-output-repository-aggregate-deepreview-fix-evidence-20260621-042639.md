# Extractor Output Repository Aggregate Deepreview Fix Evidence

## Gate

- Work unit: `Extractor 输出仓库化`
- Gate: `aggregate deepreview fix`
- Aggregate review artifact: `docs/reviews/code-review-20260621-042603.md`
- Fix evidence: `docs/reviews/extractor-output-repository-aggregate-deepreview-fix-evidence-20260621-042639.md`

## Accepted Finding Fixed

### 001 save 返回 payload 与落盘/load payload 的 sequence 形态不一致

- Status: `已修复`
- Code changes:
  - `_jsonable(...)` now returns `list[...]` for `Sequence` values.
  - Added `test_repository_save_and_load_payload_use_same_sequence_shape`.
  - Test asserts `save()` returned payload and `load()` returned payload use the same JSON array/list shape and are equal.

## Validation

Command:

```bash
uv run pytest tests/fund/test_extractor_output_repository.py tests/services/test_extractor_output_service.py tests/ui/test_cli.py tests/fund/test_extraction_snapshot.py tests/fund/test_quality_gate_integration.py -q
```

Result:

```text
107 passed in 1.33s
```

Command:

```bash
uv run ruff check fund_agent/config/paths.py fund_agent/fund/extractor_output_repository.py fund_agent/services/extractor_output_service.py fund_agent/services/__init__.py fund_agent/ui/cli.py tests/fund/test_extractor_output_repository.py tests/services/test_extractor_output_service.py tests/ui/test_cli.py
```

Result:

```text
All checks passed!
```

Command:

```bash
git diff --check
```

Result: passed with no output.

## Residual Risks

- Atomic writes, typed hydration and non-annual report types remain deferred.
