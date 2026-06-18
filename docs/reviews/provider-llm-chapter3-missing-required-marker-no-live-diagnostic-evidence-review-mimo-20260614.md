# Code Review

## Scope

- Mode: role-scoped review handoff (no-live diagnostic evidence artifact review)
- Review target: `docs/reviews/provider-llm-chapter3-missing-required-marker-no-live-diagnostic-evidence-20260614.md`
- Base: N/A (artifact review, not diff review)
- Output file: `docs/reviews/provider-llm-chapter3-missing-required-marker-no-live-diagnostic-evidence-review-mimo-20260614.md`
- Included scope: diagnostic matrix, root-cause refinement, no-live boundaries, item 05 evidence sufficiency, repair-route conclusion, next-gate recommendation
- Excluded scope: source/test/runtime/control/design/README changes; live/provider/LLM/network/PDF/FDR/source/analyze/checklist/readiness/release/PR commands
- Parallel review coverage: 无

## Findings

### 01-未修复-低-D2 证据分层：item_05 阻断行为和组合复现依赖 code-path 推理而非独立测试

- **入口/函数**: `_required_output_degrade_issues()` (`fund_agent/fund/chapter_writer.py:1787`)
- **文件(行号)**: artifact §3 D2 第 2-3 条; `chapter_writer.py:1804-1819`
- **输入场景**: Chapter 3 prompt plan 同时包含 item_01 和 item_05，两者 action 均为 `render_evidence_gap`
- **实际分支**: `_required_output_degrade_issues` 遍历 `prompt.required_output_evidence_plan` 全部 plan item；对每个 `render_evidence_gap` item 检查 marker 后 segment 是否包含 `_GAP_OUTPUT_PHRASES`
- **预期行为**: artifact 应明确区分"已有测试证明"和"code-path 推理证明"两种证据强度
- **实际行为**: D2 第 1 条引用已有测试证明 item_01 阻断行为（正确）；第 2 条"No-live inspection proves item 05 has the same behavior"未明确说明这是 code-path 推理而非测试证明；第 3 条"combined item 01 + item 05 unsafe response reproduces the live-shaped issue pair"同样依赖 code-path 推理
- **直接证据**: 测试 `test_chapter_3_missing_basic_manager_info_without_gap_phrase_blocks_after_writer` 仅验证 item_01 单独阻断；`_required_output_degrade_issues` 代码路径对所有 plan item 一视同仁遍历，无 item 特殊逻辑；现有测试中无 Chapter 3 item_05 + item_01 组合阻断测试
- **影响**: 不影响诊断结论正确性（code-path 逻辑确定性高），但证据强度表述可更精确
- **建议改法和验证点**: D2 第 2-3 条可加注"code path certainty, no dedicated test"或在 planning gate 中补充组合测试
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

### 02-未修复-低-item_05 availability_status="unreviewed" 与 "missing" 行为等价性未显式论证

- **入口/函数**: `_required_output_action()` (`fund_agent/fund/chapter_writer.py:1005`)
- **文件(行号)**: artifact §3 D1; `chapter_writer.py:1022-1028`
- **输入场景**: item_05 availability_status="unreviewed"，template `when_evidence_missing="render_evidence_gap"`
- **实际分支**: `_required_output_action` 中 `status != "available"` 且 `status is not None`（"unreviewed" 满足），进入 `behavior == "render_evidence_gap"` 分支，返回 `"render_evidence_gap"`
- **预期行为**: artifact 应显式说明 "unreviewed" 与 "missing" 在 `_required_output_action` 中产生相同 action 的代码依据
- **实际行为**: D1 陈述 item_05 为 `render_evidence_gap/unreviewed`，但未显式论证 "unreviewed" 为何不触发 `block` 或其他分支
- **直接证据**: `chapter_writer.py:1022` 条件 `status == "available" or status is None` 对 "unreviewed" 为 False；`chapter_writer.py:1027` 条件 `behavior == "render_evidence_gap"` 对 item_05 为 True
- **影响**: 不影响诊断结论（action 确实是 `render_evidence_gap`），但读者需要自行验证
- **建议改法和验证点**: D1 可加一句"code at line 1022-1028: any non-available non-None status with `when_evidence_missing='render_evidence_gap'` returns `render_evidence_gap`, including 'unreviewed'"
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

