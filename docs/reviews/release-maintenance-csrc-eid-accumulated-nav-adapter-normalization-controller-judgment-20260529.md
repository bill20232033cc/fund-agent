# CSRC EID Accumulated NAV Adapter Normalization — Controller Judgment

日期：2026-05-29

角色：Gateflow controller，非 implementation worker。

Work unit：`CSRC EID accumulated NAV adapter normalization implementation gate`

## Verdict

**Accepted local validation.**

本 gate 已把 CSRC EID 分类累计净值 source adapter 通过 Fund data typed boundary 落地。`FundNavRepository()` 当前默认使用 CSRC EID accumulated NAV source，A/C/E/F 份额分离，输出 `accumulated_nav / accumulated_nav / verified` typed series。

本 gate没有实现 max drawdown、volatility 或 `drawdown_stress` metric，没有解除 `006597 / 2024` 的 `drawdown_stress` blocker，没有修改 bond extractor、snapshot、score、quality gate、golden fixture、Service/UI、Host/Agent/dayu，也没有 push、PR、merge、release 或 golden promotion。

## Accepted Commits

```text
6dce229 gateflow: accept plan for CSRC EID accumulated NAV adapter normalization
537d252 gateflow: accept CSRC EID accumulated NAV adapter normalization
```

## Accepted Artifacts

| Purpose | Artifact |
|---|---|
| Plan | `docs/reviews/release-maintenance-csrc-eid-accumulated-nav-adapter-normalization-implementation-plan-20260529.md` |
| Plan review: MiMo | `docs/reviews/release-maintenance-csrc-eid-accumulated-nav-adapter-normalization-implementation-plan-review-mimo-20260529.md` |
| Plan review: GLM | `docs/reviews/release-maintenance-csrc-eid-accumulated-nav-adapter-normalization-implementation-plan-review-glm-20260529.md` |
| Plan fix | `docs/reviews/release-maintenance-csrc-eid-accumulated-nav-adapter-normalization-implementation-plan-fix-20260529.md` |
| Plan re-review: MiMo | `docs/reviews/release-maintenance-csrc-eid-accumulated-nav-adapter-normalization-implementation-plan-rereview-mimo-20260529.md` |
| Plan re-review: GLM | `docs/reviews/release-maintenance-csrc-eid-accumulated-nav-adapter-normalization-implementation-plan-rereview-glm-20260529.md` |
| Implementation evidence | `docs/reviews/release-maintenance-csrc-eid-accumulated-nav-adapter-normalization-implementation-evidence-20260529.md` |
| Implementation review: MiMo | `docs/reviews/release-maintenance-csrc-eid-accumulated-nav-adapter-normalization-implementation-review-mimo-20260529.md` |
| Implementation review: GLM | `docs/reviews/release-maintenance-csrc-eid-accumulated-nav-adapter-normalization-implementation-review-glm-20260529.md` |
| Aggregate deepreview: MiMo | `docs/reviews/release-maintenance-csrc-eid-accumulated-nav-adapter-normalization-aggregate-deepreview-mimo-20260529.md` |
| Aggregate deepreview: GLM | `docs/reviews/release-maintenance-csrc-eid-accumulated-nav-adapter-normalization-aggregate-deepreview-glm-20260529.md` |

## Controller Decision

### Accepted Runtime Boundary

- `FundNavRepository()` now defaults to `CsrcEidNavSource()`.
- `FundNavRepository` consumes only `_NavSourceAdapter.load_raw_nav_source(...)` through explicit parameters: `fund_code`, `share_class`, `start_date`, `end_date`, `force_refresh`.
- `_RawNavSourceResult` is an explicit DTO with `source_nav_type`, `source_adjustment_basis`, `source_query_params`, source identity and provenance fields. No `extra_payload`, `**kwargs`, or broad source options dict was introduced.
- CSRC EID classified failures are propagated as `NavDataContractError`; this gate does not fallback to Akshare, Eastmoney, stock-sdk, or product-level mixed sources.
- Legacy `FundNavDataAdapter.load_nav_data()` remains compatible. Raw-unit typed series remains constructor-injected compatibility only and stays `strong_drawdown_evidence_eligible=False`.

### Accepted CSRC EID Source Semantics

CSRC EID accumulated NAV is accepted as implemented source-level typed evidence for the verified 006597 family:

| Fund code | Share class | Source ID | Date range | Records | Status |
|---:|---|---|---|---:|---|
| `006597` | A | `5755:2030-1010` | 2018-12-18 to 2026-05-28 | 1807 | accepted |
| `006598` | C | `5755:2030-1020` | 2018-12-18 to 2026-05-28 | 1807 | accepted |
| `014217` | E | `5755:2030-1040` | 2022-04-25 to 2026-05-28 | 994 | accepted |
| `022176` | F | `5755:2030-1050` | 2024-10-08 to 2026-05-28 | 398 | accepted |

The accepted typed values are:

- `nav_type="accumulated_nav"`
- `adjusted_basis="accumulated_nav"`
- `dividend_adjustment_status="not_applicable"`
- `identity_status="verified"`
- `strong_drawdown_evidence_eligible=True`

`strong_drawdown_evidence_eligible=True` is only a source-level eligibility flag. It does not calculate a drawdown metric, does not create `bond_risk_evidence.v1.drawdown_stress` quantitative evidence, and does not解除 `bond_risk_evidence_missing.baseline_blocking=true`.

### Rejected / Preserved Non-Goals

- stock-sdk remains evidence-only. `getFundNavHistory` is still rejected as runtime typed source because of date-shift `integrity_error`.
- `getFundDividendList` remains diagnostics/cross-check only and cannot construct `FundNavSeries`.
- `raw_unit_nav` remains not eligible as strong drawdown evidence.
- `accumulated_nav` is not relabeled as `dividend_adjusted_nav`, `total_return`, or `total_return_index`.
- A/C/E/F NAV series remain separated; no product-level aggregate NAV series was introduced.

## Validation

Implementation worker reported and reviewers accepted:

```text
uv run ruff check .
All checks passed!

uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q
925 passed, total coverage 92.37%
```

Real CSRC EID smoke succeeded through `FundNavRepository()` with `force_refresh=True` for A/C/E/F, with full source/provenance/identity captured in the implementation evidence artifact.

No extraction snapshot, score, quality gate or golden run was required in this gate because the drawdown metric consumer path was intentionally not implemented.

## Review Disposition

Plan review:

- MiMo and GLM initially returned `accepted-with-required-fixes`.
- Accepted required fixes closed Protocol/DTO ownership, repository source selection, CSRC DTO normalization path, source-level `strong_drawdown_evidence_eligible` semantics, async HTTP bridge, parser choice, pagination edge tests, stock-sdk rejection tests and docs wording.
- MiMo and GLM re-review both returned `accepted`.

Implementation review:

- MiMo returned `accepted` with low residuals.
- GLM returned `accepted` with low/info residuals.

Aggregate deepreview:

- MiMo returned `accepted`.
- GLM returned `accepted`.

Controller accepts the low residuals as non-blocking and assigns them below.

## Residuals

| Residual | Owner / next gate | Required handling |
|---|---|---|
| `drawdown_stress` blocker remains unresolved | future reviewed drawdown metric contract / implementation gate | Define metric source contract, period/window, formulas and evidence projection before any score/snapshot/quality-gate change. |
| `source_query_params` mixes HTTP params with request context such as `force_refresh` | future NAV provenance cleanup gate | Consider splitting into HTTP params and request context, or explicitly document the current tuple semantics. |
| CSRC EID source is scoped to verified 006597 family constants | future NAV source generalization gate | Add verified family mapping/search logic before supporting other fund families. |
| F direct-search gap handling is hardcoded to `022176` | future NAV source generalization gate | Generalize only after another verified share-class gap is observed and reviewed. |
| CSRC detail-page share-class parsing depends on current page text format | future schema-drift hardening gate | Existing behavior fail-closes through `schema_drift` / `identity_mismatch`; monitor source drift. |
| Duplicate-date detection is not separately implemented in CSRC normalizer | future model invariant hardening gate | Model-level record shape validation already covers duplicate dates; future cleanup can make this explicit earlier. |
| CSRC EID endpoint has no SLA | future NAV caching / source resilience gate | Evaluate cache strategy only after metric consumer requirements are accepted. |

## Next Entry Point

Next minimal gate:

```text
drawdown_stress NAV-derived metric contract / implementation gate
```

That gate must not assume this source adapter alone解除 blocker. It must first define accepted metric semantics for max drawdown / volatility or other stress metric, including period, share-class choice, formula, provenance, evidence projection, and fail-closed conditions. Only after reviewed metric evidence exists may snapshot/score/quality-gate behavior be considered.

## Closeout

This work unit is ready to advance to `ready-to-open-draft-PR` after this controller judgment and control-doc update are committed locally. External actions remain forbidden without user authorization:

- no push
- no create PR
- no merge
- no mark ready
- no release
- no golden promotion
