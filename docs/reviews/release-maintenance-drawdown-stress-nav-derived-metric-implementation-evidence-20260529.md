# Drawdown Stress NAV-Derived Metric Implementation Evidence

日期：2026-05-29

角色：implementation worker only。未 commit、未 push、未创建 PR、未修改 golden fixture、未修改 score policy、quality gate FQ0-FQ6、baseline_blocking 或 snapshot schema。

## Source Of Truth

- Accepted plan：`docs/reviews/release-maintenance-drawdown-stress-nav-derived-metric-implementation-plan-20260529.md`
- Plan reviews / rereviews：
  - `docs/reviews/release-maintenance-drawdown-stress-nav-derived-metric-implementation-plan-review-glm-20260529.md`
  - `docs/reviews/release-maintenance-drawdown-stress-nav-derived-metric-implementation-plan-review-mimo-20260529.md`
  - `docs/reviews/release-maintenance-drawdown-stress-nav-derived-metric-implementation-plan-rereview-glm-20260529.md`
  - `docs/reviews/release-maintenance-drawdown-stress-nav-derived-metric-implementation-plan-rereview-mimo-20260529.md`
- Rules/design/control re-read before coding：`AGENTS.md`、`docs/design.md`、`docs/implementation-control.md`

## Implementation Review Fix

GLM implementation review L1 follow-up applied after the initial evidence run:

- `fund_agent/fund/extractors/bond_risk_evidence.py` now builds the NAV-derived drawdown summary from `report.key.year` instead of hardcoded `2024`.
- `tests/fund/extractors/test_bond_risk_evidence.py` adds a non-2024 report-context regression assertion; the fixture intentionally keeps the drawdown metric helper unchanged and verifies report-year precedence.
- No score policy, quality gate, snapshot schema, golden fixture, or provenance contract change.

Focused validation for this fix:

```text
uv run ruff check fund_agent/fund/extractors/bond_risk_evidence.py tests/fund/extractors/test_bond_risk_evidence.py
All checks passed!
```

```text
uv run pytest tests/fund/extractors/test_bond_risk_evidence.py -q
62 passed in 0.76s
```

Full validation was not rerun for this one-line behavior fix plus focused regression test; the controller handoff explicitly leaves any broader rerun decision to the controller.

## Changed Files

Production:

- `fund_agent/fund/data/nav_metrics.py`
- `fund_agent/fund/data/__init__.py`
- `fund_agent/fund/data_extractor.py`
- `fund_agent/fund/extractors/models.py`
- `fund_agent/fund/extractors/bond_risk_evidence.py`
- `fund_agent/fund/extraction_snapshot.py`
- `docs/design.md`
- `fund_agent/fund/README.md`
- `tests/README.md`

Tests:

- `tests/fund/data/test_nav_metrics.py`
- `tests/fund/test_data_extractor.py`
- `tests/fund/extractors/test_bond_risk_evidence.py`
- `tests/fund/test_extraction_snapshot.py`
- `tests/fund/test_quality_gate.py`

Unchanged by this implementation:

- `fund_agent/fund/extraction_score.py`
- `fund_agent/fund/quality_gate.py`
- golden fixtures
- generated report fixtures
- unrelated untracked `--help`、old repo-review/comprehensive audit docs、`docs/tmux-agent-memory-store.md`、`reviews/`

## Slice Summary

1. Metric helper:
   - Added `NavMaxDrawdownMetric`.
   - Added `calculate_max_drawdown_from_nav_series()` based only on `FundNavSeries.records`.
   - Requires `accumulated_nav / accumulated_nav / verified / strong_drawdown_evidence_eligible=True`.
   - Independently checks period-filtered `minimum_records`; rejects duplicate dates, non-positive NAV, raw-unit/ineligible series and invalid period.
   - Added `format_max_drawdown_percent()`.

2. `bond_risk_evidence.v1` contract extension:
   - Added `quantitative_derived` strength and `derived_metric` measurement kind.
   - Accepted strengths now include `quantitative_derived`.
   - Validator hardening implemented: `strength="quantitative_derived"` requires `measurement_kind="derived_metric"`; `actual_metric` / `actual_exposure` / other measurement kinds are rejected.
   - `drawdown_stress` can now be accepted as NAV-derived quantitative metric.
   - Weak annual-report control text remains weak when no metric is available.

3. Data extractor wiring:
   - Added typed `_NavSeriesRepository` protocol and constructor injection.
   - `FundDataExtractor.extract()` calls typed repository only for exact `bond_fund`.
   - Repository call uses explicit params: `fund_code`, `share_class="A"`, `start_date=YYYY-01-01`, `end_date=YYYY-12-31`, `minimum_records=30`, `force_refresh`.
   - `bond_risk_evidence.py` does not perform IO and does not call CSRC/source helpers directly.
   - NAV contract errors degrade to weak/missing `drawdown_stress` so score/quality continue to block naturally.

