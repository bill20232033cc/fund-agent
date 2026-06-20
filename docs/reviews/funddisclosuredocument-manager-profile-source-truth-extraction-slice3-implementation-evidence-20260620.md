# FundDisclosureDocument manager_profile.v1 Source-truth Direct Extraction Slice 3 Implementation Evidence

## Metadata

- Work unit: `FundDisclosureDocument manager_profile.v1 Source-truth Direct Extraction`
- Gate: `Implementation Gate - Slice 3 Alignment / Holdings Snapshot / Anchor-Gap Hardening`
- Role: AgentCodex implementation worker only
- Accepted plan: `docs/reviews/funddisclosuredocument-manager-profile-source-truth-extraction-plan-20260620.md`
- Plan controller judgment: `docs/reviews/funddisclosuredocument-manager-profile-source-truth-extraction-plan-controller-judgment-20260620.md`
- Slice 2 controller judgment: `docs/reviews/funddisclosuredocument-manager-profile-source-truth-extraction-slice2-code-review-controller-judgment-20260620.md`
- Verdict: `IMPLEMENTATION_SLICE3_COMPLETE`

## Changed Files

- `fund_agent/fund/processors/fund_disclosure_processor.py`
- `tests/fund/processors/test_fund_disclosure_processor.py`
- `docs/reviews/funddisclosuredocument-manager-profile-source-truth-extraction-slice3-implementation-evidence-20260620.md`

## Exact Slice 3 Objective

Add the remaining two allowed `manager_profile.v1` top-level source-truth direct values and complete anchor/gap hardening:

1. `manager_alignment`
2. `holdings_snapshot`

No other field family, facade regression, docs sync, contract/schema expansion, source/repository behavior, parser replacement, provider/LLM path, live/PDF/Docling conversion, PR state, branch state, git index, or unrelated residue was changed.

## Implemented Public Value Shape

`manager_alignment`:

```text
{
  "manager_holding": str | None,
  "employee_holding": str | None,
  "judgment": None
}
```

- Emitted only when at least one of `manager_holding` or `employee_holding` exists.
- `judgment` is always `None`.
- No motivation, benefit-alignment, manager-quality, current-stage, or risk inference is emitted.
- Generic `持有本基金` requires same-source guard context containing `基金经理`, `从业人员`, or `基金管理人`.
- Same value across multiple stable locators keeps the first anchor; conflicting values are omitted with `ambiguous_table_or_locator`.

`holdings_snapshot`:

```text
{
  "top_holdings": list[dict[str, str]] | None,
  "top_holdings_status": "direct_top_ten" | "missing",
  "top_holdings_source": "top_ten" | "none",
  "industry_distribution": list[dict[str, str]] | None,
  "industry_distribution_status": "direct" | "missing"
}
```

- Row dict keys preserve disclosed Chinese column headers.
- Row dict values preserve disclosed cell text.
- `top_holdings` is capped at the first 10 non-conflicting disclosed top-ten rows.
- Conflicting duplicate holdings rows are omitted with `ambiguous_table_or_locator`; identical duplicates keep the first locator.
- No concentration, style drift, core risk, current-stage, share-change, target-fund, bond-holding, QDII/FOF conclusion, or other interpretation is emitted.

Family status behavior:

- All five top-level subvalues present: `status="accepted"`, `extraction_mode="direct"`, no gaps except ambiguity.
- Partial top-level presence: `status="partial"`, `extraction_mode="direct"`, `field_family_partial` gaps for missing top-level values.
- Missing all allowed subvalues: `status="missing"`, `extraction_mode="missing"`, `value={}`, `anchors=()`.
- Proof-positive direct route keeps `candidate_evidence=()` for `manager_profile.v1`, including missing.

## Tests Added / Updated

- `test_manager_profile_source_truth_extracts_alignment_without_judgment`
  - Proves manager/employee holding values emit in the allowed shape and `judgment` remains `None`.
- `test_manager_profile_source_truth_extracts_holdings_snapshot_without_risk_or_stage_fields`
  - Proves top holdings and industry distribution preserve Chinese headers/cell text and do not emit risk/stage fields.
- `test_manager_profile_source_truth_rejects_generic_holding_without_guard_context`
  - Proves generic `持有本基金` cannot self-authorize without manager/employee/fund-manager guard context.
- `test_manager_profile_source_truth_same_value_multi_locator_keeps_first_anchor`
  - Proves identical duplicate alignment values keep the first public anchor and do not create ambiguity.
- `test_manager_profile_source_truth_conflicting_holdings_row_is_ambiguous`
  - Proves conflicting duplicate holdings rows are omitted and produce `ambiguous_table_or_locator`.
- `test_manager_profile_source_truth_accepted_when_all_allowed_groups_present`
  - Proves all five top-level manager-profile groups produce `accepted` direct output with no gaps.
- Existing Slice 1/Slice 2/S6-D candidate tests remained in the same file and passed in the full single-file pytest run.

## Validation

```text
uv run pytest tests/fund/processors/test_fund_disclosure_processor.py
============================= test session starts ==============================
platform darwin -- Python 3.11.15, pytest-9.0.3, pluggy-1.6.0
rootdir: /Users/maomao/fund-agent
configfile: pyproject.toml
plugins: cov-7.1.0, asyncio-1.3.0, Faker-40.18.0, anyio-4.13.0
asyncio: mode=Mode.AUTO, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 154 items

tests/fund/processors/test_fund_disclosure_processor.py ................ [ 10%]
........................................................................ [ 57%]
..................................................................       [100%]

============================= 154 passed in 0.86s ==============================
```

```text
uv run ruff check fund_agent/fund/processors/fund_disclosure_processor.py tests/fund/processors/test_fund_disclosure_processor.py
All checks passed!
```

```text
git diff --check
<no output>
```

## Explicit Non-actions

- Facade regression not performed; owned by Slice 4.
- Docs sync not performed; owned by Slice 4.
- `docs/design.md`, `fund_agent/fund/README.md`, control docs and startup packet not modified.
- `current_stage.v1` and `core_risk.v1` public values and anchors remain empty in the Slice 3 proof-positive regression tests; holdings snapshot and risk/stage interpretations are not routed into those families.
- S6-D candidate evidence was not consumed as source truth.
- No `EvidenceSourceKind`, `EvidenceAnchor`, public contract, source provenance schema, or gap taxonomy expansion was made.
- No live/network/PDF/FDR/Docling conversion/pdfplumber export/manual reference review/provider/LLM command was run.

## Residual Risks And Owners

| Residual | Classification | Owner / Destination |
|---|---|---|
| Facade projection for manager-profile FDD source-truth values remains unproven | covered by later approved slice | Slice 4 implementation worker |
| `docs/design.md` and `fund_agent/fund/README.md` not yet synced for manager-profile current facts | covered by later approved slice | Slice 4 implementation worker |
| Real-report manager-profile field correctness remains unproven | assigned to later work unit | Future evidence worker / separate evidence gate |
| `holdings_snapshot` may be relevant to future `current_stage.v1` or `core_risk.v1` interpretation | assigned to later work unit | Future field-family planning gates |
| Broader holdings shapes such as all-stock details, bond holdings, QDII/FOF holdings remain outside this slice | assigned to later work unit | Future holdings refinement gate |
| Manager alignment judgment remains absent by design | assigned to later work unit | Later CHAPTER_CONTRACT / analysis gate |

## Stop Confirmation

- No commit.
- No push.
- No PR created or modified.
- No mark-ready, merge, approval, reviewer request, or external state action.
- No staging.
- No unrelated cleanup, deletion, classification, or artifact disposition.
- No next gate action.
