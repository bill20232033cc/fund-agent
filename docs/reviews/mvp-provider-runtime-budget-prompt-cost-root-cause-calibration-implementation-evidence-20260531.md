# MVP Provider Runtime Budget and Prompt-Cost Root-Cause Calibration Implementation Evidence

- Gate: `MVP provider runtime budget and prompt-cost root-cause calibration gate`
- Role: implementation worker only; no controller action, no commit, no push, no PR state change, no merge, no release.
- Date: 2026-05-31

## Changed Files

- `fund_agent/fund/chapter_writer.py`
  - Added safe writer prompt-cost diagnostic payload `chapter_prompt_cost_diagnostic_payload.v1`.
  - Refactored writer prompt rendering into component fragments: protocol, contract, must_answer, must_not_cover, required_output, facts, anchors, repair_context.
  - Added compact writer payload mode preserving fact ids, source field ids, status, missing reason, evidence anchor ids and anchor source metadata.
  - Added deterministic `value_summary`: top-level scalar fields/values, list lengths, nested dict key names only; no natural-language inference.
- `fund_agent/services/llm_provider.py`
  - Added effective per-operation timeout selection for writer initial, auditor and writer repair.
  - Kept retry bounded and timeout-only; non-timeout provider runtime errors still return one diagnostic and do not retry.
  - Added safe diagnostics for timeout seconds, max attempts, backoff, budget kind and repair timeout fallback.
- `fund_agent/services/chapter_orchestrator.py`
  - Added runtime diagnostic root-cause hint classification and prompt-cost allowlisted serializer.
  - Ensured auditor timeout hint can only be `small_prompt_provider_timeout` or `provider_runtime_timeout_uncalibrated` for timeout rows.
  - Added `prompt_payload_mode` policy plumbing so explicit CLI `--use-llm` can use compact writer payloads.
- `fund_agent/config/llm.py`
  - Added `FUND_AGENT_LLM_WRITER_TIMEOUT_SECONDS`, `FUND_AGENT_LLM_AUDITOR_TIMEOUT_SECONDS`, `FUND_AGENT_LLM_REPAIR_TIMEOUT_SECONDS`.
  - Preserved legacy timeout env fallback and existing max attempts/backoff/max output semantics.
- `fund_agent/ui/cli.py`
  - Explicit `--use-llm` path now uses compact writer payload mode.
  - Incomplete stderr adds safe scalar root-cause hint and max output chars.
- Tests updated:
  - `tests/fund/test_chapter_writer.py`
  - `tests/services/test_llm_provider.py`
  - `tests/services/test_chapter_orchestrator.py`
  - `tests/config/test_llm_config.py`
  - `tests/ui/test_cli.py`
- README updates:
  - `fund_agent/config/README.md`
  - `fund_agent/fund/README.md`
  - `tests/README.md`

## Diagnostic Schema Notes

- Writer prompt-cost schema: `chapter_prompt_cost_diagnostic_payload.v1`.
- Runtime diagnostic payload remains `chapter_runtime_diagnostic_payload.v1` with additive fields:
  - `timeout_seconds`
  - `timeout_max_attempts`
  - `timeout_backoff_seconds`
  - `timeout_budget_kind`
  - `repair_timeout_fallback_used`
  - `timeout_root_cause_hint`
  - allowlisted `prompt_cost_diagnostic`

## Safety Confirmation

- No full prompt, draft markdown, provider request JSON, provider response JSON, raw audit response, API key or Authorization header is serialized in diagnostics.
- Prompt-cost rows contain ids, enum/status fields and char counts only; fact values and anchor notes are not serialized into diagnostics.
- Compact prompt payload explicitly tells the LLM not to cite, restate or infer omitted raw detail.
- Compact mode preserves available fact identity/status/missing semantics and anchor source metadata.
- No deterministic fallback was added.
- No Host/Agent/dayu code was introduced.
- No golden, fixtures, extraction score, quality gate, final judgment, promotion state, PR state, push, merge or release changes were made.

## Validation

Targeted tests:

```bash
uv run pytest tests/fund/test_chapter_writer.py tests/services/test_llm_provider.py tests/services/test_chapter_orchestrator.py tests/config/test_llm_config.py tests/ui/test_cli.py -q
```

Result: PASS, `225 passed in 1.28s`.

Ruff for touched Python files:

```bash
uv run ruff check fund_agent/fund/chapter_writer.py fund_agent/services/llm_provider.py fund_agent/services/chapter_orchestrator.py fund_agent/config/llm.py fund_agent/ui/cli.py tests/fund/test_chapter_writer.py tests/services/test_llm_provider.py tests/services/test_chapter_orchestrator.py tests/config/test_llm_config.py tests/ui/test_cli.py
```

Result: PASS, `All checks passed!`.

## Not Run

- Full `uv run ruff check .`: not run by this implementation worker; controller can run full repo validation.
- Full `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q`: not run by this implementation worker; controller can run full coverage gate.
- Real provider smoke: not run by this implementation worker because provider secrets and live endpoint disposition belong to controller evidence.

## Residual Risks

- Real chapter 2/6 prompt sizes after compact mode need same-source service diagnostic from a live provider smoke to confirm whether they fall below `large_writer_prompt_cost`.
- If small-prompt rows still time out under bounded operation-specific timeouts, the blocker should be classified as provider/runtime endpoint reliability rather than prompt cost.
- Compact summaries are intentionally conservative; if a required large fact still cannot be represented safely enough for writing, the next controller decision should stop for semantic compaction or tool-based fact lookup rather than relaxing evidence rules.
