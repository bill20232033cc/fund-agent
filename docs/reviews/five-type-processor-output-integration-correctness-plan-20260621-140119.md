# Five-type ProcessorRegistry + Extractor Output Integration Correctness Plan - 2026-06-21 14:01:19

## Verdict

`PLAN_FIX_READY_FOR_REREVIEW_NOT_READY`

## Goal

Add an offline, reproducible integration-correctness harness that connects the existing five-type small golden set evidence to the now-merged `FundProcessorRegistry` facade and `ExtractorOutputRepository`.

Covered fund types:

- `active_fund`: `004393`
- `index_fund`: `110020`
- `enhanced_index`: `004194`
- `bond_fund`: `006597`
- `qdii_fund`: `017641`

Deferred:

- `fof_fund`; do not count `QDII-FOF` as pure FOF.

## Motivation

The existing retained-excerpt tests prove row-field extractor correctness for five accepted rows. PR #36 and PR #37 are now merged into `origin/main`, so the next quality target is not another row-field unit test. The next target is proving the current mainline integration boundary:

```text
accepted retained-excerpt oracle
-> ParsedAnnualReport test intermediate
-> FundDataExtractor default FundProcessorRegistry path
-> StructuredFundDataBundle
-> ExtractorOutputRepository JSON
```

This must remain offline and deterministic. It must not become a live corpus run, PDF parser benchmark, golden/readiness promotion, or release proof.

## Direct Code Evidence

- `FundProcessorRegistry.create_default()` now registers parsed annual processors for `active_fund`, `index_fund`, `enhanced_index`, `bond_fund`, `qdii_fund`, and `fof_fund`.
- `FundDataExtractor.extract()` routes any classified fund type through `_extract_classified_fund_via_processor(...)`; only unclassified funds use the direct legacy residual path.
- `ExtractorOutputRepository.save()` serializes full `StructuredFundDataBundle` payloads and already preserves `Decimal` as exact JSON text.
- `tests/fund/test_small_golden_set_extractor_correctness.py` already builds same-source `ParsedAnnualReport` fixtures from `docs/reviews/mvp-small-golden-set-retained-excerpt-fixture-pdf-only-20260609.json`.
- `tests/fund/test_data_extractor.py` has synthetic registry-dispatch coverage, but not accepted-oracle five-type integration coverage.
- `tests/fund/test_extractor_output_repository.py` validates repository persistence, but not with bundles produced through the five-type registry facade.

## Non-goals

- No pure FOF candidate search or FOF oracle implementation.
- No edits to historical accepted JSON artifacts.
- No live/network/PDF access.
- No `FundDocumentRepository` real IO.
- No parser replacement or Docling/EID/pdfplumber production adoption.
- No Service/UI/Host/renderer/quality-gate consumption of raw parser artifacts.
- No extractor-output implicit side effect in `FundDataExtractor.extract()`.
- No golden/readiness or release promotion.
- No PR/merge/external GitHub mutation.

## Scope Boundary

Gate classification: `standard`.

Allowed implementation files:

- New tests-only helper module under `tests/fund/`, for example `tests/fund/small_golden_oracle_helpers.py`.
- New integration test module, for example `tests/fund/test_five_type_processor_output_integration.py`.
- Existing small golden tests only if helper extraction requires import updates.
- `tests/README.md`.

Production files are not in the initial write set. If the new integration tests expose a production bug, stop after producing failing evidence and open a narrow implementation/fix gate.

## Design Decisions

### 1. Use accepted retained-excerpt oracle as input

Reuse the existing accepted five-row oracle:

`docs/reviews/mvp-small-golden-set-retained-excerpt-fixture-pdf-only-20260609.json`

Do not rewrite it. Do not create a v2 oracle for this gate because FOF is deferred and no new source facts are being accepted.

### 2. Extract shared test helper instead of copying private test functions

Move the currently needed oracle/report-building mechanics into a tests-only helper module. The helper must:

- load the accepted oracle;
- expose the exact five fund codes and expected fund-type map;
- build `ParsedAnnualReport` objects from retained excerpts;
- keep the same no-PDF/no-network boundary.

Both the existing row-field correctness tests and the new integration test must use this shared helper for oracle loading and `ParsedAnnualReport` construction. Do not create a parallel copied builder that can drift from the row-field test input.

### 3. Prove registry path directly

Use a delegating recording registry:

- wraps `FundProcessorRegistry.create_default()`;
- records each resolved `FundProcessorDispatchKey`;
- delegates `resolve(...)` to the real default registry.

For each five-type row, assert:

- exactly one parsed annual dispatch is resolved;
- `fund_type` matches expected;
- `report_type == "annual_report"`;
- `intermediate_kind == "parsed_annual_report.v1"`;
- no FDD route is used.

### 4. Prove bundle correctness at stable field boundaries

For each five-type row, assert stable bundle values against oracle expectations:

- identity: `fund_code`, `fund_name`, `classified_fund_type`;
- benchmark;
- management fee and custody fee;
- one-year NAV return and benchmark return;
- source provenance is present and JSON-compatible.

