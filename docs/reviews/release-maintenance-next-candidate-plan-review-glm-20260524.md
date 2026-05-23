# Adversarial Plan Review: Release Maintenance Next Candidate Plan (2026-05-24)

> **Reviewer**: GLM
> **Plan under review**: `docs/reviews/release-maintenance-next-candidate-plan-20260524.md`
> **Truth sources**: `AGENTS.md`, `docs/design.md` v2.2, `docs/implementation-control.md` Startup Packet, plan artifact
> **Review lens**: adversarial plan review — handoff-readiness, evidence sufficiency, scope narrowness, boundary discipline
> **Date**: 2026-05-24

---

## Conclusion: PASS_WITH_FINDINGS

Plan is handoff-ready. The selected work unit is correctly scoped to a documentary boundary decision artifact, avoids all forbidden actions, and is well-grounded in direct evidence. No blocking findings.

**Finding count**: 4 (all non-blocking, low severity)
**Blocking questions**: 0

---

## Checklist Verification

| # | Check | Result | Evidence |
|---|-------|--------|----------|
| 1 | Candidate selection supported by direct evidence | PASS | Plan §Direct Evidence cites AGENTS.md §模块边界, design.md §2.1/§2.2, implementation-control.md Startup Packet, and current code facts (directory listing, pyproject.toml) — all directly verifiable |
| 2 | Motivation for boundary decision over dependency gate is justified | PASS | Design.md §2.2: "在没有明确 session/run/tool-loop 需求前，不应空造 Host 或 Agent 包，也不应引入未使用的 `dayu.host` / `dayu.engine` 依赖"；AGENTS.md §硬约束: "Dayu 是四层架构参考与 Host/Agent 执行底座来源" but 当前确定性主链路未接入；implementation-control.md Startup Packet: dependency gate scope guard is "仅当 Host 或 Agent 执行内核落地时" |
| 3 | No `fund_agent/host` or `fund_agent/agent` placeholder created | PASS | Plan §Non-Goals explicitly forbids; §Affected Files disallows both; §Stop Conditions lists these as stop triggers |
| 4 | Host, if needed, uses `dayu.host` | PASS | Plan §Direct Evidence line 1 cites AGENTS.md: "Host 管理 session/run/…且必须使用 `dayu.host`"；§Slice 2 trigger condition states same |
| 5 | Agent execution/tool-loop, if needed, uses `dayu.engine` | PASS | Plan §Direct Evidence line 1 cites AGENTS.md: "Agent 管理 tool loop/…且必须使用 `dayu.engine`"；§Slice 2 trigger condition states same |
| 6 | No explicit parameters hidden in `extra_payload` | PASS | Plan §Non-Goals, §Slice 2 validation, §Review Gates, §Stop Conditions all explicitly check this |
| 7 | pyproject/dayu-agent baseline dependency discipline | PASS | Plan §Direct Evidence line on pyproject baseline; §Slice 2 dependency gate trigger requires checking against dayu-agent baseline; §Risks section identifies premature dependency declaration as a risk |
| 8 | No historical six-layer/Application/Runtime/Engine wording as current truth | PASS | Plan §Non-Goals explicitly excludes these; §Direct Evidence states "disallowed historical inputs"；§Stop Conditions includes revival of these terms as stop trigger |
| 9 | Scope is narrow enough for a single work unit | PASS | Single artifact path, no code changes, no dependency changes, no package creation, 4 slices all touching same file |
| 10 | Slice boundaries are concrete | PASS (see Finding 1) | Each slice specifies exact file, exact changes, and validation commands; minor gap in Slice 2 validation specificity |
| 11 | Stop conditions are concrete | PASS | 6 explicit stop conditions with specific triggers |
| 12 | Completion report format specified | PASS (see Finding 2) | 7-field format listed; could be more specific about validation pass criteria |
| 13 | Residual risk tracking | PASS | 4 risks identified; 1 non-blocking open question |
| 14 | No source/test/config/README/design/control modification | PASS | Plan §Non-Goals and §Affected Files explicitly forbid all |
| 15 | No push/PR/merge/external action | PASS | Plan §Non-Goals explicitly forbids |

