# FundDisclosureDocument core_risk.v1 Deferred Risk Roles Source-truth Direct Extraction Plan

## Verdict

`PLAN_READY`

Release/readiness remains `NOT_READY`.

## Gate / Work Unit

- Gate: `FundDisclosureDocument core_risk.v1 Deferred Risk Roles Source-truth Direct Extraction Planning Gate`
- Work unit: implement proof-positive source-truth direct extraction for the four remaining `core_risk.v1` roles:
  - `liquidation_or_scale_risk`
  - `tracking_error_or_deviation_risk`
  - `turnover_or_style_drift_risk`
  - `concentration_risk`

## Goal

Advance the larger goal "all FundDisclosureDocument field-family source-truth direct extraction is implemented" by converting the four currently deferred `core_risk.v1` roles from candidate-only/deferred gaps into proof-positive public `core_risk.v1` subvalues when, and only when, the FDD source-truth admission contract is satisfied and a stable direct annual-report disclosure can be selected.

Success signal:

- Proof-positive FDD input can emit `core_risk.v1` public values for all four roles, with public `EvidenceAnchor` entries.
- Missing or ambiguous role-level source truth fails closed into family-local gaps and does not use candidate evidence as source truth.
- `candidate_boundary is None` remains necessary but not sufficient; missing/invalid `FundDisclosureSourceTruthAdmissionProof`, missing provenance, or non-null `failure_class` still produce no public value/anchors.
- Explicit FDD facade continues to avoid `StructuredFundDataBundle.core_risk` and does not project the four risk roles into existing bundle fields.

## Non-goals / Scope Boundary

- Do not claim real-report correctness, full field correctness, parser replacement, readiness, release, golden promotion, or PR 34 readiness/merge.
- Do not run live/network/PDF/FDR/Docling conversion/pdfplumber export/provider/LLM commands.
- Do not extend `EvidenceSourceKind` or `EvidenceAnchor`.
- Do not let Service/UI/Host/renderer/quality-gate/LLM prompt consume FDD candidate evidence directly.
- Do not add `StructuredFundDataBundle.core_risk`.
- Do not use `core_risk.v1` to overwrite existing canonical bundle fields:
  - `tracking_error` remains owned by `return_attribution.v1`.
  - `turnover_rate` remains owned by `manager_profile.v1`.
  - `holdings_snapshot` remains owned by `manager_profile.v1`.
  - `risk_characteristic_text` remains the only allowed `core_risk.v1` facade fallback.

## Current Truth Alignment

- `AGENTS.md` requires structured fund field extraction to go through Fund Processor/Extractor boundaries and forbids direct parser/candidate consumption outside that boundary.
- `docs/design.md` and `docs/current-startup-packet.md` currently record `core_risk.v1` as proof-positive direct extraction for `risk_characteristic_text` only; the four other roles remain candidate/deferred.
- `docs/implementation-control.md` current next entry is this planning gate and forbids parser replacement, PR mutation, readiness/release, source behavior changes, `EvidenceSourceKind` expansion, upper-layer candidate consumption, and live/PDF/provider commands.
- The accepted closeout `docs/reviews/funddisclosuredocument-core-risk-source-truth-extraction-final-closeout-controller-judgment-20260620.md` explicitly leaves the four roles as residuals for this gate and keeps `StructuredFundDataBundle.core_risk` unaccepted.

## Current Code Facts

- `fund_agent/fund/processors/fund_disclosure_processor.py:67-70` defines `_CORE_RISK_DEFERRED_ROLES` as the four roles in this plan.
- `fund_agent/fund/processors/fund_disclosure_processor.py:682-744` defines `_CORE_RISK_MATCH_GROUPS` for the five core-risk candidate roles. These match groups are locator evidence, not source truth.
- `FundDisclosureDocumentProcessor.extract()` runs identity/admission before field-family construction. `_build_field_families()` only enables source-truth extraction when base admission is not blocked and `_validate_source_truth_admission()` returns `None`.
- `_validate_source_truth_admission()` requires a `FundDisclosureSourceTruthAdmissionProof`, `candidate_boundary is None`, `failure_class is None`, `source_provenance is not None`, and exact context/intermediate/proof identity.
- `_extract_core_risk_source_truth()` currently delegates to `_select_core_risk_values()`, `_build_core_risk_value()`, `_core_risk_source_truth_gaps()`, and `_core_risk_status()`.
- `_select_core_risk_values()` currently returns only `_select_risk_characteristic_value()`.
- `_build_core_risk_value()` currently emits only:
  - `schema_version: "core_risk.v1"`
  - `risk_characteristic_text`
