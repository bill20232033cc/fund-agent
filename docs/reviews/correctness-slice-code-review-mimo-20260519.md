# Correctness Slice Code Review — MiMo

> **Reviewer**: AgentMiMo
> **Date**: 2026-05-19
> **Scope**: P4-R10 correctness 自动比对最小闭环
> **Gate**: correctness slice code review
> **Verdict**: **PASS** (no blocking finding)

---

## 1. Findings

### F-1 [style] `ruff format` 未执行 — 5 个实现文件格式不一致

**Severity**: low (non-blocking)
**Files**: `fund_agent/fund/golden_answer.py`, `fund_agent/fund/extraction_score.py`, `fund_agent/fund/quality_gate.py`, `fund_agent/services/extraction_score_service.py`, `fund_agent/ui/cli.py`

`ruff format --check` 报告 5 个文件需要 reformat。`ruff check` 通过。这不是 correctness 问题，但违反项目约定（commit 前应 `ruff format`）。建议在 accepted commit 前执行 `ruff format` 一次。

**Recommendation**: `uv run ruff format .` 然后 amend 或新 commit。

---

### F-2 [info] correctness 可比范围仅覆盖 `classified_fund_type.fund_type` 一个子字段

**Severity**: info (non-blocking, by design)
**File**: `fund_agent/fund/extraction_score.py:828-834`

`_snapshot_actual_index()` 硬编码只索引 `classified_fund_type` 字段。golden answer 中其他有效记录（如 `basic_identity.fund_name`、`benchmark.benchmark_name`）全部标记为 `unavailable`，不进入 correctness 分母。这是 P4-R10 最小闭环的显式设计选择（见 `correctness-slice-implementation-20260519.md`），但意味着当前 correctness 覆盖面极窄。

**Recommendation**: 已在 `implementation-control.md` RR-16 追踪。后续 `snapshot sub-field exposure slice` 负责扩大 coverage。当前策略可接受。

---

### F-3 [info] `_normalize_comparable_value` 仅做 casefold + 空白归一化

**Severity**: info (non-blocking, by design)
**File**: `fund_agent/fund/extraction_score.py:955-972`

保守 normalize 只做大小写、全角空白和连续空白归一化。不做同义词映射（如 "主动管理型" vs "active_fund"）、不补值。这是正确的设计选择——避免用间接证据推断修正 correctness。但意味着 golden answer 的 `expected_value` 必须与 snapshot 输出值在 normalize 后完全一致，否则会误报 mismatch。

**Recommendation**: 当前行为符合"保守 normalize"契约。文档已说明。可接受。

---

## 2. Review Criteria Verification

### 2.1 Correctness 比对位于 Capability 边界内，Service/UI 只做显式参数透传

**PASS**

- `compare_snapshot_correctness()` 在 `fund_agent/fund/extraction_score.py` (Capability 层)
- `_evaluate_correctness()` 在 `fund_agent/fund/quality_gate.py` (Capability 层)
- `ExtractionScoreService.run()` 只做 request 校验 + 委托 `run_extraction_score()`
- `QualityGateService.run()` 只做 request 校验 + 委托 `run_quality_gate()`
- CLI `extraction_score` 和 `quality_gate` 只做参数解析和 stdout 输出
- Service 层新增 `golden_answer_path` 参数透传，无逻辑耦合

### 2.2 复用 strict golden answer JSON loader，未重新解析 Markdown

**PASS**

- `extraction_score.py:24` 导入 `load_golden_answer_json` from `golden_answer.py`
- `compare_snapshot_correctness()` 直接调用 `load_golden_answer_json()` 读取 strict JSON
- `load_golden_answer_json()` 校验 `schema_version`、重复键、字段类型
- 无任何 Markdown 重新解析路径

### 2.3 Skipped golden records 不进入 correctness 分母

**PASS**

- `compare_snapshot_correctness()` line 539: `skipped_records = sum(len(fund.skipped_fields) for fund in golden_funds)`
- skipped 只计入 `skipped_records` 计数
- `comparable_records` 只包含 `CORRECTNESS_MATCH` 和 `CORRECTNESS_MISMATCH` 的记录（line 535）
- `accuracy_rate = matched_records / comparable_records`（line 549），skipped 不在分母
- 测试 `test_compare_snapshot_correctness_perfect_match_and_skipped_denominator` 验证 `skipped_records == 1` 且 `accuracy_rate == 1.0`

### 2.4 Unavailable 与 mismatch 语义正确，避免间接证据推断

**PASS**

- `CORRECTNESS_UNAVAILABLE`: "snapshot 未显式暴露该 golden 子字段；不进入 correctness 分母。" — 当 `(fund_code, field_name, sub_field)` 不在 `actual_index` 中时
- `CORRECTNESS_MISMATCH` (golden expects but snapshot missing): "golden 期望存在该字段，但 snapshot 明确标记为缺失。" — 当 `value_present == False` 时
- `CORRECTNESS_MISMATCH` (values differ): "保守 normalize 后不一致。" — 当 normalize 后值不同时
- `_normalize_comparable_value()` 只做 casefold + 全角空白 + 连续空白归一化，不做同义词映射或推断
- 不可用记录不进入分母（line 538）

### 2.5 `score.json/score.md` 与 `quality_gate` 对 FQ0/FQ1 行为符合 control_doc

**PASS**

| 场景 | score.json | quality_gate | 符合 control_doc |
|------|-----------|-------------|-----------------|
| 无 `--golden-answer-path` | `correctness.status = "unavailable"` | FQ0/info | ✓ |
| golden JSON 提供，全部 match | `correctness.status = "available"` | 无 FQ1 issue | ✓ |
| golden JSON 提供，存在 mismatch | `correctness.status = "available"`, `mismatched_records > 0` | FQ1/block | ✓ |
| `score.json` 无 correctness 字段 | N/A | FQ0/info | ✓ |
| `correctness.status = "not_implemented"` | N/A | FQ0/info | ✓ |

