# MVP artifact disposition controller judgment

Date: 2026-05-31
Gate: `MVP real-provider / LLM scoring artifact disposition gate`
Session reference: 019e7d70-0019-75c2-85c9-eff1f0764fb0
Baseline: `0e67389 gateflow: accept dayu host truth-source alignment`
Branch: `codex/local-reconciliation`

## Judgment

Pass for disposition planning and control. No runtime, code, tests, score rules, quality-gate rules, golden files, fixtures, PR state, release state, or truth-source semantics were modified.

The correct disposition is:

- preserve durable evidence as reviewed `docs/reviews` summaries and controller judgments;
- keep raw LLM/provider/scoring/quality outputs out of source review;
- add scoped ignores for MVP raw report roots that are repeatable runtime output;
- leave user-owned unknown files unmodified and untracked;
- require explicit user authorization before any deletion.

## Evidence To Preserve

Long-term evidence must be preserved in `docs/reviews`, especially:

- MVP real-provider smoke evidence and controller judgments;
- provider auth, timeout, prompt-contract, writer/auditor, marker repair, L1 calibration, independent body matrix, and runtime-budget/prompt-cost artifacts;
- workspace ownership reconciliation;
- this disposition artifact and this controller judgment.

Raw stdout, stderr, diagnostic JSON, exit codes, scoring byproducts, quality-gate byproducts, snapshots, full prompts, drafts, provider responses, and audit responses are not durable evidence by themselves.

## Raw Scratch Classification

The following roots are classified as regenerable scratch/runtime output, not durable source review material:

- `reports/mvp-local-acceptance/`
- `reports/mvp-provider-runtime-budget-prompt-cost-root-cause-calibration/`
- `reports/mvp-real-provider-smoke-rerun/`
- `reports/scoring-runs/`
- `reports/quality-gate-runs/`
- `reports/extraction-snapshots/`

`reports/scoring-runs/`, `reports/quality-gate-runs/`, and `reports/extraction-snapshots/` were already ignored. This gate adds the three MVP raw report roots to the same generated-output boundary.

## User-Owned Unknown

The following paths are not assigned to this gate and must not be deleted or staged without a separate user decision:

- `docs/tmux-agent-memory-store.md`
- `reviews/audit-report-2025-05-27.md`
- `reviews/audit-report-2025-05-27-v2.md`

## Deletion Boundary

No file was deleted. Any future deletion request must name exact paths and must be preceded by a bounded re-scan for unique evidence and sensitive payloads.

## Baseline Decision

Follow-on gates may continue if preflight shows only:

- untracked `docs/reviews` evidence-chain residuals;
- ignored raw report roots;
- the user-owned unknown paths listed above.

If a later gate sees new tracked dirty, or if raw outputs contain unsummarized unique evidence or sensitive payloads, that gate must stop and report.
