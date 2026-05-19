# Code Review

## Scope

- Mode: current changes
- Branch: `main`
- Base: `main` (P4-S1 accepted commit `c8a47f6`)
- Output file: `docs/reviews/p4-s2-code-review-glm-20260519.md`
- Included scope: P4-S2 implementation paths
  - `fund_agent/fund/extraction_score.py`
  - `fund_agent/services/extraction_score_service.py`
  - `fund_agent/services/__init__.py`
  - `fund_agent/ui/cli.py` (extraction-score command only)
  - `tests/fund/test_extraction_score.py`
  - `tests/services/test_extraction_score_service.py`
  - `tests/ui/test_cli.py` (extraction-score test only)
  - `README.md`
  - `fund_agent/fund/README.md`
  - `tests/README.md`
  - `docs/implementation-control-p4.md`
  - `docs/implementation-control.md`
  - `docs/reviews/p4-s2-implementation-20260519.md`
- Excluded scope: P4-S1 accepted code (`fund_agent/fund/extraction_snapshot.py` and its tests) except where P4-S2 directly depends on its exports
- Parallel review coverage: 无

## Review Criteria Alignment

逐条核对 P4-S2 review criteria：

1. **snapshot-only consumption**: `extraction_score.py` 只 import `DEFAULT_SELECTED_FUNDS_CSV`、`SNAPSHOT_FIELD_ORDER`、`SelectedFundRecord`、`load_selected_funds`、`validate_selected_fund_pool` from `extraction_snapshot`；不 import `FundDataExtractor`、`FundDocumentRepository` 或任何 PDF/cache/network 模块。`load_snapshot_records()` 只读 JSONL 文件，`select_minimal_golden_set()` 只读 CSV 文件。✅

2. **coverage / traceability only, correctness not_implemented**: `score_snapshot_records()` 计算 coverage_rate 和 traceability_rate；`_score_json_payload()` 输出 `"correctness": {"status": "not_implemented", "reason": "P4-S2 前半段只实现 coverage / traceability；人工 golden answer 留到 P4-S2 后半段。"}`；`_score_markdown()` 输出 `"- correctness: not_implemented（P4-S2 后半段再引入人工 golden answer）"`。✅

3. **field priority mapping**: `FIELD_PRIORITY_BY_NAME` 是代码内显式常量 dict，映射 14 个 field_name 到 P0/P1/P2，与 `docs/implementation-control-p4.md` 第 5.2 节 P0/P1/P2 分组完全一致。`UNKNOWN_FIELD_PRIORITY = "UNMAPPED"` 处理 snapshot 中出现但映射表未覆盖的字段。✅

4. **score output fields and thresholds**: `FieldScoreRow` 包含 field_group、field_name、priority、records、coverage_rate、traceability_rate、status。阈值是模块级 `Final` 常量（`PASS_COVERAGE_THRESHOLD = 0.90` 等），可通过 `ScoreThresholds` dataclass 覆盖。`_validate_thresholds()` 检查 0-1 范围和 watch <= pass 不变量。✅

5. **golden set selection**: `MANDATORY_GOLDEN_CODE = "004393"`；`REQUIRED_GOLDEN_CATEGORIES = ("黄金类", "海外股票类", "海外债券/稳健类", "国内债券类")`；selection 先固定纳入 004393，再按 CSV 顺序为每个 required category 选 1 只，最后再选 1 只额外 国内股票类（排除已入选的 004393），合计 2 只国内股票类；`EXCLUDED_GOLDEN_CATEGORIES = ("货币基金类",)`。所有代码只来自 CSV。对实际 CSV 验证：004393 在 line 19（国内股票类），选择后 additional 国内股票类为 001548（CSV 中第一个未被选中的国内股票类），合计 6 只。✅

6. **UI → Service → Capability boundary**: CLI `extraction_score()` 只 import `ExtractionScoreService` 和 `ExtractionScoreRequest` from `fund_agent.services`，不直接 import Capability 层。Service `run()` 用显式参数委托 `run_extraction_score()`。无 `extra_payload`。✅

