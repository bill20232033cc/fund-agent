# Drawdown Stress NAV-Derived Evidence Contract Plan

Date: 2026-05-28

Role: planning worker, not controller

Work unit: `drawdown_stress evidence contract / NAV-derived risk metric design gate`

Gate: plan

Classification: `heavy`

Artifact: `docs/reviews/release-maintenance-drawdown-stress-nav-derived-contract-plan-20260528.md`

## Worker Self-Check

- Current role is planning worker only. I did not start `$gateflow` / `/gateflow`, did not reorder the controller flow, and did not enter implementation.
- Current branch is `codex/local-reconciliation`. `git status --short` showed only unrelated untracked files before this artifact: `--help`, old repo-review / comprehensive audit artifacts, and `docs/tmux-agent-memory-store.md`.
- Scope is plan artifact only. No production code, tests, fixtures, golden data, release state, PR, push, merge, or closeout action is authorized.
- This plan treats the user handoff classification as authoritative: `heavy`, because the decision affects evidence contract, data-source boundary, score / snapshot semantics, and baseline blocker behavior.

## Goal And Motivation

The immediate goal is to decide whether `bond_risk_evidence.v1.drawdown_stress` may be satisfied by NAV-derived quantitative risk metrics, and if yes, define an implementation-ready contract that preserves the current fail-closed evidence discipline.

The root cause is not an extractor false negative anymore. Latest 006597 / 2024 evidence shows all other bond-risk groups are satisfied, while `drawdown_stress` remains weak because the annual / quarterly report text only says control-oriented language such as `控制回撤` and does not disclose a max drawdown, volatility, or stress metric. Under the current contract, weak qualitative control intent correctly keeps `bond_risk_evidence_missing.baseline_blocking=true`.

## Source Replay

### Rule Truth: `AGENTS.md`

- `AGENTS.md` is the repository-wide execution authority and requires Chinese responses, first-principles reasoning, root-cause evidence from the same logic/data source, explicit parameters instead of `extra_payload`, and evidence traceability for numerical judgments.
- Production annual-report PDF access must go through `FundDocumentRepository`; Service, UI, Host, renderer, and quality gate must not call source helpers, PDF cache, or download helpers directly.
- The target architecture is `UI -> Service -> Host -> Agent`; current deterministic path is `UI -> Service -> fund_agent/fund`. Fund-domain rules, fund type judgment, CHAPTER_CONTRACT / preferred_lens, evidence audit, and bond-risk logic belong in Agent-layer `fund_agent/fund`.
- Gate classification rules say public contract, schema, quality gate semantics, external source strategy, baseline/golden qualification, and release/PR state are high-impact and require heavier review. This plan therefore uses `heavy`.
- Fund analysis must first identify fund type, then apply `preferred_lens`, then use the 8-chapter template and evidence anchors. Bond-fund risk evidence belongs to template Chapter 6.

### Design Truth: `docs/design.md`

- Current design truth is Dayu four-layer boundary `UI -> Service -> Host -> Agent`; current CLI remains deterministic `UI -> Service -> fund_agent/fund`.
- `FundDataExtractor.extract()` currently loads annual reports through `FundDocumentRepository`, then loads NAV data through `FundNavDataAdapter`. NAV failures are downgraded to `NavDataResult(unavailable=True)` and must not mask annual-report repository failures.
- `StructuredFundDataBundle` already contains `nav_data`, but `report_evidence.py` currently does not project `nav_data` into report facts and `DerivedCalculation` is reserved for a future calculation-source gate.
- The design describes bond-fund `preferred_lens` as focusing on credit risk, duration, and max drawdown, so quantitative drawdown evidence is within the accepted fund-domain problem, but not yet implemented as a reviewed derived evidence contract.

### Control Truth: `docs/implementation-control.md`

