# MVP Template Truth Validation Gate Plan Controller Judgment

## 1. Controller Context

- Phase: `MVP typed-template-to-agent report generation stabilization phase`
- Gate: `Template truth validation gate`
- Gate classification: `heavy`
- Rule truth: `AGENTS.md`
- Design truth: `docs/design.md`
- Control truth: `docs/implementation-control.md`
- Plan artifact: `docs/reviews/mvp-template-truth-validation-gate-plan-20260604.md`
- Plan reviews:
  - `docs/reviews/mvp-template-truth-validation-gate-plan-review-ds-20260604.md`
  - `docs/reviews/mvp-template-truth-validation-gate-plan-review-mimo-20260604.md`

Controller role check: this judgment is controller work. No specialist implementation,
fix, source/test/runtime behavior change, live provider run, golden/readiness action,
push, PR, or release action is authorized by this judgment.

## 2. Judgment

Verdict: **ACCEPT PLAN**

The plan is accepted for the `Template truth validation gate` plan stage. Both
independent reviews returned `PASS` with zero blocking findings. The proposed plan
keeps the gate limited to validating the typed template truth source and its
same-source consumer chain, while preserving the current boundaries recorded in
`docs/design.md` and `docs/implementation-control.md`.

Basis:

- The plan correctly treats `docs/fund-analysis-template-draft.md` canonical
  `TEMPLATE_CONTRACT_MANIFEST_JSON` as the authored Fund template contract truth
  source, matching the accepted current fact in `docs/design.md`.
- The plan verifies both untyped and typed projections from the same JSON via
  `contracts.py` and `typed_contracts.py`, and keeps public chapter ids at `0-7`.
- The plan covers same-source consumers: `EvidenceAvailability`, writer, auditor,
  `ChapterOrchestrator`, and `chapter_contract_constraints.py`.
- The plan explicitly preserves deterministic `analyze/checklist`, quality gate,
  provider defaults, golden/readiness state, Agent runtime state, multi-year runtime
  state, score-loop state, fail-closed semantics, no deterministic fallback, and
  empty stdout for incomplete LLM output.
- The plan requires current direct validation evidence and does not rely on prior
  logs, the previous aggregate review, or indirect conclusions.

Based on the design goal and first principles, accepting this plan is the current
best practice because it validates the contract truth source before any real LLM
re-baseline or Agent migration work, and it avoids using provider runtime symptoms
or future Agent design assumptions as substitutes for direct template contract
evidence.

## 3. Review Finding Disposition

### DS-1: A6 command includes `test_execution_contract.py` without explicit coverage mapping

Disposition: **Accepted as non-blocking residual for validation evidence**

Controller decision: no plan fix required. The validation evidence owner must map
`tests/services/test_execution_contract.py` to the specific A6 evidence it covers:
request/runtime policy consistency, typed template path consistency, and fail-closed
boundary constraints.

Rationale: the matrix already includes the command and the direct evidence class.
The gap is evidence-recording precision, not plan correctness.

### DS-2: A8 forbidden scope recording template can be more explicit

Disposition: **Accepted as non-blocking residual for validation evidence**

Controller decision: no plan fix required. The validation evidence artifact must
include an explicit A8 checklist confirming no live provider, promotion, golden
readiness, snapshot refresh, release readiness, push, PR, or external state action
was run.

Rationale: A8 is a negative proof requirement. The plan already prohibits these
actions; the controller adds a concrete recording requirement for execution.

### MiMo Finding 1: hard stop does not explicitly cover modified tests masking failures

Disposition: **Accepted as non-blocking residual for validation evidence**

Controller decision: no plan fix required. The validation evidence artifact must
record `git status --short` and `git diff --name-only` before acceptance, and must
confirm no source/test/config/runtime behavior files were modified by the validation
step.

Rationale: the plan's Section 7 already requires branch/status and no source/test
modification. The added `git diff --name-only` requirement improves direct evidence
without changing the plan.

