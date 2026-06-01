# MVP Incomplete LLM Run Artifact Retention Slice 1 — Code Review

## Gate / Slice / Role

- **Gate**: MVP incomplete LLM run artifact retention gate
- **Slice**: Slice 1 — incomplete `analyze --use-llm` run artifact retention only
- **Role**: code review agent
- **Accepted plan checkpoint**: `5f18715`

## Reviewed Targets

- `fund_agent/services/llm_run_artifacts.py` (new, 1078 lines)
- `fund_agent/ui/cli.py` (modified: `_write_incomplete_llm_artifacts_for_cli`, `analyze` command trigger logic)
- `tests/services/test_llm_run_artifacts.py` (new, 667 lines)
- `tests/ui/test_cli.py` (modified: artifact-related tests)
- `.gitignore` (added `reports/llm-runs/`)
- Implementation evidence: `docs/reviews/mvp-incomplete-llm-run-artifact-retention-slice1-implementation-evidence-20260602.md`

## Verdict: PASS

No blocking findings. The implementation correctly satisfies all Slice 1 scope requirements with proper trigger boundary enforcement, fail-closed semantics, allowlist-first serialization, and adequate test coverage.

## Findings

### 1. [NON-BLOCKING] Redaction keyword set includes non-secret field names that cause collateral text damage

**File**: `fund_agent/services/llm_run_artifacts.py:55-58`

```python
re.compile(r"\bdraft_markdown\b", re.IGNORECASE),
re.compile(r"\braw_response\b", re.IGNORECASE),
re.compile(r"\bprovider_response\b", re.IGNORECASE),
```

These patterns redact the *words* `draft_markdown`, `raw_response`, and `provider_response` wherever they appear in artifact text. Since allowlist serialization already prevents those fields from being written, redacting their *names* provides no additional safety. However, it can damage readability of diagnostic messages that happen to mention these terms (e.g., an auditor message saying "raw_response was empty" would become "[REDACTED] was empty").

**Severity**: Low. Defense-in-depth at the cost of minor readability loss in local diagnostic artifacts. Does not affect runtime behavior.

**Recommendation**: Consider removing field-name-only patterns and keeping only the content-bearing patterns (`Bearer`, `sk-`, `api_key`). Not blocking for Slice 1.

### 2. [NON-BLOCKING] `_safe_text` applies `str()` to all values before redaction

**File**: `fund_agent/services/llm_run_artifacts.py:899-900`

```python
def _safe_text(value: object, *, stats: _RedactionStats) -> str:
    return _redact_text(str(value), stats)
```

If a non-string object with an unexpected `__str__` representation were passed to `_safe_text`, the resulting string could theoretically contain information not captured by the allowlist. In practice, all current call sites pass either `str`, `int`, or dataclass fields with well-defined `__str__`, so the risk is negligible.

**Severity**: Low. Mitigated by allowlist-first architecture; only explicitly selected fields enter `_safe_text`.

### 3. [NON-BLOCKING] Accepted draft identification by markdown content comparison

**File**: `fund_agent/services/llm_run_artifacts.py:346-353`

```python
if (
    accepted_draft_file is None
    and writer_draft_file is not None
    and chapter_result.accepted_draft is not None
    and draft is not None
    and draft.markdown == chapter_result.accepted_draft.markdown
):
    accepted_draft_file = writer_draft_file
```

The accepted draft is identified by full markdown content equality with the writer/repair draft. This is correct for Slice 1 but is string-comparison-based and could theoretically miss the match if the draft stored in `chapter_result.accepted_draft` undergoes any whitespace or encoding transformation between its original writing and its storage as the accepted reference. In current code paths this does not occur.

**Severity**: Low. The fallback at line 355 handles the miss case by writing a separate `accepted-draft.md`.

### 4. [OBSERVATION] Host run ID truncated to 24 characters in directory name

**File**: `fund_agent/services/llm_run_artifacts.py:984`

```python
run_id_suffix = _safe_path_component(host_run_id or "no-host-run")[:_RUN_ID_MAX_CHARS]
```

`_RUN_ID_MAX_CHARS = 24`. Current `host_run_id` format is `host_run_YYYYMMDDTHHMMSSZ` (25 characters), so the last character is consistently truncated. This is cosmetic — directory uniqueness is also provided by the timestamp prefix.

### 5. [OBSERVATION] Artifact write failure silently swallows all exception types

**File**: `fund_agent/ui/cli.py:928-933`

```python
except Exception as exc:  # noqa: BLE001
    typer.echo(
        f"LLM incomplete diagnostic artifact warning: write_failed type={type(exc).__name__}",
        err=True,
    )
    return None
```

This is intentional fail-closed behavior (per the `BLE001` justification comment), but it means programming errors in `write_llm_incomplete_run_artifacts` (e.g., `TypeError` from a refactoring mistake) would be silently swallowed. The warning message includes only the exception type name, not the message, which is correct for secret safety but limits debuggability.

**Recommendation**: Consider logging the full exception traceback to a local file in a future slice, outside the stderr surface. Not blocking.

## Scope Compliance Verification

