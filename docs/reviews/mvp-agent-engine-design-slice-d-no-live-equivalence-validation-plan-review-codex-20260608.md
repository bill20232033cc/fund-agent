# MVP Agent Engine Design Slice D No-Live Equivalence Validation Plan Review - Codex

## 1. Verdict

BLOCKED.

阻断原因：目标 plan 的 terminal mapping 把 `llm_exception` 归入 provider/runtime blocked state，但当前测试事实证明普通未知异常使用同一 stop reason，同时必须保留为 `code_bug` failure category。这会让后续 implementation planning 的 current-to-future terminal mapping 不等价。

## 2. Reviewed Target And Scope

- Review target: `docs/reviews/mvp-agent-engine-design-slice-d-no-live-equivalence-validation-plan-20260608.md`
- Role: review worker.
- Gate: `MVP Agent Engine Design Slice D No-Live Equivalence Validation Plan`.
- Scope: design-only adversarial plan review; no implementation, no source/test/control-doc/plan edits, no live/provider/network/probe commands.
- Allowed write path used: `docs/reviews/mvp-agent-engine-design-slice-d-no-live-equivalence-validation-plan-review-codex-20260608.md`.

## 3. Assumptions Tested

- Slice D must be concrete enough for a later implementation plan.
- No-live validation must be enforceable through local tests/test doubles only.
- Final assembly readiness must not be weaker than current Service `FinalChapterAssembler`.
- Agent content repair budget must remain separate from Service/provider runtime budget.
- ToolTrace/serialized diagnostics must use safe scalar allowlists only.
- The review must not authorize implementation, live provider, runtime/default/budget/config, quality gate, golden/readiness, score-loop, multi-year, public chapter id, PR or push scope.

## 4. Findings

### 01-未修复-[高]-`llm_exception` terminal mapping collapses code bugs into provider runtime

- **位置**: `docs/reviews/mvp-agent-engine-design-slice-d-no-live-equivalence-validation-plan-20260608.md:93-112`
- **问题类型**: 契约缺失 / 状态机漏洞 / 测试缺口
- **当前写法**: Slice D requires a future mapping from current `ChapterRunStopReason` / `ChapterFailureCategory` to Agent terminal state, then lists `llm_timeout`, `llm_rate_limited`, `llm_malformed_response`, `llm_network_error`, `llm_exception` together as provider/runtime blocked state.
- **反例/失败场景**: Current local test constructs a plain `RuntimeError("Authorization Bearer sk-secret prompt full text")`; the resulting chapter run has `stop_reason == "llm_exception"` but `failure_category == "code_bug"`, and the runtime diagnostic also records `chapter_failure_category == "code_bug"` while redacting secrets.
- **为什么有问题**: The plan says equivalence is based on both stop reason and failure category, but the required minimum mapping treats all `llm_exception` as provider/runtime. A later implementation plan following this table can misclassify internal/code defects as provider runtime failures, weakening root-cause ownership, retained diagnostics, provider budget interpretation and no-live equivalence.
- **直接证据**:
  - Plan maps `llm_exception` to provider/runtime blocked state: `docs/reviews/mvp-agent-engine-design-slice-d-no-live-equivalence-validation-plan-20260608.md:95-103`.
  - Current test expects unknown exception to remain `code_bug`: `tests/services/test_chapter_orchestrator.py:1584-1599`.
  - Current test also asserts secret redaction for that diagnostic: `tests/services/test_chapter_orchestrator.py:1600-1603`.
  - Control truth requires future evidence to distinguish provider timeouts, prompt contract, audit-rule block, fact gap and code bug: `docs/implementation-control.md:55`.
- **影响**: Implementation Agent may generate a terminal-state table that is not behaviorally equivalent; code bug incidents can be reported as provider/runtime blocked, making diagnostics and budget ownership wrong while still fail-closed. Review cannot later prove equivalence from the proposed minimum table.
- **建议改法和验证点**: Split mapping by `(stop_reason, failure_category)` or explicitly state that `llm_exception` with `failure_category == "code_bug"` maps to a fail-closed `code_bug` / internal-error terminal, not provider runtime. Provider/runtime blocked should cover only explicitly provider-classified runtime categories. Add a required no-live assertion that a generic unexpected exception remains `code_bug`, redacts secret canaries, does not consume content repair budget, and is not counted as provider/runtime budget evidence.
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 高

### 02-未修复-[中]-Final assembly readiness minimum assertions omit duplicate chapter fail-closed behavior

