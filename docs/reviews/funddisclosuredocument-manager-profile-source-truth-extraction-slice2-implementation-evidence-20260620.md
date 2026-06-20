# FundDisclosureDocument manager_profile.v1 Source-truth Direct Extraction Slice 2 Implementation Evidence

## Metadata

- Work unit: `FundDisclosureDocument manager_profile.v1 Source-truth Direct Extraction`
- Gate: `Implementation Gate - Slice 2 Manager Roster / Strategy / Turnover Values`
- Role: AgentCodex implementation worker only
- Accepted plan: `docs/reviews/funddisclosuredocument-manager-profile-source-truth-extraction-plan-20260620.md`
- Plan controller judgment: `docs/reviews/funddisclosuredocument-manager-profile-source-truth-extraction-plan-controller-judgment-20260620.md`
- Slice 1 accepted commit: `e6df71b`
- Evidence artifact: `docs/reviews/funddisclosuredocument-manager-profile-source-truth-extraction-slice2-implementation-evidence-20260620.md`
- Verdict: `IMPLEMENTATION_SLICE2_COMPLETE`

## Changed Files

- `fund_agent/fund/processors/fund_disclosure_processor.py`
- `tests/fund/processors/test_fund_disclosure_processor.py`
- `docs/reviews/funddisclosuredocument-manager-profile-source-truth-extraction-slice2-implementation-evidence-20260620.md`

## Exact Slice 2 Objective

Extend the accepted Slice 1 `manager_profile.v1` proof-positive direct extractor so stable FDD content can emit only the first three allowed top-level values:

- `portfolio_managers`
- `manager_strategy_text`
- `turnover_rate`

Slice 2 does not implement `manager_alignment` or `holdings_snapshot`, so positive direct-route cases remain `partial`, not `accepted`.

## Implemented Behavior

- Direct extraction still runs only behind the existing `FundDisclosureSourceTruthAdmissionProof` admission guard.
- Proof-positive direct route always returns `candidate_evidence=()` for `manager_profile.v1`, including direct-route missing.
- Missing proof / invalid proof / candidate-boundary paths keep existing candidate-only fail-closed behavior.
- Direct-route `missing` returns `value={}`, `anchors=()`, and a `field_family_missing` gap.
- Direct-route `partial` returns `extraction_mode="direct"` and only emitted top-level subvalues plus `field_family_partial` gaps for missing top-level subvalues.
- Ambiguous duplicate stable values are omitted for the conflicting output path and add `ambiguous_table_or_locator`.
- Unstable table, paragraph, or cell locators are skipped.

## Public Value Shape Emitted

### `portfolio_managers`

Emitted shape:

```python
{
    "schema_version": "portfolio_manager_tenure_list.v1",
    "fund_code": context.fund_code,
    "report_year": context.document_year,
    "portfolio_managers": [
        {
            "name": disclosed_name,
            "role": disclosed_or_normalized_role_with_基金经理,
            "start_date": disclosed_start_date_or_none,
            "end_date": disclosed_end_date,  # only when present
            "source_anchor": {
                "section_id": ...,
                "section_title": ...,
                "page_number": None,
                "table_id": ...,
                "row_locator": "portfolio_manager:<name>",
            },
        }
    ],
}
```

Rules implemented:

- Reads stable table rows under manager-related headings.
- Requires non-empty `name`.
- Requires same-row role/context containing `基金经理`; broad heading alone is insufficient.
- Preserves disclosed date text.
- Does not infer tenure or current manager status.

### `manager_strategy_text`

Emitted shape:

```python
{
    "strategy_summary": str | None,
    "market_outlook": str | None,
}
```

Rules implemented:

- Reads stable paragraphs under strategy/operation and outlook headings.
- Concatenates same-subkey stable paragraph text in document order.
- Emits only `strategy_summary` and/or `market_outlook`.
- Does not classify style, manager skill, current stage, or forecast quality.

### `turnover_rate`

Emitted shape:

```python
{
    "turnover_rate": disclosed_percent_literal,
    "turnover_basis": disclosed_basis_text_or_none,
}
```

Rules implemented:

