# P13-S1 Plan Review — GLM（2026-05-22）

## Reviewed Target and Scope

- **Target artifact**: `docs/reviews/p13-s1-tracking-error-index-data-plan-20260522.md`
- **Current gate**: `P13-S1 tracking-error / index-data source contract plan-review`
- **Design truth**: `docs/design.md`
- **Control truth**: `docs/implementation-control.md`
- **Controller constraints**: `docs/reviews/next-phase-selection-controller-judgment-20260522.md`
- **Rule source**: `AGENTS.md`
- **Review posture**: Constructively adversarial. Default skepticism; evidence-based findings only; no style feedback.

## Assumptions Tested

| # | Assumption | Verdict |
|---|-----------|---------|
| A1 | Current `StructuredFundDataBundle` has no tracking_error or index_profile fields | **Confirmed** — `fund_agent/fund/data_extractor.py:63-99` lists 14 fields; none are tracking-related |
| A2 | Renderer hardcodes tracking error as `数据不足` | **Confirmed** — `fund_agent/fund/template/renderer.py:569-593` `_render_tracking_error_segment` returns fixed insufficient text |
| A3 | Risk check receives `tracking_error` as a scalar parameter and returns `insufficient_data` when absent | **Confirmed** — `fund_agent/fund/analysis/risk_check.py:485-540` `_check_tracking_error` takes `Decimal | str | int | float | None`; `None` → `insufficient_data` |
| A4 | Service passes `resolved_contract.tracking_error` into `run_risk_checks` | **Confirmed** — `fund_agent/services/fund_analysis_service.py:377` |
| A5 | CLI `--tracking-error` is gated behind `--dev-override` | **Confirmed** — `fund_agent/ui/cli.py:81-83` |
| A6 | `FundDocumentRepository` only exposes `load_annual_report()` | **Confirmed** — `fund_agent/fund/documents/repository.py:267-318` single public async method |
| A7 | NAV adapter only fetches fund NAV, not index NAV | **Confirmed** — `fund_agent/fund/data/nav_data.py:38-76` `_default_nav_fetcher` calls akshare `fund_open_fund_info_em` |
| A8 | No pure `index_fund` profile fixture exists | **Confirmed** — `tests/fixtures/fund/extractors/profile/` has `active_fund`, `bond_fund`, `index_enhanced` only |
| A9 | `ExtractedField` supports `direct/derived/estimated/missing` modes | **Confirmed** — `fund_agent/fund/extractors/models.py:9` |
| A10 | `EvidenceAnchor.source_kind` is `Literal["annual_report", "external_api", "derived"]` | **Confirmed** — `fund_agent/fund/extractors/models.py:10` |
| A11 | Tracking error data is product-significant for index/enhanced-index `preferred_lens` | **Confirmed** — `docs/design.md:131-140` tracking error is primary lens variable |
| A12 | Risk rule says tracking error > 2% is index-fund veto condition | **Confirmed** — `docs/design.md:184-192` |

## Findings

### F1-未修复-中-Slice D 风险检查迁移接口歧义，run_risk_checks 签名变更路径未指定

