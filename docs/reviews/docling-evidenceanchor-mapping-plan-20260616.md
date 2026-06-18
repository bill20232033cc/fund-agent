# Docling EvidenceAnchor Mapping Plan - 2026-06-16

Gate: `Docling EvidenceAnchor Mapping Planning Gate`
Role: planning worker
Release/readiness: `NOT_READY`

## 1. Goal And Motivation

Define a code-generation-ready plan for mapping accepted candidate Docling document locators into the current `EvidenceAnchor` semantics without changing production behavior.

The immediate motivation is the accepted full-document coverage evidence: S1/S4/S5/S6 candidate Docling outputs have page/block/section/table/cell coverage signals sufficient to enter mapping planning, but table-cell anchors require parent-table context because the cell locator alone does not carry all EvidenceAnchor fields.

This plan is for candidate mapping only. It does not prove source truth, field correctness, production parser replacement, baseline promotion, release readiness, or PR readiness.

## 2. Non-goals And Guardrails

- Do not change `EvidenceAnchor` schema, `FundDocumentRepository`, source policy, parser behavior, Service, Host, UI, renderer, quality gate, CHAPTER_CONTRACT, or extractor facts.
- Do not introduce Docling as production source truth or production parser baseline.
- Do not use Docling Markdown/raw text/JSON directly as report facts; any future consumption must still pass through extractor/projection, `EvidenceAnchor`, and fail-closed classification.
- Do not add a production `source_kind` value in this gate. Candidate status must be carried by a candidate wrapper or `note`, not by silently extending the schema.
- Do not run live/network/EID/FDR/PDF/source acquisition, Docling conversion, provider/LLM, analyze/checklist/golden/readiness/release/PR commands.
- Preserve `release/readiness = NOT_READY`.
- Do not use unrelated untracked residue as evidence.

## 3. Evidence Inputs

| Input | Use In This Plan |
| --- | --- |
| `AGENTS.md` | Rule truth source, module boundaries, evidence guardrails |
| `docs/design.md` relevant EvidenceAnchor / FundDisclosureDocument / Docling sections | Current design truth for EvidenceAnchor fields, Fund documents boundary, candidate-only Docling status |
| `docs/implementation-control.md` front current-control section | Current gate, accepted artifacts, residuals, NOT_READY status |
| `docs/current-startup-packet.md` | Current active gate and startup guardrails |
| `docs/reviews/docling-full-document-coverage-evidence-controller-judgment-20260616.md` | Accepted coverage facts and next-gate constraint for parent table context |
| `docs/reviews/docling-full-document-coverage-evidence-20260616.md` | S1 vs S4/S5/S6 schema distinction and coverage matrix |
| `reports/docling-full-document-coverage/20260616/coverage-summary.json` | Machine-readable sample/page/block/table/cell coverage summary |

Accepted bounded input facts:

- S1 `004393 / 2025`, S4 `006597 / 2024`, S5 `017641 / 2024`, and S6 `110020 / 2024` are covered by the evidence matrix.
- S1 uses the current full representation schema with `pages` and `provenance_locator` objects.
- S4/S5/S6 use the runtime-containment lightweight schema where table-cell locator evidence is represented by `table_id + table.page_number + cell_index + row_start + column_start`.
- Heading locator, paragraph locator, table shape, table-cell locator, paragraph text, and cell text coverage are 100% for the measured candidate representation fields.
- These are coverage signals only; value correctness and source truth remain unproven.

## 4. Current EvidenceAnchor Fields And Constraints

Current design documents `EvidenceAnchor` as the extractor evidence anchor model with these fields:

| Field | Current Semantic Constraint |
| --- | --- |
| `source_kind` | Existing documented kinds are `annual_report`, `external_api`, and `derived`; this plan must not add production kinds. |
| `document_year` | Report year for annual-report evidence. Must come from accepted document identity, not from inferred text alone. |
| `section_id` | Annual-report section identifier or derived namespace such as `derived:nav`. For Docling annual-report candidates, use document section context only when deterministically available. |
| `page_number` | Source page number when the annual-report locator supplies it. For non-paged candidates such as future HTML render candidates, design already requires `page_number=null`; Docling PDF candidates should preserve page when available. |
| `table_id` | Annual-report table identifier when evidence comes from a table or cell. Must include parent table context for cells. |
| `row_locator` | Row, cell, or metric locator within the table/derived source. For text blocks without table context, leave unset and put block locator detail in `note`. |
| `note` | Human-readable provenance detail and candidate-only metadata that does not fit stable fields. Must not hide missing required locator fields. |

Constraints for this mapping gate:

- Mapping can produce candidate anchors for evidence comparison or future extractor projection only.
- A mapped candidate anchor must be traceable back to accepted document identity and locator fields.
- If a required field cannot be assigned deterministically, the candidate must be marked blocked/residual instead of fabricating an anchor.
- `note` may preserve extra locator detail, but it must not be the only carrier of table identity for table cells.

## 5. Candidate Docling Locator Source Fields

### 5.1 S1 Full Schema

Use S1 candidate fields as a richer locator source:

| Candidate Element | Locator Inputs To Use |
| --- | --- |
| Heading | `provenance_locator` object; page reference; heading text/path; nearest or declared section context |
| Paragraph | `provenance_locator` object; page reference; paragraph/block identity; section context |
| Table | table identity; page reference; table shape; table-level `provenance_locator`; section context |
| Cell | cell-level `provenance_locator` plus parent table identity, parent table page, row/column position, and available row/column header context |

The implementation worker must treat `provenance_locator` as candidate locator metadata, not as source truth. If a S1 cell has a cell locator but its parent table cannot be resolved, the mapping must stop for that cell.

### 5.2 S4/S5/S6 Lightweight Schema

Use S4/S5/S6 candidate fields as a lightweight locator source:

| Candidate Element | Locator Inputs To Use |
| --- | --- |
| Heading | heading locator coverage from the candidate object, page reference when present, heading text/path, section context |
| Paragraph | paragraph locator coverage from the candidate object, page reference when present, paragraph text/block identity, section context |
| Table | `table_id`, `table.page_number`, table shape, section context |
| Cell | `table_id`, parent `table.page_number`, `cell_index`, `row_start`, `column_start`, cell text, and any available row/column header context |

For S4/S5/S6 cells, `table_id + table.page_number + cell_index + row_start + column_start` is the minimum accepted locator tuple. `cell_index` alone is insufficient.

## 6. Parent-table Context Rule For Table Cells

Every table-cell EvidenceAnchor candidate must be built from a composite locator:

```text
document identity
+ section context
+ parent table identity
+ parent table page
+ cell row/column position
+ optional row/column header context
+ cell text/hash or normalized value marker
```

Required rule:

- A cell candidate cannot map to `EvidenceAnchor` without resolving its parent table.
- `table_id` must come from the parent table, not from a cell-local synthetic value.
- `page_number` for cells must come from the cell locator when explicit, otherwise from the parent table page. If neither exists, stop.
- `row_locator` must include cell position and should include row/column header path when available.
- `note` must preserve the original candidate locator fields used to construct the anchor, including schema family `S1_full` or `S4_S5_S6_lightweight`.

## 7. Proposed Mapping Rules

### 7.1 Common Preflight

For every candidate block:

1. Verify accepted document identity: sample id, fund code, document year, report type if available, and source JSON path from accepted evidence.
2. Verify candidate-only status and preserve `NOT_READY`.
3. Resolve block type: heading, paragraph, table, cell, or unsupported.
4. Resolve section context from declared section id, nearest section, or heading path.
5. If section context cannot be resolved, do not emit an EvidenceAnchor candidate for report-facing evidence; record `mapping_blocked: missing_section_context`.

### 7.2 `source_kind`

