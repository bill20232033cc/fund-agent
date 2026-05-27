# Bond Risk Evidence Extractor / Anchor Hardening Slice 2 Controller Judgment

> Date: 2026-05-27
> Work unit: `bond risk evidence extractor / anchor hardening design gate`
> Controller role: Gateflow controller
> Gate: Slice 2 implementation -> code review -> fix -> re-review
> Decision: accepted for local Slice 2 checkpoint

## Self-Check

- Current role: controller only; implementation, review, fix, and re-review were delegated.
- Branch: `codex/local-reconciliation`.
- Scope: Slice 2 extractor contract implementation only; no snapshot, score, quality gate, data source, golden promotion, PR, push, merge, or release readiness work.
- Source of truth: accepted plan, Slice 2 implementation artifact, DS/MiMo reviews, GLM fix artifact, DS re-review artifact.
- Stop conditions: none triggered. Validation passed and residual risks are classified with owners.

## Inputs Reviewed

- `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-plan-20260527.md`
- `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-slice2-implementation-20260527.md`
- `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-slice2-code-review-ds-20260527.md`
- `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-slice2-code-review-mimo-20260527.md`
- `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-slice2-fix-20260527.md`
- `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-slice2-rereview-ds-20260527.md`

## Accepted Implementation

Slice 2 introduces `extract_bond_risk_evidence(report, classified_fund_type)` as an Agent-layer extractor that consumes an already loaded `ParsedAnnualReport` and returns `ExtractedField[BondRiskEvidenceValue]`.

Accepted behavior:

- Non-bond or unknown fund types return `not_applicable_non_bond_fund` without scanning seven evidence groups.
- All seven required groups are represented through `BondRiskEvidenceValue`:
  - `duration_rate_risk`
  - `credit_risk`
  - `leverage_liquidity`
  - `asset_allocation_holdings_mix`
  - `drawdown_stress`
  - `redemption_share_pressure`
  - `convertible_bond_equity_exposure`
- Weak qualitative evidence remains weak:
  - drawdown control text is `weak` / `qualitative_control_intent`;
  - leverage strategy or liquidity text without repo/financing rows is `weak`;
  - ambiguous multi-share-class share-change tables remain `ambiguous`.
- Explicit absence rows for equity or convertible-bond exposure can produce `accepted_absence` only when row values are dash or zero-like absence values.
- Stable group-level anchors use the accepted format `bond-risk:<fund_code>:<report_year>:<group_id>:<ordinal>`.
- `validate_bond_risk_evidence_value` is called before returning a populated field.

## Review Finding Disposition

Accepted and fixed in this slice:

- DS F5: added dedicated `classified_fund_type=None` early-return test.
- DS F6: removed the dead `_field_note` fallback.
- MiMo/DS test gap: added partial extraction tests proving incomplete coverage maps to `contract_status="partial"` and compatible `extraction_mode="estimated"`, not `direct`.
- MiMo/DS test gap: added negative non-zero equity exposure test so non-absence rows do not become `accepted_absence`.
- DS F3: tightened `duration_rate_risk` text matching so bare boilerplate `利率风险` no longer satisfies the group.

Deferred with owner:

- Table section attribution remains rule-assigned because `ParsedTable` has no section identity. Owner: Slice 6 real `006597 / 2024` validation and later parser-section hardening if evidence proves section mismatch risk material.
- `ExtractionMode` still lacks a literal `partial`; extractor maps partial contracts to existing compatible mode `estimated`. Owner: Slice 4 snapshot/model integration decision.
- Broader table keyword and section filtering hardening remains deferred until real-report validation shows the exact shape of 006597 tables and anchors. Owner: Slice 6.

Rejected as not required in this slice:

- Parser schema changes for table section IDs.
- Changes to `data_extractor`, snapshot, score, quality gate, README, design/control docs, fixtures, PDF cache, or document source code.

## Validation Evidence

Controller reran:

- `uv run pytest tests/fund/extractors/test_bond_risk_evidence.py -q`
  - Result: `28 passed in 0.73s`
- `uv run ruff check fund_agent/fund/extractors/bond_risk_evidence.py tests/fund/extractors/test_bond_risk_evidence.py`
  - Result: `All checks passed!`
- `git diff --check`
  - Result: passed

Worker/re-review validation also reported the same Slice 2 checks passing.

## Boundary Judgment

Hard constraints remain intact:

- No weakening of FQ0-FQ6.
- No bypass of `FundDocumentRepository`; the extractor does not access production annual reports, PDF cache, direct sources, or download helpers.
- Missing evidence is not converted into passing evidence.
- Weak qualitative evidence is not disguised as strong quantitative evidence.
- No golden corpus promotion.
- No QDII, FOF, 110020, release readiness, Host/Agent/dayu, PR, push, merge, approve, or mark-ready work.
- No explicit parameters were hidden in `extra_payload`.
- UI -> Service -> Host -> Agent boundary remains unchanged; this slice stays inside the current Agent-layer `fund_agent/fund` extractor surface.

## Decision

Slice 2 is accepted for local checkpoint. Proceed to Slice 3 bundle integration, where the extractor can be wired into the deterministic extraction bundle without changing score, snapshot, quality gate, or golden promotion behavior.