- Current phase is release maintenance. The next entry point is `drawdown_stress evidence contract / NAV-derived risk metric design gate`.
- The Startup Packet says 006597 / 2024 `credit_risk` and `redemption_share_pressure` false negatives are repaired and locally validated.
- The remaining bond blocker is `bond_risk_evidence_missing.baseline_blocking=true` because `drawdown_stress` is weak qualitative evidence under the current contract.
- The allowed scope is plan/review before implementation, defining a separate contract for NAV-derived or other quantitative max drawdown / volatility evidence, preserving evidence-strength distinctions, keeping qualitative drawdown-control text weak, and not changing FQ0-FQ6 behavior.
- The control doc still labels the next gate as `standard`, but the current handoff explicitly upgrades it to `heavy`. This plan follows the newer handoff because the gate changes public evidence contract and score semantics.

### Accepted Prior Judgment

`docs/reviews/release-maintenance-section2-crosscheck-unit-suffix-repair-controller-judgment-20260528.md` records:

- `redemption_share_pressure` is no longer missing / ambiguous for real 006597 / 2024.
- Latest satisfied groups are `duration_rate_risk`, `credit_risk`, `leverage_liquidity`, `asset_allocation_holdings_mix`, `redemption_share_pressure`, and `convertible_bond_equity_exposure`.
- Latest weak group is only `drawdown_stress`.
- Score still reports `bond_risk_evidence_missing.baseline_blocking=true` with `missing_evidence_groups=["drawdown_stress"]`.
- The next gate must decide whether and how to source quantitative max drawdown / volatility / stress evidence and must not upgrade qualitative `控制回撤` text to strong evidence without a reviewed contract.

`docs/reviews/code-review-20260528-081225.md` records:

- `extract_bond_risk_evidence()` consumes an already parsed `ParsedAnnualReport` and does not call `FundDocumentRepository`, cache helpers, download helpers, Service/UI/Host/Agent, or dayu internals.
- `FundDataExtractor.extract()` remains the production boundary that loads annual reports through `self._repository.load_annual_report(...)` before calling bond-risk extraction.
- Drawdown remains intentionally weak for qualitative `控制回撤` text with `na_reason="drawdown_metric_not_found"`.
- Score policy remains fail-closed: missing, malformed, no-anchor, weak, or ambiguous bond-risk records keep unsatisfied groups and preserve the blocker.
- Quality gate projection remains `FQ2F/warn`; FQ0-FQ6 thresholds were not weakened.

### Latest Artifacts

Latest snapshot:

- `reports/extraction-snapshots/bond-risk-crosscheck-suffix-006597-2024-20260528/snapshot.jsonl`
- `bond_risk_evidence` row has `value_present=true`, `anchor_present=true`, `bond_risk_contract_status="partial"`, satisfied groups all except `drawdown_stress`, `bond_risk_weak_groups=["drawdown_stress"]`, and no missing / ambiguous groups.
- `nav_data` row has `value_present=true`, `anchor_present=false`, `note="source=nav_cache; cached=True; records=1802"`.

Latest score:

- `reports/scoring-runs/bond-risk-crosscheck-suffix-006597-2024-20260528/score.json`
- `score_applicability_issues[0].issue_code="bond_risk_evidence_missing"`.
- `baseline_blocking=true`.
- `missing_evidence_groups=["drawdown_stress"]`.

Latest quality gate:

- `reports/quality-gate-runs/bond-risk-crosscheck-suffix-006597-2024-20260528/quality_gate.json`
- `status="warn"`.
- A projected `FQ2F` issue with `reason="bond_risk_evidence_missing"` remains. This is expected and must remain until score no longer emits the blocker for contract-valid reasons.

## Direct Code Evidence

