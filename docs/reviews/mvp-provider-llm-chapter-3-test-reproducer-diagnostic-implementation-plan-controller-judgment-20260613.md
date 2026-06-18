# Provider/LLM Chapter 3 Test-reproducer / Diagnostic Implementation Plan Controller Judgment

Date: 2026-06-13

Gate: `Provider/LLM Chapter 3 Test-reproducer / Diagnostic Implementation Planning Gate`

Status: `ACCEPT_PLAN_NOT_READY`

Release/readiness: `NOT_READY`

## Inputs

| Input | Role |
| --- | --- |
| `AGENTS.md` | Rule truth, EID source boundary, no `extra_payload`, no raw body leakage. |
| `docs/design.md` | Design truth for Route C, EID single-source and Service/Host/Agent/Fund boundaries. |
| `docs/current-startup-packet.md` | Current gate and accepted evidence checkpoint `4a7c191`. |
| `docs/implementation-control.md` | Control truth for current no-live planning gate. |
| `docs/reviews/mvp-provider-llm-chapter-3-code-bug-root-cause-evidence-controller-judgment-20260613.md` | Accepted `DIAGNOSTIC_PROPAGATION_GAP_PRE_PROVIDER` evidence. |
| `docs/reviews/mvp-provider-llm-chapter-3-test-reproducer-diagnostic-implementation-plan-20260613.md` | Plan under judgment. |
| `docs/reviews/mvp-provider-llm-chapter-3-test-reproducer-diagnostic-implementation-plan-review-ds-20260613.md` | Visible-panel DS review. |
| `docs/reviews/mvp-provider-llm-chapter-3-test-reproducer-diagnostic-implementation-plan-review-mimo-20260613.md` | Visible-panel MiMo review. |

## Controller Judgment

The implementation plan is accepted.

The plan is code-generation-ready for a future no-live implementation gate because it identifies:

- exact source/test files;
- exact functions and call paths to modify;
- exact no-live reproducers and assertions;
- typed `max_output_chars` propagation points;
- safe scalar diagnostic boundaries;
- artifact fixture assertions;
- validation commands and stop conditions.

The plan does not authorize implementation in this planning gate.

## Accepted Implementation Sequencing

Controller accepts the plan with this sequencing instruction for the next implementation gate:

| Implementation pass | Scope | Reason |
| --- | --- | --- |
| Pass A | S1 + S2 together: add Agent/Service reproducer tests and implement safe pre-provider diagnostic propagation. | S1 tests are expected to fail before S2. Combining them avoids committing an intentionally failing test-only checkpoint while still keeping scope narrow. |
| Pass B | S3 artifact code-bug/pre-provider fixture and S4 focused validation. | Artifact fixture should verify the serializer output after Pass A, without broadening artifact schema. |

The next implementation handoff may combine Pass A and Pass B into a single local implementation pass only if the worker confirms the touched files remain exactly within the accepted plan and validation remains focused. If implementation complexity increases, controller must split them.

## Reviewer Finding Disposition

| Finding / note | Controller disposition | Required handling |
| --- | --- | --- |
| DS: `_FakeExtractor` was not located by direct grep. | `ACCEPT_NONBLOCKING_IMPLEMENTATION_DETAIL` | Implementation worker may use the existing equivalent fixture/helper already present in the allowed test file. If no equivalent exists, stop and report to controller; do not invent broad fixture infrastructure. |
| DS: split S1-S3 vs one pass is controller decision. | `ACCEPT_WITH_SEQUENCING_REWRITE` | Use Pass A / Pass B sequencing above. |
| MiMo: `_FakeChapterLLMClient` in the Service test accepts `texts` only. | `ACCEPT_NONBLOCKING_IMPLEMENTATION_DETAIL` | Implementation worker may extend the existing fake narrowly or create a local test-only variant in the allowed test file. Do not change production provider behavior. |
| MiMo: auto-recalled memory note. | `ACCEPT_PROCESS_NOTE_NONBLOCKING` | MiMo artifact explicitly states memory was not used as gate evidence. Future implementation/review handoffs must continue to forbid memory probing. |

## Source Policy Judgment

Current operational annual-report source truth remains:

- `selected_source=eid`
- `source_mode=single_source_only`
- `fallback_enabled=false`

Eastmoney, fund-company/CDN, CNINFO and any annual-report fallback are not current source truth, not current execution paths and not authorized current sources.

The accepted plan does not change source acquisition policy, fallback behavior, provider defaults, provider model, base URL, timeout budget, EID policy, deterministic fallback or release/readiness state.

## Implementation Gate Boundaries

The next implementation gate must preserve:

- no live/provider/LLM/network/PDF/FDR/source/cache commands;
- no `fund-analysis analyze`, `fund-analysis checklist` or `fund-analysis analyze-annual-period`;
- no memory probing;
- no source policy or fallback change;
- no `extra_payload` parameter propagation;
- no raw exception message, prompt, draft, provider body, model name, API key, header, credential or secret in diagnostics/artifacts;
- code bugs remain distinct from provider runtime availability;
- release/readiness remains `NOT_READY`.

## Next Entry

Recommended next entry:

`Provider/LLM Chapter 3 Test-reproducer / Diagnostic Implementation Gate`

The next gate is no-live implementation. It may modify only the files accepted by the plan and controller sequencing.
