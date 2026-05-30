# release-maintenance bond-lens score applicability implementation evidence - 2026-05-27

> Worker: AgentCodex implementation worker
> Gate: `bond-lens score applicability implementation gate`
> Latest accepted checkpoint supplied by handoff: `02741e0`
> Scope: implementation only; no commit, no push, no PR

## Scope Guard Confirmation

- Stayed within the accepted implementation scope: Fund scoring, Fund quality gate, focused tests, Fund/test README sync, and this evidence artifact.
- Did not modify renderer, Service/CLI, Host/Agent/dayu, `FundDocumentRepository`, source strategy/helpers/cache/downloaders, extractor logic, `fund_type.py`, golden/baseline fixtures, FQ0-FQ6 thresholds/policy, `extra_payload`, or GitHub state.
- 006597 evidence used the existing public CLI path from an existing public snapshot artifact; no direct source helper, PDF cache, or repository internals were used.

## Files Changed

- `fund_agent/fund/extraction_score.py`
- `fund_agent/fund/quality_gate.py`
- `tests/fund/test_extraction_score.py`
- `tests/fund/test_quality_gate.py`
- `fund_agent/fund/README.md`
- `tests/README.md`
- `docs/reviews/release-maintenance-bond-lens-score-applicability-implementation-evidence-20260527.md`

Pre-existing unrelated untracked files were left untouched:

- `docs/reviews/release-maintenance-comprehensive-audit-report-20260526.md`
- `docs/reviews/repo-review-20260526-231040.md`
- `docs/tmux-agent-memory-store.md`

## Behavior Summary

- Added explicit `BondRiskEvidenceGroup` with seven groups:
  `duration_rate_risk`, `credit_risk`, `leverage_liquidity`, `asset_allocation_holdings_mix`, `drawdown_stress`, `redemption_share_pressure`, `convertible_bond_equity_exposure`.
- For exact `bond_fund`, `holdings_snapshot` is excluded from stock-holdings scoring denominator only with paired `bond_risk_evidence.v1` replacement issue output.
- Added additive `score.json` top-level arrays:
  `field_applicability_decisions` and `score_applicability_issues`.
- Deterministic issue id format implemented:
  `score-applicability:{fund_code}:{report_year}:{field_name}:{issue_code}:{contract_id}`.
- Unknown or conflicted fund types fail closed: no bond-specific exclusion and no bond replacement issue.
- `FundQualityRow.missing_field_rate` remains the applicable missing rate after filtering; raw/applicable denominator observability is carried in `field_applicability_decisions`.
- `quality_gate.py` treats missing `score_applicability_issues` as an empty list for old score JSON compatibility.
- `bond_risk_evidence_missing` projects to warn-level `FQ2F` using existing `QualityGateIssue.reason` / `message`; `QualityGateIssue` was not extended.
- FQ4 thresholds and severity policy remain unchanged: warn `>= 0.20`, block `>= 0.35`.

## Review Fix Note

After PASS_WITH_FINDINGS review, one accepted narrow fix was applied:

- `quality_gate.py` now validates `score_applicability_issues[].issue_id` by exact deterministic equality:
  `score-applicability:{fund_code}:{report_year}:{field_name}:{issue_code}:{contract_id}`.
- `report_year` is read from the issue object and participates in exact validation, so a wrong year segment in `issue_id` is rejected.
- Added focused coverage in `tests/fund/test_quality_gate.py` for wrong `report_year` segment rejection.

## Tests Run

```text
uv run pytest tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py -q
```

Result: `71 passed in 0.72s` on final run.

Post-review narrow fix validation:

```text
uv run pytest tests/fund/test_quality_gate.py -q
```

Result: `30 passed in 0.06s`.

```text
uv run ruff check fund_agent/fund/extraction_score.py fund_agent/fund/quality_gate.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py
```

Result: `All checks passed!`

Post-review narrow fix lint:

```text
uv run ruff check fund_agent/fund/quality_gate.py tests/fund/test_quality_gate.py
```

Result: `All checks passed!`

```text
git diff --check
```

Result: passed with no output.

## Focused Coverage Added

- Extraction score:
  - exact `bond_fund` holdings exclusion plus replacement issue
  - deterministic issue id
  - active fund regression
  - index/enhanced regression
  - unknown/conflicted fund type fail-closed behavior
