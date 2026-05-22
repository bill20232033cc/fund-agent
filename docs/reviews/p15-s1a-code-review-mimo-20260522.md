# P15-S1A Implementation Code Review — AgentMiMo（2026-05-22）

## Verdict

`PASS_WITH_FINDINGS`

P15-S1A implementation artifact 满足 source contract 和 stop conditions，遵守 AGENTS.md 边界约束，candidate 分类逻辑正确，provenance 记录充分，validation 与 artifact-only scope 相称。无阻断 finding。

## Review Scope

- Implementation artifact: `docs/reviews/p15-s1a-tracking-error-evidence-acquisition-implementation-20260522.md`
- Plan: `docs/reviews/p15-s1a-tracking-error-source-contract-evidence-acquisition-plan-20260522.md`
- Controller judgment: `docs/reviews/p15-s1a-plan-review-controller-judgment-20260522.md`
- Design truth: `docs/design.md`
- Control truth: `docs/implementation-control.md`
- Source code: `fund_agent/fund/extractors/performance.py`, `fund_agent/fund/data_extractor.py`

## Review Criteria

### 1. Source Contract 和 Stop Conditions 满足度

**PASS**

- Verdict `BLOCKED_NO_DIRECT_DISCLOSURE_EVIDENCE` 正确：12 个 candidate 中 0 个为 direct observed disclosure。
- Golden decision `do_not_edit_golden` 正确：artifact 明确拒绝从 `0.2%` daily deviation target 或 `2%` annualized tracking-error control target 添加 golden rows。
- Stop conditions 全部命中：`extract_performance(report).tracking_error` 返回 `extraction_mode="missing"`、`note="tracking_error_ambiguous"`、`value=None`、`anchors=()`，符合 "extractor 不是 direct" 停止条件。
- Source contract 的 12 项 acceptable evidence 字段要求在本 artifact 中无一满足，正确进入 blocked 路径。

### 2. AGENTS.md 边界遵守

**PASS**

- 年报访问通过 `FundDocumentRepository.load_annual_report("001548", 2024)` 和 `FundDataExtractor.extract("001548", 2024)` 完成，未直接操作 PDF cache、下载 helper 或 source adapter。
- 证据可溯源：所有 12 个 candidate 均标注年报章节、行号和原文短摘。
- 第一性原理：artifact 从原始年报文本出发逐行/逐表扫描，不依赖经验判断或间接证据。
- 显式参数：`fund_code="001548"`、`report_year=2024`、`force_refresh=False` 均显式声明。
- 未引入 Dayu runtime、Host、Engine、tool loop、LLM audit 或外部依赖。

### 3. 12 个 Candidate 分类是否足以支撑 BLOCKED_NO_DIRECT_DISCLOSURE_EVIDENCE

**PASS（有 finding）**

12 个 candidate 全部被正确分类为 `investment-objective target/limit`（6 个）或 `manager narrative`（6 个）。分类理由逐条给出，与 `performance.py` 的 `_TRACKING_ERROR_NEGATIVE_KEYWORDS`（`控制在`、`最小化`等）和 `_TRACKING_ERROR_ACTUAL_KEYWORDS`（`报告期`、`本报告期`等）语义一致。

两个含百分比数值的 candidate（`0.2%` 日偏离度控制目标、`2%` 年化跟踪误差控制限）均被正确识别为 investment-objective target/limit，不是 observed value。代码层面 `_tracking_error_context_is_target_or_ambiguous()` 正确命中 `控制在` 关键词，`_has_actual_tracking_error_signal()` 不会误触发（因为这些行不含 `报告期`/`本报告期` 等 actual signal）。

**Finding F1**: Classification summary 表的 class count 与 candidate 明细表不一致（详见下方）。

### 4. 误判风险检查

**PASS**

