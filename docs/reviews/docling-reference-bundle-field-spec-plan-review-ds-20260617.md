# Docling Reference Bundle Field-spec Plan Review — AgentDS — 2026-06-17

Status: FINAL

## Reviewed Target And Scope

- **Target**: `docs/reviews/docling-reference-bundle-field-spec-plan-20260617.md` (planning worker)
- **Gate**: `Docling Reference Bundle Field-spec Planning Gate`
- **Scope**: adversarial review of the code-generation-ready field-level plan for candidate-only repository reference-bundle enrichment and semantic-rule predicate expansion, following the accepted `Docling Semantic Residual Rule Design Gate` with binding next-gate amendments.
- **Reviewer role**: AgentDS, review worker only. No code, commit, control-doc, or gate transition.

## Sources Consulted

- `AGENTS.md` — project-wide constraints, module boundaries, hard constraints
- `docs/design.md` — architecture boundaries, repository-mediated access rules
- `docs/implementation-control.md` — current gate, guardrails, non-goals
- `docs/reviews/docling-semantic-residual-rule-design-controller-judgment-20260617.md` — binding next-gate amendments (items 1-6)
- `docs/reviews/docling-semantic-residual-rule-design-20260617.md` — accepted design
- `docs/reviews/docling-semantic-residual-rule-design-review-ds-20260617.md` — prior DS review with DS-01 through DS-06 findings
- `docs/reviews/docling-semantic-residual-rule-design-review-mimo-20260617.md` — prior MiMo review
- `fund_agent/fund/documents/candidates/source_truth_residual_closure.py` — current dataclasses, evaluator, coercion functions
- `tests/fund/documents/test_docling_source_truth_residual_closure.py` — current test suite

---

## Findings

### DS-P1 未修复-中-`row_hierarchy_path` 默认行为使用"may"措辞导致实现歧义

- **位置**: plan 第 134 行，`row_hierarchy_path` 字段定义
- **问题类型**: 实现歧义
- **当前写法**: "if implementation can prove no parent and path is absent, may set to current `row_label_path`"
- **反例/失败场景**: 实施 Agent A 理解为"无父行时 row_hierarchy_path 应等于 row_label_path"，实施 Agent B 理解为"无父行时 row_hierarchy_path 保持 ()"。这会导致同样的 standalone 行在不同实现下产生不同的 `row_hierarchy_path` 值。下游规则评估如果检查 `row_hierarchy_path` 是否为空来判断是否有层级信息，两个实现会产生不同的闭合结果。
- **为什么有问题**: "may" 是许可性措辞而非规范性措辞。`row_hierarchy_path` 的默认值和空值语义直接影响 S6-F049/S6-F050 的层级区分逻辑。当前计划说 `row_hierarchy_role="unknown"` 时 fail-closed，但如果 `row_hierarchy_path` 被设为 `row_label_path` 而 role 仍为 `unknown`，这会产生不一致的内部状态。
- **直接证据**: plan 第 134 行 "may set to current `row_label_path`"；plan 第 244 行 "Value equality, expected field name, row order alone, or nearby duplicate text alone must not prove hierarchy." 与使用 `row_label_path` 作为 hierarchy path 之间存在张力——如果 `row_label_path` 本身是从平面标签来的，那用它填充 `row_hierarchy_path` 就没有增加任何新信息。
- **影响**: 实施 Agent 跑偏 / 不同实现产生不一致闭合结果
- **建议改法和验证点**: 将"may"改为明确规则：(a) 如果上游能证明该行无父行且非子行，`row_hierarchy_path` 应设为 `row_label_path` 且 `row_hierarchy_role` 应设为 `"standalone"`；(b) 如果无法证明，两者均保持默认值 `()` 和 `"unknown"`。在测试用例中增加 standalone 行 hierarchy path 的显式断言。
- **修复风险**: 低（措辞修正）
- **严重程度**: 中

### DS-P2 未修复-中-`column_header_band_path` 在消费者侧的语义未定义