- `fund_agent/fund/data_extractor.py` defines `_NavDataProvider` and loads NAV through `nav_provider.load_nav_data(...)`. NAV exceptions are converted to `NavDataResult(unavailable=True)`, while repository failures are not masked.
- `fund_agent/fund/data/nav_data.py` currently returns raw Akshare/Eastmoney-shaped records and caches them in SQLite. For 006597, the current cache sample contains `净值日期`, `单位净值`, and `日增长率`; it does not by itself prove a dividend-adjusted / cumulative total-return series.
- `fund_agent/fund/extractors/bond_risk_evidence.py` currently accepts annual-report table-backed `最大回撤` as `quantitative_direct`; otherwise `控制回撤` / `回撤` text is `status="weak"`, `strength="qualitative_control_intent"`, `measurement_kind="control_intent"`, `na_reason="drawdown_metric_not_found"`.
- `fund_agent/fund/extractors/models.py` currently validates accepted groups against `quantitative_direct` or `qualitative_direct` only. It requires accepted/weak groups to have parseable anchor refs using the annual-report-oriented `bond-risk:<fund_code>:<report_year>:<group_id>:<ordinal>` ID format.
- `fund_agent/fund/extraction_snapshot.py` builds `bond_risk_evidence` records using `_first_annual_report_anchor(...)`; NAV-derived evidence would otherwise have no traceable snapshot anchor.
- `fund_agent/fund/extraction_score.py` treats a bond-risk record with no `value_present`, no `anchor_present`, malformed group sets, `missing`, `weak`, `ambiguous`, or groups absent from satisfied as unsatisfied. This is the right blocker behavior and must be preserved.
- `fund_agent/fund/quality_gate.py` only projects score applicability issues into `FQ2F/warn`; it should not decide whether NAV-derived evidence is valid.

## Contract Decision

### Decision

`drawdown_stress` may accept NAV-derived quantitative evidence, but only under a new explicit derived-evidence contract. Accepted quantitative drawdown evidence does not have to come only from the annual report.

The accepted source hierarchy for `drawdown_stress` should be:

1. Annual-report direct quantitative metric, unchanged: table-backed max drawdown / volatility / stress metric with annual-report anchor.
2. Public NAV-derived quantitative metric, new: total-return NAV series from the unified NAV data access boundary, with explicit provenance, calculation method, period, data-quality checks, and derived anchor.
3. Annual-report qualitative control text, unchanged: weak evidence only, never sufficient.
4. Missing / unavailable / ambiguous, unchanged: unsatisfied and baseline-blocking.

### Why NAV-Derived Evidence Is Acceptable

Maximum drawdown and realized volatility are deterministic functions of a public NAV return series. They are not managerial intent claims and do not require annual-report narrative disclosure if the NAV source, adjustment basis, window, formula, and data quality are explicit and reproducible. The repository already treats NAV as part of the P1/P2 data bundle, so this is not a new UI/Service/Host boundary.

### Why Current NAV Data Is Not Sufficient By Itself

The current 006597 cache row shows `单位净值` and `日增长率`; this does not by itself establish a dividend-adjusted total-return series. A plan that directly computes max drawdown from unadjusted unit NAV would risk overstating drawdown around distributions. Therefore implementation must either normalize a cumulative / adjusted / total-return NAV series or fail closed.

## Required Contract Fields

Do not pass any of these through `extra_payload` or free-form dicts. They must be explicit typed fields.

Add or equivalent typed contract fields for `BondRiskEvidenceGroupRecord` and supporting dataclasses:

- `evidence_source`: `annual_report_direct | public_nav_series_derived`
- `metric_name`: existing field; for NAV path use stable values such as `max_drawdown`, `annualized_volatility`, `worst_20_observation_return`
- `metric_value`: existing field; store a stable formatted summary, not just prose
- `metric_unit`: existing field; use `ratio`
- `period_label`: existing field; use `2024-01-01..2024-12-31` style
- `period_start`: new explicit ISO date
- `period_end`: new explicit ISO date
- `calculation_method`: `disclosed | total_return_nav_max_drawdown_daily | total_return_nav_annualized_volatility_daily | total_return_nav_worst_20_observation_return`
- `provenance`: typed `BondRiskMetricProvenance | None`
- `source_anchor_ids`: existing field; NAV-derived records must still reference a stable derived anchor

Add typed `BondRiskMetricProvenance` or equivalent with explicit fields:

