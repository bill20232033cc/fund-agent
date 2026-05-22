# P19-S3 Valuation State Integration Plan Review（MiMo）

- **reviewed target**: `docs/reviews/p19-s3-valuation-state-integration-plan-20260523.md`
- **scope**: 独立 adversarial plan review；只审计划，不修改生产代码或测试。
- **review timestamp**: `20260523-020212`
- **conclusion**: `fail`

## Scope And Sources

本次评审重点检查 P19-S3 是否已经足够 code-generation-ready，能否安全改变 `fund-analysis analyze` 第 6 题检查清单和最终判断派生路径。

直接读取并对照：

- `docs/design.md` §11.7/§11.8：P19-S3 才允许自动集成；必须保留显式输入优先级、unavailable 灰灯语义、审计输入中的温度/日期/来源/指数/窗口/unavailable reason；CLI 和报告必须包含非官方独立计算免责标注。
- `docs/implementation-control.md` P19-S3：自动调用温度计、指数基金优先跟踪指数、温度不可用返回 `ValuationState.UNAVAILABLE`、用户显式输入优先、3 只样本端到端；硬约束包括不依赖公开页、不改分层、不修改 R=A+B-C/基金类型/年报抽取/现有审计规则、CLI 和报告输出免责标注。
- 相关代码事实：`fund_analysis_service.py` 当前默认 `valuation_state="unavailable"` 并直接传给 `run_checklist()`；`cli.py` 当前 `--valuation-state` 默认 `"unavailable"`；`checklist.py` 的 `ChecklistItem` 只有 `code/signal/status/anchors/reason`，第 6 题当前无锚点；`audit_programmatic.py` 的 `ProgrammaticAuditInput` 没有 valuation resolution/provenance 字段，R1 当前只校验数量、汇总信号和 status；`profile.py` 当前 `benchmark_index_code=None`，主要依赖 benchmark text/components；`ThermometerService` 支持 `000300`/`000905` 自建指数读数。

## Assumptions Tested

- 自动估值默认接入不会把过去缺省灰灯报告变成不可解释的红/黄/绿最终判断。
- CLI 缺省 `None`、显式 `unavailable`、Service 程序化调用默认值三者语义能被清楚区分。
- benchmark alias 匹配足以防止把非目标指数或复合基准误判成 `000300`/`000905`。
- 审计能基于结构化事实验证自动估值证据，而不是依赖展示文案。
- slice 已经具体到实现 Agent 不需要重新设计状态、schema 或审计协议。
- UI / Service / Capability 边界不被温度计 IO、benchmark 规则或审计细节穿透。

## Findings

### PR-MIMO-001-未修复-高-审计无法可靠区分自动温度计证据与显式/派生文案

- **位置**: Plan `Audit And Evidence Plan`、`Checklist contract`、`Evidence anchors`、`Exit Criteria`
- **问题类型**: 契约缺失 / 测试缺口 / 不可直接实施
- **当前写法**: plan 要求 `ValuationStateResolution` 进入 `FundAnalysisResult`，`run_checklist()` 使用 `resolution.anchors/reason`；R1 审计根据 valuation item 的信号、锚点、以及 reason/source 是否“indicates self-owned thermometer”检查证据完整性。
- **反例/失败场景**: 实现 Agent 可以生成一个第 6 题 `green/yellow/red`，附带 `derived` 锚点或只在 reason 中写“温度计显示”，但不携带 `external_api` 锚点的温度、日期、指数、窗口。因为现有 `ChecklistItem` 只有 `anchors` 和自由文本 `reason`，`ProgrammaticAuditInput` 也没有 `valuation_state_resolution` 或 `valuation_source` 字段，R1 很容易只能做字符串启发式判断。只要文案不包含 plan 预期关键词，自动估值缺证可能绕过审计；反过来，文案调整也可能误触发审计失败。
- **为什么有问题**: `docs/design.md` §11.7 明确要求自动映射必须在审计输入中保留温度值、数据日期、来源、指数代码、回溯窗口和 unavailable 原因。当前代码事实中 `ProgrammaticAuditInput` 只有 `checklist_result/index_profile/tracking_error` 等字段，R1 当前只审 7 项数量、overall signal 和 signal/status 对应关系。plan 的 exit criterion “automatic non-unavailable valuation lacks thermometer evidence fails” 需要结构化 provenance，否则不是可验证契约。
- **直接证据**:
  - plan lines 157-164 定义 `ValuationStateResolution` 字段，但 lines 251-261 只说在 `_audit_checklist_rules()` 内检查 checklist item。
  - plan lines 176-190 把 source-specific 信息放入 `_check_valuation()` reason 和 anchors。
  - `fund_agent/fund/analysis/checklist.py` lines 49-67：`ChecklistItem` 没有 source/provenance 字段。
  - `fund_agent/fund/audit/audit_programmatic.py` lines 94-123：`ProgrammaticAuditInput` 没有 valuation resolution 字段。
  - `fund_agent/fund/audit/audit_programmatic.py` lines 867-913：R1 当前不检查 valuation provenance。
