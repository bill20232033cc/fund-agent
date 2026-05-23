# P19-S3 Code Review Fix（2026-05-23）

## Summary

本次修复关闭 `docs/reviews/p19-s3-code-review-controller-judgment-20260523.md` 中 P19-S3 阻断项。

## Fixes

1. **温度计返回指数身份 fail-closed**
   - `FundAnalysisService._resolve_valuation_state()` 在收到 `ThermometerReading` 后校验 `result.index_code == target.index_code`。
   - 错配时抛出 `ValueError`，不生成 `ValuationStateResolution`。
   - 新增 Service 回归测试：映射目标为 `000300`，fake provider 返回 `000905` 时失败。

2. **`ThermometerCalculationError` fallback provenance**
   - 新增 `build_thermometer_failure_anchor()`，生成 `source_kind="derived"`、`section_id="thermometer"`、`row_locator="<index_code>:calculation_error"` 的专用失败锚点。
   - 锚点 note 保留目标 `index_code`、`index_name`、`unavailable_reason` 和 self-owned thermometer/disclaimer context。
   - Service 计算异常路径现在同时保留 benchmark anchors 和 thermometer failure anchor。
   - R1 对 `source="unavailable_thermometer"` 要求存在 `external_api` thermometer anchor，或包含不可用原因的 derived thermometer failure anchor。

3. **`benchmark_index_code` 与同源文本冲突 hardening**
   - 支持代码 `000300` / `000905` 不再直接绕过文本校验。
   - 当 `benchmark_index_code` 同时存在基准文本/成分文本时，文本必须与同一 exact rule 或可忽略现金/债券成分兼容。
   - 派生、风格、行业、其他权益或不确定成分会返回 `unsupported_index` / `ambiguous_benchmark`，不调用温度计。
   - 新增单测覆盖 `000300 + 沪深300价值指数收益率`、`000905 + 中证500质量成长指数收益率`。

4. **README 旧口径修正**
   - `fund_agent/fund/README.md` 已改为：估值消费 `ValuationStateResolution`；显式 `valuation_state` 只是手动 override 和旧兼容投影。

5. **Capability export**
   - `fund_agent/fund/analysis/__init__.py` 导出 `build_thermometer_failure_anchor`。
   - 该导出是必要的：Service 使用 `fund_agent.fund.analysis` 聚合入口导入估值 resolution helper，避免绕过 Capability 公共入口。

## Validation

```text
.venv/bin/python -m pytest tests/fund/analysis/test_valuation_state.py tests/fund/analysis/test_checklist.py tests/services/test_fund_analysis_service.py tests/ui/test_cli.py tests/fund/audit/test_audit_programmatic.py tests/fund/template/test_renderer.py -q
```

Result:

```text
163 passed in 0.71s
```

```text
.venv/bin/python -m pytest -q
```

Result:

```text
537 passed in 1.08s
```

```text
.venv/bin/python -m ruff check fund_agent tests
```

Result:

```text
All checks passed!
```

```text
git diff --check
```

Result: passed with no output.

## Residual Risks

- 未运行 live akshare / Legulegu smoke；真实外部数据可用性和 schema drift 仍由现有温度计 source/cache 的 unavailable/fail-closed 语义覆盖。
- `ProgrammaticAuditInput.valuation_state_resolution` 仍保留历史可选兼容分支；当前 Service/renderer 主链路会传入 resolution。是否完全移除兼容分支应放到后续审计 hardening phase。
- 当前自动估值仍只支持沪深300 `000300` 和中证500 `000905`，不覆盖全 A、主动基金持仓估值、债券、QDII 或 FOF。