- `source_kind`: `annual_report | public_nav_series`
- `source_name`: e.g. `akshare.fund_open_fund_info_em`
- `origin_source_name`: underlying public source where available, e.g. Eastmoney via Akshare
- `cached`: bool
- `cache_updated_at`: ISO timestamp or `None`
- `fund_code`
- `series_type`: `total_return_nav | cumulative_nav | adjusted_nav`
- `adjustment_basis`: `cumulative_nav | provider_adjusted_nav | source_daily_return_compounded`
- `observation_count`
- `first_observation_date`
- `last_observation_date`
- `max_calendar_gap_days`
- `missing_trading_day_policy`: stable literal, e.g. `observed_nav_dates_no_imputation`
- `data_quality_status`: `accepted | fail_closed`
- `data_quality_reason`

Extend evidence strength / measurement literals:

- Add `quantitative_derived` to `BondRiskEvidenceStrength`.
- Add `calculated_metric` to `BondRiskEvidenceMeasurementKind`.
- Allow `status="accepted"` only when `strength in {"quantitative_direct", "qualitative_direct", "quantitative_derived"}` and derived provenance is present for `quantitative_derived`.

Anchor format:

- Keep existing stable `anchor_id` grammar unless the implementation proves a parser change is safer: `bond-risk:<fund_code>:<report_year>:drawdown_stress:<ordinal>`.
- Extend `BondRiskEvidenceAnchorRef` explicitly with `source_kind`, `source_name`, and `provenance_ref`.
- For NAV-derived anchor refs, use `section_id=None`, `page_number=None`, `table_id=None`, `row_locator="nav_series:<period_start>..<period_end>:observations=<n>"`, `evidence_role="nav_derived_drawdown_stress_metric"`.
- Add matching `EvidenceAnchor(source_kind="derived" or "external_api", document_year=None, section_id=None, row_locator=...)` so snapshot can mark the field traceable without pretending it came from an annual-report section.

## NAV Data Boundary

All NAV series access must stay inside Agent-layer `fund_agent/fund/data` and be orchestrated by `FundDataExtractor`. No extractor may read SQLite/cache files directly and no extractor may ad hoc scrape web pages.

Implementation boundary:

- `FundNavDataAdapter` remains the production provider.
- Add a typed normalization API, for example `load_total_return_nav_series(fund_code, *, force_refresh=False) -> NavSeriesResult`, or add a method on the existing provider protocol with explicit return type.
- `FundDataExtractor.extract()` may pass typed NAV-derived risk metric input into bond-risk extraction or call a separate metric calculator before composing `bond_risk_evidence`.
- `extract_bond_risk_evidence()` must not call the NAV provider itself. It may accept an explicit `drawdown_stress_metric` / `nav_risk_metrics` parameter from the façade. This keeps source access in the façade/data layer and extraction logic deterministic.

NAV cache provenance:

- Current `NavDataResult.source="nav_cache"` loses the underlying origin source in the public result even though SQLite stores `source`. Add explicit origin metadata rather than inferring from cache path.
- Legacy cache rows without origin source, series type, or update timestamp must be accepted for raw `nav_data` availability but must be fail-closed for `drawdown_stress` satisfaction.

## NAV-Derived Metric Method

### Source Series

Accepted derived evidence requires a total-return-equivalent NAV level series:

- Preferred: cumulative NAV / accumulated NAV from the public source.
- Accepted equivalent: provider-adjusted NAV explicitly marked as adjusted/复权.
- Conditional accepted equivalent: source-provided daily return compounded only if the adapter documents that the daily return is total-return-equivalent and the raw record contains the required return field for all observations.
- Not accepted: unadjusted `单位净值` alone.

### Time Window

For annual-report year `Y`, compute on the report-year calendar window:

- `period_start = Y-01-01`
- `period_end = Y-12-31`
- Use observations with `period_start <= nav_date <= period_end`.
- Sort by `nav_date`; reject duplicate dates with conflicting values.

Coverage requirements for a full-year fund:

- `first_observation_date <= Y-01-10`
- `last_observation_date >= Y-12-20`
- `observation_count >= 200`
- `max_calendar_gap_days <= 10`

