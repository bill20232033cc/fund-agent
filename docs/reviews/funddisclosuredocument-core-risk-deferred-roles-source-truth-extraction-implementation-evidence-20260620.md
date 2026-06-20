# FundDisclosureDocument core_risk.v1 Deferred Risk Roles Source-truth Direct Extraction Implementation Evidence

## Verdict

`IMPLEMENTATION_COMPLETE`

Release/readiness remains `NOT_READY`.

## Gate / Work Unit

- Gate: `FundDisclosureDocument core_risk.v1 Deferred Risk Roles Source-truth Direct Extraction Implementation Gate`
- Plan commit: `1f56ee8`
- Controller judgment: `docs/reviews/funddisclosuredocument-core-risk-deferred-roles-source-truth-extraction-plan-controller-judgment-20260620.md`

## Changed Files

| File | Change |
|---|---|
| `fund_agent/fund/processors/fund_disclosure_processor.py` | Add `_CoreRiskRoleValueCandidate`, `_CoreRiskValueCandidate` union, `_CORE_RISK_REQUIRED_TOP_LEVEL`, `_CORE_RISK_ROLE_KEYS`; remove `_CORE_RISK_DEFERRED_ROLES`; add `_select_core_risk_role_values`, `_collect_core_risk_role_paragraph_candidates`, `_collect_core_risk_role_cell_candidates`, `_is_core_risk_role_placeholder`, `_is_core_risk_role_heading_only`, `_resolve_core_risk_role_candidate`, `_build_core_risk_role_disclosure_value`; rewrite `_select_core_risk_values`, `_build_core_risk_value`, `_core_risk_emitted_output_paths`, `_core_risk_source_truth_gaps`, `_core_risk_status` |
| `tests/fund/processors/test_fund_disclosure_processor.py` | Replace `test_core_risk_source_truth_extracts_risk_characteristic_text_only` with `test_core_risk_source_truth_extracts_all_five_required_subvalues`; add `test_core_risk_source_truth_risk_text_only_yields_partial`, `test_core_risk_source_truth_role_heading_only_not_promoted`, `test_core_risk_source_truth_role_ambiguity_omits_role`, `test_core_risk_source_truth_identical_role_text_resolves_first`, `test_core_risk_source_truth_paragraph_heading_only_rejected`, `test_core_risk_source_truth_generic_token_requires_guard_context`, `test_core_risk_source_truth_generic_token_with_guard_accepted`; update `test_product_essence_source_truth_extracts_minimal_shape` and `test_investor_experience_source_truth_does_not_pollute_stage_or_core_risk` for partial status and `field_family_partial` gaps; import `_CORE_RISK_ROLE_KEYS` |
| `tests/fund/test_data_extractor.py` | Add `_CoreRiskAllRolesDisclosureProcessor` test processor and `test_explicit_disclosure_core_risk_role_keys_not_projected_to_bundle` facade no-projection test |
| `fund_agent/fund/README.md` | Replace deferred-role wording with current five-subvalue accepted state; remove stale `deferred_role`/candidate-only role claims |

## Exact Public `core_risk.v1` Value Shape

```python
{
    "schema_version": "core_risk.v1",
    "risk_characteristic_text": {
        # 既有 risk_characteristic_text.v1 shape，不变
        "schema_version": "risk_characteristic_text.v1",
        "fund_code": "<code>",
        "report_year": <year>,
        "risk_characteristic_text": "<normalized disclosure>",
        "source_anchors": [...],
    },
    "liquidation_or_scale_risk": {
        "schema_version": "core_risk_role_disclosure.v1",
        "fund_code": "<code>",
        "report_year": <year>,
        "role": "liquidation_or_scale_risk",
        "risk_disclosure_text": "<normalized direct annual-report disclosure>",
    },
    "tracking_error_or_deviation_risk": {  # 同上五键 }
    "turnover_or_style_drift_risk":    {  # 同上五键 }
    "concentration_risk":              {  # 同上五键 }
}
```

Shape constraints verified:
- `risk_characteristic_text.v1` unchanged.
- Role subvalues use `core_risk_role_disclosure.v1` (five keys: `schema_version`, `fund_code`, `report_year`, `role`, `risk_disclosure_text`).
- No `source_anchors` inside role subvalues; public anchors only in `FundFieldFamilyResult.anchors`.
- No `deferred_role` gaps emitted.
- No `pressure_test`, `max_drawdown`, `veto`, `risk_level`, `risk_summary`, `final_decision` keys.

## Admission / Fail-Closed Behavior

Preserved from prior gate:
- `_validate_source_truth_admission()` unchanged: requires `FundDisclosureSourceTruthAdmissionProof`, `candidate_boundary is None`, `failure_class is None`, `source_provenance is not None`, exact identity match.
- Proof-missing/invalid/candidate-boundary paths suppress all public values and anchors; candidate evidence preserved in non-proof paths.
- Proof-positive direct paths suppress candidate evidence.