- **影响**: 自动估值可能改变最终判断，但缺少可机器验证的证据来源；review 不可验收，后续实现容易通过 happy-path renderer 测试却让审计空转。
- **建议改法和验证点**:
  - 明确把 `ValuationStateResolution` 或最小 `ValuationEvidenceProvenance` 放入 `ProgrammaticAuditInput`，或在 `ChecklistItem` 增加结构化 `source/provenance` 字段；不要让 R1 从 `reason` 文本推断来源。
  - R1 应直接校验：`source == self_owned_thermometer` 且 `state in low/fair/high` 时必须存在 `external_api` anchor，并且结构化字段/anchor note 包含 index code、data date、temperature、PE/PB percentile、source、lookback、cached/stale、disclaimer。
  - 增加负测：自动 `low` 但 source/provenance 缺失、自动 `low` 但 external anchor 缺温度、自动 `low` 但只有 derived anchor，均应 R1 fail；显式 `--valuation-state high` 不应要求 external_api。
- **修复风险（低/中/高）**: 中
- **严重程度（低/中/高/严重）**: 高

### PR-MIMO-002-未修复-高-benchmark alias 匹配规则不足以防止变种指数误判

- **位置**: Plan `Mapping Rules` / `Benchmark decision rules` / Slice 1
- **问题类型**: 不可直接实施 / 最佳实践偏离 / 测试缺口
- **当前写法**: plan 支持 `沪深300`、`中证500` 及 `CSI 300/CSI 500` 等 alias；规则要求 normalize whitespace/full-width punctuation 后匹配 alias，若 exactly one supported index alias found 就映射；若包含 supported index plus clearly unsupported equity index tokens 则 ambiguous。
- **反例/失败场景**: `中证500质量成长指数收益率*95%+银行活期存款利率*5%`、`沪深300红利低波动指数`、`沪深300价值指数`、`中证500等权重指数` 都包含 supported alias，但它们不是 `000905`/`000300` 宽基本体。按“包含 alias 且只有一个 supported index alias”的实现，很容易错误映射到已支持宽基，进而把第 6 题变成红/黄/绿并影响最终判断。
- **为什么有问题**: 当前 `IndexProfileValue.benchmark_index_code` 代码事实仍为 `None`，P19-S3 主要依赖 benchmark text。设计真源要求指数基金优先使用其跟踪指数温度，但这要求“跟踪指数”身份可确定；把名称前缀相同的策略/风格/行业/等权变种当作宽基，会制造同源错误证据。plan 的 “clearly unsupported equity index tokens” 没有给出 token 表、边界匹配规则、中文/英文正则边界或否定测试，不足以交给实现 Agent。
- **直接证据**:
  - plan lines 214-230 只列 alias 示例和高层 decision rules。
  - plan lines 280-283 的 Slice 1 只要求 “supported, unsupported, missing and ambiguous mappings”，没有列变种指数负例。
  - `fund_agent/fund/extractors/profile.py` lines 670-675：当前 `benchmark_index_code=None`。
  - `fund_agent/fund/extractors/profile.py` lines 726-733：当前复合基准拆分只按 `＋+×*|和|及` 等简单分隔符。
- **影响**: 默认 `analyze` 会在用户没有显式估值输入时自动调用温度计；一旦 alias 误判，报告会生成看似可审计但实质错配的估值判断，最终判断可能从 `needs_attention` 变成 `worth_holding` 或 `suggest_replace`。
- **建议改法和验证点**:
  - 在 plan 中把匹配规则改成“规范化组件级 exact identity match”，只允许完整组件等于宽基本体或明确等价别名；名称后缀含“质量、成长、价值、红利、低波、低波动、等权、行业、消费、医药、增强策略”等修饰时必须 ambiguous/unsupported。
  - 明确中文和英文 alias 的边界规则，例如 `CSI 300` 后不得紧跟 style/sector token。
  - Test matrix 必须增加负例：`中证500质量成长指数`、`沪深300价值指数`、`沪深300红利低波动指数`、`中证500等权重指数`、`沪深300 + 中证500`、`沪深300指数收益率*80%+中证全债指数收益率*20%`。
