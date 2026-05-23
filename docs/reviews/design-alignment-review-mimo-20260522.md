# Design Alignment Review — MiMo Independent Review（2026-05-22）

## Verdict

**PASS_WITH_FINDINGS**

Controller review `docs/reviews/design-alignment-review-20260522.md` correctly partially accepted `docs/design-control-alignment-guide.md`. From first principles, all five core decisions are defensible and internally consistent. The `docs/design.md` v2.1 edits and `docs/implementation-control.md` bookkeeping changes are accurate, appropriately scoped, and preserve the P17-S1 active gate. No blocking issue found; two low-severity observations are noted below.

---

## Review Scope

| Input | Role |
|---|---|
| `docs/design-control-alignment-guide.md` | Alignment guide under review |
| `docs/reviews/design-alignment-review-20260522.md` | Controller partial-acceptance artifact under review |
| `docs/design.md` diff (v2.0 → v2.1) | Design truth edits to assess |
| `docs/implementation-control.md` diff | Control bookkeeping edits to assess |
| `AGENTS.md` | Project hard constraints and module boundaries |
| Code facts: `fund_agent/services/thermometer_service.py`, `fund_agent/data/thermometer.py`, `fund_agent/ui/cli.py` | ThermometerService/CLI implementation evidence |
| Phase control history: P13-P16 gate artifacts, PR 7/9/10 | Historical phase identity evidence |

Excluded local drafts per scope: `docs/design0522.md`, `docs/implementation-control0522.md`, `docs/repo-audit-20260521.md`.

---

## Finding 1: ThermometerService/CLI — Wording Clarification, Not Design Violation

**Guide claim**: P1 — "非目标被绕过"，ThermometerService 实现违反 design.md §1.3 "不做温度计自建"。

**Controller decision**: Corrected, not accepted as violation. Non-goal wording clarified from "不做温度计自建" to "不做温度计自建计算".

**First-principles assessment**: **Correct.**

Evidence chain:
- `docs/design.md` v2.0 §1.3 原文："不做温度计自建（MVP 使用有知有行公开页面数据 + 缓存）"——括号内已说明"自建"的边界是"不自建计算，可查询公开数据"。
- `docs/design.md` v2.0 §6.3 已记录 `ThermometerService`、`data/thermometer.py` 和 CLI 结构。Guide 声称 thermometer "wholly missing from design" 与文档事实不符。
- 代码事实：`ThermometerService` 是只读查询有知有行公开页面数据 + 本地缓存复用；不自行计算温度值，不自动映射 `valuation_state`，不参与 `fund-analysis analyze` 默认分析链路。
- v2.1 修改将括号内隐含语义提升为显式措辞，没有改变非目标的实质边界。

**Verdict**: No issue. Wording clarification is precise and does not authorize new product scope.

---

## Finding 2: P13-P16 → P18 Historical Rewrite — Correctly Rejected

**Guide claim**: P2 — P13-P16 粒度过细，应合并为 P18 "指数基金核心指标数据质量"。

**Controller decision**: Rejected for history rewrite; defer as optional capability summary.

**First-principles assessment**: **Correct.**

Reasoning:
- P13-P16 已通过完整 gate 链路（plan → review → implementation → code review → aggregate deepreview → PR → merge），每个 phase 有独立 artifact 路径、commit hash、PR URL、reviewer judgment 和 residual owner。
- Phase 身份是证据台账的锚点，追溯改名会破坏 artifact 可追溯性——未来 resume 时无法用旧名定位已有证据。
- Guide 的 P18 proposal 将 P15-S1（blocked，`BLOCKED_NO_DIRECT_DISCLOSURE_EVIDENCE`）标记为 "P18-S3（标记 blocked）" 但同时要求 "P18 整体状态：部分完成，P18-S3 标记为 blocked，不阻断 P18 关闭"——这会在控制文档中引入"phase 可关闭但有 blocked 子任务"的新语义，与现有 phaseflow 闭合标准不一致。
- 能力域摘要（capability-domain summary）作为可选补充不改写历史身份，是更安全的替代方案。

**Verdict**: No issue. Historical integrity preserved.

---

## Finding 3: Broad `tracking_error coverage >= 90%` Target — Correctly Rejected

**Guide claim**: P18 Exit Criteria 包含 "指数基金 tracking_error coverage ≥ 90%"。

**Controller decision**: Rejected for current gates unless denominator restricted to direct observed disclosure evidence.

**First-principles assessment**: **Correct, with one nuance.**

Evidence chain:
- P15-S1A 审查了 `001548` 2024 年报，12 个关键词命中全部分类为投资目标限值（target/limit）或经理叙事（manager narrative），无一直接披露观察值。结果：`BLOCKED_NO_DIRECT_DISCLOSURE_EVIDENCE`。
- P16-S1 审查了 5 只增强指数候选（`004194`, `005313`, `017644`, `019918`, `019923`），所有 `tracking_error` 行被阻断，原因同上。
- 当前精选基金池中指数/增强指数基金的 `tracking_error` 直接披露证据极度稀缺。在此条件下设置全域 ≥90% 覆盖率目标，会产生激励偏差——为了达标而降低证据接受标准（如接受目标限值文本或叙事推断）。
- Controller 的 "restricted denominator" 条件是正确的安全阀：只有当 eligible universe 限定为有直接披露证据的基金时，覆盖率目标才有意义。

Nuance: Guide 的 P18 proposal 中 "无直接披露证据的基金明确标记 `unavailable`，不估算" 这一约束本身是合理的。但将其作为 exit criteria 的一部分而不修改覆盖率分母定义，仍然会在实践中产生与全域目标的矛盾。

