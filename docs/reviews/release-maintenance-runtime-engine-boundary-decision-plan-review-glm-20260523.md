# Adversarial Plan Review — Runtime/Engine Boundary Decision Plan

> **Reviewer**: GLM-5.1
> **Date**: 2026-05-23
> **Plan under review**: `docs/reviews/release-maintenance-runtime-engine-boundary-decision-plan-20260523.md`
> **Authority**: 用户提供的 AGENTS.md（六层边界 `UI / Application / Runtime / Service / Engine / Capability`），本地 AGENTS.md 有未接受冲突 diff 不作为真源
> **Design truth**: `docs/design.md` v2.2
> **Control truth**: `docs/implementation-control.md` v1.1

---

## 结论：pass-with-risks

无 blocker。计划证据链完整，defer 决策有直接事实支撑，scope/non-scope 边界清晰，可交给 implementation/docs worker 执行。但存在 2 条 material finding 需在 Slice 1 执行前确认处理方式。

---

## Material Findings

### M1. design.md §9.0 项目结构树与磁盘事实不一致——Slice 1 scope 未明确覆盖

**事实**：`docs/design.md` 第 698-699 行在项目结构树中列出：

```text
│   ├── runtime/                         # Runtime 层（目标包；当前未接入 Agent runtime）
│   ├── engine/                          # Engine 层（目标包；当前未接入通用工具执行框架）
```

磁盘实际目录只有 `application/`、`config/`、`fund/`、`services/`、`ui/`，不存在 `runtime/` 或 `engine/`。

条目注释已写"目标包"和"当前未接入"，但在树形结构图格式中，`├── runtime/` 在视觉上暗示这是一个存在于磁盘的目录。这与 AGENTS.md "以代码为准，不让文档先于代码'设计未来'"规则存在张力。

**计划的 Gap**：Slice 1 的 scope 描述为"保留六层目标边界，同时明确 Runtime/Engine 是 future concrete capability boundary，不以空包表示当前完成状态"——但这不等于修正 §9.0 目录树。如果 Slice 1 只在 §2.1 或 §2.2 增加文字说明而不动 §9.0 的树形图，design.md 内部就会出现"§2.2 说没有"与"§9.0 画出来好像有"的表述矛盾。

**建议**：Slice 1 scope 应明确包含对 design.md §9.0 项目结构树中 `runtime/` 和 `engine/` 条目的处理——要么从树中移除（让树只反映磁盘事实），要么将注释改为更醒目的标注如 `# ⬜ 目标包（磁盘不存在）`，确保树与文字叙述一致。

**严重度**：不阻塞计划接受，但 Slice 1 执行前应确认处理方式。不修正会在 design.md 内留下自相矛盾。

### M2. 本地 AGENTS.md 冲突 diff 导致两套口径并存——defer 期间 worker 风险

**事实**：本地 AGENTS.md 已被修改（`git status` 显示 `M AGENTS.md`），包含四层口径 `UI -> Service -> Host -> Agent`，且要求 Host 使用 `dayu.host`、Agent 使用 `dayu.engine`。用户提供的权威版本是六层 `UI / Application / Runtime / Service / Engine / Capability`，且要求 Runtime/Engine 在本项目内化实现。

计划 §5 Non-Scope 正确排除修改本地 AGENTS.md，§10 Residual Risks 最后一行也记录了这个风险。但问题是：在 AGENTS.md 冲突解决前，任何新启动的 worker 读到本地版本（四层 + Dayu 外部 runtime）可能做出与六层边界矛盾的判断。

**当前缓解措施已足够**：plan-review checklist、design.md v2.2、implementation-control.md、fund_agent/README.md 全部使用六层口径。只要 worker 遵循"必读文件优先级"（AGENTS.md > design.md > implementation-control.md），就不会被本地冲突 diff 误导。但缓解依赖 worker 合规，不依赖技术强制。

**建议**：无需改变计划 scope。但 controller 在接受本计划时应确认：在 push 到 main 前，AGENTS.md 冲突必须先由用户显式裁决。

**严重度**：不阻塞。属于已记录的 residual risk，缓解措施充分。

---

## Non-Blocking Observations

### O1. Defer 决策有直接证据支撑

对"当前不应创建占位包"这一核心判断，证据链如下：

