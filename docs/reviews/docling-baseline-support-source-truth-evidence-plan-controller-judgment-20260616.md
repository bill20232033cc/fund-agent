# Docling Baseline Support Source-truth Evidence Plan Controller Judgment - 2026-06-16

Gate: `Docling Baseline Support Source-truth Evidence Plan Controller Judgment`
Role: controller
Gate classification: `heavy`
Release/readiness: `NOT_READY`

## 1. Inputs Reviewed

Plan:

- `docs/reviews/docling-baseline-support-source-truth-evidence-plan-20260616.md`

Plan review and re-review:

- `docs/reviews/plan-review-20260616-181757.md`
- `docs/reviews/plan-review-20260616-181852.md`

Latest accepted implementation checkpoint:

- `8fe3dd9 gateflow: accept docling anchor coverage implementation`

## 2. Controller Decision

The source-truth evidence plan is accepted for execution.

Accepted next gate:

```text
Docling Baseline Support Source-truth Evidence Gate
```

This judgment authorizes only repository parsed source-body evidence generation using:

```text
FundDocumentRepository.load_annual_report(fund_code, report_year, force_refresh=False)
```

It does not authorize live/network acquisition, direct PDF/cache/source-helper reads, Docling conversion, pdfplumber export, provider/LLM commands, release/readiness, PR, push, or merge.

## 3. Finding Disposition

| Review artifact | Verdict | Controller disposition |
| --- | --- | --- |
| `docs/reviews/plan-review-20260616-181757.md` | `fail` | Accepted finding; plan required fix |
| `docs/reviews/plan-review-20260616-181852.md` | `pass` | Accepted; finding closed |

The blocking plan finding is closed.

## 4. Accepted Evidence Contract

The evidence gate must:

- load annual reports only through `FundDocumentRepository`;
- use `force_refresh=False`;
- classify unavailable repository source body as residual or blocked, not trigger live refresh;
- apply deterministic matching order for table, section text and report-level fallback;
- classify duplicate normalized source matches as `ambiguous_source_body_match`;
- mark `repository_raw_text_unlocated_match` as residual for baseline qualification;
- keep `S6-F041` as `semantic_assignment_residual` unless repository source body independently proves benchmark-labeled context.

## 5. Non-accepted Conclusions

This judgment does not accept:

- source truth yet;
- full field correctness;
- Docling baseline promotion;
- production parser replacement;
- release readiness;
- PR readiness.

## 6. Next Gate Write Set

The next evidence gate may write only:

```text
docs/reviews/docling-baseline-support-source-truth-evidence-20260616.md
reports/docling-baseline-support-source-truth/20260616/source_truth_matrix.json
```

## 7. Validation

Observed planning validation:

```bash
git diff --check
# passed
```

## 8. Verdict

```text
VERDICT: ACCEPT_SOURCE_TRUTH_EVIDENCE_PLAN_READY_FOR_EXECUTION_NOT_READY
```
