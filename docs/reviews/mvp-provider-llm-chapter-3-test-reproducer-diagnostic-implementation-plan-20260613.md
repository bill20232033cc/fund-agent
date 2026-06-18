# Provider/LLM Chapter 3 Test-reproducer / Diagnostic Implementation Plan

Date: 2026-06-13

Gate: `Provider/LLM Chapter 3 Test-reproducer / Diagnostic Implementation Planning Gate`

Role: AgentCodex / ProCodex planning worker only.

Status: `PLAN_READY_FOR_REVIEW_NOT_READY`

Release/readiness: `NOT_READY`

Accepted evidence checkpoint: `4a7c191`

## 1. Goal And Non-goals

### Goal

Produce a no-live, code-generation-ready implementation plan for the accepted
`DIAGNOSTIC_PROPAGATION_GAP_PRE_PROVIDER` residuals:

1. Add an exact Chapter 3 no-live failure-shape reproducer for the accepted
   live metadata shape: Chapter 3 `ValueError`, Service stop reason
   `llm_exception`, failure category `code_bug`, provider attempt count `0`.
2. Add Service/Agent bridge assertions proving pre-provider internal code bugs
   project to Service-safe `llm_exception` / `code_bug` diagnostics.
3. Propagate pre-provider `max_output_chars` as a safe scalar into runtime
   diagnostics and first-failed diagnostic selection.
4. Add an artifact fixture proving code-bug / pre-provider runtime lineage is
   retained by `summary.json` through allowlisted safe diagnostics.

This plan treats "exact" as exact safe-metadata failure shape. It does not
replay the live command and does not read `004393 / 2025` source bodies. If an
implementation worker concludes that exact source identity requires PDF/cache/
provider/source-body access, implementation must stop and return to controller.

### Non-goals

- Do not run live/provider/LLM/network/PDF/FDR/source/cache/helper commands.
- Do not run `fund-analysis analyze`, `fund-analysis checklist` or
  `fund-analysis analyze-annual-period`.
- Do not change provider config, provider defaults, model, base URL, timeout
  budgets or env loading.
- Do not change EID source policy, fallback behavior or annual-report source
  acquisition.
- Do not convert code bugs into provider availability or provider runtime
  failures.
- Do not expose prompt text, draft text, provider bodies, raw responses, API
  keys, headers, credentials or secrets in diagnostics or artifacts.
- Do not pass explicit parameters via `extra_payload`; all new diagnostic inputs
  must be typed explicit parameters.
- Do not update README, `docs/design.md`, `docs/implementation-control.md` or
  source-truth docs in this implementation work unit.
- Do not stage, commit, push, PR, merge, mark-ready, cleanup, delete, move,
  archive or ignore.

## 2. Accepted Evidence Basis From `4a7c191`

The controller accepted
`docs/reviews/mvp-provider-llm-chapter-3-code-bug-root-cause-evidence-controller-judgment-20260613.md`
with status `ACCEPT_EVIDENCE_NOT_READY`.

Accepted facts:

- Current operational annual-report source truth remains EID single-source:
  `selected_source=eid`, `source_mode=single_source_only`,
  `fallback_enabled=false`.
- Eastmoney, fund-company/CDN, CNINFO and annual-report fallback are not current
  source truth, not current execution paths and not authorized current sources.
- The accepted Route C live execution failed closed: exit `1`, empty stdout,
  incomplete final assembly, Chapter 3 `llm_exception` / `code_bug` /
  `ValueError`, provider attempt count `0`.
- `FUND_AGENT_LLM_MAX_OUTPUT_CHARS=12000` is an accepted command fact; runtime
  metadata `max_output_chars=null` is a blocker residual.
- H1 is rejected for the covered no-live typed path, with residual missing exact
  Chapter 3 reproducer.
- H2 is rejected for inspected Chapter 3 typed rows, with residual missing exact
  fixture/assertion for the live failure shape.
- H3 is accepted as expected mapping needing diagnostic clarity:
  `blocked_internal_code_bug` maps to Service `llm_exception` while preserving
  `code_bug`.
- H4 is accepted as `DIAGNOSTIC_PROPAGATION_GAP_PRE_PROVIDER`: runtime policy
  carries the cap, provider diagnostics preserve the cap, but unknown
  pre-provider exception diagnostics and terminal selection do not expose it in
  first-failed metadata.
