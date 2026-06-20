# FundDisclosureDocument manager_profile.v1 Source-truth Direct Extraction Aggregate Deepreview Controller Judgment

## Metadata

- Work unit: `FundDisclosureDocument manager_profile.v1 Source-truth Direct Extraction`
- Gate: `Aggregate Deepreview Gate`
- Review range: `4286987..HEAD`
- Reviewed HEAD: `f89ff07`
- Aggregate deepreviews:
  - AgentDS: `docs/reviews/funddisclosuredocument-manager-profile-source-truth-extraction-aggregate-deepreview-ds-20260620-110155.md`
  - AgentMiMo: `docs/reviews/funddisclosuredocument-manager-profile-source-truth-extraction-aggregate-deepreview-mimo-20260620-110155.md`
- Controller verdict: `ACCEPT_AGGREGATE_DEEPREVIEW_READY_FOR_READY_TO_OPEN_DRAFT_PR_NOT_READY`

## Decision

Accept the aggregate deepreview gate.

Both independent aggregate reviews returned `AGGREGATE_DEEPREVIEW_PASS` and found no substantive issue. The reviewed range covers the full `manager_profile.v1` work unit plan plus Slices 1-4:

- `5e4c8ff` plan accepted
- `e6df71b` Slice 1 accepted
- `30054f3` Slice 2 accepted
- `6c30386` Slice 3 accepted
- `f89ff07` Slice 4 accepted

## Controller Disposition

| Review question | Controller disposition |
|---|---|
| Source-truth admission integrity | accepted; no admission weakening found |
| Public missing/partial/accepted semantics and candidate suppression | accepted; direct route suppresses candidate evidence and preserves existing anchors/gaps |
| Facade regression and docs sync | accepted; explicit FDD facade projection is proven and docs do not overclaim |
| Scope limited to `manager_profile.v1` | accepted; remaining families are not implemented and holdings data does not leak to risk/stage |
| Prior review finding closure | accepted; all accepted slice findings are fixed or correctly dispositioned |

No aggregate finding requires fix. Residual risks are classified and owned by future gates.

## Controller Validation

The aggregate reviews reran or inspected:

```text
uv run pytest tests/fund/test_data_extractor.py tests/fund/processors/test_fund_disclosure_processor.py
194 passed
```

```text
uv run ruff check fund_agent/fund/processors/fund_disclosure_processor.py tests/fund/processors/test_fund_disclosure_processor.py tests/fund/test_data_extractor.py
All checks passed!
```

```text
git diff --check
<no output>
```

Controller accepts those validation results. No additional code change was made in this gate.

## Accepted Current Facts

- `manager_profile.v1` proof-positive FDD source-truth direct extraction is implemented for:
  - `portfolio_managers`
  - `manager_strategy_text`
  - `turnover_rate`
  - `manager_alignment`
  - `holdings_snapshot`
- Explicit FDD facade projection to `StructuredFundDataBundle` is covered by positive and negative tests.
- `docs/design.md` and `fund_agent/fund/README.md` are synced for the current implemented facts.
- `investor_experience.v1`, `current_stage.v1`, and `core_risk.v1` remain unimplemented for FDD source-truth direct extraction.
- Candidate evidence remains candidate-only / not-proven / NOT_READY.
- No real-report correctness, parser replacement, `EvidenceSourceKind` expansion, upper-layer direct consumption, golden/readiness, release, PR, push, or live evidence claim is accepted.

## Residual Risks

| Risk | Owner | Destination |
|---|---|---|
| Real-report manager-profile field correctness remains unproven | Future evidence worker | Separate evidence gate |
| `holdings_snapshot` may be relevant to future `current_stage.v1` / `core_risk.v1` extraction, but is not interpreted here | Future field-family planning worker | `current_stage.v1` / `core_risk.v1` planning gates |
| Broader holdings shapes, tenure normalization, strategy ambiguity, and manager alignment judgment remain outside this work unit | Future refinement owners | Later refinement / CHAPTER_CONTRACT gates |
| `investor_experience.v1`, `current_stage.v1`, and `core_risk.v1` still lack FDD source-truth direct extraction | Controller / planning worker | Subsequent field-family work units |

## Next Entry Point

`FundDisclosureDocument manager_profile.v1 Source-truth Direct Extraction Ready-to-open-draft-PR Gate`

Release/readiness remains `NOT_READY`.
