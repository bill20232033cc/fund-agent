# Atomic Source Fact Store / Composite Analysis View Split S2B Code Review

## Scope

- Mode: restricted current workspace S2B review
- Branch: `evidence-confirm-productionization`
- Included scope:
  - `fund_agent/fund/processors/active_annual.py`
  - `tests/fund/processors/test_active_annual_processor.py`
  - `tests/fund/test_data_extractor.py`
  - `docs/reviews/evidence-confirm-productionization-atomic-source-fact-store-s2b-implementation-20260625-143342.md`
- Excluded scope:
  - `docs/reviews/evidence-confirm-productionization-rr-09-product-cli-ec-fail-quality-gate-residual-plan-20260623.md`
  - unrelated untracked research/scratch files
  - live/PDF/provider/product CLI/remote state

## Findings

### S2B-CR-001 - High - partial child fact is hidden by compatibility composite assembly

- Classification: accepted
- Entry path: `_ParsedAnnualReportFundProcessor.extract -> _collect_existing_extractor_fields -> _build_source_fact_store -> _build_field_family_result -> FundDataExtractor bundle projection`
- Evidence:
  - `fund_agent/fund/processors/active_annual.py:499-522`
  - `fund_agent/fund/processors/active_annual.py:602-608`
  - `fund_agent/fund/processors/active_annual.py:657-689`
  - `fund_agent/fund/processors/active_annual.py:852-875`
- Triggering input: one migrated composite has one accepted child and one explicit missing child, for example `fee_schedule.management_fee` present and `fee_schedule.custody_fee` missing.
- Actual behavior: `_source_fact_from_child_field()` creates both the accepted child fact and the explicit missing child fact, but `_composite_value_from_source_facts()` only returns accepted children. `_build_field_family_result()` then sees a truthy composite value, writes the legacy composite field, and skips the missing-field path. The missing child is omitted from the legacy value, family gaps, and status calculation.
- Expected behavior: explicit missing child facts must remain visible in compatibility projection or family gap/status semantics. Missing siblings must not be silently hidden by a present sibling.
- Impact: downstream consumers can read a top-level compatibility composite that appears complete enough while the atomic store contains a missing child. This weakens the no-fabrication contract and can cause S4/S5 consumers or legacy report paths to misjudge completeness.
- Fix direction: migrated composite assembly should include all required child keys, using actual values for accepted facts and `None` for explicit missing facts, and should feed missing child gaps into family gaps/status. Add sibling-partial regression tests.

## Open Questions

- The accepted plan artifact `docs/reviews/evidence-confirm-productionization-atomic-source-fact-store-composite-view-implementation-plan-20260625.md` is modified in the current workspace but was not in the S2B implementation review scope. Controller must decide whether this is related control drift, a pre-existing change to ignore, or a file that must be excluded from the S2B commit.

## Residual Risks

- S2B tests currently lack migrated composite sibling-partial coverage. Owner: S2B fix worker; destination: S2B fix gate.
- `tests/fund/test_data_extractor.py` uses a superset assertion for bundle source facts, which does not catch unexpected extra migrated facts. Owner: S2B fix worker; destination: S2B fix gate or re-review.
- Explicit FundDisclosureDocument route remains out of scope. Owner: S3 implementation worker; destination: S3 gate.
- ChapterFactProvider atomic bridge and Evidence Confirm atomic materialization remain out of scope. Owner: S4/S5 implementation workers; destination: later approved gates.
- live/PDF/product CLI/provider/LLM checks were not run and cannot be inferred. Owner: later explicit evidence gate.

## Validations

- Reviewer ran branch/status checks and restricted diff/source reads for included S2B files.
- Reviewer ran a minimal no-live in-memory validation of partial child behavior.
- Full pytest/ruff was not rerun by reviewer because the blocker is not covered by the current suite.
- No live/PDF/provider/product CLI/network/PR/push/merge/tag/release/readiness commands were run.

## Verdict

S2B_CODE_REVIEW_BLOCKED_FIX_REQUIRED_NOT_READY

