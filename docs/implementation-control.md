# 基金行为教练 Agent —— 实施总控文档

> **版本**: v1.0
> **日期**: 2026-05-16
> **设计真源**: `docs/design.md`
> **MVP 计划书**: `fund-agent-mvp-plan.md`
> **定性模板**: `fund-analysis-template-draft.md`

---

## 1. 总览

### 1.1 Phase 列表

| Phase | 名称 | 周期 | 状态 | 依赖 |
|-------|------|------|------|------|
| P0 | 环境搭建与架构骨架 | Week 1 | ✅ done | 无 |
| P1 | 数据层（PDF 下载 + 解析 + 提取） | Week 2-3 | ✅ done | P0 |
| P2 | 分析引擎（R=A+B-C + 检验 + 审计） | Week 3-4 | ✅ done | P1 |
| P3 | CLI 入口 + 整合测试 + 验证 | Week 4-5 | 🟡 in progress | P2 |

### 1.2 里程碑

| 里程碑 | 目标日期 | 关联 Phase | 验收标准 |
|--------|---------|-----------|---------|
| M1: 架构就绪 | Week 1 结束 | P0 | 四层骨架可运行，样本基金 PDF 可下载解析 |
| M2: 数据管道可用 | Week 3 中 | P1 | 12 项关键数据提取准确率 > 90% |
| M3: 分析引擎可用 | Week 4 中 | P2 | R=A+B-C 计算正确，言行一致性检验输出信号 |
| M4: MVP 交付 | Week 5 结束 | P3 | `fund-analysis <code>` 输出完整 8 章报告 |

### 1.3 当前 Gate 与基线裁决（2026-05-18）

- 当前分支：`feat/p3-cli-integration`
- 当前 gate：`P3-S8 implementation + review`
- 下一 gate：`P3-S8 implementation + review`
- 当前裁决：
  - P0 维持 `done`。已验证 `dayu` 依赖可导入、`fund-agent` 处于 editable install、`fund-analysis --help` 可用、样本基金 `110011` 年报可下载、`pdfplumber` 可提取全文文本和表格。
  - P1 已完成并通过 aggregate review。
  - P2 已完成并通过 aggregate deepreview。
  - P3 已进入 `in progress`。
  - `P3-S1 CLI 入口封装` 已完成，通过 Typer CLI 和 Service 层输出单只基金 8 章 Markdown 报告；下一 gate 为 `P3-S2 implementation + review`。
  - `P3-S2 温度计数据爬取` 已完成并通过 GLM/MiMo code review；当前实现范围仅限 Capability data adapter，不接入 CLI/Service。
  - `P3-S3 端到端整合测试` 已完成实现与 GLM/MiMo/controller code review：新增 3 只样本基金 CLI 端到端矩阵，闭合真实 `§2` 表格字段抽取、parsed report 低质量缓存门槛和模板 `benchmark_text` 契约错配。
  - `P3-S4 程序审计集成` 已完成实现与 controller code review：P3 CLI 端到端矩阵现在记录真实 Service 返回值，并断言 P1/P2/P3/L1/R1/R2 全部程序审计规则执行通过；下一 gate 为 `P3-S5 implementation + review`。
  - `P3-S5 证据锚点集成` 已完成实现与 controller code review：P3 CLI 端到端矩阵现在逐份报告断言 8 章正文证据行、附录年报章节/表格/行定位和无缺证占位；下一 gate 为 `P3-S6 implementation + review`。
  - `P3-S6 编写 README.md` 已完成实现与 controller code review：根 README 已按当前 CLI 成功路径更新为用户手册，并移除过期的端到端矩阵未实现表述；下一 gate 为 `P3-S7 implementation + review`。
  - `P3-S7 编写单元测试` 已完成实现与 controller code review：dev 依赖和测试手册新增覆盖率 gate，当前 `fund_agent` 总覆盖率 90.07%，超过 50% 目标；下一 gate 为 `P3-S8 implementation + review`。
  - `P2-S1` 至 `P2-S8` 已收口为 accepted baseline commit `a6b1516`。收口范围仅包含 P2 analysis/audit 实现、测试、README 同步与 review artifact；本地运行辅助文件 `launchd/`、`scripts/` 和旧 P1 review artifact 未纳入该基线。
  - `P1-S1 文档访问契约收口` 已完成：对外唯一仓库入口收口为 `FundDocumentRepository.load_annual_report(...) -> ParsedAnnualReport`，公共契约已迁入 `fund_agent/fund/documents/*`，`fund_agent/fund/pdf/*` 降为仓库内部 helper / adapter。
  - `P1-S2 章节定位修复与 §3 冻结` 已完成：
    - `§3` root cause 已直接关闭，不是基金代码特判
    - 章节规则已迁出到 `fund_agent/fund/pdf/section_catalog.py`
    - 目录过滤已从单一 `"..."` 升级为可复用规则表
    - `110011/2024` 的正文 `§3` 已由 fixture + test 稳定覆盖
  - `P1-S3 两级缓存与仓库内解析物化` 已完成：
    - raw PDF 元信息缓存与 parsed report 物化缓存均已落在 `documents` 层内部
    - repository 已优先命中缓存，避免重复下载 / 重复全文解析
    - `force_refresh=True` 已正确穿透 parsed report 与已记录的 PDF 路径
    - 本 slice 未创建 `structured_data` 表，也未冻结其 schema
  - `P1-S4 基础画像与基金类型识别` 已完成：
    - `fund_agent/fund/fund_type.py` 已承载稳定的基金类型识别输出 `classified_fund_type` / `classification_basis`
    - `fund_agent/fund/extractors/profile.py` 已落地 `basic_identity`、`product_profile`、`benchmark`、`fee_schedule`
    - 基金类型识别已显式先于通用字段构造执行，并由测试锁定
    - 费率、基准、规模、经理信息均已带 `EvidenceAnchor`
  - `P1-S5 §3 表现提取与投资者收益 fallback` 已完成：
    - `fund_agent/fund/extractors/performance.py` 已落地 `nav_benchmark_performance` 与 `investor_return`
    - `investor_return` 已稳定区分 `direct / estimated / missing`
    - `§3` 直接披露与估算披露命中均带 `EvidenceAnchor`
    - 未披露路径不再静默返回空字符串，而是显式标记 `missing`
    - `nav_benchmark_performance` 在部分命中时不再伪装成完整 `direct`
  - `P1-S6 管理人文本、换手率、利益一致性与持有人结构` 已完成：
    - `fund_agent/fund/extractors/manager_ownership.py` 已落地 `manager_strategy_text`、`turnover_rate`、`manager_alignment`、`holder_structure`
    - `§4/§8/§9` 命中字段均带 `EvidenceAnchor`
    - `manager_alignment` 仅输出原始披露，未引入利益一致性判断
    - 未披露路径显式标记 `missing`
  - `P1-S7 持仓快照与份额变动` 已完成：
    - `fund_agent/fund/extractors/holdings_share_change.py` 已落地 `holdings_snapshot` 与 `share_change`
    - 前十大重仓与份额变动可结构化输出
    - 行业分布未披露时显式标记 `missing`
    - 表格命中路径均带页码、表 ID 和行定位
  - `P1-S8 façade 集成、净值数据适配器与 P1 验收矩阵` 已完成：
    - `fund_agent/fund/data_extractor.py` 已落地 `FundDataExtractor` 与 `StructuredFundDataBundle`
    - `fund_agent/fund/data/nav_data.py` 已落地 `FundNavDataAdapter` 与 `nav_cache`
    - 3 只样本基金 12 项矩阵达到 `36/36`
    - P1 全量测试当前通过
  - `P2-S1 R=A+B-C 计算模块` 已完成：
    - `fund_agent/fund/analysis/r_abc.py` 已落地 `RabcInput`、`RabcAttribution`、`calculate_r_abc(...)`、`calculate_r_abc_series(...)` 与 `calculate_r_abc_from_bundle(...)`
    - 计算公式按 `docs/design.md` 第 4.1 节实现：`B=业绩比较基准收益率×股票仓位`，`A=R-B`，`C=管理费+托管费+换手率×0.3%`，`净超额=A-C`
    - 当前只消费 P1 `StructuredFundDataBundle`，不直接读取 PDF、文档仓库或文件系统
    - P1 尚未稳定抽取股票仓位，当前要求调用方显式传入 `equity_position`；缺失时返回 `missing`，不静默假设
    - 单元测试已覆盖手工公式闭合、P1 字段解析、证据锚点传递、关键字段缺失和子字段缺失
  - `P2-S2 超额收益性质判断` 已完成：
    - `fund_agent/fund/analysis/alpha_judge.py` 已落地 `AlphaObservation`、`AlphaJudgmentRule`、`AlphaJudgment`、`judge_alpha_nature(...)` 与 `observations_from_attributions(...)`
    - 默认规则按 MVP 规则引擎实现：多年度为正、牛熊环境都为正、来源可解释
    - 输出 `structural / partial_structural / cyclical / not_applicable / insufficient_data`
    - 市场环境与来源解释强度必须由调用方显式提供，模块不从收益结果中反推
    - 单元测试已覆盖结构性、部分结构性、阶段性、不适用、样本不足和缺少显式环境输入
  - `P2-S3 言行一致性检验` 已完成：
    - `fund_agent/fund/analysis/consistency_check.py` 已落地 `ConsistencyRule`、`ConsistencyDimensionResult`、`ConsistencyCheckResult` 与 `check_consistency(...)`
    - 已输出投资风格、行业偏好、仓位管理、换手水平 4 维度信号
    - 实际持仓风格和股票仓位必须由调用方显式传入，缺失时返回 `insufficient_data`
    - 行业偏好只在 §4 行业宣称和 §8 行业分布都存在时判断
    - `fund_agent/fund/analysis/_ratios.py` 已收口 P2 分析模块内重复比例解析逻辑
    - 单元测试已覆盖 4 维度一致、风格/行业不一致、缺少显式实际证据、高换手冲突和行业分布缺失
  - `P2-S4 投资者获得感分析` 已完成：
    - `fund_agent/fund/analysis/investor_return.py` 已落地 `BehaviorGapResult`、`FundFlowResult`、`InvestorExperienceResult`、`analyze_investor_experience(...)`、`calculate_behavior_gap(...)` 与 `judge_fund_flow(...)`
    - 行为损益按 `投资者实际收益率 - 基金产品收益率` 计算
    - 资金流向基于 §10 份额净变动和产品收益方向输出 `chasing_performance / bottom_fishing / outflow / normal / missing`
    - 投资者收益率缺失时返回 `missing`，不在分析层静默估算
    - 单元测试已覆盖行为损益、投资者收益缺失、追涨/抄底资金流向、获得感负向和份额字段缺失
  - `P2-S5 否决项检查` 已完成：
    - `fund_agent/fund/analysis/risk_check.py` 已落地 `RiskCheckRule`、`RiskCheckItem`、`RiskCheckResult` 与 `run_risk_checks(...)`
    - 已执行 5 项否决检查：清盘风险、基金经理任期、严重风格漂移、费率远超同类、指数基金跟踪误差
    - 基金经理任期、同类费率中位数和跟踪误差必须由调用方显式提供，缺失时返回 `insufficient_data`
    - 单元测试已覆盖安全路径、5 项否决触发和显式输入缺失路径
  - `P2-S6 压力测试` 已完成：
    - `fund_agent/fund/analysis/risk_check.py` 已落地 `StressTestRule`、`StressScenarioResult`、`StressTestResult` 与 `run_stress_test(...)`
    - 固定模拟 `-20% / -40% / -60%` 三个场景
    - 按基金类型应用模板第 6 章 `preferred_lens` 压力阈值
    - 最大可承受亏损比例必须显式提供；缺失时只输出浮亏，不猜测用户承受能力
    - 单元测试已覆盖主动基金、债券基金、缺少承受能力、非法输入和自定义阈值配置
    - controller code review 已通过；MiMo/GLM 外部 review 因 Claude hook/思考状态卡住未产出 artifact，不能作为独立 review 依据
  - `P2-S7 检查清单引擎` 已完成：
    - `fund_agent/fund/analysis/checklist.py` 已落地 `ChecklistRule`、`ChecklistItem`、`ChecklistResult` 与 `run_checklist(...)`
    - 已输出 7 问题 `green / yellow / red / gray` 与 `pass / watch / block / insufficient_data`
    - 检查清单消费 R=A+B-C、§9 利益一致性披露、投资者获得感、言行一致性、否决项检查、估值状态和用户资金期限
    - 估值和资金期限必须由调用方显式提供；缺失时输出灰灯，不默认通过
    - 单元测试已覆盖全绿、红灯阻断、灰灯缺失、黄灯跟踪、资金年限阈值配置、异常否决项输入和 7 问题顺序
    - controller code review 已通过
  - `P2-S8 程序审计` 已完成：
    - `fund_agent/fund/audit/audit_programmatic.py` 已落地 `ProgrammaticAuditInput`、`AuditIssue`、`ProgrammaticAuditResult` 与 `run_programmatic_audit(...)`
    - 已执行 P1/P2/P3/L1/R1/R2 程序审计
    - P1/P2/P3 消费报告 Markdown，L1/R1/R2 消费结构化 P2 结果和显式最终判断
    - 缺少报告、R=A+B-C 结构化结果、检查清单或最终判断时返回失败，不把未执行规则伪装成通过
    - 单元测试已覆盖必需输入缺失、章节缺失、内容过短、证据缺失、R=A+B-C 不闭合、检查清单规则错误和最终判断冲突
    - controller code review 已通过
  - `P2-S9 模板渲染器` 已完成：
    - `fund_agent/fund/template/renderer.py` 已落地 `TemplateRenderInput`、`TemplateRenderResult`、`render_template_report(...)` 与 `build_programmatic_audit_input(...)`
    - 渲染器固定输出 `docs/design.md` 第 3.1 节 0-7 共 8 章 Markdown，并附带 `证据与出处`
    - 渲染器只消费 P1/P2 结构化结果与显式输入，不读取年报、PDF、缓存、文档仓库、UI、Service、Runtime 或 Engine
    - `TemplateRenderResult.audit_input` 可直接传给 `run_programmatic_audit(...)`，携带报告 Markdown、R=A+B-C 结果、检查清单和最终判断
    - 缺失数据显式渲染为“未披露”或“数据不足”
    - 最终判断限制为 `worth_holding / needs_attention / suggest_replace`，报告不输出买入、卖出、收益预测或仓位比例
    - code review 接受并修复了 `dict_values(...)` 可见输出、重复句号和 README 过期条目问题
    - 验证命令 `.venv/bin/python -m pytest tests/fund/template tests/fund/audit -q` 当前通过（`18 passed`），`.venv/bin/python -m pytest tests/fund/analysis -q` 当前通过（`40 passed`）
  - `P2-S10 证据锚点标注` 已完成：
    - 正文证据行已按年报年份、章节和描述输出；非年报来源显式标注来源类型
    - 附录年报锚点按 `年报{年份}§{章节}表{编号}行{行号}` 输出
    - 表格、行定位、章节缺失时显式降级为 `未定位`，不静默丢失年份或章节
    - 页码作为附加位置元数据保留
    - 缺少章节证据时，正文和附录均显式输出数据不足
    - `ProgrammaticAuditInput` 兼容性保持不变
    - 验证命令 `.venv/bin/python -m pytest tests/fund/template tests/fund/audit -q` 当前通过（`23 passed`），`.venv/bin/python -m pytest tests/fund/analysis -q` 当前通过（`40 passed`）
