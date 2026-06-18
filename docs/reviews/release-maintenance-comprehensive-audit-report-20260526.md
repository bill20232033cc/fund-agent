# Fund-Agent 仓库级综合审核报告

> **审核日期**: 2026-05-26
> **审核范围**: 全仓库代码、文档、测试、配置
> **分支**: `codex/local-reconciliation`
> **基线**: `origin/main` at `44ea955`
> **HEAD**: `f5b91ad`
> **审核性质**: 只读审核，零代码改动

---

## 1. 执行摘要

本次审核对 `fund-agent` 仓库进行了严格深度审核，覆盖代码、文档、测试、配置及所有 review artifact。审核基于第一性原理：从项目核心目标（"让 LLM 从基金年报中提取信息并生成可审计的分析报告"）出发，逐层验证当前实现与真源文档的一致性。

**核心结论**：

- **当前代码状态健康**：全部 697 个测试通过，`ruff` 零告警，`git diff --check` 通过
- **无阻塞性发现**：无 blocking findings，当前 gate 可继续推进
- **当前 gate**: `dev-only chapter audit × small baseline corpus evaluation accepted locally`
- **下一入口**: `renderer minimal integration design gate`（仅限设计，不授权实现）
- **完备可用功能**: CLI 三命令（`analyze`, `checklist`, `thermometer`）+ 报告质量验证器 + 章节契约审计 sidecar

---

## 2. 项目当前状态

### 2.1 架构状态

当前生产主链路为确定性 CLI 实现，采用 Dayu 四层架构设计：

```
UI (CLI) -> Service -> fund_agent/fund (Agent 层基金能力)
```

- **Host 层**: 尚未接入，占位包未创建（符合 AGENTS.md 硬约束）
- **Agent 执行内核**: 尚未接入 `dayu.engine`（符合当前 gate 非目标）
- **Service 层**: `fund_agent/services/fund_analysis_service.py` 稳定
- **Fund 层**: 核心基金领域能力包，包含提取器、审计器、模板、渲染器

### 2.2 当前 Gate 状态

| 字段 | 状态 |
|---|---|
| Branch | `codex/local-reconciliation` |
| Current phase | `release maintenance` |
| Current gate | `dev-only chapter audit × small baseline corpus evaluation accepted locally` |
| Next entry point | `renderer minimal integration design gate; active-fund Chapter 3 only; no implementation/product-flow integration authorized` |
| Latest accepted gate checkpoint | `f5b91ad` |

### 2.3 验证矩阵

| 检查项 | 命令 | 结果 |
|---|---|---|
| 代码风格 | `uv run ruff check .` | PASS (All checks passed!) |
| 测试 | `uv run pytest -q` | PASS (697 passed in 1.93s) |
| 锁文件 | `uv lock --check` | PASS (Resolved 75 packages) |
| 空白字符 | `git diff --check` | PASS |
| CLI analyze | `uv run fund-analysis analyze 004393 --report-year 2024 --quality-gate-policy block` | PASS (exit 0, quality_gate_status: warn) |
| CLI checklist | `uv run fund-analysis checklist 004393 --report-year 2024` | PASS (exit 0, quality_gate_status: warn) |
| CLI thermometer | `uv run fund-analysis thermometer --json` | PASS (exit 0, JSON valid) |
| 审计测试 | `uv run pytest tests/fund/test_report_writing_audit.py` | PASS (16 passed) |
| Sidecar + 审计 | `uv run pytest tests/fund/template/test_chapter_contract_constraints.py tests/fund/test_report_writing_audit.py` | PASS (20 passed) |

---

## 3. 完备可用功能清单

### 3.1 用户可用功能（CLI）

| 命令 | 功能 | 状态 | 备注 |
|---|---|---|---|
| `fund-analysis analyze <code> --report-year <year>` | 生成基金分析报告 | 可用 | 004393/2024 通过，quality_gate_status: warn |
| `fund-analysis checklist <code> --report-year <year>` | 生成基金检查清单 | 可用 | 同上 |
| `fund-analysis thermometer --json` | 输出基金温度计 JSON | 可用 | 有效 JSON 输出 |

### 3.2 开发者可用功能

| 模块 | 功能 | 状态 |
|---|---|---|
| `fund_agent/fund/report_quality_validation.py` | 报告质量验证器 | 可用，已通过多轮 review |
| `fund_agent/fund/report_evidence.py` | 报告证据 bundle 模型 | 可用 |
| `fund_agent/fund/report_writing_audit.py` | 报告写作审计 | 可用，active Chapter 3 已调优 |
| `fund_agent/fund/template/chapter_contract_constraints.py` | 章节契约约束 sidecar | 可用 |
| `scripts/report_quality_eval.py` | 报告质量评估脚本 | 可用，dev-only 工具 |

### 3.3 已完成的 Gate

| Gate | 状态 | 关键产出 |
|---|---|---|
| Report-quality validator design | Accepted | 验证器设计文档 |
| Report-quality validator implementation | Accepted | `report_quality_validation.py` |
| Report-quality validator quasi-real bundle | Accepted | 准真实 bundle 消费验证 |
| Small baseline real evaluation | Accepted | 3 只基金真实评估 |
| First improvement slice | Accepted | 验证器多 bundle JSONL 修复 |
| Chapter contract writing upgrade design | Accepted | 章节契约升级设计 |
| Chapter contract sidecar implementation | Accepted | `chapter_contract_constraints.py` + `report_writing_audit.py` |
| Dev-only chapter audit × small baseline | Accepted | 16 项审计测试通过，假阳性已修复 |

---

