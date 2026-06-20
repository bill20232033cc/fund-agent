# FundDisclosureDocument current_stage.v1 Source-truth Direct Extraction Plan

## Verdict

`PLAN_FIXED_READY_FOR_REVIEW`

## Goal, Motivation, Success Signal

Goal: implement exactly `current_stage.v1` proof-positive FundDisclosureDocument source-truth direct extraction inside `FundDisclosureDocumentProcessor`.

Motivation: controller confirmed `current_stage.v1` currently has only candidate-only locator evidence via `_select_current_stage_candidate_evidence`; it has no direct source-truth extractor and remains one of two missing FDD source-truth families. This work unit should close only the `current_stage.v1` processor-level direct extraction gap while preserving all proof-positive admission rules and public missing semantics.

Process state: controller has transitioned this branch to `current_stage.v1` planning on `funddisclosure-current-stage-source-truth`. No implementation is authorized until the fixed plan is accepted and committed by the controller.

Success signal:

- Proof-positive FDD content can return `current_stage.v1` with existing public field-family keys only: `schema_version`, `basic_identity`, `share_change`, `holdings_snapshot`, `portfolio_managers`.
- `current_stage.v1` direct result has public anchors, `extraction_mode="direct"` when non-missing, and `candidate_evidence=()`.
- Direct-route missing also returns `candidate_evidence=()`, not candidate locator evidence.
- Proof-missing, proof-invalid, candidate-boundary, missing provenance, and failure-class paths keep public `status="missing"`, `value={}`, `anchors=()`.
- `core_risk.v1` remains unimplemented for source-truth direct extraction and keeps existing candidate-only behavior.

## Non-goals and Boundaries

- No code, test, design, control, README, commit, push, PR, live, network, PDF, FDR, Docling, pdfplumber, provider, or LLM command in this Plan Gate.
- No implementation until accepted plan commit.
- No `core_risk.v1` source-truth implementation.
- No parser replacement, source acquisition change, repository/source behavior change, `EvidenceSourceKind` expansion, public `EvidenceAnchor` schema expansion, Service/UI/Host/renderer/quality-gate direct consumption, real-report correctness claim, readiness claim, release claim, or golden/baseline promotion.
- No new public subvalues such as `current_stage_summary`, `stage_status`, `manager_change`, `share_scale_change`, `holding_strategy_change`, `stage_judgment`, `market_timing`, `valuation_state`, or final holding/replacement judgment.
- Candidate selector roles are locator evidence only. They may inform implementation search surfaces, but they must not become public keys without a separate schema/public contract gate.

## Direct Code Evidence

- `docs/design.md` states current FDD source-truth direct extraction covers `product_essence.v1`, `return_attribution.v1`, `manager_profile.v1`, and `investor_experience.v1`; `current_stage.v1` and `core_risk.v1` remain unimplemented.
- `docs/implementation-control.md` and `docs/current-startup-packet.md` keep the same boundary: remaining missing FDD source-truth families are `current_stage.v1` and `core_risk.v1`; no parser replacement, upper-layer consumption, readiness, or release is authorized.
- `fund_agent/fund/processors/active_annual.py:27-30` and `fund_agent/fund/processors/active_annual.py:156-168` define the existing `current_stage.v1` field-family public keys as `basic_identity`, `share_change`, `holdings_snapshot`, and `portfolio_managers`.
- `fund_agent/fund/data_extractor.py:192-217` defines `StructuredFundDataBundle` fields. There is no `current_stage` bundle field.
- `fund_agent/fund/data_extractor.py:590-619` projects only named fields from field families into existing bundle fields.
- `fund_agent/fund/data_extractor.py` documents `_active_processor_result_to_bundle()` as `current_stage.v1 -> informational/redundant，不投影`; therefore this work must not add a bundle projection unless a separate public contract gate first changes bundle schema.
- `fund_agent/fund/processors/fund_disclosure_processor.py:964-981` currently creates direct extraction variables for the four implemented families only.
- `fund_agent/fund/processors/fund_disclosure_processor.py:1003-1013` always selects `current_stage.v1` candidate evidence and `core_risk.v1` candidate evidence.
- `fund_agent/fund/processors/fund_disclosure_processor.py:1016-1034` has no direct result branch for `current_stage.v1`; it falls through to candidate/missing family construction.
- Current local branch is `funddisclosure-current-stage-source-truth`; this is process evidence for current-stage planning only, not authorization to implement before accepted plan commit.

## Affected Files and Modules

Implementation write set:

- `fund_agent/fund/processors/fund_disclosure_processor.py`
- `tests/fund/processors/test_fund_disclosure_processor.py`
- `tests/fund/test_data_extractor.py`

