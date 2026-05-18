# P2-S9 Code Review — AgentGLM

- **Gate**: P2-S9 code review
- **Reviewer**: AgentGLM (independent review worker)
- **Date**: 2026-05-18
- **Design source**: `docs/design.md`
- **Control source**: `docs/implementation-control.md`
- **Implementation artifact**: `docs/reviews/p2-s9-implementation-2026-05-18.md`

## Conclusion

**FAIL — 1 accepted finding, severity medium.**

The template renderer achieves the P2-S9 goal of producing an 8-chapter Markdown report compatible with `run_programmatic_audit`. Test suite and audit pass-through validation are meaningful and correct. However, Chapter 3 has a confirmed rendering bug that leaks a raw Python `dict_values(...)` representation into the report body instead of the intended human-readable text.

---

## Findings

### F-1 [medium] Chapter 3 renders raw `dict_values(...)` string for manager_alignment

**Location**: `fund_agent/fund/template/renderer.py:269`

```python
f"- 利益一致性原始披露：{_join_values(manager_alignment.values()) if manager_alignment else _MISSING_TEXT}。",
```

**Root cause**: `manager_alignment` is an `ExtractedField[dict]`, so `manager_alignment.value` is a `dict`. Calling `.values()` on it returns a `dict_values` view object. The `_join_values` helper (`renderer.py:711-731`) checks for `tuple | list | set` but **not** `dict_values`, so the value falls through to `str(values)` at line 731, producing the raw Python string:

```
dict_values(['基金经理持有本基金'])
```

**Expected output**: `基金经理持有本基金`

**Fix**: In `_join_values`, add `dict_values` (or more broadly, any `Iterable`) to the isinstance check, or convert `manager_alignment.values()` to `tuple()` at the call site. Minimal fix at the call site:

```python
_join_values(tuple(manager_alignment.values()))
```

Or extend `_join_values` to handle `dict_values | dict_keys | dict_items`:

```python
if isinstance(values, tuple | list | set | dict_values | dict_keys | dict_items):
```

(Requires `from collections.abc import dict_values, dict_keys, dict_items` or `from typing import ItemsView, KeysView, ValuesView`.)

**Reproduction**:

```bash
.venv/bin/python -c "
from fund_agent.fund.extractors.models import ExtractedField
from fund_agent.fund.template.renderer import _join_values
field = ExtractedField(
    value={'manager_holding': '基金经理持有本基金'},
    anchors=(), extraction_mode='direct', note=None,
)
print(repr(_join_values(field.value.values())))
"
# Output: "dict_values(['基金经理持有本基金'])"
```

**Evidence in rendered output** (full report print):

```
# 3. 基金经理画像与言行一致性
...
- 利益一致性原始披露：dict_values(['基金经理持有本基金'])。
```

**Impact**: Report text contains a non-human-readable Python representation. This is not caught by `_validate_report_wording` (no forbidden terms triggered), and the audit passes because P2/P3 rules only check minimum length and evidence presence, not textual quality. Users reading the report would see the raw `dict_values(...)` string.

---

### F-2 [low] Double period in Chapter 4 reasons

**Location**: `fund_agent/fund/template/renderer.py:302`

```python
f"- 依据说明：{_join_values(input_data.investor_experience.reasons)}。",
```

When `reasons` contains text ending with `"。"`, the template appends another `"。"`, producing `"。。"` in the rendered report.

**Evidence in rendered output**:

```
- 依据说明：投资者收益高于产品收益。。
```

**Fix**: Strip trailing `"。"` from `_join_values` result before appending, or remove the hardcoded `"。"` from the template and require callers to include trailing punctuation in reasons tuples.

---

### F-3 [low] README `template/` entry duplicated in internal layering section

**Location**: `fund_agent/fund/README.md:217` and `fund_agent/fund/README.md:222`