- **位置**: plan 第 131 行 `column_header_band_path` 字段定义；第 263-265 行 share-class 证明来源；第 288-289 行 period-context 证明来源
- **问题类型**: 契约缺失
- **当前写法**: `column_header_band_path` 被定义为 "multi-row/multi-column header bands, outer-to-inner"。Share-class 证明来源包含 `header_band`，period-context 证明来源包含 `header_band`。但计划未说明：(a) share-class/period 检测函数如何消费 `column_header_band_path` vs `column_header_path`；(b) 两个字段的值是否可能重叠（例如某些实现可能把 header band 内容也放入 `column_header_path`）；(c) 消费优先级——是先检查 `column_header_path` 再 fallback 到 `column_header_band_path`，还是两者平等检查。
- **反例/失败场景**: 某基金年报的费用表中，列标题是"本期"和"上期"，而份额类别"A类/C类"标在更上层表头 band 中。如果实现只检查 `column_header_path`（当前 `_has_share_class_context` 的行为），即使 `column_header_band_path` 明确包含"A类/C类"，F015 的 C 份额检查仍会失败。但如果实现同时检查两个字段且不定义优先级，在 column_header_path 包含模糊标签而 band_path 包含确定标签时，可能产生不确定的结果。
- **为什么有问题**: 计划正确地识别了 header band 可能是份额/期间上下文的唯一来源（这解决了之前 DS-04 的 concern），但没有说明消费者应如何使用这个新字段。实施 Agent 需要自行决定 `_has_share_class_context` 的检查范围扩展方式。
- **直接证据**: 当前 `_has_share_class_context`（`source_truth_residual_closure.py:1267-1295`）仅接收 `values: tuple[str, ...]`（来自 `column_header_path`），不检查 header band 或 row label。计划在第 263-265 行和第 288-289 行将 header_band 列为证明来源，但 Slice 2（第 396-407 行）只说"canonical share-class context and allowed sources"和"canonical period context"，未定义消费函数的输入面变更。
- **影响**: 实施 Agent 跑偏 / share-class 和 period 检测在不同实现间不一致
- **建议改法和验证点**: 在 Slice 2 描述中或字段定义表中增加：(a) share-class/period 检测函数的输入应为 `(column_header_path, column_header_band_path, row_label_path, table_context)` 四个来源的联合；(b) 检测优先级为 column_header_path > column_header_band_path > row_label_path > table_context，任一来源提供确定性证据即可；(c) 或改为所有来源平等检查，不做优先级排序。同时更新测试用例覆盖"份额类别仅在 header band 中体现"的场景。
- **修复风险**: 低
- **严重程度**: 中

### DS-P3 未修复-低-`_coerce_cell()` 中派生 `table_family` 的边界未定义

- **位置**: plan 第 348-349 行 coercion contract
- **问题类型**: 性能/边界模糊
- **当前写法**: "If `table_family` is missing, `_coerce_cell()` may derive it using the deterministic classifier above from available fields."
- **反例/失败场景**: `_coerce_cell()` 当前是纯数据转换函数，不涉及任何分类逻辑。如果在 coercion 阶段引入表族分类，每个 cell 的 coercion 都会触发分类计算。对于 S5 样本（`cell_reference_count=6879`），这意味着 6879 次独立的分类调用。而且单个 cell 的可用信号（仅自己的 row_label_path、column_header_path、table_context）远少于完整 table 上下文，分类准确率会下降。
- **为什么有问题**: (a) 表族分类本质上是表级别（table-level）而非单元格级别（cell-level）的概念——同一张表的所有 cell 应共享同一个 `table_family`。在 coercion 阶段做 per-cell 分类既低效又不准确。(b) "may derive"中的"may"再次引入实现歧义——实施 Agent 可能选择不做分类（所有缺失 table_family 保持 unknown），也可能选择做 per-cell 分类。建议的 per-cell 分类路径会导致同一张表的不同 cell 被赋予不同的 table_family，破坏规则的确定性。
- **直接证据**: plan 第 348-349 行；plan 第 196-217 行的分类规则需要 table_title_path、heading_path 等表级信号，单个 cell 不一定拥有全部这些信息。
- **影响**: 性能浪费 / 分类不一致
- **建议改法和验证点**: 将 `table_family` 的派生从 `_coerce_cell()` 移到 bundle 级别的后处理步骤（如 `_coerce_bundle()` 或独立的 `_classify_bundle_tables()`），以 table_id 为粒度做一次分类后广播到该表的所有 cell。`_coerce_cell()` 缺失 `table_family` 时直接设为 `"unknown"`，由上层负责填充。更新 Slice 2 描述以反映这个两阶段流程。
- **修复风险**: 低
- **严重程度**: 低

