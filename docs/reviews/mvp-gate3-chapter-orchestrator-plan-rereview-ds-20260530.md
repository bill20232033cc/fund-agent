# MVP Gate 3 chapter_orchestrator — Plan Re-Review (AgentDS)

日期：2026-05-30
审查角色：AgentDS，独立 plan re-reviewer
审查目标：`docs/reviews/mvp-gate3-chapter-orchestrator-plan-20260530.md`（修复后）
前次审查：`docs/reviews/mvp-gate3-chapter-orchestrator-plan-review-ds-20260530.md`（结论 BLOCKED，3 BLOCKING + 2 HIGH + 2 MEDIUM + 1 LOW + 1 INFO）
审查结论：**PASS**

---

## Finding Resolution Verification

### DS-1 (BLOCKING) — ChapterRunStopReason 未覆盖全部 writer 停止原因 → FIXED

- §7.1: `llm_empty_response`、`llm_contract_violation` 已加入 `ChapterRunStopReason` literal
- §8.1: 新增完整 1:1 mapping table，覆盖全部 10 个 `ChapterWriteStopReason` → 恰好一个 `ChapterRunStopReason`
- `evidence_anchor_missing` → `missing_required_facts`（事实不足，非 writer 可重试问题）
- `item_rule_deleted_required_content` → `missing_required_facts`（契约/输入事实不足）
- `prompt_only` → `writer_blocked`
- 未在表中的 stop reason → raise `ValueError`，fail-closed

### DS-2 (BLOCKING) — ChapterOrchestrator.orchestrate() 缺少 fact_provider → FIXED

- §7.6: `ChapterOrchestrator.__init__(self, fact_provider: ChapterFactProvider | None = None)` 显式接受并存储
- `orchestrate()` 委托 `orchestrate_chapters(..., fact_provider=self._fact_provider)`，不 hardcode
- 与 standalone 函数 `orchestrate_chapters()` 注入语义一致

### DS-3 (BLOCKING) — Auditor LLM unavailable 触发无意义 retry → FIXED

- §8 step 3: 全局 preflight — `run_llm_audit=True` 且 `auditor is None` → 直接 `blocked`，`generated_chapter_ids=()`，不调用 writer，不进入 repair loop
- §8.2 decision table row 2: `run_llm_audit and not auditor_available` → action `stop`
- §8.2 decision table row 3: `audit_result.llm.status=="blocked"` + `LLM_UNAVAILABLE` → `stop`
- §9.7: 三层防御 — 全局 preflight、decision table、per-issue check
- §12 Slice 2 tests: "auditor unavailable blocks before writer when `run_llm_audit=True`"
- §12 Slice 3 tests: "auditor LLM_UNAVAILABLE issue returns stop and does not retry writer"

### DS-4 (HIGH) — Stop reason 映射歧义（"或"）→ FIXED

- §8.1 table 完全消除歧义，每个 writer reason → 恰好一个 orchestrator reason
- `evidence_anchor_missing`、`item_rule_deleted_required_content` 统一为 `missing_required_facts`

### DS-5 (HIGH) — AcceptedChapterConclusion 无长度上限 → FIXED

- §7.5: 新增 `conclusion_truncated: bool`、`conclusion_source: Literal["heading", "fallback_lines"]`
- §10: `MAX_ACCEPTED_CONCLUSION_CHARS = 500` 硬上限
- §10: 支持 `### 结论要点` 和 `## 结论要点`
- §10: fallback 取前 3 非空行，不是整篇 draft
- §12 Slice 4 tests: "long conclusion is capped at 500 chars and sets `conclusion_truncated=True`"

### DS-6 (MEDIUM) — _decide_repair() 未定义 → FIXED

- §8.2: 完整函数签名、参数语义、8 行决策表
- 覆盖 `accepted=True`（不应被调用）、auditor unavailable、LLM_UNAVAILABLE、needs_more_facts、repair_hint=none、budget exhausted、blocked+regenerate、fail+regenerate
- `issue_ids` 收集行为明确

### DS-7 (MEDIUM) — Service __init__.py 导出不明确 → FIXED

- §12 Slice 4: 精确 7 项导出列表，仅包含主入口和顶层 request/result/policy/client bundle

### DS-8 (LOW) — 同 prompt regeneration 修复率 → ACCEPTED RESIDUAL

- §16 residual risk 更新，明确 best-effort、test budget exhaustion
- §8 step 6 明确 patch→regenerate "可能重复生成同类失败，必须受 retry budget 限制"

### DS-9 (INFO) — 第 5 章 accept 概率 → ACCEPTED

- §16 新增 residual: "`partial` result consumption is unresolved"，Gate 4 负责裁决

---

## Cross-Review: MiMo Findings Verification

| MiMo Finding | Disposition | Verified |
|---|---|---|
| MiMo-1 patch→regenerate 修复率 | Accepted residual | §16 updated, §12 tests cover budget exhaustion |
| MiMo-2 auditor LLM unavailable | Fixed (same as DS-3) | §8 step 3 + §8.2 + §9.7 triple defense |
| MiMo-3 façade 注入不一致 | Fixed (same as DS-2) | §7.6 `__init__` + delegate |
| MiMo-4 partial status Gate 4 消费 | Accepted residual | §7.1 + §17 Gate 4 must decide |
| MiMo-5 max_repair_attempts=0 | Fixed | §7.3 说明 + §8.2 decision table + §12 test |

---

## Additional Verification

- **Service/Fund 边界**: orchestrator 在 Service，writer/auditor/contracts 在 Fund ✓
- **No extra_payload**: 所有参数在 typed dataclass 中显式声明 ✓
- **No chapter 0/7 generation**: policy validation 拒收 0/7，§9.1–§9.3 明确 ✓
- **No scope creep**: non-goals 覆盖 final assembler、CLI、dayu、source、promotion、golden ✓
- **Repair budget**: `max_repair_attempts >= 0`，0 表示不重试，§8.2 完整决策 ✓
- **Fail-closed**: 全局 preflight、decision table、unknown stop reason → ValueError ✓
- **Fake LLM tests-only**: §11 明确 fake class 只能在 test file 内 ✓
- **Test coverage**: 4 slices × ~7 tests each，覆盖 validation、mapping、repair、conclusion、budget、fail_fast ✓
- **Validation commands**: ruff、pytest targeted + adjacent + coverage gate ✓
- **Docs discipline**: implementation worker 不更新 control/design docs ✓

---

## Residual Risks (Post-Fix)

| Risk | Status |
|------|--------|
| patch→regenerate 同 prompt 可能重复失败 | Accepted；budget 限制；tests 覆盖 exhaustion |
| partial result 消费未裁决 | Accepted；Gate 4 plan 必须显式处理 |
| 第 5 章单期下 accept 率不确定 | Accepted；cross-period data gate 前置条件 |
| LLM exception 粗粒度 | Accepted；MVP fail-closed 足够 |
| No typed patch API | Accepted；future gate |

---

## Verdict: PASS

前次审查的 3 BLOCKING、2 HIGH、2 MEDIUM finding 均已修复。1 LOW 转为 accepted residual，1 INFO 已改善文档。MiMo 交叉审查 findings 亦已处置。

Plan 现在是 code-generation-ready：所有 public contract 完整、stop reason mapping 无歧义、repair decision table 覆盖全部状态组合、auditor unavailable 有 early stop 防御、conclusion extraction 有硬上限、Service exports 明确、`_decide_repair()` 签名与决策表完整。

可交给 implementation agent。
