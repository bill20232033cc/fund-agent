# Docling Baseline Support Source-truth Evidence Plan - 2026-06-16

Gate: `Docling Baseline Support Source-truth Evidence Planning Gate`
Role: planning worker
Gate classification: `heavy`
Release/readiness: `NOT_READY`

## 1. Goal

Plan the next evidence gate required for Docling to support a future baseline disposition.

The immediate goal is not to promote Docling. The immediate goal is to prove, through the production annual-report access boundary, whether selected Docling candidate anchors correspond to repository-loaded annual-report source body.

Accepted latest local checkpoint:

```text
8fe3dd9 gateflow: accept docling anchor coverage implementation
```

Accepted bounded fact from that checkpoint:

```text
candidate anchor coverage: 44 / 72 -> 72 / 72
prior missing anchors recovered: 28 / 28
S5 positive control preserved: 17 / 17
source_truth_status: not_proven
candidate_field_correctness_status: not_proven
```

## 2. Baseline Support Gate Sequence

Docling can support baseline consideration only after these gates pass in order:

| Order | Gate | Purpose | Promotion allowed? |
| ---: | --- | --- | --- |
| 1 | Source-truth evidence gate | Compare selected Docling candidate anchors against annual-report source body obtained through `FundDocumentRepository` only. | No |
| 2 | Full field-correctness evidence gate | Expand from selected reviewed facts to field-family and chapter-contract correctness, including currently residual semantic cases. | No |
| 3 | Baseline qualification gate | Compare Docling against current production baseline for correctness, provenance, failure modes, cost/cache/runtime, and rollback behavior. | No |
| 4 | Production integration design gate | Decide whether Docling is shadow baseline, candidate reference baseline, partial parser component, or production replacement. | Plan only |
| 5 | Production integration implementation gate | Implement accepted integration decision with public contract tests and rollback path. | Only if prior gates accept |

This plan covers only gate 1.

## 3. Scope

Evidence write set:

```text
docs/reviews/docling-baseline-support-source-truth-evidence-20260616.md
reports/docling-baseline-support-source-truth/20260616/source_truth_matrix.json
```

No source-code write set is accepted in this gate.

Allowed read inputs:

```text
docs/reviews/docling-field-correctness-anchor-coverage-no-live-implementation-controller-judgment-20260616.md
docs/reviews/docling-field-correctness-anchor-coverage-no-live-implementation-evidence-20260616.md
reports/docling-field-correctness-anchor-coverage-no-live-implementation/20260616/anchor_coverage_after_matrix.json
reports/docling-field-correctness-comparative/20260616/field_comparison_matrix.json
reports/representation-json/docling_multi_sample_field_family_correctness_reviewed_facts_20260616.json
fund_agent/fund/documents/repository.py
fund_agent/fund/documents/models.py
```

Allowed annual-report access:

```text
FundDocumentRepository.load_annual_report(fund_code, report_year, force_refresh=False)
```

Use of `force_refresh=True` is not allowed in this gate. If a required report is unavailable through the repository/cache path with `force_refresh=False`, classify the row or sample as `repository_source_body_unavailable` and stop before any live/network acquisition.

## 4. Non-goals

- No direct filesystem reads of annual-report PDFs.
- No direct reads of `cache/pdf`, parsed cache internals, source adapters, downloader helpers, or private repository state.
- No live/network/source acquisition.
- No `force_refresh=True`.
- No Docling conversion.
- No pdfplumber export.
- No provider/LLM/analyze/checklist/golden/release/PR/push/merge.
- No parser replacement.
- No source policy or fallback behavior change.
- No Service, Host, UI, renderer, quality gate, or production extractor behavior change.
- No acceptance of `基金年报/` as source truth.

## 5. Evidence Method

The evidence worker must build a source-truth matrix using the same 72 accepted comparative rows already used by the anchor-coverage gate.

For each row:

1. Load the annual report through `FundDocumentRepository` with `force_refresh=False`.
2. Verify repository metadata:
   - `metadata.source.selected_source == "eid"` when present;
   - `metadata.source.source_mode == "single_source_only"` when present;
   - `metadata.source.fallback_used is False` when present;
   - `metadata.source.report_year` matches the reviewed row year when present.
3. Resolve the Docling candidate anchor from the accepted after matrix.
4. Compare the candidate value/excerpt to repository-loaded source body using same-report, same-section, same-page or same-table evidence when available through public `ParsedAnnualReport` contract.
5. Classify each row with one of:
   - `source_body_match`;
   - `source_body_mismatch`;
   - `ambiguous_source_body_match`;
   - `repository_source_body_unavailable`;
   - `insufficient_public_locator`;
   - `semantic_assignment_residual`.

Rows may be accepted as source-truth evidence only when the source body is loaded through `FundDocumentRepository` and the comparison is direct enough to be same-source, not inferred from candidate-to-candidate agreement.

## 6. Deterministic Matching Contract

This gate proves only repository parsed source-body correspondence. It does not prove raw-PDF bbox truth because the public `ParsedAnnualReport` contract exposes `raw_text`, `sections`, `tables`, and metadata, but not source PDF bbox/crop objects.

The evidence worker must use this matching order:

1. Table-backed candidate rows:
   - use candidate page number and normalized row/cell value from the accepted anchor matrix;
   - search only repository `ParsedTable` objects with the same `page_number`;
   - normalize repository table cells and candidate value with the same deterministic normalizer;
   - count exact normalized cell or row-value occurrences.
