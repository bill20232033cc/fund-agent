# MVP writer prompt contract diagnostic narrowing plan review (GLM)

日期：2026-05-31

审阅者角色：Gateflow plan reviewer（GLM），不是 implementation worker。

审阅对象：`docs/reviews/mvp-writer-prompt-contract-diagnostic-narrowing-plan-20260531.md`

## 结论

**PASS**

Plan 满足当前 gate 目标，安全边界完整，taxonomy 覆盖充分，code touch 最小。以下为逐项分析和非阻塞观察。

## 1. Gate 目标满足度

**满足。**

Plan 目标明确：把 `prompt_contract` / `llm_contract_violation` 收窄到唯一可修复子类。两个可接受结果定义清晰：

1. 完整 0-7 章报告 exit `0`。
2. fail-closed + 唯一 primary subcategory + chapter/phase/attribution + 最小修复入口。

这与 prompt-contract calibration controller judgment 指定的下一入口完全对齐。Controller judgment 明确要求："只做 secret-safe writer contract failure diagnostics：不保存完整 prompt、完整 draft 或 provider response，只记录失败子类和最小 prompt/parser 修正入口。" Plan 完整遵守了这一约束。

## 2. 敏感数据保护

**满足。**

Plan 显式禁止保存：

- `ChapterWriterPrompt.system_prompt` / `user_prompt`
- `ChapterDraft.markdown`
- `ChapterAuditLLMRequest.draft_markdown`
- Raw provider response / audit response
- API key / Authorization header / env dump
- String snippets from provider output

Diagnostic JSON 只包含整数计数器、枚举标量和章节身份。`issue_id_prefix_counts` 约束明确：不得包含 raw anchor id、missing reason value、facet text、forbidden phrase text、required output item text 或 message snippets。

### 观察 O1（非阻塞）

`issue_id_prefix_counts` 的前缀提取逻辑需要对所有 writer issue id 格式统一处理。当前 writer issue id 格式为 `writer:<type>:<suffix>`，其中 suffix 可能是 index、anchor_id 或 position。实现时需确保 suffix 被统一剥离。Plan 已在约束中覆盖此点（第 281 行），implementation worker 只需严格按约束实现。

## 3. Taxonomy 完备性

**满足。**

逐条对照 `chapter_writer.py` 当前所有 issue id 和 reason：

| Writer issue id / reason | Plan subcategory | 映射正确 |
|---|---|---|
| `missing_required_structure` (reason) | `missing_structure` | ✓ |
| `missing_required_output_marker` (reason) | `missing_required_marker` | ✓ |
| `unknown_anchor` (reason, issue `writer:unknown_anchor:*`) | `unknown_anchor` | ✓ |
| `writer:invalid_anchor_marker:*` | `invalid_marker` | ✓ |
| `writer:invalid_missing_marker:*` | `invalid_marker` | ✓ |
| `writer:unknown_missing_reason:*` | `invalid_marker` | ✓ |
| `writer:evidence_line_without_anchor_marker` | `invalid_marker` | ✓ |
| `writer:forbidden_phrase:*` | `forbidden_phrase` | ✓ |
| `response_too_long` (reason) | `response_length_incomplete` | ✓ |
| `response_incomplete` (reason) | `response_length_incomplete` | ✓ |
| Generic `writer:llm_contract_violation`（draft=None，无具体 issue） | `code_bug_other` | ✓ |

Audit 侧覆盖：

| Audit 来源 | Plan subcategory | 映射正确 |
|---|---|---|
| Programmatic audit candidate facet boundary | `candidate_facet_assertion` | ✓ |
| Audit forbidden content counter | `forbidden_phrase` | ✓ |

Primary selection order 安全优先且确定性：

1. `response_length_incomplete` — 对应 `_draft_from_llm_response` 中最早返回的 length/incomplete 检查
2. `invalid_marker` — parser 格式不可能
3. `unknown_anchor` — anchor 集合不匹配
4. `missing_required_marker` — required output 缺失
5. `missing_structure` — 固定段落缺失
6. `candidate_facet_assertion` — audit 阶段
7. `forbidden_phrase` — 可能在 writer 或 audit 阶段
8. `code_bug_other` — catch-all

该优先级与 `_draft_from_llm_response` 的执行顺序一致：先检查 length/incomplete，再检查 marker/structure/anchor。顺序合理。

### 观察 O2（非阻塞）

