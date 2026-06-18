# Provider/LLM Chapter 3 Diagnostic Ready-state Disposition

Date: 2026-06-13

Gate: `Provider/LLM Chapter 3 Diagnostic Ready-state Disposition Gate`

Controller: `AgentController`

Release/readiness: `NOT_READY`

## 1. Scope

This gate is a no-live controller disposition gate only.

In scope:

- Classify the current strongest root cause for the Chapter 3 provider-before failure.
- Decide whether accepted evidence is sufficient to enter a next gate.
- Choose exactly one next gate class: no-live fix, more no-live evidence, bounded live re-evidence, or blocked.
- Preserve current source policy and release/readiness status.

Out of scope:

- Source/test/runtime implementation changes.
- `docs/implementation-control.md` or `docs/current-startup-packet.md` update.
- stage, commit, push, PR, merge, release or readiness state changes.
- live/provider/LLM/network/PDF/FDR/source/analyze/checklist/readiness/release/PR commands.
- annual-period LLM route design.
- repair budget change or calibration.
- release-ready, MVP-ready or LLM-path-ready claims.

## 2. Evidence Reviewed

Truth sources:

- `AGENTS.md`
- `docs/implementation-control.md`
- `docs/current-startup-packet.md`
- `docs/design.md`

Evidence artifacts:

- `docs/reviews/mvp-provider-llm-chapter-3-code-bug-root-cause-evidence-controller-judgment-20260613.md`
- `docs/reviews/mvp-provider-llm-chapter-3-test-reproducer-diagnostic-implementation-controller-judgment-20260613.md`
- `docs/reviews/mvp-provider-llm-chapter-3-test-reproducer-diagnostic-implementation-evidence-20260613.md`

Relevant design/control facts reviewed:

- Route C `fund-analysis analyze --use-llm` is explicit opt-in, provider-backed and fail-closed.
- Current `analyze-annual-period` is deterministic and is not a Route C LLM body-chapter route.
- Host remains lifecycle-only and business-opaque; Service owns ExecutionContract, provider construction/runtime ceilings and final product fail-closed mapping.
- Agent currently owns no-live body-chapter mechanics; full production Agent runtime expansion remains future scope.
- EID annual-report source policy remains single-source only: `selected_source=eid`, `source_mode=single_source_only`, `fallback_enabled=false`.

## 3. Accepted Current Facts

| Fact | Disposition |
|---|---|
| Exact accepted live Provider/LLM execution for `004393 / 2025` failed closed before provider attempt for Chapter 3. | Accepted historical live fact only; not readiness proof. |
| Chapter 3 first failure was `llm_exception` / `code_bug` / `ValueError`, with provider attempt count `0`. | Accepted current failure shape. |
| Prior root-cause evidence rejected H1/H2 for covered no-live typed paths, accepted H3 only as expected mapping needing diagnostic clarity, accepted H4 as diagnostic propagation gap, and rejected H5 as artifact extraction mismatch. | Accepted H1-H5 disposition. |
| Implementation checkpoint `eb72e6c` added no-live reproducer tests and safe diagnostic propagation for provider-before Chapter 3 `ValueError`. | Accepted code/test fact. |
| Safe `max_output_chars=12000` now propagates through no-live pre-provider code-bug diagnostics and incomplete-run artifact lineage. | Accepted no-live diagnostic fact. |
| Incomplete-run artifacts retain pre-provider `llm_exception` / `code_bug`, provider attempt count `0`, empty provider runtime categories and redacted runtime lineage. | Accepted artifact fact. |
| Live provider/LLM full completion, LLM content quality, 401/403 provider-response classification, PR state and release/readiness remain unproven. | Accepted residual; release/readiness remains `NOT_READY`. |

## 4. Root-cause Classification

Current strongest root-cause classification:

`DIAGNOSTIC_PROPAGATION_GAP_PRE_PROVIDER`

Current broader failure class:

`PRE_PROVIDER_CODE_BUG_NOT_PROVIDER_RUNTIME`

Reasoning:

- The accepted live failure shape has provider attempt count `0`, so it is not currently classified as provider runtime failure.
- The accepted no-live tests reproduce Chapter 3 `ValueError` as internal `code_bug` / `llm_exception`.
- The Service/Agent bridge mapping is accepted as expected fail-closed behavior, not a provider retry/fallback issue.
- The prior blocker `max_output_chars=null` is now specifically explained and addressed as a diagnostic propagation/selection gap for unknown pre-provider exceptions.
- Artifact serialization is faithful to current diagnostic state and was not accepted as the root cause.

This classification does not prove live provider completion or content quality. It also does not authorize source fallback, provider default changes, annual-period LLM routing or repair budget changes.

## 5. Disposition Decision

Disposition: `PROCEED_TO_NO_LIVE_FIX_GATE`

Evidence sufficiency:

- Sufficient to proceed beyond root-cause/evidence gathering for the provider-before diagnostic/code path.
- Sufficient to reject bounded live re-evidence as the immediate next gate, because live replay would not isolate or fix provider-before code behavior and remains separately authorized.
- Sufficient to reject `NEED_MORE_NO_LIVE_DIAGNOSTIC_EVIDENCE` for the diagnostic propagation issue, because `eb72e6c` added direct no-live reproducer, bridge/orchestrator propagation and artifact lineage evidence.
- Not sufficient to claim LLM path readiness, MVP readiness, release readiness or live completion.

The next gate should be a narrow no-live fix gate only if it targets the remaining provider-before Chapter 3 code/failure path under fake/no-live evidence. It must not include annual-period LLM design, repair budget calibration, provider default changes, source fallback or live execution.

## 6. Next Gate Recommendation

Recommended next gate:

`Provider/LLM Chapter 3 Provider-before Code-bug No-live Fix Gate`

Required next-gate boundaries:

- no-live only;
- source/test/runtime changes only after an accepted implementation plan;
- no live/provider/LLM/network/PDF/FDR/source/analyze/checklist/readiness/release/PR commands;
- no EID source-policy change;
- no Eastmoney, fund-company/CDN, CNINFO or fallback re-entry;
- no annual-period LLM route design;
- no repair budget change;
- no provider defaults/model/base URL/runtime budget change;
- preserve release/readiness as `NOT_READY`.

Minimum next-gate objective:

- Identify the exact no-live code path that can still produce Chapter 3 pre-provider `ValueError` or equivalent internal code-bug failure.
- Apply a narrow no-live code fix only if the code path is directly proven.
- Preserve fail-closed behavior and safe diagnostics.
- Keep deterministic default `analyze/checklist` unchanged.

## 7. Residuals

| Residual | Status | Owner / next handling |
|---|---|---|
| Exact live `004393 / 2025` Route C full completion remains unproven. | Deferred | Separately authorized bounded live re-evidence gate after no-live fix, if needed. |
| LLM content quality remains unproven. | Deferred | Future content-quality/readiness gate; not this gate. |
| 401/403 provider-response classification remains unproven. | Deferred | Future provider-response negative evidence gate. |
| Annual-period LLM route remains undesigned. | Deferred | Separate annual-period LLM route design gate only. |
| Chapter repair budget remains uncalibrated. | Deferred | Separate repair budget calibration gate only. |
| Release/readiness remains `NOT_READY`. | Accepted residual | Release/readiness gate only; no current readiness claim. |

## 8. Control-doc Update Recommendation

Do not update control docs in this gate.

Recommended future control-doc update location after this artifact is reviewed/accepted:

- `docs/implementation-control.md` current gate table:
  - set next entry point to `Provider/LLM Chapter 3 Provider-before Code-bug No-live Fix Gate`;
  - record this artifact path as the disposition basis;
  - preserve `NOT_READY`.
- `docs/current-startup-packet.md` current mainline table:
  - mirror the next entry point;
  - keep EID single-source/no-fallback guardrail;
  - explicitly state live/provider/readiness remains deferred.

## 9. Final Verdict

VERDICT: PROCEED_TO_NO_LIVE_FIX_GATE
