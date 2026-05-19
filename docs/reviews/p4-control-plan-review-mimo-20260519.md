# P4 实施控制文档 Plan Review — AgentMiMo

> **日期**: 2026-05-19
> **审核对象**: `docs/implementation-control-p4.md` (v0.1)
> **审核基准**: `docs/post-mvp-p4-first-principles-plan.md`、`docs/reviews/p4-audit-input-controller-judgment-20260519-0144.md`、`docs/design.md`、`docs/implementation-control.md`、`docs/code_20260519.csv`、README.md、tests/README.md
> **角色**: AgentMiMo 独立 plan reviewer。只读审查，不改文件。

---

## 1. Verdict

**P4 实施控制文档方向正确、切片合理，可作为 P4 实施基线。P4-S1 scope 清楚、非目标明确、不过度设计。但 snapshot schema 存在 2 个 blocking gap（field_group 映射缺失、field_name 未枚举），需在 P4-S1 implementation 前补齐或明确推迟策略。**

核心判断：P4 北极星从第一性原理成立——先质量闭环，再扩功能。切片顺序 S1→S2→S3→S4 符合"先度量、再评分、再修复、再阻断"的依赖链。P4-S1 scope 足够小，不偷跑修 extractor 或报告审计。

---

## 2. Findings

### 2.1 Blocking (B)

#### B1. Snapshot schema 缺少 field_group → field_name 映射

**位置**: §4.4 Snapshot Schema

**问题**: schema 定义了 `field_group`（取值如 profile/performance/manager/holdings/share_change）和 `field_name`，但未定义每个 group 包含哪些 field_name。当前 P1 extractor 输出的字段名（如 `basic_identity`、`product_profile`、`benchmark`、`fee_schedule`、`nav_benchmark_performance`、`investor_return`、`manager_strategy_text`、`turnover_rate`、`holdings_snapshot`、`share_change` 等）与 `field_group` 的对应关系未明确。

**影响**: 实现者无法确定每条 snapshot 记录的 `field_name` 和 `field_group` 应填什么。不同实现者可能产生不一致的 snapshot，导致 P4-S2 评分规则无法对齐。

**建议修复**: 在 §4.4 或附录中增加 field_group → field_name 映射表。可直接从现有 extractor 输出推导：

| field_group | field_name 列表 |
|---|---|
| profile | basic_identity, product_profile, benchmark, fee_schedule |
| performance | nav_benchmark_performance, investor_return |
| manager | manager_strategy_text, turnover_rate, manager_alignment |
| holdings | holdings_snapshot |
| share_change | share_change |
| holder | holder_structure |

#### B2. field_name 未定义枚举或来源

**位置**: §4.4 Snapshot Schema

**问题**: `field_name` 字段没有说明其值从哪里来。P4-S2 §5.2 定义了 P0/P1/P2 字段等级，使用的是自然语言名称（如"基金名称"、"净值增长率"、"换手率"），而 extractor 输出使用的是 snake_case 标识符（如 `basic_identity`、`nav_benchmark_performance`、`turnover_rate`）。snapshot 的 `field_name` 应使用哪套命名？

**影响**: 与 B1 同源。如果 snapshot 用 extractor 标识符，P4-S2 评分规则需要建立自然语言→标识符映射；如果 snapshot 用自然语言名称，需要从 extractor 输出反向映射。无论哪种，都需要显式决策。

**建议修复**: 明确 `field_name` 使用 extractor 输出的 snake_case 标识符（与代码一致），并在 P4-S2 中将 P0/P1/P2 自然语言名称映射到这些标识符。这样 snapshot 和代码同源，评分规则的映射在 P4-S2 再做。

### 2.2 Reviewable (R)

#### R1. report_year 策略未明确

**位置**: §4.2 范围、§4.4 Snapshot Schema

**问题**: snapshot 包含 `report_year` 字段，但未说明：
- 是作为参数传入（如当前 CLI 的 `--report-year 2024`）？
- 还是 snapshot generator 自动确定（如取最新年报）？
- 如果多只基金年报年份不同，是统一取一个年份还是各自取最新？

**影响**: 当前 CLI 默认 `--report-year 2024`。如果 snapshot generator 也默认 2024，对于尚未发布 2024 年报的基金可能取不到数据。如果自动取最新，需要额外逻辑。

**建议**: P4-S1 先采用与 CLI 一致的策略：默认 2024，支持参数覆盖。在 summary.md 中记录每只基金实际使用的 report_year。

#### R2. summary.md 的"coverage / traceability 粗略统计"定义不清

**位置**: §4.6 验收条件

