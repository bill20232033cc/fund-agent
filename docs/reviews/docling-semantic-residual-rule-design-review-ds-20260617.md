# Docling Semantic Residual Rule Design Review — AgentDS — 2026-06-17

Status: FINAL

## Reviewed Target And Scope

- **Target**: `docs/reviews/docling-semantic-residual-rule-design-20260617.md` (design worker AgentCodex)
- **Gate**: `Docling Semantic Residual Rule Design Gate`
- **Scope**: adversarial review of the minimum fund-domain semantic rules and reference-bundle additions proposed to address seven residual rows (`F015`, `F020`, `S4-F015`, `S5-F032`, `S6-F041`, `S6-F049`, `S6-F050`), within the hard constraints of candidate-only, repository-mediated, no source-truth/baseline/parser/release claims, and fail-closed for ambiguous cases.
- **Reviewer role**: AgentDS, review worker only. No code, commit, control-doc, or gate transition.

## Assumptions Tested

1. All seven residual rows receive a specific rule or explicit preservation stance.
2. Guard flags (`NOT_READY`, candidate-only, no source truth, no baseline, no parser replacement, no full correctness, no release readiness) are preserved through all proposed rules and reference-bundle additions.
3. Annual-report access remains repository-mediated; no direct PDF/cache/source helper access is introduced.
4. No row is closed by value equality alone.
5. S6-F041 benchmark and S6-F049/S6-F050 identical-value cases are handled fail-closed.
6. Proposed changes are minimal, fund-domain specific, and implementable within candidate internals.
7. Implementation slices and tests are specific enough for a handoff-ready next gate.

## Sources Consulted

- `AGENTS.md` — project-wide constraints, module boundaries, hard constraints
- `docs/reviews/docling-source-truth-residual-closure-evidence-controller-judgment-20260616.md` — controller judgment with accepted residual facts
- `reports/docling-baseline-support-source-truth-residual-closure/20260616/residual_closure_matrix.json` — full 17-row evidence matrix with per-row guard flags and reference bundle status
- `fund_agent/fund/documents/candidates/source_truth_residual_closure.py` — current `ResidualClosureRule`, `RepositoryReferenceCell`, `RepositoryReferenceBundle`, `_evaluate_semantics`, `_match_satisfies_rule`, `_has_share_class_context` implementation

---

## Findings

### DS-01 未修复-中-参考包数据模型变更规格不足

- **位置**: Reference Bundle Requirements 第 1–7 项（设计文档第 161–178 行）
- **问题类型**: 不可直接实施
- **当前写法**: 设计列出 7 项参考包需要新增保留的信息维度（表格标题/标题路径、多层表头层级、行父子层级、表族分类、章节文本 span 上下文标签、诊断信息），但未说明这些信息在 `RepositoryReferenceCell`、`RepositoryReferenceTextSpan` 或 `RepositoryReferenceBundle` 中的具体字段和类型。
- **反例/失败场景**: 实施 Agent 拿到设计后，需要自行决定：表格标题是加 `table_title: str | None` 字段还是合并到 `table_context`、行层级用 `parent_row_path: tuple[str, ...]` 还是单独的 `row_hierarchy` 嵌套结构、表族分类是枚举还是自由文本。这些数据模型决策会直接影响 Slice 2 的规则谓词实现方式。不同实施 Agent 的选择会导致不兼容的实现。
- **为什么有问题**: 当前 `RepositoryReferenceCell`（`source_truth_residual_closure.py:88-158`）包含 `row_label_path`、`column_header_path`、`table_context`，但没有 `table_title`、`heading_path`、`parent_row_path`、`child_row_path`、`table_family` 等字段。设计描述了"要保留什么"但没描述"数据模型怎么改"。实施 Agent 被迫在设计层做数据模型决策，这不是"code-generation-ready"。
- **直接证据**: 
  - 设计第 166 行："Preserve table title / caption / preceding heading path for each `RepositoryReferenceCell`"——未指定字段名。
  - 设计第 167 行："Preserve multi-row and multi-column header hierarchy"——未指定 `column_header_path` 是从 `tuple[str, ...]` 变为嵌套结构还是新增字段。
  - 设计第 168 行："Preserve row hierarchy, including parent row and child row relation"——当前 `RepositoryReferenceCell` 无此能力。
  - 设计第 170 行："Preserve table-family classification as candidate metadata"——未指定是加到 cell 级别还是 bundle 级别，是枚举还是字符串。
