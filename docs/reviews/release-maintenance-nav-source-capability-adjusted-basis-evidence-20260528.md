# NAV Source Capability / Adjusted Basis Evidence

Date: 2026-05-28

Worker: Codex

Role: planning + capability evidence worker, not controller

Gate: `NAV source capability / adjusted basis evidence gate`

## Worker Self-Check - Start

- Status: pass.
- I stayed in the assigned specialist gate and did not start `$gateflow` / `/gateflow`.
- I did not modify production code, tests, score, quality gate, schema, golden fixture, release / PR state, or blocker status.
- Evidence collection used static code review, current artifacts, and allowed public-boundary smoke through `FundNavDataAdapter.load_nav_data("006597")`.
- No direct production PDF access was used. NAV SQLite inspection was read-only, diagnostic-only, and non-authoritative for public adapter capability; future production code and implementation gates must not copy direct cache reads as a boundary bypass.

## Files And Artifacts Read

Truth sources:

- `AGENTS.md`
- `docs/design.md`
- `docs/implementation-control.md`
- `docs/reviews/release-maintenance-drawdown-stress-nav-derived-contract-controller-judgment-20260528.md`
- `docs/reviews/release-maintenance-drawdown-stress-nav-derived-contract-plan-review-ds-20260528.md`

Latest 006597 artifacts:

- `reports/extraction-snapshots/bond-risk-crosscheck-suffix-006597-2024-20260528/snapshot.jsonl`
- `reports/scoring-runs/bond-risk-crosscheck-suffix-006597-2024-20260528/score.json`
- `reports/quality-gate-runs/bond-risk-crosscheck-suffix-006597-2024-20260528/quality_gate.json`

Current code and docs:

- `fund_agent/fund/data/nav_data.py`
- `fund_agent/fund/data_extractor.py`
- `fund_agent/fund/extraction_snapshot.py`
- `fund_agent/fund/README.md`
- `tests/fund/data/test_nav_data.py`
- relevant `rg` matches in `docs/` and `tests/`

## Commands Run

Preflight:

```bash
pwd
git branch --show-current
git status --short
```

Truth and artifact reads:

```bash
sed -n '1,260p' AGENTS.md
sed -n '1,260p' docs/design.md
sed -n '1,260p' docs/implementation-control.md
sed -n '1,260p' docs/reviews/release-maintenance-drawdown-stress-nav-derived-contract-controller-judgment-20260528.md
sed -n '1,260p' docs/reviews/release-maintenance-drawdown-stress-nav-derived-contract-plan-review-ds-20260528.md
sed -n '1,260p' reports/extraction-snapshots/bond-risk-crosscheck-suffix-006597-2024-20260528/snapshot.jsonl
sed -n '1,240p' reports/scoring-runs/bond-risk-crosscheck-suffix-006597-2024-20260528/score.json
sed -n '1,260p' reports/quality-gate-runs/bond-risk-crosscheck-suffix-006597-2024-20260528/quality_gate.json
```

Code and documentation inspection:

```bash
sed -n '1,280p' fund_agent/fund/data/nav_data.py
sed -n '280,620p' fund_agent/fund/data/nav_data.py
sed -n '1,320p' fund_agent/fund/data_extractor.py
sed -n '1,320p' fund_agent/fund/extraction_snapshot.py
sed -n '960,1045p' fund_agent/fund/extraction_snapshot.py
rg -n "NavData|nav_data|FundNavDataAdapter|单位净值|累计净值|复权|total-return|adjust" fund_agent docs README.md tests -g '!*.pyc'
rg -n "nav_cache|nav.sqlite|fund_open_fund_info_em|日增长率|净值日期" . -g '!*.pyc' -g '!reports/**'
```

Allowed public smoke and diagnostic cache metadata check:

```bash
uv run python -c $'import asyncio, json\nfrom fund_agent.fund.data.nav_data import FundNavDataAdapter\nasync def main():\n    result = await FundNavDataAdapter().load_nav_data("006597")\n    payload = {"fund_code": result.fund_code, "source": result.source, "cached": result.cached, "unavailable": result.unavailable, "unavailable_reason": result.unavailable_reason, "record_count": len(result.records), "first_record": result.records[0] if result.records else None, "last_record": result.records[-1] if result.records else None, "field_names": sorted({key for row in result.records[:5] for key in row.keys()})}\n    print(json.dumps(payload, ensure_ascii=False, indent=2))\nasyncio.run(main())'
```

