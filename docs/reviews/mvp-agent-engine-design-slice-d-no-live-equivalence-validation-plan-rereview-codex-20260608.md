# MVP Agent Engine Design Slice D No-Live Equivalence Validation Plan Re-Review - Codex

## 1. Verdict

PASS.

目标 plan 已解决 prior Codex review 的两个 blocking findings，并已足够吸收 DS NBO 指向的三个补充点：

- terminal mapping 明确按 `(stop_reason, failure_category)` 二维键映射；
- `llm_exception + code_bug` 明确 fail-closed 为 internal/code-bug state，不归 provider/runtime；
- final assembly readiness 明确包含 required body chapter rows 和 source accepted chapter ids uniqueness，且 duplicate chapter rows fail-closed；
- DS 点名的缺失 stop reasons、`ChapterFailureCategory` 枚举、`request_id` explicit response-header allowlist 均已进入目标 plan。

## 2. Reviewed Target And Scope

- Target plan: `docs/reviews/mvp-agent-engine-design-slice-d-no-live-equivalence-validation-plan-20260608.md`
- Prior review: `docs/reviews/mvp-agent-engine-design-slice-d-no-live-equivalence-validation-plan-review-codex-20260608.md`
- DS review checked for NBO absorption: `docs/reviews/mvp-agent-engine-design-slice-d-no-live-equivalence-validation-plan-review-ds-20260608.md`
- Supplemental artifact written: `docs/reviews/mvp-agent-engine-design-slice-d-no-live-equivalence-validation-plan-rereview-codex-20260608.md`

Scope was limited to targeted re-review of the revised plan. No source, test, control-doc, or target-plan edits were made. No live `--use-llm`, provider readiness, curl, DNS, socket, endpoint, or network probe was run. No `fund_agent/agent` scaffold was created. No commit, PR, push, or external state change was performed.

## 3. Prior Blocking Findings Resolution

### 3.1 `llm_exception + code_bug` provider/runtime misclassification

Status: resolved.

Prior Codex finding required the plan to stop collapsing `llm_exception` into provider/runtime and to map terminal state by `(stop_reason, failure_category)`, because current behavior records generic unexpected exceptions as `stop_reason == "llm_exception"` and `failure_category == "code_bug"`.

Revised target plan now states:

- future mapping key is the pair `(stop_reason, failure_category)`, not `stop_reason` alone;
- provider/runtime blocked applies only to provider-classified failure categories;
- `llm_exception` with `failure_category=code_bug` maps to a fail-closed internal code bug state, not provider/runtime;
- future implementation planning must enumerate every current `ChapterRunStopReason` and every current `ChapterFailureCategory`, including `code_bug`.

Evidence:

- Target plan: `docs/reviews/mvp-agent-engine-design-slice-d-no-live-equivalence-validation-plan-20260608.md:95-123`
- Prior blocking finding: `docs/reviews/mvp-agent-engine-design-slice-d-no-live-equivalence-validation-plan-review-codex-20260608.md:28-43`
- Current test fact: `tests/services/test_chapter_orchestrator.py:1584-1603`
- Current code fact: `fund_agent/services/chapter_orchestrator.py:1697-1714`

Assessment: the revised plan now preserves root-cause ownership and does not permit `code_bug` incidents to be counted as provider/runtime evidence.

### 3.2 Final assembly readiness duplicate rows / source ids uniqueness

Status: resolved.

Prior Codex finding required final assembly readiness to include duplicate chapter row fail-closed behavior and uniqueness constraints for accepted source ids.

Revised target plan now states:

- source accepted chapter ids exclude blocked/failed chapters;
- required body chapter rows and source accepted chapter ids are unique;
- duplicate chapter rows remain fail-closed with no report markdown.

Evidence:

- Target plan: `docs/reviews/mvp-agent-engine-design-slice-d-no-live-equivalence-validation-plan-20260608.md:145-160`
- Prior blocking finding: `docs/reviews/mvp-agent-engine-design-slice-d-no-live-equivalence-validation-plan-review-codex-20260608.md:45-59`
- Current test fact: `tests/services/test_final_chapter_assembler.py:321-344`

Assessment: the revised plan no longer weakens current Service final assembly readiness on duplicate rows or accepted-source uniqueness.

## 4. DS NBO Absorption Check

### 4.1 Missing stop reasons

Status: sufficiently absorbed.

DS NBO identified missing explicit coverage for `fund_type_unknown`, `writer_blocked`, `llm_unavailable`, and `llm_empty_response`.

Revised target plan now includes:

- `llm_unavailable` and `llm_empty_response` in provider-classified runtime mapping;
- `fund_type_unknown` as fund identity/fact-gap precondition state;
- `writer_blocked` as writer precondition blocked state with no provider call;
- an implementation-planning requirement to enumerate every current `ChapterRunStopReason`.

Evidence:

- DS NBO: `docs/reviews/mvp-agent-engine-design-slice-d-no-live-equivalence-validation-plan-review-ds-20260608.md:14-35`
- Target plan: `docs/reviews/mvp-agent-engine-design-slice-d-no-live-equivalence-validation-plan-20260608.md:102-117`
- Current enum fact: `fund_agent/services/chapter_orchestrator.py:53-77`

