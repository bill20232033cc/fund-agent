# P4 Audit Input Controller Judgment

> 日期：2026-05-19
> 输入：`docs/repo-audit-20260519.md`、`docs/p4-plan-review-20260519.md`
> 独立复核：`docs/reviews/p4-audit-input-review-mimo-20260519.md`、`docs/reviews/p4-audit-input-review-glm-20260519.md`
> 裁决目标：从第一性原理判断哪些建议应采纳、延后、不采纳或需要更多证据。

## 1. Controller Verdict

当前 P4 的主目标是建立“精选基金池报告可度量、可复核、可迭代”的质量闭环。

因此，本轮裁决原则如下：

1. 直接服务 P4 质量闭环的建议优先采纳。
2. 能防止用户或开发者误解当前能力边界的最小文档同步可以采纳。
3. 仅为了匹配早期 design 草案、补空目录、过早拆分模块或过早配置化的建议不采纳或延后。
4. 任何建议必须先经过事实核验；不能因为它出现在 audit 文档里就直接执行。

结论：

- `docs/p4-plan-review-20260519.md` 的方向基本可取，但其中 golden set 具体代码建议存在事实问题，不能直接采纳。
- `docs/repo-audit-20260519.md` 中 dayu 依赖与 design 文档偏差属实；implementation-control 状态未更新、config/tools 完全为空等说法存在事实错误或误读。
- 下一步应创建 P4 实施控制文档，并把 P4-S1 定义为 extraction snapshot + quality gate MVP。

## 2. Adopt Now

### A1. 创建独立 P4 实施控制文档

来源：

- `docs/p4-plan-review-20260519.md`
- MiMo A3
- GLM “implementation-control-p4.md” 建议

裁决：采纳。

理由：

- 主 `docs/implementation-control.md` 已很长，继续追加 P4 细节会降低可维护性。
- P4 与 P1-P3 性质不同：P1-P3 是 MVP 功能建设，P4 是质量系统建设。
- 独立文档可以明确 P4-S1 到 P4-S4、验收条件、风险和 owner。

建议做法：

- 新增 `docs/implementation-control-p4.md`。
- 主 `docs/implementation-control.md` 只保留 P4 总览和链接，不承载所有 slice 细节。

### A2. 采纳 P4-S1 到 P4-S4 的任务切片

来源：

- `docs/p4-plan-review-20260519.md`
- MiMo A3/A4
- GLM P4 slicing recommendation

裁决：采纳。

建议切片：

| Slice | 目标 | 验收 |
|---|---|---|
| P4-S1 | Selected Fund Extraction Snapshot + Quality Gate MVP | 能对指定基金和分层抽样基金生成 snapshot 与 summary |
| P4-S2 | 字段级评分规则 + Golden Set 标注 | P0 字段 coverage / traceability 可计算 |
| P4-S3 | 修复基金类型误判 + 高影响 extractor 缺口 | `004393` 不再误判为 `index_fund`，并由 score 证明改进 |
| P4-S4 | 报告质量审计与阻断 | 低质量输入可被 quality gate 标记或阻断 |

### A3. 明确 golden set，但不能采纳 review 给出的具体代码

来源：

- `docs/p4-plan-review-20260519.md`
- MiMo A4
- GLM “Adopt now（部分）”

裁决：采纳“必须明确 golden set”的原则；不采纳 review 中给出的具体代码列表。

事实核验：

- `docs/p4-plan-review-20260519.md` 建议 `004393、110011、000001、519772、000322、159915`。
- 这些代码中只有 `004393` 存在于 `docs/code_20260519.csv`。
- `110011、000001、519772、000322、159915` 均不在当前精选基金池 CSV 中。

行动：

- P4-S1 只能从 `docs/code_20260519.csv` 中选择 golden set。
- `004393` 必须纳入，因为它是已知 failure case。
- 其它代码应按 App 类别从 CSV 中重新选择，而不是沿用 review 建议。

### A4. P4 snapshot 采用离线优先设计

