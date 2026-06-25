# Atomic Source Fact Store / Composite Analysis View Split S6 Code Review

## Scope

- Mode: current workspace S6 docs/control review.
- Branch: `evidence-confirm-productionization`.
- Base / checkpoint: HEAD `a2e4255` (`control: advance atomic source fact split to s6`); S5 accepted local commit `29fbb79`.
- Reviewed files:
  - `docs/design.md`
  - `fund_agent/fund/README.md`
  - `docs/implementation-control.md`
  - `docs/current-startup-packet.md`
  - `docs/reviews/evidence-confirm-productionization-atomic-source-fact-store-s6-implementation-20260625-155918.md`
- Explicitly excluded: production code/test edits, live/PDF/repository/source-helper/parser/provider/LLM/product CLI commands, PR/remote/tag/release/readiness actions, and unrelated dirty/untracked residue.
- Review questions covered:
  - atomic source facts as extraction truth vs composite fields/views as compatibility or derived analysis views;
  - absence of overclaim for live/PDF, product CLI, strict V2, ECQ, quality-gate, report body, checklist, provider/LLM, FDD default-on, tag/release/readiness;
  - control-doc consistency with S6 current gate and S5 commit `29fbb79`;
  - whether missing required test paths should block S6.

## Findings

未发现实质性问题。

Direct evidence:

- `docs/design.md:7` states S1-S5 have moved current structured extraction truth to Fund Processor/Extractor atomic source facts, with `FundProcessorResult.source_facts` as the Processor atomic fact store and `StructuredFundDataBundle.source_facts` as mirror only; it also states composite fields remain derived/compatibility and do not change V2/ECQ/quality-gate, report body, CLI, renderer, checklist, provider/LLM, product CLI, FDD default-on, live/PDF, tag, release, or readiness.
- `fund_agent/fund/README.md:139` states the same ownership split and preserves the no-fabrication rule for derived views; `fund_agent/fund/README.md:676` repeats the module-level current fact and leaves unproven real-report correctness, golden/readiness, and release to later gates.
- Code spot-check supports the doc claim: `fund_agent/fund/processors/contracts.py:644` defines `source_facts` as the Processor atomic source facts truth surface; `fund_agent/fund/data_extractor.py:221` and `fund_agent/fund/data_extractor.py:253` define the bundle field as a mirror; `fund_agent/fund/chapter_facts.py:298` to `fund_agent/fund/chapter_facts.py:310` carries source facts plus derived views; `fund_agent/fund/chapter_facts.py:1353` to `fund_agent/fund/chapter_facts.py:1371` projects atomic facts through `source_fact_ids`; `fund_agent/fund/chapter_facts.py:1399` to `fund_agent/fund/chapter_facts.py:1413` projects composite views through `derived_view_id`; `fund_agent/fund/evidence_confirm.py:1884` to `fund_agent/fund/evidence_confirm.py:1898` resolves material values through those bridge ids and fails closed on unresolved bridge targets.
- `docs/current-startup-packet.md:27` sets the next entry point to S6 code review and explicitly says not to treat S6 implementation as accepted code review or release/readiness evidence.
- `docs/implementation-control.md:10` and `docs/implementation-control.md:50` to `docs/implementation-control.md:53` align current gate, S5 commit `29fbb79`, and S6 review boundary while preserving release/readiness `NOT_READY`.
- `docs/reviews/evidence-confirm-productionization-atomic-source-fact-store-s6-implementation-20260625-155918.md:21` to `docs/reviews/evidence-confirm-productionization-atomic-source-fact-store-s6-implementation-20260625-155918.md:28` states S6 did not touch product behavior or forbidden live/external surfaces.

## Open Questions

- 无。

## Residual Risk

- The required first pytest command names two paths that do not exist in this checkout: `tests/fund/processors/test_active_annual_atomic.py` and `tests/fund/processors/test_fund_disclosure_processor_atomic.py`. I do not treat this as an S6 blocker because existing renamed/current processor suites cover the same atomic/source fact surfaces and passed, and S6 is docs/no-live truth sync with no production or test edits. This remains a controller-owned stale plan/test-path cleanup residual, not release/readiness evidence.
- This review did not perform live/PDF, repository/source-helper/parser, provider/LLM, product CLI, PR, tag, release, or readiness checks by instruction. Those remain later-gate proof obligations.
- Existing unrelated dirty/untracked residue remains untouched and was not reviewed.

## Validation

- `git branch --show-current` -> `evidence-confirm-productionization`.
- `git status --short --branch --untracked-files=all` showed S6 dirty docs plus unrelated dirty/untracked residue; no staging/commit/push was performed.
- `git log --oneline -8` confirmed HEAD `a2e4255` and S5 accepted commit `29fbb79`.
- `git diff --check -- docs/design.md fund_agent/fund/README.md docs/implementation-control.md docs/current-startup-packet.md docs/reviews/evidence-confirm-productionization-atomic-source-fact-store-s6-implementation-20260625-155918.md` -> no output.
- Required command rerun:
  - `uv run pytest tests/fund/test_source_facts.py tests/fund/processors/test_active_annual_atomic.py tests/fund/processors/test_fund_disclosure_processor_atomic.py tests/fund/test_chapter_facts_atomic.py tests/fund/test_evidence_confirm_atomic.py -q`
  - Result: exit code 4; `ERROR: file or directory not found: tests/fund/processors/test_active_annual_atomic.py`; no tests ran.
- Supplemental existing atomic/source fact no-live suite rerun:
  - `uv run pytest tests/fund/test_source_facts.py tests/fund/processors/test_active_annual_processor.py tests/fund/processors/test_fund_disclosure_processor.py tests/fund/test_chapter_facts_atomic.py tests/fund/test_evidence_confirm_atomic.py -q`
  - Result: `243 passed in 0.54s`.
- Existing compatibility no-live suite rerun:
  - `uv run pytest tests/fund/test_data_extractor.py tests/fund/test_chapter_facts.py tests/fund/test_evidence_confirm.py tests/fund/test_evidence_confirm_sources.py tests/fund/test_evidence_confirm_value_diagnostics.py -q`
  - Result: `180 passed in 0.97s`.

## Verdict

S6_CODE_REVIEW_PASS_READY_FOR_ACCEPTED_SLICE_COMMIT_NOT_READY
