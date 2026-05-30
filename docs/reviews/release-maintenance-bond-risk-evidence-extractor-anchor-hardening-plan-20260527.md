# Bond Risk Evidence Extractor / Anchor Hardening Plan

> Date: 2026-05-27
> Role: planning worker
> Gate: `bond risk evidence extractor / anchor hardening design gate`
> Work unit: `bond risk evidence extractor / anchor hardening design gate`
> Status: handoff-ready
> Blocking questions: none

## Worker Self-Check

### Before Start

- Self-check: pass
- Role confirmed: planning worker only, not controller.
- Current gate confirmed: plan gate for positive `bond_risk_evidence.v1` records and stable group-level anchors.
- External-state boundary confirmed: no workflow command, no skill, no implementation, no review, no staging, no commit, no PR, no golden promotion.
- Dirty scope confirmed before writing: only pre-existing untracked `--help`, repo/comprehensive review artifacts, and `docs/tmux-agent-memory-store.md`; this plan writes only the newly requested artifact path.

### Before File Edit

- Self-check: pass
- Allowed write path confirmed: `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-plan-20260527.md`.
- This artifact is newly created and does not touch unrelated untracked files.
- Plan scope remains code-generation-ready planning only.

### Before Completion

- Self-check: pass
- This artifact contains source-of-truth evidence, contract decisions, implementation slices, tests, validation matrix, review gates, risks, and completion report format.
- No blocking schema/contract option remains unresolved.

## Goal And Motivation

Goal: define and implement positive `bond_risk_evidence.v1` records plus stable group-level annual-report evidence anchors so that `006597` / `2024`, when real annual-report evidence satisfies the contract, no longer emits blocking `bond_risk_evidence_missing.baseline_blocking=true`.

Root cause: current scoring already excludes equity-style `holdings_snapshot` from bond-fund quality denominators, but it has no positive replacement record contract. Therefore exact `bond_fund` rows conservatively emit an aggregate `bond_risk_evidence_missing` issue for all seven groups, even when same-fund/year annual-report evidence exists.

First-principles decision: the fix must make the real evidence first-class and checkable. It must not lower thresholds, suppress issues, or treat missing evidence as pass.

## Non-Goals And Scope

In scope:

- Define `bond_risk_evidence.v1` schema and stable anchor contract.
- Extract positive bond-risk evidence from the already repository-loaded `ParsedAnnualReport`.
- Add `bond_risk_evidence` to the structured bundle and extraction snapshot as a field-level record.
- Update score applicability logic so the existing missing issue is emitted only for unsatisfied required groups.
- Add tests for complete, missing, weak, ambiguous, anchor-missing, and real `006597` positive paths.

Out of scope:

- No FQ0-FQ6 weakening, threshold lowering, severity remapping, or quality-gate bypass.
- No direct PDF/cache/source-helper access outside `FundDocumentRepository`.
- No conversion of missing evidence into pass.
- No representation of qualitative text as strong quantitative evidence.
- No golden corpus promotion, baseline fixture promotion, release readiness, PR, push, merge, or GitHub mutation.
- No QDII, FOF, `110020`, Host/Agent/dayu, renderer rewrite, LLM audit, Evidence Confirm, or report-quality replacement work.
- No hidden `extra_payload`; every new parameter or field must be explicit.

## Direct Evidence From Source Of Truth

### `AGENTS.md`

- `AGENTS.md` is the repository execution rule source and requires Chinese responses, first-principles reasoning, same-source root-cause evidence, and traceable numerical evidence.
- Production annual-report/PDF access must go through `FundDocumentRepository`; Service, UI, Host, renderer, and quality gate must not directly call concrete source, PDF cache, or download helpers.
- Source fallback must stay fail-closed for `schema_drift`, `identity_mismatch`, and `integrity_error`; only `not_found` / `unavailable` are fallback-eligible.
- Architecture boundary is `UI -> Service -> Host -> Agent`; current deterministic path is UI -> Service -> `fund_agent/fund`.
- Explicit parameters are mandatory; no explicit business parameters may be hidden in `extra_payload`.
- Fund type must be resolved before applying `preferred_lens`; bond analysis must use bond-lens evidence.
- Tests must move with implementation boundaries and fund-analysis tests must cover template completeness, evidence anchor format, and audit/rule triggering.

### `docs/design.md`

- Current product path is deterministic MVP: UI CLI calls Service; Service calls `fund_agent/fund`; `FundDataExtractor` loads reports via `FundDocumentRepository`.
- Current architecture remains `UI -> Service -> Host -> Agent`; Host/Agent packages are not current production facts, and future Host/Agent work must use `dayu.host` / `dayu.engine`.
- The current field order is `basic_identity` through `nav_data`; quality gate rules are FQ0-FQ6 and must not be replaced by report-quality scoring.
- `FQ2F` projects score-applicability issues, including current bond replacement issues.
- `FQ5` proves template contract applicability only; it does not prove renderer semantic compliance.
- Bond preferred lens emphasizes credit risk, duration, and max drawdown; broader report-quality design identifies `bond_fund` risk evidence as duration, credit, leverage, liquidity, and downside experience.
- `FundAnalysisService` may run quality gate from an already extracted bundle; quality gate must not reread PDF/cache/documents.

