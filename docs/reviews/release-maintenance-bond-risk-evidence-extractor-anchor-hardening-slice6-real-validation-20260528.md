# Bond Risk Evidence Extractor / Anchor Hardening - Slice 6 Real Validation

> Date: 2026-05-28
> Role: Gateflow controller evidence
> Work unit: `bond risk evidence extractor / anchor hardening design gate`
> Target: `006597` / `2024`
> Status: validation failed; blocker still present

## Controller Self-Check

- Current gate / role: Slice 6 real validation; controller only.
- Source of truth: `AGENTS.md`, `docs/design.md`, `docs/implementation-control.md`, accepted plan and Slice 1-5 controller judgments.
- Scope boundary: public CLI validation and repository smoke only; no golden promotion, no PR/push/merge, no Host/Agent/dayu work, no QDII/FOF/110020 work.
- Stop condition: triggered. Score still contains `bond_risk_evidence_missing.baseline_blocking=true`.
- Evidence: commands and generated public outputs below.
- Next action: stop this gate as blocked-with-reason unless user authorizes a new/amended implementation slice.

## Commands

| Check | Command | Exit |
|---|---|---:|
| Branch preflight | `git branch --show-current` | 0 |
| Dirty preflight | `git status --short` | 0 |
| Repository smoke | `uv run python -c ... FundDocumentRepository().load_annual_report("006597", 2024, force_refresh=True) ...` | 0 |
| Snapshot | `uv run fund-analysis extraction-snapshot --run-id bond-risk-evidence-006597-2024-20260528 --fund-code 006597 --report-year 2024 --source-csv docs/code_20260519.csv --output-dir reports/extraction-snapshots/bond-risk-evidence-006597-2024-20260528` | 0 |
| Score | `uv run fund-analysis extraction-score --snapshot-path reports/extraction-snapshots/bond-risk-evidence-006597-2024-20260528/snapshot.jsonl --errors-path reports/extraction-snapshots/bond-risk-evidence-006597-2024-20260528/errors.jsonl --source-csv docs/code_20260519.csv --output-dir reports/scoring-runs/bond-risk-evidence-006597-2024-20260528` | 0 |
| Quality gate | `uv run fund-analysis quality-gate --score-path reports/scoring-runs/bond-risk-evidence-006597-2024-20260528/score.json --output-dir reports/quality-gate-runs/bond-risk-evidence-006597-2024-20260528` | 0 |
| Ruff | `uv run ruff check .` | 0 |
| Full pytest | `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q` | 0 |

## Repository Smoke

The smoke used `FundDocumentRepository` and did not directly access PDF/cache/source helpers.

Observed output:

- `fund_code`: `006597`
- `year`: `2024`
- `sections`: `8`
- `tables`: `85`
- `source_metadata_present`: `True`
- `pdf_cache_hit`: `False`
- `parsed_cache_hit`: `False`
- `pdf_path_present`: `True`
- `fallback_used`: `True`

This classifies the real PDF/network path as successful. It does not justify bypassing source provenance or fallback rules.

## Public Outputs

| Artifact | Path |
|---|---|
| Snapshot JSONL | `reports/extraction-snapshots/bond-risk-evidence-006597-2024-20260528/snapshot.jsonl` |
| Snapshot summary | `reports/extraction-snapshots/bond-risk-evidence-006597-2024-20260528/summary.md` |
| Snapshot errors | `reports/extraction-snapshots/bond-risk-evidence-006597-2024-20260528/errors.jsonl` |
| Score JSON | `reports/scoring-runs/bond-risk-evidence-006597-2024-20260528/score.json` |
| Score Markdown | `reports/scoring-runs/bond-risk-evidence-006597-2024-20260528/score.md` |
| Quality gate JSON | `reports/quality-gate-runs/bond-risk-evidence-006597-2024-20260528/quality_gate.json` |
| Quality gate Markdown | `reports/quality-gate-runs/bond-risk-evidence-006597-2024-20260528/quality_gate.md` |

`errors.jsonl` has 0 lines.

## Acceptance Check

### Snapshot bond record

The snapshot contains a positive `bond_risk_evidence` row, but it is partial:

- `field_name`: `bond_risk_evidence`
- `extraction_mode`: `estimated`
- `value_present`: `true`
- `anchor_present`: `true`
- `bond_risk_contract_status`: `partial`
- `bond_risk_satisfied_groups`: `duration_rate_risk`, `leverage_liquidity`, `asset_allocation_holdings_mix`, `convertible_bond_equity_exposure`
- `bond_risk_missing_groups`: empty
- `bond_risk_weak_groups`: `credit_risk`, `drawdown_stress`
- `bond_risk_ambiguous_groups`: `redemption_share_pressure`

### Score blocker

The score still contains:

- `issue_code`: `bond_risk_evidence_missing`
- `contract_id`: `bond_risk_evidence.v1`
- `baseline_blocking`: `true`
- `missing_evidence_groups`: `credit_risk`, `drawdown_stress`, `redemption_share_pressure`

Therefore the primary user acceptance criterion is not met.

### Quality gate

Quality gate status is `warn` with 7 issues. The bond-specific FQ2F issue remains present and references `reason=bond_risk_evidence_missing`.

Other warnings are existing unrelated P1/FQ4 gaps (`turnover_rate`, `holder_structure`, `share_change`) plus FQ0 info due to no strict golden answer configured for this run.

## Worker Findings

Two independent workers investigated the failure:

- DS root-cause review: `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-slice6-root-cause-review-ds-20260528.md`
- GLM evidence investigation: `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-slice6-investigation-glm-20260528.md`

Consistent findings:

| Group | Current state | Root cause | Fixable in current extractor? |
|---|---|---|---|
| `credit_risk` | weak | rating distribution tables exist, but extractor misses them because row matching requires credit/rating terms in data rows rather than accepting header-level rating tables | yes |
| `drawdown_stress` | weak | annual report has qualitative control-drawdown text only; no max drawdown, volatility, or stress metric | no |
| `redemption_share_pressure` | ambiguous | share change table exists, but extractor selects the wrong table and does not use parsed §2 share-class mapping to disambiguate A share | yes |

## Controller Classification

This is not a JSON-building failure, not a source smoke failure, and not a quality gate weakening issue.

It is a contract-faithful validation failure:

- The system now emits a positive structured `bond_risk_evidence.v1` row.
- The row preserves weak/ambiguous semantics.
- Score naturally keeps the baseline blocker because not all seven groups are accepted.
- This behavior protects the hard constraint that weak qualitative drawdown evidence must not be treated as strong quantitative evidence.

Best possible outcome within annual-report-only extractor hardening is expected to be 6/7 groups accepted with `drawdown_stress` still weak. Full blocker removal requires either a future NAV-derived max-drawdown evidence contract or a reviewed contract change. The latter would weaken the current accepted design if it simply accepts qualitative control-drawdown text.

## Validation Summary

- `uv run ruff check .`: pass.
- `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q`: 834 passed; coverage 92.22%.
- `FundDocumentRepository` real smoke: pass.
- `extraction-snapshot`: pass.
- `extraction-score`: pass.
- `quality-gate`: pass.
- Business acceptance: fail because `bond_risk_evidence_missing.baseline_blocking=true` remains.

## Disposition

Gateflow stop condition is triggered. Do not proceed to aggregate deepreview, ready-to-open-draft-PR, push, PR, merge, approval, or golden promotion.

Recommended next entry point if authorized:

1. Extractor-hardening amendment for `credit_risk` and `redemption_share_pressure` only.
2. Separate design gate for NAV-derived `drawdown_stress` evidence if the blocker must be fully解除 without weakening the current contract.