### 4.2 `ChapterFailureCategory` enum

Status: sufficiently absorbed.

DS NBO required explicit treatment of `ChapterFailureCategory` as a parallel classification axis.

Revised target plan now requires mapping from current `ChapterRunStopReason` and `ChapterFailureCategory`, uses `(stop_reason, failure_category)` as the mapping key, and explicitly lists the current seven categories: `provider_runtime`, `llm_timeout`, `prompt_contract`, `audit_parse`, `audit_rule_too_strict`, `fact_gap`, `code_bug`.

Evidence:

- DS NBO: `docs/reviews/mvp-agent-engine-design-slice-d-no-live-equivalence-validation-plan-review-ds-20260608.md:48-60`
- Target plan: `docs/reviews/mvp-agent-engine-design-slice-d-no-live-equivalence-validation-plan-20260608.md:95-123`
- Current enum fact: `fund_agent/services/chapter_orchestrator.py:105-113`

### 4.3 `request_id` explicit response-header allowlist

Status: sufficiently absorbed.

DS NBO required the `request_id` diagnostic scalar to be constrained to an explicit response-header allowlist, not arbitrary headers or provider config values.

Revised target plan now:

- forbids arbitrary response headers and provider config values;
- allows only an allowlisted request id scalar from an explicit response-header allowlist.

Evidence:

- DS NBO: `docs/reviews/mvp-agent-engine-design-slice-d-no-live-equivalence-validation-plan-review-ds-20260608.md:36-47`
- Target plan: `docs/reviews/mvp-agent-engine-design-slice-d-no-live-equivalence-validation-plan-20260608.md:164-202`

## 5. Blocking Findings

None.

No supplemental blocking finding is warranted within the requested targeted scope.

## 6. Non-Blocking Observations

None.

The remaining exhaustive future-state naming work is already assigned to the later implementation planning gate by the revised target plan and is not a blocker for this Slice D design-only validation plan.

## 7. Validation Commands And Results

- `git branch --show-current`
  - Result: exit 0; branch `feat/mvp-llm-incomplete-run-artifacts`.
- `git status --short`
  - Result: exit 0; existing dirty state observed before this re-review, including modified `pyproject.toml` and untracked review artifacts. This re-review wrote only the supplemental artifact named above.
- `rg -n "Slice D|mvp-agent-engine-design-slice-d|ChapterFailureCategory|request_id explicit response-header allowlist|stop_reason" /Users/maomao/.codex/memories/MEMORY.md`
  - Result: exit 1; no relevant memory hit used.
- `nl -ba docs/reviews/mvp-agent-engine-design-slice-d-no-live-equivalence-validation-plan-20260608.md`
  - Result: exit 0; target plan read with line numbers.
- `nl -ba docs/reviews/mvp-agent-engine-design-slice-d-no-live-equivalence-validation-plan-review-codex-20260608.md`
  - Result: exit 0; prior Codex review read with line numbers.
- `nl -ba docs/reviews/mvp-agent-engine-design-slice-d-no-live-equivalence-validation-plan-review-ds-20260608.md`
  - Result: exit 0; DS review read with line numbers.
- `nl -ba fund_agent/services/chapter_orchestrator.py | sed -n '45,125p'`
  - Result: exit 0; current `ChapterRunStopReason` and `ChapterFailureCategory` literal values inspected.
- `nl -ba tests/services/test_chapter_orchestrator.py | sed -n '1560,1610p'`
  - Result: exit 0; `llm_exception + code_bug` test fact inspected.
- `nl -ba tests/services/test_final_chapter_assembler.py | sed -n '300,355p'`
  - Result: exit 0; duplicate chapter fail-closed test fact inspected.
- `test -e docs/reviews/mvp-agent-engine-design-slice-d-no-live-equivalence-validation-plan-rereview-codex-20260608.md`
  - Result before write: exit 1; supplemental artifact did not exist.
- `date +%Y-%m-%dT%H:%M:%S%z`
  - Result: `2026-06-08T01:51:26+0800`.
- `git diff --check -- docs/reviews/mvp-agent-engine-design-slice-d-no-live-equivalence-validation-plan-20260608.md docs/reviews/mvp-agent-engine-design-slice-d-no-live-equivalence-validation-plan-rereview-codex-20260608.md`
  - Result after write: exit 0; no whitespace errors.
- `git diff --check --no-index -- /dev/null docs/reviews/mvp-agent-engine-design-slice-d-no-live-equivalence-validation-plan-rereview-codex-20260608.md`
  - Result after write: exit 1 because `--no-index` reports file difference against `/dev/null`; no whitespace errors emitted. This extra check was used because the supplemental artifact is untracked.
- `git status --short -- docs/reviews/mvp-agent-engine-design-slice-d-no-live-equivalence-validation-plan-rereview-codex-20260608.md`
  - Result after write: exit 0; supplemental artifact is untracked.

## 8. Final Re-Review Conclusion

PASS.

The revised target plan is ready for controller judgment within the requested targeted re-review scope. Prior Codex blocking findings are resolved, and DS NBO absorption is sufficient for this design-only Slice D plan.
