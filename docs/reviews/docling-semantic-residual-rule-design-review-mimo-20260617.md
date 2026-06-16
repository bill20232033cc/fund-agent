# Docling Semantic Residual Rule Design Review - AgentMiMo - 2026-06-17

Gate: `Docling Semantic Residual Rule Design Gate`
Role: review worker only, AgentMiMo
Verdict: `PASS_WITH_FINDINGS`

## Reviewed Target

- `docs/reviews/docling-semantic-residual-rule-design-20260617.md`

## Scope

Adversarial review of the semantic residual rule design artifact. Focus areas:

1. Does the design correctly cover all 7 residual rows?
2. Does it preserve NOT_READY and avoid source truth, baseline, parser replacement, full correctness, release readiness claims?
3. Does it keep annual-report access repository-mediated and avoid direct PDF/cache/source helper access?
4. Does it avoid closing by numeric or text equality alone?
5. Are proposed rule/reference-bundle changes minimal, fund-domain specific, and implementable in candidate internals?
6. Are S6-F041 benchmark and S6-F049/S6-F050 identical-value cases handled fail-closed?
7. Are later implementation slices and tests specific enough for a handoff-ready next gate?

## Source Of Truth And Evidence Read

- `AGENTS.md`
- `docs/reviews/docling-source-truth-residual-closure-evidence-controller-judgment-20260616.md`
- `reports/docling-baseline-support-source-truth-residual-closure/20260616/residual_closure_matrix.json`
- `fund_agent/fund/documents/candidates/source_truth_residual_closure.py`

## Validation Checks

### 1. Seven-row coverage

Design lists all 7 residual rows at lines 11-19:

- `F015` `sales_service_fee_C_current_year`
- `F020` `manager_holding_range_A`
- `S4-F015` `fixed_income_investment_amount`
- `S5-F032` `equity_investment_amount`
- `S6-F041` `benchmark`
- `S6-F049` `equity_investment_amount`
- `S6-F050` `stock_investment_amount`

Confirmed against residual closure matrix rows at JSON lines 215, 283, 499, 788, 1154, 1222, 1290. All 7 match. **PASS**.

### 2. NOT_READY preservation and claim avoidance

Non-goals at lines 21-31 explicitly state: no code implementation, no production parser replacement, no baseline promotion, no source-truth acceptance, no full field correctness claim, no release readiness, no PR readiness, no row closure by value equality alone, no weakening of no-live/candidate-only/repository-mediated/NOT_READY.

Completion report at lines 287-295 confirms: code implementation not performed, control docs not modified, commit/stage/push/PR not performed, release/readiness=NOT_READY. **PASS**.

### 3. Repository-mediated annual-report access

Line 33: "Production annual-report access must remain through `FundDocumentRepository`; any future reference-bundle construction must preserve `force_refresh=False`, blocked network socket guard in no-live validation, and candidate-only output status."

Reference Bundle Requirements lines 162-163: "Future reference-bundle enrichment should be candidate-only and repository-mediated. It should not read PDF/cache/source helper directly and should not call live acquisition."

Stop Conditions line 256: "Reference bundle construction would require live acquisition, direct PDF/cache/source-helper access, or non-repository access." **PASS**.

### 4. No closure by value equality alone

Rule 1 line 97: "if more than one same-source match satisfies all predicates, keep `semantic_equivalent_duplicate_residual` rather than closing."

Rule 3 lines 137-138: "equity_investment_amount: row hierarchy must prove aggregate `权益投资`; reject child stock rows... duplicated stock-only contexts."

Rule 4 line 156: "benchmark text must be associated with the benchmark label by row label, heading, or text-span context, not by nearby value equality or shared section alone."

Stop Conditions line 255: "Same value appears for aggregate and child portfolio fields and row hierarchy cannot distinguish them." **PASS**.

### 5. S6-F041 benchmark fail-closed

Rule 4 lines 153-158: investment-objective context must be rejected; benchmark text must be explicitly labeled `业绩比较基准`; residual preservation unless benchmark-labeled context is proven.

