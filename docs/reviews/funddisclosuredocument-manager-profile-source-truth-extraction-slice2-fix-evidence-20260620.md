# FundDisclosureDocument manager_profile.v1 Source-truth Direct Extraction Slice 2 Fix Evidence

## Metadata

- Work unit: `FundDisclosureDocument manager_profile.v1 Source-truth Direct Extraction`
- Gate: `Slice 2 Fix Gate after code review`
- Role: AgentCodex fix worker only
- Implementation evidence: `docs/reviews/funddisclosuredocument-manager-profile-source-truth-extraction-slice2-implementation-evidence-20260620.md`
- Code reviews:
  - `docs/reviews/code-review-20260620-095003.md`
  - `docs/reviews/code-review-20260620-095109.md`
- Evidence artifact: `docs/reviews/funddisclosuredocument-manager-profile-source-truth-extraction-slice2-fix-evidence-20260620.md`
- Verdict: `FIX_COMPLETE`

## Changed Files

- `fund_agent/fund/processors/fund_disclosure_processor.py`
- `tests/fund/processors/test_fund_disclosure_processor.py`
- `docs/reviews/funddisclosuredocument-manager-profile-source-truth-extraction-slice2-fix-evidence-20260620.md`

## Findings Fixed / Deferred

| Finding | Status | Evidence |
|---|---|---|
| DS F1 MEDIUM roster guard / fallback role bug | fixed | `_manager_profile_roster_row_context()` no longer includes `cell.heading_path`; `_manager_profile_roster_entry()` skips rows with disclosed role values that do not contain `基金经理`; role fallback only uses same-row labels/headers/cell values. Added `test_manager_profile_source_truth_roster_broad_heading_does_not_authorize_non_manager_row`. |
| DS F2 + MiMo 001 MEDIUM strategy body-text false positive | fixed | `_manager_profile_paragraph_matches_strategy()` is now heading-path gated only. Added `test_manager_profile_source_truth_strategy_requires_heading_path_membership`. |
| Low test assertion fix | fixed | Replaced `dict.get()` empty-truth assertion with explicit key absence checks in `test_manager_profile_source_truth_partial_when_required_groups_missing`. |
| Low roster ambiguity coverage | fixed | Added `test_manager_profile_source_truth_ambiguous_roster_name_omits_conflicting_entry` and `test_manager_profile_source_truth_identical_roster_duplicate_keeps_first_locator`. Roster duplicate comparison now excludes `source_anchor` so identical disclosed values keep the first locator instead of conflicting on locator metadata. |
| MiMo 003 optional strategy ambiguity test | deferred-with-owner | Current Slice 2 implementation defines strategy paragraphs as same-subkey disclosed text concatenation in document order and does not define a separate conflict detector for heading lineage. No new strategy ambiguity semantics were invented in this fix gate. Owner: future manager-profile source-truth refinement or explicit controller-approved strategy ambiguity gate. |

## Tests Added / Updated

- Added `test_manager_profile_source_truth_roster_broad_heading_does_not_authorize_non_manager_row`
  - Proves broad table/section heading containing manager tokens cannot self-authorize a row with `职务=研究员`.
- Added `test_manager_profile_source_truth_strategy_requires_heading_path_membership`
  - Proves body text containing `投资策略` / `运作分析` under `其他重要事项` does not emit `manager_strategy_text`.
- Added `test_manager_profile_source_truth_ambiguous_roster_name_omits_conflicting_entry`
  - Proves same manager name with conflicting disclosed date values omits `portfolio_managers` and adds `ambiguous_table_or_locator`.
- Added `test_manager_profile_source_truth_identical_roster_duplicate_keeps_first_locator`
  - Proves same manager name with identical disclosed role/date values emits exactly one entry with the first locator and no ambiguity gap.
- Updated `test_manager_profile_source_truth_partial_when_required_groups_missing`
  - Uses explicit missing-key assertions for absent top-level values.

Existing Slice 1, Slice 2 positive/negative, and S6-D candidate-only tests remain passing.

## Validation

```text
uv run pytest tests/fund/processors/test_fund_disclosure_processor.py
============================= test session starts ==============================
platform darwin -- Python 3.11.15, pytest-9.0.3, pluggy-1.6.0
rootdir: /Users/maomao/fund-agent
configfile: pyproject.toml
plugins: cov-7.1.0, asyncio-1.3.0, Faker-40.18.0, anyio-4.13.0
asyncio: mode=Mode.AUTO, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 148 items

tests/fund/processors/test_fund_disclosure_processor.py ................ [ 10%]
........................................................................ [ 59%]
............................................................             [100%]

============================= 148 passed in 0.78s ==============================
```

```text
uv run ruff check fund_agent/fund/processors/fund_disclosure_processor.py tests/fund/processors/test_fund_disclosure_processor.py
All checks passed!
```

```text
git diff --check
<no output>
```

## No Scope Expansion Confirmation

- No Slice 3 implementation.
- No `manager_alignment` implementation.
- No `holdings_snapshot` implementation.
- No Slice 4 facade regression or docs sync implementation.
- No `investor_experience.v1`, `current_stage.v1`, `core_risk.v1`, or other family source-truth extraction implementation.
- No public contract, `EvidenceSourceKind`, `EvidenceAnchor`, provenance schema, or gap taxonomy expansion.
- No repository/source/cache/live/network/provider/LLM, Service/UI/Host/renderer/quality-gate change.

## Stop Confirmation

- No commit.
- No push.
- No PR creation or update.
- No mark-ready, merge, or later gate action.
- No external state change.
- No unrelated cleanup, staging, deletion, or classification.
- No live/network/PDF/FDR/Docling conversion/pdfplumber export/manual reference review/provider/LLM command.
