# EID Source Provenance Truth Alignment Implementation Evidence

日期：2026-06-11 13:12:50

Gate: `EID source provenance truth alignment implementation gate`

Plan: `docs/reviews/mvp-eid-source-provenance-truth-alignment-plan-20260611-130159.md`

Controller judgment: `docs/reviews/mvp-eid-source-provenance-truth-alignment-plan-controller-judgment-20260611-130744.md`

## Implementation Summary

Aligned public source provenance with current EID single-source truth without changing source acquisition or fallback behavior.

Changed:

- `fund_agent/fund/source_provenance.py`
  - schema version updated to `repository_source_provenance.v2`
  - added public fields `selected_source`, `source_mode`, `fallback_enabled`
  - retained `source_strategy` as compatibility alias only
  - current EID metadata path emits `single_source_only`
  - metadata-absent / legacy paths emit `legacy_or_unknown`
  - no current policy is inferred from `resolved_source_name`
- `fund_agent/fund/extraction_snapshot.py`
  - snapshot records now copy `selected_source`, `source_mode`, `fallback_enabled`
  - Source Provenance summary table includes current policy fields
  - failed-fund omission wording updated to Source Provenance v2
- `fund_agent/fund/documents/sources.py`
  - fixed stale `AnnualReportSourceOrchestrator.__init__` docstring wording only
- `fund_agent/fund/README.md`
  - documents v2 additive provenance fields and `source_strategy` compatibility alias
- focused tests updated for v2 fields and current EID negative assertion.

Not changed:

- no Eastmoney / fund-company / CNINFO fallback re-entry
- no source expansion, multi-source orchestrator, repository/cache/downloader behavior, metadata model, readiness/golden promotion, renderer, FQ0-FQ6, CLI, Service, Host or Agent runtime changes
- no live EID/network/PDF/FDR/provider/LLM/analyze/checklist/golden/readiness/release/PR command

## Validation

| Check | Result |
|---|---|
| `uv run pytest tests/fund/test_source_provenance.py -q` | PASS, 19 passed |
| `uv run pytest tests/fund/test_data_extractor.py -q` | PASS, 10 passed |
| `uv run pytest tests/fund/test_extraction_snapshot.py -q` | PASS, 13 passed |
| `uv run pytest tests/fund/test_extraction_score.py -q` | PASS, 55 passed |
| `uv run pytest tests/fund/test_source_provenance.py tests/fund/test_data_extractor.py tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py -q` | PASS, 97 passed |
| targeted `uv run ruff check ...` from plan | PASS |
| `rg -n "primary_then_fallback" fund_agent tests --glob '*.py'` | only required current EID negative assertion test remains |
| `rg -n "selected_source\|source_mode\|fallback_enabled\|source_strategy" fund_agent/fund/README.md` | shows EID policy line and v2 provenance wording |
| `git diff --check` | PASS |
| `git diff --name-only` | only accepted implementation write set |

## Current Diff Scope

Accepted implementation files:

- `fund_agent/fund/source_provenance.py`
- `fund_agent/fund/extraction_snapshot.py`
- `fund_agent/fund/documents/sources.py`
- `fund_agent/fund/README.md`
- `tests/fund/test_source_provenance.py`
- `tests/fund/test_data_extractor.py`
- `tests/fund/test_extraction_snapshot.py`
- `tests/fund/test_extraction_score.py`

New evidence/control artifacts for this gate:

- `docs/reviews/mvp-eid-source-provenance-truth-alignment-plan-20260611-130159.md`
- `docs/reviews/mvp-eid-source-provenance-truth-alignment-plan-review-mimo-20260611-130744.md`
- `docs/reviews/mvp-eid-source-provenance-truth-alignment-plan-review-ds-20260611-130744.md`
- `docs/reviews/mvp-eid-source-provenance-truth-alignment-plan-controller-judgment-20260611-130744.md`
- `docs/reviews/mvp-eid-source-provenance-truth-alignment-implementation-evidence-20260611.md`

## Residuals

- `docs/design.md` still contains historical/current public snapshot v1 wording and should be handled by a later design-truth-sync/control update after controller acceptance.
- `AnnualReportSourceName` still includes `eastmoney`; this remains deferred source-candidate/fallback design scope and was not changed.
- `golden_readiness_preflight.py` was not modified. Existing readiness fallback field semantics remain unchanged because `fallback_used`, `primary_failure_category`, `fallback_eligibility`, and `source_provenance_status` are still present.
