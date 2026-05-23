# 基金行为教练 Agent —— 实施总控文档

> **版本**: v2.0
> **日期**: 2026-05-21
> **设计真源**: `docs/design.md`（v2.0，与代码同步）
> **定性模板**: `docs/fund-analysis-template-draft.md`（v2）
> **P4 质量体系**: `docs/implementation-control-p4.md`
> **仓库**: `https://github.com/bill20232033cc/fund-agent`（main 分支）

---

## 1. 当前状态

### 1.1 项目阶段

**MVP 已完成（P0-P7 全部合入 main）**。当前处于 MVP 交付后、v2 规划前的稳定期。

| 指标 | 值 |
|------|-----|
| 总 commit 数 | 55+ |
| 已合入 Phase | P0-P7 |
| 已关闭 PR | 4 个（PR#1-P4） |
| Open issues | 0 |
| 最后推送 | 2026-05-20 |

### 1.2 Phase 完成记录

| Phase | 名称 | 状态 | 合入 PR | 实际内容 |
|-------|------|------|---------|---------|
| P0 | 环境搭建与架构骨架 | ✅ done | — | 项目骨架、pyproject.toml、CLI 占位 |
| P1 | 数据层（PDF 下载 + 解析 + 提取） | ✅ done | PR#1 | PDF 下载/解析、年报章节定位、12 项数据提取、净值获取 |
| P2 | 模板渲染与证据锚点 | ✅ done | PR#2 | 8 章模板渲染器、CHAPTER_CONTRACT、ITEM_RULE、证据锚点 |
| P3 | CLI 集成与端到端门控 | ✅ done | PR#3 | Typer CLI、Service 编排、程序审计集成、温度计 |
| P4 | 质量闭环 | ✅ done | PR#4 | extraction_snapshot、extraction_score、quality_gate（FQ0-FQ6）、golden_answer |
| P5 | 质量门控主线集成 | ✅ done | — | quality_gate 集成到 FundAnalysisService、FQ5/FQ6 规则、post-MVP 基础设施验证 |
| P6 | 模板契约机器审计 | ✅ done | — | TemplateContractManifest、C2 审计规则（44 required + 9 forbidden）、ITEM_RULE 评估 |
| P7 | 文档仓库源抽象 | ✅ done | — | FundDocumentRepository、多源适配（EID + 东方财富）、source metadata |

### 1.3 里程碑达成

| 里程碑 | 目标 | 实际达成 | 验收 |
|--------|------|---------|------|
| M1: 架构就绪 | 三层骨架可运行 | P0 完成 | ✅ |
| M2: 数据管道可用 | 12 项关键数据提取 | P1 完成 | ✅ |
| M3: 分析引擎可用 | R=A+B-C + 检验 + 审计 | P2 完成 | ✅ |
| M4: MVP 交付 | `fund-analysis <code>` 输出 8 章报告 | P3 完成 | ✅ |
| M5: 质量闭环 | 精选基金池抽取质量可量化 | P4 完成 | ✅ |
| M6: 契约审计 | CHAPTER_CONTRACT 程序化校验 | P6 完成 | ✅ |

---

## 2. 已实现的架构与能力

> 以下为简要概述，详细设计见 `docs/design.md`。

### 2.1 三层架构（非原计划四层）

原计划采用四层架构（UI → Service → Host → Agent/Engine），实际实现为三层纯 Python 架构：

```
UI（Typer CLI）→ Service（7 个服务）→ Capability（基金领域知识）
```

**关键偏差**：MVP 阶段不依赖 LLM，因此 Host/Engine 层未接入。`pyproject.toml` 声明了 `dayu-agent` 依赖，但代码零导入。

### 2.2 已实现能力清单

| 能力域 | 模块 | 关键文件 |
|--------|------|---------|
| CLI 入口 | `ui/cli.py` | Typer，3 个命令（analyze / checklist / thermometer） |
| Service 编排 | `services/` | 7 个服务（analysis / snapshot / score / gate / golden_prefill / golden_answer / thermometer） |
| 文档仓库 | `fund/documents/` | repository / cache / sources / adapters（统一入口，禁止直接文件操作） |
| 结构化抽取 | `fund/extractors/` | profile / performance / manager_ownership / holdings_share_change |
| 基金类型识别 | `fund/fund_type.py` | 6 种类型（index / active / bond / enhanced_index / qdii / fof） |
| R=A+B-C 归因 | `fund/analysis/r_abc.py` | 结构性 vs 阶段性超额判断 |
| 言行一致性 | `fund/analysis/consistency_check.py` | 4 维度信号（风格/行业/仓位/换手） |
| 投资者获得感 | `fund/analysis/investor_return.py` | 行为损益 + 资金流向 |
| 否决项 + 压力测试 | `fund/analysis/risk_check.py` | 5 项否决 + 3 场景压力测试 |
| 检查清单 | `fund/analysis/checklist.py` | 7 问题红/黄/绿灯 |
| 模板系统 | `fund/template/` | contracts（932 行）+ item_rules（563 行）+ renderer（1035 行） |
| 程序审计 | `fund/audit/` | P1/P2/P3/C2/L1/R1/R2 规则 |
| 质量门控 | `fund/quality_gate.py` | FQ0-FQ6 规则 + golden answer correctness |
| 外部数据 | `fund/data/` | 净值（akshare）+ 温度计（有知有行公开页面） |

### 2.3 技术选型（与原计划对比）