### MiMo Finding 2: accepted checkpoint requirements and non-goals have control-doc tension

Disposition: **Accepted as controller-owned process clarification**

Controller decision: no plan fix required. Plan acceptance artifacts can be accepted
without editing source/test/config/runtime behavior. Any control document update is
controller bookkeeping, not specialist implementation, and must remain scoped to the
current gate state, artifact paths, residuals, and next entry point.

Rationale: `phaseflow` requires control-state maintenance. The non-goal is correctly
read as prohibiting specialist/runtime changes and template/design mutation in the
validation plan, not as banning controller bookkeeping when needed.

### MiMo Finding 3: `lru_cache` residual owner should mention Agent engine gate

Disposition: **Accepted as non-blocking future-owner clarification**

Controller decision: no plan fix required. The long-process template cache masking
risk is assigned to future developer tooling/cache invalidation cleanup, with
re-evaluation required if the Agent engine/tool-loop gate introduces long-lived
template contract loading.

Rationale: current validation commands are one-shot processes, so this is not a
current gate blocker.

### MiMo Finding 4: A1 validates structure, not business content quality

Disposition: **Accepted as out-of-scope residual**

Controller decision: no plan fix required. Template business-content quality remains
outside this gate. This gate validates truth-source identity, projection, and
consumer wiring, not whether every template item is optimal.

Rationale: expanding this gate into template business-quality review would mix scope
with later calibration and score-loop work.

### MiMo Finding 5: A8 row should repeat test-file integrity evidence

Disposition: **Accepted as non-blocking residual for validation evidence**

Controller decision: no plan fix required. The validation evidence artifact must
include test/source integrity evidence via `git status --short` and
`git diff --name-only`, and explicitly map that evidence to A8.

Rationale: Section 7 already covers this globally; the controller records the A8
mapping requirement here.

## 4. Accepted Plan Verifier Matrix

The accepted validation-stage verifier is the plan's A1-A8 matrix, with the following
controller additions for the evidence artifact:

| Accepted criterion | Controller evidence requirement |
| --- | --- |
| A6 Service typed path | Explicitly map `tests/services/test_execution_contract.py` to request/runtime policy consistency and typed path mismatch fail-closed behavior |
| A8 Forbidden scope | Include a checklist confirming no live provider, promotion, golden readiness, snapshot refresh, release readiness, push, PR, or external state change |
| Source/test integrity | Record `git status --short` and `git diff --name-only`; confirm no source/test/config/runtime behavior file was modified by validation |
| Residual ownership | Keep cache/literal/naming/multi-year/provider/Agent/score-loop items as future residuals with owners, not current blockers |

## 5. Stop Conditions For Next Step

The next step is validation/evidence execution for the same gate. Stop immediately
if any of the following occur:

- A proposed validation command fails without an external-environment explanation.
- Any validation requires changing source, tests, config, runtime behavior, template
  document, provider defaults, quality gate behavior, golden/readiness state, or
  public chapter ids.
- Any path enters live provider, real LLM smoke, provider runtime/default changes,
  Agent runtime implementation, multi-year runtime, score-loop, golden/readiness,
  PR, push, or release state.
- Any evidence relies on prior aggregate reviews, old logs, or indirect conclusions
  instead of current command output and inspected current files.
- Any incomplete/partial LLM path appears to produce a stdout report or deterministic
  fallback.

## 6. Next Entry Point

After accepted local plan checkpoint, continue within `Template truth validation gate`
to validation/evidence execution. This is still controller-orchestrated work. If
specialist execution is needed, route implementation/evidence collection through
`AgentCodex` or `AgentOpus` and route review/re-review through two of
`AgentDS` / `AgentMiMo` / `AgentGLM`.

Do not enter `Real LLM smoke re-baseline gate` until the validation evidence,
review, controller judgment, control-state update, and accepted local checkpoint
for `Template truth validation gate` are complete.
