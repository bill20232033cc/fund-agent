# P19-S3 Plan Review（GLM）- 2026-05-23

Generated at: 20260523-020131

## Reviewed Target And Scope

- Target: `docs/reviews/p19-s3-valuation-state-integration-plan-20260523.md`
- Scope: 仅审查计划是否足够交给 implementation agent；未修改生产代码或测试。
- Focus: 显式输入优先、默认行为迁移、quality gate 前后顺序、证据锚点与 ProgrammaticAudit、active/bond/QDII/FOF unavailable 语义、仅支持 `000300`/`000905` 的映射规则、`ThermometerService` 注入和 failure semantics。

## Assumptions Tested

- 自动 thermometer-to-`valuation_state` 会改变 `fund-analysis analyze` 第 6 问、检查清单汇总信号和最终判断派生路径。
- P19-S3 只允许将 A 股指数基金/指数增强基金中可确定映射到 `000300` 或 `000905` 的场景自动映射；其余应为 `unavailable` 灰灯。
- 显式 `--valuation-state` 必须优先，且不得触发温度计 IO。
- 程序审计必须基于结构化同源数据验证自动估值证据，而不能靠报告文本或人类可读 reason 间接推断。
- `ThermometerService` 只能通过自建指数温度计路径参与 `analyze`，不能回落到有知有行公开页面快照。

## Evidence-Based Findings

### F1-未修复-高-ProgrammaticAudit 没有结构化 valuation resolution 输入，审计只能靠 reason/anchor 文本间接推断自动估值来源

- **位置**: plan `Type And Interface Changes`、`Checklist contract`、`Audit And Evidence Plan`；`docs/reviews/p19-s3-valuation-state-integration-plan-20260523.md:101-107`, `:166-191`, `:251-261`
- **问题类型**: 契约缺失 / 架构边界 / 测试缺口 / 不可直接实施
- **当前写法**: plan 只要求 `FundAnalysisResult` 增加 `valuation_state_resolution`，`run_checklist()` 消费 resolution 并把 anchors/reason 写入 `ChecklistItem`；审计阶段则在 `_audit_checklist_rules()` 中判断 “valuation item reason/source indicates self-owned thermometer” 和 anchor note/row locator 字段完整性。
- **反例/失败场景**: implementation agent 生成一个自动温度计 `high` 的 `ChecklistItem`，但错误地使用 `source_kind="derived"` 或漏掉 `lookback` 字段；如果 reason 文本没有稳定标识 “self-owned thermometer”，R1 可能只看到红灯 item 有 anchor 而放过。反过来，显式用户输入 `--valuation-state high` 也会产生非灰灯第 6 问和 derived anchor，审计若靠 reason 文本区分来源，容易把文案调整当作契约。
- **为什么有问题**: 设计真源要求“自动映射必须在审计输入中保留温度值、数据日期、来源、指数代码、回溯窗口和 unavailable 原因”（`docs/design.md:917`）。当前 `ProgrammaticAuditInput` 只有 `checklist_result`、`index_profile`、`tracking_error` 等字段，没有估值 resolution；`_audit_checklist_rules()` 只按 checklist item 数量、汇总信号和 signal/status 一致性检查，无法基于结构化来源判断自动估值证据是否完整。
- **直接证据**:
  - 当前 Service 把 `request.valuation_state` 直接传给 checklist：`fund_agent/services/fund_analysis_service.py:391-400`。
  - 当前 `ChecklistItem` 只有 `code/question/signal/status/anchors/reason`，没有 `source` 或 resolution 字段：`fund_agent/fund/analysis/checklist.py:42-58`。
  - 当前 `_check_valuation()` 生成第 6 问时 anchors 为空：`fund_agent/fund/analysis/checklist.py:416-444`。
  - 当前 `ProgrammaticAuditInput` 没有 valuation resolution：`fund_agent/fund/audit/audit_programmatic.py:93-123`。
  - 当前 `_audit_checklist_rules()` 不审计任何估值证据字段：`fund_agent/fund/audit/audit_programmatic.py:867-913`。
