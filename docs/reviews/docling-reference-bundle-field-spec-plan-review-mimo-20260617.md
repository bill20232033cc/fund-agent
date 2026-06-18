# Docling Reference Bundle Field-spec Plan Review — AgentMiMo — 2026-06-17

Gate: `Docling Reference Bundle Field-spec Planning Gate`
Role: review worker only, AgentMiMo
Verdict: `PASS_WITH_FINDINGS`

## Reviewed Target

- `docs/reviews/docling-reference-bundle-field-spec-plan-20260617.md`

## Scope

Adversarial review of the field-spec plan artifact. Focus areas:

1. Is the plan code-generation-ready enough for implementation worker, especially dataclass fields, type/defaults, to_dict/coercion, table-family classifier, row hierarchy, share/period context, benchmark text-span context, partial enrichment behavior?
2. Does it preserve NOT_READY, candidate-only, no source truth, no baseline promotion, no parser replacement, no full field correctness, no readiness/release/PR?
3. Does it keep annual-report access repository-mediated via FundDocumentRepository and avoid direct PDF/cache/source-helper/live/provider/LLM/analyze/checklist/golden commands?
4. Does it avoid closing rows by value equality alone?
5. Does it keep S6-F041 fail-closed unless benchmark-labeled context is proven?
6. Does it keep S6-F049/S6-F050 fail-closed unless row hierarchy distinguishes equity aggregate vs stock child semantics?
7. Does it introduce overdesign or implementation ambiguity that should block the next implementation gate?

## Source Of Truth And Evidence Read

- `AGENTS.md`
- `docs/design.md`
- `docs/implementation-control.md`
- `docs/reviews/docling-semantic-residual-rule-design-controller-judgment-20260617.md`
- `docs/reviews/docling-semantic-residual-rule-design-20260617.md`
- `docs/reviews/docling-semantic-residual-rule-design-review-ds-20260617.md`
- `docs/reviews/docling-semantic-residual-rule-design-review-mimo-20260617.md`
- `fund_agent/fund/documents/candidates/source_truth_residual_closure.py`
- `tests/fund/documents/test_docling_source_truth_residual_closure.py`

## Validation Checks

### 1. Code-generation readiness

**Dataclass fields**: Plan specifies exact field names, types, defaults, and serialization/coercion for `RepositoryReferenceCell` (11 new fields), `RepositoryReferenceTextSpan` (2 new fields), `RepositoryReferenceBundle` (3 new fields), and `ResidualClosureRule` (9 new fields). Literal type aliases are defined. **PASS**.

**to_dict/coercion**: Plan specifies `to_dict()` must emit all new fields with defaults, tuple fields serialize as JSON lists, literal fields serialize as strings. `_coerce_cell()` accepts legacy payloads with missing fields defaulting to `()` / `"unknown"`. **PASS**.

**Table-family classifier**: Plan specifies deterministic classification rules with priority-ordered input signals, allowed labels, precedence rules (fair_value_hierarchy overrides portfolio), and unknown/failure behavior. **PASS**.

**Row hierarchy**: Plan specifies `row_parent_label_path`, `row_hierarchy_path`, `row_hierarchy_role` fields, proof requirements, and predicate behavior. **PASS**.

**Share/period context**: Plan specifies `ShareClassContext`, `ShareClassContextSource`, `PeriodContext`, `PeriodContextSource` with canonical variants and allowed proof sources. **PASS**.

**Benchmark text-span context**: Plan specifies `TextSemanticContext` with `benchmark` / `investment_objective` disambiguation and explicit acceptance predicate. **PASS**.

**Partial enrichment behavior**: Plan specifies missing enriched context fails closed for the relevant predicate dimension, `enrichment_status` is evidence/status only, and a bundle needs only the fields required by that row's rule. **PASS**.

### 2. NOT_READY preservation and claim avoidance

Plan section "Non-goals" (lines 472-487) explicitly lists: no code implementation, no source truth, no baseline promotion, no parser replacement, no full field correctness, no release readiness, no PR readiness, no live/network commands. Status header says `HANDOFF_READY_NOT_READY`. **PASS**.

### 3. Repository-mediated annual-report access

