# DS-role Review: Turnover Rate Regulatory Applicability Evidence Gate

Date: 2026-06-12

Review target:
`docs/reviews/mvp-turnover-rate-regulatory-applicability-evidence-20260612.md`

Reviewer role: AgentDS-role

Verdict: `PASS_WITH_AMENDMENTS`

## Findings

| ID | Severity | Finding | Controller disposition |
| --- | --- | --- | --- |
| `DS-REG-001` | medium | `REGULATORY_APPLICABILITY_SCORING_GAP_CONFIRMED` direction is acceptable, but official evidence needs durable citation/locator rather than URL summaries only. | Accepted and amended. Artifact now includes captured official material hashes, source URLs, command evidence and locators. |
| `DS-REG-002` | none | Reclassifying `004393 / 2025` turnover warning as applicability/scoring scope is defensible. Prior evidence accepted snapshot-to-score chain but did not prove extractor miss; official effective-date/template evidence explains why 2025 should not be scored by the new mandatory item. | Accepted. |
| `DS-REG-003` | low | `2025 and earlier annual reports` conclusion is sufficient for the current sample, but future cutoff semantics still need design. | Accepted as planning residual. |
| `DS-REG-004` | none | Next entry is correct: `Turnover rate regulatory applicability narrow fix planning gate`, not direct implementation. | Accepted. |
| `DS-REG-005` | low | Workspace guard has tracked control-doc diff; controller judgment should record that those changes are control sync only. | Accepted; final verification records no source/test/runtime diff. |

## Residuals

- User business assertion cannot replace official/template evidence.
- Fix planning must explicitly decide cutoff semantics: report year, publication
  date, or source/template version.
- Fix planning must keep source acquisition, EID, fallback, provider and
  readiness unchanged.

## Final Recommendation

Accept after evidence-locator amendment. Do not open extractor implementation.
Next entry should be `Turnover rate regulatory applicability narrow fix planning
gate`.
