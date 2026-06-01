# MVP programmatic audit L1 calibration controller judgment

日期：2026-05-31

Gate：`MVP programmatic audit L1 calibration gate`

角色：Gateflow controller，不是 implementation worker。

## Decision

**Local accepted for L1 calibration; Gate B real provider smoke remains blocked.**

本 gate 的 L1 taxonomy / repair guidance / writer prompt calibration 已通过 plan review、implementation review 和本地验证。`programmatic:L1` 不再停留在 `code_bug_other` / CLI `unknown` 的诊断盲区；本地 fake/service 路径会归类为 `l1_numerical_closure`，并且 unsafe L1 cases 仍 fail-closed。

真实 provider acceptance 仍未通过：authoritative CLI smoke `fund-analysis analyze 006597 --report-year 2024 --use-llm` exit `1`、stdout empty、无 deterministic fallback。唯一主 blocker 以 CLI 验收命令为准：chapter `1` / stop_reason `llm_timeout` / category `llm_timeout` / subcategory `unknown`。这不是 provider config/auth。

补充 service-level diagnostic 在另一次真实 provider 调用中越过 chapter 1-2，并定位到下一层次问题：chapter `3` / phase `programmatic_audit` / issue prefixes `programmatic:C2` + `llm:0:blocking` / category `prompt_contract` / subcategory `code_bug_other`。该结果作为后续诊断入口记录，但不覆盖本次 CLI smoke 的主 blocker。

## Evidence

| Evidence | Result |
|---|---|
| Branch | `codex/local-reconciliation` |
| Dirty scope | Large local accepted gate stack plus current gate artifacts; no push/PR/merge/release performed |
| Plan | `docs/reviews/mvp-programmatic-audit-l1-calibration-plan-20260531.md` |
| Plan reviews | `docs/reviews/mvp-programmatic-audit-l1-calibration-plan-review-mimo-20260531.md`; `docs/reviews/mvp-programmatic-audit-l1-calibration-plan-review-glm-20260531.md` |
| Implementation evidence | `docs/reviews/mvp-programmatic-audit-l1-calibration-implementation-evidence-20260531.md` |
| Code reviews | `docs/reviews/mvp-programmatic-audit-l1-calibration-code-review-mimo-20260531.md`; `docs/reviews/mvp-programmatic-audit-l1-calibration-code-review-glm-20260531.md` |
| CLI smoke evidence | `reports/mvp-local-acceptance/20260531-programmatic-audit-l1-calibration/controller-real-provider-006597-2024.stderr`; `.exitcode`; `.stdout` |
| Service diagnostic evidence | `reports/mvp-local-acceptance/20260531-programmatic-audit-l1-calibration/controller-real-provider-006597-2024-diagnostic.json`; `.exitcode`; `.stderr` |

## Validation

| Command | Result |
|---|---|
| `uv run ruff check fund_agent/fund/chapter_auditor.py fund_agent/fund/chapter_writer.py fund_agent/services/chapter_orchestrator.py tests/fund/test_chapter_auditor.py tests/fund/test_chapter_writer.py tests/services/test_chapter_orchestrator.py tests/ui/test_cli.py` | PASS |
| `uv run pytest tests/fund/test_chapter_auditor.py tests/fund/test_chapter_writer.py tests/services/test_chapter_orchestrator.py tests/ui/test_cli.py -q` | PASS, `180 passed` |
| `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q` | PASS, `1186 passed`, total coverage `91.85%` |
| `uv run fund-analysis analyze 006597 --report-year 2024` | PASS, exit `0` |
| `uv run fund-analysis checklist 006597 --report-year 2024` | PASS, exit `0` |
| isolated missing-config `--use-llm` with LLM env unset | PASS fail-closed, exit `1`, stdout bytes `0` |
| `git diff --check` | PASS |
| real provider `fund-analysis analyze 006597 --report-year 2024 --use-llm` | BLOCKED, exit `1`, stdout bytes `0`, no deterministic fallback; first failed chapter `1`, `llm_timeout` |
| service-level real provider diagnostic | exit `0` diagnostic capture; orchestration `partial`, final assembly `incomplete`, report absent; chapters `1` and `2` accepted, chapter `3` failed in `programmatic_audit` with `programmatic:C2` |
| scoped secret scan over current gate docs/reports/control docs | PASS, no matches for API key, Authorization header, bearer token, full prompt, full draft or raw response patterns |

## Safety Judgment

- L1 audit rule was not relaxed. `_audit_numerical_closure()` and its anchor proximity semantics remain fail-closed.
- Candidate facet and forbidden phrase precedence remain higher than `l1_numerical_closure`.
- Repair guidance requires same-sentence or +/-2-line allowed anchor for formula/percentage closure, or deletion of unsupported numeric closure into missing/data-gap semantics.
- No golden, fixtures, score, quality gate, final judgment, Host/Agent/dayu, provider config/auth, PR state, push, merge or release changes were made.
- No full prompt, full draft, full provider response, raw audit response, API key or Authorization header was stored in the current gate evidence.

## Blocker Classification

Primary blocker for Gate B acceptance:

- Category: `llm_timeout`
- Chapter: `1`
- Phase: provider-backed writer/repair path as surfaced by CLI first-failed summary
- Evidence: `controller-real-provider-006597-2024.stderr`
- Minimum next entry: `MVP provider runtime timeout follow-up gate`

Secondary diagnostic to carry forward after timeout is stabilized:

- Category: `prompt_contract`
- Subcategory: `code_bug_other`
- Chapter: `3`
- Phase: `programmatic_audit`
- Issue prefixes: `programmatic:C2`, `llm:0:blocking`
- Evidence: `controller-real-provider-006597-2024-diagnostic.json`
- Minimum next entry after timeout is no longer the first blocker: `MVP programmatic audit C2 calibration gate`

## Controller Judgment

Accept this L1 calibration gate locally because it solved the intended L1 diagnostic/repair gap without weakening audit boundaries and all required local validations passed.

Do not accept Gate B real provider smoke. The next controller step must not return to provider config/auth. It should first handle the current authoritative CLI blocker, `llm_timeout` at chapter 1, with a bounded provider runtime follow-up. If a rerun then consistently reaches chapter 3, start a narrow C2 calibration gate using the safe service diagnostic evidence.
