# P9-S2 Plan Review — AgentDS

- **Date**: 2026-05-21
- **Review target**: `docs/reviews/p9-s2-quality-gate-golden-coverage-plan-20260521.md`
- **Reviewer**: AgentDS (independent plan review)
- **Baseline**: post-P9-S1 follow-up planning accepted (`e8be00f`)
- **Design source**: `docs/design.md`
- **Control source**: `docs/implementation-control.md`
- **Prior decision**: `docs/reviews/post-p9-s1-follow-up-planning-20260521.md`

## Verdict

**PASS_WITH_FINDINGS**

The plan's first-principles decision is correct: missing strict golden coverage must be `FQ0/info` (non-blocking), not `gate_not_run`. The state taxonomy is well-reasoned, the non-goals are properly scoped, and the file-level implementation plan touches the right modules. However, the state model mapping to existing `CorrectnessSummary` is underspecified, the test matrix has false-positive risks where aggregate status alone won't prove FQ0/info generation, and CLI diagnosis visibility for the golden coverage gap is ambiguous. These should be clarified before or during implementation but do not require plan re-approval.

---

## Findings

### Finding 1 — State Model Mapping Gap (severity: HIGH)

**What**: The plan proposes 9 explicit state names (Section 3) but does not specify how they map to the existing `CorrectnessSummary` dataclass fields.

**Evidence**:
- Current `CorrectnessSummary` (`extraction_score.py:310-337`) has: `status` (available/unavailable), `golden_answer_path`, `total_records`, `comparable_records`, `matched_records`, `mismatched_records`, `unavailable_records`, `skipped_records`, `accuracy_rate`, `reason`, `record_results`
- The plan proposes `coverage_scope` (not_configured/fund_not_covered/partially_covered/covered) plus `covered_fund_codes`, `missing_fund_codes`, `coverage_required` (Section 4)
- The plan does not specify whether `coverage_scope` replaces or augments the existing `status` field, or how the per-fund scope is derived from `record_results`

**Why it matters**: `compare_snapshot_correctness()` (`extraction_score.py:771-833`) currently operates on ALL records without fund-scoping. The golden file contains 6 funds; if analyzing fund `000216` (a selected-pool member not in the golden file), the function will still return `status=available` with 0 comparable records for `000216`. The plan needs to specify whether `coverage_scope` is computed by checking `record_results` for the current fund's presence, or by scanning the golden file's fund list before comparison.

**Recommendation**: The plan should add a mapping table from proposed states to `CorrectnessSummary` fields, and clarify that `coverage_scope` for single-fund analyze is derived by checking `golden_answer_path` existence → golden fund list membership → record_result presence.

### Finding 2 — Test Matrix False Positive Risk (severity: HIGH)

**What**: Three test cases in the matrix (rows: "correctness unavailable only", "correctness fund not covered only", "selected-pool member without golden coverage") verify only aggregate gate status (`pass` / `gate runs; not not_run`), which can be satisfied without the implementation actually generating FQ0/info issues.

**Evidence**:
- Current `_evaluate_correctness()` (`quality_gate.py:270-317`) only emits FQ0/info when `correctness.status` is `unavailable` or `not_implemented` (aggregate level), and only emits FQ1/block for mismatch records
- If the golden file EXISTS and the fund is simply not in it, `correctness.status` will be `available` (not `unavailable`), and with 0 mismatched records, `_evaluate_correctness()` returns empty issues — no FQ0/info is generated at all
- A test asserting `aggregate status == pass` would pass even if the new per-fund FQ0/info logic is never implemented, because no block/warn issues means pass by default (`_aggregate_gate_status()`, quality_gate.py:936-954)

**Recommendation**: Each of these three test cases must also assert the presence of at least one `QualityGateIssue` with `rule_code="FQ0"` and `severity="info"` scoped to the target fund_code, not just the aggregate gate status.

### Finding 3 — CLI Diagnosis Visibility Gap (severity: MEDIUM)