If the fund inception date or termination date is in the report year and is explicitly available from `basic_identity`, a later gate may define a shortened-window rule. This gate should not infer shortened windows silently; absent an explicit shortened-window contract, fail closed.

### Missing Trading Days

- Do not impute missing trading days.
- Compute metrics only on observed NAV publication dates.
- Record `missing_trading_day_policy="observed_nav_dates_no_imputation"`.
- Fail closed when coverage thresholds above are not met.

### Formulas

Let `x_t` be the accepted total-return NAV level for observation `t`, strictly positive and sorted by date.

Maximum drawdown:

```text
running_peak_t = max(x_0 ... x_t)
drawdown_t = x_t / running_peak_t - 1
max_drawdown = min(drawdown_t)
max_drawdown_abs = abs(max_drawdown)
```

Daily log return:

```text
r_t = ln(x_t / x_{t-1}), for t >= 1
```

Annualized volatility:

```text
annualized_volatility = sample_stddev(r_t) * sqrt(252)
```

Stress metric:

```text
rolling_20_observation_return_t = x_t / x_{t-20} - 1, for t >= 20
worst_20_observation_return = min(rolling_20_observation_return_t)
```

Acceptance requires at least `max_drawdown` and one of `annualized_volatility` or `worst_20_observation_return` to be computed from the same accepted series. The `drawdown_stress` group can be satisfied by the derived metric set, not by any qualitative text.

### Formatting

Store ratios as decimal strings with enough precision for audit, for example:

```text
max_drawdown=-0.012345; annualized_volatility=0.018765; worst_20_observation_return=-0.006789; observations=244; period=2024-01-01..2024-12-31; method=total_return_nav
```

Do not round before calculations. Display rounding, if any, belongs to rendering, not this evidence contract.

## Fail-Closed Conditions

`drawdown_stress` must remain weak or missing, and score must keep the blocker, if any of these occur:

- NAV provider unavailable or `NavDataResult.unavailable=True`.
- NAV source is outside the explicit allowlist / typed adapter boundary.
- Implementation can only access unadjusted `单位净值` and cannot prove total-return / cumulative / adjusted treatment.
- Missing origin source, series type, cache timestamp, or calculation provenance for a cached series.
- No observations in the report-year window.
- First / last observation or observation count does not meet window coverage thresholds.
- `max_calendar_gap_days > 10`.
- Duplicate dates with conflicting values.
- Non-positive NAV values, malformed dates, malformed decimals, or non-monotonic duplicate handling ambiguity.
- Calculated metric is `NaN`, infinite, or cannot be represented as a stable finite decimal.
- Fund code or report year does not match the current bundle.
- Derived anchor cannot be serialized into snapshot output.
- Score sees malformed bond-risk group sets, no traceable anchor, weak group, ambiguous group, or missing group.

## Qualitative Drawdown Text Rule

Annual-report text such as `控制回撤`, `保持净值稳定`, or generic `回撤` language remains:

- `status="weak"`
- `strength="qualitative_control_intent"`
- `measurement_kind="control_intent"`
- `na_reason="drawdown_metric_not_found"`

It must never be converted into `quantitative_direct`, `quantitative_derived`, `actual_metric`, or `calculated_metric`. If NAV-derived evidence is accepted, the accepted status is based only on the derived metric and its provenance; the qualitative text is at most contextual and not the satisfying evidence.

## Snapshot / Score / Quality Gate Decision

Snapshot changes are required.

- Current `bond_risk_evidence` snapshot uses `_first_annual_report_anchor(...)`. That is insufficient for NAV-derived evidence.
- Add explicit traceability output for bond-risk evidence that can represent annual-report, external API, and derived anchors.
- Either add generic `anchor_source_kind` fields to `SnapshotRecord`, or add bond-risk-specific fields such as `bond_risk_evidence_source_kinds`, `bond_risk_metric_names`, `bond_risk_calculation_methods`, and `bond_risk_provenance_status`.
- Do not make `nav_data` itself a report fact or correctness-comparable field in this gate.

Score changes are required.