### `docs/implementation-control.md`

- Current phase is `release maintenance`; current accepted state is bond positive-risk evidence accepted locally.
- Next entry point is this design gate for positive `bond_risk_evidence.v1` records and durable anchors.
- Current implementation remains UI -> Service -> `fund_agent/fund`; no Host/Agent package should be introduced in this gate.
- `006597` / `2024` annual report contains same-fund/year candidate evidence for all seven groups, but current public CLI/score cannot express positive records or durable group-level anchors.
- `bond_risk_evidence_missing.baseline_blocking=true` must remain until a reviewed extractor/anchor gate resolves it.
- Golden corpus v1 remains blocked and must not be entered here.

### `docs/reviews/repo-review-20260527-225303.md`

- Repository-wide audit found deterministic MVP runnable with `ruff`, full `pytest`, real network/PDF smoke, product `analyze`, and `golden-build` passing.
- Main high finding: `006597` is not blocked because `golden-build` fails; it is blocked because positive `bond_risk_evidence.v1` records and stable anchors are absent.
- The current score path defines all seven bond groups with `baseline_blocking=True` and emits `bond_risk_evidence_missing` for exact `bond_fund`.
- `quality_gate.status=warn` can coexist with baseline/golden blocked because baseline blocking is currently represented in score applicability, not as an executable golden-readiness gate.
- Recommended next step is this bond extractor/anchor gate, not rerunning golden-build.

### `docs/reviews/release-maintenance-bond-positive-risk-evidence-20260527.md`

- Public CLI run for `006597` / `2024` succeeded, produced empty `errors.jsonl`, classified the fund as `bond_fund`, and still emitted `bond_risk_evidence_missing` with all seven groups missing.
- Repository inspection used `FundDocumentRepository().load_annual_report("006597", 2024)` and did not use direct PDF/cache/source helpers.
- Candidate same-fund/year annual-report evidence exists for all seven groups:
  - `duration_rate_risk`: duration strategy, short-duration allocation, interest-rate risk management by duration adjustment.
  - `credit_risk`: credit-bond strategy, medium-high-grade positioning, credit-risk control, rating distributions.
  - `leverage_liquidity`: flexible leverage strategy and liquidity-risk control text, plus portfolio/repo-related locators needing precise normalization.
  - `asset_allocation_holdings_mix`: fixed-income allocation, bond/ABS/cash-like allocation, bond category mix, top bonds, top ABS.
  - `drawdown_stress`: qualitative drawdown-control intent; no max drawdown or volatility metric currently extracted.
  - `redemption_share_pressure`: holder structure and multi-share-class share-change/subscription/redemption tables.
  - `convertible_bond_equity_exposure`: explicit no equity/stock and no convertible/exchangeable bond holdings.
- Final evidence state is extractor/evidence-anchor issue, not data gap.

### `docs/reviews/release-maintenance-bond-positive-risk-evidence-controller-judgment-20260527.md`

- Controller accepted the evidence artifact locally.
- Findings accepted as future-gate constraints:
  - `drawdown_stress` qualitative control intent must not be treated as max drawdown / volatility.
  - `leverage_liquidity` qualitative strategy text must not be treated as quantitative leverage or repo borrowing evidence without an accepted rule.
  - precise page/table/row anchors are required before leverage/liquidity evidence is consumed.
  - evidence-strength distinctions must be preserved.
  - multi-share-class selection issue is an extraction/normalization concern, not disclosure absence.
- Next recommended cursor is this scoped design gate, not golden promotion.

## Current Code Evidence

- `fund_agent/fund/extraction_score.py` defines:
  - `BOND_RISK_EVIDENCE_CONTRACT_ID = "bond_risk_evidence.v1"`
  - `BOND_RISK_REPLACEMENT_FIELD_NAME = "bond_risk_evidence"`
  - `BOND_RISK_EVIDENCE_GROUPS` with seven required groups, all `baseline_blocking=True`.
  - `derive_score_applicability_issues(...)`, which currently emits one aggregate missing issue for exact `bond_fund` whenever the bond holdings replacement applies.
  - `_bond_risk_evidence_missing_issue(...)`, which sets `missing_evidence_groups` to all seven group ids.
- `fund_agent/fund/data_extractor.py` currently builds `StructuredFundDataBundle` from profile, performance, manager/ownership, holdings/share-change, nav data, and source provenance; it has no `bond_risk_evidence` field.
- `fund_agent/fund/extraction_snapshot.py` currently serializes one first anchor per field into snapshot rows. It has no explicit multi-anchor group contract for `bond_risk_evidence`.
- Existing extractor anchor model is `EvidenceAnchor(source_kind, document_year, section_id, page_number, table_id, row_locator, note)` in `fund_agent/fund/extractors/models.py`.

## Contract Decision: `bond_risk_evidence.v1`

### Record Scope

`bond_risk_evidence.v1` is a fund-level, report-year-level, bond-only replacement evidence contract for exact `bond_fund`. It replaces the equity-stock interpretation of `holdings_snapshot` for bond-lens risk adequacy. It does not replace FQ0-FQ6 and does not make a fund baseline/golden-ready by itself.

### Field Placement

Add a new explicit structured field:

- `StructuredFundDataBundle.bond_risk_evidence: ExtractedField[BondRiskEvidenceValue]`
- Snapshot field row:
  - `field_group = "risk"`
  - `field_name = "bond_risk_evidence"`
  - `extraction_mode = "direct"` when every required group has accepted positive or accepted explicit absence evidence.
  - `extraction_mode = "partial"` when at least one group has usable evidence but one or more required groups remain missing/weak/ambiguous.
  - `extraction_mode = "missing"` when no group satisfies the contract.

Do not put this under `extra_payload` or free-form notes only.

### Type Model

Add dataclasses in `fund_agent/fund/extractors/models.py`:

- `BondRiskEvidenceStatus = Literal["accepted", "accepted_absence", "weak", "ambiguous", "missing"]`
- `BondRiskEvidenceStrength = Literal["quantitative_direct", "quantitative_absence", "qualitative_direct", "qualitative_control_intent", "ambiguous", "missing"]`
- `BondRiskEvidenceGroupId = Literal["duration_rate_risk", "credit_risk", "leverage_liquidity", "asset_allocation_holdings_mix", "drawdown_stress", "redemption_share_pressure", "convertible_bond_equity_exposure"]`
- `BondRiskEvidenceAnchorRef`
  - `anchor_id: str`
  - `section_id: str`
  - `page_number: int | None`
  - `table_id: str | None`
  - `row_locator: str`
  - `evidence_role: str`
- `BondRiskEvidenceGroupRecord`
  - `group_id: BondRiskEvidenceGroupId`
  - `status: BondRiskEvidenceStatus`
  - `strength: BondRiskEvidenceStrength`
  - `summary: str`
  - `measurement_kind: Literal["actual_metric", "actual_exposure", "explicit_absence", "risk_disclosure", "strategy_text", "control_intent", "not_found"]`
  - `metric_name: str | None`
  - `metric_value: str | None`
  - `metric_unit: str | None`
  - `period_label: str | None`
  - `source_anchor_ids: tuple[str, ...]`
  - `na_reason: str | None`
  - `reviewer_note: str | None`
- `BondRiskEvidenceValue`
  - `schema_version: Literal["bond_risk_evidence.v1"]`
  - `contract_id: Literal["bond_risk_evidence.v1"]`
  - `fund_code: str`
  - `report_year: int`
  - `groups: tuple[BondRiskEvidenceGroupRecord, ...]`
  - `anchors: tuple[BondRiskEvidenceAnchorRef, ...]`
  - `satisfied_group_ids: tuple[BondRiskEvidenceGroupId, ...]`
  - `missing_group_ids: tuple[BondRiskEvidenceGroupId, ...]`
  - `weak_group_ids: tuple[BondRiskEvidenceGroupId, ...]`
  - `ambiguous_group_ids: tuple[BondRiskEvidenceGroupId, ...]`
  - `contract_status: Literal["satisfied", "partial", "missing"]`

### Anchor Format

Stable group-level anchor id format:

`bond-risk:<fund_code>:<report_year>:<group_id>:<ordinal>`

Rules:

- `fund_code`, `report_year`, and `group_id` are mandatory.
- `ordinal` is deterministic within each group, starting from `1`, ordered by `(section_id, page_number, table_id, row_locator, evidence_role)`.
- Each accepted or weak group record must have at least one `source_anchor_id` that resolves to `BondRiskEvidenceValue.anchors`.
- Each anchor must map to an extractor `EvidenceAnchor` with `source_kind="annual_report"` and same `document_year`.
- Accepted table evidence should include `section_id`, `page_number`, `table_id`, and non-empty `row_locator`.
- Text evidence may have `table_id=None` but must include `section_id`, `page_number` when available, non-empty `row_locator`, and a short note.
- Anchor-missing accepted groups are invalid and must be downgraded to `missing` or raise a local contract validation error in tests, depending on call path.

### Evidence Satisfaction Rules

A group is satisfied only when:

- `status in {"accepted", "accepted_absence"}`
- `strength` is compatible with the group rule below.
- at least one resolvable annual-report anchor exists.

`weak`, `ambiguous`, and `missing` do not satisfy required groups and keep the missing issue active for those groups. Weak evidence remains observable but is not silently promoted to pass.

## Seven Group Decisions For `006597` / `2024`

### 1. `duration_rate_risk`

Accepted evidence:

- Product strategy and manager text mention duration strategy and short-duration allocation.
- Risk disclosure mentions interest-rate risk management by duration adjustment.

Required output:

- `status="accepted"`
- `strength="qualitative_direct"` unless a quantitative duration / average remaining term table is extracted later.
- `measurement_kind="risk_disclosure"` or `strategy_text`.
- Anchors from `§2`, `§4`, and/or financial-statement risk section are acceptable if precise.

### 2. `credit_risk`

Accepted evidence:

- Medium-high-grade credit strategy and strict credit-risk control.
- Rating distribution tables for short-term bonds, long-term bonds, ABS, and similar instruments.

Required output:

- `status="accepted"`
- Prefer `strength="quantitative_direct"` when rating distribution table rows are captured.
- `measurement_kind="actual_exposure"` for rating-distribution tables.
- Qualitative strategy text alone may be emitted as weak support but should not be the only accepted evidence if rating tables exist.

### 3. `leverage_liquidity`

