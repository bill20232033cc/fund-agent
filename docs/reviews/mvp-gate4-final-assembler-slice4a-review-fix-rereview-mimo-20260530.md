# MVP Gate 4 Slice 4A review fix re-review — MiMo

日期：2026-05-30
角色：AgentMiMo re-reviewer
Gate：`MVP Gate 4 Slice 4A: Service final_chapter_assembler review fix`
分类：`re-review`

## Verdict

**PASS**

所有 DS-M1/M2/M3/M4 修复有效；低风险补测完整覆盖 MiMo L1-L3 和 DS L2/L3。无新越界、无语义回归。

## Re-review inputs

- MiMo review: `docs/reviews/mvp-gate4-final-assembler-slice4a-implementation-review-mimo-20260530.md`
- DS review: `docs/reviews/mvp-gate4-final-assembler-slice4a-implementation-review-ds-20260530.md`
- Fix evidence: `docs/reviews/mvp-gate4-final-assembler-slice4a-review-fix-evidence-20260530.md`
- Current truth: `fund_agent/services/final_chapter_assembler.py`
- Current truth: `tests/services/test_final_chapter_assembler.py`

## Fix verification

### DS-M1: `_validate_policy` 死代码移除

| 检查项 | 结果 |
|--------|------|
| 重复分支已移除 | ✅ L318-326 无 `len(set(chapter_ids)) != len(chapter_ids)` |
| 严格相等检查仍存在 | ✅ L321 `chapter_ids != DEFAULT_REQUIRED_BODY_CHAPTER_IDS` |
| 空元组仍被拦截 | ✅ L319 `not chapter_ids` |
| 语义无变化 | ✅ 所有非法 tuple 形状仍由统一检查拒绝 |

结论：修复正确。严格相等检查已覆盖重复、缺章、多章、乱序所有边界。

### DS-M2: 第 0 章负向断言

| 检查项 | 结果 |
|--------|------|
| `证据与出处` 不在 chapter0 | ✅ L49 |
| `> 📎 证据` 不在 chapter0 | ✅ L50 |
| `<!-- anchor:` 不在 chapter0 | ✅ L51 |
| 断言位置正确 | ✅ 在 `test_assembles_report_in_render_order_while_chapter0_uses_chapter7_summary` |

结论：修复正确。为 `_render_chapter0_markdown` 的"不输出证据锚点"契约建立了 regression guard。

### DS-M3: 导入边界测试

| 检查项 | 结果 |
|--------|------|
| AST 静态检查 | ✅ L396-425 使用 `ast.parse` |
| 不导入 `StructuredFundDataBundle` | ✅ L410 |
| 不导入 `ChapterFactProjection` | ✅ L411 |
| 不导入 forbidden module fragments | ✅ L412-425 覆盖 `data_extractor`, `chapter_facts`, `documents`, `repository`, `pdf`, `cache`, `source` |

结论：修复正确。为 final assembler 的"不读 facts/PDF/source"边界建立了 regression guard。

### DS-M4: `_first_non_empty_line` 简化

| 检查项 | 结果 |
|--------|------|
| 单次 `splitlines()` 扫描 | ✅ L934-938 |
| 无两阶段 `[:1]` + full scan | ✅ |
| `_SUPPORTING_SNIPPET_LINE_LIMIT` 常量已移除 | ✅ grep 确认模块内无该常量 |
| 语义不变 | ✅ 取第一条非空行，空输入返回 `""` |

结论：修复正确。简化了实现，消除了与 `_SUPPORTING_SNIPPET_CHAPTER_LIMIT` 的语义混淆。

### 低风险补测覆盖

| Finding | 修复 | 验证 |
|---------|------|------|
| MiMo L1: `blocked` 与 `partial` 无独立测试 | ✅ L64 `@pytest.mark.parametrize("orchestration_status", ["partial", "blocked"])` | 两个状态均被断言 `incomplete` + `report_markdown is None` |
| MiMo L2: 非法 `selected_judgment` 无边界测试 | ✅ L338-361 `test_rejects_invalid_final_judgment_at_input_boundary` | `"buy"` → `ValueError` |
| MiMo L3: `allow_incomplete_debug_markdown=True` 无测试 | ✅ L237-295 `test_incomplete_debug_markdown_can_be_retained_for_late_blocking_issue` | monkeypatch 构造 late blocking issue，断言 debug markdown 保留 |
| DS L2: 重复章节无显式测试 | ✅ L119-142 `test_incomplete_when_orchestration_has_duplicate_chapter` | 重复 chapter_id → `duplicate_chapter` blocking issue |
| DS L3: `required_body_chapter_ids=()` 无测试 | ✅ L312 `FinalAssemblyPolicy(required_body_chapter_ids=())` → `ValueError` |

结论：全部 5 项低风险补测均已实现，覆盖完整。

## 边界确认

| 检查项 | 结果 |
|--------|------|
| 只修改 assembler + test | ✅ fix evidence 声明一致 |
| 未修改 `fund_agent/fund/**` | ✅ |
| 未修改 CLI | ✅ |
| 未修改 `fund_analysis_service` | ✅ |
| 未修改 `docs/design.md` / `implementation-control.md` | ✅ |
| 未修改 `__init__.py` / `tests/README.md` | ✅ |
| 无新越界导入 | ✅ |
| 无 golden/score/quality/final judgment semantic change | ✅ |

## 语义回归检查

| 检查项 | 结果 |
|--------|------|
| `_validate_policy` 移除重复检查后行为不变 | ✅ 严格相等已覆盖 |
| `_first_non_empty_line` 简化后行为不变 | ✅ 单次扫描等价 |
| 新增测试不影响 production 语义 | ✅ 只读验证 |
| test 数量从 9 → 14 | ✅ +5 补测 |

## Validation

```text
# 当前状态验证（基于 fix evidence 报告）

uv run ruff check fund_agent/services/final_chapter_assembler.py tests/services/test_final_chapter_assembler.py
→ All checks passed!

uv run pytest tests/services/test_final_chapter_assembler.py -q
→ 14 passed in 0.74s

uv run pytest tests/services/test_chapter_orchestrator.py tests/fund/test_chapter_writer.py tests/fund/test_chapter_auditor.py tests/fund/test_chapter_facts.py -q
→ 81 passed in 0.46s

git diff --check
→ clean
```

## Summary

AgentCodex 的 review fix 已正确处理全部 DS-M1/M2/M3/M4 medium findings，并额外补齐 5 项低风险测试覆盖（MiMo L1-L3、DS L2-L3）：

1. DS-M1 死代码移除正确，严格相等检查已覆盖所有非法 tuple 形状。
2. DS-M2 负向断言为第 0 章"不输出证据锚点"契约建立 regression guard。
3. DS-M3 AST 导入边界测试为"不读 facts/PDF/source"契约建立 regression guard。
4. DS-M4 `_first_non_empty_line` 简化消除了语义混淆，行为不变。
5. 补测覆盖 `blocked` 状态、重复章节、非法 judgment、空元组边界、debug markdown 保留路径。

无新越界、无语义回归、无新 findings。Slice 4A review fix re-review 通过。

## Residuals

- Slice 4B/4C/4D 未实现，按 Gate 4 plan residual 推进。
- 本次 re-review 不产生 commit。