| Requirement | Status | Evidence |
|---|---|---|
| Trigger: typed `FundLLMAnalysisResult` only | PASS | `isinstance` guard in `_write_incomplete_llm_artifacts_for_cli` (cli.py:919) and `write_llm_incomplete_run_artifacts` (llm_run_artifacts.py:119) |
| Trigger: incomplete only (no accepted final report) | PASS | `report_markdown is not None` guard (cli.py:921, llm_run_artifacts.py:123) |
| No deterministic/checklist artifact writing | PASS | `_forbid_llm_artifact_writer` sentinel used in `test_analyze_cli_default_product_request` (test_cli.py:2350-2353) and `test_checklist_cli_calls_service_and_prints_summary` (test_cli.py:2689-2692) |
| No config/construction failure artifact writing | PASS | Exceptions caught before artifact code paths (cli.py:268-273) |
| No quality gate block artifact writing | PASS | Quality gate exceptions re-raised before artifact paths (cli.py:274-279, cli.py:877-878) |
| No Host failure without typed result artifact writing | PASS | `operation_result is not None` guard (cli.py:253) |
| Fail-closed: stdout empty, exit code 1 | PASS | Verified in 6+ test functions |
| Fail-closed: artifact write failure doesn't mask incomplete | PASS | `test_analyze_cli_incomplete_artifact_write_failure_preserves_fail_closed` (test_cli.py:1898) |
| Allowlist serialization (no `asdict()`/`__dict__`) | PASS | Every payload builder selects fields explicitly |
| No prompt/raw provider payload leakage | PASS | `test_artifact_schema_does_not_serialize_prompts_or_raw_provider_payloads` (test_llm_run_artifacts.py:159) |
| No API key/secret leakage | PASS | `test_artifact_redacts_secret_canaries` (test_llm_run_artifacts.py:124) |
| Artifact schema: manifest/summary/chapters/drafts/feedback | PASS | All present and validated in tests |
| `.gitignore` covers `reports/llm-runs/` | PASS | `.gitignore:28` |
| No chapter acceptance calibration | PASS | No code touches acceptance thresholds |
| No progress UX changes | PASS | No UI changes outside artifact stderr line |
| No provider timeout budget changes | PASS | No timeout-related code in new files |
| No score-loop entry | PASS | No scoring code in new files |
| No external dayu dependency | PASS | No `dayu` imports anywhere |

## Test Coverage Assessment

**Positive paths covered**:
- Typed incomplete result writes manifest, summary, and chapter artifacts (`test_write_llm_incomplete_run_artifacts_writes_manifest_summary_and_chapters`)
- Writer drafts, repair drafts, and auditor feedback are preserved (`test_artifact_includes_writer_repair_and_auditor_feedback`)
- Redaction of secret canaries with counter tracking (`test_artifact_redacts_secret_canaries`)
- Prompt and raw provider payload exclusion (`test_artifact_schema_does_not_serialize_prompts_or_raw_provider_payloads`)
- Accepted final report rejection (`test_artifact_writer_rejects_accepted_final_report_by_default`)
- `.gitignore` rule verification (`test_gitignore_ignores_llm_run_artifacts`)
- CLI artifact path printing while fail-closed (`test_analyze_cli_use_llm_typed_incomplete_writes_artifact_path`)
- CLI artifact write failure preserves fail-closed (`test_analyze_cli_incomplete_artifact_write_failure_preserves_fail_closed`)
- Stderr safety (no secret leakage in error messages) (`test_analyze_cli_use_llm_incomplete_prints_safe_all_chapter_matrix`, `test_analyze_cli_use_llm_timeout_fail_closed_without_fallback`)

**Negative boundary coverage**:
- Deterministic analyze path does not trigger artifact writer (sentinel guard in `test_analyze_cli_default_product_request`)
- Checklist path does not trigger artifact writer (sentinel guard in `test_checklist_cli_calls_service_and_prints_summary`)
- Config error path does not trigger artifact writer (sentinel guard in `test_analyze_cli_use_llm_missing_config_fails_before_service`)
- Quality gate block paths verified without artifact writing (`test_analyze_cli_use_llm_structured_quality_gate_block`, `test_analyze_cli_use_llm_structured_quality_gate_not_run_block`)
- Host terminal failure without typed result (`test_analyze_cli_use_llm_host_terminal_failure_does_not_fake_success`)

**Adequate**: Yes. All trigger boundary conditions are covered, both positive and negative. Failure-path coverage includes artifact write failure, Host failure, timeout, and quality gate interruption.

## Residual Risks

1. **Local artifact lifecycle**: No automated cleanup. `retention_policy=manual_local_cleanup` is recorded in manifest. Deferred to future observability gate.
2. **Real provider smoke**: Artifact behavior under real LLM provider nondeterminism has not been exercised. All tests use fixtures. Deferred to future smoke rerun gate.
3. **Redaction pattern completeness**: Regex-based redaction is defense-in-depth; primary protection is allowlist serialization. Edge cases in regex patterns (e.g., multi-line Bearer tokens with unusual whitespace) are acceptable risk given the allowlist guard.

## Explicit Statement

**No blocking findings exist.** All Slice 1 scope requirements are satisfied. The implementation is correct, safe, and adequately tested. The three non-blocking observations noted above do not prevent this slice from passing review.
