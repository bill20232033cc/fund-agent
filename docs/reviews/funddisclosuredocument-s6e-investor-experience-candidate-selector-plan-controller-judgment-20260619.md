# Controller Judgment: S6-E Investor Experience Candidate Selector Plan

## Gate

- Gate: `FundDisclosureDocument S6-E Single-family Candidate Evidence Selector Planning Gate`
- Classification: `heavy planning gate`
- Work unit type: feature slice inside the Fund Processor/Extractor route

## Inputs Reviewed

- Plan: `docs/reviews/funddisclosuredocument-s6e-investor-experience-candidate-selector-plan-20260619.md`
- DS boundary plan review: `docs/reviews/plan-review-20260619-121210.md`
- MiMo plan review: `docs/reviews/plan-review-20260619-121354.md`
- Current control truth: `docs/implementation-control.md`
- Startup packet: `docs/current-startup-packet.md`
- Design truth: `docs/design.md` v2.25
- Current processor/test code:
  - `fund_agent/fund/processors/fund_disclosure_processor.py`
  - `tests/fund/processors/test_fund_disclosure_processor.py`
  - `fund_agent/fund/processors/active_annual.py`

## Decision

`ACCEPT_S6E_INVESTOR_EXPERIENCE_CANDIDATE_SELECTOR_PLAN_WITH_BINDING_AMENDMENTS_NOT_READY`

The S6-E plan is accepted for implementation with binding amendments. It selects exactly one remaining field family, `investor_experience.v1`, and keeps the implementation surface inside the Fund Processor/Extractor boundary as a candidate-only locator selector.

The accepted implementation gate must not implement `current_stage.v1` or `core_risk.v1`, must not change public contracts, and must not claim source truth, parser replacement, field correctness, readiness, release, or upper-layer consumption.

## Accepted Scope

The next implementation gate may:

- add a deterministic `investor_experience.v1` candidate locator selector;
- read only `FundDisclosureDocumentContentIntermediate` section, paragraph, table, and cell protocol fields;
- attach results only to `FundFieldFamilyResult.candidate_evidence`;
- keep `investor_experience.v1` public status as `missing`;
- keep `value={}` and `anchors=()`;
- update focused processor tests and sync `fund_agent/fund/README.md` / `docs/design.md` current-state wording after code facts exist.

## Binding Amendments

### A1. Subscription/Redemption Guard Must Avoid Self-guard

The implementation must not allow `subscription_redemption` generic tokens such as `申购`, `赎回`, `净申购`, and `净赎回` to pass solely because the same cell text also contains `份额` or `基金份额`.

For `subscription_redemption`:

- Strong tokens may match directly when they are specific actual-flow locators, such as `基金总申购份额`, `基金总赎回份额`, `总申购份额`, `总赎回份额`, `本期申购`, `本期赎回`, and `申购赎回`.
- Generic tokens require source-level guard context.
- Standalone `份额` and standalone `基金份额` are not sufficient guard tokens for generic `subscription_redemption`.
- Accepted guard context tokens are narrower actual-flow or share-change context tokens, such as `份额变动`, `基金份额变动`, `基金份额总额变动`, `基金总申购`, `基金总赎回`, `总申购份额`, `总赎回份额`, and `申购赎回`.
- For cell records, generic guard context must exclude `cell_text_normalized` and `cell_text`; it may use parent table `heading_text`, parent table `table_caption_or_nearby_heading`, parent table `heading_path`, cell `row_label_path`, cell `column_header_path`, and cell `heading_path`.

The implementation test set must add a negative case where a cell or paragraph such as `申购份额` / `申购份额的计算方式` appears under unrelated or fee-style context and must not produce `subscription_redemption` candidate evidence.

### A2. Income-distribution Guard And Dedupe

`income_distribution` remains accepted as a Chapter 4 investor-experience locator role even though it is not an independent current `ActiveFundAnnualProcessor` public field.

