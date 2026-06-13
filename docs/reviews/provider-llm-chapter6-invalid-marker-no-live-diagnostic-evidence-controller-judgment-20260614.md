# Provider/LLM Chapter 6 Invalid-marker No-live Diagnostic Evidence Controller Judgment

Date: 2026-06-14

Role: AgentController

Gate: `Provider/LLM Chapter 6 Invalid-marker No-live Diagnostic Evidence Gate`

Verdict: `ACCEPT_READY_FOR_NARROW_NO_LIVE_FIX_PLANNING_GATE_NOT_READY`

Release/readiness: `NOT_READY`

## 1. Scope

This controller judgment closes the Chapter 6 invalid-marker no-live diagnostic evidence gate.

The gate is evidence-only. It does not implement a fix, modify source/tests/runtime behavior, change prompt/runtime/provider defaults, change repair budget, change EID source policy, run live/provider commands, open PR state, or claim readiness.

EID source policy remains single-source/no-fallback. Eastmoney, fund-company, CNINFO and other fallback routes remain out of scope.

## 2. Evidence Reviewed

| Evidence | Controller use |
|---|---|
| `AGENTS.md` | Rule truth: standard gate expectations, root-cause discipline, EID single-source/no-fallback and `NOT_READY` preservation. |
| `docs/design.md` | Design truth: Route C `--use-llm` is explicit opt-in and fail-closed; writer marker contract is exact; full runtime/readiness remains future scope. |
| `docs/current-startup-packet.md` | Current active gate and checkpoint `6afe67e`. |
| `docs/implementation-control.md` | Control truth: D1-D5 no-live evidence gate, no implementation/live by default. |
| `docs/reviews/provider-llm-chapter6-invalid-marker-live-blocker-disposition-plan-controller-judgment-20260614.md` | Accepted routing basis for this evidence gate. |
| `docs/reviews/provider-llm-chapter6-invalid-marker-no-live-diagnostic-evidence-20260614.md` | Evidence artifact under judgment. |
| `docs/reviews/provider-llm-chapter6-invalid-marker-no-live-diagnostic-evidence-review-ds-20260614.md` | Independent AgentDS review; verdict `ACCEPT`. |
| `docs/reviews/provider-llm-chapter6-invalid-marker-no-live-diagnostic-evidence-review-mimo-20260614.md` | Independent AgentMiMo review; verdict `ACCEPT`. |

No writer/auditor/repair markdown bodies, provider payloads, PDF/source/cache bodies, source bodies or final report bodies were read for this controller judgment.

No live/provider/LLM/network/PDF/FDR/source/acquisition/analyze/checklist/golden/readiness/release/PR commands were run for this controller judgment.

## 3. Accepted Diagnostic Facts

| Diagnostic item | Controller disposition |
|---|---|
| D1 prompt contract rendering | `ACCEPT_PROVEN_NO_LIVE`: Chapter 6 prompt rendering includes exact `<!-- anchor:<anchor_id> -->` syntax, allowed-anchor boundary language, prohibition on synthesized IDs and Chapter 6 bond-risk internal/组级 anchor prohibition. |
| D2 validator taxonomy | `ACCEPT_PROVEN_NO_LIVE`: malformed anchor comments route to `invalid_marker` / `llm_contract_violation`; syntactically valid but unauthorized anchor IDs route to `unknown_anchor`. |
| D3 diagnostic payload mapping | `ACCEPT_PROVEN_NO_LIVE`: `writer:invalid_anchor_marker` contributes to `invalid_marker_count`; safe diagnostics strip raw suffixes and do not leak malformed marker text. |
| D4 repair-context specificity | `ACCEPT_PROVEN_GAP`: current `invalid_marker` writer block returns before audit/repair, so no invalid-marker repair context exists today. Existing generic repair wording does not provide exact marker syntax for this pre-audit blocker. |
| D5 boundary preservation | `ACCEPT`: evidence used no-live reads/tests/fake snippets only; no source/test/runtime modifications, no body reads, no live/provider/source/fallback/readiness/release/PR command. |

