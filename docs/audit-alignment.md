# Dayu-Agent 审计机制与基金分析项目对照研究

> 本文档基于对 Dayu-Agent 审计机制的完整分析，逐层对照基金分析项目的审计需求，给出复用、适配、全新设计的分类判定与量化估算。所有结论均来自对 Dayu-Agent 源码的直接阅读与比对。

---

## 一、架构层对照

Dayu-Agent 与基金分析项目在审计架构上**完全同构**，均采用三层递进式审计：

| 层级 | Dayu-Agent | 基金分析项目 | 结论 |
|------|-----------|-------------|------|
| 第一层：程序化审计 | `audit_rules.py` 中的规则函数 | 需新建基金审计规则 | 骨架结构匹配、长度检查等可直接复用 |
| 第二层：LLM 审计 | `audit` scene + `audit_facts_tone_json` task | 需新建基金审计 scene/task | 结构复用，prompt 需按基金分析场景重写 |
| 第三层：证据复核 | `confirm` scene + `confirm_evidence_violations` task | 需新建基金证据复核 scene/task | 结构复用，工具调用适配为基金文档工具 |

### 编排器

- **Dayu-Agent**：使用 `ChapterAuditCoordinator` 统一编排三层审计流程，管理 audit → confirm → repair 的完整生命周期。
- **基金分析项目**：需新建 `FundAuditCoordinator`，继承编排逻辑，替换为基金领域的规则码、scene 定义和修复策略。

### Scene 机制

Dayu-Agent 将审计拆分为三个独立 scene：

| Scene | 职责 | 基金分析复用策略 |
|-------|------|----------------|
| `audit` | LLM 审计章节内容，输出违规列表 | 复用机制，重写 prompt（基金分析场景、规则码、判定标准） |
| `confirm` | 对 E 类违规进行证据复核 | 复用机制，适配工具调用（基金年报文档工具） |
| `repair` | 对确认的违规执行局部修复 | 复用机制，适配修复策略（锚点格式、处置模式） |

---

## 二、审计规则码对照

### 2.1 直接沿用（6 个）

以下规则码在两个项目中语义完全一致，可直接沿用：

| 规则码 | 含义 | Dayu-Agent 实现 | 基金分析适用性 |
|--------|------|----------------|---------------|
| **P1** | 章节骨架结构不匹配 | `_matches_skeleton_structure()` 比对章节标题与预期骨架 | 基金分析模板 8 章骨架同样需要结构校验 |
| **P2** | 章节内容长度异常 | 检查章节字数是否低于阈值 | 基金年报分析章节同样有最低内容量要求 |
| **E1** | 事实性声明缺少证据 | LLM 审计检测无证据支撑的事实声明 | 基金分析核心要求：所有判断必须有证据 |
| **E2** | 证据与声明不匹配 | LLM 审计检测证据与声明之间的逻辑断裂 | 基金分析核心要求：证据与结论必须对应 |
| **E3** | 证据来源不可靠 | LLM 审计评估证据质量 | 基金分析中需确保证据来自年报等权威来源 |
| **C1** | 章节内容越界 | 检查章节是否覆盖了不属于该章的内容 | 基金分析 CHAPTER_CONTRACT 中 must_not_cover 的程序化校验 |

### 2.2 全新设计（4 个）

以下规则码为基金分析项目特有，需全新设计：

| 规则码 | 含义 | 设计依据 | 实现层级 |
|--------|------|---------|---------|
| **L1** | R=A+B-C 计算错误 | 基金分析核心公式，需校验 Alpha/Beta/Cost 的数值拆分是否正确，且 Alpha + Beta - Cost = 投资者实际收益 | 程序化审计（数值校验） |
| **L2** | 百分位计算错误 | 基金排名、同类比较中的百分位数值需校验计算正确性 | 程序化审计（数值校验） |
| **R1** | 检查清单规则错误 | CHAPTER_CONTRACT 中的 must_answer / must_not_cover 规则是否被正确执行 | 程序化审计（规则校验） |
| **R2** | 判定与评分不一致 | 最终判断（值得持有/需要关注/建议替换）与各维度评分之间是否存在逻辑矛盾 | 程序化审计 + LLM 审计 |

