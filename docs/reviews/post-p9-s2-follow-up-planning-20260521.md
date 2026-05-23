# Post-P9-S2 Follow-Up Planning

- **Date**: 2026-05-21
- **Baseline commit**: `fe5f2dc`
- **Previous accepted slice**: P9-S2 quality gate / golden coverage calibration
- **Current gate**: `P9-S2 accepted`

## Baseline

P9 now has two accepted slices:

- P9-S1 hardened the `analyze` product contract:
  - product mode exposes only user-safe minimal inputs;
  - developer-only inputs require `developer_override` / `--dev-override`;
  - final judgment is derived by Fund Capability and audited through selected/derived/source;
  - product mode keeps quality gate `block` fail-closed.
- P9-S2 calibrated quality gate and strict golden coverage:
  - selected-pool membership remains `docs/code_20260519.csv`;
  - missing strict golden coverage is `FQ0/info`, not `gate_not_run`;
  - explicit correctness mismatch remains `FQ1/block`;
  - unknown unavailable correctness coverage metadata fails closed;
  - CLI emits fund-scoped `quality_gate_info` without changing exit status.

Current verification baseline:

- `.venv/bin/python -m pytest -q` -> `377 passed`
- `.venv/bin/ruff check .` -> passed
- `git diff --check` -> passed

## Remaining Options

### Option A - Open another P9 product slice

Possible candidates include thermometer-to-valuation mapping, correctness-required policy, broader strict golden coverage, or report UX improvements around quality gate messages.

Decision: do not start another P9 product slice now. These candidates either require new evidence/design input or were explicitly non-goals of P9-S1/P9-S2. Starting them immediately would expand P9 beyond the product-contract hardening objective.

### Option B - Repo hygiene / control-doc hygiene

Repo hygiene remains useful: LICENSE, CI, `.gitignore`, default path cleanup, and control doc readability. These are not part of the P9 product contract and should remain separate maintenance slices.

Decision: defer. They should not block P9 aggregate review.

### Option C - P9 aggregate readiness and deepreview

P9 changed the user-facing `analyze` contract, Service quality-gate state machine inputs, final judgment derivation path, and strict golden coverage semantics. P9-S2 also completed with a recorded review limitation: AgentDS did not produce a durable code-review artifact, AgentGLM was unavailable, and AgentCodex/AgentMiMo had participated in implementation.

Decision: accept this as the next step. Aggregate review is the right gate to validate cross-slice behavior and compensate for the P9-S2 independent-review limitation before any draft-PR/readiness decision.

## Controller Decision

**Next gate: P9 aggregate readiness reconciliation, then P9 aggregate deepreview.**

No new P9 implementation slice should start before aggregate review unless a blocking readiness issue is discovered.

Aggregate review must focus on:

- Product mode cannot consume developer-only override fields.
- `quality_gate_policy=block` remains the product default.
- `gate_not_run` remains limited to pre-gate execution/membership/source failure.
- Missing strict golden correctness coverage remains visible as `FQ0/info`, not a product bypass or false failure.
- Explicit correctness mismatch, malformed golden files, malformed score correctness schemas, and low-quality extraction signals remain fail-closed.
- Final judgment derivation still respects quality gate pass/warn/block/not-run state and does not silently recommend buy/sell language.
- README and package docs describe current behavior without future-policy drift.

## Agent Routing

Preferred aggregate reviewers:

- AgentDS
- AgentGLM

Current availability caveat:

- AgentDS pane previously became stuck in Claude compacting during P9-S2 review and produced no artifact.
- AgentGLM pane has API 401.
- AgentMiMo implemented P9-S2 as a substitute and should not be treated as independent reviewer for P9-S2-specific findings, but may still provide an aggregate pass if the controller records the limitation.

Controller requirement for the next gate:

- First try to restore/refresh AgentDS and AgentGLM.
- If two independent aggregate reviewers cannot be obtained, record the exact unavailability and ask whether to proceed with a single-reviewer aggregate risk exception or pause for agent recovery.

## Next Entry Point

`P9 aggregate readiness reconciliation`
