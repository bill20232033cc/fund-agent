# MVP typed template contract Slice 5 audit_focus code review (DS)

## Self-check

- Role: code review worker only, not controller and not implementation worker.
- Gate: `MVP typed template contract Slice 5 per-chapter audit_focus bounded semantic audit implementation gate`.
- Classification: `heavy`.
- Branch: `feat/mvp-llm-incomplete-run-artifacts`.
- Scope: code review only; no file edits, no commit, no push, no live provider probe, no other gate entry.

## Sources read

1. `AGENTS.md`
2. `docs/current-startup-packet.md`
3. `docs/implementation-control.md`
4. `docs/reviews/mvp-typed-template-contract-implementation-planning-plan-20260603.md` Slice 5 section
5. `docs/reviews/mvp-typed-template-contract-slice5-audit-focus-implementation-evidence-20260603.md`
6. Full source files: `fund_agent/fund/chapter_auditor.py` (1779 lines), `fund_agent/fund/template/typed_contracts.py` (1295 lines), `tests/fund/test_chapter_auditor.py` (1130 lines)
7. `git diff HEAD` for `fund_agent/fund/chapter_auditor.py`, `tests/fund/test_chapter_auditor.py`, `fund_agent/fund/README.md`, `tests/README.md`

## Validation executed

```bash
uv run pytest tests/fund/test_chapter_auditor.py tests/services/test_llm_run_artifacts.py
# Result: 46 passed in 0.80s

uv run pytest tests/fund/template/test_typed_contracts.py
# Result: 8 passed in 0.45s

uv run ruff check fund_agent/fund/chapter_auditor.py tests/fund/test_chapter_auditor.py \
  fund_agent/fund/README.md tests/README.md
# Result: All checks passed!

git diff --check
# Result: no output (clean)

Secret scan on diff: NO_SECRETS_FOUND
```

## Findings

### Finding 1 — NON-BLOCKING: Broad ValueError catch discards specific validation reason

`audit_chapter_llm()` at `chapter_auditor.py:489-505` catches `ValueError` broadly and issues a fixed generic message `"typed audit_focus 无法安全投影为闭集 LLM 审计关注点。"`, discarding the specific reason from `_llm_audit_focus()` (chapter mismatch, empty focus, or closed-set violation). The original ValueError messages are informative (`"typed audit_focus 章节不匹配：contract=2, input=3"`, `"章节 LLM audit_focus 不能为空"`, `"章节 LLM audit_focus 包含闭集外 id：('disable_programmatic',)"`). Currently safe because `_llm_request()` only raises ValueError from `_llm_audit_focus()`, but if `_llm_request()` later raises ValueError for an unrelated reason, it would be misclassified as `llm:audit_focus_invalid`.

Severity: non-blocking. The catch scope is currently correct and no other ValueError sources exist in `_llm_request()`. The generic message is a reasonable safe-diagnostic choice. Recommend adding a comment at the `except ValueError` line noting this intent, or storing `str(exc)` in a `diagnostic_detail` field that is safe to serialize.

### Finding 2 — NON-BLOCKING: No test for DEFAULT_AUDIT_FOCUS path with typed_chapter_contract=None and run_llm=True explicitly

The extended test `test_llm_audit_prompt_spells_exact_pass_and_issue_line_protocol` verifies `request.audit_focus == DEFAULT_AUDIT_FOCUS` when `typed_chapter_contract` is not set (None by default). However, there is no explicit test that constructs `ChapterAuditInput` with `typed_chapter_contract=None` and `run_llm=True` to assert the exact default tuple equals `DEFAULT_AUDIT_FOCUS` constants. The existing test covers this implicitly through the default `None` value in the `_audit_input()` helper, which is sufficient.

Severity: non-blocking. The implicit test coverage is adequate; the existing test at line 855 `assert request.audit_focus == DEFAULT_AUDIT_FOCUS` already confirms the default path.

### Finding 3 — CONFIRMED: No overclaiming in README updates

`fund_agent/fund/README.md` changes at lines 122 and 141:
- Updated `audit_focus` description adds `"显式传入 typed contract 时会投影到 LLM audit request 和 prompt 语义强调"` — accurate to implementation.
- New line `"audit_chapter_llm() 在未提供 typed contract 时继续使用旧 DEFAULT_AUDIT_FOCUS 兼容路径"` — accurate to implementation.

`tests/README.md` change at line 23:
- Added `"typed per-chapter audit_focus 只进入 LLM request 且不关闭程序阻断"` — accurate to implementation.

