# Provider/LLM Chapter 3 Code-bug Root-cause Plan

Date: 2026-06-13

Gate: `Provider/LLM Chapter 3 Code-bug Root-cause Planning Gate`

Status: `PLAN_READY_FOR_REVIEW_NOT_READY`

Release/readiness: `NOT_READY`

## Scope

This is a no-live root-cause planning gate after accepted controlled live
Provider/LLM evidence checkpoint `6cc89a5`.

The plan defines the next evidence path to determine why the accepted exact
Route C `004393 / 2025 --use-llm` live run failed closed on Chapter 3 before
provider attempt metadata was available, and whether a later narrow code/test
fix may be needed.

This planning gate does not execute provider/LLM/live/network/PDF/FDR/source/
analyze/checklist/readiness/release/PR commands. It does not modify source,
tests, runtime behavior, source policy, golden-answer content, fixtures,
manifest, README/design truth, cleanup state, PR state or external state.

EID single-source/no fallback remains preserved. Release/readiness remains
`NOT_READY`.

## Inputs

Truth/control inputs:

| Input | Role |
|---|---|
| `AGENTS.md` | Rule truth, four-layer boundary, no direct source/PDF/cache access, no hidden `extra_payload`. |
| `docs/design.md` | Design truth for Route C, typed template path, Host/Agent/Fund boundaries and EID single-source policy. |
| `docs/current-startup-packet.md` | Current active gate and checkpoint `6cc89a5`. |
| `docs/implementation-control.md` | Control truth for accepted checkpoint, residuals and next entry. |
| `docs/reviews/mvp-controlled-live-provider-llm-evidence-execution-20260613.md` | Accepted safe execution metadata and residual facts. |
| `docs/reviews/mvp-controlled-live-provider-llm-evidence-execution-controller-judgment-20260613.md` | Controller disposition and required next no-live planning route. |

Relevant read-only source/test scope for the next evidence gate:

| Path | Evidence purpose |
|---|---|
| `fund_agent/services/fund_analysis_service.py` | Service hosted Route C request/runtime assembly and `max_output_chars` propagation. |
| `fund_agent/services/chapter_orchestrator.py` | Stop reason, runtime diagnostic, first-failed summary and diagnostic consistency semantics. |
| `fund_agent/services/llm_run_artifacts.py` | Manifest/summary extraction and safe artifact serialization. |
| `fund_agent/services/agent_bridge.py` | Agent task to Service `ChapterRunResult` projection, `llm_exception` mapping and runtime diagnostics bridge. |
| `fund_agent/agent/runner.py` | Chapter execution loop, writer input construction, typed evidence availability, exception-to-code-bug behavior. |
| `fund_agent/fund/chapter_writer.py` | Chapter 3 writer input, typed required-output evidence plan and pre-provider `ValueError` risks. |
| `tests/services/test_fund_analysis_service_llm.py` | Existing runtime plan and `max_output_chars` propagation tests. |
| `tests/services/test_chapter_orchestrator.py` | Existing fail-closed, typed path, prompt-contract and runtime diagnostic tests. |
| `tests/services/test_llm_run_artifacts.py` | Existing artifact summary/runtime lineage tests. |
| `tests/agent/test_runner.py` | Existing Agent runner code-bug and typed availability tests. |

## Accepted Facts From Prior Gate

| Fact | Current disposition |
|---|---|
| Exact Route C `--use-llm` command for `004393 / 2025` ran once after explicit authorization. | ACCEPTED bounded live fact. |
| Command failed closed with `exit_code=1`, empty stdout and incomplete final assembly. | ACCEPTED bounded live fact. |
| Chapters 1, 2, 4, 5 and 6 reached accepted status in safe metadata. | ACCEPTED_WITH_SCOPE_LIMIT; not content-quality acceptance. |
| Chapter 3 failed with `llm_exception` / `code_bug` / `ValueError`. | ACCEPTED residual. |
| First-failed provider attempt count was `0`. | ACCEPTED safe metadata fact. |
| Exact command set `FUND_AGENT_LLM_MAX_OUTPUT_CHARS=12000`. | ACCEPT_COMMAND_FACT. |
| Runtime metadata proves `max_output_chars=12000`. | REJECTED; safe metadata recorded `max_output_chars=null`. |
| Provider readiness, LLM content quality, release/readiness and 401/403 classification. | REJECTED or deferred. |
| Safe metadata did not show annual-report source fallback or Eastmoney/CNINFO/fund-company expansion. | ACCEPTED_WITH_SCOPE_LIMIT; not broad source-policy proof. |

