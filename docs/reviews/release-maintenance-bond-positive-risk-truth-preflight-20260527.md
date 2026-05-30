# Bond Positive-Risk Evidence Gate — Truth Preflight

> Date: 2026-05-27
> Controller: Codex
> Gate: `release-maintenance bond positive-risk evidence gate`
> Scope: truth-source preflight only; no production code, renderer, quality gate, extractor, Service/CLI, Host/Agent/dayu, QDII probing, baseline/golden promotion, or GitHub mutation.

## Startup Packet Replay

| Item | State |
|---|---|
| Current phase | `release maintenance` |
| Current gate | `release-maintenance consolidation / QDII post-021539 disposition accepted locally` |
| Next entry point | `bond positive-risk evidence gate; must use init-agents / tmux multi-agent flow` |
| Current HEAD | `8083340 docs: accept qdii post 021539 disposition` |

This gate follows the Startup Packet next entry point. No cursor switch is required.

## Allowed / Forbidden Scope

Allowed:

- Truth preflight.
- Artifact disposition inventory.
- Docs-only truth-source mismatch recording and minimal repair.
- Plan/review-first bond positive-risk evidence gate for `006597` / 2024.

Forbidden:

- QDII probing.
- FOF taxonomy.
- Golden corpus preflight or promotion.
- Release readiness.
- Production code, renderer, quality gate, extractor, Service/CLI, Host/Agent/dayu changes.
- GitHub mutation.
- Deleting the stray file named `--help` or other untracked files without explicit authorization.

## Truth-Source Mismatch

`docs/implementation-control.md` currently says the phase uses `AGENTS.md` Gate classification rules and requires `fast_path` / `standard` / `heavy` classification before each gate. Direct search in `AGENTS.md` found no `fast_path`, `standard`, or `heavy` rule definitions.

Mismatch:

- Control doc references a rule source that does not currently define the referenced categories.
- Because `AGENTS.md` is the repository's highest-priority execution rule source, this should be fixed before using the classification in the bond gate.

## Minimal Fix Decision

Accepted minimal repair:

- Add a concise `Gate 轻重分类规则` section to `AGENTS.md`.
- Define `fast_path`, `standard`, and `heavy`.
- Preserve current conservative behavior: default `standard`; when unsure choose the heavier class; public contract, schema, quality gate semantics, final judgment, Host/Agent/dayu, external source strategy, release/PR external state, implementation/fix, and baseline/golden promotion cannot use `fast_path`.

Rejected alternative:

- Removing the classification reference from `docs/implementation-control.md`.

Reason: the current control plane and recent gate artifacts already depend on gate classification. Removing the reference would reduce recovery clarity; defining the missing rules in the authoritative execution doc is the smaller and more durable fix.

## Artifact Disposition Inventory

| Path | Category | Decision |
|---|---|---|
| `--help` | stray untracked file | leave untracked; do not stage; ask before delete |
| `docs/reviews/release-maintenance-comprehensive-audit-report-20260526.md` | untracked historical/research input | leave untracked |
| `docs/reviews/release-maintenance-comprehensive-audit-report-20260527.md` | untracked historical/research input | leave untracked |
| `docs/reviews/repo-review-20260526-231040.md` | untracked historical review input | leave untracked unless separately accepted |
| `docs/tmux-agent-memory-store.md` | untracked coordination scratch | leave untracked |

No untracked artifact is promoted by truth preflight.

## Next Step

After the docs-only truth-source mismatch repair, enter `bond positive-risk evidence gate` as a `standard` gate:

- Plan/review first.
- Use `$init-agents` / tmux multi-agent flow.
- Scope evidence to `006597` / 2024 and `bond_risk_evidence_missing.baseline_blocking=true`.
- Do not enter golden corpus or any other cursor.