- `_core_risk_source_truth_gaps()` currently appends the four deferred roles as `required=False` `deferred_role` gaps only when a value exists.
- `_core_risk_status()` currently returns `accepted` if `risk_characteristic_text` exists, otherwise `missing`.
- `_select_core_risk_candidate_evidence()` scans `sections -> paragraph_blocks -> table_blocks -> cells`, preserves role order, de-dupes by source path, and marks all candidate records as candidate-only/not-proven/not-ready.
- `fund_agent/fund/data_extractor.py:_active_processor_result_to_bundle()` projects `core_risk.v1` only as `risk_characteristic_text` fallback when `product_essence.v1` lacks that field; it does not expose a bundle-level `core_risk`.
- `tests/fund/processors/test_fund_disclosure_processor.py` already asserts:
  - current `core_risk.v1` exact shape contains only `schema_version` and `risk_characteristic_text`;
  - current deferred gaps are the four roles and `required=False`;
  - proof-positive direct missing suppresses candidate evidence;
  - proof missing/invalid/candidate-boundary paths do not emit public values;
  - candidate selector remains candidate-only.
- `tests/fund/test_data_extractor.py` already asserts explicit FDD facade has no `core_risk` attribute and only uses `core_risk.v1` as risk-text fallback.

## First-principles Contract Decision

These roles should enter `core_risk.v1` public field-family value, but only as field-family subvalues.

Reasoning:

- The work unit goal is complete `core_risk.v1` source-truth direct extraction. Keeping the four roles as `deferred_role` gaps after this gate would not advance the family to completion.
- The four roles are Chapter 6 risk disclosure surfaces, so their natural public owner is `core_risk.v1`.
- They are not stable canonical `StructuredFundDataBundle` fields today. Existing bundle fields already have separate owners for overlapping raw metrics. Creating `StructuredFundDataBundle.core_risk` would be a new public bundle contract and is not necessary to complete direct field-family extraction.
- Candidate selector locators are not sufficient. Source-truth public values require direct annual-report disclosure text plus a public `EvidenceAnchor`; section/table heading-only matches remain locator evidence or missing gaps.

## Public Value Shape

`core_risk.v1` should become:

```python
{
    "schema_version": "core_risk.v1",
    "risk_characteristic_text": {
        # existing risk_characteristic_text.v1 shape, unchanged
    },
    "liquidation_or_scale_risk": {
        "schema_version": "core_risk_role_disclosure.v1",
        "fund_code": context.fund_code,
        "report_year": context.document_year,
        "role": "liquidation_or_scale_risk",
        "risk_disclosure_text": "<normalized direct annual-report disclosure>",
    },
    "tracking_error_or_deviation_risk": {
        "schema_version": "core_risk_role_disclosure.v1",
        "fund_code": context.fund_code,
        "report_year": context.document_year,
        "role": "tracking_error_or_deviation_risk",
        "risk_disclosure_text": "<normalized direct annual-report disclosure>",
    },
    "turnover_or_style_drift_risk": {
        "schema_version": "core_risk_role_disclosure.v1",
        "fund_code": context.fund_code,
        "report_year": context.document_year,
        "role": "turnover_or_style_drift_risk",
        "risk_disclosure_text": "<normalized direct annual-report disclosure>",
    },
    "concentration_risk": {
        "schema_version": "core_risk_role_disclosure.v1",
        "fund_code": context.fund_code,
        "report_year": context.document_year,
        "role": "concentration_risk",
        "risk_disclosure_text": "<normalized direct annual-report disclosure>",
    },
}
```

