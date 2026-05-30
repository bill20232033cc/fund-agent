# NAV Source Capability / Adjusted Basis Plan

Date: 2026-05-28

Worker: Codex

Role: planning + capability evidence worker, not controller

Gate: `NAV source capability / adjusted basis evidence gate`

Gate classification: `standard`

## Worker Self-Check - Start

- Status: pass.
- Current role is specialist worker only. I did not start `$gateflow` / `/gateflow`, did not restart from plan, and did not enter implementation.
- Source of truth read: `AGENTS.md`, `docs/design.md`, `docs/implementation-control.md`, prior drawdown contract controller judgment, DS plan review, latest `006597 / 2024` snapshot / score / quality-gate artifacts, and current NAV boundary code.
- Scope boundary: write durable plan and evidence artifacts only. No production code, tests, score, quality gate, schema, golden fixture, release / PR state, Host / Agent / dayu, QDII / FOF / `110020`, or blocker removal.
- Completion signal: two artifacts under `docs/reviews/`, explicit `capability_decision_recommendation`, command evidence, fail-closed next gate.

## Source Replay

The current gate starts from these truths:

- `AGENTS.md` is the highest-priority execution rule source. The project boundary is `UI -> Service -> Host -> Agent`; current deterministic production flow is UI / Service calling the Agent-layer Fund package directly as a transition path.
- `docs/design.md` says `FundDataExtractor` composes `FundDocumentRepository`, section extractors, and `FundNavDataAdapter`; `NavDataResult` exposes successful NAV results as `source="nav_cache" / "akshare"` plus `cached`, and degraded NAV failures as `unavailable=True`.
- `docs/implementation-control.md` sets the current next entry point to this NAV source capability gate. It explicitly says the previous drawdown NAV-derived contract gate was blocked because the current public adapter result proves only `单位净值走势` / `日增长率`, not total-return / cumulative / adjusted basis.
- `docs/reviews/release-maintenance-drawdown-stress-nav-derived-contract-controller-judgment-20260528.md` accepted all material findings that current NAV source cannot prove adjusted basis and that no implementation or blocker解除 is authorized.
- `docs/reviews/release-maintenance-drawdown-stress-nav-derived-contract-plan-review-ds-20260528.md` concluded the current provider exposes `净值日期` / `单位净值` / `日增长率` only, and source capability must be decided before any derived drawdown contract work.
- Latest `006597 / 2024` artifacts still show `bond_risk_evidence` partial with `drawdown_stress` weak, `nav_data` value present but not traceable, and quality gate warning rather than baseline unblock.

## Goal

Decide whether the existing project NAV capability can safely support future maximum drawdown / volatility evidence on an adjusted, cumulative, or total-return-equivalent basis.

This plan does not authorize implementation. It is a source-capability and contract-readiness plan for the controller to use before any future drawdown implementation gate.

## Non-Goals

- Do not upgrade qualitative `控制回撤` text to accepted quantitative evidence.
- Do not change `bond_risk_evidence` satisfaction, score semantics, quality gate semantics, snapshot schema, golden fixtures, baseline status, or release / PR state.
- Do not add web scraping in `FundDataExtractor` or bypass `FundNavDataAdapter`.
- Do not directly read production annual-report PDFs or PDF cache.
- Do not create Host / Agent packages or introduce `dayu.host` / `dayu.engine`.
- Do not route explicit parameters through `extra_payload`.
- Do not enter QDII, FOF, `110020`, golden readiness, release readiness, PR, push, merge, or closeout work.

## Current Capability Assessment

### Existing Boundary

The project already has a Fund-layer NAV adapter:

- `fund_agent/fund/data/nav_data.py` defines `FundNavDataAdapter`.
- `fund_agent/fund/data_extractor.py` defines `_NavDataProvider` and injects it into `FundDataExtractor`.
- `StructuredFundDataBundle.nav_data` carries `NavDataResult`.
- `fund_agent/fund/extraction_snapshot.py` projects a coarse `nav_data` snapshot row.

This is an Agent / Fund data capability, not a UI, Service, Host, or generic repository capability. It is closer to an adapter than a full source repository/service. A future durable NAV repository/source adapter should remain in `fund_agent/fund/data/` and be consumed through explicit Fund-layer protocols. Service may orchestrate use cases, but Service should not parse NAV source rows or infer adjustment basis.

