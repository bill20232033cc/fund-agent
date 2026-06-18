# Docling Multi-sample Field-family Correctness Expansion Plan - 2026-06-15

Gate: `Docling Multi-sample Field-family Correctness Expansion Planning Gate`
Role: planning worker
Release/readiness: `NOT_READY`
Artifact status: plan only; no evidence executed

## 1. Goal / Motivation

Plan a handoff-ready evidence gate to test whether the accepted `004393 / 2025`
Docling candidate-layer bounded pilot can expand across multiple funds, multiple
report years and multiple field families.

The evidence gate must answer only this question:

> For existing accepted/local candidate representation artifacts, do selected
> Docling candidate facts match same-source annual-report references at the
> field-family level often enough to justify the next bounded design/evidence
> gate?

This plan does not claim source truth, production parser replacement, full field
correctness, taxonomy compatibility, raw XML availability, release readiness, or
PR readiness.

## 2. Accepted Inputs And Non-proof Boundaries

Accepted inputs:

- `docs/reviews/docling-baseline-qualification-review-provenance-remediation-controller-judgment-20260615.md`
  - `afebc92` remains accepted after remediated real tmux DS/MiMo review provenance.
  - Old non-tmux DS/MiMo review artifacts for the 004393 pilot are provenance-contaminated and must not be cited as true DS/MiMo reviews.
  - Next entry is `Docling Multi-sample Field-family Correctness Expansion Gate`.
- `docs/reviews/docling-baseline-qualification-004393-field-family-correctness-pilot-controller-judgment-20260615.md`
  - Accepted bounded fact: `004393 / 2025` selected Docling facts matched same-source repository-loaded PDF bbox crop excerpts in 21/21 reviewed facts: 19 exact + 2 normalized.
  - pdfplumber comparator mismatch is limited to 4 selected locator/crop checks.
  - EID HTML remains blocked/deferred for this sample.
  - Candidate `field_correctness_status` remains `not_proven`.
- `reports/representation-json/004393_field_family_correctness_pilot_reviewed_facts_20260615.json`
  - Existing reviewed-facts schema and accepted S1 fact set.
- `reports/representation-json/full-representation-export-manifest-20260615.json`
  - Existing full candidate representation inputs for S1/S4/S5/S6.

Non-proof boundaries:

- Existing representation JSON files are candidate inputs, not source truth.
- Existing local PDFs or cached paths are not proof unless the future evidence
  gate records repository-loaded annual-report identity and same-source reference
  derivation.
- Parser-vs-parser agreement is not correctness proof.
- pdfplumber can be used only as a comparator when its locator exists; pdfplumber
  mismatch or pass must not be generalized.
- EID HTML render is blocked/deferred unless a separate mapping gate accepts
  current-envelope render artifacts and same-source reference mapping.
- Untracked residue must not be used as proof.
- This plan does not authorize live acquisition, Docling conversion, PDF/FDR
  execution, provider/LLM route, analyze/checklist/golden/readiness/release/PR
  commands, source/test/runtime edits, or production integration.

## 3. Sample Matrix Design

Use only current accepted/local candidate artifacts. Do not require live
acquisition in this plan. Before evidence review, the future evidence worker
must establish a no-live same-source reference route for each sample: either an
accepted same-source reference artifact is available, or `FundDocumentRepository`
can provide repository metadata/reference access with explicit no-refresh/no-live
intent and `force_refresh=False`. If this cannot be proven from repository
metadata or an accepted same-source reference artifact, mark the sample
`blocked_reference_unavailable` with reason `no_no_live_reference_proof` and stop
before selecting or reviewing facts for that sample.

| Sample | Fund / year | Candidate inputs | Planned role | Evidence requirement | Status in this plan |
| --- | --- | --- | --- | --- | --- |
| S1 | `004393 / 2025` | `004393_2025_docling_full.json`, `004393_2025_pdfplumber_full.json`, prior reviewed-facts JSON | Accepted control sample and regression baseline | Reuse prior reviewed facts by hash; any new facts must repeat same-source repository-loaded reference method | Required |
| S4 | `006597 / 2024` | `006597_2024_docling_full.json`, `006597_2024_pdfplumber_full.json`; EID HTML blocked JSON | Cross-fund 2024 sample; use existing full candidate JSON only | Evidence worker must verify a no-live same-source reference route through an accepted same-source reference artifact or `FundDocumentRepository(force_refresh=False)` before correctness review | Required if no-live reference proof exists |
| S5 | `017641 / 2024` | `017641_2024_docling_full.json`, `017641_2024_pdfplumber_full.json`; EID HTML blocked JSON | Cross-fund 2024 sample with likely different disclosure shape | Same as S4 | Required if no-live reference proof exists |
| S6 | `110020 / 2024` | `110020_2024_docling_full.json`, `110020_2024_pdfplumber_full.json`; EID HTML blocked JSON | Cross-fund 2024 sample with index-style/product-profile pressure | Same as S4 | Required if no-live reference proof exists |

