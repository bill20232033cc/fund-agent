# MVP Real LLM Incomplete-Run Artifact Retention Plan Review (DS)

## Review Metadata

- **Review role**: plan review specialist (not controller, not implementation)
- **Review target**: `docs/reviews/mvp-real-llm-incomplete-run-artifact-retention-and-chapter-acceptance-calibration-plan-20260602.md`
- **Review date**: 2026-06-02
- **Review classification**: `standard`
- **Gateflow status**: plan review only; no implementation, staging, commit, push, PR

## Evidence Basis

- Plan artifact (full read).
- `AGENTS.md` (authoritative execution rules).
- `docs/design.md` (current implementation sections and Route C future design).
- `docs/implementation-control.md` (current phase/gate/residuals/ledger).
- `.gitignore` (confirmed `reports/llm-runs/` not present).
- `fund_agent/ui/cli.py` (verified `_LLMIncompleteHostRunError`, `_llm_incomplete_message()`, `_first_failed_chapter_summary()`, `_chapter_matrix_summary()`, Host runner integration).
- `fund_agent/services/chapter_orchestrator.py` (verified `ChapterAttemptRecord`, `ChapterRunResult`, `ChapterOrchestrationResult`, `serialize_chapter_prompt_contract_diagnostics()`, `serialize_chapter_runtime_diagnostics()`).
- `fund_agent/fund/chapter_writer.py` (verified `ChapterWriteResult`, `ChapterDraft`, `ChapterWriterPrompt` with `system_prompt`/`user_prompt`).
- `fund_agent/fund/chapter_auditor.py` (verified `ChapterAuditResult`, `ChapterLLMAuditResult.raw_response`, `ChapterAuditIssue.repair_hint`).
- `fund_agent/services/final_chapter_assembler.py` (verified `FinalChapterAssemblyResult.report_markdown`, `allow_incomplete_debug_markdown`).
- `fund_agent/services/fund_analysis_service.py` (verified `FundLLMAnalysisResult`).
- `tests/ui/test_cli.py` (verified incomplete exit/secret safety tests).
- `tests/services/test_chapter_orchestrator.py` (verified serializer safe-scalar tests).
- `tests/services/test_fund_analysis_service_llm.py` (verified config error, construction error, missing writer/auditor, quality gate block/not-run tests).
- `reports/manual-llm-smoke/006597-2024/` (verified evidence directory exists per plan's direct evidence section).

## Review Findings

### Finding 1 — Code Facts Are Accurate and Verifiable

**Severity**: informational (no action required)

All "Current Code Facts" (Section 2) claims were independently verified against the current branch:

- CLI incomplete handling: `_LLMIncompleteHostRunError`, `_llm_incomplete_message()`, `_first_failed_chapter_summary()`, `_chapter_matrix_summary()`, `_hosted_llm_incomplete_message()` all confirmed at expected line locations.
- Service orchestrator: `ChapterAttemptRecord` retains `writer_result`, `audit_result`, `repair_decision`. `ChapterRunResult` retains `failure_category`, `failure_subcategory`. Both `serialize_chapter_prompt_contract_diagnostics()` and `serialize_chapter_runtime_diagnostics()` exist and output safe allowlisted scalars only.
- Writer: `ChapterWriteResult` has `prompt` (containing `system_prompt` and `user_prompt`). `ChapterDraft` has `markdown`. These forbidden/allowed distinctions match the plan's redaction policy exactly.
- Auditor: `ChapterLLMAuditResult` has `raw_response`. `ChapterAuditResult` has `programmatic`, `llm`, `repair_hint`.
- Final assembly: `FinalChapterAssemblyResult.report_markdown` is `None` when not accepted. `allow_incomplete_debug_markdown` exists but is default `False`.
- Tests: existing incomplete tests assert exit `1`, stdout empty, no deterministic fallback, and scan for 14+ forbidden secret strings.
- `.gitignore`: confirmed `reports/llm-runs/` is absent — plan's ignore gap identification is correct.

No code fact in Section 2 was found to be incorrect or misleading.

### Finding 2 — Work-Unit Shape Recommendation Is Sound

**Severity**: informational (controller decision required)

The plan recommends upgrading to a phase (`MVP real LLM observability and chapter acceptance phase`) with 5 gates, and narrowing the current gate to `MVP incomplete LLM run artifact retention gate` (Slice 1 artifact retention only).

The rationale holds under first-principles analysis:

1. Artifact retention is a **prerequisite** for calibration — without retained per-chapter evidence, calibration work risks guessing from stderr summaries.
2. Calibration, progress UX, runtime budget calibration, and score-loop entry are **separable concerns** with different owners, touchpoints, and risk profiles.
3. Combining them in one gate increases review scope and creates smuggling pressure.

The single-gate alternative is documented transparently (Section 1A, lines 63-69). It explicitly requires a hard stop after Slice 1 if artifacts indicate progress/timeout/runtime/score-loop work is the actual next step.

The deferred-with-owner assignments (Section 1A, lines 85-91) are explicit and complete: each of the 4 deferred gates has a named owner (controller + future planning/implementation workers) and a clear scope boundary.

**Recommendation**: Accept the phase upgrade. The single-gate alternative carries higher residual risk because Slice 2 calibration root cause is unknowable until Slice 1 artifacts exist — and the current evidence (`provider_runtime_timeout_small_prompt`) already suggests the blocker may be runtime, not prompt/audit.

### Finding 3 — Artifact Schema Is Sufficiently Concrete

**Severity**: informational (no action required)

The schema (Section 4) defines:

- **Directory layout**: `reports/llm-runs/<fund_code>-<report_year>-<timestamp>/` with `manifest.json`, `summary.json`, `chapters/chapter-XX.json`, and text files (`writer.md`, `repair.md`, `auditor-feedback.md`).
- **`manifest.json`**: 11 fields with explicit types and values. Includes `redaction_policy` object for transparency.
- **`summary.json`**: 12 fields. `chapter_matrix` has one row per chapter with all key status fields. `first_failed` captures the diagnostic anchor.
- **`chapter-XX.json`**: comprehensive attempt-level metadata. Writer status, draft file, issues, audit status, programmatic/LLM issues, repair decision — all allowlisted fields.
- **Text files**: writer/repair draft markdown from `ChapterDraft.markdown`, auditor feedback derived from structured issues (not raw response).
- **Forbidden fields**: prompts, raw provider payloads, API keys, secrets, report markdown — explicitly enumerated.

The schema is concrete enough for an implementation worker to write serialization code without designing new types or making judgment calls about what to include/exclude.

One minor ambiguity: the `repair.md` suffix convention (lines 202-203) says `attempt_index > 0` → `repair.md`. With the current `repair_budget` of 1, this means at most `attempt-01-repair.md`. If `repair_budget` is ever increased, the naming is unambiguous: `attempt-02-repair.md`, `attempt-03-repair.md`, etc. No change needed.

### Finding 4 — Secret/Redaction Policy Is Sufficiently Safe

**Severity**: no finding (policy meets all safety criteria)

The redaction policy (Section 6) uses three complementary defense layers:

1. **Allowlist-first serialization** (line 325): JSON metadata is built from typed allowlisted fields, not from `__dict__`, `asdict()`, or exception string dumps. This is the strongest defense — it prevents accidental leakage through reflection-based serialization.

2. **Forbidden pattern scanning** (lines 319-321): Three categories of forbidden patterns — key names (`authorization`, `api_key`, `apikey`, `token`, `secret`, `password`, `cookie`), value patterns (`Bearer\s+\S+`, `sk-[A-Za-z0-9_-]+`), and payload labels (`system_prompt`, `user_prompt`, `draft_markdown`, `raw_response`, `provider_response`, `headers`).

3. **Canary scanner before write** (lines 326-328): Redacts matched segments and records `redaction_count` in chapter JSON and manifest. Artifact remains usable but manifest records `redaction_applied=true`.

The policy correctly prohibits: API key, Authorization, provider secrets, raw HTTP headers/body, prompts, raw provider response, complete sensitive config. Allowed LLM text is limited to writer draft markdown and normalized auditor feedback — both are local ignored diagnostic artifacts.

The forbid list aligns with the existing CLI secret safety test (`tests/ui/test_cli.py` lines 1843-1858) which already scans for 14+ forbidden strings in stderr output.

**Defense-in-depth note**: The redaction function should be tested with edge cases — e.g., `Authorization` appearing inside a legitimate markdown code block, `Bearer` appearing as a noun in analysis text (unlikely but possible). The `[REDACTED]` replacement preserves readability for these edge cases.

### Finding 5 — Trigger Conditions Are Correct

**Severity**: no finding (conditions match fail-closed design)

The trigger conditions (Section 7) correctly limit artifact creation to:

- `analyze --use-llm` with typed `FundLLMAnalysisResult` where `final_assembly_result.report_markdown is None`.
- Host failed terminal state caused by `_LLMIncompleteHostRunError` (because CLI still has `host_result.operation_result`).

Artifacts are correctly **not** created for:

- Provider config errors or construction errors thrown before Service execution.
- Quality gate block or quality gate not-run block propagated before orchestration.
- Host failures without typed `operation_result`.
- Deterministic `analyze` and `checklist`.

This matches the existing test coverage: `test_build_fund_llm_execution_request_raises_config_error_before_host_run`, `test_build_fund_llm_execution_request_raises_construction_error_before_host_run`, `test_analyze_with_llm_propagates_quality_gate_block_before_orchestration`, `test_deterministic_analyze_does_not_call_llm_orchestrator_path`, `test_deterministic_checklist_does_not_call_llm_orchestrator_path` all exist and pass.

### Finding 6 — Fail-Closed Preservation Is Explicit and Complete

**Severity**: no finding (fail-closed invariants are clear and enforceable)

Section 8 invariant list (lines 411-417) preserves all fail-closed properties:

- Artifact writer rejects accepted final reports (raises `ValueError`).
- Artifact writer does not call provider, repository, Host runner, deterministic renderer, or quality gate.
- CLI stdout remains empty, exit code remains `1`.
- Existing incomplete stderr summary remains present (artifact path is additive, not replacement).

Section 13 stop conditions (lines 663-668) are well-defined: if any invariant cannot be met (e.g., cannot write artifacts without leaking prompts), implementation must stop.

### Finding 7 — Slice 1 Implementation Decisions Are Code-Generation-Ready

**Severity**: informational (no action required)

Section 8 provides everything an implementation worker needs:

- **Exact files/modules to touch**: `fund_agent/services/llm_run_artifacts.py` (new), `fund_agent/ui/cli.py` (CLI option + call site), `.gitignore`, test files.
- **Exact data flow**: 7-step sequence from CLI → Host → Service artifact writer → stderr path line.
- **Function/type signatures**: `LLMRunArtifactWriteResult`, `write_llm_incomplete_run_artifacts()` with parameter names and types, 8 private helper function names.
- **Write atomicity**: `mkdir(parents=True, exist_ok=False)` + temp file + `Path.replace()`, UTF-8, `sort_keys=True` for JSON.
- **Error handling**: artifact write failure does not convert incomplete to success; safe warning to stderr with exception type only.

An implementation worker can proceed directly to Slice 1 without designing schema, paths, trigger conditions, redaction, or tests — all are specified.

### Finding 8 — Test Coverage Is Comprehensive

**Severity**: informational (no action required)

The test plan (Section 9) covers:

| Test | Negative/positive | Coverage target |
|------|-------------------|-----------------|
| Artifact writes manifest/summary/chapters | Positive | Module unit |
| Writer repair + auditor feedback files | Positive | Module unit |
| Secret canary redaction | Negative | Module unit (redaction) |
| No prompt/raw provider payload leakage | Negative | Module unit (schema) |
| Rejects accepted final report | Negative | Module unit (invariant) |
| CLI incomplete exit + artifact path | Positive | CLI integration |
| Config error no artifacts | Negative | CLI integration |
| Deterministic no artifacts | Negative | CLI integration |
| Artifact write failure preserves fail-closed | Negative | CLI integration (resilience) |
| `.gitignore` contains `reports/llm-runs/` | Static | Infrastructure |

The plan also specifies the exact validation command and expected assertions per test category.

One gap: the plan does not explicitly test that the `--no-llm-diagnostic-artifacts` flag (if implemented) suppresses artifact creation. However, the plan says the recommended default is automatic artifact writing with no flag, so this gap only materializes if the flag is implemented.

### Finding 9 — No Scope Creep Detected

**Severity**: informational (no action required)

I conducted an adversarial scope-creep scan against all 10 categories listed in the review focus area #9. Results:

| Smuggling target | Present in plan? | Verdict |
|-----------------|------------------|---------|
| Progress UX | Explicitly forbidden (Section 1A, 3) | Clean |
| Runtime budget calibration | Explicitly deferred to phase gate 4 | Clean |
| `chapter_generation_score` | Explicitly deferred to phase gate 5 | Clean |
| Agent/dayu/tool-loop | Explicitly forbidden (Section 3) | Clean |
| Historical residuals | Explicitly forbidden (Section 3) | Clean |
| Calibration implementation | Only if controller keeps single-gate; otherwise deferred to phase gate 3 | Clean |
| Deterministic fallback | Explicitly forbidden (Section 3, 8) | Clean |
| Quality gate change | Explicitly forbidden (Section 3) | Clean |
| Repair budget increase | Explicitly forbidden (Section 3) | Clean |
| Auditor relaxation | Explicitly forbidden (Section 3) | Clean |

The anti-smuggling rule (Section 1A, lines 93-103) provides an explicit checklist of 10 forbidden activities for the current gate.

### Finding 10 — One Gap: No Explicit Artifact Retention Lifecycle Policy

**Severity**: low (non-blocking, can be addressed in implementation or controller judgment)

The plan defines where artifacts are written (`reports/llm-runs/`) and that they are git-ignored, but does not address:

1. **Retention duration**: Should old artifact directories be cleaned up? If so, by what policy (manual only, age-based, count-based)?
2. **Disk space accumulation**: Each incomplete run produces per-chapter drafts/feedback. Over many runs, this directory could grow significantly.
3. **Privacy implication**: Writer drafts contain fund analysis text that, while not containing secrets, is derived from real fund annual report data. The plan notes "local artifact retention privacy risk" in residual risks (Section 13) but defers broader data retention policy to controller.

This is not a blocking finding — the plan correctly identifies privacy risk as a residual owner for controller. An implementation worker could add a note in the artifact directory README or a `retention_policy` field in manifest.json. But the plan doesn't require this, and the gap is acceptable for a local diagnostic tool.

### Finding 11 — Rejected Accepted Final Report Behavior Could Be More Specific

**Severity**: low (non-blocking, implementation choice)

The plan says the artifact writer must "reject/raise `ValueError` if `result.final_assembly_result.report_markdown is not None` and trigger is the default incomplete trigger" (Section 8, line 412). This is correct for direct calls to `write_llm_incomplete_run_artifacts()`.

However, the CLI call site has two paths where artifacts could theoretically be triggered:

1. Host non-succeeded with typed incomplete `operation_result` (correct trigger).
2. Host succeeded but `report_markdown is None` (correct trigger, line 374).

In the second case, if a future code change accidentally sets `report_markdown` to a non-None value during an incomplete run, the `ValueError` guard will catch it. Good.

But the plan does not specify whether a future explicit diagnostic flag for accepted runs would use the same `write_llm_incomplete_run_artifacts()` function or a separate entry point. This is explicitly deferred (Section 7, lines 349-351), so it's not a gap — just a reminder that the `ValueError` guard should not be weakened when that future flag is added.

## Open Questions

### OQ1 — Controller Decision on Phase Upgrade

The plan requests controller decision on whether to:
- Accept the phase upgrade (`MVP real LLM observability and chapter acceptance phase`) and narrow current gate to `MVP incomplete LLM run artifact retention gate`; or
- Keep the original single-gate shape.

This is a genuine controller decision with different risk profiles. The phase upgrade has lower risk (clean separation, clear stop point, deferred-with-owner for all follow-up work). The single-gate alternative requires a hard stop after Slice 1 if artifacts show the blocker is runtime/UX/score-loop rather than prompt/audit.

**Recommendation**: Accept the phase upgrade. Rationale: the current `implementation-control.md` ledger shows the real provider blocker is `provider_runtime_timeout_small_prompt` — a runtime issue, not a prompt/audit issue. Calibrating chapter acceptance before fixing the runtime blocker would be working on the wrong problem.

### OQ2 — CLI Flag Decision

The plan recommends automatic artifact writing for incomplete `--use-llm` (no new CLI flag by default). Alternative: expose `--llm-diagnostic-artifacts` / `--no-llm-diagnostic-artifacts`.

The automatic approach is simpler but adds a new stderr line to every incomplete run. Users who are accustomed to the current compact stderr output will see an additional line with a file path. This is a user-visible behavior change.

The flag approach gives users control but adds CLI surface area.

**Recommendation**: Keep automatic writing as the plan recommends. The stderr path line is useful (it tells users where to find diagnostics) and adds negligible noise. The `--no-llm-diagnostic-artifacts` flag can be added later if users complain.

### OQ3 — Raw Auditor Response

The plan says default implementation should NOT save `ChapterLLMAuditResult.raw_response` (Section 4). If implementation finds raw response is essential for root cause diagnosis, it must escalate to controller.

Is this escalation path clear enough for an implementation worker? If an implementation worker is uncertain whether normalized feedback is sufficient, the plan's stop condition (Section 13: "Artifact writer needs to store raw auditor response to diagnose root cause and no safe normalized alternative is enough") will trigger. This is adequate — the worker will stop and ask.

**Status**: Resolved by plan's stop condition. No change needed.

## Residual Risks

| Risk | Likelihood | Impact | Owner |
|------|-----------|--------|-------|
| Artifact directory grows without bound | Medium (if many incomplete runs) | Low (local disk only) | Controller (broader retention policy) |
| Writer draft contains sensitive fund data in edge case | Low (allowlist-first + canary scanner) | Low (local file, git-ignored) | Implementation worker (redaction tests) |
| Real provider nondeterminism makes artifacts non-reproducible | High (LLM inherent) | Low (diagnostic purpose only) | Controller (record evidence; do not treat as golden) |
| Artifact format changes break deferred calibration tools | Low (schema versioned) | Medium (rework) | Future calibration gate worker |
| `reports/llm-runs/` accidentally tracked if `.gitignore` update fails | Low (test validates) | Low (local only, no secrets) | Implementation worker (ignore test) |

## Verdict

**PASS with recommendations.**

The plan is handoff-ready and code-generation-ready. An implementation worker can proceed directly to Slice 1 artifact retention without designing schema, paths, trigger conditions, redaction policy, or tests.

The work-unit shape recommendation (phase upgrade + narrow gate) is well-reasoned and supported by evidence from `docs/implementation-control.md` which shows the real provider blocker is `provider_runtime_timeout_small_prompt` — a runtime issue, not a prompt/audit calibration issue.

The artifact schema is concrete. The redaction policy is defense-in-depth with three layers. The trigger conditions are precise and fail-closed. The scope boundaries are clean with explicit anti-smuggling rules.

No blocking findings. Two low-severity informational observations (Finding 10: retention lifecycle; Finding 11: accepted-report guard specificity). One controller decision pending (OQ1: phase upgrade vs single-gate). One implementation choice (OQ2: CLI flag).

**Recommended next action**: Controller decides OQ1 (recommend phase upgrade), then accepted plan commit. After accepted plan commit, proceed to Slice 1 implementation with the verified code facts and specified file/module list.

---

*Review conducted in planreview specialist role. No code, staging, commits, pushes, PRs, or Gateflow controller actions performed.*
