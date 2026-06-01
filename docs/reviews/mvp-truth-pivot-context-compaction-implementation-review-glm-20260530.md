# MVP Truth Pivot and Context Compaction Gate — Implementation Review (GLM)

> **Reviewer**: AgentGLM (implementation reviewer)
> **Date**: 2026-05-30
> **Role**: Gateflow implementation reviewer（非 controller/implementation worker）
> **Gate**: MVP truth pivot and context compaction gate
> **Classification**: `heavy`
> **Source plan**: `docs/reviews/mvp-truth-pivot-context-compaction-plan-20260530.md`
> **Implementation evidence**: `docs/reviews/mvp-truth-pivot-context-compaction-implementation-evidence-20260530.md`
> **Changed files**: `docs/design.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md`, evidence artifact

---

## Verdict: PASS_WITH_NON_BLOCKING

实现正确完成了 docs-only pivot 目标。三个控制文档之间关键事实一致，Route C 统一标记为未来设计，当前确定性实现状态完整保留，release-maintenance 长账本已压缩。有一个 low-severity 措辞问题不阻断但不建议忽略。

---

## Findings

### F1. LOW — Recent Active Gate Ledger "no commit/push/PR" 措辞与 Gateflow 本地 checkpoint commit 规则存在潜在冲突

**位置**: `docs/implementation-control.md` line 98 (Recent Active Gate Ledger Next action 列)

**现状**: Ledger 写为 `Stop after evidence and report; no commit/push/PR`。

**问题**: AGENTS.md `standard` 分类明确要求 "local accepted commit"（line 55）；`heavy` 作为更高级别分类，隐含同等或更严格的 checkpoint 约束。当前 plan 已作为 commit `70184d3` 被接受，但实现变更（design.md、implementation-control.md、current-startup-packet.md）均未 commit。Ledger 中 "no commit" 的绝对措辞可能被解读为阻止 controller 在接受 evidence 后创建本地 checkpoint commit。

**缓解因素**: `docs/current-startup-packet.md` line 98 使用了更宽松的措辞 `Do not commit, push or create PR unless a later controller step explicitly authorizes it`，部分缓解了冲突。从上下文意图看，"no commit" 针对的是 implementation specialist 而非 controller。

**建议**: 将 `docs/implementation-control.md` line 98 的 Next action 改为：
```
Stop after evidence and report; no push/PR/promotion; local gateflow checkpoint commit allowed after controller acceptance
```

---

## Pass Items（按 review criteria 逐项确认）

### C1. Control doc current phase 与 next entry ✅

| 检查项 | 结果 |
|--------|------|
| `docs/implementation-control.md` Current phase | `MVP fund analysis report generation phase` ✅ |
| `docs/implementation-control.md` Next entry point | `MVP Gate 1: facet_recognizer + ChapterFactProvider/FundToolService contract gate` ✅ |
| `docs/current-startup-packet.md` Current phase | 与 control doc 一致 ✅ |
| `docs/current-startup-packet.md` Next entry point | 与 control doc 一致 ✅ |

三份文档的 phase、gate、classification、next entry point 完全一致。

### C2. Route C 只写为 accepted future design ✅

| 文档 | Route C 措辞 |
|------|-------------|
| `docs/implementation-control.md` line 23 | "Route C 是已接受的未来设计，不是当前实现" ✅ |
| `docs/implementation-control.md` line 65 | "Route C is the accepted future route" ✅ |
| `docs/implementation-control.md` line 73-80 | 表格列名为 "Future scope" ✅ |
| `docs/design.md` line 486 | 标题 "已接受的未来设计：MVP LLM report generation route" ✅ |
| `docs/design.md` line 488 | "它不是当前代码事实" ✅ |
| `docs/design.md` line 506 | Gate 1 组件名称为 "未来候选命名，不是当前代码类型" ✅ |
| `docs/current-startup-packet.md` line 48 | "Route C is accepted future design ... It is not current implementation" ✅ |
| `docs/current-startup-packet.md` line 58 | "Gate 1 names are future candidate names" ✅ |

没有任何位置将 Route C 写成当前实现。

### C3. 当前 deterministic analyze/checklist、UI -> Service -> fund_agent/fund、FQ0-FQ6 状态保持 ✅

| 检查项 | 结果 |
|--------|------|
| Deterministic `fund-analysis analyze/checklist` 仍为唯一实现主链路 | implementation-control.md line 21, design.md line 23, startup-packet.md lines 30-31 ✅ |
| UI -> Service -> `fund_agent/fund` 过渡路径 | implementation-control.md line 22, design.md line 27, startup-packet.md lines 32-33 ✅ |
| FQ0-FQ6 quality gate 不变 | startup-packet.md line 37 ✅ |
| 无 LLM chapter writing | startup-packet.md line 38 ✅ |
| 无 LLM audit | startup-packet.md line 39 ✅ |
| 无 write-audit-repair loop | startup-packet.md line 40 ✅ |
| 无 chapter orchestrator | startup-packet.md line 41 ✅ |
| 无 final LLM assembler | startup-packet.md line 42 ✅ |
| 无 CLI `--use-llm` | startup-packet.md line 43 ✅ |
| 无 Host/Agent/dayu runtime | startup-packet.md line 44 ✅ |

### C4. Golden/strict correctness/QDII/FOF/110020/fixture promotion 保留为 residual ✅

