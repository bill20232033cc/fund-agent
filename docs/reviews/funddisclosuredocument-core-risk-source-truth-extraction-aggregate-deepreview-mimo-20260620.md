# Aggregate Deepreview

## Scope

- Mode: Aggregate Deepreview Gate (committed range review)
- Branch: `funddisclosure-core-risk-source-truth`
- Range: `origin/funddisclosure-current-stage-source-truth..HEAD`
- Accepted commits: `75cd23d` (plan), `8332595` (implementation)
- Accepted plan: `docs/reviews/funddisclosuredocument-core-risk-source-truth-extraction-plan-20260620.md`
- Implementation evidence: `docs/reviews/funddisclosuredocument-core-risk-source-truth-extraction-implementation-evidence-20260620.md`
- Code review artifacts reviewed: `docs/reviews/code-review-core-risk-source-truth-ds-20260620.md`, `docs/reviews/code-review-core-risk-source-truth-mimo-20260620.md`
- Output file: `docs/reviews/funddisclosuredocument-core-risk-source-truth-extraction-aggregate-deepreview-mimo-20260620.md`
- Included scope: 16 files changed in committed range; full work unit from plan through implementation
- Excluded scope: `contracts.py`, `active_annual.py`, production `data_extractor.py`, Service/UI/Host/Agent/renderer/quality-gate, parser/repo/source/cache
- Parallel review coverage: 无

## Aggregate Checklist

### 1. Plan/Implementation Consistency

Plan 定义了 5 个 implementation slices：

- Slice 1 (Wire core-risk direct route): 已实现。`_field_families_for_intermediate` 新增 `core_risk_source_truth` 变量，在 `source_truth_extraction_allowed and content_intermediate is not None` 条件下调用 `_extract_core_risk_source_truth`；candidate evidence 在 direct route 时为 `()`。代码行 1001-1052，1080-1081。
- Slice 2 (Minimal core-risk direct extractor): 已实现。`_extract_core_risk_source_truth`、`_select_core_risk_values`、`_build_core_risk_value`、`_core_risk_source_truth_gaps`、`_core_risk_status`、`_core_risk_emitted_output_paths` 全部按 plan 定义实现。中性 risk-characteristic selector helpers 已提取：`_select_risk_characteristic_value`、`_collect_risk_characteristic_table_candidates`、`_collect_risk_characteristic_paragraph_candidates`、`_resolve_risk_characteristic_candidate`、`_RiskCharacteristicValueCandidate` dataclass。代码行 3782-4042, 4518-4811。
- Slice 3 (Processor tests): 已实现。7 个新增 core_risk source-truth 测试 + 多个现有测试更新，覆盖 positive, direct missing, ambiguous, proof missing, proof invalid, candidate boundary, candidate suppression, forbidden keys, non-interference。代码行 6567-6909（test file）。
- Slice 4 (Facade projection tests): 已实现。`_CoreRiskFallbackDisclosureProcessor`、`_CoreRiskProductWinsDisclosureProcessor` 两个 marker processor，`test_explicit_disclosure_core_risk_fallback_projects_risk_text_only`、`test_explicit_disclosure_product_risk_text_wins_over_core_risk_fallback` 两个 facade 测试。未编辑 production `data_extractor.py`。
- Slice 5 (Docs sync): 已实现。`docs/design.md`、`docs/implementation-control.md`、`docs/current-startup-packet.md`、`fund_agent/fund/README.md` 均已更新。

所有 5 个 slices 与 plan 一致。无偏离。

### 2. Source-truth Admission

- `_validate_source_truth_admission()` 六字段 identity 校验未改动。
- `candidate_boundary is not None` → `source_truth_extraction_allowed=False`，阻止所有六个字段族进入 direct extraction。
- Proof-missing → `source_truth_admission_missing`，candidate evidence 保留。
- Proof-invalid → `source_truth_admission_invalid`，candidate evidence 保留。
- Missing provenance / failure_class → blocked/unsupported，无 direct family extraction。
- 测试 `test_core_risk_source_truth_requires_positive_proof`、`test_core_risk_source_truth_rejects_invalid_proof`、`test_core_risk_source_truth_candidate_boundary_remains_blocked` 全部验证。