Implementation must keep it candidate-only and must not add a new public field. Dedupe may remain family-local by exact `source_field_path`; if a single source path matches multiple roles, first-record-wins is acceptable for this slice because the candidate source remains present in the same field family and no public value is produced.

The residual risk is that `income_distribution` role labels may be suppressed by earlier role order on the same source path. This is accepted as non-blocking for S6-E and should be carried to future field-extraction/source-truth design.

### A3. Helper Refactor Boundary

The implementation must not refactor existing S6-B/S6-C/S6-D traversal helpers or selector semantics as part of S6-E.

Allowed implementation strategies:

- add S6-E-local private helper functions; or
- add narrowly shared helpers only if existing S6-B/S6-C/S6-D code paths are not rewritten.

Any cross-family helper extraction that rewrites existing selectors is deferred to a separate cleanup/refactor gate. Existing S6-B/S6-C/S6-D tests must remain regression coverage, not a license to perform a broad refactor in this implementation gate.

### A4. Existing Regression Test Updates

MiMo finding 1 is rejected as a blocker because the cited tests use `_stub()`, which is `FundDisclosureDocumentIntermediate` only, not `_ContentIntermediateStub`, and therefore does not enter candidate selector logic. The existing assertions in `test_extract_admits_candidate_boundary_but_returns_blocked` and `test_extract_satisfied_returns_fully_gapped_result` should remain unchanged unless the implementation intentionally changes their input type, which is not authorized.

If any existing test expectation is updated, the implementation evidence must identify the exact test and explain why the input is content-bearing and newly eligible for S6-E candidate evidence.

## Plan Review Finding Disposition

### DS F1: cell-level generic token self-guard

- Disposition: `accepted`
- Controller action: resolved by binding amendment A1.
- Reason: cell self-text as both match and guard can make the guard meaningless for broad `申购` / `赎回` tokens and can fill the 16-record limit with low-value cells.

### DS F2: `subscription_redemption` guard token `份额` is too broad

- Disposition: `accepted`
- Controller action: resolved by binding amendment A1.
- Reason: standalone `份额` / `基金份额` is too common and does not distinguish actual申购赎回发生额 from fee, calculation, or generic share-class text.

### DS F3: `income_distribution` lacks independent field mapping

- Disposition: `accepted as residual risk`
- Controller action: binding amendment A2 keeps the role candidate-only and accepts first-record-wins by path for this slice.
- Reason: the source remains available inside `investor_experience.v1`; role-label precision is a later field-extraction/source-truth concern.

### DS F4 and MiMo F2: helper refactor boundary

- Disposition: `accepted`
- Controller action: resolved by binding amendment A3.
- Reason: S6-E should not combine feature implementation with cross-family traversal refactor.

### MiMo F1: current regression tests require unspecified updates

- Disposition: `rejected-with-reason`
- Reason: the cited tests call `_stub()`, not `_ContentIntermediateStub`, and current selector logic only runs for content-bearing intermediates. The finding's premise is factually incorrect for those tests.

### MiMo F3: income-distribution strong/guard overlap

- Disposition: `deferred-with-owner`
- Owner: future field-extraction/source-truth design
- Reason: the redundancy does not violate candidate-only locator semantics and does not block implementation.

## Required Validation For Next Gate

```bash
uv run pytest tests/fund/processors/test_fund_disclosure_processor.py
uv run ruff check fund_agent/fund/processors/fund_disclosure_processor.py tests/fund/processors/test_fund_disclosure_processor.py
git diff --check
```

If docs are updated:

```bash
git diff --check -- fund_agent/fund/README.md docs/design.md
```

## Explicit Non-Readiness

This accepted plan does not prove source truth, field correctness, parser replacement, full coverage, golden/readiness, release, PR readiness, or upper-layer consumption. Release/readiness remains `NOT_READY`.

## Next Entry Point

`FundDisclosureDocument S6-E Investor Experience Candidate Selector Implementation Gate`
