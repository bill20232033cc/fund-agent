# MVP chapter generation score loop design review — MiMo

日期：2026-05-31

角色：AgentMiMo 独立设计 reviewer，不 controller、不 implementation worker。

Review target：`docs/reviews/mvp-chapter-generation-score-loop-design-20260531.md`

前置输入：
- Gate A accepted judgment：`docs/reviews/mvp-llm-writer-auditor-contract-hardening-controller-judgment-20260531.md`
- Gate B blocked judgment：`docs/reviews/mvp-real-provider-smoke-acceptance-controller-judgment-20260531.md`
- 当前代码：`fund_agent/fund/chapter_writer.py`、`fund_agent/fund/chapter_auditor.py`、`fund_agent/services/chapter_orchestrator.py`、`fund_agent/services/llm_provider.py`、`fund_agent/fund/extraction_score.py`、`fund_agent/services/extraction_score_service.py`
- 当前控制面：`AGENTS.md`、`docs/implementation-control.md`、`docs/current-startup-packet.md`

## 1. Review Questions — Findings

### Q1: 三类 score 是否清晰区分、不混用？

结论：**PASS**

- Section 1.2 用精确表格区分了三个 score 的评估对象、回答问题和不负责边界。
- `extraction_score` 评估 `StructuredFundDataBundle` 结构化字段抽取质量；不评价 ChapterFactProvider 投影或 writer/auditor 输出。
- `chapter_fact_score` 评估 `ChapterFactProvider` 输出的 `chapter_fact_projection.v1` / `ChapterFactInput`；不评价底层字段正确性或 writer/auditor 输出。
- `chapter_generation_score` 评估 writer/auditor 产物（`ChapterWriteResult`、`ChapterDraft`、`ChapterAuditResult`、`ChapterRunResult`）；不评价 provider runtime 稳定性。
- 三者共享同一基础 score object shape，但通过 `name` 字段和 per-chapter report 中的独立位置区分，不会混用。

**残留发现**：代码库已有 `fund_agent/fund/extraction_score.py`（含 `ExtractionScoreResult`、`ScoreThresholds`、`FieldScoreRow` 等）和 `fund_agent/services/extraction_score_service.py`。设计文档未显式说明新的 `extraction_score` 概念与现有 `ExtractionScoreResult` 的关系——是复用、替换还是并行。这不影响三类 score 的概念区分，但后续实现 gate 需要明确集成策略。记录为 residual。

### Q2: provider_runtime/timeout 是否正确路由到 not_scored/blocked_provider_runtime？

结论：**PASS**

- Section 1.3 明确处理 Gate B blocker：`chapter_id=2`、`stop_reason=llm_timeout` 时，`chapter_generation_score.status` 必须为 `not_scored`。
- timeout 不计为 `pass=false` 也不计为 `pass=true`，overall result 为 `blocked_provider_runtime`。
- Section 5.1 failure taxonomy 将 `runtime.provider_timeout`、`runtime.provider_rate_limited`、`runtime.provider_network_error`、`runtime.provider_malformed_response`、`runtime.provider_exception` 全部归入 `provider_runtime` class，generation score 均为 `not_scored`。
- 章节报告示例（Section 4）正确展示了 chapter 2 timeout 时 `chapter_generation_score.status=not_scored`、`not_scored_reason=provider_runtime_timeout`。
- `chapter_orchestrator.py` 已有 `_provider_runtime_stop_reason()` 函数（line 821）处理 provider runtime exception 分类。设计正确消费此现有状态，不重新实现。

**残留发现**：Section 5.1 列出 5 种 provider_runtime failure code，但 Section 4 示例中 `not_scored_reason` 只写了 `provider_runtime_timeout`。若后续 provider runtime 分类扩展（如 `provider_rate_limited`），`not_scored_reason` 的取值空间是否需要显式枚举？当前设计用 free-form string，实现时需注意一致性。

### Q3: 是否包含所有必要组件？

结论：**PASS**（9/9 组件齐全）

| 组件 | 对应 Section | 评估 |
|---|---|---|
| Score schema | Section 3 | 完整 JSON schema，含 root artifact 和 score object 两层 |
| Failure taxonomy | Section 5 | 4 类 failure（runtime、extraction、fact、generation），每类有 failure code、severity、含义、修复方向 |
| Per-chapter report | Section 4 | 完整 JSON shape，含 run_status、三类 score、top_failures、task_candidates |
| Pro-Codex task generation rules | Section 7 | 含 task schema、routing rules、priority rules |
| Pass/fail thresholds | Section 6 | `mvp_strict_v1` profile，含 per-score 阈值和整体 run pass/blocked 条件 |
| Rerun command | Section 8 | opt-in `score-chapters` 命令设计，含 exit code 和边界说明 |
| Artifact lifecycle | Section 9 | run artifacts 和 review artifacts 两层，含保留规则和 redaction 要求 |
| Human review entry points | Section 10 | override schema、allowed decisions、对 raw score 的限制 |
| Validation matrix | Section 11 | 最小验证矩阵和 readiness boundary |

