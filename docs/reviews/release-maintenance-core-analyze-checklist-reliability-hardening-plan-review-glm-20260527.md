# Gate 2 Independent Plan Review: Core Analyze/Checklist Reliability Hardening

> **Reviewer**: AgentGLM (review specialist, not implementer)
> **Date**: 2026-05-27
> **Review target**: `docs/reviews/release-maintenance-core-analyze-checklist-reliability-hardening-plan-20260527.md`
> **Truth sources**: `AGENTS.md`, `docs/design.md` (v2.2), `docs/implementation-control.md` Startup Packet / Current gate / Next entry point, accepted Gate 1 commit `20f5814`
> **Verdict**: **PASS_WITH_FINDINGS**

---

## Review Scope

Adversarial review focused on:

1. Plan code-generation readiness; no later-gate smuggling.
2. NAV degradation: catch scope, `NavDataResult` extension adequacy, source/cached/unavailable semantics stability.
3. `command_source`: minimal explicit contract vs. smaller alternative; risk to default `analyze`/`checklist` behavior.
4. `turnover_rate`: FQ0-FQ6 non-weakening proof; test sufficiency for turnover-only warn vs FQ4 aggregate block.
5. Testing/validation: command prefix, 004393 smoke precision.
6. README/design/control sync obligations.

---

## Source Verification

All plan-referenced code locations verified against HEAD `20f5814`:

| Plan claim | Verified code | Match |
|---|---|---|
| `NavDataResult` has 4 fields (`fund_code`, `records`, `source`, `cached`) | `nav_data.py:99-113` | ✅ |
| `StructuredFundDataBundle.nav_data` typed as `NavDataResult` (not optional) | `data_extractor.py:110` | ✅ |
| Repository load before NAV in `extract()` | `data_extractor.py:161-166` | ✅ |
| NAV call at line 166, extractors at 167-170 | `data_extractor.py:166-170` | ✅ |
| `FundAnalysisRequest` has no `command_source` field | `fund_analysis_service.py:156-181` | ✅ |
| `_default_quality_gate_run_id` hardcodes `"analyze-"` prefix | `fund_analysis_service.py:928-942` | ✅ |
| `analyze()` and `checklist()` both call `_run_analysis_core(request)` | `fund_analysis_service.py:434/486, 450/502` | ✅ |
| FQ2 P1 fail → `SEVERITY_WARN` | `quality_gate.py:589-601` | ✅ |
| FQ2F P1 fail → `SEVERITY_WARN` | `quality_gate.py:639-649` | ✅ |
| FQ4 warn ≥ 20%, block ≥ 35% | `quality_gate.py:40-41, 747-773` | ✅ |
| `_build_nav_record()` reads `source`, `cached`, `records`; empty → `extraction_mode="missing"` | `extraction_snapshot.py:946-964` | ✅ |

---

## Finding 1: NAV catch scope is correctly narrowed (PASS)

**Adversarial question**: Does extending `NavDataResult` suffice? Does catch scope risk masking repository/PDF failures?

**Assessment**:

- `NavDataResult` extension with `unavailable: bool = False` and `unavailable_reason: str | None = None` is backwards compatible. Existing callers see defaults matching current successful shape.
- `unavailable_nav_data_result()` factory provides a single construction point for degraded results, with `records=[]`, `source="nav_unavailable"`, `cached=False`, `unavailable=True`.
- Source/cached/unavailable semantics are stable and well-defined: success path preserves `source="nav_cache"/"akshare"`, `cached=True/False`, `unavailable=False`; degraded path uses a distinct `source` value.
- Plan explicitly requires repository load (`load_annual_report`) to remain **outside** any NAV catch boundary. Verified: `data_extractor.py:161-165` (repository) precedes `166` (NAV) and plan's `_load_nav_data_or_unavailable` helper wraps only the NAV call.
- Snapshot `_build_nav_record()` already handles empty records as `extraction_mode="missing"`; adding `unavailable`/`reason` to the note is additive.
- `StructuredFundDataBundle.nav_data` remains non-optional (`NavDataResult`, not `NavDataResult | None`), preserving renderer and downstream consumer assumptions.

**Verdict**: NAV degradation design is sound. No issues.

---

