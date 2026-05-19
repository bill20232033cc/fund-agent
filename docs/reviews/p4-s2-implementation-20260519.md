# P4-S2 Implementation Artifact

## Scope

本次实现 P4-S2 前半段：在 P4-S1 `snapshot.jsonl` 之上计算字段级 coverage / traceability，并选择最小 golden set。未实现 correctness 评分，也未引入人工 golden answer。

## Changed Paths

- `fund_agent/fund/extraction_score.py`
- `fund_agent/services/extraction_score_service.py`
- `fund_agent/services/__init__.py`
- `fund_agent/ui/cli.py`
- `tests/fund/test_extraction_score.py`
- `tests/services/test_extraction_score_service.py`
- `tests/ui/test_cli.py`
- `README.md`
- `fund_agent/fund/README.md`
- `tests/README.md`
- `docs/implementation-control-p4.md`
- `docs/implementation-control.md`
- `docs/reviews/p4-s2-implementation-20260519.md`

## Field Priority Mapping

P0:

- `basic_identity`
- `classified_fund_type`
- `benchmark`
- `nav_benchmark_performance`
- `fee_schedule`
- `manager_strategy_text`

P1:

- `product_profile`
- `turnover_rate`
- `holder_structure`
- `manager_alignment`
- `holdings_snapshot`
- `share_change`

P2:

- `investor_return`
- `nav_data`

该映射未调整用户指定清单。仅在文档中补充了自然语言字段到当前 `field_name` 的解释关系，程序仍以 P4-S1 snapshot 的 snake_case 字段名为唯一输入。

## Scoring

`fund_agent.fund.extraction_score` 新增：

- `score_snapshot_records(...)`：消费内存中的 snapshot 记录，输出字段级 `FieldScoreRow`
- `run_extraction_score(...)`：读取 `snapshot.jsonl`，写出 `score.json`、`score.md`、`golden_set.json`
- `select_minimal_golden_set(...)`：从 `docs/code_20260519.csv` 选择最小 golden set

评分阈值为显式常量：

- `pass`：coverage >= 90% 且 traceability >= 90%
- `watch`：coverage >= 70% 且 traceability >= 70%
- `fail`：其余情况

Traceability 口径为 `anchor_present=True` 的记录数 / 该字段总记录数，和 P4-S1 summary 同源。

## Golden Set

当前最小 golden set 选择规则：

- 固定包含 `004393`
- 黄金类、海外股票类、海外债券/稳健类、国内债券类各 1 只
- 国内股票类至少 2 只，其中包含 `004393` 和额外 1 只
- 所有代码只来自 `docs/code_20260519.csv`
- 暂时排除货币基金类；原因是当前 8 章模板对货币基金适配度较低，作为 edge case 记录在 `golden_set.json`

## CLI / Service Boundary

新增 `fund-analysis extraction-score`：

```bash
fund-analysis extraction-score \
  --snapshot-path reports/extraction-snapshots/p4-s1-selected-1x/snapshot.jsonl
```

UI 层只解析参数并调用 `ExtractionScoreService`；Service 只做显式请求校验并委托 Capability 层。评分不访问 PDF、cache、文档仓库或网络。

## Verification

已运行：

```bash
.venv/bin/python -m pytest tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py tests/services/test_extraction_snapshot_service.py tests/services/test_extraction_score_service.py tests/ui/test_cli.py -q
.venv/bin/python -m ruff check fund_agent/fund/extraction_score.py fund_agent/services/extraction_score_service.py fund_agent/ui/cli.py tests/fund/test_extraction_score.py tests/services/test_extraction_score_service.py tests/ui/test_cli.py
.venv/bin/fund-analysis extraction-score --help
git diff --check
```

结果：

```text
17 passed
All checks passed!
extraction-score command registered
diff check passed
```

## Residual Risks

- Correctness 仍未实现，无法判断抽取值是否正确，只能判断是否存在值和证据锚点。
- `nav_data` 当前来自净值适配器，没有年报证据锚点，因此 traceability 在该字段上会自然偏低；这属于当前 P4-S2 前半段的真实基线。
- Golden set 当前按 CSV 顺序 deterministic 选择，不代表业务最优样本；后续人工 golden answer 建立时可调整。
