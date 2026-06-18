# MVP Real LLM Incomplete-Run Artifact Retention And Chapter Acceptance Calibration Plan

## Gate Context

- Work unit: MVP real LLM incomplete-run artifact retention and chapter acceptance calibration gate.
- Current gate: plan gate only.
- Current role: planning specialist, not controller.
- Branch observed: `feat/mvp-llm-incomplete-run-artifacts`.
- Workspace note: existing untracked files are present under `docs/reviews/`, `docs/`, `reports/manual-llm-smoke/`, and `reviews/`; this plan only assigns future implementation work and does not claim ownership of those unrelated files.
- Plan artifact path: `docs/reviews/mvp-real-llm-incomplete-run-artifact-retention-and-chapter-acceptance-calibration-plan-20260602.md`.

## 1. Goal, Motivation, And Direct Evidence

Goal: make real `--use-llm` incomplete runs debuggable without weakening fail-closed behavior, then use the retained evidence to calibrate chapter acceptance for real provider runs.

Motivation: the current CLI protects users by leaving stdout empty and returning non-zero on incomplete LLM runs, but it only emits a compact stderr summary. That summary is insufficient to diagnose why real chapters 2/3/6 failed because the draft text, repair draft, and auditor feedback are not retained anywhere.

Direct evidence supplied by controller:

- Evidence directory: `reports/manual-llm-smoke/006597-2024/`.
- `stderr.txt` records an incomplete real LLM run.
- `stdout.md` is empty.
- `exitcode=1`.
- `run_id=host_run_23a293cccbe14579`.
- `orchestration_status=partial`.
- `final_assembly_status=incomplete`.
- `first_failed_chapter_id=2`.
- `first_failed_category=prompt_contract`.
- `first_failed_subcategory=l1_numerical_closure`.
- `chapter_matrix=1 accepted; 2 failed; 3 failed; 4 accepted; 5 accepted; 6 failed`.

Success signal:

- Slice 1: an incomplete `--use-llm` run still exits fail-closed with empty stdout, but writes local ignored diagnostics under `reports/llm-runs/<fund_code>-<report_year>-<timestamp>/`.
- Deferred follow-up: the retained artifacts from Slice 1 support a later evidence-based calibration gate for chapters 2/3/6, with chapter 2 `prompt_contract/l1_numerical_closure` analyzed first, and no audit rule relaxation or deterministic fallback.

## 1A. Controller Decision Input / Work-Unit Shape Decision

This section treats the user-provided phase proposal as planning input only. It does not start `$phaseflow`, `/phaseflow`, `$gateflow`, or implementation.

Phase proposal supplied by user:

- Phase name: MVP real LLM observability and chapter acceptance phase.
- Design truth: `docs/design.md`.
- Control truth: `docs/implementation-control.md`.
- Phase goal: make real LLM failures auditable, reproducible, and iteratable before improving chapter accepted rate.
- Suggested gates:
  1. MVP incomplete LLM run artifact retention gate.
  2. MVP LLM run progress and timeout UX gate.
  3. MVP real LLM chapter acceptance calibration gate.
  4. MVP provider runtime budget calibration gate.
  5. MVP chapter generation score-loop entry gate.

Decision recommendation for controller: upgrade the broader work to a phase named `MVP real LLM observability and chapter acceptance phase`, and narrow the current accepted gate to `MVP incomplete LLM run artifact retention gate`.

Rationale from first principles:

- The direct root cause problem is observability: current real LLM failures are fail-closed but not inspectable enough. Without retained per-chapter evidence, calibration work risks guessing from indirect stderr summaries.
- Artifact retention is a prerequisite for chapter acceptance calibration, progress UX, provider runtime budget calibration, and score-loop entry. It has a clean contract: write local ignored diagnostic artifacts while preserving fail-closed stdout/exit behavior.
- Calibration changes can touch writer guidance, repair guidance, diagnostics, or bug fixes; progress UX can touch Host/CLI lifecycle and timeout presentation; provider runtime budget calibration can touch runtime policy; score-loop entry can introduce new scoring contracts. Combining these in one gate increases review scope and creates pressure to smuggle unrelated behavior into the artifact-retention implementation.
- The proposed phase provides clearer sequencing: first make failures auditable, then use the audit trail to decide whether prompt/guidance, UX, provider budgets, or score loops are the next best intervention.

Single-gate alternative:

- Keeping the original work unit as one gate (`MVP real LLM incomplete-run artifact retention and chapter acceptance calibration gate`) is only acceptable if controller explicitly decides the implementation will include exactly two sequential slices:
  - Slice 1 artifact retention.
  - Slice 2 chapter acceptance calibration based only on Slice 1 artifacts.
- Under that alternative, boundaries remain clear only if Slice 2 is prohibited from progress UX, provider runtime budget calibration, score-loop entry, repair budget increases, audit relaxation, deterministic fallback, and partial stdout.
- Risk remains higher than the phase option because Slice 2 root cause is not knowable before Slice 1 artifacts exist. The plan would need a hard stop after Slice 1 if artifacts indicate progress/timeout/runtime budget/score-loop work is the actual next step.

Recommended current gate shape:

- Accepted plan name: `MVP incomplete LLM run artifact retention gate`.
- Current gate implementation scope: only Slice 1 artifact retention.
- Current gate completion signal:
  - incomplete `analyze --use-llm` still exits `1`;
  - stdout stays empty;
  - incomplete stderr summary remains safe;
  - local ignored artifacts are written under `reports/llm-runs/`;
  - per-chapter writer draft, repair draft, normalized auditor feedback, status, chapter matrix, and first failed diagnostic are retained with redaction;
  - deterministic `analyze` and `checklist` are unchanged.
