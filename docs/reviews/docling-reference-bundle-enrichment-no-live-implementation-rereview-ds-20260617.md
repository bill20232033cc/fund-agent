# Docling Reference Bundle Enrichment No-live Implementation Re-review (AgentDS) — 2026-06-17

Gate: `Docling Reference Bundle Enrichment No-live Implementation Gate`
Role: AgentDS re-review worker only
Verdict: `PASS`
Release/readiness: `NOT_READY`

## Reviewed Fix

Fix evidence: `docs/reviews/docling-reference-bundle-enrichment-no-live-implementation-fix-evidence-20260617.md`

Changed files:
- `fund_agent/fund/documents/candidates/source_truth_residual_closure.py`
- `tests/fund/documents/test_docling_source_truth_residual_closure.py`
- `docs/reviews/docling-reference-bundle-enrichment-no-live-implementation-fix-evidence-20260617.md`

Prior review: `docs/reviews/docling-reference-bundle-enrichment-no-live-implementation-code-review-ds-20260617.md`

## Prior Finding Disposition

| Finding | Severity | Status | Evidence |
|---|---|---|---|
| F-DS-1: enrichment 未接入 close_source_truth_residuals | Low | **FIXED** | `source_truth_residual_closure.py:742–745` — `_enrich_reference_bundle_contexts` 现在在 coercion 后立即对每个 bundle 调用。v1 legacy bundle 会被自动 enrichment；v2 bundle 跳过（设计选择：v2 视为已富化）。`test_raw_legacy_bundle_entrypoint_enriches_before_closure_and_still_rejects_prior` 验证 v1 路径。 |
| F-DS-2: _cell_has_required_text_semantic_context 仅处理 benchmark | Low | NOT FIXED | 未在本次 fix 范围内。当前无规则使用其他 TextSemanticContext，无功能影响。可接受。 |
| F-DS-3: _period_context_from_text 复合标签边界 | Low | NOT FIXED | 未在本次 fix 范围内。仍属于理论边界情况，当前规则不会被误闭合。可接受。 |
| F-DS-4: _enrich_reference_bundle_contexts 缺少集成测试 | Info | PARTIALLY ADDRESSED | 新测试覆盖 v1 enrichment 端到端路径（raw dict → coercion → enrichment → closure），但未显式测试 table_family 广播到同表多 cell。间接覆盖充分。 |
| F-DS-5: 测试命名不够精确 | Info | NOT FIXED | 未在本次 fix 范围内，断言正确。可接受。 |

### F-DS-1 Fix Detail

`close_source_truth_residuals` 新增 enrichment 调用（line 742–745）：

```python
bundles = {
    key: _enrich_reference_bundle_contexts(bundle)
    for key, bundle in bundles.items()
}
```

`_enrich_reference_bundle_contexts` 函数签名和 docstring 已更新（line 1904–1917），明确语义：

> legacy/raw bundle 返回带派生 cell context 的引用 bundle；v2 bundle 原样返回。

**Enrichment 版本守卫**（line 1919–1920）：

```python
if bundle.reference_bundle_schema_version != _LEGACY_REFERENCE_BUNDLE_SCHEMA_VERSION:
    return bundle
```

该守卫是一个合理的设计选择：
- v1（legacy）bundle：缺少 enrichment 字段 → 自动派生 table_family / share_class / period
- v2 bundle：假定上游已富化 → 原样返回，不覆盖上游决策
- 如果 v2 bundle 的 enrichment 字段是非法值（如 via `_coerce_literal` → `"unknown"`），不会通过 enrichment 修复——这是故意的 fail-closed 行为：v2 bundle 携带的 enrichment 数据质量应由上游保证

**v1/v2 行为验证**（运行时确认）：
- v2 bundle → enrichment 返回同一对象（`cells same object? True`），`table_family="unknown"`
- v1 bundle → enrichment 派生：`table_family="expense_fee_table"`, `share_class_context="C"`, `period_context="current_period"`

