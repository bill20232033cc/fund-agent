# Gate C Design Review — MVP chapter generation score loop design

日期：2026-05-31
Reviewer：AgentGLM（independent design reviewer）
Reviewed target：`docs/reviews/mvp-chapter-generation-score-loop-design-20260531.md`
Context：
- Gate A accepted judgment：`docs/reviews/mvp-llm-writer-auditor-contract-hardening-controller-judgment-20260531.md`
- Gate B blocked judgment：`docs/reviews/mvp-real-provider-smoke-acceptance-controller-judgment-20260531.md`

## Review scope

对 Gate C 设计 artifact 做独立 adversarial review，验证：
1. 三类 score 的关注点分离是否清晰
2. provider_runtime/timeout 是否正确路由到 `not_scored` / `blocked_provider_runtime`
3. schema、failure taxonomy、per-chapter report、task generation、thresholds、rerun command、artifact lifecycle、manual override 是否完整
4. 是否避免侵入现有 golden/fixture/score/quality gate/readiness 语义和 Gate 5
5. 安全边界是否完整保留
6. 是否 code-generation-ready，无过度设计或隐藏耦合

## Assumptions tested

| # | Assumption | 验证方式 |
|---|---|---|
| A1 | `StructuredFundDataBundle`、`ChapterFactProvider`、`ChapterDraft`、`ChapterWriteResult`、`ChapterAuditResult`、`ChapterRunResult`、`ChapterOrchestrationResult` 均为当前代码中的真实 dataclass | 代码事实验证 |
| A2 | `ChapterRunStopReason` 包含 `llm_timeout` 等 5 个 `llm_*` runtime variant | 代码事实验证 |
| A3 | 当前 `score.json`、quality gate、golden answer、fixture、promotion pipeline 独立于本章 score-loop | 代码结构验证 |
| A4 | 当前 CLI 默认路径 `fund-analysis analyze/checklist` 不受 score-loop 影响 | CLI entry point 验证 |
| A5 | 章节评分范围 1-6，章节 0/7 由 final assembly 处理 | orchestrator 代码验证 |
| A6 | Gate B blocker 是 `provider_runtime / timeout`、`stop_reason=llm_timeout` | Gate B judgment 验证 |

## Code facts verified

| 代码实体 | 存在 | 文件 | 行 |
|---|---|---|---|
| `ChapterDraft` | YES | `fund_agent/fund/chapter_writer.py` | 242 |
| `ChapterWriteResult` | YES | `fund_agent/fund/chapter_writer.py` | 294 |
| `ChapterAuditResult` | YES | `fund_agent/fund/chapter_auditor.py` | 283 |
| `ChapterRunResult` | YES | `fund_agent/services/chapter_orchestrator.py` | 251 |
| `ChapterOrchestrationResult` | YES | `fund_agent/services/chapter_orchestrator.py` | 276 |
| `StructuredFundDataBundle` | YES | `fund_agent/fund/data_extractor.py` | 140 |
| `ChapterFactProvider` | YES | `fund_agent/fund/chapter_facts.py` | 432 |
| `llm_timeout` in `ChapterRunStopReason` | YES | `fund_agent/services/chapter_orchestrator.py` | 42-66 |

现有评分/质量门控模块（score-loop 不触碰）：

- `fund_agent/fund/extraction_score.py`
- `fund_agent/fund/quality_gate.py`
- `fund_agent/fund/quality_gate_integration.py`
- `fund_agent/fund/golden_answer.py`
- `fund_agent/services/extraction_score_service.py`
- `fund_agent/services/quality_gate_service.py`
- `fund_agent/services/golden_answer_service.py`

CLI 当前命令集（score-loop 不改变）：`analyze`、`checklist`、`thermometer`、`extraction-snapshot`、`extraction-score`、`golden-prefill`、`golden-build`、`quality-gate`、`golden-readiness-preflight`。

## Review question findings

### Q1: 三类 score 关注点是否清晰分离？

**结论：清晰分离，无混用。**

设计 §1.2 用表格精确定义了三个 score 的评估对象、回答的问题和不负责的范围：

| Score | 评估对象 | 代码对应 |
|---|---|---|
| `extraction_score` | `StructuredFundDataBundle` | `data_extractor.py:140` |
| `chapter_fact_score` | `ChapterFactProvider` → `ChapterFactProjection` | `chapter_facts.py:432` |
| `chapter_generation_score` | `ChapterWriteResult`、`ChapterDraft`、`ChapterAuditResult`、`ChapterRunResult` | `chapter_writer.py`、`chapter_auditor.py`、`chapter_orchestrator.py` |