**问题**: 验收条件要求 `summary.md` 显示"每个字段的 coverage / traceability 粗略统计"，但未定义：
- coverage = `value_present=true` 的记录数 / 总基金数？
- traceability = `anchor_present=true` 的记录数 / 总基金数？
- 统计粒度是 per-field 还是 per-field_group？

**建议**: P4-S1 先定义最小统计：
- per-fund: 总字段数、value_present 数、anchor_present 数
- per-field（跨所有基金）: coverage = 有值基金数 / 总基金数，traceability = 有锚点基金数 / 总基金数

#### R3. P4-S1 实现形式未指定

**位置**: §4.2 范围

**问题**: P4-S1 描述了"做什么"但未指定"以什么形式做"：
- 是 CLI 子命令（如 `fund-analysis snapshot --csv docs/code_20260519.csv`）？
- 是库函数（如 `fund_agent/fund/quality/snapshot.py`）？
- 是脚本（如 `scripts/extraction_snapshot.py`）？
- 是 pytest 测试？

**影响**: 不同实现形式影响可测试性、可复用性和与后续 P4-S2/S3/S4 的集成方式。

**建议**: 参考 GLM review 建议，优先实现为 Capability 层库函数（如 `fund_agent/fund/quality/snapshot.py`），CLI 通过 Service 层调用。这样 snapshot 生成能力可被测试、被 CLI 和后续 CI gate 复用。但这是一个 implementation detail，不阻塞 plan review 通过。

#### R4. P0/P1/P2 字段等级与 Phase 命名可能混淆

**位置**: §5.2 字段等级

**问题**: P4-S2 使用 P0/P1/P2 表示字段重要性等级（必须/关键/增强），而项目使用 P0/P1/P2/P3/P4 表示 Phase。在同一文档中两套 P-prefix 含义不同，可能造成阅读混淆。

**影响**: 低。文档内已通过"P0 必须字段"等上下文区分。但如果有新的协作者加入，可能需要解释。

**建议**: 可考虑改用 F0/F1/F2（Field priority）或 L0/L1/L2（Level）避免歧义。非阻塞。

#### R5. source_csv 字段未说明是绝对路径还是相对路径

**位置**: §4.4 Snapshot Schema

**问题**: `source_csv` 记录 CSV 路径，但未指定格式。不同运行环境（开发机、CI、容器）的绝对路径不同，会影响跨环境比较。

**建议**: 使用相对于 repo root 的相对路径（如 `docs/code_20260519.csv`）。

### 2.3 Info (I)

#### I1. 004393 snapshot 中的 classified_fund_type=index_fund 是否需要显式标记

**位置**: §4.6 验收条件

**说明**: 验收条件说"004393 的 classified_fund_type=index_fund 被记录为 known failure，而不是被静默覆盖"。当前 schema 的 `note` 字段可用于此目的（如 `note: "known_failure: index_fund misclassification"`）。实现时需确保 snapshot generator 不会因为 004393 是 known failure 就跳过或修改其分类结果。这一点在验收条件中已隐含覆盖，无需额外修改。

#### I2. errors.jsonl 的 schema 未定义

**位置**: §4.5 输出路径

**说明**: 输出路径包含 `errors.jsonl`，但未定义其 schema。建议至少包含：`fund_code`、`error_type`（如 network_error、parse_error、extraction_error）、`error_message`、`timestamp`。可在 P4-S1 实现时自然定义，不阻塞 plan review。

#### I3. 精选基金池 CSV 中的类别分布已可统计

**说明**: `docs/code_20260519.csv` 共 56 条记录，类别分布如下（从 CSV 直接统计）：
- 黄金类: 1
- 海外股票类: 9
- 海外债券/稳健类: 3
- 国内股票类: 18（含 016492 重复）
- 国内债券类: 15
- 货币基金类: 1

P4-S2 的 golden set 候选可从此分布推导。016492 对应"南方均衡成长混合A"和"易方达逆向投资混合A"两条记录，均属国内股票类。

---

## 3. Accepted Strengths

### S1. 北极星从第一性原理成立

P4 不继续扩功能，而是建立质量闭环。这与 controller judgment §1 和 first principles plan §1 完全一致。"先度量，再改进"是正确的工程优先级。

### S2. 切片顺序正确且依赖清晰

S1(看清楚) → S2(评分) → S3(修复) → S4(阻断) 形成严格的依赖链。每个 slice 的验收条件依赖前一个 slice 的产出。没有隐含并行或循环依赖。

### S3. P4-S1 scope 足够小且非目标明确

§4.3 的 6 条"不做"有效防止了 scope creep：不修 004393、不扩 extractor、不建 golden answer、不接温度计、不引 LLM 审计、不接 CI。这保证 P4-S1 可在合理工作量内完成。