## Finding 2: `command_source` is the minimal explicit contract (PASS)

**Adversarial question**: Is adding `FundAnalysisRequest.command_source` the smallest change, or could it be smaller? Does it risk changing default behavior?

**Assessment**:

- Alternative `is_checklist: bool = False` would be technically smaller (one boolean vs. one Literal) but loses domain clarity and extensibility. `Literal["analyze", "checklist"]` is the right trade-off: minimal fields, explicit domain, readable in logs and test assertions.
- Default `command_source="analyze"` preserves backward compatibility for all existing callers who don't pass the field. No behavior change for `analyze`.
- `checklist()` normalizing to `command_source="checklist"` **does change** checklist run_id from `analyze-004393-2024-...` to `checklist-004393-2024-...`. This is the intended naming/observability change. It does NOT affect FQ0-FQ6 rule evaluation, block/warn policy, quality gate pass/fail, or `derive_final_judgment()` input.
- Explicit user-provided `quality_gate_run_id` remains authoritative and is not rewritten.
- `_validate_request()` rejecting invalid `command_source` values is a proper guard.

**Minor finding F1**: The plan says both (a) "CLI should pass `command_source=...` explicitly" and (b) "Service methods normalize their own source." This creates a potential double-set. **Recommendation**: Clarify in the plan that Service normalization is a safety net for direct programmatic callers (tests, future Host integration), while CLI explicit construction is for test observability. Both should converge to the same value; no semantic conflict.

**Verdict**: `command_source` is appropriate. F1 is non-blocking.

---

## Finding 3: Turnover plan correctly avoids weakening FQ0-FQ6 (PASS)

**Adversarial question**: Does the plan prove that pre-2026 missing turnover is not hard-blocking? Are tests sufficient to distinguish turnover-only warn from FQ4 aggregate block?

**Assessment**:

- Verified: `turnover_rate` is P1 (`extraction_score.py:41-58`, `design.md:730-735`).
- Verified: FQ2 P1 fail → `warn` (not `block`); FQ2F P1 fail → `warn` (not `block`). This is code-verified at `quality_gate.py:589-649`.
- Verified: R=A+B-C returns `status="missing"` and note when `turnover_rate` is unavailable, not an exception.
- Verified: Manager extractor returns `extraction_mode="missing"` for undisclosed turnover.
- Plan's primary decision ("no production code change") is correct given current code semantics.
- Plan's stop condition ("if pre-2026 missing turnover still blocks because total missing-field-rate triggers FQ4/block, do not weaken FQ4") is the right safety valve.

**Minor finding F2**: The plan's Service integration test constructs a bundle with `turnover_rate=missing` and asserts "no `QualityGateBlockedError`." This assertion may be fragile if the test bundle has **other** missing fields that collectively push the overall missing-field-rate above FQ4's 20% warn or 35% block threshold. **Recommendation**: The plan should explicitly note that the test bundle must be constructed so that overall missing-field-rate stays below 20% (i.e., only `turnover_rate` is missing, or total missing count keeps rate < 0.20), OR the test should assert specifically that FQ4 is not triggered while FQ2/FQ2F warn is present. This ensures the test distinguishes "turnover-only P1 warn" from "aggregate missing-field-rate block."

**Verdict**: Turnover handling is correct. F2 is non-blocking but should be addressed in implementation.

---

## Finding 4: Testing/validation commands and smoke precision (PASS_WITH_MINOR)

**Adversarial question**: Should commands use `uv run`? Are 004393 smoke expectations precise enough after Gate 1 `year_not_covered` behavior?

**Minor finding F3**: Test matrix commands use bare `python -m pytest` and `python -m ruff check`. Project execution convention (per `pyproject.toml` and established gate history) uses `uv run` as the execution wrapper. **Recommendation**: All commands should use `uv run` prefix: `uv run python -m pytest`, `uv run python -m ruff check`. Smoke commands should use `uv run fund-analysis analyze` / `uv run fund-analysis checklist`.

**Minor finding F4**: Smoke expectations say "Commands exit 0 or preserve already accepted Gate 1 behavior." After Gate 1 (commit `20f5814`), `year_not_covered` maps to `FQ0/info`. For 004393:

