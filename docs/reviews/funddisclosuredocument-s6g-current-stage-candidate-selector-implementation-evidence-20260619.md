# FundDisclosureDocument S6-G Current Stage Candidate Selector Implementation Evidence

## Gate / Role

- Gate: `FundDisclosureDocument S6-G Current Stage Candidate Selector Implementation Gate`
- Worker role: AgentCodex implementation worker only
- Accepted plan: `docs/reviews/funddisclosuredocument-s6g-current-stage-candidate-selector-plan-20260619.md`
- Controller judgment: `docs/reviews/funddisclosuredocument-s6g-current-stage-candidate-selector-plan-controller-judgment-20260619.md`

## Changed Files

- `fund_agent/fund/processors/fund_disclosure_processor.py`
- `tests/fund/processors/test_fund_disclosure_processor.py`
- `fund_agent/fund/README.md`
- `docs/design.md`
- `docs/reviews/funddisclosuredocument-s6g-current-stage-candidate-selector-implementation-evidence-20260619.md`

## Contract Summary

- Implemented exactly one selector: `current_stage.v1`.
- Added `_CURRENT_STAGE_CANDIDATE_LIMIT = 16`.
- Added `current_stage.v1` candidate evidence to `_field_families_for_intermediate()` mapping style without restoring nested conditional logic.
- Selector role order is:
  1. `stage_status`
  2. `manager_change`
  3. `share_scale_change`
  4. `holding_strategy_change`
- Source order inside each role is: `sections`, `paragraph_blocks`, `table_blocks`, `table_cells`.
- Dedupe is family-local by exact `source_field_path`; there is no cross-family dedupe.
- Cell scan order is sorted by `(row_index, column_index)` while `source_field_path` preserves the original tuple index.
- Row locator schema follows the accepted plan:
  - section: `role={role}; locator=section_id={section.section_id}`
  - paragraph: `role={role}; locator=block_id={paragraph.block_id}`
  - table: `role={role}; locator=table_id={table.table_id}`
  - cell: `role={role}; locator=table_id={cell.table_id}; row={cell.row_index}; column={cell.column_index}`
- `_current_stage_cell_guard_context()` is role-invariant and uses only `table.heading_text`, `table.table_caption_or_nearby_heading`, `*table.heading_path`, `*cell.row_label_path`, `*cell.column_header_path`, `*cell.heading_path`. It excludes `cell_text` and `cell_text_normalized`.
- Public `current_stage.v1` result remains fail-closed:
  - `status="missing"`
  - `extraction_mode="missing"`
  - `value={}`
  - `anchors=()`
  - candidate records are only stored in `FundFieldFamilyResult.candidate_evidence`.
- S6-B/S6-C/S6-D/S6-E/S6-F selector traversal, row locators, limits, source paths, gaps, public values and public anchors were not intentionally changed.

## Test Coverage Added

- Positive role coverage for `stage_status`, `manager_change`, `share_scale_change`, and `holding_strategy_change`.
- Public value/anchor leak prevention and candidate boundary field assertions.
- No-match `field_family_missing` behavior.
- Candidate-boundary input remains result-level `contract_status="blocked"`.
- Order/dedupe/limit/excerpt/cell tuple-index path behavior.
- Generic guard negative and positive behavior.
- Cell self-guard blocking while allowing strong cell token matches.
- Chapter 5 reasoning/output token blocking, including pure forbidden and forbidden-plus-legal mixed content.
- Chapter 6/S6-F risk-token non-capture.
- Market/valuation external-token non-capture.
- Product identity-only, manager biography-only, investor-experience-only and return/fee-only overlap non-capture.
- Comparative overlap regression with baseline S6-E `share_change` strong-token content, verifying S6-B/S6-C/S6-D/S6-E/S6-F record count, source path order, gap code, public value and public anchors are unchanged; S6-E share_change signature is unchanged.
- Existing admission and forbidden-boundary tests continue passing.

## Validation Commands / Results

```bash
uv run pytest tests/fund/processors/test_fund_disclosure_processor.py
```

Result: passed, `95 passed in 0.78s`.

```bash
uv run ruff check fund_agent/fund/processors/fund_disclosure_processor.py tests/fund/processors/test_fund_disclosure_processor.py
```

Result: passed, `All checks passed!`.

```bash
git diff --check
```

Result: passed, no output.

```bash
git diff --check -- fund_agent/fund/README.md docs/design.md
```

Result: passed, no output.

## Docs Decision

- `fund_agent/fund/README.md` was updated to describe S6-G `current_stage.v1` as current FundDisclosureDocument candidate locator behavior.
- `docs/design.md` was updated from v2.27 to v2.28 and now records S6-G as current design fact.
- Both docs preserve candidate-only / not_proven / NOT_READY wording and do not claim source truth, field correctness, parser replacement, readiness, release, Chapter 5 conclusion quality or upper-layer consumption.
- `docs/implementation-control.md` and `docs/current-startup-packet.md` were not edited by this implementation worker.

## Residual Risks

- Token-based false positives remain possible. Owner/destination: later field-extraction/source-truth evidence gate; current public family remains `missing`.
- Fee-adjustment current-stage evidence remains under-covered because fee tokens stay S6-C-owned in this gate. Owner/destination: later Chapter 5 field-family mapping gate if required.
- Market environment changes remain under-covered because market forecast and valuation external-truth tokens are forbidden. Owner/destination: later Chapter 5 analysis/evidence design gate.
- Candidate excerpts may contain numeric-looking text, but tests assert this does not leak to public `value` or `anchors`. Owner/destination: later source-truth/readiness gates.
- No repository-loaded PDF, live/network, FDR, Docling conversion, pdfplumber export, provider, LLM or manual source comparison was run. Owner/destination: deferred source-truth/readiness gates.

## Boundary Statement

`current_stage.v1` evidence remains internal `candidate_only` / `not_proven` / `not_ready` locator evidence only. It is not source truth, not field correctness, not parser replacement, not Chapter 5 final conclusion, not upper-layer consumption and not release/readiness evidence. Project release/readiness remains `NOT_READY`.
