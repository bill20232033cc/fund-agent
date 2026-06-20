# Aggregate Deepreview: FundDisclosureDocument investor_experience.v1 Source-truth Direct Extraction

## Gate Metadata

- Work unit: `FundDisclosureDocument investor_experience.v1 Source-truth Direct Extraction`
- Gate: Aggregate Deepreview Gate
- Role: AgentDS aggregate deepreviewer only
- Branch: `funddisclosure-investor-experience-source-truth`
- Review range: `git diff 1bf4187..HEAD`, current HEAD `8dac1fc`
- Accepted plan: `docs/reviews/funddisclosuredocument-investor-experience-source-truth-extraction-plan-20260620.md`
- Controller judgment (plan): `docs/reviews/funddisclosuredocument-investor-experience-source-truth-extraction-plan-controller-judgment-20260620.md`
- Implementation evidence: `docs/reviews/funddisclosuredocument-investor-experience-source-truth-extraction-implementation-evidence-20260620.md`
- Code reviews:
  - DS: `docs/reviews/code-review-investor-experience-source-truth-ds-20260620.md`
  - MiMo: `docs/reviews/code-review-investor-experience-source-truth-mimo-20260620.md`
- Fix evidence: `docs/reviews/funddisclosuredocument-investor-experience-source-truth-extraction-fix-evidence-20260620.md`
- MiMo re-review: `docs/reviews/code-rereview-investor-experience-source-truth-mimo-20260620.md`
- Code review controller judgment: `docs/reviews/funddisclosuredocument-investor-experience-source-truth-extraction-code-review-controller-judgment-20260620.md`
- Artifact path: `docs/reviews/funddisclosuredocument-investor-experience-source-truth-extraction-aggregate-deepreview-ds-20260620.md`

## Verdict

**AGGREGATE_DEEPREVIEW_PASS**

No blocking finding. All scope items verified end-to-end. Implementation exactly covers the accepted plan: proof-positive `investor_experience.v1` source-truth direct extraction for `investor_return`, `holder_structure`, and `share_change` only. `subscription_redemption` and `income_distribution` remain candidate-only; `current_stage.v1` and `core_risk.v1` remain unimplemented and unaffected. No forbidden files, architecture boundary violations, or overclaims in docs/control truth.

## Findings

Findings ordered by severity. No blocking finding.

## Scope Verification Matrix

### S1 — Proof-positive investor_experience.v1 direct extraction exists only for investor_return, holder_structure, share_change

**Result: PASS**

Evidence:
- `fund_agent/fund/processors/fund_disclosure_processor.py`: `_INVESTOR_EXPERIENCE_REQUIRED_TOP_LEVEL` constant contains exactly `("investor_return", "holder_structure", "share_change")` (diff line `+_INVESTOR_EXPERIENCE_REQUIRED_TOP_LEVEL`)
- `_build_investor_experience_value()` iterates only these three keys: `for top_level in _INVESTOR_EXPERIENCE_REQUIRED_TOP_LEVEL` (diff line `+1255`)
- `_investor_experience_status()` checks all three keys present for `"accepted"`: `if all(top_level in value for top_level in _INVESTOR_EXPERIENCE_REQUIRED_TOP_LEVEL)` (diff line `+1360`)
- `_investor_experience_source_truth_gaps()` adds partial gaps only for missing top-level keys: `top_level for top_level in _INVESTOR_EXPERIENCE_REQUIRED_TOP_LEVEL if top_level not in value` (diff line `+1318`)
- `grep subscription_redemption \| income_distribution` on processor diff returns zero matches — neither term appears in any added public value emission path
- Tests `test_investor_experience_source_truth_extracts_exact_value_shape` and `test_explicit_disclosure_source_truth_investor_experience_projects_to_bundle` confirm `value` dict contains only `schema_version`, `investor_return`, `holder_structure`, `share_change`

### S2 — subscription_redemption and income_distribution remain candidate-only and never public values

**Result: PASS**

Evidence:
- `grep -n "subscription_redemption\|income_distribution"` on the processor diff (`1bf4187..HEAD`) returns no output — neither term appears in any added code
- `docs/design.md` v2.31 (line `+**状态补充**`): `subscription_redemption 和 income_distribution 仍只作为 candidate locator roles，不进入 public value`
- `docs/design.md` v2.31 summary table row: `subscription_redemption 与 income_distribution 仍只作为 investor_experience.v1 candidate locator roles，不是 public source-truth subvalues`
- `fund_agent/fund/README.md`: `subscription_redemption 和 income_distribution 仍只作为 investor_experience.v1 candidate locator roles，不是 public source-truth subvalues`
- Existing S6-E candidate selector `_select_investor_experience_candidate_evidence()` is unchanged except for the suppression path when direct route is active

### S3 — proof-missing, proof-invalid, candidate-boundary stay public missing and candidate-only where applicable

**Result: PASS**

