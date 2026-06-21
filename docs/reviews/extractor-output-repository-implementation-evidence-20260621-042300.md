# Extractor Output Repository Implementation Evidence

## Gate

- Work unit: `Extractor 输出仓库化`
- Gate: `implementation`
- Branch: `extractor-output-repository`
- Plan artifact: `docs/reviews/extractor-output-repository-plan-20260621-041604.md`
- Implementation evidence: `docs/reviews/extractor-output-repository-implementation-evidence-20260621-042300.md`

## Implemented Scope

### Slice 1: Fund-layer Repository and Serialization

Changed files:

- `.gitignore`
- `fund_agent/config/paths.py`
- `fund_agent/fund/extractor_output_repository.py`
- `tests/fund/test_extractor_output_repository.py`

Implemented behavior:

- Added `DEFAULT_EXTRACTOR_OUTPUT_ROOT = Path("reports/extractor-outputs")`.
- Added `ExtractorOutputRepository` with `path_for`, `save` and `load`.
- Default path is `<root>/<fund_code>/annual_report/<year>/structured_fund_data.json`.
- Schema version is `fund-agent.extractor_output.v1`.
- `load(...)` validates schema and identity against requested `fund_code + report_type + report_year`.
- Serialization preserves full `StructuredFundDataBundle` payload, including `ExtractedField.value`, `anchors`, `extraction_mode`, `note`, `nav_data` and `source_provenance`.
- `_jsonable(...)` is strict and fail-closed for unknown objects; no `default=str` fallback.
- Runtime output root is ignored by `.gitignore`.

### Slice 2: Service and CLI Thin Entry

Changed files:

- `fund_agent/services/extractor_output_service.py`
- `fund_agent/services/__init__.py`
- `fund_agent/ui/cli.py`
- `tests/services/test_extractor_output_service.py`
- `tests/ui/test_cli.py`

Implemented behavior:

- Added `ExtractorOutputSaveRequest`.
- Added `ExtractorOutputService` with injectable extractor and repository factory.
- Production default uses `FundDataExtractor()` and `ExtractorOutputRepository`.
- CLI command added:

```bash
fund-analysis extractor-output-save FUND_CODE --report-year 2024
```

- CLI only constructs request, delegates to Service and prints path/schema/identity.

### Slice 3: Docs Sync

Changed files:

- `README.md`
- `fund_agent/fund/README.md`
- `tests/README.md`

Documented:

- user-facing command and default output path;
- bundle-level repository contract;
- distinction from field-level `extraction_snapshot`, strict golden answer and quality gate;
- current non-goals and test boundaries.

## Validation

Command:

```bash
uv run pytest tests/fund/test_extractor_output_repository.py tests/services/test_extractor_output_service.py tests/ui/test_cli.py tests/fund/test_extraction_snapshot.py tests/fund/test_quality_gate_integration.py -q
```

Result:

```text
103 passed in 0.97s
```

Command:

```bash
git diff --check
```

Result: passed with no output.

Command:

```bash
uv run ruff check fund_agent/config/paths.py fund_agent/fund/extractor_output_repository.py fund_agent/services/extractor_output_service.py fund_agent/services/__init__.py fund_agent/ui/cli.py tests/fund/test_extractor_output_repository.py tests/services/test_extractor_output_service.py tests/ui/test_cli.py
```

Result:

```text
All checks passed!
```

## Non-goals Preserved

- `FundDataExtractor.extract(...)` still has no implicit write side effect.
- `extraction_snapshot` remains field-level scoring input and was not reused as bundle repository.
- Annual-period analysis does not yet read extractor output JSON.
- LLM route does not yet consume extractor output JSON.
- Non-annual report types remain unsupported.
- No source truth, golden/readiness, release or parser replacement claim is made.

## Residual Risks

- Typed hydration from `structured_fund_data.json` into `StructuredFundDataBundle` remains assigned to a future consumer gate.
- Concurrent writes and atomic replacement remain deferred until a real multi-writer use case exists.
- `report_type` expansion beyond `annual_report` requires a later schema extension gate.
