# Bond Risk Evidence Extractor / Anchor Hardening Slice 1 Code Review

> Date: 2026-05-27
> Role: code review worker
> Gate: code review for implementation Slice 1 Model Contract of work unit `bond risk evidence extractor / anchor hardening design gate`
> Reviewer: mimo
> Status: PASS

## Reviewer Self-Check

- Self-check: pass
- Role confirmed: code review worker only, not controller.
- Scope confirmed: Slice 1 Model Contract only; no code, test, plan, or implementation artifact modification.
- Prohibited actions avoided: no workflow command, no skill, no stage, no commit, no push, no PR, no merge, no golden promotion.
- Allowed write path confirmed: `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-slice1-code-review-mimo-20260527.md`.

## Reviewed Files

- `fund_agent/fund/extractors/models.py` (implementation target)
- `tests/fund/extractors/test_bond_risk_evidence.py` (test target)
- `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-plan-20260527.md` (accepted plan)
- `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-slice1-implementation-20260527.md` (implementation artifact)
- `fund_agent/fund/extraction_score.py` (constant duplication check)

## Plan Invariant Verification

| # | Invariant | Verdict | Evidence |
|---|---|---|---|
| 1 | Exactly seven groups | PASS | `BOND_RISK_EVIDENCE_GROUP_IDS` lines 43-51 contains exactly 7 entries. `_validate_bond_risk_group_records` checks `len(group_ids) != len(BOND_RISK_EVIDENCE_GROUP_IDS)` at line 253. |
| 2 | Group ids match required set | PASS | `_validate_bond_risk_group_records` checks `set(group_ids) != set(BOND_RISK_EVIDENCE_GROUP_IDS)` at line 255 and `len(set(group_ids)) != len(group_ids)` at line 257 (no duplicates). |
| 3 | Stable anchor id format | PASS | `_parse_bond_risk_anchor_id` at line 336 validates `bond-risk:<fund_code>:<report_year>:<group_id>:<ordinal>` with 5-part split, prefix check, fund code match, year match, and positive integer ordinal. |
| 4 | Accepted/weak groups require at least one anchor | PASS | `_validate_bond_risk_group_anchor_refs` at line 381 checks `group.status in _BOND_RISK_ACCEPTED_ANCHORED_STATUSES` (`accepted`, `accepted_absence`, `weak`) requires non-empty `source_anchor_ids`. |
| 5 | Anchor ids must exist in `BondRiskEvidenceValue.anchors` | PASS | Line 384-386 verifies each `anchor_id in anchor_ids`. |
| 6 | Cross-group anchor references rejected | PASS | Line 387-389 extracts `anchor_id.split(":")[3]` and verifies `anchor_group_id == group.group_id`. |
| 7 | `accepted_absence` requires `quantitative_absence` + `explicit_absence` | PASS | `_validate_bond_risk_status_strength` at line 287-289 enforces both constraints. |
| 8 | `weak` drawdown-control remains unsatisfied | PASS | Test `test_weak_drawdown_control_record_validates_but_is_unsatisfied` at line 65 verifies `drawdown_stress` not in `satisfied_group_ids`, in `weak_group_ids`, and `contract_status == "partial"`. |
| 9 | Derived id tuples reject caller inconsistency | PASS | `_require_same_group_ids` at line 429 compares caller-provided tuples against `_derive_bond_risk_group_id_sets` output. Test at line 55 verifies `satisfied_group_ids` mismatch raises `ValueError`. |
| 10 | `contract_status` derivation correct | PASS | `_derive_bond_risk_contract_status` at line 455: all 7 satisfied → `"satisfied"`, any satisfied/weak/ambiguous → `"partial"`, else `"missing"`. Verified by three tests with different group compositions. |
| 11 | Chinese docstrings with template第6章 reference | PASS | All new public types and validator functions have Chinese docstrings referencing 模板第6章核心风险. |
| 12 | No scope creep into extractor/snapshot/score | PASS | Only `models.py` and test file changed. No changes to `data_extractor.py`, `extraction_snapshot.py`, `extraction_score.py`, or any extractor module. |

## Findings

