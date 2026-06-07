# Gate 2 Implementation Evidence: Core Analyze/Checklist Reliability Hardening

> Date: 2026-05-27
> Role: AgentCodex implementation specialist, not controller
> Approved plan: `docs/reviews/release-maintenance-core-analyze-checklist-reliability-hardening-plan-20260527.md`
> Controller judgment: `docs/reviews/release-maintenance-core-analyze-checklist-reliability-hardening-plan-controller-judgment-20260527.md`
> Baseline: `20f58144b7ab696544f0d82110442ee963c99ddf`

## Self-Check

- Self-check: pass.
- Implemented only the accepted Gate 2 minimal slices.
- Did not commit, push, create PR, mutate GitHub state, or add tracked run artifacts.
- Did not modify renderer Chapter 3, `report_writing_audit`, Host/Agent/dayu, `FundDocumentRepository`, source helpers, annual-report fallback policy, or FQ0-FQ6 rule semantics.

## Changed Files

- `fund_agent/fund/data/nav_data.py`
- `fund_agent/fund/data_extractor.py`
- `fund_agent/fund/extraction_snapshot.py`
- `fund_agent/services/fund_analysis_service.py`
- `fund_agent/ui/cli.py`
- `fund_agent/fund/README.md`
- `tests/README.md`
- `tests/fund/data/test_nav_data.py`
- `tests/fund/test_data_extractor.py`
- `tests/fund/test_extraction_snapshot.py`
- `tests/fund/test_quality_gate.py`
- `tests/services/test_fund_analysis_service.py`
- `tests/ui/test_cli.py`

## Implemented Items

### Slice 1: NAV unavailable/degraded handling

- Extended `NavDataResult` with compatible optional fields:
  - `unavailable: bool = False`
  - `unavailable_reason: str | None = None`
- Added `unavailable_nav_data_result(...)` factory returning `records=[]`, `source="nav_unavailable"`, `cached=False`, and explicit unavailable reason.
- Added `FundDataExtractor` boundary helper that catches `except Exception as exc` only around `nav_provider.load_nav_data(...)`.
- Kept `FundDocumentRepository.load_annual_report(...)` and annual-report extractors outside the NAV catch boundary.
- Updated snapshot NAV note to preserve `source/cached/records` and append `unavailable=True; reason=...` only on degraded NAV.

### Slice 2: analyze/checklist command source for default run_id

- Added explicit `AnalyzeCommandSource = Literal["analyze", "checklist"]`.
- Added `FundAnalysisRequest.command_source`, defaulting to `"analyze"`.
- Made `FundAnalysisService.analyze()` normalize to `"analyze"` and `FundAnalysisService.checklist()` normalize to `"checklist"` before running the shared core.
- Preserved explicit `quality_gate_run_id` as authoritative.
- Changed default quality gate run_id to `{command_source}-{fund_code}-{report_year}-{timestamp}`.
- CLI now constructs requests with explicit `command_source` for readability and test observability; Service remains the correctness boundary.

### Slice 3: pre-2026 turnover regression lock

- Added focused quality gate test proving `turnover_rate`-only P1 failure produces `FQ2/warn` and `FQ2F/warn`, with no FQ4 and no block.
- Added Service test proving 2024 missing `turnover_rate` yields R=A+B-C `missing` note and quality gate warn, not standalone hard block.
- No production changes to FQ0-FQ6, FQ4, R=A+B-C, or turnover extractor semantics were needed.
- During test development, a temporary 004393 fixture produced FQ1 correctness block due golden mismatch; this was classified as non-turnover and fixed by isolating the turnover-only test with a local selected CSV and no golden answer.

## Validation

Required focused validation:

- `uv run pytest tests/fund/data/test_nav_data.py tests/fund/test_extraction_snapshot.py -q`
  - Result: `10 passed in 0.61s`
- `uv run pytest tests/fund/test_data_extractor.py -q`
  - Result: `2 passed in 0.58s`
- `uv run pytest tests/services/test_fund_analysis_service.py -q`
  - Result: `31 passed in 0.51s`
- `uv run pytest tests/fund/test_quality_gate.py tests/fund/test_quality_gate_integration.py -q`
  - Result: `29 passed in 0.51s`
- `uv run pytest tests/ui/test_cli.py -q`
  - Result: `39 passed in 0.73s`
- `uv run ruff check .`
  - Result: `All checks passed!`
- `git diff --check`
  - Result: pass, no output.

Additional validation:

- `uv run pytest -q`
  - Result: `746 passed in 1.54s`

## Documentation Decision

- Updated `fund_agent/fund/README.md` because Fund package behavior now explicitly degrades NAV provider/cache/akshare failures into `NavDataResult(unavailable=True, records=[])`.
- Updated `tests/README.md` because a new focused `tests/fund/test_data_extractor.py` file was added.
- Did not update root `README.md`; no user-facing CLI flags or user workflow changed.
- Did not update `fund_agent/README.md`; it does not enumerate the full `FundAnalysisRequest` field set and no architecture boundary changed.
- Did not update `docs/design.md`; implementation stayed within the accepted plan and current design boundary.

## Residual Risks

- NAV degraded empty records remain visible as missing `nav_data` in snapshot/score. This is accepted by the plan because `nav_data` is P2 and the goal is annual-report main path continuity.
- NAV catch is intentionally broad around one provider call. It may convert unexpected NAV provider programming errors to unavailable data, but the reason includes exception type and message.
- `command_source` is normalized by Service methods, so direct callers cannot force checklist naming through `analyze()` or analyze naming through `checklist()`. Invalid request values are still rejected in validation when they reach the core.
- pre-2026 turnover can still contribute to aggregate FQ4 if many fields are missing. This gate intentionally did not weaken FQ4; any future false blocker should be handled in a separate field-applicability design gate.

## Boundary Confirmation

- No renderer Chapter 3 or report writing audit changes.
- No Host/Agent/dayu changes.
- No `FundDocumentRepository`, PDF adapter, source helper, or fallback policy changes.
- No FQ0-FQ6 rule semantic changes.
- No report-quality validator integration changes.
- No durable fixtures or tracked run artifacts added.
- No commit, push, PR, merge, approval, branch deletion, external comment, or issue mutation performed.
