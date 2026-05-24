# Release Maintenance 004393 Quality Gate S0 Evidence Review - GLM

## Scope

- Review target: `docs/reviews/release-maintenance-004393-quality-gate-evidence-20260524.md`
- Accepted plan: `docs/reviews/release-maintenance-004393-quality-gate-plan-20260524.md`
- Reviewer role: S0 evidence code-review specialist B
- Date: 2026-05-24
- Constraint: review-only artifact; no source, test, golden, README, plan, or control-file changes.

## Verdict

`PASS_WITH_FINDINGS`

The S0 evidence is acceptable as S1/S2 prerequisite evidence. It records direct same-source observations through `FundDocumentRepository`, covers all required S0 facts, and does not rely on direct PDF/cache/source-helper reads. The findings below are residual controls for implementation and later S4/golden/source-provenance decisions, not blockers for S1/S2.

## Findings

### F1 - Source provenance metadata is unavailable, but this is not an S1/S2 blocker

Severity: Medium / residual

Evidence records `metadata.source = null`, `source_metadata_present=false`, `fallback_used` unavailable, and `parsed_cache_hit=true`. The accepted plan asked the S0 artifact to include source metadata, cache status, and fallback-used status. The artifact does include those fields, but the repository-returned object cannot provide fallback/source provenance from the parsed cache.

This should not block S1/S2 because the S0 question is whether parser-visible same-source content supports the extraction changes. It does. However, this evidence must not be used to claim source fallback correctness, source identity, or fallback classification behavior. Any later controller approval for golden/source-sensitive claims should either accept this provenance limitation explicitly or rerun through a route that preserves `metadata.source.fallback_used`.

References:

- Plan requires source/cache/fallback metadata in S0: `release-maintenance-004393-quality-gate-plan-20260524.md:121`
- Evidence reports source/fallback unavailable: `release-maintenance-004393-quality-gate-evidence-20260524.md:271`
- Evidence still uses required repository route: `release-maintenance-004393-quality-gate-evidence-20260524.md:9`

### F2 - Fee evidence is valid, but S1 must search by subsection semantics, not parser section id

Severity: Medium / implementation guardrail

The plan names annual-report `§7.4.10.2`, but the parsed cache exposes that subsection under parser section `§5`; `get_section_text("§7")` is absent. The evidence explains this and locates `7.4.10.2.1 基金管理费` and `7.4.10.2.2 基金托管费` in parser section `§5` with table ordinals and text locators.

This is sufficient same-source evidence for S1. The implementation must treat `§7.4.10.2` as a subsection heading found within parser-visible text/tables, not as a requirement that `ParsedAnnualReport.get_section_text("§7")` exists. A hard-coded `get_section_text("§7")` fallback would repeat the S0 command failure.

References:

- Plan requires `§7.4.10.2` fee evidence: `release-maintenance-004393-quality-gate-plan-20260524.md:73`
- Evidence explains parser section `§5` containment: `release-maintenance-004393-quality-gate-evidence-20260524.md:291`
- Management fee locator/rate: `release-maintenance-004393-quality-gate-evidence-20260524.md:301`
- Custody fee locator/rate: `release-maintenance-004393-quality-gate-evidence-20260524.md:302`

### F3 - Holdings evidence supports S2 extractor planning, but not a completed gate-coverage claim

Severity: Low / residual

The evidence establishes that `§8` contains both separate industry-distribution tables and all-stock-investment-details tables with stock code/name/quantity/fair value/net-asset-ratio semantics and at least 10 rows. This is enough to start S2 extractor work under the accepted plan.

It does not by itself prove quality-gate coverage is fixed. S2 still must add and test machine-readable `top_holdings_status` / `top_holdings_source` semantics and prove industry-only evidence cannot satisfy stock-holdings coverage if gate coverage is claimed.

References:

- Plan requires all-stock details plus industry evidence: `release-maintenance-004393-quality-gate-plan-20260524.md:74`
- Plan requires machine-readable holdings source/status before claiming coverage: `release-maintenance-004393-quality-gate-plan-20260524.md:244`
- Evidence confirms all-stock details: `release-maintenance-004393-quality-gate-evidence-20260524.md:303`
- Evidence confirms independent industry evidence: `release-maintenance-004393-quality-gate-evidence-20260524.md:304`

### F4 - Benchmark whitespace evidence supports S2 normalization; S4 still needs row-level approval

Severity: Low / residual

The evidence shows raw parser text splits `中债综合` as `中债综\n合`, and that removing the visual newline yields the semantic benchmark text. This is enough to justify the planned benchmark-field-only correctness normalization.

It is not, by itself, approval to edit golden rows. S4 still requires a separate row-level controller approval artifact listing the current value, new value, direct locator, and build command.

References:

- Plan limits benchmark resolution to correctness/golden decision: `release-maintenance-004393-quality-gate-plan-20260524.md:23`
- Plan requires row-level S4 approval: `release-maintenance-004393-quality-gate-plan-20260524.md:567`
- Evidence benchmark locator/raw text: `release-maintenance-004393-quality-gate-evidence-20260524.md:308`

## Focus Checks

### Same-source / root-cause evidence

Pass. All positive observations are tied to `ParsedAnnualReport.get_section_text(...)` or `ParsedAnnualReport.tables` via the repository route. The failed initial command does not contradict the facts because the failure happened after repository load and was caused by slicing `None` for absent parser section `§7`; subsequent commands preserved missing sections explicitly and inspected actual section ids.

### Fee `§7.4.10.2` under parser section `§5`

Pass with implementation guardrail. The evidence demonstrates that parser section ids do not align with the visual annual-report chapter numbering for this subsection. S1 should search for `7.4.10.2` heading/table semantics across parser-visible text/tables, then anchor output to the subsection heading/table locator.

### A/C share-class evidence

Pass. The evidence uses same-source `§2` rows mapping `004393` to `安信企业价值优选混合A` and `020964` to `安信企业价值优选混合C`, then selects the adjacent `§10` A-class column. This avoids fund-code suffix inference.

One implementation nuance remains: the net-change value is recorded as same-table arithmetic from beginning and ending shares. That is acceptable for S0 support, but S2 tests should verify the extractor's intended output contract precisely: either extract a disclosed net row if one exists or compute only if the share-change contract explicitly allows the arithmetic.

### All-stock-details + industry evidence

Pass. The evidence is enough for S2 to implement semantic fallback from explicit top-ten tables to all-stock-investment-details tables while preserving industry distribution separately. It must not be overstated as gate readiness until status/source propagation and industry-only failure behavior are tested.

### Benchmark whitespace

Pass. The evidence is enough for benchmark-field-only correctness normalization and for later S4 consideration. It is not an authorization to edit golden files.

### `source=null`, unavailable `fallback_used`, and `parsed_cache_hit=true`

Residual, not blocker for S1/S2. This limits provenance claims but does not undermine parser-content root-cause evidence. It should be carried forward as a residual risk and revisited before any source/fallback-sensitive assertion.

### Initial command failure

Not a blocker. No plan rewrite or S0 rerun is required for S1/S2. The failure usefully revealed that the plan-pattern script was brittle around absent `§7`; the successful follow-up commands satisfy the evidence intent and should steer implementation away from hard-coded parser section ids.

## S1/S2 Readiness

S1 may proceed on `basic_identity` and `fee_schedule`, with the fee fallback implemented against subsection/table semantics rather than `get_section_text("§7")` only.

S2 may proceed on holdings, share-change, and benchmark correctness normalization, with fail-closed A/C selection and holdings status/source tests required before claiming quality-gate coverage.

S4 remains blocked until a separate row-level controller approval artifact exists. Turnover remains deferred applicability scope and should not be implemented under this plan.
