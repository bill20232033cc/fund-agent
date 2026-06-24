# RR-09 A5 Projection Locator Adoption / R3 Missing-section Residual Plan

Verdict target: `RR_09_A5_PLAN_READY_FOR_NO_LIVE_IMPLEMENTATION_NOT_READY`

Gate: `RR-09 A5 Projection Locator Adoption / R3 Missing-section Residual Planning Gate`.

## Current Status

Release/readiness remains `NOT_READY`.

A4-S1 added no-live support for Processor-style row locators in `fund_agent/fund/evidence_confirm_sources.py`, including blocking behavior for malformed, mismatched or out-of-range Processor locators. A4 live/PDF re-evidence was accepted as evidence but did not improve runtime results:

- strict V2 still fails for R1-R4;
- `processor_row_locator_rows=0` for all four samples;
- no `processor_row_locator_*` blocking issue appeared;
- `coarse_reference_insufficient` counts are unchanged from A3;
- R3 still has `missing_section=3`.

This proves A4 row materialization is not receiving a usable runtime locator/reference shape for the current residuals. It does not by itself prove whether the source is:

- runtime projection not carrying Processor locators;
- runtime path using legacy extractor locators;
- Processor anchors being broadcast at field-family granularity;
- table/section identity mismatch before Processor row parsing;
- or a separate reference-builder section identity residual.

## Goal

Prepare the next no-live implementation gate that explains and fixes the projection-side locator adoption gap without weakening Evidence Confirm.

The target is not to make strict V2 pass by accepting broader evidence. The target is to make each proof-positive fact bind only to source-compatible anchors so that existing Evidence Confirm materialization can either:

- build row-level proof references from already available Processor row/table locators; or
- fail closed with a specific diagnostic when the locator, table or section identity is not usable.

## Motivation

The coarse-reference residual is now upstream of A4 row parsing. A4 can materialize Processor row locators, but current R1-R4 evidence shows those locators are not becoming successful references. The next gate must inspect and correct the data path between Processor/extractor output and `ChapterFactProjection`/reference build.

## Success Signals

No-live implementation is successful only if deterministic tests and artifacts prove all of the following:

1. For target fields `fee_schedule`, `nav_benchmark_performance`, `manager_alignment` and `manager_strategy_text`, projection diagnostics can report:
   - fact id / source field id;
   - bound anchor ids;
   - section id;
   - table id;
   - row locator;
   - locator protocol class;
   - whether the anchor's locator field path matches the fact field path.
2. For proof-positive FDD processor fixtures, field-family anchors are not blindly assigned to every top-level bundle field.
3. Composite top-level fields select only anchors whose `field=` path belongs to that field, including child paths such as `fee_schedule.management_fee`.
4. If a field value exists but no matching source anchor exists, the projected field remains fail-closed with empty anchors rather than borrowing unrelated family anchors.
5. R3 `missing_section=3` remains visible as its own reference-builder issue and is not hidden by row locator adoption.
6. No live/PDF, provider/LLM, product CLI, checklist/report-body rendering, V2/ECQ/quality-gate semantic, release or tag behavior changes occur in this gate.

## Non-goals

- Do not run live/PDF or product CLI commands.
- Do not change V2 value-match semantics.
- Do not treat table-level or section-level excerpts as sufficient row proof.
- Do not add provider-backed semantic default-on behavior.
- Do not add checklist Evidence Confirm support or report-body rendering.
- Do not change source admission, fallback policy, repository API, parser/cache access policy or release/readiness state.
- Do not fix R3 `missing_section=3` by guessing section ids from headings or page text.
- Do not make Service/UI/Host consume parser artifacts, Docling/FDD internals or repository internals directly.

## Direct Code Evidence

### A4 materializer boundary

`fund_agent/fund/evidence_confirm_sources.py` builds references from `ChapterFactProjection` annual-report anchors. It preflights section identity before excerpt materialization and only enters `_table_row_excerpt()` after a supported table id is found.

Key facts:

- `_projection_annual_anchors()` reads anchors from projection chapters.
- `_facts_by_anchor()` maps anchor ids to all facts that cite them.
- `_anchor_preflight_issue()` returns blocking `missing_section` before any table/row locator logic.
- `_table_excerpt()` only supports `page-{page_number}-table-{table_index}` table ids.
- `_table_row_excerpt()` now supports native `row-N`, Processor `field=...; table_id=...; row=...`, and legacy semantic narrowing/downgrade.

