# FundDisclosureDocument investor_experience.v1 Source-truth Direct Extraction Implementation Evidence

## Gate Metadata

- Work unit: `FundDisclosureDocument investor_experience.v1 Source-truth Direct Extraction`
- Gate: Implementation Gate
- Role: AgentCodex implementation worker only
- Branch: `funddisclosure-investor-experience-source-truth`
- Accepted plan commit: `1bf4187`
- Accepted plan artifact: `docs/reviews/funddisclosuredocument-investor-experience-source-truth-extraction-plan-20260620.md`
- Controller judgment: `docs/reviews/funddisclosuredocument-investor-experience-source-truth-extraction-plan-controller-judgment-20260620.md`
- Artifact path: `docs/reviews/funddisclosuredocument-investor-experience-source-truth-extraction-implementation-evidence-20260620.md`

## Changed Files

- `fund_agent/fund/processors/fund_disclosure_processor.py`
- `tests/fund/processors/test_fund_disclosure_processor.py`
- `tests/fund/test_data_extractor.py`
- `fund_agent/fund/README.md`
- `docs/design.md`
- `docs/reviews/funddisclosuredocument-investor-experience-source-truth-extraction-implementation-evidence-20260620.md`

No changes were made to `contracts.py`, `data_extractor.py`, `extractors/**`, `documents/**`, `services/**`, `ui/**`, `host/**`, or `agent/**`.

## Implementation Summary

- Added proof-positive `investor_experience.v1` FDD source-truth direct extraction inside `FundDisclosureDocumentProcessor`.
- Public `investor_experience.v1.value` is limited to:
  - `schema_version`
  - `investor_return`
  - `holder_structure`
  - `share_change`
- `subscription_redemption` and `income_distribution` remain candidate-only roles and are not emitted as public subvalues.
- Proof-positive direct route returns `candidate_evidence=()` for `investor_experience.v1`, including direct-route missing.
- Proof-missing / proof-invalid / candidate-boundary paths keep public missing semantics and do not promote candidate evidence.
- `current_stage.v1` and `core_risk.v1` source-truth extraction remains unimplemented; investor direct-route suppression does not clear their candidate evidence.
- No parser, repository, source/cache/PDF, Docling, pdfplumber, live/network/provider/LLM, `EvidenceSourceKind`, public `EvidenceAnchor`, or facade production code change was introduced.

## Validation

```text
uv run pytest tests/fund/processors/test_fund_disclosure_processor.py
174 passed in 0.57s
```

```text
uv run pytest tests/fund/test_data_extractor.py -k "disclosure_source_truth_investor_experience or disclosure_candidate_only_investor_experience"
2 passed, 37 deselected in 0.44s
```

Additional hygiene:

```text
uv run ruff check fund_agent/fund/processors/fund_disclosure_processor.py tests/fund/processors/test_fund_disclosure_processor.py tests/fund/test_data_extractor.py
All checks passed!
```

```text
git diff --check
passed
```

## Residual Risks

- Real-report correctness is not claimed; validation is fixture-backed and no live/PDF/provider/parser work was authorized.
- `investor_return` direct extraction intentionally accepts only explicit label/value disclosures with stable locators; report-specific wording outside the accepted labels remains fail-closed.
- `share_change` column selection is intentionally narrow: one non-label value column or exact fund-code header match only.
- `subscription_redemption` and `income_distribution` require a separate schema/public contract gate before they can become public subvalues.
- `current_stage.v1` and `core_risk.v1` remain separate future source-truth work units.

## Completion Status

Implementation Gate scope completed. No commit, push, PR mutation, mark-ready, merge, control-doc update, parser replacement, readiness, or release action was performed.
