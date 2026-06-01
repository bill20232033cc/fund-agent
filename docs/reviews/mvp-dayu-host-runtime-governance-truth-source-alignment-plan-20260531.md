# MVP dayu.host Runtime Governance Truth-Source Alignment Plan

- Gate: `MVP dayu.host runtime governance truth-source alignment gate`
- Role: Gateflow controller docs-only plan.
- Date: 2026-05-31
- Classification: `heavy`

## Goal

Align design/control truth so `dayu.host runtime governance adapter gate` is no longer optional future work. It is a user-facing MVP readiness prerequisite. Keep `dayu.engine` as a later Agent/tool-loop migration.

## Evidence

- `AGENTS.md` fixes the target architecture as `UI -> Service -> Host -> Agent`.
- Current accepted provider/runtime checkpoint: `b3a769b`.
- Latest provider runtime/prompt-cost controller judgment accepts runtime-cost diagnostics locally but leaves real provider smoke blocked by `provider_runtime_timeout_small_prompt`.
- Current implementation path remains `CLI -> Service -> fund_agent/fund -> provider HTTP call`.

## Non-Goals

- No runtime implementation.
- No tests/runtime/README edits.
- No `AGENTS.md` edits.
- No golden, fixtures, score, quality gate, PR state, push, merge or release.
- Do not touch `--help`, `docs/tmux-agent-memory-store.md`, historical reports or unrelated reviews.

## Required Truth Changes

1. `docs/design.md`
   - Mark current path as `CLI -> Service -> fund_agent/fund -> provider HTTP call`.
   - Record missing runtime governance: global deadline, cancel, terminal run state, safe diagnostics and run lifecycle.
   - Split Route C Gate 5 into `Gate 5A dayu.host runtime governance adapter` and `Gate 5B dayu.engine Agent/tool-loop migration`.
   - State that runtime budget / prompt-cost / shim remains transitional.

2. `docs/implementation-control.md`
   - Set next entry to `MVP dayu.host runtime governance adapter plan gate`.
   - Record `dayu.host` as user-facing MVP readiness prerequisite.
   - Keep provider endpoint small-prompt calibration as later diagnostic work.

3. `docs/current-startup-packet.md`
   - Keep startup short.
   - Make `dayu.host` prerequisite clear.
   - Keep `dayu.engine` deferred.

## Validation

- Run `git diff --check`.
- Ruff/pytest are not required because this is docs/control artifact only and does not modify runtime code.

## Stop Conditions

- Any runtime/test/README/golden/quality/PR/release change is required.
- Any need to edit `AGENTS.md`.
- Future design cannot be distinguished from current implementation.
- New tracked dirty outside the allowed docs set appears.
