# Gate 2 Implementation Review: Core Analyze/Checklist Reliability Hardening

> Date: 2026-05-27
> Reviewer: AgentMiMo (code review specialist, not implementer)
> Baseline: `20f58144b7ab696544f0d82110442ee963c99ddf`
> Evidence: `docs/reviews/release-maintenance-core-analyze-checklist-reliability-hardening-implementation-evidence-20260527.md`
> Plan: `docs/reviews/release-maintenance-core-analyze-checklist-reliability-hardening-plan-20260527.md`

## Verdict: PASS

## Review Summary

All three Gate 2 slices are implemented within the accepted plan scope. 12 files changed (+433 / -12). Full test suite 746 passed, zero regressions. No boundary violations, no rule weakening, no tracked run artifacts.

---

## Slice 1: NAV unavailable/degraded handling

### Contract compliance

- `NavDataResult` extended with `unavailable: bool = False` and `unavailable_reason: str | None = None`. Defaults preserve existing successful shape. **PASS.**
- `unavailable_nav_data_result()` factory returns `records=[]`, `source="nav_unavailable"`, `cached=False`, explicit `unavailable=True` and reason. Input validation on empty strings. **PASS.**
- `_load_nav_data_or_unavailable()` is a module-level async helper catching `except Exception as exc` around exactly one call to `nav_provider.load_nav_data(...)`. Repository call (`load_annual_report`) remains outside the catch. **PASS.**
- `unavailable_reason` includes `f"{type(exc).__name__}: {exc}"`. **PASS.**

### Boundary verification

- `fund_agent/fund/template/` — zero diff. Renderer Chapter 3/5 untouched.
- `fund_agent/fund/documents/` — zero diff. `FundDocumentRepository` and PDF adapter untouched.
- `fund_agent/fund/quality_gate.py` — zero diff. FQ0-FQ6 rules untouched.
- `fund_agent/fund/extraction_score.py` — zero diff. Scoring untouched.
- `fund_agent/fund/analysis/` — zero diff. R=A+B-C untouched.
- `fund_agent/fund/extractors/` — zero diff. Extractor semantics untouched.

### Snapshot note

`extraction_snapshot.py:946-950` — appended `unavailable=True; reason=...` only when `nav_data.unavailable` is truthy. Existing `source/cached/records` note preserved. **PASS.**

### Tests

- `test_nav_data.py`: existing cache/fetch tests updated with `unavailable is False` / `unavailable_reason is None` assertions. New `test_unavailable_nav_data_result_returns_explicit_empty_result` validates factory with whitespace trimming. **PASS.**
- `test_data_extractor.py` (new file): fake repository + fake nav provider raising `RuntimeError("network down")`. Asserts extraction succeeds, annual-report fields populated, `bundle.nav_data.records == []`, `unavailable is True`, reason contains `RuntimeError`. Repository failure regression test asserts exception propagates without NAV call. **PASS.**
- `test_extraction_snapshot.py`: new `test_build_snapshot_records_preserves_unavailable_nav_reason` validates note contains `source=nav_unavailable`, `records=0`, `unavailable=True`, reason text. **PASS.**

### Findings

None.

---

## Slice 2: command_source run_id distinction

### Contract compliance

- `AnalyzeCommandSource = Literal["analyze", "checklist"]` defined. `FundAnalysisRequest.command_source` defaults to `"analyze"`. **PASS.**
- `FundAnalysisService.analyze()` uses `replace(request, command_source="analyze")` before `_run_analysis_core()`. **PASS.**
- `FundAnalysisService.checklist()` uses `replace(request, command_source="checklist")`. **PASS.**
- Service methods are authoritative — caller cannot override via request field. **PASS.**
- Explicit `quality_gate_run_id` preserved unchanged (not rewritten by `command_source`). **PASS.**
- `_default_quality_gate_run_id()` now takes `command_source` kwarg, returns `{command_source}-{fund_code}-{report_year}-{timestamp}`. **PASS.**
- `_validate_request()` rejects `command_source not in {"analyze", "checklist"}`. **PASS.**
- CLI `analyze` passes `command_source="analyze"`, `checklist` passes `command_source="checklist"`. **PASS.**
- No `extra_payload` or `developer_overrides` usage for `command_source`. **PASS.**

