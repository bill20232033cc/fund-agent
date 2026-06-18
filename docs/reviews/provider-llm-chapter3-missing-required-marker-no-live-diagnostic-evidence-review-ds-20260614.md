# Provider/LLM Chapter 3 Missing-required-marker No-live Diagnostic Evidence Review (DS)

Date: 2026-06-14

Role: DS independent reviewer

Gate: `Provider/LLM Chapter 3 Missing-required-marker No-live Diagnostic Evidence Gate`

Review target: `docs/reviews/provider-llm-chapter3-missing-required-marker-no-live-diagnostic-evidence-20260614.md`

Final verdict: **PASS** — no-live evidence supports `READY_FOR_NO_LIVE_FIX_PLANNING_GATE`

## Scope

This review verifies whether the no-live diagnostic evidence supports D1-D4 and the refined root cause, and checks command evidence, no-live boundaries, and no live/provider/source/readiness overclaim.

Source evidence used: `AGENTS.md`, `docs/current-startup-packet.md`, `docs/implementation-control.md`, controller judgment `cbcf586`, `fund_agent/agent/runner.py` (lines 355-420, 535-619, 645-689, 1348-1377, 1544-1623), `fund_agent/agent/repair.py` (lines 178-208), `fund_agent/fund/chapter_writer.py` (lines 1680-1834, 2109-2159), `docs/fund-analysis-template-draft.md` (lines 665-697), and cited tests verified present on disk.

No live/provider/LLM/network/PDF/FDR/source/analyze/checklist/readiness/release/PR commands were executed. Source, tests, runtime, control docs, design docs, and README were not modified.

## Findings

### F1-中-无现场检查命令不可复现
- **入口/函数**: 证据 §2 Evidence Commands，Python 检查
- **文件(行号)**: 证据行 64-65
- **输入场景**: 需要复现 typed prompt plan 观察结果时
- **实际分支**: 占位符命令 `<inspection using tests.agent.test_runner helpers and run_agent_body_chapters>` 不是可执行的具体命令
- **预期行为**: 无现场证据应给出可直接执行的命令，使观察结果可复现
- **实际行为**: 命令是占位符，缺失模块导入、函数调用和参数，无法独立复现
- **直接证据**: 证据行 64：`uv run python -c '<inspection using tests.agent.test_runner helpers and run_agent_body_chapters>'`
- **影响**: 证据行 68-85 的 typed prompt plan 观察结果（`status blocked blocked missing_required_output_marker`、`plans`、`issues`）缺少可复现命令链。D1 可通过模板真源独立验证，D2 可通过已有测试独立验证，但 plan 级别的 item_01/item_05 状态观察缺少直接复现路径
- **建议改法和验证点**: 若需加强证据链，补写具体可执行命令（含 import 和函数调用）。当前 D1/D2 通过模板和测试可独立证明，此缺陷不推翻 verdict
- **修复风险（低）**: 仅补充命令文本，不改变结论
- **严重程度（中）**: 降低特定观察的可复现性，但不削弱 D1-D4 的核心结论

### F2-中-证据未检查修复上下文函数同样限定第 6 章范围
- **入口/函数**: `repair_context_from_writer_invalid_marker`、`_should_retry_writer_invalid_marker`
- **文件(行号)**: `fund_agent/agent/repair.py` 行 199；`fund_agent/agent/runner.py` 行 687
- **输入场景**: 若后续修复将 writer-block retry 扩展到第 3 章 `writer:required_output_gap_missing`
- **实际分支**: D3 证明 `_should_retry_writer_invalid_marker()`（runner.py:678-689）有 chapter_id=6、stop_reason="llm_contract_violation"、issue 前缀三层独立关卡，第 3 章 missing_required_output_marker 全部未通过
- **预期行为**: 证据应同时检查 `repair_context_from_writer_invalid_marker()` 是否也为第 6 章独占
- **实际行为**: 证据 D3 只分析了 retry routing 函数，未检查 `repair_context_from_writer_invalid_marker()`（repair.py:199）也通过 `issue.issue_id.startswith("writer:invalid_anchor_marker")` 过滤，不会为 `writer:required_output_gap_missing` issue 生成正确修复上下文
- **直接证据**: repair.py:199：`if issue.issue_id.startswith("writer:invalid_anchor_marker")`——修复上下文函数与 retry 检查函数有相同范围限定
- **影响**: 第 3 章修复方案需要同时修改 runner.py 的 retry routing 和 repair.py 的 context 构造，而不仅是扩展 `_should_retry_writer_invalid_marker`。证据的 `CH3_REQUIRED_OUTPUT_GAP_MARKER_WRITER_BLOCK_HAS_NO_REPAIR_RETRY_ROUTE` 根因描述只涵盖了 routing，未明确 context 函数也受限。下一 planning gate 应同时检查两处代码
- **建议改法和验证点**: 下一 fix planning gate 应将 repair.py 第 199 行的 `writer:invalid_anchor_marker` 过滤也纳入 scope，决定是为 `writer:required_output_gap_missing` 新增并行 function 还是泛化现有 function
- **修复风险（低）**: 不影响当前证据 verdict，只丰富 planning gate 的输入
- **严重程度（中）**: 根因表述轻微不完整——修复涉及两个文件两处限定，证据只点名了一处

