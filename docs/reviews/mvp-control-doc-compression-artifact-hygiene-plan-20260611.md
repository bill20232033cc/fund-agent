# Control-doc compression / artifact hygiene planning gate plan

日期：2026-06-11

角色：planning worker

计划状态：code-generation-ready；docs-only；不进入 implementation。

## 1. Gate objective / non-goals / classification

### Objective

为下一 gate 提供可执行的 docs-only implementation plan：

1. 压缩 `docs/implementation-control.md` 与 `docs/current-startup-packet.md` 的当前启动面，保留 current gate、next entry、accepted artifact index、open residual owner 和 guardrails。
2. 将过长的 accepted artifact 列表与 historical ledger 从 active control surface 中抽离为索引型 artifact，避免控制真源继续线性膨胀。
3. 对当前未跟踪、生成、研究、scratch、review 残留做 disposition planning，只分类、指定 owner 与 next gate，不删除、不移动、不归档、不 stage。

### Non-goals

- 不修改 source、tests、runtime behavior、provider/default/config、fallback、extractor、analyze、checklist、golden、readiness、score-loop、release 或 PR 状态。
- 不运行 live EID、network、PDF、FDR、FundDocumentRepository、helper、fallback、provider、LLM、extractor、analyze、checklist、golden、readiness、score-loop、release 命令。
- 不把 untracked workspace residue 当作 proof、fixture、accepted evidence 或产品范围。
- 不清理 `fund_agent/tools/`、`reports/manual-llm-smoke/`、`基金年报/`、`reviews/`、`docs/audit/` 等残留；只能在 disposition artifact 中记录后续处理建议。
- 不改写 `docs/design.md` 的架构事实，除非 controller 在后续 implementation gate 明确发现 control compression 必须同步一个已实现事实索引；本计划不建议默认修改 `docs/design.md`。

### Classification

建议分类：`standard`。

理由：

- 虽然是 docs-only/control-plane gate，但会修改 control truth 和 startup truth 的组织方式。
- 触及 accepted artifact index、historical ledger 和 workspace residue disposition，影响后续 controller 复位路径。
- 不改变代码行为、public contract、schema、quality gate、final judgment、Host/Agent/dayu、外部来源策略、baseline/golden 资格或 release/PR 外部状态，因此不需要 `heavy`。

## 2. Facts and opinions boundary

### Repo facts

以下事实来自本次 no-live 文件系统元数据读取：

| Fact | Evidence command / result |
| --- | --- |
| 当前分支 | `git branch --show-current` -> `feat/mvp-llm-incomplete-run-artifacts` |
| 分支状态 | `git status --branch --short` -> branch ahead of origin by 84 commits |
| `AGENTS.md` 行数 | `wc -l` -> 260 |
| `docs/design.md` 行数 | `wc -l` -> 1244 |
| `docs/implementation-control.md` 行数 | `wc -l` -> 842 |
| `docs/current-startup-packet.md` 行数 | `wc -l` -> 527 |
| tracked `docs/reviews` 文件数 | `git ls-files docs/reviews | wc -l` -> 2174 |
| 当前 `docs/reviews` 顶层文件数 | `find docs/reviews -maxdepth 1 -type f | wc -l` -> 2208 |
| `docs/reviews` 当前未跟踪条目数 | `git status --short docs/reviews | wc -l` -> 34 |
| untracked dirs/files present | `git status --short` lists `docs/audit/`, multiple `docs/reviews/*.md/json`, `docs/learning-roadmap.md`, `docs/next-development-phaseflow.md`, `docs/superpowers/specs/2026-06-02-template-rebuild-facet-wiring-design.md`, `docs/tmux-agent-memory-store.md`, `fund_agent/tools/`, `reports/manual-llm-smoke/`, `reviews/`, `scripts/claude_mimo_simple.py`, `基金年报/`, `定性分析模板.md` |
| `docs/audit/` sample count | `find docs/audit -maxdepth 2 -type f` -> 1 markdown audit report |
| `reports/manual-llm-smoke/` sample count | `find reports/manual-llm-smoke -maxdepth 3 -type f` -> 8 files under two run directories |
| `fund_agent/tools/` sample count | `find fund_agent/tools -maxdepth 3 -type f` -> `claude_mimo.py` plus one `__pycache__` file |
| `reviews/` sample count | `find reviews -maxdepth 3 -type f` -> 2 audit reports |
| `基金年报/` sample count | `find 基金年报 -maxdepth 2 -type f` -> 5 annual-report PDFs |

