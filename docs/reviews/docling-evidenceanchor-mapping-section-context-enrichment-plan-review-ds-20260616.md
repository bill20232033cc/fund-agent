# Docling EvidenceAnchor Mapping Section-context Enrichment Plan Review — AgentDS — 2026-06-16

Gate: `Docling EvidenceAnchor Mapping Section-context Enrichment Plan Review Gate`
Role: AgentDS review worker
Release/readiness: `NOT_READY`

## Reviewed Target

Plan artifact: `docs/reviews/docling-evidenceanchor-mapping-section-context-enrichment-plan-20260616.md`

## Sources of Truth Consulted

| Source | Purpose |
| --- | --- |
| `AGENTS.md` | Execution constraints, module boundaries, candidate/production isolation |
| `docs/design.md` | Docling is candidate-layer only, not source truth, not production EvidenceAnchor |
| `docs/implementation-control.md` | Current gate classification `heavy`, binding constraints, NOT_READY |
| `docs/current-startup-packet.md` | Current mainline entry, accepted evidence chain |
| `docs/reviews/docling-evidenceanchor-mapping-evidence-controller-judgment-20260616.md` | Accepted facts: 0.43% yield, 23373 blocked, 99.96% missing section context, zero table/cell yield |
| `docs/reviews/docling-evidenceanchor-mapping-evidence-20260616.md` | Representative blocked samples, including `2.1 基金基本情况` blocked as missing_section_context |
| `fund_agent/fund/documents/candidates/evidence_anchor_mapping.py` | Current code structure, function signatures, `_SECTION_KEYWORD_FAMILIES`, `_resolve_section_id`, `_map_cell`, `_resolve_parent_table` |
| `tests/fund/documents/test_docling_evidence_anchor_mapping.py` | Existing synthetic test patterns and coverage |

## Assumptions Tested

| Assumption | Verdict | Evidence |
| --- | --- | --- |
| A1: Plan stays inside Fund documents candidate internals | **PASS** | Scope section explicitly limits to `fund_agent/fund/documents/candidates/`; non-goals exclude all production/Service/Host/UI surfaces; rule #10 preserves candidate-only metadata |
| A2: Exact write set is narrow (2 files) | **PASS** | Write set lists exactly `evidence_anchor_mapping.py` and `test_docling_evidence_anchor_mapping.py`; no source/repository/parser/Service/Host/UI |
| A3: S1 full JSON mismatch is not silently bypassed | **PASS** | Slice 6 explicitly blocks S1 full JSON; fail-closed stop rule explicitly rejects treating S1 full JSON as current envelope; regeneration deferred to separate gate |
| A4: Table/cell propagation avoids source truth claims | **PASS** | Slice 4 cells inherit from parent table only; no cell text/row_label/column_header inference; rule #10 preserves `field_correctness_status="not_proven"` and `source_truth_status="not_proven"` |
| A5: Parent table resolution remains structural | **PASS** | Slice 4 preserves existing structural rules: explicit argument → source_ref match → bbox containment; explicitly rejects content-based resolution |
| A6: Duplicate/out-of-order handling is fail-closed | **PARTIAL** — see findings DS-F1, DS-F2 |
| A7: Section normalization is deterministic and auditable | **PARTIAL** — see findings DS-F3, DS-F4 |
| A8: Tests cover both positive enrichment and safety stops | **PARTIAL** — see finding DS-F5 |
| A9: Re-evidence design can prove table/cell yield without readiness claims | **PASS** | Re-evidence section explicitly requires before/after comparison, blocked distributions, candidate-only assertions; acceptance requires yield > 0 without reducing guardrails, and still must not claim source truth/readiness |

## Findings

### DS-F1 — 中 — TOC heading duplicate risk not addressed in section index rules

