# Bond Risk Evidence Extractor / Anchor Hardening - Aggregate Deepreview Controller Judgment

> Date: 2026-05-28
> Role: Gateflow controller
> Work unit: `bond risk evidence extractor / anchor hardening`
> Aggregate deepreview: `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-aggregate-deepreview-mimo-20260528.md`
> Judgment: accepted blocked closeout; not ready-to-open-draft-PR

## Decision

Accept the aggregate deepreview conclusion `PASS_WITH_FINDINGS`.

This does not advance the work unit to `ready-to-open-draft-PR`, because Slice 6 real validation did not satisfy the user acceptance criterion: `006597` / `2024` still emits `bond_risk_evidence_missing.baseline_blocking=true`.

The gate is closed as **blocked-with-trackable-reason**:

- Positive `bond_risk_evidence.v1` contract and public output are implemented.
- FQ0-FQ6 semantics are preserved.
- Weak and ambiguous evidence is not pseudo-passed.
- Real validation proves the remaining blocker is contract-faithful.
- The unresolved cause is traceable to `drawdown_stress` lacking quantitative annual-report evidence, plus two safe extractor false negatives that do not unlock the blocker by themselves.

## Accepted Findings

| Finding | Controller disposition |
|---|---|
| F1: `credit_risk` misses rating distribution tables | Accepted as future extractor-hardening amendment; safe false negative |
| F2: `redemption_share_pressure` misses §2 share-class mapping / §10 table selection | Accepted as future extractor-hardening amendment; safe false negative |
| F3: `drawdown_stress` cannot be satisfied from annual report alone | Accepted as the primary remaining blocker; requires NAV-derived evidence design gate or reviewed contract change |
| F4: `extraction_mode=estimated` for partial bond evidence | Accepted as non-blocking; structured `bond_risk_contract_status=partial` is authoritative |
| F5: no `_record_is_covered()` special-case for `bond_risk_evidence` | Accepted as non-issue; field-level coverage and contract-level blocker remain separate |

## Verification Matrix

| Requirement | Evidence |
|---|---|
| Plan/review/implementation artifacts exist | Plan, plan reviews, Slice 1-5 implementation/review/controller artifacts under `docs/reviews/` |
| Deepreview loop exists | Aggregate deepreview artifact and this controller judgment |
| Real `006597` / `2024` validation done through repository/CLI | Slice 6 real validation artifact |
| Blocker解除 if satisfied | Not achieved; score still has `baseline_blocking=true` |
| Trackable未解除原因 if not satisfied | Achieved; DS/GLM/MiMo artifacts agree on root cause |
| FQ0-FQ6 not weakened | Deepreview confirms `quality_gate.py` unchanged and score blocker remains conservative |
| No direct production PDF/cache access | Deepreview confirms extractor consumes `ParsedAnnualReport`; real smoke used `FundDocumentRepository` |
| No golden promotion / PR / push / merge | No external mutation performed |

## Final State

Current branch local checkpoints:

- `0a5bac9` accepted plan
- `dc7d260` Slice 1
- `b684b2a` Slice 2
- `b45d860` Slice 3
- `155f99b` Slice 4 amendment
- `98b0fc5` Slice 4
- `7db6673` Slice 5
- `c42bc70` Slice 6 blocked validation evidence

This judgment should be committed as a final local evidence checkpoint. It is not a draft-PR readiness checkpoint.

## Next Entry Point

If continuing this product goal, open one of these gates:

1. `drawdown_stress evidence contract / NAV-derived risk metric design gate` to define how calculated max drawdown / volatility can satisfy `bond_risk_evidence.v1` without pretending annual-report qualitative text is quantitative evidence.
2. A narrower extractor-hardening amendment for `credit_risk` and `redemption_share_pressure`, with the explicit expectation that `drawdown_stress` remains weak and `baseline_blocking=true` remains until a quantitative drawdown/stress source exists.
