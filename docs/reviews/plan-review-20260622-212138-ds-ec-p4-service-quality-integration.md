# Plan Review — EC-P4 Service/UI/Renderer/Quality-Gate Integration

## Gate

- Review gate: `plan review`
- Reviewed target: `docs/reviews/evidence-confirm-productionization-ec-p4-service-quality-integration-plan-20260622.md`
- Reviewer: AgentDS
- Classification: `heavy`
- Timestamp: `2026-06-22 21:21 Asia/Shanghai`
- Verdict: **PASS_WITH_FINDINGS**

## Reviewed Target

`docs/reviews/evidence-confirm-productionization-ec-p4-service-quality-integration-plan-20260622.md` — a 6-slice plan integrating accepted EC-P1A/EC-P2/EC-P3 Evidence Confirm capabilities into the production Service/UI/renderer/quality-gate surface.

## Summary

The plan is structurally sound and respects the core AGENTS.md boundaries. It correctly identifies that Evidence Confirm belongs to the Fund layer, Service owns user-visible policy, quality gate owns issue projection, and CLI owns display. The opt-in-first strategy, deliberate non-rendering decision, and ECQ (not FQ7) issue family are all correct architectural choices. The plan is largely code-generation-ready, with six documented slices and explicit allowed files, test specs, and stop conditions.

However, the plan has a non-trivial scope ambiguity around the `checklist` command path that blocks Slice 2/3 implementation. It also underspecifies the interaction between `quality_gate_policy` and `evidence_confirm_policy` in the combined blocking scenario. These findings must be resolved before implementation can proceed to code generation.

## Findings

### Finding DS-PR-01 — Checklist command lacks developer override mode path (HIGH)

- **Severity**: HIGH
- **Location**: Plan Slice 2 line "if current checklist has no explicit mode surface, the implementation must either add a matching `--mode developer_override` path with tests or restrict the flag to `analyze` and record checklist as Slice 2. Preferred: support both commands with identical validation."
- **Issue**: The current `checklist()` CLI command (`fund_agent/ui/cli.py:893`) has no `--mode` parameter, no `FundAnalysisDeveloperOverrides` construction, and always creates `FundAnalysisRequest` in product mode. The plan acknowledges this gap but does not resolve it — it presents both options as equally valid and defers the decision to the implementation worker. Slice 3 tests (e.g., `checklist --mode developer_override --evidence-confirm-policy warn`) cannot even be written without knowing which option is chosen.
- **Why it matters**: This is a blocking ambiguity for Slices 2 and 3. If `checklist` is deferred, Slice 3 must not include checklist tests. If `checklist` is included, Slice 2 must first add `--mode developer_override` to the checklist CLI and the internal `checklist()` Service method must construct and pass developer overrides. Without this decision, no implementation worker can produce a correct implementation.
- **Required fix**: Decide explicitly. Recommendation: restrict Slice 1–3 to `analyze` only and defer `checklist` Evidence Confirm support to a separate follow-up gate. The checklist command's current architecture (product-mode only, no developer override surface) makes it a non-trivial addition that should not be bolted on in a single slice. Remove checklist-related tests from Slice 3 and add a residual risk entry.
- **Suggested owner**: Controller (decision) / Plan author (artifact update).

### Finding DS-PR-02 — Combined blocking semantics underspecified (HIGH)

- **Severity**: HIGH
- **Location**: Plan § "State machine" steps 6, and ECQ taxonomy table.
- **Issue**: The plan defines two overlapping blocking paths:
  1. `quality_gate_policy="block"` + combined gate status `block` → `QualityGateBlockedError`
  2. Quality gate off/not runnable + `evidence_confirm_policy="block"` + EC `fail` → `EvidenceConfirmBlockedError`
  
  But the case where both are active is ambiguous. If `quality_gate_policy="block"` AND `evidence_confirm_policy="block"` AND EC fails (producing ECQ2/block) while FQ passes: does the combined gate status become `block` (triggering `QualityGateBlockedError`), or should the EC-only failure trigger `EvidenceConfirmBlockedError`? If `evidence_confirm_policy="warn"` AND `quality_gate_policy="block"` AND FQ independently blocks: ECQ2/warn is merged but the gate status is already `block` from FQ — does this produce `QualityGateBlockedError` carrying ECQ warn issues, or should it be `EvidenceConfirmBlockedError`?

  The taxonomy table (ECQ2 severity = "block when EC policy block, otherwise warn") implies severity is orthogonal to quality gate policy, but the blocking logic in step 6 only checks quality gate policy for the combined status, not individual ECQ severity.
