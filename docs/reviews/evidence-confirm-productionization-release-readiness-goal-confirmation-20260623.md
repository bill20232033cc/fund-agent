# Evidence Confirm Productionization Release/Readiness Goal Confirmation

## Gate

- Work unit: Evidence Confirm Productionization release/readiness.
- Gate: goal confirmation.
- Classification: heavy.
- Branch: `evidence-confirm-productionization`.
- Current local head: `cb199ce gateflow: audit evidence confirm release readiness`.
- Current PR surface: PR-40 remains draft/open at `af86b9b`; local release/readiness audit commit is not yet pushed.
- Artifact: `docs/reviews/evidence-confirm-productionization-release-readiness-goal-confirmation-20260623.md`.

## First-principles Judgment

The release/readiness work unit is valid but not ready for implementation as one broad slice.

Evidence Confirm has already reached a useful production-integration draft PR state:

- EC-P1A: no-live reference materialization.
- EC-P2: repository-bounded live source/PDF pathway for the exact authorized sample.
- EC-P3: no-live semantic entailment companion contract.
- EC-P4: Service/UI/renderer/quality-gate integration for developer opt-in, compact summary and ECQ projection.

Release/readiness is still not proven because the current default product path does not call Evidence Confirm. A release claim must cover what users get by default, not only a developer opt-in path. Therefore the first readiness blocker to plan is default-on Evidence Confirm policy.

## Current Code Evidence

- `docs/design.md` states default product `analyze` and `checklist` do not call Evidence Confirm.
- `fund_agent/services/fund_analysis_service.py` resolves `evidence_confirm_policy` to `"off"` by default.
- `fund_agent/services/fund_analysis_service.py` keeps `checklist` effective Evidence Confirm policy fixed to `"off"`.
- `fund_agent/ui/cli.py` exposes `--evidence-confirm-policy` only under `analyze --dev-override`.
- `tests/ui/test_cli.py` asserts default analyze output has no Evidence Confirm lines and checklist help does not expose Evidence Confirm policy.
- `docs/reviews/evidence-confirm-productionization-release-readiness-requirements-audit-20260623.md` records release/readiness as not met.

## Goal

Produce a code-generation-ready plan for making Evidence Confirm default-on where it is safe and release-meaningful, without weakening existing fail-closed behavior or crossing repository/source/provider boundaries.

The plan must decide the minimum viable default-on policy for release/readiness and spell out exact implementation slices, tests, docs, residual evidence gates and stop conditions.

## Success Signal

The next plan artifact is accepted only if it answers:

1. Which product paths become default-on candidates in this work unit: `analyze`, `checklist`, or both.
2. Whether default policy is `warn` or `block`, and why that is the correct release-readiness step.
3. How existing developer override remains available without allowing product users to silently disable Evidence Confirm.
4. How Service, CLI, renderer and quality-gate behavior changes, with exact files and invariants.
5. How deterministic no-live tests prove the policy and how live/provider evidence remains separate.
6. Which readiness blockers remain after this work unit, with owners and next gates.

## Non-goals

- Do not run new live/PDF commands in the planning gate.
- Do not construct provider-backed semantic clients.
- Do not add checklist CLI Evidence Confirm flags unless the plan proves this is part of the minimum default-on policy.
- Do not render Evidence Confirm into report Markdown or appendices unless the plan proves release scope requires it.
- Do not change source fallback behavior, public `EvidenceSourceKind`, `EvidenceAnchor`, parser behavior, repository internals, Host/Agent runtime, provider defaults or LLM budgets.
- Do not mark PR-40 ready, merge, release, request reviewers, delete branches or mutate external state.

## Scope Boundary For Plan Worker

Allowed read/write scope for the plan artifact:

- Read: `AGENTS.md`, `docs/design.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md`, current EC-P1A/P2/P3/P4 artifacts, the release/readiness audit artifact, and relevant current code/tests under:
  - `fund_agent/services/fund_analysis_service.py`
  - `fund_agent/ui/cli.py`
  - `fund_agent/fund/evidence_confirm_production.py`
  - `fund_agent/fund/quality_gate_integration.py`
  - `tests/services/test_fund_analysis_service.py`
  - `tests/ui/test_cli.py`
  - `tests/fund/test_quality_gate_integration.py`
- Write exactly one plan artifact:
  - `docs/reviews/evidence-confirm-productionization-default-on-policy-plan-20260623.md`

No source code, tests, README, design/control docs, git state or PR state may be modified by the plan worker.

## Dispatch

Next concrete task: dispatch `AgentCodex` as planning worker using `$gateflow` syntax.

Expected completion report:

- artifact path,
- recommended default-on policy,
- implementation slice list,
- validations,
- residual blockers,
- explicit stop condition.

## Verdict

GOAL_CONFIRMED_READY_FOR_DEFAULT_ON_POLICY_PLAN_GATE_NOT_READY
