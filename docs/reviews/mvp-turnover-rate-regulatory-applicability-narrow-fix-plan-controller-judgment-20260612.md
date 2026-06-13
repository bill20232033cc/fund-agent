# Controller Judgment: Turnover Rate Regulatory Applicability Narrow Fix Plan

Date: 2026-06-12

Gate: `Turnover rate regulatory applicability narrow fix planning gate`

Classification: `standard`

Verdict: `ACCEPT_WITH_AMENDMENTS_NOT_READY`

## Reviewed Artifacts

- Plan:
  `docs/reviews/mvp-turnover-rate-regulatory-applicability-narrow-fix-plan-20260612.md`
- DS-role review:
  `docs/reviews/mvp-turnover-rate-regulatory-applicability-narrow-fix-plan-review-ds-20260612.md`
- MiMo-role review:
  `docs/reviews/mvp-turnover-rate-regulatory-applicability-narrow-fix-plan-review-mimo-20260612.md`
- Regulatory applicability evidence controller judgment:
  `docs/reviews/mvp-turnover-rate-regulatory-applicability-evidence-controller-judgment-20260612.md`

## Decision

The plan is accepted with amendments. Implementation may proceed only inside the
allowed write set and only after entering the next implementation gate.

Accepted root-cause class:

`REGULATORY_APPLICABILITY_SCORING_GAP_CONFIRMED`

Accepted cutoff for the first narrow fix:

- `report_year < 2026`: exclude `turnover_rate` from P1 scoring;
- `report_year >= 2026`: keep `turnover_rate` applicable unless explicit
  row-level non-annual metadata says otherwise;
- do not infer report kind from anchors, source provenance, file names, paths or
  untracked artifacts.

## Accepted Write Set For Implementation

Allowed source:

- `fund_agent/fund/extraction_score.py`

Allowed tests:

- `tests/fund/test_extraction_score.py`
- `tests/services/test_fund_analysis_service.py`

Conditional documentation:

- `fund_agent/fund/README.md`, only if it currently documents quality-score
  field applicability or `turnover_rate` quality semantics.

Explicitly excluded:

- extractor code;
- source acquisition, repository, cache, downloader, FDR and fallback code;
- `fund_agent/fund/quality_gate.py`;
- provider/LLM, golden, readiness, release, PR and cleanup surfaces.

## Review Disposition

| Finding | Disposition | Reason |
| --- | --- | --- |
| Plan is narrow and code-generation-ready | `ACCEPT` | The write set is limited to score applicability and tests. |
| Report-year cutoff is acceptable as first fix | `ACCEPT` | Current snapshot contract has stable `report_year`; durable publication-date/template-version metadata is absent. |
| Non-annual metadata wording must be row-level only | `ACCEPT_WITH_REWRITE` | Plan was amended to forbid inference from anchors, provenance, file names or residue. |
| Shared `_scorable_records(...)` path must be explicit | `ACCEPT_WITH_REWRITE` | Plan now requires implementation evidence to verify `score_snapshot_records`, `score_fund_records`, and `derive_fund_quality_records`. |
| Prevent over-broad filtering | `ACCEPT_WITH_REWRITE` | Plan now requires a mixed-record test proving unrelated P1 failures remain visible. |
| Preserve bond/index applicability behavior | `ACCEPT_WITH_REWRITE` | Plan now requires existing bond/index applicability tests to remain green and focused assertion if early-return refactor risks regression. |
| Preserve future `FQ2/FQ2F` warning semantics | `ACCEPT_WITH_REWRITE` | Plan now requires the manual failed-score quality-gate test to remain green and be recorded in evidence. |

## Implementation Gate Acceptance Criteria

The next implementation gate cannot be accepted unless evidence shows:

1. pre-2026 `turnover_rate` no longer creates field-level P1 fail or derivative
   fund-level fail;
2. pre-2026 `turnover_rate` exclusion does not suppress unrelated applicable P1
   failures;
3. 2026+ applicable `turnover_rate` missing rows still fail P1 scoring;
4. explicit row-level non-annual report-kind metadata excludes `turnover_rate`;
5. `derive_field_applicability_decisions(...)` explains each exclusion;
6. no replacement `ScoreApplicabilityIssue` is emitted for expected
   non-applicability;
7. existing index/bond applicability behavior remains unchanged;
8. manually supplied failed `turnover_rate` score rows still create
   `FQ2/FQ2F` warnings in quality gate.

## Required Validation For Implementation Gate

```bash
uv run pytest tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py tests/services/test_fund_analysis_service.py -q
uv run ruff check fund_agent/fund/extraction_score.py tests/fund/test_extraction_score.py tests/services/test_fund_analysis_service.py
git status --short
git status --branch --short
git diff --name-only
git diff --check
```

## Residuals

| Residual | Owner | Destination |
| --- | --- | --- |
| Publication-date/template-version cutoff semantics | Fund scoring/applicability owner | Future applicability refinement only if durable snapshot metadata is introduced |
| Strict golden 2025 `FQ0/info year_not_covered` | Strict golden coverage owner | Strict golden 2025 coverage/promotion planning gate |
| Release/readiness state | Controller/release owner | Future release-readiness rollup after implementation evidence and reviews |

## Next Entry

Recommended next entry:

`Turnover rate regulatory applicability narrow fix implementation gate`

Implementation remains closed until this gate is explicitly entered. The next
gate must not open extractor, source acquisition, fallback, provider/LLM, strict
golden, readiness/release, PR or cleanup work.
