# Plan Review: Report-Quality Validator Dry-Run Evidence Planning

> **Reviewer**: AgentGLM
> **Date**: 2026-05-25
> **Timestamp**: 20260525-142409
> **Target**: `docs/reviews/release-maintenance-report-quality-validator-dry-run-evidence-plan-20260525.md`
> **Gate**: `report-quality validator dry-run evidence planning`
> **Design truth**: `docs/design.md` §5.4 / §5.4.1 / §5.4.2 / §9.1 / §10
> **Control truth**: `docs/implementation-control.md` Startup Packet / Next Entry Point
> **Implementation truth**: `docs/reviews/release-maintenance-report-quality-scoring-jsonl-content-validation-implementation-controller-judgment-20260525.md`
> **Code truth**: `fund_agent/fund/report_quality_validation.py`, `tests/fund/test_report_quality_validation.py`, `fund_agent/fund/report_evidence.py`

## Reviewed Scope

Adversarial review of the dry-run evidence planning artifact against:

1. Planning-only boundary: implementation must only produce `docs/reviews/` Markdown evidence, no source/tests/README/tracked reports/fixtures/product flow changes.
2. Single-bundle JSONL clarity: avoid accidentally validating multi-bundle aggregation.
3. Input purity: no PDF/cache/source helper/FundDocumentRepository, no new fetch, no real annual-report evidence.
4. Dry-run example coverage: valid zero issue, fallback conflict, chapter_summary canonical/no duplicate N/A, N/A semantics, link integrity, scoring_ready precondition, summary/error_code counts/run_id/schema_version/pointers.
5. Acceptance criteria: no overclaim of product integration readiness.
6. Residual completeness: multi-bundle, unknown_upstream, non-scoring-ready chapter_summary/report_level, nav_data, derived calculations, durable baseline, Host/Agent/dayu, fallback recovery, FOF taxonomy.
7. Required validation: rg boundary check specificity and false-positive risk.

## Assumptions Tested

| # | Assumption | Evidence | Verdict |
|---|-----------|----------|---------|
| A1 | Plan is strictly planning-only; future implementation only writes to `docs/reviews/` | Plan §1 explicitly states planning-only status; §8 lists exactly one allowed tracked file; §9 boundary checks verify no source/test changes | **Confirmed** |
| A2 | Single-bundle JSONL is unambiguously scoped | Plan §2.6 "Each JSONL file must contain at most one `record_type='bundle'` record"; §4.4 "confirmation that the JSONL contains exactly one bundle record"; §5.4 "A single-bundle JSONL run proves only artifact consumer behavior for one bundle" | **Confirmed** |
| A3 | Input is synthetic only; no real data access | Plan §2 constructs bundles equivalent to test helper `_valid_bundle_dict()`; §2 "Rejected inputs" lists PDF/cache/source helper/production reports as forbidden; §4 command imports only validator and typed constants | **Confirmed** |
| A4 | Five representative issue categories cover validator consumer contract | Plan §4.5 lists RQV_FALLBACK_CONFLICT, RQV_CHAPTER_SUMMARY_SEMANTICS, RQV_NA_SEMANTICS, RQV_REF_MISSING/RQV_GAP_LINK_INCOMPLETE, RQV_SCORING_READY_PRECONDITION; validator has ~13 distinct error codes (see code lines 53-131 for enum domains, 442-491 for `_validate_bundle_record` call graph) | **Partially confirmed — material gap found (see F1)** |
| A5 | Acceptance criteria do not overclaim product integration | Plan §5 has explicit "Insufficient evidence" section (5 items) stating what passing does NOT prove; §4.6 limits evidence to consumer-contract behavior only | **Confirmed** |
| A6 | Residuals cover all deferred concerns | Plan §7 has 11 items covering multi-bundle, unknown_upstream message, non-scoring-ready chapter_summary/report_level, nav_data, derived calculations, durable baseline, Host/Agent/dayu, fallback recovery, FOF taxonomy, real corpus | **Confirmed** |
| A7 | Boundary rg will not produce false positives | Plan §9.1 rg pattern matches forbidden keywords; plan states "If matches exist only in boundary sections, the evidence must explicitly mark them as non-goals" | **Confirmed, with minor caveat (see OQ1)** |

