# Atomic Source Fact Store / Composite Analysis View Split S5 Code Review

## Scope

- Mode: Gateflow S5 code review after implementation
- Branch: `evidence-confirm-productionization`
- Work unit: Atomic Source Fact Store / Composite Analysis View Split
- Gate: S5 Code Review
- Output file: `docs/reviews/code-review-atomic-source-fact-store-s5-20260625-155208.md`
- Included scope:
  - `fund_agent/fund/evidence_confirm.py`
  - `fund_agent/fund/evidence_confirm_sources.py`
  - `fund_agent/fund/evidence_confirm_value_diagnostics.py`
  - `tests/fund/test_evidence_confirm_atomic.py`
  - `docs/reviews/evidence-confirm-productionization-atomic-source-fact-store-s5-implementation-20260625-154945.md`
- Excluded scope:
  - unrelated dirty docs/reviews plan files
  - unrelated untracked docs/scripts
  - live/PDF/product CLI/provider/LLM/PR/readiness
  - S6 docs/control/regression gate
- Parallel review coverage: 无

## Findings

未发现实质性问题。

Reviewed evidence:

- Projection-level V1/V2 entry points pass the supplied `ChapterFactProjection` into `_confirm_fact` / `_confirm_fact_v2`; single-chapter legacy entry points remain projection-free and therefore retain legacy behavior. Evidence: `confirm_projection_evidence()` passes `projection` at `fund_agent/fund/evidence_confirm.py:335-364`; `confirm_projection_evidence_v2()` passes `projection` at `fund_agent/fund/evidence_confirm.py:427-458`; `confirm_chapter_evidence()` and `confirm_chapter_evidence_v2()` call fact confirmation without projection at `fund_agent/fund/evidence_confirm.py:295-318` and `fund_agent/fund/evidence_confirm.py:383-408`.
- Bridge-aware material resolution is driven only by `ChapterFactEntry.source_fact_ids` / `derived_view_id` and the supplied `ChapterFactProjection`; it does not rediscover atomic mappings from dict keys, `field_path`, or row locator parsing. Evidence: `_resolved_fact_material_value()` resolves exactly one `source_fact_id`, rejects multi-id or missing target with `_UNRESOLVED_FACT_MATERIAL`, resolves derived view by `derived_view_id`, and otherwise falls back to `fact.value` at `fund_agent/fund/evidence_confirm.py:1866-1898`.
- Atomic value_match uses the resolved single atomic fact value. Missing bridge target / multi-id bridge fails closed before token matching. Evidence: V2 value_match receives `material_value` from `_resolved_fact_material_value()` at `fund_agent/fund/evidence_confirm.py:569-572`; `_dimension_value_match()` converts `_UNRESOLVED_FACT_MATERIAL` into E3 blocking failure at `fund_agent/fund/evidence_confirm.py:1106-1118`; V1 has the same fail-closed path at `fund_agent/fund/evidence_confirm.py:1467-1473`.
- Derived fact policy remains not-applicable when dependency provenance is complete and fails safely when the derived view or dependency provenance is missing. Evidence: `_confirm_fact_v2()` checks `_derived_dependency_provenance_issues()` before returning not-applicable at `fund_agent/fund/evidence_confirm.py:515-519`; `_derived_dependency_provenance_issues()` emits E3 blocking issues for missing `derived_view_id`, missing dependency atomic fact, or missing section-or-better provenance at `fund_agent/fund/evidence_confirm.py:1941-1971`.
- Sources materializer and value diagnostics use the same resolver where relevant. Evidence: semantic row narrowing uses `_resolved_fact_material_tokens()` for bridge facts at `fund_agent/fund/evidence_confirm_sources.py:1317-1322` and `fund_agent/fund/evidence_confirm_sources.py:1343-1364`; diagnostics uses `_resolved_fact_material_tokens()` before matching token diagnostics at `fund_agent/fund/evidence_confirm_value_diagnostics.py:238-241`.
- Legacy no-bridge path remains unchanged for material tokens: bridge fields absent falls back to `fact.value`, and the compatibility tests exercise this behavior. Evidence: resolver fallback at `fund_agent/fund/evidence_confirm.py:1898`; tests at `tests/fund/test_evidence_confirm_atomic.py:162-222`.
- New tests cover the main regression surfaces without proving behavior through implementation-only hooks: atomic sibling isolation, diagnostics token source, derived provenance degradation, no-fabrication on missing child anchor, and no-bridge compatibility. Evidence: `tests/fund/test_evidence_confirm_atomic.py:24-222`.

## Accepted Finding IDs

无

## Open Questions

无

## Residual Risks

- Focused `mypy` evidence is still unavailable because the environment has no `mypy` executable. Owner/destination: environment/tooling decision if Gateflow controller requires type-check evidence before accepted slice commit.
- Live/PDF strict re-evidence for `017641 / 2024`, `004393 / 2021-2025`, and additional atomic samples was intentionally not run. Owner/destination: post-S5 live/PDF re-evidence gate.
- Release/readiness, product CLI, checklist Evidence Confirm support, report body rendering, provider/LLM behavior, PR remote state, tag, and release were intentionally not reviewed. Owner/destination: later authorized gates.
- Projection-free `confirm_chapter_evidence(_v2)` remains legacy and cannot validate bridge target existence because it has no supplied `ChapterFactProjection`; this is consistent with the S5 projection-supplied scope but should not be used as proof of bridge-aware behavior. Owner/destination: S6 docs/control or later API boundary decision if single-chapter bridge support becomes required.

## Validation

- `uv run pytest tests/fund/test_evidence_confirm_atomic.py -q`
  - Result: `6 passed in 0.74s`
- `uv run pytest tests/fund/test_evidence_confirm.py tests/fund/test_evidence_confirm_sources.py tests/fund/test_evidence_confirm_value_diagnostics.py -q`
  - Result: `108 passed in 1.27s`
- `uv run pytest tests/fund/test_chapter_facts_atomic.py tests/fund/test_source_facts.py -q`
  - Result: `23 passed in 0.38s`
- `uv run ruff check fund_agent/fund/evidence_confirm.py fund_agent/fund/evidence_confirm_sources.py fund_agent/fund/evidence_confirm_value_diagnostics.py tests/fund/test_evidence_confirm_atomic.py`
  - Result: `All checks passed!`
- `git diff --check -- fund_agent/fund/evidence_confirm.py fund_agent/fund/evidence_confirm_sources.py fund_agent/fund/evidence_confirm_value_diagnostics.py tests/fund/test_evidence_confirm_atomic.py docs/reviews/evidence-confirm-productionization-atomic-source-fact-store-s5-implementation-20260625-154945.md`
  - Result: passed with no output
- `uv run mypy fund_agent/fund/evidence_confirm.py fund_agent/fund/evidence_confirm_sources.py fund_agent/fund/evidence_confirm_value_diagnostics.py`
  - Result: failed before type-checking: `Failed to spawn: mypy`

## Verdict

S5_CODE_REVIEW_PASS_READY_FOR_ACCEPTED_SLICE_COMMIT_NOT_READY
