# MVP multi-year annual evidence scope design review fix evidence

## Worker Self-Check

- Role: scoped design-fix specialist only, not controller.
- Gate: `MVP multi-year annual evidence scope design gate`.
- Classification: `heavy`, design/review only.
- Allowed edited files:
  - `docs/reviews/mvp-multi-year-annual-evidence-scope-design-20260603.md`
  - `docs/reviews/mvp-multi-year-annual-evidence-scope-design-review-fix-evidence-20260603.md`
- Required inputs read: `AGENTS.md`, `docs/design.md`, `docs/implementation-control.md`, the design artifact, AgentDS review, AgentMiMo review, and the required Fund model/extractor/projection files.
- Actions intentionally not taken: no implementation, no source/test/truth-doc edits, no README edits, no report mutation, no commit, no push, no PR.

## Finding Disposition Table

| Finding | Disposition | Fix evidence |
|---|---|---|
| DS F1 optional prior-year fail-closed contradiction | Accepted and fixed | Design now splits current-year blocking from optional prior-year per-year isolation. Optional prior-year `schema_drift` / `identity_mismatch` / `integrity_error` marks that year `failed_closed`, blocks dependent cross-year claims, and does not kill current-year report unless current year or a future required prior year is affected. |
| DS F2 requirement-sensitive availability missing from type shape | Accepted and fixed | Added `requirement_availability` keyed by requirement/fact category such as `fee_trend`, `turnover_trend`, `holdings_trend`, `manager_continuity`, and `performance_series`; coarse `1Y` / `3Y` / `5Y` is now a derived summary only. |
| DS F3 `AnnualEvidenceScopeRequest` precedence undefined | Accepted and fixed | Added construction-time validation: `target_year` required, `required_years` must contain `target_year`, required/optional years must be disjoint, `max_years` cap is `1..5`, optional years truncate from most distant first, and canonical order is target year then prior years descending. |
| DS F4 same-fund identity and `fund_id` mismatch | Accepted and fixed | Added identity contract: same `fund_code` always; `fund_id` consistency compared only within the same source when present across years; same-source mismatch is `identity_mismatch` for affected year; cross-source `fund_id` comparison is not required for MVP. |
| DS F5 cumulative fallback provenance | Accepted and fixed | Added `AnnualEvidenceFallbackSummary` with `fallback_years`, `fallback_year_count`, and `primary_failure_categories`; `CrossYearDerivedFact` carries fallback provenance caveat when source years used fallback. |
| DS F6 `AnnualEvidenceGap` undefined | Accepted and fixed | Design now reuses or extends `ReportDataGap` for MVP; `AnnualEvidenceGap` may only be an alias/specialization that serializes into the same gap truth and may not create a third unrelated gap source. |
| DS F7 `DocumentIdentityStatus` mapping unclear | Accepted and fixed | Added MVP mapping from current `DocumentIdentityStatus`: successful same-fund annual reports use `verified_annual_report`; `identity_mismatch` maps to `mismatch`; source fail-closed or unavailable/missing optional years map to `source_failed` plus `ReportDataGap`. Future `same_fund_verified` / `cross_year_ambiguous` statuses are allowed but not required. |
| DS F8 cross-year anchor provenance missing | Accepted and fixed | Added `CrossYearDerivedFact` conceptual shape with `source_years` and `source_year_anchor_ids`; writer/auditor consumption requires source-year anchors. |
| DS F9 repeated NAV/drawdown risk | Accepted and fixed | Template/Agent feed and planning slices now state prior-year extraction should prefer annual-report-only summaries and avoid repeated prior-year NAV/drawdown unless a later gate explicitly requires multi-year NAV/drawdown. |
| DS F10 `ReportEvidenceProjectionContext` relationship missing | Accepted and fixed | Current facts now note it is single-year shaped; bundle semantics now require per-year `source_failure_category`, `fallback_used`, `primary_failure_category`, and `document_identity_status`, with bundle summaries derived from per-year fields. |
| MiMo F1 raw `fund_code` vs `DocumentKey` pattern | Deferred with explicit planning implication | Kept Service request as explicit user/business scope fields and added same-`fund_code` plus per-year identity requirements. Canonical per-year document identity choice remains implementation-slice work because Service must not own repository `DocumentKey` construction. |
| MiMo F2 cross-year `ChapterFactProvider` contract unspecified | Accepted and fixed | Added explicit requirement that ChapterFactProvider / ChapterFactProjection extension contract be defined before implementation; allowed approaches preserve public chapter ids `0-7` and use typed year-level gaps / `CrossYearDerivedFact`. |
| MiMo F3 Chapter 2 multi-year R=A+B-C data source | Accepted and fixed | Added `performance_series` availability and Chapter 2 degradation rule: use only available anchored years or mark unavailable rows; no synthetic five-year table and no Ch2 split authorization. |
| MiMo F4 `AnnualEvidenceBundle` vs `ReportEvidenceBundle` relationship | Accepted and fixed | Added `ReportDataGap` reuse, per-year projection context fields, bundle-level fallback summary, and canonical anchor id namespace as planning-slice requirements. |
| MiMo F5 requirement-sensitive examples and coarse tier relationship | Accepted and fixed | Added concrete requirement keys and made coarse `data_tier_availability` derived over `requirement_availability`, not independently asserted. |
| MiMo F6 year ordering unspecified | Accepted and fixed | Added canonical request order: `target_year`, then prior years descending. Cross-year calculations may sort internally only if source years and anchor ids remain explicit. |
| MiMo F7 repository concurrency | Deferred as residual | Added residual and loading-boundary statement: concurrency is allowed only after a later implementation gate proves repository/cache/source adapter safety; sequential loading remains acceptable for correctness-first MVP. |
| MiMo F8 `force_refresh` semantics across years | Accepted as MVP clarification; granular control deferred | Added MVP rule that `force_refresh` applies uniformly to all requested years; per-year refresh is deferred and must not be hidden in `extra_payload`. |

