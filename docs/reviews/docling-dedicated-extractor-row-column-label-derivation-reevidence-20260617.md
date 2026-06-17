# Docling Dedicated Extractor Row-column Label Derivation Re-evidence - 2026-06-17

Gate: `Docling Dedicated Extractor Row-column Label Derivation Re-evidence Gate`
Accepted plan commit: `07886d1`
Status: `REEVIDENCE_COMPLETE_NOT_READY`
Verdict: `ROW_COLUMN_LABEL_DERIVATION_LIMITED_UPLIFT_NOT_READY`
Release/readiness: `NOT_READY`

## Evidence Artifact

- `reports/docling-dedicated-extractor-row-column-label-derivation-reevidence/20260617/template_field_coverage_after_row_column_labels.json`

## Aggregate Result

| Metric | Section-context baseline | After row/column labels |
|---|---:|---:|
| Runnable samples | 4 | 4 |
| Target field slots | 92 | 92 |
| Direct slots | 48 | 49 |
| Missing slots | 44 | 43 |
| Candidate anchors | 52 | 57 |
| Direct coverage ratio | 0.5217391304347826 | 0.532608695652174 |

## Per-sample Direct Coverage

| Sample | Fund | Direct | Missing | Anchors |
|---|---:|---:|---:|---:|
| S1 | 004393 | 13 | 10 | 14 |
| S4 | 006597 | 12 | 11 | 15 |
| S5 | 017641 | 11 | 12 | 12 |
| S6 | 110020 | 13 | 10 | 16 |

## Field-level Uplift

Only one target field improved against the section-context baseline:

| Field | Before | After |
|---|---:|---:|
| `holdings_snapshot.target_fund_holdings` | 0 | 1 |

Fields still missing in all four samples:

- `product_profile.investment_scope`
- `nav_benchmark_performance.nav_growth_rate`
- `nav_benchmark_performance.benchmark_return_rate`
- `tracking_error.value_text`
- `turnover_rate`
- `manager_strategy_text`
- `holder_structure`
- `share_change`
- `bond_risk_evidence`

## Interpretation

Accepted facts:

- The implementation preserves candidate-only and `source_truth_status="not_proven"` boundaries.
- The implementation creates a small real-envelope uplift but does not materially close the baseline gap.
- The main remaining residual is not solved by generic row/column label derivation.
- The result does not authorize field correctness claims, source-truth acceptance, parser replacement, baseline promotion, production integration, release readiness, or PR readiness.

## Validation

Command:

```text
uv run pytest tests/fund/documents/test_docling_template_field_extraction.py tests/fund/documents/test_docling_evidence_anchor_mapping.py -q
```

Result:

```text
56 passed in 0.41s
```

Command:

```text
uv run ruff check fund_agent/fund/documents/candidates/template_field_extraction.py tests/fund/documents/test_docling_template_field_extraction.py
```

Result:

```text
All checks passed!
```

No-live matrix generation:

```text
uv run python -c '<load same four accepted current-schema candidate JSON payloads; project_candidate_representation(payload); extract_docling_template_fields(document); write template_field_coverage_after_row_column_labels.json>'
```

Result:

```text
{"anchor_count": 57, "blocked_slot_count": 0, "direct_coverage_ratio": 0.532608695652174, "direct_slot_count": 49, "missing_ratio": 0.4673913043478261, "missing_slot_count": 43, "sample_count": 4, "target_field_slot_count": 92}
```

## Residual Owner

Next recommended gate:

`Docling Dedicated Extractor Residual Table-shape Diagnostic Planning Gate`

Purpose:

- explain why performance, tracking error, turnover, and remaining holdings fields still do not match;
- inspect actual real-envelope table/text shapes for the still-missing field families;
- decide whether the next narrow route is target-specific table family recognition, text-pattern extraction, or field-specific extractor rules;
- keep candidate-only / `NOT_READY` boundaries.

VERDICT: `ROW_COLUMN_LABEL_DERIVATION_LIMITED_UPLIFT_NOT_READY`
