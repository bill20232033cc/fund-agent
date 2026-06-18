# Workspace Scope Reconciliation And Artifact Disposition

Date: 2026-06-15

Gate: `Workspace Scope Reconciliation & Artifact Disposition Closeout Gate`

Role: controller

Readiness state: `NOT_READY`

## 1. Scope

This artifact classifies the current dirty workspace before any cleanup, archive, local checkpoint or PR action.

This gate does not delete, move, archive, ignore, stage, commit, push or create a PR.

Current control truth:

- Current active gate: `Docling Baseline Qualification Acquisition Status Planning Gate`
- Current gate type: planning-only
- Current release/readiness state: `NOT_READY`
- Current source policy: EID single-source; no Eastmoney, CNINFO, fund-company website or other fallback re-entry

## 2. Commands Run

```text
git branch --show-current
git status --short
git diff --name-status
git diff --stat
find docs/reviews -maxdepth 1 -type f | wc -l
find docs/reviews -maxdepth 1 -type f -name '*docling-baseline-qualification*' -print | sort
find reports -maxdepth 2 -type f -print | sort
find fund_agent/fund/documents/candidates -maxdepth 3 -type f -print | sort
find tests/fixtures/fund/docling_route_a tests/fund/documents -maxdepth 3 -type f -print | sort | rg 'docling|candidate|repository'
find docs -maxdepth 1 -type f -print | sort
find docs/audit reviews .mimocode -maxdepth 2 -type f -print | sort
find '基金年报' -maxdepth 2 -type f -print | sort
```

## 3. Branch And Dirty State

| Field | State |
|---|---|
| Branch | `feat/mvp-llm-incomplete-run-artifacts` |
| Upstream divergence | ahead `142` |
| Tracked dirty files | 6 |
| Untracked `docs/reviews` files | 2905 files observed under `docs/reviews/` |
| PR suitability | Not suitable for direct PR |
| Cleanup suitability | Suitable only after scoped disposition; destructive cleanup not authorized |
| Archive suitability | Not suitable as a bulk action; archive would change evidence-chain paths |

## 4. Tracked Diff Disposition

| Path | Category | Evidence | Decision | Owner | Next gate | Blocker? |
|---|---|---|---|---|---|---|
| `docs/current-startup-packet.md` | current-control artifact plus accumulated route migration | Diff moves startup packet from old Provider/LLM route to XBRL/Docling route and current Docling acquisition-status planning gate | `promote-through-review`; eligible for scoped control checkpoint only after controller accepts accumulated route migration as current truth | Controller | scoped control checkpoint gate | Yes for PR |
| `docs/implementation-control.md` | current-control artifact plus accumulated route migration | Diff includes XBRL/Docling route queue, residuals, non-goals and current mainline sync | `promote-through-review`; eligible for scoped control checkpoint only after controller accepts accumulated route migration as current truth | Controller | scoped control checkpoint gate | Yes for PR |
| `docs/design.md` | design-truth candidate/update | Diff adds deterministic annual-period non-LLM boundary, repair-budget fact, Route C route de-prioritization, Docling candidate, XBRL HTML render candidate and FDR boundary notes | `promote-through-review`; requires design-truth-sync review before PR | Design owner / controller | design-truth-sync checkpoint gate | Yes for PR |
| `AGENTS.md` | rules-truth tracked diff | Diff is a large rewrite/recompression of execution rules, commands, structure and guardrails | `defer`; do not stage into current Docling closeout without a separate AGENTS rules-sync judgment | Rules owner / controller | AGENTS rules-sync disposition gate | Yes for PR |
| `README.md` | user-facing docs update | Diff adds that `analyze-annual-period` does not accept `--use-llm` and annual-period LLM route remains future design | `promote-through-review`; only with corresponding code/design control checkpoint | Docs owner / controller | docs-sync checkpoint gate | No if left unstaged |
| `tests/fund/documents/test_repository.py` | no-consumption guard test | Diff adds a no-candidate-route assertion for `FundDocumentRepository.load_annual_report` | `promote-through-review`; belongs with Docling candidate-internals / repository-boundary implementation evidence, not current planning-only gate | Fund documents owner | accepted implementation checkpoint reconciliation | Yes for PR if unreviewed |

## 5. Current-gate Untracked Artifact Disposition

