# Gate 2 Plan Review: Core Analyze/Checklist Reliability Hardening

> **Reviewer**: AgentMiMo (review specialist, not implementer)
> **Review target**: `docs/reviews/release-maintenance-core-analyze-checklist-reliability-hardening-plan-20260527.md`
> **Truth sources**: `AGENTS.md`, `docs/design.md` v2.2, `docs/implementation-control.md` Startup Packet / Current gate / Next entry point, HEAD `20f5814`
> **Date**: 2026-05-27

---

## 1. Gate 2 Scope Coverage

| Scope requirement | Plan covers? | Evidence |
|---|---|---|
| NAV external failure degradation | Yes | Slice 1, Candidate B analysis, root-cause evidence section |
| pre-2026 turnover_rate warn/degradation | Yes | Slice 3, root-cause evidence section |
| analyze/checklist artifact run_id distinction | Yes | Slice 2, Candidate D analysis, root-cause evidence section |

All three scope items from the Next Entry Point are addressed.

---

## 2. Root-Cause Evidence and Line References

### 2.1 NAV failure blocks annual-report extraction

**Plan claim**: `data_extractor.py:161-166` loads repository then NAV sequentially; NAV exception blocks all subsequent extractors.

**Verification**: CONFIRMED. Current code at `data_extractor.py:161-170`:
```python
report = await self._repository.load_annual_report(...)   # 161-165
nav_data = await self._nav_provider.load_nav_data(...)     # 166
profile_result = extract_profile(report)                    # 167
performance_result = extract_performance(report)            # 168
...
```
NAV call is sequential and unguarded; any exception propagates and blocks extractors.

### 2.2 NavDataResult has no unavailable fields

**Plan claim**: `nav_data.py:99-113` defines `NavDataResult` with only `fund_code`, `records`, `source`, `cached`.

**Verification**: CONFIRMED. `nav_data.py:99-113` matches exactly.

### 2.3 Renderer Chapter 5 uses `len(nav_data.records)`

**Plan claim**: `renderer.py:1295-1308` reads `len(nav_data.records)`; empty records are compatible.

**Verification**: CONFIRMED. `renderer.py:1295`: `nav_count = len(input_data.structured_data.nav_data.records)`. Empty list yields `0`, which renders as `净值记录 0 条` — degraded but not broken.

### 2.4 Snapshot `_build_nav_record()` handles empty records

**Plan claim**: `extraction_snapshot.py:946-964` reads `source`, `cached`, `records`; empty records produce `extraction_mode="missing"`.

**Verification**: CONFIRMED. Line 959: `extraction_mode=_EXTRACTION_MODE_DIRECT if value_present else _EXTRACTION_MODE_MISSING`.

### 2.5 FQ2/FQ2F P1 fail is warn, not block

**Plan claim**: `quality_gate.py:563-601` and `quality_gate.py:625-649` show P1 fail → `SEVERITY_WARN`, P0 fail → `SEVERITY_BLOCK`.

**Verification**: CONFIRMED. Lines 563-575: P0 fail → block. Lines 589-601: P1 fail → warn. Lines 625-638: FQ2F P0 → block. Lines 639-649: FQ2F P1 → warn.

### 2.6 `_default_quality_gate_run_id` always uses `analyze-` prefix

**Plan claim**: `fund_analysis_service.py:928-942` returns `f"analyze-{fund_code}-{report_year}-{timestamp}"`.

**Verification**: CONFIRMED. Line 942 exactly matches.

### 2.7 FQ4 missing_field_rate can block at ≥35%

**Plan claim**: FQ4 blocks when `missing_field_rate >= 0.35`.

**Verification**: CONFIRMED. `quality_gate.py:747`: `if missing_field_rate >= FQ4_BLOCK_MISSING_FIELD_RATE` (0.35). This means if turnover_rate is one of many missing fields, FQ4 can still block even though turnover_rate itself is only P1/warn.

### 2.8 Candidate B direct evidence

**Plan claim**: `data_extractor.py:161-166` is the correct catch point for NAV-only degradation.

**Verification**: CONFIRMED. The repository load (161-165) is before the NAV call (166), and extractors (167-170) are after. Catching only around line 166 preserves repository fail-closed.

---

## 3. Architecture Boundary Check