Plan lines 17-19: "no direct PDF/cache/source-helper access, no live/source acquisition/provider/LLM/analyze/checklist/golden/readiness/release commands". Stop conditions line 469: "reference-bundle enrichment would require live acquisition, direct PDF/cache/source-helper access, or non-repository access". **PASS**.

### 4. No closure by value equality alone

Plan line 245: "Value equality, expected field name, row order alone, or nearby duplicate text alone must not prove hierarchy." Line 468: "closure would rely on value equality, expected field name, row order alone, or nearby context alone". Per-residual table for S6-F049/S6-F050 explicitly says "Do not close by value equality." **PASS**.

### 5. S6-F041 fail-closed

Plan lines 317-332: benchmark acceptance requires `semantic_context_label == "benchmark"` or explicit `业绩比较基准` label; investment-objective context is rejected. Line 332: "S6-F041 remains RESIDUAL unless benchmark-labeled context is proven." **PASS**.

### 6. S6-F049/S6-F050 fail-closed

Plan lines 250-251: "If equity_investment_amount and stock_investment_amount share the same normalized value in the same table, both may close only if their matched references have distinct row_index or distinct proven row_hierarchy_path, and the field-specific hierarchy predicates are fully satisfied." Line 252: "keep S6-F049 and S6-F050 as RESIDUAL." **PASS**.

### 7. Implementation ambiguity and overdesign

**PARTIAL**. See Findings below.

## Findings

### 01-未修复-中-`ResidualClosureRule` 序列化/反序列化契约未指定

- **位置**: Field Spec with dataclass-level changes — `ResidualClosureRule` additions (lines 163-174)
- **问题类型**: 契约缺失
- **当前写法**: Plan specifies 9 new fields on `ResidualClosureRule` with types, defaults, and consumption semantics, but does not specify: (a) whether `ResidualClosureRule` needs a `to_dict()` method or serialization contract; (b) whether `_coerce_rule()` or equivalent deserialization helper is needed for `FIELD_RULES` loaded from JSON; (c) how new `Literal` type fields on the rule serialize/deserialize.
- **反例/失败场景**: Current `ResidualClosureRule` is defined as a frozen dataclass (`source_truth_residual_closure.py:61-86`) with no `to_dict()` and no coercion helper — it is constructed directly in Python via `FIELD_RULES` dict (lines 419-493). If `FIELD_RULES` must remain Python-only, serialization may not be needed. But if rules are ever loaded from config/JSON (which the new Literal types suggest), a coercion contract is needed. The implementation agent must decide: keep rules as Python-only constants, or add serialization/deserialization.
- **为什么有问题**: `allowed_table_families: tuple[TableFamily, ...]` and `rejected_table_families: tuple[TableFamily, ...]` are new typed tuple fields. Without a serialization contract, the implementation agent may leave `to_dict()` inconsistent across dataclasses, or may skip coercion for rules entirely, creating an asymmetric model.
- **建议改法和验证点**: Clarify whether `FIELD_RULES` remain Python-only constants (no serialization needed) or should support JSON loading (coercion needed). If Python-only, state "ResidualClosureRule serialization is not required in this slice; rules are Python constants." If JSON-loadable, add `to_dict()` and `_coerce_rule()` specs. 验证点: 实施 agent 能确定是否需要为 `ResidualClosureRule` 添加序列化。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 中

### 02-未修复-中-`_coerce_bundle()` 如何导出 `enrichment_status` 未指定

- **位置**: Serialization and Coercion Contract (lines 334-370), RepositoryReferenceBundle additions (lines 155-159)
- **问题类型**: 契约缺失
- **当前写法**: Plan says `enrichment_status` defaults to `"not_enriched"` and missing/invalid input becomes `"not_enriched"`. Plan also says `_coerce_cell()` may derive `table_family` from available fields if missing. But `_coerce_bundle()` behavior for `enrichment_status` is not specified: should it remain `"not_enriched"` for legacy payloads, or should it be derived from cell-level enrichment?
- **反例/失败场景**: A legacy bundle payload has no `enrichment_status` field. `_coerce_bundle()` deserializes it. Should `enrichment_status` always be `"not_enriched"` for legacy payloads? Or should it be `"partially_enriched"` if some cells have new fields like `table_family`? Without this contract, the implementation agent may leave `enrichment_status` as always `"not_enriched"` for legacy payloads regardless of cell state, or may try to derive it inconsistently.
- **为什么有问题**: `enrichment_status` is declared as "evidence/status only" and "not a pass condition." But its derivation logic must be consistent to avoid misleading downstream consumers. If the plan intends it to always default to `"not_enriched"` for legacy payloads (and only set to `"partially_enriched"` or `"enriched"` by the upstream construction pipeline), that should be stated explicitly.
- **建议改法和验证点**: Add one line to the coercion contract: "For legacy bundle payloads without `enrichment_status`, set to `"not_enriched"`; do not derive from cell-level fields." 验证点: legacy payload coercion is deterministic.
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 中