### Truth-doc facts

以下事实来自 `AGENTS.md`、`docs/design.md`、`docs/implementation-control.md`、`docs/current-startup-packet.md`：

1. `AGENTS.md` 是最高优先级规则真源；`docs/design.md` 是设计真源；`docs/implementation-control.md` 是控制真源；`docs/current-startup-packet.md` 是短启动入口。
2. `docs/implementation-control.md` 前部只应保留控制面信息：Startup Packet、Current Truth Guardrails、current gate、next entry point、当前 accepted artifacts、open residuals、non-goal reminder、最近 Active Gate Ledger。
3. 历史审计账本、长版本记录、旧 phase 全量日志、PR/commit 细节和 superseded 架构叙述应迁入 `docs/reviews/` 或 `docs/archive/`，在 control doc 中只保留索引和必要摘要。
4. `docs/reviews/` 和 `docs/archive/` 只作为 evidence chain，不覆盖 current startup packet、`AGENTS.md` 或 `docs/design.md` 当前/未来状态标签。
5. 当前 startup packet 明确 next entry point 是 `Control-doc compression / artifact hygiene planning gate`，scope 是 no-live/control-plane only。
6. 当前 startup packet 明确禁止在本 gate 删除、移动、归档、stage、commit 外部 cleanup，禁止运行 live EID/PDF/FDR/network、fallback、provider/LLM、extractor/analyze/checklist、golden/readiness、score-loop、release、push、PR 或 merge。
7. `docs/design.md` 当前设计事实仍是 EID single-source operational annual-report source；Eastmoney、基金公司官网/CDN、CNINFO 仅为 deferred candidate / historical evidence route；本 gate 不应改变该设计事实。

### Planning opinions

以下是本 planning worker 的建议，不是已接受事实：

1. 后续 implementation gate 的最短路径应分成 A/B/C 三个 docs-only slice：先压缩当前启动面，再抽出 accepted artifact index / historical ledger，最后写 residue disposition artifact。
2. `docs/current-startup-packet.md` 的 accepted commit 长表不应继续作为短启动入口主体；应改成短摘要 + index artifact link。
3. `docs/implementation-control.md` 不应继续内联增长所有 historical gate 行；应保留当前 gate、最近 ledger 和 residual owner，旧记录转为 evidence index。
4. 当前 untracked residue 不应阻塞 docs-only planning closeout；但会阻塞 release/readiness 类 gate，除非有独立 disposition judgment。
5. `fund_agent/tools/` 因路径位于 source tree，风险高于普通 scratch；后续 gate 只能先记录 ownership/non-impact disposition，不能自动清理或纳入产品。

## 3. Proposed implementation slices

### Slice A: control-doc compression / startup packet index compression

目标：压缩 active startup surface，不改变 control meaning。

Allowed edits:

- `docs/implementation-control.md`
- `docs/current-startup-packet.md`
- Slice A implementation evidence/review/judgment artifact under `docs/reviews/`

Implementation steps:

1. 在两个 control docs 顶部保留：
   - current phase
   - current gate closeout
   - next entry point
   - current design truth and control truth
   - strict non-goals
   - open residual owner summary
   - accepted artifact index link
2. 将长 accepted commit/path list 替换为压缩索引引用：
   - 保留最近 current gate closeout 的 plan/evidence/review/judgment/checkpoint。
   - 保留当前 phase 的关键 accepted checkpoints 摘要。
   - 其他历史 accepted artifact 通过 Slice B 的 index artifact 引用。
3. 明确 `docs/current-startup-packet.md` 是 resume packet，不是 historical ledger。
4. 对照 `AGENTS.md` 文档规范，确认 active surface 前部不再追加长日志。
5. 不修改 `docs/design.md`，除非 DS/MiMo review 指出 control-doc compression 导致设计真源状态不一致。

Acceptance criteria:

- 两个 control docs 仍能回答“当前 phase/gate 是什么、下一步是什么、依据哪些 accepted artifacts、还有哪些 residual owner”。
- `Control-doc compression / artifact hygiene implementation gate` 成为唯一主线 next entry。
- 旧 ledger 仅作为 evidence chain，不再覆盖 startup/current gate。
- `rg -n "Next entry point|Current gate|Control-doc compression|docs/reviews" docs/implementation-control.md docs/current-startup-packet.md` 能定位当前 gate 和索引入口。

