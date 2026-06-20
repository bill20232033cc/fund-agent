# Aggregate Deepreview

## Scope

- Mode: Gateflow aggregate deepreview (committed range)
- Work unit: `FundDisclosureDocument core_risk.v1 risk_characteristic_text Source-truth Direct Extraction`
- Branch: `funddisclosure-core-risk-source-truth`
- Base: `origin/funddisclosure-current-stage-source-truth`
- Output file: `docs/reviews/funddisclosuredocument-core-risk-source-truth-extraction-aggregate-deepreview-ds-20260620.md`
- Included scope: committed range `origin/funddisclosure-current-stage-source-truth..HEAD` (commits `75cd23d` plan, `8332595` implementation); 16 files changed across production code, tests, docs, and review artifacts
- Excluded scope: untracked docs files not part of this work unit; contracts.py / active_annual.py / production data_extractor.py (confirmed unchanged by git diff); repository/source/cache/parser/Docling/pdfplumber/Provider/LLM/Service/UI/Host/renderer/quality gate (unchanged)
- Accepted plan: `docs/reviews/funddisclosuredocument-core-risk-source-truth-extraction-plan-20260620.md`
- Implementation evidence: `docs/reviews/funddisclosuredocument-core-risk-source-truth-extraction-implementation-evidence-20260620.md`
- Code review artifacts input: `docs/reviews/code-review-core-risk-source-truth-ds-20260620.md` (DS, CODE_REVIEW_PASS), `docs/reviews/code-review-core-risk-source-truth-mimo-20260620.md` (MiMo, CODE_REVIEW_PASS)
- Parallel review coverage: 无；本 aggregate review 由主 reviewer 独立执行全量交叉验证，不使用 subagent

## Aggregate Review Method

本 aggregate deepreview 执行以下交叉验证：

1. 逐项验证 plan → implementation 的完整一致性，包括 public contract、deferred roles、fail-closed semantics、forbidden scope
2. 逐项验证两个 code review 的每个 verification item 是否可被代码直接证据复现
3. 独立走读关键 source-truth admission chain、core_risk extractor call chain、neutral helper refactoring、product_essence preservation、candidate_evidence suppression、deferred_role gaps、ambiguity handling、facade fallback
4. 检查两个 code review 之间是否存在冲突结论
5. 检查是否存在 code review 未能覆盖的 material risk
6. 判断 CODE_REVIEW_PASS 是否可被独立证据支撑

## Plan/Implementation/Review Consistency Verification

### 1. Public contract: exact value shape

Plan 要求 `core_risk.v1` value 只含 `schema_version` 和 `risk_characteristic_text`，且 `risk_characteristic_text.v1` 形状与既有 `product_essence.v1` 中的形状完全一致。

实现验证：`_build_core_risk_value()` (line ~4700) 构造 `{"schema_version": "core_risk.v1", "risk_characteristic_text": _build_risk_characteristic_text_value(...)}`。`_build_risk_characteristic_text_value()` (line ~4521) 产出精确的既有形状 `{"schema_version": "risk_characteristic_text.v1", "fund_code": ..., "report_year": ..., "risk_characteristic_text": ..., "source_anchors": [...]}`。测试 `test_core_risk_source_truth_extracts_risk_characteristic_text_only` 逐字段断言 value shape 精确匹配预期。

**一致。** 两个 code review 的逐项验证记录（DS §4, MiMo §Neutral risk-characteristic helper correctness）可直接被代码证据复现。

### 2. Deferred roles: four required=False gaps

Plan 要求 `_CORE_RISK_DEFERRED_ROLES` 包含 `liquidation_or_scale_risk`、`tracking_error_or_deviation_risk`、`turnover_or_style_drift_risk`、`concentration_risk`，每个以 `required=False` 的 `deferred_role` gap 暴露。

实现验证：`_CORE_RISK_DEFERRED_ROLES` (line ~64) 定义为 `("liquidation_or_scale_risk", "tracking_error_or_deviation_risk", "turnover_or_style_drift_risk", "concentration_risk")`。`_core_risk_source_truth_gaps()` (line ~4777) 在 value 非空时 `gaps.extend(FundExtractionGap(gap_code="deferred_role", required=False, ...) for role in _CORE_RISK_DEFERRED_ROLES)`。测试验证 gaps 包含四个 deferred_role，全部 `required=False`，forbidden keys 不在 value 中。

**一致。**

### 3. Candidate evidence suppression

Plan 要求 direct route（含 direct missing）的 `candidate_evidence` 始终为空元组。

