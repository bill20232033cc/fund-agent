# Correctness Slice Code Review — AgentGLM (2026-05-19)

> **Reviewer**: AgentGLM
> **Scope**: P4-R10 correctness 自动比对相关未提交 diff
> **Control docs**: `docs/implementation-control.md`, `docs/implementation-control-p4.md`
> **Implementation artifact**: `docs/reviews/correctness-slice-implementation-20260519.md`
> **Verdict**: **PASS** — 无 blocking finding

---

## 1. Findings

### F-1 [Info] `_escape_markdown_cell` 在两个 Capability 模块中重复

- **Files**: `fund_agent/fund/extraction_score.py:1297`, `fund_agent/fund/quality_gate.py:619`
- **Description**: 两个模块各自定义了完全相同的 `_escape_markdown_cell(value: str) -> str` 函数。
- **Assessment**: 函数体仅 1 行，当前不值得为此创建共享 util 模块。若后续第三处出现可再抽取。
- **Action**: No action required.

### F-2 [Info] `_snapshot_actual_index` 硬编码 `classified_fund_type` 字段

- **File**: `fund_agent/fund/extraction_score.py:800-815`
- **Description**: `_snapshot_actual_index` 只索引 `CLASSIFIED_FUND_TYPE_FIELD` 子键。当后续 snapshot 暴露更多显式子字段时需要扩展此索引。
- **Assessment**: P4-R10 最小闭环设计明确只比较 snapshot 显式暴露的字段，当前只有 `classified_fund_type.fund_type`。这是 by-design 限制，已在 RR-16 中追踪。
- **Action**: 后续 `snapshot sub-field exposure slice` 负责扩展。

### F-3 [Info] `load_golden_answer_json` 的错误路径缺少独立测试

- **File**: `tests/fund/test_golden_answer.py`
- **Description**: 新增的 `test_load_golden_answer_json_reuses_strict_schema` 只验证了 happy path。`load_golden_answer_json` 的 validation error 路径（schema_version 不匹配、funds 非 array、record 缺字段、重复键等）没有独立测试。
- **Assessment**: 同一 validation 逻辑在 Markdown 路径的 `test_golden_answer.py` golden-build 测试中已覆盖相同 data class 校验规则。JSON loader 使用相同的 `_ALLOWED_CONFIDENCE`、`seen_keys` 重复检测和必需字段检查。低风险。
- **Action**: 可选补强；不阻塞。

---

## 2. 审查标准逐项结论

### 2.1 Correctness 比对位于 Capability 边界内，Service/UI 只做显式参数透传

**PASS**。

- `compare_snapshot_correctness()` 和 `load_golden_answer_json()` 均位于 Capability 层（`extraction_score.py` / `golden_answer.py`）。
- `ExtractionScoreService` 只校验 `.json` 后缀并通过 `golden_answer_path=request.golden_answer_path` 透传给 Capability。
- CLI `extraction_score` 命令只解析 `--golden-answer-path` Typer option 并构造 `ExtractionScoreRequest`。
- Service/UI 不包含任何基金领域规则或 correctness 逻辑。

### 2.2 复用 strict golden answer JSON loader，未重新解析 Markdown

**PASS**。

- `compare_snapshot_correctness()` 调用 `load_golden_answer_json(path)` 直接读取 strict JSON。
- `load_golden_answer_json()` 复用 `GoldenAnswerFund` / `GoldenAnswerRecord` 数据类，与 `build_golden_answer_json()` 共享类型定义。
- correctness 比对路径不接触 Markdown；Markdown 仅在 `golden-build` 人工标注阶段使用。

### 2.3 Skipped golden records 不进 correctness 分母

**PASS**。

- `_compare_golden_funds()` 只遍历 `fund.records`（有效记录），不遍历 `fund.skipped_fields`。
- `skipped_records` 单独计数：`sum(len(fund.skipped_fields) for fund in golden_funds)`。
- `comparable_records` 只含 `match` + `mismatch`。
- `accuracy_rate = matched_records / comparable_records`，分母不含 skipped 和 unavailable。
- 测试 `test_compare_snapshot_correctness_perfect_match_and_skipped_denominator` 明确断言 `skipped_records == 1` 且 `comparable_records == 1`。

### 2.4 Unavailable 与 mismatch 语义正确，避免间接证据推断

**PASS**。

- **Unavailable**: golden 有效记录的 `(fund_code, field_name, sub_field)` 不在 `actual_index` 中 → 标记 `unavailable`，不进分母。语义：snapshot 未暴露该子字段。
- **Mismatch（值不一致）**: `normalized_actual != normalized_expected` → mismatch。snapshot 暴露了值但与 golden 不一致。
- **Mismatch（值缺失）**: `actual_index` 中键存在但值为 `None`（`value_present=False`）→ mismatch。golden 期望有值但 snapshot 标记缺失。
- `_normalize_comparable_value()` 只做 strip、全角空白归一化、连续空白压平、casefold。无同义词映射，无锚点推断，无经验补值。
- 测试覆盖了 match + unavailable + mismatch 三种状态。

### 2.5 `score.json/score.md` 与 `quality_gate` 对 FQ0/FQ1 行为符合 control_doc

