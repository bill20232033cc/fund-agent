# Code Review

## Scope

- Mode: current changes (uncommitted workspace changes only)
- Branch: `funddisclosure-core-risk-source-truth`
- Base: `main` (committed branch history includes prior source-truth work units)
- Output file: `docs/reviews/code-review-core-risk-source-truth-ds-20260620.md`
- Included scope: uncommitted changes to `fund_agent/fund/processors/fund_disclosure_processor.py`, `tests/fund/processors/test_fund_disclosure_processor.py`, `tests/fund/test_data_extractor.py`, `docs/design.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md`, `fund_agent/fund/README.md`
- Excluded scope: committed branch history prior to this work unit; untracked docs files (`docs/code-wiki.md`, `docs/codewiki.md`, etc.) not part of this work unit; `contracts.py` / `active_annual.py` / production `data_extractor.py` (not in uncommitted changes); repository/source/cache/parser/Docling/pdfplumber/Provider/LLM/Service/UI/Host/renderer/quality gate (unchanged)
- Parallel review coverage: 无

## Findings

未发现实质性问题。

### 逐项验证记录

以下按 review priorities 逐项验证，均基于代码直接证据：

**1. source-truth admission proof** (`fund_disclosure_processor.py:1099-1145`)

`_validate_source_truth_admission()` 校验 proof identity 六字段（fund_code, report_year, document_kind, intermediate_kind, source_kind）与 context 及 content_intermediate 三方一致性；`candidate_boundary is not None` → `source_truth_admission_invalid`；`failure_class is not None` → `source_truth_admission_invalid`；`source_provenance is None` → `source_truth_admission_invalid`。proof missing 返回 `source_truth_admission_missing`。全部校验通过后方可进入 direct extraction。

**2. candidate_boundary fail-closed** (`fund_disclosure_processor.py:1126-1127`)

`candidate_boundary is not None` 直接映射为 `source_truth_admission_invalid`，导致 `source_truth_extraction_allowed=False`，阻止所有六个字段族进入 direct extraction。测试 `test_core_risk_source_truth_candidate_boundary_remains_blocked` (test line 6818) 验证 `result.contract_status == "blocked"`，public value/anchors 为空，candidate evidence 保持 candidate-only。

**3. no _select_product_essence_values call from core_risk** (verified by grep)

`_select_product_essence_values` 仅出现在三处：`_extract_product_essence_source_truth:1167`（调用）、函数定义 `:3733`、以及测试 `test_fund_disclosure_processor.py:7037`。`_select_core_risk_values:4682` 仅调用 `_select_risk_characteristic_value`。

**4. neutral risk-characteristic helper correctness** (`fund_disclosure_processor.py:3782-4042`)

- `_select_risk_characteristic_value` 仅收集 `risk_characteristic_text.risk_characteristic_text` 单一 output path
- `_collect_risk_characteristic_table_candidates` 仅匹配 `_PRODUCT_ESSENCE_LABELS[_RISK_CHARACTERISTIC_OUTPUT_PATH]` = `("风险收益特征", "基金风险收益特征")`
- `_collect_risk_characteristic_paragraph_candidates` 同理
- `_is_risk_characteristic_value_allowed` 过滤空值、label 自身、泛化表头
- 不收集 product identity、benchmark、fee、tracking-error、turnover、holdings、holder-structure 等 product_essence 其他值
- 返回类型为 `_RiskCharacteristicValueCandidate`（家族中立类型，仅含 output_path/value/anchor/source_field_path）

**5. product_essence shape preservation** (`fund_disclosure_processor.py:3733-3779, 4521-4546`)

- `_select_product_essence_values` 对 `risk_characteristic_text.risk_characteristic_text` 路径走 `_select_risk_characteristic_value`，然后将 `_RiskCharacteristicValueCandidate` 包装为 `_ProductEssenceValueCandidate`（`:3762-3767`）
- 其余 product_essence 路径仍走原有 `_collect_product_essence_table_candidates` / `_collect_product_essence_paragraph_candidates`
- `_build_risk_characteristic_text_value:4521-4546` 产出精确的既有 `risk_characteristic_text.v1` 字典形状：`schema_version`, `fund_code`, `report_year`, `risk_characteristic_text`, `source_anchors`
- product_essence 测试 25 passed + processor 全量 188 passed 确认 shape 兼容

**6. direct candidate_evidence suppression** (`fund_disclosure_processor.py:1188-1225, 1051-1052`)