实现验证：`_extract_core_risk_source_truth()` 的 `return FundFieldFamilyResult(..., candidate_evidence=())` 无条件返回空元组 (line ~1224)。`_field_families_for_intermediate()` 中 `core_risk_evidence = () if core_risk_source_truth is not None else ...` (line ~1051)，因为 extractor 始终返回非 None，direct route 的 candidate_evidence 始终为空。测试 `test_core_risk_source_truth_direct_missing_suppresses_candidate_evidence` 和 `test_core_risk_source_truth_candidate_tokens_do_not_leak_on_direct_route` 独立验证。

**一致。**

### 4. Fail-closed semantics

Plan 要求 proof-missing/proof-invalid/candidate-boundary/missing-provenance/failure-class 全部保持 fail-closed，不产出 public values 或 anchors。

- **Proof missing**: `_validate_source_truth_admission()` 返回 `source_truth_admission_missing` → `source_truth_extraction_allowed=False` → `_extract_core_risk_source_truth()` 不执行 → `core_risk_source_truth is None` → 走 `_select_core_risk_candidate_evidence()` 分支 → candidate evidence 保留。测试 `test_core_risk_source_truth_requires_positive_proof` 验证。
- **Proof invalid**: 同上，返回 `source_truth_admission_invalid`。测试 `test_core_risk_source_truth_rejects_invalid_proof` 验证。
- **Candidate boundary**: `candidate_boundary is not None` → upstream `source_truth_extraction_allowed=False` → 同上路径。测试 `test_core_risk_source_truth_candidate_boundary_remains_blocked` 验证 `result.contract_status == "blocked"`。
- **Missing provenance / failure class**: 上游 admission layer 已拦截，不进入 family-level extraction。现有 admission-layer 测试覆盖。

**一致。**

### 5. Neutral risk-characteristic helper refactoring

Plan 要求提取中性 helper：`_collect_risk_characteristic_table_candidates`、`_collect_risk_characteristic_paragraph_candidates`、`_select_risk_characteristic_value`，仅收集 `risk_characteristic_text.risk_characteristic_text` 单一 output path。`_select_product_essence_values` 对 risk-characteristic 路径委托给 `_select_risk_characteristic_value`，其余路径保持原有逻辑。

实现验证：
- `_select_risk_characteristic_value()` (line ~3779) 仅调用 `_collect_risk_characteristic_table_candidates` / `_collect_risk_characteristic_paragraph_candidates`，只收集 `_RISK_CHARACTERISTIC_OUTPUT_PATH`
- `_select_product_essence_values()` (line ~3751) 对 `_RISK_CHARACTERISTIC_OUTPUT_PATH` 路径调用 `_select_risk_characteristic_value()` 并包装结果，其余路径走原有 `_collect_product_essence_table_candidates` / `_collect_product_essence_paragraph_candidates`
- 原有 table/paragraph collectors 显式跳过 `_RISK_CHARACTERISTIC_OUTPUT_PATH`（`_match_product_essence_cell_output_path` 和 `_collect_product_essence_paragraph_candidates` 中增加 `if output_path == _RISK_CHARACTERISTIC_OUTPUT_PATH: continue`）
- `_build_risk_characteristic_text_value()` 被 `product_essence` 和 `core_risk` 共享调用
- Focused product_essence 测试 25 passed 确认 shape 兼容

**一致。** 这是计划中最敏感的 refactoring，已通过独立 focused 测试验证。

### 6. Non-interference

Plan 要求 `product_essence.v1`、`return_attribution.v1`、`manager_profile.v1`、`investor_experience.v1`、`current_stage.v1` 不因新增 core_risk extraction 而改变行为。

实现验证：
- 188 processor tests 全量通过（新增 core_risk tests + 修改的 existing tests + 所有未修改的 existing tests）
- 25 product_essence focused tests 通过
- 修改的 existing tests（`test_investor_experience_source_truth_does_not_pollute_stage_or_core_risk`、`test_current_stage_source_truth_does_not_project_core_risk_section_locator`、`test_product_essence_source_truth_extracts_exact_value_shape`）的 assert 变更是因为 core_risk 现在也产出 direct value，而非其他家族行为变化

**一致。**

### 7. Forbidden scope

Plan 明确禁止修改：`contracts.py`、`active_annual.py`、production `data_extractor.py`、`docs/fund-analysis-template-draft.md`、repository/source/cache/parser、Docling/pdfplumber、Service/UI/Host/Agent、renderer、quality gate、template。

