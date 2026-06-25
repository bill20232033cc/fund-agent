# Code Review - Atomic Source Fact Store / Composite Analysis View Split S6

## Scope

- Mode: scoped S6 code/docs review.
- Branch: `evidence-confirm-productionization`.
- Reviewed files:
  - `docs/design.md`
  - `fund_agent/fund/README.md`
  - `docs/implementation-control.md`
  - `docs/current-startup-packet.md`
  - `docs/reviews/evidence-confirm-productionization-atomic-source-fact-store-s6-implementation-20260625-155918.md`
- Base/checkpoints: S5 accepted local commit `29fbb79`; S5-to-S6 control sync local commit `a2e4255`.
- Excluded scope: production code changes, test code changes, live/PDF, repository/source-helper/parser/provider/LLM/product CLI commands, PR/tag/release/readiness mutation, and unrelated dirty/untracked residue.
- Parallel review coverage: none.

## Findings

### F-01-未修复-中-Resume checklist still routes the next entry to S6 implementation instead of S6 code review

- **入口/函数**: control-doc resume path for the current gate.
- **文件(行号)**: `docs/implementation-control.md:681`.
- **输入场景**: A later controller/reviewer resumes from `docs/implementation-control.md` after the S6 implementation artifact has already been written.
- **实际分支**: The top control update says the next gate is S6 code review, but the resume checklist still says the current next entry is `Atomic Source Fact Store / Composite Analysis View Split S6 Regression / Docs / Control Sync Gate` and says S6 must verify/sync.
- **预期行为**: After S6 implementation evidence, the control surface should route the next actor to S6 code review/controller decision, not back to implementation/regression/docs sync.
- **实际行为**: One current-truth entry routes to S6 code review, while the resume checklist still routes to the pre-review S6 implementation gate.
- **直接证据**: `docs/implementation-control.md:10` says "next gate is S6 code review"; `docs/current-startup-packet.md:27` says "Next entry point is S6 code review"; `docs/implementation-control.md:681` still says "Current next entry is ... S6 Regression / Docs / Control Sync Gate" and describes S6 as work still to perform.
- **影响**: Resume routing can repeat or mis-scope the already completed S6 docs/regression implementation instead of moving to code-review/controller disposition. This is control-plane drift, not production behavior drift.
- **建议改法和验证点**: Update only the resume checklist line so it names S6 code review/controller disposition as the current next entry, preserves S5 commit `29fbb79`, records that S6 implementation evidence exists, and keeps live/PDF/product CLI/PR/tag/release/readiness outside scope. Re-run targeted `rg` for `Current next entry is .*S6 Regression` and `git diff --check` on the touched control docs.
- **修复风险（低/中/高）**: 低.
- **严重程度（低/中/高/严重）**: 中.

## Open Questions

- 无.

## Residual Risk

- The required first pytest command remains stale because `tests/fund/processors/test_active_annual_atomic.py` and `tests/fund/processors/test_fund_disclosure_processor_atomic.py` do not exist in this checkout. I do not treat this as an S6 blocker by itself: the S6 artifact records the failure, existing corresponding processor tests are present without the `_atomic` suffix, and the supplemental atomic/source-fact suite passed. This should remain a plan/test-path cleanup residual unless the controller requires exact path restoration.
- S6 remains no-live and does not prove live/PDF, product CLI, strict V2, ECQ, quality-gate, report body, checklist, provider/LLM, `FundDisclosureDocument` default-on, tag, release, or readiness.
- Existing unrelated dirty/untracked residue was observed and left untouched.

## Validation

- `git branch --show-current` -> `evidence-confirm-productionization`.
- `git status --short` showed the expected scoped S6 docs changes plus existing unrelated residue; no staging/commit/push/PR/tag/release action was performed.
- `git show --stat --oneline 29fbb79` confirmed S5 accepted local commit `29fbb79 gateflow: accept atomic source fact split s5`.
- `git show --stat --oneline a2e4255` confirmed S5-to-S6 control sync local commit `a2e4255 control: advance atomic source fact split to s6`.
- `uv run pytest tests/fund/test_source_facts.py tests/fund/processors/test_active_annual_atomic.py tests/fund/processors/test_fund_disclosure_processor_atomic.py tests/fund/test_chapter_facts_atomic.py tests/fund/test_evidence_confirm_atomic.py -q` failed before collection because the two `_atomic.py` processor test files do not exist.
- `uv run pytest tests/fund/test_source_facts.py tests/fund/processors/test_active_annual_processor.py tests/fund/processors/test_fund_disclosure_processor.py tests/fund/test_chapter_facts_atomic.py tests/fund/test_evidence_confirm_atomic.py -q` -> `243 passed in 0.89s`.
- `uv run pytest tests/fund/test_data_extractor.py tests/fund/test_chapter_facts.py tests/fund/test_evidence_confirm.py tests/fund/test_evidence_confirm_sources.py tests/fund/test_evidence_confirm_value_diagnostics.py -q` -> `180 passed in 1.34s`.
- `git diff --check -- docs/design.md fund_agent/fund/README.md docs/implementation-control.md docs/current-startup-packet.md` -> passed.

## Verdict

S6_CODE_REVIEW_FINDINGS_NEED_FIX_NOT_READY