- Current gate stop point: after Slice 1 implementation/review/accepted checkpoint and a real smoke rerun that produces either accepted output or local artifacts. Do not implement calibration in this gate unless controller rejects the phase upgrade and explicitly accepts the single-gate alternative.

Deferred-with-owner work if controller accepts the phase upgrade:

- Deferred to phase gate 2, owner controller + future planning worker: MVP LLM run progress and timeout UX. This includes progress display, timeout UX, elapsed phase reporting, and any Host/CLI lifecycle presentation changes.
- Deferred to phase gate 3, owner controller + future planning/implementation workers: MVP real LLM chapter acceptance calibration. This includes chapter 2/3/6 root-cause analysis and prompt/repair/diagnostic/code-bug fixes based on Slice 1 artifacts.
- Deferred to phase gate 4, owner controller + future planning/implementation workers: MVP provider runtime budget calibration. This includes timeout/runtime budget policy changes and provider budget evidence.
- Deferred to phase gate 5, owner controller + future planning/implementation workers: MVP chapter generation score-loop entry. This includes any `chapter_generation_score` contract, scoring storage, and score-loop workflow.
- Deferred to phaseflow controller, owner controller: update `docs/implementation-control.md` and, if needed, `docs/design.md` with the phase shape before later phase gates start.

Explicit anti-smuggling rule for the current gate:

- Do not implement progress UX.
- Do not implement provider runtime budget calibration.
- Do not implement `chapter_generation_score` or score-loop entry.
- Do not implement chapter acceptance calibration unless controller explicitly keeps the original single-gate shape after plan review.
- Do not change deterministic `analyze` or `checklist`.
- Do not allow incomplete LLM to fall back to deterministic output.
- Do not change quality gate semantics.
- Do not raise repair budget as a default solution.
- Do not introduce `dayu-agent`, `dayu.host`, or `dayu.engine` as production runtime dependencies.
- Preserve plan/review before implementation/review/accepted checkpoint for every gate.

## 2. Current Code Facts

These are current implementation facts, not planned future behavior.

CLI facts from `fund_agent/ui/cli.py`:

- `analyze` has a `--use-llm` boolean option.
- `--use-llm` first calls `_build_llm_execution_request_or_fail(request)`, then `_run_llm_analysis_in_host(execution_request)`.
- `_run_llm_analysis_in_host()` creates `FundAnalysisService()`, runs `service.analyze_with_llm_execution(...)` inside `HostRuntimeRunner().run_sync(...)`, and stores `incomplete_result` when `result.final_assembly_result.report_markdown is None`.
- When incomplete, `_run_llm_analysis_in_host()` records Host safe diagnostics with `final_assembly_status` and `error_type=_LLMIncompleteHostRunError`, raises `_LLMIncompleteHostRunError` inside Host, then replaces `host_result.operation_result` with the typed incomplete result before returning.
- CLI emits `_hosted_llm_incomplete_message(...)` when Host status is not succeeded but `operation_result` exists.
- CLI exits `1` for incomplete LLM results and does not print half-finished markdown to stdout.
- `_llm_incomplete_message()` includes `orchestration_status`, `final_assembly_status`, final assembly issue reasons, first failed chapter summary, and chapter matrix.
- Existing stderr summaries intentionally avoid prompt, draft, raw response, `Authorization`, `Bearer`, `sk-`, `api_key`, headers, and provider body text.

Service/orchestrator facts from `fund_agent/services/chapter_orchestrator.py`:

- `ChapterAttemptRecord` currently retains `writer_result`, optional `audit_result`, optional `repair_decision`, and runtime diagnostics for each attempt.
- `ChapterRunResult` retains `chapter_id`, `title`, `status`, `stop_reason`, optional `accepted_draft`, optional `accepted_conclusion`, all attempts, issues, failure category/subcategory, prompt-contract diagnostics, and runtime diagnostics.
- `ChapterOrchestrationResult` retains overall `status`, `fund_code`, `report_year`, projection, chapter results, accepted conclusions, blocked reasons, generated chapter IDs, and skipped chapter IDs.
- `_run_single_chapter()` appends an attempt for every writer/auditor cycle. Repair is represented by the next attempt's `writer_result`; there is no separate persisted "repair draft" field beyond the attempt index and writer result.
- Current safe serializers exist:
  - `serialize_chapter_prompt_contract_diagnostics()` outputs only status/category/count/scalar diagnostics.
  - `serialize_chapter_runtime_diagnostics()` outputs only allowlisted runtime scalar diagnostics.
- Current serializers explicitly do not output prompt, draft, provider response, raw audit response, API keys, or headers.

Writer facts from `fund_agent/fund/chapter_writer.py`:

- `ChapterWriteResult` contains `status`, `stop_reason`, `prompt`, optional `draft`, `issues`, `response_chars`, `finish_reason`, and `max_output_chars`.
- `ChapterDraft` contains `chapter_id`, `title`, `markdown`, `used_fact_ids`, `used_anchor_ids`, `declared_missing_reasons`, `deleted_item_rule_ids`, `model_name`, and `finish_reason`.
- Writer blocked results can include issues and scalar response metadata, but no draft.
- Writer prompts contain `system_prompt` and `user_prompt`; these must not be saved in Slice 1 artifacts.

Auditor facts from `fund_agent/fund/chapter_auditor.py`:

- `ChapterAuditResult` contains `programmatic`, `llm`, `accepted`, and aggregate `repair_hint`.
- `ChapterAuditIssue` contains `issue_id`, `layer`, `rule_code`, `severity`, `message`, `location`, related ids, and `repair_hint`.
- `ChapterLLMAuditResult` contains `status`, `issues`, optional `raw_response`, `model_name`, and `finish_reason`.
- Programmatic audit checks include numerical closure (`L1`) and returns patch/regenerate/needs_more_facts style repair hints through issues and aggregate result.