## 4. 审核发现

### 4.1 Material Findings（重要但不阻塞）

#### 4.1.1 design.md 禁用词口径落后

- **位置**: `docs/design.md:670`
- **问题**: 仍描述旧的全局字符串匹配逻辑（"校验禁用词（买入/卖出/仓位比例/收益预测）"），未反映当前实现（短语匹配 + 正则模式 + 允许年报披露语境）
- **影响**: 真源文档与代码事实不一致，可能误导后续 Agent
- **建议**: 更新为"校验直接交易建议与明确配置指令（禁用短语 + 正则模式），允许年报披露语境"
- **是否阻塞**: 否，文档债务

#### 4.1.2 design.md 温度计措辞口径模糊

- **位置**: `docs/design.md:1072`
- **问题**: "温度计不得输出买入卖出或仓位比例"表述可能被理解为全局禁用
- **影响**: 与 renderer 实现不一致
- **建议**: 明确为"直接交易建议"
- **是否阻塞**: 否，文档债务

#### 4.1.3 CI 覆盖率阈值与 AGENTS.md 不一致

- **位置**: `tests/test_repo_hygiene.py:13`
- **问题**: `--cov-fail-under=50` 与 AGENTS.md "单文件测试覆盖率目标 ≥80%" 不一致
- **影响**: CI gate 偏松，但当前全局覆盖率实际已在 90%+
- **建议**: 后续 coverage policy reconciliation
- **是否阻塞**: 否

### 4.2 Minor Findings（次要）

#### 4.2.1 审计规则码口径不一致

- **位置**: AGENTS.md vs `fund_agent/fund/audit/audit_programmatic.py`
- **问题**: AGENTS.md 声明 `P1/P2/E1/E2/E3/C1/L1/L2/R1/R2`，实际代码 `P1/P2/P3/C2/L1/R1/R2`
- **建议**: 后续文档/设计里明确三层审计完整目标 vs MVP Programmatic 已实现规则
- **是否阻塞**: 否

#### 4.2.2 硬编码错误码字符串

- **位置**: `fund_agent/fund/report_quality_validation.py`
- **问题**: 存在 `"RQV_FIELD_MISSING"` 等硬编码错误码标识
- **分析**: MVP 阶段合理折中，测试已覆盖
- **建议**: 后续 robustness gate 可考虑配置化
- **是否阻塞**: 否

### 4.3 已拒绝的 Findings（历史审核中已裁决）

| Finding | 裁决 | 理由 |
|---|---|---|
| "测试只覆盖 happy path" | Rejected | 19+ 个 fail-closed 测试用例已验证 |
| "存在 tracked scratch 文件" | Rejected | 仅 1 个 untracked review artifact |
| "引入 dayu.host / dayu.engine" | Rejected | 代码搜索确认未引入任何 dayu 依赖 |
| "report-quality validator 与 FQ0-FQ6 混淆" | Rejected | 模块级 docstring 明确声明不替代 FQ0-FQ6 |
| "FundDocumentRepository 边界被绕过" | Rejected | 验证器只消费内存 bundle，不读取文档 |
| "renderer / FQ0-FQ6 被意外改变" | Rejected | git diff 确认未触及 renderer 或 FQ0-FQ6 |
| "旧六层/Runtime/Engine 口径被当成当前架构" | Rejected | 当前代码和文档均统一使用 Dayu 四层 |

---

## 5. 残余风险

| 风险 | 所有者 | 阻塞？ |
|---|---|---|
| Renderer minimal integration 未实现 | 未来 design gate | 否 |
| Chapter 2 enhanced-index 和 Chapter 6 bond 约束仍为 `config_only` | 未来 data extraction gate | 否 |
| Clean baseline 仍缺少 index、QDII、纯 FOF 样本 | 未来 corpus selection gate | 否 |
| Records-mode audit 仍较窄且 fail-closed | 未来 dev-only corpus gate | 否 |
| 更广泛的 NL claim coverage | 未来 dev-only corpus gate | 否 |
| Duplicate occurrence-level `issue_id` 唯一性 | 未来 audit-output ergonomics slice | 否 |
| Per-file 覆盖率测量受 numpy import 问题影响 | 已知，有替代验证 | 否 |

---

## 6. 推荐下一步行动

1. **继续当前 gate**: 当前状态健康，无阻塞项，建议 continue current gate
2. **同步 design.md 措辞口径**: 第 670 行、第 1072 行（非阻塞，可并行）
3. **推进 renderer minimal integration design**: 仅限 active-fund Chapter 3，仅限设计阶段
4. **审计规则码和覆盖率阈值**: 放入后续候选 backlog

---

## 7. 审核方法论

本次审核遵循以下原则：

1. **第一性原理**: 从项目核心目标出发，不假设作者知晓一切
2. **真源文档优先**: 以 `AGENTS.md`、`docs/design.md`、`docs/implementation-control.md` 为唯一权威
3. **代码事实为准**: 文档与代码不一致时，以代码为准，记录为文档债务
4. **分层边界检查**: 所有发现均显式对照 UI/Service/Host/Agent 四层边界
5. **证据链完整**: 每个发现均附带具体文件位置、验证命令、影响分析
6. **零代码改动**: 纯审核，不修改任何代码

---

## 8. Sign-off

- **审核日期**: 2026-05-26
- **审核范围**: 全仓库
- **代码改动**: 0 文件
- **Blocking Findings**: 0
- **Material Findings**: 3（均为文档债务）
- **Minor Findings**: 2
- **裁决**: 当前变更不偏离目标，可继续开发。建议 continue current gate。
