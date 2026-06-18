# MVP Real LLM Chapter Acceptance Calibration Slice 1G Plan

## 1. Goal

Fix two deterministic residual roots found by the accepted evidence gate:

1. Ch2 `chapter_2_alpha_yearly_breakdown` false-positive / under-specified delete-rule handling.
2. Ch6 `must_not_cover` phrase extraction incorrectly treating `压力测试` from an exception clause as a forbidden phrase.

No live LLM, provider/runtime/default/budget/config, template JSON, quality gate, golden/readiness, Host runtime, Agent runtime, score-loop, PR, push or release change is allowed.

## 2. Direct Evidence

Accepted evidence:

- `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-deterministic-residual-evidence-20260607.md`
- `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-deterministic-residual-evidence-review-20260607.md`
- `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-deterministic-residual-evidence-judgment-20260607.md`

Same-source root facts:

- Ch2 retained attempt 1 hit `programmatic:C2:chapter_2_alpha_yearly_breakdown:*`.
- Current `chapter_2_alpha_yearly_breakdown` ITEM_RULE is still active and `delete_segment`.
- Current `_deleted_rule_marker_present()` maps that rule to `("超额收益分年度拆解", "超额收益稳定性")`.
- `超额收益稳定性` is too broad because Ch2 required output still asks for `超额收益（A = R - B）及稳定性` and `超额收益性质判断（结构性 vs 阶段性）`.
- Ch6 retained attempt 0 hit `programmatic:C2:压力测试:*`.
- Current Ch6 contract says `不复述当前阶段事实，除非明确转译为风险、压力测试或否决项。`.
- Current `_must_not_cover_phrases()` extracts `('复述当前阶段事实', '除非明确转译为风险', '压力测试')`, so it blocks an exception topic rather than only the forbidden topic.

## 3. Scope

Allowed production files:

- `fund_agent/fund/chapter_writer.py`
- `fund_agent/services/chapter_orchestrator.py`
- `fund_agent/fund/chapter_auditor.py`
- `fund_agent/fund/README.md`

Allowed tests:

- `tests/fund/test_chapter_writer.py`
- `tests/services/test_chapter_orchestrator.py`
- `tests/fund/test_chapter_auditor.py`

Allowed artifacts/control:

- Slice 1G plan/review/judgment/evidence/review/judgment artifacts.
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`

## 4. Non-Goals

- Do not remove or weaken `chapter_2_alpha_yearly_breakdown` ITEM_RULE.
- Do not forbid legitimate Ch2 required-output discussion of stability / structure vs stage.
- Do not disable `must_not_cover` enforcement for true forbidden topics.
- Do not change template JSON, public chapter ids, parser behavior, LLM provider behavior, repair budget, score-loop, golden/readiness or Host/Agent runtime.
- Do not claim live acceptance for Ch2 or Ch6.

## 5. Implementation Decisions

### 5.1 Ch2 Deleted ITEM_RULE Calibration

1. Narrow `_deleted_rule_marker_present()` for `chapter_2_alpha_yearly_breakdown`:
   - keep markers that identify the deleted optional segment, such as `超额收益分年度拆解`;
   - remove the broad `超额收益稳定性` marker because it overlaps with current Ch2 required output semantics.

2. Add writer prompt clarity for deleted ITEM_RULE decisions:
   - do not output deleted ITEM_RULE headings or optional segment titles;
   - deleted ITEM_RULE ids are not permission to omit required_output markers;
   - for Ch2, stability can still be discussed only inside required output items when anchored or framed as evidence gap.

3. Add repair-context specificity for item-rule deleted-section issues:
   - if an auditor issue has `item_rule_ids`, tell the next writer to remove the deleted ITEM_RULE heading/segment while preserving required_output coverage.

### 5.2 Ch6 Must-Not-Cover Exception Calibration

1. Make `_must_not_cover_phrases()` exception-aware:
   - for clauses containing `除非`, extract forbidden phrases only from the text before `除非`;
   - do not return exception terms such as `压力测试` as forbidden phrases.

2. Preserve enforcement of true forbidden phrases:
   - `复述当前阶段事实` should still be blocked when present;
   - unrelated existing must_not_cover tests must still pass.

## 6. Tests

Add or update deterministic tests:

- `tests/fund/test_chapter_auditor.py`
  - Ch2 audit does not fail solely for required-output stability wording such as `多年度超额收益稳定性判断` when no deleted segment heading is present.
  - Ch2 audit still fails for deleted segment heading `#### 超额收益分年度拆解`.
  - Ch6 audit does not fail solely for pressure-test wording that is framed as risk / verification / pressure-test semantics.
  - Ch6 audit still fails for `复述当前阶段事实`.

- `tests/fund/test_chapter_writer.py`
  - writer prompt includes deleted ITEM_RULE boundary guidance.

- `tests/services/test_chapter_orchestrator.py`
  - item-rule deleted-section repair context tells writer to remove deleted ITEM_RULE heading/segment while preserving required_output coverage.

## 7. Validation Commands

```bash
uv run pytest tests/fund/test_chapter_writer.py tests/fund/test_chapter_auditor.py tests/services/test_chapter_orchestrator.py -q
```

Expected: pass.

```bash
uv run pytest tests/services/test_fund_analysis_service_llm.py tests/services/test_execution_contract.py -q
```

Expected: pass.

```bash
uv run ruff check fund_agent/fund/chapter_writer.py fund_agent/fund/chapter_auditor.py fund_agent/services/chapter_orchestrator.py tests/fund/test_chapter_writer.py tests/fund/test_chapter_auditor.py tests/services/test_chapter_orchestrator.py
```

Expected: pass.

```bash
git diff --check -- fund_agent/fund/chapter_writer.py fund_agent/fund/chapter_auditor.py fund_agent/services/chapter_orchestrator.py fund_agent/fund/README.md tests/fund/test_chapter_writer.py tests/fund/test_chapter_auditor.py tests/services/test_chapter_orchestrator.py docs/current-startup-packet.md docs/implementation-control.md docs/reviews/
```

Expected: pass.

## 8. Completion Criteria

Slice 1G can be accepted locally if:

- Ch2 deleted ITEM_RULE enforcement remains active for real deleted headings/segments.
- Ch2 legitimate required-output stability / structure-vs-stage wording is no longer blocked as deleted optional segment output.
- Ch6 pressure-test exception wording is no longer blocked by generic must_not_cover phrase extraction.
- True must_not_cover enforcement still blocks forbidden phrases.
- Focused validations pass.
- No live LLM or out-of-scope runtime/config/template/quality/golden/Host/Agent changes occur.
