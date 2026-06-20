# FundDisclosureDocument investor_experience.v1 Source-truth Direct Extraction Code Review Controller Judgment

## Metadata

- Work unit: `FundDisclosureDocument investor_experience.v1 Source-truth Direct Extraction`
- Gate: Implementation / Code Review / Fix / Re-review Gate
- Branch: `funddisclosure-investor-experience-source-truth`
- Accepted plan commit: `1bf4187`
- Plan artifact: `docs/reviews/funddisclosuredocument-investor-experience-source-truth-extraction-plan-20260620.md`
- Implementation evidence: `docs/reviews/funddisclosuredocument-investor-experience-source-truth-extraction-implementation-evidence-20260620.md`
- Code reviews:
  - `docs/reviews/code-review-investor-experience-source-truth-ds-20260620.md`
  - `docs/reviews/code-review-investor-experience-source-truth-mimo-20260620.md`
- Fix evidence: `docs/reviews/funddisclosuredocument-investor-experience-source-truth-extraction-fix-evidence-20260620.md`
- Targeted re-review: `docs/reviews/code-rereview-investor-experience-source-truth-mimo-20260620.md`
- Artifact path: `docs/reviews/funddisclosuredocument-investor-experience-source-truth-extraction-code-review-controller-judgment-20260620.md`

## Controller Judgment

Verdict: `ACCEPT_IMPLEMENTATION_AND_CODE_REVIEW_READY_FOR_ACCEPTED_SLICE_COMMIT_NOT_READY`

The implementation gate is accepted for the current slice. The accepted scope is exactly `investor_experience.v1` FDD source-truth direct extraction for existing public/bundle keys:

- `investor_return`
- `holder_structure`
- `share_change`

`subscription_redemption` and `income_distribution` remain candidate-only locator roles and are not public source-truth subvalues. `current_stage.v1` and `core_risk.v1` remain unimplemented for FDD source-truth direct extraction. This judgment does not claim real-report correctness, parser replacement, golden/readiness, release, or direct Service/UI/Host/renderer/quality-gate consumption.

## Accepted Findings

| Finding | Source | Decision | Status |
|---|---|---|---|
| Missing dedicated `share_change_selects_single_value_column` test | `code-review-investor-experience-source-truth-mimo-20260620.md` F1 | accepted | fixed by `test_investor_experience_source_truth_share_change_selects_single_value_column`; confirmed by targeted re-review |
| `_investor_return_has_unavailable_wording` single-character `无` edge | `code-review-investor-experience-source-truth-ds-20260620.md` F1 | rejected-with-reason | no functional false-positive risk because no percent value is matched on standalone unavailable wording |
| Plan-listed single-value-column test was initially merged into broader coverage | `code-review-investor-experience-source-truth-ds-20260620.md` F2 | accepted | fixed by the dedicated test above |
| Unavailable wording before label edge | `code-review-investor-experience-source-truth-ds-20260620.md` F3 | deferred-with-owner | future wording-expansion hardening only if real fixture evidence shows a false-positive; not a current blocker |

No blocking finding remains after targeted re-review.

## Validation Accepted

Controller accepted the following local validation evidence:

```text
uv run pytest tests/fund/processors/test_fund_disclosure_processor.py
175 passed
```

```text
uv run pytest tests/fund/test_data_extractor.py -k disclosure_source_truth_investor_experience
1 passed
```

```text
uv run ruff check fund_agent/fund/processors/fund_disclosure_processor.py tests/fund/processors/test_fund_disclosure_processor.py tests/fund/test_data_extractor.py
All checks passed
```

```text
git diff --check
passed
```

Fix-gate validation additionally accepted:

```text
uv run pytest tests/fund/processors/test_fund_disclosure_processor.py -k investor_experience_source_truth_share_change_selects_single_value_column
1 passed
```

## Scope Boundaries

- No `contracts.py`, `data_extractor.py`, `extractors/**`, `documents/**`, `services/**`, `ui/**`, `host/**`, or `agent/**` production changes were made.
- No parser replacement, repository/source/cache/PDF/Docling/pdfplumber/live/network/provider/LLM work was introduced.
- No `EvidenceSourceKind` or public `EvidenceAnchor` expansion was introduced.
- Public direct extraction remains proof-positive only; proof-missing, proof-invalid, and candidate-boundary paths retain public missing semantics.
- Direct-route `investor_experience.v1` returns `candidate_evidence=()`, including direct-route missing.

## Next Gate

After the accepted slice commit, the next entry point is:

`FundDisclosureDocument investor_experience.v1 Source-truth Direct Extraction Aggregate Deepreview Gate`

Release/readiness remains `NOT_READY`.
