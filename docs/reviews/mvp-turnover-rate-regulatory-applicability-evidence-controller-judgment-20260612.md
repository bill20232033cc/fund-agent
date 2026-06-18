# Controller Judgment: Turnover Rate Regulatory Applicability Evidence Gate

Date: 2026-06-12

Gate: `Turnover rate regulatory applicability evidence gate`

Classification: `standard`

Verdict: `ACCEPT_WITH_AMENDMENTS_NOT_READY`

## Reviewed Artifacts

- Evidence:
  `docs/reviews/mvp-turnover-rate-regulatory-applicability-evidence-20260612.md`
- DS-role review:
  `docs/reviews/mvp-turnover-rate-regulatory-applicability-evidence-review-ds-20260612.md`
- MiMo-role review:
  `docs/reviews/mvp-turnover-rate-regulatory-applicability-evidence-review-mimo-20260612.md`
- Prior turnover root-cause controller judgment:
  `docs/reviews/mvp-turnover-rate-root-cause-evidence-controller-judgment-20260612.md`

## Decision

The gate is accepted with disposition:

`REGULATORY_APPLICABILITY_SCORING_GAP_CONFIRMED`

The accepted `004393 / 2025` warning remains a real warning identity in the
current code path, but the root cause is now reclassified from source/extractor
uncertainty to applicability/scoring scope.

This gate does not authorize a code change. It authorizes the next planning gate
for a narrow scoring/applicability fix.

## Evidence Basis

| Evidence | Controller finding |
| --- | --- |
| CSRC captured HTML | The revised periodic-report guideline is a 2026 CSRC rule and is effective from `2026-05-01`. |
| AMAC captured HTML | The related XBRL templates are effective from `2026-05-01` and include quarterly plus annual/interim templates. |
| AMAC annual/semiannual template | Section `8.4.4 股票换手率` exists; its item is annual-report-only and not applicable to interim reports; applicability is active stock and mixed funds. |
| AMAC quarterly template negative search | No `股票换手率` / `换手率` item was found in the captured quarterly template by the recorded local search. |
| Prior root-cause evidence | Snapshot-to-score-to-quality chain is internally consistent, so the accepted `FQ2/FQ2F` warning is not a score aggregation bug for the current row. |

## Review Disposition

| Finding | Disposition | Reason |
| --- | --- | --- |
| Need durable official evidence locator | `ACCEPT_WITH_REWRITE` | Evidence artifact now includes capture directory, URLs, sizes, SHA-256 hashes, commands and source locators. |
| Reclassification to applicability/scoring scope | `ACCEPT` | Effective-date/template evidence makes extractor failure the wrong default branch for `004393 / 2025`. |
| Cutoff semantics remain open | `ACCEPT_AS_RESIDUAL` | The current sample is pre-effective under report-year semantics; publication-date/template-version semantics must be planned before implementation. |
| Next entry is narrow fix planning | `ACCEPT` | This gate proves the root-cause class, not the exact implementation. |

## Residuals

| Residual | Owner | Next gate | Current blocker? |
| --- | --- | --- | --- |
| Exact cutoff semantics | Fund scoring/applicability owner | `Turnover rate regulatory applicability narrow fix planning gate` | Blocks implementation |
| Required code surface | Fund scoring/applicability owner | Same planning gate | Blocks implementation |
| Post-fix quality warning closure evidence | Controller + implementation owner | Future fix evidence/review/controller acceptance gate | Blocks readiness |
| Strict golden 2025 `FQ0/info` | Strict golden coverage owner | Strict golden 2025 coverage/promotion planning gate | Separate residual |

## Next Entry

Recommended next entry:

`Turnover rate regulatory applicability narrow fix planning gate`

Planning objective:

- define the smallest code change that excludes non-applicable
  `turnover_rate` rows from P1 coverage/traceability scoring;
- explicitly decide cutoff semantics:
  - report-year cutoff;
  - publication-date cutoff;
  - source/template-version cutoff;
- ensure quarterly and interim reports are non-applicable;
- preserve `FQ2/FQ2F` semantics for truly applicable future annual reports that
  still fail coverage/traceability;
- keep EID source policy, fallback policy, provider/LLM behavior, strict golden,
  release/readiness and PR state unchanged.

Implementation remains closed until that narrow fix planning gate is accepted.
