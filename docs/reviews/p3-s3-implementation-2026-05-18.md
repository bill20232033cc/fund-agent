# P3-S3 Implementation - CLI End-to-End Matrix

## Verdict

Implemented. P3-S3 now has a deterministic 3-fund CLI end-to-end matrix and fixes the real integration failures found while running the sample funds.

## Scope

- Added table-aware `§2` profile extraction for key-value tables where the first pair appears in table headers.
- Hardened parsed annual report cache reuse with a minimum quality gate:
  - raw text length must be realistic
  - required annual report sections must be present
- Fixed fund type classification for real table disclosures:
  - QDII can be detected from fund short name
  - bond fund name/category wins before mixed stock-index benchmark matching
- Fixed template rendering to read `benchmark_text`, matching the current profile extractor contract.
- Added P3 CLI matrix covering:
  - `110011` -> `qdii_fund`
  - `510300` -> `index_fund`
  - `000171` -> `bond_fund`

## Root Cause

Direct evidence from the real repository path showed that valid annual reports expose `§2` identity and product fields primarily through `ParsedTable` objects. The previous profile extractor and fund type classifier only handled colon-style text lines, so real reports degraded to missing fields or wrong fund type classification.

A second direct cause was stale low-quality parsed report cache data. A cache payload with tiny raw text and missing sections could previously be returned as if it were a valid annual report.

## Files Changed

- `fund_agent/fund/documents/cache.py`
- `fund_agent/fund/extractors/profile.py`
- `fund_agent/fund/fund_type.py`
- `fund_agent/fund/template/renderer.py`
- `tests/fund/documents/test_cache.py`
- `tests/fund/documents/test_repository.py`
- `tests/fund/extractors/test_profile.py`
- `tests/fund/integration/test_p3_cli_e2e_matrix.py`
- `fund_agent/fund/README.md`
- `tests/README.md`
- `docs/implementation-control.md`

## Validation

Executed:

```bash
.venv/bin/python -m pytest tests/fund/documents tests/fund/extractors/test_profile.py tests/fund/integration/test_p3_cli_e2e_matrix.py tests/fund/template/test_renderer.py -q
```

Result:

```text
33 passed
```

## Residual Risk

- P3-S3 matrix isolates network/PDF with fake repository and fake NAV provider, but still exercises real CLI parsing, Service orchestration, P1/P2 Capability logic, template rendering, and programmatic audit.
- Real PDF parsing remains sensitive to upstream table extraction quality; this slice closes the downstream table-consumption bug and stale-cache bug, not every possible PDF parser issue.
