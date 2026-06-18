# Provider/LLM Chapter 3 Code-bug Root-cause Evidence Controller Judgment

Date: 2026-06-13

Gate: `Provider/LLM Chapter 3 Code-bug Root-cause Evidence Gate`

Status: `ACCEPT_EVIDENCE_NOT_READY`

Release/readiness: `NOT_READY`

## Inputs

| Input | Role |
| --- | --- |
| `AGENTS.md` | Rule truth, source boundary, four-layer boundary and no hidden `extra_payload` guardrail. |
| `docs/design.md` | Design truth for Route C, EID single-source policy and Service/Host/Agent/Fund boundaries. |
| `docs/current-startup-packet.md` | Current gate and accepted checkpoints `9de9321` / `1416c8f`. |
| `docs/implementation-control.md` | Control truth for current no-live evidence gate and next-entry routing. |
| `docs/reviews/mvp-provider-llm-chapter-3-code-bug-root-cause-plan-20260613.md` | Accepted evidence plan and H1-H5 classification framework. |
| `docs/reviews/mvp-provider-llm-chapter-3-code-bug-root-cause-evidence-20260613.md` | Evidence worker artifact under review. |
| `docs/reviews/mvp-provider-llm-chapter-3-code-bug-root-cause-evidence-review-ds-20260613.md` | Visible-panel DS review. |
| `docs/reviews/mvp-provider-llm-chapter-3-code-bug-root-cause-evidence-review-mimo-20260613.md` | Visible-panel MiMo review. |

## Controller Decision

The evidence artifact is accepted.

The strongest accepted root-cause classification is:

`DIAGNOSTIC_PROPAGATION_GAP_PRE_PROVIDER`

Accepted evidence:

- Chapter 3 can reach fake writer in the currently covered no-live typed path.
- Current inspected Chapter 3 typed required-output and `EvidenceAvailability` rows are coherent.
- Service/Agent bridge mapping is expected rather than faulty: internal code bug maps to Service `llm_exception` while preserving `code_bug`.
- `max_output_chars=null` is explainable as a pre-provider code-bug diagnostic propagation/selection gap: runtime policy carries the cap, provider diagnostics preserve the cap, but unknown pre-provider exception diagnostics and terminal selection do not expose it in first-failed metadata.
- Artifact summary is faithful to current serializer output; no artifact summary extraction bug was accepted.

The evidence does not authorize implementation, repeat live execution, provider readiness, LLM content-quality acceptance, release readiness, PR readiness, source-policy change, fallback, Eastmoney, fund-company/CDN or CNINFO re-entry.

## H1-H5 Disposition

| Hypothesis | Controller disposition | Basis |
| --- | --- | --- |
| H1 - Chapter 3 prompt/input construction bug before provider call | `REJECT_FOR_COVERED_NO_LIVE_TYPED_PATH_WITH_RESIDUAL` | Existing no-live typed tests prove Chapter 3 can reach fake writer, but exact `004393 / 2025` live failure shape is not reproduced. |
| H2 - Chapter 3 typed requirement projection bug | `REJECT_FOR_INSPECTED_ROWS_WITH_RESIDUAL` | Static/test evidence shows current inspected Chapter 3 required-output and availability rows are coherent. |
| H3 - Service/Agent bridge error mapping bug | `ACCEPT_WITH_REWRITE: MAPPING_EXPECTED_BUT_NEEDS_DIAGNOSTIC_CLARITY` | Mapping is expected and fail-closed, but future diagnostics should make pre-provider code-bug shape easier to distinguish. |
| H4 - Diagnostic propagation causing `max_output_chars=null` | `ACCEPT: DIAGNOSTIC_PROPAGATION_GAP_PRE_PROVIDER` | Runtime cap exists before provider path, but unknown pre-provider diagnostics and terminal selection do not surface it in first-failed safe metadata. |
| H5 - Artifact writer/summary extraction mismatch | `REJECT_WITH_FIXTURE_RESIDUAL` | Artifact summary appears faithful to serializer output; missing code-bug/pre-provider fixture remains a future test residual. |

## Review Disposition

| Reviewer finding | Controller disposition | Reason |
| --- | --- | --- |
| DS F1: unauthorized memory `rg` command was not in handoff allowed-command list. | `ACCEPT_PROCESS_RESIDUAL_NONBLOCKING` | The artifact now labels it `DEVIATION_NOT_EVIDENCE`; no H1-H5 classification relies on it. Future evidence handoffs must not probe agent memory unless explicitly authorized. |
| DS F2: section numbering inconsistency. | `DEFER_COSMETIC_NO_ACTION` | Cosmetic only; not worth revising an accepted evidence artifact. |
| MiMo PASS with residual routing. | `ACCEPT` | MiMo independently confirmed source truth, H1-H5 classification, validation sufficiency and `NOT_READY`. |

## Source Policy Judgment

Current operational annual-report source truth remains:

- `selected_source=eid`
- `source_mode=single_source_only`
- `fallback_enabled=false`

Eastmoney, fund-company/CDN, CNINFO and any annual-report fallback are not current source truth, not current execution paths and not authorized current sources. Historical mentions, code names or old artifacts cannot re-enter the current design or execution policy through this gate.

## Validation Accepted

Accepted no-live validation results from the evidence artifact:

- `uv run pytest tests/services/test_fund_analysis_service_llm.py tests/services/test_chapter_orchestrator.py tests/services/test_llm_run_artifacts.py tests/agent/test_runner.py -q`
  - Result: `125 passed in 1.07s`
- `uv run ruff check fund_agent/services/fund_analysis_service.py fund_agent/services/chapter_orchestrator.py fund_agent/services/llm_run_artifacts.py fund_agent/services/agent_bridge.py fund_agent/agent/runner.py fund_agent/fund/chapter_writer.py tests/services/test_fund_analysis_service_llm.py tests/services/test_chapter_orchestrator.py tests/services/test_llm_run_artifacts.py tests/agent/test_runner.py`
  - Result: `All checks passed!`

The unauthorized memory `rg` command is not accepted as validation evidence.

## Residuals

| Residual | Owner | Next routing |
| --- | --- | --- |
| Missing exact Chapter 3 fake-writer reproducer for `004393 / 2025` live failure shape. | Future planning/implementation owner | No-live `Chapter 3 Test-reproducer / Diagnostic Implementation Planning Gate`. |
| Missing bridge projection assertion for pre-provider `ValueError` -> Service `llm_exception` / `code_bug` / safe metadata. | Future diagnostic/test owner | No-live diagnostic/test implementation planning gate. |
| Missing pre-provider `max_output_chars` assertion. | Future diagnostic/test owner | No-live diagnostic/test implementation planning gate. |
| Missing artifact code-bug/pre-provider fixture. | Future artifact diagnostic/test owner | No-live artifact diagnostic/test implementation planning gate. |
| Evidence worker ran unauthorized memory `rg`. | Controller / handoff owner | Future handoffs must explicitly exclude memory probing unless authorized; current artifact quarantined it as `DEVIATION_NOT_EVIDENCE`. |

## Next Entry

Recommended next entry:

`Provider/LLM Chapter 3 Test-reproducer / Diagnostic Implementation Planning Gate`

Required boundary for the next gate:

- no live/provider/LLM/network/PDF/FDR/source/analyze/checklist/readiness/release/PR commands;
- no Eastmoney, fund-company/CDN, CNINFO or annual-report fallback;
- no implementation until a reviewed planning artifact accepts exact files, tests and diagnostics to add;
- preserve `NOT_READY`.