### S4. 016492 重复处理口径明确

§2 和 §8 风险追踪 P4-R1 明确：P4-S1 允许重复但标红，不阻塞 snapshot；真实修正需用户核对 App 源数据。这避免了在数据源不确定时做出不可逆决策。

### S5. Snapshot schema 适度最小

schema 的 18 个字段覆盖了必要的追溯信息（run_id、timestamp、source_csv）和提取状态（extraction_mode、value_present、anchor_present），没有引入过早的评分字段（如 score、grade）或复杂的嵌套结构。符合 controller judgment A5 的"保留跨 run 可追溯性，避免过早架构化"。

### S6. 004393 known failure 处理合理

将 004393 纳入 golden set（§5.4）并在 snapshot 中记录其误判（§4.6），而不是立即修复。这保证了"先建立基线，再用基线驱动修复"的正确顺序，避免跳过 P4-S1/S2 直接修 bug。

### S7. 离线优先设计

§4.5 输出路径和 §8 风险追踪 P4-R5 体现了离线优先原则：snapshot 基于已缓存/已解析的产物，真实 network/PDF smoke 单独记录。这与 controller judgment A4 一致。

### S8. FQ 规则定义合理且 FQ6 正确延后

§7.2 的 FQ1-FQ5 覆盖了核心质量维度（类型冲突、字段缺失、锚点缺失、数据不足比例、lens 不匹配）。FQ6 跨 run diff 延后到 P4-S4 末尾或 P5，符合"需要至少两个稳定 run 之后才有意义"的判断。

---

## 4. Required Fixes

以下问题需在 P4-S1 implementation 前修复或显式决策：

| ID | 问题 | 建议修复 |
|---|---|---|
| B1 | field_group → field_name 映射缺失 | 在 §4.4 增加映射表，从现有 extractor 输出推导 |
| B2 | field_name 枚举/来源未定义 | 明确使用 extractor 输出的 snake_case 标识符 |

以下问题需在 P4-S1 implementation 时一并处理：

| ID | 问题 | 建议处理 |
|---|---|---|
| R1 | report_year 策略 | 默认 2024，支持参数覆盖 |
| R2 | summary.md 统计定义 | 明确 per-fund 和 per-field 统计口径 |
| R3 | 实现形式 | 建议 Capability 层库函数 + CLI 调用 |
| R5 | source_csv 路径格式 | 使用相对路径 |

---

## 5. Deferred Suggestions

| ID | 建议 | 延后理由 | 重新评估时机 |
|---|---|---|---|
| R4 | P0/P1/P2 字段等级改名避免混淆 | 当前通过上下文可区分 | 有新协作者加入时 |
| I2 | errors.jsonl schema 定义 | 实现时自然定义 | P4-S1 implementation |
| — | dayu-agent 依赖降级 optional | 不阻塞 P4-S1 | P4 cleanup 阶段 |
| — | Gate 阈值配置化 | 先硬编码验证链路 | 阈值频繁调整时 |
| — | CI gate 集成 | 先独立 CLI | P4-S4 完成后 |
| — | 大文件拆分 | 当前内聚性高 | 文件超 50KB 时 |
| — | FQ6 跨 run diff | 需要至少两个 run | P4-S4 末尾或 P5 |

---

## 6. Final Recommendation

**可进入 P4-S1 implementation，前提是 B1 和 B2 在 implementation 开始时一并解决。**

具体建议：

1. **立即修复 B1/B2**: 在 §4.4 增加 field_group → field_name 映射表（可从现有 extractor 代码直接推导），明确 `field_name` 使用 extractor 输出的 snake_case 标识符。这可在 10 分钟内完成。

2. **P4-S1 implementation 时处理 R1-R3/R5**: report_year 默认 2024、summary.md 统计口径、实现形式（库函数 + CLI）、相对路径。这些是 implementation detail，不需要阻塞 plan review。

3. **后续 slice 按计划推进**: P4-S2（评分 + golden set）→ P4-S3（修 004393 + extractor 缺口）→ P4-S4（FQ 规则 + 质量阻断）的依赖链清晰，无需调整。

4. **016492 重复**: 按已有口径处理——P4-S1 允许重复但标红，不阻塞。用户后续核对 App 源数据后修正。

5. **golden set 具体名单**: P4-S1 实施时从 CSV 按类别各选 1 只，004393 固定纳入。具体代码由 controller 或用户在 P4-S1 开始时确认。

---

> 审核人：AgentMiMo
> 审核完成时间：2026-05-19
> Artifact 路径：`docs/reviews/p4-control-plan-review-mimo-20260519.md`
