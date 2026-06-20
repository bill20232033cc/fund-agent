# FundDisclosureDocument manager_profile.v1 Source-truth Direct Extraction Slice 3 Code Review Controller Judgment

## Metadata

- Work unit: `FundDisclosureDocument manager_profile.v1 Source-truth Direct Extraction`
- Gate: `Implementation Gate - Slice 3 Alignment / Holdings Snapshot / Anchor-Gap Hardening`
- Plan artifact: `docs/reviews/funddisclosuredocument-manager-profile-source-truth-extraction-plan-20260620.md`
- Plan controller judgment: `docs/reviews/funddisclosuredocument-manager-profile-source-truth-extraction-plan-controller-judgment-20260620.md`
- Slice 2 accepted commit: `30054f3`
- Implementation evidence: `docs/reviews/funddisclosuredocument-manager-profile-source-truth-extraction-slice3-implementation-evidence-20260620.md`
- Initial code reviews:
  - AgentDS: `docs/reviews/code-review-20260620-101854.md`
  - AgentMiMo: `docs/reviews/code-review-20260620-102521.md`
- Fix evidence: `docs/reviews/funddisclosuredocument-manager-profile-source-truth-extraction-slice3-fix-evidence-20260620.md`
- Targeted re-reviews:
  - AgentDS: `docs/reviews/code-review-20260620-103515-slice3-rereview-ds.md`
  - AgentMiMo: `docs/reviews/code-review-20260620-103515-slice3-rereview-mimo.md`
- Controller verdict: `ACCEPT_SLICE3_READY_FOR_SLICE4_FACADE_TEST_DOCS_SYNC_NOT_READY`

## Decision

Accept Slice 3 implementation after fix and targeted re-review.

Slice 3 implements proof-positive `manager_profile.v1` direct extraction for the remaining two approved top-level values:

- `manager_alignment`
- `holdings_snapshot`

Together with accepted Slice 2 values, `manager_profile.v1` now has direct-route extraction for `portfolio_managers`, `manager_strategy_text`, `turnover_rate`, `manager_alignment`, and `holdings_snapshot` inside `FundDisclosureDocumentProcessor`.

This gate preserves fail-closed source-truth admission, direct-route `candidate_evidence=()`, public partial/missing semantics, existing `EvidenceAnchor` shape, existing gap taxonomy, and no-leakage to `current_stage.v1` / `core_risk.v1`. It does not implement Slice 4 facade regression, docs sync, other field families, parser replacement, source-kind expansion, upper-layer consumption, real-report correctness, readiness or release.

## Review Disposition

| Finding | Source | Controller disposition | Evidence |
|---|---|---|---|
| `_manager_profile_status` could return `accepted` while ambiguity gaps existed | DS medium | accepted and fixed | DS and MiMo targeted re-reviews verify `accepted` requires all five top-level values and empty `ambiguous_paths`; ambiguity keeps status `partial` |
| `_manager_profile_cell_original_index` silently returned `0` for a foreign cell | DS low | accepted and fixed | DS and MiMo targeted re-reviews verify `ValueError` and regression coverage |
| Table-backed `manager_alignment` positive path lacked coverage | DS residual request | accepted and fixed | DS and MiMo targeted re-reviews verify label/value split, guard context, public shape and candidate suppression coverage |

No accepted finding remains open for Slice 3. No new blocker was reported by targeted re-review.

## Controller Validation

```text
uv run pytest tests/fund/processors/test_fund_disclosure_processor.py
157 passed in 0.85s
```

```text
uv run ruff check fund_agent/fund/processors/fund_disclosure_processor.py tests/fund/processors/test_fund_disclosure_processor.py
All checks passed!
```

```text
git diff --check
<no output>
```

## Accepted Behavior

- `manager_alignment` emits only `manager_holding`, `employee_holding`, and `judgment=None`.
- `manager_alignment` does not infer motivation, benefit alignment, manager quality, current stage or risk.
- Generic `持有本基金` requires same-source manager/employee/fund-manager guard context.
- `holdings_snapshot` emits direct top-ten holdings and industry distribution rows using disclosed Chinese headers and cell text.
- `holdings_snapshot` does not emit concentration, style drift, share-change, current-stage, core-risk, QDII/FOF or bond-holding interpretation.
- Conflicting duplicate holdings rows are omitted with `ambiguous_table_or_locator`.
- Identical duplicate manager-alignment values keep the first locator.
- A complete five-value `manager_profile.v1` result is `accepted` only when no ambiguity gaps exist; complete values with internal ambiguity remain `partial`.
- Direct-route missing/partial results keep `candidate_evidence=()`.

## Residual Risks

| Risk | Owner | Destination |
|---|---|---|
| Facade projection for manager-profile FDD source-truth values remains unproven | Implementation worker | Slice 4 |
| `docs/design.md` and `fund_agent/fund/README.md` not yet synced for manager-profile current facts | Implementation worker | Slice 4 |
| Real-report manager-profile field correctness remains unproven | Future evidence worker | Separate evidence gate |
| Broader holdings shapes such as all-stock details, bond holdings, QDII/FOF holdings remain outside this slice | Future refinement owner | Future holdings refinement gate |
| Manager alignment judgment remains absent by design | Future analysis owner | Later CHAPTER_CONTRACT / analysis gate |
| Remaining field families `investor_experience.v1`, `current_stage.v1`, and `core_risk.v1` still lack source-truth direct extraction work units | Controller / planning worker | Subsequent family planning gates |

## Next Entry Point

`FundDisclosureDocument manager_profile.v1 Source-truth Direct Extraction Implementation Gate - Slice 4 Facade/Test/Docs Sync`

Release/readiness remains `NOT_READY`.
