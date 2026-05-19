# P5-S3 Snapshot Sub-field Exposure Plan - 2026-05-20

## Verdict

P5-S3 进入 plan review。

本 slice 目标是关闭 RR-16 的第一段：扩大 correctness denominator，让 strict golden answer 中已经人工审核的 P0 子字段不再全部落为 `unavailable`。实现必须保持数据同源，只从 P1 `StructuredFundDataBundle` 的结构化字段进入 snapshot，不从报告 Markdown、note、source 文本或自然语言段落中反推。

下一 gate：`P5-S3 plan review`。

## Inputs

- Design truth: `docs/design.md`
- Global control doc: `docs/implementation-control.md`
- P4/P5 control doc: `docs/implementation-control-p4.md`
- P5-S2 acceptance: `docs/reviews/p5-s2-acceptance-reconciliation-20260520.md`
- Golden answer JSON: `reports/golden-answers/golden-answer.json`
- Existing Capability code:
  - `fund_agent/fund/extraction_snapshot.py`
  - `fund_agent/fund/extraction_score.py`
  - `fund_agent/fund/golden_answer.py`

## First Principles

Correctness denominator 扩大必须以同一条抽取链路为准：年报仓库 -> extractor -> `StructuredFundDataBundle` -> snapshot -> score。不能为了让 golden answer 可比而解析 `source`、报告正文或人工 Markdown，也不能使用“通常字段名相近”一类间接证据。

## Scope

### 1. SnapshotRecord 增加 `comparable_values`

在 `SnapshotRecord` 中新增：

| 字段 | 类型 | 含义 |
|---|---|---|
| `comparable_values` | `dict[str, str]` | 当前字段下可直接与 golden answer 比较的子字段值 |

规则：

- 只写入当前 `ExtractedField.value` 中已经存在的结构化子键。
- 只保留可序列化为非空字符串的标量值。
- 不展开 list/dict 嵌套值，避免把复杂表格自然语言化后误比。
- `value_present=False` 时可以为空 dict，但 correctness 仍能按字段缺失规则处理。
- 字段或子字段不在白名单时，不能用缺失状态制造 mismatch；必须保持 unavailable。

### 2. 首版可比字段白名单

首版只暴露结构化、稳定、P0 优先字段：

| field_name | sub_fields |
|---|---|
| `basic_identity` | `fund_name`, `fund_code`, `fund_category`, `management_company`, `custodian`, `inception_date`, `classified_fund_type` |
| `benchmark` | `benchmark_name`, `benchmark_text` |
| `nav_benchmark_performance` | `nav_growth_rate`, `benchmark_return_rate` |
| `classified_fund_type` | `fund_type` |

`product_profile` 暂不纳入首版 correctness denominator，原因是当前 golden answer 中 `investment_scope` 和 `style_positioning` 多为长文本或人工裁剪语义，容易因文本边界不稳定引入 false mismatch；后续可单独做文本字段 normalize/review。

`fee_schedule` 暂不纳入首版，因为当前 004393 golden answer 明确 skipped，且不同基金费率表字段命名和份额级别可能需要额外 A/C 份额选择策略。

`benchmark` alias 策略：

- 当前 extractor 可能输出 `benchmark_text`。
- golden answer 可能使用 `benchmark_name`。
- 仅在 `benchmark` 字段内，当 `benchmark_name` 缺失且 `benchmark_text` 存在时，写入 `comparable_values["benchmark_name"] = benchmark_text`。
- 不做跨字段同义词推断。

### 3. Correctness 索引改造

`compare_snapshot_correctness(...)` 的 `_snapshot_actual_index(...)` 改为：

- 优先读取 snapshot record 的 `comparable_values`。
- 对 `classified_fund_type.fund_type` 保留兼容逻辑，读取顶层 `classified_fund_type`。
- 如果 golden key 的 `field_name` 存在对应 snapshot record，但 `sub_field` 不在 `comparable_values`：
  - 只有当 `field_name` 和 `sub_field` 都在 P5-S3 comparable whitelist 中，且 `value_present=False`，才返回 `None`，后续判为 mismatch。
  - 非白名单字段或非白名单 sub-field 必须保持 key 不存在，后续判为 unavailable，不进入分母。
  - 若 `value_present=True` 但白名单 sub-field 未暴露，保持 key 不存在，后续判为 unavailable，不进入分母。

### 4. Backward compatibility

旧 snapshot JSONL 没有 `comparable_values` 时：

- `classified_fund_type.fund_type` 仍按旧逻辑可比。
- 其他子字段保持 unavailable。
- 不抛 fatal schema 错误。

## Non-Goals

- 不修改 golden answer JSON schema。
- 不扩大到所有 P1/P2 字段。
- 不做长文本 fuzzy match。
- 不解析报告 Markdown 或人工 source 文本。
- 不改 quality gate 规则。
- 不处理 failed funds accounting；P5-S4 负责。

## Tests

- `tests/fund/test_extraction_snapshot.py`
  - snapshot schema 包含 `comparable_values`。
  - basic_identity / benchmark / nav_benchmark_performance / classified_fund_type 写入白名单子字段。
  - 非白名单字段不写入 comparable 子字段。
- `tests/fund/test_extraction_score.py`
  - correctness 对 `basic_identity.fund_name`、`benchmark.benchmark_name`、`nav_benchmark_performance.nav_growth_rate` 可比并 match。
  - `benchmark.benchmark_name` 可通过 `benchmark_text` alias 命中。
  - missing field 的 exposed comparable key 为 `None` 时 mismatch。
  - 旧 snapshot 缺少 `comparable_values` 时除 `classified_fund_type.fund_type` 外保持 unavailable。
  - 非白名单字段 missing 仍保持 unavailable。

## Acceptance Criteria

- `score.json.correctness.comparable_records` 在测试中不再只依赖 `classified_fund_type.fund_type`。
- 旧 snapshot 兼容。
- Targeted tests、full suite、ruff、diff check 通过。
- README / tests README 同步说明 `comparable_values` 当前白名单和边界。

## Risks And Tracking

| Risk | Decision |
|---|---|
| 文本字段边界导致 false mismatch | 首版不纳入 `product_profile` 长文本 |
| 费率份额级别选择不稳 | 首版不纳入 `fee_schedule`，留给后续 A/C 份额策略 |
| 旧 snapshot 无 comparable_values | 保持兼容，只新增可比能力 |
| 白名单外字段被误判 mismatch | correctness 只对白名单字段/子字段的明确缺失返回 mismatch |

## Gate Decision

当前 gate 从 `P5-S3 plan review` 推进为 `P5-S3 plan patched after controller review`。

下一步进入 `P5-S3 plan re-review`。