三个 score 分别对应 extract → project → generate 三阶段管道，每个 score 的 failure taxonomy（§5.2-5.4）与对应代码实体对齐。routing rules（§7.2）明确禁止跨层修复（如 "不得修改 writer/auditor 来掩盖字段错误"）。

### Q2: provider_runtime/timeout 是否正确路由？

**结论：正确路由，不伪装为生成质量通过或失败。**

验证：
- §1.3 明确规定 `stop_reason=llm_timeout` 时 `chapter_generation_score.status=not_scored`。
- §3.1 root 约束：`runtime_status.category=provider_runtime` 且 `reason=timeout` 时，未获得 draft/audit 的章节必须 `not_scored`。
- §5.1 failure taxonomy 将 `runtime.provider_timeout` 映射到 `provider_runtime` class，score 处理为 `generation not_scored`。
- §4 per-chapter report 示例展示了 chapter 2 `llm_timeout` 的完整形状，`chapter_generation_score.status=not_scored`，`not_scored_reason=provider_runtime_timeout`。
- §6.1 整体 run blocked 条件明确包含 provider runtime timeout。
- 代码事实：`ChapterRunStopReason` 包含 `llm_timeout`（`chapter_orchestrator.py:42-66`），与设计中的 `runtime.provider_timeout` 对应。

与 Gate B judgment 的一致性：Gate B 记录 `stop_reason=llm_timeout`，设计将该场景路由为 `blocked_provider_runtime`，不改变现有 quality gate 语义。一致。

### Q3: 设计是否包含所有必要 artifact？

**结论：完整覆盖。**

| 要求 | 设计位置 | 评估 |
|---|---|---|
| Score schema | §3.1 Root artifact + §3.2 Score object | JSON 形状完整，字段约束明确 |
| Failure taxonomy | §5.1-5.4 四类 | runtime 7 个 + extraction 7 个 + fact 7 个 + generation 12 个，共 33 个 failure code |
| Per-chapter report | §4 | JSON 形状含 run_status、三个 score、top_failures、task_candidates |
| Pro-Codex task generation | §7.1-7.3 | Task schema、routing rules、priority rules 完整 |
| Pass/fail thresholds | §6.1 | `mvp_strict_v1` profile 三级阈值 + blocking rule |
| Rerun command | §8 | CLI 命令形状、边界、exit code、兼容方式 |
| Artifact lifecycle | §9.1-9.2 | Run artifacts 目录结构、保留规则、review artifacts 命名约定 |
| Human review/manual override | §10.1-10.2 | Override schema、4 种 allowed decisions、禁止事项 |

### Q4: 是否避免侵入现有语义和 Gate 5？

**结论：明确不侵入。**

- §2 Non-goals 列出 7 条不改变项：源码、score.json、quality gate、golden、fixture、readiness pipeline、Gate 5/dayu/Host/Agent。
- §8 命令边界明确 `score-chapters` 为 opt-in，不改变 `analyze/checklist` 默认行为。
- §11 Readiness boundary 四条边界声明。
- 代码事实验证：现有 extraction_score、quality_gate、golden_answer 模块均在独立文件中，score-loop 新增代码不会触碰这些模块的文件。

### Q5: 安全边界是否完整保留？

**结论：完整保留。**

逐项验证：

| 安全边界 | 设计位置 | 评估 |
|---|---|---|
| Evidence anchor | `generation.evidence_line_missing`（blocking）、`extraction.anchor_missing`（blocking）| 规则码 E1/E3 映射正确 |
| ITEM_RULE | `generation.item_rule_deleted_content_present`（blocking）、`fact.item_rule_projection_missing`（blocking）| C2 规则映射正确 |
| Candidate facet | `fact.asserted_candidate_facet`（blocking）、`generation.asserted_candidate_facet`（blocking）| L2 规则映射正确，fail-closed |
| Trading advice | `generation.trading_advice`（blocking）| 禁止输出买入/卖出建议，R2 映射正确 |
| E2 deferred | §5.4 后段明确"E2 源文核验仍是 Evidence Confirm gate 边界...不得把 E2 deferred 当作通过源文核验" | 正确隔离 |
| No weak evidence pass | 所有 severity=blocking 的 check 都使 score status=fail，即使加权均分高于阈值（§3.2 约束）| 无弱证据通过路径 |

§7.2 routing rules 中的 non_goals 约束（"do not relax evidence or ITEM_RULE boundaries"）与实现 slices 的 `non_goals` 一致，形成双重保护。

### Q6: 是否 code-generation-ready？

**结论：code-generation-ready，无过度设计或隐藏耦合。**

**Implementation slices（§12）评估：**