- Investment-objective target/limit → 已正确拒绝：`0.2%` 和 `2%` 均为控制目标/限值。
- Manager narrative → 已正确拒绝：§4 全部 6 个 candidate 为管理人关于跟踪误差控制策略的叙述，无数值披露。
- Benchmark-only → 不适用：artifact 单独记录 benchmark evidence 仅支持 `index_profile`。
- Standard deviation → 未发现：candidate 表中无标准差列命中。
- Ambiguous hit → 未发现：无同一上下文混有实际值和目标控制语义的情况。

### 5. Provenance 和 source_metadata=None 处理

**PASS**

- `source_metadata=None` 在 parsed-cache hit 场景下被正确记录：`source_metadata_present=False`。
- Artifact 显式声明 "Because source metadata is absent on this parsed-cache hit, this artifact records cache provenance but does not infer an external source URL or fallback status beyond available repository metadata"。
- Cache provenance 字段完整：`parsed_cache_hit=True`、`pdf_cache_hit=False`、`pdf_path=None`、`cache_schema_version=1`。
- 未伪造 source URL、fallback status 或外部来源信息。

### 6. Validation 与 artifact-only scope 相称性

**PASS**

- Validation commands 仅包含读取验证和现有测试，未引入新测试文件或代码变更。
- 4 条验证命令覆盖：repository identity + structured extraction、context inventory、full bundle extraction、existing extractor tests。
- `test_performance.py` 14 passed，覆盖 direct disclosure、target-only、ambiguous、standard deviation 和 table/text consistency 行为。

**Finding F2**: Plan 的 acceptance tests 列出 `tests/fund/test_tracking_error_evidence.py`，但该文件不存在。Implementation 未创建 dedicated evidence test 文件。

### 7. 越界检查

**PASS**

- 无 source code 变更。
- 无 test 变更。
- 无 README 变更。
- 无 golden answer 或 selected-fund data 变更。
- 无 production `tracking_error` golden rows 添加。
- 无 Dayu Host/Engine/tool loop、external runtime、LLM audit、Evidence Confirm、external index adapter 或 calculated tracking-error path 引入。
- 未读取或引用 `docs/design0522.md`、`docs/implementation-control0522.md`、`docs/repo-audit-20260521.md`。

## Findings

### F1 — Classification summary 表 class count 与 candidate 明细不一致（LOW）

**Severity**: LOW

**Evidence**: Classification summary 表显示 `not found: 1`，但 candidate 明细表有 12 行，每行均有明确 location（§2/§4/§5/page 6）。所有 12 个 candidate 均已分类为 `investment-objective target/limit` 或 `manager narrative`，不存在 "not found" 类别的 candidate。

**Impact**: 不影响 verdict 正确性（BLOCKED 结论不受 class count 影响），但 summary 表的计数可能误导 reviewer 认为存在一个无法分类的 candidate。

**Recommendation**: 如果 `not found: 1` 代表 "direct observed disclosure not found" 的元语义（而非第 13 个 candidate），应在表头或 footnote 明确说明。如果代表实际计数错误，应修正为与明细表一致。

**Reference**: Implementation artifact lines 86-94 (Classification summary) vs lines 72-84 (Candidate Classification table).

### F2 — Plan 列出的 dedicated evidence test 文件未创建（LOW）

**Severity**: LOW

**Evidence**: Plan section "Acceptance Tests / Validation Commands" 列出验证命令 `.venv/bin/python -m pytest tests/fund/test_tracking_error_evidence.py -q`，但该文件不存在。Implementation validation 仅运行 `test_performance.py`（14 passed），未创建 dedicated evidence classification 测试。

**Impact**: Plan 的 MiMo review F3 指出应覆盖 target/limit、benchmark-only、narrative-only、standard deviation、ambiguous、unparseable 和 anchor-incomplete 场景。当前 `test_performance.py` 的 14 个测试覆盖了部分场景，但 dedicated evidence test 文件的缺失意味着 plan 列出的 evidence-level failure 分类测试覆盖未被显式验证。

**Recommendation**: 不阻断当前 artifact 接受。若后续进入 golden gate 或 extractor fix 阶段，应补充 dedicated evidence classification 测试覆盖。

