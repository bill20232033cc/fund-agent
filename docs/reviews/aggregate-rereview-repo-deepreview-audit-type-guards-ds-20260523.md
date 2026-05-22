# Aggregate Re-Review — repo-deepreview-audit-type-guards

## Scope

- Mode: aggregate re-review of accepted finding fix
- Branch: `fix/repo-deepreview-audit-type-guards`
- Source aggregate review: `docs/reviews/aggregate-deepreview-repo-deepreview-audit-type-guards-ds-20260523.md`
- Fix artifact: `docs/reviews/aggregate-fix-repo-deepreview-audit-type-guards-20260523.md`
- Output file: `docs/reviews/aggregate-rereview-repo-deepreview-audit-type-guards-ds-20260523.md`

## Previous Aggregate Finding Status

### 1-已修复-低-`validate_programmatic_contract_rules` 重复加载 coverage manifest 引入冗余校验

- **Fix 状态**: 已修复 ✓
- **代码变更**（`fund_agent/fund/audit/contract_rules.py`）：
  1. **新增 `_build_contract_audit_coverage_manifest()`**（第 488-504 行）：纯构造 helper，返回未校验的 manifest，替代此前 `load_contract_audit_coverage_manifest` 中内联的构造+校验
  2. **`load_contract_audit_coverage_manifest()` 重构**（第 483-485 行）：`_build` then `validate`，公开行为不变
  3. **`load_programmatic_contract_rules()` 移除冗余调用**（删除原第 506 行 `load_contract_audit_coverage_manifest()`）：不再以默认 `_FORBIDDEN_CONTENT_RULES` 重复校验
  4. **`validate_programmatic_contract_rules()` 重构**（第 538-544 行）：通过 `validate_contract_audit_coverage_manifest(_build_contract_audit_coverage_manifest(), forbidden_content_rules=rules.forbidden_contents)` 以实际 forbidden rules 做单次完整校验
  5. **`validate_contract_audit_coverage_manifest` 签名扩展**（第 547-589 行）：新增 keyword-only 参数 `forbidden_content_rules: tuple[...] = _FORBIDDEN_CONTENT_RULES`，透传至 `_validate_must_not_cover_coverage_rules`
- **Fail-closed 验证**：
  - 删除任意 `_FORBIDDEN_CONTENT_RULES` 条目 → `validate_programmatic_contract_rules` 中 `_validate_must_not_cover_coverage_rules` 以 `rules.forbidden_contents` 计算 `programmatic_items` → `missing_items` 非空 → `ValueError` ✓
  - `test_programmatic_contract_rules_fail_closed_for_uncovered_must_not_cover`（`test_audit_programmatic.py:893`）仍按此路径执行并通过 ✓
  - 公开入口 `load_contract_audit_coverage_manifest()` 行为不变（默认 `_FORBIDDEN_CONTENT_RULES` 校验）✓
- **回归检查**：
  - 549 passed ✓
  - Ruff: All checks passed ✓
  - 仅 `contract_rules.py` 有 uncommitted 改动，无 scope creep ✓

## 新增 Findings

无。

## 结论

Finding 1 已正确修复。`_build_contract_audit_coverage_manifest` 构造 helper 正确且不削弱 fail-closed 行为。现有测试和 fix artifact 记录的验证充分。无 scope creep，无回归。

此前 aggregate review 的 no-blocker 结论在 fix 后仍然成立。

---

## Residual Risk

- 与 aggregate review 一致：narrative_guidance 路由仍为声明式覆盖，Ch0 产品 backlog 项仍在 scope 外。

---

- **Findings**: 0（aggregate finding 已修复）
- **最高严重度**: 无
- **Blocker**: 无
- **Artifact 路径**: `docs/reviews/aggregate-rereview-repo-deepreview-audit-type-guards-ds-20260523.md`