### DS-P4 未修复-低-`bounded_neighbor_row_labels` 的正向用途未定义

- **位置**: plan 第 136 行 `bounded_neighbor_row_labels` 字段定义
- **问题类型**: 规格不完整
- **当前写法**: "optional bounded context only; must not prove closure by itself"
- **反例/失败场景**: 字段被加入 dataclass 但从未被任何规则消费。实施 Agent 不知道是否应在 reference-bundle 构建时填充此字段，也不知道填充范围（上下各多少行？）。如果规则评估从不读取此字段，它就是 dead code。如果某个实施 Agent 决定在规则评估中参考它（尽管计划说"must not prove closure by itself"），它可能被作为辅助信号使用而产生不一致。
- **为什么有问题**: 计划只说了这个字段不能做什么，没说要它做什么。字段的存在本身暗示它应该有某种用途（例如帮助人类审查者理解上下文、未来诊断用途），但计划没有显式说明。如果它是纯诊断/人类审查用途，应标注为 `diagnostic_only`；如果它有辅助用途（如增强分类信号但不独立决定闭合），应说明。
- **直接证据**: plan 第 136 行；plan Slice 2（第 396-407 行）未提及如何使用此字段。
- **影响**: dead code / 实现不一致
- **建议改法和验证点**: 在字段定义中显式标注用途——建议标注为 `diagnostic_only` 并说明它可用于人类审查或未来诊断，不在当前 Slice 1-3 中用于闭合决策。或在非目标列表中增加"bounded_neighbor_row_labels 不作为规则评估输入"的显式声明。
- **修复风险**: 低
- **严重程度**: 低

### DS-P5 未修复-低-旧字段 `required_table_family_any` 与新字段共存时的优先级规则缺失

- **位置**: plan 第 176 行和第 228 行
- **问题类型**: 契约缺失
- **当前写法**: "Existing `required_table_family_any` remains as legacy raw-context fallback for non-target rules. For the seven target residual rows, implementation must use `allowed_table_families` / `rejected_table_families`"；"_match_satisfies_rule() checks rejected families before allowed families."
- **反例/失败场景**: 一个 rule 同时设置了 `required_table_family_any=("投资组合",)` 和 `allowed_table_families=("portfolio_asset_composition_table",)`。`_match_satisfies_rule()` 应该先检查新字段（allowed/rejected）还是旧字段？如果新旧字段都通过，是 AND 还是 OR？如果旧字段通过但新字段拒绝，应如何处理？
- **为什么有问题**: 计划明确说旧字段保留给非目标规则使用，但没有定义当新字段和旧字段同时出现在同一个 rule 上时（无论是错误配置还是过渡期）的优先级。实施 Agent 需要自行决定处理方式。由于 plan 的说法可以理解为"两者不应同时存在"，但没有 fail-safe 机制。
- **直接证据**: plan 第 176 行 "Existing `required_table_family_any` remains as legacy raw-context fallback for non-target rules"；plan 第 228 行 "Legacy `required_table_family_any` may remain for existing tests, but target rows must not rely on it as the sole proof."
- **影响**: 实施 Agent 跑偏（低概率）
- **建议改法和验证点**: 在 `_match_satisfies_rule()` 描述中增加一条规则：当 `allowed_table_families` 或 `rejected_table_families` 非空时，忽略 `required_table_family_any`（仅检查新字段）。并在 Slice 2 测试中增加"同时设置新旧字段时新字段优先生效"的用例。
- **修复风险**: 低
- **严重程度**: 低

