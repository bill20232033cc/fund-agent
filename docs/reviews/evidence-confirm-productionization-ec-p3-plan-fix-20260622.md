# Evidence Confirm Productionization EC-P3 Plan Fix

- Gate: plan fix
- Work unit: Evidence Confirm productionization / EC-P3 semantic entailment
- Date: 2026-06-22
- Plan artifact: `docs/reviews/evidence-confirm-productionization-ec-p3-semantic-entailment-plan-20260622.md`
- Review artifact: `docs/reviews/plan-review-20260622-171441.md`
- Artifact path: `docs/reviews/evidence-confirm-productionization-ec-p3-plan-fix-20260622.md`

## Accepted Findings

### 001 semantic aggregate cannot represent warn claim results

- Status: accepted
- Fix status: 已修复

## Fix Applied

Updated the EC-P3 plan to define an explicit aggregate gate status:

```python
EvidenceSemanticOverallStatus = Literal["pass", "warn", "fail", "not_applicable"]
```

The plan now separates:

- per-claim `EvidenceSemanticStatus`, which answers semantic support;
- aggregate `EvidenceSemanticOverallStatus`, which answers pass/warn/fail/not-applicable gate state.

Aggregate mapping is now specified:

- `fail` for contradicted or block-severity claim results;
- `warn` for insufficient or warn-severity claim results;
- `pass` for entailed claim results with no block/warn;
- `not_applicable` otherwise.

The test matrix now includes `test_semantic_aggregate_warns_when_claim_insufficient`.

## Validation

- `git diff --check -- docs/reviews/evidence-confirm-productionization-ec-p3-semantic-entailment-plan-20260622.md docs/reviews/plan-review-20260622-171441.md`
- Result: pass

## Residual Risks

- Provider-backed semantic quality remains assigned to later controlled semantic provider evidence gate.
- Service/renderer claim extraction remains assigned to later Service/UI/renderer integration gate.
- Quality-gate consumption remains assigned to later quality-gate integration gate.

No unclassified residual risk remains for plan fix.