- **位置**: Slice 2 (Stable Section Index), rules 2–5；Residual Risks 第2条
- **问题类型**: 状态机漏洞 / 切片过粗
- **当前写法**: Slice 2 规则 2 说"忽略不归一化为 §1..§10 的封面/报告标题/日期标题"，规则 5 说"如果两个不同的 section node 归一化为同一章节族且无法证明为同一源节点，将该章节族标记为 duplicate 且不可用于传播"。但计划没有区分目录（TOC）中的章节标题和正文中的章节标题。
- **反例/失败场景**: 年报 S4 的目录节点在页 2-3 包含 `§2 基金简介`，正文 `§2 基金简介` section node 在页 5。两个节点都归一化为 §2，但页面不同，触发规则 5 将 §2 标记为 duplicate。结果：§2 跨度的所有 table/cell/text block 都无法通过页面传播解析章节，包括正文中实际 §2 范围内的块。
- **为什么有问题**: 当前计划把目录标题归一化为正文章节后，会污染 stable section index，导致本应可映射的块大规模 fall back 到 blocked。这与计划的目标（提高 table/cell yield）冲突。计划在 Residual Risks 第2条承认"页面传播在 TOC、重复标题附近可能不安全"，但没有在 section index 构建规则中给出具体缓解措施。
- **直接证据**:
  - 证据 artifact 显示 S4 有 229 个 section node（部分来自目录/TOC），正文章节节点可能少于总数
  - Slice 2 规则 2 只排除"封面/报告标题/日期标题"，不排除目录节点
  - 当前代码 `map_candidate_document_anchor_candidates` 遍历 `document.sections` 不做目录/正文区分
- **影响**: 实施 Agent 可能实现出 yield 远低于预期的版本，因为目录污染导致大量章节族被标记为 duplicate；也可能实施 Agent 自行增加启发式 TOC 排除规则，超出计划范围
- **建议改法和验证点**:
  1. 在 Slice 2 增加一条 TOC/目录排除规则：要求 section node 的 heading level 或结构性位置排除目录页区间，或在规则 2 中明确"目录中的章节标题不作为 stable section node"
  2. 或者在 re-evidence 设计中明确预期 yield 受 TOC 影响的程度，并将 TOC 处理作为 deferred residual
- **修复风险**: 中——需要判断目录页区间，可能与页面范围耦合
- **严重程度**: 中

### DS-F2 — 中 — monotonic ordering rule 与分节段内子标题的交互未定义

- **位置**: Slice 2 规则 4
- **问题类型**: 状态机漏洞
- **当前写法**: "Require monotonic annual section ordering by first stable page."
- **反例/失败场景**: 年报正文中，§8 的 section node 页 60，但 §8 的第一个子标题 section node（如 `8.1 期末基金资产组合情况`）作为 Docling section node 可能在页 58 出现（因为它前面的文本跨页）。子标题归一化到 §8，但页面在 §7 的 section node（页 55–57）之后、§8 主标题之前。这不会破坏 §1→§2→...→§7→§8→... 的跨章节 monotonic ordering，但如果有多个 §8 子标题 section node 分散在不同页面，它们之间的 intra-section 顺序可能乱。
- **为什么有问题**: 计划没有区分"跨章节 monotonic"和"同章内子标题 monotonic"。规则 4 的措辞暗示只检查不同章节族之间的页面顺序，但没有说清楚同章节的多个 section node 是否参与 monotonic 检查。如果同章 section node 参与检查且乱序，可能错误地将整个 §8 标记为不可用。
- **直接证据**: 当前代码中 `document.sections` 包含所有层级的 section node；计划 Slice 2 规则 1 说"Index only section nodes that normalize to exactly one supported annual-report section"，意味着子标题也会进入 index
- **影响**: 实施 Agent 可能做出不同解释，导致 monotonic 检查过严（降低 yield）或过松（漏掉真正乱序）
- **建议改法和验证点**: 明确 monotonic ordering 只检查不同章节族（如 §7 的最大页 < §8 的最小页），同章 section node 不参与跨章 monotonic 检查；或者同章 node 只取最小页面作为该章节的 span 起点
- **修复风险**: 低
- **严重程度**: 中

