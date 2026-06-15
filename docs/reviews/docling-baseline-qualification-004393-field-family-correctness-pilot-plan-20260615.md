# 004393 Field-family Correctness Pilot Planning Gate - 2026-06-15

Gate: `004393 Field-family Correctness Pilot Planning Gate`
Role: planning worker
Release/readiness: `NOT_READY`

## 1. Goal

Plan a bounded field-family correctness pilot for the user-designated fund:

- fund code: `004393`
- fund name: 安信企业价值优选混合A
- report year: `2025`

The pilot should determine whether current-envelope Docling candidate extraction can be trusted for selected field families before any production integration or parser replacement discussion.

## 2. Current Accepted Preconditions

Accepted checkpoints:

- `ff64968 gateflow: accept docling baseline candidate decision`
- `1e055fa gateflow: accept 004393 current envelope refresh`
- `9286511 gateflow: accept 004393 locator stability evidence`

Accepted current-envelope artifacts:

- `reports/representation-json/004393_2025_docling_current_envelope.json`
- `reports/representation-json/004393_2025_pdfplumber_current_envelope.json`
- `reports/representation-json/004393_2025_eid_html_render_blocked_current_envelope.json`

Accepted locator facts:

- Docling: 25 sections, 95 tables, 3,493 cells, 100% page/bbox/row-column locator coverage, 524 header-flag cells.
- pdfplumber: 8 sections, 92 tables, 3,640 cells, 100% page/row-column locator coverage, 94.1% bbox locator coverage, no header flags.
- EID HTML: blocked current-envelope for this sample.

## 3. Non-goals

This plan does not authorize:

- field correctness evidence execution;
- live/network/EID/provider/LLM/analyze/checklist/readiness/release/PR commands;
- production `FundDocumentRepository` behavior changes;
- source policy changes;
- parser replacement;
- public `EvidenceAnchor` schema changes;
- Service/Host/UI/renderer/quality gate consumption of candidate internals;
- EID HTML table-bearing mapping;
- cleanup/archive/delete of legacy artifacts.

## 4. Correctness Principle

Correctness must be judged against the same annual-report source, not against another parser route.

Allowed evidence in the future evidence gate:

- candidate current-envelope cells and locators;
- original annual-report source accessed through `FundDocumentRepository`;
- bounded PDF page/table excerpts or screenshots derived from the repository-loaded annual report;
- manually reviewed reference fact rows recorded in an evidence artifact.

Not allowed as correctness proof:

- Docling and pdfplumber agreeing with each other;
- current-envelope locator coverage alone;
- EID HTML route-specific JSON;
- legacy Route A JSON;
- inferred field values without same-source page/table evidence;
- NAV/database values for annual-report table correctness unless the field family explicitly targets NAV cross-checking and the plan says so.

## 5. Pilot Field Families

Choose small field families that cover the template-critical surface without becoming a full report audit.

| Family | Template relevance | Candidate source tables | Pilot fields | Why included |
| --- | --- | --- | --- | --- |
| `fund_identity_profile` | Chapter 0/1 product identity | Docling `#/tables/2`, pdfplumber `page:5:table:0` | fund name, fund short name, fund code, operation mode, contract effective date, manager, custodian, ending share total | Low ambiguity; tests key-value table extraction and identity safety. |
| `product_contract_profile` | Chapter 1 product nature | Docling `#/tables/3`, pdfplumber `page:5:table:1` | investment objective, investment strategy, benchmark, risk-return characteristic | Tests long text cells and product classification inputs. |
| `performance_indicators` | Chapter 2 R=A+B-C / Chapter 4 investor experience | Docling `#/tables/8`, `#/tables/9`, `#/tables/10`; pdfplumber `page:7:table:0`, `page:8:table:0` | A/C class period profit or NAV-growth rows; benchmark return; alpha columns `①-③` where present | Tests multi-column performance tables. |
| `expense_costs` | Chapter 2 cost C | Docling tables containing management fee / custodian fee / sales service fee; pdfplumber counterparts when locatable | management fee, custodian fee, sales service fee current-year values | Tests fee/cost extraction; central to R=A+B-C. |
| `portfolio_structure` | Chapter 3/5/6 holdings and risk | Docling tables around industry allocation and asset allocation; pdfplumber counterparts when locatable | top industry/asset allocation rows, stock/bond/cash exposure where present | Tests portfolio tables relevant to style/risk. |
| `manager_alignment` | Chapter 3 manager portrait | Docling `#/tables/14`, `#/tables/86`; pdfplumber counterparts when locatable | fund manager name/tenure, manager holding range | Tests manager facts and holding alignment; small but decision-relevant. |