- 下一 entry point：
  - 进入 `P2 aggregate deepreview`
  - 优先目标是对 P2-S1 至 P2-S10 的完整 P2 diff 做 aggregate review，确认分析、审计、模板和证据锚点组合后无跨 slice 回归
- 当前 artifact：
  - plan: `docs/reviews/p1-plan-2026-05-17.md`
  - plan review: `docs/reviews/p1-plan-review-2026-05-17.md`
  - `P1-S1`:
    - baseline reconciliation: `docs/reviews/p1-s1-baseline-reconciliation-2026-05-17.md`
    - implementation: `docs/reviews/p1-s1-implementation-2026-05-17.md`
    - code review:
      - `docs/reviews/p1-s1-code-review-mimo-2026-05-17.md`
      - `docs/reviews/p1-s1-code-review-glm-2026-05-17.md`
      - controller judgment: `docs/reviews/p1-s1-code-review-controller-judgment-2026-05-17.md`
    - fix: `docs/reviews/p1-s1-fix-2026-05-17.md`
    - re-review:
      - `docs/reviews/p1-s1-rereview-mimo-2026-05-17.md`
      - `docs/reviews/p1-s1-rereview-glm-2026-05-17.md`
      - controller confirmation: `docs/reviews/p1-s1-rereview-controller-2026-05-17.md`
    - accepted slice commit: `e772dae`
  - `P1-S2`:
    - baseline reconciliation: `docs/reviews/p1-s2-baseline-reconciliation-2026-05-17.md`
    - implementation: `docs/reviews/p1-s2-implementation-2026-05-17.md`
    - code review:
      - `docs/reviews/p1-s2-code-review-mimo-2026-05-17.md`
      - `docs/reviews/p1-s2-code-review-glm-2026-05-17.md`
      - controller judgment: `docs/reviews/p1-s2-code-review-controller-judgment-2026-05-17.md`
    - accepted slice commit: `c3bd264`
  - `P1-S3`:
    - baseline reconciliation: `docs/reviews/p1-s3-baseline-reconciliation-2026-05-17.md`
    - implementation: `docs/reviews/p1-s3-implementation-2026-05-17.md`
    - code review:
      - `docs/reviews/p1-s3-code-review-mimo-2026-05-17.md`
      - `docs/reviews/p1-s3-code-review-glm-2026-05-17.md`
      - controller judgment: `docs/reviews/p1-s3-code-review-controller-judgment-2026-05-17.md`
    - accepted slice commit: `d92eef7`
  - `P1-S4`:
    - baseline reconciliation: `docs/reviews/p1-s4-baseline-reconciliation-2026-05-17.md`
    - implementation: `docs/reviews/p1-s4-implementation-2026-05-17.md`
    - code review:
      - `docs/reviews/p1-s4-code-review-mimo-2026-05-17.md`
      - `docs/reviews/p1-s4-code-review-glm-2026-05-17.md`
      - `docs/reviews/p1-s4-code-review-controller-judgment-2026-05-17.md`
    - fix: `docs/reviews/p1-s4-fix-2026-05-17.md`
    - re-review:
      - `docs/reviews/p1-s4-rereview-glm-2026-05-17.md`
      - `docs/reviews/p1-s4-rereview-controller-2026-05-17.md`
    - accepted slice commit: `22a1a7a`
  - `P1-S5`:
    - baseline reconciliation: `docs/reviews/p1-s5-baseline-reconciliation-2026-05-17.md`
    - implementation: `docs/reviews/p1-s5-implementation-2026-05-17.md`
    - code review:
      - `docs/reviews/p1-s5-code-review-mimo-2026-05-17.md`
      - `docs/reviews/p1-s5-code-review-glm-2026-05-17.md`
      - `docs/reviews/p1-s5-code-review-controller-judgment-2026-05-17.md`
    - fix: `docs/reviews/p1-s5-fix-2026-05-17.md`
    - re-review:
      - `docs/reviews/p1-s5-rereview-controller-2026-05-17.md`
    - accepted slice commit: `8102944`
  - `P1-S6`:
    - baseline reconciliation: `docs/reviews/p1-s6-baseline-reconciliation-2026-05-17.md`
    - implementation: `docs/reviews/p1-s6-implementation-2026-05-17.md`
    - code review:
      - `docs/reviews/p1-s6-code-review-controller-judgment-2026-05-17.md`
    - accepted slice commit: `18566f9`
  - `P1-S7`:
    - baseline reconciliation: `docs/reviews/p1-s7-baseline-reconciliation-2026-05-17.md`
    - implementation: `docs/reviews/p1-s7-implementation-2026-05-17.md`
    - code review:
      - `docs/reviews/p1-s7-code-review-controller-judgment-2026-05-17.md`
    - accepted slice commit: `3167754`
  - `P1-S8`:
    - baseline reconciliation: `docs/reviews/p1-s8-baseline-reconciliation-2026-05-17.md`
    - implementation: `docs/reviews/p1-s8-implementation-2026-05-17.md`
    - code review:
      - `docs/reviews/p1-s8-code-review-controller-judgment-2026-05-17.md`
    - accepted slice commit: `d398bc2`
  - `P1 aggregate review`: `docs/reviews/p1-aggregate-review-2026-05-17.md`
  - `P2-S1`:
    - implementation: `docs/reviews/p2-s1-implementation-2026-05-17.md`
    - code review:
      - `docs/reviews/p2-s1-code-review-controller-judgment-2026-05-17.md`
  - `P2-S2`:
    - implementation: `docs/reviews/p2-s2-implementation-2026-05-17.md`
    - code review:
      - `docs/reviews/p2-s2-code-review-controller-judgment-2026-05-17.md`
  - `P2-S3`:
    - implementation: `docs/reviews/p2-s3-implementation-2026-05-17.md`
    - code review:
      - `docs/reviews/p2-s3-code-review-controller-judgment-2026-05-17.md`
  - `P2-S4`:
    - implementation: `docs/reviews/p2-s4-implementation-2026-05-17.md`
    - code review:
      - `docs/reviews/p2-s4-code-review-controller-judgment-2026-05-17.md`
  - `P2-S5`:
    - implementation: `docs/reviews/p2-s5-implementation-2026-05-17.md`
    - code review:
      - `docs/reviews/p2-s5-code-review-controller-judgment-2026-05-17.md`
  - `P2-S6`:
    - implementation: `docs/reviews/p2-s6-implementation-2026-05-17.md`
    - code review:
      - `docs/reviews/p2-s6-code-review-controller-judgment-2026-05-17.md`
  - `P2-S7`:
    - implementation: `docs/reviews/p2-s7-implementation-2026-05-17.md`
    - code review:
      - `docs/reviews/p2-s7-code-review-controller-judgment-2026-05-17.md`
  - `P2-S8`:
    - implementation: `docs/reviews/p2-s8-implementation-2026-05-17.md`
    - code review:
      - `docs/reviews/p2-s8-code-review-controller-judgment-2026-05-18.md`
  - P2 baseline risk review: `docs/reviews/code-review-20260518-0547.md`
  - P2-S1 至 P2-S8 accepted baseline commit: `a6b1516`
  - `P2-S9`:
    - implementation: `docs/reviews/p2-s9-implementation-2026-05-18.md`
    - code review:
      - `docs/reviews/p2-s9-code-review-mimo-2026-05-18.md`
      - `docs/reviews/p2-s9-code-review-glm-2026-05-18.md`
      - controller judgment: `docs/reviews/p2-s9-code-review-controller-judgment-2026-05-18.md`
    - fix: `docs/reviews/p2-s9-fix-2026-05-18.md`
    - re-review:
      - `docs/reviews/p2-s9-rereview-glm-2026-05-18.md`
    - accepted slice commit: `bf64b0f`
  - `P2-S10`:
    - implementation: `docs/reviews/p2-s10-implementation-2026-05-18.md`
    - code review:
      - `docs/reviews/p2-s10-code-review-mimo-2026-05-18.md`
      - `docs/reviews/p2-s10-code-review-glm-2026-05-18.md`
      - controller judgment: `docs/reviews/p2-s10-code-review-controller-judgment-2026-05-18.md`
    - accepted slice commit: `2d041ae`
  - `P2 aggregate deepreview`:
    - review:
      - `docs/reviews/p2-aggregate-review-mimo-2026-05-18.md`
      - `docs/reviews/p2-aggregate-review-glm-2026-05-18.md`
      - controller judgment: `docs/reviews/p2-aggregate-review-controller-judgment-2026-05-18.md`
    - fix: `docs/reviews/p2-aggregate-fix-2026-05-18.md`
    - accepted deepreview commit: `07fe0d0`
  - `Draft PR #1`:
    - URL: `https://github.com/bill20232033cc/fund-agent/pull/1`
    - base: `main` (`a6b1516`)
    - head: `chore/reconcile-baseline`
    - PR review:
      - `docs/reviews/pr-1-review-glm-2026-05-18.md`
      - controller judgment: `docs/reviews/pr-1-review-controller-judgment-2026-05-18.md`
    - PR fix: `docs/reviews/pr-1-fix-2026-05-18.md`
    - PR re-review: `docs/reviews/pr-1-rereview-glm-2026-05-18.md`
    - accepted PR review commit: `8f5029c`
  - `P3-S1`:
    - implementation: `docs/reviews/p3-s1-implementation-2026-05-18.md`
    - code review:
      - `docs/reviews/p3-s1-code-review-glm-2026-05-18.md`
      - controller judgment: `docs/reviews/p3-s1-code-review-controller-judgment-2026-05-18.md`
    - fix: `docs/reviews/p3-s1-fix-2026-05-18.md`
    - re-review:
      - `docs/reviews/p3-s1-rereview-glm-2026-05-18.md`
    - accepted slice commit: `c5a240c`

