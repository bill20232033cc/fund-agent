# Provider/LLM Chapter 3 No-live Code-bug Root-cause/Fix Verification Evidence - ProcCodex - 2026-06-14

Status: `BLOCKED_NEEDS_CONTROLLER_DECISION`

Release/readiness: `NOT_READY`

## 1. Scope

This artifact covers the role-scoped no-live verification gate for the remaining
Chapter 3 Route C pre-provider `ValueError` / `code_bug` after the bounded live
retry accepted at
`docs/reviews/provider-llm-chapter3-bounded-live-re-evidence-retry-controller-judgment-20260614.md`.

In scope:

- Review accepted safe metadata/evidence for the bounded retry.
- Use no-live tests and scoped code inspection to classify the remaining root
  cause.
- Implement a narrow fix only if the required file is inside the allowed write
  set.

Out of scope and not performed:

- live/provider/network/analyze/checklist/readiness/release/PR commands;
- source/PDF/cache/FDR/FundDocumentRepository access;
- report body, raw prompt, provider payload, credential, raw report, raw
  PDF/cache/source body reads;
- source policy/fallback, annual-period LLM route, Docling, repair budget or
  provider default changes.

## 2. Evidence Reviewed

Truth/control:

- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- relevant Route C / Agent runner / provider LLM boundary excerpts from
  `docs/design.md`

Accepted retry/fix evidence:

- `docs/reviews/provider-llm-chapter3-bounded-live-re-evidence-retry-controller-judgment-20260614.md`
- `docs/reviews/provider-llm-chapter3-bounded-live-re-evidence-retry-execution-20260614.md`
- `docs/reviews/provider-llm-chapter3-provider-before-code-bug-no-live-fix-implementation-controller-judgment-20260614.md`

Scoped code/tests:

- `fund_agent/agent/runner.py`
- `fund_agent/services/chapter_orchestrator.py`
- `fund_agent/services/agent_bridge.py`
- `fund_agent/services/fund_analysis_service.py`
- `fund_agent/fund/chapter_writer.py` read only
- `tests/agent/test_runner.py`
- `tests/services/test_chapter_orchestrator.py`
- `tests/services/test_fund_analysis_service_llm.py`

Command evidence:

| Command | Result |
|---|---|
| `git status --short` | Dirty workspace existed before this worker: `AGENTS.md`, `README.md`, `docs/design.md`, many untracked artifacts/reports. No cleanup/stage/commit was performed. |
| `git diff --name-only` before artifact write | Existing tracked diff only: `AGENTS.md`, `README.md`, `docs/design.md`. |
| `uv run pytest tests/agent/test_runner.py::test_chapter_3_writer_input_value_error_is_internal_code_bug_before_writer_tool tests/services/test_chapter_orchestrator.py::test_typed_contract_path_preserves_independent_body_execution tests/services/test_fund_analysis_service_llm.py::test_analyze_with_llm_execution_projects_chapter_3_value_error_as_code_bug_safe_diagnostic -q` | `3 passed in 0.84s`. |
| temporary red reproducer: `uv run pytest tests/agent/test_runner.py::test_chapter_3_missing_typed_availability_should_fail_closed_as_fact_gap -q` | `1 failed in 0.82s`; current behavior was `task.status == "failed"` instead of expected writer-preflight fact-gap block. Temporary test was removed after capturing the red result. |
| `uv run pytest tests/agent/test_runner.py::test_chapter_3_writer_input_value_error_is_internal_code_bug_before_writer_tool tests/services/test_chapter_orchestrator.py::test_chapter_3_writer_input_value_error_serializes_safe_runtime_cap_before_writer_tool tests/services/test_fund_analysis_service_llm.py::test_analyze_with_llm_execution_projects_chapter_3_value_error_as_code_bug_safe_diagnostic -q` | `3 passed in 0.45s`. |

## 3. Root-cause Classification

Classification: H3 within this worker scope.

The remaining failure is consistent with H1 at the product/runtime level:
a pre-provider typed writer-input / typed contract mapping path can still turn a
Chapter 3 typed required-output availability gap into `ValueError`, producing
Chapter 3 `llm_exception` / `code_bug` before any provider attempt.

The narrow semantic fix is outside this worker's allowed write set. The
necessary change should be made in the Fund writer / typed availability boundary,
not in Service bridge or Agent runner:

- candidate file: `fund_agent/fund/chapter_writer.py`
- possible companion if controller authorizes broader evidence/fix:
  `fund_agent/fund/evidence_availability.py` or typed contract sidecar files
- reason: `ChapterWriterInput` prompt planning currently raises
  `ValueError` when typed required-output availability is missing for an item
  with `when_evidence_missing`. That error occurs before `write_chapter_tool`
  can return a typed `ChapterWriteResult` with a fail-closed writer-preflight
  issue.

H2 is rejected. The retry already has safe runtime metadata with
`terminal_runtime_diagnostic_present=true`, `diagnostic_consistency_status=consistent`,
`terminal_runtime_operation=writer`, `terminal_issue_class=ValueError`,
`provider_attempt_count=0`, and `max_output_chars=12000`. The remaining issue is
not only a diagnostic projection gap.

