# Fund-Agent 仓库级综合审核报告

> **审核日期**: 2026-05-27
> **审核范围**: 全仓库代码、文档、测试、配置
> **分支**: `codex/local-reconciliation`
> **基线**: `origin/main` at `44ea955`
> **HEAD**: `f88a3aa`
> **相对基线**: ahead 21 commits
> **审核性质**: 只读审核，零代码改动

---

## 1. 执行摘要

本次审核对 `fund-agent` 仓库进行了严格深度审核，覆盖代码、文档、测试、配置及所有 review artifact。审核基于第一性原理：从项目核心目标（"让 LLM 从基金年报中提取信息并生成可审计的分析报告"）出发，逐层验证当前实现与真源文档的一致性。

**核心结论**：

- **当前代码状态健康**：全部 789 个测试通过（较上次审核 +63），`ruff` 零告警，`git diff --check` 通过
- **无阻塞性发现**：无 blocking findings，当前 gate 可继续推进
- **当前 gate**: `source provenance primary-failure-category propagation implementation accepted locally`
- **下一入口**: `source provenance post-implementation bounded evidence rerun plan/review gate; must use init-agents / tmux multi-agent flow`
- **完备可用功能**: CLI 三命令（`analyze`, `checklist`, `thermometer`）+ 报告质量验证器 + 章节契约审计 sidecar + 来源可追溯性（source provenance）

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
- **Fund 层**: 核心基金领域能力包，包含提取器、审计器、模板、渲染器、来源可追溯性

### 2.2 当前 Gate 状态

| 字段 | 状态 |
|---|---|
| Branch | `codex/local-reconciliation` |
| Current phase | `release maintenance` |
| Current gate | `source provenance primary-failure-category propagation implementation accepted locally` |
| Next entry point | `source provenance post-implementation bounded evidence rerun plan/review gate; must use init-agents / tmux multi-agent flow` |
| Latest accepted gate checkpoint | `source provenance primary-failure-category propagation implementation local accepted commit; use latest branch HEAD for exact hash` |
| Design truth | `docs/design.md` (v2.2) |
| Control truth | `docs/implementation-control.md` |

### 2.3 验证矩阵

| 检查项 | 命令 | 结果 |
|---|---|---|
| 代码风格 | `uv run ruff check .` | PASS (All checks passed!) |
| 测试 | `uv run pytest -q` | PASS (**789 passed** in 2.04s) |
| 锁文件 | `uv lock --check` | PASS (Resolved 75 packages) |
| 空白字符 | `git diff --check` | PASS |

---

## 3. 自上次审核以来的重大进展

### 3.1 新增核心功能

| 功能 | 模块 | 状态 |
|---|---|---|
| **来源可追溯性（Source Provenance）** | `fund_agent/fund/source_provenance.py` | 已实现，测试通过 |
| **主来源失败分类传播** | `fund_agent/fund/documents/models.py` + `sources.py` | 已实现 |
| **章节契约约束 sidecar** | `fund_agent/fund/template/chapter_contract_constraints.py` | 已实现，20 测试通过 |
| **报告写作审计** | `fund_agent/fund/report_writing_audit.py` | 已实现，16 测试通过 |
| **报告质量评估脚本** | `scripts/report_quality_eval.py` | 已实现，dev-only |

### 3.2 关键修复

| 修复 | 影响 |
|---|---|
| 份额变动提取器（S2）修复 | `holdings_share_change.py` 新增 basic_identity 字段和 fee_schedule fallback |
| 渲染器禁用词策略升级 | 从全局字符串匹配升级为短语匹配 + 正则模式，避免误杀年报原文引用 |
| 验证器多 bundle JSONL 修复 | `RQV_REF_MISSING` 问题已解决 |
| 质量 gate 年份范围修正 | correctness 评分年份覆盖范围修正 |
| 核心 analyze/checklist 可靠性加固 | 生产路径错误处理增强 |

### 3.3 测试增长

| 时间 | 测试数 | 新增 |
|---|---|---|
| 上次审核 (2026-05-26) | 726 | - |
| 本次审核 (2026-05-27) | **789** | **+63** |