7. **test isolation and coverage**:
   - `test_extraction_score.py`：4 个测试覆盖 scoring rates/status/priority、threshold boundaries、output files、golden set selection。使用内存 records 和 `tmp_path`，不触发网络或 PDF。
   - `test_extraction_score_service.py`：2 个测试覆盖 Service 显式参数转发和非 JSONL 路径拒绝。使用 `monkeypatch`。
   - `test_cli.py`：1 个测试覆盖 CLI → Service 参数转发。使用 `_FakeExtractionScoreService`。
   ✅

## Findings

未发现实质性问题。

以下为逐文件走读确认无 findings 的关键路径：

### `fund_agent/fund/extraction_score.py`

- **数据源隔离**: 只消费 `snapshot.jsonl`（通过 `load_snapshot_records`）和 CSV（通过 `load_selected_funds`）。不访问 PDF、cache、文档仓库或网络。
- **评分逻辑正确性**: `score_snapshot_records()` 按 `(field_group, field_name)` 分组计数，`value_present` 和 `anchor_present` 通过 `_truthy_bool()` 转换后分别累加。coverage_rate = covered_records / records，traceability_rate = traceable_records / records，分母为 0 时 `_rate()` 返回 0.0。status 判定：pass 要求 coverage AND traceability 均 >= pass 阈值，watch 要求均 >= watch 阈值，其余 fail。逻辑与控制文档 §5.3 一致。
- **阈值常量可见性**: 4 个阈值（pass_coverage/traceability = 0.90, watch_coverage/traceability = 0.70）均为模块顶层 `Final` 常量，`ScoreThresholds` dataclass 默认值引用这些常量，`_validate_thresholds()` 做范围和排序校验。CLI 使用默认值。
- **golden set 选择**: 选择过程为先固定 004393，再按 CSV 顺序遍历 REQUIRED_GOLDEN_CATEGORIES 各选 1 只未入选基金，最后选 1 只额外 国内股票类。`_find_fund_by_code()` 拒绝排除类别中的代码。`_first_fund_by_category()` 跳过已入选和排除类别。`_append_golden_record()` 去重。错误路径均有 ValueError。
- **correctness not_implemented**: JSON 和 Markdown 输出均显式标注 correctness 为 not_implemented 并附理由。
- **输出字段完整性**: `_score_json_payload()` 包含 snapshot_path、source_csv、thresholds、field_count、status_counts、p0_status（P0 字段聚合状态）、field_scores（每行含 field_group/field_name/priority/records/coverage_rate/traceability_rate/status）、golden_set、correctness。`_score_markdown()` 输出 Status Counts 表、Field Scores 表、Golden Set 表和 Excluded Categories 段。
- **_aggregate_status**: 空集合返回 fail，任一 fail 返回 fail，任一 watch 返回 watch，全 pass 返回 pass。语义合理。
- **_ordered_counters**: 按 `SNAPSHOT_FIELD_ORDER` 排序已知字段，额外字段按 key 排序追加末尾。保持输出顺序与 P4-S1 snapshot schema 一致。

### `fund_agent/services/extraction_score_service.py`

- **Service 层职责**: `_validate_request()` 校验 snapshot_path 后缀为 `.jsonl`，output_dir 如存在须为目录。`run()` 用显式参数委托 Capability `run_extraction_score()`。无 `extra_payload`，无业务逻辑。
- **Architecture boundary**: 只 import Capability 层的 `ExtractionScoreResult`、`ScoreThresholds`、`run_extraction_score`。不 import PDF/cache/网络模块。

### `fund_agent/services/__init__.py`

- 新增 `ExtractionScoreRequest` 和 `ExtractionScoreService` 到 `__all__`。与已有 P4-S1 导出一致。

### `fund_agent/ui/cli.py` (extraction-score command)

- **UI → Service**: `extraction_score()` 只 import Service 层类型。创建 `ExtractionScoreRequest` 传递显式参数，调用 `ExtractionScoreService().run()`。不 import Capability 层。
- **错误处理**: try/except 捕获异常，输出 `"评分生成失败：{exc}"` 到 stderr 并以 code=1 退出。与 extraction-snapshot 和 analyze 的错误处理模式一致。
- **CLI 参数**: `--snapshot-path`（必需）、`--source-csv`（默认 `docs/code_20260519.csv`）、`--output-dir`（可选，默认使用 snapshot 所在目录）。参数均为显式传递，无隐式 cwd 依赖。

