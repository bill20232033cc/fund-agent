# P19-S3 Plan Re-review（MiMo）

- **reviewed target**: `docs/reviews/p19-s3-valuation-state-integration-plan-20260523.md`
- **scope**: re-review stance；只验证上一轮 accepted blockers 是否关闭，并检查新增阻塞风险；未修改生产代码或测试。
- **review timestamp**: `20260523-021051`
- **conclusion**: `fail`

## Scope And Sources

本次复审只针对 controller 在 `docs/reviews/p19-s3-plan-review-controller-judgment-20260523.md` 接受的 5 个 blocker：

1. `ValuationStateResolution` / equivalent provenance 必须成为 renderer/audit 结构化真源，R1 不得解析 `ChecklistItem.reason`。
2. benchmark identity 必须 exact match，并覆盖派生/策略/行业/等权/低波等负例。
3. CLI/Service 默认从 `unavailable` 改成 `None` 必须作为 public contract change，并提供 opt-out。
4. CLI/report disclaimer 必须可验收。
5. `ThermometerCalculationError` 或 equivalent auto-path failure 必须有灰灯测试，同时 programming contract errors fail-closed。

直接读取：

- `docs/reviews/p19-s3-valuation-state-integration-plan-20260523.md`
- `docs/reviews/p19-s3-plan-review-mimo-20260523.md`
- `docs/reviews/p19-s3-plan-review-glm-20260523.md`
- `docs/reviews/p19-s3-plan-review-controller-judgment-20260523.md`
- 当前 renderer 代码事实：`fund_agent/fund/template/renderer.py`
- 当前 CLI/audit/template 接口事实：`fund_agent/ui/cli.py`、`fund_agent/fund/audit/audit_programmatic.py`、`fund_agent/fund/template/renderer.py`

## Accepted Blocker Closure Check

| Accepted blocker | Status | Evidence |
|---|---|---|
| Structured `ValuationStateResolution` as ProgrammaticAudit/TemplateRenderInput truth; R1 not reason-text based | closed | Plan now states automatic mapping must use `ValuationStateResolution` as structured truth in `TemplateRenderInput` and `ProgrammaticAuditInput` (`lines 25`, `45`, `72-73`, `117-127`). R1 must use `ProgrammaticAuditInput.valuation_state_resolution`, not `ChecklistItem.reason` (`lines 329-348`). Service, audit/renderer slices and test matrix include propagation/tamper tests (`lines 401`, `431-434`, `493-497`, `530`, `533`). |
| Benchmark identity exact match and derived-index negative examples | closed | Plan now forbids substring alias matching and requires component-level exact identity (`lines 263-281`). It lists concrete negative examples including `沪深300价值指数收益率`, `沪深300等权重指数收益率`, `中证500质量成长指数收益率`, sector/low-vol variants, supported-index mix ambiguity, and bond/cash allowed component case (`lines 283-304`). Slice/test matrix require these examples (`lines 368-371`, `464-473`, `528`). |
| CLI/Service default `None` public contract change and opt-out | closed | Plan explicitly records the default change as intentional public contract change and defines opt-out paths: CLI `--valuation-state unavailable` and Service `FundAnalysisRequest(..., valuation_state="unavailable")` (`lines 82-107`). Slices/tests/exit criteria cover default None, explicit unavailable suppressing thermometer, help/README wording, and old manual gray restoration (`lines 398`, `415-419`, `447-448`, `488-491`, `524-526`). |
| CLI/report disclaimer acceptance | partially closed but new blocker below | Plan now requires user-visible disclaimer when self-owned thermometer was called (`lines 225-233`), renderer tests for disclaimer outside anchor note (`lines 350-354`, `498-499`), and exit criteria for CLI/report output (`line 532`). However, the proposed text conflicts with current forbidden-word validation and project no-trading-advice constraints. |
| `ThermometerCalculationError` / equivalent auto-path gray tests | closed | Plan now requires expected calculation/data-quality exceptions to become unavailable gray with precise reason (`lines 316`, `323`), Service tests for fake thermometer raising `ThermometerCalculationError` or equivalent (`lines 403-404`, `484-485`), and exit criteria preserving fail-closed behavior for impossible provider types (`line 534`). |

## Findings

### PR-MIMO-RR-001-未修复-高-计划要求的 disclaimer 文案会被当前报告禁用词校验拒绝

