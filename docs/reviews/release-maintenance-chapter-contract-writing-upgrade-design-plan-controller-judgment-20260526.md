# Controller Judgment: Chapter Contract + Report Writing Upgrade Design Plan

> Date: 2026-05-26
> Controller: AgentController
> Gate: chapter contract implementation + report writing quality upgrade design gate
> Scope: Gate A report-quality escalation synthesis, Gate B executable CHAPTER_CONTRACT design, Gate C report-writing quality upgrade plan, Gate D plan review / re-review judgment

## Inputs

| Purpose | Artifact |
|---|---|
| Design + code-generation-ready plan | `docs/reviews/release-maintenance-chapter-contract-writing-upgrade-design-plan-20260526.md` |
| Plan review: MiMo | `docs/reviews/release-maintenance-chapter-contract-writing-upgrade-design-plan-review-mimo-20260526.md` |
| Plan review: GLM | `docs/reviews/release-maintenance-chapter-contract-writing-upgrade-design-plan-review-glm-20260526.md` |
| Plan re-review: MiMo | `docs/reviews/release-maintenance-chapter-contract-writing-upgrade-design-plan-rereview-mimo-20260526.md` |
| Plan re-review: GLM | `docs/reviews/release-maintenance-chapter-contract-writing-upgrade-design-plan-rereview-glm-20260526.md` |

Note: AgentGLM twice failed to write the initial review artifact to the requested path, then emitted the review text in the pane. The controller transcribed that text into the GLM review artifact and preserved the provenance in the artifact header. The subsequent GLM re-review was written by AgentGLM directly and returned `PASS`.

## Gate A Judgment

Gate A is accepted.

The plan lists five report-quality issues with direct evidence and failure-category classification:

| Rank | Issue | Controller judgment |
|---:|---|---|
| 1 | `004393` active Chapter 3 turnover/style-consistency gap | Accepted as `chapter contract`; direct evidence comes from quasi-real and small-baseline artifacts. |
| 2 | `004393` active Chapter 3 accepted wording marker not emitted by current renderer | Accepted as `writing template`; runtime required item remains deferred until output-changing scope is separately justified. |
| 3 | `004194` enhanced-index tracking-error readiness | Accepted as `data extraction`; not a writing-template fix. |
| 4 | `006597` bond risk lens facts | Accepted as `data extraction`; not a writing-template fix. |
| 5 | Multi-bundle JSONL `RQV_REF_MISSING=4` before the validator fix | Accepted as `validator consumer / evidence-link integrity`; already fixed, retained as escalation evidence rather than an unresolved report-writing defect. |

The plan does not rely on subjective report taste. Each issue points to an accepted artifact and keeps data extraction, evidence-link integrity, chapter contract, and writing-template concerns separate.

## Gate B Judgment

Gate B is accepted after patch.

The accepted design is a dev-only executable sidecar over existing `ChapterContract`, not a replacement and not a parallel truth source:

- `fund_agent/fund/template/contracts.py` remains the source for existing chapter ids, titles, `must_answer`, `must_not_cover`, `required_output_items`, and `preferred_lens`.
- The future sidecar stores `required_evidence`, `allowed_na_reason`, `failure_behavior`, and overlay severity without mutating the frozen `ChapterContract` dataclass.
- Sidecar validation must fail closed if it disagrees with existing chapter ids/titles.
- `audit_chapter_contract()` is separate from `run_programmatic_audit()` and `validate_report_quality_bundle()` / `validate_report_quality_jsonl()`.
- Chapter 2 enhanced-index and Chapter 6 bond requirements are configuration/informational only until their extraction gates supply reviewed evidence.

The design explicitly preserves the current eight-chapter v0 renderer default output and does not alter Service, CLI, renderer, FQ0-FQ6, Host/Agent/dayu, source helpers, `FundDocumentRepository`, or product entry points.

## Gate C Judgment

Gate C is accepted after patch.

The selected first implementation slice is the smallest scope that follows from the evidence: Fund-layer executable CHAPTER_CONTRACT sidecar plus dev-only report-writing audit, centered on active-fund Chapter 3 claim safety.

