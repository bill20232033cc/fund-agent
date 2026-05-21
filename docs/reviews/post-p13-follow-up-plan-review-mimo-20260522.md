# Post-P13 Follow-up Plan Review — AgentMiMo（2026-05-22）

## Verdict

`PASS_WITH_FINDINGS`

Phase selection P14-S1 index_profile / tracking_error quality-denominator 是 P13 后最短、最稳的下一步。但 planning artifact 对"quality denominator"的具体定义、字段优先级分配、退出条件和非指数基金路径存在 6 个可修 findings，均可在 plan-review artifact 内闭环，不阻塞 phase selection 本身。

## Review Target

- `docs/reviews/post-p13-follow-up-planning-20260522.md`

## Reference Truth

- `AGENTS.md` — 硬约束、模块边界、基金分析原则
- `docs/design.md` — 设计真源：确定性 MVP、FundDocumentRepository、quality gate FQ0-FQ6、preferred_lens
- `docs/implementation-control.md` — 实施总控：P13 已合并、gate 状态、residual owners
- `docs/reviews/p13-main-branch-closeout-20260522.md` — P13 merge 证据与 residual owners
- `docs/reviews/p13-pr-review-controller-judgment-20260522.md` — PR 7 接受、residuals 明确
- `docs/reviews/p13-aggregate-deepreview-controller-judgment-20260522.md` — aggregate PASS、snapshot promotion 为 residual

## Codebase Verification

Review 过程中对以下代码事实做了独立验证：

- `fund_agent/fund/extraction_snapshot.py`: `SNAPSHOT_FIELD_ORDER` 已含 `index_profile` 和 `tracking_error`（16 字段）；`COMPARABLE_SUB_FIELDS_BY_FIELD` 明确排除两者，docstring 注释"P13 新增指数画像和跟踪误差观测字段，但不进入可比值分母"。
- `fund_agent/fund/extraction_score.py`: `FIELD_PRIORITY_BY_NAME` 不含 `index_profile` 或 `tracking_error`，两者在 FQ2/FQ2F 聚合中优先级为 `UNMAPPED`，不参与 P0/P1 阻断判定。
- `fund_agent/fund/quality_gate.py`: FQ2 基于 `value_present` / `anchor_present` 布尔值判定 coverage/traceability；`comparable_values` 是 golden answer correctness 比对的独立机制，不是 FQ2 分母。
- `fund_agent/fund/golden_answer.py`: `GoldenAnswerRecord` 按 `(fund_code, field_name, sub_field)` 组织，当前 golden JSON 不含 `index_profile` 或 `tracking_error` 条目。
- `fund_agent/fund/extractors/models.py`: `IndexProfileValue`（12 字段）和 `TrackingErrorValue`（18 字段）均为 typed dataclass，仅 `index_fund` / `enhanced_index` 适用。

## Findings

### F-1: "Quality denominator" 概念未定义 — 必须明确具体机制

**Severity**: HIGH（plan scope ambiguity）

**Observation**: Artifact Required Constraints #1 要求"明确 `index_profile` / `tracking_error` 进入哪个现有分母，或是否新增等价 denominator"，但 artifact 自身的 Goal 和最小目标均未回答此问题。"quality denominator" 在代码中不存在对应概念；实际存在三个独立机制：

| 机制 | 代码位置 | 当前状态 | 功能 |
|---|---|---|---|
| FQ2 field priority | `extraction_score.py` FIELD_PRIORITY_BY_NAME | 两字段 UNMAPPED | 决定是否参与 P0/P1 coverage/traceability 聚合 |
| comparable sub-fields | `extraction_snapshot.py` COMPARABLE_SUB_FIELDS_BY_FIELD | 两字段排除 | 决定 snapshot record 是否携带可比子字段值 |
| golden answer records | `golden_answer.py` GoldenAnswerRecord | 两字段无条目 | 决定 correctness 比对是否覆盖该字段 |

Artifact 将这三个机制笼统称为"golden/FQ2 denominator 或等价质量分母"，但没有指定 P14-S1 具体改哪些、不改哪些。