Rejected/deferred sample additions:

- `004194 / 2024`: has historical accepted/local evidence in other gate families,
  but no accepted Docling full candidate representation manifest entry in the
  current Docling expansion input set. Do not add it unless a separate
  candidate-artifact capture/export gate accepts its Docling/pdfplumber candidate
  artifacts.
- S2/S3 placeholders or provenance-questioned artifacts: do not use unless a
  separate provenance/disposition gate accepts them.
- Additional report years beyond 2024/2025: out of scope unless a separate
  no-live candidate-generation gate accepts local candidate artifacts or the
  controller explicitly authorizes a live acquisition gate.

Minimum matrix for an evidence verdict:

- `S1` plus at least two of `S4/S5/S6` must be reviewable.
- At least two report years must be represented by reviewable samples: current
  plan target is 2025 and 2024.
- If fewer than three samples are reviewable, verdict must be
  `BLOCKED_INSUFFICIENT_REVIEWABLE_SAMPLE_MATRIX_NOT_READY`.

## 4. Field-family Matrix

The evidence worker should select 3-5 Docling facts per applicable family per
new sample. S1 may reuse accepted facts and should not be expanded unless needed
to align the schema.

| Family | Purpose | Preferred fact shape | May be `not_applicable` when | Minimum per applicable sample |
| --- | --- | --- | --- | --- |
| `fund_identity_profile` | Fund identity, report identity and safety checks | fund name, fund short name, fund code, manager, custodian, operation mode, contract effective date | Only if the annual report/reference cannot expose an identity table; normally should not be N/A | 4 facts |
| `product_contract_profile` | Product nature for template Chapter 1 | investment objective, investment strategy, benchmark, risk-return characteristic | Product contract text is absent from annual report or disclosed only by prospectus/fund contract, not annual report | 3 facts if present |
| `performance_indicators` | Chapter 2/4 performance and benchmark table pressure | NAV growth, benchmark return, excess/alpha-like columns, class-specific rows | A share/class or comparable annual performance table is absent or not locatable in the annual report | 3 facts if present |
| `expense_costs` | Cost `C` surface | management fee, custodian fee, sales service fee, transaction/other fee rows where disclosed | Fee class does not apply or row is absent for the fund/share class; e.g. no sales service fee for A class | 2 facts if present |
| `portfolio_structure` | Portfolio allocation/style/risk surface | asset allocation, industry allocation, top holdings category, stock/bond/cash exposure | Disclosure table is genuinely absent or product type makes the specific row irrelevant; FOF/QDII variants may require adapted labels | 3 facts if present |
| `manager_alignment` | Manager tenure and interest-alignment surface | manager name, tenure start/period, manager holding range | Manager holding/tenure table is not disclosed, not applicable to the product type, or no individual manager alignment data exists | 2 facts if present |

`not_applicable` rules:

- `not_applicable` must be based on same-source annual-report review, not on
  candidate JSON absence alone.
- A family can be `not_applicable` for a sample only with a recorded
  `family_applicability_reason`.
- If the family is expected for the product type but locators cannot be found,
  use `blocked_locator_unresolved` or `not_reviewable`, not `not_applicable`.

## 5. Same-source Correctness Principle

Reference facts must come from one of:

1. The annual report loaded through `FundDocumentRepository` for the exact
   `(fund_code, document_year)` under review.
2. An accepted same-source reference artifact whose provenance states it was
   derived from that repository-loaded annual report.

Reference availability must be clarified before evidence review. The future
evidence worker must first prefer an accepted same-source reference artifact if
one exists for the exact `(fund_code, document_year, report_type)`. If no such
artifact exists, the worker may use only `FundDocumentRepository` with
no-refresh/no-live intent and `force_refresh=False`, and must rely on repository
metadata to prove the reference was available without live acquisition. The
worker must not call source helpers, cache internals, direct PDF paths,
`force_refresh=True`, or any operation that inspects or mutates source/cache
implementation details. If no-live availability cannot be proven from
repository metadata or an accepted same-source reference artifact, the sample
must be marked `blocked_reference_unavailable` with reason
`no_no_live_reference_proof`.

