# FundDisclosureDocument Non-active Facade/Processor Route Implementation Evidence

## Gate

- Work unit: `FundDisclosureDocument Non-active Facade/Processor Route`
- Gate type: `standard implementation evidence`
- Branch: `fund-processor-non-active-registry`
- Base context: branch is based on PR #35 merge commit `29075bc505a63ded7f4d923b7b6d2c30001e9902`

## Scope

Implemented explicit `fund_disclosure_document.v1` routing for the existing six `FundType` values:

- `active_fund`
- `index_fund`
- `enhanced_index`
- `bond_fund`
- `qdii_fund`
- `fof_fund`

The route still requires `FundDataExtractor.extract(..., disclosure_intermediate=...)` explicit opt-in. Default `disclosure_intermediate=None` extraction remains on the `parsed_annual_report.v1` path and does not auto-parse FDD.

## Changed Files

- `fund_agent/fund/processors/fund_disclosure_processor.py`
  - Added a shared `_FundDisclosureDocumentFundProcessor` base.
  - Kept active FDD support through `FundDisclosureDocumentProcessor`.
  - Added one concrete non-active FDD processor per fund type:
    - `IndexFundDisclosureDocumentProcessor`
    - `EnhancedIndexDisclosureDocumentProcessor`
    - `BondFundDisclosureDocumentProcessor`
    - `QdiiFundDisclosureDocumentProcessor`
    - `FofFundDisclosureDocumentProcessor`
  - Preserved admission, identity validation, source-truth proof, candidate-only gap, and field-family extraction behavior inside the shared implementation.
- `fund_agent/fund/processors/registry.py`
  - Registered all five non-active FDD processors in the default registry.
- `fund_agent/fund/processors/__init__.py`
  - Exported the FDD processor classes.
- `fund_agent/fund/data_extractor.py`
  - Changed the explicit FDD facade route to use `classified_fund_type` from the repository-loaded `ParsedAnnualReport` instead of hard-coded `active_fund`.
  - Kept FDD intermediate identity validation before processor resolution.
  - Kept no fallback on unsupported/blocked processor result.
- `tests/fund/processors/test_fund_disclosure_processor.py`
  - Added default-registry resolution coverage for five non-active FDD processors.
  - Added supports coverage proving each FDD processor only accepts its declared fund type.
- `tests/fund/processors/test_registry.py`
  - Added default-registry FDD resolution coverage for five non-active fund types.
- `tests/fund/test_data_extractor.py`
  - Replaced the old non-active FDD active-only failure expectation with a parameterized facade dispatch regression for `index_fund`, `enhanced_index`, `bond_fund`, `qdii_fund`, and `fof_fund`.
  - The test asserts dispatch `fund_type`, `intermediate_kind`, and projected bundle identity.
- `docs/design.md`
- `fund_agent/fund/README.md`
- `tests/README.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`

## Invariants Preserved

- `FundDisclosureDocumentIntermediate` does not decide fund type.
- Fund type still comes from the repository-loaded `ParsedAnnualReport` profile classification.
- `disclosure_intermediate=None` remains default production behavior and does not parse `fund_disclosure_document.v1`.
- Candidate-only evidence remains internal to processor results and does not become public source truth.
- No `EvidenceSourceKind` / `EvidenceAnchor` expansion.
- No repository/source policy change.
- No Service/UI/Host/renderer/quality-gate direct FDD consumption.
- No parser replacement, real-report correctness, golden/readiness, release, or PR external-state transition claim.

## Validation

Passed:

```text
uv run pytest tests/fund/processors/test_fund_disclosure_processor.py tests/fund/processors/test_registry.py tests/fund/test_data_extractor.py -q
260 passed in 1.16s

uv run pytest tests/fund/processors tests/fund/test_data_extractor.py -q
285 passed in 0.99s

uv run pytest tests/fund -q
1624 passed in 5.42s

uv run ruff check .
All checks passed!

git diff --check
passed with no output
```

## Residual Risks

- Real-report correctness for non-active FDD source-truth extraction is not proven by this route gate; it requires separate evidence gates.
- Fund types outside the current `FundType` literal set, such as money market funds, commodity funds, or REITs, remain unsupported/unmodeled by this work unit.
- The active FDD concrete class name remains `FundDisclosureDocumentProcessor` for existing call sites and tests; a future naming cleanup may introduce an explicit `ActiveFundDisclosureDocumentProcessor` alias, but that is not required for this route gate.

## Status

Implementation evidence is formed locally. Validation passed for the current implementation scope.
