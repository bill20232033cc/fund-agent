# MVP Real LLM Chapter Acceptance Calibration Deterministic Residual Evidence Judgment

## 1. Decision

`EVIDENCE_ACCEPTED_OPEN_SLICE_1G`

The deterministic residual evidence is accepted. The chapter acceptance calibration gate should continue with a reviewed implementation slice.

## 2. Evidence Chain

- Plan: `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-deterministic-residual-evidence-plan-20260607.md`
- Plan review: `docs/reviews/plan-review-20260607-100800.md`
- Plan controller judgment: `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-deterministic-residual-evidence-controller-judgment-20260607.md`
- Evidence: `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-deterministic-residual-evidence-20260607.md`
- Evidence review: `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-deterministic-residual-evidence-review-20260607.md`

## 3. Accepted Facts

- Ch2 `chapter_2_alpha_yearly_breakdown` delete-rule C2 survives as current deterministic behavior because the ITEM_RULE still requires deleting the segment outside active/enhanced-index funds and retained attempt 1 rendered a deleted segment marker.
- Ch6 pressure-test C2 survives as an audit-contract residual because current phrase extraction treats `压力测试` from an exception clause as a forbidden phrase.
- Ch6 attempt 1 absence of pressure-test C2 is inconclusive because the writer stopped on unknown anchors before a normal audit pass.
- Local validation passed: `89 passed`, `78 passed`, ruff PASS.

## 4. Authorized Next Slice

Open `Slice 1G - Ch2 delete-rule prompt/repair and Ch6 pressure-test must_not_cover exception calibration`.

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

- Slice 1G plan, review, controller judgment, implementation evidence, code review and implementation judgment.
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`

## 5. Non-Goals

- No live LLM command, retry, endpoint probe or provider call.
- No provider/default/runtime/budget/config change.
- No template JSON edit.
- No removal of Ch2 ITEM_RULE.
- No auditor relaxation for true forbidden topics.
- No parser relaxation, quality/golden/readiness/score-loop/Host/Agent runtime/PR/push/release change.

## 6. Next Action

Write and review the Slice 1G implementation plan before editing code.
