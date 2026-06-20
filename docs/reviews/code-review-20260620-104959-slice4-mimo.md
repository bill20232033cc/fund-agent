# Code Review

## Scope

- Mode: current changes (Slice 4 implementation)
- Branch: `funddisclosure-return-attribution-source-truth`
- Base: `6c30386` (latest accepted checkpoint)
- Output file: `docs/reviews/code-review-20260620-104959-slice4-mimo.md`
- Included scope: `tests/fund/test_data_extractor.py`, `docs/design.md`, `fund_agent/fund/README.md`, `docs/reviews/funddisclosuredocument-manager-profile-source-truth-extraction-slice4-implementation-evidence-20260620.md`
- Excluded scope: production `data_extractor.py`, `fund_disclosure_processor.py`, `contracts.py`, Service/UI/Host/renderer/quality-gate, control docs
- Parallel review coverage: none

## Findings

未发现实质性问题。

## Open Questions

- 无。

## Residual Risk

- 正向 facade 回归测试不验证 `EvidenceAnchor.source_kind`、具体 `row_locator` 格式或 `candidate_evidence == ()`。这些由 `tests/fund/processors/test_fund_disclosure_processor.py` 中已有的 Slice 1-3 测试覆盖，不在本 Slice 4 facade 回归范围内。
- 正向 facade 回归只覆盖 proof-positive direct route 全部五子字段 emitted（accepted 状态），未覆盖 proof-positive route 下 partial 或 missing 子字段的 facade 投影行为。partial/missing 行为由 processor 测试覆盖。
- `manager_alignment.judgment` 保持 `None` 由 fixture 设计保证；无独立断言。
- Real-report manager-profile 字段正确性仍未证明，归属后续 evidence gate。

## Review Questions Answered

### Q1: Positive FDD facade regression proof

**是。** `test_explicit_disclosure_source_truth_manager_profile_projects_to_bundle` (L1226-1313) 使用 `FundProcessorRegistry.create_default()` 生产 registry，传入带有效 `FundDisclosureSourceTruthAdmissionProof` 的 FDD stub，断言：

- `bundle.portfolio_managers.extraction_mode == "direct"`，值包含 `schema_version="portfolio_manager_tenure_list.v1"`、`fund_code`、`report_year` 和具体 manager 条目
- `bundle.turnover_rate.value` 包含 `turnover_rate` 和 `turnover_basis`
- `bundle.manager_alignment.value` 包含 `manager_holding`、`employee_holding` 和 `judgment=None`
- `bundle.manager_strategy_text.value` 包含 `strategy_summary` 和 `market_outlook`
- `bundle.holdings_snapshot.value` 包含 `top_holdings`、`top_holdings_status`、`top_holdings_source`、`industry_distribution`、`industry_distribution_status`
- 五个字段全部 `extraction_mode == "direct"` 且 `.anchors` 非空
- 不相关字段 (`investor_return`, `holder_structure`, `share_change`, `bond_risk_evidence`) 保持 `value is None`

### Q2: Negative facade regression proof

**是。** `test_explicit_disclosure_candidate_only_manager_profile_stays_missing` (L1317-1360) 使用 `FundProcessorRegistry.create_default()` 生产 registry，传入 `source_truth_admission=None` 的同一 FDD content stub，断言五个 manager_profile bundle 字段全部 `value is None`、`anchors == ()`、`extraction_mode == "missing"`。candidate evidence 不被提升为字段值。

### Q3: Docs accuracy

**是。** `docs/design.md` 和 `fund_agent/fund/README.md` diff 准确更新：

- `product_essence.v1`、`return_attribution.v1`、`manager_profile.v1` 有 proof-positive FDD source-truth direct extraction
- `investor_experience.v1`、`current_stage.v1`、`core_risk.v1` 仍未实现，保持 public `missing`
- candidate evidence 保持 candidate_only / not_proven / NOT_READY
- 不声明 real-report correctness、parser replacement、readiness 或 release

### Q4: Scope compliance

**是。** 只修改了 plan 允许的文件：`tests/fund/test_data_extractor.py`、`docs/design.md`、`fund_agent/fund/README.md`、`docs/reviews/` 实现证据。未修改生产 facade 代码、parser、`EvidenceSourceKind`/`EvidenceAnchor`、Service/UI/Host/renderer/quality-gate 代码。

## Validation

```text
uv run pytest tests/fund/test_data_extractor.py tests/fund/processors/test_fund_disclosure_processor.py
194 passed in 0.53s
```

```text
uv run ruff check tests/fund/test_data_extractor.py tests/fund/processors/test_fund_disclosure_processor.py
All checks passed!
```

```text
git diff --check -- tests/fund/test_data_extractor.py tests/fund/processors/test_fund_disclosure_processor.py docs/design.md fund_agent/fund/README.md
<no output>
```

## Verdict

**PASS**