- H5 artifact summary extraction mismatch is rejected; the residual is a missing
  code-bug/pre-provider artifact fixture.
- The prior memory `rg` was accepted only as
  `DEVIATION_NOT_EVIDENCE`. This plan and the future implementation gate must
  not probe memory.

Accepted no-live validation from the evidence gate was:

```text
uv run pytest tests/services/test_fund_analysis_service_llm.py tests/services/test_chapter_orchestrator.py tests/services/test_llm_run_artifacts.py tests/agent/test_runner.py -q
# 125 passed in 1.07s

uv run ruff check fund_agent/services/fund_analysis_service.py fund_agent/services/chapter_orchestrator.py fund_agent/services/llm_run_artifacts.py fund_agent/services/agent_bridge.py fund_agent/agent/runner.py fund_agent/fund/chapter_writer.py tests/services/test_fund_analysis_service_llm.py tests/services/test_chapter_orchestrator.py tests/services/test_llm_run_artifacts.py tests/agent/test_runner.py
# All checks passed!
```

Those commands are evidence basis only; this planning gate did not rerun them.

## 3. Architecture And Invariants

- Service owns request/runtime assembly, provider construction, runtime ceilings,
  Host bridge invocation and final product fail-closed mapping.
- Host remains lifecycle-only and business-opaque.
- Agent owns body-chapter runner, task state, ToolTrace and Fund tool invocation.
- Fund owns CHAPTER_CONTRACT / typed required-output writer input and audit
  semantics.
- `max_output_chars` is already a typed field in `ChapterOrchestrationPolicy`,
  `AgentRunPolicy`, writer input and provider runtime budget. The implementation
  must keep it typed and explicit.
- Runtime diagnostics must remain allowlist-only safe scalar payloads.
  `max_output_chars`, `error_type`, operation, attempt indices and category
  fields are safe; prompt/draft/provider/raw/secret/message bodies are not.

## 4. Implementation Slices

### Slice S1 - Agent And Service Reproducer Tests

Objective: add no-live tests that reproduce the accepted Chapter 3 failure
shape before changing diagnostic behavior.

Allowed files:

- `tests/agent/test_runner.py`
- `tests/services/test_fund_analysis_service_llm.py`

Exact changes:

1. In `tests/agent/test_runner.py`, add
   `test_chapter_3_value_error_is_internal_code_bug_without_provider_runtime`.
   Use existing `_FakeWriter`, `_FakeAuditor`, `_projection()` and
   `run_agent_body_chapters()`.
2. Configure `_FakeWriter(actions={3: ValueError("Authorization Bearer sk-secret prompt raw")})`.
3. Run `run_agent_body_chapters(_projection((3,)), llm_clients=AgentLLMClients(...), policy=AgentRunPolicy(target_chapter_ids=(3,), max_output_chars=12000, typed_template_path="typed_template_contract"))`.
4. Assert:
   - writer request chapter ids are `[3]`;
   - run status is blocked or failed according to current Agent aggregate
     semantics, but the single task is `status=="failed"`;
   - task terminal state is `blocked_internal_code_bug`;
   - task failure category is `code_bug`;
   - no provider runtime category is introduced;
   - rendered blocked reasons do not contain `Authorization`, `Bearer`,
     `sk-secret` or `prompt raw`.
5. In `tests/services/test_fund_analysis_service_llm.py`, add
   `test_analyze_with_llm_execution_projects_chapter_3_value_error_as_code_bug_safe_diagnostic`.
   Use existing `_FakeExtractor`, `_bundle`, `_FakeChapterLLMClient`,
   `_FakeAuditLLMClient`, `_execution_request()` and `FundAnalysisService`.
6. Build a test execution request with
   `ChapterOrchestrationPolicy(target_chapter_ids=(3,), max_repair_attempts=0, max_output_chars=12000, prompt_payload_mode="compact", typed_template_path="typed_template_contract", run_programmatic_audit=False)`.