Final assembly facts from `fund_agent/services/final_chapter_assembler.py`:

- `FinalChapterAssemblyResult.report_markdown` is `None` unless final assembly status is accepted or `allow_incomplete_debug_markdown` is enabled.
- Default flow should not enable incomplete debug markdown for CLI output.

Test facts:

- `tests/ui/test_cli.py` already verifies incomplete `--use-llm` exits `1`, stdout is empty, no deterministic fallback occurs, Host failed summary is present, first failed summary and chapter matrix are present, and sensitive strings are absent from stderr.
- `tests/services/test_chapter_orchestrator.py` already verifies sanitized prompt-contract/runtime serializers exclude raw payloads and expose only safe scalars.
- `tests/services/test_fund_analysis_service_llm.py` already verifies missing writer/auditor returns typed blocked/incomplete and does not fall back deterministic.

Ignore facts:

- `.gitignore` currently ignores several `reports/...` generated output directories, but does not ignore `reports/llm-runs/`.
- `reports/manual-llm-smoke/` is currently untracked in the working tree and should remain local input evidence unless controller explicitly decides otherwise.

## 3. Non-Goals And Scope Boundaries

Non-goals for the recommended current gate:

- Do not change provider configuration strategy.
- Do not change Host fail-closed semantics.
- Do not change quality gate semantics.
- Do not increase repair budget.
- Do not relax auditor or programmatic audit.
- Do not introduce external `dayu` production runtime dependencies.
- Do not disguise failed chapters as accepted.
- Do not let incomplete LLM results fall back to deterministic renderer.
- Do not output partial reports to stdout.
- Do not process unrelated historical residuals.
- Do not implement chapter acceptance calibration unless controller explicitly rejects the phase upgrade and keeps the original single-gate shape.
- Do not implement progress UX, provider runtime budget calibration, or chapter generation score-loop entry.

Boundary mapping:

- CLI owns command options, stderr/stdout behavior, and the point at which incomplete run artifacts are requested after Service execution.
- Service owns LLM analysis use case result structures and chapter orchestration result traversal.
- Agent/Fund owns writer/auditor data structures and audit rule semantics. Slice 1 may read those typed results for diagnostics, but must not move prompt rendering, audit logic, or fund rules into CLI.
- Host owns run lifecycle and failed terminal state. Slice 1 must not reinterpret Host failure as success.

## 4. Artifact Schema

Add a small Service-owned artifact serialization module or functions. Recommended file: `fund_agent/services/llm_run_artifacts.py`. Rationale: artifact schema traverses Service result types (`FundLLMAnalysisResult`, `ChapterOrchestrationResult`, `FinalChapterAssemblyResult`) and should not live in UI. CLI may call the Service helper after an incomplete `--use-llm` result is available.

Directory layout:

```text
reports/llm-runs/<fund_code>-<report_year>-<timestamp>/
  manifest.json
  summary.json
  chapters/
    chapter-01.json
    chapter-01-attempt-00-writer.md
    chapter-01-attempt-00-auditor-feedback.md
    chapter-02.json
    chapter-02-attempt-00-writer.md
    chapter-02-attempt-00-auditor-feedback.md
    chapter-02-attempt-01-repair.md
    chapter-02-attempt-01-auditor-feedback.md
```

Use zero-padded chapter and attempt numbers for stable sorting. If a writer result in attempt `0` is produced from the initial writer input, the text file suffix is `writer.md`. If `attempt_index > 0`, the text file suffix is `repair.md`; this is the repair draft generated by the writer on the repair attempt.

`manifest.json` fields:

- `schema_version`: `"llm_incomplete_run_artifact_manifest.v1"`.
- `created_at`: ISO-8601 local or UTC timestamp with timezone.
- `artifact_kind`: `"llm_incomplete_run_diagnostic"`.
- `fund_code`.
- `report_year`.
- `run_id`: Host run id when available, else `null`.
- `trigger`: `"use_llm_incomplete"` or `"explicit_diagnostic_flag"`.
- `cli_command`: sanitized command label only, for example `"analyze --use-llm"`; do not save argv values that may contain secrets.
- `orchestration_status`.
- `final_assembly_status`.
- `chapter_count`.
- `chapter_files`: list of relative paths.
- `summary_file`: `"summary.json"`.
- `redaction_policy`: object with policy id and forbidden categories.

`summary.json` fields:

- `schema_version`: `"llm_incomplete_run_summary.v1"`.
- `fund_code`.
- `report_year`.
- `run_id`.
- `orchestration_status`.
- `final_assembly_status`.
- `final_assembly_issues`: list of safe issue summaries: `reason`, `severity`, optional `chapter_id`/location if present; no report markdown.
- `first_failed`: `chapter_id`, `status`, `stop_reason`, `failure_category`, `failure_subcategory`.
- `chapter_matrix`: one row per chapter with `chapter_id`, `title`, `status`, `stop_reason`, `failure_category`, `failure_subcategory`, `attempt_count`, `accepted_draft_present`, `accepted_conclusion_present`.
- `prompt_contract_diagnostics`: value from `serialize_chapter_prompt_contract_diagnostics()`.
- `runtime_diagnostics`: value from `serialize_chapter_runtime_diagnostics()`.
- `artifact_files`: relative path list.

Per-chapter `chapter-XX.json` fields:

- `schema_version`: `"llm_incomplete_run_chapter_artifact.v1"`.
- `fund_code`, `report_year`, `chapter_id`, `title`.
- `status`, `stop_reason`, `failure_category`, `failure_subcategory`.
- `accepted`: boolean equal to `status == "accepted"`.
- `accepted_draft_file`: relative path when `accepted_draft` exists; otherwise `null`.
- `attempts`: list of attempt metadata:
  - `attempt_index`.
  - `writer_status`, `writer_stop_reason`, `writer_finish_reason`, `writer_response_chars`, `writer_max_output_chars`.
  - `writer_draft_file`: relative path when `writer_result.draft` exists; otherwise `null`.
  - `writer_used_fact_ids`, `writer_used_anchor_ids`, `writer_declared_missing_reasons`, `writer_deleted_item_rule_ids` when draft exists.
  - `writer_issues`: safe issue summaries with `issue_id`, `severity`, `reason`, `message`, `fact_ids`, `anchor_ids`, `item_rule_ids`.
  - `audit_status`, `audit_accepted`, `audit_repair_hint`, `audit_feedback_file`.
  - `programmatic_issues`: safe issue summaries with `issue_id`, `layer`, `rule_code`, `severity`, `message`, `location`, related ids, `repair_hint`.
  - `llm_issues`: same safe issue summary shape.
  - `llm_audit_raw_response_file`: relative path only if raw LLM auditor response is saved under the same redaction policy; recommended default is to save normalized auditor feedback from issues, not raw response.
  - `repair_decision`: `action`, `reason`, `stop_reason`, `source_repair_hint`, `issue_ids` when present.
  - `runtime_diagnostics`: allowlisted scalar payloads already used by runtime serializer.
- `chapter_prompt_contract_diagnostics`: prompt-contract diagnostic payloads for this chapter.
- `chapter_runtime_diagnostics`: runtime diagnostic payloads for this chapter.

Allowed text files:

- Writer draft markdown from `ChapterDraft.markdown`.
- Repair draft markdown from `ChapterDraft.markdown` on attempts where `attempt_index > 0`.
- Auditor feedback text derived from structured programmatic and LLM issues:
  - include `layer`, `rule_code`, `severity`, `location`, `message`, and `repair_hint`;
  - include `ChapterAuditResult.repair_hint`;
  - include `ChapterRepairDecision` summary.
- Accepted chapter draft markdown may be saved for accepted chapters because the calibration needs accepted-vs-failed comparison. Mark it as local diagnostic text, not final report.

Forbidden fields and raw payloads:

- Do not save `ChapterWriterPrompt.system_prompt`.
- Do not save `ChapterWriterPrompt.user_prompt`.
- Do not save `ChapterLLMRequest` raw request.
- Do not save `ChapterAuditLLMRequest.system_prompt`, `user_prompt`, or `draft_markdown` as request payload.
- Do not save provider raw HTTP body, headers, request payload, response JSON, or stack traces.
- Do not save API key, provider secret, full provider config, base URL if controller considers it sensitive, `Authorization`, `Bearer ...`, cookies, or environment dumps.
- Do not save final incomplete `report_markdown` and do not synthesize a partial full report.

Raw auditor response decision:

- Default implementation should not save `ChapterLLMAuditResult.raw_response`. Store normalized auditor feedback from parsed issues instead.
- If implementation finds raw auditor response is essential, it must be behind an explicit diagnostic flag and pass the same secret redaction scanner; otherwise stop and return a Blocking Question for Controller before saving raw responses.

## 5. Directory And Ignore Policy

Implementation must update `.gitignore` with:

```text
reports/llm-runs/
```

`reports/llm-runs/` is local generated evidence and must not be tracked by default.

The tracked review artifact may mention:

- the planned directory pattern;
- smoke command;
- high-level summarized evidence;
- local artifact path basename.

The tracked review artifact must not include:

- copied writer drafts;
- copied repair drafts;
- copied auditor feedback;
- raw provider text;
- local secrets;
- full run output.

Manual smoke evidence under `reports/manual-llm-smoke/` remains local input evidence for this gate. Do not add it to tracked files unless controller explicitly changes ownership.

## 6. Secret Redaction Policy

Add an allowlist-first redaction function in the artifact writer module. Recommended constants:

- `FORBIDDEN_SECRET_KEY_PATTERNS`: case-insensitive `authorization`, `api_key`, `apikey`, `token`, `secret`, `password`, `cookie`, `set-cookie`, `x-api-key`.
- `FORBIDDEN_SECRET_VALUE_PATTERNS`: `Bearer\s+\S+`, `sk-[A-Za-z0-9_-]+`, common OpenAI-compatible key patterns if known, and long header-like opaque values.
- `FORBIDDEN_PAYLOAD_LABELS`: `system_prompt`, `user_prompt`, `draft_markdown` as request field, `raw_response` when representing raw provider body, `provider_response`, `provider body`, `headers`.

Required behavior:

- All JSON metadata is built from typed allowlisted fields, not from `__dict__`, `asdict()` over whole objects, or exception string dumps.
- All saved text files pass a final canary scanner before write. If a forbidden pattern is detected, replace the matched segment with `[REDACTED]` and record `redaction_count` in the chapter JSON and manifest.
- The scanner must run on writer draft, repair draft, and normalized auditor feedback even though these are expected to be user-facing LLM text.
- If redaction changes text, the artifact remains usable but the manifest must include `redaction_applied=true`.
- Do not write secrets to stderr while reporting the artifact path.

## 7. Trigger Conditions

Default Slice 1 behavior:

- Write artifacts automatically only for `analyze --use-llm` runs that complete Service execution and return a typed `FundLLMAnalysisResult` with `final_assembly_result.report_markdown is None`.
- This includes Host failed terminal state caused by `_LLMIncompleteHostRunError`, because CLI still has `host_result.operation_result`.
- Do not create chapter artifacts for LLM provider config errors or construction errors thrown before Service execution.
- Do not create chapter artifacts for quality gate block or quality gate not-run block propagated before orchestration.
- Do not create chapter artifacts for Host failures without typed `operation_result`.
- Deterministic `analyze` and `checklist` must not create artifacts.

