# Drawdown Stress NAV-Derived Metric — Aggregate Deepreview (MiMo)

日期：2026-05-29

角色：aggregate deepreview worker only。未编辑文件、未 commit、未 push、未 PR、未 merge、未 release、未 golden promotion、未运行破坏性命令。

Gate：`drawdown_stress NAV-derived metric contract / implementation gate`

Gate classification：`heavy`

---

## 0. Review Scope

### 0.1 Work Unit Commits

- `41485d5` gateflow: accept plan for drawdown stress nav metric
- `bd1013b` gateflow: accept drawdown stress nav metric implementation

### 0.2 Base Reference

`73da81b`（CSRC EID adapter normalization accepted checkpoint）

### 0.3 Required Artifacts Verified

| Artifact | Path | Status |
|---|---|---|
| Plan | `docs/reviews/release-maintenance-drawdown-stress-nav-derived-metric-implementation-plan-20260529.md` | present, code-generation-ready |
| Plan review MiMo | `docs/reviews/release-maintenance-drawdown-stress-nav-derived-metric-implementation-plan-review-mimo-20260529.md` | pass-with-risks |
| Plan review GLM | `docs/reviews/release-maintenance-drawdown-stress-nav-derived-metric-implementation-plan-review-glm-20260529.md` | present |
| Plan rereview MiMo | `docs/reviews/release-maintenance-drawdown-stress-nav-derived-metric-implementation-plan-rereview-mimo-20260529.md` | accepted |
| Plan rereview GLM | `docs/reviews/release-maintenance-drawdown-stress-nav-derived-metric-implementation-plan-rereview-glm-20260529.md` | accepted |
| Implementation evidence | `docs/reviews/release-maintenance-drawdown-stress-nav-derived-metric-implementation-evidence-20260529.md` | present, self-check pass |
| Implementation review MiMo | `docs/reviews/release-maintenance-drawdown-stress-nav-derived-metric-implementation-review-mimo-20260529.md` | accepted |
| Implementation review GLM | `docs/reviews/release-maintenance-drawdown-stress-nav-derived-metric-implementation-review-glm-20260529.md` | accepted (L1 fix applied) |
| Implementation rereview MiMo | `docs/reviews/release-maintenance-drawdown-stress-nav-derived-metric-implementation-rereview-mimo-20260529.md` | accepted |
| Implementation rereview GLM | `docs/reviews/release-maintenance-drawdown-stress-nav-derived-metric-implementation-rereview-glm-20260529.md` | accepted |
| design.md | `docs/design.md` | updated in this work unit |
| implementation-control.md | `docs/implementation-control.md` | updated in this work unit |

### 0.4 Real Run Artifacts Verified

| Artifact | Path | Verified |
|---|---|---|
| Snapshot | `reports/extraction-snapshots/bond-risk-drawdown-nav-006597-2024-20260529/snapshot.jsonl` | `bond_risk_contract_status="satisfied"`, seven groups satisfied |
| Score | `reports/scoring-runs/bond-risk-drawdown-nav-006597-2024-20260529/score.json` | `score_applicability_issues=[]` |
| Quality gate | `reports/quality-gate-runs/bond-risk-drawdown-nav-006597-2024-20260529/quality_gate.json` | `status="warn"`, no `bond_risk_evidence_missing` FQ2F |

---

## 1. Plan Review Loop Closure

### 1.1 Initial Reviews

MiMo plan review identified 4 findings:

| # | Severity | Disposition | Closure |
|---|---|---|---|
| 01 | 中 | accepted as required plan fix | Closed in rereview |
| 02 | 低 | folded | Closed in rereview |
| 03 | 低 | folded | Closed in rereview |
| 04 | 低 | non-blocking residual | Closed in rereview |

GLM plan review identified N1-N5 (all LOW), all folded in rereview.

### 1.2 Rereviews

- MiMo rereview: **accepted** — all 7 rereview tasks passed, no scope expansion or weakening.
- GLM rereview: **accepted** — all MiMo 01-04 and GLM N1-N5 findings closed; plan fix notes complete; validator constraint precise; reject test present; minimum_records independence clarified; stop conditions and regression test in place.

### 1.3 Plan Loop Status

**Closed.** Plan reached code-generation-ready after rereviews. Controller disposition fully implemented.

---

## 2. Implementation Review / Fix / Re-Review Loop Closure

### 2.1 Initial Reviews

MiMo implementation review: **accepted** — 15 review focus points, all non-blocking. 2 low-risk observations (Finding 14: Decimal quantize semantics; Finding 15: error_reason prefix). No blocking findings.