### Slice B: accepted artifact index / historical ledger extraction strategy

目标：把长 accepted artifact 列表和 historical ledger 抽成可检索索引 artifact，而不是继续占用 active control surface。

Recommended new artifacts:

- `docs/reviews/mvp-control-doc-compression-accepted-artifact-index-20260611.md`
- `docs/reviews/mvp-control-doc-compression-historical-ledger-index-20260611.md`

Implementation steps:

1. 从 `docs/implementation-control.md` 和 `docs/current-startup-packet.md` 中识别当前 active surface 必需条目与 historical evidence 条目。
2. 建立 `accepted-artifact-index`，按 gate family 分组，而不是按时间全量平铺：
   - current gate closeout
   - EID single-source operational hardening
   - small-golden row-shape / extractor correctness
   - typed-template truth-source replacement
   - Agent engine / Host governance
   - provider/runtime/LLM diagnostics
   - release-maintenance historical evidence
3. 每组只记录：
   - gate family
   - accepted status
   - authoritative artifact paths
   - accepted checkpoint(s)
   - current relevance
   - residual owner / deferred gate
4. 建立 `historical-ledger-index`，只收纳 superseded 或 historical entries，并明确不覆盖 startup packet、control truth 或 design truth。
5. 在 `docs/implementation-control.md` 和 `docs/current-startup-packet.md` 中只引用这两个 index artifact。

Acceptance criteria:

- active control docs 不再内联巨大 accepted path/commit 列表。
- index artifact 足以重建证据链，但明确不是当前架构真源。
- 未新增 release/readiness/golden/provider/runtime 结论。

### Slice C: untracked residue disposition plan

目标：逐类记录 untracked/generated/research/scratch/review residue 的 disposition；只计划，不清理。

Recommended new artifact:

- `docs/reviews/mvp-control-doc-compression-untracked-residue-disposition-20260611.md`

Disposition table:

| Path / group | Category | Decision | Owner | Next gate | Blocker? |
| --- | --- | --- | --- | --- | --- |
| `docs/reviews/*.md/json` currently untracked | evidence-chain artifact | `promote-through-review` only if controller maps each file to accepted gate; otherwise `leave-untracked` | controller | artifact hygiene implementation gate / per-gate evidence acceptance | Blocks release/readiness until classified; does not block this planning gate |
| `docs/audit/` | evidence-chain artifact or review artifact | `leave-untracked`; optionally promote through review after provenance check | controller + reviewer owner | review-artifact acceptance gate | Non-blocking for planning; blocker for release if unclassified |
| `docs/learning-roadmap.md` | research input | `leave-untracked` unless a future roadmap/docs gate accepts it | user/controller | research-doc disposition gate | Non-blocking |
| `docs/next-development-phaseflow.md` | planning/research input | `leave-untracked`; do not treat as control truth | controller | phaseflow planning gate only if explicitly requested | Non-blocking |
| `docs/superpowers/specs/2026-06-02-template-rebuild-facet-wiring-design.md` | research input / candidate design | `leave-untracked`; cannot override `docs/design.md` | design owner | future design gate | Non-blocking; blocker if cited as current truth |
| `docs/tmux-agent-memory-store.md` | research/scratch operations note | `leave-untracked`; possible archive only with explicit gate | controller | ops artifact disposition gate | Non-blocking |
| `fund_agent/tools/` | source-like residue | `leave-untracked`; do not import, stage, or clean; require ownership/non-impact review | implementation owner + controller | source-like residue ownership gate | Blocker for release/readiness until resolved |
| `fund_agent/tools/__pycache__/` | scratch/runtime output | `ignore` candidate, but do not edit `.gitignore` in this gate unless authorized | controller | artifact hygiene implementation gate or ignore-rule gate | Non-blocking for planning; blocker for clean release hygiene |
| `reports/manual-llm-smoke/` | scratch/runtime output / live evidence residue | `leave-untracked`; can be evidence only if prior gate accepted exact run artifact | runtime evidence owner | provider/live evidence disposition gate | Blocker for release/readiness if unclassified |
| `reviews/` | obsolete duplicate or external review residue | `leave-untracked`; possible archive/delete requires explicit authorization | controller/user | artifact disposition gate | Non-blocking for planning; blocker for release if unclassified |
| `scripts/claude_mimo_simple.py` | scratch helper | `leave-untracked`; do not promote without reviewed tool-support gate | user/controller | tooling disposition gate | Non-blocking; blocker if imported or used as proof |
| `基金年报/` | user-owned unknown / local PDF corpus | `leave-untracked`; do not read through filesystem for production proof; deletion requires explicit user authorization | user | data artifact disposition gate | Non-blocking for planning; blocker for release/readiness |
| `定性分析模板.md` | user-owned unknown / research input | `leave-untracked`; do not promote without docs/design gate | user/controller | research-doc disposition gate | Non-blocking |

