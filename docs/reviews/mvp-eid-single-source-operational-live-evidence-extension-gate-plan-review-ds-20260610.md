# EID Single Source Operational Live Evidence Extension Gate — Plan Review (AgentDS)

## 审查结论

**Verdict: PASS_WITH_FINDINGS**

无阻塞性发现。以下发现按严重度排列，均不构成 BLOCKED，但建议在进入 live command 前处理或记录为已知 residual risk。

---

## Finding 1 — MEDIUM：not_found 行级继续缺少聚合 sanity check

**参考**：plan §Row-Level Outcome Rules，continuation rules 第 2 条

**问题**：plan 规定 `blocked_not_found` 时记录 residual 并继续下一行，理由是"行级 EID 发现缺失，不授权 fallback"。这个单行逻辑本身正确——不同 fund_code 在 EID 中的可用性确实独立。

但 plan 未包含聚合 sanity check：如果全部 4 行都返回 `not_found`，该结果存在两种互斥解释：
- 4 只基金的年报确实都不在 EID 中（真阴性）
- EID API 响应格式已漂移，但现有代码将其误归类为 `not_found` 而非 `schema_drift`（假阴性）

当前代码的 `EidAnnualReportSource` 异常分类逻辑决定了这两种情况的区分能力。plan 依赖该分类是正确的，但未要求在 evidence artifact 中记录聚合判断：若全部 `not_found`，应显式声明"无法区分真缺失与 schema drift 伪装，需要独立 schema drift 探测 gate"。

**建议**：在 evidence artifact 的 required content 中增加一条：若全部行均为 `not_found`，artifact 必须包含显式 aggregate ambiguity 声明。不强求修改 plan，可作为 evidence review 的检查项。

**严重度理由**：不阻塞 live command 执行，因为单行 continuation 逻辑不错误；但全部 `not_found` 场景下的证据解释存在歧义，可能被误读为"确认 4 行均不在 EID"。

---

## Finding 2 — LOW：blocked_environment 类别未在 AGENTS.md fallback 分类表中定义

**参考**：plan §Row-Level Outcome Rules，`blocked_environment`；AGENTS.md §年报来源 fallback 策略

**问题**：plan 引入了 `blocked_environment` 作为行级 outcome 类别，但 AGENTS.md 的 fallback 分类表只定义了 5 个类别：`not_found`、`unavailable`、`schema_drift`、`identity_mismatch`、`integrity_error`。`blocked_environment` 不在其中。

**分析**：plan 将其用于"unexpected exception"场景且 stop the gate，语义上最接近 `unavailable`（环境/服务临时不可用）。区分"已知的 unavailable"和"未知的 environmental exception"有诊断价值，但该分类未在 AGENTS.md 中注册，可能导致后续 gate 对 `blocked_environment` 的处理语义不一致。

**建议**：若 `blocked_environment` 仅作为本次 gate 的 internal artifact 分类（不写入 `FundDocumentRepository` 或 source policy 的公共契约），则可接受。建议在 evidence artifact 中注明该类别为 gate-local，不改变 AGENTS.md 分类表。

**严重度理由**：不影响 live command 正确性；分类边界不模糊（unexpected exception 明确区别于已知五类）；仅涉及 artifact 命名空间。

---

## Finding 3 — LOW：plan 未显式要求验证 live command 的异常→分类映射

**参考**：plan §Command Shape 与 §Row-Level Outcome Rules 之间

**问题**：plan 声明了 7 种行级 outcome 类别，但未要求 live command 脚本显式展示"EID source 原始异常 → 归类决策"的映射证据。当前代码的 `EidAnnualReportSource` 和 `AnnualReportSourceOrchestrator` 会抛出特定异常，`FundDocumentRepository.load_annual_report()` 向上传播。plan 依赖这些现有分类，但 evidence artifact 的 required content 中只要求"per-row failure category for blocked rows"，不要求记录原始异常类型或归类路径。

**风险**：如果某行的实际异常是 `httpx.TimeoutException` 但被归类为 `blocked_environment` 而非 `blocked_unavailable`，evidence reviewer 无法从 artifact 中判断归类是否正确。

**建议**：在 evidence artifact 的 required content 中增加：blocked 行必须同时记录原始异常类型（`type(exc).__name__`）和归类决策。这不需要修改 plan 的 continuation rules，只增强 evidence artifact 的可审计性。

**严重度理由**：归类错误会被 evidence review 捕获（reviewer 会对照 AGENTS.md 分类表）；缺少原始异常信息降低 review 效率但不导致错误决策。

---

## Finding 4 — INFORMATIONAL：matched_without_hash 行在 live 前无 identity 重校验步骤

