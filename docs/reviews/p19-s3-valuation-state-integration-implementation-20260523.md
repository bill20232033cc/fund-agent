# P19-S3 Valuation State Integration Implementation（2026-05-23）

## Summary

P19-S3 已实现 `fund-analysis analyze` 的自动 thermometer-to-`valuation_state` 集成。

当前行为：

- `FundAnalysisRequest.valuation_state=None` 表示允许自动估值。
- 显式 `low/fair/high/unavailable` 都优先于自动路径，并且不调用温度计。
- 自动路径仅支持 `index_fund` / `enhanced_index`，且基准 exact identity 映射到沪深300 `000300` 或中证500 `000905`。
- 主动、债券、QDII、FOF、缺失/歧义/未支持/派生指数全部返回 `unavailable` 灰灯，不调用温度计。
- 自动路径只调用 self-owned `ThermometerService(ThermometerRequest(index_code=...))`，不使用 `FundThermometerAdapter` 公开页作为分析真源。
- `ValuationStateResolution` 是结构化真源，并传入 `FundAnalysisResult`、`TemplateRenderInput` 和 `ProgrammaticAuditInput`。
- 检查清单第 6 问只投影 resolution 的 state / reason / anchors；R1 审计不从 reason 文本反推来源。
- 温度计被调用后，报告第 7 章显示自建温度计免责声明，且未放宽 renderer forbidden-term guard。

## Changed Files

| Area | Files |
|---|---|
| Capability valuation model | `fund_agent/fund/analysis/valuation_state.py`, `fund_agent/fund/analysis/__init__.py` |
| Checklist projection | `fund_agent/fund/analysis/checklist.py` |
| Service orchestration | `fund_agent/services/fund_analysis_service.py` |
| CLI contract | `fund_agent/ui/cli.py` |
| Renderer and audit | `fund_agent/fund/template/renderer.py`, `fund_agent/fund/audit/audit_programmatic.py` |
| Tests | `tests/fund/analysis/test_valuation_state.py`, `tests/fund/analysis/test_checklist.py`, `tests/services/test_fund_analysis_service.py`, `tests/ui/test_cli.py`, `tests/fund/audit/test_audit_programmatic.py`, `tests/fund/template/test_renderer.py` |
| Docs | `README.md`, `fund_agent/README.md`, `fund_agent/fund/README.md`, `tests/README.md` |

## Validation

```text
.venv/bin/python -m pytest tests/fund/analysis/test_valuation_state.py tests/fund/analysis/test_checklist.py tests/services/test_fund_analysis_service.py tests/ui/test_cli.py tests/fund/audit/test_audit_programmatic.py tests/fund/template/test_renderer.py -q
```

Result:

```text
158 passed in 0.68s
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

## Notes

- Full test suite was not run in this worker pass; targeted P19-S3 validation and lint/diff checks passed.
- Existing untracked files present before implementation were left untouched: `docs/design0522.md`, `docs/implementation-control0522.md`, `docs/repo-audit-20260521.md`.