4. Snapshot / score / quality natural path:
   - Added derived-only anchor projection test.
   - Narrow production compatibility fix in `extraction_snapshot.py`: snapshot now prefers the first annual-report anchor, but if a field has only derived anchors it projects the first traceable anchor. No schema fields were added.
   - No production change to `extraction_score.py`; existing `test_weak_drawdown_bond_risk_evidence_issue_lists_only_drawdown_group` covers the failure-path blocker regression where only `drawdown_stress` remains unsatisfied.
   - Added quality gate test proving no `bond_risk_evidence_missing` FQ2F is generated when score has no such applicability issue.

5. Docs:
   - Updated `docs/design.md`, `fund_agent/fund/README.md`, and `tests/README.md` for the implemented current behavior.
   - Documented max drawdown only, A-class annual period, derived provenance, fail-closed behavior, and volatility/golden/FQ non-goals.

## Production Change Justification

`fund_agent/fund/extraction_snapshot.py` was changed because derived-only `bond_risk_evidence` anchors would otherwise lose field-level traceability: previous projection selected only `source_kind="annual_report"`. The fix is narrow:

- Prefer annual-report anchors exactly as before.
- If no annual-report anchor exists, project the first available traceable anchor, including `source_kind="derived"`.
- No snapshot schema addition.
- No score threshold, score policy, issue severity, `baseline_blocking`, FQ semantics, quality gate, or golden fixture change.

`fund_agent/fund/extraction_score.py` was not modified.

## Validation

Focused:

```text
uv run pytest tests/fund/data/test_nav_metrics.py -q
6 passed in 0.09s
```

```text
uv run pytest tests/fund/extractors/test_bond_risk_evidence.py -q
61 passed in 0.82s
```

```text
uv run pytest tests/fund/test_data_extractor.py -q
10 passed in 0.59s
```

```text
uv run pytest tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py -q
99 passed in 0.82s
```

```text
uv run ruff check fund_agent/fund/data/nav_metrics.py fund_agent/fund/data_extractor.py fund_agent/fund/extractors/models.py fund_agent/fund/extractors/bond_risk_evidence.py fund_agent/fund/extraction_snapshot.py tests/fund/data/test_nav_metrics.py tests/fund/test_data_extractor.py tests/fund/extractors/test_bond_risk_evidence.py tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py
All checks passed.
```

```text
uv run pytest tests/fund/data/test_nav_metrics.py tests/fund/test_data_extractor.py tests/fund/extractors/test_bond_risk_evidence.py tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py -q
176 passed in 0.79s
```

Full:

```text
uv run ruff check .
All checks passed.
```

```text
uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q
938 passed in 4.58s
Total coverage: 92.42%
```

## Real CSRC EID NAV Smoke

Primary A-class annual-period command computed 006597/A 2024 max drawdown:

```text
006597 A accumulated_nav accumulated_nav verified True 1807 2018-12-18 2026-05-28 csrc_eid 5755:2030-1010
metric 006597 A 2024-01-01 2024-12-31 243 -0.0010059518819683125157179982 -0.10% 2024-09-26 1.1929 2024-10-09 1.1917
006598 C accumulated_nav accumulated_nav verified True 1807 2018-12-18 2026-05-28 csrc_eid 5755:2030-1020
014217 E accumulated_nav accumulated_nav verified True 994 2022-04-25 2026-05-28 csrc_eid 5755:2030-1040
```

The same command attempted `022176/F` for `2024-01-01..2024-12-31` and failed closed with `missing_date_range` because F class starts at `2024-10-08`. This is expected and not used as 006597/A evidence.

Follow-up source-inception smoke for F:

```text
006597 A 2024-01-01 2024-12-31 accumulated_nav accumulated_nav verified True 1807 2018-12-18 2026-05-28 csrc_eid 5755:2030-1010
006598 C 2024-01-01 2024-12-31 accumulated_nav accumulated_nav verified True 1807 2018-12-18 2026-05-28 csrc_eid 5755:2030-1020
014217 E 2024-01-01 2024-12-31 accumulated_nav accumulated_nav verified True 994 2022-04-25 2026-05-28 csrc_eid 5755:2030-1040
022176 F 2024-10-08 2024-12-31 accumulated_nav accumulated_nav verified True 398 2024-10-08 2026-05-28 csrc_eid 5755:2030-1050
```

## Real 006597 Extraction / Score / Quality

Commands:

```text
uv run fund-analysis extraction-snapshot --run-id bond-risk-drawdown-nav-006597-2024-20260529 --fund-code 006597 --report-year 2024 --force-refresh
```

