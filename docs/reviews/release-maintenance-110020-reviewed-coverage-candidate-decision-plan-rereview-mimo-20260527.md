# Re-Review: 110020 Reviewed Coverage Candidate Decision Plan

> Reviewer: AgentMiMo (re-review, findings closure check)  
> Date: 2026-05-27  
> Target: `docs/reviews/release-maintenance-110020-reviewed-coverage-candidate-decision-plan-20260527.md`  
> Prior review: `docs/reviews/release-maintenance-110020-reviewed-coverage-candidate-decision-plan-review-mimo-20260527.md`  
> GLM review: `docs/reviews/release-maintenance-110020-reviewed-coverage-candidate-decision-plan-review-glm-20260527.md`

## Verdict: PASS

All MiMo findings (M1/M2/M3/L1/L2) and GLM findings (F1/F2) are closed in the revised plan. No new findings.

---

## MiMo Findings Closure

### M1 (medium): 缺少 index-lens evidence sufficiency 定义 — CLOSED

Plan now includes a dedicated "Index-Lens Evidence Sufficiency Definition" section (lines 76-86) with a table defining `sufficient` / `insufficient` / `out_of_scope` for three items: `index_profile`, `tracking_error`, and benchmark-methodology / constituents / tracking evidence. Each row includes required assessment, sufficient means, insufficient means, and out-of-scope means.

Key improvement: `tracking_error` is explicitly stated as "a concrete prerequisite for treating `110020` as a mature index fund coverage candidate in any later baseline/golden preflight" (line 86). This directly addresses the original finding.

### M2 (medium): strict golden not configured 缺少 concrete resolution path — CLOSED

Risk table row (line 71) now reads: "Carried-forward residual. Correctness cannot be reviewed until same-year strict golden coverage is established; the score must not be treated as strict correctness proof."

This explicitly names the disposition (carried-forward residual) and the constraint (score is not correctness proof), which is the concrete resolution path: the evidence gate must record this state and not treat the score as golden-ready.

### M3 (medium): Stop conditions 过窄 — CLOSED

Three missing stop conditions now added:

1. **New warnings** (line 113): "Stop and report if fresh public evidence introduces new P0/P1 warnings or blocks beyond the known `turnover_rate` P1 warn, `FQ2F` P1 field failure warn, and `FQ0` strict-golden-not-configured info."
2. **Source strategy regression** (line 114): "Stop if `source_strategy`, `resolved_source_name`, `fallback_used`, `primary_failure_category`, `fallback_eligibility`, `source_provenance_status`, or `source_provenance_reason` changes from the accepted tuple unless the controller explicitly accepts the changed evidence state."
3. **Review BLOCK** (line 187): "Stop if any reviewer returns `BLOCK` until fixed and re-reviewed."

Acceptance matrix also updated: snapshot step (line 182), score step (line 183), quality-gate step (line 184) all carry forward the new-warning and source-change stop conditions.

### L1 (low): fund_type 缺失 — CLOSED

Evidence summary table now includes `fund_type_slot: index_fund` (line 43). Candidate A entry conditions include "Accepted fund-type slot remains `index_fund`" (line 97).

### L2 (low): Independent review BLOCK verdict 处理不明确 — CLOSED

Acceptance matrix "Independent reviews" row (line 187) now explicitly states: "Stop if any reviewer returns `BLOCK` until fixed and re-reviewed."

---

## GLM Findings Closure

### GLM F1 (non-blocking): Index-specific evidence 评估缺少独立验证 step — CLOSED

Plan now includes a dedicated "Index evidence assessment" row in the acceptance matrix (line 185) with explicit required action: "Evaluate `index_profile`, `tracking_error`, and benchmark-methodology / constituents / tracking evidence from public snapshot/score/gate outputs and accepted artifacts." Output is "`index_evidence_assessment` section in the evidence artifact." Acceptance condition requires "each item receives `sufficient`, `insufficient`, or `out_of_scope` with reason and source pointer."

This matches GLM's recommendation to make the index evidence assessment an independent step rather than burying it in the general evidence artifact row.

### GLM F2 (non-blocking): `--source-csv` 路径版本一致性应显式声明 — CLOSED

Public snapshot acceptance condition (line 182) now includes: "artifact records `docs/code_20260519.csv` path plus git identity/version note. Plan-revision observed CSV state: repo HEAD `188f150cf27c6b3792a92ed11ebedb164b485ebb`, CSV last commit `7596c5ece4894166d5479ee764fc8641a23cfc0d`, `git status --short docs/code_20260519.csv` clean, mtime `May 19 00:28:41 2026`, size `3213 bytes`."

Evidence artifact step (line 186) also requires recording "CSV identity/version note." This fully addresses GLM's recommendation.

---

## Summary

| Finding | Source | Status |
|---|---|---|
| M1: index-lens evidence sufficiency definition | MiMo | closed |
| M2: strict golden resolution path | MiMo | closed |
| M3: stop conditions too narrow | MiMo | closed |
| L1: fund_type missing | MiMo | closed |
| L2: review BLOCK handling | MiMo | closed |
| GLM F1: index-specific assessment step | GLM | closed |
| GLM F2: source-csv version note | GLM | closed |

No new findings. Plan is ready for controller judgment.
