# Gate 2 Targeted Re-Review: Core Analyze/Checklist Reliability Hardening Plan

> **Reviewer**: AgentGLM (review specialist, not implementer)
> **Date**: 2026-05-27
> **Review target**: `docs/reviews/release-maintenance-core-analyze-checklist-reliability-hardening-plan-20260527.md` (patched)
> **Prior review**: `docs/reviews/release-maintenance-core-analyze-checklist-reliability-hardening-plan-review-glm-20260527.md`
> **Verdict**: **PASS**

---

## Finding Closure Verification

### F1: command_source double-set clarification — CLOSED

| Aspect | Evidence |
|---|---|
| Authority statement | Line 148: "Service methods are authoritative for `command_source`. CLI explicit construction is for readability and test observability only; if a direct caller passes `command_source="checklist"` to `analyze()`, Service normalizes the core run to `"analyze"`, and vice versa." |
| CLI scope statement | Line 209: "This is not the correctness boundary; Service method normalization remains authoritative." |
| Conflict resolution | Explicit example: mismatched `command_source` is overridden by Service, not by CLI. |

**Assessment**: Authority chain is unambiguous. Service normalization is the correctness guarantee; CLI explicit construction is observability. Both converge to the same value in normal flow; mismatch is handled deterministically. No residual ambiguity.

---

### F2: turnover test bundle / FQ4 fragility — CLOSED

| Aspect | Evidence |
|---|---|
| Test construction constraint | Line 240: "Construct the bundle so all other fields are present enough to keep `missing_field_rate < 20%`; ... quality gate includes P1/FQ2/FQ2F warning semantics and does not include FQ4." |
| FQ4 decision procedure | Line 251: Concrete decision tree — run smoke, inspect `quality_gate.json`/`score.json`, distinguish turnover-only P1 failure from multi-field/P0 aggregate block. If turnover is the sole P1 failure with no P0 failures, return to controller; otherwise classify as designed aggregate block. |
| Stop condition preserved | Line 250: "do not weaken FQ4 in this gate. Return to controller with evidence and propose a separate field-applicability design gate." |

**Assessment**: The test now has an explicit construction constraint (missing_field_rate < 20%) and a negative assertion (FQ4 not triggered). The concrete FQ4 decision procedure in the stop condition gives the implementation agent a deterministic triage path. This resolves the fragility concern completely.

---

### F3: uv run command convention — CLOSED

| Aspect | Evidence |
|---|---|
| Test matrix | Lines 257-260: All four `pytest` commands use `uv run pytest` prefix. |
| Project validation | Line 273: `uv run ruff check .`; Line 274: `uv run pytest -q`. |
| Smoke commands | Lines 279-282: All four smoke commands use `uv run fund-analysis` prefix. |

**Assessment**: Every execution command in the test matrix, project validation, and smoke sections uses `uv run`. Fully consistent with project convention.

---

### F4: 2024 vs 2025 smoke expectations split — CLOSED

| Aspect | Evidence |
|---|---|
| 2024 expectations | Line 286: "2024 analyze/checklist commands exit 0 and preserve the accepted release-readiness baseline: `quality_gate_status: warn`, not a correctness block." |
| 2025 expectations | Line 287: "2025 analyze/checklist commands exit 0; missing same-year golden coverage remains `year_not_covered` / `FQ0/info`, not FQ1 mismatch from 2024 golden." |
| Cross-cutting | Line 288: "Quality gate artifacts for analyze/checklist have distinguishable run_id/path prefixes: `analyze-...` vs `checklist-...`." |

**Assessment**: 2024 and 2025 expectations are now split with specific exit codes, gate statuses, and golden coverage semantics. The 2025 expectation correctly states `year_not_covered` / `FQ0/info` and explicitly notes it should NOT become FQ1 mismatch from 2024 golden. This matches the accepted Gate 1 commit `20f5814` behavior.

---

### F5: fund_agent/fund/README.md sync check — CLOSED

| Aspect | Evidence |
|---|---|
| NavDataResult check | Line 293: "update `fund_agent/fund/README.md` only if it currently documents `NavDataResult` fields or NAV failure behavior" |
| Explicit fund README obligation | Line 294: "implementation must explicitly check `fund_agent/fund/README.md` for NAV / `StructuredFundDataBundle` / `NavDataResult` wording and update it if the new degraded contract is part of the current Fund package behavior." |

**Assessment**: Both the conditional check and the explicit implementation obligation are present. The wording covers `NavDataResult` fields, `StructuredFundDataBundle`, and the new degraded contract. Consistent with AGENTS.md documentation sync rule: `fund_agent/fund/` modification triggers `fund_agent/fund/README.md` review.

---

## New Content Review

The patch introduced additional material beyond the F1-F5 fixes. Reviewed for correctness:

| New content | Lines | Assessment |
|---|---|---|
| Broad `except Exception` rationale | 128, 174 | Correctly explains WHY the catch is broad (heterogeneous NAV exception types) and WHAT the stop condition guards (scope, not narrowing). Consistent with Risks §. |
| `unavailable_reason` format requirement | 174 | `f"{type(exc).__name__}: {exc}"` is a concrete, parseable format. Supports diagnostic observability without leaking sensitive details. |
| Concrete FQ4 decision procedure | 251 | Adds a deterministic triage path: smoke → inspect JSON → classify as turnover-only or aggregate. Does not smuggle FQ4 weakening. Correct. |

No new issues introduced by the patches.

---

## Verdict

**PASS**

All five findings (F1-F5) are fully closed. The patched plan is code-generation-ready with no residual concerns. No new issues were introduced by the patches.
