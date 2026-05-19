# P4 Audit Input Review — AgentGLM Independent Assessment

> **日期**: 2026-05-19
> **审核者**: AgentGLM (plan/repo audit reviewer)
> **审核范围**: `docs/repo-audit-20260519.md` + `docs/p4-plan-review-20260519.md`
> **审核基准**: 第一性原理 — 当前目标是让精选基金池报告可度量、可复核、可迭代

---

## Verdict

Repo audit 方向大体正确但包含一个事实错误（implementation-control 状态）和若干过时/误读。P4 plan review 质量高于 repo audit，建议采纳率约 70%。两份文档的核心盲点是：均未识别出 design.md 自身已在第 1 行标注"设计草案"且声明"实际实现以代码为准"，因此部分"设计文档与代码脱节"发现本质上是 design.md 的已知状态而非新发现。

---

## 一、Repo Audit 逐项裁决

### 2.1 dayu-agent 依赖声明但零导入

**事实**: ✅ 正确。`pyproject.toml` 声明 `dayu-agent v0.1.4`，`grep -r "from dayu\|import dayu" fund_agent/` 返回零结果。

**裁决**: **Defer**

**理由**: P4 目标是建立精选基金池提取质量闭环。dayu-agent 依赖声明不影响 extraction snapshot、quality gate 或 golden set 的建立。它是一个 pyproject.toml 卫生问题，不阻塞任何 P4 步骤。应在 P4 质量闭环稳定后的 v2 规划期清理，此时可一并决定是移除还是标记 optional。

---

### 2.2 设计文档说"直接复用 dayu.engine/dayu.host"但代码未接入

**事实**: ✅ 正确。design.md §2.1 和 §7.1 写了直接复用，代码零导入。

**裁决**: **Defer**

**理由**: design.md 第 8 行已明确声明"本文档为设计草案"且"实际实现以代码为准"。这不是"脱节"而是 design.md 自身标注的已知状态。MVP 选择自建 Capability 层而非接入 dayu 框架，这是已记录的设计决策。P4 不应花时间回填设计文档。应在 v2 规划期、真正决定是否接入 dayu 时再同步。

**Controller 注意**: 如果 v2 确定接入 dayu，则需在接入前更新 design.md；如果确定不接入，应直接更新 design.md 移除 dayu 复用预期。无论哪种，都不是 P4 的工作。

---

### 2.3 项目结构与 design.md 第 7 章不一致

**事实**: ⚠️ 部分正确，部分误读。

逐项核实：

| 设计文档描述 | 实际状态 | Repo Audit 说法 | 事实判断 |
|---|---|---|---|
| tools/ 含 fund_doc_tools.py 等 | tools/ 只有 `__init__.py` | "目录为空" | ✅ 正确（空目录） |
| audit/ 含 coordinator, rules, models | 仅有 audit_programmatic.py | "缺失" | ✅ 正确 |
| config/prompts/ 存在 | config/prompts/ 存在但 base/scenes/tasks 子目录均为空 | "完全不存在" | ❌ 误读：目录存在，内容为空 |
| services/ 含 checklist_service, contract_preparation | 仅有 fund_analysis_service.py | "均不存在" | ✅ 正确 |

**裁决**: **Reject / no action on structure alignment; Defer config/prompts 填充**

**理由**: design.md 已标注为设计草案（第 8 行），项目结构偏差是 MVP 有意取舍的结果。当前 4 层架构（UI → Service → Capability → 数据）已完整落地并验证。补充缺失文件属于"追求文档形式一致"，不是"让报告可度量"。P4 应聚焦 extraction quality，不补空文件。

config/prompts/ 子目录为空但骨架已存在，v2 接入 LLM 或 scene 机制时自然填充。

---

### 2.4 实施总控文档状态未更新

**事实**: ❌ 事实错误。

**证据**: `implementation-control.md` 第 16-20 行 Phase 列表：

```
| P0 | ... | ✅ done |
| P1 | ... | ✅ done |
| P2 | ... | ✅ done |
| P3 | ... | ✅ done |
```

所有 Phase 状态均标记为 `✅ done`，且有详细的状态更新日志（第 1214-1267 行，30+ 条更新记录）。

Repo audit 声称"所有 Phase 状态仍标记为 `pending`"是不正确的。审计者可能只看了退出条件的 checkbox（确实未勾选）而忽略了 Phase 表格和状态更新日志。

**裁决**: **Reject / no action**

**附加说明**: P1 退出条件 checkbox 确实未勾选（仍是 `- [ ]`），这是一个文档卫生问题。但 Phase 状态已明确标记 done，且每个 Slice 的完成状态都有独立段落记录。勾选 checkbox 属于锦上添花，不阻塞 P4。

---

### 3.1 缺少 audit_coordinator.py 和 audit_rules.py

**裁决**: **Reject / no action**

**理由**: `audit_programmatic.py` 当前 15KB，实现 P1/P2/P3/L1/R1/R2 六类规则。从第一性原理看：当前审计规则数量有限（6 条），单文件可维护。P4 计划新增 FQ1-FQ5 五条质量审计规则，总共约 11 条规则——仍然不需要 coordinator 模式。拆分应在规则数量或复杂度实际增长到需要独立协调时再做，而非预判。

