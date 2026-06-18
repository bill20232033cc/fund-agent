# Provider/LLM Chapter 3 Code-bug Root-cause Evidence

Date: 2026-06-13

Gate: `Provider/LLM Chapter 3 Code-bug Root-cause Evidence Gate`

Role: AgentCodex / ProCodex no-live evidence worker only.

Status: `EVIDENCE_READY_FOR_REVIEW_NOT_READY`

Release/readiness: `NOT_READY`

## 1. No-live Boundary

This artifact collects no-live root-cause evidence for the accepted
`004393 / 2025 --use-llm` Chapter 3 failure from checkpoint `6cc89a5`.

The gate used only accepted reviewed metadata, existing tests and static
read-only inspection. It did not modify source code, tests, fixtures,
assertions, runtime behavior, source policy, README, design truth or control
docs. It did not run `fund-analysis analyze`, `fund-analysis checklist`,
`fund-analysis analyze-annual-period`, live provider/LLM/network/PDF/FDR/source
commands, readiness/release/PR commands, cleanup, stage, commit, push, merge or
archive operations.

Runtime artifact chapter Markdown, prompt/provider payloads, provider
responses, final report bodies, PDF/cache/source bodies, credentials, headers
and tokens were not read.

Operational annual-report source truth for this gate remains EID single-source
only: `selected_source=eid`, `source_mode=single_source_only`,
`fallback_enabled=false`. Eastmoney, fund-company/CDN, CNINFO and any
annual-report fallback are not current execution paths, not current source
truth and not authorized current sources. If those names appear in static code,
historical artifacts, older command output or old docs, this gate treats them
only as historical/residual/not-authorized-for-current-gate references. This
gate does not modify source acquisition policy and does not reintroduce
fallback. Accepted live/provider evidence must not be described as fallback
enabled or fallback used.

## 2. Prior Checkpoint Facts From `6cc89a5`

| Fact | Evidence disposition used here |
|---|---|
| Exact Route C `004393 / 2025 --use-llm` command was run once after authorization. | Accepted bounded live fact only. |
| Command failed closed with `exit_code=1`, empty stdout and incomplete final assembly. | Accepted bounded live fact. |
| Chapters 1, 2, 4, 5 and 6 reached accepted status in metadata. | Accepted with scope limit; not content-quality acceptance. |
| Chapter 3 failed with `llm_exception` / `code_bug` / `ValueError`. | Accepted residual for this root-cause evidence gate. |
| First-failed provider attempt count was `0`. | Accepted safe metadata fact. |
| Exact command set `FUND_AGENT_LLM_MAX_OUTPUT_CHARS=12000`. | Accepted command fact. |
| Runtime metadata proved `max_output_chars=12000`. | Rejected by controller; safe metadata recorded `max_output_chars=null`. |
| Runtime `max_output_chars=null`. | Accepted blocker residual; this gate explains whether expected or diagnostic gap. |
| Provider readiness, LLM content quality, 401/403 classification, PR and release/readiness. | Unproven; not accepted here. |
| EID single-source/no-fallback source policy. | Preserved; no source expansion or fallback authorized. |

## 3. Commands Run And Results

