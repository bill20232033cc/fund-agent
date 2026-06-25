# Atomic Source Fact Store / Composite Analysis View Split S2A Implementation Evidence

- Work unit: `Atomic Source Fact Store / Composite Analysis View Split`
- Gate: `S2A - Default parsed annual extractor child fact split implementation`
- Verdict: `S2A_IMPLEMENTED_READY_FOR_CODE_REVIEW_NOT_READY`
- Stop condition: ready for code review, not committed, release/readiness `NOT_READY`

## Scope

Implemented S2A only. This slice splits default parsed annual extractor outputs into child-level extractor fields before processor assembly. It does not emit `AtomicSourceFact`; S2B remains responsible for processor consumption and atomic fact emission.

No changes were made to `fund_agent/fund/processors/active_annual.py`, `fund_agent/fund/data_extractor.py`, `chapter_facts.py`, `evidence_confirm*.py`, control docs, design docs, README, live/PDF paths, product CLI, provider/LLM, PR state, tags, release, or readiness.

## Changed Files

- `fund_agent/fund/extractors/models.py`
- `fund_agent/fund/extractors/profile.py`
- `fund_agent/fund/extractors/performance.py`
- `fund_agent/fund/extractors/manager_ownership.py`
- `tests/fund/extractors/test_profile.py`
- `tests/fund/extractors/test_performance.py`
- `tests/fund/extractors/test_manager_ownership.py`
- `docs/reviews/evidence-confirm-productionization-atomic-source-fact-store-s2a-implementation-20260625-141827.md`

## Child Output Contract Implemented

Each migrated child output is now exposed on the relevant extractor result dataclass as a trailing/defaulted `ExtractedField[object]` compatibility extension:

- `ProfileExtractionResult.fee_schedule_management_fee` for `fee_schedule.management_fee`
- `ProfileExtractionResult.fee_schedule_custody_fee` for `fee_schedule.custody_fee`
- `PerformanceExtractionResult.nav_benchmark_performance_nav_growth_rate` for `nav_benchmark_performance.nav_growth_rate`
- `PerformanceExtractionResult.nav_benchmark_performance_benchmark_return_rate` for `nav_benchmark_performance.benchmark_return_rate`
- `ManagerOwnershipExtractionResult.manager_strategy_text_strategy_summary` for `manager_strategy_text.strategy_summary`
- `ManagerOwnershipExtractionResult.manager_strategy_text_market_outlook` for `manager_strategy_text.market_outlook`
- `ManagerOwnershipExtractionResult.manager_alignment_manager_holding` for `manager_alignment.manager_holding`
- `ManagerOwnershipExtractionResult.manager_alignment_employee_holding` for `manager_alignment.employee_holding`

Directly matched children carry:

- their own scalar value;
- `extraction_mode="direct"`;
- their own source anchor copied from the direct text/table match;
- canonical child path in anchor `row_locator`, e.g. `source_field_path=fee_schedule.management_fee; locator=management_fee`;
- no note.

Missing children carry:

- `value=None`;
- `extraction_mode="missing"`;
- `anchors=()`;
- gap note with canonical child path, e.g. `source_field_path=manager_strategy_text.market_outlook; gap=...`.

No child output is created from a composite dict key alone. Every direct child field is built from the extractor's matched text/table source object. Missing child fields are explicit gaps and have no fabricated anchors.

## Compatibility Behavior Preserved

Existing composite extractor fields remain available:

- `fee_schedule`
- `nav_benchmark_performance`
- `manager_strategy_text`
- `manager_alignment`

Their dict values are assembled from the child `ExtractedField` values. Existing composite anchors remain based on the extractor's direct matched source objects, so current processor assembly and top-level field projection remain unchanged in S2A. Processor-level atomic source fact emission is intentionally not added here.

## Validation

- `uv run pytest tests/fund/extractors/test_profile.py tests/fund/extractors/test_performance.py tests/fund/extractors/test_manager_ownership.py -q` -> `65 passed in 0.75s`
- `uv run pytest tests/fund/test_source_facts.py -q` -> `17 passed in 0.59s`
- `uv run pytest tests/fund/test_data_extractor.py -q` -> `57 passed in 0.57s`
- `uv run pytest tests/fund/processors/test_fund_disclosure_processor.py -q` -> `199 passed in 0.64s`
- `uv run ruff check fund_agent/fund/extractors/profile.py fund_agent/fund/extractors/performance.py fund_agent/fund/extractors/manager_ownership.py tests/fund` -> `All checks passed!`
- `git diff --check` -> passed with no output

## Residual Risks / Owner

- S2B processor emission remains pending: `active_annual.py` still consumes the existing composite extractor fields and has not yet emitted child-level `AtomicSourceFact` records. Owner: S2B implementation worker.
- Evidence Confirm, ChapterFactProvider bridge, quality gate, renderer, product CLI, live/PDF evidence, release and readiness remain later gates. Owner: later approved S3/S4/S5/RR gates.
- This slice adds trailing/defaulted result dataclass fields for compatibility. Consumers that do not read the new child fields keep current behavior; code review should verify S2B can consume these names without inferring children from composite dicts.

## Completion Status

`S2A_IMPLEMENTED_READY_FOR_CODE_REVIEW_NOT_READY`

No commit was created. No push, PR mutation, merge, tag, release, live/PDF, product CLI, provider/LLM, or readiness action was executed.
