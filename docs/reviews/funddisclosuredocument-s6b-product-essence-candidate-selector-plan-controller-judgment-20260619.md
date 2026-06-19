# FundDisclosureDocument S6-B Product Essence Candidate Selector Plan Controller Judgment

## Verdict

`ACCEPT_S6B_PRODUCT_ESSENCE_CANDIDATE_SELECTOR_PLAN_WITH_AMENDMENTS_READY_FOR_IMPLEMENTATION_NOT_READY`

## Reviewed Artifacts

- Plan: `docs/reviews/funddisclosuredocument-s6b-product-essence-candidate-selector-plan-20260619.md`
- Plan review: `docs/reviews/plan-review-20260619-085123.md`

## Judgment

The S6-B product essence candidate selector plan is accepted with binding amendments.

Accepted scope:

- exactly one field family: `product_essence.v1`;
- candidate evidence only;
- `status="missing"`, `extraction_mode="missing"`, `value={}`, `anchors=()`;
- local gap `candidate_only_not_source_truth` when candidate evidence is present;
- no facade projection, public anchor, partial/accepted status, source truth, parser replacement, readiness or release.

## Binding Amendments

### A. Stable source_field_path format

Implementation must use these exact path formats:

- section records: `sections[{index}]`
- paragraph records: `paragraph_blocks[{index}]`
- table records: `table_blocks[{index}]`
- cell records: `table_blocks[{table_index}].cells[{cell_index}]`

Tests must assert exact path strings for at least section, table and cell candidate evidence.

### B. Implementation gate name

The next gate is:

`FundDisclosureDocument S6-B Product Essence Candidate Selector Implementation Gate`

The plan text's `S6-C` implementation wording is superseded by this controller amendment. `S6-C` remains unused.

### C. Evidence role encoding

S6-B may encode the matched role in `row_locator` as a stable prefix:

`role=<role>; locator=<human-readable locator>`

It must not add new fields to `FundCandidateEvidenceRecord` in this gate.

## Next Entry Point

`FundDisclosureDocument S6-B Product Essence Candidate Selector Implementation Gate`

Release/readiness remains `NOT_READY`.