Source-truth admission 语义完整，fail-closed 路径全部覆盖。

### 3. Public Contract

Plan 规定的 public contract：

- `core_risk.v1.value` 只含 `schema_version` 和 `risk_characteristic_text` → 代码行 4697-4709 (`_build_core_risk_value`) 验证。
- `risk_characteristic_text.v1` shape 与既有 product/profile shape 一致 → `_build_risk_characteristic_text_value` (行 4521-4546) 产出精确 `schema_version`, `fund_code`, `report_year`, `risk_characteristic_text`, `source_anchors` 字典。
- `status` 二元 `accepted | missing` → `_core_risk_status` (行 4792-4802) 仅检查 `"risk_characteristic_text" in value`。
- `extraction_mode` 为 `direct` 或 `missing` → `_extract_core_risk_source_truth` (行 1216) 按 status 派生。
- `candidate_evidence=()` 始终 → 行 1224。
- 四个 `required=False` `deferred_role` gaps → `_core_risk_source_truth_gaps` (行 4777-4787) 仅在 value 非空时追加。
- Forbidden keys 不出现在 public value → 测试 `test_core_risk_source_truth_extracts_risk_characteristic_text_only` 验证。
- 无 `StructuredFundDataBundle.core_risk` → production `data_extractor.py` 零改动。

Public contract 与 plan 完全一致。

### 4. Docs Truth

- `docs/design.md`: 状态补充声明 `core_risk.v1` 只实现 `risk_characteristic_text`，四个 deferred roles，deferred_role gaps。不覆盖完整 core_risk、parser replacement、readiness/release。
- `docs/implementation-control.md`: active gate 更新为 core_risk implementation gate completed locally；truth guardrails 增加 core_risk 限定。
- `docs/current-startup-packet.md`: current active gate 和 next entry point 更新。
- `fund_agent/fund/README.md`: 三处增加 core_risk 限定描述。

所有文档均不声明 parser replacement、readiness、release、golden 或完整 core_risk source truth。文档与实现一致。

### 5. Validation Adequacy

实现 evidence 记录的验证：

- `uv run pytest tests/fund/processors/test_fund_disclosure_processor.py -q`: 188 passed (aggregate deepreview 实时验证: 188 passed in 0.88s)
- `uv run pytest tests/fund/processors/test_fund_disclosure_processor.py -q -k product_essence`: 25 passed, 163 deselected
- `uv run pytest tests/fund/test_data_extractor.py -q`: 42 passed
- `uv run ruff check ...`: All checks passed
- `git diff --check ...`: passed

验证矩阵与 plan Validation Matrix 一致。无 forbidden validation commands 执行。

### 6. Forbidden Scope

- `contracts.py`: 未改动
- `active_annual.py`: 未改动
- `data_extractor.py` production: 未改动
- `docs/fund-analysis-template-draft.md`: 未改动
- 无 repository/source/cache/parser/Docling/pdfplumber/Service/UI/Host/Agent/renderer/quality-gate 改动
- 无 `EvidenceSourceKind` / `EvidenceAnchor` expansion
- 无 `StructuredFundDataBundle.core_risk` field

Forbidden scope 全部遵守。

### 7. Code Review PASS 可辩护性

两份 code review (DS, MiMo) 均给出 `CODE_REVIEW_PASS`。逐项验证：

- 两份 review 都逐条验证了 source-truth admission、candidate_boundary fail-closed、no product_essence call from core_risk、neutral helper correctness、product_essence shape preservation、candidate_evidence suppression、deferred_role gaps、ambiguity behavior、facade fallback、docs truth、forbidden files、test coverage。
- 两份 review 结论一致，无冲突。
- Aggregate deepreview 独立验证确认所有 review findings 准确。

