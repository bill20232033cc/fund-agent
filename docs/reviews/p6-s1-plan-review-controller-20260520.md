# P6-S1 Plan Review - Controller - 2026-05-20

## Reviewed Target

- Plan: `docs/reviews/p6-s1-template-contract-manifest-plan-20260520.md`
- Scope: P6-S1 template contract manifest plan
- Design truth: `docs/design.md`
- Template source: `docs/fund-analysis-template-draft.md`
- Current code facts:
  - renderer chapter titles are private `_CHAPTER_TITLES` in `fund_agent/fund/template/renderer.py`
  - `fund_agent/fund/template/__init__.py` currently exports only renderer-facing APIs
  - `FundType` is defined in `fund_agent/fund/fund_type.py`

## Assumptions Tested

- A curated Python manifest is safer than runtime Markdown comment parsing for P6-S1.
- P6-S1 should stay in Capability and not touch Service/UI.
- P6-S1 should not perform contract audit, renderer alignment, ITEM_RULE parsing, or FQ5 upgrade.
- The implementation plan is specific enough for an implementation agent.

## Findings

### P6-S1-PR1-未修复-中-章节标题校验会诱导依赖 renderer 私有常量

- **位置**: `Schema Rules` 第 2 条、`Tests` 第 2 条、`Target Files` 的 renderer non-goal
- **问题类型**: 架构边界 / 过度耦合 / 不可直接实施
- **当前写法**: plan 要求 “Titles must match current `_CHAPTER_TITLES` in `fund_agent/fund/template/renderer.py`”，并要求测试证明 “Chapter titles match the renderer titles”；同时又要求 P6-S1 不修改 `render_template_report(...)`，renderer alignment 留到 P6-S2。
- **反例/失败场景**: 实施 agent 为了满足测试，可能在 `contracts.py` 中直接 import `renderer._CHAPTER_TITLES`，把 contract manifest 反向绑定到 renderer 的私有实现细节；或者复制两份标题，只用测试比较私有常量，导致后续 P6-S2 前 contract 与 renderer 仍有两个可写真源。
- **为什么有问题**: P6-S1 的目标是建立机器契约真源。让新 contract 依赖 renderer 私有常量，会让 renderer 继续事实拥有章节标题真源，削弱 manifest 的设计目标；复制两份标题又会制造 drift 风险。当前 plan 没有给出不依赖私有常量的可实施路径。
- **直接证据**:
  - `fund_agent/fund/template/renderer.py` 中章节标题常量名为 `_CHAPTER_TITLES`，带私有下划线。
  - `docs/reviews/p6-s1-template-contract-manifest-plan-20260520.md` 要求标题匹配该私有常量。
  - 同一 plan 又把 renderer alignment 推迟到 P6-S2。
- **影响**: 实施 Agent 可能引入 contract->renderer 的错误依赖；后续 P6-S2/P6-S3 需要返工标题真源；plan review 后仍难判断 P6-S1 的 manifest 是否真正成为后续 contract audit 的基础。
- **建议改法和验证点**:
  - 修订 plan：P6-S1 中不要让 production code import renderer private constants。
  - 在 `contracts.py` 中让 manifest 自带章节标题，并将其视为 P6 机器契约标题真源。
  - 测试改为：manifest 的 0-7 章标题与 `docs/design.md` 第 3.1 节定义的标题一致；不要要求 production code 依赖 `_CHAPTER_TITLES`。
  - 明确 P6-S2 负责让 renderer 复用 manifest 标题或通过公开 helper 对齐。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 中

## Open Questions

无 blocking open question。

## Residual Risks

- P6-S1 仍会手工复制 `docs/fund-analysis-template-draft.md` 的 contract 文本；短期可接受，但后续若模板文档继续编辑，需要通过 P6-S2/P6-S3 之后的 tests 和 review 防止 manifest drift。
- `ITEM_RULE` 留到 P6-S4，P6-S1 不能声称完整覆盖模板条件项。

## Conclusion

`fail` until P6-S1-PR1 is patched in the plan. Finding 修复后，该计划可以进入 P6-S1 plan re-review。
