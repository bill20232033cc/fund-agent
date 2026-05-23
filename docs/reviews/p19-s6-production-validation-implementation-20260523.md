# P19-S6 Production Validation Implementation

## Scope

本次实现补强只覆盖 P19-S6 已接受计划中的确定性验证，不修改生产温度计算法、支持指数集合、数据源 fallback 或 `fund-analysis analyze` 行为。

## Changes

- `tests/services/test_fund_analysis_service.py`
  - 参数化 `_index_bundle()`，允许构造沪深300、中证500、不支持 exact code 与复合基准样本。
  - 新增中证500 exact identity 自动估值测试，断言 `ThermometerRequest.index_code == "000905"`。
  - 新增不支持 exact code `399006` 测试，断言保持 `unavailable_mapping` 且不调用温度计。
  - 新增沪深300 + 中证500 复合基准歧义测试，断言保持 `unavailable_mapping` 且不调用温度计。
- `tests/fund/integration/test_p3_cli_e2e_matrix.py`
  - 新增 fake thermometer service，避免 CLI e2e 触发真实 akshare。
  - 新增 510300 缺省 `--valuation-state` 样本，经过真实 Typer CLI、Service、P1/P2 Capability、模板渲染和程序审计，断言 exact benchmark 只请求 `000300`。
- `tests/README.md`
  - 同步 P19-S6 确定性回归组合。
  - 记录真实 `fund-analysis thermometer` 命令只作为人工 smoke，不进入常规 pytest。

## Validation

- `pytest tests/services/test_fund_analysis_service.py -q` -> 23 passed
- `pytest tests/fund/integration/test_p3_cli_e2e_matrix.py -q` -> 2 passed

后续仍需运行 P19-S6 完整确定性组合、ruff、diff check 和必要的 deepreview。

## Residual Risk

- 真实 akshare 可用性和本机 native dependency 状态仍只能由人工或 opt-in live smoke 证明；不应写入默认 pytest。
- 与有知有行页面方向比较仍是合理性信号，不是精确数值复刻承诺。
