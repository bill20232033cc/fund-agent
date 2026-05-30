# Plan Review: Small Baseline Corpus v1

> Date: 2026-05-27
> Reviewer: AgentMiMo
> Review target: `docs/reviews/release-maintenance-small-baseline-corpus-v1-plan-20260527.md`
> Verdict: **PASS_WITH_FINDINGS**

---

## Review Criteria

### Criterion 1: Gate 4 — 从 004393 扩到 5-10 只代表样本

**Verdict: PASS**

Plan defines a 7-row candidate matrix covering `active_fund`, `enhanced_index`, `bond_fund`, `index_fund`, `qdii_fund`, and `fof_fund` attempt. Three clean rows (`004393`/active, `004194`/enhanced-index, `006597`/bond) enter the clean evaluation denominator. Two fallback-blocked rows (`110020`/index, `017641`/QDII) are kept visible but excluded from clean denominator. FOF is explicitly recorded as `data_gap` / `taxonomy_pending`. The control doc next entry point requires 5-10 representative samples; the plan covers 7 planning rows across 6 fund-type slots, which satisfies the gate requirement even though only 3 are clean.

No finding.

---

### Criterion 2: 每只基金要求输出字段

**Verdict: PASS**

The candidate matrix (lines 38-47) explicitly specifies per-row columns for: annual report availability, extraction field gaps, quality gate status to capture, report-quality issue categories to classify, false-positive suspicion, and suitability for future golden. Each row is populated with specific field gaps, issue categories, and required next actions.

No finding.

---

### Criterion 3: 严格禁止项

**Verdict: PASS**

The Non-Goals section (lines 146-157) explicitly enumerates all prohibitions from the gate specification: renderer, FQ0-FQ6, Service/CLI defaults, Host/Agent/dayu, extractor, `FundDocumentRepository` source fallback, extra_payload, and GitHub mutation. The Scope header (line 5) and Startup Packet Recap (lines 7-14) reinforce these boundaries. The plan states "No source code, tests, README, product output, fixture, control doc, commit, push, or PR was modified."

No finding.

---

### Criterion 4: fallback-blocked 与 FOF data_gap 排除出 clean denominator

**Verdict: PASS**

- Lines 31-32: fallback-blocked rows are "kept visible but outside the clean denominator until the upstream failure category is recovered as `not_found` or `unavailable`, or the row is replaced."
- Line 33: FOF attempts are "kept visible as `data_gap` / `taxonomy_pending`; do not count QDII-FOF as pure FOF coverage."
- Lines 55-57: Manifest freeze step explicitly marks fallback-blocked and FOF data-gap rows as exclusions with exact reason.
- Lines 127-129: Stop conditions block fallback-blocked rows from clean denominator before upstream failure category recovery.

No finding.

---

### Criterion 5: Verifier Matrix 可执行性

**Verdict: PASS_WITH_FINDINGS**

**Finding M1: Plan-only gate 是否需要 ruff/git diff/checkpoint smoke**

Evidence: Lines 119-120 state "Ruff: Required for implementation gates; for this planning-only artifact, not executed unless reviewer asks." and "Full pytest: Not required for this design-only / analysis-only plan because it adds no executable code." The control doc gate sequence requires "each gate closeout 有验证和 local accepted commit."

Risk: If the implementation worker produces the plan as a tracked artifact under `docs/reviews/`, a `git diff --check` should at minimum verify no unintended whitespace/formatting issues were introduced. The plan does not mandate this basic hygiene check for its own artifact.

Recommendation: Add a line in the Verifier Matrix or Validation section requiring `git diff --check` after the plan artifact is written, even for plan-only gates. This is a minimal hygiene check that does not require running tests.

Severity: **MATERIAL**

---

**Finding M2: `selected_funds_smoke.py` dry-run vs run 区分不够明确**

Evidence: Lines 105-106 show two commands for `selected_funds_smoke.py` — a dry-run (default) and an explicit `--run` variant. The dry-run "verifies command construction without product run" while the run is "optional bounded smoke." However, the plan does not specify what constitutes "command construction verification" — does it check argument parsing only, or does it attempt a partial extraction?

