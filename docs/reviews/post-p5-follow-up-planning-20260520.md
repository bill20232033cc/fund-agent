# Post-P5 Follow-up Planning - 2026-05-20

## Verdict

Post-P5 follow-up planning is accepted.

P5 已经完成并合入 `main`。quality gate 已进入 `fund-analysis analyze` 主链路，P4/P5 的主要质量保护缺口已经关闭。下一阶段第一优先级不应继续堆 extractor 或自动估值映射，而应把模板中的 `CHAPTER_CONTRACT` / `ITEM_RULE` 从文档约束推进为 Capability 层可消费的机器契约。

下一 gate：`P6-S1 template contract manifest plan/review`。

## Inputs

- Design truth: `docs/design.md`
- Global control doc: `docs/implementation-control.md`
- P4/P5 control doc: `docs/implementation-control-p4.md`
- Template source: `docs/fund-analysis-template-draft.md`
- P5 merge: PR 4 `https://github.com/bill20232033cc/fund-agent/pull/4`
- P5 merge commit: `d33b901fd1bee9f85206df461cc6419a813bcbae`

## First Principles

当前系统已经能生成 8 章报告、执行程序审计、生成 snapshot/score/quality gate，并在主链路阻断低质量输入。剩余高价值问题不是“能不能多抽一个字段”，而是“模板规则是否能被程序稳定检查”。

`docs/design.md` 明确把模板驱动、`CHAPTER_CONTRACT`、`must_answer`、`must_not_cover`、`preferred_lens` 和证据可审计作为核心机制。当前代码里的 `render_template_report(...)` 固定输出 8 章，但 `CHAPTER_CONTRACT` 仍主要停留在 `docs/fund-analysis-template-draft.md` 的文档注释中；P5 的 FQ5 也只能做到 `preferred_lens_resolvability`，不能校验实际章节是否遵守对应 lens 和章节契约。

因此 P6 的第一优先级应是建立机器可读模板契约，而不是引入 LLM 审计或自动把温度计映射为估值判断。没有同源规则前，自动估值映射会把外部数据解释成投资判断，风险高于收益。

## Boundary Judgment

- Capability 层负责 `CHAPTER_CONTRACT` / `ITEM_RULE` 解析、模板章节契约、preferred_lens 应用和审计规则。
- Service 层只负责编排模板渲染和审计，不理解具体章节规则。
- UI 层只展示结果和参数，不做模板规则判断。
- 新契约必须以当前代码事实为准，不把未来 LLM 写作能力提前写成已实现。
- 不直接从任意基金文档文件系统读取数据；本阶段若读取模板资产，只读取 repo 内模板/契约资产，不读取年报 PDF/cache。

## P6 Candidate Backlog

| Slice | Priority | Owner | Scope | Acceptance signal |
|---|---:|---|---|---|
| P6-S1 | P0 | template contract manifest slice | 建立机器可读 `CHAPTER_CONTRACT` manifest，覆盖 0-7 章的 `must_answer`、`must_not_cover`、`required_output_items`、`preferred_lens`，并提供 Capability 层加载/校验接口 | tests 能断言 8 章契约完整、基金类型能解析到 lens、缺字段/非法 chapter id 失败闭合 |
| P6-S2 | P0 | renderer contract alignment slice | 让当前 `render_template_report(...)` 与机器契约对齐，至少暴露每章 stable chapter id/title，并为后续审计提供可定位章节块 | 程序能把 report Markdown 切成 0-7 章并关联 contract；现有报告输出不破坏 |
| P6-S3 | P1 | programmatic contract audit slice | 在程序审计中增加首版 contract audit，校验 `required_output_items`、章节禁止内容和最小证据规则，不调用 LLM | 缺 required item 或出现 must_not_cover 内容时生成明确 audit issue；测试覆盖 failure paths |
| P6-S4 | P1 | ITEM_RULE manifest slice | 将模板中的 `ITEM_RULE` 机器化，首版只覆盖 deterministic optional/conditional 条目，不做 LLM 判断 | 条件缺失时能证明“删除整段”或“显式未披露”的行为符合规则 |
| P6-S5 | P2 | quality gate FQ5 upgrade slice | 在机器契约存在后，把 FQ5 从 `preferred_lens_resolvability` 升级为实际 contract/lens 应用检查 | `score.json` / `quality_gate.json` 能说明 lens 是 resolved、not_applicable 还是 mismatch |
| P6-S6 | Human | selected-fund source reconciliation | 核对 `docs/code_20260519.csv` 中重复 `016492` 的 App 源数据 | 用户/App 源确认后再更新 CSV；不由代码自动裁决 |

## P6-S1 Plan Requirements

P6-S1 进入实现前必须先形成 plan/review artifact，至少回答：

1. 机器契约资产放在哪里：Capability 代码常量、repo 配置文件，还是由 `docs/fund-analysis-template-draft.md` 解析生成。
2. 章节 ID、标题、`must_answer`、`must_not_cover`、`required_output_items`、`preferred_lens` 的稳定 schema。
3. 基金类型到 preferred_lens 的映射是否复用现有 `FundType`，避免新旧类型名并存。
4. 契约加载失败、缺章、缺 lens、非法 item rule 时如何 fail closed。
5. 如何保证契约不会越界到 Service/UI，也不会把 v2 LLM 审计提前混入 MVP 程序审计。

## Deferred But Tracked

| Risk | Decision |
|---|---|
| RR-13 / `016492` duplicate | human-owned；需要用户/App 源确认，不作为 P6-S1 代码阻塞项 |
| RR-16 / correctness denominator still limited | P6-S1/S5 为后续 contract-aware correctness 和 FQ5 升级提供基础；不在 P6-S1 直接扩大 extractor 输出 |
| RR-4 / thermometer blocked | P5-S7 已提供 read-only Service/CLI 和 unavailable fallback；自动映射为 `valuation_state` 仍 deferred，除非先有同源估值规则 |
| RR-7 / item-level evidence confirm | 进入 v2 Evidence Confirm；P6-S3 只做 deterministic contract audit，不做 PDF 二次证据确认 |
| LLM audit E1/E2/E3/C1/C2 | v2 scope；P6 先补程序可判定的 contract surface |

## Gate Decision

当前 gate 从 `post-P5 follow-up planning` 推进为 `post-P5 follow-up planning accepted`。

下一步进入 `P6-S1 template contract manifest plan/review`。在 P6-S1 plan 通过前，不应直接实现 contract loader 或改动 renderer。
