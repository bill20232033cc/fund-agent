# P4 审计输入独立评审

> **日期**: 2026-05-19
> **审核对象**: `docs/repo-audit-20260519.md` + `docs/p4-plan-review-20260519.md`
> **审核基准**: `docs/design.md`、`docs/implementation-control.md`、`docs/post-mvp-p4-first-principles-plan.md`、仓库实际代码
> **角色**: AgentMiMo 独立 plan/repo audit reviewer。只读审查，不改代码。

---

## Verdict

**Repo audit 整体评分偏高，存在多处事实错误和对 design.md 免责声明的忽略。P4 plan review 质量良好，大部分建议合理但多数已被 P4 草案覆盖。两份审查均不应作为 controller 直接执行的输入——需要逐条裁决后再采纳。**

核心判断：当前项目的第一性原理目标是"精选基金池报告可度量、可复核、可迭代"。所有文档形式一致性、架构预设、过早抽象的建议都应让位于这个目标。

---

## Adopt Now（应立即采纳）

### A1. dayu-agent 依赖应降级为 optional

**来源**: repo-audit §2.1
**事实**: `pyproject.toml` 确实声明了 `dayu-agent v0.1.4`，但 `fund_agent/` 零导入。
**裁决**: 事实正确。这是唯一一个 repo audit 中既事实正确又值得现在处理的 P0 问题。dayu-agent 作为硬依赖会在新环境安装时引入不必要的下载和潜在的 GitHub 可达性问题（已在 RR-5 追踪）。
**行动**: 移至 `[project.optional-dependencies]`，加注释 `# v2: dayu.engine / dayu.host integration`。

### A2. 更新 design.md 第 2.1 节，标注 MVP 未使用 dayu

**来源**: repo-audit §2.2
**事实**: design.md 第 2.1 节写了"直接复用 dayu.engine/dayu.host"，但实际 MVP 未使用。
**裁决**: 虽然 design.md 顶部已有免责声明（第 8 行："第7章中的代码路径在代码实现前为预览性质"），但该免责声明只覆盖第 7 章，不覆盖第 2.1 节的架构声明。这是一个真实的文档-代码偏差。
**行动**: 在第 2.1 节加一行注记：`> MVP 阶段未接入 dayu-engine，当前 Engine/Host 由自建实现承载。v2 规划接入。`

### A3. P4 应有独立实施控制文档

**来源**: p4-plan-review §四
**裁决**: 合理。当前 `implementation-control.md` 已有 1268 行，再追加 P4 会进一步膨胀。独立的 `docs/implementation-control-p4.md` 更清晰。
**行动**: 创建独立文档，遵循 P1-P3 的 gate/slice/residual-risk 格式。

### A4. P4 草案应明确 6 只 golden set 具体代码

**来源**: p4-plan-review §三 Open Questions
**裁决**: P4 草案 Step 4 说"建议第一批 6 只，按类别覆盖"，但只指定了 `004393`，其余 5 只只给了类别。这会在执行时反复确认。
**行动**: 在 P4-S1 冻结时确认具体代码。reviewer 建议的 6 只（004393/110011/000001/519772/000322/159915）可作为起点，但需用户确认。

---

## Defer（应延后采纳）

### D1. snapshot 增加 `extraction_timestamp` 和 `extractor_version`

**来源**: p4-plan-review §二 Step 2
**裁决**: 合理但非 P4-S1 阻塞项。第一版 snapshot 可以先不带版本元数据，等 extractor 有实际迭代后再加。过早加版本字段会增加 snapshot schema 复杂度，而当前 extractor 只有一个版本。
**延后到**: P4-S2 或 extractor 首次实质性迭代后。

### D2. gate 阈值可配置化（放入 `config/settings.py`）

**来源**: p4-plan-review §二 Step 3
**裁决**: 过早抽象。当前 gate 阈值（P0 coverage >= 90%、基金类型正确率 100%）只有 3-4 个硬编码值，直接写在代码中比引入配置文件更清晰、更易测试。等阈值频繁调整或有多个环境需求时再配置化。
**延后到**: gate 阈值超过 10 个或需要 per-environment 差异化时。

### D3. FQ6：同一基金跨 run 的 snapshot diff

**来源**: p4-plan-review §二 Step 6
**裁决**: 好主意，但 P4 阶段没有跨 run 的实际需求。当前目标是建立第一个 baseline，不是做回归监控。跨 run diff 是 P5 或 CI 阶段的事。
**延后到**: 有至少 2 个 run-id 需要对比时。

### D4. CI gate 集成

**来源**: p4-plan-review §五 5.3
**裁决**: 当前 pytest 已有覆盖率 gate（90.07%）和性能 gate（<30s）。P4 的 quality gate 可以先作为独立 CLI 脚本运行，不急于集成到 CI。等 snapshot/score 稳定后再接入 pre-commit 或 GitHub Actions。
**延后到**: P4-S4 完成后评估。