Correctness must not be inferred from:

- Docling vs pdfplumber agreement;
- Docling vs EID HTML agreement;
- current-envelope locator coverage alone;
- local candidate JSON existence alone;
- external NAV/API/database values;
- manual memory of fund facts;
- untracked PDFs or unreviewed local residue.

For each fact, the evidence artifact must identify both the candidate cell and
the same-source reference span. For ambiguous table cells, the evidence worker
must include the smallest useful reference excerpt or visual/crop note needed to
explain the match.

## 6. Route Comparison Scope

Primary route:

- `docling_pdf_candidate`.
- Evidence verdict thresholds apply to Docling facts only.

Comparator route:

- `pdfplumber_pdf_candidate`, only when a corresponding locator exists and the
  comparator can be tied to the same fact.
- Comparator results are diagnostic. They can help classify whether Docling
  improves locator stability, but they do not prove correctness by agreement and
  do not disprove pdfplumber generally by mismatch.

Blocked/deferred route:

- `eid_xbrl_html_render_candidate`.
- Current expansion gate must keep EID HTML blocked/deferred. Do not attempt
  HTML current-envelope mapping, raw XML lookup, taxonomy compatibility proof,
  or HTML-vs-PDF field correctness unless a separate mapping/evidence gate is
  accepted.

## 7. Reviewed-facts Evidence Artifact Schema

Future evidence gate must write one durable JSON artifact plus one Markdown
evidence summary. Suggested output path:

```text
reports/representation-json/docling_multi_sample_field_family_correctness_reviewed_facts_20260615.json
docs/reviews/docling-baseline-qualification-multi-sample-field-family-correctness-expansion-evidence-20260615.md
```

JSON top-level schema:

```json
{
  "schema_version": "docling_multi_sample_field_family_correctness.v1",
  "gate": "Docling Multi-sample Field-family Correctness Expansion Evidence Gate",
  "created_at": "YYYY-MM-DDTHH:MM:SSZ",
  "not_source_truth": true,
  "not_production_parser_replacement": true,
  "not_full_field_correctness": true,
  "not_readiness_proof": true,
  "candidate_field_correctness_status_remains": "not_proven",
  "input_artifacts": [],
  "samples": [],
  "facts": [],
  "family_results": [],
  "sample_results": [],
  "route_results": [],
  "stop_conditions_triggered": []
}
```

`input_artifacts[]` item schema:

```json
{
  "artifact_path": "reports/representation-json/006597_2024_docling_full.json",
  "route": "docling_pdf_candidate",
  "fund_code": "006597",
  "document_year": 2024,
  "sample_id": "S4",
  "sha256": "<computed hash>",
  "accepted_manifest_path": "reports/representation-json/full-representation-export-manifest-20260615.json",
  "provenance_judgment_path": "<accepted controller judgment path or null>",
  "artifact_role": "candidate_input"
}
```

`samples[]` item schema:

```json
{
  "sample_id": "S4",
  "fund_code": "006597",
  "fund_name_or_null": null,
  "document_year": 2024,
  "report_type": "annual_report",
  "sample_role": "expansion_sample",
  "repository_load": {
    "attempted": true,
    "status": "loaded | blocked_reference_unavailable | not_attempted",
    "metadata_source": "eid",
    "source_mode": "single_source_only",
    "fallback_enabled": false,
    "fallback_used": false,
    "no_live_reference_proof": "accepted_same_source_reference_artifact | repository_metadata_no_refresh | null",
    "reference_blocker_reason_or_null": "no_no_live_reference_proof | null",
    "parsed_cache_hit_or_null": null,
    "raw_text_len_or_null": null,
    "section_count_or_null": null,
    "table_count_or_null": null,
    "blocker_or_null": null
  },
  "candidate_routes_present": ["docling_pdf_candidate", "pdfplumber_pdf_candidate"],
  "eid_html_status": "blocked_deferred",
  "sample_review_status": "reviewed | partial | blocked",
  "sample_result": "pass | partial | fail | blocked"
}
```

`facts[]` item schema:

```json
{
  "fact_id": "S4-F001",
  "sample_id": "S4",
  "fund_code": "006597",
  "document_year": 2024,
  "family": "fund_identity_profile",
  "field_name": "fund_name",
  "field_applicability": "applicable | not_applicable | blocked_locator_unresolved | blocked_reference_unavailable",
  "family_applicability_reason": "same-source annual report identity table present",
  "candidate_route": "docling_pdf_candidate",
  "candidate_artifact": "reports/representation-json/006597_2024_docling_full.json",
  "candidate_value": "...",
  "candidate_table_id": "...",
  "candidate_page_number": 5,
  "candidate_row_index": 0,
  "candidate_column_index": 1,
  "candidate_bbox_or_null": {},
  "candidate_cell_hash_or_null": "...",
  "candidate_locator_status": "resolved | missing | ambiguous",
  "reference_source": "repository_loaded_annual_report | accepted_same_source_reference_artifact",
  "reference_artifact_or_null": null,
  "reference_document_metadata_or_null": {},
  "reference_page_number": 5,
  "reference_table_or_section_label": "...",
  "reference_row_label_or_null": "...",
  "reference_column_label_or_null": "...",
  "reference_excerpt": "...",
  "candidate_excerpt": "...",
  "normalization_applied": ["strip_whitespace"],
  "match_status": "exact_match | normalized_match | partial_match | mismatch | not_reviewable | not_applicable",
  "mismatch_type": "none | missing_cell | wrong_cell | merged_cell_loss | header_mapping_loss | numeric_format_loss | text_wrap_loss | page_locator_loss | source_review_unavailable | not_applicable",
  "normalized_equal": true,
  "review_note": "..."
}
```

`family_results[]` item schema:

```json
{
  "sample_id": "S4",
  "family": "performance_indicators",
  "applicability": "applicable | not_applicable | blocked",
  "docling_fact_count": 3,
  "docling_exact_or_normalized_count": 3,
  "docling_partial_count": 0,
  "docling_mismatch_count": 0,
  "pdfplumber_comparator_count": 2,
  "family_result": "pass | partial | fail | not_applicable | blocked",
  "reason": "..."
}
```

`sample_results[]` item schema:

```json
{
  "sample_id": "S4",
  "reviewable_family_count": 5,
  "passed_family_count": 5,
  "partial_family_count": 0,
  "failed_family_count": 0,
  "blocked_family_count": 0,
  "not_applicable_family_count": 1,
  "sample_result": "pass | partial | fail | blocked",
  "reason": "..."
}
```

`route_results[]` item schema:

```json
{
  "route": "docling_pdf_candidate",
  "reviewed_fact_count": 60,
  "exact_or_normalized_count": 58,
  "partial_count": 1,
  "mismatch_count": 1,
  "route_result": "candidate_pass | candidate_partial | candidate_fail | blocked",
  "boundary": "candidate-only; not source truth"
}
```

The evidence worker may add fields only if they are additive, documented in the
Markdown summary and do not weaken the required fields above.

## 8. Acceptance Thresholds

Family-level Docling thresholds:

- `fund_identity_profile`: all reviewed applicable Docling facts must be
  `exact_match` or `normalized_match`; no `partial_match`.
- `product_contract_profile`: short labels must be exact/normalized; long text
  may be `partial_match` only when the reference excerpt confirms the same
  clause without omitted contradicting text.
- `performance_indicators`: all selected numeric values must be exact after
  whitespace, line-break, percent-sign and thousand-separator normalization.
- `expense_costs`: all selected numeric/rate values must be exact after numeric
  formatting normalization; missing non-applicable fee rows may be
  `not_applicable` only with same-source reason.
- `portfolio_structure`: row labels and percentages/amounts must be exact or
  normalized; wrong row or wrong column is fail.
- `manager_alignment`: manager names, tenure dates/periods and holding ranges
  must be exact or normalized; missing disclosure may be `not_applicable` only
  with same-source reason.

Per-family verdict:

- `pass`: all applicable Docling facts meet the family threshold.
- `partial`: only allowed for `product_contract_profile` long text when every
  partial fact has bounded excerpts and no contradiction; otherwise use `fail`.
- `fail`: any applicable field has mismatch, wrong row/column or unaccepted
  partial match.
- `not_applicable`: same-source reference confirms the family is not applicable
  or not disclosed for the product/sample.
- `blocked`: reference or locator cannot be reviewed without new unauthorized
  acquisition, source access or production changes.

Per-sample threshold:

- `pass`: at least 4 applicable families are reviewed and all applicable family
  results are `pass` or accepted `not_applicable`; no family `fail`; no more than
  1 family `blocked`.