### DS-F3 — 中 — 数值标题归一化的正则模式未完整定义

- **位置**: Slice 1 (Section Token Normalization)
- **问题类型**: 不可直接实施
- **当前写法**: "numeric body headings such as `2 基金简介`, `2.1 基金基本情况`, `8.4 报告期末按行业分类的股票投资组合`" 加上 "full-width digits and punctuation after Unicode NFKC normalization"
- **反例/失败场景**: 以下真实年报标题模式的归一化行为未定义：
  - `二、基金简介`（中文数字）— 是否归一化？
  - `（二）基金基本情况`（括号包裹）— 括号是否被 strip？
  - `第八节 基金投资组合报告` 或 `第二节 基金简介`（中文数字 + 中文量词）
  - `2、基金简介`（顿号分隔）
  - `§2.1 基金基本情况`（既含 § token 又含子章节号）— 当前 § 正则 `§\s*(\d+(?:\.\d+)*)` 会捕获 `2.1`，`split('.')[0]` 得到 `2`，但这是否符合意图？
- **为什么有问题**: 计划说"closed and deterministic"，但只列举了 happy-path 模式（显式 §、阿拉伯数字、中文第X章），没有覆盖中文数字、括号等常见变体。实施 Agent 需要自行决定这些边缘情况，可能引入不可审计的行为差异。
- **直接证据**:
  - Slice 1 接受的模式只有 3 类：explicit `§`、numeric body、Chinese chapter markers with Arabic numbers
  - 当前代码 `_ANNUAL_SECTION_PATTERN = re.compile(r"§\s*(\d+(?:\.\d+)*)")` 只处理 § token
  - 证据中 blocked sample `2.1 基金基本情况` 表明数值前缀确实缺失 § token
- **影响**: 实施 Agent 做出不可复现的归一化决策，或者保守实现导致 yield 改善有限
- **建议改法和验证点**:
  1. 增加一条：中文数字、括号中文数字、顿号分隔等不在闭合模式内，一律归一化失败 → blocked as `unsupported_heading_number`
  2. 或者显式列出要拒绝的模式，确保实施 Agent 不用猜测
- **修复风险**: 低——增加模式拒绝列表即可
- **严重程度**: 中

### DS-F4 — 低 — 关键词族别名可能覆盖不足，实施 Agent 可能越权扩展

- **位置**: Slice 1 最小别名补充
- **问题类型**: 范围漂移 / 不可直接实施
- **当前写法**: 计划添加 4 个别名（§2: 基金基本情况；§8: 两个；§9: 一个），说这是"Minimum alias additions"
- **反例/失败场景**: 实施 Agent 在归一化 `4.5 管理人对报告期内基金利润分配情况的说明` 时，发现 `4` 是 top-level 但剩余文本不匹配 §4 当前关键词族（"管理人报告"/"基金管理人"/"报告期内基金投资策略"），可能自作主张添加别名以提升 yield。同样 `8.1 期末基金资产组合情况` 已匹配 §8 的"期末基金资产组合"（现有关键词），但 `8.2 报告期末按行业分类的股票投资组合` 是新增别名。如果 `8.3 报告期末按公允价值计量的金融资产` 等子标题不匹配，实施 Agent 可能继续扩展。
- **为什么有问题**: 计划说"Minimum"，暗示可能不够但先这样。这给实施 Agent 留下了"不够就加"的灰色地带。closed keyword family 的闭合性取决于别名是否真的 closed，如果实施 Agent 在实现过程中持续添加，就不再是 plan-controlled。
- **直接证据**: 计划的 Minimum 措辞；Residual Risks 第1条承认"如果闭合关键词族太宽，数值标题归一化可能增加假阳性"
- **影响**: 实施 Agent scope creep，或者 yield 改善不如预期因为关键词族覆盖不足
- **建议改法和验证点**: 要么将"Minimum"改为"Exact"并声明后续扩展必须经过独立 gate；要么在计划中增加一个原则：任何额外别名必须先作为 blocked reason 出现并在 re-evidence 中量化后再决定是否加入
- **修复风险**: 低
- **严重程度**: 低

