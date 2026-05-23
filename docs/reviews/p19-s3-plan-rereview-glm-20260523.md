# P19-S3 Plan Re-review（GLM）- 2026-05-23

Generated at: `20260523-021012`

## Reviewed Target And Scope

- Target: `docs/reviews/p19-s3-valuation-state-integration-plan-20260523.md`
- Comparison inputs:
  - `docs/reviews/p19-s3-plan-review-glm-20260523.md`
  - `docs/reviews/p19-s3-plan-review-mimo-20260523.md`
- Scope: 仅复审 patched plan 是否真正关闭上一轮 accepted findings；不修改生产代码或测试。
- Focus: ProgrammaticAudit 结构化 provenance、派生指数拒绝规则、default auto opt-out、disclaimer 输出、calculation exception 灰灯测试。

## Conclusion

`pass-with-risks`

patched plan 已经把上一轮 GLM/MiMo 的 material findings 收敛到可实施契约，足以交给 implementation agent。原阻断点已被关闭：

- ProgrammaticAudit 不再依赖 `ChecklistItem.reason` 文案推断来源，而是要求 `ValuationStateResolution` 进入 `FundAnalysisResult`、`TemplateRenderInput` 和 `ProgrammaticAuditInput`，并由 R1 以结构化 resolution 为真源校验。
- benchmark 映射从 alias substring 改为组件级 exact identity match，并显式列出派生/策略/风格/行业/等权/低波负例。
- 默认从手动灰灯迁移到 auto 已被声明为 intentional public contract change，且明确 `--valuation-state unavailable` / `FundAnalysisRequest(valuation_state="unavailable")` 是旧行为 opt-out。
- disclaimer 不再只是 anchor note 装饰，patched plan 要求 self-owned thermometer 被调用时 CLI/report 输出用户可见免责说明。
- `ThermometerCalculationError` 或等价自建温度计计算/数据质量异常已有 Service 测试要求：auto path 应灰灯继续，并保留 precise reason。

没有发现仍需阻断实现的 remaining finding。当前风险主要是实现期执行风险，而不是 plan 规格缺失。

## Accepted Findings Closure Review

### GLM-F1 / MIMO-001: ProgrammaticAudit 结构化 provenance

Status: `closed`

patched plan 在 `Structured provenance truth` 中明确选择 `ValuationStateResolution` 为唯一结构化真源，并要求传播到 `FundAnalysisResult`、`TemplateRenderInput`、`ProgrammaticAuditInput`。同时写明 `ChecklistItem.anchors` 只是 resolution anchors 的投影；如果 checklist reason、anchors 与 resolution 不一致，audit 以 `ProgrammaticAuditInput.valuation_state_resolution` 为准并由 R1 报错。

`Audit And Evidence Plan` 进一步要求 R1 不得从 `ChecklistItem.reason` 推断来源，并直接检查 `source == "self_owned_thermometer"` 时的 `index_code`、`index_name`、`temperature`、`pe_percentile`、`pb_percentile`、`data_date`、`lookback_start/end`、`thermometer_source`、`cached`、`stale`、`disclaimer`、`external_api` anchor。测试矩阵也包含 auto valuation without resolution、without external_api anchor、missing structured fields、derived-only anchor 等 tamper tests。

这关闭了“审计只能靠 reason/anchor 文本间接推断”的阻断问题。

### GLM-F2 / MIMO-002: 派生指数拒绝规则

Status: `closed`

patched plan 已把 benchmark decision rules 收紧为组件级 exact index identity match，明确禁止 substring alias matching。允许 identity forms 仅限 `沪深300` / `沪深300指数` / `CSI300` / `CSI 300` 和 `中证500` / `中证500指数` / `CSI500` / `CSI 500`。

计划还明确：supported alias 嵌入更长权益指数名称时返回 `unsupported_index` 或 `ambiguous_benchmark`；任一 unsupported equity index 与 supported component 并存时返回 `ambiguous_benchmark`，不得按权重选择 supported component。负例表覆盖 `沪深300价值`、`沪深300成长`、`沪深300红利低波动`、`沪深300等权重`、`中证500质量成长`、`中证500低波动`、`中证500医药卫生`、双 supported index 复合等场景，并要求 implementation tests 包含这些例子或等价 fixtures。

