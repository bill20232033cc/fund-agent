# P2 Aggregate Deep Review — AgentMiMo

> **日期**: 2026-05-18
> **基线**: `a6b1516` (P2-S1 through P2-S8 accepted baseline)
> **审查范围**: `a6b1516...HEAD` (P2-S9 template renderer + P2-S10 evidence anchor labeling)
> **结论**: **PASS**

---

## 1. Validation Summary

| 检查维度 | 结果 | 说明 |
|----------|------|------|
| 测试通过 | PASS | 63 passed in 0.73s (`tests/fund/template` + `tests/fund/audit` + `tests/fund/analysis`) |
| 跨 slice 兼容 | PASS | S9 renderer 输出的 `ProgrammaticAuditInput` 与 S8 audit 消费接口完全匹配 |
| 边界约束 | PASS | template 只消费 Capability 层结构化结果，无 repository/PDF/filesystem/UI/Service/Engine/Runtime 访问 |
| 证据可追溯 | PASS | 正文和附录锚点格式规范，缺失证据显式标注，R=A+B-C 输入不被掩盖 |
| 最终判断措辞 | PASS | 只允许 `worth_holding / needs_attention / suggest_replace`，禁用词运行时校验 |
| 文档/总控一致性 | PASS | implementation-control 当前 gate、artifact 和下一 entry point 连贯 |
| 过度耦合/未来泄漏 | PASS | 无 P3 功能泄漏，无未来 slice 预留代码 |

---

## 2. Cross-Slice Correctness (S8 audit + S9 renderer + S10 evidence)

### 2.1 renderer → audit 接口兼容

`render_template_report()` 返回 `TemplateRenderResult.audit_input`，类型为 `ProgrammaticAuditInput`。`build_programmatic_audit_input()` 是纯透传（`renderer.py:151`）。审计消费的 4 个字段 (`report_markdown`, `rabc_attributions`, `checklist_result`, `final_judgment`) 均由 renderer 在 `renderer.py:128-133` 正确组装。

测试 `test_render_template_report_builds_audit_input_that_passes_p1_p2_p3_l1_r1_r2` (`test_renderer.py:708-728`) 验证了端到端：renderer 输出 → audit 输入 → 6 条规则全部通过。

测试 `test_render_template_report_keeps_l1_r1_r2_structured_inputs_unmodified` (`test_renderer.py:790-811`) 验证了结构化输入不被 renderer 篡改。

### 2.2 证据锚点跨层传递

S10 的证据标注完全在 renderer 内完成，不改变 `ProgrammaticAuditInput` 的结构化字段。审计通过正则 `_EVIDENCE_MARKER_PATTERN`（匹配 `📎 证据`、`证据与出处`、`年报\d{4}§`）检测报告中的证据标记（`audit_programmatic.py:24`）。renderer 在每个章节末尾输出 `> 📎 证据：...` 并在附录输出 `## 证据与出处`，P3 审计可正确命中。

### 2.3 章节标题对齐

审计的 `_REQUIRED_CHAPTER_TITLES`（`audit_programmatic.py:26-35`）使用子串匹配（`required_title in heading`）。renderer 的 `_CHAPTER_TITLES`（`renderer.py:27-36`）每个标题都包含审计所需的子串。已验证无遗漏。

---

## 3. Boundary Compliance

renderer.py 的导入范围（`renderer.py:15-23`）：
- `fund_agent.fund.analysis.*` — Capability 层分析模块
- `fund_agent.fund.audit` — Capability 层审计模块
- `fund_agent.fund.data_extractor` — Capability 层数据包
- `fund_agent.fund.extractors.models` — Capability 层模型

无 `documents`、`pdf`、`data`、`ui`、`services`、`engine`、`runtime` 导入。renderer 不读文件、不访问网络、不写缓存。

---

## 4. Evidence Traceability

### 4.1 正文证据行格式

`_evidence_line()` (`renderer.py:429-444`) 输出统一格式 `> 📎 证据：{描述}`。年报来源包含年份和章节（`renderer.py:463-464`），非年报来源显式标注来源类型（`renderer.py:465-467`）。缺少锚点时输出"数据不足"（`renderer.py:443`）。

### 4.2 附录证据格式

`_anchor_reference()` (`renderer.py:470-491`) 按 `年报{年份}§{章节}表{编号}行{行号}` 输出。表格/行定位缺失时降级为"未定位"，不丢年份或章节。页码作为附加元数据保留。非年报来源通过 `_non_annual_anchor_reference()` (`renderer.py:494-511`) 显式标注。