Therefore A4 cannot repair anchors that never reach projection, have unsupported table identity, or fail section preflight.

### Bundle projection boundary

`fund_agent/fund/data_extractor.py::_field_from_family()` currently projects a top-level field by returning:

```python
ExtractedField(
    value=value,
    anchors=family_result.anchors,
    extraction_mode=family_result.extraction_mode,
    note=None,
)
```

This means every top-level field in a processor family receives the same family-level anchor tuple.

### Processor family anchor shape

`fund_agent/fund/processors/fund_disclosure_processor.py` builds field-family anchors by deduping selected output-path anchors:

- `return_attribution.v1` uses emitted paths including `nav_benchmark_performance.nav_growth_rate`, `nav_benchmark_performance.benchmark_return_rate`, `fee_schedule.management_fee`, `fee_schedule.custody_fee`, `tracking_error`.
- `manager_profile.v1` uses emitted top-level paths such as `portfolio_managers`, `turnover_rate`, `manager_alignment`, `manager_strategy_text`, `holdings_snapshot`.

The Processor row locator format already carries field identity in `row_locator`, for example:

```text
field=fee_schedule.management_fee; table_id=...; row=...; column=...; cell_id=...
```

The family result contract currently exposes only `anchors`, not a per-field anchor map. The least invasive adoption point is therefore bundle projection, where top-level field names are already known.

### Legacy extractor anchor shape

Legacy extractors still emit field-name locators such as `management_fee`, `custody_fee`, `nav_growth_rate`, `benchmark_return_rate`, `manager_holding`, `employee_holding`, `strategy_summary` and `market_outlook`. Those locators are semantic and should not be rewritten into Processor locators unless a row/table identity is explicitly available and verified.

## First-principles Judgment

Evidence Confirm can only prove a value against text it can materialize. If one composite fact binds to a broad or unrelated anchor set, V2 either receives coarse excerpts or mismatched excerpts. Passing V2 by widening excerpt acceptance would weaken the audit. The correct direction is to preserve source specificity earlier in projection and let Evidence Confirm fail closed when specificity is absent.

The next implementation must not infer row identity from values or headings. It may only use locator identity already emitted by the Processor/extractor boundary.

## Affected Files and Modules

Planned implementation write set:

- `fund_agent/fund/data_extractor.py`
- `tests/fund/test_data_extractor.py`
- `fund_agent/fund/README.md`
- implementation evidence artifact under `docs/reviews/`
- code review/controller artifacts under `docs/reviews/`

Allowed only if A5-S0 proves a direct local need for a diagnostic helper:

- `fund_agent/fund/evidence_confirm_value_diagnostics.py`
- `tests/fund/test_evidence_confirm_value_diagnostics.py`

Do not edit in A5 no-live implementation unless a later reviewed slice explicitly authorizes it:

- `fund_agent/fund/evidence_confirm_sources.py`
- `fund_agent/fund/processors/fund_disclosure_processor.py`
- Service/UI/Host/runtime product CLI code
- source repository/cache/download helpers
- quality gate, V2 or ECQ semantic code

## Public Contract / Schema / State-machine Changes

No public schema change is planned.

`FundFieldFamilyResult` remains unchanged. The implementation must not add a new public per-field anchor schema in A5 unless a separate plan/review gate approves it.

Internal bundle projection behavior changes:

- For processor family projection where the family anchor set contains recognized semicolon `field=` Processor locators, each top-level `ExtractedField` should receive only anchors compatible with that field path.
- If a field-locator-capable family has recognized Processor field locators but none are compatible with the target field, do not borrow unrelated field-locator anchors.
- If a family has no recognized semicolon `field=` Processor locators, preserve the existing `family_result.anchors` behavior; this protects non-FDD processor paths that intentionally wrap legacy extractor anchors.
- Missing fields stay `extraction_mode="missing"` with existing notes.

Evidence Confirm state semantics remain unchanged:

- unsupported/missing section/table/row identity stays fail-closed;
- row references remain proof-bearing only when source metadata admission and reference materialization pass.

## Implementation Decisions

### Field path matching

Add a small private helper in `data_extractor.py`, for example:

```python
def _anchors_for_family_field(
    family_result: FundFieldFamilyResult,
    field_name: str,
) -> tuple[EvidenceAnchor, ...]:
    ...
```

The helper should:

1. inspect `anchor.row_locator`;
2. parse only the `field=` key from semicolon-delimited Processor locators;
3. treat a locator as compatible when:
   - `field_path == field_name`; or
   - `field_path.startswith(f"{field_name}.")`;