### Current Provider And Fields

Current production fetch code calls:

```text
ak.fund_open_fund_info_em(symbol=fund_code, indicator="单位净值走势")
```

`NavDataResult` currently exposes:

- `fund_code`
- `records`
- `source`
- `cached`
- `unavailable`
- `unavailable_reason`

It does not expose:

- `origin_source_name` on cache hit
- `retrieved_at` / cache `updated_at`
- `nav_type`
- `adjustment_basis`
- `series_type`
- `dividend_adjustment_status`
- provider methodology metadata
- data completeness / missing-date classification

The SQLite cache stores `source` and `updated_at`, but `_load_cached_sync()` returns only `payload_json`. Therefore the public adapter result loses stored source and retrieval timestamp when `source="nav_cache"`.

### Latest 006597 Evidence

Allowed smoke through the unified Fund-layer NAV boundary returned:

- `fund_code="006597"`
- `source="nav_cache"`
- `cached=true`
- `unavailable=false`
- `record_count=1802`
- first row: `{"净值日期": "2018-12-03", "单位净值": 1.0, "日增长率": 0.0}`
- last row: `{"净值日期": "2026-05-18", "单位净值": 1.227, "日增长率": 0.01}`
- field names: `净值日期`, `单位净值`, `日增长率`

Diagnostic-only read-only SQLite inspection of the same cache row found:

- `stored_source="akshare"`
- `updated_at="2026-05-19T05:07:11.758531+00:00"`
- `record_count=1802`
- field names still only `净值日期`, `单位净值`, `日增长率`

The public `FundNavDataAdapter.load_nav_data("006597")` smoke proves raw NAV availability for 006597 through the current unified Fund boundary. The SQLite inspection is diagnostic-only and non-authoritative for public adapter capability; it must not be copied into production code or future implementation paths as a way to bypass the Fund-layer adapter contract. Neither the public smoke nor the diagnostic cache inspection proves total-return, cumulative, or dividend-adjusted basis.

## Required Future Contract Decision

Future maximum drawdown and volatility contract should use adjusted / total-return-equivalent basis, not raw unit NAV.

Accepted basis should be one of:

- `total_return_nav`: provider explicitly documents total-return / reinvested-distribution series.
- `cumulative_nav`: provider supplies cumulative NAV that incorporates distributions.
- `adjusted_nav`: provider supplies explicit adjusted / restored NAV with documented adjustment method.

Rejected or fail-closed basis:

- `unit_nav_only`
- `daily_growth_rate_unknown_basis`
- `cache_legacy_unknown_basis`
- any row set without explicit provider methodology or adapter-level basis proof

If adjusted basis cannot be proven, derived max drawdown / volatility must not satisfy `drawdown_stress`. It may remain a diagnostic calculation only if clearly marked ineligible and excluded from score / quality / baseline decisions.

## Provenance And Anchor Fields To Require

A future NAV source adapter gate should define a typed result that can carry:

- `source_name`: stable adapter/source name, for example `akshare.fund_open_fund_info_em` plus upstream indicator.
- `origin_source_name`: real upstream source even when served from project cache.
- `retrieved_at`: fetch time or cache `updated_at`.
- `fund_code`: normalized six-digit fund code.
- `date_range`: first and last observation dates.
- `nav_type`: unit NAV, cumulative NAV, adjusted NAV, total-return NAV, or explicit unknown.
- `adjustment_basis`: cumulative, provider-adjusted, total-return, unadjusted, or unknown.
- `dividend_adjustment_status`: explicit decision point for the future gate. The gate may either absorb this into `adjustment_basis` with documented semantics, or expose it as an independent field if dividend reinvestment / adjustment method needs separate representation.
- `record_count`: accepted observations count.
- `missing_dates`: explicit calendar / trading-day completeness result, or `not_evaluated` with fail-closed semantics.
- `calculation_method`: formula for any derived max drawdown / volatility metrics.
- `identity_status`: match / mismatch / unknown for requested fund code and returned data.
- `data_quality_status`: accepted / unavailable / schema_drift / identity_mismatch / adjustment_basis_unknown / insufficient_history.

Derived anchors must not pretend to be annual-report section anchors. A later schema gate should decide whether this is `bond_risk_evidence.v2` or a source-kind-aware v1-compatible extension.

