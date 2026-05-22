# Design.md 与 Implementation-control.md 对齐指南

> **生成日期**: 2026-05-22
> **适用项目**: fund-agent
> **参考框架**: code-is-cheap 工程控制框架

---

## 1. 诊断摘要

### 1.1 核心问题

**项目当前状态不是"开发远超 design.md"，而是：**

> Design.md 和 Implementation-control.md 已经分裂成两个独立演进的事实源，导致没有单一真源可以判定"什么该做、什么不该做"。

### 1.2 问题清单

| 问题 | 严重程度 | 说明 |
|------|----------|------|
| **P1: 非目标被绕过** | 🔴 高 | Design.md 第 1.3 节的"不做温度计自建"被突破，ThermometerService 已实现 |
| **P2: Phase 粒度过细** | 🟡 中 | P13-P16 实质处理同一问题，应合并为单一 Phase |
| **P3: Exit Criteria 不可验证** | 🔴 高 | 当前 exit criteria 是"实现 xxx"，而非可自动化验证的指标 |
| **P4: Plan Review 缺设计对照** | 🟡 中 | Review artifacts 未显式检查"plan 是否超出 design.md 范围" |
| **P5: 设计文档未及时回写** | 🔴 高 | Control doc 已到 P16，design.md 仍为 v2.0，两者分离 |

### 1.3 非目标遵守检查

| 非目标（design.md §1.3） | 当前实现状态 | 是否越界 | 处理建议 |
|--------------------------|--------------|----------|----------|
| 不做全市场横向比较 | 未实现 | ✅ 遵守 | — |
| 不做实时行为偏差检测 | 未实现 | ✅ 遵守 | — |
| **不做温度计自建** | ThermometerService + CLI 已实现 | ⚠️ **越界** | 保留但标记为 v2 功能，或回滚 |
| 不做组合管理 | 未实现 | ✅ 遵守 | — |
| 不输出买卖建议或仓位比例 | 未实现 | ✅ 遵守 | — |
| 不把外部 Dayu Host/Engine 作为主链路依赖 | config 目录结构暗示抽象层 | ⚠️ **风险** | 明确声明：config 只含路径常量 |

---

## 2. 短期修复方案（立即执行）

### 2.1 冻结开发，执行设计对齐审查

**目标**：生成一份 Design Alignment Review artifact，显式列出当前代码与 design.md 的所有偏差。

**执行步骤**：

```markdown
## Design Alignment Review — 2026-05-22

### 1. 非目标遵守检查
[填写上表内容]

### 2. 已实现功能与 design.md 对照
| 功能 | design.md 是否记录 | 处理决定 |
|------|-------------------|----------|
| ThermometerService | 否 | 保留并回写 design.md §6.3 |
| Thermometer CLI | 否 | 保留并回写 design.md §9 CLI 命令清单 |
| tracking_error 直接披露 | 是（P13 记录） | ✅ 已对齐 |
| index_profile 结构化 | 是（P14 记录） | ✅ 已对齐 |

### 3. Phase 范围检查
- P13-P16 是否应合并为单一 Phase "Index Data Quality"？ → **是**
- 当前 Phase 的 exit criteria 是否可验证？ → **否，需重构**

### 4. Design.md 更新需求
- [ ] 回写 ThermometerService 到 §6.3 外部数据
- [ ] 回写 thermometer CLI 到 §9 项目结构
- [ ] 调整 §1.3 非目标：明确"不做温度计自建计算，但可查询有知有行公开数据"
```

**产物路径**：`docs/reviews/design-alignment-review-20260522.md`

---

### 2.2 更新 design.md 到 v2.1

**目标**：让 design.md 反映当前已实现功能，消除与代码的事实分离。

**具体修改**：

#### 修改 1：调整 §1.3 非目标

```markdown
### 1.3 非目标

- 不做全市场横向比较（MVP 在精选基金池内做质量门控）
- 不做实时行为偏差检测（改为买入前检查清单）
- **不做温度计自建计算**（MVP 使用有知有行公开页面数据查询，不自行计算温度值）
- 不做组合管理（v2 阶段）
- 不输出买卖建议或仓位比例
- 不把外部 Dayu Host/Engine/tool loop 作为主链路依赖或运行时接口
```

#### 修改 2：补充 §6.3 外部数据

```markdown
### 6.3 外部数据

| 数据 | 来源 | 获取方式 | 代码位置 |
|------|------|---------|---------|
| 基金年报 PDF | EID/证监会资本市场统一信息披露平台主源 + Eastmoney fallback | httpx 下载 | `documents/sources.py` |
| 基金净值序列 | 天天基金 / akshare | API | `data/nav_data.py` |
| **温度计数据** | **有知有行公开页面** | **httpx + HTML 解析** | **`data/thermometer.py`** |
| 精选基金池 | 手动维护 CSV | 文件读取 | `extraction_snapshot.py` |

> **新增（v2.1）**：温度计查询通过 `ThermometerService` 和 `fund-analysis thermometer` CLI 提供，仅查询有知有行公开数据，不涉及自建计算。
```