Explicit diagnostic flag:

- Recommended CLI option: `--llm-diagnostic-artifacts/--no-llm-diagnostic-artifacts`, default `True` for `--use-llm` incomplete runs and ignored/rejected when `--use-llm` is absent.
- Avoid adding a flag that saves accepted final report artifacts by default.
- If controller prefers no new CLI option, implementation may hard-code automatic incomplete artifact writing. In that case tests must assert accepted LLM success does not write diagnostics unless a future explicit flag is added.

Accepted final report behavior:

- Accepted `--use-llm` final reports should not default to writing chapter artifacts. The user-visible output remains stdout report plus existing quality summary behavior.
- If an explicit diagnostic flag later saves accepted runs, it must not be implemented in Slice 1 unless controller approves scope expansion.

## 8. Slice 1 Implementation Decisions

Slice id: `slice-1-incomplete-llm-run-artifact-retention`.

Objective: write local chapter-level diagnostics for incomplete `--use-llm` runs while preserving fail-closed CLI semantics.

Allowed files/modules:

- `fund_agent/services/llm_run_artifacts.py` new module.
- `fund_agent/services/__init__.py` only if exporting artifact helper is needed.
- `fund_agent/ui/cli.py` for CLI option, call site, and stderr artifact path line.
- `.gitignore`.
- Tests:
  - `tests/services/test_llm_run_artifacts.py` new module, or focused additions to `tests/services/test_chapter_orchestrator.py` if reviewer prefers fewer files.
  - `tests/ui/test_cli.py`.
  - `tests/services/test_fund_analysis_service_llm.py` only if needed to cover construction/quality-gate no-artifact cases.
- README/docs only if user-visible CLI option is added. If only automatic local diagnostics are added for incomplete runs, root `README.md` can be updated with one troubleshooting line; otherwise record docs decision in implementation artifact.

Exact data flow:

1. CLI builds execution request and runs Host as today.
2. If Host returns non-succeeded with typed incomplete `operation_result`, CLI calls Service artifact writer before printing incomplete stderr and exiting `1`.
3. If Host succeeds but typed result has `final_assembly_result.report_markdown is None`, CLI also calls artifact writer before `_llm_incomplete_message()` and exit `1`.
4. Artifact writer receives:
   - `FundLLMAnalysisResult`;
   - optional `host_result.run_id`;
   - output root default `Path("reports/llm-runs")`;
   - trigger string;
   - timestamp provider for tests.
5. Artifact writer builds directory name `<fund_code>-<report_year>-<YYYYMMDDTHHMMSS±TZ or Z>-<short_run_id_or_nonce>`.
6. Artifact writer writes files atomically and returns an object with `artifact_dir`, `manifest_path`, `summary_path`, `redaction_applied`, and `written_files`.
7. CLI prints one safe stderr line, for example:
   - `LLM incomplete diagnostic artifacts: reports/llm-runs/006597-2024-20260602T153000+0800-host_run_23a293/manifest.json`
   This line must not change exit code or stdout.

Safe write atomicity:

- Create the final run directory with `mkdir(parents=True, exist_ok=False)`.
- Write each file using a same-directory temporary filename, then `Path.replace()` into final path.
- Use UTF-8.
- JSON uses deterministic key order in tests (`sort_keys=True`) and indentation for local inspection.
- If artifact writing itself fails, do not convert incomplete LLM into success. Print a short safe warning to stderr and continue with original incomplete exit `1`. Do not include exception body if it may contain paths/secrets; include exception type and safe message only.

Function/type recommendations:

- `@dataclass(frozen=True, slots=True) class LLMRunArtifactWriteResult`.
- `write_llm_incomplete_run_artifacts(result: FundLLMAnalysisResult, *, host_run_id: str | None, output_root: Path = Path("reports/llm-runs"), clock: Callable[[], datetime] | None = None, trigger: str = "use_llm_incomplete") -> LLMRunArtifactWriteResult`.
- Private helpers:
  - `_build_manifest_payload(...)`.
  - `_build_summary_payload(...)`.
  - `_build_chapter_payload(...)`.
  - `_writer_draft_text(...)`.
  - `_auditor_feedback_text(...)`.
  - `_redact_text(...)`.
  - `_atomic_write_text(...)`.
  - `_atomic_write_json(...)`.

Invariants:

- Artifact writer must reject/raise `ValueError` if `result.final_assembly_result.report_markdown is not None` and trigger is the default incomplete trigger.
- Artifact writer must not call provider clients, document repositories, Host runner, deterministic renderer, or quality gate.
- Artifact writer must not mutate `ChapterRunResult` or `FundLLMAnalysisResult`.
- CLI stdout remains empty on incomplete.
- CLI exit code remains `1` on incomplete.
- Existing incomplete stderr summary remains present.

## 9. Slice 1 Tests And Validation

Unit tests for artifact module:

- `test_write_llm_incomplete_run_artifacts_writes_manifest_summary_and_chapters`
  - Build a fake `FundLLMAnalysisResult` with chapters matching accepted/failed states.
  - Assert `manifest.json`, `summary.json`, and per-chapter files exist under `tmp_path`.
  - Assert `summary.first_failed.chapter_id == 2`, category `prompt_contract`, subcategory `l1_numerical_closure`.
  - Assert chapter matrix includes accepted and failed rows.
- `test_artifact_includes_writer_repair_and_auditor_feedback`
  - Fake chapter with attempt 0 writer draft, failed audit, repair decision, attempt 1 repair draft, failed L1 audit.
  - Assert attempt 0 text uses `writer.md`, attempt 1 text uses `repair.md`, and feedback file contains normalized `L1` issue and repair hint.
