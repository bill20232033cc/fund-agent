# MVP Gate 4 final_chapter_assembler + chapter 0 + CLI --use-llm Plan Review (AgentDS)

日期：2026-05-30
角色：AgentDS plan reviewer
Gate：`MVP Gate 4: final_chapter_assembler + chapter 0 + CLI --use-llm plan gate`
分类：`heavy`

## Verdict

**PASS**

Plan 在 slice 拆分、边界归属、fail-closed policy、第 0/7 章约束和禁止事项上均与 AGENTS.md、design.md §5.4/§5.4.1、模板 CHAPTER_CONTRACT 及 Gate 1-3 accepted contracts 一致。以下 7 个 findings 需在 implementation 或 controller judgment 中处理，但不构成 BLOCKED。

---

## Findings

### F1 [MEDIUM] 第 0 章输入压缩风险：500 字符结论可能不足以支撑封面页

- **文件**：plan §4.4；Gate 3 `chapter_orchestrator.py:65` (`MAX_ACCEPTED_CONCLUSION_CHARS = 500`)
- **问题**：第 0 章需从最多 7 条 `AcceptedChapterConclusion`（每条 ≤500 字符）中合成 9 个 required output items。其中“当前最值得盯住的变量”“什么变化会升级、降级或终止当前动作”等需要具体阈值和条件，500 字符的结论摘要可能已被截断。
- **证据**：plan §4.4 mapping table 将“当前最值得盯住的变量”映射到“第 7 章下一轮验证计划或第 6 章主要风险”，但第 6 章 accepted conclusion 的 500 字符可能只保留风险名称而不保留具体跟踪变量。
- **影响**：第 0 章可能大量输出“见第 N 章 accepted conclusion，当前缺少可压缩为封面项的结论”的 fallback，降低封面页实用性。
- **建议**：在 4A implementation 的 test case 中构造 realistic truncated conclusions（模拟 Gate 3 500 字符截断产出），验证第 0 章在最佳/最差输入下的输出质量。如果 fallback 比例过高，记录为 residual 并在后续 gate 中考虑提高结论长度上限或允许第 0 章访问 `FinalJudgmentDecision.reasons`。

### F2 [MEDIUM] 第 7 章“支撑判断的核心依据”可能输出内部规则消息而非投资者友好解释

- **文件**：plan §4.5；`final_judgment.py:25-34` (reason constants)
- **问题**：plan §4.5 规定第 7 章核心依据使用 `FinalJudgmentDecision.reasons`。当前 reasons 是派生规则内部消息（如“检查清单存在黄灯或灰灯问题，需要最小验证”），并非面向投资者的 narrative。若逐字渲染，第 7 章核心依据读起来像审计日志而非分析结论。
- **证据**：`final_judgment.py:32` — `_CHECKLIST_WATCH_REASON = "检查清单存在黄灯或灰灯问题，需要最小验证。"`。该文本未提及具体问题、具体信号或下一步动作。
- **影响**：中等。第 7 章核心依据的表达质量可能低于模板要求。但 plan 已将此风险标记为 residual（§4.5 Residual: “如果 review 认为 deterministic 第 7 章不满足模板表达质量，可在后续开 chapter7 writer/auditor 独立 gate”）。
- **建议**：4A implementation 应在 `_build_chapter7_markdown()` 中将 reasons 作为依据来源之一，同时从第 1-6 章 accepted conclusions 中提取与 judgment 方向一致的结论短句作为补充。在 test 中断言核心依据包含至少一条来自 accepted conclusions 的具体信息（非纯 rule reason）。若实现选择只输出 reasons verbatim，必须在 implementation evidence 中声明并在 residual 中记录表达质量风险。

### F3 [MEDIUM] 第 0 章从 chapter 7 conclusion_markdown 中解析 final judgment 是脆弱的字符串依赖

- **文件**：plan §4.4 mapping table；“第 7 章 accepted conclusion 的 `最终判断` 行”
- **问题**：plan 规定第 0 章只能接收 `AcceptedChapterConclusion`（含 `conclusion_markdown: str`）。chapter 0 mapping 需要从 chapter 7 的 conclusion_markdown 字符串中提取“当前动作”（🟢值得持有/🟡需要关注/🔴建议替换），但 `AcceptedChapterConclusion` 没有 typed judgment 字段。这要求 chapter 0 做 markdown 字符串解析。
- **证据**：plan §4.4 数据流显示 chapter 7 先生成 markdown，再构造 `AcceptedChapterConclusion(chapter_id=7)`，再交给 chapter 0。
- **影响**：若 chapter 7 markdown 格式在未来调整（如增加修饰文本、调整 emoji 前缀），chapter 0 的字符串解析可能静默失败，输出错误的动作或 fallback。
- **建议**：两种方案（implementation worker 选择，reviewer 确认）：
  - (a) 在 chapter 7 conclusion 构造时为 `AcceptedChapterConclusion` 增加可选的 typed `final_judgment: FinalJudgment | None` 字段（仅 chapter_id=7 时有值），chapter 0 读取该字段而非解析 markdown。
  - (b) 保持当前设计，但在 `_build_chapter0_markdown()` 中对 judgment label 解析失败时记录 blocking issue 而非静默 fallback。
  - 方案 (a) 不违反“第 0 章不接收 `FinalJudgmentDecision`”约束，因为 `FinalJudgment` 是独立的 Literal type，不是 `FinalJudgmentDecision` dataclass。

