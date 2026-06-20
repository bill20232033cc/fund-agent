# Code Review: FundDisclosureDocument investor_experience.v1 Source-truth Direct Extraction

## Gate Metadata

- Work unit: `FundDisclosureDocument investor_experience.v1 Source-truth Direct Extraction`
- Gate: Code Review Gate
- Role: AgentDS code reviewer only
- Branch: `funddisclosure-investor-experience-source-truth`
- Reviewed: uncommitted diff against accepted plan commit `1bf4187`
- Accepted plan: `docs/reviews/funddisclosuredocument-investor-experience-source-truth-extraction-plan-20260620.md`
- Controller judgment: `docs/reviews/funddisclosuredocument-investor-experience-source-truth-extraction-plan-controller-judgment-20260620.md`
- Implementation evidence: `docs/reviews/funddisclosuredocument-investor-experience-source-truth-extraction-implementation-evidence-20260620.md`
- Review artifact: `docs/reviews/code-review-investor-experience-source-truth-ds-20260620.md`
- Verdict: **CODE_REVIEW_PASS**

## Changed Files Verified

- `fund_agent/fund/processors/fund_disclosure_processor.py` (+1469 lines)
- `tests/fund/processors/test_fund_disclosure_processor.py` (+749 lines)
- `tests/fund/test_data_extractor.py` (+224 lines)
- `fund_agent/fund/README.md` (+8/-8 lines)
- `docs/design.md` (+12/-12 lines)

No changes to `contracts.py`, `data_extractor.py`, `extractors/**`, `documents/**`, `services/**`, `ui/**`, `host/**`, or `agent/**`.

## Validation

```text
uv run pytest tests/fund/processors/test_fund_disclosure_processor.py
174 passed in 0.82s

uv run pytest tests/fund/test_data_extractor.py -k "disclosure_source_truth_investor_experience or disclosure_candidate_only_investor_experience"
2 passed, 37 deselected in 0.40s

uv run ruff check [...]/fund_disclosure_processor.py [...]/test_fund_disclosure_processor.py [...]/test_data_extractor.py
All checks passed!
```

## Scope Verification

### ✅ Public Value Shape (Plan §4)

- `investor_experience.v1.value` only contains `schema_version`, `investor_return`, `holder_structure`, `share_change`。`_build_investor_experience_value()` (line 6304) 严格只遍历 `_INVESTOR_EXPERIENCE_REQUIRED_TOP_LEVEL`。
- No `subscription_redemption`/`income_distribution`/`profitable_investor_ratio`/`behavior_loss` etc. emitted。`_INVESTOR_EXPERIENCE_REQUIRED_TOP_LEVEL` (line 276) 只含三个 key。
- `investor_return` subvalue shape：`investor_return_rate` + `disclosure_status` + `fallback_status`。`_collect_investor_return_paragraph_candidates` (line 5363) 与 `_collect_investor_return_table_candidates` (line 5413) 正确构造三种形态。
- `holder_structure` subvalue shape：`institutional_holder` + `individual_holder`，允许单侧为 None。`_select_investor_experience_holder_structure` (line 5641) 仅在两侧皆无候选时返回 None。
- `share_change` subvalue shape：`beginning_share` + `ending_share` + `net_change` + `share_class_column` + `share_class_selection_reason`。`_share_change_candidate_from_table` (line 5959) 只发出 plan 允许的 key，无申购/赎回子 key。

### ✅ Source Selection Rules (Plan §5)

