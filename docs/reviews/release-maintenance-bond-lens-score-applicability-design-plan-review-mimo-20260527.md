# Plan Review: bond-lens score applicability design plan

> Reviewer: AgentMiMo
> Date: 2026-05-27
> Target: `docs/reviews/release-maintenance-bond-lens-score-applicability-design-plan-20260527.md`
> Truth sources: `AGENTS.md`, `docs/design.md` v2.2, `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point / Open Residuals / Active Gate Ledger, accepted prior judgment `docs/reviews/release-maintenance-bond-lens-contract-baseline-coverage-plan-controller-judgment-20260527.md`

## Verdict

**PASS_WITH_FINDINGS** — no blocking or material findings; no re-review required.

## Review Method

- Verified plan scope guard, Startup Packet replay, and forbidden/allowed lists against `docs/implementation-control.md` Current Gate and Next Entry Point.
- Verified plan's current code facts claims against actual source: `extraction_score.py` (lines 102-103, 1409-1495), `quality_gate.py` (lines 40-41, 45), `fund_type.py` (lines 15-22).
- Cross-checked design decisions against `docs/design.md` §3.4 preferred_lens, §7.3-7.4 quality gate, §6.5 fund type, and the accepted prior judgment's refinement requirements.
- Evaluated code-generation readiness, silent N/A prevention, FQ4 denominator behavior, issue taxonomy determinism, file scope, and validation matrix sufficiency.

## Findings

### F1: `BondRiskEvidenceGroup` dataclass shape not fully specified

**Severity**: Informational

**Evidence**: Section 4 lists 7 evidence groups with `required_evidence`, `allowed_na_reason`, and `failure_behavior` columns, and section 5.1 suggests `BOND_RISK_EVIDENCE_GROUPS: Final[tuple[BondRiskEvidenceGroup, ...]]` as a constant, but the `BondRiskEvidenceGroup` dataclass fields are never defined explicitly. The column names in the table imply fields, but the implementer must infer the mapping.

**Judgment**: Non-blocking. The table column names are clear enough for a competent implementer to derive the dataclass. However, for true code-generation readiness, specifying the dataclass fields (e.g., `group_id: str`, `required_evidence_description: str`, `allowed_na_reasons: tuple[str, ...]`, `failure_behavior: str`, `severity: str`, `baseline_blocking: bool`, `related_chapters: tuple[int, ...]`) would remove ambiguity.

### F2: `bond_risk_data_gap_declared` severity "by group criticality" is under-specified

**Severity**: Low

**Evidence**: Section 7.1 issue code table says `bond_risk_data_gap_declared` has severity `info or warn by group criticality`, but does not define which of the 7 groups are critical (warn) vs. informational. The implementer must make a judgment call.

**Judgment**: Non-blocking. The first implementation defaults to aggregate fund-level issue (section 7.2 last paragraph), so per-group severity differentiation can be deferred. But the plan should either specify the criticality split or explicitly state it is deferred to implementation review.

### F3: `QualityGateIssue` extension for `issue_id` / `issue_code` is underspecified

**Severity**: Low

**Evidence**: Section 6 says "If `QualityGateIssue` is extended with optional `issue_id` / `issue_code`, ensure JSON and Markdown renderers include them and existing tests remain compatible." Current `QualityGateIssue` (quality_gate.py:45) has no `issue_id` or `issue_code` field. The plan does not specify the field type, default value, or whether the extension is required or optional for the first slice.

**Judgment**: Non-blocking. The plan correctly notes this as conditional ("if extended"). The first implementation can project `bond_risk_evidence_missing` into the existing `reason` field without extending the dataclass. The extension can be deferred to a later consumer-driven gate.

### F4: Raw/applicable denominator metadata output location is ambiguous

**Severity**: Low

**Evidence**: Section 5.3 lists 8 metadata fields (`raw_total_field_count`, `raw_missing_field_count`, etc.) and says "Implementation may keep current `total_field_count`, `missing_field_count`, and `missing_field_rate` as applicable counts for quality_gate compatibility, but must emit the raw/applicable comparison in `fund_quality` or `field_applicability_decisions`." The "or" leaves the implementer a choice that affects downstream consumers.

**Judgment**: Non-blocking. Both locations are additive and backward-compatible. The plan should recommend one primary location (suggested: `field_applicability_decisions` as it is the new dedicated output) with a note that `fund_quality` may carry a summary if quality_gate consumers need it.

### F5: `_scorable_records()` refactoring risk not explicitly addressed

**Severity**: Informational

**Evidence**: Section 8.2 step 2 says "Refactor `_scorable_records()` from 'index-only exclusion' into a general applicability decision path while preserving current index behavior." Current code (extraction_score.py:1435-1463) shows `_scorable_records()` is called at 5 locations (lines 569, 1170, 1227, 1293, 1395). The plan does not call out the refactoring risk of changing a function used in 5 call sites, or specify whether the refactor changes the function signature.

**Judgment**: Non-blocking. The existing `_is_non_applicable_index_quality_record()` helper pattern is clean and extensible. Adding a parallel `_is_non_applicable_bond_holdings_record()` check inside `_scorable_records()` or composing via a general `_is_non_applicable_record()` dispatcher is low-risk. But the plan should specify the approach (compose vs. replace) to prevent implementation drift.

### F6: `score_applicability_issues` consumer compat for older score.json

**Severity**: Informational

**Evidence**: Section 8.4 says "Existing older `score.json` without `score_applicability_issues` must run." This is correct. But the plan does not specify whether `quality_gate.py` should treat missing `score_applicability_issues` as empty list, missing key, or skip parsing entirely. The difference matters for defensive coding.

**Judgment**: Non-blocking. Standard Python `dict.get("score_applicability_issues", [])` pattern is implied. Worth noting in implementation to use optional parsing.

## Hard Constraint Compliance

| Constraint | Status | Evidence |
|---|---|---|
| No renderer changes | PASS | Section 10 explicitly forbids |
| No FQ0-FQ6 policy change | PASS | Section 5.3 preserves thresholds; section 6 preserves semantics |
| No Service/CLI changes | PASS | Section 10 explicitly forbids |
| No Host/Agent/dayu | PASS | Section 10 explicitly forbids |
| No source strategy/helper | PASS | Section 10 explicitly forbids |
| No extractor logic changes | PASS | Section 10 explicitly forbids; scope limited to score/gate |
| No golden/baseline promotion | PASS | Section 10 explicitly forbids |
| No extra_payload | PASS | Section 10 explicitly forbids |
| No GitHub mutation | PASS | Section 10 explicitly forbids |

## Specific Review Focus Assessment

### Code-generation readiness (without authorizing implementation)

The plan provides concrete dataclass designs (section 5.1), constant names (section 4), step-by-step implementation guidance (sections 8.2-8.3), and a validation matrix (section 9). It is code-generation-ready as a design artifact. It correctly defers actual coding to a separate implementation gate after controller acceptance.

### Silent N/A prevention for bond_fund equity-shaped holdings_snapshot

**Strong**. The plan's core design decision (section 3.1-3.3) explicitly requires:
1. Exclusion from denominator only when paired with replacement issue.
2. Single allowed N/A reason: `not_applicable_to_bond_fund_equity_holdings`.
3. Plain `not_applicable` without replacement issue is explicitly invalid.
4. `bond_risk_evidence_missing` as the mandatory replacement issue with `severity=warn` and `baseline_blocking=true`.

This prevents the silent pass scenario completely.

### FQ4 raw/applicable denominator + 006597 anti-mis-pass + baseline_blocking

**Strong**. Section 5.3 specifies raw/applicable metadata for observability. Section 5.4 requires 5 specific proof points for 006597, including before/after FQ4 counts, deterministic issue id, and explicit statement that quality gate status change is not solely from denominator reduction. `baseline_blocking=true` on replacement issues blocks baseline/golden promotion while allowing quality gate `warn` to pass, which is the correct separation.

### Issue taxonomy / deterministic issue id / quality_gate projection

**Adequate with minor gaps** (F2, F3). 8 issue codes are defined with clear meanings. Deterministic id format is stable and parseable. Quality gate projection specifies FQ2F rule code with warn severity. The gaps are informational/low and do not block implementation.

### File scope

**Appropriate**. `extraction_score.py` and `quality_gate.py` are the correct files. `fund_type.py` is correctly excluded unless taxonomy conditions are met (section 8.1). The plan explicitly enumerates the conditions under which `fund_type.py` scope expansion would be justified.

### Validation matrix

**Sufficient and not excessive**. 8 focused extraction tests, 5 focused quality gate tests, 1 evidence run, and 3 regression targets. Correctly does not require full pytest for the narrow slice. Commands are explicit.

## Controller Judgment Alignment

The plan correctly incorporates all requirements from the accepted prior judgment:
- Convertible-bond / equity-exposure evidence group added (section 4, row 7).
- FQ4 denominator validation requirement included (section 5.4).
- Proof that 006597 is not improved only by suppressing equity evidence (section 5.4, requirement 5).
- Startup Packet replay matches current gate state.
- Allowed/forbidden scope matches prior judgment boundaries.

## Summary

The plan is well-structured, follows first-principles design, and correctly prevents the silent N/A risk that was the core motivation. Six findings are all informational or low severity. No blocking issues. No re-review required.