### Tests

- `test_fund_analysis_service_default_gate_run_id_does_not_overwrite`: updated with `output_dir.name.startswith("analyze-004393-2024-")`. **PASS.**
- `test_fund_analysis_service_checklist_default_gate_run_id_uses_checklist_prefix`: passes `command_source="analyze"` to `checklist()` method, asserts output starts with `checklist-`. Validates Service normalization. **PASS.**
- `test_fund_analysis_service_analyze_normalizes_command_source`: passes `command_source="checklist"` to `analyze()`, asserts output starts with `analyze-`. Validates Service authority. **PASS.**
- `test_fund_analysis_service_explicit_gate_run_id_remains_authoritative`: explicit `quality_gate_run_id="fixture-run"` through `checklist()`, asserts output dir is exactly `fixture-run`. **PASS.**
- `test_cli.py`: CLI analyze asserts `command_source == "analyze"`, checklist asserts `command_source == "checklist"`. **PASS.**

### Findings

None.

---

## Slice 3: pre-2026 turnover_rate regression lock

### Contract compliance

- No production changes to FQ0-FQ6, FQ4, R=A+B-C, or turnover extractor semantics. **PASS.**
- `turnover_rate` P1 failure remains `FQ2/warn` + `FQ2F/warn`, no `FQ4`, no block. **PASS.**

### Tests

- `test_quality_gate.py::test_run_quality_gate_warns_turnover_only_p1_failure_without_fq4`: score payload with only `turnover_rate` P1 fail, `missing_field_rate=0.01`. Asserts `status == warn`, issues include `FQ2/warn` and `FQ2F/warn`, no block issues, no `FQ4`. **PASS.**
- `test_fund_analysis_service.py::test_fund_analysis_service_pre_2026_missing_turnover_is_warn_not_standalone_block`: 2024 bundle with `turnover_rate=ExtractedField(value=None, extraction_mode="missing")`, all other fields present, `missing_field_rate < 20%`. Asserts `rabc_attribution.status == "missing"`, note contains `缺少 §8 换手率`, quality gate `warn`, FQ2/FQ2F warnings present, no FQ4. **PASS.**

### Findings

None.

---

## Boundary Audit

| Boundary | Expected | Actual |
|---|---|---|
| Renderer Chapter 3 / report writing | No changes | Zero diff |
| `FundDocumentRepository` / PDF adapter | No changes | Zero diff |
| `fund_agent/fund/quality_gate.py` | No changes | Zero diff |
| `fund_agent/fund/extraction_score.py` | No changes | Zero diff |
| `fund_agent/fund/analysis/` (R=A+B-C) | No changes | Zero diff |
| `fund_agent/fund/extractors/` | No changes | Zero diff |
| Host / Agent / dayu | No changes | Zero diff |
| FQ0-FQ6 rule semantics | No weakening | No changes |
| Tracked run artifacts | None added | None found |
| Commit / push / PR | None | None |

## Documentation

- `fund_agent/fund/README.md`: updated to describe NAV degradation behavior. **PASS.**
- `tests/README.md`: updated with `tests/fund/test_data_extractor.py` entry. **PASS.**
- Chinese docstrings retained in all new code. **PASS.**

## Validation

- `uv run pytest -q`: **746 passed in 1.65s** — zero regressions.
- `uv run ruff check .`: **All checks passed!**
- `git diff --check`: pass, no output.

## Residual Risks (acknowledged, not blocking)

1. `except Exception` around NAV is intentionally broad — may mask NAV provider programming errors. Mitigated by `unavailable_reason` including exception type + message.
2. Empty NAV records increase P2 `nav_data` missing signal in snapshot/score. Accepted — NAV is P2, gate goal is annual-report main path continuity.
3. Pre-2026 turnover can still contribute to aggregate FQ4 if many fields are missing. This gate intentionally does not weaken FQ4; separate field-applicability design gate if needed.