---

## 2. Phase 详细定义

### P0: 环境搭建与架构骨架

**目标**

完成开发环境搭建，建立四层架构骨架，验证数据提取可行性。

**进入条件**

- [x] 设计真源文档 `docs/design.md` 已冻结
- [x] 实施总控文档 `docs/implementation-control.md` 已创建
- [x] Python 3.11+ 可用

**退出条件**

- [x] `dayu-agent` 包可正常安装且 import 通过（`dayu.engine`、`dayu.host`、`dayu.config`）
- [x] 四层架构目录结构就位（ui/services/fund/config）
- [x] `pyproject.toml` 配置完成且 `pip install -e .` 无报错
- [x] 选定 3-5 只样本基金并记录分析基准
- [x] 能从巨潮资讯网下载至少 1 只样本基金的年报 PDF
- [x] 能用 pdfplumber 提取 PDF 文本和表格
- [x] `fund-analysis` CLI 命令可运行且输出帮助信息

**任务切片**

| Slice | 任务 | 验证方式 |
|-------|------|---------|
| P0-S1 | 安装 dayu-agent 依赖，验证 Engine/Host/Config 可用 | `python -c "from dayu.engine import AsyncAgent; from dayu.host import Host"` 通过 |
| P0-S2 | 创建项目骨架目录结构（ui/services/fund/config） | `ls fund_agent/` 输出符合 design.md |
| P0-S3 | 编写 `pyproject.toml`（含 dayu-agent 依赖 + pdfplumber 等） | `pip install -e .` 无报错 |
| P0-S4 | 选定样本基金（从有知有行严选基金池） | 记录基金代码和手动分析结果 |
| P0-S5 | 实现 `fund/pdf/downloader.py` 基础版 | 能下载巨潮网年报 PDF |
| P0-S6 | 实现 `fund/pdf/parser.py` 基础版 | 能读取 PDF 文本和表格 |
| P0-S7 | 编写 CLI 入口（`fund-analysis` 命令） | `fund-analysis --help` 输出帮助信息 |

**验证要求**

- P0-S4：下载 3 只不同类型基金的年报 PDF，确认均可获取
- P0-S5：对 1 只基金年报执行 pdfplumber 提取，确认能读取 §2/§3/§4/§8/§9/§10 的文本

**风险与追踪**

| 风险 | 概率 | 缓解措施 | 追踪状态 |
|------|------|---------|---------|
| 巨潮网反爬 | 低 | 改用东方财富 akshare API + pdf.dfcfw.com | ✅ 已缓解：改用 akshare + eastmoney PDF |
| pdfplumber 对中文 PDF 支持差 | 中 | 备选 PyPDF2 + pdfminer.six | ✅ 已验证：中文提取正常，70K 字文本可提取 |

**当前实现裁决（2026-05-17）**

- 已验证 `fund-agent==0.1.0` 以 editable install 方式安装在当前虚拟环境中，`fund-analysis --help` 可直接运行。
- 已验证样本基金基线存在：`docs/sample-funds.md` 已记录主动权益、指数、债券三类样本。
- 已验证样本年报下载与解析链路：`110011` 的 2024 年年报可下载，且可提取约 70K 字全文与 99 个表格。
- 当前未把 `pip install -e .` 的重放网络波动记为代码阻塞；下载 `dayu-agent` wheel 时可能受 GitHub 可达性影响。

---

### P1: 数据层（PDF 下载 + 解析 + 提取）

**目标**

完成 PDF 下载、解析和数据提取功能，能从基金年报中提取 12 项关键数据。

**进入条件**

- [x] P0 退出条件全部满足
- [x] 样本基金 PDF 已下载到本地

**退出条件**

- [ ] `fund/pdf/downloader.py` 能下载任意基金年报 PDF（输入基金代码）
- [ ] `fund/pdf/parser.py` 能解析 PDF 并提取文本和表格
- [ ] `fund/data_extractor.py` 能提取 12 项关键数据（准确率 > 90%）
- [ ] `fund/pdf/cache.py` 两级缓存（文件 + SQLite）可用
- [ ] 对 3 只样本基金的数据提取结果与人工核对一致

**任务切片**

| Slice | 任务 | 验证方式 |
|-------|------|---------|
| P1-S1 | 文档访问契约收口 | `FundDocumentRepository.load_annual_report(...)` 成为唯一公开入口 |
| P1-S2 | 章节定位修复与 `§3` 冻结 | `110011/2024` 年报稳定命中 `§3` 正文 |
| P1-S3 | 两级缓存与仓库内解析物化 | 重复加载同一年报不重复下载/不重复全文解析 |
| P1-S4 | 基础画像与基金类型识别 | 3 只样本都输出 `classified_fund_type` 与 `classification_basis` |
| P1-S5 | `§3` 表现提取与投资者收益 fallback | 净值增长率、基准收益率、投资者收益三态输出 |
| P1-S6 | 管理人文本、换手率、利益一致性与持有人结构 | `§4/§8/§9` 直接披露字段可结构化提取 |
| P1-S7 | 持仓快照与份额变动 | 前十大重仓、份额期初/期末/净变动可回归 |
| P1-S8 | façade 集成、净值数据适配器与 P1 验收矩阵 | 3 只样本 36 格矩阵至少 `33/36` 通过 |

**验证要求**

- 对 3 只样本基金（指数/主动/债券各 1 只）执行全量数据提取
- 每只基金提取 12 项数据，与人工核对准确率 > 90%
- 缓存命中时提取时间 < 1 秒

**风险与追踪**

| 风险 | 概率 | 缓解措施 | 追踪状态 |
|------|------|---------|---------|
| 不同基金公司年报格式差异大 | 高 | 设计兜底策略：解析失败显示"数据获取失败" | ⬜ 待验证 |
| 2026 新规"投资者收益率"尚未落地 | 中 | 先用份额变动估算，新规落地后切换 | ⬜ 待验证 |
| akshare API 不稳定 | 中 | 备选天天基金直接 API | ⬜ 待验证 |

**当前实现基线（2026-05-17）**

- 已有 `fund_agent/fund/pdf/downloader.py` 原型，可通过 akshare 查找公告并下载样本基金 `110011` 的 2024 年年报。
- 已有 `fund_agent/fund/pdf/parser.py` 原型，可提取全文文本、表格，并提供 `locate_sections()` / `extract_section()` 的初版章节定位能力。
- 当前章节定位尚不稳定：在样本基金 `110011` 上仅定位到 `§1/§2/§4/§5/§8/§9/§10`，漏掉 `§3`，还不能支撑后续 12 项结构化提取。
- 结构化数据提取模块、SQLite 缓存层和测试套件尚未落地。

**P1-S1 当前状态（2026-05-17）**

- `P1-S1 文档访问契约收口`：✅ completed
- 当前完成内容：
  - `fund_agent/fund/documents/*` 已承载稳定公共契约与唯一仓库入口
  - `FundDocumentRepository.load_annual_report(...)` 不再向上层暴露本地 `Path`
  - `fund_agent/fund/pdf/downloader.py` 已明确降级为内部 helper，并去除目标年份缺失时的 silent fallback
  - downloader / adapter 中的同步阻塞调用已通过 `asyncio.to_thread(...)` 隔离
  - 相关测试命令 ` .venv/bin/python -m pytest tests/fund/documents/test_repository.py tests/fund/pdf/test_downloader.py ` 当前通过（`11 passed`）
- 当前 residual risks：
  - `P1-S2` owner：`parser.py` 章节定位原型仍未稳定，`§3` 漏识别尚未关闭
  - `P1-S3` owner：缓存根路径策略与 SQLite 物化尚未落地
  - 后续 phase owner：当前只支持 `annual_report`，未扩展到其它文档类型

**P1-S2 当前状态（2026-05-17）**

- `P1-S2 章节定位修复与 §3 冻结`：✅ completed
- 当前完成内容：
  - `fund_agent/fund/pdf/section_catalog.py` 已承载 `§1/§2/§3/§4/§5/§8/§9/§10` 的标题规则和目录信号规则
  - `fund_agent/fund/pdf/parser.py` 已从硬编码字典改为消费配置化 catalog
  - `tests/fixtures/fund/pdf_sections/110011_2024_excerpt.txt` 已固定“目录行 + 正文行同名”的 `§3` 事实
  - `tests/fund/pdf/test_parser.py` 已覆盖：
    - 正文 `§3` 命中
    - 目录误判回归
    - `§1/§2/§3/§4/§8/§9/§10` 偏移单调递增
  - 验证命令 `.venv/bin/python -m pytest tests/fund/pdf/test_parser.py -q` 当前通过（`3 passed`）
- 当前 residual risks：
  - `P1-S3` owner：负向/边界测试仍偏少，可在缓存阶段一并补强
  - 后续样本回归 owner：`§5` 当前规则已存在，但 fixture 尚未覆盖
  - 后续样本回归 owner：`§3` 模式仍使用 `.*` 贪婪通配，需由更多样本决定是否收窄

**P1-S3 当前状态（2026-05-17）**

