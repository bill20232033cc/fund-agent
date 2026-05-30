# Slice 3 Code Review: Bundle Integration

> Date: 2026-05-27
> Reviewer: AgentMiMo
> Gate: Slice 3 code review after implementation
> Branch: `codex/local-reconciliation`
> Status: **PASS**

## Review Criteria Results

### 1. StructuredFundDataBundle.bond_risk_evidence field — PASS

`data_extractor.py:148` — 显式字段 `bond_risk_evidence: ExtractedField[BondRiskEvidenceValue]`，使用 `default_factory=_default_bond_risk_evidence_field`。无 `extra_payload` 使用。类型签名正确。

### 2. 年报单次加载 + 显式 classified_fund_type — PASS

- `data_extractor.py:201` — `report = await self._repository.load_annual_report(...)` 仅调用一次。
- `data_extractor.py:215` — `classified_fund_type = _classified_fund_type(profile_result.basic_identity)` 从已有的 `profile_result.basic_identity` 计算。
- `data_extractor.py:216-218` — `extract_bond_risk_evidence(report, classified_fund_type=classified_fund_type)` 显式传入。
- 同一个 `classified_fund_type` 也被 `_tracking_error_for_fund_type` 复用（`data_extractor.py:232-235`），无重复计算。

### 3. Source provenance 和 tracking_error 行为保持不变 — PASS

- `data_extractor.py:232-235` — `tracking_error` 仍通过 `_tracking_error_for_fund_type` 裁剪，逻辑未变。
- `data_extractor.py:242` — `source_provenance` 仍通过 `project_public_source_provenance(report.metadata.source)` 投影。
- 测试中 provenance 断言（`test_data_extractor.py:166-167, 260-268, 341-344, 371-374, 404-408`）全部保留且通过。

### 4. 非债券路径 not-applicable 且不扫描七组 — PASS

- `test_data_extractor.py:272-315` — monkeypatch 测试将 `_extract_duration_rate_risk` 替换为失败函数，验证非债券基金（`active_fund`）路径：
  - `bond_risk_evidence.value is None`
  - `bond_risk_evidence.extraction_mode == "missing"`
  - `bond_risk_evidence.note == "not_applicable_non_bond_fund"`
  - 不触发七组 extractor（monkeypatch 函数若被调用则 AssertionError）。

### 5. 无 Service/UI/PDF/cache/snapshot/score/golden 变更 — PASS

仅修改 `data_extractor.py` 和 `test_data_extractor.py`。构造函数签名未变。无直接 PDF/cache/source helper 调用。

### 6. 测试充分性 — PASS

8 个测试全部通过，覆盖：

| 测试 | 覆盖场景 |
|------|---------|
| `test_data_extractor_degrades_nav_failure_without_blocking_annual_report` | NAV 失败降级 + bond_risk_evidence 非债券缺失 |
| `test_data_extractor_does_not_mask_repository_failure` | 仓库异常不被吞掉 |
| `test_structured_bundle_default_source_provenance_is_not_none` | 默认 fixture 构造安全 |
| `test_data_extractor_returns_bundle_with_bond_risk_evidence` | 正常抽取携带 bond_risk_evidence |
| `test_data_extractor_non_bond_bond_risk_evidence_does_not_scan_groups` | 非债券早退不扫描七组 |
| `test_data_extractor_projects_primary_source_metadata` | 主源 provenance 投影 |
| `test_data_extractor_projects_fallback_metadata_as_unknown_when_category_absent` | fallback 缺失分类保持 unknown |
| `test_data_extractor_projects_metadata_primary_failure_category` | 主源失败分类投影 |

## Findings

无 blocking findings。

## Residual Risks

1. **Monkeypatch 覆盖深度**：非债券早退测试仅 patch 了 `_extract_duration_rate_risk`（第一组 extractor）。若早退逻辑失效，其余六组 extractor 未被 patch，测试仍可能通过但掩盖生产 bug。风险低（Slice 2 extractor 测试覆盖七组行为），可接受。

2. **`bond_risk_evidence` 字段位置**：`StructuredFundDataBundle` 中该字段位于 `source_provenance` 之后（`data_extractor.py:148`），而其他数据字段在 `source_provenance` 之前。这是 default_factory 字段的放置位置，功能正确，但与字段逻辑分组有轻微不一致。不影响合约或测试。

3. **Slice 3 范围确认**：Snapshot 投影、score 适用性、quality gate 和真实 `006597` 验证均属于后续 Slice 4-6，不在本次审查范围。

## Lint & Test Results

```
uv run ruff check fund_agent/fund/data_extractor.py tests/fund/test_data_extractor.py
→ All checks passed!

uv run pytest tests/fund/test_data_extractor.py -q
→ 8 passed in 0.72s
```

## Conclusion

**PASS**。Slice 3 实现满足全部六项审查标准。无 blocking findings。Residual risks 均为低风险且在后续 slice 范围内处理。
