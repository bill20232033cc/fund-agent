# P6 Aggregate Deepreview — Template Contract Hardening

## Scope

- Mode: current changes (committed P6-S1 through P6-S5 on `main`)
- Branch: main
- Base: post-P5 baseline `d33b901fd1bee9f85206df461cc6419a813bcbae` through HEAD `a993739`
- Output file: `docs/reviews/p6-aggregate-deepreview-mimo-20260520.md`
- Included scope: P6 template contract hardening — 5 accepted slices
  - P6-S1: `fund_agent/fund/template/contracts.py` (934 lines, new), `tests/fund/template/test_contracts.py`
  - P6-S2: `fund_agent/fund/template/renderer.py` (modified), `fund_agent/fund/template/__init__.py` (modified)
  - P6-S3: `fund_agent/fund/template/chapter_blocks.py` (226 lines, new), `fund_agent/fund/audit/audit_programmatic.py` (modified), `fund_agent/fund/audit/contract_rules.py` (219 lines, new), `tests/fund/audit/test_audit_programmatic.py`
  - P6-S4: `fund_agent/fund/template/item_rules.py` (569 lines, new), `tests/fund/template/test_item_rules.py`
  - P6-S5: `fund_agent/fund/quality_gate.py` (modified), `fund_agent/fund/extraction_score.py` (modified), `tests/fund/test_quality_gate.py`, `tests/fund/test_extraction_score.py`
- Excluded scope: Service layer, Engine, UI, CLI behavior, fund document PDF/cache access, LLM audit, Evidence Confirm
- Parallel review coverage: 3 subagents (contracts/chapter_blocks/renderer, audit/quality_gate/extraction_score, item_rules/__init__)

## Findings

### 1-未修复-低-`"## 证据与出处"` 硬编码三处不同步风险

- **入口/函数**: `_render_evidence_section` / `_audit_minimum_chapter_evidence` / `_EVIDENCE_APPENDIX_HEADING`
- **文件(行号)**: `renderer.py:467`, `audit_programmatic.py:288`, `chapter_blocks.py:18`
- **输入场景**: 任何涉及证据附录标题的渲染或审计路径
- **实际分支**: renderer 在 line 467 内联硬编码 `"## 证据与出处"`；audit 在 line 288 内联硬编码同一字符串；`chapter_blocks.py` 在 line 18 定义了 `_EVIDENCE_APPENDIX_HEADING` 常量但 renderer 和 audit 均未引用
- **预期行为**: 三个位置应共享同一常量，标题变更时只需改一处
- **实际行为**: 三处独立维护同一字符串，变更时必须手动同步
- **直接证据**: `renderer.py:467` — `lines = ["## 证据与出处"]`；`audit_programmatic.py:288` — `if "## 证据与出处" in block.body_markdown`；`chapter_blocks.py:18` — `_EVIDENCE_APPENDIX_HEADING: Final[str] = "## 证据与出处"`
- **影响**: 维护性风险。标题文本变更时如果只改一处会导致审计与渲染不一致，但当前文本未变，无运行时错误
- **建议改法和验证点**: renderer 和 audit 应 `from chapter_blocks import _EVIDENCE_APPENDIX_HEADING` 或将常量提升到 `contracts.py` 公共层。验证：grep 确认全仓只有一处定义
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

### 2-未修复-低-`run_programmatic_audit` docstring 遗漏 C2

- **入口/函数**: `run_programmatic_audit`
- **文件(行号)**: `audit_programmatic.py:102`
- **输入场景**: 代码阅读
- **实际分支**: docstring 写 "执行 P1/P2/P3/L1/R1/R2 程序审计"
- **预期行为**: 应包含 C2，与 `_CHECKED_RULES` (line 37: `"P1", "P2", "P3", "C2", "L1", "R1", "R2"`) 一致
- **实际行为**: docstring 遗漏 C2
- **直接证据**: line 102 docstring vs line 37 `_CHECKED_RULES`
- **影响**: 文档漂移，不影响运行时
- **建议改法和验证点**: 更新 docstring 为 "执行 P1/P2/P3/C2/L1/R1/R2 程序审计"
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

### 3-未修复-低-`extraction_score._derive_contract_applicability` 使用 `locals()` 守卫循环变量

- **入口/函数**: `_derive_contract_applicability`
- **文件(行号)**: `extraction_score.py:1379-1381`
- **输入场景**: `resolve_preferred_lens` 在首次迭代时抛出 `ValueError`
- **实际分支**: `except ValueError` 块中使用 `if "chapter" in locals()` 判断循环变量是否存在
- **预期行为**: 循环变量应在 try 块外预先绑定，避免依赖 `locals()` 反射
- **实际行为**: 如果首次迭代 `resolve_preferred_lens` 抛异常，`chapter` 未赋值，`locals()` 检查防止 `NameError`。逻辑正确但脆弱
- **直接证据**: line 1379-1381 — `except ValueError as exc: if "chapter" in locals(): unresolved_chapter_ids.append(chapter.chapter_id)`
- **影响**: 可维护性。当前逻辑正确，但 `locals()` 模式在重构时容易引入 bug
- **建议改法和验证点**: 在 for 循环体内第一行赋值 `current_chapter = chapter`，except 块改用 `current_chapter`。或改用 `enumerate` + 提前 `break`
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

