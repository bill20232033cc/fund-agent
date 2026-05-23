# P13-S1 Plan Review — MiMo（2026-05-22）

## Reviewed Target

`docs/reviews/p13-s1-tracking-error-index-data-plan-20260522.md`

## Scope

P13-S1 tracking-error / index-data source contract plan-review gate. Adversarial assessment of whether this plan is code-generation-ready and safe for future implementation.

## Review Inputs

| Source | Role |
|---|---|
| `docs/design.md` | Design truth: architecture, boundaries, data sources, audit rules |
| `docs/implementation-control.md` | Control truth: phase state, gate constraints, residuals |
| `docs/reviews/next-phase-selection-controller-judgment-20260522.md` | 5 required P13-S1 constraints |
| `AGENTS.md` | Agent execution rules, module boundaries, hard constraints |
| `fund_agent/fund/data_extractor.py` | Current `StructuredFundDataBundle` shape |
| `fund_agent/fund/extractors/models.py` | `ExtractedField`, `ExtractionMode`, `EvidenceSourceKind` |
| `fund_agent/fund/template/renderer.py` | Current renderer hardcoded `数据不足` |
| `fund_agent/fund/analysis/risk_check.py` | Current `tracking_error` parameter path |
| `fund_agent/services/fund_analysis_service.py` | Service override path: `resolved_contract.tracking_error` |
| `fund_agent/ui/cli.py` | `--tracking-error` developer override |

## Assumptions Tested

1. `ExtractedField[TrackingErrorValue]` can carry `developer_override` source type without model changes.
2. Renderer can consume new `index_profile` / `tracking_error` fields through existing `structured_data` without explicit contract.
3. `run_risk_checks` migration from Service scalar to Capability helper is straightforward.
4. Composite benchmark can safely return `missing` without implementation confusion.
5. Fixture strategy covers all critical extraction paths.
6. Controller constraints are fully answered.

---

## Findings

### 01-未修复-中-ExtractedField extraction_mode 与 TrackingErrorValue source_type 存在语义缺口

- **位置**: Section 7.3 `TrackingErrorValue`, Section 7.4 Extraction Modes And Anchors
- **问题类型**: 契约缺失
- **当前写法**: `TrackingErrorValue.source_type` 包含 `developer_override`；Section 7.4 说 `developer_override` 值使用 no annual-report anchor 并携带 `provenance_note="developer_override"`。但 `ExtractedField.extraction_mode` 的 Literal 类型（`models.py:9`）只有 `direct / derived / estimated / missing`，没有 `developer_override`。
- **反例/失败场景**: Implementation agent 不知道 `developer_override` 路径的 `ExtractedField` 应使用哪个 `extraction_mode`。如果用 `missing`，语义矛盾——值存在但 mode 说缺失。如果用 `derived`，来源不对——不是从时间序列计算的。如果自行添加新 mode，需要改 `models.py` 的公共契约，但 plan 没有在 Slice A 或 D 中提及此改动。
- **为什么有问题**: `ExtractedField` 是 Capability 层公共契约（`models.py`），所有 extractor 和 consumer 依赖它的 Literal 类型。Plan 没有明确这个契约变更属于哪个 slice，implementation agent 必须自行决定，容易导致不一致。
- **直接证据**: `fund_agent/fund/extractors/models.py:9` 定义 `ExtractionMode = Literal["direct", "derived", "estimated", "missing"]`；Plan Section 7.3 定义 `source_type: Literal["direct_disclosure", "calculated_from_series", "developer_override"]`；Plan Section 7.4 未提及 `models.py` 需要变更。
- **影响**: 实施 Agent 跑偏 / 生成不一致的 mode 语义 / 后续 consumer（audit、quality gate）对 mode 的判断出错
- **建议改法和验证点**: 在 Slice A 中显式声明是否扩展 `ExtractionMode` 为 `Literal["direct", "derived", "estimated", "missing", "developer_override"]`，或规定 `developer_override` 使用 `extraction_mode="missing"` 并通过 `source_type` 区分。选择后者时需在 `TrackingErrorValue` 文档中明确 `extraction_mode` 与 `source_type` 的关系。验证：`models.py` 变更后 `ruff check` 和现有 extractor 测试通过。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 中