Shape constraints:

- Keep `risk_characteristic_text.v1` unchanged.
- Use the same `core_risk_role_disclosure.v1` subvalue schema for all four roles to avoid four unnecessary near-identical schemas.
- Keep `core_risk_role_disclosure.v1` as a processor-local builder function contract, implemented by `_build_core_risk_role_disclosure_value(...)`; do not add a public dataclass/schema in `contracts.py` unless implementation evidence proves a real consumer need.
- The role subvalue shape is exactly five keys: `schema_version`, `fund_code`, `report_year`, `role`, `risk_disclosure_text`.
- Do not include role-local `source_anchors`. Public anchors live only in `FundFieldFamilyResult.anchors`, consistent with the other FDD field families.
- `risk_disclosure_text` is a direct disclosure excerpt, not a derived risk judgment, not a buy/sell/replace decision, and not a metric recalculation.
- Do not emit pressure tests, max drawdown, veto, risk level, risk summary, final judgment, or market prediction keys.

## Source-truth Role Selection Rules

Use the actual FDD content structure:

- Scan only `intermediate.paragraph_blocks` and `intermediate.table_blocks[*].cells`; `sections` and table-level fields are guard context only.
- Only stable locators can produce public values: paragraph/table/cell `locator_stability` must be `"stable"` on every source object used for the selected value.
- Reuse the four non-`risk_characteristic` entries in `_CORE_RISK_MATCH_GROUPS` as `(role, strong_tokens, generic_tokens, guard_tokens)`.
- Normalize candidate text with the same match-text normalization already used by the processor for token comparison; normalize the emitted `risk_disclosure_text` by trimming, preferring normalized text over raw text, and collapsing whitespace/newlines. Do not do semantic rewriting.

Paragraph candidate rule:

- Candidate text is `paragraph.text_normalized.strip()` if non-empty, otherwise `paragraph.text_raw.strip()`.
- A paragraph qualifies directly when candidate text contains a role-specific `strong_token`.
- A paragraph containing only a `generic_token` qualifies only when guard context contains a same-role `guard_token`; guard context is `paragraph.heading_path` plus the same paragraph text. The generic token alone is not enough.
- A paragraph is heading-only and must be rejected when normalized candidate text equals one token/label/header phrase, has no substantive disclosure sentence, or is only a short structural label such as `跟踪误差`, `换手率`, `持仓集中度`, `基金合同终止`. FDD paragraphs do not expose `heading_level`; therefore heading-only rejection must be text-based for paragraphs.
- A paragraph with heading-path guard and body text is allowed only when the paragraph body itself contains a strong token or a guarded generic token plus substantive disclosure text; heading_path alone cannot authorize public value.

Table/cell candidate rule:

- Candidate text is `cell.cell_text_normalized.strip()` if non-empty, otherwise `cell.cell_text.strip()`.
- Reject a cell if `cell.is_header_cell is True`, or `cell.row_index` is in `table.header_rows`, or `cell.row_index` is not in `table.body_rows` when `body_rows` is non-empty.
- Reject a cell whose candidate text is empty, placeholder-only (`无`, `不适用`, `-`, `—`, `--`, `未披露`, `N/A`), or equals only a row/column/header label.
- A cell qualifies directly when candidate text contains a role-specific `strong_token`.
- A cell containing only a `generic_token` qualifies only when guard context contains a same-role `guard_token`; guard context is `table.heading_text`, `table.table_caption_or_nearby_heading`, `table.heading_path`, `cell.row_label_path`, `cell.column_header_path`, and `cell.heading_path`. The selected cell text still must be substantive.
- Table `heading_text`, `table_caption_or_nearby_heading`, `heading_path`, `row_label_path`, and `column_header_path` can authorize context but cannot be emitted as `risk_disclosure_text` by themselves.

Substantive disclosure rule:

- Substantive text must contain more than a structural label: after normalization it must not equal any matched token, any row/column label, or any generic cell text.
- It should contain at least one of: a clause with explanatory wording, a regulatory threshold/condition, a numeric threshold/ratio, or a risk-process statement. This is a fail-closed rule; uncertain cases stay missing/partial.
- For role-specific examples:
  - `liquidation_or_scale_risk`: accept disclosure text mentioning conditions such as net asset value below 50 million, holder count below 200, continuous 20 working days, contract termination, or liquidation; reject a heading/caption only saying `基金合同终止事由`.
  - `tracking_error_or_deviation_risk`: accept text explaining tracking error/deviation level, control target, cause, or benchmark/index deviation; reject a table header only saying `跟踪误差`.
  - `turnover_or_style_drift_risk`: accept text explaining turnover rate, calculation口径, strategy/style drift/change, or portfolio operation effect; reject a row label only saying `换手率`.
  - `concentration_risk`: accept text/table data cell disclosing holdings/industry/top-ten/asset concentration content; reject captions such as `前十名股票投资明细` unless a body cell supplies substantive disclosure text.

Conflict detection and resolution:

- `_select_core_risk_role_values(...)` returns `tuple[dict[str, _CoreRiskRoleValueCandidate], set[str]]`, where role output paths use the role key itself, for example `liquidation_or_scale_risk`.
- Candidate collection preserves scan order: paragraphs by tuple index, then tables by table index and cells sorted by `(row_index, column_index)`. Do not use candidate evidence records as input.
- `_resolve_core_risk_role_candidate(role, candidates, ambiguous_paths)` must be code-mappable:
  - no candidates -> return `None`;
  - all candidates have the same normalized `risk_disclosure_text` -> return the first candidate in scan order and do not emit ambiguity;
  - candidates have different normalized text -> omit the role and add `role` to `ambiguous_paths`;
  - paragraph-vs-cell with identical normalized text is not ambiguous; paragraph-vs-cell with different normalized text is ambiguous;
  - same-role duplicates from multiple paragraphs/cells are allowed only when normalized text is identical;
  - different roles are resolved independently and never conflict with each other.
- `ambiguous_table_or_locator` is emitted only for a role in `ambiguous_paths`, with `source_field_path=<role>`, `required=True`, and the role omitted from `value`.
- `EvidenceAnchor.row_locator` for role anchors must include the role key and source path consistently:
  - paragraph: `field=<role>; source=paragraph_blocks[<index>]; block_id=<block_id>`
  - cell: `field=<role>; source=table_blocks[<table_index>].cells[<cell_index>]; table_id=<table_id>; row=<row_index>; column=<column_index>; cell_id=<cell_id>`

## Anchor / Gap Semantics

Anchor semantics:

- Every emitted role must contribute one public `EvidenceAnchor` to `FundFieldFamilyResult.anchors`.
- Role subvalues must not embed anchors; `FundFieldFamilyResult.anchors` is the only public anchor carrier.
- Anchor `source_kind` remains `annual_report`; no `EvidenceSourceKind` expansion.
- Allowed direct sources:
  - paragraph text with role-specific strong token or generic token plus source-level guard context;
  - table cell text with role-specific strong token or generic token plus table/row/column/heading guard context;
  - table row or cell value where the selected disclosure text is substantive, not only a generic heading.
- Disallowed direct sources:
  - section-only heading matches;
  - table-only heading/caption matches with no substantive row/cell disclosure;
  - candidate evidence excerpts;
  - inferred risk labels from unrelated fields;
  - derived calculations from NAV, holdings, tracking-error series, turnover formula, or external data.

Gap semantics:

- Rename/replace `_CORE_RISK_DEFERRED_ROLES` with required top-level semantics, for example `_CORE_RISK_REQUIRED_TOP_LEVEL = ("risk_characteristic_text", "liquidation_or_scale_risk", "tracking_error_or_deviation_risk", "turnover_or_style_drift_risk", "concentration_risk")`.
- Remove `deferred_role` gap emission from the source-truth path. `deferred_role` is not in `FundExtractionGapCode` and should not be expanded.
- If no `core_risk.v1` subvalue is emitted and no ambiguity exists, emit one `field_family_missing` gap with `required=True`.
- If at least one subvalue is emitted but one or more required top-level roles are missing, emit `field_family_partial` for each missing top-level key with `required=True`.
- If a role has conflicting stable candidates, omit that role and emit `ambiguous_table_or_locator` with `source_field_path=<role>`.
- A role missing because the FDD representation only has a section/table locator remains missing/partial; do not promote the locator text.
- Proof-missing/invalid paths should continue to preserve candidate evidence and append source-truth admission gaps.
- Proof-positive direct paths should continue to suppress candidate evidence, including when the result is missing/partial.

Status semantics:

- `accepted`: all five required top-level subvalues are present.
- `partial`: at least one required top-level subvalue is present, but not all.
- `missing`: no subvalues are present.

This intentionally changes the current "risk text only => accepted" behavior to "risk text only => partial" once the four roles are promoted from deferred to required.

## Implementation Plan

### Slice 1: core_risk role source-truth extraction

Allowed files:

- `fund_agent/fund/processors/fund_disclosure_processor.py`
- `tests/fund/processors/test_fund_disclosure_processor.py`

Changes:

- Add a private value-candidate dataclass, for example `_CoreRiskRoleValueCandidate`, with:
  - `output_path: str`
  - `role: str`
  - `value: str`
  - `anchor: EvidenceAnchor`
  - `source_field_path: str`
- Add a local union alias near the candidate dataclasses:
  - `_CoreRiskValueCandidate = _RiskCharacteristicValueCandidate | _CoreRiskRoleValueCandidate`
- Change `_select_core_risk_values()` to merge:
  - existing `_select_risk_characteristic_value()`;
  - new role text candidates for the four roles.
- Update affected signatures explicitly:
  - `_select_core_risk_values(...) -> tuple[dict[str, _CoreRiskValueCandidate], set[str]]`
  - `_select_core_risk_role_values(...) -> tuple[dict[str, _CoreRiskRoleValueCandidate], set[str]]`
  - `_build_core_risk_value(selected_values: dict[str, _CoreRiskValueCandidate], context: FundProcessorDispatchKey) -> dict[str, object]`
  - `_core_risk_emitted_output_paths(value: dict[str, object], selected_values: dict[str, _CoreRiskValueCandidate]) -> tuple[str, ...]`
  - `_core_risk_source_truth_gaps(value: dict[str, object], ambiguous_paths: set[str]) -> tuple[FundExtractionGap, ...]`
- Add helper functions:
  - `_select_core_risk_role_values(intermediate, context) -> tuple[dict[str, _CoreRiskRoleValueCandidate], set[str]]`
  - `_collect_core_risk_role_paragraph_candidates(...)`
  - `_collect_core_risk_role_cell_candidates(...)`
  - `_core_risk_role_anchor(...)`
  - `_core_risk_role_text_value(...)`
  - `_resolve_core_risk_role_candidate(...)`
  - `_build_core_risk_role_disclosure_value(...)`
- Reuse `_CORE_RISK_MATCH_GROUPS` for token/guard definitions but skip `risk_characteristic`.
- Do not reuse `_select_core_risk_candidate_evidence()` output as source-truth input. The role source-truth helpers can reuse the same tokens and scan order, but must build public values from direct paragraph/cell sources.
- Keep section/table heading matches as guard/locator context only; they cannot produce public role values by themselves.
- Update `_build_core_risk_value()` to include the four role keys when selected.
- `_build_core_risk_value()` must dispatch by type:
  - `_RiskCharacteristicValueCandidate` -> existing `_build_risk_characteristic_text_value(...)` under top-level key `risk_characteristic_text`;
  - `_CoreRiskRoleValueCandidate` -> `_build_core_risk_role_disclosure_value(...)` under top-level key equal to `candidate.role`;
  - unexpected candidate type is a programming error and should not be silently ignored.
