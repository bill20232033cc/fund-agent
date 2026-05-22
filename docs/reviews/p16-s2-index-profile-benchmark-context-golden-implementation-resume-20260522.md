# P16-S2 Index Profile Benchmark-context Golden Implementation Resume（2026-05-22）

## Verdict

`IMPLEMENTED_P16_S2_GOLDEN_ROWS`

本次 resumed implementation 在 P16-S2.1 newline normalization 已接受后恢复执行 P16-S2 golden implementation。实现只添加 5 个 enhanced-index production candidates 的 25 条 `index_profile` scalar golden rows，并通过现有 `golden-build` 流程重建 strict JSON。

未修改 `docs/design.md`、`docs/implementation-control.md`、selected CSV、RR-13、source code、README、branch、commit、PR 或外部状态。未读取、引用、stage 或修改 `docs/design0522.md`、`docs/implementation-control0522.md`、`docs/repo-audit-20260521.md`。

## Changed Files

| File | Change |
|---|---|
| `reports/golden-answers/golden-answer-prefill-reviewed.md` | 追加 5 个 enhanced-index candidate 小节，每只基金 5 条 `index_profile` scalar rows。 |
| `reports/golden-answers/golden-answer.json` | 通过 `golden-build` 从 reviewed Markdown 重建；`fund_count=11`，`record_count=150`。 |
| `tests/fund/test_golden_answer.py` | 覆盖 strict JSON 中 25 条计划内 rows、禁止非计划字段、保留 `001548` 既有 rows。 |
| `tests/fund/test_extraction_snapshot.py` | 覆盖 composite `IndexProfileValue` 只序列化 scalar comparable values，省略 null/tuple 字段。 |
| `tests/fund/test_extraction_score.py` | 覆盖 composite scalar correctness match 与 mismatch。 |
| `tests/fund/test_quality_gate.py` | 覆盖 composite scalar correctness mismatch 经 FQ1 阻断。 |

## Exact Rows Added

| fund_code | sub_field | expected_value | source |
|---|---|---|---|
| `004194` | `benchmark_text` | `中证1000指数收益率×95%+同期银行活期存款利率（税后）×5%` | `年报2024 §2 page-5 page-5-table-1 benchmark` |
| `004194` | `benchmark_identity_status` | `composite` | `年报2024 §2 page-5 page-5-table-1 benchmark` |
| `004194` | `methodology_availability` | `benchmark_only` | `年报2024 §2 page-5 page-5-table-1 benchmark` |
| `004194` | `constituents_availability` | `benchmark_only` | `年报2024 §2 page-5 page-5-table-1 benchmark` |
| `004194` | `source_tier` | `benchmark_context` | `年报2024 §2 page-5 page-5-table-1 benchmark` |
| `005313` | `benchmark_text` | `中证1000指数收益率*95%＋一年期人民币定期存款利率（税后）*5%` | `年报2024 §2 page-5 page-5-table-1 benchmark` |
| `005313` | `benchmark_identity_status` | `composite` | `年报2024 §2 page-5 page-5-table-1 benchmark` |
| `005313` | `methodology_availability` | `benchmark_only` | `年报2024 §2 page-5 page-5-table-1 benchmark` |
| `005313` | `constituents_availability` | `benchmark_only` | `年报2024 §2 page-5 page-5-table-1 benchmark` |
| `005313` | `source_tier` | `benchmark_context` | `年报2024 §2 page-5 page-5-table-1 benchmark` |
| `017644` | `benchmark_text` | `中证1000指数收益率×95%+同期银行活期存款利率(税后)×5%` | `年报2024 §2 page-6 page-6-table-0 benchmark` |
| `017644` | `benchmark_identity_status` | `composite` | `年报2024 §2 page-6 page-6-table-0 benchmark` |
| `017644` | `methodology_availability` | `benchmark_only` | `年报2024 §2 page-6 page-6-table-0 benchmark` |
| `017644` | `constituents_availability` | `benchmark_only` | `年报2024 §2 page-6 page-6-table-0 benchmark` |
| `017644` | `source_tier` | `benchmark_context` | `年报2024 §2 page-6 page-6-table-0 benchmark` |
| `019918` | `benchmark_text` | `中证2000指数收益率*95%+中国人民银行人民币活期存款利率（税后）*5%` | `年报2024 §2 page-5 page-5-table-1 benchmark` |
| `019918` | `benchmark_identity_status` | `composite` | `年报2024 §2 page-5 page-5-table-1 benchmark` |
| `019918` | `methodology_availability` | `benchmark_only` | `年报2024 §2 page-5 page-5-table-1 benchmark` |
| `019918` | `constituents_availability` | `benchmark_only` | `年报2024 §2 page-5 page-5-table-1 benchmark` |
| `019918` | `source_tier` | `benchmark_context` | `年报2024 §2 page-5 page-5-table-1 benchmark` |
| `019923` | `benchmark_text` | `中证2000指数收益率×95%＋人民币活期存款税后利率×5%` | `年报2024 §2 page-6 page-6-table-0 benchmark` |
| `019923` | `benchmark_identity_status` | `composite` | `年报2024 §2 page-6 page-6-table-0 benchmark` |
| `019923` | `methodology_availability` | `benchmark_only` | `年报2024 §2 page-6 page-6-table-0 benchmark` |
| `019923` | `constituents_availability` | `benchmark_only` | `年报2024 §2 page-6 page-6-table-0 benchmark` |
| `019923` | `source_tier` | `benchmark_context` | `年报2024 §2 page-6 page-6-table-0 benchmark` |