- **位置**: `Evidence anchors and disclaimer`、`Renderer coverage`、`Exit Criteria`
- **问题类型**: 契约冲突 / 不可直接实施 / 测试缺口
- **当前写法**: plan 要求当自动路径调用自建温度计并收到 available/stale/unavailable reading 时，报告主体或稳定证据区必须包含等价 user-visible statement，其中示例文案包含“仅供买入前检查参考”；renderer 测试还要断言 disclaimer text 出现在报告输出中，CLI/report exit criteria 也要求包含该 disclaimer。
- **反例/失败场景**: implementation agent 按计划把示例 disclaimer 渲染进报告或 CLI stdout。当前 `render_template_report()` 会在返回前调用 `_validate_report_wording(report_markdown)`；该校验把 `"买入"` 列为禁用投资建议措辞。报告一旦包含“买入前检查参考”，renderer 会抛 `ValueError("报告包含禁用投资建议措辞：买入")`，导致 P19-S3 renderer/Service/CLI happy path 无法通过。
- **为什么有问题**: 这不是单纯措辞问题。仓库约束禁止直接输出“买入”“卖出”建议，当前 renderer 也用禁用词做硬校验。plan 同时要求报告必须出现 disclaimer、又给出包含禁用词的 disclaimer 文案，但没有把 `_validate_report_wording` 的边界修改列入任何 slice，也没有指定使用不含禁用词的等价文案。实现 agent 会被迫临场选择：弱化报告安全校验，或偏离 plan 的可验收 disclaimer 文案。
- **直接证据**:
  - Plan `lines 225-231`: disclaimer 示例包含“仅供买入前检查参考”。
  - Plan `lines 350-354`: renderer test 要断言 disclaimer text 出现在 report output，而不是仅在 anchor note。
  - Plan `line 532`: exit criteria 要求 CLI/report output 包含 independent-methodology disclaimer。
  - `fund_agent/fund/template/renderer.py:53`: `_FORBIDDEN_TERMS = ("买入", "卖出", "仓位比例", "收益预测")`。
  - `fund_agent/fund/template/renderer.py:1575-1590`: `_validate_report_wording()` 对报告中任一禁用词抛 `ValueError`。
- **影响**: P19-S3 实现不可直接通过计划要求的 renderer/report 测试；若实现为通过测试而放宽禁用词校验，会扩大交易建议风险并违反基金分析专项原则。
- **建议改法和验证点**:
  - 将 disclaimer 示例改为不含禁用词的等价文案，例如把“仅供买入前检查参考”改为“仅供投资前检查参考”或“仅供持有判断前的风险检查参考”。
  - 在 Slice 5 / renderer tests 中明确断言 disclaimer 不触发 `_validate_report_wording()`，并保留禁用词测试，确保没有因 disclaimer 放宽全局禁用词。
  - 不建议为了这条 disclaimer 给 `"买入"` 做全局白名单；这会削弱已有报告安全边界。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 高

## Open Questions

- `ValuationStateResolution` 的类型是否需要由 `TemplateRenderInput` 引用 Capability analysis 模块里的具体 dataclass，还是以 Protocol / minimal structured object 降低 template/audit 对 analysis 实现的耦合？当前计划可实施，但实现时要避免 renderer 反向承载 valuation 解析逻辑。

## Residual Risks

- benchmark text exact matching 已按 fail-closed 收敛，但在 `benchmark_index_code` 长期为空的前提下仍有文本质量残余风险；plan 已把该风险记录到 residuals，可接受。
- 默认 `FundAnalysisRequest(fund_code=...)` 触发自动温度计 IO 是有意 public behavior change；plan 已要求 README/help/tests 写清楚，但实施 review 仍需重点核对。
- `cached/stale` 与 disclaimer 同时进入 reason、anchor note、resolution 时存在重复表达风险；plan 已指定 resolution 为真源，实施时应避免让 anchor note 成为第二真源。

## Final Plan Review Conclusion

`fail`

上一轮 5 个 accepted blockers 中，结构化审计真源、benchmark exact match/负例、默认 `None` public contract/opt-out、calculation-error 灰灯测试均已关闭；disclaimer 可验收性方向已补上，但引入了新的阻塞冲突：计划要求渲染的示例 disclaimer 含有当前 renderer 明确禁止的“买入”。在进入 implementation 前，应先把 disclaimer 文案改为不含禁用词的等价表述，并把“不触发 forbidden wording validation”列入 renderer 验收。
