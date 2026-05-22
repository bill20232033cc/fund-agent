# Design Alignment Review — GLM Independent Review (2026-05-22)

## Verdict

**PASS_WITH_FINDINGS**

Controller 对 `docs/design-control-alignment-guide.md` 的部分接受裁决从第一性原理看是正确的。没有阻断性问题阻塞本设计对齐切片的提交。有一个低优先级 finding 需要后续处理。

---

## Review Scope

| Input | Role |
|---|---|
| `docs/design-control-alignment-guide.md` | 外部对齐指南输入 |
| `docs/reviews/design-alignment-review-20260522.md` | Controller 裁决 |
| `docs/design.md` current diff (v2.0 → v2.1) | 设计真源变更 |
| `docs/implementation-control.md` current diff (v1.0 → v1.1) | 总控变更 |
| `AGENTS.md` | Agent 执行规则 |
| Code: `services/thermometer_service.py`, `fund/data/thermometer.py`, `ui/cli.py` | 实现证据 |
| `README.md` | 用户手册 |

Excluded: `docs/design0522.md`, `docs/implementation-control0522.md`, `docs/repo-audit-20260521.md`.

---

## Assessment 1: ThermometerService/CLI — 是否构成设计违规

**结论：不构成违规。Controller 裁决正确。**

代码证据：

1. `thermometer_service.py` docstring 明确声明"不决定估值状态，也不把温度计结果写入基金分析报告"。代码通过 Protocol 注入适配器，属于标准 Service 层编排。
2. `fund/data/thermometer.py` docstring 声明"不把温度计结果直接写入分析结论"。它只做 httpx 抓取 + HTML 解析 + 本地缓存。
3. `grep 'valuation_state'` 在两个温度计文件中零命中——代码实现与文档声明一致。
4. `design.md` v2.0 已在 §2.2 Service 清单中列出 `ThermometerService`（行 87），在 §6.3 外部数据表中列出 `data/thermometer.py`（行 480），在 §9 项目结构中列出 `thermometer.py` 和 `thermometer_service.py`。

Alignment Guide 的 P1 断言"非目标被绕过"过度陈述。温度计只读查询功能在 design.md v2.0 中已有记录。真正的缺口是非目标措辞模糊——"不做温度计自建"没有明确区分"自建计算"与"查询公开数据"。Controller 把这正确修正为措辞澄清而非设计违规。

v2.1 §1.3 修改（"不做温度计自建计算"，附加"不自行计算温度值，不自动映射为 `valuation_state`"）准确反映了代码事实。v2.1 §6.3 新增的温度计边界说明同样准确。

---

## Assessment 2: 拒绝 P13-P16 历史回写为 P18

**结论：正确。**

理由：

- P13 已通过 PR 7 squash-merge 至 main（`e2d8d38`）；P14 通过 PR 9（`746bfda`）；P16 通过 PR 10（`6d5a1bd`）。
- 每个 phase 有独立的 plan/review/implementation/code-review/aggregate-deepreview/PR-review/closeout artifact 链。
- 回写 P13-P16 为 P18 子任务会破坏这些已合并 artifact 的身份追溯。
- Control doc 的 Archive 章节已经保留了完整的 P13/P14/P15/P16 历史证据。
- 未来如需能力域摘要，可以在不改变历史 gate identity 的前提下新增摘要章节。

Alignment Guide 提议的 P18 scope mapping（P18-S1=S13, P18-S2=P14, P18-S3=P15, P18-S4=P16）本身有一定逻辑合理性，但不应以重写历史 gate 的方式执行。这是"正确目标、错误方法"。

---

## Assessment 3: 拒绝 broad `tracking_error coverage >= 90%`

**结论：正确。**

直接证据：

- P15-S1: `001548` 2024 年报经 `FundDataExtractor.extract("001548", 2024)` 提取，`tracking_error` 字段为 `extraction_mode="missing"`, `note="tracking_error_ambiguous"`。12 个关键词命中全部分类为投资目标 target/limit 或管理人叙事——无直接观测披露。
- P15-S1A: accepted verdict 为 `BLOCKED_NO_DIRECT_DISCLOSURE_EVIDENCE`。
- P16-S1: 五只增强指数候选全部 `tracking_error` 字段为 `blocked_no_direct_tracking_error`；rejected mentions 为 target/limit text、策略叙事或非观测跟踪误差语言。

在这些直接证据下，设置 `tracking_error coverage >= 90%` 会：
1. 对分母中包含无直接披露候选的基金产生不可能完成的指标；
2. 激励接受 benchmark-only text、target/limit text 或管理人叙事作为等价证据——这恰恰是 P15/P16 明确禁止的。

P17-S1 选择了正确的下一步：硬化现有 fail-closed extractor 语义，而非追求不可达的覆盖率指标。

Controller 的裁决"除非 denominator 限定为有直接观测披露证据的基金，否则当前 gate 不使用此覆盖率目标"是精确且安全的。

---

## Assessment 4: design.md v2.1 edits 是否准确且未 over-scope

**结论：准确，未 over-scope。**

v2.1 四处变更全部评估通过：

| 变更 | 评估 |
|------|------|
| Header: v2.0 → v2.1, 新增变更摘要 | 准确记录变更范围 |
| §1.3 非目标措辞 | "不做温度计自建计算" + 附加说明准确反映代码行为；未扩大也不缩小设计边界 |
| §6.3 温度计边界说明 | 准确描述只读查询与缓存复用；明确排除 `valuation_state` 映射和分析默认路径 |
| §9.0 CLI 命令清单 | 8 个命令全部可在 `cli.py` 中验证；`checklist` 标记为"占位"与代码一致 |
| §11 Plan Review 设计边界检查 | 纯流程改进；检查项与 AGENTS.md 硬约束和 design.md §1.3 对齐 |