| Command | Result |
|---|---|
| `rg -n "Provider/LLM Chapter 3\|mvp-provider-llm-chapter-3\|controlled-live-provider-llm\|6cc89a5\|Chapter 3\|Chapter 3 Code-bug\|NOT_READY\|EID\|fallback\|artifact summary\|max_output_chars\|fake writer\|required-output\|availability\|Service/Agent\|mapping" /Users/maomao/.codex/memories/MEMORY.md` | `DEVIATION_NOT_EVIDENCE`: actual command occurred, but it was unauthorized by the handoff allowed-command list and is not valid gate evidence. No source truth or root-cause conclusion is derived from this output. |
| `git status --branch --short` | Completed. Branch `feat/mvp-llm-incomplete-run-artifacts...origin/feat/mvp-llm-incomplete-run-artifacts [ahead 61]`; many pre-existing untracked residues visible. |
| `git status --short` | Completed. Same untracked residue family visible; not treated as proof. |
| `git diff --name-only` | Completed. No output before artifact write. |
| `git diff --check` | Completed. No output before artifact write. |
| `rg -n "^(#\|##\|###)\|6cc89a5\|Provider/LLM\|Chapter 3\|NOT_READY\|EID\|fallback\|artifact\|H1\|H2\|H3\|H4\|H5\|max_output_chars\|required-output\|availability\|Service\|Agent\|mapping\|fake writer" AGENTS.md docs/design.md docs/current-startup-packet.md docs/implementation-control.md docs/reviews` | Completed, output was overbroad/truncated and used only as a locator. |
| `rg -n "Chapter 3\|chapter_3\|chapter-3\|writer\|fake writer\|required_output\|required-output\|availability\|max_output_chars\|artifact_summary\|artifact summary\|summary\|Service\|Agent\|mapping\|EID\|fallback\|single-source\|provider\|llm" fund_agent/services/fund_analysis_service.py fund_agent/services/chapter_orchestrator.py fund_agent/services/llm_run_artifacts.py fund_agent/services/agent_bridge.py fund_agent/agent/runner.py fund_agent/fund/chapter_writer.py tests/services/test_fund_analysis_service_llm.py tests/services/test_chapter_orchestrator.py tests/services/test_llm_run_artifacts.py tests/agent/test_runner.py` | Completed, output was overbroad/truncated and used only as a locator. |
| `sed -n '1,220p' docs/reviews/mvp-provider-llm-chapter-3-code-bug-root-cause-plan-20260613.md` | Completed. Read accepted plan scope, H1-H5 and evidence fields. |
| `sed -n '221,520p' docs/reviews/mvp-provider-llm-chapter-3-code-bug-root-cause-plan-20260613.md` | Completed. Read residual routing and acceptance criteria. |
| `sed -n '1,260p' docs/reviews/mvp-controlled-live-provider-llm-evidence-execution-20260613.md` | Completed. Read accepted safe metadata summary only. |
| `sed -n '1,240p' docs/reviews/mvp-controlled-live-provider-llm-evidence-execution-controller-judgment-20260613.md` | Completed. Read controller dispositions for `6cc89a5`. |
| `rg -n "Provider/LLM Chapter 3\|6cc89a5\|Route C\|typed_template\|EID single-source\|single-source\|no fallback\|fallback\|Host\|Agent\|Service\|NOT_READY\|max_output_chars\|llm_exception\|code_bug\|ValueError\|current active gate\|Next entry" docs/design.md docs/current-startup-packet.md docs/implementation-control.md` | Completed. Confirmed current gate, Route C path and EID single-source/no-fallback guardrails. |
| `rg -n "唯一权威\|四层\|UI -> Service -> Host -> Agent\|FundDocumentRepository\|fallback\|extra_payload\|NOT_READY\|Gate\|heavy\|source policy\|EID\|直接操作文件系统\|禁止" AGENTS.md` | Completed. Confirmed AGENTS boundary rules. |
| `sed -n '18,45p' docs/current-startup-packet.md`; `sed -n '36,110p' docs/current-startup-packet.md`; `sed -n '515,540p' docs/design.md`; `sed -n '650,684p' docs/design.md`; `sed -n '91,136p' AGENTS.md`; `sed -n '1,90p' docs/implementation-control.md` | Completed. Read current gate/control/source-policy/four-layer boundary ranges. |
| `rg -n "def build_fund_llm_execution_request\|ProviderRuntimeBudget\|FundLLMExecutionRequest\|FundLLMRuntimePlan\|max_output_chars\|typed_template_path\|deterministic_fallback_allowed\|analyze_with_llm\|analyze_with_llm_execution\|analyze_with_llm_hosted" fund_agent/services/fund_analysis_service.py` | Completed. Located Service runtime plan and max-output propagation. |
| `rg -n "def _agent_policy_from_service\|def _service_evidence_availability\|def _stop_reason_from_task\|def _failure_category_from_task\|def _runtime_diagnostics_from_task\|blocked_internal_code_bug\|llm_exception\|code_bug\|max_output_chars\|typed_template_path\|EvidenceAvailability" fund_agent/services/agent_bridge.py` | Completed. Located Service-to-Agent mapping and diagnostics bridge. |
| `rg -n "def _writer_input\|def _run_evidence_availability\|def _typed_required_output_items\|def _exception_task\|def _terminal_from_exception\|def _failure_category_from_exception\|blocked_internal_code_bug\|llm_exception\|code_bug\|max_output_chars\|typed_template_path\|EvidenceAvailability\|generate_chapter" fund_agent/agent/runner.py` | Completed. Located Agent policy, writer input and exception classification paths. |
| `sed -n '1214,1290p' fund_agent/services/fund_analysis_service.py`; `sed -n '90,150p' fund_agent/services/agent_bridge.py`; `sed -n '480,520p' fund_agent/services/agent_bridge.py`; `sed -n '629,690p' fund_agent/services/agent_bridge.py`; `sed -n '585,660p' fund_agent/agent/runner.py` | Completed. Confirmed explicit typed fields, mapping and writer input construction. |
| `sed -n '897,940p' fund_agent/agent/runner.py`; `sed -n '1090,1135p' fund_agent/agent/runner.py`; `sed -n '1380,1475p' fund_agent/agent/runner.py`; `sed -n '1460,1515p' fund_agent/agent/runner.py`; `sed -n '1460,1520p' fund_agent/fund/chapter_writer.py` | Completed. Confirmed exception-to-code-bug behavior and typed required-output prompt rendering. |
| `rg -n "def build_chapter_writer_input\|def _required_output_evidence_plan\|def _availability_for_required_output\|typed required output\|不属于当前章节\|缺少 EvidenceAvailability\|RequiredOutputEvidencePlan\|availability_status\|when_evidence_missing\|chapter_id" fund_agent/fund/chapter_writer.py` | Completed. Located typed required-output pre-provider `ValueError` paths. |
| `rg -n "def serialize_chapter_runtime_diagnostics\|def _terminal_runtime_diagnostic\|def _representative_runtime_diagnostics\|def _first_failed_runtime_diagnostic\|_RUNTIME_TERMINAL_STOP_REASONS\|diagnostic_consistency_status\|max_output_chars\|missing_terminal_runtime_diagnostic\|llm_exception\|code_bug\|ValueError\|runtime_diagnostic" fund_agent/services/chapter_orchestrator.py` | Completed. Located runtime diagnostic aggregation and null-output-cap behavior. |
| `rg -n "def _build_summary_payload\|def _runtime_diagnostic_payload\|serialize_chapter_runtime_diagnostics\|first_failed\|runtime_diagnostics\|chapter_runtime_matrix\|max_output_chars\|terminal_runtime\|summary\|raw_provider\|prompt\|redact\|allowlist" fund_agent/services/llm_run_artifacts.py` | Completed. Located artifact summary serialization. |
| `sed -n '544,640p' fund_agent/fund/chapter_writer.py`; `sed -n '905,1095p' fund_agent/fund/chapter_writer.py`; `sed -n '718,748p' fund_agent/services/chapter_orchestrator.py`; `sed -n '2320,2490p' fund_agent/services/chapter_orchestrator.py`; `sed -n '253,310p' fund_agent/services/llm_run_artifacts.py`; `sed -n '675,810p' fund_agent/services/llm_run_artifacts.py` | Completed. Confirmed writer input, required-output validation, runtime serializer and artifact summary rules. |
| `sed -n '1043,1165p' fund_agent/services/chapter_orchestrator.py`; `sed -n '2585,2715p' fund_agent/services/chapter_orchestrator.py`; `sed -n '2843,2885p' fund_agent/services/chapter_orchestrator.py`; `sed -n '1468,1485p' fund_agent/services/chapter_orchestrator.py`; `sed -n '180,190p' fund_agent/services/chapter_orchestrator.py`; `sed -n '190,210p' fund_agent/services/chapter_orchestrator.py` | Completed. Confirmed unknown exception diagnostics, terminal selector behavior and stop-reason/category mapping. |
| `rg -n "test_typed_contract_path_preserves_independent_body_execution\|test_unexpected_exception_records_code_bug_diagnostic_without_secret\|test_runtime_diagnostic_serialization_exposes_only_safe_scalars\|test_provider_timeout\|test_unknown_exception_is_code_bug_not_provider_runtime\|test_legacy_contract_does_not_derive_typed_evidence_availability\|max_output_chars\|typed_template_contract\|required_output_evidence_plan\|ch3.required_output\|fake writer\|writer.requests\|Chapter 3\|chapter_id.*3\|test_artifact_records_terminal_runtime_lineage\|test_artifact_schema_does_not_serialize_prompts" tests/services/test_fund_analysis_service_llm.py tests/services/test_chapter_orchestrator.py tests/services/test_llm_run_artifacts.py tests/agent/test_runner.py` | Completed. Located existing test assertions. |
| `rg -n "class _FakeWriter\|def generate_chapter\|writer.requests\|request.chapter_id\|chapter_id.*3\|required_output_evidence_plan\|max_output_chars" tests/services/test_chapter_orchestrator.py tests/agent/test_runner.py` | Completed. Located fake writer request recording. |
| `rg -n "max_output_chars\|typed_template_path\|ProviderRuntimeBudget\|FundLLMExecutionRequest\|runtime_plan\|FUND_AGENT_LLM_MAX_OUTPUT_CHARS" tests/services/test_fund_analysis_service_llm.py` | Completed. Located Service runtime plan assertions. |
| `sed -n '378,438p' tests/services/test_fund_analysis_service_llm.py`; `sed -n '1013,1126p' tests/services/test_chapter_orchestrator.py`; `sed -n '1390,1455p' tests/services/test_chapter_orchestrator.py`; `sed -n '1584,1642p' tests/services/test_chapter_orchestrator.py`; `sed -n '2093,2168p' tests/services/test_chapter_orchestrator.py`; `sed -n '126,166p' tests/agent/test_runner.py` | Completed. Read existing tests for runtime plan, typed path, diagnostics and code-bug classification. |
| `sed -n '80,122p' tests/agent/test_runner.py`; `sed -n '343,370p' tests/agent/test_runner.py`; `sed -n '126,170p' tests/services/test_llm_run_artifacts.py`; `sed -n '210,245p' tests/services/test_llm_run_artifacts.py`; `sed -n '572,590p' tests/services/test_llm_run_artifacts.py`; `sed -n '60,112p' tests/services/test_chapter_orchestrator.py`; `sed -n '180,232p' tests/services/test_chapter_orchestrator.py`; `sed -n '388,402p' tests/agent/test_runner.py`; `sed -n '24,56p' tests/agent/test_runner.py` | Completed. Read fake writer and artifact safety fixtures. |
| `uv run pytest tests/services/test_fund_analysis_service_llm.py tests/services/test_chapter_orchestrator.py tests/services/test_llm_run_artifacts.py tests/agent/test_runner.py -q` | Passed: `125 passed in 1.07s`. |
| `uv run ruff check fund_agent/services/fund_analysis_service.py fund_agent/services/chapter_orchestrator.py fund_agent/services/llm_run_artifacts.py fund_agent/services/agent_bridge.py fund_agent/agent/runner.py fund_agent/fund/chapter_writer.py tests/services/test_fund_analysis_service_llm.py tests/services/test_chapter_orchestrator.py tests/services/test_llm_run_artifacts.py tests/agent/test_runner.py` | Passed: `All checks passed!`. |

