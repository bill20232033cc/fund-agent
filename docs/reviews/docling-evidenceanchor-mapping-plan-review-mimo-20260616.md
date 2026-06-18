# Docling EvidenceAnchor Mapping Plan Review - AgentMiMo

Date: 2026-06-16
Reviewer: AgentMiMo
Gate: `Docling EvidenceAnchor Mapping Plan Review Gate`
Review target: `docs/reviews/docling-evidenceanchor-mapping-plan-20260616.md`
Release/readiness: `NOT_READY`

## 1. Scope And Method

Adversarial review of the EvidenceAnchor mapping plan against:

- `AGENTS.md` rule truth source
- `docs/design.md` EvidenceAnchor / FundDisclosureDocument / Docling sections
- `docs/implementation-control.md` front current-control section
- `docs/current-startup-packet.md` current active gate and guardrails
- `docs/reviews/docling-full-document-coverage-evidence-controller-judgment-20260616.md` accepted coverage facts
- `docs/reviews/docling-full-document-coverage-evidence-20260616.md` S1 vs S4/S5/S6 schema distinction
- `reports/docling-full-document-coverage/20260616/coverage-summary.json` machine-readable coverage summary

Review lenses applied: architecture boundary, best-practice, overcoupling, overengineering.

## 2. Assumptions Tested

| # | Assumption | Test Result |
|---|-----------|-------------|
| A1 | Plan preserves EvidenceAnchor schema without drift | PASS - non-goals and field table are explicit |
| A2 | Plan prevents silent production `source_kind` expansion | PASS - §7.2 explicitly blocks new production kinds |
| A3 | Plan models table-cell anchors with parent table context | PASS - §6 composite locator rule is well-defined |
| A4 | Plan avoids fabricating fields when source data absent | PASS - §7.3/§7.4/§7.5/§10 stop conditions cover absent fields |
| A5 | Plan preserves Fund documents containment | PARTIAL - §2 non-goals state containment but §7 mapping rules do not specify implementation location |
| A6 | Plan preserves candidate-only / NOT_READY boundaries | PASS - §1/§2/§7.7/§9/§10 all enforce these |
| A7 | Plan is code-generation-ready for next gate | PARTIAL - mapping rules are detailed but parent-table resolution mechanism and testing strategy are underspecified |
| A8 | Next gate is narrow and handoff-ready | PASS - review-only next gate with clear scope |

## 3. Findings

### Findings Table

| ID | Severity | Status | Summary |
|----|----------|--------|---------|
| MIMO-F1 | Medium | accepted-candidate | Mapping implementation location not explicitly constrained to `fund_agent/fund/documents/` |
| MIMO-F2 | Medium | accepted-candidate | Parent-table resolution mechanism for cell blocks is underspecified |
| MIMO-F3 | Low | accepted-candidate | Section context "stable" vs "unstable" discrimination criteria not defined |
| MIMO-F4 | Low | deferred-candidate | `table:<ordinal>` row_locator semantics for table-level anchors not fully defined |
| MIMO-F5 | Low | deferred-candidate | No testing strategy specified for the mapping implementation |
| MIMO-F6 | Low | deferred-candidate | Paragraph block `row_locator` semantics left partially open |

### MIMO-F1 - [Medium] - Mapping implementation location not explicitly constrained to `fund_agent/fund/documents/`