来源：

- `docs/p4-plan-review-20260519.md`
- GLM “Adopt now 离线设计”

裁决：采纳。

理由：

- 质量评分应尽量基于已缓存/已解析的年报产物，减少实时网络波动对结果的污染。
- 真实 network/PDF smoke 可以保留，但不能成为每次 scoring 的必要前置。

### A5. Snapshot 字段加入最小元数据

来源：

- `docs/p4-plan-review-20260519.md`
- GLM “Adopt now”
- MiMo “Defer”

裁决：部分采纳。

第一版 snapshot 建议加入：

- `run_id`
- `extraction_timestamp`
- `fund_code`
- `app_category`
- `field_name`
- `extraction_mode`
- `value_present`
- `anchor_present`
- `section_id`
- `table_id`
- `row_id`

`extractor_version` 暂不要求接复杂版本系统；可先记录当前 git commit 或 package version。这样既保留跨 run 可追溯性，也避免过早架构化。

### A6. 最小同步 design.md 的 dayu/MVP 边界

来源：

- `docs/repo-audit-20260519.md`
- MiMo A2
- GLM Defer

裁决：采纳最小同步，不做大改。

理由：

- `docs/design.md` 顶部确实说“实际实现以代码为准”，但第 2.1 节明确写了 Engine/Host 直接使用 dayu，容易误导后续开发者。
- 当前 P4 不应大规模重写 design.md，但应补一条现实边界：MVP 当前未接入 dayu Engine/Host；dayu 作为后续架构参考或 v2 接入候选。

行动：

- 在 design.md 架构段落加 MVP 实现注记即可。
- 不追求第 7 章项目结构完全重写。

## 3. Defer

### D1. dayu-agent 依赖降级 optional 或移除

来源：

- `docs/repo-audit-20260519.md`
- MiMo A1
- GLM Defer

裁决：延后到 P4 planning cleanup，不作为 P4-S1 阻塞项。

理由：

- 事实正确：`pyproject.toml` 声明 dayu-agent，但当前 `fund_agent/` 没有 dayu import。
- 它会影响新环境安装稳定性，也已在 RR-5 体现。
- 但它不阻塞 extraction snapshot / score / golden set 的建立。

建议：

- 在 P4 control 文档中列为 cleanup item。
- 若近期要给外部用户安装，则提前处理；否则不抢 P4-S1 优先级。

### D2. Gate 阈值配置化

来源：

- `docs/p4-plan-review-20260519.md`
- MiMo D2
- GLM Defer

裁决：延后。

理由：

- P4-S1 先验证 snapshot 和 scoring 链路，阈值可以硬编码在测试或 scoring 模块中。
- 等阈值稳定、有多环境需求或字段数量显著增加后，再迁入配置。

### D3. FQ6 跨 run snapshot diff

来源：

- `docs/p4-plan-review-20260519.md`
- MiMo D3
- GLM Defer

裁决：延后。

理由：

- 需要至少两个稳定 run 之后才有实际意义。
- 可在 P4-S4 或 P5 作为回归监控能力加入。

### D4. CI / pre-commit gate 集成

来源：

- `docs/p4-plan-review-20260519.md`
- MiMo D4
- GLM Defer

裁决：延后。

理由：

- P4-S1/S2 期间 snapshot schema 和评分规则还会变化。
- 先保留独立 CLI / pytest 单测；等规则稳定后再接 CI。

### D5. 大文件拆分

来源：

- `docs/repo-audit-20260519.md`
- MiMo D5
- GLM Defer

裁决：延后。

理由：

- `renderer.py` 和 `risk_check.py` 大，但职责仍较内聚。
- 当前痛点不是文件大小，而是真实基金池提取质量不可量化。
- 只有当 P4 新增逻辑导致职责明显分裂时再拆。

### D6. audit_coordinator.py / audit_rules.py 拆分

来源：

- `docs/repo-audit-20260519.md`

裁决：延后，不进入 P4-S1。

理由：

