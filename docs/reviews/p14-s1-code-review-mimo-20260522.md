# Code Review

## Scope

- Mode: current changes
- Branch: `docs/post-p13-follow-up-planning`
- Base: `main`
- Output file: `docs/reviews/p14-s1-code-review-mimo-20260522.md`
- Included scope: P14-S1 implementation diff — `fund_agent/fund/extraction_score.py`、`fund_agent/fund/extraction_snapshot.py`、`fund_agent/fund/golden_prefill.py`、`reports/golden-answers/`、`docs/golden-answer-template.md`、`tests/fund/test_extraction_snapshot.py`、`tests/fund/test_extraction_score.py`、`tests/fund/test_golden_prefill.py`、`tests/fund/test_quality_gate.py`、`tests/fund/integration/test_p1_sample_matrix.py`、`fund_agent/fund/README.md`、`tests/README.md`
- Excluded scope: `docs/repo-audit-20260521.md`（按 plan 约束排除）
- Parallel review coverage: 无

## Findings

### 001-未修复-低-`_value_mapping` helper 在 snapshot 和 golden_prefill 中重复定义

- **入口/函数**: `extraction_snapshot.py:_value_mapping()` 与 `golden_prefill.py:_value_mapping()`
- **文件(行号)**: `fund_agent/fund/extraction_snapshot.py:1060-1075`、`fund_agent/fund/golden_prefill.py:338-353`
- **输入场景**: 任何包含 dataclass `ExtractedField.value` 的 snapshot 或 golden prefill 路径
- **实际分支**: 两个模块各自实现了一份 `_value_mapping()`，逻辑完全相同（`None -> None`、`Mapping -> return`、`is_dataclass -> asdict`）
- **预期行为**: 共享逻辑应抽取为单一定义点，避免后续修改时漂移
- **实际行为**: 两处独立定义，未来修改其中一处可能忘记同步另一处
- **直接证据**: `extraction_snapshot.py:1060` 和 `golden_prefill.py:338` 的函数签名和实现体完全一致
- **影响**: 仅 maintainability；当前行为正确，不会导致 incorrectness
- **建议改法和验证点**: 后续 refactor 可将 `_value_mapping` 抽取到 `fund_agent/fund/extractors/_field_utils.py` 或类似共享位置；当前 slice 不需要修改，因 plan 要求最小化跨模块变更
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

### 002-未修复-信息-生产 golden 001548 confidence 从 plan 的 medium 提升为 high

- **入口/函数**: golden answer JSON 中 001548 `index_profile` 4 条记录
- **文件(行号)**: `reports/golden-answers/golden-answer.json`、`reports/golden-answers/golden-answer-prefill-reviewed.md`
- **输入场景**: 001548 index_profile golden rows
- **实际分支**: 4 条记录的 `confidence` 均为 `"high"`
- **预期行为**: plan 规定 `medium` confidence，除非实现者验证 exact PDF pages 并可安全 promote to `high`
- **实际行为**: 实现者已验证 reviewed markdown 中 001548 的 §2 benchmark evidence，选择提升到 `high`；golden-answer-prefill-reviewed.md 中的 source 和 expected_value 与 reviewed evidence 一致
- **直接证据**: plan 第 4 节 "Values are `medium` confidence unless implementer verifies exact PDF pages and can safely promote to `high`"；reviewed markdown 中 001548 的 benchmark 行标注 `high`，source 指向 `年报2024 §2 page-6 page-6-table-0 benchmark`
- **影响**: 无 incorrectness 风险；confidence 提升有 reviewed evidence 支撑
- **建议改法和验证点**: 无需修改；实现者已在 implementation artifact 中记录该决策
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低（信息）

## Findings Disposition Summary

| # | Severity | Status | Description |
|---|---|---|---|
| 001 | 低 | 未修复 | `_value_mapping` 重复定义 |
| 002 | 信息 | 未修复 | 001548 confidence medium→high |

两个 finding 均不阻断 merge。001 是 maintainability 建议，可在后续 refactor slice 处理。002 是 plan 内允许的实现者裁决，有 reviewed evidence 支撑。

## Open Questions

- 无。

## Residual Risk

### RR-P14-1: tracking_error 生产 golden 缺失