- `P1-S3 两级缓存与仓库内解析物化`：✅ completed
- 当前完成内容：
  - `fund_agent/fund/documents/cache.py` 已提供 `AnnualReportDocumentCache`
  - `documents` 表与 `parsed_reports` 表已在 `documents` 层内部落地
  - parsed report 已物化到 `cache/documents/parsed_reports/*.json`
  - repository 已支持：
    - parsed report 缓存命中
    - 已记录 PDF 路径复用
    - `force_refresh=True` 穿透 parsed report 与 PDF 路径缓存
  - `tests/fund/documents/test_cache.py` 与 `tests/fund/documents/test_repository.py` 已覆盖缓存最小闭环
  - 验证命令 `.venv/bin/python -m pytest tests/fund/documents -q` 当前通过（`10 passed`）
- 当前 residual risks：
  - 后续性能优化 owner：缓存 `initialize()` 每次操作都会重复执行，当前正确但不够高效
  - 后续性能优化 owner：默认缓存实例不做复用，当前单仓库场景无正确性风险
  - 后续缓存治理 owner：缓存根目录仍使用相对路径，后续若要统一根路径策略再单独裁决

**P1-S4 当前状态（2026-05-17）**

- `P1-S4 基础画像与基金类型识别`：✅ completed
- 当前完成内容：
  - `fund_agent/fund/fund_type.py` 已提供 6 类标准基金类型标签和 `FundTypeClassification`
  - `fund_agent/fund/extractors/models.py` 已提供 `EvidenceAnchor`、`ExtractedField`、`ProfileExtractionResult`
  - `fund_agent/fund/extractors/profile.py` 已落地：
    - `basic_identity`
    - `product_profile`
    - `benchmark`
    - `fee_schedule`
  - `extract_profile(report)` 已显式先调用 `classify_fund_type(report)`，再构造通用画像字段
  - `basic_identity.value` 已稳定包含：
    - `classified_fund_type`
    - `classification_basis`
  - `tests/fund/extractors/test_profile.py` 已覆盖：
    - 分类先于通用字段构造
    - 主动权益 / 增强指数 / 债券三类样本识别
    - 费率、基准、规模、经理 anchor 存在
  - 验证命令 `.venv/bin/python -m pytest tests/fund/extractors/test_profile.py -q` 当前通过（`4 passed`）
- 当前 residual risks：
  - 后续 extractor refactor owner：`fund_type.py` 与 `profile.py` 之间仍有部分字段 pattern 重复定义
  - 后续样本回归 owner：`index_fund` / `qdii_fund` / `fof_fund` 仍缺 fixture 与测试覆盖
  - 后续可维护性优化 owner：`_build_basic_identity()` 当前使用列表索引映射字段，后续若继续扩字段建议改为按名字组织

**P1-S5 当前状态（2026-05-17）**

- `P1-S5 §3 表现提取与投资者收益 fallback`：✅ completed
- 当前完成内容：
  - `fund_agent/fund/extractors/models.py` 已补充 `PerformanceExtractionResult`
  - `fund_agent/fund/extractors/performance.py` 已落地：
    - `nav_benchmark_performance`
    - `investor_return`
  - `investor_return` 当前已稳定区分：
    - `direct`
    - `estimated`
    - `missing`
  - `tests/fund/extractors/test_performance.py` 已覆盖：
    - 净值增长率 / 基准收益率提取与 anchor
    - 投资者收益率直接披露路径
    - 投资者收益率估算披露路径
    - 投资者收益率未披露时显式 `missing`
    - `nav_benchmark_performance` 部分命中时显式保留 `missing`
  - `tests/fixtures/fund/extractors/performance/` 已固定最小 `§3` 文本夹具
  - 验证命令 `.venv/bin/python -m pytest tests/fund/extractors/test_performance.py -q` 当前通过（`5 passed`）
- 当前 residual risks：
  - 后续 fallback owner：当前 `estimated` 仅覆盖 `§3` 中显式标记“估算”的披露，不包含依赖 `§10` 或净值序列的后续 fallback
  - 后续集成测试 owner：`§3` 整体缺失路径仍需在真实样本矩阵或单独 fixture 中补强
  - 后续样本回归 owner：当前以最小文本夹具锁定三态输出，真实样本覆盖仍需在 `P1-S8` 验收矩阵阶段继续扩展

**P1-S6 当前状态（2026-05-17）**

- `P1-S6 管理人文本、换手率、利益一致性与持有人结构`：✅ completed
- 当前完成内容：
  - `fund_agent/fund/extractors/models.py` 已补充 `ManagerOwnershipExtractionResult`
  - `fund_agent/fund/extractors/manager_ownership.py` 已落地：
    - `manager_strategy_text`
    - `turnover_rate`
    - `manager_alignment`
    - `holder_structure`
  - `manager_alignment.value["judgment"]` 当前固定为 `None`，确保 P1 只输出原始披露
  - `tests/fund/extractors/test_manager_ownership.py` 已覆盖：
    - 完整披露路径
    - 未披露 `missing` 路径
    - 部分披露路径
    - 换手率口径命中但数值缺失路径
    - 换手率与持有人信息 anchor
  - `tests/fixtures/fund/extractors/manager_ownership/` 已固定最小 `§4/§8/§9` 文本夹具
  - 验证命令 `.venv/bin/python -m pytest tests/fund/extractors/test_manager_ownership.py -q` 当前通过（`4 passed`）
- 当前 residual risks：
  - 后续样本回归 owner：真实年报 `§4/§8/§9` 可能使用表格或不同字段名称，需在 `P1-S8` 验收矩阵阶段继续扩展
  - 后续估算 owner：换手率未披露时的同类中位数估算尚未接入，当前只能显式返回 `missing`

**P1-S7 当前状态（2026-05-17）**

- `P1-S7 持仓快照与份额变动`：✅ completed
- 当前完成内容：
  - `fund_agent/fund/extractors/models.py` 已补充 `HoldingsShareChangeExtractionResult`
  - `fund_agent/fund/extractors/holdings_share_change.py` 已落地：
    - `holdings_snapshot`
    - `share_change`
  - `tests/fund/extractors/test_holdings_share_change.py` 已覆盖：
    - 前十大重仓表
    - 行业分布表
    - 份额变动表
    - 行业分布缺失路径
    - 表格整体缺失路径
  - 验证命令 `.venv/bin/python -m pytest tests/fund/extractors/test_holdings_share_change.py -q` 当前通过（`3 passed`）
- 当前 residual risks：
  - 后续样本回归 owner：真实年报表头差异仍需在 `P1-S8` 验收矩阵阶段继续扩展
  - 后续 schema owner：当前表格行按原表头输出，最终标准字段名需在 façade 集成前裁决

**P1-S8 当前状态（2026-05-17）**

- `P1-S8 façade 集成、净值数据适配器与 P1 验收矩阵`：✅ completed
- 当前完成内容：
  - `fund_agent/fund/data_extractor.py` 已落地：
    - `StructuredFundDataBundle`
    - `FundDataExtractor`
  - `fund_agent/fund/data/nav_data.py` 已落地：
    - `FundNavDataAdapter`
    - `NavDataResult`
    - `nav_cache` SQLite 表
  - `tests/fund/integration/test_p1_sample_matrix.py` 已覆盖 3 只样本基金 12 项矩阵，当前结果 `36/36`
  - `tests/fund/data/test_nav_data.py` 已覆盖净值缓存命中和强制刷新
  - 验证命令 `.venv/bin/python -m pytest tests/fund/documents tests/fund/pdf/test_parser.py tests/fund/extractors tests/fund/data/test_nav_data.py tests/fund/integration/test_p1_sample_matrix.py -q` 当前通过（`32 passed`）
- 当前 residual risks：
  - 后续端到端 owner：当前 P1 矩阵使用 fake repository 和 fixture report，真实 PDF 样本矩阵需在端到端验证中继续扩展
  - 后续网络验证 owner：默认 akshare fetcher 已封装，本轮测试未访问真实网络

---

### P2: 分析引擎（R=A+B-C + 检验 + 审计）

**目标**

完成收益归因计算、言行一致性检验、投资者获得感分析、否决项检查、程序审计功能。

**进入条件**

- [x] P1 退出条件全部满足
- [x] 12 项关键数据可从缓存获取

**退出条件**

- [x] `fund/analysis/r_abc.py` 能计算近 1/3/5 年 R=A+B-C 归因
- [x] `fund/analysis/alpha_judge.py` 能区分结构性 vs 阶段性超额
- [x] `fund/analysis/consistency_check.py` 能输出言行一致性 4 维度信号
- [x] `fund/analysis/investor_return.py` 能计算行为损益
- [x] `fund/analysis/risk_check.py` 能执行 5 项否决检查 + 压力测试
- [x] `fund/analysis/checklist.py` 能输出 7 问题红/黄/绿灯
- [x] `fund/audit/audit_programmatic.py` 能执行 P1/P2/P3/L1/R1/R2 规则检查
- [x] `fund/template/renderer.py` 能将数据填充到定性模板 v2

**任务切片**

| Slice | 任务 | 验证方式 |
|-------|------|---------|
| P2-S1 | 实现 R=A+B-C 计算模块 | 对样本基金计算，与手动计算一致 |
| P2-S2 | 实现超额收益性质判断 | 对已知基金判断结果合理 |
| P2-S3 | 实现言行一致性检验 | 对样本基金输出 4 维度信号 |
| P2-S4 | 实现投资者获得感分析 | 计算行为损益 + 资金流向判断 |
| P2-S5 | 实现否决项检查 | 5 项否决条件检查正确 |
| P2-S6 | 实现压力测试 | 模拟 -20%/-40%/-60% 场景 |
| P2-S7 | 实现检查清单引擎 | 7 问题输出红/黄/绿灯 |
| P2-S8 | 实现程序审计（P1/P2/P3/L1/R1/R2） | 能检测到故意注入的错误 |
| P2-S9 | 实现模板渲染器 | 输出 8 章报告 Markdown |
| P2-S10 | 实现证据锚点标注 | 每个数据标注来源 |

**验证要求**

- R=A+B-C 计算结果与手动计算误差 < 0.01%
- 程序审计能检测到以下注入错误：
  - 章节缺失（P1）
  - 关键字段为空（P2）
  - R=A+B-C 计算不闭合（L1）
  - 检查清单信号与规则不一致（R1）
- 模板渲染输出包含 8 章完整内容

**P2-S1 当前状态（2026-05-17）**

- `P2-S1 实现 R=A+B-C 计算模块`：✅ completed
- 当前完成内容：
  - `fund_agent/fund/analysis/r_abc.py` 已提供纯计算入口 `calculate_r_abc(...)` 与多周期入口 `calculate_r_abc_series(...)`
  - `calculate_r_abc_from_bundle(...)` 已支持从 P1 `StructuredFundDataBundle` 适配计算
  - `RabcAttribution` 已输出 `R/B/A/C/turnover_cost/net_excess_return` 与参与计算字段的 `EvidenceAnchor`
  - 缺少股票仓位、关键字段或关键子字段时返回 `missing`，不使用默认仓位或间接假设
  - `tests/fund/analysis/test_r_abc.py` 已覆盖公式闭合、P1 字段解析、证据锚点和缺失路径
  - 验证命令 `.venv/bin/python -m pytest tests/fund/analysis/test_r_abc.py -q` 当前通过（`6 passed`）
- 当前 residual risks：
  - `P2-S2` owner：当前只输出数值归因，不判断结构性/阶段性超额
  - `P2-S8` owner：L1 公式审计尚未接入
  - 后续 extractor refinement owner：股票仓位仍需显式输入，尚未由 P1 稳定抽取

