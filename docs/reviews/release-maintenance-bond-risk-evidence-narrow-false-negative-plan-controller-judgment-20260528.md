# Bond Risk Evidence Narrow False-Negative Plan — Controller Judgment

> Date: 2026-05-28
> Gate: `bond risk evidence narrow false-negative gate`
> Controller: Codex
> Status: **accepted for implementation**

## Scope Decision

This gate remains a narrow false-negative hardening gate. It is not a golden promotion gate and is not a release-readiness gate.

Accepted implementation scope:

- `fund_agent/fund/extractors/bond_risk_evidence.py`
- `tests/fund/extractors/test_bond_risk_evidence.py`
- gate evidence artifacts under `docs/reviews/`
- minimal `docs/implementation-control.md` update only after evidence closure

Explicitly out of scope:

- schema redesign, score engine redesign, snapshot pipeline redesign, or quality-gate weakening
- QDII, FOF, `110020`, Host/Agent/dayu architecture work
- NAV-derived drawdown calculation
- golden corpus promotion, PR creation, push, merge, approval, or ready marking

## Truth Source Restatement

The current blocker for `006597 / 2024` is still `bond_risk_evidence_missing.baseline_blocking=true`.

The previous gate established that strict JSON generation is not the blocker. The remaining issue surface is:

- `credit_risk`
- `redemption_share_pressure`
- `drawdown_stress`

This gate may remove false negatives for `credit_risk` and `redemption_share_pressure`. It must preserve `drawdown_stress` as weak or missing unless a real max drawdown, volatility, or stress metric exists in accepted report evidence.

## Accepted Semantic Contract

### credit_risk

The annual report rating distribution tables for `006597 / 2024` are held bond/security rating distributions. They may support:

- `credit_risk.meaning = portfolio_credit_exposure`
- `evidence_kind = holding_rating_distribution`

They must not be represented as:

- `fund_rating`
- `ratings`
- `fund_own_rating`
- any equivalent claim that the fund itself received a rating

Implementation must reject fund-own-rating contexts and require held-position or §8 portfolio context plus numeric table shape and anchors.

### redemption_share_pressure

`006597 / 2024` has A/C/E/F share classes. The extractor must aggregate all classes across:

- beginning shares
- subscription shares
- redemption shares
- ending shares
- net change
- net change ratio

It must preserve class-level breakdown and anchors. A-only extraction is invalid. Ambiguous class mapping, missing class rows, non-parseable values, column count mismatch, duplicate class mapping, or arithmetic mismatch must fail closed instead of producing accepted evidence.

### drawdown_stress

Qualitative wording such as `控制回撤` remains weak qualitative evidence only. This gate must not upgrade it to accepted quantitative evidence and must not introduce NAV-derived drawdown calculation.

## Review Result

Initial plan:

- `docs/reviews/release-maintenance-bond-risk-evidence-narrow-false-negative-plan-20260528.md`

First-round reviews:

- `docs/reviews/release-maintenance-bond-risk-evidence-narrow-false-negative-plan-review-ds-20260528.md`
- `docs/reviews/release-maintenance-bond-risk-evidence-narrow-false-negative-plan-review-mimo-20260528.md`

Plan fix:

- `docs/reviews/release-maintenance-bond-risk-evidence-narrow-false-negative-plan-fix-20260528.md`

Re-reviews:

- `docs/reviews/release-maintenance-bond-risk-evidence-narrow-false-negative-plan-rereview-ds-20260528.md`
- `docs/reviews/release-maintenance-bond-risk-evidence-narrow-false-negative-plan-rereview-mimo-20260528.md`

Controller accepts both re-review verdicts:

- DS verdict: **PASS**
- MiMo verdict: **PASS**

The accepted plan now closes all mandatory findings:

- async `FundDocumentRepository` smoke command uses `asyncio.run`
- `bond_risk_contract_status=partial` remains authoritative while `ExtractionMode.estimated` is used because there is no `partial` enum
- share table selection scans all candidates and fails closed on ambiguity
- credit rating evidence rejects fund-own-rating semantics
- holding rating tables require numeric current-period shape and anchors
- multiple valid rating tables retain all anchors
- Decimal parsing and tolerance are explicit
- A/C/E/F column alignment is explicit and fail-closed
- F class zero beginning is not treated as a failure
- targeted import smoke and §2 mapping tests are required
- validation output uses a new run id to avoid overwriting previous gate evidence

## Implementation Authorization

Implementation may proceed under the accepted plan.

The implementation worker must stop and return to controller if any of these occur:

- the blocker cannot be reproduced
- implementation requires schema, score, snapshot, or quality-gate changes
- reliable A/C/E/F aggregation cannot be achieved from parsed report evidence
- any fix would weaken FQ0-FQ6
- drawdown qualitative evidence would need to be upgraded
- `FundDocumentRepository` real smoke fails and cannot be classified
- any required validation fails
- external PR/push/merge/release/golden-promotion work becomes necessary

## Next Step

Dispatch implementation worker for the accepted narrow scope only. After implementation, run code review, fix/re-review if needed, deepreview, required validations, and final controller judgment before stopping at `ready-to-open-draft-PR`.
