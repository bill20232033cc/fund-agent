# MVP Incomplete LLM Run Artifact Retention Slice 1 Implementation Evidence

## Self-check

- Self-check: pass.
- Current gate / role: implementation for `MVP incomplete LLM run artifact retention gate`; implementation specialist only.
- Scope: implemented only Slice 1 incomplete `analyze --use-llm` typed result local artifacts.
- Forbidden scope confirmation: no chapter acceptance calibration, no progress UX, no provider timeout budget change, no score-loop entry, no quality gate/auditor/repair-budget semantic change, no deterministic fallback.
- External action confirmation: no stage, no commit, no push, no PR, no `$gateflow`, no `/gateflow`, no `$phaseflow`, no `/phaseflow`.

## Changed Files

- `.gitignore`
- `fund_agent/services/llm_run_artifacts.py`
- `fund_agent/ui/cli.py`
- `tests/services/test_llm_run_artifacts.py`
- `tests/ui/test_cli.py`
- `docs/reviews/mvp-incomplete-llm-run-artifact-retention-slice1-implementation-evidence-20260602.md`

## Implemented Items Mapped To Plan

- Added Service-owned `write_llm_incomplete_run_artifacts()` for typed `FundLLMAnalysisResult` only.
- Writes `reports/llm-runs/<fund_code>-<report_year>-<timestamp>-<run_id>/` with `manifest.json`, `summary.json`, `chapters/*.json`, writer draft markdown, repair draft markdown, and normalized auditor feedback markdown.
- Added `.gitignore` rule for `reports/llm-runs/`.
- Serialized chapter status, first failed diagnostic, chapter matrix, writer drafts, repair drafts, normalized auditor feedback, prompt-contract diagnostics, runtime scalar diagnostics, repair decisions, and final assembly issue summaries.
- Kept allowlist-first serialization; no whole-object `asdict()` / `__dict__` serialization.
- Added redaction scanner for saved text and allowlisted JSON text fields, with `redaction_applied` / `redaction_count` in manifest, summary, and chapter metadata.
- CLI now writes artifacts only for typed incomplete `--use-llm` results, including Host failed state with typed `operation_result`; it prints one safe manifest path line to stderr.
- Artifact write failure prints only a safe warning with exception type and preserves original fail-closed exit path.

## Safety / Non-Leakage

- Not saved: prompts, raw provider HTTP body/headers, API keys, Authorization/Bearer/cookies, full provider config, raw provider response, raw auditor response, stack traces, partial final report.
- Direct helper rejects accepted final reports by default.
- CLI does not write artifacts for config/construction preflight failures, deterministic analyze, checklist, Host failure without typed result, or quality gate block/not-run paths.

## Validation

- `uv run pytest tests/services/test_llm_run_artifacts.py -q` -> pass, `6 passed`.
- `uv run pytest tests/ui/test_cli.py -q` -> pass, `59 passed`.
- `uv run ruff check fund_agent/services/llm_run_artifacts.py tests/services/test_llm_run_artifacts.py fund_agent/ui/cli.py tests/ui/test_cli.py` -> pass.
- `uv run pytest tests/services/test_llm_run_artifacts.py tests/ui/test_cli.py tests/services/test_chapter_orchestrator.py tests/services/test_fund_analysis_service_llm.py -q` -> pass, `156 passed`.
- `uv run ruff check .` -> pass.
- `python -m py_compile fund_agent/services/llm_run_artifacts.py fund_agent/ui/cli.py` -> pass.

## Docs Decision

- No README update. No new CLI flag or user-visible command contract was added; behavior is automatic local diagnostic retention for incomplete `--use-llm` only.
- This implementation evidence records the artifact directory and retention decision. Lifecycle cleanup remains manual local cleanup as recorded in `manifest.json`.

## Residual Risks / Deferred Owners

- Local artifact lifecycle and disk cleanup: deferred to future observability/control policy; current manifest records `retention_policy=manual_local_cleanup`.
- Real provider nondeterminism and real smoke rerun: not executed in this slice; future controller/work unit can rerun with credentials/network and inspect generated local artifacts.
- Chapter 2/3/6 acceptance calibration: deferred to future `MVP real LLM chapter acceptance calibration gate` after artifact evidence exists.
- Progress/timeout UX, provider runtime budget calibration, and score-loop entry remain deferred to their future gates.

## Completion Status

Slice 1 implementation complete and locally validated. No staging, commit, push, PR, gateflow, or phaseflow action performed.
