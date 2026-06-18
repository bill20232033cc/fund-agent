# Provider/LLM Chapter 3 Post-fix Provider-before ValueError No-live Root-cause Scout - procodex - 2026-06-14

## 1. Scope

Gate: `Provider/LLM Chapter 3 Post-fix Bounded Live Re-evidence Gate`.

Role: role-scoped evidence worker / scout only. This artifact independently verifies the post-fix bounded live result from safe metadata and proposes the exact next no-live root-cause evidence target for the remaining Chapter 3 provider-before `ValueError`.

Boundaries preserved:

- No code fix implemented.
- No source policy change; EID remains single-source/no-fallback.
- No live/provider/LLM/network/PDF/FDR/source/analyze/checklist/readiness/release/PR command was run.
- No writer markdown, auditor feedback markdown, raw prompt, provider payload, source/cache/PDF body was used as evidence.
- `release/readiness` remains `NOT_READY`.

Worker self-check: pass for artifact write scope. Existing worktree had unrelated modified/untracked files before this artifact; this worker only adds this artifact.

## 2. Evidence reviewed

Truth/control:

- `AGENTS.md`
- `docs/current-startup-packet.md`, especially current gate, `NOT_READY`, EID single-source/no-fallback and post-fix live retry boundaries.
- `docs/implementation-control.md`, especially current status that the Fund-writer missing-availability patch is accepted as `ACCEPT_IMPLEMENTATION_NOT_READY`.

Safe bounded-live evidence:

- `docs/reviews/provider-llm-chapter3-post-fix-bounded-live-re-evidence-20260614.md`
- `reports/llm-runs/004393-2025-20260613T182423Z-host_run_c1b20382568e4ae/summary.json`, allowlisted structured fields only.
- `reports/llm-runs/004393-2025-20260613T182423Z-host_run_c1b20382568e4ae/chapters/chapter-03.json`, allowlisted structured diagnostic fields only.

Allowed code/test paths read for direct no-live target selection:

- `fund_agent/fund/chapter_writer.py`
- `fund_agent/agent/runner.py`
- `tests/agent/test_runner.py`
- `tests/services/test_chapter_orchestrator.py`

Execution residual for controller awareness: during scout, one exploratory read touched `fund_agent/fund/evidence_availability.py` and a small template snippet while narrowing terms. This artifact does not use those snippets as controlling evidence; the next gate should explicitly authorize any deeper read of `evidence_availability.py` or typed template truth if the controller classifies that as necessary.

## 3. Verified live facts

The post-fix bounded live artifact records the exact command as a single `004393 / 2025` Route C live run and states that it did not change source policy, provider defaults, repair budget, annual-period LLM route, Docling scope, readiness, release or PR state.

Safe metadata independently matches that summary:

- `fund_code=004393`, `report_year=2025`, `run_id=host_run_c1b20382568e4ae0`.
- `orchestration_status=partial`.
- `final_assembly_status=incomplete`.
- `first_failed.chapter_id=3`.
- `first_failed.status=failed`.
- `first_failed.stop_reason=llm_exception`.
- `first_failed.failure_category=code_bug`.
- Chapter 3 metadata: `status=failed`, `accepted=false`, `stop_reason=llm_exception`, `failure_category=code_bug`, `terminal_issue_class=ValueError`, `terminal_runtime_operation=writer`, `terminal_runtime_diagnostic_present=true`, `diagnostic_consistency_status=consistent`.
- Chapter 3 metadata has `attempts_count=0`, `accepted_conclusion_present=false`, `accepted_draft_file=null`.
- Runtime diagnostic for Chapter 3 has `error_type=ValueError`, `operation=writer`, `repair_attempt_index=0`, `max_output_chars=12000`, and provider fields all null.
- Summary-level first-failed runtime diagnostic records `provider_attempt_count=0`, `provider_runtime_categories=[]`, `max_output_chars=12000`.
- Chapters 1, 2, 4, 5 and 6 are accepted in the chapter matrix; Chapter 3 blocks final assembly.

Verified interpretation:

- The prior `max_output_chars=null` metadata residual is closed for this run.
- The remaining failure is still provider-before; it is not provider availability, provider response classification or LLM content-quality evidence.
- The metadata is insufficient to prove the exact source line of the `ValueError`; it proves the failure class and call phase only.

## 4. Remaining root-cause hypotheses ranked by direct code path

### H1 - Highest - Real Chapter 3 typed required-output plan still raises inside Fund writer prompt/preflight path

Direct path:

- `write_chapter()` builds the prompt before returning preflight `blocked` results: `fund_agent/fund/chapter_writer.py:759-762`.
- Prompt construction calls `_required_output_evidence_plan()`, which raises when the typed path has no `EvidenceAvailability`: `fund_agent/fund/chapter_writer.py:905-928`.
- `_required_output_plan_item()` and `_required_output_action()` can also raise for mismatched chapter item ids, missing behavior, or invalid delete semantics: `fund_agent/fund/chapter_writer.py:950-1024`.
- `_required_output_preflight_issues()` only converts `action="block"` plans into `missing_required_facts`; it does not catch `ValueError`: `fund_agent/fund/chapter_writer.py:1090-1113`.

Why ranked first:

- The accepted patch covered "provided availability object but missing mapped requirement with declared `when_evidence_missing`" and converted it to writer-preflight `fact_gap`.
- The live result still reports writer-phase `ValueError`, so the remaining path is likely a different typed plan construction error than the patched missing-mapping branch.
- Current tests prove selected abstract branches, but not a live-like real Chapter 3 projection / real typed contract / real availability combination for `004393 / 2025`.

What would falsify it:

- A no-live reproducer using real typed Chapter 3 required-output items and a live-like Chapter 3 projection reaches `missing_required_facts` / `fact_gap` with zero provider calls instead of `ValueError`.

### H2 - High - Writer input construction raises before `write_chapter_tool`

Direct path:

- Runner builds writer input before scheduling the writer tool and maps any exception to `_exception_task(... traces=())`: `fund_agent/agent/runner.py:309-324`.
- `_writer_input()` injects `_typed_required_output_items()` and typed `evidence_availability` into `build_chapter_writer_input()`: `fund_agent/agent/runner.py:595-629`.
- `_typed_required_output_items()` reads the typed chapter contract for typed path: `fund_agent/agent/runner.py:1107-1128`.

Why ranked second:

- The observed `attempts_count=0` is consistent with a pre-writer-tool exception.
- However, `attempts_count=0` is not decisive, because `_exception_task()` also suppresses a single `fund.write_chapter` trace from attempts: `fund_agent/agent/runner.py:935-962`.

What would falsify it:

- A no-live reproducer that instruments only test assertions, not production code, shows `_writer_input()` succeeds and the exception is raised later by `write_chapter()`.

### H3 - Medium - Existing no-live tests cover adjacent branches but miss the live-like combination

Direct test evidence:

- `tests/agent/test_runner.py:204-250` simulates `_typed_required_output_items()` raising `ValueError` before writer tool and verifies `writer.requests == []`, `llm_exception`, `code_bug`, and empty attempts.
- `tests/agent/test_runner.py:253-298` verifies an empty availability mapping can now become `missing_required_facts` / `fact_gap` with zero provider calls.
- `tests/agent/test_runner.py:301-318` verifies a completely missing `EvidenceAvailability` envelope remains `ValueError` with no provider request.
- `tests/services/test_chapter_orchestrator.py:1649-1705` verifies Service serialization of the pre-writer `ValueError` shape, including `provider_attempt_count=0` and `max_output_chars=12000`.

Why ranked third:

- These tests prove the intended abstract behavior, but they do not identify which real `004393 / 2025` typed item/status combination is still falling into `ValueError`.

### H4 - Lower - Service/Agent mapping misclassifies a writer `fact_gap` as `code_bug`

Direct path:

- Runner maps writer `missing_required_facts`, `evidence_anchor_missing` and `item_rule_deleted_required_content` to `blocked_fact_gap`: `fund_agent/agent/runner.py:1288-1322`.
- Existing regression asserts the missing-availability branch yields `terminal_state=blocked_fact_gap`, `stop_reason=missing_required_facts`, and `failure_category=fact_gap`: `tests/agent/test_runner.py:282-298`.

