# Post-P10 Follow-Up Planning

- **Date**: 2026-05-21
- **Previous accepted phase**: P10 repo hygiene / release readiness
- **Current gate**: `P10 merged`
- **Design truth**: `docs/design.md`
- **Control truth**: `docs/implementation-control.md`

## Current State

P10 is closed and merged through PR #6.

Delivered baseline:

- MIT license and package license metadata.
- GitHub Actions CI for `ruff` and `pytest`.
- Narrow generated-output `.gitignore` policy.
- Static `fund_agent.config.paths` defaults and migration guard tests.
- README / package docs / test docs sync.
- PR-level MiMo and GLM review with passing CI.

The project is now in a release-ready repository baseline. No P10 residual blocks product behavior.

## Candidate Backlog After P10

| Candidate | Type | Owner | Decision |
|---|---|---|---|
| P11 control doc hygiene / recovery ergonomics | Process / docs | Controller + plan reviewers | Recommended next phase |
| RR-13 duplicate `016492` source reconciliation | Human data decision | User / App source | Keep human-owned; can run in parallel |
| `fund_agent/fund/tools/` empty directory note | Repo/design fact | Controller | No code phase; design already says no Fund tool runtime exists |
| `docs/repo-audit-20260521.md` local audit input | Local artifact disposition | Controller / user | Keep excluded unless user asks to publish or archive |
| Product features after P9/P10 | Product / Capability | Future design phase | Defer; avoid opening new feature work before control-doc recovery improves |

## First Principles

The design goal is to keep a deterministic, evidence-backed fund analysis main path. After P10, the main technical risk is no longer repository release readiness; it is recovery and coordination cost:

- `docs/implementation-control.md` is the phaseflow truth, but it is now very long.
- The active state is present, yet expensive to recover after compaction or agent handoff.
- Historical evidence must remain durable, but controller startup should not require scanning every historical line.
- The project has accumulated several human-owned or deferred residuals that need clearer active-vs-archive separation.

Therefore the next best phase should improve control-plane ergonomics without changing product behavior.

## Recommended Phase

**Next phase: P11 control doc hygiene / recovery ergonomics.**

First gate:

```text
P11-S1 control doc hygiene and recovery plan/review
```

P11-S1 should produce a code-generation-ready documentation plan before any restructuring.

## Accepted Scope For P11-S1 Planning

The plan must cover:

- A stable active-state section for current branch, gate, next entry point, open risks, and latest accepted artifacts.
- An index or navigation table for historical phase logs.
- A strategy to reduce recovery cost without deleting audit evidence.
- Rules for what remains in `docs/implementation-control.md` versus what can be archived or summarized.
- How to preserve exact artifact paths, commit hashes, PR links, validation results, and residual-risk owners.
- How to keep `docs/design.md` and `docs/implementation-control.md` aligned after the hygiene pass.
- Tests or mechanical checks, if any, that ensure referenced review artifacts still exist.

## Non-Goals

- Do not change source code, product CLI behavior, Fund Capability logic, audit rules, quality gate behavior, renderer output, or extraction logic.
- Do not delete historical review artifacts.
- Do not rewrite history or alter prior accepted gate facts.
- Do not auto-resolve RR-13 duplicate `016492`; it remains user/App-source owned.
- Do not publish or commit `docs/repo-audit-20260521.md` unless a later scope decision explicitly accepts it.
- Do not introduce external Dayu runtime, Host/Engine/tool loop, prompt scene registry, or LLM writing.

## Residual Risks And Owners

| Risk | Owner / Destination | Status |
|---|---|---|
| Control doc readability and recovery cost | P11-S1 | Recommended next phase |
| RR-13 duplicate `016492` | User / App source | Human-owned, not automated |
| `docs/repo-audit-20260521.md` | Local excluded artifact | Keep untracked for now |
| `fund_agent/fund/tools/` empty directory concern | Controller | No implementation needed unless a tracked file appears |
| Future product feature selection | Post-P11 planning | Deferred |

## Controller Decision

Proceed to `P11-S1 control doc hygiene and recovery plan/review`.

This is a planning gate. Implementation must not begin until a plan is reviewed and accepted.

## Next Entry Point

```text
P11-S1 control doc hygiene and recovery plan/review
```
