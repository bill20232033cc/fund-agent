# Provider/LLM Chapter 2 L1 Narrow No-live Fix Implementation Review

Date: 2026-06-14

Role: AgentDS review worker

Gate: `Provider/LLM Chapter 2 L1 Numerical Closure Narrow No-live Fix Implementation Gate`

Verdict: `PASS`

## 1. Scope

- Mode: current changes (uncommitted implementation diff for this gate only)
- Branch: `feat/mvp-llm-incomplete-run-artifacts`
- Base: controller judgment accepted plan at `d5a643e` via `docs/reviews/provider-llm-chapter2-l1-narrow-no-live-fix-plan-controller-judgment-20260614.md`
- Output file: `docs/reviews/provider-llm-chapter2-l1-narrow-no-live-fix-implementation-review-ds-20260614.md`
- Included scope:
  - `fund_agent/fund/chapter_writer.py` — `_ch2_numerical_closure_contract_prompt()` and `_ch2_l1_repair_guidance_prompt()` only
  - `tests/fund/test_chapter_writer.py` — updated header assertions, compact prompt assertions
  - `tests/services/test_chapter_orchestrator.py` — updated repair guidance assertions, preserved auditor-output assertions
  - `tests/fund/test_chapter_auditor.py` — new safe gap/minimum-verification test
  - `fund_agent/fund/README.md` — single bullet synchronization
  - `docs/reviews/provider-llm-chapter2-l1-narrow-no-live-fix-implementation-evidence-20260614.md` — implementation evidence artifact
- Excluded scope: pre-existing unrelated workspace residue (`AGENTS.md`, root `README.md`, `docs/design.md`, untracked `docs/reviews/`, `reports/`, `reviews/`, user/data residue); `tests/README.md` (checked, not stale)
- Parallel review coverage: 无

## 2. Evidence Reviewed

| Evidence | Use |
|---|---|
| `AGENTS.md` | Execution truth, module boundaries, hard constraints |
| `docs/current-startup-packet.md` §4 Current Gate Scope | Gate boundaries, allowed/prohibited actions |
| `docs/implementation-control.md` §Current Gate | Control truth, implementation constraints |
| `docs/reviews/provider-llm-chapter2-l1-narrow-no-live-fix-plan-controller-judgment-20260614.md` | Binding controller amendments (1-9) |
| `docs/reviews/provider-llm-chapter2-l1-narrow-no-live-fix-implementation-evidence-20260614.md` | Implementation self-report and validation results |
| `git diff` for all five target implementation files | Direct source/test change evidence |
| `fund_agent/fund/chapter_writer.py` lines 1258-1318, 1458-1481 | Prompt function implementations, `_repair_context_prompt()` verification |
| `tests/fund/test_chapter_writer.py` lines 483-560, 1197-1257 | Writer test assertions |
| `tests/services/test_chapter_orchestrator.py` lines 1516-1567 | Orchestrator repair and fail-closed tests |
| `tests/fund/test_chapter_auditor.py` lines 860-910 | Auditor safe-gap and unanchored-failure tests |

No writer Markdown, auditor feedback Markdown, repair Markdown, raw prompts, provider payloads, source/PDF/cache body or final report body was read.

## 3. Findings

未发现实质性问题。

### Controller Amendment Compliance Verification

Each binding amendment from the controller judgment was verified against direct source/diff evidence:

| # | Amendment | Evidence | Result |
|---|---|---|---|
| 1 | `_repair_context_prompt()` unchanged | `git diff` shows zero change to line 1458-1481; function body confirmed identical at lines 1471-1480 | 通过 |
| 2 | Source changes limited to Ch2-specific prompt functions | `git diff -- fund_agent/fund/chapter_writer.py` only touches `_ch2_numerical_closure_contract_prompt()` (lines 1260-1268) and `_ch2_l1_repair_guidance_prompt()` (lines 1308-1318) | 通过 |
| 3 | Stable initial header `第2章 L1 数字闭环安全输出契约` | Present at `chapter_writer.py:1261`; asserted in `test_chapter_writer.py:486`, `test_chapter_writer.py:556`, `test_chapter_writer.py:511` (non-ch2 absent) | 通过 |
| 4 | Stable repair header `第2章 L1 repair 必须改写规则` | Present at `chapter_writer.py:1310`; asserted in `test_chapter_writer.py:1200`, `test_chapter_orchestrator.py:1541`, `test_chapter_writer.py:1255-1257` (absent outside ch2+L1) | 通过 |
| 5 | Tests assert new stable headers; old assertions removed | Old `"第2章 R=A+B-C 数字闭环"` replaced by new header in writer test at line 486; old `"repair checklist"` replaced by `"repair 必须改写规则"` in writer test at line 1200 and orchestrator test at line 1541; compact prompt updated at line 556; non-ch2 exclusion test updated at lines 511-512 | 通过 |
| 6 | Compact prompt coverage maintained | `test_compact_prompt_payload_preserves_fact_and_anchor_contract` (line 556-557) asserts `"第2章 L1 数字闭环安全输出契约"` and `"不写具体百分比，改写为数据不足/下一步最小验证问题"` survive compact mode | 通过 |
| 7 | No-live failure coverage for ignored/unanchored percentages | `test_l1_failure_after_repair_budget_exhausted_keeps_l1_subcategory` (line 1550-1567) proves `status=="failed"`, `stop_reason=="repair_budget_exhausted"`, `failure_category=="prompt_contract"`, `failure_subcategory=="l1_numerical_closure"` with `max_repair_attempts=1` | 通过 |
| 8 | Safe gap/minimum-verification auditor coverage | New test `test_programmatic_audit_allows_l1_gap_minimum_verification_without_concrete_percentage` (line 869-891) proves `数据不足…下一步最小验证问题` output passes L1 without triggering; existing `test_programmatic_audit_allows_l1_formula_framework_without_concrete_percentage` (line ~854-866) remains for formula-only case | 通过 |
| 9 | Full three-file no-live suite passed | Evidence reports: focused tests `7+3+7 passed`, full suite `176 passed`, ruff `All checks passed`, `git diff --check` no output | 通过 |

### Scope Boundary Verification

- Repair budget default: `max_repair_attempts=1` preserved in orchestrator test at line 1529 and fail-closed test at line 1559
- L1 fail-closed: `test_l1_failure_after_repair_budget_exhausted_keeps_l1_subcategory` unchanged except for updated writer prompt assertions
- `_has_l1_numerical_closure_repair_issue()` gate function: unchanged (not in diff), still uses `issue_id.startswith("programmatic:L1")`
- EID single-source/no-fallback: untouched
- Service/Host/provider/source-policy: untouched
- `NOT_READY`: preserved
- Forbidden files: no change to `docs/design.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md`, root `README.md`, `pyproject.toml`, `.gitignore`, or any source acquisition/provider/model files

### Fund README Update

- Change is a single bullet at `fund_agent/fund/README.md:181`: old wording describing two-section rule replaced by consolidated wording matching the new initial contract prompt (Alpha/Beta/Cost coverage, source-label-as-anchor prohibition, data-gap/minimum-verification fallback)
- Update is necessary because the old bullet explicitly described the Chapter 2 writer prompt's numerical-closure contract that was changed
- Update is bounded: one line changed, no terminology drift, no new claims
- `tests/README.md` was checked and left unchanged because it does not document Chapter 2 L1 headers or exact prompt wording — acceptable

### Implementation Quality Observations

These are observations, not defects:

- **Orchestrator test auditor-output assertions preserved**: `test_l1_repair_context_guides_anchored_correction_and_accepts_after_repair` (lines 1538-1540) still asserts old auditor-generated `required_corrections` strings (`"第2章 R=A+B-C 数字闭环"`, etc.). This is correct because the auditor (`chapter_auditor.py`) was not in scope and its deterministic output is unchanged. The test properly separates auditor-output assertions from writer-prompt assertions.
- **Repair guidance strength**: New repair prompt is more prescriptive than old checklist — step 1 is explicit deletion, step 2 is conditional re-add, step 5 is a concrete token-scan self-check. This directly addresses the repair-effectiveness regression hypothesis (H3 root cause).
- **Initial prompt binary framing**: `只能二选一` replaces the old softer guidance, removing ambiguity about whether approximate/unanchored percentages are acceptable.

## 4. Residuals

| Residual | Status | Owner / next handling |
|---|---|---|
| Auditor `required_corrections` strings use old terminology `"第2章 R=A+B-C 数字闭环"` vs new stable header `"第2章 L1 数字闭环安全输出契约"` | Expected under current gate scope; auditor was not in write set | Future gate if terminology consistency is desired |
| Live model behavior after strengthened prompt | Deferred | Future bounded live re-evidence gate |
| Repair budget calibration | Deferred | Separate gate |
| Chapter 5 forbidden phrase blocker | Deferred | Separate disposition/root-cause gate |
| Release/readiness | `NOT_READY` | Preserved |

## 5. Verdict

`PASS`

All nine controller amendments are satisfied with direct source/test evidence. Source changes are limited to the two Chapter 2-specific prompt functions. Stable headers are present and asserted in all three test files. L1 fail-closed semantics and repair budget defaults are preserved. Compact prompt, ignored/unanchored failure, and safe gap/minimum-verification coverage are all demonstrated. No forbidden files were modified. No material defects found.
