# FundDisclosureDocument current_stage.v1 Source-truth Direct Extraction Code Review (DS)

## Verdict

`CODE_REVIEW_PASS`

## Findings

### No Blocking Findings

本 review 未发现阻塞性 finding。实现严格符合 accepted plan `docs/reviews/funddisclosuredocument-current-stage-source-truth-extraction-plan-20260620.md` 的全部范围、contract 和 non-goal 约束。

### 逐条验证摘要

**Scope boundary（全部通过）**

- `_extract_current_stage_source_truth()` 只在 `source_truth_extraction_allowed and content_intermediate is not None` 时调用（`fund_disclosure_processor.py:999-1001`），proof-missing/proof-invalid/candidate-boundary 路径保持 fail-closed public missing。
- allowed public keys 仅 `schema_version`、`basic_identity`、`share_change`、`holdings_snapshot`、`portfolio_managers`，由 `_CURRENT_STAGE_REQUIRED_TOP_LEVEL` 常量（`:358-362`）和 `_build_current_stage_value()`（`:6538-6552`）双重约束。
- 未新增 `StructuredFundDataBundle.current_stage`；facade 测试 `test_explicit_disclosure_current_stage_source_truth_has_no_bundle_projection` 和 marker 测试 `test_active_fund_uses_processor_path_with_marker_values` 均断言 `not hasattr(bundle, "current_stage")`。
- 未引入 `current_stage_summary`、`stage_status`、`manager_change`、`share_scale_change`、`holding_strategy_change`、`stage_judgment`、`market_timing`、`valuation_state` 或 final holding/replacement judgment；测试 `test_current_stage_source_truth_extracts_allowed_fact_inputs_only` 显式验证 `forbidden_keys.isdisjoint(value)`。

**Candidate evidence 抑制（全部通过）**

- Direct route（含 direct missing）`candidate_evidence` 均为空 tuple：`_extract_current_stage_source_truth()` 返回 `candidate_evidence=()`（`:6494`），`_field_families_for_intermediate()` 在 `current_stage_source_truth is not None` 时将 `current_stage_evidence` 设为 `()`（`:1023-1026`）。
- 测试 `test_current_stage_source_truth_direct_missing_suppresses_candidate_evidence` 确认 direct missing 不回退 candidate evidence。

**Fail-closed 路径（全部通过）**

- `test_current_stage_source_truth_requires_positive_proof()`: source_truth_admission=None → status=missing, value={}, anchors=(), candidate_evidence 存在，gap 包含 `source_truth_admission_missing`。
- `test_current_stage_source_truth_rejects_invalid_proof()`: fund_code 不一致 → status=missing, gap 包含 `source_truth_admission_invalid`。
- `test_current_stage_source_truth_candidate_boundary_remains_blocked()`: candidate_boundary 存在 → contract_status=blocked, status=missing, gap 包含 `candidate_only_not_source_truth`。

**core_risk.v1 非干涉（通过）**

- `core_risk_evidence = _select_core_risk_candidate_evidence(intermediate)` 保持无条件调用（`:1028`），无 `_extract_core_risk_source_truth()` 函数。
- 测试 `test_current_stage_source_truth_does_not_implement_core_risk()` 确认 core_risk 保持 missing/candidate-only。

**Helper 复用（全部通过）**

- `basic_identity`: 调用 `_select_product_essence_values()` + `_build_product_essence_basic_identity()`（`:6516-6523`），未新增 identity parser。
- `share_change`: 调用 `_select_investor_experience_share_change()`（`:6543`），复用现有 arithmetic/column-selection 逻辑。
- `holdings_snapshot`: 调用 `_select_manager_profile_holdings_snapshot()`（`:6550`），未输出 concentration/style/risk/current-stage 结论。
- `portfolio_managers`: 调用 `_select_manager_profile_portfolio_managers()`（`:6560`），未输出 manager quality 或 current-stage 推断。
- 无新增 parser、无 EvidenceSourceKind 扩展、无 EvidenceAnchor 扩展。