## 4. Process Boundary Deviation / Controller Boundary Finding

The memory `rg` command over `/Users/maomao/.codex/memories/MEMORY.md` was an
unauthorized-by-handoff command deviation. It is not a repo fact, not a
truth-doc fact, not source truth and not root-cause evidence for this gate.

No H1-H5 classification relies on memory output. The source/test evidence
classifications below are based on the handoff-authorized truth/control files,
allowed source/test files, focused tests and static inspection only.

This deviation does not change the H1-H5 classifications, but it remains a
process residual requiring reviewer/controller disposition.

## 5. Exact Source/Test Paths Inspected

Truth/control inputs inspected:

- `AGENTS.md`
- `docs/design.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/reviews/mvp-provider-llm-chapter-3-code-bug-root-cause-plan-20260613.md`
- `docs/reviews/mvp-controlled-live-provider-llm-evidence-execution-20260613.md`
- `docs/reviews/mvp-controlled-live-provider-llm-evidence-execution-controller-judgment-20260613.md`

Allowed source/test files inspected:

- `fund_agent/services/fund_analysis_service.py`
- `fund_agent/services/chapter_orchestrator.py`
- `fund_agent/services/llm_run_artifacts.py`
- `fund_agent/services/agent_bridge.py`
- `fund_agent/agent/runner.py`
- `fund_agent/fund/chapter_writer.py`
- `tests/services/test_fund_analysis_service_llm.py`
- `tests/services/test_chapter_orchestrator.py`
- `tests/services/test_llm_run_artifacts.py`
- `tests/agent/test_runner.py`