- Common rules：`locator_stability != "stable"` 跳过（各行均检查）；`source_kind="annual_report"`；`document_year` 来自 context；`section_id`/`table_id` 来自 source block；`page_number=None`；`row_locator` 遵循 `field={output_path}; ...` 格式；`note` 截断至 160 字符。
- `investor_return` paragraph extraction：`_investor_return_value_from_text` (line 5456) 要求同 paragraph label + percent value；`_investor_return_has_unavailable_wording` (line 5521) 检查 label 后 32 字符窗口内的 unavailable token；estimated label 优先由 `_investor_return_label_kind` 检查（line 5433 先匹配 estimated 再 direct）。
- `investor_return` conflict：`_resolve_investor_experience_candidate` (line 6252) 对多个 normalized value 不等的候选写入 `ambiguous_paths` 并返回 None；direct > estimated 优先级由 `_select_investor_experience_return` (line 5314) 实现：先尝试 direct，仅 direct 为空时用 estimated。
- `holder_structure` placeholder filtering：`_holder_structure_value_from_text` (line 5779) 和 `_holder_structure_cell_value` (line 5808) 均检查 `_HOLDER_STRUCTURE_PLACEHOLDERS` frozenset，将 ""、"无"、"不适用"、"-"、"—"、"未披露" 正规化为 None；`_holder_structure_table_has_guard` (line 5760) 检查表格 guard context。
- `share_change` column selection：`_share_change_value_columns` (line 5973) 先做 label column 排除（`_share_change_is_label_column` line 5999），再做 value column 验证（`_share_change_column_has_row_value` line 6029）；`_select_share_change_value_column` (line 6055) 实现 `single_value_column` 与 exact `fund_code_header_match`（`_normalize_match_text` 去空格后全等）；多 value column 无法 selection 时返回 `(None, None)` 并写入 `ambiguous_paths.add("share_change")`。
- `_share_change_column_header` (line 6174) 聚合 `column_header_path`：按 scan order 收集非空 trimmed part，去重保留 first occurrence，用 ` / ` 连接。
- `_calculate_investor_share_net_change` (line 6205) 使用 `Decimal` 算术 `ending - beginning`，输出 `f"{net_change:,.2f}"`，排除逗号后解析，异常返回 None。
- `_looks_like_share_change_value` (line 6233) 使用 `_SHARE_CHANGE_VALUE_PATTERN` 做 fullmatch，排除了空字符串与常见 placeholder。

### ✅ Candidate Suppression / Proof-missing (Plan §6)

- Direct route active：`_field_families_for_intermediate` (line 979) 在 `source_truth_extraction_allowed and content_intermediate is not None` 时才调用 `_extract_investor_experience_source_truth`；direct result 存在时 `investor_experience_evidence = ()`（line 998）。
- Direct-route missing：`_extract_investor_experience_source_truth` (line 5254) 当 status=="missing" 时设置 `extraction_mode="missing"`，`candidate_evidence=()`，`value={}`。Gap 为 `field_family_missing`（`_investor_experience_source_truth_gaps` line 6385）。
- Proof missing/invalid：`source_truth_extraction_allowed=False` 时不进入 direct extractor；`_select_investor_experience_candidate_evidence` 仍然调用；candidate records 保留；`_with_source_truth_admission_gap` 追加 `source_truth_admission_missing` 或 `invalid`。
- Candidate boundary：`candidate_boundary is not None` 的输入由 `_validate_source_truth_admission` 阻断，不进入 direct route。

### ✅ Adjacent Families Non-interference (Plan §6 §2)

- `current_stage_evidence = _select_current_stage_candidate_evidence(intermediate)` 无条件调用（line 1003）。
- `core_risk_evidence = _select_core_risk_candidate_evidence(intermediate)` 无条件调用（line 1004）。
- investor direct route 只 suppress 自己的 candidate evidence（line 998-1002），不影响 stage/risk。
- Test `test_investor_experience_source_truth_does_not_populate_stage_or_risk` 验证 `current_stage.candidate_evidence` 与 `core_risk.candidate_evidence` 非空。

### ✅ Forbidden Scope Boundaries

- No parser replacement：未修改 `documents/`、`extractors/`、repository/source/cache/PDF/Docling/pdfplumber。
- No `EvidenceSourceKind` or public `EvidenceAnchor` expansion：`EvidenceAnchor` 保持不变，`source_kind` 固定为 `"annual_report"`。
- No `contracts.py` change。
- No `data_extractor.py` production change（仅测试扩展）。
- No Service/UI/Host/renderer/quality-gate change。
- No live/network/provider/LLM code。
- `_InvestorExperienceValueCandidate` dataclass (line 390) 只有 4 个字段：`output_path`、`value`、`anchor`、`source_field_path`，无额外 schema 扩展。

### ✅ Docs Sync (Plan §7 Slice 4)