### 4-未修复-低-`unresolved_chapter_ids` 语义不精确：只记录首个失败章节

- **入口/函数**: `_derive_contract_applicability`
- **文件(行号)**: `extraction_score.py:1379-1389`
- **输入场景**: 某章 `resolve_preferred_lens` 抛出 `ValueError`
- **实际分支**: except 块在 line 1382 直接 `return`，只记录当前失败章节，后续章节未被尝试
- **预期行为**: 要么尝试全部章节后汇总所有失败 ID，要么字段名改为 `failed_chapter_id`
- **实际行为**: `unresolved_chapter_ids` 名称暗示"所有未解析章节"，实际只含首个失败
- **直接证据**: line 1382 — `return _contract_applicability_result(...)` 在 except 块中立即返回
- **影响**: 语义混淆。消费方可能误以为 `unresolved_chapter_ids` 包含全部失败章节。当前消费方（quality_gate.py）只检查 status，不依赖 ID 列表长度，影响有限
- **建议改法和验证点**: 改名为 `failed_chapter_ids` 或在 except 中 `continue` 而非 `return`，遍历完全部章节后汇总
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

## Open Questions

- 无。

## Residual Risk

### 设计层面（非 defect，但值得记录）

1. **preferred_lens 不完整**: `contracts.py` 中 chapters 4 和 5 缺少 `enhanced_index`、`qdii_fund`、`fof_fund` 的 lens 条目，fallback 到 `"default"`。验证器接受此行为（因为有 default），但 3/6 基金类型在这两章获得的是通用指导而非定制化指导。这是内容完善问题，不是代码 defect。

2. **禁止标记粒度**: `contract_rules.py` 中部分 forbidden markers 使用短子串（如 `"性格"`、`"人品"`、`"动机"`），可能在合法讨论中产生误报。这是确定性 vs 精度的已知 trade-off，模块 docstring 已声明。

3. **renderer `_FORBIDDEN_TERMS` 与 C2 forbidden rules 分层**: renderer 只检查 4 个禁止词（`买入`、`卖出`、`仓位比例`、`收益预测`），C2 审计规则覆盖更广的 `must_not_cover` 条目。两层独立运作，不是 gap，但耦合度低。

4. **FQ5 与 FQ1 独立性**: FQ5 检查 `preferred_lens_status == "mismatch"`，FQ1 检查 `app_category_status == "conflict"`。两者独立不交叉验证。如果 `app_category_status == "conflict"` 但 `preferred_lens_status == "resolved"`，FQ5 不会标记。这是独立规则设计，不是 bug。

### 测试覆盖

- 246/246 全量测试通过
- ruff clean
- P6-S1: `test_contracts.py` 覆盖 8 章契约完整性、lens 映射、fail-closed 校验
- P6-S2: `test_renderer.py` 覆盖 chapter_blocks 输出、contract heading 对齐
- P6-S3: `test_audit_programmatic.py` 覆盖 C2/P3 审计规则、fallback 切分、forbidden markers
- P6-S4: `test_item_rules.py` 覆盖 4 条 conditional 规则、facet 冲突 fail-closed、segment markers
- P6-S5: `test_quality_gate.py` 覆盖 FQ5 mismatch 阻断、`test_extraction_score.py` 覆盖 contract applicability

### 未覆盖区域

- renderer 条件段落渲染（ITEM_RULE triggered sections）尚未实现 — 未来 slice
- LLM 审计 E1/E2/E3/C1/C2 — v2 scope
- Evidence Confirm 项级证据确认 — v2 scope
- chapters 4/5 的 `enhanced_index`/`qdii_fund`/`fof_fund` lens 定制 — 内容完善

## Verification

```bash
.venv/bin/python -m pytest tests/ -q                    # 246 passed
.venv/bin/python -m ruff check .                        # All checks passed
git diff --check                                        # clean
git log --oneline d33b901..HEAD                         # 15 commits, all P6
git diff --stat d33b901..HEAD                           # 56 files, +8659 -157
```

## Conclusion

PASS.

P6 template contract hardening correctly moves `CHAPTER_CONTRACT` and `ITEM_RULE` from document-only guidance into Capability-layer machine contracts. All five slices (S1-S5) are implemented deterministically with no LLM/NLP, no fund document/PDF/cache access, no `extra_payload`, no Service/UI/CLI behavior changes. Import cycles are avoided via `chapter_blocks.py` shared module and lazy renderer exports. The splitter fails closed on all malformed inputs. C2 deterministic audit covers all 45 required item markers and 9 forbidden content rules. FQ5 consumes contract facts from `score.json` without overclaiming. 246/246 tests pass, ruff clean.

Four low-severity maintenance findings: hardcoded evidence heading string in 3 locations, docstring drift omitting C2, `locals()` guard pattern in extraction_score, and `unresolved_chapter_ids` semantic imprecision. None are correctness or stability blockers.
