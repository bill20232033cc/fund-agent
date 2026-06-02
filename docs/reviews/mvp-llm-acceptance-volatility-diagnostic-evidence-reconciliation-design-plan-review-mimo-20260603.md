# MVP LLM acceptance volatility and diagnostic evidence reconciliation design plan review — MiMo

## Scope

- Role: independent plan reviewer, not controller.
- Gate: `MVP LLM acceptance volatility and diagnostic evidence reconciliation design gate`.
- Classification: heavy.
- Artifact reviewed: `docs/reviews/mvp-llm-acceptance-volatility-diagnostic-evidence-reconciliation-design-plan-20260603.md`.
- Actions not taken: no code, test, config, runtime, provider, auditor, template, score, golden, readiness, commit, push or PR changes.

## Required Inputs Read

| Input | Disposition |
|---|---|
| `AGENTS.md` | reviewed for heavy gate, first-principles, same-source root cause, fail-closed constraints |
| `docs/design.md` | reviewed for current Route C, Service/Host/Agent boundary, future design labels |
| `docs/implementation-control.md` | reviewed for current gate, accepted evidence, prohibited changes |
| `docs/current-startup-packet.md` | reviewed for short startup state and residuals |
| `docs/reviews/mvp-ch2-auditor-timeout-120s-evidence-20260603.md` | reviewed as direct 120s diagnostic evidence |
| `docs/reviews/mvp-ch2-auditor-timeout-120s-evidence-controller-judgment-20260603.md` | reviewed for accepted/rejected conclusions |
| `reports/llm-runs/006597-2024-20260602T220325Z-host_run_c83e8c1adcc846a/summary.json` | inspected via safe scalar fields |
| `reports/llm-runs/006597-2024-20260602T224137Z-host_run_4b7dddc60d084e7/summary.json` | inspected via safe scalar fields |
| 120s `chapter-02.json` | inspected for status, stop reason, issue ids/reasons, repair decisions, runtime diagnostics |
| `fund_agent/services/chapter_orchestrator.py` | inspected for serializer functions, `_exception_result`, `_runtime_diagnostics_for_run`, `ChapterRunResult`, terminal failure tracking |
| `fund_agent/services/llm_run_artifacts.py` | inspected for retained artifact serializer references, allowlist fields |

## Findings

### F1 — Ch2 "diagnostic attribution gap" may overstate design complexity vs code bug

**Severity**: Major (advisory, not blocking)

The plan frames the Ch2 discrepancy as a "diagnostic attribution gap" requiring a design-level reconciliation gate. The observed data is:

- 120s run Ch2: `stop_reason=llm_timeout`, `failure_category=llm_timeout`, issues contain `LLMProviderTimeoutError`.
- 120s run Ch2 runtime diagnostics: single auditor row with `finish_reason=stop`, `response_chars=22`, `chapter_failure_category=prompt_contract`, no timeout scalar fields.
- 120s run Ch2 chapter JSON: attempt has a `programmatic:L1` repair decision, meaning the auditor completed normally before the terminal timeout.

The plan treats this as a design-level problem requiring new `diagnostic_consistency_status` fields and a full serialization repair gate. However, the more parsimonious explanation is a concrete code bug: `_runtime_diagnostics_for_run()` merges chapter-level `result.runtime_diagnostics` with per-attempt `attempt.runtime_diagnostics` into a flat tuple, and `_first_failed_runtime_diagnostic()` blindly picks the first collected row when it conflicts with chapter terminal status. The prior audit diagnostic (which is valid — the auditor DID complete) is being surfaced as the representative diagnostic, while the exception-originated timeout diagnostic is either not attached to the result or is lost during the merge.

This is a bug in `_exception_result()` / `_runtime_diagnostics_for_run()` interaction, not a design gap requiring new fields. The fix is likely: ensure `_exception_result()` writes the timeout diagnostic to `result.runtime_diagnostics` (not only to the attempt), or ensure `_first_failed_runtime_diagnostic()` prefers terminal-matching diagnostics when `stop_reason` is a provider/runtime reason.

The plan's proposed `diagnostic_consistency_status` field (Slice 1) is a useful *exposure* mechanism regardless, but it should be framed as "expose the existing bug and make it machine-checkable" rather than "reconcile a design-level attribution gap." The difference matters because a code bug can be fixed in a standard gate, while a design gap suggests heavier gate classification and longer timeline.

