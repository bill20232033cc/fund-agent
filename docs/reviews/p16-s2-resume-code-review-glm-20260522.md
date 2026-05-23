# P16-S2 Resume Code Review (AgentGLM)（2026-05-22）

## Verdict

`PASS`

## Review Scope

| File | Role |
|---|---|
| `reports/golden-answers/golden-answer-prefill-reviewed.md` | Reviewed golden Markdown（diff only） |
| `reports/golden-answers/golden-answer.json` | Strict JSON rebuild（diff only） |
| `tests/fund/test_golden_answer.py` | Golden row 验证测试 |
| `tests/fund/test_extraction_snapshot.py` | Composite snapshot 序列化测试 |
| `tests/fund/test_extraction_score.py` | Composite correctness match/mismatch 测试 |
| `tests/fund/test_quality_gate.py` | Composite FQ1 阻断测试 |
| `docs/reviews/p16-s2-index-profile-benchmark-context-golden-implementation-resume-20260522.md` | Implementation artifact |

Review truth sources: `docs/design.md`, `docs/implementation-control.md`, `docs/reviews/p16-s2-index-profile-benchmark-context-golden-implementation-plan-20260522.md`, `docs/reviews/p16-s2-plan-review-controller-judgment-20260522.md`, `docs/reviews/p16-s2-1-code-review-controller-judgment-20260522.md`.

Excluded: `docs/design0522.md`, `docs/implementation-control0522.md`, `docs/repo-audit-20260521.md`.

## Focus 1: Planned Rows Conformance

**结论：完全符合。**

Markdown diff 追加 5 个 `---` 分隔的小节，每只基金恰好 5 条 `index_profile` scalar rows：

| fund_code | subfields | 条数 |
|---|---|---|
| `004194` | benchmark_text, benchmark_identity_status, methodology_availability, constituents_availability, source_tier | 5 |
| `005313` | 同上 | 5 |
| `017644` | 同上 | 5 |
| `019918` | 同上 | 5 |
| `019923` | 同上 | 5 |

逐字段与 P16-S2 plan 表对比：25 条 `expected_value` 全部逐字符匹配，包括标点差异（`×` vs `*`、`（` vs `(`、`＋` vs `+`）、source anchor 页码差异（`page-5` vs `page-6`、`table-0` vs `table-1`）。所有 `confidence=high`。所有 `benchmark_identity_status=composite`。

## Focus 2: Forbidden Field Absence

**结论：无违规。**

通过独立 Python 验证脚本确认 golden-answer.json 中五个候选基金：

- 无 `benchmark_index_name` row
- 无 `benchmark_index_code` row
- 无 `benchmark_component_text` row
- 无 `methodology_summary` / `methodology_source_title` / `constituents_summary` / `constituents_as_of_date` row
- 无 `missing_reasons` row
- 无 `tracking_error` field 或任何 `tracking_error.*` row
- 每个 fund 的 `field_name` 集合仅为 `{'index_profile'}`

## Focus 3: JSON Rebuild Correctness

**结论：正确。**

| 指标 | 值 | 合理性 |
|---|---|---|
| `fund_count` | 11 | 6 既有 + 5 新增 |
| `record_count` | 150 | 125 既有 + 25 新增 |

`001548` index_profile rows 完整保留：

```text
benchmark_text: 上证50指数收益率×95%＋银行活期存款利率（税后） ×5%
benchmark_identity_status: identified
benchmark_index_name: 上证50指数
source_tier: benchmark_context
```

这与 `test_reviewed_golden_answer_preserves_001548_index_profile_rows` 测试断言完全一致。`001548` 的 `benchmark_index_name=上证50指数` 和 `benchmark_identity_status=identified` 未被改写。

JSON 的 `funds` 数组和 `records` 扁平数组包含完全相同的 25 条新增 row，与 Markdown 源一一对应。

## Focus 4: Test Coverage Assessment

### 4.1 `test_golden_answer.py`

| 测试 | 覆盖 | 评估 |
|---|---|---|
| `test_reviewed_golden_answer_contains_only_planned_p16_s2_index_profile_rows` | 对真实 golden-answer.json 5 个候选逐基金、逐 sub_field 验证 expected_value 和 confidence；断言 `benchmark_index_name`/`benchmark_index_code`/`benchmark_component_text` 不存在；断言无 `tracking_error` row；断言 `expected_value` 无嵌入换行 | **充分** |
| `test_reviewed_golden_answer_preserves_001548_index_profile_rows` | 对真实 golden-answer.json 中 `001548` 的 4 条 index_profile rows 做精确值匹配 | **充分** |

`_P16_S2_INDEX_PROFILE_GOLDEN_ROWS` fixture 字典硬编码了全部 5 个候选的精确 expected_value，覆盖了所有标点差异。

### 4.2 `test_extraction_snapshot.py`

