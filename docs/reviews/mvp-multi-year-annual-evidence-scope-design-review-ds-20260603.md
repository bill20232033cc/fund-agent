# MVP multi-year annual evidence scope design review — AgentDS

## Worker Self-Check

- Role: AgentDS independent design reviewer, not controller.
- Gate: `MVP multi-year annual evidence scope design gate`.
- Classification: `heavy`; design/review only.
- Scope: adversarial design review only. No implementation, commit, push, PR, or mutation of retained artifacts.
- Target: `docs/reviews/mvp-multi-year-annual-evidence-scope-design-20260603.md`.
- Required read set: `AGENTS.md`, `docs/design.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md`, `docs/fund-analysis-template-draft.md`, prior controller judgments (template typed contract, Agent engine/tool-loop), `fund_agent/fund/documents/repository.py`, `fund_agent/fund/documents/models.py`, `fund_agent/fund/data_extractor.py`, `fund_agent/fund/chapter_facts.py`, `fund_agent/fund/report_evidence.py`.
- Source-of-truth discipline: findings are based on the design text against current code facts, accepted prior gate outputs, and the AGENTS.md boundary rules.

## Verdict

**PASS-WITH-FINDINGS.** The design correctly identifies the core problem (single-year `StructuredFundDataBundle` cannot support Chapter 5 cross-period claims), correctly bounds the MVP scope to annual reports only, correctly rejects raw PDF injection and quarterly/provider-budget/score-loop/Ch2-split leakage, and correctly routes all loading through `FundDocumentRepository`. No finding is blocking for design acceptance, but several material ambiguities must be resolved before an implementation planning gate can proceed.

## Findings

### Finding 1 — [Material] Optional prior year fail-closed semantics contradict degradation policy

**Severity**: Material

The failure semantics table states:

> Optional prior year `schema_drift` → Fail closed for the multi-year evidence run; do not mask as missing
> Optional prior year `identity_mismatch` → Fail closed for the multi-year evidence run; same-fund identity is broken
> Optional prior year `integrity_error` → Fail closed for the multi-year evidence run; do not use corrupted evidence

But the `AnnualEvidenceScopeRequest.degradation_policy` is `current_year_required_prior_years_optional`, which implies current-year chapters can survive prior-year failures. If a prior year triggers `schema_drift`, the design says the entire multi-year run fails closed—but the degradation policy says prior years are optional.

The design must clarify: does an optional prior year `schema_drift`/`identity_mismatch`/`integrity_error`:
- (a) Fail the entire run (no report generated), or
- (b) Fail only the multi-year evidence scope (current-year chapters survive, Chapter 5 degrades with `prior_year_failed_closed` gap), or
- (c) Fail only the affected year's evidence (other prior years survive)?

Option (a) contradicts `prior_years_optional`. Option (b) is the most consistent with the degradation policy but the table doesn't say it. Option (c) is the safest but requires per-year failure isolation not described in the design.

**Recommendation**: Split the failure semantics by scope. Optional prior year `schema_drift`/`identity_mismatch`/`integrity_error` should fail-closed for that year's evidence and prevent cross-year claims that depend on it, but should not kill the current-year report unless the current year itself is affected. The table should be updated with an explicit "affects only this prior year's evidence; cross-year claims that require this year are disallowed" column.

### Finding 2 — [Material] Requirement-sensitive availability is not supported by proposed `EvidenceAvailability` types

**Severity**: Material

The design claims:

> Availability is requirement-sensitive. For example, fee trend may be available across more years than holdings-style trend if holdings extraction failed or was not reviewed for a prior year.

This is the most innovative semantic in the availability design. However, the proposed `EvidenceAvailability` type only has:

```python
data_tier_availability: Mapping[Literal["1Y", "3Y", "5Y"], AvailabilityStatus]
year_availability: Mapping[int, AnnualYearAvailability]
```

Neither field carries per-requirement (per-fact-type) availability. A consumer looking at `data_tier_availability["5Y"] == "available"` cannot know whether that means "all 5 years have fee data" or "all 5 years have fee data AND holdings data AND manager data."

The per-year `AnnualYearEvidence` carries `data_gaps` and `bundle: StructuredFundDataBundle | None`, but the requirement-sensitive availability needs to be derived from which specific facts are present in which years. This derivation is not described, and the `EvidenceAvailability` type cannot express its output.

**Recommendation**: Either (a) add a `requirement_availability: Mapping[str, YearTierAvailability]` field keyed by fact category (e.g., `"fee_trend"`, `"holdings_trend"`, `"turnover_trend"`) to `EvidenceAvailability`, or (b) explicitly defer requirement-sensitive availability to a later gate and simplify MVP `EvidenceAvailability` to coarse year-tier flags with a documented limitation. Option (b) is safer for MVP scope.

