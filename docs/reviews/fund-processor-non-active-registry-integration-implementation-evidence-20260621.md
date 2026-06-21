# Fund Processor Non-active ParsedAnnualReport Registry Integration Implementation Evidence - 2026-06-21

## Gate

- Work unit: `实现非active fund Processor/Extractor index / enhanced_index / bond / qdii / fof 分类型接入 FundProcessorRegistry`
- Gate: implementation evidence
- Classification: standard
- Branch: `fund-processor-non-active-registry`
- Base: PR #35 merge commit `29075bc505a63ded7f4d923b7b6d2c30001e9902`

## Scope

This gate connects classified non-active annual `ParsedAnnualReport` inputs to the Fund-layer `FundProcessorRegistry`.

In scope:

- `index_fund`
- `enhanced_index`
- `bond_fund`
- `qdii_fund`
- `fof_fund`
- `annual_report + parsed_annual_report.v1`
- default `FundDataExtractor.extract()` facade dispatch for non-null `classified_fund_type`

Out of scope:

- explicit `fund_disclosure_document.v1` route expansion beyond active fund
- unclassified fund type inference
- parser replacement
- source policy or repository behavior changes
- `EvidenceSourceKind` / `EvidenceAnchor` expansion
- Service/UI/Host/renderer/quality-gate direct consumption
- real-report field correctness, golden/readiness or release

## Implementation

Changed files:

- `fund_agent/fund/processors/active_annual.py`
- `fund_agent/fund/processors/registry.py`
- `fund_agent/fund/processors/__init__.py`
- `fund_agent/fund/data_extractor.py`
- `tests/fund/processors/test_registry.py`
- `tests/fund/test_data_extractor.py`
- `docs/design.md`
- `fund_agent/fund/README.md`
- `tests/README.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`

Key decisions:

- Shared the existing `ParsedAnnualReport` field-family mapping through `_ParsedAnnualReportFundProcessor`.
- Kept `ActiveFundAnnualProcessor` processor ID and priority unchanged.
- Added per-type processors:
  - `IndexFundAnnualProcessor`
  - `EnhancedIndexFundAnnualProcessor`
  - `BondFundAnnualProcessor`
  - `QdiiFundAnnualProcessor`
  - `FofFundAnnualProcessor`
- Registered the five non-active processors in `FundProcessorRegistry.create_default()`.
- Changed `FundDataExtractor.extract()` so every non-null `classified_fund_type` uses `FundProcessorRegistry`.
- Kept direct legacy residual only for `classified_fund_type is None`.
- Kept explicit `FundDisclosureDocument` facade route active-fund-only.

## Validation

Passed:

```bash
uv run pytest tests/fund/processors/test_registry.py tests/fund/processors/test_active_annual_processor.py tests/fund/test_data_extractor.py -q
```

Result:

```text
65 passed
```

Passed:

```bash
uv run pytest tests/fund -q
```

Result:

```text
1618 passed
```

Passed:

```bash
uv run ruff check fund_agent/fund/processors/active_annual.py fund_agent/fund/processors/registry.py fund_agent/fund/processors/__init__.py fund_agent/fund/data_extractor.py tests/fund/processors/test_registry.py tests/fund/processors/test_active_annual_processor.py tests/fund/test_data_extractor.py
```

Result:

```text
All checks passed!
```

Passed:

```bash
uv run ruff check .
```

Result:

```text
All checks passed!
```

Passed:

```bash
git diff --check
```

Result: no whitespace errors.

## Evidence

- `test_registry_create_default_resolves_non_active_parsed_annual_processors` proves default registry resolution for `index_fund`, `enhanced_index`, `bond_fund`, `qdii_fund`, and `fof_fund`.
- `test_non_active_classified_fund_types_dispatch_to_registry` proves default facade dispatch uses the actual classified fund type and `parsed_annual_report.v1` for all five non-active types.
- `test_default_non_active_without_disclosure_uses_parsed_processor_path` and `test_index_fund_default_processor_path_smoke_test` cover the index default path.
- Existing explicit FDD tests preserve active-fund-only behavior for `fund_disclosure_document.v1`.

## Residual Risks

- Real-report field correctness is not proven by this gate; it remains a separate evidence gate.
- Non-active per-type semantic specialization beyond current shared field-family mapping is not implemented; current implementation only connects each classified type to registry and preserves existing extractor semantics.
- Unclassified fund input still uses direct legacy residual path; no new inference is introduced.
- Release/readiness remains `NOT_READY`.

## Completion Status

Implementation evidence is complete for this local gate. Next entry point is code review or separate user-directed gate.