- Reads stable table/cell rows or explicit paragraphs with turnover labels.
- Requires a disclosed percent literal for `turnover_rate`.
- Basis-only disclosure does not emit `turnover_rate`.
- Does not judge turnover quality, risk, history, or regulation.

## Tests Added Or Updated

- Updated `test_manager_profile_source_truth_route_suppresses_candidate_evidence`
  - Proves proof-positive direct-route missing still suppresses S6-D candidate evidence.
- Added `test_manager_profile_source_truth_extracts_roster_strategy_turnover_shape`
  - Proves Slice 2 emits exactly `schema_version`, `portfolio_managers`, `manager_strategy_text`, and `turnover_rate`; keeps status `partial`; suppresses candidate evidence; keeps `current_stage.v1` and `core_risk.v1` missing.
- Added `test_manager_profile_source_truth_partial_when_required_groups_missing`
  - Proves partial status, absent missing top-level keys, and basis-only turnover non-emission.
- Added `test_manager_profile_source_truth_missing_when_no_allowed_labels`
  - Proves proof-positive no-match content stays direct-route missing with no candidate fallback.
- Added `test_manager_profile_source_truth_ambiguous_duplicate_omits_conflicting_value`
  - Proves conflicting turnover values omit `turnover_rate` and add `ambiguous_table_or_locator`.
- Added `test_manager_profile_source_truth_skips_unstable_locator`
  - Proves unstable table, paragraph, and cell locators do not produce public values or anchors.

Existing Slice 1 and S6-D candidate-only tests remain passing.

## Validation

```text
uv run pytest tests/fund/processors/test_fund_disclosure_processor.py
============================= test session starts ==============================
platform darwin -- Python 3.11.15, pytest-9.0.3, pluggy-1.6.0
rootdir: /Users/maomao/fund-agent
configfile: pyproject.toml
plugins: cov-7.1.0, asyncio-1.3.0, Faker-40.18.0, anyio-4.13.0
asyncio: mode=Mode.AUTO, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 144 items

tests/fund/processors/test_fund_disclosure_processor.py ................ [ 11%]
........................................................................ [ 61%]
........................................................                 [100%]

============================= 144 passed in 0.82s ==============================
```

```text
uv run ruff check fund_agent/fund/processors/fund_disclosure_processor.py tests/fund/processors/test_fund_disclosure_processor.py
All checks passed!
```

```text
git diff --check
<no output>
```

## Deferred / No Leakage Confirmation

- `manager_alignment` remains unimplemented and deferred to Slice 3.
- `holdings_snapshot` remains unimplemented and deferred to Slice 3.
- `current_stage.v1` and `core_risk.v1` do not receive `turnover_rate`, `holdings_snapshot`, strategy text, or manager roster values in this slice.
- No `investor_experience.v1`, `current_stage.v1`, `core_risk.v1`, or other family source-truth extraction was implemented.
- No `EvidenceSourceKind`, `EvidenceAnchor`, public contract, provenance schema, or gap taxonomy expansion was made.
- No S6-D candidate evidence is consumed as source truth.

## Residual Risks And Owners

| Residual risk | Classification | Owner / destination |
|---|---|---|
| `manager_alignment` source-truth value absent | covered by later approved slice | Slice 3 implementation gate |
| `holdings_snapshot` source-truth value absent | covered by later approved slice | Slice 3 implementation gate |
| Facade projection regression not added in this slice | covered by later approved slice | Slice 4 implementation gate |
| `docs/design.md` and `fund_agent/fund/README.md` not synced in this slice | covered by later approved slice | Slice 4 docs sync |
| Real-report manager-profile field correctness remains unproven | assigned to later work unit | Future evidence worker / separate evidence gate |
| Holdings/turnover interpretation for `current_stage.v1` or `core_risk.v1` remains unresolved | assigned to later work unit | Future field-family planning gates |

## Stop Confirmation

- No commit.
- No push.
- No PR creation or update.
- No mark-ready, merge, or later gate action.
- No external state change.
- No live/network/PDF/FDR/Docling conversion/pdfplumber export/manual reference review/provider/LLM command.
- No unrelated cleanup, staging, deletion, or classification.
