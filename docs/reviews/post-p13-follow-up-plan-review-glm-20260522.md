# Post-P13 Follow-up Plan Review — AgentGLM（2026-05-22）

## Verdict

`PASS_WITH_FINDINGS`

计划选择合理、方向正确、scope 约束充分。4 个 finding 均可在后续 P14-S1 plan artifact 中修复，不阻塞 gate 推进。

## Review Target

- `docs/reviews/post-p13-follow-up-planning-20260522.md`

## Reference Truth

- `AGENTS.md`
- `docs/design.md`
- `docs/implementation-control.md`
- `docs/reviews/p13-main-branch-closeout-20260522.md`
- `docs/reviews/p13-pr-review-controller-judgment-20260522.md`
- `docs/reviews/p13-aggregate-deepreview-controller-judgment-20260522.md`

## Design Alignment Check

| 维度 | 结论 |
|------|------|
| 确定性 MVP 边界 | 通过。只消费已有 structured data，不引入 LLM、Dayu runtime、外部指数序列或新 source contract |
| FundDocumentRepository / source boundary | 通过。显式禁止 Service/UI/renderer/quality gate 绕过仓库（约束 #7） |
| Fund Capability ownership | 通过。字段语义、适用性、缺失解释归 Fund Capability（约束 #2、#3） |
| 模块边界（UI / Service / Capability） | 通过。不越界到 Application / Runtime / Engine |
| Dayu / Host / Engine / tool loop | 通过。显式排除（Non-goals） |
| E1/E2/E3 / Evidence Confirm | 通过。显式排除（Non-goals、约束 #5） |
| deterministic MVP constraints | 通过。不引入 LLM writing、语义审计或修复合同 |

## First-Principles Challenge: Is P14-S1 the Best Next Phase?

**结论：是。**

代码验证确认：

1. `index_profile` 和 `tracking_error` 已在 `SNAPSHOT_FIELD_ORDER` 中（`extraction_snapshot.py` 第 33、38 行），具备 observability。
2. 但它们**不在** `COMPARABLE_SUB_FIELDS_BY_FIELD` 中，correctness denominator 完全不覆盖这两个字段。
3. 它们**不在** `FIELD_PRIORITY_BY_NAME` 中，被标记为 `"UNMAPPED"` priority，FQ2 quality gate 完全不检查这两个字段。
4. 当前非指数基金使用 `extraction_mode="missing"` 处理不适用的 `index_profile`/`tracking_error`，与真正的数据缺失共享同一枚举值。

在上述状态下，任何后续 external adapter、计算链路或 methodology extraction 增加的复杂度都会把正确性问题分散到多个来源层，root cause 不再同源。先锁住已有字段的质量契约是正确的第一性原理选择。

**候选比较表验证**：所有 10 个候选项的排除理由与代码事实一致。特别是 "calculated tracking error" 和 "external index series adapter" 的 deferral 理由成立——当前连基础 denominator 都没有，计算和来源扩展只会增加不可回归的风险面。

## Findings

### F1（Medium）：UNMAPPED priority 未显式命名

**位置**：计划文档 "Required Constraints For Next Phase" 第 5 项（质量门控边界）

**问题**：当前 `index_profile` 和 `tracking_error` 在 `FIELD_PRIORITY_BY_NAME`（`extraction_score.py` 第 40-55 行）中没有条目，运行时被标记为 `"UNMAPPED"` priority。这意味着即使这两个字段进入 comparable snapshot，FQ2 也不会对它们做任何检查。计划的约束 #5 说了"denominator failure 是 block、warn、not-run 还是仅进入 golden diff"，但没有显式点名 "UNMAPPED priority 必须被消除" 这一前置条件。

**风险**：如果 P14-S1 plan 只添加 comparable sub-fields 而不处理 priority 映射，FQ2 仍然不会对新字段生效，quality gate 形同虚设。

**Required change**：在约束 #5 中增加显式要求："P14-S1 plan 必须为 `index_profile` 和 `tracking_error` 指定 `FIELD_PRIORITY_BY_NAME` 中的 priority（P0 或 P1），消除 UNMAPPED 状态。如果 priority 需要按基金类型条件化（如仅 index_fund/enhanced_index 为 P0，其余为 not_applicable），plan 必须说明条件化 priority 的实现路径。"

### F2（Medium）：ExtractionMode `missing` 与 `not_applicable` 合并风险

**位置**：计划文档约束 #4（缺失语义）

**问题**：当前 `ExtractionMode = Literal["direct", "derived", "estimated", "missing"]`（`extractors/models.py` 第 10 行）。非指数基金的 `index_profile`/`tracking_error` 使用 `extraction_mode="missing"` + `note` 来表达不适用。这与真正在指数基金年报中找不到数据时的 `extraction_mode="missing"` 共享同一枚举值。计划约束 #4 列出了 `missing`、`not_applicable`、`insufficient_disclosure`、`invalid_disclosure`、`conflicting_disclosure` 五种语义，但没有说明是否要扩展 `ExtractionMode` 枚举。

