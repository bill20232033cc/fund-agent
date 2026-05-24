# Release Maintenance Chapter-Audit Report Pipeline Candidate

> Date: 2026-05-24
> Branch: `codex/v0-release-readiness-plan`
> Work unit: design-candidate capture
> Result: accepted as next design candidate

## Trigger

用户反馈当前积极报告质量不足，并指出 Dayu 的写作体系值得借鉴：先分章写作，每章单独通过规则审计和 LLM 审计，每条判断必须有来源出处；审计不通过时修复或重写并重新审计；最终章根据前序章节结果生成，第 0 章最后总结。

## Decision

将下一 release-maintenance candidate 设为 `chapter-audit report pipeline design plan/review`。

本次只沉淀设计候选，不改变当前 v0 deterministic renderer、CLI、Service、Agent 层基金能力、quality gate、审计实现或 Host/Agent 依赖。

## Design Direction

未来报告质量升级应从“一次性模板填充”演进为“章节级写作 -> 审计 -> 修复/重写 -> 总装”：

- Chapters 1-9 先独立写作，每章声明输入 facts、必须回答项、禁止覆盖项、证据锚点和章节结论。
- 每章必须通过规则审计和 LLM 审计；规则审计覆盖结构、锚点、CHAPTER_CONTRACT / ITEM_RULE、数值闭合与边界条件，LLM 审计覆盖证据是否支撑断言、语义越界、投资建议措辞和读者可理解性。
- 审计失败产生 `RepairDecision`：可修补问题走 patch；结构错误、关键逻辑不成立或证据缺失导致不可修补时整章 regenerate；修复后必须重新审计。
- Chapter 10 最终判断只能消费 Chapters 1-9 accepted 结构化结论和 quality gate 状态。
- Chapter 0 执行摘要最后生成，只能总结 Chapters 1-10 accepted 结论，不引入新事实。
- LLM 写作、审计和修复不得直接读取 PDF/cache/source helper；事实必须来自 `FundDocumentRepository` 派生的 evidence/fact store。
- 若未来需要 session/run/cancel/resume/outbox、章节任务并发或写作 agent 调度，必须先开独立 Host/Agent gate：Host 使用 `dayu.host`，Agent 执行内核使用 `dayu.engine`。

## Artifact Policy

后续评分、数据源迭代、写作脚本迭代和报告质量调参会产生大量本地 run 产物。默认应落在 ignored run directories：

- `reports/scoring-runs/`
- `reports/data-source-runs/`
- `reports/writing-runs/`
- `reports/smoke/`
- temp directories

只有经人工复核后要作为长期基准的输入，才进入 `docs/` 或 curated fixture。

## Non-Goals

- 不把当前 8 章 renderer 改写为 0-10 章。
- 不声明 LLM audit、Evidence Confirm、repair loop 已实现。
- 不创建 `fund_agent/host` 或 `fund_agent/agent` 占位包。
- 不接入外部 `dayu-agent` runtime。
- 不改变 quality gate block/warn/off 语义。
- 不提交运行产物或临时报告。

## Validation

- `docs/design.md` 新增章节级写作审计闭环设计候选。
- `docs/implementation-control.md` Startup Packet / Resume checklist 指向下一 design gate。
- `.gitignore` / `README.md` / `tests/README.md` 明确本地 run 产物目录。