```bash
uv run python -c 'import json, sqlite3; from fund_agent.config.paths import DEFAULT_NAV_CACHE_ROOT; path = DEFAULT_NAV_CACHE_ROOT / "nav.sqlite3"; con = sqlite3.connect(f"file:{path}?mode=ro", uri=True); row = con.execute("select fund_code, source, updated_at, payload_json from nav_cache where fund_code=?", ("006597",)).fetchone();
if row is None:
    print(json.dumps({"cache_path": str(path), "found": False}, ensure_ascii=False, indent=2))
else:
    payload = json.loads(row[3]); print(json.dumps({"cache_path": str(path), "found": True, "fund_code": row[0], "stored_source": row[1], "updated_at": row[2], "record_count": len(payload), "first_record": payload[0] if payload else None, "last_record": payload[-1] if payload else None, "field_names": sorted({key for item in payload[:5] for key in item.keys()})}, ensure_ascii=False, indent=2))'
```

One attempted inline smoke command failed with `SyntaxError` because Python cannot define `async def` after a semicolon. It did not alter repository state and was rerun successfully with newline quoting.

## Static Code Evidence

### NAV Adapter Fetches Unit NAV Trend

`fund_agent/fund/data/nav_data.py` calls Akshare with `indicator="单位净值走势"`:

```text
dataframe = ak.fund_open_fund_info_em(symbol=fund_code, indicator="单位净值走势")
```

This is current code fact. There is no alternate cumulative / adjusted / total-return method in the current adapter.

### Public Result Lacks Basis And Origin Metadata

`NavDataResult` contains only:

- `fund_code`
- `records`
- `source`
- `cached`
- `unavailable`
- `unavailable_reason`

It has no fields for `nav_type`, `adjustment_basis`, `series_type`, `origin_source_name`, `retrieved_at`, or provider methodology.

### Cache Stores Metadata But Cache Hit Drops It

Static adapter code shows the SQLite schema includes `fund_code`, `payload_json`, `source`, and `updated_at`.

On cache hit, `_load_cached_sync()` selects only `payload_json`, and `load_nav_data()` returns `source="nav_cache"` with no stored source or `updated_at`.

### Extractor Boundary Is Correct But Coarse

`FundDataExtractor.extract()` loads the annual report via `FundDocumentRepository`, then calls `_load_nav_data_or_unavailable()` through the injected `_NavDataProvider`.

NAV provider exceptions are degraded to `NavDataResult(unavailable=True)`, while annual-report repository failures remain outside that catch. This respects the current Fund-layer boundary but does not provide adjusted basis evidence.

### Snapshot Projection Is Not Source-Provenance-Complete For NAV

`_build_nav_record()` emits a note shaped as:

```text
source=<source>; cached=<bool>; records=<count>
```

It always passes `anchor=None`; `comparable_values={}`; and has no NAV provenance, basis, date range, source kind, or calculation method fields.

## Latest 006597 Artifact Evidence

### Snapshot

Latest snapshot row for `bond_risk_evidence`:

- `bond_risk_contract_status="partial"`
- `bond_risk_satisfied_groups=["duration_rate_risk","credit_risk","leverage_liquidity","asset_allocation_holdings_mix","redemption_share_pressure","convertible_bond_equity_exposure"]`
- `bond_risk_weak_groups=["drawdown_stress"]`
- `bond_risk_missing_groups=[]`

Latest snapshot row for `nav_data`:

- `value_present=true`
- `anchor_present=false`
- `note="source=nav_cache; cached=True; records=1802"`

### Score

Latest score shows:

- `bond_risk_evidence`: coverage `1.0`, traceability `1.0`, status `pass`.
- `nav_data`: coverage `1.0`, traceability `0.0`, status `fail`.
- `fund_quality` still has missing-field rate `0.2857142857142857` and P1 missing fields `holder_structure`, `share_change`, `turnover_rate`.

The score artifact does not prove `drawdown_stress` accepted quantitative evidence; the previous controller judgment states latest score still blocks baseline on `drawdown_stress`.

### Quality Gate

Latest quality gate status is `warn`.

It includes an FQ2F warning for bond fund risk evidence with reason `bond_risk_evidence_missing`. This is consistent with no blocker解除 in this gate.

## Smoke Evidence

### FundNavDataAdapter Boundary

Result of `FundNavDataAdapter().load_nav_data("006597")`:

```json
{
  "fund_code": "006597",
  "source": "nav_cache",
  "cached": true,
  "unavailable": false,
  "unavailable_reason": null,
  "record_count": 1802,
  "first_record": {
    "净值日期": "2018-12-03",
    "单位净值": 1.0,
    "日增长率": 0.0
  },
  "last_record": {
    "净值日期": "2026-05-18",
    "单位净值": 1.227,
    "日增长率": 0.01
  },
  "field_names": [
    "净值日期",
    "单位净值",
    "日增长率"
  ]
}
```

Interpretation:

- Unified Fund-layer boundary can retrieve a sequence for `006597`.
- The returned public result is a cache hit and only exposes raw rows.
- The fields prove unit NAV trend availability, not adjusted / cumulative / total-return basis.

### NAV SQLite Read-Only Metadata - Diagnostic Non-Boundary Evidence