Code review PASS 可辩护。

## Adversarial Failure Pass

### 边界条件检查

1. **Ambiguity + value 空时 gap 语义**: 当 `_resolve_risk_characteristic_candidate` 检测到多个不同 normalized values 时，返回 None 导致 `selected_values` 为空 → `value={}` → `_core_risk_source_truth_gaps` 中 `not value` 为 True 但 `ambiguous_paths` 非空 → 仅输出 `ambiguous_table_or_locator` gap (required=True)，不输出 `field_family_missing` gap。这是正确的：ambiguity 是比 missing 更具体的拒绝理由，测试 `test_core_risk_source_truth_ambiguous_text_returns_missing` 验证。

2. **Direct missing 时无 deferred gaps**: 当 value 为空时（direct missing），`_core_risk_source_truth_gaps` 在 `if not value:` 分支提前 return，不追加 deferred_role gaps。这是正确的：missing 状态下讨论 deferred roles 无意义。

3. **Candidate-boundary 时 deferred role candidate evidence 保留**: 测试 `test_core_risk_source_truth_candidate_boundary_remains_blocked` 验证 `liquidation_or_scale_risk` 的 candidate evidence 仍存在。这是因为 candidate-boundary 时 `core_risk_source_truth` 为 None（未进入 direct extraction），走 `_candidate_missing_field_family` 路径，candidate evidence 从 `_select_core_risk_candidate_evidence` 获得。

4. **Product_essence 与 core_risk 共享 selector 的 label 一致性**: `_collect_risk_characteristic_table_candidates` 和 `_collect_product_essence_table_candidates` 都使用 `_PRODUCT_ESSENCE_LABELS[_RISK_CHARACTERISTIC_OUTPUT_PATH]` 的 labels。product_essence 的 table/paragraph collectors 显式 skip `_RISK_CHARACTERISTIC_OUTPUT_PATH` 以避免重复收集。两套 collector 的 label/generic-text filtering 完全一致。

5. **Existing test 更新正确性**: `test_investor_experience_source_truth_does_not_pollute_stage_or_core_risk` 和 `test_current_stage_source_truth_does_not_project_core_risk_section_locator` 的更新反映了 core_risk 现在进入 direct route 的行为变化：当 proof-positive 中间态同时包含 risk_characteristic_text 内容时，core_risk 直接提取该值。这是预期行为。

6. **Facade fallback 生效路径**: `data_extractor.py:742-754` 的 `core_risk.v1 -> risk_characteristic_text` fallback 在本 gate 前是死代码（core_risk.v1 无法产出 accepted direct value）。本 gate 后，当 `product_essence.v1` 缺少 `risk_characteristic_text` 但 `core_risk.v1` 有该值时，fallback 生效。测试 `test_explicit_disclosure_core_risk_fallback_projects_risk_text_only` 验证。当两者都有时，product_essence 优先。测试 `test_explicit_disclosure_product_risk_text_wins_over_core_risk_fallback` 验证。

### 未发现实质性问题

## Open Questions

无。

## Residual Risk

- 完整 `core_risk.v1` source truth（四个 deferred roles 的 public values/anchors）仍需后续独立 gate。
- 本 gate 不证明 real-report correctness、parser replacement、field correctness、golden/readiness 或 release。
- `_core_risk_status()` 的二元 `accepted | missing` 模型在后续 multi-subvalue gate 中需要重新设计。
- 中性 risk-characteristic helper 的提取使 product_essence 和 core_risk 共享同一 selector，对 `risk_characteristic_text` label 集合的修改会同时影响两个家族。当前 product_essence 25 passed 测试已确认无回归。
- `_core_risk_source_truth_gaps` 的 ambiguity 分支（value 为空 + ambiguous_paths 非空）仅输出 ambiguity gap，不输出 `field_family_missing` gap。这是当前设计，但若后续 gate 需要同时报告多种 gap 类型，需审视此逻辑。

## Verdict

AGGREGATE_DEEPREVIEW_PASS