GLM implementation review: **accepted** — 10 focus points all passed. Findings:
- L1 (低): summary hardcoded "2024" — should use `report.key.year`
- I1 (信息): anchor note missing `series_record_count`
- I2 (信息): identity_status independent reject path lacks dedicated test

### 2.2 Controller-Accepted Fix

GLM L1 fix applied by implementation worker:
- `bond_risk_evidence.py`: `summary` changed from hardcoded `"2024"` to `f"{report.key.year}"`
- `test_bond_risk_evidence.py`: added `test_nav_derived_drawdown_metric_summary_uses_report_year` with `year=2023` assertion
- Focused validation: ruff passed, 62 tests passed (61 + 1 new)

### 2.3 Rereviews

- MiMo rereview: **accepted** — L1 correctly closed, no regression, core invariants confirmed.
- GLM rereview: **accepted** — L1 fix verified, touched files limited to `bond_risk_evidence.py` and test, no new issues.

### 2.4 Implementation Loop Status

**Closed.** All reviews accepted. L1 fix applied and verified by both rereviewers.

---

## 3. Code vs Accepted Plan Verification

### 3.1 Slice-by-Slice Verification

| Slice | Plan Requirement | Implementation Status |
|---|---|---|
| 1: Metric contract and calculation | `NavMaxDrawdownMetric`, `calculate_max_drawdown_from_nav_series()`, `format_max_drawdown_percent()` | Implemented in `nav_metrics.py` (311 lines) |
| 2: Contract extension + derived anchor | `quantitative_derived`, `derived_metric`, validator constraint, derived anchor builder | Implemented in `models.py` + `bond_risk_evidence.py` |
| 3: FundDataExtractor wiring | `_NavSeriesRepository` Protocol, constructor injection, bond_fund-only call, explicit params | Implemented in `data_extractor.py` |
| 4: Snapshot/score/quality natural path | Snapshot narrow fix, score regression test, quality gate test | Implemented |
| 5: Docs and real evidence | design.md, README updates, real 006597 run | Completed |

### 3.2 Contract Extension Verification

Production `models.py` changes:
- `BondRiskEvidenceStrength`: added `"quantitative_derived"` ✓
- `BondRiskEvidenceMeasurementKind`: added `"derived_metric"` ✓
- `_BOND_RISK_ACCEPTED_STRENGTHS`: extended with `"quantitative_derived"` ✓
- `_validate_bond_risk_status_strength()`: added constraint `strength=="quantitative_derived" → measurement_kind=="derived_metric"` ✓

This precisely closes MiMo plan review finding 01.

### 3.3 Data Boundary Verification

- `bond_risk_evidence.py` imports only `NavMaxDrawdownMetric`, `format_max_drawdown_percent`, `NavDataContractError` from `fund_agent.fund.data` — no IO dependencies.
- `data_extractor.py` uses `_NavSeriesRepository` Protocol with constructor injection, defaults to `FundNavRepository()`.
- Repository call uses explicit params: `fund_code`, `share_class="A"`, `start_date`, `end_date`, `minimum_records=30`, `force_refresh`.
- Non-bond funds skip typed repository entirely.
- No `extra_payload`, no direct CSRC/Eastmoney/cache access in extractors.

**Verified.**

### 3.4 Allowed/Disallowed Files

| Allowed Production File | Changed | Verified |
|---|---|---|
| `fund_agent/fund/data/nav_metrics.py` (new) | yes | ✓ |
| `fund_agent/fund/data/__init__.py` | yes | ✓ |
| `fund_agent/fund/data_extractor.py` | yes | ✓ |
| `fund_agent/fund/extractors/models.py` | yes | ✓ |
| `fund_agent/fund/extractors/bond_risk_evidence.py` | yes | ✓ |
| `fund_agent/fund/extraction_snapshot.py` | yes (narrow fix) | ✓ justified in evidence |
| `docs/design.md` | yes | ✓ |
| `fund_agent/fund/README.md` | yes | ✓ |
| `tests/README.md` | yes | ✓ |

Disallowed files **not** changed:
- `extraction_score.py` — not modified ✓
- `quality_gate.py` — not modified ✓
- Golden fixtures — not modified ✓
- Service/UI/Host/Agent/dayu — not modified ✓

---

## 4. Score / Quality / Golden Weakening Check

### 4.1 extraction_score.py

**Not modified.** `git diff 73da81b..bd1013b` shows no changes to this file.

### 4.2 quality_gate.py

**Not modified.** No changes.

