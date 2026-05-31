# MVP chapter generation score loop design controller judgment

日期：2026-05-31

Phase：`MVP real-provider stabilization and score-loop phase`

Gate：`MVP chapter generation score loop design gate`

角色：Phaseflow controller。本文记录 design-only gate 裁决，不实现代码，不 push、不创建或更新 PR、不 merge、不 release。

## Judgment

结论：`accepted_design_only`

Gate C 设计目标已达成。设计清晰区分 `extraction_score`、`chapter_fact_score`、`chapter_generation_score`，将 Gate B 的 `provider_runtime / timeout`、`stop_reason=llm_timeout` 单独路由为 `blocked_provider_runtime` / `not_scored`，不把 runtime timeout 伪装成 generation quality pass/fail。

## Evidence

- Design artifact：`docs/reviews/mvp-chapter-generation-score-loop-design-20260531.md`
- MiMo design review：`docs/reviews/mvp-chapter-generation-score-loop-design-review-mimo-20260531.md`
- GLM design review：`docs/reviews/mvp-chapter-generation-score-loop-design-review-glm-20260531.md`
- Gate B blocked input：`docs/reviews/mvp-real-provider-smoke-acceptance-controller-judgment-20260531.md`

两份 independent design review 均为 `PASS`。

## Accepted Scope

设计包含并通过 review：

- score schema；
- failure taxonomy；
- per-chapter score report；
- pro-codex task generation rules；
- pass/fail threshold；
- rerun command；
- artifact lifecycle；
- human review / manual override entry points；
- readiness/golden/quality gate boundary；
- provider timeout `not_scored` handling。

## Residual Findings

以下 findings 不阻断 design acceptance，必须作为后续 implementation gate Slice 1 前置澄清：

- `ChapterFactInput` 命名与当前代码事实 `ChapterFactProjection` 不一致：后续实现前统一为 `ChapterFactProjection`，或显式定义新的内部 input 类型。
- 新 score-loop `extraction_score` 与现有 `fund_agent/fund/extraction_score.py`、`fund_agent/services/extraction_score_service.py` 的关系必须说明：推荐放入独立 namespace，并声明并列独立、不替代、不接入现有 quality gate。
- Weights 与 threshold/value 计算语义需要精确化：明确 weights 是 reviewable penalty 计算，还是仅用于排序；blocking failure 始终覆盖分值。
- `not_scored_reason` 应定义枚举或映射表，覆盖 `provider_timeout`、`provider_rate_limited`、`provider_network_error`、`provider_malformed_response`、`provider_exception`。
- `score-chapters` exit code `3` 与当前 CLI exit code 体系需在实现 gate 校验，避免混淆现有 `analyze --use-llm` exit code。
- `generation.asserted_candidate_facet` 若映射到 L2，后续实现需确认 auditor L2 逻辑是否已有直接来源；不得因此放松 candidate facet safety boundary。

## Non-goal Confirmation

- 未实现代码。
- 未修改 golden / fixtures / score / quality gate / readiness。
- 未进入 Gate 5 dayu/Host/Agent。
- 未修改默认 deterministic `analyze/checklist` 行为。
- 未记录 API key、Authorization header、完整 provider response 或完整 writer draft。

## Next Entry Point

Phase 当前整体停在 local accepted / blocked-with-reason：

- Gate A：local accepted。
- Gate B：blocked by `provider_runtime / timeout`，stop reason `llm_timeout`。
- Gate C：design accepted。

下一最小 gate 应优先处理 Gate B timeout：`MVP real provider smoke acceptance rerun / provider runtime timeout hardening gate`。只有当 `006597 / 2024 --use-llm` 不再被 runtime timeout 阻断后，才应进入 score-loop implementation。