| 测试 | 覆盖 | 评估 |
|---|---|---|
| `test_build_snapshot_records_omits_composite_index_null_and_tuple_values` | 构造 composite `IndexProfileValue`（含 `benchmark_index_name=None`、`benchmark_component_text=tuple`、`missing_reasons=tuple`），断言 `comparable_values` 只含 5 个 scalar；断言 `benchmark_index_name`/`benchmark_index_code`/`benchmark_component_text` 不在 `comparable_values` | **充分** |

`_build_bundle` 新增 `include_composite_index_profile` 参数构造完整 composite fixture，与 `include_index_quality` 互斥（`raise ValueError`）。Fixture 包含真实 004194 benchmark text、`None` fields、tuple fields、anchor，与生产 `IndexProfileValue` 形状一致。

### 4.3 `test_extraction_score.py`

| 测试 | 覆盖 | 评估 |
|---|---|---|
| `test_compare_snapshot_correctness_matches_composite_index_profile_scalars` | 全部 5 scalar match：`comparable_records=5, matched=5, mismatched=0` | **充分** |
| `test_compare_snapshot_correctness_flags_composite_index_scalar_mismatch` | source_tier mismatch：`comparable=5, matched=4, mismatched=1`；精确断言 mismatch 字段、expected 和 actual | **充分** |

`_composite_index_profile_golden_records` helper 只返回计划内 5 scalar subfields，值与 004194 对应。`_golden_answer_json_from_records` 修改为从 `records[0]` 推导 `fund_code`，向后兼容（空 records 时 fallback 到 `"004393"`）。

### 4.4 `test_quality_gate.py`

| 测试 | 覆盖 | 评估 |
|---|---|---|
| `test_run_quality_gate_blocks_composite_index_profile_scalar_mismatch` | 构造 `score.json` 含 `index_profile.source_tier` correctness mismatch；断言 `status=BLOCK`、FQ1 issue 存在、message 包含 `index_profile.source_tier` | **充分** |

### 4.5 测试放宽风险评估

**未发现过度放宽。**

- 所有 match 测试断言精确值，不是模糊匹配或 `assert ... in ...`。
- mismatch 测试断言精确的 mismatched 字段和 count。
- `_composite_index_profile_golden_records` 虽然用 004194 的值做 correctness 机制测试，但 plan 内全部 5 候选的真实值覆盖由 `test_reviewed_golden_answer_contains_only_planned_p16_s2_index_profile_rows` 负责——该测试加载真实 golden-answer.json，逐基金逐字段做精确断言。两者职责不重叠。
- `comparable_records=5` 断言确保 composite benchmark 不会意外引入更多 comparable subfields（如从 null 补值）。

## Focus 5: Boundary / Rule Compliance

| 规则 | 状态 | 证据 |
|---|---|---|
| FundDocumentRepository/source boundary | PASS | 未修改 source、repository、cache、adapter、PDF 层代码 |
| Dayu non-dependency | PASS | 无任何 dayu import 或 runtime 依赖 |
| extra_payload 禁令 | PASS | JSON 结构仅含 schema_version、source_markdown、fund_count、record_count、funds、records；无额外 payload |
| README sync | PASS | Implementation artifact 记录无需更新；未改变 CLI、架构、测试组织或文档模板 |
| Phase scope | PASS | 未修改 design.md、implementation-control.md、CSV、RR-13、branch、commit、PR 或外部状态 |

## Validation Commands And Results

| Command | Result |
|---|---|
| `git diff --check HEAD` | PASS，无 whitespace error |
| `.venv/bin/python -m pytest tests/fund/test_golden_answer.py tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py -q` | `61 passed in 0.40s` |
| `.venv/bin/python -m ruff check fund_agent tests` | `All checks passed!` |
| `.venv/bin/python -m pytest -q` | `439 passed in 0.95s` |
| 独立 Python 验证：fund_count=11, record_count=150 | PASS |
| 独立 Python 验证：5 候选各 5 条 index_profile scalar rows | PASS |
| 独立 Python 验证：无 forbidden subfields | PASS |
| 独立 Python 验证：001548 保留 4 条 index_profile rows | PASS |

## Findings

无 blocking 或 advisory findings。

## Observations (Non-blocking)

| # | 观察 | 处置 |
|---|---|---|
| O-1 | `_composite_index_profile_golden_records` helper 用 004194 的 benchmark_text 值为所有 fund_code 参数服务 | 无需修改：该 helper 用于 correctness 机制测试（match/mismatch 路径），不用于基金特定值验证；真实基金值由 `test_reviewed_golden_answer_contains_only_planned_p16_s2_index_profile_rows` 覆盖 |

## Reviewer Limitation

本 review 未重新运行 `golden-build` 命令重建 JSON（因 implementation artifact 记录了已成功的 rebuild 且 JSON 内容已通过独立脚本逐字段验证）。未检查生产 extractor 对 5 候选的实际抽取输出（P16-S2.1 已做此验证且 controller 已接受）。