`candidate_facet_assertion_count` 的推导依赖 audit issue 的 message/code 来识别"non-asserted facet boundary"。当前 programmatic audit issue 的 rule_code 体系（P1/P2/E1/E2/E3/C1/L1/L2/R1/R2）中，没有专门的 facet 断言 rule code。Implementation worker 需要决定是通过现有 issue message 语义匹配还是新增一个窄 helper 来计数。Plan 的约束"do not store facet text"足以保证安全，但实现选择应在 evidence artifact 中注明。

## 4. 安全边界

**无漏洞。**

逐条检查：

- **证据锚点**：Plan 明确声明"Unknown anchors, invalid markers and evidence lines without anchor marker must continue blocking。" ✓
- **ITEM_RULE**："ITEM_RULE deletion remains fail-closed." ✓
- **Candidate facet**："Diagnostic counters may count candidate facet assertion but must not accept it." ✓
- **交易建议**："Trading advice and forecast phrases remain blocked." ✓
- **E2 deferred**："This gate must not pretend to implement Evidence Confirm or weaken E1/E3/L1/C1/C2." ✓
- **Missing semantics**："Missing data must remain explicit and cannot be rewritten as determinate fact." ✓
- **No deterministic fallback**："Provider runtime failures remain fail-closed; no deterministic fallback, no partial report." ✓
- **Disallowed shortcuts**：六条显式禁止全部正确。特别是"不把 `llm_contract_violation` 转为 accepted draft"和"不拓宽 allowed anchors 或 allowed missing reasons"，这两条直接防止了为通过 smoke 而放松安全合约的风险。

## 5. Code Touch 最小性

**满足。**

允许文件列表：

- `fund_agent/fund/chapter_writer.py` — 只做 subcategory derivation，不改 parser acceptance behavior
- `fund_agent/services/chapter_orchestrator.py` — 添加 typed diagnostic summary
- `fund_agent/ui/cli.py` — 添加 `first_failed_subcategory` scalar
- 测试文件
- Evidence artifacts

显式排除：模板、golden、score、quality gate、Host/Agent/dayu、provider auth/config、确定性默认链路、PR 外部状态。

### 观察 O3（非阻塞）

`ChapterRunResult` 将新增 `primary_subcategory` 字段。这是一个纯加法的 data contract 变更，不影响现有字段语义，属于最小改动。但 implementation worker 应确保该字段为 `Optional`/默认 `None`，不影响已有序列化和测试。

## 6. Tests / Validation

**满足。**

测试覆盖三个维度：

1. **Writer subcategory 映射**（`test_chapter_writer.py`）：覆盖所有 8 个子类的 issue id → subcategory 映射。
2. **Orchestrator 集成**（`test_chapter_orchestrator.py`）：覆盖 writer blocked、audit blocked、provider timeout、unmapped issue、sanitized serialization。特别关注"provider timeout 不产生 prompt-contract subcategory"和"unmapped issue 不静默通过"。
3. **CLI 输出**（`test_cli.py`）：覆盖 stderr 包含 subcategory、不包含敏感信息、默认 deterministic 行为不变。

Validation matrix 包含 ruff、targeted pytest、full coverage、deterministic analyze/checklist、missing-config smoke、real provider smoke 和 secret scan。覆盖完整。

### 观察 O4（非阻塞）

Secret scan 的范围应包含新产生的 `reports/mvp-local-acceptance/20260531-writer-prompt-contract-diagnostic-narrowing/` 下所有文件。Plan 已明确要求 `secret-scan.txt` 只包含 PASS/filtered hit summary，不包含 secrets。Implementation worker 应确保 scan 也覆盖 `docs/reviews/` 下新增的 evidence JSON。

## Summary of Observations

| ID | 类型 | 描述 | 行动 |
|---|---|---|---|
| O1 | 非阻塞 | `issue_id_prefix_counts` 前缀提取需统一处理所有 writer issue id 格式 | Implementation worker 在 evidence artifact 中记录提取逻辑 |
| O2 | 非阻塞 | `candidate_facet_assertion_count` 的推导方式需在实现时确定（message 语义匹配 vs 窄 helper） | Implementation worker 在 evidence artifact 中记录选择 |
| O3 | 非阻塞 | `ChapterRunResult.primary_subcategory` 应为 Optional/默认 None | Implementation worker 确保向后兼容 |
| O4 | 非阻塞 | Secret scan 范围应覆盖所有新增 evidence 文件 | Implementation worker 在 validation matrix 中记录 |

## Blocking Findings

无。

## Verdict

**PASS** — Plan 可进入 implementation 阶段。非阻塞观察不需阻塞 plan accept，implementation worker 应在 evidence artifact 中逐一处理。
