# Post-merge Untracked Residue Disposition

Date: 2026-06-18

Verdict: `POST_MERGE_UNTRACKED_RESIDUE_CLASSIFIED_NOT_READY`

Scope: classify the remaining untracked workspace residue after PR #22 was merged into `origin/main` and the local working branch was synchronized to `origin/main` via `post-merge/pr22-origin-main`. This gate does not delete, move, archive, ignore, promote, or read large artifact bodies.

## Preflight

- Branch: `post-merge/pr22-origin-main`
- `HEAD`: `ee2c82ba7f8e54b1390d760bf07f8c3c7ab813e8`
- `origin/main`: `ee2c82ba7f8e54b1390d760bf07f8c3c7ab813e8`
- Tracked status: clean
- Untracked count: 91 paths
- Ignore status: sampled paths are not ignored

## Disposition Table

| Path | Category | Evidence | Decision | Owner | Next gate | Blocker? |
| --- | --- | --- | --- | --- | --- | --- |
| `.mimocode/commands/review-artifact.md` | user-owned unknown / tooling | Local tool command file; not part of current source truth or S2 scope. | leave-untracked | User / tooling owner | Explicit tooling disposition if needed | No for S2; yes for release cleanliness |
| `docs/audit/fund-agent-repo-deepreview-20260610.md` | evidence-chain artifact | Historical audit artifact; control docs already treat audit artifacts as review input, not truth source. | leave-untracked | Audit owner | Separate audit artifact promotion/archive gate if needed | No for S2; yes for release cleanliness |
| `docs/reviews/*.md`, `docs/reviews/*.json` remaining untracked | evidence-chain artifact | 69 historical plan/review/evidence files across release-maintenance, Docling, provider/LLM and repo-review routes; none is current S2 source. | leave-untracked | Artifact owners | Separate historical review residue disposition gate if release readiness is pursued | No for S2; yes for release cleanliness |
| `docs/code-wiki-and-audit-report-20260613.md`, `docs/dayu-*`, `docs/liu-chenggang-*`, `docs/learning-roadmap.md`, `docs/next-development-phaseflow.md`, `docs/tmux-agent-memory-store.md`, `docs/superpowers/specs/*` | research input / user-owned unknown | Architecture/research/roadmap notes. They may inform discussion but are not accepted source truth for S2. | leave-untracked | User / research owner | Explicit research-input gate before promotion | No for S2; yes for release cleanliness |
| `reports/docling-*` | scratch/runtime output | Candidate diagnostics and benchmark matrices; current design keeps Docling evidence candidate-only and not source truth. | leave-untracked | Fund documents research owner | Future evidence/fixture gate if a specific report is needed | No for S2; yes for release cleanliness |
| `reports/live-evidence/*`, `reports/manual-llm-smoke/*` | scratch/runtime output | Historical live/manual smoke logs; not current S2 input and not release proof. | leave-untracked | Evidence owner | Separate live evidence disposition gate if needed | No for S2; yes for release cleanliness |
| top-level `reviews/*.md` | evidence-chain artifact | Historical audit reports outside `docs/reviews`; no current source-truth role. | leave-untracked | Audit owner | Separate review residue disposition gate if needed | No for S2; yes for release cleanliness |
| `scripts/claude_mimo_simple.py`, `scripts/review-artifact.sh` | user-owned unknown / tooling | Untracked helper scripts; no accepted gate promotes them as repository tooling. | leave-untracked | User / tooling owner | Explicit script review gate before promotion | No for S2; yes for release cleanliness |
| `基金年报/` PDFs and markdown reports, `定性分析模板.md` | user-owned data / research input | User data and analysis material; production document access must use `FundDocumentRepository`, not direct files. | leave-untracked | User | Explicit data disposition before any fixture/source use | No for S2; yes for release cleanliness |

## Decisions

- No tracked scratch artifacts are present.
- No untracked residue should be promoted into S2 planning by default.
- No `.gitignore` update is accepted in this gate. The residue is mixed user data, research, historical evidence and runtime output, not one clear repeatable generated-output family.
- No deletion or archive action is authorized.
- Any future deletion requires explicit user authorization.

## S2 Boundary Impact

S2 planning may proceed on tracked `origin/main` source truth only:

- `AGENTS.md`
- `docs/design.md`
- `docs/implementation-control.md`
- `docs/current-startup-packet.md`
- accepted tracked artifacts from PR #22
- current tracked code under `fund_agent/fund/processors/`

The remaining untracked residue cannot be used as source truth, field correctness proof, fixture truth, release proof, readiness proof or parser replacement evidence.

Release/readiness remains `NOT_READY` because untracked residue is still visible and broader readiness residuals remain unresolved.
