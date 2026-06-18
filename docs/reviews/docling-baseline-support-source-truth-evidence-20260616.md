# Docling Baseline Support Source-truth Evidence - 2026-06-16

Gate: `Docling Baseline Support Source-truth Evidence Gate`
Role: evidence worker
Gate classification: `heavy`
Release/readiness: `NOT_READY`

## 1. Scope

Executed the accepted plan:

- `docs/reviews/docling-baseline-support-source-truth-evidence-plan-20260616.md`
- `docs/reviews/docling-baseline-support-source-truth-evidence-plan-controller-judgment-20260616.md`

Evidence output:

- `reports/docling-baseline-support-source-truth/20260616/source_truth_matrix.json`

This gate used `FundDocumentRepository.load_annual_report(..., force_refresh=False)` only.

To preserve no-live behavior, the execution injected a cache-only annual-report loader: repository parsed-cache hits were accepted; repository-owned parsing from existing PDF cache was allowed; any attempted PDF fetch was fail-closed. No direct PDF/cache/source-helper body read was performed by the evidence worker.

## 2. Result Summary

| Metric | Value |
| --- | ---: |
| Reviewed candidate rows | `72` |
| Repository source-body matches | `55` |
| Residual or blocked rows | `17` |
| Repository loads | `4 / 4` |
| EID single-source metadata OK | `4 / 4` |

Disposition split:

| Disposition | Count |
| --- | ---: |
| `source_body_match` | `55` |
| `ambiguous_source_body_match` | `15` |
| `source_body_mismatch` | `1` |
| `semantic_assignment_residual` | `1` |

By sample:

| Sample | Rows | Accepted source-body matches | Residuals |
| --- | ---: | ---: | ---: |
| S1 | `21` | `18` | `3` |
| S4 | `17` | `14` | `3` |
| S5 | `17` | `13` | `4` |
| S6 | `17` | `10` | `7` |

## 3. Repository Source Metadata

All four reports loaded through `FundDocumentRepository` with EID single-source metadata:

| Report | Status | Source | Source mode | Fallback used | Parsed cache hit | PDF cache hit |
| --- | --- | --- | --- | --- | --- | --- |
| `004393 / 2025` | loaded | `eid` | `single_source_only` | `false` | `true` | `false` |
| `006597 / 2024` | loaded | `eid` | `single_source_only` | `false` | `true` | `false` |
| `017641 / 2024` | loaded | `eid` | `single_source_only` | `false` | `false` | `true` |
| `110020 / 2024` | loaded | `eid` | `single_source_only` | `false` | `true` | `false` |

## 4. Residuals

Residual rows are closed and not counted as source truth:

| Family | Count | Meaning |
| --- | ---: | --- |
| `ambiguous_source_body_match` | `15` | normalized value appears more than once in the allowed repository source scope |
| `source_body_mismatch` | `1` | no normalized source-body match in the allowed repository scope |
| `semantic_assignment_residual` | `1` | literal candidate value is insufficient to prove field semantics |

Notable residuals:

- `S6-F041 / benchmark` remains `semantic_assignment_residual`; the shared S6-F040/S6-F041 candidate cell is not enough to prove benchmark semantics.
- `S5-F023 / investment_objective` is `source_body_mismatch` under the deterministic repository-section matching contract.
- Fund-code, fund-name, manager/custodian and some portfolio amount fields often appear multiple times in the same allowed source scope and are therefore `ambiguous_source_body_match`.

## 5. Boundary Guardrails

This gate accepts only selected-row repository parsed source-body matches.

It does not prove:

- raw-PDF bbox source truth;
- full field correctness;
- Docling baseline qualification;
- production parser replacement;
- release readiness;
- PR readiness.

Negative guards:

```text
not_baseline_promotion=true
not_parser_replacement=true
not_release_readiness=true
not_full_field_correctness=true
not_raw_pdf_bbox_truth=true
```

## 6. Validation

Commands run:

```bash
uv run python - <<'PY'
# generated source_truth_matrix.json through FundDocumentRepository with cache-only loader
PY

python -m json.tool reports/docling-baseline-support-source-truth/20260616/source_truth_matrix.json >/dev/null

jq '.summary, .by_sample, .repository_loads, (.residuals[] | {sample_id, fact_id, field_name, row_disposition, normalized_source_match_count, residual_reason, proof_level})' reports/docling-baseline-support-source-truth/20260616/source_truth_matrix.json

git diff --check
```

Observed results:

| Check | Result |
| --- | --- |
| Matrix generation | passed |
| JSON validation | passed |
| Source-body matches | `55 / 72` |
| Residual rows | `17 / 72` |
| Diff whitespace check | passed |

## 7. Final Verdict

```text
VERDICT: SOURCE_TRUTH_EVIDENCE_PARTIAL_NOT_READY
```