### 2.3 建议引入（2 个）

| 规则码 | 含义 | 引入理由 | 优先级 |
|--------|------|---------|--------|
| **P3** | 缺少"证据与出处"小节 | 基金分析要求每章末尾有证据汇总，这是可程序化检查的结构性要求 | v2 |
| **C2** | 章节越界（细粒度） | 区别于 C1 的粗粒度检查，C2 检查章节内是否出现了属于其他 CHAPTER_CONTRACT 定义的内容 | v2 |

### 2.4 暂不引入（7 个）

| 规则码 | 含义 | 暂不引入理由 |
|--------|------|-------------|
| **S1** | 写作风格：语气不当 | 基金分析 MVP 阶段不关注写作风格，v2 再考虑 |
| **S2** | 写作风格：用词不当 | 同上 |
| **S3** | 写作风格：句式问题 | 同上 |
| **S4** | 写作风格：格式不一致 | 同上 |
| **S5** | 写作风格：冗余表达 | 同上 |
| **S6** | 写作风格：逻辑衔接 | 同上 |
| **S7** | 写作风格：可读性 | 同上 |

---

## 三、程序化审计对照

程序化审计（第一层）在 Dayu-Agent 中通过 `audit_rules.py` 实现，以下逐项对照：

| 检查项 | Dayu-Agent 实现 | 基金分析策略 | 复用程度 |
|--------|----------------|-------------|---------|
| 骨架结构匹配 | `_matches_skeleton_structure()` — 比对章节标题列表与预期骨架 | 直接复用，骨架定义替换为基金分析 8 章模板 | **直接复用** |
| 内容长度检查 | 检查章节字数是否低于配置阈值 | 直接复用，阈值按基金分析章节调整 | **直接复用** |
| 证据区存在检查 | 检查章节是否包含证据引用标记 | 适配复用，标记格式从通用格式适配为 `> 📎 证据：年报§[章节] [内容描述]` | **适配复用** |
| 数值计算校验（L1） | 无对应实现 | 全新设计：解析 R=A+B-C 各分量，校验数值一致性 | **全新设计** |
| 数值计算校验（L2） | 无对应实现 | 全新设计：解析百分位数值，校验排名计算正确性 | **全新设计** |
| 检查清单规则校验（R1） | 无对应实现 | 全新设计：解析 CHAPTER_CONTRACT 的 must_answer/must_not_cover，逐条校验 | **全新设计** |
| 判定评分一致性（R2） | 无对应实现 | 全新设计：提取最终判定与各维度评分，校验逻辑一致性 | **全新设计** |

### L1/L2 数值校验设计要点

```
L1 校验流程：
1. 从章节 markdown 中提取 Alpha、Beta、Cost 数值
2. 计算 Alpha + Beta - Cost
3. 与文中给出的投资者收益数值比对
4. 不一致则触发 L1 违规

L2 校验流程：
1. 从章节 markdown 中提取百分位数值（如"排名前 15%"）
2. 校验百分位计算是否与原始排名数据一致
3. 不一致则触发 L2 违规
```

### R1/R2 规则校验设计要点

```
R1 校验流程：
1. 加载当前章节的 CHAPTER_CONTRACT 定义
2. 提取 must_answer 列表
3. 逐条检查章节内容是否覆盖每个 must_answer 项
4. 提取 must_not_cover 列表
5. 逐条检查章节内容是否包含 must_not_cover 项
6. 违反任一条则触发 R1 违规

R2 校验流程：
1. 提取章节中的最终判定（值得持有/需要关注/建议替换）
2. 提取各维度评分/分析结论
3. 校验判定与评分之间是否存在逻辑矛盾
4. 矛盾则触发 R2 违规
```

---

## 四、LLM 审计对照

LLM 审计（第二层）通过 `audit` scene 和 `audit_facts_tone_json` task 实现。

### 4.1 Scene/Task 定义

