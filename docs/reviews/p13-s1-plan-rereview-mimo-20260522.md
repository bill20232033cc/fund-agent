# P13-S1 Plan Re-Review — MiMo（2026-05-22）

## Reviewed Target

Revised `docs/reviews/p13-s1-tracking-error-index-data-plan-20260522.md`

## Scope

Targeted re-review: verify whether the revised plan closes all findings from `docs/reviews/p13-s1-plan-review-mimo-20260522.md` (MiMo 01-05) and `docs/reviews/p13-s1-plan-review-glm-20260522.md` (GLM F1-F4). Does not expand into implementation review.

## Review Inputs

| Source | Role |
|---|---|
| Revised plan | `docs/reviews/p13-s1-tracking-error-index-data-plan-20260522.md` |
| MiMo initial review | `docs/reviews/p13-s1-plan-review-mimo-20260522.md` — 5 findings |
| GLM initial review | `docs/reviews/p13-s1-plan-review-glm-20260522.md` — 4 findings, 3 open questions |
| Code facts | `models.py:9-10`, `risk_check.py:173-183`, `renderer.py:60-85`, `fund_analysis_service.py:370-378`, `extraction_snapshot.py:41,165-187` |

---

## Finding Closure Table — MiMo (01-05)

| # | Severity | Summary | Closure section in revised plan | Verdict |
|---|---|---|---|---|
| 01 | 中 | `ExtractedField.extraction_mode` 与 `TrackingErrorValue.source_type` 语义缺口 | §8.4: explicit mapping table; decision "Do not expand ExtractionMode in P13"; developer override lives only in `ResolvedTrackingErrorForRisk.source_type`, not in `ExtractedField` | **CLOSED** |
| 02 | 中 | Renderer 消费新字段的 `TemplateRenderInput` 管道未显式定义 | §10: "Use `input_data.structured_data.index_profile`" and "Use `input_data.structured_data.tracking_error`"; "Preserve current TemplateRenderInput shape"; Slice E acceptance: "no TemplateRenderInput shape change" | **CLOSED** |
| 03 | 中 | `ResolvedTrackingErrorForRisk` 返回类型和 `run_risk_checks` 迁移路径未定义 | §11.1: concrete dataclass with 10 fields; `run_risk_checks` migrates to `tracking_error: ResolvedTrackingErrorForRisk`; "Do not keep an equal fallback raw scalar parameter" | **CLOSED** |
| 04 | 低 | Composite benchmark 预留字段可能误导 implementation agent | §9.1: acceptance paragraph "Composite benchmark is a valid index_profile.benchmark_identity_status"; §9.3: "Composite benchmark calculation is not allowed"; §15 criteria #10: composite fixture required | **CLOSED** |
| 05 | 低 | Ambiguity extraction 路径缺少 fixture 覆盖 | §13: explicit fixture "ambiguous target and observed-looking tracking-error text mixed together"; acceptance "must return missing with tracking_error_ambiguous" | **CLOSED** |

## Finding Closure Table — GLM (F1-F4)

| # | Severity | Summary | Closure section in revised plan | Verdict |
|---|---|---|---|---|
| F1 | 中 | Slice D 风险检查迁移接口歧义，`run_risk_checks` 签名变更路径未指定 | §11.1: concrete `ResolvedTrackingErrorForRisk` dataclass; "migrate run_risk_checks from raw scalar to resolved object"; "Do not keep an equal fallback raw scalar parameter" | **CLOSED** |
| F2 | 中 | 新增 bundle 字段与 quality gate snapshot/FQ2 覆盖交互未声明 | §11.3 + Slice H: "Do not add index_profile or tracking_error subfields to comparable_values in P13 first implementation"; "Existing quality gate status must not change"; explicit rationale and validation | **CLOSED** |
| F3 | 低 | 非指数基金 `index_profile` 值未显式指定 | §8.2 rule: "For non-index fund types, index_profile is still present on the bundle as ExtractedField(value=None, extraction_mode='missing')"; §9.1: explicit non-index branch; Slice C acceptance | **CLOSED** |
| F4 | 低 | QDII 基金 tracking lens 适用条件未定义 | §9.1: "current P13 treats tracking_error as not_applicable, because current FundType does not distinguish QDII index products from QDII active products"; §15 criteria #9 | **CLOSED** |

