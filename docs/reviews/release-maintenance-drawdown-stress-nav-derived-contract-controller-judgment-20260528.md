# Drawdown Stress NAV-Derived Evidence Contract Gate - Controller Judgment

Date: 2026-05-28

Controller: Codex

Work unit: `drawdown_stress evidence contract / NAV-derived risk metric design gate`

Branch: `codex/local-reconciliation`

## Verdict

`blocked-with-decision`

This gate does not proceed to implementation. The current repository can consider NAV-derived drawdown evidence in principle, but the currently available NAV source, `bond_risk_evidence.v1` anchor model, and snapshot / score projection are not sufficient to safely unblock `drawdown_stress` for `006597 / 2024`.

The `006597 / 2024` bond blocker remains valid:

- `bond_risk_evidence_missing.baseline_blocking=true`
- `missing_evidence_groups=["drawdown_stress"]`

No code, schema, score, quality gate, golden fixture, release state, PR, push, merge, or promotion was changed in this gate.

## Preflight

- `git branch --show-current`: `codex/local-reconciliation`
- `git status --short`: no tracked dirty files at entry; only known unrelated untracked files:
  - `--help`
  - old comprehensive audit / repo-review artifacts
  - `docs/tmux-agent-memory-store.md`

## Source Replay

Read and used:

- `AGENTS.md`
- `docs/design.md`
- `docs/implementation-control.md`
- `docs/reviews/release-maintenance-section2-crosscheck-unit-suffix-repair-controller-judgment-20260528.md`
- `docs/reviews/code-review-20260528-081225.md`
- latest `006597 / 2024` snapshot, score, and quality-gate artifacts:
  - `reports/extraction-snapshots/bond-risk-crosscheck-suffix-006597-2024-20260528/snapshot.jsonl`
  - `reports/scoring-runs/bond-risk-crosscheck-suffix-006597-2024-20260528/score.json`
  - `reports/quality-gate-runs/bond-risk-crosscheck-suffix-006597-2024-20260528/quality_gate.json`

Current verified state:

- `credit_risk` is satisfied.
- `redemption_share_pressure` is satisfied.
- `drawdown_stress` remains weak.
- Latest score keeps the bond-risk baseline blocker only for `drawdown_stress`.

## Plan And Review Artifacts

Plan:

- `docs/reviews/release-maintenance-drawdown-stress-nav-derived-contract-plan-20260528.md`

Plan reviews:

- MiMo: `FAIL`, 4 blocking findings.
  - `docs/reviews/release-maintenance-drawdown-stress-nav-derived-contract-plan-review-mimo-20260528.md`
- DS replacement: `FAIL`, 4 blocking findings.
  - `docs/reviews/release-maintenance-drawdown-stress-nav-derived-contract-plan-review-ds-20260528.md`

## Findings Disposition

All material findings are accepted.

| Finding | Disposition | Reason |
|---|---|---|
| MiMo P1 / DS-P1: source-class and controller decisions unresolved | `accepted` | Whether NAV-derived evidence may satisfy `drawdown_stress`, and under which source allowlist, is a public evidence-contract decision and cannot be delegated to implementation. |
| MiMo P2 / DS-P2: derived anchors conflict with current `bond_risk_evidence.v1` validation | `accepted` | Current `BondRiskEvidenceAnchorRef.section_id` is non-empty and validator rejects empty section IDs; derived NAV anchors require source-kind-aware contract or schema version strategy. |
| MiMo P3 / DS-P1: current NAV source cannot prove total-return / cumulative / adjusted basis | `accepted` | Current `FundNavDataAdapter` uses Akshare `单位净值走势`; local 006597 cache exposes `净值日期`, `单位净值`, `日增长率`, but no series type, adjustment basis, cumulative NAV, or provider methodology metadata. |
| MiMo P4 / DS-P3: snapshot / score cannot machine-check per-group derived provenance | `accepted` | Current score trusts row-level `anchor_present` plus group sets. It cannot verify that `drawdown_stress` specifically has accepted source kind, calculation method, period, and provenance. |
| DS-P4: implementation slices are too broad for unresolved source capability | `accepted` | Source capability, schema migration, calculator, extractor composition, and score acceptance should not be bundled before the source basis is proven. |

## Controller Decision

NAV-derived quantitative evidence is acceptable only as a future candidate contract, not as an implementation-ready path in this gate.

Future acceptance requires all of the following before `drawdown_stress` can become accepted quantitative evidence:

- A unified Fund-layer NAV source boundary that exposes total-return, cumulative, adjusted, or otherwise dividend-aware series basis explicitly.
- Explicit provenance: source name, origin source, cache/update metadata, fund code, period, observation count, date range, and data-quality status.
- A source-kind-aware bond-risk evidence contract, likely `bond_risk_evidence.v2` or an explicitly reviewed v1-compatible extension.
- Derived anchors that do not pretend to be annual-report section anchors.
- Snapshot projection that exposes per-group evidence source / method / provenance.
- Score logic that independently validates `drawdown_stress` provenance instead of trusting row-level `anchor_present`.

Until those exist, `drawdown_stress` remains:

- `status=weak`
- `strength=qualitative_control_intent`
- `measurement_kind=control_intent`
- `na_reason=drawdown_metric_not_found`

Qualitative text such as `控制回撤` must not be upgraded to accepted quantitative evidence.

## Validation Judgment

No implementation was performed, so full implementation validation was intentionally not run in this gate.

The latest accepted validation from the previous gate remains the current empirical baseline:

- `uv run ruff check .` passed
- full pytest passed
- `FundDocumentRepository` smoke for `006597 / 2024` passed
- `006597` snapshot / score / quality gate were rerun
- score missing groups are now only `drawdown_stress`

This gate only adds plan/review/controller artifacts and a control-doc update.

## Residuals

- `006597 / 2024` remains blocked for baseline/golden purposes by `drawdown_stress`.
- Golden corpus v1 remains blocked; no promotion work is authorized or performed.
- Current raw NAV cache can remain valid for `nav_data` availability, but it must not satisfy `drawdown_stress` until a future source-capability gate proves adjusted / total-return basis.

## Next Entry Point

Open a narrower gate:

`NAV source capability / adjusted basis evidence gate`

That gate should not change `bond_risk_evidence` satisfaction or score acceptance. Its sole purpose is to prove or reject whether the existing NAV provider, or an explicitly reviewed Fund-layer provider extension, can expose a total-return / cumulative / adjusted series with sufficient provenance for risk calculations.

If that gate passes, follow with:

`bond_risk_evidence derived drawdown contract schema gate`

That later gate should decide v2 vs v1-compatible extension, derived anchor format, per-group snapshot projection, and score validation.
