# Provider/LLM Chapter 2 L1 Narrow No-live Fix Plan Controller Judgment

Date: 2026-06-14

Role: AgentController

Gate: `Provider/LLM Chapter 2 L1 Numerical Closure Narrow No-live Fix Planning Gate`

Verdict: `ACCEPT_WITH_CONTROLLER_AMENDMENTS_READY_FOR_NARROW_NO_LIVE_FIX_IMPLEMENTATION_GATE_NOT_READY`

## Scope

This judgment closes the planning gate for the Chapter 2 L1 numerical-closure repair-effectiveness regression observed after the accepted Chapter 3 required-output policy fix.

This gate is planning only. It does not implement code, does not change source acquisition policy, does not change repair budget defaults, and does not run live/provider/LLM/network/source/PDF/FDR/analyze/checklist/readiness/release/PR commands.

Release/readiness remains `NOT_READY`.

EID annual-report acquisition remains single-source/no-fallback. Eastmoney, fund-company/CDN, CNINFO and other fallback routes remain deferred candidates only and are not authorized by this gate.

## Evidence Reviewed

| Evidence | Controller use |
|---|---|
| `AGENTS.md` | Execution truth source, module boundaries, fail-closed evidence requirements, EID/source constraints |
| `docs/design.md` | Route C current/future boundary, Service/Host/Agent/Fund ownership, EID single-source design truth |
| `docs/current-startup-packet.md` | Current gate, accepted checkpoints, `NOT_READY`, non-goals |
| `docs/implementation-control.md` | Control truth, active gate, accepted diagnostic facts, next routing |
| `docs/reviews/provider-llm-chapter2-l1-no-live-diagnostic-evidence-controller-judgment-20260614.md` | Binding diagnostic judgment and planning requirements |
| `docs/reviews/provider-llm-chapter2-l1-narrow-no-live-fix-plan-20260614.md` | Plan under judgment |
| `docs/reviews/provider-llm-chapter2-l1-narrow-no-live-fix-plan-review-ds-20260614.md` | Independent plan review |
| `docs/reviews/provider-llm-chapter2-l1-narrow-no-live-fix-plan-review-mimo-20260614.md` | Independent plan review |

No writer Markdown, auditor feedback Markdown, repair Markdown, raw prompts, provider payloads, source/PDF/cache body or final report body was read for this judgment.

## Accepted Current Facts

- Current active gate is `Provider/LLM Chapter 2 L1 Numerical Closure Narrow No-live Fix Planning Gate`.
- The accepted diagnostic checkpoint `7fbc862` proves current no-live repair-context propagation reaches writer prompt assembly and L1 remains fail-closed.
- The live regression is currently classified as Chapter 2 L1 repair-effectiveness failure, not missing repair-context propagation.
- The planning gate carried a DS residual requiring bounded diff verification for `842362d..1b9cd00 -- fund_agent/fund/chapter_writer.py`.
- The plan closes that residual by reporting `git diff 842362d..1b9cd00 -- fund_agent/fund/chapter_writer.py` exit code `0` with no output.
- The plan preserves repair budget defaults and does not weaken, suppress or downgrade L1.
- Release/readiness remains `NOT_READY`.

## Plan Disposition

| Item | Decision | Basis |
|---|---|---|
| Narrow no-live fix strategy in Fund writer prompt contract | `ACCEPT` | It directly targets the accepted repair-effectiveness surface in `fund_agent/fund/chapter_writer.py` and avoids Service/Host/provider/source-policy expansion. |
| Bounded diff closure for DS diagnostic residual | `ACCEPT` | The plan performed the required bounded diff and reported no `chapter_writer.py` change across `842362d..1b9cd00`. |
| Preserve L1 fail-closed behavior | `ACCEPT` | Plan explicitly keeps auditor failure semantics and adds tests for ignored/unanchored output continuing to fail closed. |
| Preserve one-repair default budget | `ACCEPT` | Plan forbids repair budget calibration or default changes. |
| Allowed write set | `ACCEPT_WITH_REWRITE` | Source/test write set is correct, but implementation must not modify `_repair_context_prompt()` under a generic "minor wording" escape hatch. |
| Validation matrix | `ACCEPT_WITH_REWRITE` | Focused tests are appropriate; DS F2 is accepted as non-blocking amendment requiring the full three-file no-live suite after focused commands. |
| Chapter 2 header/checklist wording ambiguity | `ACCEPT_WITH_REWRITE` | MiMo F1/F2 are accepted as implementation constraints: the implementation must make one consistent header/checklist interpretation and update tests accordingly. |

## Review Finding Disposition

