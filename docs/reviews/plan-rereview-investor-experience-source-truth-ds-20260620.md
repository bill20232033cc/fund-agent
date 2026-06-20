# Targeted Plan Re-Review: FundDisclosureDocument investor_experience.v1 Source-truth Direct Extraction

## Re-Review Metadata

- **Reviewer**: AgentDS targeted planning reviewer only
- **Gate**: Plan Re-review Gate
- **Re-reviewed plan**: `docs/reviews/funddisclosuredocument-investor-experience-source-truth-extraction-plan-20260620.md`
- **Prior DS review**: `docs/reviews/plan-review-investor-experience-source-truth-ds-20260620.md`
- **Prior MiMo review**: `docs/reviews/plan-review-investor-experience-source-truth-mimo-20260620-114946.md`
- **Branch**: `funddisclosure-investor-experience-source-truth`, HEAD `57c992f`
- **Verdict**: `TARGETED_PLAN_REREVIEW_PASS`
- **Artifact path**: `docs/reviews/plan-rereview-investor-experience-source-truth-ds-20260620.md`

## Re-Review Scope

Targeted verification of 6 accepted findings from prior reviews, checking whether each was addressed in the post-fix plan artifact. No full plan review expansion.

## Finding-by-Finding Verification

### 1. DS Finding #1 — share_change FDD column selection specificity

**Prior concern**: Plan未定义如何在 FDD table block 协议下区分 label 列与 value 列；缺少从 `column_header_path` 提取列头文本、label 列判定 token 集合、fund_code 匹配策略。

**Verified fix in plan §5.3**:
- Column header text aggregation from `column_header_path`: group by `column_index`, collect non-empty strings, trim/deduplicate/join with ` / ` (lines 217-220).
- Label column exclusion: enumerates label tokens (`项目`, `项目名称`, `份额类别`, `类别`, etc.) and requires column to be "dominated by" labels OR mostly contain row-label text instead of numeric values (lines 220-221).
- Value column gate: must contain at least one stable beginning/ending/net row value after label-column exclusion (line 222).
- `fund_code_header_match`: exact match against `context.fund_code` after whitespace trimming and internal whitespace removal (line 223).
- Dedicated test cases for label column exclusion, single_value_column selection, and fund_code_header_match (lines 346-352).

**Status**: ADDRESSED. Column selection rules are now specific enough for implementation agent to act on.

### 2. DS Finding #2 — holder_structure placeholder filtering

**Prior concern**: Placeholder 文本（`无`、`不适用`、`-`、`未披露`、`—`）会被当作合法值发出。

**Verified fix in plan §5.2**:
- Explicit placeholder rejection: "Invalid holder side values include empty string, whitespace-only text, `无`, `不适用`, `-`, `—`, and `未披露`" (lines 192-193).
- Rejected placeholder side behavior: "remains `None`; it must not be emitted as a public value and must not by itself make `holder_structure` present" (lines 193-194).
- Dedicated test case `test_investor_experience_source_truth_holder_structure_filters_placeholder_values` (line 338).

**Status**: ADDRESSED. Placeholder filtering is explicit and test-covered.

### 3. DS Finding #3 — investor_return paragraph label/value and unavailable wording

**Prior concern**: 段落抽取的 label/value 模式未定义；label 命中但无有效 value 或否定文本的处理未规定。

**Verified fix in plan §5.1**:
- Paragraph extraction contract: "label token plus a valid percent value in the same paragraph block. The value must appear after the label or within the immediate label/value phrase around the label; a label-only paragraph is not enough" (line 165).
- Unavailable/negated wording: "If the paragraph contains negated or unavailable wording near the matched label, including `未披露`, `未提供`, `无法取得`, `不适用`, or `无`, omit `investor_return` for that paragraph even if the label token matches" (line 166).
- Table/cell extraction has analogous requirement: label + value in same row/cell context, no unavailable cells (line 167).
- Dedicated test case `test_investor_experience_source_truth_investor_return_paragraph_requires_label_value_pattern` covering label-only, no-value, and negated/unavailable scenarios (line 336).

**Status**: ADDRESSED. Paragraph extraction rules are concrete and unavailable/negated wording is handled.

### 4. MiMo Finding #004 — net_change Decimal semantics

**Prior concern**: Plan未指定 net_change 计算使用与 `_calculate_net_change()` 相同的 decimal 算法，可能导致格式不一致。

**Verified fix in plan §5.3**:
- Explicit Decimal semantics: "calculate `ending - beginning` with `Decimal` arithmetic aligned with the existing `_calculate_net_change` semantics in `holdings_share_change.py`; preserve stable text formatting by using a deterministic decimal string derived from the computed `Decimal` without scientific notation and without adding presentation units" (line 226).
- Dedicated test case `test_investor_experience_source_truth_share_change_calculates_net_change` (line 354).

**Status**: ADDRESSED. Decimal arithmetic specification is now explicit and references the existing implementation.

### 5. MiMo Finding #005 — estimated investor_return conflict rule and tests

**Prior concern**: Multiple estimated values 冲突时的处理未规定。

**Verified fix in plan §5.1**:
- Estimated conflict rule: "If multiple estimated values exist and their normalized values conflict, apply the same ambiguity rule as direct conflicts: omit `investor_return` and add `ambiguous_table_or_locator` with `source_field_path="investor_return"`" (lines 170-171).
- Dedicated test case `test_investor_experience_source_truth_estimated_investor_return_conflict_omits_value` (line 333).
- Estimated-only path test `test_investor_experience_source_truth_estimated_investor_return_only` (line 332).

**Status**: ADDRESSED. Estimated conflict rule is explicit and test-covered; estimated-only happy path also has a test.

### 6. DS Open Question #4 — current_stage/core_risk candidate evidence unaffected

**Prior concern**: Plan未显式确认 direct-route suppression 不会清除 current_stage/core_risk 的 candidate evidence。

**Verified fix in plan §6**:
- Explicit non-interference clause: "Their existing candidate selectors may still populate candidate evidence when matching candidate content exists; `investor_experience.v1` direct-route suppression must not clear, suppress, or otherwise alter their candidate evidence. They must not enter source-truth direct extraction" (line 253).
- Dedicated test case `test_investor_experience_source_truth_does_not_populate_stage_or_risk` verifying both non-alteration of stage/risk source-truth behavior AND non-clearing of their candidate evidence when matching content exists (line 356).

**Status**: ADDRESSED. Non-interference is explicit and test-covered.

## New Blocker Check

No new blocker introduced by the fixes. Each fix added specificity within the existing plan structure without creating contradictions, scope drift, or implementation ambiguity.

## Conclusion

`TARGETED_PLAN_REREVIEW_PASS`

All 6 accepted plan-review findings (DS #1/#2/#3, MiMo #004/#005, DS OQ #4) have been addressed in the plan artifact with concrete rules, explicit contracts, and dedicated test cases. No new blocker was introduced by the fixes. The plan remains code-generation-ready.
