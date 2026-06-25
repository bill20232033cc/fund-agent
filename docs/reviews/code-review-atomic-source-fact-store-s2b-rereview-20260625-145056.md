# Atomic Source Fact Store / Composite Analysis View Split S2B Re-review

## Findings

未发现实质性问题。

## Accepted Finding Re-review

### S2B-CR-001: partial child fact was hidden by compatibility composite assembly

Final status: `已修复`

- Entry path reviewed: `_ParsedAnnualReportFundProcessor.extract -> _build_source_fact_store -> _build_field_family_result -> _composite_value_from_source_facts/_missing_composite_children -> FundDataExtractor bundle projection`
- Direct evidence:
  - `fund_agent/fund/processors/active_annual.py`: `_composite_value_from_source_facts()` now returns full required child-key dict when at least one child fact is accepted; missing or absent sibling children project as `None`.
  - `fund_agent/fund/processors/active_annual.py`: `_missing_composite_children()` collects explicit missing child facts.
  - `fund_agent/fund/processors/active_annual.py`: missing child gaps are added into family gap/status derivation and final gaps.
  - `fund_agent/fund/processors/active_annual.py`: composite anchors are aggregated only from accepted child facts.
  - `tests/fund/processors/test_active_annual_processor.py`: processor-level sibling partial regression verifies `custody_fee=None`, child gap, `partial` status, and no fabricated custody-fee anchor.
  - `tests/fund/test_data_extractor.py`: bundle-level sibling partial regression verifies `source_facts`, compatibility value, and accepted-child-only anchors.

Expected fixed behavior is satisfied:

- At least one accepted child plus one explicit missing child keeps all required child keys in the legacy composite dict.
- Missing child value is `None`.
- Missing child contributes a field-family gap using child `source_field_path`.
- Family status becomes `partial`.
- Anchors come only from accepted child facts.

Re-review conclusion: the fix directly addresses the original failure path. The missing sibling is no longer hidden by compatibility composite assembly.

## Scope Check

- No S3/S4/S5 scope creep found in the reviewed files.
- No FundDisclosureDocument route change detected in the S2B fix write set.
- No Evidence Confirm materializer change detected in the S2B fix write set.
- No source_facts public contract change detected in the S2B fix write set.
- No live/PDF/provider/product CLI/LLM, PR, remote, tag, release, or readiness action was run or inferred.

## Open Questions

无。

## Residual Risks

- S3 Explicit FundDisclosureDocument route atomic preservation remains unreviewed in this gate. Owner: S3 implementation worker; destination: S3 gate.
- S4 ChapterFactProvider bridge to atomic facts and derived views remains unreviewed in this gate. Owner: S4 implementation worker; destination: S4 gate.
- S5 Evidence Confirm atomic consumption and audit materialization remain unreviewed in this gate. Owner: S5 implementation worker; destination: S5 gate.
- Runtime live/PDF and product CLI re-evidence were not run. Owner: later explicit evidence gate; destination: post-S5 or separately authorized re-evidence gate.
- `tests/fund/test_data_extractor.py` happy-path source fact assertion still uses a superset check, so it is weaker than exact emission checking for bundle-level unexpected extra facts. This does not reopen S2B-CR-001 because the processor-level test asserts the exact emitted fact set. Owner: S2B/S3 test hardening; destination: accepted-slice follow-up or next implementation slice.

## Validations

- Re-reviewer ran `git status --short`.
- Re-reviewer read restricted diff for:
  - `fund_agent/fund/processors/active_annual.py`
  - `tests/fund/processors/test_active_annual_processor.py`
  - `tests/fund/test_data_extractor.py`
  - S2B code review and fix artifacts
- Re-reviewer ran `uv run pytest tests/fund/processors/test_active_annual_processor.py -q`: `13 passed`.
- Re-reviewer ran `uv run pytest tests/fund/test_data_extractor.py -q`: `58 passed`.
- Re-reviewer ran `uv run ruff check fund_agent/fund/processors/active_annual.py tests/fund/processors/test_active_annual_processor.py tests/fund/test_data_extractor.py`: passed.
- Re-reviewer ran restricted `git diff --check` for reviewed S2B files: passed with no output.
- No live/PDF/provider/product CLI/network/PR/push/merge/tag/release/readiness commands were run.

## Verdict

S2B_RE_REVIEW_PASS_READY_FOR_ACCEPTED_SLICE_COMMIT_NOT_READY

