# Re-Review: MVP Gate 3 chapter_orchestrator plan

日期：2026-05-30
角色：AgentMiMo re-reviewer
审查目标：`docs/reviews/mvp-gate3-chapter-orchestrator-plan-20260530.md`（fix pass 后）
前序 reviews：
- `docs/reviews/mvp-gate3-chapter-orchestrator-plan-review-ds-20260530.md`（BLOCKED，3 BLOCKING + 2 HIGH + 2 MEDIUM）
- `docs/reviews/mvp-gate3-chapter-orchestrator-plan-review-mimo-20260530.md`（PASS_WITH_NON_BLOCKING，2 MEDIUM + 2 LOW + 1 INFO）

## Finding Disposition Verification

### DS BLOCKING findings

| ID | Finding | Disposition | Evidence in updated plan |
|---|---|---|---|
| DS-1/DS-4 | `ChapterRunStopReason` 缺 `llm_empty_response` / `llm_contract_violation`；mapping 含"或"歧义 | **RESOLVED** | §7.1 增加 `llm_empty_response` 和 `llm_contract_violation`；§8.1 新增完整一对一 mapping table，覆盖每个 `ChapterWriteStopReason` 到唯一 `ChapterRunStopReason`，无"或"、无 fallback；末尾声明遇到不在表中的 stop reason 应 raise `ValueError` |
| DS-2 | `ChapterOrchestrator.orchestrate()` 缺 `fact_provider` 参数 | **RESOLVED** | §7.6 固定 `ChapterOrchestrator.__init__(self, fact_provider=None)` 存储 provider；§7.6 约束 `orchestrate()` 必须委托 `orchestrate_chapters(..., fact_provider=self._fact_provider)`，不得 hardcode 不可注入 provider |
| DS-3 | auditor LLM unavailable 触发无意义 regenerate 重试 | **RESOLVED** | §8 step 3 新增全局 preflight：`run_llm_audit=True` 且 auditor client 缺失时直接 blocked `llm_unavailable`，`generated_chapter_ids=()`，不得调用 writer；§8.2 decision table 第 2 行：`run_llm_audit and not auditor_available` → `stop`；§9.7 明确"不得调用 writer，不得进入 audit，不得消耗 repair budget" |

### DS HIGH findings

| ID | Finding | Disposition | Evidence in updated plan |
|---|---|---|---|
| DS-5 | `AcceptedChapterConclusion` 无长度上限，fallback 可能取全文 ~12000 chars | **RESOLVED** | §7.5 增加 `conclusion_truncated: bool` 和 `conclusion_source`；§10 增加 `MAX_ACCEPTED_CONCLUSION_CHARS = 500` 硬上限；fallback 改为前 3 个非空行（非整段），再应用 500 字符 cap |
| DS-6 | `_decide_repair()` 无签名、无决策表 | **RESOLVED** | §8.2 新增完整函数签名 `(audit_result, *, remaining_budget, auditor_available, run_llm_audit) -> ChapterRepairDecision`；新增完整 decision table 覆盖 8 条条件路径，含 auditor unavailable、LLM blocked、budget exhausted、`max_repair_attempts=0` |

### DS MEDIUM findings

| ID | Finding | Disposition | Evidence in updated plan |
|---|---|---|---|
| DS-7 | `Service/__init__.py` 导出清单未指定 | **RESOLVED** | §12 Slice 4 明确 exact exports：`ChapterOrchestrator`, `ChapterOrchestrationInput`, `ChapterOrchestrationResult`, `ChapterOrchestrationPolicy`, `ChapterOrchestratorLLMClients`, `build_chapter_orchestration_input`, `orchestrate_chapters` |

### DS LOW/INFO findings

| ID | Finding | Disposition | Evidence in updated plan |
|---|---|---|---|
| DS-8 | repair loop 复用同一 `ChapterWriterInput`，regenerate 可能输出相同失败 | **Accepted residual** | §6 明确"best-effort regenerate attempt"；§8 step 6 明确"该映射可能重复生成同类失败，必须受 retry budget 限制"；§16 residual table 记录此风险并要求 tests 覆盖 budget exhaustion |
| DS-9 | 第 5 章在单期 bundle 下 acceptance 概率未评估 | **Accepted residual** | §9.4 已描述第 5 章跨期缺失的 fail-closed 行为；§16 residual table 记录此风险 |

### MiMo findings

| ID | Finding | Disposition | Evidence in updated plan |
|---|---|---|---|
| MiMo-1 | patch -> regenerate 同 prompt 修复率低 | **Accepted residual** | §6 / §16 明确 best-effort residual；§8 step 6 明确 budget 限制；implementation tests 必须覆盖 budget exhaustion |
| MiMo-2 | auditor None 浪费 writer retry（同 DS-3） | **RESOLVED** | 见 DS-3 验证 |
| MiMo-3 | `ChapterOrchestrator` façade 注入不一致（同 DS-2） | **RESOLVED** | 见 DS-2 验证 |
| MiMo-4 | `partial` 状态 Gate 4 消费契约未裁决 | **Accepted residual for Gate 4** | §7.1 明确"Gate 4 必须单独裁决 partial 输入是拒绝、降级还是生成不完整草稿"；§17 next gates 增加"必须显式裁决 `status=='partial'` 时的 assembly 行为" |
| MiMo-5 | `max_repair_attempts=0` 行为未显式说明 | **RESOLVED** | §7.3 增加"`max_repair_attempts=0` 表示 attempt 0 初始写作后若 audit 未 accepted，直接 stop，不进入 repair retry"；§8 step 6 和 §8.2 decision table 均覆盖此路径 |

## Residual Risks

| Risk | Disposition | Owner |
|---|---|---|
| patch -> regenerate 同 prompt 可能重复失败 | Accepted; budget-bounded, tests must cover | Future repair contract gate |
| `partial` result 消费契约未裁决 | Gate 3 不把 partial 当 complete; Gate 4 必须裁决 | Gate 4 plan |
| E2 source verification deferred | Already accepted Gate 2 residual | Future Evidence Confirm gate |
| Chapter 5 cross-period evidence missing | No source probing in Gate 3 | Future cross-period data gate |

## Conclusion

**PASS**

All 3 DS BLOCKING findings are resolved with direct evidence in the updated plan. All 2 DS HIGH findings are resolved. Both DS MEDIUM findings are resolved. All MiMo findings are either resolved or explicitly documented as accepted residuals with tracking owners. The plan is code-generation-ready for implementation.
