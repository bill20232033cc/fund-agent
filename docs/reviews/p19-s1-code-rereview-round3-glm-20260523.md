# P19-S1 Code Re-review Round 3 - GLM Reviewer

日期：2026-05-23
复审对象：`HEAD` commit `3ea3d80`
范围：P19-S1 自建沪深300指数温度计 MVP；不评审全 A、PB-only 全 A 或 `fund-analysis analyze` 集成。

## Verdict

PASS

未发现阻塞性 finding。上一轮 round 2 blocker 已关闭：字符串日期现在使用原始 `str(value)` 做完整 `YYYY-MM-DD` 匹配，不再截断，也不再 trim；带时间、尾随字符、首尾空白都会 fail-closed。

## Findings

无阻塞或非阻塞 finding。

## Evidence

### 1. Strict string-date contract 已闭合

直接证据：

- `fund_agent/fund/data/thermometer_source.py:219-228`
  - `text = str(value)` 使用原始字符串；
  - 没有 `strip()`；
  - 没有 `[:10]` 截断；
  - `ISO_DATE_PATTERN.fullmatch(text)` 要求完整匹配；
  - `datetime.strptime(text, "%Y-%m-%d")` 继续拒绝 `2026-02-30` 这类形状正确但非法的日期。

测试证据：

- `tests/fund/data/test_thermometer_source.py:153-183` 覆盖：
  - `2026-05-22T00:00:00`
  - `2026-05-22 00:00:00`
  - `2026-05-22abc`
  - ` 2026-05-22`
  - `2026-05-22 `
  - ` 2026-05-22 `

手工探针验证结果：

- 接受：`date(2026, 5, 22)`、`datetime(2026, 5, 22, 1, 2, 3)`、`"2026-05-22"`
- 拒绝：`"2026-05-22T00:00:00"`、`"2026-05-22 00:00:00"`、`"2026-05-22abc"`、`" 2026-05-22"`、`"2026-05-22 "`、`" 2026-05-22 "`、`"20260522"`、`"2026/05/22"`、`"2026-02-30"`

### 2. `date` / `datetime` 对象仍被接受

直接证据：

- `fund_agent/fund/data/thermometer_source.py:215-218`
  - `datetime` 先转 `value.date().isoformat()`；
  - `date` 转 `value.isoformat()`。

测试证据：

- `tests/fund/data/test_thermometer_source.py:186-206` 覆盖 `date` 对象标准化。
- 手工探针覆盖 `datetime` 对象标准化。

### 3. 先前 accepted findings 未回归

样本不足 fail-closed：

- `fund_agent/fund/analysis/thermometer_calculator.py:18`
- `fund_agent/fund/analysis/thermometer_calculator.py:45-48`
- `tests/services/test_thermometer_service.py:297-316`

cache save 失败仍使用 fresh history：

- `fund_agent/services/thermometer_service.py:204-208`
- `tests/services/test_thermometer_service.py:272-293`

Service failure domains 仍拆开：

- `fund_agent/services/thermometer_service.py:189-203` 只捕获 `ThermometerSourceError`，数据源不可用才走 stale cache / unavailable。
- `fund_agent/services/thermometer_service.py:204-208` 只把 `OSError` 缓存写失败降级为 fresh in-memory history。
- 计算契约错误不被 source fallback 掩盖，测试见 `tests/services/test_thermometer_service.py:297-316`。

### 4. 范围未扩张

直接证据：

- `fund_agent/fund/data/thermometer_source.py:19` 仅支持 `{"000300": "沪深300"}`。
- `fund_agent/ui/cli.py:245-292` 自建温度计只通过 `fund-analysis thermometer --index` 进入。
- `fund_agent/services/thermometer_service.py:156-160` 只有显式 `ThermometerRequest.index_code` 分支进入自建指数温度计；未接入 `FundAnalysisService.analyze`。
- `rg` 检查未发现 `fund_agent/services/fund_analysis_service.py` 调用 `ThermometerService`、`load_index_history` 或 `calculate_thermometer_reading`。

## Residual Risks

- akshare 实盘返回字段仍依赖 `滚动市盈率中位数`、`市净率中位数`、`日期`。当前实现按 fail-closed 处理 schema drift，这是符合 P19-S1 边界的风险接受方式，不构成本轮 blocker。
- 当前复审只覆盖 P19-S1 自建沪深300指数温度计 MVP，没有评审后续全 A 方案、PB-only 全 A 或基金分析报告集成。

## Validation Notes

已执行：

```bash
.venv/bin/python -m pytest tests/fund/data/test_thermometer_source.py tests/fund/analysis/test_thermometer_calculator.py tests/fund/data/test_thermometer_cache.py tests/services/test_thermometer_service.py tests/ui/test_cli.py tests/fund/data/test_thermometer.py -q
```

结果：`60 passed in 0.50s`

已执行：

```bash
.venv/bin/python -m ruff check fund_agent/fund/data/thermometer_source.py fund_agent/fund/analysis/thermometer_calculator.py fund_agent/services/thermometer_service.py tests/fund/data/test_thermometer_source.py tests/services/test_thermometer_service.py
```

结果：`All checks passed!`

工作区说明：复审前 `git status --short` 仅显示既有未跟踪草稿 `docs/design0522.md`、`docs/implementation-control0522.md`、`docs/repo-audit-20260521.md`；本复审未读取或修改这些草稿。
