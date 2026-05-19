# P4-S3a Implementation: 004393 Fund Type Classification Fix

> 日期：2026-05-19
> Gate：`P4-S3a implementation`
> 范围：仅修复 `004393` 类型误判，不扩展 `§3/§4/§8/§9/§10` extractor

## Root Cause

`004393 安信企业价值优选混合A` 的已解析年报通过 `ParsedAnnualReport` 读取后，分类器输入为：

- `fund_name=安信企业价值优选混合`
- `fund_category=`（当前抽取为空）
- `benchmark=沪深300指数收益率×60%+恒生指数收益率（经汇率调整后）×20%+中债综合（全价）指数收益率×20%`
- `investment_objective=本基金在有效控制组合风险并保持基金资产流动性的前提下，力争实现基金资产的长期稳健增值。`
- `investment_strategy=资产配置、股票基本面分析、估值分析、港股通、债券等主动管理策略`

旧规则把 `fund_name + benchmark` 拼接后匹配 `_INDEX_NAME_KEYWORDS`。其中 `价值` 命中基金名，`沪深300` 命中业绩比较基准，导致在 `fund_category` 缺失时直接返回 `index_fund`。

这个 root cause 与代码和数据同源，不依赖报告肉眼判断。

## Implementation

本次修复收窄指数基金触发条件：

- 业绩比较基准不再单独触发 `index_fund`。
- 删除宽泛风格词 `价值`、`质量`、`红利`、`低波` 等作为指数身份触发词的路径。
- 指数基金需要基金名称/类别中有明确指数身份，或投资目标/范围/策略中出现 `标的指数`、`跟踪指数`、`紧密跟踪`、`复制法` 等策略证据。
- 增加 `investment_objective` / `investment_strategy` 作为分类输入，但仍只读取 `§1/§2` 与表格契约。

Code review follow-up 后进一步收窄策略证据：

- `紧密跟踪` 不再作为独立关键词，避免主动基金“紧密跟踪市场动态”误判为指数基金。
- 保留 `紧密跟踪标的指数`、`紧密跟踪指数` 等显式指数语义。
- 新增主动基金回归测试，锁定“紧密跟踪市场动态 + 基准含沪深300”仍应分类为 `active_fund`。

变更文件：

- `fund_agent/fund/fund_type.py`
- `tests/fund/extractors/test_profile.py`
- `fund_agent/fund/README.md`

## Tests And Verification

已运行：

```bash
.venv/bin/python -m pytest tests/fund/extractors/test_profile.py tests/fund/test_extraction_snapshot.py -q
# 12 passed

.venv/bin/python -m pytest tests/fund/integration/test_p1_sample_matrix.py tests/fund/integration/test_p3_cli_e2e_matrix.py -q
# 2 passed

.venv/bin/python -m ruff check fund_agent/fund/fund_type.py tests/fund/extractors/test_profile.py
# All checks passed

git diff --check
# passed
```

Code review follow-up 后复跑：

```bash
.venv/bin/python -m pytest tests/fund/extractors/test_profile.py tests/fund/test_extraction_snapshot.py tests/fund/integration/test_p1_sample_matrix.py tests/fund/integration/test_p3_cli_e2e_matrix.py -q
# 15 passed

.venv/bin/python -m ruff check fund_agent/fund/fund_type.py tests/fund/extractors/test_profile.py
# All checks passed

git diff --check
# passed
```

真实缓存复核：

```bash
.venv/bin/python - <<'PY'
from fund_agent.fund.documents.models import ParsedAnnualReport
from fund_agent.fund.fund_type import classify_fund_type
import json
from pathlib import Path

payload = json.loads(Path("cache/documents/parsed_reports/004393_2024_annual_report.json").read_text(encoding="utf-8"))
report = ParsedAnnualReport.from_dict(payload)
print(classify_fund_type(report))
PY
```

输出显示：

```text
FundTypeClassification(classified_fund_type='active_fund', ...)
```

真实 snapshot / score smoke：

```bash
.venv/bin/fund-analysis extraction-snapshot --run-id p4-s3a-004393-check --fund-code 004393 --report-year 2024
.venv/bin/fund-analysis extraction-score --snapshot-path reports/extraction-snapshots/p4-s3a-004393-check/snapshot.jsonl --output-dir reports/extraction-snapshots/p4-s3a-004393-check-score
```

`reports/extraction-snapshots/p4-s3a-004393-check/summary.md` 显示：

```text
| 004393 | 安信企业价值优选混合A | 国内股票类 | succeeded | active_fund |  |
```

`score.md` 显示 `classified_fund_type` coverage / traceability 均为 `100.0%`，但 `p0_status` 仍为 `fail`，因为 `fee_schedule`、`nav_benchmark_performance`、`manager_strategy_text` 等高影响字段仍缺失。

Follow-up 复核：

```bash
.venv/bin/fund-analysis extraction-snapshot --run-id p4-s3a-004393-rereview --fund-code 004393 --report-year 2024
```

`reports/extraction-snapshots/p4-s3a-004393-rereview/summary.md` 显示：

```text
| 004393 | 安信企业价值优选混合A | 国内股票类 | succeeded | active_fund |  |
```

## Residual Risk

- 当前分类仍是基于 `§1/§2` 的启发式规则。若真实指数基金的名称/类别缺失，且策略文本也未被抽取到，可能回退为 `active_fund`。
- 本 slice 不修复 `§3/§4/§8/§9/§10` 字段缺失。P4-S3b 应继续使用本次 snapshot/score 输出定位高影响 extractor 缺口。
