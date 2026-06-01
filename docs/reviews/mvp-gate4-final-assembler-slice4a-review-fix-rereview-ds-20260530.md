# MVP Gate 4 Slice 4A review fix re-review — AgentDS

日期：2026-05-30
角色：AgentDS re-reviewer
Gate：`MVP Gate 4 Slice 4A: Service final_chapter_assembler review fix re-review`
状态：不改代码、不 commit。

## Verdict

**PASS**

DS-M1/M2/M3/M4 全部有效修复，低风险补测正确，无新越界，无语义回归。

## Review inputs

- DS review: `docs/reviews/mvp-gate4-final-assembler-slice4a-implementation-review-ds-20260530.md`
- MiMo review: `docs/reviews/mvp-gate4-final-assembler-slice4a-implementation-review-mimo-20260530.md`
- Fix evidence: `docs/reviews/mvp-gate4-final-assembler-slice4a-review-fix-evidence-20260530.md`
- Current code: `fund_agent/services/final_chapter_assembler.py`, `tests/services/test_final_chapter_assembler.py`

## Fix verification

### DS-M1 — dead code removal ✅

旧代码 `_validate_policy` 中 `len(set(chapter_ids)) != len(chapter_ids)` 重复检查已移除。当前 `_validate_policy` (L318-326) 仅保留空检查 → 严格相等检查 → include_chapter7 → max_chars 四条独立守卫。严格相等 `(1,2,3,4,5,6)` 已隐含拒绝重复、缺章、多章、乱序。不再有不可达分支误导 reader。

### DS-M2 — chapter 0 负向断言 ✅

`test_assembles_report_in_render_order_while_chapter0_uses_chapter7_summary` (L49-51) 新增三条负向断言：
- `assert "证据与出处" not in result.chapter0_markdown`
- `assert "> 📎 证据" not in result.chapter0_markdown`
- `assert "<!-- anchor:" not in result.chapter0_markdown`

精确覆盖 plan §4.4 禁止第 0 章输出证据/锚点的要求，提供 regression guard。

### DS-M3 — 导入边界静态检查 ✅

新增 `test_final_assembler_imports_stay_above_fact_and_source_boundaries` (L383-425)，通过 AST 遍历确认：
- 不导入 `StructuredFundDataBundle`、`ChapterFactProjection`
- 不导入 `data_extractor` / `chapter_facts` / `documents` / `repository` / `pdf` / `cache` / `source` 模块片段

覆盖 plan §4.3 禁止 assembler 接触事实投影和来源仓库的要求。AST 检查比 `dir()` 更可靠，不依赖模块是否已导入。

### DS-M4 — `_first_non_empty_line` 单次扫描 ✅

函数 (L921-938) 已改为单次 `splitlines()` 循环，移除旧的两阶段 `[:1]` + 完整扫描实现。同时移除了已无用途的 `_SUPPORTING_SNIPPET_LINE_LIMIT` 常量，现有 `_SUPPORTING_SNIPPET_CHAPTER_LIMIT=3` 仅用于章节级短句数量控制 (L560)。

行为等价性验证：
- 旧：先查第一行，空则全扫描 → 返回第一条非空行
- 新：直接全扫描 → 返回第一条非空行
- 对空字符串、纯空行、正常文本均等价。无语义偏离。

## Low finding coverage verification

| 来源 | 编号 | 补测 | 状态 |
|------|------|------|------|
| MiMo | L1 | `status="blocked"` 参数化 (L64-86) | ✅ 与 `partial` 共用 `test_incomplete_when_orchestration_not_accepted`，确认为 fail-closed |
| MiMo | L2 | `selected_judgment="buy"` → ValueError (L338-361) | ✅ 覆盖 `get_args(FinalJudgment)` 校验边界 |
| MiMo | L3 | `allow_incomplete_debug_markdown=True` 分支 (L237-295) | ✅ monkeypatch 构造 late blocking chapter0 issue，断言 debug markdown 保留 |
| DS | L1 | 同 MiMo L1 | ✅ |
| DS | L2 | 重复章节 blocking issue (L119-142) | ✅ 构造 `orchestration.chapter_results[0]` 重复，断言 `duplicate_chapter` |
| DS | L3 | `required_body_chapter_ids=()` → ValueError (L312) | ✅ 已并入 `test_policy_rejects_chapter0_lens_style_reconfiguration` |

## Boundary re-check

| 检查项 | 结果 |
|--------|------|
| 未修改 `fund_agent/fund/**` | ✅ |
| 未修改 CLI | ✅ |
| 未修改 `fund_analysis_service.py` | ✅ |
| 未修改 `design.md` / `implementation-control.md` | ✅ |
| 未引入 dayu/extra_payload/provider SDK | ✅ |
| 未修改 `FinalJudgmentDecision` 或 `derive_final_judgment()` | ✅ |
| 未读取 PDF/cache/source helper/repository | ✅ |
| M4 简化未改变 `_first_non_empty_line` 语义 | ✅ |
| 删除 `_SUPPORTING_SNIPPET_LINE_LIMIT` 无残留引用 | ✅ grep 确认仅 `_SUPPORTING_SNIPPET_CHAPTER_LIMIT` 存在 |
| monkeypatch 测试不泄漏到其他 test case | ✅ 函数作用域 fixture，无模块级 patch |

## Semantic regression check

- **M1**：删除不可达分支，严格相等守卫行为不变。重复/缺章/乱序仍被 `ValueError` 拒绝。
- **M2**：纯测试补充，production 代码无变化。
- **M3**：纯测试补充，production 代码无变化。
- **M4**：`_first_non_empty_line` 从两阶段改为单阶段，等价变换。调用方 (`_supporting_conclusion_snippets`、`_chapter0_source_issues`、`_cover_value`、`_conclusion_line_for_chapter`) 语义不变。`_SUPPORTING_SNIPPET_LINE_LIMIT` 仅被旧版 `_first_non_empty_line` 使用，删除无影响。
- 低风险补测全为新增测试，不改变 production 路径。

## Validation

```text
uv run ruff check → All checks passed!
uv run pytest tests/services/test_final_chapter_assembler.py -q → 14 passed in 0.84s
uv run pytest Gate 1-3 regression → 81 passed in 0.47s
```

## Residuals

- Slice 4B/4C/4D 未实现，仍属 Gate 4 plan residual。
- 未提交 commit。
