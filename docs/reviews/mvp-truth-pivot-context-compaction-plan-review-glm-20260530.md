# Plan Review: MVP truth pivot and context compaction gate

## Review metadata

- **Reviewer**: GLM (independent plan reviewer)
- **Date**: 2026-05-30
- **Plan artifact**: `docs/reviews/mvp-truth-pivot-context-compaction-plan-20260530.md`
- **Gate classification**: `heavy`
- **Verdict**: **PASS_WITH_NON_BLOCKING**

---

## Summary

Plan 目标是将仓库 truth surface 从 release-maintenance / golden-promotion blockers 切换回 MVP fund analysis report generation 主线。Plan 只修改 docs（implementation-control.md、design.md、新建 current-startup-packet.md、以及 review 产物），不触碰 runtime、schema、score、snapshot、quality gate、golden fixtures、golden answers、promotion state 或 AGENTS.md。Route C 被明确标注为 accepted future design，当前实现保持 deterministic `fund-analysis analyze/checklist`。

Plan 结构清晰、硬约束覆盖完整、stop conditions 健全、validation plan 合理。未发现 blocking finding。以下是 4 条 non-blocking findings。

---

## Findings

### F1 (Low): `ChapterFactProvider` / `FundToolService` 是未来设计新命名词汇

**位置**: Plan Section 4, Section 7 (Route C Gate 1)

**问题**: Plan 在描述 Route C Gate 1 时引入了 `facet_recognizer`、`ChapterFactProvider`、`FundToolService` 三个新名称。这些名称在当前 `docs/design.md` 中不存在——当前设计中对应的概念是 `FundDataExtractor` 和 `StructuredFundDataBundle`。虽然 Plan Section 7 要求使用 `已接受的未来设计` 标签，但实现 agent 在写 Slice B 时需特别注意：这些名称只能出现在未来设计小节中，且应说明它们是 Route C Gate 1 的候选命名，不是当前代码中的类型。

**建议**: 在 Slice B 的 Route C 设计详情中加一句说明："Gate 1 组件名称（facet_recognizer、ChapterFactProvider、FundToolService）为 Route C 候选命名，不属于当前代码类型"。这不是 blocking——Plan 已有足够的标签保护机制——但能防止 review 阅读者误读。

---

### F2 (Low): startup packet 100-150 行目标在 9 个必填 section 下偏紧

**位置**: Plan Section 8

**问题**: Section 8 要求 startup packet 包含 9 个 required sections（标题、read order、当前主线、当前实现事实、Route C 未来路由、边界 guardrails、当前 residuals、prohibited actions、resume checklist），目标行数约 100-150 行。当前 implementation-control.md 的 Startup Packet 部分（仅 guardrails + field table）已占约 40 行，加上 9 个 section 的标题和内容，150 行是上限而非宽松目标。

**建议**: 无需修改 Plan。实现 agent 应优先保证信息完整而非强行压缩到 150 行以内。如果最终 160-180 行但结构清晰、每节精炼，仍然是合格的 startup packet。Plan 用词"about 100-150 lines"本身已留有余地。

---

### F3 (Info): Plan 未显式提及 `docs/implementation-control-p4.md`

**位置**: Plan Section 5 (files to modify)

**问题**: `docs/implementation-control-p4.md` 存在于项目结构中（见 design.md §9.0 目录树）。Plan Section 5 只允许修改 4 个文件，因此 `implementation-control-p4.md` 自动 out of scope，这是正确的。但 Plan 未提及是否需要在新的 control doc 或 startup packet 中引用该文件。

**建议**: 无需修改 Plan。实现 agent 在写 Slice A 或 Slice C 时，如果觉得 P4 质量体系控制文档值得在 read order 或 references 中提及，可以加一行链接；不加也不违反任何约束。

---

### F4 (Info): `docs/archive/` 目录的引用方式需实现 agent 自行判断

**位置**: Plan Section 6 (Slice A)

**问题**: 当前 implementation-control.md 的 Design / Control Alignment Rules 和 Historical Evidence Index 节已有 archive 目录的引用规则和内容。Plan Section 6 说"link to existing release-maintenance artifacts and archives"和"do not paste long release-maintenance ledgers"，但未具体说明 archive 引用节在新 control plane 中保留多少。

