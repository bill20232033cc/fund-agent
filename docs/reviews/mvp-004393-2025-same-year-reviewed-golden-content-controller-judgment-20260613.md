# Controller Judgment - 004393 / 2025 Same-year Reviewed Golden Content Evidence

Date: 2026-06-13

Gate: `004393 / 2025 Same-year Reviewed Golden Content Evidence Gate`

Verdict: `ACCEPT_WITH_FINDINGS_NOT_READY`

## 1. Basis

- Rules truth: `AGENTS.md`
- Design truth: `docs/design.md`
- Control truth: `docs/implementation-control.md`
- Startup truth: `docs/current-startup-packet.md`
- Accepted plan: `docs/reviews/mvp-004393-2025-same-year-reviewed-golden-content-plan-20260613.md`
- Plan controller judgment: `docs/reviews/mvp-004393-2025-same-year-reviewed-golden-content-plan-controller-judgment-20260613.md`
- Candidate preparation judgment: `docs/reviews/mvp-004393-2025-candidate-row-source-preparation-controller-judgment-20260613.md`
- Candidate rows: `docs/reviews/mvp-004393-2025-same-year-reviewed-golden-content-candidate-rows-20260613.md`
- Evidence: `docs/reviews/mvp-004393-2025-same-year-reviewed-golden-content-evidence-20260613.md`
- MiMo review: `docs/reviews/mvp-004393-2025-same-year-reviewed-golden-content-review-mimo-20260613.md`
- DS review: `docs/reviews/mvp-004393-2025-same-year-reviewed-golden-content-review-ds-20260613.md`

## 2. Controller Decision

The evidence gate is accepted as a candidate-row disposition gate only.

Accepted facts:

- The candidate artifact is parser-valid reviewed Markdown.
- The candidate artifact declares explicit `golden-answer-metadata`
  `report_year: 2025`.
- The parser-visible identity set contains exactly 9 unique
  `(004393, 2025, field, sub_field)` rows.
- Seven rows are accepted as reviewed candidate rows for future planning.
- Two fee rows are rejected for this gate.

Not accepted:

- No row is accepted as tracked strict golden truth.
- No tracked `reports/golden-answers/` content write is authorized.
- No fixture promotion is authorized.
- No primary-source verification claim is accepted, because this gate did not
  read the 2025 annual-report body directly and did not authorize PDF/network/live
  commands.
- Release/readiness remains `NOT_READY`.

## 3. Row Disposition

| Row | Controller disposition | Reason |
|---|---|---|
| `basic_identity.fund_name` | `ACCEPT_CANDIDATE_WITH_SOURCE_BODY_RESIDUAL` | Parser-valid, same-year metadata present, row identity is unique, and source locator is specific enough for candidate status. |
| `basic_identity.fund_code` | `ACCEPT_CANDIDATE_WITH_SOURCE_BODY_RESIDUAL` | Parser-valid, same-year metadata present, value matches the gate fund identity, and source locator is specific enough for candidate status. |
| `basic_identity.management_company` | `ACCEPT_CANDIDATE_WITH_SOURCE_BODY_RESIDUAL` | Parser-valid, same-year metadata present, row identity is unique, and source locator is specific enough for candidate status. |
| `basic_identity.custodian` | `ACCEPT_CANDIDATE_WITH_SOURCE_BODY_RESIDUAL` | Parser-valid, same-year metadata present, row identity is unique, and source locator is specific enough for candidate status. |
| `basic_identity.inception_date` | `ACCEPT_CANDIDATE_WITH_SOURCE_BODY_RESIDUAL` | Parser-valid, same-year metadata present, row identity is unique, and source locator is specific enough for candidate status. |
| `product_profile.investment_objective` | `ACCEPT_CANDIDATE_WITH_MEDIUM_CONFIDENCE_AND_SOURCE_BODY_RESIDUAL` | Parser-valid and in contract; `medium` confidence is appropriate because long-text span exactness requires bounded judgment. |
| `benchmark.benchmark_name` | `ACCEPT_CANDIDATE_WITH_SOURCE_BODY_RESIDUAL` | Parser-valid, same-year metadata present, row identity is unique, and source locator is specific enough for candidate status; formula exactness remains a later source-body verification concern. |
| `fee_schedule.management_fee` | `REJECT_FOR_THIS_GATE` | Accepted operator template/instructions mark `fee_schedule` as skipped for the current comparable contract, and the row lacks a stable page/table/row locator. |
| `fee_schedule.custody_fee` | `REJECT_FOR_THIS_GATE` | Accepted operator template/instructions mark `fee_schedule` as skipped for the current comparable contract, and the row lacks a stable page/table/row locator. |