- `_extract_core_risk_source_truth` 始终返回 `FundFieldFamilyResult(..., candidate_evidence=())`，无任何条件分支
- `_field_families_for_intermediate:1051-1052` 中 `core_risk_evidence = () if core_risk_source_truth is not None else _select_core_risk_candidate_evidence(intermediate)`
- 因为 direct extractor 始终返回非 None，所以 direct route（含 direct missing）的 `candidate_evidence` 始终为空元组
- 测试 `test_core_risk_source_truth_direct_missing_suppresses_candidate_evidence:6659` 和 `test_core_risk_source_truth_candidate_tokens_do_not_leak_on_direct_route:6868` 验证

**7. four required=False deferred_role gaps** (`fund_disclosure_processor.py:66-71, 4735-4788`)

- `_CORE_RISK_DEFERRED_ROLES` = `("liquidation_or_scale_risk", "tracking_error_or_deviation_risk", "turnover_or_style_drift_risk", "concentration_risk")`
- `_core_risk_source_truth_gaps:4777-4787` 仅在 `value` 非空时追加四个 `required=False` `deferred_role` gaps
- 测试 `test_core_risk_source_truth_extracts_risk_characteristic_text_only:6577` 验证 gaps 包含四个 deferred_role，全部 `required=False`，且 forbidden keys 不在 value 中
- deferred_role gaps 不携带 candidate evidence，不进入 public value

**8. ambiguity behavior** (`fund_disclosure_processor.py:4019-4042`)

- `_resolve_risk_characteristic_candidate` 对多个不同归一化值的候选 → `ambiguous_paths.add(_RISK_CHARACTERISTIC_OUTPUT_PATH)` → 返回 None
- `_core_risk_source_truth_gaps:4753-4763` 对 ambiguous_paths 输出 `ambiguous_table_or_locator` gap
- value 为空 + ambiguous_path 非空时仅返回 ambiguity gap，不追加 `field_family_missing`
- 测试 `test_core_risk_source_truth_ambiguous_text_returns_missing:6695` 验证：status=missing, value={}, anchors=(), candidate_evidence=(), gap 为 `ambiguous_table_or_locator`

**9. facade fallback no production data_extractor edit** (verified by git diff)

- `git diff -- fund_agent/fund/data_extractor.py` 无输出：production `data_extractor.py` 零改动
- 既有 fallback 逻辑位于 `data_extractor.py:742-754`，未修改
- Facade 测试 `test_explicit_disclosure_core_risk_fallback_projects_risk_text_only:1583` 和 `test_explicit_disclosure_product_risk_text_wins_over_core_risk_fallback:1636` 验证 fallback 行为正确，且 product_essence 优先

**10. docs truth sync** (verified by git diff -- docs/design.md docs/implementation-control.md docs/current-startup-packet.md fund_agent/fund/README.md)

- `docs/design.md`: 状态补充更新 `core_risk.v1` 从"仍未实现"→"当前只实现 risk_characteristic_text"，明确四个 deferred roles 和 deferred_role gaps；变更摘要声明不覆盖完整 core_risk source truth、parser replacement、readiness/release
- `docs/implementation-control.md`: active gate 更新为 core_risk implementation gate completed locally；truth guardrails 增加 core_risk `risk_characteristic_text` 限定；明确不授权完整 core_risk、push/PR/commit/stage
- `docs/current-startup-packet.md`: current active gate 更新
- `fund_agent/fund/README.md`: 多处增加 core_risk 限定描述，保持 deferred/candidate-only 口径
- 所有文档均不声明 parser replacement、readiness、release、golden 或完整 core_risk source truth

**11. forbidden files/modules** (verified by git diff --name-only)

- `contracts.py`: 不在 uncommitted changes 中
- `active_annual.py`: 不在 uncommitted changes 中
- `data_extractor.py` 生产代码: 不在 uncommitted changes 中（仅 test 文件有改动）
- `docs/fund-analysis-template-draft.md`: 未修改
- 无 repository/source/cache/parser/Docling/pdfplumber/Service/UI/Host 文件改动

**12. 测试矩阵覆盖** (verified by test file read)

全部 12 个 required processor test cases 均有对应测试函数，facade 测试覆盖 fallback 路径、product essence 优先级、no bundle.core_risk、candidate-only 不投影。验证命令全部通过（processor 188 passed, product_essence 25 passed, data_extractor 42 passed, ruff all clean）。

## Open Questions

无。

## Residual Risk

- 完整 `core_risk.v1` source truth（四个 deferred roles 的 public values/anchors）仍需后续独立 gate
- 本 gate 不证明 real-report correctness、parser replacement、field correctness、golden/readiness 或 release
- `_core_risk_status()` 的二元 `accepted | missing` 模型在后续 multi-subvalue gate 中需要重新设计
- 中性 risk-characteristic helper 的提取未改变 product_essence 行为（product_essence 测试 25 passed 确认），但长期看两个家族共享同一 selector 意味着对 `risk_characteristic_text` 的 label 集合修改会同时影响两个家族

## Verdict

CODE_REVIEW_PASS