- **影响**: 实施 Agent 跑偏 / 后续返工
- **建议改法和验证点**: 
  1. 在参考包需求中为每个新增维度指定目标 `RepositoryReferenceCell`/`RepositoryReferenceBundle` 字段名和类型。
  2. 表族分类建议定义为 `Literal["expense_fee_table", "manager_holding_table", "portfolio_asset_composition_table", "fair_value_hierarchy_table", "financial_statement_table", "holding_detail_table", "fund_profile_table"]`，避免自由文本导致后续规则匹配不稳定。
- **修复风险**: 低（纯规格补充，无需改代码）
- **严重程度**: 中

### DS-02 未修复-中-表族分类机制缺失

- **位置**: Reference Bundle Requirements 第 5 项 + Rule 3（设计文档第 170 行、第 125–129 行）
- **问题类型**: 不可直接实施
- **当前写法**: 设计要求"Preserve table-family classification as candidate metadata"并在 Rule 3 中使用"matched reference must come from a fund asset portfolio / period-end portfolio composition table, not a fair-value hierarchy, accounting statement, note..."。但设计未说明：(a) 表族分类是自动规则（基于章节+关键词）还是需要新逻辑；(b) 分类结果如何参与规则评估——是否新增 `required_table_family_classification` 字段到 `ResidualClosureRule`；(c) 分类错误时的回退行为。
- **反例/失败场景**: S4（006597 国泰利享中短债债券型）的年报 §8 可能同时包含"基金资产组合"表和"公允价值层次"表。如果分类逻辑将公允价值层次表误分类为资产组合表，`fixed_income_investment_amount` 可能从公允价值层次表中错误闭合。
- **为什么有问题**: 当前 `required_table_family_any` 通过字符串包含匹配检查 `table_context`（`_match_satisfies_rule` 第 752–756 行），而非结构化的表族分类。设计引入了新的"表族分类"概念但未将其与现有的 `required_table_family_any` 字段桥接起来，也未说明分类是前置计算（在 Slice 1 中完成）还是规则评估时动态判断。
- **直接证据**:
  - 当前 `ResidualClosureRule` 无 `required_table_family_classification` 字段（`source_truth_residual_closure.py:61-86`）。
  - 当前 `_match_satisfies_rule` 只检查 `required_table_family_any` 对 `table_context` 的字符串包含。
  - S4-F015 的 evidence matrix 行显示 `matched_table_context: []`——原始参考包没有提供足够上下文。
- **影响**: 实施 Agent 跑偏 / 生成错误代码
- **建议改法和验证点**:
  1. 明确表族分类是 Slice 1 完成的前置步骤，分类结果以结构化字段存入参考包。
  2. 在 `ResidualClosureRule` 中新增 `allowed_table_families: tuple[str, ...]` 和 `rejected_table_families: tuple[str, ...]`（或在设计文档中说明复用现有 `required_table_family_any`）。
  3. 显式声明分类失败（无法判断表族）时按 fail-closed 处理：`semantic_assignment_residual`。
- **修复风险**: 低
- **严重程度**: 中

### DS-03 未修复-中-行父子层级谓词未关联到现有规则模型

- **位置**: Rule 3 字段特定接受条件（设计文档第 136–139 行） + Slice 2（第 189–197 行）
- **问题类型**: 契约缺失
- **当前写法**: Rule 3 要求 `equity_investment_amount` "reject child stock rows"、`stock_investment_amount` 需要 "stock child row under equity investment"。Slice 2 说"Extend `ResidualClosureRule` or a successor... for row-hierarchy parent/child predicates"。但设计未指定：(a) 父/子关系是作为 `ResidualClosureRule` 的新字段（如 `required_parent_row_label_any`、`rejected_child_row_label_any`）还是新的 `row_hierarchy_rule` 子对象；(b) "子行"的判断是基于参考包中的 `parent_row_path` 字段还是基于行标签的层级前缀匹配。
- **反例/失败场景**: 在 S6（110020 易方达沪深300ETF联接）的 §8 表中，`权益投资` 行和 `其中：股票` 行在序列上相邻但共享同一个值 `149698325.51`。如果层级判断仅基于相邻行标签（"如果上一行是权益投资且当前行以其中开头则为子行"），在其他基金年报中可能因空行、合并单元格或非标准缩进导致层级判断失败。
- **为什么有问题**: 行层级是 Rule 3 的核心谓词，但设计在最需要精确语义的地方使用了模糊表述。"parent/child row context"和"row hierarchy"是领域概念，但在代码中必须落实为具体的数据结构和判断逻辑。当前设计把设计决策推到了 Slice 2。
- **直接证据**:
  - `ResidualClosureRule` 当前字段：`required_row_label_any`、`rejected_row_label_any`——没有 parent/child 概念。
  - 设计第 197 行："row-hierarchy parent/child predicates"——仅一个短语，无具体字段或逻辑描述。
  - 设计第 168 行："Preserve row hierarchy, including parent row and child row relation"——描述了参考包侧，但规则评估侧如何消费此信息未定义。
