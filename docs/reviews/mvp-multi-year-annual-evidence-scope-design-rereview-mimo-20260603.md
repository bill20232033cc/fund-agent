# MVP multi-year annual evidence scope design re-review — AgentMiMo

## Reviewer Self-Check

- Role: AgentMiMo independent re-review worker, not controller.
- Gate: `MVP multi-year annual evidence scope design gate`.
- Classification: `heavy`; design/review only.
- Scope: verify whether all material review findings are addressed without new blockers or scope leaks. No implementation, commit, push, PR, or mutation of retained artifacts.
- Review target (post-fix): `docs/reviews/mvp-multi-year-annual-evidence-scope-design-20260603.md`.
- Fix evidence: `docs/reviews/mvp-multi-year-annual-evidence-scope-design-review-fix-evidence-20260603.md`.
- Prior reviews: `docs/reviews/mvp-multi-year-annual-evidence-scope-design-review-ds-20260603.md`, `docs/reviews/mvp-multi-year-annual-evidence-scope-design-review-mimo-20260603.md`.
- Required read set: `AGENTS.md`, `docs/design.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md`, `fund_agent/fund/documents/models.py`, `fund_agent/fund/data_extractor.py`, `fund_agent/fund/chapter_facts.py`, `fund_agent/fund/report_evidence.py`.
- Source-of-truth discipline: findings are based on the post-fix design text against current code facts, accepted prior gate outputs, and the AGENTS.md boundary rules.

## Verdict

**PASS.** All material findings from the AgentDS review (F1-F10) and the AgentMiMo review (F1-F8) are addressed. No blocking findings. No scope leaks. No new blockers introduced by the fixes. The design is implementation-ready for its next handoff to an implementation planning gate.

## Finding Disposition Verification

### AgentDS Findings (F1-F10)

| DS Finding | Fix Claim | Re-review Verification | Status |
|---|---|---|---|
| F1 optional prior-year fail-closed contradiction | Split to per-year isolation; current-year continues | §3 failure handling table now says "Mark that year `failed_closed`; disallow dependent cross-year claims; current-year report may continue if no current-year impact." Failure semantics table rows for optional prior year `schema_drift`/`identity_mismatch`/`integrity_error` are consistent with `degradation_policy=current_year_required_prior_years_optional`. No contradiction remains. | Resolved |
| F2 requirement-sensitive availability missing from type shape | Added `requirement_availability` keyed by fact category | §6 now defines `RequirementAvailability` with `requirement_key`, `status_by_tier`, `source_years_by_tier`, `blocked_years_by_tier`, `data_gap_refs`. Coarse `data_tier_availability` is explicitly derived, not independently asserted. | Resolved |
| F3 `AnnualEvidenceScopeRequest` precedence undefined | Added construction-time validation | §2 now specifies: `target_year` required, `required_years` must contain `target_year`, required/optional disjoint, `max_years` cap `1..5`, optional truncate from most distant first, canonical order target-year-then-descending. | Resolved |
| F4 same-fund identity `fund_id` mismatch | Added same-source `fund_id` consistency check | §1 and §3 now specify: same `fund_code` always; `fund_id` consistency compared only within same source when present; same-source mismatch is `identity_mismatch` for affected year; cross-source comparison not required for MVP. | Resolved |
| F5 cumulative fallback provenance | Added `AnnualEvidenceFallbackSummary` | §4 defines `AnnualEvidenceFallbackSummary(fallback_years, fallback_year_count, primary_failure_categories)`. §5 `CrossYearDerivedFact` carries `fallback_provenance` field. | Resolved |
| F6 `AnnualEvidenceGap` undefined | Reuse/extend `ReportDataGap` | §4 explicitly states: "`AnnualEvidenceGap` may be a local alias or typed specialization over `ReportDataGap`, but it must serialize into the same gap truth and must not create a third unrelated source of gap semantics." | Resolved |
| F7 `DocumentIdentityStatus` mapping unclear | Added MVP mapping | §4 now specifies: successful same-fund → `verified_annual_report`; `identity_mismatch` → `mismatch`; `schema_drift`/`integrity_error`/source failure → `source_failed` plus `ReportDataGap`; unavailable/missing optional → `source_failed` with gap. | Resolved |
| F8 cross-year anchor provenance missing | Added `source_year_anchor_ids` | §5 `CrossYearDerivedFact` conceptual shape now includes `source_years` and `source_year_anchor_ids`. Constraint: "A derived fact with no source-year anchors is not eligible for writer/auditor consumption." | Resolved |
| F9 repeated NAV/drawdown risk | Prior-year extraction prefers annual-report-only | §7 explicitly states: "Prior-year extraction should prefer annual-report-only summaries. It should avoid repeated NAV loading and bond drawdown calculations for every prior year unless a later gate explicitly requires multi-year NAV or drawdown evidence." Planning slice 3 confirms. | Resolved |
| F10 `ReportEvidenceProjectionContext` relationship missing | Per-year context fields, bundle summaries | §4 now specifies: "The current single-year `ReportEvidenceProjectionContext` must not be stretched into a misleading bundle-wide field. Multi-year projection needs per-year `source_failure_category`, `fallback_used`, `primary_failure_category`, and `document_identity_status`, with bundle-level summaries derived from those per-year fields." | Resolved |