测试 `test_invalid_literals_become_unknown_and_fail_target_predicates` 使用 v2 bundle（来自 `_bundle().to_dict()`），因此 enrichment 跳过，非法 literal 保持 `"unknown"`，结果保持 `semantic_assignment_residual`——行为正确且一致。

测试 `test_raw_legacy_bundle_entrypoint_enriches_before_closure_and_still_rejects_prior` 使用无 schema version 的 raw dict（→ 强制 v1），enrichment 生效，C类/本期闭合成功，C类/上年度保持 residual——行为正确且一致。

### F-DS-1 Additional Fix: reference_generation_status Literal Coercion

`_coerce_bundle` 中原先的 `str(value.get("reference_generation_status", "available"))` 已替换为（line 1179–1183）：

```python
reference_generation_status=_coerce_literal(
    value.get("reference_generation_status"),
    _REFERENCE_GENERATION_STATUS_VALUES,
    "available",
),
```

新增 `_REFERENCE_GENERATION_STATUS_VALUES` 验证元组（line 164–167）：

```python
_REFERENCE_GENERATION_STATUS_VALUES: tuple[ReferenceGenerationStatus, ...] = (
    "available",
    "blocked_reference_unavailable",
)
```

测试 `test_reference_generation_status_coerces_invalid_to_available_but_preserves_blocked` 覆盖三种情况：

| 输入 | 强制结果 | closure 结果 |
|---|---|---|
| `None`（key 被 pop） | `"available"` | `disambiguated_source_body_match` |
| `"typo"` | `"available"` | `disambiguated_source_body_match` |
| `"blocked_reference_unavailable"` | `"blocked_reference_unavailable"` | `blocked_reference_unavailable` |

修复前的行为：`"typo"` 会通过 `str()` 直接保留为 `"typo"`，在 `_close_row` 中 `"typo" != "available"` → 误阻断。修复后非法值回退为 `"available"`，合法字面量 `"blocked_reference_unavailable"` 保留。✓

## New Tests Validation

```text
uv run pytest tests/fund/documents/test_docling_source_truth_residual_closure.py -v
```

Result: **60 passed in 0.75s**（56 original + 4 new parametrized variants）

```text
git diff --check -- fund_agent/fund/documents/candidates/source_truth_residual_closure.py tests/fund/documents/test_docling_source_truth_residual_closure.py
```

Result: whitespace clean.

## New Findings

### F-DS-R1 (Info) — Fix evidence 未记录 enrichment v1-only 守卫的设计决策

**Issue**: Fix evidence 文档只写 "Raw legacy bundles are enriched in memory before closure"，未说明 v2 bundle 被跳过。v1-only 守卫是关键的 behavioral contract，其设计理由（v2 假定已富化，不应被覆盖）应在 evidence 中明确记录，以便后续 gate 理解行为边界。

**Severity**: Info — 不影响正确性，代码中 docstring 已说明。属于文档完备性建议。

## Boundary Verification

- [x] `NOT_READY` preserved
- [x] candidate-only preserved
- [x] No source truth acceptance
- [x] No baseline promotion
- [x] No parser replacement
- [x] No full field correctness claim
- [x] No readiness/release/PR
- [x] Pure-helper boundary: no `open()`, no `FundDocumentRepository`, no source helper
- [x] No live/network/source acquisition
- [x] No Service/UI/Host/renderer/quality-gate changes
- [x] All prior test assertions still pass (no regression)
- [x] All new test assertions are correct

## Residual Risks

1. v2 bundle 携带非法 enrichment 字面量时不会被 enrichment 修复——这是 fail-closed 设计，正确但需要上游保证数据质量。
2. `_period_context_from_text` 和 `_cell_has_required_text_semantic_context` 的已知边界仍未处理（见 F-DS-2, F-DS-3），属于后续 gate 范围。
3. All validation remains fixture-based, no-live.

## Self-Check

pass — re-review stayed within AgentDS scope. No files edited/committed/pushed. Fixes are exactly scoped to the two accepted non-blocking findings. No regression, no new blocking issues. enrichment v1-only guard is a sound design choice. 60/60 tests pass, whitespace clean. Verdict: PASS.
