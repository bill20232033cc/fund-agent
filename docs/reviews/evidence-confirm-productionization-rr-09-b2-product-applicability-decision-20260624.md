# Evidence Confirm Productionization RR-09 B2 Product Applicability Decision

Verdict token:

`RR_09_B2_MANAGER_STRATEGY_QDII_APPLICABILITY_NO_CHANGE_NOT_READY`

## Scope

Gate: `RR-09 B2 R5a Manager-strategy QDII Product Applicability Decision Gate`.

This decision covers only whether `manager_strategy_text` should stop being P0/blocking for QDII funds, or whether RR-09 should preserve current quality-gate semantics and route remaining proof to runtime re-evidence after the accepted B1 extraction/anchor fix.

No code change, quality-gate semantic change, live/PDF/provider/LLM command, product CLI re-evidence, repository load, PR mutation, push, tag, release, readiness promotion, checklist support, report-body rendering, or provider-backed semantic production default was authorized or performed.

## Direct Evidence

Accepted R5a static evidence `docs/reviews/evidence-confirm-productionization-rr-09-r5a-quality-gate-static-evidence-20260623.md` proves the `017641 / 2024` block was not a QDII preferred_lens/applicability failure:

- `classified_fund_type = qdii_fund`.
- `app_category_status = match`.
- `preferred_lens_status = resolved`.
- `preferred_lens_key = qdii_fund`.
- `score_applicability_issues = []`.
- `failed_funds = []`.
- FQ4 missing-field-rate issue was `warn`, not `block`.
- The blocking rules were generic P0 `manager_strategy_text` coverage/traceability failures: `FQ2/block`, `FQ3/block`, and `FQ2F/block`.

Accepted B1 aggregate judgment `docs/reviews/evidence-confirm-productionization-rr-09-b1-aggregate-deepreview-controller-judgment-20260624.md` proves the no-live extraction/anchor side has now been narrowed and accepted:

- `manager_strategy_text` remains P0.
- QDII/overseas strategy/outlook heading variants are covered in the FundDisclosureDocument source-truth selector.
- Extraction remains heading-path-only.
- Body-only strategy/outlook keywords do not generate value or anchors.
- No quality-gate semantics changed.

Static code evidence supports the same boundary:

- `fund_agent/fund/extraction_score.py` maps `manager_strategy_text` to `P0` in `FIELD_PRIORITY_BY_NAME`.
- `APP_CATEGORY_ALLOWED_FUND_TYPES["海外股票类"]` accepts only `qdii_fund`; QDII applicability is not failing.
- `SUPPORTED_CONTRACT_FUND_TYPES` includes all current `FundType` values, including `qdii_fund`.
- The current field applicability replacement path is specific to exact `bond_fund` `holdings_snapshot` replacement by `bond_risk_evidence.v1`.
- The current exclusion path for `turnover_rate` is report-period applicability, not QDII manager strategy applicability.
- `fund_agent/fund/quality_gate.py` blocks on P0 field coverage/traceability via FQ2/FQ3/FQ2F and does not contain a QDII-specific exception for `manager_strategy_text`.

## Decision

Do not change product/field applicability for QDII `manager_strategy_text`.

`manager_strategy_text` remains P0/blocking for QDII funds. The accepted RR-09 evidence does not justify a product policy change, because the observed `017641 / 2024` block was a generic P0 coverage/traceability failure, while QDII fund type, app category, and preferred_lens applicability already resolved.

No B2 implementation is authorized from this decision. In particular, do not:

- downgrade `manager_strategy_text` from P0 for QDII,
- add a QDII-specific quality-gate exception,
- weaken FQ2/FQ3/FQ2F traceability semantics,
- hide missing QDII manager strategy/outlook disclosure,
- use B2 to claim `017641 / 2024` runtime product CLI now passes.

## Residuals

| Residual | Status | Destination |
|---|---|---|
| `017641 / 2024` runtime product CLI quality-gate re-evidence | open | B1 runtime re-evidence, requiring explicit live/PDF authorization. |
| R1-R4 EC `fail` under `warn` | open | A1 sample-specific fact-level diagnostic, requiring explicit live/PDF authorization for product samples. |
| B2 product applicability change | rejected for current evidence | No implementation authorized; reopen only with new product-policy evidence. |
| Checklist Evidence Confirm support | deferred | Separate gate. |
| Report-body Evidence Confirm rendering | deferred | Separate gate. |
| Provider-backed semantic production default | deferred | Separate gate. |
| Release/readiness | blocked | Separate release-boundary authorization and accepted readiness evidence. |

## Validation

Static evidence only:

```bash
rg -n "manager_strategy_text|FIELD_PRIORITY_BY_NAME|APP_CATEGORY_ALLOWED_FUND_TYPES|SUPPORTED_CONTRACT_FUND_TYPES|bond_risk_evidence|turnover_rate" fund_agent/fund/extraction_score.py
```

Result: current score code keeps `manager_strategy_text` as P0, resolves QDII as supported, and has no QDII-specific `manager_strategy_text` applicability exception.

```bash
rg -n "FQ2|FQ3|FQ2F|FQ4|FQ5|FQ6|_aggregate_gate_status|_evaluate_field_score|_evaluate_fund_score|_evaluate_fund_quality" fund_agent/fund/quality_gate.py tests/fund/test_quality_gate.py tests/fund/test_extraction_score.py
```

Result: current quality gate blocks generic P0 coverage/traceability failures and separately covers FQ4/FQ5/FQ6 semantics; no QDII-specific `manager_strategy_text` exception exists.

## Next Entry Point

`RR-09 B1 Runtime Re-evidence Authorization / RR-09 A1 R1-R4 Fact-level Diagnostic Authorization`

B1 runtime re-evidence and A1 diagnostics both require explicit live/PDF authorization before running product samples or repository-bounded product diagnostics.

Release/readiness remains `NOT_READY`.

Completion token:

`RR_09_B2_MANAGER_STRATEGY_QDII_APPLICABILITY_NO_CHANGE_NOT_READY`
