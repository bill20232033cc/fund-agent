# MVP multi-year annual evidence scope design re-review — AgentDS

## Worker Self-Check

- Role: AgentDS independent re-review worker, not controller.
- Gate: `MVP multi-year annual evidence scope design gate`.
- Classification: `heavy`, design/review only.
- Re-review target: `docs/reviews/mvp-multi-year-annual-evidence-scope-design-20260603.md` (after fix evidence applied).
- Fix evidence read: `docs/reviews/mvp-multi-year-annual-evidence-scope-design-review-fix-evidence-20260603.md`.
- Prior reviews read: `docs/reviews/mvp-multi-year-annual-evidence-scope-design-review-ds-20260603.md`, `docs/reviews/mvp-multi-year-annual-evidence-scope-design-review-mimo-20260603.md`.
- Required truth inputs read: `AGENTS.md`, `docs/design.md` (current implementation sections), `docs/implementation-control.md`, `docs/current-startup-packet.md`.
- Code inputs read: `fund_agent/fund/documents/models.py`, `fund_agent/fund/data_extractor.py`, `fund_agent/fund/chapter_facts.py`, `fund_agent/fund/report_evidence.py`.
- Actions intentionally not taken: no implementation, no commit, no push, no PR, no truth doc edits, no report mutation, no retained artifact mutation.
- Scope: verify all material prior review findings are addressed; flag any new blockers or scope leaks.

## Verdict

**PASS — all material findings addressed. No new blocking findings.**

All 10 DS findings and all 8 MiMo findings from prior reviews have been accepted and either fixed in the revised design or explicitly deferred with documented rationale. The revised design is internally consistent, respects all AGENTS.md boundary rules, correctly separates current facts from future design, and contains no scope leakage into quarterly/prospectus/provider-budget/score-loop/Ch2-split/raw-PDF/implementation territory.

## Finding Disposition Verification

### DS Findings (10/10 addressed)

| Finding | Verified fix location | Assessment |
|---|---|---|
| F1 optional prior-year fail-closed contradiction | §3 Fund Loading Boundary, failure semantics table | RESOLVED. Design now splits current-year blocking from optional prior-year per-year isolation: optional prior-year `schema_drift`/`identity_mismatch`/`integrity_error` marks that year `failed_closed`, blocks dependent cross-year claims, does not kill current-year report. |
| F2 requirement-sensitive availability missing | §6 EvidenceAvailability Integration | RESOLVED. `requirement_availability` added with `fee_trend`/`turnover_trend`/`holdings_trend`/`manager_continuity`/`performance_series` keys; coarse `1Y`/`3Y`/`5Y` derived from it. |
| F3 AnnualEvidenceScopeRequest precedence undefined | §2 Service Scope Declaration | RESOLVED. Construction-time validation added: `target_year` required, required/optional disjoint, `max_years` cap `1..5`, optional truncation from most distant first, canonical order specified. |
| F4 same-fund identity and fund_id mismatch | §1 Annual Evidence Scope | RESOLVED. Same-source `fund_id` consistency required when present; mismatch is `identity_mismatch` for affected year; cross-source comparison out of MVP scope. |
| F5 cumulative fallback provenance | §4 Future Typed Evidence Bundle, §5 Cross-Year Derived Facts | RESOLVED. `AnnualEvidenceFallbackSummary` with `fallback_years`/`fallback_year_count`/`primary_failure_categories`; `CrossYearDerivedFact` carries `fallback_provenance` caveat. |
| F6 AnnualEvidenceGap undefined | §4 Future Typed Evidence Bundle | RESOLVED. `ReportDataGap` reused or extended; `AnnualEvidenceGap` may be alias/specialization serializing into same gap truth; no third unrelated gap source. |
| F7 DocumentIdentityStatus mapping unclear | §4 Future Typed Evidence Bundle | RESOLVED. Explicit mapping: successful same-fund → `verified_annual_report`; identity_mismatch → `mismatch`; schema_drift/integrity_error/unavailable/missing → `source_failed` plus `ReportDataGap`. |
| F8 cross-year anchor provenance missing | §5 Cross-Year Derived Facts | RESOLVED. `CrossYearDerivedFact` includes `source_years` and `source_year_anchor_ids`; consumption requires source-year anchors. |
| F9 repeated NAV/drawdown risk | §7 Template And Agent Feed, planning slice 3 | RESOLVED. Prior-year extraction prefers annual-report-only summaries; repeated NAV/drawdown avoided unless later gate requires it. |
| F10 ReportEvidenceProjectionContext relationship | Current Fact 7, §4 Future Typed Evidence Bundle | RESOLVED. Current facts note single-year shape; bundle requires per-year `source_failure_category`/`fallback_used`/`primary_failure_category`/`document_identity_status`; bundle summaries derived from per-year fields. |

### MiMo Findings (8/8 addressed)