## Findings

### F1-未修复-中-RQV_FAIL_CLOSED_SOURCE 未纳入 representative issue 覆盖

- **位置**: Plan §4.5 "Representative issue table"
- **问题类型**: 测试缺口
- **当前写法**: Plan §4.5 列出 5 类 representative issues：RQV_FALLBACK_CONFLICT、RQV_CHAPTER_SUMMARY_SEMANTICS、RQV_NA_SEMANTICS、RQV_REF_MISSING/RQV_GAP_LINK_INCOMPLETE、RQV_SCORING_READY_PRECONDITION。RQV_FAIL_CLOSED_SOURCE 未被列出。
- **反例/失败场景**: Implementation agent 构造 malformed bundle 时，选择 `source_failure_category="not_found"` + `fallback_allowed=True` 来触发 RQV_FALLBACK_CONFLICT。这只会覆盖 fallback-eligible 路径。如果 implementation agent 不构造 `source_failure_category="schema_drift"` + `fallback_allowed=True` 的场景，RQV_FAIL_CLOSED_SOURCE 路径将完全不被测试。两条路径在 validator 代码中有不同的行为：fail-closed 路径 `continue` 跳过后续 fallback 检查（代码行 1074），而 fallback conflict 路径继续检查 `unknown_upstream`（代码行 1113）。
- **为什么有问题**: RQV_FAIL_CLOSED_SOURCE 是 implementation review 的关键修复对象。Controller judgment 记录 "GLM F2: fallback/fail-closed cascading duplicate issues — Accepted and fixed"。Dry run 作为 validator consumer contract 的首次端到端证据，如果遗漏该路径，等于没有证明 implementation review 的核心修复在独立执行中仍然正确。
- **直接证据**:
  - Validator `_validate_source_documents()` 代码行 1060-1074: `failure_category in _FAIL_CLOSED_SOURCE_FAILURES` 触发 `RQV_FAIL_CLOSED_SOURCE` 并 `continue`，完全跳过 fallback conflict 检查。
  - Validator 代码行 89-91: `_FAIL_CLOSED_SOURCE_FAILURES = frozenset(("schema_drift", "identity_mismatch", "integrity_error"))`。
  - Controller judgment: "fail-closed source failures short-circuit after `RQV_FAIL_CLOSED_SOURCE`"。
  - Plan §4.5 只列出 RQV_FALLBACK_CONFLICT，未区分 fail-closed 路径。
- **影响**: Dry run 证据不覆盖 fail-closed source 路径，implementation review 的核心修复行为未被端到端证明；后续集成时可能无法区分"没测过"和"已验证正确"。
- **建议改法和验证点**: 在 §4.5 representative issue table 增加 "fail-closed source: RQV_FAIL_CLOSED_SOURCE, blocking, showing that schema_drift/identity_mismatch/integrity_error failures cannot be masked by fallback flags"。Implementation agent 可在 malformed bundle 中添加第二个 source_document 记录，使用 `failure_category="schema_drift"` + `fallback_allowed=True`，或者在 separate in-memory variant 中单独测试。
- **修复风险**: 低。仅需在 issue table 增加一行，不改变 plan 结构、边界或 acceptance criteria。
- **严重程度**: 中。Coverage gap 不会导致 implementation agent 产出错误证据，但会遗漏关键 validator 路径的端到端证明。

### F2-未修复-低-Link integrity "RQV_REF_MISSING or RQV_GAP_LINK_INCOMPLETE" 语义模糊