**Required change**: 在最小目标中明确列出 P14-S1 的具体机制变更目标，例如：
- 是否为 `index_profile` / `tracking_error` 分配 FQ2 优先级（P0/P1/P2）？
- 是否将两字段加入 `COMPARABLE_SUB_FIELDS_BY_FIELD`？
- 是否为两字段创建 golden answer 条目？
- 如果以上都不是，"quality denominator" 具体指什么新机制？

---

### F-2: FQ2 优先级分配未指定 — 阻断/警告行为不确定

**Severity**: HIGH（gate behavior ambiguity）

**Observation**: `FIELD_PRIORITY_BY_NAME` 是 FQ2/FQ2F 阻断语义的决定因素。当前 `index_profile` 和 `tracking_error` 为 `UNMAPPED`，不参与 P0/P1 聚合。artifact 的 Required Constraints #5 要求"说明 denominator failure 是 block、warn、not-run 还是仅进入 golden diff"，但未指定两字段的优先级。

这直接影响 gate 行为：
- 如果 `tracking_error` 设为 P0，则该字段 `value_present=False` 时 FQ2 BLOCK。
- 如果设为 P1，则 FQ2 WARN。
- 如果保持 UNMAPPED 或设为 P2+，则不进入 FQ2/FQ2F 聚合。

对于非指数基金，`tracking_error` 的 `extraction_mode` 为 `missing`（非指数基金不适用），如果设为 P0 且不区分 not_applicable，会导致非指数基金被 FQ2 误阻断。

**Required change**: 在 Required Constraints 中新增一条，要求 P14-S1 plan 明确：
- `index_profile` 和 `tracking_error` 的 FQ2 优先级；
- 非指数基金 `extraction_mode="missing"` 且 priority=P0 时的 gate 行为（是排除出分母、还是以 not_applicable 不计入 fail）。

---

### F-3: 非指数基金路径 stop condition 不明确

**Severity**: MEDIUM（scope boundary）

**Observation**: artifact 最小目标第 5 条要求"给出 index、enhanced_index、active/bond/QDII/FOF 非适用路径的 deterministic validation"。但代码事实是：当前实现已经对非指数基金强制 `extraction_mode="missing"` 并附带 note（`profile.py:_build_index_profile()` 和 `data_extractor.py:_tracking_error_for_fund_type()`）。这意味着"非适用路径"已经存在。

P14-S1 的真正问题是：当 `extraction_mode="missing"` 且原因为"非指数基金不适用"时，该字段在 FQ2/golden/comparable 中如何处理？是：
- (a) 从 FQ2 分母中排除（不计入 fail）？
- (b) 以 `not_applicable` 状态计入分母但不触发 fail？
- (c) 保持当前 UNMAPPED 状态不变？

Artifact 未指定选择。

**Required change**: 明确 P14-S1 对 not_applicable 路径的处理策略，至少指定 (a)(b)(c) 中的选择。

---

### F-4: 缺少明确退出条件 / 正面验收标准

**Severity**: MEDIUM（gate ambiguity）

**Observation**: artifact Required Constraints #10 要求"必须写明可直接验证的 pass signals，而不只列禁止项"。但 artifact 自身的"最小目标"只列了 6 条目标，没有退出条件。没有说明 P14-S1 implementation 完成时：
- 需要跑多少测试、什么命令通过？
- `index_profile` / `tracking_error` 在 snapshot/golden/quality gate 中的具体预期行为是什么？
- 哪些 fixture 基金需要覆盖？
- 完整测试套件 baseline 是多少（当前 424 passed）？

**Required change**: P14-S1 plan 必须包含退出条件，至少包括：
- 验证命令和预期通过数；
- 至少一个指数基金 fixture 的 `index_profile` / `tracking_error` 进入 comparable/golden 的端到端验证；
- 至少一个非指数基金 fixture 的 not_applicable 路径验证；
- full suite baseline 不回归。

---

### F-5: Fixture 策略缺乏现有基础设施衔接

**Severity**: LOW（implementation detail）

**Observation**: artifact Required Constraints #6 要求至少 5 类 fixture 覆盖。但未说明这些 fixture 是：
- 复用 P13 已有的 deterministic text fixtures（如 `tests/fixtures/fund/extractors/` 下的文本夹具）？
- 还是需要新增真实 index fund 年报 fixture？
- 还是在现有 P3 端到端矩阵（`110011` / `510300` / `000171`）中新增断言？