Additional type-specific assertions:

- `index_fund` / `enhanced_index`: tracking error behavior must remain fund-type gated.
- `bond_fund`: bond risk evidence may be missing or partial depending on offline NAV fixture; this gate must not require live NAV.
- `qdii_fund`: keep QDII as QDII, not FOF.

### 5. Prove extractor-output persistence on produced bundles

For each produced bundle:

- save to `ExtractorOutputRepository(root_dir=tmp_path)`;
- assert path `<tmp_path>/<fund_code>/annual_report/2024/structured_fund_data.json`;
- load the JSON back through repository;
- assert bundle identity and selected payload fields match the produced bundle;
- assert JSON contains no non-serializable values.

## Implementation Slices

### Slice A - Tests-only oracle helper

Objective: factor reusable small golden oracle/test report construction without changing production behavior.

Allowed changes:

- Add `tests/fund/small_golden_oracle_helpers.py`.
- Move only the minimum helper logic needed for oracle loading and `ParsedAnnualReport` construction.
- Update `tests/fund/test_small_golden_set_extractor_correctness.py` to use the shared helper for oracle loading and report construction while keeping its existing assertions unchanged.
- Keep old small golden correctness tests passing.

Validation:

```bash
uv run pytest tests/fund/test_small_golden_set_extractor_correctness.py -q
```

Completion signal:

- Existing row-field correctness tests still pass.
- New integration tests and existing row-field tests share the same helper; no parallel copied report builder exists for the accepted oracle.

### Slice B - Five-type processor facade integration test

Objective: prove accepted oracle rows travel through the default registry facade into `StructuredFundDataBundle`.

Allowed changes:

- Add `tests/fund/test_five_type_processor_output_integration.py`.
- Add fake repository, fake NAV provider, fake NAV series repository, and recording delegating registry in the test module.
- Parametrize over exactly the five accepted fund codes.

Validation:

```bash
uv run pytest tests/fund/test_five_type_processor_output_integration.py tests/fund/test_data_extractor.py -q
```

Completion signal:

- Five rows dispatch through `FundProcessorRegistry` with expected fund type and parsed annual intermediate kind.
- Stable selected bundle fields match accepted oracle expectations.

### Slice C - Extractor output persistence integration test

Objective: prove bundles produced from the five-type registry facade can be persisted and loaded through `ExtractorOutputRepository`.

Allowed changes:

- Extend `tests/fund/test_five_type_processor_output_integration.py`.
- Use `tmp_path`; do not write `reports/extractor-outputs`.

Validation:

```bash
uv run pytest tests/fund/test_five_type_processor_output_integration.py tests/fund/test_extractor_output_repository.py tests/services/test_extractor_output_service.py tests/ui/test_cli.py -q
```

Completion signal:

- Each five-type produced bundle saves and loads as schema `fund-agent.extractor_output.v1`.

## Validation Matrix

Final targeted validation:

```bash
uv run pytest tests/fund/test_small_golden_set_manifest.py tests/fund/test_small_golden_set_fixture_shape.py tests/fund/test_small_golden_set_source_identity.py tests/fund/test_small_golden_set_parser_mechanics.py tests/fund/test_small_golden_set_extractor_correctness.py tests/fund/test_five_type_processor_output_integration.py tests/fund/test_data_extractor.py tests/fund/test_extractor_output_repository.py tests/services/test_extractor_output_service.py tests/ui/test_cli.py -q
uv run ruff check tests/fund/small_golden_oracle_helpers.py tests/fund/test_five_type_processor_output_integration.py tests/README.md
git diff --check
```

Expected assertions:

- Existing five-type small golden tests remain green.
- New integration test covers exactly five fund codes.
- No FOF success assertion is added.
- `FundDataExtractor` uses default registry route for all five accepted rows.
- Extractor output JSON roundtrips for all five produced bundles.

## Docs Decision

Update `tests/README.md` to mention the new integration test and clarify that it connects the five-type retained-excerpt oracle to ProcessorRegistry and extractor-output repository.

Do not update `docs/design.md` unless implementation changes production behavior. This gate is expected to add tests only.

## Risks and Residuals

| Risk | Classification | Owner / Destination |
|---|---|---|
| FOF remains missing | assigned to later work unit | Future pure FOF evidence intake gate |
| Test helper could duplicate existing private test logic | covered in current slice | Keep helper tests-only and minimal; old tests must remain green |
| Bond NAV-derived evidence may require external NAV if not controlled | covered in current slice | Fake NAV series repository; do not require live NAV |
| New integration test may expose production bug | requiring new fix gate | Stop after failing evidence and open narrow fix gate |
| This does not prove release/readiness | assigned to later work unit | Future readiness/promotion gate |

## Completion Report Format

Report:

- files changed;
- five fund codes/types covered;
- whether implementation stayed tests-only;
- validation results;
- residual risks;
- next gate.

## Next Entry

`Five-type ProcessorRegistry + Extractor Output Integration Correctness Plan Review Gate`.

Release/readiness remains `NOT_READY`.
