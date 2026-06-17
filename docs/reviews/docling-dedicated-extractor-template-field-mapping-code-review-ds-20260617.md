# Docling Dedicated Extractor Template-field Mapping — Code Review (AgentDS)

**Gate**: `Docling Dedicated Extractor Template-field Mapping No-live Implementation Gate`
**Reviewer**: AgentDS
**Date**: 2026-06-17
**Reviewed files**:
- `fund_agent/fund/documents/candidates/template_field_extraction.py`
- `tests/fund/documents/test_docling_template_field_extraction.py`
- `docs/reviews/docling-dedicated-extractor-template-field-mapping-implementation-evidence-20260617.md`

**Verdict**: `CODE_REVIEW_PASS_NOT_READY`

---

## 1. Candidate-only / source_truth_status Boundary

### 1.1 输出面边界 — PASS

所有输出 dataclass 均强制 `candidate_only=True`、`source_truth_status="not_proven"`，且通过 `__post_init__` 做 fail-closed 校验：

- `CandidateTemplateField.__post_init__`（`:139-159`）：`candidate_only is not True` → `ValueError`；`source_truth_status != "not_proven"` → `ValueError`。
- `DoclingTemplateFieldExtractionResult.__post_init__`（`:188-206`）：同上。
- 所有构造路径（`extract_docling_template_fields`、`_missing_field`、`_extract_single_field`）均硬编码 `candidate_only=True, source_truth_status="not_proven"`，无动态通路可越界。

### 1.2 输入面边界 — PASS

`_validate_document`（`:266-288`）逐字段校验 `CandidateRepresentationStatus` 的五个 proof 字段，`source_truth_status`、`field_correctness_status`、`candidate_status` 必须为 `not_proven`，`production_parser_replacement_status` 必须为 `not_authorized`。非 Docling source 直接 `ValueError`。

### 1.3 锚点边界 — PASS

`CandidateTemplateFieldAnchor` 是独立 candidate-only dataclass，note 字段前缀 `candidate_only:`，不引用、不构造、不返回生产 `EvidenceAnchor`。本模块无 `EvidenceAnchor` import。

**Finding 1 (non-blocking)**：`CandidateTemplateFieldAnchor.note` 字段当前是自由字符串，未在 `__post_init__` 中校验 `candidate_only:` 前缀。若未来有人构造 `CandidateTemplateFieldAnchor` 时遗漏此前缀，不会触发 fail-closed。建议在 `CandidateTemplateFieldAnchor.__post_init__` 加 `note.startswith("candidate_only:")` 断言。当前所有构造点均走 `_anchor_for_cell` / `_anchor_for_text_block` 两个辅助函数，两者均硬编码此前缀，因此当前风险不构成 blocking。

---

## 2. 生产 EvidenceAnchor 隔离 — PASS

全模块无 `EvidenceAnchor` 导入、无 `FundDataExtractor` 导入、无 parser replacement 逻辑。`extract_docling_template_fields` 只消费 `CandidateRepresentationDocument`，不消费 `CandidateEvidenceAnchorMappingResult`。

确认：无生产 EvidenceAnchor 提升通路。

---

## 3. FundDataExtractor / Parser Replacement 隔离 — PASS

模块不 import `FundDataExtractor`，不调用 `extract()` 或任何生产 parser。边界确认与 evidence doc 一致。

---

## 4. 精确一字段一路径 / Missing 语义

### 4.1 一一对应 — PASS

`extract_docling_template_fields`（`:240`）对 `target_field_paths` 逐条调用 `_extract_single_field`，每条路径必然产生恰好一个 `CandidateTemplateField`。测试 `test_docling_template_field_extractor_emits_one_candidate_field_per_default_path` 验证 `len(result.fields) == len(DEFAULT_DOCLING_TEMPLATE_FIELD_PATHS)` 且 `field_path` 集合完全匹配。

### 4.2 Missing 语义 — PASS

未匹配路径通过 `_missing_field` 构造 `extraction_mode="missing"`、`value=None`、`anchors=()` 的显式缺失字段。Deferred 字段使用稳定 note 码（如 `docling_template_field_deferred_manager_strategy_text`），非 deferred 字段使用 `docling_template_field_missing:{field_path}`。测试验证 4 个 deferred 路径全部显式 missing。

### 4.3 Blocked 语义

`blocked_field_paths` 通过 note 前缀 `blocked:` 识别（`:242-246`）。但当前代码中没有任何匹配函数设置 `blocked:` note。`_DEFERRED_FIELD_NOTES` 的值以 `docling_template_field_deferred_` 开头，不是 `blocked:`。当前 `blocked_field_paths` 在所有场景下均为空 tuple。