**Verdict**: No issue. Evidence-first gating is the correct approach.

---

## Finding 4: `docs/design.md` v2.1 Edits — Accurate, Not Over-Scoped

**Assessment of diff**:

| 变更位置 | 变更内容 | 评估 |
|---|---|---|
| Header (v2.0 → v2.1) | 版本号、状态行、变更摘要 | 准确反映变更范围 |
| §1.3 非目标 (line 34) | "不做温度计自建" → "不做温度计自建计算（MVP 只查询有知有行公开页面数据并复用本地缓存；不自行计算温度值，不自动映射为 `valuation_state`）" | 精确澄清，不改变非目标实质边界 |
| §6.3 外部数据 (after line 481) | 新增温度计能力说明段落 | 记录已实现事实，与代码一致 |
| §9.0 CLI 命令清单 (before project structure) | 新增 8 条命令表 | 完整记录当前 CLI 状态，`checklist` 标记为占位 |
| §11 Plan Review 设计边界检查 (new section) | 5 条显式检查规则 | 将已接受的 process improvement 编码为设计规则 |

**Over-scoping check**:
- 无新增产品功能、无新增模块边界、无新增依赖、无新增非目标。
- §11 是 process rule，不是 product scope——它约束 plan review 行为，不约束运行时行为。
- §6.3 新增段落的措辞（"只做只读查询与缓存复用；它不把温度计数值自动映射为...也不参与...默认分析判断"）与 §1.3 非目标一致。

**Verdict**: No issue. Edits are accurate and appropriately scoped.

---

## Finding 5: `docs/implementation-control.md` Bookkeeping — Consistent, P17-S1 Gate Preserved

**Assessment of diff**:

| 变更位置 | 变更内容 | 评估 |
|---|---|---|
| Header design truth | `docs/design.md` → `docs/design.md` (v2.1) | 准确 |
| Header current status | 更新为 "design-control alignment guide partially accepted" | 准确 |
| Startup Packet Design truth | 同上 | 一致 |
| Startup Packet Open residuals | 新增 "design-boundary checklist must appear in future plan reviews" | 与 §11 对应 |
| Startup Packet Resume checklist | 新增对齐指南接受和 P18 拒绝说明 | 完整 |
| New section "2026-05-22 Design Alignment Guide Handling" | 4 点 Accepted/Corrected/Rejected 摘要 | 与 controller review 一致 |
| Active Gate Ledger | 新增 `design-control alignment guide reconciliation` 行 | status `accepted / partial`，next action 保持 `P17-S1 plan/review` |
| Phase History Index | 新增 Design alignment guide reconciliation 行 | 归档到 Archive: P17 |
| Design/Control Alignment Rules rule 1 | 引用 (v2.1) | 一致 |
| Archive: P17 | 新增对齐指南 reconciliation 段落 | 完整记录 |

**P17-S1 gate preservation check**:
- Current gate 未变：`P17-S1 tracking_error extractor ambiguity boundary plan-review`。
- Next entry point 未变：`P17-S1 specialist plan`。
- Active Gate Ledger 中 reconciliation 行的 next action 明确为 `P17-S1 plan/review`。
- Resume checklist 中明确 "next gate remains P17-S1"。

**Verdict**: No issue. Bookkeeping is internally consistent and gate-preserving.

---

## Finding 6 (Low): Controller Review Self-Assessment Conflict of Interest

**Observation**: `docs/reviews/design-alignment-review-20260522.md` 是 controller 对自身 partial-acceptance 决策的记录。本独立 review 从第一性原理验证了所有五个核心决策，未发现偏差。

**Risk**: 低。当前不存在冲突，但长期看，设计对齐裁决的独立 reviewer 应与 controller 分离。

**Required change**: 无需立即变更。可在中期 process improvement 中考虑将 design-alignment review 分配给独立 reviewer。

---

## Finding 7 (Low): Guide §1.3 Config 层风险评估未被显式处理

**Observation**: Guide §1.3 非目标遵守检查表中有一行："不把外部 Dayu Host/Engine 作为主链路依赖" → "config 目录结构暗示抽象层" → "风险" → "明确声明：config 只含路径常量"。

Controller review 未显式回应这一条。`docs/design.md` v2.1 §2.1 Config 层已有明确描述："Config | 静态默认路径常量 | `fund_agent/config/paths.py` | 不读取 prompt manifest、workspace config、环境变量或运行时配置"。Guide 的担忧已被现有设计文档覆盖。

**Risk**: 极低。设计文档已有声明，但 controller review 未显式记录这一 check 的结果。

**Required change**: 无需变更。如需完备，可在 controller review 的 Finding Decisions 表中补充一行。

---

## Summary

Controller `docs/reviews/design-alignment-review-20260522.md` 的 partial acceptance 从第一性原理看是正确的：

1. **ThermometerService/CLI**: 非目标措辞澄清，不是设计违反。✅
2. **P18 历史改写**: 正确拒绝，保护 artifact 可追溯性。✅
3. **≥90% 覆盖率目标**: 正确拒绝，避免激励偏差。✅
4. **design.md v2.1 编辑**: 准确、不过度扩展。✅
5. **implementation-control.md 台账**: 一致、P17-S1 gate 保持。✅

两个低严重度观察（Finding 6/7）不阻塞当前 design-alignment slice 的提交。

**是否阻塞提交**: 否。当前 design-alignment slice 可以提交。