实现验证：`git diff origin/funddisclosure-current-stage-source-truth..HEAD -- fund_agent/fund/processors/contracts.py fund_agent/fund/processors/active_annual.py fund_agent/fund/data_extractor.py` 无输出。所有改动限定在允许的文件集合内（processor、tests、docs）。

**一致。**

### 8. Docs truth sync

Plan Slice 5 要求更新 `docs/design.md`、`docs/implementation-control.md`、`docs/current-startup-packet.md`、`fund_agent/fund/README.md`，且必须：
- 声明 `core_risk.v1` 只覆盖 `risk_characteristic_text`
- 声明其他 risk roles 保持 candidate-only/deferred
- 声明 `deferred_role` gaps
- 声明 `candidate_evidence` 为空
- 不声明完整 core_risk source truth、parser replacement、readiness/release

实现验证：四个文档均按计划更新。`docs/design.md` v2.32→v2.33 变更摘要明确 "仅覆盖 risk_characteristic_text"。`docs/implementation-control.md` truth guardrails 增加 "core_risk.v1 仅覆盖 risk_characteristic_text，完整核心风险 source truth 仍 deferred"。`fund_agent/fund/README.md` 三处更新均保持 deferred/candidate-only 口径。无文档声明 parser replacement、readiness、release。

**一致。**

### 9. Code review cross-consistency

两个 code review（DS 和 MiMo）均报告 `未发现实质性问题`，均给出 `CODE_REVIEW_PASS`。两者的 verification items 覆盖相同的核心检查点（source-truth admission、candidate_boundary fail-closed、no product_essence leakage、neutral helper correctness、product_essence shape preservation、candidate_evidence suppression、deferred_role gaps、ambiguity behavior、facade fallback、docs truth、forbidden scope、test coverage），无冲突结论。两个 review 的 open questions 均为 `无`，residual risk 一致指向完整 core_risk source truth deferred、不证明 real-report correctness/parser replacement/readiness/release。

**无冲突。**

### 10. Independent adversarial failure pass

主 reviewer 独立执行以下 adversarial check：

- **Auth/permissions/tenant isolation**: 不适用——本 gate 只操作处理器内部字段族提取逻辑，不涉及 auth 或 tenant。
- **Data loss/corruption**: `_core_risk_status()` 二元 `accepted|missing` 模型在单 subvalue 场景下不会产生误判。value 为空时返回 `missing`，锚点为空元组，不存在半提交状态。
- **Race conditions/ordering**: 处理器为纯函数风格（输入 intermediate → 输出 result），无共享可变状态。
- **Empty/null/timeout/cancellation**: `_resolve_risk_characteristic_candidate` 对空 candidates 返回 None → value={} → status=missing → anchors=()。`_build_core_risk_value` 对空 selected_values 返回 {}。`_core_risk_emitted_output_paths` 双重守卫（value 有 key 且 selected_values 有 path）防止 anchors 在无值时有非空锚点。
- **Duplicate requests/conflicting params**: 不适用。
- **Version skew/schema drift**: 未修改 `contracts.py` 的 `FundFieldFamilyId` 或 schema version 定义。
- **Observability gaps**: gaps 机制完整：missing 时 `field_family_missing`，ambiguity 时 `ambiguous_table_or_locator`，accepted 时 `deferred_role`×4。
- **External protocol/API boundary**: 未修改 public `EvidenceAnchor` 或 `EvidenceSourceKind`。
- **Overcoupling**: neutral helper 提取将 `product_essence` 和 `core_risk` 共享 `_select_risk_characteristic_value` 和 `_build_risk_characteristic_text_value`。这两个函数是家族中立的——它们仅收集/构造 `risk_characteristic_text` 值，不携带 product_essence 或 core_risk 的身份语义。对 label 集合的修改会同时影响两个家族，但这是 `_PRODUCT_ESSENCE_LABELS[_RISK_CHARACTERISTIC_OUTPUT_PATH]` 的共享配置问题，不是代码耦合问题。两个家族对 risk-characteristic 有同一语义定义，共享配置是正确的。
- **Test gaps**: 见下方 Residual Risk。

## Findings

未发现实质性问题。

### 交叉验证记录

以下 10 项 plan/implementation/review consistency 检查均通过，基于代码直接证据：

1. **Source-truth admission chain intact**: `_validate_source_truth_admission()` 校验 proof identity 六字段三方一致性；`candidate_boundary is not None` → `source_truth_admission_invalid`；`failure_class is not None` → `source_truth_admission_invalid`；`source_provenance is None` → `source_truth_admission_invalid`。proof missing 返回 `source_truth_admission_missing`。全部校验通过后方可进入 direct extraction。