**Finding 2 (non-blocking)**：`blocked_field_paths` 机制已设计但无生产通路。这本身不是问题（属于未来预留），但 `diagnostics` 中 `blocked_field_count` 当前始终为 0，可能让后续 gate 误以为 blocked 逻辑已经过测试验证。建议在 evidence 中显式标注 "blocked 语义已预留但当前没有触发路径"。

---

## 5. 字段匹配正确性与 Fail-Closed 行为

### 5.1 键值字段匹配 — PASS

`_match_key_value_field` 先尝试表格匹配（`_match_key_value_table_field`），再 fallback 文本匹配（`_match_text_label_field`）。表格匹配使用 `_normalize_text` 做标签比对，值单元格通过 `_find_value_cell` 取同行第一个非标签非空单元格。文本匹配用 `_value_after_label` 正则截取标签后的值。

### 5.2 业绩字段匹配 — PASS

`_match_performance_field` 同时要求 column_header_path 含目标标签且 row_label_path 含"过去一年/报告期"等时间标签，避免误采信其他时间窗口。测试验证了 `nav_growth_rate=12.34%`、`benchmark_return_rate=10.00%`。

### 5.3 跟踪误差 fail-closed — PASS

`_match_tracking_error` 的拒绝/接受关键词机制正确：
- 含"控制在/不超过/力争/争取/目标/限制/最小化"→ 拒绝（目标/限制性表述）
- 不含"实际/报告期/本报告期/过去一年"→ 拒绝（无实际披露语义）
- 不含百分数 → 拒绝

测试 `test_docling_template_field_extractor_rejects_tracking_error_target_text` 验证"力争将跟踪误差控制在 4.00%以内"被正确拒绝为 missing。

### 5.4 基金经理匹配

`_match_portfolio_managers` 在 §4 表格中查找姓名+任职日期行，过滤表头行（name 为"姓名"/"基金经理"时跳过）。返回结构化 `portfolio_manager_tenure_list.v1` schema。测试单行覆盖。

### 5.5 持仓匹配 — 仅返回第一行

`_match_holding_row` 遍历 §8 表格，但找到第一个满足 `required_labels` 上下文的行后即返回，不收集后续行。

**Finding 3 (material, non-blocking for current slice)**：`holdings_snapshot.top_holdings` / `bond_top_holdings` / `target_fund_holdings` 只返回第一行，不返回 Top N。字段名含"holdings"（复数）和"top"，暗示应返回多条记录，但当前 `{"rows": (value,)}` 是单元素 tuple。证据文档承认"首行候选字段"。当前 slice 定位为 candidate-only 首行验证，不构成 blocking，但应在 residual risk 中显式标注此限制，避免后续 gate 误以为已实现完整的 Top N 持仓抽取。

### 5.6 输入校验 fail-closed — PASS

`_validate_target_field_paths`（`:291-310`）对空路径、重复路径、不在 `DEFAULT_DOCLING_TEMPLATE_FIELD_PATHS` 中的路径全部 `ValueError`。`_validate_document` 覆盖 source kind 和全部 5 个 status 字段。

### 5.7 字段组派生

`_field_group`（`:743-769`）按 root key 分派。`turnover_rate` 归入 `manager` 组（`:761`），但其语义上属于组合/交易特征而非基金经理信息。对当前 candidate-only 阶段影响有限，但在 future gate 如需按字段组做差异化处理时可能需要重新审视。

**Finding 4 (non-blocking)**：`turnover_rate` 归入 `manager` 组而非独立 `operations` 组。当前只影响 `field_group` 标签，不影响抽取逻辑。建议在 field group 映射表中显式记录此归类决策。

---

## 6. 测试覆盖

### 6.1 已覆盖 — PASS

| 场景 | 测试 |
|------|------|
| 每个 default path 恰好一个输出 | `test_..._emits_one_candidate_field_per_default_path` |
| Profile/fee/performance 表格映射 | `test_..._maps_profile_fee_and_performance_fields` |
| Tracking/manager/holdings 映射 | `test_..._maps_tracking_manager_and_holding_fields` |
| Deferred 路径显式 missing | `test_..._emits_explicit_missing_for_deferred_paths` |
| 非 Docling source 拒绝 | `test_..._rejects_non_docling_source` |
| Status 越界拒绝 | `test_..._rejects_status_claims` |
| Tracking error 目标文本拒绝 | `test_..._rejects_tracking_error_target_text` |

7 tests, all passing.

### 6.2 覆盖缺口

**Finding 5 (material, non-blocking)**：以下路径缺少显式测试：

1. **`_validate_target_field_paths` 的三个 fail-closed 分支**：空路径、重复路径、不在 DEFAULT 中的路径均无测试。
2. **文本 fallback 路径**：所有测试 fixture 都命中表格匹配，`_match_text_label_field` 未被测试覆盖。
3. **`turnover_rate` 字段**：DEFAULT 中有 `turnover_rate`，但无针对它的显式值验证测试。当前 fixture 不含 §8 换手率数据，`turnover_rate` 预期命中 missing 路径，但无测试断言其 missing 语义。
4. **`CandidateTemplateField.__post_init__` 的 direct-without-anchors 分支**：无测试直接构造非法 `CandidateTemplateField`。
5. **`DoclingTemplateFieldExtractionResult.__post_init__` 的 schema_version 校验**：无测试传入非法 schema_version。