## Non-goals

- Do not repeat live provider/LLM execution.
- Do not invoke provider/LLM/network/PDF/FDR/source/analyze/checklist/readiness/release/PR commands.
- Do not read raw chapter writer/auditor Markdown, raw prompt payloads, raw provider payloads, raw provider responses, final report bodies, PDF/cache/source bodies, credentials, headers or tokens.
- Do not treat `reports/llm-runs/` residue as source truth, content truth, release evidence or readiness proof beyond accepted safe metadata in reviewed artifacts.
- Do not change source acquisition policy.
- Do not introduce Eastmoney, CNINFO, fund-company fallback or any annual-report fallback path.
- Do not implement a fix in this planning gate.
- Do not claim provider readiness, LLM content quality, release readiness, PR readiness or repeat-live authorization.

## Root-cause Hypotheses

### H1 - Chapter 3 Prompt/Input Construction Bug Before Provider Call

Hypothesis:

Chapter 3 failed while constructing writer input or prompt before the provider
client was called. The live evidence supports this as plausible because Chapter
3 had `provider_attempt_count=0`, `terminal_issue_class=ValueError`,
`stop_reason=llm_exception` and `failure_category=code_bug`.

Direct evidence to collect in next no-live evidence gate:

| Evidence | Exact files/functions/tests | Accept signal | Reject signal |
|---|---|---|---|
| Static path from Service policy to Agent writer input preserves `max_output_chars=12000` and `typed_template_path=typed_template_contract`. | `fund_agent/services/fund_analysis_service.py::build_fund_llm_execution_request`, `fund_agent/services/agent_bridge.py::_agent_policy_from_service`, `fund_agent/agent/runner.py::_writer_input` | Fields are explicitly passed without `extra_payload`; no fallback/default overwrite. | Missing or mutated field before writer input. |
| Chapter 3 typed writer input can be built under fake/no-live projection without provider call. | Existing tests only: inspect `tests/services/test_chapter_orchestrator.py::test_typed_contract_path_preserves_independent_body_execution` and any existing Chapter 3 fake-writer coverage; run existing focused test files only. | Existing tests/static facts show fake writer receives Chapter 3 request; no `ValueError` before fake provider call. | Existing tests do not cover Chapter 3 pre-provider construction, or static read finds a plausible untested `ValueError` path. |
| Unknown pre-provider exception is classified as code bug without leaking sensitive text. | Existing `tests/agent/test_runner.py::test_unknown_exception_is_code_bug_not_provider_runtime`; existing `tests/services/test_chapter_orchestrator.py::test_unexpected_exception_records_code_bug_diagnostic_without_secret`. | Code-bug mapping is expected only for deterministic pre-provider exception. | Provider/runtime exception is incorrectly collapsed into code bug, or sensitive text leaks. |

Expected root-cause classification:

- If Chapter 3 fake writer request construction raises `ValueError`, classify as
  `CH3_PRE_PROVIDER_INPUT_CONSTRUCTION_BUG`.
- If fake writer is called successfully, H1 is rejected or deferred behind H2-H5.

### H2 - Chapter 3 Template/Evidence Projection Requirement Bug

Hypothesis:

Typed required-output or `EvidenceAvailability` for Chapter 3 contains a
requirement mismatch that raises before provider call, for example
`typed required output item 不属于当前章节` or
`typed required output 缺少 EvidenceAvailability requirement`.

Direct evidence to collect in next no-live evidence gate:

| Evidence | Exact files/functions/tests | Accept signal | Reject signal |
|---|---|---|---|
| Chapter 3 typed required-output item IDs all match `ch3.required_output.*`. | `fund_agent/agent/runner.py::_typed_required_output_items`; `fund_agent/fund/chapter_writer.py::_required_output_evidence_plan`, `_required_output_plan_item`, `_availability_for_required_output`; existing `tests/services/test_chapter_orchestrator.py::test_typed_contract_path_preserves_independent_body_execution` | All Chapter 3 items have matching IDs and required availability rows. | Any Chapter 3 typed required-output item points to another chapter or lacks required availability. |
| Same-source availability is derived once and passed to Agent runner for typed path. | `fund_agent/services/agent_bridge.py::_service_evidence_availability`; `fund_agent/agent/runner.py::_run_evidence_availability`; existing typed-path tests. | `EvidenceAvailability` type is accepted; Chapter 3 `ch3.required_output.item_03` is present with safe status such as `unreviewed`. | Bridge passes wrong type/None for typed path or availability cannot satisfy Chapter 3 item. |
| Chapter 3 prompt contract can include required-output evidence plan without reading raw prompt. | Existing typed-path test checks `rows[3].attempts[0].writer_result.prompt.required_output_evidence_plan`; static read may inspect existing safe scalar assertions only. | Existing safe scalars show Chapter 3 plan actions and IDs are coherent. | Existing tests lack the needed scalar coverage, or static read shows prompt construction could throw due projection/requirement mismatch. |

