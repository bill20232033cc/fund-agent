# Code Review — P7-S2 Rereview (Finding 1 Fix Verification)

## Scope

- Mode: targeted re-review of medium finding fix only
- Branch: main (unstaged workspace changes)
- Base: `docs/reviews/code-review-p7-s2-mimo-20260520.md` finding 1
- Output file: `docs/reviews/code-review-p7-s2-rereview-mimo-20260520.md`
- Included scope: `AnnualReportSourceOrchestrator.__init__` empty-tuple guard
- Excluded scope: all other P7-S2 findings and code

## Finding

### 1-已修复-中-`AnnualReportSourceOrchestrator(())` 空元组静默回退

- **文件(行号)**: `sources.py:315-317`
- **修复前**: `self.sources = sources or (EastmoneyAnnualReportSource(),)` — 空元组 `()` 为 falsy，静默回退到 Eastmoney
- **修复后**: `self.sources = (EastmoneyAnnualReportSource(),) if sources is None else sources` — 显式 `is None` 检查，空元组进入 `if not self.sources` 分支抛出 `ValueError`

验证结果：

| 场景 | 预期 | 实际 | 结果 |
|---|---|---|---|
| `AnnualReportSourceOrchestrator(())` | `ValueError("sources 不能为空")` | `ValueError: sources 不能为空` | PASS |
| `AnnualReportSourceOrchestrator(None)` | 默认 Eastmoney | `sources[0].name == "eastmoney"` | PASS |
| `AnnualReportSourceOrchestrator()` | 默认 Eastmoney | `sources[0].name == "eastmoney"` | PASS |

20/20 focused tests pass (`test_annual_report_sources.py` + `test_repository.py`).

**Pass.** Fix is correct. `is None` 语义精确区分了"未传参/显式 None"（使用默认值）和"显式空元组"（配置错误）。

## Conclusion

PASS. Finding 1 修复已验证。空元组正确抛出 ValueError，None 和缺省参数正确回退到 Eastmoney。20/20 测试通过。