### DS-F5 — 中 — 测试场景未覆盖 slice 边界和新 blocked reason code

- **位置**: Tests and Validation Commands
- **问题类型**: 测试缺口
- **当前写法**: 列出了 8 个 synthetic test 场景，但缺少以下场景：
  - monotonic ordering 违规 → blocked（Slice 2 规则 4）
  - 同章节族 duplicate heading → blocked（Slice 2 规则 5）
  - multi-page table 跨越两个章节 span → `section_span_crosses_multiple_sections`（Slice 3 规则 3）
  - `unsupported_heading_number` blocked reason code 被发出（`第12章` 或 `11.1` 等超出 1..10 的编号）
  - NFKC 全角数字归一化后的模式匹配（如全角 `２．１` → 半角 `2.1`）
  - text block 通过 stable section page span 继承章节上下文（Slice 3 规则 3 的正面路径）
- **为什么有问题**: 计划说 tests 应该"cover both positive enrichment and safety stops"，但列出的 8 个测试只覆盖了归一化 happy path（2 个）、cover 拒绝（1 个）、table page span（1 个正面 + 1 个负面）、cell 继承（1 个正面）、duplicate heading（1 个）、out-of-order（1 个）和 S1 full JSON（1 个）。monotonic、multi-page cross-section、NFKC 全角等关键安全停止没有测试。
- **直接证据**: 计划第 179–187 行列出的 8 个测试场景 vs Slice 2/3 的 fail-closed 规则数量
- **影响**: 实施后可能漏掉未测试的 fail-closed 路径，re-evidence 时才发现 blocked reason 未正确触发
- **建议改法和验证点**: 在计划中补充至少 3 个测试场景：(a) monotonic ordering violation blocks propagation；(b) multi-page table crossing section spans emits `section_span_crosses_multiple_sections`；(c) heading with top-level > 10 emits `unsupported_heading_number`
- **修复风险**: 低——在测试列表中补充即可
- **严重程度**: 中

### DS-F6 — 低 — section index 数据结构与函数签名变更未指定

- **位置**: Slice 2–3 之间的实现衔接
- **问题类型**: 不可直接实施
- **当前写法**: 计划描述了 section index 的构建规则和行为，但没有说明：
  - section index 的数据结构（dataclass? dict? list?）
  - index 在哪个函数中构建、通过什么参数传递到 `_resolve_section_id` 及其调用链
  - 当前 `map_candidate_locator_to_anchor_candidate` 的签名是否需要变更
- **反例/失败场景**: 当前代码调用链是 `map_candidate_document_anchor_candidates` → `map_candidate_locator_to_anchor_candidate` → `_resolve_section_id` → `_section_candidates_from_block` / `_section_candidates_from_document_section`。section index 需要在整个文档批处理前构建一次，然后传递给每个单独块的解析。如果实施 Agent 选择每次调用 `_resolve_section_id` 时重建 index，会产生 O(n²) 行为；如果在 `map_candidate_document_anchor_candidates` 中构建并通过参数传递，需要修改至少 3 个内部函数的签名。
- **为什么有问题**: 这不是"实施细节"——错误的 index 传递方式会导致性能问题或接口不一致。计划应该至少给出推荐的 index 类型和传递路径。
- **直接证据**: 当前代码中 `_resolve_section_id` 接受 `document` 和 `block` 两个参数，没有 section index 参数；`map_candidate_locator_to_anchor_candidate` 接受 `document, block, *, schema_family, parent_table`
- **影响**: 实施 Agent 可能选择次优设计，后续 review 才发现并返工
- **建议改法和验证点**: 在 Slice 2 增加一句：`SectionIndex` 作为冻结 dataclass 在 `map_candidate_document_anchor_candidates` 中构建一次，通过参数传递给内部函数（不修改公开 API 签名）；或在计划中声明"内部函数签名调整属于实施 Agent 的自由裁量范围"
- **修复风险**: 低
- **严重程度**: 低