- `test_artifact_redacts_secret_canaries`
  - Put canaries in writer markdown and auditor issue message: `Authorization`, `Bearer abc`, `sk-secret`, `api_key`.
  - Assert files do not contain canaries and manifest records redaction.
- `test_artifact_schema_does_not_serialize_prompts_or_raw_provider_payloads`
  - Put canaries in `ChapterWriteResult.prompt.system_prompt/user_prompt` and `ChapterLLMAuditResult.raw_response`.
  - Assert no artifact file contains those canaries.
- `test_artifact_writer_rejects_accepted_final_report_by_default`
  - Accepted final report result raises `ValueError` or returns skipped status by explicit design; prefer `ValueError` for direct helper calls.

CLI tests:

- Extend `test_analyze_cli_use_llm_incomplete_result_exits_without_fallback` or add a new test:
  - monkeypatch artifact output root to `tmp_path` or monkeypatch writer helper;
  - run `analyze 110011 --use-llm`;
  - assert `exit_code == 1`;
  - assert `stdout == ""`;
  - assert stderr includes original incomplete and Host summaries;
  - assert stderr includes safe artifact manifest path;
  - assert no deterministic report text appears.
- Add `test_analyze_cli_use_llm_config_error_does_not_write_artifacts`
  - Use existing config/construction error setup.
  - Assert artifact helper not called and no output directory created.
- Add `test_analyze_cli_deterministic_analyze_and_checklist_do_not_write_llm_artifacts`
  - Existing deterministic tests can be extended with a forbidden artifact helper monkeypatch.
- Add `test_analyze_cli_incomplete_artifact_write_failure_preserves_fail_closed`
  - Artifact helper raises `OSError`.
  - Assert exit `1`, stdout empty, incomplete summary present, safe warning present, no exception body with secrets.

Ignore validation:

- Add a test or static assertion that `.gitignore` contains `reports/llm-runs/`.
- Validation command:

```bash
pytest tests/services/test_llm_run_artifacts.py tests/ui/test_cli.py tests/services/test_chapter_orchestrator.py tests/services/test_fund_analysis_service_llm.py
```

Expected assertions:

- stdout empty for incomplete LLM.
- exit code `1` for incomplete LLM.
- artifact written for typed incomplete result.
- chapter matrix and first failed diagnostic retained.
- per-chapter writer/repair/auditor feedback files retained.
- secret canaries redacted.
- `reports/llm-runs/` ignored.
- deterministic analyze/checklist unaffected.

Manual smoke command after Slice 1:

```bash
python -m fund_agent.ui.cli analyze 006597 --report-year 2024 --use-llm > reports/manual-llm-smoke/006597-2024/stdout.md 2> reports/manual-llm-smoke/006597-2024/stderr.txt
printf '%s\n' "$?" > reports/manual-llm-smoke/006597-2024/exitcode
```

Expected when still incomplete:

- exit code remains `1`;
- `stdout.md` remains empty;
- stderr includes artifact manifest path under `reports/llm-runs/`;
- local artifact directory exists and is ignored by git.

## 10. Deferred Slice 2 / Future Gate Calibration Plan

Recommended status: deferred-with-owner to the future phase gate `MVP real LLM chapter acceptance calibration gate`.

Use this section only if either:

- controller rejects the phase upgrade and explicitly keeps the original single-gate shape; or
- a later phaseflow-controlled calibration gate adopts this plan section as input after Slice 1 artifact retention is accepted.

Future slice/gate id: `mvp-real-llm-chapter-acceptance-calibration`.

Prerequisite: artifact retention gate accepted and local real smoke artifact produced from `006597` / `2024` or an equivalent controller-approved smoke target.

Objective: use retained evidence to diagnose and fix real LLM chapter acceptance failures, starting with chapter 2 `prompt_contract/l1_numerical_closure`, without relaxing audit rules.

Current gate prohibition: do not implement any work in this section during the recommended `MVP incomplete LLM run artifact retention gate`.

Allowed files/modules depend on root cause:

- Prompt/repair guidance fixes:
  - `fund_agent/fund/chapter_writer.py` if writer protocol or repair context prompt needs clearer instructions.
  - prompt/config files under `fund_agent/config/` only if current prompts are stored there and used by writer path.
  - `docs/fund-analysis-template-draft.md` only if a template wording ambiguity is confirmed and controller accepts doc update scope.
- Diagnostic clarity fixes:
  - `fund_agent/services/chapter_orchestrator.py` if failure subcategory or repair diagnostics need clearer allowlisted fields.
  - `fund_agent/services/llm_run_artifacts.py` if artifact schema needs additional safe scalar/text fields.
- Code bug fixes:
  - exact module containing the bug, only after artifact/code evidence proves implementation violates intended contract.
- Tests:
  - `tests/fund/...` or `tests/services/...` matching the changed module.
  - `tests/ui/test_cli.py` only if CLI behavior changes; expected not needed for prompt-only calibration.

Root cause workflow:

1. Locate latest Slice 1 artifact manifest for the real smoke run.
2. Read `summary.json` and `chapters/chapter-02.json`.
3. Compare chapter 2 writer draft and repair draft against normalized auditor feedback:
   - Did the draft omit explicit `R = A + B - C` numeric closure where required?
   - Did it mention numeric components without closing the equation?
   - Did it include percentages/numbers but fail the exact `_NUMERICAL_CLOSURE_RE` intent?
   - Did repair guidance tell the model exactly how to resolve L1?
   - Did the model repair a different issue while preserving L1 failure?