- `_core_risk_emitted_output_paths()` must return only paths whose corresponding top-level keys are present in `value`; role paths are the role keys themselves. Pseudocode:
  - start with `risk_characteristic_text.risk_characteristic_text` if `risk_characteristic_text` is present and selected;
  - for each role in the four role keys, append the role key if `role in value and role in selected_values`;
  - return the tuple in required top-level order.
- Update `_core_risk_source_truth_gaps()` to use required top-level partial/missing semantics and remove `deferred_role`.
- Update `_core_risk_status()` to accepted/partial/missing based on required top-level completeness.
- Preserve all existing source-truth admission behavior.

Expected tests:

- Replace `test_core_risk_source_truth_extracts_risk_characteristic_text_only` with an exact-shape test that supplies one stable paragraph/cell source for each of the four roles and asserts:
  - `status == "accepted"`;
  - `extraction_mode == "direct"`;
  - value keys are exactly `schema_version`, `risk_characteristic_text`, and the four role keys;
  - each role subvalue matches the exact `core_risk_role_disclosure.v1` shape;
  - no role subvalue contains `source_anchors` or any other anchor-like key;
  - all family anchors use `annual_report`;
  - role anchor `row_locator` contains the role key and concrete source path;
  - no `deferred_role` gaps exist;
  - `candidate_evidence == ()`.
- Add/update a test for risk-text-only direct input:
  - `status == "partial"`;
  - value contains `schema_version` and `risk_characteristic_text`;
  - gaps contain `field_family_partial` for the four role keys with `required=True`.
- Add one missing/direct suppress test:
  - proof-positive FDD with only section/table locator headings for the four roles returns `missing` or `partial` as applicable and `candidate_evidence == ()`.
- Add ambiguity tests:
  - conflicting disclosures for one role omit that role and produce `ambiguous_table_or_locator`.
  - paragraph and cell candidates with identical normalized text for the same role choose the first scan-order candidate and do not emit ambiguity.
- Add structural boundary tests:
  - paragraph heading-path-only guard without substantive paragraph body does not emit a role value;
  - `is_header_cell=True` or `row_index in table.header_rows` does not emit a role value;
  - table caption/header/row label alone does not emit `risk_disclosure_text`;
  - generic token requires same-role guard context and substantive cell/paragraph text.
- Grep and update all tests that assert `core_risk.status == "accepted"` or exact risk-text-only shape. Required grep patterns:
  - `rg -n 'core_risk\\.status == "accepted"|set\\(core_risk\\.value\\) == \\{"schema_version", "risk_characteristic_text"\\}|set\\(value\\) == \\{"schema_version", "risk_characteristic_text"\\}' tests/fund/processors/test_fund_disclosure_processor.py tests/fund/test_data_extractor.py`
  - At minimum update `test_product_essence_source_truth_extracts_minimal_shape`, `test_investor_experience_source_truth_does_not_pollute_stage_or_core_risk`, and `test_core_risk_source_truth_extracts_risk_characteristic_text_only`.
- Keep/update existing tests for:
  - proof missing;
  - invalid proof;
  - candidate boundary blocked;
  - direct route never leaks candidate evidence;
  - S6-F candidate selector still produces candidate-only records in non-proof paths.

### Slice 2: facade no-projection guard

Allowed files:

- `tests/fund/test_data_extractor.py`
- `fund_agent/fund/data_extractor.py` only if an existing projection path accidentally starts consuming role keys.

Decision:

- No planned production change in `data_extractor.py`.
- Keep `_active_processor_result_to_bundle()` behavior unchanged: `core_risk.v1` can only fallback `risk_characteristic_text`.

Expected tests:

- Extend `test_explicit_disclosure_core_risk_fallback_projects_risk_text_only` or add a neighboring test where the custom processor emits all four role keys under `core_risk.v1`; assert:
  - `not hasattr(bundle, "core_risk")`;
  - `bundle.risk_characteristic_text` fallback still works only for `risk_characteristic_text`;
  - `bundle.tracking_error`, `bundle.turnover_rate`, and `bundle.holdings_snapshot` are not populated from `core_risk.v1`;
  - no role key appears as a bundle field.

