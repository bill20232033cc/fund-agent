# Fact-Evidence Contract S2 Bundle Candidate Plan — Independent Review (AgentDS)

> Date: 2026-05-25
> Reviewer: AgentDS (planreview specialist)
> Gate: `fact-evidence-contract S2 bundle candidate planning`
> Artifact under review: `docs/reviews/release-maintenance-fact-evidence-contract-s2-bundle-candidate-plan-20260525.md`
> Conclusion: **PASS_WITH_FINDINGS**

## Step Self-Check

- Role: independent plan reviewer only. No file edits, no commits, no controller judgment.
- Truth sources read: `AGENTS.md`; `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point / Open Residuals; `docs/design.md` §2.1, §5.4, §5.4.1, §5.4.2, §5.4.3, §6.1, §7.2, §7.3, §7.4, §11.5, §12; S1 score-schema controller judgment; S1 dry-run controller judgment.
- Code facts verified: `fund_agent/fund/extractors/models.py` (EvidenceAnchor, ExtractedField, ExtractionMode, EvidenceSourceKind); `fund_agent/fund/data_extractor.py` (StructuredFundDataBundle, FundDataExtractor); `fund_agent/fund/documents/repository.py` (FundDocumentRepository).
- Scope: adversarial plan review only. No implementation, no code changes, no fixture promotion.

## Reviewed Target and Scope

The plan proposes a typed `ReportEvidenceBundle` contract model that wraps `StructuredFundDataBundle` for future report-quality scoring and chapter writing. Scope is planning only — no code implementation, no renderer/FQ0-FQ6 changes, no Host/Agent packages, no fixture promotion.

## Assumptions Tested

| # | Assumption | Verdict |
|---|-----------|--------|
| A1 | Wrapping `StructuredFundDataBundle` preserves existing extractor investment and avoids parallel extraction paths | Supported. Current bundle carries all field groups the plan lists; single extraction path aligns with `AGENTS.md` first principles and `FundDocumentRepository` boundary. |
| A2 | `ReportEvidenceBundle` belongs in `fund_agent/fund` (Agent layer) | Supported. AGENTS.md assigns "理解基金类型、财报章节、投资规则" and "CHAPTER_CONTRACT 解析 / preferred_lens 应用" to `fund_agent/fund`. |
| A3 | No Host/Agent runtime is required for the bundle model | Supported. The plan's stop condition #1 correctly gates Host/Agent work; the bundle is a data contract, not a runtime. |
| A4 | `FundDocumentRepository` is the only annual-report access path | Supported. Plan explicitly says "no direct PDF/cache/source adapter access" and "No direct PDF/cache/source/download helper access outside `FundDocumentRepository`." |
| A5 | Chapter-contract wording constraints precede extraction work | Supported. The turnover stability rule table and controller judgment are correctly reflected. |
| A6 | Identifier conventions are deterministic and avoid ad hoc names | Partially supported. Formats are specified with rules and examples, but hash stability, collision handling, and the mapping from S1 dry-run ids are not fully specified (see Finding 4). |
| A7 | `extra_payload` is excluded from all new models | Supported. Plan explicitly forbids it; Slice 1 validation includes `rg` check. |
| A8 | Existing `EvidenceAnchor` fields can be projected without loss | Supported. Current `EvidenceAnchor` has `source_kind`, `document_year`, `section_id`, `page_number`, `table_id`, `row_locator`, `note` — all preserved in the plan's anchor table. |

## Findings

### F-1-未修复-中-classified_fund_type 值域未明确枚举

- **位置**: Contract Candidate → Top-Level Fields → `classified_fund_type`
- **问题类型**: 不可直接实施
- **当前写法**: "current fund type domain plus `unknown`"
- **反例/失败场景**: 实施 Agent 需要知道枚举的具体值才能定义 Python `Literal` 类型。当前 `FundType = Literal["index_fund", "active_fund", "bond_fund", "enhanced_index", "qdii_fund", "fof_fund"]` 不含 `unknown`。实施 Agent 面临歧义：是在现有 `FundType` 基础上加 `unknown`，还是定义新的 bundle 专用类型？`StructuredFundDataBundle` 本身不直接携带 `classified_fund_type` 字段（它在 `basic_identity.value["classified_fund_type"]` 内部），投影逻辑需要明确如何从嵌套 dict 中提取并归一化。
- **为什么有问题**: 基金类型是 `preferred_lens` 应用的前置条件（AGENTS.md: "基金类型判断优先于通用分析"），值域不明确会导致 lens 选择错误或类型 slot 匹配失效。
- **直接证据**: `fund_agent/fund/fund_type.py` 定义 `FundType = Literal["index_fund", "active_fund", "bond_fund", "enhanced_index", "qdii_fund", "fof_fund"]`；`StructuredFundDataBundle` 无 `classified_fund_type` 顶层字段，该值在 `basic_identity.value` dict 内部。
- **影响**: 实施 Agent 跑偏 / 后续返工
- **建议改法和验证点**: 在 plan 中明确 `classified_fund_type` 的完整值域（建议直接复用 `FundType` 字面量并加 `"unknown"`），并说明从 `StructuredFundDataBundle.basic_identity.value["classified_fund_type"]` 的投影规则（含缺失/非法值的归一化策略）。
- **修复风险（低）**:
- **严重程度（中）**:

### F-2-未修复-中-review_status 派生算法缺少优先级与冲突裁决

- **位置**: Contract Candidate → Review Status Derivation
- **问题类型**: 状态机漏洞
- **当前写法**: 9 种 bundle status 各有一条 derivation candidate 描述；"Minimum invalid combinations" 列出 6 条规则。
- **反例/失败场景**: 一个 bundle 同时满足多个 derivation candidate 条件时（例如 `document_identity_status=verified_annual_report` 满足 `repository_verified`，但同时 `facts` 中某字段 `source_boundary=unknown` 满足 `rejected` 的部分条件），实施 Agent 无法确定最终状态。当前的 derivation candidate 表格是平行枚举，没有优先级或裁决顺序。
- **为什么有问题**: 缺少确定性派生算法意味着两个实施者可能写出不同的状态机，导致下游 scoring 消费不一致。
- **直接证据**: Plan 中 derivation candidate 表格（行 186–196）未标注优先级；invalid combinations 只覆盖 `scoring_ready` 和 `accepted_baseline` 的阻断条件，未覆盖 `rejected` / `deferred` / `candidate` 之间的冲突裁决。
- **影响**: 状态不一致 / review 不可验收
- **建议改法和验证点**: 添加优先级规则（建议顺序：`rejected` > `expired` > `deferred` > `scoring_ready` > `fact_prefill_reviewed` > `fact_prefill_generated` > `repository_verified` > `candidate`），或明确说明派生是最高严重级别优先。
- **修复风险（低）**:
- **严重程度（中）**:

### F-3-未修复-中-nav_data 到 facts 的投影规则存在结构断层

- **位置**: Contract Candidate → Facts → "Initial projection should cover current `StructuredFundDataBundle` fields: … `nav_data`"
- **问题类型**: 不可直接实施
- **当前写法**: 要求投影覆盖 `nav_data`，但 `facts` 表格定义的字段（`fact_id`、`category`、`field_path`、`value`、`unit` 等）是为离散 `ExtractedField` 设计的。
- **反例/失败场景**: `StructuredFundDataBundle.nav_data` 的类型是 `NavDataResult`（净值时间序列），不是 `ExtractedField[T]`。它没有 `extraction_mode`、没有 `anchors`（tuple of `EvidenceAnchor`），也不是键值对。实施 Agent 拿到 `nav_data` 后不知道如何把它拆成 `fact:valuation.nav_series` 之类的事实记录，也不知道时间序列的 `period`、`unit`、`source_anchor_ids` 该如何填写。
- **为什么有问题**: Plan 声称投影覆盖所有当前字段组，但 `nav_data` 与 `facts` 模型之间存在结构不兼容，实施 Agent 必须自行设计桥接逻辑，这违反了 "code-generation-ready" 目标。
- **直接证据**: `fund_agent/fund/data_extractor.py:110` — `nav_data: NavDataResult`（非 `ExtractedField`）；`fund_agent/fund/data/nav_data.py` 中 `NavDataResult` 是时间序列结果类型。Plan 的 facts 表格要求 `source_anchor_ids`、`extraction_mode` 等字段，`nav_data` 不携带这些。
- **影响**: 实施 Agent 跑偏 / 后续返工
- **建议改法和验证点**: 明确 `nav_data` 的投影策略，二选一：(a) 将 `nav_data` 排除在初始 facts 投影之外，标注为后续 slice；(b) 定义 `nav_data` 到 facts 的具体映射规则（如每条净值记录映射为一个 `fact:valuation.nav` 记录，`extraction_mode=derived`，`source_anchor_ids` 指向外部 API 锚点）。
- **修复风险（低）**:
- **严重程度（中）**:

### F-4-未修复-低-anchor_id 的 locator_hash 稳定性未定义

- **位置**: Identifier Conventions → Anchor IDs → `locator_hash`
- **问题类型**: 契约缺失
- **当前写法**: "`locator_hash` is a short deterministic hash of `page_number`, `table_id`, `row_locator`, and normalized note/ref."
- **反例/失败场景**: "short deterministic hash" 没有指定哈希算法（md5? sha256 前 6 位?）、输入归一化规则（`page_number=None` 怎么哈希？`row_locator` 空格/全角半角怎么归一化？）、截断长度。不同实现对同一锚点会生成不同 id，破坏跨 run 稳定性。
- **为什么有问题**: Anchor id 的稳定性是 `scoring_ready` 和跨 run 比对的前提。如果 hash 不稳定，同一份年报的同一位置在不同 run 中可能产生不同 anchor_id，scoring 无法关联。
- **直接证据**: Plan 行 224: "`locator_hash` is a short deterministic hash" — 无算法、无归一化规则、无截断约定。
- **影响**: 实施 Agent 跑偏 / 后续返工
- **建议改法和验证点**: 指定哈希算法（建议 sha256 前 8 位 hex），定义输入归一化规则（None → 空字符串，strip，Unicode NFC 归一化），要求 Slice 2 测试验证同一输入产生同一 hash。
- **修复风险（低）**:
- **严重程度（低）**:

### F-5-未修复-低-source_boundary=external_official 与 FundDocumentRepository 边界存在未解释张力

- **位置**: Contract Candidate → Source Documents → `source_boundary` enum
- **问题类型**: 架构边界
- **当前写法**: `source_boundary` 枚举包含 `external_official`；但 plan 同时声明 "No direct PDF/cache/source/download helper access outside `FundDocumentRepository`."
- **反例/失败场景**: 如果 `external_official` 代表官方指数公司、交易所或监管披露来源，这些数据不是通过 `FundDocumentRepository`（当前只支持年报 PDF）获取的。实施 Agent 不清楚 `external_official` 来源的数据应该从哪里获取、通过什么接口、受什么边界约束。
- **为什么有问题**: `AGENTS.md` 和 `docs/design.md` 的 `FundDocumentRepository` 边界当前覆盖年报 PDF 存取。`external_official` 暗示了新的数据获取路径，但 plan 没有说明这个路径是否已存在、是否需要新建、以及它是否也必须经过某一 Repository 接口。
- **直接证据**: `docs/design.md` §5.4.2 证据层级表包含 "官方指数公司、交易所、监管披露" 作为合法来源；`FundDocumentRepository` 当前只实现年报加载。Plan 在 source_documents 的 `source_boundary` 中加入 `external_official` 但未说明获取接口。
- **影响**: 实施 Agent 跑偏（可能直接调用外部 API）/ 风险后移
- **建议改法和验证点**: 明确 `external_official` 在 S2 范围内是否可用；如果不可用，标注为 future 枚举值（类似 anchor 的 `official_index` / `regulatory`）；如果可用，说明获取接口的边界约束（是否也需要 Repository 模式）。
- **修复风险（低）**:
- **严重程度（低）**:

### F-6-未修复-低-preferred_lens 字段的格式与派生逻辑未指定

- **位置**: Contract Candidate → Top-Level Fields → `preferred_lens`
- **问题类型**: 不可直接实施
- **当前写法**: "configured lens id / fund type lens"；"Derived after fund type classification; not a free string."
- **反例/失败场景**: 实施 Agent 不知道 `preferred_lens` 是存储现有的 `TemplateLensRule` 对象、lens key 字符串（如 `"active_fund_lens"`）、还是 `LensApplicationPlan` 的引用。当前代码中 `preferred_lens` 通过 `resolve_preferred_lens(manifest, fund_type)` 从 manifest 解析，返回 `TemplateLensRule`。bundle 中应该存什么？
- **为什么有问题**: `preferred_lens` 是章节写作和审计的关键输入（`docs/design.md` §3.4），格式不明确会导致 bundle 消费者无法正确应用 lens。
- **直接证据**: `fund_agent/fund/template/contracts.py` 中 `resolve_preferred_lens()` 返回 `TemplateLensRule`；plan 未说明 bundle 中的 `preferred_lens` 与该函数的关系。
- **影响**: 实施 Agent 跑偏
- **建议改法和验证点**: 明确 `preferred_lens` 的值格式（建议为 lens key 字符串，可从 `TemplateLensRule` 派生），或说明它是 `TemplateLensRule` 的序列化投影。
- **修复风险（低）**:
- **严重程度（低）**:

### F-7-未修复-低-实施 Slice 的验证描述不足以防止假通过

- **位置**: Future Implementation Slices → 各 Slice 的 Validation 小节
- **问题类型**: 测试缺口
- **当前写法**: Slice 2 验证包括 "Tests with fake bundles for each current field group." Slice 3 验证包括 "Parameterized tests for each invalid combination."
- **反例/失败场景**: "Tests with fake bundles for each current field group" 没有说明 fake bundle 的最小构造要求。如果 fake bundle 中 `turnover_rate` 使用了 `extraction_mode=missing` 但 `value` 非 None，投影测试可能通过但违反了字段语义约束。没有具体的边界值、负面用例或回归触发条件。
- **为什么有问题**: Plan 的验证描述是方向性的而非规范性的。实施 Agent 可能写出只覆盖 happy path 的测试，遗漏 extraction_mode 与 value 一致性、anchor 与 source_document 关联完整性、枚举拒绝等关键边界。
- **直接证据**: Plan 行 352–358 (Slice 2 验证)，行 367–371 (Slice 3 验证) — 均为高层描述。
- **影响**: review 不可验收 / 风险后移
- **建议改法和验证点**: 不要求穷举测试用例，但建议为每个 slice 补充 2-3 个具体的负面测试场景（如 "projection of `turnover_rate` with `extraction_mode=missing` and `value=None` must produce a `data_gap`, not a fact with null value"）。
- **修复风险（低）**:
- **严重程度（低）**:

### F-8-未修复-低-corpus_id 格式与 S0 证据链接未指定

- **位置**: Contract Candidate → Top-Level Fields → `corpus_id`
- **问题类型**: 契约缺失
- **当前写法**: "S0/S1 corpus id or `ad_hoc`"；"Required for baseline scoring; explicit field, not `extra_payload`."
- **反例/失败场景**: 实施 Agent 不知道 `corpus_id` 应该用什么格式（例如 `s0-corpus-20260525`？`corpus:v1:active_index_enhanced_bond_qdii`？）。也不清楚它如何关联到 S0 corpus-selection evidence artifact。未来 scoring 需要根据 `corpus_id` 查找对应的 baseline corpus 定义，但 plan 没有说明这个查找机制。
- **为什么有问题**: `corpus_id` 是 baseline scoring 的前置条件；格式不明确会导致 scoring 无法确定该 bundle 适用哪个 baseline。
- **直接证据**: Plan 行 59: "S0/S1 corpus id or `ad_hoc`" — 无格式、无链接规则。S0 evidence artifact 路径为 `docs/reviews/release-maintenance-report-quality-baseline-s0-corpus-selection-evidence-20260525.md`，plan 未引用。
- **影响**: 实施 Agent 跑偏 / 后续返工
- **建议改法和验证点**: 建议 `corpus_id` 使用 `corpus:{corpus_name}:{version}` 格式（对齐其他 id 的命名空间前缀约定），并说明在 S2 范围内 `corpus_id` 可以是 `ad_hoc`（因为 durable baseline 尚未接受）。
- **修复风险（低）**:
- **严重程度（低）**:

## Architecture Boundary Review

| Check | Result |
|---|---|
| Layering: bundle in Agent-layer `fund_agent/fund` | Correct. Per `AGENTS.md`, fund type knowledge, CHAPTER_CONTRACT, preferred_lens belong in `fund_agent/fund`. |
| Dependency direction: bundle consumes `StructuredFundDataBundle`, not vice versa | Correct. Projection adapter reads from existing bundle without modifying it. |
| `FundDocumentRepository` boundary | Preserved. Source documents describe identity/fallback metadata, not file paths. |
| No `extra_payload` | Explicitly forbidden; Slice 1 includes `rg` validation for it. |
| No Host/Agent runtime | Correct. Stop condition #1 gates this. |
| `external_official` boundary unclear | Flagged as Finding 5. |

## Overengineering Review

The plan is appropriately scoped for a contract definition. No significant overengineering detected:

- The `derived_calculations` table is detailed but justified: P2 calculations (R=A+B-C, cost estimate, pressure test) already exist and need auditable input/output records.
- The `quality_context` table is lightweight (6 fields) and observational only.
- The identifier convention with namespace prefixes (`fact:`, `anchor:`, `gap:`, `calc:`, `issue:`) is a reasonable normalization, not overengineering.

**Minor note**: `degradation_text` on `DerivedCalculation` (行 126) and `required_report_wording` on `DataGap` (行 164) serve similar purposes (wording constraints when data is missing). The plan doesn't clarify whether these are redundant or serve distinct roles. Not a finding — just a note for the implementation gate to reconcile.

## Overcoupling Review

No material overcoupling detected:

- The bundle naturally aggregates facts, anchors, gaps, calculations, quality context, and score links because report-quality scoring needs all of them. This is cohesion, not coupling.
- The projection adapter pattern (separate function, not embedded in the bundle constructor) keeps `StructuredFundDataBundle` and `ReportEvidenceBundle` independently evolvable.
- Score issue links use id references, not object references — this is the right level of coupling.

## Stop Conditions Review

The 9 stop conditions (行 419–429) are comprehensive and well-aligned with `AGENTS.md` and `docs/design.md` constraints. They cover:

- Host/Agent runtime creation (stop #1) — maps to `AGENTS.md` Dayu dependency discipline
- Renderer/FQ0-FQ6 changes (stop #2) — maps to current non-goals
- Parallel extraction (stop #3) — maps to first principles
- Direct PDF/cache access (stop #4) — maps to `FundDocumentRepository` boundary
- `extra_payload` (stop #5) — maps to explicit parameter rule
- Fallback masking (stop #6, #7) — maps to fail-closed fallback policy
- Turnover extraction without contract (stop #8) — maps to controller judgment
- Premature fixture promotion (stop #9) — maps to curated-fixture gate constraint

## Open Questions

1. Should `ReportEvidenceBundle` be `frozen=True` (like `StructuredFundDataBundle`) or mutable? The plan doesn't specify. Mutable bundles risk inconsistent review status derivation.
2. How does `fund_type_slot` interact with `classified_fund_type` when they disagree? The plan mentions `type_slot_membership_status` in invalid combinations but doesn't define the status enum or its derivation.
3. The plan proposes `chapter_ids` from `chapter_0` to `chapter_7` for data gaps (行 160). When the future 0–10 chapter mapping is implemented, will gap chapter references need migration? The plan doesn't address forward compatibility.

## Residual Risks

| Risk | Severity | Suggested owner |
|------|----------|----------------|
| Bundle immutability contract not specified | Low | Implementation gate |
| Forward compatibility of chapter references (0–7 → 0–10) | Low | Future chapter mapping gate |
| `derived_calculations` and `data_gaps` both carry wording constraints — potential overlap | Low | Implementation gate |
| `fund_type_slot` derivation rules not specified | Low | Implementation gate |

## Validation Commands

```text
# Verify plan's own self-check keywords are present
rg -n "ReportEvidenceBundle|StructuredFundDataBundle|FundDocumentRepository|extra_payload|dayu\.host|dayu\.engine|chapter_contract|turnover|data_gap_refs|no code implementation" docs/reviews/release-maintenance-fact-evidence-contract-s2-bundle-candidate-plan-20260525.md

