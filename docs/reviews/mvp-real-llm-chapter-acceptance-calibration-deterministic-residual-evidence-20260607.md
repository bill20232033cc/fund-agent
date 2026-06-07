# MVP Real LLM Chapter Acceptance Calibration Deterministic Residual Evidence

## 1. Scope

Evidence-only execution of:

- `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-deterministic-residual-evidence-plan-20260607.md`
- `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-deterministic-residual-evidence-controller-judgment-20260607.md`

No live LLM, provider call, code edit, test edit, template JSON edit, runtime/default/budget/config change, parser relaxation, quality gate change, golden/readiness change, Host runtime change, Agent runtime change, PR, push or release action was performed.

## 2. Retained Artifact Issue Matrix

Source artifact:

`reports/llm-runs/006597-2024-20260606T231450Z-host_run_435c8c7c2b8d4e2/`

| Chapter | Attempt | Retained evidence | Classification |
|---|---:|---|---|
| Ch2 | 0 | 7 required-output marker C2, 1 L1, 3 LLM C1; no `chapter_2_alpha_yearly_breakdown` issue | Marker C2 locally covered by Slice 1A; L1 locally covered by Slice 1D; no delete-rule signal yet |
| Ch2 | 1 | 7 required-output marker C2, 1 `programmatic:C2:chapter_2_alpha_yearly_breakdown:*`, 2 L1, 1 reviewable LLM C1 | `chapter_2_alpha_yearly_breakdown` delete-rule residual survives retained evidence |
| Ch6 | 0 | 4 required-output marker C2 and 1 `programmatic:C2:压力测试:*` | Marker C2 locally covered by Slice 1A; pressure-test C2 remains a distinct must_not_cover/audit-contract residual |
| Ch6 | 1 | 2 writer `unknown_anchor` issues; 0 programmatic issues | Inconclusive for pressure-test C2 because writer parsing stopped before a normal audit pass |

## 3. Current Contract Evidence

### Ch2 Item Rule

Current `fund_agent/fund/template/item_rules.py` still defines:

```text
rule_id=chapter_2_alpha_yearly_breakdown
chapter_id=2
mode=conditional
fund_types_any=('active_fund', 'enhanced_index')
segment_markers_any=('#### 超额收益分年度拆解', '超额收益分年度拆解（仅主动基金和指数增强）')
missing_behavior=delete_segment
```

Current `fund_agent/fund/chapter_auditor.py` still maps the same deleted-rule marker:

```text
chapter_2_alpha_yearly_breakdown -> ('超额收益分年度拆解', '超额收益稳定性')
```

Interpretation: Ch2 delete-rule C2 is current deterministic behavior, not stale retained evidence. It is separable from Slice 1D L1 hardening because Slice 1D did not change item-rule deletion or `_deleted_rule_marker_present()`.

### Ch6 Pressure-Test Must-Not-Cover

Current typed Ch6 contract still includes:

```text
ch6.must_not_cover.item_04:
不复述当前阶段事实，除非明确转译为风险、压力测试或否决项。
```

Current `_must_not_cover_phrases()` extracts:

```text
('复述当前阶段事实', '除非明确转译为风险', '压力测试')
```

Interpretation: the programmatic auditor currently treats `压力测试` as a forbidden phrase even though the template clause uses it inside an exception, not as a forbidden topic. This is direct code/template same-source evidence of an audit-contract residual. It is not closed by Slice 1C unknown-anchor hardening.

## 4. Validation

```bash
uv run pytest tests/fund/test_chapter_writer.py tests/fund/test_chapter_auditor.py -q
```

Result: `89 passed in 0.59s`.

```bash
uv run pytest tests/services/test_chapter_orchestrator.py -q
```

Result: `78 passed in 0.65s`.

```bash
uv run ruff check fund_agent/fund/chapter_writer.py fund_agent/fund/chapter_auditor.py tests/fund/test_chapter_writer.py tests/fund/test_chapter_auditor.py
```

Result: `All checks passed!`.

## 5. Findings

### Finding A: Ch2 Delete-Rule Residual Survives

`chapter_2_alpha_yearly_breakdown` is an active `delete_segment` ITEM_RULE for non-active / non-enhanced-index funds. Retained Ch2 attempt 1 violates it by rendering text that matches the deleted segment marker. Existing local hardening does not remove or change that rule.

Recommended route: open a small implementation slice only if the current writer prompt/repair context does not already make deleted ITEM_RULE segment boundaries clear enough. The slice should be bounded to writer/repair instructions or item-rule prompt surfacing; it must not remove the ITEM_RULE or relax the auditor.

### Finding B: Ch6 Pressure-Test C2 Survives As Audit-Contract Residual

Retained Ch6 attempt 0 hit `programmatic:C2:压力测试:*`. Current `_must_not_cover_phrases()` still extracts `压力测试` from an exception clause and therefore blocks pressure-test wording that the template appears to allow when translated as risk / pressure-test / veto semantics.

Recommended route: open a small implementation slice to correct must_not_cover phrase extraction or contract coverage for exception wording. The slice must preserve fail-closed behavior for true forbidden topics and add deterministic regression tests for Ch6 pressure-test wording.

### Finding C: Ch6 Attempt 1 Does Not Close Pressure-Test Residual

Ch6 attempt 1 has no pressure-test C2 only because it stopped at writer `unknown_anchor`. That absence is inconclusive and cannot be used as acceptance evidence.

## 6. Controller Recommendation

Do not close the chapter acceptance calibration gate yet.

Open the next reviewed implementation slice as:

`Slice 1G - Ch2 delete-rule prompt/repair and Ch6 pressure-test must_not_cover exception calibration`

Suggested boundary:

- Allowed production files: `fund_agent/fund/chapter_writer.py`, `fund_agent/services/chapter_orchestrator.py`, `fund_agent/fund/chapter_auditor.py`, `fund_agent/fund/README.md`.
- Allowed tests: `tests/fund/test_chapter_writer.py`, `tests/services/test_chapter_orchestrator.py`, `tests/fund/test_chapter_auditor.py`.
- Non-goals: no live LLM, no provider/default/runtime/budget/config changes, no template JSON edits, no removal of ITEM_RULE, no auditor relaxation for true forbidden topics, no quality/golden/readiness/score-loop/Host/Agent runtime changes.