- **位置**: `docs/reviews/mvp-agent-engine-design-slice-d-no-live-equivalence-validation-plan-20260608.md:134-147`
- **问题类型**: 测试缺口 / 契约缺失
- **当前写法**: Final assembly readiness minimum assertions cover accepted drafts/conclusions, partial/blocked orchestration, Ch0/Ch7 blocking, source accepted chapter ids and Service final product authority.
- **反例/失败场景**: Current `FinalChapterAssembler` explicitly fails closed when Gate 3 returns duplicate chapter rows; it returns `status == "incomplete"`, records `duplicate_chapter`, and does not produce report markdown.
- **为什么有问题**: Future Agent body readiness will be fed by a task graph and chapter matrix. Duplicate rows are a realistic migration hazard when task graph output, retry bookkeeping or chapter result aggregation changes. Omitting uniqueness from the minimum readiness assertions leaves a path for an implementation plan to pass readiness with duplicated rows while claiming no weaker final assembly semantics.
- **直接证据**:
  - Plan final assembly minimum assertions omit duplicate/unique chapter row checks: `docs/reviews/mvp-agent-engine-design-slice-d-no-live-equivalence-validation-plan-20260608.md:139-147`.
  - Current test requires duplicate chapter fail-closed: `tests/services/test_final_chapter_assembler.py:321-344`.
  - Parent Slice A says future `FinalAssemblyReadiness` is only a handoff and does not replace current Service final product authority: `docs/reviews/mvp-agent-engine-design-slice-a-dataclass-design-plan-controller-judgment-20260608.md:50-51`.
- **影响**: Later implementation planning may under-specify body readiness uniqueness, causing duplicate Agent rows to become accepted sources or making final assembly behavior unverifiable until late integration.
- **建议改法和验证点**: Add a minimum assertion that required body chapter rows and accepted source chapter ids are unique; duplicate chapter rows must remain fail-closed with no report markdown. The later implementation plan should either reuse `test_incomplete_when_orchestration_has_duplicate_chapter` or add an Agent-equivalent no-live test.
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 中

## 5. Parent Follow-Up Assessment

- Slice A final assembly handoff boundary is preserved in intent, but Slice D must add duplicate-row readiness equivalence before controller acceptance.
- Slice A/B ToolTrace safety follow-ups are materially covered: the plan excludes prompt, draft, fact values, unsafe anchor prose, raw provider/audit payloads, provider request/body, API key, Authorization header, bearer token, model value, base URL value, arbitrary response headers and provider config values.
- Slice B request id follow-up is covered: request id is limited to an allowlisted scalar.
- Slice C repair/provider budget separation is covered in intent: provider timeout retry does not consume content repair budget, provider runtime failures do not trigger content repair, and hidden Agent retry remains forbidden.
- Slice C terminal mapping follow-up is not fully resolved because `llm_exception` is mapped too broadly and conflicts with current `code_bug` behavior.

## 6. Scope And Forbidden-Action Audit

- Source files edited: none.
- Tests edited: none.
- Control docs edited: none.
- Target plan artifact edited: none.
- Implementation scaffold created: none.
- `fund_agent/agent` created: no.
- Live `--use-llm` run: not run.
- Provider readiness, curl, DNS, socket, endpoint or network probe: not run.
- Runtime/default/budget/config change: none.
- Quality gate, golden/readiness, score-loop, multi-year, public chapter id, PR, push or commit: none.
- Validation was limited to read-only `rg`, `sed`, `nl`, `git status`, `git branch`, `date`, `test -e` and `git diff --check`, plus writing this allowed review artifact.

## 7. Validation Commands And Results

- `git branch --show-current`
  - Result: exit 0; branch `feat/mvp-llm-incomplete-run-artifacts`.
- `git status --short`
  - Result: exit 0; existing unrelated dirty state observed, including modified `pyproject.toml` and multiple untracked review/artifact paths. No unrelated files were modified by this review.
- `git diff --check -- docs/reviews/mvp-agent-engine-design-slice-d-no-live-equivalence-validation-plan-20260608.md`
  - Result: exit 0; no whitespace errors.
- `test -e docs/reviews/mvp-agent-engine-design-slice-d-no-live-equivalence-validation-plan-review-codex-20260608.md`
  - Result before write: exit 1; review artifact did not exist.
- `date +%Y-%m-%dT%H:%M:%S%z`
  - Result: `2026-06-08T01:46:33+0800`.

- `git diff --check -- docs/reviews/mvp-agent-engine-design-slice-d-no-live-equivalence-validation-plan-20260608.md docs/reviews/mvp-agent-engine-design-slice-d-no-live-equivalence-validation-plan-review-codex-20260608.md`
  - Result after write: exit 0; no whitespace errors.

## 8. Residual Risks Or Open Questions

- After fixing the `llm_exception` mapping, the controller should check whether every current `ChapterFailureCategory`, including `code_bug`, `audit_parse`, `audit_rule_too_strict`, `fact_gap`, `prompt_contract` and `llm_timeout`, has a future terminal/readiness category or explicit residual owner.
- If future Agent readiness replaces any part of current Service final assembly readiness, duplicate row, missing required chapter, missing accepted draft, missing accepted conclusion and invalid final judgment input boundaries should be enumerated as no-live equivalence assertions.

## 9. Final Plan Review Conclusion

fail.

The plan should return to the planning worker/controller before implementation planning. It is not ready for controller acceptance until the terminal mapping distinguishes `llm_exception + code_bug` from provider/runtime blocked states and final assembly readiness includes duplicate-row fail-closed equivalence or an explicit residual owner.