- 现有 `audit_programmatic.py` 规则数量有限。
- P4-S4 增加 FQ 规则时再评估是否需要拆分。

## 4. Reject / No Action

### R1. “implementation-control.md 所有 Phase 仍 pending”

来源：`docs/repo-audit-20260519.md`

裁决：不采纳。

事实：

- `docs/implementation-control.md` 当前 P0/P1/P2/P3 均为 `✅ done`。
- 当前 gate 为 `P3 closed / PR 2 merged`，下一 gate 为 `post-MVP follow-up planning`。

说明：

- 文档中部分旧 checkbox 可能未同步，但 repo audit 的“所有 Phase pending”判断是事实错误。

### R2. checklist_service.py 必须独立为 Service 层

来源：`docs/repo-audit-20260519.md`

裁决：不采纳。

理由：

- 检查清单是基金领域分析能力，属于 Capability / analysis。
- Service 层负责编排它，而不是承载规则本身。
- 当前分层符合 AGENTS 模块边界：基金类型、规则、审计、CHAPTER_CONTRACT 应放在 Capability。

### R3. contract_preparation.py 现在必须补齐

来源：`docs/repo-audit-20260519.md`

裁决：不采纳。

理由：

- Contract preparation 是 dayu scene/host 路径里的抽象。
- 当前 MVP CLI 直接走 Service + Capability，强行补该文件是过早架构化。

### R4. 为匹配 design.md 第 7 章补空 tools/config/prompts 文件

来源：`docs/repo-audit-20260519.md`

裁决：不采纳。

理由：

- design.md 第 7 章本身声明为预览性质，实际实现以代码为准。
- 当前 P4 要解决的是真实精选基金池质量，而不是补齐早期架构草图中的占位文件。

### R5. 直接采纳 P4 review 给出的 6 只 golden set 代码

来源：`docs/p4-plan-review-20260519.md`

裁决：不采纳。

理由：

- 代码不在 `docs/code_20260519.csv` 中，除 `004393` 外均不能作为“精选基金池 golden set”。

## 5. Needs Evidence

### N1. `016492` 重复代码的真实修正

当前事实：

- `docs/code_20260519.csv` 有 56 条记录、55 个唯一代码。
- `016492` 同时对应“南方均衡成长混合A”和“易方达逆向投资混合A”。

裁决：

- P4-S1 允许重复但必须标红，不阻塞 snapshot。
- 真实修正需要用户从有知有行 App 或原始导出核对。

### N2. P4 golden set 具体名单

当前事实：

- 只能从 `docs/code_20260519.csv` 中选择。
- `004393` 必须纳入。

裁决：

- P4-S1 前需要生成候选名单，并由用户确认或由 controller 按类别默认选择。

### N3. `004393` 类型误判 root cause 的最终代码级确认

当前事实：

- 本地复现显示 `004393` 生成报告时 `classified_fund_type=index_fund`。
- 初步原因是分类逻辑把业绩基准中的指数词当作指数基金特征。

裁决：

- 进入 P4-S3 前必须写入最小复现测试，再修分类器。

## 6. Updated P4 Priority

建议下一步顺序：

1. 写 `docs/implementation-control-p4.md`，定义 P4-S1 到 P4-S4。
2. 在主 `implementation-control.md` 中仅追加 P4 指针和当前 gate。
3. P4-S1：实现 extraction snapshot MVP。
4. P4-S1 同时把 `016492` 重复标红，不阻塞运行。
5. P4-S2：定义 scoring 和 golden set。
6. P4-S3：用 scoring 结果驱动修 `004393` 类型误判和高缺失字段。
7. P4-S4：接入 report quality gate。

## 7. Final Notes

Trae repo audit 的价值在于提醒 dayu/design 偏差，但它把“文档形式一致性”排得过高，且包含事实错误。P4 plan review 的价值更高，方向与当前第一性原理一致；但其中具体 golden set 代码必须重选。

Controller 最终采纳口径：**质量闭环优先，最小文档同步，拒绝过早架构化。**
