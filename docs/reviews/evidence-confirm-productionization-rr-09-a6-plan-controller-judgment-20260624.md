# Evidence Confirm Productionization RR-09 A6 Plan Controller Judgment

Verdict token:

`ACCEPT_RR_09_A6_PLAN_READY_FOR_NO_LIVE_IMPLEMENTATION_NOT_READY`

## Scope

Gate: `RR-09 A6 Projection / Runtime Locator Adoption Planning Gate`.

Inputs:

- Plan: `docs/reviews/evidence-confirm-productionization-rr-09-a6-projection-runtime-locator-adoption-plan-20260624.md`
- Plan review: `docs/reviews/plan-review-20260624-125616.md`
- Plan fix: `docs/reviews/evidence-confirm-productionization-rr-09-a6-plan-fix-20260624.md`
- Targeted re-review: `docs/reviews/plan-review-rereview-20260624-125743.md`
- A5 live/PDF evidence: `docs/reviews/evidence-confirm-productionization-rr-09-a5-r1-r4-live-reevidence-20260624.md`

## Decision

Accept the fixed A6 plan for no-live implementation.

The accepted implementation route is:

1. Add top-level `source_field_path=<field>` semantic locators to the default parsed annual processor projection.
2. Keep `field=...; table_id=...; row=...` reserved for Processor row locators.
3. Ensure `source_field_path` stays on the semantic locator path and never triggers Processor protocol fail-closed validation.
4. Support direct subfield-scoped semantic materializer narrowing only when direct subfield provenance is supplied.
5. Prohibit parsed annual projection from inferring `source_field_path=<field>.<subfield>` from composite dict values.

## Review Finding Disposition

| Finding | Status | Controller disposition |
|---|---|---|
| PR-001 subfield scoped anchors can be fabricated from field-level anchors | fixed | Accepted. The plan now limits parsed annual projection to top-level field scope and requires negative tests against fabricated subfield proof. |

## Implementation Authorization

Authorized next gate:

`RR-09 A6 No-live Projection / Runtime Locator Adoption Implementation Gate`

Allowed implementation files:

- `fund_agent/fund/processors/active_annual.py`
- `fund_agent/fund/data_extractor.py`
- `fund_agent/fund/evidence_confirm_sources.py`
- `fund_agent/fund/README.md`

Allowed test files:

- `tests/fund/test_data_extractor.py`
- `tests/fund/test_evidence_confirm_sources.py`

Allowed evidence/control docs after implementation:

- implementation evidence artifact under `docs/reviews/`
- code review artifact under `docs/reviews/`
- `docs/implementation-control.md`
- `docs/current-startup-packet.md`

## Explicitly Not Authorized

- No live/PDF command.
- No product CLI command, including B1 `017641 / 2024`.
- No provider/LLM command.
- No FundDisclosureDocument default-on parsing or default route switch.
- No checklist Evidence Confirm support.
- No report-body Evidence Confirm rendering.
- No V2/ECQ/quality-gate semantic change.
- No R3 `missing_section=3` fix.
- No push, PR mutation, tag, release or readiness claim.

## Residuals

| Residual | Destination |
|---|---|
| A6 may remove cross-field anchor ambiguity but not all composite subfield row precision | A6 implementation evidence and later live/PDF re-evidence authorization. |
| Extractor-specific direct subfield provenance may still be required for full R1-R4 closure | Later A7 extractor-specific locator precision planning gate if A6 evidence remains insufficient. |
| R3 `missing_section=3` | Separate R3 missing-section diagnostic/fix gate. |
| B1 `017641 / 2024` product CLI block | Separate B1 runtime product CLI gate. |
| Release/readiness | `NOT_READY`. |

## Validation

Planning-only static checks:

```bash
rg -n "RR_09_A6_PLAN_FIX_READY_FOR_REREVIEW_NOT_READY|pass-with-risks|PR-001|top-level|source_field_path=mapping.output_field_name" \
  docs/reviews/evidence-confirm-productionization-rr-09-a6-projection-runtime-locator-adoption-plan-20260624.md \
  docs/reviews/evidence-confirm-productionization-rr-09-a6-plan-fix-20260624.md \
  docs/reviews/plan-review-20260624-125616.md \
  docs/reviews/plan-review-rereview-20260624-125743.md
git diff --check
```

Result:

- Targeted re-review conclusion is `pass-with-risks`.
- `git diff --check` passed.

## Next Entry Point

`RR-09 A6 No-live Projection / Runtime Locator Adoption Implementation Gate`

Release/readiness remains `NOT_READY`.

Completion token:

`ACCEPT_RR_09_A6_PLAN_READY_FOR_NO_LIVE_IMPLEMENTATION_NOT_READY`
