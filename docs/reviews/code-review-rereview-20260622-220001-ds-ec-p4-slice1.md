# Targeted Re-Review: EC-P4 Slice 1 Code Review Fix

## Gate

- Work unit: `Evidence Confirm Productionization EC-P4 Service/UI/renderer/quality-gate production integration`
- Gate: `targeted re-review` (deepreview)
- Classification: `heavy`
- Slice: `Slice 1 - Fund Summary + Quality Gate ECQ Projection`
- Branch: `evidence-confirm-productionization`
- Reviewer: AgentDS
- Timestamp: `2026-06-22 22:00 Asia/Shanghai`
- Release/readiness: `NOT_READY`

## Verdict

**PASS** — 7/7 accepted findings verified as 已修复. 0 unresolved findings. 0 blockers.

## Reviewed Artifacts

- `docs/reviews/code-review-20260622-214853-ds-ec-p4-slice1.md` (DS findings, 3 items)
- `docs/reviews/code-review-20260622-214853-mimo-ec-p4-slice1.md` (MiMo findings, 4 items)
- `docs/reviews/evidence-confirm-productionization-ec-p4-slice1-code-review-fix-20260622.md` (fix evidence)

## Fix Evidence: Current File State

- `fund_agent/fund/evidence_confirm_production.py` — 402 lines (+2: `_warning_issue_ids` extended, docstring updated)
- `fund_agent/fund/quality_gate_integration.py` — 370 lines (+3: `_ecq_policy_severity` guard, docstring updated)
- `tests/fund/test_evidence_confirm_production.py` — 348 lines (+6 tests)
- `tests/fund/test_quality_gate_integration.py` — 672 lines (+4 tests)

No Service/UI/renderer/CLI/control docs, repository/source/PDF/cache/provider/LLM module was modified by this fix gate.

## Finding Status Table

| Finding | Severity | Status | Evidence |
|---|---|---|---|
| DS-ECP4S1-01: `hard_gate.informational_issue_ids` dropped | HIGH | **已修复** | `_warning_issue_ids` L341–344 now extends with `hard_gate.informational_issue_ids`; field docstring L52 states 包含 reviewable 与 informational; `test_summary_from_repository_warn_keeps_reviewable_and_informational_ids` L101–136 asserts both IDs present |
| DS-ECP4S1-02: missing production summary tests | MEDIUM | **已修复** | +6 tests: pass summary (L71), warn summary with IDs (L101), 3 stable reason variants parametrized (L139–168), invalid reason rejection (L171), invalid policy rejection (L193), not_applicable→not_run boundary (L215) |
| DS-ECP4S1-03: `_ecq_policy_severity` off-policy silent downgrade | MEDIUM | **已修复** | `_ecq_policy_severity` L279–280 now raises `ValueError` for `policy="off"`; docstring L273–274 documents the raise; `test_quality_gate_integration_rejects_off_policy_fail_summary` L395–420 asserts `ValueError` |
| MiMo F-01: missing summary=None ECQ0 test | LOW | **已修复** | `test_quality_gate_integration_explicit_summary_none_produces_no_ecq_issues` L198–225 passes `evidence_confirm_summary=None` explicitly, asserts zero ECQ issues |
| MiMo F-02: missing pathway failure ECQ1 test | LOW | **已修复** | `test_quality_gate_integration_maps_pathway_fail_to_ecq1_block` L358–392: pathway=fail + policy=block → ECQ1/block, verifies `reason` and `issue_id` |
| MiMo F-03: ECQ2/warn policy severity untested | INFO | **已修复** | `test_quality_gate_integration_maps_evidence_confirm_fail_warn_policy_to_ecq2_warn` L262–294: policy=warn + deterministic=fail → ECQ2/warn, gate status=warn |
| MiMo F-04: off-policy handling implicit | INFO | **已修复** | Same fix as DS-ECP4S1-03: explicit `ValueError` guard + docstring make off-policy fail/warn path fail-closed and documented |

## Per-Finding Verification Detail

### DS-ECP4S1-01 — `hard_gate.informational_issue_ids` → `warning_issue_ids`

**Fix:** `_warning_issue_ids()` (L326–345) now collects `hard_gate.informational_issue_ids` alongside `reviewable_issue_ids`, with inline comment at L343. Field docstring at L52 updated.

**Test coverage:** `test_summary_from_repository_warn_keeps_reviewable_and_informational_ids` constructs a V2 result with one reviewable issue (id=`evidence-confirm:e1:reviewable`) and one informational issue (id=`evidence-confirm:e3:informational`), plus a pathway warning. Asserts `warning_issue_ids == (pathway:anchor_precision_warn, evidence-confirm:e1:reviewable, evidence-confirm:e3:informational)` — all three categories present, de-duplicated.

**Residual note:** `issue_count` now matches the ID list scope (both include informationals), resolving the original count-vs-IDs inconsistency. Verified: `assert summary.issue_count == 2` (1 reviewable + 1 informational, matching the 2 V2 issues constructed).

### DS-ECP4S1-02 — Test coverage expansion

**Fix:** 6 new tests added to `test_evidence_confirm_production.py`:

