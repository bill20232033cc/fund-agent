# Evidence Confirm Productionization RR-09 A4 R1-R4 Live/PDF Re-evidence Authorization Precheck

Verdict token:

`RR_09_A4_R1_R4_REEVIDENCE_AUTHORIZATION_PRECHECK_READY_FOR_EXACT_AUTH_NOT_READY`

## Scope

Gate: `RR-09 A4-S2 R1-R4 Live/PDF Re-evidence Authorization Precheck`.

Accepted prerequisite:

- A4-S1 code-review controller judgment: `docs/reviews/evidence-confirm-productionization-rr-09-a4-code-review-controller-judgment-20260624.md`
- Accepted local implementation commit: `04c9124`

This artifact is a precheck only. It does not execute live/PDF commands, product CLI commands, provider/LLM calls, checklist support, report-body rendering, V2/ECQ/quality-gate semantic changes, push, PR mutation, tag, release or readiness promotion.

## Current Accepted Implementation

A4-S1 no-live implementation is accepted locally:

- Native `row-N` materialization remains unchanged.
- Recognized Processor-style `field=...; table_id=...; row=...` locators can produce row-level annual-report references when table identity and row bounds are valid.
- Recognized Processor protocol failures are blocking/no-reference.
- Arbitrary non-Processor semantic locators keep the A3 downgrade path.
- `column` and `cell_id` are not proof-bearing.

## Exact Next Authorization Needed

To execute runtime evidence, the user must authorize exactly:

`授权 RR-09 A4 R1-R4 live/PDF re-evidence after A4-S1 no-live fixes`

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
- diagnostic classifications and field buckets.

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

- Does A4-S1 reduce R1-R4 `coarse_reference_insufficient` counts?
- Do Processor-style row locators now materialize row-level references in real R1-R4 samples?
- Does strict deterministic V2 pass or still fail for each R1-R4 sample?
- Does R3 still report `missing_section=3`?
- Are any recognized Processor protocol failures now blocking reference materialization?

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

`RR_09_A4_R1_R4_REEVIDENCE_AUTHORIZATION_PRECHECK_READY_FOR_EXACT_AUTH_NOT_READY`
