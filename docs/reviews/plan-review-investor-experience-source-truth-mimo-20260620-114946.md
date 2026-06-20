# Plan Review: FundDisclosureDocument investor_experience.v1 Source-truth Direct Extraction

## Reviewed Target and Scope

- **Target**: `docs/reviews/funddisclosuredocument-investor-experience-source-truth-extraction-plan-20260620.md`
- **Scope**: `investor_experience.v1` source-truth direct extraction for exactly one field family
- **Branch**: `funddisclosure-investor-experience-source-truth`, HEAD `57c992f70dd6b7c43b799508bd69f37cf1b3cd02`
- **Gate**: Plan Review Gate
- **Classification**: `heavy` (proof-positive public field-family output change)

## Assumptions Tested

1. **Investor return shape**: Plan assumes `investor_return` uses `investor_return_rate`, `disclosure_status`, `fallback_status` — verified against `performance._build_investor_return()` (lines 1100-1148).
2. **Holder structure shape**: Plan assumes `holder_structure` uses `institutional_holder`, `individual_holder` — verified against `manager_ownership._build_holder_structure()` (lines 909-938).
3. **Share change shape**: Plan assumes `share_change` uses `beginning_share`, `ending_share`, `net_change`, `share_class_column`, `share_class_selection_reason` — verified against `holdings_share_change._extract_share_change()` (lines 774-821).
4. **Share class selection reasons**: Plan limits to `single_value_column` and `fund_code_header_match` — verified against `_REASON_SINGLE_VALUE_COLUMN` and `_REASON_FUND_CODE_HEADER_MATCH` constants (lines 28-29). Note: `_REASON_SECTION_TWO_CLASS_EVIDENCE` ("section_2_share_class_evidence") exists but is excluded from this FDD slice.
5. **Facade projection**: Plan assumes `_active_processor_result_to_bundle()` already maps `investor_experience.v1` to `investor_return`, `holder_structure`, `share_change` — verified (lines 767-769, 781-787).
6. **Source-truth admission pattern**: Plan follows `_extract_return_attribution_source_truth()` / `_extract_manager_profile_source_truth()` pattern — verified (lines 1032-1109).
7. **Locator stability**: Plan requires stable locators for emitted values — verified pattern exists (lines 1177, 1254, 1433, etc.).

## Findings

### 001-unresolved-[低]-share_change column selection omits section_2_share_class_evidence reason

- **位置**: Section 5.3 `share_change` Selection, Section 7 Slice 1 Required exact semantics
- **问题类型**: 契约缺失
- **当前写法**: Plan limits `share_class_selection_reason` to `"single_value_column"` or `"fund_code_header_match"` in this FDD direct slice.
- **反例/失败场景**: Some FDD table blocks may have header content that matches section-2 class evidence pattern. The existing parsed-annual extractor accepts `section_2_share_class_evidence` as a valid third reason. If FDD content has a multi-column table where section-2 evidence disambiguates, the FDD extractor would omit `share_change` while the parsed-annual extractor would succeed.
- **为什么有问题**: This is a deliberate scope narrowing for this slice. The plan explicitly states "limited to `"single_value_column"` or `"fund_code_header_match"` in this FDD direct slice" and acknowledges "share_change column selection is intentionally narrower than parsed annual extractor behavior." The limitation is documented and intentional.
- **直接证据**: Plan Section 5.3; `holdings_share_change.py` line 30 `_REASON_SECTION_TWO_CLASS_EVIDENCE`.
- **影响**: FDD direct extraction may omit `share_change` for some multi-column tables that the parsed-annual extractor handles via §2 evidence. This is acceptable as a known limitation of this slice.
- **建议改法和验证点**: No change needed for this slice. Document in residual risks that §2 evidence integration is deferred. Future slice should integrate `_share_class_evidence()` when §2 content is available in FDD intermediate.
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

### 002-unresolved-[低]-investor_return label coverage may miss estimated variants