**Recommendation**: Keep Slice 1 as proposed, but reframe the Ch2 finding as "likely a diagnostic serialization code bug where prior audit diagnostics shadow terminal exception diagnostics" rather than "diagnostic attribution gap." This would justify a standard gate classification for the fix itself, with the consistency field as a defensive addition.

### F2 — `status_code` and `request_id` in safe evidence fields need explicit scoping

**Severity**: Minor

The plan lists `status_code` and `request_id` in Safe Evidence Fields. These are generally safe, but:

- `request_id` format varies by provider. Some providers encode account IDs, model names, or region info in request IDs. If the provider is ever switched, a new provider's request ID format could leak unexpected information.
- `status_code` is safe for standard HTTP codes (200, 400, 401, 429, 500, 503) but some providers return non-standard codes with embedded information.

The plan already has "provider base URL value" and "model value" in the Forbidden list, which shows awareness of provider-specific leakage. Adding explicit scoping for `request_id` and `status_code` would be consistent.

**Recommendation**: Add a note to Safe Evidence Fields: "`request_id` must be treated as opaque; if a provider's request_id format is found to embed account/model/region info, it must be moved to Forbidden. `status_code` must be standard HTTP status code integer only."

### F3 — Safe fields list omits `prompt_cost_diagnostic` and `anchor_cost_rows`

**Severity**: Minor

The 120s run's Ch5 runtime diagnostics include a `prompt_cost_diagnostic` field containing `anchor_cost_rows` (with `anchor_id`, `section_id`, `table_id`) and `fact_cost_rows` (with `fact_id`, `source_field_id`). These are already being serialized in the current artifact. The plan's Safe Evidence Fields list does not explicitly address whether `prompt_cost_diagnostic` payload contents are safe or forbidden.

Current code already serializes these fields, so this is not a regression. But if the plan is defining the authoritative safe/forbidden boundary for future work, it should explicitly cover `prompt_cost_diagnostic` sub-fields.

**Recommendation**: Add `prompt_cost_diagnostic` component fields (anchor_id, fact_id, section_id, source_field_id, character counts) to Safe Evidence Fields, or explicitly state that the existing per-diagnostic allowlist in `_runtime_diagnostic_payload` is the authoritative boundary.

### F4 — "diagnostic attribution gap" label risks premature gate classification

**Severity**: Minor

The plan's Inference label states: "the Ch2 discrepancy is a diagnostic attribution gap, not a proven provider-budget root cause." This is correct as a negative conclusion. But labeling it "attribution gap" rather than "serialization bug" could lead the next controller to classify the implementation gate as heavy (per the plan's recommendation), when a standard classification might suffice for a targeted serializer fix.

The plan's own code-inspection findings (line 29-32) show it inspected `_exception_result()`, `serialize_chapter_runtime_diagnostics()`, `_runtime_diagnostics_for_run()` — these are the exact functions where the bug likely lives. The fix scope is narrow: ensure terminal exception diagnostics are surfaced as the representative row when `stop_reason` is a provider/runtime reason.

**Recommendation**: The plan should note that the controller may choose `standard` classification for the implementation gate if the fix is narrowly scoped to the serializer/lineage functions without changing public CLI diagnostic semantics or retained artifact schema semantics in breaking ways.

### F5 — Ordering: Slice 1 before Slice 2 is defensible but should acknowledge the cost

**Severity**: Informational

The plan orders: (1) typed diagnostic serialization repair, (2) provider endpoint disposition. This is logically sound — fix the measurement instrument before measuring. However, it means that endpoint disposition evidence collection is blocked until serialization repair is reviewed and accepted.

Given that the current endpoint has already produced two retained runs with clear patterns (Ch2 auditor timeout at 758 tokens under 60s x2, Ch5 writer timeout at 2518 tokens under 60s x2), there is already some endpoint evidence available without serialization repair. The plan correctly notes this in Slice 2 ("allowed evidence: safe run metadata from retained artifacts"), but the gate dependency means endpoint disposition design cannot start until Slice 1 implementation is accepted.