### F4 [LOW] 4C CLI 在无 4D provider 时的 fail-closed 实现方式未明确

- **文件**：plan §4.6、§4.8
- **问题**：plan §4.6 规定“如果 production provider construction 仍未完成，`--use-llm` 必须 fail-closed”；§4.8 将 provider construction 拆为 4D。但 4C 的 CLI 代码需要构造 `ChapterOrchestratorLLMClients` 才能调用 `analyze_with_llm()`，而构造真实 client 的能力属于 4D。
- **证据**：plan §4.6 末尾：“Slice 4C 可以先接入 `--use-llm` flag 和 Service branching，但不得注入 fake pass”。
- **影响**：4C 实现者可能不清楚应该用什么机制在 CLI 层 fail-closed。如果 4C 中硬编码 provider unavailable 检查，这些代码在 4D 完成后需要替换。
- **建议**：在 4C 中提供一个明确命名的 factory helper（如 `_build_llm_clients_or_fail()`），在 4D 未实现时抛出 `RuntimeError("LLM provider 未配置/未实现")`。4D 子 gate 只需替换该 helper 的内部实现，不改变 CLI 的 control flow。

### F5 [LOW] Plan 未明确 `_run_analysis_core()` 的可见性和复用路径

- **文件**：plan §4.6；`fund_agent/services/fund_analysis_service.py`
- **问题**：plan §4.6 规定 `analyze_with_llm()` 第 1 步“调用现有 `_run_analysis_core(...)`”。该方法是 `FundAnalysisService` 的私有方法还是模块级函数？若为私有方法且签名与 LLM use case 需求不完全匹配，4B 实现可能需要重构。
- **建议**：4B implementation worker 应先读取 `_run_analysis_core()` 当前签名，确认可以被 `analyze_with_llm()` 直接复用。如需调整签名（例如增加参数控制是否运行 quality gate），必须在 implementation evidence 中记录变更及理由。

### F6 [LOW] Assembly render order vs generation order 的区分未显式说明

- **文件**：plan §4A step 6
- **问题**：plan 规定 report markdown 顺序为 0,1,2,3,4,5,6,7，同时 §4.4 数据流规定先生成 chapter 7 再生成 chapter 0（因为 chapter 0 依赖 chapter 7 的结论）。这两者不矛盾（render order ≠ generation order），但 plan 未显式区分，implementation worker 可能混淆。
- **建议**：在 4A implementation steps 中增加一条注释：生成顺序为 1-6 → 7 → 0，渲染顺序为 0 → 1-6 → 7。

### F7 [INFO] 4D 子 gate ownership 和 plan 编写责任未分配

- **文件**：plan §4.8、§5 (Slice 4D)
- **问题**：plan 将 4D 的开启与否交给 controller decision，但未指定如果开 4D 子 gate，谁负责编写 provider-specific implementation plan。
- **建议**：controller judgment 应明确 4D plan 的 owner（建议由同一 plan writer 在 4A-4C accepted 后编写，或由 controller 另行指派）。

---

## 逐项挑战结果

### 1. Gate 4 slice 拆分是否可执行

**通过。** 4A → 4B → 4C 顺序合理：assembler contract 必须先稳定（4A），Service use case 才能消费（4B），CLI 才能接入（4C）。4D 正确拆分为子 gate/residual。每个 slice 的 allowed files、implementation steps、tests 和 validation commands 均有明确定义。

### 2. final_chapter_assembler 放 Service 是否正确

**通过。** 符合 AGENTS.md 归属规则：Service 负责报告生成和质量策略选择。assembler 不理解基金类型、年报章节、ITEM_RULE 或 preferred_lens（这些属于 Fund 层），只消费已 accepted 的章节结果和 FinalJudgmentDecision。与 Gate 3 ChapterOrchestrator 的 Service 归属一致。

### 3. 第 0 章 accepted-conclusions-only 是否足够防止新事实

