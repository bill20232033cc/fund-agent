# MVP Data Artifact Disposition Planning Gate — 2026-06-12

Role: planning worker, not controller.

Gate: `Data Artifact Disposition Planning Gate` for `基金年报/` PDFs.

Target candidate group: `基金年报/`.

## 1. Gate Summary

This is a non-live metadata-only planning gate for five local PDF data artifacts under `基金年报/`.

Planning objective:

- Classify the `基金年报/` PDFs as user/data artifact candidates using metadata only.
- Prevent local PDFs from becoming fixtures, source truth, release evidence or readiness proof merely because they are present in the workspace.
- Define a bounded next evidence gate that can disposition the PDFs without reading PDF bodies.
- Preserve `NOT_READY`.

This plan does not authorize PDF body reads, PDF text extraction, source/test/runtime behavior changes, design/startup/control/README/`.gitignore` edits, file cleanup, archive, delete, move, ignore, import, promote, stage, commit, push, PR, merge, release, or live/provider/EID/network/PDF/FDR/LLM/analyze/checklist/golden/readiness/release commands.

## 2. Inputs and Prohibited Inputs

Allowed inputs read in this planning gate:

- `AGENTS.md`
- `docs/design.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/reviews/mvp-audit-artifact-disposition-evidence-controller-judgment-20260612-135642.md`
- `docs/reviews/mvp-control-doc-compression-untracked-residue-disposition-20260611.md`
- `docs/reviews/mvp-control-doc-compression-accepted-artifact-index-20260611.md`
- `docs/reviews/mvp-control-doc-compression-historical-ledger-index-20260611.md`

Allowed metadata-only commands performed:

- `git status --short`
- `git status --branch --short`
- `git diff --check`
- `git ls-files -- 基金年报`
- `git check-ignore -v 基金年报`
- `find 基金年报 -maxdepth 2 -type f -print`
- `find 基金年报 -maxdepth 1 -type f -exec wc -c {} +`
- `du -sh 基金年报`

Prohibited inputs/actions not used:

- PDF body reads
- PDF text extraction
- source/test/runtime file inspection
- report/audit/user-owned document body reads beyond allowed docs
- live/provider/EID/network/PDF/FDR/LLM/analyze/checklist/golden/readiness/release commands
- cleanup, archive, delete, move, ignore, import, promote, stage or commit

## 3. Repository Facts Observed From Metadata Only

Repository facts:

| Fact | Evidence |
|---|---|
| Current branch is `feat/mvp-llm-incomplete-run-artifacts...origin/feat/mvp-llm-incomplete-run-artifacts [ahead 169]`. | `git status --branch --short` |
| `基金年报/` is visible as untracked residue. | `git status --short` |
| `git ls-files -- 基金年报` returned no tracked path. | tracked-status metadata |
| `git check-ignore -v 基金年报` returned no ignore match. | ignore-status metadata |
| `基金年报/` contains five files at max depth 2. | `find 基金年报 -maxdepth 2 -type f -print` |
| Total byte count is 8097390. | `find 基金年报 -maxdepth 1 -type f -exec wc -c {} +` |
| Directory size is 7.7M. | `du -sh 基金年报` |
| `git diff --check` passed with no output. | whitespace validation |

Observed candidate files:

| Path | Size bytes |
|---|---:|
| `基金年报/摩根标普500指数型发起式证券投资基金(QDII)2024年年度报告.pdf` | 2970819 |
| `基金年报/招商中证1000指数增强型证券投资基金2024年年度报告.pdf` | 852514 |
| `基金年报/安信企业价值优选混合型证券投资基金2024年年度报告.pdf` | 841826 |
| `基金年报/易方达沪深300交易型开放式指数发起式证券投资基金联接基金2024年年度报告.pdf` | 2639303 |
| `基金年报/国泰利享中短债债券型证券投资基金2024年年度报告.pdf` | 792928 |

Truth-doc facts:

| Category | Fact | Source |
|---|---|---|
| truth-doc fact | Current gate is `Data Artifact Disposition Planning Gate` for `基金年报/` PDFs. | startup packet / implementation-control |
| truth-doc fact | Current annual-report source policy is EID single-source operational no-live implementation; fallback/source expansion is not authorized here. | design / startup packet / implementation-control |
| truth-doc fact | Production annual-report access must go through `FundDocumentRepository`; Service, UI, Host, renderer and quality gate must not directly call concrete source, PDF cache or download helpers. | `AGENTS.md`, design/control docs |
| truth-doc fact | Evidence-chain indexes do not override `AGENTS.md`, `docs/design.md`, startup packet or control truth. | startup packet / accepted artifact index / historical ledger index |
| truth-doc fact | Untracked residue does not become accepted proof unless a controller judgment accepts that exact artifact in a reviewed gate. | accepted artifact index |
| accepted residual | `基金年报/` PDFs were previously classified as user-owned unknown / local PDF corpus and release/readiness blocker until disposition. | untracked residue disposition index |
| accepted residual | Audit artifact disposition evidence accepted `docs/audit/...` as historical review input only and preserved `NOT_READY`; next mainline is data artifact disposition. | audit artifact disposition evidence controller judgment |
| truth-doc fact | Release/readiness remains `NOT_READY`; no path is accepted as release evidence or readiness proof. | startup packet / implementation-control / controller judgments |

No PDF content, text, metadata embedded inside PDF, hash, source identity, or document integrity was read or accepted in this planning gate.

## 4. Proposed Artifact Disposition Policy

Default classification: `user-owned/data artifact candidate`.

Default disposition: `leave-untracked`.

Policy:

- A later metadata-only evidence gate is sufficient to disposition the current `基金年报/` residue as user-owned data artifacts left untracked, because the required question is artifact ownership/release-readiness routing, not PDF content correctness.
- PDF body read is not needed for that disposition and must remain prohibited by default.
- PDF body read may only be considered in a future, explicitly authorized fixture/source-identity/data-ingestion gate that proves why metadata is insufficient.
- These PDFs must not become fixtures, source truth, release evidence, readiness proof, golden inputs, source identity proof, or product scope merely because they are present in the workspace.
- These PDFs must not be used to bypass `FundDocumentRepository` or current EID single-source/no-fallback source policy.
- Cleanup, deletion, archive, import, promotion, ignore-rule changes, staging or commit require separate reviewed authorization; deletion requires explicit user authorization.

Disposition table for the candidate group:

| Path / group | Category | Evidence | Decision | Owner | Next gate | Blocker? |
|---|---|---|---|---|---|---|
| `基金年报/` (5 PDFs) | `user-owned/data artifact candidate` | metadata-only: untracked, not ignored, five PDF filenames, total 8097390 bytes / 7.7M | `leave-untracked` pending evidence gate acceptance; no body read | User / data-artifact owner + controller | Metadata-only data artifact disposition evidence gate | Blocks release/readiness until accepted disposition; does not block this planning gate |

## 5. Plan Steps

1. Evidence worker reads the accepted planning/control baseline:
   - `AGENTS.md`
   - `docs/design.md`
   - `docs/current-startup-packet.md`
   - `docs/implementation-control.md`
   - this plan after acceptance
   - this plan's controller judgment after acceptance
   - `docs/reviews/mvp-audit-artifact-disposition-evidence-controller-judgment-20260612-135642.md`
   - accepted artifact index, historical ledger index, untracked residue disposition index

2. Evidence worker re-runs metadata-only checks:
   - `git status --short`
   - `git status --branch --short`
   - `git diff --check`
   - `git ls-files -- 基金年报`
   - `git check-ignore -v 基金年报`
   - `find 基金年报 -maxdepth 2 -type f -print`
   - `find 基金年报 -maxdepth 1 -type f -exec wc -c {} +`
   - `du -sh 基金年报`

3. Evidence worker writes only:
   - `docs/reviews/mvp-data-artifact-disposition-evidence-20260612.md`

4. Evidence artifact must:
   - identify the exact PDF paths and sizes from metadata only
   - classify the group as `user-owned/data artifact candidate`
   - recommend `leave-untracked`
   - explicitly reject fixture/source-truth/release-evidence/readiness-proof treatment
   - state that PDF body read is unnecessary for this disposition
   - preserve `NOT_READY`

5. MiMo and DS review the evidence artifact for boundary compliance.

6. Controller issues judgment. If accepted, controller may sync control docs in a separate controller-authorized sync action.

## 6. Accepted Write Set

This planning gate write set:

- `docs/reviews/mvp-data-artifact-disposition-plan-20260612.md`

Recommended next evidence gate write set:

- `docs/reviews/mvp-data-artifact-disposition-evidence-20260612.md`

Recommended review/controller artifacts after evidence worker completes:

- `docs/reviews/mvp-data-artifact-disposition-evidence-review-mimo-20260612.md`
- `docs/reviews/mvp-data-artifact-disposition-evidence-review-ds-20260612.md`
- `docs/reviews/mvp-data-artifact-disposition-evidence-controller-judgment-20260612-*.md`

No other write paths are authorized. The evidence worker must not modify source, tests, runtime, `docs/design.md`, `docs/current-startup-packet.md`, `docs/implementation-control.md`, README files, `.gitignore`, `基金年报/`, report artifacts, existing review artifacts, or any PDF.

## 7. Validation Matrix

| Validation | Purpose | Expected evidence | Allowed in planning gate | Allowed in next evidence gate |
|---|---|---|---|---|
| `git status --short` | Confirm residue remains visible and detect unintended edits | `基金年报/` remains untracked; no source/test/runtime/design/startup/control/README/`.gitignore` edits | Yes | Yes |
| `git status --branch --short` | Record branch context | Branch/ahead count only | Yes | Yes |
| `git diff --check` | Whitespace validation for written artifact | No output | Yes | Yes |
| `git ls-files -- 基金年报` | Confirm tracked status | No tracked path output unless state changes before evidence gate | Yes | Yes |
| `git check-ignore -v 基金年报` | Confirm ignore status | No ignore match unless state changes before evidence gate | Yes | Yes |
| `find 基金年报 -maxdepth 2 -type f -print` | Confirm candidate inventory | Same five PDF paths unless workspace changes | Yes | Yes |
| `find 基金年报 -maxdepth 1 -type f -exec wc -c {} +` | Confirm file sizes and total bytes without body read | Same size table unless workspace changes | Yes | Yes |
| `du -sh 基金年报` | Confirm aggregate directory size | `7.7M` unless workspace changes | Yes | Yes |

Explicitly disallowed validation:

- PDF body read or text extraction
- PDF integrity/hash/source identity checks unless separately authorized
- live/provider/EID/network/PDF/FDR/LLM commands
- `fund-analysis analyze`, `checklist`, golden, readiness or release commands
- source/test/runtime command suites
- cleanup/archive/delete/move/ignore/import/promote/stage/commit/push/PR/merge actions

## 8. Review / Controller Lifecycle

Required lifecycle:

1. Planning artifact written by planning worker.
2. MiMo plan review.
3. DS plan review.
4. Controller judgment on plan.
5. Accepted local checkpoint for planning gate if controller accepts.
6. Metadata-only evidence worker executes next gate under accepted boundaries.
7. MiMo evidence review.
8. DS evidence review.
9. Controller judgment on evidence.
10. Accepted checkpoint if controller accepts.
11. Control-doc sync only after accepted checkpoint and only in a separate controller-authorized sync action.

Review focus:

- Verify no PDF body read or text extraction occurred.
- Verify metadata-only inventory is complete and consistent.
- Verify PDFs are not accepted as fixtures, source truth, release evidence, readiness proof or product scope.
- Verify no cleanup/delete/archive/move/import/promote/ignore/stage/commit action is implied.
- Verify `NOT_READY` is preserved.

## 9. Residuals and Next Entry Point

Residuals after this planning gate:

| Residual | Classification | Owner | Next handling |
|---|---|---|---|
| `基金年报/` PDFs remain untracked and user/data-owned candidate artifacts. | `deferred_candidate` | User / data-artifact owner + controller | Metadata-only evidence gate |
| PDF body content, source identity, integrity and suitability as fixtures remain unknown. | `deferred_candidate` | User / data-artifact owner / future fixture owner | No body read unless future gate proves need |
| Release/readiness evidence gap remains. | `accepted_residual` | Release owner | Separate readiness/live evidence gate after residue disposition |
| Cleanup/delete/archive/import/promote/ignore decision remains unauthorized. | `accepted_residual` | User / controller | Separate explicit authorization required |

Recommended next entry point after plan acceptance:

- `Data Artifact Disposition Evidence Gate` for `基金年报/` PDFs, metadata-only, writing only `docs/reviews/mvp-data-artifact-disposition-evidence-20260612.md`.

Stop condition:

- Stop after writing this plan and allowed validation. Do not claim readiness.

**NOT_READY preserved.**