Evidence:
- `_field_families_for_intermediate` (diff `@@ -900,7 +995,11 @@`): `investor_experience_evidence = () if investor_experience_source_truth is not None else _select_investor_experience_candidate_evidence(intermediate)` — when no direct result, candidate selector still runs
- Direct extractor called only under `source_truth_extraction_allowed and content_intermediate is not None` (diff `@@ -884,6 +976,9 @@`)
- When `source_truth_extraction_allowed=False`, the candidate selector path is unchanged; `_with_source_truth_admission_gap()` appends `source_truth_admission_missing` or `source_truth_admission_invalid`
- `candidate_boundary is not None` is blocked by existing `_validate_source_truth_admission()` behavior — no new bypass was introduced
- Tests: `test_investor_experience_source_truth_requires_proof_even_when_candidate_boundary_none` (proof-missing), `test_investor_experience_source_truth_rejects_base_admission_invalid_paths` (provenance/failure_class), `test_investor_experience_source_truth_candidate_boundary_remains_blocked` (candidate-boundary) — all present and passing

### S4 — direct route candidate_evidence is empty

**Result: PASS**

Evidence:
- `_extract_investor_experience_source_truth()` returns `candidate_evidence=()` in all branches:
  - Missing: `candidate_evidence=()` (diff line `+193`)
  - Non-missing with values: `candidate_evidence=()` (in `FundFieldFamilyResult` construction)
- `_field_families_for_intermediate`: `investor_experience_evidence = () if investor_experience_source_truth is not None` — candidate evidence suppressed tuple, not just overridden
- Test `test_investor_experience_source_truth_route_suppresses_candidate_evidence` directly asserts `candidate_evidence == ()`

### S5 — current_stage.v1 and core_risk.v1 remain unimplemented and unaffected

**Result: PASS**

Evidence:
- `_field_families_for_intermediate` (diff): `current_stage_evidence = _select_current_stage_candidate_evidence(intermediate)` — called unconditionally, not gated on investor_experience
- `_field_families_for_intermediate` (diff): `core_risk_evidence = _select_core_risk_candidate_evidence(intermediate)` — called unconditionally
- No direct extractors named `_extract_current_stage_source_truth` or `_extract_core_risk_source_truth` exist in the diff
- Test `test_investor_experience_source_truth_does_not_populate_stage_or_risk` verifies stage/risk candidate evidence is non-empty when matching content exists, confirming non-interference with investor direct route
- `docs/design.md`: `current_stage.v1 和 core_risk.v1 的 FDD source-truth extraction 仍未实现，保持 public missing`
- `fund_agent/fund/README.md`: `current_stage.v1 和 core_risk.v1 的 FDD source-truth extraction 仍未实现，保持 public missing`

### S6 — facade projection only maps the three accepted keys

**Result: PASS**

Evidence:
- `fund_agent/fund/data_extractor.py` (production) was NOT changed — only `tests/fund/test_data_extractor.py` (test) changed
- `_active_processor_result_to_bundle()` already maps `investor_experience.v1.value` to `bundle.investor_return`, `bundle.holder_structure`, `bundle.share_change` via existing generic field projection logic
- Test `test_explicit_disclosure_source_truth_investor_experience_projects_to_bundle` verifies proof-positive FDD intermediate correctly projects all three bundle fields with `extraction_mode="direct"`, non-empty values, and annual-report anchors
- Test `test_explicit_disclosure_candidate_only_investor_experience_stays_missing` verifies proof-missing input keeps bundle fields `None` with empty anchors

### S7 — docs/control truth are accurate and do not overclaim

**Result: PASS**

Evidence:
- `docs/design.md` v2.31: correctly adds `investor_experience.v1` to the source-truth direct extraction list; explicitly limits scope to three keys; keeps `subscription_redemption`/`income_distribution` as candidate-only; keeps `current_stage.v1`/`core_risk.v1` as unimplemented; preserves `candidate_only/not_proven/NOT_READY` for candidate evidence; does not claim parser replacement, real-report correctness, golden/readiness, or release
- `docs/design.md` v2.31 Processor/Extractor table row: added `investor_experience.v1` coverage; kept `current_stage.v1`/`core_risk.v1` as residual
- `fund_agent/fund/README.md`: identity-parallel update — lists `investor_experience.v1` in source-truth coverage; states three-key limitation and candidate-only roles; states `current_stage.v1`/`core_risk.v1` remain missing
- `docs/implementation-control.md`: active gate updated to code review accepted state; next entry point set to aggregate deepreview; no overclaims introduced
- `docs/current-startup-packet.md`: updated current active gate and next entry point; no deviation from controller judgment

### S8 — no forbidden files or architecture boundary violations

**Result: PASS**

Changed files (13 total):
- `fund_agent/fund/processors/fund_disclosure_processor.py` — allowed (processor implementation)
- `tests/fund/processors/test_fund_disclosure_processor.py` — allowed (processor tests)
- `tests/fund/test_data_extractor.py` — allowed (facade regression tests only)
- `fund_agent/fund/README.md` — allowed (triggered by fund/ changes per AGENTS.md)
- `docs/design.md` — allowed (docs sync)
- `docs/implementation-control.md` — allowed (control sync)
- `docs/current-startup-packet.md` — allowed (startup packet sync)
- 6 review artifacts under `docs/reviews/` — allowed (evidence chain)