Plan 明确记录 `tracking_error` 不加入 001548 生产 golden，因为当前 reviewed artifact 中未验证 direct tracking-error value。当前 tracking_error correctness 仅由单元测试和 sample matrix 覆盖。未来如需生产级 tracking_error golden correctness，需先完成 reviewed evidence 验证。

### RR-P14-2: enhanced_index 生产 golden 缺失

Plan 明确记录 enhanced_index 不写入生产 golden answer，因当前无 selected-fund / strict-golden enhanced-index fixture。161725 仅通过 deterministic fixture 覆盖。未来 selected-fund 扩展时需补充。

### RR-P14-3: `_value_mapping` helper 重复

如上 finding 001 所述，两处独立定义存在维护漂移风险。建议后续 refactor 统一。

## Verification Summary

### Lens 1: index_profile / tracking_error 条件进入 FQ2 / snapshot score / fund score / fund quality denominator

**PASS**。

- `FIELD_PRIORITY_BY_NAME` 新增两条 P1 条目：`extraction_score.py:48-49`。
- `_scorable_records()` 过滤逻辑：非指数基金的 `index_profile` / `tracking_error` 被排除；`index_fund` / `enhanced_index` 保留；unknown/missing/conflicting fund_type 保守保留（`extraction_score.py:1371-1400`）。
- `score_snapshot_records()` 使用 `_scorable_records(records)`（记录级 fallback）：`extraction_score.py:542`。
- `_build_fund_score_row()` 使用 `_scorable_records(records)`（记录级 fallback）：`extraction_score.py:1113`。
- `_build_fund_quality_row()` 先通过 `_unique_optional_text` 解析 `classified_fund_type`，再传入 `_scorable_records(records, classified_fund_type=..., use_record_fund_type=False)`：`extraction_score.py:1222-1226`。
- `_missing_fields_by_priority()` 接收已过滤的 scorable_records 和已解析的 classified_fund_type：`extraction_score.py:1227-1231`。
- 测试覆盖：`test_index_quality_fields_are_p1_only_for_applicable_fund_types` 覆盖 active_fund、index_fund、enhanced_index、unknown（empty string）四条路径。

### Lens 2: 数据流一致性（score_snapshot_records → _build_fund_score_row → _build_fund_quality_row → _missing_fields_by_priority → _scorable_records）

**PASS**。

- `_build_fund_quality_row` 先解析 `classified_fund_type`（通过 `_unique_optional_text`），再过滤 scorable_records，最后传入 `_missing_fields_by_priority`。数据流与 plan 要求一致。
- conflicting `classified_fund_type` 时 `_unique_optional_text` 返回 `None`；`_scorable_records(classified_fund_type=None, use_record_fund_type=False)` 进入 `_is_non_applicable_index_quality_record`，`fund_type=None` → `return False`（不排除，保守评分）。符合 plan "conflicting type 保守可评分" 约束。
- `_build_fund_score_row` 使用记录级 fallback（`use_record_fund_type=True`），单基金场景下所有记录的 `classified_fund_type` 应一致，行为正确。
- 测试 `test_derive_fund_quality_records_marks_conflicting_fund_type_without_first_row` 验证 conflicting type 场景下 `missing_p1_fields == ("index_profile",)`。

### Lens 3: ExtractionMode 未扩展；not_applicable 未伪装成 extraction mode

**PASS**。

- `ExtractionMode` 保持 `Literal["direct", "derived", "estimated", "missing"]` 不变。diff 中无对 `extractors/models.py` 的修改。
- 非适用性通过 `classified_fund_type` + 适用性矩阵在 quality 层表达，不在 extractor model 层。

### Lens 4: comparable subfields 稳定、标量、bool 序列化、dataclass/dict 路径一致

**PASS**。

- `COMPARABLE_SUB_FIELDS_BY_FIELD` 新增 `index_profile`（7 子字段）和 `tracking_error`（10 子字段），均为稳定标量字段：`extraction_snapshot.py:57-80`。
- `_value_mapping()` 统一处理 dict 和 dataclass 值：`extraction_snapshot.py:1060-1075`。
- `_comparable_scalar()` 保持原有 bool→`"True"`/`"False"` 序列化行为。
- 测试 `test_build_snapshot_records_serializes_index_quality_dataclass_comparable_values` 验证 `annualized: "True"`、`input_period_complete: "False"` 序列化正确。
- 测试 `test_compare_snapshot_correctness_handles_index_quality_comparable_fields` 验证 `tracking_error.annualized` golden 期望 `"True"` 与 fixture `"False"` 触发 `CORRECTNESS_MISMATCH`，证明 bool comparable 进入 correctness 比对。

