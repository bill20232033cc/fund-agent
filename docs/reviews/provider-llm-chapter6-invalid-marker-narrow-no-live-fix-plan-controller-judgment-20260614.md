# Provider/LLM Chapter 6 Invalid-marker Narrow No-live Fix Plan Controller Judgment

Date: 2026-06-14

Role: AgentController

Gate: `Provider/LLM Chapter 6 Invalid-marker Narrow No-live Fix Planning Gate`

Verdict: `ACCEPT_WITH_CONTROLLER_AMENDMENTS_READY_FOR_NARROW_NO_LIVE_FIX_IMPLEMENTATION_GATE_NOT_READY`

Release/readiness: `NOT_READY`

## 1. Scope

This controller judgment closes the Chapter 6 invalid-marker narrow no-live fix planning gate.

The gate is planning-only. It does not implement a fix, modify source/tests/runtime behavior, change prompt/runtime/provider defaults, change repair budget defaults, change source policy, run live/provider commands, open PR state, or claim readiness.

EID source policy remains single-source/no-fallback. Eastmoney, fund-company, CNINFO and other fallback routes remain out of scope.

## 2. Evidence Reviewed

| Evidence | Controller use |
|---|---|
| `AGENTS.md` | Rule truth: standard gate expectations, role boundaries, root-cause discipline, EID single-source/no-fallback and `NOT_READY` preservation. |
| `docs/design.md` | Design truth: Route C `--use-llm` is explicit opt-in and fail-closed; exact writer marker contract; full runtime/readiness remains future scope. |
| `docs/current-startup-packet.md` | Current active gate and checkpoint `10d9373`. |
| `docs/implementation-control.md` | Control truth: narrow no-live fix planning gate; no implementation/live by default. |
| `docs/reviews/provider-llm-chapter6-invalid-marker-no-live-diagnostic-evidence-controller-judgment-20260614.md` | Accepted diagnostic basis: D1-D3 proven, D4 repair-context gap proven. |
| `docs/reviews/provider-llm-chapter6-invalid-marker-narrow-no-live-fix-plan-20260614.md` | Plan under judgment. |
| `docs/reviews/provider-llm-chapter6-invalid-marker-narrow-no-live-fix-plan-review-ds-20260614.md` | Independent AgentDS review; verdict `ACCEPT_WITH_NONBLOCKING_AMENDMENTS`. |
| `docs/reviews/provider-llm-chapter6-invalid-marker-narrow-no-live-fix-plan-review-mimo-20260614.md` | Independent AgentMiMo review; verdict `ACCEPT`. |

No writer/auditor/repair markdown bodies, provider payloads, PDF/source/cache bodies, source bodies or final report bodies were read for this controller judgment.

No live/provider/LLM/network/PDF/FDR/source/acquisition/analyze/checklist/golden/readiness/release/PR commands were run for this controller judgment.

## 3. Accepted Plan Decision

Accepted implementation strategy:

```text
Add a Chapter 6-only writer-block retry path for writer:invalid_anchor_marker,
consuming the existing per-chapter content repair attempt budget.
```

Controller rationale:

1. D1 proves the initial Chapter 6 prompt already renders the exact marker contract and Chapter 6 bond-risk anchor boundary, so prompt-salience-only is not the strongest fix surface.
2. D4 proves the missing mechanism: `invalid_marker` writer blocks return before audit/repair, so no repair context exists today.
3. A budget-consuming writer-block retry closes the proven gap while preserving fail-closed behavior and repair-budget defaults.
4. Parser relaxation, budget increase, source/fallback/provider work, readiness and PR movement remain rejected.

## 4. Review Disposition

| Review source | Finding | Controller disposition |
|---|---|---|
| AgentDS | Strategy is evidence-based and directly closes the D4-proven gap. | `ACCEPT` |
| AgentDS | Budget semantics are explicit, but successful writer-block retry consumes budget that would otherwise be available for audit repair if a retried draft later fails audit. | `ACCEPT_NONBLOCKING_AMENDMENT_BIND_TO_IMPLEMENTATION` |
| AgentDS | Tests 3 and 4 are regression guards, not red-before-green tests. | `ACCEPT_NONBLOCKING_AMENDMENT_BIND_TO_IMPLEMENTATION` |
| AgentDS | Implementation should ensure `continue` lands at the top of the existing loop after interruption checks. | `ACCEPT_NONBLOCKING_AMENDMENT_BIND_TO_IMPLEMENTATION` |
| AgentMiMo | Strategy, write set, red-test-first sequence and Chapter 6-only scope all pass. | `ACCEPT` |
| AgentMiMo | No blocking or non-blocking amendments required. | `ACCEPT` |