- **位置**: Plan §10.1 (Risk Check), Slice D (§11 Slice D)
- **问题类型**: 不可直接实施 / 架构边界
- **当前写法**: Plan 提出 Capability helper `resolve_tracking_error_for_risk(tracking_error_field, developer_override, developer_override_enabled) -> ResolvedTrackingErrorForRisk`，但不指定 `run_risk_checks` 签名如何变更。
- **反例/失败场景**: Implementation agent 面临三个互斥路径：(a) `run_risk_checks` 签名改为接受 `ResolvedTrackingErrorForRisk`，导致所有现有 `test_risk_check.py` 测试从传入原始 scalar 改为构造 resolver 输出，测试变更面大且超出 Slice D 文件列表；(b) resolver 输出一个 flat scalar 回填原签名，但这样 risk_check 内部丢失 provenance/authority/source_type 信息，无法在 risk_check item anchor 中体现来源；(c) 在原签名旁新增参数形成双路径，引入 Slice D 本应消除的 authority dual-path 问题。Plan 没有指定选择哪条路径，implementation agent 必须自行做架构决策。
- **为什么有问题**: Plan 声称要消除 Service override 和 Capability extraction 的双 authority 路径，但 Slice D 的接口变更不够具体，反而可能在 `run_risk_checks` 层引入新的歧义。违反了 positive acceptance criteria #3（developer override 有明确 precedence/conflict behavior）的实现前提——如果接口不明确，conflict behavior 无法 deterministic 测试。
- **直接证据**: 当前 `run_risk_checks` 签名为 `tracking_error: Decimal | str | int | float | None = None`（`risk_check.py:181`）。Service 调用点为 `tracking_error=resolved_contract.tracking_error`（`fund_analysis_service.py:377`）。Plan §10.1 只定义了 resolver helper，未指定 `run_risk_checks` 如何消费 resolver 输出。
- **影响**: Implementation agent 可能选择不一致的路径，导致 Slice D 的测试无法被 plan review 验收；或 risk_check 丢失 provenance 信息，使 audit trail 不完整。
- **建议改法和验证点**: Plan 应在 §10.1 或 Slice D 中显式指定以下之一：(a) `run_risk_checks` 新增参数 `tracking_error_resolved: ResolvedTrackingErrorForRisk | None = None`，与原 `tracking_error` 参数互斥，Capability helper 输出直接传入；原有 scalar 参数仅在无 resolver 输出时 fallback，并在后续 phase 废弃；(b) `run_risk_checks` 保持原签名，但 Slice D 新增一个 wrapper/adapter 函数将 resolver 输出转为 scalar 并在 risk_check item anchor 中附加 provenance。推荐 (a) 因为它让 risk_check 保留 authority 信息并保持 audit trail 完整。验证点：Slice D 测试应证明 product mode 传入 `tracking_error_resolved` 时 authority 为 Capability 数据，developer override 传入时 authority 标记为 dev fallback。
- **修复风险（低）**: 仅需在 plan §10.1 和 Slice D 补充一段接口说明，不改变整体架构。
- **严重程度（中）**: 不修复会导致 implementation agent 在关键接口上做出不一致决策，增加 re-review 返工风险。

### F2-未修复-中-新增 bundle 字段与 quality gate snapshot/FQ2 覆盖交互未声明

- **位置**: Plan §7.1 (New Structured Bundle Fields), §14 (Positive Acceptance Criteria)
- **问题类型**: 契约缺失 / 过度耦合
- **当前写法**: Plan 在 §7.1 新增 `index_profile: ExtractedField[IndexProfileValue]` 和 `tracking_error: ExtractedField[TrackingErrorValue]` 到 `StructuredFundDataBundle`，但全文未提及这些新字段如何与现有 quality gate extraction snapshot / scoring / FQ2 coverage 交互。
- **反例/失败场景**: (1) 新字段被 snapshot 记录但不在 `comparable_values` 白名单中——FQ2 覆盖率不受影响，但 snapshot 显示这些字段存在且 quality gate 不可见；(2) 新字段加入白名单但 golden answer 不包含这些字段——correctness comparison 对这些字段输出 `unavailable`，可能触发 FQ0/info 或影响 coverage 分母；(3) 新字段完全被 snapshot 忽略——与 plan 声称的"evidence-based audit"目标不一致。三种路径对 product behavior 有不同影响，plan 未指定应选哪种。
- **为什么有问题**: P5-S3 建立的 `comparable_values` 白名单机制是质量门控的字段级覆盖基础。新增 bundle 字段如果不显式声明与该机制的关系，implementation agent 可能：(a) 默认让 snapshot 记录但不影响评分（正确但未验证）；(b) 错误地加入白名单导致 golden coverage 回退；(c) 不加入 snapshot 导致 audit trail 不完整。
- **直接证据**: `StructuredFundDataBundle` 是 extraction snapshot 的输入源。P5-S3 plan 建立了白名单子字段机制。Plan §14 的 acceptance criteria 没有任何关于 quality gate 交互的条目。Plan §5 (Non-Goals) 提到"不修改 quality gate"但新增 bundle 字段本身就是对 snapshot 输入的修改。
- **影响**: Implementation 后可能出现：(a) 质量门控对新字段盲区——无法检测 tracking_error 提取退化；(b) golden coverage 分母突变导致已有基金的 gate 状态非预期变化；(c) 与 plan non-goal "不修改 quality gate" 冲突。
- **建议改法和验证点**: Plan 应在 §7.1 或 §14 显式声明以下之一：(a) P13 first implementation 不将 `index_profile`/`tracking_error` 加入 `comparable_values` 白名单，snapshot 记录但不影响 FQ2 分母——这需要在 slice A/B 实现中确认 snapshot 逻辑不变；(b) 将这些字段加入白名单但 golden answer 构建流程同步更新——这需要在 slice A 或单独的 golden-answer 补丁中处理。推荐 (a) 用于 first implementation，因为 tracking_error 提取尚未稳定，不应立即影响 quality gate 分母。验证点：P13 实现后运行现有 golden answer correctness 对比不应产生新的 mismatch。
- **修复风险（低）**: 仅需在 plan 补充一段声明。
- **严重程度（中）**: 不修复可能导致 implementation 后 quality gate 行为非预期变化，或遗漏 tracking_error 提取退化的检测能力。

