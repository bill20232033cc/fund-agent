# PR #32 Deep Review - AgentCodex

## Findings

未发现实质性问题。

## Verdict

`PR_REVIEW_PASS`

## Scope

- Mode: PR
- Branch or PR: PR #32 `https://github.com/bill20232033cc/fund-agent/pull/32`
- Base: `funddisclosure-manager-profile-source-truth`
- Head: `funddisclosure-investor-experience-source-truth`
- Reviewed head oid: `865369d9798966962baf9d4ae6bd5625be55b2cc`
- Output file: `docs/reviews/pr-32-review-codex-20260620.md`
- Included scope: PR #32 diff and gate artifacts for `FundDisclosureDocument investor_experience.v1 Source-truth Direct Extraction`
- Excluded scope: unrelated untracked files, outside-repo files, GitHub mutation, production code edits, commit, push, PR comments
- Parallel review coverage: 无

## PR Metadata Verification

Source: `gh pr view 32 --json number,state,isDraft,headRefName,baseRefName,headRefOid,mergeStateStatus,statusCheckRollup,title,url`.

| Check | Result |
|---|---|
| PR state | `OPEN` |
| Draft | `true` |
| Base branch | `funddisclosure-manager-profile-source-truth` |
| Head branch | `funddisclosure-investor-experience-source-truth` |
| Head oid | `865369d9798966962baf9d4ae6bd5625be55b2cc` |
| Merge state | `CLEAN` |
| CI | `test` / `SUCCESS` |
| Title | `FundDisclosureDocument investor_experience source-truth extraction` |

## Scope Boundary Verification

`git diff --name-status funddisclosure-manager-profile-source-truth...funddisclosure-investor-experience-source-truth` shows the PR is limited to:

- control/docs/review artifacts for the investor-experience work unit;
- `fund_agent/fund/README.md`;
- `fund_agent/fund/processors/fund_disclosure_processor.py`;
- `tests/fund/processors/test_fund_disclosure_processor.py`;
- `tests/fund/test_data_extractor.py`.

No PR diff was found in `data_extractor.py`, `contracts.py`, `extractors/**`, `documents/**`, `services/**`, `ui/**`, `host/**`, `agent/**`, renderer, or quality-gate code.

## Code Review Notes

- `fund_agent/fund/processors/fund_disclosure_processor.py:939` keeps source-truth extraction behind the existing `source_truth_extraction_allowed` admission path.
- `fund_agent/fund/processors/fund_disclosure_processor.py:979` adds only `_extract_investor_experience_source_truth(...)` under the same proof-positive guard as existing source-truth families.
- `fund_agent/fund/processors/fund_disclosure_processor.py:998` suppresses `investor_experience.v1` candidate evidence only when direct result is present; candidate-only proof-missing paths still use `_select_investor_experience_candidate_evidence(...)`.
- `fund_agent/fund/processors/fund_disclosure_processor.py:5220` emits only `investor_experience.v1` with `candidate_evidence=()`.
- `fund_agent/fund/processors/fund_disclosure_processor.py:6304` builds public value only from `investor_return`, `holder_structure`, and `share_change`.
- `fund_agent/fund/processors/fund_disclosure_processor.py:6353` records missing, partial, and ambiguity gaps without promoting `subscription_redemption` or `income_distribution`.
- `fund_agent/fund/data_extractor.py:708` already maps `investor_experience.v1` only to existing bundle fields `investor_return`, `holder_structure`, and `share_change`; PR #32 does not modify this facade.
- `tests/fund/processors/test_fund_disclosure_processor.py:5444` through `6144` cover proof-positive, proof-missing, candidate-boundary, exact public shape, estimated return, ambiguity, placeholder filtering, partial/missing, single-column and fund-code share class selection, net-change calculation, and adjacent family non-interference.
- `tests/fund/test_data_extractor.py:1317` covers proof-positive FDD facade projection to bundle fields.
- `tests/fund/test_data_extractor.py:1418` covers candidate-only investor experience staying public missing.

## Overclaim Check

No blocking overclaim found.

- `subscription_redemption` and `income_distribution` remain candidate-only roles and are not emitted as public source-truth subvalues.
- `current_stage.v1` and `core_risk.v1` remain unimplemented for FDD source-truth direct extraction.
- No parser replacement, `EvidenceSourceKind` expansion, public `EvidenceAnchor` schema expansion, source/repository behavior change, Service/UI/Host/renderer/quality-gate consumption, readiness, release, mark-ready, merge, or GitHub mutation is introduced.
- Docs/control wording preserves `NOT_READY` and candidate-only boundaries.

## Validation

```text
uv run pytest tests/fund/processors/test_fund_disclosure_processor.py
175 passed
```

```text
uv run pytest tests/fund/test_data_extractor.py -k disclosure_source_truth_investor_experience
1 passed, 38 deselected
```

```text
git diff --check funddisclosure-manager-profile-source-truth...funddisclosure-investor-experience-source-truth
passed
```

## Open Questions

无。

## Residual Risk

- Real-report correctness remains unproven by this no-live fixture-backed PR review and stays outside the authorized PR Review Gate.
- `current_stage.v1` and `core_risk.v1` source-truth direct extraction remain separate future work units.
