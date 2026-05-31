# MVP LLM writer/auditor contract hardening plan controller judgment

日期：2026-05-31

Phase：`MVP real-provider stabilization and score-loop phase`

Gate：`MVP LLM writer/auditor contract hardening gate`

角色：Phaseflow controller。本文只记录 plan/review 裁决，不进入 implementation，不 push、不创建或更新 PR、不 merge、不 release。

## Judgment

结论：`accepted_for_implementation`

依据：

- Approved plan：`docs/reviews/mvp-llm-writer-auditor-contract-hardening-plan-20260531.md`
- MiMo plan review：`docs/reviews/mvp-llm-writer-auditor-contract-hardening-plan-review-mimo-20260531.md`
- GLM plan review：`docs/reviews/mvp-llm-writer-auditor-contract-hardening-plan-review-glm-20260531.md`
- MiMo re-review：`docs/reviews/mvp-llm-writer-auditor-contract-hardening-plan-rereview-mimo-20260531.md`
- GLM re-review：`docs/reviews/mvp-llm-writer-auditor-contract-hardening-plan-rereview-glm-20260531.md`

两份 re-review 均为 `PASS`，确认 controller-accepted findings 已在 plan 中修复。Gate A 可以进入 implementation handoff。

## Accepted Findings

- MiMo F-001：accepted。Auditor required output 检查必须按 `<!-- required_output:<item> -->` exact marker，不得以裸 item text 通过。
- MiMo F-002：accepted。Auditor 测试 helper 必须同步 required output marker 协议。
- MiMo F-003 / GLM N-4：accepted。`non_asserted_facets` 去重策略固定为每个 unique facet text 的 first blocking occurrence；任一 asserted occurrence 仍 blocking。
- MiMo F-004：accepted。真实 provider smoke 命令必须显式标注并记录为 `real-provider-smoke-006597-2024`。
- MiMo F-005 / GLM N-3：accepted。新增 writer stop reason 必须在 Service 层保留精确分类，不折叠到泛化 `llm_contract_violation`。
- GLM N-1：accepted。统一 `INCOMPLETE_FINISH_REASONS` / `response_incomplete` 命名，避免把 `content_filter` 误称 truncation。
- GLM N-2：accepted。`required_corrections` 必须由确定性映射生成，未知项只允许脱敏、限长 fallback。

## Implementation Boundary

允许 implementation worker 只按 approved plan 的 Slice A-D 修改：

- `fund_agent/fund/chapter_writer.py`
- `fund_agent/fund/chapter_auditor.py`
- `fund_agent/services/chapter_orchestrator.py`
- `fund_agent/services/llm_provider.py`
- 对应测试文件
- `fund_agent/fund/README.md` / `tests/README.md` 仅在当前契约或测试说明确需同步时修改

禁止：

- 修改 golden / fixtures / score / quality gate / snapshot / promotion state。
- 进入 Gate 5 dayu/Host/Agent。
- 修改 PR 状态、push、merge、release。
- 记录 API key、Authorization header、完整 provider response 或完整 writer draft。
- 把缺证据、弱证据、candidate facet asserted fact 包装为通过。
- 改变默认 deterministic analyze/checklist 行为。

## Next Step

派发 AgentCodex 执行 Gate A implementation。完成后必须产出 implementation evidence artifact，并进入 MiMo/GLM 独立 code review。
