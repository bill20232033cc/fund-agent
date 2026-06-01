# MVP real provider smoke prompt-contract calibration plan controller judgment

日期：2026-05-31

Gate：`MVP real provider smoke acceptance rerun with prompt-contract calibration`

角色：Gateflow controller，不是 planning、implementation 或 review worker。

## Judgment

**Plan accepted for implementation.**

Accepted plan：

- `docs/reviews/mvp-real-provider-smoke-prompt-contract-calibration-plan-20260531.md`

Plan fix：

- `docs/reviews/mvp-real-provider-smoke-prompt-contract-calibration-plan-fix-20260531.md`

Independent reviews：

- `docs/reviews/mvp-real-provider-smoke-prompt-contract-calibration-plan-review-mimo-20260531.md` — PASS with non-blocking findings
- `docs/reviews/mvp-real-provider-smoke-prompt-contract-calibration-plan-review-glm-20260531.md` — pass-with-risks
- `docs/reviews/mvp-real-provider-smoke-prompt-contract-calibration-plan-rereview-glm-20260531.md` — PASS

## Controller Finding Disposition

| Finding | Decision | Resolution |
|---|---|---|
| GLM F1: `llm_timeout` dual classification ambiguity | accepted | Plan now mandates code-level `ChapterFailureCategory` expansion with `llm_timeout` as an independent category; timeout diagnostics/category return `llm_timeout`, non-timeout provider runtime remains `provider_runtime`. |
| GLM F2: CLI `first_failed_category` extraction path unspecified | accepted with amendment | Plan now mandates `ChapterRunResult.failure_category: ChapterFailureCategory | None`; CLI reads that top-level field only and does not traverse nested diagnostics. |
| GLM F3: `audit_rule_too_strict` trigger missing | accepted | Plan now mandates code-level `audit_rule_too_strict` and four-condition trigger: programmatic pass, parseable LLM fail/blocked/reviewable issue, no `llm:parse_failure`, no fact-gap / `needs_more_facts`. |
| GLM F4 / MiMo F1: `llm_empty_response` and section reference inconsistencies | accepted | Plan now maps `llm_empty_response` to `prompt_contract` and references Section 7.4 taxonomy instead of smoke evidence policy. |
| MiMo F2: taxonomy vs current Literal relationship unclear | accepted | Plan now states taxonomy is a code-level `ChapterFailureCategory` extension, not evidence-only. |

## Accepted Scope

Implementation worker may work only within the accepted plan’s allowed files:

- `fund_agent/fund/chapter_writer.py`
- `fund_agent/fund/chapter_auditor.py`
- `fund_agent/services/chapter_orchestrator.py`
- `fund_agent/services/llm_provider.py`
- `fund_agent/ui/cli.py`
- `tests/fund/test_chapter_writer.py`
- `tests/fund/test_chapter_auditor.py`
- `tests/services/test_chapter_orchestrator.py`
- `tests/services/test_llm_provider.py`
- `tests/ui/test_cli.py`
- README files only if current behavior/docs require synchronization
- implementation evidence under `docs/reviews/`
- sanitized smoke evidence under `reports/mvp-local-acceptance/20260531-prompt-contract-calibration/`

Implementation worker must not edit control docs, design docs, template, golden/fixtures/score/quality gate, Host/Agent/dayu, PR state, or unrelated dirty files.

## Required Implementation Decisions

- Writer prompt calibration must reduce model cognitive load while preserving fail-closed parser behavior.
- Auditor protocol calibration must keep parse failure blocked and classified as `audit_parse`.
- Repair/regenerate remains bounded; regenerate input must include sanitized previous failure reasons.
- `ChapterFailureCategory` must include at least `llm_timeout` and `audit_rule_too_strict`.
- `ChapterRunResult.failure_category` is the sole source for CLI `first_failed_category`.
- `llm_timeout` is an independent failure category; non-timeout provider runtime remains `provider_runtime`.
- `audit_rule_too_strict` must not override programmatic failures or fact gaps.
- Default deterministic `analyze` / `checklist` behavior must remain unchanged.

## Validation Required Before Code Review

- `uv run ruff check .`
- Targeted pytest for writer/auditor/orchestrator/provider/CLI path
- `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q`
- deterministic analyze/checklist smoke
- missing-config `--use-llm` fail-closed smoke
- real provider `uv run fund-analysis analyze 006597 --report-year 2024 --use-llm`
- secret leak scan over new reports and implementation evidence

## External State

No push, PR update, merge, release, mark-ready, reviewer request or external action is authorized by this judgment.