**P2-S2 当前状态（2026-05-17）**

- `P2-S2 实现超额收益性质判断`：✅ completed
- 当前完成内容：
  - `fund_agent/fund/analysis/alpha_judge.py` 已提供 `judge_alpha_nature(...)`
  - `observations_from_attributions(...)` 已支持从 P2-S1 `RabcAttribution` 适配判断样本
  - `AlphaJudgment` 已输出性质判断、正 Alpha 期数、环境覆盖、来源解释计数、判断依据和风险
  - 纯指数基金返回 `not_applicable`
  - 样本不足返回 `insufficient_data`，不强行判断结构性或阶段性
  - 市场环境和来源解释强度必须显式传入，缺失时报错
  - `tests/fund/analysis/test_alpha_judge.py` 已覆盖核心判断路径
  - 验证命令 `.venv/bin/python -m pytest tests/fund/analysis/test_alpha_judge.py -q` 当前通过（`7 passed`）
- 当前 residual risks：
  - `P2-S3` owner：来源解释强度后续应由言行一致性和持仓行为检查提供更强证据
  - `P3-S2 or later market-state adapter` owner：市场环境标签后续应由温度计或市场状态模块显式传入
  - `P2-S8` owner：性质判断与报告文字一致性审计尚未接入

**P2-S3 当前状态（2026-05-17）**

- `P2-S3 实现言行一致性检验`：✅ completed
- 当前完成内容：
  - `fund_agent/fund/analysis/consistency_check.py` 已提供 `check_consistency(...)`
  - 4 维度输出：
    - 投资风格：§4 风格宣称 vs 显式实际持仓风格
    - 行业偏好：§4 行业宣称 vs §8 行业分布
    - 仓位管理：§4 仓位策略 vs 显式实际股票仓位
    - 换手水平：§4 持有周期/换手宣称 vs §8 换手率
  - `ConsistencyCheckResult` 已输出整体状态和信号
  - 缺少实际风格或股票仓位时返回 `insufficient_data`，不使用默认假设
  - `tests/fund/analysis/test_consistency_check.py` 已覆盖核心信号路径
  - 验证命令 `.venv/bin/python -m pytest tests/fund/analysis/test_consistency_check.py -q` 当前通过（`5 passed`）
- 当前 residual risks：
  - 后续 extractor refinement owner：实际持仓风格和股票仓位仍需显式输入，尚未由 P1 稳定抽取
  - 后续 multi-period behavior analysis owner：跨期风格稳定性尚未实现
  - `P2-S8` owner：言行一致性信号与报告文字一致性审计尚未接入

**P2-S4 当前状态（2026-05-17）**

- `P2-S4 实现投资者获得感分析`：✅ completed
- 当前完成内容：
  - `fund_agent/fund/analysis/investor_return.py` 已提供 `analyze_investor_experience(...)`
  - `calculate_behavior_gap(...)` 已计算行为损益：投资者实际收益率减基金产品收益率
  - `judge_fund_flow(...)` 已基于 §10 份额净变动和产品收益方向判断资金流向
  - `InvestorExperienceResult` 已输出获得感状态、行为损益和资金流向
  - 投资者收益率缺失时返回 `missing`，不静默估算
  - 份额变动子字段缺失时资金流向返回 `missing`
  - `tests/fund/analysis/test_investor_return.py` 已覆盖核心路径
  - 验证命令 `.venv/bin/python -m pytest tests/fund/analysis/test_investor_return.py -q` 当前通过（`6 passed`）
- 当前 residual risks：
  - 后续 investor_return fallback refinement owner：投资者收益率缺失 fallback 尚未实现
  - later monthly flow adapter owner：高点/低点追涨抄底无法仅凭年度份额净变动精细定位
  - `P2-S8` owner：行为损益和报告文字一致性审计尚未接入

**P2-S5 当前状态（2026-05-17）**

- `P2-S5 实现否决项检查`：✅ completed
- 当前完成内容：
  - `fund_agent/fund/analysis/risk_check.py` 已提供 `run_risk_checks(...)`
  - 5 项否决检查已覆盖：
    - 清盘风险：基金规模 `< 5000 万元`
    - 基金经理任期：管理本基金 `< 6 个月`
    - 严重风格漂移：言行一致性检验红灯
    - 费率远超同类：总费率 `> 同类中位数 × 2`
    - 跟踪误差过大：指数基金跟踪误差 `> 2%`
  - `RiskCheckResult` 已输出汇总状态、否决项、跟踪项和下一步最小验证问题
  - 缺少经理任期、同类费率中位数或跟踪误差时返回 `insufficient_data`，不强行判安全
  - `tests/fund/analysis/test_risk_check.py` 已覆盖核心否决路径和缺失输入路径
  - 验证命令 `.venv/bin/python -m pytest tests/fund/analysis/test_risk_check.py -q` 当前通过（`10 passed`）
- 当前 residual risks：
  - `P2-S6` owner：压力测试需在同一风险模块内接入
  - later external metrics adapter owner：经理任期、同类费率中位数和跟踪误差仍由调用方显式提供
  - `P2-S8` owner：否决项与报告结论一致性审计尚未接入

**P2-S6 当前状态（2026-05-17）**

- `P2-S6 实现压力测试`：✅ completed
- 当前完成内容：
  - `fund_agent/fund/analysis/risk_check.py` 已提供 `run_stress_test(...)`
  - 固定模拟 `-20% / -40% / -60%` 三个场景，符合 `docs/design.md` 第 4.5 节
  - `StressTestRule` 已配置模板第 6 章 `preferred_lens` 的基金类型阈值
  - `StressScenarioResult` 已输出账户余额、浮亏金额、压力等级、承受能力状态和判断依据
  - 最大可承受亏损比例缺失时返回 `not_provided`，不猜测用户能否承受
  - `tests/fund/analysis/test_risk_check.py` 已覆盖固定场景、主动/债券基金阈值、缺失承受能力、非法输入和自定义阈值配置
  - 验证命令 `.venv/bin/python -m pytest tests/fund/analysis/test_risk_check.py -q` 当前通过（`10 passed`）
  - controller code review artifact：`docs/reviews/p2-s6-code-review-controller-judgment-2026-05-17.md`
- 当前 residual risks：
  - `P3` owner：压力测试输出已进入 P2-S9 模板渲染，端到端用户流程尚未验证
  - `P2-S8` owner：压力测试和报告文字一致性审计尚未接入
  - later user-profile input owner：投入金额和最大可承受亏损比例当前由调用方显式提供
  - `P2 aggregate review` owner：本 slice 外部 reviewer 未产出可采纳 artifact，aggregate review 前需重新取得两份独立 review 或记录用户接受单 reviewer 风险

**P2-S7 当前状态（2026-05-17）**

- `P2-S7 实现检查清单引擎`：✅ completed
- 当前完成内容：
  - `fund_agent/fund/analysis/checklist.py` 已提供 `run_checklist(...)`
  - 检查清单已覆盖 `docs/design.md` 第 4.6 节 7 个问题：
    - 超额收益能覆盖成本吗？
    - 基金经理跟我一条心吗？
    - 投资者真的赚到钱了吗？
    - 说的和做的一样吗？
    - 这只基金不死吗？
    - 当前估值处于什么位置？
    - 这笔钱 3-4 年内不会用吗？
  - `ChecklistResult` 已输出 7 项结果、红/黄/灰分组、汇总信号和下一步最小验证问题
  - 估值状态和用户资金期限必须由调用方显式提供；缺失时返回灰灯
  - `tests/fund/analysis/test_checklist.py` 已覆盖核心规则路径
  - 验证命令 `.venv/bin/python -m pytest tests/fund/analysis -q` 当前通过（`40 passed`）
  - controller code review artifact：`docs/reviews/p2-s7-code-review-controller-judgment-2026-05-17.md`
- 当前 residual risks：
  - `P2-S8` owner：R1/R2 审计尚未验证检查清单信号与规则一致性
  - later thermometer adapter owner：估值状态当前由调用方显式传入，尚未接入温度计
  - later user-profile input owner：资金期限当前由调用方显式传入，尚未接入用户问答或画像

**P2-S8 当前状态（2026-05-18）**

- `P2-S8 实现程序审计（P1/P2/P3/L1/R1/R2）`：✅ completed
- 当前完成内容：
  - `fund_agent/fund/audit/audit_programmatic.py` 已提供 `run_programmatic_audit(...)`
  - 已覆盖 MVP 程序审计规则：
    - `P1`：报告章节结构不匹配
    - `P2`：章节内容过短
    - `P3`：缺少证据与出处或证据锚点
    - `L1`：R=A+B-C 数值计算不闭合
    - `R1`：检查清单信号与规则不一致
    - `R2`：最终判断与检查清单信号矛盾
  - `ProgrammaticAuditInput` 明确区分报告 Markdown、R=A+B-C 结构化结果、检查清单结果和最终判断
  - 缺少报告、R=A+B-C 结构化结果、检查清单或最终判断时返回失败，不把未执行规则伪装成通过
  - `tests/fund/audit/test_audit_programmatic.py` 已覆盖必需输入缺失、故意注入错误和未知检查清单信号防御
  - 验证命令 `.venv/bin/python -m pytest tests/fund/analysis tests/fund/audit -q` 当前通过（`49 passed`）
  - controller code review artifact：`docs/reviews/p2-s8-code-review-controller-judgment-2026-05-18.md`
- 当前 residual risks：
  - `P2-S9` owner：模板渲染器已接入程序审计输入
  - `P3-S4` owner：端到端报告通过程序审计尚未验证
  - v2 audit owner：E1/E2/E3/C1/C2 和 LLM/证据复核层尚未实现

**P2-S9 当前状态（2026-05-18）**

- `P2-S9 实现模板渲染器`：✅ completed
- 当前完成内容：
  - `fund_agent/fund/template/renderer.py` 已提供 8 章 Markdown 模板渲染器
  - `TemplateRenderInput` 显式聚合 P1 `StructuredFundDataBundle`、P2 分析结果、检查清单、压力测试、最终判断和可选当前阶段说明
  - `TemplateRenderResult` 输出 `report_markdown`、`audit_input` 和去重后的 `evidence_anchors`
  - `audit_input` 可直接用于 `run_programmatic_audit(...)`
  - 章节内证据行使用 `> 📎 证据：年报§...`，附录输出 `## 证据与出处`
  - 缺失数据显式输出“未披露”或“数据不足”
  - 最终判断限制为 `worth_holding / needs_attention / suggest_replace`
  - 已修复 code review 发现的 `dict_values(...)` 泄漏、重复句号和 README 过期条目
  - `tests/fund/template/test_renderer.py` 已覆盖 8 章完整性、证据锚点格式、审计兼容、缺失路径、禁用交易措辞和 review 回归
  - 验证命令 `.venv/bin/python -m pytest tests/fund/template tests/fund/audit -q` 当前通过（`18 passed`）
  - 验证命令 `.venv/bin/python -m pytest tests/fund/analysis -q` 当前通过（`40 passed`）
  - code review artifacts：
    - `docs/reviews/p2-s9-code-review-mimo-2026-05-18.md`
    - `docs/reviews/p2-s9-code-review-glm-2026-05-18.md`
    - `docs/reviews/p2-s9-code-review-controller-judgment-2026-05-18.md`
    - `docs/reviews/p2-s9-rereview-glm-2026-05-18.md`