### Finding F-1: `BOND_RISK_EVIDENCE_CONTRACT_ID` constant duplication (maintainability)

- Severity: non-blocking / maintainability
- Location: `fund_agent/fund/extractors/models.py:42` and `fund_agent/fund/extraction_score.py:114`
- Description: `BOND_RISK_EVIDENCE_CONTRACT_ID` is defined independently in both files with identical value `"bond_risk_evidence.v1"` but incompatible type annotations (`BondRiskEvidenceSchemaVersion` = `Literal["bond_risk_evidence.v1"]` vs `Final[str]`). The seven group ID strings also exist in both files: once as a plain tuple in `models.py` (`BOND_RISK_EVIDENCE_GROUP_IDS`) and once as `group_id` fields inside `BondRiskEvidenceGroup` dataclass instances in `extraction_score.py` (`BOND_RISK_EVIDENCE_GROUPS`). If a group ID were renamed or added in one file but not the other, the two modules would silently diverge.
- Recommendation: In Slice 5 (Score Applicability), `extraction_score.py` should import `BOND_RISK_EVIDENCE_CONTRACT_ID` and `BOND_RISK_EVIDENCE_GROUP_IDS` from `extractors/models.py` and derive its group objects from the canonical group ID tuple. This is a Slice 5 concern, not a Slice 1 blocker.
- Gateflow evidence: `extraction_score.py` line 114 defines `BOND_RISK_EVIDENCE_CONTRACT_ID: Final[str] = "bond_risk_evidence.v1"`. `models.py` line 42 defines `BOND_RISK_EVIDENCE_CONTRACT_ID: BondRiskEvidenceSchemaVersion = "bond_risk_evidence.v1"`. Values match today; no runtime divergence exists.

### Finding F-2: No test for `weak_group_ids` or `ambiguous_group_ids` caller inconsistency (test gap)

- Severity: non-blocking / test gap
- Location: `tests/fund/extractors/test_bond_risk_evidence.py:55`
- Description: The plan requires "Derived id tuples cannot be inconsistent." Test `test_caller_provided_derived_group_ids_must_match_statuses` verifies `satisfied_group_ids` mismatch, but no test verifies that caller-provided `weak_group_ids` or `ambiguous_group_ids` mismatches are rejected. The validator does enforce this (lines 422-424), but the behavior is not tested.
- Recommendation: Add two additional test cases in a future test pass or Slice 6: one with a tampered `weak_group_ids` and one with a tampered `ambiguous_group_ids`, both expecting `ValueError`.
- Gateflow evidence: `_require_same_group_ids` is called for all four derived tuple fields at lines 421-424. Only `satisfied_group_ids` mismatch has a test at line 55.

### Finding F-3: No test for cross-group anchor rejection (test gap)

- Severity: non-blocking / test gap
- Location: `tests/fund/extractors/test_bond_risk_evidence.py`
- Description: The validator at `models.py:387-389` rejects anchor references where the anchor's group id differs from the referencing group's group id. No test exercises this path.
- Recommendation: Add a test where group A references an anchor belonging to group B, expecting `ValueError` with message "引用其他风险组锚点".
- Gateflow evidence: `_validate_bond_risk_group_anchor_refs` lines 387-389 contain the cross-group check. No corresponding test exists.

### Finding F-4: Redundant final return in `_derive_bond_risk_contract_status` (cosmetic)

- Severity: non-blocking / cosmetic
- Location: `fund_agent/fund/extractors/models.py:479-480`
- Description: The function ends with `if missing_ids: return "missing"` followed by `return "missing"`. The second return is unreachable because the seven-group invariant guarantees at least one group exists, and the prior elif already covers the case where `satisfied_ids or weak_ids or ambiguous_ids` is non-empty. If all four are empty (impossible with 7 groups), the final return is still correct by convention.
- Recommendation: No change required. Defensive code style is acceptable.

## Scope Boundary Verification

The implementation artifact claims only these files were changed:

- `fund_agent/fund/extractors/models.py`
- `tests/fund/extractors/test_bond_risk_evidence.py`
- `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-slice1-implementation-20260527.md`

No changes were made to:

- `fund_agent/fund/extractors/bond_risk_evidence.py` (not created — correct for Slice 1)
- `fund_agent/fund/data_extractor.py` (Slice 3 scope)
- `fund_agent/fund/extraction_snapshot.py` (Slice 4 scope)
- `fund_agent/fund/extraction_score.py` (Slice 5 scope)
- `fund_agent/ui/`, `fund_agent/services/`, `fund_agent/host/`, `fund_agent/agent/` (out of scope)
- Golden/baseline fixtures (out of scope)

Scope boundary: PASS.

## Type Safety Verification

- `BondRiskEvidenceGroupId` is a `Literal` with exactly seven values — type-safe and exhaustive.
- `BondRiskEvidenceStatus` is a `Literal` with five values — matches `_BOND_RISK_EVIDENCE_STATUSES` frozenset.
- `BondRiskEvidenceStrength` is a `Literal` with six values — matches `_BOND_RISK_EVIDENCE_STRENGTHS` frozenset.
- `BondRiskEvidenceMeasurementKind` is a `Literal` with seven values — matches `_BOND_RISK_EVIDENCE_MEASUREMENT_KINDS` frozenset.
- `BondRiskEvidenceContractStatus` is a `Literal` with three values.
- `BondRiskEvidenceSchemaVersion` is a `Literal` with one value.
- All dataclasses use `frozen=True, slots=True` — immutable and memory-efficient.
- Status/strength/measurement_kind compatibility is validated at runtime by `_validate_bond_risk_status_strength`.

Type safety: PASS.

## Test Coverage Assessment

| Scenario | Test | Verdict |
|---|---|---|
| Complete seven-group value validates | `test_complete_seven_group_bond_risk_evidence_value_validates` | PASS |
| Missing anchor for accepted group fails | `test_missing_anchor_for_accepted_group_fails_validation` | PASS |
| Incomplete group set fails | `test_incomplete_group_set_fails_validation` | PASS |
| Caller-provided derived ids inconsistent | `test_caller_provided_derived_group_ids_must_match_statuses` | PASS |
| Weak drawdown unsatisfied | `test_weak_drawdown_control_record_validates_but_is_unsatisfied` | PASS |
| Explicit absence convertible/equity accepted | `test_explicit_absence_convertible_equity_record_is_accepted` | PASS |

Required by plan: 4 scenarios. Implemented: 6 tests. Exceeds minimum.

Additional test scenarios identified as gaps (F-2, F-3) but not blocking for Slice 1 acceptance.

## Residual Risks

1. **Constant duplication** (F-1): `BOND_RISK_EVIDENCE_CONTRACT_ID` and group ID strings are independently defined in `models.py` and `extraction_score.py`. Currently identical; divergence risk exists if either file is modified without the other. Must be resolved in Slice 5 when `extraction_score.py` is updated to consume the new contract types.

2. **Test gaps** (F-2, F-3): `weak_group_ids`/`ambiguous_group_ids` inconsistency and cross-group anchor rejection are validated by code but not covered by tests. These are additive test scenarios and do not indicate missing validation logic.

3. **No extractor implementation in this slice**: The model contract is defined but no extractor produces `BondRiskEvidenceValue` instances yet. This is expected Slice 1 boundary.

4. **No `StructuredFundDataBundle` integration**: `bond_risk_evidence` field does not exist on the bundle yet. This is Slice 3 scope.

5. **No snapshot/score integration**: The contract types are not yet consumed by snapshot projection or score applicability logic. This is Slice 4/5 scope.

6. **`drawdown_stress` qualitative control intent**: The plan correctly requires this to remain `weak`. The model contract supports this; actual enforcement depends on extractor implementation in Slice 2.

## Conclusion

**PASS.** Slice 1 Model Contract implementation satisfies all plan invariants. The type model is correctly defined with seven groups, stable anchor validation, derived id tuple enforcement, status/strength compatibility checks, and Chinese docstrings. Four non-blocking findings identified: one constant duplication concern (F-1, Slice 5 scope), two test gaps (F-2, F-3), and one cosmetic observation (F-4). No blocking findings. No scope creep detected. No golden promotion, threshold weakening, or FQ0-FQ6 semantic change.