**建议**: 无需修改 Plan。当前 control doc 的 Historical Evidence Index 节本身就是精简索引（2 个 archive 文件路径 + 4 条说明），实现 agent 可直接保留或略作精简。Plan Section 13 的 stop condition 已覆盖了"不得删除历史 artifact 代替链接"这一硬约束。

---

## Hard constraint verification checklist

| 硬约束 | Plan 保护 | 验证 |
|--------|----------|------|
| 不改 runtime code | Section 3 non-goals; Section 5 仅允许 docs; Section 13 stop condition | PASS |
| 不改 schema / score / snapshot / quality gate / golden fixtures / golden answers / promotion | Section 3 non-goals; Section 9 evidence requirements 明确排除这些 | PASS |
| 不改 `AGENTS.md` | Section 3 non-goals 显式列出 | PASS |
| 不改 `docs/fund-analysis-template-draft.md` | Section 3 non-goals；若无法避免则 stop | PASS |
| 不删除历史 artifact | Section 3 non-goals; Section 13 stop condition | PASS |
| 不 commit / push / PR | Section 3 non-goals; Section 14 completion report | PASS |
| Route C 不写成当前实现 | Section 4 显式标注; Section 7 要求 status labels; Section 9 evidence 检查 | PASS |
| 保留 UI -> Service -> Host -> Agent | Section 6 guardrails; Section 7 reaffirm; Section 8 boundary guardrails | PASS |
| Host / Agent / dayu deferred | Section 4; Section 6 Open Residuals; Section 7 design wording | PASS |
| 不创建 fund_agent/host 或 fund_agent/agent | Section 3 non-goals; Section 8 prohibited actions | PASS |
| 不引入 dayu.host / dayu.engine 依赖 | Section 3 non-goals; Section 7 只在 Gate 5 允许 | PASS |
| 不运行 promotion / fixture promotion / strict correctness reruns | Section 3 non-goals | PASS |
| 不引用 untracked artifact 作为 accepted evidence | Section 0 branch baseline; Section 6 Open Residuals; Section 12 review checklist | PASS |
| Gate classification = heavy | Section 0; 要求两份独立 review | PASS |
| 至少两份独立 review | Section 12 | PASS |

---

## Truth alignment verification

1. **Plan Section 4 (Route C) vs AGENTS.md 模块边界**: Route C Gate 1-4 的 Service vs Agent/Fund 职责划分与 AGENTS.md §模块边界 一致。Gate 5 的 Host/Agent/dayu 约束与 AGENTS.md §Dayu 裁决 一致。PASS。

2. **Plan Section 6 (Current Truth Guardrails) vs design.md 当前设计章节**: Guardrails 中"当前 implementation remains deterministic"、"UI -> Service -> fund_agent/fund"、"Route C is accepted future design only"与 design.md §1.2, §2.1, §2.2 一致。PASS。

3. **Plan Section 7 (design.md update) vs design.md §5.4 已有未来设计节**: Plan 要求新增"已接受的未来设计：MVP LLM report generation route"节。design.md §5.4 已有"章节级写作审计闭环（已接受的未来设计）"节。实现 agent 应确保新增节与 §5.4 不产生语义冲突——§5.4 描述的是 report quality / chapter writing 的方法论框架，Route C 描述的是实现路由和 gate 序列，两者是互补关系而非替代关系。实现 agent 应注意这一点。Non-blocking：Plan 未显式要求说明新增 Route C 节与 §5.4 的关系。

4. **Plan 的 next entry 与当前 implementation-control.md 的 next entry**: 当前 next entry 是 `006597 same-fund unavailable field review / extractor projection gate`，Plan 拟改为 `MVP Gate 1: facet_recognizer + ChapterFactProvider/FundToolService contract gate`。这是本次 pivot 的核心目的，但 Plan 正确地将 006597/golden/strict-correctness 路由保留为 Open Residuals 而非删除。PASS。

---

## Validation plan assessment

Plan Section 11 的 validation plan 合理：
- `git diff --check` 适合 docs-only gate
- path-existence checks 覆盖了所有需要检查的文件
- 不运行 full ruff / pytest 的理由充分（docs-only scope）
- 如果实现意外改了 code，Section 13 stop condition 会触发

---

## Conclusion

Plan 足以安全完成 MVP truth pivot and context compaction gate。所有硬约束都有显式保护机制。stop conditions 覆盖了关键中断场景。F1-F4 均为 non-blocking，不影响 Plan 的可执行性和安全性。

**Verdict: PASS_WITH_NON_BLOCKING**