---

## Controller Amendment Coverage Verification

逐项验证 plan 是否覆盖了 controller judgment 的六项 binding next-gate amendments：

| # | Amendment | Plan coverage | Verdict |
|---|-----------|---------------|---------|
| 1 | Reference-bundle data model: exact field names, types, serialization | plan §"Field Spec with dataclass-level changes"，三个 dataclass 的字段表均包含 Field/Type/Default/Serialization | **PASS** — 完整覆盖，每个字段都有明确的类型、默认值和序列化/coercion 行为 |
| 2 | Table-family classification: deterministic signals, labels, failure behavior, consumption | plan §"Table-family Classification Spec"，包含信号优先级、10 个 label、确定性分类规则表、unknown/failure behavior、consumption by residual closure | **PASS** — 覆盖完整，分类规则有明确的信号来源和优先级 |
| 3 | Row hierarchy encoding: parent/child representation, row_label_path preservation, equity/stock distinction | plan §"Row-hierarchy Predicate Spec"，包含 encoding、proof requirement、predicate behavior、field-specific hierarchy | **PASS with DS-P1** — 覆盖完整但 row_hierarchy_path 默认行为有"may"歧义 |
| 4 | Share-class and period-context: proof sources, canonical variants | plan §"Share-class and Period-context Spec"，包含证明来源、canonical 值、字段特定要求 | **PASS with DS-P2** — 覆盖完整但 header_band 消费语义未定义 |
| 5 | Diagnostic scope: optional/future | plan 第 359-363 行 "Diagnostics: Rejected-match diagnostics are optional/future." | **PASS** — 明确标注为 optional/future |
| 6 | Partial enrichment: fail-closed, partially enriched bundles close only when required predicates are proven | plan §"Partial enrichment behavior" 第 365-370 行 | **PASS** — 明确语义 |

---

## Review Focus Compliance

| Check | Result |
|-------|--------|
| Dataclass fields, types, defaults, to_dict/coercion 是否足够 code-generation-ready | **PASS with DS-P1, DS-P2** — 三个 dataclass 的字段定义完整且包含类型、默认值、序列化行为。DS-P1（row_hierarchy_path 默认歧义）和 DS-P2（header_band 消费语义）是剩余的实现歧义 |
| Table-family classifier 是否确定性且可实施 | **PASS with DS-P3** — 分类规则有明确的信号来源、优先级顺序和确定性规则表。DS-P3（coercion 阶段 per-cell 分类）是效率/粒度问题 |
| Row hierarchy 编码和消费是否明确 | **PASS with DS-P1** — 层级编码清晰，proof requirement 显式排除了 value equality/order/adjacency。DS-P1 的"may"是剩余歧义 |
| Share/period context 是否完整定义 | **PASS with DS-P2** — 规范化值、证明来源、字段特定要求均已定义。header_band 消费方式是剩余 gap |
| Benchmark text-span context 是否正确 fail-closed | **PASS** — S6-F041 显式保持 RESIDUAL 除非 benchmark-labeled context 被证明，investment-objective 被拒绝 |
| Partial enrichment 行为是否 fail-closed | **PASS** — 显式声明 missing enriched context fails closed，部分丰富的 bundle 只在所需 predicate 全部证明时才闭合 |
| 是否保留 NOT_READY, candidate-only, no source truth, no baseline promotion, no parser replacement, no full field correctness, no readiness/release/PR | **PASS** — Non-goals § 第 472-486 行完整列出所有 guard flags；plan § 第 14-25 行确认 NOT_READY；Completion Report 确认所有 boundaries |
| 年报访问是否保持 repository-mediated | **PASS** — plan 第 25-26 行显式声明；第 181 行 "uses only already loaded repository-reference context" |
| 是否禁止按值相等闭合行 | **PASS** — plan 第 244 行、第 467 行显式禁止；S6-F049/S6-F050 的 stop condition 要求 hierarchy 证明 |
| S6-F041 是否 fail-closed 直到 benchmark label 被证明 | **PASS** — plan 第 317-332 行完整定义；investment-objective 被显式拒绝 |
| S6-F049/S6-F050 是否 fail-closed 直到 row hierarchy 区分 | **PASS** — plan 第 250-252 行、第 381-382 行显式保留 RESIDUAL |
| 是否引入过度设计或阻塞性实现歧义 | **PASS with findings** — DS-P1 和 DS-P2 是中等严重度的实现歧义，大概率不会导致错误闭合（因为 plan 已有 fail-closed 默认），但可能导致不一致实现。DS-P3/DS-P4/DS-P5 是低严重度 edge case。无阻塞性发现 |