| Slice | 边界清晰度 | 依赖 | 耦合风险 |
|---|---|---|---|
| `score_schema_models` | 纯新增 dataclass/JSON schema | 无现有代码依赖 | 低 |
| `diagnostic_to_score_mapper` | 读取现有 dataclass | `StructuredFundDataBundle`、`ChapterFactProjection`、`ChapterOrchestrationResult` | 低（只读映射） |
| `task_candidate_generator` | 基于 score object 生成任务 | score_schema_models | 低 |
| `score_cli_opt_in` | 新增 CLI 命令 | mapper + task generator | 低 |
| `artifact_hygiene_tests` | 测试 slice | 所有新增模块 | 低 |

每个 slice 有明确的 `allowed_files_hint`，防止 implementation agent 扩大修改范围。Slices 可顺序实施，无循环依赖。

**过度设计检查：**
- 三类 score 对应三阶段管道，是自然的领域切分，不是人为抽象。
- Failure taxonomy 的 33 个 failure code 每个都有明确含义和修复方向，不是枚举膨胀。
- Manual override 设计为四种 decision + `allowed_effect` 白名单，不是通用 override 框架。
- Task generation 只做 handoff 不执行，是合理的关注点分离。

## Findings

### F1-未修复-低-ChapterFactInput 命名不一致

- **位置**: §1.2 `chapter_fact_score` 行
- **问题类型**: 契约缺失
- **当前写法**: "评估对象"列为 `ChapterFactProvider 输出的 chapter_fact_projection.v1 / ChapterFactInput`
- **反例/失败场景**: Implementation agent 实现 chapter_fact_score 评分函数时，需要知道输入类型是 `ChapterFactProjection`（代码事实）还是 `ChapterFactInput`（设计中出现但代码中不存在的名称），可能导致不必要的类型查找或创建不存在的导入
- **为什么有问题**: 当前代码中 `ChapterFactProvider.project()` 返回 `ChapterFactProjection`（`chapter_facts.py:432`），不存在名为 `ChapterFactInput` 的 dataclass。设计同时使用两个名称，语义指向不明确
- **直接证据**: `fund_agent/fund/chapter_facts.py:432` 的 facade 方法签名为 `project(self, bundle, *, chapter_ids) -> ChapterFactProjection`
- **影响**: 实施 Agent 可能浪费时间查找不存在的类型，或在 mapper 中创建不必要的适配层
- **建议改法和验证点**: 在 implementation 前统一为 `ChapterFactProjection`，或注明 `ChapterFactInput` 为未来 score-loop mapper 的内部输入类型（非代码 dataclass）
- **修复风险**: 低
- **严重程度**: 低

### F2-未修复-低-extraction_score 与现有 extraction_score_service.py 的关系未显式声明

- **位置**: §1.2 `extraction_score`、§2 Non-goals
- **问题类型**: 架构边界
- **当前写法**: 设计定义了新的 `extraction_score`，评估 `StructuredFundDataBundle` 抽取质量；Non-goals 声明不修改现有 score/quality gate
- **反例/失败场景**: 当前代码已有 `fund_agent/services/extraction_score_service.py` 和 `fund_agent/fund/extraction_score.py`，它们提供基于 golden answer 的 extraction score。新 score-loop 的 `extraction_score` 名称完全相同但语义不同（一个对 golden，一个对结构完整性）。Implementation agent 或后续 reviewer 可能混淆两者
- **为什么有问题**: 名称冲突可能导致维护者误认为 score-loop 的 extraction_score 是现有模块的替代或扩展，而非独立的新评估维度
- **直接证据**: `fund_agent/services/extraction_score_service.py` 存在；设计 §3.1 使用 `extraction_score_min` 字段名
- **影响**: 后续开发中可能错误导入或混淆两个 extraction score 实现
- **建议改法和验证点**: 在 implementation slice 中明确新 score-loop 的 extraction score class/module 命名（如 `loop_extraction_score` 或放入独立 namespace），或在设计文档中显式声明与现有 `extraction_score_service.py` 的关系为"并列独立、不替代、不依赖"
- **修复风险**: 低
- **严重程度**: 低

### F3-未修复-低-权重系统与 threshold 的交互语义可更精确