New behavior:
- Proof-positive with all five required subvalues → `status="accepted"`.
- Proof-positive with only `risk_characteristic_text` → `status="partial"` + `field_family_partial` gaps for four missing role keys.
- Proof-positive with no subvalues → `status="missing"` + `field_family_missing` gap.
- Ambiguous role disclosures → omit role, emit `ambiguous_table_or_locator`.

## Facade / Bundle Decision

- No `StructuredFundDataBundle.core_risk` added.
- `_active_processor_result_to_bundle()` unchanged: `core_risk.v1` only fallbacks `risk_characteristic_text` when `product_essence.v1` lacks it.
- `bundle.tracking_error`, `bundle.turnover_rate`, `bundle.holdings_snapshot` not populated from `core_risk.v1` role keys.
- No role key appears as a bundle attribute.

## Source-Truth Role Selection Rules Implemented

- Paragraph candidates: `text_normalized` or `text_raw`; strong token → direct qualify; generic token → need guard context (heading_path + same text has guard_token).
- Cell candidates: `cell_text_normalized` or `cell_text`; reject `is_header_cell`, `header_rows`, non-`body_rows`, placeholder text (`无`/`不适用`/`-`/etc); strong/generic/guard same pattern.
- Heading-only rejection: normalized text equals a token → rejected; otherwise, if under 15 chars and contains no ASCII digit → rejected as structural label; short numeric/ratio/threshold values (containing digits) are not rejected by length alone (see follow-up fix).
- Scan order: paragraphs by tuple index, then tables by index with cells sorted by `(row_index, column_index)`.
- Resolution: no candidates → None; all same normalized text → first; different text → ambiguous.
- `_CORE_RISK_MATCH_GROUPS` entries 1–4 reused; `risk_characteristic` entry (index 0) skipped in role loop.

## Validation Outputs

### Initial implementation

```
uv run pytest tests/fund/processors/test_fund_disclosure_processor.py -q -k core_risk
28 passed, 167 deselected

uv run pytest tests/fund/processors/test_fund_disclosure_processor.py -q
195 passed

uv run pytest tests/fund/test_data_extractor.py -q
43 passed

uv run ruff check ...
All checks passed!

git diff --check -- <changed files>
(no output = clean)
```

### Follow-up fix (short numeric cell acceptance)

```
uv run pytest tests/fund/processors/test_fund_disclosure_processor.py -q -k core_risk
29 passed, 167 deselected

uv run pytest tests/fund/processors/test_fund_disclosure_processor.py -q
196 passed

uv run pytest tests/fund/test_data_extractor.py -q
43 passed

uv run ruff check ...
All checks passed!

git diff --check -- <changed files>
(no output = clean)
```

## Follow-up Fix: Short Numeric Cell Acceptance

Controller found `_is_core_risk_role_heading_only()` rejected all text with `len(normalized) < 15`, including short data cells like `180%`, `45%`, `5000万元`.

**Fix:** Added `_any_ascii_digit()` helper. After the token-equality check and before the length check, if the normalized text contains any ASCII digit (`0-9`), it is not rejected as heading-only. Short non-numeric structural labels (e.g. `换手率风险`) are still rejected.

**Changed:**
- `fund_agent/fund/processors/fund_disclosure_processor.py`: Added `_any_ascii_digit()` helper; modified `_is_core_risk_role_heading_only()` to allow short numeric/ratio values.
- `tests/fund/processors/test_fund_disclosure_processor.py`: Added `test_core_risk_source_truth_short_numeric_cell_accepted_short_label_rejected` — a turnover cell with text `换手率180%` (7 chars, contains digits) is accepted; a paragraph with text `换手率风险` (5 chars, no digits) is still rejected.

## Residual Risks

| Risk | Disposition |
|---|---|
| Real-report correctness unproven | Assigned to separate evidence/readiness gates |
| Parser/document representation quality unproven | Assigned to Fund documents evidence owner |
| Role extraction from broad tokens could over-match in real reports | Guard context + heading-only + substantive disclosure rules mitigate; real-report regression gates needed |
| `risk_characteristic_text` status changes from `accepted` to `partial` when other roles are missing | Accepted contract change; downstream consumers that only check `status` may need updating |
| Docs sync for `docs/design.md` and `docs/implementation-control.md` | Completed in follow-up docs-sync pass (see below) |
| PR 34 state remains draft/open | Controller/user disposition gate |

## Docs Sync Follow-up