| 残余项 | implementation-control.md | startup-packet.md |
|--------|--------------------------|-------------------|
| Golden / strict correctness / fixture promotion | "Residual only for MVP report generation" (line 86) ✅ | "residuals and do not block MVP report generation Gate 1" (line 79) ✅ |
| 004393 / 004194 / 006597 | "not promotion-prep-ready; fixture_state=absent; promotion_allowed=false" (line 87) ✅ | "not promotion-prep-ready" (line 80-82) ✅ |
| QDII / FOF / 110020 / 017641 | "Deferred from minimum v1 and not ready for full v1" (line 88) ✅ | "deferred from minimum v1 and not ready for full v1" (line 83) ✅ |

没有任何位置将这些项说成 ready 或已解决。

### C5. Release-maintenance 长账本已压缩为链接/摘要 ✅

| 检查项 | 结果 |
|--------|------|
| implementation-control.md Historical Evidence Index | 仅 4 条链接 (lines 105-108) ✅ |
| implementation-control.md line 99 | "Use Historical Evidence Index only; do not treat as current phase" ✅ |
| startup-packet.md line 84 | "Release-maintenance long ledger is preserved by links only" ✅ |
| 长账本未作为 current phase | ✅ |

### C6. Startup packet 足够短且可恢复 ✅

| 检查项 | 结果 |
|--------|------|
| 总行数 | 125 行（plan 目标 100-150 行）✅ |
| Read Order (§1) | 4 个必读文件 ✅ |
| Current Mainline (§2) | 7 字段状态表 + 1 行指引 ✅ |
| Implementation Facts (§3) | 14 条明确事实 ✅ |
| Route C (§4) | 5-gate 表格 + 边界说明 ✅ |
| Boundary Guardrails (§5) | 13 条护栏 ✅ |
| Current Residuals (§6) | 8 条残余 ✅ |
| Prohibited Actions (§7) | 10 条禁令 ✅ |
| Resume Checklist (§8) | 12 步恢复清单 ✅ |
| Key Artifact Links (§9) | 8 条证据链接 ✅ |

Startup packet 可以独立支撑后续 phaseflow 恢复。

### C7. 无越界改 AGENTS.md/template/runtime/schema/score/snapshot/quality/golden/manifest ✅

| 检查项 | 结果 |
|--------|------|
| AGENTS.md | 未修改 ✅ |
| `docs/fund-analysis-template-draft.md` | 未修改 ✅ |
| Runtime code | 未修改 ✅ |
| Schema / score / snapshot | 未修改 ✅ |
| Quality gate | 未修改 ✅ |
| Golden fixture / golden answer / manifest | 未修改 ✅ |
| Promotion state | 未修改 ✅ |

Evidence artifact 验证 `git diff --name-only` 仅包含 `docs/design.md` 和 `docs/implementation-control.md`。

---

## Evidence Artifact 质量评估

| 检查项 | 结果 |
|--------|------|
| Gate metadata 完整 | ✅ |
| Changed files 表格 | ✅ (4 files) |
| Before/After summary | ✅ |
| Route C future-only evidence | ✅ (5 bullets) |
| Deterministic implementation evidence | ✅ (3 bullets) |
| Residual evidence | ✅ |
| Host/Agent/Dayu evidence | ✅ |
| Validation commands | ✅ (4 commands, all PASS) |
| Residual risks/owners | ✅ |
| Stop conditions check | ✅ |
| 未修改 runtime/golden/quality/template/AGENTS.md | ✅ (显式声明) |

---

## 三文档一致性矩阵

| 关键事实 | design.md | implementation-control.md | startup-packet.md |
|----------|-----------|--------------------------|-------------------|
| Current phase = MVP report gen | §5.4.1 | line 9, 35 | line 18 |
| Route C = future only | §5.4.1 title + line 488 | line 23, 65 | line 48 |
| Deterministic = current | §1.2 line 23 | line 21, 66 | line 30 |
| UI -> Service -> fund | §2.1 line 27 | line 22 | line 32 |
| FQ0-FQ6 unchanged | 全文保留 | line 29 | line 37 |
| Gate classification = heavy | — | line 36 | line 20 |
| Accepted plan commit = 70184d3 | — | line 42 | line 24 |
| Golden/residuals | §5.4.1 line 508 | lines 86-92 | lines 79-87 |

所有关键事实三文档一致，无冲突。

---

## Residual Risks After This Review

| 风险 | Owner | 说明 |
|------|-------|------|
| F1 ledger 措辞修正 | Controller 或下一 gate specialist | 修改后需确认不引入新语义 |
| 实现变更未 commit | Controller | 接受 review 后应决定是否创建 local checkpoint commit |
| Gate 1 命名（facet_recognizer 等） | Gate 1 plan/review | 未来候选名，Gate 1 实现时可调整 |

---

## Conclusion

实现完整、正确地完成了 docs-only pivot 目标。三份控制文档关键事实一致，无内部矛盾。Route C 在所有位置均标记为未来设计，当前确定性实现状态完整保留，残余项正确分类且不被说成 ready。Release-maintenance 长账本成功压缩。

唯一发现（F1）为 low-severity 措辞问题：Recent Active Gate Ledger 中 "no commit/push/PR" 的绝对措辞可能阻止 controller 创建本地 checkpoint commit。建议修改为 "no push/PR/promotion; local gateflow checkpoint commit allowed after controller acceptance"。此问题不阻断 gate 通过。
