# MVP Gate 4 Slice 4A review fix evidence

日期：2026-05-30
角色：AgentCodex fix worker
Gate：`MVP Gate 4 Slice 4A: Service final_chapter_assembler review fix`
范围：只处理 DS-M1/M2/M3/M4；顺手覆盖 MiMo L1-L3 和 DS L2/L3 中低风险测试缺口；不做 4B/4C/4D；不 commit。

## Scope guard

本次只修改：

- `fund_agent/services/final_chapter_assembler.py`
- `tests/services/test_final_chapter_assembler.py`
- `docs/reviews/mvp-gate4-final-assembler-slice4a-review-fix-evidence-20260530.md`

未修改：

- `fund_agent/services/__init__.py`
- `tests/README.md`
- `fund_agent/fund/**`
- CLI
- `fund_analysis_service`
- `docs/design.md`
- `docs/implementation-control.md`
- `docs/current-startup-packet.md`
- golden / score / quality / final judgment semantics

注意：开始前工作区已有 `fund_agent/services/__init__.py`、`tests/README.md` 修改，以及 Slice 4A 新文件未跟踪；本 worker 未触碰禁改文件。

## Fixes

### DS-M1

`_validate_policy` 移除了 `len(set(chapter_ids)) != len(chapter_ids)` 重复分支。

原因：Slice 4A 当前使用 `chapter_ids == DEFAULT_REQUIRED_BODY_CHAPTER_IDS` 作为严格契约，非默认顺序、缺章、多章、重复章都会由严格相等统一拒绝；保留重复检查会误导 reader 以为该分支可达。

### DS-M2

在 `test_assembles_report_in_render_order_while_chapter0_uses_chapter7_summary` 增加第 0 章负向断言：

- 不包含 `证据与出处`
- 不包含 `> 📎 证据`
- 不包含 `<!-- anchor:`

### DS-M3

新增 `test_final_assembler_imports_stay_above_fact_and_source_boundaries`，通过 AST 静态检查确认 `final_chapter_assembler.py`：

- 不导入 `StructuredFundDataBundle`
- 不导入 `ChapterFactProjection`
- 不直接导入 `data_extractor` / `chapter_facts` / `documents` / `repository` / `pdf` / `cache` / `source` 相关模块

### DS-M4

`_first_non_empty_line` 改为单次 `splitlines()` 扫描，并删除已无用途的 `_SUPPORTING_SNIPPET_LINE_LIMIT` 常量。

### Low findings covered

额外补充以下测试，不改变 production 语义：

- `orchestration.status="blocked"` 与 `partial` 参数化覆盖，确认 fail-closed。
- 重复章节触发 `duplicate_chapter` blocking issue。
- `required_body_chapter_ids=()` 触发 `ValueError`。
- 非法 `selected_judgment="buy"` 触发输入边界 `ValueError`。
- 通过 monkeypatch 构造 late blocking chapter0 issue，覆盖 `allow_incomplete_debug_markdown=True` 分支保留 debug markdown。

## Validation

```text
uv run ruff check fund_agent/services/final_chapter_assembler.py tests/services/test_final_chapter_assembler.py
→ All checks passed!
```

```text
uv run pytest tests/services/test_final_chapter_assembler.py -q
→ 14 passed in 0.74s
```

```text
uv run pytest tests/services/test_chapter_orchestrator.py tests/fund/test_chapter_writer.py tests/fund/test_chapter_auditor.py tests/fund/test_chapter_facts.py -q
→ 81 passed in 0.46s
```

```text
git diff --check
→ clean
```

## Residuals

- Slice 4B/4C/4D 未处理，仍按 Gate 4 plan residual 推进。
- 未提交 commit。
