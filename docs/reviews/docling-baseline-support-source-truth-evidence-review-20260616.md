# Docling Baseline Support Source-truth Evidence Review - 2026-06-16

Gate: `Docling Baseline Support Source-truth Evidence Review Gate`
Role: evidence reviewer
Gate classification: `heavy`
Release/readiness: `NOT_READY`

## 1. Reviewed Inputs

- `docs/reviews/docling-baseline-support-source-truth-evidence-plan-20260616.md`
- `docs/reviews/docling-baseline-support-source-truth-evidence-plan-controller-judgment-20260616.md`
- `docs/reviews/docling-baseline-support-source-truth-evidence-20260616.md`
- `reports/docling-baseline-support-source-truth/20260616/source_truth_matrix.json`

## 2. Findings

No blocking findings.

## 3. Review Result

The evidence correctly reports a partial source-body result:

```text
55 / 72 source_body_match
17 / 72 residual or blocked
VERDICT: SOURCE_TRUTH_EVIDENCE_PARTIAL_NOT_READY
```

The artifact does not claim full source truth, full field correctness, baseline qualification, parser replacement, release readiness, or PR readiness.

## 4. Boundary Review

Accepted:

- annual reports were loaded through `FundDocumentRepository`;
- `force_refresh=False` was used;
- repository source metadata was recorded for all four samples;
- residual rows were not counted as source truth;
- `S6-F041` remained `semantic_assignment_residual`;
- negative guards were present.

Residual:

- the evidence permits repository-owned parsing from existing PDF cache through the FDR boundary. This is acceptable for this gate because the worker did not directly read PDF/cache files and attempted PDF fetch was fail-closed. It is not raw-PDF bbox truth and cannot support baseline qualification by itself.

## 5. Validation Reviewed

Reviewed validation:

```bash
python -m json.tool reports/docling-baseline-support-source-truth/20260616/source_truth_matrix.json >/dev/null
git diff --check
```

Both passed.

## 6. Verdict

```text
VERDICT: REVIEW_PASS_WITH_RESIDUALS_NOT_READY
```
