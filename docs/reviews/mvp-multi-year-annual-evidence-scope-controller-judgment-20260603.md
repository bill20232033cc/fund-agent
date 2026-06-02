# MVP multi-year annual evidence scope controller judgment

## Controller Self-Check

- Role: phaseflow controller.
- Gate: `MVP multi-year annual evidence scope design gate`.
- Classification: heavy.
- Scope: design/review only; no implementation authorized.
- Inputs reviewed: design artifact, DS/MiMo reviews, design-fix evidence, DS/MiMo re-reviews, `AGENTS.md`, `docs/design.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md`, and local Fund document/evidence model code facts.
- Actions intentionally not taken: no source/test/config/runtime/provider/auditor/template/score-loop/golden/readiness edit, no quarterly evidence scope, no direct raw PDF/text prompt path, no PR/push.

## Judgment

**Accepted as design-only future annual evidence scope architecture.** The gate has design, independent review, fix, independent re-review, and controller judgment. It does not change current runtime behavior.

Accepted future design:

- MVP annual evidence scope is `target_year` plus up to four immediately preceding annual reports, capped at `max_years=5`, bounded by availability and same-fund identity.
- Current public chapter ids remain `0-7`; multi-year evidence feeds Chapter 5 and internal Chapter 2/3 requirements without public chapter split.
- Service may declare annual evidence scope through explicit typed fields such as `AnnualEvidenceScopeRequest`; Service must not call `FundDocumentRepository`, PDF cache, source helpers, parsers, or filesystem paths.
- `AnnualEvidenceScopeRequest` validation is accepted as future design: target year required, required/optional years disjoint, `max_years` hard cap `1..5`, optional years truncated from most distant first, deterministic canonical order.
- Fund owns loading and projection: every annual report must be loaded through `FundDocumentRepository.load_annual_report(fund_code, year, force_refresh=...)`.
- Same-fund identity requires matching requested `fund_code`; same-source `fund_id` is compared only when present across years; mismatch is `identity_mismatch` for the affected year. Cross-source `fund_id` comparison is deferred.
- Optional prior-year `not_found` / `unavailable` produce typed year-level gaps/degradation. Optional prior-year `schema_drift` / `identity_mismatch` / `integrity_error` fail closed for that year's evidence and block dependent cross-year claims, but do not kill the current-year report unless the current year or a future required prior year is affected.
- Target-year failure remains fail-closed for report evidence.
- Future annual evidence bundle is additive: current-year `StructuredFundDataBundle` remains canonical, with year-indexed annual evidence records, source documents, anchors, `ReportDataGap` reuse, per-year availability, cross-year derived facts, and explicit degradation semantics.
- Requirement-sensitive `requirement_availability` is the truth for annual evidence availability; coarse `1Y` / `3Y` / `5Y` summaries are derived and cannot be used independently.
- Cross-year derived facts must carry `source_years` and `source_year_anchor_ids`; facts without source-year anchors are not eligible for writer/auditor consumption.
- Bundle-level fallback provenance is accepted: fallback years/count/categories must be visible, and cross-year facts using fallback years carry a caveat.
- Prior-year extraction should prefer annual-report-only summaries and avoid repeated NAV/drawdown work unless a later gate accepts multi-year NAV/drawdown evidence.

Rejected / deferred for this gate:

- No implementation, loading code, extractor change, Agent runtime change, provider budget tuning, score-loop wiring, quality/golden/readiness mutation, or template truth replacement.
- No quarterly/interim reports, prospectus, fund contract, fact sheets, third-party pages, or new annual-report source strategy.
- No raw five-year PDF text or raw five-year parsed text to LLM.
- No Ch2 public split, public chapter count change, `0+9`, or `0+10`.
- No direct Eastmoney/EID calls outside existing repository/source orchestration.
- No cache/PDF helper APIs exposed to Service/UI/Host/renderer/quality gate.

## Review Disposition

DS first review: PASS-WITH-FINDINGS. Material findings around optional prior-year fail-closed semantics, requirement-sensitive availability, request validation, identity, fallback provenance, gap model, identity-status mapping, anchor provenance, NAV/drawdown repetition, and projection context were accepted and fixed.

MiMo first review: PASS with non-blocking findings. Cross-year `ChapterFactProvider` contract, Ch2 degradation path, `AnnualEvidenceBundle` / `ReportEvidenceBundle` relationship, coarse availability semantics, year ordering, concurrency, and `force_refresh` behavior were fixed or explicitly deferred.

DS re-review: PASS, all material findings addressed, no new blocking findings.

MiMo re-review: PASS, all material findings addressed, no blocking findings, no scope leaks.

Accepted residuals for future implementation planning:

- Canonical per-year document identity type (`DocumentKey` vs narrower identity) must be decided without moving repository concerns into Service.
- Multi-year repository concurrency is deferred until cache/source adapter safety is proven.
- Requirement keys may start with accepted MVP keys but should remain extensible only through typed schema, not free prompt text.
- Chapter 5 degrade wording and audit rules need a later typed contract implementation gate.
- Cross-year derived fact algorithms need per-fact tests and anchor/gap-aware denominators.
- `ChapterFactProvider` extension contract must be accepted before implementation.

## Acceptance Evidence

| Purpose | Artifact |
|---|---|
| Design artifact | `docs/reviews/mvp-multi-year-annual-evidence-scope-design-20260603.md` |
| DS review | `docs/reviews/mvp-multi-year-annual-evidence-scope-design-review-ds-20260603.md` |
| MiMo review | `docs/reviews/mvp-multi-year-annual-evidence-scope-design-review-mimo-20260603.md` |
| Fix evidence | `docs/reviews/mvp-multi-year-annual-evidence-scope-design-review-fix-evidence-20260603.md` |
| DS re-review | `docs/reviews/mvp-multi-year-annual-evidence-scope-design-rereview-ds-20260603.md` |
| MiMo re-review | `docs/reviews/mvp-multi-year-annual-evidence-scope-design-rereview-mimo-20260603.md` |

## Next Entry Point

Per phase sequencing, the next gate is `MVP provider runtime budget calibration gate`.

Scope guard for that next gate:

- Re-evaluate Ch2/Ch4/Ch6 timeout using accepted typed template/evidence/Agent execution boundaries and retained artifacts.
- Provider runtime budget calibration may evaluate split-audit, PASS-only audit, or timeout PoC only as design/plan evidence first.
- It must not precede or rewrite accepted typed contract decisions.
- It must not loosen auditor/fail-closed semantics, introduce deterministic fallback for incomplete LLM results, or alter golden/quality/readiness/score-loop semantics.

## Validation

- DS/MiMo re-reviews — pass with no blocking findings.
- `git diff --check` over the design/fix artifacts — pass per fix evidence and re-review.

## Secret Safety

This judgment contains no API key, Authorization header, Bearer token, cookie, password, raw provider response, raw audit response, prompt body, writer draft body, repair draft body, hidden provider config value, raw PDF text, or raw parsed annual-report text.