- **位置**: §2 Non-goals, §7 Proposed Mapping Rules
- **问题类型**: 架构边界
- **当前写法**: §2 states "Do not change FundDocumentRepository" and "Do not use Docling Markdown/raw text/JSON directly as report facts; any future consumption must still pass through extractor/projection, EvidenceAnchor, and fail-closed classification." The mapping rules in §7 define WHAT to map but not WHERE in the codebase the mapping code must reside.
- **反例/失败场景**: Implementation worker places mapping code in `fund_agent/fund/extractors/` (extractor layer), `fund_agent/fund/template/` (renderer layer), or a new top-level module. This would leak Docling candidate internals into layers that should only consume structured data through established boundaries.
- **为什么有问题**: `AGENTS.md` hard constraint: "生产年报 PDF 访问必须经过 FundDocumentRepository" and "Service、UI、Host、renderer、quality gate 不得直接调用具体来源、PDF cache 或下载 helper." `docs/design.md` §6.1: "Docling 或其它文档中间层必须封装在 FundDocumentRepository / Fund documents 层内部。" Without an explicit implementation-location constraint, the next implementation gate could violate containment.
- **直接证据**: `AGENTS.md` lines on FundDocumentRepository boundary; `docs/design.md` §6.1 containment rule; plan §2 non-goals mention containment but §7 does not specify code location.
- **影响**: 实施 Agent 跑偏 / 架构边界违反 / Docling candidate internals 泄漏到 extractor/template/Service 层
- **建议改法和验证点**: Add to §2 non-goals or §7 preface: "All EvidenceAnchor mapping logic must reside within `fund_agent/fund/documents/` or a new subpackage under `fund_agent/fund/documents/candidates/`. Mapping code must not import into or be called directly from `extractors/`, `template/`, `analysis/`, `audit/`, `services/`, `host/`, `agent/`, or `ui/`." Verify: no import of mapping module outside `fund_agent/fund/documents/`.
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 中

### MIMO-F2 - [Medium] - Parent-table resolution mechanism for cell blocks is underspecified

- **位置**: §5.1 S1 Full Schema, §6 Parent-table Context Rule
- **问题类型**: 不可直接实施
- **当前写法**: §5.1 states "If a S1 cell has a cell locator but its parent table cannot be resolved, the mapping must stop for that cell." §6 states "A cell candidate cannot map to EvidenceAnchor without resolving its parent table." But the plan does not define HOW to resolve the parent table from a cell locator.
- **反例/失败场景**: S1 candidate JSON has cell-level `provenance_locator` objects. Implementation worker must determine whether parent table resolution means: (a) walking up a parent-pointer chain in the candidate JSON, (b) matching `table_id` field on the cell to a table in the same JSON, (c) using positional/heuristic matching by page and coordinates, or (d) some other mechanism. Without specifying the resolution path, the implementation worker may invent an ad-hoc heuristic that produces false parent-table matches or stops unnecessarily.
- **为什么有问题**: The plan's core value proposition is parent-table context for cell anchors. If the resolution mechanism is left to the implementation worker, different workers or iterations may resolve differently, producing inconsistent candidate anchors. The coverage evidence proves `table_id` exists on cells in S4/S5/S6 lightweight schema, but S1 uses `provenance_locator` objects where the parent-table link may be structural rather than field-based.
- **直接证据**: `coverage-summary.json` shows `cell_locator_pct: 100` for all samples but does not prove parent-table resolution is deterministic; plan §5.1/§6 define the requirement but not the mechanism.
- **影响**: 实施 Agent 需要重新设计 parent-table resolution / 生成不一致的 candidate anchors / cell mapping 因 resolution 不确定而全部 stop
- **建议改法和验证点**: Add a §6.1 subsection defining resolution: "For S1: parent table is resolved by walking the `provenance_locator` parent chain or matching the cell's table-level ancestor in the candidate JSON structure. For S4/S5/S6: parent table is resolved by matching `table_id` field on the cell to a table entry in the same candidate JSON. If the candidate JSON schema does not carry an explicit parent-table link for a cell, stop with `mapping_blocked: cannot_resolve_parent_table`." Verify: implementation can deterministically resolve or reject every cell in S1/S4/S5/S6 candidate JSONs.
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 中

### MIMO-F3 - [Low] - Section context "stable" vs "unstable" discrimination criteria not defined

