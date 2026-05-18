# P2-S9 Code Review — Template Renderer

## Gate

- 当前 gate：P2-S9 code review
- 执行角色：AgentMiMo，独立 review worker
- 停止边界：review only，不编辑文件、不提交、不推送、不创建 PR

## Conclusion

**No blocking issues. PASS.**

模板渲染器实现完整、边界清晰，与设计文档和审计输入契约一致。7 个测试覆盖正常路径、缺失数据路径、审计兼容性、禁用措辞校验和结构化输入保持，均为有意义的功能测试而非纯字符串 smoke test。

## Review Targets

| 文件 | 状态 |
|------|------|
| `fund_agent/fund/template/renderer.py` | PASS |
| `fund_agent/fund/template/__init__.py` | PASS |
| `tests/fund/template/test_renderer.py` | PASS |
| `fund_agent/fund/README.md` | PASS |

## Findings

### 无阻断项

### Info 级

#### I-1: 章节标题与审计子串匹配设计

`renderer.py:26-35` 定义了带修饰语的章节标题（如 `"R=A+B-C 收益归因"`），审计模块 `audit_programmatic.py:26-35` 使用较短的子串标题（如 `"R=A+B-C"`）。审计通过 `required_title in heading` 子串匹配（`audit_programmatic.py:397`），因此较长标题可以正确匹配。设计意图一致：审计要求子串存在即可，渲染器保留完整语义。**无需修改。**

#### I-2: 第 5 章"当前阶段"消费范围有限

`renderer.py:308-330` 第 5 章当前只消费显式 `current_stage` 字符串和 `nav_data.records` 条数。跨期年报对比结论硬编码为"数据不足"。这与 implementation artifact 的 residual risk 一致，是当前 MVP 的已知范围限制。**无需修改，后续 slice 补充。**

#### I-3: `_join_values` 对非 tuple/list/set 类型走 `str(values)` fallback

`renderer.py:731` 当 `values` 不是 `None/str/tuple/list/set` 时直接 `str(values)`。当前调用方传入的都是 `tuple[str, ...]` 或 `None`，不会命中此分支。**无实际风险。**

## Scope & Boundary Verification

| 检查项 | 结果 | 说明 |
|--------|------|------|
| 8 章结构完整 | PASS | `renderer.py:105-115` 固定渲染 0-7 章 + 证据附录 |
| 章节标题匹配设计文档 §3.1 | PASS | 与 `docs/design.md:82-91` 一致 |
| 只消费 P1/P2 结构化结果 | PASS | 不读取年报、PDF、缓存或文档仓库 |
| 无 UI/Service/Engine/文档仓库访问 | PASS | 仅 import analysis/audit/data 层 |
| final_judgment 只允许三类 | PASS | `renderer.py:24` Literal 约束 + `renderer.py:734-748` 运行时校验 |
| 禁用交易建议措辞 | PASS | `renderer.py:41` 定义禁用词 + `renderer.py:751-766` 运行时校验 |
| 缺失数据显式标注 | PASS | "未披露"/"数据不足"贯穿全文 |
| 证据锚点渲染 | PASS | 章节内 `> 📎 证据：年报§...` + 附录 `## 证据与出处` |
| audit_input 可直接传给 run_programmatic_audit | PASS | `ProgrammaticAuditInput` 4 字段（report_markdown, rabc_attributions, checklist_result, final_judgment）完全匹配 |
| P1/P2/P3/L1/R1/R2 审计通过 | PASS | 测试 `test_render_template_report_builds_audit_input_that_passes_p1_p2_p3_l1_r1_r2` 验证 |
| 缺失数据路径审计兼容 | PASS | 测试 `test_render_template_report_missing_data_path_is_explicit_and_audit_compatible` 验证 |

## Test Quality Assessment

| 测试 | 类型 | 质量 |
|------|------|------|
| `test_render_template_report_contains_exact_eight_design_chapters` | 结构验证 | 有意义：验证 8 章标题和顺序 |
| `test_render_template_report_formats_evidence_anchors_with_year_section_and_optional_row` | 证据格式 | 有意义：验证锚点格式和可选行定位 |
| `test_render_template_report_builds_audit_input_that_passes_p1_p2_p3_l1_r1_r2` | 端到端 | 有意义：渲染→审计全链路 |
| `test_render_template_report_missing_data_path_is_explicit_and_audit_compatible` | 缺失路径 | 有意义：验证缺失不被静默省略 |
| `test_render_template_report_rejects_unsafe_final_judgment_wording` | 边界校验 | 有意义：验证非法判断被拒绝 |
| `test_render_template_report_does_not_emit_buy_sell_wording` | 安全校验 | 有意义：验证禁用措辞 |
| `test_render_template_report_keeps_l1_r1_r2_structured_inputs_unmodified` | 不变量 | 有意义：验证结构化输入不被改写 |

**总结：7 个测试均为有意义的功能测试，覆盖正常路径、异常路径、安全约束和审计兼容性。**

## README 同步验证

`fund_agent/fund/README.md` 已更新：
- 新增 `render_template_report()` 和 `TemplateRenderInput`/`TemplateRenderResult` 的 API 说明
- 新增模板渲染器边界说明（MVP 填充、不调用 LLM、不预测收益）
- 新增 `template/` 目录在内部分层中的定位
- 新增当前边界中模板渲染器条目

**README 与代码实现一致。**

## Validation Run

```
.venv/bin/python -m pytest tests/fund/template tests/fund/audit -q
# Result: 16 passed in 0.83s
```

## Residual Risks

1. 第 5 章跨期年报对比仍为"数据不足"，需后续 slice 提供多期结构化输入。
2. 证据锚点精确度受上游 P1 extractor 的 `row_locator` 完整性影响；部分锚点缺少行定位时退化为章节级引用。
