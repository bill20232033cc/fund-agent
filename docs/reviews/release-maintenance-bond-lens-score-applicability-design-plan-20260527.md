# release-maintenance bond-lens score applicability design plan - 2026-05-27

> Worker: AgentCodex planning/design worker
> Scope: design / implementation-plan artifact only
> Output path: `docs/reviews/release-maintenance-bond-lens-score-applicability-design-plan-20260527.md`

## 0. Scope Guard

本 artifact 只产出 code-generation-ready design / implementation-plan，不授权实现、不提交、不 push、不创建 PR。

本次读取的当前真源：

- `AGENTS.md`
- `docs/design.md` 当前设计章节：fund type、preferred_lens、quality gate、ReportEvidenceBundle / Fact-Evidence、CHAPTER_CONTRACT、baseline / golden
- `docs/implementation-control.md` Startup Packet、Next Entry Point、Open Residuals、Active Gate Ledger
- accepted plan / judgment：`docs/reviews/release-maintenance-bond-lens-contract-baseline-coverage-plan-20260527.md`、`docs/reviews/release-maintenance-bond-lens-contract-baseline-coverage-plan-controller-judgment-20260527.md`
- 只读代码定位：`fund_agent/fund/extraction_score.py`、`fund_agent/fund/quality_gate.py`、`fund_agent/fund/fund_type.py`、`tests/fund/test_extraction_score.py`、`tests/fund/test_quality_gate.py`

`docs/reviews/` 与 archive 只作为证据链，不覆盖 Startup Packet 或 `docs/design.md` 当前设计章节。

## 1. Startup Packet Replay

