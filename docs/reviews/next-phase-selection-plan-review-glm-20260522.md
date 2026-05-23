# Next Phase Selection Plan Review（GLM，2026-05-22）

## Reviewed Target

- **Target**: `docs/reviews/next-phase-selection-20260522.md`
- **Current gate**: `maintenance-ready` → `next phase selection`
- **Review scope**: adversarially verify whether selected next gate P13-S1 tracking-error / index-data source contract plan-review is the smallest best-practice next phase and whether the selection artifact is safe to accept.
- **Truth sources**: `docs/design.md`, `docs/implementation-control.md`, `docs/reviews/post-p12-release-maintenance-closeout-20260522.md`, `AGENTS.md`
- **Focus areas**: architecture boundaries, scope, sequencing, allowed/disallowed files, RR-13 handling, repo-audit exclusion, Dayu/LLM non-goals, P13-S1 planning-only concreteness

## Assumptions Tested

| # | Assumption | Evidence | Verdict |
|---|-----------|----------|---------|
| A1 | Tracking-error/index-data is the highest-value product gap after P12 | `renderer.py:569-592` hardcodes `数据不足` for tracking error regardless of fund type; `preferred_lens` for `index_fund` and `enhanced_index` both prioritize tracking error in chapters 0/1/2/5/6/7; `StructuredFundDataBundle` has zero tracking-error or index fields; `FundAnalysisService` line 377 passes `tracking_error` from contract override, not extraction | **Confirmed** — user-visible gap with direct preferred_lens support |
| A2 | Planning-only is the right first gate, not direct implementation | Tracking-error currently enters via `ResolvedAnalyzeContract.tracking_error` (service-level override), not via Capability extraction; extraction vs calculation decision is unresolved; new external index series adapter scope is open-ended; source contract must be designed before code | **Confirmed** — architectural questions require design-first |
| A3 | E1-E3 / Evidence Confirm should be deferred | `design.md` Section 5 marks E1/E2/E3 as v2; audit architecture would introduce LLM semantics, repair contracts, and new audit contracts; scope is significantly higher than data extraction planning | **Confirmed** |
| A4 | Repo-hygiene can be deferred | D-1/D-8-C5/C-9 are maintainability improvements; no product feature is blocked by repo confusion; P13 tracking-error removal has higher user-facing value | **Confirmed** |
| A5 | RR-13 is not agent-implementable | Duplicate `016492` requires human truth about which CSV row is correct; auto-fix would corrupt source data; stop condition in Section 12 correctly blocks if P13 needs selected-pool identity | **Confirmed** |
| A6 | All document access can stay within `FundDocumentRepository` | Current repository has single public method `load_annual_report()`; Service/UI/renderer never bypass it (verified: no PDF/cache/file access in `services/` or `ui/`); `AGENTS.md` hard constraint confirms this | **Confirmed with caveat** — see Finding 1 |
| A7 | P13-S1 planning-only scope is concrete enough for a planning agent | Selection artifact specifies 5 concrete questions, 7 implementation slices with boundary rules, 9 review rejection criteria, exact allowed/disallowed files, and validation commands | **Confirmed** |

## Special Lens Review

### Architecture Boundary Review

Layering is preserved: the selection correctly requires all document access through `FundDocumentRepository`, keeps Service/UI out of source internals, and confines tracking-error/index-data work to Fund Capability. No boundary leakage found in the selection artifact.

Dependency direction is correct: the selection does not introduce Service → Capability internals, UI → document sources, or cross-layer coupling.

### Best-Practice Review

Planning before implementation for a data contract change is standard practice. The selection correctly identifies that the hardest design decision (extract disclosed tracking error vs calculate from time series) must be resolved before code generation. This aligns with the project's established gateflow pattern (P8-S3 source fallback taxonomy, P9-S1 product contract, P12-S1 ITEM_RULE compliance all planned before implementation).

### Optimal-Solution Review

Among the four candidates, P13-S1 planning-only is the smallest safe move. A smaller alternative (e.g., "just add a tracking-error field to the bundle") would skip the source contract design and risk the same extraction-vs-calculation ambiguity that the planning gate is designed to resolve. No credible simpler alternative exists.

### Overengineering Review

The selection artifact itself is not overengineered. It produces one planning document with no code changes. The 7 implementation slices are listed as required planning outputs for P13-S1, not as implementation scope for the selection gate. Scope is appropriately bounded.

### Overcoupling Review

The selection correctly isolates P13 from E1-E3, repo-hygiene, and RR-13. It does not bind tracking-error extraction to audit architecture, Service contract changes, or UI modifications. The coupling surface is minimal: only Fund Capability data models, `FundDocumentRepository`, and renderer consumption of structured data.

## Findings

