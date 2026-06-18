# EID Source Provenance Truth Alignment Plan Controller Judgment

日期：2026-06-11 13:07:44

Gate: `EID source provenance truth alignment gate`

Classification: `standard`

Plan: `docs/reviews/mvp-eid-source-provenance-truth-alignment-plan-20260611-130159.md`

Reviews:

- `docs/reviews/mvp-eid-source-provenance-truth-alignment-plan-review-mimo-20260611-130744.md`
- `docs/reviews/mvp-eid-source-provenance-truth-alignment-plan-review-ds-20260611-130744.md`

Verdict: `ACCEPT_WITH_AMENDMENTS`

## Controller Decision

Accept the amended plan. The next gate may proceed to bounded implementation using the accepted allowed write set.

## Accepted Scope

Implementation objective:

- Align public source provenance with current EID single-source truth.
- Add current public fields `selected_source`, `source_mode`, and `fallback_enabled`.
- Keep `source_strategy` only as a compatibility alias.
- Ensure current EID path does not emit `primary_then_fallback`.
- Propagate new fields to snapshot output and update Fund README package documentation.
- Correct stale EID source orchestrator wording only.

## Accepted Allowed Write Set

- `fund_agent/fund/source_provenance.py`
- `fund_agent/fund/extraction_snapshot.py`
- `fund_agent/fund/documents/sources.py`
- `fund_agent/fund/README.md`
- `tests/fund/test_source_provenance.py`
- `tests/fund/test_extraction_snapshot.py`
- `tests/fund/test_extraction_score.py`
- `tests/fund/test_data_extractor.py`

## Forbidden

- `docs/design.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- root `README.md`
- `pyproject.toml`
- `.gitignore`
- `fund_agent/fund/documents/repository.py`
- `fund_agent/fund/documents/cache.py`
- `fund_agent/fund/documents/models.py`
- live evidence / reports / golden / readiness artifacts
- live EID/network/PDF/FDR/provider/LLM/analyze/checklist/golden/readiness/release/PR commands

## Required Amendments For Implementation

- `fund_agent/fund/README.md` must describe v2 additive fields and state `source_strategy` is a compatibility alias, not fallback authorization.
- The current EID path negative assertion for `primary_then_fallback` is required, not optional.
- Static old-value check may only retain `primary_then_fallback` in that required negative assertion.
- If implementation requires changing `fund_agent/fund/documents/models.py`, stop and return to controller.

## Validation

Required validation:

- `uv run pytest tests/fund/test_source_provenance.py -q`
- `uv run pytest tests/fund/test_data_extractor.py -q`
- `uv run pytest tests/fund/test_extraction_snapshot.py -q`
- `uv run pytest tests/fund/test_extraction_score.py -q`
- focused combined fund tests from the plan
- targeted `uv run ruff check` from the plan
- `rg -n "primary_then_fallback" fund_agent tests --glob '*.py'`
- `rg -n "selected_source|source_mode|fallback_enabled|source_strategy" fund_agent/fund/README.md`
- `git diff --check`
- `git diff --name-only`

Optional if focused tests suggest shared readiness impact:

- `uv run pytest tests/fund/test_golden_readiness_preflight.py -q`

## Residuals

- `docs/design.md` may need a later design-truth-sync if implementation accepts v2 public snapshot fields. It is not modified in this gate.
- `AnnualReportSourceName` still includes `eastmoney`; this is deferred source-candidate/fallback design scope.

## Next Entry

Proceed to `EID source provenance truth alignment implementation gate`.
