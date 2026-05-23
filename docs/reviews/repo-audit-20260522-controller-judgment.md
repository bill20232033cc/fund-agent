# Repo Audit 20260522 Controller Judgment（2026-05-22）

## Verdict

`PARTIALLY_ACCEPTED`

`docs/repo-audit-20260522.md` 的核心高优先级判断成立：`docs/design.md` 已落后于 P9-P13 代码事实，需要更新。
Controller 已按第一性原理融合 `docs/design0522.md` 到 `docs/design.md`，但没有无条件采纳审计报告中的所有建议，
因为该报告基于 `main` commit `b7117876`，而当前工作流已推进到 P14/P15 planning，部分项目管理事实已经过期。

## First-Principles Criteria

裁决依据不是“审计报告列了建议就执行”，而是：

1. 是否降低当前真实风险，而不是修复已经过期的历史状态。
2. 是否符合 AGENTS.md 的模块边界和 `FundDocumentRepository` 文档访问边界。
3. 是否让设计真源更贴近当前代码，而不是把未来设计写成已实现事实。
4. 是否保持 phaseflow resume 和后续 implementation 的低认知负担。
5. 是否避免无明确 owner 的大范围清理。

## Accepted Now

| Audit item | Decision | Handling |
|---|---|---|
| N-1 / N-5: `design.md` 未反映 `final_judgment.py`、P9-P13 变更 | accepted | `docs/design.md` 已更新到 v2.0，补充 Service 关键类型、最终判断派生、模板渲染和审计事实。 |
| N-2: Dayu-Agent 状态过时 | accepted | `docs/design.md` 明确 `dayu-agent` 已从依赖移除，Dayu 仅作方法论参考；后续 runtime 能力必须项目内化。 |
| N-6 / C-8: `config/paths.py` 未记录 | accepted | `docs/design.md` 将 `fund_agent/config/paths.py` 记录为静态默认路径常量，不引入 prompt/config runtime 误解。 |
| N-7: Service 类型未记录 | accepted | `FinalJudgment`、`FinalJudgmentDecision`、`AnalyzeMode`、`FundAnalysisDeveloperOverrides`、`QualityGatePolicy` 已补入设计文档。 |
| N-8: ITEM_RULE 审计 API 未记录 | accepted | `evaluate_template_item_rule`、`TemplateItemRuleAuditContext`、`rendered_segment_present` 和后渲染校验机制已补入设计文档。 |
| D-1: design.md 缺项目结构树 | accepted with scope control | 已补主要模块结构树，但标注为边界导读，不作为逐文件 inventory，避免随代码漂移。 |
| P13 tracking error disclosure 文档缺口 | accepted and extended | 设计文档补到 P14/P15：`index_profile` / `tracking_error` 条件质量分母、production `tracking_error` golden 需 reviewed direct evidence。 |

## Rejected Or Already Obsolete

| Audit item | Decision | Rationale |
|---|---|---|
| “仓库为准，本地 workspace 版本已过时” | rejected as written | 当前 controller 工作区是最新 phaseflow 工作区；设计真源应对齐当前代码与 control reconciliation，而不是无条件以旧审计基准覆盖。 |
| N-4: Startup Packet 分支仍为 `docs/p13-main-closeout` | obsolete | 当前 `docs/implementation-control.md` 已记录 `docs/post-p14-follow-up-planning`，不是报告中的旧状态。 |
| N-10: PR 9 open | obsolete | PR 9 已 squash merge，控制文档已记录 P14 merge closeout。 |
| N-11: 2 个 open issues | obsolete | 当前 `gh issue list --state open` 返回空列表。 |
| D-8 / C-5: `fund/tools/__init__.py` | already closed | 已删除，设计文档继续声明当前无通用 Fund tool runtime。 |
| “关闭 PR#5” | requires explicit external-action authorization | PR 5 仍 open，但关闭 GitHub PR 属于外部状态变更；本裁决只记录建议，不在当前 gate 自动执行。 |

## Deferred Follow-up Candidates

| Audit item | Decision | Owner / Destination |
|---|---|---|
| N-3: implementation-control 版本号仍为 v1.0 | defer | 可在后续 control-doc hygiene phase 处理；当前 phaseflow 主要依赖 Startup Packet / Active Gate Ledger，而非版本号。 |
| C-1: `cli.py type: ignore` | defer | 真实存在，但属于 UI typing hygiene；不阻塞 P15 evidence acquisition。 |
| C-2: 魔法数字 | defer / partly mitigated | 多数核心阈值已抽为常量；剩余需要专项代码审计确定，不应从 repo audit 间接证据直接改代码。 |
| C-3: 串行抽取性能 | defer | 性能优化需先定义真实瓶颈和可接受并发边界，不能在 evidence gate 中扩 scope。 |
| C-4: 本地路径硬编码 | defer / partly closed | `fund_agent/config/paths.py` 已收口默认路径；剩余测试/README 示例路径不是同一风险等级。 |
| C-9: `docs/reviews/` 目录膨胀 | defer | phaseflow 要求 durable review artifacts；清理需要单独 artifact retention policy，不在当前 phase 删除历史证据。 |

## Design Fusion Notes

本轮没有直接照搬 `docs/design0522.md`。融合时刻意修正了以下口径：

- 保留“若设计、总控和代码冲突，以当前代码事实与最新 control-doc reconciliation 为准”的约束。
- 不把 `docs/repo-audit-20260522.md` 写成设计真源关联文档。
- 年报来源写作 EID/证监会资本市场统一信息披露平台主源 + Eastmoney fallback，而不是把 Eastmoney 或其他来源提升为同级主源。
- 项目结构树只作为模块边界导读，不作为逐文件 inventory。
- `tracking_error` 生产 golden rows 保持 P15 guardrail：必须先有 reviewed direct observed disclosure evidence。

## Next Step

Commit `docs/design.md` and this judgment artifact, then resume P15-S1A evidence-acquisition implementation with the
updated design truth.