## 4. Review Disposition

| Review source | Finding | Controller disposition |
|---|---|---|
| AgentDS | Evidence artifact stayed within allowed boundaries. | `ACCEPT` |
| AgentDS | D1-D3 are independently verified against current code; D4 gap is correctly classified. | `ACCEPT` |
| AgentDS | Recommendation to proceed to narrow no-live fix planning is supported. | `ACCEPT` |
| AgentDS | Failed snippet is represented honestly as no-value process output and not used as proof. | `ACCEPT` |
| AgentMiMo | All five review questions pass; D1-D4 are proven by no-live code/tests/snippets. | `ACCEPT` |
| AgentMiMo | Test count discrepancy is a non-blocking clarity issue: seven named test selections can yield twelve passed tests due to parametrization. | `ACCEPT_NONBLOCKING_CLARITY_RESIDUAL` |

No reviewer finding requires evidence rewrite. No reviewer finding authorizes implementation.

## 5. Accepted / Rejected / Residual Table

| Item | Disposition | Reason |
|---|---|---|
| Current strongest root-cause category remains LLM output-format noncompliance with exact anchor marker contract. | `ACCEPT` | D1-D3 show the contract exists, taxonomy works and diagnostics are safe; live blocker remains a writer output-format issue. |
| Current `invalid_marker` repair-context gap. | `ACCEPT` | D4 proves writer parse blocks before audit/repair, so no repair context exists for this blocker today. |
| Direct implementation from this evidence gate. | `REJECT` | Evidence gate did not decide a fix design; next step must choose prompt salience, writer-block repair/retry path, or both. |
| Additional no-live diagnostic evidence before planning. | `REJECT_FOR_NEXT_ENTRY` | D1-D5 are sufficient for planning; both reviewers accepted. |
| Additional bounded live evidence before planning. | `REJECT_FOR_NEXT_ENTRY` | The remaining question is no-live fix design, not another provider occurrence. |
| Parser relaxation. | `REJECT_FOR_NEXT_ENTRY` | D2 proves current strict parser taxonomy is working as designed under the exact marker contract. |
| Source/fallback investigation. | `REJECT` | The blocker is pre-provider writer marker parsing, not annual-report acquisition. |
| Readiness / MVP-ready / LLM-path-ready claim. | `REJECT` | Current Route C sample still has an accepted fail-closed blocker and final assembly is not proven complete. |

## 6. Accepted Next Gate

Next entry point:

```text
Provider/LLM Chapter 6 Invalid-marker Narrow No-live Fix Planning Gate
```

Planning constraints:

- No implementation in the planning gate.
- Preserve exact anchor marker contract unless a separate product/contract gate accepts syntax relaxation.
- Keep scope to Chapter 6 invalid-marker output-format guardrails.
- Decide whether the later fix should strengthen initial Chapter 6 writer prompt salience, add a writer-block repair/retry path for `invalid_marker`, or both.
- Require red/fake-input no-live tests before any implementation.
- Preserve EID single-source/no-fallback, provider defaults, repair budget, annual-period LLM route, Docling/source policy, release/readiness and PR state.

## 7. Control-doc Update Recommendation

After this judgment is checkpointed, update `docs/current-startup-packet.md` and `docs/implementation-control.md`:

- current active gate: `Provider/LLM Chapter 6 Invalid-marker Narrow No-live Fix Planning Gate`
- accepted evidence checkpoint: this judgment and the evidence/review artifacts
- release/readiness: `NOT_READY`
- non-goals: no implementation until plan accepted, no live/provider, no parser relaxation by default, no source fallback, no provider default or repair-budget change, no PR/release/readiness state change

## 8. Final Verdict

`VERDICT: ACCEPT_READY_FOR_NARROW_NO_LIVE_FIX_PLANNING_GATE_NOT_READY`

Stop condition for this gate: satisfied after control docs are synchronized and the scoped accepted checkpoint is committed.