| Boundary | Violated? | Notes |
|---|---|---|
| No renderer Chapter 3 changes | No | Plan explicitly excludes renderer changes |
| No Host/Agent/dayu | No | No Host/Agent package creation or dayu dependency |
| No `FundDocumentRepository` / source fallback policy change | No | Plan explicitly preserves repository fail-closed; catch scope is NAV-only |
| No FQ0-FQ6 weakening | No | Plan explicitly states no FQ rule changes |
| No `extra_payload` | No | `command_source` is an explicit typed field on `FundAnalysisRequest` |

---

## 4. Minimality of `command_source` Field and Service/CLI Changes

The plan proposes:
- `AnalyzeCommandSource = Literal["analyze", "checklist"]`
- `command_source: AnalyzeCommandSource = "analyze"` on `FundAnalysisRequest`
- Service `analyze()` normalizes to `"analyze"`, `checklist()` normalizes to `"checklist"`
- `_default_quality_gate_run_id(structured_data, command_source)` uses the source

This is minimal and explicit. The current `FundAnalysisRequest` already has `mode`, `developer_overrides`, and quality gate fields — adding one more typed field is consistent. The CLI currently constructs `FundAnalysisRequest` directly in both `analyze` (line 210) and `checklist` (line 289); adding `command_source` to each is a one-line change.

**Finding F1 (informational)**: The plan says "CLI should pass `command_source`" but also says "Service methods normalize their own source." The preferred implementation is: Service `analyze()` always forces `command_source="analyze"` regardless of what the caller passes, and `checklist()` always forces `"checklist"`. This means CLI setting it is purely for observability/test, not for correctness. The plan should clarify this precedence explicitly to avoid future confusion about whether CLI or Service is authoritative.

---

## 5. NAV Contract Challenge

### 5.1 Optional fields on `NavDataResult`

The plan adds `unavailable: bool = False` and `unavailable_reason: str | None = None` with defaults that preserve existing successful shape. This is backward-compatible:
- Existing callers reading `source`, `cached`, `records` are unaffected.
- `_build_nav_record()` only reads `source`, `cached`, `records` — unaffected.
- Renderer Chapter 5 only reads `len(records)` — unaffected.

### 5.2 Catch scope

The plan specifies catching only around `self._nav_provider.load_nav_data(...)`, not around `self._repository.load_annual_report(...)`. This preserves repository fail-closed for `identity_mismatch`, `integrity_error`, `schema_drift`.

**Finding F2 (material)**: The plan says "catches `Exception` around NAV only" but does not specify whether the catch should be a bare `except Exception` or a narrower exception type. The plan's Risk section acknowledges this is "intentionally broad" because it must cover provider, cache, akshare, and external fetch failures. However, the stop condition says "If implementation needs to catch repository/PDF errors to make tests pass, stop." This creates ambiguity: should the implementation agent catch `Exception` (broad) or enumerate specific exception types (narrow)?

Recommendation: The plan should explicitly state `except Exception` as the catch type for the single `load_nav_data` call, with `unavailable_reason` including `type(exc).__name__` for diagnostics. This matches the plan's stated goal of covering all NAV failure modes. The stop condition about repository/PDF errors is about scope (don't wrap the repository call), not about exception narrowing.

### 5.3 Snapshot behavior

The plan says to append `unavailable={nav_data.unavailable}` and `reason={nav_data.unavailable_reason}` to the snapshot note when unavailable. The current note format is `source={source}; cached={cached}; records={len(records)}`. The plan should specify whether the unavailable/reason fields are appended to the existing note or replace it.

---

## 6. Turnover_rate Plan Challenge

### 6.1 Test-only locking

The plan proposes tests to lock the current behavior: P1 fail → warn, R=A+B-C missing → status="missing", manager extractor → `extraction_mode="missing"`. This is the right approach — no production code change needed unless smoke reveals a blocker.

### 6.2 FQ4 blocking risk

**Finding F3 (material)**: The plan correctly identifies that FQ4 missing_field_rate could still block if turnover_rate is one of many missing fields. The plan says "do not weaken FQ4 in this gate" and proposes returning to controller with evidence. However, the plan does not specify what evidence the implementation agent should collect to determine if FQ4 is actually blocking for pre-2026 bundles. The implementation agent needs a concrete decision procedure:

1. Run `fund-analysis analyze 004393 --report-year 2024 --quality-gate-policy block` (already in smoke commands).
2. If it exits 0, FQ4 is not blocking for this bundle.
3. If it exits 2 with FQ4 block, check whether the block is solely due to turnover_rate or due to multiple missing fields.
4. If solely due to turnover_rate, return to controller. If due to multiple fields, FQ4 is working as designed.

The plan should add this decision procedure to Slice 3's stop conditions.

### 6.3 `fund_quality` paths

The plan does not explicitly address whether `fund_quality` (FQ2F) can block on turnover_rate. FQ2F P1 fail is warn (confirmed above), so FQ2F alone cannot block on turnover_rate. However, FQ2F P0 fail can block — and if turnover_rate is the only P1 field failing, FQ2F P1 is warn. This is consistent with the plan's claim.

---

## 7. Validation Commands

**Finding F4 (material)**: The plan's Full Test Matrix uses `python -m pytest` and `python -m ruff check .`, but the project's CI (`.github/workflows/ci.yml`) uses `uv run pytest` and `uv run ruff check .`. The plan should use `uv run` to match the project's runner convention. The smoke commands (`fund-analysis analyze/checklist`) are correct as-is since they use the CLI entry point directly.

Required change:
- `python -m pytest ...` → `uv run pytest ...`
- `python -m ruff check .` → `uv run ruff check .`
- `python -m pytest` (project validation) → `uv run pytest`

---

## 8. Summary of Findings

| ID | Severity | Category | Finding |
|---|---|---|---|
| F1 | Informational | command_source | Clarify that Service methods are authoritative for `command_source`, CLI setting is for observability only |
| F2 | Material | NAV catch scope | Explicitly state `except Exception` as the catch type for the single `load_nav_data` call; clarify the stop condition is about scope (not wrapping repository), not about exception narrowing |
| F3 | Material | turnover_rate / FQ4 | Add concrete decision procedure for implementation agent to determine if FQ4 is blocking solely due to turnover_rate vs multiple missing fields |
| F4 | Material | validation commands | Change `python -m pytest` / `python -m ruff` to `uv run pytest` / `uv run ruff` to match CI runner convention |

---

## 9. Verdict

**PASS_WITH_FINDINGS**

The plan satisfies Gate 2 scope, preserves all architecture boundaries, and provides direct root-cause evidence with accurate line references. Four findings require plan changes before implementation:

1. **F1**: Clarify Service-authoritative `command_source` precedence (informational, no code change needed).
2. **F2**: Explicitly state `except Exception` catch type for `load_nav_data` and clarify stop condition scope.
3. **F3**: Add FQ4 blocking decision procedure for the implementation agent.
4. **F4**: Change validation commands from `python -m` to `uv run`.

---

## 10. Required Plan Changes

### Required (must fix before implementation):

1. **Slice 1, step 3**: Change "catches `Exception` around NAV only" to explicitly state `except Exception as exc:` around the single `self._nav_provider.load_nav_data(...)` call, with `unavailable_reason` including `f"{type(exc).__name__}: {exc}"`. Clarify that the stop condition about repository/PDF errors means "do not wrap the repository call in the catch block," not "use a narrower exception type."

2. **Slice 3, stop conditions**: Add: "If `fund-analysis analyze 004393 --report-year 2024 --quality-gate-policy block` exits 2 with FQ4 block, inspect the FQ4 issue's `observed_rate` and `threshold`. If the missing_field_rate is at or near 0.35 and `turnover_rate` is listed in `p1_failed_fields` but no P0 fields are failing, return to controller with the FQ4 issue details as evidence that turnover_rate alone may be contributing to FQ4 block."

3. **Full Test Matrix / Project validation**: Replace all `python -m pytest` with `uv run pytest` and `python -m ruff check .` with `uv run ruff check .` to match `.github/workflows/ci.yml` runner convention.

### Recommended (informational, no blocking):

4. **Slice 2, step 8 / contract**: Add a note: "Service `analyze()` and `checklist()` are authoritative for `command_source`; CLI explicit construction is for test observability and readability, not for correctness. If a caller passes `command_source="checklist"` to `analyze()`, the Service normalizes it to `"analyze"`."