**What**: The plan says FQ0/info should be in `quality_gate.md/json` but "do not print this as a top-level failure" (Section 5). It does not specify whether the FQ0/info message appears in stderr at all.

**Evidence**:
- Current `_echo_quality_gate_summary()` (`cli.py:879-900`) prints status, issue count, and artifact paths to stderr
- For a fund like `000216` (selected-pool member, no golden coverage, good P0/P1), stderr would show `quality_gate_status: pass` with no indication that the correctness oracle was skipped
- The recommended message (Section 5): `基金 `xxxxxx` 在精选池中，但 strict golden answer 尚未覆盖...` is useful diagnostic content, but the plan doesn't say where it appears

**Why it matters**: A CLI user running `fund-analysis analyze 000216` would see a successful report with no warning that correctness wasn't verified. The user might reasonably assume the full quality gate ran, when in fact the most powerful check (correctness oracle) was absent. This undermines the "evidence auditable" design principle (`design.md` §1.2).

**Recommendation**: The plan should explicitly state that FQ0/info messages appear in stderr as informational lines (not errors) when golden coverage is absent for the analyzed fund. Alternatively, if the decision is artifact-only, the plan should document the rationale for keeping this invisible to CLI users.

### Finding 4 — `correctness_missing_comparable_value` State Redundancy (severity: LOW)

**What**: The plan introduces `correctness_missing_comparable_value` as a distinct state but says "current mismatch semantics apply" — creating a named state with identical behavior to `correctness_mismatch`.

**Evidence**:
- Current code at `extraction_score.py:1652-1665`: when `actual_value is None` for a comparable sub_field, it returns `status=CORRECTNESS_MISMATCH` with reason "golden 期望存在该字段，但 snapshot 明确标记为缺失"
- The plan's state table says this state triggers "current mismatch semantics apply"
- The distinction between "values conflict" and "value missing" is semantically meaningful but behaviorally identical (both → FQ1/block)

**Recommendation**: Either collapse into `correctness_mismatch` with distinct reason text, or keep the state but document it as a sub-case of mismatch for diagnostic purposes only. The current plan text is ambiguous about whether this is a new state code or just a documentation label.

### Finding 5 — Golden Answer File Edge Cases (severity: LOW)

**What**: The plan's Section 4 says the default golden path absence resolves to `None` (correctness unavailable), but doesn't address what happens when the file exists but is empty, malformed, or contains only skipped fields.

**Evidence**:
- `_resolve_golden_answer_path()` (`fund_analysis_service.py:630-649`): if the default path doesn't exist, returns `None` → correctness unavailable
- If the file exists but is empty/malformed, `load_golden_answer_json()` would raise `json.JSONDecodeError` or `GoldenAnswerValidationError`, which propagates up as an unhandled exception — not as a clean `correctness_not_configured` state

**Recommendation**: The implementation should catch JSON decode and validation errors from `load_golden_answer_json()` and convert them to `correctness_not_configured` with a diagnostic message, rather than letting them crash the analyze flow.

### Finding 6 — CSV Duplicate 016492 (severity: INFO)

**What**: The plan correctly defers the duplicate `016492` issue as human-owned residual risk.

**Evidence**:
- Implementation control doc (line 125): "P5-S6 user/App source reconciliation... `016492` 重复保持 human-owned，不阻断 P5-S7 plan"
- This has been explicitly deferred through multiple slices (P5-S6, P5-S7, P5 aggregate)
- Making it block P9-S2 would be scope creep inconsistent with prior controller decisions

**Recommendation**: No action needed. The plan's treatment is consistent with established controller precedent.

---

## Cross-Reference Verification

### Design doc alignment