Why ranked lower:

- The direct mapping and regression make a pure Service/Agent reclassification bug less likely than a real unconverted `ValueError` before the writer returns a blocked result.

## 5. Exact next no-live reproducer target

Recommended next gate:

`Provider/LLM Chapter 3 Post-fix Provider-before ValueError No-live Root-cause Evidence Gate`

Primary no-live reproducer target:

- File: `tests/agent/test_runner.py`
- Test shape: add a red, no-live test that runs `run_agent_body_chapters()` for Chapter 3 with `AgentRunPolicy(target_chapter_ids=(3,), max_output_chars=12000, typed_template_path="typed_template_contract")`, fake writer/auditor clients, real typed required-output lookup, and a hand-built no-live Chapter 3 projection that mirrors the safe live failure surface without reading source/PDF/provider payloads.
- Required assertions for the red reproducer:
  - `writer.requests == []` if the current failure is still before provider request construction, or exact request count if the failure is inside `write_chapter()` before provider client call.
  - `task.chapter_id == 3`.
  - `task.status == "failed"`.
  - `task.stop_reason == "llm_exception"`.
  - `task.failure_category == "code_bug"`.
  - exception class or serialized diagnostic class is `ValueError`.
  - `max_output_chars == 12000` appears in safe runtime diagnostic serialization.
  - no provider runtime category is present.

Secondary serialization target, only after the agent-level reproducer is exact:

- File: `tests/services/test_chapter_orchestrator.py`
- Test shape: project the same reproducer through Service/orchestrator serialization and assert the summary-equivalent first-failed fields: `chapter_id=3`, `stop_reason=llm_exception`, `category=code_bug`, `provider_attempt_count=0`, `provider_runtime_categories=()`, `max_output_chars=12000`, `terminal_runtime_diagnostic_present=true`, and `error_type=ValueError`.

Decision rule for next gate:

- If the reproducer fails with current `ValueError`, the next implementation gate should patch the exact Fund writer typed required-output / availability conversion branch, not Service or runner masking.
- If the reproducer produces `missing_required_facts` / `fact_gap`, then current no-live unit coverage is already ahead of the live artifact and the next evidence gate must identify the missing live-like input shape at the Service-to-Agent projection boundary before any fix.
- If the reproducer cannot be built from the currently allowed files without reading the availability derivation or typed template truth, the controller should explicitly authorize `fund_agent/fund/evidence_availability.py` and the typed template truth file for read-only no-live root-cause evidence.

## 6. Non-goals and residuals

Non-goals:

- No code fix.
- No new live run.
- No provider, network, source, PDF, FDR, fallback, analyze/checklist, readiness, release, PR, stage, commit or push action.
- No source fallback; no Eastmoney, fund-company website, CNINFO or other source path.
- No annual-period LLM route, Docling/parser benchmark, repair-budget calibration or provider default change.
- No LLM content-quality judgment.

Residuals:

| Residual | Owner / next action |
|---|---|
| Exact `ValueError` source line remains unproven by safe metadata alone. | Next no-live root-cause evidence gate. |
| The current metadata cannot distinguish `_writer_input()` construction failure from `write_chapter()` prompt/preflight failure, because runner suppresses a single writer trace from attempts. | Next no-live reproducer must split these two paths. |
| Provider readiness and provider-response classification remain unproven because provider attempt count is still `0`. | Deferred until Chapter 3 reaches provider attempt `>0`. |
| LLM content quality remains unaccepted because Chapter 3 has no accepted draft/conclusion. | Future content-quality gate after complete accepted run. |
| Release/readiness remains `NOT_READY`. | Separate readiness/release gate only. |
| Scout process residual: one exploratory non-controlling read touched files outside the user-listed code-read set. | Controller should classify whether this is process-only or requires re-scout; no source/runtime behavior was changed. |

## 7. Verdict

VERDICT: READY_FOR_NO_LIVE_ROOT_CAUSE_EVIDENCE_GATE
