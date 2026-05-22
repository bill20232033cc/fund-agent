# Post-P13 Follow-up Planning（2026-05-22）

## Verdict

`SELECT_P14_S1_INDEX_PROFILE_TRACKING_ERROR_QUALITY_DENOMINATOR_PLAN_REVIEW`

P13 已经把跟踪误差直接披露链路合并到 `main`。下一 phase 不应继续扩大数据来源或计算范围，而应先补齐 P13 新增的 `index_profile` / `tracking_error` 质量覆盖缺口。P13 已经实现 snapshot observability；缺口不是“进入 snapshot”，而是这两个字段仍未进入 `COMPARABLE_SUB_FIELDS_BY_FIELD` 可比子字段、`GoldenAnswerRecord` / golden answer JSON correctness，且在 FQ2 `FIELD_PRIORITY_BY_NAME` / `ExtractionScore` 中仍可能落入 `UNMAPPED` 或未定义优先级。

推荐下一 gate：

```text
P14-S1 index_profile / tracking_error quality-denominator plan-review
```

推荐 planning artifact：

```text
docs/reviews/p14-s1-index-profile-tracking-error-quality-denominator-plan-20260522.md
```

## Goal

本 artifact 只完成 post-P13 follow-up planning / next phase selection：

- 从 P13 合并后的 residuals 中选择下一 phase；
- 明确为什么该 phase 是当前最短、最稳、最符合设计目标的下一步；
- 给下一份 plan-review handoff 留下约束、非目标、风险归属和验证方式；
- 不实现下一 phase，不修改生产代码、测试、README、`docs/design.md`、`docs/implementation-control.md` 或 `docs/repo-audit-20260521.md`。

## Evidence Used

- `AGENTS.md`
  - 当前项目要求第一性原理判断、证据同源、生产年报访问经过 `FundDocumentRepository`。
  - 基金类型判断优先于通用分析，指数 / 指数增强基金必须先应用对应 `preferred_lens`。
  - 审计和证据锚点属于 Fund Capability；Service/UI/Engine 不得越界读取文档来源。
- `docs/design.md`
  - 当前主链路是确定性 MVP：`UI -> Service -> Fund Capability`，不依赖 LLM 写作或外部 Dayu Host/Engine/tool loop。
  - `FundDocumentRepository` 是生产年报唯一入口，fallback taxonomy 必须保留 `not_found`、`unavailable`、`schema_drift`、`identity_mismatch`、`integrity_error`。
  - `preferred_lens` 明确指数基金关注跟踪误差、费率、规模流动性；指数增强基金关注超额收益来源和跟踪误差。
  - E1/E2/E3、Evidence Confirm、语义审计和修复合同仍是 v2 / 后续审计架构。
- `docs/implementation-control.md`
  - 当前 gate 是 `P13 merged / main-branch closeout`，下一入口是 `post-P13 follow-up planning / next phase selection`。
  - P13 已关闭：direct tracking-error disclosure merged；计算型跟踪误差、外部指数序列、方法论/成份股、QDII 适用性、comparable / golden / FQ2 coverage 都是 future residuals。
  - `docs/repo-audit-20260521.md` 和 RR-13 duplicate `016492` 保持排除。
- `docs/reviews/p13-main-branch-closeout-20260522.md`
  - P13 merge commit 为 `e2d8d381b93c8d1f547836a921ea8991f1a055d8`。
  - 已交付 typed `index_profile` / `tracking_error`、直接年报披露抽取、Service 风险检查权威迁移、renderer/audit 消费和 snapshot observability。
  - 明确已做 snapshot observability，但未做 FQ2 priority、comparable sub-fields 或 golden correctness denominator 覆盖。
- `docs/reviews/p13-pr-review-controller-judgment-20260522.md`
  - PR review 为 `ACCEPTED`，MiMo / GLM 均 `PASS`，CI `test` 成功。
  - accepted residuals 包含计算型跟踪误差、外部 index series adapter、index methodology / constituents extraction、QDII 适用性、comparable / golden / FQ2 coverage、RR-13、excluded repo-audit。
- `docs/reviews/p13-aggregate-deepreview-controller-judgment-20260522.md`
  - aggregate deepreview 为 `ACCEPTED`，本地 `pytest` 为 `424 passed`，`ruff check fund_agent tests` 和 `git diff --check HEAD` 通过。
  - prior code-review findings 已关闭。