## Failure Classification

Future adapter / source contract should classify failures as:

| Condition | Classification | Handling |
|---|---|---|
| No data for fund code or period from a valid source | `not_found` | Fail closed for derived risk evidence; fallback only if source policy explicitly allows it. |
| Network, timeout, dependency, upstream temporary failure | `source_unavailable` | Fail closed for derived risk evidence; raw annual-report extraction may continue with `NavDataResult(unavailable=True)`. |
| Returned fields differ from declared schema, required NAV/date fields missing, unexpected payload shape | `schema_drift` | Fail closed; no fallback masking unless reviewed source policy says otherwise. |
| Returned fund identity conflicts with requested code, class, or date range | `identity_mismatch` | Fail closed. |
| Only unit NAV or ambiguous `日增长率` is available, with no dividend / total-return method proof | `adjustment_basis_unknown` | Fail closed for max drawdown / volatility evidence. |
| Observation count or period is below future threshold | `insufficient_history` | Fail closed for annual risk contract; optionally report diagnostic insufficiency. |
| Non-positive NAV, duplicate / unsorted dates after normalization, parse errors | `integrity_error` | Fail closed. |

These classifications should be explicit fields, not embedded in free-form notes.

## Future Gate Slicing

### Gate 1: NAV Source Repository / Adapter Capability

Objective: create or extend a Fund-layer NAV source adapter/repository contract that exposes basis and provenance.

Allowed changes in that future gate:

- `fund_agent/fund/data/` typed NAV source result and adapter methods.
- Public adapter cache-hit metadata repair for the current `_load_cached_sync()` gap, so origin source and retrieval timestamp are exposed through the typed adapter result rather than direct SQLite reads.
- Explicit `dividend_adjustment_status` decision: document whether dividend adjustment is fully represented by `adjustment_basis` or requires an independent field.
- Tests for cache hit, origin metadata, field shape, basis classification, dividend adjustment representation, identity mismatch, schema drift, unavailable, and adjustment basis unknown.
- Fund package README / design updates only after code truth exists.

Non-goals:

- No `bond_risk_evidence` satisfaction changes.
- No score / quality / golden / baseline changes.
- No derived drawdown acceptance.

Stop condition:

- If no existing or reviewed provider can expose cumulative / adjusted / total-return basis for 006597, stop as blocked. Do not enter drawdown implementation.

### Gate 2: Derived Drawdown Evidence Contract Schema

Prerequisite: Gate 1 accepted with adjusted basis proof.

Objective: decide `bond_risk_evidence.v2` vs source-kind-aware extension and define derived anchors / per-group provenance projection.

Required decisions:

- annual-report anchor vs derived NAV anchor representation.
- per-group source/provenance projection in snapshot.
- score validation rules that machine-check `drawdown_stress` provenance.
- fail-closed behavior for legacy rows and unknown basis.

### Gate 3: Risk Metric Calculator And 006597 Validation

Prerequisite: Gate 2 accepted.

Objective: compute max drawdown / volatility only from accepted adjusted basis and rerun 006597.

Required validation:

- unit-NAV-only fixture remains rejected.
- adjusted / cumulative fixture produces deterministic metrics.
- real 006597 can only unblock if source basis and provenance are accepted.

## Plan Conclusion

The current adapter can retrieve a 006597 NAV sequence through the unified Fund-layer boundary, but cannot prove adjusted, cumulative, or total-return basis. Therefore this gate should not proceed to drawdown implementation.

`capability_decision_recommendation = blocked_pending_source_adapter`

Next minimum gate:

`NAV repository/source adapter adjusted-basis contract gate`

That gate should be a narrow Fund-layer data capability gate. It should prove or reject a provider that exposes adjusted / cumulative / total-return basis with typed provenance before any `drawdown_stress` schema, score, or quality-gate work.

## Worker Self-Check - Before File Write

- Status: pass.
- File changes are limited to `docs/reviews/release-maintenance-nav-source-capability-adjusted-basis-plan-20260528.md` and the sibling evidence artifact.
- No production code, tests, score, quality gate, schema, golden fixture, design/control truth, release / PR state, or unrelated untracked files are touched.
- The conclusion preserves blocker status and does not upgrade qualitative drawdown-control text.
