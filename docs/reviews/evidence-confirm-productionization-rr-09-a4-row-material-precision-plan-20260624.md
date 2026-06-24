# Evidence Confirm Productionization RR-09 A4 Row-material Precision Plan

Verdict token:

`RR_09_A4_ROW_MATERIAL_PRECISION_PLAN_READY_FOR_REVIEW_NOT_READY`

## Scope

Gate: `RR-09 A4 R1-R4 Row-material Precision / R3 Missing-section Residual Planning Gate`.

This is a planning-only artifact. It does not authorize implementation, live/PDF execution, product CLI execution, provider/LLM calls, checklist support, report-body rendering, V2/ECQ/quality-gate semantic changes, push, PR mutation, tag, release or readiness promotion.

Accepted input:

- A3 no-live implementation/code review: `docs/reviews/evidence-confirm-productionization-rr-09-a3-code-review-controller-judgment-20260624.md`.
- Post-A3 R1-R4 evidence: `docs/reviews/evidence-confirm-productionization-rr-09-a3-live-pdf-reevidence-20260624.md`.
- Runtime re-evidence controller judgment: `docs/reviews/evidence-confirm-productionization-rr-09-runtime-reevidence-controller-judgment-20260624.md`.
- Current control truth: `docs/current-startup-packet.md` and `docs/implementation-control.md`.
- Current source code facts:
  - `fund_agent/fund/evidence_confirm_sources.py` owns annual-report reference materialization from already-loaded `ParsedAnnualReport`.
  - `fund_agent/fund/evidence_confirm_value_diagnostics.py` classifies `coarse_reference_insufficient` when proof references are downgraded or all proof references are table/section level.
  - `fund_agent/fund/processors/fund_disclosure_processor.py` emits semantic row locators such as `field=<path>; table_id=<id>; row=<index>; column=<index>; cell_id=<id>`.
  - `fund_agent/fund/documents/models.py` current `ParsedTable` exposes `page_number`, `table_index`, `headers` and `rows`, but not source cell IDs.

## Goal

Prepare a no-live implementation slice that uses existing Processor table/row locator information to reduce R1-R4 `coarse_reference_insufficient` without weakening Evidence Confirm V2.

The target behavior after later accepted implementation and separate live/PDF re-evidence:

1. Existing exact `row-N` behavior remains unchanged.
2. Processor-style semantic locators with a parseable `row=<zero_based_index>` and compatible `table_id` can materialize row-level annual-report excerpts.
3. Recognized Processor-protocol locators that are malformed, inconsistent or out of range fail closed with no proof reference; arbitrary non-Processor semantic locators still degrade to existing table/section excerpts with explicit informational issues.
4. V2 tokenization, value-match thresholds, source-truth admission, ECQ/quality-gate semantics and product runtime behavior remain unchanged.

## Motivation

Post-A3 re-evidence accepted these facts:

- R1-R4 source/PDF provenance is not the blocker: all four samples used EID `single_source_only`, fallback disabled/unused and admitted metadata.
- A3 closed the prior R3 `bond_risk_group_anchor_projection_gap`.
- Strict deterministic V2 still fails for all R1-R4.
- Remaining value-match failures are dominated by `coarse_reference_insufficient` for `fee_schedule`, `nav_benchmark_performance`, `manager_alignment` and `manager_strategy_text`.
- R3 also has `missing_section=3` in reference materialization.

The immediate cause is reference precision: V2 is receiving table/section proof excerpts where row/material excerpts are required. The minimal correct fix is to connect already-produced Processor row information to the materializer, not to loosen V2 matching.

## Success Signals

No-live implementation acceptance should require all of the following before any live/PDF re-evidence:

- Processor-style row locators with valid `row=<index>` and compatible `table_id` produce `EvidenceConfirmReference.row_locator` and row-only `excerpt_text`.
- The row excerpt contains the target row and excludes adjacent rows.
- Shared-anchor ambiguity remains fail-closed or table-level unless the row index is explicit and internally consistent.
- A recognized Processor-protocol locator with mismatched embedded `table_id`, missing embedded `table_id`, missing `row`, non-integer row, negative row, out-of-range row or missing compatible table creates no proof reference and emits a blocking issue.
- Unsupported arbitrary semantic locators continue to follow the A3 downgrade path and do not get misclassified as Processor-protocol failures.
- R3 `missing_section=3` is not hidden by row parsing; missing sections remain blocking reference-builder issues until a separate root-cause fix/disposition handles them.
- Release/readiness remains `NOT_READY`.

