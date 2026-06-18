# Provider/LLM Chapter 3 Missing-required-marker Live-blocker Disposition — DS Review

Date: 2026-06-14

Role: DS independent reviewer, not controller

Review target: `docs/reviews/provider-llm-chapter3-missing-required-marker-live-blocker-disposition-20260614.md`

Verdict: **PASS**

## Scope

- Review mode: role-scoped disposition review handoff
- Branch: `feat/mvp-llm-incomplete-run-artifacts`
- Output file: `docs/reviews/provider-llm-chapter3-missing-required-marker-live-blocker-disposition-review-ds-20260614.md`
- Included: disposition artifact fact/inference separation, root-cause classification support, overclaiming check, next gate recommendation soundness
- Excluded: source/test/runtime/control/design/README changes; live/provider/LLM/network/PDF/FDR/source/analyze/checklist/readiness/release/PR commands; raw prompt/draft/body inspection

## Findings

### F1 — 未修复 — 低 — 未记录 Chapter 3 summary/chapter 层 attempt_count 不一致

- **入口/函数**: 处置文档 §3 引用 `summary.json.first_failed.attempt_count=1`，但未提及 `chapter-03.json` 顶层缺少独立 `attempt_count` 字段
- **文件(行号)**: `docs/reviews/provider-llm-chapter3-missing-required-marker-live-blocker-disposition-20260614.md` §3 第 63 行
- **输入场景**: 裁决者对比 `summary.json` 与 `chapter-03.json` 做一致性检查时
- **实际分支**: 处置文档只引用了 `summary.json.first_failed.attempt_count=1`，未说明 `chapter-03.json` 顶层无此字段（仅 `attempts[0].attempt_index=0`）
- **预期行为**: 处置文档应在 Accepted Live Facts 或 Diagnostics Residual 中记录此不一致，供后续诊断 gate 参考
- **实际行为**: 此不一致未被记录；DS Chapter 5 review 曾将其标注为 non-blocking diagnostic residual，但本处置未继承
- **直接证据**: `summary.json:145` 显示 `"attempt_count": 1`；`chapter-03.json` 顶层无 `attempt_count` 字段，仅 `attempts[0].attempt_index=0`（第 7 行）
- **影响**: 不影响根因分类；后续诊断 gate 可能忽略此元数据不一致而错误推断修复触发次数
- **建议改法和验证点**: 在 §8 Residuals 中新增一行记录此 summary/chapter 元数据不一致，引用 DS Chapter 5 review 的 non-blocking 裁决。无需修改根因分类或 next gate 推荐
- **修复风险**: 低
- **严重程度**: 低

### F2 — 未修复 — 低 — `provider_attempt_count=0` 与 `writer_response_chars=1906` 之间的诊断分层张力可更明确

- **入口/函数**: 处置文档 §3、§5、§8
- **文件(行号)**: 处置文档第 66-67 行（Accepted Live Facts）、第 93 行（Rejected Overreads）、第 133 行（Residuals）
- **输入场景**: 未来 gate 的裁决者在不理解 prompt-contract 与 provider-runtime 诊断分层的情况下阅读此处置
- **实际分支**: 处置文档同时记录 `provider_attempt_count=0`（runtime diagnostics）和 `writer_response_chars=1906`（prompt diagnostics），并在 §5 正确拒绝推断 provider quality，在 §8 记录 "runtime scalar fields are sparse/null while prompt diagnostics are populated" 为 residual
- **预期行为**: 应更明确说明 `provider_attempt_count=0` 的语义是该失败在 prompt-contract 层被吸收（writer parse 阶段检出 marker 缺失），与 provider 是否实际被调用是两个独立的诊断层
- **实际行为**: §5 只写了"provider attempt count 0 and no provider runtime categories"，§8 只写了 sparse/null vs populated。两处各自正确但未跨层解释此张力的诊断含义，可能导致读者误以为 LLM 未被调用
- **直接证据**: `summary.json:468` 第一失败项 `provider_attempt_count=0`（runtime 层）；`chapter-03.json:82` `writer_response_chars=1906`（prompt-contract 层）；代码中 `_required_output_degrade_issues`（`chapter_writer.py:1787-1834`）在 writer parse 阶段执行，不涉及 provider runtime 诊断
- **影响**: 低——不影响当前处置的根因分类和 next gate 推荐；仅影响未来 gate 裁决者的初始理解效率
- **建议改法和验证点**: 在 §8 Residuals 第 133 行将 "Chapter 3 runtime scalar fields are sparse/null while prompt diagnostics are populated" 扩展为明确说明这是 prompt-contract 层在 provider runtime 诊断层之上独立检出失败的预期行为，不是 provider 层 bug
- **修复风险**: 低
- **严重程度**: 低