- **影响**: 实施 Agent 跑偏 / 后续返工
- **建议改法和验证点**:
  1. 在设计文档中补充 `ResidualClosureRule` 拟新增的行层级字段草案（如 `required_parent_row_context: tuple[str, ...]` 和 `rejected_child_row_context: tuple[str, ...]`）。
  2. 明确行层级判断逻辑：是基于参考包中预先计算的 `parent_row_path` 还是规则评估时动态匹配。
  3. 建议在 S6-F049/S6-F050 的 stop condition 基础上增加：如果 `equity_investment_amount` 和 `stock_investment_amount` 的候选值相同且来自同一表，即使行层级已证明区分，也必须额外的表结构一致性检查才能闭合。
- **修复风险**: 低
- **严重程度**: 中

### DS-04 未修复-低-份额类别上下文检查范围与当前代码不一致

- **位置**: Rule 1（设计文档第 96 行）vs 当前实现 `_has_share_class_context`（`source_truth_residual_closure.py:1267-1295`）
- **问题类型**: 契约缺失
- **当前写法**: 设计第 96 行："column header path, row label path, or adjacent table header context must prove C share class"。但当前 `_has_share_class_context` 仅检查 `column_headers`（来自 `column_header_path`），不检查 `row_label_path` 或 `table_context`。
- **反例/失败场景**: 某些基金年报的费用表可能在表格标题行按份额类别分列（如列标题为"A类、C类"），但列标题路径可能不直接包含"C类"二字（例如列标题是"本期"、"本期"两列，份额类别在更上层的表头 band 中）。如果依赖"行标签路径或相邻表头上下文"来判断份额类别，而代码只实现了列标题检查，C 份额的销售服务费将错误保持 residual。
- **为什么有问题**: 设计承诺的检查范围比当前代码能实现的范围更宽。Slice 2 没有明确说要扩展 `_has_share_class_context` 的检查范围到 row labels 和 table context。实施 Agent 如果只看设计文档的第 96 行而不检查当前代码的 `_has_share_class_context` 实现，会遗漏这个扩展需求。
- **直接证据**:
  - `_has_share_class_context` 仅接收 `values: tuple[str, ...]`（列标题），不检查行标签或表格上下文。
  - 设计第 96 行明确写了"row label path, or adjacent table header context"作为份额类别证明路径。
  - Slice 2 第 193 行只写了"share-class context variants"，未提及检查范围扩展。
- **影响**: 实施 Agent 跑偏
- **建议改法和验证点**: 在 Slice 2 中显式说明 `_has_share_class_context` 或等价函数需要扩展检查范围到 row label path 和 table header context，并在 Rule 1 的测试用例中增加"份额类别仅在行标签中体现"的测试场景。
- **修复风险**: 低
- **严重程度**: 低

### DS-05 未修复-低-参考包第7项诊断信息超出闭合范围

- **位置**: Reference Bundle Requirements 第 7 项（设计文档第 172 行）
- **问题类型**: 范围漂移
- **当前写法**: "Preserve matched-reference diagnostics for residual rows, including rejected match count and first few rejected contexts, without treating diagnostics as source truth."
- **反例/失败场景**: 参考包构建时收集"rejected match count and first few rejected contexts"需要额外的规则评估路径（收集被拒绝的匹配及其拒绝原因），这在当前 `_evaluate_semantics` 中不存在（当前函数只记录 accepted matches，丢弃 rejected 的）。实施这个需求会扩大 Slice 1 的范围，且该诊断信息对闭合 residual 行本身无帮助。
- **为什么有问题**: 诊断信息是调试/观测用途，不属于"最小语义规则设计"gate 的范围。它不帮助闭合任何一个 residual 行，但需要修改参考包构建逻辑和语义评估逻辑来收集和传递这些诊断信息。这违反了设计的"最小改动"原则。
- **直接证据**:
  - 设计第 79 行声明："Therefore the minimum design should enrich context and tighten acceptance predicates"
  - 第 172 行却引入了一个非闭合目的的诊断需求。
  - 当前 `_evaluate_semantics`（第 681–715 行）不返回 rejected match 信息。