| Path | Category | Evidence | Decision | Owner | Next gate | Blocker? |
|---|---|---|---|---|---|---|
| `docs/reviews/docling-baseline-qualification-plan-20260615.md` | current-gate artifact | Accepted by controller judgment | `promote-through-review`; include in scoped checkpoint candidate | Controller | scoped control checkpoint gate | Yes for PR if left untracked |
| `docs/reviews/docling-baseline-qualification-plan-review-ds-20260615.md` | current-gate review artifact | DS initial review | `promote-through-review`; include in scoped checkpoint candidate | Controller / DS | scoped control checkpoint gate | Yes for PR if left untracked |
| `docs/reviews/docling-baseline-qualification-plan-review-mimo-20260615.md` | current-gate review artifact | MiMo initial review | `promote-through-review`; include in scoped checkpoint candidate | Controller / MiMo | scoped control checkpoint gate | Yes for PR if left untracked |
| `docs/reviews/docling-baseline-qualification-plan-rereview-ds-20260615.md` | current-gate re-review artifact | DS closure re-review | `promote-through-review`; include in scoped checkpoint candidate | Controller / DS | scoped control checkpoint gate | Yes for PR if left untracked |
| `docs/reviews/docling-baseline-qualification-plan-rereview-mimo-20260615.md` | current-gate re-review artifact | MiMo closure re-review | `promote-through-review`; include in scoped checkpoint candidate | Controller / MiMo | scoped control checkpoint gate | Yes for PR if left untracked |
| `docs/reviews/docling-baseline-qualification-plan-controller-judgment-20260615.md` | current-gate controller judgment | Verdict `ACCEPT_WITH_BINDING_AMENDMENTS_READY_FOR_ACQUISITION_STATUS_PLANNING_GATE_NOT_READY` | `promote-through-review`; include in scoped checkpoint candidate | Controller | scoped control checkpoint gate | Yes for PR if left untracked |
| `docs/reviews/workspace-scope-reconciliation-artifact-disposition-20260615.md` | current disposition artifact | This artifact | `promote-through-review`; include only if this disposition is accepted | Controller | scoped control checkpoint gate | Yes for PR if left untracked |

## 6. Prior Evidence-chain Artifact Families

| Path / family | Category | Evidence | Decision | Owner | Next gate | Blocker? |
|---|---|---|---|---|---|---|
| `docs/reviews/csrc-eid-*20260614.md` | evidence-chain artifact | XBRL official resource, raw XML blocked proof, HTML render route and evidence artifacts | `leave-untracked` until a scoped evidence-chain checkpoint is opened | Controller / source research owner | evidence-chain checkpoint gate | Yes for PR cleanliness |
| `docs/reviews/funddisclosuredocument-candidate-source-*20260614.md` | evidence-chain artifact | Candidate source design/schema plan and reviews | `leave-untracked` until scoped checkpoint | Controller / Fund documents owner | evidence-chain checkpoint gate | Yes for PR cleanliness |
| `docs/reviews/docling-funddisclosuredocument-*20260615.md` | evidence-chain artifact | Docling mapping/normalization plan, implementation evidence and reviews | `leave-untracked` until implementation checkpoint reconciliation | Controller / Fund documents owner | accepted implementation checkpoint reconciliation | Yes for PR cleanliness |
| `docs/reviews/same-report-*20260614.md`, `docs/reviews/same-report-*20260615.md` | evidence-chain artifact | Same-report route comparison and full representation JSON evidence | `leave-untracked` until evidence-chain checkpoint | Controller | evidence-chain checkpoint gate | Yes for PR cleanliness |
| Other `docs/reviews/*` historical files | evidence-chain or historical review residue | 2905 review files observed; not individually classified in this gate | `leave-untracked`; no bulk archive/delete | Controller / artifact owners | historical residue disposition gate | Yes for PR cleanliness |
| `docs/audit/*`, `reviews/*` | historical audit/review residue | Audit report and top-level review reports present | `leave-untracked`; no body promotion and no archive/delete | Audit owner / controller | historical audit disposition gate | No for current gate, yes for PR cleanliness |

## 7. Runtime / Report / Data Artifact Families

| Path / family | Category | Evidence | Decision | Owner | Next gate | Blocker? |
|---|---|---|---|---|---|---|
| `reports/representation-json/004393_2025_docling_full.json` | candidate durable evidence artifact | Full same-report Docling representation JSON | `leave-untracked`; promote only through evidence/fixture gate | Fund documents owner | Docling acquisition/status or fixture gate | Yes for PR cleanliness |
| `reports/representation-json/004393_2025_pdfplumber_full.json` | candidate durable evidence artifact | Full same-report pdfplumber representation JSON | `leave-untracked`; promote only through evidence/fixture gate | Fund documents owner | Docling acquisition/status or fixture gate | Yes for PR cleanliness |
| `reports/representation-json/004393_2025_eid_html_render_full.json` | candidate durable evidence artifact | Full same-report EID HTML render representation JSON | `leave-untracked`; promote only through evidence/fixture gate | Fund documents owner | Docling acquisition/status or fixture gate | Yes for PR cleanliness |
| `reports/docling-route-a/*` | scratch/runtime output plus evidence support | Local Docling route A generated JSON/Markdown/manifest | `leave-untracked`; do not treat as fixture/source truth | Fund documents owner | fixture/evidence gate if needed | No for current gate, yes for PR cleanliness |
| `reports/golden-answers/*` | candidate durable fixture | Golden answer outputs observed | `leave-untracked`; promote only through reviewed golden fixture gate | Golden owner | golden fixture gate | Yes for PR cleanliness |
| `reports/live-evidence/*`, `reports/manual-llm-smoke/*` | runtime evidence residue | Existing live/manual smoke report directories | `leave-untracked`; do not import into current gate | Runtime evidence owner | runtime residue disposition gate | No for current gate, yes for PR cleanliness |
| `基金年报/*` | user-owned data artifact candidate | Local annual-report PDFs, including `004393` years and other funds | `leave-untracked`; no delete, no body read, no fixture/source truth | User / data owner | data artifact disposition gate | No for current gate, yes for PR cleanliness |