Risk: If the dry-run does not actually validate that the fund codes and report years resolve to valid candidates, the dry-run provides false confidence. If it does attempt partial resolution, it may trigger unintended network/cache access.

Recommendation: Clarify what the dry-run validates (argument parsing only vs. candidate resolution) and whether it requires network access. If argument-only, note that it does not verify candidate availability.

Severity: **MINOR**

---

### Criterion 6: Artifact policy — 避免提交大量运行产物

**Verdict: PASS**

Lines 75-93 define a clear artifact policy:
- Tracked artifacts: only this plan and a future review summary artifact under `docs/reviews/`.
- Scratch artifacts: explicitly listed under `/tmp/...` and `reports/...` paths.
- Line 93: "Large Markdown reports, stderr logs, snapshot JSONL, score JSON, quality gate JSON/Markdown, bundle JSON, validator summaries, and failure matrices must stay in scratch paths."

The policy correctly prevents large outputs from entering tracked artifacts.

No finding.

---

### Criterion 7: Stop conditions 和 next gate decision rules

**Verdict: PASS**

Lines 124-143 define:
- 8 explicit stop conditions that return `needs-more-evidence`.
- 5 next-gate decision rules mapping observations to specific next gates.
- The decision rules cover: sufficient evidence → golden corpus v1; missing facts → data extraction priority fixes; weak anchors → evidence anchor hardening; chapter contract issues → scoped chapter contract gate; insufficient coverage → more baseline probing.

The decision rules are sufficient to determine the next gate direction.

No finding.

---

## Additional Observations

### Finding I1: 004393/2025 probe-only 行为边界

Evidence: Lines 41, 56, 103-104, 130 define `004393`/2025 as probe-only. Line 130 states "004393 / 2025 probing tries to reuse 2024 golden rows or facts for correctness" as a stop condition. This is correct.

The plan correctly scopes 2025 probing as availability/regression probing only and prohibits reusing 2024 facts. No finding, but the explicitness is worth noting as a positive.

Severity: **INFO**

---

### Finding I2: `extraction-snapshot` / `extraction-score` 命令使用方式

Evidence: Lines 65-66 specify using `fund-analysis extraction-snapshot` and `fund-analysis extraction-score` "only as explicit commands with `--fund-code`, `--report-year`, and caller-chosen run ids." This aligns with the current production CLI interface.

The plan correctly constrains these commands to explicit invocations rather than batch/default modes.

Severity: **INFO**

---

### Finding I3: control doc current gate 状态未更新

Evidence: The control doc line 28 shows `Current gate: core analyze/checklist reliability hardening accepted locally` and line 255 shows `Next entry point: small baseline corpus v1 plan/review`. The plan artifact itself is the first deliverable of this next gate. However, the plan does not mention whether the control doc's `Current gate` field should be updated to reflect that the small baseline corpus v1 plan/review gate is now active.

Risk: If the control doc is not updated, a future agent resuming from the control doc may not realize the gate has progressed. However, since this is a plan-only artifact and the gate is `plan/review` (not `implementation`), the control doc update may be deferred to the review closeout.

Recommendation: The review closeout or controller judgment should update the control doc's `Current gate` field. The plan itself does not need to mandate this, but the reviewer notes the gap.

Severity: **MINOR**

---

## Summary

| Finding | Severity | Description |
|---------|----------|-------------|
| M1 | MATERIAL | Plan-only gate should mandate `git diff --check` for artifact hygiene |
| M2 | MINOR | `selected_funds_smoke.py` dry-run scope clarification |
| I3 | MINOR | Control doc `Current gate` field update timing |

---

## Verdict

**PASS_WITH_FINDINGS**

The plan satisfies all 7 review criteria. It correctly defines a 7-row candidate matrix covering 6 fund-type slots, explicitly records per-candidate field gaps and issue categories, prohibits all specified scope creep, excludes fallback-blocked and FOF data-gap rows from the clean denominator, defines a comprehensive verifier matrix, maintains a clean artifact policy, and provides actionable stop conditions and next-gate decision rules.

The one material finding (M1) is a process hygiene improvement: plan-only gates should still mandate `git diff --check` after writing the tracked artifact. This does not block the plan's acceptance but should be addressed in the review closeout or controller judgment.

The plan is safe to accept with the noted findings as review-closeout residuals.