**何时应重新评估**: 如果 P4 FQ 规则 + v2 E1/E2/E3/C1/C2 规则总数超过 20 条，或规则间出现编排依赖，再拆分不迟。

---

### 3.2 缺少 checklist_service.py

**裁决**: **Reject / no action**

**理由**: 检查清单逻辑当前在 `analysis/checklist.py`，Service 层通过 `fund_analysis_service.py` 编排。checklist 不需要独立 Service——它是 P2 分析结果的一部分，由主 Service 统一编排。独立 Service 意味着独立编排入口、独立测试、独立错误处理，在 MVP 阶段是过度设计。如果 v2 引入独立 `fund-analysis checklist` 命令，再评估是否拆分。

---

### 3.3 缺少 contract_preparation.py

**裁决**: **Reject / no action**

**理由**: `CHAPTER_CONTRACT` 机制在 Capability 层的 `template/renderer.py` 中实现。Service 层不需要独立的 Contract preparation 模块——当前 `FundAnalysisRequest` → `FundAnalysisService` → `TemplateRenderInput` 链路清晰、显式。Contract preparation 是 dayu scene 框架的概念，当前 MVP 不使用 dayu scene 框架，所以不需要这个模块。

---

### 3.4 config/ 目录为空

**裁决**: **Defer**

**理由**: config/ 当前只有 `__init__.py` 和空的 prompts/ 子目录骨架。配置散落在各模块内部（如 fund_type.py 的类型标签、risk_check.py 的阈值表）。P4 plan review 建议 gate 阈值可配置化（§3 放入 config/settings.py），如果采纳则 config/ 自然会有内容。但这不是 P4 的前置条件——先让 snapshot/score 跑通，再决定哪些配置值得外置。

---

### 3.5 tools/ 目录为空

**裁决**: **Reject / no action**

**理由**: Repo audit 自身已承认"这是设计决策偏差，非代码缺陷"。tools/ 是 dayu toolset registrar 模式的占位目录，MVP 不使用 dayu 工具框架。保留空目录作为 v2 接入点，不需要在设计文档中额外声明——design.md 已标注为草案。

---

### 3.6 两个大文件需要关注

**事实**: ✅ 正确。renderer.py 32KB，risk_check.py 31KB。

**裁决**: **Defer**

**理由**: 两个文件内聚性均较高——renderer.py 按 8 章组织渲染逻辑，risk_check.py 按风险类型组织检查和压力测试。拆分不会改善可度量性或可复核性。应在 P4 新增 FQ 审计规则时观察 audit_programmatic.py 的增长，以及 renderer.py 是否因 P4 snapshot 逻辑需要扩展。如果增长超过 40KB 再考虑拆分。

---

## 二、P4 Plan Review 逐项裁决

### Snapshot 字段建议（增加 extraction_timestamp 和 extractor_version）

**裁决**: **Adopt now**

**理由**: 跨版本对比是 P4 质量闭环的核心能力。没有 timestamp 和 version，无法判断两次 snapshot 差异是 extractor 改进还是数据源变化。建议在 P4-S1 snapshot 字段定义中加入：
- `extraction_timestamp`: ISO 8601
- `extractor_version`: 当前可硬编码为 `"0.1.0"`，后续接入版本管理

---

### Gate 阈值可配置化（放入 config/settings.py）

**裁决**: **Defer**

**理由**: P4-S1 先用硬编码阈值验证整个 snapshot → score → gate 链路。过早配置化会增加 P4-S1 的实现范围（新增 config 模块、配置加载逻辑、配置测试），但不增加质量闭环的实质能力。等 P4-S1 跑通、阈值经过 golden set 验证后，再提取为配置。

---

### 明确 6 只 golden set 具体代码

**裁决**: **Adopt now（部分）**

**理由**: P4 plan review 建议 6 只：004393、110011、000001、519772、000322、159915。建议采纳分类覆盖原则，但具体代码应由 controller 在 P4-S1 实施时基于 CSV 数据确认。plan review 提供的 6 只代码是合理参考，不是最终决定。

**建议**: 在 P4-S1 实施时，由 controller 从 CSV 中按类别各选 1 只，并确认 004393 作为已知 failure case 固定进入 golden set。

---

### P4 任务切片 P4-S1 ~ P4-S4

**裁决**: **Adopt now**

**理由**: 切片合理，与 P4 计划 Step 1-6 对齐。具体切片：

| Slice | 范围 | 评价 |
|---|---|---|
| P4-S1 | Step 1-2：精选基金池冻结 + Extraction Snapshot MVP | ✅ 合理，最小可验证单元 |
| P4-S2 | Step 3-4：字段级评分规则 + Golden Set 标注 | ✅ 合理，依赖 P4-S1 的 snapshot 输出 |
| P4-S3 | Step 5：修复基金类型误判 + 扩展表格抽取 | ✅ 合理，以 P4-S2 的评分结果驱动修复优先级 |
| P4-S4 | Step 6：升级报告审计 FQ1-FQ5 + 质量阻断 CLI | ✅ 合理，收口为可自动化的质量 gate |