### 03-未修复-低-表族分类同优先级信号冲突解决未完全指定

- **位置**: Table-family Classification Spec (lines 178-229)
- **问题类型**: 契约缺失
- **当前写法**: Plan specifies priority-ordered input signals and per-family rules with precedence notes (e.g., fair_value_hierarchy overrides portfolio). However, for the `portfolio_asset_composition_table` family, the rule says "lower priority than fair_value_hierarchy_table when fair-value hierarchy terms are present" but does not specify what happens when both `portfolio_asset_composition_table` and `financial_statement_table` signals match at the same priority level (e.g., a §8 table with both "基金资产组合" in title and "资产负债表" in context).
- **反例/失败场景**: A table in §8 has title "基金资产组合" and context contains "资产负债表". Both `portfolio_asset_composition_table` and `financial_statement_table` could match. The plan does not specify which takes precedence when signals conflict at the same priority level. The `financial_statement_table` rule says "must not satisfy portfolio amount fields", but this is a consumption-side rejection, not a classification-side precedence.
- **为什么有问题**: The classifier is deterministic only if all conflict cases have explicit precedence. In practice, this case is unlikely for the 7 target rows, but the implementation agent needs a deterministic rule.
- **建议改法和验证点**: Add a general precedence rule: "When signals conflict, prefer the more specific family (e.g., `portfolio_asset_composition_table` over `financial_statement_table` if portfolio row labels are present); if still ambiguous, set `unknown`." 验证点: conflicting signals produce deterministic classification.
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

### 04-未修复-低-`_has_share_class_context` 检查范围扩展未在 Slice 2 中显式标注

- **位置**: Implementation Slices — Slice 2 (lines 396-407)
- **问题类型**: 契约缺失
- **当前写法**: Slice 2 says "Extend `_match_satisfies_rule()` to evaluate... canonical share-class context and allowed sources." The field spec adds `share_class_context` and `share_class_context_source` to `RepositoryReferenceCell`, and `allowed_share_class_context_sources` to `ResidualClosureRule`. But Slice 2 does not explicitly state that `_has_share_class_context()` (currently at `source_truth_residual_closure.py:1267-1295`, checking only `column_headers`) must be replaced or extended to also check `row_label_path`, `table_context`, and `column_header_band_path`.
- **反例/失败场景**: The current `_has_share_class_context` only checks `column_headers` values. If the implementation agent adds `share_class_context` as a pre-computed field on `RepositoryReferenceCell` (which the field spec implies), the old `_has_share_class_context` function may still be called in `_match_satisfies_rule()` instead of checking the new field. The agent needs to know: replace `_has_share_class_context` with a check on `cell.share_class_context`, or extend it.
- **为什么有问题**: This is the same issue identified in DS-04 of the previous design review. The plan resolves it at the data-model level (adding `share_class_context` field) but does not explicitly describe the implementation path in Slice 2.
- **建议改法和验证点**: In Slice 2, add: "Replace `_has_share_class_context()` column-header-only check with `cell.share_class_context` field check; `_has_share_class_context` may be retained as an internal derivation helper for the `share_class_context` field construction." 验证点: share-class proof comes from `cell.share_class_context`, not only `column_header_path`.
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

### 05-未修复-低-现有测试 `_cell()` fixture 构造未说明新字段默认路径