### `tests/fund/test_extraction_score.py`

- **test_score_snapshot_records_computes_coverage_traceability_status_and_priority**: 构造 8 条混合 records，断言 basic_identity（P0, coverage=1.0, traceability=0.5, fail）、product_profile（P1, coverage=0.5, traceability=1.0, fail）、turnover_rate（P1）、nav_data（P2）的 priority 正确，且 FIELD_PRIORITY_BY_NAME 覆盖所有评分字段。
- **test_score_snapshot_records_status_thresholds_are_deterministic**: 用 30 条 records 构造 pass（10/10 coverage+traceability=100%）、watch（8/10=80%，>=70% && <90%）、fail（6/10=60%，<70%）三档，断言 status 分界正确。
- **test_run_extraction_score_writes_score_outputs**: 写临时 snapshot.jsonl，调用 `run_extraction_score()`，断言 score.json（含 correctness.status="not_implemented"、p0_status）、score.md（含 "## Field Scores"）和 golden_set.json（含 004393）均存在且内容正确。
- **test_select_minimal_golden_set_uses_only_csv_codes_and_excludes_money_market**: 对真实 CSV 验证 golden set 只含 CSV 中代码、包含 004393、包含 4 个 required categories、至少 2 只国内股票类、不包含货币基金类、excluded_categories 与 EXCLUDED_GOLDEN_CATEGORIES 一致。
- 所有测试使用内存数据或 `tmp_path`，不触发网络或 PDF。

### `tests/services/test_extraction_score_service.py`

- **test_extraction_score_service_delegates_explicit_params**: 用 `monkeypatch` 替换 Capability `run_extraction_score`，验证 Service 以完整显式参数（含自定义 thresholds）委托 Capability。
- **test_extraction_score_service_rejects_non_jsonl_snapshot**: 验证 `.json` 后缀路径被 Service 层拒绝。

### `tests/ui/test_cli.py` (extraction-score test)

- **test_extraction_score_cli_is_thin_service_entry**: 用 `_FakeExtractionScoreService` 替换 Service，验证 CLI 转发 snapshot_path、source_csv、output_dir 三个显式参数，输出 `"score_json:"` 前缀。

### Documentation sync

- `README.md`：新增 `fund-analysis extraction-score` 命令说明、输出文件列表和 correctness/golden set 边界。与 CLI 实际参数对齐。
- `fund_agent/fund/README.md`：新增 `run_extraction_score()` 和 `select_minimal_golden_set()` 说明，明确只消费 snapshot JSONL 和 CSV。
- `tests/README.md`：新增 P4-S2 score 测试条目和维护约定。
- `docs/implementation-control-p4.md`：状态更新至 P4-S2 code review。
- `docs/implementation-control.md`：状态更新至 P4-S2 code review。

## Open Questions

无。

## Residual Risk

- Golden set selection 测试读取真实 CSV 文件（`docs/code_20260519.csv`）。若 CSV 内容或结构发生变化（如类别重命名、004393 被移除），测试将失败。这是 intentional design（验证 golden set 与真实数据源一致性），但需在 CSV 维护时同步关注。
- CLI `extraction-score` 不暴露 `--thresholds` 选项，始终使用默认阈值。当前 MVP 阶段可接受；后续若需自定义阈值，需在 CLI 层新增选项。
- `score_snapshot_records()` 只输出 snapshot 中实际存在的字段；若 P4-S1 某字段完全缺失（0 条记录），该字段不会出现在 score 输出中。这是 P4-S1 的 responsibility（确保 14 个字段均有记录），P4-S2 不补充缺失字段。

## Verdict

**PASS**

P4-S2 前半段实现完整满足所有 review criteria：只消费 snapshot.jsonl 和 CSV、只实现 coverage/traceability 评分并显式标注 correctness 为 not_implemented、字段优先级映射与控制文档一致、评分输出包含所有必需字段且阈值为显式常量、golden set 选择满足所有约束、UI/Service/Capability 分层正确、测试覆盖评分逻辑/阈值/输出文件/golden set/Service-UI 边界且不依赖网络或 PDF。
