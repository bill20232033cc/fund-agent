# Provider/LLM Chapter 3 No-live Code-bug Root-cause/Fix Verification Controller Judgment - 2026-06-14

Date: 2026-06-14

Controller: `AgentController`

Gate: `Provider/LLM Chapter 3 No-live Code-bug Root-cause/Fix Verification Gate`

Release/readiness: `NOT_READY`

## 1. Scope

This judgment accepts or rejects the no-live root-cause/fix verification
evidence for the remaining Chapter 3 pre-provider `ValueError` / `code_bug`
after bounded live retry checkpoint `0159b3a`.

No source, tests, runtime behavior, source policy, provider defaults, repair
budget, annual-period LLM route, Docling behavior, readiness, release or PR
state is changed by this judgment.

## 2. Evidence Reviewed

Truth/control sources:

- `AGENTS.md`
- `docs/design.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`

Evidence and reviews:

- `docs/reviews/provider-llm-chapter3-no-live-code-bug-root-cause-fix-verification-evidence-procodex-20260614.md`
- `docs/reviews/provider-llm-chapter3-no-live-code-bug-root-cause-fix-verification-review-ds-20260614.md`
- `docs/reviews/provider-llm-chapter3-no-live-code-bug-root-cause-fix-verification-review-mimo-20260614.md`
- `docs/reviews/provider-llm-chapter3-bounded-live-re-evidence-retry-controller-judgment-20260614.md`

## 3. Accepted Findings

| Finding | Disposition | Basis |
|---|---|---|
| The remaining Chapter 3 failure is still pre-provider. | ACCEPT | Retry evidence and procodex red reproducer both preserve provider attempt count `0`; MiMo/DS reviews confirm. |
| Safe runtime metadata residual `max_output_chars=null` is closed for the bounded retry. | ACCEPT | Prior retry judgment accepted runtime `max_output_chars=12000`. |
| The remaining root cause is not merely diagnostic propagation. | ACCEPT | Diagnostics are now present/consistent; failure remains a real typed writer-input / availability path failure. |
| A typed required-output availability gap can surface as `ValueError` / `code_bug` before provider. | ACCEPT | Procodex no-live red reproducer and MiMo/DS code inspection of `chapter_writer.py` and `runner.py`. |
| The correct next fix layer is Fund writer / typed availability boundary, not Service bridge or Agent runner reclassification. | ACCEPT | AGENTS module boundaries; DS and MiMo both confirm `fund_agent/fund/chapter_writer.py` is the correct primary candidate. |
| The worker's `BLOCKED_NEEDS_CONTROLLER_DECISION` verdict is valid. | ACCEPT | Its allowed write set excluded the Fund writer file needed for the semantic fix. |
| No-live, source/fallback and readiness boundaries were preserved. | ACCEPT | No live/provider/network/source/readiness command was run; `NOT_READY` preserved. |

## 4. Review Disposition

| Reviewer | Verdict | Controller disposition |
|---|---|---|
| AgentDS | `PASS_BLOCKED` | ACCEPT. DS confirmed the blocked verdict, root-cause chain and Fund-layer fix location. |
| AgentMiMo | `PASS_BLOCKED` | ACCEPT. MiMo confirmed the blocked verdict, root-cause coherence and justified write-set expansion. |

Non-blocking observations:

- DS noted the worker may have interpreted the write set conservatively; the
  controller accepts that conservatism because it avoided cross-layer edits
  without explicit authorization.
- MiMo noted the next patch gate must distinguish "availability not provided"
  from "availability provided but missing an item"; this is accepted as a
  mandatory boundary for the next gate.

## 5. Rejected Claims

| Claim | Disposition | Reason |
|---|---|---|
| Provider readiness is proven. | REJECT | No provider attempt occurred for the first failed Chapter 3 path. |
| LLM content quality is accepted. | REJECT | No chapter/report body was read or accepted. |
| Source policy or fallback changed. | REJECT | No source path was used and EID single-source/no-fallback remains current. |
| Runner or Service should hide/reclassify the failure as success. | REJECT | That would mask a Fund-domain typed availability issue and weaken fail-closed diagnostics. |
| Release/readiness can advance. | REJECT | `NOT_READY` remains current truth. |

## 6. Next Gate Authorization

The next gate is authorized as:

`Provider/LLM Chapter 3 Fund-writer Missing-availability No-live Patch Gate`

Authorized primary write set:

- `fund_agent/fund/chapter_writer.py`
- `tests/agent/test_runner.py`
- `tests/services/test_chapter_orchestrator.py`
- `tests/services/test_fund_analysis_service_llm.py`
- one implementation evidence artifact under `docs/reviews/`

Conditional write set, only if direct no-live evidence proves the fix belongs
there instead of or in addition to `chapter_writer.py`:

- `fund_agent/fund/evidence_availability.py`
- typed contract sidecar files directly responsible for Chapter 3 required
  output availability mapping

Mandatory implementation boundary:

- Preserve `ValueError` / `code_bug` for true configuration errors where typed
  availability is not provided at all and should fail closed as code bug.
- Convert only covered missing typed required-output availability for items with
  declared `when_evidence_missing` into deterministic writer-preflight fact-gap
  blocking, with zero provider calls.
- Do not patch Agent runner, Service bridge or orchestrator to fabricate Fund
  semantics.
- Do not run live/provider/network/analyze/checklist/readiness/release/PR
  commands.

## 7. Residuals

| Residual | Owner | Next handling |
|---|---|---|
| Chapter 3 typed required-output availability gap still needs source/test fix. | Fund writer / typed availability owner + controller | Next authorized no-live patch gate. |
| Provider readiness and provider-response classification remain unproven. | Provider/runtime owner | No further live retry until no-live fix is accepted. |
| LLM content quality remains unaccepted. | Provider/runtime + chapter owners | Future content-quality gate after complete accepted run exists. |
| Release/readiness remains `NOT_READY`. | Release owner/controller | Separate readiness/release gate only. |

## 8. Final Verdict

VERDICT: ACCEPT_BLOCKED_AUTHORIZE_FUND_WRITER_PATCH_GATE_NOT_READY

NEXT_ENTRY: `Provider/LLM Chapter 3 Fund-writer Missing-availability No-live Patch Gate`