4. Validate against code:
   - `_audit_numerical_closure()` in `chapter_auditor.py` is the source of L1 behavior.
   - `_repair_context_prompt()` and `_repair_context_from_audit()` in writer/orchestrator are likely prompt/guidance surfaces.
   - `_audit_prompt_contract_diagnostic()` maps programmatic `L1` to `l1_numerical_closure`; do not reclassify to hide failure.
5. Decide root cause category:
   - `writer_prompt_gap`: instructions did not make the L1 required closure obvious enough.
   - `repair_guidance_gap`: feedback was correct but repair context did not force the missing closure.
   - `diagnostic_clarity_gap`: audit is correct, but artifact/stderr lacks enough safe detail to guide repair.
   - `code_bug`: audit/writer parser rejects a valid compliant draft or required marker logic contradicts template.
6. Implement only the minimal fix for the proven category.

Chapter 2 priority:

- First fix must target chapter 2 L1 closure.
- Do not modify chapter 3/6 behavior until chapter 2 root cause is classified and either fixed or explicitly blocked.

Chapter 3 and 6 owner:

- After chapter 2 fix, rerun real smoke and inspect latest artifacts.
- If chapter 3/6 still fail, classify each using the same categories.
- Owner for prompt/repair calibration: implementation worker for Slice 2.
- Owner for suspected audit-rule semantic change: controller, because audit relaxation or semantics change is out of scope.
- Owner for provider instability/unavailability: controller to record blocked evidence; do not mask with deterministic fallback.

Forbidden fixes:

- Do not loosen `_audit_numerical_closure()` thresholds or regex merely to pass real output unless evidence proves code rejects semantically valid required closure and controller accepts a code-bug finding.
- Do not remove L1 from programmatic audit.
- Do not change `repair_budget`.
- Do not mark chapter failed as accepted.
- Do not enable incomplete debug markdown for CLI.

## 11. Deferred Calibration Tests And Validation

Recommended status: deferred-with-owner to the future phase gate `MVP real LLM chapter acceptance calibration gate`. Do not run or implement these tests as part of the recommended current artifact-retention gate except where they overlap with Slice 1 artifact schema and redaction tests.

Unit/targeted regression tests for the future calibration gate:

- If writer prompt/guidance changes:
  - Add tests that generated writer prompt for chapter 2 includes explicit L1 closure instruction and a concrete repair instruction when previous issues include `L1`.
  - Assert the prompt still does not include forbidden investment advice language.
  - Assert no prompt fields are newly persisted into artifact JSON.
- If repair context changes:
  - Add test for `_repair_context_from_audit()` or writer input generation showing L1 issue becomes a required correction with actionable text.
  - Assert repair attempt index remains correct and repair budget unchanged.
- If diagnostic clarity changes:
  - Add artifact test asserting chapter feedback includes L1 `rule_code`, `location`, `message`, `repair_hint`, and safe issue id, without raw provider request/headers/prompts.
- If code bug is fixed:
  - Add a minimal reproducer around the failing function using the actual draft pattern from artifact, reduced to non-secret text.
  - Assert the intended compliant closure passes and non-compliant text still fails.

Required local validation command:

```bash
pytest tests/services/test_llm_run_artifacts.py tests/services/test_chapter_orchestrator.py tests/services/test_fund_analysis_service_llm.py tests/ui/test_cli.py
```

Add narrower commands matching touched modules when practical, for faster fix loops.

Real smoke verification command:

```bash
python -m fund_agent.ui.cli analyze 006597 --report-year 2024 --use-llm > reports/manual-llm-smoke/006597-2024/stdout.md 2> reports/manual-llm-smoke/006597-2024/stderr.txt
printf '%s\n' "$?" > reports/manual-llm-smoke/006597-2024/exitcode
```

Expected outcomes:

- If accepted:
  - exit code `0`;
  - stdout contains a complete report;
  - stderr has quality summary and no incomplete Host summary;
  - no default incomplete artifact required.
- If still incomplete:
  - exit code `1`;
  - stdout empty;
  - stderr includes incomplete summary and new artifact path;
  - artifact shows whether chapter 2 still fails and why;
  - no deterministic fallback and no partial report.

Provider unavailable/blocking evidence:

- If real provider credentials or network are unavailable, implementation worker must not fake Slice 2 success.
- Record a durable implementation artifact with:
  - command run;
  - safe stderr summary;
  - exact blocker category: `missing_provider_config`, `provider_unavailable`, `provider_timeout`, `rate_limited`, or `other`;
  - whether unit regressions passed;
  - latest local artifact path if one was produced.
- Controller decides whether to defer real smoke verification or provide credentials.

## 12. Review Gates

Recommended gate sequence if controller accepts the phase upgrade:

1. Plan review using `$planreview` or equivalent review agent criteria.
2. Plan fix/re-review if findings are accepted.
3. Accepted plan local commit by controller only.
4. Slice 1 artifact retention implementation.
5. Slice 1 code review.
6. Slice 1 fix/re-review.
7. Accepted Slice 1 local commit by controller only.
8. Aggregate deepreview against `main` for the artifact-retention gate.
9. Aggregate fix/re-review if findings are accepted.
10. Accepted deepreview local commit by controller only.
11. Current gate stops with local artifacts and deferred phase-gate owner mapping.
12. Controller may then start/update phaseflow state for `MVP real LLM observability and chapter acceptance phase` using `docs/design.md` and `docs/implementation-control.md`; that is outside this plan artifact's implementation scope.

Fallback gate sequence only if controller explicitly keeps the original single-gate shape:

1. Complete the recommended steps 1-7 above.
2. Re-enter plan review or controller decision checkpoint using the Slice 1 artifacts.
3. Implement calibration from Section 10 only if the root cause is classifiable from retained artifacts and does not require progress UX, provider runtime budget calibration, score-loop entry, repair budget increase, audit relaxation, quality gate change, or deterministic fallback.
4. Review/fix/re-review and accepted calibration commit.
5. Aggregate deepreview and accepted deepreview commit.