### 001-unfixed-[中]-P13-S1 需明确 tracking_error 从 service-level override 迁移到 Capability extraction 的边界决策

- **位置**: Section 5 point 2（source path）、point 3（structured contract changes）、Section 8 "Extraction/calculation" slice
- **问题类型**: 架构边界
- **当前写法**: Section 5 point 2 列出三个候选权威来源路径（年报/招募说明书 via `FundDocumentRepository`、现有 NAV adapter、新外部指数序列 adapter）；Section 8 "Extraction/calculation" slice 要求决定是提取披露值还是从时间序列计算
- **反例/失败场景**: 当前 `FundAnalysisService` line 377 通过 `resolved_contract.tracking_error`（service-level override）传入 tracking error。若 P13-S1 plan 只设计新的 Capability extraction 路径但不明确关闭旧的 service override 路径，implementation agent 可能产生两条并行入口，导致 developer override 与 extraction 数据冲突时无法裁决优先级
- **为什么有问题**: 当前 tracking_error 存在两个概念路径（service override vs 未来 extraction），selection artifact 暗示 extraction 路径但不显式关闭 override 路径。`design.md` Section 4.4 否决项表格要求"跟踪误差过大 > 2%"为否决条件，但数据来源未绑定到 extraction。若两条路径并存，否决项检查可能消费不一致的数据
- **直接证据**: `fund_agent/services/fund_analysis_service.py:377` — `tracking_error=resolved_contract.tracking_error`；`fund_agent/fund/analysis/risk_check.py:181` — `run_risk_checks` 接收外部 `tracking_error` 参数；`renderer.py:569-592` — 跟踪误差渲染硬编码为"数据不足"
- **影响**: P13-S1 plan 可能遗漏 override-to-extraction 迁移策略，implementation agent 产生双路径并存
- **建议改法和验证点**: selection artifact 本身不需要修改，但 P13-S1 plan review 应将此列为必答问题：tracking_error 的权威来源是 Capability extraction 还是 service override？若迁移到 extraction，`ResolvedAnalyzeContract.tracking_error` 和 `run_risk_checks` 的参数来源如何变更？developer override 是否保留？
- **修复风险**: 低 — 这是 P13-S1 plan 的设计问题，不是 selection artifact 的缺陷
- **严重程度**: 中 — 若 P13-S1 plan 未关闭此问题，implementation 可能产生架构分歧

### 002-unfixed-[中]-外部指数序列 adapter 范围未上界约束

- **位置**: Section 5 point 2 第三条（"any new external index series adapter only after source, cache, identity, and failure taxonomy are designed"）、Section 8 "Source contract" slice
- **问题类型**: 范围漂移
- **当前写法**: 允许设计新外部指数序列 adapter，但要求先完成 source/identity/failure taxonomy 设计
- **反例/失败场景**: 若年报中不披露跟踪误差（仅披露跟踪误差限额），P13 需要从外部指数序列计算跟踪误差。这需要：新的外部数据 adapter（指数净值序列获取）、新的 cache/provenance 模型、新的 identity 校验、新的 failure taxonomy。P13-S1 plan 可能因此膨胀为"设计完整的外部指数数据基础设施"，而非"为跟踪误差提供最小数据来源"
- **为什么有问题**: 当前 `FundDocumentRepository` 只处理年报 PDF；外部指数序列是全新的数据类别，其 adapter 设计可能等于一个独立 phase 的工作量。selection artifact 的"after designed"条件是必要但不充分的约束
- **直接证据**: `FundDocumentRepository` 只有 `load_annual_report()` 一个公共方法（`repository.py:290`）；NAV adapter `FundNavDataAdapter` 只提供基金净值，不提供指数净值；`design.md` Section 6.1 数据源表格没有指数净值序列来源
- **影响**: P13-S1 plan 范围失控，规划 agent 可能产出过于复杂的 adapter 设计
- **建议改法和验证点**: selection artifact 不需修改，但 P13-S1 plan review 应检查：(1) plan 是否将"年报已披露跟踪误差"和"需要从外部计算"分为两个独立 slice；(2) 外部 adapter 设计是否可推迟到 P13-S2 而不阻塞年报提取路径
- **修复风险**: 低 — 这是 plan review 的检查项，不影响 selection 本身
- **严重程度**: 中 — 范围膨胀风险是 planning gate 的典型挑战

### 003-unfixed-[低]-纯指数基金测试 fixture 缺失影响 P13-S1 plan 的验证设计