Expected root-cause classification:

- If typed item/availability mismatch is found, classify as
  `CH3_TYPED_REQUIREMENT_PROJECTION_BUG`.
- If all Chapter 3 typed requirements and availability rows are coherent and
  fake writer receives a request, reject H2.

### H3 - Service/Agent Bridge Error Mapping Bug

Hypothesis:

The actual failure may not be provider-related, but the Service/Agent bridge
maps deterministic exceptions to `llm_exception`, making the accepted live
metadata look like an LLM failure.

Direct evidence to collect in next no-live evidence gate:

| Evidence | Exact files/functions/tests | Accept signal | Reject signal |
|---|---|---|---|
| Agent runner distinguishes provider runtime exceptions from internal code bugs. | `fund_agent/agent/runner.py::_exception_task`, `_terminal_from_exception`, `_failure_category_from_exception`; `tests/agent/test_runner.py::test_provider_timeout_is_provider_runtime_and_does_not_content_retry`, `test_unknown_exception_is_code_bug_not_provider_runtime` | Provider timeout maps to provider runtime; unknown exception maps to code bug. | Unknown exceptions are mislabeled as provider runtime or provider exceptions as code bug. |
| Bridge maps `blocked_internal_code_bug` to Service `llm_exception` and `code_bug`. | Static read of `fund_agent/services/agent_bridge.py::_stop_reason_from_task`, `_failure_category_from_task`, `_runtime_diagnostics_from_task`; run existing bridge/runner tests only. | Mapping matches accepted live metadata and is documented as fail-closed generic stop reason. | Mapping hides the deterministic exception class so root-cause evidence cannot distinguish pre-provider bug, or existing tests do not cover this bridge path. |
| Service-level first-failed metadata preserves `terminal_issue_class=ValueError`. | `fund_agent/services/chapter_orchestrator.py::_first_failed_runtime_diagnostic`, `_terminal_issue_class`; artifact summary tests. | Safe metadata keeps `ValueError` class without message/body. | Metadata loses exception class or falsely claims provider category. |

Expected root-cause classification:

- If mapping is accurate but too generic, classify as
  `MAPPING_EXPECTED_BUT_NEEDS_DIAGNOSTIC_CLARITY`.
- If mapping incorrectly labels deterministic exception as provider/LLM runtime
  in downstream artifacts, classify as `SERVICE_AGENT_MAPPING_BUG`.

### H4 - Diagnostic Propagation Gap Causing `max_output_chars=null`

Hypothesis:

`max_output_chars=null` is expected when failure occurs before a provider
diagnostic and before a terminal runtime diagnostic matching `llm_exception` is
selected; alternatively, it indicates a diagnostic propagation defect because
Chapter 3 writer input already had the value but exception diagnostics did not
carry it.

Direct evidence to collect in next no-live evidence gate:

| Evidence | Exact files/functions/tests | Accept signal | Reject signal |
|---|---|---|---|
| Existing serialization drops representative diagnostics for `llm_exception` when no provider category exists. | `fund_agent/services/chapter_orchestrator.py::_RUNTIME_TERMINAL_STOP_REASONS`, `_terminal_runtime_diagnostic`, `_representative_runtime_diagnostics`, `_first_failed_runtime_diagnostic` | `llm_exception` with code-bug diagnostic yields `missing_terminal_runtime_diagnostic` and `max_output_chars=null` by current design. | There is a diagnostic with `max_output_chars=12000` that serializer should have selected but did not. |
| Provider diagnostics include `max_output_chars` when provider attempt exists. | Existing `tests/services/test_chapter_orchestrator.py::test_runtime_diagnostic_serialization_exposes_only_safe_scalars` and provider timeout lineage tests. | Provider-attempt diagnostics surface `max_output_chars=12000`. | Provider diagnostics also lose output cap unexpectedly. |
| Pre-provider writer input construction has `max_output_chars=12000`. | Existing `tests/services/test_fund_analysis_service_llm.py` runtime plan assertions and static read of Service -> bridge -> Agent writer input propagation only. | Existing runtime plan/static facts show the value reaches writer input/request boundary. | Existing evidence only proves runtime plan, not Chapter 3 writer input/request; record missing reproducer as residual. |

