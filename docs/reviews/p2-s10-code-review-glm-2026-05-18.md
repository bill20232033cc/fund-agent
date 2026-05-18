# P2-S10 Code Review

- **Gate**: P2-S10 code review
- **Date**: 2026-05-18
- **Reviewer**: AgentGLM
- **Design source**: `docs/design.md` §5.4 证据锚点格式
- **Control source**: `docs/implementation-control.md` P2-S10
- **Implementation artifact**: `docs/reviews/p2-s10-implementation-2026-05-18.md`

## Conclusion

**PASS** — 无阻塞问题。实现与设计 §5.4 证据锚点格式完全对齐，AGENTS 约束全部满足，63 项测试通过，Capability 边界未被穿透。

## Findings

### F1. 正文证据锚点包含年份、章节和描述 — ✅ 符合

`renderer.py:447-467` `_body_anchor_reference()` 对年报来源输出 `年报{year}§{section}{page_part} {description}`。
年份取 `anchor.document_year`，缺失时显式降级为 `"未知年份"`（行 463），不静默省略。
描述优先取 `row_locator`，其次 `note`，兜底 `"结构化字段"`（行 609）。

测试覆盖：`test_renderer.py:533-549` 验证 `年报2024§1 §1: fixture` 存在且 `年报§1`（无年份）不存在。

### F2. 附录年报锚点保留年份、章节、表格、行、页码，缺失时显式降级 — ✅ 符合

`renderer.py:470-491` `_anchor_reference()` 对年报来源输出 `年报{year}§{section}表{table_id}行{row_locator}{page_part}{note_part}`。
格式与设计 §5.4 `年报{年份}§{章节}表{编号}行{行号}` 一致。
缺表格或行时降级为 `"未定位"`（行 487-488），不静默跳过。

测试覆盖：
- `test_renderer.py:552-568` 验证附录精确输出 `年报2024§8表T1行industry_distribution`
- `test_renderer.py:571-586` 验证缺行定位时输出 `年报2024§1表未定位行未定位`，年份和章节不丢失
- `test_renderer.py:589-609` 验证页码作为 `（第18页）` 保留在正文和附录中

### F3. 非年报来源显式标注来源类型，不伪装成年报 — ✅ 符合

`renderer.py:46-49` `_SOURCE_KIND_LABELS` 为 `external_api` 和 `derived` 各提供显式标签。
`renderer.py:494-511` `_non_annual_anchor_reference()` 输出格式为 `{source_label}{location}{page_part}{note_part}`，
永远不会以 `"年报"` 开头。
`renderer.py:535-548` `_source_kind_label()` 对未知 source_kind 输出 `未知来源({source_kind})`，不回退到年报格式。

测试覆盖：`test_renderer.py:612-639` 验证 `external_api` 来源输出 `外部数据(external_api)§nav_return行2024-12-31（第1页）` 且不含 `年报2024§nav_return`。

### F4. 缺证章节在正文和附录都显式输出 — ✅ 符合

正文：`renderer.py:442-443` 当章节无锚点时输出 `> 📎 证据：数据不足，当前章节未携带证据锚点`。
附录：`renderer.py:514-532` `_missing_anchor_reference()` 输出 `年报{year}§未定位表未定位行未定位：数据不足，模板第{idx}章《{title}》当前输入未携带证据锚点。`。
章节分组由 `_collect_chapter_evidence_groups()` 驱动（行 668-697），与 8 个章节渲染函数一一对应。

测试覆盖：`test_renderer.py:642-662` 构造空 `rabc_attributions` 路径，验证正文含 `数据不足，当前章节未携带证据锚点`，附录含 `[M2]` 条目并引用模板第 2 章标题。

### F5. run_programmatic_audit 兼容性保持 — ✅ 符合

`renderer.py:126-135` `render_template_report()` 返回 `TemplateRenderResult`，其中 `audit_input` 直接构造 `ProgrammaticAuditInput`，携带 `report_markdown`、`rabc_attributions`、`checklist_result`、`final_judgment`。
`renderer.py:138-151` `build_programmatic_audit_input()` 可从渲染结果提取审计输入。

测试覆盖：
- `test_renderer.py:708-728` 验证渲染结果通过完整 P1/P2/P3/L1/R1/R2 审计
- `test_renderer.py:731-749` 验证缺失数据路径仍兼容审计且通过
- `test_renderer.py:790-811` 验证 L1/R1/R2 所需结构化输入由渲染结果原样携带，未被模板改写

### F6. Capability 边界未被穿透 — ✅ 符合

`renderer.py` 导入清单（行 15-23）全部来自 Capability 层内部：
- `fund_agent.fund.analysis.*` — Capability 内部分析模块
- `fund_agent.fund.audit` — Capability 审计
- `fund_agent.fund.data_extractor` — Capability façade
- `fund_agent.fund.extractors.models` — Capability 数据模型

无 repository、file system、PDF、UI、Service、Engine 导入。

### F7. AGENTS 约定检查 — ✅ 符合

| 约定 | 状态 | 证据 |
|------|------|------|
| 中文 docstring | ✅ | 所有函数均有中文 docstring，含 Args/Returns/Raises |
| 模板章节引用 | ✅ | 模块 docstring 引用"第 3.1 节 8 章模板"；各 `_render_chapter_*` 与 8 章一一对应 |
| 证据可溯源 | ✅ | 每章输出 `> 📎 证据：...` 行，附录汇总全部锚点 |
| 禁止买卖措辞 | ✅ | `_validate_report_wording()` 拦截"买入""卖出""仓位比例""收益预测"（行 960-975）；`_validate_final_judgment()` 只允许 3 类判断（行 943-957） |
| 不预测未来收益 | ✅ | 第 7 章固定文本"不预测未来收益，不给出交易或配置指令"（行 390） |

### F8. README 同步 — ✅ 符合

`fund_agent/fund/README.md:219` `template/` 分层条目已更新为当前实现描述。
`tests/README.md:23` 模板渲染器测试条目已更新，覆盖证据锚点格式、缺证章节、页码保留、非年报来源、审计兼容和禁用措辞。

测试覆盖：`test_renderer.py:685-705` 验证 README 不含过期条目且当前条目恰好出现一次。

## Validation Run

```
tests/fund/template tests/fund/audit — 23 passed in 0.50s
tests/fund/analysis — 40 passed in 0.41s
Total: 63 passed, 0 failed
```

## Non-blocking Observations

1. **正文只展示首个锚点**：`_evidence_line()` 行 444 只取 `anchors[0]`。当章节有多个锚点时，正文只展示一个代表性引用，附录展示全部。这是合理的可读性折中，不影响可审计性。

2. **禁用词 substring 匹配**：`_validate_report_wording()` 使用 substring 检测，若模板未来引入"买入前检查清单"等合法短语会误报。已在 implementation-control.md 残余风险中记录。

3. **缺证粒度为章节级**：缺证附录条目按章输出，不细到字段级。已在实现文档残余风险中记录，属于后续审计/确认关注点。

4. **非年报来源位置文本**：`_non_annual_location_text()` 对非年报锚点拼装可用位置信息（年份、章节、表格、行），全部缺失时输出 `位置未定位`。当前测试覆盖了 `external_api` 路径；`derived` 路径格式相同，无需单独测试。