### 4.3 缺证章节标注

`_render_evidence_section()` (`renderer.py:400-426`) 对每个章节检查锚点分组，缺证章节输出 `[M{n}]` 条目。`_collect_chapter_evidence_groups()` (`renderer.py:668-697`) 按 8 章分组收集，与 `_CHAPTER_TITLES` 一一对应。

### 4.4 R=A+B-C 输入不被掩盖

renderer 只消费 `RabcAttribution` 结构化结果，不修改、不估算、不填充缺失值。`status="missing"` 时渲染为"数据不足"（`renderer.py:248`）。审计 L1 规则只检查 `status="computed"` 的闭合性（`audit_programmatic.py:238-239`）。

---

## 5. Final Judgment Wording Safety

- `TemplateFinalJudgment` 类型别名限定为 `Literal["worth_holding", "needs_attention", "suggest_replace"]`（`renderer.py:25`）
- `_validate_final_judgment()`（`renderer.py:943-957`）在渲染前校验
- `_validate_report_wording()`（`renderer.py:960-975`）在渲染后扫描禁用词：`买入`、`卖出`、`仓位比例`、`收益预测`
- 测试 `test_render_template_report_rejects_unsafe_final_judgment_wording`（`test_renderer.py:753-767`）验证非法值抛出 `ValueError`
- 测试 `test_render_template_report_does_not_emit_buy_sell_wording`（`test_renderer.py:770-787`）验证禁用词不出现在报告中

---

## 6. Test Coverage Assessment

| 测试文件 | 用例数 | 覆盖要点 |
|----------|--------|----------|
| `tests/fund/template/test_renderer.py` | 14 | 8 章结构、正文/附录证据格式、缺证章节、页码、非年报来源、审计兼容、缺失数据、最终判断边界、禁用措辞、README 同步 |
| `tests/fund/audit/test_audit_programmatic.py` | (P2-S8 已接受) | P1/P2/P3/L1/R1/R2 规则、必需输入缺失、注入错误 |
| `tests/fund/analysis/` | 40 | R=A+B-C、alpha、一致性、投资者获得感、风险检查、检查清单 |

关键跨层测试：`test_render_template_report_builds_audit_input_that_passes_p1_p2_p3_l1_r1_r2` 验证 renderer 输出可直接通过全部 6 条审计规则。

---

## 7. Docs/Control Coherence

- `docs/implementation-control.md` 当前 gate 已更新为 `P2 aggregate deepreview`（正确）
- P2-S9 和 P2-S10 的完成记录完整，包含验证命令和通过计数
- 下一 entry point 指向 P2 aggregate deepreview 本身（当前正在执行）
- `fund_agent/fund/README.md` 已包含 `template/` 分层说明和 `render_template_report()` 契约
- `tests/README.md` 已包含 `tests/fund/template/test_renderer.py` 的覆盖说明

---

## 8. Findings

### 8.1 Observations (non-blocking)

| # | 严重度 | 文件 | 行 | 说明 |
|---|--------|------|----|------|
| O1 | info | `renderer.py` | 975 | `_validate_report_wording` 中 f-string `{'、'.join(forbidden_hits)}` 可能触发 Pyright 对 `tuple[str, ...]` join 的类型推断窄化警告，但运行时正确 |
| O2 | info | `renderer.py` | 277 | `manager_alignment.values()` 输出顺序依赖 dict 插入顺序（Python 3.7+ 保证），非问题但值得知晓 |

无 blocker、无 reviewable finding。

---

## 9. Residual Risks

1. **P3 泄漏风险低**：renderer 不导入任何 P3 模块，不预留扩展点。后续 P3 场景需修改 renderer 时应重新审查边界。
2. **审计正则脆弱性**：`_EVIDENCE_MARKER_PATTERN` 使用硬编码中文关键词。当前 renderer 输出格式稳定匹配；若后续 renderer 证据行措辞变更，需同步更新正则。
3. **章节标题子串匹配**：审计用 `required_title in heading` 做子串匹配。当前 renderer 标题完整包含审计子串；若后续标题措辞调整需验证不破坏匹配。

---

## 10. Conclusion

**PASS**。P2-S9 模板渲染器与 P2-S10 证据锚点标注与 P2-S8 程序审计在跨 slice 接口、边界约束、证据可追溯性和措辞安全性上完全兼容。63 项测试全部通过。无阻断或需复核的 finding。P2 aggregate 可进入下一 gate。
