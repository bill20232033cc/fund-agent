# MVP Gate 4 Slice 4A implementation review — AgentDS

日期：2026-05-30
角色：AgentDS implementation reviewer
Gate：`MVP Gate 4 Slice 4A: Service final_chapter_assembler implementation gate`
状态：review artifact；不改代码、不 commit。

## 1. Review inputs

- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/design.md` §5.4 / §5.4.1
- `docs/reviews/mvp-gate4-final-assembler-cli-plan-20260530.md`
- `docs/reviews/mvp-gate4-final-assembler-cli-plan-decision-20260530.md`
- `docs/reviews/mvp-gate4-final-assembler-slice4a-implementation-evidence-20260530.md`
- Workspace changes: `fund_agent/services/final_chapter_assembler.py`, `fund_agent/services/__init__.py`, `tests/services/test_final_chapter_assembler.py`, `tests/README.md`

## 2. Verdict

**PASS** — 无 BLOCKING finding。4 MEDIUM、3 LOW finding，均不阻断 Slice 4A acceptance。

## 3. Findings

### MEDIUM

#### M1. `_validate_policy` 死代码：重复检查不可达

- 文件：`fund_agent/services/final_chapter_assembler.py:322–323`
- Severity：MEDIUM
- 描述：`len(set(chapter_ids)) != len(chapter_ids)` 重复检查永远不可达，因为 L324 的 `chapter_ids != DEFAULT_REQUIRED_BODY_CHAPTER_IDS` 严格相等检查会先拦截所有非 `(1,2,3,4,5,6)` 的 tuple。两行代码不会产生错误行为，但会误导未来 reader 认为该分支可能被触发。
- 建议：如不计划开放 `required_body_chapter_ids` 配置，移除重复检查；如计划开放，将严格相等检查替换为更宽松的范围检查并保留重复检查。

#### M2. test gap：第 0 章未做证据/锚点负向断言

- 文件：`tests/services/test_final_chapter_assembler.py`
- Severity：MEDIUM
- 描述：Plan §4.4 明确要求第 0 章不输出 `证据与出处`、`> 📎 证据`、`<!-- anchor:`。代码实现确实不产生这些内容（已验证 `_render_chapter0_markdown`），但测试中没有任何负向断言验证。实现变更时没有 regression guard。
- 建议：在 `test_assembles_report_in_render_order` 或 `test_chapter0_sparse_and_truncated` 中增加：
  ```python
  assert "证据与出处" not in result.chapter0_markdown
  assert "> 📎 证据" not in result.chapter0_markdown
  assert "<!-- anchor:" not in result.chapter0_markdown
  ```

#### M3. test gap：第 0 章未显式验证不依赖 structured facts

- 文件：`tests/services/test_final_chapter_assembler.py`
- Severity：MEDIUM
- 描述：Plan §4.3 要求 final assembler 不接收 `StructuredFundDataBundle`、`ChapterFactProjection`。代码签名确实不接收（只接收 `FinalChapterAssemblyInput`，其内部不携带 bundle/projection），但测试没有静态导入检查验证 `final_chapter_assembler` 模块不导入 `StructuredFundDataBundle` / `ChapterFactProjection`。
- 建议：增加导入隔离测试，类似现有 `test_service_public_exports_final_assembler_contract`：
  ```python
  def test_final_assembler_does_not_import_facts_or_projections():
      import fund_agent.services.final_chapter_assembler as fca
      assert "StructuredFundDataBundle" not in dir(fca)
      assert "ChapterFactProjection" not in dir(fca)
  ```

#### M4. `_first_non_empty_line` 冗余两遍扫描

- 文件：`fund_agent/services/final_chapter_assembler.py:937–945`
- Severity：MEDIUM
- 描述：函数先取 `splitlines()[:1]` 只查第一行，若空再完整扫描 `splitlines()`。第一遍 `[:1]` 的分片语义与 `_SUPPORTING_SNIPPET_LINE_LIMIT=1` 耦合，但该常量本意是给 `_supporting_conclusion_snippets` 使用的，不是给通用 helper 使用的。对外部调用者而言，这段代码等价于“取第一条非空行”，但用了非直觉的两阶段实现。
- 建议：简化为单次扫描：
  ```python
  for line in text.splitlines():
      if line.strip():
          return line.strip()
  return ""
  ```
  或保留当前语义但使用独立常量，区分 `_SUPPORTING_SNIPPET_LINE_LIMIT` 和本函数的 scan limit。

### LOW

#### L1. test gap：Gate 3 `blocked` 与 `partial` 共用同一路径但无独立测试

- 文件：`tests/services/test_final_chapter_assembler.py`
- Severity：LOW
- 描述：`test_incomplete_when_orchestration_partial` 只测了 `status="partial"`。`status="blocked"` 走同一 `orchestration_not_accepted` 路径，代码行为一致。但无显式测试。
- 建议：可加一条 `status="blocked"` → `incomplete` 的参数化 case。

#### L2. test gap：Gate 3 结果重复章节的 issue 路径无显式测试

- 文件：`tests/services/test_final_chapter_assembler.py`
- Severity：LOW
- 描述：`_validate_orchestration` 在 L388–399 检测 Gate 3 结果中重复的 `chapter_id` 并返回 blocking issue，但无测试构造带重复章节的 `ChapterOrchestrationResult` 验证该路径。
- 建议：增加构造含重复章节 ID 的 orchestration result 的测试。

#### L3. test gap：`multiple_required_chapter_ids` 空元组边界

- 文件：`tests/services/test_final_chapter_assembler.py`
- Severity：LOW
- 描述：`FinalAssemblyPolicy()` 的 `required_body_chapter_ids=()` 边界由 `_validate_policy` 以 ValueError 拒绝，但无显式测试。
- 建议：在 `test_policy_rejects_chapter0_lens_style_reconfiguration` 中加入 `FinalAssemblyPolicy(required_body_chapter_ids=())` 的 ValueError 断言。

## 4. Positive confirmations

以下检查项全部通过，无发现：

### 4.1 只实现 Slice 4A

- 未编辑 `fund_agent/fund/**`、`fund_agent/ui/cli.py`、`fund_agent/services/fund_analysis_service.py` ✓
- 未编辑 `docs/design.md`、`docs/current-startup-packet.md`、`docs/implementation-control.md` ✓
- 未编辑 golden、score、quality gate、final judgment semantic 文件 ✓
- 未添加 production LLM provider ✓
- 未添加 Host/Agent/dayu ✓

### 4.2 final assembler Service 归属正确

- 文件位于 `fund_agent/services/` ✓
- `__init__.py` 正确导出 Gate 4 public API ✓
- assembler 不理解基金类型、年报章节、ITEM_RULE、preferred_lens 领域规则 ✓
- assembler 不读取 PDF/repository/source helper ✓

### 4.3 chapter 0 只消费 accepted conclusions / typed chapter7 summary

- `_render_chapter0_markdown` 签名只接收 `conclusions: tuple[AcceptedChapterConclusion, ...]` 和 `chapter7_summary: FinalChapter7Summary` ✓
- 不接收 `StructuredFundDataBundle`、`ChapterFactProjection`、`FinalJudgmentDecision` ✓
- 不重新应用 `preferred_lens`、ITEM_RULE、fund_type ✓
- 不调用 LLM ✓
- 输入稀疏/截断时输出 fallback 文本，不编造数值 ✓
- 缺章输出 informational issue，不补事实 ✓

### 4.4 chapter 7 不改变 FinalJudgmentDecision 语义

- `selected_judgment` 是唯一动作真源 ✓
- 未调用 `derive_final_judgment()` ✓
- judgment label 映射固定：worth_holding → 🟢 值得持有，needs_attention → 🟡 需要关注，suggest_replace → 🔴 建议替换 ✓
- developer_override source 和 conflict_reasons 显式保留 ✓
- chapter7 结论不包含买入/卖出/仓位/收益预测 ✓

### 4.5 partial/incomplete fail-closed

- `orchestration.status != "accepted"` → `status="incomplete"`，`report_markdown=None` ✓
- missing accepted_draft → blocking issue，incomplete ✓
- missing accepted_conclusion → blocking issue，incomplete ✓
- 无 degrade 路径：不把 partial 拼成完整报告，不 fallback deterministic ✓
- `allow_incomplete_debug_markdown=False` 时不输出 debug 内容 ✓

### 4.6 render order 0 → 1-6 → 7

- `_assembled_chapter_ids` 生成顺序 `(0, 1, 2, 3, 4, 5, 6, 7)` ✓
- `_render_report_markdown` 按 0 → body chapters → 7 拼接 ✓
- 测试显式断言 chapter 0 在 chapter 1 之前、chapter 6 在 chapter 7 之前 ✓
- 生成顺序为 chapter7 summary 先于 chapter0 ✓

### 4.7 typed contracts / docstrings

- 所有 public dataclass 有完整中文 docstring ✓
- 所有 public 函数/方法有完整中文 docstring（含 Args/Returns/Raises） ✓
- 所有私有函数有中文 docstring ✓
- 模块有概览性中文 docstring ✓

### 4.8 tests 覆盖 plan decision A4–A8

- A4（chapter0 不重应用 preferred_lens）：`test_policy_rejects_chapter0_lens_style_reconfiguration` ✓
- A5（稀疏/截断不编造数字）：`test_chapter0_sparse_and_truncated_sources_do_not_invent_absent_numbers` + `test_chapter0_output_can_be_capped_without_new_facts` ✓
- A6（chapter7 合并 reasons + 第1-6章短句）：`test_assembles_report_in_render_order` 断言 chapter7 含 `规则依据` 和 `章节结论语境` ✓
- A7（chapter0 typed 当前动作来源）：chapter0 使用 `chapter7_summary.selected_judgment_label`，测试断言 `- **当前动作**：🟡 需要关注` ✓
- A8（生成顺序 vs 渲染顺序）：渲染顺序断言 chapter0 索引 < chapter1 索引，chapter6 < chapter7 ✓

### 4.9 无 extra_payload/dayu/golden/score/quality/final judgment semantic change

- `rg` 扫描：assembler 文件中无极词命中（仅 docstring 否定声明中提到） ✓
- 无 dayu、Host/Agent runtime ✓
- 无 quality gate、score、golden、FQ 引用 ✓
- `FinalJudgmentDecision` 语义不变 ✓

### 4.10 静态与回归

- `ruff check`：All checks passed ✓
- 9/9 test_final_chapter_assembler.py passed ✓
- 81/81 Gate 1–3 regression tests passed ✓
- `git diff --check`：clean ✓
- imports：仅 `fund_agent.fund.analysis.final_judgment` (FinalJudgment, FinalJudgmentDecision) 和 `fund_agent.services.chapter_orchestrator` (AcceptedChapterConclusion, ChapterOrchestrationResult, ChapterRunResult) ✓

## 5. Unverified items (out of scope for this review)

- Slice 4B Service `analyze_with_llm()` — 未实现
- Slice 4C CLI `--use-llm` — 未实现
- Slice 4D production LLM provider construction — 未实现
- Chapter 0/7 LLM polish / LLM audit — 不在 Slice 4A scope
- Evidence Confirm / E2 source verification — 不在 Slice 4A scope
- Host/Agent/dayu — deferred to Route C Gate 5
- 单文件覆盖率 ≥80% — 本 review 未运行 coverage，留待 controller 或后续 gate 验证

## 6. Residual risks

- **M2/M3 test gap**：如果未来在 `_render_chapter0_markdown` 中不慎加入证据锚点或 facts 读取，没有 regression test 拦截。建议在 slice 4B review 前补齐。
- **M1 死代码**：如果未来放宽 `required_body_chapter_ids` 严格相等约束，必须同步评估重复检查逻辑是否仍需保留。
- **Chapter 0 确定性压缩质量**：当 Gate 3 accepted conclusions 稀疏时，chapter 0 输出以 fallback 文本为主，可读性偏低。这是 correctness-first 策略的已知取舍，不是 bug。