| Finding | Disposition | Assessment |
|---|---|---|
| F1 raw fund_code vs DocumentKey | Deferred with explicit planning implication | ACCEPTABLE. Service keeps explicit business fields; canonical per-year identity choice deferred to implementation. Service must not own repository `DocumentKey` construction. |
| F2 ChapterFactProvider contract unspecified | Accepted and fixed in §7 | RESOLVED. Extension contract must be defined before implementation; two acceptable approaches specified; public chapter ids preserved. |
| F3 Chapter 2 multi-year data source | Accepted and fixed in §6-§7 | RESOLVED. `performance_series` availability added; degradation rule requires available anchored years or explicit unavailable rows; no synthetic five-year table. |
| F4 AnnualEvidenceBundle vs ReportEvidenceBundle | Accepted and fixed in planning slice 4 | RESOLVED. `ReportDataGap` reuse, per-year projection context, bundle-level fallback summary, canonical anchor namespace specified. |
| F5 requirement-sensitive examples and coarse tier | Accepted and fixed in §6 | RESOLVED. Concrete requirement keys added; coarse `data_tier_availability` derived from `requirement_availability`. |
| F6 year ordering unspecified | Accepted and fixed in §1-§2 | RESOLVED. Canonical order: target year, then prior years descending; cross-year calculations may sort internally with explicit anchor ids. |
| F7 repository concurrency | Deferred as residual in §3 | ACCEPTABLE. Concurrency gated behind later implementation proof of safety; sequential loading acceptable for correctness-first MVP. |
| F8 force_refresh across years | Accepted as MVP clarification in §2 | ACCEPTABLE. Uniform application for MVP; per-year refresh deferred and prohibited from `extra_payload`. |

## Scope Leak Verification

Verified the following are present only in rejection/non-goals/residual contexts:

- **Raw PDF/text injection**: rejected in §1, §4, §7, non-goals, acceptance criteria, boundary mapping. No positive usage.
- **Quarterly/interim reports**: deferred in §1, non-goals. No positive scope.
- **Prospectus/fund contract**: deferred in §1, non-goals. No positive scope.
- **Provider budget/score-loop**: deferred in non-goals, residual risk #5. No positive scope.
- **Ch2 split / 0+9 / 0+10**: rejected in non-goals, §7, acceptance criteria. Chapter ids remain `0-7`.
- **Implementation authorization**: explicitly denied in Worker Self-Check, non-goals, next handoff.
- **extra_payload**: prohibited in §2 (twice), boundary mapping.
- **New source strategy / direct Eastmoney/EID calls**: rejected in non-goals.
- **Cache/PDF helper exposure to Service/UI/Host**: prohibited in §3, boundary mapping.
- **Final judgment taxonomy change**: rejected in non-goals.
- **Template truth replacement**: rejected in Worker Self-Check, non-goals.

## Current Facts Accuracy

Re-verified the current facts section (lines 16-32) against live code:

- Fact 1: `FundDocumentRepository.load_annual_report(fund_code, year, force_refresh=...)` — confirmed in `documents/repository.py`. ✓
- Fact 2: `AnnualReportSourceMetadata` fields and 5-category failure taxonomy — confirmed in `documents/models.py:15-21,25-62`. ✓
- Fact 3: `FundDataExtractor.extract()` loads one report, builds one bundle — confirmed in `data_extractor.py`. ✓
- Fact 4: `StructuredFundDataBundle` is single-year — confirmed via `data_extractor.py` usage. ✓
- Fact 5: `ChapterFactProvider.project()` consumes single-year bundle — confirmed in `chapter_facts.py:432-457`. ✓
- Fact 6: Chapter 5 synthetic `cross_period_comparison_missing` — confirmed in `chapter_facts.py:1188-1199`. ✓
- Fact 7: `ReportEvidenceBundle` and `ReportEvidenceProjectionContext` are single-year shaped — confirmed in `report_evidence.py:571-653`. ✓
- Fact 8: `ReportDataGap` exists as typed gap truth — confirmed in `report_evidence.py:339-373`. ✓
- Fact 9: Current deterministic/LLM behavior unchanged — design-only gate, no code touched. ✓

## Boundary Rule Compliance

- UI→Service→Host→Agent→Fund layer mapping consistent with `AGENTS.md` and `docs/design.md`. ✓
- Service declares scope, does not load documents. ✓
- Fund loading goes only through `FundDocumentRepository`. ✓
- Host stays lifecycle-only, business-agnostic. ✓
- Agent consumes typed evidence, not raw PDFs. ✓
- No `dayu-agent`/`dayu.host`/`dayu.engine` runtime dependency. ✓
- All parameters typed and explicit; no `extra_payload`. ✓
- Fallback taxonomy preserved: `not_found`/`unavailable` eligible, `schema_drift`/`identity_mismatch`/`integrity_error` fail-closed. ✓

## Residual Risks (Post-Fix)

The following residual risks from the design remain acceptable for design acceptance:

