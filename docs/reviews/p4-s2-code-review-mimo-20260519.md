# P4-S2 Code Review — AgentMiMo

> **日期**: 2026-05-19
> **审查人**: AgentMiMo
> **Gate**: P4-S2 code review
> **审查范围**: P4-S2 实现路径（不重审 P4-S1 已接受代码）
> **设计真源**: `docs/design.md`
> **控制文档**: `docs/implementation-control.md`、`docs/implementation-control-p4.md`
> **实现产物**: `docs/reviews/p4-s2-implementation-20260519.md`

---

## 审查路径

| 文件 | 状态 |
|---|---|
| `fund_agent/fund/extraction_score.py` | ✅ reviewed |
| `fund_agent/services/extraction_score_service.py` | ✅ reviewed |
| `fund_agent/services/__init__.py` | ✅ reviewed |
| `fund_agent/ui/cli.py` | ✅ reviewed |
| `tests/fund/test_extraction_score.py` | ✅ reviewed |
| `tests/services/test_extraction_score_service.py` | ✅ reviewed |
| `tests/ui/test_cli.py` | ✅ reviewed |
| `README.md` | ✅ reviewed |
| `fund_agent/fund/README.md` | ✅ reviewed |
| `tests/README.md` | ✅ reviewed |
| `docs/implementation-control-p4.md` | ✅ reviewed |
| `docs/implementation-control.md` | ✅ reviewed |
| `docs/reviews/p4-s2-implementation-20260519.md` | ✅ reviewed |

---

## Findings

### F1 [INFO] CLI test only asserts `score_json:` output, not `score_md:` or `golden_set:`

**文件/行号**: `tests/ui/test_cli.py:319`

**证据**: `test_extraction_score_cli_is_thin_service_entry` 断言 `"score_json:" in result.output`，但未断言 `"score_md:"` 或 `"golden_set:"`。CLI 实际输出三行（`cli.py:235-237`），测试只覆盖第一行。

**建议**: 补充 `"score_md:"` 和 `"golden_set:"` 存在性断言，与 `extraction-snapshot` CLI 测试覆盖三条输出路径保持一致。

**严重性**: INFO — 测试已验证参数转发和成功路径，缺失的断言不影响正确性。

---

### F2 [INFO] Golden set 错误路径缺少显式测试

**文件/行号**: `tests/fund/test_extraction_score.py:144-169`

**证据**: `test_select_minimal_golden_set_uses_only_csv_codes_and_excludes_money_market` 覆盖了正向选择规则。但 `select_minimal_golden_set` 的 `ValueError` 路径（必需类别缺失、`004393` 缺失、`004393` 属于排除类别）未被显式测试。`_find_fund_by_code` 和 `_first_fund_by_category` 的异常路径依赖代码审查确认。

**建议**: 后续 slice 可补充 golden set 选择的负向测试，验证 CSV 缺少必需类别或 `004393` 被错误归类时的 `ValueError` 行为。

**严重性**: INFO — 当前 CSV 包含所有必需类别和 `004393`，正向路径已覆盖。

---

## 逐条审查标准核对

### 1. P4-S2 前半段只消费 P4-S1 `snapshot.jsonl`，不读取 PDF/cache/文档仓库/网络

✅ **通过**。`extraction_score.py` 只从 `snapshot_path` 读取 JSONL，从 `source_csv` 读取精选基金池 CSV。未导入 `FundDocumentRepository`、`FundDataExtractor`、PDF 模块或任何网络库。

### 2. 只实现 coverage / traceability 评分；correctness 和人工 golden answer 显式标记 `not_implemented`

✅ **通过**。`_score_json_payload` 第 628-631 行输出 `correctness.status = "not_implemented"` 并附带原因。`_score_markdown` 第 680 行输出 `correctness: not_implemented`。实现产物与控制文档一致。

### 3. 字段优先级映射为代码同源、显式，且与实现产物/控制文档一致

✅ **通过**。`FIELD_PRIORITY_BY_NAME`（`extraction_score.py:24-39`）与 `SNAPSHOT_FIELD_ORDER`（`extraction_snapshot.py:25-40`）覆盖相同的 14 个 `field_name`。P0/P1/P2 分组与 `implementation-control-p4.md` 第 5.2 节和 `p4-s2-implementation-20260519.md` 一致。

### 4. 评分输出包含 `field_group, field_name, priority, records, coverage_rate, traceability_rate, status`；阈值为显式常量或请求字段，无隐藏魔法数字

✅ **通过**。`FieldScoreRow` dataclass 包含全部 7 个必需字段加上 `covered_records` 和 `traceable_records`。阈值通过模块级 `Final` 常量定义（第 44-47 行），`ScoreThresholds` dataclass 提供显式默认值。`_validate_thresholds` 校验范围和单调性。无隐藏魔法数字。

### 5. Golden set 选择只使用 `docs/code_20260519.csv` 代码，包含 `004393`，覆盖必需类别，至少 2 只国内股票类，排除货币基金类

✅ **通过**。验证逻辑：

- `select_minimal_golden_set` 调用 `load_selected_funds(source_csv)` 只从 CSV 选码
- `MANDATORY_GOLDEN_CODE = "004393"` 固定纳入，`_find_fund_by_code` 若缺失则 `ValueError`
- `REQUIRED_GOLDEN_CATEGORIES` 包含黄金类、海外股票类、海外债券/稳健类、国内债券类
- 国内股票类额外选 1 只（加上 `004393` 共 2 只）
- `EXCLUDED_GOLDEN_CATEGORIES = (MONEY_MARKET_CATEGORY,)` 排除货币基金类
- 测试 `test_select_minimal_golden_set_uses_only_csv_codes_and_excludes_money_market` 覆盖全部选择规则

### 6. UI 只依赖 Service，不依赖 Capability；Service 只传显式参数，无 `extra_payload`

✅ **通过**。`cli.py` 导入 `ExtractionScoreService` 和 `ExtractionScoreRequest`（第 17-19 行）。`extraction_score` 命令（第 201-237 行）只构造 `ExtractionScoreRequest` 并调用 `service.run()`。`ExtractionScoreService.run()`（`extraction_score_service.py:39-59`）只传 `snapshot_path`、`source_csv`、`output_dir`、`thresholds` 四个显式参数，无 `extra_payload`。

### 7. 测试不访问真实网络/PDF，覆盖评分率/状态/优先级、输出文件、golden set 选择、Service/UI 边界

✅ **通过**。

- `test_extraction_score.py`：4 个测试覆盖 coverage/traceability/status/priority 映射、阈值确定性、score 输出文件和 golden set 选择规则
- `test_extraction_score_service.py`：2 个测试覆盖显式参数转发和非法 snapshot 路径拒绝
- `test_cli.py`：`test_extraction_score_cli_is_thin_service_entry` 覆盖 CLI 参数转发
- 全部使用 monkeypatch/fake/临时文件，无网络/PDF 访问

---

## Verdict

**PASS**

P4-S2 实现正确覆盖了字段级 coverage / traceability 评分和最小 golden set 选择。代码消费 snapshot JSONL 而非原始 PDF/cache，阈值为显式常量，字段优先级映射与控制文档一致，golden set 选择规则满足全部约束，UI→Service→Capability 边界清晰。发现 2 个 INFO 级 finding，不阻塞 acceptance。
