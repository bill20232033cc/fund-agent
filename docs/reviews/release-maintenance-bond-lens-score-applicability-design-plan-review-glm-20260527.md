# Plan Review: bond-lens score applicability design plan

> Reviewer: AgentGLM (GLM-5.1)
> Date: 2026-05-27
> Target plan: `docs/reviews/release-maintenance-bond-lens-score-applicability-design-plan-20260527.md`
> Truth sources: `AGENTS.md`, `docs/design.md` v2.2, `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point / Open Residuals / Active Gate Ledger
> Accepted prior judgment: `docs/reviews/release-maintenance-bond-lens-contract-baseline-coverage-plan-controller-judgment-20260527.md`
> Code reviewed read-only: `fund_agent/fund/extraction_score.py`, `fund_agent/fund/quality_gate.py`

## Startup Packet Replay

| Item | State |
|---|---|
| Current phase | `release maintenance` |
| Current gate entering this review | `bond-lens score applicability design gate` |
| Latest accepted checkpoint | `c09a4cb` |
| Design truth | `docs/design.md` v2.2 |
| Control truth | `docs/implementation-control.md` |
| Prior accepted judgment | bond-lens contract + baseline coverage recovery plan accepted locally; convertible-bond / equity-exposure handling and FQ4 denominator validation required |

## Verdict

**PASS_WITH_FINDINGS**

No blocking or material findings. The plan is first-principles correct, properly scoped, and includes adequate safeguards against silent quality-gate weakening. All findings are informational or low severity. Re-review is not required.

## Review Focus Area Assessment

### 1. bond_risk_evidence replacement contract — first-principles correctness

**Assessment: Correct.**

The plan's core decision — exclude equity-shaped `holdings_snapshot` from bond_fund denominator and replace with explicit `bond_risk_evidence` contract — is first-principles sound:

- `docs/design.md` §3.4 confirms bond_fund preferred_lens is credit risk, duration, and max drawdown.
- `docs/design.md` §5.4.3 confirms bond fund methodology centers on duration, credit, leverage, liquidity, and drawdown, with Chapter 4 / Chapter 6 as core and Chapter 2 / Chapter 5 as high priority.
- Stock top-ten holdings (`top_holdings_status` / `top_holdings_source` allowlist in `_record_is_covered()`) measure equity investment behavior — a category error for bond risk questions.
- The plan does not allow silent N/A. Section 3.3 explicitly requires every equity holdings N/A to be paired with a replacement issue or evidence decision.

The 7 evidence groups cover the full bond-risk methodology matrix: `duration_rate_risk`, `credit_risk`, `leverage_liquidity`, `asset_allocation_holdings_mix`, `drawdown_stress`, `redemption_share_pressure`, and `convertible_bond_equity_exposure`. The `convertible_bond_equity_exposure` group satisfies the controller judgment F2 refinement requirement.

First implementation correctly defaults to `bond_risk_evidence_missing` for all bond_fund samples without reviewed bond-risk evidence, which is fail-closed behavior.

### 2. FQ2F / FQ4 interaction — quality gate projection without product policy change

**Assessment: Correct with one low-severity observation (F1).**

The plan proposes projecting `bond_risk_evidence_missing` as a warn-level FQ2F issue. This matches existing FQ2F P1 semantics in `quality_gate.py:639-650` where P1 fund-level failures emit `SEVERITY_WARN`. No new FQ rule code is introduced; no threshold or severity policy changes.

For FQ4, the plan excludes equity-shaped holdings_snapshot from both numerator and denominator for exact bond_fund. This changes FQ4 inputs for bond_fund but keeps thresholds unchanged (`FQ4_WARN_MISSING_FIELD_RATE = 0.20`, `FQ4_BLOCK_MISSING_FIELD_RATE = 0.35`). The plan requires raw/applicable denominator metadata to make the change observable.

The FQ4 denominator change could shift 006597's gate status. The plan explicitly requires anti-mis-pass evidence proving the status change is driven by correct applicability semantics plus replacement issue visibility, not by silent denominator suppression (Section 5.4). This is sufficient safeguard.

### 3. baseline_blocking separation from product FQ semantics

**Assessment: Correct with one informational observation (F2).**

The plan separates `baseline_blocking: bool` from FQ severity. `bond_risk_evidence_missing` uses `severity="warn"` (for FQ gate aggregation) and `baseline_blocking=true` (for baseline/golden eligibility). This correctly prevents baseline/golden misclassification without introducing a new FQ severity level.

Current `quality_gate.py` `_aggregate_gate_status()` only checks severity for pass/warn/block aggregation. The `baseline_blocking` field does not participate in this aggregation. This means the plan's design preserves FQ0-FQ6 product semantics while adding a parallel blocking mechanism for baseline/golden selection.

### 4. Unknown / conflicted fund type fail-closed path

**Assessment: Correct.**

The plan's fail-closed behavior is verified against `extraction_score.py` code:

- `_unique_optional_text()` (line 1343-1371) returns `None` on conflicting values with an explicit reason.
- `_is_non_applicable_index_quality_record()` (line 1466-1495) keeps records when fund_type is None (line 1493-1494).
- The plan extends this pattern: applicability exclusion only applies when `classified_fund_type` is exactly `bond_fund`. Unknown, conflicted, or missing fund types keep `holdings_snapshot` in the denominator.

The `unknown_fund_type_fail_closed` issue code (severity=info, baseline_blocking=true for baseline candidates) provides visibility without changing scoring behavior. This is correct conservative behavior.

### 5. Deterministic ids / schema compatibility and tests

**Assessment: Correct.**

Issue id format `score-applicability:{fund_code}:{report_year}:{field_name}:{issue_code}:{contract_id}` is deterministic and stable. Per-group format appends `:{group_id}`. Normalization rules are explicit and produce stable lowercase ids.

Schema compatibility is preserved:

- `field_applicability_decisions` and `score_applicability_issues` are additive optional top-level arrays in `score.json`.
- Existing `field_scores`, `fund_scores`, `fund_quality` remain present.
- `quality_gate.py` `_evaluate_score_payload()` reads specific keys (`field_scores`, `fund_scores`, `fund_quality`, `failed_funds`, `correctness`) — new keys are ignored.
- Older `score.json` without `score_applicability_issues` must still run (Section 8.4).

The validation matrix (Section 9) covers: bond_fund exclusion, active/index/enhanced preservation, unknown/conflicted conservative behavior, quality gate projection, malformed input fail-fast, 006597 anti-mis-pass, and regression for `004393` / `004194`.

## Findings

### F1: FundQualityRow field semantics shift for bond_fund FQ4 consumer

**Severity:** Low
**Section:** 5.3

The plan says "Implementation may keep current `total_field_count`, `missing_field_count`, and `missing_field_rate` as applicable counts for quality_gate compatibility." This means for bond_fund, `FundQualityRow.missing_field_rate` would semantically shift from "raw missing rate" to "applicable missing rate" because equity-shaped holdings_snapshot is excluded from both numerator and denominator.

Downstream `quality_gate.py` `_missing_rate_issues()` (line 729-773) reads `missing_field_rate` from `fund_quality` rows and applies FQ4 thresholds. For bond_fund, the rate could decrease because the equity holdings category error no longer inflates the missing count.

**Evidence:** The plan requires raw/applicable denominator metadata (`raw_total_field_count`, `raw_missing_field_count`, `raw_missing_field_rate`, `applicable_total_field_count`, `applicable_missing_field_count`, `applicable_missing_field_rate`, `excluded_non_applicable_fields`, `replacement_issue_ids`) to make this change observable. The plan also requires 006597 anti-mis-pass evidence proving gate status change is driven by correct semantics.

**Assessment:** The plan acknowledges the possibility (Section 5.4 point 4: "If FQ4 moves from block to warn or disappears, the implementation evidence must state that the product-level FQ4 threshold was not changed") and provides mitigation. This is a correct applicability-driven change, not a policy weakening. However, the implementation should be explicit in code comments that `FundQualityRow.missing_field_rate` is now "applicable missing rate" for bond_fund, not raw rate.

### F2: baseline_blocking consumption point undefined

**Severity:** Informational
**Section:** 5.1, 5.4

The plan introduces `baseline_blocking: bool` on `ScoreApplicabilityIssue` but does not specify which module or function checks this field to block baseline/golden promotion. Current `quality_gate.py` has no baseline/golden eligibility logic.

**Evidence:** The plan's scope does not authorize baseline/golden implementation, and `implementation-control.md` Current Non-Goals states "Do not promote local scoring, writing, or data-source run outputs into tracked fixtures without a later reviewed gate." Baseline/golden promotion is already blocked at the gate level.

**Assessment:** Non-blocking. The `baseline_blocking` field definition is correct for future consumption. The future baseline/golden gate must define the concrete consumption contract — i.e., which function reads `score_applicability_issues[].baseline_blocking` and how it gates baseline promotion. Until then, the field serves as a self-documenting contract that prevents future implementations from accidentally treating `bond_risk_evidence_missing` (warn) as baseline-eligible.

### F3: Local BOND_FUND_TYPE constant vs FundType import

**Severity:** Informational
**Section:** 4, 8.1

The plan proposes `BOND_FUND_TYPE = "bond_fund"` as a local constant in `extraction_score.py` rather than importing from `fund_agent/fund/fund_type.py`. If `fund_type.py` ever changes the `bond_fund` literal (unlikely but possible), this local constant would silently diverge.

**Evidence:** The plan explicitly prohibits modifying `fund_type.py` in the minimal slice (Section 8.1). The existing pattern in `extraction_score.py` already uses local constants like `HOLDINGS_SNAPSHOT_FIELD_NAME` and `INDEX_QUALITY_FIELD_NAMES` rather than centralizing in fund_type.py.

**Assessment:** Acceptable for the minimal slice. The implementation should add a code comment linking `BOND_FUND_TYPE` to `FundType` literal. If a future gate expands bond subtypes and requires `fund_type.py` changes, this constant should be refactored to use the canonical type.

### F4: BondRiskEvidenceGroup dataclass structure not fully specified

**Severity:** Informational
**Section:** 4

The plan defines `BOND_RISK_EVIDENCE_GROUPS` as `Final[tuple[BondRiskEvidenceGroup, ...]]` and specifies 7 groups in a table, but does not show the `BondRiskEvidenceGroup` dataclass field definitions. The table columns (group id, required_evidence, allowed_na_reason, failure_behavior) imply the dataclass structure but it is not explicitly stated.

**Evidence:** Section 5.1 shows `FieldApplicabilityDecision` and `ScoreApplicabilityIssue` dataclass definitions with full field lists. The `BondRiskEvidenceGroup` dataclass is referenced but its fields are only implied by the Section 4 table.

**Assessment:** The table provides sufficient information for code generation. The implementation should define `BondRiskEvidenceGroup` with fields: `group_id: str`, `required_evidence: str`, `allowed_na_reasons: tuple[str, ...]`, `failure_behavior: str`. This is an implementation detail, not a design gap.

### F5: First implementation always emits bond_risk_evidence_missing for bond_fund

**Severity:** Informational
**Section:** 4

The plan states "The first implementation should default current snapshot-only runs to `bond_risk_evidence_missing` unless accepted source facts already exist in `comparable_values` or a future reviewed evidence input is added by separate gate." This means every bond_fund in the current snapshot will receive the aggregate replacement issue.

**Evidence:** No current snapshot record carries reviewed bond-risk evidence in `comparable_values`. The plan's non-goals explicitly exclude "bond-risk extraction from annual reports" and "extractor logic changes."

**Assessment:** This is correct fail-closed behavior. The plan explicitly acknowledges this in Section 4 ("A current bond_fund with no reviewed bond-risk evidence must emit a replacement issue") and Section 5.2 ("Future positive coverage can be accepted only when at least one direct or reviewed-derived group has source anchors"). The emission is intentional and preserves quality observability.

## Scope Compliance Check

| Constraint | Status | Evidence |
|---|---|---|
| No renderer changes | Compliant | Section 10 non-goals explicitly excludes renderer |
| No FQ0-FQ6 policy change | Compliant | Section 6 states "Do not change FQ4 thresholds, FQ2 P0 block / P1 warn semantics, FQ5 preferred_lens semantics, product quality_gate_policy=block behavior" |
| No Service/CLI changes | Compliant | Section 10 non-goals |
| No Host/Agent/dayu | Compliant | Section 10 non-goals |
| No source strategy/helper | Compliant | Section 10 non-goals |
| No extractor logic | Compliant | Section 10 non-goals |
| No golden/baseline promotion | Compliant | Section 1 Startup Packet "blocked; no sample may be promoted" |
| No extra_payload | Compliant | Section 10 hard prohibitions |
| No GitHub mutation | Compliant | Section 10 hard prohibitions |
| File scope limited to extraction_score.py + quality_gate.py + tests | Compliant | Section 8.1; fund_type.py explicitly excluded |
| Includes convertible-bond / equity-exposure | Compliant | Section 4, 7th evidence group |
| FQ4 denominator validation required | Compliant | Section 5.3, 5.4 |

## Hard Constraints Verification

| Hard constraint | Verification |
|---|---|
| Plan follows AGENTS.md boundaries | Confirmed. Plan scopes changes to Agent layer fund capability (extraction_score.py, quality_gate.py). No UI, Service, Host boundary violations. |
| No silent N/A for bond_fund | Confirmed. Section 3.3 Non-Silent N/A Rule explicitly prohibits plain not_applicable without replacement issue. |
| FQ0-FQ6 semantics preserved | Confirmed. No threshold, severity, or rule code changes. Replacement issue uses existing FQ2F P1 warn semantics. |
| 006597 cannot pass only by denominator reduction | Confirmed. Section 5.4 requires 5-point evidence including deterministic replacement issue and explicit statement of threshold non-change. |
| Unknown/conflicted fail-closed | Confirmed. Section 5.2 explicitly states "do not exclude holdings_snapshot" and "Emit no bond-specific replacement issue unless the effective fund type is exactly bond_fund." |
| Deterministic ids stable for code generation | Confirmed. Section 7.2 defines stable format with normalization rules. |
| Issue taxonomy sufficient | Confirmed. Section 7.1 defines 8 issue codes covering equity exclusion, missing evidence, anchor gap, data gap, partial, sufficient, unknown type, and contract error. |

## Summary

The plan is well-structured and first-principles correct. It correctly identifies that equity-shaped `holdings_snapshot` is a category error for `bond_fund` scoring, and replaces it with a comprehensive bond-risk evidence contract that prevents silent quality-gate weakening. The 7 evidence groups cover the full bond methodology matrix. The fail-closed behavior for unknown/conflicted fund types is correct. Deterministic ids and additive schema changes preserve backward compatibility. All findings are informational or low severity — none require plan revision before implementation.

📢 债券评分适用性设计计划审查完成：通过，带五个低/信息级发现，无阻断问题。