- `_bond_risk_unsatisfied_groups()` must continue to fail closed for no value, no traceable anchor, malformed groups, weak groups, ambiguous groups, and absent satisfied groups.
- It may treat `drawdown_stress` as satisfied only when the snapshot row declares the group satisfied and has traceable annual or derived provenance.
- `baseline_blocking=true` remains whenever `drawdown_stress` is weak/missing/ambiguous or derived provenance fails.

Quality gate changes should be minimal.

- FQ0-FQ6 definitions and thresholds must not change.
- `quality_gate.py` should continue projecting `score_applicability_issues` to `FQ2F/warn`.
- If score no longer emits `bond_risk_evidence_missing` because all seven groups are contract-satisfied, quality gate naturally has no bond-risk FQ2F issue. That is not a weakening of FQ0-FQ6; it is a stricter upstream evidence contract producing a different score input.

## Affected Files / Modules

Allowed for later implementation, subject to approved plan review:

- `fund_agent/fund/data/nav_data.py`
- `fund_agent/fund/data/__init__.py`
- `fund_agent/fund/data_extractor.py`
- `fund_agent/fund/extractors/models.py`
- `fund_agent/fund/extractors/bond_risk_evidence.py`
- `fund_agent/fund/extraction_snapshot.py`
- `fund_agent/fund/extraction_score.py`
- `fund_agent/fund/quality_gate.py` only if needed for schema tolerance; no FQ semantic changes
- `fund_agent/fund/README.md`
- `tests/fund/data/test_nav_data.py`
- `tests/fund/test_data_extractor.py`
- `tests/fund/extractors/test_bond_risk_evidence.py`
- `tests/fund/test_extraction_snapshot.py` or nearest existing snapshot tests
- `tests/fund/test_extraction_score.py`
- `tests/fund/test_quality_gate.py` only for unchanged projection behavior
- `tests/README.md`

Explicitly not allowed:

- Golden fixtures / promoted baseline fixtures.
- QDII, FOF, 110020, golden-readiness, release-readiness, Host/Agent/dayu, PR/push/merge.
- UI/Service public behavior outside the existing deterministic extraction/scoring path.
- Direct annual-report PDF/cache/source helper access outside `FundDocumentRepository`.
- Direct NAV cache reads inside bond-risk extractor.

## Implementation Slices If Approved

### Slice 1: NAV Series Normalization And Provenance

Objective: create a typed total-return NAV series boundary inside `fund_agent/fund/data`.

Allowed changes:

- Add typed dataclasses such as `NavSeriesObservation`, `NavSeriesProvenance`, `NavSeriesResult`.
- Normalize raw Akshare/Eastmoney-shaped records into explicit date/value/series-type observations.
- Preserve `source_name`, `origin_source_name`, `cached`, `cache_updated_at`, `series_type`, and `adjustment_basis`.
- Add fail-closed result for unsupported unit-NAV-only series.
- Keep existing `load_nav_data()` behavior compatible for current callers.

Tests:

- cache hit preserves origin source and timestamp for derived metric provenance.
- unit-NAV-only records are available as raw `nav_data` but not accepted as total-return series.
- cumulative / adjusted NAV records normalize to sorted positive observations.
- malformed date, non-positive NAV, duplicate conflicting date, missing provenance fail closed.

Stop condition:

- If no reliable total-return / cumulative / adjusted NAV source can be represented through the existing provider, stop with blocked-with-decision. Do not compute accepted metrics from unit NAV.

### Slice 2: NAV Risk Metric Calculator

Objective: compute max drawdown, annualized volatility, and worst 20-observation return from accepted total-return NAV observations.

Allowed changes:

- Add a small pure calculator module under `fund_agent/fund/data` or `fund_agent/fund/analysis`, but keep source access out of the calculator.
- Implement the formulas and coverage thresholds in named constants.
- Return a typed result with metric values, period, observation count, max gap, method, and fail-closed reason.

Tests:

- deterministic max drawdown on a known series.
- volatility and worst-20 formulas on fixture data.
- no imputation for missing dates.
- fail closed for insufficient count, period coverage gap, excessive max calendar gap, and malformed values.

