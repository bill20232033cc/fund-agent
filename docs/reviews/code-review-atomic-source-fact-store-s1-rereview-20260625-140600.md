# Atomic Source Fact Store S1 Re-review

## Verdict

`S1_REREVIEW_PASS_READY_FOR_ACCEPTED_SLICE_COMMIT_NOT_READY`

- Gate: `S1 re-review gate after fix`
- Work unit: `Atomic Source Fact Store / Composite Analysis View Split`
- Branch: `evidence-confirm-productionization`
- Accepted finding: `S1-CR-001`
- Final status: `已修复`
- Readiness/release: `NOT_READY`; this re-review does not authorize PR mutation, push, merge, tag, release, live/PDF, product CLI, provider/LLM, repository/parser/source-helper commands, or S2-S5 expansion.

## Reviewed Files

- `fund_agent/fund/source_facts.py`
- `tests/fund/test_source_facts.py`
- `fund_agent/fund/README.md`
- `docs/reviews/evidence-confirm-productionization-atomic-source-fact-store-s1-fix-20260625-140323.md`
- `docs/reviews/code-review-atomic-source-fact-store-s1-subagent-20260625-135803.md`
- `docs/reviews/evidence-confirm-productionization-atomic-source-fact-store-composite-view-implementation-plan-20260625.md` S1-relevant sections

Excluded by instruction: unrelated dirty/untracked workspace files, live/PDF/product CLI/provider/LLM/repository/parser/source-helper behavior, and S2/S3/S4/S5 implementation surfaces.

## Findings

未发现实质性问题。

New finding count by severity:

- 严重: 0
- 高: 0
- 中: 0
- 低: 0

## S1-CR-001 Re-review

Final status: `已修复`.

Evidence:

- The accepted plan requires derived composite views to list child dependencies, allows `accepted` only when required child facts satisfy assembly policy, and requires missing child provenance to become gap/status rather than fabricated child source paths (`docs/reviews/evidence-confirm-productionization-atomic-source-fact-store-composite-view-implementation-plan-20260625.md:132-137`). S1 also explicitly requires a pure assembler helper and missing dependency fail-closed behavior (`...plan-20260625.md:165-170`, `:174-179`).
- `build_composite_analysis_view()` no longer accepts caller-supplied `value`; its public signature only takes `view_id`, `source_facts`, `dependency_fact_ids`, and optional `required_fact_ids` (`fund_agent/fund/source_facts.py:270-276`). The returned value is built from present dependency facts only as `{fact_id: fact.value}` (`fund_agent/fund/source_facts.py:333-337`).
- Absent dependencies no longer call `get_required()` or leak `KeyError`; the helper uses `get_optional()`, records absent ids, emits `missing dependency fact: <fact_id>` gaps, and returns `partial` or `missing` status based on available facts (`fund_agent/fund/source_facts.py:304-345`).
- `required_fact_ids` outside `dependency_fact_ids` cannot produce an accepted view; the helper validates the subset relation and raises `ValueError` before assembly (`fund_agent/fund/source_facts.py:294-302`). This is consistent with the function docstring (`fund_agent/fund/source_facts.py:285-291`) and focused regression test (`tests/fund/test_source_facts.py:308-319`).
- Regression tests cover the accepted-value derivation path, rejection of caller-supplied value, absent dependency fail-closed gap, all dependencies absent -> `missing`, required ids outside dependencies, and empty dependency ids -> null value (`tests/fund/test_source_facts.py:244-333`).
- Fund README now matches the fixed S1 contract: helper value derives from dependency atomic facts, missing dependency returns `partial` / `missing` with explicit gap, and required ids must be a subset (`fund_agent/fund/README.md:139`).

Judgment:

- Caller-supplied fabricated composite values are no longer an accepted input path.
- Accepted view values now come only from dependency atomic facts.
- Absent dependency behavior is fail-closed status/gap, not `KeyError`.
- Required ids outside dependency ids are rejected before an accepted view can be produced.
- No same-or-higher severity regression was found in the S1 fix scope.

## Validation

Run:

- `uv run pytest tests/fund/test_source_facts.py -q` -> `17 passed`
- `uv run pytest tests/fund/test_data_extractor.py -q` -> `57 passed`
- `uv run pytest tests/fund/processors/test_fund_disclosure_processor.py -q` -> `199 passed`
- `uv run ruff check fund_agent/fund/source_facts.py fund_agent/fund/data_extractor.py fund_agent/fund/processors/contracts.py tests/fund/test_source_facts.py` -> `All checks passed`
- `git diff --check` -> passed with no output

Not run by instruction:

- live/PDF commands
- product CLI commands
- provider/LLM commands
- network commands
- repository/parser/source-helper commands
- broader test suites

## Residual Risks

- S2-S5 migration behavior remains unreviewed in this gate. Owner/destination: later approved S2/S3/S4/S5 gates for migrated-family emission, chapter fact projection, Evidence Confirm consumption, and compatibility rollout.
- Workspace contains unrelated dirty/untracked files outside this re-review scope. Owner/destination: controller / artifact-disposition or the owning active gate. This re-review did not inspect or classify them beyond confirming they are outside the requested S1 fix scope.
- `source_facts.py` and `tests/fund/test_source_facts.py` are currently untracked in this workspace snapshot. Owner/destination: accepted slice commit gate must stage only intended S1 implementation/fix/re-review files and continue excluding unrelated residue.

## Stop Condition

Re-review artifact written at `docs/reviews/code-review-atomic-source-fact-store-s1-rereview-20260625-140600.md`. Stop after artifact/content. No commit, push, PR mutation, mark-ready, merge, tag, release, live/PDF, product CLI, provider/LLM, repository/parser/source-helper command, or S2-S5 review was performed.