- 当前 residual risks：
  - `P2-S10` owner：证据锚点正文和附录格式已专项收口
  - `P3-S4` owner：端到端 CLI 报告通过程序审计尚未验证
  - later template refinement owner：`_validate_report_wording()` 使用 substring 匹配禁用词，未来模板若引入合法分析短语“买入前检查清单”可能误报

**P2-S10 当前状态（2026-05-18）**

- `P2-S10 实现证据锚点标注`：✅ completed
- 当前完成内容：
  - 正文证据行对年报来源输出年份、章节和证据描述
  - 附录年报锚点按 `年报{年份}§{章节}表{编号}行{行号}` 输出
  - 表格、行定位、章节缺失时显式写 `未定位`
  - 页码以附加位置元数据保留
  - 非年报来源输出 `外部数据(external_api)`、`计算(derived)` 或未知来源标签，不伪装成年报
  - 缺少章节证据时，正文输出数据不足证据行，附录输出章节级缺证条目
  - `tests/fund/template/test_renderer.py` 已覆盖正文证据格式、附录表格/行定位、缺失定位降级、页码保留、非年报来源、缺证章节和审计兼容
  - 验证命令 `.venv/bin/python -m pytest tests/fund/template tests/fund/audit -q` 当前通过（`23 passed`）
  - 验证命令 `.venv/bin/python -m pytest tests/fund/analysis -q` 当前通过（`40 passed`）
  - code review artifacts：
    - `docs/reviews/p2-s10-code-review-mimo-2026-05-18.md`
    - `docs/reviews/p2-s10-code-review-glm-2026-05-18.md`
    - `docs/reviews/p2-s10-code-review-controller-judgment-2026-05-18.md`
- 当前 residual risks：
  - `P2 aggregate deepreview` owner：已验证 P2-S1 至 P2-S10 组合后无跨 slice 回归
  - `P3-S4` owner：端到端 CLI 报告通过程序审计尚未验证
  - later evidence confirm owner：缺证附录当前为章节级，不是 item 级证据确认
  - later template refinement owner：`_validate_report_wording()` 使用 substring 匹配禁用词，未来模板若引入合法分析短语“买入前检查清单”可能误报

**P2 aggregate deepreview 当前状态（2026-05-18）**

- `P2 aggregate deepreview`：✅ completed
- 当前完成内容：
  - 审查范围为 `a6b1516...HEAD`，覆盖 `P2-S9` 模板渲染器、`P2-S10` 证据锚点标注、相关测试、README 与 gate artifact
  - AgentMiMo aggregate review 结论为 PASS，无 blocking finding
  - AgentGLM aggregate review 结论为 PASS，无 blocking finding；接受 1 个 doc-sync info finding：P2 退出条件中模板渲染器 checkbox 未勾选
  - 已完成 doc-sync fix，将 P2 进入条件、退出条件、phase 状态和下一 gate 同步到当前真实状态
  - 验证命令 `.venv/bin/python -m pytest tests/fund/template tests/fund/audit tests/fund/analysis -q` 当前通过（`63 passed`）
  - aggregate review artifacts：
    - `docs/reviews/p2-aggregate-review-mimo-2026-05-18.md`
    - `docs/reviews/p2-aggregate-review-glm-2026-05-18.md`
    - `docs/reviews/p2-aggregate-fix-2026-05-18.md`
    - `docs/reviews/p2-aggregate-review-controller-judgment-2026-05-18.md`
  - accepted deepreview commit：`07fe0d0`
- 当前 residual risks：
  - `P3-S4` owner：端到端 CLI 报告通过程序审计尚未验证
  - later evidence confirm owner：缺证附录当前为章节级，不是 item 级证据确认
  - later template refinement owner：`_validate_report_wording()` 使用 substring 匹配禁用词，未来模板若引入合法分析短语“买入前检查清单”可能误报
  - v2 audit owner：`_EVIDENCE_MARKER_PATTERN` 和审计章节标题匹配依赖当前模板措辞，未来模板措辞调整时需同步测试

**Draft PR gate 当前状态（2026-05-18）**

- `Draft PR #1`：✅ draft-PR-pass
- 当前完成内容：
  - 已将 `a6b1516` 推送为远端 `main`
  - 已将 `chore/reconcile-baseline` 推送到远端并创建 draft PR：`https://github.com/bill20232033cc/fund-agent/pull/1`
  - PR review 接受 1 个 info finding：aggregate review artifact 存在 trailing whitespace
  - 已移除 trailing whitespace，并记录修复 artifact
  - AgentGLM re-review 结论为 PASS
  - accepted PR review commit：`8f5029c`
  - follow-up push 已完成
- 当前验证：
  - `.venv/bin/python -m pytest tests/fund/template tests/fund/audit tests/fund/analysis -q`：`63 passed`
  - `git diff --check`：通过
  - PR merge state：`CLEAN`
- 未执行动作：
  - 未 merge PR
  - 未 mark ready for review
  - 未 request reviewers
  - 未 delete branch

**风险与追踪**

| 风险 | 概率 | 缓解措施 | 追踪状态 |
|------|------|---------|---------|
| 业绩基准计算复杂（多指数加权） | 中 | MVP 先用简化计算，v2 精确实现 | ⬜ 待验证 |
| 超额收益性质判断主观性强 | 中 | MVP 用规则引擎（多年度为正 + 不同环境），v2 引入 LLM | ⬜ 待验证 |

---

### P3: CLI 入口 + 整合测试 + 验证

**目标**

完成 CLI 入口封装，整合所有功能，实现端到端验证。

**进入条件**

- [x] P2 退出条件全部满足
- [x] 单只基金分析可本地运行

**退出条件**

- [x] `fund-analysis analyze <fund_code>` 命令可用
- [x] 输出完整 8 章分析报告（Markdown 格式）
- [x] 报告通过程序审计
- [x] 3 只样本基金端到端测试通过
- [ ] 单只基金分析时间 < 30 秒（不含 PDF 下载）
- [x] 包含 README.md（安装 + 使用说明）
- [ ] 单元测试覆盖率 > 50%

**任务切片**

| Slice | 任务 | 验证方式 |
|-------|------|---------|
| P3-S1 | CLI 入口封装（Typer，与当前 `pyproject.toml` 入口对齐） | `fund-analysis analyze 110011` 输出报告 |
| P3-S2 | 温度计数据爬取（有知有行） | 能获取全市场和指数温度 |
| P3-S3 | 端到端整合测试 | 3 只样本基金完整流程 |
| P3-S4 | 程序审计集成 | 报告通过 P1/P2/P3/L1/R1/R2 |
| P3-S5 | 证据锚点集成 | 每个数据标注来源 |
| P3-S6 | 编写 README.md | 包含安装、使用、示例 |
| P3-S7 | 编写单元测试 | pytest 覆盖率 > 50% |
| P3-S8 | 性能优化 | 单只基金 < 30 秒 |

**验证要求**

- 端到端测试：输入 3 只样本基金代码，输出 3 份完整报告
- 每份报告包含 8 章内容 + 证据锚点
- 程序审计全部通过
- `pytest` 覆盖率 > 50%

**风险与追踪**

| 风险 | 概率 | 缓解措施 | 追踪状态 |
|------|------|---------|---------|
| 有知有行页面结构变更 | 中 | 异常处理 + 24h 缓存 | ⬜ 待验证 |
| 整合测试发现数据层 bug | 高 | 预留 2 天 buffer | ⬜ 待验证 |

**P3-S1 当前状态（2026-05-18）**

- `P3-S1 CLI 入口封装`：✅ completed
- 当前完成内容：
  - `fund_agent/services/fund_analysis_service.py` 新增 `FundAnalysisService`、`FundAnalysisRequest` 和 `FundAnalysisResult`
  - Service 通过显式请求字段编排 `FundDataExtractor.extract(...)`、P2 分析、8 章模板渲染和程序审计
  - UI 层 `fund_agent/ui/cli.py` 保持 Typer，与当前 `pyproject.toml` 脚本入口一致
  - `fund-analysis analyze FUND_CODE` 输出完整 Markdown 到 stdout，失败时输出 `分析失败：...` 并非零退出
  - `fund-analysis checklist FUND_CODE` 不再输出误导性成功文本，当前非零退出并提示使用 `analyze`
  - `README.md` 和 `tests/README.md` 已同步当前 CLI 和测试边界
  - 验证命令 `.venv/bin/python -m pytest tests/services tests/ui tests/fund/template tests/fund/audit tests/fund/analysis -q` 当前通过（`68 passed`）
  - `git diff --check` 当前通过
  - code review artifacts：
    - `docs/reviews/p3-s1-code-review-glm-2026-05-18.md`
    - `docs/reviews/p3-s1-code-review-controller-judgment-2026-05-18.md`
    - `docs/reviews/p3-s1-fix-2026-05-18.md`
    - `docs/reviews/p3-s1-rereview-glm-2026-05-18.md`
  - accepted slice commit：`c5a240c`
- 当前 residual risks：
  - `P3-S2` owner：Service 当前没有市场环境和来源解释输入，`judge_alpha_nature(())` 会显式返回 `insufficient_data`
  - `P3-S3` owner：真实 PDF/网络路径和 3 只样本基金 CLI 端到端矩阵尚未验证
  - later CLI UX owner：程序审计失败信息当前直接透出审计消息，MVP 可接受但后续可优化用户文案

**P3-S2 当前状态（2026-05-18）**

- `P3-S2 温度计数据爬取（有知有行）`：✅ completed
- 当前完成内容：
  - `fund_agent/fund/data/thermometer.py` 新增 `FundThermometerAdapter`
  - 输出 `ThermometerSnapshot`、`MarketTemperature`、`IndexTemperature`、`MacroTemperature`
  - 默认读取 `https://youzhiyouxing.cn/data` 与 `https://youzhiyouxing.cn/data/macro`
  - 支持 24h fresh cache、7 天 stale fallback、无缓存失败 `unavailable=True`
  - 支持当前真实页面布局：全市场 `70°`/`70℃`、指数代码位于名称单元格、前置非指数表跳过、`10年期国债到期收益率`
  - 缓存写入失败不阻断已成功抓取和解析的数据
  - 当前只提供 Capability data adapter，尚未接入 Service、CLI 或检查清单估值状态
  - live-response smoke 验证可解析全市场温度、11 行指数数据、沪深300温度/内在收益率/股息率、债市温度和 10 年期国债到期收益率
  - 验证命令 `.venv/bin/python -m pytest tests/fund/data/test_thermometer.py -q` 当前通过（`13 passed`）
  - 验证命令 `.venv/bin/python -m pytest tests/fund/data tests/fund/analysis tests/services tests/ui -q` 当前通过（`60 passed`）
  - `git diff --check` 当前通过
  - code review artifacts：
    - `docs/reviews/p3-s2-implementation-2026-05-18.md`
    - `docs/reviews/p3-s2-code-review-glm-2026-05-18.md`
    - `docs/reviews/p3-s2-code-review-mimo-2026-05-18.md`
    - `docs/reviews/p3-s2-code-review-controller-judgment-2026-05-18.md`
    - `docs/reviews/p3-s2-fix-2026-05-18.md`
    - `docs/reviews/p3-s2-rereview-glm-2026-05-18.md`
    - `docs/reviews/p3-s2-rereview-mimo-2026-05-18.md`
  - accepted slice commit：`1747aaf`
- 当前 residual risks：
  - `P3-S3/P3-S4` owner：温度计 adapter 尚未接入 Service/CLI/checklist valuation_state
  - `P3-S3/P3-S4` owner：有知有行页面结构仍可能变化，后续集成测试和运行监控需覆盖 unavailable/stale 输出
  - later integration owner：Service/CLI 接入时应显式传入运行期 cache root，避免依赖进程 cwd