这关闭了“把派生/策略/行业指数误映射为 000300/000905”的阻断问题。

### MIMO-003: default auto opt-out

Status: `closed`

patched plan 在 request/result contract 中明确：`valuation_state=None` 表示用户未显式提供，允许 auto；`low/fair/high/unavailable` 均为显式输入，不调用 thermometer。计划直接标注这是 intentional public contract change，并写出 opt-out / legacy gray path：

- CLI: `fund-analysis analyze <fund_code> --valuation-state unavailable`
- Service: `FundAnalysisRequest(..., valuation_state="unavailable")`

CLI slice、test matrix 和 exit criteria 都要求 help/README 说明默认 auto 与 explicit unavailable opt-out，并验证 explicit unavailable suppresses auto。

这关闭了“默认行为迁移没有兼容验收和显式 opt-out 表述”的问题。

### MIMO-004: disclaimer 输出

Status: `closed`

patched plan 明确 disclaimer “is not optional anchor decoration”。当 automatic path 调用 self-owned thermometer 并收到 available、stale-cache 或 unavailable thermometer reading 时，报告正文或稳定证据区必须包含等价用户可见说明：

```text
本温度计基于有知有行公开方法论独立计算，非有知有行官方数据。
计算方法：等权 PE/PB 中位数历史分位数综合。
与有知有行官方温度计可能存在合理偏差，仅供买入前检查参考。
```

renderer coverage、test matrix 和 exit criteria 均要求当 `ValuationStateResolution.disclaimer_required=True` 或 thermometer was called 时，report/CLI 输出包含 disclaimer，不能只藏在 anchor note 中。unsupported fund type / missing benchmark / ambiguous benchmark 这类未调用 thermometer 的路径不要求 disclaimer，但必须说明灰灯原因。

这关闭了“CLI/report 免责标注没有成为可验收契约”的问题。

### GLM-F3: calculation exception 灰灯测试

Status: `closed`

patched plan 的 failure semantics 要求 `ThermometerCalculationError` 或等价 self-owned thermometer calculation/data-quality exception 在 auto path 中转为 `unavailable`，分析继续，检查清单第 6 题灰灯，并保留 precise reason。Slice 3 和 test matrix 明确要求 fake thermometer 抛该异常时 analyze continues，gray unavailable，precise reason retained。

同时计划限制只能捕获预期的自建温度计数据/计算异常，不能 broad `Exception`；provider 返回 `ThermometerSnapshot`、`ThermometerBatchResult`、`None` 或 invalid candidate 时必须 `ValueError` fail closed。这关闭了“异常路径只写在表格、没有可验收测试”的问题。

## Remaining Findings

No remaining findings.

本轮没有发现仍足以阻断 implementation 的计划缺口。上一轮 accepted findings 均已在 patched plan 中转化为明确契约、slice 工作项、测试矩阵和 exit criteria。

## Residual Risks

- `benchmark_index_code` 当前仍未填充，P19-S3 仍依赖 benchmark 文本质量。patched plan 用 exact identity、负例测试和 fail-closed unavailable 缓解，但这不是完整 index identity extractor。
- `ValuationStateResolution`、`ChecklistItem.anchors/reason`、renderer 输出三者存在投影一致性风险。实现时必须保持 resolution 是单一真源，R1 负责发现 projection drift。
- default `FundAnalysisRequest(fund_code=...)` 现在会在 quality gate 通过后允许 thermometer IO。这是计划接受的 public behavior change，但实现和文档必须避免让调用方误以为省略参数仍是旧的手动灰灯。
- stale cache 读数可能被用户误读为新鲜数据。实现必须把 `cached` / `stale` 传入 resolution、anchor note、报告证据和 reason 文本。
- enhanced-index 自动映射仍是保守策略：仅 exact supported broad index 加现金/债券组件可自动映射。策略化 target index 或派生指数保持 unavailable，后续若扩大覆盖，需要新的 plan/review gate。

## Final Plan Review Conclusion

`pass-with-risks`

建议进入 P19-S3 implementation。implementation review 应重点盯住：R1 是否真的使用 `ProgrammaticAuditInput.valuation_state_resolution`，mapping 是否没有退化为 substring match，explicit unavailable 是否 suppress thermometer，disclaimer 是否出现在用户可见输出，calculation exception 是否灰灯而 programming contract error 是否 fail closed。