- **位置**: Plan §4.5 "link integrity" 行
- **问题类型**: 契约缺失
- **当前写法**: "link integrity: RQV_REF_MISSING or RQV_GAP_LINK_INCOMPLETE, with pointer to the bad ref"
- **反例/失败场景**: Implementation agent 构造 malformed bundle 只触发 RQV_REF_MISSING（dangling forward ref），不触发 RQV_GAP_LINK_INCOMPLETE（missing backlink）。这两条代码验证的是 link integrity contract 的不同方向：RQV_REF_MISSING 验证 forward reference 指向存在的记录（代码行 1937-1971），RQV_GAP_LINK_INCOMPLETE 验证 issue→gap→fact 双向回链完整性（代码行 1698-1801）。
- **为什么有问题**: "or" 语义允许 implementation agent 只覆盖一个方向。如果只覆盖 forward ref（RQV_REF_MISSING），backlink 完整性（RQV_GAP_LINK_INCOMPLETE）这一 implementation review 的修复对象（GLM F5-F6: "missing negative tests and file-handle helper issue — Added ... link tests"）可能不被端到端证明。
- **直接证据**:
  - Validator `_validate_ref()` vs `_validate_link_completeness()` 是两个独立函数，验证不同语义。
  - Controller judgment: "GLM F3-F6: missing negative tests"。
  - Plan 使用 "or" 而非 "and"。
- **影响**: 低。Malformed bundle 如果包含 gap/issue/fact 的交叉引用，自然会触发两种 code。但如果 implementation agent 最小化构造，可能只触发一种。
- **建议改法和验证点**: 将 "or" 改为 "and"，明确要求两种 link integrity code 都被覆盖；或在 note 中说明两种 code 测试不同方向，implementation agent 应构造能同时触发两者的 input。
- **修复风险**: 低。
- **严重程度**: 低。Implementation agent 大概率会自然覆盖两者，但 plan 不应留下 "只覆盖一个就够了" 的解读空间。

## Open Questions

### OQ1: rg pattern 中 `fund-analysis` 是否会在 evidence markdown 的 boundary 声明中触发匹配？

Plan §9.1 rg pattern 包含 `fund-analysis`。Evidence markdown 可能在 "non-goal: 未调用 fund-analysis CLI" 这样的 boundary 声明中包含该字符串。Plan 已说明 "If matches exist only in boundary sections, the evidence must explicitly mark them as non-goals"，所以这不会导致 false fail。但建议 implementation agent 在 boundary section 使用引号或 code block 包裹禁止项，使 rg 匹配更容易被 reviewer 区分。

**不需要 plan 修改**。Plan 已有足够的防护措施。

### OQ2: Dry run 是否应该测试 dataclass 输入路径（ReportEvidenceBundle 实例）？

Validator `validate_report_quality_bundle()` 接受 `ReportEvidenceBundle | Mapping[str, object]` 两种输入。Plan §2.1-2.2 使用 dict 构建。测试中 `test_dataclass_bundle_input_is_supported()` 已覆盖 dataclass 路径，但 dry run 不要求覆盖。

**不需要 plan 修改**。Dry run 的目标是 consumer contract 证明，不是输入类型覆盖。Validator 的 25 个 focused tests 已覆盖两种输入路径。

### OQ3: Malformed bundle 能否在一个 `review_status="scoring_ready"` 的 bundle 中同时覆盖 fallback conflict 和 scoring_ready precondition？

可以。如果 bundle 声明 `review_status="scoring_ready"` 且包含 `source_failure_category="not_found"` 的 source_document，validator 会同时输出 RQV_FALLBACK_CONFLICT（fallback 标志不一致）和 RQV_SCORING_READY_PRECONDITION（source_failure_category 不是 "none"）。Plan §2.6 已允许 separate in-memory variants，所以 implementation agent 可以选择将所有 issues 放在一个 bundle 或使用多个 variant。

**不需要 plan 修改**。Plan 已给出足够的灵活性。

## Residual Risks

