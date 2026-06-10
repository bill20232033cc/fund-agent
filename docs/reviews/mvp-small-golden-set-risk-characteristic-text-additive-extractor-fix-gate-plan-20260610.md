# risk_characteristic_text.v1 additive extractor fix gate plan

## 1. Gate Metadata

- Gate: `risk_characteristic_text.v1 additive extractor fix gate`
- Classification: `heavy`
- Reason: this changes Fund extractor public behavior by adding a new `ProfileExtractionResult` output field. It does not change source policy, fallback, golden/readiness, provider/runtime/config, live/PDF/FDR behavior, or downstream bundle/report surfaces.
- Controller baseline: branch `feat/mvp-llm-incomplete-run-artifacts`; current accepted gate truth checkpoint `d1cd1ed`
- Source of truth: `AGENTS.md`, `docs/design.md`, `docs/current-startup-packet.md`, `docs/implementation-control.md`
- Accepted failing-test baseline: `4d01617`

## 2. Goal

Make the accepted `risk_characteristic_text.v1` same-source strict xfail pass by adding an additive, dedicated risk-characteristic output surface to `extract_profile()`.

The fix must preserve the accepted distinction:

- `risk_characteristic_text.v1` is exact retained risk-characteristic text.
- `product_profile.style_positioning` remains a product profile/style field and is not the acceptance surface for risk.

## 3. Non-goals

- Do not integrate the new field into `StructuredFundDataBundle`, data extractor, snapshot, score, quality gate, report evidence, chapter facts, renderer, checklist, Service, Host or Agent runtime.
- Do not change `product_profile.style_positioning` assertions or remove existing behavior.
- Do not derive risk text by trimming fund name out of `基金类型` or other indirect identity/category text.
- Do not read PDFs, call `FundDocumentRepository`, use cache/source helpers, invoke fallback, access network, run provider/live LLM, project fixtures, promote golden/readiness state, or change source/provider/runtime/config behavior.
- Do not work on `bond_top_holding_row.v1` or `target_fund_holding_row.v1`.

## 4. Direct Evidence

- `docs/current-startup-packet.md` and `docs/implementation-control.md` list `risk_characteristic_text.v1` additive extractor fix as a valid next entry.
- `docs/design.md` says retained `risk` maps to `risk_characteristic_text.v1`, must output exact retained oracle `fields.risk.expected` with source anchors, and is not `product_profile.style_positioning`.
- `tests/fund/test_small_golden_set_extractor_correctness.py` currently contains `test_profile_extractor_exposes_same_source_risk_characteristic_text` as a strict xfail. It builds five reports from the accepted retained oracle and expects `profile.risk_characteristic_text`.
- `fund_agent/fund/extractors/profile.py` currently has no dedicated risk-characteristic field. It can parse `风险收益特征` into `style_positioning`, which is insufficient as the accepted future contract surface.
- `ProfileExtractionResult` has a single production construction site: `extract_profile(report)`.

## 5. Affected Files

Implementation files:

- `fund_agent/fund/extractors/models.py`
- `fund_agent/fund/extractors/profile.py`
- `tests/fund/extractors/test_profile.py`
- `tests/fund/test_small_golden_set_extractor_correctness.py`
- `fund_agent/fund/README.md`
- `tests/README.md`
- `docs/reviews/mvp-small-golden-set-risk-characteristic-text-additive-extractor-fix-gate-*.md`

Control sync files after accepted implementation:

- `docs/current-startup-packet.md`
- `docs/implementation-control.md`

## 6. Contract Decisions

Add `ProfileExtractionResult.risk_characteristic_text: ExtractedField[dict[str, object]]`.

`risk_characteristic_text.value` must be:

```python
{
    "schema_version": "risk_characteristic_text.v1",
    "fund_code": report.key.fund_code,
    "report_year": report.key.year,
    "risk_characteristic_text": <directly extracted risk text>,
    "source_anchors": [
        {
            "section_id": <section id>,
            "page_number": <page number or None>,
            "table_id": <table id or None>,
            "row_locator": <row locator>,
        },
        ...
    ],
}
```

Extraction rules:

- Directly extract labels that explicitly mean risk characteristic, such as `风险收益特征`, from `§2` text or `§2` key-value tables.
- Reuse existing `EvidenceAnchor` mechanics for annual-report anchors.
- Preserve `product_profile.style_positioning` behavior for current callers.
- Missing risk-characteristic evidence returns `ExtractedField(value=None, anchors=(), extraction_mode="missing", note=...)`.
- The implementation may have the same underlying annual-report line/table populate both old `style_positioning` and new `risk_characteristic_text`; acceptance depends only on the dedicated new field.

