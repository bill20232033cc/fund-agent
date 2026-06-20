# Code Re-Review: FundDisclosureDocument investor_experience.v1 Source-truth Direct Extraction

## Scope

- Mode: targeted re-review (fix gate confirmation)
- Branch: `funddisclosure-investor-experience-source-truth`
- Base: `1bf4187` (accepted plan)
- Prior review: `docs/reviews/code-review-investor-experience-source-truth-mimo-20260620.md`
- Target finding: F1 LOW — missing dedicated `share_change_selects_single_value_column` test
- Fix evidence: `docs/reviews/funddisclosuredocument-investor-experience-source-truth-extraction-fix-evidence-20260620.md`
- Review target: diff since prior code review, especially `tests/fund/processors/test_fund_disclosure_processor.py` and fix evidence artifact
- Output file: `docs/reviews/code-rereview-investor-experience-source-truth-mimo-20260620.md`
- Included scope: fix evidence artifact, test file diff, validation results
- Excluded scope: production code, docs/design.md, README, data_extractor tests, control docs, PR state, commits, push

## Scope Compliance

Fix gate allowed files:

| File | Allowed | Actual |
|---|---|---|
| `tests/fund/processors/test_fund_disclosure_processor.py` | Yes | Yes |
| `docs/reviews/funddisclosuredocument-investor-experience-source-truth-extraction-fix-evidence-20260620.md` | Yes | Yes |

Files NOT touched by this fix gate (pre-existing implementation diff only):

- `fund_agent/fund/processors/fund_disclosure_processor.py` — pre-existing diff, no new changes from fix gate
- `docs/design.md` — pre-existing diff, no new changes from fix gate
- `fund_agent/fund/README.md` — pre-existing diff, no new changes from fix gate
- `tests/fund/test_data_extractor.py` — pre-existing diff, no new changes from fix gate

No production code, docs/design.md, README, data_extractor tests, control docs, PR state, commits, or push were touched by this fix gate.

## F1 Fix Confirmation

### Finding F1 [LOW] — Missing dedicated `share_change_selects_single_value_column` test

**Status: FIXED**

Added test: `test_investor_experience_source_truth_share_change_selects_single_value_column`

Test constructs a share-change table with:
- one label column (column_index=0, row_label "项目");
- one value column whose header is `"报告期份额"` (not a fund code);
- beginning share row: `"1,000.00"`;
- ending share row: `"1,250.00"`.

Assertions:
- `beginning_share` == `"1,000.00"` ✓
- `ending_share` == `"1,250.00"` ✓
- `net_change` == `"250.00"` (Decimal calculation) ✓
- `share_class_column` == `"报告期份额"` (non-fund-code header) ✓
- `share_class_selection_reason` == `"single_value_column"` ✓

This directly and independently proves the single-value-column selection path without relying on `test_..._share_change_excludes_label_column` as implicit coverage.

Supporting helpers also added:
- `_investor_experience_source_truth_result()` — convenience wrapper for processor extract
- `_investor_paragraph()` — investor paragraph fixture builder
- `_investor_cell()` — investor cell fixture builder with configurable `column_header_path`

These helpers are shared by the full investor_experience test suite (17 tests total), which is a reasonable test infrastructure decision.

## Validation Results

| Command | Result |
|---|---|
| `uv run pytest tests/fund/processors/test_fund_disclosure_processor.py -k investor_experience_source_truth_share_change_selects_single_value_column` | 1 passed, 174 deselected in 0.73s |
| `uv run pytest tests/fund/processors/test_fund_disclosure_processor.py` | 175 passed in 0.50s |
| `uv run ruff check tests/fund/processors/test_fund_disclosure_processor.py` | All checks passed |
| `git diff --check` | Passed (no whitespace errors) |

## New Blocker Check

- No new findings introduced by this fix.
- Full test suite (175 tests) passes — no regression.
- New test is well-structured: isolated input, explicit assertions on all 5 share_change fields, no coupling to other tests.
- Helper functions are clean: correct signatures, no side effects, no dead code.

## Findings

未发现实质性问题。

## Open Questions

- 无。

## Residual Risk

- F1: fixed and validated.
- Broader investor_experience source-truth correctness: covered by prior code review gate; not re-reviewed here.
- Repository dirty state: unrelated pre-existing modified/untracked files remain outside this fix gate scope.

## Verdict

**TARGETED_CODE_REREVIEW_PASS**

F1 is fixed by a dedicated focused test (`test_investor_experience_source_truth_share_change_selects_single_value_column`) that independently proves the single-value-column selection path. No production code, docs, control docs, PR state, commits, or push were touched by this fix gate. Validation evidence is sufficient (targeted test, full suite, ruff, whitespace). No new blockers introduced.
