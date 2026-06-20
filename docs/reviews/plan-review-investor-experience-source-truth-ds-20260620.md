# Plan Review: FundDisclosureDocument investor_experience.v1 Source-truth Direct Extraction

## Review Metadata

- **Reviewer**: AgentDS planning reviewer only
- **Review gate**: Plan Review Gate
- **Reviewed plan**: `docs/reviews/funddisclosuredocument-investor-experience-source-truth-extraction-plan-20260620.md`
- **Branch**: `funddisclosure-investor-experience-source-truth`, HEAD `57c992f`
- **Verdict**: `PLAN_REVIEW_PASS`
- **Artifact path**: `docs/reviews/plan-review-investor-experience-source-truth-ds-20260620.md`

## Reviewed Target and Scope

本 review 判定该 plan 是否 code-generation-ready，并重点压测：

- 是否只覆盖 `investor_experience.v1` 一个 field family
- 是否保持 proof-positive admission boundary、candidate-only/proof-missing 语义、public missing 行为
- 是否避免 schema/public contract expansion，只定义已有 public/bundle key
- 是否避免 parser replacement、EvidenceSourceKind/EvidenceAnchor expansion、upper-layer consumption、real-report correctness/readiness/release claims
- value shapes、anchors、gaps、status、candidate suppression、facade tests、docs decision、implementation slices、allowed files、validation commands 是否连贯且充分
- `investor_return`/`holder_structure`/`share_change` 已有 shape 假设与 `share_change` column selection 假设

## Source of Truth

- `fund_agent/fund/processors/fund_disclosure_processor.py` — current processor with existing source-truth extraction for product_essence, return_attribution, manager_profile; candidate-only for investor_experience
- `fund_agent/fund/processors/contracts.py` — FundFieldFamilyResult, EvidenceAnchor, FundCandidateEvidenceRecord, FundExtractionGap, FundDisclosureDocumentContentIntermediate 契约
- `fund_agent/fund/data_extractor.py` — `_active_processor_result_to_bundle()` 已投影 investor_experience → investor_return, holder_structure, share_change
- `fund_agent/fund/extractors/performance.py` — `_build_investor_return()` shape: investor_return_rate, disclosure_status, fallback_status
- `fund_agent/fund/extractors/manager_ownership.py` — `_build_holder_structure()` shape: institutional_holder, individual_holder
- `fund_agent/fund/extractors/holdings_share_change.py` — `_extract_share_change()` shape: beginning_share, ending_share, net_change, share_class_column, share_class_selection_reason
- `docs/design.md` — design truth stating investor_experience.v1 source-truth unimplemented, candidate evidence stays candidate_only/not_proven/NOT_READY
- `tests/fund/processors/test_fund_disclosure_processor.py` — existing source-truth proof guard tests, return/manager direct extraction tests, investor-experience candidate-only tests

## Assumptions Tested

1. **Existing public/bundle keys are investor_return, holder_structure, share_change only** — VERIFIED. `_active_processor_result_to_bundle()` at `data_extractor.py:767-769` maps exactly these three keys from `investor_experience.v1` value dict. No subscription_redemption or income_distribution in bundle.

2. **Existing source-truth direct extraction pattern is reusable** — VERIFIED. `_extract_return_attribution_source_truth()` (line 1032) and `_extract_manager_profile_source_truth()` (line 1072) follow identical structure: select_values → build_value → gaps → status → dedupe_anchors → return FundFieldFamilyResult with candidate_evidence=(). Pattern is clean and directly applicable.

3. **Proof validation gate is already in place** — VERIFIED. `_validate_source_truth_admission()` (line 943) checks proof type, candidate_boundary, failure_class, source_provenance, and cross-identity equality. New family needs no change to this gate.

4. **Candidate suppression pattern exists** — VERIFIED. `_field_families_for_intermediate()` (line 848) already does `product_essence_evidence = () if product_essence_source_truth is not None else _select_product_essence_candidate_evidence(intermediate)`. Same pattern applies to investor_experience.

5. **Existing candidate-only roles stay candidate-only** — VERIFIED. `_INVESTOR_EXPERIENCE_MATCH_GROUPS` (line 374) includes `subscription_redemption` and `income_distribution` as locator roles. These remain candidate-only: no public value keys exist for them in the bundle projection.

