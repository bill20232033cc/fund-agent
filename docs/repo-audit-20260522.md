# 仓库审核报告

> **日期**: 2026-05-22
> **审核范围**: `bill20232033cc/fund-agent` main 分支（commit `b7117876`）
> **对照文档**: 仓库 `docs/design.md` v1.1、仓库 `docs/implementation-control.md` v1.0
> **上次审核**: `docs/repo-audit-20260521.md`

---

## 0. 审计摘要

| 指标 | 上次（05-21） | 本次（05-22） | 变化 |
|------|-------------|-------------|------|
| 最新 Phase | P8 closed | P13 closed | +5 Phase |
| 总 PR | 5（PR#5 open） | 9（PR#5/PR#9 open） | +4 PR |
| Open issues | 1 | 2 | +1 |
| Python 文件 | 56 | 57 | +1（final_judgment.py） |
| design.md 版本 | v1.1 | v1.1 | 未变 |
| impl-ctrl 版本 | v1.0 | v1.0 | 未变 |
| dayu-agent 依赖 | pyproject.toml 声明 | **已移除** | ✅ 改进 |
| fund/tools/ | 文件仍存在 | **已移除** | ✅ 改进 |

---

## 1. 新增 Phase 概览（P9-P13）

| Phase | 名称 | PR | 关键变更 |
|-------|------|-----|---------|
| P9 | （未在最近 15 commit 中出现，推测在 P10 之前） | — | 上次审核后、P10 之前完成 |
| P10 | repo hygiene and release readiness | PR#6 closed | 仓库卫生、发布就绪 |
| P11 | control-doc recovery | — | impl-ctrl 文档恢复 |
| P12 | ITEM_RULE compliance + evidence boundary | — | ITEM_RULE 渲染器合规、证据边界 |
| P13 | tracking error disclosure path | PR#7/PR#8 closed | 跟踪误差披露路径 |

**P12 细节**（从 commit 推断）：
- P12-S1: enforce ITEM_RULE renderer compliance（`c7570360`）
- P12-S2: render all ITEM_RULE evidence anchors（`24a35b4e`）

**P13 细节**：
- P13: add tracking error disclosure path（`e2d8d381`）

---

## 2. 上次审核问题跟踪

| 上次编号 | 问题 | 严重程度 | 当前状态 | 说明 |
|---------|------|---------|---------|------|
| 🔴 三源分歧 | 本地/仓库 design.md/仓库 impl-ctrl 三版本 | 高 | ⚠️ 部分解决 | 仓库已自行演进，本地 workspace 版本已过时。应以仓库为准 |
| D-1 | design.md 缺少项目结构树 | 中 | ⬜ 未修复 | v1.1 仍未补充 |
| D-8 | fund/tools/__init__.py 仍存在 | 中 | ✅ 已修复 | 文件树中已不存在 |
| C-1 | cli.py type:ignore | 中 | ⬜ 未修复 | 继承 |
| C-2 | 魔法数字 | 中 | ⬜ 未修复 | 继承 |
| C-3 | 串行抽取性能 | 低 | ⬜ 未修复 | 继承 |
| C-4 | 本地路径硬编码 | 中 | ⬜ 未修复 | 继承 |
| C-5 | fund/tools/__init__.py 仍存在 | 低 | ✅ 已修复 | 同 D-8 |
| C-6 | PR#5 仍 open | 低 | ⬜ 未修复 | PR#5 仍然 open |
| C-8 | config/settings.py 不存在 | 低 | ✅ 已解决 | 新增 `config/paths.py` 替代 |
| C-9 | reviews/ 目录膨胀 | 中 | ⬜ 未修复 | 200+ 文件仍在 |

---

## 3. 新发现的问题

### 3.1 文档与代码不一致

| # | 问题 | 严重程度 | 说明 |
|---|------|---------|------|
| N-1 | design.md v1.1 未反映 P9-P13 变更 | 🔴 高 | design.md 状态行仍写"P7/P8 设计裁决后代码事实对齐"，但代码已到 P13。新增的 `final_judgment.py`、`config/paths.py`、ITEM_RULE compliance 机制、tracking error disclosure 等均未在 design.md 中记录 |
| N-2 | design.md §8 Dayu-Agent 依赖状态过时 | 🟡 中 | design.md 仍写"当前代码没有自建或接入通用 tool loop / Host session / Agent runtime"，但 pyproject.toml 已移除 `dayu-agent` 依赖。§8 应更新为"已从依赖中移除"而非仅"后续候选" |
| N-3 | impl-ctrl 版本号仍为 v1.0 | 🟡 中 | 内容已更新至 P13，但版本号和日期（2026-05-16）未递增 |
| N-4 | impl-ctrl Startup Packet 引用 `docs/p13-main-closeout` 分支 | 🟢 低 | 当前分支应为 `main`（P13 已合入），但 Startup Packet 的 Branch 字段仍写 `docs/p13-main-closeout` |

### 3.2 代码层面

