# MVP Real LLM Chapter Acceptance Calibration Slice 1G Implementation Evidence

## 1. Scope

Implemented:

- Ch2 deleted ITEM_RULE calibration.
- Ch6 `must_not_cover` exception phrase calibration.

No live LLM, provider call, endpoint probe, provider/default/runtime/budget/config change, template JSON edit, parser relaxation, quality/golden/readiness change, score-loop, Host runtime change, Agent runtime change, PR, push or release action was performed.

## 2. Files Changed

Production:

- `fund_agent/fund/chapter_writer.py`
- `fund_agent/services/chapter_orchestrator.py`
- `fund_agent/fund/chapter_auditor.py`
- `fund_agent/fund/README.md`

Tests:

- `tests/fund/test_chapter_writer.py`
- `tests/services/test_chapter_orchestrator.py`
- `tests/fund/test_chapter_auditor.py`

Artifacts:

- `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-slice1g-ch2-delete-rule-and-ch6-pressure-plan-20260607.md`
- `docs/reviews/plan-review-20260607-101200.md`
- `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-slice1g-ch2-delete-rule-and-ch6-pressure-controller-judgment-20260607.md`

## 3. Implementation Summary

### Ch2 Delete-Rule Calibration

- Narrowed `_deleted_rule_marker_present()` for `chapter_2_alpha_yearly_breakdown` from:

```text
("超额收益分年度拆解", "超额收益稳定性")
```

to:

```text
("超额收益分年度拆解",)
```

Reason: `超额收益稳定性` overlaps with legitimate Ch2 required-output wording about `超额收益（A = R - B）及稳定性` and structure-vs-stage discussion.

- Kept auditor enforcement for real deleted segment headings.
- Added writer prompt guidance that deleted ITEM_RULE ids forbid only the optional/conditional segment heading and dedicated segment, not required-output coverage.
- Added Service repair-context guidance for item-rule issues: remove deleted optional/conditional heading/segment while preserving required-output markers and safe evidence-gap wording.

### Ch6 Pressure-Test Exception Calibration

- Updated `_must_not_cover_phrases()` to ignore text after `除非` before extracting literal forbidden phrases.
- Current Ch6 clause `不复述当前阶段事实，除非明确转译为风险、压力测试或否决项。` now blocks `复述当前阶段事实` but no longer treats `压力测试` as forbidden.
- Existing fail-closed must_not_cover path remains active for true forbidden phrases.

## 4. Tests Added / Updated

- `tests/fund/test_chapter_auditor.py`
  - Ch2 required-output stability wording is not blocked as deleted ITEM_RULE content.
  - Ch2 deleted segment heading `#### 超额收益分年度拆解` still blocks when the item rule decision is `delete`.
  - Ch6 pressure-test wording in risk/verification context is not blocked by must_not_cover.
  - Ch6 true forbidden phrase `复述当前阶段事实` still blocks.

- `tests/fund/test_chapter_writer.py`
  - writer prompt includes deleted ITEM_RULE boundary guidance.

- `tests/services/test_chapter_orchestrator.py`
  - required corrections include item-rule deleted-section guidance and preserve required-output coverage.

## 5. Validation

```bash
uv run pytest tests/fund/test_chapter_writer.py tests/fund/test_chapter_auditor.py tests/services/test_chapter_orchestrator.py -q
```

Result: `171 passed in 0.99s`.

```bash
uv run pytest tests/services/test_fund_analysis_service_llm.py tests/services/test_execution_contract.py -q
```

Result: `47 passed in 0.75s`.

```bash
uv run ruff check fund_agent/fund/chapter_writer.py fund_agent/fund/chapter_auditor.py fund_agent/services/chapter_orchestrator.py tests/fund/test_chapter_writer.py tests/fund/test_chapter_auditor.py tests/services/test_chapter_orchestrator.py
```

Result: `All checks passed!`.

```bash
git diff --check -- fund_agent/fund/chapter_writer.py fund_agent/fund/chapter_auditor.py fund_agent/services/chapter_orchestrator.py fund_agent/fund/README.md tests/fund/test_chapter_writer.py tests/fund/test_chapter_auditor.py tests/services/test_chapter_orchestrator.py docs/current-startup-packet.md docs/implementation-control.md docs/reviews/
```

Result: pass.

## 6. Boundary Notes

- Ch2 ITEM_RULE is not removed and still blocks real deleted segment output.
- Ch6 `must_not_cover` is not disabled; exception terms after `除非` are simply not treated as forbidden phrases.
- Live acceptance for Ch2/Ch6 remains unproven.
- Full report acceptance remains unproven.