## 6. Pilot Size

Target maximum:

- 6 field families;
- 3-5 facts per family;
- maximum 25 reviewed facts total;
- at least 15 facts must come from Docling candidate cells;
- pdfplumber is comparator for the same fact only when the corresponding candidate locator exists;
- EID HTML remains blocked and is not part of correctness comparison.

Stop if a family needs more than 5 facts to decide basic correctness pattern. That family should be split into a later dedicated gate.

## 7. Reference Fact Schema

Future evidence artifact should record each reviewed fact as:

```text
fact_id
family
field_name
expected_value_from_same_source_review
candidate_route
candidate_value
candidate_table_id
candidate_page_number
candidate_row_index
candidate_column_index
candidate_bbox_or_null
candidate_cell_hash_or_null
reference_source
reference_page_number
reference_table_or_section_label
reference_row_label
reference_column_label
match_status
mismatch_type
review_note
reference_excerpt
candidate_excerpt
```

Allowed `match_status`:

- `exact_match`
- `normalized_match`
- `partial_match`
- `mismatch`
- `not_reviewable`

Allowed `mismatch_type`:

- `none`
- `missing_cell`
- `wrong_cell`
- `merged_cell_loss`
- `header_mapping_loss`
- `numeric_format_loss`
- `text_wrap_loss`
- `page_locator_loss`
- `source_review_unavailable`

## 8. Evidence Workflow

Future evidence gate should execute:

1. Load accepted 004393 current-envelope JSON.
2. Select candidate cells for the planned field facts.
3. Load the 004393 annual report through `FundDocumentRepository`, not by direct ad hoc PDF filesystem access.
4. Produce bounded same-source reference excerpts for the relevant pages/tables only.
5. Manually or deterministically review each fact against the same-source excerpt.
6. Record match status and mismatch type.
7. Summarize by family and route.
8. Decide whether Docling is:
   - `field_family_correctness_pilot_pass_candidate`
   - `field_family_correctness_pilot_partial_candidate`
   - `field_family_correctness_pilot_fail_candidate`
   - `blocked_needs_reference_evidence`

## 9. Acceptance Thresholds

This pilot can only support future planning, not production readiness.

Suggested evidence thresholds:

- `fund_identity_profile`: all selected facts must be `exact_match` or `normalized_match`.
- `product_contract_profile`: all selected short labels must match; long text cells may be `partial_match` only if the reference excerpt confirms the same semantic sentence was captured without contradicting text.
- Any long-text `partial_match` must include both `reference_excerpt` and `candidate_excerpt` with the smallest useful surrounding text span; broad semantic paraphrase is not acceptable.
- `performance_indicators`: selected numeric values must be exact after whitespace/thousand-separator/line-wrap normalization.
- `expense_costs`: selected numeric values must be exact after numeric formatting normalization.
- `portfolio_structure`: selected row labels and percentages/amounts must be exact after formatting normalization.
- `manager_alignment`: name/tenure/holding range must be exact after whitespace normalization.

If any family fails, do not generalize failure to all Docling. Classify the route/family and recommend a narrower fix or mapping rule.

## 10. Validation Commands

Planning gate validation:

```text
git diff --check
```

Future evidence gate validation should include:

```text
uv run python - <<'PY'
# load accepted current-envelope JSON, project it, and verify all selected fact locators resolve
PY
```

If the future evidence gate uses repository-loaded PDF excerpts, it must also record the exact command and confirm:

- no live/network access unless separately authorized;
- no direct source/cache helper bypass from Service/UI/Host/renderer/quality gate;
- no production behavior change.

## 11. Review Focus

Reviewers should check:

- whether the field families are too broad for a pilot;
- whether correctness evidence is same-source and not parser-vs-parser agreement;
- whether `FundDocumentRepository` access boundary is preserved;
- whether thresholds are explicit enough to avoid subjective acceptance;
- whether EID HTML remains blocked/deferred;
- whether the plan avoids readiness, release, production, and parser replacement claims.

## 12. Stop Conditions

Stop before evidence execution if:

- the evidence worker cannot access the original annual report through `FundDocumentRepository`;
- selected fact locators do not resolve in current-envelope JSON;
- correctness review would require live/network/EID/provider/LLM access;
- evidence would need more than 25 facts or more than 5 facts per family;
- any field family requires new production code or parser behavior changes;
- reviewer/controller cannot distinguish reference facts from candidate facts.

## 13. Next Gate

Recommended next gate:

`004393 Field-family Correctness Pilot Plan Review Gate`

If accepted, next:

`004393 Field-family Correctness Pilot Evidence Gate`

The evidence gate must remain no-production and must preserve `NOT_READY`.