**Reference**: Plan lines 175-179 (Acceptance Tests) vs implementation Validation section line 128.

### F3 — `tracking_error_ambiguous` note 语义可更精确（INFO）

**Severity**: INFO

**Evidence**: `extract_performance(report).tracking_error` 返回 `note="tracking_error_ambiguous"`。代码层面，`_extract_tracking_error()` 首先调用 `_has_ambiguous_tracking_error_text(report)`，该函数检查 §3/§2 中是否存在同一行同时包含跟踪误差数值、目标控制语义和实际披露信号。对于 `001548`，所有 12 个 candidate 的拒绝原因均为 `_tracking_error_context_is_target_or_ambiguous()` 命中 `控制在`/`最小化` 等 negative keywords，而非真正的 "actual value 与 target limit 混杂在同行" 场景。

**Impact**: `tracking_error_ambiguous` 作为 note 在当前上下文中技术上正确（extractor 确实返回 missing），但可能让 reviewer 误以为存在真正的语义模糊（actual + target 混杂），而实际原因是所有 candidate 都是 target/limit 或 narrative。

**Recommendation**: 不阻断。当前 note 来自 extractor 内部逻辑，artifact 的 candidate classification 表已提供更精确的逐条拒绝理由，弥补了 note 的语义模糊。

**Reference**: Implementation artifact line 14 (`note="tracking_error_ambiguous"`) vs lines 72-84 (逐条分类理由)；`performance.py` lines 357-358, 517-542.

### F4 — Anchor appendix 数量与 candidate 明细不完全对应（INFO）

**Severity**: INFO

**Evidence**: Candidate Classification 表有 12 行，但 Anchor Appendix 表只有 8 行。差异原因是 anchor 按章节+行范围合并：§4 的 4 个 candidate 合并为 4 个 anchor entry（lines 85-87, 88-90, 92-93, 95-97），§2 的 3 个 candidate 合并为 2 个 anchor entry（lines 31-33, 56-58）。

**Impact**: 不影响 verdict 正确性。Anchor appendix 的合并是合理的（同一章节相邻行合并为一个可复核范围），但未在 artifact 中显式说明合并规则。

**Recommendation**: 不阻断。可在 anchor appendix 前增加一句说明：anchor 按章节+行范围合并，同一 anchor 可覆盖多个 candidate。

**Reference**: Implementation artifact lines 98-111 (Anchor Appendix) vs lines 72-84 (Candidate Classification).

## Non-blocking Observations

1. **Extractor 行为验证**：`performance.py` 的 `_extract_tracking_error()` 对 `001548` 返回 missing 是正确行为。12 个 candidate 全部包含 `_TRACKING_ERROR_NEGATIVE_KEYWORDS`（`控制在`、`最小化`等），`_tracking_error_context_is_target_or_ambiguous()` 正确排除它们。代码逻辑与 artifact 结论一致。

2. **FundDataExtractor 边界**：`data_extractor.py` 的 `_tracking_error_for_fund_type()` 对 `index_fund` 保留 tracking_error 字段（不裁剪为 not_applicable），`001548` 被识别为 `index_fund` 是正确的。

3. **Scope self-check 完整**：artifact 的 Scope Self-Check 列出 8 项非变更声明，全部与实际行为一致。

4. **Golden sequencing 遵守**：artifact 正确执行 "先 evidence artifact → 再 review → 再决定 golden gate" 顺序，`do_not_edit_golden` 是正确结论。

## Conclusion

P15-S1A implementation artifact 通过 code review。Verdict `BLOCKED_NO_DIRECT_DISCLOSURE_EVIDENCE` 正确，12 个 candidate 分类逻辑与代码实现一致，source contract 和 stop conditions 全部满足，FundDocumentRepository / FundDataExtractor 边界严格遵守，provenance 记录充分，`source_metadata=None` 被正确处理。4 个 findings 均为 LOW/INFO 级别，不阻断 artifact 接受。