- **影响**: 后续返工
- **建议改法和验证点**: 将第 7 项从参考包需求中移除或标记为 `optional / future`。如需保留，明确标注"非本 gate 范围，不阻塞 closure"。
- **修复风险**: 低（删除或标注即可）
- **严重程度**: 低

### DS-06 未修复-低-跨基金类型表格结构差异未讨论

- **位置**: Rule 3（设计文档第 122–145 行）
- **问题类型**: open question 未收敛
- **当前写法**: Rule 3 将 S4-F015（债券基金 006597）、S5-F032（QDII 指数基金 017641）、S6-F049 和 S6-F050（ETF 联接基金 110020）的资产组合字段统一处理。但债券基金年报的 §8 表格结构（"基金资产组合"、"固定收益投资"为主）与 QDII 指数基金（"基金资产组合"、"权益投资"包含海外股票）和 ETF 联接基金显著不同。设计未讨论跨基金类型的投资组合表格结构差异是否影响规则适用性。
- **反例/失败场景**: 某债券基金的 §8 可能没有"权益投资"行（因为债券基金基本不持股票），`equity_investment_amount` 应该直接保持 residual。但 Rule 3 的接受谓词假设了所有基金都有"权益投资"行，这可能在某些基金类型的年报中产生误分类。
- **为什么有问题**: S4 是债券基金（006597 国泰利享中短债），其 §8 的资产组合结构与 S5（017641 QDII 指数基金）不同。设计未区分这两种情况，实施 Agent 可能对债券基金的 `equity_investment_amount` 应用同样"严格"的资产组合表规则，而实际上债券基金的 `equity_investment_amount` 可能天然缺失或为 0。
- **直接证据**: S4 的 residual rows 只包含 `S4-F015`（`fixed_income_investment_amount`），不包含 `equity_investment_amount`。设计正确地为 S4 只诊断了 `fixed_income_investment_amount`，但没有讨论为什么 S4 没有 `equity_investment_amount` residual 以及这对规则通用性意味着什么。
- **影响**: 实施 Agent 跑偏（低概率）/ review 不可验收（低）
- **建议改法和验证点**: 在设计文档中增加一段简短说明：债券基金的资产组合表以固收为主，QDII/股票基金的资产组合表以权益为主，规则设计已按字段而非基金类型应用，缺失字段的 residual 状态由上游 matrix 保证。
- **修复风险**: 低
- **严重程度**: 低

---

## Open Questions

1. **表族分类算法**：表族分类是基于 (a) 章节号 + 表标题关键词规则匹配，(b) 表内行标签关键词集合分类，还是 (c) 基于参考包中已有的 `table_context` 字段推断？这影响 Slice 1 的实现复杂度。建议在设计文档中补充分类策略的最低规格。

2. **参考包内存占用**：新增的 7 项上下文维度（特别是行层级和表族分类元数据）会增加 `RepositoryReferenceBundle` 的内存占用。当前 S5 的 `cell_reference_count=6879`，如果每个 cell 都增加 `parent_row_path`、`table_family` 等字段，对 no-live 批量处理的性能影响需要考虑。这属于后续实现 gate 的性能考量，不阻塞当前设计 gate。

3. **F015 的多重语义等价重复**：设计第 97 行说"if more than one same-source match satisfies all predicates, keep `semantic_equivalent_duplicate_residual`"。当前 `sales_service_fee_C_current_year` 规则已设置 `allow_semantic_equivalent_duplicate=True`。但参考包增强后可能产生更多符合条件的匹配（因为列标题上下文更丰富）。设计应说明当所有重复行都满足语义条件时，是全部保留 residual 还是可以接受第一个。这一点设计基本正确（保留 residual），但可以更明确。

---

## Residual Risks