- `docs/design.md` v2.30→v2.31：正确声明 `investor_experience.v1` 进入 source-truth direct extraction；明确只有 `investor_return`/`holder_structure`/`share_change`；`subscription_redemption`/`income_distribution` 保持 candidate-only；`current_stage.v1`/`core_risk.v1` 保持 unimplemented；`candidate_evidence` 保持 `candidate_only/not_proven/NOT_READY`。
- `fund_agent/fund/README.md`：同步更新 source-truth 覆盖列表、investor facade route 描述、scope limitation。
- Implementation evidence artifact 完整记录了 validation output。

### ✅ Tests Cover Contract

- 17 个新 processor 测试覆盖 plan 列出的全部场景：direct-route missing candidate suppression、proof-missing 保持、invalid base admission 阻挡、candidate-boundary 阻挡、exact value shape、estimated only、estimated conflict、label/value pattern 要求、placeholder filtering、partial status、no-allowed-labels missing、ambiguous duplicate omission、label column exclusion、fund-code header match、ambiguous share class、net change calculation、stage/risk non-interference。
- 2 个新 facade 测试覆盖 proof-positive projection 与 candidate-only missing 两条 path。
- Negative cases：ambiguous/conflicting values、placeholder/invalid values、label-only paragraphs、unavailable wording、missing top-level groups、candidate-only roles no public value、stage/risk independence。

## Findings

Findings ordered by severity. No blocking finding.

### F1 (Low) — `_investor_return_has_unavailable_wording` single-char "无" check scope

**Location**: `fund_agent/fund/processors/fund_disclosure_processor.py:5536-5539`

**Description**: The "无" token check uses `window.startswith("无")` on the normalized after-label window. When the label is followed by a delimiter (e.g., `投资者收益率：无`), the normalized window becomes `：无`, and `startswith("无")` returns False. This means `：无` as standalone unavailable wording would not be caught by the "无" check specifically.

**Assessment**: In practice, when `：无` follows the label, the percent pattern also finds no match in the after-label text, so `_investor_return_value_from_text` would return None regardless. The multi-character unavailable tokens (`未披露`, `未提供`, etc.) use substring matching and are not affected. No real functional gap.

**Severity**: Low. No action required for this gate.

### F2 (Low) — Test granularity: `share_change_selects_single_value_column` merged into `extracts_exact_value_shape`

**Location**: `tests/fund/processors/test_fund_disclosure_processor.py:5480` (`test_investor_experience_source_truth_extracts_exact_value_shape`)

**Description**: The plan lists `test_investor_experience_source_truth_share_change_selects_single_value_column` as a separate test. The current implementation verifies `share_class_selection_reason="single_value_column"` inside the broader `extracts_exact_value_shape` test rather than as a standalone focused test.

**Assessment**: The contract is still verified — `test_investor_experience_source_truth_share_change_excludes_label_column` also implicitly confirms single_value_column selection (label column excluded, one value column remains → `single_value_column`). Coverage is sufficient.

**Severity**: Low. No action required for this gate.

### F3 (Info) — `_investor_return_value_from_text` only checks after-label unavailable wording

**Location**: `fund_agent/fund/processors/fund_disclosure_processor.py:5469-5474`

**Description**: The unavailable wording check (`_investor_return_has_unavailable_wording`) only inspects the text after the matched label. If unavailable wording like `本期未披露` appears before the label in the same paragraph, it would not be detected.

**Assessment**: The plan requires checking for unavailable wording "near the matched label." The current implementation takes a conservative interpretation (only after-label). For text like `本期未披露，投资者收益率见下表` without a percent value in the same paragraph, the percent pattern wouldn't match anyway, so no false positive. In the unlikely case of `本期未披露投资者收益率：8.00%` where the unavailable wording is before the label but a label+value pair exists after, this could theoretically be missed. This is an acceptable edge case given the plan's fail-closed design intent for other paths.

**Severity**: Info. No action required.

## Summary

All contract items pass verification. No blocking findings. Implementation strictly follows the accepted plan: exactly `investor_experience.v1` with three existing public/bundle keys, proof-positive only with candidate suppression, proof-missing/invalid/candidate-boundary preserved, `subscription_redemption`/`income_distribution` candidate-only, `current_stage.v1`/`core_risk.v1` untouched, no parser/repository/schema/upper-layer changes. All 174 processor tests + 2 facade tests pass; ruff clean.