- `partial`: at least 3 applicable families are reviewed, no more than 1 family
  `fail`, and every fail has a precise mismatch category.
- `fail`: 2 or more applicable families fail, or `fund_identity_profile` fails.
- `blocked`: repository-loaded same-source reference is unavailable, or fewer
  than 3 applicable families are reviewable.

Overall expansion threshold:

- `candidate_expansion_pass_not_ready`: S1 remains accepted by hash, at least 2
  of S4/S5/S6 are `pass`, and no reviewed expansion sample has
  `fund_identity_profile` fail.
- `candidate_expansion_partial_not_ready`: S1 remains accepted by hash, at least
  2 of S4/S5/S6 are reviewable, and failures are isolated to named families.
- `candidate_expansion_fail_not_ready`: S1 remains accepted but 2 or more
  expansion samples fail or identity safety fails.
- `blocked_not_ready`: sample/reference matrix is insufficient, unauthorized
  live access would be needed, or evidence schema cannot distinguish candidate
  facts from same-source references.

All verdicts preserve `NOT_READY`.

## 9. Evidence Workflow For The Future Evidence Gate

1. Verify the plan artifact and accepted input artifact paths exist.
2. Load `reports/representation-json/full-representation-export-manifest-20260615.json`.
3. Verify each candidate JSON path listed in the manifest for S1/S4/S5/S6 exists
   before selecting facts. If any required candidate JSON path is missing, mark
   the affected sample `blocked_missing_candidate_input` and stop fact selection
   for that sample.
4. Compute SHA-256 hashes for all existing candidate JSON inputs used by
   S1/S4/S5/S6 and compare them to accepted manifest expectations before fact
   selection. If any hash cannot be computed or mismatches the accepted manifest,
   mark the affected sample `blocked_candidate_hash_mismatch` and stop fact
   selection for that sample.
5. For S1, verify the prior reviewed-facts JSON hash matches the accepted
   controller judgment before reusing it.
6. Clarify no-live same-source reference availability for each sample before
   fact selection. Use an accepted same-source reference artifact if available;
   otherwise use only `FundDocumentRepository` with no-refresh/no-live intent and
   `force_refresh=False`. Do not call source helpers, cache internals, direct PDF
   paths, `force_refresh=True`, live/EID acquisition, or any source/cache
   implementation detail. If no-live availability cannot be proven from
   repository metadata or an accepted same-source reference artifact, mark the
   sample `blocked_reference_unavailable` with reason
   `no_no_live_reference_proof` and stop fact selection for that sample.
7. For S4/S5/S6, select 3-5 Docling facts per applicable family from existing
   full candidate JSONs only after candidate existence/hash verification and
   reference availability proof have passed for that sample.
8. Resolve pdfplumber comparator locators only for selected facts where a
   corresponding locator exists.
9. Load or identify the exact same-source annual-report reference through the
   approved no-live route established above. Repository access must remain inside
   `FundDocumentRepository` and must use `force_refresh=False`.
10. Derive bounded same-source reference excerpts or accepted same-source
   reference artifact rows for each selected fact.
11. Compare candidate values to references and classify match status/mismatch
   type.
12. Write the JSON reviewed-facts artifact and Markdown evidence summary.
13. Run validation commands listed in this plan.
14. Stop for DS/MiMo review and controller judgment; do not proceed to
    implementation.

## 10. Stop Conditions

Stop before or during evidence execution if:

- any action would require live/network/EID acquisition without a separately
  accepted live gate;
- no-live same-source reference availability cannot be proven from repository
  metadata or an accepted same-source reference artifact; in that case mark the
  sample `blocked_reference_unavailable` with reason
  `no_no_live_reference_proof` and stop before fact selection/review;
- the evidence worker cannot load same-source references through
  `FundDocumentRepository` or an accepted same-source reference artifact;
- reference proof would require source helpers, cache internals, direct PDF
  paths, `force_refresh=True`, or source/cache implementation inspection;
- selected Docling locators cannot be resolved without changing source/runtime
  code;
- any required candidate JSON path for the affected sample is missing before
  fact selection; mark the sample `blocked_missing_candidate_input`;
- candidate JSON provenance is ambiguous, hash cannot be computed, or hash
  mismatches accepted manifest expectations; mark the sample
  `blocked_candidate_hash_mismatch`;