## 4. Red-test-first Evidence

A temporary red reproducer was inserted into the allowed test file
`tests/agent/test_runner.py` and then removed after failure capture.

The reproducer:

- monkeypatched `runner_module.derive_evidence_availability` to return an empty
  same-identity `EvidenceAvailability`;
- executed Chapter 3 only with `typed_template_path="typed_template_contract"`;
- used fake writer/auditor clients, so no provider/network call occurred;
- expected missing typed availability to become a writer-preflight fact-gap
  block with one writer attempt and zero provider calls.

Observed red result:

- command: `uv run pytest tests/agent/test_runner.py::test_chapter_3_missing_typed_availability_should_fail_closed_as_fact_gap -q`
- result: `1 failed in 0.82s`
- direct failure: `AssertionError: assert 'failed' == 'blocked'`
- important retained fact: `writer.requests == []` passed before the failed
  assertion, proving the failure remained pre-provider.

This red result proves the current typed-path behavior can still convert a
typed availability gap into a pre-provider internal `ValueError` / `code_bug`.
It does not prove provider readiness, content quality or release readiness.

## 5. Implementation Summary or No-code Decision

No production code change was made.

No test change was retained. The temporary red reproducer was removed after
capturing the failing result because the semantic fix requires editing outside
this worker's allowed write set.

Rejected in-scope workaround:

- Do not patch `fund_agent/agent/runner.py` to reclassify this as success or
  hide the exception. The runner's current safe diagnostic behavior is useful
  and already accepted; masking the typed mapping failure at the runner layer
  would weaken fail-closed evidence.
- Do not patch `fund_agent/services/agent_bridge.py` or
  `fund_agent/services/chapter_orchestrator.py` to fabricate availability
  requirements. Service/bridge should not invent Fund-domain evidence semantics
  or silently downgrade typed contract gaps.

Patch plan requiring controller decision:

1. Authorize `fund_agent/fund/chapter_writer.py` for edit.
2. Convert missing typed required-output availability for items with declared
   `when_evidence_missing` into a deterministic writer-preflight
   `ChapterWriteIssue` / `ChapterWriteResult(status="blocked")`, preserving
   safe diagnostics and zero provider attempts.
3. If investigation shows the mapping is incomplete rather than writer behavior
   too strict, authorize the exact availability/typed sidecar file and add the
   missing requirement mapping there.
4. Add a retained regression test in an allowed test file asserting Chapter 3
   missing typed availability does not surface as `code_bug` and does not call
   provider.

## 6. Validation Results

Accepted existing no-live matrix after temporary red test removal:

```text
uv run pytest tests/agent/test_runner.py::test_chapter_3_writer_input_value_error_is_internal_code_bug_before_writer_tool tests/services/test_chapter_orchestrator.py::test_chapter_3_writer_input_value_error_serializes_safe_runtime_cap_before_writer_tool tests/services/test_fund_analysis_service_llm.py::test_analyze_with_llm_execution_projects_chapter_3_value_error_as_code_bug_safe_diagnostic -q
...                                                                      [100%]
3 passed in 0.45s
```

No live/provider/network/analyze/checklist/readiness/release/PR command was run.
No `ruff` was run because no source/test change was retained.

## 7. Accepted / Rejected / Residual Claims

| Claim | Disposition | Reason |
|---|---|---|
| The bounded retry still failed before provider. | ACCEPT | Accepted retry evidence records Chapter 3 `ValueError` / `code_bug`, writer operation, provider attempt count `0`. |
| The previous diagnostic-only residual for `max_output_chars=null` remains open. | REJECT | Accepted retry evidence records `max_output_chars=12000`. |
| This gate proves provider readiness. | REJECT | No provider attempt occurred for the first failed chapter; this worker ran no live/provider command. |
| This gate accepts LLM content quality. | REJECT | No chapter/report body was read or accepted; final assembly remains incomplete. |
| EID source policy or fallback changed. | REJECT | No source/FDR/provider/live path was used; EID single-source/no-fallback remains unchanged. |
| A narrow fix can be safely made inside this worker's write set. | REJECT | The semantic fix belongs in Fund writer / typed availability mapping, outside the allowed write set. |
| Release/readiness can advance. | REJECT | `NOT_READY` is preserved. |

Residuals:

| Residual | Owner | Next handling |
|---|---|---|
| Chapter 3 typed required-output availability gap can still surface as pre-provider `ValueError` / `code_bug`. | Controller + Fund writer/typed availability owner | Authorize narrowed write set expansion or route a new patch gate. |
| Provider readiness and provider-response classification remain unproven. | Provider/runtime owner | No further live retry until no-live root cause is fixed or controller accepts a no-code disposition. |
| LLM content quality remains unaccepted. | Provider/runtime + chapter owners | Future content-quality gate only after complete accepted run exists. |
| Release/readiness remains `NOT_READY`. | Release owner/controller | Separate readiness/release gate only. |

## 8. Final Verdict

VERDICT: BLOCKED_NEEDS_CONTROLLER_DECISION