**PASS**。

| 场景 | control_doc 要求 | 实际行为 | 测试覆盖 |
|---|---|---|---|
| 无 golden answer | FQ0/info，不阻断 | `_evaluate_correctness` 返回 FQ0/info，severity=info | `test_run_quality_gate_keeps_fq0_info_without_golden_answer` |
| correctness.status=unavailable | FQ0/info | 同上路径，包含 "not_implemented" 兼容 | 同上 |
| 明确 mismatch | FQ1/block | `_correctness_mismatch_issue` 生成 FQ1, severity=block | `test_run_quality_gate_blocks_correctness_mismatch_as_fq1` |
| 所有 match | 无 FQ1 | `_evaluate_correctness` 遍历 record_results 只对 mismatch 发 issue | `test_compare_snapshot_correctness_perfect_match_and_skipped_denominator` |

Control doc §7.2 FQ1 定义为"基金类型与 App 类别或 golden answer 明显冲突"。当前只实现了 golden answer mismatch 路径；App 类别冲突检查属于 FQ1 的另一半，延后到 `quality gate rules slice`（P4-R9 已追踪）。

### 2.6 Schema 兼容/空值/错误处理/Markdown 输出/测试覆盖

**PASS**（带 F-3 info）。

- **Schema 兼容**: `QualityGateIssue` 新增 `fund_code`、`expected_value`、`actual_value` 均有默认值 `None`，向后兼容。`ExtractionScoreResult` 新增 `fund_scores` 和 `correctness` 作为必填字段，唯一构造点 `run_extraction_score()` 始终填充。
- **空值处理**: `FundScoreRow.fund_name: str | None`、`CorrectnessRecordResult.actual_value: str | None`、`accuracy_rate: float | None` 均显式可空。
- **错误处理**: `load_golden_answer_json` 校验 schema_version、funds 类型、每条记录必需字段、confidence 枚举、source 非 manual_required、重复键。`_evaluate_correctness` 校验 status 合法性和 record_results 类型。
- **Markdown 输出**: correctness 明细表和 fund_scores 表均使用 `_escape_markdown_cell` 防止竖线注入。
- **测试覆盖**: 6 个新增测试覆盖 match/mismatch/unavailable/skipped/FQ0/FQ1/per-fund。

### 2.7 未引入过度耦合或基金领域规则放错层

**PASS**。

- correctness 比对、normalize、fund_scores 计算均在 Capability 层。
- quality gate FQ1 评估在 Capability 层 `quality_gate.py`。
- Service 层无 domain rule。
- UI 层只做 Typer 参数解析。
- `_normalize_comparable_value` 不含领域特定同义词。

---

## 3. 验证命令与结果

| # | 命令 | 结果 |
|---|---|---|
| 1 | `.venv/bin/python -m pytest tests/fund/test_golden_answer.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py tests/services/test_extraction_score_service.py tests/services/test_quality_gate_service.py tests/ui/test_cli.py -q` | `28 passed` in 0.42s |
| 2 | `.venv/bin/python -m ruff check fund_agent/fund/extraction_score.py fund_agent/fund/golden_answer.py fund_agent/fund/quality_gate.py fund_agent/services/extraction_score_service.py fund_agent/ui/cli.py` | All checks passed |
| 3 | `git diff --check` (all correctness-scope files) | No output (passed) |

---

## 4. Residual Risk

### 4.1 Correctness 可比字段覆盖面窄（已追踪：RR-16）

当前 P4-R10 只比较 snapshot 显式暴露的 `classified_fund_type.fund_type`。真实 004393 smoke 显示 golden answer 有 121 条有效记录和 29 个 skipped fields，但只有 1 条进入 correctness 分母。

**评估**：可接受。这是 by-design 保守策略：
- 避免了间接证据推断。
- Snapshot 记录当前不暴露子字段值（如 `basic_identity.fund_name`），golden 记录自然标记为 `unavailable`。
- 后续 `snapshot sub-field exposure slice` 负责在 snapshot 中暴露更多子字段值后自然扩大可比范围。
- 该策略确保 correctness 分母中的每一条记录都有直接、显式的 snapshot 值，不存在"从 anchor 文本推断"的灰色地带。

### 4.2 `_normalize_comparable_value` 对非枚举字段可能过于保守

当前 normalize 只做大小写和空白归一化。对于 `fund_name` 等自由文本字段，后续可能需要更智能的 normalize（如去除空格后缀、全半角统一等）。当前只对 `classified_fund_type.fund_type`（枚举值）比对，不存在此风险。

### 4.3 `quality_gate` 未接入 `analyze` 主链路（已追踪：RR-15, P4-R8）

当前 quality gate 是独立 CLI 命令，不影响报告生成主链路。作为后续 `quality gate integration slice` 追踪。

---

## 5. Conclusion

**PASS**。无 blocking finding。3 个 info 级 finding 均不阻碍当前 gate。实现正确地在 Capability 层完成了 P4-R10 correctness 最小闭环，Service/UI 层只做参数透传，skipped 不进分母，unavailable/mismatch 语义清晰，FQ0/FQ1 行为符合控制文档。
