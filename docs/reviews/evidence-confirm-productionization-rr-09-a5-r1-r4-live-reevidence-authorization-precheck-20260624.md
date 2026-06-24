# Evidence Confirm Productionization RR-09 A5 R1-R4 Live/PDF Re-evidence Authorization Precheck

Verdict token:

`RR_09_A5_R1_R4_REEVIDENCE_AUTHORIZATION_PRECHECK_READY_FOR_EXACT_AUTH_NOT_READY`

## Scope

Gate: `RR-09 A5 R1-R4 Live/PDF Re-evidence Authorization Precheck`.

Accepted prerequisite:

- A5 code-review controller judgment: `docs/reviews/evidence-confirm-productionization-rr-09-a5-code-review-controller-judgment-20260624.md`
- Accepted local implementation commit: `9d128b5`

This artifact is a precheck only. It does not execute live/PDF commands, product CLI commands, provider/LLM calls, repository/source-helper commands, checklist support, report-body rendering, V2/ECQ/quality-gate semantic changes, push, PR mutation, tag, release or readiness promotion.

## Current Accepted Implementation

A5 no-live implementation is accepted locally:

- Field-locator-capable processor family projection filters anchors by exact or dot-prefix `field=` identity.
- Field-locator-capable family fields with no compatible anchor receive `anchors=()`.
- Processor families with no recognized semicolon `field=` locator preserve existing `family_result.anchors`.
- Row/table/section validity remains Evidence Confirm materializer responsibility.
- R3 `missing_section=3` remains a separate fail-closed residual.

## Exact Next Authorization Needed

To execute runtime evidence, the user must authorize exactly:

`授权 RR-09 A5 R1-R4 live/PDF re-evidence after A5 no-live fixes`

## Authorized Command Shape After Exact Approval

The allowed command shape after exact approval is repository-bounded R1-R4 evidence only:

```bash
uv run python - <<'PY'
...
bundle = await FundDataExtractor().extract(fund_code, report_year, force_refresh=True)
projection = project_chapter_facts(bundle)
runner_result = await run_repository_bounded_evidence_confirm(
    EvidenceConfirmRepositoryRunRequest(
        fund_code=fund_code,
        report_year=report_year,
        projection=projection,
        force_refresh=False,
    )
)
diagnostic = summarize_value_match_diagnostics(...)
...
PY
```

Allowed samples:

| Residual | Sample |
|---|---|
| R1 | `004393 / 2025` |
| R2 | `004194 / 2024` |
| R3 | `006597 / 2024` |
| R4 | `110020 / 2024` |

Allowed evidence output:

- safe aggregate JSON only;
- source provenance summary;
- reference build status/count/reasons;
- strict V2 status/score/counts;
- diagnostic classifications and field buckets;
- `processor_row_locator_rows` count;
- recognized `processor_row_locator_*` issue counts;
- locator protocol summary for failing buckets when safe.

Forbidden output:

- raw annual-report excerpts;
- raw scalar token values;
- full structured field values;
- PDF/cache paths;
- source URLs or source-helper internals;
- provider payloads;
- report body text;
- secrets;
- tracebacks unless needed for fail-closed command failure classification.

## Explicitly Not Authorized

- No product CLI command, including B1 `017641 / 2024`.
- No provider/LLM command.
- No checklist Evidence Confirm support.
- No report-body Evidence Confirm rendering.
- No V2/ECQ/quality-gate semantic changes.
- No R3 missing-section fix.
- No B1 runtime residual fix.
- No push, PR mutation, tag, release or readiness claim.

## Expected Evidence Questions

The live/PDF evidence should answer:

- Does A5 increase field-compatible Processor row locator adoption in R1-R4 runtime projections?
- Do Processor-style row locators now materialize row-level references in real R1-R4 samples?
- Does A5 reduce R1-R4 `coarse_reference_insufficient` counts?
- Does strict deterministic V2 pass or still fail for each R1-R4 sample?
- Does R3 still report `missing_section=3`?
- Are any recognized Processor protocol failures now blocking reference materialization?
- If `processor_row_locator_rows=0` remains, is the residual more likely no-`field=`/legacy projection, section/table preflight failure, or another locator adoption gap?

## Residuals

| Residual | Destination |
|---|---|
| R1-R4 runtime closure | Exact user authorization above. |
| B1 `017641 / 2024` product CLI block | Separate B1 runtime gate. |
| R3 `missing_section=3` | Follow-up diagnostic/fix gate if still present after live/PDF re-evidence. |
| Release/readiness | `NOT_READY`. |

## Completion

Ready for exact authorization.

Completion token:

`RR_09_A5_R1_R4_REEVIDENCE_AUTHORIZATION_PRECHECK_READY_FOR_EXACT_AUTH_NOT_READY`
