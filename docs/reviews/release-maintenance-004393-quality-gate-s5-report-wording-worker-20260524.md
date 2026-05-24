# Release Maintenance 004393 S5 Report Wording Worker

## Scope

- Worker role: Gateflow specialist worker.
- Branch: `codex/checklist-host-engine-design`.
- Current gate: release maintenance 004393 S5 end-to-end quality gate verification.
- Objective: fix the renderer wording false positive where annual-report disclosure text such as `买入并持有` was treated as direct investment advice.

## Root Cause

`fund_agent/fund/template/renderer.py` used whole-report substring matching for `买入` and `卖出`.
That conflated direct trading advice with disclosed annual-report source text and methodology phrases rendered as evidence-backed content.

This is not an FQ1/FQ2 quality gate mismatch. The failure happened later in the template renderer wording validator.

## Changes

- Updated `fund_agent/fund/template/renderer.py`.
  - Replaced the broad `买入` / `卖出` term ban with explicit prohibited report phrases: `买入金额`, `卖出时机`, `仓位比例`, `收益预测`.
  - Added context-based direct trading advice detection for phrases such as `建议买入`, `建议卖出`, `推荐加仓`, and `应该减仓`.
  - Kept the final judgment contract unchanged: renderer still only allows `worth_holding`, `needs_attention`, and `suggest_replace`.
- Updated `tests/fund/template/test_renderer.py`.
  - Added validator coverage proving explicit trading advice remains rejected.
  - Added renderer coverage proving disclosed `买入并持有好公司` text no longer blocks report rendering.
  - Kept regression coverage that rendered reports do not emit `建议买入` / `建议卖出`, `收益预测`, or `仓位比例`.

## Validation

- `uv run pytest tests/fund/template/test_renderer.py -q`
  - Result: `54 passed`.
- `uv run ruff check fund_agent/fund/template/renderer.py tests/fund/template/test_renderer.py`
  - Result: passed.
- `uv run fund-analysis analyze 004393 --report-year 2024 --quality-gate-policy block`
  - Result: passed.
  - `quality_gate_status: warn`
  - Latest generated quality gate run: `reports/quality-gate-runs/analyze-004393-2024-20260524T015852936729Z`.
  - The rendered report includes the annual-report disclosure context `买入并持有`, and no longer fails with `报告包含禁用投资建议措辞：买入`.
- `git diff --check -- fund_agent/fund/template/renderer.py tests/fund/template/test_renderer.py`
  - Result: passed.

## Residual Risk

- The direct-advice detector is intentionally phrase/context based. It does not attempt full natural-language classification of every possible trading instruction.
- The smoke currently finishes with `quality_gate_status: warn`; this worker only fixes the downstream renderer wording false positive and does not change quality gate scoring, extraction, golden answers, config, runtime, or implementation-control state.
- Existing unrelated workspace changes were left untouched.
