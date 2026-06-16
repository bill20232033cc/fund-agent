# Docling Source-truth Residual Closure Plan - 2026-06-16

Gate: `Docling Source-truth Residual Closure Planning Gate`
Role: planning worker
Gate classification: `heavy`
Release/readiness: `NOT_READY`

## 1. Goal

Create a handoff-ready no-live implementation and evidence plan for the 17 residual rows from:

```text
reports/docling-baseline-support-source-truth/20260616/source_truth_matrix.json
```

The target is not to force `17 / 17` closure. The target is to classify every residual through the accepted `source -> processed -> fund` contract:

- close rows only when source identity, processed locator and fund semantic rule all agree;
- keep rows as residual/blocker when the same-source body or benchmark-labeled context cannot be proven;
- preserve `NOT_READY`.

## 2. Accepted Inputs

| Input | Use |
| --- | --- |
| `docs/reviews/fund-disclosure-processor-contract-design-controller-judgment-20260616.md` | Binding contract and guardrails for this planning gate. |
| `docs/reviews/fund-disclosure-processor-contract-design-20260616.md` | `source -> processed -> fund` design, locator requirements and residual handling rules. |
| `docs/reviews/docling-baseline-support-source-truth-evidence-controller-judgment-20260616.md` | Accepted upstream fact: `55 / 72` source-body matches and `17 / 72` residual/blocker rows. |
| `reports/docling-baseline-support-source-truth/20260616/source_truth_matrix.json` | Machine-readable residual rows and source-body evidence state. |
| `reports/docling-field-correctness-anchor-coverage-no-live-implementation/20260616/anchor_coverage_after_matrix.json` | Candidate anchor mapping state, if implementation needs mapped anchor fields. |
| `reports/docling-field-correctness-comparative/20260616/field_comparison_matrix.json` | Candidate/reference comparison context, if implementation needs fact-family metadata. |
| Existing candidate representation JSONs under `reports/representation-json/` | Candidate-only processed-layer locator inputs. Must not be treated as source truth. |

## 3. Hard Boundaries

Implementation and evidence workers must not:

- change `FundDocumentRepository` behavior;
- change production parser behavior;
- change public `EvidenceAnchor` schema;
- read PDF files, cache internals or source-helper bodies directly;
- run live/network/EID/provider/LLM/analyze commands;
- run Docling conversion;
- use parser-vs-parser agreement as source truth;
- claim full field correctness, baseline qualification, parser replacement, release readiness or PR readiness.

Allowed document access:

- source-reference evidence may use `FundDocumentRepository.load_annual_report(..., force_refresh=False)` only under no-live/cache-only guard semantics;
- if no no-live repository reference can be proven, the affected row must be `blocked_reference_unavailable`.

## 4. Residual Rows In Scope