| Item | Current state / plan interpretation |
|---|---|
| Current phase | `release maintenance` |
| Current gate | `bond-lens contract + baseline coverage recovery plan accepted locally` |
| Next entry point | `bond-lens score applicability design gate` |
| Latest accepted checkpoint | `c09a4cb` |
| Design truth | `docs/design.md` v2.2 current design sections |
| Control truth | `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point / Open Residuals / Active Gate Ledger |
| Current architecture guardrail | Target remains `UI -> Service -> Host -> Agent`; current deterministic production path remains Service -> `fund_agent/fund` Agent-layer fund capability |
| Current product quality gate | FQ0-FQ6 semantics unchanged; FQ4 thresholds remain warn >= 20%, block >= 35% |
| Durable baseline / golden status | blocked; no sample may be promoted in this gate |

Allowed in the future implementation slice after review/controller acceptance:

- Fund-layer score applicability changes inside `fund_agent/fund/extraction_score.py`.
- Quality gate consumer changes inside `fund_agent/fund/quality_gate.py` only to surface score-applicability replacement issues without changing FQ0-FQ6 policy semantics.
- Focused tests in `tests/fund/test_extraction_score.py` and `tests/fund/test_quality_gate.py`.
- Minimal README sync only if accepted implementation changes Fund scoring behavior or test maintenance instructions.
- Read-only / validation commands including focused pytest, 006597 score/gate evidence run, regression commands, ruff, and `git diff --check`.

Forbidden in this gate and future minimal implementation unless a later accepted plan explicitly expands scope:

- renderer changes.
- FQ0-FQ6 rule meaning, severity policy, or threshold changes.
- Service / CLI behavior changes.
- Host / Agent package creation or `dayu.host` / `dayu.engine` runtime integration.
- `FundDocumentRepository` source strategy, fallback semantics, source helpers, downloaders, PDF cache, or direct PDF access.
- extractor logic changes.
- golden answer, durable baseline, curated fixture, or baseline corpus promotion.
- passing explicit parameters through `extra_payload`.
- GitHub mutation.

Verifier matrix for this design gate:

| Verifier | Required result |
|---|---|
| Artifact path | present exactly at this file path |
| `git diff --check` | must pass and be recorded in section 11 |
| Scope check | worker-created file set limited to this artifact |
| Plan review | MiMo / GLM should review using section 12 checklist |
| Controller decision | required before source/test implementation |

## 2. Current Code Facts

Current `extraction_score.py` already has a fund-type applicability pattern:

- `INDEX_QUALITY_FIELD_NAMES = ("index_profile", "tracking_error")`.
- `_scorable_records()` excludes index quality fields when `classified_fund_type` is not `index_fund` or `enhanced_index`.
- unknown or conflicted fund type remains conservative because fund-level `_unique_optional_text()` returns `None` on conflicts and `use_record_fund_type=False` prevents first-row fallback.

Current `holdings_snapshot` behavior is equity-shaped:

- `HOLDINGS_SNAPSHOT_FIELD_NAME = "holdings_snapshot"`.
- `_record_is_covered()` treats `holdings_snapshot` as covered only when `top_holdings_status` / `top_holdings_source` matches `("direct_top_ten", "top_ten")` or `("direct_all_stock_details", "all_stock_investment_details")`.
- This is correct for active/index/enhanced equity-shaped holdings evidence, but it is a category error for `bond_fund`.

Current `quality_gate.py` behavior:

- FQ2 / FQ2F use `field_scores` / `fund_scores`.
- FQ4 only consumes `fund_quality.missing_field_rate`.
- FQ5 consumes preferred_lens applicability status.
- There is no deterministic issue id field in `QualityGateIssue` today.

Implication: the safest future implementation is to add a score-applicability layer beside the existing index applicability filter, then surface replacement bond-risk issues as explicit score-applicability issues. Do not solve this by making bond funds silently skip `holdings_snapshot` with no replacement issue.

## 3. Design Decision

### 3.1 Accepted Decision

For `bond_fund`, equity-shaped `holdings_snapshot` records do not enter the stock-holdings coverage denominator.

This exclusion is not a pass condition. It must be paired with an explicit replacement contract named `bond_risk_evidence`. If the current snapshot cannot prove bond-risk evidence, scoring must emit deterministic replacement issue(s) explaining the evidence gap and preserving severity.

### 3.2 First-Principles Rationale

`docs/design.md` defines `bond_fund` preferred_lens as credit risk, duration, and maximum drawdown; the methodology matrix places bond funds around duration, credit, leverage, liquidity, and drawdown, with Chapter 4 / Chapter 6 as core and Chapter 2 / Chapter 5 as high priority.

Stock top-ten holdings are not the right denominator for those questions. But a bond fund still needs risk evidence for the investor decision. Therefore the correct contract is:

- exclude non-applicable stock-holdings evidence from the denominator;
- require explicit bond-risk evidence or explicit data-gap issues;
- keep unknown/conflicted fund types fail-closed;
- preserve FQ0-FQ6 policy meaning.

### 3.3 Non-Silent N/A Rule

The only allowed N/A for equity-shaped `holdings_snapshot` under `bond_fund` is:

`not_applicable_to_bond_fund_equity_holdings`

This N/A is valid only when paired with a replacement issue or evidence decision for `bond_risk_evidence`. A plain `not_applicable`, missing replacement issue, or green/pass status is invalid.

## 4. Bond-Risk Evidence Contract

Future code should model the contract as data constants in `extraction_score.py`, not as scattered conditionals. Suggested names:

- `BOND_FUND_TYPE = "bond_fund"`
- `BOND_RISK_EVIDENCE_CONTRACT_ID = "bond_risk_evidence.v1"`
- `BOND_RISK_REPLACEMENT_FIELD_NAME = "bond_risk_evidence"`
- `BOND_RISK_EVIDENCE_GROUPS: Final[tuple[BondRiskEvidenceGroup, ...]]`

The first implementation does not need to extract these groups from annual reports. It must define the contract, evaluate current snapshot support conservatively, and issue explicit gaps.

| Group | required_evidence | allowed_na_reason | failure_behavior |
|---|---|---|---|
| `duration_rate_risk` | portfolio duration, average remaining maturity, interest-rate sensitivity disclosure, rate-risk note, or accepted reviewed derived duration/rate-risk evidence with anchors | `bond_duration_rate_risk_not_disclosed`, `bond_duration_rate_risk_not_yet_reviewed` | Missing reviewed evidence emits `bond_risk_evidence_missing` tied to Chapter 6 / Chapter 5; no silent pass |
| `credit_risk` | bond rating distribution, credit bond exposure, default/impairment risk disclosure, non-policy-financial bond exposure, issuer credit concentration, or accepted data gap | `bond_credit_risk_not_disclosed`, `bond_credit_risk_not_yet_reviewed` | Missing reviewed evidence emits `bond_risk_evidence_missing` tied to Chapter 6 |
| `leverage_liquidity` | leverage ratio, repo/financing exposure, liquidity risk note, top holder / large redemption concentration if disclosed, or accepted data gap | `bond_leverage_liquidity_not_disclosed`, `bond_leverage_liquidity_not_yet_reviewed` | Missing reviewed evidence emits `bond_risk_evidence_missing`; liquidity/redemption overlap must keep share pressure issue link |
| `asset_allocation_holdings_mix` | bond/cash/financial-instrument mix, top bond holdings if disclosed, issuer/sector concentration if disclosed, or accepted data gap | `bond_asset_mix_not_disclosed`, `bond_asset_mix_not_yet_reviewed` | Missing reviewed evidence emits `bond_risk_evidence_missing`; stock top-ten cannot satisfy this group |
| `drawdown_stress` | max drawdown, volatility, stress threshold status, drawdown/stress calculation with source anchors, or accepted data gap | `bond_drawdown_stress_not_disclosed`, `bond_drawdown_stress_not_yet_reviewed` | Missing reviewed evidence emits `bond_risk_evidence_missing`; no yield/return proxy may replace drawdown |
| `redemption_share_pressure` | share change, subscription/redemption trend, holder concentration pressure, large redemption disclosure, or explicit ambiguity/data gap | `bond_redemption_pressure_not_disclosed`, `bond_redemption_pressure_ambiguous`, `bond_redemption_pressure_not_yet_reviewed` | Missing/ambiguous evidence emits issue; existing `share_change` ambiguity remains a separate extractor/evidence residual, not silently solved here |
| `convertible_bond_equity_exposure` | convertible bond exposure, equity exposure, secondary-bond/mixed-bond equity allocation, or explicit statement that no equity/convertible exposure is disclosed | `bond_convertible_equity_exposure_not_disclosed`, `bond_convertible_equity_exposure_not_yet_reviewed` | Missing reviewed evidence emits `bond_risk_evidence_missing`; accepted refinement from controller judgment must be covered before implementation |

Minimum initial pass semantics:

- A current `bond_fund` with no reviewed bond-risk evidence must emit a replacement issue.
- Future positive coverage can be accepted only when at least one direct or reviewed-derived group has source anchors and missing groups are explicit data gaps.
- The first implementation should default current snapshot-only runs to `bond_risk_evidence_missing` unless accepted source facts already exist in `comparable_values` or a future reviewed evidence input is added by separate gate.

## 5. Score Applicability And Denominator Behavior

### 5.1 Applicability Records

Add a deterministic internal applicability decision layer in `extraction_score.py`.

Suggested dataclasses:

- `FieldApplicabilityDecision`
  - `fund_code: str`
  - `field_name: str`
  - `classified_fund_type: str | None`
  - `applicability_status: Literal["applicable", "not_applicable_replaced", "applicable_missing_replacement", "unknown_fail_closed"]`
  - `reason_code: str`
  - `replacement_field_name: str | None`
  - `contract_id: str | None`
  - `denominator_effect: Literal["included", "excluded_with_replacement_issue", "included_fail_closed"]`

- `ScoreApplicabilityIssue`
  - `issue_id: str`
  - `issue_code: str`
  - `severity: Literal["block", "warn", "info"]`
  - `fund_code: str`
  - `field_name: str`
  - `classified_fund_type: str | None`
  - `replacement_field_name: str | None`
  - `contract_id: str`
  - `priority: str`
  - `message: str`
  - `baseline_blocking: bool`
  - `rule_code_hint: str`
  - `denominator_excluded_fields: tuple[str, ...]`
  - `required_evidence_groups: tuple[str, ...]`
  - `missing_evidence_groups: tuple[str, ...]`

Expose them in `score.json` as optional top-level arrays:

- `field_applicability_decisions`
- `score_applicability_issues`

The existing `field_scores`, `fund_scores`, and `fund_quality` remain present. Existing readers should remain valid.

### 5.2 Records Replaced Or Non-Applicable For `bond_fund`

| Current score record | Current priority | `bond_fund` behavior | Replacement |
|---|---:|---|---|
| `holdings_snapshot` with stock top-ten / all-stock semantics | P1 | exclude from coverage / traceability / fund missing denominator when the record's effective fund type is exactly `bond_fund` | `bond_risk_evidence` issue / future evidence contract |
| `index_profile` | P1 | existing behavior: excluded for non-index funds | none |
| `tracking_error` | P1 | existing behavior: excluded for non-index funds | none |
| `turnover_rate` | P1 | remains applicable until a separate evidence/policy gate proves otherwise | none |
| `holder_structure` | P1 | remains applicable / needs-more-evidence; do not infer absence from public score output | none |
| `share_change` | P1 | remains applicable; current ambiguity remains explicit | none |
| `investor_return` | P2 | remains P2 score/evidence-contract residual; not bond N/A | none |
| `nav_data` | P2 | remains P2 external-data provenance residual; not bond N/A | none |

Unknown/conflicted fund type behavior:

- If fund type is missing, unsupported, or conflicted, do not exclude `holdings_snapshot`.
- Keep current conservative denominator.
- Emit no bond-specific replacement issue unless the effective fund type is exactly `bond_fund`.

### 5.3 FQ4 Denominator / Numerator

Current FQ4 uses `fund_quality.missing_field_rate = missing_field_count / total_field_count`.

Future `bond_fund` behavior:

- `total_field_count`: exclude the equity-shaped `holdings_snapshot` record only when replaced by `bond_risk_evidence`.
- `missing_field_count`: exclude the same record from the missing numerator.
- `missing_p1_fields`: do not list `holdings_snapshot` when the only missingness is the equity-shaped stock-holdings category error.
- `score_applicability_issues`: must include `bond_risk_evidence_missing` or a reviewed positive evidence decision, so denominator reduction is visible.

Required denominator metadata for review/debug output:

- `raw_total_field_count`
- `raw_missing_field_count`
- `raw_missing_field_rate`
- `applicable_total_field_count`
- `applicable_missing_field_count`
- `applicable_missing_field_rate`
- `excluded_non_applicable_fields`
- `replacement_issue_ids`

Implementation may keep current `total_field_count`, `missing_field_count`, and `missing_field_rate` as applicable counts for quality_gate compatibility, but must emit the raw/applicable comparison in `fund_quality` or `field_applicability_decisions`.

### 5.4 006597 Anti-Mis-Pass Requirement

Future implementation must prove `006597` is not improved only by lowering the FQ4 denominator.

Required evidence in the implementation report:

1. Before/after FQ4 counts for `006597`.
2. A deterministic `bond_risk_evidence_missing` issue id in `score.json`.
3. Quality gate status must not become `pass` solely because `holdings_snapshot` was excluded.
4. If FQ4 moves from `block` to `warn` or disappears, the implementation evidence must state that the product-level FQ4 threshold was not changed and that the remaining status is driven by explicit replacement issue(s), FQ2/FQ2F warnings, or other existing issues.
5. Baseline/golden eligibility must remain blocked while any `baseline_blocking=true` score-applicability issue exists.

The replacement issue severity should be:

- `warn` for current FQ quality-gate aggregation, because the replaced field is P1 and FQ2/FQ2F P1 semantics are warning-level today.
- `baseline_blocking=true` for baseline/golden selection, because explicit bond-risk evidence is mandatory before treating the bond sample as clean representative coverage.

This preserves FQ0-FQ6 semantics while preventing baseline/golden misclassification.

## 6. Quality Gate Projection

Future `quality_gate.py` should consume `score_applicability_issues` if present.

Projection rules:

- Validate each issue has deterministic `issue_id`, `issue_code`, `severity`, `fund_code`, `field_name`, `contract_id`, and `message`.
- Project `bond_risk_evidence_missing` into a `QualityGateIssue` without introducing a new FQ rule code.
- Use `rule_code="FQ2F"` for fund-level P1 replacement quality issue, or `rule_code="FQ2"` if the implementation chooses field-level projection. The plan recommends `FQ2F` because the replacement is a fund-level contract gap rather than a snapshot field-score row.
- Keep `severity="warn"` for quality gate aggregation.
- Include machine-readable `reason="bond_risk_evidence_missing"` and message text identifying `bond_risk_evidence.v1`.
- If `QualityGateIssue` is extended with optional `issue_id` / `issue_code`, ensure JSON and Markdown renderers include them and existing tests remain compatible.

Do not change:

- FQ4 thresholds.
- FQ2 P0 block / P1 warn semantics.
- FQ5 preferred_lens semantics.
- product `quality_gate_policy=block` behavior.

## 7. Issue Taxonomy And Deterministic Ids

### 7.1 Issue Codes

| Issue code | Meaning | Severity | Baseline blocking |
|---|---|---:|---:|
| `equity_holdings_not_applicable_to_bond` | equity-shaped `holdings_snapshot` excluded for exact `bond_fund` | `info` | false |
| `bond_risk_evidence_missing` | replacement contract exists but no reviewed bond-risk evidence/data-gap record is present | `warn` | true |
| `bond_risk_anchor_missing` | bond-risk value exists but lacks accepted provenance / anchor | `warn` | true |
| `bond_risk_data_gap_declared` | explicit reviewed data gap exists for one or more evidence groups | `info` or `warn` by group criticality | true until controller accepts it for baseline |
| `bond_risk_evidence_partial` | some required groups are reviewed while others are explicit gaps | `warn` | true by default |
| `bond_risk_evidence_sufficient` | minimum reviewed evidence condition satisfied | `info` | false |
| `unknown_fund_type_fail_closed` | fund type missing/conflicted; applicability exclusion not applied | `info` | true if baseline candidate |
| `score_applicability_contract_error` | score payload has inconsistent applicability / replacement issue state | `block` | true |

### 7.2 Deterministic Issue Ids

Use stable lowercase ids with no spaces:

```text
score-applicability:{fund_code}:{report_year}:{field_name}:{issue_code}:{contract_id}
```

Normalization rules:

- `fund_code`: exact six-digit fund code from snapshot.
- `report_year`: snapshot `report_year` if available; otherwise `unknown-year`.
- `field_name`: original field, e.g. `holdings_snapshot`.
- `issue_code`: taxonomy code above.
- `contract_id`: `bond_risk_evidence.v1`.

For per-group issues, append `:{group_id}`:

```text
score-applicability:{fund_code}:{report_year}:bond_risk_evidence:{issue_code}:bond_risk_evidence.v1:{group_id}
```

The first implementation should prefer one aggregate fund-level `bond_risk_evidence_missing` issue containing `missing_evidence_groups`, unless tests show consumers need per-group issue rows.

## 8. Minimal Future Implementation Slice

### 8.1 Files

Allowed source files:

- `fund_agent/fund/extraction_score.py`
- `fund_agent/fund/quality_gate.py`

Allowed tests:

- `tests/fund/test_extraction_score.py`
- `tests/fund/test_quality_gate.py`

README sync:

- `fund_agent/fund/README.md` should be updated if the implementation changes documented Fund scoring behavior.
- `tests/README.md` should be updated only if new test conventions or commands are added.
- No root README, Service README, Host README, Agent README, or config README update should be needed.

Do not modify `fund_agent/fund/fund_type.py` in the minimal slice.

Only expand to `fund_type.py` if review accepts one of these conditions:

- a new explicit bond subtype/facet is required to distinguish pure bond, secondary bond, convertible-heavy bond, or mixed bond before score applicability can be safe;
- current `FundType` literal cannot represent a required fail-closed state;
- existing classification precedence is proven by same-source evidence to misclassify the target sample.

Convertible-bond / equity-exposure handling does not by itself require `fund_type.py`; it belongs in the bond-risk evidence groups unless a later taxonomy gate says otherwise.

### 8.2 Extraction Score Steps

1. Add bond-risk constants and optional dataclasses near existing score dataclasses in `extraction_score.py`.
2. Refactor `_scorable_records()` from "index-only exclusion" into a general applicability decision path while preserving current index behavior.
3. Add `_field_applicability_decision(record, classified_fund_type, use_record_fund_type)` or equivalent helper.
4. For exact `bond_fund` + `holdings_snapshot`, return `not_applicable_replaced` with reason `not_applicable_to_bond_fund_equity_holdings`.
5. Exclude those records from coverage / traceability / fund missing denominator.
6. Emit `field_applicability_decisions` and `score_applicability_issues` in result JSON.
7. Add raw/applicable denominator metadata for fund_quality rows or an adjacent output object.
8. Ensure `score_snapshot_records()`, `score_fund_records()`, and `derive_fund_quality_records()` use consistent applicability logic.
9. Preserve unknown/conflicted fund type conservative behavior.

### 8.3 Quality Gate Steps

1. Add parser for optional `score_applicability_issues`.
2. Validate issue objects fail-fast on malformed required fields.
3. Project `bond_risk_evidence_missing` into warn-level FQ2F issue with deterministic id included in JSON/Markdown if the dataclass is extended.
4. Add a rule result or issue message that makes the replacement contract visible.
5. Do not change FQ4 threshold code or `_missing_rate_issues()`.

### 8.4 Compatibility Notes

Existing older `score.json` without `score_applicability_issues` must still run.

Existing `field_scores`, `fund_scores`, `fund_quality`, correctness, preferred_lens, and FQ0-FQ6 JSON shapes should remain valid. New fields may be additive.

## 9. Testing And Validation Matrix

Focused extraction score tests:

- `bond_fund` equity-shaped `holdings_snapshot` missing does not enter field/fund/fund_quality denominator.
- `bond_fund` exclusion emits `field_applicability_decisions` and aggregate `bond_risk_evidence_missing`.
- `bond_fund` issue id is deterministic and includes fund code, report year, field, issue code, and contract id.
- Active fund still requires equity-shaped `holdings_snapshot` stock-holdings status/source allowlist.
- Index and enhanced index existing `index_profile` / `tracking_error` applicability behavior remains unchanged.
- Unknown fund type keeps `holdings_snapshot` in denominator and does not emit bond replacement issue.
- Conflicting fund type values keep conservative denominator and FQ5 mismatch behavior.
- Missing `classified_fund_type` remains `not_applicable` for FQ5 and conservative for score applicability.

Focused quality gate tests:

- `score_applicability_issues` with `bond_risk_evidence_missing` projects to warn-level FQ2F issue.
- Malformed applicability issue fails fast with clear `ValueError`.
- Existing score without applicability issues remains compatible.
- FQ4 threshold tests remain unchanged.
- A synthetic 006597-like payload with raw 35.7% missing rate and applicable lower denominator still returns non-pass because replacement issue is present.

006597 evidence run:

- Run the same public snapshot / score / quality-gate path used by the previous share_change evidence, scoped to `006597` / 2024.
- Record before/after raw and applicable missing counts.
- Record exact `bond_risk_evidence_missing` issue id.
- Prove no durable baseline/golden promotion occurred.

Regression:

- Active representative: `004393` score/gate behavior must preserve holdings_snapshot coverage semantics.
- Enhanced representative: `004194` index/enhanced applicability behavior must preserve index fields.
- Index representative, if clean source candidate is available in current workspace evidence, otherwise use synthetic test only.
- Unknown/conflicted fund-type synthetic tests.

Commands:

- `pytest tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py`
- `pytest tests/fund/test_quality_gate_integration.py` if score JSON shape is consumed there.
- 006597 score/gate evidence command through existing public CLI or existing accepted script path; do not call source helpers directly.
- `ruff check fund_agent/fund/extraction_score.py fund_agent/fund/quality_gate.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py`
- `git diff --check`

Do not require full pytest for this narrow future slice unless implementation expands beyond the files above or changes shared JSON schema in a way consumed by broader tests.

## 10. Non-Goals And Hard Prohibitions

Non-goals:

- No bond-risk extraction from annual reports.
- No renderer/report wording changes.
- No report-writing audit or CHAPTER_CONTRACT sidecar implementation for bond Chapter 6.
- No baseline/golden fixture promotion.
- No index/QDII/FOF recovery work.
- No `turnover_rate`, `holder_structure`, `investor_return`, or `nav_data` fixes.
- No `FundDocumentRepository` or source fallback changes.
- No source-helper direct calls.
- No Service/CLI behavior change.
- No Host/Agent/dayu runtime work.

Hard prohibitions:

- Do not weaken FQ0-FQ6 semantics or thresholds.
- Do not use silent N/A to make `006597` pass.
- Do not infer source absence from public missing output.
- Do not put explicit parameters into `extra_payload`.
- Do not mutate GitHub state.

## 11. Validation Recorded By This Worker

Initial workspace status before artifact creation:

- `git rev-parse --short HEAD`: `c09a4cb`
- Pre-existing untracked files observed and not touched:
  - `docs/reviews/release-maintenance-comprehensive-audit-report-20260526.md`
  - `docs/reviews/repo-review-20260526-231040.md`
  - `docs/tmux-agent-memory-store.md`

`git diff --check` result:

- Passed; command exited 0 with no output.

## 12. Review Checklist For MiMo / GLM

Reviewers should verify:

- The plan follows `AGENTS.md` and current `docs/design.md` boundaries.
- The `bond_fund` decision excludes equity-shaped holdings from denominator but does not create silent N/A.
- Bond-risk evidence groups cover duration/rate, credit, leverage/liquidity, asset mix, drawdown/stress, redemption/share pressure, and convertible/equity exposure.
- FQ4 denominator behavior is explicit and preserves raw/applicable count observability.
- 006597 cannot become `pass` or baseline-eligible only because denominator was lowered.
- Replacement issue severity preserves FQ0-FQ6 semantics while blocking baseline/golden promotion.
- Issue taxonomy and deterministic ids are stable enough for code generation.
- Minimal implementation files are scoped to `extraction_score.py`, `quality_gate.py`, and focused tests unless a concrete condition expands scope.
- `fund_type.py` is not modified without an accepted taxonomy condition.
- No renderer, Service/CLI, Host/Agent/dayu, source strategy, extractor, baseline/golden, or GitHub mutation work is authorized.
- Validation matrix is sufficient and does not over-require full pytest for the narrow slice.
