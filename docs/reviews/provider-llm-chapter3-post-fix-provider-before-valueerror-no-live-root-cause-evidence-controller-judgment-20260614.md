# Provider/LLM Chapter 3 Post-fix Provider-before ValueError No-live Root-cause Evidence - Controller Judgment

Date: 2026-06-14

## 1. Scope

Gate: `Provider/LLM Chapter 3 Post-fix Provider-before ValueError No-live Root-cause Evidence Gate`.

This judgment accepts or rejects the no-live root-cause evidence for the remaining Chapter 3 provider-before `ValueError` after the accepted post-fix bounded live evidence.

No code fix is implemented by this judgment.

## 2. Evidence Reviewed

Truth/control:

- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`

Accepted prior gate:

- `docs/reviews/provider-llm-chapter3-post-fix-bounded-live-re-evidence-controller-judgment-20260614.md`

Root-cause evidence:

- `docs/reviews/provider-llm-chapter3-post-fix-provider-before-valueerror-no-live-root-cause-evidence-20260614.md`

Reviews:

- `docs/reviews/provider-llm-chapter3-post-fix-provider-before-valueerror-no-live-root-cause-evidence-review-ds-20260614.md`
- `docs/reviews/provider-llm-chapter3-post-fix-provider-before-valueerror-no-live-root-cause-evidence-review-mimo-20260614.md`

## 3. Accepted Root-cause Facts

| Fact | Controller classification |
| --- | --- |
| `_writer_input()` succeeds for the reproduced missing-portfolio-managers shape. | Accepted no-live evidence fact |
| Fund writer fails before provider/fake-writer invocation while building required-output plan. | Accepted no-live evidence fact |
| `ch3.required_output.item_01` depends on `structured.basic_identity` and `structured.portfolio_managers`. | Accepted code/template fact |
| When `portfolio_managers` is missing, `ch3.required_output.item_01` availability status becomes `missing`. | Accepted no-live evidence fact |
| The typed template declares `when_evidence_missing=null` for `ch3.required_output.item_01`. | Accepted template fact |
| `_required_output_action()` raises `ValueError("typed required output 缺证但未声明 when_evidence_missing：ch3.required_output.item_01")` for status in missing-evidence states with null behavior. | Accepted code fact |
| Agent runner maps that `ValueError` to `blocked_internal_code_bug` / `llm_exception` / `code_bug` with zero writer/provider calls and attempts `0`. | Accepted no-live evidence fact |
| This matches the accepted live failure shape: Chapter 3, `ValueError`, `llm_exception`, `code_bug`, provider attempt count `0`. | Accepted evidence-chain fact |

## 4. Review Disposition

| Reviewer / artifact | Verdict | Controller disposition |
| --- | --- | --- |
| DS review: `docs/reviews/provider-llm-chapter3-post-fix-provider-before-valueerror-no-live-root-cause-evidence-review-ds-20260614.md` | `PASS_WITH_FINDINGS` | ACCEPT_WITH_FINDINGS. DS independently re-ran the key reproducer and confirmed the full six-step chain. DS findings are accepted as implementation-gate guidance: item 01 lacks missing-evidence behavior, and current exception classification is diagnostically coarse. |
| MiMo review: `docs/reviews/provider-llm-chapter3-post-fix-provider-before-valueerror-no-live-root-cause-evidence-review-mimo-20260614.md` | `PASS` | ACCEPT_WITH_MINOR_WORDING_FINDING. MiMo confirms the root cause and notes that the artifact should say `status in _MISSING_EVIDENCE_STATUSES` rather than the broader phrase `non-available status`. This wording issue does not weaken the root-cause proof. |

## 5. Controller Decision

The no-live root cause is accepted as proven.

Current strongest classification:

`TYPED_REQUIRED_OUTPUT_ITEM_01_MISSING_BEHAVIOR_PROVIDER_BEFORE_VALUEERROR`

The remaining Chapter 3 live failure is not provider availability, provider response quality or LLM content quality. It is a Fund/typed-template missing-evidence policy gap surfaced as a provider-before `ValueError`.

## 6. Implementation-gate Direction

Next gate:

`Provider/LLM Chapter 3 Required-output Item 01 Missing-evidence No-live Fix Implementation Gate`

Required implementation-gate decisions:

1. Decide the explicit missing-evidence behavior for `ch3.required_output.item_01` when its availability status is in `_MISSING_EVIDENCE_STATUSES`.
2. Prefer a fail-closed domain behavior over masking in Service/Agent runner.
3. Add red-test-first coverage for `portfolio_managers` missing / unreviewed causing `ch3.required_output.item_01` to avoid provider-before `ValueError`.
4. Verify the result remains zero-provider when evidence is insufficient, and maps to fact-gap or an explicitly accepted template/prompt-contract status instead of `code_bug`.
5. Preserve EID single-source/no-fallback and `NOT_READY`.

Implementation-gate non-goals:

- no live/provider/network/source/PDF/FDR/analyze/checklist/readiness/release/PR command;
- no Service/runner masking of Fund semantics;
- no provider-default, repair-budget, annual-period LLM route or Docling change;
- no release or MVP-ready claim.

## 7. Residuals

| Residual | Owner / next action |
| --- | --- |
| Exact live field state is not present in safe runtime artifacts. | Accepted residual; no source/PDF body read is needed because no-live reproducer matches the live diagnostic shape. |
| Other `_MISSING_EVIDENCE_STATUSES` may trigger the same item 01 null-behavior path. | Implementation gate must cover the status set, not only `missing`. |
| Other typed required-output items with `when_evidence_missing=null` may have analogous risks. | Future audit candidate; not a blocker for this Chapter 3 item 01 fix gate unless touched. |
| Provider readiness and LLM content quality remain unproven. | Deferred until Chapter 3 reaches provider and accepted draft/conclusion exists. |
| Release/readiness remains `NOT_READY`. | Separate readiness/release gate only. |

## 8. Control-doc Update Recommendation

Update `docs/current-startup-packet.md` and `docs/implementation-control.md` to record:

- this no-live root-cause evidence accepted;
- next entry point `Provider/LLM Chapter 3 Required-output Item 01 Missing-evidence No-live Fix Implementation Gate`;
- `NOT_READY` preserved;
- no live/provider/source/fallback/readiness/release/PR state changed.

## 9. Final Verdict

VERDICT: ACCEPT_ROOT_CAUSE_PROVEN_READY_FOR_NO_LIVE_FIX_IMPLEMENTATION_GATE_NOT_READY

Next entry point:

`Provider/LLM Chapter 3 Required-output Item 01 Missing-evidence No-live Fix Implementation Gate`