**Recommendation**: No change needed. The ordering is correct. The plan already allows Slice 2 to use retained artifact metadata from existing runs. Acknowledging the timeline cost is sufficient.

### F6 — Future design vs current fact boundary is properly maintained

**Severity**: Informational (positive)

The plan consistently labels future design elements (PASS-only, split-audit, audit_focus, endpoint disposition) as "do not run now" or "design gate only." It does not write the 120s evidence as a basis for default changes. The "Required invariant" blocks are correctly framed as invariants to enforce, not as current implementation claims.

The plan's Non-goals section (line 9-10) explicitly lists prohibited changes. The Stop Conditions section (line 402-410) correctly covers the key risks including "Ch2 split, 0+9, 0+10, Agent runner/tool-loop, multi-year runtime, score-loop or provider default behavior is being written as current fact."

### F7 — PASS-only/split-audit deferral is correct

**Severity**: Informational (positive)

The plan defers PASS-only timing probe and split-audit probe to after serialization repair and endpoint disposition. This is correct because:

- PASS-only produces synthetic timing evidence that cannot prove report acceptance.
- Split-audit changes audit shape and could mask programmatic-first semantics if rushed.
- Both require better diagnostics before their evidence is interpretable.

The plan's "Deferred Probes" section (line 287-299) correctly labels these as future design with explicit prerequisites.

### F8 — Ch1/Ch4 volatility framing is correct

**Severity**: Informational (positive)

The plan correctly identifies Ch1/Ch4 cross-run acceptance volatility as evidence of LLM nondeterminism under strict evidence boundaries, not as evidence that the auditor should be relaxed. The Required invariant (line 99-100) states: "An accepted chapter in one live run does not invalidate a later fail-closed audit issue." This is the correct fail-closed stance.

The plan does not propose relaxing auditor rules, reducing repair budget, or accepting unsupported facets/inferences. This aligns with `AGENTS.md` fail-closed constraints.

## Summary

| # | Finding | Severity | Blocking? |
|---|---------|----------|-----------|
| F1 | Ch2 attribution gap may be code bug, not design gap | Major (advisory) | No |
| F2 | `status_code`/`request_id` need explicit scoping | Minor | No |
| F3 | `prompt_cost_diagnostic` sub-fields not in safe list | Minor | No |
| F4 | "Attribution gap" label risks heavy gate classification | Minor | No |
| F5 | Slice 1 before Slice 2 has timeline cost | Informational | No |
| F6 | Future design vs current fact boundary maintained | Informational (positive) | No |
| F7 | PASS-only/split-audit deferral correct | Informational (positive) | No |
| F8 | Ch1/Ch4 volatility framing correct | Informational (positive) | No |

## Gate Verdict

**PASS — no blocking findings.**

The plan is well-structured, same-source, and fail-closed. It correctly identifies the Ch2 diagnostic discrepancy, properly defers expensive live probes, maintains the future/current boundary, and does not authorize any default, auditor, template or runtime changes. The safe evidence contract is adequate for retained artifacts.

The one advisory finding (F1) suggests the Ch2 issue is more likely a serializer code bug than a design-level attribution gap. This does not block the design gate but should inform the next implementation gate's classification: if the fix is narrowly scoped to `_exception_result()` / `_runtime_diagnostics_for_run()` / `_first_failed_runtime_diagnostic()`, the implementation gate can be classified as `standard` rather than `heavy`.

## Recommended Follow-Up

1. The next controller should consider `standard` classification for the implementation gate if the fix scope stays within the serializer/lineage functions.
2. Add explicit scoping notes for `request_id` and `status_code` in Safe Evidence Fields.
3. Explicitly include or exclude `prompt_cost_diagnostic` sub-fields in the safe fields list.
4. Frame the implementation task as "fix diagnostic serialization bug where prior audit diagnostics shadow terminal exception diagnostics" with `diagnostic_consistency_status` as a defensive exposure mechanism.

## Artifact Path

`docs/reviews/mvp-llm-acceptance-volatility-diagnostic-evidence-reconciliation-design-plan-review-mimo-20260603.md`

## Secret Safety

This review contains no API key, Authorization header, Bearer token, cookie, password, provider base URL value, model value, raw prompt body, raw provider response, raw audit response, writer draft body, repair draft body, markdown report body, raw PDF text or raw parsed annual-report text.