### F3-未修复-低-非指数基金 index_profile 值未显式指定

- **位置**: Plan §8.1 (Authority Resolution), §7.2 (IndexProfileValue)
- **问题类型**: 契约缺失
- **当前写法**: Plan §8.1 对 tracking_error 指定了非指数基金行为（`missing/not_applicable`），但对 `index_profile` 没有对应规则。Plan §7.2 定义了 `IndexProfileValue` 数据模型但没有说非指数基金类型是否应构造该值。
- **反例/失败场景**: Implementation agent 对 `active_fund` 的 `index_profile` 可能选择：(a) `ExtractedField(value=None, extraction_mode="missing")` — 显式 missing；(b) bundle 中 `index_profile` 字段为 `None` — 不构造 ExtractedField。如果选择 (b)，下游 consumer 需要做 `None` 检查，与现有 bundle 字段（全部非 None ExtractedField）的处理模式不一致。如果选择 (a)，对于主动基金来说构造了一个永远不会被消费的 `IndexProfileValue(missing)` 对象。
- **为什么有问题**: Plan 声称 positive acceptance criteria #12 要求"覆盖 pure index_fund, enhanced_index, active/non-index deletion path, and missing-data path"，但没有指定 active/non-index 路径的 `index_profile` 行为。Implementation agent 可能对同一基金类型产生不同的 bundle 结构。
- **直接证据**: 当前 `StructuredFundDataBundle` 所有字段都是 `ExtractedField[T]`（非 Optional），即 bundle 总是构造完整的 ExtractedField。Plan §7.1 新增的 `index_profile: ExtractedField[IndexProfileValue]` 如果对非指数基金设为 `None`，会打破这一 pattern。
- **影响**: 实现后非指数基金的 bundle 结构不一致，renderer 或其他 consumer 需要额外的 None check，增加 coupling。
- **建议改法和验证点**: Plan §8.1 应补充一行："For non-index fund types, `index_profile` should be `ExtractedField(value=None, extraction_mode="missing", anchors=(), note="非指数基金不适用指数画像")` to maintain bundle field consistency." 验证点：Slice A 测试应证明非指数基金 bundle 构造后 `index_profile.extraction_mode == "missing"`。
- **修复风险（低）**: 仅需补充一行规则。
- **严重程度（低）**: 不修复不会导致错误行为，但会增加 implementation agent 的歧义。

### F4-未修复-低-QDII 基金 tracking lens 适用条件未定义

