# MVP typed template truth-source replacement Slice 1 controller judgment

## Gate context

- Gate: `MVP typed template truth-source replacement gate`
- Classification: `heavy`
- Slice: Slice 1, template-authored canonical JSON block
- Controller decision date: 2026-06-04
- Plan checkpoint: `266e18f gateflow: accept plan for typed template truth source replacement`

## Scope accepted for this slice

Slice 1 is limited to making `docs/fund-analysis-template-draft.md` carry the current accepted typed contract data as the authored template-side truth snapshot:

- Add one canonical `TEMPLATE_CONTRACT_MANIFEST_JSON` HTML comment block.
- Replace the eight per-chapter structured `CHAPTER_CONTRACT` blocks with non-authoritative `CHAPTER_CONTRACT_REF` blocks.
- Preserve public chapter ids `0-7`, chapter titles, `CHAPTER_GOAL`, body scaffolding, `ITEM_RULE`, evidence guidance, and audit appendices.
- Preserve the currently accepted typed contract data: stable ids and exact texts, `preferred_lens`, `audit_focus`, dependencies, Ch2 internal subcontracts, Ch3 evidence predicate, and required-output missing behavior/reasons.

The slice does not change parser authority, source code, tests, README, design/control docs, renderer behavior, deterministic defaults, provider/runtime behavior, Agent runtime, multi-year runtime, score-loop, golden/readiness state, PR state, or release state.

## Implementation evidence reviewed

Reviewed implementation artifact:

- `docs/reviews/mvp-typed-template-truth-source-replacement-slice1-implementation-evidence-20260604.md`

Reviewed changed files:

- `docs/fund-analysis-template-draft.md`
- `docs/reviews/mvp-typed-template-truth-source-replacement-slice1-implementation-evidence-20260604.md`

Controller-side validation also rechecked the template JSON block:

```text
canonical_blocks=1
public_chapter_ids=[0, 1, 2, 3, 4, 5, 6, 7]
chapters=8 ids=[0, 1, 2, 3, 4, 5, 6, 7]
chapter_contract_refs=8 ids=[0, 1, 2, 3, 4, 5, 6, 7]
ch3_clause_04_predicate=ch3.evidence.manager_behavior_style_unreviewed
validation=pass
```

`git diff --check` for the slice files also passed with no output.

## Review results

Independent review artifacts:

- `docs/reviews/mvp-typed-template-truth-source-replacement-slice1-code-review-ds-20260604.md`
- `docs/reviews/mvp-typed-template-truth-source-replacement-slice1-code-review-mimo-20260604.md`

Review verdicts:

- AgentDS: `PASS`, no blocking findings.
- AgentMiMo: `PASS`, no blocking findings, one LOW finding about the evidence artifact omitting the full generation helper body.

Controller disposition:

- The LOW finding is accepted as non-blocking because the implementation evidence and both reviewers independently validated the generated JSON against current untyped and typed loaders, strict JSON parsing, chapter ids, reference blocks, no structured duplication outside canonical JSON, Ch2 internal subcontracts, Ch3 predicate, and required-output missing behavior.
- No Slice 1 fix loop is required.

## Scope check

Accepted staged scope for the Slice 1 checkpoint is limited to:

- `docs/fund-analysis-template-draft.md`
- `docs/reviews/mvp-typed-template-truth-source-replacement-slice1-implementation-evidence-20260604.md`
- `docs/reviews/mvp-typed-template-truth-source-replacement-slice1-code-review-ds-20260604.md`
- `docs/reviews/mvp-typed-template-truth-source-replacement-slice1-code-review-mimo-20260604.md`
- `docs/reviews/mvp-typed-template-truth-source-replacement-slice1-controller-judgment-20260604.md`

Unrelated untracked artifacts in the workspace remain outside this checkpoint and must not be staged by this gate.

## Accepted / deferred distinction

Accepted in Slice 1:

- The template draft now contains the current accepted typed contract data as a canonical JSON block.
- Per-chapter structured contract blocks are removed from the markdown body and replaced by references.
- The Slice 1 evidence and review artifacts are accepted.

Still deferred to later slices in this same gate:

- Production parser reads `TEMPLATE_CONTRACT_MANIFEST_JSON` from `docs/fund-analysis-template-draft.md`.
- Code-authored sidecar/current typed truth is removed or reduced to generated projection.
- Tests prove template consistency, typed contract projection, malformed template fail-closed behavior, audit/evidence compatibility, and no deterministic behavior change.
- `docs/design.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md`, and `fund_agent/fund/README.md` are synchronized after code authority changes.

Explicit non-goals remain deferred:

- Agent runtime or tool-loop implementation.
- Provider/default/runtime budget changes or live probe.
- Multi-year evidence runtime.
- Score-loop.
- Ch2 public split.
- Deterministic default behavior changes.
- Golden/readiness/release/PR external-state changes.

## Controller verdict

**ACCEPT Slice 1.**

The Slice 1 implementation is correct, reviewed, validated, and scope-contained. It may be committed as a local accepted checkpoint for Slice 1 only. This does not accept the full truth-source replacement gate and does not authorize Slice 2, phaseflow, real LLM smoke, provider/runtime work, or Agent runtime implementation.
