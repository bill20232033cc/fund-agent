# Docling Baseline Support Source-truth Evidence Controller Judgment - 2026-06-16

Gate: `Docling Baseline Support Source-truth Evidence Controller Judgment`
Role: controller
Gate classification: `heavy`
Release/readiness: `NOT_READY`

## 1. Inputs Reviewed

Plan and plan judgment:

- `docs/reviews/docling-baseline-support-source-truth-evidence-plan-20260616.md`
- `docs/reviews/docling-baseline-support-source-truth-evidence-plan-controller-judgment-20260616.md`

Evidence and review:

- `docs/reviews/docling-baseline-support-source-truth-evidence-20260616.md`
- `reports/docling-baseline-support-source-truth/20260616/source_truth_matrix.json`
- `docs/reviews/docling-baseline-support-source-truth-evidence-review-20260616.md`

## 2. Controller Decision

Accept the source-truth evidence as partial, residual-preserving evidence.

Accepted bounded fact:

```text
55 / 72 selected Docling candidate rows matched repository parsed source body
17 / 72 rows remain residual or blocked
4 / 4 reports loaded through FundDocumentRepository with EID single-source metadata
```

This is not enough for Docling baseline qualification.

## 3. Residual Disposition

| Residual family | Count | Controller disposition |
| --- | ---: | --- |
| `ambiguous_source_body_match` | `15` | Accepted residual; requires locator/disambiguation strengthening before source-truth closure |
| `source_body_mismatch` | `1` | Accepted blocker; requires row-level investigation before field correctness |
| `semantic_assignment_residual` | `1` | Accepted residual; S6-F041 benchmark semantics remains unproven |

## 4. Not Accepted

This judgment does not accept:

- raw-PDF bbox source truth;
- full field correctness;
- Docling baseline qualification;
- production parser replacement;
- release readiness;
- PR readiness.

## 5. Next Entry Point

Next gate:

```text
Docling Source-truth Residual Closure Planning Gate
```

Purpose:

- decide whether to improve locator disambiguation for the 15 ambiguous rows;
- investigate the single S5-F023 source-body mismatch;
- keep S6-F041 as semantic residual unless benchmark-labeled source context can be proven;
- determine whether a later raw-PDF/bbox proof gate is required before baseline qualification.

Do not enter full field-correctness or baseline qualification while these residuals remain open.

## 6. Validation Accepted

Accepted validation:

```bash
python -m json.tool reports/docling-baseline-support-source-truth/20260616/source_truth_matrix.json >/dev/null
git diff --check
```

Both passed.

## 7. Verdict

```text
VERDICT: ACCEPT_SOURCE_TRUTH_EVIDENCE_PARTIAL_WITH_RESIDUALS_NOT_READY
```