### AgentMiMo Findings (F1-F8)

| MiMo Finding | Fix Claim | Re-review Verification | Status |
|---|---|---|---|
| F1 raw `fund_code` vs `DocumentKey` pattern | Deferred with planning implication | Accepted. Service keeps explicit user/business scope fields; canonical per-year document identity remains implementation-slice work because Service must not own repository `DocumentKey` construction. This is an implementation decision, not a design blocker. | Deferred (acceptable) |
| F2 cross-year `ChapterFactProvider` contract unspecified | Added explicit pre-implementation requirement | §7 now states: "`ChapterFactProvider` extension must be explicit before implementation. Acceptable MVP options are either an additive multi-year projection provider that consumes `AnnualEvidenceBundle`, or an extension of `ChapterFactProjection` that adds Chapter 5 cross-year facts while preserving public chapter ids `0-7`." | Resolved |
| F3 Chapter 2 multi-year R=A+B-C data source | Added `performance_series` availability and degradation rule | §7 now states: "If `performance_series` availability is partial, Chapter 2 must degrade the table to available anchored years or mark unavailable rows explicitly; it must not synthesize a five-year R=A+B-C table from missing years." | Resolved |
| F4 `AnnualEvidenceBundle` vs `ReportEvidenceBundle` relationship | Added `ReportDataGap` reuse and canonical anchor namespace | §4 specifies `ReportDataGap` reuse, per-year projection context fields, bundle-level fallback summary. Planning slice 4 requires canonical anchor id namespace. | Resolved |
| F5 requirement-sensitive examples and coarse tier relationship | Added concrete requirement keys; coarse tier is derived | §6 now defines `RequirementAvailability` with explicit `requirement_key` literals (`fee_trend`, `turnover_trend`, `holdings_trend`, `manager_continuity`, `performance_series`). "Coarse `data_tier_availability` for `1Y`/`3Y`/`5Y` is a derived summary over `requirement_availability`, not an independent truth source." | Resolved |
| F6 year ordering unspecified | Added canonical order | §1 specifies: "MVP deterministic order is most-recent first for request planning and presentation summaries, while cross-year calculations may internally sort ascending when computing deltas as long as anchor ids and source years remain explicit." §2 specifies canonical request order. | Resolved |
| F7 repository concurrency | Deferred as residual | §3: "Multi-year loading may use concurrency only after an implementation gate proves repository/cache/source adapters are safe under concurrent access and without changing provider/runtime budgets. Sequential loading is acceptable for correctness-first MVP planning." Residual risk #9 confirms. | Deferred (acceptable) |
| F8 `force_refresh` semantics across years | MVP clarification; granular control deferred | §2: "MVP `force_refresh` applies uniformly to all requested years if present. More granular per-year refresh is deferred; it must not be hidden in `extra_payload`." | Resolved |