Review emphasis:

- Artifact schema is allowlist-based and does not leak prompts/secrets.
- CLI fail-closed behavior is preserved.
- `reports/llm-runs/` is ignored.
- Calibration/progress/runtime/score-loop work is not smuggled into the current artifact-retention gate.
- No new external `dayu` runtime dependency.
- No unrelated dirty files are staged.

## 13. Stop Conditions And Residual Risk Owner

Stop conditions for Slice 1:

- Cannot safely write artifacts without serializing prompts/raw provider payloads.
- Artifact writer needs to store raw auditor response to diagnose root cause and no safe normalized alternative is enough.
- CLI cannot access typed incomplete `FundLLMAnalysisResult` for a target failure mode.
- Adding a CLI option creates user-visible contract ambiguity that controller has not approved.
- Secret redaction canary appears in any generated artifact.

Stop conditions for deferred calibration if controller later authorizes it:

- Slice 1 artifact is unavailable and real smoke cannot be rerun.
- Provider config/network is unavailable.
- Root cause appears to require relaxing audit rule semantics, changing quality gate, increasing repair budget, or accepting incomplete output.
- Chapter 2 failure cannot be reproduced or classified from artifact evidence.
- Fix would require touching architecture boundaries outside Service/Agent/Fund ownership.

Residual risk owners:

- Local artifact retention privacy risk: implementation worker owns redaction tests; controller owns final acceptance and any broader data retention policy.
- Real provider nondeterminism: Slice 2 worker records evidence; controller decides whether repeated smoke is sufficient.
- Chapter 2/3/6 acceptance failures after artifact retention: deferred-with-owner to future phase gate `MVP real LLM chapter acceptance calibration gate`.
- Progress and timeout UX gaps surfaced by smoke: deferred-with-owner to future phase gate `MVP LLM run progress and timeout UX gate`.
- Provider runtime budget gaps surfaced by smoke: deferred-with-owner to future phase gate `MVP provider runtime budget calibration gate`.
- Chapter generation score-loop entry: deferred-with-owner to future phase gate `MVP chapter generation score-loop entry gate`.
- README/docs scope: implementation worker proposes docs decision; controller accepts or defers based on user-visible behavior.

## 14. Completion Report Format For Workers

Slice 1 worker completion report:

```markdown
Gate: implementation
Work unit: MVP incomplete LLM run artifact retention gate
Slice: slice-1-incomplete-llm-run-artifact-retention
Approved plan: docs/reviews/mvp-real-llm-incomplete-run-artifact-retention-and-chapter-acceptance-calibration-plan-20260602.md

Changed files:
- ...

Implemented:
- ...

Validation:
- `pytest ...` -> pass/fail with key failure summary
- Manual smoke command -> pass/fail/not run with reason

Artifact behavior verified:
- stdout empty on incomplete:
- exit code 1 on incomplete:
- artifact path:
- redaction canary:
- reports/llm-runs ignored:

Docs decision:
- ...

Residual risks:
- ...

Self-check: pass
```

Deferred calibration worker completion report for a future gate or fallback single-gate decision:

```markdown
Gate: implementation
Work unit: MVP real LLM chapter acceptance calibration gate
Slice: mvp-real-llm-chapter-acceptance-calibration
Approved plan: docs/reviews/mvp-real-llm-incomplete-run-artifact-retention-and-chapter-acceptance-calibration-plan-20260602.md

Evidence used:
- latest Slice 1 artifact manifest:
- chapter 2 files inspected:
- chapter 3/6 files inspected:

Root cause classification:
- chapter 2:
- chapter 3:
- chapter 6:

Changed files:
- ...

Implemented:
- ...

Validation:
- unit/targeted pytest:
- real smoke command:
- result: accepted/incomplete/blocked

Audit semantics:
- repair budget unchanged:
- auditor/programmatic rules not relaxed:
- deterministic fallback not introduced:
- partial stdout not introduced:

Residual risks:
- ...

Self-check: pass
```

## Blocking Questions For Controller

No blocking question prevents the recommended artifact-retention gate from entering plan review.

Controller decision requested before accepted plan commit:

- Accept the recommended upgrade to `MVP real LLM observability and chapter acceptance phase` and narrow this gate to `MVP incomplete LLM run artifact retention gate`; or
- explicitly keep the original single-gate shape and accept the higher risk that calibration root cause is unknowable until after Slice 1 artifacts exist.

Implementation worker should not decide this shape question. If controller accepts the phase upgrade, the only implementation scope from this plan is Slice 1 artifact retention. The only embedded low-risk implementation choice remaining inside Slice 1 is whether to expose `--llm-diagnostic-artifacts`; the recommended default is automatic artifact writing for incomplete `--use-llm` only, with no accepted-run artifact saving in Slice 1.

## Planning Self-Check

- Current gate / role: plan gate; planning specialist only.
- Source of truth: AGENTS instructions, controller handoff, current branch/status, and code facts from CLI, Service orchestrator, writer/auditor, tests, and `.gitignore`.
- Scope boundary: this artifact assigns future implementation work; no code, staging, commits, pushes, PRs, or Gateflow controller actions performed.
- Stop conditions: no blocking question found; raw auditor response saving is explicitly not default and requires controller escalation if needed.
- Evidence and validation: plan includes work-unit shape recommendation, artifact schema, trigger policy, redaction policy, exact touched files for Slice 1, validation matrix, real smoke commands, deferred phase-gate owner mapping, and worker report format.
- Next action: controller should send this plan to plan review, then decide whether to accept the recommended phase upgrade before accepted plan commit.
