# Bond Risk Evidence Extractor / Anchor Hardening - Slice 6 Controller Judgment

> Date: 2026-05-28
> Role: Gateflow controller
> Gate: Slice 6 real validation
> Judgment: **blocked-with-reason**

## Decision

The gate does not satisfy acceptance. Stop before deepreview / ready-to-open-draft-PR.

The implementation through Slice 5 is locally healthy and emits a structured positive `bond_risk_evidence.v1` row, but real `006597` / `2024` score output still contains:

- `issue_code=bond_risk_evidence_missing`
- `contract_id=bond_risk_evidence.v1`
- `baseline_blocking=true`
- `missing_evidence_groups=[credit_risk, drawdown_stress, redemption_share_pressure]`

Therefore the blocker is not解除.

## Evidence Basis

Primary validation artifact:

- `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-slice6-real-validation-20260528.md`

Independent worker artifacts:

- `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-slice6-root-cause-review-ds-20260528.md`
- `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-slice6-investigation-glm-20260528.md`

Generated public outputs:

- `reports/extraction-snapshots/bond-risk-evidence-006597-2024-20260528/snapshot.jsonl`
- `reports/scoring-runs/bond-risk-evidence-006597-2024-20260528/score.json`
- `reports/quality-gate-runs/bond-risk-evidence-006597-2024-20260528/quality_gate.json`

## Accepted Findings

| Finding | Controller judgment |
|---|---|
| `credit_risk` is weak because real rating distribution tables are missed by row keyword logic | Accepted; extractor hardening is valid future work |
| `redemption_share_pressure` is ambiguous because the extractor finds the wrong table and does not use §2 parsed share-class mapping | Accepted; extractor hardening is valid future work |
| `drawdown_stress` is weak because the annual report lacks max drawdown / volatility / stress metric evidence | Accepted; do not upgrade qualitative "控制回撤" text |
| Full blocker removal is impossible under the current annual-report-only `bond_risk_evidence.v1` contract unless `drawdown_stress` gets quantitative evidence or the contract changes | Accepted |

## Non-Decisions

- No FQ0-FQ6 semantics changed.
- No score-policy bypass accepted.
- No weak/ambiguous evidence was treated as accepted evidence.
- No golden corpus, baseline promotion, release readiness, PR, push, merge, approval, QDII, FOF, 110020, Host/Agent/dayu work was entered.

## Validation

- `uv run ruff check .`: pass.
- `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q`: 834 passed; coverage 92.22%.
- `FundDocumentRepository` real smoke for `006597` / `2024`: pass.
- `fund-analysis extraction-snapshot`: pass.
- `fund-analysis extraction-score`: pass.
- `fund-analysis quality-gate`: pass.
- Acceptance-specific validation: fail; blocker remains.

## Residuals

| Residual | Owner / next gate |
|---|---|
| Harden `credit_risk` rating distribution table extraction | future amended implementation slice |
| Harden `redemption_share_pressure` §2 share-class mapping and §10 share-change table selection | future amended implementation slice |
| Define whether and how NAV-derived max drawdown can satisfy `drawdown_stress` without annual-report disclosure | future separate design gate |
| Keep current `drawdown_stress` qualitative-control text weak | current contract |

## Final Controller State

This work unit is stopped at Slice 6 validation failure. It is not ready to open a draft PR, because the named acceptance criterion is unmet.