---

## Findings

### F1-未修复-[低]-Goal "code-generation-ready" 措辞与实际 deliverable 不匹配

- **Plan位置**: §Goal / Motivation, 第 1 段 "给出 code-generation-ready 实施计划"
- **问题类型**: 措辞准确性
- **计划当前写法**: "为下一轮 release-maintenance 本地 work unit 选择一个可进入 plan review 的最小候选，并给出 code-generation-ready 实施计划。"
- **为什么有问题**: 计划的实际 deliverable 是一个纯文档决策 artifact（boundary decision），不产生任何代码或代码可执行的实施步骤。"code-generation-ready" 暗示存在可直接转入编码的计划，但实际 work unit 的结论是"保持当前确定性过渡路径、不创建 Host/Agent 包"，没有可生成的代码。这会造成后续 reader 对 plan 性质的误判。
- **直接证据**: §Selected Work Unit 明确写 "本 work unit 只生成一个新的 review artifact"；§Affected Files 唯一允许的修改是 `docs/reviews/` 下新增文件；4 个 Slice 全部只操作同一 markdown 文件。
- **影响**: 低。Non-Goals、Affected Files、Slices 和 Stop Conditions 共同消歧了实际范围，不会导致实施者误解。但对 review 读者造成初始预期偏差。
- **建议改法和验证点**: 将 Goal 中的 "code-generation-ready 实施计划" 改为 "plan-review-ready 决策计划" 或等效措辞，明确 deliverable 是决策文档而非可编码实施步骤。验证：rg "code-generation-ready" 不应出现在最终 plan 中。
- **修复风险**: 低。纯措辞修改，不影响任何实质内容。
- **严重程度**: 低

### F2-未修复-[低]-Slice 2 validation 缺少自动化检查命令

- **Plan位置**: §Implementation Slices > Slice 2 > Tests / validation
- **问题类型**: 验证具体性
- **计划当前写法**: 三个 "Confirm artifact states ..." 纯文字断言，没有对应 grep/rg 命令。
- **为什么有问题**: Slice 1 和 Slice 3 都提供了具体的 `rg -n` 命令作为自动化验证，Slice 2 却只有手动确认。对于同一个文档 artifact，三个 slice 的验证方式应保持一致，否则 Slice 2 的验证可能被跳过或执行不一致。
- **直接证据**: Slice 1 validation 提供 `rg -n "UI -> Service -> Host -> Agent|dayu.host|..." `；Slice 3 validation 提供 `rg -n "Host implementation gate|Agent execution/tool-loop gate|..."`；Slice 2 没有。
- **影响**: 低。Slice 2 的确认内容（Host/Agent dependency gate blocked、no placeholder、no extra_payload）可在 review 时人工验证，且 Slice 1 的 rg 命令部分覆盖了这些内容。
- **建议改法和验证点**: 为 Slice 2 添加等效 rg 命令，例如：`rg -n "dependency gate remains blocked|no fund_agent/host|no fund_agent/agent|extra_payload" docs/reviews/release-maintenance-host-agent-boundary-decision-20260524.md`。验证：三个 slice 的 validation section 均包含可执行命令。
- **修复风险**: 低。只增加验证命令，不改变实质内容。
- **严重程度**: 低

### F3-未修复-[低]-Completion Report Format "Validation run" 字段缺少通过标准

- **Plan位置**: §Completion Report Format
- **问题类型**: 验收标准具体性
- **计划当前写法**: "Validation run:" 无进一步说明，没有定义"通过"意味着什么。
- **为什么有问题**: §Implementation Slices 中每个 slice 都定义了具体的验证命令（rg、git diff --check），但 Completion Report 的 "Validation run" 字段没有说明应记录什么内容（命令输出？退出码？grep 命中数？）。这会让实施者对完成报告的填写标准产生歧义。
- **直接证据**: Slice 1 有 `rg -n` 命令和 `git diff --check`；Slice 3 有 `rg -n` 和 `git diff --check`；Slice 4 有 `git diff --name-only`。Completion Report 只说 "Validation run:" 不说明如何判定通过。
- **影响**: 低。Slices 自身定义了足够的验证方式，Completion Report 只是最终汇总格式。
- **建议改法和验证点**: 在 "Validation run:" 后增加说明，例如 "记录每个 slice 的验证命令及退出码 0 或预期输出"。或在 §Completion Report Format 中引用 slice validation commands 作为通过标准。
- **修复风险**: 低。
- **严重程度**: 低