| Case | Mapping |
| --- | --- |
| Annual-report PDF candidate intended to project into current annual-report evidence semantics | Use canonical `source_kind="annual_report"` only inside candidate/projection evidence, not as production acceptance. |
| Candidate-only Docling provenance | Do not add `source_kind="docling"` or any new production kind in this gate. Preserve `candidate_source=docling` in wrapper metadata or `note`. |
| Future EID HTML render candidate | Keep separate; design requires `page_number=null` and candidate metadata in `note`. Do not mix HTML render semantics into this Docling PDF mapping slice. |
| Derived metric | Out of scope except to preserve existing `source_kind="derived"` behavior. |

### 7.3 `section_id`

Priority order:

1. Use explicit candidate section id if it is present and stable.
2. Else use nearest enclosing section from section hierarchy.
3. Else use normalized heading path only if the mapping can deterministically bind it to a section.
4. Else stop with `mapping_blocked: missing_section_context`.

Do not infer fund-analysis template chapter ids from arbitrary keywords during this mapping. Template chapter projection is a later extractor/CHAPTER_CONTRACT concern.

### 7.4 `page_number`

| Block Type | Rule |
| --- | --- |
| Heading | Use heading locator page. |
| Paragraph | Use paragraph locator page. |
| Table | Use table page. |
| Cell | Use cell page if explicit; otherwise parent table page; stop if neither is available. |
| No-page candidate | Stop for Docling PDF anchor mapping unless a future gate explicitly accepts a no-page PDF locator rule. |

### 7.5 `table_id`

| Block Type | Rule |
| --- | --- |
| Heading / paragraph | Leave unset. |
| Table | Use candidate table identity. |
| Cell | Use parent table identity. Stop if parent table identity is missing. |
| No-table text fact | Leave unset; use paragraph/heading provenance in `note`. |

### 7.6 `row_locator`

| Block Type | Rule |
| --- | --- |
| Heading | Leave unset; preserve heading path in `note`. |
| Paragraph | Leave unset unless a future schema gate accepts paragraph-specific row semantics. Preserve paragraph/block identity in `note`. |
| Table | Leave unset for table-level anchor, or use `table` / `table:<ordinal>` only for table-level evidence where no row is claimed. |
| Cell | Build from row/column position, e.g. `cell:r{row_start}:c{column_start}:idx{cell_index}`; append row/column header path when available. |
| Derived metric | Existing derived metric row locator rules are out of scope and must remain unchanged. |

### 7.7 `note`

`note` should be structured enough for future evidence review:

```text
candidate_source=docling;
schema_family=<S1_full|S4_S5_S6_lightweight>;
sample_id=<S1|S4|S5|S6>;
fund_code=<code>;
locator=<original candidate locator summary>;
text_hash_or_excerpt=<bounded marker when available>;
candidate_only=true;
field_correctness_status=not_proven
```

`note` must not be used to compensate for missing `section_id`, `page_number`, or parent `table_id` when those fields are required by the mapped block type.

## 8. Handling By Element Type

| Element Type | Mapping Behavior |
| --- | --- |
| Heading | Map to a candidate text anchor with `section_id` from the heading/section context, `page_number` from heading locator, `table_id=null`, `row_locator=null`, and heading path in `note`. Do not treat heading text as a field value without extractor projection. |
| Paragraph | Map to a candidate text anchor with section/page context and paragraph/block locator in `note`. No table fields. Paragraph evidence can support narrative/source section review only after future extractor projection. |
| Table | Map to a table-level candidate anchor with section/page/table context. Do not claim row or cell value correctness from table presence alone. |
| Cell | Map only with parent table context. Use parent `table_id`, page, row/column locator, and original cell locator metadata. Stop if parent table cannot be resolved. |
| No-table / no-cell text case | Use heading or paragraph rules. Leave table fields unset. |
| Table without cells | Table-level anchor may be emitted for representation coverage, but numeric/value extraction from that table must stop with `mapping_blocked: missing_cell_locator`. |
| Cell without table | Do not emit anchor. Record `mapping_blocked: missing_parent_table_context`. |
| Unsupported block | Do not emit anchor. Record `mapping_blocked: unsupported_block_type`. |

