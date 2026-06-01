# Bond Risk Evidence Extractor / Anchor Hardening — Slice 1 Code Review (AgentDS)

> Date: 2026-05-28
> Role: code review worker (AgentDS)
> Gate: second code review for `bond risk evidence extractor / anchor hardening design gate`
> Scope: implementation Slice 1 Model Contract
> Reviewed artifact: `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-slice1-implementation-20260527.md`
> Approved plan: `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-plan-20260527.md`

## Worker Self-Check

- Self-check: pass
- Role confirmed: code review worker only, not controller.
- Prohibited actions avoided: no code modification, no test modification, no staging, no commit, no push, no PR, no merge, no golden promotion.
- Allowed write path confirmed: only this review artifact.
- Reviewed all target files against plan invariants.

## Review Target Files

- `fund_agent/fund/extractors/models.py` — model contract types + validator
- `tests/fund/extractors/test_bond_risk_evidence.py` — 6 tests

## Validation Commands Re-run

| Command | Result |
|---|---|
| `uv run ruff check fund_agent/fund/extractors/models.py tests/fund/extractors/test_bond_risk_evidence.py` | All checks passed |
| `uv run pytest tests/fund/extractors/test_bond_risk_evidence.py -q` | 6 passed in 0.53s |
| `uv run python -c "from fund_agent.fund.extractors.models import validate_bond_risk_evidence_value"` | import ok |

## Plan Invariant Checklist

### Type Model Completeness

| Planned Type | Present | Line |
|---|---|---|
| `BondRiskEvidenceStatus` | PASS | models.py:12 |
| `BondRiskEvidenceStrength` | PASS | models.py:13–20 |
| `BondRiskEvidenceGroupId` | PASS | models.py:21–29 |
| `BondRiskEvidenceAnchorRef` | PASS | models.py:104–122 |
| `BondRiskEvidenceGroupRecord` | PASS | models.py:125–155 |
| `BondRiskEvidenceValue` | PASS | models.py:158–189 |
| `validate_bond_risk_evidence_value` | PASS | models.py:192–236 |

Additional types beyond plan minimum:
- `BondRiskEvidenceMeasurementKind` (models.py:30–38) — supports `measurement_kind` field
- `BondRiskEvidenceContractStatus` (models.py:39) — supports `contract_status` field
- `BondRiskEvidenceSchemaVersion` (models.py:40) — typed `schema_version`/`contract_id`

These additions are reasonable and support the planned fields without scope creep.

### Exactly Seven Groups

| Group ID | In Literal | In Tuple | Plan Match |
|---|---|---|---|
| `duration_rate_risk` | PASS | PASS | PASS |
| `credit_risk` | PASS | PASS | PASS |
| `leverage_liquidity` | PASS | PASS | PASS |
| `asset_allocation_holdings_mix` | PASS | PASS | PASS |
| `drawdown_stress` | PASS | PASS | PASS |
| `redemption_share_pressure` | PASS | PASS | PASS |
| `convertible_bond_equity_exposure` | PASS | PASS | PASS |

Validation enforces exact count (`len(group_ids) != len(BOND_RISK_EVIDENCE_GROUP_IDS)`, line 253), exact set membership, and no duplicates.

### Anchor ID Validation

| Rule | Enforced | Location |
|---|---|---|
| Format `bond-risk:<fund_code>:<report_year>:<group_id>:<ordinal>` | PASS | `_parse_bond_risk_anchor_id` (line 351) |
| fund_code must match value | PASS | line 355–356 |
| report_year must match value | PASS | line 357–358 |
| ordinal must be positive integer | PASS | line 359–360 |
| group_id must be known | PASS | line 323–325 |
| No duplicate anchor IDs | PASS | line 319–321 |
| Non-empty anchor_id, section_id, row_locator, evidence_role | PASS | lines 317–331 |

### Accepted/Weak Anchor Requirements

| Rule | Enforced | Location |
|---|---|---|
| Accepted/weak records must have ≥1 source_anchor_id | PASS | lines 381–382 |
| Referenced anchors must exist in value.anchors | PASS | lines 384–386 |
| No cross-group anchor references | PASS | lines 387–389 |

### Derived ID Tuples

| Rule | Enforced | Location |
|---|---|---|
| `satisfied_group_ids` derived from status | PASS | `_derive_bond_risk_group_id_sets` + `_require_same_group_ids` |
| `missing_group_ids` derived from status | PASS | same |
| `weak_group_ids` derived from status | PASS | same |
| `ambiguous_group_ids` derived from status | PASS | same |
| Caller-provided values rejected when inconsistent | PASS | `_require_same_group_ids` (line 448–452) |

### contract_status Derivation

| Condition | Expected | Actual |
|---|---|---|
| All 7 satisfied | `satisfied` | PASS |
| Some satisfied + some weak/ambiguous | `partial` | PASS |
| All missing | `missing` | PASS |
| Caller mismatch rejected | ValueError | PASS |

### Status/Strength Compatibility

