# NAV Source Capability / Adjusted Basis Gate - Controller Judgment

Date: 2026-05-28

Controller: Codex

Work unit: `NAV source capability / adjusted basis evidence gate`

Branch: `codex/local-reconciliation`

## Verdict

`blocked_pending_source_adapter`

The project has a unified Fund-layer NAV access boundary (`FundNavDataAdapter` consumed through `FundDataExtractor`), and `006597` NAV rows are reachable through that boundary. The current public adapter capability is not sufficient for future `drawdown_stress` accepted quantitative evidence because it does not prove adjusted, cumulative, total-return, dividend-aware, or provider-methodology basis.

The `006597 / 2024` bond blocker remains valid:

- `bond_risk_evidence_missing.baseline_blocking=true`
- `missing_evidence_groups=["drawdown_stress"]`

No code, schema, score policy, quality gate, golden fixture, baseline promotion, release state, PR, push, or merge was changed in this gate.

## Preflight

- `git branch --show-current`: `codex/local-reconciliation`
- `git status --short` at entry: no tracked dirty files; only known unrelated untracked files.

## Source Replay

Read and used:

- `AGENTS.md`
- `docs/design.md`
- `docs/implementation-control.md`
- `docs/reviews/release-maintenance-drawdown-stress-nav-derived-contract-controller-judgment-20260528.md`
- `docs/reviews/release-maintenance-drawdown-stress-nav-derived-contract-plan-review-ds-20260528.md`
- Latest `006597 / 2024` artifacts:
  - `reports/extraction-snapshots/bond-risk-crosscheck-suffix-006597-2024-20260528/snapshot.jsonl`
  - `reports/scoring-runs/bond-risk-crosscheck-suffix-006597-2024-20260528/score.json`
  - `reports/quality-gate-runs/bond-risk-crosscheck-suffix-006597-2024-20260528/quality_gate.json`

Current verified `006597 / 2024` state:

- `credit_risk` remains satisfied.
- `redemption_share_pressure` remains satisfied.
- `drawdown_stress` remains weak and does not have accepted quantitative evidence.
- Latest score keeps the bond-risk baseline blocker only for `drawdown_stress`.

## Worker And Review Artifacts

Capability plan and evidence:

- `docs/reviews/release-maintenance-nav-source-capability-adjusted-basis-plan-20260528.md`
- `docs/reviews/release-maintenance-nav-source-capability-adjusted-basis-evidence-20260528.md`

Tmux reviews:

- DS: `docs/reviews/release-maintenance-nav-source-capability-adjusted-basis-plan-review-ds-20260528.md`
- GLM: `docs/reviews/release-maintenance-nav-source-capability-adjusted-basis-plan-review-glm-20260528.md`

Artifact-only fix and re-review:

- Fix evidence: `docs/reviews/release-maintenance-nav-source-capability-adjusted-basis-fix-evidence-20260528.md`
- DS re-review: `docs/reviews/release-maintenance-nav-source-capability-adjusted-basis-rereview-ds-20260528.md`
- GLM re-review: `docs/reviews/release-maintenance-nav-source-capability-adjusted-basis-rereview-glm-20260528.md`

Non-tmux review artifacts created during an earlier controller mistake were removed and are not part of this gate's accepted evidence chain. The accepted review path is DS / GLM through tmux panes per `$init-agents`.

## NAV Capability Evidence

Current code facts:

- `fund_agent/fund/data/nav_data.py` calls `ak.fund_open_fund_info_em(symbol=fund_code, indicator="单位净值走势")`.
- `NavDataResult` exposes only `fund_code`, `records`, `source`, `cached`, `unavailable`, and `unavailable_reason`.
- Cache hit returns `source="nav_cache"` and the cached payload only; origin source and retrieval timestamp are not exposed through the public adapter result.
- `FundDataExtractor.extract()` loads annual reports through `FundDocumentRepository` and NAV data through the injected `_NavDataProvider`, preserving current Fund-layer boundaries.

Controller public-boundary smoke through `FundNavDataAdapter.load_nav_data("006597")`:

```json
{
  "fund_code": "006597",
  "source": "nav_cache",
  "cached": true,
  "unavailable": false,
  "record_count": 1809,
  "first": {"净值日期": "2018-12-03", "单位净值": 1.0, "日增长率": 0.0},
  "last": {"净值日期": "2026-05-27", "单位净值": 1.2275, "日增长率": 0.01},
  "keys": ["净值日期", "单位净值", "日增长率"]
}
```

This proves raw NAV availability through the public Fund-layer boundary. It does not prove adjusted, cumulative, total-return, dividend-aware, or provider-methodology basis.