No other runtime artifact body, prompt/provider payload, provider response,
final report body, PDF/cache/source body, credential, header or token was
inspected.

## 6. Direct Static/Test Evidence

### 5.1 Service Runtime Plan And Agent Writer Input

`build_fund_llm_execution_request()` constructs `ChapterOrchestrationPolicy`
and `ProviderRuntimeBudget` with `max_output_chars=config.max_output_chars`,
`prompt_payload_mode="compact"` and `typed_template_path="typed_template_contract"`.
It also sets `deterministic_fallback_allowed=False`.

`_agent_policy_from_service()` maps Service policy fields into `AgentRunPolicy`,
including `max_output_chars`, `prompt_payload_mode`, `run_programmatic_audit`,
`run_llm_audit` and `typed_template_path`. `_writer_input()` then calls
`build_chapter_writer_input()` with `max_output_chars=policy.max_output_chars`,
typed required-output items and typed `EvidenceAvailability` when
`typed_template_path=="typed_template_contract"`.

Existing test coverage confirms Service runtime plan propagation:
`test_build_fund_llm_execution_request_prepares_contract_and_runtime_plan`
asserts `chapter_policy.max_output_chars == 34567`,
`provider_runtime_budget.max_output_chars == 34567`,
`prompt_payload_mode == "compact"` and deterministic fallback disabled.