**参考**：plan §Authorized Live Scope，fixed row set；`docs/implementation-control.md` current gate status

**问题**：4 行目标行的 prior docs-only identity status 均为 `matched_without_hash`。plan 直接进入 live acquisition，未要求 live command 在执行 `load_annual_report()` 前做 identity 预检查（如确认 EID 返回的 `upload_info_id` 或文件名与预期基金代码匹配）。

**分析**：这不是 plan 缺陷。live acquisition 的目的恰恰是从 `matched_without_hash` 升级到 `matched`（带 PDF SHA256）。live command 调用 `load_annual_report(fund_code, 2024, force_refresh=True)`，identity 校验由 repository/source 层在执行中完成（`identity_mismatch` 会 stop the gate）。plan 的 acceptance matrix 已包含 identity check。本发现仅记录为 informational：live command 成功后，artifact 中的 report key 和 metadata 自然构成 identity 证据。

**严重度理由**：不影响安全性；identity 由代码层 fail-closed 保证。

---

## Scope 检查

以下检查全部通过，无发现：

| 检查项 | 状态 |
|---|---|
| Strict single-source EID（`selected_source=eid`, `mode=single_source_only`, `fallback_enabled=false`） | ✅ plan §Controller Startup Judgment 显式保留当前实现策略 |
| FundDocumentRepository 单入口 | ✅ plan §Command Shape 要求所有行通过 `repository.load_annual_report()` |
| 无 fallback 调用 | ✅ plan §Command Shape must-not 列表 + §Acceptance Matrix `fallback_used=false` |
| 无 Eastmoney / 基金公司官网 / CNINFO 来源 | ✅ plan §Still forbidden 列表 + must-not 列表禁止 import/构造 `EastmoneyAnnualReportSource` |
| 无 provider / LLM / endpoint probe | ✅ plan §Still forbidden |
| 无 extractor correctness 工作 | ✅ plan §Still forbidden + must-not 禁止调用 `FundDataExtractor` |
| 无 fixture projection / golden / readiness | ✅ plan §Still forbidden |
| 无 source code / test / config 变更 | ✅ plan §Still forbidden + §Validation 只允许 `git status/diff` 检查 |
| Evidence retention 仅标量 metadata/count/hash/category | ✅ plan §Command Shape + §Acceptance Matrix safe retention 行 |
| 不保留 PDF bytes / raw text | ✅ plan §Command Shape must 列表 + §Evidence Artifact |

## 其他确认

- **Failure classification 边界**：plan 的 `not_found` vs `unavailable` vs `schema_drift` vs `identity_mismatch` vs `integrity_error` 分类与 AGENTS.md §年报来源 fallback 策略一致。`not_found` 继续 / `unavailable` 停止的区分符合第一性原理：前者是行级数据缺失，后者是环境级服务不可用。
- **Row continuation rules 不会掩盖 schema_drift / identity_mismatch / integrity_error**：这三类在 plan 中均为 stop the gate，fail-closed，符合 AGENTS.md 要求。Finding 1 涉及的 `not_found` 伪装问题已单独记录。
- **单源构造约束**：plan §Command Shape must-not 禁止 `AnnualReportSourceOrchestrator` 构造多于一个 source，与当前代码的 `single_source_only` 强制一致。
- **Stop conditions 完整性**：覆盖了非 EID 来源尝试、代码变更需求、schema_drift/identity_mismatch/integrity_error/unavailable、repository 边界绕过、tracked file 变更和作用域模糊。完备。

## Residual Risk

1. **全部 not_found 的歧义风险**（见 Finding 1）：若 4 行全部 `not_found`，无法仅从 evidence artifact 区分真缺失与 schema drift 伪装。缓解：evidence reviewer（AgentDS/AgentMiMo）会检查此场景。
2. **临时 PDF cache 目录清理**：plan 要求使用 temporary PDF cache directory，但未显式要求 live command 在退出前清理。若 live command 异常退出，临时目录可能残留 PDF 文件。缓解：临时目录在 `/tmp` 下，系统重启自然清理；不属于 source/test 变更，不触发 scope violation。

---

## 审查元数据

- **审查者**：AgentDS
- **审查类型**：adversarial plan review
- **审查范围**：source-policy、FDR boundary、failure-classification、scope drift
- **审查依据**：`AGENTS.md`、`docs/design.md`、`docs/implementation-control.md`、当前代码状态
- **未审查**：live authorization boundary（AgentMiMo 职责）、row continuation rule 细节（AgentMiMo 职责）、evidence retention 安全（AgentMiMo 职责）
- **未运行**：live command、network、PDF、FDR、pytest
