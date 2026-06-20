# FundDisclosureDocument current_stage.v1 Source-truth Direct Extraction Aggregate Deepreview (DS)

**Role**: AgentDS，独立 aggregate deepreview reviewer
**Gate**: Aggregate Deepreview Gate
**Work unit**: `FundDisclosureDocument current_stage.v1 Source-truth Direct Extraction`
**Branch**: `funddisclosure-current-stage-source-truth`
**Review range**: `d85baad..7c63409`
**Date**: 2026-06-20

## Verdict

`AGGREGATE_DEEPREVIEW_PASS`

## Findings

### No Blocking Findings

本 aggregate deepreview 未发现阻塞性 finding。实现、测试、文档和评审 artifact 在全部 mandatory check 上一致通过。

---

## Mandatory Check Results

### M1: 实现对照 Accepted Plan 和 Controller Amendments — PASS

实现严格遵循 accepted plan (`docs/reviews/funddisclosuredocument-current-stage-source-truth-extraction-plan-20260620.md`) 及 DS re-review 后的精确约束：

- `_extract_current_stage_source_truth()` 仅在 `source_truth_extraction_allowed and content_intermediate is not None` 时调用（`fund_disclosure_processor.py:999-1001`），proof-missing/proof-invalid/candidate-boundary 路径保持 fail-closed
- 四个 key 的精确复用目标全部命中：`basic_identity` 复用 `_select_product_essence_values()` + `_build_product_essence_basic_identity()`；`share_change` 复用 `_select_investor_experience_share_change()`；`holdings_snapshot` 复用 `_select_manager_profile_holdings_snapshot()`；`portfolio_managers` 复用 `_select_manager_profile_portfolio_managers()`
- 未引入新 identity parser 或 current-stage parser
- 未超出 bounded refactor budget（零个新增共享 helper，直接复用现有函数调用）
- Implementation Slices 1-5 全部完成

### M2: 代码、测试、文档、评审 Artifact 一致性 — PASS

- `docs/design.md` v2.32：`current_stage.v1` 加入 proof-positive FDD source-truth direct extraction 列表，声明仅四 key、不投影 bundle、不输出语义摘要，`core_risk.v1` 仍未实现
- `docs/implementation-control.md`：Active gate 正确指向 Code Review Gate，Next entry point 正确指向 Aggregate Deepreview Gate，未提前宣称 PR/readiness/release
- `docs/current-startup-packet.md`：状态行同步，next entry 为 Aggregate Deepreview Gate
- `fund_agent/fund/README.md`：同步 five-family 覆盖和 bundle non-projection
- 代码、测试、文档三者口径一致，无双重表述

### M3: Allowed Current Stage Value Keys — PASS

`_CURRENT_STAGE_REQUIRED_TOP_LEVEL` 常量（`fund_disclosure_processor.py:358-362`）仅包含：
- `basic_identity`
- `share_change`
- `holdings_snapshot`
- `portfolio_managers`

`schema_version` 由 `_build_current_stage_value()` 在至少一个 key 被发出时自动追加。测试 `test_current_stage_source_truth_extracts_allowed_fact_inputs_only` 显式验证 `set(value) == {"schema_version", "basic_identity", "share_change", "holdings_snapshot", "portfolio_managers"}`。

### M4: 无 Bundle-level current_stage / 无语义摘要 / 无禁止 key — PASS

- 无 `StructuredFundDataBundle.current_stage` 属性（测试 `test_explicit_disclosure_current_stage_source_truth_has_no_bundle_projection` 和 `test_active_fund_uses_processor_path_with_marker_values` 均断言 `not hasattr(bundle, "current_stage")`）
- 无 `current_stage_summary`、`stage_status`、`manager_change`、`share_scale_change`、`holding_strategy_change`、`stage_judgment`、`market_timing`、`valuation_state` 或 final holding/replacement judgment
- 测试 `test_current_stage_source_truth_extracts_allowed_fact_inputs_only` 显式验证 `forbidden_keys.isdisjoint(value)`
- 代码中上述 token 仅出现在 S6-G candidate selector（candidate-only evidence），不出现在 source-truth direct extraction 路径

### M5: Direct Route candidate_evidence 为空，含 Direct Missing — PASS

- `_extract_current_stage_source_truth()` 返回 `candidate_evidence=()`（`:6494`）
- `_field_families_for_intermediate()` 在 `current_stage_source_truth is not None` 时将 `current_stage_evidence` 设为 `()`（`:1023-1026`）
- 测试 `test_current_stage_source_truth_direct_missing_suppresses_candidate_evidence` 确认 direct missing 也不回退 candidate evidence
- 测试 `test_current_stage_source_truth_extracts_allowed_fact_inputs_only` 确认 `family.candidate_evidence == ()`

### M6: Proof-missing/Proof-invalid/Candidate-boundary Fail-closed — PASS

三个测试覆盖全部 fail-closed 路径：
- `test_current_stage_source_truth_requires_positive_proof()`：`source_truth_admission=None` → `status=missing`，gap 含 `source_truth_admission_missing`
- `test_current_stage_source_truth_rejects_invalid_proof()`：`fund_code` 不一致 → `status=missing`，gap 含 `source_truth_admission_invalid`
- `test_current_stage_source_truth_candidate_boundary_remains_blocked()`：`candidate_boundary` 存在 → `contract_status=blocked`，不产出 public value/anchors
- 三条路径均无 candidate evidence 提升为 public value/anchors