- **Why it matters**: Ambiguous blocking semantics lead to implementation that chooses one path arbitrarily, potentially hiding EC failures behind FQ blocks or vice versa. The user-visible contract (which error type, which exit code, which stderr content) must be unambiguous before code generation.
- **Required fix**: Add an explicit decision table:
  - `quality_gate_policy=block` + EC `fail` + EC policy `block` → combined gate `block` → `QualityGateBlockedError` with ECQ issues in the gate result (preferred, since quality gate is the canonical output blocker).
  - `quality_gate_policy=off` + EC `fail` + EC policy `block` → `EvidenceConfirmBlockedError`.
  - `quality_gate_policy=block` + EC `warn` + EC policy `warn` → combined gate status depends on FQ only; ECQ warn issues are informational.
  - `quality_gate_policy=warn` + EC `fail` + EC policy `block` → should EC policy override quality gate policy? (Recommend: yes, block on EC fail regardless of quality gate warn policy.)

  Also specify whether `EvidenceConfirmBlockedError` should carry the full summary (plan says yes, confirm explicitly in the decision table).
- **Suggested owner**: Plan author.

### Finding DS-PR-03 — `checklist()` Service method has no developer override resolution (MEDIUM)

- **Severity**: MEDIUM
- **Location**: Plan § "Service request/result contracts" and Slice 2, referenced code `fund_agent/services/fund_analysis_service.py:719`.
- **Issue**: The plan adds `evidence_confirm_policy` to `FundAnalysisDeveloperOverrides` and `ResolvedAnalyzeContract`. However, `checklist()` (line 719) calls `_run_analysis_core(replace(request, command_source="checklist"))` without constructing developer overrides, and the CLI `checklist` command (line 893) never sets `mode` or `developer_overrides`. If the plan resolves DS-PR-01 by supporting checklist, the internal resolution of `evidence_confirm_policy` for checklist needs to be explicitly designed: checklist has no `ResolvedAnalyzeContract` resolution of its own — it reuses `_resolve_analyze_contract` which pulls from `request.developer_overrides`. If `developer_overrides` is None, the resolved policy will always be `"off"`.
- **Why it matters**: This is the implementation detail behind DS-PR-01. Even if the plan resolves DS-PR-01 in favor of checklist support, the Service-level plumbing is not designed.
- **Required fix**: If checklist is included, specify exactly how `FundAnalysisRequest` carries developer overrides for checklist (same `developer_overrides` field already exists on `FundAnalysisRequest`). Specify the resolution rule: if checklist request has `developer_overrides=None`, `evidence_confirm_policy` resolves to `"off"`. If checklist is deferred per DS-PR-01 recommendation, remove checklist from Slice 2 allowed scope.
- **Suggested owner**: Plan author / implementation worker.

### Finding DS-PR-04 — Missing status re-aggregation specification for ECQ merge (MEDIUM)

- **Severity**: MEDIUM
- **Location**: Plan Slice 1, "Exact changes" bullet 4: "Merge ECQ issues with existing `QualityGateResult` after `run_quality_gate()` returns".
- **Issue**: `run_quality_gate()` returns `QualityGateResult` with an aggregated `status` field computed by `_aggregate_gate_status(issues)`. After merging ECQ issues, the aggregated status must be recomputed — but the plan doesn't specify whether to re-call `_aggregate_gate_status()` on the combined issue set, or whether to use a different aggregation that considers ECQ severity differently from FQ severity. If ECQ2/block is merged but status is not re-aggregated, the block won't actually take effect.
- **Why it matters**: Without re-aggregation, ECQ2/block issues are present in the issue list but the gate status remains whatever FQ computed — making the blocking semantics in Slice 2 silently broken.
- **Required fix**: Add explicit step: after merging ECQ issues, re-aggregate gate status on the combined issue list using the same `_aggregate_gate_status()` semantics. Add test `test_quality_gate_integration_ecq2_block_changes_gate_status_to_block` to Slice 1.
- **Suggested owner**: Plan author / implementation worker.

### Finding DS-PR-05 — Missing boundary static test for `quality_gate_integration.py` (MEDIUM)

- **Severity**: MEDIUM
- **Location**: Plan Slice 1 allowed files, and Slice 2 boundary static test spec.
- **Issue**: Slice 2 includes boundary static tests for `fund_analysis_service.py` (no repository/PDF/cache/source adapter imports), but Slice 1 doesn't include an equivalent boundary static test for `quality_gate_integration.py`. Since Slice 1 adds ECQ issue projection to `quality_gate_integration.py`, this module must also not import repository, PDF cache, source helpers, source adapters, Docling artifacts, or parser JSON.
- **Why it matters**: The quality gate integration module is the bridge between Evidence Confirm and quality gate output. If implementation accidentally imports repository internals, the boundary is violated without detection.
- **Required fix**: Add `test_quality_gate_integration_boundary_no_repository_or_source_imports` to Slice 1 test list, with same pattern as Slice 2's equivalent test.
- **Suggested owner**: Plan author.

