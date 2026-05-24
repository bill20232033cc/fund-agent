# Release Maintenance Design Boundary Correction - Controller Judgment

Date: 2026-05-23

## Gate

`release maintenance design boundary correction`

## Trigger

After RM-B2 closed the UI -> Application boundary in code, `docs/design.md` still contained local unaccepted wording that replaced the repository boundary model with Dayu-style `UI -> Service -> Host -> Agent` and required future Host/Agent implementation to use external `dayu.host` / `dayu.engine`.

That wording conflicted with the user-provided `AGENTS.md` rules for this repository:

- `AGENTS.md` is the authoritative rule source for agents.
- The module boundary is UI / Application / Runtime / Service / Engine / Capability.
- Dayu is methodology and historical research reference only.
- The current production mainline must not depend on external `dayu-agent` runtime, Host, Engine, tool loop, or external Dayu API.

## Decision

Accepted a controller-owned design-truth correction.

## Scope

Changed only `docs/design.md` to:

- restore the six-layer UI / Application / Runtime / Service / Engine / Capability architecture;
- record RM-B2 current-state fact that CLI production paths call Application use-case facades;
- preserve true product facts from P19-S5 and RM-B2, including `wind_all_a` as the default thermometer CLI target and the implemented `fund-analysis checklist` command;
- keep Dayu manuals as engineering and boundary-discipline reference, not as production runtime dependency or target architecture;
- keep explicit-parameter rules: business parameters must stay in typed request / contract / config, not `extra_payload`;
- update plan-review checks to enforce the six-layer boundary and external-Dayu-runtime non-dependency.

## Non-Scope

- No production code changes.
- No test or fixture changes.
- No push, PR, reviewer request, branch deletion, issue mutation, or external action.
- No staging of the local conflicting `AGENTS.md` diff or unrelated deleted documents.

## Validation

- `rg` conflict scan over `docs/design.md` found no residual `dayu.host`, `dayu.engine`, Dayu four-layer target, or external Host/Agent requirement wording.
- `git diff --check docs/design.md` passed.

## Residuals

- `fund_agent/runtime` and `fund_agent/engine` remain unimplemented and should only be planned when a real runtime/tool-loop requirement exists.
- Local `AGENTS.md` remains conflicted with the user-provided authoritative rules and must not be staged without explicit user decision.
- Existing unrelated deletions, including `LICENSE`, remain outside this gate.
