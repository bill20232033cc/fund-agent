# Evidence Confirm Productionization RR-09 A6 R1-R4 Live/PDF Re-evidence Authorization Precheck

Verdict token:

`RR_09_A6_R1_R4_REEVIDENCE_AUTHORIZATION_PRECHECK_READY_FOR_EXACT_AUTH_NOT_READY`

## Scope

Gate: `RR-09 A6 R1-R4 Live/PDF Re-evidence Authorization Precheck`.

Accepted prerequisites:

- A6 plan/controller judgment: `docs/reviews/evidence-confirm-productionization-rr-09-a6-plan-controller-judgment-20260624.md`
- A6 no-live implementation evidence: `docs/reviews/evidence-confirm-productionization-rr-09-a6-implementation-evidence-20260624.md`
- A6 code review: `docs/reviews/code-review-20260624-130643.md`
- Accepted local implementation commit: `ad68c32`

This artifact is a precheck only. It does not execute live/PDF commands, repository/source-helper/parser commands, product CLI commands, provider/LLM calls, checklist support, report-body rendering, V2/ECQ/quality-gate semantic changes, push, PR mutation, tag, release or readiness promotion.

## Current Accepted Implementation

A6 no-live implementation is accepted locally:

- Default parsed annual processor projection wraps legacy extractor anchors with top-level `source_field_path=<field>` semantic locators.
- `StructuredFundDataBundle` projection filters anchors by either Processor `field=` identity or semantic `source_field_path=` identity.
- Evidence Confirm materializer scopes semantic row-narrowing tokens only when `source_field_path` is present.
- `source_field_path=<field>` uses the top-level fact value and does not fabricate row-level subfield proof from composite dictionaries.
- Explicit `source_field_path=<field>.<subfield>` can narrow to a subvalue only when direct subfield provenance is supplied by an extractor-specific future gate.
- FDD default-on route, public `EvidenceAnchor` schema, V2/ECQ semantics and quality-gate semantics remain unchanged.

## Exact Next Authorization Needed

To execute runtime evidence, the user must authorize exactly:

`授权 RR-09 A6 R1-R4 live/PDF re-evidence after A6 no-live fixes`

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
- value-match diagnostics;
- semantic locator adoption counts, including whether top-level `source_field_path` anchors appear in live projections;
- row/table/section reference counts and downgrade reasons.

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

- No A5 re-evidence rerun on the current A6 code state.
- No product CLI command, including B1 `017641 / 2024`.
- No provider/LLM command.
- No checklist Evidence Confirm support.
- No report-body Evidence Confirm rendering.
- No V2/ECQ/quality-gate semantic changes.
- No FDD default-on parsing.
- No direct subfield provenance inference from composite value shape.
- No R3 missing-section fix.
- No B1 runtime residual fix.
- No push, PR mutation, tag, release or readiness claim.

## Expected Evidence Questions

The live/PDF evidence should answer:

- Do live R1-R4 projections now expose top-level `source_field_path=<field>` anchors for the affected structured fields?
- Does top-level semantic locator adoption reduce `coarse_reference_insufficient` counts from the accepted A5 live baseline?
- Do any references narrow to row-level evidence through explicit subfield provenance, or do composite top-level facts still degrade safely to table/section excerpts?
- Does strict deterministic V2 pass or still fail for each R1-R4 sample?
- Does R3 still report `missing_section=3`?
- Are any materializer downgrade or protocol issues now blocking reference materialization?

## Residuals

| Residual | Destination |
|---|---|
| R1-R4 runtime closure after A6 | Exact user authorization above. |
| Composite subfield row precision from default parsed annual route | Separate extractor-specific direct subfield provenance gate if needed. |
| B1 `017641 / 2024` product CLI block | Separate B1 runtime gate. |
| R3 `missing_section=3` | Follow-up diagnostic/fix gate if still present after live/PDF re-evidence. |
| Release/readiness | `NOT_READY`. |

## Completion

Ready for exact authorization.

Completion token:

`RR_09_A6_R1_R4_REEVIDENCE_AUTHORIZATION_PRECHECK_READY_FOR_EXACT_AUTH_NOT_READY`
