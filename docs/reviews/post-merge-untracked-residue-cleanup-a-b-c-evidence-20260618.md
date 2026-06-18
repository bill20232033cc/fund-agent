# Post-merge Untracked Residue Cleanup A-C Evidence

Date: 2026-06-18

Branch: `post-merge/pr22-origin-main`

Verdict: `CLEANUP_A_B_C_COMPLETE_NOT_READY`

Release/readiness remains `NOT_READY`.

## Scope

Executed only Slice A, Slice B and Slice C from
`docs/reviews/post-merge-untracked-residue-cleanup-gate-design-20260618.md`.

No deletion, move or archive action was performed.

## Slice A: Ignore Repeatable Local/Generated Families

Changed file:

- `.gitignore`

Ignored families:

- `.mimocode/`
- `基金年报/`
- `reports/docling-dedicated-extractor-residual-table-shape-diagnostic/`
- `reports/docling-field-correctness-anchor-coverage-root-cause/`
- `reports/docling-field-correctness-comparative/`
- `reports/docling-route-a/`
- `reports/live-evidence/`
- `reports/manual-llm-smoke/`

Validation:

- `git check-ignore -v` confirms the new patterns cover sampled files in `.mimocode/`,
  `基金年报/`, `reports/docling-route-a/`, `reports/live-evidence/` and
  `reports/manual-llm-smoke/`.
- `git ls-files -ci --exclude-standard reports/golden-answers reports/representation-json .mimocode reports/docling-route-a 基金年报`
  produced no output, so tracked `reports/golden-answers/` and `reports/representation-json/`
  fixtures were not hidden by the new ignore rules.
- Visible untracked count after Slice A: `85`.

## Slice B: Promote Historical Evidence Chain

Promoted as evidence-chain artifacts only:

- `docs/audit/fund-agent-repo-deepreview-20260610.md`
- untracked `docs/reviews/*.md`
- untracked `docs/reviews/*.json`

Boundary:

- These files are not promoted as current design truth.
- These files are not source truth, field correctness proof, parser replacement proof, release proof or readiness proof.
- Current truth remains governed by `AGENTS.md`, `docs/design.md`, `docs/implementation-control.md` and accepted current-gate artifacts.

## Slice C: User-owned Research And Tooling Residuals

Remaining visible untracked residuals are intentionally not staged:

| Path | Category | Decision | Owner | Next gate |
| --- | --- | --- | --- | --- |
| `docs/code-wiki-and-audit-report-20260613.md` | research input / user-owned unknown | leave-untracked | User / research owner | Research-input disposition gate |
| `docs/dayu-agent-architect-gap-analysis-20260613.md` | research input / user-owned unknown | leave-untracked | User / research owner | Research-input disposition gate |
| `docs/dayu-agent-codiwiki-and-development-stage-analysis-20260614.md` | research input / user-owned unknown | leave-untracked | User / research owner | Research-input disposition gate |
| `docs/dayu-fund-agent-mvp-gap-discussion-summary-20260613.md` | research input / user-owned unknown | leave-untracked | User / research owner | Research-input disposition gate |
| `docs/learning-roadmap.md` | research input / user-owned unknown | leave-untracked | User / research owner | Research-input disposition gate |
| `docs/liu-chenggang-dayu-ai-coding-roadmap-20260614.md` | research input / user-owned unknown | leave-untracked | User / research owner | Research-input disposition gate |
| `docs/next-development-phaseflow.md` | research input / user-owned unknown | leave-untracked | User / research owner | Research-input disposition gate |
| `docs/superpowers/specs/2026-06-02-template-rebuild-facet-wiring-design.md` | research input / user-owned unknown | leave-untracked | User / research owner | Research-input disposition gate |
| `docs/tmux-agent-memory-store.md` | research input / user-owned unknown | leave-untracked | User / research owner | Research-input disposition gate |
| `reviews/audit-report-2025-05-27.md` | evidence-chain artifact outside canonical review path | leave-untracked | Audit owner | Audit-location disposition gate |
| `reviews/audit-report-2025-05-27-v2.md` | evidence-chain artifact outside canonical review path | leave-untracked | Audit owner | Audit-location disposition gate |
| `scripts/claude_mimo_simple.py` | user-owned unknown / tooling | leave-untracked | User / tooling owner | Script tooling review gate |
| `scripts/review-artifact.sh` | user-owned unknown / tooling | leave-untracked | User / tooling owner | Script tooling review gate |

## Validation Commands

- `git status --short --untracked-files=all`
- `git check-ignore -v ...`
- `git ls-files -ci --exclude-standard ...`
- `git diff --check -- .gitignore docs/reviews docs/audit`
- `git diff --cached --name-status`

## Residual Release Impact

Workspace cleanliness is improved but not fully clean. Remaining user-owned research/tooling residuals still block a strict release/readiness cleanliness check until a separate disposition gate resolves them.