| Plan claim | Design doc reference | Status |
|---|---|---|
| FQ0 = info/not-run, not block | §7.2: FQ0 "前置条件缺失 / info / not-run" | Consistent |
| FQ1 = block for mismatch | §7.2: FQ1 "correctness 或 App 类别冲突 / block" | Consistent |
| Product mode keeps block policy | §7.2: quality gate 体系 | Consistent |
| Golden answer pipeline not bypassed | §7.2: "不能把少量 golden answer 误当全域正确性证明" | Consistent |
| Selected-pool membership ≠ correctness coverage | §7.2: "基准覆盖不足时，应扩大 golden coverage 或降级为显式 residual risk" | Consistent |

### Implementation control doc alignment

| Plan claim | Control doc reference | Status |
|---|---|---|
| P9-S2 scope = quality gate / golden coverage calibration | §1.0: current gate entry point | Consistent |
| P9-S2 is planning only, no implementation | Prior decision §P9-S2 Planning Scope: "planning/review slice first" | Consistent |
| Do not weaken --dev-override | P9-S1 non-goals | Consistent |
| Do not expose warn/off to product | P9-S1 product contract | Consistent |

### Post-P9-S1 follow-up alignment

| Plan claim | Follow-up doc reference | Status |
|---|---|---|
| Default product analyze should treat missing correctness as non-blocking FQ0/info | Option A: "treat missing correctness as an explicit non-blocking FQ0/info" | Directly addressed |
| Distinguish "gate could not run" from "golden coverage absent" | Planning scope bullet 2 | Directly addressed |
| Keep `docs/code_20260519.csv` as default source | Planning scope bullet 4 | Directly addressed |
| CLI messages should explain membership vs coverage | Planning scope bullet 5 | Directly addressed |
| Lock product-mode behavior for 004393 and one non-covered fund | Planning scope bullet 6 | Addressed by test matrix |

---

## Residual Risks After Plan Acceptance

1. The 49 non-covered selected-pool funds rely on extraction coverage, traceability, fund-quality, and template applicability — no correctness oracle. The plan acknowledges this (§10). Acceptable given the alternative (product path unusable for 49/55 funds).

2. If `compare_snapshot_correctness()` is refactored to be fund-scoped for the new states, care must be taken not to break the multi-fund `extraction-score` CLI path which expects aggregate correctness.

3. The plan adds `coverage_scope` to the correctness section of `score.json`. Downstream consumers (quality gate Markdown, any future dashboard) must handle the new fields.

---

## Acceptance Criteria Traceability

| Criterion | Addressed in plan | Verifiable |
|---|---|---|
| Product mode still uses block | §2, §4, §6 (Service) | Yes |
| Selected-pool member without golden answer ≠ not_run | §3 state table, §6 (quality_gate_integration) | Yes (test matrix row "selected-pool member without golden coverage") |
| Missing golden coverage visible as FQ0/info with fund-scoped metadata | §3, §4, §5 | Partially — see Finding 3 (CLI visibility) |
| Explicit mismatch remains FQ1/block | §3 state table, §6 (quality_gate) | Yes (test matrix row "correctness mismatch") |
| Non-member or invalid CSV still blocks as not_run | §3 state table, §6 (quality_gate_integration) | Yes (test matrix row "fund not in CSV") |
| `docs/code_20260519.csv` remains default | §4 | Yes (no code change to default path) |
| 6 covered golden funds remain human-labeled | §9 non-goals | Yes (no guessing expected values) |

---

## Overall Assessment

The plan makes the correct architectural decision: missing golden coverage is an informational signal, not a gate failure. This preserves the P9-S1 safety boundary (users cannot bypass gate failure) while making the product path usable beyond the 6 human-labeled funds.

The state taxonomy is well-designed and the distinction between `gate_not_run` (membership/CSV failure) and `correctness_not_configured`/`correctness_fund_not_covered` (golden coverage gap) is the right semantic split. The implementation plan correctly identifies all affected modules and the non-goals properly constrain scope.

The findings above are implementation-level concerns that should be addressed during or immediately before implementation. They do not indicate architectural flaws requiring plan re-approval. Finding 1 (state model mapping) and Finding 2 (test false positive risk) are the most important to resolve before coding begins.
