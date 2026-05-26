# Gate A Small Baseline Corpus Candidate Selection

> Date: 2026-05-26
> Worker: AgentCodex evidence/planning specialist
> Scope: small baseline corpus candidate selection artifact only; no source, tests, README, renderer, FQ0-FQ6, Service/CLI, Host/Agent/dayu, fixtures, run output, commit, push, or PR work.

## Truth Sources

- `AGENTS.md`
- `docs/design.md` current design sections
- `docs/implementation-control.md` Startup Packet / Current Truth Guardrails / Current Gate / Next Entry Point
- Accepted S0/S1/S2/report-quality artifacts listed below:
  - `docs/reviews/release-maintenance-report-quality-baseline-s0-corpus-selection-evidence-20260525.md`
  - `docs/reviews/release-maintenance-report-quality-baseline-s0-corpus-selection-evidence-controller-judgment-20260525.md`
  - `docs/reviews/release-maintenance-report-quality-baseline-s1-score-schema-fixture-draft-controller-judgment-20260525.md`
  - `docs/reviews/release-maintenance-report-quality-baseline-s1-dry-run-evidence-controller-judgment-20260525.md`
  - `docs/reviews/release-maintenance-fact-evidence-contract-s2-bundle-candidate-plan-controller-judgment-20260525.md`
  - `docs/reviews/release-maintenance-report-quality-validator-quasi-real-bundle-controller-judgment-20260526.md`

## Boundary Statement

This artifact selects candidates from already accepted evidence only. I did not fetch or parse annual reports, call production extractors, call `FundDocumentRepository`, call PDF/cache/source helpers, call downloaders/source adapters, or inspect ignored run outputs as new evidence.

`candidate != durable baseline`. No sample below is promoted to `accepted_baseline`, no fixture is created, and no sample is marked `scoring_ready`.

## Selection Rules Applied

1. Prefer S0-clean candidates with repository-verified annual-report identity and no unresolved fallback upstream category.
2. Do not promote fallback-only, unknown source boundary, `probe_only`, or `type_gap` samples to durable baseline.
3. Treat QDII-FOF as a FOF coverage attempt only when accepted evidence says it is a data gap; do not count it as fulfilled pure `fof_fund`.
4. Preserve S1/S2 lifecycle discipline: `repository_verified` is not `fact_prefill_reviewed`, `scoring_ready`, or `accepted_baseline`.

## Candidate Table

