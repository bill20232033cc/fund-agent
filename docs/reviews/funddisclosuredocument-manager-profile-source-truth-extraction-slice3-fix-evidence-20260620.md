# FundDisclosureDocument manager_profile.v1 Source-truth Direct Extraction Slice 3 Fix Evidence

## Metadata

- Work unit: `FundDisclosureDocument manager_profile.v1 Source-truth Direct Extraction`
- Gate: `Slice 3 Fix Gate after code review`
- Role: AgentCodex fix worker only
- Implementation evidence: `docs/reviews/funddisclosuredocument-manager-profile-source-truth-extraction-slice3-implementation-evidence-20260620.md`
- Code reviews:
  - `docs/reviews/code-review-20260620-101854.md` (AgentDS)
  - `docs/reviews/code-review-20260620-102521.md` (AgentMiMo)
- Verdict: `FIX_COMPLETE`

## Changed Files

- `fund_agent/fund/processors/fund_disclosure_processor.py`
- `tests/fund/processors/test_fund_disclosure_processor.py`
- `docs/reviews/funddisclosuredocument-manager-profile-source-truth-extraction-slice3-fix-evidence-20260620.md`

## Finding Status

| Finding / request | Status | Fix evidence |
|---|---|---|
| DS Finding 1 MEDIUM: `_manager_profile_status` returns `accepted` even when ambiguity gaps exist | fixed in current slice | `_extract_manager_profile_source_truth()` now passes `ambiguous_paths` into `_manager_profile_status()`. `_manager_profile_status()` returns `accepted` only when all five top-level values are present and `ambiguous_paths` is empty. |
| DS Finding 2 LOW: `_manager_profile_cell_original_index` silently returns `0` when target cell is not found | fixed in current slice | `_manager_profile_cell_original_index()` now raises `ValueError("target_cell not found in table.cells")` instead of returning a valid-looking index. |
| DS open/residual: table-backed manager_alignment path coverage | fixed in current slice | Added a table-backed positive regression covering label/value split, guard behavior, public value shape and direct-route candidate suppression. |
| AgentMiMo findings | no accepted blocker | MiMo reported no substantive findings. Residual risks remain future-owned and are not implemented in this fix gate. |

## Tests Added / Updated

- `test_manager_profile_source_truth_full_value_with_internal_ambiguity_is_partial`
  - Proves all five `manager_profile.v1` top-level values can be present while an internal holdings ambiguity exists, and expected status is `partial`, not `accepted`.
  - Also proves `ambiguous_table_or_locator` gap remains present and `candidate_evidence == ()`.
- `test_manager_profile_source_truth_extracts_table_backed_alignment`
  - Proves table/cell-backed `manager_alignment` extraction handles label/value split and same-row guard context.
  - Confirms public shape stays `{"manager_holding", "employee_holding", "judgment"}` and `judgment` remains `None`.
- `test_manager_profile_cell_original_index_raises_for_foreign_cell`
  - Proves the private defensive helper raises `ValueError` for a cell not owned by `table.cells` and does not silently return `cells[0]`.

## Validation

```text
uv run pytest tests/fund/processors/test_fund_disclosure_processor.py
============================= test session starts ==============================
platform darwin -- Python 3.11.15, pytest-9.0.3, pluggy-1.6.0
rootdir: /Users/maomao/fund-agent
configfile: pyproject.toml
plugins: cov-7.1.0, asyncio-1.3.0, Faker-40.18.0, anyio-4.13.0
asyncio: mode=Mode.AUTO, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 157 items

tests/fund/processors/test_fund_disclosure_processor.py ................ [ 10%]
........................................................................ [ 56%]
.....................................................................    [100%]

============================= 157 passed in 0.85s ==============================
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

- No Slice 4 facade regression implemented.
- No docs sync implemented.
- No other field family implemented.
- No `docs/design.md`, README, `data_extractor.py`, `contracts.py`, extractors, repository/source/cache/live/network/provider/LLM, Service/UI/Host/renderer/quality-gate, control docs, startup packet, git state, PR/external state, or unrelated files modified.
- No public contract, source provenance schema, `EvidenceSourceKind`, `EvidenceAnchor`, or gap taxonomy expansion.
- No S6-D candidate evidence consumed as source truth.
- No live/network/PDF/FDR/Docling conversion/pdfplumber export/manual reference review/provider/LLM command run.

## Residual Risks And Owners

| Residual | Classification | Owner / Destination |
|---|---|---|
| Facade projection for manager-profile FDD source-truth values remains unproven | covered by later approved slice | Slice 4 implementation worker |
| `docs/design.md` and `fund_agent/fund/README.md` not yet synced for manager-profile current facts | covered by later approved slice | Slice 4 implementation worker |
| Real-report manager-profile field correctness remains unproven | assigned to later work unit | Future evidence worker / separate evidence gate |
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
