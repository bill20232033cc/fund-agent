# Evidence Confirm Productionization EC-P3 Plan Controller Judgment

- Gate: accepted plan judgment
- Work unit: Evidence Confirm productionization / EC-P3 semantic entailment
- Date: 2026-06-22
- Classification: heavy
- Artifact path: `docs/reviews/evidence-confirm-productionization-ec-p3-plan-controller-judgment-20260622.md`

## Reviewed Inputs

- Goal confirmation: `docs/reviews/evidence-confirm-productionization-ec-p3-semantic-entailment-goal-confirmation-20260622.md`
- Plan: `docs/reviews/evidence-confirm-productionization-ec-p3-semantic-entailment-plan-20260622.md`
- Plan review: `docs/reviews/plan-review-20260622-171441.md`
- Plan fix: `docs/reviews/evidence-confirm-productionization-ec-p3-plan-fix-20260622.md`
- Targeted re-review: `docs/reviews/plan-review-rereview-20260622-171522.md`

## Decision

ACCEPT_READY_FOR_EC_P3_SEMANTIC_ENTAILMENT_IMPLEMENTATION_NOT_READY

## Rationale

- The work unit is valid: current V2 deterministic `value_match` proves token/value support, not qualitative semantic entailment.
- The accepted plan keeps semantic entailment as a Fund-layer no-live companion contract and does not mutate V1/V2 Evidence Confirm schema or hard-gate semantics.
- The plan uses explicit `EvidenceSemanticClaim` input rather than inferring rendered claims from `ChapterFactEntry.value`, preserving the boundary between Fund evidence logic and later Service/renderer claim projection.
- Planreview finding 001 was accepted and fixed: aggregate semantic status now uses explicit gate status `pass/warn/fail/not_applicable`, while per-claim status remains semantic support.
- No provider/live, Service/UI/Host/renderer/quality-gate, repository/source fallback, mark-ready, merge or release/readiness transition is authorized by this judgment.

## Required Implementation Scope

Implementation must follow `Slice EC-P3-S1: Semantic Companion Contract` in the accepted plan.

Allowed files:

- `fund_agent/fund/evidence_confirm_semantic.py`
- `tests/fund/test_evidence_confirm_semantic.py`
- `fund_agent/fund/README.md`
- `tests/README.md` only if test taxonomy or command guidance changes

Any need to modify V2 result schema, Service/UI/Host/renderer/quality-gate, provider/client/config, repository/source/PDF/cache/downloader, `chapter_facts.py`, live commands or release/readiness routing must stop and return to plan fix.

## Validation Required After Implementation

```bash
uv run pytest tests/fund/test_evidence_confirm.py tests/fund/test_evidence_confirm_semantic.py -q
uv run ruff check fund_agent/fund/evidence_confirm_semantic.py tests/fund/test_evidence_confirm_semantic.py
git diff --check -- fund_agent/fund/evidence_confirm_semantic.py tests/fund/test_evidence_confirm_semantic.py fund_agent/fund/README.md tests/README.md
```

## Residual Risks

- Provider-backed semantic quality: assigned to later controlled semantic provider evidence gate.
- Service/renderer claim extraction: assigned to later Service/UI/renderer integration gate.
- Quality-gate consumption: assigned to later quality-gate integration gate.
- Release/readiness: remains `NOT_READY`.

No unclassified residual risk remains for the plan gate.