- `docs/reviews/next-phase-selection-controller-judgment-20260522.md`
  - P13-S1 被选择时的必答约束已要求 tracking-error authority、外部指数序列边界、methodology / constituents 可用性分级、正面接受标准和 fixture 策略。
  - 这些约束支持 P13 第一片只做直接披露，不支持 post-P13 直接混入计算、外部 adapter 或 methodology/constituents extraction。

## Non-goals

- 不重新打开 P13 direct-disclosure implementation scope。
- 不实现计算型 tracking error，不引入 fund/index time series 计算。
- 不引入 external index series adapter、index methodology extraction 或 constituents extraction。
- 不设计或实现 QDII tracking-error 适用性规则。
- 不引入 E1/E2/E3、Evidence Confirm、LLM writing、Dayu runtime、Host、Engine 或 tool loop。
- 不修改 RR-13 duplicate `016492`，不编辑 source data。
- 不读取、发布、修改或纳入 `docs/repo-audit-20260521.md`。
- 不提交、不 push、不创建 PR。

## Candidate Comparison

| Candidate | Current value | Main blocker / risk | Selection |
|---|---|---|---|
| Future P13 calculated tracking error from fund/index time series | 可在直接披露缺失时补足指数基金核心指标 | 需要指数序列 identity、cache、provenance、failure taxonomy；和 external adapter 强耦合 | defer to later data-source phase |
| External index series adapter | 是计算型 tracking error 的前置 source contract | 引入外部数据源、identity mismatch、可用性和缓存边界；当前不应混在 post-P13 first follow-up | defer to dedicated source-contract phase |
| Index methodology / constituents extraction | 能补充第 1 章产品本质和指数风险解释 | 需要新文档/来源契约；与直接披露字段不是同一最小闭环 | defer to index document/source phase |
| QDII tracking-error applicability | 避免对 QDII 误套普通指数规则 | 需要 subtype-design 和规则口径，不应作为 quality denominator 的暗含实现 | defer to subtype-design phase |
| `index_profile` / `tracking_error` comparable / golden / FQ2 coverage | 直接锁住 P13 已交付字段，让质量门控覆盖新增能力，提升回归保护 | 必须先限定只消费现有结构化字段，不扩大抽取/计算/来源范围 | select |
| Future E1-E3 / Evidence Confirm audit architecture | 长期提升证据充分性与断言匹配审计 | 属于 v2 审计架构，会引入 LLM/evidence confirm 设计；当前 deterministic MVP 不应混入 | defer to future audit architecture phase |
| Evidence-display / ITEM_RULE cleanup | 改善报告展示和 C2 噪声 | 是体验/清理类 residual，产品正确性收益低于锁住 P13 新数据契约 | defer |
| Repo-hygiene candidates D-1, D-8/C-5, C-9 | 有维护价值 | 来源是 excluded repo-audit，当前任务明确不纳入 | defer; do not read excluded input |
| RR-13 duplicate `016492` | 可能影响精选池源数据质量 | 明确为 user / App source owner，不允许自动修复 | excluded |
| Excluded `docs/repo-audit-20260521.md` | 可能包含 repo hygiene 输入 | 明确排除，且当前为未跟踪文件 | excluded |

## Selected Next Phase

选择：

```text
P14-S1 index_profile / tracking_error quality-denominator
```

该 phase 的下一步仍是 plan-review，不是 implementation。它应设计如何把 P13 已经产出的结构化字段纳入现有 comparable / golden answer / FQ2 体系，使新增字段从“snapshot 可观察”升级为“可比较、可回归、可计入 FQ2 优先级或可解释排除”。

最小目标：

- 只消费 P13 已存在的 `index_profile` / `tracking_error` structured data；
- 明确哪些子字段进入 `COMPARABLE_SUB_FIELDS_BY_FIELD` 并写入 snapshot `comparable_values`；
- 明确哪些子字段进入 `GoldenAnswerRecord` / golden answer JSON correctness 分母；
- 明确 `index_profile` / `tracking_error` 在 FQ2 `FIELD_PRIORITY_BY_NAME` / `ExtractionScore` 中是 P0、P1、P2、`UNMAPPED` 还是按基金类型条件化处理；
- 明确 missing / not-applicable / disclosed-but-invalid / conflicting-data 的断言口径；
- 给出 index、enhanced_index、active/bond/QDII/FOF 非适用路径的 deterministic validation；
- 保持 comparable / golden / FQ2 coverage 与 source extraction/calculation 解耦。

