# MVP writer prompt contract diagnostic narrowing controller judgment

日期：2026-05-31

Gate：`MVP writer prompt contract diagnostic narrowing gate`

角色：Gateflow controller，不是 implementation worker。

## Judgment

**ACCEPTED LOCALLY AS DIAGNOSTIC GATE; REAL PROVIDER SMOKE STILL BLOCKED.**

本 gate 已完成 plan / plan review / implementation / code review / validation / real-provider diagnostic rerun。实现只增加脱敏 prompt-contract 诊断和 `failure_subcategory`，没有放松证据锚点、ITEM_RULE、candidate facet、交易建议、E2 deferred、missing semantics，也没有 deterministic fallback。

`006597 / 2024 --use-llm` 仍未生成完整 0-7 章报告。当前主 blocker 不再是 provider config/auth，也不是缺配置；最新结构化 service diagnostic 将首个失败定位为：

- chapter：`1`
- phase：`writer_parse`
- stop_reason：`llm_contract_violation`
- failure_category：`prompt_contract`
- primary subcategory：`invalid_marker`
- issue prefix：`writer:invalid_missing_marker`

同一 gate 的 CLI smoke 复跑也 fail-closed，stdout empty，无 deterministic fallback；该次 live output 的 first failed summary 为 chapter `1` / `repair_budget_exhausted` / `prompt_contract` / `candidate_facet_assertion`。这说明真实 provider 输出仍有波动，但失败已经稳定停留在 writer prompt-contract 安全边界内，且当前结构化矩阵给出了下一最小修复入口。

## Evidence Read

- Plan：`docs/reviews/mvp-writer-prompt-contract-diagnostic-narrowing-plan-20260531.md`
- Plan reviews：`docs/reviews/mvp-writer-prompt-contract-diagnostic-narrowing-plan-review-mimo-20260531.md`; `docs/reviews/mvp-writer-prompt-contract-diagnostic-narrowing-plan-review-glm-20260531.md`
- Implementation evidence：`docs/reviews/mvp-writer-prompt-contract-diagnostic-narrowing-implementation-evidence-20260531.md`
- Code reviews：`docs/reviews/mvp-writer-prompt-contract-diagnostic-narrowing-code-review-mimo-20260531.md`; `docs/reviews/mvp-writer-prompt-contract-diagnostic-narrowing-code-review-glm-20260531.md`
- Controller evidence directory：`reports/mvp-local-acceptance/20260531-writer-prompt-contract-diagnostic-narrowing/`

## Implementation Accepted

Accepted implementation facts:

- `ChapterRunResult.failure_subcategory` is a safe scalar, `None` for accepted chapters.
- `ChapterPromptContractDiagnostic` records typed counts and scalar fields only.
- Writer result carries only `response_chars`, `finish_reason`, and `max_output_chars`; no raw response text.
- `issue_id_prefix_counts` strips raw anchor ids, missing reason suffixes, facet text, phrase text and location suffixes.
- CLI incomplete-result stderr adds only `first_failed_subcategory=<value>`.
- `serialize_chapter_prompt_contract_diagnostics()` serializes chapter/phase matrix without prompt, draft, provider response, audit raw response, API key or Authorization header.

Code review outcome:

- MiMo code review：PASS.
- GLM code review：PASS.
- Non-blocking observations were cleanup/wording risks only; no safety or correctness blocker.

## Validation

Controller reran:

| Command | Result |
|---|---|
| `uv run ruff check .` | PASS |
| `uv run pytest tests/fund/test_chapter_writer.py tests/services/test_chapter_orchestrator.py tests/ui/test_cli.py -q` | PASS, `137 passed` |
| `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q` | PASS, `1169 passed`, coverage `91.83%` |
| `uv run fund-analysis analyze 006597 --report-year 2024` | PASS, exit `0` |
| `uv run fund-analysis checklist 006597 --report-year 2024` | PASS, exit `0` |
| missing-config `uv run fund-analysis analyze 006597 --report-year 2024 --use-llm` with LLM env unset | PASS fail-closed, exit `1`, stdout empty |
| real provider CLI `fund-analysis analyze 006597 --report-year 2024 --use-llm` | FAIL-CLOSED, exit `1`, stdout empty |
| real provider service diagnostic serialization | PASS command execution, safe JSON written |
| secret scan over new docs/reports | PASS with safe policy-text hits only |

