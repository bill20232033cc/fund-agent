# 004393 / 2025 Same-year Reviewed Golden Content Evidence

Date: 2026-06-13

Gate: `004393 / 2025 Same-year Reviewed Golden Content Evidence Gate`

Verdict: `EVIDENCE_FOR_REVIEW_NOT_READY`

## 1. Scope

This gate reviews candidate rows from:

```text
docs/reviews/mvp-004393-2025-same-year-reviewed-golden-content-candidate-rows-20260613.md
```

This gate does not edit tracked golden answer content, does not promote fixtures,
does not run live/provider/LLM/analyze/checklist/readiness/release/PR commands,
and does not change release/readiness state.

## 2. Basis

- Rules truth: `AGENTS.md`
- Design truth: `docs/design.md`
- Control truth: `docs/implementation-control.md`
- Startup truth: `docs/current-startup-packet.md`
- Accepted plan: `docs/reviews/mvp-004393-2025-same-year-reviewed-golden-content-plan-20260613.md`
- Plan controller judgment: `docs/reviews/mvp-004393-2025-same-year-reviewed-golden-content-plan-controller-judgment-20260613.md`
- Candidate preparation judgment: `docs/reviews/mvp-004393-2025-candidate-row-source-preparation-controller-judgment-20260613.md`
- Candidate rows: `docs/reviews/mvp-004393-2025-same-year-reviewed-golden-content-candidate-rows-20260613.md`

## 3. Boundary Statement

This evidence gate did not read the 2025 annual-report body directly and did not
run PDF/network/live commands. Therefore it does not claim primary-source
verification. It reviews the candidate source package, parser-visible row shape,
explicit `report_year: 2025` metadata, duplicate identity, source locator
plausibility and accepted source-package lineage.

The candidate source package says the rows are derived from accepted
single-sample live output locators and visible 2025 annual-report source lines,
but also says live output remains product/evidence material and not row truth.
That limitation is preserved here.

## 4. Mechanical Validation

Executed:

```text
uv run python -c "from pathlib import Path; from fund_agent.fund.golden_answer import parse_golden_answer_markdown; p=Path('docs/reviews/mvp-004393-2025-same-year-reviewed-golden-content-candidate-rows-20260613.md'); funds=parse_golden_answer_markdown(p.read_text(encoding='utf-8')); assert len(funds)==1; f=funds[0]; assert f.fund_code=='004393'; assert f.report_year==2025; assert len(f.records)==9; keys=[(r.fund_code,r.report_year,r.field_name,r.sub_field) for r in f.records]; assert len(keys)==len(set(keys)); print({'fund_code': f.fund_code, 'report_year': f.report_year, 'records': len(f.records), 'unique_keys': len(set(keys))}); [print(f'{r.field_name}.{r.sub_field}|{r.confidence}|{r.expected_value}|{r.source}') for r in f.records]"
```

Result:

```text
{'fund_code': '004393', 'report_year': 2025, 'records': 9, 'unique_keys': 9}
```

Additional state checks:

- `git diff --stat` was empty before writing this evidence artifact.
- `git status --branch --short` showed no tracked source/test/golden fixture
  changes before this evidence artifact.
- Existing untracked residue was not used as proof and was not modified.

## 5. Candidate Row Disposition