当前 P3 矩阵的 `510300` 是 `index_fund`，已有 `index_profile` / `tracking_error` snapshot 记录；但 golden answer JSON 中无这两个字段的条目。P14-S1 plan 应说明是否需要为 `510300` 新增 golden answer 标注。

**Required change**: 在 fixture 策略中说明与现有 P3 矩阵和 golden answer JSON 的衔接方式。

---

### F-6: Candidate Comparison 表对 E1-E3 / Evidence Confirm 的排除理由可加强

**Severity**: LOW（documentation clarity）

**Observation**: Candidate Comparison 表中 E1-E3 / Evidence Confirm 的排除理由是"属于 v2 审计架构，会引入 LLM/evidence confirm 设计"。这与 `AGENTS.md` 和 `docs/design.md` 一致。但同一表中"Snapshot promotion"被选中时的描述"直接锁住 P13 已交付字段，让质量门控覆盖新增能力"隐含了一个假设：snapshot promotion 等于 quality gate 覆盖。实际上 snapshot 记录已存在（FQ2 覆盖），缺的是 comparable 和 golden。这一细微区别不影响 phase selection，但会让后续 plan reviewer 对"promote"的含义产生歧义。

**Required change**: 将 Selected Next Phase 中的"可观察"改为更精确的表述，区分 snapshot observability（已有）和 comparable/golden/correctness 覆盖（待建）。

## Positive Observations

1. **Phase selection 正确**: 从 8 个候选中选择 snapshot promotion 而非 calculated tracking error 或 external adapter，符合"先锁已有能力再扩来源"的第一性原理。
2. **Required Constraints 完整**: 10 条约束覆盖了 denominator 定义、字段范围、适用性矩阵、缺失语义、质量门控、fixture、source boundary、failure taxonomy、docs 和正面验收。
3. **Non-goals 明确**: 不重开 P13、不引入计算/外部 adapter/QDII subtype/E1-E3/Dayu，与 design truth 一致。
4. **Risks / Residual Owners 表清晰**: 9 个 residual 均有 owner 和 handling。
5. **Evidence Used 覆盖全面**: 引用了所有必要的 reference truth 文档。
6. **Source boundary 强调**: Required Constraints #7 和 #8 正确保留了 FundDocumentRepository 约束和 failure taxonomy。

## Verdict Rationale

Phase selection 本身 PASS：P14-S1 是 P13 后最短最稳的下一步，不引入新来源、不引入 LLM/Dayu、不扩计算范围。但 planning artifact 的 6 个 findings 中，F-1（denominator 定义）和 F-2（FQ2 优先级）是 HIGH severity，必须在 P14-S1 plan 进入 implementation 前闭环；F-3（非指数路径）和 F-4（退出条件）是 MEDIUM severity，应在 plan 中回答。F-5 和 F-6 是 LOW severity，可在 plan 或 implementation 阶段修复。

所有 findings 均可在 planning artifact 内修复，不需要重新选择 phase。

## Required Changes Summary

| Finding | Severity | Required change |
|---|---|---|
| F-1 | HIGH | 明确"quality denominator"对应的具体代码机制（FQ2 priority / comparable sub-fields / golden answer / 新机制） |
| F-2 | HIGH | 指定 `index_profile` / `tracking_error` 的 FQ2 优先级和非指数基金 not_applicable 时的 gate 行为 |
| F-3 | MEDIUM | 明确 not_applicable 路径在 FQ2/golden/comparable 中的处理策略 |
| F-4 | MEDIUM | 添加退出条件：验证命令、预期通过数、fixture 基金覆盖、baseline 不回归 |
| F-5 | LOW | 说明 fixture 策略与 P3 矩阵和 golden answer JSON 的衔接 |
| F-6 | LOW | 区分 snapshot observability（已有）和 comparable/golden correctness（待建） |

## Recommended Next Action

P14-S1 plan 应针对 F-1 至 F-4 修订后重新提交 re-review。F-5 和 F-6 可在 plan 修订中一并修复或在 implementation 阶段处理。