### M7: core_risk.v1 仍为 Unimplemented Source-truth — PASS

- 无 `_extract_core_risk_source_truth()` 函数
- `core_risk_evidence = _select_core_risk_candidate_evidence(intermediate)` 保持无条件调用（`:1028`）
- 测试 `test_current_stage_source_truth_does_not_implement_core_risk()` 确认 core_risk 保持 missing/candidate-only
- `docs/design.md`、`docs/implementation-control.md`、`docs/current-startup-packet.md`、`fund_agent/fund/README.md` 均声明 `core_risk.v1` FDD source-truth extraction 仍未实现

### M8: 无 Parser Replacement / EvidenceSourceKind Expansion / EvidenceAnchor Expansion / Upper-Layer Consumption — PASS

- Diff 中无 `fund_agent/fund/documents/` 变更（parser 仓库行为未变）
- 无新 `EvidenceSourceKind` 值（所有 anchor 仍为 `source_kind="annual_report"`）
- 无 public `EvidenceAnchor` schema expansion
- 无 Service/UI/Host/renderer/quality-gate 消费代码
- 无 live/network/PDF/FDR/Docling/pdfplumber/provider/LLM 命令或声明
- 无 readiness、release、PR mark-ready 声明

### M9: Helper 复用匹配 Plan — PASS

`_select_current_stage_values()` 精确调用：
- `basic_identity`：`_select_product_essence_values(intermediate, context)` → `_build_product_essence_basic_identity(product_values, context)`，未调用 `_extract_product_essence_source_truth()`，无新 identity parser
- `share_change`：`_select_investor_experience_share_change(intermediate, context, ambiguous_paths)`，复用全部 arithmetic/column-selection/row-kind 逻辑
- `holdings_snapshot`：`_select_manager_profile_holdings_snapshot(intermediate, context, ambiguous_paths)`，未输出 concentration/style/risk/current-stage 结论
- `portfolio_managers`：`_select_manager_profile_portfolio_managers(intermediate, context, ambiguous_paths)`，未输出 manager quality 或 current-stage 推断
- 零个新增 module-local helper（refactor budget 未消耗），现有 owning-family 调用链保持 shape-preserving

### M10: 测试覆盖 / Docs Control Next Entry — PASS

- Processor 测试：181 passed（含 positive、direct missing、proof-missing、proof-invalid、candidate-boundary、schema guard、core_risk non-interference、owning-family behavior preservation）
- Facade 测试：40 passed（含 no-bundle-attribute、no-projection、all-six-family owning-family projection）
- ruff check：passed
- git diff --check：passed
- `docs/implementation-control.md` next entry point：`FundDisclosureDocument current_stage.v1 Source-truth Direct Extraction Aggregate Deepreview Gate`
- 未宣称 PR/readiness/release

---

## Residual Risks / Test Gaps

1. **`_CURRENT_STAGE_REQUIRED_TOP_LEVEL` 硬编码四 key**（`fund_disclosure_processor.py:358-362`）：若未来需调整 current_stage required key 集合，需修改该常量并走独立 schema gate。**非当前 gate 范围**。

2. **`ambiguous_paths` set 跨 family 共享**（`fund_disclosure_processor.py:6516-6579`）：`_select_current_stage_values()` 将同一个 `ambiguous_paths` set 传入 `share_change`、`holdings_snapshot`、`portfolio_managers` 选择器。若未来修改这些选择器的 ambiguity 写入逻辑，可能产生误报。当前实现中这些选择器仅在各自 owned 路径冲突时写入，行为合理。**低风险维护关注**。

3. **`core_risk.v1` 仍为唯一缺失 FDD source-truth 字段族**：plan 明确作为后续独立 work unit。**非当前 gate 范围**。

4. **`current_stage.v1` 仅作为 fact-input 字段族**：不提供语义阶段判断、市场/估值状态或最终持有/替换建议。这些需要独立 schema/public contract gate。**非当前 gate 范围**。

5. **Existing investor_experience source-truth 路径的 observable 行为变化**：`test_investor_experience_source_truth_does_not_populate_stage_or_risk` 之前断言 `current_stage.candidate_evidence` 为 truthy，现在断言 `current_stage.candidate_evidence == ()`。这是正确的行为变化（plan 明确要求 direct route candidate_evidence 为空），已被测试捕获。**无风险**。

---

## Validation / Evidence Summary

**Cross-artifact consistency**：7 个评审输入 artifacts（plan、plan review、plan re-review、plan controller judgment、implementation evidence、code review、code review controller judgment）在范围、key、禁止项、fail-closed 语义、core_risk 非干涉和 non-goal 约束上完全一致。

**Implementation evidence**：10 files changed，+1080/-40 lines，实现严格对应 5 个 plan slices；无越界变更。

**Test evidence**：processor tests 181 passed + facade tests 40 passed = 221 passed。覆盖全部正向/负向/边界路径。

**Docs evidence**：4 个文档（design.md v2.32、implementation-control.md、startup-packet.md、fund/README.md）同步一致，无过期口径。

**Controller validation**：controller 预跑 `uv run pytest`、ruff、git diff --check 全部通过。

---

## Stop Condition

Aggregate Deepreview Gate 完成。不进入 fix gate、re-review gate、PR gate、readiness/release 或下一 phase。Next entry point 由 controller 在 `docs/implementation-control.md` 中更新。
