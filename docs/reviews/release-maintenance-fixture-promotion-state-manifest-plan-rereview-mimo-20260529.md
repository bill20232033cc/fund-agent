# Fixture Promotion State Manifest Plan — Re-Review (MiMo)

Reviewer: AgentMiMo
Date: 2026-05-29
Timestamp: 20260529-133651

## Reviewed Target

`docs/reviews/release-maintenance-fixture-promotion-state-manifest-plan-20260529.md` (revised version)

## Prior Reviews

- `docs/reviews/release-maintenance-fixture-promotion-state-manifest-plan-review-mimo-20260529.md` — MiMo initial review: `accepted-with-required-fixes`
- `docs/reviews/release-maintenance-fixture-promotion-state-manifest-plan-review-ds-20260529.md` — DS initial review: `pass-with-risks`

## Scope

Re-review of revised plan verifying that four accepted fixes are correctly incorporated:

1. MiMo Finding 1: `source_quality_gate_path` path corrected for 006597 + source path existence validation added
2. DS Finding 1: deterministic `fixture_state` mapping rules added
3. DS Finding 2: concrete blocker conflict stop conditions added
4. DS Finding 3: `blocking_reason` generation rule added

## Verification Results

### Fix 1 — 006597 quality_gate path + source path validation

**Status: VERIFIED CORRECT**

- Revised plan line 162 (example JSON): `"source_quality_gate_path": "reports/quality-gate-runs/bond-risk-drawdown-nav-006597-2024-20260529/quality_gate.json"` — correct.
- Revised plan line 236 (Bond Evidence Handling): same correct path, with explicit guard: "The 006597 `source_quality_gate_path` must remain exactly `reports/quality-gate-runs/bond-risk-drawdown-nav-006597-2024-20260529/quality_gate.json`; do not substitute the extraction-snapshot directory quality gate path."
- Revised plan line 251 (fail-closed join): "If any non-null `source_snapshot_path`, `source_score_path`, or `source_quality_gate_path` does not exist on disk, stop."
- Revised plan line 391 (validation checklist): "every non-null `source_snapshot_path`, `source_score_path`, and `source_quality_gate_path` exists on disk"
- Filesystem verification: `reports/quality-gate-runs/bond-risk-drawdown-nav-006597-2024-20260529/quality_gate.json` EXISTS. `reports/extraction-snapshots/bond-risk-drawdown-nav-006597-2024-20260529/` contains only `errors.jsonl`, `snapshot.jsonl`, `summary.md` — no `quality_gate.json`. The revised plan is correct.

### Fix 2 — Deterministic fixture_state mapping

**Status: VERIFIED CORRECT**

Revised plan lines 209-216 add explicit derivation rules:

1. `decision="needs_fixture_promotion_gate"` + preflight `fixture_promotion_state="absent"` → `absent`
2. `decision="defer_from_v1"` → `deferred_from_v1`
3. `quality_gate_block` stays in blockers but does not upgrade to `ready_for_future_promotion`
4. `ready_for_future_promotion` forbidden for all current rows
5. `promoted` forbidden for all current rows
6. Future changed rows require new gate or controller decision

Row mapping table (lines 286-297) assigns concrete values: `absent` for 004393/004194/006597, `deferred_from_v1` for all others. No "A or B" ambiguity remains.

DS prior finding 1 was: "017641 的 fixture_state 列为 deferred_from_v1 or blocked — 两个值都是 plan 认为允许的，但没有选择规则。" The revised plan eliminates this by rule 2 above — `decision="defer_from_v1"` deterministically maps to `fixture_state="deferred_from_v1"`.

The QDII/FOF/110020 Handling section (lines 332-354) still uses "becomes `deferred_from_v1` or `blocked`" wording, but the deterministic rules and row mapping table override this as the binding specification. This is acceptable — the handling section is explanatory, the derivation rules and row mapping are authoritative.

### Fix 3 — Concrete blocker reconciliation stop conditions

**Status: VERIFIED CORRECT**

Revised plan lines 256-264 define concrete conditions:

- Preflight `severity="block"` item missing from residual `current_blockers` → stop
- Residual `current_blockers` item missing from preflight → stop (unless global/policy-only)
- Global/policy-only exceptions explicitly enumerated: `qdii_replacement_hard_stop`, top-level `fixture_promotion_absent`, `policy_status`, `replacement_disposition`
- These exceptions must not be inserted into fund-row blocker reconciliation unless already present in that row's preflight blockers
- Fund code / slot id / year mismatch → stop
- Duplicate or missing join keys → stop
- `006597` has `bond_risk_evidence_missing` in current blockers → stop
- Warning-only differences: record in evidence but continue

This replaces the vague "conflict materially" from the original plan with enumerable, testable conditions.

### Fix 4 — blocking_reason generation rule

**Status: VERIFIED CORRECT**

Revised plan lines 273-282 define a concrete construction algorithm:

1. Start from residual `decision_reason`
2. Append concise summaries of every preflight blocker message, preserving codes
3. Per-row special context for 006597, 017641, QDII rows, FOF_SLOT, 110020
4. Evidence must record the generation rule and provide either generated `blocking_reason` per row or row-level summary proving rule was followed

This gives implementation agent a deterministic recipe rather than free-form composition.

## Architecture Boundary Review

No change from prior review. Plan scope remains docs/reviews JSON/evidence only.

## Best-Practice Review

No change from prior review. Validation strategy remains appropriate for JSON-only scope.

## Open Questions

No new open questions. Prior non-blocking question about future preflight consumption remains.

## Residual Risks

| Risk | Severity | Tracking |
|---|---|---|
| QDII/FOF/110020 Handling section still uses "or" wording (`deferred_from_v1` or `blocked`) despite deterministic rules binding `deferred_from_v1` | Low | Acceptable — derivation rules and row mapping table are authoritative; handling section is explanatory |
| Future gate must replicate or reference the deterministic derivation rules to maintain consistency | Low | Plan line 216 requires new gate or controller decision for changed rows |

## Reviewer Self-Check

- [x] Reviewed target and scope clearly stated
- [x] All four accepted fixes verified against revised plan text and filesystem evidence
- [x] No new findings requiring fixes
- [x] Open questions and residual risks separated from findings
- [x] Conclusion is `accepted`
- [x] Output path uses system-clock timestamp and matches `docs/reviews/` format

## Conclusion

**accepted**

All four accepted fixes are correctly incorporated into the revised plan:

1. `source_quality_gate_path` for 006597 now points to `reports/quality-gate-runs/...` (verified on disk), with explicit guard text preventing substitution.
2. Deterministic `fixture_state` derivation rules (6 rules) plus concrete row mapping table eliminate all "A or B" ambiguity.
3. Blocker reconciliation uses enumerable stop conditions with explicit global/policy-only exceptions, replacing vague "conflict materially".
4. `blocking_reason` has an 8-step construction algorithm with per-row special context and evidence recording requirement.

The plan is handoff-ready for implementation.