### Finding 3 — [Material] `AnnualEvidenceScopeRequest` field precedence is undefined

**Severity**: Material

The design proposes:

```python
AnnualEvidenceScopeRequest(
    required_years: tuple[int, ...],
    optional_years: tuple[int, ...],
    max_years: int,
    ...
)
```

With the constraint: "optional_years should contain prior years up to target_year - 4, bounded by max_years."

Questions the design doesn't answer:
- If `len(required_years) + len(optional_years) > max_years`, which years are dropped? From `optional_years`? From the end? From the beginning?
- If `target_year not in required_years`, is that a construction error or a valid scope (e.g., a historical-only analysis)?
- If a year appears in both `required_years` and `optional_years`, is that an error? The types allow it since both are `tuple[int, ...]`.
- Is `max_years` a hard cap or a default? The design says both "default and maximum 5" for the annual scope (section 1) but the request type treats it as a parameter.

**Recommendation**: Add explicit validation rules. At minimum: `required_years` must contain `target_year`; `required_years ∪ optional_years` must be disjoint; if the union exceeds `max_years`, truncate `optional_years` from the most distant year first; `max_years` is the absolute cap regardless of what Service requests.

### Finding 4 — [Material] Same-fund identity check relies on `fund_code` alone; `fund_id` mismatch across sources is unaddressed

**Severity**: Material

The design specifies:

> `same_fund_identity`: every loaded annual report must match the requested fund identity and report year through repository/source metadata and parsed document key.

Current `AnnualReportSourceMetadata` carries both `fund_code: str | None` and `fund_id: str | None` (platform-specific identifier from EID/Eastmoney). A cross-source scenario is possible where `fund_code` matches but `fund_id` differs—e.g., the fund changed its platform ID between years, or a fallback source returned a different platform's record for the same fund code.

The design's residual risk #1 acknowledges "identity continuity across fund share classes, fund name changes, fund mergers, or converted products" but doesn't address the `fund_code` vs `fund_id` divergence within the same source ecosystem.

The current `DocumentKey` is `(fund_code, year, document_kind)`. The repository validates `fund_code`. But the source metadata's `fund_id` is not validated against the requesting `fund_code` in the current code path—the source orchestrator (inside the PDF adapter) may return a document whose `fund_code` metadata field matches but whose `fund_id` differs from prior years.

**Recommendation**: Add an explicit identity contract: the repository must verify that each loaded annual report's source metadata `fund_code` matches the requested fund code (already done) AND that if multiple years are loaded, their `fund_id` values (when present and from the same source) are consistent. Inconsistency in `fund_id` across years from the same source should be treated as `identity_mismatch` for the affected prior year. Cross-source `fund_id` comparison (EID vs Eastmoney) is not required for MVP.

### Finding 5 — [Material] Multi-year fallback provenance has no cumulative semantics

**Severity**: Material

The design says: "Repository fallback remains internal to the repository/source orchestration. If fallback succeeds, metadata such as `fallback_used=True` and `primary_failure_category` must be retained."

When loading 5 annual reports, each may independently use fallback. The design doesn't address whether:
- 5/5 years via fallback is semantically different from 0/5.
- A mixed scenario (2 years official source, 3 years fallback) should affect cross-year fact confidence or Chapter 5 degradation.
- The cumulative fallback metadata should be surfaced in `AnnualEvidenceBundle` degradation or `EvidenceAvailability`.

Current `AnnualYearEvidence` has `fallback_used: bool` per year, which is necessary but not sufficient—there's no bundle-level `fallback_summary` or degradation flag.

**Recommendation**: Add a bundle-level fallback summary (e.g., `fallback_year_count`, `fallback_years: tuple[int, ...]`). Cross-year facts derived primarily from fallback years should carry a `fallback_provenance` caveat. This doesn't need to block claims, but it should be visible to writers and auditors.

### Finding 6 — [Minor] `AnnualEvidenceGap` is referenced but not defined

**Severity**: Minor

`AnnualEvidenceBundle` declares `data_gaps: tuple[AnnualEvidenceGap, ...]` and `AnnualYearEvidence` declares `data_gaps: tuple[AnnualEvidenceGap, ...]`, but `AnnualEvidenceGap` is never defined in the design. The current code has `ReportDataGap` in `report_evidence.py` with rich fields (`gap_kind`, `failure_category`, `reason_code`, `required_report_wording`, etc.).

The design should either define `AnnualEvidenceGap` or explicitly state that it reuses/extends `ReportDataGap`. If a new type is intended, its relationship to `ReportDataGap` and `AnnualEvidenceGap` at the year level vs bundle level must be specified.