| 证据来源 | 直接证据 | 位置 |
|----------|---------|------|
| design.md §2.1 | "当前 CLI 生产路径走 UI → Application → Service → Capability；Runtime / Engine 尚未接入" | 第 61 行 |
| design.md §2.2 | "当前没有 Runtime run / Engine tool loop / scene preparation 主链路" | 第 111 行 |
| design.md §2.2 | "在没有明确 session/run/tool-loop 需求前，不应空造 Runtime 或 Engine 包" | 第 113 行 |
| implementation-control.md | Open residuals: "Runtime/Engine packages are not yet implemented" | 第 118 行 |
| implementation-control.md | "Runtime / Engine 目标边界已确认；当前未接入 Agent runtime 或通用 tool engine" | 第 662 行 |
| fund_agent/README.md | "当前代码不接入外部 Dayu Host、Engine、tool loop、scene registry 或 LLM prompt runtime" | 第 9 行 |
| 磁盘事实 | `fund_agent/` 下只有 application/config/fund/services/ui 五个包 | `ls` 验证 |

所有证据一致指向：当前确定性 CLI 主链路不需要 Runtime/Engine 行为契约。占位包无法提供可测试契约，只会制造虚假架构完成感。Defer 决策逻辑成立。

### O2. 边界债有明确 owner 和触发机制

- implementation-control.md Open residuals 已记录 Runtime/Engine 为 boundary debt ✓
- 计划 §10 Residual Risks 表格为 6 个风险指定了 Owner 和处理方式 ✓
- 未来触发条件列举了 4 类具体场景（session/run 生命周期、scene registry、tool loop、LLM audit），且要求触发时先产出独立 plan-review artifact ✓
- plan-review checklist（§9）包含六层边界检查项 ✓

边界债不会被遗忘。Defer 不是否认六层边界，而是将实现绑定到真实需求。

### O3. Acceptance criteria、sequencing、validation commands 足够交给 worker

- §7 Acceptance Criteria 有 8 条，每条可判定 pass/fail ✓
- Sequencing 清晰：Slice 0（本 artifact）→ plan review → Slice 1（docs-only，条件执行）→ Slice 2（static guard，可选）✓
- Slice 0 validation 是 `git diff --check` + `git status --short`，对纯文档 artifact 充分 ✓
- Slice 1 validation 包含 `rg` 模式扫描验证 Dayu/runtime/engine 关键词一致 ✓
- Slice 2 validation 包含 `pytest`、`ruff`、`git diff --check` ✓

Worker 可以从计划直接获取足够信息执行。

### O4. 六层边界、Dayu/no-runtime、explicit-parameter、FundDocumentRepository 边界均正确保持

| 检查项 | 结果 |
|--------|------|
| 六层边界以 AGENTS.md 为权威 | ✅ 计划全文使用 UI / Application / Runtime / Service / Engine / Capability，承认当前生产路径只经四层 |
| Dayu 只作方法论/历史参考 | ✅ §5 Non-Scope 明确禁止引入外部 dayu-agent / Dayu Host / Engine / tool loop |
| 不依赖外部 Dayu runtime | ✅ §2.1 引用 design.md Dayu 裁决，§3 重申，§7 acceptance criteria 第 6 条 |
| explicit-parameter / no-extra-payload | ✅ §9 checklist 第 4 条要求所有参数进 typed request/contract/config |
| FundDocumentRepository 边界不变 | ✅ §5 Non-Scope 明确不改变年报访问路径，§7 第 7 条 |
| Docs sync 不写"已实现" | ✅ §1 明确空包产生虚假完成感，§4 scope 限制为 docs-only alignment |
| 不修改本地冲突 AGENTS.md | ✅ §5 第 5 条和 §7 第 8 条 |

---

## 对核心挑战问题的裁决

> "计划推荐 defer，不创建 fund_agent/runtime / fund_agent/engine 占位包；请挑战这个决策是否有直接证据支撑，是否会留下边界债无 owner。"

**有直接证据支撑**：见 O1 证据表。五个独立来源（design.md、implementation-control.md、README、磁盘事实、生产主链路分析）一致确认当前无 Runtime/Engine 行为需求。

**边界债有 owner**：见 O2。implementation-control.md Open residuals、计划 §10 Residual Risks 表格、plan-review checklist 三重追踪。

**但**：design.md §9.0 项目结构树是一个未修正的"文档先于代码"实例（M1）。这不改变 defer 决策本身，但 Slice 1 执行时必须处理。

---

## Summary

| 类别 | 数量 |
|------|------|
| Blocker | 0 |
| Material finding | 2 (M1: design.md 树/磁盘不一致; M2: AGENTS.md 冲突两套口径) |
| Non-blocking observation | 4 |

**最终判定**：**pass-with-risks** — 计划可以接受并进入 Slice 1。建议 Slice 1 scope 增加 M1 的处理（修正或强化标注 design.md §9.0 项目结构树中 runtime/engine 条目），M2 作为已知 residual 由 controller 在 push 前确认用户裁决。
