# P4 Implementation Control Plan Review — AgentGLM

> **日期**: 2026-05-19
> **审核者**: AgentGLM (独立 plan reviewer)
> **审核对象**: `docs/implementation-control-p4.md`
> **审核基准**: `docs/post-mvp-p4-first-principles-plan.md`、`docs/reviews/p4-audit-input-controller-judgment-20260519-0144.md`、`docs/design.md`、`docs/implementation-control.md`、`docs/code_20260519.csv`、仓库实际代码
> **角色**: 只读审查，不改文件，不 commit，不 push。

---

## Verdict

P4 实施控制文档整体设计合理，北极星清晰，切片顺序正确，P4-S1 scope 适当小。可以进入 P4-S1 implementation，但需先完成 2 个 required fixes（snapshot 生成与现有 Capability 的衔接定义、AGENTS 模块边界显式约束）。这两个修复都是文档补充，不涉及 scope 变更。

---

## Findings

### Blocking

**B1. Snapshot 生成与现有 `FundDataExtractor` / `StructuredFundDataBundle` 的衔接未定义**

P4-S1 §4.2 说"对指定基金生成 extraction snapshot"，但未说明 snapshot 生成代码与现有 `FundDataExtractor.extract(...)` 的关系。当前 extractor 返回 `StructuredFundDataBundle`（façade），snapshot 需要逐字段记录提取状态。实现者需要在以下两条路径中选择：

- **路径 A**：调用 `FundDataExtractor.extract(...)` 后拆解 bundle 为逐字段 snapshot 记录。优点：保持 façade 稳定；缺点：bundle 可能丢失部分字段级状态（如部分 `missing` 子字段被整体掩盖）。
- **路径 B**：绕过 façade，直接调用各子 extractor（`extract_profile`、`extract_performance`、`extract_manager_ownership`、`extract_holdings_share_change`）并记录逐字段结果。优点：字段级粒度完整；缺点：snapshot 生成器需要了解各子 extractor 的内部字段结构。

建议：在 §4 增加"实现约束"小节，明确选择哪条路径。倾向路径 B，因为 P4-S1 的核心价值就是"看清楚质量"，需要字段级粒度。

---

**B2. AGENTS 模块边界未作为 P4-S1 实现约束显式写出**

§9 提到"遵循 phaseflow / gateflow 多 Agent 约定"，但 §4 中没有列出实现约束。根据审查重点第 6 条，以下边界应显式声明：

- **文档仓库访问**：snapshot 生成应通过 `FundDocumentRepository` 获取 `ParsedAnnualReport`，不直接访问 `fund/pdf/*`。已验证：Service/UI 层当前不直接 import `fund/pdf/*`（grep 确认零结果）。
- **Capability/Service/UI 分层**：snapshot 生成能力应放在 Capability 层（`fund_agent/fund/`），CLI 或 Service 通过标准接口调用。不应实现为独立 `scripts/` 脚本（与 GLM audit input review 建议一致）。
- **禁止直接文件系统读基金文档**：已由 `FundDocumentRepository` 契约保证。
- **参数显式传递**：snapshot 生成器应接收 `fund_code`、`report_year`、`source_csv` 等显式参数，不依赖 cwd 或全局配置。

建议：在 §4 增加一节"实现约束"，列出上述边界要求。

---

### Reviewable

**R1. 004393 基金类型误判 root cause 描述不完整**

§1 和 §6 说 root cause 为"业绩基准中的指数词误当成指数基金特征"。代码级核验 `fund_type.py` 显示至少有三个 contributing factor：

1. `_INDEX_NAME_KEYWORDS` 包含"价值"（第 34 行），会匹配 `004393` 的基金名称"安信企业**价值**优选混合A"。
2. 分类逻辑第 278 行 `name_and_benchmark = f"{fund_name} {benchmark}"` 将基金名称和基准拼接后共同检测，任一命中 `_INDEX_NAME_KEYWORDS` 即进入指数分类路径。
3. 如果 `fund_category` 提取成功且为"混合型"，第 269 行应优先返回 `active_fund`。但 004393 年报 §2 表格格式可能与当前 3 只工程样本不同，导致 `fund_category` 提取失败，分类器跳过主动权益检查直接进入指数路径。

这不是 P4-S1 blocking issue（P4-S1 不修分类器），但建议在 §6（P4-S3）中更新 root cause 描述为更精确的代码级分析，以便 P4-S3 修复时不遗漏"价值"关键词问题。

---

**R2. Snapshot schema 混合了 run-level 和 field-level 粒度**

当前 19 个 schema 字段中：

- Run-level：`run_id`、`extraction_timestamp`、`source_csv`
- Fund-level：`fund_code`、`fund_name`、`app_category`、`report_year`、`classified_fund_type`、`classification_basis`
- Field-level：`field_name`、`field_group`、`extraction_mode`、`value_present`、`anchor_present`、`section_id`、`page`、`table_id`、`row_id`、`note`

JSONL 每行自包含所有粒度是合理的（便于逐行处理），但 `summary.md` 的统计维度应区分 run-level（总记录数、成功/失败基金数）和 field-level（每个字段的 coverage / traceability），避免重复计算。建议在 §4.5 后加一句粒度约定。

---

**R3. "按类别各抽 1 只"的抽样策略需更精确**

§4.6 验收条件说"能按类别各抽 1 只生成 snapshot"。CSV 的类别分布：

