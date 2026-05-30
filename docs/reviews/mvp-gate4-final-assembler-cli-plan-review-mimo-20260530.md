# MVP Gate 4 final_chapter_assembler + chapter 0 + CLI --use-llm Plan Review (MiMo)

日期：2026-05-30
角色：AgentMiMo，plan review worker
Review 对象：`docs/reviews/mvp-gate4-final-assembler-cli-plan-20260530.md`
Gate 分类：`heavy`
Review 范围：plan review only；不改代码、不 commit。

## Verdict

**PASS with MEDIUM findings**

Plan 整体可执行，约束覆盖完整，与 AGENTS.md、design.md、startup-packet 和 Gate 3 controller judgment 一致。核心边界（partial fail-closed、chapter 0 accepted-only、chapter 7 不改 judgment 语义、CLI opt-in、无 Host/Agent/dayu、无 PDF/cache/source helper）均已显式声明。Findings 均为 MEDIUM 或 LOW，不阻塞 plan acceptance，但 controller 应在 acceptance decision 中确认是否需要补充后再进入 implementation。

## Review Scope

逐项挑战：

1. Gate 4 slice 拆分是否可执行
2. `final_chapter_assembler` 放 Service 是否正确
3. 第 0 章 accepted-conclusions-only 是否足够防止新事实
4. 第 7 章是否真的不改 final judgment 语义
5. partial orchestration policy 是否 fail-closed
6. CLI `--use-llm` 在 provider 未实现时是否应进入本 gate 或必须拆 4D
7. allowed files / validation 是否完整
8. 是否有违反 UI→Service→Host→Agent、extra_payload、source/PDF/cache、dayu、golden/quality/score/final judgment 约束

## Findings

### Finding 1 — MEDIUM: `analyze_with_llm()` quality gate 异常传播路径未显式定义

**文件/章节**：Plan §4.6 / §5 Slice 4B

**问题**：

Plan §4.6 明确 `analyze_with_llm()` 的 implementation sequence 第 1 步是"调用现有 `_run_analysis_core()`"。§4.7 规定 partial/blocked orchestration 走 assembler incomplete policy。§5 Slice 4B tests 第 5 条写"quality gate block/not-run 仍在 `_run_analysis_core()` 阶段按现有异常阻断"。

但未显式定义：当 `_run_analysis_core()` 因 `QualityGateBlockedError` 或 `QualityGateNotRunBlockedError` 抛出异常时，`analyze_with_llm()` 是应该（a）让异常传播到 CLI（与现有 `analyze()` 行为一致），还是（b）catch 异常并返回 structured incomplete result。

现有 `analyze()` 的行为是让异常传播、CLI 输出 exit code 2。如果 `analyze_with_llm()` 也走相同路径，则 quality gate block 时 assembler 不会被调用，orchestration 和 assembly 的 incomplete policy 不会生效——只有 orchestration 成功后才进入 assembler。

这个 gap 不会导致安全问题（fail-closed 仍然成立），但可能导致 implementation worker 做出不一致的选择。

**建议**：在 §4.6 或 §5 Slice 4B 中显式声明：`analyze_with_llm()` 对 `QualityGateBlockedError` / `QualityGateNotRunBlockedError` 的处理与现有 `analyze()` 一致——让异常传播，CLI 按现有 exit code 2 输出；incomplete assembly policy 只在 quality gate pass/warn 后 orchestration partial/blocked 时生效。

---

### Finding 2 — MEDIUM: Slice 4B/4C 未提供与 4A 一致的 "Allowed files / Implementation steps / Tests" 结构

**文件/章节**：Plan §5 Slice 4B / Slice 4C

**问题**：

Slice 4A 有完整的 "Allowed files → Do not edit → Implementation steps → Tests" 四段结构，清晰可执行。Slice 4B 和 4C 有 "Allowed files → Implementation steps → Tests" 但没有 "Do not edit" 列表，且 Tests 部分是 bullet list 而非与 4A 一致的格式。

