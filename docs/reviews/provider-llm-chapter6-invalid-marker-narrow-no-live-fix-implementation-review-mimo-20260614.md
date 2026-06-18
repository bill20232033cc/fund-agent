# Provider/LLM Chapter 6 Invalid-marker Narrow No-live Fix Implementation Review

Date: 2026-06-14

Role: AgentMiMo implementation reviewer, not controller.

Gate: `Provider/LLM Chapter 6 Invalid-marker Narrow No-live Fix Implementation Gate`

Verdict: `PASS`

Release/readiness: `NOT_READY`

## 1. Scope

Review mode: current changes (uncommitted workspace diff).

Base: `main` (branch `feat/mvp-llm-incomplete-run-artifacts`).

Included scope:

- `fund_agent/agent/repair.py`
- `fund_agent/agent/runner.py`
- `tests/agent/test_repair_policy.py`
- `tests/agent/test_runner.py`
- `tests/services/test_chapter_orchestrator.py`
- `tests/fund/test_chapter_writer.py`

Excluded scope:

- Pre-existing tracked diffs: `AGENTS.md`, `README.md`, `docs/design.md`
- Historical untracked residue outside this gate
- Live/provider/source/readiness/release/PR commands

## 2. Findings

未发现实质性问题。

Implementation exactly matches the accepted plan and all five controller amendments.

## 3. Acceptance Verification

### 3.1 Accepted Behavior Checklist

| # | Accepted behavior | Status | Evidence |
|---|---|---|---|
| 1 | retry is Chapter 6-only | PASS | `runner.py:678-679`: `if chapter_id != 6: return False` is the first guard in `_should_retry_writer_invalid_marker`. |
| 2 | writer_result.status == "blocked" | PASS | `runner.py:680-681`: `if writer_result.status != "blocked": return False`. |
| 3 | stop_reason == "llm_contract_violation" | PASS | `runner.py:682-683`: `if writer_result.stop_reason != "llm_contract_violation": return False`. |
| 4 | issue id prefix writer:invalid_anchor_marker | PASS | `runner.py:686-689`: `any(issue.issue_id.startswith("writer:invalid_anchor_marker") for issue in writer_result.issues)`. |
| 5 | consumes existing content repair budget without changing defaults | PASS | `runner.py:397-398`: source comment documents budget interaction. `runner.py:399`: `attempt_index += 1` consumes budget. Default `max_content_repair_attempts=1` unchanged (`runner.py:111`). |
| 6 | branch continues through existing while loop so interruption checks run before next writer call | PASS | `runner.py:409`: `continue` re-enters `while True` loop at `runner.py:330`, which immediately runs `_check_interruption` at `runner.py:331-338`. |
| 7 | exact marker syntax is preserved; parser is not relaxed | PASS | `repair.py:30-34`: `_WRITER_INVALID_ANCHOR_CORRECTION` preserves exact `<!-- anchor:<anchor_id> -->` syntax. No parser changes in diff. |
| 8 | budget 0 and non-Chapter-6 remain one-call fail-closed | PASS | `runner.py:678-679` blocks non-Chapter-6. `runner.py:684-685` blocks budget 0. Tests `test_chapter_6_invalid_anchor_marker_budget_zero_does_not_retry` and `test_non_chapter_6_invalid_anchor_marker_does_not_retry` verify exactly 1 writer call. |
| 9 | no provider/source/fallback/readiness/release/PR behavior change | PASS | Diff touches only `repair.py` and `runner.py` within the accepted write set. No provider, source, fallback, readiness, release or PR code modified. |

### 3.2 Controller Amendment Verification

| # | Amendment | Status | Evidence |
|---|---|---|---|
| 1 | Label regression-guard tests | PASS | `test_runner.py:579-599` (budget 0) and `test_runner.py:602-622` (non-Chapter-6) are labeled as regression guards in docstrings. These were green before implementation and remain green. |
| 2 | Source comment at writer-block retry branch explaining budget consumption | PASS | `runner.py:397-398`: `# Writer-block retry consumes the same content repair budget that audit repair would use. / # With default budget 1, a successful retry does not leave an extra audit repair attempt.` |
| 3 | Ensure retry branch uses existing while True loop and continue lands at top | PASS | `runner.py:409`: `continue` re-enters `while True` at `runner.py:330`. Interruption check runs at `runner.py:331-338` before next writer call. |
| 4 | Keep Chapter 6-only and issue-prefix-specific | PASS | `_should_retry_writer_invalid_marker` enforces `chapter_id == 6` and `issue.issue_id.startswith("writer:invalid_anchor_marker")`. |
| 5 | Do not modify repair-budget defaults, parser syntax, provider defaults, source policy, readiness/release/PR state | PASS | No changes to `AgentRepairPolicy` defaults, parser, provider, source, readiness or PR code. |

