# P4-S3b Implementation

## 范围

- 当前 gate：P4-S3b implementation。
- 当前 slice：修复 004393 中有直接、语义清晰年报证据的 extractor 缺口。
- 未处理：`fee_schedule`。§6 费用表披露的是当期实际支付管理费/托管费金额，不是费率，映射到 `fee_schedule` 会污染字段语义。

## Root Cause

- `nav_benchmark_performance`：原实现只匹配 `§3` 冒号行，真实 004393 披露在净值表现表中；PDF 表头包含换行，如 `份额净值\n增长率①`、`业绩比较\n基准收益\n率③`，直接字符串匹配失败。
- `manager_strategy_text`：原实现只匹配 `投资策略：`、`后市展望：` 行，真实 004393 披露在 `4.4.1 报告期内基金投资策略和运作分析`、`4.5 管理人对宏观经济、证券市场及行业走势的简要展望` 标题后的正文块。
- Follow-up：标题块停止条件曾使用过宽的 `_SECTION_HEADING_PATTERN`，会把正文中以 `14.68%，...` 开头的百分比句子误判为小节标题，导致 004393 的 `strategy_summary` 在“沪深300指数全年上涨”处提前截断。已收紧为“1-2 位报告编号 + 点号 + 1-2 位子编号 + 可选第三级编号 + 至少一个空白 + 标题文本”。
- `manager_alignment`：原实现只匹配 `§9` 冒号行，真实 004393 披露在从业人员持有表和基金经理持有区间表中。
- `holder_structure`：真实 004393 的持有人结构表存在跨页组表头，`机构投资者/个人投资者` 在 page 62，数据列在 page 63，原实现没有表格/跨页识别。
- `share_change`：原 detector 要求 `净变动` 关键词，真实 004393 的 `§10` 表按期初、总申购、总赎回、期末拆分披露；第一次放宽后曾误命中 page 35 未分配利润变动表，已通过要求 `基金份额总额` 和回归测试收紧。

## Changed Files

- `fund_agent/fund/extractors/performance.py`
  - 新增 `§3` 净值表现表格兜底抽取。
  - 对表头语义匹配压缩内部空白，支持 PDF 换行表头。
  - 净值增长率/基准收益率表头匹配排除“标准差”列，避免列序变化时静默抽错。
  - 优先选择 `过去一年` 行，并生成 page/table anchor。
- `fund_agent/fund/extractors/manager_ownership.py`
  - 新增 `§4` 编号标题正文块抽取。
  - 新增 `§9` 从业人员/基金经理持有表抽取。
  - 新增持有人结构跨页组表头识别，并保留 page/table anchor。
  - 跨页持有人结构 fallback 只接受 0-100 的比例值，避免把份额列误作个人持有人比例。
- `fund_agent/fund/extractors/holdings_share_change.py`
  - 新增申购/赎回拆分型 `§10` 份额变动表识别。
  - 缺少净变动行时以期末份额减期初份额计算 `net_change`。
  - 多份额列场景取行标签后的首个有效份额值，避免误取 C 类份额。
  - 收紧 detector，避免把未分配利润变动表误判为份额变动表。
- `tests/fund/extractors/test_performance.py`
  - 增加 004393-like 换行表头净值表现表测试。
  - 增加“标准差列在收益率列之前”时仍抽取收益率列的回归测试。
- `tests/fund/extractors/test_manager_ownership.py`
  - 增加编号标题策略正文测试。
  - 增加正文百分比行不截断策略块的回归断言。
  - 增加 §9 持有表和跨页持有人结构表测试。
  - 增加跨页续表相邻比例列和非比例相邻列的回归测试。
- `tests/fund/extractors/test_holdings_share_change.py`
  - 增加申购/赎回拆分表测试。
  - 增加未分配利润变动表误命中回归测试。
- `fund_agent/fund/README.md`
  - 同步当前 extractor 支持的表格/标题块/跨页表头行为。
- `tests/README.md`
  - 同步 extractor 测试覆盖面和维护约定。

## Verification

```bash
.venv/bin/pytest tests/fund/extractors/test_performance.py tests/fund/extractors/test_manager_ownership.py tests/fund/extractors/test_holdings_share_change.py
```

结果：`17 passed in 0.38s`。

Controller 复核时同时运行：

```bash
.venv/bin/python -m pytest tests/fund/extractors/test_performance.py tests/fund/extractors/test_manager_ownership.py tests/fund/extractors/test_holdings_share_change.py tests/fund/test_extraction_snapshot.py -q
```

结果：`21 passed in 0.43s`。

```bash
.venv/bin/ruff check fund_agent/fund/extractors/performance.py fund_agent/fund/extractors/manager_ownership.py fund_agent/fund/extractors/holdings_share_change.py tests/fund/extractors/test_performance.py tests/fund/extractors/test_manager_ownership.py tests/fund/extractors/test_holdings_share_change.py
```

结果：`All checks passed!`。

Follow-up 验证：

```bash
.venv/bin/pytest tests/fund/extractors/test_manager_ownership.py
```

结果：`6 passed in 0.52s`。

```bash
.venv/bin/ruff check fund_agent/fund/extractors/manager_ownership.py tests/fund/extractors/test_manager_ownership.py
```

结果：`All checks passed!`。

```bash
.venv/bin/python -c '... FundDocumentRepository().load_annual_report("004393", 2024) ...'
```

结果：真实 004393 的 `manager_strategy_text.strategy_summary` 包含 `沪深300指数全年上涨 14.68%，结束了连续3年的下跌态势。`，未在百分比句子处提前截断。

