# Atomic Source Fact Store S1 Code Review

## Verdict

- Verdict: `CHANGES_REQUESTED_NOT_READY`
- Blocker: yes
- Recommendation: accept finding S1-CR-001 for fix; do not advance S1 to accepted slice commit until re-review proves the composite helper is derived-only and missing dependencies fail closed as status/gap, not exception/fabricated value.

## Scope

- Mode: Gateflow S1 implementation code review, scoped by user instruction.
- Branch: `evidence-confirm-productionization`
- Base/current input: accepted plan commit `25fef99`; S1 implementation artifact `docs/reviews/evidence-confirm-productionization-atomic-source-fact-store-s1-implementation-20260625-133727.md`
- Output file: `docs/reviews/code-review-atomic-source-fact-store-s1-subagent-20260625-135803.md`
- Reviewed files:
  - `fund_agent/fund/source_facts.py`
  - `fund_agent/fund/processors/contracts.py`
  - `fund_agent/fund/data_extractor.py`
  - `tests/fund/test_source_facts.py`
  - `fund_agent/fund/README.md`
  - `docs/reviews/evidence-confirm-productionization-atomic-source-fact-store-s1-implementation-20260625-133727.md`
  - accepted plan artifact sections relevant to S1
- Excluded scope: S2/S3/S4/S5 implementation, live/PDF, product CLI, provider/LLM, network, repository/parser/source-helper commands, unrelated dirty/untracked files, PR/release state.
- Parallel review coverage: none.
- Workspace note: existing dirty/untracked files were present before this review and were not evaluated outside the allowed scope.

## Findings

### S1-CR-001-未修复-高-Composite helper can mark caller-supplied fabricated values as accepted and does not turn absent dependencies into fail-closed partial/missing views

- **入口/函数**: `build_composite_analysis_view()`
- **文件(行号)**:
  - `fund_agent/fund/source_facts.py:270`
  - `fund_agent/fund/source_facts.py:275`
  - `fund_agent/fund/source_facts.py:298`
  - `fund_agent/fund/source_facts.py:304`
  - `fund_agent/fund/source_facts.py:310`
  - `docs/reviews/evidence-confirm-productionization-atomic-source-fact-store-composite-view-implementation-plan-20260625.md:169`
  - `docs/reviews/evidence-confirm-productionization-atomic-source-fact-store-composite-view-implementation-plan-20260625.md:170`
  - `docs/reviews/evidence-confirm-productionization-atomic-source-fact-store-composite-view-implementation-plan-20260625.md:179`
  - `tests/fund/test_source_facts.py:219`
- **输入场景**:
  - Caller passes accepted dependency facts for `fee_schedule.management_fee` and `fee_schedule.custody_fee`, but passes a `value` dict whose child values are unrelated to those facts.
  - Caller passes a `dependency_fact_ids` entry that is absent from `AtomicSourceFactStore`.
- **实际分支**:
  - The helper accepts `value` as an external parameter and never derives or validates it against dependency fact values.
  - It loads dependency facts only to aggregate anchors/gaps and compute status.
  - If all required facts have `status == "accepted"`, it returns `status="accepted"` while preserving the caller-supplied `value`.
  - If a dependency id is absent, `source_facts.get_required()` raises `KeyError`; the helper never returns a `partial` or `missing` view with an explicit gap.
- **预期行为**:
  - The accepted S1 plan requires a pure assembler helper that builds `CompositeAnalysisView` and legacy `ExtractedField[dict]` values from atomic facts for migrated families.
  - The same S1 plan requires duplicate id and missing dependency fail-closed behavior, and states that missing dependency should produce a partial/missing view, not fabricated data.
  - Composite values must be derived compatibility views with dependency fact ids, not a second source-truth object or unchecked caller payload.
- **实际行为**:
  - `build_composite_analysis_view()` can create an accepted composite view whose `value` does not come from the dependency facts.
  - Missing dependency behavior is an uncaught `KeyError`, not a status/gap-bearing derived view.
  - The focused tests cover a dependency fact that exists with `status="missing"`, but not an absent dependency id or a value/fact mismatch.