### D5. 大文件拆分（renderer.py 32KB / risk_check.py 31KB）

**来源**: repo-audit §3.6
**裁决**: 这两个文件的内聚性都很高。`renderer.py` 渲染 8 章模板，每章的渲染逻辑都消费同一组输入，拆分只会增加跨文件跳转成本。`risk_check.py` 包含 5 项否决检查和压力测试，都属于"风险评估"单一职责。32KB 在 Python 中不算大文件。
**延后到**: 文件超过 50KB 或出现明确的职责分裂信号时。

---

## Reject / No Action（不采纳及理由）

### R1. implementation-control.md Phase 状态仍标记为 pending

**来源**: repo-audit §2.4
**事实错误**: 审核报告声称"所有 Phase 状态仍标记为 pending"，但实际 `implementation-control.md` 第 17-20 行明确显示 P0/P1/P2/P3 均为 `✅ done`。这是审核中的重大事实错误，说明审核人未仔细阅读 implementation-control.md 的实际内容。
**行动**: 不采纳。implementation-control.md 状态已正确更新。

### R2. 拆分 audit_programmatic.py 为 audit_coordinator.py + audit_rules.py

**来源**: repo-audit §3.1
**裁决**: 过早拆分。`audit_programmatic.py` 当前只有 6 条规则（P1/P2/P3/L1/R1/R2），总计约 15KB。规则定义和执行逻辑的分离在规则数量超过 15-20 条时才有维护收益。现在拆分会增加文件数量但不增加可维护性。
**行动**: 不采纳。

### R3. 提升 checklist 为 Service 层

**来源**: repo-audit §3.2
**裁决**: 架构误读。当前项目的四层架构（UI/Service/Capability/Engine）中，checklist 属于 Capability 层（基金分析能力），不是 Service 层（业务编排）。`FundAnalysisService` 作为 Service 层编排 checklist，这是正确的分层。repo audit 用 design.md 中的早期设计草案来评判实际实现，忽略了实际实现的分层合理性。
**行动**: 不采纳。当前分层正确。

### R4. 补充 contract_preparation.py

**来源**: repo-audit §3.3
**裁决**: 过度架构化。design.md 描述的 `ExecutionContract` 和 `Contract preparation` 是 dayu-agent 框架的概念。MVP 未使用 dayu-agent，自然不需要这个抽象层。`FundAnalysisService.analyze()` 直接编排 Capability 模块，比引入 Contract 抽象更简洁。
**行动**: 不采纳。

### R5. config/ 和 tools/ 目录"为空"

**来源**: repo-audit §3.4, §3.5
**事实错误**: `config/` 包含 `__init__.py` 和 `prompts/` 子目录（含 `scenes/`、`tasks/`、`base/`），`fund/tools/` 包含 `__init__.py`。这些目录存在且有结构，只是内容尚少。审核人说"为空"不准确。
**行动**: 不采纳。目录已存在，内容随 P4 开发自然填充。

### R6. 设计文档"失去真源地位"

**来源**: repo-audit §五
**裁决**: 过度担忧。design.md 顶部已有免责声明，且 implementation-control.md 的详细状态日志才是实际的项目管控真源。design.md 的定位是"设计决策记录"，不是"当前实现描述"。两者混淆是 repo audit 的根本性视角错误。
**行动**: 不采纳。当前文档体系（design.md 做设计记录 + implementation-control.md 做实施管控 + 代码 README 做实现描述）是合理的三层分工。

### R7. P4 计划与 implementation-control.md 的关系需额外明确

**来源**: p4-plan-review §四
**裁决**: P4 草案已明确自定位为"post-MVP 第一性原理行动计划"，且 implementation-control.md 的"下一 gate"已指向 `post-MVP follow-up planning`。关系已经隐含明确——P4 是 post-MVP 阶段的独立计划。额外的"关系声明文档"是冗余的。
**行动**: 只需创建 `docs/implementation-control-p4.md` 即可（见 A3），不需要额外的关系说明文档。

---

## Needs Evidence（需要更多证据）

### N1. 基金类型误判的 root cause 是否确实是"业绩基准含指数词"

**来源**: P4 荲案 §2.2
**现状**: P4 荲案说 `004393` 被识别为 `index_fund`，root cause 初步判断是"业绩基准里的沪深300指数等指数词误当成基金本身的指数特征"。
**需要证据**: 查看 `fund_type.py` 的实际分类逻辑，确认：
1. 分类器是否只看名称/类别/基准/投资范围（当前 README 说是）
2. 债券基金名称优先规则是否已覆盖 `004393` 的情况
3. 是否需要运行 `fund-analysis analyze 004393` 复现误判