---

### FQ6 snapshot diff 建议

**裁决**: **Defer**

**理由**: FQ6（同一基金跨 run 的 snapshot diff 超过阈值）是回归检测能力，很有价值，但依赖 P4-S1 的 snapshot 机制先稳定运行。建议在 P4-S4 实现时评估是否纳入，如果 snapshot 格式尚未稳定则推迟到 v2。

---

### 创建独立 implementation-control-p4.md

**裁决**: **Adopt now**

**理由**: 主 `implementation-control.md` 已超过 1200 行。P4 作为独立 Phase 追加到主文档会导致继续膨胀，且 P4 的性质（质量闭环）与 P1-P3（功能实现）不同。独立文档更清晰。

但建议改为在主 implementation-control.md 的 Phase 列表中仅追加一行 P4 概要（名称、状态、指向 `docs/implementation-control-p4.md` 的链接），保持主文档作为全局总览的角色。

---

### P4 产出物建议（scripts/extraction_snapshot.py 等）

**裁决**: **Adopt now（调整优先级）**

| 产出物 | 优先级 | 评价 |
|---|---|---|
| extraction snapshot 生成能力 | 🔴 高 | P4-S1 核心产出，但应是库函数而非独立脚本 |
| quality score 计算能力 | 🔴 高 | P4-S2 核心产出，同样应是库函数 |
| golden-set-definition.md | 🟡 中 | 文档产出，P4-S2 实施时自然生成 |
| tests/fund/golden/*.json | 🟡 中 | golden answer fixture，P4-S2 实施时自然生成 |

建议 P4-S1 先实现为 `fund_agent/fund/` 内部的库函数（如 `extraction_snapshot.py`），CLI 通过 Service 层调用，而不是独立 scripts/ 脚本。这样 snapshot 生成能力可以被测试、被 CLI 和后续 CI gate 复用。

---

### Dayu-Agent 对齐补充（离线运行 + CI gate）

**裁决**: **Defer CI gate; Adopt now 离线设计**

**理由**: 离线运行设计正确——P4 snapshot 应基于已缓存的 parsed report，不依赖实时网络或 PDF 下载。这已在 `scripts/selected_funds_smoke.py` 中部分实现（deterministic fake repository）。

CI gate 集成（pytest 或 pre-commit）应推迟到 P4-S4，等 snapshot 格式和 score 规则稳定后再接入 CI。过早接入 CI 会导致频繁调整 gate 配置。

---

## 三、Controller Risks

1. **implementation-control.md 的 P1 退出条件 checkbox 未勾选**: 虽然 Phase 状态已标 done，但未勾选的 checkbox 可能被新成员或工具误读为"未完成"。建议在 P4 启动前花 10 分钟批量勾选已完成的退出条件。

2. **design.md 的"草案"标签风险**: design.md 同时充当"设计真源"和"设计草案"两种角色——implementation-control.md 引用它为"设计真源"，但 design.md 自身说"以代码为准"。这个张力应在 v2 规划期解决：要么更新 design.md 反映 MVP 实际架构并提升为正式文档，要么创建新的架构文档替代。

3. **P4 snapshot 格式稳定性**: P4-S1 定义的 snapshot 字段将成为后续 golden set、score 和 CI gate 的基础。字段设计应尽量保守——先覆盖 P4 计划已明确的字段，不过早扩展。一旦 golden set 开始标注，snapshot 格式变更成本会急剧上升。

4. **004393 基金类型误判**: 这是 P4 要修复的已知 bug，但修复应在 P4-S3（有评分数据之后）而非立即。立即修单点 bug 会跳过"建立量化基线"这一步，让后续无法判断修复是否泛化。

---

## 四、总结

| 分类 | 数量 | 项目 |
|---|---|---|
| **Adopt now** | 4 | snapshot timestamp/version 字段、P4 任务切片、implementation-control-p4.md、离线 snapshot 设计 |
| **Defer** | 6 | dayu 依赖清理、design.md 同步、config/prompts 填充、gate 阈值配置化、大文件拆分、FQ6 snapshot diff |
| **Reject / no action** | 7 | implementation-control 状态更新（已更新）、audit 拆分、checklist_service、contract_preparation、tools 空目录、项目结构对齐、CI gate |
| **Needs evidence** | 0 | 无 |

**核心判断**: Repo audit 的 10 项发现中，只有 2 项（dayu 依赖和 design.md 偏差）是事实正确且值得未来处理的，但都不是 P4 阻塞项。其余要么是事实错误（implementation-control 状态）、要么是过早架构化（audit 拆分、service 拆分）、要么是文档形式问题（config 骨架）。

P4 plan review 的建议整体采纳率更高，特别是任务切片和产出物建议。唯一的推迟项是 CI gate 和 gate 阈值配置化——先让闭环跑通再自动化。

---

> 审核完成时间：2026-05-19
> 审核者：AgentGLM
> Artifact 路径：`docs/reviews/p4-audit-input-review-glm-20260519.md`
