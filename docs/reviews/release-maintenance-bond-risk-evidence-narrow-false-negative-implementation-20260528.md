# Bond Risk Evidence Narrow False-Negative Implementation

> Date: 2026-05-28
> Role: implementation worker, not controller
> Gate: `bond risk evidence narrow false-negative gate`
> Accepted plan: `docs/reviews/release-maintenance-bond-risk-evidence-narrow-false-negative-plan-20260528.md`
> Controller judgment: `docs/reviews/release-maintenance-bond-risk-evidence-narrow-false-negative-plan-controller-judgment-20260528.md`
> Status: implementation complete for allowed files; controller validation still required

## Scope

Modified files:

- `fund_agent/fund/extractors/bond_risk_evidence.py`
- `tests/fund/extractors/test_bond_risk_evidence.py`
- `docs/reviews/release-maintenance-bond-risk-evidence-narrow-false-negative-implementation-20260528.md`

No changes were made to schema, score, snapshot, quality gate, Service, UI, Host, Agent, dayu, golden, release, PR, push, or merge state.

## Credit Risk Behavior

Implemented a dedicated holding credit-rating distribution path before the qualitative fallback:

- Detects held bond/security rating distribution tables by `信用评级` / `短期信用评级` / `长期信用评级` semantics and rating-category rows such as `A-1`, `AAA`, `AAA以下`, `未评级`, and `合计`.
- Emits `credit_risk` as `accepted / quantitative_direct / actual_exposure` only when row-level anchors and current-period parseable numeric values exist.
- Uses portfolio/holding wording:
  - `summary="年报表格披露持有债券/证券的信用评级分布"`
  - `metric_name="持仓评级分布"`
  - `evidence_role="holding_rating_distribution"`
- Rejects explicit fund-own-rating contexts such as `本基金评级`, `基金评级信息`, and `基金自身评级`.
- Preserves row-level anchors from all matching valid rating tables; `metric_value` summarizes the first representative current-period table and includes `合计` when present.

The implementation does not introduce `fund_rating`, `ratings`, or `fund_own_rating` semantics.

## Redemption Share Pressure Behavior

Replaced the old current-fund-code single-column selection path with all-class aggregation:

- Parses §2 share-class mapping from parsed tables first, then text lines as fallback.
- Supports A/C/E/F mapping such as `A=006597`, `C=006598`, `E=014217`, `F=022176`.
- Scans all share-change table candidates, rejects financial-statement-like tables containing `实收基金`, `未分配利润`, or `净资产合计`, and fails closed when best candidates are ambiguous.
- Aligns §10 value columns to all mapped classes, excluding total columns; class-column mismatch returns `ambiguous` with `na_reason="share_class_column_count_mismatch"`.
- Uses `Decimal` parsing with comma/whitespace removal, `-` / `－` / `—` / `--` as zero, and `Decimal("0.01")` reconciliation tolerance.
- Computes beginning, subscription, redemption, split, ending, net_change, and net_change_ratio for every class and for the aggregate.
- Treats per-class beginning zero as non-fatal and records `class_beginning_zero`; aggregate beginning zero fails closed.
- Emits row-level anchors for §10 beginning, subscription, redemption, ending, and optional split rows; emits a §2 mapping anchor when mapping comes from a parsed table.

The group is accepted only for complete all-class aggregation. A-only extraction no longer satisfies `redemption_share_pressure`.

## Drawdown Boundary

No drawdown upgrade was implemented. Qualitative `控制回撤` text still produces:

- `status="weak"`
- `strength="qualitative_control_intent"`
- `measurement_kind="control_intent"`
- `na_reason="drawdown_metric_not_found"`

No NAV-derived max drawdown, volatility, stress metric, score policy, or quality-gate behavior was added or changed.

## Tests Added Or Updated

Targeted tests now cover:

- Holding rating distribution accepted as portfolio credit exposure, not fund-own rating.
- Fund-own rating table rejection.
- Multiple holding rating tables preserving all anchors.
- Qualitative-only credit text remaining weak.
- Credit accepted path requiring row/table anchors and numeric current-period values.
- §2 table-based A/C/E/F share-class mapping.
- A/C/E/F aggregate share-change computation, including F beginning zero.
- Not A-only behavior.
- Rejection of net-asset-statement-like candidate tables.
- Class column count mismatch fail-closed.
- Arithmetic mismatch fail-closed.
- Non-parseable share value fail-closed.
- Full-width dash parsed as zero.
- Missing required share-change row anchor fail-closed.
- Drawdown control text remains weak and unsatisfied.

## Validation Run

Commands run locally:

```bash
uv run pytest tests/fund/extractors/test_bond_risk_evidence.py -q
uv run ruff check fund_agent/fund/extractors/bond_risk_evidence.py tests/fund/extractors/test_bond_risk_evidence.py
uv run python -c "from fund_agent.fund.extractors.bond_risk_evidence import extract_bond_risk_evidence; print('import OK')"
```

Results:

- Targeted pytest: `41 passed`
- Ruff targeted check: `All checks passed`
- Import smoke: `import OK`

Full required validation, real `006597 / 2024` repository smoke, extraction snapshot, extraction score, and quality gate rerun were not executed by this implementation worker; the accepted plan assigns those to controller validation.

## Residual Risks

- `drawdown_stress` remains weak qualitative evidence, so full bond-risk blocker解除 is not claimed.
- Real `006597 / 2024` path still needs controller validation through `FundDocumentRepository`, snapshot, score, and quality gate.
- Existing unrelated extraction gaps such as turnover, holder structure, and generic share_change remain out of scope.
- Generated report artifacts were not created or promoted in this worker run.