- **修复风险（低/中/高）**: 中
- **严重程度（低/中/高/严重）**: 高

### PR-MIMO-003-未修复-中-CLI/Service 默认语义迁移缺少兼容验收和显式 opt-out 表述

- **位置**: Plan `Service request/result`、`CLI Analyze Contract`、`Test Matrix`
- **问题类型**: public contract 变更 / open question 未收敛 / 测试缺口
- **当前写法**: plan 把 `FundAnalysisRequest.valuation_state` 默认从 `"unavailable"` 改为 `None`，CLI `--valuation-state` 默认也从 `"unavailable"` 改为 `None`；`None` 表示用户未显式提供，允许自动解析；显式 `--valuation-state unavailable` 表示手动灰灯并 suppress thermometer。
- **反例/失败场景**: 现有程序化调用方只构造 `FundAnalysisRequest(fund_code=...)`，过去得到第 6 题灰灯且不触发外部温度计 IO；P19-S3 后同样代码会触发 benchmark 映射、温度计缓存/网络路径，并可能输出红/黄/绿。CLI 用户过去省略 `--valuation-state` 等价于 gray/unavailable；现在省略变成 auto。这个变化是 P19-S3 的产品目标之一，但 plan 没有明确 legacy 行为如何通过显式参数恢复、README/help 文案如何避免误解、Service 层程序化默认语义是否也被视为 public contract change。
- **为什么有问题**: 自动估值会改变检查清单和最终判断，plan lines 5-7 已承认这不是 UI 便利功能。当前代码事实中 Service 和 CLI 默认都是 `"unavailable"`；若迁移验收只检查 “no `--valuation-state` => request valuation_state None”，无法证明用户有清晰路径保持旧灰灯语义，也无法证明外部 IO 只在用户接受默认 auto 时发生。
- **直接证据**:
  - plan lines 82-99 和 lines 323-327 定义默认 `None`。
  - plan lines 373-382 的测试只覆盖 explicit high/unavailable、absent valuation auto、CLI request field，没有覆盖旧缺省灰灯语义的恢复路径或 help 文案。
  - `fund_agent/services/fund_analysis_service.py` line 138 当前默认 `valuation_state="unavailable"`。
  - `fund_agent/ui/cli.py` lines 93-96 当前 CLI 默认 `"unavailable"`，lines 197-203 总是传 `_valuation_state(valuation_state)`。
- **影响**: 用户可见默认行为改变但迁移口径不完整；实现后出现“同一命令报告突然变红/变绿/访问外部数据”的行为时，难以判断是预期还是回归。
- **建议改法和验证点**:
  - 在 plan 中显式记录这是 intentional public contract change，并定义兼容路径：CLI 使用 `--valuation-state unavailable` 恢复旧灰灯；Service 调用方传 `valuation_state="unavailable"` suppress auto。
  - 更新 CLI help 验收：`--valuation-state` 文案必须说明“不传则自动温度计；传 unavailable 则手动灰灯且不调用温度计”。
  - 增加测试：CLI no flag 触发 auto-capable request；CLI `--valuation-state unavailable` suppress provider；Service default `None` 会 auto only after quality gate；Service explicit unavailable 不调用 provider；README 用户成功路径写清楚默认 auto 和 opt-out。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 中

### PR-MIMO-004-未修复-中-免责标注没有成为 CLI/report 输出的可验收契约