### F3-低-D4 尝试次数不一致未追踪到具体代码位置
- **入口/函数**: summary.json `first_failed.attempt_count` vs `chapter-03.json` `attempt_index`
- **文件(行号)**: 证据行 138
- **输入场景**: 读取 summary 和 chapter 元数据比较尝试次数
- **实际分支**: 证据正确携带此残余但不追踪具体代码
- **预期行为**: 无现场诊断已足够，此残余不需要阻挡下一 gate
- **实际行为**: 证据描述 `summary records the first failed attempt count as 1, while the chapter file records the prompt diagnostic as attempt_index=0` 但未解释为什么尝试计数源不同
- **直接证据**: 证据行 138：`The summary/chapter attempt-count mismatch remains a non-blocking diagnostic artifact inconsistency`
- **影响**: 对 planning gate 无实质影响——planning 不需要此残余解决即可设计修复。但若后续 gate 需要理解尝试生命周期，此残余可能需要独立诊断
- **建议改法和验证点**: 可在 planning gate 记录为 deferred diagnostic，不要求 planning 解决
- **修复风险（低）**: 仅文档化残余
- **严重程度（低）**: 不影响下一 gate 推进，属已知残余

## D1-D4 逐项裁决

### D1: Prompt Payload And Typed Policy — PROVEN

模板真源 `docs/fund-analysis-template-draft.md` 行 665-697 声明 item_01 至 item_06 均为 `when_evidence_missing: "render_evidence_gap"`。已存在测试（`test_writer_prompt_contains_typed_required_output_ids_not_freeform_fallbacks`）证明 typed prompt 使用稳定 required-output id 而非自由文本标签。无现场检查的 plan 观察结果与其他证据一致。D1 可通过模板真源和已有测试独立证明，不依赖占位符命令。

### D2: Fake-writer Reproduction — PROVEN

代码路径完整验证：`_required_output_degrade_issues()`（chapter_writer.py:1787-1834）检查 `render_evidence_gap` action 的输出是否包含 approved gap 措辞，缺失时生成 `writer:required_output_gap_missing:<item_id>` issue，reason 为 `missing_required_output_marker`。`_stop_reason()`（行 2109-2122）取首条 issue reason。Runner 分类链：`_terminal_from_writer_stop_reason()`（runner.py:1364）→ `blocked_prompt_contract`，`_failure_category_from_writer_result()`（runner.py:1568）→ `prompt_contract`，`_failure_subcategory_from_writer_stop_reason()`（runner.py:1617）→ `missing_required_marker`。已存在测试 `test_chapter_3_missing_basic_manager_info_without_gap_phrase_blocks_after_writer` 证明无现场 fake writer 可复现 item 01 阻断。分类链与接受的 live metadata 一致。

### D3: Repair-context Propagation — GAP PROVEN（决定性证据）

直接代码证据链：

1. Writer-blocked 后唯一进入 retry 的路径是 `_should_retry_writer_invalid_marker()`（runner.py:389）
2. 该函数三层独立关卡（runner.py:678-689）：
   - `chapter_id != 6` → 第 3 章在此直接返回 `False`
   - `stop_reason != "llm_contract_violation"` → 第 3 章 stop_reason 为 `missing_required_output_marker`，也不匹配
   - issue 前缀不为 `writer:invalid_anchor_marker` → 第 3 章 issue 为 `writer:required_output_gap_missing`，也不匹配
3. 即使 retry routing 被扩展，`repair_context_from_writer_invalid_marker()`（repair.py:199）同样过滤 `writer:invalid_anchor_marker`，不会为第 3 章 issue 生成正确上下文

第 3 章 `missing_required_output_marker` 在所有关卡通不过，writer-block 后直接返回 `ChapterTask(status="blocked", …)`，不进入 retry。已存在测试证明通用 repair context 可渲染到 prompt 中，typed required-output items 可在 audit 修复中保留——说明 prompt 和 context 基础设施可支持修复，但第 3 章的 writer-block retry 路径根本不存在。