## 8. Source-like / Test-like Untracked Families

| Path / family | Category | Evidence | Decision | Owner | Next gate | Blocker? |
|---|---|---|---|---|---|---|
| `fund_agent/fund/documents/candidates/*.py` | source-like implementation artifact | Candidate document models/failures/locators/normalization helpers | `promote-through-review`; belongs to accepted Docling mapping/normalization implementation checkpoint, not current planning-only gate | Fund documents owner | implementation checkpoint reconciliation | Yes for PR |
| `tests/fund/documents/test_docling_*.py` | test-like implementation artifact | Candidate model, failure, locator, no-consumption and normalization tests | `promote-through-review`; stage only with matching source-like implementation artifact and evidence | Fund documents owner | implementation checkpoint reconciliation | Yes for PR |
| `tests/fixtures/fund/docling_route_a/004393_2025/excerpt.json` | candidate fixture | Docling route A excerpt fixture | `promote-through-review`; fixture gate or implementation checkpoint must accept exact scope | Fund documents owner | fixture/evidence checkpoint gate | Yes for PR |
| `.mimocode/commands/review-artifact.md` | tooling/user-owned unknown | Local agent/tooling command file | `leave-untracked`; no current product scope | Tooling owner | tooling disposition gate | No |
| `scripts/claude_mimo_simple.py`, `scripts/review-artifact.sh` | tooling residue | Local scripts observed as untracked | `leave-untracked`; do not stage without tooling gate | Tooling owner | tooling disposition gate | No |

## 9. Top-level Research Documents

| Path / family | Category | Evidence | Decision | Owner | Next gate | Blocker? |
|---|---|---|---|---|---|---|
| `docs/dayu-*.md`, `docs/*roadmap*.md`, `docs/next-development-phaseflow.md` | research input | Dayu/code-wiki/roadmap/phaseflow notes | `leave-untracked`; may inform future design but not truth source | Research owner / controller | research-input disposition gate | No |
| `docs/tmux-agent-memory-store.md` | tooling/research input | Agent memory/tmux note | `leave-untracked` | Tooling owner | tooling disposition gate | No |
| `.DS_Store` files | scratch/runtime output | Finder metadata observed | `ask-before-delete`; deletion requires explicit cleanup authorization | User / controller | cleanup gate | No |

## 10. Decision

Direct PR is rejected for current workspace state.

Reasons:

1. Branch is ahead `142`, making PR scope already large.
2. Tracked diff spans rules truth, design truth, control truth, README and tests.
3. `docs/current-startup-packet.md` and `docs/implementation-control.md` contain accumulated route migration, not just the latest Docling acquisition-status planning sync.
4. Source-like candidate implementation files and tests are untracked.
5. Runtime/report/data artifacts remain untracked and include candidate durable evidence that should not silently enter product scope.
6. Release/readiness remains `NOT_READY`.

Bulk cleanup and bulk archive are rejected for this gate.

Reasons:

1. Deleting user-owned PDFs, reports or generated JSON is destructive.
2. Archiving review artifacts would mutate evidence-chain paths.
3. Many artifacts are candidates for future reviewed evidence, fixtures or implementation checkpoints.

## 11. Recommended Next Gate

Recommended next gate:

```text
Scoped Accepted Checkpoint Planning Gate
```

Purpose:

- split current dirty workspace into exact checkpoint candidates;
- decide whether to create one or more local commits;
- define exact stage lists;
- keep unrelated residue untracked;
- keep release/readiness `NOT_READY`;
- stop before PR.

Suggested checkpoint slices:

1. `control-route-sync`:
   - `docs/current-startup-packet.md`
   - `docs/implementation-control.md`
   - current route/controller artifacts needed to explain the control truth
2. `docling-candidate-internals`:
   - `fund_agent/fund/documents/candidates/*.py`
   - `tests/fund/documents/test_docling_*.py`
   - `tests/fixtures/fund/docling_route_a/004393_2025/excerpt.json`
   - matching implementation/review/controller artifacts
3. `design-doc-sync`:
   - `docs/design.md`
   - matching design-truth controller artifact
4. `docs-user-surface-sync`:
   - `README.md`
   - only if tied to accepted implementation/design truth
5. `rules-truth-sync`:
   - `AGENTS.md`
   - only after separate AGENTS rules-sync review

## 12. Final Verdict

`VERDICT: WORKSPACE_NOT_READY_FOR_PR_READY_FOR_SCOPED_CHECKPOINT_PLANNING_NOT_READY`