## Scope Leak Verification

| Scope Item | Expected Disposition | Verification |
|---|---|---|
| Raw PDF/text injection to LLM | Rejected | §Non-Goals and §7: "Agent/tool-loop consumes typed inputs. It must not consume raw PDFs or raw five-year extracted text in prompts." Pass. |
| Quarterly reports | Deferred | §Non-Goals: "No quarterly reports or interim reports." Pass. |
| Prospectus / fund contract | Deferred | §Non-Goals: "No prospectus or fund contract evidence scope." Pass. |
| Provider budget tuning | Deferred | §Non-Goals: "No provider budget tuning or timeout attribution change." Residual risk #5. Pass. |
| Score-loop wiring | Deferred | §Non-Goals: "No chapter generation score-loop or golden/readiness mutation." Pass. |
| Ch2 split / public chapter count | Rejected | §Non-Goals: "No public chapter id changes, no Ch2 split, no `0+9` / `0+10`." §7 confirms Chapter 2 uses performance breakdown inside chapter id 2 only. Pass. |
| Extra payload leakage | Rejected | §2: "No scope parameter may be hidden in `extra_payload`." Pass. |
| Direct Eastmoney/EID API calls | Rejected | §Non-Goals: "No new annual-report source strategy and no direct Eastmoney/EID API calls outside existing repository/source orchestration." Pass. |
| Cache/PDF helper APIs exposed | Rejected | §Non-Goals: "No cache/PDF helper APIs exposed to Service/UI/Host/renderer/quality gate." Pass. |
| Implementation code | Not authorized | §Non-Goals: "No implementation in this gate." Design-only artifact. Pass. |
| Template truth replacement | Not authorized | §Non-Goals: "No direct template truth replacement and no edit to `docs/fund-analysis-template-draft.md`." Pass. |
| Final judgment taxonomy change | Not authorized | §Non-Goals: "No final judgment taxonomy change." Pass. |

## Residual Risks After Fixes

The following residual risks survive from the original design and are explicitly acknowledged:

1. **Identity continuity across share class changes / fund mergers** (§Residual #1): MVP requires same `fund_code`; same-source `fund_id` mismatch is `identity_mismatch`; cross-source `fund_id` comparison is out of scope. Acceptable for MVP.

2. **Historical schema differences in extractors** (§Residual #2): Source/contract issue, not a prompt issue; fail-closed categories stay intact. Acceptable.

3. **`AnnualEvidenceBundle` parallel truth source risk** (§Residual #3): Design explicitly makes it an additive wrapper with one canonical anchor id namespace and `ReportDataGap` reuse. Risk is mitigated by design; implementation must follow.

4. **`requirement_availability` precision vs coarse tiers** (§Residual #4): Design makes requirement_availability the truth and coarse tiers derived. Implementation must enforce this.

5. **Provider prompt budget impact** (§Residual #5): Gate deliberately does not tune budget. Future implementation must keep summaries bounded. Acceptable deferral.

6. **Chapter 5 contract degrade wording** (§Residual #6): Needs explicit degrade wording and audit rules in a later typed contract implementation gate. Acceptable deferral.

7. **Cross-year derived fact algorithms** (§Residual #7): Need per-fact tests and same-source anchor checks. The design requires `source_years` and `source_year_anchor_ids` which constrains implementation.

8. **ChapterFactProvider extension contract** (§Residual #8): Design now requires explicit definition before implementation. This is a pre-implementation gate requirement, not a design gap.

9. **Multi-year repository concurrency** (§Residual #9): Deferred. Sequential loading is acceptable for correctness-first MVP. Acceptable.

10. **MiMo F1 deferred: canonical per-year document identity** (MiMo §F1): Implementation-slice decision. Service scope declaration uses explicit business fields; repository identity is internal. Acceptable deferral.

## Non-Findings (Verified Unchanged)

The following aspects remain correct after fixes:

1. **FundDocumentRepository boundary**: All annual report access through `FundDocumentRepository.load_annual_report()`. No bypass. Matches current code and AGENTS.md.
2. **Fallback taxonomy**: Five-category taxonomy (`not_found`, `unavailable`, `schema_drift`, `identity_mismatch`, `integrity_error`) correctly preserved. Matches `models.py:15-21`.
3. **Chapter ids remain 0-7**: No public chapter expansion. Matches template typed contract gate acceptance.
4. **Current facts accuracy**: All 9 current fact statements verified against code. `StructuredFundDataBundle` is single-year. `ChapterFactProvider.project()` consumes single-year bundle. Chapter 5 has synthetic `cross_period_comparison_missing` fact. `ReportEvidenceBundle` is single-year. `ReportDataGap` exists with rich fields. `ReportEvidenceProjectionContext` is single-year shaped.
5. **Boundary mapping table**: Correctly assigns responsibilities per layer. Consistent with AGENTS.md UI→Service→Host→Agent model.
6. **Acceptance criteria**: All 13 criteria in §Acceptance Criteria are satisfied by the post-fix design.

## Validation

- `rg -n "requirement_availability|fallback_years|source_year_anchor_ids|ReportDataGap|target_year|max_years|identity_mismatch|AnnualEvidenceFallbackSummary|AnnualEvidenceScopeRequest|AnnualEvidenceBundle" docs/reviews/mvp-multi-year-annual-evidence-scope-design-20260603.md` — pass. All fix-evidence required terms are present in the revised design artifact.
- `rg -n "raw five-year PDF|raw 5-year PDF|raw PDF text|raw multi-year" docs/reviews/mvp-multi-year-annual-evidence-scope-design-20260603.md` — pass. Raw PDF injection is rejected.
- `rg -n "quarterly|prospectus|fund.contract|score-loop|Ch2 split|0\+9|0\+10|provider budget" docs/reviews/mvp-multi-year-annual-evidence-scope-design-20260603.md` — pass. All deferred/rejected in non-goals.
- `rg -n "extra_payload" docs/reviews/mvp-multi-year-annual-evidence-scope-design-20260603.md` — pass. Explicitly prohibited.
- Code cross-reference: `fund_agent/fund/documents/models.py:15-21` — `AnnualReportSourceFailureCategory` five-category taxonomy confirmed.
- Code cross-reference: `fund_agent/fund/report_evidence.py:39-45` — `DocumentIdentityStatus` literals confirmed (`verified_annual_report`, `unverified`, `mismatch`, `source_failed`, `verified_as_annual_report_but_type_gap`).
- Code cross-reference: `fund_agent/fund/report_evidence.py:106-132` — `GapKind`, `GapFailureCategory`, `DataGapReasonCode` confirmed; `ReportDataGap` exists with rich gap semantics.
- Code cross-reference: `fund_agent/fund/data_extractor.py:44-53` — `FundDocumentRepository.load_annual_report(fund_code, year, force_refresh=...)` async signature confirmed.
- Code cross-reference: `fund_agent/fund/chapter_facts.py:1188-1199` — Chapter 5 synthetic `cross_period_comparison_missing` fact confirmed.
- Fix evidence disposition table: all 17 entries (DS F1-F10, MiMo F1-F8) have explicit disposition and fix evidence. No entry is marked "rejected" or "unaddressed".

## Secret Safety

This review artifact contains no API key, Authorization header, Bearer token, cookie, password, raw provider response, raw audit response, prompt body, writer draft body, repair draft body, hidden provider config value, raw PDF text, or raw parsed annual-report text.
