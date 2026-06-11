# Control-doc compression / artifact hygiene planning gate controller judgment

日期：2026-06-11

角色：controller

## Verdict

ACCEPT_WITH_AMENDMENTS

本 planning gate accepted locally 的依据是：planning artifact 已给出 code-generation-ready 的 no-live/control-plane implementation path；DS 与 MiMo 独立 review 均为 `PASS_WITH_FINDINGS`，且 findings 均可通过 controller amendment 收紧 scope，不构成 blocker。

Accepted plan artifact:

- `docs/reviews/mvp-control-doc-compression-artifact-hygiene-plan-20260611.md`

Review artifacts:

- `docs/reviews/mvp-control-doc-compression-artifact-hygiene-plan-review-ds-20260611.md`
- `docs/reviews/mvp-control-doc-compression-artifact-hygiene-plan-review-mimo-20260611.md`

## Basis

### Repo facts

- 当前分支为 `feat/mvp-llm-incomplete-run-artifacts`。
- `docs/implementation-control.md` 当前约 842 行，`docs/current-startup-packet.md` 当前约 527 行。
- 当前 workspace 存在大量 untracked residue，包括 `docs/audit/`、untracked `docs/reviews/*.md/json`、`fund_agent/tools/`、`reports/manual-llm-smoke/`、`reviews/`、`基金年报/`、`定性分析模板.md` 等。
- 本 planning gate 新增的 current-gate artifacts 为 plan、DS review、MiMo review 和本 controller judgment；未观察到 source/tests/runtime behavior 修改。

### Truth-doc facts

- `AGENTS.md` 规定 `docs/implementation-control.md` 前部只保留控制面信息；历史审计账本、长版本记录、旧 phase 全量日志、PR/commit 细节和 superseded 架构叙述应迁入 `docs/reviews/` 或 `docs/archive/`，control doc 只保留索引和必要摘要。
- `docs/current-startup-packet.md` 当前 next entry point 是 `Control-doc compression / artifact hygiene planning gate`，并限定 no-live/control-plane only。
- `docs/design.md` 是设计真源；本 gate 不改变 EID single-source current source policy，不重新授权 Eastmoney、基金公司官网/CDN、CNINFO、fallback、provider/LLM、extractor、golden/readiness、release/PR。

### Reviewer facts

- DS verdict: `PASS_WITH_FINDINGS`。
- MiMo verdict: `PASS_WITH_FINDINGS`。
- 两份 review 均认可计划的事实/观点分离、EID single-source/no-fallback 边界、untracked residue 只做 disposition input、单一主线 next entry。
- 两份 review 都要求禁止在本 implementation gate 中条件性修改 `docs/design.md`。
- DS 另指出 implementation allowed write set 混入 reviewer/controller artifacts，需要按角色拆分。

## Finding disposition

| Finding | Source | Disposition | Controller judgment |
| --- | --- | --- | --- |
| Implementation allowed write set 混入 DS/MiMo review artifact 与 controller judgment artifact | DS | ACCEPT_WITH_REWRITE | 后续 implementation worker 允许写 `docs/implementation-control.md`、`docs/current-startup-packet.md`、三个 index/disposition artifacts、implementation evidence。Reviewer artifacts 只能由 reviewer 写；controller judgment 只能由 controller 写。Implementation worker 不得创建、编辑或预填 review/judgment artifacts。 |
| `docs/design.md` 被保留为条件性写入口 | DS + MiMo | ACCEPT_WITH_REWRITE | `docs/design.md` 对后续 `Control-doc compression / artifact hygiene implementation gate` 明确 disallowed。若压缩中发现 design/control inconsistency，implementation worker 必须停止相关修改并记录 residual，转入单独的 design-truth-sync gate，经 plan/review/controller judgment 后再处理。 |
| Workspace metadata counts 会漂移 | MiMo | ACCEPT | 后续 implementation gate 必须重新运行 status/count metadata checks；本 planning artifact 中的计数只作为 2026-06-11 planning evidence，不作为后续 accepted release evidence。 |
| Untracked residue 仍可能阻塞 release/readiness | DS + MiMo | ACCEPT | 对本 planning gate 非 blocker；对 release/readiness gate 保持 blocker/residual，直到有独立 disposition judgment。 |
| `fund_agent/tools/` 是 source-like residue | MiMo | ACCEPT | 不得 import、stage、promote、clean；只能在 disposition artifact 中记录，并 deferred 到 source-like residue ownership gate。 |