| 组件 | Dayu-Agent | 基金分析策略 |
|------|-----------|-------------|
| Scene 定义 | `scenes/audit.md` — 定义审计场景的 system_prompt | 适配重写：替换为基金分析审计场景描述 |
| Task 定义 | `tasks/audit_facts_tone_json.md` — 定义 LLM 审计的具体指令 | 适配重写：替换为基金分析规则码、判定标准 |
| Task 契约 | `tasks/audit_facts_tone_json.contract.yaml` — 定义输入输出 schema | 结构复用，字段适配 |

### 4.2 输入结构

LLM 审计的输入参数在两个项目中结构一致：

| 参数 | Dayu-Agent 用途 | 基金分析用途 | 复用 |
|------|----------------|-------------|------|
| `chapter_markdown` | 待审计的章节内容 | 待审计的基金分析章节内容 | 直接复用 |
| `skeleton` | 章节骨架结构定义 | 基金分析 8 章骨架定义 | 直接复用 |
| `chapter_contract` | 章节契约（must_answer/must_not_cover） | CHAPTER_CONTRACT 定义 | 直接复用 |
| `item_rules` | 条目级规则 | 基金分析条目规则 | 直接复用 |
| `audit_scope_rules` | 审计范围规则（启用哪些规则码） | 基金分析审计范围规则 | 直接复用 |

### 4.3 输出结构

LLM 审计输出为结构化 JSON，两个项目格式一致：

```json
{
  "pass": true/false,
  "class": "E1|E2|E3|C1|L1|L2|R1|R2|...",
  "violations": [
    {
      "rule_code": "E1",
      "claim": "原文声明内容",
      "reason": "违规原因说明",
      "location": "段落/行号定位",
      "severity": "error|warning"
    }
  ],
  "notes": ["审计备注信息"]
}
```

### 4.4 Pass/Fail 判定优先级链

| 优先级 | Dayu-Agent | 基金分析 |
|--------|-----------|---------|
| 1（最高） | E 类（证据类） | E 类（证据类） |
| 2 | C 类（内容类） | C 类（内容类） |
| 3 | S 类（风格类） | L 类（逻辑/计算类） |
| 4（最低） | — | R 类（规则/判定类） |

> 基金分析将 S 类替换为 L+R 类，因为基金分析的核心风险是计算错误和规则违反，而非写作风格。

### 4.5 审计模式

| 模式 | Dayu-Agent | 基金分析 | 复用 |
|------|-----------|---------|------|
| 初始整章审计 | 对新生成的章节执行全量审计 | 对新分析的基金章节执行全量审计 | 直接复用 |
| 修复后局部复审 | 对修复后的段落执行定向审计 | 对修复后的基金分析段落执行定向审计 | 直接复用 |

---

## 五、证据复核对照

证据复核（第三层）通过 `confirm` scene 和 `confirm_evidence_violations` task 实现。

### 5.1 复核范围

| 项目 | Dayu-Agent | 基金分析 |
|------|-----------|---------|
| 触发条件 | 仅 E1/E2 类违规进入复核 | 仅 E1/E2 类违规进入复核 |
| 复核目的 | 确认违规是否为真正的证据缺失 | 确认基金分析中的证据引用是否可溯源 |

### 5.2 确认状态

复核结果的状态枚举在两个项目中完全一致：

| 状态码 | 含义 | 基金分析场景示例 |
|--------|------|----------------|
| `supported` | 证据充分，违规不成立 | 年报中有明确数据支撑该声明 |
| `supported_but_anchor_too_coarse` | 证据存在但锚点不够精确 | 有引用但未标注到具体表格行号 |
| `supported_elsewhere` | 证据在其他章节中存在 | 该数据在其他章节已引用，本章节可补充交叉引用 |
| `confirmed_missing` | 确认证据缺失，违规成立 | 年报中确实无对应数据，需删除或修正该声明 |

### 5.3 工具使用

| 项目 | Dayu-Agent | 基金分析 |
|------|-----------|---------|
| 复核工具 | 通用文档检索工具 | 基金文档工具（年报检索、章节定位、表格提取） |
| 工具调用方式 | LLM 在 confirm scene 中按需调用 | LLM 在基金 confirm scene 中按需调用基金文档工具 |
| 锚点格式 | 通用引用格式 | `年报{年份}§{章节}表{编号}行{行号}` |