- **影响**: 自动估值证据缺失可能通过程序审计；显式输入与自动输入的来源边界会退化为文案约定；review 难以判断 implementation 是否真正满足“自动输入可追踪”。
- **建议改法和验证点**:
  - 在 plan 中明确 `ValuationStateResolution` 必须进入 `TemplateRenderInput` / `ProgrammaticAuditInput`，或给 `ChecklistItem` 增加稳定结构化 `valuation_source` / `valuation_metadata`，二者择一，避免审计解析 reason 文本。
  - R1 应以结构化 resolution 为真源校验：`source="self_owned_thermometer"` 且 `state != "unavailable"` 时必须存在 `external_api` anchor，并逐字段校验 `index_code`、`data_date`、`temperature`、`pe_percentile`、`pb_percentile`、`thermometer_source`、`lookback_start/end`、`cached/stale`。
  - 显式用户输入路径应有 `source="explicit_user_input"`，R1 不要求 thermometer 字段，但仍要求 derived user-input anchor。
  - 增加 tamper tests：自动 resolution 缺 `lookback`、anchor source_kind 错误、显式 high 无 thermometer 字段仍通过、自动 high 用 derived anchor 必须失败。
- **修复风险（低/中/高）**: 中
- **严重程度（低/中/高/严重）**: 高

### F2-未修复-高-000300/000905 alias 映射规则没有定义 token 边界和派生指数拒绝规则，可能把 unsupported 指数误映射为沪深300/中证500

- **位置**: plan `Mapping Rules` / `Benchmark decision rules` / test matrix；`docs/reviews/p19-s3-valuation-state-integration-plan-20260523.md:210-230`, `:358-373`
- **问题类型**: 契约缺失 / 非最优方案 / 测试缺口 / 默认行为迁移风险
- **当前写法**: plan 说 normalize whitespace/full-width punctuation 后匹配 alias；若 exactly one supported index alias 命中且基金类型为 `index_fund` / `enhanced_index`，就映射到该指数。它只补充“supported index plus clearly unsupported equity index tokens” 返回 ambiguous，但没有定义什么是 token、什么是 clearly unsupported，也没有列出派生指数负例。
- **反例/失败场景**: 年报基准为 `沪深300价值指数收益率`、`沪深300成长指数收益率`、`沪深300等权重指数收益率`、`中证500质量成长指数收益率`、`中证500低波动指数收益率`。这些都包含 `沪深300` 或 `中证500` 子串，但不是 P19-S1/S2 已支持的 `000300` / `000905` 本体。按当前 plan 的 alias 子串匹配，implementation agent 很容易把它们自动映射到 `000300` / `000905`，从而把本应灰灯的第 6 问改成红/黄/绿。
- **为什么有问题**: P19-S3 的第一性目标是“只把可确定映射到 P19-S1/S2 已支持指数的 A 股指数基金 / 指数增强基金自动映射”，其余 unsupported/ambiguous 必须 `unavailable`。当前代码事实中 `IndexProfileValue.benchmark_index_code` 仍为 `None`，映射主要依赖 `benchmark_text` / `benchmark_index_name` / `benchmark_component_text`；`benchmark_index_code` 明确“禁止从基金代码猜测”。因此 alias 规则必须能防止字符串包含式误判，否则会直接改变 `analyze` 默认输出。
- **直接证据**:
  - plan 承认当前 `benchmark_index_code` 仍为 `None`：`docs/reviews/p19-s3-valuation-state-integration-plan-20260523.md:18`。
  - `IndexProfileValue.benchmark_index_code` 的契约是“可确定的指数代码；禁止从基金代码猜测”：`fund_agent/fund/extractors/models.py:93-97`。
  - 当前 profile extractor 固定写入 `benchmark_index_code=None`，只保留 benchmark 文本和组件：`fund_agent/fund/extractors/profile.py:669-675`。
  - plan 的支持范围只有 `000300` 和 `000905`：`docs/reviews/p19-s3-valuation-state-integration-plan-20260523.md:210-217`。
- **影响**: 默认未传 `--valuation-state` 的 `fund-analysis analyze` 可能对 unsupported 派生指数输出红/黄/绿强判，影响最终判断派生；这类误判不会被当前 test matrix 覆盖。
- **建议改法和验证点**:
  - 在 plan 中把 alias 匹配定义为“指数身份精确匹配”，而不是任意 substring。示例：允许 `沪深300` / `沪深300指数` / `沪深300指数收益率`，但拒绝 `沪深300价值`、`沪深300成长`、`沪深300等权`、`沪深300低波动`、`中证500质量成长` 等派生/策略/行业/风格指数。
  - 明确 composite 规则：现金、活期存款、债券现金类组件可忽略；任何未支持的权益指数组件或 supported alias 嵌入更长权益指数名称时，返回 `unsupported_index` 或 `ambiguous_benchmark`，不得映射。
  - 在 test matrix 中加入上述负例，并断言 no thermometer call、`ValuationState.UNAVAILABLE`、灰灯、reason 说明 unsupported/ambiguous。