Real provider CLI evidence:

- `reports/mvp-local-acceptance/20260531-writer-prompt-contract-diagnostic-narrowing/controller-real-provider-006597-2024.exitcode`
- `reports/mvp-local-acceptance/20260531-writer-prompt-contract-diagnostic-narrowing/controller-real-provider-006597-2024.stdout`
- `reports/mvp-local-acceptance/20260531-writer-prompt-contract-diagnostic-narrowing/controller-real-provider-006597-2024.stderr`

Real provider service diagnostic evidence:

- `reports/mvp-local-acceptance/20260531-writer-prompt-contract-diagnostic-narrowing/controller-real-provider-006597-2024-diagnostic.json`
- `reports/mvp-local-acceptance/20260531-writer-prompt-contract-diagnostic-narrowing/controller-real-provider-006597-2024-diagnostic.exitcode`
- `reports/mvp-local-acceptance/20260531-writer-prompt-contract-diagnostic-narrowing/controller-real-provider-006597-2024-diagnostic.stderr`

## Sanitized Matrix Summary

Latest structured diagnostic:

| Chapter | Status | Stop reason | Category | Subcategory | Attempt count |
|---|---|---|---|---|---|
| 1 | `blocked` | `llm_contract_violation` | `prompt_contract` | `invalid_marker` | 1 |
| 2 | `skipped` | `dependency_missing` | `fact_gap` | `None` | 0 |
| 3 | `skipped` | `dependency_missing` | `fact_gap` | `None` | 0 |
| 4 | `skipped` | `dependency_missing` | `fact_gap` | `None` | 0 |
| 5 | `skipped` | `dependency_missing` | `fact_gap` | `None` | 0 |
| 6 | `skipped` | `dependency_missing` | `fact_gap` | `None` | 0 |

Chapter 1 phase detail:

- phase：`writer_parse`
- attempt_index：`0`
- primary_subcategory：`invalid_marker`
- issue_reason_counts：`{"llm_contract_violation": 1}`
- issue_id_prefix_counts：`{"writer:invalid_missing_marker": 1}`
- candidate_facet_assertion_count：`0`
- forbidden_phrase_count：`0`

## Secret Review

No API key, bearer token value, Authorization header, full prompt, full draft, full provider response or raw audit response was found in the new diagnostic artifacts.

The `rg` scan produced policy-text hits such as "do not save prompt" and code-review explanations such as `len(raw_response)`; these are not secret-bearing content and do not include raw response bodies.

## Controller Decision

This diagnostic narrowing gate is accepted locally because it achieved the gate-specific outcome: real provider failure remains fail-closed and now has a safe chapter/phase/subcategory matrix.

Gate B real provider smoke acceptance remains **blocked** because the real provider still does not produce complete chapters 0-7.

Unique current main blocker for the next gate:

- `prompt_contract.invalid_marker` in chapter `1`, phase `writer_parse`, issue prefix `writer:invalid_missing_marker`.

Secondary observed live-output risk:

- CLI smoke also observed `prompt_contract.candidate_facet_assertion` after `repair_budget_exhausted`; this should remain a safety boundary and must not be treated as pass.

## Next Minimal Entry

Start `MVP writer marker syntax repair gate`.

Minimum scope:

- Focus on writer prompt/marker syntax calibration for allowed missing marker forms.
- Preserve strict parser fail-closed behavior.
- Do not broaden allowed missing reasons or anchors to force pass.
- Keep candidate facet assertion as a secondary monitored subcategory; if marker syntax is fixed and candidate facet becomes first failure, route to `MVP candidate facet assertion repair gate`.
- Reuse `serialize_chapter_prompt_contract_diagnostics()` for evidence.

External state remains unchanged: no push, no PR update, no merge, no release.
