# MVP typed diagnostic serialization repair implementation evidence

## Scope

- Role: AgentCodex implementation specialist, not controller.
- Gate: `MVP typed diagnostic serialization repair implementation gate`.
- Classification: heavy.
- Source of truth: accepted diagnostic evidence reconciliation design/plan and controller judgment.
- Live provider: not run.
- Staging/commit/push: not performed.

## Changed Files

- `fund_agent/services/chapter_orchestrator.py`
- `fund_agent/services/llm_run_artifacts.py`
- `fund_agent/config/paths.py`
- `fund_agent/config/README.md`
- `tests/services/test_chapter_orchestrator.py`
- `tests/services/test_llm_run_artifacts.py`

`tests/README.md` was not changed because no test convention changed.

## Implementation Summary

- Fixed terminal exception diagnostic retention so provider exceptions are kept at chapter level when they cannot be safely attached to an existing attempt. This repairs the likely lineage bug where a prior audit diagnostic could shadow the terminal exception diagnostic.
- Added safe scalar terminal consistency fields:
  - `diagnostic_consistency_status`
  - `terminal_runtime_diagnostic_present`
  - `terminal_stop_reason`
  - `terminal_failure_category`
  - `terminal_runtime_operation`
  - `terminal_repair_attempt_index`
  - `terminal_issue_class`
- Updated first-failed runtime summary selection to prefer terminal-matching runtime diagnostics. For `stop_reason=llm_timeout`, representative diagnostics require `provider_runtime_category=timeout` or `timeout_budget_kind`.
- If a terminal runtime stop has no matching runtime diagnostic, serializer now reports `missing_terminal_runtime_diagnostic` and does not invent timeout scalar fields.
- Kept prompt-contract diagnostics separate from provider runtime diagnostics. `audit_rule_too_strict`, L1, and `unknown_anchor` rows are not reclassified as runtime timeout.
- Added chapter-level and retained artifact `attempts[]` terminal lineage fields. Existing attempts are not fabricated for terminal exceptions that occur before an attempt record exists; in that case chapter-level lineage is authoritative and attempt-level rows explicitly report missing terminal runtime diagnostic.
- Scoped `status_code` output to standard HTTP integer range `100..599`; non-standard values serialize as `null`. `request_id` remains an opaque allowlisted scalar and is not used for attribution.
- Moved the LLM incomplete run artifact default root into `fund_agent/config/paths.py` as `DEFAULT_LLM_RUN_ARTIFACT_ROOT` and kept `fund_agent/services/llm_run_artifacts.py` exporting the same public alias value.
- Updated `fund_agent/config/README.md` because the config package README explicitly describes `paths.py` default path ownership.

## Test Coverage Added

- Terminal timeout after a prior audit row is represented by the matching terminal runtime diagnostic in first-failed summary.
- Writer repair timeout without a new attempt record retains the terminal row at chapter level.
- `llm_timeout` without matching timeout runtime row reports `missing_terminal_runtime_diagnostic` and leaves timeout scalars empty.
- Retained artifact writer persists terminal lineage at chapter level and attempts level.
- Artifact status code safety: non-standard status code is dropped, standard `504` is retained.
- Existing prompt-cost handling is unchanged: `llm_run_artifacts` does not serialize `prompt_cost_diagnostic`; `chapter_orchestrator` keeps its existing safe prompt-cost allowlist.

## Validation

| Command | Result |
|---|---|
| `python -m py_compile fund_agent/services/chapter_orchestrator.py fund_agent/services/llm_run_artifacts.py` | passed |
| `uv run pytest tests/config/test_paths.py::test_no_independent_repository_path_defaults_outside_config_paths -q` | passed: 1 passed |
| `uv run pytest tests/services/test_chapter_orchestrator.py tests/services/test_llm_run_artifacts.py` | passed: 82 passed |
| `uv run pytest tests/ui/test_cli.py -k "llm and diagnostic"` | no tests selected: 72 deselected, pytest exit 5 |
| `uv run pytest tests/ui/test_cli.py --collect-only -q` | passed: 72 tests collected; confirmed no current test name matches `llm and diagnostic` |
| `uv run pytest tests/ui/test_cli.py -k "llm and incomplete"` | passed: 4 passed, 68 deselected |
| `uv run pytest tests/ui/test_cli.py -k "llm and timeout"` | passed: 3 passed, 69 deselected |
| `uv run ruff check fund_agent/config/paths.py fund_agent/services/chapter_orchestrator.py fund_agent/services/llm_run_artifacts.py tests/services/test_chapter_orchestrator.py tests/services/test_llm_run_artifacts.py` | passed |
| `uv run pytest` | passed: 1292 passed |
| `git diff --check` | passed |

## Secret Safety

- No live provider was called.
- No prompt body, draft body, raw provider response, raw audit response, API key, Authorization header, Bearer token, cookie, password, provider base URL, model value, full report body, raw PDF text, or raw parsed annual-report text is stored by the new fields.
- New terminal lineage fields are scalar allowlisted values only.
- `terminal_issue_class` uses exception class names or safe issue prefixes only; it does not serialize issue messages.
- `status_code` is retained only for standard HTTP integer codes.
- `request_id` remains opaque and removable if a future provider format is found to embed account, model, region, or endpoint information.

## Residual Notes

- CLI source was not modified because it was not in the allowed file list. The requested exact CLI command selected no tests under the current test names; related incomplete/timeout CLI stderr regressions were run and passed.
- Attempt-level lineage is exposed for existing attempts. When terminal runtime failure occurs before a new attempt record exists, the implementation does not fabricate an attempt; chapter-level and summary lineage carry the terminal diagnostic, while attempt rows show missing terminal runtime diagnostic.
- No full-pytest residual remains after moving the LLM run artifact root into the config path truth module.
