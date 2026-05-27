# Bond Risk Evidence Extractor / Anchor Hardening Slice 3 Controller Judgment

> Date: 2026-05-27
> Work unit: `bond risk evidence extractor / anchor hardening design gate`
> Controller role: Gateflow controller
> Gate: Slice 3 bundle integration
> Decision: accepted for local Slice 3 checkpoint

## Self-Check

- Current role: controller only; implementation and review were delegated.
- Branch: `codex/local-reconciliation`.
- Scope: bundle integration only. No snapshot, score, quality gate, golden promotion, Service/UI parameters, PR, push, merge, approve, or mark-ready work.
- Source of truth: accepted plan Slice 3, Slice 2 accepted controller judgment, Slice 3 implementation artifact, MiMo review, and DS review.
- Stop conditions: none triggered. Reviews passed and residuals are classified with owners.

## Inputs Reviewed

- `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-plan-20260527.md`
- `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-slice2-controller-judgment-20260527.md`
- `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-slice3-implementation-20260527.md`
- `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-slice3-code-review-mimo-20260527.md`
- `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-slice3-code-review-ds-20260527.md`

## Accepted Implementation

Slice 3 adds `bond_risk_evidence` as an explicit `StructuredFundDataBundle` field and wires the already accepted extractor into `FundDataExtractor.extract(...)`.

Accepted behavior:

- `StructuredFundDataBundle.bond_risk_evidence` is typed as `ExtractedField[BondRiskEvidenceValue]`.
- Direct bundle test fixtures receive an explicit default missing field with note `bond_risk_evidence_not_extracted`.
- `FundDataExtractor.extract(...)` still loads the annual report once through the configured repository.
- The existing profile result is used to compute `classified_fund_type` once.
- That same explicit `classified_fund_type` is passed to `extract_bond_risk_evidence(report, classified_fund_type=classified_fund_type)` and reused for tracking-error applicability.
- Source provenance projection remains unchanged.
- No Service/UI constructor or method parameter changed.

## Review Finding Disposition

Accepted as no-fix / deferred:

- DS F1: `ExtractionMode` lacks a literal `partial`, so partial `bond_risk_evidence` fields currently use `extraction_mode="estimated"` while retaining `BondRiskEvidenceValue.contract_status="partial"`. Owner: Slice 4 snapshot/model integration decision.
- MiMo residual: non-bond guard test patches only the first group extractor. Accepted because Slice 2 directly tests extractor early return and Slice 6 will validate real bond flow.
- MiMo residual: bundle field appears after `source_provenance` because both fields use default factories. Accepted as non-behavioral and keyword construction remains explicit.
- DS R1/R4: bond-fund production projection is intentionally left to snapshot/score/real validation slices.
- DS R2: downstream consumers must guard `bond_risk_evidence.value is None`. Owner: Slice 4 and Slice 5.
- DS R3: `_classified_fund_type` hardcoded allow-list drift is a maintenance residual outside this gate slice.

Rejected as not required in this slice:

- Changes to extraction-mode literals.
- Snapshot, score, quality-gate, golden, Service/UI, document source, PDF/cache, or parser changes.

## Validation Evidence

Controller reran:

- `uv run pytest tests/fund/test_data_extractor.py -q`
  - Result: `8 passed in 0.69s`
- `uv run ruff check fund_agent/fund/data_extractor.py tests/fund/test_data_extractor.py`
  - Result: `All checks passed!`

Worker and reviewers also reported the same Slice 3 checks passing.

## Boundary Judgment

Hard constraints remain intact:

- No FQ0-FQ6 quality gate semantics changed.
- No bypass of `FundDocumentRepository`; production report loading remains repository-mediated.
- Missing evidence remains missing/not-applicable.
- Weak qualitative evidence semantics are unchanged.
- No golden corpus promotion.
- No QDII, FOF, 110020, release readiness, Host/Agent/dayu, PR, push, merge, approve, or mark-ready work.
- No explicit parameters hidden in `extra_payload`.
- UI -> Service -> Host -> Agent boundary is unchanged; current deterministic path still routes through Service to `fund_agent/fund`.

## Decision

Slice 3 is accepted for local checkpoint. Proceed to Slice 4 snapshot projection and field-priority integration.