## Quality Denominator Definition For P14-S1

P14-S1 中的 “quality denominator” 只能指当前代码里已经存在的三个确定性机制，不是新增抽象机制：

| Mechanism | Current implementation | P14-S1 scope | Explicitly not in scope |
|---|---|---|---|
| FQ2 priority / extraction score | `fund_agent/fund/extraction_score.py` 的 `FIELD_PRIORITY_BY_NAME`、`UNKNOWN_FIELD_PRIORITY="UNMAPPED"`、`ExtractionScoreResult`、`_build_score_row()`、`_missing_fields_by_priority()` 等评分路径 | 必须为 `index_profile` / `tracking_error` 选择 priority behavior，消除 implementation plan 中的 `UNMAPPED` 模糊性 | 不新增 FQ rule family，不重写 FQ0/FQ1/FQ3-FQ6，不改变现有 selected-fund pool 读取方式 |
| Snapshot comparable values | `fund_agent/fund/extraction_snapshot.py` 的 `COMPARABLE_SUB_FIELDS_BY_FIELD` 白名单和 snapshot `comparable_values` 输出 | 必须决定两个字段哪些稳定子字段进入白名单，或明确为何某字段暂不进入；如果进入，plan 必须列出精确子字段名 | 不把整块 nested value 直接放入 comparable，不新增外部 source，不把 methodology / constituents extraction 作为前置 |
| Golden correctness | `fund_agent/fund/golden_answer.py` 的 `GoldenAnswerRecord` / strict golden answer JSON，和 `fund_agent/fund/extraction_score.py` 的 `compare_snapshot_correctness()` | 必须决定 golden answer JSON 是否新增 `index_profile` / `tracking_error` records；如新增，plan 必须说明基金代码、字段名、子字段、expected_value、confidence、source | 不扩展 golden schema，不把人工未确认值写成 high confidence，不让 golden JSON 代替 extractor/source contract |

P14-S1 选择的最小范围应同时覆盖上述三个机制的 plan decision。implementation 可以分 slice 执行，但 plan-review 前必须明确每个机制是 “in scope with exact behavior” 还是 “explicitly excluded with reason”。不得继续使用“等价 denominator”绕开实际机制。

## Why Selected By First Principles / Design Goals

第一性原理判断：P13 的核心风险不是“缺少更多来源”，而是“新增结构化事实尚未进入足够强的质量契约”。在扩大数据来源前，必须先让已交付字段进入实际存在的 FQ2 priority、snapshot comparable values 和 golden correctness 决策，否则后续 external adapter、计算链路或 methodology extraction 增加的复杂度会把正确性问题分散到多个来源层，root cause 不再同源。

该选择符合当前设计目标：

- **确定性 MVP 优先**：只消费已有 structured data，不引入 LLM、Dayu runtime、外部指数序列或新 source contract。
- **Fund Capability ownership**：字段语义、适用性、缺失解释和审计仍归 Fund Capability；Service/UI 不越界读取文档来源。
- **证据同源**：P13 的直接披露字段来自年报路径；quality denominator 应验证同一结构化事实，而不是用外部 adapter 间接补证。
- **最小可交付**：相比 calculated tracking error，comparable / golden / FQ2 coverage 可以在不扩来源、不新增文档仓库实现的前提下独立完成。
- **防止 P13 回归**：一旦字段进入 comparable/golden/FQ2 决策，后续 renderer、audit、quality gate 或 source changes 更难静默破坏 tracking-error 表达。

## Required Constraints For Next Phase Plan

下一份 P14-S1 plan 必须先回答以下问题，未回答前不得进入 implementation：