7. Use a fake writer that raises `ValueError("Authorization Bearer sk-secret prompt raw")`.
8. Await `service.analyze_with_llm_execution(execution_request)` and assert:
   - orchestration status is `blocked` or `partial` only if current assembly
     accepted no chapters outside target scope; final assembly remains
     `incomplete`;
   - Chapter 3 status is `failed`;
   - Chapter 3 stop reason is `llm_exception`;
   - Chapter 3 failure category is `code_bug`;
   - runtime diagnostics contain `error_type=="ValueError"`;
   - diagnostics do not contain secret-like substrings;
   - deterministic fallback is not used and no accepted final report is exposed.

Expected review signal:

- These tests may fail before S2 because current diagnostics do not propagate
  `max_output_chars` for unknown pre-provider code bugs. They must not be
  weakened to accept `max_output_chars=None`.

Stop conditions:

- If either test requires live provider credentials, source-body access or
  changing annual-report source identity, stop.
- If Service execution unexpectedly raises a new public exception instead of
  returning incomplete typed result, stop and route to controller before
  changing public exception semantics.

### Slice S2 - Safe Pre-provider Runtime Diagnostic Propagation

Objective: propagate typed `max_output_chars` into unknown pre-provider code-bug
runtime diagnostics and make terminal selection treat the code-bug diagnostic as
representative for `llm_exception` / `code_bug`.

Allowed files:

- `fund_agent/services/chapter_orchestrator.py`
- `fund_agent/services/agent_bridge.py`
- `tests/services/test_chapter_orchestrator.py`
- `tests/services/test_fund_analysis_service_llm.py`

Exact changes:

1. In `fund_agent/services/chapter_orchestrator.py`, extend
   `_exception_runtime_diagnostics()` with an explicit keyword-only parameter:
   `max_output_chars: int | None = None`.
2. When provider diagnostics exist, keep current `_enrich_provider_diagnostic()`
   behavior unchanged. Do not overwrite provider diagnostic caps.
3. When constructing the fallback unknown-exception
   `ChapterLLMRuntimeDiagnostic`, set `max_output_chars=max_output_chars`.
4. In `fund_agent/services/agent_bridge.py`, thread the Service policy cap into
   diagnostic construction:
   - change `_service_chapter_result_from_task(task, *, projection)` to accept
     `max_output_chars: int | None`;
   - pass `input_data.policy.max_output_chars` from the top-level bridge call
     when mapping `agent_run.tasks`;
   - pass the same cap into `_service_attempt_from_agent()` and
     `_runtime_diagnostics_from_task()`;
   - pass `max_output_chars=max_output_chars` to both
     `_exception_runtime_diagnostics()` calls.
5. In `fund_agent/services/chapter_orchestrator.py`, update terminal diagnostic
   selection for pre-provider code bugs:
   - add a small private helper such as `_is_code_bug_runtime_diagnostic(result, diagnostic)`;
   - it must return true only when `result.stop_reason=="llm_exception"`,
     `result.failure_category=="code_bug"`,
     `diagnostic.chapter_failure_category=="code_bug"` and
     `diagnostic.provider_runtime_category is None`;
   - use it in `_terminal_runtime_diagnostic()` before the existing
     provider-runtime fallback for stop reasons without an expected provider
     category;
   - use the same helper in `_diagnostic_matches_terminal()` so representative
     diagnostics include the code-bug diagnostic.
6. Do not add `llm_exception` to a provider-runtime category mapping. The point
   is to keep code bugs distinguishable from provider runtime failures.
7. Add or update a focused test in `tests/services/test_chapter_orchestrator.py`:
   `test_chapter_3_pre_provider_value_error_serializes_safe_runtime_cap`.
   Use existing `_ChapterPlanWriterClient` or `_FakeChapterLLMClient` with
   Chapter 3 `ValueError`, policy `target_chapter_ids=(3,)`,
   `max_output_chars=12000`, `typed_template_path="typed_template_contract"`.
8. Assert from `serialize_chapter_runtime_diagnostics(result)`:
   - `first_failed["chapter_id"] == 3`;
   - `first_failed["stop_reason"] == "llm_exception"`;
   - `first_failed["category"] == "code_bug"`;
   - `first_failed["provider_attempt_count"] == 0`;
   - `first_failed["provider_runtime_categories"] == ()`;
   - `first_failed["max_output_chars"] == 12000`;
   - `first_failed["terminal_runtime_diagnostic_present"] is True`;
   - `first_failed["diagnostic_consistency_status"] == "consistent"`;
   - chapter runtime diagnostic payload includes
     `error_type=="ValueError"` and `max_output_chars==12000`;
   - serialized payload string does not contain secret-like substrings.

