# Atomic Source Fact Store / Composite Analysis View Split S3 Fix

Verdict: `S3_FIX_READY_FOR_RE_REVIEW_NOT_READY`

## Scope

- Gate: S3 Fix Gate.
- Role: fix worker only.
- Accepted review artifact: `docs/reviews/code-review-atomic-source-fact-store-s3-20260625-151412.md`.
- Accepted finding fixed: `S3-CR-001` only.
- Objective: child-level missing facts inside migrated composites must produce partial family status and explicit gaps instead of accepted family/view when parent top-level keys are present.

## Changed Files

- `fund_agent/fund/processors/fund_disclosure_processor.py`
- `tests/fund/processors/test_fund_disclosure_processor.py`
- `docs/reviews/evidence-confirm-productionization-atomic-source-fact-store-s3-fix-20260625-152142.md`

`tests/fund/test_data_extractor.py` remained part of the pre-existing S3 implementation dirty diff and was validated, but this fix pass did not require additional edits there.

## Fix

- Added explicit required-child policies for S3 migrated composites:
  - `manager_strategy_text.strategy_summary`
  - `manager_strategy_text.market_outlook`
  - `manager_alignment.manager_holding`
  - `manager_alignment.employee_holding`
  - `fee_schedule.management_fee`
  - `fee_schedule.custody_fee`
- Added `_missing_required_child_source_field_paths()` so family completeness is checked against accepted `AtomicSourceFactStore` entries, not only derived top-level composite keys.
- Updated `manager_profile.v1` and `return_attribution.v1` source-truth gap/status derivation:
  - full top-level compatibility value plus missing required child fact now returns `partial`;
  - missing required child emits `field_family_partial`;
  - child gap uses canonical child `source_field_path`, for example `manager_strategy_text.market_outlook` or `fee_schedule.custody_fee`.
- Preserved compatibility composite values with missing child keys set to `None`.
- Preserved S3 contract boundaries: no `source_facts` public contract change, no candidate-only fact emission, no S4/S5/Evidence Confirm/ChapterFactProvider/live/PDF/product CLI/provider/LLM change.

## Regression Coverage

- Added `test_manager_profile_source_truth_partial_when_strategy_child_missing`:
  - all five `manager_profile.v1` top-level groups are present;
  - `manager_strategy_text.market_outlook` is absent;
  - family status is `partial`;
  - gap source path is `manager_strategy_text.market_outlook`;
  - missing child is absent from `source_facts`.
- Added `test_return_attribution_source_truth_partial_when_fee_child_missing`:
  - all three `return_attribution.v1` top-level groups are present;
  - `fee_schedule.custody_fee` is absent;
  - family status is `partial`;
  - gap source path is `fee_schedule.custody_fee`;
  - missing child is absent from `source_facts`.
- Updated existing partial/accepted manager_profile fixtures so accepted now means both top-level completeness and required-child source fact completeness.

## Validation

- `uv run pytest tests/fund/processors/test_fund_disclosure_processor.py -q`
  - Result: `201 passed in 0.75s`
- `uv run pytest tests/fund/test_data_extractor.py -q`
  - Result: `58 passed in 0.51s`
- `uv run pytest tests/fund/test_source_facts.py -q`
  - Result: `17 passed in 0.43s`
- `uv run ruff check fund_agent/fund/processors/fund_disclosure_processor.py tests/fund/processors/test_fund_disclosure_processor.py tests/fund/test_data_extractor.py`
  - Result: `All checks passed!`
- `git diff --check`
  - Result: passed with no output.

## Residual Risks / Owners

- S4 ChapterFactProvider projection from atomic facts and derived views: covered by later approved slice; owner: S4 implementation worker.
- S5 Evidence Confirm atomic audit materialization: covered by later approved slice; owner: S5 implementation worker.
- Live/PDF, product CLI, provider/LLM, PR/remote, tag, release and readiness remain out of scope and unproven.
- Release/readiness remains `NOT_READY`.

## Stop Condition

Ready for S3 re-review, not committed. No PR, push, merge, tag, release or readiness state was changed.
