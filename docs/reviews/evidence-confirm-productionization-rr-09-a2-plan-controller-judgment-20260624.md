# RR-09 A2 Plan Controller Judgment

Verdict: `ACCEPT_RR_09_A2_PLAN_READY_FOR_NO_LIVE_IMPLEMENTATION_NOT_READY`

## Scope

Controller judgment for:

- Plan artifact: `docs/reviews/evidence-confirm-productionization-rr-09-a2-value-match-diagnostic-plan-20260624.md`
- Initial plan review: `docs/reviews/plan-review-20260624-055333.md`
- Plan fix: `docs/reviews/evidence-confirm-productionization-rr-09-a2-plan-fix-20260624.md`
- Targeted re-review: `docs/reviews/plan-review-20260624-055429.md`

No source code, tests, live/PDF command, provider/LLM command, quality-gate semantic change, checklist support, report-body rendering, tag, release, or readiness claim was performed.

## Decision

Accept the fixed A2 diagnostic plan.

Accepted work unit:

`RR-09 A2 R1-R4 Value-match / Bond-risk Missing-evidence Diagnostic`

Accepted objective:

- Add a no-live, Fund-layer, in-memory diagnostic helper that explains deterministic V2 `value_match` failures and the R3 `bond_risk_evidence` missing-evidence residual without changing product behavior.
- Require V2 same-source token/matcher diagnostics; no parallel approximate matcher is allowed.
- Route future R1-R4 live/PDF diagnostic evidence to a separate explicitly authorized A2-S2 gate.

## Finding Disposition

| Finding | Source | Disposition |
|---|---|---|
| PR-001 V2 token/matcher 同源性未被写成硬约束 | `docs/reviews/plan-review-20260624-055333.md` | ACCEPTED_AND_FIXED. Re-review `docs/reviews/plan-review-20260624-055429.md` marked it `已修复`. |

## Accepted Slice

Next implementation slice:

`A2-S1 No-live Diagnostic Helper`

Allowed files:

- `fund_agent/fund/evidence_confirm_value_diagnostics.py`
- `tests/fund/test_evidence_confirm_value_diagnostics.py`
- `fund_agent/fund/README.md`
- `tests/README.md`

Key requirements:

- Diagnostic helper must be in-memory only and Fund-layer only.
- It must not instantiate or import repository/source helper/PDF/cache/Service/Host/provider/LLM/CLI/renderer behavior.
- Token/match metadata must come from deterministic V2 same-source primitives.
- It must output only safe categories, counts, structural value paths, reference granularity, and classifications.
- It must classify `bond_risk_group_anchor_projection_gap` for bond-risk value-level anchors that are not exposed as chapter anchors.
- It must not change `evidence_confirm.py` pass/fail semantics, quality-gate semantics, extractor outputs, projection behavior, CLI, report body, provider, tag, release, or readiness.

Required validation:

```bash
uv run pytest tests/fund/test_evidence_confirm_value_diagnostics.py tests/fund/test_evidence_confirm_diagnostics.py tests/fund/test_evidence_confirm.py -q --tb=short
uv run ruff check fund_agent/fund/evidence_confirm_value_diagnostics.py tests/fund/test_evidence_confirm_value_diagnostics.py
git diff --check
```

## Residuals

| Residual | Destination |
|---|---|
| A2-S1 implementation correctness | A2-S1 implementation + code review gate. |
| R1-R4 live/PDF diagnostic evidence | A2-S2 authorization/evidence gate; not authorized by this judgment. |
| B1 `017641 / 2024` runtime product CLI re-evidence | Separate B1 runtime re-evidence authorization. |
| Checklist Evidence Confirm support | Separate gate. |
| Report-body Evidence Confirm rendering | Separate gate. |
| Provider-backed semantic production default | Separate gate. |
| Tag/release/readiness | Separate release-boundary authorization and accepted readiness evidence. |

## Next Entry Point

`RR-09 A2-S1 No-live Value-match Diagnostic Helper Implementation Gate / RR-09 B1 Runtime Re-evidence Authorization`

Release/readiness remains `NOT_READY`.

Completion token:

`ACCEPT_RR_09_A2_PLAN_READY_FOR_NO_LIVE_IMPLEMENTATION_NOT_READY`
