# MVP Independent Body Chapter Execution Controller Judgment

## Gate / Role

- Gate: `MVP independent body chapter execution gate`
- Role: Gateflow controller, not implementation worker.
- Date: 2026-05-31 13:55 CST.
- Branch: `codex/local-reconciliation`.
- PR state checked before this gate: PR #21 remains draft/open; this gate made no PR, push, merge, release or external state changes.

## Judgment

**Status: accepted locally.**

Template body chapters 1-6 now execute independently after global preflight passes. A failure in chapter 1 no longer creates synthetic `dependency_missing` rows for chapters 2-6. The final report path remains fail-closed: partial/all-chapter matrices are diagnostic only and cannot become a complete accepted report unless required body chapters are accepted.

## Scope Boundary

Reviewed accepted implementation scope:

- `fund_agent/services/chapter_orchestrator.py`
- `fund_agent/ui/cli.py`
- `tests/services/test_chapter_orchestrator.py`
- `tests/services/test_final_chapter_assembler.py`
- `tests/ui/test_cli.py`

No golden, fixtures, score, quality gate, Host, Agent, dayu, provider auth/config, writer/auditor primitive, template or PR-state changes were accepted by this gate.

## Accepted Artifacts

- Plan: `docs/reviews/mvp-independent-body-chapter-execution-plan-20260531.md`
- Plan review MiMo: `docs/reviews/mvp-independent-body-chapter-execution-plan-review-mimo-20260531.md`
- Plan review GLM: `docs/reviews/mvp-independent-body-chapter-execution-plan-review-glm-20260531.md`
- Implementation evidence: `docs/reviews/mvp-independent-body-chapter-execution-implementation-evidence-20260531.md`
- Code review MiMo: `docs/reviews/mvp-independent-body-chapter-execution-code-review-mimo-20260531.md`
- Code review GLM: `docs/reviews/mvp-independent-body-chapter-execution-code-review-glm-20260531.md`

## Controller Review Findings

- `ChapterOrchestrationPolicy.fail_fast` is now a legacy compatibility field with default `False`.
- `orchestrate_chapters()` no longer branches on `policy.fail_fast`, no longer uses `stop_remaining`, and runs `_run_single_chapter()` for every requested body chapter.
- `dependency_missing` remains mapped from the explicit writer stop reason `chapter_requires_accepted_conclusions`; it is no longer used to represent prior body chapter failure.
- `ChapterOrchestrationResult` still preserves `first_failed` diagnostics and now also preserves all chapter rows for downstream diagnostic/score-loop use.
- CLI incomplete-result stderr now includes a safe all-chapter matrix using only chapter id, status, stop reason, failure category and failure subcategory.
- Final assembly remains fail-closed and includes only accepted body chapters in `source_accepted_chapter_ids`.

## Review Disposition

- MiMo code review verdict: PASS, no blocking findings.
- GLM code review verdict: PASS, no blocking findings.
- Shared non-blocking residual: `_skipped_result()` is now unreachable in the normal body chapter path. The approved plan allowed retaining it for narrow compatibility; no production path calls it for body chapter fail-fast.

## Validation

Passed:

```bash
uv run ruff check fund_agent/services/chapter_orchestrator.py fund_agent/services/final_chapter_assembler.py fund_agent/ui/cli.py tests/services/test_chapter_orchestrator.py tests/services/test_final_chapter_assembler.py tests/ui/test_cli.py
```

Result: `All checks passed!`

Passed:

```bash
uv run pytest tests/services/test_chapter_orchestrator.py tests/services/test_final_chapter_assembler.py tests/ui/test_cli.py -q
```

Result: `141 passed in 0.98s`

Passed:

```bash
uv run ruff check .
```

Result: `All checks passed!`

Passed:

```bash
uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q
```

Result: `1196 passed in 5.75s`; total coverage `91.88%`, required `50%`.

Passed deterministic analyze smoke:

```bash
uv run fund-analysis analyze 006597 --report-year 2024
```

Result: exit `0`, deterministic 0-7 report rendered; quality gate status `warn` preserved.

Passed deterministic checklist smoke:

```bash
uv run fund-analysis checklist 006597 --report-year 2024
```

Result: exit `0`, checklist summary rendered; quality gate status `warn` preserved.

Passed missing-config fail-closed smoke:

```bash
env -u FUND_AGENT_LLM_PROVIDER -u FUND_AGENT_LLM_BASE_URL -u FUND_AGENT_LLM_API_KEY -u FUND_AGENT_LLM_MODEL uv run fund-analysis analyze 006597 --report-year 2024 --use-llm
```

Result: exit `1`, stdout empty, stderr `LLM provider 配置错误：missing FUND_AGENT_LLM_PROVIDER`.

Passed artifact/report secret scan:

```bash
rg -n -S "(Authorization:\\s*Bearer|Bearer\\s+[A-Za-z0-9._-]{20,}|sk-[A-Za-z0-9]{20,}|FUND_AGENT_LLM_API_KEY=|api[_-]?key\\s*[:=]\\s*['\"][^'\"< ]{8,})" docs/reviews/mvp-independent-body-chapter-execution-* reports/quality-gate-runs/analyze-006597-2024-20260531T055336053339Z reports/quality-gate-runs/checklist-006597-2024-20260531T055414368023Z
```

Result: no matches. A broader source scan found a deliberately fake canary in a test assertion (`Authorization: Bearer sk-secret`) used to prove CLI stderr does not leak unsafe strings; it is not artifact/report evidence and not a real secret.

## Acceptance Criteria Mapping

| Criterion | Judgment |
|---|---|
| Chapters 1-6 no longer fail-fast on prior body failure | PASS |
| Every body chapter keeps its own status / stop reason / category / subcategory | PASS |
| `first_failed` no longer hides all-chapter matrix | PASS |
| `dependency_missing` only used for true dependency, not prior body failure | PASS |
| Final report remains fail-closed and excludes blocked chapters | PASS |
| CLI/provider diagnostic can show all chapter rows safely | PASS |
| Deterministic analyze/checklist behavior unchanged | PASS |

## Residuals

- Real provider smoke was not rerun in this gate. The accepted outcome is code-level independence and diagnostic readiness: the next real provider smoke should now expose independent chapter 1-6 rows instead of synthetic chapter 2-6 `dependency_missing`.
- `_skipped_result()` is retained but unreachable for body chapter fail-fast. It may be removed in a future cleanup if no true scope/dependency skip path needs it.
- Gate B real provider smoke remains not accepted until a real `006597 / 2024 --use-llm` run produces complete 0-7 output or a new precise blocker matrix.
- Score loop remains future work and was not implemented here.

## Next Smallest Entry Point

Proceed to `MVP real provider smoke acceptance rerun with independent body chapter matrix` or fold it into the next smoke acceptance gate. The next run should verify whether chapters 2-6 now execute independently under the real provider and should classify the resulting all-chapter matrix without returning to provider config/auth.
