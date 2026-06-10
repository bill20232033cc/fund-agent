# MVP Small Golden Set Downstream Integration Implementation Evidence - 2026-06-10

## Scope

Current gate: `EID single-source downstream integration implementation gate`.

Role: implementation worker.

Implemented only the accepted downstream integration for existing row-shape extractor surfaces. No live EID, network, PDF/FDR live acquisition, fallback, provider/LLM, fixture projection, golden/readiness, Service, Host or Agent runtime expansion was performed.

## Changed Files

- `fund_agent/fund/data_extractor.py`
- `fund_agent/fund/extraction_snapshot.py`
- `fund_agent/fund/report_evidence.py`
- `fund_agent/fund/chapter_facts.py`
- `fund_agent/fund/evidence_availability.py`
- `tests/fund/test_data_extractor.py`
- `tests/fund/test_extraction_snapshot.py`
- `tests/fund/test_report_evidence.py`
- `tests/fund/test_chapter_facts.py`
- `tests/fund/test_evidence_availability.py`
- `fund_agent/fund/README.md`
- `tests/README.md`
- `docs/reviews/mvp-small-golden-set-downstream-integration-implementation-evidence-20260610.md`

## Implemented Slices

### Slice A: Bundle Fan-in

- Added explicit `StructuredFundDataBundle.portfolio_managers`.
- Added explicit `StructuredFundDataBundle.risk_characteristic_text`.
- Populated `portfolio_managers` from `manager_ownership_result.portfolio_managers`.
- Populated `risk_characteristic_text` from `profile_result.risk_characteristic_text`.
- Kept safe missing defaults for older unrelated test constructors outside this gate scope.

### Slice B: Snapshot and Report Evidence

- Added `portfolio_managers` to snapshot ordering under `manager`.
- Added `risk_characteristic_text` to snapshot ordering under `risk`.
- Added comparable subfields:
  - `portfolio_managers`: `schema_version`, `manager_count`
  - `risk_characteristic_text`: `schema_version`, `risk_characteristic_text`
- Added report evidence field specs:
  - `portfolio_managers` as `manager` fact path `portfolio_managers`
  - `risk_characteristic_text` as `risk` fact path `risk_characteristic_text`
- Preserved `bond_top_holdings` and `target_fund_holdings` inside `holdings_snapshot`; no top-level bundle fields were added for them.
- Did not change `top_holdings_status` or `top_holdings_source` semantics.

### Slice C: Chapter Facts and Evidence Availability

- Added source field ids:
  - `structured.portfolio_managers`
  - `structured.risk_characteristic_text`
- Mapped `portfolio_managers` to chapters 1 and 3.
- Mapped `risk_characteristic_text` to chapters 1 and 6.
- Kept `holdings_snapshot` as the source field for holdings sub-shapes in chapters 3, 5 and 6.
- Added EvidenceAvailability exposure:
  - `ch1.requirement.portfolio_managers_reviewed`
  - `ch1.requirement.risk_characteristic_text_reviewed`
  - `ch3.required_output.item_01` now includes `structured.portfolio_managers`
  - `ch6.requirement.risk_characteristic_text_reviewed`
- Renderer output was not changed.

## Downstream Surfaces Now Consuming Fields

`portfolio_managers` is now consumed by:

- `StructuredFundDataBundle`
- `FundDataExtractor.extract()`
- `build_snapshot_records()`
- `project_report_evidence_bundle()`
- `project_chapter_facts()` for chapters 1 and 3
- `derive_evidence_availability()` for chapter 1 and chapter 3 basic manager required output

`risk_characteristic_text` is now consumed by:

- `StructuredFundDataBundle`
- `FundDataExtractor.extract()`
- `build_snapshot_records()`
- `project_report_evidence_bundle()`
- `project_chapter_facts()` for chapters 1 and 6
- `derive_evidence_availability()` for chapters 1 and 6

## Final Source Field IDs

- `portfolio_managers`: `structured.portfolio_managers`
- `risk_characteristic_text`: `structured.risk_characteristic_text`

## Validation

```bash
uv run pytest tests/fund/test_data_extractor.py -q
```

Result: `10 passed in 0.88s`

Final rerun result after README sync: `10 passed in 0.41s`

```bash
uv run pytest tests/fund/test_extraction_snapshot.py -q
```

Result: `13 passed in 0.89s`

Final rerun result after README sync: `13 passed in 0.42s`

```bash
uv run pytest tests/fund/test_report_evidence.py -q
```

Result: `23 passed in 0.90s`

Final rerun result after README sync: `23 passed in 0.43s`

```bash
uv run pytest tests/fund/test_chapter_facts.py tests/fund/test_evidence_availability.py -q
```

Result: `23 passed in 0.44s`

Final rerun result after README sync: `23 passed in 0.44s`

```bash
uv run pytest tests/fund/test_small_golden_set_extractor_correctness.py -q
```

Result: `24 passed in 0.40s`

Final rerun result after README sync: `24 passed in 0.40s`

```bash
uv run ruff check fund_agent/fund/data_extractor.py fund_agent/fund/extraction_snapshot.py fund_agent/fund/report_evidence.py fund_agent/fund/chapter_facts.py fund_agent/fund/evidence_availability.py tests/fund/test_data_extractor.py tests/fund/test_extraction_snapshot.py tests/fund/test_report_evidence.py tests/fund/test_chapter_facts.py tests/fund/test_evidence_availability.py
```

Result: `All checks passed!`

Final rerun result after README sync: `All checks passed!`

```bash
git diff --check -- fund_agent/fund/data_extractor.py fund_agent/fund/extraction_snapshot.py fund_agent/fund/report_evidence.py fund_agent/fund/chapter_facts.py fund_agent/fund/evidence_availability.py tests/fund/test_data_extractor.py tests/fund/test_extraction_snapshot.py tests/fund/test_report_evidence.py tests/fund/test_chapter_facts.py tests/fund/test_evidence_availability.py fund_agent/fund/README.md tests/README.md docs/reviews/mvp-small-golden-set-downstream-integration-*.md
```

Result: passed with no output.

## Follow-up Fix Validation

Reviewer accepted non-blocking finding: `tests/fund/test_data_extractor.py` only asserted `hasattr` for `portfolio_managers` and `risk_characteristic_text` after `FundDataExtractor.extract()`.

Fix:

- Extended the existing in-memory fake annual report fixture with local `ParsedTable` rows for `portfolio_manager_tenure_list.v1` and `risk_characteristic_text.v1`.
- Replaced `hasattr` assertions with value-level checks for extraction mode, note, schema version, fund identity, extracted values and anchors.
- No production code changed.

```bash
uv run pytest tests/fund/test_data_extractor.py -q
```

Result: `10 passed in 0.77s`

## Residual Risks and Preserved Non-goals

- `bond_top_holdings` and `target_fund_holdings` remain `holdings_snapshot` sub-shapes; this gate does not add separate quality or top-level bundle semantics.
- This gate does not prove live EID failure branches.
- This gate does not run or authorize PDF/network/FDR live acquisition, fallback, provider/LLM, fixture projection, golden/readiness, score-loop, Service, Host or Agent runtime expansion.
- Control docs were not edited by this implementation worker.