| Test | What it proves | Lines |
|---|---|---|
| `test_summary_from_repository_pass_is_compact_and_counts_checked_facts` | pass summary has correct status, counts, no excerpt leak | 71–98 |
| `test_summary_from_repository_warn_keeps_reviewable_and_informational_ids` | warn summary collects all non-blocking IDs | 101–136 |
| `test_not_run_evidence_confirm_summary_accepts_stable_reason_variants` | parametrized: `invalid_request`, `runner_exception:RuntimeError`, `repository_failure:source_unavailable` | 139–168 |
| `test_not_run_evidence_confirm_summary_rejects_invalid_reason` | unregistered reason → `ValueError` | 171–190 |
| `test_not_run_evidence_confirm_summary_rejects_invalid_policy` | invalid policy → `ValueError` | 193–212 |
| `test_summary_from_repository_not_applicable_boundary_is_not_run` | `deterministic_status=not_applicable` aggregates to `status=not_run` | 215–236 |

Test helpers `_repository_result`, `_v2_result`, `_issue` (L239–347) use real `EvidenceConfirmResultV2`, `EvidenceConfirmHardGate`, `EvidenceConfirmFactResultV2`, `EvidenceConfirmIssue` dataclasses — no mocks. Imports are test-only from `fund_agent.fund.evidence_confirm`, not from production paths.

### DS-ECP4S1-03 / MiMo F-04 — `_ecq_policy_severity` defensive guard

**Fix:** `_ecq_policy_severity` (L264–281) now has explicit three-branch logic:

1. `policy == "block"` → `SEVERITY_BLOCK`
2. `policy == "off"` → `raise ValueError("policy='off' 的 Evidence Confirm fail/warn 摘要不能投影为 ECQ warn")`
3. else (implicitly `policy == "warn"`) → `SEVERITY_WARN`

**Test coverage:** `test_quality_gate_integration_rejects_off_policy_fail_summary` (L395–420) constructs a summary with `policy="off"`, `status="fail"`, `deterministic_status="fail"` and passes it through `run_quality_gate_for_bundle`. Asserts `pytest.raises(ValueError, match="policy='off'")`. This proves the guard fires before any ECQ issue is emitted.

### MiMo F-01 — explicit `summary=None` test

**Fix:** `test_quality_gate_integration_explicit_summary_none_produces_no_ecq_issues` (L198–225) passes `evidence_confirm_summary=None` explicitly (rather than relying on default parameter omission). Asserts no ECQ issues in both `QualityGateResult.issues` and `quality_gate.json` payload. This is distinct from `test_quality_gate_integration_without_summary_is_unchanged` which relies on the default parameter value.

### MiMo F-02 — pathway failure ECQ1 test

**Fix:** `test_quality_gate_integration_maps_pathway_fail_to_ecq1_block` (L358–392) constructs summary with `pathway_status="fail"`, `deterministic_status="not_run"`, `policy="block"`, `not_run_reason="repository_failure:source_unavailable"`. Asserts:
- `ecq1.severity == "block"`
- `ecq1.reason == "repository_failure:source_unavailable"`
- `ecq1.issue_id == "evidence-confirm:110011:2024:ECQ1:repository_failure:source_unavailable"`
- `result.quality_gate_result.status == "block"`

### MiMo F-03 — ECQ2/warn policy variant

**Fix:** `test_quality_gate_integration_maps_evidence_confirm_fail_warn_policy_to_ecq2_warn` (L262–294) constructs summary with `policy="warn"`, `status="fail"`, `deterministic_status="fail"`. Asserts `ecq2.severity == "warn"` and `result.quality_gate_result.status == "warn"` (not block).

## Validation

- `uv run pytest tests/fund/test_evidence_confirm_production.py tests/fund/test_quality_gate.py tests/fund/test_quality_gate_integration.py -q` → **56 passed** (was 44)
- `uv run ruff check` → All checks passed (per fix evidence)
- `git diff --check` → no whitespace errors (per fix evidence)
- No live/PDF/network/provider/LLM execution was performed

## Remaining Blockers

无。所有 7 个 accepted findings 已修复。

## Residual Risks

| Risk | Coverage | Owner |
|---|---|---|
| `_evidence_confirm_quality_gate_issues` 的 `summary is None` 分支仍仅在 `run_quality_gate_for_bundle` 外可达（`is not None` guard 阻止集成路径调用） | 非 Slice 1 范围；Slice 2 若需使用需补集成测试 | Service owner |
| `not_run_evidence_confirm_summary` 仍不校验 policy 与 reason 一致性 | 调用方（Service）负责；非 Slice 1 范围 | Fund owner |
| 测试 `test_evidence_confirm_production.py` 新增的 `_v2_result` / `_issue` 等 helper 导入了 `evidence_confirm` 模块的 `EvidenceConfirmResultV2` 等类型 | 测试仅用于构造 fixture；不进入生产导入路径 | — |
| 新增测试的 `_summary` helper 支持了 `policy`/`pathway_status`/`not_run_reason` 参数（`test_quality_gate_integration.py:625–671`） | 向后兼容原有调用（默认 `policy="block"`, `pathway_status="pass"`） | — |
| Service propagation (Slice 2) 及后续 Slice 仍待实现 | 后续已批准 gate | Service/UI owner |

## Required Next Gate

Proceed to EC-P4 Slice 2 — Service Deterministic Opt-In Propagation.

## Reviewed By

AgentDS, 2026-06-22 22:00 Asia/Shanghai
