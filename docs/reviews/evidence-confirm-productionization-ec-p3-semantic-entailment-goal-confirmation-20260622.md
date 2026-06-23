# Evidence Confirm Productionization EC-P3 Semantic Entailment Goal Confirmation

- Gate: goal confirmation
- Work unit: Evidence Confirm productionization / EC-P3 semantic entailment
- Date: 2026-06-22
- Classification: heavy
- Artifact path: `docs/reviews/evidence-confirm-productionization-ec-p3-semantic-entailment-goal-confirmation-20260622.md`

## Current Control Decision

Use current worktree control docs as the active routing authority:

- `docs/current-startup-packet.md` states current active gate is `EC-P3 semantic entailment Evidence Confirm goal confirmation/planning`.
- `docs/implementation-control.md` states active gate is `EC-P3 semantic entailment Evidence Confirm goal confirmation/planning`.
- The accepted program plan still labels semantic entailment as `EC-P4`, while `EC-P3` was originally deterministic production facade. That numbering is stale for the active control surface after EC-P2 closeout. This work unit follows the current control docs and records the numbering drift as a control-plane reconciliation fact, not as an implementation blocker.

## First-principles Judgment

Evidence Confirm needs two different proof surfaces:

1. Deterministic source/proof/value checks: whether the cited source exists, is proven, is same-anchor, and contains material values.
2. Semantic entailment checks: whether a qualitative claim is actually supported by the cited excerpt, without letting a semantic checker override missing source, candidate-only proof, wrong locator, or numeric mismatch.

Current V2 covers the first surface only. Its `value_match` dimension checks material token presence in same-anchor proven excerpts. That is necessary, but it is not semantic entailment. A qualitative claim can share tokens with an excerpt while overclaiming, contradicting, or adding unsupported causality. Conversely, a qualitative claim can be entailed without exact string identity. Therefore the work unit is valid and should be scoped as a separate semantic layer rather than a mutation of V2 scoring semantics.

## Goal

Define and plan a Fund-layer no-live semantic entailment Evidence Confirm contract that:

- consumes deterministic Evidence Confirm outputs and bounded excerpt/claim inputs;
- classifies qualitative support as `entailed`, `contradicted`, `insufficient`, or `not_applicable`;
- fails closed on malformed or missing semantic responses;
- never overrides deterministic failures in source support, missing evidence, proof boundary, anchor identity, or numeric value matching;
- remains import-isolated from Service, Host, provider SDKs, API-key config, network clients, renderer, UI and quality gate.

## Motivation

EC-P2 proved repository/source/PDF pathway for exact sample `004393 / 2025` but explicitly did not prove semantic entailment. Without a semantic layer, Evidence Confirm can prove that a cited excerpt exists and contains some material value tokens, but cannot prove that qualitative narrative claims are entailed by the excerpt.

## Success Signals

- A code-generation-ready plan exists for no-live EC-P3 semantic entailment.
- The plan binds schema, state transitions, fail-closed behavior, import boundaries, allowed files and tests.
- The plan keeps deterministic V2 as the source/proof/value hard gate.
- The plan does not authorize provider/live commands, Service/UI/renderer/quality-gate behavior changes, readiness/release claims, mark-ready, merge or PR external-state transitions.

## Non-goals

- No provider-backed semantic live execution.
- No real LLM/provider client construction.
- No Service/UI/Host/renderer/quality-gate integration.
- No change to `EvidenceConfirmResultV2` semantics unless explicitly planned as a companion result and reviewed.
- No release/readiness claim.
- No parser replacement, field correctness proof, golden promotion, or source fallback behavior change.
- No direct document/PDF/cache/source helper access outside Fund document repository boundaries.

## Scope Boundary

In scope for the next plan gate:

- Fund-layer semantic protocol/result contract.
- Fake-client no-live tests.
- Deterministic gating rules that prevent semantic output from masking V2 failures.
- Malformed-output fail-closed handling.
- Import isolation tests.
- Documentation updates if the implementation plan changes Fund developer docs.

Out of scope for this work unit:

- Controlled provider semantic evidence; this remains a later explicit authorization gate.
- Service opt-in policy and product request fields.
- Renderer/UI display.
- Quality-gate consumption.
- Release/readiness.

## Direct Code Evidence

- `fund_agent/fund/evidence_confirm.py` module docstring says current helper only consumes explicit projections and same-source reference excerpts, and does not read repository, provider, network, Service, Host, filesystem or dayu runtime.
- `EvidenceConfirmDimension` currently contains five deterministic dimensions: `anchor_precision`, `source_support`, `missing_evidence`, `proof_boundary`, `value_match`.
- `_confirm_fact_v2()` runs those five deterministic dimensions in order and computes hard gate from dimension results.
- `_dimension_value_match()` extracts material tokens from `fact.value` and passes when any token appears in same-anchor proven reference excerpts.
- `_token_matches_excerpt()` uses numeric boundary matching or substring matching; this is not semantic entailment.
- Tests currently verify value mismatch and unrelated-anchor behavior, but they do not model semantic contradiction, insufficient semantic support, or malformed semantic checker output.
- `fund_agent/fund/evidence_confirm_sources.py` provides EC-P2 repository-bounded runner and materializer; it does not add semantic entailment.

## Over-design Avoidance

The next plan should avoid a broad scoring framework rewrite. The narrow useful primitive is a separate semantic companion layer that receives already-bounded claims/excerpts and a protocol client. This avoids changing V2 public semantics, avoids provider coupling, and gives later provider and Service integration gates a stable contract.

## Blocking Open Questions

None for goal confirmation if current control docs are accepted as active routing authority.

## Next Gate

EC-P3 semantic entailment plan gate.

User confirmation is required before entering the plan gate under gateflow.