| Finding | Reviewer | Decision | Controller judgment |
|---|---|---|---|
| `_repair_context_prompt()` "minor wording" escape hatch is ambiguous | DS F1 | `ACCEPT_WITH_REWRITE` | Binding amendment: implementation must keep `_repair_context_prompt()` unchanged. Any need to alter the generic repair-context function requires a new plan/review loop. |
| Add full three-file no-live regression suite | DS F2 | `ACCEPT_WITH_REWRITE` | Binding amendment: after focused commands, implementation must run `uv run pytest tests/fund/test_chapter_writer.py tests/services/test_chapter_orchestrator.py tests/fund/test_chapter_auditor.py -q`. |
| `test_required_corrections_are_deterministic_for_known_issue_patterns` under-specified | DS F3 | `ACCEPT_AS_IMPLEMENTATION_CHECK` | Implementation worker must inspect/run the test and update only stable prompt-header assertions if needed; Service behavior must not broaden. |
| Prompt inflation compact-mode edge | DS F4 | `ACCEPT_AS_TEST_COVERED` | Implementation must keep compact prompt coverage and prove compact mode still preserves the strengthened Chapter 2 contract. |
| Bounded diff residual closed | DS F5 | `ACCEPT` | Accepted as closure of the prior residual. |
| Strategy robust to ignored-checklist vs weak-checklist interpretations | DS F6 | `ACCEPT` | Accepted; plan avoids claiming live behavior proof and keeps fail-closed guard tests. |
| Allowed write set matches change surface | DS F7 | `ACCEPT` | Accepted with DS F1 rewrite forbidding generic repair-context edits. |
| Checklist replacement vs keep ambiguity | MiMo F1 | `ACCEPT_WITH_REWRITE` | Binding amendment: only `_ch2_l1_repair_guidance_prompt()` may be changed for repair-specific wording; `_repair_context_prompt()` remains unchanged. Existing tests for old L1-specific checklist strings may be replaced or extended, but final tests must assert the new stable repair-only header and semantics. |
| Initial contract header ambiguity | MiMo F2 | `ACCEPT_WITH_REWRITE` | Binding amendment: `_ch2_numerical_closure_contract_prompt()` must expose the new stable header `第2章 L1 数字闭环安全输出契约`. It may preserve old descriptive wording as non-stable context only if tests assert the new header as the contract. |
| Compact-payload assertion detail | MiMo F3 | `ACCEPT_AS_TEST_COVERED` | Implementation must update compact prompt assertions to the new stable header if the old header is replaced or made non-stable. |
| Auditor safe-gap test | MiMo F4 | `ACCEPT` | Accepted as required no-live coverage for gap/minimum-verification wording without concrete percentage. |

## Controller Amendments For Implementation Gate

The next implementation gate must treat the following amendments as binding:

1. Keep `_repair_context_prompt()` unchanged. Do not use the plan's "minor wording" escape hatch. If the generic repair-context function appears contradictory, stop and return to planning.
2. Limit source changes to Chapter 2-specific prompt functions:
   - `_ch2_numerical_closure_contract_prompt()`
   - `_ch2_l1_repair_guidance_prompt()`
3. The new stable initial-contract header is `第2章 L1 数字闭环安全输出契约`.
4. The new stable repair-only header is `第2章 L1 repair 必须改写规则`.
5. Tests must assert the new stable headers. Old header assertions may be removed or retained only if they do not become the stable implementation contract.
6. Add/maintain compact-prompt coverage proving the strengthened Chapter 2 contract survives compact mode.
7. Add/maintain no-live failure coverage proving ignored or unanchored concrete percentages still fail closed with `repair_budget_exhausted` / `prompt_contract` / `l1_numerical_closure`.
8. Add/maintain no-live auditor coverage proving a safe gap/minimum-verification rewrite without concrete percentage does not trigger L1.
9. Run focused tests and then the full three-file no-live suite:

```bash
uv run pytest tests/fund/test_chapter_writer.py -k "ch2_l1 or l1_numerical_closure or repair_context or compact_prompt_payload" -q
uv run pytest tests/services/test_chapter_orchestrator.py -k "l1_repair_context or l1_failure_after_repair_budget_exhausted or required_corrections_are_deterministic" -q
uv run pytest tests/fund/test_chapter_auditor.py -k "programmatic_audit_fails_l1 or programmatic_audit_allows_l1 or a_minus_c or formula_framework or ch2_source_section or l1_gap" -q
uv run pytest tests/fund/test_chapter_writer.py tests/services/test_chapter_orchestrator.py tests/fund/test_chapter_auditor.py -q
uv run ruff check fund_agent/fund/chapter_writer.py tests/fund/test_chapter_writer.py tests/services/test_chapter_orchestrator.py tests/fund/test_chapter_auditor.py
git diff --check
git status --short
```

## Accepted Implementation Gate Write Set

Allowed implementation writes:

- `fund_agent/fund/chapter_writer.py`
- `tests/fund/test_chapter_writer.py`
- `tests/services/test_chapter_orchestrator.py`
- `tests/fund/test_chapter_auditor.py`

Conditional documentation writes only if implementation makes existing documentation stale:

- `fund_agent/fund/README.md`
- `tests/README.md`

Forbidden writes:

- `docs/design.md`
- `docs/implementation-control.md` during implementation worker execution
- `docs/current-startup-packet.md` during implementation worker execution
- repository/cache/downloader/provider/model/source acquisition files
- root `README.md`, `pyproject.toml`, `.gitignore`
- report bodies, prompt payloads, source/PDF/cache body, provider artifacts, final report body, readiness/release/PR artifacts

Controller may update control docs only after implementation review is accepted.

## Residuals

| Residual | Status | Owner / next handling |
|---|---|---|
| Live model behavior after strengthened prompt | Deferred | Future bounded live re-evidence gate only after no-live implementation is accepted. |
| Repair budget calibration | Deferred | Separate repair budget calibration gate. |
| Chapter 5 forbidden phrase blocker | Deferred | Separate disposition/root-cause gate. |
| Release/readiness | `NOT_READY` | Release/readiness remains blocked until later rollup/evidence gates. |
| Existing unrelated tracked diffs and untracked residue | Not part of this gate | Leave untouched; do not stage or commit in this gate. |

## Next Gate Recommendation

Recommended next gate:

`Provider/LLM Chapter 2 L1 Numerical Closure Narrow No-live Fix Implementation Gate`

The next gate should be delegated to AgentCodex/procodex as an implementation worker under the accepted write set and controller amendments above. DS and MiMo should review the resulting implementation evidence before controller acceptance.

## Final Verdict

`VERDICT: ACCEPT_WITH_CONTROLLER_AMENDMENTS_READY_FOR_NARROW_NO_LIVE_FIX_IMPLEMENTATION_GATE_NOT_READY`