2. Section-text-backed rows:
   - use candidate `section_id` when available;
   - search only `ParsedAnnualReport.get_section_text(section_id)` when the section exists;
   - if the section does not exist, classify as `insufficient_public_locator`, not global-match success.
3. Report-level fallback:
   - use `raw_text` only for fields whose accepted candidate anchor has no table and no supported section locator;
   - report-level fallback success must be labeled with `proof_level="repository_raw_text_unlocated_match"`;
   - it may not count as baseline qualification evidence without a later locator-strengthening gate.

Normalization must be deterministic:

- strip whitespace, full-width spaces and line breaks;
- normalize ASCII and Chinese punctuation variants only when they do not change token order;
- normalize numeric thousands separators and percent signs;
- do not infer synonyms, semantic equivalence, manager identity, benchmark identity, or table meaning.

Disposition rules:

| Condition | Row disposition |
| --- | --- |
| exactly one normalized source-body match in the allowed search scope | `source_body_match` |
| zero normalized source-body matches in the allowed search scope | `source_body_mismatch` |
| more than one normalized source-body match in the allowed search scope | `ambiguous_source_body_match` |
| repository load fails without live refresh | `repository_source_body_unavailable` |
| candidate anchor lacks enough public locator to choose table/section/report-level scope | `insufficient_public_locator` |
| row requires semantic assignment beyond literal source-body match | `semantic_assignment_residual` |

Candidate locator reuse groups require field-by-field disposition. A shared candidate locator may not automatically make every reused fact `source_body_match`.

S6-F041 must remain `semantic_assignment_residual` unless repository source body independently contains a benchmark-labeled source-body context for the same value. A literal occurrence of the same text under an investment-objective label is not enough.

## 7. Required Matrix Fields

The JSON matrix must include:

- input artifact paths and SHA-256 values;
- sample id, fund code, report year, fact id, field name and family;
- candidate anchor locator from after matrix;
- repository load status;
- repository metadata snapshot;
- source-body comparison status;
- source excerpt or a bounded redacted excerpt when available;
- candidate excerpt;
- match strategy;
- proof level;
- normalized candidate value;
- normalized source match count;
- exact/normalized comparison result;
- row disposition;
- residual reason, if any;
- negative guards:
  - `not_baseline_promotion=true`;
  - `not_parser_replacement=true`;
  - `not_release_readiness=true`;
  - `not_full_field_correctness=true`.

Allowed `proof_level` values:

```text
repository_table_page_cell_or_row_match
repository_section_text_match
repository_raw_text_unlocated_match
none
```

Only `repository_table_page_cell_or_row_match` and `repository_section_text_match` may count as selected-row source-body evidence for this gate.

## 8. Acceptance Criteria

The evidence gate can pass only if:

- every row has a closed disposition;
- no row is counted as source truth without `FundDocumentRepository` source-body access;
- no direct PDF/cache/source-helper file read is used;
- `source_body_match` has exactly one normalized source-body match in the allowed public search scope;
- `ambiguous_source_body_match` rows are residuals, not accepted source truth;
- `repository_raw_text_unlocated_match` rows are residuals for baseline qualification, even if literal text matches;
- `S6-F041` remains `semantic_assignment_residual` unless source-body evidence directly proves benchmark semantics;
- source-truth results are separated from baseline promotion;
- release/readiness remains `NOT_READY`.

Passing this gate may produce:

```text
SOURCE_TRUTH_EVIDENCE_PARTIAL_NOT_READY
SOURCE_TRUTH_EVIDENCE_ACCEPTED_FOR_SELECTED_ROWS_NOT_READY
SOURCE_TRUTH_EVIDENCE_BLOCKED_NOT_READY
```

It must not produce baseline readiness.

## 9. Validation Commands

Required commands:

```bash
uv run python - <<'PY'
# source-truth matrix generation using FundDocumentRepository only,
# force_refresh=False, no direct PDF/cache/source-helper reads
PY

python -m json.tool reports/docling-baseline-support-source-truth/20260616/source_truth_matrix.json >/dev/null

git diff --check
```

Optional command for metadata-only inspection:

```bash
jq '.summary, .negative_guards, .residuals' reports/docling-baseline-support-source-truth/20260616/source_truth_matrix.json
```

Forbidden commands:

- any network command;
- any direct PDF filesystem extraction command;
- any `force_refresh=True` repository load;
- any Docling conversion;
- any pdfplumber export;
- any provider/LLM command;
- any release/readiness/PR/push/merge command.

## 10. Stop Conditions

Stop and write `SOURCE_TRUTH_EVIDENCE_BLOCKED_NOT_READY` if:

- repository public API cannot provide enough source body to compare rows;
- repository load requires live/network refresh;
- multiple rows require direct PDF/cache reads;
- source metadata indicates fallback, identity mismatch, schema drift, or missing source identity;
- S6-F041 would need candidate-side inference to count as benchmark source truth;
- any implementation change becomes necessary.

## 11. Review Requirements

This heavy evidence plan requires review before execution.

Reviewers must check:

- `FundDocumentRepository` is the only annual-report access path;
- no direct PDF/cache/source-helper reads are allowed;
- no live/network path is hidden behind `force_refresh=True`;
- selected-row source truth is not promoted into full field correctness;
- baseline promotion remains deferred;
- `NOT_READY` is preserved.

Allowed review verdicts:

```text
REVIEW_PASS_NOT_READY
REVIEW_BLOCKED_NEEDS_FIX_NOT_READY
```

## 12. Final Verdict

```text
VERDICT: SOURCE_TRUTH_EVIDENCE_PLAN_READY_FOR_REVIEW_NOT_READY
```
