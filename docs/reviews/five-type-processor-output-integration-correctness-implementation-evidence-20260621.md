# Five-type ProcessorRegistry + Extractor Output Integration Correctness Implementation Evidence - 2026-06-21

## Verdict

`IMPLEMENTED_TESTS_ONLY_READY_FOR_REVIEW_NOT_READY`

## Scope

Implemented the accepted tests-only gate for the five accepted small golden set fund types:

- `004393` active fund
- `110020` index fund
- `004194` enhanced index fund
- `006597` bond fund
- `017641` QDII fund

FOF remains deferred. This gate did not change production extractor, processor, repository, Service, UI, Host, source, fallback, golden/readiness, score, quality gate, PR, or remote state.

## Changes

- Extracted retained-excerpt oracle/report-builder helpers into `tests/fund/small_golden_oracle_helpers.py`.
- Kept `tests/fund/test_small_golden_set_extractor_correctness.py` on the same oracle while reusing the shared helper.
- Added `tests/fund/test_five_type_processor_output_integration.py`.
  - Builds in-memory `ParsedAnnualReport` fixtures from the accepted retained-excerpt oracle.
  - Uses fake annual-report repository, fake NAV provider, fake typed NAV repository, and recording registry wrapper.
  - Verifies each accepted fund type resolves through `FundProcessorRegistry` with `annual_report + parsed_annual_report.v1`.
  - Verifies core bundle fields against the same oracle: identity, benchmark, fees, returns, risk text, manager roster, tracking-error applicability.
  - Explicitly saves and reloads `ExtractorOutputRepository(tmp_path)` JSON under `<fund_code>/annual_report/2024/structured_fund_data.json`.
- Updated `tests/README.md` with the new test file and command.

## Validation

```bash
uv run pytest tests/fund/test_small_golden_set_extractor_correctness.py tests/fund/test_five_type_processor_output_integration.py -q
# 29 passed in 0.45s

uv run ruff check tests/fund/small_golden_oracle_helpers.py tests/fund/test_small_golden_set_extractor_correctness.py tests/fund/test_five_type_processor_output_integration.py
# All checks passed!

uv run pytest tests/fund/test_small_golden_set_manifest.py tests/fund/test_small_golden_set_fixture_shape.py tests/fund/test_small_golden_set_source_identity.py tests/fund/test_small_golden_set_parser_mechanics.py tests/fund/test_small_golden_set_extractor_correctness.py tests/fund/test_five_type_processor_output_integration.py tests/fund/test_data_extractor.py tests/fund/test_extractor_output_repository.py tests/services/test_extractor_output_service.py tests/ui/test_cli.py -q
# 192 passed in 1.29s

uv run ruff check tests/fund/small_golden_oracle_helpers.py tests/fund/test_small_golden_set_extractor_correctness.py tests/fund/test_five_type_processor_output_integration.py tests/README.md
# All checks passed!

git diff --check
# passed
```

## Boundary Notes

- The new integration test uses accepted retained-excerpt oracle data only; it does not read real PDFs or invoke live `FundDocumentRepository`.
- The helper now uses explicit fund-category text derived from the accepted fund-code/type mapping so the synthetic `ParsedAnnualReport` exercises the same classifier route without leaking risk-description terms into the category field.
- `004194` remains an enhanced index fund with missing tracking-error direct disclosure in the current oracle; only `110020` asserts direct tracking-error value correctness.
- Bond typed NAV drawdown remains an explicit offline unavailable gap in this test via fake `NavDataContractError`; no live CSRC/EID NAV path is exercised.
- Pre-existing untracked docs/scripts residues were left untouched.

## Residual

`NOT_READY` for release/golden/readiness. Next gate must perform code review of this tests-only implementation before any accepted commit.