- **位置**: Section 8 "Tests" slice（"deterministic fixture for index fund"）
- **当前写法**: P13-S1 plan 要求包含指数基金和增强指数基金的确定性 fixture
- **反例/失败场景**: 当前 `tests/fixtures/fund/extractors/profile/` 只有一个增强指数 profile fixture（`index_enhanced_profile.txt`），没有纯指数基金 fixture。P13-S1 plan 需要设计 fixture 但可能低估创建难度（需要真实年报 §1/§2/§3 文本来模拟指数基金身份和跟踪误差披露）
- **为什么有问题**: 这是已知的 fixture gap，不是 selection 的错误。但 P13-S1 plan review 应确认 fixture 设计是否需要真实的年报样本（需要网络下载）或可以用人工构造的文本 fixture
- **直接证据**: `tests/fixtures/fund/extractors/profile/` 目录内容；`tests/fund/extractors/test_profile.py` 覆盖主动/增强指数/债券但无纯 `index_fund` fixture
- **影响**: 低 — fixture 创建是 implementation slice 的标准工作
- **建议改法和验证点**: 无需修改 selection artifact。P13-S1 plan 应明确 fixture 策略：是使用真实样本年报还是人工构造文本
- **修复风险**: 低
- **严重程度**: 低

## Open Questions

无阻断性开放问题。以下问题应由 P13-S1 plan 回答而非在此 selection gate 解决：

1. **tracking_error 权威来源裁决**：Capability extraction 还是 service override？developer override 是否保留？（见 Finding 001）
2. **外部指数序列 adapter 的分阶段策略**：是否可以将"年报已披露"路径作为 P13-S2 首个 implementation slice，而将"外部计算"路径推迟到后续 slice？（见 Finding 002）
3. **index_fund fixture 策略**：使用真实样本还是人工构造？（见 Finding 003）

## Residual Risks

| Risk | Severity | Tracking destination | Notes |
|------|----------|---------------------|-------|
| tracking_error 双路径并存 | 中 | P13-S1 plan review | plan 必须显式关闭 override-to-extraction 迁移策略 |
| 外部 adapter 范围膨胀 | 中 | P13-S1 plan review | plan 应将外部 adapter 作为独立可选 slice，不阻塞年报提取路径 |
| 指数基金 fixture 缺失 | 低 | P13-S1 implementation | 标准实现工作，无架构风险 |

## Architecture Boundary Verification

| Boundary | Selection compliance | Evidence |
|----------|---------------------|----------|
| UI → Service only | ✅ No UI changes proposed | Selection Section 6 non-goals; Section 7 disallowed files |
| Service → Capability only | ✅ No Service source access | Selection non-goals prohibit direct document access |
| FundDocumentRepository as sole document entry | ✅ Required in Section 5, 8, 9 | Design.md Section 2.2; AGENTS.md hard constraint |
| No Dayu runtime | ✅ Explicit non-goal | Section 6; design.md Section 8; AGENTS.md hard constraint |
| No LLM writing / Evidence Confirm | ✅ Explicit non-goal | Section 6; design.md Section 5 |
| No E1-E3 in P13 | ✅ Explicit non-goal | Section 6; Section 9 rejection criteria |
| No extra_payload | ✅ Explicit non-goal | Section 6; AGENTS.md hard constraint |
| No repo-audit modification | ✅ Explicitly excluded | Section 6; Section 7 disallowed files; Section 12 stop conditions |
| RR-13 human-owned | ✅ Preserved with stop condition | Section 6 non-goal; Section 11 residual owner; Section 12 stop condition |

## Sequencing Verification

| Check | Result |
|-------|--------|
| P13-S1 is planning-only before implementation | ✅ Section 2, 5, 8 clearly state planning/design only |
| Planning before any source/test change | ✅ Section 7 restricts P13-S1 to `docs/reviews/` only |
| Implementation files re-declared by accepted plan | ✅ Section 7 last paragraph |
| P12 remains closed | ✅ No P12 rework proposed |
| Repo-audit not touched | ✅ Section 6, 7, 10, 11, 12 all exclude it |

## Plan Review Conclusion

**PASS**

Selection artifact `docs/reviews/next-phase-selection-20260522.md` is safe to accept. P13-S1 tracking-error / index-data source contract plan-review is the smallest best-practice next phase:

1. **Highest product value**: removes user-visible `数据不足` placeholder for index/enhanced-index fund reports, directly supported by `preferred_lens` across 6 chapters.
2. **Lowest risk entry**: planning-only gate produces no code, no source changes, no design.md/control.md modifications.
3. **Correct architecture boundaries**: all document access stays within `FundDocumentRepository`; Service/UI/renderer remain consumers; no Dayu/LLM/E1-E3 leakage.
4. **Correct residual handling**: RR-13 human-owned with stop condition; repo-audit excluded; E1-E3 deferred; repo-hygiene deferred.
5. **Concrete enough**: 5 questions, 7 slices with boundary rules, 9 rejection criteria, and exact file permissions provide sufficient structure for a planning agent.

Three findings (2 medium, 1 low) are non-blocking for the selection gate and should be addressed during P13-S1 plan review, not here.