Updated three control docs plus evidence to reflect current implementation state:
- `docs/design.md`: Replaced four occurrences of stale `core_risk.v1` wording (only `risk_characteristic_text`, deferred roles, `deferred_role` gaps) with full five-subvalue description.
- `docs/current-startup-packet.md`: Updated active gate, gate classification, gate input, and non-goal reminder to `Implementation Completed` → next entry `Code Review Gate`.
- `docs/implementation-control.md`: Updated latest control update, current truth guardrails, current direction, gate classification, next entry point, and non-goal reminder.

Stale-phrase scan (`rg` over all four docs) confirmed no remaining claims of `core_risk.v1` only covering `risk_characteristic_text` or roles being deferred.

## Follow-up Fix: Code Review Gate — Finding 1 (Numeric Cell Role Matching)

Code review artifact `docs/reviews/code-review-20260620-184649.md` identified that pure numeric role table cells (e.g. `180%`, `45%`) were omitted because `_collect_core_risk_role_cell_candidates()` used only cell text for `candidate_texts` (line 4843), and `_matches_guarded_core_risk_source()` required strong/generic token hit in `texts` before considering guard context.

**Fix:** In `_collect_core_risk_role_cell_candidates()`, for body cells whose normalized text contains ASCII digits, include `table.heading_text`, `table.table_caption_or_nearby_heading`, `cell.row_label_path`, and `cell.column_header_path` in `candidate_texts` so that role tokens from cell-specific and immediate table context (including caption-only context) can authorize the cell. Non-numeric cells are unchanged. Header/placeholder/heading-only rejection preserved.

**Regression:** Two `manager_profile` tests (`test_manager_profile_source_truth_extracts_roster_strategy_turnover_shape` and `test_manager_profile_source_truth_accepted_when_all_allowed_groups_present`) asserted `core_risk.v1.value == {}` but now legitimately emit `turnover_or_style_drift_risk` because their fixtures contain a turnover-rate table with heading `报告期内股票换手率` and numeric cell `123.45%`. Assertions updated to verify the correct turnover role extraction. No regression in manager_profile field family itself.

**Changed:**
- `fund_agent/fund/processors/fund_disclosure_processor.py`: Modified `_collect_core_risk_role_cell_candidates()` — numeric body cells now expand `candidate_texts` with table heading + row/column label context for token matching.
- `tests/fund/processors/test_fund_disclosure_processor.py`:
  - `test_core_risk_source_truth_short_numeric_cell_accepted_short_label_rejected`: Changed turnover cell from `cell_text="换手率180%"` to `cell_text="180%"` (true numeric-only cell, token from guard context); added concentration cell `cell_text="45%"` with concentration guard context.
  - Added `test_core_risk_source_truth_isolated_numeric_cell_omitted`: Verifies isolated `180%` with no same-role guard remains missing.
  - Updated two manager_profile test assertions to accept legitimate turnover role extraction.
  - Added `test_core_risk_source_truth_numeric_cell_accepted_via_caption_only_context`: Verifies `cell_text="180%"` with caption-only context (`table_caption_or_nearby_heading="报告期内股票换手率"`, generic row/column labels) emits `turnover_or_style_drift_risk`.

**Controller re-review:** Initial Finding 1 fix omitted `table.table_caption_or_nearby_heading` from numeric-cell candidate expansion, leaving caption-only role context uncovered. Added in follow-up correction.

## Follow-up Fix: Code Review Gate — Finding 2 (Stale Doc Wording)

Code review identified stale wording in control/design docs that claimed `core_risk.v1` roles remain unimplemented or that current next gate is Implementation Gate.

**Fix:**
- `docs/current-startup-packet.md`: Line 63 updated from `Implementation Gate` + `remain unimplemented` to `Code Review Gate` + five required subvalues implemented + no-readiness boundary.
- `docs/design.md`: Line 1150 updated to state `core_risk.v1` field-family source-truth direct extraction is locally implemented, separated from unproven real-report correctness/readiness.

**Verification:** `rg` no longer hits `remain unimplemented`, stale `Implementation Gate` for this work unit's next-entry, or `未实现的 core_risk.v1` in design.md.

## Validation Outputs (Post Code-Review Fix)

```
uv run pytest tests/fund/processors/test_fund_disclosure_processor.py -q -k core_risk
31 passed, 167 deselected

uv run pytest tests/fund/processors/test_fund_disclosure_processor.py -q
198 passed

uv run pytest tests/fund/test_data_extractor.py -q
43 passed

uv run ruff check ...
All checks passed!

git diff --check -- <changed files>
(no output = clean)
```

## Next Gate

`FundDisclosureDocument core_risk.v1 Deferred Risk Roles Source-truth Direct Extraction Code Review Gate`.
Current: fix after code review + controller re-review completed locally. Stop condition reached — no commit, push, PR, or re-review authorized.