无新功能声明、无架构变更、无边界扩展。

---

## Assessment 5: implementation-control.md bookkeeping 一致性

**结论：一致，P17-S1 gate 保持正确。**

逐项验证：

| 检查项 | 结果 |
|--------|------|
| Startup Packet Current gate | `P17-S1 tracking_error extractor ambiguity boundary plan-review` — 未被 alignment 处理改变 ✓ |
| Design truth 引用 | 更新为 `docs/design.md (v2.1)` — 与 design.md header 一致 ✓ |
| 当前状态描述 | "design-control alignment guide partially accepted" — 与 controller 裁决一致 ✓ |
| Active Gate Ledger 新增行 | `accepted / partial`，artifact 指向 alignment guide 和 controller review ✓ |
| Phase History Index 新增行 | 归入 Archive: P17，与 post-P16 规划同一 archive ✓ |
| Resume checklist | 包含 alignment 上下文且未丢失 P17-S1 约束 ✓ |
| Open residuals | 新增"design-boundary checklist must appear in future plan reviews" ✓ |
| Non-goal reminder | 未改变 ✓ |
| P18 | 未出现在 Phase 列表或 Archive 中 — 与拒绝 P18 回写的裁决一致 ✓ |
| unsupported coverage targets | Resume checklist 末尾新增"or unsupported coverage targets" — 与 Assessment 3 一致 ✓ |
| "Design Alignment Guide Handling" 章节 | accepted/corrected/rejected 三分类完整，与 controller review 一致 ✓ |

无 bookkeeping 矛盾。

---

## Findings

### F1 (LOW): README.md 行 121 遗留"尚未接入"条目与 v2.1 非目标措辞矛盾

**文件**: `README.md:121`
**问题**: README 在"尚未接入"列表中写有"温度计数据自动映射为 `analyze --valuation-state`"。"尚未接入"的语义是"将来会接入"。但 design.md v2.1 §1.3 已明确将"不自动映射为 `valuation_state`"列为非目标。
**风险**: 低。用户可能误解 MVP 将来会支持自动估值映射，与设计真源矛盾。
**建议**: 在后续 docs-only hygiene pass 中，将此条从"尚未接入"改为明确的"设计非目标"说明，或直接移除。不阻断本次 alignment slice 提交。

### F2 (INFO): Alignment Guide P1 断言"design.md 未记录 ThermometerService"与事实不符

**文件**: `docs/design-control-alignment-guide.md:21`
**问题**: Guide 断言"非目标被绕过"并标注为高严重度，但 design.md v2.0 已在 §2.2 和 §6.3 记录了 `ThermometerService` 和 `data/thermometer.py`。
**风险**: 无。Controller review 已正确修正此断言（Finding P1 "Corrected, not accepted as violation"）。
**建议**: 无需行动。记录为信息性 finding 以确保后续 alignment guide 输入在提出诊断前验证已有文档。

### F3 (INFO): design.md §9.0 CLI 命令清单中 `checklist` 状态描述可更精确

**文件**: `docs/design.md:661`
**问题**: `checklist` 命令描述为"占位；当前提示用户先使用 `analyze` 并以非零状态退出"。这是准确的代码事实，但 v2.1 §1.3 的新措辞"不做温度计自建计算"不涉及 checklist，而 design.md §4.7 和 §8.2 仍描述 checklist 作为报告嵌入模块。CLI 占位与 Capability 实现并存本身不矛盾，但"占位"一词可能让读者误以为 checklist 分析逻辑也未实现。
**风险**: 极低。当前代码事实是 checklist 分析逻辑已在 `analysis/checklist.py` 实现并在 `analyze` 流程中调用，只是独立 CLI 入口未接入 Service。
**建议**: 可考虑在 §9.0 备注中区分"checklist 分析逻辑已通过 analyze 集成"与"独立 CLI 入口未接入 Service"。不阻断。

---

## Blocking Assessment

**无阻断性 finding。** 三项 finding 均为 LOW/INFO 级别。

- F1 可在后续 docs-only hygiene pass 中处理。
- F2 已被 controller review 正确修正，无需额外行动。
- F3 为信息性观察，无行动要求。

本设计对齐切片可以提交。

---

## Summary of Controller Decisions Validated

| Controller 决策 | GLM 评估 | 理由 |
|---|---|---|
| ThermometerService 不是设计违规，需措辞澄清 | 同意 | 代码 + v2.0 文档均已有记录；缺口仅在非目标措辞 |
| 拒绝 P13-P16 → P18 回写 | 同意 | 历史合并 artifact 身份不可回溯修改 |
| 拒绝 broad `tracking_error coverage >= 90%` | 同意 | P15/P16 直接证据显示无足够直接观测披露；覆盖率目标会激励错误接受 |
| design.md v2.1 edits scope | 同意 | 四处变更均窄范围、有代码事实支撑 |
| implementation-control.md bookkeeping | 同意 | P17-S1 gate 完整保留；alignment bookkeeping 与 controller review 一致 |
| 未来 plan review 需显式设计边界检查 | 同意 | 填补了 Alignment Guide P4 指出的真实流程缺口 |