6. **investor_return value shapes match existing extractor** — VERIFIED. `_build_investor_return()` at `performance.py:1100` produces exact shapes the plan specifies: direct disclosure with `investor_return_rate`/`disclosure_status="direct"`/`fallback_status="not_needed"`, estimated with `disclosure_status="estimated"`/`fallback_status="estimated_disclosure_in_section"`.

7. **holder_structure value shapes match existing extractor** — VERIFIED. `_build_holder_structure()` at `manager_ownership.py:909` produces `institutional_holder`/`individual_holder` as text-or-None.

8. **share_change value shapes match existing extractor** — VERIFIED. `_extract_share_change()` at `holdings_share_change.py:774` produces `beginning_share`/`ending_share`/`net_change`/`share_class_column`/`share_class_selection_reason`. Net change calculation uses `Decimal` arithmetic at line 1274.

## Findings

### 1-share-change-column-selection-中-share_change 列选择在 FDD 协议下规格不够充分

- **位置**: Plan §5.3 Selection rules, Slice 1 helpers
- **问题类型**: 不可直接实施
- **当前写法**: 列选择仅通过两个原因决定：`single_value_column` 或 `fund_code_header_match`；未定义如何从 FDD table block 协议中区分 label 列与 value 列。
- **反例/失败场景**: implementation agent 在 `FundDisclosureTableBlockLike.cells` 中扫描 column_index 时，需要判断某列是 label（如“项目”“份额类别”）还是 value（如基金代码/份额数值）。如果 label 列判断逻辑与已有 extractor 不一致，可能选中 label 列作为 value 列，产出无效 `share_change` 值。
- **为什么有问题**: 已有 `holdings_share_change._select_share_change_value_column()` 在 `ParsedTable` 上使用了 `_is_label_column()` 与 `_share_class_column_matches()` 等复杂逻辑。FDD table block 协议没有 `headers` 属性，列头信息分散在各 cell 的 `column_header_path` 中。plan 未定义如何在 FDD 协议下识别 label 列、如何从 `column_header_path` 提取列头文本与 fund_code 匹配。
- **直接证据**:
  - `contracts.py:411-420`：`FundDisclosureTableBlockLike` 只有 `cells: tuple[FundDisclosureCellLike, ...]`，无显式 headers 属性
  - `contracts.py:404-405`：每个 cell 有 `column_header_path: tuple[str, ...]` 和 `row_label_path: tuple[str, ...]`
  - `holdings_share_change.py:824-873`：已有 `_select_share_change_value_column()` 依赖 `table.headers` 和 `_ShareClassEvidence`
  - plan §5.3 明确说不使用 paragraph fallback 且不依赖 §2 share class evidence
- **影响**: 实施 Agent 需要在 FDD 协议下重新设计列分类逻辑，可能产出与已有 extractor 不一致的列选择行为
- **建议改法和验证点**:
  - 在 plan §5.3 增加：如何从 `column_header_path` 聚合列头文本、label 列的判定 token 集合（复用已有 `_LABEL_COLUMN_TOKENS` 或定义 FDD 专用集合）、fund_code header match 的比较策略（精确匹配 `context.fund_code`，忽略空白）
  - 验证：test fixture 中包含多列 share_change 表，确认 label 列被正确排除、单值列被选中、fund code 列被精确匹配
- **修复风险（低）**: 增加列选择规则的文本，不改变 plan 结构
- **严重程度（中）**: fail-closed 姿态下最坏情况是 omit share_change，不会产生错误 public value；但列选择是实现最复杂的子任务，当前规格对实施 Agent 不够直接

### 2-holder-structure-value-validation-低-holder_structure 未定义 stable disclosed value 的最小验证规则