**风险**：如果不区分 `missing` 和 `not_applicable`，则 FQ2 coverage 检查会对非适用基金报出虚假的 "field coverage failure"，或者需要所有 downstream 消费者自行解析 `note` 字符串来判断适用性。

**Required change**：约束 #4 应明确要求 P14-S1 plan 做以下二选一裁决：(a) 扩展 `ExtractionMode` 增加 `not_applicable` 值，在 extractor 层显式区分；或 (b) 保持 `ExtractionMode` 不变，在 snapshot/score/gate 层通过 `classified_fund_type` 做条件化判断。两种路径的 trade-off 必须在 plan 中显式分析。

### F3（Low）：条件化 priority 实现复杂度未显式提及

**位置**：计划文档约束 #3（适用性矩阵）

**问题**：当前 `FIELD_PRIORITY_BY_NAME` 是静态映射，不支持按基金类型条件化。如果 P14-S1 决定 `index_profile`/`tracking_error` 仅对 index_fund/enhanced_index 为 P0（高优先），对其他类型为 not_applicable 或豁免，则需要修改 `_evaluate_field_score()` 的逻辑或 `FIELD_PRIORITY_BY_NAME` 的结构。计划的约束 #3 要求了适用性矩阵，但没有显式提到这一实现复杂度。

**风险**：复杂度本身不大（改一个 dict 为 dict-of-dicts 或加条件判断），但如果 P14-S1 plan 假设 priority 是静态的而不考虑条件化，可能在 implementation 阶段才发现需要改 score/gate 基础设施。

**Required change**：约束 #3 补充一句："如果适用性矩阵要求 priority 按基金类型条件化，P14-S1 plan 必须说明 `FIELD_PRIORITY_BY_NAME` 和 `_evaluate_field_score()` 的改动范围。"

### F4（Low）：enhanced_index fixture 可用性需确认

**位置**：计划文档约束 #6（Fixture 策略）

**问题**：约束 #6 正确要求覆盖 "enhanced-index applicable path"。但当前代码的 `_INDEX_APPLICABLE_FUND_TYPES = frozenset(("index_fund", "enhanced_index"))`，而 fixture 基础设施是否已有 enhanced_index 样本的年报 fixture 需要在 P14-S1 plan 阶段确认。如果当前 3 只样本基金（110011 主动、510300 指数、003003 债券）中没有 enhanced_index，则需新增 fixture 或在 plan 中明确声明 fixture 扩建范围。

**Required change**：约束 #6 补充："P14-S1 plan 必须确认当前 fixture 基础设施是否包含 enhanced_index 类型样本。如果不包含，plan 必须明确 fixture 扩建的最小范围。"

## Scope Challenge

| 审查维度 | 结论 |
|----------|------|
| 是否过宽 | 否。只消费已有字段，不引入新来源、新计算或新文档 |
| 是否过窄 | 否。从 snapshot observability 到 quality denominator 是最小必要步骤 |
| 是否隐藏实现 | 否。Explicit Out-of-scope 列表完整 |
| 是否隐藏 source adapter | 否。约束 #7 和 Non-goals 双重排除 |
| Quality gate 歧义 | 部分约束可更精确（见 F1、F3） |
| Fixture 缺口 | 已识别但需确认 enhanced_index 可用性（见 F4） |
| Denominator 定义缺口 | 已正确列为约束 #1，plan 阶段必须回答 |
| Stop condition | 有。约束 #10 要求正面接受标准 |

## Residual Owner Validation

计划文档的 Residual Owners 与 P13 closeout、PR review 和 aggregate deepreview 的 accepted residuals 完全一致，无遗漏、无冲突、无越权。

| Residual | Plan 中 Owner | P13 Closeout 中 Owner | 一致性 |
|----------|---------------|----------------------|--------|
| Calculated tracking error | Future data-source/calculation phase | Future P13 follow-up or separate data-source phase | 一致 |
| External index series adapter | Future source-contract phase | Future source-contract phase | 一致 |
| Index methodology / constituents | Future index document/source phase | Future index document/source-contract phase | 一致 |
| QDII tracking-error applicability | Future subtype-design phase | Future subtype-design phase | 一致 |
| E1-E3 / Evidence Confirm | Future audit architecture phase | 不在 P13 aggregate closeout 中（属于长期 residual） | 一致 |
| RR-13 duplicate `016492` | User / App source | User / App source | 一致 |
| `docs/repo-audit-20260521.md` | Controller / user | Controller / user | 一致 |

## Summary

P14-S1 quality-denominator 方向正确、scope 约束充分、residual owners 与 P13 closeout 一致。4 个 finding 中 2 个 Medium（F1 priority 映射、F2 ExtractionMode 适用性语义）需要在 P14-S1 plan 中显式裁决，但不阻塞 follow-up planning gate 推进。2 个 Low（F3 条件化 priority 实现、F4 enhanced_index fixture）属于 plan 阶段确认项。

**不修改生产代码，不提交，不 push，不创建 PR。**