### Lens 5: golden_prefill 对 dataclass ExtractedField 支持；001548 index_profile golden 基于已审证据

**PASS**。

- `golden_prefill.py` 的 `_field_from_bundle()`、`_sub_field_value()`、`_anchor_for_sub_field()`、`_confidence_for_value()` 签名从 `ExtractedField[dict[str, object]]` 放宽为 `ExtractedField[object]`，新增 `_value_mapping()` 处理 dataclass。
- 测试 `test_run_golden_prefill_writes_prefilled_markdown` 使用包含 `IndexProfileValue` 和 `TrackingErrorValue` dataclass 的 fake extractor，验证 `index_profile.benchmark_index_name`、`tracking_error.annualized`、`tracking_error.value_text` 正确预填。
- 001548 生产 golden 新增 4 条 `index_profile` 记录（`benchmark_text`、`benchmark_identity_status`、`benchmark_index_name`、`source_tier`），source 均指向 `年报2024 §2 page-6 page-6-table-0 benchmark`，与 reviewed evidence 一致。
- 未引入未验证的 `tracking_error` 生产 golden（符合 plan stop condition）。
- `golden-answer.json` record_count 从 121 增至 125（+4 条 001548 index_profile），fund_count 保持 6。

### Lens 6: enhanced_index fixture 覆盖 index_profile 和 tracking_error；sample matrix assertions 证明行为

**PASS**。

- `test_p1_sample_matrix.py` 新增 `161725`（指数增强）样本：`_build_report()` 构造包含 `基金名称：样本沪深300指数增强基金161725`（触发 enhanced_index 分类）、`§2` benchmark text 和 `§3 报告期年化跟踪误差：1.23%`。
- assertions 覆盖：
  - `161725.classified_fund_type == "enhanced_index"`（`test_p1_sample_matrix.py:284`）
  - `161725.index_profile.extraction_mode == "direct"`（`test_p1_sample_matrix.py:285`）
  - `161725.tracking_error.extraction_mode == "direct"`（`test_p1_sample_matrix.py:286`）
  - `510300.tracking_error.extraction_mode == "direct"`（保持原有）
  - `110011`/`000171` tracking_error 为 `missing`（`test_p1_sample_matrix.py:287-288`）
- passed_cells 从 38 更新为 52（新增 161725 的 14 个 passed cells）。

### Lens 7: 边界合规（FundDocumentRepository、Dayu、extra_payload、分层）

**PASS**。

- 未引入直接 PDF/cache/source 访问。所有变更在 Capability 层 `extraction_score.py`、`extraction_snapshot.py`、`golden_prefill.py` 内。
- 未引入 Dayu runtime、Host、Engine 或 tool loop。
- 未使用 `extra_payload` 传递参数。
- 未修改 Service/UI/API contract 文件。
- 未触碰 `docs/design.md`、`docs/implementation-control.md`、root `README.md`、source CSV 或 RR-13 数据。

### Lens 8: 文档同步符合 AGENTS.md

**PASS**。

- `fund_agent/fund/README.md` 更新 snapshot 和 golden prefill 行为描述，反映 conditional P1 denominator 和 dataclass 支持。
- `tests/README.md` 更新 snapshot/score/golden prefill 测试描述，反映 P14-S1 覆盖范围。
- 未修改 root `README.md`（无用户入口变更）。
- 未修改 `docs/design.md`（无架构变更）。

## Conclusion

**PASS**

P14-S1 implementation 正确实现了 approved plan 的所有 slice。`index_profile` 和 `tracking_error` 作为条件 P1 字段，仅对 `index_fund` / `enhanced_index` 进入质量分母；非指数基金被排除；unknown/conflicting fund type 保守可评分。`ExtractionMode` 未扩展。comparable subfields 稳定、标量、bool 序列化正确。golden prefill 支持 dataclass，001548 生产 golden 基于已审证据。enhanced_index fixture 覆盖 index_profile 和 tracking_error。未发现阻断 finding。两个低严重度 finding（`_value_mapping` 重复定义、confidence 提升）不阻断 merge。
