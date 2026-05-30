# MVP Gate 4 Slice 4A final_chapter_assembler implementation evidence

日期：2026-05-30
角色：AgentCodex implementation worker
Gate：`MVP Gate 4 Slice 4A: Service final_chapter_assembler implementation gate`
状态：implemented locally；未 commit、未 push、未 PR。

## Source of truth

- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/design.md` §5.4 / §5.4.1
- `docs/reviews/mvp-gate4-final-assembler-cli-plan-20260530.md`
- `docs/reviews/mvp-gate4-final-assembler-cli-plan-decision-20260530.md`
- `docs/reviews/mvp-gate3-chapter-orchestrator-controller-judgment-20260530.md`
- `fund_agent/services/chapter_orchestrator.py`
- `fund_agent/fund/analysis/final_judgment.py`
- `tests/services/test_chapter_orchestrator.py`

## Files changed

- `fund_agent/services/final_chapter_assembler.py`
  - Added Service-owned `final_chapter_assembler.v1` typed contract.
  - Added `FinalChapterAssembler` / `assemble_final_chapters()`.
  - Added deterministic chapter 7 assembly from existing `FinalJudgmentDecision`.
  - Added Gate 4-local `FinalChapter7Summary` typed current-action source for chapter 0.
  - Added deterministic chapter 0 assembly from accepted conclusions only.
  - Added fail-closed policy for partial/non-accepted Gate 3 results and missing accepted drafts/conclusions.
- `fund_agent/services/__init__.py`
  - Exported Gate 4 public Service API and `AcceptedChapterConclusion`.
- `tests/services/test_final_chapter_assembler.py`
  - Added focused Slice 4A tests for contract, fail-closed paths, chapter 0/7 semantics and render order.
- `tests/README.md`
  - Documented the new Service test and local run command.
- `docs/reviews/mvp-gate4-final-assembler-slice4a-implementation-evidence-20260530.md`
  - This evidence artifact.

## Boundary confirmation

- Did not edit `fund_agent/fund/**`.
- Did not edit `fund_agent/ui/cli.py`.
- Did not edit `fund_agent/services/fund_analysis_service.py`.
- Did not edit `docs/design.md`, `docs/current-startup-packet.md` or `docs/implementation-control.md`.
- Did not edit golden, score, quality gate, final judgment semantic files, Host/Agent/dayu.
- Did not add production LLM provider construction.
- Did not read repository/PDF/cache/source helper/downloader/parser from the new assembler.
- Did not pass business parameters through `extra_payload`.
- Did not commit, push or create PR.

## Controller amendments coverage

- A4: chapter 0 does not re-apply `preferred_lens`, ITEM_RULE or fund type rules; `FinalAssemblyPolicy` only accepts fixed `(1, 2, 3, 4, 5, 6)` body chapters.
- A5: tests cover sparse and truncated accepted conclusions; chapter 0 emits fallback/informational issues and does not invent absent numbers such as `9.99%`, `2亿` or `低于1%`.
- A6: chapter 7 combines `FinalJudgmentDecision.reasons` with short snippets from chapter 1-6 accepted conclusions, while keeping `selected_judgment` as the sole action truth.
- A7: chapter 0 current action comes from Gate 4-local typed `FinalChapter7Summary.selected_judgment_label`, not markdown parsing.
- A8: implementation builds chapter 7 summary/markdown before chapter 0; final report render order is `0 -> 1-6 -> 7`, asserted by tests.

## Validation

```text
uv run ruff check fund_agent/services/final_chapter_assembler.py tests/services/test_final_chapter_assembler.py
```

Result: `All checks passed!`

```text
uv run pytest tests/services/test_final_chapter_assembler.py -q
```

Result: `9 passed in 0.47s`

```text
uv run pytest tests/services/test_chapter_orchestrator.py tests/fund/test_chapter_writer.py tests/fund/test_chapter_auditor.py tests/fund/test_chapter_facts.py -q
```

Result: `81 passed in 0.52s`

```text
git diff --check
```

Result: clean.

## Residuals

- Slice 4B Service `analyze_with_llm()` remains unimplemented.
- Slice 4C CLI `--use-llm` remains unimplemented.
- Slice 4D production LLM provider construction remains a separate future gate.
- Chapter 0/7 LLM polish and LLM audit remain out of scope.
- Evidence Confirm / E2 source verification remains out of scope.
- Host/Agent/dayu integration remains deferred to Route C Gate 5.
- Chapter 0 deterministic compression can be terse when Gate 3 accepted conclusions are sparse; current behavior is correctness-first with informational issues rather than widening inputs.