**基本通过，见 F1、F3。** plan §4.4 的输入限制（只接收 `AcceptedChapterConclusion` tuple + `FinalAssemblyPolicy`）和输出限制（不输出证据小节、不生成 anchor marker、不新增数值）构成有效的 fail-closed 围栏。确定性 assembly（无 LLM）进一步降低了引入幻觉的风险。主要残余风险是 500 字符结论的信息密度（F1）和 chapter 7 judgment 的字符串解析脆弱性（F3）。

### 4. 第 7 章是否真的不改 final judgment 语义

**通过。** plan §4.5 明确：`FinalJudgmentDecision.selected_judgment` 是唯一真源；第 7 章不得从 LLM 或 accepted conclusions 重新选择判断；不得调用或修改 `derive_final_judgment()`；label mapping 固定；developer_override source 和 conflict_reasons 必须保留。实现约束足以防止 final judgment 语义被意外修改。见 F2 关于表达质量的 residual concern。

### 5. partial orchestration policy 是否 fail-closed

**通过。** plan §4.7 默认 reject as incomplete。三种状态的行为明确定义：partial → incomplete/null、blocked → blocked/null、CLI → exit 1 + stderr。禁止 degrade 行为（不拼凑 partial report、不静默 fallback deterministic、不输出缺章报告）。debug mode 需显式 opt-in 且有 INCOMPLETE 标记。

### 6. CLI --use-llm 在 provider 未实现时的处置

**通过，见 F4。** plan 正确将 provider construction 拆为 4D 子 gate/residual。4A/4B/4C 保持 provider-agnostic。`--use-llm` 在 provider 不可用时 fail-closed（exit 1, stderr 说明），不静默回落 deterministic。4C 的 fail-closed 实现方式需要明确（F4），但不改变设计正确性。

### 7. allowed files / validation 是否完整

**通过。** 每个 slice 的 allowed files 和 do-not-edit 列表明确。validation matrix 覆盖：ruff、pytest per slice、regression guard（Gate 1/2 tests）、coverage 阈值、static boundary check（rg 扫描 dayu/extra_payload/provider SDK/PDF/cache/source helper）。review matrix 要求至少 2 个独立 reviewer per slice。

### 8. 约束合规检查

| 约束 | 来源 | 合规 | 备注 |
|------|------|------|------|
| UI → Service → Host → Agent | AGENTS.md | ✅ | 无 Host/Agent 创建 |
| 不修改 golden/quality/score/FQ/final judgment | startup-packet §7 | ✅ | plan §3 Non-Goals 明确 |
| 无 extra_payload | AGENTS.md | ✅ | 所有参数 typed dataclass |
| 无直接 PDF/cache/source helper | AGENTS.md | ✅ | plan §3 + static boundary check |
| 无 dayu | AGENTS.md | ✅ | plan §3 + static boundary check |
| 不修改 derive_final_judgment() | startup-packet §7 | ✅ | plan §4.5 明确禁止 |
| 确定性 analyze/checklist 不变 | design.md §5.4.1 | ✅ | plan §4.6 CLI 行为 + §3 Non-Goals |
| FundDocumentRepository 访问 | AGENTS.md | ✅ | 复用 _run_analysis_core()，不新增直接访问 |
| fallback 策略 | AGENTS.md | ✅ | 不在本 gate scope |
| 不修改 AGENTS.md / template | startup-packet §7 | ✅ | plan §8 |

---

## Residual Risks (for controller judgment)

1. **F1 + F3 叠加风险**：如果第 0 章因 500 字符截断和 judgment 字符串解析脆弱性同时触发，封面页可能出现“当前动作为 fallback + 核心依据为 fallback”的双重降级。controller 可考虑在 4A 实现后增加一个专门的 chapter 0 输出质量抽查（用真实 Gate 3 结论产物而非 mock）。

2. **F2 表达质量**：第 7 章核心依据如果只输出 rule reasons，用户体验可能低于确定性 renderer 当前水平。这不违反 correctness 约束，但可能影响 `--use-llm` 路径的感知价值。

3. **4D 延迟的连锁影响**：如果 4D 被记录为 residual 而不立即开子 gate，`--use-llm` 路径虽然在 CLI 层 fail-closed，但无法被用户实际使用。controller 应评估这是否影响 MVP Gate 4 的整体交付意义。

---

## Review Basis

- `AGENTS.md` (full)
- `docs/current-startup-packet.md` (full)
- `docs/design.md` §5.4 / §5.4.1 (lines 437-511)
- `docs/fund-analysis-template-draft.md` 第 0 章、第 7 章 CHAPTER_CONTRACT
- `docs/reviews/mvp-gate3-chapter-orchestrator-controller-judgment-20260530.md` (full)
- `docs/reviews/mvp-gate4-final-assembler-cli-plan-20260530.md` (full)
- 当前代码事实：`chapter_orchestrator.py`、`final_judgment.py`、`fund_analysis_service.py`、`cli.py`