| Row | Field | Current disposition | Required closure rule |
| --- | --- | --- | --- |
| `S1 / F002` | `fund_code` | `ambiguous_source_body_match` | Must match §2 profile table row label `基金主代码`; reject `交易代码` and `下属分级基金的交易代码`. |
| `S1 / F015` | `sales_service_fee_C_current_year` | `ambiguous_source_body_match` | Must match the sales-service-fee table with C-share/current-period column context; if duplicate total/vendor rows are semantically indistinguishable, keep explicit ambiguity instead of forcing uniqueness. |
| `S1 / F020` | `manager_holding_range_A` | `ambiguous_source_body_match` | Must match manager-holding table row `本基金基金经理持有本开放式基金` and A-share/class context; reject `合计` unless the field rule explicitly asks for total. |
| `S4 / S4-F001` | `fund_name` | `ambiguous_source_body_match` | Must match §2 profile table row label `基金名称`; repeated footer/header/name occurrences are not sufficient. |
| `S4 / S4-F002` | `fund_code` | `ambiguous_source_body_match` | Must match §2 profile table row label `基金主代码`; reject trading-code and share-class rows. |
| `S4 / S4-F015` | `fixed_income_investment_amount` | `ambiguous_source_body_match` | Must match §8 portfolio composition table row `固定收益投资`; reject fair-value hierarchy rows such as `第二层次` or generic `合计`. |
| `S5 / S5-F018` | `fund_name` | `ambiguous_source_body_match` | Must match §2 profile table row label `基金名称`. |
| `S5 / S5-F019` | `fund_code` | `ambiguous_source_body_match` | Must match §2 profile table row label `基金主代码`; reject trading-code and share-class rows. |
| `S5 / S5-F023` | `investment_objective` | `source_body_mismatch` | Triage source scope, processed locator and fund semantic assignment. If same-source repository body still has no normalized match, keep `source_body_mismatch`. |
| `S5 / S5-F032` | `equity_investment_amount` | `ambiguous_source_body_match` | Must match §8 portfolio composition table row `权益投资`; reject `其中：普通股` and country/region rows. |
| `S6 / S6-F035` | `fund_name` | `ambiguous_source_body_match` | Must match §2 profile table row label `基金名称`; reject ETF master-fund references, headers and footers. |
| `S6 / S6-F036` | `fund_code` | `ambiguous_source_body_match` | Must match §2 profile table row label `基金主代码`; reject share-class trading-code rows. |
| `S6 / S6-F037` | `manager` | `ambiguous_source_body_match` | Must match §2 profile table row `基金管理人` or `基金管理人名称`; repeated cover/header text is not enough. |
| `S6 / S6-F038` | `custodian` | `ambiguous_source_body_match` | Must match §2 profile table row `基金托管人` or `基金托管人名称`; repeated cover/header text is not enough. |
| `S6 / S6-F041` | `benchmark` | `semantic_assignment_residual` | Must not close unless benchmark-labeled source context is found. The shared investment-objective candidate cell remains insufficient. |
| `S6 / S6-F049` | `equity_investment_amount` | `ambiguous_source_body_match` | Must match §8 portfolio composition table row `权益投资`; reject `其中：股票`. |
| `S6 / S6-F050` | `stock_investment_amount` | `ambiguous_source_body_match` | Must match §8 portfolio composition table row `其中：股票`; reject parent row `权益投资`. |

## 5. Implementation Slice

### 5.1 Scope

Implement a candidate-internal residual closure helper under:

```text
fund_agent/fund/documents/candidates/
```

Suggested new file:

```text
fund_agent/fund/documents/candidates/source_truth_residual_closure.py
```

Suggested tests:

```text
tests/fund/documents/test_docling_source_truth_residual_closure.py
```

This helper must be candidate-only. It must not be imported from `fund_agent.fund.documents` public package exports.

### 5.2 Public Helper API

The implementation worker may adjust names, but the helper must expose equivalent behavior:

```python
def close_source_truth_residuals(
    *,
    source_truth_matrix: Mapping[str, object],
    candidate_documents: Mapping[str, CandidateRepresentationDocument],
    repository_reference_rows: Mapping[str, object],
) -> SourceTruthResidualClosureMatrix:
    ...
```

The API must:

- consume already loaded JSON-like payloads or already projected candidate documents;
- not read files internally;
- not call `FundDocumentRepository` internally;
- not call Docling;
- not call source helpers;
- not construct production `EvidenceAnchor`.

Only the later evidence wrapper may read accepted JSON artifacts and call
`FundDocumentRepository.load_annual_report(..., force_refresh=False)` under no-live/cache-only guard semantics. The pure helper must receive already constructed repository reference rows.

### 5.3 Required Data Model

Add candidate-internal dataclasses or typed dicts equivalent to:

| Model | Required fields |
| --- | --- |
| `ResidualClosureRule` | `field_name`, `expected_section_id`, `required_row_label_any`, `rejected_row_label_any`, `required_table_family_any`, `required_column_header_any`, `share_class_context`, `allow_semantic_equivalent_duplicate`, `semantic_guard`. |
| `ResidualClosureInputRow` | `sample_id`, `fact_id`, `fund_code`, `document_year`, `field_name`, `candidate_anchor`, `normalized_candidate`, `current_disposition`, `residual_reason`. |
| `ResidualClosureResultRow` | input row fields plus `closure_disposition`, `closure_reason`, `source_layer_status`, `processed_layer_status`, `fund_layer_status`, `matched_row_label_path`, `matched_column_header_path`, `matched_table_context`, `candidate_only=true`, `source_truth_status`. |
| `SourceTruthResidualClosureMatrix` | `schema_version`, `input_artifacts`, `summary`, `rows`, non-proof guard flags. |

### 5.4 Repository Reference Row Contract

The implementation must define a repository-mediated reference schema before applying fund semantic rules. The pure helper may not infer source rows from `source_excerpt_samples` alone.

Required reference models:

| Model | Required fields |
| --- | --- |
| `RepositoryReferenceCell` | `fund_code`, `document_year`, `repository_source_name`, `source_mode`, `fallback_used`, `section_id`, `page_number`, `table_id`, `row_index`, `column_index`, `row_label_path`, `column_header_path`, `raw_text`, `normalized_text`, `table_context`, `reference_origin`. |
| `RepositoryReferenceTextSpan` | `fund_code`, `document_year`, `repository_source_name`, `source_mode`, `fallback_used`, `section_id`, `page_number`, `raw_text`, `normalized_text`, `context_label`, `reference_origin`. |
| `RepositoryReferenceBundle` | `sample_id`, `fund_code`, `document_year`, `metadata_ok`, `metadata_reason`, `cells`, `text_spans`, `reference_generation_status`. |

`reference_origin` allowed values:

| Value | Meaning |
| --- | --- |
| `fund_document_repository_parsed_table` | Derived from `ParsedAnnualReport.tables` returned by `FundDocumentRepository`. |
| `fund_document_repository_section_text` | Derived from `ParsedAnnualReport.get_section_text(...)` or equivalent parsed section text. |

Rules:

- `repository_source_name` must come from repository source metadata such as `eid`; it is not `EvidenceAnchor.source_kind`.
- Annual-report semantic anchor candidates still use `EvidenceAnchor.source_kind = annual_report`.
- Reference rows must preserve `row_label_path` and `column_header_path` when table structure provides them; if unavailable, the row may not close a table-field residual.
- If a reference bundle cannot be built without live fetch, direct PDF/cache body read or source-helper body read, the sample/row must be `blocked_reference_unavailable`.
- Previous `source_excerpt_samples` may be copied into diagnostic evidence, but they are not sufficient as closure input.

### 5.5 Repository Reference Builder

The no-live evidence wrapper may include a narrow builder that converts repository parsed output into `RepositoryReferenceBundle`.

Allowed builder behavior:

- call `FundDocumentRepository.load_annual_report(fund_code, year, force_refresh=False)` under the same cache-only/no-live guard semantics accepted by the upstream source-truth evidence;
- read only the returned `ParsedAnnualReport` object and its metadata;
- project parsed tables and section text into the reference models above;
- fail closed if metadata is missing, fallback-origin, non-EID for current accepted samples, or if repository attempts live acquisition.

Not allowed:

- direct file reads from PDF/cache paths;
- source adapter/helper calls;
- weakening metadata checks to make rows close;
- hiding reference-building failure inside a generic residual.

The implementation gate may unit-test the pure helper without repository access. The evidence gate must validate reference-bundle generation or mark rows `blocked_reference_unavailable`.

### 5.6 Required Dispositions

Allowed output dispositions:

| Disposition | Meaning |
| --- | --- |
| `disambiguated_source_body_match` | Source body contains the normalized value and processed/fund locator rules identify the intended row/cell. |
| `semantic_equivalent_duplicate_residual` | Value is source-present but multiple same-value rows are semantically equivalent or unresolved under current rule. |
| `source_body_mismatch` | Same-source repository body still has no normalized match under accepted scope. |
| `semantic_assignment_residual` | Source text may exist, but field semantics are not proven. |
| `blocked_locator_unavailable` | Candidate row lacks required table/row/column locator context. |
| `blocked_reference_unavailable` | No no-live repository-mediated reference is available. |
| `blocked_rule_missing` | No explicit fund-layer rule exists for the field. |
| `blocked_candidate_metadata_violation` | Candidate-only or source/processor/EvidenceAnchor boundary guard fails. |

Do not invent a generic `pass` status. Every row must say what proof level or residual class it reached.

### 5.7 Field Rules

Implement these initial field rules as data/config within the helper, not scattered conditional literals:

| Field family | Rule |
| --- | --- |
| identity `fund_name` | §2, row label contains `基金名称`; reject unlabeled repeated names, headers, footers and linked-fund references. |
| identity `fund_code` | §2, row label contains `基金主代码`; reject `交易代码` and `下属分级基金的交易代码`. |
| identity `manager` | §2, row label contains `基金管理人` or `基金管理人名称`. |
| identity `custodian` | §2, row label contains `基金托管人` or `基金托管人名称`. |
| portfolio `fixed_income_investment_amount` | §8, table context must be portfolio composition; row label contains `固定收益投资`; reject fair-value hierarchy and totals. |
| portfolio `equity_investment_amount` | §8, table context must be portfolio composition; row label contains `权益投资`; reject child stock/common-stock/country rows. |
| portfolio `stock_investment_amount` | §8, table context must be portfolio composition; row label contains `其中：股票` or equivalent stock child row; reject parent `权益投资`. |
| manager alignment `manager_holding_range_A` | §10, manager-holding table; row label contains manager-holding phrase; column/share-class context must identify A share. |
| expense `sales_service_fee_C_current_year` | §7, sales-service-fee table; column context must identify C share and current period; unresolved duplicate rows remain explicit residual. |
| product `investment_objective` | §2, row label or source context must be `投资目标`; if same-source text absent, keep mismatch. |
| product `benchmark` | §2, row label or source context must be `业绩比较基准`; investment-objective context is explicitly rejected. |

### 5.8 Source / Processed / Fund Status Rules

Each output row must independently record:

| Status field | Valid values |
| --- | --- |
| `source_layer_status` | `same_source_reference_loaded`, `same_source_text_absent`, `blocked_reference_unavailable`, `metadata_violation` |
| `processed_layer_status` | `locator_context_available`, `locator_context_insufficient`, `locator_context_conflict`, `candidate_metadata_violation` |
| `fund_layer_status` | `semantic_rule_satisfied`, `semantic_rule_unresolved`, `semantic_rule_rejected`, `semantic_rule_missing` |

Closure requires all three:

```text
source_layer_status == same_source_reference_loaded
processed_layer_status == locator_context_available
fund_layer_status == semantic_rule_satisfied
```

Any other combination must remain residual or blocked.

### 5.9 Guard Fields

The output matrix must include and tests must assert:

```json
{
  "not_baseline_promotion": true,
  "not_parser_replacement": true,
  "not_release_readiness": true,
  "not_full_field_correctness": true,
  "not_raw_pdf_bbox_truth": true,
  "candidate_only": true
}
```

## 6. Tests

Required unit tests:

| Test | Assertion |
| --- | --- |
| identity code disambiguation | `fund_code` closes only on `基金主代码`, not `交易代码` or share-class trading-code rows. |
| identity name disambiguation | `fund_name` closes only on labeled §2 profile row. |
| manager/custodian disambiguation | manager/custodian close on labeled §2 rows and reject unlabeled duplicate occurrences. |
| portfolio parent/child split | `equity_investment_amount` and `stock_investment_amount` with the same numeric value resolve to different rows by row label. |
| fixed-income hierarchy rejection | `fixed_income_investment_amount` rejects fair-value hierarchy rows and accepts portfolio row. |
| benchmark semantic guard | `benchmark` remains `semantic_assignment_residual` when candidate context is investment objective. |
| investment-objective mismatch | no same-source normalized text keeps `source_body_mismatch`. |
| unresolved duplicate | expense duplicate rows with insufficient context produce `semantic_equivalent_duplicate_residual`, not forced closure. |
| boundary fields | repository source, processor profile and `EvidenceAnchor.source_kind` are not conflated. |
| guard flags | output matrix preserves all non-proof guard flags. |
| pure helper boundary | pure closure helper does not call `FundDocumentRepository`, read files, call Docling or call source helpers. |
| missing reference bundle | missing repository reference rows produce `blocked_reference_unavailable`. |

Required validation commands for implementation gate:

```bash
uv run pytest tests/fund/documents/test_docling_source_truth_residual_closure.py
python -m json.tool reports/docling-baseline-support-source-truth-residual-closure/20260616/residual_closure_matrix.json >/dev/null
git diff --check
```

If implementation does not yet generate the evidence matrix, omit the JSON validation from the implementation gate and require it in the evidence gate.

## 7. Evidence Slice

After implementation review acceptance, run a no-live evidence gate that writes:

```text
docs/reviews/docling-source-truth-residual-closure-evidence-20260616.md
reports/docling-baseline-support-source-truth-residual-closure/20260616/residual_closure_matrix.json
```

Evidence worker requirements:

- read only accepted artifact JSONs and repository-mediated parsed references;
- use cache-only/no-live repository guard semantics;
- build `RepositoryReferenceBundle` from `ParsedAnnualReport` metadata/tables/section text, not from previous diagnostic excerpts alone;
- include all 17 residual rows;
- include `input_artifacts` with paths and SHA-256 hashes;
- include per-row `source_layer_status`, `processed_layer_status`, `fund_layer_status`, `closure_disposition`, `closure_reason`;
- include summary counts by disposition and by sample;
- preserve all non-proof guard fields.

Expected evidence verdict format:

```text
VERDICT: SOURCE_TRUTH_RESIDUAL_CLOSURE_EVIDENCE_PARTIAL_NOT_READY
```

If all non-semantic rows close but `S6-F041` remains semantic residual, that is a valid partial result and still `NOT_READY`.

## 8. Review Requirements

Plan/code/evidence review must challenge:

- whether any row is closed by value equality alone;
- whether candidate parser route identity is confused with repository source identity or `EvidenceAnchor.source_kind`;
- whether `S6-F041 / benchmark` was closed without benchmark-labeled context;
- whether `S5-F023 / investment_objective` was closed without same-source repository body proof;
- whether direct PDF/cache/source-helper body access occurred;
- whether the helper became public production API or changed `FundDocumentRepository`;
- whether tests cover the same-value parent/child portfolio collision.

## 9. Stop Conditions

Stop and return to controller if:

- no no-live repository-mediated reference is available for a sample;
- implementation needs to read direct PDF/cache/source-helper bodies;
- implementation needs to modify production repository/parser/`EvidenceAnchor` schema;
- any field rule cannot be expressed without a new fund-domain semantic decision;
- evidence would require live/network/Docling conversion;
- a reviewer finds a closure row supported only by parser agreement.

## 10. Completion Report Format

Implementation/evidence closeout must report:

```text
Rows in scope: 17
Closed by disambiguated source-body proof: <n>
Still residual/blocker: <n>
S5-F023 disposition: <status>
S6-F041 disposition: <status>
Validation: <commands and result>
Readiness: NOT_READY
```

## 11. Next Gate If Accepted

```text
Docling Source-truth Residual Closure No-live Implementation Gate
```

## 12. Verdict

```text
VERDICT: DOCLING_SOURCE_TRUTH_RESIDUAL_CLOSURE_PLAN_READY_FOR_REVIEW_NOT_READY
```