Decision: split the group internally into evidence roles, while keeping one public group id.

Roles:

- `leverage_strategy_text`: flexible leverage strategy text; qualitative only.
- `repo_or_financing_exposure`: actual repo/financing table data; quantitative if captured.
- `liquidity_risk_disclosure`: liquidity-risk disclosure/control text.
- `liquidity_pressure_proxy`: buy-back resale financial assets or holder concentration if used as proxy, with explicit role.

Satisfaction rule:

- Accepted if at least one actual leverage/repo/liquidity-risk data anchor exists, or if precise liquidity-risk disclosure plus portfolio liquidity proxy exists.
- Flexible leverage strategy text alone must be `weak` and must not satisfy the group.

For `006597`, implementation must normalize precise table/row anchors before treating this group as accepted. If only broad page or text strategy evidence is found, this group remains weak and keeps the blocker.

### 4. `asset_allocation_holdings_mix`

Accepted evidence:

- Asset allocation table.
- Bond category mix table.
- Top five bonds and top ABS holdings.

Required output:

- `status="accepted"`
- `strength="quantitative_direct"`
- `measurement_kind="actual_exposure"`
- Table anchors required.

### 5. `drawdown_stress`

Decision: qualitative drawdown-control text is observable but not equivalent to max drawdown / volatility.

Roles:

- `drawdown_control_intent`: manager text such as controlling drawdown.
- `max_drawdown_metric`: actual or calculated max drawdown.
- `volatility_metric`: actual or calculated volatility.
- `stress_threshold_status`: explicit pressure-test result.

Satisfaction rule for this implementation slice:

- `drawdown_control_intent` alone is `status="weak"`, `strength="qualitative_control_intent"`, and does not satisfy the required group.
- The group is accepted only with `max_drawdown_metric`, `volatility_metric`, or an accepted direct stress metric with anchors.
- Because the current accepted evidence only proves qualitative control intent for `006597`, the implementation must either:
  - extract/calculate max drawdown or volatility from explicitly authorized input with source anchors, or
  - keep `drawdown_stress` in `weak_group_ids` and keep `bond_risk_evidence_missing` active for this group.

No blocking question is needed because the safe option is selected: weak qualitative drawdown text is not enough.

### 6. `redemption_share_pressure`

Accepted evidence:

- Holder structure table for share class and combined classes.
- Multi-share-class share change table with beginning shares, subscriptions, redemptions, and ending shares.

Required output:

- `status="accepted"` only when share-class selection is deterministic for the target fund code or when all-class aggregation is explicitly labelled.
- `strength="quantitative_direct"`
- `measurement_kind="actual_exposure"`
- Include role anchors:
  - `holder_structure`
  - `share_beginning`
  - `subscription`
  - `redemption`
  - `share_ending`
  - optional `all_classes_total`
- Ambiguous class selection must produce `status="ambiguous"` and must not satisfy the group.

For `006597`, target A share selection can use same-report §2 subordinate fund code/name evidence plus §10 share-change columns. All-class combined data must be labelled separately and not confused with A share.

### 7. `convertible_bond_equity_exposure`

Accepted evidence:

- Asset allocation table explicitly shows equity/stock as `-`.
- Bond category mix explicitly shows convertible/exchangeable bonds as `-`.

Required output:

- `status="accepted_absence"`
- `strength="quantitative_absence"`
- `measurement_kind="explicit_absence"`
- Table anchors required for both equity/stock absence and convertible/exchangeable bond absence when available.

## Affected Files And Modules

Implementation should be limited to:

- `fund_agent/fund/extractors/models.py`
- `fund_agent/fund/extractors/bond_risk_evidence.py` (new)
- `fund_agent/fund/extractors/__init__.py`
- `fund_agent/fund/data_extractor.py`
- `fund_agent/fund/extraction_snapshot.py`
- `fund_agent/fund/extraction_score.py`
- `tests/fund/extractors/test_bond_risk_evidence.py` (new)
- `tests/fund/test_data_extractor.py`
- `tests/fund/test_extraction_snapshot.py`
- `tests/fund/test_extraction_score.py`
- `tests/fund/test_quality_gate.py` only if serialization/projection expectations need update; do not change FQ0-FQ6 semantics.
- `fund_agent/fund/README.md` after code passes, to document current Fund package contract.
- `tests/README.md` if new test category or command expectations change.

Do not edit:

- `fund_agent/ui/`
- `fund_agent/services/`
- `fund_agent/host/`
- `fund_agent/agent/`
- production source orchestration / concrete PDF/cache/download helpers
- golden answer fixtures
- baseline fixtures
- QDII / FOF / `110020` artifacts

## Public Interface And Schema Changes

### `StructuredFundDataBundle`

Add explicit field:

`bond_risk_evidence: ExtractedField[BondRiskEvidenceValue]`

This is a public Python model change inside Fund Agent-layer capability. It remains internal to current deterministic pipeline and does not add UI/Service params.

### Snapshot JSONL

Add one field-level row:

- `field_group="risk"`
- `field_name="bond_risk_evidence"`
- `value_present=True` only when `contract_status` is `satisfied` or `partial` with at least one observed group.
- `anchor_present=True` only when the field has at least one stable group-level anchor.
- Register `bond_risk_evidence` in `FIELD_PRIORITY_BY_NAME` as `P1`, matching the replacement role currently held by `holdings_snapshot` for bond-fund risk adequacy.
- Coverage semantics for this field: `value_present=True` means `contract_status != "missing"`; absent, malformed, or missing-contract values are not present.
- Traceability semantics for this field: `anchor_present=True` requires at least one stable group-level anchor resolving to annual-report evidence.
- Complete `006597` / `2024` with all seven groups satisfied must produce 100% P1 coverage and 100% P1 traceability for `bond_risk_evidence`.
- `section_id/page/table_id/row_id` may continue to expose the first anchor for backward shape consistency.
- `comparable_values={}` for v1; do not add to golden correctness denominator in this gate.
- `note` must include stable summary tokens:
  - `contract_id=bond_risk_evidence.v1`
  - `contract_status=<satisfied|partial|missing>`
  - `satisfied_groups=...`
  - `missing_groups=...`
  - `weak_groups=...`
  - `ambiguous_groups=...`

### Score JSON

`score_applicability_issues` behavior changes as follows:

- If exact `bond_fund` has no usable `bond_risk_evidence` record, keep current aggregate issue with all seven `missing_evidence_groups`.
- If `bond_risk_evidence.contract_status="satisfied"` and all seven groups are satisfied, emit no `bond_risk_evidence_missing` issue.
- If some groups remain missing/weak/ambiguous, emit `bond_risk_evidence_missing` with only those unsatisfied groups in `missing_evidence_groups`.
- `baseline_blocking` stays `True` for any emitted bond risk missing issue.
- `required_evidence_groups` is a contract-level invariant and must always equal all seven `BOND_RISK_EVIDENCE_GROUPS` ids.
- `missing_evidence_groups` is instance-level dynamic state and must contain only currently unsatisfied group ids.
- Do not shrink `required_evidence_groups` to match `missing_evidence_groups`.
- `field_name` should remain `holdings_snapshot` for backward continuity of the replacement decision, while `replacement_field_name="bond_risk_evidence"` points to the positive record.

### Quality Gate

No FQ0-FQ6 semantic change. Existing quality-gate projection naturally sees fewer or no score-applicability issues after score logic changes. Do not add special-case pass logic in quality gate.

## Implementation Decisions

1. Positive evidence is extracted in `fund_agent/fund/extractors/bond_risk_evidence.py`, not in scoring. Scoring must consume snapshot facts, not reread annual reports.
2. The extractor consumes `ParsedAnnualReport` already loaded through `FundDocumentRepository` by `FundDataExtractor`.
3. The extractor must receive `classified_fund_type` explicitly. For non-`bond_fund`, it returns a missing/not-applicable field immediately and must not scan seven bond evidence groups.
4. Use existing `EvidenceAnchor` for extraction-level anchors and add group-level anchor ids inside `BondRiskEvidenceValue`.
5. Do not use broad page ranges for accepted table-backed evidence; accepted table evidence needs row-level locator.
6. Drawdown text is weak unless backed by a metric.
7. Leverage strategy text is weak unless paired with actual repo/leverage/liquidity data or precise liquidity-risk disclosure and proxy.
8. Explicit absence can be positive evidence for convertible/equity exposure when the annual report table explicitly shows absence.
9. Keep `bond_risk_evidence` out of comparable golden correctness in this gate.

## Implementation Slices

### Slice 1: Model Contract

Allowed files:

- `fund_agent/fund/extractors/models.py`
- `tests/fund/extractors/test_bond_risk_evidence.py`

Changes:

- Add `BondRiskEvidence*` Literal aliases and dataclasses listed above.
- Ensure docstrings are Chinese and reference template第6章核心风险.
- Add a pure validator helper if needed: `validate_bond_risk_evidence_value(value: BondRiskEvidenceValue) -> None`.

Invariants:

- Exactly seven groups must be represented.
- Group ids must match `BOND_RISK_EVIDENCE_GROUPS`.
- Accepted/weak group records must not reference missing anchors.
- `satisfied_group_ids`, `missing_group_ids`, `weak_group_ids`, `ambiguous_group_ids` must be derived from group statuses, not caller-provided arbitrary data.

Tests:

- Complete seven-group value validates.
- Missing anchor for accepted group fails validation.
- Weak drawdown-control record is not in satisfied ids.
- Explicit absence convertible/equity record is accepted.

Stop conditions:

- If the existing Python version or typing setup cannot express the Literal aliases cleanly, stop and ask controller before falling back to untyped dicts.

### Slice 2: Extractor

Allowed files:

- `fund_agent/fund/extractors/bond_risk_evidence.py`
- `fund_agent/fund/extractors/__init__.py`
- `tests/fund/extractors/test_bond_risk_evidence.py`

Functions/classes:

- `extract_bond_risk_evidence(report: ParsedAnnualReport, classified_fund_type: str | None) -> ExtractedField[BondRiskEvidenceValue]`
- `_extract_duration_rate_risk(report) -> BondRiskEvidenceGroupRecord`
- `_extract_credit_risk(report) -> BondRiskEvidenceGroupRecord`
- `_extract_leverage_liquidity(report) -> BondRiskEvidenceGroupRecord`
- `_extract_asset_allocation_holdings_mix(report) -> BondRiskEvidenceGroupRecord`
- `_extract_drawdown_stress(report) -> BondRiskEvidenceGroupRecord`
- `_extract_redemption_share_pressure(report) -> BondRiskEvidenceGroupRecord`
- `_extract_convertible_bond_equity_exposure(report) -> BondRiskEvidenceGroupRecord`
- `_build_group_anchor(...) -> tuple[EvidenceAnchor, BondRiskEvidenceAnchorRef]`

