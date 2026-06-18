# MVP typed template truth-source replacement plan controller judgment

## Controller self-check

- Role: controller; planning, plan review, plan fix and re-review were delegated to workers.
- Gate: `MVP typed template truth-source replacement gate`.
- Classification: `heavy`.
- Branch: `feat/mvp-llm-incomplete-run-artifacts`.
- Source of truth: `AGENTS.md`, `docs/design.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md`, `docs/fund-analysis-template-draft.md`, accepted typed template Slice 0-8 artifacts and aggregate deepreview checkpoint `d08eab9`.
- Scope boundary: plan-only acceptance for upgrading `docs/fund-analysis-template-draft.md` from prose template truth plus additive typed sidecar into the sole authored template contract truth source for already implemented typed mechanisms.
- Explicit non-goals preserved: no Agent runtime implementation, no multi-year runtime, no provider budget/default/runtime/live probe, no score-loop, no Ch2 public split, no deterministic default `analyze/checklist` behavior change, no quality/golden/readiness promotion, no PR/push/external action.

## Accepted artifacts

- Plan: `docs/reviews/mvp-typed-template-truth-source-replacement-plan-20260603.md`.
- DS plan review: `docs/reviews/mvp-typed-template-truth-source-replacement-plan-review-ds-20260603.md`.
- MiMo plan review: `docs/reviews/mvp-typed-template-truth-source-replacement-plan-review-mimo-20260603.md`.
- Plan fix evidence: `docs/reviews/mvp-typed-template-truth-source-replacement-plan-fix-evidence-20260603.md`.
- DS plan re-review: `docs/reviews/mvp-typed-template-truth-source-replacement-plan-rereview-ds-20260603.md`.
- MiMo plan re-review: `docs/reviews/mvp-typed-template-truth-source-replacement-plan-rereview-mimo-20260603.md`.
- Controller judgment: this file.

## Review disposition

DS initial plan review was `BLOCKED` with three accepted blocking findings:

- B1: missing concrete JSON schema for the canonical template contract block.
- B2: underspecified text/id bridge after removing `_CURRENT_TEXT_MAPPING`.
- B3: missing `EvidenceRequirementId` coupling and validation strategy.

MiMo initial plan review was `PASS-WITH-RISKS` and identified direct high/medium gaps around `chapter_contract_constraints.py` scope, JSON authorability, prose-vs-JSON locality, `source_manifest`, cache/export checks and referenced test paths.

The plan-fix pass is accepted. It adds:

- concrete canonical JSON schema/shape and representative snippet;
- explicit Option A text/id bridge: JSON carries stable `id` plus exact `text`; `contracts.py` projects untyped text and `typed_contracts.py` projects ids/text from the same parsed JSON;
- strict `EvidenceRequirementId` Literal guard with manifest-load and runtime cross-validation;
- `chapter_contract_constraints.py` regression scope;
- explicit `CHAPTER_CONTRACT_REF` locality decision: short non-authoritative refs only, no duplicated structured clauses outside canonical JSON;
- `source_manifest` validation-only compatibility with stale-manifest negative test;
- path-keyed cache and private cache-clear strategy;
- `__init__.py` export check and referenced test-file precheck.

DS re-review result: `PASS-WITH-RISKS`; all original DS blockers fixed.

MiMo re-review result: `PASS-WITH-RISKS`; DS B1/B2/B3 and MiMo F1-F6 fixed.

## Controller decision

The plan is accepted locally.

The accepted implementation direction is:

- `docs/fund-analysis-template-draft.md` will contain the single authored canonical `TEMPLATE_CONTRACT_MANIFEST_JSON` block for currently implemented typed mechanisms.
- `contracts.py` and `typed_contracts.py` will parse, project and validate the template document; they must not keep authored stable id/text mappings, missing behavior, audit focus, Ch2 internal subcontract truth, Ch0/Ch7 dependency metadata or Ch3 evidence predicate as parallel code truth.
- Public chapter ids remain exactly `0-7`; Ch2 `performance / attribution / cost` remain internal subcontracts under public Ch2.
- Deterministic renderer/default `analyze/checklist`, current explicit `--use-llm` typed path semantics and fail-closed behavior must remain unchanged.
- Malformed template edits must fail closed through parser/manifest validation and typed/evidence cross-validation.

## Residuals accepted for implementation

- Slice sequencing risk: if Slice 1 edits the template document before Slice 2 parser exists, implementation evidence must include a temporary manual JSON parse/equality check; the intermediate state must not be accepted by visual inspection alone.
- Markdown tooling risk: large strict JSON inside a Markdown HTML comment can be corrupted by external formatting; this is acceptable only because parser tests and no-provider validation must fail closed.
- Authorability cost: the canonical JSON block is less ergonomic than prose, but it removes code-authored parallel truth. Template editors must use the validation path rather than relying on informal prose duplication.

## Validation

Controller verified plan artifacts with:

```bash
git diff --check -- docs/reviews/mvp-typed-template-truth-source-replacement-plan-20260603.md docs/reviews/mvp-typed-template-truth-source-replacement-plan-fix-evidence-20260603.md docs/reviews/mvp-typed-template-truth-source-replacement-plan-review-ds-20260603.md docs/reviews/mvp-typed-template-truth-source-replacement-plan-review-mimo-20260603.md docs/reviews/mvp-typed-template-truth-source-replacement-plan-rereview-ds-20260603.md docs/reviews/mvp-typed-template-truth-source-replacement-plan-rereview-mimo-20260603.md
```

Result: exited `0`.

No provider/runtime/live probe, implementation test, PR, push or external action was run in this plan gate.

## Next gate

Start implementation under `MVP typed template truth-source replacement gate` Slice 1 only after this accepted plan checkpoint is recorded.

Do not start Agent runtime implementation, phaseflow stabilization, real LLM smoke, provider budget/default/runtime work, multi-year runtime, score-loop, PR/push or external actions from this plan judgment.