4. preserve anchor order and dedupe behavior already present in family anchors;
5. ignore malformed or absent `field=` locators for field-specific matching;
6. return an empty tuple only when at least one recognized Processor `field=` locator exists in the family and none are compatible with `field_name`;
7. return `family_result.anchors` unchanged when no recognized Processor `field=` locator exists in the family.

The helper must not:

- parse `row`, `table_id`, `column` or `cell_id` as proof;
- validate row bounds;
- infer field identity from `note`, value text, section title or table headers;
- convert legacy locators into Processor locators.

### Legacy compatibility boundary

This gate targets FDD/Processor field-locator-capable family projection. Legacy extractor fields are already returned directly from the extractor path and should not be mutated in `data_extractor.py`.

`_field_from_family()` is shared by all `FundProcessorResult` projections, including processor paths that wrap legacy extractor output. If a family result has no recognized semicolon `field=` locator, A5 must preserve the existing anchor tuple. The fail-closed empty-anchor behavior applies only to field-locator-capable families where Processor `field=` anchors exist but none match the requested top-level field.

### R3 missing-section handling

R3 `missing_section=3` is not a row-locator problem if `_anchor_preflight_issue()` rejects the anchor before materialization. A5 no-live implementation must preserve this diagnostic and route it separately unless a deterministic local fixture proves the section id is produced incorrectly by projection code.

The next live authorization, if later granted, must capture safe diagnostic rows for every `missing_section` issue:

- sample id;
- anchor id;
- source field ids citing the anchor;
- section id;
- table id;
- row locator protocol class;
- issue reason.

No PDF text or proprietary excerpt should be added to the artifact beyond existing safe-summary rules.

## Implementation Slices

### A5-S0: No-live locator inventory diagnostic

Objective:

Add deterministic no-live tests or a private diagnostic helper that can classify projection-bound anchors for the target residual fields without loading live/PDF data.

Allowed changes:

- Add tests around existing processor FDD fixtures in `tests/fund/test_data_extractor.py`.
- If test assertions become unreadable, add one private helper in `data_extractor.py` or diagnostic module to classify anchor locator shapes.

Required assertions:

- A fixture with mixed `return_attribution.v1` FDD anchors reports processor field paths for `fee_schedule.*` and `nav_benchmark_performance.*`.
- A fixture with mixed `manager_profile.v1` FDD anchors reports processor field paths for `manager_alignment.*` or `manager_alignment` and `manager_strategy_text.*` or `manager_strategy_text`.
- A no-`field=` processor family fixture reports legacy/no-field-locator behavior and preserves current anchors.
- The diagnostic can distinguish:
  - `processor_field_locator`;
  - `semantic_locator_with_table`;
  - `semantic_locator_without_table`;
  - `no_row_locator`;
  - `unsupported_or_missing_field_locator`.
- No reference materialization or V2 result is changed by S0 alone.

Stop condition:

- If S0 shows the projection already has field-specific anchors and the failure is only table/section preflight, stop before A5-S1 and route to a table/section identity plan.

### A5-S1: Field-specific processor anchor adoption

Prerequisite:

S0 must show that field-locator-capable processor family anchors are being broadcast to top-level fields or that matching processor field locators are available but not selected.

Objective:

Change `_field_from_family()` so top-level bundle fields receive only anchors whose Processor `field=` path belongs to that field when, and only when, the family is field-locator-capable.

Allowed changes:

- Add `_anchors_for_family_field()`.
- Add `_processor_locator_field_path()` or equivalent small parser for `field=`.
- Update `_field_from_family()` to use field-specific anchors for non-missing family values.
- Add focused tests for:
  - `fee_schedule` receives only `fee_schedule.management_fee` / `fee_schedule.custody_fee` anchors;
  - `nav_benchmark_performance` receives only `nav_benchmark_performance.nav_growth_rate` / `nav_benchmark_performance.benchmark_return_rate` anchors;
  - `manager_alignment` receives only manager-alignment anchors;
  - `manager_strategy_text` receives only strategy/outlook anchors;
  - an available field in a field-locator-capable family with no compatible anchor gets empty anchors and is later projected as `evidence_missing`, not as proof-bearing unrelated evidence;
  - an available field in a no-`field=` processor family keeps the existing family anchors.

Non-goals:

- Do not modify Processor extraction selection logic.
- Do not add per-subvalue public facts.
- Do not rewrite Evidence Confirm materializer.
- Do not change legacy extractor locators.