No claims about Service wiring, Agent runtime, provider/runtime, score-loop, template truth replacement, or golden/readiness changes appear in the README diffs.

### Finding 4 — CONFIRMED: No secret/prompt/raw provider response leakage

- `_llm_audit_focus()` returns only closed-set semantic labels (`"manager_consistency"`, `"evidence_anchors"`, etc.) from `SUPPORTED_AUDIT_FOCUS`.
- The prompt text contains focus ids as semantic labels only (`f"本章 bounded semantic audit focus ids：{', '.join(audit_focus)}。"`).
- No API key, Authorization header, Bearer token, raw provider response, raw audit response, draft body, model name, or provider config values are introduced in the diff.
- Tests use `_FakeAuditLLMClient`, never real providers.
- Secret scan on diff: clean (false positives are documentation stating what is NOT stored).

## Acceptance criteria verification

| Criterion | Status | Evidence |
|---|---|---|
| Typed per-chapter audit_focus projects from TypedChapterContract into ChapterAuditLLMRequest | PASS | `_llm_audit_focus()` → `_llm_request()` → `ChapterAuditLLMRequest.audit_focus` + `user_prompt` |
| Default path preserves DEFAULT_AUDIT_FOCUS | PASS | `typed_chapter_contract is None` → returns `DEFAULT_AUDIT_FOCUS`; `test_llm_audit_prompt_spells_exact_pass_and_issue_line_protocol` asserts |
| Focus ids validated against closed set SUPPORTED_AUDIT_FOCUS | PASS | `_llm_audit_focus()` checks membership before returning |
| Invalid/mismatched focus fail-closed without calling LLM client | PASS | `audit_chapter_llm()` catches ValueError, returns blocked; `client.requests == []` verified in two tests |
| Programmatic audit independent of focus | PASS | `audit_chapter_programmatic()` never reads `typed_chapter_contract`; `test_programmatic_blocker_fires_even_when_focus_omits_must_not_cover_boundary` confirms |
| C2, L1, markers, anchors, item-rule, forbidden advice, missing/degrade, severity unchanged | PASS | No programmatic audit functions modified; all existing tests pass |
| No provider/runtime/default/budget change | PASS | Diff contains zero changes to provider construction, timeout, retry, endpoint, or config |
| No Agent runtime/tool-loop implementation | PASS | No Agent runtime code touched |
| No score-loop/golden/readiness change | PASS | No score/golden/readiness code touched |
| No template truth replacement | PASS | `docs/fund-analysis-template-draft.md` and `contracts.py` untouched |

## Test coverage assessment

Four new tests added, all passing:

1. `test_per_chapter_audit_focus_is_passed_to_llm_request` — verifies focus flows from typed contract → LLM request, checks `audit_focus` equals contract focus, subset of `SUPPORTED_AUDIT_FOCUS`, and appears in `user_prompt`.
2. `test_programmatic_blocker_fires_even_when_focus_omits_must_not_cover_boundary` — verifies programmatic C2 fires regardless of focus content, with explicit `typed_chapter_contract` set on `ChapterAuditInput`.
3. `test_invalid_typed_audit_focus_blocks_without_calling_client` — verifies closed-set violation → blocked, `client.requests == []`, correct issue fields.
4. `test_mismatched_typed_audit_focus_blocks_without_calling_client` — verifies chapter mismatch → blocked, `client.requests == []`, correct generic message.

One existing test extended: `test_llm_audit_prompt_spells_exact_pass_and_issue_line_protocol` now also asserts `request.audit_focus == DEFAULT_AUDIT_FOCUS`.

Coverage is sufficient for the gate scope. The evidence notes `tests/services/test_llm_run_artifacts.py::test_artifact_serializes_audit_focus_ids_only_if_added` was not added because artifact serialization was not touched — this is correct scoping.

## Final verdict

**PASS** — no blocking findings.

Two non-blocking findings recorded above (broad ValueError catch losing specificity, implicit default-path test coverage). The implementation correctly projects typed per-chapter `audit_focus` from `TypedChapterContract` into `ChapterAuditLLMRequest` for LLM bounded semantic audit only, preserves `DEFAULT_AUDIT_FOCUS` compatibility on the default path, validates focus ids against the closed `SUPPORTED_AUDIT_FOCUS` set, fail-closes on invalid/mismatched focus without calling the LLM client, keeps programmatic audit (C2, L1, markers, anchors, item-rule, forbidden advice, missing/degrade, severity) fully independent of focus, and introduces no secret or raw provider response leakage. README updates are accurate and do not overclaim. All 54 targeted tests pass, ruff is clean, and `git diff --check` is clean.
