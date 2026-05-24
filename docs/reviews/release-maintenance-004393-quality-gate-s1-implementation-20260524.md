# Release Maintenance 004393 Quality Gate S1 Implementation - 2026-05-24

## Gate

- Work unit: `004393/2024 quality gate block root-cause investigation`
- Accepted plan: `docs/reviews/release-maintenance-004393-quality-gate-plan-20260524.md`
- S0 judgment: `docs/reviews/release-maintenance-004393-quality-gate-evidence-controller-judgment-20260524.md`
- Slice: `S1 - P0 Extraction And Comparable Fields`
- Status: implemented, pending final verification

## Scope

Touched only the S1-approved files:

- `fund_agent/fund/extractors/profile.py`
- `tests/fund/extractors/test_profile.py`
- `tests/fund/test_extraction_snapshot.py`
- `docs/reviews/release-maintenance-004393-quality-gate-s1-implementation-20260524.md`

No golden answer rows, source CSV, README, runtime output, `fund_agent/host`, or `fund_agent/agent` files were modified.

## S0 Constraints Applied

- The accepted S0 judgment confirms `management_company`, `custodian`, and `inception_date` are available in annual report `§2`.
- The accepted S0 judgment confirms management fee `1.20%` and custody fee `0.20%` are available in `7.4.10.2` subsection text/tables.
- The accepted S0 judgment explicitly states parser section `§7` is absent and `7.4.10.2` appears under parser section `§5`, so the implementation does not depend on `get_section_text("§7")`.
- S1 does not claim source/fallback provenance beyond parser-visible same-source content, matching the S0 residual constraint.

## Implementation Summary

- `basic_identity` now includes:
  - `management_company`
  - `custodian`
  - `inception_date`
- These fields are extracted from `§2` text/table labels and keep field-level evidence anchors.
- `fee_schedule` still prefers direct `§2` management/custody fee labels.
- If either side is missing, fallback searches parser-visible `7.4.10.2.1 基金管理费` and `7.4.10.2.2 基金托管费` subsection/table semantics.
- Fallback extracts scalar rates such as `1.20%` and `0.20%` without preserving surrounding prose.
- Existing benchmark, index profile, and classification behavior is preserved by focused regression coverage.
- Snapshot comparable values now include the new `basic_identity` fields when present; no snapshot schema change was required because the whitelist already existed.

## Test Coverage Added

- `tests/fund/extractors/test_profile.py`
  - `§2` management company, custodian, inception date values and anchors.
  - `7.4.10.2` text fallback when parser `§7` is absent.
  - `7.4.10.2` table-semantics fallback.
  - `§2` direct fee values are not overwritten by fallback candidates.
  - Partial direct plus fallback combination.
  - No direct/fallback fee disclosure remains missing with a clear note.
- `tests/fund/test_extraction_snapshot.py`
  - Comparable `basic_identity` values include `management_company`, `custodian`, and `inception_date` when present.

## Verification Log

Commands run during implementation:

```bash
uv run pytest tests/fund/extractors/test_profile.py -q
```

Result: exit code `0`; `28 passed`.

```bash
uv run pytest tests/fund/test_extraction_snapshot.py -q
```

Result: exit code `0`; `6 passed`.

Final required verification commands are expected to be run after this artifact is written:

```bash
uv run pytest tests/fund/extractors/test_profile.py tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py -q
uv run ruff check fund_agent/fund/extractors/profile.py tests/fund/extractors/test_profile.py tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py
git diff --check
```

## Residual Risks

- Fallback section/page provenance is limited by parser-visible text/table metadata; this slice does not improve source metadata or prove refreshed-source provenance.
- Table fallback anchors use the parser table page/index when available, but section id may remain the parser-visible containing section rather than literal `§7`.
- Golden fee rows are intentionally not changed in S1; S4 still needs separate controller approval before correctness rows are updated.
