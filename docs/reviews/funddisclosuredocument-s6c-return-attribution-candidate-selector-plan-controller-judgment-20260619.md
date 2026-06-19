# Controller Judgment: S6-C Return Attribution Candidate Selector Plan

## Gate

- Gate: `FundDisclosureDocument S6-C Single-family Candidate Evidence Selector Planning Gate`
- Classification: `heavy planning gate`
- Work unit type: feature slice inside the Fund Processor/Extractor route.

## Inputs Reviewed

- Plan: `docs/reviews/funddisclosuredocument-s6c-return-attribution-candidate-selector-plan-20260619.md`
- Plan review: `docs/reviews/plan-review-20260619-092340.md`
- Current control truth: `docs/implementation-control.md`
- Startup packet: `docs/current-startup-packet.md`
- Design truth: `docs/design.md` v2.23
- Accepted S6-A implementation judgment: `docs/reviews/funddisclosuredocument-s6a-candidate-evidence-contract-implementation-controller-judgment-20260619.md`
- Accepted S6-B implementation judgment: `docs/reviews/funddisclosuredocument-s6b-product-essence-candidate-selector-implementation-controller-judgment-20260619.md`

## Decision

`ACCEPT_S6C_RETURN_ATTRIBUTION_CANDIDATE_SELECTOR_PLAN_NOT_READY`

The S6-C plan is accepted for implementation. It selects exactly one remaining field family, `return_attribution.v1`, and keeps the implementation surface inside the Fund Processor/Extractor boundary as a candidate-only locator selector.

## Accepted Scope

The next implementation gate may:

- add a deterministic `return_attribution.v1` candidate locator selector;
- read only `FundDisclosureDocumentContentIntermediate` section, paragraph, table, and cell protocol fields;
- attach results only to `FundFieldFamilyResult.candidate_evidence`;
- keep `return_attribution.v1` public status as `missing`;
- keep `value={}` and `anchors=()`;
- add focused processor tests and update `fund_agent/fund/README.md` / `docs/design.md` current-state wording after code facts exist.

## Binding Guardrails

Implementation must preserve all of the following:

1. Exactly one new selector is allowed: `return_attribution.v1`.
2. `product_essence.v1` S6-B behavior and source path identity must remain unchanged.
3. Candidate evidence must remain `candidate_only`, `field_correctness_status="not_proven"`, `source_truth_status="not_proven"`, and `readiness_status="not_ready"`.
4. Candidate evidence must not populate `FundFieldFamilyResult.value`.
5. Candidate evidence must not create or satisfy public `EvidenceAnchor`.
6. `partial` and `accepted` statuses remain unauthorized.
7. `FundDataExtractor`, repository/source/cache/live code, Service/UI/Host, renderer, and quality gate code remain out of scope.
8. Numeric-looking candidate excerpts are allowed only as locator previews; they must not be parsed, copied, or interpreted as field values or field correctness.

## Plan Review Finding Disposition

### 001 numeric-looking excerpts can be mistaken for future field facts

- Disposition: `accepted`
- Controller action: bind candidate-only boundary and no-value-leak assertions in implementation tests.
- Reason: return/performance/fee/tracking-error locators may contain numeric-looking excerpts, but S6-C only authorizes locator evidence. Public value, anchors, field correctness, source truth, and readiness must all remain negative.

### 002 optional shared selector helper can accidentally alter S6-B ordering

- Disposition: `accepted`
- Controller action: implementation must keep or strengthen S6-B regression assertions for source path formatting and public-empty output.
- Reason: S6-B is an accepted checkpoint and S6-C must not reopen it through helper refactoring.

## Required Validation For Next Gate

```bash
uv run pytest tests/fund/processors/test_fund_disclosure_processor.py
uv run ruff check fund_agent/fund/processors/fund_disclosure_processor.py tests/fund/processors/test_fund_disclosure_processor.py
git diff --check
```

If docs are updated:

```bash
git diff --check -- fund_agent/fund/README.md docs/design.md
```

## Explicit Non-Readiness

This accepted plan does not prove source truth, field correctness, parser replacement, full coverage, golden/readiness, release, or upper-layer consumption. Release/readiness remains `NOT_READY`.

## Next Entry Point

`FundDisclosureDocument S6-C Return Attribution Candidate Selector Implementation Gate`