- **位置**: §6.1 threshold profile、§6.2 weights
- **当前写法**: §6.2 定义了各 check 类别的权重百分比，但 §6.2 最后一段声明"Weights 只用于 reviewable failures 的排序；blocking failure 永远覆盖加权分"。§3.2 score object 有 `value`（0.0-1.0）字段
- **反例/失败场景**: 当所有 blocking checks 都通过时，`value` 如何计算？是加权平均还是简单通过率？设计说 weights 用于"reviewable failures 的排序"，但如果 value 是加权平均，那 reviewable failures 的权重差异会影响 pass/fail 判定，不只是排序。如果 value 不是加权平均，那 weights 百分比的计算用途是什么？
- **为什么有问题**: Implementation agent 需要知道 `value` 的精确计算公式，当前描述有歧义
- **直接证据**: §3.2 score object 的 `value` 字段约束为 0.0-1.0；§6.2 weights 定义了百分比但没有给出计算公式
- **影响**: 可能导致 implementation 中 value 计算方式不一致，或 weights 被误用于 pass/fail 判定
- **建议改法和验证点**: 在 `score_schema_models` slice 中明确：当所有 blocking checks pass 时 `value=1.0`，存在 reviewable failures 时按加权扣分公式计算 `value`，并给出一个示例计算。或者简化为：blocking pass 时 value=1.0，存在 reviewable 时 value=1.0 - weighted_penalty
- **修复风险**: 低
- **严重程度**: 低

## Open questions

无 material open questions。三个 low findings 均可在 implementation slice 1（`score_schema_models`）阶段解决，不需要修改设计方向。

## Residual risks

| Risk | 来源 | Disposition | Tracking |
|---|---|---|---|
| extraction_score 正确性验证需要同源真值 | 设计 §13 已识别 | 初版只做结构完整性+锚点，正确性需人工 review | future extraction scoring gate |
| LLM audit 结果本身可能不稳定 | 设计 §13 已识别 | generation score 以程序审计 blocking rules 为硬约束 | future writer/auditor hardening gate |
| score-loop artifact 可能被误用为 readiness pass | 设计 §13 已识别 | 设计明确禁止接入 readiness/golden；controller judgment 需再次确认 | controller / future readiness gate |
| Provider runtime timeout 持续阻断完整 run | Gate B blocker | 设计正确分类为 `not_scored`/`blocked_provider_runtime`，不伪装为 generation failure | future provider runtime gate |
| Manual override 滥用风险 | 设计 §13 已识别 | override 只影响 task generation，不改变 raw score | controller / reviewer |

## Special lenses applied

### Architecture boundary review

三层 score 分别对应 Agent 层 `fund_agent/fund` 的三个阶段（extract → project → generate），不跨层。Score-loop 的 CLI 命令在 UI 层新增，但不改变现有 UI 默认路径。Score-loop mapper 读取现有 dataclass（只读映射），不修改 Service 层编排逻辑。边界合规。

### Best-practice review

- Failure taxonomy 先路由 runtime failure 再评分（fail-fast），符合可观测性最佳实践。
- `not_scored` 状态与 `fail` 状态分离，符合精确分类原则。
- Manual override 有 expiry 和 `allowed_effect` 白名单，符合最小权限原则。

### Optimal-solution review

设计方案是当前条件下最实际的路径：在 provider runtime 仍 blocked 的情况下，先建立评分框架和分类系统，后续 unblock 后可直接复用。替代方案（等 provider unblock 后再设计评分）会延迟迭代观察能力。

### Overengineering review

设计复杂度与目标匹配。33 个 failure code 对应 3 个评估阶段 × ~11 类失败模式，每个都有明确含义和修复方向。没有无当前需求支撑的抽象层、builder 模式或通用框架。Manual override 仅四种 decision，不是通用权限系统。

### Overcoupling review

三个 score 的评估逻辑独立：extraction 不依赖 fact，fact 不依赖 generation。Runtime status 是独立于所有 score 的前置状态。Implementation slices 无循环依赖。Task routing rules 防止跨层修复。

## Final conclusion

**PASS**

Gate C 设计 artifact 通过独立 design review。设计清晰区分三类 score，正确路由 provider runtime timeout，完整覆盖所有必要 artifact（schema、failure taxonomy、per-chapter report、task generation、thresholds、rerun command、artifact lifecycle、manual override），明确不侵入现有 golden/fixture/score/quality gate/readiness 语义，完整保留安全边界，且 code-generation-ready。

三个 low findings（`ChapterFactInput` 命名、extraction_score 名称区分、权重计算语义）均可在 implementation 第一个 slice 解决，不影响设计方向正确性。

## Reviewer self-check

- [x] Reviewed target、scope、source of truth 和 assumptions tested 已写清
- [x] Findings 为 evidence-based、adversarial、可执行，无 style/nit/speculation
- [x] Open questions、residual risks 与 findings 分开
- [x] Conclusion 为 `pass`
- [x] 未修改源码、设计 artifact、golden、fixture、score、quality gate、README 或 runtime
- [x] 未记录 API key、Authorization header、完整 provider response 或完整 writer draft
- [x] 未进入 Gate 5 dayu/Host/Agent
