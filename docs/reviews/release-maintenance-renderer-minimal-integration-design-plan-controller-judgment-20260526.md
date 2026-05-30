# Renderer Minimal Integration Design Plan Controller Judgment

> Date: 2026-05-26
> Role: Controller
> Gate: renderer minimal integration design
> Verdict: ACCEPTED_FOR_FUTURE_IMPLEMENTATION_GATE

## Scope

This judgment accepts a design-only plan for a future renderer minimal implementation gate. It does not authorize implementation in this turn.

Accepted plan:

- `docs/reviews/release-maintenance-renderer-minimal-integration-design-plan-20260526.md`

Review artifacts:

- `docs/reviews/release-maintenance-renderer-minimal-integration-design-plan-review-hume-20260526.md`
- `docs/reviews/release-maintenance-renderer-minimal-integration-design-plan-review-darwin-20260526.md`
- `docs/reviews/release-maintenance-renderer-minimal-integration-design-plan-rereview-hume-20260526.md`
- `docs/reviews/release-maintenance-renderer-minimal-integration-design-plan-rereview-darwin-20260526.md`

## Evidence Accepted

The design may proceed to a future implementation gate because:

- The dev-only chapter audit small-baseline gate accepted active-fund Chapter 3 material audit behavior after matcher tuning.
- The audit evidence proved the active-fund Chapter 3 missing-evidence / compatible `data_gap` wording contract can be evaluated deterministically.
- The renderer currently emits deterministic Chapter 3 text, so a future output-only scoped implementation can be reviewed with focused renderer tests.
- Reviewers confirmed after revision that the design no longer overstates evidence or hides product-output impact.

## Evidence Limits

The design does not prove:

- safe implementation without a separate implementation gate;
- material Chapter 2 enhanced-index or Chapter 6 bond renderer requirements;
- clean index, QDII, or pure FOF baseline readiness;
- a positive reviewed-evidence path for active-fund Chapter 3;
- any need to modify Service/CLI, FQ0-FQ6, Host/Agent/dayu, source helpers, or `FundDocumentRepository`.

## Controller Finding Judgment

| Finding | Source | Judgment | Reason |
|---|---|---|---|
| Plan only changed style-stability fallback but missed `consistency_result` positive claims | Hume F1 | ACCEPTED; FIXED | Revised plan now requires active-fund missing-reviewed-evidence path to suppress unsupported positive style-consistency / words-actions-consistency accepted-conclusion wording from summary lines and dimension reasons. |
| Missing reviewed-evidence decision source was ambiguous | Hume F2 / Darwin F3 | ACCEPTED; FIXED | Revised plan defines v1 as missing-reviewed-evidence by default because current renderer inputs lack explicit reviewed turnover/style evidence status; positive path requires a separate input-contract design gate. |
| Rendered Chapter 3 dev-only audit was optional | Hume F3 | ACCEPTED; FIXED | Revised plan makes test-only `ChapterDraftSurrogate` + `audit_report_writing_bundle()` validation required, while still banning runtime/product integration. |
| `docs/design.md` prematurely marked the design accepted | Hume F4 / Darwin F2 | ACCEPTED; FIXED DURING REVIEW | The paragraph was downgraded to `待裁决未来设计` during re-review; after this judgment it may be promoted to accepted future design. |
| Default analyze/checklist behavior boundary conflicted with output text change | Darwin F1 | ACCEPTED; FIXED | Revised plan states future implementation is output-changing only for active-fund Chapter 3 missing-evidence text; entrypoints, parameters, exit codes, Service control flow, and FQ0-FQ6 semantics remain unchanged. |
| Renderer contract regression tests were underspecified | Darwin F4 | ACCEPTED; FIXED | Revised plan adds explicit audit input, evidence appendix, forbidden investment advice, and full renderer test expectations. |
| "Satisfy audit" wording overstated coupling | Darwin F5 | ACCEPTED; FIXED | Revised plan now says align with accepted audit wording constraints and keeps audit use test-only. |

Both re-reviews returned PASS and no new blocker.

## Accepted Future Implementation Gate Scope

Next entry point: `renderer minimal integration implementation gate`.

Allowed future implementation scope, only after explicit user authorization:

- Modify `fund_agent/fund/template/renderer.py` only as needed for active-fund Chapter 3 missing-reviewed-evidence wording.
- Modify focused renderer tests and, if needed, test-only wiring to run dev-only writing audit over rendered Chapter 3.
- Preserve the 8-chapter renderer structure and evidence appendix.
- Preserve default CLI entrypoints, parameters, exit codes, Service control flow, FQ0-FQ6 semantics, Host/Agent/dayu boundaries, source-helper boundaries, and durable fixture boundaries.

The future implementation gate must not:

- call `audit_report_writing_bundle()` from production renderer, Service, CLI, or quality gate;
- add `ReportEvidenceBundle` projection to renderer;
- add new Service inputs or `TemplateRenderInput` fields for this slice;
- implement a positive reviewed-evidence path;
- modify Chapter 2 / Chapter 6 constraints;
- modify default analyze/checklist control flow;
- touch `FundDocumentRepository`, PDF/cache/source helpers, downloaders, production extractors, Host/Agent packages, or Dayu runtime.

## Required Future Verification Matrix

The future implementation gate must include:

- focused renderer tests for active-fund Chapter 3 insufficiency wording;
- a green/aligned `ConsistencyCheckResult` regression proving unsupported `风格一致` / `言行一致` accepted-conclusion wording is suppressed under missing-reviewed-evidence;
- rendered Chapter 3 wrapped as `ChapterDraftSurrogate` and audited with `audit_report_writing_bundle()` in test-only mode;
- assertions that `result.audit_input.chapter_blocks == result.chapter_blocks`;
- evidence appendix preservation checks, including Chapter 3 missing-evidence boundary;
- forbidden investment advice tests;
- full `tests/fund/template/test_renderer.py`;
- adjacent sidecar/audit tests;
- ruff and `git diff --check`.

## Residual Risks

- This does not implement renderer changes; it only authorizes a future implementation gate.
- Active-fund Chapter 3 remains the only material renderer candidate.
- Positive reviewed-evidence rendering remains deferred until a separate input-contract design gate.
- Broader chapter coverage, index/QDII/FOF baseline gaps, and LLM audit / repair loop remain future gates.