---

## 4. 完备可用功能清单

### 4.1 用户可用功能（CLI）

| 命令 | 功能 | 状态 | 备注 |
|---|---|---|---|
| `fund-analysis analyze <code> --report-year <year>` | 生成基金分析报告 | 可用 | 004393/2024 通过，quality_gate_status: warn |
| `fund-analysis checklist <code> --report-year <year>` | 生成基金检查清单 | 可用 | 同上 |
| `fund-analysis thermometer --json` | 输出基金温度计 JSON | 可用 | 有效 JSON 输出 |

### 4.2 开发者可用功能

| 模块 | 功能 | 状态 |
|---|---|---|
| `fund_agent/fund/source_provenance.py` | 来源可追溯性投影 | 可用，测试通过 |
| `fund_agent/fund/report_quality_validation.py` | 报告质量验证器 | 可用，已通过多轮 review |
| `fund_agent/fund/report_evidence.py` | 报告证据 bundle 模型 | 可用 |
| `fund_agent/fund/report_writing_audit.py` | 报告写作审计 | 可用，active Chapter 3 已调优 |
| `fund_agent/fund/template/chapter_contract_constraints.py` | 章节契约约束 sidecar | 可用 |
| `scripts/report_quality_eval.py` | 报告质量评估脚本 | 可用，dev-only 工具 |

### 4.3 已完成的 Gate（自上次审核以来新增）

| Gate | 状态 | 关键产出 |
|---|---|---|
| Source provenance design | Accepted | 来源可追溯性设计文档 |
| Source provenance implementation | Accepted | `source_provenance.py` + `models.py` 元数据扩展 |
| Source provenance primary-failure-category propagation | Accepted | 失败分类从来源传播到公共输出 |
| Renderer minimal integration design | Accepted | active-fund Chapter 3 渲染器设计 |
| Renderer minimal integration implementation | Accepted | 渲染器集成实现 |
| Core analyze/checklist reliability hardening | Accepted | 生产路径错误处理增强 |
| Share-change focused implementation | Accepted | 份额变动提取修复 |
| Quality gate correctness year scope | Accepted | 年份覆盖修正 |
| Index/QDII source recovery | Accepted | 指数/QDII 来源恢复 |
| Bond lens contract baseline coverage | Accepted | 债券 lens 契约基线覆盖 |
| Bond lens score applicability | Accepted | 债券评分适用性 |
| Small baseline corpus v1 | Accepted | 小基线语料库 v1 |

---

## 5. 审核发现

### 5.1 Material Findings（重要但不阻塞）

#### 5.1.1 design.md 禁用词口径落后（重复发现，仍未修复）

- **位置**: `docs/design.md:670`
- **问题**: 仍描述旧的全局字符串匹配逻辑，未反映当前实现（短语匹配 + 正则模式 + 允许年报披露语境）
- **影响**: 真源文档与代码事实不一致，可能误导后续 Agent
- **建议**: 更新为"校验直接交易建议与明确配置指令（禁用短语 + 正则模式），允许年报披露语境"
- **是否阻塞**: 否，文档债务

#### 5.1.2 design.md 温度计措辞口径模糊（重复发现，仍未修复）

- **位置**: `docs/design.md:1072`
- **问题**: "温度计不得输出买入卖出或仓位比例"表述可能被理解为全局禁用
- **影响**: 与 renderer 实现不一致
- **建议**: 明确为"直接交易建议"
- **是否阻塞**: 否，文档债务

#### 5.1.3 CI 覆盖率阈值与 AGENTS.md 不一致（历史问题）

- **位置**: `tests/test_repo_hygiene.py:13`
- **问题**: `--cov-fail-under=50` 与 AGENTS.md "单文件测试覆盖率目标 ≥80%" 不一致
- **影响**: CI gate 偏松，但当前全局覆盖率实际已在 90%+
- **建议**: 后续 coverage policy reconciliation
- **是否阻塞**: 否