```text
uv run fund-analysis extraction-score --snapshot-path reports/extraction-snapshots/bond-risk-drawdown-nav-006597-2024-20260529/snapshot.jsonl --errors-path reports/extraction-snapshots/bond-risk-drawdown-nav-006597-2024-20260529/errors.jsonl --output-dir reports/scoring-runs/bond-risk-drawdown-nav-006597-2024-20260529
```

```text
uv run fund-analysis quality-gate --score-path reports/scoring-runs/bond-risk-drawdown-nav-006597-2024-20260529/score.json --output-dir reports/quality-gate-runs/bond-risk-drawdown-nav-006597-2024-20260529
```

Outputs:

```text
snapshot: reports/extraction-snapshots/bond-risk-drawdown-nav-006597-2024-20260529/snapshot.jsonl
score_json: reports/scoring-runs/bond-risk-drawdown-nav-006597-2024-20260529/score.json
quality_gate_json: reports/quality-gate-runs/bond-risk-drawdown-nav-006597-2024-20260529/quality_gate.json
quality status: warn
quality issue_count: 6
```

Assertions:

```text
snapshot_status satisfied
snapshot_satisfied ['duration_rate_risk', 'credit_risk', 'leverage_liquidity', 'asset_allocation_holdings_mix', 'drawdown_stress', 'redemption_share_pressure', 'convertible_bond_equity_exposure']
snapshot_missing []
snapshot_weak []
snapshot_ambiguous []
score_applicability_issue_count 0
score_bond_missing []
quality_status warn issue_count 6
quality_bond_missing []
quality_rules [('FQ2', 'turnover_rate', None), ('FQ2', 'holder_structure', None), ('FQ2', 'share_change', None), ('FQ2F', None, None), ('FQ0', None, 'not_configured'), ('FQ4', None, None)]
```

The remaining quality warnings are unrelated to this gate:

- `FQ2` for `turnover_rate`
- `FQ2` for `holder_structure`
- `FQ2` for `share_change`
- fund-level `FQ2F` for P1 failed fields
- `FQ0` strict golden not configured
- `FQ4` missing field rate

No `FQ2F` issue with `reason="bond_risk_evidence_missing"` remains.

Direct extractor provenance confirmation:

```text
group accepted quantitative_derived derived_metric 最大回撤 -0.10% ratio 2024-01-01 至 2024-12-31 ('bond-risk:006597:2024:drawdown_stress:1',) None
ref BondRiskEvidenceAnchorRef(anchor_id='bond-risk:006597:2024:drawdown_stress:1', section_id='derived:nav', page_number=None, table_id=None, row_locator='metric:max_drawdown:A:2024-01-01:2024-12-31', evidence_role='derived_max_drawdown_metric')
extractor_anchor derived 2024 derived:nav None None metric:max_drawdown:A:2024-01-01:2024-12-31
note source=CSRC EID; source_name=csrc_eid; source_id=5755:2030-1010; source_url=http://eid.csrc.gov.cn/fund/disclose/list_net_classification.do?fundCode=006597&classification=2030-1010&limit=20; source_query_params=classification=2030-1010,end_date=2024-12-31,force_refresh=False,fundCode=006597,limit=20,requested_fund_code=006597,share_class=A,start=0,start_date=2024-01-01; retrieved_at=2026-05-28T21:53:41.487742+00:00; fund_code=006597; share_class=A; date_range=2024-01-01..2024-12-31; record_count=243; nav_type=accumulated_nav; adjusted_basis=accumulated_nav; dividend_adjustment_status=not_applicable; identity_status=verified; calculation_method=max_drawdown_on_accumulated_nav_path; peak_date=2024-09-26; peak_value=1.1929; trough_date=2024-10-09; trough_value=1.1917; max_drawdown_ratio=-0.0010059518819683125157179982
```

## Residual Risks

- CSRC EID endpoint availability remains external; source `unavailable` keeps `drawdown_stress` weak/missing and score blocks naturally.
- F class cannot cover full `2024-01-01..2024-12-31` because its source starts at `2024-10-08`; F is not used as 006597/A evidence.
- `source_query_params` still mixes HTTP params and request context such as `force_refresh`; this was pre-existing and remains future provenance cleanup work.
- Accumulated NAV max drawdown is accepted for this drawdown metric; this implementation does not claim dividend-adjusted NAV, total-return index, volatility, golden readiness, or generalized non-006597 source coverage.

## Self-Check

pass.

- Scope stayed within the accepted plan and allowed files.
- No direct CSRC/source/cache/stock-sdk access was added to extractors.
- No A/C/E/F mixing occurred in production evidence; only 006597/A is used for `drawdown_stress`.
- No score/quality/golden/schema weakening occurred.