Implementation notes:

- Do not bulk-read large files or PDFs.
- Do not use untracked residue as root-cause proof.
- If ownership is ambiguous, record `user-owned unknown` and stop.
- If a file looks valuable, decision is still `promote-through-review`, not immediate stage.
- If a file looks obsolete, decision is `ask-before-delete`, not deletion.

Acceptance criteria:

- Disposition artifact contains one row per untracked group with category, evidence, decision, owner, next gate, blocker.
- No file is deleted, moved, archived, staged, committed or ignored unless a later implementation gate explicitly allows that exact edit.
- Release/readiness blocker status is stated separately from planning-gate blocker status.

## 4. Allowed files for later implementation gate

Minimal allowed write set for the recommended implementation gate:

| Path | Allowed action |
| --- | --- |
| `docs/implementation-control.md` | Compress active control surface and replace long historical lists with index links |
| `docs/current-startup-packet.md` | Compress short resume entry and replace accepted commit/path long table with index link |
| `docs/reviews/mvp-control-doc-compression-accepted-artifact-index-20260611.md` | New index artifact |
| `docs/reviews/mvp-control-doc-compression-historical-ledger-index-20260611.md` | New index artifact |
| `docs/reviews/mvp-control-doc-compression-untracked-residue-disposition-20260611.md` | New disposition artifact |
| `docs/reviews/mvp-control-doc-compression-artifact-hygiene-implementation-evidence-20260611.md` | Implementation evidence |
| `docs/reviews/mvp-control-doc-compression-artifact-hygiene-code-review-ds-20260611.md` | DS review output, if reviewer writes it |
| `docs/reviews/mvp-control-doc-compression-artifact-hygiene-code-review-mimo-20260611.md` | MiMo review output, if reviewer writes it |
| `docs/reviews/mvp-control-doc-compression-artifact-hygiene-controller-judgment-20260611.md` | Controller judgment after review |

Paths that may only be referenced in disposition artifact, not cleaned or promoted by default:

- `docs/audit/`
- untracked `docs/reviews/*.md/json`
- `docs/learning-roadmap.md`
- `docs/next-development-phaseflow.md`
- `docs/superpowers/specs/`
- `docs/tmux-agent-memory-store.md`
- `fund_agent/tools/`
- `reports/manual-llm-smoke/`
- `reviews/`
- `scripts/claude_mimo_simple.py`
- `基金年报/`
- `定性分析模板.md`

Explicitly disallowed write set:

- source modules under `fund_agent/`
- tests under `tests/`
- runtime reports under `reports/`
- PDF/document corpus
- `.gitignore` unless a later controller explicitly authorizes an ignore-rule slice
- `docs/design.md` unless review proves a necessary current-truth inconsistency

## 5. Validation matrix

Allowed validation commands:

| Check | Command | Purpose |
| --- | --- | --- |
| Branch/status baseline | `git status --branch --short` | Confirm branch and residue state |
| Untracked inventory | `git status --short` | Confirm no unexpected staging or cleanup |
| Whitespace/doc patch safety | `git diff --check` | Catch whitespace errors |
| Control-doc length metadata | `wc -l docs/implementation-control.md docs/current-startup-packet.md docs/reviews/mvp-control-doc-compression-accepted-artifact-index-20260611.md docs/reviews/mvp-control-doc-compression-historical-ledger-index-20260611.md docs/reviews/mvp-control-doc-compression-untracked-residue-disposition-20260611.md` | Confirm compression and index artifact existence |
| Review count metadata | `git ls-files docs/reviews | wc -l` and `find docs/reviews -maxdepth 1 -type f | wc -l` | Confirm tracked/current review artifact count without reading contents |
| Current gate discoverability | `rg -n "Next entry point|Current gate|Control-doc compression|artifact hygiene|accepted-artifact-index|historical-ledger-index|untracked-residue-disposition" docs/implementation-control.md docs/current-startup-packet.md docs/reviews/mvp-control-doc-compression-*.md` | Confirm resume paths are discoverable |
| Prohibited live wording guard | `rg -n "live EID|FundDocumentRepository|--use-llm|golden/readiness|score-loop|release|PR" docs/implementation-control.md docs/current-startup-packet.md docs/reviews/mvp-control-doc-compression-*.md` | Verify any references are non-goal/deferred wording only |

Explicitly not allowed:

- `uv run fund-analysis analyze`
- `uv run fund-analysis checklist`
- live EID/FDR/PDF/network/helper/fallback commands
- provider/LLM smoke or readiness commands
- extractor/golden/score-loop/release commands
- staging/commit/push/PR commands without controller acceptance after implementation/review

## 6. Review handoff checklist for DS/MiMo

Ask reviewers to check only this plan or the later implementation artifacts against the following:

1. Does the plan preserve `AGENTS.md` as rule truth, `docs/design.md` as design truth, `docs/implementation-control.md` as control truth, and `docs/current-startup-packet.md` as short resume entry?
2. Does Slice A preserve current gate, next entry, accepted checkpoint summary, residual owner and non-goals after compression?
3. Does Slice B make accepted artifact evidence reconstructable without leaving historical ledger inside active startup surface?
4. Does Slice C classify all visible untracked groups without deleting, moving, archiving, staging or promoting them?
5. Does any wording accidentally treat untracked residue, review artifacts or archive files as current architecture/source truth?
6. Are allowed files minimal enough for a docs-only/control-plane implementation gate?
7. Are validation commands no-live and sufficient for docs-only acceptance?
8. Does the plan avoid source/tests/runtime/provider/fallback/extractor/golden/readiness/release behavior change?

Review verdict options:

- `PASS`
- `PASS_WITH_NON_BLOCKING_OBSERVATIONS`
- `BLOCKED`

Blocking findings should include exact path, section and required correction.

## 7. Controller decision points and residuals

Controller decision points before implementation:

1. Accept or reject `standard` classification.
2. Confirm whether Slice A and Slice B may run in one implementation gate or require two gates.
3. Confirm exact allowed write set.
4. Decide whether `docs/design.md` is explicitly disallowed or conditionally allowed only if review finds truth inconsistency.
5. Decide whether untracked `docs/reviews` artifacts can be promoted in this gate or only listed in the disposition artifact.
6. Decide whether `.gitignore` is out of scope for this gate. This plan recommends out of scope.

Residuals after this planning gate:

| Residual | Owner | Proposed next handling |
| --- | --- | --- |
| Current control docs are too long for efficient startup | implementation worker | Slice A |
| Accepted artifact evidence is spread across active control surface and `docs/reviews` | implementation worker | Slice B |
| Untracked residue remains in workspace | controller / artifact owner | Slice C disposition only |
| Source-like untracked `fund_agent/tools/` exists | controller + implementation owner | Separate source-like residue ownership gate |
| Manual smoke reports and PDFs exist outside accepted evidence chain | user/controller | Separate data/runtime residue disposition gate |
| Release/readiness cleanliness remains unproven | release owner | Deferred release-readiness gate after disposition acceptance |

## 8. Next entry recommendation

Recommended single mainline next entry:

`Control-doc compression / artifact hygiene implementation gate`

Deferred entries:

- Source-like residue ownership gate for `fund_agent/tools/`.
- Runtime/manual smoke artifact disposition gate for `reports/manual-llm-smoke/`.
- User-owned local document/PDF corpus disposition gate for `基金年报/` and `定性分析模板.md`.
- Research-doc disposition gate for `docs/learning-roadmap.md`, `docs/next-development-phaseflow.md`, `docs/superpowers/specs/`, and `docs/tmux-agent-memory-store.md`.
- Release-readiness cleanliness gate after accepted control compression and residue disposition.
- Any live EID/provider/extractor/golden/readiness/release gate; all require separate plan/review/controller judgment and explicit authorization.
