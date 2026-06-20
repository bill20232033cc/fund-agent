# Code Review

## Scope

- Mode: current changes
- Branch: `funddisclosure-core-risk-source-truth`
- Base: `main`
- Output file: `docs/reviews/code-review-core-risk-source-truth-mimo-20260620.md`
- Included scope: all workspace unstaged changes (no staged changes); 7 files changed: `fund_agent/fund/processors/fund_disclosure_processor.py`, `tests/fund/processors/test_fund_disclosure_processor.py`, `tests/fund/test_data_extractor.py`, `docs/design.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md`, `fund_agent/fund/README.md`
- Excluded scope: `fund_agent/fund/processors/contracts.py`, `fund_agent/fund/processors/active_annual.py`, `fund_agent/fund/data_extractor.py` (production), `docs/fund-analysis-template-draft.md`, Service/UI/Host/Agent/renderer/quality-gate files
- Parallel review coverage: 无
- Accepted plan: `docs/reviews/funddisclosuredocument-core-risk-source-truth-extraction-plan-20260620.md` (commit `75cd23d`)
- Implementation evidence: `docs/reviews/funddisclosuredocument-core-risk-source-truth-extraction-implementation-evidence-20260620.md`

## Findings

未发现实质性问题。

## Review Verification Walk-through

### Source-truth admission proof

`_field_families_for_intermediate()` (line 1006) gates `core_risk_source_truth` extraction behind `source_truth_extraction_allowed and content_intermediate is not None`, identical to all five prior source-truth families. The upstream admission chain (`_validate_source_truth_admission()`, `_admit_disclosure_intermediate()`) is unchanged. Proof-missing path retains candidate evidence and appends `source_truth_admission_missing`; proof-invalid path retains candidate evidence and appends `source_truth_admission_invalid`. Confirmed by tests `test_core_risk_source_truth_requires_positive_proof` and `test_core_risk_source_truth_rejects_invalid_proof`.

### candidate_boundary fail-closed

When `candidate_boundary` is non-null, `source_truth_extraction_allowed` is `False` upstream, so `_extract_core_risk_source_truth()` never runs. The result stays `contract_status="blocked"`, `family.status="missing"`, `family.value={}`, `family.anchors=()`. Candidate evidence for deferred roles (e.g., `liquidation_or_scale_risk`) remains present when matching source text exists. Confirmed by test `test_core_risk_source_truth_candidate_boundary_remains_blocked`.

### No `_select_product_essence_values` call from core_risk

Call chain: `_extract_core_risk_source_truth()` → `_select_core_risk_values()` → `_select_risk_characteristic_value()` → `_collect_risk_characteristic_table_candidates()` / `_collect_risk_characteristic_paragraph_candidates()` / `_resolve_risk_characteristic_candidate()`. No call to `_select_product_essence_values()` or any product-essence-specific collection/selection helper. Confirmed by code walk-through of all core_risk functions (lines 4662-4811).

### Neutral risk-characteristic helper correctness

`_select_risk_characteristic_value()` collects only `_RISK_CHARACTERISTIC_OUTPUT_PATH` = `"risk_characteristic_text.risk_characteristic_text"`. Table candidate collection (`_collect_risk_characteristic_table_candidates`) uses `_PRODUCT_ESSENCE_LABELS[_RISK_CHARACTERISTIC_OUTPUT_PATH]` for label matching and `_PRODUCT_ESSENCE_GENERIC_CELL_TEXTS` for generic text filtering. Paragraph candidate collection (`_collect_risk_characteristic_paragraph_candidates`) uses the same label/generic-text filtering. Neither collects product identity, benchmark, fee, tracking-error, turnover, holdings, holder-structure, or other product-essence values. The helper returns `_RiskCharacteristicValueCandidate`, not `_ProductEssenceValueCandidate`.

### product_essence shape preservation

`_select_product_essence_values()` (line 3754) now delegates risk-characteristic selection to `_select_risk_characteristic_value()` and wraps the result into `_ProductEssenceValueCandidate` with the same four fields (`output_path`, `value`, `anchor`, `source_field_path`). The table/paragraph candidate collectors explicitly skip `_RISK_CHARACTERISTIC_OUTPUT_PATH` to avoid duplicate collection. `_build_product_essence_value()` (line 4390) calls `_build_risk_characteristic_text_value()` which produces the exact same dict shape as the previous inline construction: `schema_version`, `fund_code`, `report_year`, `risk_characteristic_text`, `source_anchors`. Focused product_essence test suite passes: 25 passed, 163 deselected.