**禁止事项（全部通过）**

- 无 parser replacement、无 source acquisition 变更、无 repository/source 行为变更。
- 无 Service/UI/Host/renderer/quality-gate consumption。
- 无 live/network/PDF/FDR/Docling/pdfplumber/provider/LLM 命令或 claims。
- 无 readiness/release/PR mark-ready 声明。

**Docs sync（通过）**

- `docs/implementation-control.md` 的 Active gate 和 Next entry point 均正确指向 Code Review Gate，未提前宣称 accepted slice、PR、readiness 或 release。
- `docs/design.md` v2.32 的 `current_stage.v1` 描述精确：只复用 `basic_identity`、`share_change`、`holdings_snapshot`、`portfolio_managers`，不投影 bundle，不输出语义摘要，`core_risk.v1` 仍未实现。
- `docs/current-startup-packet.md` 状态行同步为 implementation completed locally, pending code review。
- `fund_agent/fund/README.md` 同步了 five-family 覆盖和 bundle non-projection。

**Validation（controller 预跑，通过）**

- `uv run pytest tests/fund/processors/test_fund_disclosure_processor.py`: 181 passed
- `uv run pytest tests/fund/test_data_extractor.py`: 40 passed
- `uv run ruff check`: passed
- `git diff --check`: passed

## Residual Risks / Test Gaps

1. **Existing fixture test `test_investor_experience_source_truth_does_not_populate_stage_or_risk` 的 share_change candidate evidence 行为变化**: 该测试在 investor_experience source-truth 路径下之前断言 `current_stage.candidate_evidence` 为 truthy（存在 candidate evidence），现在断言 `current_stage.candidate_evidence == ()`。这是因为 investor_experience 的 source-truth 路径现在也触发了 current_stage direct extraction（share_change 复用）。该行为变化是正确的——plan 明确要求 direct route 的 candidate_evidence 为空——但这是一个现有 investor_experience 路径的 observable 行为变化，当前测试覆盖了它。**Risk**: 无，已被测试捕获。

2. **`_CURRENT_STAGE_REQUIRED_TOP_LEVEL` 硬编码四个 key**: 若未来需要调整 current_stage 的 required key 集合，需修改该常量。这与 plan 一致——plan 明确将 key expansion 推迟到独立 schema/public contract gate。**Risk**: 非当前 gate 范围。

3. **依赖 `_select_investor_experience_share_change` 和 `_select_manager_profile_*` 传入 `ambiguous_paths` set**: current_stage 的 `_select_current_stage_values()` 将 `ambiguous_paths` set 传入 share_change/holdings_snapshot/portfolio_managers 选择器。若这些选择器在未来被修改为向该 set 写入非 current_stage 相关的路径，可能产生误报 ambiguity。当前实现中这些选择器只在各自 owned 路径出现冲突时写入，行为合理。**Risk**: 低，属于维护性关注。

4. **core_risk.v1 仍然是 missing**: plan 明确将 core_risk.v1 作为后续独立 work unit。当前实现正确保持 core_risk 为 candidate-only/missing。**Risk**: 非当前 gate 范围。

## Validation Summary

实现严格按照 accepted plan 的 Exact Extraction Decisions、Implementation Slices 1-4 和 Validation Matrix 执行。所有 mandatory check 通过：

- proof-positive 路径正确发出四个 allowed keys（含 schema_version）
- direct missing 路径正确回退 public missing + empty candidate_evidence
- proof-missing/proof-invalid/candidate-boundary 路径正确 fail-closed
- core_risk.v1 正确保持未实现
- 无 forbidden key、无 bundle projection、无 parser replacement、无 source kind/anchor expansion
- helper 复用路径精确匹配 plan 指定
- docs sync 只声明当前事实，未越界

## Stop Condition

本次 Code Review Gate complete。不进入 fix gate、re-review gate、PR gate 或下一 phase。
