# Bond Risk Evidence Extractor / Anchor Hardening Slice 3 Implementation

> Date: 2026-05-27
> Role: implementation worker
> Gate: Slice 3 bundle integration
> Branch: `codex/local-reconciliation`
> Status: implementation complete, awaiting independent review

## Scope Guard

- No full gateflow was started.
- No self-review, commit, push, PR, approval, merge, ready marking, or golden promotion was performed.
- Changes stayed within the allowed Slice 3 files plus this implementation artifact.
- Annual report loading remains a single `FundDocumentRepository` call through `FundDataExtractor.extract(...)`; no PDF cache, direct source, or download helper access was added.
- Constructor, Service/UI parameters, snapshot, score, quality gate, and golden paths were not changed.

## Files Changed

- `fund_agent/fund/data_extractor.py`
- `tests/fund/test_data_extractor.py`
- `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-slice3-implementation-20260527.md`

## Implementation Summary

- Added explicit `StructuredFundDataBundle.bond_risk_evidence: ExtractedField[BondRiskEvidenceValue]` with Chinese attribute documentation for template第6章“核心风险”.
- Imported `BondRiskEvidenceValue` and `extract_bond_risk_evidence` through the extractor public surface.
- Added a safe default missing `bond_risk_evidence` field for direct test fixture construction that does not run production extraction.
- In `FundDataExtractor.extract(...)`, computed `classified_fund_type` once from `profile_result.basic_identity`.
- Reused that same classified type for both `_tracking_error_for_fund_type(...)` and `extract_bond_risk_evidence(report, classified_fund_type=...)`.
- Called `extract_bond_risk_evidence(...)` after existing holdings/share-change extraction, using the already loaded `ParsedAnnualReport`.
- Updated data extractor tests so fake repository extraction returns a bundle carrying `bond_risk_evidence`.
- Preserved source provenance assertions and added explicit checks that provenance behavior remains unchanged.
- Added a local monkeypatch test proving non-bond fake extraction reaches the not-applicable missing field and does not scan seven bond-risk evidence groups.

## Validation Results

- `uv run pytest tests/fund/test_data_extractor.py -q`
  - Result: passed, `8 passed in 0.73s`
- `uv run ruff check fund_agent/fund/data_extractor.py tests/fund/test_data_extractor.py`
  - Result: passed, `All checks passed!`

## Residual Risks

- Direct `StructuredFundDataBundle(...)` test fixtures outside this slice now receive a default missing `bond_risk_evidence` field instead of production extraction. This is intentional for compatibility, but downstream snapshot/score slices must decide how to project or consume explicit positive evidence.
- Slice 3 only wires the bundle. Snapshot projection, scoring behavior, quality-gate projection, and real `006597` validation remain future slices.
- The non-bond guard is verified with local monkeypatching of the first group extractor; broader seven-group behavior remains covered by Slice 2 extractor tests.