### Slice 3: Bond-Risk Contract Extension

Objective: allow `quantitative_derived` `drawdown_stress` records with explicit provenance and derived anchor.

Allowed changes:

- Extend `BondRiskEvidenceStrength`, `BondRiskEvidenceMeasurementKind`, and validation rules.
- Add explicit derived metric/provenance fields.
- Extend `BondRiskEvidenceAnchorRef` to identify non-annual source kind and provenance.
- Preserve annual direct quantitative path unchanged.
- Preserve qualitative control-intent path as weak.

Tests:

- `quantitative_derived` drawdown with provenance validates and enters `satisfied_group_ids`.
- missing provenance for `quantitative_derived` raises `ValueError`.
- qualitative `控制回撤` remains weak and unsatisfied.
- accepted annual-report `最大回撤` path remains accepted.

### Slice 4: DataExtractor Composition Boundary

Objective: pass derived NAV risk metrics into bond-risk evidence without letting the extractor access NAV provider/cache directly.

Allowed changes:

- Extend `_NavDataProvider` protocol or `FundDataExtractor` orchestration with explicit NAV series / risk metric call.
- Call annual-report extractor and NAV metric calculator in `FundDataExtractor.extract()`.
- Pass `drawdown_stress_metric` explicitly into bond-risk evidence composition.
- Preserve NAV provider failure degradation for the general bundle, while derived metric failures produce unsatisfied `drawdown_stress`, not annual-report extraction failure.

Tests:

- repository failure is still not masked and NAV is not called.
- NAV unavailable keeps annual fields extracted and keeps `drawdown_stress` weak/missing.
- valid NAV metric satisfies `drawdown_stress`.
- invalid NAV metric does not override weak qualitative text.

### Slice 5: Snapshot / Score Traceability

Objective: make snapshot and score understand derived bond-risk provenance without weakening blockers.

Allowed changes:

- Snapshot emits traceable source kind and metric metadata for bond-risk evidence.
- Score accepts a satisfied `drawdown_stress` only if derived traceability is present and group sets are well-formed.
- Score continues emitting `bond_risk_evidence_missing` with `missing_evidence_groups=["drawdown_stress"]` for weak or invalid NAV cases.

Tests:

- snapshot row for NAV-derived accepted drawdown has `anchor_present=true` or equivalent traceable anchor flag plus source kind/provenance.
- score has no bond-risk applicability issue only when all seven groups are satisfied and derived traceability is valid.
- score emits blocker for weak qualitative only, unit-NAV-only, missing provenance, malformed anchor, or partial group sets.

### Slice 6: Quality Gate And Real Validation

Objective: verify FQ0-FQ6 semantics remain unchanged.

Allowed changes:

- Only schema-tolerance or fixture-helper updates if quality gate tests require reading new score metadata.
- No FQ thresholds, severities, rule codes, or blocker semantics change.

Validation:

- targeted unit tests above.
- `uv run ruff check .`
- `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q`
- real 006597 / 2024 snapshot / score / quality gate rerun only after tests pass.

Expected real outcomes:

- If the provider can produce accepted total-return NAV series for 006597 / 2024, snapshot should show all seven bond-risk groups satisfied, score should stop emitting `bond_risk_evidence_missing`, and quality gate should no longer include the bond-risk FQ2F issue. Other existing P1 warnings may remain.
- If the provider only has unit NAV or insufficient provenance, the real outcome must remain the current blocker with `missing_evidence_groups=["drawdown_stress"]`.

## Tests And Validation Matrix

Required targeted commands after implementation:

```bash
uv run pytest tests/fund/data/test_nav_data.py -q
uv run pytest tests/fund/test_data_extractor.py -q
uv run pytest tests/fund/extractors/test_bond_risk_evidence.py -q
uv run pytest tests/fund/test_extraction_score.py -q
uv run pytest tests/fund/test_quality_gate.py -q
```

Required full validation:

```bash
uv run ruff check .
uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q
```