| 项目 | 原计划 | 实际 | 偏差原因 |
|------|--------|------|---------|
| 架构层数 | 四层 | 三层 | MVP 不依赖 LLM |
| CLI 框架 | argparse | Typer | 类型注解友好 |
| HTTP 库 | requests | httpx | 异步支持 |
| PDF 解析 | pdfplumber | pdfplumber | 一致 |
| 年报来源 | 巨潮资讯网 | EID 巨潮 + 东方财富 fallback | 提高可用性 |
| 缓存 | 文件 + SQLite | PDF 文件 + parsed report JSON | 更简单 |
| 模板渲染 | 待定 | 纯 Python 函数 | MVP 确定性管线 |

---

## 3. P4 质量体系（独立文档）

P4-P7 的详细实施控制记录在 `docs/implementation-control-p4.md` 中，包含：

- P4-S1 ~ P4-S3b：extraction_snapshot / extraction_score / quality_gate
- P5-S1 ~ P5-S7：质量门控主线集成
- P6-S1 ~ P6-S5：模板契约机器审计
- P7-S1 ~ P7-S4：文档仓库源抽象

---

## 4. 已解决的阻塞问题

| ID | 问题 | 影响 Phase | 状态 | 实际决议 |
|----|------|-----------|------|---------|
| BQ-1 | 巨潮网反爬策略 | P0/P1 | ✅ closed | 使用 EID 巨潮 + 东方财富 fallback，httpx 下载 |
| BQ-2 | 2026 新规"投资者收益率"披露 | P1/P2 | ✅ closed | 先用份额变动估算，新规落地后切换 |
| BQ-3 | 有知有行温度数据页面结构 | P3 | ✅ closed | httpx + HTML 解析，24h 缓存 |
| BQ-4 | akshare 基金净值 API 稳定性 | P1 | ✅ closed | akshare 为主，备用天天基金直接 API |
| BQ-5 | Dayu-Agent 零导入但声明依赖 | P0-P7 | ✅ closed | pyproject.toml 保留依赖声明，代码不导入，v2 接入 |

---

## 5. 残余风险

| ID | 风险 | 当前状态 | 需要人类裁决？ |
|----|------|---------|--------------|
| RR-1 | PDF 格式不统一导致解析失败 | 已有兜底策略（extraction_mode=missing） | 否 |
| RR-2 | 超额收益性质判断主观性强 | MVP 用规则引擎，v2 引入 LLM | 否 |
| RR-3 | 审计规则过严导致频繁阻断 | C2 规则 44+9 条已校准 | 否 |
| RR-4 | 温度计页面变更导致获取失败 | 24h 缓存 + 异常处理 | 是（如被封锁需人工确认） |
| RR-5 | Dayu-Agent 版本升级破坏兼容性 | 当前零导入，不受影响 | 否（v2 接入时需评估） |
| RR-6 | 精选基金池 CSV 手动维护成本 | 当前 6 只基金，可接受 | 是（扩展时需自动化） |

---

## 6. 已知技术债

| ID | 债务 | 来源 | 优先级 | 说明 |
|----|------|------|--------|------|
| TD-1 | type:ignore 注释 | repo-audit-20260520 P1 | 高 | `cli.py` 中存在 `# type: ignore` 注释，应修复类型 |
| TD-2 | 魔法数字 | repo-audit-20260520 P2 | 中 | 多处硬编码阈值（如 0.9、0.2、0.35），应提取为常量 |
| TD-3 | 串行抽取 | repo-audit-20260520 P2 | 中 | 精选基金池抽取为串行，大批量时性能差 |
| TD-4 | 本地路径依赖 | repo-audit-20260520 P2 | 中 | 默认路径硬编码（如 `docs/code_20260519.csv`），应可配置 |
| TD-5 | tools/ 占位模块 | design.md | 低 | `fund/tools/` 下有空占位文件，v2 LLM 阶段使用 |
| TD-6 | audit 辅助文件未清理 | repo-audit-20260520 | 低 | `audit_coordinator.py`、`audit_rules.py`、`models.py` 存在但未被主流程引用 |

---

## 7. 后续迭代规划

> 以下为方向性规划，具体 Phase 定义在启动时创建。

### v2：LLM 写作 + Dayu-Agent 接入

| 功能 | 说明 | 前置条件 |
|------|------|---------|
| Dayu-Agent 运行时接入 | Engine/Host/Prompting 体系 | Dayu-Agent API 稳定 |
| LLM 审计 | 证据充分性（E1/E2/E3）+ 内容合规性（C1） | LLM API 可用 |
| 证据复核 | 对 E1/E2 类违规执行二次确认 | LLM 审计就绪 |
| 修复闭环 | patch（局部修补）+ regenerate（整章重建） | 审计闭环就绪 |
| LLM 写作 | 从模板填充升级为 LLM 生成差异化分析 | Dayu-Agent 接入 |
| 严选基金池横向比较 | 同类型基金择优 | 数据层稳定 |

### v3：产品化

| 功能 | 说明 |
|------|------|
| 组合管理 | 再平衡引擎 + 目标市值策略 |
| 温度计自建 | AKShare + 自行计算 PE/PB 百分位 |
| Web UI | FastAPI + 前端 |
| 微信入口 | 微信消息适配 |

---

## 8. 状态更新日志

| 日期 | 变更 | 备注 |
|------|------|------|
| 2026-05-16 | v1.0 创建 | 初始版本，P0-P3 规划 |
| 2026-05-17 | P1 完成 | PR#1 合入，数据层可用 |
| 2026-05-18 | P2/P3 完成 | PR#2/PR#3 合入，MVP 交付 |
| 2026-05-19 | P4 完成 | PR#4 合入，质量闭环 |
| 2026-05-20 | P5/P6/P7 完成 | 质量门控集成 + 契约审计 + 文档仓库源抽象 |
| 2026-05-21 | v2.0 重写 | 从"未来计划"改为"已完成记录 + 当前状态"，与 design.md v2.0 对齐 |