Expected behavior after S2:

- Pre-provider `ValueError` remains `llm_exception` / `code_bug`.
- Provider attempt count remains `0`.
- `max_output_chars` appears as a safe scalar in the code-bug runtime diagnostic
  and first-failed runtime summary.
- Provider diagnostics and timeout logic are unchanged.

Stop conditions:

- Stop if implementation requires adding raw exception messages, prompt text,
  provider bodies or model names to serialized payloads.
- Stop if the simplest fix would classify unknown code bugs as provider runtime
  availability.
- Stop if any explicit cap must be carried through `extra_payload`.

### Slice S3 - Artifact Code-bug / Pre-provider Fixture

Objective: lock the artifact writer's behavior for code-bug / pre-provider
runtime lineage without changing artifact redaction policy or source inputs.

Allowed files:

- `tests/services/test_llm_run_artifacts.py`

Exact changes:

1. Add a helper such as `_incomplete_code_bug_pre_provider_result()` that builds
   a `FundLLMAnalysisResult` with:
   - an accepted Chapter 1 run using existing helper patterns;
   - a failed Chapter 3 run with `status=="failed"`,
     `stop_reason=="llm_exception"`, `failure_category=="code_bug"`,
     `failure_subcategory` preserved if current constructor requires it;
   - a chapter-level `ChapterLLMRuntimeDiagnostic` with
     `operation="writer"`, `chapter_id=3`, `fund_code` and `report_year` from
     the in-memory projection, `repair_attempt_index=0`,
     `provider_attempt_index=None`, `provider_max_attempts=None`,
     `provider_runtime_category=None`, `chapter_failure_category="code_bug"`,
     `error_type="ValueError"`, `max_output_chars=12000`;
   - no message, prompt, raw provider body, headers, model name or secrets.
2. Add
   `test_artifact_records_chapter_3_pre_provider_code_bug_runtime_lineage`.
3. Call `write_llm_incomplete_run_artifacts()` with `tmp_path` and read
   `summary.json`.
4. Assert `summary["runtime_diagnostics"]["first_failed"]` contains:
   - `chapter_id == 3`;
   - `stop_reason == "llm_exception"`;
   - `category == "code_bug"`;
   - `provider_attempt_count == 0`;
   - `provider_max_attempts is None`;
   - `provider_runtime_categories == []` or `()`, matching JSON decoding;
   - `max_output_chars == 12000`;
   - `terminal_runtime_diagnostic_present is True`;
   - `diagnostic_consistency_status == "consistent"`.
5. Assert the corresponding `chapter_runtime_matrix` row and
   `chapters/chapter-03.json` runtime diagnostics include the same safe scalar
   lineage.
6. Assert artifact contents do not include `SYSTEM_PROMPT_CANARY`,
   `USER_PROMPT_CANARY`, `RAW_AUDITOR_RESPONSE_CANARY`, `raw_response`,
   `Authorization`, `Bearer` or `sk-`.

Expected behavior after S3:

- Artifact writer remains faithful to serializer output.
- No new raw body fields are added.
- H5 remains rejected; the fixture closes the missing code-bug/pre-provider
  artifact residual only.

Stop conditions:

- Stop if artifact writer must be changed to store prompt/provider/raw body
  fields.
- Stop if top-level `summary["first_failed"]` is broadened with runtime details
  instead of using `summary["runtime_diagnostics"]["first_failed"]`; that would
  be a public artifact schema decision requiring controller review.

### Slice S4 - Focused Regression And Boundary Checks

Objective: run the no-live focused validation matrix and record results in the
implementation artifact.

Allowed files:

- No new source changes unless S1-S3 tests reveal a direct gap inside their
  allowed files.
- Implementation artifact path to be assigned by controller in the future
  implementation gate.

Exact changes:

- Do not change runtime behavior beyond S2.
- Do not update docs except the future implementation artifact.
- Do not add cleanup, ignore rules, source policy docs or README edits.

Expected behavior after S4:

- The new no-live tests pass.
- Existing focused four-file tests pass.
- Ruff passes on the exact touched source/test surface.
- Release/readiness remains `NOT_READY`.

