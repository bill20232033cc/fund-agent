# Post-merge Untracked Residue Cleanup Gate Design

Date: 2026-06-18

Branch: `post-merge/pr22-origin-main`

HEAD: `8feb04d`

Verdict: `CLEANUP_GATE_DESIGNED_NOT_READY`

Release/readiness remains `NOT_READY`.

## Goal

Reduce the current untracked workspace residue into explicit dispositions:

1. promote durable evidence only through review;
2. ignore repeatable local/generated outputs that should never become source;
3. record user-owned research/tooling residuals with named owners and next gates;
4. keep source-truth boundaries unchanged.

Current inventory from `git status --short --untracked-files=all`: `120` untracked paths.

## Non-goals

- Do not treat untracked artifacts as design truth, source truth, field correctness proof, parser replacement proof, release proof or readiness proof.
- Do not change production parser, repository behavior, Processor/Extractor behavior, Service/UI/Host/renderer/quality-gate behavior, or PR/release state.
- Do not stage unrelated artifacts into an implementation gate.
- Do not delete, move or archive user-owned files without explicit authorization.
- Do not bulk-read large report/PDF bodies.

## Classification And Proposed Disposition

| Path | Category | Evidence | Decision | Owner | Next gate | Blocker? |
| --- | --- | --- | --- | --- | --- | --- |
| `.mimocode/commands/review-artifact.md`, `.mimocode/plans/1781708023242-clever-rocket.md` | user-owned unknown / local tooling | Local Mimo tooling files; not current source truth. | ignore | User / tooling owner | Slice A ignore update | Yes for clean status |
| `docs/audit/fund-agent-repo-deepreview-20260610.md` | evidence-chain artifact | Historical deep review record. | promote-through-review | Audit owner | Slice B historical evidence promotion | Yes |
| `docs/reviews/*.md`, `docs/reviews/*.json` currently untracked | evidence-chain artifact | 69 historical plan/review/evidence artifacts across Docling, MVP, provider, release-maintenance and repo-review routes. | promote-through-review as evidence chain, not truth source | Controller / artifact owners | Historical evidence promotion gate | Yes |
| `docs/code-wiki-and-audit-report-20260613.md`, `docs/dayu-*`, `docs/liu-chenggang-*`, `docs/learning-roadmap.md`, `docs/next-development-phaseflow.md`, `docs/tmux-agent-memory-store.md`, `docs/superpowers/specs/2026-06-02-template-rebuild-facet-wiring-design.md` | research input / user-owned unknown | Architecture, roadmap and learning notes; not accepted design truth. | leave-untracked with owner / promote only by later review | User / research owner | Slice C research-input decision | Yes |
| `reports/docling-dedicated-extractor-residual-table-shape-diagnostic/`, `reports/docling-field-correctness-anchor-coverage-root-cause/`, `reports/docling-field-correctness-comparative/`, `reports/docling-route-a/` | scratch/runtime output | Candidate Docling diagnostics and benchmark output; current design keeps these candidate-only and not_proven. | ignore | Fund documents evidence owner | Slice A ignore update | Yes |
| `reports/live-evidence/`, `reports/manual-llm-smoke/` | scratch/runtime output | Historical live/manual smoke logs; not current release proof. | ignore | Evidence owner | Slice A ignore update | Yes |
| `reviews/audit-report-2025-05-27.md`, `reviews/audit-report-2025-05-27-v2.md` | evidence-chain artifact | Historical audit reports outside `docs/reviews`. | leave-untracked with owner / promote only by later review | Audit owner | Slice C audit-location decision | Yes |
| `scripts/claude_mimo_simple.py`, `scripts/review-artifact.sh` | user-owned unknown / local tooling | Helper scripts with no accepted repository tooling gate. | leave-untracked with owner / promote only by later review | User / tooling owner | Slice C script tooling decision | Yes |
| `基金年报/` | user-owned data / research input | Local PDFs and analysis reports; production access must go through `FundDocumentRepository`. | ignore | User | Slice A ignore update | Yes |

## Proposed Gate Slices

### Slice A: Ignore Repeatable Local/Generated Families

Allowed edits:

- `.gitignore`

Proposed ignore additions:

- `.mimocode/`
- `基金年报/`
- `reports/docling-dedicated-extractor-residual-table-shape-diagnostic/`
- `reports/docling-field-correctness-anchor-coverage-root-cause/`
- `reports/docling-field-correctness-comparative/`
- `reports/docling-route-a/`
- `reports/live-evidence/`
- `reports/manual-llm-smoke/`

Acceptance:

- `git status --short --untracked-files=all` no longer lists those families.
- No tracked fixture families such as `reports/golden-answers/` or `reports/representation-json/` are ignored or modified.
- No files are deleted.

### Slice B: Promote Historical Evidence Chain

Allowed paths:

- `docs/audit/fund-agent-repo-deepreview-20260610.md`
- untracked `docs/reviews/*.md`
- untracked `docs/reviews/*.json`

Rules:

- Promote only as `evidence-chain artifact`.
- Do not cite these files as current architecture truth unless already absorbed by `docs/design.md` or `docs/implementation-control.md`.
- Run markdown format/sanity checks only; do not rewrite historical conclusions.
- Do not move top-level `reviews/` in this slice.

Acceptance:

- Evidence artifacts are either tracked as historical evidence or left as explicit residuals.
- No artifact is promoted as source truth, readiness proof or parser replacement proof.

### Slice C: User-owned Research And Tooling Decision

Records named residuals and next gates; no destructive action in this cleanup gate:

- top-level research/roadmap docs under `docs/`
- `scripts/claude_mimo_simple.py`
- `scripts/review-artifact.sh`
- top-level `reviews/`

Allowed decisions:

- `leave-untracked`
- `ignore`
- `promote-through-review`

Acceptance:

- Every remaining untracked path has a named owner and next gate.
- No deletion, move or archive is performed.

## Verification Matrix

Run after each slice:

- `git status --short --untracked-files=all`
- `git diff --check -- .gitignore docs/reviews docs/audit`
- `git diff --cached --name-status` before any commit
- `git check-ignore -v <path>` for each newly ignored family

## Stop Conditions

Stop and ask for controller/user decision if:

- a proposed ignore pattern would hide tracked fixtures or accepted evidence;
- a research document appears to contain unique user-authored design intent;
- a report is the only available raw evidence for an accepted artifact;
- any path outside the explicit A-C allowlist appears in `git diff --cached --name-status`;
- deletion, move or archive is requested.

## Recommended Next Action

Run Slice A first. It is non-destructive and should remove the large generated/local families from `git status` without changing source truth. Then run Slice B as a separate evidence promotion review. Slice C remains a named-residual decision record for user-owned research/tooling artifacts.