Data flow:

`ParsedAnnualReport` + explicit `classified_fund_type` -> bond-fund early gate -> group extractors -> group records + anchors -> `BondRiskEvidenceValue` -> `ExtractedField`.

Non-bond boundary:

- If `classified_fund_type != "bond_fund"`, return a missing/not-applicable `ExtractedField` without scanning report sections/tables for the seven bond groups.
- The returned value must not contain satisfied groups or anchors.
- Use an explicit missing/not-applicable reason, for example `not_applicable_non_bond_fund`, in the field note or `na_reason`; do not add hidden state to `extra_payload`.
- Unknown or absent `classified_fund_type` must not be treated as bond evidence; it should fail closed to missing/not-applicable unless the integration gate explicitly classifies it as `bond_fund`.

Error handling:

- Parser/table shape ambiguity should produce group `ambiguous` or `missing`, not crash whole extraction, unless the model would be internally inconsistent.
- Do not catch repository/source exceptions here; extractor receives already parsed report.
- Do not infer evidence from fund category alone.

Tests:

- Synthetic table-backed credit risk accepted with row-level anchors.
- Flexible leverage strategy text alone is weak.
- Repo/liquidity table row plus liquidity text satisfies leverage/liquidity.
- Drawdown-control text alone is weak.
- Multi-share-class share change selects the target class only when §2 code/name evidence disambiguates.
- Ambiguous share class stays ambiguous.
- Convertible/equity explicit `-` rows become `accepted_absence`.
- Non-bond `classified_fund_type` returns missing/not-applicable and does not invoke the seven group extractors.

Stop conditions:

- If precise leverage/repo rows for real `006597` cannot be found with current parser output, do not broaden accepted evidence. Keep group weak and report residual.
- If the implementation cannot obtain an explicit classified fund type at the extractor boundary without `extra_payload`, stop and return to controller instead of adding implicit report-text classification inside this extractor.

### Slice 3: Bundle Integration

Allowed files:

- `fund_agent/fund/data_extractor.py`
- `tests/fund/test_data_extractor.py`

Changes:

- Add `bond_risk_evidence` to `StructuredFundDataBundle`.
- Pass the already classified fund type explicitly and call `extract_bond_risk_evidence(report, classified_fund_type=...)` inside `FundDataExtractor.extract(...)` after existing holdings/share-change extraction.
- Keep constructor params explicit and unchanged; no Service/UI parameter required.

Invariants:

- Annual report is still loaded only once through `FundDocumentRepository`.
- No direct PDF/cache/source-helper calls are introduced.
- Existing fields remain populated as before.
- Non-bond funds either skip seven-group extraction through the explicit classified-fund-type gate or receive a missing/not-applicable `bond_risk_evidence` field that score ignores.

Tests:

- Fake repository extraction returns bundle with `bond_risk_evidence`.
- Source provenance behavior remains unchanged.
- Non-bond fake extraction proves the bond extractor is not asked to scan seven groups and produces no satisfied bond-risk groups.

Stop conditions:

- If integration requires Service/UI parameter changes, stop and return to controller; this gate does not need new user-facing params.
- If the classified fund type is unavailable at this boundary, stop and return to controller; do not infer bond applicability from ad hoc annual-report text inside the extractor.

### Slice 4: Snapshot Projection

Allowed files:

- `fund_agent/fund/extraction_snapshot.py`
- `tests/fund/test_extraction_snapshot.py`

Changes:

- Add `("risk", "bond_risk_evidence")` to `SNAPSHOT_FIELD_ORDER`, preferably immediately after `holdings_snapshot` or before `nav_data` with a stable comment.
- Add `bond_risk_evidence` to `FIELD_PRIORITY_BY_NAME` as `P1` so coverage/traceability statistics observe the replacement field instead of leaving it `UNMAPPED`.
- Extend `_comparable_values_for_field(...)` to keep `bond_risk_evidence` non-comparable.
- Add note formatter for `BondRiskEvidenceValue` so score can parse stable contract status and groups without ad hoc prose parsing if no extra JSON fields are added.

Preferred implementation:

- Add explicit snapshot dataclass fields only if necessary:
  - `bond_risk_contract_status: str | None`
  - `bond_risk_satisfied_groups: tuple[str, ...]`
  - `bond_risk_missing_groups: tuple[str, ...]`
  - `bond_risk_weak_groups: tuple[str, ...]`
  - `bond_risk_ambiguous_groups: tuple[str, ...]`
- This is cleaner than parsing `note` and should be chosen if review accepts snapshot schema extension.

Invariants:

- Existing snapshot rows remain backward-compatible for old consumers.
- New field does not enter golden correctness denominator.
- New field does enter P1 coverage/traceability denominators.
- `value_present` is derived from `contract_status != "missing"`.
- `anchor_present` requires at least one stable group-level anchor.
- First-anchor fields remain populated for human traceability, while group-level anchors remain in the structured value model/tests.

