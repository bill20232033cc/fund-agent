# FundDisclosureDocument S6-E Investor Experience Candidate Selector Implementation Evidence

## Gate

- Gate: `FundDisclosureDocument S6-E Investor Experience Candidate Selector Implementation Gate`
- Work unit: `Docling architecture reorientation / Fund Processor-Extractor route`
- Scope: implement exactly one new field-family selector, `investor_experience.v1`
- Worker role: implementation worker only

## Changed Files

- `fund_agent/fund/processors/fund_disclosure_processor.py`
- `tests/fund/processors/test_fund_disclosure_processor.py`
- `fund_agent/fund/README.md`
- `docs/design.md`
- `docs/reviews/funddisclosuredocument-s6e-investor-experience-candidate-selector-implementation-evidence-20260619.md`

## Implementation Summary

- Added `_INVESTOR_EXPERIENCE_CANDIDATE_LIMIT = 16`.
- Added `_INVESTOR_EXPERIENCE_MATCH_GROUPS`.
- Added a deterministic `investor_experience.v1` candidate-only selector.
- Preserved role order:
  - `investor_return`
  - `holder_structure`
  - `share_change`
  - `subscription_redemption`
  - `income_distribution`
- Preserved source order within each role:
  - `sections`
  - `paragraph_blocks`
  - `table_blocks`
  - `table_blocks[*].cells`
- Preserved stable source paths:
  - `sections[i]`
  - `paragraph_blocks[i]`
  - `table_blocks[i]`
  - `table_blocks[i].cells[j]`
- Cell scan order sorts by `(row_index, column_index)` while `source_field_path` keeps the original tuple index.
- Dedupe is family-local by exact `source_field_path`; same-path first-record-wins remains accepted.
- Candidate records are limited to 16 and reuse the existing 160-character excerpt limit.
- `investor_experience.v1` remains public `status="missing"`, `extraction_mode="missing"`, `value={}`, `anchors=()`.
- Candidate evidence is written only to `FundFieldFamilyResult.candidate_evidence`.
- No `EvidenceAnchor`, `EvidenceSourceKind`, `FundDataExtractor` facade, repository/source/cache/live/LLM/renderer/quality gate/Service/UI/Host changes were made.
- `current_stage.v1` and `core_risk.v1` remain fully missing with empty candidate evidence.
- Existing S6-B/S6-C/S6-D traversal and semantics were not refactored.

## Controller Binding Amendments

- `subscription_redemption` generic tokens `申购`, `赎回`, `净申购`, `净赎回` do not pass solely because the same cell text contains `份额` or `基金份额`.
- `subscription_redemption` generic guard tokens exclude standalone `份额` and standalone `基金份额`.
- Accepted actual-flow/share-change guard context is limited to narrower tokens such as `份额变动`, `基金份额变动`, `基金份额总额变动`, `基金总申购`, `基金总赎回`, `总申购份额`, `总赎回份额`, and `申购赎回`.
- For `subscription_redemption` cell records, generic guard context excludes `cell_text_normalized` and `cell_text`; it uses parent table heading/caption/path plus row labels, column headers, and cell heading path.
- Negative tests cover `申购份额` and `申购份额的计算方式` under fee/unrelated context.
- `income_distribution` remains candidate-only and does not create a public field.
- `_stub()`-based satisfied/candidate-boundary tests keep their expectations unchanged because `_stub()` is content-free and does not enter selector logic.

## Focused Test Coverage

- Adds candidate evidence only for `investor_experience.v1`.
- Preserves candidate boundary fields: `candidate_only`, `not_proven`, `not_ready`, and no value leak.
- Keeps other field families untouched for investor-experience-only content.
- Keeps `field_family_missing` for no-match content.
- Preserves result-level blocked status for candidate-boundary input.
- Verifies role order, source order, path dedupe, 16-record limit, excerpt truncation, and cell original-index source path.
- Verifies generic guard negative and positive cases.
- Verifies S6-C/S6-D-owned tokens do not populate `investor_experience.v1`.
- Verifies subscription/redemption self-guard negative and source-level guard positive cases.

## Validation

```bash
uv run pytest tests/fund/processors/test_fund_disclosure_processor.py
```

Result: `67 passed`.

```bash
uv run ruff check fund_agent/fund/processors/fund_disclosure_processor.py tests/fund/processors/test_fund_disclosure_processor.py
```

Result: `All checks passed!`

```bash
git diff --check
```

Result: passed.

```bash
git diff --check -- fund_agent/fund/README.md docs/design.md
```

Result: passed.

## Docs Decision

- `docs/design.md` was updated from v2.25 to v2.26 to record S6-E as current code fact.
- `fund_agent/fund/README.md` was updated to describe S6-E current behavior and guard boundary.
- Both docs preserve candidate-only / not_proven / NOT_READY wording.
- Neither doc claims source truth, field correctness, parser replacement, readiness, release, public `EvidenceAnchor` expansion, or upper-layer consumption.

## Residual Risks

- Token matching remains locator-only and can still produce false positives; owner: later field-extraction/source-truth gate.
- `income_distribution` role labels may be suppressed by same-path first-record-wins when an earlier role matches the same source path; owner: future field-extraction/source-truth design.
- `investor_experience.v1` candidate evidence does not prove comparator correctness against repository-loaded PDF, Docling, EID HTML render, or pdfplumber; owner: deferred evidence/source-truth gates.
- `current_stage.v1` and `core_risk.v1` remain unimplemented; owner: later reviewed selector gates.

## Completion Status

Implementation, focused tests, docs sync, and evidence artifact are complete for this implementation-only gate.

Final boundary: `NOT_READY`. This implementation does not prove source truth, field correctness, parser replacement, full coverage, golden/readiness, release, PR readiness, or upper-layer consumption.