- **位置**: Plan §5.2 Selection rules
- **问题类型**: 契约缺失
- **当前写法**: "Emit `holder_structure` when at least one side is found"，"Preserve text values as disclosed"
- **反例/失败场景**: FDD content 中可能存在 placeholder 文本（如“无”、“不适用”、“-”、“未披露”、“—”）。当前规则下这些文本会被当作合法 holder_structure 值发出，导致 public value 中出现语义无效的字段。
- **为什么有问题**: 已有 `_build_holder_structure()` 使用 `_extract_field()` 来抽取字段值，`_extract_field()` 内部有 token match 和值提取逻辑，只有当 label 匹配且后随有效文本时才返回值。plan 的 FDD 直抽路径没有等效的值验证。
- **直接证据**: manager_ownership.py:922 使用 `_extract_field(report, "institutional_holder")` 进行结构化抽取，而非裸文本
- **影响**: 可能将 placeholder 文本误发为合法 holder_structure public value
- **建议改法和验证点**:
  - 增加最小验证：提取到的 institutional/individual holder 文本不能是已知 placeholder token（`无`、`不适用`、`-`、`—`、`未披露`、空字符串）
  - 测试：fixture 中 holder cell 值为“无”或“不适用”，验证对应 side 保持 `None` 且不触发 full omission
- **修复风险（低）**
- **严重程度（低）**: 影响限于输出质量，不是数据损坏；fail-closed 下可以通过增加 placeholder 过滤修复

### 3-investor-return-paragraph-extraction-低-investor_return 段落抽取的 label/value 模式未定义

- **位置**: Plan §5.1 Allowed sources: "Stable paragraph text with explicit label/value pattern"
- **问题类型**: 不可直接实施
- **当前写法**: 计划接受 "Stable paragraph text with explicit label/value pattern" 但不定义抽取模式
- **反例/失败场景**: implementation agent 可能用不恰当的 regex 或文本匹配从段落中抽取投资者收益率。例如段落文本为“报告期内本基金未披露加权平均投资者收益率”，label 匹配成功但 value 语义为空或否定。
- **为什么有问题**: 已有 `_build_investor_return()` 依赖 `_extract_field()` 的 token match + value extraction 机制。plan 未说明 FDD 直抽应复用类似模式还是使用新的匹配策略。
- **直接证据**: plan §5.1 仅定义了 allowed labels 和 "explicit label/value pattern"，未指定抽取算法的输入/输出契约
- **影响**: 实施 Agent 需自行设计段落抽取算法
- **建议改法和验证点**:
  - 明确段落抽取为：label token 命中后，从同一 paragraph block 中提取紧接着的百分数文本作为 investor_return_rate
  - 如果 label 命中但无法提取有效百分数，不发出 investor_return
  - 测试：fixture 包含 label 匹配但无有效 value 的段落，验证 investor_return 被 omit
- **修复风险（低）**
- **严重程度（低）**: table/cell based extraction 是主要路径，paragraph 是次要路径；fail-closed 姿态下最坏是 omit

## Architecture Boundary Review

- **Layering**: plan 严格限定在 Processor 层 (`fund_disclosure_processor.py`)，不穿透到 Extractor、Facade、Service、UI 层。PASS.
- **Contract expansion**: plan 明确禁止 `EvidenceSourceKind`、`EvidenceAnchor`、schema/public contract 扩展。仅使用已有 `FundFieldFamilyResult`、`EvidenceAnchor(source_kind="annual_report")`、已有 gap codes。PASS.
- **Dependency direction**: plan 的 direct extractor 只依赖 `FundDisclosureDocumentContentIntermediate` 协议（sections/paragraph_blocks/table_blocks/cells），不依赖 `ParsedAnnualReport`、`FundDocumentRepository` 或外部来源。PASS.
- **Facade boundary**: plan 明确不修改 `data_extractor.py` 生产代码，仅增加回归测试。已有 `_active_processor_result_to_bundle()` 投影逻辑无需变更。PASS.

## Overcoupling Review

- plan 的 investor_experience source-truth extractor 与已有 product_essence/return_attribution/manager_profile extractor 共享 `_validate_source_truth_admission()` gate，但不共享内部选择逻辑。每个 family 有独立的 `_select_*_values()` 和 `_build_*_value()` 函数。这是正确的分离模式。PASS.
- `_field_families_for_intermediate()` 中的更改是局部添加（加一个 source-truth 变量、加一个 conditional call、改一行 candidate suppression），不触及其他 family 的 logic。PASS.
- plan 不修改 S6-E candidate selector 的遍历机制，只在外部通过 conditional 控制是否调用。PASS.

## Overengineering Review