Small-golden test builder rule:

- Add explicit `风险收益特征` content from accepted retained oracle `fields.risk.expected`.
- Do not satisfy the accepted test by parsing `基金类型` and removing the fund name.

## 7. Implementation Slices

### Slice 1: Model and extractor surface

- Add a `risk_characteristic_text` field to `ProfileExtractionResult`.
- Add `_RISK_CHARACTERISTIC_SCHEMA_VERSION = "risk_characteristic_text.v1"`.
- Add explicit field patterns/table labels for `risk_characteristic_text`.
- Add `_build_risk_characteristic_text(report)` that returns the schema above.
- Add source-anchor projection helper for the value-level `source_anchors`.
- Wire the builder into `extract_profile()`.

### Slice 2: Tests

- Remove the strict xfail marker from `test_profile_extractor_exposes_same_source_risk_characteristic_text`.
- Update the small-golden report builder to include explicit risk-characteristic content from the accepted oracle.
- Add focused profile unit tests:
  - table-based `风险收益特征` populates `risk_characteristic_text.v1` with schema, fund code, report year, text, value-level source anchor and `EvidenceAnchor`;
  - missing explicit risk-characteristic label returns missing;
  - existing builder order test accounts for the new risk builder.
- Keep focused small-golden result at `22 passed, 2 xfailed`.

### Slice 3: README alignment

- Update `fund_agent/fund/README.md` to list `risk_characteristic_text` as a current `extract_profile()` output.
- Update `tests/README.md` so remaining strict xfails are only `bond_top_holding_row.v1` and `target_fund_holding_row.v1`.

## 8. Validation Matrix

Required commands:

```bash
uv run pytest tests/fund/extractors/test_profile.py tests/fund/test_small_golden_set_extractor_correctness.py -q
uv run pytest tests/fund/test_small_golden_set_manifest.py tests/fund/test_small_golden_set_fixture_shape.py tests/fund/test_small_golden_set_source_identity.py tests/fund/test_small_golden_set_parser_mechanics.py tests/fund/test_small_golden_set_extractor_correctness.py -q
uv run pytest tests/fund/test_data_extractor.py -q
uv run ruff check fund_agent/fund/extractors/models.py fund_agent/fund/extractors/profile.py tests/fund/extractors/test_profile.py tests/fund/test_small_golden_set_extractor_correctness.py
git diff --check -- fund_agent/fund/extractors/models.py fund_agent/fund/extractors/profile.py tests/fund/extractors/test_profile.py tests/fund/test_small_golden_set_extractor_correctness.py fund_agent/fund/README.md tests/README.md docs/reviews/mvp-small-golden-set-risk-characteristic-text-additive-extractor-fix-gate-*.md docs/reviews/plan-review-20260610-145801.md
```

Expected outcomes:

- Focused profile + row-field tests pass.
- Small-golden family becomes `43 passed, 2 xfailed`.
- Data extractor stays compatible.
- Ruff passes.
- Diff check passes.

## 9. Review Gates

Plan review must challenge:

- whether this accidentally accepts `style_positioning` as the risk contract;
- whether the test builder uses indirect `基金类型` parsing;
- whether downstream integration is being smuggled into the extractor fix gate.

Code review must confirm:

- no FDR/PDF/network/source/fallback/provider/golden/readiness behavior changed;
- `risk_characteristic_text.v1` is a dedicated output field;
- accepted strict xfail was removed only after the dedicated test passes;
- remaining xfails are bond and target ETF only;
- README updates match code behavior.

## 10. Stop Conditions

Stop before implementation if:

- plan review finds the dedicated risk output surface is underspecified;
- implementation would require downstream bundle/report/snapshot integration;
- passing the small-golden test requires parsing `基金类型` as a risk proxy.

Stop after implementation if:

- the risk test still xfails;
- the focused small-golden test reports any xfail count other than two;
- data extractor compatibility fails;
- any command needs PDF/FDR/network/source/fallback/provider/live LLM.

## 11. Completion Report Format

Implementation evidence must report:

- files changed;
- new model/extractor/test behavior;
- exact validation commands and results;
- confirmation that no downstream integration or source/runtime/golden/readiness behavior changed;
- remaining next entries.