对于 heavy gate 的 plan，implementation slice 的文档结构一致性有助于减少 worker 判断空间。4B/4C 缺少 "Do not edit" 列表可能导致 worker 不小心修改了不在 scope 内的文件（如 `_run_analysis_core()` 内部实现、`checklist()` 路径、`derive_final_judgment()` 等）。

**建议**：为 4B/4C 补充显式 "Do not edit" 列表，至少包括：

- 4B: `fund_agent/fund/analysis/final_judgment.py`, `fund_agent/fund/analysis/checklist.py`, `fund_agent/fund/template/renderer.py`, `fund_agent/fund/audit/`, `fund_agent/fund/quality_gate.py`, `fund_agent/ui/cli.py`
- 4C: `fund_agent/services/fund_analysis_service.py`（内部实现，只调用 public API）, `fund_agent/fund/`（所有文件）

---

### Finding 3 — MEDIUM: CLI fail-closed 到 assembler 的精确机制有两条路径描述

**文件/章节**：Plan §4.6, §5 Slice 4C

**问题**：

§4.6 描述了两种 CLI `--use-llm` provider unavailable 时的 fail-closed 机制：

1. "CLI 必须在进入 Service 前 fail-closed"
2. "或用 provider factory 返回明确 unavailable error"

§5 Slice 4C 步骤 4 写："若 4D 未实现 provider construction，则 CLI 必须在进入 Service 前 fail-closed，或用 provider factory 返回明确 unavailable error；不得传 fake client。"

两条路径语义不同：

- **路径 A（CLI pre-check）**：CLI 在调用 `analyze_with_llm()` 前检查 provider 是否可用，不可用则直接 stderr + exit 1。这意味着 CLI 需要知道 provider 配置状态。
- **路径 B（Service/factory error）**：CLI 调用 `analyze_with_llm()`，Service 或 factory 尝试构造 provider 失败时抛出 typed error，CLI catch 后 stderr + exit 1。

Plan 同时列出两条路径但未指定哪条是 primary。如果 4D 未实现，路径 A 更简单（CLI 直接判断）；如果 4D 部分实现，路径 B 更合理（factory 抽象）。

**建议**：明确首选路径。鉴于 4D 是 residual，建议首选路径 A：4C CLI 在 `use_llm=True` 时检查 provider availability config，不可用时直接 fail-closed，不进入 Service。如果后续 4D 实现，再切换到路径 B。

---

### Finding 4 — LOW: §4.7 partial policy 表格截断

**文件/章节**：Plan §4.7

**问题**：

§4.7 的 Orchestration status → Assembly behavior 表格在 `blocked` 行后截断：

```
| `blocked` | 0/6 | `FinalAssemblyResult(status="blocked", report_markdown=None)` | stderr 说明 blocked，exit `1`
```

缺少表格结束标记。这是文档格式问题，不影响语义理解。

**建议**：修复 markdown 表格格式。

---

### Finding 5 — LOW: `FinalJudgmentDecision` 类型在 assembler 输入中引用但未显式确认 import 来源

**文件/章节**：Plan §4.3 FinalChapterAssemblyInput

**问题**：

`FinalChapterAssemblyInput.final_judgment_decision: FinalJudgmentDecision` 引用了 `FinalJudgmentDecision` 类型。该类型定义在 `fund_agent/services/__init__.py`（从 design.md §2.3 可知），assembler 作为 Service 层模块可以直接 import。

Plan 未显式说明 import 路径，但这在 implementation 阶段不构成歧义，因为 `FinalJudgmentDecision` 是 Service 层已有 public type。

**建议**：无需修改。Implementation worker 可从 `fund_agent.services` import。

---

### Finding 6 — LOW: 第 7 章 `reasons` 使用约束缺少显式测试用例

**文件/章节**：Plan §4.5, §5 Slice 4A Tests

**问题**：

§4.5 规定"支撑判断的核心依据 只能使用 `FinalJudgmentDecision.reasons` 和第 1-6 章 accepted conclusions 中的已有结论短句"。§5 Slice 4A Tests 有 "chapter 7 uses exact FinalJudgmentDecision.selected_judgment label；不重新派生" 和 "developer override conflict reasons preserved"，但没有显式测试验证 chapter 7 的 "支撑判断的核心依据" 内容不包含 accepted conclusions 以外的新短句。