| Status | Allowed Strengths | Enforced |
|---|---|---|
| `accepted` | `quantitative_direct`, `qualitative_direct` | PASS (line 285) |
| `accepted_absence` | `quantitative_absence` + `explicit_absence` measurement | PASS (lines 287–289) |
| `weak` | `qualitative_direct`, `qualitative_control_intent`, `ambiguous` | PASS (lines 290–295) |
| `ambiguous` | `ambiguous` only | PASS (lines 296–297) |
| `missing` | `missing` only | PASS (lines 298–299) |

### Chinese Docstrings + 模板第6章 Reference

| Location | Has Chinese | References 第6章 |
|---|---|---|
| `BondRiskEvidenceAnchorRef` | PASS | PASS (line 106) |
| `BondRiskEvidenceGroupRecord` | PASS | PASS (line 127) |
| `BondRiskEvidenceValue` | PASS | PASS (line 160) |
| `validate_bond_risk_evidence_value` | PASS | PASS (line 193) |
| `_validate_bond_risk_group_records` | PASS | PASS (line 240) |
| `_validate_bond_risk_status_strength` | PASS | PASS (line 273) |
| `_validate_bond_risk_anchor_refs` | PASS | PASS (line 303) |
| `_parse_bond_risk_anchor_id` | PASS | PASS (line 337) |
| `_validate_bond_risk_group_anchor_refs` | PASS | PASS (line 368) |
| `_derive_bond_risk_group_id_sets` | PASS | PASS (line 400) |
| `_require_same_group_ids` | PASS | PASS (line 434) |
| `_derive_bond_risk_contract_status` | PASS | PASS (line 462) |

### No Scope Creep

| Check | Result |
|---|---|
| Only models.py and test file modified | PASS |
| No extractor/bond_risk_evidence.py created | PASS |
| No data_extractor.py modified | PASS |
| No extraction_snapshot.py modified | PASS |
| No extraction_score.py modified | PASS |
| No README/docs/design/implementation-control modified | PASS |

## Test Coverage Analysis

### Required Tests (Plan Slice 1)

| Test | Present | Status |
|---|---|---|
| Complete seven-group value validates | `test_complete_seven_group_bond_risk_evidence_value_validates` | PASS |
| Missing anchor for accepted group fails | `test_missing_anchor_for_accepted_group_fails_validation` | PASS |
| Weak drawdown not in satisfied ids | `test_weak_drawdown_control_record_validates_but_is_unsatisfied` | PASS |
| Explicit absence convertible/equity accepted | `test_explicit_absence_convertible_equity_record_is_accepted` | PASS |
| Incomplete group set fails | `test_incomplete_group_set_fails_validation` | PASS (bonus) |
| Caller-provided derived IDs rejected | `test_caller_provided_derived_group_ids_must_match_statuses` | PASS (bonus) |

### Test Coverage Gaps (non-blocking for Slice 1)

These validation paths exist in the validator but lack dedicated unit tests:

| Path | Risk |
|---|---|
| Malformed anchor ID (wrong prefix, wrong part count) | Low — covered indirectly via anchor resolution |
| Anchor fund_code/report_year mismatch with value | Low |
| `contract_status = "missing"` (all groups missing) | Low |
| Duplicate group_id in groups tuple | Low |
| Cross-group anchor reference | Low |
| Empty anchor required fields (section_id, row_locator, evidence_role) | Low |
| Invalid status/strength combinations per `_validate_bond_risk_status_strength` | Low |
| `report_year <= 0` or empty `fund_code` | Low |

The 4 required test scenarios from the plan are well covered. The 2 bonus tests (incomplete group set, caller-provided ID mismatch) strengthen the suite. The gaps above are edge cases that don't affect Slice 1 correctness and can be filled in Slice 2 or later when the extractor exercises these paths with real/synthetic data.

**Note on test not being weakened:** The 6 tests are strict and target plan-required invariants directly. No test was lowered from acceptance criteria. The weak drawdown test correctly asserts `"drawdown_stress" not in value.satisfied_group_ids` and `value.weak_group_ids == ("drawdown_stress",)`.

## Finding 1 (Medium — Maintainability): Constant Duplication Between models.py and extraction_score.py Creates Drift Risk

**Evidence:**
- `models.py:42`: `BOND_RISK_EVIDENCE_CONTRACT_ID: BondRiskEvidenceSchemaVersion = "bond_risk_evidence.v1"`
- `extraction_score.py:114`: `BOND_RISK_EVIDENCE_CONTRACT_ID: Final[str] = "bond_risk_evidence.v1"`
- `models.py:43–51`: `BOND_RISK_EVIDENCE_GROUP_IDS` — tuple of 7 string literals
- `extraction_score.py:172–255`: `BOND_RISK_EVIDENCE_GROUPS` — tuple of `BondRiskEvidenceGroup` dataclasses with the same 7 `group_id` values plus metadata

**Impact:** If the contract ID string or group list changes in a future gate, both files must be updated independently. The two constants serve different purposes (models.py defines the typed literal alias; extraction_score.py uses a richer dataclass with severity/baseline_blocking metadata), so simple import replacement isn't trivial. However, Slice 5 (Score Applicability) is where these two must converge.

