# MVP Independent Body Chapter Execution Implementation Evidence

## Gate / Role

- Gate: MVP independent body chapter execution gate.
- Role: Gateflow implementation worker, not controller.
- Approved plan: `docs/reviews/mvp-independent-body-chapter-execution-plan-20260531.md`.
- Scope: implement approved plan slices only; no commit, push, PR, release, score loop, Host/Agent/dayu, Fund writer/auditor, config, provider or golden changes.

## Worker Self-Check

- Assigned gate/scope remained unchanged during implementation.
- Touched only allowed implementation files and this evidence artifact.
- Did not revert, clean, delete, rename, stage, commit, push or open PR.
- Did not run real provider.
- This artifact records only safe scalar outcomes and validation results; no sensitive request, response or credential material is recorded.

## Changed Files

- `fund_agent/services/chapter_orchestrator.py`
- `fund_agent/ui/cli.py`
- `tests/services/test_chapter_orchestrator.py`
- `tests/services/test_final_chapter_assembler.py`
- `tests/ui/test_cli.py`
- `docs/reviews/mvp-independent-body-chapter-execution-implementation-evidence-20260531.md`

No production change was made to `fund_agent/services/final_chapter_assembler.py`.

## Implemented Items

- Removed body chapter fail-fast stop behavior for template chapters 1-6.
- Kept `ChapterOrchestrationPolicy.fail_fast` for API compatibility, changed default to `False`, and documented it as a legacy/no-op for body chapters.
- Ensured the body chapter loop does not branch on `policy.fail_fast`.
- Preserved `dependency_missing` only through the explicit writer stop reason mapping for true accepted-conclusion dependency, not prior body chapter failure.
- Ensured requested body chapters each produce a real row after global preflight passes.
- Kept final assembly fail-closed behavior via tests: incomplete status, `report_markdown is None`, accepted source ids include only accepted body chapters.
- Added CLI incomplete stderr all-chapter matrix beside first-failed summary, with only chapter id, status, stop reason, failure category and failure subcategory.
- Did not implement score loop.

## Test Coverage Added / Strengthened

- Orchestrator:
  - chapter 1 timeout followed by chapters 2-6 still entering writer;
  - `fail_fast=True` legacy/no-op behavior;
  - mixed accepted/blocked/failed matrix preserves each chapter outcome;
  - all requested chapters blocked still execute and overall status is blocked;
  - first-failed diagnostics do not hide complete matrices;
  - `dependency_missing` remains tied to the true writer dependency stop reason and is not produced by a prior body failure.
- Final assembler:
  - partial/all-row orchestration remains incomplete;
  - blocked/all-row orchestration remains incomplete;
  - `source_accepted_chapter_ids` includes only accepted body chapter ids and excludes blocked required chapters.
- CLI:
  - incomplete stderr contains first-failed summary and all-chapter matrix;
  - matrix includes accepted and failed rows;
  - matrix path is covered by negative leakage assertions for unsafe diagnostic fields and credential-like labels.

## Validation Results

Passed:

```bash
uv run ruff check fund_agent/services/chapter_orchestrator.py fund_agent/services/final_chapter_assembler.py fund_agent/ui/cli.py tests/services/test_chapter_orchestrator.py tests/services/test_final_chapter_assembler.py tests/ui/test_cli.py
```

Result: `All checks passed!`

Passed:

```bash
uv run pytest tests/services/test_chapter_orchestrator.py tests/services/test_final_chapter_assembler.py tests/ui/test_cli.py -q
```

Result: `141 passed in 0.99s`

Additional local hygiene check:

```bash
git diff --check -- fund_agent/services/chapter_orchestrator.py fund_agent/services/final_chapter_assembler.py fund_agent/ui/cli.py tests/services/test_chapter_orchestrator.py tests/services/test_final_chapter_assembler.py tests/ui/test_cli.py
```

Result: passed with no whitespace errors.

## Docs Decision

- No README update. The public command shape and user workflow did not change; this gate only changes LLM incomplete diagnostics and Service-layer body chapter execution semantics.
- The required durable evidence is this implementation artifact.

## Residual Risks

- Real provider smoke was not run by instruction.
- Full suite was not run; controller will run broader validation.
- Score loop remains unimplemented by scope and is left for the later score-loop gate.
- Existing worktree contains prior accepted local gate changes outside this assigned scope; they were not modified or cleaned.

## Completion Status

- Implementation scope complete.
- Validation complete for required targeted commands.
- Self-check: pass.