#### 修改 3：补充 §9 CLI 命令清单

```markdown
## 9. 项目结构

### 9.0 CLI 命令清单

| 命令 | 功能 | 实现状态 |
|------|------|----------|
| `fund-analysis analyze` | 主分析入口 | ✅ 已实现 |
| `fund-analysis thermometer` | 温度计查询 | ✅ 已实现（v2.1 新增） |
| `fund-analysis extraction-snapshot` | 抽取快照 | ✅ 已实现 |
| `fund-analysis extraction-score` | 抽取评分 | ✅ 已实现 |
| `fund-analysis golden-prefill` | Golden 预填 | ✅ 已实现 |
| `fund-analysis golden-build` | Golden 构建 | ✅ 已实现 |
| `fund-analysis quality-gate` | 质量门控 | ✅ 已实现 |
| `fund-analysis checklist` | 检查清单 | ⬜ 占位，未接入 Service |
```

#### 修改 4：更新版本号

```markdown
> **版本**: v2.1
> **日期**: 2026-05-22
> **状态**: 已回写 P13-P16 实现事实，非目标已调整
```

---

### 2.3 重构 Phase 定义

**目标**：将 P13-P16 合并为单一 Phase P18，定义可验证的 exit criteria。

**新 Phase 定义**：

```markdown
## Phase P18: 指数基金核心指标数据质量

### Goal
让精选基金池中所有指数/增强指数基金的 tracking_error 和 index_profile
达到 production-ready 数据质量。

### Entry Criteria
- [ ] P12 已合入 main
- [ ] 当前 main 分支代码与 design.md v2.1 对齐
- [ ] 精选基金池 CSV 已确认（56 条记录，55 个唯一代码）

### Exit Criteria（可验证）
- [ ] 指数基金 tracking_error coverage ≥ 90%
- [ ] 指数基金 tracking_error traceability ≥ 90%
- [ ] 增强指数基金 index_profile coverage ≥ 90%
- [ ] 增强指数基金 index_profile traceability ≥ 90%
- [ ] 无直接披露证据的基金明确标记 `unavailable`，不估算
- [ ] 3 只样本基金（004393, 001548, 017644）CLI 端到端测试通过
- [ ] Quality gate FQ1-FQ6 全部通过
- [ ] 程序审计 P1/P2/P3/C2/L1/R1/R2 全部通过

### Hard Constraints（明确不做）
- 只使用年报直接披露数据
- 不引入外部指数数据适配器（如中证指数 API）
- 不实现计算型 tracking_error
- 不添加无直接披露证据基金的 golden answer
- 不修改 design.md 定义的分层边界

### Scope Mapping（原 Phase 归并）
| 原 Phase | 内容 | 归入 P18 子任务 |
|----------|------|-----------------|
| P13 | tracking_error 直接披露路径 | P18-S1 |
| P14 | index_profile/tracking_error 质量分母 | P18-S2 |
| P15 | tracking_error golden evidence（blocked） | P18-S3（标记 blocked） |
| P16 | enhanced-index index_profile golden | P18-S4 |
```

---

## 3. 中期修复方案（本周执行）

### 3.1 建立「设计漂移检测」机制

**目标**：在每个 plan review 中强制检查设计边界。

**Plan Review Checklist 模板**：

```markdown
## Plan Review Checklist

### 1. 设计边界检查
- [ ] 本 plan 是否超出 design.md §1.3 非目标？
- [ ] 本 plan 是否引入 design.md 未定义的新依赖？
- [ ] 本 plan 是否修改 design.md 定义的分层边界？

### 2. Exit Criteria 可验证性检查
- [ ] 每个 exit criterion 是否可自动化验证？
- [ ] 是否有"实现 xxx"这类不可验证的 criterion？
- [ ] 是否有覆盖率/通过率等量化指标？

### 3. 设计更新需求检查
- [ ] 如果 plan 超出 design.md，是否同时提出 design.md 更新？
- [ ] design.md 更新是否在 plan 中显式列出变更内容？

### 4. 决策记录
| 检查项 | 结果 | 处理决定 |
|--------|------|----------|
| 是否超出非目标 | 是/否 | 保留/回滚/延期 |
| 是否需要更新 design.md | 是/否 | 更新内容：... |
```

---

### 3.2 修改 phaseflow 执行流程

**目标**：在 phaseflow 中嵌入设计对照检查。

