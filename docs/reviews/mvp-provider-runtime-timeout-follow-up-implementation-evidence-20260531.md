# MVP provider runtime timeout follow-up implementation evidence

日期：2026-05-31

角色：Gateflow implementation worker，不是 controller。

Source of truth：

- `docs/reviews/mvp-provider-runtime-timeout-follow-up-plan-20260531.md`
- `docs/reviews/mvp-provider-runtime-timeout-follow-up-plan-review-mimo-20260531.md`
- `docs/reviews/mvp-provider-runtime-timeout-follow-up-plan-review-glm-20260531.md`
- `docs/reviews/mvp-provider-runtime-timeout-follow-up-plan-rereview-mimo-20260531.md`
- `docs/reviews/mvp-provider-runtime-timeout-follow-up-plan-rereview-glm-20260531.md`

## Scope

Allowed files touched in this implementation pass:

- `fund_agent/services/chapter_orchestrator.py`
- `fund_agent/services/llm_provider.py`
- `fund_agent/ui/cli.py`
- `tests/services/test_llm_provider.py`
- `tests/services/test_chapter_orchestrator.py`
- `tests/ui/test_cli.py`
- `docs/reviews/mvp-provider-runtime-timeout-follow-up-implementation-evidence-20260531.md`

Not touched:

- golden / fixtures / score / quality gate / final judgment
- Host / Agent / dayu
- provider config/auth
- PR / push / merge / release state

No real provider command was run.

## Implementation Summary

Service:

- Added `serialize_chapter_runtime_diagnostics(orchestration_result)` in `fund_agent/services/chapter_orchestrator.py`.
- Extended `ChapterLLMRuntimeDiagnostic` with optional runtime-cost scalar fields:
  - `system_prompt_chars`
  - `user_prompt_chars`
  - `approx_prompt_tokens`
  - `allowed_fact_count`
  - `allowed_anchor_count`
  - `max_output_chars`
- The serializer emits only allowlisted scalar fields:
  - schema/version and orchestration identity
  - first failed chapter status/category/subcategory
  - runtime operation, repair attempt, observed/max provider attempts, provider runtime categories, runtime-cost scalar fields
  - per chapter runtime matrix with operation, repair attempt, provider attempt index/max, runtime category, chapter failure category, elapsed_ms, status_code, request_id, finish_reason, response_chars, error_type and runtime-cost scalar fields
- It collects diagnostics from both `ChapterRunResult.runtime_diagnostics` and `ChapterAttemptRecord.runtime_diagnostics`.
- It intentionally omits `model_name` and generic `message`.

Provider:

- Added provider-bound prompt/runtime cost scalar diagnostics in `fund_agent/services/llm_provider.py`.
- Writer diagnostics use:
  - `len(request.system_prompt)`
  - `len(request.user_prompt)`
  - `ceil((system + user) / 4)` as approximate prompt tokens
  - `allowed_fact_count=None`
  - `allowed_anchor_count=len(request.required_anchor_ids)`
  - `max_output_chars=request.max_output_chars`
- Auditor diagnostics compute `user_prompt_chars` from the actual provider-bound `_audit_user_prompt(request)` text, including draft/context, without storing that text.
- These scalars do not change provider payload shape, retry policy, audit pass/fail semantics or deterministic output.

CLI:

- Extended first failed incomplete summary with:
  - `first_failed_runtime_operation`
  - `first_failed_provider_attempts`
  - `first_failed_provider_runtime_category`
  - `first_failed_elapsed_ms_max`
  - `first_failed_prompt_chars`
  - `first_failed_approx_prompt_tokens`
- Missing diagnostics degrade to `unknown` fields and `0/unknown` attempts.
- The CLI does not print runtime diagnostic `message`.

Tests:

- Added provider tests for writer/auditor timeout diagnostics carrying prompt/runtime cost scalar fields.
- Added Service serializer coverage for provider timeout diagnostics with canary `message` values containing writer/auditor/programmatic/raw audit/prompt/draft/body/key/header markers.
- Added Service coverage proving attempt-level diagnostics are included.
- Added CLI timeout stderr coverage for operation, attempt budget, runtime category, max elapsed_ms, prompt chars, approximate prompt tokens and negative leak assertions.

## Safe Diagnostic Capture Snippet

Controller can use this shape in a later validation gate after producing an `orchestration_result`.

```python
import json
from pathlib import Path

from fund_agent.services.chapter_orchestrator import (
    serialize_chapter_runtime_diagnostics,
)

payload = serialize_chapter_runtime_diagnostics(orchestration_result)
out_dir = Path("reports/mvp-local-acceptance/20260531-provider-runtime-timeout-follow-up")
out_dir.mkdir(parents=True, exist_ok=True)
(out_dir / "service-runtime-diagnostics.json").write_text(
    json.dumps(payload, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
```

The snippet writes only serializer output and does not print env values, base URL, model, prompts, drafts or raw provider/audit responses.

## Validation

Passed:

```bash
uv run ruff check fund_agent/services/llm_provider.py fund_agent/services/chapter_orchestrator.py fund_agent/ui/cli.py tests/services/test_llm_provider.py tests/services/test_chapter_orchestrator.py tests/ui/test_cli.py
```

Result: `All checks passed!`

Passed:

```bash
uv run pytest tests/services/test_llm_provider.py tests/services/test_chapter_orchestrator.py tests/ui/test_cli.py -q
```

Result: `143 passed in 1.08s`

Provider runtime targeted tests were run because this supplement modified provider diagnostics. Config tests were not run because this pass did not modify config bounds/defaults.

Real provider smoke was not run, per implementation-worker handoff constraint.

## Documentation Decision

README files were not updated in this pass because the user explicitly constrained allowed implementation files to the Service/CLI/test files plus this evidence artifact. The user-visible change is a fail-closed `--use-llm` incomplete diagnostic stderr expansion; controller can decide whether to open a separate documentation synchronization gate if needed.

## Residuals For Controller

- Controller still needs to run any real-provider current/bounded smoke required by the accepted plan.
- Controller should decide whether README/test README synchronization is required outside this worker's allowed file boundary.