| Risk | Severity | Owner | Suggested Tracking |
|------|----------|-------|-------------------|
| 参考包数据模型变更未经设计确认，实施 Agent 自行设计可能导致与规则评估不兼容 | 中 | 下一 gate（Slice 1 plan） | 在 Slice 1 plan gate 中要求先出数据模型设计再实施 |
| 表族分类缺少算法规格，不同分类策略导致同一行在不同运行时产生不同闭合结果 | 中 | 下一 gate（Slice 1 plan） | 在 Slice 1 plan 中要求表族分类策略的具体规格 |
| S6-F049/S6-F050 即使在有行层级证明后仍可能因相同数值导致误闭合 | 低 | Slice 3 验证 gate | 在 Slice 3 的测试用例中显式覆盖"同值不同行语义"场景 |
| 现有仓库解析表可能不保留合并单元格的表头层级 | 低 | Slice 1 实施 | 设计已识别此风险（第 262 行），建议在 Slice 1 中先评估现有解析表的结构保真度 |

---

## Validation Checks

### Review Focus Compliance

| Check | Result |
|-------|--------|
| 设计覆盖全部 7 个 residual 行 | **PASS** — F015(Rule1), F020(Rule2), S4-F015(Rule3), S5-F032(Rule3), S6-F041(Rule4), S6-F049(Rule3), S6-F050(Rule3) |
| 保持 NOT_READY，不声称 source truth / baseline / parser replacement / full correctness / release readiness | **PASS** — Non-goals 第 23–28 行、Stop Conditions 第 258 行、Completion Report 第 293 行全部确认 |
| 年报访问保持 repository-mediated，禁止直接 PDF/cache/source helper | **PASS** — 第 33–34 行、第 162 行、Stop Conditions 第 256 行 |
| 禁止仅靠数值或文本相等闭合 | **PASS** — 第 30 行、Stop Conditions 第 250–255 行 |
| 规则/参考包变更最小、领域特定、可在 candidate internals 实现 | **PASS with findings** — 规则设计合理聚焦中国基金年报语义，但参考包数据模型规格不足（DS-01） |
| S6-F041 benchmark 和 S6-F049/S6-F050 同值案例 fail-closed | **PASS** — Rule 4 明确 S6-F041 保持 residual，Rule 3 明确 S6-F049/S6-F050 在行层级证明前保持 residual |
| 后续实施切片和测试足够具体 | **PASS with findings** — 3 个 slice 的方向和边界正确，测试场景覆盖 4 类规则，但 Slice 1/2 的数据模型和表族分类规格不足（DS-01/DS-02/DS-03） |

### Architecture Boundary Check

- **Repository access boundary**: 设计反复确认 `FundDocumentRepository` 为唯一年报访问路径，参考包构建保持 candidate-only、`force_refresh=False`、网络 socket 阻断。**PASS**。
- **Candidate internals boundary**: Slice 1/2 限制在 Fund documents candidate internals，不触及生产 parser/extractor/Service/UI/Host。**PASS**。
- **No source-helper/cache/PDF direct access**: Stop conditions 第 256 行明确阻断。**PASS**。

### Guard Flag Consistency Check

设计文档中出现的所有 guard flag 与 evidence matrix 和 controller judgment 中的 flag 一致：
- `candidate_only=true` ✓
- `not_source_truth=true` ✓
- `not_baseline_promotion=true` ✓
- `not_parser_replacement=true` ✓
- `not_full_field_correctness=true` ✓
- `not_release_readiness=true` ✓
- `force_refresh=False` ✓
- `network_socket_guard=blocked` ✓
- `repository_access_only_via_fund_document_repository=true` ✓

---

## Verdict

**PASS_WITH_FINDINGS**

设计正确覆盖全部 7 个 residual 行，保持了所有硬约束（NOT_READY、candidate-only、repository-mediated、fail-closed），规则方向合理且聚焦中国基金年报领域语义。

不阻塞本 gate，但以下发现应在下一 gate（Slice 1 plan 或 implementation）开始前收敛：
- DS-01（参考包数据模型规格）、DS-02（表族分类机制）、DS-03（行层级谓词规格）需要更精确的字段级设计才能达到 code-generation-ready。
- DS-04（份额类别检查范围）、DS-05（诊断信息超出范围）、DS-06（跨基金类型差异）属于低严重度，可在实施时处理。