## 5. Required Tests / Assertions / Fixtures

Required new or updated assertions:

| File | Test / fixture | Required assertion |
|---|---|---|
| `tests/agent/test_runner.py` | `test_chapter_3_value_error_is_internal_code_bug_without_provider_runtime` | Ch3 `ValueError` remains Agent internal code bug, not provider runtime; no secret leakage. |
| `tests/services/test_fund_analysis_service_llm.py` | `test_analyze_with_llm_execution_projects_chapter_3_value_error_as_code_bug_safe_diagnostic` | Service execution path projects Ch3 pre-provider code bug to `llm_exception` / `code_bug`, incomplete final assembly, no deterministic fallback. |
| `tests/services/test_chapter_orchestrator.py` | `test_chapter_3_pre_provider_value_error_serializes_safe_runtime_cap` | Runtime serializer exposes `max_output_chars=12000`, provider attempt count `0`, terminal diagnostic present and consistent. |
| `tests/services/test_llm_run_artifacts.py` | `_incomplete_code_bug_pre_provider_result()` and `test_artifact_records_chapter_3_pre_provider_code_bug_runtime_lineage` | Artifact summary retains code-bug/pre-provider safe scalar runtime lineage without prompt/provider/raw/secret leakage. |

Fixtures must stay in-memory and no-live. They may use existing fake extractors,
fake writer/auditor clients and in-memory structured bundles. They must not read
runtime artifacts, live report bodies, prompts, provider payloads, PDF/cache/
source bodies or memory files.

## 6. Expected Behavior After Implementation

- Chapter 3 no-live `ValueError` reproduces the accepted live failure metadata
  shape without provider/network/source access.
- Agent classification remains `blocked_internal_code_bug` / `code_bug`.
- Service classification remains `llm_exception` / `code_bug`.
- `provider_attempt_count` remains `0`; no provider availability claim is made.
- Pre-provider code-bug runtime diagnostics carry `max_output_chars=12000` when
  policy carries that cap.
- `serialize_chapter_runtime_diagnostics()` reports terminal diagnostic present
  and consistent for pre-provider `llm_exception` / `code_bug`.
- Incomplete-run artifact summary retains the safe scalar lineage under
  `runtime_diagnostics` while excluding prompt, draft, raw provider response,
  model name, message body, headers and secrets.
- EID single-source/no-fallback and `NOT_READY` remain unchanged.

## 7. Future Validation Matrix

The future implementation gate should run only no-live/local commands:

```text
uv run pytest tests/agent/test_runner.py::test_chapter_3_value_error_is_internal_code_bug_without_provider_runtime -q
```

Expected: `1 passed`.

```text
uv run pytest tests/services/test_fund_analysis_service_llm.py::test_analyze_with_llm_execution_projects_chapter_3_value_error_as_code_bug_safe_diagnostic -q
```

Expected: `1 passed`.

```text
uv run pytest tests/services/test_chapter_orchestrator.py::test_chapter_3_pre_provider_value_error_serializes_safe_runtime_cap -q
```

Expected: `1 passed`.

```text
uv run pytest tests/services/test_llm_run_artifacts.py::test_artifact_records_chapter_3_pre_provider_code_bug_runtime_lineage -q
```

Expected: `1 passed`.

```text
uv run pytest tests/services/test_fund_analysis_service_llm.py tests/services/test_chapter_orchestrator.py tests/services/test_llm_run_artifacts.py tests/agent/test_runner.py -q
```

Expected: focused suite passes.

```text
uv run ruff check fund_agent/services/fund_analysis_service.py fund_agent/services/chapter_orchestrator.py fund_agent/services/llm_run_artifacts.py fund_agent/services/agent_bridge.py fund_agent/agent/runner.py fund_agent/fund/chapter_writer.py tests/services/test_fund_analysis_service_llm.py tests/services/test_chapter_orchestrator.py tests/services/test_llm_run_artifacts.py tests/agent/test_runner.py
```

Expected: `All checks passed!`

Forbidden validation in the implementation gate unless controller separately
authorizes it:

- live/provider/LLM/network/PDF/FDR/source/cache/helper commands;
- `fund-analysis analyze`, `fund-analysis checklist`,
  `fund-analysis analyze-annual-period`;