- a sample's fund identity in candidate facts conflicts with repository-loaded
  annual-report identity;
- EID HTML mapping is needed to make the matrix pass;
- evidence would need source/test/runtime changes, `EvidenceAnchor` schema
  changes, Service/Host/UI/renderer/quality gate changes, LLM/provider route, or
  golden/readiness/release commands;
- fact review grows beyond 5 facts per family per sample or beyond 90 total
  reviewed Docling facts for S1/S4/S5/S6.

## 11. Validation Commands For Future Evidence Gate

Planning gate validation for this artifact only:

```text
git diff --check
```

Future evidence gate validation should include only no-live/local checks unless
the controller separately authorizes live access:

```text
git diff --check
jq '.schema_version, (.samples | length), (.facts | length), (.sample_results | length)' reports/representation-json/docling_multi_sample_field_family_correctness_reviewed_facts_20260615.json
jq -e '.not_source_truth == true and .not_production_parser_replacement == true and .not_full_field_correctness == true and .not_readiness_proof == true' reports/representation-json/docling_multi_sample_field_family_correctness_reviewed_facts_20260615.json
jq -e 'all(.facts[]; has("sample_id") and has("family") and has("candidate_route") and has("reference_source") and has("match_status") and has("mismatch_type"))' reports/representation-json/docling_multi_sample_field_family_correctness_reviewed_facts_20260615.json
jq -e 'all(.samples[]; .eid_html_status == "blocked_deferred")' reports/representation-json/docling_multi_sample_field_family_correctness_reviewed_facts_20260615.json
```

If the evidence worker uses a Python helper to validate locator resolution, it
must be no-live/local and must record exact command text, input paths, output
path and observed summary. It must not run Docling conversion, EID acquisition,
FDR live refresh, provider/LLM, analyze/checklist, golden, readiness, release,
push or PR commands.

## 12. Review Focus For DS / MiMo

DS review focus:

- Same-source correctness principle is enforceable and not parser-vs-parser
  agreement.
- Schema distinguishes candidate facts, repository-loaded references, accepted
  same-source reference artifacts and comparator diagnostics.
- Sample matrix is sufficient for bounded multi-fund/multi-year expansion but
  does not smuggle in live acquisition.
- Per-family and per-sample thresholds produce deterministic verdicts.
- `not_applicable` cannot hide missing locator/reference failures.

MiMo review focus:

- Boundary language preserves `NOT_READY`, candidate-only status,
  `field_correctness_status=not_proven`, no source truth, no full correctness
  and no parser replacement.
- S4/S5/S6 use existing accepted/local candidate artifacts only and do not use
  untracked residue as proof.
- EID HTML remains blocked/deferred; raw XML/taxonomy claims are absent.
- Evidence gate cannot mutate `FundDocumentRepository`, parser, source policy,
  `EvidenceAnchor`, Service/Host/UI/renderer/quality gate, LLM route, tests or
  runtime.
- Acceptance thresholds do not overgeneralize S1 or pdfplumber comparator
  outcomes.

## 13. Next Gates

Required next gates after this plan:

1. `Docling Multi-sample Field-family Correctness Expansion Plan Review Gate`
   - DS/MiMo review of this plan.
   - Controller judgment must decide amendments before evidence execution.
2. `Docling Multi-sample Field-family Correctness Expansion Evidence Gate`
   - Evidence worker executes only the accepted reviewed plan.
   - No production implementation.
3. `Docling Multi-sample Field-family Correctness Expansion Disposition Gate`
   - Controller classifies result as candidate expansion pass/partial/fail/blocked.
   - Decide whether to proceed to a later design/schema/integration planning
     gate, defer family-specific fixes, or stop.

No production implementation, parser replacement, repository behavior change,
source policy change, readiness/release/PR state change, or LLM/provider route
may follow directly from this plan.

## 14. Completion Report Format For Evidence Worker

The future evidence worker should report:

```text
Artifact:
- JSON reviewed facts: <path>
- Markdown evidence: <path>

Verdict:
- <candidate_expansion_pass_not_ready | candidate_expansion_partial_not_ready | candidate_expansion_fail_not_ready | blocked_not_ready>

Matrix:
- Samples reviewed / blocked:
- Families passed / partial / failed / not_applicable / blocked:
- Docling reviewed fact count:
- pdfplumber comparator fact count:

Validation:
- <command>: <PASS/FAIL with observed summary>

Residuals:
- <classified residuals and next owner/gate>

Self-check: pass
```