- **位置**: Section 5.1 `investor_return` Allowed labels
- **问题类型**: 测试缺口
- **当前写法**: Plan defines direct labels (`加权平均投资者收益率`, `投资者收益率`, `投资者实际收益`) and estimated labels (`加权平均投资者收益率（估算）`, `投资者收益率（估算）`, `估算投资者收益率`).
- **反例/失败场景**: Real FDD reports may use label variants not listed (e.g., `投资者加权平均收益率`, `实际收益率`, `投资者回报率`). The plan requires "explicit disclosed value text, preferably a percent literal" and "Do not derive from NAV, benchmark, holder structure, share change, or external data." This is conservative but may miss valid disclosures.
- **为什么有问题**: The plan's label list is narrower than the S6-E candidate selector's `_INVESTOR_EXPERIENCE_MATCH_GROUPS` which includes `投资者回报`, `投资者获得感`, `行为损益`, `盈利投资者占比`. The source-truth extractor uses a different, narrower label set.
- **直接证据**: Plan Section 5.1 labels vs `_INVESTOR_EXPERIENCE_MATCH_GROUPS` lines 377-386.
- **影响**: Some valid investor_return disclosures may be missed, falling back to direct-route missing. This is acceptable fail-closed behavior for this slice.
- **建议改法和验证点**: No change needed. The narrower label set is intentional to avoid false positives. Test should verify that only explicitly listed labels trigger extraction. Future expansion should be gated by evidence review.
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

### 003-unresolved-[低]-holder_structure emits when at least one side found vs parsed-annual both-sides requirement

- **位置**: Section 5.2 `holder_structure` Selection
- **问题类型**: 契约缺失
- **当前写法**: Plan says "Emit `holder_structure` when at least one side is found. Preserve text values as disclosed; do not normalize into ratios or infer missing side. If one side is missing, keep that side as `None` and let family status/gaps carry partiality."
- **反例/失败场景**: The parsed-annual `_build_holder_structure()` also emits when only one side is found (lines 922-929 use `or` fallback). So this is consistent behavior.
- **为什么有问题**: No actual issue. The plan's behavior matches the existing parsed-annual extractor's behavior.
- **直接证据**: Plan Section 5.2; `manager_ownership.py` lines 922-929.
- **影响**: None. Behavior is consistent.
- **建议改法和验证点**: No change needed.
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

### 004-unresolved-[中]-share_change net_change calculation may produce different format than parsed-annual

- **位置**: Section 5.3 `share_change` Selection, point "If `net_change` is absent but beginning/ending are parseable numeric text, calculate `ending - beginning`"
- **问题类型**: 最佳实践偏离
- **当前写法**: Plan says "calculate `ending - beginning` and keep the result as text". The parsed-annual extractor uses `_calculate_net_change()` (line 817-820).
- **反例/失败场景**: If the FDD extractor calculates net_change differently than `_calculate_net_change()` (e.g., different decimal handling, different text formatting), the values may diverge. However, the FDD extractor operates on FDD intermediate cells, not parsed-annual tables, so the calculation logic may need to be reimplemented.
- **为什么有问题**: The FDD extractor cannot reuse `_calculate_net_change()` directly because it operates on FDD cell content, not `ParsedTable` rows. The plan should specify the exact calculation semantics to ensure consistency.
- **直接证据**: Plan Section 5.3; `holdings_share_change.py` lines 816-820.
- **影响**: net_change text format may differ between FDD direct extraction and parsed-annual extraction. Low impact because FDD direct extraction is a separate route.
- **建议改法和验证点**: The plan should specify that net_change calculation uses the same decimal arithmetic as `_calculate_net_change()`: parse beginning/ending as Decimal, compute difference, format as text with original precision. Add a test case verifying net_change calculation from beginning/ending.
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 中

### 005-unresolved-[低]-investor_return estimated label precedence not fully specified

- **位置**: Section 5.1 `investor_return` Selection
- **问题类型**: 契约缺失
- **当前写法**: Plan says "Direct labels take precedence over estimated labels. If direct and estimated both exist with different values, select direct and do not add ambiguity."
- **反例/失败场景**: If multiple direct values exist (e.g., from different tables), they conflict and omit `investor_return`. If multiple estimated values exist, the plan doesn't specify precedence.
- **为什么有问题**: The plan handles direct-vs-estimated precedence but doesn't specify what happens when multiple estimated values exist with different values.
- **直接证据**: Plan Section 5.1 Selection rules.
- **影响**: Multiple estimated values would need conflict resolution. The plan's ambiguity rule ("conflicting values for the same output path omit that output path") should apply.
- **建议改法和验证点**: Clarify that multiple estimated values with different normalized values trigger the same ambiguity rule as multiple direct values: omit `investor_return` and add `ambiguous_table_or_locator`.
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

