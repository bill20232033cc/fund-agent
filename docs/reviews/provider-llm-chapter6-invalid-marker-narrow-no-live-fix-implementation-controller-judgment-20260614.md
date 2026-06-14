# Provider/LLM Chapter 6 Invalid-marker Narrow No-live Fix Implementation Controller Judgment

Date: 2026-06-14

Role: AgentController

Gate: `Provider/LLM Chapter 6 Invalid-marker Narrow No-live Fix Implementation Gate`

Verdict: `ACCEPT_IMPLEMENTATION_NOT_READY`

Release/readiness: `NOT_READY`

## 1. Scope

This judgment closes only the no-live implementation gate for the accepted Chapter 6 invalid-marker fix.

Accepted implementation scope:

- Add a Chapter 6-only writer-block retry path for `writer:invalid_anchor_marker`.
- Consume the existing content repair budget.
- Preserve exact anchor marker syntax and parser fail-closed behavior.
- Preserve budget defaults, provider defaults, source policy, fallback policy, readiness, release and PR state.

Out of scope:

- Live/provider/LLM evidence.
- Source acquisition or fallback changes.
- Parser syntax relaxation.
- Repair-budget calibration.
- Generalizing this retry beyond Chapter 6.
- Readiness/release/PR claims.

## 2. Evidence Reviewed

- Plan controller judgment: `docs/reviews/provider-llm-chapter6-invalid-marker-narrow-no-live-fix-plan-controller-judgment-20260614.md`
- Implementation evidence: `docs/reviews/provider-llm-chapter6-invalid-marker-narrow-no-live-fix-implementation-evidence-20260614.md`
- DS review: `docs/reviews/provider-llm-chapter6-invalid-marker-narrow-no-live-fix-implementation-review-ds-20260614.md`
- MiMo review: `docs/reviews/provider-llm-chapter6-invalid-marker-narrow-no-live-fix-implementation-review-mimo-20260614.md`
- Controller local validation:
  - `uv run pytest -q tests/agent/test_repair_policy.py tests/agent/test_runner.py tests/services/test_chapter_orchestrator.py tests/fund/test_chapter_writer.py`
  - `uv run ruff check fund_agent/agent/repair.py fund_agent/agent/runner.py tests/agent/test_repair_policy.py tests/agent/test_runner.py tests/services/test_chapter_orchestrator.py tests/fund/test_chapter_writer.py`
  - `git diff --check`
  - `git status --branch --short`

## 3. Accepted Current Facts

| Fact | Disposition | Basis |
|---|---|---|
| The implementation adds a Chapter 6-only retry for writer-blocked invalid anchor marker output. | ACCEPT | `fund_agent/agent/runner.py` predicate gates on `chapter_id == 6`, blocked writer status, `llm_contract_violation`, `writer:invalid_anchor_marker` issue prefix and remaining content repair budget. |
| The retry consumes existing content repair budget and does not change defaults. | ACCEPT | `attempt_index += 1` is used before rebuilding writer input; no default policy values are changed; source comment documents the budget interaction. |
| The retry re-enters the existing `while True` loop before the next writer call. | ACCEPT | Implementation uses `continue`, so existing interruption checks run before retry generation. |
| Exact marker syntax is preserved. | ACCEPT | Repair context guidance says to use exact `<!-- anchor:<anchor_id> -->`; parser files were not changed. |
| Budget `0` and non-Chapter-6 invalid-marker paths remain fail-closed after one writer call. | ACCEPT | Covered by runner and service tests. |
| Provider/source/fallback/readiness/release/PR state is unchanged. | ACCEPT | Diff scope excludes those modules and control state remains `NOT_READY`. |

## 4. Review Disposition

| Reviewer | Verdict | Controller disposition |
|---|---|---|
| DS | `PASS` | ACCEPT. DS verified all nine accepted behavior items, all five controller amendments, focused tests, ruff and `git diff --check`. |
| MiMo | `PASS` | ACCEPT. MiMo independently verified the narrow predicate, budget arithmetic, loop behavior, exact syntax preservation, regression guards and validation commands. |

No blocking findings were raised by either reviewer.

## 5. Controller Validation

Controller reran the accepted no-live validation matrix.

```text
$ uv run pytest -q tests/agent/test_repair_policy.py tests/agent/test_runner.py tests/services/test_chapter_orchestrator.py tests/fund/test_chapter_writer.py
163 passed in 0.82s
```

```text
$ uv run ruff check fund_agent/agent/repair.py fund_agent/agent/runner.py tests/agent/test_repair_policy.py tests/agent/test_runner.py tests/services/test_chapter_orchestrator.py tests/fund/test_chapter_writer.py
All checks passed!
```

```text
$ git diff --check
(no output; passed)
```

`git status --branch --short` shows the branch ahead of origin and confirms this gate's tracked implementation changes are limited to:

- `fund_agent/agent/repair.py`
- `fund_agent/agent/runner.py`
- `tests/agent/test_repair_policy.py`
- `tests/agent/test_runner.py`
- `tests/fund/test_chapter_writer.py`
- `tests/services/test_chapter_orchestrator.py`

Pre-existing tracked diffs in `AGENTS.md`, `README.md` and `docs/design.md`, plus historical untracked residue, are not accepted by this gate.

## 6. Accepted / Rejected / Residual Table

| Item | Judgment | Rationale |
|---|---|---|
| Chapter 6 `writer:invalid_anchor_marker` writer-block retry | ACCEPT | Directly addresses the accepted no-live root cause without relaxing marker syntax. |
| Existing content repair budget consumption | ACCEPT | Matches plan amendments and avoids hidden budget expansion. |
| Parser relaxation | REJECT | Current contract remains exact marker syntax only. |
| General invalid-marker retry for other chapters | DEFER | Out of current narrow gate; non-Chapter-6 remains fail-closed. |
| Repair-budget calibration | DEFER | Product policy decision for later standard gate. |
| Live/provider success claim | DEFER | No live/provider command was run in this gate. |
| Readiness/release/PR claim | REJECT | Evidence remains no-live and scoped; release/readiness remains `NOT_READY`. |

## 7. Residuals

- This no-live implementation does not prove a future live/provider Chapter 6 sample will pass.
- If retry output still contains invalid marker syntax, Chapter 6 remains fail-closed after the existing budget is consumed.
- Default repair budget calibration remains a future standard gate.
- Generalizing invalid-marker retry beyond Chapter 6 remains deferred.
- Existing unrelated workspace diffs and historical untracked residue remain outside this gate.

## 8. Next Entry Recommendation

Recommended next entry:

`Provider/LLM Chapter 6 Invalid-marker Narrow No-live Fix Accepted Checkpoint and Control Sync Gate`

Purpose:

- Stage only accepted implementation files and current gate artifacts.
- Create a local accepted checkpoint commit.
- Sync `docs/current-startup-packet.md` and `docs/implementation-control.md` to record the accepted implementation checkpoint and route to the next controlled evidence gate.

Deferred entries:

- Bounded live Chapter 6 re-evidence gate.
- Repair budget calibration gate.
- Docling/parser benchmark gate.
- Readiness/release/PR external-state gates.

## 9. Final Verdict

`VERDICT: ACCEPT_IMPLEMENTATION_NOT_READY`

The implementation satisfies the accepted plan and controller amendments, has two independent `PASS` reviews, and passes the focused no-live validation matrix. It is accepted as a local implementation fact after checkpointing. It does not change release/readiness: `NOT_READY` remains the controlling state.
