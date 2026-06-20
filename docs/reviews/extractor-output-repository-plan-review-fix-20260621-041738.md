# Extractor Output Repository Plan Review Fix

## Gate

- Work unit: `Extractor 输出仓库化`
- Gate: `plan review fix`
- Plan artifact: `docs/reviews/extractor-output-repository-plan-20260621-041604.md`
- Review artifact: `docs/reviews/plan-review-20260621-041657.md`
- Fix artifact: `docs/reviews/extractor-output-repository-plan-review-fix-20260621-041738.md`

## Accepted Findings Fixed

### 001 宽松文本 fallback 会把 schema drift 写成合法 JSON

- Status: `已修复`
- Plan change:
  - Slice 1 serialization changed to strict recursive `_jsonable(...)`.
  - Allowed value types are limited to `None`, scalar JSON primitives, dataclass instances, mappings with string keys and sequences.
  - Unknown object types now fail closed with `TypeError`.
  - Generic `default=str` and `Path` fallback are explicitly forbidden.
  - Added repository test requirement: `test_repository_rejects_unknown_non_jsonable_bundle_value`.

### 002 Service 计划要求 fake 测试但没有注入点

- Status: `已修复`
- Plan change:
  - Service API now includes `ExtractorOutputExtractor` and `ExtractorOutputRepositoryProtocol`.
  - `ExtractorOutputService.__init__` now accepts injected `extractor` and `repository_factory`.
  - Production defaults still construct `FundDataExtractor()` and `ExtractorOutputRepository(root)`.
  - Slice 2 tests now explicitly use injected fakes and prove no real `FundDocumentRepository` path is touched.

## Validation

Plan-only fix; no production code changed yet.

Command:

```bash
git diff --check -- docs/reviews/extractor-output-repository-plan-20260621-041604.md docs/reviews/plan-review-20260621-041657.md docs/reviews/extractor-output-repository-plan-review-fix-20260621-041738.md
```

Expected result: no whitespace errors.

## Residual Risks

- Typed hydration remains deferred to annual-period/LLM consumer gate.
- Concurrent writes and atomic replacement remain deferred until multi-writer use case exists.
- Non-annual report types remain deferred to schema extension gate.
