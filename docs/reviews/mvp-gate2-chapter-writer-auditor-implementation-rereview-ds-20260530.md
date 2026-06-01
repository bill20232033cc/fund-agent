# Implementation Re-Review: MVP Gate 2 chapter_writer + chapter_auditor (post-fixes)

日期：2026-05-30
角色：AgentDS — independent implementation re-reviewer
Gate：`MVP Gate 2: chapter_writer + chapter_auditor`

## Reviewed Target

Post-fix Gate 2 implementation, verifying fixes for DS prior findings 01–03.

## Prior Findings Verified

### Finding 01 (MEDIUM): must_not_cover 程序审计确定性检查 → **已修复**

**Change**: 新增 `_audit_must_not_cover()` 函数（`chapter_auditor.py` line 555–582）和 `_must_not_cover_phrases()` 提取器（line 748–787）。

- 从 `contract.must_not_cover` 的每条契约句中，用正则剥离前缀（`不/不得/不要把/不将本章写成/...`）、去除括号注释、按分隔符拆分，提取 ≥4 字的禁止主题短语
- 对每个短语做子串匹配；命中即返回 C2 issue，`repair_hint="patch"`
- `audit_chapter_programmatic()` 调用链新增 `_audit_must_not_cover(input_data)`（line 345）
- 辅助常量：`_MUST_NOT_COVER_PREFIX_RE`、`_MUST_NOT_COVER_PARENS_RE`、`_MUST_NOT_COVER_SPLIT_RE`、`_MUST_NOT_COVER_STOPWORDS`（line 110–127）

**判定**: 已修复。must_not_cover 现在有独立的确定性程序化检查，不再完全依赖 LLM audit。短语提取策略合理（4 字阈值 + 前缀剥离 + 停用词过滤），虽非完美语义检测但对明确禁区有效。

### Finding 02 (LOW): L1 checked_rules 声明但无独立实现 → **已修复**

**Change**: 新增 `_audit_numerical_closure()` 函数（`chapter_auditor.py` line 676–704）。

- 按行检测 `A=R-B` / `A-C` / `R=A+B-C` 等数字闭环断言模式（`_NUMERICAL_CLOSURE_RE`）
- 命中行且包含数值（`_NUMERIC_TEXT_RE`：`\d+(\.\d+)?\s*%`）时，检查上下文 ±2 行内是否有 anchor marker
- 无邻近 anchor marker → L1 blocking issue，`repair_hint="patch"`
- `audit_chapter_programmatic()` 调用链新增 `_audit_numerical_closure(input_data)`（line 349）
- `checked_rules` 保持不变（已含 `"L1"`），现在有对应实现

**判定**: 已修复。L1 现在有独立的确定性检查函数，checked_rules 声明与实现匹配。

### Finding 03 (LOW): `mode="llm"` + `llm_client=None` 路径无独立测试 → **已修复**

**Change**: 新增 `test_writer_blocks_llm_mode_without_client_after_preflight_passes`（`test_chapter_writer.py` line 216–235）。

- 使用 `_bundle()` 默认 fixture（第 1 章，preflight 通过，fund_type 已知，有 anchors）
- `mode="llm"`（默认）、`llm_client=None`
- 断言 `status="blocked"`、`stop_reason="llm_unavailable"`、`draft is None`

**判定**: 已修复。preflight 通过 + llm 模式 + 无 client 路径现在有独立测试覆盖。

---

## Validation

```text
uv run ruff check .
All checks passed!
```

```text
uv run pytest tests/fund/test_chapter_writer.py tests/fund/test_chapter_auditor.py -q
38 passed in 0.80s
```

38 tests = 19 writer + 19 auditor（原 34 基础上增加 4 个：llm_unavailable 路径测试、must_not_cover 审计测试、numerical_closure 审计测试各 1 个，加 1 个额外覆盖）。

---

## Implementation Re-Review Conclusion

**PASS**

All 3 prior findings (01 MEDIUM, 02 LOW, 03 LOW) are confirmed fixed:

- `_audit_must_not_cover()` provides deterministic must_not_cover programmatic coverage
- `_audit_numerical_closure()` provides deterministic L1 numerical closure check
- `test_writer_blocks_llm_mode_without_client_after_preflight_passes` covers the llm_unavailable path

38 tests pass, no new issues introduced.

## Reviewer Self-Check

- [x] prior findings 逐项验证，均有对应代码变更
- [x] 所有修复通过测试确认
- [x] conclusion 为 PASS
- [x] output path 为 `docs/reviews/mvp-gate2-chapter-writer-auditor-implementation-rereview-ds-20260530.md`
- [x] 未修改任何文件