### 02-未修复-中-Renderer 消费新字段的 TemplateRenderInput 管道未显式定义

- **位置**: Section 9 Renderer Consumption Rules, Section 11 Slice E
- **问题类型**: 契约缺失
- **当前写法**: Section 9 描述 renderer 如何替换 `数据不足`，但未说明 `TemplateRenderInput` 如何获得 `index_profile` 和 `tracking_error`。当前 `TemplateRenderInput`（`renderer.py:60-85`）只有 `structured_data: StructuredFundDataBundle`，renderer 通过 `input_data.structured_data.benchmark` 访问数据。
- **反例/失败场景**: Plan 假设 renderer 可以通过 `input_data.index_profile` 或 `input_data.tracking_error` 访问新字段，但 `TemplateRenderInput` 当前没有这些字段。Implementation agent 需要决定：(a) 通过 `structured_data.index_profile` 访问（需确认 `StructuredFundDataBundle` 已扩展），或 (b) 在 `TemplateRenderInput` 上新增字段。两种路径影响不同 slice 的依赖顺序。
- **为什么有问题**: Plan Section 11 Slice E 说 "Files likely changed: renderer.py, test_renderer.py"，但没有提及 `TemplateRenderInput` 是否需要新增字段或是否只通过 `structured_data` 访问。Implementation agent 需要自行决定渲染输入管道。
- **直接证据**: `fund_agent/fund/template/renderer.py:60-85` 定义 `TemplateRenderInput`；Plan Section 9 描述消费规则但未描述输入管道。
- **影响**: 实施 Agent 需要架构猜测 / 可能导致 renderer 和 data_extractor 的依赖顺序错误
- **建议改法和验证点**: 在 Slice E 中显式声明 renderer 通过 `input_data.structured_data.index_profile` 和 `input_data.structured_data.tracking_error` 访问新字段（与现有 `benchmark` 模式一致），不需要在 `TemplateRenderInput` 上新增字段。验证：renderer 测试通过且 `TemplateRenderInput` 形状不变。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 中

### 03-未修复-中-ResolvedTrackingErrorForRisk helper 返回类型和迁移路径未定义

- **位置**: Section 10.1 Risk Check
- **问题类型**: 不可直接实施
- **当前写法**: Plan 定义了 `resolve_tracking_error_for_risk(...)` 的函数签名和大致返回内容（value, authority/source type, anchors/provenance, conflict/missing reason），但没有定义 `ResolvedTrackingErrorForRisk` 的具体字段类型。同时，当前 `run_risk_checks` 接收 `tracking_error: Decimal | str | int | float | None`，plan 说 "should not remain dependent on an unproven Service-level tracking-error scalar"，但没有说明 `run_risk_checks` 的参数签名如何变更。
- **反例/失败场景**: Implementation agent 不知道 `run_risk_checks` 是 (a) 改为接收 `ResolvedTrackingErrorForRisk` 对象，还是 (b) 保持现有签名但由 helper 预先解析为 scalar。两种路径对现有测试的影响不同：路径 (a) 需要改所有调用方，路径 (b) 只改 Service 层。
- **为什么有问题**: `run_risk_checks` 是 Capability 层公共 API（`risk_check.py:173`），被 Service 层调用。Plan 提出了迁移目标但没有定义具体的参数签名变更，implementation agent 必须自行决定 API 变更粒度。
- **直接证据**: `fund_agent/fund/analysis/risk_check.py:173-183` 当前签名；Plan Section 10.1 定义 helper 但未定义 `run_risk_checks` 签名变更。
- **影响**: 实施 Agent 跑偏 / 可能导致 API 变更范围过大或过小 / 测试迁移方向不明
- **建议改法和验证点**: 在 Slice D 中显式定义：(a) `ResolvedTrackingErrorForRisk` dataclass 的字段（value: Decimal | None, source_type: str, anchors: tuple, conflict_note: str | None），(b) `run_risk_checks` 是否改签名（建议保持现有签名，由 helper 解析为 scalar 后传入），(c) Service 层调用点的具体变更。验证：`test_risk_check.py` 和 service 测试通过。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 中