- `--report-year 2024`: golden exists → expect exit 0, `quality_gate_status: warn` (established release-readiness baseline).
- `--report-year 2025`: golden likely missing → expect exit 0, `year_not_covered` as `FQ0/info`, quality gate status `warn` or lower but not `block`.

**Recommendation**: Split the 4 smoke commands into two groups with explicit expected outcomes: (a) 2024 commands should match the accepted release-readiness baseline (exit 0, status warn); (b) 2025 commands should document the `year_not_covered` FQ0/info path without blocking.

**Verdict**: Testing framework is sound. F3 and F4 are non-blocking precision improvements.

---

## Finding 5: README/design/control sync obligations (PASS_WITH_MINOR)

**Adversarial question**: Does the plan correctly identify all documentation sync needs?

**Assessment**:

- `command_source` addition to `FundAnalysisRequest` changes a public Service contract type listed in `design.md` §2.3. Plan correctly identifies `fund_agent/README.md` may need update.
- Plan correctly defers `docs/design.md` update to post-implementation controller decision.
- Plan correctly says root `README.md` does not change (no new CLI flags).

**Minor finding F5**: Plan does not mention checking `fund_agent/fund/README.md` for the NavDataResult field changes (Slice 1 touches `fund_agent/fund/data/nav_data.py` and `fund_agent/fund/data_extractor.py`). Per AGENTS.md: `fund_agent/fund/` modification → update `fund_agent/fund/README.md`. If that README documents `NavDataResult` fields or NAV failure behavior, it should be updated. **Recommendation**: Add explicit check for `fund_agent/fund/README.md` in the Documentation Decision section.

**Verdict**: Documentation sync is mostly covered. F5 is non-blocking.

---

## Finding 6: No later-gate smuggling (PASS)

**Adversarial question**: Does the plan scope only what the control doc authorizes, or does it smuggle later gate work?

**Assessment**:

- Slice 1 allowed files: `nav_data.py`, `data_extractor.py`, `extraction_snapshot.py`, test files. No renderer, no Service, no Host/Agent. ✅
- Slice 2 allowed files: `fund_analysis_service.py`, `cli.py`, test files. No renderer, no Fund capability. ✅
- Slice 3 allowed files: quality gate tests, service tests, with optional narrow production change only if smoke requires. ✅
- Non-goals explicitly exclude: renderer Chapter 3, Host/Agent/dayu, `FundDocumentRepository`, source fallback strategy, FQ0-FQ6 weakening, tracked run artifacts, `extra_payload`. All match `docs/implementation-control.md` Next Entry Point constraints. ✅
- Plan's stop conditions correctly escalate to controller for any scope violation. ✅

**Verdict**: No smuggling detected.

---

## Findings Summary

| ID | Severity | Area | Summary | Required action |
|---|---|---|---|---|
| F1 | Informational | Slice 2 | Double-set of `command_source` by CLI and Service normalization | Clarify in plan: Service normalization is safety net; both converge to same value |
| F2 | Minor | Slice 3 | Turnover Service integration test may be fragile if bundle missing-field-rate exceeds FQ4 thresholds | Plan should require test bundle construction keeps missing-field-rate < 20%, or assert FQ4 not triggered |
| F3 | Minor | Test matrix | Commands should use `uv run` prefix for reproducibility | Update all test/smoke commands to use `uv run` |
| F4 | Minor | Smoke expectations | 2024 vs 2025 expected outcomes should be split with explicit assertions | Separate smoke expectations by year with specific exit/status expectations |
| F5 | Minor | Documentation | Missing check for `fund_agent/fund/README.md` sync after NavDataResult extension | Add explicit README sync check for fund package README |

---

## Verdict

**PASS_WITH_FINDINGS**

The plan is code-generation-ready. All six adversarial focus areas pass. No blocking findings. Five minor/informational findings should be addressed in the plan before implementation starts, but none warrants a BLOCK verdict:

- F1 (double-set clarification) and F2 (test bundle construction) should be patched into the plan text.
- F3 (`uv run` prefix) and F4 (smoke precision) should be corrected in the test matrix.
- F5 (fund README check) should be added to the Documentation Decision section.

None of the findings change the plan's core contracts, slice boundaries, or stop conditions.
