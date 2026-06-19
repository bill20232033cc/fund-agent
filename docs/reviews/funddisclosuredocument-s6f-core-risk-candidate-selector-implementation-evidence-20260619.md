# FundDisclosureDocument S6-F Core Risk Candidate Selector Implementation Evidence

## Gate

- Gate: `FundDisclosureDocument S6-F Core Risk Candidate Selector Implementation Gate`
- Role: AgentCodex implementation worker only
- Scope: exactly one selector, `core_risk.v1`
- Verdict: implementation completed locally; release/readiness remains `NOT_READY`

## Changed Files

- `fund_agent/fund/processors/fund_disclosure_processor.py`
- `tests/fund/processors/test_fund_disclosure_processor.py`
- `fund_agent/fund/README.md`
- `docs/design.md`
- `docs/reviews/funddisclosuredocument-s6f-core-risk-candidate-selector-implementation-evidence-20260619.md`

## Contract Summary

- Implemented `_CORE_RISK_CANDIDATE_LIMIT = 16`.
- Implemented `core_risk.v1` candidate-only locator selector for five roles in order:
  - `risk_characteristic`
  - `liquidation_or_scale_risk`
  - `tracking_error_or_deviation_risk`
  - `turnover_or_style_drift_risk`
  - `concentration_risk`
- Source order is sections, paragraph blocks, table blocks, table cells.
- Cell scan order is `(row_index, column_index)` while `source_field_path` keeps original tuple index.
- Deduplication is family-local by exact `source_field_path`; no cross-family dedupe was added.
- Public family result remains `status="missing"`, `extraction_mode="missing"`, `value={}`, `anchors=()`.
- Candidate evidence is stored only in `FundFieldFamilyResult.candidate_evidence`.
- When candidate evidence exists, the local gap is `candidate_only_not_source_truth`.
- `current_stage.v1` remains fully missing and receives no candidate evidence.
- S6-B/S6-C/S6-D/S6-E helpers were not refactored into shared helpers.
- `_field_families_for_intermediate()` now uses a local `candidate_evidence_by_family` mapping and iterates `_FAMILY_ORDER`; no sixth nested ternary was added.
- Core-risk cell generic guard context is role-invariant and always excludes `cell_text` / `cell_text_normalized`.
- Chapter 6 reasoning/output tokens and S6-E-owned share-flow/distribution tokens are not S6-F match tokens.

## Validation

```bash
uv run pytest tests/fund/processors/test_fund_disclosure_processor.py
```

Result: passed, `79 passed in 0.44s`.

```bash
uv run ruff check fund_agent/fund/processors/fund_disclosure_processor.py tests/fund/processors/test_fund_disclosure_processor.py
```

Result: passed, `All checks passed!`.

```bash
git diff --check
```

Result: passed, no output.

```bash
git diff --check -- fund_agent/fund/README.md docs/design.md
```

Result: passed, no output.

## Test Coverage Added

- role positive matching
- boundary fields and public value/anchor leak prevention
- `current_stage.v1` unchanged
- no-match missing behavior
- candidate-boundary blocked behavior
- order, dedupe, limit, excerpt, and cell tuple-index path behavior
- broad-token negative generic guard cases
- generic tokens allowed with source context
- cell self-guard blocking
- Chapter 6 reasoning/output token blocking, including pure forbidden and forbidden-plus-legal-strong mixed case
- S6-E-owned token non-capture
- comparative overlap regression for S6-B/S6-C/S6-D/S6-E record count, source path order, gap semantics, value, and anchors

## Residual Risks

- Token false positives remain possible because locator matching does not prove semantic field correctness. Owner: later field-extraction/source-truth gate.
- `core_risk.v1` still does not prove pressure-test input sufficiency, risk level, veto status, structural/cyclical risk, final holding/replacement judgment, or "most fatal risk". Owner: later Chapter 6 extraction/analysis gate.
- Candidate excerpts can contain numeric-looking text, but they are not projected into `value` or `anchors`. Owner: later extractor/evidence gate if numeric field extraction is authorized.
- No comparator correctness against repository-loaded PDF, Docling, EID HTML render, or pdfplumber was attempted in this gate. Owner: deferred evidence/source-truth gates.

## Candidate-only / NOT_READY Statement

`core_risk.v1` evidence is candidate-only locator evidence. It remains `field_correctness_status="not_proven"`, `source_truth_status="not_proven"`, `parser_replacement_authorized=False`, and `readiness_status="not_ready"`. This implementation does not prove source truth, field correctness, parser replacement, golden/readiness, release readiness, PR readiness, upper-layer consumption, or Chapter 6 final judgment. Overall release/readiness remains `NOT_READY`.