**P3-S3 当前状态（2026-05-18）**

- `P3-S3 端到端整合测试`：✅ completed
- 当前完成内容：
  - `tests/fund/integration/test_p3_cli_e2e_matrix.py` 新增 3 只样本基金 CLI 端到端矩阵
  - 矩阵覆盖 `110011 -> qdii_fund`、`510300 -> index_fund`、`000171 -> bond_fund`
  - CLI 矩阵通过 fake repository / fake nav provider 隔离网络与 PDF 副作用，但仍经过真实 Typer CLI、Service、`FundDataExtractor`、extractors、P2 analysis、模板渲染和程序审计
  - 修复真实 `§2` 表格键值字段抽取、低质量 parsed report cache 复用和模板 `benchmark_text` 契约错配
  - 验证命令 `.venv/bin/python -m pytest tests/fund/data tests/fund/documents tests/fund/extractors tests/fund/integration tests/fund/template tests/fund/audit tests/fund/analysis tests/services tests/ui -q` 当前通过（`115 passed`）
  - `git diff --check` 当前通过
  - code review artifacts：
    - `docs/reviews/p3-s3-code-review-controller-judgment-2026-05-18.md`
    - `docs/reviews/p3-s3-code-review-glm-2026-05-18.md`
    - `docs/reviews/p3-s3-code-review-mimo-2026-05-18.md`
  - accepted slice commit：`e0b1b93`
- 当前 residual risks：
  - classifier cleanup owner：基金简称中的 QDII 标识仍建议后续作为独立字段参与分类，避免仅依赖 investment_scope 的理论漏判
  - later integration owner：真实 PDF/网络路径仍应保留人工 smoke 或独立运行监控

**P3-S4 当前状态（2026-05-18）**

- `P3-S4 程序审计集成`：✅ completed
- 当前完成内容：
  - P3 CLI 端到端矩阵新增 `_RecordingService` 测试代理，记录真实 `FundAnalysisService.analyze(...)` 返回值
  - 对 3 只样本基金逐一断言 `audit_result.passed`
  - 对 3 只样本基金逐一断言 `audit_result.checked_rules == ("P1", "P2", "P3", "L1", "R1", "R2")`
  - 对 3 只样本基金逐一断言 `audit_result.issues == ()`
  - 验证命令 `.venv/bin/python -m pytest tests/fund/integration/test_p3_cli_e2e_matrix.py tests/services/test_fund_analysis_service.py tests/fund/audit/test_audit_programmatic.py tests/fund/template/test_renderer.py -q` 当前通过（`26 passed`）
  - 验证命令 `.venv/bin/python -m pytest tests/fund/data tests/fund/documents tests/fund/extractors tests/fund/integration tests/fund/template tests/fund/audit tests/fund/analysis tests/services tests/ui -q` 当前通过（`115 passed`）
  - `git diff --check` 当前通过
  - artifacts：
    - `docs/reviews/p3-s4-implementation-2026-05-18.md`
    - `docs/reviews/p3-s4-code-review-controller-judgment-2026-05-18.md`
  - accepted implementation commit：`caf5b31`
- 当前 residual risks：
  - P3-S4 使用 fake repository / fake nav provider 隔离网络与 PDF，不替代真实运行 smoke

**P3-S5 当前状态（2026-05-18）**

- `P3-S5 证据锚点集成`：✅ completed
- 当前完成内容：
  - `tests/fund/integration/test_p3_cli_e2e_matrix.py` 新增 `_body_evidence_lines(...)`、`_appendix_evidence_lines(...)` 和 `_assert_complete_evidence_contract(...)`
  - 3 只样本基金每份 CLI 报告均断言正文 `> 📎 证据：` 行数量为 8，覆盖模板 0-7 章
  - 3 只样本基金每份 CLI 报告均断言正文证据行包含 `年报2024§`，且不出现“当前章节未携带证据锚点”
  - 3 只样本基金每份 CLI 报告均断言附录不出现 `- [M...]` 缺证占位
  - 附录断言覆盖关键数据来源：`§2` 基金身份/产品/基准、`§3` 净值与投资者收益、`§4` 管理人策略、`§8` 重仓和行业、`§9` 基金经理持有、`§10` 份额变动
  - 验证命令 `.venv/bin/python -m pytest tests/fund/integration/test_p3_cli_e2e_matrix.py tests/fund/template/test_renderer.py tests/fund/audit/test_audit_programmatic.py -q` 当前通过（`24 passed`）
  - `git diff --check` 当前通过
  - artifacts：
    - `docs/reviews/p3-s5-implementation-2026-05-18.md`
    - `docs/reviews/p3-s5-code-review-controller-judgment-2026-05-18.md`
  - accepted slice commit：`46432c0`
- 当前 residual risks：
  - P3-S5 当前验证的是 deterministic fake repository 输出的报告证据契约，不替代真实 PDF/network smoke

**P3-S6 当前状态（2026-05-18）**

- `P3-S6 编写 README.md`：✅ completed
- 当前完成内容：
  - 根目录 `README.md` 已重写为用户手册，覆盖安装、5 分钟跑通、常用命令、常用参数、报告输出、当前能力、本地验证和文档导航
  - README 当前命令与 Typer CLI 对齐：`fund-analysis --help`、`fund-analysis analyze --help`、`fund-analysis analyze FUND_CODE`
  - README 明确 `fund-analysis checklist` 仍是占位命令，避免误导用户认为独立检查清单已接入
  - README 已移除“3 只样本基金端到端 CLI 矩阵尚未实现”的过期表述
  - README 文档导航仅保留当前仓库真实存在的文档路径
  - 验证命令 `.venv/bin/fund-analysis --help` 当前通过
  - 验证命令 `.venv/bin/fund-analysis analyze --help` 当前通过
  - `git diff --check` 当前通过
  - artifacts：
    - `docs/reviews/p3-s6-implementation-2026-05-18.md`
    - `docs/reviews/p3-s6-code-review-controller-judgment-2026-05-18.md`
  - accepted slice commit：`8904588`
- 当前 residual risks：
  - README 示例命令未在本 slice 执行真实 PDF/network smoke，后续仍需独立验证真实数据路径

**P3-S7 当前状态（2026-05-18）**

- `P3-S7 编写单元测试`：✅ completed
- 当前完成内容：
  - `pyproject.toml` 的 dev 依赖新增 `pytest-cov>=7.1`
  - `tests/README.md` 新增覆盖率 gate 命令和 P3-S7 覆盖率目标说明
  - 验证命令 `.venv/bin/python -m pytest tests/fund/data tests/fund/documents tests/fund/extractors tests/fund/integration tests/fund/template tests/fund/audit tests/fund/analysis tests/services tests/ui --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q` 当前通过
  - 当前结果：`115 passed`，`Required test coverage of 50% reached. Total coverage: 90.07%`
  - artifacts：
    - `docs/reviews/p3-s7-implementation-2026-05-18.md`
    - `docs/reviews/p3-s7-code-review-controller-judgment-2026-05-18.md`
  - accepted slice commit：`d1d506b`
- 当前 residual risks：
  - 覆盖率是广度信号，不替代语义 review；真实 PDF/network smoke 仍需独立验证

---

## 3. 依赖关系

```
P0（环境搭建）
  └── P1（数据层）
        └── P2（分析引擎）
              └── P3（整合测试）
```

- 所有 Phase 串行执行，无并行 Phase
- P1 内部的 Slice 可部分并行（P1-S4~P1-S7 在 P1-S3 被接受后可并行）
- P2 内部的 Slice 可部分并行（P2-S1~S7 与 P2-S8~S10 可并行）

---

## 4. 阻塞问题追踪

| ID | 问题 | 影响 Phase | 状态 | 决议 |
|----|------|-----------|------|------|
| BQ-1 | 巨潮网反爬策略未知 | P0/P1 | ✅ closed | 已改用 akshare + eastmoney PDF，无需直接访问巨潮 |
| BQ-2 | 2026 新规"投资者收益率"披露时间表 | P2 | ⬜ open | P1 已提供 `investor_return` 三态和 `share_change` 输入，P2 再实现行为损益 |
| BQ-3 | 有知有行温度数据页面结构 | P3 | ✅ closed | P3-S2 已用真实响应 smoke 验证 `/data` 与 `/data/macro` 当前布局，并以 fake HTML 单测锁定关键解析路径 |
| BQ-4 | akshare 基金净值 API 稳定性 | P1/P3 | 🟡 partially closed | P1-S8 已封装可注入 fetcher 与 `nav_cache`，真实网络验证移交 P3 |
| BQ-5 | 当前章节定位规则无法稳定识别 `§3` 正文 | P1 | ✅ closed | 已由 P1-S2 章节定位修复与 `§3` 冻结关闭 |

---

## 5. 残余风险追踪

| ID | 风险 | Phase | 缓解状态 | 需要人类裁决？ |
|----|------|-------|---------|--------------|
| RR-1 | PDF 格式不统一导致解析失败 | P1 | 已设计兜底策略 | 否 |
| RR-2 | 超额收益性质判断主观性强 | P2 | MVP 用规则引擎 | 否 |
| RR-3 | 审计规则过严导致频繁阻断 | P2 | MVP 仅启用程序审计 | 否 |
| RR-4 | 温度计爬虫被封锁 | P3 | 24h 缓存 + 7 天 stale fallback + `unavailable=True`；Service/CLI 接入仍在 P3 后续 slice | 是（如被封锁且无可用缓存需人工确认） |
| RR-5 | `dayu-agent` wheel 下载受 GitHub 可达性影响 | P0/P1 | 当前虚拟环境已安装，可继续开发；新环境安装待镜像化或替代分发方案 | 否 |
| RR-6 | 模板禁用交易措辞使用 substring 匹配，未来合法短语可能误报 | P3/v2 | P2 当前输出已测试通过；P3 若调整模板措辞需同步审查 | 否 |
| RR-7 | 缺证附录当前为章节级，不是 item 级证据确认 | v2 | MVP 先保证章节级可追溯，Evidence Confirm 层后续细化 | 否 |
| RR-8 | CLI 端到端真实 PDF/网络路径尚未覆盖 | P3 | P3-S3 用 3 只样本基金端到端矩阵验证 | 否 |
| RR-9 | 真实 `§2` 字段主要位于表格而非冒号文本行 | P3 | P3-S3 已让 profile extractor / fund type classifier 读取键值型表头与数据行，并以 3 只样本基金矩阵覆盖 | 否 |
| RR-10 | 历史低质量 parsed report 缓存污染真实端到端输出 | P3 | P3-S3 已在 parsed report 缓存命中前检查正文长度与关键章节集合，不合格缓存回退为未命中 | 否 |

---

## 6. 后续迭代（非 MVP 范围）

### v2（Week 6-9）

| 功能 | 说明 |
|------|------|
| 严选基金池内横向比较 | 同类型基金择优 |
| LLM 审计 | 证据充分性（E1/E2/E3）+ 内容合规性（C1/C2） |
| 证据复核 | 对 E1/E2 类违规执行二次确认（supported/confirmed_missing） |
| 修复闭环 | patch（局部修补）+ regenerate（整章重建）+ 锚点重写 |
| LLM 写作 | 从模板填充升级为 LLM 生成差异化分析 |

### v3（Week 10-13）