Disposition: the static path shows the command/runtime output cap is expected
to reach Service runtime plan and Agent writer input. This does not itself
prove the exact live `004393 / 2025` Chapter 3 request reached the provider.

### 5.2 Chapter 3 Fake Writer Request Construction

Existing tests prove that the current typed Chapter 3 path can build a writer
request and reach a fake writer:

- `tests/services/test_chapter_orchestrator.py::test_typed_contract_path_preserves_independent_body_execution`
  sets `typed_template_path="typed_template_contract"` and target chapters
  `(1, 2, 3)`.
- The fake writer records requests before returning a fake response.
- The test asserts `[request.chapter_id for request in writer.requests] == [1, 2, 3]`.
- It also asserts Chapter 3 reaches accepted status in that no-live fake path.

Existing Agent runner tests also show all body chapters can reach fake writer
requests:

- `tests/agent/test_runner.py::test_runner_accepts_all_body_chapters_and_builds_readiness`
  asserts writer requests for `[1, 2, 3, 4, 5, 6]`.

Disposition: current existing tests/static inspection prove Chapter 3 request
construction can reach fake writer in the covered typed no-live fixture. They
do not provide an exact reproducer for the live `004393 / 2025` pre-provider
`ValueError`.

### 5.3 Typed Required-output And Availability Rows

