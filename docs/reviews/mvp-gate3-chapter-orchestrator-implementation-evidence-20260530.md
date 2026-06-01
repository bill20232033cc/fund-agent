# MVP Gate 3 chapter_orchestrator implementation evidence

日期：2026-05-30

角色：AgentCodex implementation worker。只实现 accepted Gate 3 plan；未 commit、未 push、未创建 PR、未做 release/promotion。

## Preflight

- Branch: `codex/local-reconciliation`
- Initial `git status --short`: only unrelated untracked files; no tracked dirty changes before implementation.
- Accepted plan commit: `beb6891`
- Accepted plan: `docs/reviews/mvp-gate3-chapter-orchestrator-plan-20260530.md`
- Controller decision: `docs/reviews/mvp-gate3-chapter-orchestrator-plan-decision-20260530.md`

## Changed files

- `fund_agent/services/chapter_orchestrator.py`
- `fund_agent/services/__init__.py`
- `tests/services/test_chapter_orchestrator.py`
- `fund_agent/README.md`
- `tests/README.md`
- `docs/reviews/mvp-gate3-chapter-orchestrator-implementation-evidence-20260530.md`

No other tracked files were modified.

## Public contracts implemented

- Added Service-owned `ChapterOrchestrator` façade and `orchestrate_chapters()`.
- Added explicit typed input/result/policy/client bundle:
  - `ChapterOrchestrationInput`
  - `ChapterOrchestrationPolicy`
  - `ChapterOrchestratorLLMClients`
  - `ChapterOrchestrationResult`
- Inputs are explicit and mutually exclusive: caller provides either `StructuredFundDataBundle` or `ChapterFactProjection`; no `extra_payload`.
- Target chapters are restricted to template chapters 1-6. Chapters 0 and 7 are rejected by policy and not generated.
- Bundle input uses injected `ChapterFactProvider` or a default provider only to project requested chapter ids.
- Projection input is consumed directly and must uniquely cover requested chapters.
- Writer/auditor clients are explicit injection only; no production provider construction, env/config loading, SDK import, HTTP client import, or default fake path.
- Writer stop reason mapping is complete and one-to-one for current `ChapterWriteStopReason`.
- Auditor unavailable with `run_llm_audit=True` globally blocks before writer calls and before repair loop.
- `_decide_repair()` follows the accepted decision table; `patch` maps to budget-bounded best-effort regenerate, and `max_repair_attempts=0` does not retry.
- Accepted conclusions are deterministic, extracted from `### 结论要点` or `## 结论要点`, fallback to first 3 non-empty lines, and hard-capped at 500 characters.
- Exact `fund_agent/services/__init__.py` exports were added for:
  - `ChapterOrchestrator`
  - `ChapterOrchestrationInput`
  - `ChapterOrchestrationResult`
  - `ChapterOrchestrationPolicy`
  - `ChapterOrchestratorLLMClients`
  - `build_chapter_orchestration_input`
  - `orchestrate_chapters`

## No-scope-creep proof

- Did not modify `docs/design.md`, `docs/current-startup-packet.md`, `docs/implementation-control.md`, `AGENTS.md`, or `docs/fund-analysis-template-draft.md`.
- Did not change deterministic `fund-analysis analyze/checklist` behavior or CLI `--use-llm`.
- Did not add final assembler, chapter 0 assembly, or chapter 7 final judgment assembly.
- Did not add Host/Agent/dayu packages, dependencies, runtime, runner, ToolRegistry, ToolTrace, session/run lifecycle, concurrency, cancellation, resume, memory, or outbox.
- Did not read or call repository/PDF/cache/source helper/downloader/parser from the Service orchestrator.
- Did not add real LLM provider SDK/env/config/default fake pass. Fake LLM clients exist only in `tests/services/test_chapter_orchestrator.py`.
- Did not modify golden fixtures/answers/manifests, score, snapshot, quality gate, FQ0-FQ6, promotion state, release state, or final judgment.

## Validation

```text
uv run ruff check .
All checks passed!
```

```text
uv run pytest tests/services/test_chapter_orchestrator.py -q
29 passed in 0.54s
```

```text
uv run pytest tests/fund/test_chapter_writer.py tests/fund/test_chapter_auditor.py tests/fund/test_chapter_facts.py -q
51 passed in 0.42s
```

```text
uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q
1039 passed in 4.81s
Total coverage: 91.73%
fund_agent/services/chapter_orchestrator.py: 93%
```

```text
git diff --check
```

Result: clean.

## Residual risks

- `patch` remains mapped to best-effort regenerate with the same writer input because Gate 2 has no typed patch API. This is budget-bounded and covered by retry/budget exhaustion tests.
- `partial` result is not a complete report. Gate 3 only exposes it; Gate 4 must decide reject/degrade/incomplete assembly behavior.
- E2 source verification and chapter 5 cross-period evidence remain deferred; Gate 3 has no source access.
- Production LLM provider construction remains deferred to a future provider/config or Gate 4 decision.