- readiness/release/PR/push/merge commands;
- memory probing.

## 8. Stop Conditions And Forbidden Changes

Implementation must stop and report to controller if:

- reproducing the failure requires real provider calls, network, credentials,
  prompt/provider payloads or raw responses;
- reproducing exact `004393 / 2025` requires reading PDF/cache/source bodies or
  invoking `FundDocumentRepository`;
- diagnostics require raw exception messages, prompt text, draft text,
  provider response bodies, model names, headers, API keys or secrets;
- a proposed fix would classify internal code bugs as provider runtime
  availability;
- a proposed fix changes provider config/default/model/base URL or timeout
  budgets;
- a proposed fix changes EID source policy, fallback behavior or source
  acquisition;
- a proposed fix requires passing explicit values through `extra_payload`;
- tests require broad public schema changes to top-level artifact summary fields;
- any implementation worker believes release/readiness can be marked ready.

Forbidden changes:

- Source policy, source acquisition, fallback and repository behavior.
- Provider construction/config/env/default/model/base URL changes.
- Deterministic renderer fallback or fail-open behavior.
- README, design truth, control truth and release/readiness docs.
- Cleanup, ignore rules, artifact deletion/move/archive.
- Stage, commit, push, PR, merge or mark-ready.

## 9. Residual Risks And Deferred Items

| Residual / risk | Disposition |
|---|---|
| Exact live source identity `004393 / 2025` is not replayed. | Accepted planning constraint: this gate is no-live and cannot read source bodies. The implementation reproduces exact safe-metadata failure shape only. |
| Underlying live Chapter 3 `ValueError` root code path may differ from fake no-live `ValueError`. | Deferred to later controller-authorized no-live or live diagnostic gate after this reproducer/diagnostic fixture is accepted. |
| LLM content quality remains unproven. | Deferred; not part of this diagnostic implementation. |
| Provider readiness and 401/403 provider-response classification remain unproven. | Deferred; no provider commands in this work unit. |
| Release/readiness remains `NOT_READY`. | Preserved; this plan cannot close release/readiness. |
| Artifact schema breadth beyond `runtime_diagnostics` remains undecided. | Do not broaden in this implementation. If needed, route to a separate artifact schema gate. |

## 10. Docs Decision

No README, `docs/design.md`, `docs/implementation-control.md` or source-truth
sync is required for this implementation because the planned change is a narrow
diagnostic/test fixture update and does not change public source policy,
provider configuration, user CLI behavior, template semantics, source truth or
release/readiness state.

The future implementation gate must write only its assigned implementation
artifact under `docs/reviews/` if controller requests one.

## 11. Review Gates

Required before implementation:

1. Plan review by at least two independent reviewers or controller-recorded
   reviewer unavailability.
2. Controller judgment accepting or amending this plan.

Required after implementation:

1. Implementation artifact documenting changed files, exact assertions,
   validation output, docs decision and residual risks.
2. Code review focused on:
   - no-live boundary;
   - source policy and fallback preservation;
   - typed explicit parameter propagation, no `extra_payload`;
   - safe scalar diagnostic allowlist;
   - code_bug not converted into provider availability;
   - artifact redaction and no raw body leakage;
   - test specificity and failure-shape coverage.
3. Re-review for any accepted findings.
4. Controller judgment before any accepted local commit.

Review must reject any implementation that:

- adds source/provider/live access;
- weakens fail-closed semantics;
- broadens provider behavior;
- changes source truth;
- exposes raw bodies or secrets;
- claims readiness.

## 12. Final Next Entry Recommendation

Recommended next entry:

`Provider/LLM Chapter 3 Test-reproducer / Diagnostic Implementation Plan Review Gate`

After plan review and controller acceptance, assign Slice S1-S3 to an
implementation worker as one narrow no-live implementation pass only if the
controller agrees the slice set is small enough. Otherwise split into:

1. S1 reproducer tests;
2. S2 diagnostic propagation;
3. S3 artifact fixture.

The next implementation handoff must preserve:

- EID single-source only;
- `fallback_enabled=false`;
- Eastmoney, fund-company/CDN, CNINFO and fallback not authorized;
- no memory probing;
- no live/provider/source/readiness/release/PR commands;
- release/readiness `NOT_READY`.
