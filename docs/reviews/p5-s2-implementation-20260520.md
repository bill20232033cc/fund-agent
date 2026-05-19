# P5-S2 Quality Gate Rules Implementation - 2026-05-20

## Summary

P5-S2 implementation is completed and ready for code review.

This slice closes P4-R9 at the Capability layer by adding `fund_quality` to `score.json` and extending quality gate rules for FQ1 App category conflicts, FQ4 missing-field ratio, and FQ5 preferred_lens resolvability.

## Implemented

- Extended `fund_agent/fund/extraction_score.py`.
  - Added `FundQualityRow`.
  - Added `derive_fund_quality_records(...)`.
  - Wrote `fund_quality` into `score.json` and `score.md`.
  - Added configured App category to fund type mapping.
  - Added configured fund type to `preferred_lens_key` mapping.
  - Added fund-level uniqueness checks for repeated snapshot metadata.
- Extended `fund_agent/fund/quality_gate.py`.
  - Extended `QualityGateIssue` with structured metadata:
    - `app_category`
    - `classified_fund_type`
    - `preferred_lens_key`
    - `observed_rate`
    - `threshold`
  - Added FQ1 App category conflict branch.
  - Added FQ4 missing-field rate warn/block thresholds.
  - Added FQ5 preferred_lens resolvability block.
  - Kept old `score.json` without `fund_quality` compatible via `FQ0/info`.
- Updated docs:
  - `README.md`
  - `fund_agent/fund/README.md`
  - `tests/README.md`

## Boundary Judgment

- All new fund quality rules remain in Capability.
- No Service or CLI quality gate strategy changes were needed.
- FQ4 consumes structured snapshot missing rate, not report Markdown wording.
- FQ5 is intentionally limited to preferred_lens resolvability; it does not claim to validate a final machine-readable CHAPTER_CONTRACT lens.
- App category mapping is a quality gate check and does not replace annual-report based fund type classification.

## Tests Added / Updated

- `tests/fund/test_extraction_score.py`
  - `fund_quality` category/lens/missing-rate output
  - repeated fund-level metadata conflict handling without first-row fallback
  - score JSON/Markdown includes `fund_quality`
- `tests/fund/test_quality_gate.py`
  - FQ1 App category conflict
  - FQ4 warn/block threshold boundaries
  - FQ5 preferred_lens mismatch
  - old score JSON compatibility without `fund_quality`
- `tests/services/test_extraction_score_service.py`
  - updated fake `ExtractionScoreResult` for new stable field

## Validation

- `.venv/bin/python -m pytest tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py tests/fund/test_quality_gate_integration.py tests/services/test_fund_analysis_service.py tests/ui/test_cli.py -q`: `36 passed`
- `.venv/bin/python -m pytest tests/ -q`: `184 passed`
- `.venv/bin/ruff check .`: passed
- `git diff --check`: passed

## Known Scope Exclusions

- P5-S3 still owns widening correctness denominator beyond currently exposed comparable snapshot fields.
- P5-S4 still owns failed-fund accounting when failures only land in `errors.jsonl`.
- FQ5 does not validate final rendered report lens until template CHAPTER_CONTRACT assets become machine-readable.

## Gate Decision

Current gate: `P5-S2 implementation completed`

Next gate: `P5-S2 code review`
