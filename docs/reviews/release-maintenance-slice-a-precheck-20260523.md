# Release Maintenance Slice A Precheck — C2 Contract Audit Integrity

## Scope

- Source finding: `docs/reviews/controller-judgment-repo-deepreview-20260523.md` Slice A.
- Target findings:
  - C2 `must_not_cover` 缺少反向完整性校验。
  - 第 0 章“一句话这是什么基金”和“基金简介”共享不可区分 marker。
- Controller role: 只做当前主线核验和裁决，不修改生产代码。

## Current-State Evidence

- `fund_agent/fund/audit/contract_rules.py` 已实现 `_validate_must_not_cover_coverage_rules()`：
  - 校验 manifest `must_not_cover` 全量集合。
  - 合并程序 forbidden marker 与非程序 coverage route。
  - 拒绝缺失覆盖、重复覆盖、未知 manifest 引用和程序/非程序重复覆盖。
- `fund_agent/fund/audit/contract_rules.py` 中第 0 章 required markers 已分离：
  - `一句话这是什么基金` -> `这是什么基金：`
  - `基金简介` -> `基金简介：`
- `tests/fund/audit/test_audit_programmatic.py` 已覆盖上述行为：
  - `test_programmatic_contract_rules_fail_closed_for_uncovered_must_not_cover`
  - `test_contract_audit_coverage_manifest_covers_every_must_not_cover`
  - `test_contract_audit_coverage_manifest_fails_closed_for_missing_must_not_cover_route`
  - `test_contract_audit_coverage_manifest_fails_closed_for_duplicate_must_not_cover_route`
  - `test_contract_audit_coverage_manifest_fails_closed_for_unknown_must_not_cover_route`
  - `test_chapter_0_required_items_use_distinct_markers`

## Verification

```bash
pytest tests/fund/audit/test_audit_programmatic.py::test_programmatic_contract_rules_fail_closed_for_uncovered_must_not_cover tests/fund/audit/test_audit_programmatic.py::test_contract_audit_coverage_manifest_covers_every_must_not_cover tests/fund/audit/test_audit_programmatic.py::test_contract_audit_coverage_manifest_fails_closed_for_missing_must_not_cover_route tests/fund/audit/test_audit_programmatic.py::test_contract_audit_coverage_manifest_fails_closed_for_duplicate_must_not_cover_route tests/fund/audit/test_audit_programmatic.py::test_contract_audit_coverage_manifest_fails_closed_for_unknown_must_not_cover_route tests/fund/audit/test_audit_programmatic.py::test_chapter_0_required_items_use_distinct_markers -q
```

Result: `6 passed in 0.37s`.

## Controller Judgment

Slice A is already satisfied on current main. No implementation handoff is needed for Slice A. The next release-maintenance implementation handoff should move to Slice B, numeric type guards.