# Verify no code changes leaked into planning artifact
git diff --check

# Verify current EvidenceAnchor fields match plan's description
rg -n "source_kind|document_year|section_id|page_number|table_id|row_locator|note" fund_agent/fund/extractors/models.py

# Verify StructuredFundDataBundle field list
rg -n "^    (fund_code|report_year|basic_identity|product_profile|benchmark|index_profile|fee_schedule|turnover_rate|nav_benchmark|investor_return|tracking_error|share_change|manager_alignment|manager_strategy|holdings_snapshot|holder_structure|nav_data)" fund_agent/fund/data_extractor.py

# Verify FundDocumentRepository is the only public document entry point
rg -n "class FundDocumentRepository" fund_agent/fund/documents/repository.py
```

Results: all passed.

## Reviewer Self-Check

- [x] Reviewed target, scope, source of truth, and assumptions tested are stated
- [x] Findings are evidence-based, adversarial, actionable, and free of style/nit/speculation
- [x] Open questions, residual risks, and tracking destinations are separated from findings
- [x] Conclusion is one of: pass, pass-with-risks, fail → **PASS_WITH_FINDINGS**
- [x] Output path matches the specified artifact path

## Conclusion

**PASS_WITH_FINDINGS**

The plan correctly chooses to wrap `StructuredFundDataBundle`, preserves `FundDocumentRepository` boundaries, excludes Host/Agent runtime, and prioritizes chapter-contract wording constraints before extraction work. The field-level contract tables are detailed and well-aligned with `docs/design.md` §5.4.2.

Three medium findings (F-1, F-2, F-3) should be resolved before the implementation gate to avoid forcing the implementer to design `classified_fund_type` domain, review status precedence, and `nav_data` projection rules from scratch. Five low findings cover hash stability, source boundary clarity, `preferred_lens` format, test specificity, and `corpus_id` format. None are structural blockers — the plan's direction is sound and the gaps are fillable without replanning.

Recommended next step: controller accepts this plan with findings, then the implementation planning gate resolves F-1 through F-3 before authorizing code.