Static `chapter_writer` evidence:

- `_required_output_evidence_plan()` raises `ValueError` if typed required-output
  items are enabled without `EvidenceAvailability`.
- `_required_output_plan_item()` raises `ValueError` if an item id does not
  start with `ch{chapter_id}.required_output.`.
- `_availability_for_required_output()` raises `ValueError` if an item with
  missing-evidence behavior has no matching `EvidenceAvailability` requirement.

Existing typed-path test evidence:

- `test_typed_contract_path_preserves_independent_body_execution` derives same
  source availability once through the Service facade.
- It asserts `availability.require("ch3.required_output.item_03").status == "unreviewed"`.
- It asserts Chapter 3 prompt `required_output_items` exactly match the typed
  manifest Chapter 3 items.
- It asserts `ch3.required_output.item_03` has the expected text, action
  `render_evidence_gap` and availability status `unreviewed`.

Disposition: existing static/test evidence shows the covered Chapter 3 typed
required-output and availability rows are coherent. No mismatch was found in
the inspected current code/tests.

### 5.4 Service/Agent Mapping

Agent runner evidence:

- `_terminal_from_exception()` maps provider runtime exception classes to
  `blocked_provider_runtime`; other exceptions map to `blocked_internal_code_bug`.
- `_failure_category_from_exception()` maps provider timeout to `llm_timeout`,
  other provider runtime exceptions to `provider_runtime`, and unknown
  exceptions to `code_bug`.
- `tests/agent/test_runner.py::test_provider_timeout_is_provider_runtime_and_does_not_content_retry`
  confirms provider timeout maps to `blocked_provider_runtime` and `llm_timeout`.
- `tests/agent/test_runner.py::test_unknown_exception_is_code_bug_not_provider_runtime`
  confirms unknown exceptions map to `blocked_internal_code_bug` and `code_bug`
  without leaking secret-like text.

Service bridge evidence:

- `_stop_reason_from_task()` maps `blocked_internal_code_bug` to
  `llm_exception`.
- `_failure_category_from_task()` preserves `task.failure_category`.
- `_runtime_diagnostics_from_task()` converts task exceptions into safe Service
  runtime diagnostics.

Disposition: the live metadata combination `llm_exception` / `code_bug` /
`ValueError` is expected for an unknown deterministic exception surfaced through
the Service/Agent bridge. The mapping is not a Service/Agent mapping bug. It is
generic enough that diagnostic clarity remains useful.

### 5.5 `max_output_chars=null`

Static evidence:

- For provider diagnostics, `_enrich_provider_diagnostic()` preserves
  `diagnostic.max_output_chars`.
- For unknown exceptions without provider diagnostics,
  `_exception_runtime_diagnostics()` constructs `ChapterLLMRuntimeDiagnostic`
  with `error_type=type(exc).__name__` and safe message, but does not include
  `max_output_chars`.
- `_RUNTIME_TERMINAL_STOP_REASONS` includes `llm_exception`.
- `_RUNTIME_STOP_REASON_CATEGORY` has mappings for timeout/rate-limit/malformed/network,
  but no provider category mapping for generic `llm_exception`.
- `_terminal_runtime_diagnostic()` therefore cannot match a `llm_exception`
  diagnostic whose `provider_runtime_category` is `None`.
- `_representative_runtime_diagnostics()` returns an empty tuple when a runtime
  terminal stop reason has no matched terminal diagnostic.
- `_first_failed_runtime_diagnostic()` computes `max_output_chars` only from
  representative diagnostics, so the aggregate first-failed value becomes
  `null` in this pre-provider code-bug shape.

