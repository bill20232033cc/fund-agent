# MVP Provider Runtime Budget and Prompt-Cost Root-Cause Calibration Plan Review — AgentDS

- Gate: plan review
- Role: AgentDS plan review agent, not controller, not implementation worker
- Date: 2026-05-31
- Artifact under review: `docs/reviews/mvp-provider-runtime-budget-prompt-cost-root-cause-calibration-plan-20260531.md`

## Review Scope

验证 plan handoff readiness：先诊断再压缩/budget 顺序、同源区分 ch2/6 large vs ch1/3/5 small、
不把推测当 root cause、禁止 prompt/draft/secret 序列化、不放松 evidence/ITEM_RULE/candidate
facet/audit safety、不进入 Gate5/dayu/Host/Agent、不改 golden/fixtures/score/quality gate、
保持 deterministic 默认和 fail-closed、`docs/design.md` 仅 post-acceptance 同步。

Read: AGENTS.md, current-startup-packet.md, implementation-control.md, matrix evidence, controller
judgment, service-diagnostic.json, chapter_writer.py L1318-L1343, llm_provider.py,
chapter_orchestrator.py, config/llm.py.

## Verdict: PASS with advisory findings

## Blocking Findings

None.

## Non-blocking Findings

### N1 — Auditor `timeout_root_cause_hint` 分类表述不够显式

Plan L177-181 定义了 `large_writer_prompt_cost` 要求 `operation=writer`，但 `small_prompt_provider_timeout`
不区分 operation。当前证据 auditor prompt ~1000 tokens 自然落入 small 区间，但建议在分类规则中显式
写清：auditor 只能产出 `small_prompt_provider_timeout` 或 `provider_runtime_timeout_uncalibrated`，
不会产出 `large_writer_prompt_cost`。便于未来维护者快速判断。

### N2 — Slice 2 `value_summary` 生成算法缺少精确定义

Plan L224-228 要求对 large value 生成 `value_summary`，"derived directly from the structured value
without external inference"，但未给出算法边界（嵌套结构处理、截断策略、数值提取规则）。模糊的 summary
生成可能引入不可预期的信息丢失。建议 implementation 阶段精确定义为：只提取顶层标量字段名+值、列表长
度、嵌套 dict key 名，不推断语义或做 NL 摘要。

### N3 — repair timeout 缺少推荐默认值

Plan L200-201 定义了 `FUND_AGENT_LLM_REPAIR_TIMEOUT_SECONDS` env var，但 L321-326 的初始推荐默认
值段落只覆盖 legacy timeout/max_attempts/backoff。用 writer timeout 作为 repair fallback 是保守策略，
但建议 implementation 中显式记录这一 fallback 决策。

## Required Fixes

无。所有 findings 为 advisory，不阻塞 plan handoff。

## Checklist

| 检查项 | 结果 |
|---|---|
| 先诊断（Slice 1）再压缩/budget（Slice 2/3） | PASS |
| 同源区分 ch2/6 large vs ch1/3/5 small（阈值 8000/3000） | PASS |
| 不把推测当 root cause（阈值基于实测 prompt tokens） | PASS |
| 禁止 full prompt / draft / provider response / secret 序列化 | PASS |
| 不放松 evidence / ITEM_RULE / candidate facet / audit safety | PASS |
| 不进入 Gate5 / dayu / Host / Agent | PASS |
| 不改 golden / fixtures / extraction score / quality gate | PASS |
| 保持 deterministic 默认行为和 fail-closed | PASS |
| `docs/design.md` 仅 post-acceptance 同步 | PASS |
| 分类逻辑覆盖全部 timeout 情况 | PASS |
| Slice 2 fail-closed test（无法安全 compact 时阻断） | PASS |
| Slice 5 secret leak scan | PASS |