## Findings Adversarial Verification Summary

以下逐条验证 artifact 核心声明：

| 声明 | 验证结果 | 证据来源 |
|---|---|---|
| 模板声明 item_01 和 item_05 均为 `render_evidence_gap` | **正确** | `docs/fund-analysis-template-draft.md`; no-live inspection |
| item_01 阻断行为匹配 live issue id | **正确** | 测试 `test_chapter_3_missing_basic_manager_info_without_gap_phrase_blocks_after_writer` line 378 验证 `writer:required_output_gap_missing:ch3.required_output.item_01` |
| item_05 阻断行为与 item_01 相同 | **code-path 确定** | `_required_output_degrade_issues` 遍历全部 plan item，无 item 特殊逻辑 |
| 组合复现匹配 live classification `missing_required_output_marker`/`prompt_contract`/`missing_required_marker` | **code-path 确定** | 两个 validation layer 均产生 `missing_required_output_marker` reason；`_terminal_from_writer_stop_reason` 映射为 `blocked_prompt_contract` |
| `_should_retry_writer_invalid_marker` 仅处理 Chapter 6 | **正确** | `runner.py:678` `if chapter_id != 6: return False` |
| Chapter 3 `missing_required_output_marker` 不进入 repair 路径 | **正确** | `runner.py:379-409` writer blocked 后仅调用 `_should_retry_writer_invalid_marker`，该函数排除非 Chapter 6 |
| repair context 基础设施可用但 Chapter 3 未接入 | **正确** | `repair.py:178-208` `repair_context_from_writer_invalid_marker` 仅处理 `writer:invalid_anchor_marker` 前缀 |
| prompt-contract 与 provider runtime diagnostics 分离 | **正确** | `chapter_writer.py:1759-1784` 和 `1787-1834` 两层 validation 均在 writer 层；测试 `test_writer_prompt_contract_blocked_records_diagnostic_category` 验证 `provider_runtime_category is None` |
| summary/chapter attempt-count mismatch 是非阻断诊断残差 | **正确** | 残差已在 artifact §6 记录，不影响根因分类 |

## Open Questions

- 无。所有 controller judgment 要求的四个诊断问题均被回答，证据链完整。

## Residual Risk

1. **组合测试覆盖缺口**: Chapter 3 item_01 + item_05 同时 `render_evidence_gap` 且均缺少 gap phrase 的组合阻断场景无独立测试。当前依赖 code-path 推理（确定性高），planning gate 可考虑补充。
2. **Chapter 6 行为隔离**: planning gate 实现 Chapter 3 repair route 时，需验证 `_should_retry_writer_invalid_marker` 的 Chapter 6 only 语义不被意外改变。
3. **"unreviewed" 状态长期含义**: item_05 的 `availability_status=unreviewed` 是否在其他上下文中可能产生不同于 "missing" 的行为（如 audit 或 reporting 层），本次 review 未覆盖。

## Verdict

```text
PASS
```

artifact 诊断矩阵经 adversarial 验证成立。根因 `CH3_REQUIRED_OUTPUT_GAP_MARKER_WRITER_BLOCK_HAS_NO_REPAIR_RETRY_ROUTE` 由直接代码证据支撑。no-live 边界维护良好，无 overclaiming。item_05 证据基于 code-path 推理，逻辑确定性高，不阻断 verdict。next gate 推荐 `Provider/LLM Chapter 3 Missing-required-marker Narrow No-live Fix Planning Gate` 合适。发现两项低严重度 clarity 改进建议，不阻断 routing。