```markdown
- `template/`：模板渲染能力。当前包含 `renderer.py`，只消费 P1/P2 结构化结果并输出 8 章 Markdown 与程序审计输入。
...
- `template/`：后续模板能力的扩展位置
```

The `template/` directory appears twice in the "内部分层" section with conflicting descriptions. The first entry (line 217) is current and accurate; the second (line 222) is a stale placeholder that should be removed.

---

### F-4 [low] Latent false-positive risk in forbidden term validation

**Location**: `fund_agent/fund/template/renderer.py:764`

The `_validate_report_wording` function uses substring `in` matching for forbidden terms like `"买入"`. If the design doc's checklist section title "买入前检查清单" ever appears in rendered output (e.g., as a section header or question context), the validation would raise `ValueError` and block rendering, despite the text being a legitimate analytical reference rather than investment advice.

This is not a current issue (no rendered text contains "买入"), but the risk increases if the checklist question text evolves to include the design doc section title.

---

## Scope Adherence Checks

| Check | Result |
|-------|--------|
| P2-S9 goal: 8-chapter Markdown output compatible with `run_programmatic_audit` | PASS — all 8 chapters rendered, audit input structurally correct |
| Project boundaries: no UI/Service/Engine/document repository access | PASS — renderer only imports from `fund_agent.fund.analysis`, `fund_agent.fund.audit`, `fund_agent.fund.data_extractor`, `fund_agent.fund.extractors.models` |
| AGENTS: Chinese docstrings | PASS |
| AGENTS: template chapter references in docstrings | PASS — each `_render_chapter_N` references its chapter title and number |
| AGENTS: no explicit params hidden in `extra_payload` | PASS — `TemplateRenderInput` has all fields explicitly declared |
| AGENTS: fund type before generic analysis | PASS — Chapter 0 states "本报告先识别基金类型" and `classified_fund_type` comes from P1 classification-first extraction |
| AGENTS: evidence traceability | PASS — all chapters carry `> 📎 证据：年报§...` lines and appendix section |
| AGENTS: no buy/sell recommendations or future return prediction | PASS — `_validate_report_wording` enforces this at render time; `suggest_replace` wording is within allowed boundary |
| Final judgment boundary: allowed labels only | PASS — `TemplateFinalJudgment` is `Literal["worth_holding", "needs_attention", "suggest_replace"]` with runtime validation |
| Audit compatibility: P1/P2/P3/L1/R1/R2 pass for valid rendered output | PASS — confirmed by test and by manual run |
| Tests are meaningful and not only string smoke tests | PASS — 7 tests cover structure, evidence format, audit pass-through, missing data path, judgment boundary, forbidden terms, and structured input preservation |

---

## Validation Run

```
$ .venv/bin/python -m pytest tests/fund/template tests/fund/audit -q
................  16 passed in 0.83s

$ .venv/bin/python -m pytest tests/fund/analysis -q
........................................  40 passed in 0.77s
```

All 56 tests pass. No regressions.

---

## Open Questions / Residual Risks

1. **F-1 fix scope**: The fix for the `dict_values` bug is narrow (one line at the call site or one isinstance branch in `_join_values`). Recommend fixing before accepting the slice.
2. **Chapter 5 cross-year comparison**: The implementation artifact notes that Chapter 5 only consumes `current_stage` and nav record count; cross-year comparison remains a residual gap tracked in the implementation artifact. This is acceptable for MVP scope.
3. **Evidence anchor precision**: Anchors lacking `row_locator` are rendered with only year and section; this is by design per the implementation artifact, and precision depends on upstream P1 extraction.
4. **Stress test anchors**: `stress_test_result.anchors` are collected into the evidence appendix but not rendered inline in Chapter 6 — only Chapter 6's own evidence line shows risk check anchors. This is a minor inconsistency but not blocking.
5. **`build_programmatic_audit_input` is a passthrough**: The function simply returns `render_result.audit_input` with no additional processing. It exists as a convenience accessor, which is fine but could be removed if the API surface is deemed too wide.