Existing tests:

- `test_runtime_diagnostic_serialization_exposes_only_safe_scalars` proves
  provider-attempt diagnostics preserve `max_output_chars=12000`.
- `test_unexpected_exception_records_code_bug_diagnostic_without_secret` proves
  unknown exceptions produce code-bug diagnostics without leaking sensitive text.
- Existing tests do not assert `max_output_chars` propagation for an unknown
  pre-provider code-bug / `llm_exception` diagnostic.

Disposition: `max_output_chars=null` is explainable from current serializer
logic for pre-provider code-bug diagnostics, but it is not a fully desirable
or verified terminal fact. Because Service runtime plan and Agent writer input
carry the output cap, while unknown-exception diagnostics and the representative
selector do not expose it in first-failed metadata, this is classified as
`DIAGNOSTIC_PROPAGATION_GAP_PRE_PROVIDER`.

### 5.6 Artifact Summary Faithfulness

`write_llm_incomplete_run_artifacts()` builds `summary.json` through
`_build_summary_payload()`. The summary contains:

- a short top-level `first_failed` with chapter/status/stop/category/attempt count;
- full safe runtime diagnostics under `runtime_diagnostics`, produced by
  `serialize_chapter_runtime_diagnostics(orchestration_result)`.

The runtime diagnostic payload is allowlist-only and excludes message,
model name, prompt, draft, raw response, provider body, API key and headers.
`test_artifact_records_terminal_runtime_lineage_at_chapter_and_attempt_levels`
proves artifact summary preserves provider timeout runtime lineage. Existing
artifact safety tests prove prompts/raw provider-like canaries are not serialized.

Disposition: no evidence shows `llm_run_artifacts.py` loses a safe scalar that
`serialize_chapter_runtime_diagnostics()` exposed. The artifact summary appears
faithful to the serializer output. The `max_output_chars=null` residual routes
to diagnostic propagation/selection before artifact extraction, not to artifact
summary extraction.

## 7. H1-H5 Disposition Table

| Hypothesis | Classification | Evidence basis | Residual |
|---|---|---|---|
| H1 - Chapter 3 prompt/input construction bug before provider call | `rejected` for the covered no-live typed path | Existing tests prove Chapter 3 can reach fake writer in typed path: writer requests include chapter 3 and Chapter 3 accepted in the covered fixture. Static Service -> bridge -> Agent -> Fund writer input propagation is explicit. | Missing exact `004393 / 2025` Chapter 3 pre-provider `ValueError` reproducer remains residual. |
| H2 - Chapter 3 typed requirement projection bug | `rejected` for currently inspected rows | Static code would raise on wrong chapter item id or missing availability. Existing typed-path test asserts `ch3.required_output.item_03` availability status `unreviewed`, correct Chapter 3 typed items and `render_evidence_gap`. | Missing exact fixture/assertion for the live failure shape remains residual. |
| H3 - Service/Agent bridge error mapping bug | `MAPPING_EXPECTED_BUT_NEEDS_DIAGNOSTIC_CLARITY` | Agent maps unknown exceptions to internal code bug/category `code_bug`; bridge maps internal code bug stop to Service `llm_exception` while preserving category. Existing tests cover provider timeout vs unknown exception separation. | A future diagnostic/test planning gate may add clearer safe scalar assertions for pre-provider code bugs. |
| H4 - Diagnostic propagation causing `max_output_chars=null` | `DIAGNOSTIC_PROPAGATION_GAP_PRE_PROVIDER` | Service/runtime policy carries `max_output_chars`; provider diagnostics preserve it; unknown exception diagnostics do not carry it and the terminal selector drops representative diagnostics for generic `llm_exception` with no provider category, producing aggregate `null`. | Missing pre-provider `max_output_chars` assertion/reproducer remains residual. |
| H5 - Artifact writer/summary extraction mismatch | `rejected` | Artifact summary uses `serialize_chapter_runtime_diagnostics()` for full runtime lineage and allowlist payloads. Existing tests show provider runtime lineage is faithfully retained and prompt/raw payload canaries are excluded. | Missing artifact fixture for code-bug/pre-provider `llm_exception` shape remains residual, but no extraction mismatch was found. |

