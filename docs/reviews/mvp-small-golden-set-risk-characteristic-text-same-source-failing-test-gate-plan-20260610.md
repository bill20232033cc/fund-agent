# risk_characteristic_text.v1 same-source failing test gate plan

## 1. Gate Metadata

- Gate: `same-source failing risk test gate for risk_characteristic_text.v1`
- Classification: `standard`
- Controller baseline: branch `feat/mvp-llm-incomplete-run-artifacts`; latest accepted control sync `ac3c1be`
- Source of truth: `AGENTS.md`, `docs/current-startup-packet.md`, `docs/implementation-control.md`, accepted retained excerpt oracle `docs/reviews/mvp-small-golden-set-retained-excerpt-fixture-pdf-only-20260609.json`
- Current status: `portfolio_manager_tenure_list.v1` is a passing current extractor surface. `risk_characteristic_text.v1`, `bond_top_holding_row.v1` and `target_fund_holding_row.v1` remain future contracts.

## 2. Goal

Replace the generic `risk` unsupported-field xfail with a named, strict, same-source failing test for `risk_characteristic_text.v1` that internally checks all five accepted small-golden rows.

The test must prove a precise current gap: accepted same-source risk characteristic text exists in the retained oracle, but the current extractor surface has no dedicated `risk_characteristic_text.v1` output. This gate must not make the test pass.

## 3. Non-goals

- Do not modify production extractor code.
- Do not add `ProfileExtractionResult.risk_characteristic_text`.
- Do not treat `product_profile.style_positioning` as satisfying `risk_characteristic_text.v1`.
- Do not integrate risk text into `StructuredFundDataBundle`, snapshot, renderer, quality gate, report evidence, chapter facts, checklist, Service or Host.
- Do not read PDFs, call `FundDocumentRepository`, use cache/source helpers, invoke fallback, access network, run provider/live LLM, project fixtures, promote golden/readiness state, or change source/provider/runtime/config behavior.
- Do not touch bond or target ETF row-shape gates.

## 4. Direct Evidence

- `docs/current-startup-packet.md` and `docs/implementation-control.md` list the next valid entry as a same-source failing risk test gate for `risk_characteristic_text.v1`.
- The accepted row-shape decision records `risk_characteristic_text.v1` as a future contract and distinguishes retained `risk` from existing style-positioning semantics.
- `tests/fund/test_small_golden_set_extractor_correctness.py` currently has only `SAME_SOURCE_UNSUPPORTED_FIELDS = {"risk"}` and a generic xfail. It does not define the risk contract shape.
- The retained oracle has risk values for all accepted rows:
  - `004393`: mixed fund risk text plus Hong Kong Stock Connect risk.
  - `004194`: enhanced index higher-risk/higher-return text.
  - `006597`: bond fund lower-risk/lower-return text plus credit/liquidity control text.
  - `110020`: CSI 300 ETF feeder risk/return level text.
  - `017641`: overseas passive equity index risk text plus FX/special risks.
- `fund_agent/fund/extractors/profile.py` can extract `style_positioning` from labels such as `风险收益特征`, but that field is not a safe substitute for the accepted risk oracle because the retained risk text can include special risk clauses and operating-risk language.

## 5. Affected Files

Allowed implementation files:

- `tests/fund/test_small_golden_set_extractor_correctness.py`
- `tests/README.md`
- `docs/reviews/mvp-small-golden-set-risk-characteristic-text-same-source-failing-test-gate-*.md`

Allowed control sync files after accepted implementation:

- `docs/current-startup-packet.md`
- `docs/implementation-control.md`

No production `fund_agent/` file is in scope.

## 6. Contract Decisions For This Test Gate

This gate does not implement the production contract. It only freezes the failing-test expectation for a future extractor fix gate.

The future output surface expected by the test is:

```python
profile.risk_characteristic_text.value == {
    "schema_version": "risk_characteristic_text.v1",
    "fund_code": <accepted oracle fund_code>,
    "report_year": 2024,
    "risk_characteristic_text": <accepted oracle fields.risk.expected>,
    "source_anchors": <non-empty list>,
}
```

Additional expected field behavior:

- `risk_characteristic_text.extraction_mode == "direct"`
- `risk_characteristic_text.anchors` is non-empty.
- The value must come from the retained oracle row used to build the minimal parsed report.
- The test must fail today because `extract_profile(report)` returns no `risk_characteristic_text` attribute or equivalent dedicated output surface.

The test intentionally does not assert that `product_profile.style_positioning` equals the oracle risk text. Future implementation must either add a dedicated profile output field or route the accepted risk contract through an explicitly reviewed alternative surface.

## 7. Implementation Slices

### Slice 1: Replace generic risk xfail with named strict xfail

- Add `RISK_CONTRACT_VERSION = "risk_characteristic_text.v1"`.
- Remove `SAME_SOURCE_UNSUPPORTED_FIELDS = {"risk"}` and the generic unsupported-field xfail test.
- Add `_risk_expected_text(row)` helper that returns `fields.risk.expected` as text.
- Add `test_profile_extractor_exposes_same_source_risk_characteristic_text` marked `xfail(strict=True)`.
- The test must iterate over all five accepted fund codes inside one strict xfail case, so retained-row coverage is preserved while the accepted focused test summary remains `21 passed, 3 xfailed`.
- The test must build the same minimal report from the accepted oracle and call `extract_profile(report)`.
- The test must access the future dedicated surface `profile.risk_characteristic_text`, then assert schema version, fund code, report year, expected risk text and non-empty anchors.

Expected result: the test remains xfailed because the current extractor has no dedicated surface.

### Slice 2: Documentation alignment

- Update `tests/README.md` so the small-golden row-field correctness description names the remaining strict xfails: `risk_characteristic_text.v1`, `bond_top_holding_row.v1`, `target_fund_holding_row.v1`.
- Do not update package README files because no production module behavior changes.

## 8. Validation Matrix

Required commands:

```bash
uv run pytest tests/fund/test_small_golden_set_extractor_correctness.py -q
uv run pytest tests/fund/test_small_golden_set_manifest.py tests/fund/test_small_golden_set_fixture_shape.py tests/fund/test_small_golden_set_source_identity.py tests/fund/test_small_golden_set_parser_mechanics.py tests/fund/test_small_golden_set_extractor_correctness.py -q
uv run ruff check tests/fund/test_small_golden_set_extractor_correctness.py
git diff --check -- tests/fund/test_small_golden_set_extractor_correctness.py tests/README.md docs/reviews/mvp-small-golden-set-risk-characteristic-text-same-source-failing-test-gate-plan-20260610.md docs/reviews/plan-review-20260610-141151.md docs/reviews/mvp-small-golden-set-risk-characteristic-text-same-source-failing-test-gate-controller-judgment-20260610.md docs/reviews/mvp-small-golden-set-risk-characteristic-text-same-source-failing-test-gate-implementation-evidence-20260610.md docs/reviews/mvp-small-golden-set-risk-characteristic-text-same-source-failing-test-gate-code-review-20260610-*.md
```

Expected outcomes:

- Focused row-field correctness remains `21 passed, 3 xfailed`.
- Small-golden family remains `42 passed, 3 xfailed`.
- Ruff passes.
- Diff check passes.

## 9. Review Gates

- Plan review must challenge whether the test is too weak or accidentally allows `style_positioning` to satisfy `risk_characteristic_text.v1`.
- Code review must confirm:
  - no production code changed;
  - the risk xfail is contract-named and row-scoped over all five accepted rows;
  - the test consumes only the accepted retained oracle;
  - remaining xfail count is unchanged;
  - README wording matches the new explicit xfail state.

## 10. Stop Conditions

Stop before implementation if:

- plan review finds that the proposed future surface is too ambiguous for implementation;
- the test would pass by consuming `style_positioning`;
- a validation command requires PDF, repository, network, provider/live LLM or fallback access;
- tracked or untracked unrelated files would need to be staged.

Stop after implementation if:

- focused row-field correctness no longer reports exactly three strict xfails;
- the new risk test passes or XPASSes;
- validation fails for any reason not explained and accepted in a controller judgment.

## 11. Completion Report Format

Implementation evidence must report:

- files changed;
- exact test name added;
- validation commands and results;
- confirmation that no production extractor, source, fallback, provider/runtime/config, PDF/FDR/network, golden/readiness or downstream integration behavior changed;
- remaining next entries after the gate.