| 功能 | 说明 |
|------|------|
| 组合管理 | 再平衡引擎 + 目标市值策略 |
| 温度计自建 | AKShare + 自行计算 PE/PB 百分位 |
| Web UI | FastAPI + 前端 |
| 微信入口 | 微信消息适配 |

---

## 7. 状态更新日志

| 日期 | Phase | 状态变更 | 备注 |
|------|-------|---------|------|
| 2026-05-16 | 全部 | 创建 | 初始版本 |
| 2026-05-17 | P0 | ✅ done | 全部退出条件满足；项目更名为 fund-agent；数据源改用 akshare + eastmoney |
| 2026-05-17 | P1 | 🟡 in progress | 完成 Git 基线初始化与 baseline reconciliation；下一 gate 为 P1 plan |
| 2026-05-17 | P1 | 🟡 in progress | P1 计划通过 re-review；accepted artifacts 为 `docs/reviews/p1-plan-2026-05-17.md`、`docs/reviews/p1-plan-review-2026-05-17.md`；下一 gate 为 `P1-S1 implementation + review` |
| 2026-05-17 | P1 | 🟡 in progress | `P1-S5` code review / fix / re-review 已收口，accepted slice commit=`8102944`；下一 gate 为 `P1-S6 implementation + review` |
| 2026-05-17 | P1 | 🟡 in progress | `P1-S6` implementation 已完成，`§4/§8/§9` 管理人/持有人 extractor 与测试已落地；当前 gate 维持 `P1-S6 implementation + review` |
| 2026-05-17 | P1 | 🟡 in progress | `P1-S6` controller review 已通过；下一 gate 为 `P1-S7 implementation + review` |
| 2026-05-17 | P1 | 🟡 in progress | `P1-S6` 已接受，accepted commit 为 `18566f9`；下一 gate 为 `P1-S7 implementation + review` |
| 2026-05-17 | P1 | 🟡 in progress | `P1-S7` implementation 已完成，`§8/§10` 持仓/份额 extractor 与测试已落地；当前 gate 维持 `P1-S7 implementation + review` |
| 2026-05-17 | P1 | 🟡 in progress | `P1-S7` controller review 已通过；下一 gate 为 `P1-S8 implementation + review` |
| 2026-05-17 | P1 | 🟡 in progress | `P1-S7` 已接受，accepted commit 为 `3167754`；下一 gate 为 `P1-S8 implementation + review` |
| 2026-05-17 | P1 | 🟡 in progress | `P1-S8` implementation 已完成，façade、净值适配器与 `36/36` 样本矩阵已落地；当前 gate 维持 `P1-S8 implementation + review` |
| 2026-05-17 | P1 | 🟡 in progress | `P1-S8` controller review 已通过；下一 gate 为 `P1 aggregate review` |
| 2026-05-17 | P1 | 🟡 in progress | `P1-S8` 已接受，accepted commit 为 `d398bc2`；下一 gate 为 `P1 aggregate review` |
| 2026-05-17 | P1 | ✅ done | P1 aggregate review 通过，artifact 为 `docs/reviews/p1-aggregate-review-2026-05-17.md`；下一 gate 为 `P2-S1 implementation + review` |
| 2026-05-17 | P2 | 🟡 in progress | 进入 `P2-S1 implementation + review`，优先实现 R=A+B-C 计算模块 |
| 2026-05-17 | P2 | 🟡 in progress | `P2-S1` implementation 与 controller review 已通过；下一 gate 为 `P2-S2 implementation + review` |
| 2026-05-17 | P2 | 🟡 in progress | `P2-S2` implementation 与 controller review 已通过；下一 gate 为 `P2-S3 implementation + review` |
| 2026-05-17 | P2 | 🟡 in progress | `P2-S3` implementation 与 controller review 已通过；下一 gate 为 `P2-S4 implementation + review` |
| 2026-05-17 | P2 | 🟡 in progress | `P2-S4` implementation 与 controller review 已通过；下一 gate 为 `P2-S5 implementation + review` |
| 2026-05-17 | P2 | 🟡 in progress | `P2-S5` implementation 与 controller review 已通过；下一 gate 为 `P2-S6 implementation + review` |
| 2026-05-17 | P2 | 🟡 in progress | `P2-S6` implementation 已完成，压力测试固定场景与基金类型阈值已落地；当前 gate 为 `P2-S6 code review` |
| 2026-05-17 | P2 | 🟡 in progress | `P2-S6` controller review 已通过；外部 reviewer 未产出可采纳 artifact，风险追踪到 `P2 aggregate review`；下一 gate 为 `P2-S7 implementation + review` |
| 2026-05-17 | P2 | 🟡 in progress | `P2-S7` implementation 已完成，7 问题检查清单引擎与测试已落地；当前 gate 为 `P2-S7 code review` |
| 2026-05-17 | P2 | 🟡 in progress | `P2-S7` controller review 已通过；下一 gate 为 `P2-S8 implementation + review` |
| 2026-05-17 | P2 | 🟡 in progress | `P2-S8` implementation 已完成，P1/P2/P3/L1/R1/R2 程序审计与测试已落地；当前 gate 为 `P2-S8 code review` |
| 2026-05-18 | P2 | 🟡 in progress | `P2-S8` controller review 已通过并修复缺少必需输入时静默通过的问题；下一 gate 为 `P2-S9 implementation + review` |
| 2026-05-18 | P2 | 🟡 in progress | `P2-S1` 至 `P2-S8` 已收口为 accepted baseline commit `a6b1516`；`launchd/`、`scripts/` 和旧 P1 review artifact 保持在 P2 基线外；当前 gate 维持 `P2-S9 implementation + review` |
| 2026-05-18 | P2 | 🟡 in progress | `P2-S9` implementation / review / fix / re-review 已通过，8 章模板渲染器和程序审计输入已落地，accepted commit=`bf64b0f`；下一 gate 为 `P2-S10 implementation + review` |
| 2026-05-18 | P2 | 🟡 in progress | `P2-S10` implementation / code review 已通过，证据锚点正文和附录格式已收口，accepted commit=`2d041ae`；下一 gate 为 `P2 aggregate deepreview` |
| 2026-05-18 | P2 | ✅ done | `P2 aggregate deepreview` 已通过，MiMo/GLM 均 PASS；已修复 P2 exit checkbox 文档同步问题；accepted deepreview commit=`07fe0d0`；当前 gate 为 `ready-to-open-draft-PR` |
| 2026-05-18 | P3 | ⬜ pending | P2 退出条件已满足；下一步需用户授权 draft PR gate 后 push 并创建 draft PR，随后再进入 P3 实施 |
| 2026-05-18 | P2 | ✅ done | Draft PR #1 已创建并通过 PR review/fix/re-review；accepted PR review commit=`8f5029c` 已 push；当前 gate 为 `draft-PR-pass` |
| 2026-05-18 | P3 | 🟡 in progress | `P3-S1 implementation + review` 已进入实现；当前代码入口为 Typer，因此 P3-S1 按 current-code alignment 保留 `fund-analysis analyze FUND_CODE` 子命令并通过 Service 层编排 Capability。 |
| 2026-05-18 | P3 | 🟡 in progress | `P3-S1` implementation / code review / fix / re-review 已通过；CLI 通过 Service 层输出 8 章 Markdown，当前验证 `68 passed`；accepted commit=`c5a240c`；下一 gate 为 `P3-S2 implementation + review` |
| 2026-05-18 | P3 | 🟡 in progress | `P3-S2 implementation + review` 已进入实现；温度计 adapter 目标为读取有知有行 `/data` 与 `/data/macro`，提供 24h fresh cache、7 天 stale fallback 和 unavailable 状态，暂不接入 CLI/Service。 |
| 2026-05-18 | P3 | 🟡 in progress | `P3-S2` implementation / code review / controller fix 已通过；温度计 adapter 当前验证 `60 passed` 且真实响应 smoke 可解析全市场、指数、债市与 10 年期国债到期收益率；accepted commit=`1747aaf`；下一 gate 为 `P3-S3 implementation + review` |
| 2026-05-18 | P3 | 🟡 in progress | `P3-S3 implementation` 已完成；新增 3 只样本基金 CLI 端到端矩阵并修复真实表格抽取、低质量 parsed cache 复用和模板基准字段契约错配；当前验证 `33 passed`；下一 gate 为 `P3-S3 code review` |
| 2026-05-18 | P3 | 🟡 in progress | `P3-S3` implementation / controller code review 已通过；新增 3 只样本基金 CLI 端到端矩阵并修复真实表格抽取、低质量 parsed cache 复用和模板基准字段契约错配；当前验证 `115 passed` 且 `git diff --check` 通过；accepted commit=`e0b1b93`；下一 gate 为 `P3-S4 implementation + review` |
| 2026-05-18 | P3 | 🟡 in progress | `P3-S4 implementation` 已完成；P3 CLI 端到端矩阵现在显式记录真实 Service 返回值，并断言 P1/P2/P3/L1/R1/R2 全部程序审计规则执行通过；当前验证 `26 passed`；下一 gate 为 `P3-S4 code review` |
| 2026-05-18 | P3 | 🟡 in progress | `P3-S4` implementation / controller code review 已通过；P3 CLI 端到端矩阵已验证 3 只样本基金的 `audit_result.passed`、`checked_rules == P1/P2/P3/L1/R1/R2` 和空 issues；当前验证 `115 passed` 且 `git diff --check` 通过；accepted implementation commit=`caf5b31`；下一 gate 为 `P3-S5 implementation + review` |
| 2026-05-18 | P3 | 🟡 in progress | `P3-S5 implementation` 已完成；P3 CLI 端到端矩阵现在断言每份报告 8 章正文证据行、关键附录来源锚点和无缺证占位；当前验证 `1 passed`；下一 gate 为 `P3-S5 code review` |
| 2026-05-18 | P3 | 🟡 in progress | `P3-S5` implementation / controller code review 已通过；P3 CLI 端到端矩阵已验证每份报告 8 章正文证据行、关键附录来源锚点和无缺证占位；当前验证 `24 passed` 且 `git diff --check` 通过；accepted commit=`46432c0`；下一 gate 为 `P3-S6 implementation + review` |
| 2026-05-18 | P3 | 🟡 in progress | `P3-S6 implementation` 已完成；根 README 已按当前 CLI 成功路径更新为用户手册，并移除过期端到端矩阵状态；当前验证 `fund-analysis --help`、`fund-analysis analyze --help` 和 `git diff --check` 通过；下一 gate 为 `P3-S6 code review` |
| 2026-05-18 | P3 | 🟡 in progress | `P3-S6` implementation / controller code review 已通过；根 README 已按当前 CLI 成功路径更新为用户手册，文档导航均指向真实文件；当前验证 `fund-analysis --help`、`fund-analysis analyze --help` 和 `git diff --check` 通过；accepted commit=`8904588`；下一 gate 为 `P3-S7 implementation + review` |
| 2026-05-18 | P3 | 🟡 in progress | `P3-S7 implementation` 已完成；dev 依赖和测试手册新增覆盖率 gate，当前 `fund_agent` 总覆盖率 `90.07%`，超过 50% 目标；当前验证 `115 passed`；下一 gate 为 `P3-S7 code review` |
| 2026-05-18 | P3 | 🟡 in progress | `P3-S7` implementation / controller code review 已通过；dev 依赖和测试手册新增覆盖率 gate，当前 `fund_agent` 总覆盖率 `90.07%`，超过 50% 目标；当前验证 `115 passed`；accepted commit=`d1d506b`；下一 gate 为 `P3-S8 implementation + review` |
