# Plan Review: FundDisclosureDocument current_stage.v1 Source-truth Direct Extraction

**Role**: AgentDS plan reviewer
**Plan artifact**: `docs/reviews/funddisclosuredocument-current-stage-source-truth-extraction-plan-20260620.md`
**Gate**: Plan Review Gate
**Date**: 2026-06-20
**Verdict**: `PLAN_REVIEW_PASS`

## Evidence Basis

- `AGENTS.md` — rule truth source, Processor/Extractor boundary
- `docs/design.md` v2.31 — current design truth (lines 1-8: `current_stage.v1` / `core_risk.v1` FDD source-truth extraction 仍未实现)
- `docs/implementation-control.md` v2.9 — current gate explicitly disallows `current_stage.v1` / `core_risk.v1` parallel implementation (line 10)
- `docs/current-startup-packet.md` — same gate boundary (line 24, line 63)
- `fund_agent/fund/processors/fund_disclosure_processor.py:42-49` — `_FAMILY_ORDER` includes `current_stage.v1` and `core_risk.v1`
- `fund_agent/fund/processors/fund_disclosure_processor.py:964-981` — four existing source-truth variables, none for `current_stage.v1`
- `fund_agent/fund/processors/fund_disclosure_processor.py:1003-1013` — `current_stage_evidence` always calls candidate selector
- `fund_agent/fund/processors/fund_disclosure_processor.py:1016-1034` — ternary family selection has no `current_stage.v1` direct-result branch
- `fund_agent/fund/processors/active_annual.py:27-30,156-168` — `current_stage.v1` field-family mapping: `basic_identity`, `share_change`, `holdings_snapshot`, `portfolio_managers`
- `fund_agent/fund/data_extractor.py:192-217` — `StructuredFundDataBundle` has no `current_stage` field
- `fund_agent/fund/data_extractor.py:708-734` — `_active_processor_result_to_bundle()` docstring: `current_stage.v1 → informational/redundant，不投影`; no code references `current_stage.v1` in projection path

## Constraint Verification

### C1: No new public schema/bundle field (PASS)

Plan lines 70-74, 182 explicitly state: no `StructuredFundDataBundle.current_stage` field, no facade projection from `current_stage.v1`, existing bundle fields remain projected from their existing families only. Confirmed against current `StructuredFundDataBundle` dataclass (lines 192-217) — no `current_stage` attribute exists.

### C2: No semantic stage judgment or current_stage_summary (PASS)

Plan lines 26-27 (non-goals) explicitly forbid `current_stage_summary`, `stage_status`, `manager_change`, `share_scale_change`, `holding_strategy_change`, `stage_judgment`, `market_timing`, `valuation_state`, or final holding/replacement judgment. Allowed keys are strictly the four existing field-family keys that appear in `active_annual.py:156-168`.

### C3: Public keys justified by existing field-family contract (PASS)

All four allowed keys — `basic_identity`, `share_change`, `holdings_snapshot`, `portfolio_managers` — are verified in `active_annual.py:156-168` as the exact `current_stage.v1` field-family mapping. Plan line 33-34 cross-references this location.

### C4: State-machine precision (PASS)

Plan lines 79-83, 89-93, 105-121 detail:
- Proof-positive: `accepted` / `partial` / `missing` with `candidate_evidence=()`
- Direct-route missing: `status="missing"`, `value={}`, `anchors=()`, `candidate_evidence=()`, `field_family_missing` gap
- Proof-missing/proof-invalid/candidate-boundary: preserve public missing semantics, no anchor promotion
- Candidate locator evidence suppressed when direct extractor returns any result (including missing)

These paths are consistent with the existing four-family pattern at `fund_disclosure_processor.py:983-1001` where `candidate_evidence=()` when source-truth result exists.

### C5: core_risk.v1 unaffected (PASS)

Plan lines 25, 83, 117, 132, 148, 162, 181, 192, 198 explicitly preserve `core_risk.v1` candidate-only path. Code reference `fund_disclosure_processor.py:1004` confirms `core_risk_evidence` is `_select_core_risk_candidate_evidence(intermediate)` — unchanged by this plan.

### C6: No parser replacement / EvidenceSourceKind expansion / upper-layer consumption / readiness claim (PASS)

Plan lines 24-25 (non-goals) enumerate all prohibited transitions. No parser, source acquisition, repository behavior, `EvidenceSourceKind`, `EvidenceAnchor` schema, Service/UI/Host/renderer/quality-gate consumption, real-report correctness, readiness, release, or golden/baseline promotion claims appear.

### C7: Implementation slices and tests (PASS with findings)