Required real smoke, using the repository/CLI entrypoints already used by prior gates:

- 006597 / 2024 annual report smoke through `FundDocumentRepository`.
- 006597 / 2024 extraction snapshot rerun.
- 006597 / 2024 extraction score rerun.
- 006597 / 2024 quality gate rerun.

Assertions:

- Annual-report access still goes through `FundDocumentRepository`.
- Bond-risk extractor does not access cache, source helper, network, Service/UI/Host/dayu, or `FundDocumentRepository`.
- Qualitative drawdown text remains weak.
- Unit-NAV-only series fails closed for accepted drawdown.
- Total-return / cumulative / adjusted NAV series with complete provenance can satisfy `drawdown_stress`.
- FQ0-FQ6 rule codes, severities, and thresholds remain unchanged.

## Docs Decision

If implementation proceeds, update:

- `fund_agent/fund/README.md` because `fund_agent/fund/` behavior, bond-risk evidence, NAV-derived calculations, snapshot/score semantics, and data boundary change.
- `tests/README.md` because new NAV/risk metric/snapshot/score tests will define maintenance rules.
- `docs/design.md` only after implementation and review acceptance, because this gate changes the current design truth for `bond_risk_evidence.v1` and derived NAV risk metrics.
- `docs/implementation-control.md` only through controller closeout / judgment, not by the implementation worker.

Do not update root `README.md` unless CLI user-facing commands or output guarantees change.

## Stop Conditions

Stop and return to controller if:

- Controller does not accept NAV-derived evidence as a valid source class.
- The provider cannot expose total-return / cumulative / adjusted NAV through the unified data boundary.
- Implementation would need direct web scraping or direct cache reads inside the extractor.
- Implementation would require changing UI/Service/Host/Agent/dayu boundaries.
- Implementation would weaken FQ0-FQ6, turn missing evidence into pass, or remove `baseline_blocking` without all seven groups satisfying the explicit contract.
- Golden fixture promotion, release readiness, PR/push/merge, QDII/FOF/110020, or Host/Agent/dayu work becomes necessary.

## Risks And Open Questions

### Blocking Questions For Controller

1. Confirm the contract decision: may `drawdown_stress` accept `public_nav_series_derived` quantitative evidence when the series is total-return-equivalent, provenance-complete, and fail-closed?
2. Confirm the NAV source allowlist for this gate. Recommended: only the existing `FundNavDataAdapter` Akshare/Eastmoney path, represented through typed provenance; no new source or scraping.
3. Confirm whether implementation should stop if the current provider cannot supply cumulative / adjusted / total-return data for 006597, leaving the blocker in place, rather than accepting unit-NAV-only calculations.

### Non-Blocking Risks

- Existing cache rows may lack enough origin metadata for derived acceptance. Working assumption: legacy raw `nav_data` can remain available, but derived drawdown acceptance requires refreshed or provenance-complete series.
- Adding derived-source anchors may touch snapshot schema. This is acceptable only if score remains fail-closed for old/malformed rows.
- Real 006597 outcome is data-dependent. Passing implementation tests does not guarantee blocker removal; blocker removal requires accepted total-return NAV data in the real run.

## Completion Report Format For Later Implementation

Implementation worker must report:

- Self-check status: assigned slice, allowed files, no commit/push/PR, no scope drift.
- Changed files.
- Contract fields added and source-boundary decisions implemented.
- How annual-report direct, NAV-derived, weak qualitative, missing, and fail-closed paths behave.
- Validation commands and results.
- Real 006597 / 2024 snapshot / score / quality gate outcome, including whether `missing_evidence_groups` still contains `drawdown_stress`.
- Residual risks classified with owner / next gate.

## Plan Conclusion

Implementation is recommended only if the controller accepts NAV-derived quantitative evidence as a valid source class under the explicit contract above.

The plan does not recommend weakening the current blocker. If total-return NAV provenance cannot be established, `drawdown_stress` must remain weak / unsatisfied and `bond_risk_evidence_missing.baseline_blocking=true` must remain.

