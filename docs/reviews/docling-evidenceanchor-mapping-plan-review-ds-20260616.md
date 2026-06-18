# Docling EvidenceAnchor Mapping Plan — DS Scoped Review

Date: 2026-06-16
Reviewer: AgentDS
Reviewed target: `docs/reviews/docling-evidenceanchor-mapping-plan-20260616.md`
Gate: `Docling EvidenceAnchor Mapping Plan Review Gate`
Release/readiness: `NOT_READY`

## 1. Review Scope (DS per plan §11)

Per the plan's own review focus assignment:

- Whether the mapping rules preserve current `EvidenceAnchor` semantics without schema drift.
- Whether the parent-table context rule is sufficient for table-cell anchors.
- Whether stop conditions prevent fabricated `section_id`, `page_number`, `table_id`, or `row_locator`.
- Whether future validation can catch cell-only, table-without-cell, and no-section cases.

This review does NOT cover MiMo-scoped items (Fund containment, source_kind expansion guard, candidate-only guardrails, next gate narrowness) — those are deferred to the MiMo review.

## 2. Assumptions Tested

| # | Assumption | Verdict |
|---|-----------|--------|
| A1 | Mapping can use existing `EvidenceAnchor` fields without schema change. | Holds: plan uses only `source_kind`, `document_year`, `section_id`, `page_number`, `table_id`, `row_locator`, `note`. No new field proposed. |
| A2 | `source_kind="annual_report"` with `candidate_only=true` in `note` is sufficient to keep candidate anchors distinguishable from production. | Weakened: see DS-F1. |
| A3 | S1 `provenance_locator` provides enough context to deterministically resolve parent table for every cell. | Not fully validated: see DS-F3. |
| A4 | S4/S5/S6 lightweight schema has sufficient section hierarchy for `section_id` resolution. | Not validated: see DS-F4. |
| A5 | Stop conditions are comprehensive and mechanically enforceable. | Mostly holds: see §3 assessment below—gaps are narrow. |
| A6 | Future validation matrix can be operationalized without further design. | Holds: deferral to next gate is appropriate. |

## 3. EvidenceAnchor Schema & Semantic Preservation Assessment

### 3.1 Schema drift — PASS

The plan does not propose new `EvidenceAnchor` fields, new `EvidenceSourceKind` literals, or field renames. All seven current fields are mapped with explicit rules. The non-goals (§2) explicitly prohibit schema change. The stop condition (§10, line 1) triggers if any mapping needs a schema change.

### 3.2 Semantic boundary — PASS_WITH_FINDING

All existing semantic constraints from `docs/design.md` §5.5 and `models.py` `EvidenceAnchor` docstring are addressed:

- `source_kind`: mapped as `annual_report` for annual-report candidates (§7.2)
- `document_year`: from accepted document identity (§7.1 step 1)
- `section_id`: priority-ordered resolution with explicit stop (§7.3)
- `page_number`: type-specific rules with explicit stop (§7.4)
- `table_id`: set for table/cell, unset for heading/paragraph (§7.5)
- `row_locator`: cell-only with structured format, unset otherwise (§7.6)
- `note`: structured format with explicit `candidate_only` marker (§7.7)

One finding (DS-F1) on `source_kind` candidate/production boundary — see below.

## 4. Findings

### DS-F1 — 未修复 — 中 — `source_kind="annual_report"` 使候选锚点在类型级别与生产锚点不可区分

- **位置**: §7.2 `source_kind` 映射规则
- **问题类型**: 架构边界 / 契约缺失
- **当前写法**: 对年报 PDF 候选使用 `source_kind="annual_report"`，`candidate_only=true` 和 `candidate_source=docling` 仅在 `note`（§7.7）中携带。候选状态与生产状态之间没有程序化边界。
- **反例/失败场景**: 实现 Agent 将映射代码放在 extractor 模块中并输出 `EvidenceAnchor(source_kind="annual_report", ..., note="candidate_source=docling;candidate_only=true;...")`。后续代码重构时丢弃或截断 `note` 字段，锚点流入生产 evidence store。由于 `EvidenceSourceKind` 是 `Literal["annual_report", "external_api", "derived"]`，没有类型级别的方式区分这个锚点是候选还是生产。审计器、质量门控或报告渲染器会将其视为生产年报证据。
- **为什么有问题**: `EvidenceSourceKind` 的字面类型只包含 `annual_report`、`external_api`、`derived`。一旦候选锚点被赋值为 `source_kind="annual_report"`，所有下游消费者在类型层面都认为它是生产锚点。`note` 中的 `candidate_only=true` 是 convention，不是 contract。`docs/design.md` §6.1 中 `eid_xbrl_html_render_candidate` 的未来设计已声明“候选 `EvidenceAnchor` 映射必须保持 `page_number=null`，并在 `note` 中保留候选元数据”，说明设计真源期望候选锚点有区别于生产锚点的路径。当前方案将区分逻辑完全压缩进 `note`，没有程序化 guard。
- **直接证据**:
  - `fund_agent/fund/extractors/models.py:11`: `EvidenceSourceKind = Literal["annual_report", "external_api", "derived"]`
  - `fund_agent/fund/extractors/models.py:101`: `source_kind: EvidenceSourceKind`
  - Plan §7.2: "使用 canonical `source_kind="annual_report"` 仅用于候选/投影证据内部"
  - Plan §7.7: `candidate_only=true` 仅在 `note` 结构化文本中
  - `docs/design.md` line 676: EID XBRL HTML render 候选设计声明候选 `EvidenceAnchor` 应保持 `page_number=null` 并在 `note` 中保留元数据——说明设计真源预期候选锚点有独立路径
