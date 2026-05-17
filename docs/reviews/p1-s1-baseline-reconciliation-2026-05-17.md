# P1-S1 基线对账裁决

> 日期：2026-05-17
> Controller：Codex
> Phase / Slice：P1 / P1-S1 文档访问契约收口
> 分支：`chore/reconcile-baseline`
> 当前 gate：`plan accepted`
> 下一 gate：`P1-S1 implementation -> code review`

## 1. 触发原因

- `docs/implementation-control.md` 已把当前下一 gate 定义为 `P1-S1 implementation + review`。
- 当前 worktree 存在未提交改动，且其中部分文件与 `P1-S1` 计划切片直接相关。
- 按 `gateflow` 的 protected local commits 规则，进入 implementation / review 前必须先明确哪些改动属于当前 slice，哪些必须保护隔离。

## 2. 基线事实

当前 `git status --short`：

```text
 M fund_agent/fund/pdf/downloader.py
?? docs/reviews/code-review-20260517-0727.md
?? fund_agent/fund/README.md
?? fund_agent/fund/documents/
?? tests/README.md
?? tests/fund/
```

已核对的计划边界来自 `docs/reviews/p1-plan-2026-05-17.md` 第 8.2 节：

- `P1-S1` 允许修改：
  - `fund_agent/fund/documents/models.py`
  - `fund_agent/fund/documents/repository.py`
  - `fund_agent/fund/documents/adapters/annual_report_pdf.py`
  - `fund_agent/fund/pdf/downloader.py`
  - `tests/fund/documents/test_repository.py`
  - `tests/fund/pdf/test_downloader.py`
- `P1-S1` 禁止触碰：
  - `fund_agent/fund/pdf/parser.py`
  - 任意 extractor
  - `fund_agent/fund/data_extractor.py`
  - 上层目录

## 3. 文件归属裁决

### 3.1 纳入当前 `P1-S1` 候选实现范围

- `fund_agent/fund/documents/__init__.py`
- `fund_agent/fund/documents/models.py`
- `fund_agent/fund/documents/repository.py`
- `fund_agent/fund/documents/adapters/__init__.py`
- `fund_agent/fund/documents/adapters/annual_report_pdf.py`
- `fund_agent/fund/pdf/downloader.py`
- `tests/fund/documents/test_repository.py`
- `tests/fund/pdf/test_downloader.py`

裁决理由：

- 这些文件直接对应 `P1-S1` 的“统一文档仓库接口 + 年报 PDF 适配器 + 下载 helper + 契约测试”。
- 已确认 `fund_agent/fund/pdf/parser.py` 未被修改，满足 `P1-S1` 的禁止边界。
- 当前实现方向与已接受 plan 和 plan review 一致：公共契约位于 `fund_agent/fund/documents/*`，`pdf/*` 仅保留底层 helper / adapter 角色。

### 3.2 作为当前 `P1-S1` 的文档同步例外纳入范围

- `fund_agent/fund/README.md`
- `tests/README.md`

裁决理由：

- `AGENTS.md` 要求当 `fund_agent/fund/` 或 `tests/` 有实现变更时同步更新对应 README。
- `P1-S1` 已形成新的稳定公共契约：`FundDocumentRepository.load_annual_report(...) -> ParsedAnnualReport`。
- 这两份 README 不改变实现边界，只记录“当前怎么用 / 当前怎么工作”，属于当前 slice 的必需文档同步，而非额外 scope。

### 3.3 暂不纳入当前 gate 的文件

- `docs/reviews/code-review-20260517-0727.md`

裁决理由：

- 该文件是当前 worktree 中预存的 ad-hoc code review artifact，不是本次 `phaseflow` 下由 `AgentMiMo` / `AgentGLM` 产生的正式双 review artifact。
- 当前 gate 的正式 review 结论必须来自本次独立派发、可追踪的 review / re-review。
- controller 可把其中的事实观察作为补充证据，但不得把该文档直接记为本 gate 已接受结论。

## 4. 当前结论

- 基线 reconciliation 结论：`pass`
- 当前 worktree 中已存在一组与 `P1-S1` 高度一致的候选实现，可直接作为 `AgentCodex` 的 implementation 起点。
- 本 gate 的 worker 不得扩大到 `parser.py`、extractor、`data_extractor.py`、上层目录或非年报文档类型。

## 5. 后续执行约束

- `AgentCodex` 负责：
  - 以当前 worktree 为基线完成 `P1-S1` implementation；
  - 只在当前裁定的 in-scope 文件内工作；
  - 产出 durable implementation artifact；
  - 不 commit、不 push、不进入下一 gate。
- `AgentMiMo` 与 `AgentGLM` 负责：
  - 仅 review `P1-S1` 当前 slice；
  - 独立输出 durable review artifacts；
  - 不做实现、不做 fix。
- controller 负责：
  - 对双 review findings 做 `accepted / rejected-with-reason / deferred-with-owner / needs-more-evidence` 裁决；
  - 若存在 accepted findings，再派发 fix 与 re-review；
  - 在进入下一个 gate 前把 artifact 路径、裁决、残余风险和 next entry point 写回 `docs/implementation-control.md`。