## Files Changed

- `docs/reviews/mvp-multi-year-annual-evidence-scope-design-20260603.md`
- `docs/reviews/mvp-multi-year-annual-evidence-scope-design-review-fix-evidence-20260603.md`

## Explicit Non-Changes

- No code implementation.
- No source files changed.
- No tests changed.
- No `AGENTS.md`, `docs/design.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md`, README, or template truth changes.
- No provider budget, provider timeout, score-loop, quality gate, golden/readiness, quarterly report, prospectus, fund-contract, Ch2 split, public chapter count, or final-judgment changes.
- No direct report mutation and no raw PDF or raw parsed annual-report text introduced.

## Validation

Commands run:

```bash
git diff --check -- docs/reviews/mvp-multi-year-annual-evidence-scope-design-20260603.md docs/reviews/mvp-multi-year-annual-evidence-scope-design-review-fix-evidence-20260603.md
```

Result: pass. Command exited `0` with no output.

```bash
rg -n "requirement_availability|fallback_years|source_year_anchor_ids|ReportDataGap|target_year|max_years|identity_mismatch" docs/reviews/mvp-multi-year-annual-evidence-scope-design-20260603.md docs/reviews/mvp-multi-year-annual-evidence-scope-design-review-fix-evidence-20260603.md
```

Result: pass. The search returned matches in both the revised design artifact and this fix evidence artifact, including `requirement_availability`, `fallback_years`, `source_year_anchor_ids`, `ReportDataGap`, `target_year`, `max_years`, and `identity_mismatch`.

## Secret Safety

This fix evidence artifact contains no API key, Authorization header, Bearer token, cookie, password, raw provider response, raw audit response, prompt body, writer draft body, repair draft body, hidden provider config value, raw PDF text, or raw parsed annual-report text.