### 006-unresolved-[低]-Allowed files list omits contracts.py but plan references existing types from it

- **位置**: Section 8 Allowed / Forbidden Files
- **问题类型**: 契约缺失
- **当前写法**: Plan lists `fund_agent/fund/processors/fund_disclosure_processor.py` as allowed but not `fund_agent/fund/processors/contracts.py`.
- **反例/失败场景**: The processor imports types from `contracts.py` (`FundFieldFamilyResult`, `FundExtractionGap`, `EvidenceAnchor`, etc.). If the implementation needs to add a new gap code or modify an existing type, it would need to touch `contracts.py`.
- **为什么有问题**: The plan says "No processor contract/schema expansion unless an existing type already requires local typing; do not add a new public schema." The implementation should use existing types from `contracts.py` without modification.
- **直接证据**: Plan Section 8; `fund_disclosure_processor.py` imports from `contracts.py` (lines 17-34).
- **影响**: None if implementation uses existing types. The forbidden file list is correct because no contract changes should be needed.
- **建议改法和验证点**: No change needed. The implementation should use existing `FundExtractionGap`, `FundFieldFamilyResult`, `EvidenceAnchor` types without modification.
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

## Open Questions

None for code generation. The plan is code-generation-ready under the stated boundaries.

## Residual Risks

1. **FDD source-truth direct extraction remains no-live fixture-backed**: No real-report validation is authorized by this plan. Real-report correctness and readiness claims are explicitly excluded.

2. **Investor return label coverage**: The plan's label list is narrower than the S6-E candidate selector. Some valid disclosures may be missed, falling back to direct-route missing. This is intentional fail-closed behavior.

3. **Share change column selection is intentionally narrower**: The plan excludes `section_2_share_class_evidence` reason because §2 content is not available in FDD intermediate. Future expansion needs separate evidence review.

4. **Subscription_redemption and income_distribution remain candidate-only**: No public/bundle top-level shape exists for these roles. Adding them needs a separate schema/public contract gate.

**Tracking destination**: Residual risks should be tracked in `docs/implementation-control.md` as open residuals for the `investor_experience.v1` implementation gate.

## Plan Review Conclusion

**pass-with-risks**

The plan is code-generation-ready for exactly one family (`investor_experience.v1`) with the following verified properties:

1. **Proof-positive admission boundaries preserved**: The plan correctly requires `FundDisclosureSourceTruthAdmissionProof`, checks `candidate_boundary is None`, `failure_class is None`, and `source_provenance is not None` before allowing direct extraction.

2. **Candidate-only/proof-missing semantics preserved**: The plan correctly suppresses candidate evidence on direct route and preserves candidate-only public missing behavior on proof-missing route.

3. **Public missing behavior preserved**: Direct-route missing returns `value={}`, `status="missing"`, `extraction_mode="missing"`, `anchors=()`, `candidate_evidence=()`.

4. **No schema/public contract expansion**: The plan defines only existing public/bundle keys (`investor_return`, `holder_structure`, `share_change`) and explicitly forbids `subscription_redemption`, `income_distribution`, and other non-existing shapes.

5. **No parser replacement, EvidenceSourceKind/EvidenceAnchor expansion, upper-layer consumption, real-report correctness/readiness/release claims**: All excluded by explicit non-goals.

6. **Value shapes, anchors, gaps, status, candidate suppression, facade tests, docs decision, implementation slices, allowed files, and validation commands are coherent and sufficient**: Verified against existing codebase patterns.

7. **Assumptions around investor_return/holder_structure/share_change existing shape verified**: All three shapes match existing parsed-annual extractor outputs.

The two medium-severity findings (004 net_change calculation format, 005 estimated label precedence) are addressable during implementation without plan changes. The three low-severity findings are documented scope limitations.

The plan follows the established `_extract_return_attribution_source_truth()` / `_extract_manager_profile_source_truth()` pattern and is ready for implementation agent handoff.

---

**Reviewer**: AgentMiMo planning reviewer
**Review timestamp**: 20260620-114946
**Artifact path**: `docs/reviews/plan-review-investor-experience-source-truth-mimo-20260620-114946.md`
