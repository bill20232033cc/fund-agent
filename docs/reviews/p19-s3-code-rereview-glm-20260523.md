# P19-S3 Code Review Fix Re-review - GLM - 2026-05-23

## Findings

未发现阻断或新增 correctness / 边界 finding。原 controller judgment 中的 blocker 已由当前未提交 diff 关闭：

- 温度计返回指数身份错配已 fail-closed。`FundAnalysisService._resolve_valuation_state()` 在构造 `ValuationStateResolution` 前检查 `result.index_code != target.index_code` 并抛出 `ValueError`，因此错配读数不会进入 renderer / checklist / R1，也不能被后续结构字段自洽掩盖。证据：`fund_agent/services/fund_analysis_service.py:528-563`；回归测试：`tests/services/test_fund_analysis_service.py:611-634`。
- `ThermometerCalculationError` 会转为 `unavailable_thermometer` 灰灯，并补充 derived failure anchor。该 anchor 记录 `section_id=thermometer`、`table_id=self_owned_thermometer`、`row_locator={index_code}:calculation_error`，note 包含 `index_code`、`index_name`、`unavailable_reason` 和免责声明；R1 对 `unavailable_thermometer` 要求 external_api thermometer anchor 或包含失败原因的 derived thermometer failure anchor。证据：`fund_agent/services/fund_analysis_service.py:536-555`、`fund_agent/fund/analysis/valuation_state.py:398-430`、`fund_agent/fund/audit/audit_programmatic.py:1084-1102`、`fund_agent/fund/audit/audit_programmatic.py:1123-1157`；回归测试：`tests/services/test_fund_analysis_service.py:581-609`、`tests/fund/audit/test_audit_programmatic.py:1415-1501`。
- `benchmark_index_code` 不再无条件绕过同源文本。支持代码命中后会校验同源 benchmark / index profile 文本；派生、策略、行业或其他支持宽基混合会 fail-closed，现金/债券成分被视为可忽略配比成分。证据：`fund_agent/fund/analysis/valuation_state.py:188-207`、`fund_agent/fund/analysis/valuation_state.py:480-552`、`fund_agent/fund/analysis/valuation_state.py:611-638`；派生冲突回归测试：`tests/fund/analysis/test_valuation_state.py:253-289`；正常 000300 + 债券权重组合已有无代码路径测试：`tests/fund/analysis/test_valuation_state.py:109-115`，本次 re-review 也用当前实现临时验证了 `benchmark_index_code=000300` + `沪深300指数收益率*80% + 中证全债指数收益率*20%` 仍映射为 `mapped / 000300`。
- README 已与当前实现口径一致：检查清单消费 `ValuationStateResolution`，`analyze` 只在缺省估值输入时对 exact identity 映射到 000300 / 000905 的指数基金或指数增强基金使用项目内自建温度计；全 A 被明确列为 P19-S5 待实现。证据：`fund_agent/fund/README.md:239-256`、`fund_agent/fund/README.md:303-320`、`README.md:82-89`、`README.md:116-121`、`README.md:169-178`。
- 自动 analyze 路径仍只通过注入的自建 `ThermometerService` 调用 `ThermometerRequest(index_code=target.index_code)`；未发现 `FundThermometerAdapter`、页面抓取、all-A、Dayu 或 `extra_payload` 混入主链路。证据：`fund_agent/services/fund_analysis_service.py:92-102`、`fund_agent/services/fund_analysis_service.py:353-360`、`fund_agent/services/fund_analysis_service.py:528-535`。

## Residual risks

- R1 对 derived calculation-error failure anchor 的证明重点是 `source_kind=derived`、`section_id=thermometer`、`row_locator` 以 `:calculation_error` 结尾且 note 包含 `unavailable_reason`；它没有单独断言 note 中的 `index_code` / `index_name` 与 `ValuationStateResolution` 一致。当前 Service 统一使用 `build_thermometer_failure_anchor()`，会写入这些字段，因此不构成 blocker；若未来出现手写 `unavailable_thermometer` resolution，建议补一条 R1 单测或审计条件覆盖身份字段一致性。
- 对 `benchmark_index_code=000300/000905` 且同源文本为“宽基 exact identity + 现金/债券权重组合”的路径，本次 re-review 已临时验证当前行为不会过度拒绝；但现有提交内的持久测试主要覆盖无 `benchmark_index_code` 的正常组合和有 `benchmark_index_code` 的派生冲突。建议后续补一个显式回归测试，防止代码优先兼容校验被误改。

本次验证命令均通过：

- `.venv/bin/python -m pytest tests/fund/analysis/test_valuation_state.py tests/fund/analysis/test_checklist.py tests/services/test_fund_analysis_service.py tests/ui/test_cli.py tests/fund/audit/test_audit_programmatic.py tests/fund/template/test_renderer.py -q`：163 passed
- `.venv/bin/python -m pytest -q`：537 passed
- `.venv/bin/python -m ruff check fund_agent tests`：All checks passed
- `git diff --check`：通过

## Verdict

PASS

没有 blocking finding。当前 P19-S3 code review fix 足以关闭 controller judgment 中的 blocker，且未看到新增用户可见 CLI contract、自动数据入口、R1 审计或 benchmark identity 边界问题。