Tests:

- Complete bond evidence row has `field_name=bond_risk_evidence`, `value_present=True`, `anchor_present=True`.
- Complete `006597` / `2024` row with all seven groups satisfied has P1 coverage/traceability semantics that score as 100% for this field.
- Partial row exposes missing/weak/ambiguous groups.
- Non-bond funds may produce missing/not-applicable field if bundle carries missing evidence; score should ignore unless exact `bond_fund`.

Stop conditions:

- If snapshot schema extension is considered public-contract heavy beyond this gate, use `note` only and ask controller for a follow-up schema gate before implementation.

### Slice 5: Score Applicability

Allowed files:

- `fund_agent/fund/extraction_score.py`
- `tests/fund/test_extraction_score.py`

Functions to modify/add:

- `derive_score_applicability_issues(...)`
- `_bond_risk_evidence_missing_issue(...)`
- `_is_bond_holdings_replacement_record(...)` only if needed for clarity.
- Add:
  - `_bond_risk_evidence_record_for_fund(records) -> Mapping[str, object] | None`
  - `_bond_risk_unsatisfied_groups(record) -> tuple[str, ...]`
  - `_bond_risk_contract_satisfied(record) -> bool`

Data flow:

Snapshot records -> exact fund type check -> holdings replacement check -> find positive `bond_risk_evidence` snapshot row -> compute unsatisfied groups -> emit no issue or partial issue.

Invariants:

- Unknown/conflicting fund types remain fail-closed; no bond exclusion applies.
- Missing `bond_risk_evidence` row keeps current blocker.
- Weak/ambiguous evidence groups remain unsatisfied.
- `required_evidence_groups` is always the full ordered set of seven `BOND_RISK_EVIDENCE_GROUPS` ids.
- `missing_evidence_groups` is dynamic and contains only groups that are missing, weak, ambiguous, malformed, or anchorless for this snapshot instance.
- `baseline_blocking=True` remains for any emitted issue.
- FQ0-FQ6 thresholds and severities are unchanged.

Tests:

- Exact bond fund with no positive record emits current all-seven blocker.
- Complete positive record emits no `bond_risk_evidence_missing`.
- Weak drawdown record emits missing issue only for `drawdown_stress`.
- Ambiguous redemption pressure emits missing issue only for `redemption_share_pressure`.
- Partial issue keeps `required_evidence_groups` at all seven group ids while `missing_evidence_groups` lists only unsatisfied ids.
- Anchor-missing accepted evidence is treated as unsatisfied or fails validation before score.
- Non-bond fund ignores `bond_risk_evidence`.

Stop conditions:

- If score needs to parse free-form prose to decide contract satisfaction, stop; snapshot must expose structured status/group fields or implementation must return to Slice 4.

### Slice 6: Real `006597` Path

Allowed files:

- `tests/fund/extractors/test_bond_risk_evidence.py`
- `tests/fund/test_extraction_snapshot.py`
- `tests/fund/test_extraction_score.py`
- optional smoke documentation in `fund_agent/fund/README.md` after passing validation

Work:

- Add a real repository smoke or integration test only if current test policy allows network/PDF in non-default smoke. Otherwise document the manual validation command and keep unit tests deterministic.
- Rerun `006597` / `2024` extraction-snapshot, extraction-score, and quality-gate manually in validation.

Expected result if all seven groups are truly satisfied:

- Snapshot contains `bond_risk_evidence` row with all seven groups satisfied.
- Score has no `bond_risk_evidence_missing` issue.
- Quality gate no longer has FQ2F row with `reason=bond_risk_evidence_missing`.

Expected result if drawdown or leverage remains weak:

- Snapshot shows partial contract.
- Score emits `bond_risk_evidence_missing` only for unsatisfied group(s).
- This is acceptable and must not be papered over.

Stop conditions:

- Stop before completion if real `006597` evidence cannot satisfy `drawdown_stress` or `leverage_liquidity` under this contract. Report residual honestly; do not mark blocker resolved.

### Slice 7: Documentation

Allowed files:

- `fund_agent/fund/README.md`
- `tests/README.md` if new test category/commands are added
- `docs/design.md` only if controller requires design truth update after implementation acceptance

Docs decision:

- Because this changes Fund package current behavior and schema, update `fund_agent/fund/README.md` after code/tests pass.
- Do not update root `README.md`; no user-facing CLI usage changes are introduced.
- Do not update `fund_agent/README.md`; no layer boundary changes are introduced.
- Do not update Host/Agent docs; no Host/Agent work exists.
- `docs/design.md` should be updated only in the acceptance/controller step if the new schema is accepted as current design truth. The implementation worker should not pre-write future facts into design before code passes.

## How `score_applicability_issues` Stops Emitting The Blocker

Current behavior:

1. Exact `bond_fund`.
2. `holdings_snapshot` is treated as non-applicable to equity holdings.
3. Replacement issue always emitted because no positive replacement field exists.

Planned behavior:

1. Exact `bond_fund`.
2. `holdings_snapshot` remains excluded from equity-holdings denominator.
3. Score searches for `field_name="bond_risk_evidence"` for the same fund/year.
4. If absent, malformed, anchorless, or all groups missing, emit the same blocker.
5. If present but partial, emit blocker only for unsatisfied groups.
6. If present and all seven groups are satisfied, emit no `bond_risk_evidence_missing`.
7. In every emitted issue, keep `required_evidence_groups` as all seven required group ids and use `missing_evidence_groups` only for the dynamic unsatisfied subset.

This is natural removal by satisfying the contract, not suppression.

## Validation Commands And Expected Assertions

Required final validation matrix:

| Command | Expected assertion |
|---|---|
| `uv run ruff check .` | Pass with no lint errors. |
| `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q` | Pass; global coverage remains above 50%; new/modified modules should target >=80% or document residual risk in review. |
| Real network/PDF smoke through `FundDocumentRepository` loading `006597` / `2024` | Annual report loads through repository; no direct PDF/cache/source helper; fund code/year identity match. |
| Rerun `006597` / `2024` extraction-snapshot | `snapshot.jsonl` includes `bond_risk_evidence`; source provenance remains public/safe; errors are empty unless source unavailable. |
| Rerun extraction-score | Complete positive path has no `bond_risk_evidence_missing`; partial path lists only unsatisfied groups with `baseline_blocking=true`. |
| Rerun quality-gate | FQ0-FQ6 semantics unchanged; no FQ2F `bond_risk_evidence_missing` only if score has no such issue. |

Suggested exact smoke commands:

```bash
uv run python -c 'import asyncio; from fund_agent.fund.documents import FundDocumentRepository; report = asyncio.run(FundDocumentRepository().load_annual_report("006597", 2024)); print(report.key.fund_code, report.key.year, len(report.sections), len(report.tables))'
uv run fund-analysis extraction-snapshot --run-id bond-risk-evidence-006597-2024-20260527 --fund-code 006597 --report-year 2024
uv run fund-analysis extraction-score --snapshot-path reports/extraction-snapshots/bond-risk-evidence-006597-2024-20260527/snapshot.jsonl --errors-path reports/extraction-snapshots/bond-risk-evidence-006597-2024-20260527/errors.jsonl --golden-answer-path reports/golden-answers/golden-answer.json
uv run fund-analysis quality-gate --score-path reports/extraction-snapshots/bond-risk-evidence-006597-2024-20260527/score.json
```

Manual assertions after smoke:

- `score.json.score_applicability_issues` has no `bond_risk_evidence_missing` only when all seven groups are satisfied.
- For complete `006597` / `2024`, `bond_risk_evidence` is mapped to P1 and has 100% coverage/traceability under the field semantics above.
- If `drawdown_stress` remains qualitative-only, `score_applicability_issues` must still include `drawdown_stress`.
- If `leverage_liquidity` lacks precise table/row or accepted liquidity-risk evidence, it must remain unsatisfied.
- Any partial issue must keep `required_evidence_groups` equal to all seven ids while `missing_evidence_groups` lists only unsatisfied ids.
- No generated `reports/extraction-snapshots/...` output is staged or promoted.

## Review Gates

This is a `standard` gate unless controller upgrades it because snapshot schema/public contract expansion is considered schema-heavy.

Required before implementation acceptance:

- At least two independent plan/implementation reviews, or controller-recorded reviewer unavailability.
- Reviewer must explicitly check:
  - no FQ0-FQ6 weakening;
  - no direct PDF/cache/source-helper access;
  - drawdown qualitative evidence remains weak;
  - leverage strategy text alone remains weak;
  - anchor ids are stable and row-level where required;
  - weak/ambiguous/missing groups continue to emit blocker;
  - no golden promotion;
  - no Host/Agent/dayu or Service/UI boundary drift.
- Controller judgment required before any promotion or readiness claim.

## Risks And Open Questions

No blocking questions for controller.

Risks:

- Current parser may not expose precise enough repo/leverage table rows for `006597`; safe outcome is partial contract, not pass.
- Current annual report may not contain max drawdown / volatility; safe outcome is weak `drawdown_stress`, not pass.
- Snapshot schema extension adds a public JSONL shape. Mitigation: additive fields only, no removal or reinterpretation of existing fields.
- Adding `bond_risk_evidence` to field order changes field counts. Mitigation: tests must assert FQ0-FQ6 expected effects and no threshold/severity change.
- Real network/PDF smoke is source-dependent. Mitigation: unit tests stay deterministic; smoke results are validation evidence, not fixture promotion.

## Completion Report Format

Implementation worker final report should include:

- Artifact / branch status:
  - `Self-check: pass` or `Self-check: blocked - <reason>`
  - files changed
  - no unrelated untracked files touched/staged
- Contract result:
  - seven groups status table
  - which groups are satisfied/weak/ambiguous/missing
  - anchor format confirmation
- `006597` / `2024` result:
  - repository smoke status
  - snapshot run id
  - score issue state
  - quality gate state
- Validation:
  - `uv run ruff check .`
  - `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q`
  - extraction-snapshot / extraction-score / quality-gate reruns
- Residuals:
  - explicit statement if `drawdown_stress` or `leverage_liquidity` remains weak
  - confirmation no golden corpus promotion occurred

## Handoff Decision

Status: handoff-ready.

Blocking Questions For Controller: none.