The next implementation gate may plan code changes only within the allowed files listed in the plan, with these binding decisions:

- Default audit module path: `fund_agent/fund/report_writing_audit.py`.
- Executable constraints path: `fund_agent/fund/template/chapter_contract_constraints.py`.
- `scripts/report_quality_eval.py` integration is optional and deferrable.
- `docs/design.md` sync is owned by the implementation agent only after code/tests pass, and must describe current code facts only.
- New modules target per-file coverage of at least 80%; if tooling cannot report per-file coverage, the implementation artifact must record the measured alternative and residual risk.

Renderer changes are explicitly not part of the first implementation slice. A later output-changing slice may be opened only if dev-only audit evidence proves the exact minimal renderer wording change required.

## Review Findings Judgment

| Finding | Controller disposition | Rationale |
|---|---|---|
| MiMo M1 audit module path ambiguity | Accepted and closed | Plan now fixes `fund_agent/fund/report_writing_audit.py` as the only audit module path. |
| MiMo M2 design.md owner / acceptance ambiguity | Accepted and closed | Plan now defines implementation-agent ownership and current-code-fact-only acceptance criteria. |
| MiMo M3 coverage target missing | Accepted and closed | Plan now states new modules should target >=80% per-file coverage or record residual risk. |
| MiMo m1 audit relationship unclear | Accepted and closed | Plan now includes a three-path boundary table. |
| MiMo m2 optional script scope ambiguity | Accepted and closed | Plan now marks script integration optional and deferrable. |
| MiMo m3 `core` undefined | Accepted and closed | Plan now defines `core` as explicit sidecar requirement severity, normally tied to preferred-lens priority. |
| MiMo m4 `ReportDataGapOverride.required_report_wording` missing | Accepted and closed | Plan now requires the active Chapter 3 audit to consume or reference this wording path. |
| GLM M1 sidecar overlap with existing modules | Accepted and closed | Plan now binds the sidecar to existing `ChapterContract` and prevents parallel truth. |
| GLM M2 audit boundary unclear | Accepted and closed | Plan now separates writing audit, programmatic audit, and report-quality validator responsibilities. |
| GLM M3 new fields absent from frozen dataclass | Accepted and closed | Plan now stores new fields in the sidecar and does not mutate `ChapterContract`. |
| GLM M4 Chapter 2/6 false positive risk | Accepted and closed | Plan now limits deferred extraction-dependent requirements to informational/config findings. |
| GLM m1 existing script wording | Accepted and closed | Plan now says `scripts/report_quality_eval.py` is an existing maintainer-only script. |
| GLM m2 Top 5 category refinement | Accepted and closed | Plan now uses `validator consumer / evidence-link integrity`. |
| GLM m3 overlay tests too broad | Accepted and closed | Plan now limits enhanced-index and bond tests to configuration correctness in the first slice. |

MiMo re-review verdict: `PASS`.

GLM re-review verdict: `PASS`.

No finding remains blocking or material for the next implementation gate.

## Next Entry Point

Next gate: implement the accepted Fund-layer sidecar/audit slice.

Implementation must stop and return to controller if it needs to touch renderer, Service, CLI, FQ0-FQ6, source helpers, `FundDocumentRepository`, Host/Agent/dayu runtime, product entry points, scratch fixtures, or product default behavior.

## Residuals

| Residual | Owner / next gate |
|---|---|
| Enhanced-index tracking-error evidence for `004194` | Future data/source extraction or reviewed-fact gate |
| Bond risk lens evidence for `006597` | Future data/source extraction or reviewed-fact gate |
| Fallback-blocked index/QDII rows and pure FOF coverage | Source reliability / fund-type taxonomy gates |
| Product renderer emission of accepted Chapter 3 insufficiency wording | Future output-changing renderer/report-writing gate after dev-only audit evidence |
| LLM audit / repair loop | Future architecture/design gate |
| Host/Agent/dayu runtime integration | Future explicit architecture gate |

## Controller Decision

The design/plan/review gate is accepted locally. The implementation gate may start only from the patched plan and must preserve the current product-flow boundaries.
