# Drawdown Stress NAV-Derived Metric Controller Judgment

日期：2026-05-29

Gate：`drawdown_stress NAV-derived metric implementation gate`

角色：Gateflow controller。未 push、未创建 PR、未 merge、未 release、未进入 golden promotion。

## Verdict

Accepted local validation；本地状态推进到 `ready-to-open-draft-PR`。

本 gate 通过 reviewed implementation 在不修改 score policy、quality gate、snapshot schema 或 golden fixture 的前提下，为 `006597 / 2024` 生成 `bond_risk_evidence.v1.drawdown_stress` 的 NAV-derived quantitative evidence。`bond_risk_evidence_missing.baseline_blocking=true` 在最新 score 中自然消失。

## Accepted Commits And Artifacts

- Accepted plan commit：`41485d5 gateflow: accept plan for drawdown stress nav metric`
- Accepted implementation commit：`bd1013b gateflow: accept drawdown stress nav metric implementation`
- Plan：`docs/reviews/release-maintenance-drawdown-stress-nav-derived-metric-implementation-plan-20260529.md`
- Plan reviews / rereviews：
  - `docs/reviews/release-maintenance-drawdown-stress-nav-derived-metric-implementation-plan-review-glm-20260529.md`
  - `docs/reviews/release-maintenance-drawdown-stress-nav-derived-metric-implementation-plan-review-mimo-20260529.md`
  - `docs/reviews/release-maintenance-drawdown-stress-nav-derived-metric-implementation-plan-rereview-glm-20260529.md`
  - `docs/reviews/release-maintenance-drawdown-stress-nav-derived-metric-implementation-plan-rereview-mimo-20260529.md`
- Implementation evidence：`docs/reviews/release-maintenance-drawdown-stress-nav-derived-metric-implementation-evidence-20260529.md`
- Implementation reviews / rereviews：
  - `docs/reviews/release-maintenance-drawdown-stress-nav-derived-metric-implementation-review-glm-20260529.md`
  - `docs/reviews/release-maintenance-drawdown-stress-nav-derived-metric-implementation-review-mimo-20260529.md`
  - `docs/reviews/release-maintenance-drawdown-stress-nav-derived-metric-implementation-rereview-glm-20260529.md`
  - `docs/reviews/release-maintenance-drawdown-stress-nav-derived-metric-implementation-rereview-mimo-20260529.md`
- Aggregate deepreviews：
  - `docs/reviews/release-maintenance-drawdown-stress-nav-derived-metric-aggregate-deepreview-glm-20260529.md`
  - `docs/reviews/release-maintenance-drawdown-stress-nav-derived-metric-aggregate-deepreview-mimo-20260529.md`

## Decision

- Minimum accepted metric：max drawdown。Volatility is non-goal for this gate.
- Primary evidence share class：`006597 / A`。`006598 / C`、`014217 / E`、`022176 / F` remain separated diagnostics and are not mixed into a product-level NAV path.
- Metric period：`2024-01-01` to `2024-12-31`, aligned to the annual-report year.
- Source boundary：only `FundNavRepository.load_nav_series()` is consumed by `FundDataExtractor` with explicit params. The bond extractor receives a precomputed metric/error and performs no CSRC EID, stock-sdk, cache or filesystem IO.
- Basis：only typed `accumulated_nav / accumulated_nav / verified / strong_drawdown_evidence_eligible=True` series can produce accepted evidence. `raw_unit_nav` remains ineligible.
- Evidence contract：`BondRiskEvidenceStrength.quantitative_derived` and `BondRiskEvidenceMeasurementKind.derived_metric` were added as additive contract values. Validator requires `quantitative_derived` to pair with `derived_metric`.
- Annual-report qualitative text such as “控制回撤” remains weak qualitative when no accepted NAV-derived metric exists.

## Real Evidence

CSRC EID typed NAV smoke for the primary evidence path:

- `006597 / A`
- `source_name=csrc_eid`
- `source_id=5755:2030-1010`
- `nav_type=accumulated_nav`
- `adjusted_basis=accumulated_nav`
- `identity_status=verified`
- `strong_drawdown_evidence_eligible=True`
- full source range `2018-12-18` to `2026-05-28`
- source records `1807`
- 2024 metric records `243`

Computed max drawdown:

- `max_drawdown=-0.0010059518819683125157179982`
- display value `-0.10%`
- peak date/value：`2024-09-26 / 1.1929`
- trough date/value：`2024-10-09 / 1.1917`

Real run artifacts:

- Snapshot：`reports/extraction-snapshots/bond-risk-drawdown-nav-006597-2024-20260529/snapshot.jsonl`
- Score：`reports/scoring-runs/bond-risk-drawdown-nav-006597-2024-20260529/score.json`
- Quality gate：`reports/quality-gate-runs/bond-risk-drawdown-nav-006597-2024-20260529/quality_gate.json`

Verified outcomes:

- Snapshot `bond_risk_contract_status="satisfied"`.
- Snapshot satisfied groups contain all seven groups including `drawdown_stress`.
- Snapshot `bond_risk_missing_groups=[]`, `bond_risk_weak_groups=[]`, `bond_risk_ambiguous_groups=[]`.
- Score `score_applicability_issues=[]`.
- Score no longer contains `bond_risk_evidence_missing` or `drawdown_stress` missing.
- Quality gate remains `status="warn"` with unrelated issues only; no `reason="bond_risk_evidence_missing"`.

## Validation

Controller reran full post-fix validation after implementation review L1 was fixed:

```text
uv run ruff check .
All checks passed!
```

```text
uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q
939 passed in 4.56s
Total coverage: 92.42%
```

Implementation evidence also records focused validation, real CSRC EID NAV smoke, extraction snapshot rerun, extraction score rerun, and quality-gate rerun.

## Boundary And Quality Judgment

- FQ0-FQ6 semantics were not weakened.
- `fund_agent/fund/extraction_score.py` was not modified.
- `fund_agent/fund/quality_gate.py` was not modified.
- Golden fixtures were not modified.
- No golden corpus promotion occurred.
- `credit_risk` and `redemption_share_pressure` did not regress.
- No stock-sdk NAV data is consumed as runtime evidence.
- No A/C/E/F aggregate NAV series was created.
- No raw unit NAV is accepted as strong drawdown evidence.
- No UI / Service / Host / Agent boundary change occurred.

## Residuals

- Quality gate still reports unrelated warnings for `turnover_rate`, `holder_structure`, `share_change`, fund-level P1 field failures, FQ0 golden not configured, and FQ4 missing field rate.
- Volatility remains non-goal and not implemented.
- `022176 / F` cannot satisfy full-year 2024 period because the F share class starts on `2024-10-08`; it is accepted only as inception-forward diagnostics.
- CSRC EID source availability remains an external dependency; schema, identity, integrity, unavailable and missing-date failures continue to fail closed through the typed repository.
- Snapshot field-level projection currently exposes one traceable anchor; when annual-report and derived anchors coexist, a future multi-anchor projection gate may improve display fidelity without changing scoring.
- Golden corpus readiness / promotion remains outside this gate.

## Next Entry Point

Next minimum entry point is a non-mutating readiness / residual reconciliation gate, for example `bond risk evidence local readiness reconciliation gate`, to decide whether remaining unrelated FQ warnings or golden-readiness preflight should be addressed. That gate must not promote golden fixtures unless separately authorized.