### 04-未修复-低-Composite benchmark 计算禁止但 IndexProfileValue 已预留 component 字段

- **位置**: Section 8.3 Calculated Path Formula, Section 7.2 IndexProfileValue
- **问题类型**: 过度设计
- **当前写法**: Plan Section 8.3 说 "Composite benchmark calculation is not allowed until a weighted composite benchmark contract exists"，但 Section 7.2 的 `IndexProfileValue` 已包含 `benchmark_component_text: tuple[str, ...]` 和 `benchmark_identity_status="composite"` 选项。
- **反例/失败场景**: Implementation agent 看到 `composite` 状态和 component 字段已存在，可能尝试为 composite benchmark 实现 tracking error 计算，违反 plan 的明确禁令。
- **为什么有问题**: 预留字段暗示未来功能方向，但当前 slice 明确禁止该功能。这不是 blocker，但增加了 implementation agent 的认知负担。
- **直接证据**: Plan Section 7.2 定义 `benchmark_component_text` 和 `benchmark_identity_status="composite"`；Plan Section 8.3 禁止 composite 计算。
- **影响**: 低——Implementation agent 可能混淆方向，但 plan 的禁令足够明确
- **建议改法和验证点**: 在 Slice C 的 acceptance criteria 中补充：`benchmark_identity_status="composite"` 时，tracking_error 必须返回 `missing`，renderer 保持 `数据不足`，且不触发 composite 计算路径。验证：composite benchmark fixture 返回 missing。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

### 05-未修复-低-Ambiguity extraction 路径缺少 fixture 覆盖

- **位置**: Section 12 Fixture Strategy
- **问题类型**: 测试缺口
- **当前写法**: Plan 列出 7 个 fixture：positive extraction、target/limit negative、standard-deviation false-positive、no-text missing、pure index profile、enhanced index、calculated series。但没有覆盖 `missing_reasons=("tracking_error_ambiguous",)` 路径。
- **反例/失败场景**: Section 8.2 说 "If the extractor cannot distinguish actual observed tracking error from target/limit text, return `missing` with `missing_reasons=("tracking_error_ambiguous",)`"。没有 fixture 测试此路径，implementation agent 可能不实现 ambiguity 检测，或实现但不测试。
- **为什么有问题**: Ambiguity 是 direct-disclosure extractor 的关键 fail-safe 路径。如果 target/limit 文本和 observed value 出现在同一段落，extractor 需要区分。没有 fixture 覆盖此路径，implementation agent 可能跳过这个判断逻辑。
- **直接证据**: Plan Section 8.2 定义 ambiguity 路径；Plan Section 12 fixture 列表没有 ambiguity fixture。
- **影响**: 低——Implementation agent 可能遗漏 ambiguity 检测，但不会导致错误数据（因为 fallback 是 missing）
- **建议改法和验证点**: 在 Section 12 fixture 列表中新增 "performance fixture with ambiguous tracking-error text (target and observed mixed)" 并标注为 negative path。验证：ambiguity fixture 返回 `missing` 且 `missing_reasons` 包含 `tracking_error_ambiguous`。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

---

## Open Questions

| # | Question | Impact | Suggested resolution |
|---|---|---|---|
| OQ-1 | `ExtractionMode` 是否需要扩展 `developer_override`，还是 `developer_override` 使用 `extraction_mode="missing"` 并通过 `source_type` 区分？ | 影响 Slice A 模型设计和所有 consumer 的 mode 判断逻辑 | 建议在 Slice A 中显式裁决，推荐扩展 `ExtractionMode` |
| OQ-2 | QDII 基金的 tracking-error 分析是始终适用还是仅在 tracking lens 适用时？Plan Section 8.1 的条件不精确。 | 影响 fund_type gating 逻辑 | 建议在 plan 中明确：QDII 指数型适用，QDII 主动型不适用 |
| OQ-3 | `benchmark_index_code` 的数据来源是什么？当前 `benchmark` 只提取 `benchmark_text`，没有 index code。 | 影响 `IndexProfileValue` 的可实现性 | 建议首版设为 `None`，后续从 index series adapter 获取 |