## Fact/Inference Separation 验证

逐节检查处置文档的事实层分离：

| 声明层 | 处置位置 | DS 核实 |
|---|---|---|
| Repo fact: writer prompt 要求 exact marker（含 typed `<!-- required_output:<id> -->`） | §3 第 45-46 行 | `chapter_writer.py:693-697` 确认协议文本包含 exact marker 和 typed marker 指令 |
| Repo fact: typed required-output prompt payload 渲染 marker/id/text/availability/action/instruction | §3 第 46 行 | `_prompt_required_output_plan_item`（`chapter_writer.py:1595-1601`）确认输出字段 |
| Repo fact: parser 检查 marker 存在并发出 `missing_required_output_marker` | §3 第 47 行 | `_required_output_marker_issues`（`chapter_writer.py:1759-1784`）确认检查逻辑 |
| Repo fact: `render_evidence_gap` 项需 marker + approved gap phrasing，否则发出 `writer:required_output_gap_missing` | §3 第 48 行 | `_required_output_degrade_issues`（`chapter_writer.py:1787-1834`）和 `_GAP_OUTPUT_PHRASES`（`chapter_writer.py:114-123`）确认降级检查 |
| Repo fact: Agent runner 从 typed contract 提供 typed required-output items | §3 第 49 行 | `_typed_required_output_items`（`runner.py:1172-1193`）确认 |
| Truth-doc fact: canonical JSON 是 authored truth source；typed path 传递 typed required-output items + EvidenceAvailability | §3 第 54-57 行 | `docs/design.md:156-182` 确认 typed template truth-source replacement 和 EvidenceAvailability 是当前已实现事实 |
| Accepted live fact: `summary.json` first_failed 字段 | §3 第 63 行 | `summary.json:144-151` 逐字段匹配 |
| Accepted live fact: Chapter 3 prompt diagnostics 字段 | §3 第 64 行 | `summary.json:203-229` 逐字段匹配 |
| Accepted live fact: issue ids | §3 第 65 行 | `chapter-03.json:61-79` 确认两个 `writer:required_output_gap_missing` issue |
| Accepted live fact: Chapter 3 `accepted=false` 等状态 | §3 第 66 行 | `chapter-03.json:2-5` 确认 |
| Accepted live fact: runtime diagnostics 第一失败项 | §3 第 67 行 | `summary.json:460-489` 确认 operation=writer, provider_attempt_count=0, provider_runtime_categories=[] |
| Inference: root cause 是 writer output 不满足已有 typed required-output gap marker/phrasing contract | §4 第 85 行 | 正确标注为 inference；基于 repo fact（已有 prompt contract 和 parser）与 live fact（两个 gap_missing issue）的合理推断 |
| Residual: 未读 raw prompt/draft body，无法证明 prompt ergonomics、repair context 或 item 05 policy | §4 第 86 行 | 正确标注为 residual；诚实记录证据边界 |

**结论**：处置文档正确分离了 repo fact、truth-doc fact、accepted live fact、inference 和 residual。没有将 inference 伪装为 fact，也没有将 residual 当作已证明结论。

## Root-cause Classification 验证

处置文档将当前最强根因分类为 `LLM_WRITER_OUTPUT_NONCOMPLIANCE_WITH_EXISTING_TYPED_REQUIRED_OUTPUT_GAP_MARKER_CONTRACT`。

证据链逐段验证：

1. **触发条件**：live 运行中 Chapter 3 在 `writer_parse` 阶段以 `missing_required_output_marker` 失败（`summary.json:55`, `chapter-03.json:158`）
2. **具体失败项**：两个 `writer:required_output_gap_missing` issue，对应 typed item ids `ch3.required_output.item_01` 和 `ch3.required_output.item_05`（`chapter-03.json:61-79`）
3. **代码中的分类路径**：`_required_output_degrade_issues`（`chapter_writer.py:1805-1818`）在 `render_evidence_gap` 项缺少 marker + approved gap phrasing 时发出此 issue，归类为 `missing_required_output_marker`
4. **排除的替代解释**：
   - 非 provider 故障：`provider_attempt_count=0` 在 runtime 诊断层（`summary.json:468`）
   - 非 runtime truncation：`response_chars=1906` < `max_output_chars=12000`（`chapter-03.json:82`）
   - 非 source/EID 问题：parser 检查的是输出格式，不涉及 source 可用性
   - 非 final assembly bug：Chapter 3 在 writer parse 阶段已 blocked（`chapter-03.json:157`）

