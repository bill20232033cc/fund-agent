# Control-doc Compression / Artifact Hygiene Implementation Evidence

日期：2026-06-11

角色：implementation worker

状态：accepted implementation evidence；accepted locally at `693638b`.

## Scope

Implemented the accepted `Control-doc compression / artifact hygiene implementation gate` with the amended controller scope from `docs/reviews/mvp-control-doc-compression-artifact-hygiene-plan-controller-judgment-20260611.md`.

## Changed Files

| File | Action | Purpose |
|---|---|---|
| `docs/current-startup-packet.md` | compressed/replaced active startup surface | Keep short resume entry with current phase, current gate, next entry, truth docs, accepted artifact summary, open residuals and non-goals |
| `docs/implementation-control.md` | compressed/replaced active control surface | Keep current control truth and index links instead of full long accepted ledger |
| `docs/reviews/mvp-control-doc-compression-accepted-artifact-index-20260611.md` | created | Evidence-chain index grouped by gate family |
| `docs/reviews/mvp-control-doc-compression-historical-ledger-index-20260611.md` | created | Historical/superseded ledger index |
| `docs/reviews/mvp-control-doc-compression-untracked-residue-disposition-20260611.md` | created | Current visible untracked residue classification and deferred-owner table |
| `docs/reviews/mvp-control-doc-compression-artifact-hygiene-implementation-evidence-20260611.md` | created | This evidence record |

## Implementation Notes

- Slice A: active startup/control surface now uses short current-truth sections plus index links. It still answers current phase, current gate, next entry, control truth, design truth, current accepted checkpoint, open residuals and non-goals.
- Slice B: accepted artifact and historical ledger material moved into evidence-chain index artifacts. These artifacts explicitly do not override `AGENTS.md`, `docs/design.md`, startup packet or control truth.
- Slice C: visible untracked residue is classified by group with category/evidence/decision/owner/next gate/blocker. No cleanup or promotion was performed.

## Boundary Compliance

Not touched:

- `docs/design.md`
- `.gitignore`
- source modules under `fund_agent/`
- tests under `tests/`
- runtime reports under `reports/`
- PDF/document corpus
- reviewer artifacts
- controller artifacts

Not run:

- live EID/network/PDF/FDR/FundDocumentRepository/helper/fallback/provider/LLM commands
- extractor/analyze/checklist/golden/readiness/score-loop/release commands
- stage/commit/push/PR/merge commands

Not performed:

- delete/move/archive/clean/ignore/import/stage/promote of untracked residue
- use of arbitrary untracked residue as root-cause proof or accepted fixture

## Metadata Evidence Before Final Validation

- `git status --branch --short` showed branch `feat/mvp-llm-incomplete-run-artifacts...origin/feat/mvp-llm-incomplete-run-artifacts [ahead 86]` with visible untracked residue groups.
- `git status --short docs/reviews | wc -l` showed 34 untracked `docs/reviews` entries before this implementation added current-gate artifacts.
- `git ls-files docs/reviews | wc -l` showed 2178 tracked `docs/reviews` files.
- `find docs/reviews -maxdepth 1 -type f | wc -l` showed 2212 top-level `docs/reviews` files.
- `wc -l docs/implementation-control.md docs/current-startup-packet.md` before compression showed 851 and 529 lines.

## Validation

Allowed validation commands run after the implementation write:

| Command | Result |
|---|---|
| `git status --short` | Shows only two tracked modified allowed files plus the four new current-gate artifacts and pre-existing untracked residue; no staged files |
| `git status --branch --short` | Branch `feat/mvp-llm-incomplete-run-artifacts...origin/feat/mvp-llm-incomplete-run-artifacts [ahead 86]`; no staged files |
| `git diff --check` | PASS; no output |
| `wc -l docs/implementation-control.md docs/current-startup-packet.md docs/reviews/mvp-control-doc-compression-accepted-artifact-index-20260611.md docs/reviews/mvp-control-doc-compression-historical-ledger-index-20260611.md docs/reviews/mvp-control-doc-compression-untracked-residue-disposition-20260611.md docs/reviews/mvp-control-doc-compression-artifact-hygiene-implementation-evidence-20260611.md` | `123`, `94`, `44`, `58`, `70`, `82` lines after final evidence update |
| `rg -n "Next entry point|Current gate|Current active gate|Control-doc compression|artifact hygiene|accepted-artifact-index|historical-ledger-index|untracked-residue-disposition|docs/design.md|\\.gitignore|pending review/controller" ...` | PASS at implementation-write time; current gate, next entry, index links, prohibited-scope wording and pending-review status were discoverable before controller acceptance |

## Residuals

| Residual | Owner | Next handling |
|---|---|---|
| This implementation required review/controller acceptance | reviewer/controller | Completed by DS/MiMo reviews and controller judgment; accepted at `693638b` |
| The active docs are compressed but may still need review-driven tightening | controller | Follow-up compression only if reviewer/controller requests it |
| Untracked residue remains | controller / artifact owners | Use disposition artifact; no cleanup in this gate |
| `fund_agent/tools/` source-like residue remains | controller + implementation owner | Source-like residue ownership gate |
| Release/readiness cleanliness unproven | release owner | Release-readiness gate after accepted disposition |