## 8. Required Questions Answered

| Question | Answer |
|---|---|
| Does Chapter 3 writer request construction reach fake writer? | Yes for existing no-live typed tests. `test_typed_contract_path_preserves_independent_body_execution` proves Chapter 3 reaches fake writer and accepts in the covered fixture. It does not prove the exact live `004393 / 2025` failure cannot reproduce. |
| Are typed required-output and availability rows coherent? | Yes for inspected current rows. Chapter 3 `ch3.required_output.item_03` maps to availability `unreviewed` and action `render_evidence_gap`; no wrong-chapter or missing availability mismatch was found. |
| Is Service/Agent mapping expected or faulty? | Expected, not faulty, but generic. `blocked_internal_code_bug` -> `llm_exception` plus `code_bug` category explains accepted metadata. Diagnostic clarity can be improved in a future gate. |
| Is `max_output_chars=null` expected or diagnostic gap? | It is explainable by current pre-provider code-bug diagnostic selection, but classified as `DIAGNOSTIC_PROPAGATION_GAP_PRE_PROVIDER` because the cap exists in runtime plan/writer input but is not exposed in the first-failed diagnostic. |
| Is artifact summary faithful or mismatched? | Faithful to current serializer output. The mismatch is upstream diagnostic propagation/selection, not artifact summary extraction. |

## 9. Residuals Routed To Future No-live Planning Gate

| Residual | Required future route | Notes |
|---|---|---|
| Missing exact Chapter 3 fake-writer reproducer for `004393 / 2025` live failure shape. | Future no-live `Chapter 3 Test-reproducer / Diagnostic Implementation Planning Gate`. | Needed before any code fix or repeat live execution. |
| Missing bridge projection assertion for pre-provider `ValueError` -> Service `llm_exception` / `code_bug` / safe `ValueError` metadata. | Future no-live diagnostic/test implementation planning gate. | Current mapping is expected but generic. |
| Missing pre-provider `max_output_chars` assertion. | Future no-live diagnostic/test implementation planning gate. | Directly tied to H4. |
| Missing artifact code-bug/pre-provider fixture. | Future no-live artifact diagnostic/test implementation planning gate. | H5 is rejected on current evidence, but fixture would lock the behavior. |

These residuals do not authorize source/test/runtime edits in this gate, repeat
live execution, source policy changes, fallback, readiness/release claims, PR,
push, merge, mark-ready or cleanup.

## 10. Verdict

No current evidence supports a broad provider readiness, LLM content quality,
source fallback, release readiness or PR readiness claim.

The strongest current root-cause classification is:

`DIAGNOSTIC_PROPAGATION_GAP_PRE_PROVIDER`

The current evidence indicates:

- Chapter 3 typed request construction can reach fake writer in existing
  no-live tests.
- Chapter 3 typed required-output / availability rows are coherent in current
  inspected tests.
- Service/Agent mapping is expected rather than faulty.
- `max_output_chars=null` is caused by current pre-provider code-bug diagnostic
  propagation/selection rather than by command/runtime plan absence.
- Artifact summary is faithful to serializer output; no artifact summary
  extraction bug was found.

Release/readiness remains `NOT_READY`.

EID single-source/no-fallback remains preserved. This gate does not modify
source acquisition policy, does not reintroduce fallback and does not treat
accepted live/provider evidence as fallback-enabled evidence.

Recommended next gate: review this evidence artifact. If accepted, route the
missing reproducer/assertion/fixture residuals to a future no-live
test-reproducer / diagnostic implementation planning gate before any code fix
or repeat live/provider execution.