根因分类有 safe metadata 和 no-live code 证据支撑。分类的精确度受限于未读 raw prompt/draft body，处置文档已在 §4 Residual 中诚实记录此限制。

## Overclaiming 验证

处置文档 §5（Rejected Overreads）逐项检查：

| 拒绝的过度推断 | 处置行号 | DS 核实 |
|---|---|---|
| 不将 live runtime artifact 视为 EID/source proof | §5 第 93 行 | 正确：manifest source fields 为 null |
| 不推断 provider quality/availability | §5 第 94 行 | 正确：provider_attempt_count=0, 无 provider runtime categories |
| 不声称 full LLM path readiness | §5 第 95 行 | 正确：final_assembly 为 incomplete, Chapter 3 blocked |
| 不声称 Chapter 3 content quality | §5 第 96 行 | 正确：未读 chapter draft body |
| 不推断 raw prompt adequacy | §5 第 97 行 | 正确：未读 raw prompt |
| 不将 Chapter 5 pass 视为 general Route C pass | §5 第 98 行 | 正确：Chapter 5 是单章 pass，非全路径 proof |
| 不更改 repair budget/provider defaults/等 | §5 第 99 行 | 正确：处置 gate 无权更改这些 |

**结论**：处置文档未过度声称。所有拒绝的过度推断都有对应的证据限制支撑。

## Next Gate Recommendation 验证

处置推荐 `Provider/LLM Chapter 3 Missing-required-marker No-live Diagnostic Evidence Gate`。

推荐逻辑检查：
- 当前根因分类足够特定以排除 source/provider/final-assembly overread，但不够特定以支持 fix planning → **合理**：未读 raw prompt/draft body，无法判断应修改 prompt wording、repair context、retry trigger 还是 item policy
- 推荐的四个诊断问题直接对应当前证据缺口 → **合理**：问题 1 检查 prompt 是否包含正确 marker 条目，问题 2 验证 fake 响应可复现 bug，问题 3 检查修复路径能否收到足够上下文，问题 4 澄清 item 05 策略状态
- 推荐 no-live 而非 live 诊断 → **合理**：不需要 provider/network 即可检查 prompt payload 和 fake writer 响应；符合当前 `NOT_READY` 约束和 no-live 边界

不推荐直接进入 fix planning（跳过诊断）或不推荐更多 live evidence（live 不能回答 prompt payload 问题）的决策是正确的。

## Open Questions

- item 05（`ch3.required_output.item_05`）的 `when_evidence_missing` 当前配置是什么？处置文档 §8 将其列为 residual "Item 05 policy status is not classified here"，但 §4 根因分类已假设两个 item 都是 `render_evidence_gap`（因为 issue id 前缀是 `writer:required_output_gap_missing`）。如果 item 05 的 typed 策略与 item 01 不同，根因分类可能需要区分处理。建议 next gate 的诊断问题 4 优先回答此问题。
- `chapter-03.json` 中 `attempts[0].repair_decision=null` 且 `terminal_repair_attempt_index=null`。在 prompt-contract 层失败后，修复路径是否被正确触发（还是被 prompt-contract 层吸收而从未到达 repair 决策）？此问题应在 no-live diagnostic gate 中通过检查 repair 入口代码路径回答。

## Residual Risk

- 处置文档诚实记录了未读 raw prompt 和 draft body 的限制，next gate 的 no-live 诊断应填补此缺口
- 两个 finding（F1/F2）均为低严重度，不改变 PASS 结论
- 如果 no-live diagnostic gate 发现 prompt payload 中已包含正确的 marker 条目且 fake 响应无法复现 bug，根因可能需要重新分类为 provider 层或 live-specific 问题——此风险已在处置文档 §4 Residual 中间接覆盖
- DS Chapter 5 review 中记录的 runtime metadata inconsistency（attempt_count summary/chapter 不匹配）未被本处置继承，可能在未来 gate 中丢失上下文