---

## 六、修复机制对照

修复机制通过 `repair` scene 和 `repair_chapter` task 实现。

### 6.1 修复策略

| 策略 | Dayu-Agent 含义 | 基金分析适用性 |
|------|----------------|---------------|
| `patch` | 局部修复：仅修改违规段落 | 直接复用 |
| `regenerate` | 整章重生成 | 直接复用（当违规过多时使用） |
| `none` | 不修复（标记为已知问题） | 直接复用 |

### 6.2 修复合同（RepairContract）

修复合同的数据结构在两个项目中一致：

```yaml
repair_contract:
  chapter_id: "chapter_2"           # 章节标识
  violations_to_fix:                # 待修复违规列表
    - rule_code: "E1"
      violation_id: "v_001"
      strategy: "patch"
      disposition: "rewrite_with_existing_evidence"
  audit_scope_rules: [...]          # 复审范围
```

### 6.3 Patch 粒度

| 粒度 | 含义 | 基金分析适用性 |
|------|------|---------------|
| `substring` | 替换段落中的子串 | 适用于修正具体数值错误 |
| `line` | 替换整行 | 适用于修正单行声明 |
| `bullet` | 替换列表项 | 适用于修正要点列表中的某一项 |
| `paragraph` | 替换整段 | 适用于修正整个分析段落 |

### 6.4 处置模式

| 模式 | Dayu-Agent 含义 | 基金分析场景示例 |
|------|----------------|----------------|
| `delete_claim` | 删除无证据支撑的声明 | 删除无法从年报中验证的判断 |
| `rewrite_with_existing_evidence` | 用已有证据重写声明 | 用年报实际数据重写分析结论 |
| `anchor_fix_only` | 仅修正证据锚点格式 | 将粗略引用修正为精确的年报锚点格式 |

### 6.5 锚点格式适配

Dayu-Agent 使用通用引用格式，基金分析需适配为年报锚点格式：

```
Dayu-Agent 通用格式：
> 来源：[文档名] 第X章

基金分析锚点格式（正文引用）：
> 📎 证据：年报§[章节] [内容描述]

基金分析锚点格式（附录汇总）：
年报[年份]§[章节]表[编号]行[行号]
```

---

## 七、量化估算

基于上述逐项对照，对基金分析项目审计机制的实现工作量进行量化估算：

| 类别 | 占比 | 具体内容 |
|------|------|---------|
| **直接复用** | ~45% | 三层架构设计、P1/P2/E1/E2/E3/C1 规则码定义、骨架匹配算法、长度检查、证据复核状态枚举、修复策略/粒度/处置模式、输入输出 JSON 结构、Scene 生命周期管理 |
| **适配重写** | ~35% | FundAuditCoordinator 编排器、audit/confirm/repair 三个 scene 的 prompt 内容、审计 task 的判定指令、锚点格式转换、基金文档工具调用适配、契约 YAML 字段定义 |
| **全新设计** | ~20% | L1（R=A+B-C 数值校验）、L2（百分位校验）、R1（CHAPTER_CONTRACT 规则校验）、R2（判定评分一致性校验）的程序化审计逻辑，以及对应的 LLM 审计 prompt 片段 |

---

## 八、实施建议

### MVP 阶段（P0-P1）

**目标**：建立程序化审计能力，覆盖最关键的规则码。

| 优先级 | 规则码 | 实现内容 | 依赖 |
|--------|--------|---------|------|
| P0 | P1 | 骨架结构匹配 | 无 |
| P0 | P2 | 内容长度检查 | 无 |
| P0 | R1 | CHAPTER_CONTRACT 规则校验 | CHAPTER_CONTRACT 机制 |
| P1 | L1 | R=A+B-C 数值校验 | 数值提取逻辑 |
| P1 | R2 | 判定评分一致性校验 | 评分提取逻辑 |

