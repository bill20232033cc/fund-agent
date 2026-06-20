# FundDisclosureDocument investor_experience.v1 Source-truth Direct Extraction Fix Evidence

## Metadata

- Role: AgentCodex fix worker only
- Gate: Code Review Fix Gate
- Work unit: FundDisclosureDocument investor_experience.v1 Source-truth Direct Extraction
- Accepted finding: `docs/reviews/code-review-investor-experience-source-truth-mimo-20260620.md` F1 LOW
- Branch: `funddisclosure-investor-experience-source-truth`
- Date: 2026-06-20

## Scope

Allowed files for this fix gate:

- `tests/fund/processors/test_fund_disclosure_processor.py`
- `docs/reviews/funddisclosuredocument-investor-experience-source-truth-extraction-fix-evidence-20260620.md`

Files changed by this fix gate:

- `tests/fund/processors/test_fund_disclosure_processor.py`
- `docs/reviews/funddisclosuredocument-investor-experience-source-truth-extraction-fix-evidence-20260620.md`

No production code, `docs/design.md`, README, data_extractor tests, control docs, PR state, commits, or push were touched by this fix gate.

## Fix

Added focused test:

- `test_investor_experience_source_truth_share_change_selects_single_value_column`

The test constructs a share-change table with:

- one label column;
- one valid value column whose header is not the fund code;
- beginning and ending share rows only.

Expected behavior asserted:

- `share_change` is extracted from the sole value column;
- `net_change` is calculated as `250.00`;
- `share_class_column` remains the non-fund-code header `报告期份额`;
- `share_class_selection_reason` is exactly `single_value_column`.

This directly closes F1 without changing production extraction behavior.

## Validation

### Targeted test

Command:

```bash
uv run pytest tests/fund/processors/test_fund_disclosure_processor.py -k investor_experience_source_truth_share_change_selects_single_value_column
```

Result:

```text
collected 175 items / 174 deselected / 1 selected
tests/fund/processors/test_fund_disclosure_processor.py .                [100%]
1 passed, 174 deselected in 0.98s
```

### Full processor test file

Command:

```bash
uv run pytest tests/fund/processors/test_fund_disclosure_processor.py
```

Result:

```text
collected 175 items
tests/fund/processors/test_fund_disclosure_processor.py ................ [  9%]
........................................................................ [ 50%]
........................................................................ [ 91%]
...............                                                          [100%]
175 passed in 0.49s
```

### Ruff

Command:

```bash
uv run ruff check tests/fund/processors/test_fund_disclosure_processor.py
```

Result:

```text
All checks passed!
```

### Whitespace

Command:

```bash
git diff --check
```

Result:

```text
Passed with no output.
```

## Residual Risks

- F1 status: fixed in current fix gate.
- Production source-truth behavior: unchanged by this fix gate.
- Broader investor_experience source-truth correctness: remains covered by the existing implementation/code-review gate artifacts; not re-reviewed in this fix-only gate.
- Repository dirty state: unrelated pre-existing modified/untracked files remain outside this fix gate scope.

## Completion Status

`FIX_COMPLETE_VALIDATED`

Artifact path:

`docs/reviews/funddisclosuredocument-investor-experience-source-truth-extraction-fix-evidence-20260620.md`