Five slices covering: processor wiring (Slice 1), extractor logic (Slice 2), processor tests (Slice 3), facade tests (Slice 4), docs sync (Slice 5). Tests cover positive, missing, blocked, non-interference, and schema-guard cases.

## Findings

### F1 [MEDIUM] Reuse-target underspecification — `docs/reviews/funddisclosuredocument-current-stage-source-truth-extraction-plan-20260620.md:97-101`

The plan instructs reuse of existing extraction helpers — e.g., "reuse product-essence selection/building output for `basic_identity`" — but does not name which specific module-level functions in `fund_disclosure_processor.py` produce each of the four target value shapes. The existing `_extract_product_essence_source_truth()` (line 1094), `_extract_investor_experience_source_truth()` (line 5220), and `_extract_manager_profile_source_truth()` (line 1174) are coarse family-level extractors; the plan's intent to extract individual sub-values (`basic_identity` from product-essence, `share_change` from investor-experience, `holdings_snapshot` and `portfolio_managers` from manager-profile) requires the implementer to reverse-engineer which internal helper or selection logic produces each sub-value. This creates risk of inadvertently altering an existing family's output shape if the wrong extraction point is reused.

**Recommendation**: In implementation, first identify the exact function + call site within each existing extractor that produces the target sub-value, and document these mappings before writing new code.

### F2 [MEDIUM] "Small refactors" budget is unbounded — `docs/reviews/funddisclosuredocument-current-stage-source-truth-extraction-plan-20260620.md:102, 198`

Plan line 102: "If reuse requires extracting small shared helper functions from existing selectors, keep them module-local and behavior-preserving." The plan does not bound which functions may be refactored, how many, or how to verify behavior preservation for the four existing direct families. The residual at line 198 acknowledges this but delegates verification to "implementation reviewer." The implementation worker could scope-creep refactors beyond what's needed.

**Recommendation**: The implementation gate should require focused tests that pass the existing four-family fixtures through the refactored code path and assert output shapes are byte-identical to pre-refactor output.

### F3 [LOW] `ambiguous_table_or_locator` detection unspecified — `docs/reviews/funddisclosuredocument-current-stage-source-truth-extraction-plan-20260620.md:110`

Plan line 110: "Duplicate/conflicting stable values for a key generate `ambiguous_table_or_locator` and do not enter public value." The plan does not specify the detection heuristic: what constitutes "duplicate/conflicting" (exact match? semantic equivalence? same table but different rows?). The existing four extractors may not have this logic since each family owns its keys exclusively, whereas `current_stage.v1` is a cross-family composite.

**Recommendation**: During implementation, define the conflict detection contract before writing `_select_current_stage_values()`. The simplest correct contract is: same-key values from different source families that are not structurally equal produce `ambiguous_table_or_locator`.

### F4 [LOW] Facade test slice lacks processing-path integration — `docs/reviews/funddisclosuredocument-current-stage-source-truth-extraction-plan-20260620.md:153-157`

Slice 4 tests assert bundle absence and no projection. It does not include an integration test that feeds a full processor result containing `current_stage.v1` alongside the other five families through `_active_processor_result_to_bundle()` and asserts that the four existing bundle fields (`basic_identity`, `share_change`, `holdings_snapshot`, `portfolio_managers`) still project from their owning families, not from `current_stage.v1`. This is a low-severity gap because the current facade code (`data_extractor.py:729-734`) does not reference `current_stage.v1` at all.

**Recommendation**: Add a defensive integration test in Slice 4 that constructs a processor result with all six families and verifies `_active_processor_result_to_bundle()` output is identical regardless of `current_stage.v1` presence.

### F5 [OBSERVATION] Current gate authorization gap — `docs/implementation-control.md:10`, `docs/current-startup-packet.md:24`

The current active gate states: "No mark-ready/merge, `current_stage.v1`/`core_risk.v1` implementation … is authorized." This plan requests a new work unit for `current_stage.v1`. The plan review gate (this review) assesses whether the plan is code-generation-ready — it is. But the plan cannot be implemented without a controller gate transition that explicitly authorizes `current_stage.v1` work. This is a process observation, not a plan quality defect.

## Summary

The plan respects all hard constraints: no new bundle field, no semantic stage judgment, public keys justified by existing `active_annual.py` contract, state-machine paths are precise, `core_risk.v1` is preserved, and no parser replacement or upper-layer consumption is claimed. The five implementation slices are sufficient and minimal. All code references to existing processor and extractor lines are accurate. Findings F1-F4 are implementation-level concerns that should be addressed during the implementation gate, not blockers at plan review.

**Verdict**: `PLAN_REVIEW_PASS`