Residual Risks line 265: "S6-F041 must remain residual unless benchmark-labeled context is directly proven; investment-objective wording is not a benchmark field." **PASS**.

### 6. S6-F049/S6-F050 identical-value fail-closed

Rule 3 lines 137-138: equity aggregate rejects stock child rows; stock requires child-row context under equity investment.

Lines 146-148: both remain residual until row hierarchy proves distinct semantics.

Residual Risks line 264: "S6-F049 and S6-F050 are high-risk because identical normalized values can be valid for both aggregate equity and stock child rows in some index fund disclosures; they must not close without explicit row semantics." **PASS**.

### 7. Implementation slices handoff readiness

**PARTIAL**. See Finding 1 and Finding 2 below.

## Findings

### 01-未修复-中-参考包增强与现有数据模型不对齐

- **位置**: Reference Bundle Requirements (lines 162-172), Implementation Slice 1 (lines 183-188)
- **问题类型**: 不可直接实施
- **当前写法**: Design proposes 7 minimum additions to future reference-bundle construction: (1) table title/caption/preceding heading path, (2) multi-row/multi-column header hierarchy including share-class header bands, (3) row hierarchy including parent/child relation, (4) bounded nearby row labels, (5) table-family classification enum, (6) section text spans with context labels, (7) matched-reference diagnostics.
- **反例/失败场景**: The existing `RepositoryReferenceCell` dataclass (`source_truth_residual_closure.py:88-127`) has `table_context: tuple[str, ...]`, `row_label_path: tuple[str, ...]`, and `column_header_path: tuple[str, ...]` but does NOT have fields for `table_title`, `row_hierarchy` (parent/child encoding), or `table_family` (classification enum). An implementation agent receiving Slice 1 would need to: (a) add new fields to `RepositoryReferenceCell`, (b) update `RepositoryReferenceBundle.to_dict()` serialization, (c) update `_coerce_cell()` deserialization, (d) update `_match_satisfies_rule()` to use new fields, and (e) update the reference-bundle construction pipeline that feeds into this helper. The design does not map proposed additions to specific existing or new dataclass fields, nor does it specify the encoding for parent/child row hierarchy (nested path? separate field? tuple prefix?).
- **为什么有问题**: Slice 1 says "Add table title, heading path, row hierarchy, header hierarchy, table-family classification, and section text-span context labels to repository reference bundle construction" but the current helper's data model has no `table_title`, `row_hierarchy`, or `table_family` fields. The implementation agent must redesign the data model, not just extend it. This is a structural gap between design intent and code-generation readiness.
- **直接证据**: `source_truth_residual_closure.py:88-127` (`RepositoryReferenceCell` fields), `source_truth_residual_closure.py:162-190` (`RepositoryReferenceTextSpan` fields). Design lines 165-172 propose additions that have no corresponding fields.
- **影响**: 实施 Agent 必须重新设计数据模型，增加跨文件变更风险，可能引入不必要的耦合。
- **建议改法和验证点**: 在设计中明确每个 proposed addition 对应的 dataclass field name、type、encoding。例如: `table_title: str` on `RepositoryReferenceCell`, `parent_row_label: str | None` on `RepositoryReferenceCell`, `table_family: str | None` on `RepositoryReferenceCell` (enum-like). 验证点: 实施 agent 能仅凭设计文档确定需要新增哪些字段、修改哪些序列化/反序列化函数。
- **修复风险（低/中/高）**: 中
- **严重程度（低/中/高/严重）**: 中

### 02-未修复-中-表格族分类来源未指定