这是 P4 的第一个阻塞问题。在确认 root cause 之前，Step 5 的修复方案无法具体化。

### N2. 56 只精选基金的实际类别分布

**来源**: P4 荲案 §2.1
**现状**: 只知道 56 条记录、55 个唯一代码、`016492` 重复。
**需要证据**: 运行 `scripts/selected_funds_smoke.py` 的 dry-run 模式，获取按 App 分类的分布统计。这决定了 golden set 的抽样策略是否合理。

---

## Controller Risks（给 controller 的风险提醒）

### CR1. Repo audit 的可信度问题

repo-audit-20260519.md 存在至少 3 个事实错误（Phase 状态、config/ 为空、tools/ 为空），且忽略了 design.md 的免责声明。这说明审核人对仓库的实际状态理解不够深入。**Controller 不应直接信任 repo audit 的优先级排序，应逐条验证后再执行。**

### CR2. P4 荲案的 Step 依赖链需要注意

P4 的 6 个步骤有隐含依赖：
- Step 2（snapshot）依赖 Step 1（冻结基金池）
- Step 3（评分规则）依赖 Step 2（snapshot schema）
- Step 4（golden set）依赖 Step 3（评分规则定义）
- Step 5（修 bug）依赖 Step 4（golden set 作为回归基准）
- Step 6（审计升级）依赖 Step 5（修复验证）

这意味着 Step 1-4 不能并行，且 Step 1 的 `016492` 重复问题会阻塞后续所有步骤。建议 P4-S1 先处理重复问题（采用选项 B：允许重复但标红），不阻塞进度。

### CR3. 不要让"文档同步"变成 P4 的隐藏成本

repo audit 建议更新 design.md、创建新的 implementation-control 文档、补充产出物定义等。这些建议单独看都合理，但叠加起来会消耗大量时间。**P4 的核心目标是质量闭环，不是文档完美。** 建议只做 A1-A4 四项最小文档同步，其余随 P4 实施自然更新。

### CR4. golden set 的人工标注成本

P4 Step 4 要求对 6 只基金的 P0 字段做人工 golden answer 标注。这只在标注工具和标注规则明确后才可执行。如果标注规则（Step 3）和 snapshot（Step 2）未先就绪，golden set 工作会停滞。建议 P4-S1 同时输出标注规则草案，不等 P4-S2 完成后再启动。

---

## 附录：Repo Audit 逐条裁决速查表

| 章节 | 意见 | 裁决 | 分类 |
|------|------|------|------|
| §2.1 | dayu-agent 零导入 | 事实正确，应降级 optional | **Adopt** |
| §2.2 | design.md 说复用 dayu 但代码未接入 | 事实正确，需标注 MVP 未使用 | **Adopt** |
| §2.3 | 项目结构与 design.md ch7 不一致 | 已有免责声明，偏差已知 | **Reject** |
| §2.4 | implementation-control 状态未更新 | **事实错误**：状态已正确更新 | **Reject** |
| §3.1 | 拆分 audit 文件 | 过早拆分 | **Reject** |
| §3.2 | checklist 提升为 Service | 架构误读 | **Reject** |
| §3.3 | 补充 contract_preparation | 过度架构化 | **Reject** |
| §3.4 | config/ 为空 | **事实错误**：有内容 | **Reject** |
| §3.5 | tools/ 为空 | **事实错误**：有 __init__.py | **Reject** |
| §3.6 | 大文件拆分 | 内聚性高，暂不需要 | **Defer** |

## 附录：P4 Plan Review 逐条裁决速查表

| 建议 | 裁决 | 分类 |
|------|------|------|
| snapshot 加 timestamp/version | 合理但非阻塞 | **Defer** |
| gate 阈值可配置化 | 过早抽象 | **Defer** |
| 明确 6 只 golden set 代码 | 需用户确认 | **Adopt** |
| 货币基金不纳入 P4-S1 | P4 荲案已覆盖 | **No action** |
| 不要求真实 network/PDF 全量 | P4 荲案已覆盖 | **No action** |
| 独立 implementation-control-p4 | 合理 | **Adopt** |
| P4-S1~S4 任务切片 | 合理，与 P4 步骤对齐 | **Adopt** |
| 产出物列表（scripts/docs） | 合理但随 P4 自然创建 | **Defer** |
| 验收条件 | 合理且具体 | **Adopt** |
| FQ6 跨 run diff | P5+ 的事 | **Defer** |
| CI gate 集成 | 先独立 CLI，后接 CI | **Defer** |
| Dayu-Agent 对齐补充 | P4 荲案 §5 已覆盖 | **No action** |

---

> 审核人：AgentMiMo
> 审核完成时间：2026-05-19