| Risk | Severity | Tracking destination | Note |
|------|----------|---------------------|------|
| Multi-bundle JSONL aggregation semantics untested | Material | Plan §7.1; control doc Open Residuals | Correctly deferred; future gate |
| `unknown_upstream_failure_category` exact message not asserted | Minor | Plan §7.2; controller judgment deferred residual | Correctly deferred |
| Non-scoring-ready `chapter_summary/report_level` blocking policy | Minor | Plan §7.3-7.4; controller judgment deferred residual | Current stricter behavior is coherent |
| `nav_data` mapping | Material | Control doc Open Residuals; plan §7.5 | Correctly deferred to future nav_data source-contract slice |
| Derived calculation population | Material | Plan §7.6; control doc Open Residuals | Correctly deferred |
| Durable baseline / fixture promotion | Material | Plan §7.7; control doc Current Non-Goals | Correctly deferred |
| Host/Agent/dayu runtime | Material | Control doc Open Residuals; plan §7.8 | Correctly deferred; requires independent gate |
| Fallback upstream failure category recovery | Material | Control doc Open Residuals; plan §7.9 | Correctly deferred |
| FOF taxonomy and QDII-FOF precedence | Material | Control doc Open Residuals; plan §7.10 | Correctly deferred |
| Real corpus coverage | Material | Plan §7.11 | Correctly deferred |

All residual risks are explicitly tracked in the plan and/or the control document. No risk is silently dropped.

## Architecture Boundary Review

Plan 不引入架构边界变更。Validator 是已接受的 Agent 层 Fund 领域能力模块。Dry run 只消费 validator 的公开 API（`validate_report_quality_bundle` / `validate_report_quality_jsonl`），不触及 UI/Service/Host/Agent/renderer/FQ0-FQ6/quality_gate 任何边界。四层边界 `UI -> Service -> Host -> Agent` 不受影响。

## Best-Practice Review

- Synthetic input 先于真实数据：符合 §5.4 "首个实现切片应定义小样本基准集和报告质量评分 schema" 的设计原则。
- Explicit non-goals 和 insufficiency 声明：Plan §1 和 §5 明确区分"能证明什么"和"不能证明什么"，防止 overclaim。
- Scratch files 限制在 `/tmp`：符合 control doc Current Non-Goals "Do not promote local scoring, writing, or data-source run outputs into tracked fixtures"。
- Boundary rg 检查：Plan §9.1 的 rg pattern 覆盖了所有关键边界关键词。

## Optimal-Solution Review

Dry run 是证明 "validator 可以被作为 consumer contract 消费" 的最简单路径。不需要更复杂的方案（如集成到 Service/CLI 或使用真实年报数据），也不需要更简单的方案（如只读代码不做端到端验证）。Plan 的 scope 是合理的。

## Overengineering Review

Plan 对于 "运行 validator 两次并记录结果" 这个目标来说足够详细但不冗余。考虑到项目的 gate-based flow 和 adversarial review 文化，此细节级别是必要的：implementation agent 需要明确的边界约束来避免意外越界。

## Overcoupling Review

Plan 不引入任何耦合。Dry run 是独立的、一次性的验证活动，不与任何 product flow 组件建立持久关系。

## Reviewer Self-Check

- [x] Reviewed target, scope, source of truth and assumptions tested are documented
- [x] Findings are evidence-based, adversarial, actionable, and not style/nit/speculation
- [x] Open questions, residual risks, tracking destinations are separated from findings
- [x] Conclusion is one of: pass, pass-with-risks, fail
- [x] Output path uses machine-generated timestamp and matches artifact format

## Conclusion

**PASS_WITH_FINDINGS**

Plan 是严格 planning-only 的，single-bundle JSONL 口径明确，输入不接触 PDF/cache/source helper/FundDocumentRepository，acceptance criteria 不 overclaim 产品集成，residuals 完整覆盖所有延迟关注点。两个 findings 均不构成 blocker：

1. **Material (F1)**: RQV_FAIL_CLOSED_SOURCE 未纳入 representative issue table，遗漏了 implementation review 的关键修复路径。建议在 §4.5 增加一行。
2. **Minor (F2)**: Link integrity 使用 "or" 语义，可能被解读为只覆盖一个方向即足够。建议改为 "and" 或加注说明。

Plan 在修正 F1 后可安全交给 implementation agent 执行。