## 4. Review Finding Disposition

| Finding | Source | Controller disposition |
|---|---|---|
| Fee rows lack stable locator. | MiMo F01 / DS-F2 | `ACCEPT`. Fee rows are rejected for this gate. Future reconsideration requires stable locator or explicit source-owner rationale. |
| Fee rows are outside current comparable golden contract. | DS-F1 | `ACCEPT`. Current operator template/instructions mark `fee_schedule` as skipped; this gate must not expand contract scope. |
| Candidate rows cannot be upgraded to primary-source or strict golden truth. | DS-F3 / evidence boundary | `ACCEPT`. Seven rows are accepted only as candidate rows with source-body residuals. |
| `investment_objective` has long-text span risk. | MiMo row disposition / DS row disposition | `ACCEPT_AS_NONBLOCKING_FOR_CANDIDATE`. Candidate status is accepted with medium-confidence residual; later write/source-body gate must verify exact span. |

## 5. Validation

Executed parser/identity smoke:

```text
uv run python -c "from pathlib import Path; from fund_agent.fund.golden_answer import parse_golden_answer_markdown; p=Path('docs/reviews/mvp-004393-2025-same-year-reviewed-golden-content-candidate-rows-20260613.md'); funds=parse_golden_answer_markdown(p.read_text(encoding='utf-8')); assert len(funds)==1; f=funds[0]; assert f.fund_code=='004393'; assert f.report_year==2025; assert len(f.records)==9; keys=[(r.fund_code,r.report_year,r.field_name,r.sub_field) for r in f.records]; assert len(keys)==len(set(keys)); print({'fund_code': f.fund_code, 'report_year': f.report_year, 'records': len(f.records), 'unique_keys': len(set(keys))}); [print(f'{r.field_name}.{r.sub_field}|{r.confidence}|{r.expected_value}|{r.source}') for r in f.records]"
```

Result:

```text
{'fund_code': '004393', 'report_year': 2025, 'records': 9, 'unique_keys': 9}
```

## 6. Boundary Confirmation

This gate did not perform or authorize:

- source, test or runtime behavior changes;
- tracked golden answer content edits under `reports/golden-answers/`;
- fixture promotion edits;
- live EID, network, PDF, FDR, provider, LLM, analyze, checklist, readiness,
  release or PR commands;
- cleanup, archive, push or merge actions;
- readiness/release status changes.

## 7. Residuals

| Residual | Owner | Destination |
|---|---|---|
| Seven accepted candidate rows still have source-body residuals. | Golden content/source owner | Controlled source-body verification planning gate or write planning gate with explicit source-body decision. |
| Fee rows are rejected for this gate. | Golden contract/source owner | Separate fee-row contract/source-owner clarification gate if needed. |
| Tracked golden answer content remains unchanged. | Golden answer owner | Later tracked content write planning/implementation gate only. |
| Fixture promotion remains unresolved and year-blind. | Fixture promotion owner | Separate fixture promotion design/evidence gate. |
| Release/readiness remains `NOT_READY`. | Release owner | Future readiness rollup after content/promotion residuals close. |

## 8. Next Entry

Recommended next mainline entry:

```text
004393 / 2025 Tracked Golden Content Write Planning Gate
```

Required planning constraint for that gate:

- write planning must explicitly decide whether the seven accepted candidate rows
  can be written with source-body residuals preserved, or whether a controlled
  source-body verification gate is required first;
- fee rows must be excluded unless a separate fee-row contract/source-owner
  clarification gate accepts them;
- no write implementation may start inside the planning gate.

Deferred entries:

- `004393 / 2025 Controlled Source-body Verification Gate`
- `004393 / 2025 Fee-row Contract / Source-owner Clarification Gate`
- `004393 / 2025 Tracked Golden Content Write Implementation Gate`
- fixture promotion design/evidence gate
- release/readiness rollup gate