### 4.3 Golden Fixtures

**Not modified.** No changes.

### 4.4 Real Run Verification

Snapshot:
- `bond_risk_contract_status="satisfied"` ✓
- `bond_risk_satisfied_groups` contains all 7 groups including `drawdown_stress` ✓
- `bond_risk_weak_groups=[]` ✓
- `bond_risk_missing_groups=[]` ✓
- `bond_risk_ambiguous_groups=[]` ✓

Score:
- `score_applicability_issues=[]` — no `bond_risk_evidence_missing` ✓

Quality gate:
- `status="warn"`, `issue_count=6` — remaining warnings are unrelated: FQ2 (turnover_rate, holder_structure, share_change), FQ2F (P1 field failures), FQ0 (not configured), FQ4 (missing rate) ✓
- No `reason="bond_risk_evidence_missing"` FQ2F ✓

### 4.5 Weakening Verdict

**No weakening detected.** Score/quality/golden semantics unchanged. The `drawdown_stress` blocker was naturally解除 by implementing a reviewed metric, not by changing thresholds or policies.

---

## 5. 006597/2024 Blocker 解除 Verification

### 5.1 Seven Groups Satisfied

Before this work unit (from base `73da81b`):
- satisfied: `duration_rate_risk`, `credit_risk`, `leverage_liquidity`, `asset_allocation_holdings_mix`, `redemption_share_pressure`, `convertible_bond_equity_exposure` (6 groups)
- weak: `drawdown_stress`
- `bond_risk_evidence_missing.baseline_blocking=true`, `missing_evidence_groups=["drawdown_stress"]`

After this work unit:
- satisfied: all 7 groups including `drawdown_stress`
- weak/missing/ambiguous: empty
- `score_applicability_issues=[]`

### 5.2 Score No Longer Emits bond_risk_evidence_missing

`derive_score_applicability_issues()` returns empty because all 7 groups are satisfied. The existing regression test `test_weak_drawdown_bond_risk_evidence_issue_lists_only_drawdown_group` still passes, confirming that when `drawdown_stress` is the only unsatisfied group, the blocker correctly fires.

### 5.3 Quality Gate No FQ2F bond_risk_evidence_missing

Quality gate test `test_run_quality_gate_has_no_bond_risk_fq2f_when_score_issue_absent` confirms no FQ2F with `reason="bond_risk_evidence_missing"` when score has no applicability issues.

### 5.4 Blocker 解除 Verdict

**Naturally解除.** The `drawdown_stress` blocker was resolved by:
1. Implementing a reviewed NAV-derived max drawdown metric
2. Projecting it as `quantitative_derived / derived_metric` evidence into `bond_risk_evidence.v1`
3. Score and quality gate naturally stopped emitting the blocker

No score policy, quality gate FQ semantics, baseline_blocking, or golden fixture was weakened.

---

## 6. Residual Risks Verification

| Residual Risk | Documented | Verified |
|---|---|---|
| CSRC EID endpoint availability (no SLA) | implementation-control.md + evidence | ✓ source unavailable → weak/missing, score blocks |
| F class cannot cover full 2024 (starts 2024-10-08) | implementation-control.md + evidence | ✓ F not used as 006597/A evidence |
| `source_query_params` mixes HTTP params and request context | implementation-control.md | ✓ pre-existing, low risk |
| Accumulated NAV ≠ total-return index | implementation-control.md + evidence | ✓ not relabeled |
| Volatility non-goal | plan + implementation-control.md | ✓ not implemented |
| CSRC source scoped to 006597 family | implementation-control.md | ✓ future generalization gate |
| Snapshot anchor projection shows §2 not derived:nav when annual_report anchor coexists | MiMo review finding | ✓ structural fields correct, traceability via extractor anchors |

All residual risks accurately documented and accepted.

---

## 7. Aggregate-Level Findings

### Finding A1 — 无阻断 — implementation-control.md next entry point 更新

implementation-control.md 已将 next entry point 从 `CSRC EID accumulated NAV adapter normalization implementation gate` 更新为 `drawdown_stress NAV-derived metric contract / implementation gate`。当前 work unit 已完成该 gate。下一行的 next entry point 应在 controller judgment 中更新为下一 gate（如 volatility、source generalization 等）。这不是 implementation 偏差，而是 controller 流程推进的正常交接点。

**Severity**: 信息
**Status**: controller judgment 范围

### Finding A2 — 无阻断 — implementation-control.md gate table 已有 CSRC EID adapter normalization 行但缺少 drawdown_stress 行