- **影响**: 实施 Agent 生成的候选锚点在类型层面与生产锚点不可区分；后续重构可能静默将候选锚点提升为生产证据；审计和质量门控没有程序化方式检测候选锚点混入。
- **建议改法和验证点**:
  1. 在实施规划 gate 中显式声明：候选映射输出不得直接构造裸 `EvidenceAnchor` 对象并放入生产 evidence store。候选输出必须通过一个候选包装类型或独立的候选 artifact 路径（如 JSON 文件、候选专用集合），与生产 `EvidenceAnchor` 流保持程序化隔离。
  2. 或在后续 schema gate 中评估是否需要 `candidate_source_kind` 元数据字段或候选包装 dataclass。
  3. 验证点：实施规划 gate 必须显式写出“候选锚点不得流入生产 evidence store”的约束及其 enforce 机制。
- **修复风险（低）**: 不需要修改本 plan；在下一个实施规划 gate 中显式声明约束即可。
- **严重程度（中）**: 不阻塞本 planning gate，但若不在实施规划前收敛将在实施阶段产生结构性风险。

### DS-F2 — 未修复 — 中 — 映射代码模块边界未声明

- **位置**: 整个 plan 缺失模块归属声明（§7-8 应包含但未包含）
- **问题类型**: 架构边界 / 过度耦合
- **当前写法**: Plan 定义了映射规则（§7），按元素类型的处理行为（§8），但未声明映射逻辑应写入哪个模块、文件或包。
- **反例/失败场景**: 实施 Agent 将映射代码放在 `fund_agent/fund/extractors/` 或 `fund_agent/cli/` 或独立脚本中，直接读取 Docling JSON 并输出 EvidenceAnchor。后续 Service 或 CLI 层直接调用映射函数，绕过 `FundDocumentRepository` 边界。
- **为什么有问题**: `AGENTS.md` §121-127 和 `docs/design.md` §6.1（line 666）均要求 Docling 或其它文档中间层必须封装在 `FundDocumentRepository` / Fund documents 层内部。`docs/design.md` line 666 明确：“Docling 或其它文档中间层必须封装在 `FundDocumentRepository` / Fund documents 层内部。Service、UI、Host、renderer、quality gate 不得直接调用 Docling、PDF 文件、parser cache 或下载 helper。” 映射逻辑如果不指定模块边界，实施 Agent 可能将其放在错误位置，导致未来的 containment 和 boundary 审查成本更高。
- **直接证据**:
  - `AGENTS.md` lines 121-127: 模块边界归属规则
  - `docs/design.md` line 666: “Docling 或其它文档中间层必须封装在 `FundDocumentRepository` / Fund documents 层内部”
  - `docs/design.md` line 662: `FundDisclosureDocument` “应在 Fund documents 层内部表达”
  - Plan §2 non-goals: “Do not change EvidenceAnchor schema, FundDocumentRepository, source policy, parser behavior, Service, Host, UI, renderer, quality gate” — 但未声明映射代码的模块归属
- **影响**: 实施 Agent 可能将映射代码放在错误模块；Service/Host/UI 可能直接调用映射函数；后续 containment 审查需要回溯修正。
- **建议改法和验证点**:
  1. 在 plan §7 或 §8 中增加一条显式声明：映射代码的候选实现必须放在 `fund_agent/fund/documents/candidates/` 内，作为候选文档表示层的内部映射 helper。
  2. 实施规划 gate 必须验证映射模块的导入路径不穿透 Fund documents 边界。
- **修复风险（低）**: 在 plan 中增加一行模块归属声明。
- **严重程度（中）**: 不阻塞本 planning gate，但缺失归属声明会增加实施 Agent 的决策负担和放错位置的风险。

