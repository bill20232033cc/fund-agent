# Provider/LLM Chapter 2 L1 Narrow No-live Fix Implementation Evidence

Date: 2026-06-14

Role: AgentCodex/procodex implementation worker

Gate: `Provider/LLM Chapter 2 L1 Numerical Closure Narrow No-live Fix Implementation Gate`

## 1. Scope

Implemented only the accepted Chapter 2 L1 writer prompt-contract strengthening from:

- `docs/reviews/provider-llm-chapter2-l1-narrow-no-live-fix-plan-20260614.md`
- `docs/reviews/provider-llm-chapter2-l1-narrow-no-live-fix-plan-controller-judgment-20260614.md`

Scope boundaries preserved:

- No live/provider/LLM/network/source/PDF/FDR/analyze/checklist/readiness/release/PR/push/merge commands.
- No writer Markdown, auditor feedback Markdown, repair Markdown, raw prompts, provider payloads, source/PDF/cache body or final report body reads.
- No Service/Host/provider/source-policy/fallback/runtime/repair-budget changes.
- Release/readiness remains `NOT_READY`.

## 2. Files Changed

- `fund_agent/fund/chapter_writer.py`
- `tests/fund/test_chapter_writer.py`
- `tests/services/test_chapter_orchestrator.py`
- `tests/fund/test_chapter_auditor.py`
- `fund_agent/fund/README.md`
- `docs/reviews/provider-llm-chapter2-l1-narrow-no-live-fix-implementation-evidence-20260614.md`

`tests/README.md` was checked and left unchanged because it does not document the new stable Chapter 2 L1 headers or the exact strengthened prompt wording.

## 3. Implementation Summary

- Strengthened `_ch2_numerical_closure_contract_prompt()` with the stable initial header `第2章 L1 数字闭环安全输出契约`.
- Strengthened `_ch2_l1_repair_guidance_prompt()` with the stable repair-only header `第2章 L1 repair 必须改写规则`.
- Added explicit safe-output rules: concrete R/A/B/C/A-C, Alpha/Beta/Cost or percentage closure must have a nearby allowed anchor; otherwise the writer must omit concrete percentages and write data-gap/minimum-verification wording.
- Kept concrete unsupported percentage output fail-closed through existing auditor/orchestrator behavior.
- Added auditor coverage proving a safe gap/minimum-verification rewrite without concrete percentage does not trigger L1.
- Updated compact prompt assertions so compact mode must retain the strengthened Chapter 2 initial contract.

## 4. Controller Amendments Compliance

1. `_repair_context_prompt()` unchanged: complied.
2. Source changes limited to Chapter 2-specific prompt functions: complied. Only `_ch2_numerical_closure_contract_prompt()` and `_ch2_l1_repair_guidance_prompt()` changed in `chapter_writer.py`.
3. Stable initial-contract header asserted: `第2章 L1 数字闭环安全输出契约`.
4. Stable repair-only header asserted: `第2章 L1 repair 必须改写规则`.
5. Old stable-header assertions removed from writer/orchestrator tests where they would conflict with the new stable contract.
6. Compact-prompt coverage maintained and updated to assert the strengthened Chapter 2 contract survives compact mode.
7. No-live failure coverage maintained: ignored/unanchored concrete percentages still fail closed with `repair_budget_exhausted` / `prompt_contract` / `l1_numerical_closure`.
8. No-live auditor safe-gap coverage added: gap/minimum-verification wording without concrete percentage does not trigger L1.

Self-check: pass. This worker stayed inside the assigned implementation gate/scope, touched only allowed or conditional files, did not stage/commit/push/open PR, and produced this evidence artifact.

## 5. Validation Results

All required no-live validation commands passed:

```text
uv run pytest tests/fund/test_chapter_writer.py -k "ch2_l1 or l1_numerical_closure or repair_context or compact_prompt_payload" -q
7 passed, 39 deselected in 0.77s

uv run pytest tests/services/test_chapter_orchestrator.py -k "l1_repair_context or l1_failure_after_repair_budget_exhausted or required_corrections_are_deterministic" -q
3 passed, 77 deselected in 0.62s

uv run pytest tests/fund/test_chapter_auditor.py -k "programmatic_audit_fails_l1 or programmatic_audit_allows_l1 or a_minus_c or formula_framework or ch2_source_section or l1_gap" -q
7 passed, 43 deselected in 0.45s

uv run pytest tests/fund/test_chapter_writer.py tests/services/test_chapter_orchestrator.py tests/fund/test_chapter_auditor.py -q
176 passed in 0.78s

uv run ruff check fund_agent/fund/chapter_writer.py tests/fund/test_chapter_writer.py tests/services/test_chapter_orchestrator.py tests/fund/test_chapter_auditor.py
All checks passed!

git diff --check
passed with no output
```

`git status --short` after implementation showed the intended current-gate files plus pre-existing unrelated workspace residue. The intended current-gate changed files are:

```text
 M fund_agent/fund/README.md
 M fund_agent/fund/chapter_writer.py
 M tests/fund/test_chapter_auditor.py
 M tests/fund/test_chapter_writer.py
 M tests/services/test_chapter_orchestrator.py
?? docs/reviews/provider-llm-chapter2-l1-narrow-no-live-fix-implementation-evidence-20260614.md
```

Pre-existing unrelated dirty/untracked files remain untouched, including `AGENTS.md`, root `README.md`, `docs/design.md`, multiple historical review/audit artifacts, `reports/`, `reviews/`, and user/data residue visible in `git status --short`.

## 6. README/doc staleness check

- `fund_agent/fund/README.md`: updated one current-behavior bullet because it explicitly documented the Chapter 2 writer prompt numerical-closure contract and became stale after the strengthened safe-output rule.
- `tests/README.md`: checked with targeted search for L1 / Chapter 2 / prompt wording. No stale stable-header or exact strengthened-contract text was present, so no change was needed.
- Control/design/startup docs were not modified.

## 7. Residuals

| Residual | Status | Owner / next handling |
|---|---|---|
| Live model behavior after strengthened prompt | Deferred | Future bounded live re-evidence gate only after implementation review/controller acceptance. |
| Repair budget calibration | Deferred | Separate gate; defaults unchanged here. |
| Chapter 5 forbidden phrase blocker | Deferred | Separate disposition/root-cause gate. |
| Release/readiness | `NOT_READY` | Preserved; this implementation does not claim readiness. |
| Existing unrelated workspace residue | Not part of this gate | Left untouched and unstaged. |

## 8. Final Verdict

VERDICT: IMPLEMENTED_READY_FOR_REVIEW_NOT_READY
