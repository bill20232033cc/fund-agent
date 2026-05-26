# Renderer Minimal Integration Design Plan Review - Hume

> Date: 2026-05-26
> Reviewer: Hume
> Gate: renderer minimal integration design
> Verdict: BLOCK

## Findings

### F1 - High - Plan only replaces the style-stability fallback, but current Chapter 3 can still emit positive consistency claims

Evidence:

- The draft implementation route only says to replace the current generic Chapter 3 style-stability fallback.
- Current renderer also emits `言行一致性判断：{overall_signal} / {overall_status}`, `言行一致性汇总：...`, and each dimension reason.
- Existing renderer test fixtures include positive wording such as `风格一致。` and `言行一致性整体为绿灯。`

Risk:

- A later implementation that changes only the style-stability line may still emit unsupported `风格一致` or `言行一致` claims when Chapter 3 lacks reviewed turnover / style-change evidence.

Recommendation:

- Revise the future implementation slice so the active-fund Chapter 3 missing-evidence path handles `consistency_result` summary and dimension reason positive claims, not just the current style-stability fallback line.
- Add a test with green/aligned `ConsistencyCheckResult` and missing turnover/style evidence, proving final rendered Chapter 3 does not contain unsupported positive consistency claims.

### F2 - Medium - The source of the missing reviewed turnover/style evidence decision is not fully constrained

Evidence:

- The draft says to reuse existing renderer inputs unless a tiny explicit field is unavoidable.
- Current `_render_chapter_3()` reads `structured_data`, `consistency_result`, and anchors; it does not receive `ReportEvidenceBundle` or reviewed evidence status.

Risk:

- A later implementation agent may invent a new evidence-status detector, project `ReportEvidenceBundle`, or call the dev-only audit from renderer.

Recommendation:

- For the next minimal implementation, define the current renderer path as lacking reviewed turnover/style evidence for active-fund Chapter 3.
- Do not add a new Service input, `ReportEvidenceBundle` projection, or audit call in this slice.
- If a reviewed-evidence positive path is required later, open a separate input-contract design gate.

### F3 - Medium - Rendered Chapter 3 audit should be required test evidence, not optional confidence

Evidence:

- The draft makes `ChapterDraftSurrogate` plus `audit_report_writing_bundle()` optional.
- The gate evidence basis is the dev-only writing audit contract.

Risk:

- String assertions alone may miss positive consistency claims emitted from other renderer lines.

Recommendation:

- Add a required focused test that builds a `ChapterDraftSurrogate` from the future rendered active-fund Chapter 3 and runs `audit_report_writing_bundle()` in test-only mode with a compatible `data_gap` bundle.

### F4 - Low - `docs/design.md` records the design as accepted before plan review/controller judgment

Evidence:

- The plan was still `Draft for plan review`.
- `docs/design.md` already used `已接受的未来设计`.

Risk:

- Agents may treat a not-yet-reviewed design as accepted truth.

Recommendation:

- During review, mark the design paragraph as candidate / pending review; after controller judgment passes, upgrade it to accepted future design.

## Verdict

BLOCK. The evidence is enough to continue the design gate, but the plan is not yet safe for an implementation gate. Re-review is recommended after revising the Chapter 3 positive-claim handling and making rendered-output dev-only audit a required test.
