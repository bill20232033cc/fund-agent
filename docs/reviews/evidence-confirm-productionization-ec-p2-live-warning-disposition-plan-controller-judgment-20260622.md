# EC-P2 Live Warning Disposition Plan Controller Judgment

Date: 2026-06-22

## Verdict

`ACCEPT_EC_P2_WARNING_DISPOSITION_PLAN_READY_FOR_NO_LIVE_IMPLEMENTATION_NOT_READY`

## Accepted Inputs

- Current live evidence: `docs/reviews/evidence-confirm-productionization-ec-p2-live-sample-evidence-20260622.md`
- Current live controller judgment: `docs/reviews/evidence-confirm-productionization-ec-p2-live-sample-controller-judgment-20260622.md`
- Fixed plan: `docs/reviews/evidence-confirm-productionization-ec-p2-live-warning-disposition-fix-plan-20260622.md`
- Initial plan review: `docs/reviews/plan-review-20260622-162937.md`
- Targeted re-review: `docs/reviews/plan-review-20260622-163118.md`

## Decision

Accept the plan to distinguish strict V2 status from repository/source/PDF pathway status.

The accepted fix must not make section-only Evidence Confirm a strict V2 pass. It must keep `evidence_confirm_overall_status="warn"` visible for the current section-smoke pathway and add explicit `pathway_status` only for EC-P2 source/PDF pathway evidence.

## Binding Implementation Constraints

- Do not modify `fund_agent/fund/evidence_confirm.py`.
- Do not relax `anchor_precision`.
- Do not synthesize table-to-section proof.
- Do not edit repository/source internals or fallback policy.
- Do not edit Service/UI/renderer/quality-gate.
- Do not expand public `EvidenceSourceKind` / `EvidenceAnchor`.
- Do not run live/PDF/provider/LLM commands during no-live implementation.
- Keep `field_correctness_proven=false`.
- Preserve `status` as strict runner/V2 aggregate status; add separate `pathway_status`.

## Accepted Implementation Scope

Allowed files:

- `fund_agent/fund/evidence_confirm_sources.py`
- `scripts/evidence_confirm_ec_p2_live_sample.py`
- `tests/fund/test_evidence_confirm_sources.py`
- `fund_agent/fund/README.md`
- `tests/README.md`
- implementation/review/evidence artifacts under `docs/reviews/`

## Required Validation

```text
uv run pytest tests/fund/test_evidence_confirm.py tests/fund/test_evidence_confirm_sources.py -q
```

```text
uv run ruff check fund_agent/fund/evidence_confirm_sources.py scripts/evidence_confirm_ec_p2_live_sample.py tests/fund/test_evidence_confirm_sources.py
```

```text
git diff --check -- fund_agent/fund/evidence_confirm_sources.py scripts/evidence_confirm_ec_p2_live_sample.py tests/fund/test_evidence_confirm_sources.py fund_agent/fund/README.md tests/README.md
```

## Next Gate

EC-P2W-1 no-live pathway-status implementation.

No further live/PDF execution is authorized until the no-live implementation, code review and controller judgment are accepted.

## Release State

`NOT_READY`