1. **Identity continuity across share classes/mergers**: deferred to implementation-time rule. Same-`fund_code` baseline is sufficient for design gate.
2. **Historical schema drift in extractors**: fail-closed categories preserved; no relaxation.
3. **AnnualEvidenceBundle vs ReportEvidenceBundle duplication risk**: addressed by additive-wrapper requirement and canonical namespace in planning slice 4.
4. **Requirement-sensitive availability as truth source**: design now makes `requirement_availability` the truth and coarse tiers derived summaries.
5. **Provider prompt budget**: explicitly not tuned by this gate; summaries bounded, typed facts not raw text.
6. **Chapter 5 degradation**: explicit degrade wording deferred to typed contract implementation gate.
7. **Cross-year derived fact algorithms**: need per-fact tests; `source_years` and `source_year_anchor_ids` now required.
8. **ChapterFactProvider extension**: concrete contract required before coding; two allowed approaches specified.
9. **Multi-year concurrency and per-year refresh**: deferred until safety proven.

All nine are documented, bounded, and do not create blocking conditions for design acceptance.

## Non-Findings (Examined and Dismissed)

- No `DocumentIdentityStatus` overload concern: `source_failed` covers multiple states but is distinguished through per-year `failure_category` and `ReportDataGap` entries.
- No `force_refresh` uniform-application blocker: MVP simplification with documented deferral of per-year control.
- No concurrency pessimism concern: sequential-first is correct for correctness-first MVP; concurrency gated behind safety proof.
- No missing cross-source `fund_id` answer: explicitly out of MVP scope and documented.
- No hidden implementation leak: all "implementation" references in the design are to future planning slices or deferred decisions, not to current authorized work.
- No template chapter id drift: `0-7` preserved throughout.

## Validation

- `rg -n "requirement_availability\|source_year_anchor_ids\|fallback_years\|fallback_year_count\|ReportDataGap\|identity_mismatch\|target_year\|max_years\|failed_closed\|cross_year_facts\|performance_series\|DocumentIdentityStatus" docs/reviews/mvp-multi-year-annual-evidence-scope-design-20260603.md` — pass. All DS/MiMo fix terms present.
- `rg -n "quarterly\|prospectus\|score.loop\|provider.budget\|Ch2 split\|0\+9\|extra_payload\|raw (five-year\|5-year\|PDF\|text)" docs/reviews/mvp-multi-year-annual-evidence-scope-design-20260603.md` — pass. All scope-leak terms appear only in rejection/non-goals/residual contexts.
- `rg -n "implement\|code change\|commit\|push\|PR" docs/reviews/mvp-multi-year-annual-evidence-scope-design-20260603.md` — pass. All implementation references are to future planning slices; no current implementation authorized.
- Code cross-reference: `DocumentIdentityStatus` literals (`verified_annual_report`, `unverified`, `mismatch`, `source_failed`, `verified_as_annual_report_but_type_gap`) match design's mapping in §4. ✓
- Code cross-reference: `ReportDataGap` fields (`gap_id`, `gap_kind`, `chapter_ids`, `failure_category`, `reason_code`, `fallback_allowed`, `fallback_used`, `required_report_wording`, `blocks_claim_ids`) support the reuse described in §4. ✓
- Code cross-reference: `ChapterFactProjection` single-year shape with `fund_code`/`report_year`/`chapters` supports the extension claim in §7. ✓
- Code cross-reference: `AnnualReportSourceFailureCategory` five literals match design's fallback taxonomy. ✓
- `git diff --check -- docs/reviews/mvp-multi-year-annual-evidence-scope-design-20260603.md docs/reviews/mvp-multi-year-annual-evidence-scope-design-review-fix-evidence-20260603.md` — pass (previously confirmed by fix evidence).
- `git status --short -- docs/reviews/mvp-multi-year-annual-evidence-scope-design-20260603.md docs/reviews/mvp-multi-year-annual-evidence-scope-design-review-fix-evidence-20260603.md docs/reviews/mvp-multi-year-annual-evidence-scope-design-rereview-ds-20260603.md` — pass. Only allowed design, fix evidence, and this re-review files shown.

## Recommendation

The design is ready for controller judgment. All material review findings from both DS and MiMo prior reviews are addressed. No new blocking findings, scope leaks, or boundary violations detected. The 18 fixed/deferred findings are well documented in the fix evidence with explicit rationale. The 9 residual risks are appropriately bounded for a design-only gate.

Controller should verify:
- Whether the two deferred MiMo findings (F1 DocumentKey pattern, F7 concurrency) need explicit implementation-slice acceptance criteria or are adequately deferred.
- Whether the requirement-sensitive `requirement_availability` requirement keys (`fee_trend`/`turnover_trend`/`holdings_trend`/`manager_continuity`/`performance_series`) should be frozen as an MVP enum or kept extensible with `| str`.
- Whether the `AnnualEvidenceFallbackSummary` shape is sufficient or needs per-year `primary_failure_category` enrichment for writer/auditor consumption.

## Secret Safety

This re-review artifact contains no API key, Authorization header, Bearer token, cookie, password, raw provider response, raw audit response, prompt body, writer draft body, repair draft body, hidden provider config value, raw PDF text, or raw parsed annual-report text.