Expected root-cause classification:

- If value exists in runtime plan/request but absent in exception summary,
  classify as `DIAGNOSTIC_PROPAGATION_GAP_PRE_PROVIDER`.
- If value is absent before writer input, classify under H1.
- If current behavior is intended for pre-provider code-bug, record as
  `EXPECTED_NULL_FOR_PRE_PROVIDER_CODE_BUG` with no code fix unless reviewers
  require stronger diagnostics.

### H5 - Artifact Writer/Summary Extraction Mismatch After Pre-provider Failure

Hypothesis:

The artifact writer may have correctly received safe runtime diagnostics, but
manifest/summary extraction chose a first-failed representation that lost
available safe scalar metadata after a pre-provider failure.

Direct evidence to collect in next no-live evidence gate:

| Evidence | Exact files/functions/tests | Accept signal | Reject signal |
|---|---|---|---|
| Summary uses `serialize_chapter_runtime_diagnostics()` output and does not read raw bodies. | `fund_agent/services/llm_run_artifacts.py::_build_summary_payload`, `_runtime_diagnostic_payload`; existing redaction tests. | Summary is allowlist-only and body-safe. | Summary depends on raw chapter JSON/Markdown or prompt/provider body. |
| Artifact writer preserves runtime lineage for provider timeout and handles missing terminal diagnostics. | Existing `tests/services/test_llm_run_artifacts.py::test_artifact_records_terminal_runtime_lineage_at_chapter_and_attempt_levels` and existing serializer tests only. | Existing tests show provider timeout lineage remains intact and missing terminal diagnostic handling is explainable. | Existing tests lack code-bug/pre-provider fixture coverage, or artifact summary diverges from serializer output. |
| Chapter 3 code-bug safe metadata in accepted evidence is explainable by summary extraction rules. | Compare reviewed execution artifact metadata to serializer test fixture; do not read runtime residue bodies. | Accepted fields align with serializer behavior. | Artifact fields cannot be derived from serializer behavior. |

Expected root-cause classification:

- If artifact writer is faithful to serializer output, reject H5 and route to H1-H4.
- If summary loses safe scalar diagnostics that serializer exposes, classify as
  `ARTIFACT_SUMMARY_EXTRACTION_BUG`.

## Next No-live Evidence Gate

Recommended next gate:

`Provider/LLM Chapter 3 Code-bug Root-cause Evidence Gate`

This next gate should collect only no-live, fake-client/mock-provider, static
and targeted-test evidence. It must not perform live/provider/network/PDF/FDR/
source/analyze/checklist/readiness/release/PR commands.

Allowed commands for the next evidence gate:

```bash
git status --branch --short
git status --short
git diff --name-only
git diff --check
rg -n "<safe-pattern>" AGENTS.md docs/design.md docs/current-startup-packet.md docs/implementation-control.md docs/reviews fund_agent tests
sed -n '<range>p' <allowed-text-file>
uv run pytest tests/services/test_fund_analysis_service_llm.py tests/services/test_chapter_orchestrator.py tests/services/test_llm_run_artifacts.py tests/agent/test_runner.py -q
uv run ruff check fund_agent/services/fund_analysis_service.py fund_agent/services/chapter_orchestrator.py fund_agent/services/llm_run_artifacts.py fund_agent/services/agent_bridge.py fund_agent/agent/runner.py fund_agent/fund/chapter_writer.py tests/services/test_fund_analysis_service_llm.py tests/services/test_chapter_orchestrator.py tests/services/test_llm_run_artifacts.py tests/agent/test_runner.py
```

The next evidence gate must not add or modify tests, fixtures, assertions or
source code. If existing tests/static inspection are insufficient to reproduce
or disprove a hypothesis, the evidence artifact must record that gap as a
residual and route it to a separate future no-live `Chapter 3 Test-reproducer /
Diagnostic Implementation Planning Gate` or implementation gate after
controller acceptance.

Forbidden in the next evidence gate:

- `fund-analysis analyze`
- `fund-analysis checklist`
- `fund-analysis analyze-annual-period`
- provider/LLM live calls
- network probes
- PDF/FDR/source/cache helper calls
- reading runtime artifact chapter Markdown, prompt/provider payloads, provider responses, final report bodies, PDF/cache/source bodies, credentials, headers or tokens
- readiness/release/PR/push/merge/mark-ready commands
- source/test/runtime behavior edits
- source acquisition policy change or fallback/Eastmoney/CNINFO/fund-company logic

Evidence artifact path for the next gate:

`docs/reviews/mvp-provider-llm-chapter-3-code-bug-root-cause-evidence-20260613.md`

Expected evidence fields:

| Field | Required |
|---|---|
| Gate name and no-live boundary | Yes |
| Prior checkpoint `6cc89a5` accepted facts | Yes |
| Commands actually run | Yes |
| H1-H5 disposition table | Yes |
| Exact source/test paths inspected | Yes |
| Targeted tests run and result | Yes |
| Whether Chapter 3 writer request construction reaches fake writer | Yes |
| Whether typed required-output and availability rows are coherent | Yes |
| Whether Service/Agent mapping is expected or faulty | Yes |
| Whether `max_output_chars=null` is expected or diagnostic gap | Yes |
| Whether artifact summary is faithful or mismatched | Yes |
| Explicit `NOT_READY` preservation | Yes |
| Explicit source policy preservation | Yes |
| Missing reproducer/test/assertion/fixture residuals, if any | Yes |

## Evidence-gate Residual Routing

The next no-live evidence gate may only run existing tests and static/read-only
inspection. It must not create or edit tests, fixtures, assertions, source code
or runtime behavior.

If direct root-cause evidence requires a missing reproducer, new fake-client
test, new diagnostic assertion, or new code-bug/pre-provider fixture, the
evidence artifact must classify it as one of:

| Residual | Required routing |
|---|---|
| Missing Chapter 3 fake-writer reproducer | Future no-live `Chapter 3 Test-reproducer / Diagnostic Implementation Planning Gate`. |
| Missing bridge projection assertion | Future no-live diagnostic/test implementation planning gate. |
| Missing pre-provider `max_output_chars` assertion | Future no-live diagnostic/test implementation planning gate. |
| Missing artifact code-bug/pre-provider fixture | Future no-live artifact diagnostic/test implementation planning gate. |

These residuals do not authorize implementation, repeat live execution, source
policy changes, readiness/release claims or PR actions.

## Conditional Future Fix Slices

No implementation is authorized by this plan. A future test-reproducer,
diagnostic implementation or code-fix gate may be opened only after the no-live
evidence gate and controller accept a specific root cause or an evidence gap
that cannot be closed with existing tests/static inspection.

### Fix Slice A - Chapter 3 Input/Typed Requirement Fix

Condition:

- Evidence accepts `CH3_PRE_PROVIDER_INPUT_CONSTRUCTION_BUG` or
  `CH3_TYPED_REQUIREMENT_PROJECTION_BUG`.

Narrow file scope:

- `fund_agent/fund/chapter_writer.py`
- `fund_agent/agent/runner.py`
- `fund_agent/services/agent_bridge.py` only if bridge input type handling is the actual cause
- targeted tests in `tests/agent/test_runner.py` and/or `tests/services/test_chapter_orchestrator.py`

Stop conditions:

- Any change to provider config/default/model/base URL.
- Any live/provider/network/PDF/FDR/source access.
- Any source policy/fallback/Eastmoney/CNINFO/fund-company change.
- Any broad template rewrite or content-quality recalibration.
- Any readiness/release/PR claim.

### Fix Slice B - Service/Agent Diagnostic Mapping Fix

Condition:

- Evidence accepts `SERVICE_AGENT_MAPPING_BUG` or
  `MAPPING_EXPECTED_BUT_NEEDS_DIAGNOSTIC_CLARITY` and controller requires clearer safe diagnostics.

Narrow file scope:

- `fund_agent/services/agent_bridge.py`
- `fund_agent/services/chapter_orchestrator.py`
- targeted tests in `tests/services/test_chapter_orchestrator.py` and `tests/agent/test_runner.py`

Allowed goal:

- Preserve fail-closed status while exposing safe scalar distinction between
  provider runtime failure and deterministic pre-provider code bug.

Stop conditions:

- Retaining exception messages that may include prompt/key/header/provider body.
- Changing provider retry/timeout semantics.
- Reclassifying code bugs as provider availability.

### Fix Slice C - Pre-provider `max_output_chars` Diagnostic Propagation

Condition:

- Evidence accepts `DIAGNOSTIC_PROPAGATION_GAP_PRE_PROVIDER` and controller
  requires safe output-cap metadata on pre-provider code-bug diagnostics.

Narrow file scope:

- `fund_agent/services/chapter_orchestrator.py`
- `fund_agent/services/agent_bridge.py`
- `fund_agent/services/llm_run_artifacts.py` only if serializer/artifact summary must expose already-safe scalar fields
- targeted tests in `tests/services/test_chapter_orchestrator.py`,
  `tests/services/test_llm_run_artifacts.py`, and `tests/services/test_fund_analysis_service_llm.py`

Allowed goal:

- Add or preserve safe scalar metadata such as `max_output_chars`, without prompt
  text, draft text, raw provider body, model secret, credential or headers.

Stop conditions:

- Reading or storing raw prompt/provider/auditor/final report bodies.
- Using reports residue as source truth.
- Changing runtime budget, retry or live execution behavior.

### Fix Slice D - Artifact Summary Extraction Fix

Condition:

- Evidence accepts `ARTIFACT_SUMMARY_EXTRACTION_BUG`.

Narrow file scope:

- `fund_agent/services/llm_run_artifacts.py`
- serializer tests in `tests/services/test_llm_run_artifacts.py`
- only if necessary, shared serializer behavior in `fund_agent/services/chapter_orchestrator.py`

Stop conditions:

- Expanding artifact retention beyond allowlisted safe metadata.
- Retaining accepted final report body, raw prompt, raw provider response, raw
  auditor response, raw PDF/cache/source body or credentials.

## Review Plan

The next evidence artifact should receive at least two independent reviews
before controller judgment.

Reviewer focus:

| Reviewer focus | Required checks |
|---|---|
| Boundary | No live/provider/network/PDF/FDR/source/analyze/checklist/readiness/release/PR command. |
| Hypothesis discipline | H1-H5 each has direct evidence and accept/reject signal. |
| No raw body read | No raw prompt/provider/chapter Markdown/final report/PDF/cache/source/credential content used. |
| Source policy | EID single-source/no fallback preserved; no Eastmoney/CNINFO/fund-company path. |
| Diagnostics | `ValueError`, `provider_attempt_count=0`, `max_output_chars=null` explained from code/test facts. |
| Implementation routing | Any fix is conditional and narrow; no implementation is claimed in evidence gate. |
| Readiness posture | Provider readiness, LLM content quality, repeat live, release/readiness and PR claims rejected. |

## Acceptance Criteria

Plan acceptance requires:

- The next entry is a no-live evidence gate, not implementation.
- H1-H5 are all represented with direct evidence, exact files/functions/tests
  and accept/reject signals.
- The next evidence gate is limited to existing tests and static/read-only
  inspection.
- The plan preserves `NOT_READY`.
- The plan preserves EID single-source/no fallback.
- The plan forbids repeat live/provider/LLM/network/PDF/FDR/source/analyze/checklist/readiness/release/PR commands.
- The plan forbids raw chapter Markdown, prompt/provider payloads, provider responses, final report bodies, PDF/cache/source bodies and credentials.
- The plan defines conditional future fix slices with narrow file/test scopes and stop conditions.
- Missing reproducers, assertions or fixtures are routed as residuals to a
  future no-live test-reproducer / diagnostic implementation planning gate.
- The plan rejects provider readiness, LLM content quality, repeat live, PR/release and readiness claims.

Reject or amend the plan if:

- It asks for immediate implementation before no-live root-cause evidence.
- It allows adding or modifying tests, fixtures, assertions, source code or
  runtime behavior in the evidence gate.
- It relies on `reports/llm-runs/` residue beyond accepted safe metadata in reviewed artifacts.
- It requires raw body/prompt/provider/PDF/cache/credential reads.
- It authorizes source policy changes or fallback.
- It treats one fail-closed live run as provider readiness or LLM content quality.

## Next Entry

Unique next entry:

`Provider/LLM Chapter 3 Code-bug Root-cause Evidence Gate`

The next gate must remain no-live and must collect direct root-cause evidence
from existing tests/static inspection before any test-reproducer,
implementation gate or repeat live provider/LLM execution is considered.