- **位置**: Reference Bundle Requirements item 5 (line 170)
- **问题类型**: 契约缺失
- **当前写法**: "Preserve table-family classification as candidate metadata, for example `expense_fee_table`, `manager_holding_table`, `portfolio_asset_composition_table`, `fair_value_hierarchy_table`, `financial_statement_table`, and `holding_detail_table`."
- **反例/失败场景**: The design gives example table-family labels but does not specify: (a) who computes the classification (repository layer? helper layer? a new classifier?), (b) what input signals drive the classification (table title? row labels? column headers? section ID?), (c) whether the classification is deterministic or heuristic, (d) how to handle tables that span multiple families (e.g., a table with both expense rows and holding rows). Without this contract, the implementation agent must invent the classification logic, which may not be consistent across samples or fund types.
- **为什么有问题**: `table_family` is central to Rule 3's portfolio disambiguation (lines 129-131: "matched reference must come from a fund asset portfolio / period-end portfolio composition table, not a fair-value hierarchy..."). If the classification is wrong, the rule either rejects valid matches or accepts invalid ones. The existing `table_context` field (`source_truth_residual_closure.py:107`) is a raw tuple of strings from the table's surrounding text, not a classification.
- **直接证据**: `source_truth_residual_closure.py:107` (`table_context: tuple[str, ...]` is raw context, not classification). Design line 170 proposes `table_family` as classification but does not specify construction logic.
- **影响**: 实施 Agent 必须自行设计分类逻辑，可能导致跨样本不一致或误分类。
- **建议改法和验证点**: 指定 `table_family` 的构造契约: 输入信号（table title + section ID + row label patterns）、确定性规则（if table title contains X then family=Y）、fallback（unknown when insufficient signals）。验证点: 给定已知 table title/section/row label 组合，分类结果可预测且可测试。
- **修复风险（低/中/高）**: 中
- **严重程度（低/中/高/严重）**: 中

### 03-未修复-低-行层次编码方式未指定

- **位置**: Rule 3 field-specific acceptance (lines 136-138), Reference Bundle Requirements item 3 (line 168)
- **问题类型**: 契约缺失
- **当前写法**: "row hierarchy must prove `固定收益投资`" / "row hierarchy must prove aggregate `权益投资`" / "row hierarchy must prove `其中：股票` or equivalent stock child row under equity investment" / "Preserve row hierarchy, including parent row and child row relation for rows such as `权益投资 -> 其中：股票`."
- **反例/失败场景**: The existing `RepositoryReferenceCell.row_label_path` (`source_truth_residual_closure.py:106`) is `tuple[str, ...]`. The current `_match_satisfies_rule` function (`source_truth_residual_closure.py:740`) uses `_contains_any(row_labels, rule.required_row_label_any)` which is a flat substring match on the joined label path. This works for simple cases but cannot distinguish "权益投资" as a parent row from "权益投资" appearing as a label in a completely different context. The design proposes "parent row and child row relation" but does not specify whether this should be encoded as: (a) a nested path in `row_label_path` like `["权益投资", "其中：股票"]`, (b) a separate `parent_row_label: str | None` field, (c) a `row_hierarchy_path: tuple[str, ...]` field distinct from `row_label_path`. Without this, the implementation agent must guess the encoding.
- **为什么有问题**: The existing `_match_satisfies_rule` uses flat substring matching. If row hierarchy is encoded as a new field, the matching logic must change. If it's encoded as an extension of `row_label_path`, existing tests may break. The design should specify the encoding to avoid implementation ambiguity.
- **直接证据**: `source_truth_residual_closure.py:106` (`row_label_path` type), `source_truth_residual_closure.py:740` (`_contains_any` flat match).
- **影响**: 实施 Agent 可能选择不兼容的编码方式，导致规则匹配行为与设计意图不一致。
- **建议改法和验证点**: 指定 row hierarchy 编码方式。例如: `row_label_path` 保持为当前行的标签路径，新增 `parent_row_label: str | None` 字段用于父行标签。`_match_satisfies_rule` 增加 parent row 检查。验证点: "权益投资" 作为父行 vs 作为独立行标签时，匹配行为可区分。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

### 04-未修复-低-部分参考包增强成功时的行为未明确

