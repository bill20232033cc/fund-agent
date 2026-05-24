# Release Maintenance Slice C Handoff — Layer Boundary Cleanup

## Context

- Source: `docs/reviews/controller-judgment-repo-deepreview-20260523.md` Slice C.
- Accepted findings:
  - UI imports Capability thermometer result types directly.
  - `ThermometerService` default construction imports concrete Capability data cache/source internals.
- Controller precheck: Slice C remains open on current main.

## Implementation Scope

Worker owns the focused implementation:

- `fund_agent/ui/cli.py`
- `fund_agent/services/thermometer_service.py`
- `fund_agent/services/__init__.py`
- `fund_agent/fund/data/__init__.py`
- Focused tests under `tests/ui/` and `tests/services/`
- README updates only if public import paths or testing docs change.

## Acceptance Criteria

- UI no longer imports from `fund_agent.fund.data.thermometer_types`.
- UI can still render plain and JSON thermometer outputs for:
  - legacy public-page snapshot
  - single self-owned thermometer reading
  - batch self-owned thermometer result
- Service no longer imports `ThermometerHistoryCache` or `AkshareThermometerSource` / concrete source internals from their implementation modules for default construction.
- Capability data layer exposes a stable public factory or public aliases sufficient for Service default construction.
- Existing fake injection tests continue to avoid real network.
- Focused pytest and ruff pass.

## Non-Goals

- Do not change thermometer calculation semantics.
- Do not change CLI output schema.
- Do not introduce Application layer if not already present for this path.
- Do not push or mutate GitHub remote state.
- Do not edit `docs/implementation-control.md`; controller will update tracking separately if needed.

## Suggested Shape

- Move concrete default construction behind `fund_agent.fund.data` public functions or aliases.
- Re-export thermometer result dataclasses through `fund_agent.services` if UI still needs `isinstance` dispatch, or provide Service-facing helper functions to convert results into payload shape.
- Keep the patch small and behavior-preserving.
