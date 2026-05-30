# Slice 4 Plan Amendment Review — MiMo

> Date: 2026-05-27
> Reviewer: MiMo (plan review worker)
> Gate: Slice 4 plan amendment review
> Artifact: `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-slice4-plan-amendment-review-mimo-20260527.md`
> Role: plan review worker only. No implementation, edit, commit, push, PR, approval, merge, mark-ready, or golden promotion.

## Verdict

**PASS** — amendment is technically sound and handoff-ready, subject to residuals and conditions below.

## Review Inputs

- `AGENTS.md`
- `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-plan-20260527.md` (original plan)
- `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-slice4-implementation-20260527.md` (blocked implementation artifact)
- `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-slice4-plan-amendment-20260527.md` (amendment under review)
- `fund_agent/fund/extraction_snapshot.py` (source verification)
- `fund_agent/fund/extraction_score.py` (source verification, read-only)

## Findings

### F1 — P1 deferral is architecturally justified (no severity)

The amendment's root fact is verified:

- `FIELD_PRIORITY_BY_NAME` is defined at `extraction_score.py:41` as `Final[dict[str, str]]`.
- `extraction_snapshot.py` does not define, import, or reference `FIELD_PRIORITY_BY_NAME`.
- The import dependency is one-directional: `extraction_score` imports from `extraction_snapshot`, not vice versa.
- Original Slice 4 allowed files are `{extraction_snapshot.py, test_extraction_snapshot.py}`; original Slice 5 allowed files already include `extraction_score.py`.

Adding `extraction_score.py` to Slice 4 would merge schema projection and scoring semantics into one slice, violating the small-slice boundary established after the stop condition. The deferral to Slice 5 is the correct boundary-preserving decision.

### F2 — Temporary UNMAPPED state is acceptable as local checkpoint (no severity)

After Slice 4 completes without P1 registration:

- `bond_risk_evidence` will exist as a snapshot row.
- Coverage/traceability statistics will not observe it (UNMAPPED in score).
- Existing bond-risk applicability blocker remains unchanged.
- No existing score behavior changes beyond adding an unmapped snapshot field.

This is acceptable because:
1. The state is explicitly documented as temporary.
2. Slice 5 is marked non-optional with an inherited P1 registration requirement.
3. The amendment prohibits Slice 4 tests from asserting P1 semantics, preventing false confidence.
4. The original plan's Slice 5 already owns `extraction_score.py` and score applicability logic.

### F3 — SnapshotRecord schema extension is feasible and additive (no severity)

`SnapshotRecord` at `extraction_snapshot.py:168` is a flat `@dataclass` with ~20 fields. The amendment proposes adding five optional fields:

- `bond_risk_contract_status: str | None`
- `bond_risk_satisfied_groups: tuple[str, ...]`
- `bond_risk_missing_groups: tuple[str, ...]`
- `bond_risk_weak_groups: tuple[str, ...]`
- `bond_risk_ambiguous_groups: tuple[str, ...]`

This is an additive change to a dataclass that serializes to JSONL via `asdict()`. It does not remove or reinterpret existing fields. The amendment's stop condition ("if explicit snapshot schema extension is judged too heavy... stop and return to controller") is a reasonable safety valve, but given the dataclass structure, extension is straightforward and does not require a separate schema gate.

### F4 — Structured field requirement for Slice 5 is sound (no severity)

The amendment requires Slice 5 to consume structured snapshot fields rather than parsing free-form `note`. This is architecturally correct:

- `extraction_score.py` already imports from `extraction_snapshot.py`.
- Score logic should consume machine-readable facts, not parse prose.
- The stop condition ("Slice 5 must stop and return to controller; it must not implement ad hoc prose parsing") enforces this contract.

### F5 — Amendment test exclusions are well-scoped (no severity)

The amendment explicitly lists what Slice 4 tests must NOT assert:

- No P1 priority, coverage, or traceability assertions.
- No `FIELD_PRIORITY_BY_NAME` behavior.
- No score applicability issue suppression.

This prevents false confidence from tests that would pass only because the UNMAPPED state happens to produce the right output for wrong reasons.

### F6 — Minor: P1 non-observability assertion gap (advisory)

The amendment requires Slice 4 tests to prove `bond_risk_evidence` is snapshot-projected correctly, but does not explicitly require a test asserting that P1 coverage/traceability stats are NOT yet observable for this field. Such a test would strengthen the deferral story by proving the temporary state is intentionally limited.

**Recommendation**: Slice 4 implementation should include one test confirming `bond_risk_evidence` is absent from `FIELD_PRIORITY_BY_NAME`-derived coverage/traceability denominators, or at minimum documenting this as an intentional gap. This is advisory, not blocking.

### F7 — Minor: `note` formatter scope ambiguity (advisory)

The amendment says `note` "may include stable human-readable tokens for inspection" and lists required tokens (`contract_id`, `contract_status`, groups). It does not clarify whether Slice 4 should implement the full note formatter or just ensure the `note` field can accommodate these tokens.

**Recommendation**: Slice 4 implementation should build the note formatter as part of snapshot projection, since the amendment lists specific token requirements. This is an implementation detail, not a design issue.

## Residuals

1. **UNMAPPED window**: Between Slice 4 acceptance and Slice 5 completion, `bond_risk_evidence` will be snapshot-visible but score-invisible. This is acceptable only if Slice 5 is not skipped. The amendment correctly marks Slice 5 as non-optional.

2. **Schema extension judgment**: The amendment's stop condition delegates schema extension feasibility to the implementing worker or reviewer. Given `SnapshotRecord` is a simple dataclass, this is low-risk, but the implementing worker should confirm feasibility before committing to the five-field extension.

3. **Slice 5 inherited requirements**: The amendment adds explicit Slice 5 requirements (P1 registration, structured field consumption). These must be carried forward into the Slice 5 implementation artifact and review gate.

## Conditions For Slice 4 Acceptance

1. Slice 4 implementation must not edit `extraction_score.py`.
2. Slice 4 tests must not assert P1 semantics.
3. Slice 4 must expose machine-readable contract status and group fields (structured or note-based, with structured preferred).
4. If schema extension is infeasible, Slice 4 must stop and return to controller rather than falling back to prose-only.

## Conditions For Slice 5 Acceptance

1. Slice 5 must register `bond_risk_evidence` in `FIELD_PRIORITY_BY_NAME` as P1.
2. Slice 5 must consume structured snapshot fields, not parse free-form `note`.
3. Slice 5 must prove final P1 semantics: complete evidence → no blocker; partial → blocker for unsatisfied groups only.
4. Existing FQ0-FQ6 thresholds, severities, and meanings must remain unchanged.

## Conclusion

The amendment is technically sound. The P1 deferral respects module boundaries, the temporary UNMAPPED state is explicitly bounded, and the Slice 5 inherited requirements ensure the gap is closed. No material option requires user input — the schema extension decision is an implementation judgment call with a clear stop condition.

**Verdict: PASS.**