| Row | Candidate disposition | Reason | Residual |
|---|---|---|---|
| `basic_identity.fund_name` | `ACCEPT_CANDIDATE_WITH_SOURCE_BODY_RESIDUAL` | Parser-visible row is valid, `report_year=2025`, confidence is `high`, source cites `年报2025 §2 page-5 page-5-table-0 fund_name`, and the value is a direct identity field. | Primary annual-report body was not read in this gate. |
| `basic_identity.fund_code` | `ACCEPT_CANDIDATE_WITH_SOURCE_BODY_RESIDUAL` | Parser-visible row is valid, `report_year=2025`, confidence is `high`, source cites `年报2025 §2 page-5 page-5-table-0 fund_code`, and expected value matches the active fund code. | Primary annual-report body was not read in this gate. |
| `basic_identity.management_company` | `ACCEPT_CANDIDATE_WITH_SOURCE_BODY_RESIDUAL` | Parser-visible row is valid, `report_year=2025`, confidence is `high`, source cites `年报2025 §2 page-5 page-5-table-0 management_company`. | Primary annual-report body was not read in this gate. |
| `basic_identity.custodian` | `ACCEPT_CANDIDATE_WITH_SOURCE_BODY_RESIDUAL` | Parser-visible row is valid, `report_year=2025`, confidence is `high`, source cites `年报2025 §2 page-5 page-5-table-0 custodian`. | Primary annual-report body was not read in this gate. |
| `basic_identity.inception_date` | `ACCEPT_CANDIDATE_WITH_SOURCE_BODY_RESIDUAL` | Parser-visible row is valid, `report_year=2025`, confidence is `high`, source cites `年报2025 §2 page-5 page-5-table-0 inception_date`. | Primary annual-report body was not read in this gate. |
| `product_profile.investment_objective` | `ACCEPT_CANDIDATE_WITH_MEDIUM_CONFIDENCE_AND_SOURCE_BODY_RESIDUAL` | Parser-visible row is valid, `report_year=2025`, confidence is `medium`, source cites `年报2025 §2 page-5 page-5-table-1 investment_objective`; medium confidence is appropriate because this is a longer text span requiring bounded span selection. | Later write gate must preserve the row-specific medium-confidence rationale or re-read source body. |
| `benchmark.benchmark_name` | `ACCEPT_CANDIDATE_WITH_SOURCE_BODY_RESIDUAL` | Parser-visible row is valid, `report_year=2025`, confidence is `high`, source cites `年报2025 §2 page-5 page-5-table-1 benchmark`. | Primary annual-report body was not read in this gate. |
| `fee_schedule.management_fee` | `REJECT_FOR_THIS_GATE` | The row is parser-valid, but the accepted operator template marks `fee_schedule` as skipped for the current comparable contract and the locator `年报2025 §5 management_fee` lacks page/table/row or alternate-locator rationale. | Future inclusion requires a separate contract/source-owner clarification gate plus a stable locator. |
| `fee_schedule.custody_fee` | `REJECT_FOR_THIS_GATE` | The row is parser-valid, but the accepted operator template marks `fee_schedule` as skipped for the current comparable contract and the locator `年报2025 §5 custody_fee` lacks page/table/row or alternate-locator rationale. | Future inclusion requires a separate contract/source-owner clarification gate plus a stable locator. |

## 6. Deferred / Excluded Rows

| Row family | Disposition | Reason |
|---|---|---|
| `classified_fund_type.fund_type` | `DEFER_NOT_READ` | Candidate preparation explicitly deferred it because classification appeared derived and same-year source disclosure was not directly exposed. |
| `nav_benchmark_performance.*` | `DEFER_NOT_READ` | Candidate preparation says current visible appendix locators do not expose exact percentage values. |
| `share_change.*` | `DEFER_NOT_READ` | Candidate preparation says product output contains values but visible source lines only identify table/row family. |
| `manager_alignment.*` | `DEFER_NOT_READ` | Candidate preparation says product output contains long table text, but row-local exactness needs review. |
| `turnover_rate` | `DEFER_NOT_DISCLOSED` | Accepted applicability truth says 2025 and earlier annual reports do not disclose turnover rate; it remains non-applicable for this row set. |

## 7. Findings

| ID | Severity | Finding | Disposition |
|---|---|---|---|
| F1 | Medium | This gate cannot honestly accept primary-source truth because it did not read the 2025 annual-report body and did not authorize PDF/network/live commands. | Accepted as boundary; row dispositions are candidate-level with source-body residuals, not tracked golden truth. |
| F2 | Medium | `fee_schedule` appears in candidate rows while the accepted operator template/instructions mark `fee_schedule` as skipped for the current comparable contract, and the fee locators lack page/table/row specificity. | Accepted. The two fee rows are rejected for this gate and excluded from any later tracked write input unless a separate contract/source-owner clarification gate accepts them. |

## 8. Result

The gate can accept 7 of 9 parser-valid rows as reviewed candidate rows with
source-body residuals. The two fee rows are rejected for this gate. This gate
cannot accept any row as tracked strict golden truth and cannot authorize any
`reports/golden-answers/` write.

Minimum condition for a later tracked content write planning gate is satisfied
only at a candidate-disposition level: at least one row has a reviewed candidate
disposition. A later write gate must still decide whether candidate-level
acceptance is enough for its scope or whether a controlled source-body read is
required before writing tracked golden content.

Release/readiness remains `NOT_READY`.

## 9. Next Entry Recommendation

Recommended next entry:

```text
004393 / 2025 Same-year Reviewed Golden Content Controller Judgment Gate
```

Deferred entries:

- controlled source-body verification gate for candidate rows, if primary
  source truth is required before writing tracked golden content;
- tracked golden-answer content write planning gate, only after controller
  judgment accepts row dispositions and explicitly preserves write boundaries;
- fee-row contract/source-owner clarification gate, if fee rows should be
  considered again;
- fixture promotion design/evidence gate;
- release/readiness rollup gate.