Docs sync after implementation:

- `docs/design.md`
- `docs/implementation-control.md`
- `docs/current-startup-packet.md`
- `fund_agent/fund/README.md`

No other files are in scope.

## Public Contract, Schema, and State-machine Impact

Public contract impact: no schema expansion.

Allowed current_stage field-family public keys:

- `schema_version`
- `basic_identity`
- `share_change`
- `holdings_snapshot`
- `portfolio_managers`

Bundle impact:

- No new `StructuredFundDataBundle.current_stage` field.
- No new facade projection from `current_stage.v1`.
- Existing bundle fields `basic_identity`, `share_change`, `holdings_snapshot`, and `portfolio_managers` remain projected from their existing families (`product_essence.v1`, `investor_experience.v1`, `manager_profile.v1`) only.
- If a future requirement needs a bundle-level `current_stage` value or a semantic current-stage summary, that is a separate schema/public contract gate.

State-machine impact:

- Proof-positive FDD path: `current_stage.v1` may be `accepted`, `partial`, or `missing`.
- Proof-positive direct missing path: `status="missing"`, `value={}`, `anchors=()`, local gap, `candidate_evidence=()`.
- Proof-missing/proof-invalid path: public missing shape is preserved and source-truth admission gap is appended.
- Candidate-boundary or base admission blocked path: public missing/blocked semantics are preserved; no source-truth direct extraction runs.
- `core_risk.v1` state machine is unchanged.

## Exact Extraction Decisions

Add a `current_stage_source_truth` variable in `_field_families_for_intermediate()` and call a new `_extract_current_stage_source_truth()` only when `source_truth_extraction_allowed` and `content_intermediate is not None`.

When `current_stage_source_truth is not None`:

- use it in the family selection branch for `current_stage.v1`;
- set `current_stage_evidence=()`;
- leave `core_risk_evidence = _select_core_risk_candidate_evidence(intermediate)` unchanged.

Extraction must reuse existing FDD direct extraction helpers where they already produce the exact allowed public shapes. Exact reuse targets:

- `basic_identity`: call `_select_product_essence_values(intermediate, context)` and `_build_product_essence_basic_identity(product_selected_values, context)`. Do not call `_extract_product_essence_source_truth()` and then reinterpret a family result; do not add a new identity parser. Anchors for this key must come only from `product_selected_values` paths returned by `_product_essence_emitted_output_paths({"basic_identity": basic_identity}, product_selected_values)` that start with `basic_identity.`.
- `share_change`: call `_select_investor_experience_share_change(intermediate, context, ambiguous_paths)` or a behavior-preserving helper extracted directly from it. This must continue using `_collect_share_change_table_candidates()`, `_share_change_candidate_from_table()`, `_select_share_change_value_column()`, `_share_change_values_for_column()`, and `_calculate_investor_share_net_change()`; do not duplicate arithmetic, A-share/fund-code column selection, row-kind detection, or ambiguity logic.
- `holdings_snapshot`: call `_select_manager_profile_holdings_snapshot(intermediate, context, ambiguous_paths)` or a behavior-preserving helper extracted directly from it. This must continue using `_select_manager_profile_holdings_rows()`, `_manager_profile_holdings_table_allowed()`, `_manager_profile_holdings_row_dict()`, and `_manager_profile_holdings_row_identity()`; do not emit concentration, style drift, risk, or current-stage conclusions.
- `portfolio_managers`: call `_select_manager_profile_portfolio_managers(intermediate, context, ambiguous_paths)` or a behavior-preserving helper extracted directly from it. This must continue using `_manager_profile_roster_table_allowed()`, `_manager_profile_rows_by_index()`, `_manager_profile_roster_entry()`, and `_normalize_manager_profile_roster_entry()`; do not emit manager quality or current-stage implication.

Existing owning-family call sites that must remain shape-preserving:

- `_extract_product_essence_source_truth()` -> `_select_product_essence_values()` -> `_build_product_essence_value()` -> `_build_product_essence_basic_identity()`.
- `_extract_investor_experience_source_truth()` -> `_select_investor_experience_values()` -> `_select_investor_experience_share_change()` -> `_build_investor_experience_value()`.
- `_extract_manager_profile_source_truth()` -> `_select_manager_profile_values()` -> `_select_manager_profile_portfolio_managers()` / `_select_manager_profile_holdings_snapshot()` -> `_build_manager_profile_value()`.

Small refactor budget:

- Refactor only when required to reuse one of the exact targets above.
- Maximum new shared helpers: four module-local private helpers, one per reused top-level key.
- Maximum edits to existing owning helper bodies: moving code into the shared helper and replacing the original body/call site with a direct call; no semantic rewrites, token broadening, output key changes, status changes, gap-code changes, anchor schema changes, or candidate-evidence changes.
- If any helper is extracted, implementation must add behavior-preserving tests for existing direct families before current-stage assertions: product_essence `basic_identity`, investor_experience `share_change`, manager_profile `portfolio_managers`, and manager_profile `holdings_snapshot` outputs must remain structurally identical for the existing focused fixtures.

`current_stage.v1.value` construction:

- If no allowed key is selected, return `{}`.
- If at least one allowed key is selected, return `{"schema_version": "current_stage.v1", ...selected keys...}`.
- Missing allowed keys generate `field_family_partial` gaps when at least one key is emitted.
- No emitted keys generate one `field_family_missing` gap.
- Ambiguity/conflict contract: current_stage emits at most one candidate per top-level key from the exact owning helper listed above. Existing owning-helper ambiguity must be propagated to the matching current_stage top-level key and must generate `ambiguous_table_or_locator`. If implementation introduces an internal composite resolver that can see more than one candidate for the same current_stage key, candidates are compatible only when their normalized values are structurally equal after recursively sorting dict keys, preserving list order, and applying `_normalize_match_text()` to scalar leaves; non-equal same-key candidates are conflicting stable values, generate `ambiguous_table_or_locator`, and do not enter public value. Exact duplicate same-key values may be deduped and emitted once using the first stable anchor.

Status:

- `accepted` when all four allowed required keys are present and no ambiguity exists.
- `partial` when at least one allowed key is present and at least one required key is missing, or ambiguity exists.
- `missing` when no allowed key is emitted.

Anchors:

- Family anchors are the deduped anchors of emitted keys only.
- All anchors use existing public `EvidenceAnchor(source_kind="annual_report", ...)`.
- No candidate locator record may be converted into a public anchor by itself.

## Implementation Slices

Slice 1: Processor direct-route wiring

- Allowed file: `fund_agent/fund/processors/fund_disclosure_processor.py`
- Add `current_stage_source_truth` variable.
- Route proof-positive `current_stage.v1` through the new direct extractor branch.
- Suppress `current_stage.v1` candidate evidence when direct extractor returns a family result, including missing direct result.
- Preserve `core_risk.v1` candidate path.

Slice 2: Current-stage direct extractor

- Allowed file: `fund_agent/fund/processors/fund_disclosure_processor.py`
- Add module-local current-stage value candidate dataclass only if existing candidate dataclasses cannot be reused cleanly.
- Implement `_extract_current_stage_source_truth()`, `_select_current_stage_values()`, `_build_current_stage_value()`, `_current_stage_source_truth_gaps()`, `_current_stage_status()`, and emitted-output-path helper.
- Reuse the exact helper map in "Exact Extraction Decisions"; refactor narrowly only within the bounded refactor budget.
- Do not introduce public keys beyond the allowed list.

Slice 3: Processor tests

- Allowed file: `tests/fund/processors/test_fund_disclosure_processor.py`
- Add positive proof-positive tests for allowed keys, anchors, status, extraction mode, and `candidate_evidence=()`.
- Add direct-route missing test: proof-positive but no current-stage allowed values returns public missing and `candidate_evidence=()`.
- Add proof-missing/proof-invalid/candidate-boundary tests proving public missing semantics and no direct promotion.
- Add `core_risk.v1` non-interference test.
- Add schema guard assertion that disallows `stage_status`, `manager_change`, `share_scale_change`, `holding_strategy_change`, and any `current_stage_summary` key in public value.
- If any exact reuse helper is extracted, add behavior-preserving assertions for the existing owning families: product_essence `basic_identity`, investor_experience `share_change`, manager_profile `portfolio_managers`, and manager_profile `holdings_snapshot` must remain structurally identical on their existing focused fixtures.

Slice 4: Facade tests

- Allowed file: `tests/fund/test_data_extractor.py`
- Add proof-positive disclosure fixture containing current-stage-relevant source text.
- Assert no `StructuredFundDataBundle.current_stage` attribute exists.
- Assert current-stage direct extraction does not project into bundle fields from `current_stage.v1`.
- Assert existing bundle fields remain missing unless their owning families also produced direct source truth.
- Add integration coverage for a processor result containing all six families: `product_essence.v1`, `return_attribution.v1`, `manager_profile.v1`, `investor_experience.v1`, `current_stage.v1`, and `core_risk.v1`. Assert `_active_processor_result_to_bundle()` ignores `current_stage.v1` and still projects `basic_identity` only from `product_essence.v1`, `share_change` only from `investor_experience.v1`, and `holdings_snapshot` / `portfolio_managers` only from `manager_profile.v1`.