No reviewer finding requires plan rewrite. The DS amendments are binding implementation-gate clarifications.

## 5. Binding Controller Amendments

The implementation gate must apply these amendments:

1. Label tests for `max_content_repair_attempts=0` and non-Chapter-6 `invalid_marker` as regression guards, not red-before-green tests. They should be written before implementation and remain green.
2. Add a short source comment at the writer-block retry branch explaining that the retry consumes existing content repair budget; if the retry later reaches audit and fails audit, no extra audit repair is available under default budget `1`.
3. Ensure the retry branch uses the existing `while True` loop and `continue` lands at the top of the loop so interruption checks still run before the next writer call.
4. Keep the implementation Chapter 6-only and issue-prefix-specific: `writer:invalid_anchor_marker`.
5. Do not modify repair-budget defaults, parser acceptance syntax, provider defaults, source policy, readiness/release/PR state, or any source/fallback path.

## 6. Accepted / Rejected / Deferred Table

| Item | Disposition | Reason |
|---|---|---|
| Chapter 6-only writer-block retry for `writer:invalid_anchor_marker`. | `ACCEPT` | Narrowly closes D4-proven gap. |
| Consume existing per-chapter content repair attempt budget. | `ACCEPT` | Preserves defaults; implementation must document budget interaction. |
| Prompt salience only. | `REJECT_FOR_NEXT_ENTRY` | D1 already proves exact marker contract is rendered; D4 gap remains unclosed. |
| Prompt salience plus writer-block retry. | `REJECT_AS_OVERBROAD_FOR_NEXT_ENTRY` | Current evidence supports retry path without prompt duplication. |
| Parser relaxation or alternate marker syntax. | `REJECT` | Exact marker contract is accepted; D2 proves taxonomy works. |
| Generalize retry to all chapters. | `DEFER` | Current accepted failure is Chapter 6-specific; generalization requires future evidence. |
| Increase repair budget defaults. | `REJECT` | Budget calibration is a separate future gate. |
| Source/fallback/provider/readiness/PR work. | `REJECT` | Out of scope and unrelated to pre-provider writer-marker failure. |

## 7. Accepted Implementation Gate

Next entry point:

```text
Provider/LLM Chapter 6 Invalid-marker Narrow No-live Fix Implementation Gate
```

Allowed implementation write set:

- `fund_agent/agent/repair.py`
- `fund_agent/agent/runner.py`
- `tests/agent/test_repair_policy.py`
- `tests/agent/test_runner.py`
- `tests/services/test_chapter_orchestrator.py`
- `tests/fund/test_chapter_writer.py`

Conditional write:

- `tests/services/test_fund_analysis_service_llm.py` only if implementation changes Service-level incomplete-run or final-assembly diagnostics.

Implementation gate must begin with fake-input no-live tests and record red/green status according to the accepted plan plus controller amendments.

Minimum verification:

```text
uv run pytest -q tests/agent/test_repair_policy.py tests/agent/test_runner.py tests/services/test_chapter_orchestrator.py tests/fund/test_chapter_writer.py
uv run ruff check fund_agent/agent/repair.py fund_agent/agent/runner.py tests/agent/test_repair_policy.py tests/agent/test_runner.py tests/services/test_chapter_orchestrator.py tests/fund/test_chapter_writer.py
git diff --check
```

No live/provider/network/PDF/FDR/source/acquisition/analyze/checklist/golden/readiness/release/PR commands are part of the implementation verification.

## 8. Control-doc Update Recommendation

After this judgment is checkpointed, update `docs/current-startup-packet.md` and `docs/implementation-control.md`:

- current active gate: `Provider/LLM Chapter 6 Invalid-marker Narrow No-live Fix Implementation Gate`
- accepted plan checkpoint: this judgment and the plan/review artifacts
- release/readiness: `NOT_READY`
- non-goals: no live/provider, no parser relaxation, no budget default change, no source fallback, no provider default change, no PR/release/readiness state change

## 9. Final Verdict

`VERDICT: ACCEPT_WITH_CONTROLLER_AMENDMENTS_READY_FOR_NARROW_NO_LIVE_FIX_IMPLEMENTATION_GATE_NOT_READY`

Stop condition for this gate: satisfied after control docs are synchronized and the scoped accepted checkpoint is committed.
