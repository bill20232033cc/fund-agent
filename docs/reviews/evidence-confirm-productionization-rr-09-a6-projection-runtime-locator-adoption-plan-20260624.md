# Evidence Confirm Productionization RR-09 A6 Projection / Runtime Locator Adoption Plan

Verdict token:

`RR_09_A6_PLAN_READY_FOR_REVIEW_NOT_READY`

## Goal

Plan a no-live implementation that makes the default `ParsedAnnualReport` product projection expose top-level field-scoped semantic locators to Evidence Confirm, while reserving subfield-scoped semantic locators for sources that already carry direct anchor-to-subfield provenance. The goal is to remove cross-field shared-anchor ambiguity without fabricating row numbers, subfield provenance or enabling the explicit FundDisclosureDocument route by default.

## Motivation

A5 live/PDF re-evidence proved that A5 did not reach the real R1-R4 runtime locator surface:

- `recognized_processor_row_locator_anchors=0`
- `processor_row_locator_rows=0`
- strict V2 still failed for all R1-R4 samples
- `coarse_reference_insufficient` remained unchanged at `53`

The current direct evidence points to a projection/runtime locator adoption gap, not a Processor row-locator parser failure.

## Success Signal

The implementation is successful when no-live tests prove all of the following:

1. Default `FundDataExtractor.extract(..., disclosure_intermediate=None)` keeps the `parsed_annual_report.v1` processor route and does not enable FundDisclosureDocument by default.
2. Parsed annual field-family projection emits non-Processor top-level field-scoped semantic locators for public fields such as:
   - `fee_schedule`
   - `nav_benchmark_performance`
   - `manager_alignment`
   - `manager_strategy_text`
3. The existing `field=...; table_id=...; row=...` Processor row locator protocol remains unchanged.
4. Recognized Processor protocol failures still fail closed; the new semantic locator syntax does not trigger Processor parser errors.
5. Evidence Confirm materializer supports subfield-scoped semantic locators only when a caller supplies direct subfield-scoped anchors; parsed annual projection must not infer subfield scope from value shape alone.
6. Existing no-`field=` family anchors are still preserved where no scoped locator exists.

Release/readiness remains `NOT_READY`.

## Non-goals

- Do not run live/PDF, product CLI, provider/LLM, repository/source-helper diagnostics or release commands.
- Do not enable `FundDisclosureDocument` parsing or FDD processor route by default.
- Do not change V2 thresholds, ECQ/quality-gate semantics, checklist support or report-body rendering.
- Do not fabricate `row=` values from legacy locators.
- Do not infer subfield provenance from composite value shape alone.
- Do not treat `column` or `cell_id` as proof-bearing.
- Do not remove A4/A5 Processor row locator support.
- Do not fix R3 `missing_section=3` in this gate.
- Do not change public `StructuredFundDataBundle` field names or chapter fact schema version.

## Direct Code Evidence

### Default Runtime Route

`FundDataExtractor.extract()` loads the annual report through the repository and, when `disclosure_intermediate is None`, routes classified funds to `_extract_classified_fund_via_processor(...)`.

`_extract_classified_fund_via_processor(...)` dispatches:

```text
intermediate_kind="parsed_annual_report.v1"
processor_goal="template_chapters_1_6_minimum_field_families"
```

The explicit FDD route is separate and only runs when `disclosure_intermediate` is provided.

### Parsed Annual Processor Anchor Surface

`_ParsedAnnualReportFundProcessor.extract()` calls `_collect_existing_extractor_fields(report)` and then `_build_field_family_result(...)`.

`_build_field_family_result(...)` currently does:

```text
value[mapping.output_field_name] = field.value
anchors.extend(field.anchors)
```

This aggregates old extractor anchors at the family level without adding output-field identity. It also does not preserve a direct anchor-to-subfield mapping, so A6 must not infer subfield locators from composite values alone.

### FDD Processor Anchor Surface

`fund_disclosure_processor.py` already emits row locators such as:

```text
field=fee_schedule.management_fee; table_id=...; row=...; column=...; cell_id=...
field=manager_strategy_text.strategy_summary; block_id=...
```

But those locators are only available in the explicit FDD route. A5 live evidence showed they do not appear in default R1-R4 runtime projection.

### Current Materializer Constraint

`evidence_confirm_sources.py` treats semicolon row locators containing keys in:

```text
("field", "table_id", "row", "column", "cell_id")
```

as Processor row locators. Therefore adding `field=...` without a valid `table_id` and `row` would be unsafe because it would trigger Processor protocol validation and fail closed.

The existing semantic row narrowing path uses `_single_fact_semantic_row_excerpt(...)`, but it currently uses `_material_tokens(facts[0].value)`. For composite facts, this requires all subvalue tokens to match a single row, which is too strict when each subvalue lives on a different row.

## Design Decision

Introduce a distinct non-Processor semantic locator key:

```text
source_field_path=<top_level_or_subfield_path>; locator=<legacy_locator>
```

Rules:

- `source_field_path` is not part of `PROCESSOR_ROW_LOCATOR_KEYS`; it must stay on the semantic locator path.
- `field=...` remains reserved for Processor row locators.
- The new locator is only proof-scoping metadata; it is not row proof.
- Parsed annual processors may emit only top-level `source_field_path` values unless they have direct source evidence linking an anchor to a subfield.
- Subfield paths are allowed only for already-proven subfield anchors such as explicit FDD source-truth anchors or no-live materializer fixtures that model such direct provenance.
- Row-level proof still requires the materializer to match scoped material tokens against exactly one parsed table row.
- If scoped token narrowing fails, the materializer keeps the existing safe table/section downgrade and V2 anchor-precision warning behavior.

## Affected Files

Implementation files:

- `fund_agent/fund/processors/active_annual.py`
- `fund_agent/fund/data_extractor.py`
- `fund_agent/fund/evidence_confirm_sources.py`
- `fund_agent/fund/README.md`

Tests:

- `tests/fund/test_data_extractor.py`
- `tests/fund/test_evidence_confirm_sources.py`

Docs/control artifacts after implementation:

- implementation evidence artifact under `docs/reviews/`
- code review artifact under `docs/reviews/`
- `docs/implementation-control.md`
- `docs/current-startup-packet.md`

## Contract Changes

No public schema version changes.

Internal locator contract extension:

| Locator family | Example | Meaning | Materializer path |
|---|---|---|---|
| Processor row locator | `field=fee_schedule.management_fee; table_id=page-3-table-0; row=5; column=3` | Explicit processor row proof candidate | Processor parser; fail-closed on malformed protocol |
| Top-level scoped semantic locator | `source_field_path=fee_schedule; locator=management_fee` | Parsed annual anchor belongs to this public top-level field | Existing semantic path; downgrade safely if no unique row |
| Direct subfield scoped semantic locator | `source_field_path=fee_schedule.management_fee; locator=management_fee` | Caller already has direct anchor-to-subfield provenance | Existing semantic path; downgrade safely if no unique row |
| Legacy semantic locator | `management_fee` or `portfolio_manager:张三` | Existing semantic locator | Existing semantic path |

## Implementation Slices

### A6-S1 Parsed Annual Field-scope Locator Projection

Objective:

Add top-level field identity to parsed annual field-family anchors without changing default route selection, fabricating rows or inferring subfield provenance.

Allowed files:

- `fund_agent/fund/processors/active_annual.py`
- `fund_agent/fund/data_extractor.py`
- `tests/fund/test_data_extractor.py`
- `fund_agent/fund/README.md`

Exact changes:

1. In `active_annual.py`, add module-level helpers:
   - `_field_scoped_anchors(mapping: FieldFamilyMapping, field: ExtractedField[object]) -> tuple[EvidenceAnchor, ...]`
   - `_with_source_field_path(anchor: EvidenceAnchor, source_field_path: str) -> EvidenceAnchor`
   - `_sanitize_legacy_locator(row_locator: str | None) -> str`
2. `_field_scoped_anchors(...)` should clone every existing anchor with `source_field_path=mapping.output_field_name` only.
   - It must not walk dict values to create leaf paths.
   - It must not emit `source_field_path=<field>.<subfield>` for parsed annual fields.
   - If `field.anchors` is empty, return `()`.
3. `_with_source_field_path(...)` should clone the existing anchor with:
   - same `source_kind`, `document_year`, `section_id`, `page_number`, `table_id`, `note`;
   - `row_locator=f"source_field_path={source_field_path}; locator={sanitized_legacy_locator}"`.
4. `_build_field_family_result(...)` should replace `anchors.extend(field.anchors)` with field-scoped anchors when `_field_has_public_value(field)` is true.
5. In `data_extractor.py`, extend field filtering so `_anchors_for_family_field(...)` recognizes both:
   - Processor `field=...`
   - semantic `source_field_path=...`
6. Preserve current behavior:
   - if a family has no recognized field identity locator, return original `family_result.anchors`;
   - if a family has recognized field identity locators but none match the requested top-level field, return `()`.

Tests:

1. Add or update `tests/fund/test_data_extractor.py` to prove default parsed annual route emits top-level `source_field_path=` locators for at least `fee_schedule` and `nav_benchmark_performance`.
2. Add a direct `_field_from_family(...)` test proving `source_field_path=nav_benchmark_performance` does not attach to `fee_schedule`.
3. Add a negative test proving parsed annual projection does not generate `source_field_path=fee_schedule.management_fee` or other inferred subfield locators from composite dict values.
4. Keep existing explicit FDD tests asserting `field=...` locators unchanged.
5. Keep existing no-`field=` family preservation tests.

Expected validation:

```bash
uv run pytest tests/fund/test_data_extractor.py -q
uv run ruff check fund_agent/fund/processors/active_annual.py fund_agent/fund/data_extractor.py tests/fund/test_data_extractor.py
git diff --check
```

Stop condition:

- Stop for review after tests pass and implementation evidence is written.
- Do not run live/PDF.

### A6-S2 Scoped Semantic Materializer Narrowing

Objective:

Support scoped semantic locator metadata in the materializer without allowing parsed annual projection to fabricate subfield scope. Top-level scoped locators keep existing whole-value token behavior. Direct subfield-scoped locators, when already provided by a proven source, narrow by subvalue tokens.

Allowed files:

- `fund_agent/fund/evidence_confirm_sources.py`
- `tests/fund/test_evidence_confirm_sources.py`
- `fund_agent/fund/README.md`

Exact changes:

1. Add helper `_semantic_source_field_path(row_locator: str | None) -> str | None`.
   - It must parse semicolon `key=value` locators.
   - It must only return the `source_field_path` value.
   - It must not treat `source_field_path` as Processor protocol.
2. Add helper `_material_tokens_for_anchor_scope(fact: ChapterFactEntry, anchor: ChapterEvidenceAnchor) -> tuple[str, ...]`.
   - If `source_field_path` is absent, return existing `_material_tokens(fact.value)`.
   - If `source_field_path` is present and exactly equals `fact.source_field_name`, return existing `_material_tokens(fact.value)`.
   - If `source_field_path` is present and its top-level component matches `fact.source_field_name`, strip the top-level component and resolve the remaining path against `fact.value`.
   - If the path resolves to a value, return `_material_tokens(resolved_value)`.
   - If it cannot resolve, return `()`, forcing safe downgrade rather than broadening proof.
3. Update `_single_fact_semantic_row_excerpt(...)` to call `_material_tokens_for_anchor_scope(...)`.
4. Keep all existing safety predicates:
   - exactly one narrowable fact;
   - non-empty tokens;
   - exactly one matching parsed table row;
   - otherwise return `None` and downgrade.
5. Do not modify Processor parser behavior or V2 scoring thresholds.

Tests:

1. Add a top-level scoped fixture proving `source_field_path=fee_schedule` stays on the semantic path and does not trigger Processor parser errors.
2. Add a table fixture with two rows, one for management fee and one for custody fee.
3. Create one composite `fee_schedule` fact with two direct subfield-scoped anchors:
   - `source_field_path=fee_schedule.management_fee; locator=management_fee`
   - `source_field_path=fee_schedule.custody_fee; locator=custody_fee`
4. Assert `build_annual_report_evidence_confirm_references(...)` materializes two row-level references for the direct subfield fixture.
5. Assert `confirm_projection_evidence_v2(...)` no longer fails `value_match` for that direct subfield fixture.
6. Add a negative case where a parsed-annual-style top-level scoped composite fact still downgrades rather than pretending each subfield has direct row proof.
7. Add a negative case where the scoped token appears in multiple rows and assert it downgrades to table reference with the existing informational downgrade reason.

Expected validation:

```bash
uv run pytest tests/fund/test_evidence_confirm_sources.py -q
uv run ruff check fund_agent/fund/evidence_confirm_sources.py tests/fund/test_evidence_confirm_sources.py
git diff --check
```

Stop condition:

- Stop for review after tests pass and implementation evidence is written.
- Do not run live/PDF.

## Docs Decision

Update `fund_agent/fund/README.md` only after implementation because this gate changes Fund-layer internal locator semantics. Do not update `docs/design.md` unless the implementation review finds a design-truth mismatch that needs a separate control/design sync gate.

## Risks And Controls

| Risk | Control |
|---|---|
| Scoped semantic locators accidentally trigger Processor parser fail-closed behavior | Use `source_field_path`, not `field`; add materializer test proving it stays on semantic path. |
| Subfield path scoping hides unmatched tokens | If path cannot resolve, return empty tokens and downgrade; do not treat it as pass. Parsed annual projection must not infer subfield paths. |
| Composite value shape fabricates subfield proof | Parsed annual A6-S1 emits only top-level field scope; direct subfield scope requires source-proven anchor-to-subfield evidence. |
| Field-scoped anchors over-attach to unrelated top-level fields | Extend `_anchors_for_family_field(...)` matching and direct tests. |
| Implementation fabricates row proof | Do not write `row=` unless the source already provides a proved parsed table row index. |
| FDD route becomes default by accident | Add default route regression; no `disclosure_intermediate` means parsed annual route. |
| R3 `missing_section=3` is conflated with locator adoption | Keep R3 missing-section as a separate residual. |

## Completion Report Format

Implementation evidence must report:

- changed files;
- exact tests and results;
- whether default parsed annual route now emits `source_field_path=` locators in no-live tests;
- whether direct subfield-scoped semantic materializer tests produce row-level references;
- whether parsed-annual-style top-level scoped composite facts avoid fabricated subfield row proof;
- residuals still requiring live/PDF re-evidence;
- explicit statement that release/readiness remains `NOT_READY`.

## Next Gate

`RR-09 A6 Plan Review Gate`

Completion token:

`RR_09_A6_PLAN_READY_FOR_REVIEW_NOT_READY`
