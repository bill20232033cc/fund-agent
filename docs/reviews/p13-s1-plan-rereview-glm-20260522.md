# P13-S1 Plan Re-Review — GLM（2026-05-22）

## Scope

Targeted re-review of revised `docs/reviews/p13-s1-tracking-error-index-data-plan-20260522.md` against findings in:

- `docs/reviews/p13-s1-plan-review-glm-20260522.md` (GLM F1–F4)
- `docs/reviews/p13-s1-plan-review-mimo-20260522.md` (MiMo 01–05)

Verdict: **PASS** — all 9 findings closed; all blocking open questions resolved.

## Finding Closure Table

| Finding | Severity | Closure evidence in revised plan | Verdict |
|---------|----------|----------------------------------|---------|
| **GLM F1**: Slice D `run_risk_checks` 签名变更路径未指定 | 中 | §11.1 定义了具体 `ResolvedTrackingErrorForRisk` dataclass（10 个显式字段、两个 Literal 类型）。Migration target 明确："migrate `run_risk_checks` from raw scalar to resolved object"；"Do not keep an equal fallback raw scalar parameter"。Slice D acceptance 写明 "no equal raw-scalar tracking-error authority remains"。Acceptance criteria #7/#8 锁定单路径。 | **Closed** |
| **GLM F2**: 新增 bundle 字段与 quality gate snapshot/FQ2 交互未声明 | 中 | §11.3 显式声明："Do not add to `comparable_values`"；"Do not add to FQ2 coverage denominator, golden answer correctness denominator, or FQ0 strict preconditions"。新增 Slice H 专门处理 snapshot observability。Acceptance criteria #12 锁定策略。Review criteria 将"leaves quality gate behavior implicit"列为 reject 条件。 | **Closed** |
| **GLM F3**: 非指数基金 `index_profile` 值未显式指定 | 低 | §8.2 IndexProfileValue rules 最后一行明确：非指数基金 "still present on the bundle as `ExtractedField(value=None, extraction_mode="missing", ...)`; never make the bundle field itself optional"。§9.1 authority resolution 同步："Always construct index_profile"。Acceptance criteria #11 锁定。 | **Closed** |
| **GLM F4**: QDII tracking lens 适用条件未定义 | 低 | §9.1 显式声明：QDII "current P13 treats tracking_error as not_applicable, because current FundType does not distinguish QDII index products from QDII active products"。Acceptance criteria #9 锁定。 | **Closed** |
| **MiMo 01**: `ExtractionMode` 与 `TrackingErrorValue.source_type` 语义缺口 | 中 | §8.4 新增显式映射表。`TrackingErrorValue.source_type` 现在只有 `direct_disclosure` 和 `calculated_from_series`（移除 `developer_override`）。Developer override 仅存在于 `ResolvedTrackingErrorForRisk.source_type`。Slice A boundary："do not expand `ExtractionMode`"。 | **Closed** |
| **MiMo 02**: Renderer 消费新字段的 `TemplateRenderInput` 管道未定义 | 中 | §10 明确："Use `input_data.structured_data.index_profile`"和"Use `input_data.structured_data.tracking_error`"；"Preserve current `TemplateRenderInput` shape"。Slice E boundary 和 acceptance criteria #5 锁定。Review criteria 将"changes `TemplateRenderInput` shape without explicit accepted justification"列为 reject。 | **Closed** |
| **MiMo 03**: `ResolvedTrackingErrorForRisk` 返回类型和迁移路径未定义 | 中 | 与 GLM F1 合并关闭。§11.1 提供完整 dataclass、Literal 类型、resolver precedence（4 种情况）、migration target。 | **Closed** |
| **MiMo 04**: Composite benchmark 预留字段可能误导实现 | 低 | §9.1 新增 "Acceptance for composite benchmark" 子节：直接披露仍可消费；计算路径必须返回 `missing` 直到 weighted composite contract 存在。Slice C acceptance 和 acceptance criteria #10 锁定。Fixture 列表包含 composite benchmark missing fixture。 | **Closed** |
| **MiMo 05**: Ambiguity extraction 路径缺少 fixture | 低 | §13 fixture 列表新增："New performance fixture with ambiguous target and observed-looking tracking-error text mixed together; must return `missing` with `tracking_error_ambiguous`"。 | **Closed** |

## Open Questions Resolution

| Question | Resolution |
|----------|------------|
| **GLM OQ1**: `ResolvedAnalyzeContract.tracking_error` 字段迁移后语义 | Resolver 设计（§11.1）表明 Service 仍通过 `resolved_contract.tracking_error` 传递 developer override 字符串给 resolver，但 product mode 不消费它。不需要修改 `ResolvedAnalyzeContract` 类型——resolver 的输入签名已显式区分 `tracking_error_field` 和 `developer_override`。Resolved. |
| **GLM OQ2**: Developer override `EvidenceAnchor.source_kind` | §8.4 明确："Do not attach annual-report anchors to developer override"。§11.1 明确："developer override produces empty anchors"。不构造 anchor，因此 `source_kind` 问题不适用。Resolved. |
| **GLM OQ3**: Renderer product/developer mode 区分 | §10.2 明确："developer_override is not present in `input_data.structured_data.tracking_error`; renderer ignores it by construction"。Renderer 无需区分 mode。Resolved. |
| **MiMo OQ-1**: `ExtractionMode` 是否扩展 | §8.4 显式："Do not expand `ExtractionMode`"。Resolved. |
| **MiMo OQ-2**: QDII 适用性 | §9.1 显式：P13 QDII not applicable。Resolved. |
| **MiMo OQ-3**: `benchmark_index_code` 数据来源 | §8.2 rule："`benchmark_index_code` is optional and must not be guessed from fund code"。First implementation 为 `None`。Acceptable. |

## Residual Risks (Unchanged)

| Risk | Severity | Tracking destination |
|------|----------|---------------------|
| 跟踪误差直接披露的年报格式多样性 | Medium | P13 Slice B 验证阶段 |
| Quality gate tracking_error 覆盖延迟至后续 golden-answer phase | Medium | P14 或下一个 golden-answer 更新 phase |
| 外部指数序列 adapter 数据源稳定性 | Medium | Slice G plan/review gate |

## Conclusion

**PASS**

Revised plan closes all 9 findings from both reviews with specific, verifiable additions. The three key medium-severity gaps (risk-check API migration, quality gate policy, renderer input pipe) are now addressed with concrete dataclass definitions, explicit non-goals, and locked acceptance criteria. No new findings introduced by the revision.
