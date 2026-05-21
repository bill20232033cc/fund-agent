# P9-S1 Analyze Product Contract Planning Handoff - 2026-05-21

## Role

You are the planning specialist for P9-S1. Produce a code-generation-ready plan only. Do not edit source code, tests or documentation outside this plan artifact.

## Context

- design_doc: `docs/design.md`
- control_doc: `docs/implementation-control.md`
- current gate: `P9-S1 analyze product contract plan/review`
- post-P8 controller decision: `docs/reviews/post-p8-planning-20260521.md`
- current code baseline: `56d579f docs: accept post-P8 planning`

Read `AGENTS.md`, `docs/design.md`, `docs/implementation-control.md`, and the current `fund_agent/services/fund_analysis_service.py` / `fund_agent/ui/cli.py` analyze path before drafting the plan.

## Problem Statement

The current `fund-analysis analyze` product path exposes too many manual inputs and keeps `final_judgment` as a user-facing explicit request field. This was useful for deterministic MVP development, but it conflicts with the product goal of ordinary investors getting an auditable pre-buy fund checkup with minimal user input.

Current facts to verify:

- `FundAnalysisRequest` includes manual inputs such as `equity_position`, `actual_style`, `actual_equity_position`, `manager_tenure_months`, `peer_fee_median`, `tracking_error`, `investment_amount`, `max_tolerable_loss_rate`, `valuation_state`, `money_horizon`, `user_money_horizon_years`, `current_stage`, and `final_judgment`.
- CLI mirrors these options directly.
- Service currently passes `request.final_judgment` into `TemplateRenderInput`, and programmatic audit uses that judgment for R2 consistency.
- Some inputs are genuinely user-owned today: fund code, report year, investment amount, max tolerable loss, money horizon, and explicit valuation state until thermometer-to-valuation mapping is separately designed.
- Some inputs are likely document/system-derived or should have an explicit data-gap status: fees, manager tenure, manager ownership, holdings, share changes, NAV/benchmark, current stage, risk checks, and pressure test facts.

## Planning Objective

Draft a concrete implementation plan for P9-S1 that defines a safer product contract for `fund-analysis analyze`:

1. Product-mode user success path with minimal inputs.
2. Developer-override mode for explicit fixtures/smoke/manual comparison when needed.
3. A final judgment derivation policy from existing checklist/risk/quality signals, with explicit override semantics if retained.
4. Boundary-respecting changes across UI, Service and Fund Capability.

## Required Decisions In The Plan

The plan must decide and justify:

- Whether to add an explicit mode flag, for example product/default mode plus `--dev-override` or a separate command/subcommand.
- Which current CLI parameters remain user-facing product inputs.
- Which current CLI parameters move behind developer override.
- Which request fields should become derived, optional, or grouped into a nested explicit override object without using `extra_payload`.
- Where final judgment derivation belongs. It must not be implemented in UI; if it uses fund-domain signals, it belongs in Service orchestration only as composition or in Fund Capability as domain policy.
- How R2 audit should consume derived judgment and still catch inconsistent overrides.
- How quality gate block/warn/off interacts with product mode and developer override mode.
- How to keep existing tests and smoke commands working during migration.

## Boundary Constraints

- UI parses inputs and renders outputs only.
- Service orchestrates use cases and may compose results, but must not implement fund-domain extraction rules.
- Fund Capability owns fund-domain analysis, checklist, risk policy, template contracts and evidence rules.
- No direct fund document filesystem access outside `FundDocumentRepository`.
- No explicit parameters hidden in `extra_payload`.
- Do not introduce external Dayu runtime, LLM writing, Host/Engine/tool loop, or prompt scene registry.
- Do not make thermometer-derived valuation automatic in this slice.

## Expected Plan Shape

Write the plan to `docs/reviews/p9-s1-analyze-product-contract-plan-20260521.md`.

Include:

- Current contract inventory.
- Target contract proposal.
- Migration strategy.
- File-by-file implementation steps.
- Test plan with focused tests and full-suite expectation.
- Documentation updates.
- Risks and non-goals.
- Review checklist for MiMo/DS/GLM reviewers.

## Suggested File Ownership For Future Implementation

The implementation plan may touch:

- `fund_agent/services/fund_analysis_service.py`
- `fund_agent/ui/cli.py`
- `fund_agent/fund/analysis/checklist.py` or a new Fund Capability policy module if final judgment derivation is domain logic
- `fund_agent/fund/template/renderer.py` only if template input shape needs a controlled adaptation
- `fund_agent/fund/audit/audit_programmatic.py` only if R2 input contract changes
- relevant tests under `tests/services/`, `tests/ui/`, `tests/fund/analysis/`, `tests/fund/template/`, `tests/fund/audit/`
- root `README.md`, `fund_agent/fund/README.md`, `fund_agent/README.md` or `docs/design.md` only if public contract/boundary changes

## Agent Routing Note

Procodex / AgentCodex is the preferred planning specialist. If Procodex / AgentCodex has network or environment issues, AgentMiMo may substitute for planning or implementation, but then AgentMiMo must not review the same slice. In that case use AgentDS + AgentGLM for plan review.
