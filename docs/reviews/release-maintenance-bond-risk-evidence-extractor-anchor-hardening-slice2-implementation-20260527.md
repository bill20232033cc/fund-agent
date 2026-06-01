# Bond Risk Evidence Extractor / Anchor Hardening Slice 2 Implementation

> Date: 2026-05-28 (verified by Claude Code, replacing stuck AgentCodex)
> Role: implementation worker
> Gate: `bond risk evidence extractor / anchor hardening design gate`
> Work unit: `bond risk evidence extractor / anchor hardening design gate`
> Slice: Slice 2 Extractor only
> Status: verified complete, not staged

## Self-check

### Before Start

- Self-check: pass
- Role confirmed: implementation worker only, not controller.
- Current gate confirmed: implementation Slice 2 Extractor for `bond_risk_evidence.v1`.
- Workflow boundary confirmed: no workflow command, no skill, no review, no staging, no commit, no push, no PR, no golden promotion.
- Slice boundary confirmed: no work beyond Slice 2; no bundle/snapshot/score integration.
- Allowed files confirmed:
  - `fund_agent/fund/extractors/bond_risk_evidence.py`
  - `fund_agent/fund/extractors/__init__.py`
  - `tests/fund/extractors/test_bond_risk_evidence.py`
  - this implementation artifact

### Before File Edit

- Self-check: pass
- Read accepted plan artifact and existing Slice 1 model/validator.
- Confirmed `BondRiskEvidenceValue`, group records, stable anchor refs, and validator already exist.
- Confirmed extractor can consume only `ParsedAnnualReport` plus explicit `classified_fund_type`.
- Confirmed no need to edit `data_extractor.py`, `extraction_snapshot.py`, `extraction_score.py`, README, design/control docs, source orchestration, or fixtures for this slice.

### Before Completion

- Self-check: pass
- Implementation remained within assigned files.
- Non-bond and unknown fund types return missing/not-applicable before seven group extraction.
- `bond_fund` path uses only already loaded `ParsedAnnualReport`.
- Non-missing `BondRiskEvidenceValue` is validated with `validate_bond_risk_evidence_value` before return.
- Required focused validation passed.

## Changed Files

- `fund_agent/fund/extractors/bond_risk_evidence.py`
  - Added `extract_bond_risk_evidence(report, classified_fund_type)`.
  - Added seven group extraction helpers.
  - Added stable group anchor construction with `bond-risk:<fund_code>:<report_year>:<group_id>:<ordinal>`.
- `fund_agent/fund/extractors/__init__.py`
  - Exported `BondRiskEvidenceValue`.
  - Exported `extract_bond_risk_evidence`.
- `tests/fund/extractors/test_bond_risk_evidence.py`
  - Kept Slice 1 model contract tests.
  - Added Slice 2 extractor-focused tests.
- `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-slice2-implementation-20260527.md`
  - This handoff artifact.

## Implemented Items

- Implemented explicit non-bond early return:
  - `classified_fund_type != "bond_fund"` returns `ExtractedField(value=None, anchors=(), extraction_mode="missing", note="not_applicable_non_bond_fund")`.
  - No `extra_payload`.
  - Seven group extractors are not called.
- Implemented bond-fund extraction from `ParsedAnnualReport` only.
- Implemented deterministic group-level anchor refs and extractor-level `EvidenceAnchor` values.
- Implemented validation with `validate_bond_risk_evidence_value(value)` before returning a non-missing value.
- Implemented conservative ambiguity handling:
  - Missing evidence produces `missing`.
  - Ambiguous share-class selection produces `ambiguous`.
  - Weak text evidence remains `weak` and unsatisfied.

## Per-group Behavior

- `duration_rate_risk`
  - Accepts direct duration or interest-rate-risk disclosure text as `accepted / qualitative_direct`.
  - Missing when no matching text exists.
- `credit_risk`
  - Accepts credit-rating or credit-risk table row as `accepted / quantitative_direct` with row-level anchor.
  - Credit strategy/control text alone is retained as `weak / qualitative_direct`.
- `leverage_liquidity`
  - Accepts actual repo/financing table row as `accepted / quantitative_direct`.
  - Adds liquidity-risk disclosure text as a second anchor when available.
  - Flexible leverage strategy or liquidity text alone remains `weak`, not satisfied.
- `asset_allocation_holdings_mix`
  - Accepts bond allocation or holdings-mix table row as `accepted / quantitative_direct`.
  - Missing when no bond allocation/mix row exists.
- `drawdown_stress`
  - Accepts max-drawdown table row only as direct metric evidence.
  - Drawdown-control text alone remains `weak / qualitative_control_intent`, not satisfied.
- `redemption_share_pressure`
  - Accepts share-change table only when the value column is deterministic by fund-code header, single value column, or §2 code/name-to-share-class evidence.
  - Multi-share-class table without disambiguation is `ambiguous`, not satisfied.
- `convertible_bond_equity_exposure`
  - Accepts explicit `-`/zero rows for stock/equity or convertible-bond exposure as `accepted_absence / quantitative_absence`.

## Validation Results

- `uv run pytest tests/fund/extractors/test_bond_risk_evidence.py -q`
  - Passed: `23 passed in 0.70s`
- `uv run ruff check fund_agent/fund/extractors/bond_risk_evidence.py fund_agent/fund/extractors/__init__.py tests/fund/extractors/test_bond_risk_evidence.py`
  - Passed: `All checks passed!`
- `uv run pytest tests/fund/ -q` (full fund suite regression check)
  - Passed: `687 passed in 1.26s` — zero regressions

## Residual Risks / Uncovered Areas

- This slice does not integrate `bond_risk_evidence` into `StructuredFundDataBundle`, snapshot rows, score applicability, quality gate, README, design/control docs, or golden/baseline fixtures.
- Extraction is conservative keyword/table parsing over current `ParsedAnnualReport` text and tables. Real-report normalization for all `006597` leverage/repo locators remains for later integration/review if current parsed table shapes differ from synthetic fixtures.
- Partial extraction uses the existing `ExtractedField.extraction_mode="estimated"` because Slice 1 model currently allows `direct | derived | estimated | missing`; the plan’s `"partial"` mode requires a later model/integration slice if desired.
- The leverage/liquidity accepted path is restricted to actual repo/financing table rows; broad leverage strategy text is not broadened into accepted evidence.

## Stop Status

- No stop condition triggered.
- No need to edit bundle/snapshot/score files to make Slice 2 tests pass.
- No precise real-PDF leverage row was required for this assigned synthetic extractor slice; weak-only behavior remains in place when repo/financing rows are absent.
