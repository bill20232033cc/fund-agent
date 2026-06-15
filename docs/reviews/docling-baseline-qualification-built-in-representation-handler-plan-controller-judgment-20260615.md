# Docling Baseline Qualification Built-in Representation Handler Plan Controller Judgment - 2026-06-15

Gate: `Built-in Candidate Representation Route Handler Plan Review Gate`
Role: controller
Release/readiness: `NOT_READY`

## 1. Scope

This judgment closes review for the built-in candidate representation route handler plan.

Reviewed plan:

- `docs/reviews/docling-baseline-qualification-built-in-representation-handler-plan-20260615.md`

Review inputs:

- `docs/reviews/docling-baseline-qualification-built-in-representation-handler-plan-review-ds-20260615.md`
- `docs/reviews/docling-baseline-qualification-built-in-representation-handler-plan-review-mimo-20260615.md`
- `docs/reviews/docling-baseline-qualification-built-in-representation-handler-plan-rereview-ds-20260615.md`

This gate does not implement handlers, run Docling conversion, run pdfplumber export, read annual-report PDF bodies, run live/network/EID/FDR/provider/LLM/analyze/readiness/release/PR commands, or update production repository/source/parser behavior.

## 2. Truth Sources

- `AGENTS.md`
- `docs/design.md`
- `docs/implementation-control.md`
- `docs/current-startup-packet.md`
- `docs/reviews/docling-baseline-qualification-full-representation-export-handler-routing-decision-controller-judgment-20260615.md`
- `docs/reviews/docling-baseline-qualification-full-representation-export-implementation-controller-judgment-20260615.md`
- `docs/reviews/docling-route-a-local-artifact-conversion-quality-evidence-20260615.md`

Accepted constraints:

- production annual-report source remains EID single-source/no fallback;
- candidate representation routes are not source truth;
- Docling remains candidate-only and not a production parser replacement;
- EID HTML render remains `eid_xbrl_html_render_candidate`, not raw XML/XBRL truth;
- Service/UI/Host/renderer/quality gate must not directly access parser/cache/source helpers;
- release/readiness remains `NOT_READY`.

## 3. Review Disposition

| Finding | Source | Controller disposition | Reason |
|---|---|---|---|
| No blocking boundary issue | MiMo review | ACCEPT | MiMo found the plan preserves candidate-only status, `NOT_READY`, EID single-source/no fallback, and production repository/source/cache/Service/UI/Host/renderer/quality gate boundaries. |
| DS-F1 overwrite/reference conflict | DS review | ACCEPT_WITH_REWRITE | DS found that S1 `reference_existing_json` existing JSONs conflicted with the original no-clobber wording. The plan was amended so no-clobber applies only to write-producing `handled` and `blocked` entries, while `reference_existing_json` remains read-only validation and is never rewritten. |
| DS-F1 closure | DS targeted re-review | ACCEPT | DS targeted re-review passed and confirmed the amended plan includes no-live tests for read-only reference validation, default write-output rejection, mixed-manifest no-partial-write behavior, and `--allow-overwrite` scope. |

## 4. Accepted Plan Requirements

The accepted no-live implementation gate must follow these binding requirements:

- Implement candidate-internal handlers only under `fund_agent/fund/documents/candidates/`.
- Do not modify `FundDocumentRepository`, source policy, production cache, production parser behavior, extractor consumers, `EvidenceAnchor`, `CHAPTER_CONTRACT`, Service, Host, UI, renderer or quality gate.
- Add explicit opt-in CLI support for built-in handlers; default remains validation-only.
- Keep Docling lazy-imported and candidate-only; use local artifact/offline/socket-block semantics and blocked failure classes for missing artifacts, network attempts or model artifact unavailability.
- Keep pdfplumber handler candidate-internal and fake-tested; implementation tests must not read real annual-report PDF bodies.
- Keep EID HTML handler blocked unless a later accepted discovery gate provides local accepted render artifacts.
- Enforce default no-clobber for write-producing `handled` and `blocked` entries.
- Keep `reference_existing_json` read-only and never rewritten.
- Require `--allow-overwrite` for any write-producing overwrite, and do not use it as an implementation-test default.
- Preserve all non-proof guard fields: not source truth, not field correctness proof, not taxonomy compatibility proof, not parser replacement, not readiness proof.

## 5. Residuals

| Residual | Owner | Next handling |
|---|---|---|
| Concrete Docling socket-block implementation must be proven without real annual-report conversion in tests. | Implementation worker + reviewers | No-live implementation gate and implementation review. |
| Full S4/S5/S6 annual-report export quality is not proven. | Evidence worker | Later full representation export evidence gate after handler implementation acceptance. |
| S4/S5/S6 EID HTML render URLs/artifacts are not accepted for this baseline evidence path. | Future discovery/evidence gate | Keep EID HTML blocked JSON for first-wave evidence unless separate bounded discovery is accepted. |
| S2/S3 provenance/hash issues remain deferred. | Controller | Separate provenance/disposition gate only. |
| Release/readiness remains `NOT_READY`. | Controller | Do not make readiness/release/PR claims from this plan. |

## 6. Validation

Required before checkpoint:

```text
git diff --check
git status --short
git status --branch --short
```

## 7. Final Verdict

`VERDICT: ACCEPT_PLAN_READY_FOR_BUILT_IN_HANDLER_NO_LIVE_IMPLEMENTATION_GATE_NOT_READY`

Next recommended gate:

`Built-in Candidate Representation Route Handler No-live Implementation Gate`

Do not proceed directly to full representation export evidence, field correctness validation, production integration, readiness, release or PR.
