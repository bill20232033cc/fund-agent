# MVP real-provider stabilization and score-loop phase controller judgment

日期：2026-05-31

Phase：`MVP real-provider stabilization and score-loop phase`

角色：Phaseflow controller。本文记录本地 phase closeout，不 push、不创建或更新 PR、不 merge、不 release。

## Judgment

结论：`blocked_with_accepted_local_work`

- Gate A `MVP LLM writer/auditor contract hardening gate`：`local_accepted_with_next_gate_timeout_blocker`
- Gate B `MVP real provider smoke acceptance gate`：`blocked`
- Gate C `MVP chapter generation score loop design gate`：`accepted_design_only`

本 phase 已完成本地 plan / review / implementation / review / validation / controller judgment / control-doc update 闭环。真实 provider MVP smoke 尚未 accepted，当前最小 blocker 是 provider runtime timeout。

## Gate A Summary

Gate A 已本地接受。实现内容：

- writer prompt/parser 增加固定结构段落、exact `required_output` marker、未知 anchor、超长、incomplete finish reason 等 fail-closed 分类。
- auditor required output 审计改为 exact marker，LLM audit line protocol parse failure 保持 blocked。
- regenerate 增加 typed `ChapterRepairContext`，携带上一轮失败原因和确定性 corrections。
- provider runtime timeout/network/rate-limit/malformed response 映射到精确 Service stop reason。
- 默认 deterministic `analyze/checklist` 行为未改变。

关键 artifacts：

- `docs/reviews/mvp-llm-writer-auditor-contract-hardening-controller-judgment-20260531.md`
- `docs/reviews/mvp-llm-writer-auditor-contract-hardening-implementation-evidence-20260531.md`
- `docs/reviews/mvp-llm-writer-auditor-contract-hardening-code-rereview-mimo-20260531.md`
- `docs/reviews/mvp-llm-writer-auditor-contract-hardening-code-rereview-glm-20260531.md`

Validation：

- `uv run ruff check .`：PASS
- targeted pytest：PASS，`155 passed`
- full pytest coverage：PASS，`1127 passed`，coverage `91.77%`
- missing-config `--use-llm` smoke：PASS fail-closed
- real provider diagnostic：chapter 1 accepted；chapter 2 failed `llm_timeout`

## Gate B Summary

Gate B blocked。

Command：

```bash
uv run fund-analysis analyze 006597 --report-year 2024 --use-llm
```

Result：

- exit code `1`
- stdout empty
- no deterministic fallback
- CLI stderr only reports final assembly incomplete
- Service diagnostic classifies root blocker as `provider_runtime / timeout` with `stop_reason=llm_timeout`

Evidence：

- `docs/reviews/mvp-real-provider-smoke-acceptance-controller-judgment-20260531.md`
- `reports/mvp-local-acceptance/20260531-writer-auditor-contract-hardening/real-provider-006597-2024.stderr`
- `reports/mvp-local-acceptance/20260531-writer-auditor-contract-hardening/real-provider-006597-2024-diagnostic.json`

Gate B does not pass because it did not produce complete chapters 0-7 with audit status.

## Gate C Summary

Gate C design-only accepted。

Design defines:

- `extraction_score`
- `chapter_fact_score`
- `chapter_generation_score`
- runtime timeout `not_scored` / `blocked_provider_runtime` routing
- score schema
- failure taxonomy
- per-chapter report
- pro-codex task generation rules
- pass/fail thresholds
- rerun command
- artifact lifecycle
- human review/manual override entry points

Evidence：

- `docs/reviews/mvp-chapter-generation-score-loop-design-20260531.md`
- `docs/reviews/mvp-chapter-generation-score-loop-design-review-mimo-20260531.md`
- `docs/reviews/mvp-chapter-generation-score-loop-design-review-glm-20260531.md`
- `docs/reviews/mvp-chapter-generation-score-loop-design-controller-judgment-20260531.md`

Design residuals for a future implementation gate:

- clarify `ChapterFactInput` vs current `ChapterFactProjection`;
- define relationship to existing `extraction_score.py` / `extraction_score_service.py`;
- clarify weights/value/threshold calculation;
- enumerate `not_scored_reason`;
- align future `score-chapters` exit code with current CLI conventions;
- confirm L2 candidate facet failure source before implementation.

## Next Smallest Entry Point

Next gate should be:

`MVP real provider smoke acceptance rerun / provider runtime timeout hardening gate`

Minimal sequence:

1. Rerun `006597 / 2024 --use-llm` once to distinguish transient provider timeout from reproducible runtime blocker.
2. If timeout repeats, implement bounded provider runtime hardening only: timeout budget, bounded retry/backoff, or chapter 2 runtime-cost diagnostic.
3. Do not reopen provider auth/config unless evidence changes.
4. Do not enter score-loop implementation until Gate B can either pass or fail with a non-runtime generation/fact category.

## Prohibited Follow-up

- Do not mark PR ready, push, merge or release from this phase.
- Do not alter golden / fixtures / score / quality gate.
- Do not enter Gate 5 dayu/Host/Agent.
- Do not treat score-loop design as readiness pass.
- Do not loosen evidence, ITEM_RULE, candidate facet, trading advice or E2 deferred safety boundaries.

## Self-check

- Branch/status were checked before starting.
- Work stayed local; no external PR state changed.
- Specialist implementation/review/design work was delegated to agents.
- Controller wrote only judgment/control artifacts and ran validation.
- Artifacts do not contain API key, Authorization header value, full provider response or full writer draft.
