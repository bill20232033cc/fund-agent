# FundDisclosureDocument return_attribution.v1 Source-truth Direct Extraction Slice 2 Code Review Controller Judgment

## Gate Metadata

- Gate: `FundDisclosureDocument return_attribution.v1 Source-truth Direct Extraction Implementation Gate`
- Slice: `Slice 2: Value extraction`
- Classification: `heavy`
- Implementation evidence: `docs/reviews/funddisclosuredocument-return-attribution-source-truth-extraction-slice2-implementation-evidence-20260620.md`
- Code reviews:
  - `docs/reviews/code-review-20260620-065511-ds-return-attribution-source-truth-slice2.md`
  - `docs/reviews/code-review-20260620-065511-mimo-return-attribution-source-truth-slice2.md`
- Verdict: `ACCEPT_SLICE2_READY_FOR_SLICE3_ANCHOR_GAP_HARDENING_NOT_READY`

## Controller Decision

Slice 2 is accepted.

The implementation constructs public `return_attribution.v1` values from proof-positive FundDisclosureDocument content for the existing public keys `nav_benchmark_performance`, `fee_schedule`, and `tracking_error`. It keeps `candidate_evidence=()` on the direct route and preserves fail-closed behavior for no-match, partial, ambiguous, target/control tracking-error context, and candidate/proof-invalid paths.

The implementation necessarily includes basic public anchor and field-local gap behavior for non-missing `FundFieldFamilyResult` validity. These anchor/gap paths were reviewed in the Slice 2 code reviews. The next planned slice remains Slice 3 so the controller can keep a distinct hardening/review checkpoint for anchor/gap edge cases rather than silently closing that plan slice.

## Review Disposition

AgentDS returned `PASS` and AgentMiMo returned `PASS_WITH_FINDINGS`. No blocking finding was reported.

Accepted non-blocking findings:

1. Tracking-error candidate matching may use table-level context. This is accepted for the current slice because percent parsing, rejection context, and conflict resolution remain in place; future real-report evidence may refine it.
2. Ambiguous path and partial top-level gaps can both appear for the same missing output path. This is accepted as explanatory redundancy, not a contract violation.
3. No table-cell-specific tracking-error rejection test was added. Existing rejection logic is shared; Slice 3 may add a focused table-cell hardening test if useful.
4. Identical normalized values from different stable locators are deduped by value rather than locator identity. This is accepted as non-blocking because same-value multi-source disclosure is not a conflict; future evidence may revisit locator identity strictness.

No fix/re-review is required.

## Controller Validation

```text
uv run pytest tests/fund/processors/test_fund_disclosure_processor.py
133 passed in 0.83s

uv run ruff check fund_agent/fund/processors/fund_disclosure_processor.py tests/fund/processors/test_fund_disclosure_processor.py
All checks passed!

git diff --check -- fund_agent/fund/processors/fund_disclosure_processor.py tests/fund/processors/test_fund_disclosure_processor.py docs/reviews/funddisclosuredocument-return-attribution-source-truth-extraction-slice2-implementation-evidence-20260620.md docs/reviews/code-review-20260620-065511-ds-return-attribution-source-truth-slice2.md docs/reviews/code-review-20260620-065511-mimo-return-attribution-source-truth-slice2.md
PASS: no output
```

## Boundaries Preserved

- Exactly one field family: `return_attribution.v1`.
- No source-truth direct extraction for `manager_profile.v1`, `investor_experience.v1`, `current_stage.v1`, or `core_risk.v1`.
- No parser replacement.
- No `EvidenceSourceKind` / `EvidenceAnchor` / processor contract schema expansion.
- No `FundDocumentRepository`, source policy, fallback, cache, PDF, live/network, provider, LLM, manual reference, Docling conversion, or pdfplumber export work.
- No Service/UI/Host/renderer/quality-gate direct FDD candidate consumption.
- No real-report field correctness, full correctness, golden/readiness, release, PR, push, mark-ready, or merge claim.

## Next Entry Point

`FundDisclosureDocument return_attribution.v1 Source-truth Direct Extraction Implementation Gate - Slice 3 Anchor/Gap Hardening`

Slice 3 should treat the accepted Slice 2 anchor/gap behavior as current code and decide whether focused hardening tests or small cleanup are needed for table-cell tracking-error rejection, duplicate same-value locator handling, and ambiguous/partial gap reporting. It must not broaden field-family scope.