## Open Question Closure Table — GLM (OQ1-OQ3)

| # | Question | Revised plan disposition | Verdict |
|---|---|---|---|
| OQ1 | `ResolvedAnalyzeContract.tracking_error` 字段语义/类型是否需变更 | §11.1: "migrate run_risk_checks from raw scalar to resolved object"; `ResolvedAnalyzeContract.tracking_error` is the source for developer override, resolved before `run_risk_checks` call | **ADDRESSED** |
| OQ2 | Developer override 的 `EvidenceAnchor.source_kind` 应该用什么 | §8.4: "Do not attach annual-report anchors to developer override"; §11.1: `ResolvedTrackingErrorForRisk.anchors=()` for developer override | **ADDRESSED** |
| OQ3 | Renderer 是否需要区分 product/developer mode 渲染逻辑 | §10.2: "developer_override is not present in input_data.structured_data.tracking_error; renderer ignores it by construction" | **ADDRESSED** |

## Open Question Closure Table — MiMo (OQ-1 to OQ-3)

| # | Question | Revised plan disposition | Verdict |
|---|---|---|---|
| OQ-1 | `ExtractionMode` 是否需要扩展 `developer_override` | §8.4 decision: "Do not expand ExtractionMode in P13" with explicit mapping table | **CLOSED** |
| OQ-2 | QDII 基金 tracking-error 分析是始终适用还是仅在 tracking lens 适用时 | §9.1: "current P13 treats tracking_error as not_applicable" for all QDII | **CLOSED** |
| OQ-3 | `benchmark_index_code` 的数据来源是什么 | §8.2 rule: "benchmark_index_code is optional and must not be guessed from fund code" — still no explicit source defined, but field is optional and will be `None` in first implementation | **LOW RISK — not blocking** |

## Verification Of Revised Plan Internal Consistency

| Check | Result |
|---|---|
| §8.3 `source_type` excludes `developer_override` | **Consistent** — only `direct_disclosure` and `calculated_from_series` |
| §8.4 mapping table matches §11.1 resolver precedence | **Consistent** — developer override resolved outside `ExtractedField`, never in bundle |
| §9.1 non-index/QDII branches match §15 criteria #9 and #11 | **Consistent** |
| §10 renderer input pipe matches §11 Slice E inputs | **Consistent** — both reference `input_data.structured_data.*` |
| §11.1 `run_risk_checks` migration matches Slice D acceptance | **Consistent** — "no equal raw-scalar tracking-error authority remains" |
| §11.3 quality gate policy matches Slice H scope | **Consistent** — observable but non-comparable |
| §13 fixture list includes ambiguity (MiMo 05) and composite (MiMo 04) | **Consistent** — 9 fixtures listed |
| §15 acceptance criteria #5, #7, #8, #9, #10, #11, #12 address all findings | **Consistent** |
| §16 review criteria includes new rejection conditions | **Consistent** — "stores developer override inside StructuredFundDataBundle", "changes TemplateRenderInput shape", "leaves quality gate FQ2 behavior implicit" |

## Residual Risks From Re-Review

| Risk | Severity | Notes |
|---|---|---|
| `run_risk_checks` signature migration will require updating all existing `test_risk_check.py` tests that pass raw scalar | Low | Expected implementation cost; Slice D explicitly owns this file |
| `benchmark_index_code` data source still undefined | Low | Field is optional; first implementation returns `None` |
| `IndexProfileValue` has 14 fields, some of which (`methodology_*`, `constituents_*`) will be `None`/`missing` in first implementation | Low | Acceptable for future-proofing; no overcoupling risk |

---

## Conclusion

**Verdict: `PASS`**

All 9 findings (MiMo 01-05, GLM F1-F4) are closed by the revised plan. All 6 open questions (GLM OQ1-OQ3, MiMo OQ-1 to OQ-3) are addressed or determined non-blocking. The revised plan shows internal consistency across data model, extraction decision tree, renderer consumption, risk check migration, quality gate policy, fixture strategy, and acceptance criteria. No new blocking issues were introduced by the revision. The plan is code-generation-ready for the future implementation gate.