- **位置**: §7.3 `section_id` priority order
- **问题类型**: 契约缺失
- **当前写法**: Priority 1 is "Use explicit candidate section id if it is present and stable." Priority 3 is "use normalized heading path only if the mapping can deterministically bind it to a section."
- **反例/失败场景**: Implementation worker encounters a candidate section id that is present but semantically ambiguous (e.g., a heading that could belong to multiple sections, or a section id that changes meaning across fund types). Without a "stability" criterion, the worker may accept unstable section ids or reject stable ones.
- **为什么有问题**: The stop condition "Else stop with mapping_blocked: missing_section_context" depends on correctly classifying section context as resolvable or not. Vague stability criteria produce inconsistent stop/continue decisions across samples.
- **直接证据**: Plan §7.3 priority order uses "stable" without definition; §10 stop condition "Section context cannot be deterministically resolved" relies on the same undefined stability.
- **影响**: 实施 Agent 不确定何时 stop vs continue / 不同样本的 section_id 映射不一致
- **建议改法和验证点**: Clarify: "A candidate section id is 'stable' if it matches a known annual-report section keyword family from the coverage evidence (§5 of coverage evidence), or if the heading path can be deterministically normalized to one of those families. Ambiguous or multi-match section ids are 'unstable' and trigger stop." Verify: implementation has a concrete section keyword family list to match against.
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

### MIMO-F4 - [Low] - `table:<ordinal>` row_locator semantics for table-level anchors not fully defined

- **位置**: §7.6 `row_locator` for Table block type
- **问题类型**: 契约缺失
- **当前写法**: "Leave unset for table-level anchor, or use `table` / `table:<ordinal>` only for table-level evidence where no row is claimed."
- **反例/失败场景**: Implementation worker uses `table:1` to mean "first table on the page" while another interpretation is "first table in the section." Without a defined ordinal basis, the same table could get different `row_locator` values depending on implementation.
- **为什么有问题**: `row_locator` is a stable field in EvidenceAnchor. Ambiguous ordinal semantics could produce non-deterministic candidate anchors that are hard to compare across runs.
- **直接证据**: Plan §7.6 table row_locator rule is loosely specified.
- **影响**: 低 - table-level anchors are less critical than cell-level; `row_locator` can be left unset for table-level as the primary rule
- **建议改法和验证点**: Recommend defaulting to `row_locator=null` for table-level anchors and deferring `table:<ordinal>` to a future schema gate. This simplifies the implementation surface.
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

### MIMO-F5 - [Low] - No testing strategy specified for the mapping implementation

- **位置**: §9 Future Evidence Gate Validation Matrix, §12 Next Gate
- **问题类型**: 测试缺口
- **当前写法**: §9 defines a validation matrix with scenarios and pass/stop conditions. §12 recommends the next gate as review-only, with the following gate being "No-live Implementation Planning Gate." No testing strategy is specified in the plan itself.
- **反例/失败场景**: Implementation planning gate defines mapping code without test specifications. Implementation agent writes mapping code that passes happy-path scenarios but fails on edge cases (cell without parent table, heading without section context, no-page candidate).
- **为什么有问题**: `AGENTS.md` requires "每完成一处代码修改，应同步编写/更新测试并优先验证通过." A code-generation-ready plan should specify what tests are needed, even if the implementation gate defines exact test cases.
- **直接证据**: Plan §9 validation matrix is a specification, not a test strategy; plan does not reference `AGENTS.md` testing requirements.
- **影响**: 实施 Agent 可能遗漏 edge case 测试 / 后续 review 发现测试缺口需要返工
- **建议改法和验证点**: Add to §9 or as §9.1: "Implementation gate must include no-live tests for: (1) happy-path cell mapping with resolved parent table for S1 and S4/S5/S6; (2) stop on cell without parent table; (3) stop on heading/paragraph without section context; (4) stop on no-page candidate; (5) correct source_kind handling (no new production kind); (6) note field contains required metadata. Single-file test coverage target >=80% per AGENTS.md."
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

### MIMO-F6 - [Low] - Paragraph block `row_locator` semantics left partially open