- **修复风险（低/中/高）**: 中
- **严重程度（低/中/高/严重）**: 高

### F3-未修复-中-`ThermometerCalculationError` failure semantics 写在表格里，但 implementation slices/test matrix 没有可验收路径

- **位置**: plan `Failure Semantics` / `Implementation Slices` / `Test Matrix`；`docs/reviews/p19-s3-valuation-state-integration-plan-20260523.md:243-245`, `:299-313`, `:358-387`
- **问题类型**: failure semantics / 测试缺口 / 不可直接实施
- **当前写法**: failure table 规定 `ThermometerCalculationError during auto path` 应转为 `unavailable` 并继续分析；但 Service slice 和 test matrix 只要求 “unavailable reading produces gray”，没有要求 fake thermometer 抛 calculation error 时 analyze 继续且灰灯。
- **反例/失败场景**: `ThermometerService.run(ThermometerRequest(index_code="000300"))` 在缓存损坏、历史数据不足或 calculator invariant 失败时抛出 calculation error。若 implementation agent 只处理 `ThermometerReading.unavailable=True`，该异常会穿透到 CLI，导致 `analyze` exit 1，而不是第 6 问灰灯。
- **为什么有问题**: 当前 `ThermometerService.run()` 的类型契约允许底层传播非数据态异常；自建指数路径只有 `ThermometerSourceError` 被转为 unavailable/stale-cache，calculator 异常不是稳定返回态。P19-S3 正在改变 `analyze` 默认行为，因此 auto path 的失败语义必须用测试固定，否则外部数据或缓存异常会让原本可生成报告的分析失败。
- **直接证据**:
  - plan failure table 写明 calculation error 应继续分析：`docs/reviews/p19-s3-valuation-state-integration-plan-20260523.md:243-245`。
  - `ThermometerService.run()` 返回 union，并声明允许适配器传播异常：`fund_agent/services/thermometer_service.py:147-160`。
  - 自建指数路径调用 `calculate_thermometer_reading()` 时没有在 Service 内捕获 calculator 异常：`fund_agent/services/thermometer_service.py:223-244`。
- **影响**: implementation agent 可能实现 happy path 和 unavailable-reading path，却遗漏抛异常路径；默认 auto 集成后，温度计计算异常会把 `fund-analysis analyze` 从灰灯降级变成失败退出。
- **建议改法和验证点**:
  - 在 Slice 3 明确增加 fake thermometer 抛 `ThermometerCalculationError` 或等价 calculation exception 的 Service 测试。
  - 明确只捕获温度计 auto path 的预期计算/数据不可用异常；programming contract error（例如返回 `ThermometerSnapshot` 或 `ThermometerBatchResult`）仍 fail closed。
  - reason/anchor 必须记录 precise unavailable reason，且不 fallback 到公开页面快照。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 中

## Open Questions

- `ValuationStateResolution` 的唯一真源应放在哪里：作为 `TemplateRenderInput` / `ProgrammaticAuditInput` 的独立字段，还是嵌入 `ChecklistItem` 的结构化 metadata？当前 plan 同时提 `FundAnalysisResult` 和 checklist anchors，但没有指定审计真源。
- 对 `enhanced_index` 的复合基准，是否只允许 “一个 supported equity index + 现金/存款/债券现金类组件” 自动映射？如果是，需要在 plan 中列出允许/拒绝组件类别。
- `ThermometerCalculationError` 的具体异常类型是否已经存在并可 import？如果没有，P19-S3 需要指定捕获的异常边界，避免 broad `Exception` 把编程错误也转成灰灯。

## Residual Risks

- 默认 `FundAnalysisRequest.valuation_state=None` 会改变所有未显式传参的 programmatic callers 行为；这是 P19-S3 目标的一部分，但需要 README 和 Service tests 明确记录。
- live akshare/schema 抖动仍是外部数据残余风险；P19-S3 应只用 fake/fixture 证明 analyze failure semantics，不应依赖 live tests。
- Stale cache 证据可能被用户误读为新鲜数据；resolution 和 anchor note 必须保留 `cached` / `stale`，并在报告附录可见。

## Conclusion

fail

当前 plan 方向正确，但还不能安全交给 implementation agent。阻断点不是实现难度，而是两个会直接改变 `fund-analysis analyze` 输出的契约没有收敛：自动估值审计缺少结构化同源输入，以及 `000300`/`000905` alias 映射没有防止 unsupported 派生指数误映射。修复上述 finding 并补齐 calculation-error 测试后，可重新评审。