### Direct candidate_evidence suppression

`core_risk_evidence` (line 1051) is `()` when `core_risk_source_truth is not None`. `_extract_core_risk_source_truth()` always sets `candidate_evidence=()` on the returned `FundFieldFamilyResult` (line 1224). This applies to both accepted and missing direct results. Confirmed by tests `test_core_risk_source_truth_extracts_risk_characteristic_text_only` (candidate_evidence == ()) and `test_core_risk_source_truth_direct_missing_suppresses_candidate_evidence` (candidate_evidence == ()).

### Four required=False deferred_role gaps

`_CORE_RISK_DEFERRED_ROLES` (line 64) contains exactly `liquidation_or_scale_risk`, `tracking_error_or_deviation_risk`, `turnover_or_style_drift_risk`, `concentration_risk`. `_core_risk_source_truth_gaps()` emits one `FundExtractionGap(gap_code="deferred_role", required=False)` per role when `value` is non-empty. The test `test_core_risk_source_truth_extracts_risk_characteristic_text_only` asserts exactly four deferred_role gaps with `required=False` and correct `source_field_path` values.

### Ambiguity behavior

`_resolve_risk_characteristic_candidate()` adds the output path to `ambiguous_paths` when normalized candidate values differ. `_build_core_risk_value()` returns `{}` when no selected value exists. `_core_risk_status({})` returns `"missing"`. `_core_risk_source_truth_gaps({}, {"risk_characteristic_text.risk_characteristic_text"})` emits `gap_code="ambiguous_table_or_locator"` with `required=True`. Confirmed by test `test_core_risk_source_truth_ambiguous_text_returns_missing`.

### Facade fallback no production data_extractor edit

`git diff -- fund_agent/fund/data_extractor.py` produces no output. The existing fallback at `data_extractor.py:742-754` (`core_risk.v1 -> risk_characteristic_text` with `note="fallback_from_core_risk.v1"`) is first activated by the new direct extraction. Facade tests confirm: `test_explicit_disclosure_core_risk_fallback_projects_risk_text_only` (fallback activates, no `bundle.core_risk`) and `test_explicit_disclosure_product_risk_text_wins_over_core_risk_fallback` (product essence owns when both present).

### Docs truth sync

- `docs/design.md` v2.32→v2.33: status补充 and 变更摘要 updated to list `core_risk.v1` as having FDD source-truth direct extraction, covering only `risk_characteristic_text`, with deferred roles as `required=False` gaps. S2 description updated.
- `docs/implementation-control.md`: 最新控制更新, Current Truth Guardrails, and Active Gate table all updated to reflect core_risk implementation gate completion.
- `docs/current-startup-packet.md`: Current active gate, gate classification, current gate input, and next entry point all updated.
- `fund_agent/fund/README.md`: All three relevant sections updated with core_risk source-truth direct extraction facts, deferred role gaps, and no `StructuredFundDataBundle.core_risk`.

All docs correctly state: only `risk_characteristic_text` is admitted; deferred roles are `required=False` gaps; no `StructuredFundDataBundle.core_risk`; direct `candidate_evidence` is empty; no parser replacement/readiness/release claim.

### Forbidden files/contracts/schema checks

- `contracts.py`: no changes (git diff empty)
- `active_annual.py`: no changes
- `data_extractor.py` production: no changes
- No `EvidenceSourceKind` or `EvidenceAnchor` expansion
- No Service/UI/Host/Agent/renderer/quality-gate edits
- No parser replacement, readiness, or release claims
- Ruff lint: all checks passed
- `git diff --check`: no issues

### Test coverage

- 188 processor tests pass (including 7 new core_risk source-truth tests)
- 42 facade tests pass (including 2 new core_risk fallback tests)
- 25 product_essence focused tests pass (refactoring verification)
- Tests cover: positive extraction, direct missing, ambiguous text, proof missing, proof invalid, candidate boundary, candidate suppression, forbidden keys, non-interference, facade fallback, product-essence-wins priority

## Open Questions

无

## Residual Risk

- Complete `core_risk.v1` source truth (four deferred roles) remains deferred to later independent gates.
- This gate does not prove real-report correctness, parser replacement, full field correctness, golden/readiness, or release.
- The binary `accepted | missing` status model is intentional for single-subvalue gate; later multi-subvalue gate must redesign `_core_risk_status()`.

## Verdict

CODE_REVIEW_PASS
