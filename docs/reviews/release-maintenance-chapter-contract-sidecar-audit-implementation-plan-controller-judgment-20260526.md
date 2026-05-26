# Controller Judgment: CHAPTER_CONTRACT Sidecar + Dev-only Report-writing Audit Implementation Plan

> Date: 2026-05-26
> Controller: AgentController
> Gate: Fund-layer executable CHAPTER_CONTRACT sidecar + dev-only report-writing audit implementation gate
> Scope: Gate A implementation-plan refinement and plan-review judgment

## Inputs

| Purpose | Artifact |
|---|---|
| Implementation plan | `docs/reviews/release-maintenance-chapter-contract-sidecar-audit-implementation-plan-20260526.md` |
| Plan review: MiMo | `docs/reviews/release-maintenance-chapter-contract-sidecar-audit-implementation-plan-review-mimo-20260526.md` |
| Plan review: GLM | `docs/reviews/release-maintenance-chapter-contract-sidecar-audit-implementation-plan-review-glm-20260526.md` |

## Gate A Judgment

Gate A is accepted.

The plan is code-generation-ready for the first implementation slice:

- add `fund_agent/fund/template/chapter_contract_constraints.py`;
- add `fund_agent/fund/report_writing_audit.py`;
- add `tests/fund/template/test_chapter_contract_constraints.py`;
- add `tests/fund/test_report_writing_audit.py`;
- keep `scripts/report_quality_eval.py` integration deferred unless a later controller handoff explicitly expands scope;
- do not modify renderer, FQ0-FQ6, Service, CLI, Host/Agent, dayu runtime, document repository, PDF/cache/source helpers, production extractors, product entry points, or product defaults.

## Review Findings Judgment

| Finding | Controller disposition | Implementation instruction |
|---|---|---|
| MiMo F1 sidecar `FailureCategory` differs from existing evidence gap categories | Accepted as informational | Keep writing-audit failure categories separate from `GapFailureCategory`; document the distinction in module docstrings. |
| MiMo F2 `config_only` sidecar severity vs audit issue severity mismatch | Accepted as minor | Implementation must explicitly map sidecar `config_only` to audit issue `informational`, or expose `config_only` in a stable issue domain. Prefer mapping to `informational` to keep issue severity small. |
| MiMo F3 ChapterDraftSurrogate claim detection strategy unspecified | Accepted as minor | Implement a deterministic hybrid: explicit `claim_tags` first, then small phrase matching for the active Chapter 3 Chinese stability/consistency phrases used in tests. |
| MiMo F4 `quality_gate_integration.py` omitted from prohibited file list | Accepted as informational | Do not touch `fund_agent/fund/quality_gate_integration.py`; include it in boundary diff checks. |
| MiMo F5 docs/design sync section specificity | Accepted as informational | If docs sync is done after code/tests pass, update only `docs/design.md` §3.2 with current-code facts. |
| MiMo F6 bundle `fund_type_slot=None` fallback | Accepted as informational | Audit must resolve missing bundle fund-type slot to `default` constraints unless explicit chapter draft fund type is supplied. |
| GLM F1 `FailureBehavior` vs `RequirementSeverity` naming | Accepted as minor | Use one canonical type name. Prefer `RequirementSeverity` and either remove `FailureBehavior` or define it as an alias. |
| GLM F2 JSONL input record structure unspecified | Accepted as minor | Keep JSONL helper minimal and document that caller supplies parsed records; do not implement schema validation beyond extracting bundle-like mappings needed by tests. |
| GLM F3 surrogate fund-type simplification | Accepted as informational | Keep surrogate dev-only and map typed bundle fund type into the sidecar slot deterministically. |
| GLM F4 Chinese docstrings implicit | Accepted as informational | New modules/classes/functions must include complete Chinese docstrings per `AGENTS.md`. |
| GLM F5 boundary rg lacks `quality_gate_policy` | Accepted as informational | Add `quality_gate_policy` to local boundary grep when running validation. |

No review finding requires plan patch or re-review. The implementation handoff must include the accepted minor findings above as coding requirements.

## Next Action

Proceed to Gate B/C implementation with AgentCodex as implementation worker.

The worker must stop and report if the implementation needs any forbidden file or runtime boundary.