- `quality_gate.py:190-212`: 非 dict 或 status 在 `{not_implemented, unavailable}` 时返回 FQ0/info
- `quality_gate.py:213-214`: status 不是 `available` 时 raise ValueError（防御性校验）
- `quality_gate.py:222-223`: record status == `mismatch` 时生成 FQ1/block issue
- 测试 `test_run_quality_gate_blocks_correctness_mismatch_as_fq1` 验证 FQ1 阻断
- 测试 `test_run_quality_gate_keeps_fq0_info_without_golden_answer` 验证 FQ0/info

### 2.6 Schema 兼容/空值/错误处理/Markdown 输出/测试覆盖

**PASS (with info)**

**Schema 兼容**:
- `GoldenAnswerValidationError` 覆盖 JSON schema 校验（schema_version、funds 结构、记录字段）
- `load_golden_answer_json()` 校验重复键、缺失字段、非法 confidence/source
- `score.json` 结构包含 `field_scores`、`fund_scores`、`correctness` 三个子结构

**空值处理**:
- `golden_answer_path is None` → 返回 unavailable summary
- `actual_value is None` (value_present=False) → mismatch
- `_optional_rate(0, 0)` → `None`
- `_first_optional_text` → `None` for missing fund_name/app_category

**错误处理**:
- `_load_score_payload` 校验顶层 dict
- `_evaluate_score_payload` 校验 field_scores/fund_scores 列表和行结构
- `_evaluate_correctness` 校验 correctness dict 和 record_results 列表
- `_required_text` / `_required_fund_text` / `_required_number` 做类型校验

**Markdown 输出**:
- `score.md` 包含 `## Correctness` 段（line 1178-1204）和 `## Fund Scores` 段（line 1206-1227）
- `quality_gate.md` 包含 issues 表格，含 expected/actual 列

**测试覆盖**:
- `test_golden_answer.py`: 4 tests — Markdown 解析、strict 校验、JSON 构建、JSON loader 复用
- `test_extraction_score.py`: 7 tests — coverage/traceability、阈值、单基金 P0、score 输出、correctness match/mismatch/skipped
- `test_quality_gate.py`: 5 tests — P0 block、P1 warn、单基金 P0 block、FQ1 mismatch block、FQ0 info
- `test_extraction_score_service.py`: 2 tests — 参数透传、非法路径拒绝
- `test_cli.py`: 7 tests — CLI 参数转发（含 golden-answer-path）

**缺口**:
- 无 golden answer JSON schema 非法的独立测试（如 schema_version 错误）— 由 Markdown 解析测试间接覆盖
- 无 `_evaluate_correctness` 对非 dict correctness 的独立测试 — 由 `test_run_quality_gate_blocks_failed_p0_fields` 中 `"status": "not_implemented"` 间接覆盖

### 2.7 过度耦合或基金领域规则放错层

**PASS**

- correctness 比对逻辑全在 Capability 层 (`extraction_score.py`, `quality_gate.py`)
- Service 层无任何基金领域规则
- CLI 层无任何基金领域规则
- `golden_answer.py` 只做 JSON 构建/读取/校验，不做比对
- `_snapshot_actual_index()` 硬编码 `classified_fund_type` 是最小闭环选择，不是耦合

---

## 3. Verification Commands & Results

| Command | Result |
|---------|--------|
| `uv run pytest tests/fund/test_golden_answer.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py tests/services/test_extraction_score_service.py tests/ui/test_cli.py -q` | **26 passed** in 0.74s |
| `uv run ruff check ...` (5 implementation files) | All checks passed |
| `uv run ruff format --check ...` (5 implementation files) | **5 files would be reformatted** (F-1) |
| `git diff --check HEAD -- ...` (5 impl + 5 test files) | exit=0, no whitespace issues |
| `git diff HEAD --stat` (13 files) | 1503 insertions, 37 deletions |

---

## 4. Residual Risk

| ID | Risk | Severity | Status |
|----|------|----------|--------|
| RR-16 | correctness 可比字段覆盖面窄：当前仅 `classified_fund_type.fund_type` 进入分母 | 中 | 追踪中；后续 `snapshot sub-field exposure slice` 负责扩大 |
| F-1 | `ruff format` 未执行，5 个实现文件格式不一致 | 低 | 建议 accepted commit 前修复 |

### Snapshot 显式暴露字段策略可接受性

当前策略"只比较 snapshot 显式暴露的可比字段"是正确的最小闭环选择：
1. 避免从 snapshot 间接推断 golden answer 字段值
2. 不可用记录不污染分母，`accuracy_rate` 只反映真正可比的字段
3. `_snapshot_actual_index()` 硬编码 `classified_fund_type` 是当前唯一有 golden answer 且 snapshot 直接暴露的字段
4. 后续扩大 coverage 的路径清晰：增加 `_snapshot_actual_index()` 的字段映射即可

**结论**: 当前 snapshot 显式暴露字段策略可接受，前提是 RR-16 在后续 slice 中继续追踪。

---

## 5. Conclusion

**PASS** — 无 blocking finding。

Correctness 自动比对最小闭环实现正确：
- Capability 边界清晰，Service/UI 只做参数透传
- 复用 strict golden answer JSON loader，未重新解析 Markdown
- Skipped/unavailable 不进入分母，mismatch 语义正确
- FQ0/FQ1 行为符合 control_doc
- 26 tests 全部通过
- 1 个 low severity style issue (F-1) 建议 accepted commit 前修复
- 1 个 info residual risk (RR-16) 已在控制文档追踪