- Quality gate:
  - `score_applicability_issues` projection to `FQ2F/warn`
  - malformed issue fail-fast
  - missing-key compatibility for old score JSON
  - FQ4 threshold preservation
  - synthetic 006597-like anti-mis-pass

## 006597 Evidence

Existing pre-change public run used for before counts:

```text
reports/quality-gate-runs/analyze-006597-2024-20260526T180537875780Z/score.json
```

Before:

- `fund_quality.missing_field_count`: `5`
- `fund_quality.total_field_count`: `14`
- `fund_quality.missing_field_rate`: `0.35714285714285715`
- `missing_p1_fields`: `holder_structure`, `holdings_snapshot`, `share_change`, `turnover_rate`
- `score_applicability_issues`: missing / not present

Evidence commands:

```text
uv run fund-analysis extraction-score \
  --snapshot-path reports/quality-gate-runs/analyze-006597-2024-20260526T180537875780Z/snapshot.jsonl \
  --output-dir reports/quality-gate-runs/bond-lens-006597-2024-score-applicability-evidence
```

```text
uv run fund-analysis quality-gate \
  --score-path reports/quality-gate-runs/bond-lens-006597-2024-score-applicability-evidence/score.json \
  --output-dir reports/quality-gate-runs/bond-lens-006597-2024-score-applicability-evidence
```

After:

- `fund_quality.missing_field_count`: `4`
- `fund_quality.total_field_count`: `13`
- `fund_quality.missing_field_rate`: `0.3076923076923077`
- `missing_p1_fields`: `holder_structure`, `share_change`, `turnover_rate`
- `field_applicability_decisions[0].raw_total_field_count`: `14`
- `field_applicability_decisions[0].raw_missing_field_count`: `5`
- `field_applicability_decisions[0].raw_missing_field_rate`: `0.35714285714285715`
- `field_applicability_decisions[0].applicable_total_field_count`: `13`
- `field_applicability_decisions[0].applicable_missing_field_count`: `4`
- `field_applicability_decisions[0].applicable_missing_field_rate`: `0.3076923076923077`
- replacement issue id:
  `score-applicability:006597:2024:holdings_snapshot:bond_risk_evidence_missing:bond_risk_evidence.v1`
- `quality_gate.status`: `warn`
- projected replacement issue: `FQ2F/warn`, `reason=bond_risk_evidence_missing`

Anti-mis-pass conclusion: 006597 no longer blocks solely on the equity-shaped holdings denominator, but it does not pass. FQ4 threshold policy was unchanged; the resulting gate remains `warn` due to FQ2/FQ2F warnings, FQ4 warn, FQ0 info, and the explicit `bond_risk_evidence_missing` replacement issue.

## Post-Review Fix

Initial code reviews found one low-severity issue worth fixing before closeout: `score_applicability_issues[].issue_id` validation checked only prefix/suffix and did not prove the `report_year` segment matched the issue row.

Fix applied:

- `quality_gate.py` now reconstructs the full deterministic id as `score-applicability:{fund_code}:{report_year}:{field_name}:{issue_code}:{contract_id}` and requires exact equality.
- `quality_gate.py` now reads `report_year` from each score-applicability issue as a required non-empty string.
- `tests/fund/test_quality_gate.py` adds a wrong-report-year issue-id fail-fast regression.

Post-fix validation:

```text
uv run pytest tests/fund/test_quality_gate.py -q
```

Result: `30 passed`.

```text
uv run pytest tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py -q
```

Result: `72 passed`.

```text
uv run ruff check fund_agent/fund/quality_gate.py tests/fund/test_quality_gate.py
```

Result: `All checks passed!`

```text
git diff --check
```

Result: passed with no output.

## Residual Risks

- `bond_risk_evidence.v1` is declared and fail-closed, but no positive bond-risk extraction/evidence input is implemented in this gate. Current exact `bond_fund` snapshots with `holdings_snapshot` therefore emit `bond_risk_evidence_missing`.
- `baseline_blocking=true` is emitted in score JSON, but durable baseline/golden promotion remains a future gate consumer per accepted controller judgment.
- Existing public 006597 snapshot still has non-holdings P1 gaps (`holder_structure`, `share_change`, `turnover_rate`) and score-contract residuals; this gate intentionally does not fix extractor logic.
