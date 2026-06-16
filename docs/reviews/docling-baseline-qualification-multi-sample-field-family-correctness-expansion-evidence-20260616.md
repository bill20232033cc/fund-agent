# Docling Multi-sample Field-family Correctness Expansion Evidence - 2026-06-16

Gate: `Docling Multi-sample Field-family Correctness Evidence Gate`
Release/readiness: `NOT_READY`
Verdict candidate: `candidate_expansion_pass_not_ready`

## Scope

This evidence resumes the accepted multi-sample Docling correctness expansion after controlled same-source reference acquisition accepted S4/S5/S6 EID single-source/no-fallback metadata. It does not change source policy, parser behavior, FundDocumentRepository behavior, EvidenceAnchor schema, Service/Host/UI/renderer/quality gate, LLM route, readiness, release or PR state.

## Evidence Inputs

- Accepted S1 reviewed facts: `reports/representation-json/004393_field_family_correctness_pilot_reviewed_facts_20260615.json` sha256 `8ca8071f6c3f3fc96fe41c877c14b90697821f3b6a2272cb2cf8bb2945413beb`.
- Manifest: `reports/representation-json/full-representation-export-manifest-20260615.json` sha256 `bab5fcb81126ca501c553e94eafebcd64da2b537930833aaf81c118b648b6349`.
- Accepted prerequisite: `docs/reviews/docling-controlled-same-source-reference-acquisition-evidence-controller-judgment-20260616.md`.
- Expansion candidate JSONs and pdfplumber comparator JSONs are recorded in the durable JSON artifact.

## Method

For S4/S5/S6, the worker loaded annual reports only through `FundDocumentRepository.load_annual_report(..., force_refresh=False)`. Candidate values came from existing Docling full representation JSONs. Reference excerpts came from the returned same-source `ParsedAnnualReport` table rows. No Docling conversion, pdfplumber export, live/source acquisition, provider/LLM, analyze/checklist/golden/readiness/release/PR command or source/test/runtime edit was performed.

## Sample Results

| Sample | Fund | Year | Reference load | Reviewed families | Facts | Result |
| --- | --- | ---: | --- | ---: | ---: | --- |
| S4 | `006597` | 2024 | `eid` / `single_source_only` / fallback `False` | 5 | 17 | `pass` |
| S5 | `017641` | 2024 | `eid` / `single_source_only` / fallback `False` | 5 | 17 | `pass` |
| S6 | `110020` | 2024 | `eid` / `single_source_only` / fallback `False` | 5 | 17 | `pass` |

## Family Results

| Sample | Family | Facts | Exact/Normalized | Mismatch | Result |
| --- | --- | ---: | ---: | ---: | --- |
| S4 | `fund_identity_profile` | 5 | 5 | 0 | `pass` |
| S4 | `product_contract_profile` | 3 | 3 | 0 | `pass` |
| S4 | `performance_indicators` | 3 | 3 | 0 | `pass` |
| S4 | `expense_costs` | 3 | 3 | 0 | `pass` |
| S4 | `portfolio_structure` | 3 | 3 | 0 | `pass` |
| S4 | `manager_alignment` | 0 | 0 | 0 | `blocked` |
| S5 | `fund_identity_profile` | 5 | 5 | 0 | `pass` |
| S5 | `product_contract_profile` | 3 | 3 | 0 | `pass` |
| S5 | `performance_indicators` | 3 | 3 | 0 | `pass` |
| S5 | `expense_costs` | 3 | 3 | 0 | `pass` |
| S5 | `portfolio_structure` | 3 | 3 | 0 | `pass` |
| S5 | `manager_alignment` | 0 | 0 | 0 | `blocked` |
| S6 | `fund_identity_profile` | 5 | 5 | 0 | `pass` |
| S6 | `product_contract_profile` | 3 | 3 | 0 | `pass` |
| S6 | `performance_indicators` | 3 | 3 | 0 | `pass` |
| S6 | `expense_costs` | 3 | 3 | 0 | `pass` |
| S6 | `portfolio_structure` | 3 | 3 | 0 | `pass` |
| S6 | `manager_alignment` | 0 | 0 | 0 | `blocked` |

## Selected Fact Evidence

The full selected fact table is stored in the JSON artifact. The following examples show the evidence shape:

| Fact | Candidate | Reference excerpt | Match |
| --- | --- | --- | --- |
| `S4-F001` `fund_name` | 国泰利享中短债债券型证券投资基金 | 基金名称 | 国泰利享中短债债券型证券投资基金 | `exact_match` |
| `S4-F002` `fund_code` | 006597 | 基金主代码 | 006597 | `exact_match` |
| `S4-F003` `manager` | 国泰基金管理有限公司 | 基金管理人 | 国泰基金管理有限公司 | `exact_match` |
| `S4-F004` `custodian` | 招商银行股份有限公司 | 基金托管人 | 招商银行股份有限公司 | `exact_match` |
| `S4-F005` `contract_effective_date` | 2018 年 12 月 3 日 | 基金合同生效日 | 2018年12月3日 | `normalized_match` |
| `S4-F006` `investment_objective` | 在严格控制风险的前提下，追求稳健的投资回报。 | 投资目标 | 在严格控制风险的前提下，追求稳健的投资回报。 | `exact_match` |
| `S4-F007` `benchmark` | 中债总财富 （ 1-3 年） 指数收益率 *80% ＋一年期定期存款利率 ( 税后 )*20% | 业绩比较基准 | 中债总财富（1-3年）指数收益率*80%＋一年期定期存款利率(税后)*20% | `normalized_match` |
| `S4-F008` `risk_characteristic` | 本基金为债券型基金，预期收益和预期风险高于货币市场基金，但低于 混合型基金、股票型基金，属于较低预期风险和预期收益的产品。 | 风险收益特征 | 本基金为债券型基金，预期收益和预期风险高于货币市场基金，但低于 混合型基金、股票型基金，属于较低预期风险和预期收益的产品。 | `normalized_match` |
| `S4-F009` `period_profit_f_share` | 175,752.40 | 本期利润 | 175,752.40 | `exact_match` |

## Non-claims

- `not_source_truth`: true.
- `not_production_parser_replacement`: true.
- `not_full_field_correctness`: true.
- `not_readiness_proof`: true.
- `candidate_field_correctness_status_remains`: `not_proven`.
- EID HTML render remains `blocked_deferred` for this gate.
- pdfplumber comparator was not re-opened for S4/S5/S6.

## Residuals

- Reference excerpts are repository-loaded parsed table rows, not visual screenshots or raw PDF crop images.
- Manager alignment family was deferred in this bounded expansion evidence and must be reviewed separately before baseline disposition.
- Pdfplumber comparator was not re-opened for S4/S5/S6 in this gate.
- Docling remains candidate-only and candidate_field_correctness_status remains not_proven.

## Validation

Validation commands must be run after writing this artifact: `git diff --check` plus JSON structural checks.

## Final Evidence Result

```text
VERDICT_CANDIDATE: candidate_expansion_pass_not_ready
```
