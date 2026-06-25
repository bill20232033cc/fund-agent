# Evidence Confirm Productionization EC-P4 Slice 2 Code Review Fix

## Gate

- Work unit: Evidence Confirm Productionization EC-P4 Service/UI/renderer/quality-gate production integration
- Gate: code-review fix
- Slice: Slice 2 - Service Deterministic Opt-In Propagation
- Classification: heavy
- Release/readiness: NOT_READY
- Date: 2026-06-22

## Accepted Findings Mapping

| Finding | Status | Fix |
|---|---|---|
| DS-ECP4S2-01 MEDIUM | fixed in current slice | Added `EvidenceConfirmBlockedError` to Raises sections for `analyze()`, `checklist()`, and `_run_analysis_core()`. |
| DS-ECP4S2-02 MEDIUM | fixed in current slice | Added `EvidenceConfirmBlockedError` to the hosted LLM structured block propagation path; `operation()` now records a diagnostic and re-raises through the post-Host structured exception branch. |
| DS-ECP4S2-03 LOW | fixed in current slice | Added a direct runner exception regression where fake runner raises `RuntimeError`; EC warn returns a safe fail summary and still renders the report. |
| DS-ECP4S2-04 LOW | fixed in current slice | Added `EvidenceConfirmBlockedError` to Raises sections for `analyze_with_llm()` and `analyze_with_llm_execution()`. |
| MiMo F-01 LOW | fixed in current slice | Covered by the same direct runner exception regression. |
| MiMo F-02 INFO | fixed in current slice | Added a one-line Chinese comment for the `EvidenceConfirmRunner` type alias. |

## Changed Files

- `fund_agent/services/fund_analysis_service.py`
- `tests/services/test_fund_analysis_service.py`
- `docs/reviews/evidence-confirm-productionization-ec-p4-slice2-code-review-fix-20260622.md`

## Validation

Command:

```text
uv run pytest tests/services/test_fund_analysis_service.py -q
```

Output:

```text
.......................................                                  [100%]
39 passed in 0.92s
```

Command:

```text
uv run pytest tests/fund/test_evidence_confirm_production.py tests/fund/test_quality_gate.py tests/fund/test_quality_gate_integration.py -q
```

Output:

```text
........................................................                 [100%]
56 passed in 0.50s
```

Command:

```text
uv run ruff check fund_agent/services/fund_analysis_service.py tests/services/test_fund_analysis_service.py
```

Output:

```text
All checks passed!
```

Command:

```text
git diff --check -- fund_agent/services/fund_analysis_service.py tests/services/test_fund_analysis_service.py docs/reviews/evidence-confirm-productionization-ec-p4-slice2-code-review-fix-20260622.md
```

Output:

```text
<no output>
```

## Residual Risks

| Risk | Classification | Owner / Destination |
|---|---|---|
| CLI/UI Evidence Confirm summary and exit behavior are not implemented in this fix gate. | covered by later approved slice | Slice 3 |
| Renderer non-rendering guard remains outside this fix gate. | covered by later approved slice | Slice 4 |
| Semantic companion propagation remains outside this fix gate. | covered by later approved slice | Slice 5 |
| Checklist Evidence Confirm remains off/no runner in Slice 2. | covered by later approved slice | Slice 6 or separate checklist gate |
| Default-on/product-mode Evidence Confirm and readiness transition are still NOT_READY. | assigned to later work unit | Future readiness/release gate |

## Verdict

EC_P4_SLICE2_FIX_READY_FOR_REREVIEW_NOT_READY