这些缺口对当前 candidate-only slice 不构成 blocking，但在后续 gate 进入生产集成前需要补齐。

### 6.3 单文件覆盖率估算

新增模块 `template_field_extraction.py` 约 320 行（含 docstring），测试文件约 200 行。核心匹配函数（`_match_key_value_table_field`、`_match_text_label_field`、`_match_performance_field`、`_match_tracking_error`、`_match_portfolio_managers`、`_match_holding_row`）均有至少一条测试覆盖。`_validate_document` 的 fail-closed 分支覆盖率较高。文本 fallback、input validation edge cases 和 post_init guard 分支是主要缺口。粗略估计行覆盖率在当前 70-80% 区间，单文件 ≥80% 目标可能未达到，需后续 gate 补齐。

---

## 7. 代码质量

### 7.1 结构 — PASS

- 模块化清晰：公共 API（`extract_docling_template_fields` + dataclasses）→ 内部匹配分派（`_match_field`）→ 具体匹配器 → 工具函数。
- 无不必要的嵌套函数或嵌套类。
- 辅助函数均为模块级私有函数。
- 魔法字符串集中在模块顶部的 `Final` 常量字典中。

### 7.2 类型安全 — PASS

- 使用 `Literal` 约束 `CandidateTemplateExtractionMode`、`CandidateTemplateSourceTruthStatus`。
- 使用 `Final` 标记常量。
- 使用 `frozen=True, slots=True` dataclass。
- `from __future__ import annotations` 启用延迟求值。

### 7.3 一致性

**Finding 6 (non-blocking)**：字段路径命名风格不一致。`basic_identity.fund_name`、`fee_schedule.management_fee` 等使用 `snake_case.group_snake_case`，但 `portfolio_managers`、`turnover_rate`、`holder_structure`、`share_change` 使用裸 `snake_case` 无分组前缀。`tracking_error.value_text` 有分组但 `portfolio_managers` 没有（按模板应有 `management.portfolio_managers`）。当前对功能无影响，但后续 gate 如果要做路径 schema 验证或自动路由，这种不一致会增加复杂度。

---

## 8. Boundary Confirmation 复核

逐条对照 evidence doc 的 boundary claim：

| Claim | 代码验证 |
|-------|---------|
| 不修改 `FundDataExtractor` | 无 import，确认 |
| 不集成生产报告生成 | 无 Service/UI 依赖，确认 |
| 不改变 Service/UI/Host/renderer/quality-gate | 模块位于 `candidates/` 包内，确认 |
| 不直接访问 PDF/cache/source-helper | 只消费 `CandidateRepresentationDocument`，确认 |
| 不接受 source truth | 所有状态硬编码 not_proven，确认 |
| 不提升 Docling baseline | 无 baseline/golden 逻辑，确认 |
| 不替换生产 parser | 无 parser 引用，确认 |

Boundary claims 全部成立。

---

## 9. Residual Risks（本次 review 增补）

1. **Finding 3**：Holdings 只返回第一行，不是 Top N。后续 gate 需要实现多行收集。
2. **Finding 5**：输入校验分支、文本 fallback、turnover_rate 具体值、post_init guard 无测试覆盖。
3. **Finding 6**：字段路径命名一致性需在后续 schema 稳定性 gate 中解决。
4. Evidence doc 中 `residual risks` section 列出的风险（无 FundDataExtractor 消费、合成数据、数值归一化等）仍然有效。

---

## 10. 结论

实现严格遵循 candidate-only 边界：所有输出强制 `not_proven`，无 `EvidenceAnchor` 提升，无 `FundDataExtractor` 集成，无 parser 替换。字段匹配逻辑 fail-closed（拒绝非 Docling source、拒绝越界 status、拒绝跟踪误差目标文本）。每个 default 路径恰好一个输出，未匹配路径显式 missing。

测试覆盖核心成功路径和关键 fail-closed 场景，但存在输入校验分支、文本 fallback 和 turnover_rate 字段的覆盖缺口，以及 holdings 仅返回第一行的功能限制。这些对当前 candidate-only slice 不构成 blocking，但需在后续 gate 处理。

**VERDICT: `CODE_REVIEW_PASS_NOT_READY`**

不构成 blocking 的 findings 汇总：Finding 1（anchor note 前缀校验）、Finding 2（blocked 语义无生产通路）、Finding 3（holdings 单行限制）、Finding 4（turnover_rate group 归类）、Finding 5（测试覆盖缺口）、Finding 6（字段路径命名不一致）。