- **位置**: Tests and Validation Commands (lines 426-441)
- **问题类型**: 实施歧义
- **当前写法**: Plan says "legacy payloads deserialize with missing enriched fields set to unknown/defaults" and "legacy bundles may keep existing already-proven simple closures." The test validation list includes "serialization emits all new fields with defaults" and "legacy payloads deserialize with missing enriched fields."
- **反例/失败场景**: The existing test `_cell()` fixture (`test_docling_source_truth_residual_closure.py:106-150`) constructs `RepositoryReferenceCell` directly without new fields. After Slice 1 adds new fields with defaults, existing tests should still pass because defaults are applied. But the plan does not explicitly state whether existing test fixtures need updating or should be left unchanged to verify backward compatibility.
- **为什么有问题**: This is a minor implementation detail, but explicitly stating "existing `_cell()` and `_bundle()` test fixtures should pass unchanged after Slice 1; new test functions should construct cells with enriched fields" would remove ambiguity.
- **建议改法和验证点**: In test validation section, add: "Existing `_cell()` / `_bundle()` fixtures should pass unchanged after Slice 1 (backward compatibility proof); new test functions should use enriched constructors." 验证点: `uv run pytest tests/fund/documents/test_docling_source_truth_residual_closure.py` passes unchanged after Slice 1.
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

## Open Questions

None. All design questions that could block implementation have been captured as findings.

## Residual Risks

1. **Repository parsed tables may not preserve enough merged-cell header hierarchy or parent/child row hierarchy for all samples** (plan residual risks section). This is a known upstream limitation. The plan correctly identifies it. Tracking: next implementation gate.

2. **F015 may remain residual even after enrichment** if multiple semantically equivalent C-share current-period sales service fee rows remain. The plan explicitly allows `semantic_equivalent_duplicate_residual`. Tracking: next evidence gate.

3. **S6-F049 and S6-F050 identical-value risk**. The plan correctly requires distinct `row_index` or proven `row_hierarchy_path`. If the upstream reference bundle cannot prove hierarchy, both remain residual. Tracking: next evidence gate.

4. **S6-F041 benchmark-labeled context availability**. Whether repository parsed tables actually contain benchmark-labeled context for S6 is an implementation-time discovery. Tracking: next evidence gate.

5. **Table-family classifier accuracy across fund types**. The classifier is deterministic but may produce `unknown` for non-standard table layouts. The plan correctly fails closed for `unknown`. Tracking: next evidence gate.

## Validation Checks Summary

| Check | Result |
|-------|--------|
| Plan covers all 7 residual rows with per-row expected behavior | **PASS** |
| Plan preserves NOT_READY and all guard flags | **PASS** |
| Plan keeps annual-report access repository-mediated | **PASS** |
| Plan avoids closing by value equality alone | **PASS** |
| Plan keeps S6-F041 fail-closed unless benchmark-labeled | **PASS** |
| Plan keeps S6-F049/S6-F050 fail-closed unless row hierarchy proves distinct semantics | **PASS** |
| Plan resolves all 6 binding controller amendments | **PASS** |
| Plan is code-generation-ready for implementation worker | **PASS with findings** — findings 01-02 are material for implementation agent decisions |
| Plan avoids overdesign | **PASS** — changes are minimal and targeted to the 7 residual rows |

## Conclusion

Verdict: **PASS_WITH_FINDINGS**

The plan correctly covers all 7 residual rows, resolves all 6 binding controller amendments (dataclass fields, table-family classification, row hierarchy, share/period context, diagnostic scope, partial enrichment), preserves all hard constraints (NOT_READY, candidate-only, repository-mediated, fail-closed), and provides sufficient detail for code generation.

5 findings identified:

- **Finding 01 (中)**: `ResidualClosureRule` serialization/deserialization contract not specified. Implementation agent must decide whether rules remain Python-only constants or need JSON loading support.
- **Finding 02 (中)**: `_coerce_bundle()` derivation of `enrichment_status` for legacy payloads not specified. Should explicitly default to `"not_enriched"` without cell-level derivation.
- **Finding 03 (低)**: Table-family classifier same-priority signal conflict resolution not fully specified. General precedence rule needed.
- **Finding 04 (低)**: `_has_share_class_context` replacement path not explicitly described in Slice 2.
- **Finding 05 (低)**: Existing test fixture backward-compatibility path not explicitly stated.

Findings 01 and 02 are material for implementation agent decisions but do not block the gate. Findings 03-05 are low severity and can be resolved during implementation.

The plan is safe to proceed to implementation with the expectation that findings 01 and 02 are resolved by the implementation agent before completing Slice 1.