根因 `CH3_REQUIRED_OUTPUT_GAP_MARKER_WRITER_BLOCK_HAS_NO_REPAIR_RETRY_ROUTE` 是从 disposition 分类 `LLM_WRITER_OUTPUT_NONCOMPLIANCE_WITH_EXISTING_TYPED_REQUIRED_OUTPUT_GAP_MARKER_CONTRACT` 的精炼，不是矛盾。Disposition 回答"当前发生了什么"，精炼根因回答"为什么当前没有修复路径"。见 F2——修复涉及两个文件两处代码限定。

### D4: Prompt-contract vs Provider Runtime Diagnostics — PROVEN

分类链（D2 已引用代码行号）完全在 `chapter_writer.py` 中执行，先于任何 provider 交互。`_failure_category_from_writer_result()` 将 `missing_required_output_marker` 归入 `prompt_contract`，与 `provider_runtime` 明确区分。无现场复现同样在本地 writer 输出验证中失败，不使用 provider。因此 live metadata 中 `provider_attempt_count=0` 和 sparse/null runtime 字段的含义是：终态失败在 prompt-contract/writer-parse 层被分类，不是在 provider runtime 层被分类。

## 范围与边界检查

| 检查项 | 结论 |
|---|---|
| 证据是否修改 source/test/runtime/control/design/README？ | 否，符合 no-live 边界 |
| 是否运行 live/provider/LLM/network/PDF/FDR 命令？ | 证据声明未运行，符合 gate 约束 |
| 是否声称 provider availability/quality 结论？ | 否，D4 正确拒绝此推断 |
| 是否声称 source/EID/fallback 结论？ | 否，明确拒绝 |
| 是否声称 release/readiness 结论？ | 否，最终状态保持 `NOT_READY` |
| 是否声称 live completion/proof？ | 否，正确作为残余携带 |
| 无现场证据命令是否使用安全元数据和已有测试？ | 是，F1 记录占位符命令但核心结论通过模板和代码可独立证明 |

## Root-cause Refinement 检查

精炼根因 `CH3_REQUIRED_OUTPUT_GAP_MARKER_WRITER_BLOCK_HAS_NO_REPAIR_RETRY_ROUTE` 与 disposition 分类 `LLM_WRITER_OUTPUT_NONCOMPLIANCE_WITH_EXISTING_TYPED_REQUIRED_OUTPUT_GAP_MARKER_CONTRACT` 之间无矛盾：

- Disposition 回答"当前失败原因"：writer 输出未满足 typed required-output gap marker 契约
- 精炼根因回答"为什么没有修复尝试"：writer-block retry 路径限定在第 6 章 invalid anchor marker

证据链 1-5（证据行 160-166）逻辑正确。被拒绝的候选根因（行 170-177）拒绝理由充分：模板 policy 存在（D1）、writer validator 正确工作（D2）、provider 证据明确拒绝（D4）、truncation 被 live metadata 排除（`finish_reason=stop`、`response_chars=1906 < max_output_chars=12000`）、repair context 路径根本不到达（D3）。

## Open Questions

- 无现场检查可复现命令（F1）是否会持续成为后续 gate 的障碍？——若后续 gate 全部依赖模板真源和已有测试，则占位符命令不影响推进。若需要新增 plan 级别观察，需补写具体命令。
- `repair_context_from_writer_invalid_marker` 应泛化还是新增并行 function？——这是 fix planning gate 要决定的问题，当前证据已足够支撑 planning。
- 第 3 章 writer-block retry 修复后，是否需要更新 `_terminal_from_writer_stop_reason` 中 `missing_required_output_marker` 的 terminal 分类（当前 `blocked_prompt_contract`）？——修复后可能需要新增中间态，但 planning gate 应自行判断。

## Residual Risk

- F1 占位符命令残存：后续若需复现 plan 级别观察，需补写具体命令
- F2 repair context 函数范围残存：planning gate 需同时检查 repair.py:199 的 `writer:invalid_anchor_marker` 过滤
- 第 3 章 required-output repair 的精确措辞、issue id 传递和预算消耗策略尚未设计（证据 §6 正确携带）
- 已有测试覆盖了 prompt 构造、gap 检测和上下文渲染的局部行为，但未覆盖"第 3 章 missing required marker → retry → repair context → 二次 writer 调用"的集成路径——planning gate 应决定是否需要

## Final Verdict

```text
PASS — 无现场证据支持 READY_FOR_NO_LIVE_FIX_PLANNING_GATE
```

D1-D4 的核心结论经过直接代码阅读验证。精炼根因不矛盾于 disposition 分类。证据遵守无现场边界，不声称 provider/source/readiness 证明。F1-F3 是非阻断发现，不推翻 verdict，但应作为 planning gate 的输入残余。
