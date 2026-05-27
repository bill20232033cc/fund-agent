# Bond Risk Evidence Extractor / Anchor Hardening — Slice 4 Plan Amendment Review

> Date: 2026-05-27
> Role: plan review worker (DS)
> Gate: Slice 4 plan amendment review
> Review question: Is the amendment technically sound and handoff-ready?
> Status: **PASS** — amendment accepted with conditions and residuals

## Worker Self-Check

- Self-check: pass
- Role confirmed: plan review worker only. No implementation, commit, push, PR, approval, merge, or golden promotion.
- External-state boundary confirmed: no workflow command, no skill invocation.
- Dirty scope confirmed: this artifact writes only the requested review path.

## Source Of Truth Read

- `AGENTS.md`
- `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-plan-20260527.md`
- `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-slice4-implementation-20260527.md`
- `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-slice4-plan-amendment-20260527.md`
- `fund_agent/fund/extraction_snapshot.py` (full)
- `fund_agent/fund/extraction_score.py` (relevant sections: FIELD_PRIORITY_BY_NAME, derive_score_applicability_issues, _bond_risk_evidence_missing_issue, field score row construction, missing P0/P1 detection)

## Code Facts Verified

1. **FIELD_PRIORITY_BY_NAME** (line 41–58 of `extraction_score.py`) maps 15 field names to P0/P1/P2. `bond_risk_evidence` is not present.

2. **derive_score_applicability_issues** (line 884–925 of `extraction_score.py`) checks `classified_fund_type == BOND_FUND_TYPE` and `_is_bond_holdings_replacement_record`. It does NOT read `bond_risk_evidence` rows. The current all-seven blocker is emitted unconditionally for exact bond funds with a holdings replacement record.

3. **Field score row priority** (line 1426) uses `FIELD_PRIORITY_BY_NAME.get(counter.field_name, UNKNOWN_FIELD_PRIORITY)`. Unknown fields get "UNMAPPED" and do not participate in P0/P1 pass/watch/fail denominator calculations at line 1942–1944.

4. **_missing_p0_p1_fields_by_priority** (line 1925–1945) only collects missing fields whose priority is P0 or P1. UNMAPPED covered fields are invisible to missing-field detection.

5. **SnapshotRecord** is a frozen dataclass with `slots=True` (line 167–229, 30 fields). Adding nullable fields breaks no existing code and adds `null` to all JSONL rows.

## Findings

### Finding 1 — PASS: Temporary UNMAPPED State Is Safe (No Regression)

**Severity**: INFO

**Evidence**: Code inspection of `derive_score_applicability_issues` (line 884–925) confirms it does not consume `bond_risk_evidence` snapshot rows. The current all-seven `bond_risk_evidence_missing` blocker with `baseline_blocking=True` is emitted unconditionally for exact bond funds. After Slice 4 snapshot projection (without P1 registration), the bond blocker remains fully active — identical to current production behavior.

**UNMAPPED field behavior**: `_build_field_score_row` (line 1426) assigns priority "UNMAPPED" to `bond_risk_evidence`. The field's coverage/traceability rates are computed but excluded from P0/P1 denominators (line 1942–1944). `_missing_p0_p1_fields_by_priority` ignores UNMAPPED fields entirely. No pass/watch/fail status is affected.

**Conclusion**: Zero regression risk. The temporary state is strictly additive: a new snapshot row appears, P0/P1 scoring is unchanged, and the bond blocker persists.

### Finding 2 — PASS: Slice Boundary Preservation Is Correct

**Severity**: INFO

**Evidence**: `extraction_snapshot.py` owns field ordering, row shape, and projection. `extraction_score.py` owns priority mapping, P0/P1 denominators, and score applicability. These are distinct concerns. Merging them into one slice (by expanding Slice 4 to include `extraction_score.py`) would weaken the small-slice boundary that the original plan established and that the implementation worker's stop condition already validated.

**Amendment's decision**: Defer P1 registration to Slice 5, which already allows `extraction_score.py`. This is the minimal-scope path and respects the existing module boundary.

### Finding 3 — WATCH: Schema Extension Weight

**Severity**: WATCH

**Finding**: The amendment proposes adding 5 fields to `SnapshotRecord` (`bond_risk_contract_status`, `bond_risk_satisfied_groups`, `bond_risk_missing_groups`, `bond_risk_weak_groups`, `bond_risk_ambiguous_groups`). This is a public JSONL schema change — every existing record gets 5 new `null` fields via `asdict()`.

