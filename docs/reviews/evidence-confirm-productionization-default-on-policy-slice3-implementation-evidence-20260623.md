# Evidence Confirm Default-on Policy Slice EC-DO-3 Implementation Evidence

## Gate

- Work unit: Evidence Confirm Productionization default-on Evidence Confirm policy
- Slice: EC-DO-3 Quality Gate Regression Guard
- Role: implementation worker only
- Design truth: `docs/design.md`
- Control truth: `docs/implementation-control.md`, `docs/current-startup-packet.md`
- Accepted plan: `docs/reviews/evidence-confirm-productionization-default-on-policy-plan-20260623.md`
- Prior accepted slice commit: `115a097`
- Artifact: `docs/reviews/evidence-confirm-productionization-default-on-policy-slice3-implementation-evidence-20260623.md`

## Scope

Allowed changed files:

- `tests/fund/test_quality_gate_integration.py`
- `docs/reviews/evidence-confirm-productionization-default-on-policy-slice3-implementation-evidence-20260623.md`

No production code, score schema, control doc, startup packet, design doc, README, live/PDF/network/provider/LLM path, commit, push or PR state was changed.

## Implementation

- Kept the existing explicit regression that `policy="warn"`, `status="fail"` and `deterministic_status="fail"` maps to `ECQ2/warn` and gate status `warn`.
- Added `test_quality_gate_integration_maps_pathway_fail_warn_policy_to_ecq1_warn` to prove `policy="warn"` plus `pathway_status="fail"` maps to `ECQ1/warn`, not `block`.
- Kept `test_score_json_schema_remains_evidence_confirm_unaware`, proving ECQ issues are absent from `score.json` and only enter `quality_gate.json`.
- Kept and tightened the static boundary guard so `quality_gate_integration.py` imports are checked against repository, source, parser, Docling and provider boundary tokens.

## First-principles Judgment

The existing ECQ implementation is sufficient for product default `warn`: `_ecq_policy_severity()` already maps Evidence Confirm fail summaries to `warn` unless policy is `block`, and rejects invalid `off` fail/warn summaries. EC-DO-3 therefore only needed regression coverage. A production code change would have widened the slice without evidence of a behavior gap.

The quality gate integration remains boundary-safe because the adapter consumes only the already-materialized `EvidenceConfirmProductionSummary`. The static regression confirms it does not import repository, source, parser, Docling or provider modules, and the tests do not read source/PDF/parser artifacts.

## Validation

```text
uv run pytest -q tests/fund/test_quality_gate_integration.py
```

Result: `20 passed in 0.87s`

```text
uv run ruff check tests/fund/test_quality_gate_integration.py
```

Result: `All checks passed!`

```text
git diff --check
```

Result: passed with no output.

## Docs Decision

No docs/control sync was performed in this slice. The accepted plan assigns docs and control sync to EC-DO-4, and the user explicitly forbade control doc changes in this implementation-worker pass.

## Residual Risks And Uncovered Areas

- Fixed in current slice: missing explicit `ECQ1/warn` regression for `policy="warn"` plus `pathway_status="fail"`.
- Fixed in current slice: static quality gate integration boundary guard now covers generic `source` import tokens in addition to repository, parser, Docling and provider.
- Covered by later approved slice: docs/design/control/startup/README synchronization remains EC-DO-4 scope.
- Assigned to later work unit: checklist Evidence Confirm CLI support, provider-backed semantic quality, multi-sample live/source evidence, PR mark-ready, merge and release transition remain outside EC-DO-3.

## Completion Status

IMPLEMENTATION_SLICE_READY_FOR_REVIEW
