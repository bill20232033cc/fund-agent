# Provider/LLM Chapter 6 Invalid-marker Narrow No-live Fix Implementation Review DS

Date: 2026-06-14

Role: AgentDS implementation reviewer, not controller.

Gate: `Provider/LLM Chapter 6 Invalid-marker Narrow No-live Fix Implementation Gate`

Verdict: `PASS`

## 1. Review Scope

Reviewed only the implementation diff against the accepted behavior items and controller amendments from `docs/reviews/provider-llm-chapter6-invalid-marker-narrow-no-live-fix-plan-controller-judgment-20260614.md`.

Production files reviewed:
- `fund_agent/agent/repair.py`
- `fund_agent/agent/runner.py`

Test files reviewed:
- `tests/agent/test_repair_policy.py`
- `tests/agent/test_runner.py`
- `tests/services/test_chapter_orchestrator.py`
- `tests/fund/test_chapter_writer.py`

Pre-existing unrelated diffs (`AGENTS.md`, `README.md`, `docs/design.md`) and untracked residue were ignored per gate instructions.

## 2. Validation Commands and Results

```text
$ uv run pytest -q tests/agent/test_repair_policy.py tests/agent/test_runner.py tests/services/test_chapter_orchestrator.py tests/fund/test_chapter_writer.py
163 passed in 1.08s

$ uv run ruff check fund_agent/agent/repair.py fund_agent/agent/runner.py tests/agent/test_repair_policy.py tests/agent/test_runner.py tests/services/test_chapter_orchestrator.py tests/fund/test_chapter_writer.py
All checks passed!

$ git diff --check
(no output — passed)

$ git status --short
M fund_agent/agent/repair.py
M fund_agent/agent/runner.py
M tests/agent/test_repair_policy.py
M tests/agent/test_runner.py
M tests/fund/test_chapter_writer.py
M tests/services/test_chapter_orchestrator.py
(plus pre-existing unrelated modified/untracked files outside gate scope)
```

## 3. Accepted Behavior Verification

### 3.1 retry is Chapter 6–only

`_should_retry_writer_invalid_marker()` at `runner.py:658` has `if chapter_id != 6: return False` as the first check. Confirmed. Test `test_non_chapter_6_invalid_anchor_marker_does_not_retry` at `test_runner.py:602` verifies Chapter 5 invalid marker produces exactly one writer call and terminal blocked status.

### 3.2 writer_result.status == "blocked"

Second check in the gate function: `if writer_result.status != "blocked": return False`. Confirmed at `runner.py:671`.

### 3.3 stop_reason == "llm_contract_violation"

Third check: `if writer_result.stop_reason != "llm_contract_violation": return False`. Confirmed at `runner.py:673`.

### 3.4 issue id prefix writer:invalid_anchor_marker

Fourth check uses `any(issue.issue_id.startswith("writer:invalid_anchor_marker") for issue in writer_result.issues)`. Confirmed at `runner.py:677`. The `repair_context_from_writer_invalid_marker()` at `repair.py:178` also filters by the same prefix when collecting issues.

### 3.5 consumes existing content repair budget without changing defaults

Budget consumption: `remaining_budget = policy.repair_policy.max_content_repair_attempts - attempt_index` at `runner.py:391`. No default value is changed. The source comment at `runner.py:395-396` documents the budget interaction: "Writer-block retry consumes the same content repair budget that audit repair would use. With default budget 1, a successful retry does not leave an extra audit repair attempt."

### 3.6 branch continues through existing while loop so interruption checks run before next writer call

Retry path at `runner.py:389-409` uses `continue` after rebuilding `writer_input`, landing at the top of the existing `while True` loop. Interruption checks (cancel, timeout) at the loop top will execute before the next writer call. Confirmed.

### 3.7 exact marker syntax is preserved; parser is not relaxed

The correction constant `_WRITER_INVALID_ANCHOR_CORRECTION` at `repair.py:30-34` instructs: `使用精确 anchor marker 语法 \`<!-- anchor:<anchor_id> -->\``. No parser code is modified. No marker acceptance syntax is relaxed. Confirmed.

### 3.8 budget 0 and non-Chapter-6 remain one-call fail-closed