Slice 5: Docs sync

- Allowed files: `docs/design.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md`, `fund_agent/fund/README.md`
- State only current facts after implementation: proof-positive `current_stage.v1` direct extraction exists with exact allowed field-family keys; it has no bundle projection; `core_risk.v1` remains unimplemented; candidate evidence remains candidate_only/not_proven/NOT_READY.
- Do not claim readiness, release, parser replacement, real-report correctness, or upper-layer consumption.

## Validation Matrix

Allowed commands:

- `.venv/bin/python -m pytest tests/fund/processors/test_fund_disclosure_processor.py -q`
- `.venv/bin/python -m pytest tests/fund/test_data_extractor.py -q`
- `.venv/bin/python -m ruff check fund_agent/fund/processors/fund_disclosure_processor.py tests/fund/processors/test_fund_disclosure_processor.py tests/fund/test_data_extractor.py`
- `git diff --check -- fund_agent/fund/processors/fund_disclosure_processor.py tests/fund/processors/test_fund_disclosure_processor.py tests/fund/test_data_extractor.py docs/design.md docs/implementation-control.md docs/current-startup-packet.md fund_agent/fund/README.md`

Expected assertions:

- Positive proof-positive processor fixture emits `current_stage.v1.value["schema_version"] == "current_stage.v1"`.
- Public value keys are a subset of `{"schema_version", "basic_identity", "share_change", "holdings_snapshot", "portfolio_managers"}`.
- Positive result has anchors and `candidate_evidence == ()`.
- Direct-route no-match result has `status == "missing"`, `value == {}`, `anchors == ()`, `candidate_evidence == ()`, and a `field_family_missing` gap.
- Same-key current-stage conflicts produce `ambiguous_table_or_locator`, suppress that top-level key from public value, and yield `status == "partial"` if at least one other allowed key is emitted or `status == "missing"` if no allowed key is emitted.
- Proof-missing/proof-invalid/candidate-boundary paths keep public missing semantics and never emit current-stage anchors.
- `core_risk.v1` remains missing/candidate-only according to existing selector behavior.
- Facade bundle has no `current_stage` field and no current-stage projection.
- All-six-family facade test proves bundle projection uses owning families for `basic_identity`, `share_change`, `holdings_snapshot`, and `portfolio_managers`, not `current_stage.v1`.
- If shared helpers are extracted, existing owning-family focused fixtures still produce identical public top-level values, anchors, gaps, status, extraction mode, and `candidate_evidence` for the reused outputs.

## Docs Sync Decision

Docs sync is required after implementation because this work changes current processor truth. The sync must be narrow and factual:

- add `current_stage.v1` to the list of proof-positive FDD source-truth direct extraction families;
- state exact allowed field-family keys;
- state explicitly that no bundle-level `current_stage` field or semantic stage summary exists;
- keep `core_risk.v1` unimplemented;
- preserve NOT_READY and candidate-only boundaries.

## Residual Risks and Open Questions

- Residual: `current_stage.v1` allowed public keys are disclosed inputs for Chapter 5, not a current-stage judgment. Owner: future schema/semantic contract gate if product needs a stage summary.
- Residual: facade has no bundle-level `current_stage` projection. Owner: separate public contract gate; blocked in this work unit by existing bundle schema.
- Residual: reuse of manager/investor/product helper logic may require small refactors. Owner: implementation worker must stay within the bounded refactor budget; implementation reviewer must confirm the required behavior-preserving tests pass for existing direct families before reviewing current_stage behavior.
- Residual: `core_risk.v1` remains missing for FDD source truth. Owner: later `core_risk.v1` source-truth work unit.

No blocking open question for this plan, because existing contracts provide a sufficient processor field-family shape. The plan would become blocked only if reviewer requires a new bundle field or semantic current-stage public value; that would exceed this work unit and require a separate schema/public contract gate.

## Why This Is Not Over-designed

The plan adds one family branch and one family extractor under the existing proof-positive admission mechanism. It reuses existing public shapes and existing extraction logic where possible, avoids new schema, avoids new anchors/source kinds, avoids a bundle projection, and keeps candidate roles as locator-only evidence. The design is intentionally narrower than the candidate selector surface because Chapter 5 semantic current-stage judgment is not an existing public contract.

## Completion Report Format

Implementation worker should report:

- changed files;
- validation commands and outputs;
- exact `current_stage.v1` public keys emitted;
- confirmation that `candidate_evidence=()` on direct route;
- confirmation that facade/bundle has no current-stage projection;
- residual risks.
