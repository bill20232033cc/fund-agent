# P2-S9 Re-Review — AgentGLM

- **Gate**: P2-S9 re-review
- **Reviewer**: AgentGLM (independent review worker)
- **Date**: 2026-05-18
- **Source review**: `docs/reviews/p2-s9-code-review-glm-2026-05-18.md`
- **Fix artifact**: `docs/reviews/p2-s9-fix-2026-05-18.md`

## Conclusion

**PASS — All accepted findings (F-1/F-2/F-3) are fixed with regression tests. F-4 deferred by controller, no objection.**

---

## Per-Finding Verification

### F-1 [medium] dict_values leak — FIXED

**Call site**: `renderer.py:270` — unchanged, still passes `manager_alignment.values()`.

**Root cause fix**: `renderer.py:712-734` — `_join_values` now handles `Mapping` (line 729) and `Iterable` (line 731) as separate branches. `dict_values` is not a `Mapping` but is an `Iterable`, so it correctly iterates element-by-element instead of falling through to `str(values)`.

New imports added: `from collections.abc import Iterable, Mapping` at `renderer.py:10`.

**Rendered output verified**:
```
- 利益一致性原始披露：基金经理持有本基金。
```
No `dict_values` string appears in the report.

**Regression test**: `test_renderer.py:543-561` — `test_render_template_report_formats_manager_alignment_and_reason_punctuation` asserts:
- `"dict_values" not in result.report_markdown`
- `"利益一致性原始披露：基金经理持有本基金" in result.report_markdown`

### F-2 [low] doubled punctuation — FIXED

**Call site**: `renderer.py:303` — now wraps with `_sentence_body(...)` before appending `"。"`.

**Fix mechanism**: New helper `_sentence_body` (`renderer.py:737-753`) strips trailing Chinese/English sentence-ending punctuation (`。！？；;,.，`) before the template adds its own period.

**Rendered output verified**:
```
- 依据说明：投资者收益高于产品收益。
```
No `。。` in report.

**Regression test**: Same test as F-1, line 560 asserts:
- `"投资者收益高于产品收益。。" not in result.report_markdown`

### F-3 [low] README stale duplicate — FIXED

**Location**: `fund_agent/fund/README.md:209-221` — "内部分层" section now has single `template/` entry at line 217. The stale `- \`template/\`：后续模板能力的扩展位置` entry is removed.

**Regression test**: `test_renderer.py:563-583` — `test_fund_readme_has_single_current_template_layer_entry` reads the actual README file and asserts:
- Current entry count == 1
- Stale entry not present

### F-4 [low] latent forbidden-term false positive — DEFERRED

Controller accepted deferral. No code change. `_validate_report_wording` still uses substring `in` matching. This remains a residual risk if future template text includes phrases like "买入前检查清单". No objection to deferral for MVP scope.

---

## Validation Run

```
$ .venv/bin/python -m pytest tests/fund/template tests/fund/audit -q
..................
18 passed in 0.73s

$ .venv/bin/python -m pytest tests/fund/analysis -q
........................................
40 passed in 0.54s
```

58 total tests pass, up from 56 pre-fix (2 new regression tests added). No regressions.

---

## Residual Risks

- F-4 deferred: substring-based forbidden term check may produce false positives if checklist question text evolves to include "买入前检查清单" or similar legitimate analytical references containing forbidden substrings.
- Chapter 5 cross-year comparison and evidence anchor precision limitations unchanged from original review; tracked in implementation artifact.