| 类别 | 条目数 | 唯一代码数 |
|------|--------|-----------|
| 国内股票类 | 26 | 25（016492 重复） |
| 国内债券类 | 14 | 14 |
| 海外股票类 | 11 | 11 |
| 海外债券/稳健类 | 3 | 3 |
| 黄金类 | 1 | 1 |
| 货币基金类 | 1 | 1 |

两个需明确的点：

1. 货币基金类是否纳入 P4-S1 抽样？§5.4 说"由用户裁决"，但 §4.6 的"按类别各抽 1 只"暗示纳入。如果纳入，则当前只有 001821（兴全天添益货币B），且该基金与 8 章模板适配度较低。
2. 国内股票类 25 只中抽 1 只的策略（随机？人工选？排除 016492？）。建议至少明确 016492 在抽样中的处理。

---

### Info

**I1. 016492 重复两条记录均在"国内股票类"**

CSV 第 26 行"南方均衡成长混合A"和第 35 行"易方达逆向投资混合A"共享代码 016492，两条均在"国内股票类"。不影响按类别分层的抽样逻辑，但 summary.md 的"重复代码列表"应显示两条记录的完整信息（名称+类别），便于用户核对。

---

**I2. `fund_type.py` 的 `_INDEX_NAME_KEYWORDS` 包含多个宽泛关键词**

"中证"、"上证"、"红利"、"低波"、"价值"、"质量"等关键词不仅匹配指数基金，也常见于主动基金名称或业绩基准。例如任何以"中证"为基准的主动基金都可能被误判。这是 P4-S3 的修复范围，记录在此以便修复时不遗漏。

---

**I3. 现有 `scripts/selected_funds_smoke.py` 可复用**

该脚本已支持 CSV 校验、分层抽样和指定代码运行，并输出 `results.jsonl` 和 `summary.md`。P4-S1 的 snapshot 生成能力可以扩展此脚本或与其并行，避免重复实现 CSV 读取和抽样逻辑。但 snapshot 生成核心能力应在 Capability 层（见 B2），脚本仅作为 CLI 入口。

---

**I4. GLM/MiMo audit input reviews 的采纳口径与 control doc 高度一致**

两份独立 review 对 P4 slicing、snapshot 离线设计、016492 处理口径的裁决一致。唯一分歧在 `extraction_timestamp`/`extractor_version` 是否纳入 P4-S1：control doc 采纳了"纳入"，MiMo 建议"延后"。control doc 的选择更合理——这两个字段的实现成本极低（一个 UUID 和一个 datetime），但对跨 run 可追溯性的价值很高。

---

## Accepted Strengths

1. **北极星清晰且从第一性原理成立**："先质量闭环，再扩功能"的优先级在当前 004393 failure case 下完全成立。三个底层问题（提取可度量、类型可靠、审计可阻断）覆盖了 MVP 最关键的质量缺口。

2. **P4-S1 scope 足够小且边界清楚**：非目标列表（§4.3）的 7 条明确排除了最常见的 scope creep 风险——不修 extractor、不建 golden answer、不接温度计、不引入 LLM 审计、不接 CI、不做全量通过。P4-R3（直接修 004393 跳过质量基线）的风险等级和缓解措施都很到位。

3. **016492 处理口径务实**：允许重复但标红、不阻塞 snapshot 运行、要求用户后续核对 App 源数据。在信息不完整时做了正确的策略选择。

4. **004393 known failure 处理正确**：要求 snapshot 记录当前误分类结果，不静默覆盖。确保了 P4-S3 修复前后的基线可比较。

5. **切片顺序和依赖关系正确**：snapshot → score → fix → gate 的顺序与第一性原理对齐。每个 slice 的验收信号都是可执行、可自动化验证的。

6. **独立文档策略正确**：从主 `implementation-control.md` 分离出 P4 控制文档，避免 1275 行主文档继续膨胀。

---

## Required Fixes

| # | Finding | 行动 | 预计耗时 |
|---|---------|------|---------|
| 1 | B1: Snapshot 与 FundDataExtractor 衔接未定义 | 在 §4 增加"实现约束"小节，明确 snapshot 生成路径 | 10 min |
| 2 | B2: AGENTS 模块边界未显式约束 | 在 §4 增加"实现约束"小节，列出文档仓库访问、分层和参数传递要求 | 5 min |

---

## Deferred Suggestions

| # | Suggestion | 延后到 |
|---|-----------|--------|
| 1 | R1: 细化 004393 root cause 为代码级三因素分析 | P4-S3 definition 时更新 §6 |
| 2 | R2: Snapshot schema 粒度约定写入文档 | P4-S2 implementation 时自然明确 |
| 3 | R3: 抽样策略精确化（货币基金、016492 处理） | P4-S1 implementation 时由 implementer 决定 |
| 4 | I2: `_INDEX_NAME_KEYWORDS` 宽泛关键词清理 | P4-S3 修复范围 |
| 5 | I3: 复用 smoke 脚本作为 CLI 入口 | P4-S1 implementation 时评估 |

---

## Final Recommendation

**P4 实施控制文档可通过 plan review 并进入 P4-S1 implementation，前提是先完成 2 个 required fixes（B1、B2）。**

两个 required fixes 都是 §4 的文档补充，不涉及代码变更或 scope 调整，预计 15 分钟可完成。修复后 P4-S1 可直接进入 implementation。

P4 北极星、切片顺序、scope 控制和风险追踪已经足够成熟，无需等待 MiMo review 后再决定是否进入 implementation。MiMo review 的 findings 可以在 implementation 期间并行纳入 controller judgment。

---

> 审核完成时间：2026-05-19
> 审核者：AgentGLM
> Artifact 路径：`docs/reviews/p4-control-plan-review-glm-20260519.md`
