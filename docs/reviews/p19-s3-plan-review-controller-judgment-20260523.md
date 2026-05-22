# P19-S3 Plan Review Controller Judgment（2026-05-23）

## Verdict

`FAIL_PATCH_REQUIRED`

Two independent plan reviews failed:

- `docs/reviews/p19-s3-plan-review-mimo-20260523.md`: `fail`
- `docs/reviews/p19-s3-plan-review-glm-20260523.md`: `fail`

The P19-S3 direction is accepted, but the current plan is not safe to hand to implementation. P19-S3 changes the default `fund-analysis analyze` valuation input path, so provenance, benchmark identity, default semantics, disclaimer output, and thermometer failure behavior must be specified as verifiable contracts before implementation.

## Accepted Findings

| Finding | Source | Judgment | Required patch |
|---|---|---|---|
| ProgrammaticAudit cannot infer automatic valuation provenance from checklist reason text | MiMo / GLM | Accepted | Make `ValuationStateResolution` or equivalent provenance a structured truth source for renderer/audit; R1 must not parse human-readable reason text to decide source. |
| Benchmark alias matching can mis-map derived indices such as 沪深300价值 or 中证500质量成长 | MiMo / GLM | Accepted | Define exact index-identity matching, reject substring/derived/style/sector/equal-weight/low-volatility variants, and add negative tests. |
| CLI/Service default migration from `unavailable` to `None` lacks explicit public-contract and opt-out acceptance | MiMo | Accepted | State this is an intentional P19-S3 public contract change; require `--valuation-state unavailable` / `valuation_state=\"unavailable\"` to suppress auto and preserve manual gray semantics. |
| Disclaimer is not a report/CLI acceptance contract | MiMo | Accepted | Require report and CLI output to contain equivalent independent-calculation disclaimer when thermometer auto path is used. |
| Thermometer calculation-error gray fallback lacks tests | GLM | Accepted | Add Service tests for expected self-owned thermometer calculation/data errors converting to unavailable gray, while programming contract errors still fail closed. |

## First-principles Judgment

Automatic thermometer-to-`valuation_state` integration is not a display convenience. It changes checklist item 6, checklist aggregate signal, and potentially final judgment. Therefore the plan must make the automatic valuation source machine-verifiable and must prefer false-unavailable over false-red/green whenever index identity is uncertain.

## Required Re-review Criteria

- The patched plan defines one structured provenance truth source and threads it through Service, checklist/renderer, and ProgrammaticAudit.
- The patched plan uses exact benchmark identity matching, not alias substring matching.
- The patched plan records default auto behavior as intentional and documents the opt-out path.
- The patched plan makes disclaimer output testable.
- The patched plan covers thermometer calculation/data exceptions in tests.

## Next Gate

Patch `docs/reviews/p19-s3-valuation-state-integration-plan-20260523.md`, then run P19-S3 plan re-review.