Result of read-only cache metadata inspection:

```json
{
  "cache_path": "cache/nav/nav.sqlite3",
  "found": true,
  "fund_code": "006597",
  "stored_source": "akshare",
  "updated_at": "2026-05-19T05:07:11.758531+00:00",
  "record_count": 1802,
  "first_record": {
    "净值日期": "2018-12-03",
    "单位净值": 1.0,
    "日增长率": 0.0
  },
  "last_record": {
    "净值日期": "2026-05-18",
    "单位净值": 1.227,
    "日增长率": 0.01
  },
  "field_names": [
    "净值日期",
    "单位净值",
    "日增长率"
  ]
}
```

Interpretation:

- This section is diagnostic-only and non-authoritative for public adapter capability. It is not a production-acceptable access path and must not be used by future implementation, score, quality gate, baseline, or blocker-removal decisions.
- Public capability evidence remains the static adapter code plus `FundNavDataAdapter.load_nav_data("006597")` public result.
- Cache has useful origin metadata, but the current adapter result does not expose it on cache hit.
- Even with cache metadata, the payload does not contain cumulative NAV, adjusted NAV, total-return flag, dividend adjustment basis, or methodology.

## Capability Decision Evidence

| Question | Evidence-Based Answer |
|---|---|
| Does the project already have a NAV sequence adapter? | Yes. `FundNavDataAdapter` exists under `fund_agent/fund/data/`, and `FundDataExtractor` consumes it through a `_NavDataProvider` protocol. |
| Is it a full repository/service with source basis contract? | No. Public adapter code and result show a coarse adapter/cache returning raw records and minimal success/unavailable metadata. Diagnostic SQLite inspection is not public adapter capability evidence. |
| Can 006597 NAV sequence be obtained through the unified boundary? | Yes. `FundNavDataAdapter.load_nav_data("006597")` returned 1802 cached records. |
| Can fund code be verified? | Only at request/cache key level. There is no source-returned identity field in the current public result. |
| Can date range be observed? | Raw row dates show `2018-12-03` to `2026-05-18`, but the adapter does not expose a typed date range or completeness status. |
| Can NAV type be verified? | Only as upstream indicator `单位净值走势` from code and row field `单位净值`; no cumulative / adjusted / total-return type is exposed. |
| Can dividend / split adjustment status be verified? | No. Current public fields cannot prove adjustment basis, and the diagnostic cache metadata also does not contain dividend adjustment status. |
| Is `日增长率` sufficient to infer total return? | No. The current adapter does not document whether `日增长率` is dividend-adjusted or total-return-equivalent. |
| Should raw NAV be used for future max drawdown / volatility contract? | No. Future contract should use adjusted / total-return / cumulative basis and fail closed when basis is unknown. |

## Failure Classification For Current State

For 006597 current adapter result:

- source availability: `available_cached`
- identity status: `request_key_only_unverified`
- schema status: `raw_unit_nav_fields_present`
- adjustment basis: `unknown`
- risk-evidence eligibility: `ineligible_fail_closed`

For future gate classification, this maps to:

```text
adjustment_basis_unknown
```

Required handling:

- do not satisfy `drawdown_stress`
- do not change score / quality gate / baseline
- keep qualitative drawdown-control text weak
- open a narrow source adapter gate if controller wants to pursue adjusted-basis NAV evidence

## Recommendation

`capability_decision_recommendation = blocked_pending_source_adapter`

Reason:

The current adapter proves raw 006597 NAV sequence availability through the correct Fund-layer boundary, but it cannot prove adjusted / cumulative / total-return basis. Using raw `单位净值` or ambiguous `日增长率` would risk computing drawdown on the wrong investor-return basis. The next minimum gate must be a dedicated Fund-layer NAV repository/source adapter contract gate before any drawdown implementation, schema, score, quality gate, or blocker-removal work.

## Residual Risks

- Current legacy `nav_cache` can remain useful for raw `nav_data` availability, but it is not eligible for risk evidence until basis and provenance are explicit.
- A future provider may expose cumulative or adjusted NAV, but that must be proven through code and tests before score or quality semantics change.
- Current snapshot/score projection cannot machine-check per-group NAV-derived provenance. This belongs to a later schema/projection gate after source capability passes.
- `006597 / 2024` remains blocked for baseline/golden purposes by `drawdown_stress` until adjusted basis and derived evidence contract are both accepted.

## Worker Self-Check - Completion

- Status: pass.
- I produced the requested durable plan and evidence artifacts only.
- I did not modify production code, tests, score, quality gate, schema, golden fixture, design/control truth, release / PR state, or unrelated untracked files.
- I did not commit, push, create PR, merge, or close out the gate.
- Artifact conclusion is fail-closed: current capability is insufficient for adjusted-basis drawdown evidence.