Read-only SQLite cache inspection in the evidence artifact is accepted only as diagnostic, non-authoritative investigation. It is not a production access path and is not accepted as public adapter capability proof. Future production code, score logic, quality gates, baseline decisions, or blocker-removal work must not directly read NAV cache internals to bypass `FundNavDataAdapter`.

## Review Findings Disposition

| Finding | Disposition | Final status | Reason |
|---|---|---|---|
| DS-F1 / GLM-F1 / B-P1: direct SQLite inspection needed explicit diagnostic-only boundary | `accepted` | `已修复` | Updated plan/evidence mark SQLite inspection as diagnostic-only and non-authoritative; re-reviews passed. |
| DS-F2: plan wording made raw NAV availability proof referent ambiguous | `accepted` | `已修复` | Plan now says public `FundNavDataAdapter.load_nav_data("006597")` smoke proves raw NAV availability; SQLite inspection is separated. |
| DS-F3: `_load_cached_sync()` metadata loss should be future adapter gate scope | `accepted` | `已修复` | Future Gate 1 scope now requires public adapter cache-hit metadata repair rather than direct SQLite access. |
| GLM-F2: future fields need `dividend_adjustment_status` decision point | `accepted` | `已修复` | Future gate scope now explicitly decides whether dividend adjustment is represented inside `adjustment_basis` or as an independent field. |
| GLM-F3 / GLM-F4: failure classification and gate slicing align with prior decisions | `accepted as confirming evidence` | `证据有效` | No fix required; both support the blocked-pending-source-adapter decision. |

## Controller Decision

The current NAV source capability is rejected for `drawdown_stress` accepted quantitative evidence and the gate is blocked pending a source adapter contract.

Accepted current facts:

- The repository already has a NAV adapter boundary in Agent/Fund data (`fund_agent/fund/data/FundNavDataAdapter`).
- That boundary can load a 006597 NAV sequence.
- The current sequence and public result prove only raw unit NAV trend availability.
- The current public result cannot verify source-returned identity, adjustment basis, dividend adjustment status, cumulative NAV, total-return NAV, provider methodology, date completeness, or calculation-ready provenance.

Required next gate:

`NAV repository/source adapter adjusted-basis contract gate`

That gate should stay in `fund_agent/fund/data/` and may only proceed if it can expose, through a typed public adapter contract, source name, origin source, retrieved time, source-returned identity or explicit identity status, date range, NAV type, adjustment basis, dividend adjustment status, record count, completeness status, and fail-closed data-quality classification. Unknown adjustment basis or unknown identity must remain ineligible for risk evidence.

Only after that source adapter gate passes may a later `bond_risk_evidence derived drawdown contract schema gate` consider source-kind-aware anchors, per-group snapshot provenance, score validation, and max drawdown / volatility calculation.

## Validation Judgment

No production implementation was performed, so full implementation validation was intentionally not run.

Controller did run real NAV smoke through the unified public Fund-layer boundary:

- `uv run python -c ... FundNavDataAdapter().load_nav_data("006597") ...`
- Result: success, `source="nav_cache"`, `cached=true`, `record_count=1809`, fields `净值日期`, `单位净值`, `日增长率`.

`ruff` / full `pytest` were not run because this gate only changed review/control artifacts and did not modify Python code, tests, schema, score, quality gate, runtime behavior, or fixtures.

## Residuals

- `006597 / 2024` remains blocked for baseline/golden purposes by `drawdown_stress`.
- Qualitative `控制回撤` remains weak qualitative evidence and must not be upgraded.
- Current raw `nav_data` availability remains useful for diagnostics and existing snapshot coverage, but it is ineligible for `drawdown_stress` risk evidence until adjusted-basis source capability and derived evidence contract both pass.
- Golden corpus v1 remains blocked; no promotion work is authorized or performed.

## Next Entry Point

`NAV repository/source adapter adjusted-basis contract gate`

Minimum scope:

- Define / implement typed Fund-layer NAV source contract if and only if a provider can expose adjusted, cumulative, or total-return basis with provenance.
- Repair cache-hit metadata exposure through public adapter results, not direct SQLite reads.
- Decide `dividend_adjustment_status` representation explicitly.
- Classify `adjustment_basis_unknown`, `identity_mismatch`, `schema_drift`, `source_unavailable`, `not_found`, `insufficient_history`, and `integrity_error` fail-closed.

Non-goals:

- No `bond_risk_evidence` satisfaction changes.
- No score / quality / golden / baseline changes.
- No drawdown metric acceptance.
- No PR / push / merge / release / golden promotion.
