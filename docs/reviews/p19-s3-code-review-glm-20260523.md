# P19-S3 自动估值温度集成独立 Code Review（GLM, 2026-05-23）

## Findings

### MEDIUM - F1：`benchmark_index_code` 优先路径缺少与基准文本的同源冲突校验

证据：

- `fund_agent/fund/analysis/valuation_state.py:188`-`202` 在 `index_profile.value.benchmark_index_code` 非空时直接按代码映射，命中 `000300` / `000905` 即返回 `mapped`。
- 这条路径不会再检查同一个 `IndexProfileValue` 上的 `benchmark_text`、`benchmark_index_name` 或 `benchmark_component_text` 是否为 strict identity，也不会在文本是“沪深300价值/成长/红利低波/等权”或“中证500质量成长/低波/行业”时 fail closed。
- 当前生产 extractor 在 `fund_agent/fund/extractors/profile.py:669`-`675` 仍把 `benchmark_index_code=None`，所以这不是当前真实年报路径的 blocking defect；但 `IndexProfileValue.benchmark_index_code` 是公开结构字段，P19-S3 新增测试 `tests/fund/analysis/test_valuation_state.py:230`-`250` 只证明“代码存在时优先映射”，没有覆盖“代码与派生指数文本冲突时拒绝”。

影响：

- 一旦后续 P1/P13/P16 代码开始填充 `benchmark_index_code`，如果上游从派生指数名称或基金名称里提取出宽基代码，P19-S3 会绕过本次最关键的 exact identity 防线，把派生/策略/行业指数误接到宽基温度计。
- 这会直接改变 `fund-analysis analyze` 检查清单第 6 问和最终判断派生路径，属于用户可见 correctness 风险。

建议：

- 在 code path 中把 `benchmark_index_code` 视为一个候选事实，而不是绝对覆盖：若同时存在基准文本/成分文本，必须验证其 normalized identity 与代码对应规则一致；冲突或派生修饰词存在时返回 `unsupported_index` / `ambiguous_benchmark`。
- 增加单测：`benchmark_index_code="000300"` + `benchmark_text="沪深300价值指数收益率"`、`benchmark_index_code="000905"` + `benchmark_text="中证500质量成长指数收益率"` 必须不调用温度计。

### LOW - F2：R1 对缺失 `ValuationStateResolution` 仍保留历史兼容通过分支，降低新审计契约的可证性

证据：

- `fund_agent/fund/audit/audit_programmatic.py:965`-`975` 在 `valuation_state_resolution is None` 时，只要 checklist valuation item 没有 `external_api` 锚点，就直接返回无问题。
- P19-S3 的实现目标是 `ValuationStateResolution` 作为 `FundAnalysisResult`、`TemplateRenderInput`、`ProgrammaticAuditInput` 的结构化真源；Service/renderer 当前确实传递了该对象，见 `fund_agent/services/fund_analysis_service.py:460`-`475` 和 `fund_agent/fund/template/renderer.py:157`-`165`。
- 但审计本身没有把“新路径缺少 resolution”作为 fail-closed 必需输入；`_audit_required_inputs()` 在 `fund_agent/fund/audit/audit_programmatic.py:189`-`238` 也不检查 `valuation_state_resolution`。

影响：

- 如果后续有新的 renderer/test helper/Service 分支忘记传 `valuation_state_resolution`，R1 可能仍按旧 checklist 形态通过，无法证明“R1 只看结构字段/anchors/disclaimer，不靠 reason 文本推断”的新契约始终生效。
- 当前主链路未受影响，因此不阻断 P19-S3。

建议：

- 在 `ProgrammaticAuditInput` 或 R1 审计中增加模式化约束：当报告来自当前 renderer 或 checklist valuation item 存在任何估值锚点时，缺失 `valuation_state_resolution` 应触发 R1。
- 增加回归测试：构造包含 valuation item 但缺失 resolution 的 P19-S3 audit input，确认新路径 fail closed；历史兼容需求如仍存在，应以显式 legacy flag 表达，而不是隐式通过。

## Residual risks

- `unavailable_thermometer` provenance 当前 Service fake 测试只断言 source/state/unavailable_reason（`tests/services/test_fund_analysis_service.py:553`-`574`），没有断言 report 中 disclaimer、anchors 和 appendix provenance。真实 `build_thermometer_valuation_resolution()` 对 unavailable reading 会生成 `external_api` anchor，但 calculation-error fallback 在 `fund_agent/services/fund_analysis_service.py:535`-`546` 只能保留 benchmark anchors，没有温度计 source/cached/stale 字段。
- Manual unavailable 已覆盖 Service 和 CLI 优先级：`tests/services/test_fund_analysis_service.py:466`-`487`、`tests/ui/test_cli.py:922`-`943`；默认 `None` 也覆盖了自动调用路径。
- 派生指数文本拒绝已覆盖常见名称：`tests/fund/analysis/test_valuation_state.py:170`-`203`；但没有覆盖“派生文本 + 错误 `benchmark_index_code`”的冲突输入。
- 自动 analyze 路径没有发现 `FundThermometerAdapter`、有知有行页面抓取、all-A、Dayu 或 `extra_payload` 混入。`FundAnalysisService` 只注入 `ThermometerService` 并发送 `ThermometerRequest(index_code=...)`。
- 已运行目标验证：

```text
.venv/bin/python -m pytest tests/fund/analysis/test_valuation_state.py tests/fund/analysis/test_checklist.py tests/services/test_fund_analysis_service.py tests/ui/test_cli.py tests/fund/audit/test_audit_programmatic.py tests/fund/template/test_renderer.py -q
158 passed in 0.68s

.venv/bin/python -m ruff check fund_agent tests
All checks passed!

git diff --check dc4ea04^ dc4ea04
passed with no output
```

## Verdict

PASS

没有 blocking finding。当前 P19-S3 主链路在显式输入优先级、自建温度计唯一自动入口、派生指数文本拒绝、自动不可用灰灯、R1 结构化真源传递和文档边界上总体成立；上述 findings 是非阻断的可证性和未来漂移风险。