**Recommendation:** Slice 5 implementation must import `BOND_RISK_EVIDENCE_CONTRACT_ID` and `BOND_RISK_EVIDENCE_GROUP_IDS` from `models.py` for contract identity checks, while keeping `BOND_RISK_EVIDENCE_GROUPS` (the rich dataclass tuple) in `extraction_score.py` only if the metadata fields are genuinely used by the scorer. If the scorer only needs group IDs, it should use the models.py tuple. Add a cross-module consistency test in Slice 5 that asserts `{g.group_id for g in BOND_RISK_EVIDENCE_GROUPS} == set(BOND_RISK_EVIDENCE_GROUP_IDS)`.

**Severity:** Medium. Not blocking for Slice 1 (which only defines the model contract), but must be resolved in Slice 5 to prevent silent drift.

## Finding 2 (Low — Code Quality): Anchor ID Re-parsing in `_validate_bond_risk_group_anchor_refs` Bypasses Shared Parser

**Evidence:** `models.py:387`:
```python
anchor_group_id = anchor_id.split(":")[3]
```
This re-parses the anchor ID by direct string split rather than calling `_parse_bond_risk_anchor_id()`, which provides format validation and consistent error messages. The cross-group check at line 388 works correctly (`anchor_group_id and anchor_group_id != group.group_id`), but if the anchor ID format evolves, this split-on-colon would need a separate update.

**Severity:** Low. No correctness issue; purely a maintainability concern.

## Finding 3 (Low — Test Coverage Gap): Edge Case Validation Paths Not Covered

**Evidence:** See Test Coverage Gaps table above. Eight validation branches in the validator have no dedicated test asserting their error case.

**Severity:** Low. The 4 plan-required test scenarios are all covered, and the 2 bonus tests add useful coverage. The missing edge case tests don't compromise Slice 1 correctness. They should be added in Slice 2 when extractor implementation generates real values that exercise these paths.

## Adversarial Failure Pass

| Attack Vector | Defended? |
|---|---|
| Caller provides `satisfied_group_ids` that don't match group statuses | YES — `_require_same_group_ids` rejects |
| Caller includes accepted group with no anchors | YES — `_validate_bond_risk_group_anchor_refs` rejects |
| Caller references anchor not in value.anchors | YES — line 385–386 |
| Caller uses wrong number of groups | YES — count + set + duplicate checks |
| Caller marks weak drawdown as accepted | YES — `_validate_bond_risk_status_strength` rejects weak → accepted mismatch for qualitative_control_intent strength (line 285: accepted requires quantitative_direct or qualitative_direct) |
| Caller uses wrong schema_version | YES — line 205–206 |
| Caller passes non-positive report_year | YES — line 211–212 |
| Caller passes empty fund_code | YES — line 209–210 |
| Caller creates anchor with wrong fund_code in ID | YES — `_parse_bond_risk_anchor_id` line 355–356 |
| Caller creates anchor with wrong report_year in ID | YES — `_parse_bond_risk_anchor_id` line 357–358 |

No bypass path found for plan invariants.

## Residual Risks

1. **Constant drift (Slice 5)**: `BOND_RISK_EVIDENCE_CONTRACT_ID` and group IDs independently defined in `models.py` and `extraction_score.py`. Must be reconciled in Slice 5 via import + cross-module consistency test.

2. **Test edge cases (Slice 2)**: Anchor format validation, cross-group reference, duplicate group IDs, and status/strength incompatibility paths lack dedicated tests. Slice 2 extractor tests should cover these.

3. **`_validate_bond_risk_group_anchor_refs` re-parsing**: Minor maintainability item at line 387; no functional defect.

4. **Slice 1 only — no integration behavior**: The model types and validator are correct in isolation, but their integration with extractor (Slice 2), bundle (Slice 3), snapshot (Slice 4), and score (Slice 5) is not yet verified. The plan's stop condition (Python version / typing support) is satisfied: all Literal types and dataclasses import cleanly.

## Conclusion

**PASS.** The Slice 1 implementation correctly satisfies all plan invariants:

- Seven groups with exact matching IDs
- Stable anchor ID format validation with fund_code/year/ordinal enforcement
- Accepted/weak anchor requirements (non-empty, resolvable, no cross-group references)
- `accepted_absence` with required `quantitative_absence` strength and `explicit_absence` measurement kind
- Weak drawdown (qualitative_control_intent) remains unsatisfied
- Derived ID tuples (`satisfied_group_ids`, etc.) enforced by validator, not caller-provided
- `contract_status` derivation from group statuses with caller mismatch rejection
- Chinese docstrings referencing template第6章核心风险 throughout
- No scope creep beyond models.py and test file

No blocking findings. Three non-blocking findings documented above with remediation recommendations for later slices.

📢 代码审查通过，Slice 1 模型契约实现满足所有计划不变量，无阻塞发现。三个非阻塞发现：常量在 models 和 extraction_score 间重复、部分边界情况缺少测试、一处锚点 ID 解析未复用共享解析器。
