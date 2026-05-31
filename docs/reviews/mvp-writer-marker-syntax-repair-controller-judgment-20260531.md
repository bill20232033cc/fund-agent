# MVP writer marker syntax repair controller judgment

日期：2026-05-31

Gate：`MVP writer marker syntax repair gate`

角色：Gateflow controller，不是 implementation worker。

## Judgment

**ACCEPTED LOCALLY; REAL PROVIDER SMOKE STILL BLOCKED.**

本 gate 完成 plan / plan review / implementation / code review / validation / real-provider rerun。实现只调整 writer prompt 的 missing marker guidance：将旧的 Markdown code-span marker 指引替换为 explicit contract block，并把 allowed missing reasons token list 放在 marker contract 附近。Parser、allowed missing reasons、candidate facet、证据锚点、ITEM_RULE、交易建议、E2 deferred、missing semantics 和 no-fallback 边界未放松。

真实 provider smoke 仍未生成完整 0-7 章报告，但当前主 blocker 已从上一 gate 的 chapter 1 `writer:invalid_missing_marker` 前进到 chapter 2 programmatic audit。

## Evidence Read

- Plan：`docs/reviews/mvp-writer-marker-syntax-repair-plan-20260531.md`
- Plan reviews：`docs/reviews/mvp-writer-marker-syntax-repair-plan-review-mimo-20260531.md`; `docs/reviews/mvp-writer-marker-syntax-repair-plan-review-glm-20260531.md`
- Implementation evidence：`docs/reviews/mvp-writer-marker-syntax-repair-implementation-evidence-20260531.md`
- Code reviews：`docs/reviews/mvp-writer-marker-syntax-repair-code-review-mimo-20260531.md`; `docs/reviews/mvp-writer-marker-syntax-repair-code-review-glm-20260531.md`
- Previous diagnostic narrowing judgment：`docs/reviews/mvp-writer-prompt-contract-diagnostic-narrowing-controller-judgment-20260531.md`
- Controller evidence directory：`reports/mvp-local-acceptance/20260531-writer-marker-syntax-repair/`

## Implementation Accepted

Accepted implementation facts:

- `_MISSING_MARKER_RE`, `_invalid_marker_issues()` and `_parse_missing_markers()` acceptance behavior stayed strict.
- `ChapterFactMissingReason` and chapter-scoped `missing_reasons` were not expanded.
- New `_missing_marker_contract_prompt()` renders:
  - `MISSING_MARKER_CONTRACT`
  - `ALLOWED_MISSING_REASONS`
  - `MISSING_MARKER_EXACT_FORM`
  - placeholder replacement rule
  - no spacing/case/translation/fullwidth-colon/backtick/code-fence rule
  - no marker when allowed reasons are empty
- Invalid missing marker forms remain blocked and classify through `prompt_contract.invalid_marker`.
- `candidate_facet_assertion` remains a blocker and was not relaxed.

Code review outcome:

- MiMo code review：PASS.
- GLM code review：PASS.

## Validation

Controller reran:

| Command | Result |
|---|---|
| `uv run ruff check .` | PASS |
| `uv run pytest tests/fund/test_chapter_writer.py tests/services/test_chapter_orchestrator.py tests/ui/test_cli.py tests/config/test_llm_config.py tests/services/test_llm_provider.py -q` | PASS, `200 passed` |
| `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q` | PASS, `1176 passed`, coverage `91.84%` |
| `uv run fund-analysis analyze 006597 --report-year 2024` | PASS, exit `0` |
| `uv run fund-analysis checklist 006597 --report-year 2024` | PASS, exit `0` |
| missing-config `uv run fund-analysis analyze 006597 --report-year 2024 --use-llm` with LLM env unset | PASS fail-closed, exit `1`, stdout empty |
| real provider CLI `fund-analysis analyze 006597 --report-year 2024 --use-llm` | FAIL-CLOSED, exit `1`, stdout empty |
| real provider service diagnostic serialization | PASS command execution, safe JSON written |
| scoped secret scan over new docs/reports | PASS; policy-text hits only |

## Real Provider Evidence

CLI smoke:

- exit code：`1`
- stdout bytes：`0`
- stderr first-failed summary：chapter `2`, status `failed`, stop_reason `repair_budget_exhausted`, category `audit_rule_too_strict`, subcategory `unknown`
- no deterministic fallback

Service diagnostic:

- orchestration status：`partial`
- final assembly status：`incomplete`
- report markdown present：`False`

Sanitized chapter matrix:

| Chapter | Status | Stop reason | Category | Subcategory | Attempt count |
|---|---|---|---|---|---|
| 1 | `accepted` | `none` | `None` | `None` | 2 |
| 2 | `failed` | `repair_budget_exhausted` | `prompt_contract` | `code_bug_other` | 2 |
| 3 | `skipped` | `dependency_missing` | `fact_gap` | `None` | 0 |
| 4 | `skipped` | `dependency_missing` | `fact_gap` | `None` | 0 |
| 5 | `skipped` | `dependency_missing` | `fact_gap` | `None` | 0 |
| 6 | `skipped` | `dependency_missing` | `fact_gap` | `None` | 0 |

Chapter 2 phase detail:

- phase：`programmatic_audit`
- attempt_index：`1`
- primary_subcategory：`code_bug_other`
- issue_id_prefix_counts：`{"programmatic:L1": 2}`
- candidate_facet_assertion_count：`0`
- forbidden_phrase_count：`0`
- invalid_marker_count：`0`

Interpretation:

- The prior `writer:invalid_missing_marker` blocker is no longer first failure in the latest real-provider diagnostic.
- The current structured blocker is not a provider config/auth issue and not a missing-config issue.
- The current blocker is a programmatic audit L1 failure classification/calibration gap: audit prefix `programmatic:L1` currently falls through to `code_bug_other` in prompt-contract diagnostic subcategory, while CLI first-failed category reports `audit_rule_too_strict` after repair budget exhaustion.

## Secret Review

No API key value, bearer token, Authorization header, full prompt, full draft, full provider response or raw audit response was found in the new gate artifacts.

The scan only hit policy/test explanatory text such as `Authorization header` and `prompt.user_prompt`; these are not secret-bearing values.

## Controller Decision

This gate is accepted locally because it achieved the gate-specific goal:

- marker syntax guidance was repaired without parser relaxation;
- local validations and reviews passed;
- real provider progressed beyond the prior chapter 1 `writer:invalid_missing_marker` blocker;
- failure remains fail-closed with empty stdout and safe diagnostics.

Gate B real provider smoke acceptance remains **blocked** because the real provider still does not produce complete chapters 0-7.

## Next Minimal Entry

Start `MVP programmatic audit L1 calibration gate`.

Minimum scope:

- Do not revisit provider config/auth.
- Do not relax evidence anchors, ITEM_RULE, candidate facet, trading advice, E2 deferred or missing semantics.
- Investigate chapter 2 `programmatic:L1` after repair attempt: determine whether this is an overly strict audit rule, a writer output contract issue, or a diagnostic taxonomy gap.
- Preserve fail-closed behavior.
- If the issue is only taxonomy, map `programmatic:L1` into a precise next subcategory instead of `code_bug_other`.
- If the issue is true L1 numerical closure failure, repair writer prompt/output for that rule without weakening L1.
- Reuse safe service diagnostic JSON; do not store full prompt/draft/provider response.

External state remains unchanged: no push, no PR update, no merge, no release.