- **位置**: Stop Conditions (lines 248-257)
- **问题类型**: 状态机漏洞
- **当前写法**: Stop conditions list 8 cases where `semantic_assignment_residual` must be kept. These are all "if X is missing, keep residual" rules.
- **反例/失败场景**: What happens when reference-bundle enrichment is partially successful? For example, if `table_title` is available for a cell but `row_hierarchy` (parent/child) is not, and the field-specific predicate requires both. The existing helper's behavior (lines 610-618 in `source_truth_residual_closure.py`) keeps residual when `_evaluate_semantics` returns `semantic_rule_rejected` or `semantic_rule_unresolved`, which is the correct fail-closed behavior. But the design's stop conditions are stated as absolute rules ("if X is missing") without addressing the partial-success case. This is technically implied by the existing helper logic but should be explicitly stated for the enriched model.
- **为什么有问题**: An implementation agent might interpret the stop conditions as requiring ALL enriched context to be present before any closure attempt, which would be overly conservative and could prevent closing rows that have sufficient context through other means.
- **直接证据**: `source_truth_residual_closure.py:610-618` (existing fail-closed logic), design lines 248-257 (stop conditions).
- **影响**: Implementation agent 可能过度保守，拒绝所有部分增强的引用包，导致本可闭合的行保持 residual。
- **建议改法和验证点**: 在 stop conditions 中增加一条: "If reference-bundle enrichment is partial (some enriched fields present, others missing), apply field-specific predicates only to available enriched fields; missing enriched fields cause the corresponding predicate dimension to fail-closed (keep residual)." 验证点: 给定部分增强的引用包，字段级谓词仅对可用字段求值，缺失字段导致 residual。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

## Open Questions

None. All design questions that could block implementation have been captured as findings.

## Residual Risks

1. **Repository parsed tables may not preserve enough merged-cell header hierarchy or parent/child row hierarchy for all samples** (design line 262). This is a known limitation of the current reference-bundle construction pipeline. The design correctly identifies this risk. Tracking: next implementation gate.

2. **F015 may remain residual even after context enrichment** if multiple semantically equivalent C-share current-period sales service fee rows remain (design line 263). This is acceptable because the design explicitly allows `semantic_equivalent_duplicate_residual` for this case. Tracking: next evidence gate.

3. **S6-F049 and S6-F050 identical-value risk** (design line 264). The design correctly identifies that identical normalized values can be valid for both aggregate equity and stock child rows in some index fund disclosures. The fail-closed design (keep residual until row hierarchy proves distinct semantics) is the correct approach. Tracking: next evidence gate.

4. **S6-F041 benchmark-labeled context availability** (design line 265). The design correctly requires explicit benchmark labeling and rejects investment-objective text. Whether the repository parsed tables actually contain benchmark-labeled context for S6 is an implementation-time discovery. Tracking: next evidence gate.

5. **Reference-bundle construction pipeline changes** (design lines 183-188). Slice 1 requires changes to the reference-bundle construction pipeline that feeds into the helper, not just the helper itself. The design does not identify which upstream code constructs `RepositoryReferenceCell` instances. Tracking: next implementation gate.

## Conclusion

Verdict: **PASS_WITH_FINDINGS**

The design correctly covers all 7 residual rows, preserves NOT_READY, avoids all prohibited claims, keeps annual-report access repository-mediated, avoids closing by value equality alone, and handles S6-F041 and S6-F049/S6-F050 fail-closed. The proposed rules are minimal and fund-domain specific.

4 findings identified:

- **Finding 01 (中)**: Reference-bundle enrichment requirements are not mapped to existing dataclass fields. Implementation slices are not code-generation-ready without specifying new field names, types, and encodings.
- **Finding 02 (中)**: Table-family classification source and construction logic are not specified. Risk of inconsistent classification across samples.
- **Finding 03 (低)**: Row hierarchy encoding method is not specified. Existing flat `row_label_path` may not support parent/child predicates without redesign.
- **Finding 04 (低)**: Partial reference-bundle enrichment success behavior is implied but not explicitly stated.

Findings 01 and 02 are material for handoff-readiness: an implementation agent would need to make design decisions that should be captured in this artifact. Findings 03 and 04 are lower severity but should be addressed before the next gate.

The design is safe to proceed to implementation planning with the expectation that findings 01 and 02 are resolved in the implementation slice specification.