| fund_code | report_year | fund_type_slot | selection reason | data source status | repository_verified | scoring_ready | main risk |
|---|---:|---|---|---|---|---|---|
| `004393` | 2024 | `active_fund` | S0 accepted active-fund candidate; existing reviewed golden rows present; S1 dry-run used this fund for one narrow Chapter 3 pass and one localized turnover-rate issue. | S0 annual-report identity verified; no fallback risk recorded in accepted S0 table. | Yes: document identity and current classifier match `active_fund`. | No: S1 dry-run proves minimal issue localization only, not whole-candidate scoring readiness. | Chapter 3 turnover/style-consistency evidence gap remains; next contract wording gate must prevent unsupported stability claims. |
| `004194` | 2024 | `enhanced_index` | S0 accepted enhanced-index candidate; existing reviewed golden section present; source metadata identifies EID annual report. | S0 annual-report identity verified with EID metadata and no fallback risk recorded. | Yes: document identity and current classifier match `enhanced_index`. | No: fact review is uneven and no scoring-ready controller acceptance exists. | Enhanced-index evidence may still be benchmark-context only; do not infer tracking-error readiness without later reviewed facts. |
| `006597` | 2024 | `bond_fund` | S0 accepted bond-fund candidate; existing reviewed golden section present. | S0 annual-report identity verified; no fallback risk recorded in accepted S0 table. | Yes: document identity and current classifier match `bond_fund`. | No: no accepted scoring-ready freeze exists. | Bond-specific preferred-lens facts and anchors still need reviewed scoring input before baseline use. |
| `110020` | 2024 | `index_fund` | S0 accepted index-fund repository evidence, giving index slot coverage for planning. | S0 metadata says `eastmoney`, `fallback_used=True`; original upstream failure category is unknown. | Yes for annual-report identity and current classifier; not eligible for durable baseline until fallback category is recovered. | No. | `unknown_upstream_failure_category`; must recover `not_found`/`unavailable` or exclude before durable baseline selection. |
| `017641` | 2024 | `qdii_fund` | S0 accepted QDII repository evidence, giving QDII slot coverage for planning. | S0 metadata says `eastmoney`, `fallback_used=True`; original upstream failure category is unknown. | Yes for annual-report identity and current classifier; not eligible for durable baseline until fallback category is recovered. | No. | `unknown_upstream_failure_category`; must recover `not_found`/`unavailable` or exclude before durable baseline selection. |
| `007721` | 2024 | `fof_fund` attempt / `data_gap` | S0 attempted FOF through a QDII-FOF selected-fund candidate; existing reviewed rows identify it as QDII-FOF, but accepted evidence records current classifier and reviewed golden type as `qdii_fund`. | Annual report is loadable per S0, but type-slot membership is a gap. | No for `fof_fund` slot: document may be verified, but accepted state is `verified_as_annual_report_but_type_gap` / `candidate`. | No. | Cannot satisfy pure FOF coverage; needs pure FOF second pass or fund-type taxonomy / QDII-FOF precedence gate. |
| `017970` | 2024 | `fof_fund` attempt / `data_gap` | S0 attempted another QDII-FOF selected-fund candidate; current public classifier returns `qdii_fund`; no reviewed golden section observed. | Annual report is loadable per S0, but source metadata says `eastmoney`, `fallback_used=True`; upstream failure category unknown. | No for `fof_fund` slot: document may be verified, but accepted state is `verified_as_annual_report_but_type_gap` / `candidate`. | No. | Double blocker: FOF type gap plus `unknown_upstream_failure_category`; cannot enter durable baseline selection. |

## Evaluation Plan Eligibility

Candidates that may enter the next evaluation plan as clean corpus candidates, subject to explicit fact-review / scoring-ready freeze:

- `004393` / 2024 / `active_fund`
- `004194` / 2024 / `enhanced_index`
- `006597` / 2024 / `bond_fund`

Candidates that may enter a later evaluation plan only after source-boundary recovery proves the fallback was eligible (`not_found` or `unavailable`) or the candidate is replaced:

- `110020` / 2024 / `index_fund`
- `017641` / 2024 / `qdii_fund`

Candidates that remain data gaps / residuals and must not be treated as fulfilled pure FOF coverage:

- `007721` / 2024 / QDII-FOF evidence for `fof_fund` attempt
- `017970` / 2024 / QDII-FOF evidence for `fof_fund` attempt

## Coverage Result

| fund_type_slot | Gate A status | Evidence basis |
|---|---|---|
| `active_fund` | Covered for candidate planning | `004393` clean S0 candidate; S1 dry-run localized one Chapter 3 pass and one issue. |
| `index_fund` | Covered only as blocked candidate planning | `110020` is repository evidence, but fallback upstream category is unresolved. |
| `enhanced_index` | Covered for candidate planning | `004194` clean S0 candidate. |
| `bond_fund` | Covered for candidate planning | `006597` clean S0 candidate. |
| `qdii_fund` | Covered only as blocked candidate planning | `017641` is repository evidence, but fallback upstream category is unresolved. |
| `fof_fund` | `data_gap` | S0 attempted `007721` and `017970`; both classify as `qdii_fund`, so pure FOF is not fulfilled. |

## Durable Baseline Non-Promotion

No candidate in this artifact is a durable baseline. The accepted state remains:

- no `scoring_ready` corpus exists;
- no `accepted_baseline` exists;
- ignored scoring/data-source outputs remain scratch only;
- quasi-real validator evidence is consumer-contract evidence only and explicitly not repository-verified, scoring-ready, or baseline material.

## Suggested Control Doc Updates

Do not update `docs/implementation-control.md` in this gate. Suggested future control-doc update points for the controller:

1. Add this artifact as Gate A candidate-selection evidence under accepted artifacts if accepted.
2. Record the clean evaluation-plan candidate set as `004393`, `004194`, and `006597`.
3. Record `110020` and `017641` as fallback-blocked candidates requiring upstream failure-category recovery before durable baseline selection.
4. Preserve FOF as `data_gap`; record `007721` and `017970` as QDII-FOF/type-gap evidence, not fulfilled `fof_fund`.
5. Reconfirm that durable baseline promotion remains blocked until fact review, scoring-ready freeze, fallback recovery or replacement, and later curated-fixture gate are accepted.

## Residual Risks

| Residual | Required handling |
|---|---|
| Only three clean candidate slots are currently eligible for near-term evaluation planning. | Either run a later accepted source-boundary recovery gate for `110020` / `017641`, or replace them through a reviewed corpus second pass. |
| Pure FOF coverage is missing. | Find a repository-verified pure `fof_fund`, or open a fund-type taxonomy / QDII-FOF precedence gate before counting QDII-FOF as FOF coverage. |
| Existing reviewed golden coverage is uneven. | Generate and review fact prefill evidence before any scoring-ready freeze. |
| `004393` has a known Chapter 3 turnover-rate gap. | Complete the active-fund Chapter 3 turnover/style-consistency contract wording gate before deciding whether data extraction is required. |
| Fallback evidence can be misread as repository safety. | Keep fallback candidates out of durable baseline until original upstream failure category is recovered and accepted. |

## Validation

Read-only commands run:

```text
git status --short
rg -n "S0|S1|S2|accepted|candidate|baseline|fund_code|fund_type|active_fund|index_fund|enhanced_index|bond_fund|qdii_fund|fof_fund|FOF|data_gap|fallback|probe_only|type_gap|repository_verified|scoring_ready" docs/design.md docs/implementation-control.md docs/reviews
sed -n '1,190p' docs/implementation-control.md
sed -n '1,220p' docs/design.md
sed -n '1,260p' docs/reviews/release-maintenance-report-quality-baseline-s0-corpus-selection-evidence-20260525.md
sed -n '1,220p' docs/reviews/release-maintenance-report-quality-baseline-s0-corpus-selection-evidence-controller-judgment-20260525.md
sed -n '1,260p' docs/reviews/release-maintenance-report-quality-baseline-s1-score-schema-fixture-draft-controller-judgment-20260525.md
sed -n '1,260p' docs/reviews/release-maintenance-report-quality-baseline-s1-dry-run-evidence-controller-judgment-20260525.md
sed -n '1,300p' docs/reviews/release-maintenance-fact-evidence-contract-s2-bundle-candidate-plan-controller-judgment-20260525.md
sed -n '1,260p' docs/reviews/release-maintenance-report-quality-validator-quasi-real-bundle-controller-judgment-20260526.md
test -e docs/reviews/release-maintenance-small-baseline-corpus-candidate-selection-20260526.md; printf '%s\n' $?
rg -n "004393|110020|004194|006597|017641|007721|017970|repository_verified|scoring_ready|unknown_upstream_failure_category|data_gap|durable baseline|candidate != durable|quasi_real_review_evidence" docs/reviews/release-maintenance-report-quality-baseline-s0-corpus-selection-evidence-20260525.md docs/reviews/release-maintenance-report-quality-baseline-s0-corpus-selection-evidence-controller-judgment-20260525.md docs/reviews/release-maintenance-report-quality-baseline-s1-score-schema-fixture-draft-controller-judgment-20260525.md docs/reviews/release-maintenance-report-quality-baseline-s1-dry-run-evidence-controller-judgment-20260525.md docs/reviews/release-maintenance-fact-evidence-contract-s2-bundle-candidate-plan-controller-judgment-20260525.md docs/reviews/release-maintenance-report-quality-validator-quasi-real-bundle-controller-judgment-20260526.md
```

Result:

- Existing worktree had one unrelated untracked artifact: `docs/reviews/release-maintenance-deepreview-controller-judgment-20260526.md`.
- Target artifact did not exist before this gate.
- Accepted evidence is sufficient for 7 candidate/data-gap rows. Because pure FOF is not available from accepted evidence, this artifact records FOF as `data_gap` rather than fetching more data.