implementation-control.md `## Release Maintenance Evidence Table` 已新增 CSRC EID adapter normalization 行（accepted local validation）。当前 work unit 的 drawdown_stress gate 完成后，controller judgment 应新增对应行。这不是 implementation 偏差——implementation worker 不负责更新 gate table 的新行，该职责属于 controller。

**Severity**: 信息
**Status**: controller judgment 范围

### Finding A3 — 无阻断 — snapshot derived anchor 投影显示 §2 而非 derived:nav

当 `bond_risk_evidence` 同时存在 `annual_report` 和 `derived` 锚点时，snapshot 的 `_first_traceable_anchor()` 优先返回 `annual_report` 锚点，导致 snapshot 的 `section_id` 显示 `§2` 而非 `derived:nav`。这不影响结构化字段正确性（`bond_risk_satisfied_groups` 正确包含 `drawdown_stress`），但 reviewer 验证 derived provenance 需查看 extractor 内部 anchors。MiMo review 已记录此为低风险 residual。

**Severity**: 低（不影响 score/quality/snapshot 结构化字段正确性）
**Status**: residual，future snapshot schema 扩展可支持多锚点投影

---

## 8. Scope Creep Check

| Check | Result |
|---|---|
| Plan non-goals respected | ✓ volatility non-goal, no score/quality weakening, no PR/push/release |
| Only allowed files changed | ✓ verified in §3.4 |
| No new features beyond plan | ✓ max drawdown only, A-class only, 2024 period only |
| No golden/baseline promotion | ✓ |
| No snapshot schema fields added | ✓ only narrow anchor projection compatibility fix |
| No CLI/service/host changes | ✓ |

**No scope creep detected.**

---

## 9. Validation Verification

### 9.1 Focused Validation (from evidence)

```
uv run ruff check fund_agent/fund/data/nav_metrics.py ... tests/fund/test_quality_gate.py
All checks passed.
```

```
uv run pytest tests/fund/data/test_nav_metrics.py ... tests/fund/test_quality_gate.py -q
176 passed in 0.79s
```

### 9.2 Full Validation (from evidence)

```
uv run ruff check .
All checks passed.
```

```
uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q
938 passed in 4.58s
Total coverage: 92.42%
```

### 9.3 Real CSRC EID Smoke (from evidence)

- 006597/A: `accumulated_nav` / `accumulated_nav` / `verified` / 1807 records / `strong_drawdown_evidence_eligible=True`
- Metric: `max_drawdown_ratio=-0.0010059518819683125157179982` ≈ `-0.10%`, peak 2024-09-26 / 1.1929, trough 2024-10-09 / 1.1917, 243 period records

---

## 10. Verdict

**accepted**

### Summary

The drawdown_stress NAV-derived metric implementation gate has been fully executed through the complete gateflow lifecycle:

1. **Plan review loop closed**: MiMo/GLM initial reviews → controller disposition → plan fixes → MiMo/GLM rereviews both accepted.
2. **Implementation review loop closed**: MiMo/GLM initial reviews → GLM L1 fix applied → MiMo/GLM rereviews both accepted.
3. **Code matches accepted plan**: All 5 slices implemented within allowed scope. Contract extension (`quantitative_derived` / `derived_metric`) includes precise validator constraint closing MiMo finding 01.
4. **No score/quality/golden weakening**: `extraction_score.py`, `quality_gate.py`, and golden fixtures unchanged. Blocker naturally解除 by implementing reviewed metric.
5. **006597/2024 blocker naturally解除**: Snapshot shows 7 groups satisfied including `drawdown_stress`. Score has no `bond_risk_evidence_missing`. Quality gate has no FQ2F `bond_risk_evidence_missing`.
6. **Residual risks accurate**: CSRC EID availability, F class date range, source_query_params mixing, accumulated NAV ≠ total-return, volatility non-goal — all documented.

No aggregate-level blocking findings. Three information-level findings relate to controller judgment scope (next entry point update, gate table new row, snapshot multi-anchor projection).

---

## 11. Self-Check

pass.

- 角色合规：仅做 aggregate deepreview，未编辑代码、未 commit、未 push、未 PR、未 merge、未 release、未 golden promotion。
- 范围合规：仅覆盖 work unit commits (41485d5..bd1013b) 相对 base (73da81b) 的变更和相关 artifacts，排除无关 untracked 文件。
- Review loop 验证：plan review → rereview → implementation review → fix → rereview 全部闭环。
- Real run artifacts 交叉验证：snapshot/score/quality gate 断言与 implementation evidence 一致。
- Verdict 明确：accepted.