Confirmed by four tests:
- `test_chapter_6_invalid_anchor_marker_budget_zero_does_not_retry` (Agent runner): 1 writer call, blocked, stop_reason `llm_contract_violation`.
- `test_non_chapter_6_invalid_anchor_marker_does_not_retry` (Agent runner): 1 writer call, blocked.
- `test_chapter_6_invalid_anchor_marker_budget_zero_does_not_retry` (Service orchestrator): 1 writer call, blocked.
- Service orchestrator non-Chapter-6 behavior is implicitly covered by the runner-level gate; the orchestrator delegates to the runner.

### 3.9 no provider/source/fallback/readiness/release/PR behavior change

Diff confirms no changes to provider code, source policy, fallback logic, readiness state, release state, or PR state. EID single-source/no-fallback policy is untouched. `NOT_READY` is preserved.

## 4. Controller Amendment Compliance

| Amendment | Status | Evidence |
|---|---|---|
| 1. Label budget=0 and non-Ch6 tests as regression guards | `PASS` | Test docstrings use "回归守卫" label; both tests were green before and after implementation |
| 2. Source comment documenting budget consumption | `PASS` | Two-line comment at `runner.py:395-396` |
| 3. `continue` lands at top of existing `while True` loop | `PASS` | `continue` at `runner.py:409` re-enters loop top before next writer call |
| 4. Chapter 6–only and issue-prefix–specific | `PASS` | Four-condition gate in `_should_retry_writer_invalid_marker()` |
| 5. No budget/parser/provider/source/readiness/release/PR changes | `PASS` | Diff confirms zero changes to any of these |

## 5. Adversarial Checks

- **What if retry also produces invalid marker?** Covered by `test_chapter_6_invalid_anchor_marker_twice_fails_closed_after_one_retry`: second attempt is terminal blocked, no hidden third retry. Fail-closed preserved.
- **What if Chapter 6 produces invalid marker but stop_reason is not llm_contract_violation?** Gate function rejects: `if writer_result.stop_reason != "llm_contract_violation": return False`. Fail-closed preserved.
- **What if budget is negative?** `remaining_budget <= 0` check handles zero and negative cases. Fail-closed preserved.
- **Can raw malformed markers leak through repair context?** `_sanitize_writer_issue_message()` at `repair.py:399` applies `_COMMENT_RE` to strip HTML comments before standard sanitization. Test `test_writer_invalid_anchor_repair_context_is_sanitized_and_exact` confirms `<!-- ANCHOR:bad -->`, `Authorization`, `Bearer`, `sk-secret`, `prompt raw` are all absent from rendered context.
- **Does first attempt carry repair_context?** Confirmed `writer.requests[0].repair_context is None` in both `test_chapter_6_invalid_anchor_marker_retries_once_and_accepts` and `test_chapter_6_invalid_anchor_marker_twice_fails_closed_after_one_retry`.

## 6. Code Quality Observations

Non-blocking observations:

- `_COMMENT_RE` at `repair.py:29` is a module-level compiled regex. This is appropriate for the narrow use case.
- `_WRITER_INVALID_ANCHOR_CORRECTION` at `repair.py:30-34` is a module-level constant. The Chinese text is exact and instructive. It correctly mentions `bond_risk_evidence` as the Chapter 6–specific anchor boundary.
- `repair_context_from_writer_invalid_marker()` at `repair.py:178-208` follows the same pattern as the existing `repair_context_from_audit()`. Clean symmetry.
- The `_should_retry_writer_invalid_marker()` function at `runner.py:658-680` is a standalone predicate with clear boolean short-circuit logic. Well isolated from the retry action.
- No new dependencies, no new imports beyond `re` (stdlib) and `repair_context_from_writer_invalid_marker` (internal).

## 7. Residuals

- This no-live fix does not prove any future provider/live Chapter 6 sample will pass.
- If the retry also emits invalid marker syntax, Chapter 6 remains fail-closed after budget consumption (verified).
- Generalizing invalid-marker retry beyond Chapter 6 remains deferred.
- Chapter repair budget calibration remains a future standard gate.
- Release/readiness remains `NOT_READY`.

## 8. Final Verdict

`VERDICT: PASS`

All nine accepted behavior items verified. All five controller amendments complied with. All validation commands passed (163 tests, ruff clean, git diff --check clean). No regression in budget=0 or non-Chapter-6 paths. No scope violation, no boundary breach, no unauthorized changes.

Stop condition satisfied: review artifact written. No source/tests/control/design/README modification. No stage/commit/push/PR. No live/provider/LLM/network/PDF/FDR/source/analyze/checklist/golden/readiness/release commands.
