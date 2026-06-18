# MVP Real LLM Chapter Acceptance Calibration Slice 1C Controller Judgment

## 1. Decision

`PLAN_ACCEPTED_SLICE_1C_CH6_UNKNOWN_ANCHOR_AUTHORIZED`

The Ch6 `unknown_anchor` prompt-contract hardening plan is accepted.

## 2. Evidence Chain

- Plan: `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-slice1c-ch6-unknown-anchor-plan-20260607.md`
- Plan review: `docs/reviews/plan-review-20260607-093454.md`

## 3. Authorized Scope

Allowed production files:

- `fund_agent/fund/chapter_writer.py`
- `fund_agent/fund/README.md`

Allowed tests:

- `tests/fund/test_chapter_writer.py`
- `tests/services/test_chapter_orchestrator.py` only if needed for orchestration diagnostic regression.

Allowed evidence/control files:

- `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-slice1c-ch6-unknown-anchor-implementation-evidence-20260607.md`
- `docs/reviews/code-review-*.md`
- `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-slice1c-ch6-unknown-anchor-implementation-controller-judgment-20260607.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`

## 4. Required Implementation Boundaries

- Harden writer prompt contract so only allowed anchors may be cited.
- Explicitly forbid synthesized anchor ids from fact metadata or nested fact values.
- Explicitly state that `bond_risk_evidence` group/internal anchors are not citeable until a future conversion helper creates `ChapterEvidenceAnchor`.
- Preserve fail-closed unknown-anchor parser behavior.
- Preserve projection behavior that does not expand bond-risk group anchors into `ChapterEvidenceAnchor`.

## 5. Explicit Non-Authorization

- No live LLM.
- No provider/default/runtime/budget/config change.
- No template JSON change.
- No extractor/projection schema migration.
- No quality gate, score-loop, golden/readiness, Agent runtime, Host runtime, PR, push or release state change.
- No Ch2, Ch4 or Ch3/Ch5 implementation.
- Do not claim Ch6 live acceptance or complete report acceptance.