- plan 定义的 helper 函数数量（约 15 个小型 local helper）与已有 return_attribution 和 manager_profile 的 helper 密度一致。无 unnecessary abstraction。PASS.
- `_InvestorExperienceValueCandidate` dataclass 与已有 `_ManagerProfileValueCandidate` 结构一致，无 extra fields。PASS.

## Best-Practice Review

- fail-closed posture 被一致应用：当任何值无法确定时 omit 该 subvalue 并添加 gap，而非猜测。PASS.
- test plan 覆盖 proof-positive、proof-missing、candidate-boundary-blocked、missing-provenance、failure-class、partial、ambiguous、share_change column ambiguity、no stage/risk alteration。覆盖面充分。PASS.
- 但 test plan 缺少以下边界测试（见 Open Questions）：
  - holder_structure 的单边缺失（仅 institutional 无 individual，或反之）
  - investor_return 的 estimated-only 路径
  - share_change 的 net_change 自动计算

## Optimal-Solution Review

- plan 选择在 Processor 内部增加 field-family-local direct extractor，而非新增 Processor 或修改 registry。这是最小侵入路径，与已有三个 source-truth families 一致。PASS.
- plan 选择不引入 schema/public contract gate，只使用已有 public/bundle keys。这是正确的 sequencing：先实现已有 shape 的 source-truth extraction，后续再独立 gate 处理新 key。PASS.

## Open Questions

1. **share_change net_change 计算**: plan 说 "safely calculate from beginning/ending when both are parseable"，是否复用 `_calculate_net_change()` 的 Decimal 算法（`holdings_share_change.py:1274`）？建议 plan 显式引用已有 helper 或定义等效算法。

2. **holder_structure 单边 missing 行为**: plan 说 "Emit `holder_structure` when at least one side is found"，但未指定单边 missing 时另一侧仍然发出的测试。建议增加 `test_investor_experience_source_truth_holder_structure_partial_one_side_missing`。

3. **investor_return estimated-only 路径**: plan §5.1 定义了 estimated disclosure shape，但 test plan 中未包含 estimated-only 的专项测试（所有三个 subvalue 中只有 investor_return 在 estimated status 下发出）。

4. **Candidate evidence 压制范围**: plan 说 direct route 的 `investor_experience_evidence` 为 `()`。当 `investor_experience` 为 direct-route missing 时，`current_stage` 和 `core_risk` 的 candidate evidence 是否仍正常产生？从代码路径看是的（它们不在 suppression 范围内），但 plan 未显式确认。

## Residual Risks

1. **share_change column selection 实现复杂度**: FDD table protocol 的列选择逻辑需要 implementation agent 从 cell 级数据重新聚合列结构。这是实现中风险最高的子任务。建议 implementation gate 中优先实现并测试 share_change 列选择逻辑，再实现 investor_return 和 holder_structure。风险 owner: implementation agent。

2. **FDD source-truth 无 live fixture 验证**: plan 明确声明不进行 real-report validation。所有 test 使用 stub/fixture 数据。未来 live report 可能与 stub 假设不同（如 label 文本变体、表格结构差异）。风险 owner: 后续 evidence gate。

3. **investor_return label 覆盖率**: plan 只列出了有限的中文 label 集合。不同基金公司的年报可能使用略有不同的术语。fail-closed 姿态下未覆盖的 label 不会产生 false positive，但可能产生 false negative（应有值被 omit）。此风险在 design truth 中已接受为当前边界。风险 owner: design truth / 后续 label expansion gate。

## Tracking Destination

- Residual risks #2 和 #3 应记录到 `docs/implementation-control.md` 的当前 residual risk 节
- Open questions #1-#4 建议在 implementation gate 开始前由 controller 裁决或直接由 implementation agent 在实现中处理（均为低风险决策）

## Conclusion

`PLAN_REVIEW_PASS`

该 plan 是 code-generation-ready。它正确定义了单一 family 的 scope、preserve 了 proof-positive admission boundary、正确使用了已有 public/bundle key shapes、避免了 schema/contract expansion、正确定义了 candidate suppression 和 proof-missing 语义。三个 findings 均为边界规格的细化建议，不构成结构性风险。fail-closed 姿态使得所有未覆盖场景都收敛到 omit + gap，不会产生错误 public value。implementation slices、allowed files、validation commands 连贯且充分。