- **位置**: Plan §8.1 (Authority Resolution), line "qdii_fund when tracking lens applies"
- **问题类型**: 契约缺失
- **当前写法**: Authority resolution 写 "If fund_type not in {index_fund, enhanced_index, qdii_fund when tracking lens applies}"，但 "when tracking lens applies" 的条件未定义。
- **反例/失败场景**: 一个 QDII 指数基金（如标普 500 ETF）应适用 tracking_error 分析。一个 QDII 主动权益基金（如某 QDII 股票基金）的 `preferred_lens` 重点是"海外市场/汇率风险、跟踪或管理能力、成本"（`docs/design.md:138`），其中包含"跟踪"但不是唯一焦点。Implementation agent 需要判断 QDII 主动基金是否进入 tracking_error extraction。
- **为什么有问题**: 设计真源 `docs/design.md:138` 对 QDII 的 lens 描述包含"跟踪或管理能力"，但 tracking_error extraction 只适用于有明确跟踪目标的指数/增强指数类 QDII。Plan 应区分 QDII 指数基金和 QDII 主动基金的 tracking_error 适用性。
- **直接证据**: `docs/design.md:138` QDII preferred_lens 为"海外市场/汇率风险、跟踪或管理能力、成本"。`docs/design.md:341` 基金类型列表中 QDII 是 `qdii_fund` 一个类别，未细分为 QDII 指数/QDII 主动。
- **影响**: 如果所有 QDII 都进入 tracking_error extraction，QDII 主动基金会产生无意义的 missing extraction 和多余的 audit 记录。如果都不进入，QDII 指数基金缺失 tracking_error 分析。
- **建议改法和验证点**: Plan §8.1 应将条件改为基于 `classified_fund_type` 的具体判断，例如："qdii_fund 类型如果年报产品描述或业绩基准表明其跟踪特定指数（如 QDII ETF/LOF），则适用 tracking_error extraction；否则 tracking_error = missing/not_applicable。" 或者更简单地声明："当前 MVP 只对 `index_fund` 和 `enhanced_index` 执行 tracking_error extraction；QDII 统一走 missing/not_applicable 路径，待后续 QDII 细分类型设计后扩展。" 推荐后者，因为它与当前 `FundTypeClassification` 的粒度一致。
- **修复风险（低）**: 仅需修改一行条件。
- **严重程度（低）**: 当前 QDII fixture 不存在，即使行为不明确也不会立即产生用户可见问题。

## Open Questions

| # | Question | Risk if unresolved | Suggested owner |
|---|----------|--------------------|-----------------|
| OQ1 | Slice D 是否应同时修改 `ResolvedAnalyzeContract.tracking_error` 字段的语义或类型？当前该字段是 `Decimal | str | int | float | None`，迁移后 product mode 不再通过该字段传递 tracking error。 | Implementation agent 可能保留原字段作为 developer override 通道，也可能试图删除/重命名它。如果不统一，两个 tracking_error 路径可能并存。 | P13 implementation plan |
| OQ2 | `EvidenceAnchor.source_kind` 当前为 `Literal["annual_report", "external_api", "derived"]`。Plan §7.4 新增了 `source_kind="derived"` 用于 calculated 值，这与现有枚举兼容。但 plan 同时提到 developer override 使用 "no annual-report anchor"——developer override 的 anchor 应该用什么 `source_kind`？用 `"external_api"` 语义不正确，用 `None` 则 `EvidenceAnchor.source_kind` 类型需要改为 Optional。 | Implementation agent 可能对 developer override anchor 的 source_kind 做出不一致选择。 | P13 implementation plan |
| OQ3 | Plan §9.2 提到 renderer 对 `developer_override` 值"should not replace product renderer text unless a future plan explicitly adds a visible dev-only report marker"。这是否意味着 Slice E 的 renderer 实现需要区分 product mode 和 developer mode 的渲染逻辑？ | 如果需要区分，Slice E 的 boundary 和 acceptance 条件更复杂。如果不需要（直接忽略 developer override），plan 应明确说。 | P13 plan clarification |

## Residual Risks and Suggested Tracking Destination

| Risk | Severity | Tracking destination |
|------|----------|---------------------|
| 跟踪误差直接披露的年报格式多样性——不同基金公司年报中跟踪误差的文本/表格位置和措辞可能有显著差异，P13 first implementation 的 extraction pattern 可能覆盖不足 | Medium | P13 implementation Slice B 验证阶段；如 extraction hit rate 低，升级为后续 extraction-pattern-hardening phase |
| `IndexProfileValue` 的 `benchmark_component_text` 字段对复合基准的解析复杂度——当前只存储文本，但后续如果需要从文本中自动识别各成分权重，可能需要额外的 NLP/规则设计 | Low | Future index document/source contract phase |
| Quality gate 对新增 tracking_error/index_profile 字段的覆盖策略 (F2) 如果选择延迟加入白名单，tracking_error extraction 退化在 P13 期间不可被 quality gate 自动检测 | Medium | P13 implementation follow-up; 至少应在 P14 或下一个 golden-answer 更新 phase 中纳入 |
| 外部指数序列 adapter (Slice G) 的数据源稳定性和合规性——akshare 或其他数据源的指数数据可能存在缺失、延迟或与官方指数不一致的风险 | Medium | Slice G plan/review gate; 不在 P13 first implementation scope 内 |

## Architecture Boundary Review

