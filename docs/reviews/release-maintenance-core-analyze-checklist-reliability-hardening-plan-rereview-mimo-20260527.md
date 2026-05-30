# Gate 2 Plan Re-Review: Core Analyze/Checklist Reliability Hardening

> **Reviewer**: AgentMiMo (review specialist, not implementer)
> **Review target**: `docs/reviews/release-maintenance-core-analyze-checklist-reliability-hardening-plan-20260527.md` (patched)
> **Prior review**: `docs/reviews/release-maintenance-core-analyze-checklist-reliability-hardening-plan-review-mimo-20260527.md`
> **Date**: 2026-05-27

---

## Finding Closure Verification

### F1 (Informational) — Service-authoritative `command_source` clarification

**Status: CLOSED.**

Line 148 now states: "Service methods are authoritative for `command_source`. CLI explicit construction is for readability and test observability only; if a direct caller passes `command_source="checklist"` to `analyze()`, Service normalizes the core run to `"analyze"`, and vice versa for `checklist()`."

Line 209 (Slice 2, step 8): "This is not the correctness boundary; Service method normalization remains authoritative."

The precedence is now unambiguous.

### F2 (Material) — Explicit `except Exception as exc` and repository/PDF catch-scope stop condition

**Status: CLOSED.**

Line 128 (NAV contract): "use `except Exception as exc:` around the single `load_nav_data(...)` call because provider, cache, akshare import, and external request failures have heterogeneous exception types. The stop condition is about catch scope: never move the repository call or annual-report extractors inside this catch block."

Line 174 (Slice 1, step 3): "implement that helper with `except Exception as exc:` around only `nav_provider.load_nav_data(...)`; `unavailable_reason` must include `f\"{type(exc).__name__}: {exc}\"`"

Line 188 (Slice 1, stop conditions): "If implementation needs to catch repository/PDF errors to make tests pass, stop and return to controller. This means the repository call has entered the wrong catch boundary; it does not mean the NAV-only catch should be narrowed below `Exception`."

Catch type, scope, reason format, and stop-condition semantics are all explicit.

### F3 (Material) — Concrete FQ4 decision procedure for turnover-only vs aggregate block

**Status: CLOSED.**

Line 251 (Slice 3, stop conditions): "run `uv run fund-analysis analyze 004393 --report-year 2024` under the default block policy. If it exits 2 with FQ4 block, inspect `quality_gate.json` and `score.json`: if `turnover_rate` is the only P1 failure and no P0 fields fail, return to controller because turnover may be driving an aggregate FQ4 false blocker; if multiple fields or any P0 fields fail, classify as designed aggregate data-quality block and do not change FQ4."

The implementation agent now has a concrete decision tree: which command to run, what artifact to inspect, which condition triggers "return to controller," and which condition triggers "accept as designed."

Line 240 (Slice 3, required tests) also tightened the service integration test: "Construct the bundle so all other fields are present enough to keep `missing_field_rate < 20%`; assert no `QualityGateBlockedError`... and does not include FQ4." This ensures the test isolates turnover_rate's individual contribution.

### F4 (Material) — `uv run` validation command convention

**Status: CLOSED.**

All test matrix and validation commands now use `uv run`:

- Line 257: `uv run pytest tests/fund/data/test_nav_data.py tests/fund/test_extraction_snapshot.py -q`
- Line 258: `uv run pytest tests/services/test_fund_analysis_service.py -q`
- Line 259: `uv run pytest tests/fund/test_quality_gate.py tests/fund/test_quality_gate_integration.py -q`
- Line 260: `uv run pytest tests/ui/test_cli.py -q`
- Line 273: `uv run ruff check .`
- Line 274: `uv run pytest -q`
- Lines 279-282: `uv run fund-analysis analyze/checklist 004393 ...`

Matches `.github/workflows/ci.yml` runner convention.

---

## Verdict

**PASS**

All four findings from the initial review are closed. The patched plan is ready for implementation handoff.