## 9. Future Evidence Gate Validation Matrix

Future validation must be no-live unless separately authorized by controller.

| Scenario | Required Check | Pass Condition | Stop Condition |
| --- | --- | --- | --- |
| S1 heading mapping | S1 heading locator to candidate anchor | `section_id` and `page_number` resolved; no table fields fabricated | Missing section/page |
| S1 paragraph mapping | S1 paragraph locator to candidate anchor | paragraph block has section/page and candidate metadata in `note` | Missing section/page |
| S1 table mapping | S1 table locator to table-level anchor | parent table id/page/section present | Missing table id/page/section |
| S1 cell mapping | S1 cell locator plus parent table context | composite table-plus-cell locator produces table_id/page/row_locator | Cell cannot resolve parent table |
| S4/S5/S6 lightweight cell mapping | `table_id + table.page_number + cell_index + row_start + column_start` | all minimum tuple fields present and represented in candidate anchor | Any tuple field missing |
| No-table paragraph evidence | paragraph-only candidate | table fields unset; locator detail in `note` | table fields invented |
| Table without cells | table candidate | table-level anchor only, no value claim | row/cell value emitted |
| Source kind handling | candidate Docling source | no new production `source_kind`; candidate status preserved | new production kind introduced without schema gate |
| Readiness guard | output artifact/status | explicit `candidate_only`, `not_source_truth`, `not_full_field_correctness`, `not_baseline_promotion`, `NOT_READY` | readiness or baseline claim |

Suggested future local validation commands must be defined by the next implementation/evidence gate. This planning gate only authorizes Markdown validation for this artifact.

## 10. Stop Conditions

Stop and return to controller if any of these occur:

- Required mapping needs a schema change to `EvidenceAnchor`.
- Candidate source kind cannot be represented without inventing a new production `source_kind`.
- Cell mapping cannot retain parent table context.
- Section context cannot be deterministically resolved.
- Page number is absent for Docling PDF evidence and no accepted no-page rule exists.
- Implementation would require production parser replacement, FDR/source behavior change, Service/Host/UI/renderer/quality-gate changes, live/source acquisition, provider/LLM, or readiness/release work.
- Evidence workers try to use untracked or unaccepted residue as proof.

## 11. Review Focus

AgentDS should review:

- Whether the mapping rules preserve current `EvidenceAnchor` semantics without schema drift.
- Whether the parent-table context rule is sufficient for table-cell anchors.
- Whether stop conditions prevent fabricated `section_id`, `page_number`, `table_id`, or `row_locator`.
- Whether future validation can catch cell-only, table-without-cell, and no-section cases.

AgentMiMo should review:

- Whether the plan maintains Fund documents containment and does not leak Docling into Service/Host/UI/renderer/quality gate.
- Whether `source_kind` handling avoids implicit production enum expansion.
- Whether candidate-only, not-source-truth, not-full-field-correctness, not-baseline-promotion, and `NOT_READY` guardrails are explicit enough.
- Whether the next gate boundary is narrow enough for no-live implementation planning.

## 12. Exact Next Gate Recommendation

Immediate next gate:

```text
Docling EvidenceAnchor Mapping Plan Review Gate
```

Scope:

- DS and MiMo scoped reviews of this plan.
- Controller judgment on whether the plan is ready for a separate no-live implementation planning gate.
- No code changes, no tests/runtime behavior changes, no Docling conversion, no live/source acquisition, no provider/LLM/analyze/checklist/golden/readiness/release/PR commands.

If accepted by controller, the following gate should be:

```text
Docling EvidenceAnchor Mapping No-live Implementation Planning Gate
```

## 13. Final Verdict

```text
VERDICT: PLAN_READY_FOR_DS_MIMO_REVIEW_NOT_READY
```