### 3.3 Implementation Correctness Walk-through

**Production code path (`runner.py:379-409`)**:

1. Writer returns `status == "blocked"`.
2. Terminal state computed from stop_reason.
3. Attempt appended with terminal state.
4. `_should_retry_writer_invalid_marker` evaluates all five guards.
5. If eligible: phase events recorded, `attempt_index` incremented, writer input rebuilt with `repair_context_from_writer_invalid_marker`, `continue` re-enters loop.
6. If not eligible: existing terminal `ChapterTask` return path unchanged.

**Repair context construction (`repair.py:178-208`)**:

1. Filters issues to only `writer:invalid_anchor_marker` prefix.
2. Sanitizes messages via `_sanitize_writer_issue_message` which strips HTML comments before standard sanitization.
3. Injects exact `_WRITER_INVALID_ANCHOR_CORRECTION` guidance.
4. Returns `ChapterRepairContext` compatible with existing prompt renderer.

**Budget arithmetic**:

- Default `max_content_repair_attempts=1`.
- First writer call: `attempt_index=0`, `remaining_budget=1-0=1` > 0, eligible.
- After retry: `attempt_index=1`, `remaining_budget=1-1=0`, not eligible.
- Second failure returns terminal without hidden third retry.

### 3.4 Red/Green Baseline

Evidence artifact confirms:

- Red (before implementation): 4 failed, 159 passed. The 4 failures are exactly the 4 new tests that require the new code.
- Green (after implementation): 163 passed. All 4 new tests now pass.
- Regression guards (budget 0, non-Chapter-6, renderer contract): green before and after.

## 4. Validation Commands and Results

```text
$ uv run pytest -q tests/agent/test_repair_policy.py tests/agent/test_runner.py tests/services/test_chapter_orchestrator.py tests/fund/test_chapter_writer.py
163 passed in 1.09s

$ uv run ruff check fund_agent/agent/repair.py fund_agent/agent/runner.py tests/agent/test_repair_policy.py tests/agent/test_runner.py tests/services/test_chapter_orchestrator.py tests/fund/test_chapter_writer.py
All checks passed!

$ git diff --check
(no output - clean)

$ git status --short
 M fund_agent/agent/repair.py
 M fund_agent/agent/runner.py
 M tests/agent/test_repair_policy.py
 M tests/agent/test_runner.py
 M tests/services/test_chapter_orchestrator.py
 M tests/fund/test_chapter_writer.py
```

Only the 6 accepted implementation files are modified. Pre-existing tracked diffs (`AGENTS.md`, `README.md`, `docs/design.md`) are outside this gate's write set.

## 5. Open Questions

无。

## 6. Residual Risk

- The no-live fix does not prove any future provider/live Chapter 6 sample will pass. If the retried writer also emits invalid marker syntax, Chapter 6 remains fail-closed after budget exhaustion.
- The default content repair budget (`max_content_repair_attempts=1`) is not calibrated as a product default; calibration remains a future standard gate.
- Generalizing invalid-marker retry beyond Chapter 6 remains deferred.
- If the writer-block retry succeeds but the subsequent audit fails, no extra audit repair attempt is available under default budget 1. This is the intended documented trade-off.
- Release/readiness remains `NOT_READY`.

## 7. Final Verdict

`VERDICT: PASS`

Implementation correctly and narrowly implements the Chapter 6-only writer-block retry for `writer:invalid_anchor_marker`, consuming the existing content repair budget, preserving exact marker syntax, maintaining fail-closed behavior for budget 0 and non-Chapter-6 cases, and applying all five controller amendments. All 163 tests pass, ruff is clean, and no files outside the accepted write set are modified.

Stop condition satisfied: review artifact written. No source/tests/control/design/README modification performed.
