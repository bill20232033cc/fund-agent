# Bond Risk Evidence Extractor / Anchor Hardening — Slice 1 Targeted Re-Review (AgentDS)

> Date: 2026-05-28
> Role: re-review worker (AgentDS)
> Gate: Slice 1 targeted re-review for `bond risk evidence extractor / anchor hardening design gate`
> Source reviews: mimo-20260527, ds-20260527
> Fix artifact: `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-slice1-fix-20260527.md`

## Worker Self-Check

- Self-check: pass
- Role confirmed: re-review worker only, not controller.
- Prohibited actions avoided: no workflow command, no skill, no code/test/artifact modification, no stage, no commit, no push, no PR, no merge, no golden promotion.
- Allowed write path confirmed: only this re-review artifact.

## Per-Finding Verification

### Finding 1: Anchor ID Re-parse → Reuse `_parse_bond_risk_anchor_id`

| Aspect | Before | After | Verdict |
|---|---|---|---|
| Cross-group check | `anchor_id.split(":")[3]` (models.py:387) | `_parse_bond_risk_anchor_id(anchor_id, fund_code, report_year)` (models.py:391) | **已修复** |
| Function signature | `(group, anchor_ids)` | `(group, anchor_ids, fund_code, report_year)` (models.py:364–369) | **已修复** |
| Call site | `_validate_bond_risk_group_anchor_refs(group, anchor_ids)` | `_validate_bond_risk_group_anchor_refs(group, anchor_ids, value.fund_code, value.report_year)` (models.py:218) | **已修复** |

The cross-group check now goes through the shared `_parse_bond_risk_anchor_id()` function, which validates the 5-part format, `bond-risk` prefix, fund_code match, report_year match, and positive integer ordinal. If the anchor ID format evolves, only `_parse_bond_risk_anchor_id` needs updating.

Additional effect: because `_parse_bond_risk_anchor_id` validates fund_code and report_year, a referenced anchor with a mismatched fund_code or year now fails during the group-anchor cross-reference check rather than only during the anchor list validation pass. This makes error detection more thorough for referenced anchors.

### Finding 2: Edge-Path Test Coverage

| Controller-Accepted Test | Implemented As | Line | Verdict |
|---|---|---|---|
| `weak_group_ids` mismatch | `test_caller_provided_weak_group_ids_must_match_statuses` | test:76–92 | **已修复** |
| `ambiguous_group_ids` mismatch | `test_caller_provided_ambiguous_group_ids_must_match_statuses` | test:95–111 | **已修复** |
| Cross-group anchor rejection | `test_cross_group_anchor_reference_fails_validation` | test:114–124 | **已修复** |
| Malformed/wrong anchor ID | `test_malformed_or_wrong_anchor_id_fails_validation` (3 parametrized cases: wrong parts count, wrong fund_code, wrong year) | test:127–143 | **已修复** |
| Duplicate group ID | `test_duplicate_group_id_fails_validation` | test:55–63 | **已修复** |
| Invalid status | `test_invalid_status_fails_validation` | test:146–154 | **已修复** |
| Invalid strength | `test_invalid_strength_fails_validation` | test:157–165 | **已修复** |

All 7 controller-accepted edge-path tests are present, correctly structured (arrange → act → assert with `pytest.raises`), and pass.

### Finding 3: Constant Drift — Deferred to Slice 5

| Check | Result |
|---|---|
| `extraction_score.py` modified by fix? | No (`git diff --name-only HEAD -- fund_agent/fund/extraction_score.py` returned empty) |
| Deferral correctly documented in fix artifact? | Yes (fix artifact line 13: "Deferred Slice 5 item extraction_score.py constant drift: not changed") |
| Residual risk status | Correctly deferred; no Slice 1 regression |

## Validation Re-run

| Command | Result |
|---|---|
| `uv run pytest tests/fund/extractors/test_bond_risk_evidence.py -q` | 15 passed in 0.74s |
| `uv run ruff check fund_agent/fund/extractors/models.py tests/fund/extractors/test_bond_risk_evidence.py` | All checks passed! |

## No New Blocker Check

| Check | Result |
|---|---|
| Duplicate-ID check reordered before set-membership check | No regression — both checks remain fail-closed; error message is now more specific for the duplicate case |
| Existing 8 tests still pass? | Yes, all 15 pass (8 original + 7 new) |
| Any plan invariant weakened? | No — validation rules unchanged; only test coverage and code reuse improved |
| Any scope creep? | No — only models.py, test file, and fix artifact changed |
| Any extraction_score.py edit? | No — confirmed by git diff |
| Any FQ0-FQ6 change? | No — scoring module untouched |
| Any golden promotion? | No |

## Status Summary

| Finding | Status |
|---|---|
| DS F2 / MiMo equivalent: anchor reparse → `_parse_bond_risk_anchor_id` | **已修复** |
| Edge-path tests: weak_group_ids, ambiguous_group_ids, cross-group anchor, malformed anchor ID, duplicate group ID, invalid status, invalid strength | **已修复** |
| Constant drift models.py ↔ extraction_score.py | **Deferred to Slice 5** (confirmed no extraction_score.py edit) |

## Conclusion

All three controller-accepted findings are correctly resolved. Two are **已修复** with verified code changes and passing tests. One is correctly **deferred** to Slice 5 with no unauthorized edit to `extraction_score.py`. No new blockers introduced. All 15 tests pass, ruff is clean, scope boundary is respected.

📢 重新审查通过，两项修复均已确认，常量漂移已正确延迟至 Slice 5，无新阻塞发现。