---

## Architecture Boundary Check

- **Repository access boundary**: plan 第 25-26 行 "Annual-report access remains repository-mediated. Future implementation must not add Service/UI/Host/renderer/quality-gate direct parser, PDF, cache, source-helper, Docling, or provider access." **PASS**。
- **Candidate internals boundary**: plan §"Implementation Slices" Slice 1 限定文件为 `source_truth_residual_closure.py` 和对应测试，明确在 candidate internals 内。**PASS**。
- **Pure helper boundary**: plan 第 394 行 "Preserve pure-helper boundary: no file reads, no repository calls, no source helper imports." 与当前 code fact 一致。**PASS**。
- **No Service/UI/Host/renderer access**: Non-goals 第 484 行显式禁止。**PASS**。
- **No live/network/source acquisition**: plan 第 456 行 "No live/network/source acquisition/provider/LLM/analyze/checklist/golden/readiness/release commands are authorized by this plan." **PASS**。

## Guard Flag Consistency Check

Plan 中出现的所有 guard flag 与 evidence matrix 和 controller judgment 一致：
- `NOT_READY` ✓（第 3 行 HANDOFF_READY_NOT_READY）
- `candidate_only` ✓（第 16 行）
- `not_source_truth` ✓（第 19-20 行 "no source truth acceptance"）
- `not_baseline_promotion` ✓（第 21 行 "no baseline promotion"）
- `not_parser_replacement` ✓（第 22 行 "no parser replacement"）
- `not_full_field_correctness` ✓（第 23 行 "no full field correctness claim"）
- `not_release_readiness` ✓（第 24 行 "no release readiness or PR readiness"）
- `repository_access_only_via_fund_document_repository` ✓（第 25-26 行）

---

## Open Questions

1. **`row_hierarchy_path` 与 `row_label_path` 的关系**：当行是 standalone（无父行、无子行）时，`row_hierarchy_path` 是否应等于 `row_label_path`？Plan 用"may"留下了歧义。建议计划明确规则：如果上游能证明 standalone，则 `row_hierarchy_path = row_label_path` 且 `row_hierarchy_role = "standalone"`；否则两者分别保持 `()` 和 `"unknown"`。

2. **`column_header_band_path` 的消费实现**：Share-class 和 period 检测是否需要扩展到接收 `column_header_band_path` 作为额外输入？当前 `_has_share_class_context` 只接收 `column_header_path`，Slice 2 未说明如何修改其函数签名。

3. **`table_family` 分类应在哪一层执行**：Plan 建议在 `_coerce_cell()` 中做 per-cell 分类，但表族是 table-level 概念。建议实施时在 bundle 级别做 table-level 分类后广播到 cell，避免 per-cell 重复计算和同一表内 cell 的 table_family 不一致。