## Non-goals

- No live/PDF command.
- No product CLI command, including B1 `017641 / 2024`.
- No provider/LLM command.
- No threshold relaxation or new pass rule in `confirm_projection_evidence_v2`.
- No ECQ or quality-gate semantic change.
- No checklist Evidence Confirm support.
- No report-body Evidence Confirm rendering.
- No fallback source policy change.
- No direct source/PDF/cache/helper access outside `FundDocumentRepository`.
- No parser replacement, Docling productionization or candidate artifact promotion.
- No public schema version bump.
- No broad extractor rewrite.
- No sub-anchor schema migration in this slice.
- No tag, release, readiness promotion, push or PR external-state mutation.

## First-principles Judgment

Evidence Confirm V2 can only prove a material value against the references it receives. If the annual-report materializer converts a row/cell-backed product anchor into a whole table or whole section excerpt, V2 correctly treats the proof as imprecise and fails or warns. Fixing this by relaxing token matching would reduce audit quality. Fixing it by using existing row identity preserves the evidence contract.

The current Processor already carries row identity in its semantic locator strings. The materializer currently only recognizes `row-N` as a native row locator, then falls back to token-based narrowing for other semantic locators. Token-based narrowing is intentionally conservative and fails for many composite/multi-fact cases. Therefore A4 should add a small, deterministic parser for the Processor locator protocol and use the embedded row index only when table identity and row bounds are provably compatible with the already-loaded `ParsedTable`.

Because `ParsedTable` does not expose source `cell_id`, A4 must not claim cell-level proof. `column` and `cell_id` can be parsed for future diagnostics, but current accepted implementation should materialize at row level only.

## Direct Code Evidence

`fund_agent/fund/evidence_confirm_sources.py`:

- `SUPPORTED_ROW_LOCATOR_RE` only supports `row-N`.
- `_table_row_excerpt()` delegates unsupported row locators to `_semantic_row_locator_table_excerpt()`.
- `_single_fact_semantic_row_excerpt()` only narrows when exactly one available non-derived non-synthetic fact references the anchor and all material tokens uniquely match one row.
- `_semantic_row_locator_table_excerpt()` otherwise degrades to table excerpt and emits `semantic_row_locator_degraded_to_table_excerpt`.

`fund_agent/fund/evidence_confirm_value_diagnostics.py`:

- `_locator_downgraded()` detects source anchors that had `row_locator` but proof references lost row precision.
- `_only_coarse_references()` detects proof references that all lack row locators.
- `_classify_record()` returns `coarse_reference_insufficient` for either condition.

`fund_agent/fund/processors/fund_disclosure_processor.py`:

- Multiple source-truth processor paths emit locators shaped like `field=<output_path>; table_id=<table_id>; row=<row_index>; column=<column_index>; cell_id=<cell_id>`.

`fund_agent/fund/documents/models.py`:

- `ParsedTable.rows` is the only current row material available to Evidence Confirm; there is no stable parsed cell-id model to validate `cell_id`.

`tests/fund/test_evidence_confirm_sources.py`:

- Existing tests already cover exact `row-0`, semantic locator single-fact narrowing, shared-anchor table downgrade, partial-token table downgrade, section downgrade and repository pathway warning behavior.

## Affected Files

Planned implementation files:

- `fund_agent/fund/evidence_confirm_sources.py`
- `tests/fund/test_evidence_confirm_sources.py`
- `fund_agent/fund/README.md`

Possible implementation evidence artifact:

- `docs/reviews/evidence-confirm-productionization-rr-09-a4-implementation-evidence-20260624.md`

Follow-up review/controller artifacts:

- code review and controller judgment artifacts under `docs/reviews/`.

## Contract / Schema / State Changes

No public CLI, Service, Host, quality-gate, Evidence Confirm V2 result schema, ECQ schema, report-body contract or `chapter_fact_projection.v1` schema change is planned.

Internal behavior change:

- The annual-report reference materializer may preserve row precision for a Processor-style semantic locator when it can parse a compatible zero-based row index and build a bounded row excerpt from the already-loaded `ParsedTable`.

Internal non-change:

- `column` and `cell_id` inside Processor locators do not become proof-bearing fields in A4 because current `ParsedTable` cannot validate them.

## Implementation Slices

### Slice A4-S1: Processor Row Locator Protocol Materialization

Objective:

Support the current Processor semantic row locator protocol in `evidence_confirm_sources.py` so row-backed product anchors can materialize row-level references without relying on token-based unique-row fallback.

Allowed files:

- `fund_agent/fund/evidence_confirm_sources.py`
- `tests/fund/test_evidence_confirm_sources.py`
- `fund_agent/fund/README.md`
- `docs/reviews/evidence-confirm-productionization-rr-09-a4-implementation-evidence-20260624.md`

Exact allowed changes:

- Add a private parser for semicolon-delimited locator key/value pairs.
- Distinguish three locator classes:
  - exact native `row-N`, which keeps the current path unchanged;
  - recognized Processor protocol, meaning a semicolon-delimited locator containing at least one Processor key from `field`, `table_id`, `row`, `column` or `cell_id`;
  - arbitrary semantic locator, which keeps the current A3 token-based narrowing and table/section downgrade behavior.
- For recognized Processor protocol, accept only the bounded shape:
  - `field=<non-empty string>`
  - `table_id=<non-empty string>`
  - `row=<zero_based_integer>`
  - optional `column=<zero_based_integer>`
  - optional `cell_id=<non-empty string>`
- Add a private helper that attempts row materialization from the parsed locator before token-based semantic narrowing.
- Require embedded `table_id` to equal `anchor.table_id`.
- Require `anchor.table_id` to have already matched the compatible `page-{page_number}-table-{table_index}` table identity.
- Require `row` to be a non-negative integer and within `ParsedTable.rows`.
- Build excerpt with the existing `_format_table_row_excerpt()` and `_normalize_whitespace()` path.
- Preserve the original `anchor.row_locator` in `EvidenceConfirmReference.row_locator` when row materialization succeeds.
- For recognized Processor protocol failures, return no reference with a blocking issue; do not degrade to table excerpt.
- Keep existing semantic downgrade behavior only for arbitrary non-Processor semantic locators and for token-based narrowing failures that are not recognized Processor-protocol failures.
- Emit issue reasons precise enough for diagnostics, for example:
  - `semantic_row_locator_degraded_to_table_excerpt` for unsupported semantic locators that continue through the old downgrade path;
  - `processor_row_locator_table_mismatch` for mismatched embedded `table_id`;
  - `processor_row_locator_missing_table_id` for recognized Processor locators without embedded `table_id`;
  - `processor_row_locator_missing_row` for recognized Processor locators without `row`;
  - `processor_row_locator_invalid_row` for non-integer or negative row;
  - `processor_row_locator_out_of_range` for row indexes outside `ParsedTable.rows`.
- Do not read source helpers, PDF/cache paths, Docling artifacts, provider payloads or product CLI output.
- Do not alter V2 matching primitives or thresholds.

Expected no-live tests:

- Add a passing test proving `field=fee_schedule.management_fee; table_id=page-3-table-0; row=1; column=2; cell_id=c-1` materializes only row 1, preserves the original row locator, and passes V2 when the fact value tokens are present in that row.
- Add a passing test proving a shared-anchor multi-fact case with an explicit Processor row locator can materialize row-level proof when the embedded row is valid. This distinguishes explicit locator proof from A3 token-based single-fact proof.
- Add fail-closed Processor-protocol tests that assert `status="fail"`, `references == ()` and blocking severity for:
  - embedded `table_id` mismatch;
  - non-integer row;
  - negative row;
  - out-of-range row;
  - missing `row`;
  - missing embedded `table_id`;
- Add a separate degradation regression proving unsupported arbitrary semantic locators still follow the existing informational table downgrade behavior.
- Keep existing A3 semantic narrowing tests unchanged unless assertion text needs a new issue reason.
- Add a repository runner test or update the existing degraded semantic locator test only if the new issue reason affects pathway warning assertions.

Validation commands:

```bash
uv run pytest tests/fund/test_evidence_confirm_sources.py
uv run ruff check fund_agent/fund/evidence_confirm_sources.py tests/fund/test_evidence_confirm_sources.py
git diff --check
```

Expected assertions:

- Focused tests pass.
- Ruff passes for touched files.
- Diff whitespace check passes.
- No live/PDF/product/provider command is run.