### 5.2 Minor Findings（次要）

#### 5.2.1 审计规则码口径不一致

- **位置**: AGENTS.md vs `fund_agent/fund/audit/audit_programmatic.py`
- **问题**: AGENTS.md 声明 `P1/P2/E1/E2/E3/C1/L1/L2/R1/R2`，实际代码 `P1/P2/P3/C2/L1/R1/R2`
- **建议**: 后续文档/设计里明确三层审计完整目标 vs MVP Programmatic 已实现规则
- **是否阻塞**: 否

#### 5.2.2 硬编码错误码字符串

- **位置**: `fund_agent/fund/report_quality_validation.py`
- **问题**: 存在 `"RQV_FIELD_MISSING"` 等硬编码错误码标识
- **分析**: MVP 阶段合理折中，测试已覆盖
- **建议**: 后续 robustness gate 可考虑配置化
- **是否阻塞**: 否

### 5.3 边界合规性验证

| 检查项 | 结果 | 说明 |
|---|---|---|
| FundDocumentRepository 边界 | PASS | 所有文档访问仍通过统一接口，无直接文件系统操作 |
| 四层架构边界 | PASS | UI/Service/Fund 分层清晰，无 Host/Agent 占位包 |
| 来源 fallback 分类 | PASS | `not_found`/`unavailable` 允许 fallback，`schema_drift`/`identity_mismatch`/`integrity_error` fail-closed |
| Source provenance 边界 | PASS | 只投影已暴露的元数据，不读取来源策略内部实现 |
| 显式参数传递 | PASS | 无 `extra_payload` 绕过 |
| 禁用词策略 | PASS | 短语匹配 + 正则模式，允许年报披露语境 |

---

## 6. 残余风险

| 风险 | 所有者 | 阻塞？ |
|---|---|---|
| Renderer minimal integration 未完全接入产品流 | 未来 design gate | 否 |
| Chapter 2 enhanced-index 和 Chapter 6 bond 约束仍为 `config_only` | 未来 data extraction gate | 否 |
| Clean baseline 仍缺少纯 FOF 样本 | 未来 corpus selection gate | 否 |
| Records-mode audit 仍较窄且 fail-closed | 未来 dev-only corpus gate | 否 |
| 更广泛的 NL claim coverage | 未来 dev-only corpus gate | 否 |
| Duplicate occurrence-level `issue_id` 唯一性 | 未来 audit-output ergonomics slice | 否 |
| Per-file 覆盖率测量受 numpy import 问题影响 | 已知，有替代验证 | 否 |

---

## 7. 推荐下一步行动

1. **继续当前 gate**: 当前状态健康，无阻塞项，建议 continue current gate
2. **执行 source provenance post-implementation bounded evidence rerun**: 按 implementation-control.md 要求，使用 init-agents / tmux multi-agent flow
3. **同步 design.md 措辞口径**: 第 670 行、第 1072 行（非阻塞，可并行）
4. **审计规则码和覆盖率阈值**: 放入后续候选 backlog

---

## 8. 审核方法论

本次审核遵循以下原则：

1. **第一性原理**: 从项目核心目标出发，不假设作者知晓一切
2. **真源文档优先**: 以 `AGENTS.md`、`docs/design.md`、`docs/implementation-control.md` 为唯一权威
3. **代码事实为准**: 文档与代码不一致时，以代码为准，记录为文档债务
4. **分层边界检查**: 所有发现均显式对照 UI/Service/Host/Agent 四层边界
5. **证据链完整**: 每个发现均附带具体文件位置、验证命令、影响分析
6. **零代码改动**: 纯审核，不修改任何代码

---

## 9. Sign-off

- **审核日期**: 2026-05-27
- **审核范围**: 全仓库
- **代码改动**: 0 文件
- **Blocking Findings**: 0
- **Material Findings**: 3（均为文档债务，其中 2 个为重复发现）
- **Minor Findings**: 2
- **边界合规性**: 全部通过
- **裁决**: 当前变更不偏离目标，可继续开发。建议 continue current gate。