4. **Benchmark text-span 的 `semantic_context_label` 赋值逻辑**：Plan 定义了 `TextSemanticContext` literal 和 benchmark acceptance predicate，但没有说明 `semantic_context_label` 是在 reference-bundle 构建时由上游赋值，还是在 Slice 2 规则评估时由 helper 推导。这影响 Slice 1 的 coercion 行为——`_coerce_text_span()` 应该直接从 payload 读取 `semantic_context_label` 还是从 `context_label`/`heading_path`/`section_id` 推导？

---

## Residual Risks

| Risk | Severity | Owner | Suggested Tracking |
|------|----------|-------|-------------------|
| `row_hierarchy_path` 默认行为的"may"歧义导致不同实现产生不同的 hierarchy 值 | 中 | Slice 1 实施 gate | 在 Slice 1 plan 或 implementation gate 中接受 plan reviewer 的澄清建议 |
| `column_header_band_path` 消费语义未定义导致 share/period 检测不一致 | 中 | Slice 2 实施 gate | 在 Slice 2 实施前明确 `_has_share_class_context` 和 period 检测的输入面变更 |
| per-cell table_family 分类导致同一表内 cell 的 table_family 不一致 | 低 | Slice 2 实施 gate | 实施时在 table 级别做分类后广播，而非在 cell coercion 中做 |
| `bounded_neighbor_row_labels` 成为 dead code | 低 | Slice 1 实施 gate | 标注为 diagnostic_only 或在测试中验证其存在但不影响闭合 |
| 新旧 table_family 字段共存时的优先级未定义 | 低 | Slice 2 实施 gate | 在 `_match_satisfies_rule()` 实现中显式处理新字段优先 |

---

## Validation Checks

以下验证基于 plan 的显式声明和 cross-reference 检查：

1. Plan 是否完整覆盖 controller judgment 六项 binding amendments：**PASS**（见上表）
2. Plan 是否保留了 DS-01/DS-02/DS-03 的修复：**PASS** — 数据模型字段已完整定义（DS-01），表族分类已有确定性规则（DS-02），行层级谓词已关联到 ResidualClosureRule 新字段（DS-03）
3. Plan 是否处理了 DS-04（份额检查范围扩展）：**PASS with DS-P2** — share-class 来源扩展到了 header_band/row_label/table_context，但消费侧语义未定义
4. Plan 是否处理了 DS-05（诊断信息超出范围）：**PASS** — 诊断信息已标注为 optional/future
5. S6-F041 是否仅在 benchmark-labeled context 下闭合：**PASS** — 在 plan 第 317-332 行和 per-residual 表中有显式保证
6. S6-F049/S6-F050 同值案例是否 fail-closed：**PASS** — plan 第 250-252 行和第 381-382 行显式保留 RESIDUAL
7. 所有 stop condition 是否覆盖了 plan 第 460-470 行列出的场景：**PASS** — 10 项 stop condition 与 per-residual 表和 predicate spec 一致

---

## Verdict

**PASS_WITH_FINDINGS**

Plan 完整覆盖了 controller judgment 的全部六项 binding next-gate amendments，为三个 dataclass 提供了 code-generation-ready 级别的字段定义（类型、默认值、序列化行为、coercion 契约），并给出了确定性的 table-family 分类规则、行层级编码规范、share/period context 规范化值和 benchmark text-span fail-closed 语义。所有 guard flags（NOT_READY、candidate-only、no source truth、no baseline promotion、no parser replacement、no full field correctness、no release/PR readiness）均被显式保留。Annual-report 访问保持 repository-mediated，无直接 PDF/cache/source-helper 路径。

五个发现（DS-P1 至 DS-P5）均不阻塞本 gate：
- DS-P1（row_hierarchy_path "may" 歧义）和 DS-P2（header_band 消费语义）是中等严重度，建议在下一 gate 实施前澄清，但 plan 有 fail-closed 默认保护，不会导致错误闭合。
- DS-P3（per-cell 分类）、DS-P4（bounded_neighbor_row_labels 用途）、DS-P5（新旧字段优先级）是低严重度边缘情况，可在实施时处理。

无阻塞性发现。Plan 可以进入下一 implementation gate。