- **直接证据**:
  - Plan S1 change requires the assembler helper at plan line 169 and missing dependency fail-closed behavior at line 170.
  - Plan S1 tests require "missing dependency produces partial/missing view, not fabricated data" at line 179.
  - Implementation accepts arbitrary `value` at `source_facts.py:275`, reads dependency facts at lines 298-299, marks accepted when required facts are accepted at lines 304-305, and returns the unchanged caller value at line 310.
  - Test `test_build_composite_analysis_view_aggregates_dependencies()` at `tests/fund/test_source_facts.py:219` only verifies a present dependency fact with missing status/gap; it does not verify absent dependency ids or that the view value is derived from fact values.
  - README claims S1 provides a "no-fabrication helper" at `fund_agent/fund/README.md:139`, but the helper does not enforce that claim.
- **影响**:
  - S2/S3 assemblers can accidentally reintroduce opaque composite dict truth by passing a prebuilt dict into the helper while still receiving `status="accepted"` and source fact dependency ids.
  - Evidence Confirm or chapter projection work in later slices could trust an accepted `CompositeAnalysisView` whose visible values are not the audited atomic values.
  - Absent child facts fail as an exception path instead of carrying deterministic partial/missing status and gaps, which weakens the planned fail-closed contract and leaves a test gap at the exact invariant S1 was supposed to establish.
- **建议改法和验证点**:
  - Change the S1 helper contract so composite view values are derived from dependency fact values through an explicit view assembly spec, or validate any supplied dict against dependency fact ids and values before returning accepted/partial status.
  - Handle absent dependency ids inside the helper by returning a `missing` or `partial` view with explicit gaps, unless the accepted plan is amended to make absent dependencies a hard construction error.
  - Add focused tests for: accepted facts plus mismatched caller value is rejected or downgraded; absent dependency id returns partial/missing with a gap; empty dependency ids cannot preserve a non-null view value.
- **修复风险（低/中/高）**: 中. The fix is localized to S1 primitives and tests, but it determines the contract later S2-S5 slices will rely on.
- **严重程度（低/中/高/严重）**: 高.
- **Recommended disposition**: accepted.

## Open Questions

- None blocking beyond S1-CR-001. If the intended contract is "missing dependency raises KeyError" rather than "partial/missing view", the accepted plan must be amended first because current plan text says the opposite.

## Validation

Run:

- `git branch --show-current`
  - `evidence-confirm-productionization`
- `git status --short --branch --untracked-files=all`
  - Branch ahead of origin by 8; scoped dirty files include the S1 implementation files and artifact. Unrelated untracked docs/scripts were present and not reviewed.
- `git show --stat --oneline --decorate --no-renames 25fef99`
  - Confirmed accepted plan commit: `25fef99 gateflow: accept plan for atomic source fact split`.
- `uv run pytest tests/fund/test_source_facts.py -q`
  - `11 passed`
- `uv run pytest tests/fund/test_data_extractor.py -q`
  - `57 passed`
- `uv run pytest tests/fund/processors/test_fund_disclosure_processor.py -q`
  - `199 passed`
- `uv run ruff check fund_agent/fund/source_facts.py fund_agent/fund/data_extractor.py fund_agent/fund/processors/contracts.py tests/fund/test_source_facts.py`
  - `All checks passed`

Not run:

- Broader pytest, live/PDF, product CLI, provider/LLM, network, repository/parser/source-helper commands, PR/remote/release operations. These are outside this review scope or explicitly forbidden.

## Residual Risks

- Covered by S1 fix/re-review: derived-only/no-fabrication invariant and absent dependency fail-closed behavior.
- Covered by later approved slices: default parsed annual child-level atomic emission remains S2A/S2B.
- Covered by later approved slices: explicit `FundDisclosureDocument` source-truth atomic preservation remains S3.
- Covered by later approved slices: `ChapterFactProvider` and Evidence Confirm bridge fields remain S4/S5.
- Assigned to later exact authorization gates: live/PDF re-evidence, release/readiness, tag and release.
- Not reviewed: unrelated dirty/untracked files outside the allowed target list.

## Stop Condition

Stopped after writing this single review artifact. No production/test/docs fix, commit, push, PR mutation, mark-ready, merge, tag, release, live/PDF, product CLI, provider/LLM, network, repository/parser/source-helper command, or S2/S3/S4/S5 implementation was performed.