## Architecture Boundary Review

- **Candidate / production isolation**: PASS。规则 #10 在所有 mapped 输出上显式保留 `candidate_only=True`, `source_truth_status="not_proven"`, `field_correctness_status="not_proven"`。Fail-closed stop rules 明确阻止任何会改变 proof status 或创建 production EvidenceAnchor 的操作。
- **Module ownership**: PASS。写集合严格限定在 `fund_agent/fund/documents/candidates/`。不触及 repository、parser、source policy、Service、Host、UI。
- **Dependency direction**: PASS。table/cell 传播不向上依赖 Service/Host/UI；不引入新的外部依赖。

## Overcoupling Review

- PASS。计划没有把 section normalization、page propagation、cell inheritance 捆绑成不可独立验证的整体。6 个 slice 可以独立实现和测试。
- 唯一轻微耦合：Slice 2（section index）和 Slice 3（propagation）共享 section index 数据结构，但这是合理的结构耦合，不是过度耦合。

## Overengineering Review

- PASS。计划没有引入不必要的抽象层、builder、factory 或 protocol。归一化是纯函数，index 是冻结数据结构，传播是简单的优先级规则。

## Best-practice Review

- PASS。计划遵循了项目 fail-closed 惯例、candidate-only 隔离、显式 blocked reason taxonomy。6 个 slice 粒度合理，每个可独立验证。

## Open Questions

| ID | Question | Why it matters | Suggested owner |
| --- | --- | --- | --- |
| OQ1 | 目录（TOC）中的章节标题如何与正文章节标题区分？如果无法程序化区分，TOC 污染 section index 导致的 yield 下降是否可接受？ | 影响 table/cell yield 改善的幅度（见 DS-F1） | Planning worker or controller |
| OQ2 | `8.3 报告期末按公允价值计量的金融资产` 等不在当前关键词族的子标题，实施中应直接 blocked 还是由 controller 在 re-evidence 后决定是否加别名？ | 影响 §8 内子标题的 yield（见 DS-F4） | Controller |
| OQ3 | 页面传播时，如果 block 的页面在 stable section span 的边界页上（如 section span 为 [60, 75)，block page=75），应归属于前一个 section 还是下一个 section？ | 边界情况下误归属的影响 | Planning worker |

## Residual Risks

| Risk | Severity | Tracking |
| --- | --- | --- |
| Numeric heading normalization may miss common variants not in closed patterns | 中 | DS-F3; resolve before implementation |
| TOC/目录 pollution of section index reduces yield | 中 | DS-F1; OQ1 |
| Keyword family aliases may be insufficient for real heading diversity | 低 | DS-F4; OQ2 |
| Test gaps for monotonic/cross-section blocked paths | 中 | DS-F5 |
| S1 full JSON regeneration path is deferred to separate gate — S1 complete mapping evidence remains blocked until that gate is dispositioned | 低 | Already acknowledged in plan Slice 6 and Residual Risks |

## Final Verdict

```text
VERDICT: PASS_WITH_FINDINGS_NOT_READY
```

The plan is structurally sound: it stays inside candidate-only boundaries, preserves fail-closed behavior, correctly defers S1 full JSON to a separate gate, and has a narrow exact write set. The 6 implementation slices are well-scoped and the re-evidence design correctly avoids source truth / field correctness / baseline promotion / readiness claims.

The 6 findings (2 medium residual risks carried forward from the plan's own Residual Risks section, 3 medium implementation specification gaps, 1 low) do not constitute structural blockers. They are addressable through plan amendments before the implementation gate, or through explicit controller acknowledgment that the risks are accepted. No finding reaches the severity threshold for FAIL_BLOCKED_NOT_READY.

Next recommended action: controller disposition of DS-F1 through DS-F6 and OQ1 through OQ3 before routing to the implementation gate.