### Finding DS-PR-06 — Slice 1–2 dependency not explicit (LOW)

- **Severity**: LOW
- **Location**: Plan Slices 1 and 2.
- **Issue**: Slice 2 (Service propagation) depends on Slice 1 types (`EvidenceConfirmProductionSummary`, `EvidenceConfirmProductionPolicy`, and the updated `run_quality_gate_for_bundle` signature). The plan doesn't state this dependency explicitly. If an implementation worker starts with Slice 2, they will hit import errors.
- **Why it matters**: Low risk for an experienced implementer, but violates the "code-generation-ready" standard for independent slices.
- **Required fix**: Add "Depends on: Slice 1" to Slice 2 header.
- **Suggested owner**: Plan author.

### Finding DS-PR-07 — `EvidenceConfirmBlockedError` not integrated into CLI error handler (LOW)

- **Severity**: LOW
- **Location**: Plan Slice 3 vs current CLI code `fund_agent/ui/cli.py:957-965`.
- **Issue**: The current `checklist` CLI has explicit `except QualityGateNotRunBlockedError` and `except QualityGateBlockedError` handlers. Slice 3 adds `_echo_evidence_confirm_blocked(error)` but doesn't specify where `EvidenceConfirmBlockedError` is caught — before the existing quality gate handlers, after them, or as a separate except block. If caught before, it takes priority; if after, quality gate errors shadow it.
- **Why it matters**: Minor ordering concern, but the error handler precedence determines which error the user sees when both quality gate and EC block.
- **Required fix**: Specify: `EvidenceConfirmBlockedError` should be caught AFTER `QualityGateBlockedError` since EC-only blocking only triggers when quality gate is off/not runnable. When quality gate IS running and produces `QualityGateBlockedError` with ECQ issues merged in, the `QualityGateBlockedError` path already carries the EC failure context.
- **Suggested owner**: Implementation worker.

## Open Questions

1. Should the `_run_quality_gate_if_enabled()` helper be renamed or split, given it will now also optionally consume Evidence Confirm summary? The current name implies quality gate only, but post-EC-P4 it may accept an EC summary parameter. (Recommendation: keep the name; passing optional EC summary is additive and doesn't change the function's primary purpose.)

2. Should `EvidenceConfirmBlockedError` be defined in `fund_agent/fund/evidence_confirm_production.py` (Fund layer) or `fund_agent/services/fund_analysis_service.py` (Service layer)? The plan says Service adds it, but the error class carries a Fund-defined summary type. (Recommendation: define in Service layer with a Fund-type field; this matches the existing `QualityGateBlockedError` pattern.)

3. Should `ECQ0/info` be emitted even when `policy="off"` and no summary exists? The plan says ECQ0 is for "summary absent or status not_run" but the Slice 2 state machine says when policy is `off`, leave the result field `None` — which means the quality gate would never see a summary to generate ECQ0 from. (Recommendation: ECQ0 should be emitted when quality gate runs and EC is off, using not_run_reason="policy=off", to make the off state visible in quality gate output.)

## Residual Risks

| Risk | Owner | Mitigation |
|---|---|---|
| `checklist` Evidence Confirm path deferred creates future integration debt | Controller | Resolved by DS-PR-01 recommendation; record as residual for follow-up gate |
| Combined ECQ+FQ status aggregation may produce unexpected `block` when only ECQ warns and FQ passes | Quality gate owner | Mitigated by DS-PR-02 resolution; add explicit aggregation test |
| `EvidenceConfirmProductionSummary.auditability_score` may leak V2 scoring internals to Service/UI | Fund Evidence Confirm owner | Acceptable: score is a pre-computed integer, not raw excerpts or parser artifacts |
| Renderer may need future Evidence Confirm section wording | Renderer/product owner | Deferred to separate renderer wording gate per plan Slice 4 |
| `project_chapter_facts()` call in Service creates implicit dependency on Fund internals | Service owner | Acceptable: `project_chapter_facts()` is a public Fund-layer function consuming only `StructuredFundDataBundle`, per AGENTS.md Service→Fund boundary allowance |
| If semanic companion (Slice 5) needs provider-backed client construction, the plan allows it via injection but the implementation may be tempted to construct a real client | Semantic owner | Slice 5 stop condition explicitly blocks provider construction; static guard test should verify |

## Required Follow-up Gate

- `code review` (standard classification) after implementation. Must verify:
  - All boundary static tests pass (no repository/PDF/source adapter imports in Service/UI/quality-gate).
  - `score.json` remains Evidence-Confirm-unaware.
  - Renderer report Markdown contains no Evidence Confirm section.
  - All ECQ issues carry stable reason codes.
  - `NOT_READY` is preserved in all output.
  - No CLI flag implies default-on, ready, or provider-backed.