- **位置**: §7.6 `row_locator` for Paragraph block type
- **问题类型**: 契约缺失
- **当前写法**: "Leave unset unless a future schema gate accepts paragraph-specific row semantics. Preserve paragraph/block identity in `note`."
- **反例/失败场景**: Implementation worker is uncertain whether to always leave `row_locator` unset for paragraphs, or to set it when a paragraph has a block-level locator. The "unless a future schema gate" clause creates ambiguity about current behavior.
- **为什么有问题**: Minor ambiguity; the primary rule (leave unset) is clear, but the exception clause could distract implementation workers.
- **直接证据**: Plan §7.6 paragraph row_locator rule.
- **影响**: 低 - primary rule is clear; exception clause is future scope
- **建议改法和验证点**: Simplify to "Leave `row_locator` unset for paragraph blocks. Preserve paragraph/block identity in `note`." Remove the "unless a future schema gate" clause since it belongs in that future gate, not this plan.
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

## 4. Accepted / Rewritten / Rejected / Deferred Findings

| Finding | Disposition | Reason |
|---------|-------------|--------|
| MIMO-F1 | accepted-candidate | Architecture boundary constraint is missing; controller should bind implementation location before implementation gate |
| MIMO-F2 | accepted-candidate | Parent-table resolution is the plan's core mechanism; underspecification risks inconsistent implementation |
| MIMO-F3 | accepted-candidate | Section stability criterion is needed for deterministic stop/continue decisions |
| MIMO-F4 | deferred-candidate | Low impact; table-level anchors can default to `row_locator=null` |
| MIMO-F5 | deferred-candidate | Testing strategy belongs in implementation planning gate; can be raised there |
| MIMO-F6 | deferred-candidate | Minor wording simplification; does not block implementation |

## 5. Residuals

| Residual | Owner | Next Handling |
|----------|-------|---------------|
| MIMO-F1 binding: implementation location must be constrained to `fund_agent/fund/documents/` | Controller / implementation planning gate | Controller judgment on whether to bind in this gate or defer to implementation planning |
| MIMO-F2 binding: parent-table resolution mechanism must be specified per schema family | Controller / implementation planning gate | Controller judgment; coverage evidence JSON schema may already provide sufficient resolution hints |
| MIMO-F3 binding: section stability criterion should reference accepted section keyword families | Controller / implementation planning gate | Coverage evidence §5 section keyword list is the natural reference |
| EvidenceAnchor mapping from candidate locators remains open | documents/schema owner | `Docling EvidenceAnchor Mapping No-live Implementation Planning Gate` |
| Field-level correctness beyond selected facts remains unproven | baseline qualification owner | Comparative correctness gate |
| Production baseline disposition remains open | baseline qualification owner | Baseline disposition gate |
| Release/readiness remains `NOT_READY` | release owner | Future readiness gate only |

## 6. Reviewer Self-Check

- [x] Reviewed target, scope, source of truth and assumptions tested are written
- [x] Findings are evidence-based, adversarial, actionable, and not style/nit/speculation
- [x] Open questions, residual risks, tracking destination are separate from findings
- [x] Conclusion is `pass`, `pass-with-risks`, or `fail`
- [x] Output path uses fixed timestamp matching artifact path format

## 7. Final Recommendation

The plan is structurally sound. It correctly preserves EvidenceAnchor semantics, prevents silent schema expansion, models parent-table context for cell anchors, enforces stop conditions for absent fields, and maintains candidate-only / NOT_READY boundaries. The mapping rules in §7 are detailed enough for an implementation worker to begin work.

Three medium/low findings require controller judgment: implementation location binding (MIMO-F1), parent-table resolution mechanism (MIMO-F2), and section stability criteria (MIMO-F3). These are not plan failures but specification gaps that should be bound before or during the implementation planning gate.

```text
VERDICT: PASS_WITH_FINDINGS
```