## Accepted amendments

后续 `Control-doc compression / artifact hygiene implementation gate` 必须采用以下 amended scope：

1. Gate classification: `standard`。
2. Implementation worker allowed write set:
   - `docs/implementation-control.md`
   - `docs/current-startup-packet.md`
   - `docs/reviews/mvp-control-doc-compression-accepted-artifact-index-20260611.md`
   - `docs/reviews/mvp-control-doc-compression-historical-ledger-index-20260611.md`
   - `docs/reviews/mvp-control-doc-compression-untracked-residue-disposition-20260611.md`
   - `docs/reviews/mvp-control-doc-compression-artifact-hygiene-implementation-evidence-20260611.md`
3. Reviewer-only outputs:
   - `docs/reviews/mvp-control-doc-compression-artifact-hygiene-code-review-ds-20260611.md`
   - `docs/reviews/mvp-control-doc-compression-artifact-hygiene-code-review-mimo-20260611.md`
4. Controller-only output:
   - `docs/reviews/mvp-control-doc-compression-artifact-hygiene-controller-judgment-20260611.md`
5. Explicitly disallowed in the implementation gate:
   - `docs/design.md`
   - `.gitignore`
   - source modules under `fund_agent/`
   - tests under `tests/`
   - runtime reports under `reports/`
   - PDF/document corpus
   - any delete/move/archive/cleanup/stage of unrelated residue
6. If implementation discovers a real design-truth inconsistency, it must stop that thread and record a residual for a separate design-truth-sync gate.

## Residuals

| Residual | Status | Owner | Next handling |
| --- | --- | --- | --- |
| Active control/startup docs are too long for efficient startup | accepted work item | implementation worker | Slice A in next implementation gate |
| Accepted artifact evidence is spread across active control surface and `docs/reviews` | accepted work item | implementation worker | Slice B in next implementation gate |
| Untracked residue remains in workspace | accepted residual | controller / artifact owner | Slice C disposition artifact only; no cleanup |
| `fund_agent/tools/` source-like residue | accepted residual | controller + implementation owner | Deferred source-like residue ownership gate |
| Manual smoke reports and PDFs outside accepted evidence chain | accepted residual | user/controller | Deferred data/runtime residue disposition gate |
| Release/readiness cleanliness unproven | accepted residual | release owner | Deferred release-readiness gate after disposition acceptance |

## Validation

Accepted validation for this planning gate:

- `git status --short`
- `git status --branch --short`
- `git diff --check`
- `wc -l docs/implementation-control.md docs/current-startup-packet.md`
- targeted `rg` / `find` metadata checks used only for no-live inventory

Not run and not authorized:

- live EID / network / PDF / FDR / `FundDocumentRepository`
- helper/fallback/provider/LLM
- extractor/analyze/checklist/golden/readiness/score-loop
- release/push/PR/merge
- delete/move/archive cleanup

## Next entry

Recommended single mainline next entry:

`Control-doc compression / artifact hygiene implementation gate`

Deferred entries:

- Source-like residue ownership gate for `fund_agent/tools/`.
- Runtime/manual smoke artifact disposition gate for `reports/manual-llm-smoke/`.
- User-owned local document/PDF corpus disposition gate for `基金年报/` and `定性分析模板.md`.
- Research-doc disposition gate for `docs/learning-roadmap.md`, `docs/next-development-phaseflow.md`, `docs/superpowers/specs/`, and `docs/tmux-agent-memory-store.md`.
- Design-truth-sync gate only if implementation finds a real design/control inconsistency.
- Release-readiness cleanliness gate after accepted control compression and residue disposition.
- Any live EID/provider/extractor/golden/readiness/release gate, each requiring separate reviewed gate and explicit authorization where live/external action is involved.