**Mitigation**: The fields are additive and nullable. No existing fields are removed or reinterpreted. Downstream JSONL consumers that ignore unknown keys are unaffected. The amendment has a stop condition: if the implementing worker or reviewer judges this too heavy, stop and return to controller.

**Assessment**: The schema extension is justified. The alternative (stuffing structured data into `note` as free-form prose or ad hoc JSON) would force Slice 5 to implement fragile parsing. The amendment correctly requires Slice 5 to consume structured fields rather than parse prose. However, the original plan already flagged this as a potential stop condition. The implementing worker should explicitly confirm the extension is accepted before proceeding.

### Finding 4 — WATCH: Slice 5 Hard Dependency

**Severity**: WATCH

**Finding**: The amendment creates a non-optional inherited requirement for Slice 5: register `bond_risk_evidence` as P1 in `FIELD_PRIORITY_BY_NAME`. If Slice 5 is abandoned, delayed, or split further, `bond_risk_evidence` stays UNMAPPED indefinitely.

**Mitigation**: The amendment explicitly states "Slice 5 must not be skipped" and adds P1 registration as an inherited requirement with dedicated tests. The original Slice 5 already allows `extraction_score.py`, so no further scope expansion is needed.

**Residual**: The implementation control document should record this dependency so the controller cannot accept Slice 4 without confirming Slice 5 will follow.

### Finding 5 — INFO: No Material Option Fork

**Severity**: INFO

**Question from review brief**: "Challenge assumptions about whether this creates a material option requiring user input."

**Analysis**: Three paths exist:
1. Expand Slice 4 scope to include `extraction_score.py` — rejected by amendment; merges distinct concerns.
2. Accept amendment (defer P1 to Slice 5) — recommended; minimal scope, clean boundary.
3. Move `FIELD_PRIORITY_BY_NAME` to `extraction_snapshot.py` — refactoring unrelated to this gate; heavier than both alternatives.

Path 2 is clearly correct. No user input is required — the amendment is unambiguously the right call.

### Finding 6 — INFO: Non-Bond Fund Impact Is Null

**Severity**: INFO

**Finding**: For non-bond funds, Slice 3's extractor returns a missing/not-applicable `bond_risk_evidence` field. Slice 4 would project this as `value_present=False`, `anchor_present=False`. Score would see it as UNMAPPED (same as all other non-bond fields that aren't in FIELD_PRIORITY_BY_NAME). No existing non-bond score behavior changes.

## Decision

**PASS** — the amendment is technically sound and handoff-ready.

### Conditions for Slice 4 Implementation

1. Schema extension (5 new SnapshotRecord fields) must be explicitly confirmed as acceptable for this gate. If the implementing worker judges it too heavy, stop and return to controller — do not fall back to prose-only `note`.
2. Slice 4 tests must NOT assert P1 priority, coverage, traceability, or score applicability behavior.
3. The temporary UNMAPPED state must be documented in the Slice 4 implementation artifact.

### Conditions for Slice 5 Implementation

4. Slice 5 MUST register `bond_risk_evidence` as P1 in `FIELD_PRIORITY_BY_NAME`. This is non-optional.
5. Slice 5 MUST consume Slice 4's structured snapshot fields. If structured fields are absent, stop — do not implement prose parsing.
6. Slice 5 tests must assert: P1 priority, 100% coverage/traceability for complete evidence, partial blocker behavior, and `required_evidence_groups` invariance.

### Residual Risks

| Risk | Owner | Mitigation |
|------|-------|------------|
| Pipeline run between Slice 4 and Slice 5 shows UNMAPPED `bond_risk_evidence` while bond blocker persists — confusing but not incorrect | Controller | Accept as intermediate state; Slice 5 resolves it |
| Schema extension rejected as too heavy | Implementing worker | Stop condition fires; controller decides |
| Slice 5 delayed or descoped | Controller | Implementation control doc must not close this gate without Slice 5 completion |

### Non-Findings (Verified Clean)

- No FQ0-FQ6 weakening.
- No golden/baseline promotion risk.
- No `extra_payload` usage.
- No boundary drift (Service/UI/Host/Agent).
- No PDF/cache/source-helper access.
- No `dayu.host` / `dayu.engine` introduction.
- No source fallback strategy changes.
