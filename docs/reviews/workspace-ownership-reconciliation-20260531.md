# Workspace Ownership Reconciliation - 2026-05-31

## Scope

- Work unit: narrow preflight reconciliation only.
- Branch: `codex/local-reconciliation`.
- Runtime changes: not modified.
- Files deleted: none.
- Push / PR / merge / release: not performed.
- Dayu truth-source alignment gate: not resumed.

## Commands Run

```text
git branch --show-current
git status --short
git diff --name-status
git diff --stat
git ls-files --others --exclude-standard
```

## Git Evidence Summary

- Current branch is `codex/local-reconciliation`.
- Tracked dirty scope has 18 modified files and a large runtime/test/doc diff:
  - `18 files changed, 6888 insertions(+), 318 deletions(-)`.
- Tracked dirty files include runtime, CLI, config, tests, README, and control/startup docs.
- Untracked files include many historical `docs/reviews/` artifacts, `reports/` evidence directories, a top-level `reviews/` directory, `docs/tmux-agent-memory-store.md`, and a suspicious top-level `--help` file.

## Classification

### prior accepted gate tracked changes

These tracked modifications appear to belong to prior provider runtime / prompt-cost / real-provider stabilization gates and should be treated as the candidate baseline for any later docs-only gate, not mixed into the new dayu truth-source alignment gate:

```text
docs/current-startup-packet.md
docs/implementation-control.md
fund_agent/config/README.md
fund_agent/config/llm.py
fund_agent/fund/README.md
fund_agent/fund/chapter_auditor.py
fund_agent/fund/chapter_writer.py
fund_agent/services/chapter_orchestrator.py
fund_agent/services/llm_provider.py
fund_agent/ui/cli.py
tests/README.md
tests/config/test_llm_config.py
tests/fund/test_chapter_auditor.py
tests/fund/test_chapter_writer.py
tests/services/test_chapter_orchestrator.py
tests/services/test_final_chapter_assembler.py
tests/services/test_llm_provider.py
tests/ui/test_cli.py
```

Recommendation:

- Create an accepted local checkpoint for the previous gate before starting the dayu truth-source alignment gate, provided the previous gate artifacts and validation evidence are accepted.
- Do not modify these runtime/test files in the dayu truth-source alignment gate.
- `docs/current-startup-packet.md` and `docs/implementation-control.md` are also later docs gate candidates, but their current dirty content should first be checkpointed or explicitly accepted as baseline to avoid blending gates.

### current docs gate candidate files

Only the following files should be touchable by the later `MVP dayu.host runtime governance truth-source alignment gate` after this reconciliation is resolved:

```text
docs/design.md
docs/implementation-control.md
docs/current-startup-packet.md
docs/reviews/mvp-dayu-host-runtime-governance-truth-source-alignment-plan-20260531.md
docs/reviews/mvp-dayu-host-runtime-governance-truth-source-alignment-evidence-20260531.md
docs/reviews/mvp-dayu-host-runtime-governance-truth-source-alignment-controller-judgment-20260531.md
```

Recommendation:

- Proceed with the docs gate only after the prior accepted gate tracked changes are committed or the user explicitly authorizes treating the current tracked dirty tree as baseline.
- Keep the docs gate docs-only: no runtime, tests, fixtures, golden data, PR state, push, merge, or release changes.

### unrelated untracked artifacts

These untracked paths are historical review/evidence artifacts or report outputs. They should not be deleted by this reconciliation pass.

Representative groups:

```text
docs/reviews/mvp-*.md
docs/reviews/release-maintenance-*.md
docs/reviews/repo-review-*.md
reports/mvp-local-acceptance/
reports/mvp-provider-runtime-budget-prompt-cost-root-cause-calibration/
reports/mvp-real-provider-smoke-rerun/
reviews/
```

Recommendation:

- Keep as untracked artifacts unless a specific previous gate requires promoting selected files into an accepted commit.
- Do not include broad historical `reports/` or `reviews/` directories in the dayu docs gate.
- If these artifacts are no longer needed, deletion or ignore-policy changes require a separate user decision; this pass does neither.

### suspicious / requires user decision

```text
--help
```

Recommendation:

- Requires user decision.
- It looks like an accidental output or typo artifact, but this reconciliation pass must not delete files.
- Do not stage it into any gate checkpoint unless the user identifies it as intentional.

### unclear ownership

```text
docs/tmux-agent-memory-store.md
```

Recommendation:

- Ownership is unclear from the requested evidence alone.
- Keep untracked and do not include in the dayu docs gate.
- Ask user before staging, ignoring, moving, or deleting.

## Gate Readiness Decision

- Tracked dirty ownership: likely prior accepted gate, but not safe to treat as clean baseline until checkpointed or explicitly user-approved.
- Exact files allowed for the future dayu docs gate: listed in `current docs gate candidate files`.
- Need previous checkpoint first: yes, unless user explicitly authorizes proceeding on top of the current dirty tracked tree.

## Executable Next Step

`commit_previous_gate_first`

Rationale: the tracked dirty tree contains broad runtime/test/doc changes from prior gates. Starting a new docs-only truth-source alignment gate on top of those uncommitted changes would make file ownership and accepted checkpoint boundaries ambiguous.
