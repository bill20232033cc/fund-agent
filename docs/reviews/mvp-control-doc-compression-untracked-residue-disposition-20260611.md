# Control-doc Compression Untracked Residue Disposition

日期：2026-06-11

状态：accepted disposition record only；accepted locally at `693638b`.

Scope: classify currently visible untracked residue without deleting, moving, archiving, cleaning, ignoring, staging, importing, promoting, committing, pushing or opening PRs.

## Inventory Evidence

Allowed metadata commands used for inventory:

- `git status --short`
- `git status --branch --short`
- `find docs/audit -maxdepth 2 -type f`
- `find reports/manual-llm-smoke -maxdepth 3 -type f`
- `find fund_agent/tools -maxdepth 3 -type f`
- `find reviews -maxdepth 3 -type f`
- `find 基金年报 -maxdepth 2 -type f`
- `git status --short docs/reviews | wc -l`
- `git ls-files docs/reviews | wc -l`
- `find docs/reviews -maxdepth 1 -type f | wc -l`

Observed metadata:

- Branch: `feat/mvp-llm-incomplete-run-artifacts...origin/feat/mvp-llm-incomplete-run-artifacts [ahead 86]`
- Visible untracked `docs/reviews` entries before this implementation gate added new current-gate artifacts: 34
- Tracked `docs/reviews` files: 2178
- Current `docs/reviews` top-level files: 2212
- `docs/audit/` sample count: 1 file
- `reports/manual-llm-smoke/` sample count: 8 files
- `fund_agent/tools/` sample count: 2 files including one `__pycache__`
- `reviews/` sample count: 2 files
- `基金年报/` sample count: 5 PDF files

No untracked file content, PDF content, runtime report content or source-like residue content was used as proof for current design/control truth.

## Disposition Table

| Path / group | Category | Evidence | Decision | Owner | Next gate | Blocker? |
|---|---|---|---|---|---|---|
| `docs/reviews/mvp-control-doc-compression-accepted-artifact-index-20260611.md` | accepted current-gate artifact | Required allowed write path for the accepted implementation gate | accepted at checkpoint `693638b` | controller | None for this artifact unless future correction is required | No |
| `docs/reviews/mvp-control-doc-compression-historical-ledger-index-20260611.md` | accepted current-gate artifact | Required allowed write path for the accepted implementation gate | accepted at checkpoint `693638b` | controller | None for this artifact unless future correction is required | No |
| `docs/reviews/mvp-control-doc-compression-untracked-residue-disposition-20260611.md` | accepted current-gate artifact | Required allowed write path for the accepted implementation gate | accepted at checkpoint `693638b` | controller | Source-like residue ownership gate for `fund_agent/tools/` | No for this gate; informs next gate |
| `docs/reviews/mvp-control-doc-compression-artifact-hygiene-implementation-evidence-20260611.md` | accepted current-gate artifact | Required allowed write path for the accepted implementation gate | accepted at checkpoint `693638b` | controller | None for this artifact unless future correction is required | No |
| Other untracked `docs/reviews/*.md/json` | evidence-chain artifact | `git status --short` lists 34 untracked `docs/reviews` entries before current-gate writes | `leave-untracked`; `promote-through-review` only if controller maps each exact file to accepted gate | controller / artifact owner | Artifact-specific provenance or evidence acceptance gate | Blocks release/readiness until classified; does not block this docs-only implementation |
| `docs/audit/` | evidence-chain artifact or review artifact | `find docs/audit -maxdepth 2 -type f` lists `docs/audit/fund-agent-repo-deepreview-20260610.md` | `leave-untracked`; possible promotion only through review/provenance gate | controller + reviewer owner | Review-artifact acceptance gate | Blocks release/readiness if unclassified |
| `docs/learning-roadmap.md` | research input | Listed by `git status --short` | `leave-untracked` | user/controller | Research-doc disposition gate | Non-blocking for this gate |
| `docs/next-development-phaseflow.md` | planning/research input | Listed by `git status --short` | `leave-untracked`; do not treat as control truth | controller | Phaseflow planning gate only if explicitly requested | Non-blocking for this gate |
| `docs/superpowers/specs/2026-06-02-template-rebuild-facet-wiring-design.md` | research input / candidate design | Listed by `git status --short` | `leave-untracked`; cannot override `docs/design.md` | design owner/controller | Future design gate | Blocker only if cited as current truth |
| `docs/tmux-agent-memory-store.md` | research/scratch operations note | Listed by `git status --short` | `leave-untracked`; archive requires explicit gate | controller | Ops artifact disposition gate | Non-blocking for this gate |
| `fund_agent/tools/` | source-like residue | `find fund_agent/tools -maxdepth 3 -type f` lists `claude_mimo.py` and one `.pyc` | `leave-untracked`; do not import, stage, promote or clean | controller + implementation owner | Source-like residue ownership gate | Blocks release/readiness until resolved |
| `fund_agent/tools/__pycache__/` | scratch/runtime output under source-like residue | Metadata shows `.pyc` under untracked `fund_agent/tools/` | `leave-untracked`; `.gitignore` update is out of scope | controller | Ignore-rule or source-like residue ownership gate | Blocks clean release hygiene until resolved |
| `reports/manual-llm-smoke/` | scratch/runtime output / live evidence residue | `find reports/manual-llm-smoke -maxdepth 3 -type f` lists 8 files | `leave-untracked`; use as evidence only if exact run artifact is accepted by a reviewed gate | runtime evidence owner/controller | Provider/live evidence disposition gate | Blocks release/readiness if unclassified |
| `reviews/` | obsolete duplicate or external review residue | `find reviews -maxdepth 3 -type f` lists 2 audit reports | `leave-untracked`; archive/delete requires explicit authorization | controller/user | Artifact disposition gate | Blocks release/readiness if unclassified |
| `scripts/claude_mimo_simple.py` | scratch helper | Listed by `git status --short` | `leave-untracked`; do not promote without reviewed tool-support gate | user/controller | Tooling disposition gate | Non-blocking unless imported or used as proof |
| `基金年报/` | user-owned unknown / local PDF corpus | `find 基金年报 -maxdepth 2 -type f` lists 5 PDFs | `leave-untracked`; do not read through filesystem for production proof; deletion requires explicit user authorization | user | Data artifact disposition gate | Blocks release/readiness if unclassified |
| `定性分析模板.md` | user-owned unknown / research input | Listed by `git status --short` | `leave-untracked`; do not promote without docs/design gate | user/controller | Research-doc disposition gate | Non-blocking for this gate |

## Release / Readiness Impact

- Tracked scratch artifacts: not proven by this gate; no tracked-scratch check beyond allowed metadata commands was run.
- Untracked files do not block this docs-only implementation gate if left untouched and classified.
- Untracked files block future release/readiness gates until accepted disposition or explicit cleanup authorization exists.
- `.gitignore` may need a scoped future ignore-rule gate for repeatable runtime outputs such as `__pycache__`, but `.gitignore` is out of scope here.
- Any deletion, archive, cleanup or promotion requires explicit future authorization and a reviewed gate.

## Non-actions

No residue was deleted, moved, archived, cleaned, ignored, staged, imported, promoted, committed, pushed or used as proof.