Files NOT changed (confirmed):
- `fund_agent/fund/processors/contracts.py`
- `fund_agent/fund/data_extractor.py` (production)
- `fund_agent/fund/extractors/**`
- `fund_agent/fund/documents/**`
- `fund_agent/services/**`
- `fund_agent/ui/**`
- `fund_agent/host/**`
- `fund_agent/agent/**`
- Any renderer, quality gate, repository/source/cache/PDF/Docling/pdfplumber/provider/LLM/live/network modules

No parser replacement, `EvidenceSourceKind` expansion, public `EvidenceAnchor` expansion, or Service/UI/Host/renderer/quality-gate consumption was introduced.

## Validation Results (Reproduced)

| Command | Result |
|---|---|
| `uv run pytest tests/fund/processors/test_fund_disclosure_processor.py` | 175 passed in 0.90s |
| `uv run pytest tests/fund/test_data_extractor.py -k disclosure_source_truth_investor_experience` | 1 passed, 38 deselected in 0.38s |
| `uv run ruff check fund_agent/fund/processors/fund_disclosure_processor.py tests/fund/processors/test_fund_disclosure_processor.py tests/fund/test_data_extractor.py` | All checks passed |
| `git diff --check 1bf4187..HEAD` | Passed (no output) |

## Prior Finding Disposition Verification

| Finding | Source | Disposition | Aggregate verification |
|---|---|---|---|
| DS F1: `无` single-char unavailable check scope | DS code review | rejected-with-reason by controller | No functional gap — percent match fails on standalone `无` anyway. Accepted as LOW non-blocking. |
| DS F2: `single_value_column` test merged into broader test | DS code review | accepted, fixed | Now has dedicated `test_investor_experience_source_truth_share_change_selects_single_value_column` test; confirmed by MiMo re-review TARGETED_CODE_REREVIEW_PASS. |
| DS F3: unavailable wording before label edge | DS code review | deferred-with-owner | Not a current blocker; edge case would require real fixture evidence to justify hardening. |
| MiMo F1: missing dedicated `single_value_column` test | MiMo code review | accepted, fixed | Same as DS F2 — fixed by dedicated test in fix gate. |
| MiMo obs 1: dead code `row_index < 0` | MiMo code review | harmless, no action | Not a security/correctness issue. |

No prior finding was left unresolved or without proper disposition. No new findings were introduced by the fix gate.

## Contract Test Coverage

All 18 plan-required processor tests present (17 initial + 1 fix-gate addition). All 2 plan-required facade tests present. Coverage matrix:

| Path | Test | Status |
|---|---|---|
| Proof-positive, all 3 subvalues | `extracts_exact_value_shape` | PASS |
| Proof-positive, partial | `partial_when_required_groups_missing` | PASS |
| Proof-positive, direct-route missing | `route_suppresses_candidate_evidence` | PASS |
| Proof-positive, candidate-only content | `missing_when_no_allowed_public_labels` | PASS |
| Proof-missing | `requires_proof_even_when_candidate_boundary_none` | PASS |
| Proof-invalid (provenance/failure_class) | `rejects_base_admission_invalid_paths` | PASS |
| Candidate-boundary | `candidate_boundary_remains_blocked` | PASS |
| Ambiguous direct return | `ambiguous_duplicate_omits_conflicting_value` | PASS |
| Ambiguous estimated return | `estimated_investor_return_conflict_omits_value` | PASS |
| Ambiguous share_change column | `share_change_rejects_ambiguous_share_class_columns` | PASS |
| Estimated-only return | `estimated_investor_return_only` | PASS |
| Paragraph label/value pattern | `investor_return_paragraph_requires_label_value_pattern` | PASS |
| Placeholder filtering | `holder_structure_filters_placeholder_values` | PASS |
| Label column exclusion | `share_change_excludes_label_column` | PASS |
| Single value column | `share_change_selects_single_value_column` | PASS |
| Fund code header match | `share_change_selects_exact_fund_code_column` | PASS |
| Net change calculation | `share_change_calculates_net_change` | PASS |
| Stage/risk non-interference | `does_not_populate_stage_or_risk` | PASS |

## Residual Risks

- Real-report correctness is not claimed; all validation is fixture-backed. No live/PDF/provider/parser work was authorized.
- `investor_return` direct extraction intentionally accepts only explicit label/value disclosures. Report-specific wording outside accepted labels remains fail-closed.
- `share_change` column selection is intentionally narrow (one non-label value column or exact fund-code header match). Real-report share-class tables with more complex structures may fail-closed.
- `subscription_redemption` and `income_distribution` require a separate schema/public contract gate before they can become public subvalues.
- `current_stage.v1` and `core_risk.v1` remain separate future source-truth work units.
- Release/readiness remains `NOT_READY`. PR #31 remains draft/open and was not marked ready, merged, or mutated by this work unit.