### Slice 3: documentation/control sync after implementation acceptance

Allowed files only when explicitly authorized by the downstream gate:

- `docs/design.md`
- `fund_agent/fund/README.md`
- `docs/implementation-control.md`
- `docs/current-startup-packet.md`
- downstream review/evidence artifacts

Decision:

- This plan gate does not edit docs/control files beyond this artifact.
- Implementation should not claim docs sync complete unless the downstream gate explicitly authorizes those files.
- Once implementation is accepted, docs/control must replace the current "four roles deferred" wording with the accepted public field-family-only boundary and preserve the no-bundle/no-readiness/no-parser-replacement constraints.

## Validation Commands

Proposed only; do not run in this planning gate.

```bash
uv run pytest tests/fund/processors/test_fund_disclosure_processor.py -q
uv run pytest tests/fund/processors/test_fund_disclosure_processor.py -q -k core_risk
uv run pytest tests/fund/test_data_extractor.py -q
uv run ruff check fund_agent/fund/processors/fund_disclosure_processor.py fund_agent/fund/data_extractor.py tests/fund/processors/test_fund_disclosure_processor.py tests/fund/test_data_extractor.py
git diff --check -- fund_agent/fund/processors/fund_disclosure_processor.py fund_agent/fund/data_extractor.py tests/fund/processors/test_fund_disclosure_processor.py tests/fund/test_data_extractor.py
```

Expected outcomes:

- Processor tests pass.
- Focused `core_risk` tests prove exact value shape, partial/missing/ambiguity behavior, admission fail-closed behavior, and candidate-only preservation.
- Data extractor tests prove no `StructuredFundDataBundle.core_risk` and no accidental role projection.
- Ruff and diff-check pass.

## Risks / Residuals

| Risk | Disposition |
|---|---|
| Role direct extraction from broad tokens could promote locator-only text | Covered by Slice 1 source rules and tests: section/table heading-only remains non-public |
| Tracking/turnover/concentration overlap with existing bundle fields | Covered by field-family-only contract and Slice 2 no-projection tests |
| `risk_characteristic_text` current accepted status changes to partial when other roles are missing | Accepted contract change in this work unit because deferred roles become required public subvalues |
| Real-report correctness remains unproven | Assigned to separate evidence/readiness gates |
| Parser/document representation quality remains unproven | Assigned to Fund documents evidence owner; not part of this work unit |
| Docs/control truth will be stale after implementation if not synced | Must be handled by downstream implementation/docs-sync gate when authorized |
| PR 34 state remains draft/open | Controller/user disposition gate; not part of this plan |

## Stop Conditions

Stop and report `BLOCKED` instead of implementing if:

- A role cannot be extracted from direct paragraph/cell disclosure without relying on candidate evidence or heading-only locators.
- Implementing the role requires new public `EvidenceSourceKind`, `EvidenceAnchor` schema, `StructuredFundDataBundle.core_risk`, repository/source behavior changes, live/PDF/provider/LLM execution, or Service/UI/Host/renderer/quality-gate consumption.
- Tests require deriving risk judgments, pressure tests, max drawdown, final recommendation, or market forecasts from the role text.
- Proof-missing, invalid-proof, missing-provenance, non-null `failure_class`, or `candidate_boundary` paths would need to emit public values/anchors.
- Existing return_attribution/manager_profile bundle ownership would need to be changed to make the roles pass.

## Completion Report Format

Downstream implementation completion should report:

- verdict;
- changed files;
- exact public `core_risk.v1` value shape implemented;
- admission/fail-closed behavior summary;
- facade/bundle decision;
- validation command outputs;
- residual risks and next gate.

## Artifact

`docs/reviews/funddisclosuredocument-core-risk-deferred-roles-source-truth-extraction-plan-20260620.md`
