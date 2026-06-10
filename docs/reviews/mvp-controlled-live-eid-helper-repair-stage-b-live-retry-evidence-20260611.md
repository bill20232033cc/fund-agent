# Controlled Live EID Helper Repair Stage B Live Retry Evidence - 2026-06-11

## Scope

This artifact records the separately authorized Stage B controlled live retry after the accepted Stage A no-live helper repair.

Authorized command, executed exactly once:

```bash
uv run python scripts/controlled_live_eid_failure_branch_observation.py
```

Target is fixed by the script constants:

- `FUND_CODE = "006597"`
- `REPORT_YEAR = 2024`

## Boundary

This gate did not authorize and did not run:

- retry of the helper command
- additional fund/year rows
- fallback or non-EID sources
- provider / LLM / endpoint / DNS / curl / socket probes
- extractor / `analyze` / `checklist`
- renderer / quality gate
- fixture projection / golden / readiness promotion
- score-loop
- release / push / PR / merge

## Observed Command Result

Exit code: `0`

Stdout was one parseable JSON line:

```json
{"discovery_contract_version": "eid_annual_report_discovery.v1", "document_kind": "annual_report", "fallback_enabled": false, "fallback_used": false, "fund_code": "006597", "parsed_cache_hit": false, "pdf_cache_hit": false, "primary_failure_category": null, "raw_text_length": 61510, "report_year": 2024, "section_count": 8, "selected_source": "eid", "source": "eid", "source_metadata_present": true, "source_mode": "single_source_only", "status": "success", "table_count": 85}
```

No stderr was emitted by the command.

## Evidence Classification

Classification: `accepted_live_window_no_failure_observed`.

Basis:

- command exit code was `0`
- stdout was parseable safe JSON
- JSON target identity is `fund_code="006597"` and `report_year=2024`
- JSON status is `success`
- source policy fields remained EID single-source:
  - `source="eid"`
  - `selected_source="eid"`
  - `source_mode="single_source_only"`
  - `fallback_enabled=false`
  - `fallback_used=false`
- `primary_failure_category=null`
- helper returned only safe scalar summary fields and did not emit PDF bytes, raw response, full raw text or full table content

## Interpretation

This Stage B result proves only that the controlled helper's current live window for `006597 / 2024` completed without observing an EID acquisition failure branch after the Stage A serializer repair.

It does not prove:

- all modeled EID failure branches occurred live
- broader EID availability for other funds or years
- fallback behavior
- non-EID source behavior
- extractor correctness
- golden/readiness promotion
- provider/LLM behavior

Accepted no-live checkpoint `ac6bbe9` remains the accepted code-behavior proof for the modeled EID failure categories:

- `not_found`
- `unavailable`
- `schema_drift`
- `identity_mismatch`
- `integrity_error`

The previous evidence checkpoint `ebcd3bf` remains a historical blocked helper-serialization record, not accepted live success or live failure-branch proof.

## Residuals

- No live EID failure branch was observed in this single live window.
- `docs/design.md` stale wording about identity/integrity metadata remains a deferred docs-sync candidate and must not override current code/control truth.
- Broader live evidence, if needed, requires a new reviewed and separately authorized controlled live gate.
