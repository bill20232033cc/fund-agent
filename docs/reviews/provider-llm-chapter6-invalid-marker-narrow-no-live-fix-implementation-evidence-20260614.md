# Provider/LLM Chapter 6 Invalid-marker Narrow No-live Fix Implementation Evidence

Date: 2026-06-14

Role: AgentCodex implementation worker, not controller.

Gate: `Provider/LLM Chapter 6 Invalid-marker Narrow No-live Fix Implementation Gate`

Verdict: `IMPLEMENTED_NO_LIVE_NOT_READY`

Release/readiness: `NOT_READY`

## 1. Scope Implemented

Implemented only the accepted Chapter 6 writer-block retry for `writer:invalid_anchor_marker`.

Production changes:

- `fund_agent/agent/repair.py`
  - Added `repair_context_from_writer_invalid_marker()`.
  - Builds `ChapterRepairContext` from writer invalid-anchor issues.
  - Keeps safe issue ids, sanitizes messages, removes raw malformed HTML marker comments, and injects exact syntax guidance for `<!-- anchor:<anchor_id> -->`.
- `fund_agent/agent/runner.py`
  - Added a writer-block retry branch before the existing terminal writer-block return.
  - Eligibility is limited to all of:
    - `chapter_id == 6`
    - `writer_result.status == "blocked"`
    - `writer_result.stop_reason == "llm_contract_violation"`
    - issue id starts with `writer:invalid_anchor_marker`
    - remaining content repair budget is greater than `0`
  - Appends the failed attempt, records repair phase events, increments `attempt_index`, rebuilds writer input with repair context, and uses `continue` to re-enter the existing `while True` loop.
  - Added a source comment documenting that this consumes the same content repair budget used by audit repair.

Tests changed:

- `tests/agent/test_repair_policy.py`
- `tests/agent/test_runner.py`
- `tests/services/test_chapter_orchestrator.py`
- `tests/fund/test_chapter_writer.py`

No conditional Service-level diagnostics test was changed.

## 2. Red / Regression Baseline Before Source Changes

Command:

```text
uv run pytest -q tests/agent/test_repair_policy.py tests/agent/test_runner.py tests/services/test_chapter_orchestrator.py tests/fund/test_chapter_writer.py
```

Result before source changes:

```text
4 failed, 159 passed in 0.86s
```

Expected red failures:

- `tests/agent/test_repair_policy.py::test_writer_invalid_anchor_repair_context_is_sanitized_and_exact`
  - failed because `repair_context_from_writer_invalid_marker` did not exist.
- `tests/agent/test_runner.py::test_chapter_6_invalid_anchor_marker_retries_once_and_accepts`
  - failed because current runner returned blocked after one writer call.
- `tests/agent/test_runner.py::test_chapter_6_invalid_anchor_marker_twice_fails_closed_after_one_retry`
  - failed because current runner called writer once, not twice.
- `tests/services/test_chapter_orchestrator.py::test_chapter_6_invalid_anchor_marker_retries_and_accepts`
  - failed because orchestration delegated to the current one-call blocked runner behavior.

Regression guards were green before implementation:

- Chapter 6 budget `0` invalid marker kept one writer call.
- Non-Chapter-6 invalid marker kept one writer call.
- Repair-context renderer could render exact correction text through existing `ChapterRepairContext`.

## 3. Green Validation After Implementation

Command:

```text
uv run pytest -q tests/agent/test_repair_policy.py tests/agent/test_runner.py tests/services/test_chapter_orchestrator.py tests/fund/test_chapter_writer.py
```

Result:

```text
163 passed in 0.88s
```

Command:

```text
uv run ruff check fund_agent/agent/repair.py fund_agent/agent/runner.py tests/agent/test_repair_policy.py tests/agent/test_runner.py tests/services/test_chapter_orchestrator.py tests/fund/test_chapter_writer.py
```

Result:

```text
All checks passed!
```

Command:

```text
git diff --check
```

Result: passed with no output.

## 4. Behavior Evidence

Covered behavior:

- Chapter 6 first invalid marker then valid retry:
  - writer called exactly twice.
  - second request carries `repair_context.attempt_index == 1`.
  - repair context includes exact `<!-- anchor:<anchor_id> -->` correction.
  - chapter is accepted after the second valid output.
- Chapter 6 invalid marker twice:
  - writer called exactly twice with default content repair budget `1`.
  - second failure remains fail-closed.
  - no hidden third retry.
- Chapter 6 budget `0`:
  - writer called once.
  - fail-closed behavior preserved.
- Non-Chapter-6 invalid marker:
  - writer called once.
  - no retry branch taken.
- Helper sanitization:
  - keeps safe `writer:invalid_anchor_marker:*` issue ids.
  - removes raw malformed marker text such as `<!-- ANCHOR:bad -->`.
  - redacts sensitive strings already covered by existing sanitization.
  - injects exact syntax and Chapter 6 bond-risk anchor boundary correction.
- Service orchestration:
  - `orchestrate_chapters()` accepts Chapter 6 when first invalid marker is followed by valid retry.
  - budget `0` remains one-call fail-closed.
- Renderer contract:
  - existing writer prompt renderer carries exact correction text from `ChapterRepairContext`.

## 5. Boundary Confirmation

Confirmed not changed:

- Parser acceptance syntax.
- `<!-- anchor:<anchor_id> -->` marker contract.
- Repair budget defaults.
- Provider/runtime defaults.
- Source/FDR/PDF/cache/fallback policy.
- EID single-source/no-fallback policy.
- Annual-period LLM route.
- Golden/readiness/release/PR state.
- README, `docs/design.md`, `docs/current-startup-packet.md`, `docs/implementation-control.md`.

Commands not run:

- live/provider/LLM/network/PDF/FDR/source/acquisition/analyze/checklist/golden/readiness/release/PR commands.
- stage/commit/push/PR commands.

Working tree note:

- `git status --short` showed pre-existing modified/untracked files outside this gate, including `AGENTS.md`, `README.md`, `docs/design.md`, and multiple residue paths.
- This implementation did not modify those unrelated files.

## 6. Residuals

- This no-live fix does not prove any future provider/live Chapter 6 sample will pass.
- If the retry also emits invalid marker syntax, Chapter 6 remains fail-closed after the existing budget is consumed.
- The current default content repair budget remains uncalibrated product policy and is still a future standard gate.
- Generalizing invalid-marker retry beyond Chapter 6 remains deferred.
- Release/readiness remains `NOT_READY`.

## 7. Final Verdict

`VERDICT: IMPLEMENTATION_COMPLETE_NO_LIVE_NOT_READY`

Stop condition satisfied for this implementation worker: implementation and evidence artifact written; no controller judgment, control-doc update, commit, PR, release, readiness, live/provider/source action performed.
