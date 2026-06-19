# Controller Judgment: S6-D Manager Profile Candidate Selector Plan

## Gate

- Gate: `FundDisclosureDocument S6-D Single-family Candidate Evidence Selector Planning Gate`
- Classification: `heavy planning gate`
- Work unit type: feature slice inside the Fund Processor/Extractor route.

## Inputs Reviewed

- Plan: `docs/reviews/funddisclosuredocument-s6d-manager-profile-candidate-selector-plan-20260619.md`
- MiMo plan review: `docs/reviews/plan-review-20260619-110420.md`
- DS boundary plan review: `docs/reviews/plan-review-20260619-110824.md`
- Current control truth: `docs/implementation-control.md`
- Startup packet: `docs/current-startup-packet.md`
- Design truth: `docs/design.md` v2.24
- Accepted S6-C implementation judgment: `docs/reviews/funddisclosuredocument-s6c-return-attribution-candidate-selector-implementation-controller-judgment-20260619.md`

## Decision

`ACCEPT_S6D_MANAGER_PROFILE_CANDIDATE_SELECTOR_PLAN_WITH_BINDING_AMENDMENTS_NOT_READY`

The S6-D plan is accepted for implementation with binding amendments. It selects exactly one remaining field family, `manager_profile.v1`, and keeps the implementation surface inside the Fund Processor/Extractor boundary as a candidate-only locator selector.

The DS material findings are accepted. They are resolved by the binding amendments below and must be treated as implementation contract.

## Accepted Scope

The next implementation gate may:

- add a deterministic `manager_profile.v1` candidate locator selector;
- read only `FundDisclosureDocumentContentIntermediate` section, paragraph, table, and cell protocol fields;
- attach results only to `FundFieldFamilyResult.candidate_evidence`;
- keep `manager_profile.v1` public status as `missing`;
- keep `value={}` and `anchors=()`;
- add focused processor tests and update `fund_agent/fund/README.md` / `docs/design.md` current-state wording after code facts exist.

## Binding Amendments

### A1. Generic Guard Mechanics

Implementation must treat manager-profile generic-token guards as source-level predicates applied after a role token matches and before appending a candidate record.

For `portfolio_managers`:

- Strong tokens such as `基金经理简介`, `基金管理人及基金经理情况`, `基金经理情况`, and `主要人员情况` do not require extra context.
- Generic roster tokens such as `姓名`, `职务`, `职责`, `岗位`, `任职日期`, `任职时间`, `聘任日期`, `起始日期`, `离任日期`, `离任时间`, and `终止日期` require guard context containing `基金经理` or `管理人`.
- Guard context by source type:
  - section record: section `heading_text_normalized`, `heading_text_raw`, and `heading_path`;
  - paragraph record: paragraph `heading_path`;
  - table record: table `heading_text`, `table_caption_or_nearby_heading`, and `heading_path`;
  - cell record: parent table `heading_text`, parent table `table_caption_or_nearby_heading`, parent table `heading_path`, and cell `heading_path`.
- A table-level or cell-level generic token may pass if the parent table heading/caption/path supplies the required context.

For `manager_alignment`:

- Strong tokens such as `基金经理持有本基金`, `基金经理持有份额`, `本基金基金经理持有本开放式基金`, `基金管理人所有从业人员持有本基金`, and `从业人员持有本基金` do not require extra context.
- Generic holding tokens such as `基金经理持有`, `从业人员持有`, and `持有本基金` require guard context containing `基金经理`, `从业人员`, or `基金管理人`.
- Guard context by source type:
  - section record: section heading fields and heading path;
  - paragraph record: paragraph `text_normalized`, `text_raw`, and `heading_path`;
  - table record: table heading, caption, and heading path;
  - cell record: parent table heading, parent table caption, parent table heading path, cell text, row labels, column headers, and cell heading path.

For `manager_strategy_text`, `turnover_rate`, and `holdings_snapshot`, implementation must not add broad standalone interpretive tokens beyond the accepted plan tokens.

### A2. Required Positive Guard Test

The S6-D implementation test set must add a positive counterpart to the generic-token negative test:

- `test_manager_profile_selector_allows_generic_tokens_with_context`

This test must prove at least:

- a parent table or section with `基金经理` / `管理人` context plus generic roster labels such as `姓名` / `职务` / `任职日期` produces `manager_profile.v1` candidate evidence;
- a paragraph or table/cell context with `基金经理` / `从业人员` / `基金管理人` plus generic holding text such as `持有本基金` produces `manager_profile.v1` candidate evidence;
- public `value` and `anchors` remain empty.

### A3. Residual Risk Tracking

The following DS observations are accepted as residual risks, not implementation blockers:

- `持仓集中度` may look evaluative but is allowed only as a locator token; implementation must not infer concentration or style.
- `turnover_rate` remains negative-guarded rather than positive-context guarded; false positives are bounded by candidate-only status and must not become public facts.

## Plan Review Finding Disposition

### DS MF1 Generic guard specification is not implementation-ready

- Disposition: `accepted`
- Controller action: resolved by binding amendment A1.
- Reason: without field-level guard mechanics, implementation would have to invent guard scope and order. A1 now defines source-level guard context and append-time filtering.

### DS MF2 Missing positive test for context-dependent generic token guards

- Disposition: `accepted`
- Controller action: resolved by binding amendment A2.
- Reason: a negative-only guard test can hide over-aggressive implementations. A2 requires positive guard coverage.

### MiMo residual risks

- Disposition: `accepted as residual risks`
- Controller action: carry into implementation gate validation and future selector planning.

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

This accepted plan does not prove source truth, field correctness, parser replacement, full coverage, golden/readiness, release, or upper-layer consumption. Release/readiness remains `NOT_READY`.

## Next Entry Point

`FundDisclosureDocument S6-D Manager Profile Candidate Selector Implementation Gate`
