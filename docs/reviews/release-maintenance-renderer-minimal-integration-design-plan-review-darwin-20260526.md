# Renderer Minimal Integration Design Plan Review - Darwin

> Date: 2026-05-26
> Reviewer: Darwin
> Gate: renderer minimal integration design
> Verdict: BLOCK

## Findings

### F1 - High - Default analyze/checklist behavior boundary conflicts with the planned renderer text change

Evidence:

- The draft says a later implementation may replace active-fund Chapter 3 fallback text.
- Current `render_template_report()` directly calls `_render_chapter_3()`, and default product analysis consumes the rendered Markdown.

Risk:

- The plan can be misread in two incompatible ways: either no output text may change, or a user-visible report text change can be treated as "default behavior unchanged" without explicit output-change acceptance.

Recommendation:

- Clarify that the next implementation, if authorized, is an output-changing renderer gate.
- The invariant should be: no default entrypoint, CLI parameters, Service control flow, exit code, FQ0-FQ6 semantics, or quality-gate policy changes; only the active-fund Chapter 3 missing-evidence fallback text may change.
- Require targeted assertions proving the text change is isolated to the active-fund Chapter 3 fallback and leaves 8-chapter structure, appendix, audit input, and quality gate behavior unchanged.

### F2 - High - `docs/design.md` prematurely writes the reviewed design as accepted future design

Evidence:

- The plan status was `Draft for plan review`.
- The draft itself requires plan reviews and controller judgment before `docs/design.md` records accepted future design.
- `docs/design.md` already says `已接受的未来设计`.

Risk:

- Truth-source state can get ahead of controller judgment.

Recommendation:

- Downgrade to candidate / pending review until controller judgment passes, then promote to accepted future design.

### F3 - Medium - Missing-evidence source is ambiguous and may push the implementation into audit/input-contract work

Evidence:

- The draft requires behavior when the renderer lacks reviewed turnover/style evidence.
- Current renderer has no reviewed-evidence input.
- The draft forbids audit calls but does not define the v1 evidence decision source.

Risk:

- A later implementation may add a new renderer input, Service plumbing, `ReportEvidenceBundle` projection, or audit call.

Recommendation:

- Define v1 as: with current renderer inputs, active-fund Chapter 3 must use the insufficient-evidence path by default because reviewed turnover/style evidence is not explicitly available.
- Any positive reviewed-evidence path requires a separate input-contract design gate.

### F4 - Medium - Test matrix omits renderer contract regressions that matter for this change

Evidence:

- Current renderer returns `ProgrammaticAuditInput`, evidence appendix, chapter blocks, ITEM_RULE decisions, and forbidden-investment-advice validation.
- The draft mentions full `test_renderer.py`, but does not make these contracts explicit acceptance criteria.

Risk:

- A later implementation may pass focused Chapter 3 text tests but regress audit input, appendix, or forbidden wording validation.

Recommendation:

- Add explicit acceptance checks for `result.audit_input.chapter_blocks == result.chapter_blocks`, evidence appendix preservation, `[M3]` or equivalent Chapter 3 missing-evidence reference preservation, and forbidden investment advice tests.

### F5 - Low - "Satisfy audit" wording can overstate dev-only audit coupling

Risk:

- The phrase can encourage integrating the dev-only audit into renderer or treating it as the only implementation acceptance basis.

Recommendation:

- Use "align with accepted audit wording constraints"; keep audit use test-only/scratch-only.

## Verdict

BLOCK. Revise F1 and F2 before controller judgment; F3 and F4 should be fixed at the same time to prevent implementation scope creep.
