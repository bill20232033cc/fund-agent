# FundDisclosureDocument S6-D Manager Profile Candidate Selector Implementation Evidence

## Gate

- Gate: `FundDisclosureDocument S6-D Manager Profile Candidate Selector Implementation Gate`
- Role: implementation worker only
- Scope: implement exactly one new field-family selector, `manager_profile.v1`
- Status: implementation completed; review, commit, push, PR, merge and next gate were not performed

## Changed Files

- `fund_agent/fund/processors/fund_disclosure_processor.py`
- `tests/fund/processors/test_fund_disclosure_processor.py`
- `fund_agent/fund/README.md`
- `docs/design.md`
- `docs/reviews/funddisclosuredocument-s6d-manager-profile-candidate-selector-implementation-evidence-20260619.md`

## Behavior Summary

- Added `_MANAGER_PROFILE_CANDIDATE_LIMIT = 16`.
- Added deterministic `manager_profile.v1` candidate-only locator selector inside `FundDisclosureDocumentProcessor`.
- Selector scans roles in accepted order: `portfolio_managers`, `manager_strategy_text`, `turnover_rate`, `manager_alignment`, `holdings_snapshot`.
- Selector scans source types in accepted order: sections, paragraph blocks, table blocks, table cells.
- Source paths remain stable:
  - `sections[{section_index}]`
  - `paragraph_blocks[{paragraph_index}]`
  - `table_blocks[{table_index}]`
  - `table_blocks[{table_index}].cells[{cell_index}]`
- Cell scan order sorts by `(row_index, column_index)` while preserving original tuple index in `source_field_path`.
- Dedupe is family-local by exact `source_field_path`; no cross-family dedupe was added.
- Candidate excerpts use the existing `_CANDIDATE_EXCERPT_LIMIT = 160`.
- `manager_profile.v1` with candidate evidence returns `candidate_only_not_source_truth` local gap while public status remains missing.
- `manager_profile.v1` without candidate evidence remains `field_family_missing`.

## Controller Amendments Fulfilled

- Generic guard mechanics are source-level predicates applied after role token match and before appending a candidate record.
- `portfolio_managers` strong tokens require no extra context.
- `portfolio_managers` generic roster tokens require guard context containing `基金经理` or `管理人`.
- `portfolio_managers` guard context follows source type:
  - section: heading normalized/raw/path
  - paragraph: heading path only
  - table: heading, caption, path
  - cell: parent table heading/caption/path plus cell heading path
- `manager_alignment` strong tokens require no extra context.
- `manager_alignment` generic holding tokens require guard context containing `基金经理`, `从业人员`, or `基金管理人`.
- `manager_alignment` guard context follows source type:
  - section: heading normalized/raw/path
  - paragraph: text normalized/raw plus heading path
  - table: heading, caption, path
  - cell: parent table heading/caption/path plus cell text, row labels, column headers and cell heading path
- `manager_strategy_text`, `turnover_rate`, and `holdings_snapshot` did not receive broad standalone interpretive tokens beyond the accepted plan.
- Added `test_manager_profile_selector_allows_generic_tokens_with_context`, proving guarded generic roster and holding tokens can produce candidate evidence while public `value` and `anchors` remain empty.

## Candidate-only / NOT_READY Statement

- Candidate evidence is stored only in `FundFieldFamilyResult.candidate_evidence`.
- `manager_profile.v1` public output remains `status="missing"`, `extraction_mode="missing"`, `value={}`, and `anchors=()`.
- Candidate records remain `candidate_only=True`, `source_boundary="candidate_only"`, `field_correctness_status="not_proven"`, `source_truth_status="not_proven"`, `parser_replacement_authorized=False`, and `readiness_status="not_ready"`.
- No public `EvidenceAnchor` was created.
- No `partial`, `accepted`, `satisfied`, `direct`, `derived`, or `estimated` state was introduced by candidate evidence.
- This implementation does not prove source truth, field correctness, parser replacement, full coverage, golden/readiness, release, or upper-layer consumption.
- Release/readiness remains `NOT_READY`.

## Validation Commands And Results

```bash
uv run pytest tests/fund/processors/test_fund_disclosure_processor.py
```

Result: exit code 0; `56 passed in 0.78s`.

```bash
uv run ruff check fund_agent/fund/processors/fund_disclosure_processor.py tests/fund/processors/test_fund_disclosure_processor.py
```

Result: exit code 0; `All checks passed!`.

```bash
git diff --check
```

Result: exit code 0; no output.

```bash
git diff --check -- fund_agent/fund/README.md docs/design.md
```

Result: exit code 0; no output.

## Stop Condition

Implementation, focused tests, docs sync and this evidence artifact are complete. No staging, commit, push, PR, merge, review, cleanup of unrelated residuals, or next gate action was performed.
