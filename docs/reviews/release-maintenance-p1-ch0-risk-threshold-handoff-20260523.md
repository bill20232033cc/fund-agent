# Release Maintenance P1 Handoff — Chapter 0 Risk And Threshold Slots

## Context

- Source: `docs/reviews/controller-judgment-repo-deepreview-20260523.md` accepted P1 finding:
  - 第 0 章 “当前最大的风险” 和 “什么变化会升级、降级或终止当前动作” 当前结构性不可满足。
- Current code evidence:
  - `fund_agent/fund/template/renderer.py` `_render_chapter_0()` hardcodes:
    - `当前最大的风险：数据不足，当前未提供独立最大风险排序输入。`
    - `什么变化会升级、降级或终止当前动作：数据不足，需要后续跨期证据确认。`
- Goal: stop emitting these two blanket insufficiency placeholders when existing structured inputs already contain usable risk/checklist/final-judgment signals.

## Implementation Scope

Worker owns this focused implementation:

- `fund_agent/fund/template/renderer.py`
- `tests/fund/template/test_renderer.py`
- `fund_agent/fund/README.md` and/or `tests/README.md` if current behavior documentation needs syncing
- Optional small helper functions inside `renderer.py`; prefer module-level private helpers over nested functions.

Do not modify:

- `docs/implementation-control.md`
- GitHub remote state
- Untracked historical input files

## Acceptance Criteria

- 第 0 章 `当前最大的风险` uses existing structured inputs instead of unconditional placeholder:
  - Prefer first `risk_check_result.veto_items`.
  - Else first `risk_check_result.watch_items`.
  - Else if no risk item needs action, output a concise pass/no-veto statement grounded in `risk_check_result.overall_status`.
- 第 0 章 `什么变化会升级、降级或终止当前动作` uses existing structured inputs:
  - Include at least one downgrade/terminate threshold from veto/watch/checklist/stress/final judgment reasons when present.
  - Include an upgrade threshold for `needs_attention` / `suggest_replace` when the current evidence has actionable red/yellow/gray/watch signals.
  - For all-green/pass cases, output a concrete monitoring threshold rather than blanket `数据不足`.
- Existing final judgment wording constraints remain intact: no direct buy/sell amount/timing/position advice.
- Preserve CHAPTER_CONTRACT required markers.
- Focused tests cover:
  - veto item becomes Chapter 0 largest risk.
  - watch item or checklist warning drives upgrade/downgrade text.
  - all-green/pass case does not emit the old blanket placeholder.
- Run focused pytest and ruff.

## Non-Goals

- Do not introduce LLM writing.
- Do not add new input fields to `TemplateRenderInput` unless strictly necessary.
- Do not change chapter count, evidence appendix format, or final judgment enum.
- Do not solve broader Alpha attribution or Evidence Confirm backlog.