Completion signal:

- Implementation evidence artifact records changed files, tests, behavior, residuals and verdict token.
- Code review gate can review only `evidence_confirm_sources.py`, `tests/fund/test_evidence_confirm_sources.py`, `fund_agent/fund/README.md` and the implementation artifact.

Stop condition:

- Stop after no-live implementation evidence and code review/controller judgment. Do not run R1-R4 live/PDF re-evidence without a separate exact authorization.

### Slice A4-S2: R1-R4 Live/PDF Re-evidence Authorization Precheck

Objective:

After A4-S1 implementation and review are accepted, prepare a separate authorization precheck for live/PDF re-evidence.

Allowed files:

- A future precheck artifact under `docs/reviews/`.

Exact allowed changes:

- Record exact command scope for R1-R4 repository-bounded live/PDF re-evidence.
- Confirm no provider/LLM/product CLI/checklist/report-body/tag/release/readiness action is included.
- Confirm the expected evidence output is aggregate/safe and does not emit raw PDF/cache paths, raw excerpts or report body.

Validation commands:

```bash
git diff --check
```

Stop condition:

- Stop after precheck unless the user separately grants the exact live/PDF authorization.

## R3 Missing-section Residual

R3 `missing_section=3` is not solved by row locator parsing if the section itself cannot be found during reference materialization. A4-S1 must not mask this issue.

Disposition:

- Treat R3 `missing_section=3` as a separate residual inside A4 planning.
- If A4-S1 live/PDF re-evidence later still reports `missing_section`, route it to a targeted missing-section diagnostic/fix gate.
- Do not change section matching in A4-S1 unless a no-live reproducer directly proves the row-locator parser depends on a wrong section preflight.

## B1 Runtime Residual

B1 `017641 / 2024` remains separate.

Expected interaction:

- A4-S1 may improve `manager_strategy_text` reference precision because that field uses row/cell-backed Processor locators.
- A4-S1 does not authorize product CLI execution or claim B1 closure.
- B1 runtime product CLI re-evidence still requires separate exact authorization after accepted implementation/review.

## Docs Decision

If A4-S1 changes materializer behavior, update `fund_agent/fund/README.md` to replace the current A3-only semantic locator wording with:

- exact `row-N` remains supported;
- Processor-style `field=...; table_id=...; row=...` can be materialized to row-level annual-report references when table identity and row bounds are valid;
- unsupported semantic locators still degrade to table/section excerpts with warnings;
- `column` and `cell_id` are not yet proof-bearing because `ParsedTable` does not expose stable cell identity.

No root `README.md`, Host, Agent or Service README update is expected because this is Fund internal Evidence Confirm materializer behavior.

## Risks and Open Questions

| Risk / question | Disposition |
|---|---|
| Processor locator `row` index origin might differ from `ParsedTable.rows` origin for some source paths. | A4-S1 tests must use zero-based contract because current `ParsedTable.table_index` is zero-based and Processor `row_index` fields are used as raw indexes. Live/PDF re-evidence remains separate proof. |
| `cell_id` cannot be validated against `ParsedTable`. | Explicitly not proof-bearing in A4-S1. A future ParsedTable cell model would require a separate schema/design gate. |
| Multi-fact shared anchor may still carry multiple values from the same row. | Explicit row locator can prove row-level support, but V2 still checks material tokens per fact. Do not split anchors in A4-S1. |
| R3 `missing_section=3` may remain. | Separate residual; do not hide it under row parsing. |
| B1 product CLI may still block on `manager_strategy_text`. | Separate runtime residual; requires separate re-evidence authorization. |
| Live/PDF behavior may differ from no-live fixtures. | Expected; A4-S2 precheck and explicit authorization are required before live/PDF proof. |

No blocking open question prevents A4-S1 planning review.

## Completion Report Format

Implementation closeout should report:

- changed files;
- parser protocol accepted/rejected cases;
- tests and results;
- whether docs were updated;
- residuals for live/PDF re-evidence, R3 missing-section and B1 runtime CLI;
- explicit statement that release/readiness remains `NOT_READY`.

## Completion

This plan is ready for plan review.

Next gate:

`RR-09 A4 Row-material Precision Plan Review`

Completion token:

`RR_09_A4_ROW_MATERIAL_PRECISION_PLAN_READY_FOR_REVIEW_NOT_READY`