Expected outcome:

Local tests prove projection no longer overbinds composite top-level facts to unrelated family anchors. A later explicitly authorized live/PDF re-evidence can then determine whether current R1-R4 runtime reaches A4 row materialization.

### A5-S2: R3 missing-section residual disposition

Objective:

Keep `missing_section=3` separate from locator adoption and prepare a safe diagnostic path for the next authorized live/PDF evidence.

Allowed changes:

- Add no-live unit coverage only if a deterministic fixture can reproduce a section id absent from `ParsedAnnualReport.sections`.
- Otherwise record the residual as requiring later live/PDF safe diagnostic authorization.

Non-goals:

- Do not normalize or guess section ids.
- Do not bypass `_anchor_preflight_issue()`.
- Do not downgrade missing sections to table/section excerpts.

Expected outcome:

R3 missing-section remains a fail-closed issue with an explicit owner and does not get hidden under value-match or row-materialization results.

## Tests and Validation

Required local validation after implementation:

```bash
uv run pytest tests/fund/test_data_extractor.py -q
uv run pytest tests/fund/test_evidence_confirm_sources.py -q
uv run ruff check fund_agent/fund/data_extractor.py tests/fund/test_data_extractor.py
git diff --check
```

If A5-S0 adds or changes a value diagnostics helper, also run:

```bash
uv run pytest tests/fund/test_evidence_confirm_value_diagnostics.py -q
uv run ruff check fund_agent/fund/evidence_confirm_value_diagnostics.py tests/fund/test_evidence_confirm_value_diagnostics.py
```

Expected assertions:

- No existing A4 materializer tests regress.
- Processor row locator parsing tests remain unchanged.
- Data extractor tests prove field-specific anchor assignment.
- No live/PDF, provider/LLM or product CLI command appears in the implementation evidence.

## Documentation Decision

Update `fund_agent/fund/README.md` only if code changes the current Fund package behavior:

- document that processor family projection selects field-compatible anchors instead of assigning the full family anchor set to every top-level field;
- state that row/table validity remains Evidence Confirm materializer responsibility;
- state that missing/unsupported section/table identity remains fail-closed.

Do not update root README, Host/Agent README or implementation-control docs until implementation/review/controller acceptance.

## Risks and Residuals

| Risk | Disposition |
| --- | --- |
| A5-S1 may make some FDD processor-projected fields expose empty anchors where they previously borrowed family anchors. | Intended fail-closed behavior only for field-locator-capable families; tests must prove no-`field=` processor families keep existing anchors. |
| Runtime may still produce `processor_row_locator_rows=0` after field-specific selection because current R1-R4 path uses legacy extractors or unsupported table ids. | Later live/PDF re-evidence must classify locator protocol and table/section preflight separately. |
| R3 `missing_section=3` may remain after locator adoption. | Separate residual; do not hide under coarse-reference closure. |
| Field matching by `field=` prefix could accidentally bind `field=fee_schedule_extra`. | Use exact equality or dot-prefix only. |
| Adding a public per-field anchor map would be cleaner long term but expands schema. | Out of scope for A5; keep private projection helper unless later evidence justifies schema gate. |

## Why This Is Not Overdesigned

The plan does not introduce a new public schema, repository path, parser dependency, service integration or generalized locator framework. It uses field identity already present in FDD Processor locators and changes only the projection point that currently has both `field_name` and `family_result.anchors`. It explicitly preserves no-`field=` processor families to avoid expanding the RR-09 fix into unrelated processor behavior. The diagnostic slice exists because A4 live evidence proved the previous assumed activation path was false.

## Completion Report Format

Implementation evidence must report:

- changed files;
- whether A5-S0 proved field-family anchor broadcast, table/section preflight, legacy-locator path, or another cause;
- exact tests/commands and pass/fail result;
- whether A5-S1 was executed or stopped by S0;
- residual disposition for R3 `missing_section=3`;
- explicit statement that no live/PDF, product CLI, provider/LLM, V2/ECQ/quality-gate semantic, release or tag action was run;
- final token:

```text
RR_09_A5_NO_LIVE_IMPLEMENTATION_EVIDENCE_READY_FOR_CODE_REVIEW_NOT_READY
```

## Controller Stop Condition

After plan review and any plan fix, stop at controller judgment unless the plan is accepted. Implementation must not start unless controller returns an explicit A5 no-live implementation-ready verdict.