### Q4: 是否避免改变现有 golden/fixtures/score/quality gate/readiness 语义？是否避免进入 Gate 5？

结论：**PASS**

- Section 2 Non-goals 明确列出不修改 `score.json`、quality gate、golden answer、fixture、snapshot、manifest、promotion state。
- 不接入 readiness / golden / release pipeline。
- 不进入 Gate 5，不引入 `dayu.host`、`dayu.engine`、Host、Agent runtime 或 ToolTrace。
- 不改变 deterministic `fund-analysis analyze` / `fund-analysis checklist` 默认行为。
- Section 14 Self-check 确认未修改源码、测试、golden、fixtures、score、quality gate、README、control docs 或 runtime。
- 代码验证：`chapter_writer.py`、`chapter_auditor.py`、`llm_provider.py` 均无 score 相关代码；`chapter_orchestrator.py` 无 score 相关代码（只有 provider_runtime stop_reason 处理）。设计不会侵入现有实现。

**残留发现**：代码库已有 `reports/scoring-runs/` 和 `reports/extraction-snapshots/` 目录结构。设计建议新目录为 `reports/chapter-score-runs/`。命名空间不冲突，但实现时需注意与现有 scoring artifact 的物理隔离。

### Q5: 是否保留安全边界？

结论：**PASS**

逐项核对 AGENTS.md 安全边界：

| 边界 | 设计覆盖 | Section |
|---|---|---|
| 证据必须可溯源 | `generation.unknown_anchor`、`generation.evidence_line_missing` 均为 blocking failure | 5.4 |
| ITEM_RULE 约束 | `generation.must_not_cover_violation`、`generation.item_rule_deleted_content_present` 均为 blocking | 5.4；Section 7.2 routing 明确"不得降低审计规则、删 ITEM_RULE" |
| Candidate facet fail-closed | `fact.asserted_candidate_facet` 和 `generation.asserted_candidate_facet` 均为 blocking | 5.3, 5.4 |
| 禁止交易建议 | `generation.trading_advice` 为 blocking，Section 7.3 将交易建议边界违规列为 P0 | 5.4, 7.3 |
| E2 deferred 不算通过 | Section 5.4 明确"E2 源文核验仍是 Evidence Confirm gate 边界。score-loop 可以记录 E2_deferred=true，但不得把 E2 deferred 当作通过源文核验" | 5.4 |
| 弱证据不得通过 | blocking failure 覆盖加权分（Section 6.1）；任一 blocking fail 即整体 fail | 6.1 |
| Secret boundary | Section 2 不记录 API key、Authorization header、完整 provider response、完整 writer draft；Section 9.1 redacted artifacts 必须截断长文本并删除 secrets | 2, 9.1 |

代码验证：`ChapterAuditRuleCode` 定义了全部 11 个规则码（P1/P2/E1/E2/E3/C1/C2/L1/L2/R1/R2）。设计 failure taxonomy 中 `generation.*` failure code 与实际 auditor rule 码对齐：

| Design failure code | Auditor rule | Auditor 实现状态 |
|---|---|---|
| `generation.missing_required_structure` | P1 | ✅ 有逻辑 |
| `generation.missing_required_output_marker` | C1 | ✅ 有逻辑 |
| `generation.unknown_anchor` | E1 | ✅ 有逻辑 |
| `generation.evidence_line_missing` | E3 | ✅ 有逻辑 |
| `generation.must_not_cover_violation` | C2 | ✅ 有逻辑 |
| `generation.item_rule_deleted_content_present` | C2 | ✅ 有逻辑 |
| `generation.asserted_candidate_facet` | L2 | ⚠️ L2 类型已定义但无审计逻辑 |
| `generation.numerical_closure_missing` | L1 | ✅ 有逻辑 |
| `generation.missing_semantics_violation` | R1/R2 | ✅ 有逻辑 |
| `generation.trading_advice` | R2 | ✅ 有逻辑 |

**残留发现**：`generation.asserted_candidate_facet` 映射到 L2，但当前 `chapter_auditor.py` 中 L2 只在 `ChapterAuditRuleCode` 类型字面量中定义，无实际审计逻辑。candidate facet 违规当前由 writer 的 `_sanitize_text` 和 disclaimer 机制处理。设计将 L2 作为 blocking failure 列入 generation score，但实现时 L2 审计逻辑可能需要先在 auditor 中补齐。记录为 residual。

### Q6: 是否 code-generation-ready、无过度设计或隐藏耦合？

结论：**PASS**

