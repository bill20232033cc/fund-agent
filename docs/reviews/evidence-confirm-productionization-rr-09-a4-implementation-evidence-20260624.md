# Evidence Confirm Productionization RR-09 A4-S1 Implementation Evidence

Verdict token:

`RR_09_A4_S1_NO_LIVE_IMPLEMENTED_READY_FOR_CODE_REVIEW_NOT_READY`

## Scope

Gate: `RR-09 A4-S1 Processor Row Locator Protocol Materialization No-live Implementation`.

Accepted plan/controller:

- Plan: `docs/reviews/evidence-confirm-productionization-rr-09-a4-row-material-precision-plan-20260624.md`
- Controller judgment: `docs/reviews/evidence-confirm-productionization-rr-09-a4-plan-controller-judgment-20260624.md`

This implementation is no-live only. It did not run live/PDF commands, product CLI commands, provider/LLM calls, checklist support, report-body rendering, V2/ECQ/quality-gate semantic changes, push, PR mutation, tag, release or readiness promotion.

## Changed Files

| File | Change |
|---|---|
| `fund_agent/fund/evidence_confirm_sources.py` | Added private Processor row locator parsing and row-level materialization before A3 token-based semantic narrowing. |
| `tests/fund/test_evidence_confirm_sources.py` | Added no-live tests for Processor locator success, shared-anchor explicit row success, and blocking/no-reference failures. |
| `fund_agent/fund/README.md` | Documented current materializer behavior for native `row-N`, Processor-style row locators, arbitrary semantic locator downgrades, and non-proof-bearing `column`/`cell_id`. |

## Behavior Implemented

The materializer now distinguishes three row locator classes:

- Exact native `row-N`: unchanged existing path.
- Recognized Processor protocol: semicolon-delimited locator containing Processor keys from `field`, `table_id`, `row`, `column`, `cell_id`.
- Arbitrary semantic locator: existing A3 token-based narrowing / table-section downgrade path.

Recognized Processor protocol success:

- requires embedded `table_id` to equal `anchor.table_id`;
- requires the already-resolved compatible `ParsedTable`;
- requires `row` to be a non-negative integer within `ParsedTable.rows`;
- builds excerpt through the existing table-row formatting/normalization path;
- preserves original `anchor.row_locator` in the resulting `EvidenceConfirmReference`.

Recognized Processor protocol failures now produce no proof reference and a blocking issue:

- `processor_row_locator_malformed`;
- `processor_row_locator_missing_table_id`;
- `processor_row_locator_table_mismatch`;
- `processor_row_locator_missing_row`;
- `processor_row_locator_invalid_row`;
- `processor_row_locator_out_of_range`.

`column` and `cell_id` remain non-proof-bearing because current `ParsedTable` does not expose stable cell identity.

## Validation

Focused no-live tests:

```bash
uv run pytest tests/fund/test_evidence_confirm_sources.py -q
```

Result:

- Passed: `52 passed in 1.28s`.

Static lint:

```bash
uv run ruff check fund_agent/fund/evidence_confirm_sources.py tests/fund/test_evidence_confirm_sources.py
```

Result:

- Passed: `All checks passed!`

Whitespace/static diff check:

```bash
git diff --check
```

Result:

- Passed.

## Residuals

| Residual | Status / destination |
|---|---|
| A4 code review | Required next. |
| R1-R4 live/PDF closure | Not proven by this no-live implementation; requires separate post-review authorization precheck and exact authorization. |
| R3 `missing_section=3` | Not fixed by A4-S1; route to missing-section diagnostic/fix if still present after live/PDF re-evidence. |
| B1 `017641 / 2024` product CLI block | Not tested or closed; separate B1 runtime residual gate. |
| Cell-level proof via `cell_id` | Deferred; requires a future ParsedTable/cell identity schema gate. |
| Release/readiness | `NOT_READY`. |

## Completion

Ready for code review.

Completion token:

`RR_09_A4_S1_NO_LIVE_IMPLEMENTED_READY_FOR_CODE_REVIEW_NOT_READY`