| Boundary | Verdict | Evidence |
|----------|---------|----------|
| Extraction stays in Fund Capability | **Pass** | Plan §11 Slice B/C 属于 `fund_agent/fund/extractors/` |
| Risk-check resolver stays in Fund Capability | **Pass** | Plan §10.1 指定 `fund_agent/fund/analysis/` |
| Renderer consumes structured fields only, no source access | **Pass** | Plan §9 明确禁止 renderer 调用 repository/source |
| Service coordinates explicit fields, no source parsing | **Pass** | Plan §11 Slice D 明确 Service 不解析来源 |
| No UI/Service direct source access | **Pass** | Plan §5 Non-Goals, §6.3 adapter upper bound |
| External index adapter bounded under Capability | **Pass** | Plan §6.3 limits to one read-only module under `fund_agent/fund/data/` |

## Best-Practice Review

- **Testability**: Plan fixture strategy (§12) is appropriate — artificial fixtures with explicit positive/negative/ambiguity/missing paths. No live network. Consistent with existing P1-P12 test patterns.
- **Maintainability**: `TrackingErrorValue` and `IndexProfileValue` have many fields but each serves a documented provenance purpose. Not overengineered given the project's audit requirements.
- **Observability**: Extraction mode, source_type, provenance_note, and anchor rules provide adequate audit trail for tracking error data. Missing path has explicit reasons.
- **Failure handling**: Source failure taxonomy reuse (§6.2) is correct. Missing extraction is clearly distinguished from source failure. `insufficient_data` preserved for risk check.

## Optimal-Solution Review

- Direct disclosure first, calculated later is the correct priority given data availability constraints.
- Methodology/constituents tiering (Tier 0-4) is well-calibrated — benchmark-only text does not upgrade to methodology/constituents, which is correct and prevents false evidence.
- The bounded external index adapter (one method, one data type, no search/analytics) is the right upper bound to avoid scope creep.
- Developer override lower-priority precedence is correct for maintaining product evidence integrity.

## Overengineering Review

- `TrackingErrorValue` has 17 fields. While this seems large, each field serves provenance/audit requirements that align with the project's `R=A+B-C` evidence-chain standards. Fields like `observation_count`, `frequency`, `annualization_factor` are gated to calculated values only. Not overengineered.
- External index adapter upper bound (§6.3) includes explicit scope limits preventing methodology scraping, real-time quotes, and all-index discovery. Appropriately bounded.
- Source tiering (Tier A-D) adds complexity but is necessary to prevent benchmark text from masquerading as tracking error evidence.

## Overcoupling Review

- Slices A-G are properly sequenced with clear file ownership and boundaries. No slice requires cross-slice coordination beyond the data model contract.
- The resolver helper in Slice D is a unidirectional dependency (Capability → risk_check), not a bidirectional coupling.
- `benchmark_identity_status` appears in both `IndexProfileValue` and `TrackingErrorValue`, but this is intentional: `TrackingErrorValue` must be self-contained for provenance without cross-referencing `IndexProfileValue`. No overcoupling.

## Plan Review Conclusion

**PASS**

The plan is code-generation-ready with acceptable residual risks. All four controller constraints are substantively answered with sufficient specificity for implementation:

1. **Tracking error authority and service override migration**: Precedence chain is clear (`direct_disclosure > calculated > developer_override > missing`). Migration target is well-defined. F1 identifies that the `run_risk_checks` interface change needs additional specification, but this is a local clarification within Slice D, not a structural gap.

2. **Disclosed-vs-calculated path**: Well separated — direct disclosure is Slice B, calculated is Slice G (optional future). Calculation prerequisites (identity, cache, provenance, minimum observations) are explicit.

3. **External index adapter upper bound**: Correctly bounded to one read-only adapter with no methodology/constituents/real-time quotes/search capabilities.

4. **Methodology/constituents tiering**: Tier 0-4 with clear rules. Tier 1 benchmark-only does not upgrade. P13 may stop at Tier 1.

5. **Positive acceptance criteria**: 13 specific criteria with clear pass/fail conditions.

6. **Pure index fixture strategy**: Artificial fixtures with no live downloads, no RR-13 dependency. Fixture list covers positive, negative, ambiguity, and missing paths.

All code facts cited in the plan are verified against the current codebase. Architecture boundaries are maintained. No Dayu runtime, LLM, Evidence Confirm, or E1-E3 is introduced. The plan is safe for future implementation with the findings noted above.
