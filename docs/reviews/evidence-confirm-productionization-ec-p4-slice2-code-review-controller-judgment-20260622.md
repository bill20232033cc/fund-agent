# Evidence Confirm Productionization EC-P4 Slice 2 Code Review Controller Judgment

## Gate

- Work unit: Evidence Confirm Productionization EC-P4 Service/UI/renderer/quality-gate production integration
- Gate: code-review targeted re-review controller judgment
- Slice: Slice 2 - Service Deterministic Opt-In Propagation
- Classification: heavy
- Date: 2026-06-22
- Release/readiness: NOT_READY

## Inputs

- Implementation evidence: `docs/reviews/evidence-confirm-productionization-ec-p4-slice2-implementation-evidence-20260622.md`
- Initial DS review: `docs/reviews/code-review-20260622-225412-ds-ec-p4-slice2.md`
- Initial MiMo review: `docs/reviews/code-review-20260622-225412-mimo-ec-p4-slice2.md`
- Fix artifact: `docs/reviews/evidence-confirm-productionization-ec-p4-slice2-code-review-fix-20260622.md`
- DS targeted re-review: `docs/reviews/code-review-rereview-20260622-230645-ds-ec-p4-slice2.md`
- MiMo targeted re-review: `docs/reviews/code-review-rereview-20260622-230645-mimo-ec-p4-slice2.md`
- Changed files:
  - `fund_agent/services/fund_analysis_service.py`
  - `tests/services/test_fund_analysis_service.py`

## Finding Disposition

| Finding | Controller disposition | Evidence |
|---|---|---|
| DS-ECP4S2-01 | accepted; fixed | DS re-review records `EvidenceConfirmBlockedError` Raises coverage for `analyze()`, `checklist()`, and `_run_analysis_core()`. |
| DS-ECP4S2-02 | accepted; fixed | DS and MiMo re-reviews confirm hosted LLM structured propagation now captures, records and re-raises `EvidenceConfirmBlockedError`. |
| DS-ECP4S2-03 | accepted; fixed | DS and MiMo re-reviews confirm direct runner-exception regression coverage for safe fail summary shape. |
| DS-ECP4S2-04 | accepted; fixed | DS and MiMo re-reviews confirm `analyze_with_llm()` and `analyze_with_llm_execution()` Raises coverage. |
| MiMo F-01 | accepted; fixed | MiMo re-review confirms direct runner exception regression coverage and safe fail-closed summary assertions. |
| MiMo F-02 | accepted; fixed | MiMo re-review confirms the `EvidenceConfirmRunner` type alias has an explanatory Chinese comment. |

## Controller Validation

Command:

```text
uv run pytest tests/services/test_fund_analysis_service.py -q
```

Result:

```text
39 passed in 0.91s
```

Command:

```text
uv run pytest tests/fund/test_evidence_confirm_production.py tests/fund/test_quality_gate.py tests/fund/test_quality_gate_integration.py -q
```

Result:

```text
56 passed in 0.85s
```

Command:

```text
uv run ruff check fund_agent/services/fund_analysis_service.py tests/services/test_fund_analysis_service.py
```

Result:

```text
All checks passed!
```

## Controller Judgment

Slice 2 is accepted for local checkpoint commit.

The accepted implementation adds Service-level deterministic Evidence Confirm opt-in plumbing through typed developer overrides, injected repository-bounded runner dependency, safe runner-exception summaries, Service result summary propagation, EC-only blocking when quality gate is off or warn, and canonical `QualityGateBlockedError` behavior when the merged quality gate blocks.

The implementation remains inside the approved Slice 2 boundary:

- No CLI/UI flag or summary behavior is implemented in this slice.
- No renderer report-body content is added.
- No checklist CLI Evidence Confirm support is added.
- No direct Service/UI/renderer/quality-gate access to repository internals, PDF cache, source helpers, parser JSON, Docling, pdfplumber or EID HTML render artifacts is accepted.
- No live/PDF/provider/LLM command was required or run by the controller in this gate.
- Release/readiness remains `NOT_READY`.

## Residual Risks

| Residual | Classification | Owner / Destination |
|---|---|---|
| CLI/UI Evidence Confirm opt-in flag, summary output and exit behavior are not implemented. | covered by later approved slice | EC-P4 Slice 3 |
| Renderer non-rendering guard remains outside Slice 2. | covered by later approved slice | EC-P4 Slice 4 |
| Semantic companion propagation remains outside Slice 2. | covered by later approved slice | EC-P4 Slice 5 |
| Checklist Evidence Confirm remains off/no runner. | deferred with owner | Later checklist EC slice/gate |
| Default-on/product-mode Evidence Confirm and release/readiness transition remain unproven. | assigned to later work unit | Future readiness/release gate |

## Verdict

ACCEPT_EC_P4_SLICE2_SERVICE_OPT_IN_READY_FOR_ACCEPTED_SLICE_COMMIT_NOT_READY
