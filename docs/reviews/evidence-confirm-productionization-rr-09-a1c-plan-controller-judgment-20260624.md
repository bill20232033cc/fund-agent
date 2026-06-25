# RR-09 A1-C Fix Plan Controller Judgment

Verdict: `ACCEPT_RR_09_A1C_FIX_PLAN_READY_FOR_NO_LIVE_IMPLEMENTATION_NOT_READY`

## 1. Inputs

- Plan: `docs/reviews/evidence-confirm-productionization-rr-09-a1c-projection-anchor-materializer-fix-plan-20260624.md`
- Plan review: `docs/reviews/plan-review-20260624-053434.md`
- Accepted A1 evidence: `docs/reviews/evidence-confirm-productionization-rr-09-a1-fact-diagnostic-evidence-20260624.md`
- Accepted A1 judgment: `docs/reviews/evidence-confirm-productionization-rr-09-a1-controller-judgment-20260624.md`

## 2. Judgment

The A1-C plan is accepted for a narrow no-live implementation gate.

Accepted implementation route:

- Add bounded coarse-reference fallback in `fund_agent/fund/evidence_confirm_sources.py`.
- Preserve fail-closed behavior for invalid source truth, invalid section, unsupported table id, unresolved/duplicate table, page mismatch and row-N out-of-range.
- Add V2 precision protection in `fund_agent/fund/evidence_confirm.py` so row-locator downgrade emits E1 reviewable `anchor_precision` warning rather than silent pass.
- Cover the contract with focused no-live tests under `tests/fund/`.

## 3. Binding Constraints

- No live/PDF re-evidence is authorized by this judgment.
- No B1 `017641 / 2024` runtime product CLI re-evidence is authorized by this judgment.
- No provider, LLM, checklist support, report-body rendering, quality-gate threshold change, tag, release or readiness promotion is authorized.
- Implementation must distinguish strict aggregate `result.status` from EC-P2 `pathway_status`; an all-E1 precision-warning shape may keep strict `status="fail"` while `pathway_status="pass"`.
- Row-level semantic locators must not be represented as row-precise unless the materialized reference actually carries the matching row locator.

## 4. Next Entry

Proceed to:

`RR-09 A1-C Projection / Anchor Locator / Reference Materializer No-live Implementation Gate / RR-09 B1 Runtime Re-evidence Authorization`

Release/readiness remains `NOT_READY`.