这是一个边界约束的 test gap。

**建议**：在 Slice 4A Tests 中增加一个 case：构造 accepted conclusions 中不含某个特定短句的输入，验证 chapter 7 markdown 的 "支撑判断的核心依据" 部分不包含该短句。

---

### Finding 7 — LOW: 第 0 章 `preferred_lens` 应用方式未显式说明

**文件/章节**：Plan §4.4

**问题**：

`fund-analysis-template-draft.md` 第 0 章的 `CHAPTER_CONTRACT` 定义了按基金类型差异化的 `preferred_lens`（如 index_fund 优先跟踪误差/费率，active_fund 优先超额收益稳定性/基金经理）。Plan §4.4 的 deterministic mapping 表只指定数据来源章节，未说明如何按基金类型差异化第 0 章的表述重点。

由于 Gate 3 orchestrator 的 accepted conclusions 已经消费了 Gate 1 的 `ChapterFactProjection`（含 `preferred_lens` 决策），第 1-6 章 accepted conclusions 的内容已经按基金类型差异化。第 0 章 deterministic assembly 从这些已差异化的 conclusions 中提取，因此 lens 语义通过上游传递。

但 plan 未显式声明这一假设。如果 implementation worker 不理解这一点，可能会尝试在 assembler 中重新应用 `preferred_lens`，导致代码越界到 Fund 层领域规则。

**建议**：在 §4.4 增加一句声明："第 0 章 deterministic assembly 不重新应用 `preferred_lens`；上游 Gate 1/2/3 已将 lens 语义融入 accepted conclusions 内容。"

---

## Constraint Compliance Summary

| 约束 | 状态 | 说明 |
|------|------|------|
| UI→Service→Host→Agent 四层边界 | ✅ COMPLIANT | CLI→Service→orchestrator+assembler，无 Host/Agent/dayu |
| extra_payload 禁止 | ✅ COMPLIANT | 所有参数显式 typed dataclass / keyword-only |
| source/PDF/cache 禁止 | ✅ COMPLIANT | §3 Non-Goals、§4.3 contract rules、§6 validation matrix 均声明 |
| dayu 禁止 | ✅ COMPLIANT | §3 Non-Goals 显式排除 |
| golden/quality/score/FQ 不变 | ✅ COMPLIANT | §3 Non-Goals 显式排除 |
| final judgment 语义不变 | ✅ COMPLIANT | §4.5 显式约束 chapter 7 只渲染不派生 |
| deterministic analyze/checklist 不变 | ✅ COMPLIANT | §4.6 显式约束 |
| partial fail-closed | ✅ COMPLIANT | §4.7 reject as incomplete，CLI exit 1 |
| chapter 0 accepted-only | ✅ COMPLIANT | §4.4 只接收 AcceptedChapterConclusion |
| CLI --use-llm opt-in | ✅ COMPLIANT | §4.6 显式 opt-in flag |
| 4D provider 拆分 | ✅ COMPLIANT | §4.8 显式作为 sub gate / residual |
| Gate 分类 heavy | ✅ COMPLIANT | Plan §7 显式声明 heavy，要求 2+ independent reviewers |

## Verdict Rationale

Plan 通过 review。7 个 findings 中 3 个 MEDIUM、4 个 LOW，均不违反核心约束，不构成 plan rejection 理由。MEDIUM findings 建议 controller 在 acceptance decision 中要求 implementation worker 在对应 slice 中补充，或由 controller 在 plan decision 中显式裁决。

**关键验证点**：

- Slice 4A: assembler contract 的 typed schema 和 partial policy 是本 gate 最关键的设计决策，plan 描述充分。
- Slice 4B: `analyze_with_llm()` 复用 `_run_analysis_core()` 的策略正确，quality gate 异常传播路径需澄清（Finding 1）。
- Slice 4C: CLI opt-in 的 fail-closed 策略正确，provider unavailable 的精确机制需澄清（Finding 3）。
- Slice 4D: 作为 residual 处理合理，不阻塞 4A-4C。