### DS-F3 — 未修复 — 中 — S1 cell 到 parent table 的解析算法未指定

- **位置**: §5.1 cell 行 + §8 cell 行
- **问题类型**: 切片过粗 / 不可直接实施
- **当前写法**: §5.1 写 "cell-level `provenance_locator` plus parent table identity, parent table page, row/column position"。§8 cell 行写 "Map only with parent table context. Use parent `table_id`, page, row/column locator"。§6 写 "A cell candidate cannot map to `EvidenceAnchor` without resolving its parent table. `table_id` must come from the parent table, not from a cell-local synthetic value."
- **反例/失败场景**: S1 的完整表示 JSON 有 95 个表和 3493 个 cell。一个 cell 的 `provenance_locator` 可能包含 page reference 但不包含直接的 `parent_table_id` 字段。实施 Agent 需要自己发明 cell-to-table 匹配算法：按 page？按 bbox 包含？按文档顺序取最近的前一个 table？不同策略产生不同映射结果。如果算法选错，cell 可能被匹配到错误的父表，导致 `table_id` 不正确。
- **为什么有问题**: Plan 要求 parent table context 是必需的（§6），但未给出如何从 S1 cell 的候选 locator 中找到其父表的算法。实施 Agent 必须在规划阶段之后自行设计这个算法，这意味着本 plan 对 S1 cell 路径不够 code-generation-ready。
- **直接证据**:
  - Plan §5.1 cell 行: 假定 cell 输入包含 "parent table identity" 但不说明如何从 S1 JSON 结构中提取
  - Plan §8 cell 行: "Map only with parent table context" — 规则是明确的，但解析路径未定义
  - `coverage-summary.json`: S1 有 `table_count: 95, table_cell_count: 3493` — 匹配规模不可忽略
  - S1 使用的是 `pages` + `provenance_locator` 完整 schema（§5.1），与 S4/S5/S6 的轻量 schema 不同
- **影响**: 实施 Agent 必须自行设计 cell-to-table 解析算法；错误的解析导致 cell 映射到错误的 `table_id`；增加实施规划 gate 的设计负担。
- **建议改法和验证点**:
  1. 在 plan 中补充：S1 schema 下 cell 到 parent table 的解析策略（按 page 共现、按 document order 的前一个 table、或按 bbox/page 区域包含），至少声明选择策略的约束条件。
  2. 或在实施规划 gate 中显式声明 S1 cell-to-table 解析为独立的子任务，需在实施前完成算法设计。
  3. 验证点：实施规划 gate 必须包含 cell-to-table 解析的明确算法描述。
- **修复风险（低）**: 可在本 plan 中补充，也可在实施规划 gate 中处理。
- **严重程度（中）**: 对 S1 cell 映射路径不够 code-generation-ready。

### DS-F4 — 未修复 — 低 — S4/S5/S6 轻量 schema 的 section hierarchy 假设未验证

- **位置**: §5.2 combined with §7.3
- **问题类型**: open question 未收敛
- **当前写法**: §7.3 定义了 `section_id` 的优先级顺序：显式 section id → 最近包围 section → 规范化 heading path → 停止。§5.2 对 S4/S5/S6 声明 heading 输入包含 "section context"，但轻量 schema 的 heading 可能只有扁平 heading 文本和 page reference，没有显式的 section hierarchy。
- **反例/失败场景**: S4/S5/S6 轻量 schema 的 heading 是扁平的（没有嵌套 section 结构），实施 Agent 发现无法走“最近包围 section”路径，只能依赖“规范化 heading path 能否确定性绑定到 section”。如果 heading path 与已知 annual-report section 的匹配不够确定性，大量 heading 会触发 `mapping_blocked: missing_section_context`，导致 S4/S5/S6 的映射产出极低。
- **为什么有问题**: Plan 对 S4/S5/S6 的 section context 可用性做了一个隐式假设（§5.2 中的 "section context"），但没有验证该假设。如果假设不成立，实施规划 gate 需要处理大量 `mapping_blocked` 输出，可能需要在 plan 中提前承认该风险。
- **直接证据**:
  - Plan §5.2: 对 S4/S5/S6 heading 列出 "section context" 作为可用输入
  - Plan §7.3 优先级 2: "Else use nearest enclosing section from section hierarchy" — 假设存在 section hierarchy
  - `coverage-summary.json`: S4/S5/S6 的 heading 数分别为 229/208/222，如果大量缺少 section hierarchy，影响面大
  - 轻量 schema 的描述（§5.2）未提及嵌套 section 结构；已知 S4/S5/S6 使用的是 runtime-containment 轻量 schema