**Recommendation**: Either alias `AnnualEvidenceGap = ReportDataGap` for MVP, or define a narrower type that carries only the fields needed at the annual evidence layer. Avoid introducing a third gap type without clear semantics.

### Finding 7 — [Minor] `AnnualYearEvidence` uses `DocumentIdentityStatus` from `report_evidence.py` without mapping

**Severity**: Minor

The `AnnualYearEvidence.identity_status` field uses `DocumentIdentityStatus` from `report_evidence.py`, which has these literals: `verified_annual_report`, `unverified`, `mismatch`, `source_failed`, `verified_as_annual_report_but_type_gap`.

For multi-year evidence, the mapping is not obvious:
- If a prior year loaded successfully from EID with matching `fund_code`, is it `verified_annual_report`? The design requires "same-fund identity" but `verified_annual_report` in the current code means the document exists and was parsed, not that it was cross-referenced against other years.
- Is `unverified` the right status for a year that hasn't been cross-checked yet?
- `source_failed` overlaps with `AnnualYearEvidence.status == "failed_closed"` and `failure_category`.

**Recommendation**: Either define multi-year-specific identity statuses (e.g., `same_fund_verified`, `cross_year_ambiguous`) or clarify the mapping from current `DocumentIdentityStatus` values to multi-year semantics.

### Finding 8 — [Minor] Cross-year derived fact algorithms have no anchor provenance requirements

**Severity**: Minor

The design lists allowed cross-year derived facts (fee schedule changes, turnover trend, holdings concentration change, etc.) and says they should be "derived only from available typed yearly evidence." But it doesn't specify that each derived cross-year fact must carry anchors back to the source years' evidence.

Example: "fee increased from 1.2% to 1.5% between 2021 and 2024" should anchor to `AnnualYearEvidence[2021].bundle.fee_schedule` and `AnnualYearEvidence[2024].bundle.fee_schedule`, not just to the derived `CrossYearDerivedFact` itself.

Residual risk #7 mentions "Cross-year derived fact algorithms need per-fact tests and same-source anchor checks," which is correct but should be elevated to a design requirement: every `CrossYearDerivedFact` must carry `source_year_anchor_ids` that reference the source years' evidence anchors.

**Recommendation**: Add `source_year_anchor_ids: tuple[str, ...]` to the `CrossYearDerivedFact` conceptual shape, with the constraint that every cross-year fact must be traceable to its source years' typed evidence.

### Finding 9 — [Minor] Current-year `StructuredFundDataBundle` construction is not additive; multi-year loading may conflict with existing single-year assumptions

**Severity**: Minor

The design proposes an additive wrapper (`AnnualEvidenceBundle`) around the current-year `StructuredFundDataBundle`. This is the correct approach. However, the current `FundDataExtractor.extract()` always calls `self._repository.load_annual_report(fund_code, report_year)` and constructs exactly one bundle. For multi-year loading, a new loading path would need to call the repository once per year and construct N bundles.

The design's Slice 3 says "produce per-year `StructuredFundDataBundle` or narrower `AnnualYearEvidenceSummary` from parsed annual reports, reusing current extractors where valid." This is reasonable, but the current `FundDataExtractor` also calls `_load_nav_data_or_unavailable` and `_load_drawdown_metric_for_bond_fund` per extraction. For a 5-year run, that would mean 5 NAV calls and up to 5 bond drawdown calculations. The design doesn't discuss whether this is acceptable or whether NAV/drawdown should be loaded once for the current year and only annual-report extraction repeated for prior years.

**Recommendation**: Clarify in the implementation planning slices that prior-year extraction should use only annual-report extractors (profile, performance, manager, holdings) and skip NAV/drawdown unless a later gate specifically requires multi-year NAV for cross-year performance claims.

### Finding 10 — [Minor] The design's "current facts" section misses one code fact about `ReportEvidenceBundle`

**Severity**: Minor

Current Fact 7 states: "Current `ReportEvidenceBundle` is also projected from one `StructuredFundDataBundle`." This is correct but incomplete. The current `project_report_evidence_bundle()` also takes a `ReportEvidenceProjectionContext` that carries `corpus_id`, `source_boundary`, `source_failure_category`, `fund_type_slot`, `document_identity_status`, `fallback_used`, and other fields. The design's future `AnnualEvidenceBundle` would need to either consume or replace some of this context. The design doesn't discuss the relationship between `ReportEvidenceProjectionContext` (current) and the multi-year loading context (future).

**Recommendation**: In the implementation planning gate, add a slice that explicitly addresses how `ReportEvidenceProjectionContext` fields relate to multi-year annual evidence loading, particularly `source_failure_category` (which is currently singular) and `fallback_used` (which is currently a single boolean).

## Design Strengths

The following aspects of the design are correct and well-bounded:

1. **Repository-only loading**: Every annual report goes through `FundDocumentRepository.load_annual_report()`. No bypass, no raw filesystem access. This is consistent with AGENTS.md constraints.

2. **Raw PDF rejection**: The design explicitly and repeatedly rejects feeding raw 5-year PDF/text to LLM prompts. This is the correct safety boundary.

3. **Scope discipline**: Quarterly reports, prospectus, fund contract, provider budget, score-loop, Ch2 split, and public chapter id changes are all explicitly deferred or rejected. The non-goals section is comprehensive.

4. **Fallback taxonomy preservation**: The existing `not_found`/`unavailable` eligible vs `schema_drift`/`identity_mismatch`/`integrity_error` fail-closed taxonomy is correctly carried forward into the multi-year design.

5. **Chapter 5 degradation awareness**: The design correctly recognizes that Chapter 5 needs explicit degrade semantics and that partial prior-year availability must not produce fake cross-year claims.

6. **Additive wrapper approach**: Using `AnnualEvidenceBundle` as an additive wrapper over the current-year `StructuredFundDataBundle` is the correct architectural choice to avoid creating a parallel truth source.

7. **`EvidenceAvailability` not a tool**: The design correctly repeats the accepted prior gate decision that `EvidenceAvailability` is a precomputed derived input, not a ToolRegistry tool.

8. **Service scope declaration without loading**: Service declares what evidence is needed through typed fields but does not touch repository/cache internals. This respects the AGENTS.md boundary.

9. **Boundary mapping**: The layer-by-layer responsibility table is consistent with the accepted UI→Service→Host→Agent→Fund boundary model.

## Non-Findings

The following concerns were examined and do NOT constitute findings:

- **Current code is unchanged**: Confirmed. The design correctly labels all proposed types and flows as future design. No current code fact is misrepresented.
- **No `extra_payload` leakage**: Confirmed. The design explicitly prohibits hidden parameters.
- **No quarterly/prospectus scope creep**: Confirmed. Non-goals are explicit.
- **No provider budget/score-loop leakage**: Confirmed. Both are deferred.
- **No public chapter id changes**: Confirmed. Chapter ids remain `0-7`.
- **No raw PDF text injection**: Confirmed. Explicitly rejected throughout.
- **No direct Eastmoney/EID API calls**: Confirmed. All loading goes through repository.
- **Fallback taxonomy consistency**: Confirmed. The five-category taxonomy is correctly mapped.

## Validation

- Verified `FundDocumentRepository.load_annual_report(fund_code, year, force_refresh=...)` signature against design claim — pass. The repository accepts `fund_code` and `year` as required parameters; the design correctly describes the loading contract.
- Verified `AnnualReportSourceMetadata` carries `fund_code`, `fund_id`, `fallback_used`, `primary_failure_category` — pass. The design's metadata requirements are supported by current model fields.
- Verified `StructuredFundDataBundle` is single-year with `fund_code` and `report_year` — pass. Current Fact 4 is accurate.
- Verified `DocumentKey` is `(fund_code, year, document_kind)` — pass. The repository's `_build_document_key` uses these fields.
- Verified `ChapterFactProjection` is single-year with `fund_code` and `report_year` — pass. Current Fact 5-6 are accurate.
- Verified `chapter_facts.py` `_synthetic_missing_facts` produces `cross_period_comparison_missing` for chapter 5 — pass. Current Fact 6 is accurate.
- Verified `AnnualReportSourceFailureCategory` literals match the fallback taxonomy — pass. `not_found`, `unavailable`, `schema_drift`, `identity_mismatch`, `integrity_error` are the exact literals.
- Verified prior template typed contract controller judgment defers multi-year annual evidence scope to a separate gate — pass. The next entry point correctly points to this gate.
- Verified prior Agent engine/tool-loop controller judgment scope guard says "Evidence must flow through FundDocumentRepository and typed evidence bundles" — pass. The design follows this guard.
- `rg -n "raw five-year PDF|raw 5-year PDF|raw PDF text|raw multi-year" docs/reviews/mvp-multi-year-annual-evidence-scope-design-20260603.md` — pass. Raw PDF injection is rejected in multiple locations.
- `rg -n "quarterly|prospectus|fund.contract|score-loop|Ch2 split|0\+9|0\+10|provider budget" docs/reviews/mvp-multi-year-annual-evidence-scope-design-20260603.md` — pass. All are in non-goals or rejections sections.
- `rg -n "extra_payload" docs/reviews/mvp-multi-year-annual-evidence-scope-design-20260603.md` — pass. Explicitly prohibited.

## Secret Safety

This review artifact contains no API key, Authorization header, Bearer token, cookie, password, raw provider response, raw audit response, prompt body, writer draft body, repair draft body, hidden provider config value, raw PDF text, or raw parsed annual-report text.