- JSON schema 完整且具体：root artifact、score object、per-chapter report、task schema、override schema 均有示例 JSON。
- Failure code 枚举明确，每个 code 有 severity、含义、修复方向。
- Threshold profile 有具体数值。
- Task routing rules 将 failure code 映射到 allowed_files_hint，为实现者提供明确边界。
- Implementation slices（Section 12）拆成 5 个独立 slice，每个有明确输入输出和 allowed files。
- 不引入不必要的抽象：score object 共享同一基础 shape 是合理复用，不是过度抽象。
- 不引入隐藏耦合：score-loop 是 opt-in 诊断产物，不接入现有 pipeline。

**残留发现**：

1. Section 6.2 建议 weights 有双重语义矛盾：一方面说"Weights 只用于 reviewable failures 的排序"（Section 6.1），另一方面给出详细百分比 weights 用于加权均分计算。实现时需明确 weights 的实际用途——是排序优先级还是加权均分。若仅用于排序，则百分比隐含的"加权均分高于阈值"逻辑（Section 3.2 blocking failure 覆盖加权分）需要重新表述。

2. Section 12 implementation slices 建议 `score_schema_models` 作为第一个 slice，只处理内存对象和 JSON 序列化。但现有 `extraction_score.py` 已有 score dataclass 基础设施。实现时需决定是复用现有模型还是新建独立模型族。

3. `score-chapters` CLI 命令的 exit code 3 语义（`blocked_provider_runtime`）需要与现有 CLI exit code 体系对齐。当前 `fund-analysis analyze --use-llm` 失败统一 exit code 1，新增 exit code 3 是语义改进但需确认无冲突。

## 2. Overall Judgment

结论：**PASS**

Gate C design target 已达成。设计清晰定义了 chapter generation score loop 的完整产品规范，满足全部 6 个 review questions。

设计正确处理了 Gate B blocker（provider_runtime / timeout），将其路由为 `not_scored` / `blocked_provider_runtime`，不伪装为 generation quality pass/fail。设计保留了所有 AGENTS.md 安全边界，不改变现有 golden/fixtures/score/quality gate/readiness 语义，不进入 Gate 5 dayu/Host/Agent。

设计是 code-generation-ready 的：schema、failure taxonomy、thresholds、task generation rules、rerun command、artifact lifecycle、manual override、implementation slices 均已定义到可直接编码的粒度。

## 3. Residual Risks

| # | Risk | Severity | Disposition | Owner |
|---|---|---|---|---|
| R1 | 设计 `extraction_score` 概念与代码库已有 `ExtractionScoreResult` / `extraction_score_service.py` 的关系未说明 | info | 实现 gate 需明确集成策略：复用、替换或并行 | future implementation gate |
| R2 | `generation.asserted_candidate_facet` 映射 L2 但 auditor 无 L2 审计逻辑 | info | 实现时需先在 auditor 补齐 L2 逻辑或调整 failure code 映射 | future writer/auditor hardening gate |
| R3 | Section 6.2 weights 双重语义（排序 vs 加权均分）需实现时明确 | info | 实现时选定一种语义并统一表述 | future implementation gate |
| R4 | `not_scored_reason` 为 free-form string，5 种 provider_runtime failure code 的 reason 枚举未显式定义 | info | 实现时建议定义枚举或映射表 | future implementation gate |
| R5 | score-loop artifacts 可能被误用为 readiness pass | info | 设计已通过 Non-goals、readiness boundary 和 manual override 约束；controller judgment 必须再次确认 | controller |
| R6 | `score-chapters` exit code 3 与现有 CLI exit code 体系需对齐 | info | 实现时确认无冲突 | future implementation gate |
| R7 | Section 12 slice 1 `score_schema_models` 与现有 `extraction_score.py` dataclass 基础设施的关系需明确 | info | 实现时决定复用或新建 | future implementation gate |
| R8 | chapters 0/7 final assembly 失败不在 score-loop 评估范围内 | info | 设计正确聚焦 chapters 1-6；final assembly 失败由 overall pass 条件中的"deterministic fallback"检查覆盖 | design scope |

## 4. Self-check

- Review role：AgentMiMo 独立设计 reviewer，不 controller、不 implementation worker。
- Review target：`docs/reviews/mvp-chapter-generation-score-loop-design-20260531.md`。
- Source of truth：已读取 `AGENTS.md`、`docs/implementation-control.md`、`docs/current-startup-packet.md`、Gate A judgment、Gate B blocked judgment。
- 代码验证：已确认 `chapter_writer.py`、`chapter_auditor.py`、`chapter_orchestrator.py`、`llm_provider.py` 无 score 相关代码；已确认 `ChapterAuditRuleCode` 包含全部 11 个规则码；已确认 `extraction_score.py` 和 `extraction_score_service.py` 存在。
- Scope boundary：本 review 不修改源码、测试、golden、fixtures、score、quality gate、README、control docs 或 runtime。不修改 review target 设计 artifact。
- Secret boundary：本 review 未记录 API key、Authorization header、完整 provider response 或完整 writer draft。
- 不包含 secrets / provider responses。
