# FundDisclosureDocument core_risk.v1 Deferred Risk Roles Source-truth Direct Extraction Code Review Controller Judgment

## Verdict

`ACCEPT_CODE_REVIEW_AND_REREVIEW_READY_FOR_ACCEPTED_SLICE_COMMIT`

Release/readiness remains `NOT_READY`.

## Scope

- Work unit: `FundDisclosureDocument core_risk.v1 Deferred Risk Roles Source-truth Direct Extraction`
- Gate: code review -> fix -> targeted re-review
- Branch: `funddisclosure-core-risk-source-truth`
- Accepted plan commit: `1f56ee8`
- Implementation evidence: `docs/reviews/funddisclosuredocument-core-risk-deferred-roles-source-truth-extraction-implementation-evidence-20260620.md`

## Reviewed Artifacts

- Initial Codex code review: `docs/reviews/code-review-20260620-184649.md`
- Initial MiMo code review: `docs/reviews/code-review-20260620-184943.md`
- Codex targeted re-review: `docs/reviews/code-review-20260620-191113.md`
- MiMo targeted re-review: `docs/reviews/code-review-20260620-191158.md`

## Finding Disposition

### Codex Finding 1: pure numeric role table cells omitted

Disposition: `accepted`, fixed, and re-reviewed closed.

Reason:

- The initial implementation only matched role tokens against `cell_text`, so pure numeric body cells such as `180%` and `45%` could be omitted even when same-role row/header/caption context existed.
- The fix expands numeric body-cell matching context to include `table.heading_text`, `table.table_caption_or_nearby_heading`, `cell.row_label_path`, and `cell.column_header_path`, while still emitting only the selected cell text as `risk_disclosure_text`.
- Regression coverage now includes numeric cells authorized by row/header context, isolated numeric cells without same-role context, and caption-only same-role context.

Accepted closure evidence:

- `docs/reviews/code-review-20260620-191113.md` reports Finding 1 closed and verifies caption-only coverage.
- `docs/reviews/code-review-20260620-191158.md` reports Finding 1 closed and verifies isolated numeric cells remain missing.

### Codex Finding 2: stale control/design truth

Disposition: `accepted`, fixed, and re-reviewed closed.

Reason:

- `docs/current-startup-packet.md` and `docs/design.md` still had stale current-state wording that could route the controller back to implementation or imply the four roles remained unimplemented.
- The fix updates current control/design wording to local implementation complete, code review/re-review accepted, and preserves the boundaries: no parser replacement, no readiness/release, no `EvidenceSourceKind` expansion, no `StructuredFundDataBundle.core_risk`.

Accepted closure evidence:

- `docs/reviews/code-review-20260620-191113.md` reports Finding 2 closed.
- `docs/reviews/code-review-20260620-191158.md` reports Finding 2 closed.

### MiMo initial review

Disposition: `accepted as initial input, superseded by Codex accepted findings and later targeted re-reviews`.

Reason:

- `docs/reviews/code-review-20260620-184943.md` did not report blockers, but it predated the final caption-only follow-up fix and contains earlier validation counts.
- It remains useful as review-chain evidence but is not the controlling acceptance artifact.

## Controller Validation

Controller re-ran the required local validation after the final fix:

```text
uv run pytest tests/fund/processors/test_fund_disclosure_processor.py -q -k core_risk
31 passed, 167 deselected

uv run pytest tests/fund/processors/test_fund_disclosure_processor.py -q
198 passed

uv run pytest tests/fund/test_data_extractor.py -q
43 passed

uv run ruff check fund_agent/fund/processors/fund_disclosure_processor.py fund_agent/fund/data_extractor.py tests/fund/processors/test_fund_disclosure_processor.py tests/fund/test_data_extractor.py
All checks passed!

git diff --check -- fund_agent/fund/processors/fund_disclosure_processor.py tests/fund/processors/test_fund_disclosure_processor.py tests/fund/test_data_extractor.py docs/design.md docs/current-startup-packet.md docs/implementation-control.md fund_agent/fund/README.md docs/reviews/funddisclosuredocument-core-risk-deferred-roles-source-truth-extraction-implementation-evidence-20260620.md
clean
```

## Accepted Implementation Facts

- Proof-positive `core_risk.v1` source-truth direct extraction now emits all five required subvalues when available:
  - `risk_characteristic_text`
  - `liquidation_or_scale_risk`
  - `tracking_error_or_deviation_risk`
  - `turnover_or_style_drift_risk`
  - `concentration_risk`
- The four role subvalues use processor-local `core_risk_role_disclosure.v1` shape.
- Role subvalues do not embed source anchors; public anchors remain on `FundFieldFamilyResult.anchors`.
- Missing roles fail closed as `field_family_partial`; conflicting role candidates fail closed as `ambiguous_table_or_locator`.
- Proof-positive direct paths suppress candidate evidence.
- No `StructuredFundDataBundle.core_risk` was added, and existing bundle projection remains limited to the accepted `risk_characteristic_text` fallback.
- No parser replacement, real-report field correctness, full field correctness, golden/readiness, release, PR mark-ready or merge is proven.

## Residual Risks

- Real-report correctness remains unproven and must stay in later evidence/readiness gates.
- Token breadth and numeric-cell matching remain bounded by source-truth admission, stable body-cell requirements, same-role context, heading-only rejection and ambiguity fail-closed behavior; real-report regression evidence is still a later gate.
- PR 34 metadata, CI and external state were not changed by this local gate.

## Next Gate

`FundDisclosureDocument core_risk.v1 Deferred Risk Roles Source-truth Direct Extraction Accepted Slice Commit Gate`.
