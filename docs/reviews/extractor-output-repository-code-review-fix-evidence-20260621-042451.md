# Extractor Output Repository Code Review Fix Evidence

## Gate

- Work unit: `Extractor 输出仓库化`
- Gate: `code review fix`
- Code review artifact: `docs/reviews/code-review-20260621-042350.md`
- Fix evidence: `docs/reviews/extractor-output-repository-code-review-fix-evidence-20260621-042451.md`

## Accepted Findings Fixed

### 001 Service 保存前未校验 extractor 返回 bundle 身份

- Status: `已修复`
- Code changes:
  - Added `_validate_bundle_identity(request, bundle)` in `fund_agent/services/extractor_output_service.py`.
  - `ExtractorOutputService.save(...)` now validates `bundle.fund_code` and `bundle.report_year` before repository save.
  - Added `test_service_rejects_extractor_bundle_identity_mismatch`.

### 002 Repository load 未校验 bundle 内部身份与顶层身份一致

- Status: `已修复`
- Code changes:
  - Added `_require_bundle_identity_matches(bundle_payload, identity)` in `fund_agent/fund/extractor_output_repository.py`.
  - `ExtractorOutputRepository.load(...)` now validates `bundle.fund_code` and `bundle.report_year` against top-level identity.
  - Added `test_repository_rejects_bundle_identity_mismatch` for fund code and report year mismatch.

## Validation

Command:

```bash
uv run pytest tests/fund/test_extractor_output_repository.py tests/services/test_extractor_output_service.py tests/ui/test_cli.py tests/fund/test_extraction_snapshot.py tests/fund/test_quality_gate_integration.py -q
```

Result:

```text
106 passed in 1.38s
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

- Atomic writes, typed hydration and non-annual report types remain deferred as classified in the implementation evidence.
