# Atomic Source Fact Store / Composite Analysis View Split S5 Implementation

## Verdict

S5_IMPLEMENTED_READY_FOR_CODE_REVIEW_NOT_READY

## Scope

- Gate: S5 Evidence Confirm Atomic Audit Implementation Gate.
- Worker role: implementation only.
- Scope implemented: Evidence Confirm material resolution uses S4 bridge ids when present.
- Policy boundary: no Evidence Confirm V2 / ECQ / quality-gate / CLI / report / provider / live/PDF policy change.

## Changed Files

- `fund_agent/fund/evidence_confirm.py`
- `fund_agent/fund/evidence_confirm_sources.py`
- `fund_agent/fund/evidence_confirm_value_diagnostics.py`
- `tests/fund/test_evidence_confirm_atomic.py`
- `docs/reviews/evidence-confirm-productionization-atomic-source-fact-store-s5-implementation-20260625-154945.md`

Existing unrelated dirty/untracked files were not edited by this S5 worker.

## Behavior Summary

- Added a projection-aware Evidence Confirm material resolver:
  - `ChapterFactEntry.source_fact_ids` resolves from `ChapterFactProjection.source_facts`.
  - Single atomic bridge facts materialize exactly one atomic source fact value.
  - Missing bridge target or multi-id bridge fails closed as unresolved material.
  - Legacy no-bridge facts keep existing `fact.value` behavior.
- V1/V2 projection-level Evidence Confirm now passes projection context into fact confirmation.
- Derived bridge facts remain not directly confirmed when dependency provenance is complete, but fail safely when the referenced `derived_view_id` is missing or any dependency atomic fact lacks section-or-better provenance.
- Reference materializer semantic row narrowing and value diagnostics now use the same bridge-aware material token resolver.
- No atomic mapping is rediscovered from dict keys, `field_path`, or row locator parsing.

## Tests Added

`tests/fund/test_evidence_confirm_atomic.py` covers:

- `fee_schedule.management_fee` value_match ignores `custody_fee` sibling when bridge id exists.
- Diagnostics token count/category uses `ChapterFactEntry.source_fact_ids`.
- Derived `fee_schedule` view fails safely when a child fact lacks section-level provenance.
- Missing child anchor is not fabricated from composite dict or locator.
- Legacy no-bridge fact keeps existing composite `fact.value` material behavior.
- No atomic facts available preserves no-bridge projection behavior.

No existing Evidence Confirm tests required helper/import edits.

## Validation

- `uv run pytest tests/fund/test_evidence_confirm_atomic.py -q`
  - Result: `6 passed in 0.66s`
- `uv run pytest tests/fund/test_evidence_confirm.py tests/fund/test_evidence_confirm_sources.py tests/fund/test_evidence_confirm_value_diagnostics.py -q`
  - Result: `108 passed in 1.22s`
- `uv run pytest tests/fund/test_chapter_facts_atomic.py tests/fund/test_source_facts.py -q`
  - Result: `23 passed in 0.66s`
- `uv run ruff check fund_agent/fund/evidence_confirm.py fund_agent/fund/evidence_confirm_sources.py fund_agent/fund/evidence_confirm_value_diagnostics.py tests/fund/test_evidence_confirm_atomic.py`
  - Result: `All checks passed!`
- `git diff --check`
  - Result: passed with no output.
- `uv run mypy fund_agent/fund/evidence_confirm.py fund_agent/fund/evidence_confirm_sources.py fund_agent/fund/evidence_confirm_value_diagnostics.py`
  - Result: not executed; environment has no `mypy` executable: `Failed to spawn: mypy`.

## Residual Risks

- Live/PDF strict re-evidence for `017641 / 2024`, `004393 / 2021-2025`, and additional atomic samples remains routed to post-S5 live/PDF re-evidence gate.
- Release/readiness remains `NOT_READY`; owner: release/readiness gate after accepted S5 review and separately authorized evidence.
- Product CLI, checklist Evidence Confirm support, report body rendering, provider/LLM behavior, PR remote state, tag, release, and readiness remain later gates.
- Focused mypy could not run because `mypy` is absent from the environment; destination: code review / environment tooling decision if type-check evidence is required.

## Explicit Non-goals Preserved

- Did not remove `StructuredFundDataBundle`.
- Did not rename public bundle fields.
- Did not change `FundFieldFamilyResult` schema.
- Did not change Evidence Confirm V2 pass/fail thresholds or ECQ semantics.
- Did not change quality-gate FQ0-FQ6 rules or policy.
- Did not change report-body, renderer, checklist, provider/LLM, or CLI behavior.
- Did not make FDD default-on.
- Did not consume Docling JSON, PDF cache, or source helpers outside Fund boundaries.
- Did not claim release readiness.
- Did not commit, push, create PR, merge, tag, or release.