2. **candidate_boundary fail-closed**: `candidate_boundary is not None` 直接映射为 `source_truth_admission_invalid`，导致 `source_truth_extraction_allowed=False`。测试验证 `result.contract_status == "blocked"`。

3. **No `_select_product_essence_values` call from core_risk**: `_select_core_risk_values` → `_select_risk_characteristic_value` → `_collect_risk_characteristic_table_candidates` / `_collect_risk_characteristic_paragraph_candidates` / `_resolve_risk_characteristic_candidate`。无调用 `_select_product_essence_values` 或任何 product-essence-specific 函数。

4. **Neutral risk-characteristic helper correctness confirmed**: `_select_risk_characteristic_value` 仅收集 `risk_characteristic_text.risk_characteristic_text` 单一 output path，使用 `_PRODUCT_ESSENCE_LABELS[_RISK_CHARACTERISTIC_OUTPUT_PATH]` 做 label 匹配，返回家族中立类型 `_RiskCharacteristicValueCandidate`。

5. **product_essence shape preservation confirmed**: `_select_product_essence_values` 对 risk-characteristic 路径委托给 neutral helper 并包装为 `_ProductEssenceValueCandidate`，其余路径保持原逻辑。`_build_risk_characteristic_text_value` 产出精确既有形状。focused 测试 25/25 通过。

6. **Direct candidate_evidence suppression confirmed**: `_extract_core_risk_source_truth` 始终返回 `candidate_evidence=()`。`core_risk_evidence = () if core_risk_source_truth is not None`。direct route（含 direct missing）candidate_evidence 始终为空。

7. **Four required=False deferred_role gaps confirmed**: `_CORE_RISK_DEFERRED_ROLES` 精确包含四个 deferred roles。`_core_risk_source_truth_gaps` 在 value 非空时追加四个 `required=False` deferred_role gaps，不携带 candidate evidence。

8. **Ambiguity behavior confirmed**: `_resolve_risk_characteristic_candidate` 对多个不同归一化值的候选 → `ambiguous_paths.add(...)` → 返回 None。`_core_risk_source_truth_gaps` 输出 `ambiguous_table_or_locator` gap。value 为空时不追加 `field_family_missing`（由 ambiguity gap 替代）。

9. **Facade fallback without production edit confirmed**: `git diff -- fund_agent/fund/data_extractor.py` 无输出。既有 fallback 逻辑未修改。Facade 测试验证 fallback 行为正确，product_essence 优先。

10. **Validation adequacy confirmed**: 188 processor tests pass（含 7 new + 2 renamed/modified）；25 product_essence focused tests pass（refactoring verification）；42 facade tests pass（含 2 new）；ruff all clean；git diff --check pass。

## Open Questions

无。

## Residual Risk

- 完整 `core_risk.v1` source truth（四个 deferred roles 的 public values/anchors）仍需后续独立 gate。Owner: future core_risk multi-subvalue public contract gate。
- 本 gate 不证明 real-report correctness、parser replacement、field correctness、golden/readiness 或 release。Owner: separate evidence/readiness gates。
- `_core_risk_status()` 的二元 `accepted | missing` 模型在后续 multi-subvalue gate 中必须重新设计。Owner: later multi-subvalue core_risk gate。
- neutral risk-characteristic helper 的 label 集合 `_PRODUCT_ESSENCE_LABELS[_RISK_CHARACTERISTIC_OUTPUT_PATH]` 同时服务于 product_essence 和 core_risk 两个家族，修改该 label 集合会影响两个家族的提取行为。当前共享是正确的（两家族对 risk-characteristic 有同一语义定义），但后续若两个家族的 risk-characteristic 提取语义需要分化，需要解耦 label 配置。
- 两个 code review 均未覆盖 facade projection 路径的边界条件：当 `product_essence.v1` 的 `risk_characteristic_text` 存在但值为空字符串时的 fallback 优先级行为。当前 production `data_extractor.py:742-754` 的既有 fallback 检查 `product_essence_risk_text` truthiness，空字符串会被视为 falsy 从而触发 fallback，这是现有行为的延续，不是本 gate 新增风险。
- 两个 code review 均标记 `未发现实质性问题`，与本 aggregate review 的独立验证结论一致。

## Verdict

AGGREGATE_DEEPREVIEW_PASS
