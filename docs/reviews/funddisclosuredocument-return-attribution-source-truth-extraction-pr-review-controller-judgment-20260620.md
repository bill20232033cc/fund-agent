# FundDisclosureDocument return_attribution.v1 Source-truth Direct Extraction PR Review Controller Judgment

## Verdict

`ACCEPT_PR_REVIEW_READY_FOR_ACCEPTED_PR_REVIEW_COMMIT_NOT_READY`

## Inputs

- PR: #30 `https://github.com/bill20232033cc/fund-agent/pull/30`
- PR title: `FundDisclosureDocument return_attribution source-truth extraction`
- PR state: draft/open
- Base: `main`
- Head branch: `funddisclosure-return-attribution-source-truth`
- Head reviewed: `f2937897d81caebde69fe37edc3a19fef1786bca`
- PR review artifact: `docs/reviews/pr-30-review-20260620-081341.md`
- CI refresh: `gh pr checks 30` reported `test pass`

## Controller Findings Disposition

| Item | Disposition |
|---|---|
| PR review substantive findings | Accepted as none. The review found `未发现实质性问题`. |
| PR head drift residual | Accepted as non-blocking review/control residual. PR #30 was created at `5ab675d`; the create-draft-PR bookkeeping commit was pushed and the reviewed current head is `f2937897d81caebde69fe37edc3a19fef1786bca`. Future controller judgments must use live PR metadata rather than treating `5ab675d` as current head. |
| CI pending residual from create-draft-PR gate | Closed by PR review refresh: `gh pr checks 30` reports `test pass`. |

## Accepted Boundary

- Only proof-positive `FundDisclosureDocument` admission may emit public source-truth values/anchors.
- `candidate_boundary is None` remains necessary but not sufficient.
- Missing/invalid proof, non-null `failure_class`, missing provenance, or candidate boundary preserves fail-closed public missing behavior.
- `return_attribution.v1` direct extraction is bounded to `nav_benchmark_performance`, `fee_schedule`, and `tracking_error`.
- Existing non-index `tracking_error` missing semantics remain preserved at facade projection.
- `manager_profile.v1`, `investor_experience.v1`, `current_stage.v1`, and `core_risk.v1` remain unimplemented for public source-truth extraction.
- No candidate promotion, parser replacement, `EvidenceSourceKind` expansion, Service/UI/Host/renderer/quality-gate direct consumption, mark-ready, merge, readiness or release transition is accepted here.

## Validation

- PR review artifact: `docs/reviews/pr-30-review-20260620-081341.md`
- Local targeted tests: `uv run pytest tests/fund/processors/test_fund_disclosure_processor.py tests/fund/test_data_extractor.py` -> `170 passed`
- Local lint: `uv run ruff check fund_agent/fund/processors/fund_disclosure_processor.py tests/fund/processors/test_fund_disclosure_processor.py tests/fund/test_data_extractor.py` -> `All checks passed!`
- GitHub CI: `gh pr checks 30` -> `test pass`

## Next Entry

`FundDisclosureDocument return_attribution.v1 Source-truth Direct Extraction Accepted PR Review Commit Gate`

This judgment only accepts the PR review gate and routes to local accepted PR review bookkeeping commit. PR #30 remains draft/open until a separate gate authorizes later PR state changes.