- **影响**: 如果 section hierarchy 缺失，S4/S5/S6 映射产出显著降低；风险在实施阶段暴露时可能需要回溯修改 plan。
- **建议改法和验证点**:
  1. 在 plan 中显式声明：S4/S5/S6 轻量 schema 的 section hierarchy 可用性是未验证假设，实施规划 gate 必须首先验证，若不可用则需设计仅基于 heading path 的 fallback 策略或显式接受低产出。
  2. 验证点：实施规划 gate 的第一步应是对 S4/S5/S6 候选 JSON 做 section hierarchy 存在性检查。
- **修复风险（低）**: 作为风险声明加入 plan 即可。
- **严重程度（低）**: 不阻塞，但应在实施前确认。

## 5. Stop Conditions Assessment

Plan §10 列出的 stop conditions 覆盖了当前 gate 范围内的关键失败模式：

| Stop condition | Coverage | Assessment |
|---|---|---|
| Schema change needed | Covered | Directly triggers return to controller |
| New production `source_kind` needed | Covered | §7.2 + §10 line 2 |
| Cell mapping loses parent table context | Covered | §6 + §8 + §10 line 3 |
| Section context not deterministically resolvable | Covered | §7.3 + §10 line 4 |
| Page number absent for Docling PDF | Covered | §7.4 + §10 line 5 |
| Would need production parser/repo/Service/Host/UI changes | Covered | §10 lines 6-7 |
| Untracked residue used as proof | Covered | §10 line 8 |

The stop conditions are mechanically enforceable. The one gap is that they are procedural (stop and return to controller), not programmatic (enforced by code). Since this is a planning gate, procedural stops are appropriate.

## 6. Future Validation Assessment (Plan §9)

The future validation matrix (§9) correctly identifies scenarios for cell-only, table-without-cell, and no-section cases:

- "Cell cannot resolve parent table" (line 216) → catches cell-only
- "Table without cells" (line 219) → catches table-without-cell value claim
- "Missing section/page" (line 213, 214) → catches no-section cases

The matrix defers validation commands to the next gate, which is appropriate for a planning artifact. The pass/stop conditions are clearly stated.

One observation: the matrix does not have a scenario for "candidate anchor mistakenly ingested as production evidence." This is a deferred concern (see DS-F1), but worth noting.

## 7. Open Questions

| # | Question | Recommended owner |
|---|---|---|
| Q1 | Will the S1 cell → parent table resolution rely on page co-occurrence, bbox containment, or document-order proximity? | Implementation planning gate |
| Q2 | Does the S4/S5/S6 lightweight schema actually carry section hierarchy, or only flat headings? | Implementation planning gate (first verification step) |
| Q3 | Should candidate EvidenceAnchor output live in a separate artifact file (JSON) rather than in-memory EvidenceAnchor objects? | Implementation planning gate (informed by DS-F1) |
| Q4 | Should the `note` structured format be defined as a typed dataclass or kept as a semicolon-delimited string? | Implementation planning gate |

## 8. Residuals

| Residual | Severity | Recommended destination |
|---|---|---|
| Candidate `source_kind` boundary is convention-only (DS-F1) | Medium | Next implementation planning gate — require programmatic candidate/production boundary |
| Module boundary for mapping code undeclared (DS-F2) | Medium | Plan amendment or implementation planning gate — declare `fund_agent/fund/documents/candidates/` |
| S1 cell-to-table resolution algorithm unspecified (DS-F3) | Medium | Implementation planning gate — design resolution strategy before implementation |
| S4/S5/S6 section hierarchy availability unvalidated (DS-F4) | Low | Implementation planning gate — verify as first step |

## 9. Verdict

```text
VERDICT: PASS_WITH_FINDINGS
```

### Findings table

| Finding | Severity | Recommendation |
|---|---|---|
| DS-F1: candidate `source_kind` silently indistinguishable from production | 中 | Next gate must declare programmatic candidate/production boundary |
| DS-F2: mapping code module boundary undeclared | 中 | Add module归属 to plan or implementation planning gate |
| DS-F3: S1 cell→parent table resolution unspecified | 中 | Design resolution algorithm before S1 cell implementation |
| DS-F4: S4/S5/S6 section hierarchy assumption unvalidated | 低 | Verify as first step in implementation planning gate |

### Final recommendation

The plan preserves EvidenceAnchor semantics, has sound parent-table context rules, and has adequate stop conditions. Four findings (all medium or low) identify gaps that can be addressed in the next implementation planning gate without requiring plan rejection. None of the findings requires plan rewrite.

Recommended controller action: ACCEPT this plan and route DS-F1 through DS-F4 as binding constraints for the `Docling EvidenceAnchor Mapping No-live Implementation Planning Gate`.