```bash
.venv/bin/fund-analysis extraction-snapshot --run-id p4-s3b-004393-check --fund-code 004393 --report-year 2024
```

结果：

- `snapshot`: `reports/extraction-snapshots/p4-s3b-004393-check/snapshot.jsonl`
- `summary`: `reports/extraction-snapshots/p4-s3b-004393-check/summary.md`
- `errors`: `reports/extraction-snapshots/p4-s3b-004393-check/errors.jsonl`
- `errors.jsonl`: `0` bytes

Controller final run：

```bash
.venv/bin/fund-analysis extraction-snapshot --run-id p4-s3b-004393-final --fund-code 004393 --report-year 2024
.venv/bin/fund-analysis extraction-score --snapshot-path reports/extraction-snapshots/p4-s3b-004393-final/snapshot.jsonl --output-dir reports/extraction-snapshots/p4-s3b-004393-final-score
```

结果：

- `reports/extraction-snapshots/p4-s3b-004393-final/summary.md` 显示 5 个本 slice 字段均为 `100.0%` coverage / traceability。
- `reports/extraction-snapshots/p4-s3b-004393-final-score/score.md` 显示 `pass=9`、`fail=5`，`p0_status=fail`。
- `p0_status=fail` 的原因是 `fee_schedule` 仍缺失；这是本 slice 有意保留的语义边界，不把费用金额误作费率。
- `reports/extraction-snapshots/p4-s3b-004393-final/errors.jsonl` 为 `0` bytes。

Controller accepted-finding follow-up：

```bash
.venv/bin/python -m pytest tests/fund/extractors/test_performance.py tests/fund/extractors/test_manager_ownership.py tests/fund/extractors/test_holdings_share_change.py -q
```

结果：`20 passed in 0.71s`。

```bash
.venv/bin/ruff check fund_agent/fund/extractors/performance.py fund_agent/fund/extractors/manager_ownership.py fund_agent/fund/extractors/holdings_share_change.py tests/fund/extractors/test_performance.py tests/fund/extractors/test_manager_ownership.py tests/fund/extractors/test_holdings_share_change.py
```

结果：`All checks passed!`。

```bash
git diff --check
.venv/bin/fund-analysis extraction-snapshot --run-id p4-s3b-004393-controller-final --fund-code 004393 --report-year 2024
.venv/bin/fund-analysis extraction-score --snapshot-path reports/extraction-snapshots/p4-s3b-004393-controller-final/snapshot.jsonl --output-dir reports/extraction-snapshots/p4-s3b-004393-controller-final-score
```

结果：

- `reports/extraction-snapshots/p4-s3b-004393-controller-final/summary.md` 显示 5 个本 slice 字段均为 `100.0%` coverage / traceability。
- `reports/extraction-snapshots/p4-s3b-004393-controller-final-score/score.md` 显示 `pass=9`、`fail=5`、`p0_status=fail`。
- `reports/extraction-snapshots/p4-s3b-004393-controller-final/errors.jsonl` 为 `0` bytes。

## Snapshot Improvement

相对 `reports/extraction-snapshots/p4-s3a-004393-rereview/summary.md`：

| field | P4-S3a | P4-S3b |
|---|---:|---:|
| `nav_benchmark_performance` | 0.0% coverage / 0.0% traceability | 100.0% / 100.0% |
| `manager_strategy_text` | 0.0% / 0.0% | 100.0% / 100.0% |
| `manager_alignment` | 0.0% / 0.0% | 100.0% / 100.0% |
| `holder_structure` | 0.0% / 0.0% | 100.0% / 100.0% |
| `share_change` | 0.0% / 0.0% | 100.0% / 100.0% |

真实 004393 抽取值抽查：

- `nav_benchmark_performance`: `nav_growth_rate=17.32%`, `benchmark_return_rate=14.45%`, anchor `§3 page-8-table-0`。
- `manager_strategy_text`: `strategy_summary` 与 `market_outlook` 均来自 `§4` 标题块。
- `manager_alignment`: anchor `§9 page-63-table-2` 与 `§9 page-63-table-1`。
- `holder_structure`: `institutional_holder=86.46`, `individual_holder=13.54`, anchor `§9 page-63-table-0`。
- `share_change`: `beginning_share=27,666,410.41`, `ending_share=149,565,740.00`, `net_change=121,899,329.59`, anchor `§10 page-64-table-0`。

仍为 0.0% 的字段：

- `fee_schedule`：本 slice 明确不处理，避免把实际支付金额误当费率。
- `investor_return`：年报未直接披露，后续需要 fallback 设计。
- `turnover_rate`：本 slice 未覆盖。
- `holdings_snapshot`：真实 §8 持仓表标题/表格形态需要单独设计，避免过拟合。

## Residual Risks

- 表格跨页拼接仍依赖 `ParsedTable` 顺序和相邻页表格形态；更多基金可能出现非相邻页或更复杂多行表头，需要后续在文档解析层或 extractor 层补更通用的表格语义结构。
- `manager_alignment` 当前保留整表文本作为原始披露，便于证据追溯，但还没有拆成 A/C 份额级别结构；这符合当前字段“原始披露”边界，不应在本 slice 输出利益一致性判断。
- `share_change` 多份额列当前取首个有效份额列，适配 004393 A 份额；如果未来按 C 份额基金代码抽取，需要明确份额级别选择策略。
- `holdings_snapshot` 未在本 slice 修复，因为真实 §8 表格识别需要更稳健的持仓/行业语义规则。