**交付物**：
- `FundAuditCoordinator` 编排器骨架
- P1/P2/R1/L1/R2 程序化审计规则
- 审计结果数据模型（`AuditResult`, `Violation`）
- 单元测试（覆盖率 >= 80%）

### v2 阶段（P2-P3）

**目标**：引入 LLM 审计和证据复核，形成完整闭环。

| 优先级 | 内容 | 依赖 |
|--------|------|------|
| P2 | LLM 审计 scene/task（E1/E2/E3） | MVP 程序化审计 |
| P2 | 证据复核 scene/task（confirm） | LLM 审计 |
| P2 | 修复 scene/task（repair） | 证据复核 |
| P2 | C1 程序化审计 | CHAPTER_CONTRACT must_not_cover |
| P3 | P3（证据小节检查） | 证据格式规范 |
| P3 | C2（细粒度章节越界） | C1 实现 |
| P3 | L2（百分位校验） | L1 实现经验 |

**交付物**：
- audit/confirm/repair 三个完整 scene
- 对应的 task prompt 和契约 YAML
- 证据复核工具适配（基金文档工具）
- 锚点格式转换逻辑
- 端到端集成测试

---

## 九、Dayu-Agent 审计代码路径索引

以下列出 Dayu-Agent 仓库中与审计机制相关的所有文件路径及其职责，供基金分析项目实现时参考：

### Prompt 定义

| 文件路径 | 职责 |
|---------|------|
| `dayu/config/prompts/scenes/audit.md` | 审计场景 system_prompt，定义 LLM 审计的行为规范和判定标准 |
| `dayu/config/prompts/scenes/confirm.md` | 证据复核场景 system_prompt，定义证据确认的行为规范 |
| `dayu/config/prompts/scenes/repair.md` | 局部修复场景 system_prompt，定义修复策略和执行规范 |
| `dayu/config/prompts/tasks/audit_facts_tone_json.md` | LLM 审计 task prompt，包含具体的审计指令和输出格式要求 |
| `dayu/config/prompts/tasks/audit_facts_tone_json.contract.yaml` | 审计 task 输入契约，定义 chapter_markdown、skeleton、chapter_contract 等输入 schema |
| `dayu/config/prompts/tasks/confirm_evidence_violations.md` | 证据复核 task prompt，包含复核指令和确认状态定义 |
| `dayu/config/prompts/tasks/confirm_evidence_violations.contract.yaml` | 证据复核 task 输入契约，定义违规列表、可用工具等输入 schema |
| `dayu/config/prompts/tasks/repair_chapter.md` | 局部修复 task prompt，包含修复指令和锚点格式要求 |
| `dayu/config/prompts/tasks/repair_chapter.contract.yaml` | 修复 task 输入契约，定义修复合同、违规列表、原文内容等输入 schema |

### Service 层

| 文件路径 | 职责 |
|---------|------|
| `dayu/services/write_service.py` | Service 层入口，编排写作流程，调用 ChapterAuditCoordinator |

### Pipeline 内部模块

| 文件路径 | 职责 |
|---------|------|
| `dayu/services/internal/write_pipeline/chapter_audit_coordinator.py` | 审计协调器，管理 audit → confirm → repair 的完整生命周期，决定每轮审计的策略和范围 |
| `dayu/services/internal/write_pipeline/audit_rules.py` | 程序化审计规则实现，包含骨架匹配、长度检查等规则函数 |
| `dayu/services/internal/write_pipeline/audit_formatting.py` | 审计结果格式化，将违规列表格式化为可读的审计报告 |
| `dayu/services/internal/write_pipeline/audit_evidence_rewriter.py` | 证据重写逻辑，处理锚点修正和证据格式标准化 |
| `dayu/services/internal/write_pipeline/repair_executor.py` | 修复执行器，根据 RepairContract 执行 patch/regenerate/none 策略 |
| `dayu/services/internal/write_pipeline/models.py` | 数据模型定义，包含 AuditResult、Violation、RepairContract 等 |
| `dayu/services/internal/write_pipeline/enums.py` | 枚举定义，包含规则码（RuleCode）、确认状态（ConfirmStatus）、修复策略（RepairStrategy）等 |
