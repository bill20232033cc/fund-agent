# Atomic Source Fact Store / Composite Analysis View Split S4 Implementation

## Verdict

S4_IMPLEMENTED_READY_FOR_CODE_REVIEW_NOT_READY

## Gate

- Work unit: Atomic Source Fact Store / Composite Analysis View Split
- Current gate: S4 ChapterFactProvider Bridge Implementation Gate
- Role: implementation worker only
- Scope: no-live Fund-layer ChapterFactProvider atomic projection bridge

## Changed Files

- `fund_agent/fund/chapter_facts.py`
- `tests/fund/test_chapter_facts_atomic.py`
- `tests/fund/test_chapter_facts.py`

`tests/fund/test_chapter_facts.py` was minimally synchronized because its static import guard rejected any module containing the substring `source`; S4 intentionally imports Fund-internal `fund_agent.fund.source_facts` as the accepted atomic bridge contract. The guard still rejects documents, repository, cache, PDF, external source helper, Service, dayu, provider/LLM imports.

## Behavior Summary

- Added trailing defaulted bridge fields to `ChapterFactEntry`:
  - `source_fact_ids: tuple[str, ...] = ()`
  - `derived_view_id: str | None = None`
- Added trailing defaulted bridge fields to `ChapterFactProjection`:
  - `source_facts: AtomicSourceFactStore = empty_atomic_source_fact_store()`
  - `derived_views: tuple[CompositeAnalysisView, ...] = ()`
- `ChapterFactProjection.source_facts` now mirrors `StructuredFundDataBundle.source_facts` by object identity.
- Migrated S4 fields are projected from accepted atomic fact IDs only:
  - `fee_schedule.management_fee`
  - `fee_schedule.custody_fee`
  - `nav_benchmark_performance.nav_growth_rate`
  - `nav_benchmark_performance.benchmark_return_rate`
  - `manager_strategy_text.strategy_summary`
  - `manager_strategy_text.market_outlook`
  - `manager_alignment.manager_holding`
  - `manager_alignment.employee_holding`
- Atomic chapter entries use `field_path="AtomicSourceFact.<fact_id>"`, `source_field_id="structured.<fact_id>"`, and `source_fact_ids=(fact_id,)`.
- Derived composite entries use `field_path="CompositeAnalysisView.<view_id>"`, set `derived_view_id`, and leave `source_fact_ids=()`.
- `projection.derived_views` is built from `AtomicSourceFactStore` through `build_composite_analysis_view`; no composite dict key flattening is used to fabricate atomic facts or dependencies.
- When a migrated field has no matching atomic facts in the store, projection falls back to the existing legacy `StructuredFundDataBundle.<field>` behavior with bridge fields empty.
- Non-migrated legacy fields keep existing field paths and empty bridge fields.

## Validation

- `uv run pytest tests/fund/test_chapter_facts_atomic.py -q`
  - Result: passed, `6 passed in 0.38s`
- `uv run pytest tests/fund/test_chapter_facts.py -q`
  - Result: passed, `14 passed in 0.44s`
- `uv run pytest tests/fund/test_source_facts.py -q`
  - Result: passed, `17 passed in 0.40s`
- `uv run ruff check fund_agent/fund/chapter_facts.py tests/fund/test_chapter_facts.py tests/fund/test_chapter_facts_atomic.py`
  - Result: passed, `All checks passed!`
- `git diff --check`
  - Result: passed

## Residual Risks

- S5 Evidence Confirm bridge remains uncovered in this gate.
  - Owner/destination: S5 Evidence Confirm Atomic Audit gate.
- S6 regression/docs/control sync remains uncovered in this gate.
  - Owner/destination: S6 Migration Regression and Test Reclassification / controller docs-control gate.
- Live/PDF/product CLI/provider/LLM behavior remains untested and unchanged in this gate.
  - Owner/destination: later explicitly authorized live/PDF and release/readiness evidence gates.
- Release/readiness remains `NOT_READY`.
  - Owner/destination: explicit release-boundary authorization and accepted readiness evidence.

## Explicit Non-goals Preserved

- No Evidence Confirm changes.
- No live/PDF/product CLI/provider/LLM commands or behavior changes.
- No report, renderer, checklist, quality-gate policy, or FDD default-on changes.
- No README, design, or control sync.
- No push, PR mutation, merge, tag, release, or readiness claim.
