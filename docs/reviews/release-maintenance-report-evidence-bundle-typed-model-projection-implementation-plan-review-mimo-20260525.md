# Plan Review: Typed ReportEvidenceBundle Model / Projection Implementation Plan

> Date: 2026-05-25
> Reviewer: AgentMiMo
> Reviewed artifact: `docs/reviews/release-maintenance-report-evidence-bundle-typed-model-projection-implementation-plan-20260525.md`
> Gate: `typed ReportEvidenceBundle model/projection implementation plan review`
> Scope: adversarial plan review only; no code, no commit, no push, no PR.

## Step Self-Check

- Reviewed target: the typed ReportEvidenceBundle model/projection implementation plan artifact.
- Truth sources consulted: `AGENTS.md`; `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point / Open Residuals; `docs/design.md` §2.1, §5.4, §5.4.1, §5.4.2, §5.4.3, §7.2, §7.3, §7.4; S2 bundle candidate plan and controller judgment; code facts in `fund_agent/fund/data_extractor.py`, `fund_agent/fund/extractors/models.py`, `fund_agent/fund/fund_type.py`, `fund_agent/fund/template/contracts.py`, `fund_agent/fund/template/lens_application.py`, and `tests/fund/test_extraction_snapshot.py`.
- Assumptions tested: code-generation readiness, file ownership, domain consistency, boundary preservation, test sufficiency, and internal consistency.

## Assumptions Tested

1. The plan can be implemented without forcing the implementer to redesign domains, dataclasses, or projection algorithm.
2. File ownership choices (`fund_agent/fund/report_evidence.py`, `tests/fund/test_report_evidence.py`) are correct and leak no Service/renderer/Host/Agent internals.
3. Enum/Literal domains are internally consistent and match the S2 accepted contract.
4. The plan preserves `FundDocumentRepository` boundary, explicit params, no `extra_payload`, no renderer/FQ0-FQ6 changes.
5. Tests and validation commands are sufficient, including negative tests.
6. No overdesign, missing edge cases, contradictory rules, or mismatch with current code.

## Findings

### 1-未修复-中-SourceFailureCategory domain 包含 S2 未接受的值

- **位置**: Exact Value Domains → Source Document / Boundary Domains → `SourceFailureCategory`
- **问题类型**: 契约缺失 / 域不一致
- **当前写法**: `SourceFailureCategory = Literal["none", "not_found", "unavailable", "schema_drift", "identity_mismatch", "integrity_error", "data_gap", "unknown_upstream_failure_category", "not_applicable"]`
- **反例/失败场景**: S2 bundle candidate plan 定义的 `source_failure_category` 域是 `none`, `not_found`, `unavailable`, `schema_drift`, `identity_mismatch`, `integrity_error`, `unknown_upstream_failure_category`。Implementation plan 新增了 `data_gap` 和 `not_applicable`，但 S2 未接受这两个值。`data_gap` 与 `GapKind` 中的 `source_failure` 语义重叠；`not_applicable` 未在 S2 中定义使用场景。
- **为什么有问题**: S2 controller judgment 明确说 "S2 accepted directly implementable contract decisions for ... source boundaries"。新增域值超出 accepted contract 会让 implementation agent 不确定是否应实现这些值的处理逻辑。
- **直接证据**: S2 plan `source_failure_category` 域（line 90）vs implementation plan `SourceFailureCategory`（lines 123-133）。S2 plan 只有 7 个值，implementation plan 有 9 个。
- **影响**: Implementation agent 可能实现 S2 未接受的值处理，或在测试中覆盖未定义的行为。
- **建议改法和验证点**: 去掉 `data_gap` 和 `not_applicable`，或在 plan 中显式说明这两个值是 implementation 新增并解释使用场景和测试覆盖。验证：`rg "data_gap|not_applicable" fund_agent/fund/report_evidence.py` 应只出现在 `GapKind` 或 `GapFailureCategory`，不应出现在 `SourceFailureCategory`。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 中

### 2-未修复-中-缺少 accepted_baseline 不可派生的显式测试

- **位置**: Test Plan (tests 1-20)
- **问题类型**: 测试缺口
- **当前写法**: Residual Risks 表格说 "Add explicit test that first slice rejects or never derives `accepted_baseline`"。但 Test Plan 的 20 个测试中没有一个专门验证 `accepted_baseline` 不可派生。
- **反例/失败场景**: Implementation agent 实现 review-status derivation 时，可能遗漏对 `accepted_baseline` 的阻断逻辑，导致 bundle 意外进入 `accepted_baseline` 状态。
- **为什么有问题**: Plan 明确要求 "the first implementation must never derive it unless a later curated-fixture gate adds an explicit enablement path" 和 "validation should reject any caller-supplied attempt to force `accepted_baseline`"。这是一个关键约束，但没有对应测试。
- **直接证据**: Residual Risks 表格 row "accepted_baseline domain exists but is not derivable"（line 905）要求显式测试。Test Plan（lines 768-857）无对应测试。
- **影响**: Implementation 可能允许 `accepted_baseline` 被派生或被 caller 强制设置，违反 S2 约束。
- **建议改法和验证点**: 在 Test Plan 中增加 `test_accepted_baseline_cannot_be_derived_or_forced`：构造满足所有 scoring_ready 条件的 bundle，断言 review_status 不是 `accepted_baseline`；构造 caller 显式传入 `accepted_baseline` 的 context，断言被拒绝。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 中

### 3-未修复-低-ReportDataGapOverride 字段未完全指定

- **位置**: Proposed Dataclasses (line 375)
- **问题类型**: 不可直接实施
- **当前写法**: Dataclass 列表包含 `ReportDataGapOverride`，Step 8 展示了 S1 turnover gap override 的使用示例，但未给出该 dataclass 的完整字段定义。
- **反例/失败场景**: Implementation agent 需要自行决定 `ReportDataGapOverride` 的字段。Step 8 的示例暗示了 `gap_kind`, `field_path`, `failure_category`, `reason_code`, `chapter_ids`, `required_report_wording`，但未明确哪些是 required vs optional。
- **为什么有问题**: 与 `ReportSourceDocument`, `ReportEvidenceAnchor`, `ReportFact` 等有详细字段说明的 dataclass 相比，`ReportDataGapOverride` 缺少同等规格。
- **直接证据**: Proposed Dataclasses 列表（lines 362-375）只列名字，Step 8（lines 583-599）只给使用示例。
- **影响**: 低。Implementation agent 可以从示例推断字段，但可能做出与 plan intent 不一致的 optional/required 选择。
- **建议改法和验证点**: 为 `ReportDataGapOverride` 添加最小字段表，至少列出 required fields 和类型。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

### 4-未修复-低-ReportEvidenceProjectionContext 缺少 fund_code/report_year

- **位置**: Proposed Dataclasses → `ReportEvidenceProjectionContext` (lines 381-395)
- **问题类型**: 契约缺失
- **当前写法**: Context 字段列表包含 `run_id`, `corpus_id`, `fund_type_slot`, `document_identity_status`, `source_boundary`, `source_failure_category`, `fallback_used`, `review_artifact_refs`, `fact_review_status`, `schema_revision_status`, `quality_context`, `data_gap_overrides`, `score_issue_links`。Bundle id format `reb:{fund_code}:{report_year}:{schema_version}:{run_id}` 需要 `fund_code` 和 `report_year`。
- **反例/失败场景**: Projection 函数签名是 `project_report_evidence_bundle(bundle: StructuredFundDataBundle, context: ReportEvidenceProjectionContext)`。`fund_code` 和 `report_year` 可从 bundle 获取，所以不需要在 context 中重复。但 plan 未显式说明这个设计决策。
- **为什么有问题**: Implementation agent 可能困惑于 bundle id 的 `fund_code`/`report_year` 来源。
- **直接证据**: Bundle id format（lines 404-406）vs context 字段（lines 382-394）。
- **影响**: 极低。从 `StructuredFundDataBundle.fund_code` 和 `StructuredFundDataBundle.report_year` 读取是显而易见的实现路径。
- **建议改法和验证点**: 在 Projection Algorithm 节增加一句说明：`fund_code` 和 `report_year` 从输入 bundle 直接读取，不在 context 中重复。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

## Open Questions

无。所有 findings 均可由 implementation agent 在不重新设计 plan 的情况下解决。

## Residual Risks

| Residual | Risk | Suggested tracking |
|---|---|---|
| `nav_data` excluded | NAV time series facts unavailable to report evidence | Future `nav_data` source-contract slice |
| Manual review is Markdown-backed | Machine validation cannot fully prove reviewed rows | Curated JSON fixture gate |
| `external_official` is metadata only | Future implementer might confuse with network permission | Validation and tests blocking as sole source boundary |
| FOF pure coverage missing | Baseline cannot claim full fund-type coverage | Fund-type taxonomy gate |
| Fallback category unknown for `110020`, `17641`, `1970` | Cannot be scoring-ready | Source reliability gate |
| README sync after code | `AGENTS.md` triggers README update on `fund_agent/fund/` change | Controller includes in implementation gate or records as residual |
| `DerivedCalculation` minimal in first slice | Broad calculation population deferred | Future calculation slice |
| `ReportDataGapOverride` fields partially specified | Implementer may infer from examples | Controller should confirm before code gate |

## Plan Review Conclusion

**PASS_WITH_FINDINGS**

The plan is code-generation-ready for the narrow implementation slice. It correctly chooses file ownership in Agent-layer `fund_agent/fund`, uses frozen slotted dataclasses matching current code patterns, defines comprehensive Literal domains, specifies a clear projection algorithm with explicit params and no `extra_payload`, preserves `FundDocumentRepository` boundaries, and includes 20 targeted tests with negative cases and validation commands.

The 4 findings are low-to-medium severity and can be resolved by the implementation agent without plan redesign:

1. **Medium**: `SourceFailureCategory` adds `data_gap`/`not_applicable` not in S2 accepted contract — implementation agent should drop these or get controller confirmation.
2. **Medium**: Missing explicit test for `accepted_baseline` rejection — implementation agent should add one per the plan's own residual risk note.
3. **Low**: `ReportDataGapOverride` fields underspecified — implementation agent can infer from Step 8 example but should confirm.
4. **Low**: `fund_code`/`report_year` source for bundle id not explicitly stated — obvious from bundle param but worth a sentence.

No blockers found. The plan preserves all architecture boundaries, does not introduce Host/Agent/dayu dependencies, does not change renderer/FQ0-FQ6, and does not promote fixtures.

## Validation Commands

```text
rg -n "SourceFailureCategory|accepted_baseline|ReportDataGapOverride|fund_code|report_year" docs/reviews/release-maintenance-report-evidence-bundle-typed-model-projection-implementation-plan-20260525.md
git diff --check
```

Expected: both pass. This is an artifact-only review gate; no pytest, ruff, or renderer validation required.