**建议流程**：

```
phaseflow 执行顺序（修改后）：

1. 读取 design.md → 提取设计边界（非目标、分层约束）
2. 读取 implementation-control.md → 确定当前 phase
3. 生成 plan → **新增：对照 design.md 检查 plan 是否越界**
4. plan review → **新增：使用 Plan Review Checklist**
5. 如果越界 → 暂停，要求显式决策（更新 design 或裁剪 plan）
6. 继续原有流程（实现 → 代码评审 → 审计 → ...）
```

---

### 3.3 建立 design.md 版本控制

**目标**：让 design.md 的变更可追溯。

**建议**：

1. 每次更新 design.md 时，在文档头部记录变更摘要：

```markdown
> **版本**: v2.1
> **日期**: 2026-05-22
> **变更摘要**:
> - §1.3 非目标调整：明确温度计查询允许，自建计算不允许
> - §6.3 新增温度计数据源说明
> - §9 新增 CLI 命令清单
```

2. 在 implementation-control.md 中记录 design.md 版本依赖：

```markdown
| Design truth | `docs/design.md` (v2.1) |
```

---

## 4. 长期机制建设

### 4.1 单一真源原则

**原则**：任何时候，design.md 和 implementation-control.md 必须保持一致。

**执行规则**：

| 场景 | 规则 |
|------|------|
| 新增功能 | 先更新 design.md，再创建 Phase |
| Phase 完成 | 检查是否需要回写 design.md |
| 发现偏离 | 立即暂停，执行 Design Alignment Review |
| design.md 更新 | 同步更新 implementation-control.md 的 design truth 引用 |

---

### 4.2 Phase 定义规范

**原则**：每个 Phase 必须是用户可感知的功能增量，而非任务清单。

**规范**：

| 要素 | 要求 |
|------|------|
| Goal | 一句话说明用户价值 |
| Entry Criteria | 可自动化验证的前置条件 |
| Exit Criteria | 可自动化验证的后置条件（覆盖率/通过率/测试结果） |
| Hard Constraints | 明确不做的事项 |
| Scope Mapping | 如果合并多个原 Phase，说明归并关系 |

---

### 4.3 Review 机制强化

**原则**：所有 review 必须包含设计对照检查。

**Review 类型与要求**：

| Review 类型 | 必须检查 |
|-------------|----------|
| Plan Review | 是否超出 design.md 范围 |
| Code Review | 是否符合 design.md 分层边界 |
| Aggregate Deepreview | 是否有未记录的设计偏离 |

---

## 5. 执行检查清单

### 5.1 立即执行（今天）

- [ ] 创建 `docs/reviews/design-alignment-review-20260522.md`
- [ ] 更新 `docs/design.md` 到 v2.1
- [ ] 在 `docs/implementation-control.md` 中创建 P18 Phase 定义
- [ ] 标记 P13-P16 为"已归并于 P18"

### 5.2 本周执行

- [ ] 建立 Plan Review Checklist 模板
- [ ] 修改 phaseflow 执行流程（嵌入设计对照检查）
- [ ] 建立 design.md 版本控制机制

### 5.3 持续执行

- [ ] 每个 Phase 完成后检查是否需要回写 design.md
- [ ] 每次发现偏离时执行 Design Alignment Review
- [ ] 定期审计 design.md 与代码的一致性

---

## 6. 参考资源

- code-is-cheap 框架：https://github.com/noho/code-is-cheap
- code-is-cheap 核心理念：**代码是廉价的，工程控制才是昂贵的**
- 本项目 design.md：`docs/design.md`
- 本项目 implementation-control.md：`docs/implementation-control.md`

---

## 附录 A：Design.md v2.1 变更清单

| 章节 | 变更类型 | 变更内容 |
|------|----------|----------|
| Header | 版本更新 | v2.0 → v2.1，日期 2026-05-22 |
| §1.3 | 非目标调整 | "不做温度计自建" → "不做温度计自建计算，但可查询有知有行公开数据" |
| §6.3 | 新增内容 | 温度计数据源说明 |
| §9 | 新增章节 | CLI 命令清单 |

---

## 附录 B：Phase P18 子任务拆分

| 子任务 | 原 Phase | 内容 | 状态 |
|--------|----------|------|------|
| P18-S1 | P13 | tracking_error 直接披露路径 | 已实现 |
| P18-S2 | P14 | index_profile/tracking_error 质量分母 | 已实现 |
| P18-S3 | P15 | tracking_error golden evidence | Blocked（无直接披露证据） |
| P18-S4 | P16 | enhanced-index index_profile golden | 已实现 |

**P18 整体状态**：部分完成，P18-S3 标记为 blocked，不阻断 P18 关闭。
