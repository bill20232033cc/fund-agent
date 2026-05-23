# P19-S3 Code Review - Mimo - 2026-05-23

## Findings

### Blocker - 自动估值没有校验温度计返回的指数身份，可能用错误指数改写 `valuation_state`

- 文件/行号：`fund_agent/services/fund_analysis_service.py:519-549`, `fund_agent/fund/analysis/valuation_state.py:332-390`
- 直接证据：Service 先用 `resolve_valuation_index_target(...)` 得到 `target.index_code`，再调用 `ThermometerRequest(index_code=target.index_code)`；但收到 `ThermometerReading` 后只检查类型，直接 `build_thermometer_valuation_resolution(result)`，没有断言 `result.index_code == target.index_code`、`result.index_name == target.index_name` 或返回身份属于本次映射目标。
- 触发路径：如果 thermometer provider、缓存污染或实现回归在请求 `000300` 时返回 `ThermometerReading(index_code="000905", valuation_state_candidate="low")`，`analyze` 会把中证500温度作为该沪深300基金的估值状态，报告、checklist、renderer 和 R1 都会围绕返回的 `000905` resolution 自洽通过。
- 影响：违反 P19-S3 “只对 exact benchmark identity 为 000300/000905 自动调用并映射”的根契约。当前 R1 校验的是 `ValuationStateResolution` 内部字段与锚点一致，不知道 Service 原本请求的 target，因此无法捕获“请求指数”和“返回指数”错配。
- 建议：在 `FundAnalysisService._resolve_valuation_state()` 中，`isinstance(result, ThermometerReading)` 后立即校验 `result.index_code == target.index_code`，必要时也校验 `target.index_name`；错配属于 provider/cache 编程契约错误，应 `ValueError` fail-closed。补充 Service 测试：mapped `000300` 但 fake provider 返回 `000905` 必须失败，而不是生成 resolution。

### Medium - `ThermometerCalculationError` 灰灯路径的 evidence anchors 没有记录温度计失败 provenance

- 文件/行号：`fund_agent/services/fund_analysis_service.py:535-546`, `fund_agent/fund/audit/audit_programmatic.py:1084-1118`
- 直接证据：自动温度计调用抛出 `ThermometerCalculationError` 时，Service 构造 `source="unavailable_thermometer"` 的 `ValuationStateResolution`，但 `anchors=target.anchors`。这些锚点来自年报 benchmark/index_profile，只证明为什么会尝试某个指数，不记录本次温度计调用失败、失败原因或自建温度计 provenance。R1 对 `unavailable_thermometer` 只要求 `state=unavailable` 和 `reason/unavailable_reason` 非空；若 `disclaimer_required=True`，只检查 disclaimer 字段和报告可见性，不要求 anchor 里出现 unavailable reason。
- 触发路径：支持指数基金默认自动估值，fake/生产 provider 在计算阶段抛 `ThermometerCalculationError("样本不足")`。报告正文 reason 会有“样本不足”，但证据附录里的估值锚点仍是年报基准锚点，不包含“样本不足”或温度计调用失败来源。
- 影响：P19-S3 计划要求 unavailable thermometer 路径保留足以支撑 R1 和证据锚点的 provenance，且 unavailable reason 应进入对应 anchor note。当前结构化 reason 可用，但 evidence anchor 不足，审计也不会发现此缺口。
- 建议：为 `ThermometerCalculationError` 路径构造专门的 `derived` 估值锚点，例如 `section_id="thermometer"`, `row_locator=f"{target.index_code}:calculation_error"`, `note` 包含异常类型、原因、目标指数和 disclaimer；R1 对 `source="unavailable_thermometer"` 且无 external_api anchor 的路径，应要求至少一个 thermometer/valuation derived anchor 携带 unavailable reason。

### Low - Fund README 仍有旧口径，称第 6 问只消费显式 `valuation_state`

- 文件/行号：`fund_agent/fund/README.md:239`
- 直接证据：文档仍写“当前估值处于什么位置：消费调用方显式传入的 `valuation_state`”。同一 README 后文已经记录 P19-S3 自动估值和 `ValuationStateResolution`，但该旧句会让读者以为当前 checklist 仍只有显式输入路径。
- 影响：不影响运行时正确性，但违反本轮“README 只描述当前实现，不设计未来/不保留旧口径”的文档同步要求。
- 建议：后续修复代码时同步把该 bullet 改为“消费 `ValuationStateResolution`；无 resolution 的旧兼容路径才退回显式 `valuation_state`”。

## Residual risks

- 未执行 live akshare/Legulegu smoke；本次验证只覆盖 fixture 和 fake provider。外部接口可用性、schema drift 和真实缓存内容仍是外部数据风险。
- `FundAnalysisService` 默认注入的是 `ThermometerService()`，`analyze` 自动路径只传 `index_code`，未看到调用 `FundThermometerAdapter` 公开页、all-A、Dayu 或 `extra_payload`；但 `ThermometerService` 本身仍保留无 index 的公开页查询能力，后续改动需继续防止 analyze 路径误走 no-index 分支。
- `ProgrammaticAuditInput.valuation_state_resolution` 仍是可选字段以兼容旧测试；当前 Service/renderer 会传同一个 resolution，但若未来绕过 renderer 手工构造 audit input，R1 对无 external anchor 的缺失 resolution 仍可能兼容放行。
- 已运行验证：

```bash
.venv/bin/python -m pytest tests/fund/analysis/test_valuation_state.py tests/fund/analysis/test_checklist.py tests/services/test_fund_analysis_service.py tests/ui/test_cli.py tests/fund/audit/test_audit_programmatic.py tests/fund/template/test_renderer.py -q
.venv/bin/python -m ruff check fund_agent tests
git diff --check dc4ea04^ dc4ea04
```

结果：targeted pytest `158 passed in 0.69s`；ruff passed；diff check passed。

## Verdict

BLOCKED