- **位置**: Plan `Evidence anchors`、`Audit And Evidence Plan`、`Exit Criteria`
- **问题类型**: 约束遗漏 / 测试缺口
- **当前写法**: plan 要求 thermometer available anchor 的 `note` contains disclaimer；renderer 测试只要求 thermometer/unavailable anchors appear in `## 证据与出处`；exit criteria 只要求 evidence appendix includes valuation source details。
- **反例/失败场景**: 实现 Agent 可能只把 disclaimer 放入 `EvidenceAnchor.note`，且只在 available thermometer path 出现；第 7 章主体和 CLI report 输出中没有清晰的非官方独立计算说明，或者 unavailable/unsupported 自动路径完全没有免责说明。测试只看非年报 anchor 是否出现在附录，不会验证设计真源要求的完整等价文案。
- **为什么有问题**: `docs/design.md` §11.8 和 `docs/implementation-control.md` Hard Constraints 都要求 CLI 和报告输出必须包含非官方独立计算免责标注。P19-S3 默认接入 `analyze` 后，报告主体和 CLI stdout 就是用户看到的分析结果，不能只把免责声明作为可选锚点 note 的副产品。
- **直接证据**:
  - plan lines 185-193 只在 anchor note 里提 disclaimer。
  - plan lines 263-266 只要求 appendix 出现非年报 anchor。
  - plan lines 408-419 的 exit criteria 没有 “CLI/report contains disclaimer”。
  - `docs/design.md` lines 919-925 和 `docs/implementation-control.md` lines 212-223 明确要求 CLI 和报告输出免责标注。
- **影响**: 合规/用户理解边界可能缺失，尤其自动红/绿灯影响最终判断时，用户可能误以为这是有知有行官方温度或交易信号。
- **建议改法和验证点**:
  - 在 exit criteria 增加：当自动路径调用自建温度计并产生 available/stale/unavailable thermometer reading 时，报告和 CLI stdout 必须包含等价免责说明。
  - renderer 测试不要只检查 appendix anchor；应断言报告正文或证据附录稳定包含 `本温度计基于有知有行公开方法论独立计算，非有知有行官方数据` 及 PE/PB 分位方法边界。
  - 明确无需调用温度计的 unsupported fund type mapping 是否需要免责声明；若不需要，plan 应写清楚触发条件。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 中

## Open Questions

- P19-S3 是否要把 `ValuationStateResolution` 作为 Fund Capability 的稳定公共契约，还是只作为 Service 内部解析结果并投影到 checklist/audit？当前 plan 同时让 `FundAnalysisResult` 暴露它、让 checklist 消费它、又让 audit 从 checklist 推断它，所有权还不够单一。
- 对 enhanced index，是否只要 benchmark exact match 到宽基就自动使用温度计？增强指数可能存在策略化 target index 或复合现金/债券成分；plan 需要明确与普通 index_fund 使用完全同一规则还是更保守。
- `force_refresh=True` 当前同时用于年报/底层数据刷新。P19-S3 将其转发给 thermometer request 后，是否接受一次 `analyze --force-refresh` 同时刷新年报和温度计外部数据？如果接受，需要在 CLI/help/README 中说明。
- Programmatic audit 增强 R1 是否违反 implementation-control “不修改现有审计规则”？plan 说复用 R1 而非新增规则码是合理方向，但应明确这是扩展 R1 的证据完整性检查，不改变已有 R1 语义。

## Residual Risks

- 即使 alias 规则收紧，当前没有可用 `benchmark_index_code`，P19-S3 仍依赖年报 benchmark text 质量；建议把误判风险作为后续 `index_profile` identity extractor 残余项追踪。
- 真实 akshare 可用性仍是外部数据风险；P19-S3 不应新增 live smoke 作为阻塞验收，只应通过 fake/provider fixture 证明 failure semantics。
- 自动 `low/fair/high` 会直接影响 `derive_final_judgment()`；即使本次 plan 修复，上线后仍需要在 3 只样本端到端中人工核对报告第 7 章最终判断是否符合“估值只是买入前检查输入，不是交易建议”。
- `ValuationStateResolution` 字段较多，存在与 `EvidenceAnchor.note` 重复表达的耦合风险；实现时应选择一个结构化真源，再由 renderer/audit投影，避免三份状态不一致。

## Final Plan Review Conclusion

`fail`

该 plan 的方向总体正确：范围收窄、显式输入优先、unsupported 走 gray、Service/Capability 边界基本成立。但它还不应直接交给 implementation agent。自动估值会改变 `analyze` 默认输出和最终判断，当前 plan 对审计 provenance、benchmark alias 误判防护、默认语义迁移和免责输出的可验证契约仍不够具体。建议先 patch plan，补齐结构化审计输入、严格 benchmark identity 匹配负例、默认 auto 的 opt-out/help/README 验收，以及 CLI/report disclaimer 测试后再进入实现。