## Residual Risks

| Risk | Severity | Owner / Destination | Handling |
|---|---|---|---|
| `ExtractedField` mode 语义缺口 | 中 | P13-S1 plan update or Slice A | 在 plan 或 implementation 中显式裁决 |
| Renderer input 管道未显式 | 中 | P13-S1 plan update or Slice E | 明确通过 `structured_data` 访问 |
| `run_risk_checks` API 迁移路径未定义 | 中 | P13-S1 plan update or Slice D | 定义 helper 返回类型和签名变更策略 |
| Composite benchmark 预留字段可能误导 | 低 | Slice C acceptance criteria | 补充 composite 路径的 missing 行为 |
| Ambiguity fixture 缺失 | 低 | Section 12 fixture list | 新增 ambiguity fixture |
| Calculated tracking error 的 golden answer 缺失 | 低 | Future Slice G | 首版只做 direct disclosure，calculated 路径后续补充 golden |
| `IndexProfileValue` 模型较宽（14 字段） | 低 | Slice C | 首版可简化为 benchmark context only，methodology/constituents 字段保留 None |

---

## Architecture Boundary Review

Plan 正确维护了三层架构边界：

- Capability 层 owns `IndexProfileValue`、`TrackingErrorValue`、`resolve_tracking_error_for_risk` helper、extraction、renderer、audit。
- Service 层只协调，不解析来源或检查仓库内部。
- UI 层不直接调用 document source、PDF cache 或 index adapter。
- `FundDocumentRepository` 仍是生产年报唯一入口。

**无架构边界违反。**

## Overcoupling Review

Plan 的 slice 切分合理，各 slice 独立可交付：

- Slice A（typed models）不依赖 B-G。
- Slice B（direct extraction）只依赖 A 和 `ParsedAnnualReport`。
- Slice C（index profile）只依赖 A 和 benchmark field。
- Slice D（risk migration）依赖 A 但不依赖 B/C 的具体实现。
- Slice E（renderer）依赖 A/B/C。
- Slice F（audit）依赖 A/B/C/E。
- Slice G（calculated）独立且可选。

**无过度耦合问题。**

## Best-Practice Review

- Plan 显式定义了 source failure taxonomy，复用已有年报 taxonomy，这是好的实践。
- Plan 显式禁止 `extra_payload`，要求所有字段 typed，符合项目硬约束。
- Plan 显式定义了 stop conditions，防止 scope creep。
- Plan 的 fixture 策略使用人工确定性 fixture，避免网络依赖，符合测试最佳实践。

**无重大最佳实践偏离。**

---

## Conclusion

**Verdict: `pass-with-risks`**

Plan 是 substantially code-generation-ready 的。它正确回答了 controller 的 5 个约束，定义了清晰的 source contract、data model、extraction decision tree、renderer/audit/risk consumption rules、7 个 implementation slices 和 positive acceptance criteria。Architecture boundaries 和 slice independence 经验证无问题。

3 个中等风险 finding 需要在 implementation 前解决：

1. `ExtractedField` extraction_mode 与 `developer_override` source_type 的语义缺口——需在 Slice A 显式裁决。
2. Renderer 消费新字段的 `TemplateRenderInput` 管道——需在 Slice E 显式声明通过 `structured_data` 访问。
3. `ResolvedTrackingErrorForRisk` helper 返回类型和 `run_risk_checks` 迁移路径——需在 Slice D 定义具体 API。

2 个低风险 finding 可在 implementation 中处理：composite benchmark 预留字段的 acceptance criteria 补充，和 ambiguity fixture 覆盖。

这些问题不阻断 plan acceptance，但应在 implementation gate 前由 controller 裁决或在 plan 中补充，以避免 implementation agent 需要架构猜测。