### F4-未修复-[低]-Review Gates checklist 与 design.md §12 对齐不完整

- **Plan位置**: §Review Gates > Review checklist
- **问题类型**: 检查清单完整性
- **计划当前写法**: 8 项 review checklist，覆盖四层边界、dayu.host/dayu.engine、占位包、dependency gate、文件修改范围、extra_payload、pyproject baseline、历史口径。
- **为什么有问题**: design.md §12 要求 plan review 检查 "生产年报访问是否仍只通过 `FundDocumentRepository` / `FundDataExtractor`" 和 "License/repo hygiene"。Plan 的 review checklist 没有包含这两项。虽然本 work unit 不触碰年报访问路径或 License，但 design.md §12 是对所有后续 plan review 的统一要求，遗漏会削弱 review 的系统性。
- **直接证据**: design.md §12 Plan Review 设计边界检查列出 9 项，其中第 3 项 "生产年报访问是否仍只通过 FundDocumentRepository / FundDataExtractor" 和第 8 项 "是否保持 License/repo hygiene" 未出现在 plan §Review Gates 的 8 项 checklist 中。
- **影响**: 低。本 work unit 不涉及年报访问或 License 变更，遗漏不会导致实际风险。但作为 review template 的一致性，建议补齐。
- **建议改法和验证点**: 在 §Review Gates checklist 中增加两项：(1) "Confirms production annual report access remains through FundDocumentRepository / FundDataExtractor only"；(2) "Confirms License/repo hygiene is preserved"。验证：review checklist 条目数应 ≥ 10 且覆盖 design.md §12 全部 9 项。
- **修复风险**: 低。
- **严重程度**: 低

---

## Residual Risks

| ID | Risk | Severity | Mitigation |
|----|------|----------|------------|
| RR-1 | Boundary decision artifact 可能被视为"空架构文档"，后续 reader 误以为 Host/Agent 已开始设计 | 低 | Plan §Risks 已识别此风险；Slice 2 要求 artifact 明确声明 "keep deterministic transition path as default" |
| RR-2 | Open question "哪个具体产品需求触发第一个 Host/Agent implementation gate" 未回答 | 低 | 正确标记为 non-blocking future question；不影响当前 plan 的执行 |
| RR-3 | Future gate skeletons 的具体内容（契约 schema、测试类别明细）需在后续 plan 中展开 | 低 | Plan §Slice 3 定义了 skeleton 的必含元素，后续 plan review 可进一步细化 |
| RR-4 | 纯文档 deliverable 可能增加 docs/reviews/ 目录膨胀 | 低 | 当前 artifact 是单文件、有明确命名规范，风险可控 |

---

## Truth Source Alignment Summary

| Truth Source | Plan Alignment | Notes |
|---|---|---|
| AGENTS.md §模块边界 | Full | Plan 正确引用四层边界、dayu.host/dayu.engine 要求、extra_payload 禁令 |
| AGENTS.md §硬约束 | Full | Plan 正确引用 Dayu 四层参考定位和第一性原理判断 |
| design.md §1.3 非目标 | Full | Plan 不触碰任何 §1.3 列出的非目标 |
| design.md §2.1/§2.2 | Full | Plan 正确描述当前确定性过渡路径和 Host/Agent 接入条件 |
| design.md §12 Plan Review | Partial (see F4) | Plan review checklist 覆盖 §12 大部分但遗漏 2 项 |
| implementation-control.md Startup Packet | Full | Plan 正确引用 current gate、next entry point、candidate 列表、scope guard |
| Current code facts | Full | Plan 正确验证 fund_agent/host 和 fund_agent/agent 不存在、pyproject.toml 无 dayu 依赖 |

---

## Blocking Questions

None.