| # | 问题 | 严重程度 | 说明 |
|---|------|---------|------|
| N-5 | 新增 `analysis/final_judgment.py` 未在 design.md 中记录 | 🟡 中 | services/__init__.py 新增 `from fund_agent.fund.analysis.final_judgment import FinalJudgment`，但 design.md 的分析引擎章节未提及此模块 |
| N-6 | 新增 `config/paths.py` 未在 design.md 中记录 | 🟢 低 | 替代了不存在的 `config/settings.py`，但 design.md 未更新 |
| N-7 | services/__init__.py 新增 `AnalyzeMode`、`FundAnalysisDeveloperOverrides`、`QualityGateNotRunBlockedError` | 🟢 低 | design.md §2.3 契约表未记录这些新增类型 |
| N-8 | template/__init__.py 新增 `evaluate_template_item_rule`、`TemplateItemRuleAuditContext`、`rendered_segment_present` 等 ITEM_RULE 审计 API | 🟢 低 | design.md §3.3 ITEM_RULE 机制未提及审计上下文 API |

### 3.3 项目管理

| # | 问题 | 严重程度 | 说明 |
|---|------|---------|------|
| N-9 | PR#5 仍 open（P6-P8 hardening） | 🟡 中 | P6-P8 已在 main 中，此 PR 似乎被后续 PR 超越。应关闭或合入 |
| N-10 | PR#9 open（P14-S1 index quality denominators） | 🟢 低 | P14 已在开发中，impl-ctrl 应记录 |
| N-11 | 2 个 open issues | 🟢 低 | 需确认是否与 PR#5/PR#9 相关 |

---

## 4. 正面变化（相比上次审核的改进）

| # | 改进 | 说明 |
|---|------|------|
| ✅ B-1 | dayu-agent 依赖已从 pyproject.toml 移除 | 之前声明依赖但零导入，现在彻底移除，消除了混淆 |
| ✅ B-2 | fund/tools/ 已移除 | 之前 design.md 说已移除但文件仍在，现在文件树确认已删除 |
| ✅ B-3 | 新增 `config/paths.py` | 替代了不存在的 `settings.py`，提供路径配置 |
| ✅ B-4 | 新增 `analysis/final_judgment.py` | 将最终判断逻辑独立为模块，符合单一职责 |
| ✅ B-5 | P10 repo hygiene | 仓库卫生和发布就绪改进 |
| ✅ B-6 | P12 ITEM_RULE compliance | ITEM_RULE 渲染器合规和证据边界加固 |
| ✅ B-7 | P13 tracking error disclosure | 跟踪误差披露路径完善 |
| ✅ B-8 | pyproject.toml 新增 MIT license | 开源许可证明确 |
| ✅ B-9 | README.md 更新 | 快速开始和常用命令与实际 CLI 一致 |

---

## 5. design.md §1.2 设计原则一致性校验

design.md v1.1 §1.2 列出 6 条设计原则，逐条与代码校验：

| 原则 | 代码一致性 | 说明 |
|------|-----------|------|
| 确定性 MVP 主链路 | ✅ | pyproject.toml 无 LLM 依赖，代码纯 Python |
| 好资产 + 好价格 + 长期持有 | ✅ | 检查清单 7 问题覆盖 |
| 证据可审计 | ✅ | EvidenceAnchor + 程序审计 P1/P2/P3/C2/L1/R1/R2 |
| 模板驱动而非自由生成 | ✅ | renderer.py 纯 Python 函数 |
| 分层解耦 | ✅ | UI/Service/Capability 三层，Protocol 注入 |
| 基金类型判断优先 | ✅ | fund_type.py + preferred_lens + ITEM_RULE |

**结论**：6 条设计原则全部与代码一致。✅

---

## 6. 总结与建议

### 6.1 整体评价

**仓库持续健康发展**。从 P8 到 P13，完成了 5 个 Phase 的迭代，重点加固了 ITEM_RULE 合规性、仓库卫生、文档恢复和跟踪误差披露。dayu-agent 依赖已彻底移除，fund/tools/ 已清理，代码与设计原则保持一致。

**主要风险**：design.md v1.1 已严重滞后于代码（P9-P13 的变更未记录），这是唯一的高优先级问题。

### 6.2 建议优先级

| 优先级 | 建议 | 理由 |
|--------|------|------|
| 🔴 高 | 更新 design.md 至 v1.2，反映 P9-P13 变更 | 设计真源落后代码 5 个 Phase |
| 🟡 中 | 关闭 PR#5（已被后续 PR 超越） | 避免 PR 积压混淆 |
| 🟡 中 | 递增 impl-ctrl 版本号 | 内容已到 P13，版本号仍为 v1.0 |
| 🟡 中 | 更新 design.md §8 Dayu-Agent 状态 | 已从 pyproject.toml 移除，应更新表述 |
| 🟢 低 | 补充 design.md 项目结构树 | 上次审核 D-1，仍未修复 |
| 🟢 低 | 清理 reviews/ 目录 | 200+ 文件影响可读性 |
| 🟢 低 | 修复 cli.py type:ignore | 继承自 05-20 审核 |
| 🟢 低 | 提取魔法数字为常量 | 继承自 05-20 审核 |