1. **Denominator 定义**：只能使用实际机制：FQ2 `FIELD_PRIORITY_BY_NAME` / `ExtractionScore`、snapshot `COMPARABLE_SUB_FIELDS_BY_FIELD` / `comparable_values`、`GoldenAnswerRecord` / golden answer JSON correctness。不得再写“等价 denominator”而不绑定代码机制。
2. **字段范围**：只允许纳入 P13 已交付 structured fields；不得新增 calculated tracking error、external index series、methodology、constituents 或 QDII subtype rules。
3. **FQ2 priority 决策**：必须消除 `index_profile` / `tracking_error` 的 `UNMAPPED` 模糊性。plan 必须选择二者是 P0、P1、P2、继续 `UNMAPPED` 且显式排除，还是按基金类型条件化；如果条件化，必须说明实现区域是 `FIELD_PRIORITY_BY_NAME`、`_evaluate_field_score` / `_build_score_row` / `_missing_fields_by_priority` 或等价 scoring logic，而不是只改文案。
4. **Comparable sub-fields 决策**：必须列出每个进入 `COMPARABLE_SUB_FIELDS_BY_FIELD` 的精确子字段。候选必须来自 P13 已有结构化值，例如 `tracking_error.value_text` / `period_label` / `annualized` / `source_type`，以及 `index_profile.benchmark_identity_status` / `benchmark_index_name` / `benchmark_text` / `methodology_availability` / `constituents_availability`；plan 也可以排除部分候选，但必须给出稳定性理由。
5. **Golden correctness 决策**：必须说明 golden answer JSON 是否新增 `GoldenAnswerRecord`。如新增，必须说明使用哪些 fund code、field_name、sub_field、expected_value、confidence、source；如不新增，必须说明 why comparable coverage 不进入 correctness 分母。
6. **适用性矩阵**：明确 index_fund / enhanced_index / active_fund / bond_fund / qdii_fund / fof_fund 的 expected denominator behavior，尤其要说明非指数基金是 excluded / not_applicable 还是 counted-as-missing。
7. **非指数与 not_applicable 语义**：当前 `ExtractionMode` 只有 `direct` / `derived` / `estimated` / `missing`。P14-S1 plan 必须二选一：扩展 `ExtractionMode` 增加 `not_applicable`，或保持 enum 不变并用 `classified_fund_type` / applicability matrix 在 snapshot-score-gate 逻辑中排除非适用字段。plan 必须写清 trade-off：扩 enum 会触及 extractor/model/consumer/test 面，保持 enum 则要防止 non-index missing 被 FQ2 误计为质量失败。
8. **缺失与冲突语义**：区分 missing、not_applicable、insufficient_disclosure、invalid_disclosure、conflicting_disclosure；如果不新增 enum，必须说明这些语义落在 `note`、snapshot record、score logic 还是 golden comparison reason。
9. **质量门控边界**：说明 denominator failure 是 block、warn、not-run 还是仅进入 golden diff；不得扩大为 E1/E2/E3 或 Evidence Confirm。
10. **Fixture 策略**：必须基于现有 P3/sample matrix 和 golden answer JSON 说明 fixture 来源。`510300` 当前可作为 index_fund disclosed tracking_error path 候选；plan 必须确认是否使用它。enhanced_index fixture 当前不能假设已存在，plan 必须先证明已有 fixture 覆盖 enhanced_index，或最小新增一个 deterministic fixture。
11. **Validation / exit criteria**：必须列出具体命令和预期基线，至少包括 targeted snapshot/score/golden tests、P1/P3 sample matrix、quality gate 或 extraction score service 相关测试、ruff、full suite。预期 baseline 应不低于 P13 closeout 的 full suite `424 passed`，除非 plan 明确说明测试数量变化原因。
12. **Required behavior assertions**：必须覆盖 index_fund disclosed path、enhanced_index applicable path、non-index not_applicable/excluded path、missing tracking_error、conflicting disclosure fail-closed、comparable_values 输出、golden correctness match/mismatch/unavailable 断言、full suite no regression。
13. **Source boundary**：任何年报数据仍必须通过 `FundDocumentRepository`；Service/UI/renderer/quality gate 不得直接调用具体来源、PDF cache 或下载 helper。
14. **Failure taxonomy preservation**：如 plan 触及文档来源错误表达，必须保留 `not_found` / `unavailable` 可 fallback、`schema_drift` / `identity_mismatch` / `integrity_error` fail-closed。
15. **Docs decision**：如仅修改 Fund/quality/golden/test 行为，必须同步判断是否更新 `fund_agent/fund/README.md` 与 `tests/README.md`；不得改根 README，除非用户入口或命令变化。
16. **Positive acceptance criteria**：必须写明可直接验证的 pass signals，而不只列禁止项。

## Explicit Out-of-scope Items

