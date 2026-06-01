# Bond Risk Evidence Narrow False-Negative — Validation Failure Controller Judgment

> Date: 2026-05-28
> Gate: `bond risk evidence narrow false-negative gate`
> Controller: Codex
> Status: **stopped at validation failure**

## Controller Decision

This gate must stop before accepted implementation commit.

The plan, implementation, code review, fix, and re-review loops completed locally, but required real-path validation failed the gate acceptance condition for `redemption_share_pressure`.

Per the user stop condition, any validation failure stops the gateflow. The controller must not mark the work unit accepted, must not enter golden promotion, and must not proceed to draft PR readiness.

## Validation Commands Run

Passed:

```bash
uv run ruff check .
uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q
uv run python -c 'import asyncio; from fund_agent.fund.documents import FundDocumentRepository; repo = FundDocumentRepository(); report = asyncio.run(repo.load_annual_report("006597", 2024, force_refresh=True)); print(report.key.fund_code, report.key.year, len(report.sections), len(report.tables))'
uv run fund-analysis extraction-snapshot --run-id bond-risk-narrow-006597-2024-20260528 --fund-code 006597 --report-year 2024 --source-csv docs/code_20260519.csv --output-dir reports/extraction-snapshots/bond-risk-narrow-006597-2024-20260528
uv run fund-analysis extraction-score --snapshot-path reports/extraction-snapshots/bond-risk-narrow-006597-2024-20260528/snapshot.jsonl --errors-path reports/extraction-snapshots/bond-risk-narrow-006597-2024-20260528/errors.jsonl --source-csv docs/code_20260519.csv --output-dir reports/scoring-runs/bond-risk-narrow-006597-2024-20260528
uv run fund-analysis quality-gate --score-path reports/scoring-runs/bond-risk-narrow-006597-2024-20260528/score.json --output-dir reports/quality-gate-runs/bond-risk-narrow-006597-2024-20260528
```

Observed pass details:

- Ruff: all checks passed.
- Full pytest coverage: `852 passed`, total coverage `92.33%`, above `--cov-fail-under=50`.
- `FundDocumentRepository` smoke: `006597 2024 8 85`.
- Snapshot, score, and quality gate commands completed successfully.

## Failing Acceptance Check

Real `006597 / 2024` extractor output after implementation:

```text
contract_status partial
satisfied ('duration_rate_risk', 'credit_risk', 'leverage_liquidity', 'asset_allocation_holdings_mix', 'convertible_bond_equity_exposure')
weak ('drawdown_stress',)
ambiguous ('redemption_share_pressure',)
missing ()
```

`credit_risk` is fixed:

```text
status=accepted
strength=quantitative_direct
summary=年报表格披露持有债券/证券的信用评级分布
metric_name=持仓评级分布
metric_value=holding_rating_distribution: 未评级=6353108138.08, 合计=6353108138.08
anchor count=8
```

`drawdown_stress` is correctly preserved as weak:

```text
status=weak
strength=qualitative_control_intent
na_reason=drawdown_metric_not_found
```

`redemption_share_pressure` remains unresolved:

```text
status=ambiguous
strength=ambiguous
summary=份额变动表无法完成 A/C/E/F 全类别聚合与对账，已失败关闭
na_reason=share_class_column_count_mismatch
```

This fails the accepted plan assertion:

- Snapshot `bond_risk_satisfied_groups` must include `redemption_share_pressure`.
- Snapshot `bond_risk_ambiguous_groups` must no longer contain `redemption_share_pressure`.

## Score And Quality Gate Observations

`score.json` no longer marks `bond_risk_evidence` as a failed field:

- `bond_risk_evidence` field score: `status=pass`
- `coverage_rate=1.0`
- `traceability_rate=1.0`

However, this does not satisfy the gate because the snapshot contract still shows `redemption_share_pressure` as ambiguous.

`quality_gate.json` remains `warn` with 7 issues. The bond-risk warning still reports `reason=bond_risk_evidence_missing`; this reflects remaining partial contract status and is not accepted as readiness in this gate.

## Failure Classification

The failure is classified as a real-path extractor false negative, not a source/network/PDF failure.

Evidence:

- Real report loading through `FundDocumentRepository` succeeded.
- Snapshot generation succeeded.
- Score and quality gate generation succeeded.
- The extractor reached fail-closed logic for `redemption_share_pressure`, specifically `share_class_column_count_mismatch`.

The likely next implementation problem is that the real §10 table column structure differs from the synthetic A/C/E/F test fixture, and the current column alignment logic cannot reliably align class value columns to the §2 A/C/E/F mapping.

## Boundary Status

The implementation did not weaken FQ0-FQ6.

The implementation did not bypass `FundDocumentRepository`.

The implementation did not turn missing evidence into a pass.

The implementation did not describe held bond/security rating distribution as fund own rating.

The implementation did not upgrade qualitative drawdown evidence.

No schema, score, snapshot, quality gate, Service, UI, Host, Agent, dayu, golden, release, push, PR, or merge work was performed.

## Controller Stop

Stop here.

Do not create an accepted implementation commit.

Do not update `docs/implementation-control.md` as if the evidence loop completed.

Do not run aggregate deepreview or mark ready-to-open-draft-PR.

Next entry point, if authorized by the user, should be a narrower fix pass for real §10 A/C/E/F table column alignment, starting from this classified failure:

```text
redemption_share_pressure real-path fail-closed with na_reason=share_class_column_count_mismatch
```