All rows use `confidence=high`.

## Stop Condition Status

| Stop condition | Status |
|---|---|
| Current extractor output differs from accepted expected values | PASS; preflight verified all five benchmark texts match accepted values and contain no embedded newline. |
| Need `tracking_error`, `benchmark_index_name`, `benchmark_component_text`, detail, missing reason, or non-plan fields | PASS; none added. |
| Need direct PDF/cache/source helper, CSV, RR-13, design/control, or external state | PASS; none touched. |
| Existing golden records, especially `001548`, preserved | PASS; tests verify `001548` index_profile rows unchanged. |

## Commands And Results

| Command | Result |
|---|---|
| `.venv/bin/python - <<'PY' ... FundDataExtractor(nav_provider=EmptyNavProvider()).extract(...) ... PY` | PASS. `004194`、`005313`、`017644`、`019918`、`019923` benchmark_text matched accepted values, no embedded newline, all `enhanced_index` / `composite` / `benchmark_only` / `benchmark_context`, no synthesized `benchmark_index_name`. |
| `.venv/bin/python -m fund_agent.ui.cli golden-build --input-path reports/golden-answers/golden-answer-prefill-reviewed.md --output-path reports/golden-answers/golden-answer.json` | PASS. Output `funds: 11`, `records: 150`, `skipped: 29`. |
| `.venv/bin/python - <<'PY' ... strict JSON row verification ... PY` | PASS. Confirmed exact 25 planned rows, no forbidden rows, and `001548` rows preserved. |
| `.venv/bin/python -m pytest tests/fund/test_golden_answer.py tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py -q` | PASS. `61 passed in 0.45s`. |
| `.venv/bin/python -m ruff check fund_agent tests` | PASS. `All checks passed!` |
| `git diff --check HEAD` | PASS. No whitespace errors. |
| `.venv/bin/python -m pytest -q` | PASS. `439 passed in 0.95s`. |

## README Update Decision

No README update required. This gate adds curated golden answer rows and focused tests; it does not change public CLI usage, package architecture, Engine/Fund contracts, config defaults, test organization, or documented template structure. Existing README descriptions of strict golden answer, comparable scalar correctness, and conditional `index_profile` quality behavior remain accurate.

## Residual Risks

- `benchmark_index_name=null` and `benchmark_component_text` tuple semantics remain intentionally outside current strict golden denominator. This is covered by tests that omit null/tuple comparable values and by the absence of forbidden golden rows.
- `tracking_error` production golden expansion remains blocked for these five candidates until a future reviewed direct observed disclosure evidence gate accepts eligible rows.