- P13 direct-disclosure implementation 返工。
- 基于基金净值和指数时间序列计算 tracking error。
- 新增外部指数行情、指数成份、指数方法论来源。
- 对 QDII tracking-error 做业务适用性改判。
- E1/E2/E3、Evidence Confirm、LLM semantic audit、RepairContract。
- Dayu runtime、Host、Engine、tool loop 或外部 Dayu API。
- RR-13 duplicate `016492`。
- `docs/repo-audit-20260521.md` 及其 D-1、D-8/C-5、C-9 候选项。
- README、`docs/design.md`、`docs/implementation-control.md` 更新，除非下一 phase plan/review 后的 implementation scope 明确要求。
- 泛化地把字段“提升进 snapshot”的表述；P13 已有 snapshot observability，P14-S1 只讨论明确选中的 comparable sub-fields、golden correctness 和 FQ2 priority。

## Risks / Residual Owners

| Risk / residual | Owner / destination | Handling now |
|---|---|---|
| Calculated tracking error from time series remains absent | Future data-source/calculation phase | deferred |
| External index series adapter remains undefined | Future source-contract phase | deferred |
| Index methodology / constituents extraction remains missing | Future index document/source phase | deferred |
| QDII tracking-error applicability remains unmodeled | Future subtype-design phase | deferred |
| E1-E3 / Evidence Confirm still not implemented | Future audit architecture phase | deferred |
| Evidence-display / ITEM_RULE cleanup remains open | Future cleanup or rule-display slice | deferred |
| Repo hygiene D-1, D-8/C-5, C-9 | Future repo-hygiene phase if explicitly selected | deferred; excluded input not read |
| RR-13 duplicate `016492` | User / App source | excluded |
| `docs/repo-audit-20260521.md` | Controller / user | excluded and untouched |

## Recommended Next Gate

Proceed to:

```text
P14-S1 index_profile / tracking_error quality-denominator plan-review
```

The next planning agent should create:

```text
docs/reviews/p14-s1-index-profile-tracking-error-quality-denominator-plan-20260522.md
```

The next plan should be handoff-ready for implementation only after plan review and any re-review close all FQ2 priority, comparable sub-field, golden correctness, applicability, fixture, quality gate, and source-boundary questions.

## Required P14-S1 Plan Exit Criteria

P14-S1 plan-review 通过前必须把以下 exit criteria 写成可验证清单：

- Validation commands:
  - targeted snapshot tests for comparable values;
  - targeted extraction score / FQ2 priority tests;
  - targeted golden answer correctness tests;
  - existing P3/sample matrix integration tests, including current `tests/fund/integration/test_p1_sample_matrix.py` if selected;
  - quality gate or extraction score service tests if scoring output changes;
  - `ruff check fund_agent tests`;
  - full `pytest` suite with no regression from the P13 `424 passed` baseline unless test count changes are explained.
- Behavioral assertions:
  - `510300` or another explicitly chosen index_fund fixture exercises disclosed `tracking_error` and expected `index_profile` comparable sub-fields;
  - enhanced_index applicable path is covered by an existing fixture or by a minimal new deterministic fixture;
  - active/bond/QDII/FOF non-index paths are excluded / not_applicable according to the selected semantics, not silently counted as FQ2 failures;
  - missing tracking_error remains distinguishable from non-applicable tracking_error;
  - conflicting tracking-error disclosure remains fail-closed and does not create false golden correctness matches;
  - comparable values appear only for whitelisted sub-fields;
  - golden answer JSON assertions cover match, mismatch, and unavailable / not-in-denominator behavior as applicable;
  - full suite and ruff pass.

## Validation For This Docs-only Artifact

Performed / required validation for this artifact:

- Branch preflight: current branch is `docs/post-p13-follow-up-planning`, not a protected trunk branch.
- Worktree preflight: existing untracked `docs/repo-audit-20260521.md` was observed and left untouched.
- File existence check before writing: `docs/reviews/post-p13-follow-up-planning-20260522.md` did not previously exist.
- Scope validation: this artifact adds only `docs/reviews/post-p13-follow-up-planning-20260522.md`.
- No production code, tests, README, `docs/design.md`, `docs/implementation-control.md`, source data, RR-13 data, or `docs/repo-audit-20260521.md` were modified.
- No test suite is required for this docs-only planning artifact; final validation should run `git diff --check HEAD` and confirm `git status --short` shows only this new artifact plus pre-existing excluded untracked files.
