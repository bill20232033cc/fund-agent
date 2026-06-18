# Docling EvidenceAnchor Mapping Section-context Enrichment Re-evidence Fix Evidence - 2026-06-16

Gate: `Docling EvidenceAnchor Mapping Section-context Enrichment Re-evidence Fix Gate`
Role: evidence fix worker
Release/readiness: `NOT_READY`

## Scope

This fix only amends the re-evidence artifact:

- `docs/reviews/docling-evidenceanchor-mapping-section-context-enrichment-reevidence-20260616.md`

No code, tests, control docs, design docs, README, reports, cache, source acquisition, repository, parser, Service, Host, UI, provider/LLM, readiness, release, PR, push or merge files/actions were changed.

## Finding Disposition

| Review finding | Disposition | Fix applied |
| --- | --- | --- |
| DS finding 01: S1-current-envelope and S1-full-json artifact relationship not disclosed | ACCEPTED_AND_FIXED | Added an explicit statement that S1-current-envelope and S1-full-json are not interchangeable; S1 counts represent the accepted envelope path only. |
| DS finding 02 / MiMo finding 02: aggregate yield mixes schema families and paragraph mapping is S1-specific | ACCEPTED_AND_FIXED | Added interpretation caveat under table/cell yield and added residual for S4/S5/S6 zero paragraph mapping. |
| MiMo finding 01: S5/S6 yield variance not explained | ACCEPTED_AS_RESIDUAL | Existing S6 low-yield residual is retained; per-sample variance is routed to future root-cause investigation, not this evidence fix. |

## Validation

```text
git diff --check
```

Result: passed before this fix; controller should rerun after this fix before closeout.

## Final Status

```text
FIXED_EVIDENCE_DISCLOSURE_NOT_READY
```
